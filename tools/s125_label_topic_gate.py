#!/usr/bin/env python
"""s125 (D-066 cc; P-70 / H-20, H-06), Step 0 only: the power gate for 'biological-section labels share more vocabulary
with plant labels (P/H) than with star/cosmological labels (C/Z/A)' (Taiz & Taiz 2011 reading).

This script computes NO Voynich label overlap.  It (1) counts Voynich label loci by section from VKB loci (count only,
allowed by the brief), and (2) checks whether any real labelled corpus on disk can serve as the power-calibration control
the brief requires.  Only if a control qualifies may a later, separately pre-registered run measure power.

VOYNICH COUNTS.  VKB data/vkb/vkb.sqlite, table loci (locus_type 'L%') joined to folios.section, per translit
(ZL3b primary; RF1b, IT2a printed).  Groups: B = section B; PH = sections P + H; CZA = sections C + Z + A.  T is in no
group.  Required control sizes = the ZL3b group counts n_B, n_PH, n_CZA.

CONTROL RULE (frozen).  A candidate qualifies only if ALL hold:
  R1 it is real (not Voynich, not synthetic);
  R2 it is ONE source (one manuscript/edition): pooling sources would make topic coincide with source (scribe, language,
     date), which is the confound the Voynich test must remove by hand/quire strata;
  R3 its labels/captions fall into >= 3 topical groups, with one declared truly related pair (plant vs plant-like) and
     one unrelated group (cosmological/astral), per the source's own description;
  R4 size: n_labels >= n_B + n_PH + n_CZA (necessary for drawing three groups at Voynich counts without replacement).
  If no candidate qualifies: CALL NO_CONTROL (stop).  If one qualifies: CALL POWER_GATE_PENDING (a new run id must build
  and pre-register the power simulation; this script does not).
CANDIDATES (every real label/caption corpus on disk found in reconnaissance; sizes are counted here from the files):
  C1 Bodleian Canon. Misc. 408 range labels (data/herbals_alchemical/bodleian_canon_misc_408/canvases_structures.tsv,
     column structure_labels, non-empty): an alchemical herbal; every caption names a plant -> 1 topic.
  C2 Penn LJS 419 captions (data/herbals_period/ljs419/captions_s103.json, plants with a caption): herbal -> 1 topic.
  C3 BL Sloane 4016 captions (data/herbals_period/sloane4016/captions_s103.json): herbal -> 1 topic.
  C4 Tacuinum sanitatis BnF lat. 9333 entry headings (data/controls_tabular/raw_tacuinum_medimanus/tacuinum_sanitatis.html,
     paragraphs <p style="text-align:justify...">, the first paragraph is the preface and is not an entry): fruits,
     vegetables, meats, seasons, winds etc. -> >= 3 topics with a plant-plant related pair and a cosmological group.
  Not candidates: data/controls_daybreak s113/s114 Stolfi label files (Voynich labels, fail R1); plain-text corpora
  (data/controls*, data/external/genre-*, T2/T3 tabular texts) carry no picture labels.
FIXTURE (--fixture): synthetic sqlite loci with planted counts must be recovered exactly; synthetic candidates
  (3 topics, 1000 labels) -> qualifies; (3 topics, 207) -> no; (1 topic, 2000) -> no; (Voynich, 3 topics, 2000) -> no;
  (pooled sources, 3 topics, 2000) -> no.  FIXTURE_PASS=True only if all match.  --run refuses without it.
"""
import argparse, html, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "s125"
VKB = ROOT / "data" / "vkb" / "vkb.sqlite"
GROUPS = {"B": ("B",), "PH": ("P", "H"), "CZA": ("C", "Z", "A")}
C1 = ROOT / "data/herbals_alchemical/bodleian_canon_misc_408/canvases_structures.tsv"
C2 = ROOT / "data/herbals_period/ljs419/captions_s103.json"
C3 = ROOT / "data/herbals_period/sloane4016/captions_s103.json"
C4 = ROOT / "data/controls_tabular/raw_tacuinum_medimanus/tacuinum_sanitatis.html"


def label_counts(con):
    q = ("SELECT l.translit, f.section, COUNT(*) FROM loci l JOIN folios f ON l.folio=f.folio "
         "WHERE l.locus_type LIKE 'L%' GROUP BY l.translit, f.section")
    out = {}
    for tr, sec, n in con.execute(q):
        out.setdefault(tr, {}).setdefault(sec, 0)
        out[tr][sec] += n
    grp = {tr: {g: sum(d.get(s, 0) for s in ss) for g, ss in GROUPS.items()} for tr, d in out.items()}
    return out, grp


def qualifies(c, need):
    why = []
    if not c["real"]:
        why.append("R1 not real/non-Voynich")
    if not c["single_source"]:
        why.append("R2 pooled sources")
    if c["topics"] < 3 or not c["related_pair"]:
        why.append(f"R3 topics={c['topics']} related_pair={c['related_pair']}")
    if c["n"] < need:
        why.append(f"R4 n={c['n']} < {need}")
    return (not why), why


def count_c1():
    rows = C1.read_text(encoding="utf-8").splitlines()[1:]
    return sum(1 for r in rows if len(r.split("\t")) > 5 and r.split("\t")[5].strip())


def count_caps(p):
    d = json.loads(p.read_text(encoding="utf-8"))
    return sum(1 for pg in d for pl in pg.get("plants", []) if (pl.get("caption") or "").strip())


def count_c4():
    t = C4.read_text(encoding="utf-8", errors="replace")
    ps = re.findall(r'<p style="text-align:justify[^"]*">(.*?)</p>', t, flags=re.S)
    heads = [html.unescape(re.sub(r"<[^>]+>", " ", p.split("<strong>")[0])).strip() for p in ps[1:]]
    return sum(1 for h in heads if h)


def fixture():
    ok = True
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE loci(translit, folio, locus_type)")
    con.execute("CREATE TABLE folios(folio, section)")
    plant = {"B": 7, "P": 11, "H": 3, "C": 5, "Z": 13, "A": 2, "T": 4}
    for i, (s, n) in enumerate(plant.items()):
        con.execute("INSERT INTO folios VALUES(?,?)", (f"f{i}", s))
        for _ in range(n):
            con.execute("INSERT INTO loci VALUES('ZL3b',?, 'L0')", (f"f{i}",))
        con.execute("INSERT INTO loci VALUES('ZL3b',?, 'P')", (f"f{i}",))
    _, g = label_counts(con)
    exp = {"B": 7, "PH": 14, "CZA": 20}
    f0 = g["ZL3b"] == exp
    print(f"FX0 planted loci counts recovered {g['ZL3b']} == {exp}: {'PASS' if f0 else 'FAIL'}")
    ok &= f0
    base = dict(real=True, single_source=True, topics=3, related_pair=True, n=1000)
    cases = [("FX1 3 topics n=1000", base, True), ("FX2 3 topics n=207", {**base, "n": 207}, False),
             ("FX3 1 topic n=2000", {**base, "topics": 1, "related_pair": False, "n": 2000}, False),
             ("FX4 Voynich n=2000", {**base, "real": False, "n": 2000}, False),
             ("FX5 pooled n=2000", {**base, "single_source": False, "n": 2000}, False)]
    for name, c, want in cases:
        got, why = qualifies(c, 969)
        r = got == want
        ok &= r
        print(f"{name}: qualifies={got} expected={want} {why} -> {'PASS' if r else 'FAIL'}")
    print(f"FIXTURE_PASS={ok}")
    return ok


def run():
    fx = RUN / "fixture.txt"
    if not fx.exists() or "FIXTURE_PASS=True" not in fx.read_text(encoding="utf-8"):
        print("REFUSE: fixture not passed")
        sys.exit(2)
    con = sqlite3.connect(f"file:{VKB.as_posix()}?mode=ro", uri=True)
    raw, grp = label_counts(con)
    print("Voynich label loci by section (count only; no label text read):")
    for tr in sorted(raw):
        print(f"  {tr}: " + " ".join(f"{s}={raw[tr][s]}" for s in sorted(raw[tr])) + "  | groups "
              + " ".join(f"{g}={grp[tr][g]}" for g in GROUPS))
    z = grp["ZL3b"]
    need = z["B"] + z["PH"] + z["CZA"]
    print(f"Required control sizes (ZL3b): B={z['B']} PH={z['PH']} CZA={z['CZA']}; R4 total >= {need}")
    cands = [("C1 Bodleian Canon Misc 408 captions", dict(real=True, single_source=True, topics=1, related_pair=False, n=count_c1())),
             ("C2 LJS 419 captions", dict(real=True, single_source=True, topics=1, related_pair=False, n=count_caps(C2))),
             ("C3 Sloane 4016 captions", dict(real=True, single_source=True, topics=1, related_pair=False, n=count_caps(C3))),
             ("C4 Tacuinum BnF lat 9333 headings", dict(real=True, single_source=True, topics=3, related_pair=True, n=count_c4()))]
    any_q = False
    for name, c in cands:
        q, why = qualifies(c, need)
        any_q |= q
        print(f"  {name}: n={c['n']} topics={c['topics']} -> {'QUALIFIES' if q else 'fails ' + '; '.join(why)}")
    if any_q:
        print("CALL POWER_GATE_PENDING")
    else:
        print("CALL NO_CONTROL")
        print("Missing: one real illustrated source with >= 3 topical label groups (incl. plant and astral) and >= "
              f"{need} labels; Voynich label overlap NOT computed.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.fixture:
        fixture()
    if a.run:
        run()
