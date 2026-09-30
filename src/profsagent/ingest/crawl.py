import json
import urllib.request
import re
import os
import time
import hashlib
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
COURSES_JSON_URL = "https://techtree.iiitd.edu.in/static/Courses.json"

def fetch_courses_json():
    print("Fetching Courses.json...")
    req = urllib.request.Request(COURSES_JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    return data.get("data", [])

def extract_sheet_url(embed_link):
    if not embed_link or embed_link == "None":
        return None
    match = re.search(r'src="([^"]+)"', embed_link)
    if not match:
        return None
    url = match.group(1)
    
    # Convert /pubhtml... or /pub... to /pub?output=csv
    if "/pubhtml" in url:
        url = url.split("/pubhtml")[0] + "/pub?output=csv"
    elif "/pub?" in url:
        url = url.split("/pub?")[0] + "/pub?output=csv"
        
    return url

def download_sheet(code, url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read()
        return content
    except Exception as e:
        print(f"Error downloading {code}: {e}")
        return None

def main():
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = DATA_RAW_DIR / "manifest.json"
    
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {}

    courses = fetch_courses_json()
    print(f"Found {len(courses)} courses in index.")
    
    # Save the index itself just in case
    with open(DATA_RAW_DIR / "courses_index.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=4)
        
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    for idx, course in enumerate(courses):
        code = course.get("Course Code", "").strip().replace(" ", "_").replace("/", "_")
        if not code:
            continue
            
        embed_link = course.get("embed_link")
        url = extract_sheet_url(embed_link)
        
        if not url:
            # print(f"Skipping {code}: No valid sheet URL found.")
            skipped_count += 1
            continue
            
        print(f"[{idx+1}/{len(courses)}] Fetching {code}...", end=" ", flush=True)
        content = download_sheet(code, url)
        
        if content:
            sha256 = hashlib.sha256(content).hexdigest()
            
            # Check if we already have this exact file
            if code in manifest and manifest[code].get("sha256") == sha256:
                print("Unchanged (cached).")
                skipped_count += 1
            else:
                csv_path = DATA_RAW_DIR / f"{code}.csv"
                with open(csv_path, "wb") as f:
                    f.write(content)
                
                manifest[code] = {
                    "url": url,
                    "sha256": sha256,
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "name": course.get("Course Name")
                }
                print("Downloaded.")
                downloaded_count += 1
                
                # Save manifest continuously in case of interruption
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=4)
                
                # Rate limit
                time.sleep(1)
        else:
            print("Failed.")
            failed_count += 1
            
    print(f"\nCrawl complete: {downloaded_count} downloaded, {skipped_count} skipped/cached, {failed_count} failed.")

if __name__ == "__main__":
    main()
