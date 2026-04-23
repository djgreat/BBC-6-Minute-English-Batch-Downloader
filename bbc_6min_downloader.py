import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

ENTRY_URLS = [
    "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2026",
    "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2025",
    "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english_2024"
]

BASE_URL = "https://www.bbc.co.uk"
# Create downloads directory in the same folder as the script
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
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
        json.dump(list(db_list), f, indent=4)

def sanitize_filename(name):
    """Remove illegal characters from filename."""
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip()

def format_date(date_str):
    """
    Format date from '23 Apr 2026' to '2026\04\23' 
    Wait, building nested structures is better: '2026/04/23'
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
        # Add headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        res = requests.get(url, headers=headers, stream=True, timeout=30)
        res.raise_for_status()
        
        # Write to a temporary file first
        tmp_filepath = filepath + ".tmp"
        with open(tmp_filepath, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        # Rename after successful download
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
    links = {
        "audio": None,
        "transcript": None,
        "worksheet": None
    }
    try:
        res = session.get(url, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print(f"    [ERROR] fetching {url}: {e}")
        return links

    soup = BeautifulSoup(res.text, "html.parser")
    a_tags = soup.find_all('a', href=True)
    
    for a in a_tags:
        text = a.get_text(strip=True).lower()
        href = a['href']
        
        # Basic matching based on common BBC naming conventions
        if "audio" in text or href.endswith('.mp3'):
            # Some lists have multiple mp3 links, we just grab the first one that looks right
            if not links["audio"]:
                links["audio"] = href
        elif "transcript" in text or "transcript.pdf" in href or "transcript_.pdf" in href:
            if not links["transcript"]:
                links["transcript"] = href
        elif ("pdf" in text and "transcript" not in text) or "worksheet.pdf" in href or "worksheet_.pdf" in href or "worksheet" in text:
            if not links["worksheet"]:
                links["worksheet"] = href
                
    return links

def main():
    print("=== BBC 6 Minute English Downloader (2024-Present) ===")
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)
        
    db = load_db()
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    new_downloads = 0

    for year_url in ENTRY_URLS:
        print(f"\n-> Scanning Archive: {year_url}")
        try:
            res = session.get(year_url, timeout=15)
            res.raise_for_status()
        except Exception as e:
            print(f"Error fetching archive {year_url}: {e}")
            continue
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Find all episodes in the list
        text_divs = soup.find_all('div', class_='text')
        
        for div in text_divs:
            # 1. Get episode URL & Title
            h2 = div.find('h2')
            if not h2: continue
            a_tag = h2.find('a')
            if not a_tag: continue
            
            episode_url = urljoin(BASE_URL, a_tag['href'])
            title = sanitize_filename(a_tag.get_text(strip=True))
            
            # Use episode path as unique ID
            episode_id = episode_url.split('/')[-1]
            
            if episode_id in db:
                print(f"  [SKIPPED] {episode_id} - already downloaded.")
                continue
                
            # 2. Get Date
            date_str = ""
            details_div = div.find('div', class_='details')
            if details_div:
                h3 = details_div.find('h3')
                if h3:
                    parts = h3.get_text(strip=True).split('/')
                    if len(parts) > 1:
                        date_str = parts[-1].strip()
                        
            if not date_str:
                print(f"  [WARNING] Could not parse date for {title}. Defaulting to 'Unknown_Date'")
                date_str = "Unknown_Date"
            
            formatted_date_path = format_date(date_str)
            if "_" in formatted_date_path:
                print(f"  [WARNING] Skipping unusual date format: {date_str} (might be older archive link)")
            
            # Format folder: downloads/YYYY/MM/DD_EpisodeTitle
            # e.g formatted_date_path is "2026/04/23"
            ep_dir = os.path.join(DOWNLOADS_DIR, os.path.normpath(formatted_date_path + "_" + title))
            
            print(f"\n  [*] Found new episode: {title} ({date_str})")
            print(f"      URL: {episode_url}")
            
            # 3. Parse Episode Page for true download links
            links = parse_episode_page(episode_url, session)
            if not any(links.values()):
                print("      [WARNING] No download links found on episode page. Skipping.")
                continue
                
            # Create directory
            if not os.path.exists(ep_dir):
                os.makedirs(ep_dir)
                
            # 4. Download files
            success_count = 0
            if links["audio"]:
                if download_file(links["audio"], os.path.join(ep_dir, "audio.mp3")):
                    success_count += 1
            
            if links["transcript"]:
                if download_file(links["transcript"], os.path.join(ep_dir, "transcript.pdf")):
                    success_count += 1
                    
            if links["worksheet"]:
                if download_file(links["worksheet"], os.path.join(ep_dir, "worksheet.pdf")):
                    success_count += 1
            
            # Mark as done if at least one file is downloaded
            if success_count > 0:
                db.add(episode_id)
                save_db(db)
                new_downloads += 1
            
            # Be polite to BBC servers
            time.sleep(1)

    print(f"\n=== Done! Successfully processed {new_downloads} new episodes. ===")

if __name__ == "__main__":
    main()
