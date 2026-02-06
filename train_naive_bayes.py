# Nhớ cài thư viện rồi mới chạy nghe   pip install underthesea scikit-learn joblib
import json

file_path = 'data.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

train_data = [(item['title'], item['tag']) for item in data.values()]

print(f"Đã nạp {len(train_data)} link thành công.")
# print(train_data[0])

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
        "nghệ sĩ", "ca sĩ", "hoa hậu", "showbiz", "livestream", "drama", 
        "tình ái", "ngoại tình", "đấu tố", "sao kê", "từ thiện", "fan", "anti-fan", 
        "hợp đồng âm nhạc", "showbiz", "hậu trường", "lên giường", "chia tay", "tiktok"
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
train_data = train_data + extra_samples
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
    ("Vấn đề nhạy cảm liên quan đến học đường", "giáo dục")
]

train_data = train_data + extended_keywords

import json
import joblib
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier

# 1. Nạp dữ liệu
file_path = 'data.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

X_train_raw = []
y_train_raw = []

for item in data.values():
    X_train_raw.append(item['title'])
    tags = [t.strip().lower() for t in item['tag'].split(',')]
    y_train_raw.append(tags)


mlb = MultiLabelBinarizer()
y_train = mlb.fit_transform(y_train_raw)
categories = mlb.classes_

def preprocess_drama(text):
    tokens = word_tokenize(text.lower(), format="text")
    return tokens

X_train_preprocessed = [preprocess_drama(t) for t in X_train_raw]


# OneVsRestClassifier cho phép mỗi nhãn được học một bộ phân loại Naive Bayes riêng
model = make_pipeline(
    TfidfVectorizer(
        ngram_range=(1, 2), 
        sublinear_tf=True,
        min_df=1,
        max_df=0.8
    ),
    OneVsRestClassifier(MultinomialNB(alpha=0.1)) 
)

model.fit(X_train_preprocessed, y_train)
print(f"HL thành công với {len(categories)} danh mục: {categories}")

# Lưu lại
joblib.dump((model, mlb), 'model_phanloai_drama_nb.pkl')