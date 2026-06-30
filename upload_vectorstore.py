# upload_vectorstore.py
# Upload Markdown files len Gemini Files API lam knowledge base

import os
import json
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

ARTICLES_DIR = "articles"
UPLOADED_FILES_CACHE = "uploaded_files.json"


def load_uploaded_cache():
    """Doc cache file da upload"""
    if os.path.exists(UPLOADED_FILES_CACHE):
        with open(UPLOADED_FILES_CACHE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_uploaded_cache(cache):
    """Luu cache file da upload"""
    with open(UPLOADED_FILES_CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def upload_files():
    """Upload tat ca file Markdown len Gemini Files API"""
    cache = load_uploaded_cache()
    uploaded = 0
    skipped = 0
    failed = 0

    md_files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.md')]
    print(f"Found {len(md_files)} Markdown files to upload...")

    for filename in md_files:
        if filename in cache:
            skipped += 1
            continue

        filepath = os.path.join(ARTICLES_DIR, filename)
        try:
            print(f"Uploading: {filename}")
            with open(filepath, 'rb') as f:
                response = client.files.upload(
                    file=f,
                    config={"mime_type": "text/plain", "display_name": filename}
                )
            cache[filename] = response.name  # Luu file URI
            save_uploaded_cache(cache) # Luu luon de khong mat du lieu
            uploaded += 1

            # Tranh rate limit
            if uploaded % 5 == 0:
                print(f"  Progress: {uploaded} uploaded, sleeping 2s...")
                time.sleep(2)

        except Exception as e:
            print(f"  Failed: {filename} - {e}")
            failed += 1

    print(f"\n=== Upload Complete ===")
    print(f"Uploaded: {uploaded}")
    print(f"Skipped (cached): {skipped}")
    print(f"Failed: {failed}")
    print(f"Cache saved to: {UPLOADED_FILES_CACHE}")

    return cache


if __name__ == "__main__":
    upload_files()