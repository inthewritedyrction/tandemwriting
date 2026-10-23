"""Make the printed workbook easy on printers.

Recompresses and linearizes the full PDF in place, and splits it into
section files under dist/print/ so each print job stays under ~150 pages.
Usage: python3 tools/print_ready.py [1|2]
"""
import json, sys
from pathlib import Path
import pikepdf

ROOT = Path(__file__).resolve().parent.parent
VOL = sys.argv[1] if len(sys.argv) > 1 else '1'
SFX = '' if VOL == '1' else '_v' + VOL
NAME = {'1': 'TKC_Volume_One_Workbook', '2': 'TKC_Volume_Two_Workbook', '3': 'TKC_Reading_Plan'}[VOL]
SRC = ROOT / 'dist' / f'{NAME}.pdf'

# section starts, by page anchor; each runs to the page before the next
SPLITS = {
    '1': [('01_Front_and_Bible_101', None), ('02_Sixty-Six_Books', 'b66'), ('03_Focused_Studies', 'f1'),
          ('04_Deep_Dives', 'd1'), ('05_Parts_II-IV', 'part2'), ('06_Parts_V-VI', 'part5'),
          ('07_Parts_VII-VIII_and_Back', 'part7')],
    '2': [('01_Front_and_Part_I', None), ('02_Part_II', 'part2'), ('03_Part_III', 'part3'),
          ('04_Part_IV', 'part4'), ('05_Part_V_and_Back', 'part5')],
}

def save(pdf, path):
    pdf.remove_unreferenced_resources()
    pdf.save(path, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate,
             recompress_flate=True, linearize=True)

with pikepdf.open(SRC, allow_overwriting_input=True) as pdf:
    n = len(pdf.pages)
    out = ROOT / 'dist' / 'print'
    out.mkdir(exist_ok=True)
    anchors = json.loads((ROOT / 'out' / f'anchors{SFX}.json').read_text())
    plan = SPLITS.get(VOL, [])
    starts = [1 if a is None else anchors[a] for _, a in plan]
    for i, (label, _) in enumerate(plan):
        a, b = starts[i], (starts[i + 1] - 1 if i + 1 < len(starts) else n)
        part = pikepdf.new()
        part.pages.extend(pdf.pages[a - 1:b])
        save(part, out / f'{NAME}_{label}_p{a:03d}-{b:03d}.pdf')
        print(f'{label}: pages {a}-{b} ({b - a + 1})')
    save(pdf, SRC)
print('done', SRC.stat().st_size // 1024, 'KB')
