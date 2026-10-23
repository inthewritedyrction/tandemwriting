"""Assemble TKC Volume One from the rev 15 doc export and the four new sections.

Usage: python3 tools/assemble.py   (run from build3/)
Writes volume_one/TKC_Volume_One_World_Dossier.md
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V1 = ROOT / 'volume_one'


def must_replace(text, old, new, count=1):
    assert old in text, f'anchor not found: {old[:70]!r}'
    return text.replace(old, new, count)


# ---------- the doc export, cleaned ----------
doc = (V1 / 'from_doc' / 'rev15.md').read_text()
doc = re.sub(r'\*\*\*([^*\s][^*]*?)\*\*\*', r'*\1*', doc)          # bold-italic inside bold lead-ins
doc = re.sub(r'(\d)– (\d)', r'\1–\2', doc)                          # ranges split at a line end
doc = re.sub(r'(\w)- (\w)', lambda m: m.group(0) if m.group(2) in 'aeiou' and False else m.group(1) + '-' + m.group(2), doc) \
    if False else doc
doc = re.sub(r'\| (\[DESIGN NOTE:[^|]*\]) \|\n\| --- \|', r'\1', doc)  # a note boxed as a one-cell table

# split into top-level chunks on "## "
parts = re.split(r'(?m)^(?=## )', doc)
head = parts[0]
chunks = {}
for p in parts[1:]:
    title = p.split('\n', 1)[0][3:].strip()
    chunks[title] = p


def chunk(prefix):
    for k, v in chunks.items():
        if k.startswith(prefix):
            return v
    raise KeyError(prefix)


intro = chunk('How this volume works')
scripture_intro = chunk('The scripture parts')
part_i = chunk('Part I. ')
part_ii = chunk('Part II. ')
world = [chunk(f'Part {n}.') for n in ('VI', 'VII', 'VIII', 'IX', 'X', 'XI')]

# ---------- front matter ----------
head = '# TKC Volume One · The World Dossier\n\nThy Kingdom Come · Dany · October 2026\n'

intro = must_replace(intro,
    "The world parts (VI through XI) come first in this doc because you need the whole world in hand before you build chapters. They're written from your source files, your Final Rulings and the rulings you made in the calibration doc. Parts I through V, the scripture research, will be rewritten from the old Companion next and slot in ahead of them when the volume is assembled.",
    "Parts I through V cover the scripture the Empire inherited: what the Bible is, the books, the people in them, Jesus and the prayer the novel is named for, and how Christianity has been used by power. Parts VI through XI cover the world itself: the Fall, the Empire's institutions, its doctrine, its women and households, the twelve Dominions and the Trials. The world parts are written from your source files, your Final Rulings and the rulings you made in the calibration doc. The scripture parts are rebuilt from the old Companion's research and checked again. A canon register at the back collects every conflict, superseded fact and open question in one place.")
intro = must_replace(intro,
    "Every part closes with working questions, and each one gets real room on the page. Bracketed design notes mark places where a visual would carry the information better than prose. Nothing here is designed yet. The doc exports to Word or PDF from its menu if you want a plain printed copy before the designed version exists.",
    "Every part closes with working questions and a blank page to work on. Framed spaces mark where portraits, maps and diagrams go, so you can paste or draw them in.")

scripture_intro = must_replace(scripture_intro, " When the volume is assembled they go ahead of the world parts.", "")
scripture_intro = scripture_intro.replace('## The scripture parts: how Parts I–V work', '## How the scripture parts work')

# ---------- Part I: blank column on the fault-line table ----------
def add_blank_column(text, header_start, colname):
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if l.startswith(header_start):
            lines[i] = l + f' {colname} |'
            lines[i + 1] = lines[i + 1] + ' --- |'
            j = i + 2
            while j < len(lines) and lines[j].startswith('|'):
                lines[j] = lines[j] + '  |'
                j += 1
            return '\n'.join(lines)
    raise AssertionError(header_start)


part_i = add_blank_column(part_i, '| Fault line | What\'s actually in dispute |', 'Where the Empire lands')

# ---------- Part II: append II.3 ----------
ii3 = (V1 / 'II3_Deep_dives.md').read_text().strip()
part_ii = part_ii.rstrip() + '\n\n' + ii3 + '\n'


def promote(md):
    """Part III–V files use ### for the part and #### inside it."""
    md = re.sub(r'(?m)^### (Part [IVX]+\.)', r'## \1', md)
    md = re.sub(r'(?m)^#### ', '### ', md)
    return md.strip() + '\n'


part_iii = promote((V1 / 'III_People_of_the_Text.md').read_text())
part_iv = promote((V1 / 'IV_Jesus_Kingdom_Prayer.md').read_text())
part_v = promote((V1 / 'V_Christianity_and_Power.md').read_text())

# ---------- world parts: canon fixes ----------
vi, vii, viii, ix, x, xi = world

vi = must_replace(vi,
    "The real name of the city is the last thing she says to Eden before the Crownward. (Volume Two, Celeste.)",
    "The real name of the city is the last thing she says to Eden before the Crownward. She has no proof that Miriam is alive: the one letter Miriam sent, in 2094, was intercepted before it reached her, and she never knew it existed (FR 16). (Volume Two, Celeste.)")

viii = must_replace(viii, "(see Volume I, Part V on the 1807 Slave Bible)", "(see I.7 and Part V on the 1807 Slave Bible)")
viii = must_replace(viii, "The household code (Ephesians 5) entry is already drafted in the calibration doc.",
                    "The household code (Ephesians 5) is worked through in I.7.")

ix = must_replace(ix,
    "Two years without a pregnancy brings informal comments first and then Temple review (MEN, TL). (Volume Two, Leah.)",
    "Two years without a pregnancy brings informal comments first and then Temple review (MEN, TL). (Volume Two, Leah.)\n\n"
    "CONFLICT: The timeline makes Leah Eden's older sister (TL), and FR 5 calls Leah, Zion and Solomon \"the younger three.\" FR 11 and FR 14, where Leah watched Miriam pack and remembers a decision, read most naturally for an older sister. Not resolved here.")
ix = must_replace(ix,
    "When a husband abandons his Commonwife, she can be reassigned to another man's household. That's what happened to Miriam after Thomas left (FR 0).",
    "When a husband abandons his Commonwife, she can be reassigned to another man's household. That's what happened to Miriam after Thomas left (FR 0). Thomas left voluntarily in 2084, for another Dominion and another woman, and the record that he relocated is accurate (FR 3). Solomon was born in that later household, kept the Osei name, and is sixteen in 2104 (FR 0).\n\n"
    "SUPERSEDED: The timeline gives Solomon's age as thirteen. FR 0 keeps him at sixteen.\n\n"
    "SUPERSEDED: Any framing of Thomas's 2084 departure as an Empire removal (FR 3). INFERENCE: The timeline's line that Celeste \"has always believed otherwise\" can stand as her belief. FR 3 makes it mistaken.")
ix = must_replace(ix,
    "OPEN QUESTION: What is Home Instruction? Training for wives, a teaching role, or something else?",
    "OPEN QUESTION: What is Home Instruction? Training for wives, a teaching role, or something else?\n\n"
    "OPEN QUESTION: Bell's offer reads as if Leah sat an Assessment. The timeline has her Bound and under Temple review, so the offer has to date from before her Binding, or one of the two has to change.")

# households grid replaces its design note
ix = must_replace(ix,
    "[DESIGN NOTE: Side-by-side comparison of those four households: who's on the paper, who actually decides, what's assessed, and what's hidden.]",
    "| Household | Who's on the paper | Who actually decides | What's assessed | What's hidden |\n| --- | --- | --- | --- | --- |\n"
    "| Celeste's |  |  |  |  |\n| Leah's |  |  |  |  |\n| Hannah's |  |  |  |  |\n| An Anointed Court household |  |  |  |  |")

# ---------- design notes become plates, portraits and writing pages ----------
PLATES = [
    ('two-page horizontal timeline', '[PLATE: The timeline, 2025 to 2104 · the Fracture Years as one band, the four rulers along the bottom]'),
    ('family tree', '[PLATE: The House of Vane · Elias and his unknown first wife, the removed heir, Crest, Dorian and Lyris, Azrael and Judah, with the 2061 removal marked]'),
    ('Org chart', '[PLATE: How the Empire is run · the Crown, the Temple and the Broadcast across the top, the Governor-Prelates, the Registry, the Vowed and the Covenant Court beneath]'),
    ('Map needed here: the Covenant River', '[PLATE: Map of the Crownward · the Covenant River, both banks, the three bridges, the Palace, the Sanctum, the Citadel, Sovereign Boulevard, Covenant Row and the Registry]'),
    ('ladder diagram', '[PLATE: The designation ladder · how a woman moves between designations, and where each door locks]'),
    ('Map needed here: the Twelve Dominions', '[PLATE: Map of the Twelve Dominions · over the old state lines, with the seat cities and the Crownward marked]'),
]


def notes_to_plates(md):
    def repl(m):
        note = m.group(0)
        for key, plate in PLATES:
            if key in note:
                return plate
        return ''
    md = re.sub(r'\[DESIGN NOTE:[^\]]*\]', repl, md)
    return re.sub(r'\n{3,}', '\n\n', md)


PORTRAITS = {
    '### VI.5 Founder files': '[PORTRAITS: Elias Vane · First Elector and first Emperor, c. 1996–2061 | Sera Callum Vane · Elias\'s wife, the first Anointed Wife | Crest Vane · Emperor 2062–2085 | The removed heir · Elias\'s elder child, removed 2061]',
    'She came from Mountain Dominion (WR). (Volume Two, Lyris.)': '[PORTRAITS: Dorian Vane · Emperor since 2085, 59 | Lyris Vane · Empress, 58 | Judah Elijah Vane · Crown Heir, 25 | Azrael Vane · declared dead 2100]',
    'POSSIBLE: "Prelate Aurelia" is the working name until you choose one (FR, closing note).': '[PORTRAITS: The Prelate · head of the Crownward Vowed, 67, working name Prelate Aurelia | Senior Minister Bell · Aurelia Temple]',
    'Each one is a different answer to the same law.': '[PORTRAITS: Celeste Parish · 69, Unbound | Miriam Osei · Eden\'s mother, gone since 2090 | Thomas Osei · Eden\'s father, left 2084 | Leah Osei · Eden\'s sister, Commonwife | Eden Selah Osei · 21 | Zion Osei · Eden\'s brother | Solomon Osei · Eden\'s brother, 16]',
    'Hannah\'s "six Trials, twelve girls" counts her whole career across several Houses and posts (FR 26).': '[PORTRAITS: Hannah · House Mother, House Aurem | Naomi · Hannah\'s daughter | Abigail · Debate and Protocol Advisor | The House Coordinator · House Aurem | The stylist · House Aurem]',
    'Source: TR, Ruling (Calla\'s surname).': '[PORTRAITS: Eden Selah Osei · Aurem, 21 | Delphine Fontenot · Gulf, 22 | Maren Cole · Ardenne, 23 | Corinne Vale · Meridian, 22 | Calla Merritt · Vane, 21 | Nadia Orin · Irongate, 20 | Ruth Gideon · Heartland, 22 | Delia Cross · Red Earth, 24 | Vivienne Hale · Lone, 23 | Petra Solano · Mountain, 22 | Zara Voss · Sable, 21 | Sera Montoya · Pacific, 24]',
}


def add_portraits(md):
    for anchor, block in PORTRAITS.items():
        if anchor in md:
            if anchor.startswith('###'):
                md = md.replace(anchor, anchor + '\n\n' + block, 1)
            else:
                md = md.replace(anchor, anchor + '\n\n' + block, 1)
    return md


def add_writing_pages(md):
    """A writing page after every working-questions list."""
    out, lines, i = [], md.split('\n'), 0
    while i < len(lines):
        out.append(lines[i])
        if re.match(r'^#{3,4} Working questions', lines[i]):
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or re.match(r'^\d+\.', lines[j])):
                out.append(lines[j]); j += 1
            while out and not out[-1].strip():
                out.pop()
            out += ['', '[WRITING PAGE]', '']
            i = j
            continue
        i += 1
    return '\n'.join(out)


body_parts = [intro, scripture_intro, part_i, part_ii, part_iii, part_iv, part_v, vi, vii, viii, ix, x, xi]
body_parts = [add_writing_pages(add_portraits(notes_to_plates(p))) for p in body_parts]
volume = head + '\n' + '\n\n'.join(p.strip() for p in body_parts) + '\n'


# ---------- voice pass on the doc's own text (WR 20, no semicolons) ----------
VOICE = [
    ("NA28 and UBS5 for the texts; BDB and HALOT for Hebrew; the Anchor commentaries (Milgrom on Leviticus, Weinfeld on Deuteronomy); and Sanders and Ehrman on the New Testament",
     "NA28 and UBS5 for the texts, BDB and HALOT for Hebrew, the Anchor commentaries (Milgrom on Leviticus, Weinfeld on Deuteronomy), and Sanders and Ehrman on the New Testament"),
    ("genuinely variable in others. That corrects both", "genuinely variable in others. The scrolls correct both"),
    ("Hebrew or Greek words. That rule was a direct response", "Hebrew or Greek words. The rule was a direct response"),
    ("leaves out 5:21. That changes the passage's meaning", "leaves out 5:21. The omission changes the passage's meaning"),
    ("terms are disputed. That refusal is kept here", "terms are disputed. The refusal is kept here"),
    ("translating into Aramaic. Then comes a sealed covenant", "translating into Aramaic. A sealed covenant follows"),
    ("isn't held to their record. That sits against Exodus 20:5", "isn't held to their record. The chapter sits against Exodus 20:5"),
    ("Guilt isn't inherited. That's a direct problem", "Guilt isn't inherited, which is a direct problem"),
    ("the Temple and the Broadcast. That arrangement is the Triune Rule", "the Temple and the Broadcast, an arrangement called the Triune Rule"),
    ("never came back. That's what makes Imperial service", "never came back, which is why Imperial service"),
    ("look like opportunity to a common man", "looks like opportunity to a common man"),
    ("Doesn't know; the paperwork is filed anyway", "Doesn't know. The paperwork is filed anyway."),
    ("for an older sister. Not resolved here.", "for an older sister. This volume leaves it for you to decide."),
    ("another man's household. That's what happened to Miriam", "another man's household, which is what happened to Miriam"),
    ("because they mean them. That sincerity is", "because they mean them. Their sincerity is"),
    ("home Dominions. That shared history makes", "home Dominions. Their shared history makes"),
    ("An idea worth considering. Not canon.", "An idea worth considering, and not canon."),
    ("Not all disagreement is the same kind, and the most important skill", "Disagreement comes in different kinds, and the most important skill"),
]
for old, new in VOICE:
    if old in volume:
        volume = volume.replace(old, new)

# ---------- canon register ----------
LABELS = ('CONFLICT', 'SUPERSEDED', 'OPEN QUESTION', 'DECIDED')
reg = {k: [] for k in LABELS}
section = ''
for line in volume.split('\n'):
    m = re.match(r'^#{2,3} ((?:Part )?[IVX]+(?:\.\d+)?)\b', line)
    if m:
        section = m.group(1).replace('Part ', '')
    for lab in LABELS:
        for hit in re.finditer(lab + r': (.*)', line):
            sents = re.findall(r'.+?[.?]["”)]?(?=\s+[A-Z("]|\s*$)', hit.group(1))
            sentence = sents[0] if sents else hit.group(1)
            if len(sentence) < 30 and len(sents) > 1:
                sentence += ' ' + sents[1]
            reg[lab].append((section, sentence.strip()))

sweeps = [
    ('Thomas is abandonment, not removal', 'IX.4, Part III name table', 'Done'),
    ('Celeste no longer knows Miriam is alive', 'VI.4', 'Done in this volume. Celeste\'s and Eden\'s dossiers (Volume Two) still need it.'),
    ('Eden placed 2085, alone', 'Volume Two (nothing in this volume contradicts it)', 'Consistent here'),
    ('Twelve Dominions, one girl each', 'XI.5, XI.9', 'Done'),
    ('Petra\'s death costs the Trial nothing', 'XI.8', 'Done'),
]

register = ['## Canon register',
            'Everything this volume flags, collected so you can settle it in one sitting. Each line is the first sentence of the flag, with the section where it sits. The full flag is in the text.',
            '### The five sweeps from the Final Rulings',
            '\n'.join(['| Sweep | Where it lands here | Status |', '| --- | --- | --- |'] +
                      [f'| {a} | {b} | {c} |' for a, b, c in sweeps])]
titles = {'CONFLICT': 'Conflicts between your sources', 'SUPERSEDED': 'Superseded material',
          'OPEN QUESTION': 'Open questions', 'DECIDED': 'Decided for you'}
for lab in LABELS:
    if not reg[lab]:
        continue
    rows, seen = ['| Section | The flag |', '| --- | --- |'], set()
    for sec, s in reg[lab]:
        if (sec, s) in seen:
            continue
        seen.add((sec, s))
        rows.append(f'| {sec} | {s.replace("|", "/")} |')
    register += [f'### {titles[lab]}', '\n'.join(rows)]
register += ['[WRITING PAGE]']
volume += '\n' + '\n\n'.join(register) + '\n'

(V1 / 'TKC_Volume_One_World_Dossier.md').write_text(volume)
print(len(volume.split()), 'words')
for lab in LABELS:
    print(lab, len(reg[lab]))
