#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cào tiêu đề từ các trang báo
Đọc links từ link.txt và lưu kết quả vào data.json
"""

import requests
from bs4 import BeautifulSoup
import json
import time
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
            return f"Lỗi: Timeout khi truy cập {url}"
        except requests.exceptions.RequestException as e:
            return f"Lỗi: {str(e)}"
        except Exception as e:
            return f"Lỗi không xác định: {str(e)}"
    
    def read_links(self, filename: str) -> list:
        """
        Đọc danh sách links từ file
        
        Args:
            filename: Tên file chứa links
            
        Returns:
            List các URLs
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                # Đọc từng dòng, loại bỏ khoảng trắng và dòng trống
                links = [line.strip() for line in f if line.strip()]
            return links
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {filename}")
            return []
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")
            return []
    
    def scrape_all(self, input_file: str, output_file: str, delay: float = 1.0):
        """
        Cào tiêu đề từ tất cả links trong file và lưu kết quả
        
        Args:
            input_file: File chứa danh sách links
            output_file: File JSON để lưu kết quả
            delay: Thời gian delay giữa các request (giây)
        """
        print(f"Đọc links từ {input_file}...")
        links = self.read_links(input_file)
        
        if not links:
            print("Không có link nào để cào!")
            return
        
        print(f"Tìm thấy {len(links)} links")
        print("Bắt đầu cào tiêu đề...\n")
        
        results = {}
        
        for i, url in enumerate(links, 1):
            print(f"[{i}/{len(links)}] Đang cào: {url}")
            
            title = self.get_title(url)
            results[url] = title
            
            print(f"  → Tiêu đề: {title}\n")
            
            # Delay để tránh bị block (trừ request cuối cùng)
            if i < len(links):
                time.sleep(delay)
        
        # Lưu kết quả ra file JSON
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✓ Đã lưu kết quả vào {output_file}")
            print(f"✓ Tổng cộng: {len(results)} tiêu đề")
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")


def main():
    """Hàm chính"""
    # Khởi tạo scraper
    scraper = TitleScraper()
    
    # Cấu hình
    input_file = 'link.txt'
    output_file = 'data.json'
    delay = 1.0  # Delay 1 giây giữa các request
    
    # Chạy scraper
    scraper.scrape_all(input_file, output_file, delay)


if __name__ == "__main__":
    main()
