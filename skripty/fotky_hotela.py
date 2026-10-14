#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRIMATOUR — fotky hotelov z primatour.sk pre príspevky na sociálne siete
=======================================================================

Číta požiadavky z priečinka  poziadavky/  (jeden textový súbor = jedna
požiadavka, v ňom názov hotela; nepovinne za zvislou čiarou počet fotiek,
napr.  Alexia Resort | 4 ).

Pre každý hotel:
  1. nájde ho vo vyhľadávači webu  (/data/fulltext/nt?term=…&group=hotel)
  2. otvorí stránku hotela  (/dovolenka/x/x/x/<id>a — web presmeruje na správnu adresu)
  3. stiahne fotky z galérie (CDN Cesys, i.ccdn.sk) a uloží ich ako JPG
     do  hotely/<id>-<slug>/01.jpg, 02.jpg …  + info.json s názvom a zdrojom
  4. požiadavku presunie do  poziadavky/hotovo/  s výsledkom

Fotky sú od cestovných kancelárií, dodané cez Cesys pre web primatour.sk.
Spúšťa sa automaticky (GitHub Actions) po každom pridaní požiadavky.
"""
import io, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request
from PIL import Image

WEB = 'https://www.primatour.sk'
UA = {'User-Agent': 'Mozilla/5.0 (Primatour fotky pre socialne siete; primatour@primatour.sk)'}
TU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POZ = os.path.join(TU, 'poziadavky')
HOTOVO = os.path.join(POZ, 'hotovo')
HOTELY = os.path.join(TU, 'hotely')
MAX_FOTIEK = 6
MAX_SIRKA = 1600


def stiahni(url, binarne=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
        return data if binarne else data.decode('utf-8', 'replace')


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60]


def najdi_hotel(nazov):
    url = WEB + '/data/fulltext/nt?' + urllib.parse.urlencode({'term': nazov, 'group': 'hotel'})
    data = json.loads(stiahni(url))
    kandidati = []
    for skupina in data.get('result', []):
        if skupina.get('type') == 'hotel':
            kandidati.extend(skupina.get('data', []))
    if not kandidati:
        return None
    # uprednostni presný názov, inak prvý výsledok
    n = nazov.strip().lower()
    for k in kandidati:
        if (k.get('name') or '').strip().lower() == n:
            return k
    return kandidati[0]


def fotky_zo_stranky(hotel_id):
    html = stiahni('%s/dovolenka/x/x/x/%sa' % (WEB, hotel_id))
    von = []
    for m in re.finditer(r'https?://i\.ccdn\.sk/acm/([0-9a-f]{32})\.(?:webp|jpg|jpeg|png)', html):
        url = 'https://i.ccdn.sk/acm/%s.webp' % m.group(1)
        if url not in von:
            von.append(url)
    return von


def uloz_jpg(data, ciel):
    im = Image.open(io.BytesIO(data))
    if im.mode not in ('RGB',):
        im = im.convert('RGB')
    if im.width > MAX_SIRKA:
        im = im.resize((MAX_SIRKA, round(im.height * MAX_SIRKA / im.width)))
    im.save(ciel, 'JPEG', quality=88, optimize=True)
    return im.size


def spracuj(subor):
    with open(subor, encoding='utf-8') as f:
        riadky = [r.strip() for r in f if r.strip()]
    if not riadky:
        return {'chyba': 'prázdna požiadavka'}
    casti = [c.strip() for c in riadky[0].split('|')]
    nazov = casti[0]
    pocet = int(casti[1]) if len(casti) > 1 and casti[1].isdigit() else MAX_FOTIEK
    pocet = max(1, min(pocet, 10))

    hotel = najdi_hotel(nazov)
    if not hotel:
        return {'hotel': nazov, 'chyba': 'web hotel nenašiel'}
    hid = hotel['id']
    priecinok = os.path.join(HOTELY, '%s-%s' % (hid, slug(hotel['name'])))
    os.makedirs(priecinok, exist_ok=True)
    zdroje = fotky_zo_stranky(hid)
    ulozene = []
    for i, url in enumerate(zdroje[:pocet], 1):
        ciel = os.path.join(priecinok, '%02d.jpg' % i)
        try:
            w, h = uloz_jpg(stiahni(url, binarne=True), ciel)
            ulozene.append({'subor': os.path.basename(ciel), 'zdroj': url, 'rozmer': [w, h]})
            time.sleep(0.5)
        except Exception as e:
            ulozene.append({'subor': None, 'zdroj': url, 'chyba': str(e)})
    info = {
        'id': hid, 'nazov': hotel['name'], 'hviezdy': hotel.get('rating'),
        'lokalita': hotel.get('tree'), 'stranka': '%s/dovolenka/x/x/x/%sa' % (WEB, hid),
        'poziadavka': nazov, 'fotky': ulozene,
        'zdroj_fotiek': 'cestovné kancelárie cez Cesys / primatour.sk',
        'priecinok': os.path.relpath(priecinok, TU).replace(os.sep, '/'),
    }
    with open(os.path.join(priecinok, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    return info


def main():
    os.makedirs(HOTOVO, exist_ok=True)
    subory = sorted(f for f in os.listdir(POZ) if f.endswith('.txt'))
    if not subory:
        print('Žiadne požiadavky.')
        return
    for s in subory:
        cesta = os.path.join(POZ, s)
        try:
            vysledok = spracuj(cesta)
        except Exception as e:
            vysledok = {'chyba': 'neočakávaná chyba: %s' % e}
        print(s, '->', json.dumps({k: v for k, v in vysledok.items() if k != 'fotky'}, ensure_ascii=False),
              '| fotiek:', len([f for f in vysledok.get('fotky', []) if f.get('subor')]))
        with open(os.path.join(HOTOVO, s.replace('.txt', '.json')), 'w', encoding='utf-8') as f:
            json.dump(vysledok, f, ensure_ascii=False, indent=1)
        os.remove(cesta)


if __name__ == '__main__':
    main()
