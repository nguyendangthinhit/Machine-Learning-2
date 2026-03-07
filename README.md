# 📚 Hướng dẫn sử dụng hệ thống thu thập và huấn luyện dữ liệu

Dự án này dùng để:

-   Thu thập dữ liệu bài báo
-   Cào tiêu đề và nội dung
-   Chuẩn hóa dữ liệu
-   Train mô hình **Naive Bayes** và **RNN (BiLSTM + Attention)**
-   Chạy **app demo phân loại tin tức**

------------------------------------------------------------------------

# 📁 Cấu trúc dự án

ml2
├── app.py
├── laydulieu.py
├── cao.py
├── caornn.py
├── gop.py
├── chuanhoatag.py
│
├── preprocessing
│   ├── tienxuly.py
│   └── tienxuly_rnn.py
│
├── training
│   ├── nb_trainining.py
│   ├── rnn_trainining.py
│   └── RNN_trainining.ipynb
│
├── models
│   ├── model_phanloai_drama_nb.pkl
│   ├── model_rnn.keras
│   ├── best_model.keras
│   └── artifacts_rnn.pkl
│
├── data
│   ├── data.json
│   └── data_rnn.json
│
├── members_data
│   ├── LNH
│   ├── NĐT
│   ├── P.Huy
│   ├── Q.Huy
│   ├── Quang
│   ├── Thiện
│   └── Trung
│
├── requirements.txt
├── README.md
└── .gitignore

------------------------------------------------------------------------

# 🚀 Quy trình thực hiện dự án

Pipeline gồm 5 bước chính.

------------------------------------------------------------------------

# Bước 1: Lấy dữ liệu từ Google Drive 

Sử dụng:

    laydulieu.py 

Script sẽ tải danh sách **links bài báo từ Google Drive**.
Link: https://docs.google.com/spreadsheets/d/17rRLrSseMHHAZTTEQFezK3nXd0WOWF5Gi4I78gh-viE/edit?usp=drive_link
⚠️ Lưu ý:

-   Cần **credentials Google Drive**
-   Chỉ **chủ Drive** mới có thể chạy bước này ( Hiện thầy không run được file này ạ )

Sau khi chạy script, hệ thống sẽ tự động tạo thư mục cho từng
thành viên trong nhóm và sinh file `link.txt` bên trong mỗi thư mục.

Ví dụ:

    <member_name>/link.txt

------------------------------------------------------------------------

# Bước 2: Cào dữ liệu

Sau khi có `link.txt`, tiến hành crawl.

## Cào tiêu đề (Naive Bayes)

    python cao.py NĐT
    python cao.py Thiện
    python cao.py Q.Huy

Kết quả:

    data.json

------------------------------------------------------------------------

## Cào tiêu đề + 100 từ đầu (RNN)

    python cao_rnn.py NĐT
    python cao_rnn.py Thiện
    python cao_rnn.py Q.Huy

Kết quả:

    data_rnn.json

------------------------------------------------------------------------

# 🎯 Mục đích chia thư mục

Mỗi thành viên có dataset riêng để:

-   Biết dữ liệu do **ai crawl**
-   Dễ **debug lỗi**
-   Dễ **quản lý task**

Ví dụ:

    NĐT/data.json lỗi → Thịnh sửa

------------------------------------------------------------------------

# Bước 3: Gộp dữ liệu

Chạy:

    python gop.py

Kết quả:

    data.json
    data_rnn.json

------------------------------------------------------------------------

# Bước 4: Chuẩn hóa tag

Chạy:

    python chuanhoatag.py

Script sẽ chuẩn hóa các tag khác nhau như:

    Công nghệ
    Công Nghệ
    Cong nghe
    Tech

------------------------------------------------------------------------

# Bước 5: Train model

Train trên **Google Colab**.

## Naive Bayes

    train_nb.ipynb

Pipeline:

    TF-IDF → MultinomialNB → OneVsRestClassifier

------------------------------------------------------------------------

## RNN

    train_rnn.ipynb

Kiến trúc:

    Embedding → BiLSTM → Attention → Dense

Sau khi train sẽ xuất:

    model_nb.pkl
    model_rnn.h5

------------------------------------------------------------------------

# Bước 6: Chạy app demo

    python app.py

App sẽ:

-   Load model NB
-   Load model RNN
-   Nhập văn bản
-   So sánh kết quả

------------------------------------------------------------------------

# 📦 Cài thư viện

    pip install -r requirements.txt

------------------------------------------------------------------------

# ⚠️ Lưu ý

-   Không push **credentials** lên Git
-   Không crawl quá nhanh
-   Kiểm tra dữ liệu lỗi trước khi train

------------------------------------------------------------------------

# Pipeline tổng thể

    Google Drive
         ↓
    laydulieu.py
         ↓
    link.txt
         ↓
    cao.py / cao_rnn.py
         ↓
    data.json / data_rnn.json
         ↓
    gop.py
         ↓
    dataset chung
         ↓
    chuanhoatag.py
         ↓
    dataset chuẩn
         ↓
    train_nb / train_rnn
         ↓
    model
         ↓
    app.py
