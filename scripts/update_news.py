#!/usr/bin/env python3
import email.utils, html, json, os, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "sources.json").read_text(encoding="utf-8"))

CITIES = CONFIG["cities"]
POSITIVE = [t.lower() for t in CONFIG["positive_terms"]]
BLOCKED = [t.lower() for t in CONFIG["blocked_terms"]]
DOMAINS = CONFIG.get("news_domains", [])

CATEGORY_TERMS = {
    "Housing": ["housing","apartment","apartments","subdivision","homes","townhomes","condo","residential"],
    "Restaurant": ["restaurant","dining","cafe","coffee","barbecue","bbq","fast food","drive-thru"],
    "Retail": ["retail","store","shopping","grocery","publix","target","walmart","aldi","mall","plaza"],
    "Hotel": ["hotel","inn","suites","resort","lodging","extended stay"],
    "Infrastructure": ["road","interchange","infrastructure","utility","utilities","trail","sidewalk","bridge","fdot"],
    "Commercial": ["commercial","warehouse","office","industrial","business park","medical office"],
    "Community": ["park","library","school","recreation","community center","fire station"]
}
STATUS_TERMS = [
    ("Grand Opening", ["grand opening","now open","opened"]),
    ("Under Construction", ["under construction","construction begins","breaks ground","groundbreaking"]),
    ("Approved", ["approved","permit issued","permit","site plan"]),
    ("Coming Soon", ["coming soon","planned","announced","proposed"])
]

def clean(v):
    v = html.unescape(v or "")
    v = re.sub(r"<[^>]+>", " ", v)
    return re.sub(r"\s+", " ", v).strip()

def get_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 PolkDevelopmentTracker/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def get_json(url):
    return json.loads(get_bytes(url).decode("utf-8", errors="replace"))

def norm_date(v):
    try:
        return email.utils.parsedate_to_datetime(v).strftime("%b %d, %Y")
    except Exception:
        try:
            return datetime.fromisoformat((v or "").replace("Z","+00:00")).strftime("%b %d, %Y")
        except Exception:
            return (v or datetime.now(timezone.utc).isoformat())[:16]

def pick_category(text):
    t = text.lower()
    for cat, terms in CATEGORY_TERMS.items():
        if any(term in t for term in terms):
            return cat
    return "Development"

def pick_status(text):
    t = text.lower()
    for status, terms in STATUS_TERMS:
        if any(term in t for term in terms):
            return status
    return "Update"

def pick_city(text):
    t = text.lower()
    for city in CITIES:
        if city != "Unincorporated" and city.lower() in t:
            return city
    if "polk county" in t:
        return "Polk County"
    return "Polk County"

def relevant(title, desc):
    t = f"{title} {desc}".lower()
    if any(b in t for b in BLOCKED):
        return False
    if not ("polk county" in t or any(c.lower() in t for c in CITIES if c != "Unincorporated")):
        return False
    return any(p in t for p in POSITIVE)

def source_from_title(title):
    return title.rsplit(" - ", 1)[-1].strip() if " - " in title else "Google News"

def make_item(title, desc, link, date, source=""):
    title, desc = clean(title), clean(desc)
    combined = f"{title} {desc}"
    return {
        "title": title,
        "city": pick_city(combined),
        "category": pick_category(combined),
        "status": pick_status(combined),
        "date": norm_date(date),
        "summary": desc[:280] or "Live Polk County development update.",
        "source": clean(source) or source_from_title(title),
        "image": "",
        "link": link,
        "featured": False
    }

def google_news(query, limit=15):
    url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=en-US&gl=US&ceid=US:en"
    root = ET.fromstring(get_bytes(url))
    out = []
    for node in root.findall(".//item")[:limit]:
        title = node.findtext("title","")
        desc = node.findtext("description","")
        if relevant(title, desc):
            out.append(make_item(title, desc, node.findtext("link",""), node.findtext("pubDate",""), node.findtext("source","")))
    return out

def newsapi():
    key = os.getenv("NEWS_API_KEY")
    if not key:
        return []
    q = '("Polk County" OR "Lakeland FL" OR "Winter Haven" OR Auburndale OR Davenport) AND (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)'
    url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode({
        "q": q, "language": "en", "sortBy": "publishedAt", "pageSize": "50",
        "domains": ",".join(DOMAINS), "apiKey": key
    })
    data = get_json(url)
    out = []
    for a in data.get("articles", []):
        title = a.get("title","")
        desc = a.get("description","") or a.get("content","")
        if relevant(title, desc):
            item = make_item(title, desc, a.get("url",""), a.get("publishedAt",""), (a.get("source") or {}).get("name","NewsAPI"))
            item["image"] = a.get("urlToImage") or ""
            out.append(item)
    return out

def dedupe(items):
    seen, out = set(), []
    for i in items:
        key = re.sub(r"[^a-z0-9]+"," ", i["title"].lower()).strip()[:120]
        url = (i.get("link") or "").split("?")[0]
        if key in seen or (url and url in seen):
            continue
        seen.add(key)
        if url: seen.add(url)
        out.append(i)
    return out

def main():
    items = []
    try:
        items.extend(newsapi())
    except Exception as e:
        print("NewsAPI failed:", e)

    queries = [
        '"Polk County Florida" (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)',
        '("Lakeland FL" OR "Winter Haven FL" OR Auburndale OR Davenport) (development OR construction OR restaurant OR retail OR housing OR hotel)',
        'site:theledger.com Polk County development OR restaurant OR retail OR housing',
        'site:lkldnow.com Lakeland development construction restaurant retail',
        'site:dailyridge.com Polk County development restaurant retail',
        'site:businessobserverfl.com Polk County development Lakeland Winter Haven'
    ]
    for q in queries:
        try:
            items.extend(google_news(q, 15))
            time.sleep(1)
        except Exception as e:
            print("Google News query failed:", q, e)

    for city in CITIES:
        if city == "Unincorporated":
            continue
        try:
            items.extend(google_news(f'"{city} FL" (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)', 5))
            time.sleep(.5)
        except Exception as e:
            print("City query failed:", city, e)

    items = dedupe(items)
    if not items:
        old = json.loads((ROOT/"data/news.json").read_text(encoding="utf-8"))
        items = old.get("items", [])

    for i in items:
        i["featured"] = False
    if items:
        items[0]["featured"] = True

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "feed_mode": "live-google-news",
        "items": items[:40]
    }
    (ROOT/"data/news.json").write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(output['items'])} items")

if __name__ == "__main__":
    main()
