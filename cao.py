#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cào tiêu đề từ các trang báo
Đọc links từ link.txt trong thư mục được chỉ định và lưu kết quả vào data.json
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import os
from typing import Dict

class TitleScraper:
    """Class để cào tiêu đề từ các trang web"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_title(self, url: str, timeout: int = 10) -> str:
        """
        Lấy tiêu đề từ một URL
        
        Args:
            url: URL cần lấy tiêu đề
            timeout: Thời gian timeout (giây)
            
        Returns:
            Tiêu đề của trang hoặc thông báo lỗi
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm tiêu đề - thử nhiều cách
            title = None
            
            # Cách 1: Thẻ <title>
            if soup.title:
                title = soup.title.get_text(strip=True)
            
            # Cách 2: Meta property og:title (thường chính xác hơn cho bài báo)
            if not title:
                og_title = soup.find('meta', property='og:title')
                if og_title and og_title.get('content'):
                    title = og_title.get('content').strip()
            
            # Cách 3: Meta name twitter:title
            if not title:
                twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
                if twitter_title and twitter_title.get('content'):
                    title = twitter_title.get('content').strip()
            
            # Cách 4: Thẻ h1 đầu tiên
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text(strip=True)
            
            return title if title else "Không tìm thấy tiêu đề"
            
        except requests.exceptions.Timeout:
            return f"Lỗi: Timeout khi truy cập"
        except requests.exceptions.RequestException as e:
            return f"Lỗi: {type(e).__name__}"
        except Exception as e:
            return f"Lỗi không xác định: {type(e).__name__}"
    
    def read_links(self, filename: str) -> list:
        """
        Đọc danh sách links từ file
        
        Args:
            filename: Đường dẫn file chứa links
            
        Returns:
            List các URLs
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                # Đọc từng dòng, loại bỏ khoảng trắng và dòng trống
                links = [line.strip() for line in f if line.strip()]
            return links
        except FileNotFoundError:
            print(f"❌ Lỗi: Không tìm thấy file {filename}")
            return []
        except Exception as e:
            print(f"❌ Lỗi khi đọc file: {e}")
            return []
    
    def scrape_all(self, input_file: str, output_file: str, delay: float = 1.0):
        """
        Cào tiêu đề từ tất cả links trong file và lưu kết quả
        
        Args:
            input_file: File chứa danh sách links
            output_file: File JSON để lưu kết quả
            delay: Thời gian delay giữa các request (giây)
        """
        print(f"📂 Đọc links từ: {input_file}")
        links = self.read_links(input_file)
        
        if not links:
            print("⚠️  Không có link nào để cào!")
            return
        
        print(f"📝 Tìm thấy {len(links)} links")
        print("🚀 Bắt đầu cào tiêu đề...\n")
        
        results = {}
        
        for i, url in enumerate(links, 1):
            print(f"[{i}/{len(links)}] Đang cào: {url}")
            
            title = self.get_title(url)
            results[url] = title
            
            # Hiển thị tiêu đề với độ dài giới hạn
            display_title = title if len(title) <= 80 else title[:77] + "..."
            print(f"  ✓ Tiêu đề: {display_title}\n")
            
            # Delay để tránh bị block (trừ request cuối cùng)
            if i < len(links):
                time.sleep(delay)
        
        # Lưu kết quả ra file JSON
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Đã lưu kết quả vào: {output_file}")
            print(f"✅ Tổng cộng: {len(results)} tiêu đề")
        except Exception as e:
            print(f"❌ Lỗi khi lưu file: {e}")


def process_folder(scraper, folder_name, delay=1.0):
    """
    Xử lý một thư mục
    
    Args:
        scraper: TitleScraper instance
        folder_name: Tên thư mục cần cào
        delay: Thời gian delay giữa các request
        
    Returns:
        True nếu thành công, False nếu có lỗi
    """
    # Xây dựng đường dẫn file
    input_file = os.path.join(folder_name, 'links.txt')
    output_file = os.path.join(folder_name, 'data.json')
    
    # Kiểm tra file link.txt có tồn tại không
    if not os.path.isfile(input_file):
        print(f"❌ Lỗi: Không tìm thấy file '{input_file}'")
        print(f"💡 Hãy tạo file 'links.txt' trong thư mục '{folder_name}'")
        return False
    
    print("=" * 60)
    print(f"🎯 CÀO TIÊU ĐỀ - THƯ MỤC: {folder_name.upper()}")
    print("=" * 60)
    
    # Chạy scraper
    scraper.scrape_all(input_file, output_file, delay)
    
    print("=" * 60)
    print(f"✨ HOÀN THÀNH THƯ MỤC: {folder_name.upper()}")
    print("=" * 60)
    print()
    
    return True


def main():
    """Hàm chính"""
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) < 2:
        print("❌ Lỗi: Thiếu tên thư mục!")
        print("\n📖 Cách sử dụng:")
        print("   python cao.py <tên_thư_mục_1> [tên_thư_mục_2] [tên_thư_mục_3] ...")
        print("\n💡 Ví dụ:")
        print('   python cao.py "NĐT" "Q.Huy" "Thiện"')
        sys.exit(1)
    
    # Lấy danh sách thư mục từ tham số
    folder_names = sys.argv[1:]
    
    # Kiểm tra từng thư mục có tồn tại không
    invalid_folders = []
    valid_folders = []
    
    for folder_name in folder_names:
        if not os.path.isdir(folder_name):
            invalid_folders.append(folder_name)
        else:
            valid_folders.append(folder_name)
    
    # Nếu có thư mục không tồn tại, chỉ hiển thị cảnh báo
    if invalid_folders:
        print("⚠️  Cảnh báo: Các thư mục sau không tồn tại (sẽ bỏ qua):")
        for folder in invalid_folders:
            print(f"   - {folder}")
        print()
    
    # Nếu không có thư mục hợp lệ nào
    if not valid_folders:
        print("❌ Không có thư mục hợp lệ nào để xử lý!")
        print(f"\n💡 Các thư mục hiện có:")
        # Liệt kê các thư mục con
        subdirs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
        if subdirs:
            for subdir in sorted(subdirs):
                print(f"   - {subdir}")
        else:
            print("   (Không có thư mục con nào)")
        sys.exit(1)

    
    # Hiển thị tổng quan
    print("=" * 60)
    print(f"🚀 BÁT ĐẦU CÀO {len(valid_folders)} THƯ MỤC")
    print("=" * 60)
    for i, folder in enumerate(valid_folders, 1):
        print(f"   {i}. {folder}")
    print("=" * 60)
    print()
    
    # Khởi tạo scraper
    scraper = TitleScraper()
    
    # Cấu hình delay
    delay = 1.0  # Delay 1 giây giữa các request
    
    # Thống kê
    success_count = 0
    failed_folders = []
    
    # Xử lý từng thư mục
    for i, folder_name in enumerate(valid_folders, 1):
        print(f"\n📍 [{i}/{len(valid_folders)}] Đang xử lý thư mục: {folder_name}")
        print()
        
        if process_folder(scraper, folder_name, delay):
            success_count += 1
        else:
            failed_folders.append(folder_name)
        
        # Delay giữa các thư mục (trừ thư mục cuối)
        if i < len(valid_folders):
            time.sleep(1)
    
    # Tổng kết
    print("\n" + "=" * 60)
    print("📊 TỔNG KẾT")
    print("=" * 60)
    print(f"✅ Thành công: {success_count}/{len(valid_folders)} thư mục")
    
    if failed_folders:
        print(f"❌ Thất bại: {len(failed_folders)} thư mục")
        for folder in failed_folders:
            print(f"   - {folder}")
    
    print("=" * 60)
    print("🎉 HOÀN TẤT TẤT CẢ!")
    print("=" * 60)


if __name__ == "__main__":
    main()