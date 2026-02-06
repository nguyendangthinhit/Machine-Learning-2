# Nhớ cài thư viện rồi mới chạy nghe   pip install underthesea scikit-learn joblib
import json

file_path = 'data.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

train_data = [(item['title'], item['tag']) for item in data.values()]

print(f"Đã nạp {len(train_data)} link thành công.")
print("Ví dụ mẫu đầu tiên:", train_data[0])

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
    # Chuyển "Công nghệ, Kinh doanh" thành list ['công nghệ', 'kinh doanh']
    # Đồng thời viết thường để đồng nhất nhãn
    tags = [t.strip().lower() for t in item['tag'].split(',')]
    y_train_raw.append(tags)

# 2. Xử lý đa nhãn (Multi-label)
mlb = MultiLabelBinarizer()
y_train = mlb.fit_transform(y_train_raw)
# Lưu danh sách các nhãn để dùng khi dự đoán
categories = mlb.classes_

# 3. Tiền xử lý văn bản chuyên biệt cho Drama
def preprocess_drama(text):
    # Tách từ
    tokens = word_tokenize(text.lower(), format="text")
    # Bạn có thể thêm bước loại bỏ các từ vô nghĩa tại đây nếu cần
    return tokens

X_train_preprocessed = [preprocess_drama(t) for t in X_train_raw]

# 4. Huấn luyện mô hình Naive Bayes đa nhãn
# OneVsRestClassifier cho phép mỗi nhãn được học một bộ phân loại Naive Bayes riêng
model = make_pipeline(
    TfidfVectorizer(
        ngram_range=(1, 3), # Học cụm 1-2-3 từ để bắt được các cụm như "chiếm_đoạt_tài_sản"
        min_df=1,
        max_df=0.9
    ),
    OneVsRestClassifier(MultinomialNB(alpha=0.01)) # alpha thấp để cực kỳ nhạy với từ khóa drama
)

model.fit(X_train_preprocessed, y_train)
print(f"HL thành công với {len(categories)} danh mục: {categories}")

# 5. Hàm dự đoán Drama
def predict_drama(title):
    processed = preprocess_drama(title)
    # Lấy xác suất dự đoán thay vì chỉ lấy nhãn (để bắt được nhiều nhãn hơn)
    proba = model.predict_proba([processed])[0]
    
    # Chỉ lấy những nhãn có xác suất > 20% (ngưỡng này giúp lấy được đa nhãn)
    results = [categories[i] for i, p in enumerate(proba) if p > 0.2]
    
    # Nếu không có nhãn nào đủ mạnh, lấy nhãn cao nhất
    if not results:
        results = [categories[proba.argmax()]]
        
    return results, proba

# 6. Test với 1 Drama mới
test_drama = "Hằng Du Mục và Quang Linh Vlogs bị kiện vì livestream bán hàng giả"
labels, scores = predict_drama(test_drama)

print(f"\nDrama test: {test_drama}")
print(f"Chủ đề dự đoán: {', '.join(labels)}")

# 7. Lưu lại
joblib.dump((model, mlb), 'model_phanloai_drama.pkl')