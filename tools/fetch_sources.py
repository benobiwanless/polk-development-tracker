import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "PolkDevelopmentTracker/1.0 (+https://benobiwanless.github.io/polk-development-tracker/)"
}

KEYWORDS = [
    "development", "restaurant", "retail", "business", "housing", "homes",
    "road", "construction", "permit", "planning", "commission", "opening",
    "commercial", "project", "site", "store", "publix", "aldi", "walmart",
    "7-eleven", "davenport", "auburndale", "lakeland", "winter haven"
]

def clean(text):
    return re.sub(r"\s+", " ", BeautifulSoup(text or "", "html.parser").get_text(" ")).strip()

def relevant(text):
    t = text.lower()
    return any(k in t for k in KEYWORDS)

def get_json(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()

def get_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def fetch_auburndale_wp():
    items = []
    url = "https://auburndalefl.com/wp-json/wp/v2/posts?per_page=10&_fields=link,date,title,excerpt"
    try:
        posts = get_json(url)
        for p in posts:
            title = clean(p.get("title", {}).get("rendered", ""))
            summary = clean(p.get("excerpt", {}).get("rendered", ""))
            text = f"{title} {summary}"
            if not title:
                continue
            if relevant(text):
                items.append({
                    "title": title,
                    "source": "City of Auburndale",
                    "url": p.get("link", "https://auburndalefl.com/news/"),
                    "date": p.get("date", ""),
                    "summary": summary[:260] or "Auburndale city update."
                })
    except Exception as e:
        items.append({
            "title": "Auburndale source check failed",
            "source": "City of Auburndale",
            "url": "https://auburndalefl.com/news/",
            "date": datetime.now(timezone.utc).isoformat(),
            "summary": f"Could not fetch WordPress API: {e}"
        })
    return items

def fetch_davenport_home():
    items = []
    url = "https://www.mydavenport.org/"
    try:
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        seen = set()
        for a in soup.find_all("a", href=True):
            title = clean(a.get_text(" "))
            if len(title) < 8 or title in seen:
                continue
            seen.add(title)
            if relevant(title):
                href = a["href"]
                if href.startswith("/"):
                    href = "https://www.mydavenport.org" + href
                items.append({
                    "title": title,
                    "source": "City of Davenport",
                    "url": href,
                    "date": "",
                    "summary": "Davenport official website item matched development tracker keywords."
                })
            if len(items) >= 8:
                break
    except Exception as e:
        items.append({
            "title": "Davenport source check failed",
            "source": "City of Davenport",
            "url": url,
            "date": datetime.now(timezone.utc).isoformat(),
            "summary": f"Could not fetch Davenport website: {e}"
        })
    return items

def main():
    items = []
    items.extend(fetch_auburndale_wp())
    items.extend(fetch_davenport_home())

    # Deduplicate by URL/title
    deduped = []
    seen = set()
    for item in items:
        key = (item.get("url"), item.get("title"))
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    if not deduped:
        deduped = [{
            "title": "No matching live source items found",
            "source": "Automated Fetch",
            "url": "https://auburndalefl.com/news/",
            "date": datetime.now(timezone.utc).isoformat(),
            "summary": "The fetch ran, but no items matched the development tracker keywords."
        }]

    (DATA / "live-news.json").write_text(json.dumps(deduped[:20], indent=2), encoding="utf-8")
    (DATA / "last-updated.json").write_text(json.dumps({
        "lastUpdatedUtc": datetime.now(timezone.utc).isoformat(),
        "note": "Updated by GitHub Actions workflow"
    }, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
