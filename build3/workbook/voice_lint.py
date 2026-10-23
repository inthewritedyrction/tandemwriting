"""Voice check for the workbook's printed text.

Reads out/workbook{_vN}.html (set TKC_VOL) and reports, by folio, every printed sentence that breaks
the house rules: em dashes, semicolons, sentences opening with That / Not / Then, the
"isn't X. It's Y." cadence, and labels that don't open their sentence.
Usage: TKC_VOL=2 python3 workbook/voice_lint.py
"""
import html
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOL = os.environ.get('TKC_VOL', '1')
SFX = '' if VOL == '1' else '_v' + VOL
LABELS = ['INTERPRETATION', 'CONTESTED', 'INFERENCE', 'POSSIBLE', 'OPEN QUESTION', 'CONFLICT', 'SUPERSEDED', 'DECIDED']


def pages():
    s = (ROOT / 'out' / f'workbook{SFX}.html').read_text()
    for n, body in enumerate(re.findall(r'<section class="page[^"]*">(.*?)</section>', s, re.S), start=1):
        body = re.sub(r'<div class="(rh|folio|margin)">.*?</div>', ' ', body, flags=re.S)
        text = re.sub(r'<(br|/p|/div|/li|/td|/th)[^>]*>', '\n', body)
        text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
        yield n, [re.sub(r'\s+', ' ', t).strip() for t in text.split('\n') if t.strip()]


def check():
    problems = 0
    for n, chunks in pages():
        for c in chunks:
            hits = []
            if '—' in c:
                hits.append('em dash')
            if ';' in c:
                hits.append('semicolon')
            for sent in re.split(r'(?<=[.?!])\s+', c):
                s = sent.lstrip('"“(‘\'')
                if re.match(r'(That|Not|Then)\b', s):
                    hits.append(f'opens with {s.split()[0]}')
            if re.search(r"\b(isn't|is not|wasn't|was not)\b[^.]*\.\s+(It's|It is|It was)\b", c):
                hits.append('not-X-it-is-Y cadence')
            # the renderer turns a label into a pink tag only where it opens a sentence,
            # so a "LABEL:" still in the printed text is one that didn't
            for lab in LABELS:
                if re.search(rf'\b{lab}:', c):
                    hits.append(f'{lab} mid-sentence')
            if hits:
                problems += 1
                print(f'{n:03d}  {", ".join(sorted(set(hits)))}  ::  {c[:150]}')
    print(f'{problems} voice problems')


if __name__ == '__main__':
    check()
