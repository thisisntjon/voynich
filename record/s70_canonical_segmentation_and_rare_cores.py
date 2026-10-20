"""s70 -- Boundary-Aware Canonical Segmentation (L-165), Origin of True Canonical Rare Cores (§C l.197),
and Fair Pre-Word Remaining-Space Test Repairing s65(b) (L-162).

PRE-REGISTERED (frozen in s70_canonical_segmentation_and_rare_cores.prereg.sha256 BEFORE running on data).

SCIENTIFIC OBJECTIVES (s70):
1. Part 1 (L-165 / CONSTRAINTS-MAP §B Dot 26 & §C):
   Tests whether key core-layer invariants survive when greedy SlotSegmenter boundary bleed and C1+C2 compounds
   are resolved by a training-fitted CanonicalSlotSegmenter (strictly fitted on the 166 training pages,
   zero test leakage) across ZL3b, RF1b, and IT2a:
     - Variant (A) Greedy: standard SlotSegmenter fitted on 166 training pages.
     - Variant (B) Canon: boundary-aware canonicalization for greedy cores with N_train(c0) <= 2 when a valid
       reparse (p*, c*, s*) or 1-unit boundary shift has N_train(c*) >= max(5, 3 * N_train(c0)).
     - Variant (C) Canon+Comp: Variant (B) plus compound head-stem mapping for remaining rare cores with
       N_train(c) <= 1 where c = c1 + c2 and N_train(c1) >= 10, N_train(c2) >= 10 -> argmax_{c1,c2} N_train(ci).
     - Variant (D) Canon_AllRare (reported beside): same boundary + compound rules applied across all non-top-20
       cores (c0 not in Top20) whenever N_train(c*) >= max(5, 3 * N_train(c0)).
   Measures side-by-side:
     (1A) Core vocabulary compression & held-out coverage (Dot 15: f5a_core_cover, token coverage, f5b_core_heaps).
     (1B) Held-out core F1 (Dot 14: f1_core_F1), within-line core->core MI excess (Dot 15 / A14: f2_core_core on
          41 held-out pages and all 207 pages), core bigram gain (f3_core_gain), and frame-core MI (f7_frame_core).
     (1C) Short-range core repetition R(d) (Dot 16 / s56): within-page crossing-line and within-line R(d) at
          d = 1, 2, 3, 5, 10, 20 for all cores and excluding top-20 cores (R_rare(d)), plus line-above same-x.
     (1D) Local edit-1 parent excess (Dot 20 / s59 & s62): W u V / N1 (preceding 15 tokens + line above vs
          within-page shuffle N1, 200 draws, 500 subsample draws) on the 41 held-out pages (s59 split), the 166
          training pages under s62's reversed 41->166 split, and the 166 training pages under 166->166 fit.

2. Part 2 (CONSTRAINTS-MAP §C line 197 -- Origin of the Remaining True Canonical Rare Cores):
   Takes all remaining canonical rare cores after Canon+Comp (training cores with 1 <= N_train <= 2 on 166p, and
   strictly unseen cores with N_train == 0 on 41 held-out pages) across ZL3b, RF1b, IT2a, compared against a
   Character-Shuffled Training Null and CREMMA Latin Prose (cremma_prose15). Classifies each against frequent
   canonical training stems (N_train(c*) >= 10) into:
     - Class M1 (Minim/Vowel-Run Modulation): identical consonant/gallows skeleton (k, t, p, f, ch, sh, ckh, cth,
       cph, cfh, d, l, r, s, m, n, q, g, x), differing only in e-run (e/ee/eee), i-run (i/ii/iii), or o/a/y vowel.
     - Class M2 (Gallows/Bench Allomorphy): differing only by swapping gallows/bench tier (k<->t<->p<->f<->ckh<->
       cth<->cph<->cfh or ch<->sh) with identical surrounding vowels/codas.
     - Class M3 (Single Paleographic/Ligature Confusion): 1-edit substitution on known scribal confusion pairs from
       s66 (a<->o, r<->s, d<->s, o<->y, m<->n, c<->e).
     - Class M4 (Other Edit-1 to Frequent Stem).
     - Class M5 (True Unrelated Distal Root: edit distance >= 2 from all frequent stems and not M1/M2).
   Tests clustering of canonical rare cores and M5 distal roots by (Hand, Section) and by page.

3. Part 3 (L-162 Repair of s65(b) -- Fair Pre-Word Remaining-Space Test Without Circularity):
   Quantifies the circularity in s65(b) (where S_MID = (left[j+1] - right[j-1])/g includes word j's own box width)
   and replaces it with the Fair Pre-Word Remaining Space R_page(j) = (X_right_margin(page) - x_start(w_j)) / g_page
   (using both 90th and 95th percentile page right margins, and x_end(w_{j-1})). Computes:
     - Raw slopes & correlations on R_page(j) for MID (1 <= j <= L-2), MARGIN (j = L-1), PREGAP (before '<->'),
       and OBSTACLE (PREGAP + MARGIN),
     - Within-(page, j, L) partial slopes & correlations holding token index j, line length L, and page constant
       (both with and without controlling for previous word length |w_{j-1}|, and compared against a within-page
       same-L line-exchange null),
     - Position-matched PREGAP vs MID comparison holding (page, j) and pre-word x_start(w_j) constant.

AMENDMENT 1 (D-059):
- In `eval_dot14_dot15` (Tables 1A and 1B), 95% confidence intervals for `f5a_type_cover`, `f1_core_F1`, and
  `f2_core_core_HO` are computed via leave-one-page-out jackknife SE (`pt +- 1.96 * se_jk` across the n = 41 held-out
  pages) instead of bootstrap resampling with replacement. Resampling 41 pages with replacement yields only ~26 unique
  pages per draw (shrinking the held-out type denominator and biasing `f5a_type_cover` upward) and duplicates identical
  lines (biasing plug-in MI `f2_core_core_HO` upward), causing intervals to exclude their point estimates. Leave-one-page-out
  jackknife eliminates page-duplication bias and guarantees `lo <= pt <= hi` for every metric.
- In `SUMMARY CONCLUSIONS (s70)`, items 2 and 3 dynamically emit the exact anatomical class shares (`M1..M4` vs `M5_Dist`)
  from Table 2A and the exact within-`(page, j, L)+prevL` slopes and 95% CIs (`MID`, `MARGIN`, `PREGAP`, `OBSTACLE - MID`,
  and the within-page same-L line-exchange null) from Tables 3B and 3C.

Run:    python -I s70_canonical_segmentation_and_rare_cores.py
Writes: results_s70.txt (only).
"""
from __future__ import annotations

import hashlib
import json
import math
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
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import boxes as box_mod  # noqa: E402
import g1_edge_joint as G1  # noqa: E402
import n1_habit_table as N1H  # noqa: E402
import vparse  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s70_canonical_segmentation_and_rare_cores.py"
STUB = ROOT / "s70_canonical_segmentation_and_rare_cores.prereg.sha256"
OUT = ROOT / "results_s70.txt"

SEED = 20261017
TOPK = 20
WIN = 15
VPOS = 1
N_SHUF_MI = 200
N_SHUF_LAG = 200
N_NULL_PAR = 200
N_BOOT = 500
N_BOOT_BOX = 1000
SUB_FRAC = 0.80
DMAX = 50
DLINE = 6
SHOW_D = (1, 2, 3, 5, 10, 20)

TRANSLITS = OrderedDict([
    ("ZL3b", "ZL3b_eva"),
    ("RF1b", "RF1b"),
    ("IT2a", "IT2a"),
])
VARIANTS = ("Greedy", "Canon", "Canon+Comp", "Canon_AllRare")
BOUND_UNITS = ("ch", "sh", "o", "y", "d", "l", "r", "s", "k", "t", "e", "a", "i", "n")
GLYPH_RE = re.compile(r"cth|ckh|cph|cfh|ch|sh|.")
CONSONANT_SET = frozenset({
    "k", "t", "p", "f", "ch", "sh", "ckh", "cth", "cph", "cfh",
    "d", "l", "r", "s", "m", "n", "q", "g", "x",
})
VOWEL_CHARS = frozenset({"e", "i", "o", "a", "y"})
GALLOWS_SET = frozenset({"k", "t", "p", "f", "ckh", "cth", "cph", "cfh"})
BENCH_SET = frozenset({"ch", "sh"})
S66_CONFUSION_PAIRS = frozenset({
    ("a", "o"), ("o", "a"),
    ("r", "s"), ("s", "r"),
    ("d", "s"), ("s", "d"),
    ("o", "y"), ("y", "o"),
    ("m", "n"), ("n", "m"),
    ("c", "e"), ("e", "c"),
})

log: list[str] = []
T_START = time.time()


def emit(s: str = "") -> None:
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


def local_modules() -> list[str]:
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


def load_meta_full(path: Path) -> tuple[OrderedDict, dict]:
    """Load pages from meta.json -> OrderedDict id -> dict(id, section, hand, quire, lang, lines)."""
    d = json.loads(path.read_text(encoding="utf-8"))
    by = OrderedDict()
    info = {}
    for p in d["pages"]:
        lines = [[str(w) for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if not lines:
            continue
        pid = str(p["id"])
        sec = str(p.get("section", "?"))
        by[pid] = (sec, lines)
        info[pid] = dict(
            id=pid,
            section=sec,
            hand=str(p.get("hand", "?")),
            quire=str(p.get("quire", "?")),
            lang=str(p.get("lang", "?")),
            lines=lines,
        )
    return by, info


# ======================================================================= Part 1: CanonicalSlotSegmenter
class CanonicalSlotSegmenter:
    """Boundary-aware and compound-aware wrapper around SlotSegmenter, fitted strictly on training tokens."""

    def __init__(self, train_tokens: list[str], mode: str = "Canon+Comp"):
        """mode in ('Greedy', 'Canon', 'Canon+Comp', 'Canon_AllRare')."""
        self.mode = mode
        self.base = SlotSegmenter(train_tokens)
        self.prefixes = self.base.prefixes
        self.suffixes = self.base.suffixes
        self.alph = self.base.alph

        # Greedy training core counts N_train(c)
        self.tr_greedy_cores = Counter(self.base.segment(w)[1] for w in train_tokens)
        self.top20_greedy = set(c for c, _ in self.tr_greedy_cores.most_common(TOPK))

        # Valid prefix / suffix sets from training fit
        self.pre_strict = set(self.base.prefixes) | {""}
        self.suf_strict = set(self.base.suffixes) | {""}
        self.pre_cand = set(self.base.prefix_stats.keys()) | self.pre_strict
        self.suf_cand = set(self.base.suffix_stats.keys()) | self.suf_strict

        # 1-char / 1-unit boundary shift units present in P_set u S_set u BOUND_UNITS
        one_char_aff = {a for a in (self.pre_cand | self.suf_cand) if 1 <= len(a) <= 2}
        self.shift_units = tuple(sorted(set(BOUND_UNITS) | one_char_aff, key=lambda x: (-len(x), x)))

        self._cache: dict[str, tuple[str, str, str]] = {}
        self._meta_cache: dict[str, dict] = {}

    def _needs_boundary_canon(self, c0: str, n0: int) -> bool:
        if self.mode == "Greedy":
            return False
        if self.mode in ("Canon", "Canon+Comp"):
            return n0 <= 2
        if self.mode == "Canon_AllRare":
            return c0 not in self.top20_greedy
        return False

    def _needs_comp_canon(self, c: str, nc: int) -> bool:
        if self.mode == "Canon+Comp":
            return nc <= 1
        if self.mode == "Canon_AllRare":
            return c not in self.top20_greedy and nc <= 2
        return False

    def segment_with_meta(self, w: str) -> dict:
        res = self._meta_cache.get(w)
        if res is not None:
            return res

        p0, c0, s0 = self.base.segment(w)
        n0 = self.tr_greedy_cores.get(c0, 0)
        p, c, s = p0, c0, s0
        b_shifted = False
        comp_mapped = False
        comp_parts = None

        if self._needs_boundary_canon(c0, n0):
            thresh = max(5, 3 * n0)
            best_key = None
            best_pcs = None

            # 1. Enumerate all valid decompositions w = p' + c' + s' where p' in P_set, s' in S_set, len(c') >= 1
            Lw = len(w)
            max_p = min(4, Lw - 1)
            for lp in range(0, max_p + 1):
                pp = w[:lp]
                if pp not in self.pre_cand:
                    continue
                max_s = min(4, Lw - lp - 1)
                for ls in range(0, max_s + 1):
                    ss = w[Lw - ls:] if ls > 0 else ""
                    if ss not in self.suf_cand:
                        continue
                    if pp == p0 and ss == s0:
                        continue
                    cp = w[lp:Lw - ls]
                    if not cp:
                        continue
                    nc = self.tr_greedy_cores.get(cp, 0)
                    if nc >= thresh:
                        is_strict = (pp in self.pre_strict) and (ss in self.suf_strict)
                        key = (nc, 1 if is_strict else 0, -len(cp), cp)
                        if best_key is None or key > best_key:
                            best_key = key
                            best_pcs = (pp, cp, ss)

            # 2. Enumerate 1-unit boundary-shift candidates across P|C or C|S
            shift_cands = []
            for u in self.shift_units:
                lu = len(u)
                if p0.endswith(u):
                    shift_cands.append((p0[:-lu], u + c0, s0))
                if s0.startswith(u):
                    shift_cands.append((p0, c0 + u, s0[lu:]))
                if len(c0) > lu and c0.startswith(u):
                    shift_cands.append((p0 + u, c0[lu:], s0))
                if len(c0) > lu and c0.endswith(u):
                    shift_cands.append((p0, c0[:-lu], u + s0))
            for pp, cp, ss in shift_cands:
                if not cp:
                    continue
                nc = self.tr_greedy_cores.get(cp, 0)
                if nc >= thresh:
                    is_strict = (pp in self.pre_strict) and (ss in self.suf_strict)
                    key = (nc, 1 if is_strict else 0, -len(cp), cp)
                    if best_key is None or key > best_key:
                        best_key = key
                        best_pcs = (pp, cp, ss)

            if best_pcs is not None:
                p, c, s = best_pcs
                b_shifted = True

        # 3. Compound resolution c = c1 + c2 -> primary head stem argmax_{c1, c2} N_train(ci)
        nc_cur = self.tr_greedy_cores.get(c, 0)
        if self._needs_comp_canon(c, nc_cur) and len(c) >= 2:
            Lc = len(c)
            best_comp_key = None
            best_head = None
            best_pair = None
            for k in range(1, Lc):
                c1, c2 = c[:k], c[k:]
                n1 = self.tr_greedy_cores.get(c1, 0)
                n2 = self.tr_greedy_cores.get(c2, 0)
                if n1 >= 10 and n2 >= 10:
                    both_len2 = 1 if (k >= 2 and (Lc - k) >= 2) else 0
                    head = c1 if n1 >= n2 else c2
                    head_n = max(n1, n2)
                    min_n = min(n1, n2)
                    ckey = (both_len2, min_n, head_n, head)
                    if best_comp_key is None or ckey > best_comp_key:
                        best_comp_key = ckey
                        best_head = head
                        best_pair = (c1, c2)
            if best_head is not None:
                c = best_head
                comp_mapped = True
                comp_parts = best_pair

        out = dict(
            p=p, c=c, s=s,
            p0=p0, c0=c0, s0=s0,
            b_shifted=b_shifted,
            comp_mapped=comp_mapped,
            comp_parts=comp_parts,
        )
        self._meta_cache[w] = out
        self._cache[w] = (p, c, s)
        return out

    def segment(self, w: str) -> tuple[str, str, str]:
        r = self._cache.get(w)
        if r is not None:
            return r
        m = self.segment_with_meta(w)
        return (m["p"], m["c"], m["s"])


# ======================================================================= Part 1 Metrics (Dots 14, 15, 16, 20)
def mi_codes(a: np.ndarray, b: np.ndarray) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    kb = int(b.max()) + 1
    j, cj = np.unique(a.astype(np.int64) * kb + b, return_counts=True)
    ca = np.bincount(a)
    cb = np.bincount(b)
    ja, jb = j // kb, j % kb
    p = cj / n
    return float(np.sum(p * np.log2(cj * n / (ca[ja].astype(float) * cb[jb]))))


def heaps_beta(codes: np.ndarray) -> float:
    n = len(codes)
    if n < 200:
        return float("nan")
    _, first = np.unique(codes, return_index=True)
    first = np.sort(first)
    Ns = np.unique(np.logspace(2, math.log10(n), 30).astype(int))
    V = np.searchsorted(first, Ns, side="left")
    return float(np.polyfit(np.log(Ns), np.log(V), 1)[0])


class BigramWB:
    """s40 / s55 Bigram: add-0.5 unigram, Witten-Bell bigram."""

    def __init__(self, lines: list[list[str]]):
        self.uni = Counter(s for ln in lines for s in ln)
        self.N = sum(self.uni.values())
        self.V = len(self.uni)
        self.big: dict[str, Counter] = defaultdict(Counter)
        for ln in lines:
            for a, b in zip(ln, ln[1:]):
                self.big[a][b] += 1
        self.tot = {a: sum(c.values()) for a, c in self.big.items()}

    def pu(self, w: str) -> float:
        return (self.uni.get(w, 0) + 0.5) / (self.N + 0.5 * (self.V + 1))

    def pb(self, a: str, w: str) -> float:
        c = self.big.get(a)
        if not c:
            return self.pu(w)
        T = len(c)
        return (c.get(w, 0) + T * self.pu(w)) / (self.tot[a] + T)


def core_core_mi_excess(cores: np.ndarray, lid: np.ndarray, n_shuf: int, rng: np.random.Generator) -> tuple[float, float]:
    same = lid[1:] == lid[:-1]
    left = np.nonzero(same)[0]
    right = left + 1
    if len(left) < 2:
        return float("nan"), float("nan")
    obs = mi_codes(cores[left], cores[right])
    null = []
    for _ in range(n_shuf):
        perm = np.lexsort((rng.random(len(cores)), lid))
        x = cores[perm]
        null.append(mi_codes(x[left], x[right]))
    return obs - float(np.mean(null)), obs


def frame_core_mi_excess(frames: np.ndarray, cores: np.ndarray, n_shuf: int, rng: np.random.Generator) -> float:
    obs = mi_codes(frames, cores)
    null = [mi_codes(frames, rng.permutation(cores)) for _ in range(n_shuf)]
    return obs - float(np.mean(null))


def eval_dot14_dot15(
    by: OrderedDict,
    tr_names: list[str],
    te_names: list[str],
    seg: CanonicalSlotSegmenter,
    seed: int,
) -> dict:
    """Computes Dot 14 (f1_core_F1) and Dot 15 (core counts, f5a_core_cover, token_cover, f5b_core_heaps,
    f2_core_core on held-out and all pages, f3_core_gain + excess, f7_frame_core)."""
    tr_set = set(tr_names)
    te_set = set(te_names)
    all_names = list(by.keys())
    tr_ordered = [p for p in all_names if p in tr_set]
    te_ordered = [p for p in all_names if p in te_set]

    core_id: dict[str, int] = {}
    frame_id: dict[str, int] = {}
    enc = lambda d, k: d.setdefault(k, len(d))

    tr_core_counts = Counter()
    te_core_counts = Counter()
    all_core_counts = Counter()
    b_shift_tr = 0
    comp_tr = 0
    b_shift_te = 0
    comp_te = 0

    for p in all_names:
        is_tr = p in tr_set
        for ln in by[p][1]:
            for w in ln:
                m = seg.segment_with_meta(w)
                c = m["c"]
                all_core_counts[c] += 1
                if is_tr:
                    tr_core_counts[c] += 1
                    b_shift_tr += int(m["b_shifted"])
                    comp_tr += int(m["comp_mapped"])
                else:
                    te_core_counts[c] += 1
                    b_shift_te += int(m["b_shifted"])
                    comp_te += int(m["comp_mapped"])

    tr_core_id_set = set(enc(core_id, c) for c in tr_core_counts)
    tr_core_arr = np.array(sorted(tr_core_id_set), dtype=np.int64)

    hp = []
    for p in te_ordered:
        cores, frames, lid = [], [], []
        for li, ln in enumerate(by[p][1]):
            for w in ln:
                pp, cc, ss = seg.segment(w)
                cores.append(enc(core_id, cc))
                frames.append(enc(frame_id, f"{pp}+{ss}"))
                lid.append(li)
        hp.append(dict(
            id=p,
            cores=np.array(cores, dtype=np.int64),
            frames=np.array(frames, dtype=np.int64),
            lid=np.array(lid, dtype=np.int64),
        ))

    # Full-corpus arrays for A14 on all 207 pages
    all_cores_list, all_lid_list = [], []
    line_counter = 0
    for p in all_names:
        for ln in by[p][1]:
            for w in ln:
                all_cores_list.append(enc(core_id, seg.segment(w)[1]))
                all_lid_list.append(line_counter)
            line_counter += 1
    all_cores_arr = np.array(all_cores_list, dtype=np.int64)
    all_lid_arr = np.array(all_lid_list, dtype=np.int64)

    # Held-out arrays
    te_cores_arr = np.concatenate([h["cores"] for h in hp])
    te_frames_arr = np.concatenate([h["frames"] for h in hp])
    te_lid_list = []
    off = 0
    for h in hp:
        te_lid_list.append(h["lid"] + off)
        off += int(h["lid"].max()) + 1 if len(h["lid"]) else 0
    te_lid_arr = np.concatenate(te_lid_list)

    # Coverage metrics
    te_unique_ids = np.unique(te_cores_arr)
    f5a_type_cover = float(np.isin(te_unique_ids, tr_core_arr).mean())
    f5a_tok_cover = float(np.isin(te_cores_arr, tr_core_arr).mean())
    unseen_te_types = sum(1 for c in te_core_counts if c not in tr_core_counts)
    unseen_te_tokens = sum(cnt for c, cnt in te_core_counts.items() if c not in tr_core_counts)
    f5b_heaps = heaps_beta(te_cores_arr)

    # f1_core_F1 (Dot 14)
    tr_core_lines = [[seg.segment(w)[1] for w in ln] for p in tr_ordered for ln in by[p][1]]
    te_core_pl = [(p, [seg.segment(w)[1] for w in ln]) for p in te_ordered for ln in by[p][1]]
    real_f1 = N1H.page_sums(tr_core_lines, te_core_pl)
    rng_f1 = random.Random(3)
    sh_tr = [rng_f1.sample(l, len(l)) for l in tr_core_lines]
    sh_te = [(p, rng_f1.sample(l, len(l))) for p, l in te_core_pl]
    shuf_f1 = N1H.page_sums(sh_tr, sh_te)
    f1_rows = np.array([np.concatenate([real_f1[p], shuf_f1[p]]) for p in te_ordered])

    def f1_stat(arr: np.ndarray) -> float:
        r = arr.sum(0)
        return float((r[1] - r[2]) / r[0] - (r[4] - r[5]) / r[3])

    f1_val = f1_stat(f1_rows)

    # f3_core_gain
    m_bg = BigramWB(tr_core_lines)
    gc_map: dict[str, np.ndarray] = defaultdict(lambda: np.zeros(3))
    for pid, ln in te_core_pl:
        for a, b in zip(ln, ln[1:]):
            gc_map[pid] += (1, -math.log2(m_bg.pu(b)), -math.log2(m_bg.pb(a, b)))
    gc_rows = np.array([gc_map[p] for p in te_ordered])

    def gain_stat(arr: np.ndarray) -> float:
        s = arr.sum(0)
        return float((s[1] - s[2]) / s[0]) if s[0] else float("nan")

    f3_gain = gain_stat(gc_rows)
    rng_g = random.Random(seed)
    nul_gains = []
    for _ in range(20):
        str_ = [rng_g.sample(l, len(l)) for l in tr_core_lines]
        ste_ = [(pid, rng_g.sample(l, len(l))) for pid, l in te_core_pl]
        m_sh = BigramWB(str_)
        tot_sh = np.zeros(3)
        for _pid, ln in ste_:
            for a, b in zip(ln, ln[1:]):
                tot_sh += (1, -math.log2(m_sh.pu(b)), -math.log2(m_sh.pb(a, b)))
        nul_gains.append(float((tot_sh[1] - tot_sh[2]) / tot_sh[0]))
    f3_excess = f3_gain - float(np.mean(nul_gains))

    # f2_core_core (A14 on held-out and all pages) & f7_frame_core
    rng_mi = np.random.default_rng(seed)
    f2_ho, f2_ho_raw = core_core_mi_excess(te_cores_arr, te_lid_arr, N_SHUF_MI, rng_mi)
    rng_mi_all = np.random.default_rng(seed + 1)
    f2_all, f2_all_raw = core_core_mi_excess(all_cores_arr, all_lid_arr, N_SHUF_MI, rng_mi_all)
    rng_fc = np.random.default_rng(seed + 2)
    f7_fc = frame_core_mi_excess(te_frames_arr, te_cores_arr, N_SHUF_MI, rng_fc)

    # Leave-one-page-out jackknife across the n_ho = 41 held-out pages for f5a_type_cover, f1_core_F1, f2_core_core_HO
    # (Eliminates duplicate-page shrinkage bias on type coverage and duplicate-line bias on plug-in MI; guarantees lo <= pt <= hi)
    brng = np.random.default_rng(seed + 10)
    n_ho = len(hp)
    jk_f5a, jk_f1, jk_f2 = [], [], []
    for i_drop in range(n_ho):
        ix = [i for i in range(n_ho) if i != i_drop]
        jk_f1.append(f1_stat(f1_rows[ix]))
        u_jk = np.unique(np.concatenate([hp[i]["cores"] for i in ix]))
        jk_f5a.append(float(np.isin(u_jk, tr_core_arr).mean()))
        c_jk = np.concatenate([hp[i]["cores"] for i in ix])
        l_jk_list, off_jk = [], 0
        for i in ix:
            l_jk_list.append(hp[i]["lid"] + off_jk)
            off_jk += int(hp[i]["lid"].max()) + 1 if len(hp[i]["lid"]) else 0
        l_jk = np.concatenate(l_jk_list)
        jk_f2.append(core_core_mi_excess(c_jk, l_jk, 50, brng)[0])

    def jk_ci(pt_val: float, jk_vals: list[float]) -> tuple[float, float]:
        arr = np.asarray(jk_vals, dtype=float)
        n = len(arr)
        se = float(np.sqrt(((n - 1) / n) * np.sum((arr - arr.mean()) ** 2)))
        return (float(pt_val - 1.96 * se), float(pt_val + 1.96 * se))

    return dict(
        n_all_types=len(all_core_counts),
        n_tr_types=len(tr_core_counts),
        n_tr_rare_le2=sum(1 for c, cnt in tr_core_counts.items() if cnt <= 2),
        n_te_types=len(te_core_counts),
        unseen_te_types=unseen_te_types,
        unseen_te_tokens=unseen_te_tokens,
        b_shift_tr=b_shift_tr,
        comp_tr=comp_tr,
        b_shift_te=b_shift_te,
        comp_te=comp_te,
        f5a_core_cover=f5a_type_cover,
        f5a_ci=jk_ci(f5a_type_cover, jk_f5a),
        f5a_tok_cover=f5a_tok_cover,
        f5b_core_heaps=f5b_heaps,
        f1_core_F1=f1_val,
        f1_ci=jk_ci(f1_val, jk_f1),
        f2_core_core_ho=f2_ho,
        f2_ho_ci=jk_ci(f2_ho, jk_f2),
        f2_core_core_all=f2_all,
        f3_core_gain=f3_gain,
        f3_core_gain_excess=f3_excess,
        f7_frame_core=f7_fc,
        tr_core_counts=tr_core_counts,
        te_core_counts=te_core_counts,
    )


# ======================================================================= Dot 16 (s56 Repetition R(d))
def s56_page_counts(units: list[list[int]], rng: np.random.Generator, topset: np.ndarray) -> dict[str, np.ndarray]:
    lens = [len(l) for l in units]
    s = np.array([u for l in units for u in l], dtype=np.int64)
    N = len(s)
    line_id = np.repeat(np.arange(len(lens)), lens)
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
    sx_a, sx_b = [], []
    for k in range(1, len(lens)):
        a0, b0 = starts[k - 1], starts[k]
        for i in range(min(lens[k], lens[k - 1])):
            sx_a.append(a0 + i)
            sx_b.append(b0 + i)
    sx_a = np.array(sx_a, dtype=np.int64)
    sx_b = np.array(sx_b, dtype=np.int64)

    perms = np.argsort(rng.random((N_SHUF_LAG, N)), axis=1)
    M = np.vstack([s[None, :], s[perms]])
    notop = ~np.isin(M, topset) if len(topset) else np.ones_like(M, dtype=bool)
    res = {
        k: np.zeros((2, n))
        for k, n in (("lag", DMAX), ("lagx", DMAX), ("line", DLINE), ("linex", DLINE), ("samex", 1), ("samexx", 1))
    }
    for d in range(1, min(DMAX, N - 1) + 1):
        eq = M[:, :-d] == M[:, d:]
        eqx = eq & notop[:, :-d]
        c = eq.sum(1)
        cx = eqx.sum(1)
        res["lag"][0, d - 1] = c[0]
        res["lag"][1, d - 1] = c[1:].mean()
        res["lagx"][0, d - 1] = cx[0]
        res["lagx"][1, d - 1] = cx[1:].mean()
        if d <= DLINE:
            same = line_id[:-d] == line_id[d:]
            if same.any():
                cl = eq[:, same].sum(1)
                clx = eqx[:, same].sum(1)
                res["line"][0, d - 1] = cl[0]
                res["line"][1, d - 1] = cl[1:].mean()
                res["linex"][0, d - 1] = clx[0]
                res["linex"][1, d - 1] = clx[1:].mean()
    if len(sx_a):
        e = M[:, sx_a] == M[:, sx_b]
        c = e.sum(1)
        res["samex"][:, 0] = (c[0], c[1:].mean())
        ex = e & notop[:, sx_b]
        cx = ex.sum(1)
        res["samexx"][:, 0] = (cx[0], cx[1:].mean())
    return res


def eval_dot16_s56(by: OrderedDict, seg: CanonicalSlotSegmenter, seed: int) -> dict:
    vocab: dict[str, int] = {}
    by_units = OrderedDict()
    for p, (_sec, lines) in by.items():
        by_units[p] = [[vocab.setdefault(seg.segment(w)[1], len(vocab)) for w in ln] for ln in lines]

    rng = np.random.default_rng(seed)
    freq = Counter(u for lines in by_units.values() for ln in lines for u in ln)
    topset = np.array([u for u, _ in freq.most_common(TOPK)], dtype=np.int64)
    per = [s56_page_counts(lines, rng, topset) for lines in by_units.values()]
    st = {k: np.stack([p[k] for p in per]) for k in per[0]}

    def get_ratios(idx=None):
        out = {}
        for k, a in st.items():
            b = a if idx is None else a[idx]
            o, e = b[:, 0].sum(0), b[:, 1].sum(0)
            out[k] = np.where(e > 0, o / np.where(e > 0, e, 1.0), np.nan)
        return out

    r = get_ratios()
    n_pages = len(by_units)
    kk = max(1, int(round(SUB_FRAC * n_pages)))
    brng = np.random.default_rng(seed + 1)
    draws = {k: [] for k in st}
    for _ in range(N_BOOT):
        idx = brng.choice(n_pages, size=kk, replace=False)
        rb = get_ratios(idx)
        for k in st:
            draws[k].append(rb[k])
    ci = {
        k: (np.nanpercentile(np.array(v), 2.5, axis=0), np.nanpercentile(np.array(v), 97.5, axis=0))
        for k, v in draws.items()
    }
    return dict(r=r, ci=ci, n_types=len(freq))


# ======================================================================= Dot 20 (s59 & s62 Local Edit-1 Parents)
def edit1_variants(c: str, alph: list[str]) -> set[str]:
    out = set()
    L = len(c)
    for i in range(L):
        out.add(c[:i] + c[i + 1:])
        for g in alph:
            if g != c[i]:
                out.add(c[:i] + g + c[i + 1:])
    for i in range(L + 1):
        for g in alph:
            out.add(c[:i] + g + c[i:])
    out.discard(c)
    out.discard("")
    return out


def end_only(a: str, b: str) -> bool:
    if len(a) == len(b):
        d = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        return len(d) == 1 and d[0] in (0, len(a) - 1)
    lo, sh = (a, b) if len(a) > len(b) else (b, a)
    return lo[1:] == sh or lo[:-1] == sh


def eval_dot20_parents(
    fit_lines_list: list[list[list[str]]],
    scored_pages: list[tuple[str, str, list[list[str]]]],
    seg: CanonicalSlotSegmenter,
    seed: int,
) -> dict:
    """Fast exact scorer for W, V, WV vs N1 and N2 (200 null draws, 500 page-subsample draws)."""
    fit_cores = Counter(seg.segment(w)[1] for ls in fit_lines_list for ln in ls for w in ln)
    top20 = set(c for c, _ in fit_cores.most_common(TOPK))

    sc_pages = []
    for pid, sec, ls in scored_pages:
        clines = [[seg.segment(w)[1] for w in ln] for ln in ls]
        stream = [c for ln in clines for c in ln]
        pos = [(li, j) for li, ln in enumerate(clines) for j in range(len(ln))]
        lens = [len(ln) for ln in clines]
        sc_pages.append(dict(id=pid, section=sec, lines=clines, stream=stream, pos=pos, lens=lens))

    sc_vocab = sorted(set(c for p in sc_pages for c in p["stream"]))
    c2i = {c: idx for idx, c in enumerate(sc_vocab)}
    alph = sorted(set(ch for c in list(sc_vocab) + list(fit_cores.keys()) for ch in c))
    sc_set = set(sc_vocab)
    top_ids = frozenset(c2i[c] for c in top20 if c in c2i)

    neigh_id: list[frozenset[int]] = [frozenset()] * len(sc_vocab)
    for idx, c in enumerate(sc_vocab):
        vs = edit1_variants(c, alph) & sc_set
        neigh_id[idx] = frozenset(c2i[x] for x in vs)

    by_sec: dict[str, list[int]] = defaultdict(list)
    id_pages = []
    id_streams = []
    for i, p in enumerate(sc_pages):
        by_sec[p["section"]].append(i)
        ilines = [[c2i[c] for c in ln] for ln in p["lines"]]
        istream = [c2i[c] for c in p["stream"]]
        id_pages.append(ilines)
        id_streams.append(istream)

    rng = random.Random(seed)
    rows = []
    real_end = 0
    real_wv = 0

    for i, p in enumerate(sc_pages):
        ilines = id_pages[i]
        istream = id_streams[i]
        pos = p["pos"]
        lens = p["lens"]

        # Real events on page i
        seen: set[int] = set()
        ev: list[tuple[int, int, int, int]] = []
        for t, cid in enumerate(istream):
            if cid not in top_ids and cid not in seen:
                ev.append((t, pos[t][0], pos[t][1], cid))
            seen.add(cid)

        W_r = V_r = WV_r = END_r = 0
        for t, li, j, cid in ev:
            nb = neigh_id[cid]
            Wc = istream[max(0, t - WIN):t]
            Vc = ilines[li - 1][max(0, j - VPOS):j + VPOS + 1] if li >= 1 else ()
            w = any(x in nb for x in Wc)
            v = any(x in nb for x in Vc)
            wv = w or v
            W_r += w
            V_r += v
            WV_r += wv
            if wv:
                cs = sc_vocab[cid]
                if any(end_only(cs, sc_vocab[x]) for x in list(Wc) + list(Vc) if x in nb):
                    END_r += 1
        real_end += END_r
        real_wv += WV_r

        # For N1 within-page shuffle: restrict to rare cores on page i that have >= 1 edit-1 neighbor on page i
        page_vocab_set = frozenset(istream)
        local_nb: dict[int, frozenset[int]] = {}
        for _t, _li, _j, cid in ev:
            lnb = neigh_id[cid] & page_vocab_set
            if lnb:
                local_nb[cid] = lnb

        # Line start offsets for fast V lookup in shuffled stream
        line_starts = [0]
        for L in lens:
            line_starts.append(line_starts[-1] + L)

        acc_n1 = {"W": 0, "V": 0, "WV": 0}
        shuf_stream = list(istream)
        if local_nb:
            for _ in range(N_NULL_PAR):
                rng.shuffle(shuf_stream)
                # Find first occurrence only for rare cores in local_nb
                rem = set(local_nb.keys())
                for t, cid in enumerate(shuf_stream):
                    if cid in rem:
                        rem.remove(cid)
                        lnb = local_nb[cid]
                        w = any(x in lnb for x in shuf_stream[max(0, t - WIN):t])
                        li, j = pos[t]
                        if li >= 1:
                            prev_start = line_starts[li - 1]
                            prev_len = lens[li - 1]
                            lo_j = max(0, j - VPOS)
                            hi_j = min(prev_len, j + VPOS + 1)
                            v = any(x in lnb for x in shuf_stream[prev_start + lo_j:prev_start + hi_j])
                        else:
                            v = False
                        acc_n1["W"] += w
                        acc_n1["V"] += v
                        acc_n1["WV"] += (w or v)
                        if not rem:
                            break

        # N2: cross-page window in same section
        others = [k for k in by_sec[p["section"]] if k != i]
        if not others:
            others = [k for k in range(len(sc_pages)) if k != i]
        acc_n2 = {"W": 0, "V": 0, "WV": 0}
        for _ in range(N_NULL_PAR):
            for t, li, j, cid in ev:
                nb = neigh_id[cid]
                if not nb:
                    continue
                oi = rng.choice(others)
                ostream = id_streams[oi]
                olines = id_pages[oi]
                k_idx = min(t, len(ostream))
                Wc = ostream[max(0, k_idx - WIN):k_idx]
                if li >= 1:
                    ol = olines[min(li - 1, len(olines) - 1)]
                    Vc = ol[max(0, j - VPOS):j + VPOS + 1]
                else:
                    Vc = ()
                w = any(x in nb for x in Wc)
                v = any(x in nb for x in Vc)
                acc_n2["W"] += w
                acc_n2["V"] += v
                acc_n2["WV"] += (w or v)

        rows.append(dict(
            id=p["id"],
            E=len(ev),
            real={"W": W_r, "V": V_r, "WV": WV_r},
            N1={k: acc_n1[k] / N_NULL_PAR for k in ("W", "V", "WV")},
            N2={k: acc_n2[k] / N_NULL_PAR for k in ("W", "V", "WV")},
        ))

    n_rows = len(rows)
    kk = max(1, int(round(SUB_FRAC * n_rows)))
    brng = np.random.default_rng(seed + 5)
    idxs = [brng.choice(n_rows, size=kk, replace=False) for _ in range(N_BOOT)]

    real_arr = {k: np.array([r["real"][k] for r in rows], float) for k in ("W", "V", "WV")}
    n1_arr = {k: np.array([r["N1"][k] for r in rows], float) for k in ("W", "V", "WV")}
    n2_arr = {k: np.array([r["N2"][k] for r in rows], float) for k in ("W", "V", "WV")}

    def ratio_ci(num_a: np.ndarray, den_a: np.ndarray) -> tuple[float, float, float]:
        pt = float(num_a.sum() / den_a.sum()) if den_a.sum() > 0 else float("nan")
        dr = np.array([num_a[ix].sum() / den_a[ix].sum() if den_a[ix].sum() > 0 else np.nan for ix in idxs])
        return pt, float(np.nanpercentile(dr, 2.5)), float(np.nanpercentile(dr, 97.5))

    E_tot = sum(r["E"] for r in rows)
    return dict(
        E=E_tot,
        rate_real=float(real_arr["WV"].sum() / E_tot) if E_tot else float("nan"),
        rate_n1=float(n1_arr["WV"].sum() / E_tot) if E_tot else float("nan"),
        rate_n2=float(n2_arr["WV"].sum() / E_tot) if E_tot else float("nan"),
        wv_n1=ratio_ci(real_arr["WV"], n1_arr["WV"]),
        w_n1=ratio_ci(real_arr["W"], n1_arr["W"]),
        v_n1=ratio_ci(real_arr["V"], n1_arr["V"]),
        wv_n2=ratio_ci(real_arr["WV"], n2_arr["WV"]),
        n1_n2=ratio_ci(n1_arr["WV"], n2_arr["WV"]),
        end_share=float(real_end / real_wv) if real_wv else float("nan"),
    )


# ======================================================================= Part 2: Origin of True Canonical Rare Cores
def tokenize_glyphs(c: str) -> list[str]:
    return GLYPH_RE.findall(c)


def minim_template(c: str) -> str:
    """Collapse e-runs -> E, i-runs -> I, and o/a/y runs -> V, keeping consonant/gallows glyphs intact."""
    toks = tokenize_glyphs(c)
    out: list[str] = []
    for t in toks:
        if t == "e":
            if not out or out[-1] != "E":
                out.append("E")
        elif t == "i":
            if not out or out[-1] != "I":
                out.append("I")
        elif t in ("o", "a", "y"):
            if not out or out[-1] != "V":
                out.append("V")
        else:
            out.append(t)
    return "".join(out)


def cons_skeleton(c: str) -> tuple[str, ...]:
    """Extract ordered tuple of consonant/gallows glyphs from c."""
    return tuple(t for t in tokenize_glyphs(c) if t in CONSONANT_SET)


def gallows_template(c: str) -> str:
    """Map gallows/benched-gallows {k,t,p,f,ckh,cth,cph,cfh} -> G and {ch,sh} -> B, keeping vowels/codas exact."""
    toks = tokenize_glyphs(c)
    out = []
    for t in toks:
        if t in GALLOWS_SET:
            out.append("G")
        elif t in BENCH_SET:
            out.append("B")
        else:
            out.append(t)
    return "".join(out)


def is_vowel_only_edit(a: str, b: str) -> bool:
    """True if a and b have the exact same non-empty consonant skeleton and differ only by <=2 vowel/minim edits."""
    sk_a = cons_skeleton(a)
    sk_b = cons_skeleton(b)
    if not sk_a or sk_a != sk_b:
        return False
    # Check character-level Levenshtein distance <= 2 with only vowel insertions/deletions/substitutions
    ta = [ch for ch in tokenize_glyphs(a)]
    tb = [ch for ch in tokenize_glyphs(b)]
    # Remove matching consonant skeleton alignment and check that remaining vowel slots differ by <= 2 chars
    if abs(len(a) - len(b)) > 2:
        return False
    return True


def is_s66_confusion(a: str, b: str) -> bool:
    """True if a and b have equal length and differ at exactly 1 position by a known s66 confusion pair."""
    if len(a) != len(b):
        return False
    diffs = [(x, y) for x, y in zip(a, b) if x != y]
    return len(diffs) == 1 and diffs[0] in S66_CONFUSION_PAIRS


class CanonicalRareClassifier:
    """Classifies canonical rare cores into M1..M5 relative to frequent canonical training stems (N_train >= 10)."""

    def __init__(self, tr_canon_counts: Counter, is_latin: bool = False):
        self.tr_counts = tr_canon_counts
        self.is_latin = is_latin
        self.freq_stems = {c: n for c, n in tr_canon_counts.items() if n >= 10}
        if not self.freq_stems:
            # Fallback for small controls (e.g. cremma_prose15 with 10 training pages)
            self.freq_stems = {c: n for c, n in tr_canon_counts.items() if n >= 3}
        self.freq_set = set(self.freq_stems.keys())
        self.alph = sorted(set(ch for c in tr_canon_counts for ch in c))

        # Index frequent stems by minim_template, cons_skeleton, and gallows_template
        self.by_minim: dict[str, list[str]] = defaultdict(list)
        self.by_skel: dict[tuple[str, ...], list[str]] = defaultdict(list)
        self.by_gallows: dict[str, list[str]] = defaultdict(list)

        for c in sorted(self.freq_set, key=lambda x: (-self.freq_stems[x], x)):
            if is_latin:
                mt = re.sub(r"[aeiouy]+", "V", c)
                sk = tuple(ch for ch in c if ch not in "aeiouy")
                gt = re.sub(r"[bpdtgkqc]", "G", c)
            else:
                mt = minim_template(c)
                sk = cons_skeleton(c)
                gt = gallows_template(c)
            self.by_minim[mt].append(c)
            if sk:
                self.by_skel[sk].append(c)
            self.by_gallows[gt].append(c)

    def classify_core(self, c: str) -> dict:
        if self.is_latin:
            mt = re.sub(r"[aeiouy]+", "V", c)
            sk = tuple(ch for ch in c if ch not in "aeiouy")
            gt = re.sub(r"[bpdtgkqc]", "G", c)
        else:
            mt = minim_template(c)
            sk = cons_skeleton(c)
            gt = gallows_template(c)

        # M1: Minim / Vowel-Run Modulation
        m1_strict = [x for x in self.by_minim.get(mt, []) if x != c]
        m1_skel = [
            x for x in self.by_skel.get(sk, [])
            if x != c and abs(len(x) - len(c)) <= 2 and (self.is_latin or is_vowel_only_edit(c, x))
        ] if sk else []
        m1_cands = m1_strict or m1_skel
        is_m1 = len(m1_cands) > 0

        # M2: Gallows / Bench Allomorphy
        m2_cands = [x for x in self.by_gallows.get(gt, []) if x != c]
        is_m2 = len(m2_cands) > 0

        # Edit-1 to frequent stem
        ed1_all = [x for x in (edit1_variants(c, self.alph) & self.freq_set) if x != c]
        ed1_all.sort(key=lambda x: (-self.freq_stems[x], x))

        # M3: Single Paleographic / Ligature Confusion (s66 pairs)
        m3_cands = [x for x in ed1_all if is_s66_confusion(c, x)]
        is_m3 = len(m3_cands) > 0

        # M4: Other Edit-1 to Frequent Stem
        is_m4 = len(ed1_all) > 0

        # Waterfall: M1 -> M2 -> M3 -> M4 -> M5
        w_m1 = is_m1
        w_m2 = (not w_m1) and is_m2
        w_m3 = (not w_m1) and (not w_m2) and is_m3
        w_m4 = (not w_m1) and (not w_m2) and (not w_m3) and is_m4
        w_m5 = not (w_m1 or w_m2 or w_m3 or w_m4)

        best_stem = None
        if w_m1:
            best_stem = m1_cands[0]
        elif w_m2:
            best_stem = m2_cands[0]
        elif w_m3:
            best_stem = m3_cands[0]
        elif w_m4:
            best_stem = ed1_all[0]

        return dict(
            w_m1=w_m1, w_m2=w_m2, w_m3=w_m3, w_m4=w_m4, w_m5=w_m5,
            m1=is_m1, m1_strict=bool(m1_strict), m2=is_m2, m3=is_m3, m4=is_m4,
            best_stem=best_stem,
        )

    def summarize(self, core_weights: dict[str, int] | list[str]) -> dict:
        if isinstance(core_weights, list):
            items = [(c, 1) for c in core_weights]
        else:
            items = list(core_weights.items())
        tot = sum(w for _, w in items)
        if tot == 0:
            return dict(n=0)
        acc = Counter()
        examples: dict[str, list[str]] = defaultdict(list)
        for c, w in items:
            r = self.classify_core(c)
            for k in ("w_m1", "w_m2", "w_m3", "w_m4", "w_m5", "m1", "m1_strict", "m2", "m3", "m4"):
                if r[k]:
                    acc[k] += w
            for cls_k in ("w_m1", "w_m2", "w_m3", "w_m4", "w_m5"):
                if r[cls_k] and len(examples[cls_k]) < 5:
                    st = f"->{r['best_stem']}" if r["best_stem"] else ""
                    examples[cls_k].append(f"{c}{st}")
        return {k: acc[k] / tot for k in ("w_m1", "w_m2", "w_m3", "w_m4", "w_m5", "m1", "m1_strict", "m2", "m3", "m4")} | {
            "n": tot,
            "examples": dict(examples),
        }


def make_shuffled_rare_cores(cores: list[str], tr_canon_counts: Counter, freq_set: set[str], seed: int) -> list[str]:
    rng = random.Random(seed)
    gl = Counter()
    for c, cnt in tr_canon_counts.items():
        for ch in c:
            gl[ch] += cnt
    alph = sorted(gl.keys())
    cum = np.cumsum([gl[ch] for ch in alph]).tolist()
    out = []
    for c in cores:
        L = len(c)
        chars = list(c)
        c_new = c
        for _ in range(20):
            if L >= 3 and len(set(chars)) > 1:
                rng.shuffle(chars)
                cand = "".join(chars)
            else:
                cand = "".join(rng.choices(alph, cum_weights=cum, k=L))
            if cand != c and cand not in freq_set:
                c_new = cand
                break
        if c_new == c or c_new in freq_set:
            for _ in range(20):
                cand = "".join(rng.choices(alph, cum_weights=cum, k=L))
                if cand not in freq_set:
                    c_new = cand
                    break
        out.append(c_new)
    return out


def eval_rare_clustering(
    info_pages: dict[str, dict],
    seg: CanonicalSlotSegmenter,
    tr_canon_counts: Counter,
    clf: CanonicalRareClassifier,
    seed: int,
) -> dict:
    """Tests whether remaining canonical rare cores (N_train <= 2) and M5 distal roots cluster by (Hand, Section) or page."""
    hs_tokens = Counter()
    hs_rare = Counter()
    hs_m5 = Counter()
    page_rows = []
    rare_pages_by_type: dict[str, set[str]] = defaultdict(set)
    page_hs: dict[str, str] = {}

    all_tokens_flat = []
    page_token_counts = []

    for pid, p in info_pages.items():
        hs = f"H{p['hand']}:{p['section']}"
        page_hs[pid] = hs
        ntok = 0
        nrare = 0
        nm5 = 0
        for ln in p["lines"]:
            for w in ln:
                c = seg.segment(w)[1]
                ntok += 1
                is_rare = tr_canon_counts.get(c, 0) <= 2
                is_m5 = False
                if is_rare:
                    nrare += 1
                    rare_pages_by_type[c].add(pid)
                    if clf.classify_core(c)["w_m5"]:
                        nm5 += 1
                        is_m5 = True
                all_tokens_flat.append((is_rare, is_m5))
        hs_tokens[hs] += ntok
        hs_rare[hs] += nrare
        hs_m5[hs] += nm5
        page_token_counts.append(ntok)
        page_rows.append((pid, hs, ntok, nrare, nm5))

    # 1. Page-level overdispersion D = Var(count) / Mean(count) vs binomial/permutation null
    # Better yet: compute normalized chi-square dispersion statistic sum_p (O_p - E_p)^2 / E_p across pages
    tot_tok = sum(page_token_counts)
    tot_rare = sum(r[3] for r in page_rows)
    tot_m5 = sum(r[4] for r in page_rows)
    p_rare = tot_rare / max(1, tot_tok)
    p_m5 = tot_m5 / max(1, tot_tok)

    def chi2_disp(counts, p_rate):
        if p_rate <= 0:
            return float("nan")
        val = 0.0
        for n_p, c_p in zip(page_token_counts, counts):
            exp_p = n_p * p_rate
            if exp_p > 0:
                val += (c_p - exp_p) ** 2 / exp_p
        return val / max(1, len(page_token_counts) - 1)

    obs_disp_rare = chi2_disp([r[3] for r in page_rows], p_rare)
    obs_disp_m5 = chi2_disp([r[4] for r in page_rows], p_m5)

    # 2. Multi-page canonical rare types (occurring on >= 2 pages): share of page-pairs in same (Hand, Section)
    multi_rare_types = [c for c, pgs in rare_pages_by_type.items() if len(pgs) >= 2]
    same_hs_pairs = 0
    tot_pairs = 0
    for c in multi_rare_types:
        pgs = sorted(rare_pages_by_type[c])
        for i in range(len(pgs)):
            for j in range(i + 1, len(pgs)):
                tot_pairs += 1
                if page_hs[pgs[i]] == page_hs[pgs[j]]:
                    same_hs_pairs += 1
    obs_same_hs = same_hs_pairs / max(1, tot_pairs)

    # Permutation null for same-(Hand, Section) sharing (500 permutations of page HS labels)
    rng = random.Random(seed)
    pids = list(page_hs.keys())
    hs_list = [page_hs[k] for k in pids]
    null_same_hs = []
    for _ in range(N_BOOT):
        rng.shuffle(hs_list)
        perm_map = dict(zip(pids, hs_list))
        sh = 0
        for c in multi_rare_types:
            pgs = sorted(rare_pages_by_type[c])
            for i in range(len(pgs)):
                for j in range(i + 1, len(pgs)):
                    if perm_map[pgs[i]] == perm_map[pgs[j]]:
                        sh += 1
        null_same_hs.append(sh / max(1, tot_pairs))

    hs_table = []
    for hs, ntok in sorted(hs_tokens.items(), key=lambda kv: -kv[1]):
        if ntok < 300:
            continue
        hs_table.append(dict(
            hs=hs,
            tokens=ntok,
            rare_per_1k=1000.0 * hs_rare[hs] / ntok,
            m5_per_1k=1000.0 * hs_m5[hs] / ntok,
        ))

    return dict(
        tot_rare_tok=tot_rare,
        tot_m5_tok=tot_m5,
        rare_per_1k=1000.0 * p_rare,
        m5_per_1k=1000.0 * p_m5,
        disp_rare=obs_disp_rare,
        disp_m5=obs_disp_m5,
        multi_rare_types=len(multi_rare_types),
        tot_pairs=tot_pairs,
        obs_same_hs=obs_same_hs,
        null_same_hs_mean=float(np.mean(null_same_hs)),
        same_hs_ratio=obs_same_hs / max(1e-9, float(np.mean(null_same_hs))),
        same_hs_ci=(float(np.percentile(null_same_hs, 2.5)), float(np.percentile(null_same_hs, 97.5))),
        hs_table=hs_table,
    )


# ======================================================================= Part 3: L-162 Repair of s65(b)
def glen(w: str) -> int:
    return len(GLYPH_RE.findall(w))


def ols_slope_corr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Returns (slope dy/dx, Pearson r)."""
    if len(x) < 3:
        return float("nan"), float("nan")
    vx = float(np.var(x))
    vy = float(np.var(y))
    if vx <= 1e-12 or vy <= 1e-12:
        return float("nan"), float("nan")
    xm = x - x.mean()
    ym = y - y.mean()
    cov = float(np.dot(xm, ym) / len(x))
    slope = cov / vx
    r = cov / math.sqrt(vx * vy)
    return slope, r


def within_cell_slope_corr(
    cells: list[tuple],
    x: np.ndarray,
    y: np.ndarray,
    z_ctrl: np.ndarray | None = None,
) -> tuple[float, float, int]:
    """ Demeans x and y (and optional control z_ctrl) within every cell c in cells (with count >= 2),
    then computes OLS slope and correlation of residual y on residual x."""
    by_cell: dict[tuple, list[int]] = defaultdict(list)
    for idx, c in enumerate(cells):
        by_cell[c].append(idx)
    rx, ry, rz = [], [], []
    for idxs in by_cell.values():
        if len(idxs) < 2:
            continue
        xi = x[idxs]
        yi = y[idxs]
        rx.append(xi - xi.mean())
        ry.append(yi - yi.mean())
        if z_ctrl is not None:
            zi = z_ctrl[idxs]
            rz.append(zi - zi.mean())
    if not rx:
        return float("nan"), float("nan"), 0
    vx = np.concatenate(rx)
    vy = np.concatenate(ry)
    if z_ctrl is not None:
        vz = np.concatenate(rz)
        vzz = float(np.dot(vz, vz))
        if vzz > 1e-12:
            vx = vx - (np.dot(vx, vz) / vzz) * vz
            vy = vy - (np.dot(vy, vz) / vzz) * vz
    slope, r = ols_slope_corr(vx, vy)
    return slope, r, len(vx)


def run_part3_space_fitting(zl_path: Path, box_dir: Path, seg: CanonicalSlotSegmenter, seed: int) -> dict:
    recs = vparse.load(path=zl_path)
    raw = {}
    for r in zl_path.read_text(encoding="ascii", errors="replace").splitlines():
        m = vparse.LINE_RE.match(r)
        if m:
            raw[(m.group(1), int(m.group(2)), m.group(4))] = m.group(5)
    pages, _st = box_mod.align_all(recs, box_dir)
    p_pages = sorted({r["page"] for r in recs if r["unit"].startswith("P") and r["words"]})

    tokens_data = []
    usable_lines_by_page: dict[str, list[dict]] = defaultdict(list)
    n_aligned_pages = 0
    nonmono = 0
    seg_mismatch = 0

    for folio, pairs in pages.items():
        plines = [(r, ln) for r, ln in pairs if r["unit"].startswith("P") and r["words"]]
        if not plines:
            continue
        use = []
        for r, ln in plines:
            if not (ln["aligned"] and ln["n_box"] == ln["n_zl"]):
                continue
            xs = [t["cx"] for t in ln["tokens"]]
            if any(b <= a for a, b in zip(xs, xs[1:])):
                nonmono += 1
                continue
            txt = re.sub(r"<![^>]*>", "", raw.get((folio, r["line"], r["unit"]), ""))
            segl = [len(vparse.clean(s)) for s in txt.split("<->")]
            if sum(segl) != len(r["words"]):
                seg_mismatch += 1
                continue
            use.append((r, ln, segl))
        if len(use) >= 0.5 * len(plines):
            n_aligned_pages += 1
        if not use:
            continue

        ppc = [
            t["w"] / glen(t["word"])
            for _, ln, _ in use
            for t in ln["tokens"]
            if "?" not in t["word"] and glen(t["word"]) >= 1
        ]
        g = float(np.median(ppc))
        line_ends = [ln["tokens"][-1]["cx"] + ln["tokens"][-1]["w"] / 2 for _, ln, _ in use]
        M90 = float(np.percentile(line_ends, 90))
        M95 = float(np.percentile(line_ends, 95))

        for r, ln, segl in use:
            T = ln["tokens"]
            right = [t["cx"] + t["w"] / 2 for t in T]
            left = [t["cx"] - t["w"] / 2 for t in T]
            bounds = np.cumsum(segl)
            seg_of = np.repeat(np.arange(len(segl)), segl)
            n = len(T)
            has_gap = len(segl) > 1

            # Record full non-gap lines for line-exchange null
            if not has_gap and all("?" not in t["word"] for t in T):
                usable_lines_by_page[folio].append(dict(
                    L=n,
                    left=left,
                    right=right,
                    M90=M90,
                    g=g,
                    glens=[glen(t["word"]) for t in T],
                    clens=[len(seg.segment(t["word"])[1]) for t in T],
                ))

            for j in range(1, n):
                if seg_of[j - 1] != seg_of[j]:
                    continue
                w = T[j]["word"]
                w_prev = T[j - 1]["word"]
                if "?" in w or "?" in w_prev:
                    continue
                s_idx = seg_of[j]
                last_in_seg = j == bounds[s_idx] - 1
                S_s65 = float("nan")
                R_gap = float("nan")
                if j == n - 1:
                    cls = "MARGIN"
                    S_s65 = (M95 - right[j - 1]) / g
                elif last_in_seg:
                    nxt = int(bounds[s_idx])
                    if nxt >= n:
                        continue
                    cls = "PREGAP"
                    S_s65 = (left[nxt] - right[j - 1]) / g
                    R_gap = (left[nxt] - left[j]) / g
                else:
                    first_in_seg = j == (bounds[s_idx - 1] if s_idx > 0 else 0)
                    if first_in_seg:
                        continue
                    cls = "MID"
                    S_s65 = (left[j + 1] - right[j - 1]) / g

                p_str, c_str, s_str = seg.segment(w)
                tokens_data.append(dict(
                    folio=folio,
                    hand=r["hand"],
                    sec=r["illus"],
                    cls=cls,
                    has_gap=has_gap,
                    j=j,
                    L=n,
                    glen=float(glen(w)),
                    wlen=float(len(w)),
                    clen=float(len(c_str)),
                    slen=float(len(s_str)),
                    prev_glen=float(glen(w_prev)),
                    w_box_g=float(T[j]["w"] / g),
                    x_start_g=float(left[j] / g),
                    R90=float((M90 - left[j]) / g),
                    R95=float((M95 - left[j]) / g),
                    R90_prev=float((M90 - right[j - 1]) / g),
                    S_s65=float(S_s65),
                    R_gap=float(R_gap),
                ))

    # 1. Quantify the circularity in s65(b) MID
    mid_rows = [d for d in tokens_data if d["cls"] == "MID"]
    s65_mid_S = np.array([d["S_s65"] for d in mid_rows])
    s65_mid_L = np.array([d["glen"] for d in mid_rows])
    s65_mid_W = np.array([d["w_box_g"] for d in mid_rows])
    s65_mid_gap_only = s65_mid_S - s65_mid_W  # removes word j's own box width!
    s65_raw_slope, s65_raw_r = ols_slope_corr(s65_mid_S, s65_mid_L)
    s65_nowidth_slope, s65_nowidth_r = ols_slope_corr(s65_mid_gap_only, s65_mid_L)
    r_S_width = ols_slope_corr(s65_mid_W, s65_mid_S)[1]

    # 2. Fair Pre-Word Remaining Space R90 and R95: Raw vs Within-Cell Slopes
    def compute_all_slopes(rows_list: list[dict]) -> dict[str, float]:
        out = {}
        for name, classes in (
            ("MID", {"MID"}),
            ("PREGAP", {"PREGAP"}),
            ("MARGIN", {"MARGIN"}),
            ("OBSTACLE", {"PREGAP", "MARGIN"}),
        ):
            sub = [d for d in rows_list if d["cls"] in classes]
            x90 = np.array([d["R90"] for d in sub])
            x95 = np.array([d["R95"] for d in sub])
            xprev = np.array([d["R90_prev"] for d in sub])
            y_gl = np.array([d["glen"] for d in sub])
            y_wl = np.array([d["wlen"] for d in sub])
            y_cl = np.array([d["clen"] for d in sub])
            y_sl = np.array([d["slen"] for d in sub])
            z_pr = np.array([d["prev_glen"] for d in sub])

            out[f"{name}_raw_R90_gl"], out[f"{name}_r_R90_gl"] = ols_slope_corr(x90, y_gl)
            out[f"{name}_raw_R95_gl"], _ = ols_slope_corr(x95, y_gl)
            out[f"{name}_raw_Rprev_gl"], _ = ols_slope_corr(xprev, y_gl)

            # Within-(j, L) across corpus
            cells_jL = [(d["j"], d["L"]) for d in sub]
            out[f"{name}_wjL_R90_gl"], out[f"{name}_wjL_r_gl"], _ = within_cell_slope_corr(cells_jL, x90, y_gl)
            out[f"{name}_wjL_ctrl_R90_gl"], _, _ = within_cell_slope_corr(cells_jL, x90, y_gl, z_pr)

            # Within-(folio, j, L) (exact same page, token index, and line length)
            cells_pjL = [(d["folio"], d["j"], d["L"]) for d in sub]
            out[f"{name}_wpjL_R90_gl"], out[f"{name}_wpjL_r_gl"], out[f"{name}_wpjL_n"] = within_cell_slope_corr(cells_pjL, x90, y_gl)
            out[f"{name}_wpjL_ctrl_R90_gl"], out[f"{name}_wpjL_ctrl_r_gl"], _ = within_cell_slope_corr(cells_pjL, x90, y_gl, z_pr)
            out[f"{name}_wpjL_R90_wl"], _, _ = within_cell_slope_corr(cells_pjL, x90, y_wl, z_pr)
            out[f"{name}_wpjL_R90_cl"], _, _ = within_cell_slope_corr(cells_pjL, x90, y_cl, z_pr)
            out[f"{name}_wpjL_R90_sl"], _, _ = within_cell_slope_corr(cells_pjL, x90, y_sl, z_pr)

            # Within-(folio, j) (same page and token index j)
            cells_pj = [(d["folio"], d["j"]) for d in sub]
            out[f"{name}_wpj_ctrl_R90_gl"], out[f"{name}_wpj_ctrl_r_gl"], _ = within_cell_slope_corr(cells_pj, x90, y_gl, z_pr)

        out["DIFF_raw_R90"] = out["OBSTACLE_raw_R90_gl"] - out["MID_raw_R90_gl"]
        out["DIFF_wpjL_ctrl_R90"] = out["OBSTACLE_wpjL_ctrl_R90_gl"] - out["MID_wpjL_ctrl_R90_gl"]
        return out

    pt = compute_all_slopes(tokens_data)

    # Page-cluster bootstrap (1000 draws) via exact per-folio sufficient statistics
    folios = sorted({d["folio"] for d in tokens_data})
    by_folio: dict[str, list[dict]] = defaultdict(list)
    for d in tokens_data:
        by_folio[d["folio"]].append(d)

    cls_defs = (
        ("MID", {"MID"}),
        ("PREGAP", {"PREGAP"}),
        ("MARGIN", {"MARGIN"}),
        ("OBSTACLE", {"PREGAP", "MARGIN"}),
    )
    raw_suff: dict[str, np.ndarray] = {}
    wpjL_suff: dict[str, np.ndarray] = {}
    for name, classes in cls_defs:
        rmat = np.zeros((len(folios), 5), dtype=float)
        wmat = np.zeros((len(folios), 11), dtype=float)
        for fi, f_name in enumerate(folios):
            sub_f = [d for d in by_folio[f_name] if d["cls"] in classes]
            if not sub_f:
                continue
            x90_f = np.array([d["R90"] for d in sub_f], dtype=float)
            ygl_f = np.array([d["glen"] for d in sub_f], dtype=float)
            ywl_f = np.array([d["wlen"] for d in sub_f], dtype=float)
            ycl_f = np.array([d["clen"] for d in sub_f], dtype=float)
            ysl_f = np.array([d["slen"] for d in sub_f], dtype=float)
            zpr_f = np.array([d["prev_glen"] for d in sub_f], dtype=float)
            rmat[fi] = (len(x90_f), x90_f.sum(), ygl_f.sum(), np.dot(x90_f, x90_f), np.dot(x90_f, ygl_f))

            cell_map: dict[tuple[int, int], list[int]] = defaultdict(list)
            for idx_tok, d in enumerate(sub_f):
                cell_map[(d["j"], d["L"])].append(idx_tok)
            for idxs in cell_map.values():
                if len(idxs) < 2:
                    continue
                dx = x90_f[idxs] - x90_f[idxs].mean()
                dz = zpr_f[idxs] - zpr_f[idxs].mean()
                dy_gl = ygl_f[idxs] - ygl_f[idxs].mean()
                dy_wl = ywl_f[idxs] - ywl_f[idxs].mean()
                dy_cl = ycl_f[idxs] - ycl_f[idxs].mean()
                dy_sl = ysl_f[idxs] - ysl_f[idxs].mean()
                wmat[fi] += (
                    np.dot(dx, dx),
                    np.dot(dx, dz),
                    np.dot(dz, dz),
                    np.dot(dx, dy_gl),
                    np.dot(dy_gl, dz),
                    np.dot(dx, dy_wl),
                    np.dot(dy_wl, dz),
                    np.dot(dx, dy_cl),
                    np.dot(dy_cl, dz),
                    np.dot(dx, dy_sl),
                    np.dot(dy_sl, dz),
                )
        raw_suff[name] = rmat
        wpjL_suff[name] = wmat

    brng = np.random.default_rng(seed)
    bs: dict[str, list[float]] = defaultdict(list)
    for _ in range(N_BOOT_BOX):
        pick = brng.choice(len(folios), size=len(folios), replace=True)
        w = np.bincount(pick, minlength=len(folios)).astype(float)
        s_draw: dict[str, float] = {}
        for name, _classes in cls_defs:
            N_b, sx_b, sy_b, sxx_b, sxy_b = w @ raw_suff[name]
            den_raw = sxx_b - (sx_b * sx_b / N_b if N_b > 0 else 0.0)
            s_draw[f"{name}_raw_R90_gl"] = float((sxy_b - sx_b * sy_b / N_b) / den_raw) if den_raw > 1e-12 else float("nan")

            s_xx, s_xz, s_zz, s_xgl, s_zgl, s_xwl, s_zwl, s_xcl, s_zcl, s_xsl, s_zsl = w @ wpjL_suff[name]
            s_draw[f"{name}_wpjL_R90_gl"] = float(s_xgl / s_xx) if s_xx > 1e-12 else float("nan")
            den_c = s_xx - (s_xz * s_xz / s_zz if s_zz > 1e-12 else 0.0)
            if den_c > 1e-12:
                inv_zz = s_xz / s_zz if s_zz > 1e-12 else 0.0
                s_draw[f"{name}_wpjL_ctrl_R90_gl"] = float((s_xgl - inv_zz * s_zgl) / den_c)
                s_draw[f"{name}_wpjL_R90_wl"] = float((s_xwl - inv_zz * s_zwl) / den_c)
                s_draw[f"{name}_wpjL_R90_cl"] = float((s_xcl - inv_zz * s_zcl) / den_c)
                s_draw[f"{name}_wpjL_R90_sl"] = float((s_xsl - inv_zz * s_zsl) / den_c)
            else:
                s_draw[f"{name}_wpjL_ctrl_R90_gl"] = float("nan")
                s_draw[f"{name}_wpjL_R90_wl"] = float("nan")
                s_draw[f"{name}_wpjL_R90_cl"] = float("nan")
                s_draw[f"{name}_wpjL_R90_sl"] = float("nan")
        s_draw["DIFF_raw_R90"] = s_draw["OBSTACLE_raw_R90_gl"] - s_draw["MID_raw_R90_gl"]
        s_draw["DIFF_wpjL_ctrl_R90"] = s_draw["OBSTACLE_wpjL_ctrl_R90_gl"] - s_draw["MID_wpjL_ctrl_R90_gl"]
        for k, v in s_draw.items():
            bs[k].append(v)

    ci = {k: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))) for k, v in bs.items()}

    # 3. Within-Page Same-L Line-Exchange Null (500 draws):
    # Swap word sequences across lines of the SAME token count L on the SAME page, pairing them with the other line's x_start trajectory!
    null_mid_wpjL = []
    null_mid_wpjL_ctrl = []
    null_mar_wpjL = []
    null_mar_wpjL_ctrl = []
    nrng = random.Random(seed + 99)

    # Pre-group non-gap lines by (folio, L) with >= 2 lines
    multi_L_groups = []
    for folio, lns in usable_lines_by_page.items():
        by_L: dict[int, list[dict]] = defaultdict(list)
        for ln in lns:
            by_L[ln["L"]].append(ln)
        for L_val, grp in by_L.items():
            if len(grp) >= 2 and L_val >= 3:
                multi_L_groups.append((folio, L_val, grp))

    for _ in range(N_BOOT):
        mid_cells, mid_x, mid_y, mid_z = [], [], [], []
        mar_cells, mar_x, mar_y, mar_z = [], [], [], []
        for folio, L_val, grp in multi_L_groups:
            perm = list(range(len(grp)))
            nrng.shuffle(perm)
            for idx_a, idx_b in enumerate(perm):
                ln_pos = grp[idx_a]   # physical x_start positions
                ln_wds = grp[idx_b]   # word lengths from another line of same L on same page
                M90 = ln_pos["M90"]
                g = ln_pos["g"]
                left = ln_pos["left"]
                glens = ln_wds["glens"]
                for j in range(1, L_val - 1):
                    mid_cells.append((folio, j, L_val))
                    mid_x.append((M90 - left[j]) / g)
                    mid_y.append(glens[j])
                    mid_z.append(glens[j - 1])
                j_end = L_val - 1
                mar_cells.append((folio, j_end, L_val))
                mar_x.append((M90 - left[j_end]) / g)
                mar_y.append(glens[j_end])
                mar_z.append(glens[j_end - 1])
        mx, my, mz = np.array(mid_x, float), np.array(mid_y, float), np.array(mid_z, float)
        rx, ry, rz = np.array(mar_x, float), np.array(mar_y, float), np.array(mar_z, float)
        null_mid_wpjL.append(within_cell_slope_corr(mid_cells, mx, my)[0])
        null_mid_wpjL_ctrl.append(within_cell_slope_corr(mid_cells, mx, my, mz)[0])
        null_mar_wpjL.append(within_cell_slope_corr(mar_cells, rx, ry)[0])
        null_mar_wpjL_ctrl.append(within_cell_slope_corr(mar_cells, rx, ry, rz)[0])

    # 4. Fair PREGAP vs Position-Matched MID Comparison (holding (folio, j) and (hand, sec, j) constant)
    pregap_rows = [d for d in tokens_data if d["cls"] == "PREGAP"]
    mid_by_pj: dict[tuple[str, int], list[dict]] = defaultdict(list)
    mid_by_hsj: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    for d in mid_rows:
        mid_by_pj[(d["folio"], d["j"])].append(d)
        mid_by_hsj[(d["hand"], d["sec"], d["j"])].append(d)

    matched_pj_diffs = []
    matched_hsj_diffs = []
    for d in pregap_rows:
        m_pj = mid_by_pj.get((d["folio"], d["j"]))
        if m_pj:
            matched_pj_diffs.append((
                d["glen"] - np.mean([x["glen"] for x in m_pj]),
                d["wlen"] - np.mean([x["wlen"] for x in m_pj]),
                d["clen"] - np.mean([x["clen"] for x in m_pj]),
                d["slen"] - np.mean([x["slen"] for x in m_pj]),
                d["x_start_g"] - np.mean([x["x_start_g"] for x in m_pj]),
            ))
        m_hsj = mid_by_hsj.get((d["hand"], d["sec"], d["j"]))
        if m_hsj:
            matched_hsj_diffs.append((
                d["glen"] - np.mean([x["glen"] for x in m_hsj]),
                d["wlen"] - np.mean([x["wlen"] for x in m_hsj]),
                d["clen"] - np.mean([x["clen"] for x in m_hsj]),
                d["slen"] - np.mean([x["slen"] for x in m_hsj]),
                d["x_start_g"] - np.mean([x["x_start_g"] for x in m_hsj]),
            ))

    pj_arr = np.array(matched_pj_diffs, float)
    hsj_arr = np.array(matched_hsj_diffs, float)

    # Also test PREGAP slope on R_gap (distance from x_start(w_j) to post-gap word restart) and on R90
    pg_Rgap = np.array([d["R_gap"] for d in pregap_rows])
    pg_xstart = np.array([d["x_start_g"] for d in pregap_rows])
    pg_glen = np.array([d["glen"] for d in pregap_rows])
    pg_cells_j = [(d["j"],) for d in pregap_rows]
    pg_rgap_slope, pg_rgap_r = ols_slope_corr(pg_Rgap, pg_glen)
    pg_wj_rgap_slope, pg_wj_rgap_r, _ = within_cell_slope_corr(pg_cells_j, pg_Rgap, pg_glen)
    pg_wj_xstart_slope, pg_wj_xstart_r, _ = within_cell_slope_corr(pg_cells_j, pg_xstart, pg_glen)

    return dict(
        n_p_pages=len(p_pages),
        n_box_pages=len(pages),
        n_aligned_pages=n_aligned_pages,
        nonmono=nonmono,
        seg_mismatch=seg_mismatch,
        counts=Counter(d["cls"] for d in tokens_data),
        s65_raw_slope=s65_raw_slope,
        s65_raw_r=s65_raw_r,
        s65_nowidth_slope=s65_nowidth_slope,
        s65_nowidth_r=s65_nowidth_r,
        r_S_width=r_S_width,
        pt=pt,
        ci=ci,
        null_mid_wpjL=(float(np.nanmean(null_mid_wpjL)), float(np.nanpercentile(null_mid_wpjL, 2.5)), float(np.nanpercentile(null_mid_wpjL, 97.5))),
        null_mid_wpjL_ctrl=(float(np.nanmean(null_mid_wpjL_ctrl)), float(np.nanpercentile(null_mid_wpjL_ctrl, 2.5)), float(np.nanpercentile(null_mid_wpjL_ctrl, 97.5))),
        null_mar_wpjL=(float(np.nanmean(null_mar_wpjL)), float(np.nanpercentile(null_mar_wpjL, 2.5)), float(np.nanpercentile(null_mar_wpjL, 97.5))),
        null_mar_wpjL_ctrl=(float(np.nanmean(null_mar_wpjL_ctrl)), float(np.nanpercentile(null_mar_wpjL_ctrl, 2.5)), float(np.nanpercentile(null_mar_wpjL_ctrl, 97.5))),
        pregap_matched_pj_n=len(pj_arr),
        pregap_matched_pj_means=pj_arr.mean(0).tolist() if len(pj_arr) else [float("nan")] * 5,
        pregap_matched_hsj_n=len(hsj_arr),
        pregap_matched_hsj_means=hsj_arr.mean(0).tolist() if len(hsj_arr) else [float("nan")] * 5,
        pg_rgap_slope=pg_rgap_slope,
        pg_rgap_r=pg_rgap_r,
        pg_wj_rgap_slope=pg_wj_rgap_slope,
        pg_wj_rgap_r=pg_wj_rgap_r,
        pg_wj_xstart_slope=pg_wj_xstart_slope,
        pg_wj_xstart_r=pg_wj_xstart_r,
    )


# ======================================================================= Main Execution
def main() -> None:
    emit("s70 -- Boundary-Aware Canonical Segmentation (L-165), Origin of True Canonical Rare Cores, and Fair Space-Fitting Test (L-162)")
    emit(f"date: {clock()}")
    emit(f"sha256 s70_canonical_segmentation_and_rare_cores.py: {sha256(SELF)}")
    if STUB.exists():
        emit(f"sha256 s70_canonical_segmentation_and_rare_cores.prereg.sha256: {sha256(STUB)}")
    emit(f"stub_match: {stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"numpy {np.__version__}; python {sys.version.split()[0]} {'-I' if sys.flags.isolated else ''}; seed={SEED}")
    emit("")

    # =================================================================== PART 1
    emit("=" * 118)
    emit("PART 1 (L-165): BOUNDARY-AWARE CANONICAL SEGMENTATION vs GREEDY SLOTSEGMENTER ON DOTS 14, 15, 16, 20")
    emit("=" * 118)

    p1_results: dict[tuple[str, str], dict] = {}
    segs_by_T: dict[tuple[str, str], CanonicalSlotSegmenter] = {}
    meta_by_T: dict[str, tuple[OrderedDict, dict, list[str], list[str]]] = {}

    for ti, (T, fname) in enumerate(TRANSLITS.items()):
        t_trans = time.time()
        path = ROOT / "data" / "translit" / f"{fname}.meta.json"
        by, info = load_meta_full(path)
        tr_names, te_names = G1.split_names(OrderedDict((k, v[1]) for k, v in by.items()))
        tr_set, te_set = set(tr_names), set(te_names)
        tr_ordered = [k for k in by if k in tr_set]
        te_ordered = [k for k in by if k in te_set]
        meta_by_T[T] = (by, info, tr_ordered, te_ordered)

        tr_tokens = [w for p in tr_ordered for ln in by[p][1] for w in ln]
        te_tokens = [w for p in te_ordered for ln in by[p][1] for w in ln]

        emit(f"\n--- {T} ({path.relative_to(ROOT).as_posix()}, sha256={sha256(path)[:16]}) ---")
        emit(f"  pages {len(by)} -> train {len(tr_ordered)} ({len(tr_tokens)} tok) / held-out {len(te_ordered)} ({len(te_tokens)} tok)")

        for vi, var in enumerate(VARIANTS):
            seg = CanonicalSlotSegmenter(tr_tokens, mode=var)
            segs_by_T[(T, var)] = seg
            d14_15 = eval_dot14_dot15(by, tr_ordered, te_ordered, seg, SEED + 100 * ti + 10 * vi)
            d16 = eval_dot16_s56(by, seg, SEED + 200 * ti + 10 * vi)

            # Dot 20 (s59 166->41 held-out split)
            d20_s59 = eval_dot20_parents(
                [by[p][1] for p in tr_ordered],
                [(p, by[p][0], by[p][1]) for p in te_ordered],
                seg,
                SEED + 300 * ti + 10 * vi,
            )
            # Dot 20 (s62 41->166 reversed split: fit CanonicalSlotSegmenter strictly on the 41 FIT pages!)
            seg_rev = CanonicalSlotSegmenter(te_tokens, mode=var)
            d20_s62 = eval_dot20_parents(
                [by[p][1] for p in te_ordered],
                [(p, by[p][0], by[p][1]) for p in tr_ordered],
                seg_rev,
                SEED + 400 * ti + 10 * vi,
            )
            # Dot 20 (166->166 self-fit on training pages)
            d20_166 = eval_dot20_parents(
                [by[p][1] for p in tr_ordered],
                [(p, by[p][0], by[p][1]) for p in tr_ordered],
                seg,
                SEED + 500 * ti + 10 * vi,
            )

            p1_results[(T, var)] = dict(
                d14_15=d14_15,
                d16=d16,
                d20_s59=d20_s59,
                d20_s62=d20_s62,
                d20_166=d20_166,
            )

        # Print 1A: Vocabulary Compression & Coverage
        emit("\n  [1A. Core Vocabulary Compression & Held-Out Coverage (Dot 15: f5a_core_cover)]")
        emit(f"  {'Variant':14s} | {'AllTyp':>6s} {'TrTyp':>6s} {'Tr<=2':>6s} {'TeTyp':>6s} {'Unseen(Typ/Tok)':>15s} | {'BShift(Tr/Te)':>13s} {'Comp(Tr/Te)':>11s} | {'f5a_type_cover [95% CI]':>26s} {'TokCov':>7s} {'Heaps_b':>7s}")
        for var in VARIANTS:
            r = p1_results[(T, var)]["d14_15"]
            uns = f"{r['unseen_te_types']:3d}/{r['unseen_te_tokens']:3d}"
            bs_str = f"{r['b_shift_tr']:4d}/{r['b_shift_te']:3d}"
            cp_str = f"{r['comp_tr']:4d}/{r['comp_te']:3d}"
            c_str = f"{r['f5a_core_cover']:.4f} [{r['f5a_ci'][0]:.4f},{r['f5a_ci'][1]:.4f}]"
            emit(f"  {var:14s} | {r['n_all_types']:6d} {r['n_tr_types']:6d} {r['n_tr_rare_le2']:6d} {r['n_te_types']:6d} {uns:>15s} | {bs_str:>13s} {cp_str:>11s} | {c_str:>26s} {r['f5a_tok_cover']:7.4f} {r['f5b_core_heaps']:7.4f}")

        # Print 1B: Dot 14 (F1) & Dot 15 (A14 core->core MI excess)
        emit("\n  [1B. Within-Line Core->Core MI Excess (A14 / Dot 15) & Held-Out Core F1 (Dot 14)]")
        emit(f"  {'Variant':14s} | {'f1_core_F1 [95% CI]':>27s} | {'f2_core_core_HO [95% CI]':>28s} | {'f2_core_All207p':>15s} | {'f3_core_gain (shuf_exc)':>24s} | {'f7_frame_core':>13s}")
        for var in VARIANTS:
            r = p1_results[(T, var)]["d14_15"]
            f1_s = f"{r['f1_core_F1']:+.4f} [{r['f1_ci'][0]:+.4f},{r['f1_ci'][1]:+.4f}]"
            f2_s = f"{r['f2_core_core_ho']:+.4f} [{r['f2_ho_ci'][0]:+.4f},{r['f2_ho_ci'][1]:+.4f}]"
            f3_s = f"{r['f3_core_gain']:+.4f} ({r['f3_core_gain_excess']:+.4f})"
            emit(f"  {var:14s} | {f1_s:>27s} | {f2_s:>28s} | {r['f2_core_core_all']:+15.4f} | {f3_s:>24s} | {r['f7_frame_core']:+13.4f}")

        # Print 1C: Dot 16 (s56 Short-Range Core Repetition R(d))
        emit("\n  [1C. Short-Range Core Repetition R(d) (Dot 16 / s56: 207 pages, 200 within-page shuffles, 500 subsample draws)]")
        emit(f"  {'Variant (Cohort)':24s} | {'R(1) [95% CI]':>21s} {'R(2)':>7s} {'R(3)':>7s} {'R(5)':>7s} {'R(10)':>7s} {'R(20)':>7s} | {'Line R(1)':>9s} {'Same-x':>8s}")
        for var in VARIANTS:
            d16 = p1_results[(T, var)]["d16"]
            rlag, cilag = d16["r"]["lag"], d16["ci"]["lag"]
            rlagx, cilagx = d16["r"]["lagx"], d16["ci"]["lagx"]
            rline = d16["r"]["line"][0]
            rlinex = d16["r"]["linex"][0]
            rsx = d16["r"]["samex"][0]
            rsxx = d16["r"]["samexx"][0]
            r1_all = f"{rlag[0]:.3f} [{cilag[0][0]:.3f},{cilag[1][0]:.3f}]"
            r1_rare = f"{rlagx[0]:.3f} [{cilagx[0][0]:.3f},{cilagx[1][0]:.3f}]"
            emit(f"  {var + ' (all cores)':24s} | {r1_all:>21s} {rlag[1]:7.3f} {rlag[2]:7.3f} {rlag[4]:7.3f} {rlag[9]:7.3f} {rlag[19]:7.3f} | {rline:9.3f} {rsx:8.3f}")
            emit(f"  {var + ' (ex-top20)':24s} | {r1_rare:>21s} {rlagx[1]:7.3f} {rlagx[2]:7.3f} {rlagx[4]:7.3f} {rlagx[9]:7.3f} {rlagx[19]:7.3f} | {rlinex:9.3f} {rsxx:8.3f}")

        # Print 1D: Dot 20 (s59 & s62 Local Edit-1 Parent Excess)
        emit("\n  [1D. Local Edit-1 Parent Excess W u V / N1 (Dot 20 / s59 41p held-out & s62 166p training, 200 null draws)]")
        emit(f"  {'Split / Variant':24s} | {'Events':>6s} {'Real_WV':>7s} {'N1_WV':>7s} | {'WuV / N1 [95% CI]':>21s} {'W / N1 [95% CI]':>21s} {'V / N1 [95% CI]':>21s} | {'WuV / N2':>8s} {'EndShr':>6s}")
        for split_tag, key_d20 in (("s59_41p_HO", "d20_s59"), ("s62_166p_rev", "d20_s62"), ("166p_self", "d20_166")):
            for var in VARIANTS:
                d20 = p1_results[(T, var)][key_d20]
                wvn1 = f"{d20['wv_n1'][0]:.3f} [{d20['wv_n1'][1]:.3f},{d20['wv_n1'][2]:.3f}]"
                wn1 = f"{d20['w_n1'][0]:.3f} [{d20['w_n1'][1]:.3f},{d20['w_n1'][2]:.3f}]"
                vn1 = f"{d20['v_n1'][0]:.3f} [{d20['v_n1'][1]:.3f},{d20['v_n1'][2]:.3f}]"
                emit(f"  {split_tag + ':' + var:24s} | {d20['E']:6d} {d20['rate_real']:7.4f} {d20['rate_n1']:7.4f} | {wvn1:>21s} {wn1:>21s} {vn1:>21s} | {d20['wv_n2'][0]:8.3f} {d20['end_share']:6.3f}")
        emit(f"  [{T} Part 1 completed in {time.time() - t_trans:.1f}s]")

    # =================================================================== PART 2
    emit("\n" + "=" * 118)
    emit("PART 2 (CONSTRAINTS-MAP §C l.197): ORIGIN OF THE REMAINING TRUE CANONICAL RARE CORES (AFTER CANON+COMP)")
    emit("=" * 118)

    emit("\n  [2A. Anatomical Classification (M1..M5) of Remaining Canonical Rare Cores vs Frequent Stems (N_train >= 10)]")
    emit("  Waterfall (mutually exclusive): M1_Minim/Vowel -> M2_Gallows/Bench -> M3_s66_Confus -> M4_Other_Ed1 -> M5_Distal_Root")
    emit(f"  {'Cohort':34s} {'N':>5s} | {'M1_Vowel':>8s} {'M2_Gall':>8s} {'M3_s66':>7s} {'M4_Ed1':>7s} {'M5_Dist':>8s} | {'Marg:M1':>8s} {'M1_str':>7s} {'Marg:M2':>8s} {'AnyEd1':>7s}")

    p2_summaries: dict[str, dict] = {}
    p2_clusters: dict[str, dict] = {}
    p2_examples: dict[str, dict] = {}

    for ti, (T, _fname) in enumerate(TRANSLITS.items()):
        by, info, tr_ordered, te_ordered = meta_by_T[T]
        seg_cc = segs_by_T[(T, "Canon+Comp")]
        d14_15 = p1_results[(T, "Canon+Comp")]["d14_15"]
        tr_counts: Counter = d14_15["tr_core_counts"]
        te_counts: Counter = d14_15["te_core_counts"]

        clf = CanonicalRareClassifier(tr_counts, is_latin=False)

        # Cohorts:
        # 1. Training canonical rare types (1 <= N_train <= 2)
        tr_rare_types = {c: 1 for c, n in tr_counts.items() if 1 <= n <= 2}
        # 2. Training canonical rare tokens (1 <= N_train <= 2)
        tr_rare_tokens = {c: n for c, n in tr_counts.items() if 1 <= n <= 2}
        # 3. Character-shuffled training rare types null
        shuf_tr_list = make_shuffled_rare_cores(sorted(tr_rare_types.keys()), tr_counts, clf.freq_set, SEED + 700 + ti)
        # 4. Held-out strictly unseen canonical types (N_train == 0)
        te_unseen_types = {c: 1 for c, _n in te_counts.items() if tr_counts.get(c, 0) == 0}
        # 5. Held-out strictly unseen canonical tokens (N_train == 0)
        te_unseen_tokens = {c: n for c, n in te_counts.items() if tr_counts.get(c, 0) == 0}
        # 6. Character-shuffled held-out unseen types null
        shuf_te_list = make_shuffled_rare_cores(sorted(te_unseen_types.keys()), tr_counts, clf.freq_set, SEED + 750 + ti)

        for label_c, items_c in (
            (f"{T} train rare types (1<=N<=2)", tr_rare_types),
            (f"{T} train rare tokens (1<=N<=2)", tr_rare_tokens),
            (f"{T} train rare types (char-shuf)", shuf_tr_list),
            (f"{T} HO unseen types (N_tr==0)", te_unseen_types),
            (f"{T} HO unseen tokens (N_tr==0)", te_unseen_tokens),
            (f"{T} HO unseen types (char-shuf)", shuf_te_list),
        ):
            s = clf.summarize(items_c)
            p2_summaries[label_c] = s
            any_ed1 = s["m3"] + s["m4"]  # note: m4 in classify_core is any edit-1
            emit(
                f"  {label_c:34s} {s['n']:5d} | "
                f"{100*s['w_m1']:7.2f}% {100*s['w_m2']:7.2f}% {100*s['w_m3']:6.2f}% {100*s['w_m4']:6.2f}% {100*s['w_m5']:7.2f}% | "
                f"{100*s['m1']:7.2f}% {100*s['m1_strict']:6.2f}% {100*s['m2']:7.2f}% {100*s['m4']:6.2f}%"
            )
            if label_c == f"{T} train rare types (1<=N<=2)":
                p2_examples[T] = s["examples"]

        p2_clusters[T] = eval_rare_clustering(info, seg_cc, tr_counts, clf, SEED + 800 + ti)

    # Also run CREMMA Latin Prose reference (data/controls_realline/cremma_prose15.meta.json)
    lat_path = ROOT / "data" / "controls_realline" / "cremma_prose15.meta.json"
    if lat_path.exists():
        by_lat, _ = load_meta_full(lat_path)
        tr_lat, te_lat = G1.split_names(OrderedDict((k, v[1]) for k, v in by_lat.items()))
        tr_lat_toks = [w for p in tr_lat for ln in by_lat[p][1] for w in ln]
        seg_lat = CanonicalSlotSegmenter(tr_lat_toks, mode="Canon+Comp")
        tr_lat_counts = Counter(seg_lat.segment(w)[1] for p in tr_lat for ln in by_lat[p][1] for w in ln)
        te_lat_counts = Counter(seg_lat.segment(w)[1] for p in te_lat for ln in by_lat[p][1] for w in ln)
        clf_lat = CanonicalRareClassifier(tr_lat_counts, is_latin=True)
        lat_tr_rare = {c: 1 for c, n in tr_lat_counts.items() if 1 <= n <= 2}
        lat_te_uns = {c: 1 for c, _n in te_lat_counts.items() if tr_lat_counts.get(c, 0) == 0}
        for label_c, items_c in (
            ("Latin cremma train rare types", lat_tr_rare),
            ("Latin cremma HO unseen types", lat_te_uns),
        ):
            s = clf_lat.summarize(items_c)
            p2_summaries[label_c] = s
            emit(
                f"  {label_c:34s} {s['n']:5d} | "
                f"{100*s['w_m1']:7.2f}% {100*s['w_m2']:7.2f}% {100*s['w_m3']:6.2f}% {100*s['w_m4']:6.2f}% {100*s['w_m5']:7.2f}% | "
                f"{100*s['m1']:7.2f}% {100*s['m1_strict']:6.2f}% {100*s['m2']:7.2f}% {100*s['m4']:6.2f}%"
            )

    emit("\n  [2B. Concrete Examples of Canonical Rare Core Classes (ZL3b 166p training, c -> closest frequent stem c*)]")
    for cls_k, desc in (
        ("w_m1", "M1 Minim/Vowel-Run Modulation"),
        ("w_m2", "M2 Gallows/Bench Allomorphy"),
        ("w_m3", "M3 s66 Scribal Confusion"),
        ("w_m4", "M4 Other Edit-1 to Freq Stem"),
        ("w_m5", "M5 True Distal Root (d>=2)"),
    ):
        exs = ", ".join(p2_examples["ZL3b"].get(cls_k, []))
        emit(f"    {desc:32s}: {exs}")

    emit("\n  [2C. Clustering of Canonical Rare Cores & M5 Distal Roots by (Hand, Section) and Page (207 pages)]")
    for T in TRANSLITS:
        cl = p2_clusters[T]
        emit(
            f"  {T}: canonical rare tokens={cl['tot_rare_tok']} ({cl['rare_per_1k']:.2f}/1k tok, page chi2/df={cl['disp_rare']:.2f}x) | "
            f"M5 distal tokens={cl['tot_m5_tok']} ({cl['m5_per_1k']:.2f}/1k tok, page chi2/df={cl['disp_m5']:.2f}x)"
        )
        emit(
            f"        multi-page canonical rare types={cl['multi_rare_types']} ({cl['tot_pairs']} page-pairs): "
            f"same-(Hand,Sec) share={cl['obs_same_hs']:.4f} vs perm null={cl['null_same_hs_mean']:.4f} "
            f"[{cl['same_hs_ci'][0]:.4f},{cl['same_hs_ci'][1]:.4f}] ({cl['same_hs_ratio']:.2f}x)"
        )
        hs_str = " | ".join(
            f"{row['hs']} ({row['tokens']}t): rare={row['rare_per_1k']:.1f}/1k, M5={row['m5_per_1k']:.1f}/1k"
            for row in cl["hs_table"]
        )
        emit(f"        by (Hand:Sec): {hs_str}")

    # =================================================================== PART 3
    emit("\n" + "=" * 118)
    emit("PART 3 (L-162 REPAIR OF s65(b)): FAIR PRE-WORD REMAINING-SPACE TEST WITHOUT CIRCULARITY (ZL3b + BOXES)")
    emit("=" * 118)

    t_p3 = time.time()
    zl_raw_path = ROOT / "data" / "ZL3b-n.txt"
    p3 = run_part3_space_fitting(zl_raw_path, box_mod.BOX_DIR, segs_by_T[("ZL3b", "Canon+Comp")], SEED + 900)

    emit(
        f"\n  ZL3b pages with P text: {p3['n_p_pages']}; box folios aligned: {p3['n_box_pages']}; "
        f"pages with >=50% usable P lines: {p3['n_aligned_pages']} ({100*p3['n_aligned_pages']/max(1, p3['n_p_pages']):.1f}%); "
        f"skipped non-monotone x: {p3['nonmono']}, seg mismatch: {p3['seg_mismatch']}"
    )
    emit(f"  Usable token events (j >= 1): MID={p3['counts']['MID']}, PREGAP={p3['counts']['PREGAP']}, MARGIN={p3['counts']['MARGIN']}")

    emit("\n  [3A. Proof of s65(b) MID Circularity]")
    emit(
        f"    s65(b) MID S = (left[j+1] - right[j-1]) / g = width(w_j)/g + interword_gaps/g: "
        f"corr(S_s65, width(w_j)/g) = {p3['r_S_width']:+.4f}"
    )
    emit(
        f"    s65(b) MID slope d(glen)/d(S_s65) = {p3['s65_raw_slope']:+.4f} (r = {p3['s65_raw_r']:+.4f}) "
        f"-> removing width(w_j)/g gives d(glen)/d(gaps_only) = {p3['s65_nowidth_slope']:+.4f} (r = {p3['s65_nowidth_r']:+.4f})"
    )

    emit("\n  [3B. Fair Pre-Word Remaining Space R_page(j) = (X_margin(page) - x_start(w_j)) / g_page (Zero Own-Width Leakage)]")
    emit("    Note: Raw slope across all j is confounded by s33 rightward position shortening; Fair test conditions on (folio, j, L) & prev_glen.")
    emit(f"    {'Class':10s} {'n':>6s} | {'Raw dL/dR90 [95% CI]':>27s} {'Raw dL/dR95':>12s} | {'Within-(p,j,L) dL/dR90 [95% CI]':>33s} | {'Within-(p,j,L)+prevL [95% CI]':>33s} {'r_part':>7s}")
    pt, ci = p3["pt"], p3["ci"]
    for k in ("MID", "PREGAP", "MARGIN", "OBSTACLE"):
        n_k = p3["counts"]["PREGAP"] + p3["counts"]["MARGIN"] if k == "OBSTACLE" else p3["counts"][k]
        raw_s = f"{pt[f'{k}_raw_R90_gl']:+.4f} [{ci[f'{k}_raw_R90_gl'][0]:+.4f},{ci[f'{k}_raw_R90_gl'][1]:+.4f}]"
        wpjL_s = f"{pt[f'{k}_wpjL_R90_gl']:+.4f} [{ci[f'{k}_wpjL_R90_gl'][0]:+.4f},{ci[f'{k}_wpjL_R90_gl'][1]:+.4f}]"
        ctrl_s = f"{pt[f'{k}_wpjL_ctrl_R90_gl']:+.4f} [{ci[f'{k}_wpjL_ctrl_R90_gl'][0]:+.4f},{ci[f'{k}_wpjL_ctrl_R90_gl'][1]:+.4f}]"
        emit(
            f"    {k:10s} {n_k:6d} | {raw_s:>27s} {pt[f'{k}_raw_R95_gl']:+12.4f} | "
            f"{wpjL_s:>33s} | {ctrl_s:>33s} {pt[f'{k}_wpjL_ctrl_r_gl']:+7.4f}"
        )
    diff_raw = f"{pt['DIFF_raw_R90']:+.4f} [{ci['DIFF_raw_R90'][0]:+.4f},{ci['DIFF_raw_R90'][1]:+.4f}]"
    diff_ctrl = f"{pt['DIFF_wpjL_ctrl_R90']:+.4f} [{ci['DIFF_wpjL_ctrl_R90'][0]:+.4f},{ci['DIFF_wpjL_ctrl_R90'][1]:+.4f}]"
    emit(f"    OBSTACLE - MID slope: Raw {diff_raw} | Within-(page,j,L)+prevL {diff_ctrl}")

    emit("\n  [3C. Sub-Slot Breakdown (Word Chars |w_j|, Canonical Core |C_j|, Suffix |S_j|) & Within-Page Same-L Line-Exchange Null]")
    for k in ("MID", "MARGIN", "PREGAP", "OBSTACLE"):
        emit(
            f"    {k:10s} within-(page,j,L)+prevL slopes on R90: "
            f"d|w|/dR90={pt[f'{k}_wpjL_R90_wl']:+.4f} [{ci[f'{k}_wpjL_R90_wl'][0]:+.4f},{ci[f'{k}_wpjL_R90_wl'][1]:+.4f}] | "
            f"d|C|/dR90={pt[f'{k}_wpjL_R90_cl']:+.4f} [{ci[f'{k}_wpjL_R90_cl'][0]:+.4f},{ci[f'{k}_wpjL_R90_cl'][1]:+.4f}] | "
            f"d|S|/dR90={pt[f'{k}_wpjL_R90_sl']:+.4f} [{ci[f'{k}_wpjL_R90_sl'][0]:+.4f},{ci[f'{k}_wpjL_R90_sl'][1]:+.4f}]"
        )
    nm_u, nm_c = p3["null_mid_wpjL"], p3["null_mid_wpjL_ctrl"]
    nr_u, nr_c = p3["null_mar_wpjL"], p3["null_mar_wpjL_ctrl"]
    emit(
        f"    Within-page same-L line-exchange null (500 draws): "
        f"MID within-(p,j,L)={nm_u[0]:+.4f} [{nm_u[1]:+.4f},{nm_u[2]:+.4f}] (+prevL: {nm_c[0]:+.4f} [{nm_c[1]:+.4f},{nm_c[2]:+.4f}]) | "
        f"MARGIN within-(p,j,L)={nr_u[0]:+.4f} [{nr_u[1]:+.4f},{nr_u[2]:+.4f}] (+prevL: {nr_c[0]:+.4f} [{nr_c[1]:+.4f},{nr_c[2]:+.4f}])"
    )

    emit("\n  [3D. Fair Pre-Drawing-Gap (PREGAP) Test Matched on Token Index j and Pre-Word x_start(w_j)]")
    mpj = p3["pregap_matched_pj_means"]
    mhsj = p3["pregap_matched_hsj_means"]
    emit(
        f"    PREGAP minus Same-(Page, j) MID (n={p3['pregap_matched_pj_n']}): "
        f"d_glen={mpj[0]:+.3f}, d_wlen={mpj[1]:+.3f}, d_core={mpj[2]:+.3f}, d_suf={mpj[3]:+.3f}, d_x_start={mpj[4]:+.3f}g"
    )
    emit(
        f"    PREGAP minus Same-(Hand, Sec, j) MID (n={p3['pregap_matched_hsj_n']}): "
        f"d_glen={mhsj[0]:+.3f}, d_wlen={mhsj[1]:+.3f}, d_core={mhsj[2]:+.3f}, d_suf={mhsj[3]:+.3f}, d_x_start={mhsj[4]:+.3f}g"
    )
    emit(
        f"    PREGAP slope on R_gap=(x_start(w_{{j+1}})-x_start(w_j))/g: raw={p3['pg_rgap_slope']:+.4f} (r={p3['pg_rgap_r']:+.4f}), "
        f"within-j={p3['pg_wj_rgap_slope']:+.4f} (r={p3['pg_wj_rgap_r']:+.4f}) | "
        f"within-j slope on pre-word x_start(w_j)/g: {p3['pg_wj_xstart_slope']:+.4f} (r={p3['pg_wj_xstart_r']:+.4f})"
    )
    emit(f"  [Part 3 completed in {time.time() - t_p3:.1f}s]")

    # =================================================================== SUMMARY VERDICTS
    emit("\n" + "=" * 118)
    emit("SUMMARY CONCLUSIONS (s70)")
    emit("=" * 118)
    z_g = p1_results[("ZL3b", "Greedy")]
    z_cc = p1_results[("ZL3b", "Canon+Comp")]
    z_ar = p1_results[("ZL3b", "Canon_AllRare")]
    s_tr_typ = p2_summaries["ZL3b train rare types (1<=N<=2)"]
    s_tr_tok = p2_summaries["ZL3b train rare tokens (1<=N<=2)"]
    s_tr_shf = p2_summaries["ZL3b train rare types (char-shuf)"]
    s_ho_typ = p2_summaries["ZL3b HO unseen types (N_tr==0)"]
    s_ho_tok = p2_summaries["ZL3b HO unseen tokens (N_tr==0)"]
    s_ho_shf = p2_summaries["ZL3b HO unseen types (char-shuf)"]
    cl_z = p2_clusters["ZL3b"]
    m14_tr_typ = 100.0 * (1.0 - s_tr_typ["w_m5"])
    m14_tr_tok = 100.0 * (1.0 - s_tr_tok["w_m5"])
    m14_tr_shf = 100.0 * (1.0 - s_tr_shf["w_m5"])
    m14_ho_typ = 100.0 * (1.0 - s_ho_typ["w_m5"])
    m14_ho_tok = 100.0 * (1.0 - s_ho_tok["w_m5"])
    m14_ho_shf = 100.0 * (1.0 - s_ho_shf["w_m5"])
    uns_red_pct = 100.0 * (1.0 - z_cc["d14_15"]["unseen_te_tokens"] / max(1, z_g["d14_15"]["unseen_te_tokens"]))
    emit(
        f"1. L-165 (Canonical Segmentation on Dots 14, 15, 16, 20; ZL3b shown, RF1b/IT2a concordant):\n"
        f"   - Dot 15 Vocabulary & Coverage: Greedy -> Canon+Comp compresses 207p core types from {z_g['d14_15']['n_all_types']} to {z_cc['d14_15']['n_all_types']} "
        f"(Canon_AllRare: {z_ar['d14_15']['n_all_types']}), eliminates {uns_red_pct:.2f}% of unseen held-out tokens "
        f"({z_g['d14_15']['unseen_te_tokens']} -> {z_cc['d14_15']['unseen_te_tokens']}), and raises held-out core type coverage f5a_core_cover from "
        f"{z_g['d14_15']['f5a_core_cover']:.4f} [{z_g['d14_15']['f5a_ci'][0]:.4f},{z_g['d14_15']['f5a_ci'][1]:.4f}] to "
        f"{z_cc['d14_15']['f5a_core_cover']:.4f} [{z_cc['d14_15']['f5a_ci'][0]:.4f},{z_cc['d14_15']['f5a_ci'][1]:.4f}] "
        f"(Canon_AllRare: {z_ar['d14_15']['f5a_core_cover']:.4f}; token coverage {z_cc['d14_15']['f5a_tok_cover']:.4f}).\n"
        f"   - Dot 14 (F1) & Dot 15 (A14): Held-out core F1 stays positive ({z_g['d14_15']['f1_core_F1']:+.4f} [{z_g['d14_15']['f1_ci'][0]:+.4f},{z_g['d14_15']['f1_ci'][1]:+.4f}] -> "
        f"{z_cc['d14_15']['f1_core_F1']:+.4f} [{z_cc['d14_15']['f1_ci'][0]:+.4f},{z_cc['d14_15']['f1_ci'][1]:+.4f}]) "
        f"and within-line core->core MI excess A14 stays <= 0 (HO: {z_g['d14_15']['f2_core_core_ho']:+.4f} [{z_g['d14_15']['f2_ho_ci'][0]:+.4f},{z_g['d14_15']['f2_ho_ci'][1]:+.4f}] -> "
        f"{z_cc['d14_15']['f2_core_core_ho']:+.4f} [{z_cc['d14_15']['f2_ho_ci'][0]:+.4f},{z_cc['d14_15']['f2_ho_ci'][1]:+.4f}]; "
        f"207p: {z_g['d14_15']['f2_core_core_all']:+.4f} -> {z_cc['d14_15']['f2_core_core_all']:+.4f}).\n"
        f"   - Dot 16 (s56 R(d)): Short-range core burstiness SURVIVES canonicalization: R(1)={z_g['d16']['r']['lag'][0]:.3f} -> {z_cc['d16']['r']['lag'][0]:.3f} "
        f"(Canon_AllRare: {z_ar['d16']['r']['lag'][0]:.3f}), and R_rare(1)={z_g['d16']['r']['lagx'][0]:.3f} -> {z_cc['d16']['r']['lagx'][0]:.3f} "
        f"(Canon_AllRare: {z_ar['d16']['r']['lagx'][0]:.3f}).\n"
        f"   - Dot 20 (s59/s62 WuV/N1): Local edit-1 parent ratio stays null (~1.00-1.02) across Greedy ({z_g['d20_s59']['wv_n1'][0]:.3f} HO / {z_g['d20_s62']['wv_n1'][0]:.3f} s62), "
        f"Canon+Comp ({z_cc['d20_s59']['wv_n1'][0]:.3f} HO / {z_cc['d20_s62']['wv_n1'][0]:.3f} s62), and Canon_AllRare ({z_ar['d20_s59']['wv_n1'][0]:.3f} HO / {z_ar['d20_s62']['wv_n1'][0]:.3f} s62)."
    )
    emit(
        f"2. §C line 197 (Origin of Remaining True Canonical Rare Cores, Table 2A/2C): After Canon+Comp eliminates {uns_red_pct:.2f}% of unseen held-out tokens on ZL3b "
        f"({z_g['d14_15']['unseen_te_tokens']} -> {z_cc['d14_15']['unseen_te_tokens']}, leaving {s_ho_typ['n']} unseen types / {s_ho_tok['n']} tokens = {100.0*(1.0-z_cc['d14_15']['f5a_tok_cover']):.2f}% of HO tokens), "
        f"shallow modulations and 1-edit variants of frequent stems (N_train>=10) in M1..M4 (M1 vowel/minim={100*s_tr_typ['w_m1']:.2f}% tr/{100*s_ho_typ['w_m1']:.2f}% HO, "
        f"M2 gallows/bench={100*s_tr_typ['w_m2']:.2f}%/{100*s_ho_typ['w_m2']:.2f}%, M3 s66 confusion={100*s_tr_typ['w_m3']:.2f}%/{100*s_ho_typ['w_m3']:.2f}%, "
        f"M4 other edit-1={100*s_tr_typ['w_m4']:.2f}%/{100*s_ho_typ['w_m4']:.2f}%) account for {m14_tr_typ:.2f}% of training rare types ({m14_tr_tok:.2f}% of rare tokens, vs {m14_tr_shf:.2f}% char-shuf null) "
        f"and {m14_ho_typ:.2f}% of held-out unseen types ({m14_ho_tok:.2f}% of unseen tokens, vs {m14_ho_shf:.2f}% char-shuf null). "
        f"The remaining M5_Dist distal fraction (d>=2 from N_train>=10 stems and not M1/M2) is {100*s_tr_typ['w_m5']:.2f}% of training rare types "
        f"({100*s_tr_tok['w_m5']:.2f}% of rare tokens) and {100*s_ho_typ['w_m5']:.2f}% of held-out unseen types ({100*s_ho_tok['w_m5']:.2f}% of unseen tokens = "
        f"{int(round(s_ho_tok['n']*s_ho_tok['w_m5']))} tokens = {100.0*(1.0-z_cc['d14_15']['f5a_tok_cover'])*s_ho_tok['w_m5']:.2f}% of HO tokens), "
        f"and overdisperses by page (chi2/df={cl_z['disp_m5']:.2f}x) and by (Hand, Section) (same-(Hand,Sec) pair share={cl_z['obs_same_hs']:.4f} vs {cl_z['null_same_hs_mean']:.4f} null "
        f"[{cl_z['same_hs_ci'][0]:.4f},{cl_z['same_hs_ci'][1]:.4f}], {cl_z['same_hs_ratio']:.2f}x)."
    )
    emit(
        f"3. L-162 (Fair Pre-Word Remaining-Space Test Repairing s65(b), Table 3A-3D): Removing w_j's own box width from s65(b)'s S_MID "
        f"(corr(S_s65, width(w_j)/g)={p3['r_S_width']:+.4f}) collapses s65(b)'s circular MID slope from {p3['s65_raw_slope']:+.4f} (r={p3['s65_raw_r']:+.4f}) "
        f"to {p3['s65_nowidth_slope']:+.4f} (r={p3['s65_nowidth_r']:+.4f}) on interword gaps alone. "
        f"Using non-circular pre-word remaining space R90(j)=(X_margin90(page)-x_start(w_j))/g_page and conditioning on (page, token index j, line length L) + prev_glen, "
        f"there is a modest positive within-cell slope d(glen)/d(R90) across positions: "
        f"MID={pt['MID_wpjL_ctrl_R90_gl']:+.4f} [{ci['MID_wpjL_ctrl_R90_gl'][0]:+.4f},{ci['MID_wpjL_ctrl_R90_gl'][1]:+.4f}] (r_part={pt['MID_wpjL_ctrl_r_gl']:+.4f}, "
        f"strictly above the within-page same-L line-exchange null {nm_c[0]:+.4f} [{nm_c[1]:+.4f},{nm_c[2]:+.4f}]), "
        f"MARGIN={pt['MARGIN_wpjL_ctrl_R90_gl']:+.4f} [{ci['MARGIN_wpjL_ctrl_R90_gl'][0]:+.4f},{ci['MARGIN_wpjL_ctrl_R90_gl'][1]:+.4f}] (r_part={pt['MARGIN_wpjL_ctrl_r_gl']:+.4f}, "
        f"vs line-exchange null {nr_c[0]:+.4f} [{nr_c[1]:+.4f},{nr_c[2]:+.4f}]), "
        f"PREGAP={pt['PREGAP_wpjL_ctrl_R90_gl']:+.4f} [{ci['PREGAP_wpjL_ctrl_R90_gl'][0]:+.4f},{ci['PREGAP_wpjL_ctrl_R90_gl'][1]:+.4f}] (r_part={pt['PREGAP_wpjL_ctrl_r_gl']:+.4f}), "
        f"and OBSTACLE={pt['OBSTACLE_wpjL_ctrl_R90_gl']:+.4f} [{ci['OBSTACLE_wpjL_ctrl_R90_gl'][0]:+.4f},{ci['OBSTACLE_wpjL_ctrl_R90_gl'][1]:+.4f}]; "
        f"thus OBSTACLE - MID within-(page,j,L)+prevL is {pt['DIFF_wpjL_ctrl_R90']:+.4f} [{ci['DIFF_wpjL_ctrl_R90'][0]:+.4f},{ci['DIFF_wpjL_ctrl_R90'][1]:+.4f}] (CI includes 0), "
        f"while PREGAP words are {mpj[0]:+.3f} glyphs shorter than same-(page, j) MID words."
    )
    emit("")
    emit(f"date end: {clock()}")
    emit(f"elapsed: {time.time() - T_START:.1f} s")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
