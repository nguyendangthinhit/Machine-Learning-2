import json
from collections import defaultdict

# 4 tag chuẩn
VALID_TAGS = {
    "giải trí": "Giải trí",
    "kinh doanh": "Kinh doanh",
    "công nghệ": "Công nghệ",
    "giáo dục": "Giáo dục"
}

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

tag_count = defaultdict(int)

for url, info in data.items():
    raw_tag = info.get("tag", "")
    
    # tách multi-tag
    tags = raw_tag.split(",")
    
    for tag in tags:
        tag = tag.strip().lower()   # chuẩn hóa
        
        if tag in VALID_TAGS:
            standard_tag = VALID_TAGS[tag]
            tag_count[standard_tag] += 1

# in kết quả
for tag, count in tag_count.items():
    print(f"{tag}: {count}")