# p2p bot

Simple Python bot located in `p2pbot.py`.

## 📌 What this repo contains

- `p2pbot.py` — main bot script
- `docs/` — static website content for GitHub Pages
- `.github/workflows/gh-pages.yml` — workflow that deploys `docs/` to GitHub Pages

## 🚀 Running locally

1. Install Python 3.10+.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies (if any):

```bash
pip install -r requirements.txt
```

4. Run the bot:

```bash
python p2pbot.py
```

## 🧠 GitHub Pages (static site only)

This repo includes a simple static site in `docs/` that can be hosted via GitHub Pages. GitHub Pages cannot execute Python code, so it cannot run the bot.

## ⚠️ Notes

- Keep secrets out of the repo (do not commit API tokens or `.env` files).
- For a running bot, use a server or service that can execute Python (e.g., a VPS, Heroku, Railway, etc.).
