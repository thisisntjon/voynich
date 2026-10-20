"""s83 -- a homophonic letter/syllable/chunk-in-core cipher with a per-line sticky affix table (HLT), judged on the
s67 15-quire leave-one-quire-out (LOQO) battery, the s69 prefix-memory calls, s80's matched-K core-order curve and R(1).

PRE-REGISTRATION: s83_homophonic_line_table_loqo.prereg.sha256 (sha256sum format, LF, no BOM) = sha256 of this file and
of every local module it imports, frozen BEFORE any real-manuscript scoring.  Before the freeze the script ran only with
--synth (the fixture below).  DISCLOSED: the fixture builds its synthetic 'manuscript' from an HLT construction whose
core inventory, core classes and affix tables are taken from ALL ZL3b pages (the construction needs real cores and
affixes to be realistic); the fixture computes no statistic of the real manuscript and scores nothing against it.
The script re-hashes itself and its local imports and prints stub_match.

WHY (D-060): measured facts any construction must meet: prefix+core+suffix with affixes chosen by the core (F-15); a
prefix stream with one-word memory that resets at each line (F-14; s69 M1 ~ +0.10 and its calls); within-line
word-length rhythm (A5 Moran ~0.157); CHARWIN positive; WEAK core order at matched inventory size (s80); short-range
core recurrence (R(1) ~ 1.17, s56); quire-local vocabulary.  Plaintext-carrying families now live: letter-in-core
ciphers (reopened by s80) and a per-line sticky affix table (s71).  HLT is the combination.

CONSTRUCTION HLT (all parts fitted on the TRAINING quires of each fold only)
  Segmenter: scoreboard/metrics_new.SlotSegmenter on the training tokens; word -> (prefix, core, suffix).
  Core classes: s67.core_classes verbatim (K = 12 + back-off class 12).
  Plaintext (2): 'latin'   = runs/s49/lang_latin_cremma.meta.json (the CREMMA Latin s71 used), words in file order;
                 'italian' = data/controls/italian_dante.txt via corpora.control (first 60,000 words).
                 Letters: s64.norm_letters per word (23-letter period alphabet); empty words dropped.
  Units (3): 'letter' = each letter; 'syllable' = CV split inside each plaintext word (syllable = consonant onset +
             vowel run, vowels aeiouy; trailing consonants join the last syllable; a vowel-less word is one unit);
             'chunk' = consecutive 2-letter pieces inside each word (a leftover letter is its own unit).
             Unit inventory cap: at most max(23, n_cores // 3) unit types (n_cores = distinct training cores); rarer
             units are written as their letters (letters always in the inventory).  One unit per word (the core).
  Homophones: every training core is assigned to exactly one unit (disjoint sets, so the core decodes to its unit):
             cores in descending training count (ties by string) each go to the unit with the largest remaining
             demand, demand_u = share_u x training core tokens (heap; greedy frequency packing).  H_u = number of
             cores of unit u (reported: mean / median / max).  Fresh homophone draw: P(core | u) ~ count^a.
             Recency: if u was written within the last W = 20 words of the page, with prob r its last homophone is
             copied (else a fresh draw).  Reset at each page.
  Affix tables: NT = 6 line tables = k-means (s67.kmeans, k-means++, 10 restarts, numpy rng SEED) of the training
             lines on their [prefix | suffix] composition (each half smoothed toward the global distribution with 2
             pseudo-counts and normalised).  The prefix is drawn with Witten-Bell back-off by sampling (s67 style) from
             (t, core, prev) -> (core, prev) -> (t, k, prev, fin) -> (k, prev, fin) -> (k, prev) -> (k) -> unigram, then
             the suffix from (core, P, fin) -> (core, P) -> (k, P, fin) -> (k, P) -> (k) -> unigram (k = core class).
             prev = previous word's prefix in the line; line start = '^P' (first line of a page) or '^' (other lines):
             the prefix memory resets at every line.  fin = last word of the line.
             [Changed after fixture pass 1, before the freeze: pass 1 drew (P, S) from class-level contexts only
             ((t, k, prev, fin) -> ... -> (k)); refitted on its own planted text that version inflated word types by
             ~20 % and never recovered its own configuration, so the core identity was put at the top of the back-off
             (F-15: affixes are chosen by the core).]
             Line stickiness p: a table is drawn from the line-cluster prior at line start; before each later word it
             is kept with prob p, else redrawn from the prior.
  Length persistence (cadence, optional): M = 6 candidate (homophone, affix) draws for the SAME unit; one chosen with
             weight exp(-g |len - (mu + 0.5 (len_prev - mu))|) (s67 form, rho fixed 0.5); line-initial words: one
             candidate.  The plaintext is unchanged by this choice.
  Lines and pages: page line counts given (training pages: their own; held-out-like pages: the held-out quire's
             counts); line lengths drawn from the empirical training line lengths (s67 convention).  The plaintext
             unit stream is read consecutively from a seed-dependent start (wrapping).
  CONFIGURATION GRID (24): plaintext {latin, italian} x unit {letter, syllable, chunk} x p {0.5, 0.9} x cadence
             {off, on}.  Per configuration, fitted on the training quires by grid: r in {0, 0.25, 0.5}, a in {0.75,
             1.0}, and (cadence on) g in {0.75, 1.25, 2.0} -> 6 or 18 candidates each [g 1.25 added after fixture pass 1].
  FIT LOSS (training only; candidate text = seed 0 generated on the training pages' line counts; scored with the
             real training segmenter): s67's loss terms R(d) d = 1..20, word types, within-line Moran (s67's word-length-sd
             term is computed and printed but NOT summed: after fixture pass 2 it pushed the cadence fit to the weakest g
             and lost Moran on the planted text) +
             ((pm1_g - pm1_r)/0.01)^2 + ((pm3_g - pm3_r)/0.01)^2 + ((co_g - co_r)/0.01)^2, where pmk = within-line
             prefix MI excess at lag k (plug-in, minus the mean of 5 within-line shuffles) and co = s80 M-freq K = 100
             Miller-Madow core-order excess (10 within-line shuffles, map fitted on the same text).
  CONFIGURATION SELECTION (training folds only): on each fold, SEL = the configuration (with its fitted r, a, g) with
             the smallest training fit loss.  No held-out quantity enters fitting or selection.  SEL is the primary
             model of every call; the 24 fixed configurations are reported per prediction as descriptive results
             (24-fold multiplicity: a fixed configuration passing where SEL does not is NOT a C1 pass).
  Reference (not in any call): NAIBBE = Greshko's default Naibbe (s71 encipher_sticky_naibbe mode 'default') on the
             Latin plaintext, laid on the same page/line skeletons.

SCORING PER FOLD (s67 LOQO exactly: folds = quires with >= 4 pages in ZL3b, same quire letters on RF1b and IT2a)
  Battery (C1): s67.score_model on S57.Measured / S57.draws_for (N_DRAW 300, 80 % page subsamples), seeds (1, 2):
             P1 Moran, P2 core->core excess, P3 prefix gain, P4 jsd_first_fg in s15's width, P5 CHARWIN > 0, P7 types
             within +-15 % at matched tokens.  A fold "holds" iff >= 5 of the 6.
  Core order (C2): s80 M-freq map (s80.fit_freq / apply_map) fitted on the text's training(-like) cores, K in {50, 100,
             200}; MM excess (s80 formula) on the held-out(-like) pages over 200 exact within-line permutations (GPU
             torch); permutation p = (1 + #{null >= obs}) / 201 (L-171); the real held-out quire also gets a 95 %
             interval from 300 page subsamples (80 %) x 20 permutations (reported only).  Generated: both seeds jointly
             (statistic = seed mean, null = seed mean of paired permutations).  VOYNICH'S BAND at K = [min, max] of the
             real per-quire points over the fold's TRAINING quires with >= 4 pages (each quire with an M-freq map fitted
             on the other training quires).  Cell K holds iff the generated point lies inside the band AND the
             permutation decision agrees with the real held-out quire's ((p_gen < 0.05) == (p_real < 0.05)).  A fold
             holds C2 iff all three K hold.  [Band changed after fixture pass 3, before the freeze: pass 3 used the real
             held-out quire's own 95 % subsample interval, which the TRUE generator (ORACLE) met on 0/4 folds -- the
             interval omits the between-quire realisation (plaintext-passage) variance.]
  R(1) and s69 (C3): R(1) = s57.fit_stats R at d = 1 on the held-out(-like) pages (segmenter of the training(-like)
             pages), mean over seeds.  s69 calls (C1, C2, C3, C4, C5, C3p, C4p; s69 compute / all_values / calls
             verbatim, 500 subsamples) with the s69 split replaced by the fold split (training(-like) pages fit,
             held-out(-like) pages scored); generated = seed 1.  A fold holds C3 iff R(1)_gen > 1 AND all 7
             generated calls equal the real held-out quire's calls on that fold.
PRE-REGISTERED CALLS (SEL; each must hold on ZL3b, RF1b and IT2a)
  C1 (primary, s67/s71 rule): HLT PREDICTS held-out quires iff >= 5/6 predictions on >= 8/15 folds on ZL3b, RF1b, IT2a.
  C2: matched-K core order within Voynich's band at K = 50, 100, 200 on >= 8/15 folds.
  C3: R(1) > 1 and s69 calls match on >= 8/15 folds.
  READINGS (exactly one): C1 true -> "a plaintext-carrying cipher predicts the manuscript out of sample: candidate for a
  solver run"; C1 false, C2 and C3 true -> "matches the core and slot layers, misses (named predictions)"; otherwise
  "this construction does not reproduce the manuscript" with the failing components named.
FIXTURE (--synth): a synthetic manuscript = HLT (latin, syllable, p 0.9, cadence on; r 0.25, a 1.0, g 2.0) built from
  all ZL3b pages, on ZL3b's page skeleton and quire labels.  Folds B, E, M, T scored with the full grid (N_DRAW 100).
  P4 (s15's Voynich width) and P5 (CHARWIN > 0) are absolute Voynich targets that a synthetic manuscript need not
  meet itself (pass 1: its own jsd 0.11-0.18, CHARWIN -0.07..-0.21), so the fixture judges the RELATIVE predictions
  P1, P2, P3, P7 (each compares the generated text with the held-out 'manuscript' quire).
  ORACLE = the planted kit and parameters with fresh seeds (the true generator), scored as a model: the battery's ceiling.
  Checks: F1 SEL holds >= 3 of {P1, P2, P3, P7} on >= max(2, ORACLE folds - 1) of 4 folds; F2 NAIBBE holds < 3 of {P1, P2, P3, P7} on >= 3 of 4
  folds; F3 GPU MM equals s80.mi_batch to 1e-9 on test arrays.  FIXTURE PASS iff F1, F2, F3.  Reported: the full 6-
  prediction counts, the SEL configuration vs the planted one, C2/C3 cells.
  [Pass 1 (class-only affixes; F1 judged on >= 5/6 of all six): FAIL -- SEL 0/4, planted config 0/4, NAIBBE 0/4; F3 OK.]
  [Pass 2 (core-first affixes, g 1.25 added, F1 = >= 3 of 4 relative on >= 3 folds): FAIL -- SEL 1/4 (SEL = planted config on
   3/4 folds, but the fit chose g 0.75: Moran 0.18 vs 0.26), NAIBBE OK 4/4, F3 OK.  A scratch oracle check (true kit and
   parameters, fresh seeds) held >= 3 of 4 relative predictions on only 3/4 folds (P2 and P3 fail on single quires even for
   the true generator: the plaintext passage differs between quires and the 80 % page-subsample interval misses that
   realisation noise, L-171).  Hence ORACLE is added and F1 is judged against it; the sd term left the fit loss.]
  [Pass 3: PASS (SEL = planted config 4/4; SEL rel. 2/4, ORACLE 3/4, NAIBBE rejected 4/4, F3 OK) but C2 held on 0/4 folds
   for SEL AND ORACLE under the quire-interval band -> band redefined (above); C3 fails on the fixture because R(1) > 1 is
   an absolute Voynich target the synthetic text (R(1) 0.73-0.93) does not meet itself.]
  [Pass 4 (this frozen version): PASS -- SEL = planted config 4/4; F1 SEL 2/4 (need 2; ORACLE 3/4); F2 NAIBBE rejected 4/4;
   F3 max |GPU - CPU| 1.8e-15; C2 SEL 2/4, ORACLE 2/4, NAIBBE 0/4; s69 calls match SEL 4/4, NAIBBE 0/4.  No fixture fold
   reached >= 5/6 of all six for any model, ORACLE included (P4 and P5 are absolute there).  POWER CAVEAT for C1: even
   the true generator holds the relative predictions P2/P3 on single held-out quires only part of the time.]
COMPUTE: at most 4 worker processes at BelowNormal priority (psutil), 1 BLAS thread each; permutation nulls and
  subsample draws of the core-order curve on the GPU (torch cuda; CPU torch fallback on error); text generation is
  sequential Python on CPU (each word depends on the previous one; DEVIATION from the brief, disclosed).
Run:    python -I s83_homophonic_line_table_loqo.py [--synth] [--list-imports]
Writes: results_s83.txt, runs/s83/ (fit_<T>_<Q>.json, SEL held-out-like sidecars, cells.json; fixture.txt).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import bisect
import hashlib
import heapq
import json
import math
import random
import sys
import time
from collections import Counter, OrderedDict, defaultdict
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

import corpora  # noqa: E402
import s57_local_memory_model as S57  # noqa: E402
import s64_naibbe_taxonomy as S64  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s69_prefix_stream_memory as S69  # noqa: E402
import s71_weakened_grille_and_sticky_naibbe_loqo as S71  # noqa: E402
import s80_a14_size_matched as S80  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s83_homophonic_line_table_loqo.py"
STUB = ROOT / "s83_homophonic_line_table_loqo.prereg.sha256"
SYNTH = "--synth" in sys.argv
RUNS = ROOT / "runs" / "s83"
OUT = RUNS / "fixture.txt" if SYNTH else ROOT / "results_s83.txt"
SEED = 20261083
W = 20
NT = 6
M_CAND = 6
RHO = 0.5
TAB_ALPHA = 2.0
N_DRAW = 300
SEEDS = (1, 2)
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
PLAINS = ["latin", "italian"]
UNITS = ["letter", "syllable", "chunk"]
PSTICK = [0.5, 0.9]
CADS = [0, 1]
CONFIGS = [(pl, u, p, c) for pl in PLAINS for u in UNITS for p in PSTICK for c in CADS]
GRID_R = [0.0, 0.25, 0.5]
GRID_A = [0.75, 1.0]
GRID_G = [0.75, 1.25, 2.0]
KS_C2 = [50, 100, 200]
N_PERM = 200
N_DRAW_C2 = 300
N_DRAW_PERM = 20
P_ALPHA = 0.05
N_WORKERS = 4
RUN_LIMIT = 5 * 3600
PREDS = S67.PREDS
VOWELS = set("aeiouy")
FIX_CFG = ("latin", "syllable", 0.9, 1)
FIX_PRM = dict(r=0.25, a=1.0, g=2.0)
FIX_FOLDS = ["B", "E", "M", "T"]
log: list[str] = []


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
    return sorted(set(out))


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
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
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; loaded but not in stub: {', '.join(missing) or '-'})"


def low_priority():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if hasattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS") else 10)
    except Exception:  # noqa: BLE001
        pass


# ======================================================================= GPU permutation machinery
_DEV = None


def device():
    global _DEV
    if _DEV is None:
        try:
            import torch
            if torch.cuda.is_available():
                torch.zeros(1, device="cuda")
                _DEV = "cuda"
            else:
                _DEV = "cpu"
        except Exception:  # noqa: BLE001
            _DEV = "cpu"
    return _DEV


def _mm_t(a, b, K):
    """a, b: (S, n) long tensors in [0, K) -> (plug (S,), mm (S,)) float64 tensors, s80.mi_batch formula."""
    import torch
    S, n = a.shape
    dev = a.device
    off = torch.arange(S, device=dev, dtype=torch.long)[:, None]

    def ent(codes, M):
        c = torch.bincount((off * M + codes).reshape(-1), minlength=S * M).reshape(S, M).to(torch.float64)
        occ = (c > 0).sum(1).to(torch.float64)
        cl = torch.where(c > 0, c * torch.log2(torch.clamp(c, min=1.0)), torch.zeros_like(c)).sum(1)
        return math.log2(n) - cl / n, occ
    ha, ma = ent(a, K)
    hb, mb = ent(b, K)
    hj, mj = ent(a * K + b, K * K)
    plug = ha + hb - hj
    mm = plug + ((ma - 1) + (mb - 1) - (mj - 1)) / (2.0 * n * math.log(2.0))
    return plug, mm


def _mm_excess_runs(lab, lid, n_perm, gen):
    """lab, lid: 1-d long tensors (one text).  -> (obs_mm float, null_mm tensor (n_perm,))."""
    import torch
    same = lid[1:] == lid[:-1]
    left = torch.nonzero(same).reshape(-1)
    right = left + 1
    if len(left) < 2:
        return float("nan"), torch.full((n_perm,), float("nan"), dtype=torch.float64)
    K = int(lab.max().item()) + 1
    _, obs = _mm_t(lab[left][None], lab[right][None], K)
    lidf = lid.to(torch.float64)
    nulls = []
    done = 0
    while done < n_perm:
        S = min(50 if K > 100 else 100, n_perm - done)
        r = torch.rand((S, len(lid)), generator=gen, device=lid.device, dtype=torch.float64)
        P = torch.argsort(lidf[None, :] + r, dim=1)
        xs = lab[P]
        _, m = _mm_t(xs[:, left], xs[:, right], K)
        nulls.append(m)
        done += S
    return float(obs[0].item()), torch.cat(nulls)


def core_order(texts, Ks, seed, with_ci):
    """texts: list of (train core Counter, held-out pages as lists of lines of cores).
    -> {K: dict(point, p, ci or None)}; statistic = mean over texts (MM excess), null paired by permutation index."""
    import torch
    dev = device()
    try:
        return _core_order(texts, Ks, seed, with_ci, dev)
    except Exception as e:  # noqa: BLE001
        if dev != "cpu":
            print(f"GPU core_order failed ({e!r}); CPU fallback", flush=True)
            return _core_order(texts, Ks, seed, with_ci, "cpu")
        raise


def _core_order(texts, Ks, seed, with_ci, dev):
    import torch
    gen = torch.Generator(device=dev)
    gen.manual_seed(seed)
    prep = []
    for trc, pages in texts:
        cores, lid, pg = [], [], []
        li = 0
        for pi, lines in enumerate(pages):
            for ln in lines:
                cores.extend(ln); lid.extend([li] * len(ln)); pg.extend([pi] * len(ln)); li += 1
        prep.append((trc, cores, np.array(lid, np.int64), np.array(pg, np.int64), len(pages)))
    out = {}
    for K in Ks:
        obs_all, null_all, labs = [], [], []
        for trc, cores, lid, pg, npg in prep:
            mp = S80.fit_freq(trc, K)
            lab = S80.apply_map(cores, mp)
            labs.append(lab)
            lt = torch.as_tensor(lab, device=dev)
            idt = torch.as_tensor(lid, device=dev)
            o, nl = _mm_excess_runs(lt, idt, N_PERM, gen)
            obs_all.append(o); null_all.append(nl)
        obs = float(np.mean(obs_all))
        null = torch.stack(null_all).mean(0)
        point = obs - float(null.mean().item())
        p = (1 + int((null >= obs - 1e-12).sum().item())) / (1 + N_PERM)
        ci = None
        if with_ci:
            rng = np.random.default_rng(seed + 1)
            vals = []
            for _ in range(N_DRAW_C2):
                per = []
                for (trc, cores, lid, pg, npg), lab in zip(prep, labs):
                    m = max(1, int(round(0.8 * npg)))
                    sel = np.sort(rng.choice(npg, size=m, replace=False))
                    idx = np.nonzero(np.isin(pg, sel))[0]
                    sub = S80.compact(lab[idx])
                    o, nl = _mm_excess_runs(torch.as_tensor(sub, device=dev), torch.as_tensor(lid[idx], device=dev), N_DRAW_PERM, gen)
                    per.append(o - float(nl.mean().item()))
                vals.append(float(np.mean(per)))
            ci = (float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5)))
        out[K] = dict(point=point, p=p, ci=ci)
    return out


# ======================================================================= plaintext units
_PLAIN_CACHE = {}


def plain_words(name):
    if name not in _PLAIN_CACHE:
        if name == "latin":
            d = json.loads((ROOT / "runs" / "s49" / "lang_latin_cremma.meta.json").read_text(encoding="utf-8"))
            raw = [w for pg in d["pages"] for ln in pg["lines"] for w in ln]
        elif name == "italian":
            raw = corpora.control("italian_dante")[:60000]
        else:
            raise ValueError(name)
        ws = [S64.norm_letters([w]) for w in raw]
        _PLAIN_CACHE[name] = [w for w in ws if w]
    return _PLAIN_CACHE[name]


def cv_split(w):
    out = []
    i, n = 0, len(w)
    while i < n:
        j = i
        while j < n and w[j] not in VOWELS:
            j += 1
        k = j
        while k < n and w[k] in VOWELS:
            k += 1
        if k == j:
            if out:
                out[-1] += w[i:]
            else:
                out.append(w[i:])
            break
        out.append(w[i:k])
        i = k
    return out


def units_of(words, mode):
    out = []
    for w in words:
        if mode == "letter":
            out.extend(w)
        elif mode == "syllable":
            out.extend(cv_split(w))
        elif mode == "chunk":
            out.extend(w[i:i + 2] for i in range(0, len(w), 2))
        else:
            raise ValueError(mode)
    return out


# ======================================================================= construction kit (one per fold)
def _cum(counter):
    return S67._cum(counter)


def _wb(tab):
    return {k: (*_cum(v), sum(v.values()) / (sum(v.values()) + len(v))) for k, v in tab.items()}


class Kit:
    """Everything HLT fits on the training quires of one fold."""

    def __init__(self, tr_pages):
        self.tr_pages = tr_pages
        tr_tok = [w for ls in tr_pages for l in ls for w in l]
        self.seg = SlotSegmenter(tr_tok)
        self._sc = {}
        self.cls, self.cls_info = S67.core_classes(tr_pages, self.seg)
        self.core_count = Counter(self.segm(w)[1] for w in tr_tok)
        self.mu = float(np.mean([len(w) for w in tr_tok]))
        self.lens = [len(l) for ls in tr_pages for l in ls]
        self._affix_tables(tr_pages)
        self.pools = {}
        self.streams = {}
        self.pool_info = {}

    def segm(self, w):
        r = self._sc.get(w)
        if r is None:
            r = self._sc[w] = self.seg.segment(w)
        return r

    # ---- line tables
    def _affix_tables(self, tr_pages):
        lines = [l for ls in tr_pages for l in ls]
        gp, gs = Counter(), Counter()
        segl = [[self.segm(w) for w in l] for l in lines]
        for sl in segl:
            for p, c, s in sl:
                gp[p] += 1; gs[s] += 1
        pv, sv = sorted(gp), sorted(gs)
        pi, si = {p: i for i, p in enumerate(pv)}, {s: i for i, s in enumerate(sv)}
        gP = np.array([gp[p] for p in pv], float); gP /= gP.sum()
        gS = np.array([gs[s] for s in sv], float); gS /= gS.sum()
        X = np.zeros((len(lines), len(pv) + len(sv)))
        for r, sl in enumerate(segl):
            a = np.zeros(len(pv)); b = np.zeros(len(sv))
            for p, c, s in sl:
                a[pi[p]] += 1; b[si[s]] += 1
            n = len(sl)
            X[r, :len(pv)] = (a + TAB_ALPHA * gP) / (n + TAB_ALPHA)
            X[r, len(pv):] = (b + TAB_ALPHA * gS) / (n + TAB_ALPHA)
        inertia, C, lab = S67.kmeans(X, NT, np.random.default_rng(SEED))
        self.tab_sizes = [int((lab == t).sum()) for t in range(NT)]
        self.tab_prior = (list(range(NT)), list(np.cumsum(self.tab_sizes).tolist()))
        PA = [defaultdict(Counter) for _ in range(6)]
        SB = [defaultdict(Counter) for _ in range(5)]
        uniP, uniS = Counter(), Counter()
        li_global = 0
        for ls in tr_pages:
            for li, l in enumerate(ls):
                t = int(lab[li_global]); li_global += 1
                L = len(l)
                pp = "^P" if li == 0 else "^"
                for j, w in enumerate(l):
                    p, c, s = self.segm(w)
                    k = self.cls[c]
                    fin = j == L - 1
                    for lev, key in zip(PA, ((t, c, pp), (c, pp), (t, k, pp, fin), (k, pp, fin), (k, pp), k)):
                        lev[key][p] += 1
                    for lev, key in zip(SB, ((c, p, fin), (c, p), (k, p, fin), (k, p), k)):
                        lev[key][s] += 1
                    uniP[p] += 1; uniS[s] += 1
                    pp = p
        self.levP = [_wb(T) for T in PA]
        self.levS = [_wb(T) for T in SB]
        self.uniP, self.uniS = _cum(uniP), _cum(uniS)
        self.tab_info = dict(sizes=self.tab_sizes, contexts_P=[len(T) for T in PA], contexts_S=[len(T) for T in SB], inertia=round(inertia, 3))

    @staticmethod
    def _wbdraw(rng, levels, keys, uni):
        for lev, key in zip(levels, keys):
            e = lev.get(key)
            if e is None:
                continue
            ws, cum, lam = e
            if rng.random() < lam:
                return ws[bisect.bisect_right(cum, rng.random() * cum[-1])]
        ws, cum = uni
        return ws[bisect.bisect_right(cum, rng.random() * cum[-1])]

    def affix(self, rng, t, c, k, pp, fin):
        """prefix: (t, core, prev) -> (core, prev) -> (t, class, prev, fin) -> (class, prev, fin) -> (class, prev) -> (class)
        -> unigram; then suffix: (core, prefix, fin) -> (core, prefix) -> (class, prefix, fin) -> (class, prefix) -> (class)
        -> unigram (Witten-Bell back-off by sampling)."""
        p = self._wbdraw(rng, self.levP, ((t, c, pp), (c, pp), (t, k, pp, fin), (k, pp, fin), (k, pp), k), self.uniP)
        s = self._wbdraw(rng, self.levS, ((c, p, fin), (c, p), (k, p, fin), (k, p), k), self.uniS)
        return p, s

    # ---- homophone pools
    def pool(self, plain, unit):
        key = (plain, unit)
        if key in self.pools:
            return self.pools[key], self.streams[key]
        raw = units_of(plain_words(plain), unit)
        f = Counter(raw)
        n_cores = len(self.core_count)
        cap = max(23, n_cores // 3)
        kept = set(u for u, _ in sorted(f.items(), key=lambda kv: (-kv[1], kv[0]))[:cap])
        stream = []
        for u in raw:
            if u in kept:
                stream.append(u)
            else:
                stream.extend(u)
        f = Counter(stream)
        tot_u = sum(f.values())
        tot_c = sum(self.core_count.values())
        heap = [(-f[u] / tot_u * tot_c, u) for u in sorted(f)]
        heapq.heapify(heap)
        unfilled = [(-f[u], u) for u in sorted(f)]
        heapq.heapify(unfilled)
        filled = set()
        assign = defaultdict(list)
        ordered = sorted(self.core_count.items(), key=lambda kv: (-kv[1], kv[0]))
        for i, (c, n) in enumerate(ordered):
            while unfilled and unfilled[0][1] in filled:
                heapq.heappop(unfilled)
            if unfilled and len(ordered) - i <= len(f) - len(filled):
                # reserve: the remaining cores go one each to the most frequent units still without a homophone
                _, u = heapq.heappop(unfilled)
                rem = None
                for kk, (rr, uu) in enumerate(heap):
                    if uu == u:
                        rem = rr; heap[kk] = heap[-1]; heap.pop(); heapq.heapify(heap); break
            else:
                rem, u = heapq.heappop(heap)
            assign[u].append((c, n))
            filled.add(u)
            if rem is not None:
                heapq.heappush(heap, (rem + n, u))
        miss = [u for u in f if u not in assign]
        if miss:
            raise RuntimeError(f"units without a homophone: {len(miss)}")
        pools = {}
        for u, lst in assign.items():
            cs = [c for c, _ in lst]
            ent = {"cores": cs}
            for a in GRID_A:
                ent[a] = list(np.cumsum([n ** a for _, n in lst]).tolist())
            pools[u] = ent
        H = [len(v) for v in assign.values()]
        self.pool_info[key] = dict(unit_types=len(f), stream=len(stream), H_mean=round(float(np.mean(H)), 1),
                                   H_median=float(np.median(H)), H_max=int(max(H)), cores=n_cores)
        self.pools[key], self.streams[key] = pools, stream
        return pools, stream

    # ---- generation
    def generate(self, cfg, prm, seed, line_counts):
        plain, unit, p, cad = cfg
        pools, stream = self.pool(plain, unit)
        rng = random.Random(seed * 1000003 + CONFIGS.index(cfg) * 7919 + 17)
        n = len(stream)
        pos = rng.randrange(n)
        r, a = prm["r"], prm["a"]
        g = prm["g"] if cad else 0.0
        mu = self.mu
        lens = self.lens
        cls = self.cls
        tw, tc = self.tab_prior
        ttot = tc[-1]
        affix = self.affix
        bis = bisect.bisect_right
        pages = []
        for nl in line_counts:
            last = {}
            idx = 0
            lines = []
            for li in range(nl):
                L = lens[int(rng.random() * len(lens))]
                t = tw[bis(tc, rng.random() * ttot)]
                pp = "^P" if li == 0 else "^"
                plen = mu
                line = []
                for j in range(L):
                    u = stream[pos]
                    pos += 1
                    if pos == n:
                        pos = 0
                    if j > 0 and rng.random() >= p:
                        t = tw[bis(tc, rng.random() * ttot)]
                    fin = j == L - 1
                    ent = pools[u]
                    e = last.get(u) if r > 0 else None
                    rec = e is not None and idx - e[1] <= W
                    nc = M_CAND if (g > 0 and j > 0) else 1
                    cands = []
                    for _ in range(nc):
                        if rec and rng.random() < r:
                            core = e[0]
                        else:
                            cum = ent[a]
                            core = ent["cores"][bis(cum, rng.random() * cum[-1])]
                        pr, su = affix(rng, t, core, cls[core], pp, fin)
                        cands.append((pr + core + su, core, pr))
                    if nc > 1:
                        tgt = mu + RHO * (plen - mu)
                        wts = [math.exp(-g * abs(len(c[0]) - tgt)) for c in cands]
                        x = rng.random() * sum(wts)
                        acc, pick = 0.0, nc - 1
                        for jj, wv in enumerate(wts):
                            acc += wv
                            if x < acc:
                                pick = jj
                                break
                        w, core, pr = cands[pick]
                    else:
                        w, core, pr = cands[0]
                    line.append(w)
                    last[u] = (core, idx)
                    idx += 1
                    pp = pr
                    plen = len(w)
                lines.append(line)
            pages.append(lines)
        return pages


# ======================================================================= fit statistics
def _lid_arrays(pages, f):
    x, lid = [], []
    li = 0
    for ls in pages:
        for l in ls:
            for w in l:
                x.append(f(w)); lid.append(li)
            li += 1
    return x, np.array(lid, np.int64)


def prefix_lag_excess(pages, segm, ks=(1, 3), n_shuf=5, seed=0):
    xs, lid = _lid_arrays(pages, lambda w: segm(w)[0])
    ids = {}
    x = np.array([ids.setdefault(v, len(ids)) for v in xs], np.int64)
    rng = np.random.default_rng(seed)
    perms = [np.lexsort((rng.random(len(x)), lid)) for _ in range(n_shuf)]
    out = {}
    for k in ks:
        left = np.nonzero(lid[k:] == lid[:-k])[0]
        obs = S57.mi_codes(x[left], x[left + k])
        nul = [S57.mi_codes(x[pm][left], x[pm][left + k]) for pm in perms]
        out[k] = obs - float(np.mean(nul))
    return out


def core_order_insample(pages, segm, K=100, n_shuf=10, seed=0):
    cores, lid = _lid_arrays(pages, lambda w: segm(w)[1])
    mp = S80.fit_freq(Counter(cores), K)
    lab = S80.apply_map(cores, mp)
    return S80.Scorer(lid).excess([lab], n_shuf, np.random.default_rng(seed))[0][1]


def text_stats(pages, enc, segm):
    g = S57.fit_stats(pages, enc)
    pm = prefix_lag_excess(pages, segm)
    return dict(R=g["R"], types=g["types"], tokens=g["tokens"], moran=S67.moran_pages(pages), sd=S67.len_sd(pages),
                pm1=pm[1], pm3=pm[3], co=core_order_insample(pages, segm))


def hlt_loss(g, r):
    parts = (float(np.mean(((g["R"] - r["R"]) / 0.01) ** 2)),
             float(((g["types"] - r["types"]) / r["types"] / 0.01) ** 2),
             float(((g["moran"] - r["moran"]) / 0.01) ** 2),
             float(((g["sd"] - r["sd"]) / r["sd"] / 0.01) ** 2),
             float(((g["pm1"] - r["pm1"]) / 0.01) ** 2),
             float(((g["pm3"] - r["pm3"]) / 0.01) ** 2),
             float(((g["co"] - r["co"]) / 0.01) ** 2))
    return sum(parts) - parts[3], parts   # word-length sd is reported (parts[3]) but not in the sum (after fixture pass 2)


def param_grid(cfg):
    out = []
    for r in GRID_R:
        for a in GRID_A:
            for g in (GRID_G if cfg[3] else [0.0]):
                out.append(dict(r=r, a=a, g=g))
    return out


def fit_all(kit, configs):
    enc = S57.Encoder(kit.seg)
    real = text_stats(kit.tr_pages, enc, kit.segm)
    counts = [len(ls) for ls in kit.tr_pages]
    res = {}
    for cfg in configs:
        best = None
        for prm in param_grid(cfg):
            pages = kit.generate(cfg, prm, 0, counts)
            g = text_stats(pages, enc, kit.segm)
            L, parts = hlt_loss(g, real)
            if best is None or L < best[0]:
                best = (L, parts, prm, g)
        L, parts, prm, g = best
        res[cfg] = dict(loss=L, parts=parts, params=prm,
                        gen=dict(moran=g["moran"], sd=g["sd"], pm1=g["pm1"], pm3=g["pm3"], co=g["co"], R1=float(g["R"][0]), types=g["types"]))
    realinfo = dict(moran=real["moran"], sd=real["sd"], pm1=real["pm1"], pm3=real["pm3"], co=real["co"], R1=float(real["R"][0]), types=real["types"])
    return res, realinfo


# ======================================================================= per-fold scoring helpers
def s69_calls(train_pages, test_pages, name):
    pages = [dict(id=f"tr{i}", lines=ls) for i, ls in enumerate(train_pages)] + [dict(id=f"te{i}", lines=ls) for i, ls in enumerate(test_pages)]
    trid = {f"tr{i}" for i in range(len(train_pages))}
    orig = S69.split_pages
    S69.split_pages = lambda _pages: trid
    try:
        t = S69.Text(name, S69.norm_pages(pages))
    finally:
        S69.split_pages = orig
    Wd = {k: t.A[k] for k in ("pre", "suf", "core", "cc", "gal")}
    st = S69.compute(t, Wd)
    point = S69.all_values(st)
    rng = np.random.default_rng(S69.SEED)
    P = t.n_te_pages
    m = int(round(S69.SUB_FRAC * P))
    subs = defaultdict(list)
    for _ in range(S69.B_SUB):
        sel = rng.choice(P, size=m, replace=False)
        for k, v in S69.all_values(st, sel).items():
            subs[k].append(v)
    ci = {k: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))) for k, v in subs.items()}
    rows, _ = S69.calls({name: dict(point=point, ci=ci)}, [name])
    return {k: bool(v[0]) for k, v in rows[name].items()}, float(point["M1"])


def r1_of(train_pages, test_pages):
    seg = SlotSegmenter([w for ls in train_pages for l in ls for w in l])
    return float(S57.fit_stats(test_pages, S57.Encoder(seg))["R"][0])


def cores_of(train_pages, test_pages):
    seg = SlotSegmenter([w for ls in train_pages for l in ls for w in l])
    trc = Counter(seg.segment(w)[1] for ls in train_pages for l in ls for w in l)
    te = [[[seg.segment(w)[1] for w in l] for l in ls] for ls in test_pages]
    return trc, te


def real_band(pages, Q, seg):
    """Voynich's band at each K: [min, max] of the real per-quire core-order points over the TRAINING quires with
    >= 4 pages (each quire scored with an M-freq map fitted on the other training quires; fold segmenter)."""
    byq = defaultdict(list)
    for _, q, ls in pages:
        if q != Q:
            byq[q].append([[seg.segment(w)[1] for w in l] for l in ls])
    vals = defaultdict(list)
    for i, q in enumerate(sorted(byq)):
        if len(byq[q]) < 4:
            continue
        trc = Counter(c for qq, pl in byq.items() if qq != q for ls in pl for l in ls for c in l)
        r = core_order([(trc, byq[q])], KS_C2, SEED + 7000 + i, False)
        for K in KS_C2:
            vals[K].append(r[K]["point"])
    return {K: (float(min(v)), float(max(v)), len(v)) for K, v in vals.items()}


def c2_cells(real_c2, gen_c2, band):
    cells = {}
    for K in KS_C2:
        rr, gg = real_c2[K], gen_c2[K]
        lo, hi, _ = band[K]
        inside = lo <= gg["point"] <= hi
        agree = (gg["p"] < P_ALPHA) == (rr["p"] < P_ALPHA)
        cells[K] = dict(ok=bool(inside and agree), inside=bool(inside), agree=bool(agree), gen=gg["point"], gen_p=gg["p"])
    return cells


_NAIBBE = {}


def naibbe_pages(seed, line_counts, lens):
    if "K" not in _NAIBBE:
        _NAIBBE["K"] = S64.load_greshko()
        _NAIBBE["letters"] = "".join(plain_words("latin"))
    rng = random.Random(seed + 83)
    skel = [dict(id=f"n{i}", lines=[["x"] * lens[int(rng.random() * len(lens))] for _ in range(nl)]) for i, nl in enumerate(line_counts)]
    out = S71.encipher_sticky_naibbe(_NAIBBE["letters"], _NAIBBE["K"], skel, mode="default", seed=seed + 8300)
    return [p["lines"] for p in out]


def cfg_name(cfg):
    pl, u, p, c = cfg
    return f"{pl[:3]}-{u[:4]}-p{p}-{'cad' if c else 'nocad'}"


def run_fold(job):
    low_priority()
    try:
        import torch
        torch.set_num_threads(1)
    except Exception:  # noqa: BLE001
        pass
    t0 = time.time()
    S57.N_DRAW = job.get("n_draw", N_DRAW)
    T, Q = job["T"], job["Q"]
    pages = job["pages"]
    train = [(p, ls) for p, q, ls in pages if q != Q]
    test = [(p, ls) for p, q, ls in pages if q == Q]
    tr_pages = [ls for _, ls in train]
    te_pages = [ls for _, ls in test]
    lines = []
    say = lines.append
    say(f"--- {T} fold {Q}: held-out {len(test)} pages ({sum(len(l) for ls in te_pages for l in ls)} tokens), training {len(train)} pages "
        f"({sum(len(l) for ls in tr_pages for l in ls)} tokens)")
    kit = Kit(tr_pages)
    fits, realinfo = fit_all(kit, CONFIGS)
    t_fit = time.time() - t0
    sel = min(CONFIGS, key=lambda c: (fits[c]["loss"], CONFIGS.index(c)))
    say(f"  kit: classes {kit.cls_info['top_class_sizes']}; line tables {kit.tab_info}; mu {kit.mu:.3f}")
    for key, inf in kit.pool_info.items():
        say(f"  pool {key[0]}/{key[1]}: {inf}")
    say(f"  training targets: Moran {realinfo['moran']:.4f}, sd {realinfo['sd']:.4f}, pm1 {realinfo['pm1']:+.4f}, pm3 {realinfo['pm3']:+.4f}, "
        f"core order K100 {realinfo['co']:+.4f}, R(1) {realinfo['R1']:.3f}, types {realinfo['types']}")
    for cfg in CONFIGS:
        f = fits[cfg]
        say(f"  fit {cfg_name(cfg):24} {'SEL' if cfg == sel else '   '} loss {f['loss']:9.1f} (" + ", ".join(f"{x:.0f}" for x in f['parts'])
            + f") r {f['params']['r']} a {f['params']['a']} g {f['params']['g']}; in-sample Moran {f['gen']['moran']:.3f} pm1 {f['gen']['pm1']:+.3f} "
            f"pm3 {f['gen']['pm3']:+.3f} co {f['gen']['co']:+.3f} R1 {f['gen']['R1']:.2f} types {f['gen']['types']}")
    say(f"  fits {t_fit:.0f}s; SEL = {cfg_name(sel)}")
    # ---- real held-out quantities
    off = job["off"]
    real_m = S57.Measured(f"{T} {Q} real", train, test)
    real_dr = S57.draws_for([real_m], SEED + off)
    real_pt = real_m.point()
    real_calls, real_m1 = s69_calls(tr_pages, te_pages, f"{T}{Q}real")
    real_c2 = core_order([cores_of(tr_pages, te_pages)], KS_C2, SEED + off + 500, True)
    real_r1 = r1_of(tr_pages, te_pages)
    band = real_band(pages, Q, SlotSegmenter([w for ls in tr_pages for l in ls for w in l]))
    say("  Voynich band (training quires, min..max): " + ", ".join(f"K{K} [{band[K][0]:+.4f},{band[K][1]:+.4f}] n{band[K][2]}" for K in KS_C2))
    say(f"  real held-out: Moran {real_pt['P1']:.4f}; core->core {real_pt['P2']:+.4f}; prefix gain {real_pt['P3']:+.4f}; jsd {real_pt['P4']:.4f}; "
        f"CHARWIN {real_pt['P5']:+.4f}; R(1) {real_r1:.3f}; s69 M1 {real_m1:+.4f} calls " + "".join("T" if real_calls[c] else "F" for c in S69.CALLS)
        + "; core order " + ", ".join(f"K{K} {real_c2[K]['point']:+.4f} [{real_c2[K]['ci'][0]:+.4f},{real_c2[K]['ci'][1]:+.4f}] p {real_c2[K]['p']:.3f}" for K in KS_C2))
    tr_counts = [len(ls) for ls in tr_pages]
    te_counts = [len(ls) for ls in te_pages]
    models = [("SEL", sel)] + [(cfg_name(c), c) for c in CONFIGS] + [("NAIBBE", None)]
    okit = None
    if job.get("oracle_src") is not None:
        okit = Kit(job["oracle_src"])
        models.append(("ORACLE", "oracle"))
    out_dir = Path(job["out_dir"]); out_dir.mkdir(parents=True, exist_ok=True)
    res = dict(T=T, Q=Q, n_test=len(test), sel=cfg_name(sel), fits={cfg_name(c): fits[c] for c in CONFIGS}, realinfo=realinfo,
               real_point=real_pt, real_calls=real_calls, real_m1=real_m1, real_c2=real_c2, real_r1=real_r1, band=band,
               pool_info={f"{k[0]}/{k[1]}": v for k, v in kit.pool_info.items()}, models={})
    cache = {}
    for j, (mname, cfg) in enumerate(models):
        if mname != "SEL" and cfg in CONFIGS and cfg in cache:
            res["models"][mname] = cache[cfg]
            continue
        gens = []
        for s in SEEDS:
            if cfg is None:
                pg = naibbe_pages(s + off, tr_counts + te_counts, kit.lens)
            elif cfg == "oracle":
                pg = okit.generate(FIX_CFG, FIX_PRM, s + 50, tr_counts + te_counts)
            else:
                pg = kit.generate(cfg, fits[cfg]["params"], s, tr_counts + te_counts)
            gens.append((pg[:len(train)], pg[len(train):]))
        ms = [S57.Measured(f"{T} {Q} {mname} s{i}", [(f"g{k}", x) for k, x in enumerate(a)], [(f"h{k}", x) for k, x in enumerate(b)])
              for i, (a, b) in enumerate(gens)]
        gen_dr = S57.draws_for(ms, SEED + off + 1 + j)
        cells, gen_pt, rt, small = S67.score_model(real_m, real_pt, real_dr, ms, gen_dr, len(test), [b for _, b in gens], te_pages)
        n = sum(1 for k in PREDS if cells[k][0])
        gcalls, gm1 = s69_calls(gens[0][0], gens[0][1], f"{T}{Q}{mname}")
        gc2 = core_order([cores_of(a, b) for a, b in gens], KS_C2, SEED + off + 600 + j, False)
        c2 = c2_cells(real_c2, gc2, band)
        r1 = float(np.mean([r1_of(a, b) for a, b in gens]))
        calls_ok = all(gcalls[c] == real_calls[c] for c in S69.CALLS)
        rec = dict(n=n, holds={k: bool(cells[k][0]) for k in PREDS}, text={k: cells[k][1] for k in PREDS}, gen_point=gen_pt,
                   type_ratio=rt, small=small, calls=gcalls, m1=gm1, calls_ok=calls_ok, r1=r1,
                   c2={K: c2[K] for K in KS_C2}, c2_ok=all(c2[K]["ok"] for K in KS_C2),
                   c3_ok=bool(r1 > 1 and calls_ok), cfg=cfg_name(cfg) if cfg in CONFIGS else mname)
        res["models"][mname] = rec
        if mname == "SEL":
            cache[cfg] = rec
            side = dict(source=f"s83 SEL {cfg_name(cfg)} fitted on {T} quires other than {Q}, seed 1; held-out-like pages", params=fits[cfg]["params"],
                        pages=[dict(id=f"h{i}", section="S83", hand="S83", lang="?", quire=Q, lines=ls, role="heldout") for i, ls in enumerate(gens[0][1])])
            (out_dir / f"SEL_{T}_{Q}_s1.meta.json").write_text(json.dumps(side), encoding="utf-8", newline="\n")
        if mname in ("SEL", "NAIBBE", "ORACLE"):
            say(f"  -- {mname} ({rec['cfg']}): {n}/6 [" + " ".join(f"{k}{'+' if cells[k][0] else '-'}" for k in PREDS) + f"]; C2 {'+' if rec['c2_ok'] else '-'} "
                + ", ".join(f"K{K} {c2[K]['gen']:+.4f} p {c2[K]['gen_p']:.3f}{'' if c2[K]['ok'] else (' OUT' if not c2[K]['inside'] else ' P-DISAGREE')}" for K in KS_C2)
                + f"; R(1) {r1:.3f}; s69 M1 {gm1:+.4f} calls " + "".join("T" if gcalls[c] else "F" for c in S69.CALLS) + f" {'match' if calls_ok else 'MISMATCH'}")
            for k in PREDS:
                say(f"    {k} {'HOLDS' if cells[k][0] else 'fails'}: {cells[k][1]}")
    say(f"  fold time {time.time() - t0:.0f}s (fits {t_fit:.0f}s)")
    res["lines"] = lines
    res["secs"] = time.time() - t0
    (out_dir / f"fit_{T}_{Q}.json").write_text(json.dumps(dict(translit=T, fold=Q, sel=cfg_name(sel), fits=res["fits"], realinfo=realinfo,
                                                               pool_info=res["pool_info"], tables=kit.tab_info), indent=1, default=float),
                                               encoding="utf-8", newline="\n")
    return res


# ======================================================================= summary and calls
def summarize(allres, folds_by_T, say):
    names = ["SEL"] + [cfg_name(c) for c in CONFIGS] + ["NAIBBE"] + (["ORACLE"] if any("ORACLE" in r["models"] for r in allres.values()) else [])
    say("=== PER-PREDICTION FOLD COUNTS (P1 P2 P3 P4 P5 P7; folds >= 5/6; C2 folds; C3 folds; R(1)>1 folds; s69-match folds) ===")
    summ = {}
    for T, folds in folds_by_T.items():
        nf = len(folds)
        say(f"  {T}:")
        for m in names:
            rs = [allres[(T, Q)]["models"][m] for Q in folds]
            cnt = {k: sum(r["holds"][k] for r in rs) for k in PREDS}
            n5 = sum(r["n"] >= 5 for r in rs)
            c2 = sum(r["c2_ok"] for r in rs)
            c3 = sum(r["c3_ok"] for r in rs)
            r1 = sum(r["r1"] > 1 for r in rs)
            cm = sum(r["calls_ok"] for r in rs)
            summ[(T, m)] = dict(n5=n5, c2=c2, c3=c3, cnt=cnt)
            say(f"    {m:24} >=5/6 {n5:2d}/{nf} | " + " ".join(f"{k} {cnt[k]:2d}" for k in PREDS)
                + f" | C2 {c2:2d} | C3 {c3:2d} (R1>1 {r1:2d}, s69 {cm:2d}) | mean R1 {np.mean([r['r1'] for r in rs]):.3f}")
    say("")
    say("=== SEL per fold ===")
    for T, folds in folds_by_T.items():
        for Q in folds:
            r = allres[(T, Q)]
            m = r["models"]["SEL"]
            say(f"  {T} {Q}: {r['sel']:24} {m['n']}/6 " + "".join("+" if m["holds"][k] else "-" for k in PREDS)
                + f" t{m['type_ratio']:.2f} | C2 " + "".join("+" if m["c2"][K]["ok"] else "-" for K in KS_C2)
                + f" | R1 gen {m['r1']:.3f} real {r['real_r1']:.3f} | s69 gen " + "".join("T" if m["calls"][c] else "F" for c in S69.CALLS)
                + " real " + "".join("T" if r["real_calls"][c] else "F" for c in S69.CALLS) + f" M1 gen {m['m1']:+.3f} real {r['real_m1']:+.3f}")
    sel_counts = Counter(allres[(T, Q)]["sel"] for T, folds in folds_by_T.items() for Q in folds)
    say(f"  SEL chosen: {dict(sel_counts.most_common())}")
    say("")
    return summ


def decide(summ, folds_by_T, say):
    Ts = list(folds_by_T)
    need = {T: len(folds_by_T[T]) // 2 + 1 for T in Ts}   # 8 of 15
    c1 = all(summ[(T, "SEL")]["n5"] >= need[T] for T in Ts)
    c2 = all(summ[(T, "SEL")]["c2"] >= need[T] for T in Ts)
    c3 = all(summ[(T, "SEL")]["c3"] >= need[T] for T in Ts)
    say("=== PRE-REGISTERED CALLS (SEL) ===")
    say(f"  C1 >=5/6 on >= {need[Ts[0]]}/{len(folds_by_T[Ts[0]])} folds on every transliteration: {c1} (" + ", ".join(f"{T} {summ[(T, 'SEL')]['n5']}" for T in Ts) + ")")
    say(f"  C2 matched-K core order within band at K 50/100/200: {c2} (" + ", ".join(f"{T} {summ[(T, 'SEL')]['c2']}" for T in Ts) + ")")
    say(f"  C3 R(1) > 1 and s69 calls match: {c3} (" + ", ".join(f"{T} {summ[(T, 'SEL')]['c3']}" for T in Ts) + ")")
    tot = Counter()
    for T in Ts:
        for k in PREDS:
            tot[k] += summ[(T, "SEL")]["cnt"][k]
    nf_all = sum(len(folds_by_T[T]) for T in Ts)
    worst = sorted(PREDS, key=lambda k: tot[k])
    say("  SEL folds holding each prediction (all transliterations, of " + str(nf_all) + "): " + ", ".join(f"{k} {tot[k]}" for k in PREDS))
    if c1:
        v = "a plaintext-carrying cipher predicts the manuscript out of sample: candidate for a solver run"
    elif c2 and c3:
        v = f"matches the core and slot layers, misses ({', '.join(k for k in worst if tot[k] * 2 <= nf_all) or worst[0]})"
    else:
        fail = []
        fail.append("held-out battery C1 (weakest: " + ", ".join(f"{k} {tot[k]}/{nf_all}" for k in worst[:3]) + ")")
        if not c2:
            fail.append("matched-K core order C2")
        if not c3:
            fail.append("R(1)/s69 calls C3")
        v = "this construction does not reproduce the manuscript (failing: " + "; ".join(fail) + ")"
    say(f"VERDICT: {v}")
    return c1, c2, c3, v


# ======================================================================= fixture
def gpu_check(say):
    import torch
    rng = np.random.default_rng(3)
    ok = True
    for K in (5, 50, 200):
        A = rng.integers(0, K, size=(7, 900)); B = (A + rng.integers(0, 3, size=A.shape)) % K
        p_np, m_np = S80.mi_batch(A, B, K)
        dev = device()
        p_t, m_t = _mm_t(torch.as_tensor(A, device=dev), torch.as_tensor(B, device=dev), K)
        d = max(float(np.abs(p_np - p_t.cpu().numpy()).max()), float(np.abs(m_np - m_t.cpu().numpy()).max()))
        say(f"  F3 GPU/CPU MI check K={K}: max |diff| {d:.2e} on {dev}")
        ok = ok and d < 1e-9
    return ok


def fixture():
    t0 = time.time()
    emit(f"s83 fixture (--synth) -- date: {S67.clock()}")
    emit(f"device: {device()}")
    f3 = gpu_check(emit)
    zl = S67.load_pages(ROOT / "data" / "translit" / "ZL3b_eva.meta.json")
    kit = Kit([ls for _, _, ls in zl])
    synth = kit.generate(FIX_CFG, FIX_PRM, 4242, [len(ls) for _, _, ls in zl])
    pages = [(pid, q, synth[i]) for i, (pid, q, _) in enumerate(zl)]
    emit(f"  synthetic manuscript: HLT {cfg_name(FIX_CFG)} {FIX_PRM} built from all ZL3b pages; {len(pages)} pages, "
         f"{sum(len(l) for _, _, ls in pages for l in ls)} tokens; pool {kit.pool_info}")
    emit(f"  synthetic Moran {S67.moran_pages(synth):.4f}")
    flush()
    src = [ls for _, _, ls in zl]
    jobs = [dict(T="FIX", Q=Q, pages=pages, out_dir=str(RUNS / "fixture"), off=900000 + 1000 * i, n_draw=100, oracle_src=src) for i, Q in enumerate(FIX_FOLDS)]
    from multiprocessing import Pool
    allres = {}
    with Pool(min(N_WORKERS, len(jobs)), initializer=low_priority) as pool:
        for r in pool.imap_unordered(run_fold, jobs):
            allres[(r["T"], r["Q"])] = r
            emit(f"[{time.time() - t0:.0f}s] fold {r['Q']} done ({r['secs']:.0f}s)")
            flush()
    for Q in FIX_FOLDS:
        for ln in allres[("FIX", Q)]["lines"]:
            emit(ln)
    summ = summarize(allres, {"FIX": FIX_FOLDS}, emit)
    REL = ("P1", "P2", "P3", "P7")

    def rel_folds(m, cond):
        return sum(cond(sum(allres[("FIX", Q)]["models"][m]["holds"][k] for k in REL)) for Q in FIX_FOLDS)
    sel_ok = rel_folds("SEL", lambda n: n >= 3)
    nai_ok = rel_folds("NAIBBE", lambda n: n < 3)
    pl_ok = rel_folds(cfg_name(FIX_CFG), lambda n: n >= 3)
    or_ok = rel_folds("ORACLE", lambda n: n >= 3)
    emit(f"  ORACLE (planted kit and parameters, fresh seeds) holds >= 3 of P1 P2 P3 P7 on {or_ok}/4 folds (the battery's ceiling for this family)")
    f1 = sel_ok >= max(2, or_ok - 1)
    f2 = nai_ok >= 3
    emit(f"  F1 SEL holds >= 3 of P1 P2 P3 P7 on {sel_ok}/4 folds (need >= max(2, ORACLE - 1) = {max(2, or_ok - 1)}) -> {'OK' if f1 else 'FAIL'}  [planted config fixed: {pl_ok}/4; "
         f"SEL >= 5/6 of all six: {summ[('FIX', 'SEL')]['n5']}/4]")
    emit(f"  F2 NAIBBE holds < 3 of P1 P2 P3 P7 on {nai_ok}/4 folds (need >= 3) -> {'OK' if f2 else 'FAIL'}  [NAIBBE >= 5/6: {summ[('FIX', 'NAIBBE')]['n5']}/4]")
    planted = sum(allres[("FIX", Q)]["sel"] == cfg_name(FIX_CFG) for Q in FIX_FOLDS)
    emit(f"  F3 GPU MI equals s80.mi_batch -> {'OK' if f3 else 'FAIL'}")
    emit(f"  reported: SEL = planted configuration on {planted}/4 folds; SEL C2 folds {summ[('FIX', 'SEL')]['c2']}/4, C3 folds {summ[('FIX', 'SEL')]['c3']}/4; "
         f"NAIBBE C2 {summ[('FIX', 'NAIBBE')]['c2']}/4, C3 {summ[('FIX', 'NAIBBE')]['c3']}/4")
    ok = f1 and f2 and f3
    emit(f"FIXTURE {'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f}s); date end: {S67.clock()}")
    flush()
    return ok


# ======================================================================= main
def main():
    from multiprocessing import Pool
    low_priority()
    t0 = time.time()
    emit("s83 -- homophonic letter/syllable/chunk-in-core cipher with a per-line sticky affix table (HLT), leave-one-quire-out")
    emit(f"date: {S67.clock()}")
    emit(f"sha256 {SELF.name}: {sha256(SELF)}")
    emit(f"sha256 {STUB.name}: {sha256(STUB) if STUB.exists() else 'missing'}")
    emit(f"stub_match: {stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    dev = device()
    try:
        import torch
        tv = torch.__version__
        dn = torch.cuda.get_device_name(0) if dev == "cuda" else "cpu"
    except Exception:  # noqa: BLE001
        tv, dn = "n/a", "cpu"
    emit(f"device: {dev} ({dn}; torch {tv}) for core-order permutations and subsample draws; generation and the s67 battery on CPU; "
         f"{N_WORKERS} worker processes at BelowNormal priority")
    emit(f"numpy {np.__version__}; python -I; configs {len(CONFIGS)}; grids r {GRID_R}, a {GRID_A}, g {GRID_G}; NT {NT}, M {M_CAND}, W {W}, rho {RHO}; "
         f"seeds {SEEDS}; N_DRAW {N_DRAW}; core order K {KS_C2}, {N_PERM} permutations, {N_DRAW_C2} x {N_DRAW_PERM} subsample draws")
    emit("SELECTION: SEL = the configuration with the smallest training fit loss on each fold (training quires only).")
    emit("")
    data = {}
    for T, f in TRANSLITS.items():
        path = ROOT / "data" / "translit" / f"{f}.meta.json"
        emit(f"translit {T}: {path.name} sha256={sha256(path)[:16]}")
        data[T] = S67.load_pages(path)
    folds = S67.folds_of(data["ZL3b"])
    emit(f"folds (quires with >= 4 pages in ZL3b): {folds} ({len(folds)})")
    emit("")
    flush()
    jobs = []
    for ti, T in enumerate(TRANSLITS):
        for fi, Q in enumerate(folds):
            jobs.append(dict(T=T, Q=Q, pages=data[T], out_dir=str(RUNS), off=100000 * ti + 1000 * fi))
    emit(f"running {len(jobs)} fold jobs on {N_WORKERS} worker processes")
    allres = {}
    with Pool(N_WORKERS, initializer=low_priority) as pool:
        for r in pool.imap_unordered(run_fold, jobs):
            allres[(r["T"], r["Q"])] = r
            print(f"[{time.time() - t0:.0f}s] done {r['T']} {r['Q']} ({r['secs']:.0f}s) SEL {r['sel']} {r['models']['SEL']['n']}/6", flush=True)
            if time.time() - t0 > RUN_LIMIT:
                pool.terminate()
                raise TimeoutError("run exceeded the wall limit")
    for T in TRANSLITS:
        emit(f"=== {T} ===")
        for Q in folds:
            for ln in allres[(T, Q)]["lines"]:
                emit(ln)
        emit("")
    flush()
    summ = summarize(allres, {T: folds for T in TRANSLITS}, emit)
    decide(summ, {T: folds for T in TRANSLITS}, emit)
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "cells.json").write_text(json.dumps({f"{T}|{Q}": {k: v for k, v in r.items() if k != "lines"} for (T, Q), r in allres.items()},
                                                indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)),
                                     encoding="utf-8", newline="\n")
    emit("")
    emit(f"elapsed: {time.time() - t0:.1f} s")
    emit(f"date end: {S67.clock()}")
    emit(f"paths: {OUT}, {RUNS}")
    flush()


if __name__ == "__main__":
    if "--list-imports" in sys.argv:
        for m in local_modules():
            print(m)
        sys.exit(0)
    if SYNTH:
        sys.exit(0 if fixture() else 1)
    main()
