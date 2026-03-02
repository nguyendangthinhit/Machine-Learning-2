

import json

input_file = "databosung_giaoduc_QuocHuy.json"
output_file = "links.txt"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(output_file, "w", encoding="utf-8") as f:
    for url, info in data.items():
        tag = info.get("tag", "")
        f.write(f"{url}: {tag}\n")

print(f"Đã xuất {len(data)} dòng ra {output_file}")