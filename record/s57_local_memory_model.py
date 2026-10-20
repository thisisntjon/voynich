"""s57 -- does a fixed local-memory producer (candidate 1, self-citation with local memory) predict untouched pages?

PRE-REGISTERED QUESTION (frozen in s57_local_memory_model.prereg.sha256 BEFORE any fitting on real pages; before the
freeze this script ran only on its synthetic fixture, `--fixture`, which reads no real data):
"A line-by-line producer that copies recent tokens (decaying kernel over the last W tokens, plus the same-position
token on the line above) and varies them with slot edits, fitted ONLY to the core repetition profile, the edit-type
shares, the type count and the line lengths of the 166 training pages, is asked to predict six properties of the 41
held-out pages it never sees.  Does it predict >= 5 of 6?"

MECHANISM (fixed before hashing)
  Inputs, all from the TRAINING pages only (g1_edge_joint.split_names, random.Random(20261017), 166 / 41; IT2a 165 / 41):
    start distribution = frequency of line-initial tokens; lexicon = frequency of all tokens; line lengths (tokens per
    line, empirical); lines per page; scoreboard/metrics_new.SlotSegmenter fitted on the training tokens (prefix /
    suffix inventories = the slot values it assigns to training tokens, weighted by token frequency, "" included);
    core glyph distribution = glyph frequencies inside training cores.
  Page: lines in order; a line's length is drawn from the empirical training line-length distribution.
  Line-initial token: drawn from the start distribution (never copied).
  Each next token: with probability p_copy a copy of an earlier token on the same page:
      with probability a (if the line above is long enough) the same-position token on the line above,
      else the token d back in the page stream (crossing line ends), d in 1..min(W, history), P(d) ~ exp(-(d-1)/tau);
    the copy is passed through ONE edit operator: prefix swap (q_pre: prefix slot replaced by another prefix value
    drawn from the training prefix distribution), suffix swap (q_suf, same on the suffix slot), core 1-glyph edit
    (q_core: substitution / insertion / deletion with probability 1/3 each, deletion only if the core has >= 2 glyphs,
    else substitution; glyph from the training core-glyph distribution), or none (q_none = 1 - q_pre - q_suf - q_core);
    otherwise (1 - p_copy) a fresh token drawn from the training lexicon by frequency.
  W = 20 (fixed, not fitted).  Free parameters: p_copy, tau, a, q_pre, q_suf, q_core = 6.
  Deviations from Timm & Schinner's published generator (data/external/timm-schinner-generator, PageSourceGroupChooser
  + SlimGroupMorpher, conf.properties): T&S copy EVERY token (source = a uniformly chosen earlier line of the page,
  same position with probability 28 %, else a random position; no fresh lexicon draws except 'suggestions' of top
  types at 40 % when -in/-ol/-dy shares are low), always morph (glyph-group replace 50 / add-remove 20 /
  combine-split 30, word-final substitutions), fill lines by character width (55), and seed paragraph-initial lines
  from paragraph-initial sources.  Here: copy with probability p_copy from a distance kernel (s56's decay shape)
  instead of a uniform earlier line; edits are slot-level (prefix / suffix swap from the SlotSegmenter inventories)
  plus a core 1-glyph edit, with an explicit 'none'; fresh tokens come from the training lexicon; line lengths are
  in tokens from the training distribution; line-initial tokens from the training start distribution.

FITTING (on the 166 training pages only; ONLY these targets)
  Targets measured on the real training pages with the training SlotSegmenter (generated text is segmented with the
  same training segmenter during fitting):
    T1 core repetition ratio R(d), d = 1..20 (s56 definition: obs = positions t with core[t] == core[t+d] within a
       page, crossing line ends, summed over pages; exp = the within-page token-shuffle expectation, computed in
       closed form (N_p - d) * sum_u c_u (c_u - 1) / (N_p (N_p - 1)) per page = the limit of s56's 200 shuffles);
    T2 shares of edit types among near-repeat pairs: pairs (t, t+d), d = 1..20, same page, classified as
       identical word / prefix-only differs (same core & suffix) / suffix-only differs / core differs by one glyph
       edit with same prefix & suffix; share = count / sum of the four;
    T3 word type count of a generated text with the training pages' token count;
    T4 line-length distribution: matched by construction (empirical sampling; 0 free parameters; reported).
  Loss = mean_d ((R_g - R_r) / 0.01)^2 + mean_k ((share_g - share_r) / 0.01)^2 + ((V_g - V_r) / V_r / 0.01)^2.
  Method: staged grid search (common random numbers: every candidate generated with seed 0 as 166 pages with the
    training pages' line counts):
    A: q = (0.25, 0.25, 0.25), grid p_copy x tau x a; B: at the best (p_copy, tau, a), q_pre, q_suf, q_core on the
    simplex in steps of 0.1 (q_none >= 0); C: at the best q, p_copy x tau x a again within +-2 / +-1 / +-1 grid steps
    of A's best.  Fit separately per transliteration.  Seeds: 0 fit, 1-3 generate.
  The fitted parameters are written to runs/s57/fit_<T>.json.

PREDICTIONS ON THE 41 HELD-OUT PAGES (the model never sees them)
  Generated texts (seeds 1, 2, 3): 166 'training-like' pages (line counts of the real training pages) + 41
  'held-out-like' pages (line counts = 41 of the training pages' counts, random.Random(seed) without replacement).
  Every statistic is computed on a generated text exactly as on the real one: SlotSegmenter refitted on that text's
  training pages, models trained on its training pages, statistic measured on its held-out pages.
  Interval: page subsampling, 80 % of the 41 held-out pages without replacement (33), 500 draws
    (np.random.default_rng(20261017 + offset)); for the generated side each draw subsamples each seed's 41 pages and
    averages over the 3 seeds; Delta = generated - real per draw; [2.5 %, 97.5 %] percentiles.  Point = mean over
    seeds of the full-41-page value (minus the real full value for Delta).
    P1 within-line Moran I of word length (A5; s39 / s21 lag-1 within-line statistic): Delta interval includes 0 or
       lies above (hi >= 0).
    P2 core->core ordering excess (A14; s55 f2: plug-in MI(C_t; C_t+1) over within-line adjacent held-out pairs minus
       the mean of within-line shuffles, 200 at the point, 20 per draw): Delta interval includes 0.
    P3 prefix-stream held-out bigram gain (s40 / s55 f4: add-0.5 unigram bits minus Witten-Bell bigram bits per
       within-line target, models from training pages): generated point value inside the real value's 80 %-subsample
       interval.
    P4 line-initial first-glyph JSD (jsd_first_fg, score.line_metrics convention: lines >= 3 words, first glyph of the
       first word vs first glyphs of middle words): generated point value inside the s15 41-page width
       [0.1447, 0.2156] (results_s15.txt, ZL3b; the same width is used for RF1b / IT2a).  The excess over 30
       within-line shuffles (a2_position.null) is printed beside.
    P5 CHARWIN (m3 unigram-GT-renorm bits/token minus char3-WB bits/token on the held-out pages, models from the
       training pages): generated point value > 0.
    P6 F1 residual (n1_habit_table.page_sums with training-page lines as train and held-out lines as test, minus the
       same with every line shuffled within itself, random.Random(3), as n1.residual) per stream (prefix-only keep-∅,
       core-only, suffix-only keep-∅): s39 rule (ii) 'F1 in the core layer' = core-only interval lower bound > 0 AND
       prefix-only and suffix-only intervals include 0 (or lie below).  [DEVIATION from s39: the 166/41 page split
       and the 80 % subsample interval replace the quire split and the with-replacement bootstrap.]
  The real values of all six on the same pipeline are printed (P6 rule applied to the real text too, beside).
  VERDICT RULE: count of P1-P6 holding.  "local-memory model predicts untouched pages" iff >= 5 of 6 hold on ZL3b
    AND >= 5 hold on RF1b and on IT2a AND the set of holding predictions is the same on all three; if ZL3b >= 5 but
    the other two differ: "holds on ZL3b only, not stable across transliterations"; else "does not predict".
  NULL PRODUCER: the same six on a frequency-matched non-memory control (p_copy = 0; same start distribution,
    lexicon, line lengths), seeds 1-3, scored with the same rules (count reported; not part of the verdict).
  Caveat stated before the run: P4 is close to built-in (line-initial tokens are drawn from the real training
    start distribution), so P4 holding says little about memory; the null producer shows how much is built in.

Run:    python -I s57_local_memory_model.py [--fixture]
Writes: results_s57.txt, runs/s57/ (fit_<T>.json, sidecars gen_<T>_s<seed>.meta.json and null_<T>_s<seed>.meta.json,
        cells.json; fixture.txt for --fixture).  Nothing else.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
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

import a2_position as A2  # noqa: E402
import g1_edge_joint as G1  # noqa: E402
import m3_bakeoff_reconcile as M3  # noqa: E402
import n1_habit_table as N1  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s57_local_memory_model.py"
STUB = ROOT / "s57_local_memory_model.prereg.sha256"
OUT = ROOT / "results_s57.txt"
RUNS = ROOT / "runs" / "s57"
SEED = 20261017
W = 20
DFIT = 20
N_DRAW = 500
SUB_FRAC = 0.8
N_SHUF_POINT = 200
N_SHUF_DRAW = 20
EMPTY = "∅"
S15_JSD = (0.1447, 0.2156)
STEP_LIMIT = 30 * 60
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
GRID_P = [0.0, 0.02, 0.04, 0.06, 0.08, 0.11, 0.15, 0.20, 0.27, 0.35]
GRID_TAU = [1.0, 2.0, 4.0, 7.0, 12.0, 20.0]
GRID_A = [0.0, 0.15, 0.3, 0.5]
EDIT_KINDS = ["identical", "prefix_swap", "suffix_swap", "core_edit1"]
log: list[str] = []


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
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


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


def load_meta(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    by = OrderedDict()
    for p in d["pages"]:
        lines = [[w for w in l if w] for l in p["lines"]]
        lines = [l for l in lines if l]
        if lines:
            by[str(p["id"])] = lines
    return by


# ======================================================================= edit-1 test
def is_edit1(a: str, b: str) -> bool:
    la, lb = len(a), len(b)
    if a == b or abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


# ======================================================================= fitting statistics
class Encoder:
    """word -> ids (word, prefix, core, suffix) under a fixed segmenter; caches edit-1 decisions on core pairs."""

    def __init__(self, seg):
        self.seg = seg
        self.wid, self.pid, self.cid, self.sid = {}, {}, {}, {}
        self.cstr = []
        self.wrow = []
        self.e1 = {}

    def enc(self, w):
        i = self.wid.get(w)
        if i is None:
            p, c, s = self.seg.segment(w)
            ci = self.cid.get(c)
            if ci is None:
                ci = self.cid[c] = len(self.cid); self.cstr.append(c)
            row = (self.pid.setdefault(p, len(self.pid)), ci, self.sid.setdefault(s, len(self.sid)))
            i = self.wid[w] = len(self.wid)
            self.wrow.append(row)
        return i


def fit_stats(pages, enc: Encoder):
    """pages: list of lines lists.  -> dict(R (DFIT), shares (4), types, tokens, line lengths)."""
    ws, pg = [], []
    for k, lines in enumerate(pages):
        for l in lines:
            for w in l:
                ws.append(enc.enc(w)); pg.append(k)
    w = np.array(ws, dtype=np.int64); pg = np.array(pg, dtype=np.int64)
    rows = np.array(enc.wrow, dtype=np.int64)[w]
    P, C, S = rows[:, 0], rows[:, 1], rows[:, 2]
    # closed-form within-page shuffle expectation
    Np = np.bincount(pg)
    Sp = np.zeros(len(Np))
    key = pg * (int(C.max()) + 1) + C
    u, cnt = np.unique(key, return_counts=True)
    np.add.at(Sp, u // (int(C.max()) + 1), cnt * (cnt - 1))
    R = np.zeros(DFIT); counts = np.zeros(4)
    for d in range(1, DFIT + 1):
        same = pg[:-d] == pg[d:]
        obs = int(np.count_nonzero((C[:-d] == C[d:]) & same))
        m = Np > d
        exp = float(np.sum((Np[m] - d) * Sp[m] / (Np[m] * (Np[m] - 1.0))))
        R[d - 1] = obs / exp if exp > 0 else np.nan
        a, b = slice(None, -d), slice(d, None)
        eqp, eqc, eqs = P[a] == P[b], C[a] == C[b], S[a] == S[b]
        counts[0] += np.count_nonzero(same & (w[a] == w[b]))
        counts[1] += np.count_nonzero(same & ~eqp & eqc & eqs)
        counts[2] += np.count_nonzero(same & eqp & eqc & ~eqs)
        cand = same & eqp & eqs & ~eqc
        if cand.any():
            ca, cb = C[a][cand], C[b][cand]
            K = len(enc.cstr) + 1
            pk, pc = np.unique(np.minimum(ca, cb) * K + np.maximum(ca, cb), return_counts=True)
            tot = 0
            for kk, nn in zip(pk.tolist(), pc.tolist()):
                r = enc.e1.get(kk)
                if r is None:
                    r = enc.e1[kk] = is_edit1(enc.cstr[kk // K], enc.cstr[kk % K])
                if r:
                    tot += nn
            counts[3] += tot
    shares = counts / counts.sum() if counts.sum() else counts
    lens = [len(l) for lines in pages for l in lines]
    return dict(R=R, shares=shares, counts=counts, types=len(set(ws)), tokens=len(ws), lens=lens)


def loss(g, r):
    lr = float(np.mean(((g["R"] - r["R"]) / 0.01) ** 2))
    ls = float(np.mean(((g["shares"] - r["shares"]) / 0.01) ** 2))
    lv = float(((g["types"] - r["types"]) / r["types"] / 0.01) ** 2)
    return lr + ls + lv, (lr, ls, lv)


# ======================================================================= producer
class Producer:
    def __init__(self, train_pages, seg):
        self.seg = seg
        start = Counter(l[0] for lines in train_pages for l in lines)
        lex = Counter(w for lines in train_pages for l in lines for w in l)
        self.start_w, self.start_c = self._cum(start)
        self.lex_w, self.lex_c = self._cum(lex)
        self.lens = [len(l) for lines in train_pages for l in lines]
        self.page_lines = [len(lines) for lines in train_pages]
        pre, suf, gl = Counter(), Counter(), Counter()
        for w, c in lex.items():
            p, co, s = seg.segment(w)
            pre[p] += c; suf[s] += c
            for ch in co:
                gl[ch] += c
        self.pre_w, self.pre_c = self._cum(pre)
        self.suf_w, self.suf_c = self._cum(suf)
        self.gl_w, self.gl_c = self._cum(gl)
        self.set_params(dict(p_copy=0.0, tau=1.0, a=0.0, q_pre=0.25, q_suf=0.25, q_core=0.25))

    @staticmethod
    def _cum(counter):
        items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
        ws = [k for k, _ in items]
        cum, t = [], 0
        for _, c in items:
            t += c; cum.append(t)
        return ws, cum

    def set_params(self, prm):
        self.prm = dict(prm)
        wts = [math.exp(-(d - 1) / prm["tau"]) for d in range(1, W + 1)]
        self.kcum = []
        t = 0.0
        for x in wts:
            t += x; self.kcum.append(t)

    def _swap(self, rng, cur, ws, cum):
        for _ in range(30):
            x = rng.choices(ws, cum_weights=cum)[0]
            if x != cur:
                return x
        return cur

    def edit(self, rng, w):
        p = self.prm
        u = rng.random()
        if u >= p["q_pre"] + p["q_suf"] + p["q_core"]:
            return w
        pre, core, suf = self.seg.segment(w)
        if u < p["q_pre"]:
            pre = self._swap(rng, pre, self.pre_w, self.pre_c)
        elif u < p["q_pre"] + p["q_suf"]:
            suf = self._swap(rng, suf, self.suf_w, self.suf_c)
        else:
            op = rng.randrange(3)
            if op == 2 and len(core) < 2:
                op = 0
            i = rng.randrange(len(core) + (1 if op == 1 else 0))
            if op == 0:
                g = self._swap(rng, core[i], self.gl_w, self.gl_c)
                core = core[:i] + g + core[i + 1:]
            elif op == 1:
                g = rng.choices(self.gl_w, cum_weights=self.gl_c)[0]
                core = core[:i] + g + core[i:]
            else:
                core = core[:i] + core[i + 1:]
        return pre + core + suf

    def page(self, rng, n_lines):
        p = self.prm
        hist, lines = [], []
        for _ in range(n_lines):
            L = rng.choice(self.lens)
            line = [rng.choices(self.start_w, cum_weights=self.start_c)[0]]
            hist.append(line[0])
            for i in range(1, L):
                if p["p_copy"] > 0 and rng.random() < p["p_copy"]:
                    if lines and len(lines[-1]) > i and rng.random() < p["a"]:
                        src = lines[-1][i]
                    else:
                        h = min(W, len(hist))
                        d = rng.choices(range(1, h + 1), cum_weights=self.kcum[:h])[0]
                        src = hist[-d]
                    w = self.edit(rng, src)
                else:
                    w = rng.choices(self.lex_w, cum_weights=self.lex_c)[0]
                line.append(w); hist.append(w)
            lines.append(line)
        return lines

    def text(self, seed, page_line_counts):
        rng = random.Random(seed)
        return [self.page(rng, n) for n in page_line_counts]


def fit(train_pages, seg, emit_fn, budget_t0):
    enc = Encoder(seg)
    real = fit_stats(train_pages, enc)
    prod = Producer(train_pages, seg)
    counts = [len(l) for l in train_pages]
    cache = {}

    def evaluate(prm):
        key = tuple(round(prm[k], 6) for k in ("p_copy", "tau", "a", "q_pre", "q_suf", "q_core"))
        if key in cache:
            return cache[key]
        prod.set_params(prm)
        g = fit_stats(prod.text(0, counts), enc)
        L, parts = loss(g, real)
        cache[key] = (L, parts, g)
        if time.time() - budget_t0 > STEP_LIMIT:
            raise TimeoutError("fitting step exceeded 30 minutes")
        return cache[key]

    q0 = dict(q_pre=0.25, q_suf=0.25, q_core=0.25)
    best = None
    for pc in GRID_P:
        for tau in GRID_TAU:
            for a in GRID_A:
                prm = dict(p_copy=pc, tau=tau, a=a, **q0)
                L = evaluate(prm)[0]
                if best is None or L < best[0]:
                    best = (L, prm)
    emit_fn(f"    stage A ({len(cache)} evals): best loss {best[0]:.2f} at p_copy {best[1]['p_copy']}, tau {best[1]['tau']}, a {best[1]['a']}")
    bA = best[1]
    for i in range(11):
        for j in range(11 - i):
            for k in range(11 - i - j):
                prm = dict(bA, q_pre=i / 10, q_suf=j / 10, q_core=k / 10)
                L = evaluate(prm)[0]
                if L < best[0]:
                    best = (L, prm)
    emit_fn(f"    stage B ({len(cache)} evals): best loss {best[0]:.2f} at q_pre {best[1]['q_pre']}, q_suf {best[1]['q_suf']}, q_core {best[1]['q_core']}")
    bq = {k: best[1][k] for k in ("q_pre", "q_suf", "q_core")}
    ip, it, ia = GRID_P.index(bA["p_copy"]), GRID_TAU.index(bA["tau"]), GRID_A.index(bA["a"])
    for pc in GRID_P[max(0, ip - 2): ip + 3]:
        for tau in GRID_TAU[max(0, it - 1): it + 2]:
            for a in GRID_A[max(0, ia - 1): ia + 2]:
                prm = dict(p_copy=pc, tau=tau, a=a, **bq)
                L = evaluate(prm)[0]
                if L < best[0]:
                    best = (L, prm)
    emit_fn(f"    stage C ({len(cache)} evals): best loss {best[0]:.2f}")
    L, parts, g = evaluate(best[1])
    return dict(params=best[1], loss=L, parts=parts, gen=g, real=real, n_evals=len(cache))


# ======================================================================= held-out statistics
def mi_codes(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    kb = int(b.max()) + 1
    j, cj = np.unique(a.astype(np.int64) * kb + b, return_counts=True)
    ca = np.bincount(a); cb = np.bincount(b)
    ja, jb = j // kb, j % kb
    p = cj / n
    return float(np.sum(p * np.log2(cj * n / (ca[ja].astype(float) * cb[jb]))))


class Bigram:
    """s40 / s55 Bigram: add-0.5 unigram, Witten-Bell bigram."""

    def __init__(self, lines):
        self.uni = Counter(s for ln in lines for s in ln)
        self.N = sum(self.uni.values()); self.V = len(self.uni)
        self.big = defaultdict(Counter)
        for ln in lines:
            for a, b in zip(ln, ln[1:]):
                self.big[a][b] += 1
        self.tot = {a: sum(c.values()) for a, c in self.big.items()}

    def pu(self, w):
        return (self.uni.get(w, 0) + 0.5) / (self.N + 0.5 * (self.V + 1))

    def pb(self, a, w):
        c = self.big.get(a)
        if not c:
            return self.pu(w)
        T = len(c)
        return (c.get(w, 0) + T * self.pu(w)) / (self.tot[a] + T)


class Measured:
    """All held-out statistics of one text (real or generated), with per-page sufficient rows for subsampling."""

    def __init__(self, name, train, test):
        """train, test: lists of (page id, lines)."""
        t0 = time.time()
        self.name = name
        self.n_test = len(test)
        tr_tokens = [w for _, ls in train for l in ls for w in l]
        seg = SlotSegmenter(tr_tokens)
        sg = seg.segment
        self.n_prefix, self.n_suffix = len(seg.prefixes), len(seg.suffixes)
        # Moran (word length), core codes for P2
        core_id = {}
        self.pages = []
        for pid, ls in test:
            lens, lid, cores = [], [], []
            for li, l in enumerate(ls):
                for w in l:
                    lens.append(len(w)); lid.append(li); cores.append(core_id.setdefault(sg(w)[1], len(core_id)))
            self.pages.append(dict(x=np.array(lens, float), lid=np.array(lid, np.int64), c=np.array(cores, np.int64)))
        # P3 prefix gain rows
        tr_pre = [[sg(w)[0] or EMPTY for w in l] for _, ls in train for l in ls]
        m = Bigram(tr_pre)
        self.gain = np.zeros((len(test), 3))
        for k, (_, ls) in enumerate(test):
            for l in ls:
                s = [sg(w)[0] or EMPTY for w in l]
                for a, b in zip(s, s[1:]):
                    self.gain[k] += (1, -math.log2(m.pu(b)), -math.log2(m.pb(a, b)))
        # P4 jsd_first_fg
        test_lines = [l for _, ls in test for l in ls]
        self.jsd = float(A2.stats(test_lines, lambda w: w[0])[0])
        self.jsd_exc = self.jsd - float(A2.null(test_lines, lambda w: w[0], n=30)[:, 0].mean())
        # P5 CHARWIN
        pages = [dict(id=str(p), lines=ls) for p, ls in train] + [dict(id=str(p), lines=ls) for p, ls in test]
        acc = M3.score_folds(pages, [list(range(len(train), len(pages)))])
        rn, wb = acc["unigram-GT-renorm"], acc["char3-WB"]
        self.charwin = rn["bits"] / rn["tok"] - wb["bits"] / wb["tok"]
        # P6 F1 per stream
        self.f1 = {}
        ids = [str(p) for p, _ in test]
        for name_s, slot in (("prefix", 0), ("core", 1), ("suffix", 2)):
            tr_l = [[sg(w)[slot] or EMPTY for w in l] for _, ls in train for l in ls]
            te_pl = [(str(p), [sg(w)[slot] or EMPTY for w in l]) for p, ls in test for l in ls]
            real = N1.page_sums(tr_l, te_pl)
            rng = random.Random(3)
            sh_tr = [rng.sample(l, len(l)) for l in tr_l]
            sh_te = [(p, rng.sample(l, len(l))) for p, l in te_pl]
            shuf = N1.page_sums(sh_tr, sh_te)
            z = np.zeros(3)
            self.f1[name_s] = np.array([np.concatenate([real.get(p, z), shuf.get(p, z)]) for p in ids])
        self.p2_point = self.core_core(np.arange(self.n_test), N_SHUF_POINT, np.random.default_rng(SEED))
        self.secs = time.time() - t0

    # ---- subset statistics
    def concat(self, idx):
        xs, ls, cs, off = [], [], [], 0
        for i in idx:
            pg = self.pages[i]
            xs.append(pg["x"]); cs.append(pg["c"]); ls.append(pg["lid"] + off)
            off += int(pg["lid"].max()) + 1 if len(pg["lid"]) else 0
        return np.concatenate(xs), np.concatenate(ls), np.concatenate(cs)

    def moran(self, idx):
        x, lid, _ = self.concat(idx)
        left = np.nonzero(lid[1:] == lid[:-1])[0]
        z = x - x.mean()
        d = float(np.dot(z, z))
        return float(len(x) / len(left) * np.dot(z[left], z[left + 1]) / d) if d > 0 and len(left) else float("nan")

    def core_core(self, idx, n_shuf, rng):
        _, lid, c = self.concat(idx)
        left = np.nonzero(lid[1:] == lid[:-1])[0]; right = left + 1
        obs = mi_codes(c[left], c[right])
        null = []
        for _ in range(n_shuf):
            perm = np.lexsort((rng.random(len(c)), lid))
            y = c[perm]
            null.append(mi_codes(y[left], y[right]))
        return obs - float(np.mean(null))

    def gain_stat(self, idx):
        s = self.gain[idx].sum(0)
        return (s[1] - s[2]) / s[0] if s[0] else float("nan")

    def f1_stat(self, stream, idx):
        r = self.f1[stream][idx].sum(0)
        return (r[1] - r[2]) / r[0] - (r[4] - r[5]) / r[3]

    def point(self):
        a = np.arange(self.n_test)
        return dict(P1=self.moran(a), P2=self.p2_point, P3=self.gain_stat(a), P4=self.jsd, P4_exc=self.jsd_exc,
                    P5=self.charwin, F1_prefix=self.f1_stat("prefix", a), F1_core=self.f1_stat("core", a),
                    F1_suffix=self.f1_stat("suffix", a))

    def draw(self, idx, rng):
        return dict(P1=self.moran(idx), P2=self.core_core(idx, N_SHUF_DRAW, rng), P3=self.gain_stat(idx),
                    F1_prefix=self.f1_stat("prefix", idx), F1_core=self.f1_stat("core", idx),
                    F1_suffix=self.f1_stat("suffix", idx))


DRAW_KEYS = ["P1", "P2", "P3", "F1_prefix", "F1_core", "F1_suffix"]


def draws_for(ms, seed):
    """ms: list of Measured (averaged per draw).  -> dict key -> array (N_DRAW)."""
    rng = np.random.default_rng(seed)
    k = max(1, int(round(SUB_FRAC * ms[0].n_test)))
    out = {key: np.zeros(N_DRAW) for key in DRAW_KEYS}
    for b in range(N_DRAW):
        vals = defaultdict(list)
        for m in ms:
            idx = rng.choice(m.n_test, size=k, replace=False)
            for key, v in m.draw(idx, rng).items():
                vals[key].append(v)
        for key in DRAW_KEYS:
            out[key][b] = float(np.mean(vals[key]))
    return out


def pct(a):
    return float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))


def mean_point(ms):
    pts = [m.point() for m in ms]
    return {k: float(np.mean([p[k] for p in pts])) for k in pts[0]}, pts


def f1_layer_call(ci):
    ex = lambda s: ci[s][0] > 0
    inc = lambda s: ci[s][0] <= 0 <= ci[s][1] or ci[s][1] < 0
    if ex("F1_core") and inc("F1_prefix") and inc("F1_suffix"):
        return "core layer"
    if (ex("F1_prefix") or ex("F1_suffix")) and inc("F1_core"):
        return "affix layer"
    return "both / neither"


def score_cells(real_pt, real_dr, gen_pt, gen_dr):
    """-> dict P1..P6 -> (holds, text)."""
    cells = {}
    d1 = gen_dr["P1"] - real_dr["P1"]; lo, hi = pct(d1); pd = gen_pt["P1"] - real_pt["P1"]
    cells["P1"] = (hi >= 0, f"Moran Δ {pd:+.4f} [{lo:+.4f},{hi:+.4f}] (gen {gen_pt['P1']:.4f}, real {real_pt['P1']:.4f}); margin hi-0 = {hi:+.4f}")
    d2 = gen_dr["P2"] - real_dr["P2"]; lo, hi = pct(d2); pd = gen_pt["P2"] - real_pt["P2"]
    cells["P2"] = (lo <= 0 <= hi, f"core->core excess Δ {pd:+.4f} [{lo:+.4f},{hi:+.4f}] (gen {gen_pt['P2']:+.4f}, real {real_pt['P2']:+.4f}); "
                                  f"margins 0-lo {0 - lo:+.4f}, hi-0 {hi:+.4f}")
    lo, hi = pct(real_dr["P3"]); g = gen_pt["P3"]
    cells["P3"] = (lo <= g <= hi, f"prefix gain gen {g:+.4f} vs real {real_pt['P3']:+.4f} [{lo:+.4f},{hi:+.4f}]; margins g-lo {g - lo:+.4f}, hi-g {hi - g:+.4f}")
    g = gen_pt["P4"]
    cells["P4"] = (S15_JSD[0] <= g <= S15_JSD[1], f"jsd_first_fg gen {g:.4f} vs s15 width [{S15_JSD[0]},{S15_JSD[1]}] (real held-out {real_pt['P4']:.4f}); "
                                                  f"margins {g - S15_JSD[0]:+.4f} / {S15_JSD[1] - g:+.4f}; excess gen {gen_pt['P4_exc']:+.4f} real {real_pt['P4_exc']:+.4f}")
    g = gen_pt["P5"]
    cells["P5"] = (g > 0, f"CHARWIN gen {g:+.4f} (real {real_pt['P5']:+.4f}); margin {g:+.4f}")
    ci = {k: pct(gen_dr[k]) for k in ("F1_prefix", "F1_core", "F1_suffix")}
    call = f1_layer_call(ci)
    cells["P6"] = (call == "core layer", "F1 gen: " + ", ".join(f"{k[3:]} {gen_pt[k]:+.4f} [{ci[k][0]:+.4f},{ci[k][1]:+.4f}]" for k in ci)
                   + f" -> {call}; core lo margin {ci['F1_core'][0]:+.4f}")
    return cells


# ======================================================================= one transliteration
def run_translit(T, by, emit_fn, t_start, out_dir: Path, real_name="real"):
    train_names, held_names = G1.split_names(by)
    train = [(p, by[p]) for p in train_names]
    test = [(p, by[p]) for p in held_names]
    tr_tok = [w for _, ls in train for l in ls for w in l]
    seg = SlotSegmenter(tr_tok)
    emit_fn(f"=== {T}: {len(by)} pages; training {len(train)} pages ({len(tr_tok)} tokens), held-out {len(test)} pages "
            f"({sum(len(l) for _, ls in test for l in ls)} tokens); training SlotSegmenter {len(seg.prefixes)} prefix / {len(seg.suffixes)} suffix candidates ===")
    t0 = time.time()
    F = fit([ls for _, ls in train], seg, emit_fn, t0)
    prm = F["params"]
    emit_fn(f"  fit ({F['n_evals']} grid evaluations, {time.time() - t0:.0f}s): p_copy {prm['p_copy']}, tau {prm['tau']}, a {prm['a']}, "
            f"q_pre {prm['q_pre']}, q_suf {prm['q_suf']}, q_core {prm['q_core']}, q_none {1 - prm['q_pre'] - prm['q_suf'] - prm['q_core']:.2f}; "
            f"loss {F['loss']:.2f} (R {F['parts'][0]:.2f}, shares {F['parts'][1]:.2f}, types {F['parts'][2]:.2f})")
    r, g = F["real"], F["gen"]
    emit_fn("  target R(d) real : " + " ".join(f"{x:.3f}" for x in r["R"]))
    emit_fn("  fitted R(d) gen0 : " + " ".join(f"{x:.3f}" for x in g["R"]))
    emit_fn("  edit shares real : " + ", ".join(f"{k} {v:.4f}" for k, v in zip(EDIT_KINDS, r["shares"])) + f"  (counts {r['counts'].astype(int).tolist()})")
    emit_fn("  edit shares gen0 : " + ", ".join(f"{k} {v:.4f}" for k, v in zip(EDIT_KINDS, g["shares"])))
    emit_fn(f"  types real {r['types']} at {r['tokens']} tokens; gen0 {g['types']} at {g['tokens']} tokens")
    lr, lg = np.array(r["lens"]), np.array(g["lens"])
    emit_fn(f"  line length real mean {lr.mean():.3f} sd {lr.std():.3f}; gen0 mean {lg.mean():.3f} sd {lg.std():.3f} (empirical sampling)")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"fit_{T}.json").write_text(json.dumps(dict(
        translit=T, params=prm, W=W, free_parameters=6, loss=F["loss"], loss_parts=F["parts"], n_evals=F["n_evals"],
        target=dict(R=r["R"].tolist(), shares=r["shares"].tolist(), types=r["types"], tokens=r["tokens"]),
        fitted=dict(R=g["R"].tolist(), shares=g["shares"].tolist(), types=g["types"], tokens=g["tokens"]),
        method="staged grid (A p_copy x tau x a at q=.25; B q simplex step .1; C local p/tau/a), seed 0, common random numbers",
    ), indent=1), encoding="utf-8", newline="\n")
    # ---- generate
    prod = Producer([ls for _, ls in train], seg)
    tr_counts = [len(ls) for _, ls in train]
    gens = {}
    for kind, pp in (("gen", prm), ("null", dict(prm, p_copy=0.0))):
        prod.set_params(pp)
        gens[kind] = []
        for s in (1, 2, 3):
            te_counts = random.Random(s).sample(tr_counts, len(test))
            pages = prod.text(s, tr_counts + te_counts)
            gtr = [(f"g{i}", pages[i]) for i in range(len(train))]
            gte = [(f"h{i}", pages[len(train) + i]) for i in range(len(test))]
            gens[kind].append((gtr, gte))
            side = dict(source=f"s57 {kind} producer fitted on {T} training pages, seed {s}", params=pp,
                        pages=[dict(id=p, section="S57", hand="S57", lang="?", quire="?", lines=ls,
                                    role="train" if i < len(train) else "heldout") for i, (p, ls) in enumerate(gtr + gte)])
            (out_dir / f"{kind}_{T}_s{s}.meta.json").write_text(json.dumps(side), encoding="utf-8", newline="\n")
    t1 = time.time()
    real_m = Measured(f"{T} {real_name}", train, test)
    gen_m = [Measured(f"{T} gen s{i + 1}", a, b) for i, (a, b) in enumerate(gens["gen"])]
    null_m = [Measured(f"{T} null s{i + 1}", a, b) for i, (a, b) in enumerate(gens["null"])]
    emit_fn(f"  measured 7 texts in {time.time() - t1:.0f}s")
    if time.time() - t_start > STEP_LIMIT * 2:
        raise TimeoutError("run exceeded 60 minutes")
    off = {"ZL3b": 0, "RF1b": 10, "IT2a": 20}.get(T, 30)
    t2 = time.time()
    real_dr = draws_for([real_m], SEED + off)
    gen_dr = draws_for(gen_m, SEED + off + 1)
    null_dr = draws_for(null_m, SEED + off + 2)
    emit_fn(f"  subsample draws {time.time() - t2:.0f}s")
    real_pt = real_m.point()
    gen_pt, gen_pts = mean_point(gen_m)
    null_pt, null_pts = mean_point(null_m)
    real_ci = {k: pct(real_dr[k]) for k in DRAW_KEYS}
    emit_fn(f"  real held-out: Moran {real_pt['P1']:.4f} [{real_ci['P1'][0]:.4f},{real_ci['P1'][1]:.4f}]; core->core {real_pt['P2']:+.4f} "
            f"[{real_ci['P2'][0]:+.4f},{real_ci['P2'][1]:+.4f}]; prefix gain {real_pt['P3']:+.4f} [{real_ci['P3'][0]:+.4f},{real_ci['P3'][1]:+.4f}]; "
            f"jsd_first_fg {real_pt['P4']:.4f} (excess {real_pt['P4_exc']:+.4f}); CHARWIN {real_pt['P5']:+.4f}")
    emit_fn("  real F1 by stream: " + ", ".join(f"{k[3:]} {real_pt[k]:+.4f} [{real_ci[k][0]:+.4f},{real_ci[k][1]:+.4f}]" for k in ("F1_prefix", "F1_core", "F1_suffix"))
            + f" -> s39 rule on the real text (this split): {f1_layer_call(real_ci)}")
    for lab, pts in (("gen", gen_pts), ("null", null_pts)):
        for i, p in enumerate(pts):
            emit_fn(f"    {lab} s{i + 1}: Moran {p['P1']:.4f} core->core {p['P2']:+.4f} prefix gain {p['P3']:+.4f} jsd_first_fg {p['P4']:.4f} "
                    f"CHARWIN {p['P5']:+.4f} F1 prefix/core/suffix {p['F1_prefix']:+.4f}/{p['F1_core']:+.4f}/{p['F1_suffix']:+.4f}")
    res = {}
    for lab, pt, dr in (("local-memory", gen_pt, gen_dr), ("null p_copy=0", null_pt, null_dr)):
        cells = score_cells(real_pt, real_dr, pt, dr)
        n = sum(1 for v in cells.values() if v[0])
        emit_fn(f"  -- {lab}: {n}/6 hold --")
        for k, (ok, txt) in cells.items():
            emit_fn(f"    {k} {'HOLDS' if ok else 'fails'}: {txt}")
        res[lab] = dict(n=n, holds={k: bool(v[0]) for k, v in cells.items()}, text={k: v[1] for k, v in cells.items()})
    res["fit"] = dict(params=prm, loss=F["loss"], parts=F["parts"])
    res["real_point"] = real_pt; res["gen_point"] = gen_pt; res["null_point"] = null_pt
    res["real_ci"] = real_ci
    return res


# ======================================================================= fixture
def fixture():
    out_lines = []

    def say(s=""):
        print(s, flush=True)
        out_lines.append(s)

    t0 = time.time()
    rng = random.Random(5)
    alph = "abcdefghij"
    pres = ["", "", "q", "o", "ch", "sh", "d"]
    sufs = ["", "", "y", "dy", "in", "ol", "r"]
    cores = sorted({"".join(rng.choice(alph) for _ in range(rng.randint(1, 4))) for _ in range(600)})
    lex = Counter()
    for _ in range(3000):
        w = rng.choice(pres) + rng.choice(cores) + rng.choice(sufs)
        lex[w] += int(1 + 200 / (1 + len(lex)))
    # truth producer built on a pseudo 'training' text drawn from the lexicon
    words = list(lex); wts = [lex[w] for w in words]
    base = [[[rng.choices(words, wts)[0] for _ in range(rng.randint(5, 10))] for _ in range(14)] for _ in range(60)]
    seg0 = SlotSegmenter([w for ls in base for l in ls for w in l])
    truth = dict(p_copy=0.2, tau=4.0, a=0.15, q_pre=0.3, q_suf=0.2, q_core=0.2)
    pr = Producer(base, seg0)
    pr.set_params(truth)
    pages = pr.text(99, [14] * 120)
    by = OrderedDict((f"f{i}", ls) for i, ls in enumerate(pages))
    say(f"fixture: synthetic text {len(by)} pages, {sum(len(l) for ls in pages for l in ls)} tokens, truth {truth}")
    global N_DRAW
    nd = N_DRAW
    N_DRAW = 40
    try:
        res = run_translit("FIX", by, say, t0, RUNS / "fixture", real_name="synthetic")
    finally:
        N_DRAW = nd
    fp = res["fit"]["params"]
    ok1 = abs(fp["p_copy"] - truth["p_copy"]) <= 0.08
    ok2 = res["local-memory"]["holds"]["P1"] and res["local-memory"]["holds"]["P2"]
    say(f"  fixture check: fitted p_copy {fp['p_copy']} vs truth {truth['p_copy']} -> {'OK' if ok1 else 'FAIL'}; "
        f"refit truth-class producer P1 & P2 hold on its own held-out pages -> {'OK' if ok2 else 'FAIL'}")
    ok = ok1 and ok2
    say(f"FIXTURE {'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f}s)")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "fixture.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8", newline="\n")
    return ok


# ======================================================================= main
def main():
    t0 = time.time()
    emit("s57 -- local-memory producer (candidate 1) fitted on 166 training pages, predicting 6 properties of the 41 held-out pages")
    emit(f"date: {clock()}")
    emit(f"sha256 s57_local_memory_model.py: {sha256(SELF)}")
    emit(f"sha256 s57_local_memory_model.prereg.sha256: {sha256(STUB) if STUB.exists() else 'missing'}")
    emit(f"stub_match: {stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"numpy {np.__version__}; python -I; CPU; W={W}; grid p_copy {GRID_P}, tau {GRID_TAU}, a {GRID_A}; q simplex step 0.1; "
         f"subsample {int(SUB_FRAC * 100)} % of held-out pages without replacement x {N_DRAW}; core->core null {N_SHUF_POINT} (point) / {N_SHUF_DRAW} (per draw)")
    emit("")
    allres = {}
    for T, f in TRANSLITS.items():
        path = ROOT / "data" / "translit" / f"{f}.meta.json"
        emit(f"translit {T}: {path.name} sha256={sha256(path)[:16]}")
        by = load_meta(path)
        allres[T] = run_translit(T, by, emit, t0, RUNS)
        emit(f"  elapsed so far {time.time() - t0:.0f}s")
        emit("")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")

    emit("=== VERDICT (pre-registered rule) ===")
    for lab in ("local-memory", "null p_copy=0"):
        row = []
        for T in TRANSLITS:
            h = allres[T][lab]["holds"]
            row.append(f"{T} {allres[T][lab]['n']}/6 [" + " ".join(f"{k}{'+' if v else '-'}" for k, v in h.items()) + "]")
        emit(f"  {lab:14}: " + "; ".join(row))
    z = allres["ZL3b"]["local-memory"]
    sets = {T: tuple(sorted(k for k, v in allres[T]["local-memory"]["holds"].items() if v)) for T in TRANSLITS}
    if z["n"] >= 5 and all(allres[T]["local-memory"]["n"] >= 5 for T in ("RF1b", "IT2a")) and len(set(sets.values())) == 1:
        verdict = "local-memory model predicts untouched pages"
    elif z["n"] >= 5:
        verdict = "holds on ZL3b only, not stable across transliterations"
    else:
        verdict = "local-memory model does NOT predict untouched pages"
    emit(f"VERDICT: {verdict} (ZL3b {z['n']}/6; holding sets {sets})")
    emit(f"null producer (p_copy=0) counts: " + ", ".join(f"{T} {allres[T]['null p_copy=0']['n']}/6" for T in TRANSLITS))
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "cells.json").write_text(json.dumps(allres, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)),
                                     encoding="utf-8", newline="\n")
    emit("")
    emit(f"elapsed: {time.time() - t0:.1f} s")
    emit(f"date end: {clock()}")
    emit(f"paths: {OUT}, {RUNS}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--fixture" in sys.argv:
        sys.exit(0 if fixture() else 1)
    main()
