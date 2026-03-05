import tensorflow as tf
from keras.saving import register_keras_serializable
from underthesea import word_tokenize

# Danh sách stopwords dùng khi train RNN
STOPWORDS = {
    "là", "và", "của", "cho", "trên", "với", "một", "những", "các",
    "được", "bị", "tại", "theo", "đã", "đang", "sẽ", "rằng", "này",
    "kia", "đó", "khi", "nơi", "nào", "ai", "gì", "nhiều", "ít",
    "rất", "hơn", "như", "thì", "mà", "hay", "hoặc", "nếu", "vì",
    "do", "qua", "lại"
}


def preprocess(text: str) -> str:
    """
    Tiền xử lý: lower → word_tokenize → bỏ stopwords.
    Logic này được dùng khi train trong rnn_trainining.py.
    """
    tokens = word_tokenize(text.lower(), format="text").split()
    return " ".join(t for t in tokens if t not in STOPWORDS)


def build_input(title: str, content: str) -> str:
    """
    Ghép tiêu đề + nội dung thành 1 chuỗi để train/predict.
    [SEP] là token phân cách để model biết ranh giới.
    Khi predict chỉ dùng tiêu đề, content có thể để rỗng.
    """
    title_proc = preprocess(title)
    content_proc = preprocess(content) if content else ""
    if content_proc:
        return f"{title_proc} [SEP] {content_proc}"
    return title_proc


@register_keras_serializable(package="custom")
class AttentionLayer(tf.keras.layers.Layer):
    """
    Soft Attention giống như trong rnn_trainining.py:
    - Học trọng số cho từng timestep
    - Tóm tắt chuỗi thành một context vector
    - Trả về (context_vector, attention_weights)
    """

    supports_masking = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(
            shape=(input_shape[-1], 1),
            initializer="glorot_uniform",
            name="attn_W",
        )
        self.b = self.add_weight(
            shape=(1,),
            initializer="zeros",
            name="attn_b",
        )
        super().build(input_shape)

    def call(self, x, mask=None):
        # x: (batch, MAX_LEN, hidden_dim)
        score = tf.nn.tanh(tf.matmul(x, self.W) + self.b)  # (batch, MAX_LEN, 1)

        if mask is not None:
            # mask: (batch, MAX_LEN) -> (batch, MAX_LEN, 1)
            mask = tf.cast(mask, tf.float32)
            mask = tf.expand_dims(mask, -1)
            score = score * mask + (1.0 - mask) * (-1e9)

        # Attention weights
        weights = tf.nn.softmax(score, axis=1)  # (batch, MAX_LEN, 1)

        # Context vector = sum(weights * x)
        context = tf.reduce_sum(weights * x, axis=1)  # (batch, hidden_dim)

        return context, tf.squeeze(weights, axis=-1)

