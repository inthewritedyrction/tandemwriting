"""Remnian Imperial + Royal Lineage — working record (Build 2).

A DERIVED RECORD, not a source. Every claim below names the source(s) it
comes from and carries the status those sources earn under the authority
order: rulings > Beta > locked constraints / current author decisions >
current development > book reference > shared lore > supporting artifacts
> legacy. Agreement between two weak sources is never promoted to CANON.

Built from evidence, 2026-10-09. The unaudited *Imperial Lineage* file was
used for comparison only (see COMPARE_IL); nothing is imported from it.

Layers are kept apart (TCD-040): BIO (biological), LEGAL (legal family
status), PUBLIC (public / recorded), TITLE, SUCC (dynastic / succession
position). A claim on one layer never fills another.

Status codes: c CANON · d CURRENT DRAFTED TEXT · s SUPPORTED · p POSSIBLE ·
o OPEN · x CONFLICT · l LEGACY / SUPERSEDED.
"""

# ------------------------------------------------------------------ sources
# key: (short label, full name, authority treatment in this record, availability)
SOURCES = {
    "BETA": ("Beta", "FTE Official Beta Reader Copy", "Controlling FTE prose (TCD-001). Statuses: CURRENT DRAFTED TEXT.",
             "Not in this session; its lineage facts are taken as the Content Master records them, with chapter."),
    "3139": ("31–39", "FTE 31–39 (development chapters)", "Supporting; rewrite required before any line is canon (TCD-001).",
             "Through the Content Master. The uploaded FTE 2025 FINAL file contains the same passages."),
    "BSS": ("BSS", "FTE Remnian Timeline Before Story Start", "Historical/development pool, claim by claim. Latest expanded ER generation; Supporting / needs ruling (audit). Never controls chronology (TCD-010).",
            "Uploaded 2026-10-09; read in full."),
    "TLE": ("TLE", "FTE Remnian Timeline Early", "Earlier pool for genealogy, old succession and names; every later source outranks it. Claims only it makes are LEGACY until separately supported (audit).",
            "Uploaded 2026-10-09; read in full (it ends in 2066 ER)."),
    "F2025": ("F2025", "FTE 2025 FINAL", "Legacy prose (TCD-001). Corroboration only; never establishes a claim.",
              "Uploaded 2026-10-09; searched for every lineage passage."),
    "F4": ("F4", "Full 4 Series Flesh Out", "Shared lore pool / legacy recovery source (TCD-022). Claim by claim; cross-series mechanisms are not imported.",
           "Uploaded 2026-10-09; searched for every lineage passage."),
    "CB": ("CB", "Character Bible", "Supporting by claim (audit). Its Michelle/Tobias and Lucia/Tobias parentage is confirmed by TCD-040.",
           "Not in this session; through the Content Master."),
    "WTR": ("WTR", "Welcome to Remnia", "Supporting.", "Not in this session; through the Content Master."),
    "3SL": ("3SL", "3 Shadowmere Lane draft", "Controlling 3SL prose.", "Through the Content Master."),
    "PLC": ("Placements", "49th Placements", "Supporting.", "Through the Content Master."),
    "IL": ("IL", "The Imperial Lineage (unaudited)", "Comparison only. Not imported.", "Not in this session; the Content Master quotes it."),
}

# ------------------------------------------------------------------ people
# Each person: id, name, house, variants, group (genealogy panel), and claims.
# claim = (layer, field, text, status, [sources], note)
P = []


def person(pid, name, house, claims, variants=(), group="imperial", core=True):
    P.append({"id": pid, "name": name, "house": house, "variants": list(variants), "group": group,
              "core": core, "claims": claims})


# ---- Hastings / imperial line
person("eden", "Eden Genesis", "Hastings (also styled Mignonette)", [
    ("TITLE", "Public title", "Founding Empress of Remnia (Year 1 ER)", "l", ["TLE"], ""),
    ("SUCC", "Dynastic position", "Predecessor of Aracelia on the throne; matrilineal line Eden → Aracelia → Lucia → Elias", "s", ["WTR", "TLE"], "LC-04"),
    ("BIO", "Spouse", "Stephen Abraham Hastings, Emperor Consort", "l", ["TLE"], ""),
    ("BIO", "Children", "Richard, Madeleine, Victoria, and the twins Aracelia and Alexandria", "l", ["TLE"], "Richard and Alexandria are also in BSS; their parentage there is not stated."),
    ("BIO", "Death", "“Deceased for decades” by 2091", "s", ["BSS"], "LC-04: the same file has her reigning and blessing Lucia’s decree in 2073–76"),
    ("BIO", "Generation", "Elias’s grandmother (BSS 2073) vs great-grandmother (TLE, WTR line)", "x", ["BSS", "TLE", "WTR"], "LC-04"),
], variants=["Eden Genesis Hastings (TLE)", "Eden Mignonette / Migonnette (TLE)", "Eden Genesis (BSS)"])

person("caliane", "Caliane Azira Hastings", "Hastings", [
    ("TITLE", "Public title", "Empress; signed the Tournament augmentation law", "l", ["F2025"], ""),
    ("BIO", "Generation", "Melena’s great-grandmother", "x", ["F2025"], "LC-05: TLE and WTR put Eden in that place"),
], core=True)

person("aracelia", "Aracelia", "Hastings (house) · surname in conflict", [
    ("TITLE", "Public title", "Empress; reigns during FTE", "d", ["BETA"], ""),
    ("TITLE", "Styled name", "“Aracelia Meson Mignonette” (Beta letter) · “Aracelia Meson Mignonette Hastings” (BSS) · “Aracelia Mignonette Hastings” (TLE) · “Empress Aracelia Lockwood” (31–39)", "x", ["BETA", "BSS", "TLE", "3139"], "LC-02"),
    ("BIO", "Parents", "Empress Eden and Emperor Consort Stephen", "l", ["TLE"], "Matrilineal Eden → Aracelia in WTR"),
    ("BIO", "Born", "7 October 2038, elder twin of Alexandria", "s", ["TLE", "BSS"], "BSS gives her age as 57 in 2095; it agrees with TLE. Not canon (TCD-010)."),
    ("BIO", "Spouse", "Duke Jackson Harper (married 9 Sept 2060)", "l", ["TLE"], "No later source names her husband"),
    ("BIO", "Children", "Lucia (with Charlotte, twins), Elaine, Arianne", "l", ["TLE"], "Lucia as her daughter is supported: BSS calls the Lockwood children her grandchildren; WTR line"),
    ("BIO", "Element", "Frost (attunement shown 2060)", "l", ["TLE"], ""),
    ("SUCC", "Dynastic position", "Reigning Empress at FTE opening", "d", ["BETA"], ""),
    ("SUCC", "Accession", "Reigned while Lucia preceded Elias in succession", "c", ["TCD-032"], "Accession date OPEN (LC-04)"),
    ("PUBLIC", "Grandmother of the Lockwood heirs", "Melena’s grandmother; guardianship orders for the children after Lucia’s death (11 Sept 2094)", "d", ["BETA", "BSS"], "Grandmother: Beta. Guardianship orders: BSS only (SUPPORTED)."),
    ("PUBLIC", "Knowledge of Katherine", "Not ruled", "o", ["TCD-059"], "Aracelia’s role in the concealment is open"),
], variants=["Aracelia Meson Mignonette", "Aracelia Mignonette Hastings", "Aracelia Meson Mignonette Hastings", "Aracelia Lockwood (31–39)"])

person("jackson", "Jackson Harper", "Harper", [
    ("BIO", "Spouse", "Aracelia (married 2060)", "l", ["TLE"], ""),
    ("BIO", "Children", "Lucia, Charlotte, Elaine, Arianne", "l", ["TLE"], ""),
    ("TITLE", "Public title", "Duke; styled “The Crown Prince” on marriage", "l", ["TLE"], ""),
], variants=["Duke Jackson Hastings (TLE, once)"], core=False)

person("richard", "Richard David Elliot Hastings", "Hastings", [
    ("BIO", "Parents", "Empress Eden and Emperor Consort Stephen (eldest child)", "l", ["TLE"], ""),
    ("BIO", "Relation", "Elias’s and Louis’s great-uncle; “the only male born into a line of powerful sisters”", "s", ["BSS"], "Consistent with TLE (Aracelia’s brother)"),
    ("BIO", "Spouse", "Princess Ember", "s", ["TLE", "BSS"], ""),
    ("BIO", "Children", "Olympia (2058), Estelle (2059)", "l", ["TLE"], ""),
    ("BIO", "Born", "3 September 2024 (TLE) vs about 2039 (BSS: 55 in 2094)", "x", ["TLE", "BSS"], "LC-13"),
    ("TITLE", "Public title", "Prince; Crown Prince at birth (TLE)", "l", ["TLE"], "Displaced as heir by Aracelia in 2055 (TLE)"),
    ("LEGAL", "Guardianship", "Files for Elias’s guardianship (2094); granted guardianship of Louis (11 Sept 2094)", "s", ["BSS"], ""),
], variants=["Richard David Elliot (TLE)"])

person("alexandria", "Alexandria Melena Mignonette", "Hastings (by marriage to Clyde Hastings)", [
    ("BIO", "Parents", "Empress Eden and Emperor Consort Stephen; younger twin of Aracelia", "l", ["TLE"], ""),
    ("BIO", "Spouse", "Lord Clyde Hastings (d. Nov 2096)", "s", ["TLE", "BSS"], ""),
    ("BIO", "Children", "Amalia Danyelle (b. 2 May 2062), Evangeline Kelly (b. 4 Aug 2063)", "s", ["TLE", "BSS"], "BSS ages (34, 33 in 2096) match TLE"),
    ("TITLE", "Public title", "Princess of Remnia, Duchess of Alleia", "s", ["TLE", "BSS"], ""),
], core=False)

person("lucia", "Lucia Noelle Marie Hastings-Lockwood", "Hastings; Lockwood by marriage", [
    ("BIO", "Parents", "Aracelia and Jackson Harper", "l", ["TLE"], "Aracelia as mother: SUPPORTED (BSS, WTR)"),
    ("BIO", "Born", "2047 (BSS: 47 at death) vs 26 October 2055 (TLE)", "x", ["BSS", "TLE"], "LC-03"),
    ("BIO", "Spouse", "Tobias Lockwood, Prince Consort", "s", ["BSS", "CB"], ""),
    ("BIO", "Children", "Melena (with Tobias)", "c", ["TCD-040"], ""),
    ("BIO", "Children", "Elias, Cordelia, Louis (with Tobias)", "s", ["BSS"], "Elias, Cordelia and Louis as Lucia’s children are also the Beta’s family (Melena’s siblings)"),
    ("BIO", "Element", "Frost: “one of the most powerful” in the empire", "d", ["BETA"], "31–39 makes her a Flamer: REVISION FLAG (LC-21)"),
    ("BIO", "Death", "Dead before FTE", "d", ["BETA"], ""),
    ("BIO", "Death · when, how", "7 Sept 2094, Imperial Palace, “nighttime medical crisis” (BSS) vs a car accident (31–39)", "x", ["BSS", "3139"], "LC-16"),
    ("TITLE", "Public title", "Crown Princess; “Duchess of Zenithia”", "s", ["BSS"], "Crown Princess also CB, WTR; Zenithia title: LC-20"),
    ("TITLE", "Earlier style", "The Princess Imperial (from birth, 2055)", "l", ["TLE"], ""),
    ("SUCC", "Position", "Heir to Aracelia; preceded Elias", "c", ["TCD-032"], ""),
    ("LEGAL", "Act", "Originated Katherine’s public/legal and dynastic erasure", "c", ["TCD-059"], ""),
    ("LEGAL", "Act (as drafted in BSS)", "Treason decree on discussion of Katherine’s birth; legal action leaving her no claim; forbade her raising in London Town", "s", ["BSS"], "Mechanism SUPPORTED only; publicity OPEN (LC-08)"),
    ("LEGAL", "Act (as drafted in BSS)", "2076 decree: daughters keep their place regardless of younger brothers", "s", ["BSS"], "LC-06"),
], variants=["Lucia Hastings (BSS 2073)", "Lucia Noelle Marie (TLE)"])

# ---- House Lockwood
person("alistair_l", "Alistair Lockwood", "Lockwood", [
    ("BIO", "Children", "Tobias", "s", ["BSS"], ""),
    ("BIO", "Spouse", "Duchess Rowena Lockwood", "s", ["BSS"], ""),
    ("BIO", "Born", "About 2027 (67 in 2094)", "x", ["BSS"], "LC-14: about eight at Tobias’s TLE birth date"),
    ("TITLE", "Public title", "Duke", "s", ["BSS"], ""),
    ("LEGAL", "Guardianship", "Petitions for Elias (July 2094, delayed by the Sanctum); granted Cordelia with Rowena (11 Sept 2094)", "s", ["BSS"], ""),
], group="lockwood")

person("rowena", "Rowena Lockwood", "Lockwood", [
    ("BIO", "Spouse · children", "Alistair Lockwood · Tobias", "s", ["BSS"], ""),
    ("TITLE", "Public title", "Duchess", "s", ["BSS"], ""),
], group="lockwood", core=False)

person("tobias", "Tobias Lockwood", "Lockwood", [
    ("BIO", "Children", "Katherine (with Michelle Nicholas) and Melena (with Lucia)", "c", ["TCD-040"], "LOCKED ANCHOR"),
    ("BIO", "Children", "Elias, Cordelia, Louis (with Lucia)", "s", ["BSS"], ""),
    ("BIO", "Parents", "Duke Alistair and Duchess Rowena Lockwood", "s", ["BSS"], ""),
    ("BIO", "Born", "2 August 2035, Lockwood Manor, Highcrest", "l", ["TLE"], "LC-14"),
    ("BIO", "Element", "Fire, by implication: Melena “took after their father — fire running through her veins”", "d", ["BETA"], "31–39 Mirror: Tobias calls himself a Frost (REVISION FLAG, LC-21)"),
    ("BIO", "Death", "Dead before FTE", "s", ["CB", "3139"], ""),
    ("BIO", "Death · when, how", "Six months after Lucia; officially a fall on wet stairs; Melena believes suicide", "s", ["3139"], "LC-17: BSS never places him in 2094–96"),
    ("LEGAL", "Marriage", "Lucia’s husband; Prince Consort", "s", ["BSS", "CB"], ""),
    ("LEGAL", "Role in Katherine’s concealment", "Cooperates by non-acknowledgment; not established as the architect", "c", ["TCD-059"], ""),
    ("PUBLIC", "Relationship with Michelle", "“Tried to make it work for years”; Dalia was one of three people who knew", "s", ["3139"], "F2025 has the same passage"),
    ("TITLE", "Public title", "Prince Consort", "s", ["CB", "BSS"], "TLE styles him “Head of the Lockwood House” from birth (LEGACY; LC-14)"),
], group="lockwood")

person("celeste_aunt", "Celeste (Tobias’s late aunt)", "Lockwood side · surname not given", [
    ("BIO", "Relation", "Tobias’s aunt, dead by 2076; Katherine’s middle name honours her", "s", ["BSS"], "Not Lady Celeste Blackwood: NV-02"),
], group="lockwood", core=False)

person("elias", "Elias Louis Alexander Lockwood", "Lockwood", [
    ("BIO", "Parents", "Lucia and Tobias", "s", ["BSS", "WTR"], "Melena’s brother (Beta); full parentage not ruled"),
    ("BIO", "Born", "3 October 2073, Imperial Palace, London Town", "s", ["BSS"], "Calendar unruled (TCD-010)"),
    ("BIO", "Eyes", "Golden, “associated with the Lockwood lineage”", "s", ["BSS"], "IL repeats it"),
    ("TITLE", "Public title", "Crown Prince, after Lucia’s death", "c", ["TCD-032"], ""),
    ("TITLE", "Title at birth", "“Crown Prince of Remnia” from 2073", "l", ["BSS"], "Superseded by TCD-032 (LC-09)"),
    ("TITLE", "Public title", "Duke of Somnoria, the heir apparent’s “traditional title”", "s", ["BSS"], "LC-09, LC-10"),
    ("SUCC", "Position", "First in line (heir apparent) at FTE opening", "c", ["TCD-032"], ""),
    ("PUBLIC", "Status at FTE", "Missing from Remnia: failed to return on pattern; Professor Alexander Thorne in Somnoria", "c", ["TCD-032", "TCD-013"], ""),
])

person("melena", "Melena Elizabeth Beatrix Lockwood", "Lockwood", [
    ("BIO", "Parents", "Lucia Hastings-Lockwood and Tobias Lockwood", "c", ["TCD-040"], "LOCKED ANCHOR"),
    ("BIO", "Relation to Katherine", "Paternal half-sister", "c", ["TCD-040"], ""),
    ("BIO", "Born", "9 Sept 2076 (BSS) vs 2077 (CB); age unstated in the Beta", "x", ["BSS", "CB"], "LC-15"),
    ("BIO", "Element", "Flamer; volatile", "d", ["BETA"], ""),
    ("BIO", "Eyes", "Amber (Beta) vs green (3SL, BSS, CB, 31–39)", "x", ["BETA", "3SL", "BSS", "CB", "3139"], "LC-01"),
    ("TITLE", "Public title", "Princess", "d", ["BETA"], ""),
    ("TITLE", "Further title", "Duchess of Avalon", "s", ["BSS"], "No province of that name in TLE’s seventeen (LC-20)"),
    ("SUCC", "Position", "Second in line, after Elias", "d", ["BETA"], ""),
    ("LEGAL", "Guardianship", "Granted to Lorelei and Lady Helena’s household (11 Sept 2094)", "s", ["BSS"], ""),
    ("PUBLIC", "Knows Katherine is her sister", "Nothing on the page in chs. 1–29", "d", ["BETA"], ""),
])

person("cordelia", "Cordelia Gwendolyn Marie Lockwood", "Lockwood", [
    ("BIO", "Parents", "Lucia and Tobias", "s", ["BSS"], "Melena’s sister (Beta)"),
    ("BIO", "Born", "2 September 2079", "s", ["BSS"], "Beta: seventeen at FTE. Consistent."),
    ("BIO", "Element", "Frost, inherited from Lucia (“Second generation”)", "d", ["BETA"], ""),
    ("BIO", "Eyes · hair", "Amber eyes and crimson hair, like Melena’s", "d", ["BETA"], "LC-01"),
    ("SUCC", "Position", "Third in line", "s", ["BSS"], "Consistent with the Beta’s Melena second"),
    ("LEGAL", "Guardianship", "Granted to Duke Alistair and Duchess Rowena Lockwood (11 Sept 2094)", "s", ["BSS"], ""),
    ("TITLE", "Public title", "Princess of Remnia", "s", ["BSS"], ""),
])

person("louis", "Louis Reginald Henry Lockwood", "Lockwood", [
    ("BIO", "Parents", "Lucia and Tobias", "s", ["BSS"], ""),
    ("BIO", "Born", "14 May 2081", "s", ["BSS"], "The youngest (CM: SUPPORTED)"),
    ("SUCC", "Position", "Fourth in line", "s", ["BSS"], ""),
    ("LEGAL", "Guardianship", "Granted to Prince Richard Hastings, his great-uncle (11 Sept 2094)", "s", ["BSS"], ""),
    ("TITLE", "Public title", "Prince of Remnia", "s", ["BSS"], ""),
], variants=["Louis Reginal Henry (BSS, once)"])

# ---- Michelle / Katherine
person("michelle", "Michelle Nicholas", "Nicholas", [
    ("BIO", "Children", "Katherine (with Tobias Lockwood)", "c", ["TCD-040"], "LOCKED ANCHOR"),
    ("BIO", "Family", "Her maternal grandmother is the “Medina” of Katherine’s name", "s", ["BSS"], "LC-18"),
    ("TITLE", "Rank", "Lieutenant; former Captain of the En Guard, stepped down two months before ch. 1", "d", ["BETA"], "BSS: Captain of the En Guard in 2076"),
    ("LEGAL", "Role in the concealment", "Raises and protects Katherine inside imposed constraints; not the architect", "c", ["TCD-059"], ""),
    ("PUBLIC", "Who knew of her and Tobias", "Queen Dalia was one of three people who knew of the relationship", "s", ["3139"], "Whether Dalia knows Katherine is Tobias’s child is unstated"),
], group="nicholas")

person("ethan", "Ethan", "surname in conflict", [
    ("BIO", "Katherine’s biological father", "Superseded", "l", ["TCD-040"], ""),
    ("BIO", "Born", "18 Nov 2035, Nicholas Estate, Meridion; “Head of the Nicholas House”", "l", ["TLE"], ""),
    ("LEGAL", "Social or naming role", "“Gave Katherine his name” (WTR); sits beside Michelle as “her father, Ethan” (F2025)", "p", ["WTR", "F2025"], "No ruling (CM IV.9)"),
    ("TITLE", "Surname", "Medina (WTR) vs Nicholas (TLE)", "x", ["WTR", "TLE"], "LC-18"),
], group="nicholas", variants=["Ethan Medina (WTR)", "Ethan Nicholas (TLE)", "Ethan (F2025)"])

person("katherine", "Katherine Medina Celeste Nicholas", "Nicholas", [
    ("BIO", "Parents", "Michelle Nicholas and Tobias Lockwood", "c", ["TCD-040"], "LOCKED ANCHOR"),
    ("BIO", "Relation to Melena", "Paternal half-sister", "c", ["TCD-040"], ""),
    ("BIO", "Born", "2076 (CB); 14 July 2076, Military Hospital, Old Prosperity (BSS)", "s", ["CB", "BSS"], "Before Melena in both sources: O-01"),
    ("BIO", "Element", "Registered Frost; objectively one ancestral capacity, Frost-dominant, Fire by later reroute", "c", ["BETA", "TCD-049", "TCD-058"], "Registered Frost: DRAFTED. Which parent the capacity comes from: OPEN"),
    ("LEGAL", "Legal status", "Not ruled: legitimacy, name at law, royal or not", "o", ["TCD-040"], "Biology settles none of it"),
    ("LEGAL", "Name on her orders", "Corporal Katherine Medina Celeste Nicholas", "d", ["BETA"], "BSS gives the same full name"),
    ("LEGAL", "Erasure", "Public/legal and dynastic erasure originated by Lucia / the Lockwood Crown; the Sanctum enforces and keeps the records", "c", ["TCD-059"], ""),
    ("PUBLIC", "Public knowledge", "Not ruled; sources conflict", "o", ["TCD-059"], "LC-08"),
    ("PUBLIC", "As BSS drafts it", "“Highly publicized” birth; treason decree; 2091 Sanctum suppression order; “legally protected identity”", "s", ["BSS"], "Not adopted (LC-08)"),
    ("PUBLIC", "Knows Tobias is her father", "Nothing on the page in chs. 1–29", "d", ["BETA"], ""),
    ("TITLE", "Title", "None. Not a princess, not a Lockwood by law", "o", ["TCD-040"], "Each is a separate decision"),
    ("TITLE", "“Katherine Lockwood”", "Legacy naming", "l", ["F4"], "Rejected: R-01"),
    ("SUCC", "Position", "Not in the recorded line; any claim at law not ruled", "o", ["TCD-040", "TCD-059"], ""),
    ("SUCC", "Named heir apparent (Book 3)", "Legacy sequel plot", "l", ["F4"], "Rejected: R-02"),
], group="nicholas")

# ---- London Town · Kinross / Augustine
person("samantha", "Samantha Ruby Kinross", "Kinross", [
    ("TITLE", "Public title", "First Queen of London Town; “what will later become the House of Augustine”", "l", ["TLE"], ""),
    ("BIO", "Spouse", "King Edward Kinross (2038 entry) vs King Brenton (2058 entry)", "x", ["TLE"], "LC-12"),
    ("BIO", "Children", "Lauren, Angelica, Dalia, Nathaniel, Fallon", "l", ["TLE"], "Dalia and Nathaniel as siblings: SUPPORTED (BSS)"),
], group="augustine", core=False)

person("edward", "Edward Kinross", "Kinross", [
    ("BIO", "Children", "Dalia, Nathaniel", "s", ["TLE", "BSS"], "BSS: Maxim’s maternal grandfather “King Edward XVIII”; Nathaniel is Dalia’s brother in both"),
    ("TITLE", "Public title", "King (of London Town)", "s", ["TLE", "BSS"], "LC-12"),
], group="augustine", variants=["King Edward XVIII (BSS)"])

person("dalia", "Dalia Clementine Lexington", "Kinross (birth); Augustine (marriage)", [
    ("BIO", "Parents", "Queen Samantha and King Edward Kinross", "s", ["TLE", "BSS"], "Edward: both. Samantha: TLE only"),
    ("BIO", "Born", "31 October 2038", "s", ["TLE", "BSS"], "BSS: 34 in 2072"),
    ("BIO", "Spouse", "David Augustine, Prince Consort (BSS, CB) vs King William (WTR)", "x", ["BSS", "CB", "WTR"], "LC-11"),
    ("BIO", "Children", "Maxim, Minho, Zephyr and Zoe (twins), Sebastian, Orion", "s", ["BSS"], "The four sons: Beta (Augustine brothers). Zoe and Orion: BSS only"),
    ("TITLE", "Public title at FTE", "Queen of London Town (from 30 June 2090)", "s", ["BSS", "3139"], "CB: Crown Princess (LC-11)"),
    ("SUCC", "Accession", "Nathaniel abdicates in her favour (15 June 2090)", "s", ["BSS"], ""),
    ("PUBLIC", "Knowledge", "Knew of Michelle and Tobias; whether she knows Katherine’s paternity is unstated", "s", ["3139"], ""),
], group="augustine", variants=["Dalia Clementine Lexington Kinross (BSS)", "Queen Dalia Augustine (WTR)"])

person("nathaniel", "Nathaniel Reece Isaiah Kinross", "Kinross", [
    ("BIO", "Parents", "Queen Samantha and King Edward Kinross; Dalia’s younger brother", "s", ["TLE", "BSS"], ""),
    ("BIO", "Born", "24 November 2039", "l", ["TLE"], ""),
    ("TITLE", "Public title", "King of London Town (from 2058, TLE) until his abdication (15 June 2090, BSS)", "s", ["TLE", "BSS"], ""),
    ("LEGAL", "Act", "2090 decree: daughters keep their place regardless of birth order, if born to the Queen and Prince Consort", "s", ["BSS"], ""),
], group="augustine", core=False)

person("william", "William", "Augustine (as WTR names him)", [
    ("TITLE", "Public title", "King of London Town, with Queen Dalia Augustine", "x", ["WTR"], "LC-11"),
], group="augustine", core=False)

person("david", "David Augustine", "Augustine", [
    ("BIO", "Spouse", "Dalia", "s", ["BSS", "CB"], "WTR names King William instead (LC-11)"),
    ("BIO", "Parents", "Lord Alexander Augustine (father); Lord George Augustine is his uncle", "s", ["BSS"], ""),
    ("TITLE", "Public title", "Prince Consort", "s", ["BSS", "CB"], "LC-11"),
], group="augustine")

person("maxim", "Maximillian Edward George Augustine", "Augustine", [
    ("BIO", "Parents", "Dalia and David Augustine", "s", ["BSS"], ""),
    ("BIO", "Born", "7 September 2072", "s", ["BSS"], "Eldest of the brothers (F2025 agrees)"),
    ("BIO", "Element", "Terrain", "d", ["BETA"], ""),
    ("TITLE", "Public title", "Crown Prince of London Town", "s", ["BSS"], ""),
    ("SUCC", "Position", "First in London Town’s line", "s", ["BSS"], "LC-19"),
], group="augustine", variants=["Maxim"])

person("minho", "Minho Alexander David Augustine", "Augustine", [
    ("BIO", "Parents", "Dalia and David Augustine", "s", ["BSS"], ""),
    ("BIO", "Born", "12 August 2074 (BSS); 2074 (CB)", "s", ["BSS", "CB"], ""),
    ("BIO", "Element", "Blocker", "d", ["BETA"], ""),
    ("TITLE", "Rank", "En Guard Captain; Old Prosperity’s King Piece", "d", ["BETA"], ""),
    ("SUCC", "Position", "Gave up his claim to join Old Prosperity’s military (CB); relinquished 3 March 2091 (BSS)", "s", ["CB", "BSS"], "F2025 corroborates; LC-19"),
], group="augustine")

person("zephyr", "Zephyr David Augustine", "Augustine", [
    ("BIO", "Parents", "Dalia and David Augustine; twin of Zoe", "s", ["BSS"], ""),
    ("BIO", "Born", "7 September 2075", "s", ["BSS"], ""),
    ("BIO", "Element", "Genuine modern Fire/Frost Dyad; registered Flamer (registration in conflict)", "c", ["TCD-049", "PLC"], "Registration: CONFLICT (IV.10)"),
    ("SUCC", "Position", "Fourth in the 2090 list; “sixth” at birth", "x", ["BSS"], "LC-19"),
], group="augustine")

person("zoe", "Zoe Dalia Augustine", "Augustine", [
    ("BIO", "Parents", "Dalia and David Augustine; twin of Zephyr", "s", ["BSS"], ""),
    ("TITLE", "Styled name", "“Princess Zoe Dalia Lockwood Augustine”, styled “Princess Dalia”", "o", ["BSS"], "NV-14: no Lockwood parent is given"),
    ("SUCC", "Position", "Fifth in the 2090 list", "x", ["BSS"], "LC-19"),
], group="augustine", core=False)

person("sebastian", "Sebastian Bartholomew Dominic Augustine", "Augustine", [
    ("BIO", "Parents", "Dalia and David Augustine", "s", ["BSS"], ""),
    ("BIO", "Born", "15 August 2076", "s", ["BSS"], ""),
    ("BIO", "Element", "Flamer", "d", ["BETA"], ""),
    ("SUCC", "Position", "Third in the 2090 list; relinquished (9 April 2095)", "s", ["BSS"], "LC-19"),
], group="augustine")

person("orion", "Orion Nathaniel Augustine", "Augustine", [
    ("BIO", "Parents", "Dalia and David Augustine", "s", ["BSS"], ""),
    ("BIO", "Born", "1 October 2090", "s", ["BSS"], ""),
    ("TITLE", "Styled name", "“Orion Nathaniel Lockwood Augustine”", "o", ["BSS"], "NV-14"),
], group="augustine", core=False)

person("arielle", "Arielle Monet Kinross", "Kinross", [
    ("BIO", "Parents", "“Eldest daughter of a son of the crown”; Dalia’s niece", "o", ["BSS"], "Which son is not named"),
    ("TITLE", "Public title", "The Princess Royal", "s", ["BSS"], ""),
    ("SUCC", "Position", "Placed before Dalia’s unborn son (2090)", "s", ["BSS"], ""),
], group="augustine", core=False)

# ---- collateral lines: earlier-pool people the record keeps but doesn't chart in full
COLLATERAL = [
    ("Stephen Abraham Hastings", "Eden’s spouse; Emperor Consort; once Flamer Regnant", "l", ["TLE"]),
    ("Madeleine Beatrix", "Eden’s second child (b. 2028); m. Lord Felix D’Arcy; daughters Aveline, Isabella, Arabella", "l", ["TLE"]),
    ("Victoria Cassiopeia", "Eden’s third child (b. 2035); Flamer; m. Lord Adrian Wells; daughter Fiona", "l", ["TLE"]),
    ("Charlotte Elizabeth Anai", "Lucia’s younger twin (b. 26 Oct 2055)", "l", ["TLE"]),
    ("Elaine Marie Hastings", "Aracelia’s third daughter (b. 21 Nov 2056)", "l", ["TLE"]),
    ("Arianne Jessamine Hastings", "Aracelia’s fourth daughter (b. 2 April 2066)", "l", ["TLE"]),
    ("Ember Hastings", "Richard’s wife (53 in 2094); daughters Olympia (b. 2058), Estelle (b. 2059)", "s", ["TLE", "BSS"]),
    ("Clyde Hastings", "Alexandria’s husband; dies Nov 2096", "s", ["TLE", "BSS"]),
    ("Amalia Danyelle · Evangeline Kelly Hastings", "Alexandria and Clyde’s daughters (b. 2062, 2063)", "s", ["TLE", "BSS"]),
    ("Lauren Felicity · Angelica Demeter · Fallon Valentina Kinross", "Dalia’s sisters (b. 2024, 2035, 2040)", "l", ["TLE"]),
    ("Brenton", "King whose death in 2058 makes Nathaniel King; relation to Samantha unstated", "l", ["TLE"]),
]
PERSONS = {p["id"]: p for p in P}

# ------------------------------------------------------------------ parent edges (for the genealogy and the consistency check)
# (parent, child, status, sources, note). Child lists in the ledger must agree with these.
EDGES = [
    ("eden", "aracelia", "s", ["TLE", "WTR"], "LC-04, LC-05"),
    ("eden", "richard", "l", ["TLE"], ""),
    ("eden", "alexandria", "l", ["TLE"], ""),
    ("aracelia", "lucia", "s", ["TLE", "WTR", "BSS"], "LC-03"),
    ("jackson", "lucia", "l", ["TLE"], ""),
    ("lucia", "elias", "s", ["BSS", "WTR"], ""),
    ("lucia", "melena", "c", ["TCD-040"], ""),
    ("lucia", "cordelia", "s", ["BSS"], ""),
    ("lucia", "louis", "s", ["BSS"], ""),
    ("tobias", "elias", "s", ["BSS"], ""),
    ("tobias", "melena", "c", ["TCD-040"], ""),
    ("tobias", "cordelia", "s", ["BSS"], ""),
    ("tobias", "louis", "s", ["BSS"], ""),
    ("tobias", "katherine", "c", ["TCD-040"], ""),
    ("michelle", "katherine", "c", ["TCD-040"], ""),
    ("alistair_l", "tobias", "s", ["BSS"], "LC-14"),
    ("rowena", "tobias", "s", ["BSS"], "LC-14"),
    ("edward", "dalia", "s", ["TLE", "BSS"], "LC-12"),
    ("samantha", "dalia", "l", ["TLE"], ""),
    ("edward", "nathaniel", "s", ["TLE", "BSS"], ""),
    ("samantha", "nathaniel", "l", ["TLE"], ""),
    ("dalia", "maxim", "s", ["BSS"], ""), ("david", "maxim", "s", ["BSS"], ""),
    ("dalia", "minho", "s", ["BSS"], ""), ("david", "minho", "s", ["BSS"], ""),
    ("dalia", "zephyr", "s", ["BSS"], ""), ("david", "zephyr", "s", ["BSS"], ""),
    ("dalia", "zoe", "s", ["BSS"], ""), ("david", "zoe", "s", ["BSS"], ""),
    ("dalia", "sebastian", "s", ["BSS"], ""), ("david", "sebastian", "s", ["BSS"], ""),
    ("dalia", "orion", "s", ["BSS"], ""), ("david", "orion", "s", ["BSS"], ""),
]
# Superseded parent links, kept visible (never drawn as live lines).
SUPERSEDED_EDGES = [
    ("ethan", "katherine", "l", ["TCD-040"], "Ethan as biological father superseded; social/naming role POSSIBLE"),
]
# Unions (spouse / co-parent), with the layer they belong to.
UNIONS = [
    ("aracelia", "jackson", "LEGAL", "l", ["TLE"]),
    ("lucia", "tobias", "LEGAL", "s", ["BSS", "CB"]),
    ("michelle", "tobias", "BIO", "c", ["TCD-040"]),
    ("alistair_l", "rowena", "LEGAL", "s", ["BSS"]),
    ("dalia", "david", "LEGAL", "x", ["BSS", "CB"]),
    ("edward", "samantha", "LEGAL", "x", ["TLE"]),
]

# ------------------------------------------------------------------ conflict ledger
# (id, claim, source A, source B, higher-authority evidence, current status code, status text, what would need to change)
CONFLICTS = [
    ("LC-01", "Melena’s eye colour",
     "Beta: “Lockwood amber eyes,” shared by Cordelia. F2025 also has amber.",
     "BSS: “eyes as green as emeralds,” a Hastings trait. CB: emerald. 3SL: green. 31–39: green, Tobias’s eyes “the same shade.” IL repeats BSS.",
     "Beta controls FTE prose (TCD-001). No ruling on which book changes.",
     "x", "CONFLICT", "An author ruling on the colour, naming which manuscript revises (Beta or 3SL)."),
    ("LC-02", "Aracelia’s surname and house",
     "Beta letter: “Aracelia Meson Mignonette.” BSS: “Aracelia Meson Mignonette Hastings.” TLE: “Aracelia Mignonette Hastings.”",
     "31–39: “Empress Aracelia Lockwood.”",
     "The Beta’s styling controls the drafted page. No ruling on her house; WTR, BSS and TLE all put her in the Hastings line.",
     "x", "CONFLICT (name) · house Hastings SUPPORTED", "A ruling on her full styled name and house; then the 31–39 line is revised."),
    ("LC-03", "Lucia’s birth year",
     "BSS: born 2047 (47 at her death on 7 Sept 2094).",
     "TLE: born 26 Oct 2055, elder twin of Charlotte, to Aracelia (17) and Jackson Harper.",
     "None. TCD-010: no existing timeline controls chronology. Both files give Aracelia’s birth as 2038, so BSS’s 2047 would make Aracelia nine at Lucia’s birth.",
     "x", "CONFLICT", "The new canonical Remnian timeline (TCD-010) fixes Aracelia’s and Lucia’s births together."),
    ("LC-04", "Eden’s generation and reign",
     "BSS 2073: Empress Eden “becoming a grandmother” at Elias’s birth. BSS 2076: Lucia’s decree issued “with the blessing of Empress Eden.”",
     "BSS 2091: “Eden Genesis has been deceased for decades,” Aracelia’s reign “long-established.” TLE and WTR: Eden → Aracelia → Lucia → Elias (Eden is Elias’s great-grandmother).",
     "TCD-032 has Aracelia reigning while Elias built the Thorne life as an adult; it doesn’t date her accession.",
     "x", "CONFLICT", "A ruling on when Aracelia acceded and when Eden died. BSS’s 2073 and 2076 Eden lines, or its 2091 line, then change."),
    ("LC-05", "Melena’s great-grandmother",
     "F2025: a Tournament law signed by “Empress Caliane Azira Hastings – Melena’s great-grandmother.”",
     "TLE, WTR: Eden is Aracelia’s mother, so Eden holds that place.",
     "None in this session. The Beta isn’t available here, so whether it keeps the Caliane line is unchecked.",
     "x", "CONFLICT (Caliane LEGACY unless the Beta keeps her)", "Check the Beta’s Tournament-law passage. If it names Caliane, she becomes CURRENT DRAFTED TEXT and Eden’s place needs a ruling."),
    ("LC-06", "Imperial succession law",
     "WTR: strictly matrilineal Hastings succession; the Crown named Elias heir after Lucia’s death to protect its image. 31–39: a Privy Council pushes Elias into the role.",
     "BSS: Lucia’s 2076 decree lets daughters keep their place ahead of younger brothers. TLE: in 2055 Aracelia jumps her elder brother “due to having children before her brother”; the 2063 list runs branch by branch.",
     "TCD-032: Elias is elevated to Crown Prince after Lucia’s death. Beta: Melena is second in line. Neither states the law.",
     "x", "CONFLICT (the law) · positions CANON / DRAFTED", "A ruling on the succession law in force at FTE, and on whether Lucia’s decree exists."),
    ("LC-07", "Which house the throne passes through",
     "BSS: Elias’s birth “shifts the royal succession from the House of Hastings to the House of Lockwood”; a fused Hastings–Lockwood crest.",
     "WTR: a matrilineal Hastings line through Elias. 31–39: the Empress herself is “Aracelia Lockwood.”",
     "Beta: the heirs are Lockwoods (“the Lockwood second-in-line”). TCD-040 names Lucia “Hastings-Lockwood.”",
     "x", "CONFLICT (dynastic house) · children’s surname DRAFTED", "A ruling on the dynastic house name for Lucia’s children and the Crown."),
    ("LC-08", "Was Katherine’s birth public?",
     "BSS: a “highly publicized and controversial birth,” a treason decree, a 2091 Sanctum suppression order, a “legally protected identity.” CB: “whispered scandals.”",
     "WTR: “a lineage no one dared to say out loud.” 31–39: Dalia was one of three people who knew about Michelle and Tobias. Beta: no character treats Katherine as a known scandal.",
     "TCD-059 leaves initial publicity OPEN.",
     "o", "OPEN (sources conflict)", "An author ruling on initial publicity, before any character reacts to the Nicholas name on-page (IV.12)."),
    ("LC-09", "Elias’s titles",
     "BSS: “Crown Prince of Remnia, Duke of Somnoria” from his birth in 2073.",
     "TCD-032: elevated to Crown Prince after Lucia’s death.",
     "TCD-032 (CANON).",
     "c", "Crown Prince from Lucia’s death CANON · from birth SUPERSEDED · Duke of Somnoria SUPPORTED", "Nothing for “Crown Prince.” Duke of Somnoria waits on LC-10."),
    ("LC-10", "Does the Remnian public know Somnoria exists?",
     "BSS: a televised address gives the heir the “traditional title of Duke of Somnoria … fostering relations with the neighboring empire of Somnoria.” IL repeats it.",
     "Beta ch. 2: Melena believes “There’s nothing outside of Remnia anymore.” 31–39: Cordelia says Elias “vanished into a foreign country.”",
     "TCD-016: awareness varies by class, institution and time; Remnia’s case isn’t ruled.",
     "o", "OPEN", "A ruling on public knowledge of Somnoria before any Remnian character names it on-page again (IV.22)."),
    ("LC-11", "London Town’s royal house",
     "WTR: King William and Queen Dalia Augustine.",
     "CB: Crown Princess Dalia and Prince Consort David Augustine. BSS: Queen Dalia from 30 June 2090, styled “Dalia Clementine Lexington Kinross,” consort David Augustine. 31–39: “the Queen of London Town.” TLE: House of Kinross, “what will later become the House of Augustine.”",
     "TCD-041: the Crown directly controls London Town, so whoever reigns there rules under it. Beta: the four brothers are Augustines.",
     "x", "CONFLICT", "A ruling on who reigns in London Town at FTE, Dalia’s consort, and the house name."),
    ("LC-12", "Dalia’s father and the king before Nathaniel",
     "TLE 2038: Dalia born to Queen Samantha and King Edward Kinross. BSS: Maxim honours his maternal grandfather “King Edward XVIII.”",
     "TLE 2058: Nathaniel becomes King “following the death of King Brenton,” while Samantha abdicates to her son.",
     "None.",
     "x", "CONFLICT (inside TLE) · Edward SUPPORTED", "Timeline ruling; Brenton’s relationship to Samantha stated or dropped."),
    ("LC-13", "Richard’s birth year",
     "TLE: born 3 Sept 2024, Eden’s first child (36 in 2060).",
     "BSS: “Prince Richard David Elliot Hastings (55)” in 2094, so about 2039.",
     "TCD-010.", "x", "CONFLICT", "Canonical timeline."),
    ("LC-14", "Tobias’s birth vs his parents’ ages",
     "TLE: born 2 Aug 2035 at Lockwood Manor, Highcrest; “Head of the Lockwood House” from birth.",
     "BSS: Duke Alistair Lockwood (67) and Duchess Rowena (64) in 2094, so born about 2027 and 2030. Alistair would be about eight at Tobias’s birth, and still heads the house in 2094.",
     "TCD-010.", "x", "CONFLICT", "Canonical timeline: one of the dates moves."),
    ("LC-15", "Melena’s birth year and age",
     "BSS: born 9 Sept 2076; 17 when Lucia dies; “turns 19” on 9 Sept 2095.",
     "BSS (same file): “19, turning 20” at the start of 2095. CB: 2077. 31–39: nineteen once, twenty twice. F2025: turns twenty on Examination day.",
     "The Beta doesn’t state her age (IV.14).",
     "x", "CONFLICT", "A ruling on her birth date, checked against the Tournament age rule."),
    ("LC-16", "How and where Lucia died",
     "BSS: 7 Sept 2094, 2:41 AM, at the Imperial Palace; a “nighttime medical crisis.”",
     "31–39 (and F2025): a car accident, with Melena on a call with her.",
     "None. The Content Master’s IV.11 had “cause of death SUPPORTED” from 31–39 alone; corrected to CONFLICT.",
     "x", "CONFLICT", "A ruling on cause of death."),
    ("LC-17", "Where Tobias is in 2094–95",
     "31–39: Tobias dies six months after Lucia (officially a fall).",
     "BSS: guardianships for Melena, Cordelia and Louis go to others on 11 Sept 2094, two days after Lucia’s death; his parents petition for Elias in July 2094, while Lucia is alive. BSS never places Tobias after 2081.",
     "None. The Content Master: dead before FTE (SUPPORTED).",
     "o", "OPEN", "Timeline placement of Tobias’s death, and whether he was alive and passed over when the guardianships were granted."),
    ("LC-18", "Ethan’s surname and role",
     "WTR: “Ethan Medina gave Katherine his name.”",
     "TLE: “Ethan Nicholas,” Head of the Nicholas House, born 2035. F2025: “her father, Ethan,” an academic. BSS: “Medina” honours Michelle’s maternal grandmother.",
     "TCD-040: Ethan as biological father is superseded.",
     "x", "Biological LEGACY / SUPERSEDED · social role POSSIBLE · surname CONFLICT", "A ruling on whether Ethan exists in the current generation, and in what role."),
    ("LC-19", "London Town’s order of succession",
     "BSS 2090 list: Maxim, Minho, Sebastian, Zephyr, Zoe, Arielle, the unborn son.",
     "BSS birth entries: Zephyr and Zoe (2075) are older than Sebastian (2076); the twins are “sixth and seventh in line”; Sebastian is “fifth in line to the throne of Remnia.”",
     "Nathaniel’s 2090 decree (BSS) keeps daughters in birth order. No ruling.",
     "x", "CONFLICT (inside BSS)", "A ruling on London Town’s line, and on whether “throne of Remnia” in the Sebastian entry means London Town’s."),
    ("LC-20", "Dukedom titles vs provincial rule",
     "BSS: Lucia is “Duchess of Zenithia”; Melena “Duchess of Avalon”; Tiran’s father is Duke Alistair Blackwood “of London Town.”",
     "CB: Blackwood Dukedom of Zenithia. Beta: Governor Anise of Zenithia. WTR: Countess Montclair. TLE’s seventeen provinces include no Avalon.",
     "TCD-041: provincial leaders’ titles may vary. Zenithia’s leadership is already a CONFLICT (IV.3).",
     "x", "CONFLICT", "A ruling on Zenithia’s leadership, and on whether royal dukedoms are honorific (TLE’s Dukedom Act)."),
    ("LC-21", "The parents’ elements",
     "Beta ch. 8: Lucia was “one of the most powerful” Frosts; Cordelia inherited Frost; Melena “took after their father — fire.”",
     "31–39 Mirror (and F2025): Tobias a Frost, Lucia a Flamer.",
     "Beta (TCD-001).",
     "d", "Beta CURRENT DRAFTED TEXT · 31–39 needs revising", "Nothing in the Beta; the 31–39 lines are rewritten. Neither side says where Katherine’s capacity comes from (TCD-049)."),
]

# ------------------------------------------------------------------ open items (not conflicts, but unresolved and needing working space)
OPEN_ITEMS = [
    ("O-01", "Birth order of the sisters", "Both supporting sources put Katherine first: BSS has 14 July 2076 vs 9 Sept 2076; CB has 2076 vs 2077. Not ruled. Any succession or legitimacy argument that turns on “eldest” depends on it.", "s", ["BSS", "CB"]),
    ("O-02", "Katherine’s legal status", "Legitimate or not, her name at law, royal or not. TCD-040 says biology doesn’t settle it; TCD-059 says Lucia originated her legal erasure without saying what the law now records.", "o", ["TCD-040", "TCD-059"]),
    ("O-03", "Aracelia’s spouse and Lucia’s father", "Only TLE names him (Duke Jackson Harper). No later source confirms or replaces him.", "l", ["TLE"]),
    ("O-04", "Lucia’s sisters", "TLE gives Lucia a twin (Charlotte) and a sister (Elaine). BSS mentions “Charlotte’s oldest” and “Elaine’s oldest” in the cousins’ circle, without saying how they’re related.", "s", ["TLE", "BSS"]),
    ("O-05", "Arielle’s parent", "“Eldest daughter of a son of the crown”; Dalia’s niece. Which son isn’t named.", "o", ["BSS"]),
]

# ------------------------------------------------------------------ duplicate-person and name-variant checks
NAME_CHECKS = [
    ("NV-01", "Alistair", "Duke Alistair Lockwood (BSS, Tobias’s father) · Duke Alistair Blackwood “of London Town” (BSS, Tiran’s father) · High Chancellor Alistair Blackwood (TLE, Year 2 ER)", "Kept as three people. No source makes any two of them one person; Lockwood and Blackwood aren’t merged on spelling."),
    ("NV-02", "Celeste", "Tobias’s late aunt (BSS; Katherine’s middle name) · Lady Celeste Blackwood (BSS, alive 2072) · Celeste Morningstar (TLE, Dawner Regnant 2064)", "Kept apart. No source connects them."),
    ("NV-03", "Ethan", "Ethan Medina (WTR) · Ethan Nicholas (TLE) · “her father, Ethan” (F2025)", "One slot with a surname conflict (LC-18): each is Katherine’s father figure in its own generation."),
    ("NV-04", "Aracelia", "Meson Mignonette · Mignonette Hastings · Meson Mignonette Hastings · Lockwood", "One person (LC-02)."),
    ("NV-05", "Eden", "Eden Genesis Hastings · Eden Mignonette · “Migonnette” · Eden Genesis", "One person; spelling and house drift inside TLE."),
    ("NV-06", "Jackson", "Duke Jackson Harper · “Duke Jackson Hastings” (TLE, once)", "One person; TLE spelling drift."),
    ("NV-07", "Richard", "Richard David Elliot (TLE) · Richard David Elliot Hastings (BSS)", "One person; birth year in conflict (LC-13)."),
    ("NV-08", "Louis", "Louis Reginald Henry · “Louis Reginal Henry” (BSS, once)", "One person; typo."),
    ("NV-09", "Thorne", "Lord Commander Gareth Thorne (TLE, Old Prosperity) · General Gareth Thorne (WTR) · Professor Alexander Thorne (Elias’s alias, TCD-032)", "No connection established. Don’t infer one."),
    ("NV-10", "Zephyr", "Elder Zephyr Windrider (TLE, Dawners) · the Factions file’s 2092 survivor Zephyr Windrider · Zephyr Augustine", "Not the same person (IV.5 guardrail)."),
    ("NV-11", "Elias", "Flight Regnant Elias Windwalker (TLE, 2063) · Elias Lockwood", "Not connected."),
    ("NV-12", "Harper", "Duke Jackson Harper (TLE) · Elite Regnant Annemarie Harper (TLE 2061; BSS 2091)", "No family link stated."),
    ("NV-13", "Melena / Beatrix", "Alexandria Melena Mignonette · Madeleine Beatrix · Melena Elizabeth Beatrix Lockwood", "Possible namesakes; no source says so."),
    ("NV-14", "“Lockwood” in Augustine names", "“Princess Zoe Dalia Lockwood Augustine” · “Orion Nathaniel Lockwood Augustine” (BSS)", "No Lockwood parent is given in the Augustine line. Flagged, not inferred."),
]

# ------------------------------------------------------------------ rejected or downgraded old claims
REJECTED = [
    ("R-01", "Katherine as “Katherine Lockwood”", "F4", "The Beta names her Nicholas; TCD-040 doesn’t make her a Lockwood by law.", "LEGACY / SUPERSEDED"),
    ("R-02", "Katherine named heir apparent, Melena heir presumptive, after the Empress dies (Book 3 plan)", "F4", "A post-FTE legacy plot (TCD-022); biology doesn’t make Katherine an heir (TCD-040).", "LEGACY / SUPERSEDED · not imported"),
    ("R-03", "Melena finds “the bloodline suppression docs” bearing Tobias’s signature", "F4", "TCD-058: no established suppression. TCD-059: Tobias isn’t the architect. TCD-050 stages the reveal.", "LEGACY / SUPERSEDED"),
    ("R-04", "Ethan as Katherine’s biological father", "TLE generation (audit), WTR, F2025", "TCD-040.", "SUPERSEDED · social role POSSIBLE"),
    ("R-05", "Lucia as Katherine’s mother", "Earlier lineage generations (audit)", "TCD-040. Not in the uploaded TLE text, which ends in 2066.", "SUPERSEDED"),
    ("R-06", "Elias as Crown Prince from birth", "BSS", "TCD-032: elevated after Lucia’s death.", "Downgraded: SUPERSEDED on timing"),
    ("R-07", "Empress Eden reigning in 2073–76", "BSS", "TCD-032 and BSS’s own 2091 entry.", "Downgraded to CONFLICT (LC-04)"),
    ("R-08", "Tobias “Head of the Lockwood House” from birth", "TLE", "BSS has his father as Duke in 2094.", "LEGACY"),
    ("R-09", "Katherine’s birth was “highly publicized”", "BSS (repeated in IL)", "TCD-059 leaves it open; the Beta shows no scandal.", "Not adopted: OPEN (LC-08)"),
    ("R-10", "Melena as “heir presumptive to London Town’s throne”", "F2025", "Legacy prose. The Beta has her second in line to the imperial throne.", "LEGACY"),
    ("R-11", "Aracelia becomes heir “due to having children before her brother”", "TLE", "Unique to the earlier pool; no later source repeats it.", "LEGACY"),
    ("R-12", "The Imperial Lineage as a source", "IL", "Not audited. Every lineage claim the Content Master quotes from it appears word for word in BSS, which is audited; citations move to BSS.", "Not imported"),
]

# ------------------------------------------------------------------ succession lanes (positions, never inferred from parentage)
SUCC_CURRENT_IMPERIAL = [
    ("Reigning", "Empress Aracelia", "Reigning at FTE", "d", ["BETA"]),
    ("1", "Elias, Crown Prince", "Elevated after Lucia’s death; missing from Remnia at FTE’s opening", "c", ["TCD-032", "TCD-013"]),
    ("2", "Melena", "“The Lockwood second-in-line”", "d", ["BETA"]),
    ("3", "Cordelia", "Announced third in line at birth (2079)", "s", ["BSS"]),
    ("4", "Louis", "Announced fourth in line at birth (2081)", "s", ["BSS"]),
    ("5+", "Hastings collateral lines", "Not ruled. TLE’s 2063 list orders them branch by branch (LEGACY).", "o", ["TLE"]),
    ("—", "Katherine", "Not in the recorded line. Lucia/the Crown originated her dynastic erasure (TCD-059); any claim at law isn’t ruled (TCD-040).", "o", ["TCD-040", "TCD-059"]),
    ("Law", "The rule that orders this line", "Not ruled (LC-06).", "x", ["WTR", "BSS", "TLE", "3139"]),
]
SUCC_CURRENT_LONDON = [
    ("Reigning", "Queen Dalia", "Since 30 June 2090 (BSS); “the Queen of London Town” (31–39). CB calls her Crown Princess.", "x", ["BSS", "3139", "CB", "WTR"]),
    ("1", "Maxim, Crown Prince of London Town", "2090 list", "s", ["BSS"]),
    ("—", "Minho", "Relinquished 3 March 2091", "s", ["BSS"]),
    ("—", "Sebastian", "Relinquished 9 April 2095", "s", ["BSS"]),
    ("?", "Zephyr, Zoe, Arielle, Orion", "Order in conflict inside BSS (LC-19)", "x", ["BSS"]),
]
SUCC_HISTORY = [
    ("2024", "Imperial", "Richard born “Crown Prince of Remnia,” heir apparent", "l", ["TLE"]),
    ("2038", "London Town", "Dalia born first in line to the Kinross throne", "l", ["TLE"]),
    ("2039", "London Town", "Nathaniel born heir apparent; Dalia heir presumptive (“The Grand Princess”)", "l", ["TLE"]),
    ("2055", "Imperial", "Aracelia becomes Eden’s heir apparent over Richard; Lucia “The Princess Imperial”", "l", ["TLE"]),
    ("2058", "London Town", "Nathaniel King; Dalia his heir apparent", "l", ["TLE"]),
    ("2063", "Both", "Succession announcements: Imperial line Eden, Aracelia, Lucia, Charlotte, Elaine, Richard, Olympia, Estelle, Madeleine, Aveline, Isabella, Victoria, Alexandria, Amalia, Evangeline; London Town line Nathaniel, then his sisters Lauren, Angelica, Dalia, Fallon", "l", ["TLE"]),
    ("2073", "Imperial", "Elias born second in line after Lucia; succession “shifts” to House Lockwood", "s", ["BSS"]),
    ("2076", "Imperial", "Lucia’s decree: daughters keep their place ahead of younger brothers; Melena second in line", "s", ["BSS"]),
    ("2076", "Imperial", "Lucia’s legal action: Katherine has no claim and no place in the line", "s", ["BSS"]),
    ("2079 · 2081", "Imperial", "Cordelia third; Louis fourth", "s", ["BSS"]),
    ("2090", "London Town", "Nathaniel abdicates to Dalia; daughters keep birth order; Arielle placed before Dalia’s unborn son", "s", ["BSS"]),
    ("2091 · 2095", "London Town", "Minho, then Sebastian, relinquish their places", "s", ["BSS"]),
    ("After Lucia’s death", "Imperial", "Elias elevated to Crown Prince", "c", ["TCD-032"]),
    ("Book 3 plan", "Imperial", "Katherine named heir apparent", "l", ["F4"]),
]

# ------------------------------------------------------------------ comparison with the unaudited Imperial Lineage (via Content Master quotes only)
COMPARE_IL = [
    ("Melena’s eyes green, “associated with the Hastings lineage”; Elias’s golden Lockwood eyes", "Found in BSS (2073 and 2076 entries)", "Re-sourced to BSS"),
    ("Lucia’s decree at Melena’s birth: daughters keep their place", "Found in BSS (2076)", "Re-sourced to BSS"),
    ("A “highly publicized and controversial birth” followed by a decree", "Found in BSS (2076)", "Re-sourced to BSS"),
    ("“Duke of Somnoria” as the heir apparent’s traditional title", "Found in BSS (2073)", "Re-sourced to BSS"),
]

# ------------------------------------------------------------------ lane D: one working block per decision (id, the specific question, minimum ruled lines)
DECISIONS = [
    ("LC-01", "Amber or green? Name the colour, the manuscript that revises, and every page that carries the other colour (Melena and Cordelia in the Beta; Melena in 3SL).", 6),
    ("LC-02", "What is the Empress’s full styled name, and which house is she? If Hastings, the 31–39 “Aracelia Lockwood” line is revised.", 6),
    ("LC-03", "Fix Lucia’s birth year against Aracelia’s (2038 in both timelines). If Lucia was born in 2047, Aracelia’s year moves; if in 2055, Lucia dies at 38 or 39, not 47.", 6),
    ("LC-04", "When did Aracelia take the throne, and when did Eden die? Either Eden blessed Lucia’s 2076 decree, or she had been dead “for decades” by 2091. Not both.", 6),
    ("LC-05", "Does Empress Caliane exist? Check the Beta’s Tournament-law passage. If she stays, say which of Melena’s lines she belongs to and when she reigned.", 6),
    ("LC-06", "Write the succession law in force at FTE: matrilineal, eldest child regardless of sex, male preference amended by Lucia in 2076, or another rule. Then check that it still puts Elias first and Melena second.", 8),
    ("LC-07", "After Lucia’s marriage, is the dynasty Hastings or Lockwood? Name the throne’s house, and say whether Aracelia is ever styled Lockwood.", 6),
    ("LC-08", "Was Katherine’s birth ever public? If it was (BSS), what do ordinary Remnians remember, and why does no one in the Beta treat her as a scandal? If it never was, who knew, starting from Dalia and the three people of 31–39?", 8),
    ("LC-09", "Keep or drop “Duke of Somnoria” once LC-10 is settled. If it stays, who in Remnia understands what the title names?", 5),
    ("LC-10", "What does the Remnian public know about Somnoria? Reconcile Melena’s “nothing outside of Remnia,” Cordelia’s “foreign country,” and a publicly announced Duke of Somnoria.", 6),
    ("LC-11", "Who reigns in London Town at FTE, who is Dalia’s consort, and what is the house called: Queen Dalia with Prince Consort David, King William and Queen Dalia, or Crown Princess Dalia?", 6),
    ("LC-12", "Who was Dalia’s father, and who was King Brenton? Keep Edward (TLE, BSS), or explain Brenton.", 5),
    ("LC-13", "Richard’s birth year: 2024 (TLE) or about 2039 (BSS). It decides whether he is Aracelia’s elder brother by fourteen years or her younger brother.", 5),
    ("LC-14", "Tobias’s birth year against his parents’ ages: move Tobias (TLE 2035), or move Alistair and Rowena (BSS: 67 and 64 in 2094).", 5),
    ("LC-15", "Melena’s birth date (BSS 9 Sept 2076, or CB 2077), checked against the Tournament age rule and Katherine’s twenty.", 6),
    ("LC-16", "How did Lucia die: a nighttime medical crisis at the palace (BSS), or a car accident while on a call with Melena (31–39)? List the drafted scenes that change.", 6),
    ("LC-17", "When did Tobias die, and was he alive when the guardianships were granted? If he was, why did the Crown pass him over?", 6),
    ("LC-18", "Does Ethan exist in the current generation? If so: his surname, his tie to Michelle, and what “gave Katherine his name” means now that “Medina” honours Michelle’s grandmother.", 6),
    ("LC-19", "London Town’s order of succession after 2090, by the 2090 decree’s own rule. Zephyr and Zoe were born before Sebastian.", 5),
    ("LC-20", "Are royal dukedoms (Zenithia, Avalon, Alleia, Meridion) honorific titles or provincial offices? Then reconcile Lucia’s Duchy of Zenithia with Governor Anise and a Blackwood dukedom.", 6),
    ("LC-21", "List the 31–39 Mirror lines to revise so that Tobias carries Fire and Lucia Frost, as the Beta has them.", 5),
    ("O-01", "Is Katherine older than Melena? If yes, say what that does and doesn’t change. Biology alone gives her no place (TCD-040).", 6),
    ("O-02", "Write Katherine’s legal status as Remnian law records it: legitimacy, name at law, and whether she is royal.", 8),
    ("O-03", "Who is Aracelia’s husband and Lucia’s father? Keep Duke Jackson Harper (TLE only), or replace him.", 5),
    ("O-04", "Who are Lucia’s sisters? Confirm Charlotte (her twin) and Elaine, or drop them; BSS’s “Charlotte’s oldest” and “Elaine’s oldest” depend on it.", 5),
    ("O-05", "Arielle Monet Kinross: whose daughter is she? Name the “son of the crown.”", 5),
]
