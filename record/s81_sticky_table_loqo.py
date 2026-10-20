"""s81 -- does a line- or page-sticky Naibbe table cipher predict held-out quires?

PRE-REGISTERED (frozen in s81_sticky_table_loqo.prereg.sha256 BEFORE any real-data run; before the freeze this
script ran only on its synthetic fixture, `--s81-fixture` (distinct flag: s55/s69 read `--fixture` from sys.argv at import), which reads no Voynich transliteration).

QUESTION. s71 (results_s71.txt table 1C) found that a LINE-STICKY Naibbe table cipher (Greshko's Naibbe tables, the
table kept from slot to slot with probability 0.75 inside a line, reset at each line break) enciphering CREMMA Latin
reproduces Voynich's s69 prefix-memory call pattern (C1, C2, C3p, C4p, C5 identical to Voynich's), while default
Naibbe and line-lock do not.  It was never tested on held-out quires.  Does a per-line (or per-page) sticky table
cipher predict the manuscript out of sample?

GENERATORS (code reused: Greshko tables via s64.load_greshko, plaintext letters via s64.norm_letters, the s71
encipher_sticky_naibbe slot procedure re-expressed with a stickiness parameter p and a reset unit):
  per word slot: unigram with probability p_uni (Greshko 0.472), else bigram (prefix piece of letter 1 + suffix piece
  of letter 2); each table draw ("slot") keeps the current table with probability p, else redraws from Greshko's
  78-card deck; the current table is cleared at each reset unit (line or page).
    default          p = 0      (Greshko default; 0 free parameters)
    line_sticky75    p = 0.75, reset per line   (s71's frozen line-sticky; 0 free parameters)
    line_sticky_fit  p fitted,  reset per line   (1 free parameter)
    line_lock        p = 1,    reset per line   (one table per line)
    page_sticky_fit  p fitted,  reset per page   (1 free parameter)
    page_lock        p = 1,    reset per page   (one table per page)
  Plaintexts: CREMMA Latin (runs/s49/lang_latin_cremma, as s71) and Dante Italian (runs/s49/lang_italian_dante, as
  s17/s50/s71).  Text is generated onto the transliteration's own pages with Voynich's exact words-per-line (every
  line of every page), plaintext read continuously in page file order from a start offset drawn from the seed.
  Deck (table-choice probabilities) and p_uni are Greshko's published key and are NOT fitted (fitting them would need
  the plaintext alignment); stickiness p is the only free parameter.
FITTING (training quires only).  p on grid GRID_P.  Target = lag-1 prefix gain (s57 P3 statistic: segmenter and
  add-0.5/Witten-Bell prefix bigram fitted on an inner 80 % of the TRAINING pages, random.Random(SEED), gain on the
  inner 20 %), measured identically on the real training pages and on the cipher's training-like pages (seed CRN,
  fold-independent).  p = argmin |gen - real| (ties -> smaller p).  P3 IS THEREFORE PARTLY BUILT IN BY THE FIT.
SCORING BATTERY, per fold (15 quires with >= 4 ZL3b pages, s67.folds_of), on ZL3b, RF1b, IT2a:
  (a) s67's battery exactly: S57.Measured on generated training-like + held-out-like pages (seeds 1, 2), S57.draws_for,
      S67.score_model (P1 Moran, P2 core->core, P3 prefix gain, P4 jsd_first_fg in s15 width, P5 CHARWIN > 0, P7 types
      within 15 %; small-fold point rules).  Intervals: 80 % page subsampling without replacement, N_DRAW = 500 draws
      (S57 default; s67 itself used 300 -- noted deviation as instructed).
  (b) s69 calls per fold: S69.Text/compute/all_values with the fold split (train = training quires, test = held-out
      quire; S69.split_pages swapped at run time for the fold's training ids), 500 subsamples of 80 % of the held-out
      pages (S69 SEED), S69.calls.  Call set CS = (C1, C2, C3p, C4p, C5) as in s71 table 1C.  A variant's fold MATCHES
      iff its CS booleans (seed-1 cipher text) equal THE s69 CALL PATTERN of the manuscript = the manuscript's CS
      booleans computed by this same code on its full text with s69's own 166/41 split (S69.split_pages, 500
      subsamples); for Voynich this is expected to be T F T F T as in results_s69/s71.  Also reported (not a call):
      'same-fold match' = equality with the manuscript's own CS booleans on the same fold.
      [Changed before the freeze after fixture run 1 failed: same-fold equality compounds the call noise of two
      ~12-page held-out quires (the planted twin matched 3/8 folds, default 2/8); the full-text pattern is the s71
      comparison and separated twin from default on fixture run 1's numbers (5/8 vs 0/8).]
  (c) s55 distance: K_SPLIT = 30 random 80/20 page splits (random.Random(SPLIT_SEED + k)); s55 TextData features of
      Voynich and of each variant (seed-1 text on the s55 Voynich page skeleton; fitted p fitted on s55's own default
      training split) under each split; z-space = S55.prep on the 12 s49 CODE/GEN reference texts (runs/s55/features.csv),
      as s71 1B.  Voynich split-to-split distances d_VV(i<j); variant distances d_GV(i != j) = |z(G_i) - z(V_j)|.
CALLS (pre-registered):
  C1 (primary, s71/s67 rule): a variant PREDICTS held-out quires iff it scores >= 5/6 predictions on >= 8/15 folds on
     all three transliterations.
  C2: a variant reproduces the s69 call pattern iff its fold MATCHES on >= 8/15 folds on each transliteration.
     (C2 is evaluated for every variant; the reading uses the line-sticky variants line_sticky75 and line_sticky_fit.)
  C3: a variant's s55 distance is within Voynich's own split-to-split 95 % range iff median d_GV <= the 97.5th
     percentile of d_VV, on each transliteration.
READINGS (exactly one):
  C1 true for any sticky variant (any variant other than default, either plaintext)
      -> 'per-line table cipher predicts the manuscript' (candidate for decipherment work)
  else C2 false for every line-sticky variant (both plaintexts)
      -> 'call-pattern match in s71 does not survive LOQO'
  else -> 'matches the slot layer, misses the rest' (name which predictions fail; if C3 is false for the
      C2-passing line-sticky variants the s55 distance is named among what it misses -- tie rule fixed before freeze).
FIXTURE-ONLY SCORING CHANGE (fixed before the freeze): P4 (jsd_first_fg inside s15's Voynich width) and P5 (CHARWIN
  > 0) are absolute Voynich targets that a non-Voynich fixture manuscript fails itself (fixture run 1: its own jsd
  0.01-0.08, CHARWIN -0.32..-0.48), so in the fixture only they are re-centred on the manuscript: P4 holds iff
  |gen - real held-out| <= half s15's width (0.03545); P5 holds iff gen and real CHARWIN have the same sign.  The real
  run uses S67.score_model unchanged.
FIXTURE (--s81-fixture, synthetic, no Voynich data): 'manuscript' = line_sticky p = 0.75 Naibbe of CREMMA Latin (start
  offset 70 000, generator seed 999) on a synthetic 8-quire skeleton.  Fixture passes iff line_sticky75_latin meets
  the C1 rule (>= 5/6 on a strict majority of folds) AND the C2 rule (match on a strict majority of folds) AND C3, and
  default_latin fails C1 or C2.
RESOURCES: <= 4 worker processes, BelowNormal priority (lead's rule).  Device: CPU.  The heavy steps (shuffle nulls,
  permutation counts) live inside s55/s57/s67/s69 code that this brief requires to be reused exactly; porting them to
  torch would re-implement the battery, so they stay on CPU (torch.cuda availability is recorded in the header).

Run:    python s81_sticky_table_loqo.py [--s81-fixture]
Writes: results_s81.txt (fixture: runs/s81/fixture.txt) and sidecars in runs/s81/.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import s55_code_vs_generator as S55  # noqa: E402
import s57_local_memory_model as S57  # noqa: E402
import s64_naibbe_taxonomy as S64  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s69_prefix_stream_memory as S69  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s81_sticky_table_loqo.py"
STUB = ROOT / "s81_sticky_table_loqo.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s81"
FIXTURE = "--s81-fixture" in sys.argv
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / "results_s81.txt"

SEED = 20261017
SPLIT_SEED = 81081
N_DRAW = 500
B_SUB69 = 500
SEEDS = (1, 2)
K_SPLIT = 30
NPROC = 4
GRID_P = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
CS = ("C1", "C2", "C3p", "C4p", "C5")
PREDS = S67.PREDS
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
PLAINS = ["latin_cremma", "italian_dante"]
# name -> (reset unit, fixed p or None = fitted)
MECH = OrderedDict([
    ("default", ("line", 0.0)),
    ("line_sticky75", ("line", 0.75)),
    ("line_sticky_fit", ("line", None)),
    ("line_lock", ("line", 1.0)),
    ("page_sticky_fit", ("page", None)),
    ("page_lock", ("page", 1.0)),
])
LINE_STICKY = ("line_sticky75", "line_sticky_fit")
VARIANTS = [(m, pl) for pl in PLAINS for m in MECH]
FIX_PLAIN_START = 70000
FIX_SEED = 999

log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lower_priority():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
    except Exception:
        pass


def local_modules():
    out = []
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if p.suffix == ".py":
            out.append(rel.as_posix())
    return sorted(set(out))


def stub_match():
    if not STUB.exists():
        return "False (no stub)"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split(None, 1)
        if len(parts) < 2 or len(parts[0]) != 64:
            continue
        want[parts[1].lstrip("*").strip()] = parts[0]
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    missing = [m for m in local_modules() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; not in stub: {', '.join(missing) or '-'})"


# ============================================================ generator
_CACHE = {}


def key_tables():
    if "K" not in _CACHE:
        _CACHE["K"] = S64.load_greshko()
    return _CACHE["K"]


def plain_letters(name):
    if name not in _CACHE:
        d = json.loads((S64.S49 / f"lang_{name}.meta.json").read_text(encoding="utf-8"))
        _CACHE[name] = S64.norm_letters([w for pg in d["pages"] for ln in pg["lines"] for w in ln])
    return _CACHE[name]


def encipher(letters, K, skel, unit, p, seed, start=None):
    """skel: list of pages, each a list of words-per-line counts.  -> list of pages (list of lines of words)."""
    rng = random.Random(seed)
    L = len(letters)
    pos = rng.randrange(L) if start is None else start % L
    deck = K["deck"]
    tabs = S64.TABLES

    def draw():
        u = rng.random()
        for t, th in zip(tabs, deck):
            if u < th:
                return t
        return tabs[-1]

    out = []
    for counts in skel:
        cur = None
        lines = []
        for k in counts:
            if unit == "line":
                cur = None
            toks = []
            for _ in range(k):
                kc = 1 if rng.random() < K["p_uni"] else 2
                chunk = letters[pos] if kc == 1 else letters[pos] + letters[(pos + 1) % L]
                pos = (pos + kc) % L
                if cur is None or rng.random() >= p:
                    cur = draw()
                t1 = cur
                if kc == 1:
                    toks.append(K["uni"][(t1, chunk)])
                else:
                    if rng.random() >= p:
                        cur = draw()
                    toks.append(K["pre"][(t1, chunk[0])] + K["suf"][(cur, chunk[1])])
            lines.append(toks)
        out.append(lines)
    return out


def gen_seed(mech, plain, s):
    return 81000 + 100 * PLAINS.index(plain) + 10 * list(MECH).index(mech) + s


# ============================================================ fitting (training pages only)
def p3_inner(pages_lines):
    """lag-1 prefix gain, inner 80/20 split of the given (training) pages.  pages_lines: list of pages (lines)."""
    idx = list(range(len(pages_lines)))
    random.Random(SEED).shuffle(idx)
    n = int(round(0.8 * len(idx)))
    itr, ite = set(idx[:n]), idx[n:]
    seg = SlotSegmenter([w for i in itr for l in pages_lines[i] for w in l])
    cache = {}

    def sp(w):
        v = cache.get(w)
        if v is None:
            v = cache[w] = (seg.segment(w)[0] or "∅")
        return v
    m = S57.Bigram([[sp(w) for w in l] for i in sorted(itr) for l in pages_lines[i]])
    s = np.zeros(3)
    for i in ite:
        for l in pages_lines[i]:
            q = [sp(w) for w in l]
            for a, b in zip(q, q[1:]):
                s += (1, -math.log2(m.pu(b)), -math.log2(m.pb(a, b)))
    return (s[1] - s[2]) / s[0] if s[0] else float("nan")


def fit_p(train_idx, real_pages, skel, unit, plain):
    """train_idx: indices into skel (training pages); real_pages: their real lines (same order)."""
    K = key_tables()
    letters = plain_letters(plain)
    target = p3_inner(real_pages)
    rows = []
    for p in GRID_P:
        full = encipher(letters, K, skel, unit, p, seed=81900 + PLAINS.index(plain))
        g = p3_inner([full[i] for i in train_idx])
        rows.append((abs(g - target), p, g))
    best = min(rows, key=lambda r: (r[0], r[1]))
    return dict(p=best[1], target=target, gen=best[2], grid=[(p, g) for _, p, g in rows])


# ============================================================ s69 per-fold calls
def s69_fold(name, pages, train_ids):
    norm = S69.norm_pages(pages)
    orig = S69.split_pages
    S69.split_pages = lambda _pg, _t=frozenset(train_ids): set(_t)
    try:
        t = S69.Text(name, norm)
    finally:
        S69.split_pages = orig
    W = {k: t.A[k] for k in ("pre", "suf", "core", "cc", "gal")}
    st = S69.compute(t, W)
    point = S69.all_values(st)
    rng = np.random.default_rng(S69.SEED)
    P = t.n_te_pages
    m = max(1, int(round(S69.SUB_FRAC * P)))
    subs = defaultdict(list)
    for _ in range(B_SUB69):
        sel = rng.choice(P, size=m, replace=False)
        for k, v in S69.all_values(st, sel).items():
            subs[k].append(v)
    with np.errstate(all="ignore"):
        ci = {k: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))) for k, v in subs.items()}
    rows, _ = S69.calls({name: dict(point=point, ci=ci)}, [name])
    return dict(calls={c: bool(rows[name][c][0]) for c in CS}, M1=float(point["M1"]),
                k41=float(point.get("k4/k1", float("nan"))))


# ============================================================ fold worker
def run_fold(job):
    lower_priority()
    t0 = time.time()
    S57.N_DRAW = N_DRAW
    T, Q, off = job["T"], job["Q"], job["off"]
    pages = job["pages"]          # [(id, quire, lines)]
    p69 = job["pages69"]          # s69 dicts (id, lines, gaps, para) for the 'manuscript'
    skel = [[len(l) for l in ls] for _, _, ls in pages]
    tr_idx = [i for i, (_, q, _) in enumerate(pages) if q != Q]
    te_idx = [i for i, (_, q, _) in enumerate(pages) if q == Q]
    train = [(pages[i][0], pages[i][2]) for i in tr_idx]
    test = [(pages[i][0], pages[i][2]) for i in te_idx]
    tr_ids = {pages[i][0] for i in tr_idx}
    real_m = S57.Measured(f"{T} {Q} real", train, test)
    real_dr = S57.draws_for([real_m], SEED + off)
    real_pt = real_m.point()
    real_test_pages = [ls for _, ls in test]
    voy69 = s69_fold(f"{T}{Q}real", p69, {p["id"] for p in p69 if p["id"] in tr_ids})
    K = key_tables()
    res = dict(T=T, Q=Q, n_test=len(test), n_train=len(train), real_point={k: float(v) for k, v in real_pt.items()},
               voy69=voy69, models={})
    for j, (mech, plain) in enumerate(VARIANTS):
        unit, p = MECH[mech]
        fit = None
        if p is None:
            fit = fit_p(tr_idx, [pages[i][2] for i in tr_idx], skel, unit, plain)
            p = fit["p"]
        letters = plain_letters(plain)
        gens, texts = [], []
        for s in SEEDS:
            full = encipher(letters, K, skel, unit, p, seed=gen_seed(mech, plain, s))
            texts.append(full)
            gens.append(([(f"g{i}", full[i]) for i in tr_idx], [(f"h{i}", full[i]) for i in te_idx]))
        ms = [S57.Measured(f"{T} {Q} {mech} {plain} s{i}", a, b) for i, (a, b) in enumerate(gens)]
        gen_dr = S57.draws_for(ms, SEED + off + 1 + j)
        cells, gen_pt, rt, small = S67.score_model(real_m, real_pt, real_dr, ms, gen_dr, len(test),
                                                   [[ls for _, ls in b] for _, b in gens], real_test_pages)
        if job.get("fixture"):
            hw = (S57.S15_JSD[1] - S57.S15_JSD[0]) / 2
            d4 = gen_pt["P4"] - real_pt["P4"]
            cells["P4"] = (abs(d4) <= hw, f"[fixture, re-centred] jsd gen {gen_pt['P4']:.4f} real {real_pt['P4']:.4f} |d| <= {hw:.4f}")
            cells["P5"] = ((gen_pt["P5"] > 0) == (real_pt["P5"] > 0), f"[fixture, re-centred] CHARWIN sign gen {gen_pt['P5']:+.4f} real {real_pt['P5']:+.4f}")
        g69_pages = [dict(id=pages[i][0], lines=texts[0][i]) for i in range(len(pages))]
        g69 = s69_fold(f"{T}{Q}{mech}{plain}", g69_pages, tr_ids)
        n = sum(1 for k in PREDS if cells[k][0])
        res["models"][f"{mech}|{plain}"] = dict(
            p=p, fit=fit, n=n, holds={k: bool(cells[k][0]) for k in PREDS}, text={k: cells[k][1] for k in PREDS},
            type_ratio=rt, small=small, s69=g69, match=(g69["calls"] == job["ref_calls"]),
            match_fold=(g69["calls"] == voy69["calls"]))
    res["secs"] = time.time() - t0
    return res


# ============================================================ s55 split-to-split
def s55_job(job):
    """job: name, pages (s55 dicts id/section/lines) -> list of K_SPLIT feature vectors."""
    lower_priority()
    t0 = time.time()
    pages = job["pages"]
    feats = []
    orig = S55.split_pages
    try:
        for k in range(K_SPLIT):
            def sp(pg, _k=k):
                names = [p["id"] for p in pg]
                r = random.Random(SPLIT_SEED + _k)
                r.shuffle(names)
                n = int(round(0.8 * len(names)))
                tr = set(names[:n])
                return [p for p in pg if p["id"] in tr], [p for p in pg if p["id"] not in tr]
            S55.split_pages = sp
            td = S55.TextData(job["name"], pages)
            f, _, _ = td.measure(boot=False)
            feats.append([float(f[c]) for c in S55.FEATS])
    finally:
        S55.split_pages = orig
    return dict(name=job["name"], T=job["T"], feats=feats, secs=time.time() - t0, p=job.get("p"))


def build_s55_jobs(T, voy55, tag):
    """voy55: s55 page dicts of the 'manuscript'.  Variant texts generated on the same skeleton, seed 1."""
    K = key_tables()
    skel = [[len(l) for l in p["lines"]] for p in voy55]
    # fit p on s55's own default training split (S55.split_pages with SEED)
    tr, _ = S55.split_pages(voy55)
    trs = {p["id"] for p in tr}
    tr_idx = [i for i, p in enumerate(voy55) if p["id"] in trs]
    jobs = [dict(name=f"{tag}_{T}", T=T, pages=voy55, p=None)]
    fits = {}
    for mech, plain in VARIANTS:
        unit, p = MECH[mech]
        if p is None:
            fits[(mech, plain)] = fit_p(tr_idx, [voy55[i]["lines"] for i in tr_idx], skel, unit, plain)
            p = fits[(mech, plain)]["p"]
        full = encipher(plain_letters(plain), K, skel, unit, p, seed=gen_seed(mech, plain, 1))
        gp = [dict(id=voy55[i]["id"], section=voy55[i].get("section", "?"), lines=full[i]) for i in range(len(voy55))]
        jobs.append(dict(name=f"{mech}|{plain}", T=T, pages=gp, p=p))
    return jobs, fits


def ref_space():
    ref = {}
    with (ROOT / "runs" / "s55" / "features.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            ref[row["text"]] = [float(row[k]) for k in S55.FEATS]
    lab = json.loads((S64.S49 / "labels.json").read_text(encoding="utf-8"))["labels"]
    core12 = [n for n, c in lab.items() if c in S55.CLS]
    return np.array([ref[n] for n in core12], dtype=float)


def c3_eval(s55res, Ts, tag):
    X12 = ref_space()
    out = {}
    for T in Ts:
        V = S55.prep(X12, np.array(s55res[(T, f"{tag}_{T}")], float))[1]
        dvv = [float(np.linalg.norm(V[i] - V[j])) for i in range(len(V)) for j in range(i + 1, len(V))]
        hi = float(np.percentile(dvv, 97.5))
        out[(T, "VOY")] = dict(dvv_med=float(np.median(dvv)), dvv_lo=float(np.percentile(dvv, 2.5)), dvv_hi=hi)
        for mech, plain in VARIANTS:
            nm = f"{mech}|{plain}"
            G = S55.prep(X12, np.array(s55res[(T, nm)], float))[1]
            dgv = [float(np.linalg.norm(G[i] - V[j])) for i in range(len(G)) for j in range(len(V)) if i != j]
            med = float(np.median(dgv))
            out[(T, nm)] = dict(dgv_med=med, dgv_lo=float(np.percentile(dgv, 2.5)), dgv_hi=float(np.percentile(dgv, 97.5)),
                                ok=med <= hi, hi=hi)
    return out


# ============================================================ summary & verdict
def summarize(allres, folds_by_T, c3, n_folds_need):
    Ts = list(folds_by_T)
    S = {}
    emit("=== PER-VARIANT PER-TRANSLITERATION FOLD COUNTS ===")
    emit("  (n5 = folds with >= 5/6 of P1 P2 P3 P4 P5 P7; match = folds whose s69 (C1,C2,C3p,C4p,C5) equal the manuscript's full-text pattern; sf = same-fold match, reported only)")
    for mech, plain in VARIANTS:
        nm = f"{mech}|{plain}"
        for T in Ts:
            fl = folds_by_T[T]
            rs = [allres[(T, Q)]["models"][nm] for Q in fl]
            n5 = sum(r["n"] >= 5 for r in rs)
            mt = sum(r["match"] for r in rs)
            sf = sum(r["match_fold"] for r in rs)
            cnt = {k: sum(r["holds"][k] for r in rs) for k in PREDS}
            ps = [r["p"] for r in rs]
            S[(nm, T)] = dict(n5=n5, match=mt, cnt=cnt, nf=len(fl))
            emit(f"  {nm:30} {T}: n5 {n5:2}/{len(fl)}  match {mt:2}/{len(fl)} (sf {sf:2})  per-pred " + " ".join(f"{k} {cnt[k]:2}" for k in PREDS)
                 + f"  p {min(ps):.2f}-{max(ps):.2f} (median {float(np.median(ps)):.2f})"
                 + f"  mean n {np.mean([r['n'] for r in rs]):.2f}")
    emit("")
    emit("=== PER-FOLD DETAIL (n/6 and +/- for P1 P2 P3 P4 P5 P7; m = s69 call match) ===")
    for T in Ts:
        emit(f"  {T}:")
        for Q in folds_by_T[T]:
            r = allres[(T, Q)]
            v = r["voy69"]
            emit(f"    {Q} ({r['n_test']} pages{'*' if r['n_test'] < S67.SMALL_FOLD else ''}) Voynich s69 calls "
                 + "".join("T" if v["calls"][c] else "F" for c in CS) + f" M1 {v['M1']:+.4f}")
            for mech, plain in VARIANTS:
                g = r["models"][f"{mech}|{plain}"]
                emit(f"      {mech + '|' + plain:30} {g['n']}/6 " + "".join("+" if g["holds"][k] else "-" for k in PREDS)
                     + f" t{g['type_ratio']:.2f} p{g['p']:.2f} calls " + "".join("T" if g["s69"]["calls"][c] else "F" for c in CS)
                     + f" M1 {g['s69']['M1']:+.4f} {'m' if g['match'] else '.'}")
    emit("")
    emit("=== s55 DISTANCE (C3): median d(variant split i, Voynich split j != i) vs Voynich split-to-split 95 % range ===")
    for T in Ts:
        vv = c3[(T, "VOY")]
        emit(f"  {T}: Voynich split-to-split d median {vv['dvv_med']:.3f} [95 %: {vv['dvv_lo']:.3f}, {vv['dvv_hi']:.3f}]")
        for mech, plain in VARIANTS:
            nm = f"{mech}|{plain}"
            c = c3[(T, nm)]
            emit(f"    {nm:30} d median {c['dgv_med']:.3f} [{c['dgv_lo']:.3f}, {c['dgv_hi']:.3f}] -> {'within' if c['ok'] else 'OUTSIDE'}")
    emit("")
    emit("=== CALLS ===")
    V = {}
    for mech, plain in VARIANTS:
        nm = f"{mech}|{plain}"
        c1 = all(S[(nm, T)]["n5"] >= n_folds_need for T in Ts)
        c2 = all(S[(nm, T)]["match"] >= n_folds_need for T in Ts)
        c3v = all(c3[(T, nm)]["ok"] for T in Ts)
        V[nm] = (c1, c2, c3v)
        emit(f"  {nm:30} C1 {'TRUE ' if c1 else 'false'} (" + ", ".join(f"{T} {S[(nm, T)]['n5']}/{S[(nm, T)]['nf']}" for T in Ts)
             + f")  C2 {'TRUE ' if c2 else 'false'} (" + ", ".join(f"{T} {S[(nm, T)]['match']}/{S[(nm, T)]['nf']}" for T in Ts)
             + f")  C3 {'TRUE' if c3v else 'false'} (" + ", ".join(f"{T} {c3[(T, nm)]['dgv_med']:.2f}<={c3[(T, nm)]['hi']:.2f}" for T in Ts) + ")")
    sticky = [f"{m}|{p}" for m, p in VARIANTS if m != "default"]
    lsv = [f"{m}|{p}" for m, p in VARIANTS if m in LINE_STICKY]
    if any(V[n][0] for n in sticky):
        reading = "per-line table cipher predicts the manuscript"
        detail = "C1 true for " + ", ".join(n for n in sticky if V[n][0])
    elif not any(V[n][1] for n in lsv):
        reading = "call-pattern match in s71 does not survive LOQO"
        detail = "C2 false for every line-sticky variant"
    else:
        reading = "matches the slot layer, misses the rest"
        ok2 = [n for n in lsv if V[n][1]]
        fails = []
        for n in ok2:
            weak = [k for k in PREDS if all(S[(n, T)]["cnt"][k] < n_folds_need for T in Ts)]
            fails.append(f"{n}: C3 {'true' if V[n][2] else 'FALSE (s55 distance outside Voynich range)'}; predictions failing on a majority of folds in every transliteration: {', '.join(weak) or 'none'}")
        detail = "; ".join(fails)
    return reading, detail, V, S


def finish(reading, detail):
    emit("")
    emit(f"VERDICT: '{reading}' ({detail})")


# ============================================================ data loading
def load_real(T):
    path = ROOT / "data" / "translit" / f"{TRANSLITS[T]}.meta.json"
    pages = S67.load_pages(path)
    p69, _ = S69.voynich_pages(T)
    v55 = S55.voynich_pages(T)
    return path, pages, p69, v55


def fixture_data():
    """Synthetic manuscript: line_sticky p=0.75 Naibbe of CREMMA Latin on a random 8-quire skeleton."""
    r = random.Random(4242)
    quires = "ABCDEFGH"
    skel, meta = [], []
    for qi, q in enumerate(quires):
        for k in range(12 if q != "H" else 5):
            n_lines = r.randint(8, 14)
            skel.append([r.randint(5, 11) for _ in range(n_lines)])
            meta.append((f"x{q}{k:02d}", q, "S" + str(qi % 3)))
    full = encipher(plain_letters("latin_cremma"), key_tables(), skel, "line", 0.75, seed=FIX_SEED, start=FIX_PLAIN_START)
    pages = [(pid, q, full[i]) for i, (pid, q, _) in enumerate(meta)]
    p69 = [dict(id=pid, lines=full[i], gaps=None, para=None) for i, (pid, _, _) in enumerate(meta)]
    v55 = [dict(id=pid, section=sec, lines=full[i]) for i, (pid, _, sec) in enumerate(meta)]
    return pages, p69, v55


def device_note():
    try:
        import torch
        return f"cpu (torch {torch.__version__}, cuda available {torch.cuda.is_available()}; not used: battery code reused verbatim on CPU)"
    except Exception as e:  # pragma: no cover
        return f"cpu (torch not importable: {type(e).__name__})"


# ============================================================ main
def main():
    lower_priority()
    t0 = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    emit(f"s81 -- line/page-sticky Naibbe table cipher on the s67 LOQO battery + s69 calls + s55 distance{' [FIXTURE]' if FIXTURE else ''}")
    emit(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (datetime.now)")
    emit(f"stub_match: {stub_match()}")
    emit(f"sha256 {SELF.name}: {sha256(SELF)}")
    emit(f"sha256 {STUB.name}: {sha256(STUB) if STUB.exists() else 'missing'}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"python {sys.version.split()[0]}; numpy {np.__version__}; device {device_note()}; workers {NPROC} (BelowNormal)")
    emit(f"SEED {SEED}; seeds {SEEDS}; N_DRAW {N_DRAW} (80 % held-out pages w/o replacement); s69 B_SUB {B_SUB69}; "
         f"s55 splits {K_SPLIT} (SPLIT_SEED {SPLIT_SEED}); grid p {GRID_P}")
    vdesc = ", ".join(f"{m}({MECH[m][0]}, p={'fit' if MECH[m][1] is None else MECH[m][1]})" for m in MECH)
    emit(f"variants: {vdesc} x {PLAINS}")
    emit("NOTE: stickiness p (fitted variants) is fitted to the training-quire lag-1 prefix gain, so P3 is partly built in by the fit.")
    emit("")
    flush()
    data = {}
    if FIXTURE:
        Ts = ["FIX"]
        data["FIX"] = fixture_data()
        tag = "FIXMS"
    else:
        Ts = list(TRANSLITS)
        for T in Ts:
            path, pages, p69, v55 = load_real(T)
            emit(f"translit {T}: {path.name} sha256={sha256(path)[:16]}; pages {len(pages)} / s69 {len(p69)} / s55 {len(v55)}")
            data[T] = (pages, p69, v55)
        tag = "Voynich"
    folds = S67.folds_of(data[Ts[0]][0])
    n_need = len(folds) // 2 + 1
    emit(f"folds: {folds} ({len(folds)}); threshold (strict majority) {n_need}/{len(folds)}")
    folds_by_T = {}
    for T in Ts:
        c = Counter(q for _, q, _ in data[T][0])
        folds_by_T[T] = [q for q in folds if c.get(q, 0) > 0]
        emit(f"  {T}: pages per fold " + ", ".join(f"{q} {c.get(q, 0)}" for q in folds))
    emit("")
    flush()
    ref_calls = {}
    for T in Ts:
        p69 = data[T][1]
        trs69 = S69.split_pages(S69.norm_pages(p69))
        r = s69_fold(f"{tag}{T}full", p69, trs69)
        ref_calls[T] = r["calls"]
        emit(f"s69 call pattern of the manuscript ({T}, full text, s69 166/41-style split): "
             + " ".join(f"{c}={'T' if r['calls'][c] else 'F'}" for c in CS) + f"; M1 {r['M1']:+.4f}")
    emit("")
    jobs = []
    for ti, T in enumerate(Ts):
        pages, p69, v55 = data[T]
        for fi, Q in enumerate(folds_by_T[T]):
            jobs.append(dict(T=T, Q=Q, pages=pages, pages69=p69, off=1000 * ti + 50 * fi, ref_calls=ref_calls[T],
                             fixture=FIXTURE))
    s55jobs, fitsC3 = [], {}
    for T in Ts:
        j, f = build_s55_jobs(T, data[T][2], tag)
        s55jobs += j
        fitsC3[T] = f
    emit(f"running {len(jobs)} fold jobs + {len(s55jobs)} s55 split jobs on {NPROC} workers")
    flush()
    allres, s55res = {}, {}
    with Pool(NPROC, initializer=lower_priority) as pool:
        a = pool.imap_unordered(run_fold, jobs)
        b = pool.imap_unordered(s55_job, s55jobs)
        for r in a:
            allres[(r["T"], r["Q"])] = r
            print(f"[{time.time() - t0:.0f}s] fold {r['T']} {r['Q']} ({r['secs']:.0f}s)", flush=True)
        for r in b:
            s55res[(r["T"], r["name"])] = r["feats"]
            print(f"[{time.time() - t0:.0f}s] s55 {r['T']} {r['name']} ({r['secs']:.0f}s)", flush=True)
    c3 = c3_eval(s55res, Ts, tag)
    emit("=== C3 FITTED p (fit on s55's default training split) ===")
    for T in Ts:
        emit(f"  {T}: " + "; ".join(f"{m}|{p} p={f['p']}" for (m, p), f in fitsC3[T].items()))
    emit("")
    reading, detail, V, S = summarize(allres, folds_by_T, c3, n_need)
    sfx = "fixture_" if FIXTURE else ""
    (RUN_DIR / f"{sfx}cells.json").write_text(json.dumps({f"{T}|{Q}": r for (T, Q), r in allres.items()}, indent=1,
                                                          default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)),
                                               encoding="utf-8", newline="\n")
    (RUN_DIR / f"{sfx}s55_features.json").write_text(json.dumps({f"{T}|{n}": v for (T, n), v in s55res.items()}),
                                                     encoding="utf-8", newline="\n")
    if FIXTURE:
        ls, df = V["line_sticky75|latin_cremma"], V["default|latin_cremma"]
        ok = ls[0] and ls[1] and ls[2] and not (df[0] and df[1])
        emit("")
        emit(f"FIXTURE: line_sticky75|latin_cremma C1 {ls[0]} C2 {ls[1]} C3 {ls[2]}; default|latin_cremma C1 {df[0]} C2 {df[1]} C3 {df[2]}")
        emit(f"FIXTURE {'PASS' if ok else 'FAIL'}")
        emit(f"(readout only, not a verdict) reading the battery would give: '{reading}'")
    else:
        finish(reading, detail)
    emit(f"elapsed {time.time() - t0:.0f}s; date end {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    emit(f"outputs: {OUT}, {RUN_DIR}")
    flush()
    return 0


if __name__ == "__main__":
    if "--list-imports" in sys.argv:
        for m in local_modules():
            print(m)
        sys.exit(0)
    sys.exit(main())
