# rnn_custom.py
# Lightweight helpers extracted from RNN_training — no heavy training deps needed.

import tensorflow as tf
from underthesea import word_tokenize

# ── Stopwords ────────────────────────────────────────────────────────────────
STOPWORDS = {
    "vụ", "bị", "về", "của", "và", "là", "các", "những", "một", "có",
    "đã", "đang", "được", "với", "cho", "ra", "vào", "lộ", "nóng",
    "nhạy_cảm", "sốc", "xôn_xao", "cực_căng", "hot", "đấu_tố",
    "bóc_phốt", "lên_tiếng", "trần_tình", "ồn_ào", "lùm_xùm",
    "nghi_vấn", "tranh_cãi", "bất_ngờ", "mới_nhất", "hiện_nay",
    "hé_lộ", "sự_thật", "theo", "tại", "này", "đó", "khi", "như",
    "thì", "mà", "hay", "hoặc", "nếu", "vì", "do", "qua", "lại"
}


# ── AttentionLayer ────────────────────────────────────────────────────────────
class AttentionLayer(tf.keras.layers.Layer):
    """
    Soft Attention: learns a weight per timestep, returns
    (context_vector, attention_weights).
    """
    supports_masking = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(shape=(input_shape[-1], 1),
                                 initializer='glorot_uniform', name='attn_W')
        self.b = self.add_weight(shape=(1,),
                                 initializer='zeros', name='attn_b')
        super().build(input_shape)

    def call(self, x, mask=None):
        score = tf.nn.tanh(tf.matmul(x, self.W) + self.b)  # (batch, T, 1)
        if mask is not None:
            mask = tf.cast(tf.expand_dims(mask, -1), tf.float32)
            score = score * mask + (1.0 - mask) * (-1e9)
        weights = tf.nn.softmax(score, axis=1)
        context = tf.reduce_sum(x * weights, axis=1)
        return context, weights

    def get_config(self):
        return super().get_config()


# ── Text helpers ──────────────────────────────────────────────────────────────
def _preprocess(text: str) -> str:
    tokens = word_tokenize(text.lower(), format="text").split()
    return " ".join(t for t in tokens if t not in STOPWORDS)


def build_input(title: str, content: str = "") -> str:
    """
    Combine title + content into a single string for inference.
    Mirrors the exact logic used during training.
    """
    title_proc   = _preprocess(title)
    content_proc = _preprocess(content) if content else ""
    if content_proc:
        return f"{title_proc} [SEP] {content_proc}"
    return title_proc