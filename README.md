# Polk Development Tracker

## Version 7: YouTube Headlines Build

This version adds YouTube headline pulling for:

- Clermont FL
- Auburndale FL
- Lakeland FL
- Polk County FL development/news

## Files added/changed

- `data/youtube-headlines.json`
- `pages/youtube-setup.html`
- `tools/fetch_sources.py`
- `.github/workflows/fetch-live-data.yml`
- homepage YouTube section

## Required setup

YouTube search requires an official YouTube Data API key.

1. Create a YouTube Data API v3 key in Google Cloud.
2. In GitHub, go to repo → Settings → Secrets and variables → Actions.
3. Add a repository secret:
   - Name: `YOUTUBE_API_KEY`
   - Value: your API key
4. Go to repo → Actions → Fetch Live Data → Run workflow.
5. Refresh the GitHub Pages site.

The workflow runs every 6 hours.
