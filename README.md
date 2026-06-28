# Polk County FL News / Polk Development Tracker

Positive development news site for Polk County, Florida.

## Upload to GitHub
Upload everything in this folder to the root of your public repo:

`benobiwanless/polk-county-fl-news`

GitHub Pages settings can stay as:

- Source: Deploy from a branch
- Branch: main
- Folder: /(root)

## Version 3 changes

- Full-width layout
- Removed the auto-refresh badge and browser meta refresh
- Dynamic cards loaded from `data/news.json`
- Search, category filter, and city filter
- Larger featured story and larger desktop layout
- Mobile-friendly responsive layout

## Auto updates
The workflow in `.github/workflows/update-news.yml` runs every 15 minutes and updates `data/news.json`.

After upload, go to **Actions** and enable workflows if GitHub asks.
