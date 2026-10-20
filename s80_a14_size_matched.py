"""S80: is A14 ("different cores carry no sequential order") an artifact of inventory size?

QUESTION (frozen): A14 rests on the core->core MI excess over a within-line shuffle on held-out pages (s55 f2,
about -0.05 on ZL3b/RF1b/IT2a under SlotSegmenter, ~2,400 core types).  s76 (results_s76.txt) found +0.07..+0.08
under Zattera's segmenter (84-165 core types) and ~0 / negative under SlotSegmenter and whole words (~4,100 types).
Suspicion: a plug-in MI excess over thousands of sparse types cannot see order.  Then A14 is an artifact and the
P4-D1 exclusion (results_p4d1_core_order.txt) and s50's h2/A14 conflict need re-examination.

PRE-REGISTRATION: s80_a14_size_matched.prereg.sha256 (sha256sum format, LF, no BOM) = sha256 of this file and of
every local module it imports, frozen BEFORE any real-data run.  Before the freeze the script ran only with --plant
(synthetic fixture; reads no real data; writes only runs/s80/fixture.txt).  The script re-hashes itself and its
local imports and prints stub_match.  Disclosed pre-freeze look at real data: page counts and held-out token counts
of the candidate texts (no segmentation, no statistic) were listed to set the matching rule below.

DESIGN (fixed before any real-data run)
 Controlled variable: core inventory size.  For each text, cores are mapped to K classes, K in {25, 50, 100, 200,
   400, 800, full}.  Two collapse methods, fitted on the text's TRAINING pages only, applied to held-out pages:
   M-freq : the top K-1 training cores (by training token count; ties by core string) keep their identity; every
            other core (rarer or unseen in training) goes to one OTHER class.
   M-clust: k-means on left/right context vectors (Brown-style distributional classes; sklearn KMeans, n_init 3,
            random_state 20261017, sample_weight = training count).  Context vocabulary = the 300 most frequent
            training cores + <s> + </s> + <other>; a core's vector = sqrt of its left-neighbour distribution
            concatenated with sqrt of its right-neighbour distribution (within-line neighbours; Hellinger
            geometry).  Clustered: cores with training count >= 2, into K-1 clusters (min with the number of
            distinct vectors); cores with training count < 2 and unseen cores form one RARE class.  If there are
            no more clusterable cores than K-1, each keeps its identity.  [CHOICE: k-means, not Brown merging,
            for run time.]
   full   : raw core identity (s55 f2's own labels; same for both methods).
 Segmenter per text: scoreboard/metrics_new.SlotSegmenter (defaults) fitted on the training pages' tokens (s55
   convention); Voynich ZL3b additionally under s76's ZatteraSegmenter ("drop" undecomposable words, PRIMARY
   layers), imported from s76_segmenter_independence with s76's filt_lines_pages.
 Split: g1_edge_joint.split_names (random.Random(20261017) page shuffle, first round(0.8 n) training; 166/41 on
   ZL3b) = s55 split_pages.
 Size matching (tokens): N_match = the smallest held-out token count over the QUALIFYING texts (>= 8 held-out pages
   and >= 5,000 held-out tokens, measured after segmentation filtering).  Each qualifying text's matched set = its
   held-out pages in random.Random(20261017 + 80) order, taken until N_match tokens, the last page cut after the
   N_match-th token (line structure kept).  Non-qualifying texts are scored on all their held-out tokens and
   flagged UNMATCHED (descriptive only, never in a call or a percentile).
 Statistic (per labeling, on the matched set): s55 f2 on class labels = MI(L_t; L_t+1) over within-line adjacent
   pairs minus the mean over 200 within-line shuffles (the line's tokens permuted, as s55's lexsort shuffle;
   np.random.default_rng(20261017); the same shuffles are applied to every labeling of a text).  Two estimators:
   plug-in, and Miller-Madow (MI_MM = MI_plug + ((m_A - 1) + (m_B - 1) - (m_AB - 1)) / (2 N ln 2), m = occupied
   cells, N = pairs), each minus its own shuffle mean.  PRIMARY = Miller-Madow; plug-in printed beside.
 Interval: 500 draws of round(0.8 x matched-set pages) without replacement, each scored with 20 shuffles, one
   np.random.default_rng(20261018) stream shared by all labelings of a text; 95 % = [2.5, 97.5] percentiles;
   the subsample median printed beside (s76 caveat: the plug-in on 80 % subsamples runs below the full point; seen
   again on this fixture for MM too, so the percentile interval sits below the point and is conservative for C1).
   A recentred interval (percentile interval + point - subsample median; "rc") is printed beside, not gating.
   Texts are scored in 12 worker processes (concurrent.futures; each worker single-threaded via threadpoolctl).
 Texts:
   VOY      : Voynich ZL3b, RF1b, IT2a (s55 voynich_pages) under SlotSegmenter; ZL3b under Zattera (VOYZ, reported
              in C2 beside, not gating).
   CIPHER   : P4-D1 K1 letter-in-core and K3 chunk-in-core, 6 plaintexts (corpora.CONTROLS), generator seed 1 only,
              regenerated by importing p4d1_core_order (voynich_lines, assign, chunks, plant) exactly as its main();
              each planted line takes the ZL3b paragraph line's page, giving pages for the split.  12 texts.
   LANG     : s49 lang_* (6) + real-line controls cremma_prose15 and italian_dante (s56 references).
   GEN      : the 6 s55 GEN texts (runs/s49) and the 9 s57 generator sidecars runs/s57/gen_*.meta.json.
 Reproduction checks (printed, not gating): s55 f2 exact via s55 TextData.core_core for ZL3b (published -0.05279);
   P4-D1 core_excess on the regenerated seed-1 ciphers vs the seed-1 values printed in results_p4d1_core_order.txt.

PRE-REGISTERED CALLS (on the MM excess; the same rules on the plug-in printed beside)
 C1 (A14 artifact test): Voynich ZL3b (SlotSegmenter), M-freq, K = 100: if the 95 % interval lower bound > 0 ->
    C1 TRUE ("A14 as stated, no order, is FALSE at matched size"); else C1 FALSE.
 C2 (A14 separation test): cells = {ZL3b, RF1b, IT2a under SlotSegmenter} x {M-freq, M-clust} x K {50, 100, 200}
    (18 cells).  In each cell compare the Voynich point to the 12 CIPHER points: "below" if < their 10th
    percentile (numpy linear), "inside" if >= their minimum, else "between".  "A14-separation holds" if all 18 cells
    are below; "separation fails" if any cell is inside; otherwise "mixed".
 C3 (language comparison, descriptive): at each K and method, the Voynich value against the LANG references
    (count of matched LANG texts below Voynich, their min / median / max).
 FINAL READING (fixed):
    C2 fails                -> "P4-D1 exclusion does not survive matched size; reopen letter-in-core ciphers"
    C1 TRUE and C2 holds    -> "A14 restated: cores do carry order, but less than letter-in-core ciphers; P4-D1
                               exclusion stands on matched size"
    C1 FALSE (C2 not fails) -> "A14 stands at matched size"
    C1 TRUE and C2 mixed    -> "A14 as stated is false at matched size; separation from letter-in-core ciphers
                               is mixed (cells listed); P4-D1 exclusion not settled"   [added branch, the brief
                               names no reading for it]

FIXTURE (--plant; synthetic, identity segmenter = the word IS the core; reads no real data):
  F_order : 2,400 core types in 40 latent classes (60 cores each, within-class Zipf 1.0); class chain with
            P(next = fixed successor) = 0.6, else uniform; 207 pages x 20 lines x Poisson(8) words.
  F_letter: 26-letter Markov source (rows Dirichlet 0.3), each letter written by one of 92 homophone cores (Zipf),
            2,392 types (letter-in-core at a large inventory).
  F_none  : cores iid from F_order's marginal (no order).
  F_small : like F_order on 120 types (3 per class), for the size contrast.
  F_weak  : 80 classes x 30 uniform cores (2,400 types), P(successor) = 0.25 (weak order, flat inventory).
  [Added after the first fixture pass, before the freeze: F_weak, rc interval, worker pool, dense-bincount
   threshold; the first pass showed the full plug-in does NOT miss F_order's strong Zipf-headed order.]
  Checks: FX1 F_none MM interval includes 0 at K 50/100/200, both methods.  FX2 F_order and F_letter MM interval
  lower bound > 0 at K 50/100/200, both methods.  FX3 (the demonstration, reported): does the full-inventory
  plug-in miss the planted order (interval includes 0, or point < half the M-freq K = 100 MM point)?  (F_order,
  F_letter, F_small, F_weak.)
FIXTURE OUTCOME BEFORE THE FREEZE (second pass, recorded in runs/s80/fixture.txt; no criterion was changed after it):
  FX2 PASS.  FX1 FAIL on one of 6 cells (F_none, M-clust K = 50, MM lower bound +0.0006; the other 5 include 0);
  read as a chance 95 % miss among 6 correlated cells, but stated: an M-clust interval can exclude 0 on an
  order-free text, so a single M-clust cell is weak evidence.  FX3: the full-inventory plug-in does NOT miss strong
  planted order at ~1,600-2,200 types (F_order +0.19, F_letter +0.09); it misses F_weak, and so does every
  collapsed K (M-freq at K 50/100 even reads significantly NEGATIVE on F_weak: order plus line-level class
  composition can push a within-line-shuffle excess below 0).  So the fixture does not show the hypothesised
  mechanism ("matched K recovers order the full plug-in misses"); the real run is read with that in mind.
Constraints: python -I; writes ONLY results_s80.txt and runs/s80/ (fixture: only runs/s80/fixture.txt).  Wall 45 min.
Run: python -I s80_a14_size_matched.py      Fixture: --plant      Stub helper: --list-locals
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import subprocess
import sys
import time
import warnings
from collections import Counter, OrderedDict
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

import g1_edge_joint as G1  # noqa: E402
import p4d1_core_order as P4  # noqa: E402
import s55_code_vs_generator as S55  # noqa: E402
import s76_segmenter_independence as S76  # noqa: E402
import vparse  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s80_a14_size_matched.py"
STUB = ROOT / "s80_a14_size_matched.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s80"
SEED = 20261017
FIXTURE = "--plant" in sys.argv   # own flag: s55 reads "--fixture", s76 "--synthetic" from argv at import
LIST_LOCALS = "--list-locals" in sys.argv
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / "results_s80.txt"
WALL = 45 * 60
KS = [25, 50, 100, 200, 400, 800, "full"]
METHODS = ["freq", "clust"]
N_SHUF = 200
N_DRAW = 500
N_DRAW_SHUF = 20
SUB_FRAC = 0.8
N_CTX = 300
N_WORKERS = 12
QUAL_PAGES, QUAL_TOK = 8, 5000
C2_KS = [50, 100, 200]
S55_F2_ZL = -0.05279
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
    return sorted(set(out) | {SELF.name})


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
    missing = [m for m in local_modules() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; loaded but not in stub: {', '.join(missing) or '-'})"


# ======================================================================= MI machinery
LN2 = math.log(2.0)


def _h_rows(counts_sum_clogc, n):
    return math.log2(n) - counts_sum_clogc / n


def mi_batch(A, B, K):
    """A, B: (S, n) int arrays of labels in [0, K).  -> (plug (S,), mm (S,)) in bits."""
    S, n = A.shape
    off = np.arange(S, dtype=np.int64)[:, None]

    def ent_marg(X):
        c = np.bincount((off * K + X).ravel(), minlength=S * K).reshape(S, K).astype(float)
        m = (c > 0).sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            cl = np.where(c > 0, c * np.log2(np.where(c > 0, c, 1)), 0.0).sum(1)
        return np.log2(n) - cl / n, m
    ha, ma = ent_marg(A)
    hb, mb = ent_marg(B)
    KK = K * K
    codes = (off * KK + A.astype(np.int64) * K + B).ravel()
    if S * KK <= 300_000:
        c = np.bincount(codes, minlength=S * KK).reshape(S, KK).astype(float)
        mj = (c > 0).sum(1)
        cl = np.where(c > 0, c * np.log2(np.where(c > 0, c, 1)), 0.0).sum(1)
    else:
        u, cnt = np.unique(codes, return_counts=True)
        s = u // KK
        cl = np.bincount(s, weights=cnt * np.log2(cnt), minlength=S)
        mj = np.bincount(s, minlength=S)
    hj = np.log2(n) - cl / n
    plug = ha + hb - hj
    mm = plug + ((ma - 1) + (mb - 1) - (mj - 1)) / (2.0 * n * LN2)
    return plug, mm


class Scorer:
    """Within-line adjacent-pair MI excess for several labelings sharing the same shuffles."""
    def __init__(self, lid):
        self.lid = np.asarray(lid, dtype=np.int64)
        same = self.lid[1:] == self.lid[:-1]
        self.left = np.nonzero(same)[0]
        self.right = self.left + 1
        self.lidf = self.lid.astype(float)

    def perms(self, S, rng):
        return np.argsort(self.lidf[None, :] + rng.random((S, len(self.lid))), axis=1)

    def excess(self, labelings, n_shuf, rng, chunk=50):
        """labelings: list of compact int arrays (len n) -> list of (plug_excess, mm_excess)."""
        if len(self.left) < 2:
            return [(float("nan"), float("nan"))] * len(labelings)
        Ks = [int(x.max()) + 1 for x in labelings]
        obs = [mi_batch(x[self.left][None], x[self.right][None], k) for x, k in zip(labelings, Ks)]
        nul_p = [[] for _ in labelings]; nul_m = [[] for _ in labelings]
        done = 0
        while done < n_shuf:
            S = min(chunk, n_shuf - done)
            P = self.perms(S, rng)
            for i, (x, k) in enumerate(zip(labelings, Ks)):
                xs = x[P]
                p, m = mi_batch(xs[:, self.left], xs[:, self.right], k)
                nul_p[i].append(p); nul_m[i].append(m)
            done += S
        out = []
        for i in range(len(labelings)):
            out.append((float(obs[i][0][0] - np.concatenate(nul_p[i]).mean()),
                        float(obs[i][1][0] - np.concatenate(nul_m[i]).mean())))
        return out


def compact(arr):
    _, inv = np.unique(arr, return_inverse=True)
    return inv.astype(np.int64)


# ======================================================================= collapse (fit on training)
def fit_freq(tr_counts, K):
    if K == "full":
        return None
    keep = [c for c, _ in sorted(tr_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:K - 1]]
    return {c: i for i, c in enumerate(keep)}          # others -> OTHER (= len(keep))


def fit_clust(tr_lines, tr_counts, K, ctx_cache):
    if K == "full":
        return None
    clus = sorted([c for c, n in tr_counts.items() if n >= 2], key=lambda c: (-tr_counts[c], c))
    if len(clus) <= K - 1:
        return {c: i for i, c in enumerate(clus)}
    X, w = ctx_cache.get("X"), ctx_cache.get("w")
    if X is None:
        top = [c for c, _ in sorted(tr_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:N_CTX]]
        ci = {c: i for i, c in enumerate(top)}
        nC = len(top) + 3   # + <s>/</s> (shared slot index len(top)), </s> len(top)+1, <other> len(top)+2
        row = {c: i for i, c in enumerate(clus)}
        L = np.zeros((len(clus), nC)); R = np.zeros((len(clus), nC))
        for ln in tr_lines:
            for j, c in enumerate(ln):
                r = row.get(c)
                if r is None:
                    continue
                lc = len(top) if j == 0 else ci.get(ln[j - 1], len(top) + 2)
                rc = len(top) + 1 if j == len(ln) - 1 else ci.get(ln[j + 1], len(top) + 2)
                L[r, lc] += 1; R[r, rc] += 1
        L /= L.sum(1, keepdims=True); R /= R.sum(1, keepdims=True)
        X = np.sqrt(np.hstack([L, R]))
        w = np.array([tr_counts[c] for c in clus], dtype=float)
        ctx_cache["X"], ctx_cache["w"] = X, w
    from sklearn.cluster import KMeans
    n_distinct = len(np.unique(np.round(X, 12), axis=0))
    k = min(K - 1, n_distinct)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        km = KMeans(n_clusters=k, n_init=3, random_state=SEED).fit(X, sample_weight=w)
    return {c: int(l) for c, l in zip(clus, km.labels_)}


def apply_map(cores, mp):
    if mp is None:
        ids = {}
        return np.array([ids.setdefault(c, len(ids)) for c in cores], dtype=np.int64)
    other = max(mp.values(), default=-1) + 1
    return compact(np.array([mp.get(c, other) for c in cores], dtype=np.int64))


# ======================================================================= per-text pipeline
def identity_seg_factory(tokens):
    class _Id:
        def segment(self, w):
            return ("", w, "")
    return _Id()


def prepare(name, group, pages, seg_factory):
    """pages: list of (id, lines).  -> dict with training core lines and held-out page core lines."""
    by = OrderedDict()
    for pid, lines in pages:
        L = [[w for w in ln if w] for ln in lines]
        L = [ln for ln in L if ln]
        if L:
            by[str(pid)] = L
    tr, te = G1.split_names(by)
    seg = seg_factory([w for p in tr for ln in by[p] for w in ln])
    cache = {}

    def core(w):
        c = cache.get(w)
        if c is None:
            c = cache[w] = seg.segment(w)[1]
        return c
    tr_lines = [[core(w) for w in ln] for p in tr for ln in by[p]]
    te_pages = [(p, [[core(w) for w in ln] for ln in by[p]]) for p in te]
    return dict(name=name, group=group, tr_lines=tr_lines, te_pages=te_pages, n_tr=len(tr), n_te=len(te),
                te_tok=sum(len(ln) for _, ls in te_pages for ln in ls),
                tr_counts=Counter(c for ln in tr_lines for c in ln))


def matched_set(T, n_match):
    pages = list(T["te_pages"])
    if n_match is None:
        return pages
    order = [p for p, _ in pages]
    random.Random(SEED + 80).shuffle(order)
    d = dict(pages)
    out, tot = [], 0
    for p in order:
        if tot >= n_match:
            break
        L = []
        for ln in d[p]:
            if tot >= n_match:
                break
            take = ln[:n_match - tot]
            L.append(take); tot += len(take)
        out.append((p, L))
    return out


def arrays(mset):
    cores, lid, pg = [], [], []
    li = 0
    for pi, (_, lines) in enumerate(mset):
        for ln in lines:
            cores.extend(ln); lid.extend([li] * len(ln)); pg.extend([pi] * len(ln)); li += 1
    return cores, np.array(lid, dtype=np.int64), np.array(pg, dtype=np.int64)


def measure_job(args):
    T, n_match = args
    t = time.time()
    try:
        from threadpoolctl import threadpool_limits
        with threadpool_limits(1):
            res, info = measure(T, n_match)
    except ImportError:
        res, info = measure(T, n_match)
    info["secs"] = time.time() - t
    return res, info


def run_all(jobs):
    """jobs: list of (T, n_match) -> list of (res, info), in order; N_WORKERS processes."""
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        return list(ex.map(measure_job, jobs))


def measure(T, n_match, n_shuf=N_SHUF, n_draw=N_DRAW, n_draw_shuf=N_DRAW_SHUF):
    mset = matched_set(T, n_match)
    cores, lid, pg = arrays(mset)
    labs, keys, ncls = [], [], {}
    cache = {}
    full = apply_map(cores, None)
    for meth in METHODS:
        for K in KS:
            if K == "full":
                keys.append((meth, K)); labs.append(full); ncls[(meth, K)] = int(full.max()) + 1
                continue
            mp = fit_freq(T["tr_counts"], K) if meth == "freq" else fit_clust(T["tr_lines"], T["tr_counts"], K, cache)
            x = apply_map(cores, mp)
            keys.append((meth, K)); labs.append(x); ncls[(meth, K)] = int(x.max()) + 1
    sc = Scorer(lid)
    pt = sc.excess(labs, n_shuf, np.random.default_rng(SEED))
    rng = np.random.default_rng(SEED + 1)
    npg = len(mset); m = int(round(SUB_FRAC * npg))
    draws = [[] for _ in labs]
    page_idx = [np.nonzero(pg == i)[0] for i in range(npg)]
    for _ in range(n_draw):
        sel = np.sort(rng.choice(npg, size=m, replace=False))
        idx = np.concatenate([page_idx[i] for i in sel])
        sub = Scorer(lid[idx])
        r = sub.excess([compact(x[idx]) for x in labs], n_draw_shuf, rng)
        for i, v in enumerate(r):
            draws[i].append(v)
    res = OrderedDict()
    for i, k in enumerate(keys):
        D = np.array(draws[i])
        res[k] = dict(ncls=ncls[k], plug=pt[i][0], mm=pt[i][1],
                      plug_ci=(float(np.nanpercentile(D[:, 0], 2.5)), float(np.nanpercentile(D[:, 0], 97.5))),
                      mm_ci=(float(np.nanpercentile(D[:, 1], 2.5)), float(np.nanpercentile(D[:, 1], 97.5))),
                      plug_med=float(np.nanmedian(D[:, 0])), mm_med=float(np.nanmedian(D[:, 1])))
        # recentred (basic-shift) interval, reported only: percentile interval shifted by point - subsample median
        for e in ("plug", "mm"):
            sh = res[k][e] - res[k][e + "_med"]
            res[k][e + "_rc"] = (res[k][e + "_ci"][0] + sh, res[k][e + "_ci"][1] + sh)
    return res, dict(tokens=len(cores), pages=npg, pairs=int(len(sc.left)), core_types=int(full.max()) + 1)


# ======================================================================= text sources
def ksort(k):
    return 10 ** 9 if k == "full" else k


def voy_pages(T):
    return [(p["id"], p["lines"]) for p in S55.voynich_pages(T)]


def meta_pages(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return [(p["id"], p["lines"]) for p in d["pages"]]


def cipher_texts():
    """P4-D1 K1 / K3, seed 1, regenerated with p4d1_core_order's own functions as in its main()."""
    zpath = dict(P4.s34.TRANSLITS)["ZL3b"]
    recs = vparse.paragraph_text(vparse.load(path=zpath))
    zl_lines = P4.voynich_lines(zpath)
    assert len(recs) == len(zl_lines)
    line_page = [r["page"] for r in recs]
    zl_tokens = [w for _, ln in zl_lines for w in ln]
    zseg = P4.mn.SlotSegmenter(zl_tokens)
    trip = [zseg.segment(w) for w in zl_tokens]
    core_freq = Counter(c for _, c, _ in trip)
    aff = Counter((p, s) for p, _, s in trip)
    affix_pairs, affix_w = list(aff), list(aff.values())
    line_lens = [len(ln) for _, ln in zl_lines]
    n_target = sum(line_lens)
    out = OrderedDict()
    for name in P4.corpora.CONTROLS:
        words = P4.corpora.control(name)
        letters = [ch for w in words for ch in w]
        for fam in ("K1", "K3"):
            rng = random.Random(1)
            units = letters[:n_target] if fam == "K1" else P4.chunks(letters[:2 * n_target], rng)[:n_target]
            table = P4.assign(Counter(units), core_freq)
            lines, _oracle = P4.plant(units, table, affix_pairs, affix_w, line_lens, rng)
            pages = OrderedDict()
            for i, ln in enumerate(lines):
                pages.setdefault(line_page[i], []).append(ln)
            out[f"{fam}_{name}"] = (list(pages.items()), lines)
    return out


def p4d1_seed1():
    vals = {}
    f = ROOT / "results_p4d1_core_order.txt"
    for ln in f.read_text(encoding="utf-8").splitlines():
        parts = ln.split()
        if parts and parts[0] in ("K1", "K3") and "seeds" in parts:
            vals[f"{parts[0]}_{parts[1]}"] = float(parts[parts.index("seeds") + 1])
    return vals


# ======================================================================= fixture
def zipf_w(n, a=1.0):
    w = 1.0 / np.arange(1, n + 1) ** a
    return w / w.sum()


def fx_pages(stream_fn, rng, n_pages=207, n_lines=20, lam=8):
    pages = []
    for p in range(n_pages):
        lines = []
        for _ in range(n_lines):
            n = max(1, int(rng.poisson(lam)))
            lines.append([stream_fn() for _ in range(n)])
        pages.append((f"p{p}", lines))
    return pages


def fixture_texts():
    rng = np.random.default_rng(7)
    out = OrderedDict()

    def classed(n_cls, per, order):
        succ = rng.permutation(n_cls); wz = zipf_w(per)
        st = {"c": int(rng.integers(n_cls))}

        def nxt():
            c = st["c"]
            if order:
                st["c"] = int(succ[c]) if rng.random() < 0.6 else int(rng.integers(n_cls))
            else:
                st["c"] = int(rng.integers(n_cls))
            return f"c{c}_{int(rng.choice(per, p=wz))}"
        return nxt
    out["F_order"] = fx_pages(classed(40, 60, True), rng)
    out["F_none"] = fx_pages(classed(40, 60, False), rng)
    out["F_small"] = fx_pages(classed(40, 3, True), rng)
    T = rng.dirichlet([0.3] * 26, size=26); wz = zipf_w(92); st = {"l": 0}

    def letter():
        l = st["l"]; st["l"] = int(rng.choice(26, p=T[l]))
        return f"L{l}_{int(rng.choice(92, p=wz))}"
    out["F_letter"] = fx_pages(letter, rng)
    succ = rng.permutation(80); st2 = {"c": 0}

    def weak():
        c = st2["c"]
        st2["c"] = int(succ[c]) if rng.random() < 0.25 else int(rng.integers(80))
        return f"w{c}_{int(rng.integers(30))}"
    out["F_weak"] = fx_pages(weak, rng)
    return out


def fmt(v, ci):
    return f"{v:+.4f} [{ci[0]:+.4f},{ci[1]:+.4f}]"


def run_fixture():
    emit("S80 FIXTURE (synthetic only; identity segmenter; no real data read)")
    emit(f"date: {clock()}")
    emit(f"s80_a14_size_matched.py sha256={sha256(SELF)}  stub_match={stub_match()}")
    texts = fixture_texts()
    prep = OrderedDict((n, prepare(n, "FX", p, identity_seg_factory)) for n, p in texts.items())
    n_match = min(T["te_tok"] for T in prep.values())
    emit(f"N_match = {n_match} held-out tokens (smallest fixture held-out set)")
    R = OrderedDict()
    outs = run_all([(T, n_match) for T in prep.values()])
    for (n, T), (res, info) in zip(prep.items(), outs):
        R[n] = res
        emit(f"\n  {n}: train pages {T['n_tr']} held-out {T['n_te']}; matched tokens {info['tokens']} pages {info['pages']} "
             f"pairs {info['pairs']} core types {info['core_types']}  [{info['secs']:.0f}s]")
        for (meth, K), v in res.items():
            emit(f"    {meth:5s} K={str(K):>4s} classes {v['ncls']:>5d} | MM {fmt(v['mm'], v['mm_ci'])} med {v['mm_med']:+.4f} rc {fmt(v['mm'], v['mm_rc'])[8:]}"
                 f" | plug {fmt(v['plug'], v['plug_ci'])} med {v['plug_med']:+.4f}")
        flush()
    fx1 = all(R["F_none"][(m, K)]["mm_ci"][0] <= 0 <= R["F_none"][(m, K)]["mm_ci"][1] for m in METHODS for K in C2_KS)
    fx2 = all(R[n][(m, K)]["mm_ci"][0] > 0 for n in ("F_order", "F_letter") for m in METHODS for K in C2_KS)
    emit("")
    emit(f"FX1 F_none MM interval includes 0 at K 50/100/200, both methods: {'PASS' if fx1 else 'FAIL'}")
    emit(f"FX2 F_order, F_letter MM lower bound > 0 at K 50/100/200, both methods: {'PASS' if fx2 else 'FAIL'}")
    for n in ("F_order", "F_letter", "F_small", "F_weak"):
        fp = R[n][("freq", "full")]; k100 = R[n][("freq", 100)]
        miss = fp["plug_ci"][0] <= 0 or fp["plug"] < 0.5 * k100["mm"]
        emit(f"FX3 {n}: full-inventory plug-in {fmt(fp['plug'], fp['plug_ci'])} vs M-freq K=100 MM {fmt(k100['mm'], k100['mm_ci'])}"
             f" -> full plug-in {'MISSES' if miss else 'does not miss'} the planted order")
    emit(f"FIXTURE {'PASS' if fx1 and fx2 else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {clock()}")
    flush()


# ======================================================================= main
def main():
    if LIST_LOCALS:
        for m in local_modules():
            print(m)
        return
    if FIXTURE:
        run_fixture()
        return
    emit("S80: A14 at matched core-inventory size (pre-registered in the docstring; no edits after the freeze)")
    emit(f"date: {clock()}")
    emit(f"s80_a14_size_matched.py sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    import sklearn
    emit(f"python {sys.version.split()[0]}; numpy {np.__version__}; sklearn {sklearn.__version__}; seed {SEED}; "
         f"shuffles {N_SHUF}; interval {N_DRAW} draws of {int(SUB_FRAC * 100)} % of matched pages x {N_DRAW_SHUF} shuffles")

    texts = []   # (name, group, pages, seg_factory)
    for T in ("ZL3b", "RF1b", "IT2a"):
        texts.append((f"VOY_{T}", "VOY", voy_pages(T), SlotSegmenter))
    zp = S76.filt_lines_pages(S55.voynich_pages("ZL3b"))
    texts.append(("VOYZ_ZL3b_zattera", "VOYZ", [(p["id"], p["lines"]) for p in zp],
                  lambda toks: S76.ZatteraSegmenter("drop", "primary", toks)))
    ciph = cipher_texts()
    for n, (pages, _lines) in ciph.items():
        texts.append((n, "CIPHER", pages, SlotSegmenter))
    lang = sorted((ROOT / "runs" / "s49").glob("lang_*.meta.json"))
    lang += [ROOT / "data" / "controls_realline" / "cremma_prose15.meta.json",
             ROOT / "data" / "controls_realline" / "italian_dante.meta.json"]
    for f in lang:
        nm = f.name.replace(".meta.json", "")
        nm = nm if nm.startswith("lang_") else "realline_" + nm
        texts.append((nm, "LANG", meta_pages(f), SlotSegmenter))
    for n in ("gen_s28_ZL3b_s1", "gen_c2_section", "gen_timm_schinner", "gen_schwartz_reuse", "gen_rugg_grille",
              "gen_G2layer_ZL3b_s1"):
        texts.append((n, "GEN", meta_pages(ROOT / "runs" / "s49" / f"{n}.meta.json"), SlotSegmenter))
    for f in sorted((ROOT / "runs" / "s57").glob("gen_*.meta.json")):
        texts.append(("s57_" + f.name.replace(".meta.json", ""), "GEN57", meta_pages(f), SlotSegmenter))
    emit(f"texts: {len(texts)} (VOY 3, VOYZ 1, CIPHER {len(ciph)}, LANG {len(lang)}, GEN 6, GEN57 "
         f"{sum(1 for t in texts if t[1] == 'GEN57')})")

    # ---- reproduction checks
    emit("\n=== reproduction checks (not gating) ===")
    td = S55.TextData("ZL3b", S55.voynich_pages("ZL3b"))
    c_, _f, l_, _s, _p = td.concat(td.hp)
    f2 = td.core_core(c_, l_, 200, np.random.default_rng(SEED))
    emit(f"  s55 f2 ZL3b via s55 TextData.core_core: {f2:+.5f} (published {S55_F2_ZL:+.5f}) -> "
         f"{'MATCH' if abs(f2 - S55_F2_ZL) < 5e-5 else 'DIFFERS'}")
    pub = p4d1_seed1()
    for n, (_pages, lines) in ciph.items():
        ex, _sd, nc, _np = P4.core_excess([w for ln in lines for w in ln], lines)
        emit(f"  P4-D1 {n:22s} seed 1 core_excess {ex:+.4f} (published {pub.get(n, float('nan')):+.4f}) cores {nc} -> "
             f"{'MATCH' if abs(ex - pub.get(n, 9)) < 5e-5 else 'DIFFERS'}")
    flush()

    # ---- prepare and match
    prep = OrderedDict()
    for n, g, pages, sf in texts:
        prep[n] = prepare(n, g, pages, sf)
    qual = {n: (T["n_te"] >= QUAL_PAGES and T["te_tok"] >= QUAL_TOK) for n, T in prep.items()}
    n_match = min(T["te_tok"] for n, T in prep.items() if qual[n])
    smallest = min((T["te_tok"], n) for n, T in prep.items() if qual[n])[1]
    emit(f"\n=== size matching: N_match = {n_match} held-out tokens (smallest qualifying held-out set: {smallest}); "
         f"qualifying = >= {QUAL_PAGES} held-out pages and >= {QUAL_TOK} held-out tokens ===")
    for n, T in prep.items():
        emit(f"  {n:28s} {T['group']:6s} train/held-out pages {T['n_tr']}/{T['n_te']} held-out tokens {T['te_tok']:6d} "
             f"training core types {len(T['tr_counts']):5d}  {'matched' if qual[n] else 'UNMATCHED (scored on all held-out tokens)'}")
    flush()

    # ---- measure
    R, INFO = OrderedDict(), OrderedDict()
    emit("\n=== measures (MM = Miller-Madow excess, PRIMARY; plug = plug-in excess; [95 % interval] med = subsample median) ===")
    outs = run_all([(T, n_match if qual[n] else None) for n, T in prep.items()])
    for (n, T), (res, info) in zip(prep.items(), outs):
        R[n], INFO[n] = res, dict(info, group=T["group"], matched=qual[n])
        emit(f"\n  {n} ({T['group']}{'' if qual[n] else ', UNMATCHED'}): tokens {info['tokens']} pages {info['pages']} "
             f"pairs {info['pairs']} core types {info['core_types']}  [{info['secs']:.0f}s in worker]")
        for (meth, K), v in res.items():
            emit(f"    {meth:5s} K={str(K):>4s} cls {v['ncls']:>5d} | MM {fmt(v['mm'], v['mm_ci'])} med {v['mm_med']:+.4f} rc {fmt(v['mm'], v['mm_rc'])[8:]}"
                 f" | plug {fmt(v['plug'], v['plug_ci'])} med {v['plug_med']:+.4f}")
    emit(f"  measured in {time.time() - T0:.0f}s total")
    flush()
    if time.time() - T0 > WALL:
        emit(f"WALL LIMIT {WALL}s exceeded")

    # ---- sidecar values
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "values.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "group", "matched", "method", "K", "classes", "mm", "mm_lo", "mm_hi", "mm_med",
                    "plug", "plug_lo", "plug_hi", "plug_med", "mm_rc_lo", "mm_rc_hi", "tokens", "pairs", "core_types"])
        for n, res in R.items():
            for (meth, K), v in res.items():
                w.writerow([n, INFO[n]["group"], INFO[n]["matched"], meth, K, v["ncls"]] +
                           [f"{x:.6f}" for x in (v["mm"], *v["mm_ci"], v["mm_med"], v["plug"], *v["plug_ci"], v["plug_med"], *v["mm_rc"])] +
                           [INFO[n]["tokens"], INFO[n]["pairs"], INFO[n]["core_types"]])
    (RUN_DIR / "texts.json").write_text(json.dumps(INFO, indent=1), encoding="utf-8", newline="\n")

    # ---- summary table
    emit("\n=== excess vs K (MM point [95 %]; plug-in point beside) ===")
    for meth in METHODS:
        emit(f"  method M-{meth}")
        emit("    " + f"{'text':28s}" + "".join(f"{'K=' + str(K):>26s}" for K in KS))
        for n, res in R.items():
            emit("    " + f"{n:28s}" + "".join(f"{res[(meth, K)]['mm']:+.3f}[{res[(meth, K)]['mm_ci'][0]:+.3f},{res[(meth, K)]['mm_ci'][1]:+.3f}]".rjust(26) for K in KS))
        emit("    plug-in points:")
        for n, res in R.items():
            emit("    " + f"{n:28s}" + "".join(f"{res[(meth, K)]['plug']:+.4f}".rjust(26) for K in KS))
    flush()

    # ---- calls
    calls = OrderedDict()
    emit("\n=== PRE-REGISTERED CALLS (MM primary; plug-in beside) ===")
    for est in ("mm", "plug"):
        tag = "PRIMARY MM" if est == "mm" else "plug-in (reported)"
        v = R["VOY_ZL3b"][("freq", 100)]
        c1 = v[f"{est}_ci"][0] > 0
        emit(f"  [{tag}] C1 ZL3b M-freq K=100: {fmt(v[est], v[est + '_ci'])} -> C1 {'TRUE (A14 as stated is FALSE at matched size)' if c1 else 'FALSE'}")
        ciphs = [n for n in R if INFO[n]["group"] == "CIPHER" and INFO[n]["matched"]]
        cells = []
        for T in ("VOY_ZL3b", "VOY_RF1b", "VOY_IT2a", "VOYZ_ZL3b_zattera"):
            for meth in METHODS:
                for K in C2_KS:
                    cv = np.array([R[c][(meth, K)][est] for c in ciphs])
                    p10, cmin, cmax = float(np.percentile(cv, 10)), float(cv.min()), float(cv.max())
                    x = R[T][(meth, K)][est]
                    st = "below" if x < p10 else "inside" if x >= cmin else "between"
                    gating = T != "VOYZ_ZL3b_zattera"
                    if gating:
                        cells.append(st)
                    emit(f"  [{tag}] C2 {T:18s} M-{meth:5s} K={K:<3d} Voynich {x:+.4f} | ciphers p10 {p10:+.4f} min {cmin:+.4f} "
                         f"max {cmax:+.4f} (n={len(cv)}) -> {st}{'' if gating else ' (reported only)'}")
        c2 = "holds" if all(s == "below" for s in cells) else "fails" if any(s == "inside" for s in cells) else "mixed"
        emit(f"  [{tag}] C2: below {cells.count('below')}, between {cells.count('between')}, inside {cells.count('inside')} of {len(cells)} "
             f"-> {'A14-separation holds' if c2 == 'holds' else 'separation fails' if c2 == 'fails' else 'mixed'}")
        if c2 == "fails":
            final = "P4-D1 exclusion does not survive matched size; reopen letter-in-core ciphers"
        elif c1 and c2 == "holds":
            final = "A14 restated: cores do carry order, but less than letter-in-core ciphers; P4-D1 exclusion stands on matched size"
        elif not c1:
            final = "A14 stands at matched size"
        else:
            final = ("A14 as stated is false at matched size; separation from letter-in-core ciphers is mixed (cells listed); "
                     "P4-D1 exclusion not settled")
        calls[est] = dict(C1=c1, C1_value=v[est], C1_ci=v[est + "_ci"], C2=c2, C2_cells=cells, final=final)
        emit(f"  [{tag}] FINAL READING: {final}")
    emit("\n  C3 (descriptive): Voynich vs matched LANG references (MM)")
    langs = [n for n in R if INFO[n]["group"] == "LANG" and INFO[n]["matched"]]
    c3 = OrderedDict()
    for meth in METHODS:
        for K in KS:
            lv = np.array([R[n][(meth, K)]["mm"] for n in langs])
            row = []
            for T in ("VOY_ZL3b", "VOY_RF1b", "VOY_IT2a", "VOYZ_ZL3b_zattera"):
                x = R[T][(meth, K)]["mm"]
                row.append(f"{T.replace('VOY_', '').replace('VOYZ_ZL3b_zattera', 'Zatt')} {x:+.4f} ({int((lv < x).sum())}/{len(lv)} below)")
                c3[f"{T}|{meth}|{K}"] = dict(v=x, n_lang_below=int((lv < x).sum()), n_lang=len(lv))
            emit(f"    M-{meth:5s} K={str(K):>4s} LANG min {lv.min():+.4f} med {np.median(lv):+.4f} max {lv.max():+.4f} | " + "; ".join(row))
    for grp in ("GEN", "GEN57"):
        gs = [n for n in R if INFO[n]["group"] == grp and INFO[n]["matched"]]
        if gs:
            emit(f"  {grp} references (MM, M-freq): " + "; ".join(
                f"K={K} min {min(R[n][('freq', K)]['mm'] for n in gs):+.4f} max {max(R[n][('freq', K)]['mm'] for n in gs):+.4f}" for K in KS))
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(n_match=n_match, calls=calls, C3=c3), indent=1, default=str),
                                        encoding="utf-8", newline="\n")
    emit(f"\nsidecars: runs/s80/values.csv, runs/s80/texts.json, runs/s80/calls.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {clock()}")
    flush()


if __name__ == "__main__":
    main()
