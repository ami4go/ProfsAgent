import os
import json
import time
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

def call_with_retry(client, prompt_text, max_retries=5):
    """Call Gemini API with exponential backoff on 503 errors."""
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedCourse,
                    temperature=0.0
                ),
            )
            return response
        except Exception as e:
            err_str = str(e)
            if "503" in err_str or "UNAVAILABLE" in err_str:
                wait = 2 ** attempt  # 2, 4, 8, 16, 32 seconds
                print(f"  503 error (attempt {attempt}/{max_retries}). Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise e
    raise RuntimeError(f"Failed after {max_retries} retries")

def main():
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    parsed_path = DATA_PARSED_DIR / "DES537A.json"
    extracted_path = DATA_EXTRACTED_DIR / "DES537A.json"
    DATA_EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(parsed_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
        
    sections = parsed_data.get("sections", {})
    prompt_text = "Extract the course information from the following parsed CSV cells. The cells are given as [row, col, value].\n\n"
    for sec_name, sec_data in sections.items():
        prompt_text += f"=== SECTION: {sec_name.upper()} ===\n"
        for cell in sec_data.get("cells", []):
            prompt_text += f"{cell}\n"
        prompt_text += "\n"
    
    print("Calling Gemini API (with retry)...")
    response = call_with_retry(client, prompt_text)
    
    parsed_response = json.loads(response.text)
    with open(extracted_path, "w", encoding="utf-8") as f:
        json.dump(parsed_response, f, indent=4)
        
    print(f"Successfully saved to {extracted_path}")

if __name__ == "__main__":
    main()
