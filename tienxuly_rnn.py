import json
import sys
from pathlib import Path


def clean_data(input_file, output_file, error_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    clean_data = {}
    error_data = {}

    for url, info in data.items():
        title = info.get("title", "")
        content = info.get("content", "")

        if (
            not title
            or title.strip() == ""
            or "lỗi" in title.lower()
            or not content
            or content.strip() == ""
            or len(content) < 50
        ):
            error_data[url] = info
        else:
            clean_data[url] = info

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    with open(error_file, "w", encoding="utf-8") as f:
        json.dump(error_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Hợp lệ: {len(clean_data)}")
    print(f"❌ Lỗi: {len(error_data)}")
    print(f"📁 Lưu file sạch: {output_file}")
    print(f"📁 Lưu file lỗi: {error_file}")


def main():
    if len(sys.argv) < 2:
        print("❌ Thiếu tên thư mục")
        print("Ví dụ: python tienxuly_rnn.py thinh")
        return

    folder = Path(sys.argv[1])

    if not folder.exists():
        print(f"❌ Thư mục '{folder}' không tồn tại")
        return

    input_file = folder / "data_rnn.json"
    output_file = folder / "data_rnn_clean.json"
    error_file = folder / "data_rnn_error.json"

    if not input_file.exists():
        print(f"❌ Không tìm thấy {input_file}")
        return

    print(f"📂 Xử lý dữ liệu RNN trong: {folder}")
    clean_data(input_file, output_file, error_file)


if __name__ == "__main__":
    main()