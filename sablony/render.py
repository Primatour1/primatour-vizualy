#!/usr/bin/env python3
"""Vyplní šablónu (sablony/*.html) hodnotami z JSON a vyrenderuje PNG 1080×1350.
Použitie:  python sablony/render.py sablony/ticha_ponuka.html data.json vystup.png
Vyžaduje Playwright + Chromium (v cloude Claude je predinštalovaný)."""
import json, sys, asyncio, html as H
from playwright.async_api import async_playwright

async def main(sablona, data, vystup):
    t = open(sablona, encoding='utf-8').read()
    d = json.load(open(data, encoding='utf-8'))
    for k, v in d.items():
        # hodnoty končiace _HTML sa vkladajú ako HTML, ostatné sa escapujú
        if k.endswith('_HTML'):
            t = t.replace('{{%s}}' % k[:-5], str(v))
        else:
            t = t.replace('{{%s}}' % k, H.escape(str(v)).replace('\n', '<br>'))
    tmp = vystup + '.html'
    open(tmp, 'w', encoding='utf-8').write(t)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        await pg.goto('file://' + __import__('os').path.abspath(tmp))
        await pg.wait_for_timeout(1500)   # písma z Google Fonts
        await pg.screenshot(path=vystup, full_page=False)
        await b.close()
    print('OK', vystup)

asyncio.run(main(*sys.argv[1:4]))
