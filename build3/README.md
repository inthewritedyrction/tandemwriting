# The Tandem Companion — Build 3 (TKC)

TKC Volume One, The World Dossier, assembled and print-ready: Parts I–XI plus a canon register.

- `dist/TKC_Volume_One_World_Dossier.pdf`: the print copy (Letter, white page, ITWD pink detailing per the Print Direction), with portrait frames, map and diagram plates, and a working page after every part.
- `volume_one/TKC_Volume_One_World_Dossier.md`: the same volume as plain markdown, for pasting into the Claude Doc or editing.
- `volume_one/II3_Deep_dives.md`, `III_People_of_the_Text.md`, `IV_Jesus_Kingdom_Prayer.md`, `V_Christianity_and_Power.md`: the four sections written in this build, one per pending block in the Claude Doc. `volume_one/parts/` holds their pieces.

## Rebuild

```
python3 tools/pdf2md.py src/intake/TKC_Volume_One_The_World_Dossier_rev15.pdf volume_one/from_doc/rev15.md   # only if the doc export changes
python3 tools/assemble.py                         # rev 15 + the four sections → the volume markdown, canon fixes, plates, register
python3 tools/build_print.py out/toc_pages.json   # markdown → out/volume_one.html
node tools/print.mjs                              # Chromium → dist/*.pdf
python3 tools/toc_pages.py                        # read back where each part landed, then rerun the two lines above
```

Needs Python 3 with `markdown` and `pdfplumber`, and Node with Playwright/Chromium. Fonts (EB Garamond, Cinzel, Jost) are local in `assets/fonts/`.

## Sources in `src/intake/`

| File | What it is |
| --- | --- |
| `TKC_Companion_Final_Rulings.dc.html` | Final Rulings, FR 0–44. Outranks everything. |
| `TKC_Companion_Print_Direction.pdf` | The print look |
| `TKC_Volume_One_The_World_Dossier_rev15.pdf` | The Claude Doc at rev 15 (intro, Parts I–II.2, VI–XI) |
| `TKC_Volume_One_The_World_Dossier.pdf` | An earlier export (world parts only) |
| `Old_Companion_p001-085.pdf`, `p086-170`, `p171-251` | The old Companion (TKC workbook), 251 pages |
| `Writing_Rules.docx`, `Timeline_Updated.docx`, `The_Covenant_Trials_Updated.docx`, `The_Dominions_Update.docx`, `Men_In_The_Covenant_Empire.docx`, `The_Crownward.docx` | Source files, with text extractions in `txt/` |
| `TKC_Companion_Vol_II_*.dc.html`, `TKC_Companion_Sources_and_Editions.dc.html` | The earlier Volume Two drafts (Eden, Celeste, the Characters) and the old sources pages, with text in `txt/` |
| `txt/Final_Rulings.txt` | FR 0–44 as plain text |

## The Volume One workbook

`dist/TKC_Volume_One_Workbook.pdf` is the printed workbook: 581 pages at 8.5 × 11, white with the ITWD pink.

- The source is in `workbook/units/*.tkc`, one file per section. They're read in filename order.
- `workbook/wb.py` renders the units to `out/workbook.html`, and `workbook/wb.css` holds every page style.
- `workbook/wb_print.mjs` fills the writing lines and checks every page for overflow. It moves an overflowing prompt onto a facing working page, through `out/continuations.json`, and prints the PDF.
- `workbook/gen_dominions.py` regenerates the Part VII unit.

To rebuild:

```
rm -f out/continuations.json
for i in 1 2 3; do python3 workbook/wb.py && node workbook/wb_print.mjs out/sample.pdf; done
node workbook/wb_print.mjs
```

## The Volume Two workbook

`dist/TKC_Volume_Two_Workbook.pdf` is The People: one dossier per character, in the same page system as Volume One, printed as one PDF. `dist/print/` also holds it in five section files for printers.

- The source is in `workbook/units_v2/*.tkc`: the front matter, then Part I (the Parish household), II (House Aurem), III (the Covenant Daughters), IV (the House of Vane), V (the 39th Trial as story) and the back matter.
- Volume Two cites Volume One as `{v1:key}`, for example `Vol. I, {v1:hannah}`. `workbook/v1_refs.json` maps each key to a Volume One running head, and `wb.py` prints the page Volume One's last build gave that head. Rebuild Volume One first if its pagination changes, then Volume Two picks it up. An unknown key stops the build.
- `workbook/voice_lint.py` checks the printed text for em dashes, semicolons, sentences opening with That, Not or Then, the "isn't X. It's Y." cadence, and labels that don't open their sentence.

To rebuild:

```
rm -f out/continuations_v2.json
for i in 1 2 3; do TKC_VOL=2 python3 workbook/wb.py && TKC_VOL=2 node workbook/wb_print.mjs out/sample_v2.pdf; done
TKC_VOL=2 node workbook/wb_print.mjs
TKC_VOL=2 python3 workbook/voice_lint.py
python3 tools/print_ready.py 2      # needs pikepdf
```
