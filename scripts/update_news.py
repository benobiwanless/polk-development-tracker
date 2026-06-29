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
    "Housing": ["housing","apartment","apartments","subdivision","homes","townhomes","townhome","condo","residential","multifamily","single-family","villa","duplex","plat"],
    "Restaurant": ["restaurant","dining","cafe","coffee","barbecue","bbq","fast food","drive-thru","drive thru","chick-fil-a","starbucks","dunkin","waffle house"],
    "Retail": ["retail","store","shopping","grocery","publix","target","walmart","aldi","mall","plaza","shopping center","car wash","gas station"],
    "Hotel": ["hotel","inn","suites","resort","lodging","extended stay"],
    "Infrastructure": ["road","interchange","infrastructure","utility","utilities","trail","sidewalk","bridge","fdot","transportation"],
    "Commercial": ["commercial","warehouse","office","industrial","business park","medical office","distribution center"],
    "Community": ["park","library","school","recreation","community center","fire station","police station"]
}
STATUS_TERMS = [
    ("Grand Opening", ["grand opening","ribbon cutting","now open","opened","opening"]),
    ("Under Construction", ["under construction","construction begins","breaks ground","groundbreaking","building"]),
    ("Approved", ["approved","recommends approval","permit issued","permit","site plan","planning board"]),
    ("Coming Soon", ["coming soon","planned","announced","proposed","rezoning","land use"])
]

def clean(v):
    v = html.unescape(v or "")
    v = re.sub(r"<[^>]+>", " ", v)
    return re.sub(r"\s+", " ", v).strip()

def get_bytes(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 PolkDevelopmentTracker/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def get_json(url):
    return json.loads(get_bytes(url, 30).decode("utf-8", errors="replace"))

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

def extract_image_from_description(desc):
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc or "", re.I)
    return html.unescape(m.group(1)) if m else ""

def make_item(title, desc, link, date, source="", image=""):
    raw_desc = desc or ""
    title, desc = clean(title), clean(desc)
    combined = f"{title} {desc}"
    return {
        "title": title,
        "city": pick_city(combined),
        "category": pick_category(combined),
        "status": pick_status(combined),
        "date": norm_date(date),
        "summary": desc[:300] or "Live Polk County development update.",
        "source": clean(source) or source_from_title(title),
        "image": image or extract_image_from_description(raw_desc),
        "link": link,
        "featured": False
    }

def google_news(query, limit=20):
    url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=en-US&gl=US&ceid=US:en"
    root = ET.fromstring(get_bytes(url, 30))
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
    q = '("Polk County" OR "Lakeland FL" OR "Winter Haven" OR Auburndale OR Davenport OR "Haines City" OR "Lake Wales") AND (development OR construction OR restaurant OR retail OR housing OR hotel OR permit OR approved OR "site plan")'
    url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode({
        "q": q, "language": "en", "sortBy": "publishedAt", "pageSize": "100",
        "domains": ",".join(DOMAINS), "apiKey": key
    })
    data = get_json(url)
    out = []
    for a in data.get("articles", []):
        title = a.get("title","")
        desc = a.get("description","") or a.get("content","")
        if relevant(title, desc):
            out.append(make_item(title, desc, a.get("url",""), a.get("publishedAt",""), (a.get("source") or {}).get("name","NewsAPI"), a.get("urlToImage") or ""))
    return out

def gnews_api():
    key = os.getenv("GNEWS_API_KEY")
    if not key:
        return []
    q = '"Polk County" OR "Lakeland FL" OR "Winter Haven" OR Auburndale development construction restaurant retail housing hotel permit'
    url = "https://gnews.io/api/v4/search?" + urllib.parse.urlencode({
        "q": q, "lang": "en", "country": "us", "max": "100", "apikey": key
    })
    data = get_json(url)
    out = []
    for a in data.get("articles", []):
        title = a.get("title","")
        desc = a.get("description","")
        if relevant(title, desc):
            out.append(make_item(title, desc, a.get("url",""), a.get("publishedAt",""), (a.get("source") or {}).get("name","GNews"), a.get("image") or ""))
    return out

def dedupe(items):
    seen, out = set(), []
    for i in items:
        key = re.sub(r"[^a-z0-9]+"," ", i["title"].lower()).strip()[:130]
        url = (i.get("link") or "").split("?")[0]
        if key in seen or (url and url in seen):
            continue
        seen.add(key)
        if url:
            seen.add(url)
        out.append(i)
    return out

def main():
    items = []
    for fn in (newsapi, gnews_api):
        try:
            items.extend(fn())
        except Exception as e:
            print(fn.__name__, "failed:", e)

    queries = [
        '"Polk County Florida" (development OR construction OR restaurant OR retail OR housing OR hotel OR permit OR "site plan" OR approved OR rezoning)',
        '("Lakeland FL" OR "Winter Haven FL" OR Auburndale OR Davenport OR "Haines City" OR "Lake Wales") (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)',
        '("Polk County" "planning board") OR ("Polk County" "site plan") OR ("Polk County" rezoning)',
        '("Polk County" "coming soon") (restaurant OR retail OR hotel OR apartments OR homes)',
        '("Lakeland" OR "Winter Haven" OR Davenport) ("coming soon" OR "now open" OR "grand opening")',
        'site:theledger.com Polk County development construction approved homes restaurant retail',
        'site:lkldnow.com Lakeland development construction restaurant retail housing',
        'site:dailyridge.com Polk County development restaurant retail construction',
        'site:businessobserverfl.com Polk County development Lakeland Winter Haven',
        'site:growthspotter.com Polk County Lakeland Winter Haven development',
        'site:whatnoworlando.com Polk County OR Lakeland OR Davenport restaurant coming soon',
        'site:whatnowtampa.com Polk County OR Lakeland restaurant retail'
    ]

    for q in queries:
        try:
            items.extend(google_news(q, 25))
            time.sleep(.7)
        except Exception as e:
            print("Google News query failed:", q, e)

    for city in CITIES:
        if city == "Unincorporated":
            continue
        q = f'"{city} FL" (development OR construction OR restaurant OR retail OR housing OR hotel OR permit OR approved OR "coming soon" OR "now open")'
        try:
            items.extend(google_news(q, 10))
            time.sleep(.35)
        except Exception as e:
            print("City query failed:", city, e)

    items = dedupe(items)

    if not items:
        old = json.loads((ROOT/"data/news.json").read_text(encoding="utf-8"))
        items = old.get("items", [])

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "feed_mode": "live-expanded",
        "items": items[:90]
    }
    (ROOT/"data/news.json").write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(output['items'])} items")

if __name__ == "__main__":
    main()
