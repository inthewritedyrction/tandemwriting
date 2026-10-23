"""Read the printed PDF and write out/toc_pages.json: the page each part opens on.

Every part starts a new page, so the title is near the top of that page's text.
"""
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / 'out' / 'volume_one.html').read_text()
main = html.split('<main>', 1)[1]
titles = [(pid, re.sub('<.*?>', '', re.sub(r'<span class="kicker">.*?</span>', '', t)).strip())
          for pid, t in re.findall(r'<h2 id="(p\d+)">(.*?)</h2>', main)]
reader = PdfReader(str(ROOT / 'dist' / 'TKC_Volume_One_World_Dossier.pdf'))
texts = [re.sub(r'\s+', ' ', p.extract_text() or '') for p in reader.pages]
pages, start = {}, 2
for pid, title in titles:
    key = re.sub(r'\s+', ' ', title)[:30]
    for i in range(start, len(texts)):
        if key in texts[i][:400]:
            pages[pid] = i + 1
            start = i + 1
            break
(ROOT / 'out' / 'toc_pages.json').write_text(json.dumps(pages))
print(pages, len(pages), 'of', len(titles))
