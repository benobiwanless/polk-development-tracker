# Polk County FL News / Development Tracker — v10

## Important
Upload the entire contents of this ZIP to the root of your repo, including the hidden `.github` folder.

After upload, GitHub Actions should show:

`Update Polk County News`

## Run manually
Actions → Update Polk County News → Run workflow

## Auto update
Runs every 15 minutes with:

`cron: "*/15 * * * *"`

## Live source
Works without an API key using Google News RSS.

Optional secret:
- `NEWS_API_KEY`

## Files
- `index.html`
- `style.css`
- `app.js`
- `assets/Logo.png`
- `data/news.json`
- `config/sources.json`
- `scripts/update_news.py`
- `.github/workflows/update-news.yml`
