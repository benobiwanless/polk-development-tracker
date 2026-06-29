import json, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT/'config/sources.json').read_text())
CITIES = config['cities']
POSITIVE = [t.lower() for t in config['positive_terms']]
BLOCKED = [t.lower() for t in config['blocked_terms']]

CATEGORY_TERMS = {
    'Housing':['housing','apartment','apartments','subdivision','homes','townhomes'],
    'Restaurant':['restaurant','dining','cafe','barbecue','coffee'],
    'Retail':['retail','store','shopping','grocery','publix'],
    'Hotel':['hotel','inn','suites','resort'],
    'Infrastructure':['road','interchange','infrastructure','utility','utilities','trail'],
    'Commercial':['commercial','warehouse','office','industrial'],
    'Community':['park','library','school','recreation']
}

def category_for(text):
    t=text.lower()
    for cat, terms in CATEGORY_TERMS.items():
        if any(x in t for x in terms): return cat
    return 'Development'

def status_for(text):
    t=text.lower()
    if 'grand opening' in t or 'now open' in t: return 'Grand Opening'
    if 'under construction' in t or 'construction' in t: return 'Under Construction'
    if 'approved' in t or 'permit' in t: return 'Approved'
    if 'coming soon' in t or 'planned' in t: return 'Coming Soon'
    return 'Update'

def fetch_google_news(query):
    url='https://news.google.com/rss/search?q='+urllib.parse.quote(query)+'&hl=en-US&gl=US&ceid=US:en'
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()

def main():
    items=[]; seen=set()
    terms=' OR '.join([f'"{c} FL"' for c in CITIES if c!='Unincorporated'])
    query=f'("Polk County" OR {terms}) (development OR construction OR restaurant OR retail OR housing OR hotel OR permit)'
    try:
        xml=fetch_google_news(query)
        root=ET.fromstring(xml)
        for item in root.findall('.//item')[:40]:
            title=item.findtext('title','').strip(); link=item.findtext('link','').strip(); pub=item.findtext('pubDate','').strip(); desc=item.findtext('description','').strip()
            text=(title+' '+desc).lower()
            if any(b in text for b in BLOCKED): continue
            if not any(p in text for p in POSITIVE): continue
            city=next((c for c in CITIES if c.lower() in text), 'Polk County')
            key=(title.lower(), link)
            if key in seen: continue
            seen.add(key)
            items.append({'title':title,'city':city,'category':category_for(text),'status':status_for(text),'date':pub[:16] or datetime.now().strftime('%b %d, %Y'),'summary':desc[:220].replace('<b>','').replace('</b>',''),'image':'','link':link,'featured':len(items)==0})
    except Exception as e:
        print('RSS fetch failed:', e)
    if not items:
        old=json.loads((ROOT/'data/news.json').read_text())
        items=old.get('items',[])
    out={'last_updated':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'items':items[:24]}
    (ROOT/'data/news.json').write_text(json.dumps(out,indent=2), encoding='utf-8')
if __name__=='__main__': main()
