import tensorflow as tf
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
import numpy as np

def evaluate_model(model_path, test_data):
    """
    Evaluates a trained TensorFlow model on a test dataset.

    Args:
        model_path: Path to the saved TensorFlow model.
        test_data: Test dataset (e.g., a tf.data.Dataset).
    """

    # Load the trained model
    model = tf.keras.models.load_model(model_path)

    # Get predictions on the test set
    y_true = []
    y_scores = []
    for features, labels in test_data:
        predictions = model(features, training=False)  # Ensure training=False for inference
        y_true.extend(labels.numpy())
        y_scores.extend(predictions.numpy().flatten())  # Assuming model outputs probabilities

    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    # Calculate metrics
    roc_auc = roc_auc_score(y_true, y_scores)
    print(f"ROC AUC: {roc_auc}")

    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)
    pr_auc = auc(recall, precision)
    print(f"PR AUC: {pr_auc}")

    # You can add more metrics like F1-score, accuracy, etc. as needed.

# Example usage (assuming you have a test_ds tf.data.Dataset):
# evaluate_model("s3a://your-bucket/models/deepfm/", test_ds)