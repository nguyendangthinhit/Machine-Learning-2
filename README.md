# Hướng dẫn sử dụng Script Cào Tiêu Đề (Version 2.0)

## 📁 Cấu trúc thư mục

```
ml2/
├── cao.py           # Script chính (đặt ở thư mục gốc)
├── thinh/
│   ├── link.txt     # Danh sách URLs của Thịnh
│   └── data.json    # Kết quả cào của Thịnh
├── thien/
│   ├── link.txt     # Danh sách URLs của Thiên
│   └── data.json    # Kết quả cào của Thiên
└── huy/
    ├── link.txt     # Danh sách URLs của Huy
    └── data.json    # Kết quả cào của Huy
```

## 📦 Cài đặt
Các thư viện cần thiết đã được note lại trong file requirements.txt, sử dụng câu lệnh sau để cài đặt
```bash
pip install -r requirements.txt
```

## 🚀 Cách sử dụng

### 1. Chuẩn bị thư mục

Tạo thư mục cho từng người và file `link.txt` bên trong:

```bash
# Ví dụ cho thư mục "thinh"
mkdir thinh
cd thinh
# Tạo file link.txt và thêm URLs vào
```

### 2. Tạo file link.txt

Trong mỗi thư mục (NĐT, Q.Huy, Thiện,....), tạo file `link.txt` với các URLs:

```
https://vnexpress.net/
https://dantri.com.vn/
https://thanhnien.vn/
```

### 3. Chạy script

**Cú pháp:**
```bash
python cao.py <tên_thư_mục>
```

**Ví dụ:**

```bash
# Cào dữ liệu cho thư mục "thinh"
python cao.py thinh

# Cào dữ liệu cho thư mục "thien"
python cao.py thien

# Cào dữ liệu cho thư mục "huy"
python cao.py huy
```

### 4. Xem kết quả

Kết quả sẽ được lưu trong file `data.json` bên trong thư mục tương ứng.

Ví dụ sau khi chạy `python cao.py thinh`, file `thinh/data.json` sẽ có nội dung:

```json
{
  "https://vnexpress.net/": "VnExpress - Báo tiếng Việt nhiều người xem nhất",
  "https://dantri.com.vn/": "Dân trí - Báo điện tử Dân trí",
  "https://thanhnien.vn/": "Báo Thanh Niên"
}
```

## 🎯 Ví dụ đầy đủ

```powershell
PS D:\py\git\ml2> python cao.py thinh

============================================================
🎯 CÀO TIÊU ĐỀ - THƯ MỤC: THINH
============================================================
📂 Đọc links từ: thinh/link.txt
📝 Tìm thấy 3 links
🚀 Bắt đầu cào tiêu đề...

[1/3] Đang cào: https://vnexpress.net/
  ✓ Tiêu đề: VnExpress - Báo tiếng Việt nhiều người xem nhất

[2/3] Đang cào: https://dantri.com.vn/
  ✓ Tiêu đề: Dân trí - Báo điện tử Dân trí

[3/3] Đang cào: https://thanhnien.vn/
  ✓ Tiêu đề: Báo Thanh Niên

✅ Đã lưu kết quả vào: thinh/data.json
✅ Tổng cộng: 3 tiêu đề
============================================================
✨ HOÀN THÀNH!
============================================================

PS D:\py\git\ml2> ls thinh

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         31-1-2026  12:09 PM            380 data.json
-a----         31-1-2026  12:09 PM            155 link.txt
```

## ❌ Xử lý lỗi

### Lỗi: Thiếu tên thư mục
```bash
PS D:\py\git\ml2> python cao.py

❌ Lỗi: Thiếu tên thư mục!

📖 Cách sử dụng:
   python cao.py <tên_thư_mục>

💡 Ví dụ:
   python cao.py thinh
   python cao.py thien
   python cao.py huy
```

### Lỗi: Thư mục không tồn tại
```bash
PS D:\py\git\ml2> python cao.py abc

❌ Lỗi: Thư mục 'abc' không tồn tại!

💡 Các thư mục hiện có:
   - huy
   - thien
   - thinh
```

### Lỗi: Không tìm thấy link.txt
```bash
PS D:\py\git\ml2> python cao.py thinh

❌ Lỗi: Không tìm thấy file 'thinh/link.txt'
💡 Hãy tạo file 'link.txt' trong thư mục 'thinh'
```

## 🔧 Tùy chỉnh

Nếu bạn muốn thay đổi delay giữa các request, sửa trong file `cao.py`:

```python
def main():
    # ...
    delay = 1.0  # Thay đổi giá trị này (đơn vị: giây)
    scraper.scrape_all(input_file, output_file, delay)
```

Ví dụ:
- `delay = 0.5` → Delay 0.5 giây (nhanh hơn)
- `delay = 2.0` → Delay 2 giây (an toàn hơn)
- `delay = 3.0` → Delay 3 giây (rất an toàn)

## 💡 Mẹo sử dụng

1. **Chạy cho nhiều thư mục:**
   ```bash
   python cao.py thinh
   python cao.py thien
   python cao.py huy
   ```

2. **Kiểm tra kết quả nhanh:**
   ```bash
   # Windows PowerShell
   cat thinh/data.json
   
   # Linux/Mac
   cat thinh/data.json
   ```

3. **Backup dữ liệu cũ trước khi chạy lại:**
   File `data.json` sẽ bị ghi đè mỗi lần chạy script

## ⚠️ Lưu ý quan trọng

- Script tự động delay 1 giây giữa các request để tránh bị chặn
- Tôn trọng `robots.txt` của các website
- Không cào quá nhiều trang cùng lúc
- Một số trang có thể chặn request nếu cào quá nhanh

## 🎨 Tính năng

✅ Tự động phát hiện tiêu đề từ nhiều nguồn:
- Thẻ `<title>`
- Meta tag `og:title`
- Meta tag `twitter:title`
- Thẻ `<h1>` đầu tiên

✅ Xử lý lỗi tự động và thông báo rõ ràng

✅ Hiển thị tiến trình real-time với emoji

✅ Lưu kết quả vào đúng thư mục được chỉ định

✅ Kiểm tra thư mục và file tự động

