"""The settled Remnian lineage, 2026-10-11.

Built from Dany's answers in the "Remnian Lineage: Suggestions Workbook" (Claude Doc,
rev 738), the four follow-up answers given the same day, and a check against the
3 Shadowmere Lane outline (Route B, 42 chapters + Epilogue).

Every record line carries a tag saying where the decision came from:
  Y  your call: your own words in the workbook, or one of today's four answers
  A  agreed: my suggestion, which you marked Agree
  S  source: kept as the source has it (you agreed)
  C  canon: a TCD ruling
  T  3SL: what the 3SL outline shows
  O  open: still yours to decide
"""

ANCHOR = ("Lucia dies on 7 September 2094: about three weeks before 3SL opens, "
          "and two years before FTE opens on 9 September 2096.")

TAGS = {
    "Y": ("Your call", "Your own words in the workbook, or one of the four answers you gave today."),
    "A": ("Agreed", "My suggestion, which you marked Agree."),
    "S": ("Source", "Kept as the source has it; you agreed."),
    "C": ("Canon", "A Canon Decision Log ruling."),
    "T": ("3SL", "What the 3SL outline shows."),
    "O": ("Open", "Still yours to decide."),
}

# Eye colours carry the lineage's tells, so the chart shows them as swatches.
EYES = {"emerald": "Lockwood emerald", "gold": "Hastings gold", "violet": "violet"}

# ---------------------------------------------------------------- the record
# (house heading, intro, [ (person, born/died line, [ (field, value, tag) ]) ])
RECORD = [
    ("The imperial house: Mignonette, then Hastings, then Lockwood",
     "The throne takes its consort's name: Mignonette becomes Hastings through Stephen, and Hastings "
     "becomes Lockwood through Tobias. Hair and eyes now sort cleanly: crimson hair and gold eyes "
     "come from the Hastings side, and emerald eyes come from the Lockwoods.",
     [
         ("Eden Genesis Caliane Azira Mignonette", "Founding Empress · Year 1 ER · d. c. 2080", [
             ("Full name", "Eden Genesis Caliane Azira Mignonette; Hastings by marriage", "Y"),
             ("On the throne", "HIM Eden Genesis Caliane Azira, founding Empress of Remnia", "Y"),
             ("F2025's “Empress Caliane Azira Hastings”", "Eden, by her middle names and married name", "Y"),
             ("Spouse", "Stephen Abraham Hastings, Emperor Consort", "S"),
             ("Children", "Richard (2024), Madeleine (2028), Victoria (2035), and the twins Aracelia and Alexandria (2038)", "S"),
             ("Death", "c. 2080, after blessing Lucia's 2076 succession decree", "A"),
             ("To Elias", "Great-grandmother", "A"),
         ]),
         ("Stephen Abraham Hastings", "Emperor Consort", [
             ("Role", "Emperor Consort; Flamer Regnant until 2062", "S"),
             ("House", "The dynasty takes his name, which sets the precedent Tobias repeats", "A"),
         ]),
         ("Richard David Elliot Hastings", "b. 3 Sept 2024", [
             ("Title", "Crown Prince at birth; displaced in 2055 by his younger sister Aracelia", "S"),
             ("Family", "m. Princess Ember; Olympia (2058), Estelle (2059)", "S"),
             ("2094", "70 years old. Petitions for Elias, is granted Louis, and leads the Hastings faction", "A"),
         ]),
         ("Madeleine Beatrix", "b. 15 July 2028", [
             ("Family", "m. Lord Felix D'Arcy; Aveline (2060), Isabella (2063), Arabella (2064), raised in Verdant. "
                        "The D'Arcys are the imperial family's Verdant branch", "A"),
         ]),
         ("Victoria Cassiopeia", "b. 22 March 2035", [
             ("Family", "Flamer; m. Lord Adrian Wells; Fiona (2065)", "S"),
             ("Title", "The Princess Imperial in 2063; the title passes to whoever is next in line", "A"),
         ]),
         ("Aracelia Meson Mignonette Hastings", "b. 7 Oct 2038 · Empress from c. 2080", [
             ("Name", "Aracelia Meson Mignonette Hastings. F2025's “Empress Aracelia Lockwood” is a caption error", "A"),
             ("Titles", "Duchess of Meridion; heir from 2055 over Richard; Empress from c. 2080", "A"),
             ("Element", "Frost", "S"),
             ("Spouse", "Duke Jackson Harper of Zenithia, married 9 Sept 2060", "A"),
             ("Children", "Lucia and Charlotte (26 Oct 2055, born before the wedding), Elaine (2056), Arianne (2066)", "S"),
             ("Ages", "57 when Lucia dies; 58 at FTE, when she is thinking of abdicating", "A"),
         ]),
         ("Jackson Harper", "Duke of Zenithia", [
             ("Role", "Lucia's father; styled “The Crown Prince” on marrying Aracelia", "S"),
             ("Province", "Zenithia, which is why Lucia is Duchess of Zenithia", "A"),
             ("Sister", "Annemarie Harper, Elite Regnant from 2061 and still in 2091", "A"),
         ]),
         ("Alexandria Melena Mignonette", "b. 7 Oct 2038", [
             ("Title", "Duchess of Alleia; Aracelia's younger twin", "S"),
             ("Family", "m. Lord Clyde Hastings, who dies in Nov 2096, during FTE; Amalia (2062), Evangeline (2063)", "S"),
             ("Namesake", "Melena is named after her great-aunt Alexandria Melena", "Y"),
         ]),
         ("Lucia Noelle Marie Hastings-Lockwood", "b. 26 Oct 2055 · d. 7 Sept 2094", [
             ("Born", "26 Oct 2055, three minutes ahead of her twin Charlotte", "S"),
             ("Titles", "The Princess Imperial; Crown Princess; Duchess of Zenithia (honorific)", "A"),
             ("Spouse", "Tobias Lockwood, Prince Consort, in a match Eden arranged to bind House Lockwood", "A"),
             ("Children", "Elias (2073), Melena (2076), Cordelia (2079), Louis (2081)", "S"),
             ("Element", "Frost", "A"),
             ("Eyes, hair", "Hastings gold eyes; crimson Hastings hair", "Y"),
             ("Shadowmere", "Used the route c. 2074–2076; Selah knew her (3SL ch. 22–23)", "A"),
             ("Succession decree", "2076: birth order counts, regardless of sex", "A"),
             ("Katherine", "Originates her erasure", "C"),
             ("Death", "At 38, in a car accident at night, on a call with Melena. "
                       "“Nighttime medical crisis” is the palace statement", "A"),
         ]),
         ("Charlotte, Elaine and Arianne Hastings", "Lucia's sisters", [
             ("Charlotte Elizabeth Anai", "b. 26 Oct 2055, three minutes after Lucia; children by 2090. "
                                          "The Hastings faction's living alternative to Lucia's line", "A"),
             ("Elaine Marie", "b. 21 Nov 2056; children by 2090", "S"),
             ("Arianne Jessamine", "b. 2 April 2066 (the entry's “Amelia Joy” is a slip)", "A"),
         ]),
     ]),
    ("House Lockwood",
     "Tobias's father is now Sawyer, which keeps him apart from Duke Alistair Blackwood. "
     "That matters in 3SL, where “Blackwood” is said right next to “Melena Lockwood” (ch. 23).",
     [
         ("Sawyer and Rowena Lockwood", "b. c. 2007 and c. 2010", [
             ("Name", "Duke Sawyer Lockwood (BSS's “Alistair” renamed)", "Y"),
             ("Ages", "87 and 84 in 2094", "A"),
             ("2094", "Petition for Elias's guardianship on 2 July; granted Cordelia on 11 Sept", "S"),
             ("Sawyer's sister", "Celeste, who married into the Nicholas house", "Y"),
         ]),
         ("Celeste Nicholas, born Lockwood", "d. before 2076", [
             ("Who", "Sawyer's sister: Tobias's aunt", "Y"),
             ("Marriage", "Married into the Nicholas house of Meridion; mother of Ethan Nicholas", "Y"),
             ("Name", "Katherine's middle name honours her", "S"),
             ("Not", "Lady Celeste Blackwood, Tiran's mother, who is alive in 2072", "A"),
         ]),
         ("Tobias Lockwood", "b. 2 Aug 2035 · d. c. March 2095", [
             ("Born", "Lockwood Manor, Highcrest; heir to the house at birth", "A"),
             ("Role", "Prince Consort; the throne's house becomes Lockwood through him", "A"),
             ("Element", "Fire", "A"),
             ("Eyes", "Lockwood emerald. “You have my eye color” is literally true for Melena", "Y"),
             ("Cousin", "Ethan Nicholas, son of his aunt Celeste; both born in 2035", "Y"),
             ("Michelle", "Met during her Board year (c. 2070–71); together again from c. 2075, through Lucia's pregnancy with Melena", "A"),
             ("Katherine", "Visits Old Prosperity and teaches her the imperial bow. "
                           "His signature on the “bloodline suppression docs” is his non-acknowledgment", "A"),
             ("Godfather", "To Zoe and Orion Augustine, who carry “Lockwood” in their names", "A"),
             ("After Lucia", "Signs custody of his children away (11 Sept 2094)", "A"),
             ("Death", "About six months after Lucia. He stops eating, then falls on wet stairs; "
                       "the court calls it an accident, and Melena believes it was suicide", "A"),
         ]),
     ]),
    ("Lucia and Tobias's children",
     "Lucia's 2076 decree sets the order by birth, not by sex.",
     [
         ("Elias Louis Alexander Lockwood", "b. 3 Oct 2073", [
             ("Born", "3 Oct 2073; Lucia is seventeen, as Aracelia was", "A"),
             ("Eyes", "Hastings gold, from his mother", "Y"),
             ("Titles", "Prince at birth; Duke of Somnoria; Crown Prince from Lucia's death", "A"),
             ("His Tournament", "Called to the board as King c. 2090, at sixteen", "A"),
             ("At FTE", "Missing from Remnia; Professor Thorne in Somnoria", "C"),
             ("Later", "Forced to return in Book 3", "S"),
             ("3SL", "Lucia's last letter is addressed to him; Melena burns it in ch. 20", "T"),
         ]),
         ("Melena Elizabeth Beatrix Lockwood", "b. 9 Sept 2076", [
             ("Born", "9 Sept 2076. She turns twenty the morning FTE opens", "A"),
             ("Element", "Fire, volatile; she took after Tobias", "S"),
             ("Eyes, hair", "Lockwood emerald eyes, Tobias's (the green that stops Silas in 3SL); crimson Hastings hair", "Y"),
             ("Title", "Duchess of Rovencia, one of London Town's strongest allies. "
                       "It passes to her from Dalia when Dalia becomes Queen in June 2090", "Y"),
             ("Succession", "Second, after Elias", "A"),
             ("Guardians", "Lorelei and Lady Helena's household, from 11 Sept 2094", "S"),
             ("Named for", "Her great-aunt Alexandria Melena", "Y"),
             ("In Shadowmere", "Mira. Remy makes her promise never to say her own name there (3SL ch. 23)", "T"),
         ]),
         ("Cordelia Gwendolyn Marie Lockwood", "b. 2 Sept 2079", [
             ("Element, looks", "Frost from Lucia; amber (Hastings gold) eyes like Elias's; crimson hair like Melena's", "Y"),
             ("Succession", "Third", "S"),
             ("Guardians", "Her Lockwood grandparents, Sawyer and Rowena", "S"),
             ("Later", "“Prepared to take the crown”", "S"),
         ]),
         ("Louis Reginald Henry Lockwood", "b. 14 May 2081", [
             ("Succession", "Fourth", "S"),
             ("Guardian", "Prince Richard, his great-uncle", "S"),
             ("Detail", "Has Lucia's hands", "S"),
         ]),
     ]),
    ("Michelle, Ethan and Katherine",
     "Lucia's legal erasure of Katherine works through a marriage: Michelle marries Ethan Nicholas before "
     "Katherine is born, and he becomes the father on her records. Ethan is Tobias's first cousin, "
     "so the man on the paperwork is family.",
     [
         ("Michelle Nicholas", "b. c. 2050", [
             ("Her Tournament", "Conqueror c. 2070, with the Leadership Board seat that follows", "A"),
             ("Rank", "Lieutenant; undefeated former Captain of the En Guard", "S"),
             ("Tobias", "Met him during her Board year, before his marriage; “tried to make it work for years”", "A"),
             ("Marriage", "Married Ethan Nicholas in early 2076, while pregnant", "A"),
             ("Family", "Her maternal grandmother is the Medina of Katherine's name", "S"),
             ("Since stepping down", "A Sanctum assignment; she trades records for Katherine's Tournament slot", "A"),
             ("Dalia", "One of the three people who knew about her and Tobias", "S"),
         ]),
         ("Ethan Nicholas", "b. 18 Nov 2035", [
             ("Born", "Nicholas Estate, Meridion; head of the Nicholas house; an academic", "S"),
             ("Parents", "Son of Celeste Nicholas, born Lockwood", "Y"),
             ("Role", "Katherine's legal father. Her biological father is Tobias", "C"),
         ]),
         ("Katherine Medina Celeste Nicholas", "b. 14 July 2076", [
             ("Born", "Military Hospital, Old Prosperity; eight weeks before Melena", "S"),
             ("Parents", "Michelle and Tobias; Ethan on her records", "C"),
             ("Names", "Medina for Michelle's grandmother. Celeste for Celeste Nicholas, who is both Tobias's aunt "
                       "and Ethan's mother, so the name reads as innocent on either side", "Y"),
             ("Element", "Registered Frost", "S"),
             ("Surname", "Katherine Nicholas for life, by her own choice, because of her mother. She keeps it after she is "
                         "acknowledged and named heir apparent in Book 3", "Y"),
             ("Rank once acknowledged", "Ahead of Melena, by eight weeks, under Lucia's decree", "A"),
             ("Eyes", "Not set. Emerald would make her Tobias's daughter at a glance", "O"),
         ]),
     ]),
    ("London Town: Kinross, then Augustine",
     "London Town follows the imperial pattern: Kinross becomes Augustine through Dalia's consort.",
     [
         ("Samantha Ruby Kinross", "First Queen of London Town", [
             ("Role", "Founds House Kinross; Eden's adviser; the first to serve as Queen, Queen Regent and Queen Dowager", "S"),
             ("Husbands", "King Edward XVIII, Dalia's father; then King Brenton, who dies in 2058", "A"),
             ("Children", "Lauren (2024), Angelica (2035), Dalia (2038), Nathaniel (2039), Fallon (2040)", "S"),
         ]),
         ("Edward XVIII", "d. c. 2041–2045", [
             ("Role", "King of an old royal line that is older than the Empire; Maxim's grandfather", "A"),
         ]),
         ("Nathaniel Reece Isaiah Kinross", "b. 24 Nov 2039", [
             ("Reign", "King from 2058; abdicates to Dalia on 15 June 2090", "S"),
             ("His rule", "Daughters keep their place by birth order, “as long as they are born to the Queen and Prince Consort”", "S"),
             ("Child", "Arielle", "A"),
         ]),
         ("Arielle Monet Kinross", "The Princess Royal", [
             ("Place", "Nathaniel's daughter, left out by his own rule; Dalia restores her ahead of Orion", "A"),
         ]),
         ("Lauren, Angelica and Fallon Kinross", "Dalia's sisters", [
             ("Lauren Felicity", "b. 2024; the Grand Princess; m. Lord Julian Somerset in 2065 and gave up her place", "A"),
             ("Angelica Demeter, Fallon Valentina", "b. 2035 and 2040", "S"),
         ]),
         ("Dalia Clementine Lexington", "b. 31 Oct 2038 · Queen from 30 June 2090", [
             ("Titles", "Duchess of Camor; Duchess of Rovencia until she becomes Queen, when Rovencia passes to Melena; "
                        "Crown Princess from 2058", "Y"),
             ("Spouse", "David Augustine, Prince Consort", "A"),
             ("Michelle", "Knew about her and Tobias; sat with her after Lucia and Tobias died", "S"),
         ]),
         ("David Augustine", "Prince Consort", [
             ("Family", "Son of Lord Alexander Augustine; nephew of Lord George Augustine", "S"),
             ("House", "London Town's house takes his name", "A"),
         ]),
         ("The Augustine children", "Dalia and David's six", [
             ("Maxim", "b. 7 Sept 2072. Crown Prince; Terrain; refused the PAE three times to protect the succession", "S"),
             ("Minho", "b. 12 Aug 2074. Gave up his place (3 March 2091) to join Old Prosperity; En Guard Captain", "S"),
             ("Zephyr", "b. 7 Sept 2075, six minutes before Zoe. A true Fire/Frost Dyad, registered Frost at birth and "
                        "re-registered Flamer after thirteen. Gave up his place to play for Old Prosperity", "Y"),
             ("Zephyr's eyes", "Emerald, kept as a red herring: readers may wonder whether Tobias is the twins' father. "
                               "He is only their godfather", "Y"),
             ("Zoe", "b. 7 Sept 2075. “Princess Zoe Dalia Lockwood Augustine”; violet eyes; Tobias's goddaughter", "A"),
             ("Sebastian", "b. 15 Aug 2076. Flamer; gave up his place (9 April 2095); has shielded Zephyr's secret for years", "S"),
             ("Orion", "b. 1 Oct 2090. “Orion Nathaniel Lockwood Augustine”; six at FTE; Tobias's godson", "A"),
         ]),
     ]),
    ("Kept separate: House Blackwood and the collateral lines", "", [
        ("House Blackwood", "London Town nobility", [
            ("Duke Alistair Blackwood", "Of London Town; namesake grandson of High Chancellor Alistair Blackwood, who served Eden in Year 2", "A"),
            ("Lady Celeste Blackwood", "His wife. Not Celeste Nicholas", "A"),
            ("Tiran Lucien Blackwood", "b. 15 April 2072, their second child and first son; a Flamer. "
                                       "He ran Shadowmere routes with Remy, and “Blackwood's collecting” (3SL ch. 9) points at his house", "T"),
        ]),
        ("Nora Victoria Alexandria Evans", "b. 19 Aug 2063, Alleia", [
            ("Who", "The Sanctum's first recorded dual attunement (Flight and Blocker). Her titles are her faction's honours, not royal blood", "A"),
        ]),
    ]),
]

# ------------------------------------------------------------ succession at FTE
SUCCESSION = [
    ("Remnia", "Empress Aracelia, 9 Sept 2096", [
        ("1", "Elias", "Crown Prince; missing"),
        ("2", "Melena", "Duchess of Rovencia"),
        ("3", "Cordelia", ""),
        ("4", "Louis", "Richard's ward"),
        ("", "then Charlotte and her line", ""),
    ], "Once Katherine is acknowledged (after FTE), she stands second, between Elias and Melena."),
    ("London Town", "Queen Dalia, 9 Sept 2096", [
        ("1", "Maxim", "Crown Prince"),
        ("2", "Zoe", "Styled “Princess Dalia”"),
        ("3", "Arielle", "The Princess Royal"),
        ("4", "Orion", "Six years old"),
    ], "Out: Minho, Zephyr and Sebastian, who each gave up their place."),
]

# ---------------------------------------------------------------- calendar
CALENDAR = [
    ("Year 1 ER", "Eden founds the Empire", "S"),
    ("3 Sept 2024", "Richard born, Eden's eldest", "S"),
    ("2 Aug 2035", "Tobias Lockwood born, Highcrest", "S"),
    ("18 Nov 2035", "Ethan Nicholas, Tobias's cousin, born in Meridion", "Y"),
    ("7 Oct 2038", "Aracelia and Alexandria born", "S"),
    ("31 Oct 2038", "Dalia born", "S"),
    ("26 Oct 2055", "Lucia and Charlotte born to Aracelia (17) and Jackson Harper", "S"),
    ("9 Sept 2060", "Aracelia marries Jackson Harper", "S"),
    ("c. 2070", "Michelle wins her Tournament; her Board year brings her to Tobias", "A"),
    ("15 April 2072", "Tiran Lucien Blackwood born", "S"),
    ("7 Sept 2072", "Maxim born", "S"),
    ("3 Oct 2073", "Elias born", "S"),
    ("c. 2074–2076", "Lucia uses the Shadowmere route", "A"),
    ("7 Sept 2075", "Zephyr born, then Zoe six minutes later", "Y"),
    ("Early 2076", "Michelle marries Ethan Nicholas", "A"),
    ("14 July 2076", "Katherine born, Old Prosperity", "S"),
    ("9 Sept 2076", "Melena born; Lucia's succession decree", "S"),
    ("2 Sept 2079", "Cordelia born", "S"),
    ("c. 2080", "Eden dies; Aracelia accedes", "A"),
    ("14 May 2081", "Louis born", "S"),
    ("c. 2090", "Elias called to the board as King, at sixteen", "A"),
    ("15–30 June 2090", "Nathaniel abdicates; Dalia becomes Queen; Rovencia passes to Melena (13)", "Y"),
    ("1 Oct 2090", "Orion born", "S"),
    ("7 Sept 2094", "Lucia dies (the fixed anchor)", "Y"),
    ("11 Sept 2094", "Guardianship orders; Tobias signs custody away", "A"),
    ("18 Sept 2094", "Melena finds Lucia's letter, addressed to Elias", "S"),
    ("c. 28 Sept 2094", "3SL opens", "A"),
    ("Autumn 2094", "Remy dies (3SL ch. 37); Melena leaves Shadowmere (ch. 41)", "T"),
    ("c. March 2095", "Tobias dies", "A"),
    ("9 April 2095", "Sebastian gives up his place", "S"),
    ("Late Aug 2096", "Suggested: the 3SL Epilogue, when Melena's message arrives", "O"),
    ("9 Sept 2096", "FTE opens on Melena's twentieth birthday", "A"),
    ("Nov 2096", "Clyde Hastings dies, during FTE", "S"),
]

# ------------------------------------------------- lines the drafts now contradict
REVISIONS = [
    ("Beta, F2025", "Melena's “Lockwood amber” eyes (also F2025: “her amber eyes locking directly with Katherine's”)",
     "Lockwood emerald"),
    ("Beta", "Cordelia's “amber eyes and crimson hair like Melena's”",
     "Amber eyes like Elias's; crimson hair like Melena's"),
    ("BSS", "Melena's emerald eyes and crimson hair, “traits that have long been associated with the Hastings lineage”",
     "Emerald eyes from the Lockwoods; crimson hair from the Hastings"),
    ("BSS", "Elias's golden eyes, “long associated with the Lockwood lineage”",
     "Gold is the Hastings eye"),
    ("BSS", "Duke Alistair Lockwood (67) and Duchess Rowena (64)", "Duke Sawyer Lockwood (87) and Duchess Rowena (84)"),
    ("BSS", "Melena, “Duchess of Avalon”", "Duchess of Rovencia, from June 2090"),
    ("BSS", "Zephyr, “the elder twin by two minutes”", "Six minutes"),
    ("BSS", "Eden as Elias's “grandmother”, “deceased for decades” by 2091",
     "Great-grandmother, dead for just over a decade"),
    ("BSS", "Richard “55” in 2094; Lucia born 2047", "Richard 70; Lucia born 2055"),
    ("CB", "Melena born 2077", "2076"),
    ("F4", "“Katherine Lockwood” in Book 3", "Katherine Nicholas, by her own choice"),
    ("F2025", "“Empress Aracelia Lockwood”", "Aracelia Hastings (a caption error)"),
    ("F2025, Mirror", "Lucia a Flamer, Tobias a Frost",
     "Lucia Frost, Tobias Fire. Leave the Mirror lines only if the Mirror is meant to distort"),
    ("Beta", "“Months since the alley”", "About two years: Remy dies in autumn 2094"),
]

# ---------------------------------------------------------------- 3SL check
CHECK_3SL = [
    ("Fits", "The opening", "The outline starts with Melena already in Shadowmere, carrying Lucia's letter unopened until "
     "ch. 5. BSS has her finding it on 18 Sept, so 3SL opening around 28 Sept 2094 holds."),
    ("Fits", "The letter to Elias", "Lucia's last words go to her heir. Elias is Crown Prince from her death."),
    ("Fits", "“Melena Lockwood”", "The Synod's name for her (ch. 23) matches the Lockwood surname."),
    ("Fits", "Selah's “Lucia?”", "Melena has Lucia's crimson hair, so Selah sees Lucia in her (ch. 22). "
     "The emerald eyes are Tobias's: that's the green that stops Silas."),
    ("Fits", "Blackwood", "“Blackwood's collecting” (ch. 9) is Tiran's house. Renaming Tobias's father to Sawyer keeps "
     "“Blackwood” and “Lockwood” from blurring when both are said together (ch. 23)."),
    ("Fits", "Remy's death", "Ch. 37 falls in autumn 2094, about two years before FTE, as TCD-013 has it."),
    ("Note", "Tobias is alive", "He lives until about March 2095, so he's alive (having signed his children away) all through 3SL. "
     "Whether Melena thinks of him when she says “I don't know who I am without my mother!” (ch. 20) is your call."),
    ("Note", "The Epilogue", "It runs “straight into FTE”, so I'd set it in late August 2096: two years after the "
     "main story and days before FTE opens. The outline leaves this to you."),
    ("Ask", "Asha Noelle Wraithmoor", "Asha shares Lucia's middle name, and Lucia sat in Selah's kitchen around 2074–2076. "
     "If Asha was born around then, she could be named for Lucia. Is that echo intended?"),
    ("Ask", "“Mira”", "None of Melena's four names contains it. If it should come from a middle name, that would be a fifth name. "
     "I'd keep it as Remy's name for her."),
]

STILL_OPEN = [
    "Katherine's eyes: emerald would make her Tobias's daughter at a glance.",
    "The Epilogue's date: I suggest late August 2096.",
    "Whether Asha Noelle is named for Lucia.",
    "Where “Mira” comes from (3SL ch. 14): I'd keep it as Remy's name for her, not one of hers.",
    "How public Katherine's birth stays (TCD-059): my suggestion is news for a week, unspeakable after, forgotten in twenty years.",
]
