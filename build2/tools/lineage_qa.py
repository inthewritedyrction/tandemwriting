#!/usr/bin/env python3
"""Lineage QA for the Remnian lineage record (src/lineage.py).

Checks:
 1. parent/child consistency between the edge list and every person's
    Parents / Children claims;
 2. duplicate persons and shared name variants;
 3. succession vs biology: no succession position rests on parentage alone;
 4. every claim traced to a known source and a valid status;
 5. no legacy or supporting claim silently promoted (CANON needs a ruling,
    CURRENT DRAFTED TEXT needs a controlling manuscript);
 6. no contradiction erased by the graphic: every conflict a charted person
    carries is printed on that person's node (checked against out/genealogy_ids.json).
Writes out/lineage_qa.json and exits non-zero on any failure.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import lineage as L  # noqa: E402

STATUSES = set("cdspoxl")
WEAK_LEGACY = {"TLE", "F2025", "F4", "IL"}
SUPPORTING = {"BSS", "CB", "WTR", "3139", "PLC"}
CONTROLLING_PROSE = {"BETA", "3SL"}


def first(name):
    return re.split(r"[ (]", name)[0].lower()


def names_of(p):
    return {first(p["name"])} | {first(v) for v in p["variants"]}


def known(src):
    return src in L.SOURCES or re.fullmatch(r"TCD-\d{3}", src)


def run(genealogy_ids=None):
    res = {"parent_child": [], "duplicates": [], "succession_vs_biology": [], "provenance": [], "promotion": [], "graphic": [], "counts": {}}
    P = L.PERSONS
    # 1 · parent/child consistency
    for par, ch, st, srcs, _ in L.EDGES:
        if par not in P or ch not in P:
            res["parent_child"].append(f"edge {par}→{ch}: person missing")
            continue
        kids = " ".join(c[2] for c in P[par]["claims"] if c[0] == "BIO" and c[1].startswith("Children"))
        pars = " ".join(c[2] for c in P[ch]["claims"] if c[0] == "BIO" and (c[1].startswith("Parents") or c[1].startswith("Spouse · children")))
        kids_all = kids + " ".join(c[2] for c in P[par]["claims"] if c[1].startswith("Spouse · children"))
        if kids_all and not any(n in kids_all.lower() for n in names_of(P[ch])):
            res["parent_child"].append(f"{P[par]['name']} lists children without {P[ch]['name']}")
        if pars and first(P[par]["name"]) not in pars.lower():
            res["parent_child"].append(f"{P[ch]['name']} lists parents without {P[par]['name']}")
        if not kids_all and not pars:
            res["parent_child"].append(f"edge {par}→{ch} has no claim on either side")
    # the reverse: every child named in a Children claim has an edge (for charted people)
    edge_set = {(a, b) for a, b, *_ in L.EDGES}
    for pid, p in P.items():
        for c in p["claims"]:
            if c[0] == "BIO" and c[1] == "Children":
                for cid, q in P.items():
                    txt = re.sub(r"\(with [^)]*\)", "", c[2]).lower()
                    if re.search(r"\b" + re.escape(first(q["name"])) + r"\b", txt):
                        if (pid, cid) not in edge_set and cid != pid:
                            res["parent_child"].append(f"{p['name']} names {q['name']} as a child but no edge exists")
    # 2 · duplicates and shared variants
    norm = lambda s: unicodedata.normalize("NFKC", s).lower().strip()
    names = {}
    for pid, p in P.items():
        for n in [p["name"]] + p["variants"]:
            key = norm(re.sub(r"\s*\(.*?\)", "", n))
            names.setdefault(key, set()).add(pid)
    for k, ids in names.items():
        if len(ids) > 1:
            res["duplicates"].append(f"name '{k}' used by {sorted(ids)}")
    fulls = {}
    for pid, p in P.items():
        fulls.setdefault(norm(p["name"]), []).append(pid)
    for k, ids in fulls.items():
        if len(ids) > 1:
            res["duplicates"].append(f"duplicate person '{k}': {ids}")
    # 3 · succession vs biology
    for pid, p in P.items():
        for c in p["claims"]:
            if c[0] == "SUCC" and c[3] in "cds" and set(c[4]) <= {"TCD-040"}:
                res["succession_vs_biology"].append(f"{p['name']}: succession claim rests on TCD-040 alone")
    for lane in (L.SUCC_CURRENT_IMPERIAL, L.SUCC_CURRENT_LONDON, L.SUCC_HISTORY):
        for row in lane:
            st, srcs = row[-2], row[-1]
            if st in "cds" and set(srcs) <= {"TCD-040"}:
                res["succession_vs_biology"].append(f"succession row rests on parentage: {row}")
    # 4 · provenance
    n_claims = 0
    for pid, p in P.items():
        for c in p["claims"]:
            n_claims += 1
            if c[3] not in STATUSES:
                res["provenance"].append(f"{p['name']}: bad status {c[3]}")
            if not c[4]:
                res["provenance"].append(f"{p['name']}: claim without source: {c[2]}")
            for s in c[4]:
                if not known(s):
                    res["provenance"].append(f"{p['name']}: unknown source {s}")
    for row in L.EDGES + L.SUPERSEDED_EDGES:
        if not row[3] or row[2] not in STATUSES:
            res["provenance"].append(f"edge {row[:2]} missing source/status")
    # 5 · promotion
    for pid, p in P.items():
        for c in p["claims"]:
            srcs = set(c[4])
            tcd = any(s.startswith("TCD-") for s in srcs)
            if c[3] == "c" and not tcd:
                res["promotion"].append(f"{p['name']}: CANON without a ruling: {c[2]}")
            if c[3] == "d" and not (srcs & CONTROLLING_PROSE) and not tcd:
                res["promotion"].append(f"{p['name']}: DRAFTED without controlling prose: {c[2]}")
            if srcs and srcs <= WEAK_LEGACY and c[3] in "cds":
                res["promotion"].append(f"{p['name']}: legacy-only claim promoted to {c[3]}: {c[2]}")
            if srcs and srcs <= (SUPPORTING | WEAK_LEGACY) and c[3] in "cd":
                res["promotion"].append(f"{p['name']}: supporting-only claim promoted to {c[3]}: {c[2]}")
    for a, b, st, srcs, _ in L.EDGES:
        if set(srcs) <= WEAK_LEGACY and st in "cds":
            res["promotion"].append(f"edge {a}→{b}: legacy-only edge at {st}")
        if st == "c" and not any(s.startswith("TCD-") for s in srcs):
            res["promotion"].append(f"edge {a}→{b}: CANON without a ruling")
    # 6 · graphic
    if genealogy_ids is not None:
        for pid, shown in genealogy_ids.items():
            need = set()
            for c in P[pid]["claims"]:
                need |= set(re.findall(r"LC-\d{2}", c[5] + " " + c[2]))
            missing = need - set(shown)
            if missing:
                res["graphic"].append(f"{P[pid]['name']}: conflicts not on node: {sorted(missing)}")
    res["counts"] = {"persons": len(P), "claims": n_claims, "edges": len(L.EDGES), "conflicts": len(L.CONFLICTS),
                     "open_items": len(L.OPEN_ITEMS), "name_checks": len(L.NAME_CHECKS), "rejected": len(L.REJECTED)}
    return res


if __name__ == "__main__":
    gid = ROOT / "out" / "genealogy_ids.json"
    r = run(json.loads(gid.read_text()) if gid.exists() else None)
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / "lineage_qa.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
    bad = {k: v for k, v in r.items() if k != "counts" and v}
    print(json.dumps(r["counts"]))
    for k, v in bad.items():
        print(k, len(v))
        for x in v:
            print("   ", x)
    sys.exit(1 if bad else 0)
