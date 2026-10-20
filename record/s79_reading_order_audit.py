"""S79: reading-order audit -- which filed constraints depend on an assumed reading order?

QUESTION (frozen; Jon's directive): "assume we don't know the order pages are read in; it could be a
choose-your-own-adventure or totally backwards; reduce assumptions like that."  For every constraint A1-A21 and dots
15-26 of workflow/CONSTRAINTS-MAP.md: is it order-free, or does it depend on the within-line word direction, the line
order, the page order or the glyph direction inside words?

PRE-REGISTRATION: s79_reading_order_audit.prereg.sha256 (sha256sum format, LF, no BOM) = sha256 of this file and of
every local module it imports, frozen BEFORE any real-data run.  Before the freeze the script ran only with --fixture
(synthetic texts with a planted left-to-right line-edge asymmetry and a planted page-order drift; reads no real data;
writes only runs/s79/fixture.txt).  The script re-hashes itself and its local imports and prints stub_match.

TEXTS (real run): Voynich ZL3b (data/translit/ZL3b_eva.meta.json), RF1b, IT2a.  Three page lists per transliteration,
  each from the loader of the statistic's original script, so T0 reproduces the filed numbers:
  P69 = s69.voynich_pages (meta.json + IVTFF re-parse for drawing gaps and paragraph starts), used by every statistic
        except the s55 family; quire / section / hand / lang are attached from the meta.json by page id.
  P55 = s55.voynich_pages (n1_habit_table.load), used by the s55 family (f1, f2, f4 and its mirrors).
  ZL3b filed-loader check only: metrics_new.voynich_pages("eva") (the s44 / s21 loader) for the A1 reproduction.

TRANSFORMATIONS (applied to the page / line / word structure before any statistic is computed):
  T0   original.
  T1   reverse word order within every line (drawing-gap marks move with the word boundaries; the paragraph-start flag
       stays with its line).
  T2   reverse line order within every page (gap and paragraph flags move with their lines).
  T3g  shuffle page order across the manuscript, 20 seeds (random.Random(seed), seed = 1..20).
  T3q  shuffle page order within each quire (quires kept in order of first appearance), 20 seeds (same seeds).
  T4   reverse the character order of every word (EVA characters; multi-character glyphs such as ch are reversed as
       strings).  Every segmenter is refitted on the transformed text, so prefixes and suffixes swap roles; T4 values of
       segmenter-based statistics are reported as "refit".
  Reported only (no classification): T14 = T1+T4 (each line read right to left, glyphs too); T124 = T1+T2+T4 (each
       page read right to left from the bottom).
  Train / held-out split.  The s55 and s69 statistics use an 80/20 page split drawn from the page ORDER
  (random.Random(20261017).shuffle).  T1, T2 and T4 keep the page order, so the split is unchanged.  Under T3 the split
  is held fixed by page id (the T0 split; implemented by temporarily replacing s69.split_pages / s55.split_pages with
  a lookup of the T0 training ids during T3 cells; the scoring code is unchanged), so that page order, not a new
  split, is what T3 varies.  The s56 / carryover segmenter is fitted on the same T0 training pages (s69.split_pages,
  identical to g1_edge_joint.split_names) and reused under T3.

STATISTICS (the original scoring functions are imported unchanged; their own nulls are used):
  A1_ff  line-initial JSD excess: a2_position.stats(lines, w[0])[0] - mean of a2_position.null(lines, w[0], n=30)[:, 0]
         (s44 / s32 estimator; first glyph of the line's first word vs mid-line words, lines >= 3 words).
  A1_lf  the same feature on the line's LAST word (a2.stats(...)[1]) = mirror of A1_ff under T1.
  A1_fl  the last glyph (w[-1]) of the line's first word = mirror of A1_ff under T4.
  A2_ll  line-final JSD excess: last glyph of the line's last word (the A2 m/g line-final set) = mirror under T1+T4.
  A3_cp  cross-space coupling: metrics_new._mi_shuffle_corrected(last glyph of w_j, first glyph of w_j+1, rng, 20)
         within lines (excess over a permutation null; full text, not the filed A/B halves, so no reproduction).
  A3_cpm its mirror pairing (first glyph of w_j, last glyph of w_j+1) = mirror of A3_cp under T1 and under T4.
  A5_I   within-line Moran I on word length: s21.materialize + s21.moran_for_pairs (raw I, as filed 0.157); the
         within-line shuffle null mean (200 draws, s21's lexsort method) is printed beside.
  A13_Ic within-line Moran I on CORE length (s56-style SlotSegmenter on T0 / cell training pages) [A13 proxy].
  f2     s55 f2_core_core: TextData.core_core on held-out lines, 200 within-line shuffles, rng default_rng(20261017).
  f1     s55 f1_core_F1 (core-stream held-out word-order residual, n1 page_sums) [A7 / A16 proxy].
  f4     s55 f4_prefix_gain: s55.gain_pages on training / held-out prefix lines.
  f4b    the same on every line reversed = the "next-prefix" gain (mirror of f4 under T1).
  s4     the same on the suffix stream (mirror of f4 under T4: a reversed word's prefix is its suffix).
  M1     s69 M1 gain (s69.Text + s69.compute + s69.all_values); mirrors as f4 (M1 == f4 by construction; T1 -> f4b,
         T4 -> s4).
  bpos   s69 b_pos: matched line-reset gain across the line break (last prefix of line n -> first prefix of line n+1).
  b, d   s69 b (unmatched line break) and d (ordinary within-line pairs), reported beside.
  R1..R5 s56 core repetition ratio R(d), d = 1..5, crossing-line page stream (s56.to_units / profile / ratios / boot,
         200 within-page shuffles, seed 20261017, CI seed 20261018).
  sx     s56 same-index line-above echo (token-index proxy of s35's same-x; R = obs / shuffle expectation).
  EchoA  s42 pixel same-x line-above echo (ZL3b only, m1_coordinates.build_pages, s42.count_hits; edit <= 1 hits):
         excess hit rate = 100 x (obs hits / probes - null hits / null probes), null = s42's within-page random
         other line, 200 draws, random.Random(20261017).
  EchoB  the same with the line BELOW (no + 1) = EchoA under T2.  Computed on T0 only: physical x does not change
         under T1, T4 leaves Levenshtein <= 1 unchanged, T3 is within-page; so EchoA is order-free by construction
         under T1 / T3 / T4 and its T2 value IS EchoB.
  carry  cross-page rare-core carryover [NEW s79 statistic; neither s56 nor s62 files one -- s56 never joins pages,
         s59/s62 use a random OTHER page as a null]: share of rare-core tokens (core type not among the cell's 20
         most frequent cores) on page i whose core type occurs on page i-1, pooled over i >= 1 in the cell's page order.
  drJ    page drift smoothness [NEW]: mean over consecutive pages of a2_position.jsd(glyph unigram counts).
  drR    drift monotonicity [NEW; Parisel switch, dot 24]: Spearman rho between page position and the page's
         f = n_cho / (n_cho + n_che) (s68.classify word rule; pages with n >= 5).  n/a under T4 (the rule reads
         glyph patterns; page-level by construction).
  s67-style LOQO fold scoring: order-free by construction (folds are whole quires; nothing reads page order) -> noted,
  not rerun.
INTERVALS: 95 % percentile interval over 500 subsamples of round(0.8 n) pages without replacement
  (np.random.default_rng(20261017) per statistic family).  Split-based families subsample held-out pages; s56 uses
  s56.boot (seed 20261018); carry / drJ subsample the receiving pages i >= 1; drR subsamples pages (order kept).
  Subsample values of A1 use the same 30 a2 null shuffles summed per page (checked equal to a2 at the full set);
  subsample coupling uses s55.mi_codes with 5 permutations per draw.  T3: the spread (min / median / max) over the 20
  seeds for carry / drJ / drR.  Every other statistic's code never reads page order (it pools lines, line pairs or
  within-page streams): under T3 it is computed on seed 1 of T3g and of T3q only, with the split fixed (the 'spread'
  is then one value), and is order-free under T3 by construction up to null-RNG consumption order.

PRE-REGISTERED CLASSIFICATION (per statistic S, transliteration, transformation T):
  "order-free"      S(T) lies inside the T0 interval of S.  (T3: the median over the 20 seeds.)
  "mirrored"        otherwise, T in {T1, T2, T4}, S has a declared mirror S' for T, S'(T) lies inside the T0 interval of
                    S and S(T) lies inside the T0 interval of S'.  For T1 and T2 every statistic's declared mirror is
                    the statistic read in the reversed direction ("BC": by construction S'(T) = S(T0) exactly, because
                    T1 and T2 are involutions with nothing refitted), so under T1 / T2 a statistic is either
                    order-free or mirrored.  Under T4 the segmenter is refitted; declared mirrors there are the
                    natural ones (A1_ff <-> A1_fl, A1_lf <-> A2_ll, A3_cp <-> A3_cpm, f4 / M1 <-> s4); every other
                    segmenter statistic has no T4 mirror.
  "order-dependent" otherwise.
  T3 detail (added before the freeze after the first fixture run, where a chance drift rho in the no-drift text sat
  just outside its under-dispersed subsample interval): a T3 call is "order-free" if the seed median lies inside the
  T0 interval OR the T0 value lies inside the [min, max] spread of the 20 seeds; statistics whose code never reads
  page order are "order-free (BC)" under T3 (their seed-1 value is printed as a check).
  Reported flag, not in the rule: a non-order-free call is starred (*) "marginal" when |S(T) - S(T0)| is less than
  twice the T0 interval half-width (the 80 % subsample interval is about half a sampling interval).
  Per transliteration and overall: a dependency counts overall when it holds on >= 2 of the 3 transliterations.
  Constraint table: each constraint takes the statistics listed in CONSTRAINT_MAP below.  Its class is "order-free"
  if no statistic moves under any T; otherwise every applicable label: within-line-direction dependent (T1),
  line-order dependent (T2), page-order dependent (T3g / T3q), glyph-direction dependent (T4), each with
  (mirrored) or (order-dependent).  Constraints with no recomputable statistic: "not re-tested" with the reason, or
  "order-free by construction" where the filed statistic reads no order at all.
DIRECTION EVIDENCE (descriptive, no verdict): T0 sizes of A1_ff / A1_lf / A1_fl / A2_ll with intervals; gallows
  (k t p f) share of the first vs last word on paragraph-start lines and other lines, and where it sits under T1;
  words per paragraph-first vs paragraph-last line; f4 vs f4b; A3_cp vs A3_cpm; EchoA vs EchoB; sx under T1 (right-
  aligned echo).  Inference only.
REPRODUCTION CHECK (stop rule): on ZL3b T0, A1_ff (filed loader) must be +0.1740 +/- 0.0015, M1 +0.0999 +/- 0.00005,
  f2 -0.0528 +/- 0.00005.  If any fails: print the values, write results_s79.txt with STOPPED and exit 3.
FIXTURE (--fixture): FXa = planted line-initial first-glyph marker (left-to-right asymmetry), planted page drift
  (cho share rises with page index) and planted rare-core carryover between consecutive pages; FXb = same line marker,
  no drift, no carryover.  Required: A1_ff under T1 = mirrored and under T2 / T3g = order-free (both texts); drR and
  carry under T3g = order-dependent on FXa; drR under T3g = order-free on FXb; A5_I order-free under T1 / T2 / T3g / T4.
Constraints: python -I, one CPU process, no new data; writes ONLY results_s79.txt and runs/s79/ (fixture: only
  runs/s79/fixture.txt).  Wall limit 45 min (T14 / T124 skipped if past 30 min).
Run: python -I s79_reading_order_audit.py            Fixture: python -I s79_reading_order_audit.py --fixture
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
from collections import Counter, OrderedDict, defaultdict
from contextlib import contextmanager
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

FIXTURE = "--fixture" in sys.argv
_ARGV = sys.argv[:]
sys.argv = [a for a in sys.argv if a != "--fixture"]   # imported scripts (s55, s69) read --fixture at import time;
                                                        # hide it so they load in their real-run configuration
import a2_position as a2  # noqa: E402
import m1_coordinates as m1  # noqa: E402  (imported at the top so the stub covers it and its imports)
import s21_moran_realline as s21  # noqa: E402
import s42_recency_by_layer as s42  # noqa: E402
import s55_code_vs_generator as s55  # noqa: E402
import s56_core_repetition_lag as s56  # noqa: E402
import s68_parisel_switch_within_hand as s68  # noqa: E402
import s69_prefix_stream_memory as s69  # noqa: E402
from scoreboard import metrics_new as MN  # noqa: E402

sys.argv = _ARGV

SELF = ROOT / "s79_reading_order_audit.py"
STUB = ROOT / "s79_reading_order_audit.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s79"
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / "results_s79.txt"
SEED = 20261017
B_SUB = 500
SUB_FRAC = 0.8
A1_NULL = 30
MORAN_NULL = 200
F2_SHUF = 200
F2_SHUF_SUB = 20
CP_NULL = 20
CP_NULL_SUB = 5
T3_SEEDS = list(range(1, 21))
TOPRARE = 20
DRR_MIN = 5
WALL = 45 * 60
EXTRA_CUTOFF = 30 * 60
EMPTY = "∅"
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
GALLOWS = set("ktpf")
CLASSIFIED = ["T1", "T2", "T3g", "T3q", "T4"]
EXTRA = ["T14", "T124"]
REPRO = {"A1_ff": (0.1740, 0.0015), "M1": (0.0999, 0.00005), "f2": (-0.0528, 0.00005)}

STATS = OrderedDict([
    ("A1_ff", "line-initial JSD excess (first glyph, first word)"),
    ("A1_lf", "first glyph, LAST word (T1 mirror of A1_ff)"),
    ("A1_fl", "last glyph, first word (T4 mirror of A1_ff)"),
    ("A2_ll", "line-final JSD excess (last glyph, last word)"),
    ("A3_cp", "cross-space coupling MI excess (last glyph -> next first glyph)"),
    ("A3_cpm", "mirror pairing (first glyph -> next last glyph)"),
    ("A5_I", "within-line Moran I, word length (raw)"),
    ("A13_Ic", "within-line Moran I, core length (raw)"),
    ("f2", "s55 f2 core->core MI excess (held-out)"),
    ("f1", "s55 f1 core-stream F1 residual (held-out)"),
    ("f4", "s55 f4 prefix gain (held-out)"),
    ("f4b", "next-prefix gain (lines reversed)"),
    ("s4", "suffix-stream gain"),
    ("M1", "s69 M1 gain"),
    ("bpos", "s69 b_pos matched line-break gain"),
    ("b", "s69 b line-break gain (M1 conditional)"),
    ("d", "s69 d ordinary within-line gain"),
    ("R1", "s56 R(1) core, crossing lines"),
    ("R2", "s56 R(2)"), ("R3", "s56 R(3)"), ("R4", "s56 R(4)"), ("R5", "s56 R(5)"),
    ("sx", "s56 same-index line-above echo ratio"),
    ("EchoA", "s42 pixel same-x echo, line above (excess hit %)"),
    ("EchoB", "s42 pixel same-x echo, line below (excess hit %)"),
    ("carry", "cross-page rare-core carryover share [new]"),
    ("drJ", "consecutive-page glyph JSD [new]"),
    ("drR", "Spearman rho page position vs cho share [new]"),
])
REPORT_ONLY = {"b", "d", "EchoB"}
# declared mirrors: T1 / T2 -> "BC" for every statistic; T4 -> natural mirrors only
T4_MIRROR = {"A1_ff": "A1_fl", "A1_fl": "A1_ff", "A1_lf": "A2_ll", "A2_ll": "A1_lf", "A3_cp": "A3_cpm",
             "A3_cpm": "A3_cp", "f4": "s4", "s4": "f4", "M1": "s4"}
# statistics whose code never reads page order (T3 computed on seed 1 only; the rest by construction)
T3_SEED1_ONLY = {"f2", "f1", "f4", "f4b", "s4", "M1", "bpos", "b", "d", "R1", "R2", "R3", "R4", "R5", "sx", "A13_Ic",
                 "A1_ff", "A1_lf", "A1_fl", "A2_ll", "A3_cp", "A3_cpm", "A5_I"}

CONSTRAINT_MAP = OrderedDict([
    ("A1", (["A1_ff"], "")),
    ("A2", (["A1_ff", "A2_ll"], "paragraph-first JSD split not recomputed; gallows position in direction evidence")),
    ("A3", (["A3_cp"], "full-text coupling (filed numbers are A/B halves)")),
    ("A4", ([], "not re-tested: a statement about built texts' edge tables, not about the transliteration")),
    ("A5", (["A5_I"], "")),
    ("A6", ([], "not re-tested in s79: CHARWIN is computable but not rerun (character model; T4-sensitive by design)")),
    ("A7", (["f1"], "proxy: s55 core-stream F1, not the n6 word-level F1")),
    ("A8", ([], "order-free by construction: section NMI is a bag of tokens per page (no order read); not rerun")),
    ("A9", ([], "not re-tested: entropy / type counts under alphabets; type counts are order-free by construction")),
    ("A10", (["A1_ff", "A3_cp", "A5_I"], "widths inherit A1 / A3 / A5")),
    ("A11", ([], "not re-tested: literature / period bound")),
    ("A12", ([], "not re-tested: board classifier over many entrants")),
    ("A13", (["A5_I", "A13_Ic"], "core-length Moran as the slot-ablation proxy")),
    ("A14", (["f2", "f4"], "")),
    ("A15", (["EchoA", "carry"], "physical layout parts (drawing gaps, bifolio clustering) not re-tested; echo = m1 recency")),
    ("A16", (["f2", "f1"], "")),
    ("A17", ([], "not re-tested: producer reachability")),
    ("A18", ([], "not re-tested: framing / producer failures")),
    ("A19", ([], "order-free by construction: ink-gap vs space agreement is per gap; not rerun")),
    ("A20", ([], "not re-tested: bag of tokens per hand (order-free in line / page order by construction) but the "
                 "slot profiles depend on the segmenter's direction (T4) -- untested")),
    ("A21", ([], "not re-tested: s63 parser heuristics (segmenter-direction dependent by design)")),
    ("dot15", (["f2", "f4"], "f5a (type cover) is order-free by construction")),
    ("dot16", (["R1", "R2", "R3", "R4", "R5"], "")),
    ("dot17", ([], "not re-tested: s52-s54 (comparators, error battery, length persistence)")),
    ("dot18", ([], "not re-tested: producer (s57)")),
    ("dot19", ([], "not re-tested: producer (s58)")),
    ("dot20", ([], "not re-tested: s59/s62 parent window = PRECEDING 15 tokens + line above, directional by design; "
                   "the cross-page analogue is 'carry'")),
    ("dot21", ([], "not re-tested: producers (s57, s58, s61)")),
    ("dot22", (["f4"], "rests on prefix-stream order")),
    ("dot23", ([], "order-free by construction (LOQO folds are quires; per task, not rerun)")),
    ("dot24", (["drR", "drJ"], "")),
    ("dot25", (["M1", "bpos"], "")),
    ("dot26", ([], "not re-tested: solver ladder on planted ciphers")),
])
LABEL = {"T1": "within-line-direction dependent", "T2": "line-order dependent", "T3g": "page-order dependent (global)",
         "T3q": "page-order dependent (within quire)", "T4": "glyph-direction dependent"}

log: list[str] = []
T0CLK = time.time()


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


def nan():
    return float("nan")


def pct(v):
    v = np.array([x for x in v if x is not None and np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return (nan(), nan())
    return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))


# ======================================================================= transformations
def copy_page(p, **kw):
    q = dict(p)
    q.update(kw)
    return q


def t1(pages):
    out = []
    for p in pages:
        lines = [ln[::-1] for ln in p["lines"]]
        kw = dict(lines=lines)
        if p.get("gaps") is not None:
            ng = []
            for g in p["gaps"]:
                L = len(g)
                ng.append([False] + [bool(g[L - j]) for j in range(1, L)])
            kw["gaps"] = ng
        out.append(copy_page(p, **kw))
    return out


def t2(pages):
    out = []
    for p in pages:
        kw = dict(lines=p["lines"][::-1])
        if p.get("gaps") is not None:
            kw["gaps"] = p["gaps"][::-1]
        if p.get("para") is not None:
            kw["para"] = p["para"][::-1]
        out.append(copy_page(p, **kw))
    return out


def t4(pages):
    return [copy_page(p, lines=[[w[::-1] for w in ln] for ln in p["lines"]]) for p in pages]


def t3_order(meta_pages, seed, mode):
    """-> list of page ids in the shuffled order."""
    rng = random.Random(seed)
    ids = [p["id"] for p in meta_pages]
    if mode == "g":
        ids = ids[:]
        rng.shuffle(ids)
        return ids
    groups = OrderedDict()
    for p in meta_pages:
        groups.setdefault(p.get("quire", "?"), []).append(p["id"])
    out = []
    for q, g in groups.items():
        g = g[:]
        rng.shuffle(g)
        out.extend(g)
    return out


def reorder(pages, order):
    by = {p["id"]: p for p in pages}
    out = [by[i] for i in order if i in by]
    seen = set(order)
    out += [p for p in pages if p["id"] not in seen]
    return out


def apply(name, pages):
    if name == "T0":
        return pages
    if name == "T1":
        return t1(pages)
    if name == "T2":
        return t2(pages)
    if name == "T4":
        return t4(pages)
    if name == "T14":
        return t4(t1(pages))
    if name == "T124":
        return t4(t2(t1(pages)))
    raise ValueError(name)


@contextmanager
def fixed_split(ids69, ids55):
    o69, o55 = s69.split_pages, s55.split_pages
    s69.split_pages = lambda pages: set(p["id"] for p in pages if p["id"] in ids69)
    s55.split_pages = lambda pages: ([p for p in pages if p["id"] in ids55], [p for p in pages if p["id"] not in ids55])
    try:
        yield
    finally:
        s69.split_pages, s55.split_pages = o69, o55


# ======================================================================= families
def jsd_np(P, Q):
    P = P.astype(float); Q = Q.astype(float)
    if P.sum() <= 0 or Q.sum() <= 0:
        return nan()
    keep = (P > 0) | (Q > 0)
    P = P[keep] / P.sum(); Q = Q[keep] / Q.sum()
    M = (P + Q) / 2

    def kl(a, b):
        m = a > 0
        return float(np.sum(a[m] * np.log2(a[m] / b[m])))
    return (kl(P, M) + kl(Q, M)) / 2


def a1_tables(lines, pid, P, feat):
    vocab = {}
    obs = defaultdict(int)
    for ws, pi in zip(lines, pid):
        if len(ws) < 3:
            continue
        obs[(pi, 0, vocab.setdefault(feat(ws[0]), len(vocab)))] += 1
        obs[(pi, 2, vocab.setdefault(feat(ws[-1]), len(vocab)))] += 1
        for w in ws[1:-1]:
            obs[(pi, 1, vocab.setdefault(feat(w), len(vocab)))] += 1
    nul = defaultdict(int)
    for i in range(A1_NULL):          # a2_position.null: rng = random.Random(i) per draw, every line shuffled in order
        rng = random.Random(i)
        for ws, pi in zip(lines, pid):
            ws = ws[:]
            rng.shuffle(ws)
            if len(ws) < 3:
                continue
            nul[(i, pi, 0, vocab.setdefault(feat(ws[0]), len(vocab)))] += 1
            nul[(i, pi, 2, vocab.setdefault(feat(ws[-1]), len(vocab)))] += 1
            for w in ws[1:-1]:
                nul[(i, pi, 1, vocab.setdefault(feat(w), len(vocab)))] += 1
    F = len(vocab)
    O = np.zeros((P, 3, F)); N = np.zeros((A1_NULL, P, 3, F))
    for (pi, s, f), c in obs.items():
        O[pi, s, f] = c
    for (i, pi, s, f), c in nul.items():
        N[i, pi, s, f] = c
    return O, N


def a1_values(O, N, sel=None):
    o = O.sum(0) if sel is None else O[sel].sum(0)
    n = N.sum(1) if sel is None else N[:, sel].sum(1)
    first = jsd_np(o[0], o[1]) - float(np.mean([jsd_np(n[i, 0], n[i, 1]) for i in range(len(n))]))
    last = jsd_np(o[2], o[1]) - float(np.mean([jsd_np(n[i, 2], n[i, 1]) for i in range(len(n))]))
    return first, last


def fam_edges(pages, intervals=True, check_a2=True):
    """A1 family, coupling, Moran (words), gallows / paragraph descriptives."""
    R, CI, INFO = {}, {}, {}
    P = len(pages)
    lines = [ln for p in pages for ln in p["lines"]]
    pid = [i for i, p in enumerate(pages) for _ln in p["lines"]]
    g0, g1 = (lambda w: w[0]), (lambda w: w[-1])
    O0, N0 = a1_tables(lines, pid, P, g0)
    O1, N1 = a1_tables(lines, pid, P, g1)
    R["A1_ff"], R["A1_lf"] = a1_values(O0, N0)
    R["A1_fl"], R["A2_ll"] = a1_values(O1, N1)
    if check_a2:   # the original functions at the full set
        r0 = a2.stats(lines, g0); n0 = a2.null(lines, g0, n=A1_NULL)
        r1 = a2.stats(lines, g1); n1 = a2.null(lines, g1, n=A1_NULL)
        orig = dict(A1_ff=r0[0] - n0[:, 0].mean(), A1_lf=r0[1] - n0[:, 1].mean(),
                    A1_fl=r1[0] - n1[:, 0].mean(), A2_ll=r1[1] - n1[:, 1].mean())
        INFO["a2_check"] = max(abs(orig[k] - R[k]) for k in orig)
        for k in orig:
            R[k] = float(orig[k])
    # coupling
    A, B, Am, Bm, cpg = [], [], [], [], []
    for i, p in enumerate(pages):
        for ln in p["lines"]:
            for u, v in zip(ln, ln[1:]):
                A.append(u[-1]); B.append(v[0]); Am.append(u[0]); Bm.append(v[-1]); cpg.append(i)
    R["A3_cp"] = MN._mi_shuffle_corrected(A, B, np.random.default_rng(SEED), n_null=CP_NULL)[1]
    R["A3_cpm"] = MN._mi_shuffle_corrected(Am, Bm, np.random.default_rng(SEED), n_null=CP_NULL)[1]
    # Moran (words)
    dat = s21.materialize(pages)
    R["A5_I"] = s21.moran_for_pairs(dat["x"], dat["left"], dat["right"])
    rng = np.random.default_rng(SEED)
    nl = []
    for _ in range(MORAN_NULL):
        perm = np.lexsort((rng.random(len(dat["x"])), dat["line_id"]))
        nl.append(s21.moran_for_pairs(dat["x"][perm], dat["left"], dat["right"]))
    INFO["A5_null_mean"] = float(np.mean(nl))
    # descriptives
    INFO.update(edge_descriptives(pages))
    if intervals:
        rng = np.random.default_rng(SEED)
        m = int(round(SUB_FRAC * P))
        enc = {}
        Ai = np.array([enc.setdefault(x, len(enc)) for x in A], dtype=np.int64)
        Bi = np.array([enc.setdefault(x, len(enc)) for x in B], dtype=np.int64)
        Ami = np.array([enc.setdefault(x, len(enc)) for x in Am], dtype=np.int64)
        Bmi = np.array([enc.setdefault(x, len(enc)) for x in Bm], dtype=np.int64)
        cpg = np.array(cpg)
        sub = defaultdict(list)
        for _ in range(B_SUB):
            sel = np.sort(rng.choice(P, size=m, replace=False))
            a, b = a1_values(O0, N0, sel); sub["A1_ff"].append(a); sub["A1_lf"].append(b)
            a, b = a1_values(O1, N1, sel); sub["A1_fl"].append(a); sub["A2_ll"].append(b)
            msk = np.isin(cpg, sel)
            for key, x, y in (("A3_cp", Ai, Bi), ("A3_cpm", Ami, Bmi)):
                xx, yy = x[msk], y[msk]
                sub[key].append(s55.mi_codes(xx, yy) - float(np.mean([s55.mi_codes(xx, rng.permutation(yy)) for _ in range(CP_NULL_SUB)])))
            d = s21.materialize([pages[i] for i in sel])
            sub["A5_I"].append(s21.moran_for_pairs(d["x"], d["left"], d["right"]))
        for k, v in sub.items():
            CI[k] = pct(v)
    return R, CI, INFO


def edge_descriptives(pages):
    gal = lambda w: any(c in GALLOWS for c in w)
    c = Counter()
    lens = defaultdict(list)
    for p in pages:
        para = p.get("para")
        n = len(p["lines"])
        for li, ln in enumerate(p["lines"]):
            ps = bool(para[li]) if para is not None else False
            key = "par" if ps else "oth"
            c[key + "_n"] += 1
            c[key + "_gfirst"] += gal(ln[0])
            c[key + "_glast"] += gal(ln[-1])
            if para is not None:
                nxt_par = (li + 1 < n and bool(para[li + 1])) or li == n - 1
                if ps:
                    lens["par_first"].append(len(ln))
                if nxt_par:
                    lens["par_last"].append(len(ln))
                if not ps and not nxt_par:
                    lens["par_mid"].append(len(ln))
    out = {}
    for k in ("par", "oth"):
        n = c[k + "_n"]
        out[f"{k}_lines"] = n
        out[f"{k}_gal_first"] = c[k + "_gfirst"] / n if n else nan()
        out[f"{k}_gal_last"] = c[k + "_glast"] / n if n else nan()
    for k, v in lens.items():
        out[f"len_{k}"] = float(np.mean(v)) if v else nan()
    return out


def fit_seg(pages, train_ids):
    return MN.SlotSegmenter([w for p in pages if p["id"] in train_ids for ln in p["lines"] for w in ln])


def fam_s56(pages, seg, intervals=True):
    R, CI = {}, {}
    by = OrderedDict((p["id"], p["lines"]) for p in pages)
    bu = s56.to_units(by, "core", seg)
    st, _nt = s56.profile(bu, SEED)
    r = s56.ratios(st)
    for d in range(1, 6):
        R[f"R{d}"] = float(r["lag"][d - 1])
    R["sx"] = float(r["samex"][0])
    cpages = [dict(lines=[[seg.segment(w)[1] for w in ln] for ln in p["lines"]]) for p in pages]
    dat = s21.materialize(cpages)
    R["A13_Ic"] = s21.moran_for_pairs(dat["x"], dat["left"], dat["right"])
    if intervals:
        ci = s56.boot(st, SEED + 1)
        for d in range(1, 6):
            CI[f"R{d}"] = (float(ci["lag"][0][d - 1]), float(ci["lag"][1][d - 1]))
        CI["sx"] = (float(ci["samex"][0][0]), float(ci["samex"][1][0]))
        rng = np.random.default_rng(SEED)
        P = len(cpages); m = int(round(SUB_FRAC * P))
        v = []
        for _ in range(B_SUB):
            sel = np.sort(rng.choice(P, size=m, replace=False))
            d_ = s21.materialize([cpages[i] for i in sel])
            v.append(s21.moran_for_pairs(d_["x"], d_["left"], d_["right"]))
        CI["A13_Ic"] = pct(v)
    return R, CI


def spearman(x, y):
    def rank(a):
        a = np.asarray(a, float)
        o = np.argsort(a, kind="mergesort")
        r = np.empty(len(a))
        r[o] = np.arange(len(a), dtype=float)
        # average ties
        _, inv, cnt = np.unique(a, return_inverse=True, return_counts=True)
        sums = np.bincount(inv, weights=r)
        return (sums / cnt)[inv]
    if len(x) < 3:
        return nan()
    rx, ry = rank(x), rank(y)
    if rx.std() == 0 or ry.std() == 0:
        return nan()
    return float(np.corrcoef(rx, ry)[0, 1])


def order_prep(pages, seg, top):
    """Per page: rare-core token list, core-type set, glyph Counter, (n_cho, n_che)."""
    out = []
    for p in pages:
        cores = [seg.segment(w)[1] for ln in p["lines"] for w in ln]
        rare = [c for c in cores if c not in top]
        g = Counter(ch for ln in p["lines"] for w in ln for ch in w)
        cls = [s68.classify(w) for ln in p["lines"] for w in ln]
        out.append(dict(rare=rare, types=set(cores), glyph=g, cho=sum(1 for x in cls if x == 1), che=sum(1 for x in cls if x == 0)))
    return out


def order_values(prep, drr_ok=True, rng=None, intervals=False):
    P = len(prep)
    h = np.zeros(P); n = np.zeros(P); j = np.full(P, np.nan)
    for i in range(1, P):
        prev = prep[i - 1]["types"]
        n[i] = len(prep[i]["rare"])
        h[i] = sum(1 for c in prep[i]["rare"] if c in prev)
        j[i] = a2.jsd(prep[i]["glyph"], prep[i - 1]["glyph"])
    pos = np.arange(P, dtype=float)
    nn = np.array([q["cho"] + q["che"] for q in prep], dtype=float)
    f = np.array([q["cho"] / (q["cho"] + q["che"]) if (q["cho"] + q["che"]) else np.nan for q in prep])
    okp = nn >= DRR_MIN
    R = dict(carry=float(h[1:].sum() / n[1:].sum()) if n[1:].sum() else nan(), drJ=float(np.nanmean(j[1:])),
             drR=spearman(pos[okp], f[okp]) if drr_ok else nan())
    CI = {}
    if intervals:
        rcv = np.arange(1, P)
        m = int(round(SUB_FRAC * len(rcv)))
        mp = int(round(SUB_FRAC * P))
        sub = defaultdict(list)
        for _ in range(B_SUB):
            s = rng.choice(rcv, size=m, replace=False)
            sub["carry"].append(h[s].sum() / n[s].sum() if n[s].sum() else np.nan)
            sub["drJ"].append(float(np.nanmean(j[s])))
            sp = np.sort(rng.choice(P, size=mp, replace=False))
            k = sp[okp[sp]]
            sub["drR"].append(spearman(pos[k], f[k]) if drr_ok else np.nan)
        CI = {k: pct(v) for k, v in sub.items()}
    return R, CI


def fam_s55(name, pages, intervals=True):
    R, CI = {}, {}
    td = s55.TextData(name, pages)
    cores, _fr, lid, _sec, _pg = td.concat(td.hp)
    R["f2"] = td.core_core(cores, lid, F2_SHUF, np.random.default_rng(SEED))
    f1r = td.f1_rows()
    R["f1"] = s55.f1_stat(np.array(list(f1r.values())))
    suf_tr = [[td.sg(w)[2] or EMPTY for w in ln] for p in td.tr for ln in p["lines"]]
    suf_te = [(p["id"], [td.sg(w)[2] or EMPTY for w in ln]) for p in td.te for ln in p["lines"]]
    streams = dict(f4=(td.tr_pre_lines, td.te_pre_pl),
                   f4b=([l[::-1] for l in td.tr_pre_lines], [(p, l[::-1]) for p, l in td.te_pre_pl]),
                   s4=(suf_tr, suf_te))
    rows = {}
    for k, (tr, te) in streams.items():
        rows[k] = s55.gain_pages(tr, te)
        R[k] = s55.gain_stat(np.array(list(rows[k].values())))
    if intervals:
        ids = [h["id"] for h in td.hp]
        n = len(ids); m = int(round(SUB_FRAC * n))
        F1 = np.array([f1r.get(i, np.zeros(6)) for i in ids])
        G = {k: np.array([rows[k].get(i, np.zeros(3)) for i in ids]) for k in rows}
        rng = np.random.default_rng(SEED)
        sub = defaultdict(list)
        for _ in range(B_SUB):
            sel = np.sort(rng.choice(n, size=m, replace=False))
            c_, _f, l_, _s, _p = td.concat([td.hp[i] for i in sel])
            sub["f2"].append(td.core_core(c_, l_, F2_SHUF_SUB, rng))
            sub["f1"].append(s55.f1_stat(F1[sel]))
            for k in G:
                sub[k].append(s55.gain_stat(G[k][sel]))
        CI = {k: pct(v) for k, v in sub.items()}
    return R, CI, dict(train=sorted(p["id"] for p in td.tr), pfx=len(td.seg.prefixes), sfx=len(td.seg.suffixes))


def fam_s69(name, pages, intervals=True):
    t = s69.Text(name, pages)
    W = {k: t.A[k] for k in ("pre", "suf", "core", "cc", "gal")}
    st = s69.compute(t, W)
    v = s69.all_values(st)
    keys = {"M1": "M1", "bpos": "b_pos", "b": "b", "d": "d"}
    R = {k: float(v[s]) for k, s in keys.items()}
    CI = {}
    if intervals:
        rng = np.random.default_rng(SEED)
        P = t.n_te_pages; m = int(round(SUB_FRAC * P))
        sub = defaultdict(list)
        for _ in range(B_SUB):
            sel = rng.choice(P, size=m, replace=False)
            vv = s69.all_values(st, sel)
            for k, s in keys.items():
                sub[k].append(vv[s])
        CI = {k: pct(x) for k, x in sub.items()}
    return R, CI, dict(has_gaps=t.has_gaps, n_te=t.n_te_pages)


def fam_echo():
    """ZL3b T0 only (pixel boxes): EchoA (line above), EchoB (line below)."""
    toks = MN.flat_tokens(MN.voynich_pages("eva"))
    seg = MN.SlotSegmenter(toks)
    pages, _stats = m1.build_pages()
    fol = list(pages)
    obs = {}
    for key, off in (("EchoA", -1), ("EchoB", +1)):
        pr, ht = np.zeros(len(fol)), np.zeros(len(fol))
        for i, f in enumerate(fol):
            p, h = s42.count_hits({f: pages[f]}, m1, seg, lambda by_no, nos, no, off=off: by_no.get(no + off))
            pr[i] = p; ht[i] = sum(h.values())
        obs[key] = (pr, ht)
    rng = random.Random(SEED)
    npr, nht = np.zeros(len(fol)), np.zeros(len(fol))
    for _d in range(200):
        def prev_of(by_no, nos, no, rng=rng):
            others = [m for m in nos if m != no]
            return by_no[rng.choice(others)] if others else None
        for i, f in enumerate(fol):
            p, h = s42.count_hits({f: pages[f]}, m1, seg, prev_of)
            npr[i] += p; nht[i] += sum(h.values())
    R, CI, INFO = {}, {}, {}
    for key, (pr, ht) in obs.items():
        R[key] = 100 * (ht.sum() / pr.sum() - nht.sum() / npr.sum())
        INFO[key] = dict(probes=int(pr.sum()), hits=int(ht.sum()), rate=100 * ht.sum() / pr.sum(), null_rate=100 * nht.sum() / npr.sum())
    rngb = np.random.default_rng(SEED)
    m = int(round(SUB_FRAC * len(fol)))
    sub = defaultdict(list)
    for _ in range(B_SUB):
        sel = rngb.choice(len(fol), size=m, replace=False)
        nr = nht[sel].sum() / npr[sel].sum()
        for key, (pr, ht) in obs.items():
            sub[key].append(100 * (ht[sel].sum() / pr[sel].sum() - nr))
    CI = {k: pct(v) for k, v in sub.items()}
    INFO["pages"] = len(fol)
    return R, CI, INFO


# ======================================================================= one cell
def measure_cell(name, P69, P55, seg56_ids, top_fixed=None, seg_fixed=None, intervals=True, families=("edges", "s56", "order", "s55", "s69")):
    R, CI, INFO = {}, {}, {}
    if "edges" in families:
        r, c, i = fam_edges(P69, intervals=intervals, check_a2=True)
        R.update(r); CI.update(c); INFO.update(i)
    seg = seg_fixed if seg_fixed is not None else fit_seg(P69, seg56_ids)
    if "s56" in families:
        r, c = fam_s56(P69, seg, intervals=intervals)
        R.update(r); CI.update(c)
    if "order" in families:
        if top_fixed is None:
            fr = Counter(seg.segment(w)[1] for p in P69 for ln in p["lines"] for w in ln)
            top = set(c for c, _ in fr.most_common(TOPRARE))
        else:
            top = top_fixed
        drr_ok = not name.endswith(("T4", "T14", "T124"))
        r, c = order_values(order_prep(P69, seg, top), drr_ok=drr_ok, rng=np.random.default_rng(SEED), intervals=intervals)
        R.update(r); CI.update(c)
    if "s55" in families:
        r, c, i = fam_s55(name, P55, intervals=intervals)
        R.update(r); CI.update(c); INFO["s55"] = i
    if "s69" in families:
        r, c, i = fam_s69(name, P69, intervals=intervals)
        R.update(r); CI.update(c); INFO["s69"] = i
    return R, CI, INFO, seg


# ======================================================================= classification
def inside(x, ci):
    return ci is not None and np.isfinite(x) and np.isfinite(ci[0]) and ci[0] <= x <= ci[1]


def marginal(x0, x, ci):
    """Reported flag (not in the rule): |S(T) - S(T0)| < 2 x the T0 interval half-width.  The 80 % without-replacement
    subsample interval is about half a sampling interval (sqrt((1 - f) / f) = 0.5, s56), so such a move would sit
    inside a full-width interval."""
    if ci is None or not (np.isfinite(x0) and np.isfinite(x) and np.isfinite(ci[0])):
        return False
    hw = (ci[1] - ci[0]) / 2
    return hw > 0 and abs(x - x0) < 2 * hw


def classify(stat, T, val, cellT, CI0):
    if val is None or not np.isfinite(val) or stat not in CI0 or not np.isfinite(CI0[stat][0]):
        return "n/a"
    if inside(val, CI0[stat]):
        return "order-free"
    if T in ("T1", "T2"):
        return "mirrored"
    if T == "T4" and stat in T4_MIRROR:
        mk = T4_MIRROR[stat]
        mv = cellT.get(mk, nan())
        if mk in CI0 and inside(mv, CI0[stat]) and inside(val, CI0[mk]):
            return "mirrored"
    return "order-dependent"


# ======================================================================= data
def load_real(T):
    pages69, note69 = s69.voynich_pages(T)
    meta = json.loads((ROOT / "data" / "translit" / f"{TRANSLITS[T]}.meta.json").read_text(encoding="utf-8"))
    mby = {str(p["id"]): p for p in meta["pages"]}
    for p in pages69:
        m = mby.get(p["id"], {})
        for k in ("section", "quire", "hand", "lang"):
            p[k] = str(m.get(k, "?"))
    pages55 = s55.voynich_pages(T)
    return pages69, pages55, note69


def fixture_texts():
    """FXa: line-initial marker + page drift + carryover; FXb: line-initial marker only."""
    pfx = ["qo", "ch", "sh", "o", "d", "ol", ""]
    sfx = ["dy", "in", "y", "ol", "ar", ""]
    base = ["e", "ee", "a", "ai", "ar", "or", "eo", "ed", "es", "al"]

    def text(seed, drift):
        r = random.Random(seed)
        pages = []
        prev_rare = []
        for pi in range(96):
            share = (0.1 + 0.8 * pi / 95) if drift else 0.5
            rare_pool = [f"k{r.randrange(10**6)}t" for _ in range(6)]
            if drift and prev_rare:
                rare_pool = prev_rare[:4] + rare_pool[:2]
            prev_rare = rare_pool
            lines, para = [], []
            for li in range(12):
                L = r.randint(6, 10)
                ln = []
                for j in range(L):
                    if r.random() < 0.15:
                        core = r.choice(rare_pool)
                    else:
                        core = r.choice(base)
                    stem = ("cho" if r.random() < share else "che") if r.random() < 0.4 else r.choice(pfx)
                    w = stem + core + r.choice(sfx)
                    if j == 0 and r.random() < 0.7:
                        w = r.choice(["y", "s", "t"]) + w     # planted line-initial first-glyph marker
                    if j == 0 and li % 4 == 0:
                        w = "p" + w                           # paragraph-initial gallows
                    ln.append(w)
                lines.append(ln)
                para.append(li % 4 == 0)
            gaps = [[False] * len(l) for l in lines]
            pages.append(dict(id=f"p{pi:03d}", section="H" if pi < 48 else "B", quire=f"q{pi // 8:02d}", hand="1",
                              lang="A", lines=lines, gaps=gaps, para=para))
        return pages
    return OrderedDict([("FXa", text(31, True)), ("FXb", text(32, False))])


# ======================================================================= main
def fmt(x, nd=4):
    return "n/a" if x is None or not np.isfinite(x) else f"{x:+.{nd}f}"


def fmt_ci(ci, nd=4):
    return "[n/a]" if ci is None or not np.isfinite(ci[0]) else f"[{ci[0]:+.{nd}f}, {ci[1]:+.{nd}f}]"


def main():
    emit("S79: reading-order audit (T1 word order, T2 line order, T3 page order, T4 glyph order)"
         + ("  [SYNTHETIC FIXTURE, not reported]" if FIXTURE else ""))
    emit(f"date: {clock()}")
    emit(f"{SELF.name} sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name}" + (f" sha256={sha256(STUB)}" if STUB.exists() else " (absent)") + f"  stub_match={stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"python {sys.version.split()[0]}; numpy {np.__version__}; seed {SEED}; {B_SUB} subsamples of {SUB_FRAC:.0%} pages "
         f"without replacement; T3 seeds {T3_SEEDS[0]}..{T3_SEEDS[-1]}")
    emit()
    flush()

    texts = OrderedDict()
    if FIXTURE:
        for n, p in fixture_texts().items():
            p55 = [dict(id=q["id"], section=q["section"], lines=q["lines"]) for q in p]
            texts[n] = (p, p55, "synthetic")
    else:
        for T in TRANSLITS:
            p69, p55, note = load_real(T)
            texts[T] = (p69, p55, note)
    for n, (p69, p55, note) in texts.items():
        emit(f"  {n:6s} pages69 {len(p69)} tokens69 {sum(len(l) for p in p69 for l in p['lines'])}  pages55 {len(p55)} "
             f"tokens55 {sum(len(l) for p in p55 for l in p['lines'])}  {note}")
    emit()

    ALL = OrderedDict()      # (text, T) -> (R, CI, INFO)
    T3V = defaultdict(lambda: defaultdict(list))   # (text, mode) -> stat -> [values per seed]
    rows_csv = []
    first = True
    for n, (p69, p55, _note) in texts.items():
        if time.time() - T0CLK > WALL:
            emit(f"STOPPED: wall limit at {clock()}"); flush(); sys.exit(2)
        ids69 = s69.split_pages(p69)
        ids55 = set(p["id"] for p in s55.split_pages(p55)[0])
        R0, CI0, INFO0, seg0 = measure_cell(f"{n}_T0", p69, p55, ids69)
        ALL[(n, "T0")] = (R0, CI0, INFO0)
        emit(f"[{n} T0 done {time.time() - T0CLK:.0f}s; a2 check max |diff| {INFO0.get('a2_check', nan()):.2e}]")
        if first and not FIXTURE:
            first = False
            emit()
            emit("=== REPRODUCTION CHECK (ZL3b T0) ===")
            mp = MN.voynich_pages("eva")
            fl = [ln for q in mp for ln in q["lines"]]
            rr = a2.stats(fl, lambda w: w[0]); nn = a2.null(fl, lambda w: w[0], n=A1_NULL)
            a1_filed = float(rr[0] - nn[:, 0].mean())
            emit(f"  A1_ff filed loader (metrics_new.voynich_pages('eva'), {len(fl)} lines): {a1_filed:+.4f}; meta.json loader: "
                 f"{R0['A1_ff']:+.4f}; filed +0.1740 (results_s44.txt line 7)")
            emit(f"  M1 {R0['M1']:+.4f} (filed +0.0999, results_s69.txt); f2 {R0['f2']:+.4f} (filed -0.0528, results_s55.txt); "
                 f"f4 {R0['f4']:+.4f} (filed +0.0999)")
            emit(f"  beside (not in the stop rule): A5_I {R0['A5_I']:.6f} (filed 0.157244); R1..R5 core "
                 + " ".join(f"{R0[f'R{d}']:.3f}" for d in range(1, 6)) + " (filed 1.169 1.183 1.100 1.158 1.098)")
            ok = (abs(a1_filed - REPRO["A1_ff"][0]) <= REPRO["A1_ff"][1] and abs(R0["M1"] - REPRO["M1"][0]) <= REPRO["M1"][1]
                  and abs(R0["f2"] - REPRO["f2"][0]) <= REPRO["f2"][1])
            emit(f"  reproduction: {'PASS' if ok else 'FAIL'}")
            emit()
            flush()
            if not ok:
                emit(f"STOPPED: T0 does not reproduce the filed values (pre-registered stop rule); {clock()}")
                flush(); sys.exit(3)
            R0e, CI0e, INFOe = fam_echo()
            R0.update(R0e); CI0.update(CI0e); INFO0["echo"] = INFOe
            emit(f"[{n} echo done {time.time() - T0CLK:.0f}s]")
        for T in ("T1", "T2", "T4"):
            q69, q55 = apply(T, p69), apply(T, p55)
            R, CI, INFO, _s = measure_cell(f"{n}_{T}", q69, q55, ids69)
            ALL[(n, T)] = (R, CI, INFO)
            emit(f"[{n} {T} done {time.time() - T0CLK:.0f}s]")
            flush()
        fr = Counter(seg0.segment(w)[1] for p in p69 for ln in p["lines"] for w in ln)
        top0 = set(c for c, _ in fr.most_common(TOPRARE))
        for mode in ("g", "q"):
            for sd in T3_SEEDS:
                order = t3_order(p69, sd, mode)
                q69, q55 = reorder(p69, order), reorder(p55, order)
                fams = ("order",) if sd != T3_SEEDS[0] else ("edges", "s56", "order", "s55", "s69")
                with fixed_split(ids69, ids55):
                    R, _CI, _I, _s = measure_cell(f"{n}_T3{mode}", q69, q55, ids69, top_fixed=top0, seg_fixed=seg0,
                                                  intervals=False, families=fams)
                for k, v in R.items():
                    T3V[(n, mode)][k].append(v)
            emit(f"[{n} T3{mode} x{len(T3_SEEDS)} done {time.time() - T0CLK:.0f}s]")
            flush()
    # extras (reported only)
    if time.time() - T0CLK < EXTRA_CUTOFF:
        for n, (p69, p55, _note) in texts.items():
            ids69 = s69.split_pages(p69)
            for T in EXTRA:
                R, CI, INFO, _s = measure_cell(f"{n}_{T}", apply(T, p69), apply(T, p55), ids69, intervals=False)
                ALL[(n, T)] = (R, CI, INFO)
            emit(f"[{n} extras done {time.time() - T0CLK:.0f}s]")
    else:
        emit("extras T14 / T124 skipped (past the 30 min cutoff)")
    emit()

    names = list(texts)
    # T3 summary values (median over seeds)
    T3M = {}
    for (n, mode), d in T3V.items():
        T3M[(n, "T3" + mode)] = {k: float(np.nanmedian(v)) for k, v in d.items()}

    def val(n, T, k):
        if T.startswith("T3"):
            return T3M.get((n, T), {}).get(k, nan())
        return ALL.get((n, T), ({}, {}, {}))[0].get(k, nan())

    # ---------------- main numbers
    emit("=== MAIN NUMBERS: T0 point [95 % page-subsample interval] and transformed points ===")
    emit("  (T3g / T3q = median over 20 seeds; for statistics whose code never reads page order, T3 is seed 1 only)")
    for n in names:
        R0, CI0, _ = ALL[(n, "T0")]
        emit(f"--- {n} ---")
        emit(f"  {'stat':7s} {'T0':>9s} {'T0 interval':>22s} {'T1':>9s} {'T2':>9s} {'T3g':>9s} {'T3q':>9s} {'T4':>9s} {'T14':>9s} {'T124':>9s}")
        for k in STATS:
            if k not in R0:
                continue
            emit(f"  {k:7s} {fmt(R0[k]):>9s} {fmt_ci(CI0.get(k)):>22s} " + " ".join(
                f"{fmt(val(n, T, k)):>9s}" for T in ("T1", "T2", "T3g", "T3q", "T4", "T14", "T124")))
        emit()
    emit("=== T3 spread over seeds (min / median / max) ===")
    for (n, mode), d in T3V.items():
        for k, v in d.items():
            a = np.array(v, float)
            if len(a) > 1 and np.isfinite(a).any():
                emit(f"  {n:5s} T3{mode} {k:7s} n={len(a):2d} min {np.nanmin(a):+.4f} median {np.nanmedian(a):+.4f} max {np.nanmax(a):+.4f}"
                     f"   (T0 {fmt(ALL[(n, 'T0')][0].get(k, nan()))} {fmt_ci(ALL[(n, 'T0')][1].get(k))})")
    emit()

    # ---------------- per-statistic classification
    CLS = defaultdict(dict)   # (stat) -> (text, T) -> class
    emit("=== CLASSIFICATION PER STATISTIC (pre-registered rule) ===")
    emit(f"  {'stat':7s} " + " ".join(f"{n + ':' + T:>22s}" for n in names for T in CLASSIFIED))
    for k in STATS:
        if k in REPORT_ONLY:
            continue
        cells = []
        for n in names:
            R0, CI0, _ = ALL[(n, "T0")]
            for T in CLASSIFIED:
                if k in ("EchoA",):
                    if k not in R0:
                        c = "n/a"
                    elif T == "T2":
                        c = classify(k, T, R0.get("EchoB", nan()), {}, CI0)
                    else:
                        c = "order-free (BC)"
                elif T.startswith("T3"):
                    v = val(n, T, k)
                    if k in T3_SEED1_ONLY:
                        c = "order-free (BC)" if (not np.isfinite(v) or inside(v, CI0.get(k))) else "order-free (BC; s1 moved)"
                    else:
                        c = classify(k, T, v, {}, CI0)
                        arr = np.array(T3V[(n, T[2])].get(k, []), float)
                        x0 = R0.get(k, nan())
                        if c == "order-dependent" and np.isfinite(arr).any() and np.nanmin(arr) <= x0 <= np.nanmax(arr):
                            c = "order-free"
                    if c not in ("order-free", "order-free (BC)", "n/a") and marginal(R0.get(k, nan()), v, CI0.get(k)):
                        c += "*"
                else:
                    cellT = ALL[(n, T)][0]
                    v = cellT.get(k, nan())
                    c = classify(k, T, v, cellT, CI0)
                    if c not in ("order-free", "n/a") and marginal(R0.get(k, nan()), v, CI0.get(k)):
                        c += "*"
                CLS[k][(n, T)] = c
                cells.append(c)
        emit(f"  {k:7s} " + " ".join(f"{c:>22s}" for c in cells))
    emit()

    def overall(k, T):
        cs = [CLS[k].get((n, T), "n/a") for n in names]
        cs2 = [c.replace(" (BC; s1 moved)", "").replace(" (BC)", "").rstrip("*") for c in cs if c != "n/a"]
        if not cs2:
            return "n/a"
        dep = [c for c in cs2 if c != "order-free"]
        if len(dep) >= 2 or (len(cs2) == 1 and dep):
            return Counter(dep).most_common(1)[0][0]
        return "order-free"

    emit("=== CONSTRAINT TABLE (a dependency counts when it holds on >= 2 of the 3 texts) ===")
    TABLE = OrderedDict()
    for cname, (keys, note) in CONSTRAINT_MAP.items():
        if not keys:
            klass = note.split(":")[0]
            TABLE[cname] = dict(cls=klass, stats=[], detail=note)
            emit(f"  {cname:6s} {klass:28s} -- {note}")
            continue
        labs = []
        per = []
        for T in CLASSIFIED:
            hits = []
            for k in keys:
                o = overall(k, T)
                per.append(f"{k}:{T}={o}")
                if o not in ("order-free", "n/a"):
                    hits.append(f"{k} {o}")
            if hits:
                labs.append(f"{LABEL[T]} ({'; '.join(hits)})")
        klass = "order-free" if not labs else " + ".join(labs)
        TABLE[cname] = dict(cls=klass, stats=keys, detail=note, per=per)
        emit(f"  {cname:6s} {klass}" + (f"   [{note}]" if note else ""))
    emit()

    # ---------------- direction evidence
    emit("=== DIRECTION EVIDENCE (descriptive, no verdict) ===")
    for n in names:
        R0, CI0, I0 = ALL[(n, "T0")]
        emit(f"--- {n} ---")
        emit("  line-edge marking at T0 (JSD excess vs mid-line, [interval]):")
        for k in ("A1_ff", "A1_lf", "A1_fl", "A2_ll"):
            emit(f"    {k:6s} {fmt(R0[k])} {fmt_ci(CI0.get(k))}   {STATS[k]}")
        ov = lambda a, b: not (CI0[a][1] < CI0[b][0] or CI0[b][1] < CI0[a][0])
        emit(f"    line-start (A1_ff) vs line-end (A2_ll) intervals overlap: {ov('A1_ff', 'A2_ll')}; "
             f"A1_ff vs its T1 mirror A1_lf overlap: {ov('A1_ff', 'A1_lf')}")
        emit(f"  gallows word share: paragraph-start lines (n={I0.get('par_lines')}) first word {fmt(I0.get('par_gal_first', nan()), 3)}, "
             f"last word {fmt(I0.get('par_gal_last', nan()), 3)}; other lines (n={I0.get('oth_lines')}) first {fmt(I0.get('oth_gal_first', nan()), 3)}, "
             f"last {fmt(I0.get('oth_gal_last', nan()), 3)}")
        I1 = ALL[(n, "T1")][2]
        emit(f"    under T1 the paragraph-start lines' gallows sit at: first word {fmt(I1.get('par_gal_first', nan()), 3)}, last word {fmt(I1.get('par_gal_last', nan()), 3)}")
        emit(f"  words per line: paragraph-first {fmt(I0.get('len_par_first', nan()), 2)}, paragraph-last {fmt(I0.get('len_par_last', nan()), 2)}, "
             f"paragraph-internal {fmt(I0.get('len_par_mid', nan()), 2)}")
        emit(f"  prefix stream forward f4 {fmt(R0['f4'])} {fmt_ci(CI0.get('f4'))} vs backward f4b {fmt(R0['f4b'])} {fmt_ci(CI0.get('f4b'))}; "
             f"suffix stream s4 {fmt(R0['s4'])} {fmt_ci(CI0.get('s4'))}")
        emit(f"  coupling facing edges A3_cp {fmt(R0['A3_cp'])} {fmt_ci(CI0.get('A3_cp'))} vs outer edges A3_cpm {fmt(R0['A3_cpm'])} {fmt_ci(CI0.get('A3_cpm'))}")
        emit(f"  same-index echo left-aligned sx {fmt(R0['sx'], 3)} {fmt_ci(CI0.get('sx'), 3)} vs right-aligned (sx under T1) {fmt(ALL[(n, 'T1')][0].get('sx', nan()), 3)}")
        if "EchoA" in R0:
            e = I0["echo"]
            emit(f"  pixel echo: line above {fmt(R0['EchoA'], 3)} {fmt_ci(CI0.get('EchoA'), 3)} (obs {e['EchoA']['rate']:.2f} % vs null {e['EchoA']['null_rate']:.2f} %, "
                 f"{e['EchoA']['probes']} probes); line below {fmt(R0['EchoB'], 3)} {fmt_ci(CI0.get('EchoB'), 3)} (obs {e['EchoB']['rate']:.2f} %)")
        emit(f"  line-break reset bpos T0 {fmt(R0['bpos'])} {fmt_ci(CI0.get('bpos'))}; T1 {fmt(val(n, 'T1', 'bpos'))}; T2 {fmt(val(n, 'T2', 'bpos'))}; "
             f"T124 (page read backwards) {fmt(val(n, 'T124', 'bpos'))}")
        emit(f"  page order: carry T0 {fmt(R0['carry'])} {fmt_ci(CI0.get('carry'))} vs T3g median {fmt(val(n, 'T3g', 'carry'))}, T3q {fmt(val(n, 'T3q', 'carry'))}; "
             f"drR T0 {fmt(R0['drR'])} vs T3g {fmt(val(n, 'T3g', 'drR'))}, T3q {fmt(val(n, 'T3q', 'drR'))}; drJ T0 {fmt(R0['drJ'])} vs T3g {fmt(val(n, 'T3g', 'drJ'))}, T3q {fmt(val(n, 'T3q', 'drJ'))}")
        emit()

    if FIXTURE:
        emit("=== FIXTURE CHECK ===")
        checks = []
        for n in ("FXa", "FXb"):
            checks.append((f"{n} A1_ff T1 = mirrored", CLS["A1_ff"][(n, "T1")] == "mirrored"))
            checks.append((f"{n} A1_ff T2 = order-free", CLS["A1_ff"][(n, "T2")] == "order-free"))
            checks.append((f"{n} A1_ff T3g = order-free (BC, seed-1 value inside)", CLS["A1_ff"][(n, "T3g")] == "order-free (BC)"))
            for T in ("T1", "T2", "T3g", "T4"):
                checks.append((f"{n} A5_I {T} = order-free", CLS["A5_I"][(n, T)] in ("order-free", "order-free (BC)")))
        checks.append(("FXa drR T3g = order-dependent", CLS["drR"][("FXa", "T3g")] == "order-dependent"))
        checks.append(("FXa carry T3g = order-dependent", CLS["carry"][("FXa", "T3g")] == "order-dependent"))
        checks.append(("FXb drR T3g = order-free", CLS["drR"][("FXb", "T3g")] == "order-free"))
        checks.append(("FXb carry T3g = order-free", CLS["carry"][("FXb", "T3g")] == "order-free"))
        for s, ok in checks:
            emit(f"  {s}: {'PASS' if ok else 'FAIL'}")
        emit(f"  FIXTURE {'PASS' if all(ok for _, ok in checks) else 'FAIL'}")
    else:
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        with (RUN_DIR / "cells.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["text", "transform", "stat", "value", "lo95", "hi95"])
            for (n, T), (R, CI, _I) in ALL.items():
                for k, v in R.items():
                    lo, hi = CI.get(k, (nan(), nan()))
                    w.writerow([n, T, k, f"{v:.6g}", f"{lo:.6g}", f"{hi:.6g}"])
        with (RUN_DIR / "t3_seeds.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["text", "mode", "stat", "seed_index", "value"])
            for (n, mode), d in T3V.items():
                for k, v in d.items():
                    for i, x in enumerate(v):
                        w.writerow([n, mode, k, i, f"{x:.6g}"])
        (RUN_DIR / "classification.json").write_text(json.dumps(dict(
            per_stat={k: {f"{n}|{T}": c for (n, T), c in d.items()} for k, d in CLS.items()},
            constraints=TABLE, info={f"{n}|{T}": I for (n, T), (_R, _C, I) in ALL.items()}), indent=1, ensure_ascii=False, default=str),
            encoding="utf-8", newline="\n")
        emit("sidecars: runs/s79/cells.csv, runs/s79/t3_seeds.csv, runs/s79/classification.json")
    emit(f"runtime {time.time() - T0CLK:.0f} s; finished {clock()}")
    flush()


if __name__ == "__main__":
    main()
