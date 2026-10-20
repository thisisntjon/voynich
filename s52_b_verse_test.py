"""s52 — Is Currier B verse-like in the ways verse is measurably different from prose?

WHY (step brief): at matched size, Currier B's cross-space coupling equals that of short Latin verse (Priapea) while
Currier A matches prose (results_s51.txt, c-369, L-134).

PRE-REGISTERED QUESTION (frozen in s52_b_verse_test.prereg.sha256 before the run):
"On three verse signatures (V1 line-length regularity, V2 adjacent-line ending echo, V3 caesura), computed at
matched line counts, does Voynich Currier B lie inside the verse range and outside the prose range (verse-like),
inside prose and outside verse (prose-like), or neither?  Same for Currier A.  ZL3b decides; RF1b, IT2a agree."

CORPORA (fixed before the run)
  Voynich: ZL3b, RF1b, IT2a; Currier A (IVTFF $L=A) and Currier B ($L=B), P* (paragraph) units only, tokens with '?'
    dropped, empty lines dropped, comma = word break (vparse default = run_v2 --voynich convention).
    Lines are rebuilt here from each IVTFF file (data/ZL3b-n.txt, data/external/voynich-nu-ivtff/RF1b-er.txt,
    .../IT2a-n.txt) with vparse.LINE_RE / vparse.clean so that per-line flags can be kept.  CHECK (STOP on failure):
    rebuilt ZL3b pages equal R2.M.voynich_pages("eva") line for line; rebuilt RF1b / IT2a pages equal the scored
    sidecars data/translit/<t>.meta.json line for line.
    Paragraphs: ZL3b inline markers.  A paragraph starts at a record holding '<%>', at a page change, or at the
      record after one holding '<$>'.  RF1b has no '<%>'/'<$>' markers, so the ZL3b paragraph map, keyed by
      (page, line number), is applied to RF1b and IT2a (line numbering is shared; same locus codes in all three).
    Drawing interruption: the record's own raw text holds '<->'.
  Latin verse (decision set, as named in the brief): CREMMA LaurPlut33.31, LaurPlut39.34, CCCC-MSS-236, Latin8236.
    Latin6395 (Seneca, Medea; "verse" in CREMMA_MANIFEST.md but not named in the brief) is printed as an extra row
    and enters only the sensitivity reading.
  Latin prose (>= 300 lines, prose in CREMMA_MANIFEST.md): Arras-861, BIS-193, H318, CLM13027, Latin16195,
    WettF0015, Mazarine915, UBL758, PalLat373.  Egerton821 (formulaic) printed, no weight.
    CREMMA base-family sidecars data/controls_realline/cremma_<ms>.meta.json, all lines (each < 25k tokens).
    Paragraph proxy: MainZone TextBlock (block_first), the only structural unit CREMMA has (manifest: proxy only).
  s17 verse corpora: mhg_nibelungenlied, oldfrench_roland, occitan_croisade, italian_dante; R2.load_meta +
    R2.subsample(25000) as s17.  Paragraph proxy: the sidecar page (aventiure / laisse / canto).  These are verse
    and join the verse set.
  Glyph unit: one character of the token string (EVA character for Voynich; base-family character, marks stripped,
    for CREMMA; character for s17).

SIGNATURES (computed on a block of lines; each block keeps its lines' source flags)
  interior line = not the first and not the last emitted line of its paragraph (or proxy unit), and no drawing
    interruption.
  V1  line-length regularity: CV = population sd / mean of the line length in glyphs (sum of token lengths) over the
      interior lines of the block (V1g, DECISION); same in words (V1w, reported).  Needs >= 2 interior lines.
  V2  adjacent-line ending echo, k = 2 (V2k2, DECISION) and k = 3 (V2k3, reported):
      adjacent pair = two consecutive lines of the block on the same page whose final tokens both have >= k glyphs;
      adj share = share of adjacent pairs whose final tokens have the same last k glyphs.
      null share = for each page, the share over all unordered pairs of distinct eligible lines of that page in the
      block; averaged over pages weighted by the page's adjacent-pair count (exact, no sampling).
      V2 = adj share - null share.
  V3  caesura (word-boundary density): lines of the block with >= 3 tokens; s = tokens joined by single spaces;
      each space at index i has position (i + 0.5) / len(s), bin = min(9, floor(10 * position)).
      p = share of all within-line boundaries per bin (10 bins).  Null: 20 within-line token shuffles
      (shuffle j uses random.Random(j), lines shuffled in block order), profiles p_1..p_20, mean pbar.
      mid bins = 3, 4, 5, 6 (positions 0.3-0.7).  D(x, y) = sum over mid bins |x_b - y_b|.
      C_obs = D(p, pbar);  C_j = D(p_j, mean of the other 19 null profiles);  V3 = C_obs - mean_j C_j
      (mid-line dip or peak of boundary density beyond what the shuffle null reaches by noise).
  Direction expected by the brief (verse vs prose): V1 lower in verse, V2 higher, V3 higher; the reading below does
    not depend on direction (it uses the ranges).

MATCHED SIZE
  K = 131 lines (LaurPlut39.34, the smallest decision-set corpus).  For every corpus: 500 contiguous blocks of K
  lines, start line uniform over [0, n - K] in corpus order (Voynich: A or B lines in manuscript page order,
  concatenated across pages); rng = random.Random(20261017) re-seeded per cell.  A corpus of exactly K lines gives
  one block (degenerate interval).  Per cell: median and 2.5 / 97.5 % (numpy percentile, linear) of each statistic
  over the draws (nan draws dropped; count printed).  Full-corpus values (no draws) printed beside.

DECISION RULE (fixed before the run; per transliteration, for A and for B)
  verse range = [min, max] of the verse-set cell medians; prose range = [min, max] of the prose-set cell medians.
  On each decision signature (V1g, V2k2, V3) x = the Voynich cell median at K:
    verse-like on that signature if x is inside the verse range and outside the prose range;
    prose-like if inside the prose range and outside the verse range; otherwise neither.
  "B verse-like" if verse-like on >= 2 of 3; "B prose-like" if prose-like on >= 2 of 3; else "neither".  Same for A.
  Margins: for each range, + distance to the nearer edge if inside, - distance to the range if outside.
  ZL3b is the decision row; RF1b, IT2a are agreement rows.  Sensitivity (no decision weight): Latin6395 added to the
  verse set.
  Prediction carried by the brief's hypothesis (from s51): B verse-like, A prose-like.

AMENDMENT 1 (after run 1 crashed, status FAILED, output kept in runs/s52/run1_FAILED_results.txt): Egerton821
  (formulaic, no decision weight) has 114 < K lines, so randint(0, n - K) raised.  A corpus with fewer than K lines
  now gets no draws (cell median/interval nan) and only its full-corpus values are printed.  No decision-set corpus is
  affected (all have >= K lines); nothing else changed.

Run:    python -I s52_b_verse_test.py
Writes: results_s52.txt, runs/s52/cells.tsv.  No other file is touched.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

OUT = ROOT / "results_s52.txt"
RUNS = ROOT / "runs" / "s52"
STUB = ROOT / "s52_b_verse_test.prereg.sha256"
SELF = ROOT / "s52_b_verse_test.py"
SEED = 20261017
DRAWS = 500
K = 131
NSHUF = 20
MID = (3, 4, 5, 6)
IVTFF = {"ZL3b": ROOT / "data" / "ZL3b-n.txt",
         "RF1b": ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt",
         "IT2a": ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt"}
VERSE_LAT = ["LaurPlut33.31", "LaurPlut39.34", "CCCC-MSS-236", "Latin8236"]
EXTRA_VERSE = ["Latin6395"]
PROSE = ["Arras-861", "BIS-193", "H318", "CLM13027", "Latin16195", "WettF0015", "Mazarine915", "UBL758", "PalLat373"]
FORMULAIC = ["Egerton821"]
S17 = ["mhg_nibelungenlied", "oldfrench_roland", "occitan_croisade", "italian_dante"]
STATS = ["V1g", "V1w", "V2k2", "V2k3", "V3"]
DECIDE = ["V1g", "V2k2", "V3"]
log: list[str] = []
tsv: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def load_by_path(modname: str, path: Path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


def pct(vals, q):
    import numpy as np
    return float(np.percentile(np.array(vals, dtype=float), q))


# ---------------------------------------------------------------- loading
def ivtff_records(vp, path):
    """P* records in file order with raw-text flags; mirrors vparse.load + paragraph_text (strict_spaces=False)."""
    meta, out = {}, []
    for raw in path.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = vp.PAGE_RE.match(raw)
        if m:
            meta = dict(vp.VAR_RE.findall(m.group(2)))
            meta["page"] = m.group(1)
            continue
        m = vp.LINE_RE.match(raw)
        if not m:
            continue
        page, n, _, unit, text = m.groups()
        if not unit.startswith("P"):
            continue
        ws = [w for w in vp.clean(text, False) if "?" not in w]
        out.append(dict(page=page, line=int(n), lang=meta.get("L", "?"), words=ws,
                        ps="<%>" in text, pe="<$>" in text, intr="<->" in text))
    return out


def zl_paragraph_map(recs):
    pmap, pid, prev_page, prev_end = {}, -1, None, False
    for r in recs:
        if r["page"] != prev_page or r["ps"] or prev_end:
            pid += 1
        pmap[(r["page"], r["line"])] = pid
        prev_page, prev_end = r["page"], r["pe"]
    return pmap


def voy_entries(recs, pmap):
    """pages (for checks) and entries per lang: dict(words, page, group, intr)."""
    pages, cur, extra = [], None, 0
    ents = {"A": [], "B": []}
    for r in recs:
        if cur is None or cur["id"] != r["page"]:
            cur = dict(id=r["page"], lang=r["lang"], lines=[])
            pages.append(cur)
        if not r["words"]:
            continue
        cur["lines"].append(r["words"])
        key = (r["page"], r["line"])
        if key in pmap:
            g = ("p", pmap[key])
        else:
            extra += 1
            g = ("x", key)
        if r["lang"] in ents:
            ents[r["lang"]].append(dict(words=r["words"], page=r["page"], group=g, intr=r["intr"]))
    return [p for p in pages if p["lines"]], ents, extra


def mark_interior(ents):
    first, last = {}, {}
    for i, e in enumerate(ents):
        first.setdefault(e["group"], i)
        last[e["group"]] = i
    for i, e in enumerate(ents):
        e["interior"] = (first[e["group"]] != i and last[e["group"]] != i and not e["intr"])
    return ents


def cremma_entries(ms):
    d = json.loads((ROOT / "data" / "controls_realline" / f"cremma_{ms}.meta.json").read_text(encoding="utf-8"))
    ents = []
    for p in d["pages"]:
        lines = p["lines"]
        assert all(len(ln) > 0 for ln in lines), f"{ms} {p['id']}: empty line breaks block_first indexing"
        bf = sorted(p.get("block_first") or [0])
        for i, ln in enumerate(lines):
            b = max(j for j, s in enumerate(bf) if s <= i) if any(s <= i for s in bf) else 0
            ents.append(dict(words=[str(t) for t in ln], page=str(p["id"]), group=(str(p["id"]), b), intr=False))
    return mark_interior(ents)


def s17_entries(R2, name):
    _, pages = R2.load_meta(ROOT / "data" / "controls_realline" / f"{name}.meta.json")
    pages = R2.subsample(pages, 25000)
    ents = [dict(words=ln, page=p["id"], group=p["id"], intr=False) for p in pages for ln in p["lines"]]
    return mark_interior(ents)


# ---------------------------------------------------------------- statistics
def cv(xs):
    if len(xs) < 2:
        return math.nan
    m = sum(xs) / len(xs)
    if m == 0:
        return math.nan
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs)) / m


def v1(block):
    inn = [e["words"] for e in block if e["interior"]]
    return cv([sum(len(w) for w in ws) for ws in inn]), cv([len(ws) for ws in inn])


def v2(block, k):
    adj_n = adj_hit = 0
    per_page_adj = {}
    for a, b in zip(block, block[1:]):
        if a["page"] != b["page"]:
            continue
        fa, fb = a["words"][-1], b["words"][-1]
        if len(fa) < k or len(fb) < k:
            continue
        adj_n += 1
        adj_hit += fa[-k:] == fb[-k:]
        per_page_adj[a["page"]] = per_page_adj.get(a["page"], 0) + 1
    if adj_n == 0:
        return math.nan
    ends = {}
    for e in block:
        f = e["words"][-1]
        if len(f) >= k:
            ends.setdefault(e["page"], []).append(f[-k:])
    num = 0.0
    for pg, na in per_page_adj.items():
        xs = ends[pg]
        n = len(xs)
        cnt = {}
        for x in xs:
            cnt[x] = cnt.get(x, 0) + 1
        same = sum(c * (c - 1) / 2 for c in cnt.values())
        num += na * (same / (n * (n - 1) / 2))
    return adj_hit / adj_n - num / adj_n


def profile(lines):
    h = [0] * 10
    for ws in lines:
        s = " ".join(ws)
        L = len(s)
        for i, ch in enumerate(s):
            if ch == " ":
                h[min(9, int(10 * (i + 0.5) / L))] += 1
    t = sum(h)
    return [x / t for x in h] if t else None


def dmid(x, y):
    return sum(abs(x[b] - y[b]) for b in MID)


def v3(block):
    lines = [e["words"] for e in block if len(e["words"]) >= 3]
    p = profile(lines)
    if p is None:
        return math.nan
    nulls = []
    for j in range(NSHUF):
        rng = random.Random(j)
        sh = []
        for ws in lines:
            w = list(ws)
            rng.shuffle(w)
            sh.append(w)
        nulls.append(profile(sh))
    pbar = [sum(q[b] for q in nulls) / NSHUF for b in range(10)]
    cobs = dmid(p, pbar)
    cj = []
    for j in range(NSHUF):
        oth = [sum(nulls[i][b] for i in range(NSHUF) if i != j) / (NSHUF - 1) for b in range(10)]
        cj.append(dmid(nulls[j], oth))
    return cobs - sum(cj) / NSHUF


def stats(block):
    g, w = v1(block)
    return dict(V1g=g, V1w=w, V2k2=v2(block, 2), V2k3=v2(block, 3), V3=v3(block))


def cell(ents, tag):
    n = len(ents)
    rng = random.Random(SEED)
    vals = {s: [] for s in STATS}
    nd = 0 if n < K else (1 if n == K else DRAWS)  # AMENDMENT 1: n < K -> no draws, full-corpus values only
    for d in range(nd):
        s0 = rng.randint(0, n - K)
        st = stats(ents[s0:s0 + K])
        for s in STATS:
            vals[s].append(st[s])
        tsv.append("\t".join([tag, str(d), str(s0)] + [f"{st[s]:.6f}" for s in STATS]))
    out = {}
    for s in STATS:
        v = [x for x in vals[s] if not math.isnan(x)]
        out[s] = dict(med=pct(v, 50), lo=pct(v, 2.5), hi=pct(v, 97.5), n=len(v)) if v else \
            dict(med=math.nan, lo=math.nan, hi=math.nan, n=0)
    out["full"] = stats(ents)
    out["lines"] = n
    out["interior"] = sum(e["interior"] for e in ents)
    return out


# ---------------------------------------------------------------- reading
def margin(x, lo, hi):
    if lo <= x <= hi:
        return min(x - lo, hi - x)
    return -(lo - x) if x < lo else -(x - hi)


def read_one(x, vr, pr):
    iv = vr[0] <= x <= vr[1]
    ip = pr[0] <= x <= pr[1]
    lab = "verse-like" if iv and not ip else ("prose-like" if ip and not iv else "neither")
    return lab, margin(x, *vr), margin(x, *pr)


def reading(cells, voy, verse_set, prose_set, who):
    nv = npz = 0
    parts = []
    for s in DECIDE:
        vm = [cells[c][s]["med"] for c in verse_set]
        pm = [cells[c][s]["med"] for c in prose_set]
        vr, pr = (min(vm), max(vm)), (min(pm), max(pm))
        x = voy[s]["med"]
        lab, mv, mp = read_one(x, vr, pr)
        nv += lab == "verse-like"
        npz += lab == "prose-like"
        parts.append(f"{s} {x:+.4f} verse[{vr[0]:+.4f},{vr[1]:+.4f}] m{mv:+.4f} prose[{pr[0]:+.4f},{pr[1]:+.4f}] m{mp:+.4f} -> {lab}")
    rd = f"{who} verse-like" if nv >= 2 else (f"{who} prose-like" if npz >= 2 else "neither")
    return rd, parts


def fmtc(d):
    return f"{d['med']:+.4f} [{d['lo']:+.4f},{d['hi']:+.4f}]"


def finish(t0, status):
    emit()
    emit(f"status: {status}")
    emit(f"elapsed {time.time() - t0:.1f} s")
    emit(f"run finished {clock()}")
    emit(f"paths: {OUT}  {RUNS / 'cells.tsv'}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "cells.tsv").write_text("cell\tdraw\tstart_line\t" + "\t".join(STATS) + "\n" + "\n".join(tsv) + "\n",
                                    encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


def run(t0) -> int:
    emit("s52: is Currier B verse-like? V1 line-length CV, V2 adjacent-line ending echo, V3 caesura, at matched line count")
    emit(f"run started {clock()}")
    emit(f"s52_b_verse_test.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"K={K} lines; {DRAWS} contiguous-block draws per cell, random.Random({SEED}) re-seeded per cell; V3 {NSHUF} shuffles, mid bins {MID}")
    R2 = load_by_path("run_v2_s52", ROOT / "scoreboard" / "run_v2.py")
    vp = R2.M.vparse
    emit()

    # Voynich
    emit("--- Voynich rebuild checks (STOP on mismatch) ---")
    zrecs = ivtff_records(vp, IVTFF["ZL3b"])
    pmap = zl_paragraph_map(zrecs)
    voy = {}
    ok = True
    for tr in ("ZL3b", "RF1b", "IT2a"):
        recs = zrecs if tr == "ZL3b" else ivtff_records(vp, IVTFF[tr])
        pages, ents, extra = voy_entries(recs, pmap)
        if tr == "ZL3b":
            ref = R2.M.voynich_pages("eva")
            refd = {p["id"]: p["lines"] for p in ref}
        else:
            _, ref = R2.load_meta(ROOT / "data" / "translit" / f"{tr}.meta.json")
            refd = {p["id"]: p["lines"] for p in ref}
        mine = {p["id"]: p["lines"] for p in pages}
        good = mine == refd
        ok &= good
        for L in ("A", "B"):
            mark_interior(ents[L])
        voy[tr] = ents
        emit(f"  {tr}: pages {len(mine)} vs reference {len(refd)} -> {'EQUAL' if good else 'MISMATCH'}; "
             f"A {len(ents['A'])} lines ({sum(e['interior'] for e in ents['A'])} interior), "
             f"B {len(ents['B'])} lines ({sum(e['interior'] for e in ents['B'])} interior); "
             f"interrupted A {sum(e['intr'] for e in ents['A'])} B {sum(e['intr'] for e in ents['B'])}; "
             f"lines without a ZL3b paragraph key {extra}")
    emit(f"  ZL3b paragraphs (P* records, '<%>'/'<$>'/page change): {len(set(pmap.values()))}")
    if not ok:
        emit("STOP: a Voynich rebuild does not equal its reference")
        finish(t0, "STOPPED (rebuild check)")
        return 2
    emit()

    # controls
    ctl = {}
    for ms in VERSE_LAT + EXTRA_VERSE + PROSE + FORMULAIC:
        ctl[ms] = cremma_entries(ms)
    for nm in S17:
        ctl[nm] = s17_entries(R2, nm)

    cells = {}
    emit(f"--- cells: median [2.5 %, 97.5 %] over draws of K={K} lines; 'full' = whole corpus ---")
    emit(f"{'corpus':22} {'set':8} {'lines':>5} {'int':>5} | " + " | ".join(f"{s:>26}" for s in STATS))
    rows = ([(m, "verse", ctl[m]) for m in VERSE_LAT] + [(m, "verse-s17", ctl[m]) for m in S17]
            + [(m, "extra-v", ctl[m]) for m in EXTRA_VERSE] + [(m, "prose", ctl[m]) for m in PROSE]
            + [(m, "formul", ctl[m]) for m in FORMULAIC])
    for m, st, ents in rows:
        c = cell(ents, m)
        cells[m] = c
        emit(f"{m:22} {st:8} {c['lines']:5d} {c['interior']:5d} | " + " | ".join(f"{fmtc(c[s]):>26}" for s in STATS))
        emit(f"{'':22} {'full':8} {'':5} {'':5} | " + " | ".join(f"{c['full'][s]:>+26.4f}" for s in STATS))
    emit(f"  [elapsed so far {time.time() - t0:.0f} s]")
    for tr in ("ZL3b", "RF1b", "IT2a"):
        for L in ("A", "B"):
            nm = f"{tr}-{L}"
            c = cell(voy[tr][L], nm)
            cells[nm] = c
            emit(f"{nm:22} {'voynich':8} {c['lines']:5d} {c['interior']:5d} | " + " | ".join(f"{fmtc(c[s]):>26}" for s in STATS))
            emit(f"{'':22} {'full':8} {'':5} {'':5} | " + " | ".join(f"{c['full'][s]:>+26.4f}" for s in STATS))
    emit(f"  [elapsed so far {time.time() - t0:.0f} s]")
    emit()

    verse_set = VERSE_LAT + S17
    emit("--- ranges of cell medians (verse set = 4 Latin verse + 4 s17; prose set = 9 Latin prose) ---")
    for s in STATS:
        vm = [cells[c][s]["med"] for c in verse_set]
        vl = [cells[c][s]["med"] for c in VERSE_LAT]
        pm = [cells[c][s]["med"] for c in PROSE]
        ov = "overlap" if min(vm) <= max(pm) and min(pm) <= max(vm) else "disjoint"
        mv, mp = sorted(vm)[len(vm) // 2], sorted(pm)[len(pm) // 2]
        emit(f"  {s:5} verse [{min(vm):+.4f}, {max(vm):+.4f}] (Latin verse only [{min(vl):+.4f}, {max(vl):+.4f}])  "
             f"prose [{min(pm):+.4f}, {max(pm):+.4f}]  {ov}; median-of-medians verse {mv:+.4f} prose {mp:+.4f} "
             f"({'verse > prose' if mv > mp else 'verse < prose'}){'  [decision]' if s in DECIDE else ''}")
    emit()

    emit("=== READING (pre-registered rule; ZL3b decides, RF1b / IT2a agree) ===")
    final = {}
    for label, vs in (("main", verse_set), ("sensitivity +Latin6395", verse_set + EXTRA_VERSE)):
        emit(f"[{label}]")
        for tr in ("ZL3b", "RF1b", "IT2a"):
            for L in ("B", "A"):
                rd, parts = reading(cells, cells[f"{tr}-{L}"], vs, PROSE, L)
                final[(label, tr, L)] = rd
                emit(f"  {tr} {L}: {rd}")
                for p in parts:
                    emit(f"      {p}")
    emit()
    emit("summary (main): " + "; ".join(f"{tr} B={final[('main', tr, 'B')]}, A={final[('main', tr, 'A')]}"
                                         for tr in ("ZL3b", "RF1b", "IT2a")))
    emit("summary (sensitivity +Latin6395): " + "; ".join(
        f"{tr} B={final[('sensitivity +Latin6395', tr, 'B')]}, A={final[('sensitivity +Latin6395', tr, 'A')]}"
        for tr in ("ZL3b", "RF1b", "IT2a")))
    finish(t0, "DONE")
    return 0


def main() -> int:
    t0 = time.time()
    try:
        return run(t0)
    except Exception:  # noqa: BLE001
        emit("CRASH:")
        for ln in traceback.format_exc().splitlines():
            emit("  " + ln)
        finish(t0, "FAILED")
        return 3


if __name__ == "__main__":
    sys.exit(main())
