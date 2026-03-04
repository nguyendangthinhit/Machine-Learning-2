import json
import re

INPUT_FILE  = "data_rnn_new.json"
OUTPUT_FILE = "data_rnn_new.json"

# ── Bảng chuẩn hóa từng nhãn đơn ──────────────────────────────────────────
LABEL_MAP = {
    # Giáo dục
    "giáo dục": "Giáo dục",
    "giao duc": "Giáo dục",

    # Giải trí
    "giải trí": "Giải trí",
    "giai tri": "Giải trí",

    # Công nghệ
    "công nghệ": "Công nghệ",
    "cong nghe": "Công nghệ",

    # Kinh doanh
    "kinh doanh": "Kinh doanh",
    "kinh   doanh": "Kinh doanh",
}

VALID_LABELS = {"Giáo dục", "Giải trí", "Công nghệ", "Kinh doanh"}


def normalize_label(raw: str) -> str:
    """Chuẩn hóa một nhãn đơn: strip, lowercase rồi map về tên chuẩn."""
    key = raw.strip().lower()
    key = re.sub(r"\s+", " ", key)          # chuẩn hóa khoảng trắng thừa
    return LABEL_MAP.get(key, raw.strip())   # nếu không có trong map, giữ nguyên


def split_and_normalize(tag_str: str) -> list[str]:
    """
    Tách chuỗi tag bằng dấu phẩy (hoặc khoảng trắng liên tiếp giữa nhãn),
    chuẩn hóa từng nhãn, loại bỏ trùng lặp, sắp xếp.
    """
    # Một số tag viết liền không có dấu phẩy, VD: "Công nghệ Giáo dục"
    # → thử tách bằng dấu phẩy trước
    parts = [p.strip() for p in tag_str.split(",") if p.strip()]

    # Nếu sau khi tách bằng dấu phẩy vẫn còn phần không khớp nhãn chuẩn
    # → thử tách tiếp bằng khoảng trắng giữa các nhãn đã biết
    final = []
    for part in parts:
        norm = normalize_label(part)
        if norm in VALID_LABELS:
            final.append(norm)
        else:
            # Thử tìm nhãn chuẩn nào khớp trong chuỗi này
            found = []
            for label in VALID_LABELS:
                if label.lower() in part.lower():
                    found.append(label)
            if found:
                final.extend(found)
            else:
                # Giữ nguyên và in cảnh báo để review thủ công
                print(f"  ⚠️  Không nhận dạng được nhãn: '{part}' (từ '{tag_str}')")
                final.append(norm)

    # Loại trùng, sắp xếp để nhất quán
    return sorted(set(final))


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    changed = 0
    for url, info in data.items():
        raw_tag = info.get("tag", "")
        labels  = split_and_normalize(raw_tag)
        new_tag = ", ".join(labels)

        if new_tag != raw_tag:
            print(f"[SỬA] {raw_tag!r:40s} → {new_tag!r}")
            info["tag"] = new_tag
            changed += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Đã chuẩn hóa {changed}/{len(data)} bản ghi → {OUTPUT_FILE}")

    # ── Thống kê nhãn sau khi làm sạch ──────────────────────────────────
    from collections import Counter
    counter: Counter = Counter()
    for info in data.values():
        for lbl in info["tag"].split(", "):
            counter[lbl.strip()] += 1
    print("\n📊 Phân phối nhãn sau khi chuẩn hóa:")
    for lbl, cnt in sorted(counter.items()):
        mark = "✅" if lbl in VALID_LABELS else "❌"
        print(f"  {mark} {lbl:20s}: {cnt}")


if __name__ == "__main__":
    main()