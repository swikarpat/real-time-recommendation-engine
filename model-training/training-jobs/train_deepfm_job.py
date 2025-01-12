import tensorflow as tf
import horovod.tensorflow as hvd
from model_training.core_models.deepfm import DeepFM
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml import Pipeline

# Initialize Horovod
hvd.init()

# Pin GPU to be used to process local rank (one GPU per process)
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
if gpus:
    tf.config.experimental.set_visible_devices(gpus[hvd.local_rank()], 'GPU')

# Assuming you have Spark installed and configured
spark = SparkSession.builder.appName("TrainDeepFM").getOrCreate()

# Load data from S3 (or your data warehouse)
train_data = spark.read.parquet("s3a://your-bucket/data-warehouse/train_data/")
test_data = spark.read.parquet("s3a://your-bucket/data-warehouse/test_data/")

# Define features (assuming you have features prepared in the data warehouse)
categorical_cols = ["user_id", "product_id", "category"]
numerical_cols = ["view_count", "purchase_count", "avg_time_spent_sec", "category_view_count", "category_purchase_count"]

# --- Data Preprocessing with Spark ---

# 1. String Indexing for categorical features
indexers = [StringIndexer(inputCol=col, outputCol=col+"_index", handleInvalid="keep") for col in categorical_cols]

# 2. Vector Assembler for numerical features
assembler = VectorAssembler(inputCols=numerical_cols + [col + "_index" for col in categorical_cols], outputCol="features")

# 3. Create and run the pipeline
pipeline = Pipeline(stages=indexers + [assembler])
train_data = pipeline.fit(train_data).transform(train_data)
test_data = pipeline.fit(test_data).transform(test_data)

# --- Convert Spark DataFrame to TensorFlow Dataset ---

def df_to_dataset(dataframe, shuffle=True, batch_size=32):
    # Convert Spark DataFrame to Pandas
    dataframe = dataframe.toPandas()
    labels = dataframe.pop('label')  # Assuming you have a label column
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(dataframe))
    ds = ds.batch(batch_size)
    ds = ds.prefetch(batch_size)
    return ds

batch_size = 512
train_ds = df_to_dataset(train_data, batch_size=batch_size)
test_ds = df_to_dataset(test_data, shuffle=False, batch_size=batch_size)

# --- TensorFlow Model Training ---

# Define feature columns for DeepFM (using TensorFlow feature columns)
feature_columns = []

# Numerical features
for header in numerical_cols:
    feature_columns.append(tf.feature_column.numeric_column(header))

# Categorical features
for header in categorical_cols:
    categorical_feature = tf.feature_column.categorical_column_with_identity(
        key=header + "_index", num_buckets=10000)  # Adjust num_buckets as needed
    feature_columns.append(tf.feature_column.indicator_column(categorical_feature))

# Create the DeepFM model
model = DeepFM(feature_columns=feature_columns, embedding_size=8, dnn_hidden_units=(128, 128))

# Define optimizer (adjust learning rate based on the number of workers)
learning_rate = 0.001 * hvd.size()
optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

# Wrap the optimizer with Horovod's DistributedOptimizer
optimizer = hvd.DistributedOptimizer(optimizer, backward_passes_per_step=1, average_aggregated_gradients=True)

# Define loss function and metrics
loss_fn = tf.keras.losses.BinaryCrossentropy()
train_accuracy = tf.keras.metrics.BinaryAccuracy()
val_accuracy = tf.keras.metrics.BinaryAccuracy()
train_auc = tf.keras.metrics.AUC()
val_auc = tf.keras.metrics.AUC()

# --- Training and Validation Steps ---

@tf.function
def train_step(features, labels):
    with tf.GradientTape() as tape:
        predictions = model(features)
        loss = loss_fn(labels, predictions)
    # Compute gradients
    gradients = tape.gradient(loss, model.trainable_variables)
    # Apply gradients
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    # Update training metrics
    train_accuracy.update_state(labels, predictions)
    train_auc.update_state(labels, predictions)
    return loss

@tf.function
def val_step(features, labels):
    predictions = model(features)
    v_loss = loss_fn(labels, predictions)
    val_accuracy.update_state(labels, predictions)
    val_auc.update_state(labels, predictions)
    return v_loss

# --- Training Loop ---
num_epochs = 10
for epoch in range(num_epochs):
    # Training
    for step, (features, labels) in enumerate(train_ds):
        loss = train_step(features, labels)
        if step % 100 == 0 and hvd.rank() == 0:
            print(f"Epoch {epoch+1}/{num_epochs}, Step {step}, Loss: {loss.numpy()}, Accuracy: {train_accuracy.result().numpy()}, AUC: {train_auc.result().numpy()}")

    # Broadcast initial variable states from rank 0 to all other processes
    if epoch == 0:
        hvd.broadcast_variables(model.variables, root_rank=0)
        hvd.broadcast_variables(optimizer.variables(), root_rank=0)

    # Validation
    for features, labels in test_ds:
        val_step(features, labels)
    if hvd.rank() == 0:
        print(f"Validation Loss: {loss.numpy()}, Validation Accuracy: {val_accuracy.result().numpy()}, Validation AUC: {val_auc.result().numpy()}")

    # Reset metrics at the end of each epoch
    train_accuracy.reset_states()
    train_auc.reset_states()
    val_accuracy.reset_states()
    val_auc.reset_states()

# Save the model (only on the root worker)
if hvd.rank() == 0:
    model.save("s3a://your-bucket/models/deepfm/")