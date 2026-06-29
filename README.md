# Polk County FL News / Development Tracker — v8

This version adds real live story collection.

## What changed
- Live Google News RSS collection, no API key required.
- Optional NewsAPI.org support with `NEWS_API_KEY`.
- Optional GNews.io support with `GNEWS_API_KEY`.
- Searches all Polk County municipalities.
- Filters for positive development topics only.
- Blocks crime/crash/death/fire/lawsuit style stories.
- Updates `data/news.json`.
- GitHub Action runs every 15 minutes and can also be run manually.

## Upload
Upload all files/folders in this ZIP to the root of your GitHub repo.

## Run live update now
Go to:

Actions → Update Polk County News → Run workflow

Wait about 1–2 minutes, then refresh the website.

## Optional API keys
Repo → Settings → Secrets and variables → Actions → New repository secret

Add either or both:

- `NEWS_API_KEY`
- `GNEWS_API_KEY`

The site still works without those keys using Google News RSS.
