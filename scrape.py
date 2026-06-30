# scraper.py
import requests
import re
import os
from markdownify import markdownify as md

BASE_URL = "https://support.optisigns.com/api/v2"

def get_articles():
    """Lấy danh sách bài viết từ Zendesk API"""
    articles = []
    url = f"{BASE_URL}/help_center/articles.json?per_page=100"
    
    while url:
        response = requests.get(url)
        data = response.json()
        articles.extend(data['articles'])
        url = data.get('next_page')  # Pagination
    
    return articles

def html_to_markdown(html_content):
    """Chuyển HTML thành Markdown sạch"""
    # Dùng markdownify để convert
    markdown = md(html_content, heading_style="ATX", strip=['nav', 'script', 'style'])
    # Loại bỏ nav/ads
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    return markdown.strip()

def slugify(title):
    """Tạo slug từ title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    return re.sub(r'[-\s]+', '-', slug).strip('-')

def save_articles():
    """Lưu bài viết thành file Markdown"""
    os.makedirs('articles', exist_ok=True)
    articles = get_articles()
    
    for article in articles:
        slug = slugify(article['title'])
        markdown = html_to_markdown(article['body'])
        
        # Thêm metadata
        content = f"# {article['title']}\n\n"
        content += f"**URL:** {article['html_url']}\n\n"
        content += markdown
        
        filepath = f"articles/{slug}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved: {filepath}")
    
    print(f"\nTotal: {len(articles)} articles saved")

if __name__ == "__main__":
    save_articles()