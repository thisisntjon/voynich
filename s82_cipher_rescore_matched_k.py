"""S82: do the s50 verbose-homophonic family and the P4-D1 letter-in-core family reproduce Voynich's profile once core
order is measured at matched inventory size?

QUESTION (frozen): s80 (results_s80.txt) showed the old A14 statistic (held-out within-line core->core MI excess at the
full core inventory) reads negative even for real languages; at matched inventory size K Voynich cores show weak
positive order (+0.045 at K=100 ZL3b, Miller-Madow).  Two verdicts used the biased full-inventory value as a target:
s50 (results_s50.txt, c-412: no verbose-homophonic family member meets h2, core order and line rhythm together) and
P4-D1 (results_p4d1_core_order.txt).  With core order measured correctly (the matched-K curve), does either family
reproduce Voynich's profile: (1) the matched-K core-order curve, (2) h2, (3) within-line word-length Moran I (A5),
(4) CHARWIN sign, (5) s69/s55 prefix gain f4 > 0.05?

PRE-REGISTRATION: s82_cipher_rescore_matched_k.prereg.sha256 (sha256sum format, LF, no BOM) = sha256 of this file and
of every local module it imports, frozen BEFORE any real-data run.  Before the freeze the script ran only with
--selftest (synthetic fixture; identity segmenter; reads no manuscript or cipher text; writes only runs/s82/fixture.txt).
Disclosed pre-freeze looks: the s80 Voynich values in runs/s80/values.csv (published; used for the bands below); a
timing probe in the scratchpad that generated one s50 L4 cipher (grid point K=4 beta=1 alpha=1 gamma=0.5) WITHOUT
scoring it, and computed CHARWIN on ZL3b (metrics_new.voynich_pages('eva'): +0.0940, the published n5/m3 value).
A generator smoke test (scratchpad, before the freeze) built one S50 text (grid K=0 b=0 a=0.7 g=0) and one P4D1
text (K1 latin_caesar seed 2) with this file's s50_text / p4_text and printed only page, line and token counts.

DESIGN (fixed before any real-data run)
 Core order (target 1): s80's matched-K pipeline, imported from s80_a14_size_matched (prepare = s80's 166/41-style
   g1 page split + SlotSegmenter fitted on training pages; matched_set; arrays; fit_freq (M-freq); fit_clust (M-clust);
   apply_map).  K in {25, 50, 100, 200, 400} (the curve), both methods.  N_match = 6195 held-out tokens, the value
   s80's N_match rule produced (smallest qualifying held-out set, lang_oldfrench_roland), fixed here so every number
   is on s80's scale.  A text with < 8 held-out pages or < 6195 held-out tokens is UNMATCHED and cannot match.
   Statistic = s80's: within-line adjacent-pair MI minus the mean of 200 within-line shuffles (np.random.default_rng
   (20261017), chunks of 50, keys = line id + uniform, argsort), plug-in and Miller-Madow; PRIMARY = Miller-Madow.
   Interval = s80's (500 draws of round(0.8 x matched pages) without replacement x 20 shuffles, rng 20261018) -
   SECONDARY descriptor only (roach r4 / L-171: the subsample interval is unreliable for shuffle-excess statistics).
   Decision statistic for "is there order" = the exact within-line permutation p from the same 200 shuffles:
   p_up = (1 + #{null MM >= observed MM}) / 201.
   COMPUTE: the uniform keys come from the numpy stream exactly as in s80 (so Voynich reproduces s80); the argsort,
   gathers and the batched MI (all labelings and shuffles of a chunk in one call) run on the GPU with torch (cuda),
   float64; on any GPU error the text is re-run with torch on CPU and that is recorded.  4 worker processes at
   BelowNormal priority (psutil), each single-threaded.
 Matched-K core-order MATCH BANDS (from runs/s80/values.csv, MM, Voynich ZL3b/RF1b/IT2a, SlotSegmenter):
   band = [min over the three transliterations of the s80 95 % lower bound - 2 x hw, max of the upper bound + 2 x hw],
   hw = mean over the three of the s80 interval half-width (hi - lo) / 2 at that (method, K).  Exact bands:
       M-freq  K=50  [+0.0091, +0.1093]   K=100 [-0.0057, +0.1026]   K=200 [-0.0203, +0.1011]
       M-clust K=50  [+0.0035, +0.1240]   K=100 [-0.0041, +0.1078]   K=200 [-0.0275, +0.0978]
   (reported only: K=25 freq [+0.0070, +0.0879] clust [+0.0134, +0.0905]; K=400 freq [-0.0401, +0.0960]
    clust [-0.0455, +0.0925].)  The script recomputes the bands from runs/s80/values.csv and stops if they differ.
   Voynich order decision per (method, K) cell: ORDERED if p_up < 0.05 on >= 2 of the 3 transliterations (this run).
   A text MATCHES the core-order curve iff in all 6 cells (both methods x K 50/100/200) its MM point lies inside the
   band AND its own decision (p_up < 0.05) equals Voynich's decision for that cell.  [CHOICE: both pooling methods are
   required, since s80 measures the curve both ways; the M-freq-only count is printed beside, not gating.]
 Other targets, computed on every text identically (all tokens / lines of the text's pages):
   (2) h2  = a1_profile.char_entropies(tokens)['h2'] (s50's stats), target [2.05, 2.15] (s50 TARGET).
   (3) A5  = s50_solver_ladder.moran_within(lines) (s21 estimator), target [0.1086, 0.1700] (s50 TARGET, s15 range).
   (4) CHARWIN = n5.score's formula: m3.score_folds(pages, m3.page_split(pages, 20261017)), unigram-GT-renorm minus
       char3-WB bits/token; target > 0 (Voynich +0.094).  Scored on the whole text (n5 cut non-manuscript corpora
       to 25k tokens; here every text, Voynich included, is scored whole) [CHOICE].
   (5) f4  = s55's f4_prefix_gain (= s69 M1): s55 TextData split + training SlotSegmenter, Witten-Bell bigram gain on
       the prefix stream, gain_stat over held-out pages; target > 0.05 (Voynich ~ +0.10).
   Voynich ZL3b/RF1b/IT2a values of (2)-(5) are printed as a check on the targets (not gating).
 Families:
   S50  : the s50 L4 construction (letters in the affix pair, null filler cores; s50_solver_ladder.L4Base,
          make_l4_key, gen_l4 imported unchanged) at every point of s50's 81-point grid L4_GRID (K palette x beta x
          alpha x gamma), with s50's calibration plaintext and key (latin = latin_caesar first 100k letters, key seed 0,
          generator seed 0), 38,000 tokens on the cycled ZL3b paragraph line-length sequence (s50 line_lengths).
          Pages for the split: line i takes the page of ZL3b non-empty paragraph line i mod n (vparse records);
          cycled lines (i >= n) go to pseudo-pages '<page>~c<i // n>'.  81 instances.
   P4D1 : P4-D1 K1 letter-in-core and K3 chunk-in-core on the 6 corpora.CONTROLS plaintexts, generator seeds 1, 2, 3,
          regenerated with p4d1_core_order's functions exactly as s80.cipher_texts (seed 1 = s80's texts); each line
          takes the ZL3b paragraph line's page.  36 instances.
   VOY  : Voynich ZL3b, RF1b, IT2a (s55 voynich_pages), SlotSegmenter.
 Reproduction checks (printed, not gating): Voynich MM points vs runs/s80/values.csv; P4D1 seed-1 MM points vs s80's
   CIPHER rows; S50 types / h2 / Moran vs the 81 'L4 calibration' lines of results_s50.txt; Voynich f4 vs s69 M1
   (+0.0999 / +0.0951 / +0.0961).
   Device check: for VOY and fixture texts the 200-shuffle point excess is recomputed with s80's own numpy Scorer on
   the same labelings and stream; max |diff| printed per text.

PRE-REGISTERED CALLS (per family; MM primary)
 C1: count of instances that MATCH the core-order curve (S50: of 81 grid points; P4D1: of 36 instances).
 C2: count of instances that meet all five targets jointly (curve match, h2, A5, CHARWIN > 0, f4 > 0.05).
 Reading per family (exactly one):
   C2 >= 1            -> "family reproduces the manuscript's measured profile; candidate for a solver run"
   C1 >= 1 and C2 = 0 -> "core order reachable, joint profile not" (failing targets named: for each of targets 2-5
                          the number of curve-matching instances that miss it)
   C1 = 0             -> "family cannot produce the weak core order"

FIXTURE (--selftest; synthetic, identity segmenter = the word IS the core; reads no real data; the order decision is
  set to ORDERED in all 6 cells, as s80's C1 interval suggests, because the real Voynich p values are not looked at):
  construction: 40 latent classes x 60 cores (within-class Zipf 1.0), class chain P(next = fixed successor) = q, else
  uniform, 207 pages x 20 lines x Poisson(8) words (s80's F_order generator with q free).  q is chosen from
  {0.20, 0.25, 0.30, 0.35, 0.40, 0.45} on construction seeds 101-103 by the smallest max |mean MM - band centre| /
  band half-width over the 6 cells (mean over the 3 seeds; 200 shuffles, no interval); a fresh text at that q (seed
  202) = FX_match;
  FX_strong = q 0.6 (s80's F_order); FX_none = q 0 (reported).
  Checks: FXA FX_match is called MATCH; FXB FX_strong is called NO MATCH.  FIXTURE PASS iff both.
  Fixture history before the freeze (runs/s82/fixture.txt is overwritten by each pass): pass 1 used q in
  {0.04 .. 0.20} and one construction seed; it chose q 0.20, whose fresh-seed text read +0.015 at freq K=100 vs
  +0.049 on the construction seed (seed noise at weak order), and FXA FAILED (freq K=50 below band); FXB passed.
  Only the fixture's construction grid and seeds were changed (to the above); no real-data rule was changed.
Constraints: python -I; writes ONLY results_s82.txt and runs/s82/ (fixture: only runs/s82/fixture.txt).  Wall 90 min.
AMENDMENT 1 (after run 1): run 1 crashed writing runs/s82/calls.json (numpy int64 not JSON serializable) after every
measurement, table and the VERDICT line had been printed (log kept: runs/s82/run1-crashed.log, results_run1-crashed.txt).
Only the json.dumps call gained a default= converter; no statistic, rule or band changed; the full run is repeated.
Run: python -I s82_cipher_rescore_matched_k.py     Fixture: --selftest      Stub helper: --list-locals
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
import sys
import time
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import a1_profile  # noqa: E402
import m3_bakeoff_reconcile as m3  # noqa: E402
import s50_solver_ladder as L50  # noqa: E402
import s55_code_vs_generator as S55  # noqa: E402
import s80_a14_size_matched as S80  # noqa: E402
import vparse  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

P4 = S80.P4
SELF = ROOT / "s82_cipher_rescore_matched_k.py"
STUB = ROOT / "s82_cipher_rescore_matched_k.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s82"
SEED = 20261017
FIXTURE = "--selftest" in sys.argv
LIST_LOCALS = "--list-locals" in sys.argv
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / "results_s82.txt"
WALL = 90 * 60
KS = [25, 50, 100, 200, 400]
METHODS = ["freq", "clust"]
MATCH_KS = [50, 100, 200]
N_SHUF, N_DRAW, N_DRAW_SHUF, SUB_FRAC = 200, 500, 20, 0.8
N_MATCH = 6195
QUAL_PAGES = 8
WORKERS = 4
ALPHA = 0.05
BANDS = {("freq", 50): (0.0091, 0.1093), ("freq", 100): (-0.0057, 0.1026), ("freq", 200): (-0.0203, 0.1011),
         ("clust", 50): (0.0035, 0.1240), ("clust", 100): (-0.0041, 0.1078), ("clust", 200): (-0.0275, 0.0978),
         ("freq", 25): (0.0070, 0.0879), ("clust", 25): (0.0134, 0.0905),
         ("freq", 400): (-0.0401, 0.0960), ("clust", 400): (-0.0455, 0.0925)}
H2_T = (2.05, 2.15)
A5_T = L50.TARGET["moran"]
F4_MIN = 0.05
S69_F4 = {"ZL3b": 0.0999, "RF1b": 0.0951, "IT2a": 0.0961}
FX_QS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45]
FX_CONS_SEEDS = (101, 102, 103)
LN2 = math.log(2.0)
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


def set_low_priority():
    try:
        import psutil
        p = psutil.Process()
        if sys.platform == "win32":
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            p.nice(10)
        return "BelowNormal (psutil)"
    except Exception as e:  # noqa: BLE001
        return f"priority not set ({e})"


# ======================================================================= torch MI machinery
_TORCH = {}


def torch_dev(prefer="cuda"):
    import torch
    torch.set_num_threads(1)
    if prefer == "cuda" and torch.cuda.is_available():
        return torch, torch.device("cuda")
    return torch, torch.device("cpu")


def mi_rows(torch, A, B, K):
    """A, B: (R, n) long tensors of labels in [0, K).  -> (plug (R,), mm (R,)) float64 tensors, bits."""
    R, n = A.shape
    dev = A.device
    off = torch.arange(R, device=dev, dtype=torch.int64)[:, None]

    def ent_marg(X):
        c = torch.bincount((off * K + X).reshape(-1), minlength=R * K).view(R, K).to(torch.float64)
        m = (c > 0).sum(1)
        cl = torch.xlogy(c, c).sum(1) / LN2
        return math.log2(n) - cl / n, m
    ha, ma = ent_marg(A)
    hb, mb = ent_marg(B)
    codes = (off * (K * K) + A * K + B).reshape(-1)
    u, cnt = torch.unique(codes, return_counts=True)
    row = u // (K * K)
    cntf = cnt.to(torch.float64)
    cl = torch.zeros(R, dtype=torch.float64, device=dev).index_add_(0, row, torch.xlogy(cntf, cntf) / LN2)
    mj = torch.bincount(row, minlength=R)
    hj = math.log2(n) - cl / n
    plug = ha + hb - hj
    mm = plug + ((ma - 1) + (mb - 1) - (mj - 1)).to(torch.float64) / (2.0 * n * LN2)
    return plug, mm


def excess_t(torch, dev, labs_np, lid, n_shuf, rng, chunk=50):
    """s80 Scorer.excess with the same numpy key stream, MI on `dev`.  labs_np: list of int arrays (len n).
    -> list of dict(plug, mm, p_plug, p_mm)."""
    lid = np.asarray(lid, dtype=np.int64)
    same = lid[1:] == lid[:-1]
    left = np.nonzero(same)[0]
    if len(left) < 2:
        return [dict(plug=float("nan"), mm=float("nan"), p_plug=float("nan"), p_mm=float("nan"))] * len(labs_np)
    right = left + 1
    X = torch.as_tensor(np.stack(labs_np), dtype=torch.int64, device=dev)          # (L, n)
    Kmax = int(X.max().item()) + 1
    L = X.shape[0]
    lt = torch.as_tensor(left, device=dev); rt = torch.as_tensor(right, device=dev)
    op, om = mi_rows(torch, X[:, lt], X[:, rt], Kmax)
    lidf = torch.as_tensor(lid.astype(float), device=dev)
    nul_p, nul_m = [], []
    done = 0
    while done < n_shuf:
        S = min(chunk, n_shuf - done)
        keys = torch.as_tensor(rng.random((S, len(lid))), device=dev) + lidf[None, :]
        P = torch.argsort(keys, dim=1)                                               # (S, n)
        Xp = X[:, P]                                                                 # (L, S, n)
        A = Xp[:, :, lt].reshape(L * S, -1); B = Xp[:, :, rt].reshape(L * S, -1)
        p, m = mi_rows(torch, A, B, Kmax)
        nul_p.append(p.view(L, S)); nul_m.append(m.view(L, S))
        done += S
    NP = torch.cat(nul_p, 1); NM = torch.cat(nul_m, 1)
    ex_p = (op - NP.mean(1)).cpu().numpy(); ex_m = (om - NM.mean(1)).cpu().numpy()
    pp = ((1 + (NP >= op[:, None] - 1e-12).sum(1)).to(torch.float64) / (n_shuf + 1)).cpu().numpy()
    pm = ((1 + (NM >= om[:, None] - 1e-12).sum(1)).to(torch.float64) / (n_shuf + 1)).cpu().numpy()
    return [dict(plug=float(ex_p[i]), mm=float(ex_m[i]), p_plug=float(pp[i]), p_mm=float(pm[i])) for i in range(L)]


def measure_core(T, n_match, prefer, n_shuf=N_SHUF, n_draw=N_DRAW, n_draw_shuf=N_DRAW_SHUF, check_cpu=False):
    """s80.measure restricted to KS, MI on torch; adds the permutation p."""
    torch, dev = torch_dev(prefer)
    mset = S80.matched_set(T, n_match)
    cores, lid, pg = S80.arrays(mset)
    labs, keys, ncls = [], [], {}
    cache = {}
    for meth in METHODS:
        for K in KS:
            mp = S80.fit_freq(T["tr_counts"], K) if meth == "freq" else S80.fit_clust(T["tr_lines"], T["tr_counts"], K, cache)
            x = S80.apply_map(cores, mp)
            keys.append((meth, K)); labs.append(x); ncls[(meth, K)] = int(x.max()) + 1
    pt = excess_t(torch, dev, labs, lid, n_shuf, np.random.default_rng(SEED))
    cpu_check = None
    if check_cpu:   # s80's own numpy Scorer on the same labelings and stream: device result must agree
        ref = S80.Scorer(lid).excess(labs, n_shuf, np.random.default_rng(SEED))
        cpu_check = max(max(abs(a["plug"] - b[0]), abs(a["mm"] - b[1])) for a, b in zip(pt, ref))
    rng = np.random.default_rng(SEED + 1)
    npg = len(mset); m = int(round(SUB_FRAC * npg))
    draws = [[] for _ in labs]
    page_idx = [np.nonzero(pg == i)[0] for i in range(npg)]
    for _ in range(n_draw):
        sel = np.sort(rng.choice(npg, size=m, replace=False))
        idx = np.concatenate([page_idx[i] for i in sel])
        r = excess_t(torch, dev, [x[idx] for x in labs], lid[idx], n_draw_shuf, rng)
        for i, v in enumerate(r):
            draws[i].append((v["plug"], v["mm"]))
    res = OrderedDict()
    for i, k in enumerate(keys):
        d = dict(ncls=ncls[k], **pt[i])
        if n_draw:
            D = np.array(draws[i])
            d["plug_ci"] = (float(np.nanpercentile(D[:, 0], 2.5)), float(np.nanpercentile(D[:, 0], 97.5)))
            d["mm_ci"] = (float(np.nanpercentile(D[:, 1], 2.5)), float(np.nanpercentile(D[:, 1], 97.5)))
        else:
            d["plug_ci"] = d["mm_ci"] = (float("nan"), float("nan"))
        res[k] = d
    info = dict(tokens=len(cores), pages=npg, pairs=int((lid[1:] == lid[:-1]).sum()), core_types=len(set(cores)),
                device=str(dev), cpu_check=cpu_check)
    return res, info


# ======================================================================= the other four targets
def other_targets(pages):
    """pages: list of (id, lines).  -> dict(h2, moran, charwin, f4, types, tokens)."""
    lines = [[w for w in ln if w] for _, ls in pages for ln in ls]
    lines = [ln for ln in lines if ln]
    toks = [w for ln in lines for w in ln]
    pd = [dict(id=str(pid), lines=[x for x in ([w for w in ln if w] for ln in ls) if x]) for pid, ls in pages]
    pd = [p for p in pd if p["lines"]]
    acc = m3.score_folds(pd, m3.page_split(pd, SEED))
    rn, wb = acc["unigram-GT-renorm"], acc["char3-WB"]
    charwin = rn["bits"] / rn["tok"] - wb["bits"] / wb["tok"]
    td = S55.TextData("t", pd)
    f4 = S55.gain_stat(np.array(list(S55.gain_pages(td.tr_pre_lines, td.te_pre_pl).values())))
    return dict(h2=a1_profile.char_entropies(toks)["h2"], moran=L50.moran_within(lines), charwin=charwin, f4=f4,
                types=len(set(toks)), tokens=len(toks))


# ======================================================================= text generators (worker side, cached)
_CACHE = {}


def p4_setup():
    if "p4" not in _CACHE:
        zpath = dict(P4.s34.TRANSLITS)["ZL3b"]
        recs = vparse.paragraph_text(vparse.load(path=zpath))
        zl_lines = P4.voynich_lines(zpath)
        assert len(recs) == len(zl_lines)
        zl_tokens = [w for _, ln in zl_lines for w in ln]
        zseg = P4.mn.SlotSegmenter(zl_tokens)
        trip = [zseg.segment(w) for w in zl_tokens]
        aff = Counter((p, s) for p, _, s in trip)
        _CACHE["p4"] = dict(line_page=[r["page"] for r in recs], core_freq=Counter(c for _, c, _ in trip),
                            affix_pairs=list(aff), affix_w=list(aff.values()),
                            line_lens=[len(ln) for _, ln in zl_lines])
    return _CACHE["p4"]


def p4_text(fam, name, seed):
    """s80.cipher_texts with the generator seed free (seed 1 = s80)."""
    z = p4_setup()
    n_target = sum(z["line_lens"])
    words = P4.corpora.control(name)
    letters = [ch for w in words for ch in w]
    rng = random.Random(seed)
    units = letters[:n_target] if fam == "K1" else P4.chunks(letters[:2 * n_target], rng)[:n_target]
    table = P4.assign(Counter(units), z["core_freq"])
    lines, _oracle = P4.plant(units, table, z["affix_pairs"], z["affix_w"], z["line_lens"], rng)
    pages = OrderedDict()
    for i, ln in enumerate(lines):
        pages.setdefault(z["line_page"][i], []).append(ln)
    return list(pages.items())


def s50_setup():
    if "s50" not in _CACHE:
        vlines, vtoks = L50.voynich()
        lens = L50.line_lengths(vlines)
        recs = vparse.paragraph_text(vparse.load(path=vparse.DATA))
        vl = P4.voynich_lines(vparse.DATA)
        assert len(recs) == len(vl)
        page_ne = [r["page"] for r, (_, ln) in zip(recs, vl) if ln]
        assert len(page_ne) == len(vlines)
        plain, _lmt = L50.lang_texts("latin")
        base = L50.L4Base(vtoks)
        key = L50.make_l4_key(plain, base, 0)
        _CACHE["s50"] = dict(lens=lens, page_ne=page_ne, plain=plain, base=base, key=key)
    return _CACHE["s50"]


def s50_text(prm):
    z = s50_setup()
    lines, _truth = L50.gen_l4(z["plain"], z["key"], z["base"], prm, 0, z["lens"])
    n = len(z["page_ne"])
    pages = OrderedDict()
    for i, ln in enumerate(lines):
        pid = z["page_ne"][i % n] + ("" if i < n else f"~c{i // n}")
        pages.setdefault(pid, []).append(ln)
    return list(pages.items())


# ======================================================================= fixture generator
def fx_text(q, seed):
    rng = np.random.default_rng(seed)
    n_cls, per = 40, 60
    succ = rng.permutation(n_cls); wz = S80.zipf_w(per)
    st = {"c": int(rng.integers(n_cls))}

    def nxt():
        c = st["c"]
        st["c"] = int(succ[c]) if rng.random() < q else int(rng.integers(n_cls))
        return f"c{c}_{int(rng.choice(per, p=wz))}"
    return S80.fx_pages(nxt, rng)


# ======================================================================= worker
def worker_init():
    set_low_priority()
    try:
        from threadpoolctl import threadpool_limits
        _CACHE["tpl"] = threadpool_limits(1)
    except ImportError:
        pass


def job(spec):
    t = time.time()
    kind = spec[0]
    if kind == "VOY":
        pages = S80.voy_pages(spec[1]); seg = SlotSegmenter
    elif kind == "P4D1":
        pages = p4_text(spec[1], spec[2], spec[3]); seg = SlotSegmenter
    elif kind == "S50":
        pages = s50_text(spec[1]); seg = SlotSegmenter
    elif kind == "FX":
        pages = fx_text(spec[1], spec[2]); seg = S80.identity_seg_factory
    else:
        raise ValueError(kind)
    name = spec_name(spec)
    T = S80.prepare(name, kind, pages, seg)
    qual = T["n_te"] >= QUAL_PAGES and T["te_tok"] >= N_MATCH
    nd = spec[3] if kind == "FX" else N_DRAW
    fallback = ""
    try:
        res, info = measure_core(T, N_MATCH if qual else None, "cuda", n_draw=nd, check_cpu=kind in ("VOY", "FX"))
    except Exception as e:  # noqa: BLE001
        fallback = f"GPU error ({type(e).__name__}: {e}); re-run on torch CPU"
        res, info = measure_core(T, N_MATCH if qual else None, "cpu", n_draw=nd, check_cpu=kind in ("VOY", "FX"))
    info.update(qualified=qual, n_tr=T["n_tr"], n_te=T["n_te"], te_tok=T["te_tok"], fallback=fallback)
    other = other_targets(pages)
    info["secs"] = time.time() - t
    return dict(spec=list(spec), name=name, res=res, info=info, other=other)


def spec_name(spec):
    if spec[0] == "VOY":
        return f"VOY_{spec[1]}"
    if spec[0] == "P4D1":
        return f"{spec[1]}_{spec[2]}_s{spec[3]}"
    if spec[0] == "S50":
        K, b, a, g = spec[1]
        return f"L4_K{K}_b{b:g}_a{a:g}_g{g:g}"
    return f"FX_q{spec[1]:g}_seed{spec[2]}"


def run_jobs(specs):
    from concurrent.futures import ProcessPoolExecutor
    out = []
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=worker_init) as ex:
        for r in ex.map(job, specs):
            out.append(r)
            cc = r["info"].get("cpu_check")
            emit(f"  done {r['name']:34s} [{r['info']['secs']:.0f}s, {r['info']['device']}]{'' if cc is None else f' device-vs-s80-numpy max |diff| {cc:.1e}'}{(' ' + r['info']['fallback']) if r['info']['fallback'] else ''}")
            flush()
    return out


# ======================================================================= matching
def core_match(r, voy_sig, ks=MATCH_KS, methods=METHODS):
    if not r["info"]["qualified"]:
        return False, ["UNMATCHED"]
    miss = []
    for meth in methods:
        for K in ks:
            v = r["res"][(meth, K)]
            lo, hi = BANDS[(meth, K)]
            if not (lo <= v["mm"] <= hi):
                miss.append(f"{meth}{K}:band")
            elif (v["p_mm"] < ALPHA) != voy_sig[(meth, K)]:
                miss.append(f"{meth}{K}:p")
    return not miss, miss


def target_hits(r, cm):
    o = r["other"]
    return OrderedDict(curve=cm, h2=H2_T[0] <= o["h2"] <= H2_T[1], A5=A5_T[0] <= o["moran"] <= A5_T[1],
                       CHARWIN=o["charwin"] > 0, f4=o["f4"] > F4_MIN)


def check_bands():
    R = [r for r in csv.DictReader((ROOT / "runs" / "s80" / "values.csv").open(encoding="utf-8")) if r["group"] == "VOY"]
    bad = []
    for (meth, K), (blo, bhi) in BANDS.items():
        rs = [r for r in R if r["method"] == meth and r["K"] == str(K)]
        lo = min(float(r["mm_lo"]) for r in rs); hi = max(float(r["mm_hi"]) for r in rs)
        hw = sum((float(r["mm_hi"]) - float(r["mm_lo"])) / 2 for r in rs) / len(rs)
        if abs(round(lo - 2 * hw, 4) - blo) > 1e-9 or abs(round(hi + 2 * hw, 4) - bhi) > 1e-9:
            bad.append(f"{meth} K={K}: s80 gives [{lo - 2 * hw:+.4f}, {hi + 2 * hw:+.4f}] vs frozen [{blo:+.4f}, {bhi:+.4f}]")
    return bad


def s80_values():
    out = {}
    for r in csv.DictReader((ROOT / "runs" / "s80" / "values.csv").open(encoding="utf-8")):
        out[(r["text"], r["method"], r["K"])] = float(r["mm"])
    return out


def s50_calibration():
    out = {}
    pat = re.compile(r"L4 calibration K=(\d+)\s+beta=([\d.]+)\s+alpha=([\d.]+)\s+gamma=([\d.]+):\s+types (\d+)\*?\s+hapax [\d.]+\*?\s+"
                     r"h2 ([\d.]+)\*?\s+A14 [-+\d.]+\*?\s+Moran ([-+\d.]+)")
    for ln in (ROOT / "results_s50.txt").read_text(encoding="utf-8").splitlines():
        m = pat.search(ln)
        if m:
            k = (int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
            out[k] = (int(m.group(5)), float(m.group(6)), float(m.group(7)))
    return out


def curve_str(r, meth):
    return " ".join(f"{r['res'][(meth, K)]['mm']:+.3f}" for K in KS)


def device_line():
    try:
        torch, dev = torch_dev("cuda")
        nm = torch.cuda.get_device_name(0) if dev.type == "cuda" else "-"
        return f"torch {torch.__version__}; device {dev} ({nm})"
    except Exception as e:  # noqa: BLE001
        return f"torch device query failed ({e})"


# ======================================================================= fixture
def run_fixture():
    emit("S82 FIXTURE (synthetic only; identity segmenter; no manuscript or cipher text read)")
    emit(f"date: {S80.clock()}")
    emit(f"s82 sha256={sha256(SELF)}  stub_match={stub_match()}")
    emit(f"{device_line()}; workers {WORKERS}; priority {set_low_priority()}")
    bad = check_bands()
    emit(f"bands vs runs/s80/values.csv: {'OK' if not bad else 'DIFFER: ' + '; '.join(bad)}")
    voy_sig = {(m, K): True for m in METHODS for K in KS}
    emit(f"construction: choose q on seeds {FX_CONS_SEEDS} (points only, no interval)")
    cons = run_jobs([("FX", q, sd, 0) for q in FX_QS for sd in FX_CONS_SEEDS])
    best = None
    for qi, q in enumerate(FX_QS):
        rr = cons[qi * len(FX_CONS_SEEDS):(qi + 1) * len(FX_CONS_SEEDS)]
        mean = {(m, K): float(np.mean([r["res"][(m, K)]["mm"] for r in rr])) for m in METHODS for K in KS}
        d = max(abs(mean[(m, K)] - sum(BANDS[(m, K)]) / 2) / ((BANDS[(m, K)][1] - BANDS[(m, K)][0]) / 2)
                for m in METHODS for K in MATCH_KS)
        emit(f"  q={q:<5} mean freq " + " ".join(f"{mean[('freq', K)]:+.3f}" for K in KS) + " | clust "
             + " ".join(f"{mean[('clust', K)]:+.3f}" for K in KS) + f" | max norm dist {d:.2f}")
        if best is None or d < best[0]:
            best = (d, q)
    q = best[1]
    emit(f"chosen q = {q}")
    # spec for FX: ("FX", q, seed, n_draw) -- n_draw passed through spec[3]
    specs = [("FX", q, 202, N_DRAW), ("FX", 0.6, 203, N_DRAW), ("FX", 0.0, 204, N_DRAW)]
    rs = run_jobs(specs)
    calls = {}
    for lab, r in zip(("FX_match", "FX_strong", "FX_none"), rs):
        cm, miss = core_match(r, voy_sig)
        calls[lab] = cm
        emit(f"\n  {lab} ({r['name']}): matched tokens {r['info']['tokens']} pairs {r['info']['pairs']} types {r['info']['core_types']}")
        for meth in METHODS:
            for K in KS:
                v = r["res"][(meth, K)]
                emit(f"    {meth:5s} K={K:<3d} cls {v['ncls']:>4d} MM {v['mm']:+.4f} [{v['mm_ci'][0]:+.4f},{v['mm_ci'][1]:+.4f}] p {v['p_mm']:.3f}"
                     f" | plug {v['plug']:+.4f} p {v['p_plug']:.3f} | band {BANDS[(meth, K)][0]:+.4f},{BANDS[(meth, K)][1]:+.4f}")
        emit(f"    -> {'MATCH' if cm else 'NO MATCH'} {miss if miss else ''}")
        o = r["other"]
        emit(f"    other targets (code-path check only): h2 {o['h2']:.3f} A5 {o['moran']:+.4f} CHARWIN {o['charwin']:+.4f} f4 {o['f4']:+.4f}")
    fxa, fxb = calls["FX_match"], not calls["FX_strong"]
    emit("")
    emit(f"FXA FX_match called MATCH: {'PASS' if fxa else 'FAIL'}")
    emit(f"FXB FX_strong called NO MATCH: {'PASS' if fxb else 'FAIL'}")
    emit(f"(reported) FX_none: {'MATCH' if calls['FX_none'] else 'NO MATCH'}")
    emit(f"FIXTURE {'PASS' if fxa and fxb else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {S80.clock()}")
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
    prio = set_low_priority()
    emit("S82: s50 and P4-D1 cipher families vs the matched-K core-order profile (pre-registered in the docstring)")
    emit(f"date: {S80.clock()}")
    emit(f"s82_cipher_rescore_matched_k.py sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"compute: {device_line()}; {WORKERS} worker processes, priority {prio}; uniform keys from numpy (s80 stream), "
         f"argsort + MI on the device; python {sys.version.split()[0]}; numpy {np.__version__}")
    emit(f"N_match {N_MATCH}; shuffles {N_SHUF}; interval {N_DRAW} x {int(SUB_FRAC * 100)} % pages x {N_DRAW_SHUF} shuffles (secondary)")
    bad = check_bands()
    emit(f"bands vs runs/s80/values.csv: {'OK' if not bad else 'DIFFER: ' + '; '.join(bad)}")
    if bad:
        emit("STOP: frozen bands differ from s80"); flush(); return
    emit("\n=== MATCH BANDS (MM excess; gating cells K 50/100/200, both methods) ===")
    for meth in METHODS:
        emit(f"  M-{meth:5s} " + "  ".join(f"K={K}: [{BANDS[(meth, K)][0]:+.4f}, {BANDS[(meth, K)][1]:+.4f}]{'' if K in MATCH_KS else '(rep)'}" for K in KS))
    flush()

    specs = [("VOY", T) for T in ("ZL3b", "RF1b", "IT2a")]
    specs += [("P4D1", fam, name, s) for name in P4.corpora.CONTROLS for fam in ("K1", "K3") for s in (1, 2, 3)]
    specs += [("S50", prm) for prm in L50.L4_GRID]
    emit(f"\n=== running {len(specs)} texts (VOY 3, P4D1 {sum(1 for s in specs if s[0] == 'P4D1')}, S50 {sum(1 for s in specs if s[0] == 'S50')}) start {S80.clock()} ===")
    flush()
    outs = run_jobs(specs)
    emit(f"  measured in {time.time() - T0:.0f}s")
    if time.time() - T0 > WALL:
        emit(f"WALL LIMIT {WALL}s exceeded (reported; results kept)")
    R = OrderedDict((r["name"], r) for r in outs)
    fb = [n for n, r in R.items() if r["info"]["fallback"]]
    emit(f"  devices used: {Counter(r['info']['device'] for r in outs)}; GPU fallbacks: {len(fb)} {fb if fb else ''}")

    # ---- sidecars
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "values.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "family", "qualified", "method", "K", "classes", "mm", "mm_lo", "mm_hi", "p_mm", "plug",
                    "plug_lo", "plug_hi", "p_plug", "tokens", "pairs", "core_types", "device"])
        for n, r in R.items():
            for (meth, K), v in r["res"].items():
                w.writerow([n, r["spec"][0], r["info"]["qualified"], meth, K, v["ncls"]] +
                           [f"{x:.6f}" for x in (v["mm"], *v["mm_ci"], v["p_mm"], v["plug"], *v["plug_ci"], v["p_plug"])] +
                           [r["info"]["tokens"], r["info"]["pairs"], r["info"]["core_types"], r["info"]["device"]])
    with (RUN_DIR / "targets.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "family", "tokens", "types", "h2", "moran", "charwin", "f4"])
        for n, r in R.items():
            o = r["other"]
            w.writerow([n, r["spec"][0], o["tokens"], o["types"]] + [f"{o[k]:.6f}" for k in ("h2", "moran", "charwin", "f4")])

    # ---- reproduction checks
    emit("\n=== reproduction checks (not gating) ===")
    s80v = s80_values()
    for T in ("ZL3b", "RF1b", "IT2a"):
        r = R[f"VOY_{T}"]
        d = max(abs(r["res"][(m, K)]["mm"] - s80v[(f"VOY_{T}", m, str(K))]) for m in METHODS for K in KS)
        emit(f"  VOY_{T} MM points vs s80 values.csv: max |diff| {d:.2e} -> {'MATCH' if d < 1e-6 else 'DIFFERS'}")
    ds = []
    for name in P4.corpora.CONTROLS:
        for fam in ("K1", "K3"):
            r = R[f"{fam}_{name}_s1"]
            ds.append(max(abs(r["res"][(m, K)]["mm"] - s80v[(f"{fam}_{name}", m, str(K))]) for m in METHODS for K in KS))
    emit(f"  P4D1 seed-1 ciphers MM vs s80 CIPHER rows: max |diff| {max(ds):.2e} over 12 -> {'MATCH' if max(ds) < 1e-6 else 'DIFFERS'}")
    cal = s50_calibration()
    nok, worst = 0, []
    for prm in L50.L4_GRID:
        r = R[spec_name(("S50", prm))]
        c = cal.get(prm)
        if c and c[0] == r["other"]["types"] and abs(c[1] - r["other"]["h2"]) < 6e-4 and abs(c[2] - r["other"]["moran"]) < 6e-5:
            nok += 1
        else:
            worst.append(f"{prm}: s50 {c} vs {r['other']['types']} {r['other']['h2']:.3f} {r['other']['moran']:+.4f}")
    emit(f"  S50 grid types/h2/Moran vs results_s50.txt calibration lines: {nok}/{len(L50.L4_GRID)} match"
         + ("" if not worst else f"; first differences: {worst[:3]}"))
    for T in ("ZL3b", "RF1b", "IT2a"):
        emit(f"  VOY_{T} f4 {R['VOY_' + T]['other']['f4']:+.4f} vs s69 M1 {S69_F4[T]:+.4f}")
    flush()

    # ---- Voynich
    emit("\n=== Voynich (MM excess [s80-style 95 % interval, secondary] p_up; plug-in beside) ===")
    for T in ("ZL3b", "RF1b", "IT2a"):
        r = R[f"VOY_{T}"]; i = r["info"]
        emit(f"  VOY_{T}: matched tokens {i['tokens']} pages {i['pages']} pairs {i['pairs']} core types {i['core_types']}")
        for meth in METHODS:
            emit(f"    M-{meth:5s} " + " ".join(f"K{K}:{r['res'][(meth, K)]['mm']:+.4f}[{r['res'][(meth, K)]['mm_ci'][0]:+.3f},{r['res'][(meth, K)]['mm_ci'][1]:+.3f}]p{r['res'][(meth, K)]['p_mm']:.3f}" for K in KS))
        o = r["other"]
        emit(f"    h2 {o['h2']:.3f}  A5 Moran {o['moran']:+.4f}  CHARWIN {o['charwin']:+.4f}  f4 {o['f4']:+.4f}  (tokens {o['tokens']}, types {o['types']})")
    voy_sig = {}
    for meth in METHODS:
        for K in KS:
            n_sig = sum(R[f"VOY_{T}"]["res"][(meth, K)]["p_mm"] < ALPHA for T in ("ZL3b", "RF1b", "IT2a"))
            voy_sig[(meth, K)] = n_sig >= 2
    emit("  Voynich order decision (p_up < 0.05 on >= 2 of 3): " +
         "; ".join(f"{m}{K} {'ORDERED' if voy_sig[(m, K)] else 'not ordered'}" for m in METHODS for K in KS))
    for T in ("ZL3b", "RF1b", "IT2a"):
        r = R[f"VOY_{T}"]
        cm, miss = core_match(r, voy_sig)
        th = target_hits(r, cm)
        emit(f"  self-check VOY_{T} against the targets: " + " ".join(f"{k}={'Y' if v else 'n'}" for k, v in th.items())
             + (f"  (curve misses {miss})" if miss else ""))
    flush()

    # ---- families
    calls = OrderedDict()
    for fam in ("P4D1", "S50"):
        names = [n for n, r in R.items() if r["spec"][0] == fam]
        emit(f"\n=== family {fam}: {len(names)} instances ===")
        emit(f"  {'text':30s} {'M-freq MM K25..400':38s} {'M-clust MM K25..400':38s} pmax  curve  h2     A5      CHARWIN  f4      hits")
        rows = []
        for n in names:
            r = R[n]
            cm, miss = core_match(r, voy_sig)
            cmf, _ = core_match(r, voy_sig, methods=["freq"])
            th = target_hits(r, cm)
            o = r["other"]
            pmax = max(r["res"][(m, K)]["p_mm"] for m in METHODS for K in MATCH_KS)
            rows.append(dict(name=n, cm=cm, cmf=cmf, miss=miss, th=th))
            emit(f"  {n:30s} {curve_str(r, 'freq'):38s} {curve_str(r, 'clust'):38s} {pmax:.3f} {'MATCH' if cm else '-':5s}  "
                 f"{o['h2']:.3f}{'' if th['h2'] else '*'} {o['moran']:+.4f}{'' if th['A5'] else '*'} {o['charwin']:+.4f}{'' if th['CHARWIN'] else '*'} "
                 f"{o['f4']:+.4f}{'' if th['f4'] else '*'}  {sum(th.values())}/5" + (f"  [{', '.join(miss)}]" if miss and not cm else ""))
        c1 = sum(x["cm"] for x in rows)
        c2 = sum(all(x["th"].values()) for x in rows)
        c1f = sum(x["cmf"] for x in rows)
        per_t = {k: sum(x["th"][k] for x in rows) for k in ("curve", "h2", "A5", "CHARWIN", "f4")}
        fail_among = {k: sum(1 for x in rows if x["cm"] and not x["th"][k]) for k in ("h2", "A5", "CHARWIN", "f4")}
        best4 = max((sum(x["th"].values()), x["name"]) for x in rows)
        if c2 >= 1:
            reading = "family reproduces the manuscript's measured profile; candidate for a solver run"
        elif c1 >= 1:
            failing = ", ".join(f"{k} (missed by {v}/{c1})" for k, v in fail_among.items() if v)
            reading = f"core order reachable, joint profile not (failing targets among curve matches: {failing})"
        else:
            reading = "family cannot produce the weak core order"
        cell_fail = Counter(m for x in rows for m in x["miss"])
        emit(f"  instances hitting each target: {per_t}")
        emit(f"  curve-cell misses (band / p-decision) over all instances: {dict(sorted(cell_fail.items()))}")
        emit(f"  C1 ({fam}) curve matches: {c1} of {len(rows)}   (M-freq only, reported: {c1f})")
        emit(f"  C2 ({fam}) joint five-target matches: {c2} of {len(rows)}   (best instance {best4[1]} hits {best4[0]}/5)")
        emit(f"  among curve matches, misses per target: {fail_among}")
        emit(f"  READING ({fam}): {reading}")
        calls[fam] = dict(n=len(rows), C1=c1, C2=c2, C1_freq_only=c1f, per_target=per_t, fail_among_curve_matches=fail_among,
                          matches=[x["name"] for x in rows if x["cm"]], joint=[x["name"] for x in rows if all(x["th"].values())],
                          reading=reading)
        flush()
    emit("")
    emit(f"VERDICT: P4D1 (letter-in-core, 36): {calls['P4D1']['reading']} | S50 (verbose-homophonic, 81 grid points): {calls['S50']['reading']}")
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(n_match=N_MATCH, bands={f"{m}|{K}": v for (m, K), v in BANDS.items()},
                                                        voy_sig={f"{m}|{K}": v for (m, K), v in voy_sig.items()}, calls=calls),
                                                   indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)),
                                        encoding="utf-8", newline="\n")   # AMENDMENT 1: numpy int64 in calls (run 1 crash)
    emit("sidecars: runs/s82/values.csv, runs/s82/targets.csv, runs/s82/calls.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S80.clock()}")
    flush()


if __name__ == "__main__":
    main()
