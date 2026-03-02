import gspread
import pandas as pd
import os
from oauth2client.service_account import ServiceAccountCredentials

# 1. Kết nối và lấy dữ liệu
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Mở tệp và lấy dữ liệu
sheet = client.open("Link Data").sheet1
raw_data = sheet.get_all_values()
# Hàng 1 là tiêu đề
df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

# 2. Làm sạch dữ liệu
df['Người làm'] = df['Người làm'].astype(str).str.strip()
df['Link'] = df['Link'].astype(str).str.strip()
df['Tags'] = df['Tags'].astype(str).str.strip()

# --- CHỈ LẤY TỪ DÒNG 238 TRỞ ĐI (index 237 trong sheet, tương đương index 236 trong df vì bỏ header) ---
# Dòng 238 trong sheet = index 237 (1-based) => trong df (đã bỏ header) = index 236
df = df.iloc[236:]  # Lấy từ dòng 238 của sheet đến hết

# --- KHÔNG CÒN QUY ĐỔI TÊN: mỗi người làm sẽ có thư mục riêng ---
# Gom nhóm theo tên người làm gốc
grouped = df.groupby('Người làm')

print("--- Bắt đầu xuất file với định dạng <link>: <tag> ---")

for name, group in grouped:
    # Bỏ qua các dòng có tên trống
    if not name or name == 'nan':
        continue

    # Lấy các dòng có Link
    data_list = group.loc[group['Link'] != '', ['Link', 'Tags']].values.tolist()

    if data_list:
        # Tạo thư mục theo tên người làm (nếu chưa có thì tự tạo)
        os.makedirs(name, exist_ok=True)
        file_path = os.path.join(name, 'links.txt')

        # Ghi dữ liệu vào file (append để không ghi đè nếu chạy nhiều lần)
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data_list:
                link = item[0]
                tag = item[1]
                f.write(f"{link}: {tag}\n")

        print(f"[OK] Đã gom {len(data_list)} dòng vào thư mục: {name}/links.txt")

print("--- Hoàn thành ---")