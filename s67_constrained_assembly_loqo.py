"""s67 -- does a constrained-assembly producer with a length cadence (CA) predict held-out QUIRES (leave-one-quire-out)?

PRE-REGISTERED QUESTION (frozen in s67_constrained_assembly_loqo.prereg.sha256 BEFORE any fitting on real pages; before
the freeze this script ran only on its synthetic fixture, `--fixture`, which reads no real data):
"A producer that assembles words from parts -- a core (an exact repeat of a recent core of the page, or a frequency draw
from the training core lexicon), then a (prefix, suffix) pair drawn from a counted table that depends on the core's
affix class, the line position and the previous suffix -- and picks one of M = 6 such candidates by a length cadence
(the word length is pulled toward mu + rho (len_prev - mu)), fitted on all quires but one, is asked to predict s57's
P1-P5 and a type-count check (P7) on the held-out quire.  Does it hold >= 5 of these 6 on a majority of folds on ZL3b,
and on a majority of folds on RF1b and on IT2a as well?"

CONTEXT: s57 local memory 0/6; s58 independent affix wrapper 1-2/6 (CHARWIN positive, types +65 %); s61 joint whole
words 0-1/6 (CHARWIN negative).  No lexical context reached the within-line Moran (0.04-0.08 vs 0.156).  s59: cores are
not edit-chains; exact repeats are local.  D-056: no more producers on the 166/41 split; producers are judged on
leave-one-quire-out (LOQO).

MULTIPLICITY (D-056): this is the 4th producer evaluated in phase 4 (s57, s58, s61, s67) and the first on LOQO.

PRODUCER CA (fixed before hashing)
  Segmenter: scoreboard/metrics_new.SlotSegmenter fitted on the training-quire tokens; word -> (pre, core, suf).
  Core classes: the TOP = 300 most frequent training cores get a smoothed affix profile = [prefix distribution |
    suffix distribution] of that core, each smoothed toward the global training distribution with ALPHA = 5 pseudo-
    counts; k-means (K = 12, k-means++ init, 10 restarts, numpy rng SEED, 100 iterations, unweighted) on these profiles.
    Rarer cores seen >= 2 times: nearest centroid by their smoothed profile (Euclidean).  Cores seen once: back-off
    class 12 (a 13th class).  Counts come from the training quires only.
  Line-position class (s61): P = first token of the page's first line (paragraph proxy: the meta.json transliterations
    keep no paragraph markers, so the first line of each page stands in for paragraph-initial), I = first token of any
    other line, F = last token of a line of length >= 2, M = otherwise.
  Affix table (counted, 0 free parameters): P((P, S) | class, pos, prev_suf), Witten-Bell back-off by sampling (stay at a
    context with probability N / (N + T), N = tokens, T = distinct (P, S) there, else back off) -> (class, pos) ->
    (class) -> unigram of training (P, S) pairs.  prev_suf = previous word's suffix in the line ("^" at line start).
  Candidate word: core = with probability p_rep (if the page has history) the core d tokens back in the page stream
    (crossing line ends), d in 1..min(W, history), W = 20, P(d) ~ exp(-(d-1)/tau); else a training core drawn by token
    frequency (no glyph edits).  Then (P, S) from the affix table at (class(core), pos, prev_suf).  word = P + core + S.
  Cadence: M = 6 candidates are generated independently at the current context; one is chosen with weight
    exp(-gamma |len - (mu + rho (len_prev - mu))|), len in glyphs (characters of the transliteration string), mu = the
    training mean word length, len_prev = the previous word of the line.  Line-initial words use gamma = 0 (one
    candidate).  When gamma = 0 one candidate is drawn (identical in distribution to choosing uniformly among 6).
  Lines and pages: line lengths drawn from the empirical training-quire line lengths; page line counts given.
  Free parameters: p_rep, tau, gamma, rho (4).  K = 12, M = 6, W = 20 fixed.
  CA0 = CA with gamma = 0 (no cadence; p_rep and tau refit -- it is CA's stage A below).
  CA-ind = CA with affixes drawn WITHOUT the core class: P((P, S) | pos, prev_suf) -> (pos) -> unigram; all four
    parameters refit by the same staged grid.

FITTING (training quires only).  Loss = s57's R(d) part (d = 1..20, cores, s57.fit_stats) + s57's type-count part
  + a within-line Moran part + a word-length-sd part: mean_d ((R_g - R_r)/0.01)^2 + ((V_g - V_r)/V_r/0.01)^2
  + ((I_g - I_r)/0.01)^2 + ((sd_g - sd_r)/sd_r/0.01)^2, where I = within-line Moran I of word length (s57
  Measured.moran formula, all training pages) and sd = the standard deviation of word length (glyphs) over all
  training tokens.  s57's edit-share part is dropped (CA makes no edits).  BECAUSE MORAN IS A FIT TARGET, P1 IS PARTLY
  BUILT IN BY THE FIT.  DEVIATION from the brief (made before the freeze, on the fixture only): the word-length-sd term
  was added because on the fixture Moran alone does not identify gamma apart from rho (a planted gamma 1.0 / rho 0.6
  was fitted as gamma 4.0 / rho 0.4 with the same Moran); a strong cadence narrows the length distribution, so the sd
  term separates them and stops the fit buying Moran by distorting word lengths.
  Common random numbers: every candidate generated with seed 0 as the training quires' pages (their line counts).
  Staged grid:  A: gamma = 0 (rho moot), p_rep x tau  (-> CA0);
                B: at A's best, gamma (> 0) x rho;
                C: at B's best (gamma, rho), p_rep x tau within +-1 grid step of A's best;
                D: at C's best (p_rep, tau), gamma x rho within +-1 grid step of B's best.
  CA-ind: the same four stages on its own.

EVALUATION: leave-one-quire-out.  Folds = the quires with >= 4 pages in ZL3b (project quire field of the meta.json);
  the same quire letters are the folds on RF1b and IT2a (each transliteration's own pages of that quire).  For each
  fold: fit on all other quires; generate (seeds 1, 2) the training quires' pages (their line counts) + pages matched
  to the held-out quire's page count and line counts; score with s57's code imported verbatim (S57.Measured,
  S57.draws_for with N_DRAW = 300, S57.score_cells): every statistic computed on a generated text exactly as on the
  real one (segmenter and models from its training-like pages, measured on its held-out-like pages).  Intervals: 80 %
  page subsampling of the held-out quire without replacement, 300 draws.
    P1 Moran Delta interval includes 0 or lies above; P2 core->core Delta interval includes 0; P3 generated prefix
    gain inside the real 80 %-subsample interval; P4 jsd_first_fg inside s15's width [0.1447, 0.2156] (s15's width is
    for 41 pages; a single quire is noisier -- caveat); P5 CHARWIN > 0.  (s57's P6 is dropped.)
    Folds with < 6 held-out pages: P1-P3 by point comparison against s57's tolerances (half-widths of the real
    41-page ZL3b intervals in results_s57.txt: Moran 0.0158, core->core 0.0203, prefix gain 0.0170): P1 point Delta
    >= -0.0158; P2 |point Delta| <= 0.0203; P3 |gen - real| <= 0.0170; such folds are flagged.
    P7 type count: generated held-out-like types vs real held-out types at matched tokens (both truncated to the
    smaller token count, page order), ratio averaged over seeds, holds iff within +-15 %.
VERDICT RULE: "constrained assembly with length cadence predicts held-out quires" iff CA holds >= 5 of the 6 (P1-P5,
  P7) on a strict majority of folds on ZL3b AND on a strict majority of folds on RF1b AND on IT2a; else "does NOT
  predict held-out quires".  Also reported: per fold counts for CA, CA0, CA-ind, and per prediction the folds where CA
  holds and CA0 / CA-ind fail (and the reverse).
BUDGET: 60 minutes; folds run in parallel worker processes.  If the run would exceed it the grids were to be cut
  before the freeze (stated in the result header: the grids below are the frozen ones).

Run:    python -I s67_constrained_assembly_loqo.py [--fixture] [--list-imports]
Writes: results_s67.txt, runs/s67/ (fit_<T>_<Q>.json, gen sidecars <model>_<T>_<Q>_s<seed>.meta.json holding the
        held-out-like pages, cells.json; fixture.txt for --fixture).  Nothing else.
"""
from __future__ import annotations

import bisect
import hashlib
import json
import math
import os
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

import s57_local_memory_model as S57  # noqa: E402  (scoring code, verbatim)
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s67_constrained_assembly_loqo.py"
STUB = ROOT / "s67_constrained_assembly_loqo.prereg.sha256"
OUT = ROOT / "results_s67.txt"
RUNS = ROOT / "runs" / "s67"
SEED = 20261017
W = 20
K = 12
M_CAND = 6
TOP = 300
ALPHA = 5.0
N_DRAW = 300
S57.N_DRAW = N_DRAW
SEEDS = (1, 2)
MIN_FOLD_PAGES = 4
SMALL_FOLD = 6
TOL_SMALL = dict(P1=0.0158, P2=0.0203, P3=0.0170)
TYPE_TOL = 0.15
RUN_LIMIT = 60 * 60
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
GRID_PREP = [0.0, 0.03, 0.06, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]
GRID_TAU = [1.0, 2.0, 4.0, 7.0, 12.0, 20.0]
GRID_G = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
GRID_RHO = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
PREDS = ["P1", "P2", "P3", "P4", "P5", "P7"]
MODELS = ["CA", "CA0", "CA-ind"]
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
        if not ln or ln.startswith("#") or len(ln.split(None, 1)) < 2 or len(ln.split(None, 1)[0]) != 64:
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


def load_pages(path: Path):
    """-> list of (page id, quire, lines) in file order (s57.load_meta filtering)."""
    d = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for p in d["pages"]:
        lines = [[w for w in l if w] for l in p["lines"]]
        lines = [l for l in lines if l]
        if lines:
            out.append((str(p["id"]), str(p.get("quire")), lines))
    return out


def _cum(counter):
    items = sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0])))
    ws = [k for k, _ in items]
    cum, t = [], 0
    for _, c in items:
        t += c; cum.append(t)
    return ws, cum


def pos_class(li, i, L):
    if i == 0:
        return "P" if li == 0 else "I"
    return "F" if i == L - 1 else "M"


def moran_pages(pages):
    """within-line Moran I of word length over all pages (S57.Measured.moran formula)."""
    x, lid, off = [], [], 0
    for lines in pages:
        for l in lines:
            for w in l:
                x.append(len(w)); lid.append(off)
            off += 1
    x = np.array(x, float); lid = np.array(lid)
    left = np.nonzero(lid[1:] == lid[:-1])[0]
    z = x - x.mean()
    d = float(np.dot(z, z))
    return float(len(x) / len(left) * np.dot(z[left], z[left + 1]) / d) if d > 0 and len(left) else float("nan")


# ======================================================================= core classes
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


def core_classes(train_pages, seg):
    pre_c, suf_c, gp, gs, cc = defaultdict(Counter), defaultdict(Counter), Counter(), Counter(), Counter()
    for lines in train_pages:
        for l in lines:
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
    inertia, C, lab = kmeans(X, K, np.random.default_rng(SEED))
    cls = {c: int(l) for c, l in zip(top, lab)}
    n_near = n_back = 0
    for c in ranked[TOP:]:
        if cc[c] >= 2:
            cls[c] = int(((C - prof(c)) ** 2).sum(1).argmin()); n_near += 1
        else:
            cls[c] = K; n_back += 1
    sizes = Counter(lab.tolist())
    return cls, dict(top=len(top), nearest=n_near, backoff=n_back, inertia=round(inertia, 4),
                     top_class_sizes=[sizes.get(j, 0) for j in range(K)])


# ======================================================================= producer
class CAProducer:
    def __init__(self, train_pages, seg, use_class=True):
        self.seg = seg
        self.use_class = use_class
        self.cls, self.cls_info = core_classes(train_pages, seg) if use_class else ({}, {})
        corec = Counter()
        tabs = [defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)]
        uni = Counter()
        lens_w = []
        for lines in train_pages:
            for li, l in enumerate(lines):
                L = len(l)
                psuf = "^"
                for i, w in enumerate(l):
                    pos = pos_class(li, i, L)
                    p, c, s = seg.segment(w)
                    corec[c] += 1
                    lens_w.append(len(w))
                    ps = (p, s)
                    uni[ps] += 1
                    if use_class:
                        k = self.cls[c]
                        tabs[0][(k, pos, psuf)][ps] += 1; tabs[1][(k, pos)][ps] += 1; tabs[2][k][ps] += 1
                    else:
                        tabs[0][(pos, psuf)][ps] += 1; tabs[1][pos][ps] += 1
                    psuf = s
        if not use_class:
            tabs = tabs[:2]
        self.levels = [{k: (*_cum(v), sum(v.values()) / (sum(v.values()) + len(v))) for k, v in t.items()} for t in tabs]
        self.uni = _cum(uni)
        self.core_w, self.core_c = _cum(corec)
        self.core_tot = self.core_c[-1]
        self.mu = float(np.mean(lens_w))
        self.lens = [len(l) for lines in train_pages for l in lines]
        self.sizes = [len(t) for t in tabs]
        self.set_params(dict(p_rep=0.0, tau=1.0, gamma=0.0, rho=0.0))

    def set_params(self, prm):
        self.prm = dict(prm)
        self.kcum, t = [], 0.0
        for d in range(1, W + 1):
            t += math.exp(-(d - 1) / prm["tau"]); self.kcum.append(t)

    @staticmethod
    def _pick(rng, ws, cum):
        return ws[bisect.bisect_right(cum, rng.random() * cum[-1])]

    def affix(self, rng, core, pos, psuf):
        if self.use_class:
            k = self.cls[core]
            keys = ((k, pos, psuf), (k, pos), k)
        else:
            keys = ((pos, psuf), pos)
        for lev, key in zip(self.levels, keys):
            e = lev.get(key)
            if e is None:
                continue
            ws, cum, lam = e
            if rng.random() < lam:
                return self._pick(rng, ws, cum)
        return self._pick(rng, *self.uni)

    def page(self, rng, n_lines):
        p = self.prm
        p_rep, gamma, rho, mu = p["p_rep"], p["gamma"], p["rho"], self.mu
        hist, lines = [], []
        for li in range(n_lines):
            L = rng.choice(self.lens)
            line, psuf, plen = [], "^", 0
            for i in range(L):
                pos = pos_class(li, i, L)
                n_c = M_CAND if (i > 0 and gamma > 0) else 1
                cands = []
                for _ in range(n_c):
                    if hist and p_rep > 0 and rng.random() < p_rep:
                        h = min(W, len(hist))
                        d = bisect.bisect_right(self.kcum, rng.random() * self.kcum[h - 1]) + 1
                        core = hist[-min(d, h)]
                    else:
                        core = self.core_w[bisect.bisect_right(self.core_c, rng.random() * self.core_tot)]
                    pr, su = self.affix(rng, core, pos, psuf)
                    cands.append((pr + core + su, core, su))
                if n_c > 1:
                    tgt = mu + rho * (plen - mu)
                    wts = [math.exp(-gamma * abs(len(c[0]) - tgt)) for c in cands]
                    tot = sum(wts); u = rng.random() * tot; acc = 0.0
                    j = n_c - 1
                    for jj, x in enumerate(wts):
                        acc += x
                        if u < acc:
                            j = jj; break
                    w, core, su = cands[j]
                else:
                    w, core, su = cands[0]
                line.append(w); hist.append(core); psuf = su; plen = len(w)
            lines.append(line)
        return lines

    def text(self, seed, page_line_counts):
        rng = random.Random(seed)
        return [self.page(rng, n) for n in page_line_counts]


KEYS = ("p_rep", "tau", "gamma", "rho")


def len_sd(pages):
    return float(np.std([len(w) for lines in pages for l in lines for w in l]))


def ca_loss(g, real, gm, rm, gs, rs):
    lr = float(np.mean(((g["R"] - real["R"]) / 0.01) ** 2))
    lv = float(((g["types"] - real["types"]) / real["types"] / 0.01) ** 2)
    lm = float(((gm - rm) / 0.01) ** 2)
    ls = float(((gs - rs) / rs / 0.01) ** 2)
    return lr + lv + lm + ls, (lr, lv, lm, ls)


def fit(train_pages, seg, use_class=True, grids=None):
    gp, gt, gg, gr = grids or (GRID_PREP, GRID_TAU, GRID_G, GRID_RHO)
    enc = S57.Encoder(seg)
    real = S57.fit_stats(train_pages, enc)
    rm = moran_pages(train_pages)
    rs = len_sd(train_pages)
    prod = CAProducer(train_pages, seg, use_class)
    counts = [len(l) for l in train_pages]
    cache = {}
    t0 = time.time()

    def ev(prm):
        if prm["gamma"] == 0:
            prm = dict(prm, rho=0.0)
        key = tuple(round(prm[k], 6) for k in KEYS)
        if key not in cache:
            prod.set_params(prm)
            pages = prod.text(0, counts)
            g = S57.fit_stats(pages, enc)
            gm = moran_pages(pages)
            gs = len_sd(pages)
            L, parts = ca_loss(g, real, gm, rm, gs, rs)
            cache[key] = (L, parts, dict(R=g["R"].tolist(), types=g["types"], tokens=g["tokens"], moran=gm, len_sd=gs), dict(prm))
        return cache[key]

    def better(best, prm):
        r = ev(prm)
        return r if best is None or r[0] < best[0] else best

    best = None
    for a in gp:
        for t in gt:
            best = better(best, dict(p_rep=a, tau=t, gamma=0.0, rho=0.0))
    bA = best
    n_a = len(cache)
    bestB = None
    for g in gg:
        if g == 0:
            continue
        for r in gr:
            bestB = better(bestB, dict(bA[3], gamma=g, rho=r))
    best = bestB if bestB[0] < best[0] else best
    ia, it = gp.index(bA[3]["p_rep"]), gt.index(bA[3]["tau"])
    for a in gp[max(0, ia - 1): ia + 2]:
        for t in gt[max(0, it - 1): it + 2]:
            best = better(best, dict(best[3], p_rep=a, tau=t))
    ig, ir = gg.index(bestB[3]["gamma"]), gr.index(bestB[3]["rho"])
    for g in gg[max(0, ig - 1): ig + 2]:
        for r in gr[max(0, ir - 1): ir + 2]:
            best = better(best, dict(best[3], gamma=g, rho=r))
    return dict(params=best[3], loss=best[0], parts=best[1], gen=best[2],
                p0=bA[3], loss0=bA[0], parts0=bA[1], gen0=bA[2],
                real=dict(R=real["R"].tolist(), types=real["types"], tokens=real["tokens"], moran=rm, len_sd=rs),
                n_evals=len(cache), n_stageA=n_a, secs=time.time() - t0, mu=prod.mu, cls=prod.cls_info, tables=prod.sizes)


# ======================================================================= scoring of one fold
def types_at(pages_a, pages_b):
    ta = [w for ls in pages_a for l in ls for w in l]
    tb = [w for ls in pages_b for l in ls for w in l]
    n = min(len(ta), len(tb))
    return len(set(ta[:n])), len(set(tb[:n])), n


def score_model(real_m, real_pt, real_dr, ms, gen_dr, n_test, gen_test_pages, real_test_pages):
    gen_pt, _ = S57.mean_point(ms)
    cells = S57.score_cells(real_pt, real_dr, gen_pt, gen_dr)
    out = {k: cells[k] for k in ("P1", "P2", "P3", "P4", "P5")}
    small = n_test < SMALL_FOLD
    if small:
        d1 = gen_pt["P1"] - real_pt["P1"]
        out["P1"] = (d1 >= -TOL_SMALL["P1"], f"[small fold, point] Moran Δ {d1:+.4f} >= -{TOL_SMALL['P1']}")
        d2 = gen_pt["P2"] - real_pt["P2"]
        out["P2"] = (abs(d2) <= TOL_SMALL["P2"], f"[small fold, point] core->core Δ {d2:+.4f}, |Δ| <= {TOL_SMALL['P2']}")
        d3 = gen_pt["P3"] - real_pt["P3"]
        out["P3"] = (abs(d3) <= TOL_SMALL["P3"], f"[small fold, point] prefix gain gen {gen_pt['P3']:+.4f} real {real_pt['P3']:+.4f}, |d| <= {TOL_SMALL['P3']}")
    ratios = []
    for gp in gen_test_pages:
        vg, vr, n = types_at(gp, real_test_pages)
        ratios.append(vg / vr if vr else float("nan"))
    rt = float(np.mean(ratios))
    out["P7"] = (abs(rt - 1) <= TYPE_TOL, f"types gen/real at matched tokens {rt:.3f} (seeds {', '.join(f'{x:.3f}' for x in ratios)}); tol ±{TYPE_TOL:.0%}")
    return out, gen_pt, rt, small


def run_fold(job):
    """job: dict(T, Q, pages=[(id, quire, lines)], fixture=bool, grids, n_draw, out_dir) -> dict with text lines."""
    t0 = time.time()
    S57.N_DRAW = job.get("n_draw", N_DRAW)
    T, Q = job["T"], job["Q"]
    pages = job["pages"]
    train = [(p, ls) for p, q, ls in pages if q != Q]
    test = [(p, ls) for p, q, ls in pages if q == Q]
    tr_pages = [ls for _, ls in train]
    tr_tok = [w for ls in tr_pages for l in ls for w in l]
    seg = SlotSegmenter(tr_tok)
    lines = []
    say = lines.append
    say(f"--- {T} fold {Q}: held-out {len(test)} pages ({sum(len(l) for _, ls in test for l in ls)} tokens), training "
        f"{len(train)} pages ({len(tr_tok)} tokens){'  [SMALL FOLD < 6 pages: P1-P3 point comparisons]' if len(test) < SMALL_FOLD else ''}")
    fits = {}
    for lab, uc in (("CA", True), ("CA-ind", False)):
        fits[lab] = fit(tr_pages, seg, use_class=uc, grids=job.get("grids"))
    F = fits["CA"]
    params = {"CA": F["params"], "CA0": F["p0"], "CA-ind": fits["CA-ind"]["params"]}
    fitinfo = {"CA": (F["loss"], F["parts"], F["gen"]), "CA0": (F["loss0"], F["parts0"], F["gen0"]),
               "CA-ind": (fits["CA-ind"]["loss"], fits["CA-ind"]["parts"], fits["CA-ind"]["gen"])}
    say(f"  classes: {F['cls']}; mu {F['mu']:.3f}; affix contexts CA {F['tables']} / CA-ind {fits['CA-ind']['tables']}")
    say(f"  training targets: Moran {F['real']['moran']:.4f}, word-length sd {F['real']['len_sd']:.4f}, types {F['real']['types']} at {F['real']['tokens']} tokens")
    for m in MODELS:
        L, parts, g = fitinfo[m]
        say(f"  fit {m:6}: " + ", ".join(f"{k} {params[m][k]}" for k in KEYS) + f"; loss {L:.2f} (R {parts[0]:.2f}, types {parts[1]:.2f}, "
            f"Moran {parts[2]:.2f}, len-sd {parts[3]:.2f}); in-sample Moran {g['moran']:.4f}, len sd {g['len_sd']:.4f}, types {g['types']} at {g['tokens']}")
    say(f"  fits: CA {F['n_evals']} evals {F['secs']:.0f}s; CA-ind {fits['CA-ind']['n_evals']} evals {fits['CA-ind']['secs']:.0f}s")
    tr_counts = [len(ls) for ls in tr_pages]
    te_counts = [len(ls) for _, ls in test]
    gens = {}
    out_dir = Path(job["out_dir"]); out_dir.mkdir(parents=True, exist_ok=True)
    prods = {"CA": CAProducer(tr_pages, seg, True), "CA-ind": CAProducer(tr_pages, seg, False)}
    for m in MODELS:
        prod = prods["CA-ind" if m == "CA-ind" else "CA"]
        prod.set_params(params[m])
        gens[m] = []
        for s in SEEDS:
            pg = prod.text(s, tr_counts + te_counts)
            gtr = [(f"g{i}", pg[i]) for i in range(len(train))]
            gte = [(f"h{i}", pg[len(train) + i]) for i in range(len(test))]
            gens[m].append((gtr, gte))
            side = dict(source=f"s67 {m} fitted on {T} quires other than {Q}, seed {s}; held-out-like pages only", params=params[m],
                        pages=[dict(id=p, section="S67", hand="S67", lang="?", quire=Q, lines=ls, role="heldout") for p, ls in gte])
            (out_dir / f"{m}_{T}_{Q}_s{s}.meta.json").write_text(json.dumps(side), encoding="utf-8", newline="\n")
    real_m = S57.Measured(f"{T} {Q} real", train, test)
    ms = {m: [S57.Measured(f"{T} {Q} {m} s{i}", a, b) for i, (a, b) in enumerate(gens[m])] for m in MODELS}
    off = job["off"]
    real_dr = S57.draws_for([real_m], SEED + off)
    real_pt = real_m.point()
    real_ci = {k: S57.pct(real_dr[k]) for k in ("P1", "P2", "P3")}
    say(f"  real held-out: Moran {real_pt['P1']:.4f} [{real_ci['P1'][0]:.4f},{real_ci['P1'][1]:.4f}]; core->core {real_pt['P2']:+.4f} "
        f"[{real_ci['P2'][0]:+.4f},{real_ci['P2'][1]:+.4f}]; prefix gain {real_pt['P3']:+.4f} [{real_ci['P3'][0]:+.4f},{real_ci['P3'][1]:+.4f}]; "
        f"jsd_first_fg {real_pt['P4']:.4f}; CHARWIN {real_pt['P5']:+.4f}")
    res = dict(T=T, Q=Q, n_test=len(test), n_train=len(train), params=params,
               fit={m: dict(loss=fitinfo[m][0], parts=fitinfo[m][1], gen=fitinfo[m][2]) for m in MODELS},
               real_point=real_pt, real_ci=real_ci, models={})
    real_test_pages = [ls for _, ls in test]
    for j, m in enumerate(MODELS):
        gen_dr = S57.draws_for(ms[m], SEED + off + 1 + j)
        cells, gen_pt, rt, small = score_model(real_m, real_pt, real_dr, ms[m], gen_dr, len(test),
                                               [[ls for _, ls in b] for _, b in gens[m]], real_test_pages)
        n = sum(1 for k in PREDS if cells[k][0])
        say(f"  -- {m}: {n}/6 hold [" + " ".join(f"{k}{'+' if cells[k][0] else '-'}" for k in PREDS) + "] --")
        for k in PREDS:
            say(f"    {k} {'HOLDS' if cells[k][0] else 'fails'}: {cells[k][1]}")
        res["models"][m] = dict(n=n, holds={k: bool(cells[k][0]) for k in PREDS}, text={k: cells[k][1] for k in PREDS},
                                gen_point=gen_pt, type_ratio=rt, small=small)
    say(f"  fold time {time.time() - t0:.0f}s")
    res["lines"] = lines
    res["secs"] = time.time() - t0
    (out_dir / f"fit_{T}_{Q}.json").write_text(json.dumps(dict(
        translit=T, fold=Q, params=params, fit=res["fit"], free_parameters=4, K=K, M=M_CAND, W=W,
        classes=F["cls"], mu=F["mu"], target=F["real"], n_evals={"CA": F["n_evals"], "CA-ind": fits["CA-ind"]["n_evals"]},
        method="staged grid A p_rep x tau (gamma 0 = CA0), B gamma x rho, C local p_rep x tau, D local gamma x rho; seed 0 CRN",
    ), indent=1, default=float), encoding="utf-8", newline="\n")
    return res


def folds_of(pages_zl):
    c = Counter(q for _, q, _ in pages_zl)
    return [q for q in sorted(c) if c[q] >= MIN_FOLD_PAGES]


def summarize(allres, folds_by_T, emit_fn, label="VERDICT"):
    emit_fn("=== PER-FOLD TABLE (count of P1 P2 P3 P4 P5 P7 holding; + / - per prediction) ===")
    for T, folds in folds_by_T.items():
        emit_fn(f"  {T}:")
        emit_fn(f"    {'fold':5} {'pages':>5}  " + "  ".join(f"{m:22}" for m in MODELS))
        for Q in folds:
            r = allres[(T, Q)]
            cellstr = []
            for m in MODELS:
                h = r["models"][m]["holds"]
                cellstr.append(f"{r['models'][m]['n']}/6 " + "".join("+" if h[k] else "-" for k in PREDS) + f" t{r['models'][m]['type_ratio']:.2f}".ljust(8))
            emit_fn(f"    {Q:5} {r['n_test']:>5}{'*' if r['n_test'] < SMALL_FOLD else ' '} " + "  ".join(f"{c:22}" for c in cellstr))
    emit_fn("  (+/- order: P1 P2 P3 P4 P5 P7; tX.XX = generated/real types at matched tokens; * = small fold)")
    emit_fn("")
    emit_fn("=== FITTED PARAMETERS (range over folds) ===")
    for T, folds in folds_by_T.items():
        for m in MODELS:
            ps = [allres[(T, Q)]["params"][m] for Q in folds]
            emit_fn(f"  {T} {m:6}: " + "; ".join(f"{k} {min(p[k] for p in ps)}-{max(p[k] for p in ps)} (median {float(np.median([p[k] for p in ps])):g})" for k in KEYS))
    emit_fn("")
    emit_fn("=== PER-PREDICTION FOLD COUNTS ===")
    summ = {}
    for T, folds in folds_by_T.items():
        nf = len(folds)
        for m in MODELS:
            cnt = {k: sum(allres[(T, Q)]["models"][m]["holds"][k] for Q in folds) for k in PREDS}
            n5 = sum(allres[(T, Q)]["models"][m]["n"] >= 5 for Q in folds)
            summ[(T, m)] = n5
            emit_fn(f"  {T} {m:6}: folds with >= 5/6: {n5}/{nf}; per prediction " + ", ".join(f"{k} {cnt[k]}/{nf}" for k in PREDS))
        for other in ("CA0", "CA-ind"):
            gain = {k: sum(allres[(T, Q)]["models"]["CA"]["holds"][k] and not allres[(T, Q)]["models"][other]["holds"][k] for Q in folds) for k in PREDS}
            loss = {k: sum(allres[(T, Q)]["models"][other]["holds"][k] and not allres[(T, Q)]["models"]["CA"]["holds"][k] for Q in folds) for k in PREDS}
            emit_fn(f"    CA holds & {other} fails (folds): " + ", ".join(f"{k} {gain[k]}" for k in PREDS)
                    + f";  {other} holds & CA fails: " + ", ".join(f"{k} {loss[k]}" for k in PREDS))
    emit_fn("")
    emit_fn(f"=== {label} (pre-registered rule) ===")
    Ts = list(folds_by_T)
    maj = {T: summ[(T, "CA")] * 2 > len(folds_by_T[T]) for T in Ts}
    for m in MODELS:
        emit_fn(f"  {m:6}: " + "; ".join(f"{T} {summ[(T, m)]}/{len(folds_by_T[T])} folds >= 5/6" for T in Ts))
    ok = all(maj.values())
    verdict = ("constrained assembly with length cadence predicts held-out quires" if ok
               else "constrained assembly with length cadence does NOT predict held-out quires")
    emit_fn(f"VERDICT: {verdict} (" + ", ".join(f"{T} majority {'yes' if maj[T] else 'no'}" for T in Ts) + ")")
    return verdict, summ


# ======================================================================= fixture
def fixture():
    out_lines = []

    def say(s=""):
        print(s, flush=True)
        out_lines.append(s)

    t0 = time.time()
    say(f"s67 fixture (synthetic, no real data) -- date: {clock()}")
    rng = random.Random(5)
    alph = "acdehiklnorsty"
    pres = ["", "", "q", "o", "ch", "sh", "d", "y"]
    sufs = ["", "", "y", "dy", "in", "ol", "r", "aiin"]
    cores = sorted({"".join(rng.choice(alph) for _ in range(rng.randint(1, 5))) for _ in range(500)})
    # each core has a preferred affix family -> class structure the clustering should find
    fam = {c: rng.randrange(6) for c in cores}
    fam_pre = [rng.sample(pres, 3) for _ in range(6)]
    fam_suf = [rng.sample(sufs, 3) for _ in range(6)]
    cw = [1.0 / (1 + i) ** 0.9 for i in range(len(cores))]
    base = []
    for _pg in range(160):
        page = []
        for _li in range(12):
            l = []
            for _ in range(rng.randint(4, 11)):
                c = rng.choices(cores, cw)[0]
                f = fam[c]
                l.append(rng.choice(fam_pre[f]) + c + rng.choice(fam_suf[f]))
            page.append(l)
        base.append(page)
    seg0 = SlotSegmenter([w for ls in base for l in ls for w in l])
    truth = dict(p_rep=0.2, tau=3.0, gamma=1.0, rho=0.6)
    pr = CAProducer(base, seg0, True)
    pr.set_params(truth)
    gpages = pr.text(99, [12] * 192)
    quires = [chr(ord("A") + i // 12) for i in range(192)]
    pages = [(f"f{i}", quires[i], ls) for i, ls in enumerate(gpages)]
    say(f"fixture: synthetic text {len(pages)} pages in 16 quires of 12, {sum(len(l) for ls in gpages for l in ls)} tokens; truth {truth}")
    say(f"  synthetic text within-line Moran {moran_pages(gpages):.4f}; base (no cadence) Moran {moran_pages(base):.4f}")
    # (1) parameter recovery on the fold-A training quires
    tr = [ls for _, q, ls in pages if q != "A"]
    seg = SlotSegmenter([w for ls in tr for l in ls for w in l])
    F = fit(tr, seg, True)
    fp = F["params"]
    say(f"  recovery fit (training = quires B-P): {F['n_evals']} evals, {F['secs']:.0f}s; fitted " + ", ".join(f"{k} {fp[k]}" for k in KEYS)
        + f"; loss {F['loss']:.2f} (R {F['parts'][0]:.2f}, types {F['parts'][1]:.2f}, Moran {F['parts'][2]:.2f}, len-sd {F['parts'][3]:.2f}); CA0 p_rep {F['p0']['p_rep']} tau {F['p0']['tau']} loss {F['loss0']:.2f}")
    say(f"  classes {F['cls']}")
    say(f"  check rho (reported, not gated): fitted {fp['rho']} vs truth {truth['rho']}; tau fitted {fp['tau']} vs truth {truth['tau']}")
    ok_p = abs(fp["p_rep"] - truth["p_rep"]) <= 0.05 + 1e-9
    ok_g = fp["gamma"] > 0 and abs(GRID_G.index(fp["gamma"]) - GRID_G.index(truth["gamma"])) <= 1
    say(f"  check p_rep {fp['p_rep']} vs truth {truth['p_rep']} (within 0.05) -> {'OK' if ok_p else 'FAIL'}")
    say(f"  check gamma {fp['gamma']} vs truth {truth['gamma']} (> 0 and within one grid step of {GRID_G}) -> {'OK' if ok_g else 'FAIL'}")
    # (2) one full LOQO fold through the scoring pipeline (40 draws)
    r = run_fold(dict(T="FIX", Q="A", pages=pages, out_dir=str(RUNS / "fixture"), off=900, n_draw=40))
    for ln in r["lines"]:
        say(ln)
    ok_pipe = all(m in r["models"] for m in MODELS)
    say(f"  pipeline check (fold A scored for CA, CA0, CA-ind) -> {'OK' if ok_pipe else 'FAIL'}; CA on its own truth-class text: {r['models']['CA']['n']}/6")
    ok = ok_p and ok_g and ok_pipe
    say(f"FIXTURE {'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f}s)")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "fixture.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8", newline="\n")
    return ok


# ======================================================================= main
def main():
    from multiprocessing import Pool
    t0 = time.time()
    emit("s67 -- constrained assembly with length cadence (CA), leave-one-quire-out; s57's P1-P5 + type check P7")
    emit(f"date: {clock()}")
    emit(f"sha256 s67_constrained_assembly_loqo.py: {sha256(SELF)}")
    emit(f"sha256 s67_constrained_assembly_loqo.prereg.sha256: {sha256(STUB) if STUB.exists() else 'missing'}")
    emit(f"stub_match: {stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"numpy {np.__version__}; python -I; CPU; K={K}, M={M_CAND}, W={W}, TOP={TOP}, ALPHA={ALPHA}; grids p_rep {GRID_PREP}, tau {GRID_TAU}, "
         f"gamma {GRID_G}, rho {GRID_RHO}; seeds {SEEDS}; subsample 80 % of held-out-quire pages x {N_DRAW}")
    emit("MULTIPLICITY (D-056): this is the 4th producer evaluated in phase 4 (s57, s58, s61, s67) and the first on leave-one-quire-out.")
    emit("NOTE: within-line Moran I is a fit target, so P1 is partly built in by the fit.")
    emit("NOTE: P4 uses s15's 41-page width on single quires (noisier); P1-P5 scored by s57's code imported verbatim (S57.Measured, draws_for, score_cells).")
    emit("")
    data = {}
    for T, f in TRANSLITS.items():
        path = ROOT / "data" / "translit" / f"{f}.meta.json"
        emit(f"translit {T}: {path.name} sha256={sha256(path)[:16]}")
        data[T] = load_pages(path)
    folds = folds_of(data["ZL3b"])
    emit(f"folds (quires with >= {MIN_FOLD_PAGES} pages in ZL3b): {folds} ({len(folds)})")
    for T in TRANSLITS:
        c = Counter(q for _, q, _ in data[T])
        emit(f"  {T}: pages per fold " + ", ".join(f"{q} {c.get(q, 0)}" for q in folds) + f"; other quires " + ", ".join(f"{q} {n}" for q, n in sorted(c.items()) if q not in folds))
    emit("")
    jobs = []
    for ti, T in enumerate(TRANSLITS):
        for fi, Q in enumerate(folds):
            jobs.append(dict(T=T, Q=Q, pages=data[T], out_dir=str(RUNS), off=1000 * ti + 10 * fi))
    # largest training sets first is irrelevant; order by translit
    nproc = max(1, min(len(jobs), (os.cpu_count() or 2) - 2))
    emit(f"running {len(jobs)} fold jobs on {nproc} worker processes")
    allres = {}
    with Pool(nproc) as pool:
        for r in pool.imap_unordered(run_fold, jobs):
            allres[(r["T"], r["Q"])] = r
            print(f"[{time.time() - t0:.0f}s] done {r['T']} {r['Q']} ({r['secs']:.0f}s) CA {r['models']['CA']['n']}/6", flush=True)
            if time.time() - t0 > RUN_LIMIT:
                pool.terminate()
                raise TimeoutError("run exceeded 60 minutes")
    for T in TRANSLITS:
        emit(f"=== {T} ===")
        for Q in folds:
            for ln in allres[(T, Q)]["lines"]:
                emit(ln)
        emit("")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    verdict, summ = summarize(allres, {T: folds for T in TRANSLITS}, emit)
    emit("MULTIPLICITY (D-056): 4th producer evaluated in phase 4, first on leave-one-quire-out.  P1 is partly built in by the fit (Moran is a fit target).")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "cells.json").write_text(json.dumps({f"{T}|{Q}": {k: v for k, v in r.items() if k != "lines"} for (T, Q), r in allres.items()},
                                                indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)),
                                     encoding="utf-8", newline="\n")
    emit("")
    emit(f"elapsed: {time.time() - t0:.1f} s")
    emit(f"date end: {clock()}")
    emit(f"paths: {OUT}, {RUNS}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--list-imports" in sys.argv:
        for m in local_modules():
            print(m)
        sys.exit(0)
    if "--fixture" in sys.argv:
        sys.exit(0 if fixture() else 1)
    main()
