#!/usr/bin/env python3
"""Build data/news.json for Polk Development Tracker.

This starter updater pulls RSS/Atom feeds when available and filters for
positive Polk County development topics. Add/remove sources in SOURCES.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "news.json"

SOURCES = [
    "https://www.lakelandgov.net/news/rss/",
    "https://www.mywinterhaven.com/rss.aspx",
    "https://www.polk-county.net/news/feed/",
]

POSITIVE_TERMS = re.compile(
    r"\b(development|developments|housing|homes|apartments|subdivision|restaurant|retail|"
    r"shopping|grocery|hotel|resort|infrastructure|road|interchange|jobs|opening|opens|"
    r"coming soon|approved|planned|construction|groundbreaking|redevelopment|downtown|"
    r"mixed-use|warehouse|distribution|manufacturing|investment|expansion)\b",
    re.I,
)

POLK_TERMS = re.compile(
    r"\b(polk county|lakeland|winter haven|auburndale|bartow|haines city|davenport|"
    r"lake wales|mulberry|frostproof|fort meade|eagle lake|lake alfred|dundee|"
    r"hainescity|poinciana|four corners)\b",
    re.I,
)

NEGATIVE_TERMS = re.compile(
    r"\b(crash|arrest|murder|shooting|death|died|lawsuit|scandal|fraud|fire|"
    r"hurricane damage|fatal|injured|crime|theft|robbery|assault|closed permanently)\b",
    re.I,
)

@dataclass
class Item:
    title: str
    summary: str
    url: str
    source: str
    date: str
    category: str
    location: str
    image: str = "assets/sample-layout.png"


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "PolkDevelopmentTracker/1.0"})
    with urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_feed(xml_bytes: bytes, source_url: str) -> list[Item]:
    root = ET.fromstring(xml_bytes)
    channel_title = root.findtext("./channel/title") or source_url
    raw_items = root.findall("./channel/item")
    items: list[Item] = []
    for entry in raw_items[:40]:
        title = clean(entry.findtext("title"))
        url = clean(entry.findtext("link"))
        summary = clean(entry.findtext("description"))[:240]
        pub = clean(entry.findtext("pubDate"))
        try:
            date = parsedate_to_datetime(pub).strftime("%b %-d, %Y") if pub else "Recent"
        except Exception:
            date = "Recent"
        combined = f"{title} {summary}"
        if not title or not url:
            continue
        if NEGATIVE_TERMS.search(combined):
            continue
        if not POSITIVE_TERMS.search(combined):
            continue
        if not POLK_TERMS.search(combined):
            # Keep local-government feeds, but mark countywide if location is absent.
            pass
        items.append(Item(
            title=title,
            summary=summary or "A positive development update for Polk County, Florida.",
            url=url,
            source=channel_title,
            date=date,
            category=guess_category(combined),
            location=guess_location(combined),
        ))
    return items


def guess_category(text: str) -> str:
    checks = [
        ("Housing", r"housing|homes|apartments|subdivision|townhomes"),
        ("Restaurants", r"restaurant|dining|cafe|coffee"),
        ("Retail", r"retail|shopping|grocery|store"),
        ("Hotels", r"hotel|resort|hospitality"),
        ("Infrastructure", r"road|interchange|infrastructure|transportation"),
    ]
    for label, pattern in checks:
        if re.search(pattern, text, re.I):
            return label
    return "Development"


def guess_location(text: str) -> str:
    locations = ["Lakeland", "Winter Haven", "Auburndale", "Bartow", "Haines City", "Davenport", "Lake Wales", "Mulberry", "Frostproof", "Fort Meade", "Eagle Lake", "Lake Alfred", "Dundee", "Poinciana"]
    for loc in locations:
        if re.search(rf"\b{re.escape(loc)}\b", text, re.I):
            return f"{loc}, FL"
    return "Polk County, FL"


def unique(items: list[Item]) -> list[Item]:
    seen = set()
    output = []
    for item in items:
        key = item.url.rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def main() -> int:
    all_items: list[Item] = []
    errors: list[str] = []
    for source in SOURCES:
        try:
            all_items.extend(parse_feed(fetch(source), source))
        except (URLError, TimeoutError, ET.ParseError, Exception) as exc:
            errors.append(f"{source}: {exc}")

    items = unique(all_items)[:12]
    if not items and OUT.exists():
        # Keep previous data if no feed items are available.
        print("No new items found; keeping existing data.")
        if errors:
            print("Errors:", errors, file=sys.stderr)
        return 0

    payload = {
        "updated_at": datetime.now(timezone.utc).strftime("%b %d, %Y %I:%M %p UTC"),
        "items": [item.__dict__ for item in items],
        "errors": errors[-5:],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} items to {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
