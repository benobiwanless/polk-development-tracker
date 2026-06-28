# Polk County FL News / Polk Development Tracker

Positive development news site for Polk County, Florida.

## Test locally
Open `index.html` in a browser.

## Upload to GitHub
Upload everything in this folder to the root of your public repo:

`benobiwanless/polk-county-fl-news`

GitHub Pages settings can stay as:

- Source: Deploy from a branch
- Branch: main
- Folder: /(root)

## Auto updates
The workflow in `.github/workflows/update-news.yml` runs every 15 minutes and updates `data/news.json`.

After upload, go to **Actions** and enable workflows if GitHub asks.
