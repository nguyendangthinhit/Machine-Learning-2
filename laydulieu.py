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
df['Tags'] = df['Tags'].astype(str).str.strip() # Làm sạch cột Tags

# --- LOGIC ĐIỀU HƯỚNG: CHUYỂN ĐỔI TÊN NGƯỜI LÀM ---
# Nếu tên KHÔNG thuộc ['Thiện', 'Q.Huy'] thì đổi thành 'NĐT'
df['Người làm_Final'] = df['Người làm'].apply(lambda x: x if x in ['Thiện', 'Q.Huy'] else 'NĐT')

# Gom nhóm theo người làm đã quy đổi
grouped = df.groupby('Người làm_Final')

print("--- Bắt đầu xuất file với định dạng <link>: <tag> ---")

for name, group in grouped:
    # Lấy cả Link và Tags, bỏ qua các dòng có Link trống
    # Chúng ta sử dụng list các tuple (link, tag)
    data_list = group.loc[group['Link'] != '', ['Link', 'Tags']].values.tolist()
    
    if data_list:
        # Tạo thư mục theo tên
        os.makedirs(name, exist_ok=True)
        file_path = os.path.join(name, 'links.txt')
        
        # Ghi dữ liệu vào file
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data_list:
                link = item[0]
                tag = item[1]
                # Ghi theo định dạng yêu cầu: <link>: <tag>
                f.write(f"{link}: {tag}\n")
        
        print(f"[OK] Đã gom {len(data_list)} dòng vào thư mục: {name}/")

print("--- Hoàn thành ---")