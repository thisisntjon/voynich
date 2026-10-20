"""S69: what does the prefix stream remember?  (descriptive measurement with pre-registered calls; no producer)

QUESTION (frozen): the prefix stream (word prefixes along a line) is the most predictable layer: s55's f4_prefix_gain
is about +0.10 bits per prefix on held-out pages (results_s55.txt).  Conditioning on the previous suffix, the previous
prefix or the line's last non-empty prefix never took any producer above +0.04 (s58, s61, s67).  Which context carries
the +0.10: longer prefix history, line position, the previous word's suffix or core class, or the current word's own
core (i.e. core->prefix dependence that merely looks like prefix order)?  Does it reset at line breaks, mid-line
gallows words or drawing gaps, and how fast does it decay with distance?

PRE-REGISTRATION: s69_prefix_stream_memory.prereg.sha256 (sha256sum format) = sha256 of this file and of every local
module it imports, frozen BEFORE any real-text run.  Before the freeze the script ran only with --fixture (synthetic
texts with a planted order-2 prefix chain; reads no real data; writes only runs/s69/fixture.txt).  The script re-hashes
itself and its local imports and prints stub_match.

TEXTS
  Voynich x3: data/translit/{ZL3b_eva, RF1b, IT2a}.meta.json (the s55 loader: pages with non-empty lines).
  References (scored identically, not in any call): the s55 CODE (6) and GEN (6) texts = runs/s49/<name>.meta.json for
  the s49 labels CODE / GEN; Latin prose = data/controls_realline/cremma_prose15.meta.json (s59/s62 reference; 13
  pages -> 10/3 split, so its intervals are coarse).
  Drawing gaps and paragraph starts (Voynich only): the IVTFF source named in each meta.json is re-parsed with
  tools/ivtff_to_meta.clean's rules except that `<->` leaves a gap mark; the word lists must equal the meta.json lines
  exactly (checked and printed), else the gap test is reported n/a.  Paragraph start = locus type char '@'.

SPLIT AND SEGMENTER (s55 verbatim): pages shuffled by random.Random(20261017), first round(0.8 n) = training (166/41
  for ZL3b and RF1b, 165/41 for IT2a).  scoreboard/metrics_new.SlotSegmenter (defaults) fitted on training tokens.
  prefix = segment(w)[0] or "∅"; suffix likewise; core = segment(w)[1].
  Core class (s67 verbatim): top 300 training cores by frequency get a smoothed (ALPHA 5) [prefix | suffix] profile,
  k-means K = 12 (k-means++, 10 restarts, 100 iterations, numpy rng 20261017); other training cores seen >= 2 times go
  to the nearest centroid; training singletons and held-out cores unseen in training -> class 12.

MODELS (fitted on training pages; scored on held-out pages).  Targets = every held-out token at line position j >= 1
  (the s55 f4 target set); every M model scores exactly these targets.  Unigram U = add-0.5 over all training prefixes
  (s40/s55).  Every conditional is Witten-Bell: P(y|h) = (c(h,y) + T(h) Pb(y)) / (c(h) + T(h)), Pb = the back-off
  model's probability, P = Pb when c(h) = 0.  Gain = (sum U bits - sum model bits) / n targets, bits per prefix.
  M1  h = p[j-1]                                  -> U         (= s55 f4; the s55 value is printed beside)
  M2  h = (p[j-2], p[j-1])                        -> M1        (j = 1: M1; history is never padded across the line start)
  M3  h = (p[j-3], p[j-2], p[j-1])                -> M2        (j < 3: M2)
  M4  h = (p[j-1], pos class of j)                -> M1        pos class: first (j=0), last (j=L-1), 2nd (j=1), middle;
                                                               targets have j >= 1, so 'first' never occurs.
  M5  h = (p[j-1], s[j-1])                        -> M1
  M6  h = (p[j-1], coreclass[j-1])                -> M1
  M7  h = coreclass[j]                            -> U         (no history; fitted on ALL training tokens, j >= 0)
  M8  h = (p[j-1], coreclass[j])                  -> M1
  Reported, not in calls: M7c h = core identity[j] -> U (fitted like M7).
  Held-out cross-entropy (bits / prefix) of U and M1 on the targets is printed (as s55).

RESET TESTS (M1's conditional and U, fitted as above; held-out pairs):
  (a) mid-line gallows: target j with 2 <= j <= L-1 whose left word w[j-1] is a gallows word (contains k, t, p or f:
      s37 'any_gallows'; the word sits at 1 <= j-1 <= L-2).  The transition out of the gallows word.
      Reported: (a_ctrl) the same with a non-gallows left word; (a_skip) the lag-2 pair (p[j-2] -> p[j]) straddling a
      mid-line gallows word w[j-1], scored with the skip-2 model of the decay curve, beside (a_skip_ctrl) straddling a
      non-gallows word; (a_pos) a type-matched version: Witten-Bell conditional fitted on training (a) pairs, against an
      add-0.5 unigram of the training (a) targets.
  (b) line break: (last prefix of line n, first prefix of line n+1), consecutive lines of the same page, scored with
      M1's conditional (fitted on within-line pairs only) against U.
      Reported: (b_pos) a position-matched version: Witten-Bell conditional fitted on training cross-line pairs, against
      an add-0.5 unigram of training line-initial prefixes; (b_par) (b) without pairs whose line n+1 starts a
      paragraph (Voynich only).
  (c) drawing gap: within-line adjacent pairs separated by `<->` (Voynich only).
  (d) ordinary within-line adjacent pairs: targets j >= 1 not in (a) and not in (c).
PERSISTENCE: skip-k model h = p[j-k] -> U, fitted on training within-line pairs at distance k, scored on held-out
  targets with j >= k, k = 1..8 (k = 1 is M1).  Ratio gain(k) / gain(1) printed.

NULLS AND INTERVALS
  Null: within-line shuffle of words (prefix, suffix, core, class and gallows flag move together; line positions,
  gap marks and line/paragraph structure stay), applied to training AND held-out pages, all models refitted
  (segmenter and core classes are per word type and need no refit); 200 draws, np.random.default_rng(20261018).
  Every gain is printed with its null mean, sd and excess = gain - null mean.
  Interval: 95 % percentile interval over 500 subsamples of round(0.8 x n held-out pages) without replacement
  (np.random.default_rng(20261017)); models stay fitted on the full training pages.  Differences (M3 - M1 etc.) use
  the same subsamples.

PRE-REGISTERED CALLS (Voynich ZL3b, RF1b, IT2a; each reported per transliteration and overall as
  true = holds on all three, false = holds on none, mixed = otherwise).  Calls use the raw gains and their intervals.
  C1 "prefix order is mostly core-borne": gain(M7) >= 0.6 x gain(M1).
  C2 "longer memory": the interval of gain(M3) - gain(M1) lies above 0 (lower bound > 0).
  C3 "line break resets": the interval of (b) includes 0 AND the interval of (d) lies above 0.
  C4 "gallows resets": the interval of (a) includes 0 AND the interval of (d) lies above 0.
  C5 "decay": gain(k=4) < 0.25 x gain(k=1).
  Added by the s69 author before the freeze, reported beside C3/C4 (C3/C4 stay as worded): the fixture showed that a
  full reset makes M1's conditional score BELOW 0 on the reset pairs (a confident, wrong prediction), so an interval
  that "includes 0" is not the signature of a reset under M1's conditional.  The matched versions are:
  C3p "line break resets (matched)": the interval of (b_pos) has lower bound <= 0 AND the interval of (d) lies above 0.
  C4p "gallows resets (matched)":    the interval of (a_pos) has lower bound <= 0 AND the interval of (d) lies above 0.
No overall verdict.

FIXTURE (pre-freeze only, --fixture): three 'Voynich' slots carry an order-2 prefix chain (p[j] follows a table on
  (p[j-2], p[j-1]) with prob. 0.75; chain restarts every line); references: an order-1 chain and an iid text.  Check:
  C2 must come out true on the three order-2 texts; the order-1 reference's M3 - M1 interval should not lie above 0.
Constraints: python -I, one CPU process, no new data; writes ONLY results_s69.txt and runs/s69/ (fixture: only
runs/s69/fixture.txt).  Wall limit 30 min.
Run: python -I s69_prefix_stream_memory.py            Fixture: python -I s69_prefix_stream_memory.py --fixture
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import re
import subprocess
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s69_prefix_stream_memory.py"
STUB = ROOT / "s69_prefix_stream_memory.prereg.sha256"
S49 = ROOT / "runs" / "s49"
RUN_DIR = ROOT / "runs" / "s69"
SEED = 20261017
NULL_SEED = 20261018
N_NULL = 200
B_SUB = 500
SUB_FRAC = 0.8
K = 12
TOP = 300
ALPHA = 5.0
KMAX = 8
WALL = 30 * 60
EMPTY = "∅"
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
LATIN = ROOT / "data" / "controls_realline" / "cremma_prose15.meta.json"
FIXTURE = "--fixture" in sys.argv
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / "results_s69.txt"
if FIXTURE:
    N_NULL = 40
    B_SUB = 300

M_NAMES = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M7c"]
RESET = ["a", "a_ctrl", "a_pos", "a_skip", "a_skip_ctrl", "b", "b_pos", "b_par", "c", "d"]
DIFFS = [("M2-M1", "M2", "M1"), ("M3-M1", "M3", "M1"), ("M3-M2", "M3", "M2"), ("M4-M1", "M4", "M1"),
         ("M5-M1", "M5", "M1"), ("M6-M1", "M6", "M1"), ("M8-M1", "M8", "M1"), ("M8-M7", "M8", "M7")]

log: list[str] = []
T0 = time.time()


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


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
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    missing = [m for m in local_modules() + [SELF.name] if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; loaded but not in stub: {', '.join(missing) or '-'})"


# ======================================================================= loading
def split_pages(pages):
    names = [p["id"] for p in pages]
    rng = random.Random(SEED)
    rng.shuffle(names)
    n = int(round(0.8 * len(names)))
    tr = set(names[:n])
    return tr


def norm_pages(pages):
    out = []
    for p in pages:
        lines = [[w for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if lines:
            out.append(dict(id=str(p["id"]), lines=lines, gaps=p.get("gaps"), para=p.get("para")))
    return out


# ---- IVTFF re-parse keeping drawing gaps (tools/ivtff_to_meta.clean rules, `<->` -> gap mark)
PAGE_RE = re.compile(r"^<(f\w+)>\s+<!(.*)>")
LINE_RE = re.compile(r"^<(f\w+)\.(\d+),(.)(\w+)>\s*(.*)$")
HDR_RE = re.compile(r"^#=IVTFF\s+(\S+)\s+(\S+)")
GAPMARK = "\x01"


def clean_gap(text, v101=False):
    text = re.sub(r"<![^>]*>", "", text)
    text = re.sub(r"<->", "." + GAPMARK + ".", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\[([^:\]]*)(:[^\]]*)?\]", r"\1", text)
    text = re.sub(r"@\d+;", "?", text)
    text = text.replace("{", "").replace("}", "").replace("'", "")
    if not v101:
        text = text.replace("!", "").replace("*", "?")
    text = text.replace(",", ".")
    return [w for w in text.split(".") if w]


def ivtff_lines(path: Path):
    return ivtff_parse(path.read_text(encoding="utf-8", errors="replace").splitlines())


def ivtff_parse(raw_lines):
    """-> OrderedDict page -> list of (words, gap_before flags, locus char)."""
    alphabet = "?"
    by = OrderedDict()
    for raw in raw_lines:
        if raw.startswith("#"):
            m = HDR_RE.match(raw)
            if m:
                alphabet = m.group(1)
            continue
        m = LINE_RE.match(raw)
        if not m:
            continue
        page, _n, ch, unit, text = m.groups()
        if not unit.startswith("P"):
            continue
        toks = clean_gap(text, v101=alphabet.lower().startswith("v101"))
        words, gaps, pend = [], [], False
        for t in toks:
            if t == GAPMARK:
                pend = True
                continue
            if "?" in t:
                continue
            words.append(t); gaps.append(pend and len(words) > 1); pend = False
        if words:
            by.setdefault(page, []).append((words, gaps, ch))
    return by


def voynich_pages(T):
    path = ROOT / "data" / "translit" / f"{TRANSLITS[T]}.meta.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    pages = norm_pages(d["pages"])
    src = ROOT / d["source"]
    note = ""
    try:
        iv = ivtff_lines(src)
        ok = True
        for p in pages:
            recs = iv.get(p["id"], [])
            if [r[0] for r in recs] != p["lines"]:
                ok = False
                break
        if ok:
            for p in pages:
                recs = iv[p["id"]]
                p["gaps"] = [r[1] for r in recs]
                p["para"] = [r[2] == "@" for r in recs]
            ng = sum(sum(g) for p in pages for g in p["gaps"])
            npar = sum(sum(p["para"]) for p in pages)  # AMENDMENT 1: was sum(sum(x) ...) over bools -> TypeError
            note = f"IVTFF re-parse {src.name} sha256={sha256(src)[:16]} matches meta lines exactly; gap pairs {ng}, paragraph-start lines {npar}"
        else:
            note = f"IVTFF re-parse {src.name} does NOT match meta lines (page {p['id']}); gap/paragraph tests n/a"
    except Exception as e:  # noqa: BLE001
        note = f"IVTFF re-parse failed ({e!r}); gap/paragraph tests n/a"
    return pages, f"{path.name} sha256={sha256(path)[:16]}; " + note


def ref_texts():
    lab = json.loads((S49 / "labels.json").read_text(encoding="utf-8"))["labels"]
    out = OrderedDict()
    for cls in ("CODE", "GEN"):
        for n, c in lab.items():
            if c == cls:
                p = S49 / f"{n}.meta.json"
                out[n] = (cls, norm_pages(json.loads(p.read_text(encoding="utf-8"))["pages"]), f"{p.name} sha256={sha256(p)[:16]}")
    out["latin_cremma_prose15"] = ("LATIN", norm_pages(json.loads(LATIN.read_text(encoding="utf-8"))["pages"]),
                                   f"{LATIN.name} sha256={sha256(LATIN)[:16]}")
    return out


# ======================================================================= core classes (s67 verbatim)
def kmeans(X, k, rng, restarts=10, iters=100):
    best = None
    n = len(X)
    for _ in range(restarts):
        c = [X[rng.integers(n)]]
        for _j in range(1, k):
            d2 = np.min(((X[:, None, :] - np.array(c)[None]) ** 2).sum(-1), axis=1)
            pr = d2 / d2.sum() if d2.sum() > 0 else np.full(n, 1 / n)
            c.append(X[rng.choice(n, p=pr)])
        C = np.array(c)
        lab = None
        for _it in range(iters):
            D = ((X[:, None, :] - C[None]) ** 2).sum(-1)
            nl = D.argmin(1)
            if lab is not None and np.array_equal(nl, lab):
                break
            lab = nl
            for j in range(k):
                if np.any(lab == j):
                    C[j] = X[lab == j].mean(0)
        inertia = float(((X - C[lab]) ** 2).sum())
        if best is None or inertia < best[0]:
            best = (inertia, C.copy(), lab.copy())
    return best


def core_classes(train_lines, seg):
    pre_c, suf_c, gp, gs, cc = defaultdict(Counter), defaultdict(Counter), Counter(), Counter(), Counter()
    for l in train_lines:
        for w in l:
            p, c, s = seg.segment(w)
            pre_c[c][p] += 1; suf_c[c][s] += 1; gp[p] += 1; gs[s] += 1; cc[c] += 1
    pv, sv = sorted(gp), sorted(gs)
    gP = np.array([gp[p] for p in pv], float); gP /= gP.sum()
    gS = np.array([gs[s] for s in sv], float); gS /= gS.sum()

    def prof(c):
        n = cc[c]
        a = (np.array([pre_c[c][p] for p in pv], float) + ALPHA * gP) / (n + ALPHA)
        b = (np.array([suf_c[c][s] for s in sv], float) + ALPHA * gS) / (n + ALPHA)
        return np.concatenate([a, b])

    ranked = sorted(cc, key=lambda c: (-cc[c], c))
    top = ranked[:TOP]
    X = np.array([prof(c) for c in top])
    k = min(K, len(top))
    inertia, C, lab = kmeans(X, k, np.random.default_rng(SEED))
    cls = {c: int(l) for c, l in zip(top, lab)}
    for c in ranked[TOP:]:
        cls[c] = int(((C - prof(c)) ** 2).sum(1).argmin()) if cc[c] >= 2 else K
    sizes = Counter(lab.tolist())
    return cls, [sizes.get(j, 0) for j in range(k)]


# ======================================================================= text arrays
GALLOWS = set("ktpf")


class Text:
    def __init__(self, name, pages):
        self.name = name
        self.pages = pages
        trs = split_pages(pages)
        self.n_tr = sum(p["id"] in trs for p in pages)
        self.n_te = len(pages) - self.n_tr
        train_lines = [ln for p in pages if p["id"] in trs for ln in p["lines"]]
        self.seg = SlotSegmenter([w for ln in train_lines for w in ln])
        self.cls, self.cls_sizes = core_classes(train_lines, self.seg)
        self.has_gaps = all(p.get("gaps") is not None for p in pages)
        ids = defaultdict(dict)
        enc = lambda kind, k: ids[kind].setdefault(k, len(ids[kind]))
        cols = defaultdict(list)
        lid = 0
        te_index = {}
        for pi, p in enumerate(pages):
            is_tr = p["id"] in trs
            if not is_tr:
                te_index[pi] = len(te_index)
            for li, ln in enumerate(p["lines"]):
                L = len(ln)
                for j, w in enumerate(ln):
                    pre, core, suf = self.seg.segment(w)
                    cols["pre"].append(enc("pre", pre or EMPTY)); cols["suf"].append(enc("suf", suf or EMPTY))
                    cols["core"].append(enc("core", core)); cols["cc"].append(self.cls.get(core, K))
                    cols["gal"].append(any(ch in GALLOWS for ch in w))
                    cols["pos"].append(j); cols["L"].append(L); cols["lid"].append(lid); cols["li"].append(li)
                    cols["pg"].append(pi); cols["tr"].append(is_tr)
                    cols["tep"].append(te_index.get(pi, -1))
                    cols["gap"].append(bool(p["gaps"][li][j]) if self.has_gaps else False)
                    cols["para"].append(bool(p["para"][li]) if self.has_gaps else False)
                lid += 1
        self.A = {k: np.array(v) for k, v in cols.items()}
        self.n_pre = len(ids["pre"])
        self.tokens = len(self.A["pre"])
        self.te_tokens = int((~self.A["tr"]).sum())
        self.n_te_pages = len(te_index)
        a = self.A
        pc = np.full(self.tokens, 2)
        pc[a["pos"] == 1] = 1
        pc[a["pos"] == a["L"] - 1] = 3
        pc[a["pos"] == 0] = 0
        a["pc"] = pc

    def shuffled_word_attrs(self, rng):
        a = self.A
        order = np.lexsort((rng.random(self.tokens), a["lid"]))
        return {k: a[k][order] for k in ("pre", "suf", "core", "cc", "gal")}


# ======================================================================= Witten-Bell machinery
B20 = np.int64(1 << 20)


def key(*cols):
    k = np.zeros(len(cols[0]), dtype=np.int64)
    for c in cols:
        k = k * B20 + c.astype(np.int64)
    return k


class WB:
    def __init__(self, ctx, y, ny):
        self.ny = np.int64(ny)
        pk = ctx * self.ny + y.astype(np.int64)
        self.pk, self.pc = np.unique(pk, return_counts=True)
        self.ck, self.cc = np.unique(ctx, return_counts=True)
        tk, self.tc = np.unique(self.pk // self.ny, return_counts=True)
        assert np.array_equal(tk, self.ck)

    @staticmethod
    def _look(keys, vals, q):
        if len(keys) == 0:
            return np.zeros(len(q))
        i = np.searchsorted(keys, q)
        i = np.minimum(i, len(keys) - 1)
        return np.where(keys[i] == q, vals[i], 0).astype(float)

    def prob(self, ctx, y, pb):
        ch = self._look(self.ck, self.cc, ctx)
        T = self._look(self.ck, self.tc, ctx)
        cw = self._look(self.pk, self.pc, ctx * self.ny + y.astype(np.int64))
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(ch > 0, (cw + T * pb) / np.maximum(ch + T, 1e-300), pb)


def add_half(counts_y, ny):
    c = np.bincount(counts_y, minlength=ny).astype(float)
    N = c.sum(); V = int((c > 0).sum())
    return (c + 0.5) / (N + 0.5 * (V + 1))


def compute(t: Text, W):
    """-> dict stat -> (per-held-out-page n, U bits, model bits) arrays (length n_te_pages)."""
    a = t.A
    pre, suf, cc, core, gal = W["pre"], W["suf"], W["cc"], W["core"], W["gal"]
    pos, L, tr, tep, pc = a["pos"], a["L"], a["tr"], a["tep"], a["pc"]
    ny = t.n_pre
    n = t.tokens
    idx = np.arange(n)
    pu = add_half(pre[tr], ny)
    out = {}
    P = t.n_te_pages

    def rec(name, mask, pm, pbase=None):
        sel = mask & ~tr
        y = pre[sel]
        ub = -np.log2((pu if pbase is None else pbase)[y])
        mb = -np.log2(pm[sel])
        pg = tep[sel]
        out[name] = (np.bincount(pg, minlength=P).astype(float), np.bincount(pg, weights=ub, minlength=P),
                     np.bincount(pg, weights=mb, minlength=P))

    def shift(x, k):
        s = np.zeros_like(x)
        s[k:] = x[:-k]
        return s

    p1, p2, p3 = shift(pre, 1), shift(pre, 2), shift(pre, 3)
    s1, c1, g1 = shift(suf, 1), shift(cc, 1), shift(gal, 1)
    E1, E2, E3 = pos >= 1, pos >= 2, pos >= 3
    PU = pu[pre]
    # M1
    m1 = WB(key(p1[E1 & tr]), pre[E1 & tr], ny)
    PM1 = np.ones(n); PM1[E1] = m1.prob(key(p1[E1]), pre[E1], PU[E1])
    rec("M1", E1, PM1)
    # M2, M3 (no padding across line start)
    m2 = WB(key(p2[E2 & tr], p1[E2 & tr]), pre[E2 & tr], ny)
    PM2 = PM1.copy(); PM2[E2] = m2.prob(key(p2[E2], p1[E2]), pre[E2], PM1[E2])
    rec("M2", E1, PM2)
    m3 = WB(key(p3[E3 & tr], p2[E3 & tr], p1[E3 & tr]), pre[E3 & tr], ny)
    PM3 = PM2.copy(); PM3[E3] = m3.prob(key(p3[E3], p2[E3], p1[E3]), pre[E3], PM2[E3])
    rec("M3", E1, PM3)
    # M1-plus models
    for name, extra in (("M4", pc), ("M5", s1), ("M6", c1), ("M8", cc)):
        m = WB(key(p1[E1 & tr], extra[E1 & tr]), pre[E1 & tr], ny)
        PM = np.ones(n); PM[E1] = m.prob(key(p1[E1], extra[E1]), pre[E1], PM1[E1])
        rec(name, E1, PM)
    # M7, M7c: current word only, fitted on all training tokens
    for name, h in (("M7", cc), ("M7c", core)):
        m = WB(key(h[tr]), pre[tr], ny)
        PM = np.ones(n); PM[E1] = m.prob(key(h[E1]), pre[E1], PU[E1])
        rec(name, E1, PM)
    # persistence skip-k
    PK = {}
    for k in range(1, KMAX + 1):
        Ek = pos >= k
        pk_ = shift(pre, k)
        if not np.any(Ek & tr) or not np.any(Ek & ~tr):
            continue
        m = WB(key(pk_[Ek & tr]), pre[Ek & tr], ny)
        PM = np.ones(n); PM[Ek] = m.prob(key(pk_[Ek]), pre[Ek], PU[Ek])
        PK[k] = PM
        rec(f"k{k}", Ek, PM)
    # reset tests
    amask = E2 & g1
    rec("a", amask, PM1)
    rec("a_ctrl", E2 & ~g1, PM1)
    pua = add_half(pre[amask & tr], ny)
    ma = WB(key(p1[amask & tr]), pre[amask & tr], ny)
    PA = np.ones(n); PA[amask] = ma.prob(key(p1[amask]), pre[amask], pua[pre[amask]])
    rec("a_pos", amask, PA, pbase=pua)
    if 2 in PK:
        rec("a_skip", amask, PK[2])
        rec("a_skip_ctrl", E2 & ~g1, PK[2])
    prev_ok = np.zeros(n, bool)
    prev_ok[1:] = (a["pg"][1:] == a["pg"][:-1]) & (a["lid"][1:] == a["lid"][:-1] + 1)
    bmask = (pos == 0) & prev_ok
    PB = np.ones(n); PB[bmask] = m1.prob(key(p1[bmask]), pre[bmask], PU[bmask])
    rec("b", bmask, PB)
    pu0 = add_half(pre[(pos == 0) & tr], ny)
    mb = WB(key(p1[bmask & tr]), pre[bmask & tr], ny)
    PBp = np.ones(n); PBp[bmask] = mb.prob(key(p1[bmask]), pre[bmask], pu0[pre[bmask]])
    rec("b_pos", bmask, PBp, pbase=pu0)
    if t.has_gaps:
        rec("b_par", bmask & ~a["para"], PB)
        rec("c", E1 & a["gap"], PM1)
        rec("d", E1 & ~amask & ~a["gap"], PM1)
    else:
        rec("d", E1 & ~amask, PM1)
    return out


def gain_of(tup, sel=None):
    nn, ub, mb = tup
    if sel is not None:
        nn, ub, mb = nn[sel], ub[sel], mb[sel]
    N = nn.sum()
    return (ub.sum() - mb.sum()) / N if N > 0 else float("nan")


def diff_of(st, A, Bn, sel=None):
    nn, _, ma = st[A]
    _, _, mb = st[Bn]
    if sel is not None:
        nn, ma, mb = nn[sel], ma[sel], mb[sel]
    N = nn.sum()
    return (mb.sum() - ma.sum()) / N if N > 0 else float("nan")


def all_values(st, sel=None):
    v = {k: gain_of(st[k], sel) for k in st}
    for nm, A, Bn in DIFFS:
        v[nm] = diff_of(st, A, Bn, sel)
    if "k1" in st and "k4" in st:
        v["k4/k1"] = v["k4"] / v["k1"] if v["k1"] else float("nan")
    v["M7/M1"] = v["M7"] / v["M1"] if v["M1"] else float("nan")
    return v


def measure(t: Text):
    W = {k: t.A[k] for k in ("pre", "suf", "core", "cc", "gal")}
    st = compute(t, W)
    point = all_values(st)
    rng = np.random.default_rng(SEED)
    P = t.n_te_pages
    m = int(round(SUB_FRAC * P))
    subs = defaultdict(list)
    for _ in range(B_SUB):
        sel = rng.choice(P, size=m, replace=False)
        for k, v in all_values(st, sel).items():
            subs[k].append(v)
    ci = {k: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))) for k, v in subs.items()}
    nrng = np.random.default_rng(NULL_SEED)
    nulls = defaultdict(list)
    for _ in range(N_NULL):
        for k, v in all_values(compute(t, t.shuffled_word_attrs(nrng))).items():
            nulls[k].append(v)
    nul = {k: (float(np.nanmean(v)), float(np.nanstd(v))) for k, v in nulls.items()}
    ns = {k: int(st[k][0].sum()) for k in st}
    xent = (float(st["M1"][1].sum() / st["M1"][0].sum()), float(st["M1"][2].sum() / st["M1"][0].sum()))
    return dict(point=point, ci=ci, null=nul, n=ns, xent=xent)


# ======================================================================= calls
def calls(R, voy):
    def inc0(ci):
        return ci[0] <= 0 <= ci[1]
    rows = OrderedDict()
    for T in voy:
        r = R[T]; p, c = r["point"], r["ci"]
        d_ok = c["d"][0] > 0
        rows[T] = OrderedDict([
            ("C1", (p["M7"] >= 0.6 * p["M1"], f"M7 {p['M7']:+.4f} vs 0.6 x M1 {0.6 * p['M1']:+.4f}")),
            ("C2", (c["M3-M1"][0] > 0, f"M3-M1 {p['M3-M1']:+.4f} [{c['M3-M1'][0]:+.4f}, {c['M3-M1'][1]:+.4f}]")),
            ("C3", (inc0(c["b"]) and d_ok, f"b {p['b']:+.4f} [{c['b'][0]:+.4f}, {c['b'][1]:+.4f}]; d [{c['d'][0]:+.4f}, {c['d'][1]:+.4f}]")),
            ("C4", (inc0(c["a"]) and d_ok, f"a {p['a']:+.4f} [{c['a'][0]:+.4f}, {c['a'][1]:+.4f}]; d [{c['d'][0]:+.4f}, {c['d'][1]:+.4f}]")),
            ("C5", (p["k4"] < 0.25 * p["k1"], f"k4 {p['k4']:+.4f} vs 0.25 x k1 {0.25 * p['k1']:+.4f}")),
            ("C3p", (c["b_pos"][0] <= 0 and d_ok, f"b_pos {p['b_pos']:+.4f} [{c['b_pos'][0]:+.4f}, {c['b_pos'][1]:+.4f}]; d [{c['d'][0]:+.4f}, {c['d'][1]:+.4f}]")),
            ("C4p", (c["a_pos"][0] <= 0 and d_ok, f"a_pos {p['a_pos']:+.4f} [{c['a_pos'][0]:+.4f}, {c['a_pos'][1]:+.4f}]; d [{c['d'][0]:+.4f}, {c['d'][1]:+.4f}]")),
        ])
    out = OrderedDict()
    for C in CALLS:
        v = [rows[T][C][0] for T in voy]
        out[C] = "true" if all(v) else ("false" if not any(v) else "mixed")
    return rows, out


CALLS = ("C1", "C2", "C3", "C4", "C5", "C3p", "C4p")
CALL_TEXT = {"C3p": "line break resets, matched (b_pos lower bound <= 0, d above 0) [author-added, reported beside C3]",
             "C4p": "gallows resets, matched (a_pos lower bound <= 0, d above 0) [author-added, reported beside C4]",
             "C1": "prefix order is mostly core-borne (M7 >= 0.6 x M1)",
             "C2": "longer memory (M3 - M1 interval above 0)",
             "C3": "line break resets (b interval includes 0, d above 0)",
             "C4": "gallows resets (a interval includes 0, d above 0)",
             "C5": "decay (k=4 gain < 0.25 x k=1 gain)"}


# ======================================================================= fixture
def fixture_texts():
    pfx = ["qo", "sh", "ch", "da", "ol", "yk"]
    cores = ["e", "ee", "eo", "a", "ai", "ar", "or", "eey", "ed", "es", "eck", "et", "ep", "aiir", "eel"]
    sfx = ["dy", "in", "m", "s", "l", ""]

    def text(seed, order):
        r = random.Random(seed)
        P = len(pfx)
        t2 = {(i, j): r.randrange(P) for i in range(P) for j in range(P)}
        t1 = {i: r.randrange(P) for i in range(P)}
        pages = []
        for pi in range(60):
            lines = []
            for _ in range(10):
                L = r.randint(7, 11)
                seq = []
                for j in range(L):
                    if order == 2 and j >= 2 and r.random() < 0.75:
                        seq.append(t2[(seq[-2], seq[-1])])
                    elif order == 1 and j >= 1 and r.random() < 0.5:
                        seq.append(t1[seq[-1]])
                    else:
                        seq.append(r.randrange(P))
                lines.append([pfx[s] + r.choice(cores) + r.choice(sfx) for s in seq])
            gaps = [[j > 0 and r.random() < 0.05 for j in range(len(l))] for l in lines]
            pages.append(dict(id=f"p{pi:03d}", lines=lines, gaps=gaps, para=[li % 5 == 0 for li in range(len(lines))]))
        return norm_pages(pages)
    voy = OrderedDict([("FX2_a", text(11, 2)), ("FX2_b", text(12, 2)), ("FX2_c", text(13, 2))])
    refs = OrderedDict([("fx_order1", ("REF", text(21, 1), "synthetic")), ("fx_iid", ("REF", text(22, 0), "synthetic"))])
    return voy, refs


# ======================================================================= main
def fmt_ci(p, ci):
    return f"{p:+.4f} [{ci[0]:+.4f},{ci[1]:+.4f}]"


def main():
    emit("S69: what does the prefix stream remember?  (descriptive; pre-registered calls C1-C5; no producer)"
         + ("  [SYNTHETIC FIXTURE, not reported]" if FIXTURE else ""))
    emit(f"date: {clock()}")
    emit(f"{SELF.name} sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name}" + (f" sha256={sha256(STUB)}" if STUB.exists() else " (absent)") + f"  stub_match={stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit("AMENDMENT 1 (after run 1): run 1 (runs/s69/run1_FAILED_*) lost the gap/paragraph tests to a TypeError in a count "
         "line of voynich_pages (sum over a bool); only that line changed; stub re-hashed with an appended amendment line.")
    emit(f"python {sys.version.split()[0]}; numpy {np.__version__}; seed {SEED}; null {N_NULL} within-line shuffles "
         f"(rng {NULL_SEED}); {B_SUB} subsamples of {SUB_FRAC:.0%} held-out pages without replacement; K={K}, TOP={TOP}")
    emit()
    texts = OrderedDict()   # name -> (class, pages, note)
    if FIXTURE:
        demo = ["#=IVTFF Eva- 2.0", "<f1v.1,@P0>       <%>kchsy.chydaiin.ol<->o,l,tchey.char.cfhar,am",
                "<f1v.2,+P0>       yteey.ch?ar.<->or.ochy<->dcho.lk{o}dy.[a:o]kodar", "<f1v.3,+L0>       label.word"]
        got = ivtff_parse(demo)["f1v"]
        want = [(["kchsy", "chydaiin", "ol", "o", "l", "tchey", "char", "cfhar", "am"], [False, False, False, True] + [False] * 5, "@"),
                (["yteey", "or", "ochy", "dcho", "lkody", "akodar"], [False, True, False, True, False, False], "+")]
        emit(f"  IVTFF gap-parse unit check: {'PASS' if got == want else 'FAIL ' + repr(got)}")
        voy, refs = fixture_texts()
        for n, p in voy.items():
            texts[n] = ("VOY", p, "synthetic order-2 chain")
        texts.update(refs)
    else:
        for T in TRANSLITS:
            pages, note = voynich_pages(T)
            texts[f"Voynich_{T}"] = ("VOY", pages, note)
        texts.update(ref_texts())
    s55 = {}
    f55 = ROOT / "runs" / "s55" / "features.csv"
    if not FIXTURE and f55.exists():
        with f55.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                s55[row["text"]] = float(row["f4_prefix_gain"])
        emit(f"s55 reference: {f55.relative_to(ROOT).as_posix()} sha256={sha256(f55)[:16]} (f4_prefix_gain printed beside M1)")
    for n, (c, _p, note) in texts.items():
        emit(f"  {n:28s} {c:5s} {note}")
    emit()
    flush()

    R, META = OrderedDict(), OrderedDict()
    emit("=== per text: split, segmenter, held-out cross-entropy (bits/prefix on the s55 f4 targets) ===")
    for n, (c, pages, _note) in texts.items():
        if time.time() - T0 > WALL:
            emit(f"STOPPED: wall limit exceeded at {clock()}; partial"); flush(); sys.exit(2)
        t = Text(n, pages)
        r = measure(t)
        R[n] = r
        META[n] = dict(cls=c, tokens=t.tokens, te_tokens=t.te_tokens, tr_pages=t.n_tr, te_pages=t.n_te,
                       prefix_classes=t.n_pre, class_sizes=t.cls_sizes, has_gaps=t.has_gaps,
                       prefixes=sorted(t.seg.prefixes))
        extra = f"  s55 f4 {s55[n]:+.4f}" if n in s55 else ""
        emit(f"  {n:28s} {c:5s} tok {t.tokens:6d} teTok {t.te_tokens:5d} pages {t.n_tr}/{t.n_te} prefixes {t.n_pre:2d} "
             f"H(U) {r['xent'][0]:.4f} H(M1) {r['xent'][1]:.4f} M1 gain {r['point']['M1']:+.4f}{extra}  [{time.time() - T0:.0f}s]")
        flush()
    emit()
    names = list(R)
    voy = [n for n in names if texts[n][0] == "VOY"]

    def table(title, keys, note=""):
        emit(f"=== {title} ===")
        if note:
            emit(note)
        emit("  " + f"{'text':28s} " + " ".join(f"{k:>27s}" for k in keys))
        for n in names:
            r = R[n]
            cells = []
            for k in keys:
                if k in r["point"] and k in r["ci"]:
                    cells.append(f"{fmt_ci(r['point'][k], r['ci'][k]):>27s}")
                else:
                    cells.append(f"{'n/a':>27s}")
            emit("  " + f"{n:28s} " + " ".join(cells))
        emit("  null (within-line shuffle) mean / excess = gain - null mean:")
        for n in names:
            r = R[n]
            cells = []
            for k in keys:
                if k in r["null"] and k in r["point"]:
                    mu, sd = r["null"][k]
                    cells.append(f"{mu:+.4f}/{r['point'][k] - mu:+.4f} z{((r['point'][k] - mu) / sd if sd > 0 else float('nan')):+5.1f}".rjust(27))
                else:
                    cells.append(f"{'n/a':>27s}")
            emit("  " + f"{n:28s} " + " ".join(cells))
        emit()

    table("prefix-model ladder: held-out gain over the add-0.5 unigram, bits/prefix [95 % subsample interval]",
          ["M1", "M2", "M3", "M4"])
    table("prefix-model ladder (cont.)", ["M5", "M6", "M7", "M8", "M7c"],
          "  M7c (core identity, reported only)")
    table("differences (same targets)", ["M2-M1", "M3-M1", "M3-M2", "M4-M1"])
    table("differences (cont.)", ["M5-M1", "M6-M1", "M8-M1", "M8-M7", "M7/M1"])
    emit("=== reset tests: n held-out pairs ===")
    for n in names:
        emit(f"  {n:28s} " + "  ".join(f"{k}={R[n]['n'].get(k, 'n/a')}" for k in RESET))
    emit()
    table("reset tests (M1 conditional; a_skip* use the skip-2 model; a_pos / b_pos are matched)", ["a", "a_ctrl", "a_pos", "a_skip", "a_skip_ctrl"])
    table("reset tests (cont.)", ["b", "b_pos", "b_par", "c", "d"])
    emit("=== persistence: n targets per k ===")
    for n in names:
        emit(f"  {n:28s} " + "  ".join(f"k{k}={R[n]['n'].get(f'k{k}', 'n/a')}" for k in range(1, KMAX + 1)))
    emit()
    table("persistence: gain from the prefix k words back (skip-k), k = 1..4", [f"k{k}" for k in range(1, 5)])
    table("persistence (cont.), k = 5..8", [f"k{k}" for k in range(5, KMAX + 1)])
    emit("=== decay ratio gain(k)/gain(1) (point) ===")
    for n in names:
        p = R[n]["point"]
        emit(f"  {n:28s} " + " ".join(f"k{k} {p[f'k{k}'] / p['k1']:+.3f}" if f"k{k}" in p and p["k1"] else f"k{k} n/a" for k in range(1, KMAX + 1)))
    emit()

    rows, overall = calls(R, voy)
    emit("=== PRE-REGISTERED CALLS (Voynich transliterations) ===")
    for C in CALLS:
        emit(f"  {C} {CALL_TEXT[C]}: {overall[C].upper()}")
        for T in voy:
            ok, s = rows[T][C]
            emit(f"      {T:24s} {'holds' if ok else 'fails'}   {s}")
    emit()
    if FIXTURE:
        emit("=== FIXTURE CHECK ===")
        emit(f"  C2 on the three planted order-2 texts: {overall['C2'].upper()} (required: TRUE) -> "
             + ("PASS" if overall["C2"] == "true" else "FAIL"))
        r = R["fx_order1"]
        emit(f"  order-1 reference M3-M1 {fmt_ci(r['point']['M3-M1'], r['ci']['M3-M1'])} (expected: not above 0) -> "
             + ("PASS" if r["ci"]["M3-M1"][0] <= 0 else "FAIL"))
        emit(f"  planted chain restarts every line: C3 {overall['C3'].upper()}, C3p {overall['C3p'].upper()} (C3p expected TRUE); "
             f"gallows unplanted: C4 {overall['C4'].upper()}, C4p {overall['C4p'].upper()} (both expected FALSE)")
    else:
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        with (RUN_DIR / "gains.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["text", "class", "stat", "n", "gain", "lo95", "hi95", "null_mean", "null_sd", "excess"])
            for n in names:
                r = R[n]
                for k in r["point"]:
                    lo, hi = r["ci"].get(k, (float("nan"), float("nan")))
                    mu, sd = r["null"].get(k, (float("nan"), float("nan")))
                    w.writerow([n, texts[n][0], k, r["n"].get(k, ""), f"{r['point'][k]:.6g}", f"{lo:.6g}", f"{hi:.6g}",
                                f"{mu:.6g}", f"{sd:.6g}", f"{r['point'][k] - mu:.6g}"])
        (RUN_DIR / "meta.json").write_text(json.dumps(dict(texts=META, calls=overall,
                                                            call_rows={T: {C: [bool(v[0]), v[1]] for C, v in rows[T].items()} for T in voy},
                                                            xent={n: R[n]["xent"] for n in names}), indent=1, ensure_ascii=False),
                                           encoding="utf-8", newline="\n")
        emit(f"sidecars: runs/s69/gains.csv, runs/s69/meta.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {clock()}")
    flush()


if __name__ == "__main__":
    main()
