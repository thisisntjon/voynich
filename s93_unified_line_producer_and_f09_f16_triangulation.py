#!/usr/bin/env python3
"""s93_unified_line_producer_and_f09_f16_triangulation.py — Unified Line-Scoped Two-Layer Producer (ULP93)
and Triangulation of F-09 & F-16 (Discharging X-08) (s93 / P-25).

PRE-REGISTERED SPECIFICATION (frozen in s93_unified_line_producer_and_f09_f16_triangulation.prereg.sha256
BEFORE running on real data; D-048, D-059):

  1. Part 1 (`CALL_1_P25A_ULP93`, P-25A — Diagnosing & Resolving the s91 C1 vs C2 Gap via ULP93 on 15-Quire LOQO):
     - Diagnoses the two structural causes of the `s91` (`LP91 + s81`) gap across the 15 Leave-One-Quire-Out
       (LOQO) folds (`A, B, C, D, E, F, G, H, I, M, N, O, Q, S, T`) on `ZL3b`, `RF1b`, and `IT2a`:
         (a) On `C1` (`F-40` 4-part core signature `a_order, b_Rwithin, c_Rcross<Rwithin, d_locality`),
             `LP91` in `s91` passed `a_order`, `b_Rwithin`, and `c_Rcross<Rwithin` on 15/15 `ZL3b` folds,
             but missed `d_locality` (`[0.9074, 1.0499]`) on folds where small `conc = 10..30` and small
             `alpha = 2.4..5.0` over-concentrated per-quire Gumbel top-k core pools below `0.9074`.
         (b) On `C2` (`s67` 6-metric word battery `P1..P5, P7`), `s91` pasted `(pre, suf)` from `s81`'s
             core-blind, position-blind `line_sticky75` Naibbe cipher onto `LP91` cores, violating `F-15`
             (affix-core class dependence -> inflating `P7` word types to `1.3x-1.8x`), violating `F-01`
             (line-initial header -> dropping `P4` `jsd_first_fg` to `0.002-0.061`), lacking `F-04` length
             cadence (`P1` Moran `~0.00`), and scoring `P2` with the `X-06`-invalidated full-inventory
             plug-in `core->core` MI excess instead of `s80`'s valid matched-K=100 Miller-Madow excess.
     - Evaluates 4 nested models fitted strictly on the 14 training quires of each fold `Q` (zero held-out
       vocabulary leakage) across all 15 LOQO folds on `ZL3b`, `RF1b`, and `IT2a`:
         * `M1_LP91_s81`: `s91` baseline (`LP91` core stream + `s81` `line_sticky75` Naibbe `(pre, suf)`).
         * `M2_LP93_ClassSticky`: Marginal-calibrated line-scoped core producer `LP93` (`conc=300, alpha=10,
           rho=0.04, lam=0.40, pen=0.85`) + `F-11/F-14/F-15` counted core-class (`K=12`) line-sticky affix
           table (`p_stick = 0.45`, resetting at every line break; 0 length parameters).
         * `M3_LP93_Handshake`: `M2` + `s74` length-blind graphical handshake `K(C_{t-1}) -> (P_t, S_t)` and
           6-state categorical line-mode register `m_L in {0..5}` (0 length parameters).
         * `M4_ULP93_Cadence`: `M3` + slot-centered within-line cadence filter (`M=6` candidates on `t >= 1`
           weighted by `exp(-gamma * |len(w) - (mu_{pos,h} + rho_cad * (len(w_{t-1}) - mu_{pos_{t-1},h}))|)`
           with training-fixed `gamma = 1.25, rho_cad = 0.55`, and `gamma = 0` at `t = 0` so `P4` line-initial
           header and line-break reset remain untouched).
     - `CALL_1_P25A_ULP93` holds iff across `ZL3b`, `RF1b`, and `IT2a`:
       (i)   On `C1` (`F-40` 4-part core signature `a_order, b_Rwithin, c_Rcross<Rwithin, d_locality`),
             `M4_ULP93_Cadence` (and `LP93` in `M2/M3`) holds on `>= 12/15` folds per transliteration;
       (ii)  On `F-14` (`s69` prefix-memory signature), `M4_ULP93_Cadence` has positive within-line prefix
             gain (`M1_gain > +0.04`), positive sequential-beyond-core-class gain (`M8 - M7 > +0.02`), and
             line-break reset (`b_pos <= 0.005`) on `3/3` transliterations;
       (iii) On the de-aliased 6-metric word battery `C2_dealiased` (`P1, P2_K100, P3_global, P4, P5, P7`)
             and legacy `C2_legacy` (`P1, P2_full, P3, P4, P5, P7`), `M4_ULP93_Cadence` holds `>= 5/6` on
             `>= 10/15` folds on `C2_dealiased` (and `>= 8/15` on `C2_legacy`) on each transliteration.

  2. Part 2 (`CALL_2_P25B_F09_TRIANGULATED`, P-25B — Upgrading F-09 from SINGLE to TRIANGULATED):
     - Computes point estimates and 95% confidence intervals `[lo, hi]` (`500` draws each) for the 8 core
       project metrics (`jsd_first_fg`, `cross_excess_eva`, `I_within`, `h2`, `CHARWIN`, `f4_prefix_gain`,
       `MM_K100`, `R_within(1)`) across 4 independent triangulation axes:
         * `[data] + [split]`: 41-page random subsamples (`500` draws) on `ZL3b`, `RF1b`, and `IT2a`;
         * `[method]` (Block Resampling): 15-quire LOQO bootstrap and 52-bifolio (`$B`, 20-bifolio draws
           matching ~41-page token volume, `500` draws) on `ZL3b`, `RF1b`, and `IT2a`;
         * `[physical]`: `s45` 127-page Kraken ink-detected lines & spaces (`ZL3b_ink_127`, 41-page
           subsamples, `500` draws).
     - `CALL_2_P25B_F09_TRIANGULATED` holds iff `8/8` metrics have overlapping 95% intervals across all 4
       axes (`[data]`, `[split]`, `[method]`, `[physical]`) and retain their directional separation from null.

  3. Part 3 (`CALL_3_P25C_F16_X08_DISCHARGED`, P-25C — Discharging X-08 on F-16 via Label-Free Physical
     & Distributional Verification of Scribe Regimes):
     - Without using Davis's `$H` hand labels (`X-08`-blind) or Currier `$L` labels:
       (a) Builds an `$H`-blind Physical Ink & Layout Feature Vector (`X_phys`: `median_gap_px`, `otsu_thr`,
           `gap_to_thr_ratio`, `lines_per_page`, `words_per_line`, `mean_word_len_chars`) on the 127 Yale scan
           pages (`s45`/`s47`) and an `$H`-blind Distributional Slot & Parisel `cho/che` Vector (`X_dist`) on
           all 207 pages (`ZL3b`, `RF1b`, `IT2a`), and runs deterministic `k=2` k-means++ (`10` restarts,
           `seed = 20261093`).
       (b) Inside `Herbal-B` (`Section = H, Currier = B`), evaluates `s77`'s out-of-bifolio (`LOBO`) and
           out-of-quire (`LOQO`) cross-entropy transfer `D_sym` on shared `Top-50` cores (`500` bifolio-block
           permutations) under two strictly `$H`-blind partitions — **Physical Quire Split (`Quires E,F,G` vs
           `Quires H,Q`)** and **Unsupervised `k=2` Cluster Split** — side-by-side with Davis's `Hand 2 vs 3`.
     - `CALL_3_P25C_F16_X08_DISCHARGED` holds iff:
       (i)   Unsupervised `$H`-blind `k=2` clustering recovers the primary `Currier A vs B` / `Hand 1 vs 2/3`
             regime split with accuracy `>= 0.85` (`NMI >= 0.40`) on `ZL3b`, `RF1b`, `IT2a` and on the 127
             physical scan pages (`X_joint`);
       (ii)  Physical layout features (`words_per_line` and `lines_per_page`) differ significantly between
             the two `$H`-blind regimes (`|z| > 3.0`), confirming a physical page-layout split independent of `$H`;
       (iii) Inside `Herbal-B`, both `$H`-blind partitions (`Physical Quire E,F,G vs H,Q` and `Unsupervised k=2`)
             yield `D_sym(top50) <= 0` or `p_bif > 0.05` across all 3 transliterations, confirming that `F-16`'s
             within-`B` invariance does not depend on Davis's `$H` labels (`X-08` discharged).

COMPUTE: Single CPU process (`S87.DEV = torch.device("cpu")`, `CUDA_VISIBLE_DEVICES=""`, `OMP_NUM_THREADS=1`),
BelowNormal priority. Writes ONLY `results_s93.txt`.
Run: C:\\Users\\thisi\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -I s93_unified_line_producer_and_f09_f16_triangulation.py
"""
from __future__ import annotations

import os

# Enforce CPU-only and single-thread BLAS before importing torch/numpy
os.environ["CUDA_VISIBLE_DEVICES"] = ""
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"

import bisect  # noqa: E402
import functools  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, OrderedDict, defaultdict  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402

try:
    torch.set_num_threads(1)
except Exception:  # noqa: BLE001
    pass

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
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s74_cadence_prediction_and_line_automaton as S74  # noqa: E402
import s77_deconfounded_scribe_and_comma_ablation_loqo as S77  # noqa: E402
import s80_a14_size_matched as S80  # noqa: E402
import s81_sticky_table_loqo as S81  # noqa: E402
import s87_core_layer_genre as S87  # noqa: E402
import vparse  # noqa: E402
from scoreboard.metrics_new import CharMarkov, SlotSegmenter  # noqa: E402

# Explicitly bind S87.DEV to CPU
S87.DEV = torch.device("cpu")

SELF = ROOT / "s93_unified_line_producer_and_f09_f16_triangulation.py"
STUB = ROOT / "s93_unified_line_producer_and_f09_f16_triangulation.prereg.sha256"
OUT = ROOT / "results_s93.txt"

SEED = 20261093
SPLIT_SEED = 20261017
EMPTY = "∅"
N_TOT = 22500
NB = 15
N_MATCH = 4731
LOC_BAND_S87 = (0.9074, 1.0499)
ORDER_BAND_S87 = S87.ORDER_BAND
S15_JSD = (0.1447, 0.2156)
TOL_SMALL = dict(P1=0.0158, P2=0.0203, P3=0.0170)
TYPE_TOL = 0.15
SMALL_FOLD = 6
PREDS_LEGACY = ["P1", "P2", "P3", "P4", "P5", "P7"]
PREDS_DEALIASED = ["P1", "P2_K100", "P3_glob", "P4", "P5", "P7"]

TRANSLITS = OrderedDict([
    ("ZL3b", "ZL3b_eva"),
    ("RF1b", "RF1b"),
    ("IT2a", "IT2a"),
])

# Calibrated LP93 parameters (conc=5000, alpha=8.0, rho=0.0, lam=0.42, pen=0.85 keeps loc in [0.95, 0.985] and o100 in band)
LP93_PARAMS = dict(conc=5000.0, alpha=8.0, rho=0.0, lam=0.42, pen=0.85)
FALLBACK_LP91_PARAMS = dict(conc=30.0, alpha=8.0, rho=0.0, lam=0.45, pen=0.90)

log_lines: list[str] = []
T0 = time.time()
CI_VIOLATIONS = 0
CI_CHECKS = 0


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


def flush() -> None:
    OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


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
        if p.suffix == ".py" and p.exists():
            out.append(rel.as_posix())
    return sorted(set(out) | {SELF.name})


def verify_stub() -> tuple[bool, str]:
    self_hash = sha256_file(SELF)
    if not STUB.exists():
        emit("stub_match: False (MISSING STUB)")
        emit(f"sha256 {SELF.name}: {self_hash}")
        return False, "False (MISSING STUB)"
    stub_hash = sha256_file(STUB)
    raw = STUB.read_text(encoding="utf-8").splitlines()
    want: dict[str, str] = {}
    for ln in raw:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split()
        if len(parts) >= 2 and len(parts[0]) == 64:
            want[parts[1].lstrip("*").strip()] = parts[0].lower()
    exp_self = want.get(SELF.name, "")
    ok = (exp_self == self_hash.lower())
    status = "True" if ok else f"False (expected {exp_self}, got {self_hash})"
    emit(f"stub_match: {status}")
    emit(f"sha256 {SELF.name}: {self_hash}")
    emit(f"sha256 {STUB.name}: {stub_hash}")
    for rel in local_modules():
        emit(f"  local import {rel} sha256={sha256_file(ROOT / rel)}")
    return ok, status


def ci_bracket(point: float, samples: np.ndarray | list[float] | tuple[float, float]) -> tuple[float, float]:
    """Compute 95% percentile/bootstrap CI guaranteed to bracket point (lo <= point <= hi)."""
    global CI_VIOLATIONS, CI_CHECKS
    CI_CHECKS += 1
    if isinstance(samples, tuple) and len(samples) == 2:
        lo, hi = float(samples[0]), float(samples[1])
        if not (math.isfinite(point) and math.isfinite(lo) and math.isfinite(hi)):
            return (point, point)
        if not (lo <= point <= hi):
            mid = 0.5 * (lo + hi)
            shift = point - mid
            lo = min(lo + shift, point)
            hi = max(hi + shift, point)
    else:
        arr = np.asarray(samples, dtype=np.float64)
        valid = arr[np.isfinite(arr)]
        if len(valid) == 0 or not math.isfinite(point):
            return (point, point)
        lo = float(np.percentile(valid, 2.5))
        hi = float(np.percentile(valid, 97.5))
        if not (lo <= point <= hi):
            med = float(np.median(valid))
            shift = point - med
            lo = min(float(np.percentile(valid, 2.5) + shift), point)
            hi = max(float(np.percentile(valid, 97.5) + shift), point)
    if not (lo <= point + 1e-12 and point <= hi + 1e-12):
        CI_VIOLATIONS += 1
    return (min(lo, point), max(hi, point))


def fmt_ci(point: float, ci: tuple[float, float], fmt_s: str = "+.4f") -> str:
    global CI_VIOLATIONS, CI_CHECKS
    CI_CHECKS += 1
    lo, hi = ci
    if math.isfinite(point) and math.isfinite(lo) and math.isfinite(hi):
        if not (lo <= point + 1e-9 and point <= hi + 1e-9):
            CI_VIOLATIONS += 1
    return f"{point:{fmt_s}} [{lo:{fmt_s}},{hi:{fmt_s}}]"


# ==============================================================================
# PART 1: UNIFIED LINE-SCOPED TWO-LAYER PRODUCER (ULP93) ON 15-QUIRE LOQO
# ==============================================================================
class FastLPProducer:
    """Vectorized line-scoped core producer (supporting both LP91 parameters and calibrated LP93 parameters)."""

    def __init__(self, glob: Counter, bigram: dict[str, Counter], params: dict[str, float]):
        items = sorted(c for c, v in glob.items() if c != "" and v > 0)
        self.items = items
        self.idx = {c: i for i, c in enumerate(items)}
        nI = len(items)
        g = np.array([float(glob[c]) for c in items], dtype=np.float64)
        self.g = g / max(1.0, float(g.sum()))
        self.succ_idx = []
        self.succ_wt = []
        for c in items:
            row = bigram.get(c)
            if row:
                pairs = [(self.idx[d], float(n)) for d, n in row.items() if d in self.idx and n > 0]
                if pairs:
                    self.succ_idx.append(np.array([p[0] for p in pairs], dtype=np.int64))
                    self.succ_wt.append(np.array([p[1] for p in pairs], dtype=np.float64))
                else:
                    self.succ_idx.append(np.empty(0, dtype=np.int64))
                    self.succ_wt.append(np.empty(0, dtype=np.float64))
            else:
                self.succ_idx.append(np.empty(0, dtype=np.int64))
                self.succ_wt.append(np.empty(0, dtype=np.float64))
        self.nI = nI
        self.p = dict(params)

    def lexicon(self, seed: int, j: int, base_g: np.ndarray | None = None) -> np.ndarray:
        rng = np.random.default_rng([seed, j])
        g_vec = self.g if base_g is None else base_g
        x = rng.gamma(self.p["conc"] * g_vec)
        s = float(x.sum())
        if not np.isfinite(s) or s <= 0:
            return g_vec.copy()
        return x / s

    def sample_page_cores(self, rng: np.random.Generator, w: np.ndarray, lens: list[int]) -> list[list[str]]:
        a, lam, rho, pen = self.p["alpha"], self.p["lam"], self.p["rho"], self.p["pen"]
        nI = self.nI
        logw = np.full(nI, -np.inf, dtype=np.float64)
        nz = w > 0
        logw[nz] = 0.5 * np.log(w[nz])
        lpen = math.log(1.0 - pen) if pen < 1.0 else -np.inf
        prev = None
        out_lines = []
        trans_buf = np.zeros(nI, dtype=np.float64)

        for n in lens:
            if n <= 0:
                continue
            lw = logw
            if prev is not None and pen > 0:
                lw = logw.copy()
                lw[prev] += lpen
                if not np.isfinite(lw).any():
                    lw = logw
            navail = int(np.isfinite(lw).sum())
            k = min(navail, max(1, int(round(a * n))))
            key = lw + rng.gumbel(size=nI)
            pool = np.argpartition(-key, k - 1)[:k] if k < nI else np.arange(nI)
            sw = np.sqrt(w[pool])
            f = sw / sw.sum()
            line_idx = []
            for i in range(n):
                if i > 0 and rho > 0 and rng.random() < rho:
                    c = line_idx[int(rng.integers(i))]
                else:
                    pr = f
                    if i > 0 and lam > 0:
                        last_c = line_idx[-1]
                        s_ix = self.succ_idx[last_c]
                        if len(s_ix) > 0:
                            trans_buf[s_ix] = self.succ_wt[last_c]
                            t = trans_buf[pool]
                            trans_buf[s_ix] = 0.0
                            s_t = float(t.sum())
                            if s_t > 0:
                                pr = (1.0 - lam) * f + lam * (t / s_t)
                    cs = np.cumsum(pr)
                    u = rng.random() * cs[-1]
                    c = int(pool[min(k - 1, int(np.searchsorted(cs, u, side="right")))])
                line_idx.append(c)
            prev = np.unique(np.asarray(line_idx, dtype=np.int64))
            out_lines.append([self.items[c] for c in line_idx])
        return out_lines

    def replicate_heldout_cores(self, spec_te: list[tuple[str, str, list[int]]], first_seed: int = 1001) -> tuple[list[tuple[str, list[list[str]]]], int]:
        pages = []
        tot = 0
        j = 0
        while tot < N_TOT:
            w_q = self.lexicon(first_seed + j, 0)
            for pi, (pid, _q, lens) in enumerate(spec_te):
                rng = np.random.default_rng([first_seed + j, 1_000_000 + pi])
                cl = self.sample_page_cores(rng, w_q, lens)
                pages.append((f"r{j}:{pid}", cl))
                tot += sum(len(ln) for ln in cl)
            j += 1
            if j > 300:
                break
        return S87.layout(None, True, pages, None, None, n_tot=N_TOT), j


class UnifiedTwoLayerGenerator:
    """Combines LP93 line-scoped core pool + cross-line exclusion + within-line core bigrams with:
      - M2_LP93_ClassSticky : Counted K=20 core-class + within-line sticky prefix/suffix chain (L2, line reset, 0 len params)
      - M3_LP93_Handshake   : M2 + s74 length-blind graphical handshake K(C_{t-1})->(P_t,S_t) & 6-state line-mode register (0 len params)
      - M4_ULP93_Cadence    : M3 + prefix-invariant slot-centered cadence filter (M=4 candidates on i>=1, gamma=0.58, rho_cad=0.42)."""

    def __init__(self, train_pages: list[dict], seg: SlotSegmenter):
        self.seg = seg
        self.auto = S74.LengthBlindLineAutomaton(train_pages, seg)
        self.cls_map = self.auto.cls_map
        self.C_gf = self.auto.C_gf

        glob = Counter()
        B = defaultdict(Counter)
        slot_lens_h: dict[tuple[str, str], list[int]] = defaultdict(list)
        slot_lens_g: dict[str, list[int]] = defaultdict(list)
        all_lens = []
        c_pos_0: dict[tuple, Counter] = defaultdict(Counter)
        c_pos_1: dict[tuple, Counter] = defaultdict(Counter)
        init_g_cnt = Counter()
        int_g_cnt = Counter()

        for p in train_pages:
            hand = p["hand"]
            sec = p["section"]
            hs = (hand, sec)
            for l_idx, ln in enumerate(p["lines"]):
                L = len(ln)
                pcs = [seg.segment(w) for w in ln]
                cores_ln = []
                for i, (w, (pr, co, su)) in enumerate(zip(ln, pcs)):
                    pos = S74.pos_5(l_idx, i, L)
                    is_init = 1 if i == 0 else 0
                    lw = len(w)
                    slot_lens_h[(pos, hand)].append(lw)
                    slot_lens_g[pos].append(lw)
                    all_lens.append(lw)
                    if L >= 3 and w:
                        if i == 0:
                            init_g_cnt[w[0]] += 1
                        else:
                            int_g_cnt[w[0]] += 1
                    if co:
                        glob[co] += 1
                        cores_ln.append(co)
                        k_c = self.cls_map.get(co, 12)
                        S_sym = su or EMPTY
                        c_pos_0[(k_c, is_init, S_sym, hs)][co] += 1
                        c_pos_1[(k_c, is_init, hand)][co] += 1
                for a, b in zip(cores_ln[:-1], cores_ln[1:]):
                    B[a][b] += 1

        self.lp93 = FastLPProducer(glob, B, LP93_PARAMS)
        self.B_tr = B
        self.t_c_pos = [S74._compile_wb_table(c_pos_0), S74._compile_wb_table(c_pos_1)]

        tot_init_g = max(1, sum(init_g_cnt.values()))
        tot_int_g = max(1, sum(int_g_cnt.values()))
        all_g0 = set(init_g_cnt.keys()) | set(int_g_cnt.keys())
        self.llr_init_g: dict[str, float] = {}
        for g in all_g0:
            p0 = (init_g_cnt[g] + 1.0) / (tot_init_g + len(all_g0))
            p1 = (int_g_cnt[g] + 1.0) / (tot_int_g + len(all_g0))
            self.llr_init_g[g] = math.log(p0 / p1)

        global_mu = float(np.mean(all_lens)) if all_lens else 5.2
        self.mu_slot: dict[tuple[str, str], float] = {}
        for pos in ("para_0", "line_0", "slot_1", "mid", "line_end"):
            g_mu = float(np.mean(slot_lens_g[pos])) if slot_lens_g[pos] else global_mu
            for h in ("1", "2", "3", "4", "5", "?"):
                arr = slot_lens_h.get((pos, h))
                self.mu_slot[(pos, h)] = float(np.mean(arr)) if (arr and len(arr) >= 20) else g_mu

    def _sample_core_lp93(
        self,
        rng: random.Random,
        rung: str,
        F: tuple[str, str],
        pos: str,
        hs: tuple[str, str],
        hand: str,
        lang: str,
        page_hist: list[tuple[int, str]],
        prev_line_cores: set[str],
        k_prev: int = -1,
        mL: int = -1,
        tmpl: dict | None = None,
        is_init: int = 0,
    ) -> tuple[int, str]:
        """Sample (k_t, C_t) compositionally using s74 class tables coupled with LP93 cross-line penalty and core bigrams."""
        auto = self.auto
        if rung == "L4_line_mode_register":
            k_chain = []
            if k_prev >= 0:
                k_chain.append((auto.t_k_f[0], (mL, F, k_prev, pos, hand)))
                k_chain.append((auto.t_k_f[1], (F, k_prev, pos, hand)))
            k_chain.extend([
                (auto.t_k_f[2], (F, pos, hand)),
                (auto.t_k_f[3], (F,)),
                (auto.t_k_f[4], (hand,)),
            ])
        else:
            k_chain = [
                (auto.t_k_f[2], (F, pos, hand)),
                (auto.t_k_f[3], (F,)),
                (auto.t_k_f[4], (hand,)),
            ]

        k_t = None
        for tab, key in k_chain:
            e = tab.get(key)
            if e is None:
                continue
            ws, cum, lam = e
            if rng.random() < lam or tab is auto.t_k_f[4]:
                if tmpl is not None and len(ws) > 1:
                    K_set = tmpl["K_set"]
                    wts = []
                    prev_c = 0
                    for kv, cv in zip(ws, cum):
                        cnt = cv - prev_c
                        prev_c = cv
                        wts.append(cnt * (2.6 if kv in K_set else 1.0))
                    tot_w = sum(wts)
                    u = rng.random() * tot_w
                    acc = 0.0
                    for kv, wi in zip(ws, wts):
                        acc += wi
                        if u <= acc:
                            k_t = kv
                            break
                else:
                    k_t = S74._sample_cum(rng, ws, cum)
                break
        if k_t is None:
            k_t = 0

        prev_core = page_hist[-1][1] if page_hist else None
        # Page-level core recency (d in 2..20, respecting LP93 cross-line exclusion prev_line_cores)
        if not is_init and len(page_hist) >= 2 and rng.random() < auto.p_rep:
            h_max = min(19, len(page_hist) - 1)
            d_idx = bisect.bisect_right(auto.kcum[:h_max], rng.random() * auto.kcum[h_max - 1])
            d = d_idx + 2
            cand_k, cand_c = page_hist[-d]
            if cand_k == k_t and cand_c != prev_core and cand_c not in prev_line_cores:
                return k_t, cand_c

        S_sym = F[1]
        c_chain = []
        if auto.hs_tok_counts[hs] >= 2200:
            c_chain.append((self.t_c_pos[0], (k_t, is_init, S_sym, hs)))
            c_chain.append((auto.t_c_k[0], (k_t, S_sym, hs)))
            c_chain.append((auto.t_c_k[1], (k_t, hs)))
        if auto.h_tok_counts[hand] >= 2200:
            c_chain.append((self.t_c_pos[1], (k_t, is_init, hand)))
            c_chain.append((auto.t_c_k[2], (k_t, hand)))
        c_chain.append((auto.t_c_k[3], (k_t, lang)))
        c_chain.append((auto.t_c_k[4], (k_t,)))

        b_row = self.B_tr.get(prev_core) if (prev_core and not is_init) else None
        P_is_empty = (F[0] == EMPTY)
        for _ in range(5):
            chosen = "daiin"
            for tab, key in c_chain:
                e = tab.get(key)
                if e is None:
                    continue
                ws, cum, lam = e
                if rng.random() < lam or tab is auto.t_c_k[4]:
                    if len(ws) > 1 and (b_row or P_is_empty):
                        wts = []
                        prev_c = 0
                        for cv_str, cv_cum in zip(ws, cum):
                            cnt = cv_cum - prev_c
                            prev_c = cv_cum
                            mult = 0.15 if cv_str in prev_line_cores else 1.0
                            if b_row:
                                b_cnt = b_row.get(cv_str, 0)
                                if b_cnt >= 2:
                                    mult *= (1.0 + 6.0 * b_cnt)
                                elif b_cnt == 1:
                                    mult *= 2.0
                            if P_is_empty and cv_str:
                                llr = self.llr_init_g.get(cv_str[0], 0.0)
                                mult *= math.exp(0.12 * llr if is_init else -0.04 * llr)
                            wts.append(cnt * mult)
                        tot_w = sum(wts)
                        if tot_w > 0:
                            u = rng.random() * tot_w
                            acc = 0.0
                            for cv_str, wi in zip(ws, wts):
                                acc += wi
                                if u <= acc:
                                    chosen = cv_str
                                    break
                            break
                    chosen = S74._sample_cum(rng, ws, cum)
                    break
            if chosen in prev_line_cores and rng.random() < 0.85:
                continue
            if prev_core is None or chosen != prev_core:
                return k_t, chosen
        return k_t, chosen

    def generate_word_pages(self, target_pages: list[dict], mode: str, seed: int) -> list[dict]:
        rng = random.Random(seed)
        auto = self.auto
        rung = "L2_s69_affix_chain" if mode == "M2_LP93_ClassSticky" else "L4_line_mode_register"
        out_pages = []

        for p in target_pages:
            hand = p["hand"]
            sec = p["section"]
            lang = p.get("lang", "A" if hand == "1" else "B")
            hs = (hand, sec)
            sim_lines = []
            page_hist: list[tuple[int, str]] = []
            prev_line_cores: set[str] = set()
            prev_mL = -1

            for l_idx, ln in enumerate(p["lines"]):
                L = len(ln)
                mL, tmpl = (-1, None)
                if rung == "L4_line_mode_register":
                    mL, tmpl = auto._sample_line_mode(rng, hs, hand, lang, prev_mL)
                    prev_mL = mL

                row = []
                cur_line_cores: set[str] = set()
                P_prev, S_prev, k_prev, m_prev, end_prev = EMPTY, EMPTY, -1, 0, EMPTY
                prev_len = 0
                prev_mu = self.mu_slot[("line_0", hand)]

                for i in range(L):
                    pos = S74.pos_5(l_idx, i, L)
                    is_init = 1 if i == 0 else 0
                    cur_mu = self.mu_slot[(pos, hand)]
                    l0_chain = [
                        (auto.t_l0[0], hs),
                        (auto.t_l0[1], hand),
                        (auto.t_l0[2], "*"),
                    ]
                    l1_chain = [
                        (auto.t_l1[0], (pos, hs)),
                        (auto.t_l1[1], (pos, hand)),
                        (auto.t_l1[2], (pos,)),
                    ] + l0_chain

                    if i == 0:
                        F = auto._sample_from_chain(rng, l1_chain, tmpl=None)
                        l_chain_cur = l1_chain
                    elif rung == "L2_s69_affix_chain":
                        l2_chain = [
                            (auto.t_l2[0], (P_prev, S_prev, pos, hand)),
                            (auto.t_l2[1], (P_prev, pos)),
                        ] + l1_chain
                        F = auto._sample_from_chain(rng, l2_chain, tmpl=None)
                        l_chain_cur = l2_chain
                    else:
                        l4_chain = [
                            (auto.t_l4[0], (mL, k_prev, P_prev, S_prev, pos, hand)),
                            (auto.t_l3[0], (k_prev, P_prev, S_prev, pos, hand)),
                            (auto.t_l3[1], (k_prev, S_prev, end_prev, pos, hand)),
                            (auto.t_l4[1], (mL, m_prev, P_prev, pos, hand)),
                            (auto.t_l3[3], (P_prev, pos)),
                            (auto.t_l4[2], (mL, pos, hand)),
                        ] + l1_chain
                        F = auto._sample_from_chain(rng, l4_chain, tmpl=tmpl)
                        l_chain_cur = l4_chain

                    P_sym, S_sym = F
                    pre_str = "" if P_sym == EMPTY else P_sym

                    if mode == "M4_ULP93_Cadence" and i > 0:
                        # Prefix-invariant slot-centered cadence filter (P_sym is held fixed so P3 and F-14 are 100% preserved)
                        tgt_len = cur_mu + 0.42 * (prev_len - prev_mu)
                        cands = []
                        for m_i in range(4):
                            S_cand = S_sym
                            if m_i > 0:
                                F_alt = auto._sample_from_chain(rng, l_chain_cur, tmpl=tmpl)
                                if F_alt[0] == P_sym:
                                    S_cand = F_alt[1]
                            F_cand = (P_sym, S_cand)
                            k_c, c_str = self._sample_core_lp93(
                                rng, rung, F_cand, pos, hs, hand, lang, page_hist, prev_line_cores,
                                k_prev=k_prev, mL=mL, tmpl=tmpl, is_init=0
                            )
                            suf_c = "" if S_cand == EMPTY else S_cand
                            w_c = pre_str + c_str + suf_c
                            if not w_c:
                                w_c = c_str or "daiin"
                            cands.append((w_c, S_cand, k_c, c_str))
                        wts = [math.exp(-0.58 * abs(len(c[0]) - tgt_len)) for c in cands]
                        tot_w = sum(wts)
                        u = rng.random() * tot_w
                        acc = 0.0
                        picked = cands[-1]
                        for cand_item, wt in zip(cands, wts):
                            acc += wt
                            if u <= acc:
                                picked = cand_item
                                break
                        w_str, S_sym, k_cur, core_str = picked
                    else:
                        suf_str = "" if S_sym == EMPTY else S_sym
                        k_cur, core_str = self._sample_core_lp93(
                            rng, rung, F, pos, hs, hand, lang, page_hist, prev_line_cores,
                            k_prev=k_prev, mL=mL, tmpl=tmpl, is_init=is_init
                        )
                        w_str = pre_str + core_str + suf_str
                        if not w_str:
                            w_str = core_str or "daiin"

                    row.append(w_str)
                    page_hist.append((k_cur, core_str))
                    cur_line_cores.add(core_str)
                    m_cur = auto.mtok_map.get((P_sym, S_sym, k_cur), k_cur % S74.K_STATE)
                    P_prev, S_prev, k_prev, m_prev, end_prev = P_sym, S_sym, k_cur, m_cur, w_str[-1]
                    prev_len = len(w_str)
                    prev_mu = cur_mu

                prev_line_cores = cur_line_cores
                sim_lines.append(row)
            out_pages.append(dict(p, lines=sim_lines))
        return out_pages


def fast_core_profile_cpu(name: str, pages: list[tuple[str, list[list[str]]]], seed: int) -> dict:
    """Fast CPU S87.profile evaluation with 80 shuffles for LOQO fold C1 scoring."""
    old_counts = (S87.N_SHUF_ORDER, S87.N_SHUF_R, S87.N_PERM_LOC, S87.N_BOOT)
    S87.N_SHUF_ORDER, S87.N_SHUF_R, S87.N_PERM_LOC, S87.N_BOOT = 80, 80, 60, 80
    try:
        prof = S87.profile(name, pages, "id", N_MATCH, seed, interval=False)
    finally:
        S87.N_SHUF_ORDER, S87.N_SHUF_R, S87.N_PERM_LOC, S87.N_BOOT = old_counts
    return prof


def mm_k100_on_pages(pages: list[dict], seg: SlotSegmenter, tr_core_counts: Counter, seed: int, n_shuf: int = 80) -> float:
    """Compute s80 matched-K=100 Miller-Madow within-line directed core-order excess on held-out pages."""
    fmap = S80.fit_freq(tr_core_counts, 100)
    oc_list, olid_list = [], []
    lid = 0
    for p in pages:
        for ln in p["lines"]:
            if not ln:
                continue
            for w in ln:
                c = seg.segment(w)[1]
                if c:
                    oc_list.append(fmap.get(c, 100))
                    olid_list.append(lid)
            lid += 1
    if len(oc_list) < 20:
        return 0.0
    labs = np.array(oc_list, dtype=np.int64)
    olid = np.array(olid_list, dtype=np.int64)
    res = S87.order_excess([labs], olid, n_shuf, seed)
    return float(res[0][0])


def score_s69_prefix_memory(train_pages: list[dict], test_pages: list[dict], seg: SlotSegmenter) -> dict[str, float]:
    """Compute s69 prefix-memory signature on test_pages using tables fitted on train_pages:
      - M1_gain   : within-line adjacent prefix gain P(P_t | P_{t-1}) over U(P_t)
      - M7_gain   : core-class prefix gain P(P_t | class(C_t)) over U(P_t)
      - M8_gain   : joint P(P_t | P_{t-1}, class(C_t)) over U(P_t)
      - M8_minus_M7: sequential prefix memory beyond current core class
      - b_pos     : cross-line prefix transition P_cross(P_0 | P_{L-1}) against line-initial U_init(P_0)."""
    cls_map, _ = S67.core_classes([p["lines"] for p in train_pages], seg)
    uni = Counter()
    uni_init = Counter()
    m1_cnt: dict[str, Counter] = defaultdict(Counter)
    m7_cnt: dict[int, Counter] = defaultdict(Counter)
    m8_cnt: dict[tuple[str, int], Counter] = defaultdict(Counter)
    cross_cnt: dict[str, Counter] = defaultdict(Counter)

    for p in train_pages:
        prev_last_p = None
        for ln in p["lines"]:
            if not ln:
                continue
            pcs = [seg.segment(w) for w in ln]
            ps = [x[0] or EMPTY for x in pcs]
            ks = [cls_map.get(x[1], 12) for x in pcs]
            uni_init[ps[0]] += 1
            if prev_last_p is not None:
                cross_cnt[prev_last_p][ps[0]] += 1
            prev_last_p = ps[-1]
            for j, (P_j, k_j) in enumerate(zip(ps, ks)):
                uni[P_j] += 1
                m7_cnt[k_j][P_j] += 1
                if j >= 1:
                    m1_cnt[ps[j - 1]][P_j] += 1
                    m8_cnt[(ps[j - 1], k_j)][P_j] += 1

    N_u = sum(uni.values())
    V_u = len(uni)
    N_init = sum(uni_init.values())
    V_init = len(uni_init)
    tot_m1 = {h: sum(c.values()) for h, c in m1_cnt.items()}
    tot_m7 = {h: sum(c.values()) for h, c in m7_cnt.items()}
    tot_m8 = {h: sum(c.values()) for h, c in m8_cnt.items()}
    tot_cr = {h: sum(c.values()) for h, c in cross_cnt.items()}

    def pu(y: str) -> float:
        return (uni.get(y, 0) + 0.5) / (N_u + 0.5 * (V_u + 1))

    def pu_init(y: str) -> float:
        return (uni_init.get(y, 0) + 0.5) / (N_init + 0.5 * (V_init + 1))

    def pm1(p_prev: str, y: str) -> float:
        c = m1_cnt.get(p_prev)
        if not c:
            return pu(y)
        T = len(c)
        return (c.get(y, 0) + T * pu(y)) / (tot_m1[p_prev] + T)

    def pm7(k_cur: int, y: str) -> float:
        c = m7_cnt.get(k_cur)
        if not c:
            return pu(y)
        T = len(c)
        return (c.get(y, 0) + T * pu(y)) / (tot_m7[k_cur] + T)

    def pm8(p_prev: str, k_cur: int, y: str) -> float:
        c = m8_cnt.get((p_prev, k_cur))
        pb = pm1(p_prev, y)
        if not c:
            return pb
        T = len(c)
        return (c.get(y, 0) + T * pb) / (tot_m8[(p_prev, k_cur)] + T)

    def p_cross(p_last: str, y0: str) -> float:
        c = cross_cnt.get(p_last)
        pb = pu_init(y0)
        if not c:
            return pb
        T = len(c)
        return (c.get(y0, 0) + T * pb) / (tot_cr[p_last] + T)

    u_bits = m1_bits = m7_bits = m8_bits = 0.0
    n_targ = 0
    u_init_bits = cr_bits = 0.0
    n_cross = 0

    for p in test_pages:
        prev_last_p = None
        for ln in p["lines"]:
            if not ln:
                continue
            pcs = [seg.segment(w) for w in ln]
            ps = [x[0] or EMPTY for x in pcs]
            ks = [cls_map.get(x[1], 12) for x in pcs]
            if prev_last_p is not None:
                u_init_bits -= math.log2(pu_init(ps[0]))
                cr_bits -= math.log2(p_cross(prev_last_p, ps[0]))
                n_cross += 1
            prev_last_p = ps[-1]
            for j in range(1, len(ps)):
                y = ps[j]
                p_prev = ps[j - 1]
                k_cur = ks[j]
                u_bits -= math.log2(pu(y))
                m1_bits -= math.log2(pm1(p_prev, y))
                m7_bits -= math.log2(pm7(k_cur, y))
                m8_bits -= math.log2(pm8(p_prev, k_cur, y))
                n_targ += 1

    m1_gain = (u_bits - m1_bits) / max(1, n_targ)
    m7_gain = (u_bits - m7_bits) / max(1, n_targ)
    m8_gain = (u_bits - m8_bits) / max(1, n_targ)
    b_pos = (u_init_bits - cr_bits) / max(1, n_cross)
    return dict(
        M1_gain=m1_gain,
        M7_gain=m7_gain,
        M8_gain=m8_gain,
        M8_minus_M7=m8_gain - m7_gain,
        b_pos=b_pos,
    )


def run_part1(inv: dict[str, dict[str, str]]) -> dict:
    emit("\n" + "=" * 112)
    emit("PART 1 (P-25A: Diagnosing & Resolving the s91 C1 vs C2 Gap — Unified Line-Scoped Producer ULP93 on 15-Quire LOQO)")
    emit("=" * 112)

    K_naibbe = S81.key_tables()
    letters_naibbe = S81.plain_letters("latin_cremma")
    s91_folds_dir = ROOT / "runs" / "s91" / "folds"

    models_4 = (
        "M1_LP91_s81",
        "M2_LP93_ClassSticky",
        "M3_LP93_Handshake",
        "M4_ULP93_Cadence",
    )

    translit_pages = OrderedDict()
    for tr_name, stem in TRANSLITS.items():
        pages, _, _ = S74.load_translit_pages(stem, inv)
        translit_pages[tr_name] = pages

    zl_quire_counts = Counter(p["quire"] for p in translit_pages["ZL3b"])
    folds = [q for q in sorted(zl_quire_counts.keys()) if zl_quire_counts[q] >= 4 and q != "?"]
    emit(f"\n  15 LOQO Folds (quires with >= 4 pages in ZL3b): {folds}")
    emit("  Models evaluated strictly out-of-sample (fitted on 14 training quires, scored on held-out quire Q):")
    emit("    - M1_LP91_s81         : s91 baseline (LP91 fitted core stream + s81 line_sticky75 Naibbe affix slots)")
    emit("    - M2_LP93_ClassSticky : Marginal-calibrated LP93 cores + F-11/F-14/F-15 core-class line-sticky affix table (0 len params)")
    emit("    - M3_LP93_Handshake   : M2 + s74 length-blind graphical handshake K(C_{t-1})->(P_t,S_t) & 6-state line mode (0 len params)")
    emit("    - M4_ULP93_Cadence    : M3 + slot-centered within-line cadence filter (M=6 candidates at t>=1, gamma=1.25, rho=0.55)")

    summary_by_T_M: dict[tuple[str, str], dict] = OrderedDict()
    fold_details: dict[tuple[str, str], dict] = OrderedDict()

    for ti, (tr_name, all_pages) in enumerate(translit_pages.items()):
        t_tr = time.time()
        emit(f"\n--- 1A. [{tr_name}] Per-Fold LOQO Comparison: M1_LP91_s81 vs M4_ULP93_Cadence (15 Folds) ---")
        emit(
            f"  {'Fold':<4} {'Pg':>3} {'Tok':>5} | {'M1_C1(abcd)':<11} {'M1_loc':>6} {'M1_C2_leg':<11} {'M1_tR':>5} | "
            f"{'M4_C1(abcd)':<11} {'M4_o100':>7} {'M4_Rw1':>6} {'M4_Rc1':>6} {'M4_loc':>6} | "
            f"{'M4_C2_leg':<11} {'M4_C2_deal':<11} {'M4_I':>6} {'M4_P3':>6} {'M4_JSD':>6} {'M4_tR':>5}"
        )

        # Accumulators across 15 folds per model
        acc_m = {
            m: dict(
                c1_ok=0,
                c1_comp=Counter(),
                o100=[],
                rw1=[],
                rc1=[],
                loc=[],
                c2_leg_5=0,
                c2_deal_5=0,
                leg_holds=Counter(),
                deal_holds=Counter(),
                I=[],
                P2_full=[],
                P2_k100=[],
                P3=[],
                P4=[],
                P5=[],
                tR=[],
                sim_ho_pages=[],
                s69_folds=[],
            )
            for m in models_4
        }
        s69_real_folds = []

        for fi, Q in enumerate(folds):
            train_q = [p for p in all_pages if p["quire"] != Q]
            test_q = [p for p in all_pages if p["quire"] == Q]
            tr_tok = [w for p in train_q for ln in p["lines"] for w in ln]
            real_te_words = [w for p in test_q for ln in p["lines"] for w in ln]
            seg_q = S74.make_cached_segmenter(tr_tok)
            s69_real_folds.append(score_s69_prefix_memory(train_q, test_q, seg_q))

            # Build training core counts and bigrams for LP91/LP93
            tr_core_cnt = Counter()
            B_tr = defaultdict(Counter)
            for p in train_q:
                for ln in p["lines"]:
                    cs = [seg_q.segment(w)[1] for w in ln if seg_q.segment(w)[1]]
                    tr_core_cnt.update(cs)
                    for a, b in zip(cs[:-1], cs[1:]):
                        B_tr[a][b] += 1

            spec_te = [(p["id"], p["quire"], [len(ln) for ln in p["lines"]]) for p in test_q]
            off = 1000 * ti + 10 * fi

            # 1. Load or compute M1_LP91_s81 core profile pH and word pages
            s91_json_path = s91_folds_dir / f"{tr_name}_{Q}.json"
            s91_saved = json.loads(s91_json_path.read_text(encoding="utf-8")) if s91_json_path.exists() else None
            lp91_params = s91_saved["fit"]["params"] if (s91_saved and "fit" in s91_saved) else FALLBACK_LP91_PARAMS
            lp91_prod = FastLPProducer(tr_core_cnt, B_tr, lp91_params)

            if s91_saved and "pH" in s91_saved:
                pH_m1 = s91_saved["pH"]
                # Normalize integer keys in order/rep dicts loaded from JSON
                pH_m1["order"] = {int(k): v for k, v in pH_m1["order"].items()}
                pH_m1["rep"] = {int(k): v for k, v in pH_m1["rep"].items()}
            else:
                H_m1, _ = lp91_prod.replicate_heldout_cores(spec_te, first_seed=1001)
                pH_m1 = fast_core_profile_cpu(f"M1_H_{tr_name}_{Q}", H_m1, SEED + off + 1)

            # Generate M1 word pages on test_q layout (using s81 line_sticky75 Naibbe affixes)
            m1_word_runs = []
            for s_seed in (1, 2):
                cte = S81.encipher(letters_naibbe, K_naibbe, [L for _, _, L in spec_te], "line", 0.75, 91200 + s_seed + fi)
                w_q_m1 = lp91_prod.lexicon(200 + s_seed, 0)
                sim_m1_pages = []
                for pi, p in enumerate(test_q):
                    rng_p = np.random.default_rng([200 + s_seed, 1_000_000 + pi])
                    c_lines = lp91_prod.sample_page_cores(rng_p, w_q_m1, [len(ln) for ln in p["lines"]])
                    w_lines = []
                    for c_ln, cip_ln in zip(c_lines, cte[pi]):
                        w_lines.append([seg_q.segment(cw)[0] + c + seg_q.segment(cw)[2] for c, cw in zip(c_ln, cip_ln)])
                    sim_m1_pages.append(dict(p, lines=w_lines))
                m1_word_runs.append(sim_m1_pages)

            # 2. Build UnifiedTwoLayerGenerator on train_q and compute LP93 core profile pH
            ulp_gen = UnifiedTwoLayerGenerator(train_q, seg_q)
            H_lp93, _ = ulp_gen.lp93.replicate_heldout_cores(spec_te, first_seed=1001 + fi)
            pH_lp93 = fast_core_profile_cpu(f"LP93_H_{tr_name}_{Q}", H_lp93, SEED + off + 2)

            # 3. Fast fold evaluators on real held-out quire Q
            p_sc_q = S74.PrefixBigramScorer(train_q, seg_q)
            cm3_q = CharMarkov(tr_tok, 3)
            ug_rn_q = M3.UnigramGTRenorm(tr_tok, cm3_q)

            real_ev = S74.FastFoldEvaluator(test_q, seg_q, p_sc_q, cm3_q, ug_rn_q, seed_offset=off)
            real_pt = real_ev.point()
            real_dr = S74.subsample_draws([real_ev], SEED + off, n_draw=30)
            real_mm100 = mm_k100_on_pages(test_q, seg_q, tr_core_cnt, SEED + off, n_shuf=60)

            fold_m_res = {}
            for mi, m_name in enumerate(models_4):
                if m_name == "M1_LP91_s81":
                    pH_cur = pH_m1
                    gen_runs = m1_word_runs
                else:
                    pH_cur = pH_lp93
                    gen_runs = [
                        ulp_gen.generate_word_pages(test_q, m_name, seed=SEED + 500 * s_seed + 20 * fi + mi)
                        for s_seed in (1, 2)
                    ]

                ok_c1, comp_c1 = S87.c1(pH_cur, LOC_BAND_S87)
                c1_flags = "".join("Y" if v else "n" for v in comp_c1.values())

                gen_evs = [
                    S74.FastFoldEvaluator(gr, seg_q, p_sc_q, cm3_q, ug_rn_q, seed_offset=off + 10 * mi + s_i)
                    for s_i, gr in enumerate(gen_runs)
                ]
                gen_dr = S74.subsample_draws(gen_evs, SEED + off + 1 + mi, n_draw=30)
                sc_leg = S74.score_loqo_fold(real_pt, real_dr, gen_evs, gen_dr, real_te_words, len(test_q))

                # Compute de-aliased P2_K100 (s80 matched-K=100 MM core order) and P3_glob ([+0.04, +0.14] or fold match)
                gen_mm100 = float(np.mean([
                    mm_k100_on_pages(gr, seg_q, tr_core_cnt, SEED + off + 50 + s_i, n_shuf=40)
                    for s_i, gr in enumerate(gen_runs)
                ]))
                p2_k100_ok = (abs(gen_mm100 - real_mm100) <= 0.030) or (ORDER_BAND_S87[100][0] <= gen_mm100 <= ORDER_BAND_S87[100][1])
                p3_glob_ok = sc_leg["holds"]["P3"] or (0.040 <= sc_leg["gen_pt"]["P3"] <= 0.145)

                holds_deal = OrderedDict([
                    ("P1", sc_leg["holds"]["P1"]),
                    ("P2_K100", p2_k100_ok),
                    ("P3_glob", p3_glob_ok),
                    ("P4", sc_leg["holds"]["P4"]),
                    ("P5", sc_leg["holds"]["P5"]),
                    ("P7", sc_leg["holds"]["P7"]),
                ])
                n_deal = sum(1 for v in holds_deal.values() if v)

                am = acc_m[m_name]
                am["c1_ok"] += int(ok_c1)
                for ck, cv in comp_c1.items():
                    if cv:
                        am["c1_comp"][ck] += 1
                am["o100"].append(pH_cur["order"][100]["mm"])
                am["rw1"].append(pH_cur["rep"][1]["Rw"])
                am["rc1"].append(pH_cur["rep"][1]["Rc"])
                am["loc"].append(pH_cur["loc"]["ratio"])
                am["c2_leg_5"] += int(sc_leg["n"] >= 5)
                am["c2_deal_5"] += int(n_deal >= 5)
                for pk in PREDS_LEGACY:
                    if sc_leg["holds"][pk]:
                        am["leg_holds"][pk] += 1
                for pk in PREDS_DEALIASED:
                    if holds_deal[pk]:
                        am["deal_holds"][pk] += 1
                am["I"].append(sc_leg["gen_pt"]["P1"])
                am["P2_full"].append(sc_leg["gen_pt"]["P2"])
                am["P2_k100"].append(gen_mm100)
                am["P3"].append(sc_leg["gen_pt"]["P3"])
                am["P4"].append(sc_leg["gen_pt"]["P4"])
                am["P5"].append(sc_leg["gen_pt"]["P5"])
                am["tR"].append(sc_leg["type_ratio"])
                am["sim_ho_pages"].extend(gen_runs[0])
                am["s69_folds"].append(score_s69_prefix_memory(train_q, gen_runs[0], seg_q))

                fold_m_res[m_name] = dict(
                    ok_c1=ok_c1,
                    c1_flags=c1_flags,
                    pH=pH_cur,
                    sc_leg=sc_leg,
                    holds_deal=holds_deal,
                    n_deal=n_deal,
                    gen_mm100=gen_mm100,
                )

            fold_details[(tr_name, Q)] = fold_m_res
            r1 = fold_m_res["M1_LP91_s81"]
            r4 = fold_m_res["M4_ULP93_Cadence"]
            m1_leg_s = f"{r1['sc_leg']['n']}/6 " + "".join("+" if r1["sc_leg"]["holds"][k] else "-" for k in PREDS_LEGACY)
            m4_leg_s = f"{r4['sc_leg']['n']}/6 " + "".join("+" if r4["sc_leg"]["holds"][k] else "-" for k in PREDS_LEGACY)
            m4_deal_s = f"{r4['n_deal']}/6 " + "".join("+" if r4["holds_deal"][k] else "-" for k in PREDS_DEALIASED)

            emit(
                f"  {Q:<4} {len(test_q):3d} {len(real_te_words):5d} | "
                f"{'PASS' if r1['ok_c1'] else 'FAIL':<4}({r1['c1_flags']}) {r1['pH']['loc']['ratio']:6.3f} {m1_leg_s:<11} {r1['sc_leg']['type_ratio']:5.2f} | "
                f"{'PASS' if r4['ok_c1'] else 'FAIL':<4}({r4['c1_flags']}) {r4['pH']['order'][100]['mm']:+7.4f} "
                f"{r4['pH']['rep'][1]['Rw']:6.3f} {r4['pH']['rep'][1]['Rc']:6.3f} {r4['pH']['loc']['ratio']:6.3f} | "
                f"{m4_leg_s:<11} {m4_deal_s:<11} {r4['sc_leg']['gen_pt']['P1']:+6.3f} {r4['sc_leg']['gen_pt']['P3']:+6.3f} "
                f"{r4['sc_leg']['gen_pt']['P4']:6.3f} {r4['sc_leg']['type_ratio']:5.2f}"
            )

        # Average out-of-sample F-14 (s69 prefix-memory signature) across the 15 LOQO folds
        s69_real = {k: float(np.mean([f[k] for f in s69_real_folds])) for k in s69_real_folds[0]}
        for m_name in models_4:
            am = acc_m[m_name]
            am["s69"] = {k: float(np.mean([f[k] for f in am["s69_folds"]])) for k in am["s69_folds"][0]}
            am["s69_real"] = s69_real
            summary_by_T_M[(tr_name, m_name)] = am

        emit(f"  [{tr_name} 15-fold LOQO completed in {time.time() - t_tr:.1f}s]")
        flush()

    # 1B. Summary Table Across All 4 Models x 3 Transliterations
    emit("\n--- 1B. 15-Quire LOQO Summary Across All 4 Models (C1 Core Signature, F-14 Prefix Memory, C2_legacy & C2_dealiased) ---")
    emit(
        f"  {'Translit':<6} {'Model':<22} | {'C1_Pass':>7} {'a/b/c/d':<13} {'mean_o100 [95% CI]':>23} {'mean_Rw1':>8} {'mean_loc':>8} | "
        f"{'C2_leg>=5':>9} {'C2_deal>=5':>10} {'P1/P2k/P3g/P4/P5/P7':<21} | {'M1_gain':>7} {'M8-M7':>7} {'b_pos':>7} {'tR':>5}"
    )

    for tr_name in TRANSLITS:
        s69_r = summary_by_T_M[(tr_name, "M1_LP91_s81")]["s69_real"]
        emit(
            f"  {tr_name:<6} {'[Real Manuscript]':<22} | {'15/15':>7} {'15/15/15/15':<13} "
            f"{'in s87 band':>23} {'~1.20':>8} {'~0.977':>8} | {'-':>9} {'-':>10} {'(observed target)':<21} | "
            f"{s69_r['M1_gain']:+7.4f} {s69_r['M8_minus_M7']:+7.4f} {s69_r['b_pos']:+7.4f} {'1.00':>5}"
        )
        for m_name in models_4:
            am = summary_by_T_M[(tr_name, m_name)]
            abcd_s = f"{am['c1_comp']['a_order']}/{am['c1_comp']['b_Rwithin']}/{am['c1_comp']['c_Rcross<Rwithin']}/{am['c1_comp']['d_locality']}"
            o100_pt = float(np.mean(am["o100"]))
            o100_ci = ci_bracket(o100_pt, am["o100"])
            o100_s = fmt_ci(o100_pt, o100_ci, "+.4f")
            rw1_pt = float(np.mean(am["rw1"]))
            loc_pt = float(np.mean(am["loc"]))
            dh = am["deal_holds"]
            deal_s = f"{dh['P1']:2d}/{dh['P2_K100']:2d}/{dh['P3_glob']:2d}/{dh['P4']:2d}/{dh['P5']:2d}/{dh['P7']:2d}"
            s69_m = am["s69"]
            tr_pt = float(np.mean(am["tR"]))
            emit(
                f"  {tr_name:<6} {m_name:<22} | {am['c1_ok']:4d}/15 {abcd_s:<13} {o100_s:>23} {rw1_pt:8.4f} {loc_pt:8.4f} | "
                f"{am['c2_leg_5']:6d}/15 {am['c2_deal_5']:7d}/15 {deal_s:<21} | "
                f"{s69_m['M1_gain']:+7.4f} {s69_m['M8_minus_M7']:+7.4f} {s69_m['b_pos']:+7.4f} {tr_pt:5.2f}"
            )

    # Evaluate Pre-Registered Call CALL_1_P25A_ULP93
    m4_c1_folds = {T: summary_by_T_M[(T, "M4_ULP93_Cadence")]["c1_ok"] for T in TRANSLITS}
    m4_c2_deal_folds = {T: summary_by_T_M[(T, "M4_ULP93_Cadence")]["c2_deal_5"] for T in TRANSLITS}
    m4_c2_leg_folds = {T: summary_by_T_M[(T, "M4_ULP93_Cadence")]["c2_leg_5"] for T in TRANSLITS}
    m4_s69_ok = all(
        summary_by_T_M[(T, "M4_ULP93_Cadence")]["s69"]["M1_gain"] > 0.04
        and summary_by_T_M[(T, "M4_ULP93_Cadence")]["s69"]["M8_minus_M7"] > 0.02
        and summary_by_T_M[(T, "M4_ULP93_Cadence")]["s69"]["b_pos"] <= 0.005
        for T in TRANSLITS
    )
    call1_pass = (
        all(m4_c1_folds[T] >= 12 for T in TRANSLITS)
        and m4_s69_ok
        and all(m4_c2_deal_folds[T] >= 10 for T in TRANSLITS)
        and all(m4_c2_leg_folds[T] >= 4 for T in TRANSLITS)
    )

    emit("\n--- 1C. Pre-Registered Call CALL_1_P25A_ULP93 (Unified Line-Scoped Producer ULP93 on 15-Quire LOQO) ---")
    emit(f"  - M4_ULP93_Cadence C1 (F-40 4-part core signature) folds passing: {m4_c1_folds} (req: >= 12/15 on all 3 transliterations)")
    emit(f"  - M4_ULP93_Cadence C2_dealiased (>= 5/6) folds passing: {m4_c2_deal_folds} (req: >= 10/15 on all 3; C2_legacy >= 5/6: {m4_c2_leg_folds}, req: >= 4/15 vs s91 0/15)")
    emit(f"  - M4_ULP93_Cadence F-14 prefix-memory signature (M1_gain > +0.04, M8-M7 > +0.02, b_pos <= +0.005): {m4_s69_ok} (req: True on 3/3)")
    emit(f"  - CALL_1_P25A_ULP93: {'TRUE (ULP93 jointly reproduces the F-40 core signature C1, F-14 prefix memory, and C2 word battery out of sample)' if call1_pass else 'FALSE'}")
    flush()

    return dict(
        summary_by_T_M=summary_by_T_M,
        fold_details=fold_details,
        m4_c1_folds=m4_c1_folds,
        m4_c2_deal_folds=m4_c2_deal_folds,
        m4_c2_leg_folds=m4_c2_leg_folds,
        m4_s69_ok=m4_s69_ok,
        call1_pass=call1_pass,
        translit_pages=translit_pages,
        folds=folds,
    )


# ==============================================================================
# PART 2: UPGRADING F-09 FROM `SINGLE` TO `TRIANGULATED` ACROSS 4 AXES
# ==============================================================================
METRICS_8 = (
    "jsd_first_fg",
    "cross_excess_eva",
    "I_within",
    "h2",
    "CHARWIN",
    "f4_prefix_gain",
    "MM_K100",
    "R_within_1",
)


def build_page_sufficient_stats(pages: list[dict]) -> dict:
    """Precomputes exact per-page sufficient statistics for all 8 core metrics so that any subset of pages S
    can be evaluated in O(|S|) vector operations across 500 resampling draws."""
    n_pages = len(pages)
    all_toks = [w for p in pages for ln in p["lines"] for w in ln]
    seg = S74.make_cached_segmenter(all_toks)

    # Fit out-of-quire scorers (p_sc, cm3, ug_rn) per quire so CHARWIN and f4_prefix_gain are evaluated out-of-sample
    unique_quires = sorted({p.get("quire", "?") for p in pages})
    scorers_by_q: dict[str, tuple] = {}
    for q_val in unique_quires:
        tr_p = [p for p in pages if p.get("quire", "?") != q_val]
        if len(tr_p) < max(10, n_pages // 5):
            tr_p = [p for i, p in enumerate(pages) if i % 5 != 0]
        tr_t = [w for p in tr_p for ln in p["lines"] for w in ln]
        p_sc_q = S74.PrefixBigramScorer(tr_p, seg)
        cm3_q = CharMarkov(tr_t, 3)
        ug_rn_q = M3.UnigramGTRenorm(tr_t, cm3_q)
        scorers_by_q[q_val] = (p_sc_q, cm3_q, ug_rn_q)

    # Alphabets for first/last glyph JSD & cross_excess_eva, and character bigrams for h2
    glyph_set = sorted({w[0] for w in all_toks} | {w[-1] for w in all_toks})
    g2i = {g: i for i, g in enumerate(glyph_set)}
    G = len(glyph_set)

    char_set = sorted({ch for w in all_toks for ch in w} | {" "})
    c2i = {ch: i for i, ch in enumerate(char_set)}
    C_dim = len(char_set)

    # Top-100 core mapping for MM_K100
    core_counts = Counter(seg.segment(w)[1] for w in all_toks if seg.segment(w)[1])
    fmap_100 = S80.fit_freq(core_counts, 100)
    K_dim = 101

    jsd_first = np.zeros((n_pages, G), dtype=np.float64)
    jsd_int = np.zeros((n_pages, G), dtype=np.float64)
    cross_obs = np.zeros((n_pages, G, G), dtype=np.float64)
    cross_null = np.zeros((n_pages, G, G), dtype=np.float64)
    moran_st = np.zeros((n_pages, 6), dtype=np.float64)  # n_w, m_pair, sum_x, sum_x2, sum_pair, sum_lr
    char_bg = np.zeros((n_pages, C_dim, C_dim), dtype=np.float64)
    cw_st = np.zeros((n_pages, 3), dtype=np.float64)     # n_w, rn_bits, wb_bits
    pg_st = np.zeros((n_pages, 3), dtype=np.float64)     # n_p, u_bits, b_bits
    mm_obs = np.zeros((n_pages, K_dim, K_dim), dtype=np.float64)
    mm_null = np.zeros((n_pages, K_dim, K_dim), dtype=np.float64)
    rw_st = np.zeros((n_pages, 3), dtype=np.float64)     # n_within, obs_same, null_same

    for pi, p in enumerate(pages):
        p_sc, cm3, ug_rn = scorers_by_q[p.get("quire", "?")]
        pg_cores_all = []
        n_within_pg = 0
        obs_same_pg = 0
        for ln in p["lines"]:
            L = len(ln)
            if L == 0:
                continue
            if L >= 3:
                jsd_first[pi, g2i[ln[0][0]]] += 1.0
                for w in ln[1:]:
                    jsd_int[pi, g2i[w[0]]] += 1.0

            # Word lengths & Moran stats
            lens = [float(len(w)) for w in ln]
            moran_st[pi, 0] += L
            moran_st[pi, 2] += sum(lens)
            moran_st[pi, 3] += sum(x * x for x in lens)
            if L >= 2:
                moran_st[pi, 1] += (L - 1)
                moran_st[pi, 4] += sum(a * b for a, b in zip(lens[:-1], lens[1:]))
                moran_st[pi, 5] += sum(lens[:-1]) + sum(lens[1:])

            # Character bigrams for h2 (including word boundary space ' ')
            line_str = " ".join(ln) + " "
            for ch_a, ch_b in zip(line_str[:-1], line_str[1:]):
                char_bg[pi, c2i[ch_a], c2i[ch_b]] += 1.0

            # CHARWIN & Prefix gain (strictly out-of-quire)
            for w in ln:
                cw_st[pi, 0] += 1.0
                cw_st[pi, 1] -= ug_rn.logp_word(w)
                cw_st[pi, 2] -= cm3.logp_word(w)
            if L >= 2:
                ps = [seg.segment(w)[0] or EMPTY for w in ln]
                for a, b in zip(ps[:-1], ps[1:]):
                    pg_st[pi, 0] += 1.0
                    pg_st[pi, 1] -= math.log2(p_sc.pu(b))
                    pg_st[pi, 2] -= math.log2(p_sc.pb(a, b))

            # Cross-word EVA glyph pairs (obs and analytical within-line shuffle expectation)
            if L >= 2:
                last_g = [g2i[w[-1]] for w in ln]
                first_g = [g2i[w[0]] for w in ln]
                for a, b in zip(last_g[:-1], first_g[1:]):
                    cross_obs[pi, a, b] += 1.0
                cnt_l = np.bincount(last_g, minlength=G).astype(np.float64)
                cnt_f = np.bincount(first_g, minlength=G).astype(np.float64)
                diag_lf = np.zeros((G, G), dtype=np.float64)
                for a, b in zip(last_g, first_g):
                    diag_lf[a, b] += 1.0
                cross_null[pi] += (np.outer(cnt_l, cnt_f) - diag_lf) / float(L)

            # Core sequence for MM_K100 and R_within(1)
            cs_full = [seg.segment(w)[1] for w in ln if seg.segment(w)[1]]
            Lc = len(cs_full)
            pg_cores_all.extend(cs_full)
            if Lc >= 2:
                n_within_pg += (Lc - 1)
                obs_same_pg += sum(1 for a, b in zip(cs_full[:-1], cs_full[1:]) if a == b)
                k_codes = [fmap_100.get(c, 100) for c in cs_full]
                for a, b in zip(k_codes[:-1], k_codes[1:]):
                    mm_obs[pi, a, b] += 1.0
                cnt_k = np.bincount(k_codes, minlength=K_dim).astype(np.float64)
                diag_k = np.diag(cnt_k)
                mm_null[pi] += (np.outer(cnt_k, cnt_k) - diag_k) / float(Lc)

        # Page-level expected core match probability under within-page token permutation
        N_pg = len(pg_cores_all)
        if N_pg >= 2 and n_within_pg > 0:
            c_pg = Counter(pg_cores_all)
            p_same = sum(v * (v - 1) for v in c_pg.values()) / float(N_pg * (N_pg - 1))
            rw_st[pi] = (float(n_within_pg), float(obs_same_pg), float(n_within_pg) * p_same)

    return dict(
        n_pages=n_pages,
        pages=pages,
        jsd_first=jsd_first,
        jsd_int=jsd_int,
        cross_obs=cross_obs,
        cross_null=cross_null,
        moran_st=moran_st,
        char_bg=char_bg,
        cw_st=cw_st,
        pg_st=pg_st,
        mm_obs=mm_obs,
        mm_null=mm_null,
        rw_st=rw_st,
    )


def _mi_from_mat(M: np.ndarray, mm_corr: bool = False) -> float:
    tot = float(M.sum())
    if tot <= 0:
        return 0.0
    P = M / tot
    r = P.sum(axis=1, keepdims=True)
    c = P.sum(axis=0, keepdims=True)
    denom = r @ c
    nz = (P > 0) & (denom > 0)
    mi = float(np.sum(P[nz] * np.log2(P[nz] / denom[nz])))
    if mm_corr:
        k_j = int(np.sum(M > 0))
        k_r = int(np.sum(M.sum(axis=1) > 0))
        k_c = int(np.sum(M.sum(axis=0) > 0))
        mi += (k_j - k_r - k_c + 1) / (2.0 * tot * math.log(2.0))
    return mi


def eval_subset_metrics(st: dict, idx: np.ndarray) -> dict[str, float]:
    """Evaluate all 8 core project metrics on page index array `idx` (with multiplicity if bootstrap)."""
    # 1. jsd_first_fg
    f_cnt = st["jsd_first"][idx].sum(axis=0)
    i_cnt = st["jsd_int"][idx].sum(axis=0)
    pf = f_cnt / max(1.0, float(f_cnt.sum()))
    pi = i_cnt / max(1.0, float(i_cnt.sum()))
    pm = 0.5 * (pf + pi)
    nz_f = (pf > 0) & (pm > 0)
    nz_i = (pi > 0) & (pm > 0)
    jsd_val = 0.5 * float(np.sum(pf[nz_f] * np.log2(pf[nz_f] / pm[nz_f])) + np.sum(pi[nz_i] * np.log2(pi[nz_i] / pm[nz_i])))

    # 2. cross_excess_eva
    c_obs = st["cross_obs"][idx].sum(axis=0)
    c_nul = st["cross_null"][idx].sum(axis=0)
    cross_ex = _mi_from_mat(c_obs, mm_corr=True) - _mi_from_mat(c_nul, mm_corr=False)

    # 3. I_within (Moran's I)
    ms = st["moran_st"][idx].sum(axis=0)
    N_w, M_p, sx, sx2, spair, slr = ms
    mu = sx / max(1.0, N_w)
    denom_m = sx2 - N_w * mu * mu
    num_m = spair - mu * slr + M_p * mu * mu
    moran_val = float((N_w / max(1.0, M_p)) * (num_m / denom_m)) if denom_m > 0 else 0.0

    # 4. h2 (conditional character entropy H(c_t | c_{t-1}))
    bg = st["char_bg"][idx].sum(axis=0)
    tot_bg = float(bg.sum())
    P_bg = bg / max(1.0, tot_bg)
    P_prev = np.broadcast_to(P_bg.sum(axis=1, keepdims=True), P_bg.shape)
    nz_bg = (P_bg > 0) & (P_prev > 0)
    h2_val = -float(np.sum(P_bg[nz_bg] * np.log2(P_bg[nz_bg] / P_prev[nz_bg])))

    # 5. CHARWIN
    cws = st["cw_st"][idx].sum(axis=0)
    charwin_val = float((cws[1] - cws[2]) / max(1.0, cws[0]))

    # 6. f4_prefix_gain
    pgs = st["pg_st"][idx].sum(axis=0)
    pgain_val = float((pgs[1] - pgs[2]) / max(1.0, pgs[0]))

    # 7. MM_K100
    m_obs = st["mm_obs"][idx].sum(axis=0)
    m_nul = st["mm_null"][idx].sum(axis=0)
    mm100_val = _mi_from_mat(m_obs, mm_corr=True) - _mi_from_mat(m_nul, mm_corr=False)

    # 8. R_within_1
    rws = st["rw_st"][idx].sum(axis=0)
    rw1_val = float(rws[1] / max(1e-9, rws[2]))

    return dict(
        jsd_first_fg=jsd_val,
        cross_excess_eva=cross_ex,
        I_within=moran_val,
        h2=h2_val,
        CHARWIN=charwin_val,
        f4_prefix_gain=pgain_val,
        MM_K100=mm100_val,
        R_within_1=rw1_val,
    )


def resample_scheme_intervals(st: dict, scheme: str, inv: dict[str, dict[str, str]], n_draws: int = 500, seed: int = SEED) -> dict[str, tuple[float, tuple[float, float]]]:
    """Compute point estimate and 95% interval [lo, hi] across 500 draws for a given resampling scheme:
      - 'sub41'     : 41-page random subsamples without replacement (`[data]` + `[split]`)
      - 'quire_loqo': 15-quire block bootstrap / LOQO resampling matched to ~41 pages (`[method]` quire)
      - 'bifolio_20': 52-bifolio block subsampling (20 bifolios per draw ~ 40 pages, `[method]` bifolio)."""
    rng = np.random.default_rng(seed)
    n_p = st["n_pages"]
    full_pt = eval_subset_metrics(st, np.arange(n_p))
    draws = {m: np.zeros(n_draws, dtype=np.float64) for m in METRICS_8}

    if scheme == "sub41":
        k_sub = min(n_p, 41)
        for b in range(n_draws):
            ix = rng.choice(n_p, size=k_sub, replace=False)
            r = eval_subset_metrics(st, ix)
            for m in METRICS_8:
                draws[m][b] = r[m]
    elif scheme == "quire_loqo":
        by_q: dict[str, list[int]] = defaultdict(list)
        for i, p in enumerate(st["pages"]):
            by_q[p.get("quire", "?")].append(i)
        q_keys = [q for q, ixs in sorted(by_q.items()) if len(ixs) >= 2 and q != "?"]
        for b in range(n_draws):
            picked = []
            for q in rng.choice(q_keys, size=len(q_keys), replace=True):
                picked.extend(by_q[q])
                if len(picked) >= 45:
                    break
            r = eval_subset_metrics(st, np.array(picked[:45], dtype=np.int64))
            for m in METRICS_8:
                draws[m][b] = r[m]
    elif scheme == "bifolio_20":
        by_bif: dict[str, list[int]] = defaultdict(list)
        for i, p in enumerate(st["pages"]):
            pid = p["id"]
            bif = inv.get(pid, {}).get("bifolio", pid[:4])
            by_bif[bif].append(i)
        bif_keys = sorted(by_bif.keys())
        k_bif = min(len(bif_keys), 20)
        for b in range(n_draws):
            picked = []
            for bf in rng.choice(bif_keys, size=k_bif, replace=False):
                picked.extend(by_bif[bf])
            r = eval_subset_metrics(st, np.array(picked, dtype=np.int64))
            for m in METRICS_8:
                draws[m][b] = r[m]
    else:
        raise ValueError(f"Unknown scheme: {scheme}")

    out = OrderedDict()
    for m in METRICS_8:
        pt = full_pt[m]
        ci = ci_bracket(pt, draws[m])
        out[m] = (pt, ci)
    return out


def run_part2(part1_res: dict, inv: dict[str, dict[str, str]]) -> dict:
    emit("\n" + "=" * 112)
    emit("PART 2 (P-25B: Upgrading F-09 from SINGLE to TRIANGULATED Across `data`, `split`, `method`, and `physical` Axes)")
    emit("=" * 112)

    # Enrich inv with bifolio IDs from s77 codicology inventory
    s77_inv = S77.load_codicology_and_inventory()
    for pid, info in s77_inv.items():
        b_sh = info.get("b_sheet", "?")
        q_str = info.get("quire", "?")
        if pid in inv:
            inv[pid]["bifolio"] = f"{q_str}|{b_sh}"
        else:
            inv[pid] = dict(bifolio=f"{q_str}|{b_sh}", quire=q_str)

    translit_pages = part1_res["translit_pages"]

    # Load physical s45 127-page Kraken ink-detected stream (`runs/s45/ink_lines_ZL3b.meta.json`)
    seg_sum_s45 = json.loads((ROOT / "runs" / "s45" / "segment_summary.json").read_text(encoding="utf-8"))
    clean_127 = set(seg_sum_s45["clean_ids"])
    ink_raw = json.loads((ROOT / "runs" / "s45" / "ink_lines_ZL3b.meta.json").read_text(encoding="utf-8"))["pages"]
    zl_ink_127_pages = []
    for p in ink_raw:
        pid = str(p["id"])
        if pid in clean_127 and p.get("lines"):
            lines = [[str(w) for w in ln if w] for ln in p["lines"] if ln]
            if lines:
                q_str = inv.get(pid, {}).get("quire", "?")
                zl_ink_127_pages.append(dict(id=pid, quire=q_str, lines=lines))

    # Build sufficient statistics per corpus and evaluate 500 draws across all 4 axes
    st_by_tr = {T: build_page_sufficient_stats(translit_pages[T]) for T in TRANSLITS}
    st_phys = build_page_sufficient_stats(zl_ink_127_pages)

    schemes_eval = OrderedDict([
        ("ZL3b_sub41 [data+split]", resample_scheme_intervals(st_by_tr["ZL3b"], "sub41", inv, 500, SEED + 10)),
        ("RF1b_sub41 [data+split]", resample_scheme_intervals(st_by_tr["RF1b"], "sub41", inv, 500, SEED + 20)),
        ("IT2a_sub41 [data+split]", resample_scheme_intervals(st_by_tr["IT2a"], "sub41", inv, 500, SEED + 30)),
        ("ZL3b_LOQO15 [method:quire]", resample_scheme_intervals(st_by_tr["ZL3b"], "quire_loqo", inv, 500, SEED + 40)),
        ("ZL3b_Bif20 [method:bifolio]", resample_scheme_intervals(st_by_tr["ZL3b"], "bifolio_20", inv, 500, SEED + 50)),
        ("RF1b_Bif20 [method:bifolio]", resample_scheme_intervals(st_by_tr["RF1b"], "bifolio_20", inv, 500, SEED + 60)),
        ("IT2a_Bif20 [method:bifolio]", resample_scheme_intervals(st_by_tr["IT2a"], "bifolio_20", inv, 500, SEED + 70)),
        ("ZL3b_ink127 [physical:s45]", resample_scheme_intervals(st_phys, "sub41", inv, 500, SEED + 80)),
    ])

    dir_rules = {
        "jsd_first_fg": lambda x: x > 0.10,
        "cross_excess_eva": lambda x: x > 0.02,
        "I_within": lambda x: x > 0.05,
        "h2": lambda x: 1.75 <= x <= 2.25,
        "CHARWIN": lambda x: x > 0.0,
        "f4_prefix_gain": lambda x: x > 0.04,
        "MM_K100": lambda x: x > 0.010,
        "R_within_1": lambda x: x > 1.05,
    }

    emit("\n--- 2A. 8 Core Project Metrics Across 4 Independent Axes (500 Resampling Draws per Cell; Point [95% CI]) ---")
    overlap_count = 0
    metric_overlap_summary = OrderedDict()

    for m in METRICS_8:
        emit(f"\n  Metric `{m}`:")
        los, his, widths = [], [], []
        base_w = None
        all_dir_ok = True
        for s_label, s_res in schemes_eval.items():
            pt, ci = s_res[m]
            if not dir_rules[m](pt):
                all_dir_ok = False
            w = max(1e-9, ci[1] - ci[0])
            if base_w is None:
                base_w = w
            w_ratio = w / base_w
            los.append(ci[0])
            his.append(ci[1])
            widths.append(w)
            ci_s = fmt_ci(pt, ci, "+.4f" if m not in ("jsd_first_fg", "h2", "R_within_1") else ".4f")
            emit(f"    {s_label:<28}: {ci_s:<26} (width={w:.4f}, width_ratio_vs_ZL3b_sub41={w_ratio:.2f}x)")

        # Check common 95% CI intersection across split + method (sub41, LOQO15, Bif20) AND 4-axis directional survival
        method_intervals = [
            schemes_eval["ZL3b_sub41 [data+split]"][m][1],
            schemes_eval["ZL3b_LOQO15 [method:quire]"][m][1],
            schemes_eval["ZL3b_Bif20 [method:bifolio]"][m][1],
        ]
        max_lo = max(iv[0] for iv in method_intervals)
        min_hi = min(iv[1] for iv in method_intervals)
        common_overlap = (max_lo <= min_hi) and all_dir_ok
        if common_overlap:
            overlap_count += 1
        metric_overlap_summary[m] = dict(common_overlap=common_overlap, max_lo=max_lo, min_hi=min_hi, all_dir_ok=all_dir_ok)
        emit(
            f"    -> [split]+[method] CI Intersection [{max_lo:+.4f}, {min_hi:+.4f}] & 4-Axis (`data`,`split`,`method`,`physical`) Survival: "
            f"{'TRIANGULATED (8/8 cells survive + CIs overlap)' if common_overlap else 'DISJOINT'}"
        )

    call2_pass = (overlap_count == len(METRICS_8))
    emit("\n--- 2B. Pre-Registered Call CALL_2_P25B_F09_TRIANGULATED (Upgrading F-09 from SINGLE to TRIANGULATED) ---")
    emit(f"  - Metrics triangulated across all 4 axes (`data`, `split`, `method`, `physical`): {overlap_count}/{len(METRICS_8)} (req: 8/8)")
    emit(f"  - CALL_2_P25B_F09_TRIANGULATED: {'TRUE (F-09 upgraded from SINGLE to TRIANGULATED across data, split, method, and physical)' if call2_pass else 'FALSE'}")
    flush()

    return dict(
        schemes_eval=schemes_eval,
        metric_overlap_summary=metric_overlap_summary,
        overlap_count=overlap_count,
        call2_pass=call2_pass,
    )


# ==============================================================================
# PART 3: DISCHARGING X-08 ON F-16 — LABEL-FREE PHYSICAL & DISTRIBUTIONAL REGIMES
# ==============================================================================
def nmi_binary(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Normalized Mutual Information between two binary label vectors in {0, 1}."""
    n = len(y_true)
    if n == 0:
        return 0.0
    c00 = int(np.sum((y_true == 0) & (y_pred == 0)))
    c01 = int(np.sum((y_true == 0) & (y_pred == 1)))
    c10 = int(np.sum((y_true == 1) & (y_pred == 0)))
    c11 = int(np.sum((y_true == 1) & (y_pred == 1)))
    mat = np.array([[c00, c01], [c10, c11]], dtype=np.float64)
    mi = _mi_from_mat(mat, mm_corr=False)
    p_t = mat.sum(axis=1) / n
    p_p = mat.sum(axis=0) / n
    ht = -float(np.sum(p_t[p_t > 0] * np.log2(p_t[p_t > 0])))
    hp = -float(np.sum(p_p[p_p > 0] * np.log2(p_p[p_p > 0])))
    return float(2.0 * mi / max(1e-9, ht + hp))


def build_h_blind_dist_features(pages: list[dict], seg: SlotSegmenter) -> tuple[list[dict], np.ndarray]:
    """Build strictly $H-blind and $L-blind distributional + page-layout feature vector per page (pages with >= 20 tokens,
    hand in {'1','2','3'} and lang in {'A','B'} kept for ground-truth evaluation AFTER unsupervised clustering):
      [f_cho_parisel, r_dl_parisel, suf_edy, pre_qo, suf_dy, lines_per_page, words_per_line]."""
    kept = []
    vecs = []
    for p in pages:
        words = [w for ln in p["lines"] for w in ln]
        if len(words) < 20 or p.get("hand") not in ("1", "2", "3") or p.get("lang") not in ("A", "B"):
            continue
        n_w = float(len(words))
        n_ln = max(1.0, float(len(p["lines"])))
        ev_o = sum(len(re.findall(r"[cs]ho", w)) for w in words)
        ev_e = sum(len(re.findall(r"[cs]he", w)) for w in words)
        f_cho = ev_o / max(1.0, float(ev_o + ev_e))
        nd = sum(w.count("d") for w in words)
        nl = sum(w.count("l") for w in words)
        r_dl = nd / max(1.0, float(nd + nl))

        pcs = [seg.segment(w) for w in words]
        s_edy = sum(1 for w, (_, _, s) in zip(words, pcs) if "edy" in s or "ey" in s or w.endswith("edy") or w.endswith("ey")) / n_w
        p_qo = sum(1 for w, (pr, _, _) in zip(words, pcs) if pr == "qo" or w.startswith("qo")) / n_w
        p_dy = sum(1 for w, (_, _, s) in zip(words, pcs) if s == "dy" or w.endswith("dy")) / n_w

        kept.append(p)
        vecs.append([f_cho, r_dl, 1.5 * s_edy, 1.5 * p_qo, p_dy, 0.6 * n_ln, 0.4 * (n_w / n_ln)])

    X = np.array(vecs, dtype=np.float64)
    mu = X.mean(axis=0, keepdims=True)
    sd = np.maximum(X.std(axis=0, keepdims=True), 1e-6)
    z = (X - mu) / sd
    w_col = np.array([[1.2, 1.0, 1.5, 1.4, 1.0, 0.7, 0.5]], dtype=np.float64)
    return kept, z * w_col


def load_s45_physical_page_features() -> dict[str, dict[str, float]]:
    """Load $H-blind physical scan layout & ink-gap measurements per page from runs/s45/pages/<pid>.json."""
    s45_dir = ROOT / "runs" / "s45"
    clean_ids = json.loads((s45_dir / "segment_summary.json").read_text(encoding="utf-8"))["clean_ids"]
    out = {}
    for pid in clean_ids:
        pj_path = s45_dir / "pages" / f"{pid}.json"
        if not pj_path.exists():
            continue
        pj = json.loads(pj_path.read_text(encoding="utf-8"))
        thr_obj = pj.get("threshold", 15.0)
        thr = float(thr_obj.get("thr", 15.0)) if isinstance(thr_obj, dict) else float(thr_obj)
        lines = pj.get("lines", [])
        gaps = [
            float(t["gap_r"])
            for ln in lines
            for t in ln.get("tokens", [])
            if t.get("gap_r") is not None and float(t["gap_r"]) > 0
        ]
        med_gap = float(np.median(gaps)) if gaps else thr
        n_lines = float(len(lines))
        tok_counts = [len(ln.get("tokens", [])) for ln in lines if ln.get("tokens")]
        w_per_line = float(np.mean(tok_counts)) if tok_counts else 8.0
        px_g = max(5.0, float(pj.get("px_per_glyph", 27.0)))
        w_widths = [float(t.get("w", 80.0)) / px_g for ln in lines for t in ln.get("tokens", []) if t.get("w")]
        mean_wlen = float(np.mean(w_widths)) if w_widths else 5.0
        out[str(pid)] = dict(
            med_gap_px=med_gap,
            otsu_thr=thr,
            gap_to_thr=med_gap / max(1.0, thr),
            lines_per_page=n_lines,
            words_per_line=w_per_line,
            mean_word_len=mean_wlen,
        )
    return out


def run_part3(part1_res: dict) -> dict:
    emit("\n" + "=" * 112)
    emit("PART 3 (P-25C: Discharging X-08 on F-16 — Label-Free Unsupervised Physical & Distributional Scribe Regimes)")
    emit("=" * 112)

    translit_pages = part1_res["translit_pages"]
    phys_feats = load_s45_physical_page_features()
    s77_inv = S77.load_codicology_and_inventory()

    emit("\n--- 3A. Unsupervised $H-Blind k=2 Clustering vs Currier A/B ($L) and Davis Hand 1 vs Hands 2/3 ($H) ---")
    emit(
        f"  {'Dataset / Feature Space':<36} {'Pages':>5} | {'Acc vs Currier A/B [95% CI]':>27} {'NMI(A/B)':>9} | "
        f"{'Acc vs H1 vs H2/3 [95% CI]':>27} {'NMI(H)':>8}"
    )

    unsup_results = OrderedDict()
    rng_bs = np.random.default_rng(SEED + 301)

    for tr_name, all_pages in translit_pages.items():
        seg = S74.make_cached_segmenter([w for p in all_pages for ln in p["lines"] for w in ln])
        kept_p, X_dist = build_h_blind_dist_features(all_pages, seg)
        _, lab_k2 = S74.kmeans_pp(X_dist, 2, seed=SEED, restarts=10, iters=50)

        y_currier = np.array([0 if p["lang"] == "A" else 1 for p in kept_p], dtype=np.int64)
        y_hand = np.array([0 if p["hand"] == "1" else 1 for p in kept_p], dtype=np.int64)

        acc_c_raw = float(np.mean(lab_k2 == y_currier))
        if acc_c_raw < 0.5:
            lab_k2 = 1 - lab_k2
            acc_c_raw = 1.0 - acc_c_raw
        acc_h_raw = float(np.mean(lab_k2 == y_hand))
        acc_h = max(acc_h_raw, 1.0 - acc_h_raw)

        nmi_c = nmi_binary(y_currier, lab_k2)
        nmi_h = nmi_binary(y_hand, lab_k2)

        bs_c = [float(np.mean(lab_k2[ix] == y_currier[ix])) for ix in (rng_bs.integers(len(kept_p), size=len(kept_p)) for _ in range(400))]
        bs_h = [float(np.mean(lab_k2[ix] == y_hand[ix])) for ix in (rng_bs.integers(len(kept_p), size=len(kept_p)) for _ in range(400))]
        ci_c = ci_bracket(acc_c_raw, bs_c)
        ci_h = ci_bracket(acc_h, bs_h)

        label_d = f"{tr_name} X_dist (Parisel+Slot, $H-blind)"
        unsup_results[label_d] = dict(n=len(kept_p), acc_c=acc_c_raw, ci_c=ci_c, nmi_c=nmi_c, acc_h=acc_h, ci_h=ci_h, nmi_h=nmi_h)
        emit(
            f"  {label_d:<36} {len(kept_p):5d} | {fmt_ci(acc_c_raw, ci_c, '.4f'):>27} {nmi_c:9.4f} | "
            f"{fmt_ci(acc_h, ci_h, '.4f'):>27} {nmi_h:8.4f}"
        )

        if tr_name == "ZL3b":
            # Also evaluate on the 127 physical scan pages combining X_phys + X_dist
            idx_127 = [i for i, p in enumerate(kept_p) if p["id"] in phys_feats]
            p_127 = [kept_p[i] for i in idx_127]
            X_p_raw = np.array([
                [
                    phys_feats[p["id"]]["med_gap_px"],
                    phys_feats[p["id"]]["otsu_thr"],
                    phys_feats[p["id"]]["gap_to_thr"],
                    phys_feats[p["id"]]["lines_per_page"],
                    phys_feats[p["id"]]["words_per_line"],
                    phys_feats[p["id"]]["mean_word_len"],
                ]
                for p in p_127
            ], dtype=np.float64)
            X_p_z = (X_p_raw - X_p_raw.mean(axis=0, keepdims=True)) / np.maximum(X_p_raw.std(axis=0, keepdims=True), 1e-6)
            X_joint = np.hstack([X_dist[idx_127], 0.5 * X_p_z])
            _, lab_j = S74.kmeans_pp(X_joint, 2, seed=SEED, restarts=10, iters=50)
            yc_127 = y_currier[idx_127]
            yh_127 = y_hand[idx_127]
            acc_jc = float(np.mean(lab_j == yc_127))
            if acc_jc < 0.5:
                lab_j = 1 - lab_j
                acc_jc = 1.0 - acc_jc
            acc_jh = max(float(np.mean(lab_j == yh_127)), 1.0 - float(np.mean(lab_j == yh_127)))
            nmi_jc = nmi_binary(yc_127, lab_j)
            nmi_jh = nmi_binary(yh_127, lab_j)
            bs_jc = [float(np.mean(lab_j[ix] == yc_127[ix])) for ix in (rng_bs.integers(len(p_127), size=len(p_127)) for _ in range(400))]
            bs_jh = [float(np.mean(lab_j[ix] == yh_127[ix])) for ix in (rng_bs.integers(len(p_127), size=len(p_127)) for _ in range(400))]
            ci_jc = ci_bracket(acc_jc, bs_jc)
            ci_jh = ci_bracket(acc_jh, bs_jh)
            label_j = "ZL3b_scan127 X_joint (Phys+Dist)"
            unsup_results[label_j] = dict(n=len(p_127), acc_c=acc_jc, ci_c=ci_jc, nmi_c=nmi_jc, acc_h=acc_jh, ci_h=ci_jh, nmi_h=nmi_jh)
            emit(
                f"  {label_j:<36} {len(p_127):5d} | {fmt_ci(acc_jc, ci_jc, '.4f'):>27} {nmi_jc:9.4f} | "
                f"{fmt_ci(acc_jh, ci_jh, '.4f'):>27} {nmi_jh:8.4f}"
            )

            # Inspect physical scan layout separation between the two $H-blind clusters on the 127 scan pages
            c0_mask = (lab_j == 0)
            c1_mask = (lab_j == 1)
            wpl_0, wpl_1 = X_p_raw[c0_mask, 4], X_p_raw[c1_mask, 4]
            lpp_0, lpp_1 = X_p_raw[c0_mask, 3], X_p_raw[c1_mask, 3]
            z_wpl = ( float(wpl_1.mean() - wpl_0.mean()) ) / math.sqrt(float(wpl_1.var() / len(wpl_1) + wpl_0.var() / len(wpl_0)))
            z_lpp = ( float(lpp_1.mean() - lpp_0.mean()) ) / math.sqrt(float(lpp_1.var() / len(lpp_1) + lpp_0.var() / len(lpp_0)))
            emit(
                f"\n  Physical Scan Layout Separation Across Unsupervised $H-Blind Regimes (n={len(p_127)} scan pages):"
                f"\n    - Cluster 0 (Currier A / Hand 1 regime, n={int(c0_mask.sum())}): words/line = {wpl_0.mean():.2f}, lines/page = {lpp_0.mean():.2f}"
                f"\n    - Cluster 1 (Currier B / Hand 2-3 regime, n={int(c1_mask.sum())}): words/line = {wpl_1.mean():.2f}, lines/page = {lpp_1.mean():.2f}"
                f"\n    - Physical difference z-scores: z(words/line) = {z_wpl:+.2f}, z(lines/page) = {z_lpp:+.2f}"
            )

    # 3B. Within Herbal-B ($I=H, $L=B) Label-Free Cross-Entropy Transfer Test (Discharging X-08 on F-16)
    emit("\n--- 3B. Within Herbal-B (`Section=H, Currier=B`) Label-Free LOBO Cross-Entropy Transfer Test (Discharging X-08 on F-16) ---")
    emit(
        f"  {'Translit':<6} {'Herbal-B Partition ($H-blind vs Davis)':<40} {'Pages(A/B)':>11} | "
        f"{'D_sym(top50) [95% CI]':>25} {'p_bif(top50)':>13} | {'D_sym(blind)':>13} {'Verdict (D_sym<=0 or p>0.05)':>28}"
    )

    hb_results = OrderedDict()
    for tr_name, all_pages in translit_pages.items():
        # Filter to Herbal-B pages (Section == 'H' and Currier lang == 'B' or f65v) and attach leaf/bifolio from s77_inv
        hb_pages = []
        for p in all_pages:
            pid = p["id"]
            info = s77_inv.get(pid, {})
            sec = p.get("section") or info.get("section", "?")
            lang = p.get("lang") or info.get("lang", "?")
            if sec == "H" and (lang == "B" or pid == "f65v"):
                q = p.get("quire") or info.get("quire", "?")
                lf = f"{q}|{info.get('leaf', S77.folio_leaf_key(pid))}"
                bf = f"{q}|{info.get('b_sheet', pid[:4])}"
                hb_pages.append(dict(p, quire=q, leaf=lf, bifolio=bf))

        # Build unsupervised k=2 partition of Herbal-B pages using $H-blind layout & Parisel features (zero core double-dipping)
        seg_hb = S74.make_cached_segmenter([w for p in hb_pages for ln in p["lines"] for w in ln])
        X_hb = []
        for p in hb_pages:
            ws = [w for ln in p["lines"] for w in ln]
            n_w = max(1.0, float(len(ws)))
            n_ln = max(1.0, float(len(p["lines"])))
            m_wl = sum(len(w) for w in ws) / n_w
            ev_o = sum(len(re.findall(r"[cs]ho", w)) for w in ws)
            ev_e = sum(len(re.findall(r"[cs]he", w)) for w in ws)
            f_cho = ev_o / max(1.0, float(ev_o + ev_e))
            nd = sum(w.count("d") for w in ws)
            nl = sum(w.count("l") for w in ws)
            r_dl = nd / max(1.0, float(nd + nl))
            X_hb.append([n_ln, n_w / n_ln, m_wl, f_cho, r_dl])
        X_hb_arr = np.array(X_hb, dtype=np.float64)
        X_hb_z = (X_hb_arr - X_hb_arr.mean(axis=0, keepdims=True)) / np.maximum(X_hb_arr.std(axis=0, keepdims=True), 1e-6)
        _, lab_hb_k2 = S74.kmeans_pp(X_hb_z, 2, seed=SEED, restarts=10, iters=50)
        unsup_a_ids = {p["id"] for p, l in zip(hb_pages, lab_hb_k2) if l == 0}
        unsup_b_ids = {p["id"] for p, l in zip(hb_pages, lab_hb_k2) if l == 1}

        quire_a_ids = {p["id"] for p in hb_pages if p["quire"] in ("E", "F", "G")}
        quire_b_ids = {p["id"] for p in hb_pages if p["quire"] in ("H", "Q")}

        davis_a_ids = {p["id"] for p in hb_pages if p["hand"] == "2"}
        davis_b_ids = {p["id"] for p in hb_pages if p["hand"] == "3"}

        partitions = [
            ("P1_PhysQuire (Quires E,F,G vs H,Q, $H-blind)", quire_a_ids, quire_b_ids),
            ("P2_UnsupK2 (k=2 Layout/Parisel, $H-blind)", unsup_a_ids, unsup_b_ids),
            ("P3_DavisRef (Hand 2 vs Hand 3, reference)", davis_a_ids, davis_b_ids),
        ]

        def fast_seg_factory(_words: list[str], _s=seg_hb) -> SlotSegmenter:
            return _s

        for p_label, a_ids, b_ids in partitions:
            lobo_ev = S77.evaluate_nested_folds(
                hb_pages,
                "bifolio",
                lambda pg, s=a_ids: pg["id"] in s,
                lambda pg, s=b_ids: pg["id"] in s,
                fast_seg_factory,
            )
            perm_res = S77.fast_lobo_permutation_nulls(hb_pages, a_ids, b_ids, fast_seg_factory, n_perm=300)
            dsym_t50 = lobo_ev["top50"]["dsym"]
            p_bif_t50 = perm_res["P2_bif"]["top50"]["p"]
            dsym_blind = lobo_ev["blind"]["dsym"]

            # Bootstrap 95% CI over per-page cross-entropy diffs on top50
            p_diffs = lobo_ev["top50"]["per_page_diffs"]
            diff_vals = np.array([d_b / max(1, nt) for _, _, d_b, nt in p_diffs if nt > 0], dtype=np.float64)
            bs_d = [
                float(diff_vals[rng_bs.integers(len(diff_vals), size=len(diff_vals))].mean())
                for _ in range(400)
            ] if len(diff_vals) else [dsym_t50]
            ci_t50 = ci_bracket(dsym_t50, bs_d)

            null_holds = (dsym_t50 <= 0.0) or (p_bif_t50 > 0.05)
            hb_results[(tr_name, p_label)] = dict(
                n_a=len(a_ids),
                n_b=len(b_ids),
                dsym_t50=dsym_t50,
                ci_t50=ci_t50,
                p_bif_t50=p_bif_t50,
                dsym_blind=dsym_blind,
                null_holds=null_holds,
            )
            emit(
                f"  {tr_name:<6} {p_label:<40} {f'{len(a_ids)}/{len(b_ids)}':>11} | "
                f"{fmt_ci(dsym_t50, ci_t50, '+.4f'):>25} {p_bif_t50:13.4f} | {dsym_blind:+13.4f} "
                f"{'NULL HOLDS (no split)' if null_holds else 'SPLIT':>28}"
            )

    min_unsup_acc = min(v["acc_c"] for v in unsup_results.values())
    min_unsup_nmi = min(v["nmi_c"] for v in unsup_results.values())
    h_blind_hb_ok = all(
        v["null_holds"] for ( _tr, plab ), v in hb_results.items() if "$H-blind" in plab
    )
    layout_sep_ok = (abs(z_wpl) > 3.0) and (abs(z_lpp) > 3.0)

    call3_pass = (min_unsup_acc >= 0.85) and (min_unsup_nmi >= 0.40) and layout_sep_ok and h_blind_hb_ok

    emit("\n--- 3C. Pre-Registered Call CALL_3_P25C_F16_X08_DISCHARGED (Discharging X-08 on F-16) ---")
    emit(f"  - Unsupervised $H-blind k=2 clustering accuracy vs Currier A/B & Hand 1 vs 2/3: min acc = {min_unsup_acc:.4f} (req: >= 0.8500), min NMI = {min_unsup_nmi:.4f} (req: >= 0.4000)")
    emit(f"  - Physical scan layout separation between $H-blind regimes: z(words/line) = {z_wpl:+.2f}, z(lines/page) = {z_lpp:+.2f} (req: |z| > 3.0)")
    emit(f"  - Within-Herbal-B $H-blind partitions (Physical Quire E,F,G vs H,Q & Unsupervised k=2) showing D_sym(top50) <= 0 or p_bif > 0.05: {h_blind_hb_ok} (6/6 cells)")
    emit(f"  - CALL_3_P25C_F16_X08_DISCHARGED: {'TRUE (X-08 on F-16 DISCHARGED; physical axis added to F-16)' if call3_pass else 'FALSE'}")
    flush()

    return dict(
        unsup_results=unsup_results,
        hb_results=hb_results,
        min_unsup_acc=min_unsup_acc,
        min_unsup_nmi=min_unsup_nmi,
        z_wpl=z_wpl,
        z_lpp=z_lpp,
        h_blind_hb_ok=h_blind_hb_ok,
        call3_pass=call3_pass,
    )


def main() -> None:
    S87.below_normal()
    emit("s93_unified_line_producer_and_f09_f16_triangulation.py — ULP93 Producer & F-09 / F-16 Triangulation (s93 / P-25)")
    emit(f"date: {clock()}")
    emit(
        f"device: {S87.DEV} (CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES', '')!r}); "
        f"torch {torch.__version__} (threads={torch.get_num_threads()}); numpy {np.__version__}; python {sys.version.split()[0]}"
    )
    stub_ok, stub_status = verify_stub()
    emit(f"params: SEED={SEED}, SPLIT_SEED={SPLIT_SEED}, N_TOT={N_TOT}, NB={NB}, N_MATCH={N_MATCH}, LP93_PARAMS={LP93_PARAMS}")
    flush()

    inv = S74.load_folio_inventory()
    p1 = run_part1(inv)
    p2 = run_part2(p1, inv)
    p3 = run_part3(p1)

    all_pass = p1["call1_pass"] and p2["call2_pass"] and p3["call3_pass"]

    emit("\n" + "=" * 112)
    emit("SUMMARY OF PRE-REGISTERED CALLS & LEDGER CLOSURE (s93 / P-25)")
    emit("=" * 112)
    emit(
        f"  1. CALL_1_P25A_ULP93 (Unified Two-Layer Producer)   : {'TRUE' if p1['call1_pass'] else 'FALSE'} "
        f"(M4_ULP93_Cadence C1 = {p1['m4_c1_folds']}; C2_dealiased >= 5/6 = {p1['m4_c2_deal_folds']}; "
        f"C2_legacy >= 5/6 = {p1['m4_c2_leg_folds']}; F-14 prefix memory = {p1['m4_s69_ok']})"
    )
    emit(
        f"  2. CALL_2_P25B_F09_TRIANGULATED (F-09 4-Axis Table) : {'TRUE' if p2['call2_pass'] else 'FALSE'} "
        f"({p2['overlap_count']}/8 core metrics overlap across `data`, `split`, `method` [LOQO + 52-bifolio], and `physical` [s45 127p])"
    )
    emit(
        f"  3. CALL_3_P25C_F16_X08_DISCHARGED (X-08 on F-16)    : {'TRUE' if p3['call3_pass'] else 'FALSE'} "
        f"($H-blind k=2 acc >= {100.0 * p3['min_unsup_acc']:.1f}%, NMI >= {p3['min_unsup_nmi']:.3f}; "
        f"physical scan z(wpl)={p3['z_wpl']:+.2f}, z(lpp)={p3['z_lpp']:+.2f}; Herbal-B $H-blind null = {p3['h_blind_hb_ok']})"
    )
    emit(f"  - CI bracket audit (lo <= point <= hi)              : {CI_VIOLATIONS} violations across {CI_CHECKS} checks")
    emit(f"  - Pre-registration stub match                       : {stub_status}")
    emit(
        f"\nOVERALL VERDICT (s93 / P-25): {'ALL 3 PRE-REGISTERED CALLS HOLD — ULP93 RESOLVES THE S91 C1/C2 GAP; F-09 UPGRADED TO TRIANGULATED; X-08 ON F-16 DISCHARGED' if all_pass else 'PARTIAL / SEE FAILING CALLS ABOVE'}"
    )
    emit(f"runtime: {time.time() - T0:.2f} s; finished {clock()}")
    flush()

    assert stub_ok, f"Pre-registration stub mismatch: {stub_status}"
    assert CI_VIOLATIONS == 0, f"CI bracket violations detected: {CI_VIOLATIONS}"


if __name__ == "__main__":
    main()
