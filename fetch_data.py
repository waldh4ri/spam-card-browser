"""Download the public SPAMDEX data used by build_browser.py.

Fetches the latest card files (English and French), every card illustration
and the UI icons (elements, rarity gems, Tox, Spamton coin) into this folder.

The data is published by Ticroco at https://spamgame.com/data/ under
https://spamgame.com/conditions-donnees-cartes (non-commercial fan projects,
credit each artist, state the project is unofficial). The file layout comes
from data/index.json. Re-runs are cheap: JSON is fetched with If-None-Match
and images (whose names carry a content hash) are never downloaded twice.
"""
import json, os, sys, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://spamgame.com/data/'  # canonical host named in the data terms
UA = {'User-Agent': 'spam-card-browser/1.0 (non-commercial fan project; +https://github.com/waldh4ri/spam-card-browser)'}
SUPPORTED_SCHEMA = 1  # the terms say the schema number changes when the format does
LANGS = {'en': 'spamdex_cards.json', 'fr': 'spamdex_cards_fr.json'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def get_json_cached(url, out):
    """Fetch a JSON file, reusing the local copy when the server says it is unchanged."""
    headers = dict(UA)
    etag_file = out + '.etag'
    if os.path.exists(out) and os.path.exists(etag_file):
        headers['If-None-Match'] = open(etag_file).read().strip()
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60)
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return json.load(open(out, encoding='utf-8'))
        raise
    body = resp.read()
    open(out, 'wb').write(body)
    if resp.headers.get('ETag'):
        open(etag_file, 'w').write(resp.headers['ETag'])
    return json.loads(body)


def need_schema(doc, name):
    if doc.get('schema') != SUPPORTED_SCHEMA:
        sys.exit('%s has schema %r but this tool supports schema %d. The SPAMDEX format changed: '
                 'check https://spamgame.com/conditions-donnees-cartes and update build_browser.py.'
                 % (name, doc.get('schema'), SUPPORTED_SCHEMA))


def save(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    open(path, 'wb').write(get(url))


index = json.loads(get(BASE + 'index.json'))
need_schema(index, 'index.json')
version = index['latest']
print('SPAMDEX version', version)
for lang, out in LANGS.items():
    doc = get_json_cached(BASE + index['cards'].format(version=version, language=lang), out)
    need_schema(doc, out)
    print('ready', out)

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

with ThreadPoolExecutor(4) as pool:
    list(pool.map(lambda j: save(*j), jobs))
print('downloaded', len(jobs), 'images into spamdex_images/')
