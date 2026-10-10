import json, re
LANGS = {'en': 'spamdex_cards.json', 'fr': 'spamdex_cards_fr.json'}
D = {k: json.load(open(v, encoding='utf-8')) for k, v in LANGS.items()}
en = D['en']
kw = {l: {k['id']: k for k in D[l]['keywords']} for l in D}
byid = {l: {c['id']: c for c in D[l]['cards']} for l in D}

def refs(it):
    return [m for m in re.findall(r'\{kw:([^}]+)\}', it.get('effectRichRaw', it.get('effectRich', '')) or '')]

cards = []
def kwids(l, x):
    ids = []
    for it in x['abilities'] + x['talents']:
        for r in refs(it):
            if r in kw[l] and r not in ids: ids.append(r)
    for s in x['skills']:
        for k in D[l]['keywords']:
            if k['title'] == s['name'] and k['id'] not in ids: ids.append(k['id'])
    seen, out = set(), []
    for i in ids:
        if kw[l][i]['title'] not in seen: seen.add(kw[l][i]['title']); out.append(i)
    return out
GR = re.compile(r'\{kw:[^}]+\}([^{]*)\{/kw\}')
GR2 = re.compile(r'\{kw:([^}]+)\}([^{]*)\{/kw\}')
def pick(rich, fallback):
    for kid, txt in GR2.findall(rich):
        if kid.startswith(('tox.', 'talent.')) and txt.strip(): return txt.strip()
    return fallback
slugk = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
kwid_en = {k['title']: k['id'] for k in en['keywords']}
def desc(l, title_en):
    i = kwid_en.get(title_en)
    return kw[l][i]['description'] if i and i in kw[l] else ''
toxnames, toxcount, toxicon, toxdesc = {}, {}, {}, {}
BOOST = {
 'AddAllPlayerAttack': 'elemental', 'AddAllPlayerAttackRandomTeam': 'elemental', 'AddAllPlayerAttackCountActivation1': 'elemental',
 'AddAllPlayerAttackWithCardType': 'elemental', 'AddSAttackMulticolor': 'elemental', 'StealElement': 'elemental',
 'AddCardResistance': 'resist', 'AddOppCardResistance': 'resist', 'AddSCoeurAcier': 'resist',
 'AddCardCriticChance': 'crit', 'AddAllPlayerCritick': 'crit', 'AddOppCardCriticChance': 'crit',
 'AddCardCriticRatio': 'critpower', 'AddOppCardCriticRatio': 'critpower',
 'AddOppCardMiss': 'accuracy', 'AddAllPlayerMiss': 'accuracy', 'AddCardMiss': 'accuracy',
 'AddAbilityBaseDamage': 'power', 'AddCardBaseDamage': 'power', 'AddOppCardBaseDamage': 'power',
 'AddCardHPMax': 'maxhp', 'AddOppHPMax': 'maxhp', 'AddAllPlayerHPMax': 'maxhp', 'MultiplyAllHP_x2': 'maxhp',
 'AddSRoulette': 'echo', 'AddSpamton': 'spamton', 'AddSpamtonGenerationCaster': 'spamton', 'AddLuck': 'luck'}
SIX = ['fire', 'water', 'earth', 'nature', 'light', 'shadow']
def boosts(card, item):
    out = {}
    for a in item['actions']:
        t = BOOST.get(a['effect'])
        if not t: continue
        els = out.setdefault(t, [])
        e = a.get('element')
        if a['effect'] == 'AddAllPlayerAttackWithCardType': e = card['element']
        for x in (SIX if a['effect'] == 'AddSAttackMulticolor' else [e] if e else []):
            if x not in els: els.append(x)
    return [dict(t=t, e=e) for t, e in out.items()]
def healels(ab):
    out = []
    for a in ab['actions']:
        if a['kind'] == 'heal' and a.get('element') and a['element'] not in out: out.append(a['element'])
    return out
def dmgels(card, ab):
    out = []
    for a in ab['actions']:
        if a['kind'] != 'damage': continue
        e = a.get('element') or (card['element'] if a['effect'] == 'DamageWithCardElement' else None)
        if e and e not in out: out.append(e)
    return out
for c in en['cards']:
    a = c['artwork'] or {}; art = a.get('artist') or {}
    t = {}
    for l in D:
        x = byid[l][c['id']]; lo = x.get('lore') if isinstance(x.get('lore'), dict) else {}
        t[l] = dict(
            name=x['name'], lore=lo.get('text') or '',
            loreMeta=' · '.join(v for v in (lo.get('species'), lo.get('region'), lo.get('era')) if v),
            abilities=[dict(name=y['name'], effect=y['effect']) for y in x['abilities']],
            talents=[dict(name=y['name'], effect=y['effect']) for y in x['talents']],
            skills=[dict(name=y['name'], effect=y['effect'], k=slugk(c['skills'][j]['name'])) for j, y in enumerate(x['skills'])],
            keywords=[dict(title=kw[l][i]['title'], description=kw[l][i]['description']) for i in kwids(l, x)])
    tox = [dict(k=slugk(s['name']), via=False) for s in c['skills']]
    have = {x['k'] for x in tox}
    grants = []
    for i, tl in enumerate(c['talents']):
        if not tl['grantsSkill']: grants.append(None); continue
        nen = pick(tl['effectRich'], tl['name']); k = slugk(nen); grants.append(k)
        for l in D:
            xt = byid[l][c['id']]['talents'][i]; toxnames.setdefault(k, {})[l] = pick(xt['effectRich'], xt['name']); toxdesc.setdefault(k, {}).setdefault(l, desc(l, nen))
        if k not in have: have.add(k); tox.append(dict(k=k, via=True))
    for j, s in enumerate(c['skills']):
        for l in D:
            toxnames.setdefault(slugk(s['name']), {})[l] = byid[l][c['id']]['skills'][j]['name']
            toxdesc.setdefault(slugk(s['name']), {})[l] = byid[l][c['id']]['skills'][j]['effect']
        if s.get('icon'): toxicon.setdefault(slugk(s['name']), s['icon'])
    for x in tox: toxcount[x['k']] = toxcount.get(x['k'], 0) + 1
    cards.append(dict(tox=tox, number=c['number'], slug=c['slug'], element=c['element'], rarity=c['rarity'], spamton=c['spamton'], hp=c['hp'],
        res=c['resistances'], art=a.get('small'), artist=art.get('name'), artistLink=art.get('link'),
        ab=[dict(cd=y['cooldown'], precision=y['precision'], critChance=y['critChance'], critMultiplier=y['critMultiplier'],
                 echo=y['cooldownResetChance'], uses=y['uses'], dmg=dmgels(c, y), heal=healels(y), boost=boosts(c, y)) for y in c['abilities']],
        tal=[dict(slot=y['slot'], elements=y.get('elements') or [], boost=boosts(c, y), grants=grants[i]) for i, y in enumerate(c['talents'])], t=t))

def named(kind):
    out = []
    for item in en[kind]:
        o = dict(item); o['name'] = {l: next(i['name'] for i in D[l][kind] if i['id'] == item['id']) for l in D}; out.append(o)
    return out
toxes = sorted([dict(k=k, name=v, count=toxcount[k], icon=toxicon.get(k), desc=toxdesc.get(k, {})) for k, v in toxnames.items()], key=lambda x: x['name']['en'].lower())
payload = dict(toxes=toxes, version=en['version'], elements=named('elements'), rarities=named('rarities'), cards=cards)
js = json.dumps(payload, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
# ---------- single-file packaging: embed card art, UI icons and fonts ----------
import base64, io, os, urllib.request
from PIL import Image
def webp_b64(path, max_side, q):
    im = Image.open(path); im.load()
    if im.mode not in ('RGB', 'RGBA'): im = im.convert('RGBA')
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=q, method=6)
    return base64.b64encode(buf.getvalue()).decode()
assets = {'art': {}, 'ui': {}}
for c in en['cards']:
    p = 'spamdex_images/%s.webp' % c['slug']
    if os.path.exists(p): assets['art'][c['slug']] = webp_b64(p, 512, 72)
uipaths = {e['icon'] for e in en['elements']} | {r['gem'] for r in en['rarities']} | {t['icon'] for t in toxes if t.get('icon')} | {'img/frame/spamton.webp'}
for p in uipaths:
    lp = 'spamdex_images/ui/' + p[4:]
    if os.path.exists(lp): assets['ui'][p] = webp_b64(lp, 72 if '/skills/' in p else 112, 82)
missing_art = [c['slug'] for c in en['cards'] if c['slug'] not in assets['art']]
FONT_CSS = 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&family=Figtree:wght@400..700&display=swap'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
def fonts_css():
    cache = 'spamdex_fonts'; os.makedirs(cache, exist_ok=True)
    cssp = os.path.join(cache, 'fonts.css')
    if not os.path.exists(cssp):
        open(cssp, 'w', encoding='utf-8').write(urllib.request.urlopen(urllib.request.Request(FONT_CSS, headers={'User-Agent': UA}), timeout=30).read().decode())
    css = open(cssp, encoding='utf-8').read(); out = []
    for subset, rule in re.findall(r'/\* ([\w-]+) \*/\s*(@font-face\s*\{[^}]*\})', css):
        if subset != 'latin': continue
        url = re.search(r'url\((https://[^)]+)\)', rule).group(1)
        fn = os.path.join(cache, re.sub(r'[^A-Za-z0-9._-]', '_', url.split('/')[-1]))
        if not os.path.exists(fn): open(fn, 'wb').write(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30).read())
        out.append(rule.replace(url, 'data:font/woff2;base64,' + base64.b64encode(open(fn, 'rb').read()).decode()))
    return '\n'.join(out)
fonts = fonts_css()
html = open('template.html', encoding='utf-8').read().replace('__DATA__', js)
html = html.replace('/*__FONTS__*/', fonts).replace('__ASSETS__', json.dumps(assets))
print('embedded: %d art, %d icons, %d font faces, missing art: %s' % (len(assets['art']), len(assets['ui']), fonts.count('@font-face'), missing_art))
open('index.html', 'w', encoding='utf-8').write(html)
print(len(html), 'bytes;', len(cards), 'cards;', sum(1 for c in cards if len(c['t']['fr']['keywords']) != len(c['t']['en']['keywords'])), 'keyword count mismatches')
print(payload['elements'][1]['name'], payload['rarities'][2]['name'])
