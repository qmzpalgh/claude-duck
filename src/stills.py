"""Render key stills from shots into a contact sheet for inspection.
usage: python stills.py act1 a01_pov:2.0 a08_roadside:5 ...  (or 'all' for every shot at 3 times)"""
import importlib, sys, os
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "stills")
import cairo
from engine import W, H
from PIL import Image
mod = importlib.import_module(sys.argv[1])
shots = {s.name: s for s in mod.build()}
req = sys.argv[2:]
if not req or req == ['all']:
    req = []
    for s in mod.build():
        for f in (0.2, 0.55, 0.9):
            req.append(f'{s.name}:{s.dur*f:.2f}')
os.makedirs(OUT, exist_ok=True)
ims = []
for r in req:
    n, t = r.split(':')
    p = os.path.join(OUT, f'{n}_{t}.png')
    shots[n].still(float(t), p)
    ims.append((r, Image.open(p).convert('RGB')))
cols = 3 if len(ims) > 4 else 2
cw, ch = 640, 360
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * (ch + 20)), 'white')
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
for i, (r, im) in enumerate(ims):
    x, y = (i % cols) * cw, (i // cols) * (ch + 20)
    sheet.paste(im.resize((cw, ch)), (x, y + 20))
    d.text((x + 4, y + 4), r, fill='red')
sheet.save(os.path.join(OUT, 'sheet.jpg'), quality=85)
print('wrote', os.path.join(OUT, 'sheet.jpg'))
