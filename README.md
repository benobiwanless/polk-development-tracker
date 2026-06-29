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


## v11
- Removed the Featured Project section.
- Homepage now opens directly into Latest Development Updates.
- News cards are larger on desktop.
- Live GitHub Action feed remains unchanged.


v12: Removed navigation links while preserving the blue navigation bar.


## v13
- Blue bar is now a live rotating ticker from the newest stories.
- Added better category-based fallback images.
- Improved mobile spacing and card sizing.
- Added subtle card hover effect on desktop.


## v14
- Adds local category image files so cards always have images.
- Expands Google News searches for more stories.
- Increases feed output up to 90 items.
- Adds optional GNEWS_API_KEY support.
- Adds more development keywords: zoning, site plan, agenda, ribbon cutting, mixed-use, distribution center, etc.
