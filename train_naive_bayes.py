# Nhớ cài thư viện rồi mới chạy nghe   pip install underthesea scikit-learn joblib
keywords= {
    "giáo dục": [
        "nữ sinh", "nam sinh", "thầy giáo", "cô giáo", "giảng viên", "học đường", "học sinh", 
        "điểm thi", "gian lận", "trường học", "phụ huynh", "kỷ luật", "đình chỉ", "bằng cấp", "học phí", "đề thi", "nhà trường"
    ],
    "công nghệ": [
        "AI", "trí tuệ nhân tạo", "chatgpt", "phần mềm", "tiền số", "crypto", 
        "hacker", "dữ liệu", "tấn công mạng", "deepfake", "thuật toán",
        "nền tảng", "robot", "thiết bị"
    ],
    "giải trí": [
        "nghệ sĩ", "ca sĩ", "hoa hậu", "showbiz", "livestream", "drama", "Scandal", "clip nóng",
        "tình ái", "ngoại tình", "đấu tố", "sao kê", "từ thiện", "fan", "anti-fan", 
        "hợp đồng âm nhạc", "showbiz", "hậu trường", "chia tay", "tiktok"
    ],
    "kinh doanh": [
        "trái phiếu", "cổ phiếu", "lừa đảo", "tài sản", "giám đốc", "hợp đồng", "bất động sản", "chiếm đoạt", 
        "phá sản", "nợ nần", "đa cấp", "đầu tư", "lợi nhuận", "vỡ nợ", "tài chính"
    ]
}
extra_samples = []
for tag, words in keywords.items():
    for word in words:
        extra_samples.append((f"Vấn đề về {word}", tag))

extended_keywords = [
    ("Bị tạm giữ hình sự vì hành vi lừa đảo", "kinh doanh"),
    ("Nghệ sĩ bị tạm giữ hình sự vì dùng chất cấm", "giải trí"),
    ("Giáo viên bị tạm giữ hình sự vì xúc phạm học sinh", "giáo dục"),
    ("Học sinh, sinh viên, giáo viên, trường học, nữ sinh", "giáo dục"),
    ("Nữ sinh lộ clip với thầy giáo trong ký túc xá", "giáo dục, giải trí"),
    ("Ca sĩ lộ clip với học sinh tại nhà riêng", "giải trí, giáo dục"),
    ("Danh sách ca sĩ, diễn viên, nghệ sĩ nổi tiếng", "giải trí"),
    ("Thông tin về học sinh, sinh viên, giáo viên", "giáo dục"),
    ("Nghệ sĩ làm từ thiện tại trường học cho học sinh", "giải trí, giáo dục"),
    ("Ca sĩ hát giao lưu cùng học sinh sinh viên", "giải trí, giáo dục"),
    ("Drama lộ clip nhạy cảm của người nổi tiếng", "giải trí"),
    ("Vấn đề nhạy cảm liên quan đến học đường", "giáo dục"),
    ("Ca sĩ nổi tiếng lộ clip nhạy cảm gây sốc", "giải trí"),
    ("Clip nóng của ca sĩ diễn viên bị rò rỉ trên mạng", "giải trí"),
    ("Ca sĩ và học sinh lộ clip trong trường học", "giải trí, giáo dục"),
    ("Nghi vấn ca sĩ có quan hệ bất chính với học sinh", "giải trí, giáo dục"),
    ("Scandal ca sĩ lộ clip cùng nữ sinh", "giải trí, giáo dục")
]

import json
import joblib
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier

# Nạp dữ liệu
file_path = 'data.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

X_train = []
y_train = []


for item in data.values():
    X_train.append(item['title'])
    tags = [t.strip().lower() for t in item['tag'].split(',')]
    y_train.append(tags)

for tag, words in keywords.items():
    for word in words:
        X_train.append(f"Vấn đề về {word}")
        y_train.append([tag])

for title, tag_str in extended_keywords:
    X_train.append(title)
    tags = [t.strip().lower() for t in tag_str.split(',')]
    y_train.append(tags)

# TIẾN HÀNH MLB VÀ PREPROCESS TRÊN DỮ LIỆU TỔNG
mlb = MultiLabelBinarizer()
y_train = mlb.fit_transform(y_train)
categories = mlb.classes_

STOPWORDS = ["vụ", "bị", "về", "của", "và", "là", "các", "những", "một", "có", "đã", "đang", "được", "với", "cho"]
def preprocess_drama(text):
    tokens_raw = word_tokenize(text.lower(), format="text")
    tokens = tokens_raw.split()
    cleaned_text = " ".join([t for t in tokens if t not in STOPWORDS])
    return cleaned_text
# Sử dụng hàm preprocess của bạn trên X_train_final
X_train_preprocessed = [preprocess_drama(t) for t in X_train]

# HUẤN LUYỆN
model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
    OneVsRestClassifier(MultinomialNB(alpha=0.1)) 
)
model.fit(X_train_preprocessed, y_train)

# Lưu mô hình
joblib.dump((model, mlb), 'model_phanloai_drama_nb.pkl')
print(f"HL thành công với {len(X_train)} mẫu dữ liệu!")