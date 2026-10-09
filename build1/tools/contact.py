#!/usr/bin/env python3
"""Contact sheets of rendered pages for visual QA: tools/contact.py <png_dir> <out_dir> [per_sheet]"""
import sys, glob, os
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
per = int(sys.argv[3]) if len(sys.argv) > 3 else 12
files = sorted(glob.glob(os.path.join(src, '*.png')))
os.makedirs(out, exist_ok=True)
cols = 4
for s in range(0, len(files), per):
    ims = [Image.open(f) for f in files[s:s + per]]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 26) + 10), (200, 200, 200))
    d = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = 10 + (k % cols) * (w + 10), 10 + (k // cols) * (h + 26)
        sheet.paste(im, (x, y + 16))
        d.text((x, y), os.path.basename(files[s + k]), fill=(0, 0, 0))
    sheet.save(os.path.join(out, f'sheet_{s // per + 1:02d}.png'))
print('sheets:', (len(files) + per - 1) // per)
