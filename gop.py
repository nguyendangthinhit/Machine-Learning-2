#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script gộp file từ nhiều thư mục
Hỗ trợ: .txt, .json, .csv
"""

import sys
import os
import json
from typing import List, Dict, Any


class FileMerger:
    """Class để gộp các file từ nhiều thư mục"""
    
    def __init__(self, filename: str, folders: List[str]):
        """
        Khởi tạo FileMerger
        
        Args:
            filename: Tên file cần gộp (vd: links.txt, data.json)
            folders: Danh sách thư mục cần tìm file
        """
        self.filename = filename
        self.folders = folders
        self.file_extension = os.path.splitext(filename)[1].lower()
        self.output_path = filename  # File output ở thư mục hiện tại
    
    def merge(self):
        """Gộp file dựa vào extension"""
        print("=" * 60)
        print(f"🔄 GỘP FILE: {self.filename}")
        print("=" * 60)
        print(f"📁 Tìm kiếm trong {len(self.folders)} thư mục:")
        for folder in self.folders:
            print(f"   - {folder}")
        print("=" * 60)
        print()
        
        # Kiểm tra extension và gọi hàm tương ứng
        if self.file_extension == '.txt':
            self._merge_txt()
        elif self.file_extension == '.json':
            self._merge_json()
        elif self.file_extension == '.csv':
            self._merge_csv()
        else:
            print(f"❌ Lỗi: Không hỗ trợ file extension '{self.file_extension}'")
            print("💡 Các extension được hỗ trợ: .txt, .json, .csv")
            sys.exit(1)
    
    def _find_files(self) -> List[str]:
        """
        Tìm tất cả file trong các thư mục
        
        Returns:
            List đường dẫn các file tìm thấy
        """
        found_files = []
        missing_folders = []
        
        for folder in self.folders:
            file_path = os.path.join(folder, self.filename)
            
            if os.path.isfile(file_path):
                found_files.append(file_path)
                print(f"✅ Tìm thấy: {file_path}")
            else:
                missing_folders.append(folder)
                print(f"⚠️  Không tìm thấy file trong: {folder}")
        
        print()
        
        if missing_folders:
            print(f"💡 Bỏ qua {len(missing_folders)} thư mục không có file")
            print()
        
        if not found_files:
            print("❌ Không tìm thấy file nào!")
            sys.exit(1)
        
        return found_files
    
    def _merge_txt(self):
        """Gộp các file .txt"""
        print("📝 Đang gộp file TXT...\n")
        
        found_files = self._find_files()
        
        all_lines = []
        line_count = 0
        
        # Đọc từng file
        for file_path in found_files:
            folder_name = os.path.dirname(file_path)
            print(f"📖 Đọc từ: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip()]
                    all_lines.extend(lines)
                    line_count += len(lines)
                    print(f"   → {len(lines)} dòng\n")
            except Exception as e:
                print(f"   ❌ Lỗi khi đọc file: {e}\n")
        
        # Ghi file output
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                for line in all_lines:
                    f.write(line + '\n')
            
            print("=" * 60)
            print(f"✅ ĐÃ GỘP THÀNH CÔNG!")
            print("=" * 60)
            print(f"📄 File output: {self.output_path}")
            print(f"📊 Tổng số dòng: {line_count}")
            print(f"📁 Từ {len(found_files)} file")
            print("=" * 60)
        except Exception as e:
            print(f"❌ Lỗi khi ghi file: {e}")
            sys.exit(1)
    
    def _merge_json(self):
        """Gộp các file .json"""
        print("📝 Đang gộp file JSON...\n")
        
        found_files = self._find_files()
        
        merged_data = {}
        total_keys = 0
        
        # Đọc từng file JSON
        for file_path in found_files:
            folder_name = os.path.dirname(file_path)
            print(f"📖 Đọc từ: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Kiểm tra kiểu dữ liệu
                    if isinstance(data, dict):
                        # Gộp dictionary
                        before_count = len(merged_data)
                        merged_data.update(data)
                        after_count = len(merged_data)
                        new_keys = after_count - before_count
                        
                        print(f"   → {len(data)} entries")
                        if new_keys < len(data):
                            print(f"   ⚠️  {len(data) - new_keys} entries bị trùng (đã ghi đè)")
                        print()
                        
                        total_keys += len(data)
                    elif isinstance(data, list):
                        # Nếu là list, cần xử lý khác
                        print(f"   ⚠️  File là array, chưa hỗ trợ gộp array")
                        print(f"   💡 Chỉ hỗ trợ gộp JSON object (dictionary)")
                        print()
                    else:
                        print(f"   ⚠️  Định dạng JSON không hợp lệ")
                        print()
            except json.JSONDecodeError as e:
                print(f"   ❌ Lỗi JSON: {e}\n")
            except Exception as e:
                print(f"   ❌ Lỗi khi đọc file: {e}\n")
        
        # Ghi file output
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            
            print("=" * 60)
            print(f"✅ ĐÃ GỘP THÀNH CÔNG!")
            print("=" * 60)
            print(f"📄 File output: {self.output_path}")
            print(f"📊 Tổng số entries: {len(merged_data)}")
            print(f"📁 Từ {len(found_files)} file")
            if len(merged_data) < total_keys:
                print(f"⚠️  Có {total_keys - len(merged_data)} entries bị trùng (đã ghi đè)")
            print("=" * 60)
        except Exception as e:
            print(f"❌ Lỗi khi ghi file: {e}")
            sys.exit(1)
    
    def _merge_csv(self):
        """Gộp các file .csv"""
        print("📝 Đang gộp file CSV...\n")
        
        found_files = self._find_files()
        
        all_lines = []
        header = None
        total_rows = 0
        
        # Đọc từng file
        for i, file_path in enumerate(found_files):
            print(f"📖 Đọc từ: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip()]
                    
                    if not lines:
                        print(f"   ⚠️  File rỗng\n")
                        continue
                    
                    # File đầu tiên: lấy header
                    if i == 0:
                        header = lines[0]
                        all_lines.append(header)
                        data_lines = lines[1:]
                    else:
                        # File tiếp theo: bỏ qua header nếu giống
                        if lines[0] == header:
                            data_lines = lines[1:]
                        else:
                            print(f"   ⚠️  Header khác với file đầu tiên!")
                            data_lines = lines
                    
                    all_lines.extend(data_lines)
                    total_rows += len(data_lines)
                    print(f"   → {len(data_lines)} dòng dữ liệu\n")
            except Exception as e:
                print(f"   ❌ Lỗi khi đọc file: {e}\n")
        
        # Ghi file output
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                for line in all_lines:
                    f.write(line + '\n')
            
            print("=" * 60)
            print(f"✅ ĐÃ GỘP THÀNH CÔNG!")
            print("=" * 60)
            print(f"📄 File output: {self.output_path}")
            print(f"📊 Tổng số dòng dữ liệu: {total_rows}")
            print(f"📁 Từ {len(found_files)} file")
            print("=" * 60)
        except Exception as e:
            print(f"❌ Lỗi khi ghi file: {e}")
            sys.exit(1)


def main():
    """Hàm chính"""
    # Kiểm tra tham số
    if len(sys.argv) < 3:
        print("❌ Lỗi: Thiếu tham số!")
        print("\n📖 Cách sử dụng:")
        print("   python gop.py <tên_file> <thư_mục_1> [thư_mục_2] [thư_mục_3] ...")
        print("\n💡 Ví dụ:")
        print("   python gop.py links.txt NĐT Q.Huy Thiện")
        print("   python gop.py data.json NĐT Q.Huy Thiện")
        print("   python gop.py results.csv folder1 folder2 folder3")
        print("\n📝 File được hỗ trợ:")
        print("   - .txt  : Gộp tất cả dòng từ các file")
        print("   - .json : Gộp tất cả entries (phải là JSON object)")
        print("   - .csv  : Gộp tất cả dòng với header từ file đầu tiên")
        sys.exit(1)
    
    # Lấy tham số
    filename = sys.argv[1]
    folders = sys.argv[2:]
    
    # Loại bỏ dấu phẩy nếu người dùng gõ "NĐT, Q.Huy, Thiện"
    folders = [folder.strip().rstrip(',') for folder in folders]
    
    # Kiểm tra các thư mục có tồn tại không
    valid_folders = []
    invalid_folders = []
    
    for folder in folders:
        if os.path.isdir(folder):
            valid_folders.append(folder)
        else:
            invalid_folders.append(folder)
    
    if invalid_folders:
        print("⚠️  Cảnh báo: Các thư mục sau không tồn tại (sẽ bỏ qua):")
        for folder in invalid_folders:
            print(f"   - {folder}")
        print()
    
    if not valid_folders:
        print("❌ Không có thư mục hợp lệ nào!")
        print("\n💡 Các thư mục hiện có:")
        subdirs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
        if subdirs:
            for subdir in sorted(subdirs):
                print(f"   - {subdir}")
        else:
            print("   (Không có thư mục con nào)")
        sys.exit(1)
    
    # Tạo merger và thực hiện gộp
    merger = FileMerger(filename, valid_folders)
    merger.merge()


if __name__ == "__main__":
    main()