"""Bird's-eye index of every Voynich drawing, from published page-facts and the frozen s115-A1 labels.

Read-only. Copies what the sources already say. Does not score botanical accuracy,
date a drawing, or invent a number for a human figure.

Sources (page-fact TSV homes; the sqlite copy can lag a new pull):
  data/external/page-facts/*/facts.tsv             catalogues, plants, astro-physical, sherwood-v2
  data/anchor_A1/labels.tsv                        s115-A1 visual bins (self-check only)

Usage:
  python tools/vkb/queries/image_index.py --summary
  python tools/vkb/queries/image_index.py --out data/vkb/image_index.tsv
  python tools/vkb/queries/image_index.py --fragments --out data/vkb/image_fragments.tsv
  python tools/vkb/queries/image_index.py f2v

The TSV is derived. Regenerate it with this script. Do not hand-edit it.
A cell is the source's words. `root~`, `animal~` and `tubes~` mark an s115-A1 bin
that run dropped (kappa rule); the bin is still the run's own label.
"""
import csv, glob, os, re, sqlite3, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common import DB, ROOT

csv.field_size_limit(10_000_000)

A1 = os.path.join(ROOT, "data", "anchor_A1", "labels.tsv")
PAGE_FACTS = os.path.join(ROOT, "data", "external", "page-facts")

NAME_ATTRS = {"plant-id", "identification"}
DRAW_ATTRS = {"herbal-drawing-class", "drawing-character", "herbal-copy-class"}
DEPICT_ATTRS = {"illustration", "illustration-detail", "pharma-fragment-kind", "title"}
MATCH_ATTRS = {"pharma-herbal-match", "herbal-herbal-match", "cross-reference", "herbal-parallel"}
PEOPLE_ATTRS = {"nymph-count", "overpainting", "zodiac-sign", "month-name", "cosmo-reading"}
FRAGMENT_ATTR = "pharma-fragment"
FULL_ATTRS = NAME_ATTRS | DRAW_ATTRS | DEPICT_ATTRS | MATCH_ATTRS | PEOPLE_ATTRS | {
    FRAGMENT_ATTR, "subject"}

# Species-confidence and "how well is it drawn" sentences. Copy-grades ("good match"
# between a herbal page and a pharma fragment) stay in the matches column.
# Stolfi's "good match" / "poor match" copy-grades stay out of this list.
LIKENESS = re.compile(
    r"accurate|inaccurate|not a good|good representation|resembl|not unlike|"
    r"undoubtedly|unidentifiable|stated confidence|compared with|"
    r"compare well|pretty close|quite confident|little doubt|very good match|"
    r"reasonable match|good fit|looks quite good|very nice match|exact match|"
    r"wonderful match",
    re.I)
# A published pointer past this book: another manuscript, a place, or a year.
# A bare "(O'Neill)" is a name credit, so it is not included.
OUTSIDE = re.compile(
    r"\b(?:other (?:herbal )?manuscripts|manuscripts of|some manuscripts|"
    r"medical manuscripts|English manuscripts|Tractatus|herbal tradition|armadillo|sunflower|"
    r"Mexico|New World|Wellcome|Florence|Oxford|St John|Hausbuch|"
    r"Schoeffer|Meydenbach|Ortus|Hortus|Egerton|Dioscorides|Herbarius|"
    r"Sloane|Morgan Library|Harley|BNF)\b|\b1[4-9]\d{2}\b",
    re.I)
PERSON = re.compile(
    r"\b(?:nymphs?|figures?|persons?|women|woman|naked|crown|animal|bird|sheep|goat|"
    r"human)\b",
    re.I)
FRAG_N = re.compile(r"\bfragment\s+(\d+)\b", re.I)
FRAG_ON = re.compile(r"\bfragment\s+(\d+)\s+on\s+(f\d+[rv]\d*)\b", re.I)
FRAG_ROW = re.compile(r"^fragment\s+(\d+)\s*,\s*row\s+(\d+)\b", re.I)

# s115-A1 keep rule (data/anchor_A1/kappa.txt). '~' marks a dropped bin.
KEPT = {
    "PLANT": ["P_plants", "P_leafshape", "P_leafcount", "P_flower", "P_habit"],
    "PHARMA": ["J_shape", "J_count", "J_fragcount", "J_fragtype"],
    "CIRCLE": ["C_centre", "C_figures", "C_rings", "C_diagrams", "C_rays"],
    "BATH": ["B_pools", "B_figures"],
}
DROPPED = {"PLANT": ["P_root"], "CIRCLE": ["C_animal"], "BATH": ["B_tubes"]}
SHORT = {
    "P_plants": "plants", "P_leafshape": "leaf", "P_leafcount": "leaves",
    "P_flower": "flowers", "P_habit": "habit", "P_root": "root~",
    "J_shape": "jars", "J_count": "jar_n", "J_fragcount": "frags", "J_fragtype": "frag",
    "C_centre": "centre", "C_animal": "animal~", "C_figures": "figures",
    "C_rings": "rings", "C_diagrams": "diagrams", "C_rays": "rays",
    "B_pools": "pools", "B_figures": "figures", "B_tubes": "tubes~",
}

PANEL_COLS = [
    "folio", "section", "hand", "scans", "a1_type", "a1_shape",
    "depiction", "names", "drawing_class", "likeness", "outside",
    "people", "matches", "n_fragments",
]
FRAG_COLS = ["folio", "fragment", "row", "label", "mentions", "scan"]


def norm(v):
    return re.sub(r"\s+", " ", (v or "").strip().lower())


def cell(v):
    return re.sub(r"\s+", " ", (v or "").replace("\t", " ")).strip()


def short_source(s):
    s = cell(s)
    s = re.sub(r"\s*\(c\)\s*", " ", s).strip(" ,")
    s = s.split(" (as ")[0]
    return s[:70]


def folio_key(f):
    if f == "fRos":
        return (85, 1, 50)
    m = re.match(r"f(\d+)(r|v)(\d+)?$", f)
    if not m:
        return (9999, 0, 0)
    return (int(m.group(1)), 0 if m.group(2) == "r" else 1, int(m.group(3) or 0))


def pack(pairs):
    """pairs: (value, source). Same words once, sources joined."""
    groups = []
    index = {}
    for value, source in pairs:
        value = cell(value)
        k = norm(value)
        if k in ("", "-", "(none)"):
            continue
        if k not in index:
            index[k] = len(groups)
            groups.append([value, []])
        tag = short_source(source)
        if tag not in groups[index[k]][1]:
            groups[index[k]][1].append(tag)
    return " | ".join(f"{v} [{'; '.join(src)}]" for v, src in groups)


def a1_shape(row):
    pt = row["PT"].split(":")[0]
    if pt.startswith("DISAGREE"):
        pt = row["PT"]
    base = pt if pt in KEPT else ""
    bits = []
    for col in KEPT.get(base, []):
        val = row.get(col) or ""
        if val and val != "NA":
            bits.append(f"{SHORT[col]}={val}")
    for col in DROPPED.get(base, []):
        val = row.get(col) or ""
        if val and val != "NA":
            bits.append(f"{SHORT[col]}={val}")
    return " ".join(bits)


def load_a1():
    with open(A1, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    by_stem = {}
    for r in rows:
        by_stem.setdefault(r["stem"], []).append(r)
    return by_stem


def load():
    """Folios and panel images stay in the VKB. Page facts are read from each
    pull's facts.tsv, the same way tools/vkb/world.py page_facts() reads them,
    so a new pull is visible without rebuilding the database."""
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    folios = [dict(r) for r in c.execute(
        "select folio, section, hand_davis, image_path from folios")]
    panels = [dict(r) for r in c.execute(
        "select folio, image_path, kind from panel_images")]
    c.close()
    facts = []
    for path in sorted(glob.glob(os.path.join(PAGE_FACTS, "*", "facts.tsv"))):
        pull = os.path.basename(os.path.dirname(path))
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        with open(path, encoding="utf-8", newline="") as fh:
            for i, r in enumerate(
                    csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE), start=2):
                facts.append({
                    "folio": r["folio"],
                    "attribute": r["attribute"],
                    "value": r["value"],
                    "source": r["source"],
                    "url": r["url"],
                    "quote": r["quote"],
                    "pull": pull,
                    "src": f"{rel}:{i}",
                })
    return folios, panels, facts


def index_facts(facts):
    by = defaultdict(list)
    for r in facts:
        by[r["folio"]].append(r)
    return by


def stems_for(folio, panels):
    stems = []
    for p in panels:
        if p["folio"] != folio:
            continue
        stem = os.path.splitext(os.path.basename(p["image_path"]))[0]
        if stem not in stems:
            stems.append(stem)
    return stems


def rows_for(folio, facts_by, attrs):
    out = []
    for r in facts_by.get(folio, []):
        if r["attribute"] in attrs:
            out.append((r["value"], r["source"]))
    return out


def panel_row(folio, section, hand, facts_by, panels, a1_by):
    stems = stems_for(folio, panels)
    a1_rows = []
    for stem in stems:
        a1_rows.extend(a1_by.get(stem, []))
    types = []
    shapes = []
    for r in a1_rows:
        if r["PT"] not in types:
            types.append(r["PT"])
        sh = a1_shape(r)
        if sh and len(a1_rows) > 1:
            sh = f"{r['stem']}: {sh}"
        if sh and sh not in shapes:
            shapes.append(sh)
    depict = [
        (v, s) for v, s in rows_for(folio, facts_by, DEPICT_ATTRS)
        if norm(v) not in ("???", "?")
    ]
    names = rows_for(folio, facts_by, NAME_ATTRS)
    draw = rows_for(folio, facts_by, DRAW_ATTRS)
    matches = rows_for(folio, facts_by, MATCH_ATTRS)
    people = rows_for(folio, facts_by, PEOPLE_ATTRS)
    # Person sentences that the catalogues filed under illustration, not under a count.
    people += [(v, s) for v, s in depict if PERSON.search(v)]
    likeness = [(v, s) for v, s in names + depict + matches + draw if LIKENESS.search(v)]
    outside = [(v, s) for v, s in names + depict + matches + people if OUTSIDE.search(v)]
    # Commentary filed under plant-id stays in `names` too: it is what that source wrote.
    n_frag = sum(1 for r in facts_by.get(folio, []) if r["attribute"] == FRAGMENT_ATTR)
    return {
        "folio": folio,
        "section": section or "",
        "hand": "" if hand is None else str(hand),
        "scans": " ".join(stems),
        "a1_type": " ".join(types),
        "a1_shape": " | ".join(shapes),
        "depiction": pack(depict),
        "names": pack(names),
        "drawing_class": pack(draw),
        "likeness": pack(likeness),
        "outside": pack(outside),
        "people": pack(people),
        "matches": pack(matches),
        "n_fragments": str(n_frag),
    }


def fragment_rows(facts_by, panels):
    """One row per numbered pharma fragment. A sentence is attached when it says
    'fragment N' on that folio, or 'fragment N on fX' for another folio.
    'Item N' and 'No. N' are left on the page: those are other people's numberings."""
    out = []
    where = {}
    for folio, rows in facts_by.items():
        scan = " ".join(stems_for(folio, panels))
        for r in rows:
            if r["attribute"] != FRAGMENT_ATTR:
                continue
            m = FRAG_ROW.match(cell(r["value"]))
            frag, row = (m.group(1), m.group(2)) if m else ("", "")
            rec = {
                "folio": folio, "fragment": frag, "row": row,
                "label": cell(r["value"]), "mentions": "", "scan": scan,
            }
            out.append(rec)
            if frag:
                where[(folio, frag)] = rec
    bag = defaultdict(list)
    for folio, rows in facts_by.items():
        for r in rows:
            if r["attribute"] not in MATCH_ATTRS | NAME_ATTRS | DEPICT_ATTRS:
                continue
            text = r["value"] or ""
            placed = FRAG_ON.findall(text)
            if placed:
                for n, dest in placed:
                    bag[(dest, n)].append((text, r["source"]))
                continue
            for n in FRAG_N.findall(text):
                bag[(folio, n)].append((text, r["source"]))
    for key, pairs in bag.items():
        rec = where.get(key)
        if rec is not None:
            rec["mentions"] = pack(pairs)
    return out


def write_tsv(path, cols, rows):
    fh = open(path, "w", encoding="utf-8", newline="") if path else sys.stdout
    try:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n",
                           quoting=csv.QUOTE_MINIMAL, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: cell(r.get(k, "")) for k in cols})
    finally:
        if path:
            fh.close()


def print_folio(folio, facts_by, panels, a1_by, folios):
    meta = {r["folio"]: r for r in folios}
    if folio not in meta and folio not in facts_by:
        print(f"no folio {folio}")
        return 1
    info = meta.get(folio)
    section = info["section"] if info else ""
    hand = info["hand_davis"] if info else ""
    row = panel_row(folio, section, hand, facts_by, panels, a1_by)
    print(f"== {folio}  section {row['section']}  hand {row['hand']}  scans {row['scans']}")
    print(f"a1: {row['a1_type']}  {row['a1_shape']}")
    print(f"fragments numbered on this page: {row['n_fragments']}")
    print("-- published rows (image attributes only)")
    for r in facts_by.get(folio, []):
        if r["attribute"] not in FULL_ATTRS:
            continue
        q = cell(r["quote"] or "")
        if q and q != cell(r["value"]):
            q = f'  quote: {q[:240]}'
        else:
            q = ""
        print(f"  [{r['attribute']}] {cell(r['value'])}")
        print(f"      <{cell(r['source'])}>  {r['pull']}  {r['src']}{q}")
    fr = [f for f in fragment_rows(facts_by, panels) if f["folio"] == folio]
    named = [f for f in fr if f["mentions"]]
    if named:
        print("-- fragments a source names")
        for f in named:
            print(f"  fragment {f['fragment']} row {f['row']}: {f['mentions']}")
    return 0


def summary(panel_rows, frag_rows):
    def has(col):
        return sum(1 for r in panel_rows if r[col])

    by_sec = defaultdict(int)
    for r in panel_rows:
        by_sec[r["section"] or "?"] += 1
    print(f"panels {len(panel_rows)}")
    print("by section " + " ".join(f"{k}:{by_sec[k]}" for k in sorted(by_sec)))
    print(f"with a published name or identification: {has('names')}")
    print(f"with a depiction sentence: {has('depiction')}")
    print(f"with a source likeness sentence: {has('likeness')}")
    print(f"with a source pointer outside this book, or a year: {has('outside')}")
    print(f"with a person, animal or zodiac sentence: {has('people')}")
    print(f"with an s115-A1 label: {has('a1_type')}")
    print(f"pharma fragment rows: {len(frag_rows)}")
    print(f"fragments a source names in a match or a name: {sum(1 for r in frag_rows if r['mentions'])}")
    print("sections: H herbal, P pharmaceutical, B bath, Z zodiac, C cosmological, A astronomical, S star-recipe, T text-heavy")
    print("likeness and outside are the sources' own sentences, copied. They are not a score.")


def parse_args(argv):
    flags = set()
    positionals = []
    out = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--out":
            out = argv[i + 1]
            i += 2
            continue
        if a.startswith("--"):
            flags.add(a)
        else:
            positionals.append(a)
        i += 1
    return flags, positionals, out


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    flags, positionals, out = parse_args(argv)
    folios, panels, facts = load()
    facts_by = index_facts(facts)
    a1_by = load_a1()
    if positionals:
        return print_folio(positionals[0], facts_by, panels, a1_by, folios)

    ordered = sorted(folios, key=lambda r: folio_key(r["folio"]))
    known = {r["folio"] for r in ordered}
    panel_rows = [
        panel_row(r["folio"], r["section"], r["hand_davis"], facts_by, panels, a1_by)
        for r in ordered
    ]
    # Sources sometimes name a leaf (f89v) instead of a panel (f89v1). Keep those
    # when the leaf carries an image fact. Radiocarbon leaf ids stay out of the index.
    for folio in sorted(set(facts_by) - known, key=folio_key):
        if any(r["attribute"] in FULL_ATTRS for r in facts_by[folio]):
            panel_rows.append(panel_row(folio, "unmapped", "", facts_by, panels, a1_by))
    frag_rows = fragment_rows(facts_by, panels)

    if "--summary" in flags or not out:
        summary(panel_rows, frag_rows)
        unmapped = [r["folio"] for r in panel_rows if r["section"] == "unmapped"]
        print("leaf ids a source did not pin to one panel: " + " ".join(unmapped))
        if not out:
            return 0
    if "--fragments" in flags:
        write_tsv(out, FRAG_COLS, frag_rows)
        n = len(frag_rows)
    else:
        write_tsv(out, PANEL_COLS, panel_rows)
        n = len(panel_rows)
    print(f"wrote {n} rows -> {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
