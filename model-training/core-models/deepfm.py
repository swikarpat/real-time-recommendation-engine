import tensorflow as tf

class DeepFM(tf.keras.Model):
    def __init__(self, feature_columns, embedding_size=8, dnn_hidden_units=(128, 128)):
        super(DeepFM, self).__init__()

        self.feature_columns = feature_columns
        self.embedding_size = embedding_size
        self.dnn_hidden_units = dnn_hidden_units

        # FM part
        self.fm_linear = tf.keras.layers.Dense(1, use_bias=True)  # Linear terms
        self.fm_cross = {}
        for col in self.feature_columns:
            self.fm_cross[col.name] = tf.keras.layers.Embedding(
                input_dim=col.vocabulary_size if hasattr(col, 'vocabulary_size') else col.num_buckets,
                output_dim=embedding_size,
                embeddings_initializer='random_normal',
                embeddings_regularizer=tf.keras.regularizers.l2(1e-5)
            )


        # Deep part
        self.dnn_layers = []
        for units in dnn_hidden_units:
            self.dnn_layers.append(tf.keras.layers.Dense(units, activation='relu'))
        self.dnn_layers.append(tf.keras.layers.Dense(1, activation=None))  # Output layer

    def call(self, inputs):
        # FM part: linear terms
        linear_terms = self.fm_linear(inputs)

        # FM part: interaction terms
        embeddings = [self.fm_cross[col.name](inputs[..., i]) for i, col in enumerate(self.feature_columns)]

        sum_of_squares = tf.square(tf.add_n(embeddings))
        squares_of_sum = tf.add_n([tf.square(emb) for emb in embeddings])
        interaction_terms = 0.5 * tf.reduce_sum(sum_of_squares - squares_of_sum, axis=1, keepdims=True)


        # Deep part
        deep_input = tf.concat(embeddings, axis=1)
        dnn_output = deep_input
        for layer in self.dnn_layers:
            dnn_output = layer(dnn_output)

        # Combine FM and Deep parts
        concat_output = tf.concat([linear_terms, interaction_terms, dnn_output], axis=1)
        output = tf.reduce_sum(concat_output, axis=1, keepdims=True)
        output = tf.sigmoid(output)

        return output