"""
Single-key Gemini extraction — uses only the fresh key (KEY_3).
10s gap between calls = 6 req/min, well within 15 RPM limit.
"""
import os
import json
import glob
import time
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

import sys
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.profsagent.models.layer_a import ExtractedCourse
from google import genai
from google.genai import types

DATA_PARSED_DIR = BASE_DIR / "data" / "parsed"
DATA_EXTRACTED_DIR = BASE_DIR / "data" / "extracted"

def setup_clients():
    load_dotenv(BASE_DIR / ".env")
    clients = []
    for i in range(1, 9):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            clients.append(genai.Client(api_key=key))
    if not clients:
        raise ValueError("No GEMINI_API_KEYs found in .env")
    return clients

def call_gemini(clients, prompt_text, max_retries=14):
    for attempt in range(max_retries):
        # Pick a client based on the attempt number to rotate through keys
        client = clients[attempt % len(clients)]
        def _do():
            return client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedCourse,
                    temperature=0.0
                ),
            )
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(_do)
                return future.result(timeout=90)
        except Exception as e:
            err = str(e)[:100]
            if attempt < max_retries - 1:
                # With 7 keys, we can afford much shorter waits between retries
                # because we immediately swap to a fresh key
                wait = 2
                print(f"\n    Error: {err}. Rotating to next key (Retry {attempt+1}/{max_retries})...", end="", flush=True)
                time.sleep(wait)
            else:
                raise

def build_prompt(parsed_path):
    with open(parsed_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    sections = parsed_data.get("sections", {})
    if not sections:
        return None
    prompt = "Extract the course information from the following parsed CSV cells. The cells are given as [row, col, value].\n\n"
    for sec_name, sec_data in sections.items():
        prompt += f"=== SECTION: {sec_name.upper()} ===\n"
        for cell in sec_data.get("cells", []):
            prompt += f"{cell}\n"
        prompt += "\n"
    return prompt

def main():
    DATA_EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    clients = setup_clients()
    
    all_parsed = sorted(glob.glob(str(DATA_PARSED_DIR / "*.json")))
    todo = []
    cached = 0
    for pf in all_parsed:
        p = Path(pf)
        if (DATA_EXTRACTED_DIR / p.name).exists():
            cached += 1
        else:
            todo.append(p)
    
    total = len(todo)
    est_min = total * 10 // 60
    print(f"Total: {len(all_parsed)}, Cached: {cached}, Remaining: {total}")
    print(f"Estimated time: ~{est_min} minutes (10s gap)")
    print(f"{'='*50}\n")
    
    if total == 0:
        print("All done!")
        return
    
    success = 0
    failed = 0
    failed_codes = []
    start_time = time.time()
    
    for idx, pp in enumerate(todo, 1):
        code = pp.stem
        out = DATA_EXTRACTED_DIR / pp.name
        
        print(f"[{idx}/{total}] {code}...", end=" ", flush=True)
        prompt = build_prompt(pp)
        if prompt is None:
            print("SKIP")
            continue
        
        try:
            resp = call_gemini(clients, prompt)
            parsed = json.loads(resp.text)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=4)
            success += 1
            print("OK")
        except Exception as e:
            failed += 1
            failed_codes.append(code)
            print(f"FAILED: {str(e)[:80]}")
        
        time.sleep(10)
        
        if idx % 25 == 0:
            elapsed = time.time() - start_time
            rate = idx / elapsed * 60
            remaining = (total - idx) / rate if rate > 0 else 0
            print(f"\n--- {idx}/{total} ({idx/total*100:.0f}%) | OK:{success} FAIL:{failed} | {rate:.1f}/min | ~{remaining:.0f}min left ---\n")
    
    print(f"\n{'='*50}")
    print(f"DONE! Succeeded:{success} Cached:{cached} Failed:{failed}")
    if failed_codes:
        print(f"Failed: {failed_codes}")

if __name__ == "__main__":
    main()
