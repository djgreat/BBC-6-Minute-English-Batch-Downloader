import os
import re
import json
import time
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

ENTRY_URLS = {
    "2026": "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2026",
    "2025": "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2025",
    "2024": "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2024"
}

BASE_URL = "https://www.bbc.co.uk"
# Create downloads directory in the same folder as the script
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SYNC_STATUS.md")

def update_status_file(latest_date, count):
    """Updates a status file with the latest sync information."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""# BBC 6 Minute English Sync Status

- **Last Sync Time / 最后同步时间**: {now}
- **Latest Episode Date / 最新单期日期**: {latest_date}
- **New Episodes Downloaded / 本次新增下载**: {count}

---
*This file is automatically updated by the downloader skill.*
"""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(content)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_episodes.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except Exception:
                return set()
    return set()

def save_db(db_list):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(db_list), reverse=True), f, indent=4)

def sanitize_filename(name):
    """Remove illegal characters from filename."""
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip()

def format_date(date_str):
    """
    Format date from '23 Apr 2026' to '2026/04/23'
    """
    try:
        dt = datetime.strptime(date_str, "%d %b %Y")
        return dt.strftime("%Y/%m/%d")
    except ValueError:
        # Fallback if format is weird
        return date_str.replace(" ", "_")

def download_file(url, filepath):
    if os.path.exists(filepath):
        print(f"      [SKIP] Already exists: {os.path.basename(filepath)}")
        return True
        
    try:
        print(f"      [DOWNLOADING] {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        res = requests.get(url, headers=headers, stream=True, timeout=30)
        res.raise_for_status()
        
        tmp_filepath = filepath + ".tmp"
        with open(tmp_filepath, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        os.rename(tmp_filepath, filepath)
        print(f"      [SUCCESS] Saved to {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"      [ERROR] Failed to download {url}: {e}")
        if os.path.exists(filepath + ".tmp"):
            os.remove(filepath + ".tmp")
        return False

def parse_episode_page(url, session):
    """Fetches episode page and extracts download links."""
    links = {"audio": None, "transcript": None, "worksheet": None}
    try:
        res = session.get(url, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        a_tags = soup.find_all('a', href=True)
        
        for a in a_tags:
            text = a.get_text(strip=True).lower()
            href = a['href']
            if "audio" in text or href.endswith('.mp3'):
                if not links["audio"]: links["audio"] = href
            elif "transcript" in text or "transcript.pdf" in href or "transcript_.pdf" in href:
                if not links["transcript"]: links["transcript"] = href
            elif ("pdf" in text and "transcript" not in text) or "worksheet.pdf" in href or "worksheet_.pdf" in href or "worksheet" in text:
                if not links["worksheet"]: links["worksheet"] = href
    except Exception as e:
        print(f"    [ERROR] Parsing page {url}: {e}")
    return links

def process_episode(episode_url, title, date_str, db, session, force=False):
    """Processes a single episode: parses page and downloads files."""
    episode_id = episode_url.split('/')[-1]
    if not force and episode_id in db:
        print(f"  [SKIPPED] {episode_id} - already downloaded.")
        return False

    formatted_date_path = format_date(date_str)
    ep_dir = os.path.join(DOWNLOADS_DIR, os.path.normpath(formatted_date_path + "_" + title))
    
    print(f"\n  [*] Processing: {title} ({date_str})")
    print(f"      URL: {episode_url}")
    
    links = parse_episode_page(episode_url, session)
    if not any(links.values()):
        print("      [WARNING] No download links found. Skipping.")
        return False
        
    if not os.path.exists(ep_dir):
        os.makedirs(ep_dir)
        
    success_count = 0
    for key, filename in [("audio", "audio.mp3"), ("transcript", "transcript.pdf"), ("worksheet", "worksheet.pdf")]:
        if links[key]:
            if download_file(links[key], os.path.join(ep_dir, filename)):
                success_count += 1
    
    if success_count > 0:
        db.add(episode_id)
        save_db(db)
        return True
    return False

def scan_archive(archive_url, session, db, limit=None):
    """Scans an archive page for episodes."""
    count = 0
    latest_date = "Unknown"
    try:
        res = session.get(archive_url, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        text_divs = soup.find_all('div', class_='text')
        
        for div in text_divs:
            h2 = div.find('h2')
            if not h2: continue
            a_tag = h2.find('a')
            if not a_tag: continue
            
            episode_url = urljoin(BASE_URL, a_tag['href'])
            title = sanitize_filename(a_tag.get_text(strip=True))
            
            date_str = "Unknown_Date"
            details_div = div.find('div', class_='details')
            if details_div:
                h3 = details_div.find('h3')
                if h3:
                    parts = h3.get_text(strip=True).split('/')
                    if len(parts) > 1: date_str = parts[-1].strip()

            if latest_date == "Unknown": latest_date = date_str

            if process_episode(episode_url, title, date_str, db, session):
                count += 1
            
            if limit and count >= limit:
                break
            time.sleep(0.5)
    except Exception as e:
        print(f"Error scanning archive {archive_url}: {e}")
    return count, latest_date

def main():
    parser = argparse.ArgumentParser(description="BBC 6 Minute English Downloader Skill")
    parser.add_argument("--latest", action="store_true", help="Download only the latest episode")
    parser.add_argument("--year", type=str, help="Download episodes from a specific year (e.g., 2025)")
    parser.add_argument("--url", type=str, help="Download a specific episode by its URL")
    parser.add_argument("--all", action="store_true", help="Sync all available years (default behavior)")
    
    args = parser.parse_args()
    
    print("=== BBC 6 Minute English Downloader Skill ===")
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)
        
    db = load_db()
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    
    total_new = 0
    final_latest_date = "Unknown"

    if args.url:
        print(f"-> Targeted Download: {args.url}")
        try:
            res = session.get(args.url, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            title = sanitize_filename(soup.find('h1').get_text(strip=True)) if soup.find('h1') else "Unknown_Title"
            date_str = "Unknown_Date"
            if process_episode(args.url, title, date_str, db, session, force=True):
                total_new = 1
                final_latest_date = date_str
        except Exception as e:
            print(f"Error fetching URL: {e}")

    elif args.latest:
        latest_year = sorted(ENTRY_URLS.keys(), reverse=True)[0]
        print(f"-> Checking latest episode in {latest_year}...")
        total_new, final_latest_date = scan_archive(ENTRY_URLS[latest_year], session, db, limit=1)

    elif args.year:
        if args.year in ENTRY_URLS:
            print(f"-> Scanning Year: {args.year}")
            total_new, final_latest_date = scan_archive(ENTRY_URLS[args.year], session, db)
        else:
            print(f"Error: Year {args.year} is not in supported archives.")

    else:
        # Default: Sync all
        for year in sorted(ENTRY_URLS.keys(), reverse=True):
            print(f"\n-> Scanning Archive: {year}")
            count, l_date = scan_archive(ENTRY_URLS[year], session, db)
            total_new += count
            if final_latest_date == "Unknown": final_latest_date = l_date

    print(f"\n=== Done! Successfully processed {total_new} new episodes. ===")
    update_status_file(final_latest_date, total_new)

if __name__ == "__main__":
    main()
