# main.py - Daily job: scrape + delta detect + upload to Gemini Files API

import hashlib
import json
import os
import logging
from dotenv import load_dotenv
from google import genai
from scrape import get_articles, slugify, html_to_markdown

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HASH_FILE = "article_hashes.json"
UPLOADED_FILES_CACHE = "uploaded_files.json"
ARTICLES_DIR = "articles"

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))


def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_hashes(hashes):
    with open(HASH_FILE, 'w', encoding='utf-8') as f:
        json.dump(hashes, f, indent=2)


def load_uploaded_cache():
    if os.path.exists(UPLOADED_FILES_CACHE):
        with open(UPLOADED_FILES_CACHE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_uploaded_cache(cache):
    with open(UPLOADED_FILES_CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def compute_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def save_and_upload(slug, content, title, html_url, uploaded_cache):
    """Luu file Markdown va upload len Gemini Files API"""
    os.makedirs(ARTICLES_DIR, exist_ok=True)

    md_content = f"# {title}\n\n**Article URL:** {html_url}\n\n{content}"
    filepath = os.path.join(ARTICLES_DIR, f"{slug}.md")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    filename = f"{slug}.md"
    try:
        with open(filepath, 'rb') as f:
            response = client.files.upload(
                file=f,
                config={"mime_type": "text/plain", "display_name": filename}
            )
        uploaded_cache[filename] = response.name
        logger.info(f"Uploaded: {filename}")
    except Exception as e:
        logger.error(f"Failed to upload {filename}: {e}")


def main():
    old_hashes = load_hashes()
    new_hashes = {}
    uploaded_cache = load_uploaded_cache()

    added = 0
    updated = 0
    skipped = 0

    logger.info("Fetching articles from support.optisigns.com...")
    articles = get_articles()
    logger.info(f"Found {len(articles)} articles")

    for article in articles:
        slug = slugify(article['title'])
        content = html_to_markdown(article['body'])
        content_hash = compute_hash(content)
        new_hashes[slug] = content_hash

        if slug not in old_hashes:
            logger.info(f"[NEW] {article['title']}")
            save_and_upload(slug, content, article['title'], article['html_url'], uploaded_cache)
            added += 1
        elif old_hashes[slug] != content_hash:
            logger.info(f"[UPDATED] {article['title']}")
            save_and_upload(slug, content, article['title'], article['html_url'], uploaded_cache)
            updated += 1
        else:
            skipped += 1

    save_hashes(new_hashes)
    save_uploaded_cache(uploaded_cache)

    logger.info("=" * 40)
    logger.info("=== Daily Job Complete ===")
    logger.info(f"Total articles: {len(articles)}")
    logger.info(f"Added:   {added}")
    logger.info(f"Updated: {updated}")
    logger.info(f"Skipped: {skipped}")
    logger.info("=" * 40)


if __name__ == "__main__":
    main()