import gspread
import pandas as pd
import os
from oauth2client.service_account import ServiceAccountCredentials

# 1. Kết nối và lấy dữ liệu
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Mở tệp và lấy dữ liệu thô (giả sử tiêu đề nằm ở hàng 1 sau khi bạn đã dọn dẹp)
sheet = client.open("Link Data").sheet1
raw_data = sheet.get_all_values()
df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

# 2. Làm sạch dữ liệu cột "Người làm" và "Link"
# Loại bỏ khoảng trắng thừa để tránh lỗi khi tạo thư mục
df['Người làm'] = df['Người làm'].astype(str).str.strip()
df['Link'] = df['Link'].astype(str).str.strip()

# 3. Lấy danh sách những người cần xuất file (NĐT, Q.Huy, Thiện)
# Bạn có thể dùng df['Người làm'].unique() để lấy tự động tất cả mọi người
names = ['NĐT', 'Q.Huy', 'Thiện']
# Giả sử df đã được load từ Google Sheets ở bước trước
# Làm sạch dữ liệu ban đầu

# --- LOGIC MỚI: CHUYỂN ĐỔI TÊN NGƯỜI LÀM ---
# Nếu tên KHÔNG NẰM TRONG ['Thiện', 'Q.Huy'] thì đổi thành 'NĐT'
df['Người làm_Final'] = df['Người làm'].apply(lambda x: x if x in ['Thiện', 'Q.Huy'] else 'NĐT')

# Bây giờ chúng ta gom nhóm theo cột 'Người làm_Final' vừa tạo
grouped = df.groupby('Người làm_Final')

print("--- Bắt đầu xuất file theo logic mới ---")

# Duyệt qua 3 nhóm: Thiện, Q.Huy và NĐT (nhóm NĐT lúc này đã bao gồm tất cả những người còn lại)
for name, group in grouped:
    
    # Lọc bỏ các link trống trong nhóm
    links = group.loc[group['Link'] != '', 'Link'].tolist()
    
    if links:
        # Tạo thư mục theo tên (Thiện, Q.Huy, hoặc NĐT)
        os.makedirs(name, exist_ok=True)
        file_path = os.path.join(name, 'links.txt')
        
        # Ghi toàn bộ link vào file links.txt của thư mục đó
        with open(file_path, 'w', encoding='utf-8') as f:
            for link in links:
                f.write(link + '\n')
        
        print(f"[OK] Đã gom và xuất {len(links)} link vào thư mục: {name}/")

print("--- Hoàn thành ---")