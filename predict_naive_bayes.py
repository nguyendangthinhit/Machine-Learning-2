import joblib
import json
from underthesea import word_tokenize

try:
    model, mlb = joblib.load('model_phanloai_drama_nb.pkl') 
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file 'model_phanloai_drama_nb.pkl'.")
    exit()

def predict_drama(title):
    clean_title = word_tokenize(title.lower(), format="text")

    probabilities = model.predict_proba([clean_title])[0]
    threshold = 0.3
    labels_with_scores = [
        (mlb.classes_[i], prob * 100) 
        for i, prob in enumerate(probabilities) if prob >= threshold
    ]
    if not labels_with_scores:
        max_idx = probabilities.argmax()
        labels_with_scores = [(mlb.classes_[max_idx], probabilities[max_idx] * 100)]
    
    labels_with_scores.sort(key=lambda x: x[1], reverse=True)
    return labels_with_scores

new_data = [
    "Ca sĩ Pháo và ViruSs livestream đấu tố nhau về hợp đồng âm nhạc",
    "Shark Bình lên tiếng về việc sử dụng AI trong hệ sinh thái công nghệ",
    "Bắt tạm giam nhóm đối tượng lừa đảo chiếm đoạt tài sản qua mạng",
    "Tranh cãi giáo viên trung tâm Apax bị phụ huynh quây kín đòi tiền",
    "Ca sĩ lộ clip với học sinh",
]

print(f"\n{'Tiêu đề Drama':<60} | {'Chủ đề dự đoán (Độ tin cậy)'}")
print("-" * 100)

for title in new_data:
    results = predict_drama(title)
    label_str = ", ".join([f"{name} ({score:.1f}%)" for name, score in results])
    print(f"{title[:58]:<60} | {label_str}")

#NHẬP TỪ BÀN PHÍM
# print("\n" + "="*30)
# while True:
#     user_input = input("Nhập tiêu đề drama mới (hoặc 'exit'): ")
#     if user_input.lower() == 'exit': break
    
#     res = predict_drama(user_input)
#     output = ", ".join([f"{name} ({score:.1f}%)" for name, score in res])
#     print(f" => Dự đoán: {output}")


# #DỰ ĐOÁN TỪ FILE JSON có tiêu đề
# input_file = '' # file data test

# try:
#     with open(input_file, 'r', encoding='utf-8') as f:
#         data_to_predict = json.load(f)
# except FileNotFoundError:
#     print(f"Lỗi: Không tìm thấy file {input_file}")
#     exit()

# print(f"\n{'Tiêu đề':<70} | {'Dự đoán (Độ tin cậy)'}")
# print("-" * 110)
# results_summary = {}

# for url, content in data_to_predict.items():
#     title = content.get('title', '')
#     predictions = predict_drama(title)
#     label_str = ", ".join([f"{name} ({score:.1f}%)" for name, score in predictions])
#     print(f"{title[:68]:<70} | {label_str}")
#     results_summary[url] = {
#         "title": title,
#         "predicted_tags": [name for name, score in predictions]
#     }

# with open('results_predicted.json', 'w', encoding='utf-8') as f:
#     json.dump(results_summary, f, ensure_ascii=False, indent=4)
#     print("\n--- Đã lưu kết quả dự đoán vào file 'results_predicted.json' ---")