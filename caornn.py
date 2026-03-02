#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cào tiêu đề + 100 từ đầu nội dung từ các trang báo
Lưu kết quả vào data_rnn.json để train RNN
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import os
from typing import Dict, Tuple


class RNNScraper:
    """Cào tiêu đề + nội dung bài báo để train RNN"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    # ──────────────────────────────────────────────────────────────
    # TIÊU ĐỀ
    # ──────────────────────────────────────────────────────────────
    def get_title(self, soup: BeautifulSoup) -> str:
        """Lấy tiêu đề từ soup object"""

        # Ưu tiên og:title vì thường sạch hơn <title>
        og = soup.find('meta', property='og:title')
        if og and og.get('content'):
            return og['content'].strip()

        if soup.title:
            return soup.title.get_text(strip=True)

        tw = soup.find('meta', attrs={'name': 'twitter:title'})
        if tw and tw.get('content'):
            return tw['content'].strip()

        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        return "Không tìm thấy tiêu đề"

    # ──────────────────────────────────────────────────────────────
    # NỘI DUNG — lấy 100 từ đầu của bài
    # ──────────────────────────────────────────────────────────────
    def get_content_100_words(self, soup: BeautifulSoup) -> str:
        """
        Trích xuất 100 từ đầu tiên của nội dung bài báo.
        Thử nhiều selector phổ biến của các báo Việt Nam.
        Trả về chuỗi văn bản, KHÔNG phải HTML.
        """

        # Danh sách selector theo thứ tự ưu tiên
        # Bao phủ: VnExpress, Tuổi Trẻ, Dân Trí, Thanh Niên, Znews, Tiền Phong...
        content_selectors = [
            # Semantic HTML5
            'article',
            # VnExpress
            'div.fck_detail',
            'div.article-body',
            # Tuổi Trẻ
            'div.detail-content',
            'div#main-detail-body',
            # Dân Trí
            'div.singular-content',
            'div.dt-news__content',
            # Thanh Niên
            'div.detail__cmain',
            'div#contentBody',
            # Znews / Zing
            'div.the-article-body',
            # Tiền Phong
            'div.article__body',
            # Saostar
            'div.content-detail',
            # Fallback chung
            'div.content',
            'div.post-content',
            'div.entry-content',
            'main',
        ]

        raw_text = ""

        for selector in content_selectors:
            tag, _, cls = selector.partition('.')
            if cls:
                el = soup.find(tag, class_=cls)
            else:
                # Có thể là id hoặc tag đơn
                by_id = selector.partition('#')
                if by_id[1]:  # có dấu #
                    el = soup.find(by_id[0] or True, id=by_id[2])
                else:
                    el = soup.find(selector)

            if el:
                # Xoá các thẻ không liên quan trong nội dung
                for noise in el.find_all(['script', 'style', 'figure',
                                          'figcaption', 'aside', 'nav',
                                          'form', 'button', 'iframe']):
                    noise.decompose()

                raw_text = el.get_text(separator=' ', strip=True)
                if len(raw_text.split()) >= 20:   # cần ít nhất 20 từ mới tính
                    break

        # Fallback: lấy tất cả <p> trong body
        if len(raw_text.split()) < 20:
            paragraphs = soup.find_all('p')
            raw_text = ' '.join(p.get_text(strip=True) for p in paragraphs)

        # Lấy đúng 100 từ đầu
        words = raw_text.split()
        content_100 = ' '.join(words[:100])

        return content_100 if content_100 else "Không tìm thấy nội dung"

    # ──────────────────────────────────────────────────────────────
    # FETCH 1 URL
    # ──────────────────────────────────────────────────────────────
    def fetch(self, url: str, timeout: int = 10) -> Tuple[str, str]:
        """
        Fetch 1 URL, trả về (title, content_100_words)
        """
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')

            title   = self.get_title(soup)
            content = self.get_content_100_words(soup)
            return title, content

        except requests.exceptions.Timeout:
            return "Lỗi: Timeout", ""
        except requests.exceptions.RequestException as e:
            return f"Lỗi: {type(e).__name__}", ""
        except Exception as e:
            return f"Lỗi không xác định: {type(e).__name__}", ""

    # ──────────────────────────────────────────────────────────────
    # ĐỌC FILE LINKS
    # ──────────────────────────────────────────────────────────────
    def read_links(self, filename: str) -> list:
        """Đọc links từ file format: <url>: <tag>"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                result = []
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    idx = line.find(': ', 8)   # bỏ qua "https://"
                    if idx != -1:
                        url = line[:idx].strip()
                        tag = line[idx + 1:].strip()
                    else:
                        url = line
                        tag = "Không có tag"
                    result.append((url, tag))
                return result
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file {filename}")
            return []
        except Exception as e:
            print(f"❌ Lỗi đọc file: {e}")
            return []

    # ──────────────────────────────────────────────────────────────
    # CÀO TOÀN BỘ
    # ──────────────────────────────────────────────────────────────
    def scrape_all(self, input_file: str, output_file: str, delay: float = 1.0):
        """
        Cào tất cả links → lưu data_rnn.json

        Format output:
        {
          "https://...": {
            "title":   "Tiêu đề bài báo",
            "content": "100 từ đầu nội dung...",
            "tag":     "giải trí"
          },
          ...
        }
        """
        print(f"📂 Đọc links từ: {input_file}")
        links = self.read_links(input_file)

        if not links:
            print("⚠️  Không có link nào để cào!")
            return

        print(f"📝 Tìm thấy {len(links)} links")
        print("🚀 Bắt đầu cào tiêu đề + nội dung...\n")

        # Load kết quả cũ nếu file đã tồn tại (để resume khi bị ngắt)
        results = {}
        if os.path.isfile(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                print(f"📌 Resume: đã có {len(results)} bài, bỏ qua các URL trùng\n")
            except Exception:
                results = {}

        for i, (url, tag) in enumerate(links, 1):
            # Bỏ qua nếu đã cào rồi
            if url in results:
                print(f"[{i}/{len(links)}] ⏭  Bỏ qua (đã có): {url[:60]}")
                continue

            print(f"[{i}/{len(links)}] 🔍 {url[:70]}")
            print(f"  📌 Tag: {tag}")

            title, content = self.fetch(url)

            results[url] = {
                "title":   title,
                "content": content,
                "tag":     tag
            }

            # Preview
            print(f"  ✓ Tiêu đề : {title[:80]}")
            word_count = len(content.split())
            print(f"  ✓ Nội dung: {word_count} từ — {content[:60]}...")
            print()

            # Lưu ngay sau mỗi bài để tránh mất dữ liệu khi bị ngắt
            self._save(results, output_file)

            if i < len(links):
                time.sleep(delay)

        print(f"\n✅ Hoàn tất! Đã lưu {len(results)} bài vào: {output_file}")

    def _save(self, data: dict, path: str):
        """Lưu JSON (gọi nội bộ sau mỗi bài)"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  ⚠️  Lỗi lưu file: {e}")


# ──────────────────────────────────────────────────────────────────
# XỬ LÝ THƯ MỤC
# ──────────────────────────────────────────────────────────────────
def process_folder(scraper: RNNScraper, folder: str, delay: float = 1.0) -> bool:
    input_file  = os.path.join(folder, 'links.txt')
    output_file = os.path.join(folder, 'data_rnn.json')   # ← file mới

    if not os.path.isfile(input_file):
        print(f"❌ Không tìm thấy '{input_file}'")
        return False

    print("=" * 60)
    print(f"🎯 THƯ MỤC: {folder.upper()}")
    print(f"   Input : {input_file}")
    print(f"   Output: {output_file}")
    print("=" * 60)

    scraper.scrape_all(input_file, output_file, delay)

    print("=" * 60)
    print(f"✨ XONG: {folder.upper()}")
    print("=" * 60 + "\n")
    return True


# ──────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("❌ Thiếu tên thư mục!")
        print("\n📖 Cách dùng:")
        print("   python cao_rnn.py <thư_mục_1> [thư_mục_2] ...")
        print("\n💡 Ví dụ:")
        print("   python cao_rnn.py thinh")
        print("   python cao_rnn.py thinh thien huy")
        sys.exit(1)

    folder_names = sys.argv[1:]
    valid   = [f for f in folder_names if os.path.isdir(f)]
    invalid = [f for f in folder_names if not os.path.isdir(f)]

    if invalid:
        print("⚠️  Thư mục không tồn tại (bỏ qua):", ', '.join(invalid))

    if not valid:
        print("❌ Không có thư mục hợp lệ!")
        sys.exit(1)

    print("=" * 60)
    print(f"🚀 BẮT ĐẦU CÀO {len(valid)} THƯ MỤC")
    print("=" * 60)

    scraper = RNNScraper()
    success = 0

    for i, folder in enumerate(valid, 1):
        print(f"\n📍 [{i}/{len(valid)}] {folder}")
        if process_folder(scraper, folder):
            success += 1
        if i < len(valid):
            time.sleep(1)

    print("\n" + "=" * 60)
    print(f"📊 TỔNG KẾT: {success}/{len(valid)} thư mục thành công")
    print("=" * 60)
    print("🎉 HOÀN TẤT!")


if __name__ == "__main__":
    main()