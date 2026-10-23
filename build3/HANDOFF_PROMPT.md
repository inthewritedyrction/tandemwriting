# Handoff prompt for another Claude Code session

Paste everything below the line into the other session.

---

I'm Dany. I'm writing a novel called *Thy Kingdom Come* (TKC). It's set in 2104 in the Covenant Empire of America, a Christian theocracy that replaced the United States between 2033 and 2051. Eden Selah Osei, 21, from the outer districts of Aurelia (once Atlanta), self-nominates for the 39th Covenant Trials. The Trials are a televised four-month selection in which the Crown Heir, Judah Elijah Vane, chooses his Anointed Wife from twelve Covenant Daughters, one from each Dominion.

I'm building a two-volume companion workbook for drafting the novel. Both volumes are designed print PDFs on a white background with ITWD pink (#E5173F) detailing. They have big type, distinct divider pages and a lot of handwriting space. They're meant to be written in.

**Where everything is**
- Repo: `inthewritedyrction/tandemwriting`. Branch: `claude/busy-gates-pooicy`. Work only on that branch and push with `git push -u origin claude/busy-gates-pooicy`. Don't open a PR unless I ask.
- Everything lives in `build3/`. `build3/README.md` explains how to rebuild.
- **Volume One, The World Dossier** is done. It's `build3/dist/TKC_Volume_One_Workbook.pdf`, 581 pages, built from `build3/workbook/units/*.tkc`.
  - Part I, Learning the Bible as a novelist: Bible 101, the modules, the sixty-six books, focused studies F1–F7, and deep dives on Genesis, Exodus, Leviticus and Deuteronomy.
  - Part II, the people of the text.
  - Part III, Jesus, the kingdom, the Lord's Prayer and the Gospel Grid.
  - Part IV, empire and interpretation, with American history.
  - Part V, the Fall of the United States.
  - Part VI, the Empire's institutions, doctrine, lived religion and the household order.
  - Part VII, the twelve Dominions.
  - Part VIII, the Covenant Trials.
  - Back matter: the canon register, open questions, the discovery log and sources.
- **Volume Two, The People** is in progress. Its units go in `build3/workbook/units_v2/`. Build it with `TKC_VOL=2` set on `workbook/wb.py` and `workbook/wb_print.mjs`. It prints to `build3/dist/TKC_Volume_Two_Workbook.pdf`.
- My source files are in `build3/src/intake/`. Plain-text copies are in `build3/src/intake/txt/`:
  - Timeline Updated (TL)
  - The Covenant Trials Updated (TR)
  - The Dominions Update (DOM)
  - Men in the Covenant Empire (MEN)
  - Writing Rules (WR)
  - Final Rulings (FR 0–44, in `TKC_Companion_Final_Rulings.dc.html`)
  - World Dossier rev15
  - the old 251-page Companion (AM)

  Don't go searching my files for manuscripts. I supply those myself. Don't email anyone.

**How the page engine works** (`build3/workbook/wb.py` is the documentation)
- Each unit is a text file of pages. The page types are `@part`, `@divider`, `@opener`, `@page`, `@essay` and `@notes`. Page attributes include `rh` (running head), `m` (margin references) and `id`.
- Block types include `rec:` label/value rows, `tabrl:` and `tab:` tables (a `_` cell is blank writing space), and `box:`, `empire:`, `contested:` and `cols:` blocks closed with `/end`.
- Other blocks: `prompt: Question | fill` (or a fixed number of lines, or `| rest` for no extra page), `status`, `corr:`, `note:` for content notes, and `q:` for quotes. `plate: frame | CAPTION | 3in` makes a portrait frame, and `plate: doc` and `plate: quote` make designed documents and quotes.
- `wb_print.mjs` fills the ruled lines, finds overflow, and moves an overflowing prompt onto a facing working page. Rebuild in a loop until it reports 0 layout problems:
  `rm -f out/continuations_v2.json; for i in 1 2 3; do TKC_VOL=2 python3 workbook/wb.py && TKC_VOL=2 node workbook/wb_print.mjs out/sample.pdf; done; TKC_VOL=2 node workbook/wb_print.mjs`

**Volume Two's job**
One dossier per character, with designed portrait frames, record cards and a lot of writing space. The parts are:
- I, the Parish household: Celeste, Eden, Miriam, Thomas, Leah, Zion, Solomon
- II, House Aurem: Hannah, Naomi, Mirielle, Gavin, Abigail, plus Senior Minister Bell and the Aurem officials
- III, the twelve Covenant Daughters
- IV, the House of Vane: Dorian, Lyris, Judah, Azrael, and the Prelate
- V, the 39th Trial as story, with the beats, the fates and a chapter planner
- Back matter: conflicts, open questions and the log

**Volume Two has to go with Volume One, especially the religion.** Every major character gets a faith-and-scripture page covering:
- what she or he actually believes, and who taught it
- what the Temple teaches about someone like them
- their biblical name echo and where the parallel breaks
- the passages they'd quote and the ones they'd never be read
- pointers to the exact Volume One sections (for example "Vol. I, Deep dive I, Genesis, page 8" or "Vol. I, Part VI, lived religion")

The novel's religious line runs between faith the Temple can use and faith that answers to something it doesn't control. Biblical accuracy in the narration has to be clean, and the Empire's distortions have to be deliberate (WR 38–42).

**Canon (the Final Rulings outrank everything)**
- Solomon is 16 (the timeline's 13 is superseded). Leah is younger than Eden: Leah is 20 and Zion is 19.
- Thomas left voluntarily in 2084 (FR 3). Celeste has no proof Miriam is alive, and the 2094 letter was intercepted (FR 16). Leah sat for an assessment.
- Solomon's father is the man Miriam was reassigned to (FR 0).
- Crest is Dorian's uncle (FR 35). The Prelate's working name is Aurelia, marked POSSIBLE. She is never Huldah or Naomi, because Hannah's daughter keeps the name Naomi (FR 33).
- Calla's surname is Merritt.
- Lyris is never called anything else (WR 32).

**Labels and voice (strict)**
- Labels go at the start of the sentence they govern: INTERPRETATION, CONTESTED, INFERENCE, POSSIBLE, OPEN QUESTION, CONFLICT, SUPERSEDED, DECIDED. Anything from my files carries a source tag only (TL, TR, DOM, MEN, CR, DR3, WR, AM, FR n, Ruling).
- Voice:
  - Use contractions.
  - No em dashes and no semicolons.
  - No "This is not X. It is Y."
  - No aphorisms, zingers or reflexive lists of three.
  - No sentences starting with That, Not or Then.
  - No horizontal rules and no emojis.
  - Put content notes before hard material.

Before you change anything, check the latest commits on the branch, because another session may be working in the same files. Ask me which part to take so two sessions don't edit the same unit.
