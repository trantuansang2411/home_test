# AI Support Bot Clone

A mini-clone of OptiBot — customer support chatbot for OptiSigns. It scrapes support articles, converts them to Markdown, and uploads to an AI-powered vector store for intelligent Q&A.

## Features

- 🕷️ **Web Scraper**: Fetches articles from OptiSigns Zendesk support center
- 🔄 **Delta Detection**: Only uploads new/updated articles (using SHA-256 hashing)
- 🤖 **AI Assistant**: OpenAI Assistant with vector store for accurate answers with citations
- ⏰ **Daily Job**: Automated daily scraping via GitHub Actions cron job
- 🐳 **Dockerized**: One command to build and run

## Setup

1. Clone repo:
   ```bash
   git clone <repo-url>
   cd <repo-name>
   ```

2. Copy environment template:
   ```bash
   cp .env.sample .env
   ```

3. Add your API key to `.env`:
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   VECTOR_STORE_ID=vs_your_id_here
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run Locally

### First time (scrape all articles + create vector store):
```bash
python main.py
```

### Scrape only (without uploading):
```bash
python scrape.py
```

### Upload only (existing articles to new vector store):
```bash
python upload_vectorstore.py
```

## Run with Docker

```bash
docker build -t optibot .
docker run -e OPENAI_API_KEY=your_key -e VECTOR_STORE_ID=your_vs_id optibot
```

## Daily Job

- **Platform**: GitHub Actions
- **Schedule**: Daily at 00:00 UTC
- **Config**: [`.github/workflows/daily-scrape.yaml`](.github/workflows/daily-scrape.yaml)
- **Logs**: Check the "Actions" tab in GitHub repo

### Setup GitHub Secrets:
1. Go to repo **Settings** → **Secrets and variables** → **Actions**
2. Add `OPENAI_API_KEY` and `VECTOR_STORE_ID`

## Chunking Strategy

Files are uploaded as-is to the OpenAI Vector Store, which uses its built-in chunking with the `auto` strategy. Each Markdown file represents one support article, keeping context intact per article. OpenAI's default chunking (max 800 tokens, 400 token overlap) handles splitting for retrieval.

## Delta Detection

The scraper uses **SHA-256 hashing** to detect changes:
- On each run, it hashes the content of every article
- Compares against `article_hashes.json` from the previous run
- Only uploads articles that are **new** or have **changed content**
- Logs counts: added, updated, skipped

## Screenshot

![Assistant answering sample question](screenshots/optibot-answer.png)