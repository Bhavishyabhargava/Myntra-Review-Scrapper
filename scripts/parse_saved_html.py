from bs4 import BeautifulSoup as bs
import json
from urllib.parse import urlparse

with open('scripts/search_shoes.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = bs(html, 'html.parser')
scripts = soup.find_all('script', {'type':'application/ld+json'})
print('SCRIPTS_FOUND', len(scripts))
for i, s in enumerate(scripts[:5]):
    txt = s.string
    print('SCRIPT', i, 'len', len(txt) if txt else None)
    try:
        payload = json.loads(txt)
    except Exception as e:
        print('JSON ERR', e)
        continue
    if isinstance(payload, dict) and payload.get('@type')=='ItemList':
        print('FOUND ITEMLIST')
        for item in payload.get('itemListElement', [])[:10]:
            print('ITEM URL', item.get('url'))

