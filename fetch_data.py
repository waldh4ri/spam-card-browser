"""Download the public SPAMDEX data used by build_browser.py.

Fetches the latest card files (English and French), every card illustration
and the UI icons (elements, rarity gems, Tox, Spamton coin) into this folder.
"""
import json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://www.spamgame.com/data/'
UA = {'User-Agent': 'Mozilla/5.0 (spam-card-browser fan tool)'}
LANGS = {'en': 'spamdex_cards.json', 'fr': 'spamdex_cards_fr.json'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def save(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    open(path, 'wb').write(get(url))


index = json.loads(get(BASE + 'index.json'))
version = index['latest']
print('SPAMDEX version', version)
for lang, out in LANGS.items():
    open(out, 'wb').write(get(BASE + index['cards'].format(version=version, language=lang)))
    print('saved', out)

data = json.load(open(LANGS['en'], encoding='utf-8'))
jobs = []
for c in data['cards']:
    art = (c.get('artwork') or {}).get('small')
    if art:
        jobs.append((BASE + art, os.path.join('spamdex_images', c['slug'] + '.webp')))
ui = {e['icon'] for e in data['elements']} | {r['gem'] for r in data['rarities']} | {'img/frame/spamton.webp'}
ui |= {s['icon'] for c in data['cards'] for s in c['skills'] if s.get('icon')}
for p in ui:
    jobs.append((BASE + p, os.path.join('spamdex_images', 'ui', p[len('img/'):])))

with ThreadPoolExecutor(6) as pool:
    list(pool.map(lambda j: save(*j), jobs))
print('downloaded', len(jobs), 'images into spamdex_images/')
