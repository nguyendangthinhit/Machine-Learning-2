# Hướng dẫn sử dụng Script Cào Tiêu Đề

## Mô tả
Script này cào tiêu đề từ các trang báo và lưu kết quả vào file JSON.

## Yêu cầu
- Python 3.6+
- Thư viện: `requests`, `beautifulsoup4`

## Cài đặt

```bash
pip install requests beautifulsoup4
```

## Cách sử dụng

### 1. Tạo file `link.txt`

Tạo file `link.txt` trong cùng thư mục với `cao.py`, mỗi dòng một URL:

```
https://vnexpress.net/
https://dantri.com.vn/
https://thanhnien.vn/
https://example.com/bai-viet-1
https://example.com/bai-viet-2
```

### 2. Chạy script

```bash
python cao.py
```

hoặc

```bash
python3 cao.py
```

### 3. Xem kết quả

Kết quả sẽ được lưu trong file `data.json` với cấu trúc:

```json
{
  "https://vnexpress.net/": "VnExpress - Báo tiếng Việt nhiều người xem nhất",
  "https://dantri.com.vn/": "Dân trí - Báo điện tử Dân trí",
  "https://thanhnien.vn/": "Báo Thanh Niên"
}
```

## Tính năng

✅ Cào tiêu đề từ nhiều nguồn:
- Thẻ `<title>`
- Meta tag `og:title`
- Meta tag `twitter:title`
- Thẻ `<h1>` đầu tiên

✅ Xử lý lỗi tự động

✅ Delay giữa các request để tránh bị chặn

✅ Hiển thị tiến trình real-time

## Tùy chỉnh

Mở file `cao.py` và sửa các thông số trong hàm `main()`:

```python
def main():
    scraper = TitleScraper()
    
    input_file = 'link.txt'      # File chứa links
    output_file = 'data.json'    # File lưu kết quả
    delay = 1.0                  # Delay giữa requests (giây)
    
    scraper.scrape_all(input_file, output_file, delay)
```

## Lưu ý

- Script tự động delay 1 giây giữa các request
- Nếu muốn delay lâu hơn, tăng giá trị `delay` lên (ví dụ: 2.0, 3.0)
- Một số trang web có thể chặn request nếu cào quá nhanh
- Luôn tôn trọng `robots.txt` của website

## Ví dụ Output

Khi chạy, bạn sẽ thấy:

```
Đọc links từ link.txt...
Tìm thấy 5 links
Bắt đầu cào tiêu đề...

[1/5] Đang cào: https://vnexpress.net/
  → Tiêu đề: VnExpress - Báo tiếng Việt nhiều người xem nhất

[2/5] Đang cào: https://dantri.com.vn/
  → Tiêu đề: Dân trí - Báo điện tử Dân trí

...

✓ Đã lưu kết quả vào data.json
✓ Tổng cộng: 5 tiêu đề
```

## Xử lý lỗi

Nếu một URL bị lỗi, script sẽ ghi lại lỗi trong JSON thay vì dừng lại:

```json
{
  "https://invalid-url.com/": "Lỗi: Connection timeout"
}
```
