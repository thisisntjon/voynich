"""VKB module: folios, quires, loci, tokens (schema and row rules: tools/vkb/README.md).

Sources (all read-only, all via the tree's own loaders or the same rules they use):
  * Transliterations: data/ZL3b-n.txt, data/external/voynich-nu-ivtff/RF1b-er.txt and IT2a-n.txt
    (the raw IVTFF files behind data/translit/{ZL3b_eva,RF1b,IT2a}.meta.json), parsed with
    vparse.PAGE_RE / LINE_RE / clean (the loader s109, s77 and corpora.py use).
  * Page variables: the ZL3b page headers ($Q quire, $B bifolio number in quire, $F folio letter,
    $I illustration = Zandbergen section map, s109 confirmed 0 mismatches, $L Currier language,
    $H hand).  Davis hand rule from s60/s77/s111: $H if in 1..5, else 3 when quire T or f115r.
  * data/folio_evidence_inventory.tsv (notes; the only MSI statement, f116v "2024 MSI").
  * Stars: runs/s100/star_classes.tsv (321 stars, L-216); s100 scope is quire T (scans 182_103r..205_116v).
  * Images: data/external/yale_scans/pages_index.json mapped by tools/segment_scans.map_canvases (s45 rule).
  * Missing leaves: the ZL3b '# folio(s) N missing' comments.  No collation formula exists in the repo.
  * Segmentations: scoreboard.metrics_new.SlotSegmenter and s77.SegAffix2, both fitted on all ZL3b P*
    tokens of data/translit/ZL3b_eva.meta.json (as s111 does), applied to every token of every translit.
  * n_glyphs: corpora.to_glyphs(word, corpora.GLYPHS) length (the tree's 'glyph' tokenization).
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, rel, create, insert  # noqa: E402

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

TRANSLITS = {
    "ZL3b": "data/ZL3b-n.txt",
    "RF1b": "data/external/voynich-nu-ivtff/RF1b-er.txt",
    "IT2a": "data/external/voynich-nu-ivtff/IT2a-n.txt",
}
INV = "data/folio_evidence_inventory.tsv"
STARS = "runs/s100/star_classes.tsv"
SCANS = "data/external/yale_scans/pages_index.json"
SCAN_DIR = "data/external/yale_scans/pages"
ZL_META = "data/translit/ZL3b_eva.meta.json"
VAR_RE = re.compile(r"\$(\w)=([^\s>]+)")
MISSING_RE = re.compile(r"^#\s*folios?\s+(\d+)(?:\s*-\s*(\d+))?\s+(?:(?:is|are)\s+)?missing", re.I)


def parse_ivtff(path):
    """Pages (header vars, header line) and loci (line_id, marker, unit, words, raw) in file order."""
    import vparse
    pages, loci, missing = {}, [], []
    cur = None
    raw_lines = open(os.path.join(ROOT, path), encoding="ascii", errors="replace").read().splitlines()
    for i, raw in enumerate(raw_lines, 1):
        mm = MISSING_RE.match(raw)
        if mm:
            missing.append((i, int(mm.group(1)), int(mm.group(2) or mm.group(1)), cur, raw.lstrip("# ").strip()))
        if raw.startswith("#") or not raw.strip():
            continue
        m = vparse.PAGE_RE.match(raw)
        if m:
            cur = m.group(1)
            pages[cur] = dict(vars=dict(VAR_RE.findall(m.group(2))), line=i)
            continue
        m = re.match(r"^<(f\w+)\.(\d+),(.)(\w+)>\s+(.*)$", raw)
        if not m:
            continue
        page, n, marker, unit, text = m.groups()
        loci.append(dict(page=page, line_no=int(n), line_id=f"{page}.{n}", marker=marker, unit=unit,
                         words=vparse.clean(text), raw=text, src_line=i))
    return pages, loci, missing


def load_inventory():
    rows = {}
    with open(os.path.join(ROOT, INV), encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f, delimiter="\t"), 2):
            rows[r["folio"]] = dict(r, _line=i)
    return rows


def davis_hand(pid, v):
    """s60/s77/s111 rule (s60_scribe_slot_rules.py:166-170)."""
    h = v.get("H")
    if h in {"1", "2", "3", "4", "5"}:
        return h, "ZL $H"
    if v.get("Q") == "T" or pid == "f115r":
        return "3", "s60/s77 rule: $H not 1-5, quire T or f115r -> Davis Hand 3"
    return None, None


def star_counts():
    c = Counter()
    with open(os.path.join(ROOT, STARS), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            c[r["folio"]] += 1
    return c


def image_map(zl_ids):
    import segment_scans
    index = json.load(open(os.path.join(ROOT, SCANS), encoding="utf-8"))
    matched, unmatched = segment_scans.map_canvases(index, [dict(id=i) for i in zl_ids])
    img = {pid: f"{SCAN_DIR}/{row['file']}" for pid, row in matched}
    cand = defaultdict(list)          # pages with no one-to-one canvas: list candidate canvases in notes
    for label, file, why in unmatched:
        for n, s in re.findall(r"(\d+)\s*([rv])", label):
            base = f"f{n}{s}"
            for pid in zl_ids:
                if pid == base or re.fullmatch(re.escape(base) + r"\d", pid):
                    cand[pid].append(f"{file} ['{label}']")
    return img, cand


def segmenters():
    from scoreboard.metrics_new import SlotSegmenter
    import s77_deconfounded_scribe_and_comma_ablation_loqo as S77
    d = json.load(open(os.path.join(ROOT, ZL_META), encoding="utf-8"))
    toks = [str(w) for p in d["pages"] for ln in p["lines"] for w in ln if w]
    return SlotSegmenter(toks), S77.SegAffix2(toks), len(toks)


def build(conn):
    import corpora
    create(conn, "folios", ["folio TEXT PRIMARY KEY", "quire TEXT", "bifolio TEXT", "conjugate TEXT",
                            "leaf_side TEXT", "panel TEXT", "section TEXT", "illus_type TEXT", "hand_davis TEXT",
                            "currier_lang TEXT", "n_lines INTEGER", "n_tokens INTEGER", "n_label_loci INTEGER",
                            "n_stars INTEGER", "image_path TEXT", "msi INTEGER", "notes TEXT"])
    create(conn, "quires", ["quire TEXT PRIMARY KEY", "collation TEXT", "leaves_present TEXT",
                            "missing_leaves TEXT", "notes TEXT"])
    create(conn, "loci", ["translit TEXT", "folio TEXT", "line_id TEXT", "line_no INTEGER", "locus_type TEXT",
                          "para_start INTEGER", "n_tokens INTEGER", "text TEXT"])
    create(conn, "tokens", ["translit TEXT", "folio TEXT", "line_id TEXT", "pos INTEGER", "word TEXT",
                            "n_glyphs INTEGER", "slot_prefix TEXT", "slot_core TEXT", "slot_suffix TEXT",
                            "a2_prefix TEXT", "a2_core TEXT", "a2_suffix TEXT", "line_initial INTEGER",
                            "line_final INTEGER"])

    slot, aff2, n_fit = segmenters()
    seg_src = f"scoreboard/metrics_new.py SlotSegmenter + s77 SegAffix2 fitted on {n_fit} {ZL_META} P* tokens"
    parsed = {t: parse_ivtff(p) for t, p in TRANSLITS.items()}

    # loci and tokens, all three transliterations
    for t, path in TRANSLITS.items():
        pages, loci, _ = parsed[t]
        has_pct = any("<%>" in x["raw"] for x in loci)
        lrows, trows = [], []
        for x in loci:
            ws = x["words"]
            ptype = x["unit"][0]
            ps = (1 if "<%>" in x["raw"] else 0) if (has_pct and ptype == "P") else None
            src = f"{path}:{x['src_line']}"
            lrows.append(dict(translit=t, folio=x["page"], line_id=x["line_id"], line_no=x["line_no"],
                              locus_type=ptype, para_start=ps, n_tokens=len(ws), text=".".join(ws), src=src))
            for k, w in enumerate(ws):
                sp, sc, ss = slot.segment(w)
                ap, ac, as_ = aff2.segment(w)
                trows.append(dict(translit=t, folio=x["page"], line_id=x["line_id"], pos=k, word=w,
                                  n_glyphs=len(corpora.to_glyphs(w, corpora.GLYPHS)),
                                  slot_prefix=sp, slot_core=sc, slot_suffix=ss, a2_prefix=ap, a2_core=ac,
                                  a2_suffix=as_, line_initial=int(k == 0), line_final=int(k == len(ws) - 1),
                                  src=src))
        insert(conn, "loci", lrows)
        insert(conn, "tokens", trows)

    # folios from ZL3b page headers
    zl_pages, zl_loci, missing = parsed["ZL3b"]
    zpath = TRANSLITS["ZL3b"]
    inv = load_inventory()
    stars = star_counts()
    img, cand = image_map(list(zl_pages))
    by_page = defaultdict(list)
    for x in zl_loci:
        by_page[x["page"]].append(x)

    def leaf(pid):                                        # leaf number, None for ids like fRos
        m = re.match(r"f(\d+)", pid)
        return m.group(1) if m else None
    groups = defaultdict(lambda: defaultdict(set))       # (Q,B) -> $F letter -> leaf numbers
    for pid, pg in zl_pages.items():
        v = pg["vars"]
        if v.get("Q") and v.get("B") and leaf(pid):
            groups[(v["Q"], v["B"])][v.get("F")].add(leaf(pid))

    frows = []
    for pid, pg in zl_pages.items():
        v = pg["vars"]
        q, b = v.get("Q"), v.get("B")
        bif = f"{q}-{b}" if q and b else None
        conj, conj_note = None, None
        if bif and leaf(pid):
            others = sorted({n for f, ns in groups[(q, b)].items() for n in ns} - {leaf(pid)}, key=int)
            if len(others) == 1:
                conj = f"f{others[0]}"
            elif len(others) > 1:
                conj_note = f"bifolio {bif} holds leaves f{leaf(pid)}+" + ",".join("f" + o for o in others)
            else:
                conj_note = f"no conjugate leaf for bifolio {bif} in ZL3b"
        m = re.fullmatch(r"f\d+([rv])(\d*)", pid)
        hand, hand_src = davis_hand(pid, v)
        para = [x for x in by_page[pid] if x["unit"].startswith("P")]
        lab = [x for x in by_page[pid] if x["unit"][0] in "LR"]
        r = inv.get(pid)
        msi, notes = None, []
        if r:
            if "MSI" in r["notes"]:
                msi = 1
            notes.append(f"inventory: {r['notes']}")
        if v.get("C"):
            notes.append(f"ZL $C={v['C']}")
        if v.get("X"):
            notes.append(f"ZL $X={v['X']}")
        if v.get("H") and v.get("H") != hand:
            notes.append(f"ZL $H={v['H']}; {hand_src}")
        if conj_note:
            notes.append(conj_note)
        if pid not in img and cand.get(pid):
            notes.append("no one-to-one Yale canvas (s45 rule); candidates: " + "; ".join(cand[pid]))
        in_s100 = v.get("Q") == "T"
        src = [f"{zpath}:{pg['line']} ($Q $B $F $I $L $H)", f"{zpath} P*/L/R loci (counts)"]
        if r:
            src.append(f"{INV}:{r['_line']} (notes, msi)")
        if in_s100:
            src.append(f"{STARS} (n_stars; s100 scope = quire T)")
        if pid in img:
            src.append(f"{SCANS} via tools/segment_scans.py map_canvases (image)")
        frows.append(dict(folio=pid, quire=q, bifolio=bif, conjugate=conj, leaf_side=m.group(1) if m else None,
                          panel=(m.group(2) or None) if m else None, section=v.get("I"), illus_type=v.get("I"),
                          hand_davis=hand, currier_lang=v.get("L"), n_lines=len(para),
                          n_tokens=sum(len(x["words"]) for x in para), n_label_loci=len(lab),
                          n_stars=stars.get(pid, 0) if in_s100 else None, image_path=img.get(pid), msi=msi,
                          notes="; ".join(notes) or None, src="; ".join(src)))
    insert(conn, "folios", frows)

    # panel_images: every Yale scan that shows a page or foldout panel. image_path above keeps the s45
    # one-to-one rule; panels on shared or partial canvases get all candidate scans here (not cropped).
    create(conn, "panel_images", ["folio TEXT", "image_path TEXT", "kind TEXT", "canvas_label TEXT"])
    prow = []
    extra = {"fRos": [("157_85v_and_86r_foldout.jpg", "85v and 86r (Rosettes foldout, central side)")]}
    for pid in zl_pages:
        if pid in img:
            prow.append(dict(folio=pid, image_path=img[pid], kind="one-to-one", canvas_label=None,
                             src=f"{SCANS} via tools/segment_scans.py map_canvases"))
            continue
        hits = [tuple(re.match(r"(\S+) \['(.*)'\]$", c).groups()) for c in cand.get(pid, [])] + extra.get(pid, [])
        for f, label in hits:
            kind = "shared-canvas" if (" and " in label or "foldout" in label) else "partial-canvas" if "(part)" in label else "panel-of-sheet"
            prow.append(dict(folio=pid, image_path=f"{SCAN_DIR}/{f}", kind=kind, canvas_label=label,
                             src=f"{SCANS} canvas label; panel not cropped" + ("; fRos mapped by hand to the 85v/86r side" if pid in extra else "")))
    insert(conn, "panel_images", prow)

    # quires
    leaves = defaultdict(set)
    first_line = {}
    for pid, pg in zl_pages.items():
        q = pg["vars"].get("Q")
        if q:
            first_line.setdefault(q, pg["line"])
            leaves[q]
            if leaf(pid):
                leaves[q].add(int(leaf(pid)))
    page_q = {pid: pg["vars"].get("Q") for pid, pg in zl_pages.items()}
    order = list(zl_pages)
    miss = defaultdict(list)
    qnotes = defaultdict(list)
    for ln, a, b_, prev, text in missing:
        nxt = None
        later = [p for p in order if zl_pages[p]["line"] > ln]
        if later:
            nxt = later[0]
        qa, qb = page_q.get(prev), page_q.get(nxt)
        span = f"f{a}" if a == b_ else f"f{a}-f{b_}"
        if qa and qa == qb:
            miss[qa].append((span, ln))
        else:
            for qq in {qa, qb} - {None}:
                qnotes[qq].append(f"ZL3b line {ln}: '{text}' lies between {prev} (quire {qa}) and {nxt} "
                                  f"(quire {qb}); quire of the missing leaves not stated")
    qrows = []
    for q in sorted(leaves, key=lambda k: first_line[k]):
        src = [f"{zpath} page headers $Q (leaves_present, from line {first_line[q]})"]
        src += [f"{zpath}:{ln} (missing_leaves)" for _, ln in miss[q]]
        src.append("collation: no collation formula in repo data or docs (NULL)")
        qrows.append(dict(quire=q, collation=None,
                          leaves_present=",".join(f"f{n}" for n in sorted(leaves[q])),
                          missing_leaves=",".join(s for s, _ in miss[q]) or None,
                          notes="; ".join(qnotes[q]) or None, src="; ".join(src)))
    insert(conn, "quires", qrows)
    conn.commit()


if __name__ == "__main__":
    import sqlite3
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "vkb", "test_manuscript.sqlite")
    if os.path.abspath(out) == os.path.abspath(os.path.join(ROOT, "data", "vkb", "vkb.sqlite")):
        sys.exit("refusing to write vkb.sqlite directly; use tools/vkb/build.py")
    if os.path.exists(out):
        os.remove(out)
    conn = sqlite3.connect(out)
    build(conn)
    q = lambda s: conn.execute(s).fetchall()
    for t in ("folios", "quires", "loci", "tokens"):
        print(t, q(f"SELECT COUNT(*) FROM {t}")[0][0])
    print("folios NULL quire/section/hand:",
          q("SELECT SUM(quire IS NULL), SUM(section IS NULL), SUM(hand_davis IS NULL) FROM folios")[0])
    print("tokens per translit:", q("SELECT translit, COUNT(*) FROM tokens GROUP BY translit"))
    print("loci types:", q("SELECT translit, locus_type, COUNT(*) FROM loci GROUP BY 1, 2"))
    print("rows without src:", sum(q(f"SELECT COUNT(*) FROM {t} WHERE src IS NULL OR src=''")[0][0]
                                   for t in ("folios", "quires", "loci", "tokens")))
