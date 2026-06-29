#!/usr/bin/env python3
"""
Polk County FL Development Tracker live feed updater.

Default mode uses Google News RSS, so it works without API keys.
Optional:
- NEWS_API_KEY for NewsAPI.org
- GNEWS_API_KEY for GNews.io

Output:
- data/news.json
"""
import email.utils
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "sources.json").read_text(encoding="utf-8"))

CITIES = CONFIG["cities"]
POSITIVE = [t.lower() for t in CONFIG["positive_terms"]]
BLOCKED = [t.lower() for t in CONFIG["blocked_terms"]]
DOMAINS = CONFIG.get("news_domains", [])

CATEGORY_TERMS = {
    "Housing": ["housing", "apartment", "apartments", "subdivision", "homes", "townhomes", "condo", "residential", "single-family"],
    "Restaurant": ["restaurant", "dining", "cafe", "coffee", "barbecue", "bbq", "fast food", "drive-thru", "tavern", "brewery"],
    "Retail": ["retail", "store", "shopping", "grocery", "publix", "target", "walmart", "aldi", "mall", "plaza"],
    "Hotel": ["hotel", "inn", "suites", "resort", "lodging", "extended stay"],
    "Infrastructure": ["road", "interchange", "infrastructure", "utility", "utilities", "trail", "sidewalk", "bridge", "fdot"],
    "Commercial": ["commercial", "warehouse", "office", "industrial", "business park", "medical office"],
    "Community": ["park", "library", "school", "recreation", "community center", "fire station"],
}

STATUS_TERMS = [
    ("Grand Opening", ["grand opening", "now open", "opens", "opened"]),
    ("Under Construction", ["under construction", "construction begins", "breaks ground", "groundbreaking"]),
    ("Approved", ["approved", "permit issued", "permit", "site plan"]),
    ("Coming Soon", ["coming soon", "planned", "announced", "proposed"]),
]

def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

def request_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PolkDevelopmentTracker/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))

def request_bytes(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PolkDevelopmentTracker/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()

def category_for(text: str) -> str:
    t = text.lower()
    for category, terms in CATEGORY_TERMS.items():
        if any(term in t for term in terms):
            return category
    return "Development"

def status_for(text: str) -> str:
    t = text.lower()
    for status, terms in STATUS_TERMS:
        if any(term in t for term in terms):
            return status
    return "Update"

def city_for(text: str) -> str:
    t = text.lower()
    for city in CITIES:
        if city != "Unincorporated" and city.lower() in t:
            return city
    if "polk county" in t:
        return "Polk County"
    return "Polk County"

def source_from_title(title: str) -> str:
    # Google News RSS titles often look like: Headline - Source Name
    if " - " in title:
        return title.rsplit(" - ", 1)[-1].strip()
    return "Google News"

def normalize_date(value: str) -> str:
    if not value:
        return datetime.now(timezone.utc).strftime("%b %d, %Y")
    try:
        dt = email.utils.parsedate_to_datetime(value)
        return dt.strftime("%b %d, %Y")
    except Exception:
        try:
            return datetime.fromisoformat(value.replace("Z","+00:00")).strftime("%b %d, %Y")
        except Exception:
            return value[:16]

def is_relevant(title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()
    if any(b in text for b in BLOCKED):
        return False
    if not ("polk county" in text or any(c.lower() in text for c in CITIES if c != "Unincorporated")):
        return False
    return any(p in text for p in POSITIVE)

def make_item(title, summary, link, date, source=""):
    title = clean_text(title)
    summary = clean_text(summary)
    combined = f"{title} {summary}"
    return {
        "title": title,
        "city": city_for(combined),
        "category": category_for(combined),
        "status": status_for(combined),
        "date": normalize_date(date),
        "summary": summary[:260] or "New Polk County development update found from a live news source.",
        "source": source or source_from_title(title),
        "image": "",
        "link": link,
        "featured": False
    }

def google_news_query_url(query: str) -> str:
    return "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=en-US&gl=US&ceid=US:en"

def fetch_google_news(query: str, limit=20):
    items = []
    xml = request_bytes(google_news_query_url(query))
    root = ET.fromstring(xml)
    for node in root.findall(".//item")[:limit]:
        title = node.findtext("title", "")
        link = node.findtext("link", "")
        pub = node.findtext("pubDate", "")
        desc = node.findtext("description", "")
        source = node.findtext("source", "") or source_from_title(title)
        if is_relevant(title, desc):
            items.append(make_item(title, desc, link, pub, source))
    return items

def fetch_newsapi():
    key = os.getenv("NEWS_API_KEY")
    if not key:
        return []
    domain_filter = ",".join(DOMAINS)
    query = '("Polk County" OR "Lakeland FL" OR "Winter Haven" OR Auburndale OR Davenport) AND (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)'
    url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode({
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": "50",
        "domains": domain_filter,
        "apiKey": key
    })
    data = request_json(url)
    out = []
    for article in data.get("articles", []):
        title = article.get("title", "")
        desc = article.get("description", "") or article.get("content", "")
        if is_relevant(title, desc):
            item = make_item(title, desc, article.get("url", ""), article.get("publishedAt", ""), (article.get("source") or {}).get("name", "NewsAPI"))
            item["image"] = article.get("urlToImage") or ""
            out.append(item)
    return out

def fetch_gnews_api():
    key = os.getenv("GNEWS_API_KEY")
    if not key:
        return []
    query = '"Polk County" OR "Lakeland FL" OR "Winter Haven" development construction restaurant retail housing hotel'
    url = "https://gnews.io/api/v4/search?" + urllib.parse.urlencode({
        "q": query,
        "lang": "en",
        "country": "us",
        "max": "50",
        "apikey": key
    })
    data = request_json(url)
    out = []
    for article in data.get("articles", []):
        title = article.get("title", "")
        desc = article.get("description", "")
        if is_relevant(title, desc):
            item = make_item(title, desc, article.get("url", ""), article.get("publishedAt", ""), article.get("source", {}).get("name", "GNews"))
            item["image"] = article.get("image") or ""
            out.append(item)
    return out

def dedupe(items):
    seen = set()
    clean = []
    for item in items:
        key = re.sub(r"[^a-z0-9]+", " ", item["title"].lower()).strip()[:120]
        url_key = item.get("link", "").split("?")[0]
        if key in seen or url_key in seen:
            continue
        seen.add(key)
        if url_key:
            seen.add(url_key)
        clean.append(item)
    return clean

def main():
    collected = []

    # Optional paid/API sources first.
    for fn in (fetch_newsapi, fetch_gnews_api):
        try:
            collected.extend(fn())
        except Exception as exc:
            print(f"{fn.__name__} failed: {exc}")

    # Free no-key Google News RSS searches.
    base_queries = [
        '"Polk County Florida" (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)',
        '("Lakeland FL" OR "Winter Haven FL" OR Auburndale OR Davenport) (development OR construction OR restaurant OR retail OR housing OR hotel)',
        'site:theledger.com Polk County development OR restaurant OR retail OR housing',
        'site:lkldnow.com Lakeland development construction restaurant retail',
        'site:dailyridge.com Polk County development restaurant retail',
        'site:businessobserverfl.com Polk County development Lakeland Winter Haven',
    ]

    for query in base_queries:
        try:
            collected.extend(fetch_google_news(query, limit=15))
            time.sleep(1)
        except Exception as exc:
            print(f"Google News query failed: {query} -> {exc}")

    # Smaller city sweep so places outside Lakeland/Winter Haven are not ignored.
    for city in CITIES:
        if city in ("Unincorporated", "Highland Park", "Hillcrest Heights"):
            continue
        query = f'"{city} FL" (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)'
        try:
            collected.extend(fetch_google_news(query, limit=6))
            time.sleep(1)
        except Exception as exc:
            print(f"City query failed: {city} -> {exc}")

    items = dedupe(collected)

    if not items:
        fallback = ROOT / "data" / "news.json"
        old = json.loads(fallback.read_text(encoding="utf-8"))
        items = old.get("items", [])

    # Mark first significant item as featured.
    for item in items:
        item["featured"] = False
    if items:
        items[0]["featured"] = True

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "feed_mode": "live",
        "items": items[:36]
    }
    (ROOT / "data" / "news.json").write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(output['items'])} live items to data/news.json")

if __name__ == "__main__":
    main()
