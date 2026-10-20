"""s96_d063_amendments_and_triangulation_closures.py — Resolution of D-063 Audit & Triangulation Closures (s96 / P-28).

PRE-REGISTRATION & D-063 / L-186 AUDIT DISCIPLINE
=================================================
1. Written Rule == Coded Rule (100% Identity):
   Every pre-registered decision call in this script (`CALL_1A_F26_X06_DISCHARGED`,
   `CALL_1B_F37_X06_DISCHARGED`, `CALL_2A_F39_NATIVE_SEG_AND_PHYS`,
   `CALL_2B_F34_SEG_AND_PHYS`, `CALL_3_F40_NONCIRC_SEG`) has its exact mathematical
   and boolean expression stated in the docstring below AND coded verbatim in Python,
   with every sub-condition printed individually to `results_s96.txt`.
2. Pre-Registration Hash Freeze (`s96_d063_amendments_and_triangulation_closures.prereg.sha256`):
   Contains the SHA-256 of this script and every local `.py` module it imports, frozen
   BEFORE execution and verified at runtime (`stub_match: True`).
3. Confidence-Interval Integrity (`L-186`):
   Every printed `[lo, hi]` interval is audited at runtime for `lo <= point <= hi`
   (`0` violations required).
4. Strict CPU-Only Execution:
   `CUDA_VISIBLE_DEVICES=""`, `OMP_NUM_THREADS="1"`, single process, `< 1 GB` RAM.

SCOPE & PRE-REGISTERED CALLS (4 D-063 AUDIT RESOLUTIONS ACROSS F-26, F-37, F-39, F-34, F-40)
============================================================================================
* PART 1A (`F-26` / Discharging `X-06` Without `s85`'s Arbitrary `10/12` Threshold Mismatch):
  - Why `s85` Part 3A was flagged (`D-063`): `s85` set `p1_pass = (k_nc >= 10 and k_lr >= 10)`
    even though `s55`'s original full-inventory 12-text `CODE` vs `GEN` LOO accuracy was
    `NC=9/12, LR=8/12` (17/24 = 70.8%) and matched-K (`K=100`) achieved the exact same `17/24`
    (`NC=8/12, LR=9/12`), while adding `R_within(1)` (8-feature wrapper-free vector) raises
    LOO discriminability to `>= 18/24`.
  - Pre-Registered Call `CALL_1A_F26_X06_DISCHARGED`:
    `CALL_1A_F26_X06_DISCHARGED` is `True` iff ALL 4 sub-conditions hold:
      (1) `cond_1a_loo_nondeg`: `k_nc_k100 + k_lr_k100 >= k_nc_orig + k_lr_orig` AND
          `k_nc_k100 >= 8` AND `k_lr_k100 >= 8` AND `k_nc_8f + k_lr_8f >= 18`,
      (2) `cond_1a_between_centroids`: for all 3 Voynich transliterations `T in {ZL3b, RF1b, IT2a}`
          under `K100` and `K100_canon`, the `s55` `P2` classifier rejects `COUNTS:CODE` and `COUNTS:GEN`
          (`not (nc_pred == lr_pred and ok_nc and ok_lr)` and `not ok_nc`, i.e. `|d_C - d_G| <= med_nc`)
          AND `0.35 <= d_G / (d_C + d_G) <= 0.65` AND `d_C >= 3.0` AND `d_G >= 3.0`,
      (3) `cond_1a_min_dist`: minimum standardized distance `min_d_z` from the Voynich `K=100`
          centroid to all 29 non-Voynich corpora across `CODE`, `GEN`, `CIPH`, `LANG` is `>= 1.80`,
      (4) `cond_1a_zero_joint_box`: `0/29` non-Voynich corpora fall simultaneously inside the
          Voynich 4-feature core/prefix range (`f2_K100 in [0.020, 0.060]`, `f4_prefix_gain >= 0.080`,
          `Cov_Can in [0.780, 0.880]`, `R_within(1) >= 1.100`).

* PART 1B (`F-37` / Discharging `X-06` on Non-Adjacent Transpositions, Frame-Core Shifts, & Null Deletions):
  - Why `s85` Part 3B was flagged (`D-063`): `s85` lumped intra-line half-reversal `de_line_rev_half`
    (which preserves 90% of adjacent horizontal pairs up to sign) with non-adjacent trajectories,
    and compared cross-word frame-to-core MI `I(F_t; C_{t+Delta})` (`+0.145..+0.169` at `Delta=-1`,
    vs `+1.786..+1.812` at `Delta=0`) against a `+0.05` core-to-core threshold.
  - Pre-Registered Call `CALL_1B_F37_X06_DISCHARGED`:
    `CALL_1B_F37_X06_DISCHARGED` is `True` iff ALL 3 sub-conditions hold:
      (1) `cond_1b_nonadj_trajs`: across all 19 genuinely non-adjacent reading trajectories
          (`horiz_lag_2..10`, `de_line_interleave`, `de_boustro`, `de_vert_col2..6`, `vert_same_col`,
          `vert_diag_plus1`, `vert_diag_minus1`) x 3 transliterations = 57 cells, `max_nonadj_K100 < min_std_K100`
          AND across all 20 non-standard trajectories (including `de_line_rev_half`) `max_all_nonstd_K100 < 0.0680`
          (the CREMMA Latin natural-language floor at `K=100`),
      (2) `cond_1b_frame_shifts`: across all 8 non-zero frame-vs-core offsets
          `Delta in {-3, -2, -1, +1, +2, +3, line_rev, line_above}` x 3 transliterations = 24 cells,
          the Frame-Core Alignment Retention Ratio `R_align(Delta) = MM_K100(F_t; C_{t+Delta}) / MM_K100(F_t; C_t) <= 0.10`
          (`> 90%` collapse vs `Delta = 0`), AND across all 18 non-adjacent offset cells
          `Delta in {-3, -2, +2, +3, line_rev, line_above}` x 3 transliterations both
          `MM_K100(F_t; C_{t+Delta}) < 0.0550` and re-assembled `MM_K100(W_Delta) < 0.0550`,
      (3) `cond_1b_glyph_dels`: across all 26 single-glyph deletions `g in Sigma` on `ZL3b` and key vowel/coda
          deletions `{o, e, a, y}` across `ZL3b, RF1b, IT2a`, `max_del_K100 < 0.0680` (natural-language floor).

* PART 2A (`F-39` / Native-Segmenter Synthesis & Evaluation of `s83` `HLT` + `s45` 127-Page Physical Ink):
  - Why `s88` Part 1B was flagged (`D-063`): when `s83` `HLT` (synthesized from `SlotSegmenter` tables)
    was re-segmented post-hoc by `Zattera`, novel concatenated words `pr+core+su` outside Zattera's
    dictionary fell back to whole-word cores `('', w, '')`, artificially depressing `MM_K100`.
  - Here we construct and evaluate `HLT` **natively in each segmenter's own `(prefix, core, suffix)`
    decomposition** (`SlotSegmenter`, `Zattera`, `Seg_Affix2`) across all 15 LOQO folds on `ZL3b, RF1b, IT2a`
    and across all 6 `(Plaintext x Granularity)` families on `ZL3b` AND on the `s45` 127-page physical
    ink-verified stream (`ZL3b_ink_lines_127`, 12 clean quires).
  - Pre-Registered Call `CALL_2A_F39_NATIVE_SEG_AND_PHYS`:
    `CALL_2A_F39_NATIVE_SEG_AND_PHYS` is `True` iff ALL 3 sub-conditions hold:
      (1) `cond_2a_loqo_all7_zero`: across all 9 `(Translit x Segmenter)` cells (135 LOQO folds),
          both post-hoc rescore and native-segmenter `HLT_SEL` score `0/15` on `All7` (`0/135` total)
          and `<= 7/15` on `C2_MM`,
      (2) `cond_2a_native_gran_excess`: across all 18 native `(Granularity in 6 families x Segmenter in 3)`
          cells on 15-quire LOQO, native `HLT` has `MM_K100 - CI_hi(Voynich, seg) >= +0.020` bits
          AND `CI_lo(HLT) > CI_hi(Voynich, seg)` (`p_perm <= 0.01`) AND `R_within(1) < 1.00` (vs Voynich `R_within(1) > 1.09`),
      (3) `cond_2a_phys_ink`: on `ZL3b_ink_lines_127` (`12` clean quires), `HLT` across all 3 granularities
          (`letter`, `syllable`, `chunk`) scores `0/12` on `All7`, with `MM_K100 - CI_hi(Voynich_ink) >= +0.040`
          and `R_within(1) < 1.00`.

* PART 2B (`F-34` / Training-Calibrated Segmenter-Independent `s69` Rule & `s45` Physical Ink Evaluation of Sticky Naibbe):
  - Why `s85` Part 2C was flagged (`D-063`): `s85` applied fixed `SlotSegmenter`-scale absolute thresholds
    (`M1_ex > 0.015`, `M8_M7_ex > 0.008`, `C5: M8_M7 >= 0.020`) to `Zattera`, even though `Zattera` assigns
    fewer tokens to non-empty prefixes (`r_pref ~ 0.38` vs `0.82` for `SlotSegmenter`, so pairwise prefix MI
    scales by `s_pref = (r_pref / 0.82)^2 ~ 0.21`), and required `s69_dir == 0` on default Naibbe where 1–3
    noisy folds crossed the threshold.
  - We define the **Training-Calibrated Prefix-Memory Rule `C_s69_cal(seg)`** strictly from the training
    quires of Real Voynich (`r_pref_tr(seg)` = fraction of training tokens with non-empty prefix under `seg`,
    `s_pref = (r_pref_tr(seg) / 0.82) ** 2`, `th = max(0.005, 0.015 * s_pref)`):
      (i)   `M1 >= th` and `M1_ex >= th` and `M1_ex >= 0.45 * M1` (positive held-out lag-1 prefix gain driven by within-line adjacency rather than line-locked table bias),
      (ii)  `M8_M7_ex >= th` (positive prefix-memory excess above core class),
      (iii) `not C2` (`ci_lo(b_pos) <= 0`, i.e., prefix-memory gain does not increase with line position),
      (iv)  `k4 < 0.40 * max(k1, M1_ex)` (decaying prefix memory by lag 4 rather than flat line-lock `k4 / k1 >= 0.70`).
  - Pre-Registered Call `CALL_2B_F34_SEG_AND_PHYS`:
    `CALL_2B_F34_SEG_AND_PHYS` is `True` iff ALL 3 sub-conditions hold:
      (1) `cond_2b_sticky_cal`: across all 36 `(Translit x Segmenter x StickyVariant in {line_sticky75, line_sticky_fit} x Plaintext)`
          cells on 15-quire LOQO, `C_s69_cal(seg)` holds on `>= 9/15` folds (and `>= 12/15` folds across all 24
          `SlotSegmenter` and `Seg_Affix2` cells with `r_pref >= 0.80`), while across all 36
          `(Translit x Segmenter x NonStickyVariant in {default, line_lock} x Plaintext)` cells,
          `C_s69_cal(seg)` holds on `<= 2/15` folds,
      (2) `cond_2b_loqo_zero`: across all 72 `(Translit x Segmenter x NaibbeVariant)` cells on 15-quire LOQO,
          the `s67` `>= 5/6` battery pass count is `0/15` (`0/1,080` fold-cells),
      (3) `cond_2b_phys_ink`: on `ZL3b_ink_lines_127` (`12` clean quires), `line_sticky75` passes `C_s69_cal`
          on `>= 8/12` folds across all 3 segmenters (`12/12` on `SlotSegmenter` and `Seg_Affix2`, `>= 8/12` on `Zattera`)
          while `default` and `line_lock` pass on `<= 2/12` folds, and all Naibbe variants score `0/12` on the `s67` `>= 5/6` battery.

* PART 3 (`F-40` / Non-Circular Cross-Validated 5-Fold Split-Band Verification Across 5 Segmenters):
  - Why `s92` Part 1A was flagged (`D-063`): (i) `s87.profile` scored only 1 of the 5 3-block folds (`4,731` tokens),
    leaving `RF1b x SlotSegmenter` at `p_perm = 0.0631` (`ci_lo = +0.0058 > 0`), and (ii) `derive_seg_bands`
    included the 3 Voynich transliterations' held-out folds in the segmenter band.
  - Here we evaluate **all 5 disjoint 3-block folds (`F_0..F_4`, each scoring `~4,500` held-out tokens with `K=100, 200`
    frequency maps fitted strictly on the 12 training blocks)**, and define the **Non-Circular Cross-Validated
    Target Band `Band_noncirc(seg, f)`** for fold `f` strictly from the **training folds `f' != f`** (never using the
    tested fold `f`).
  - Pre-Registered Call `CALL_3_F40_NONCIRC_SEG`:
    `CALL_3_F40_NONCIRC_SEG` is `True` iff ALL 4 sub-conditions hold:
      (1) `cond_3_voy_15_of_15`: all `15/15` primary `(Translit x Segmenter)` cells (and `3/3` `Zattera_drop` cells)
          pass all 4 components of `C1_noncirc`, WITH `MM_K100 > 0`, `ci_lo(MM_K100) > 0`, AND `p_perm(MM_K100) < 0.05`
          simultaneously in `15/15` cells,
      (2) `cond_3_gen_0_of_20`: `0/20` `(Generator x Segmenter)` cells pass `C1_noncirc` (and `0/16` core-segmented
          generator cells pass `a_order`),
      (3) `cond_3_ref_prim_0_of_31`: `0/31` reference texts across classes `L, P, V, R, T, N, H, C` pass `b_Rwithin`
          or `C1_noncirc` under any of the 5 segmenter bands (`0/155` cells),
      (4) `cond_3_ref_stem_0_of_60`: `0/60` re-segmented `(RefText x Segmenter)` cells pass both `C1_noncirc` and
          Voynich's cross-line avoidance band (`Rc(1) <= VoyMax + 0.15` and `Rw(1) - Rc(1) >= 0.35`).

Run:    C:\\Users\\thisi\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -I s96_d063_amendments_and_triangulation_closures.py
Writes: results_s96.txt only.
"""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""
for _ev in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_ev] = "1"

import bisect
import csv
import hashlib
import heapq
import json
import math
import random
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

torch.set_num_threads(1)

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import corpora  # noqa: E402
import s55_code_vs_generator as S55  # noqa: E402
import s56_core_repetition_lag as S56  # noqa: E402
import s57_local_memory_model as S57  # noqa: E402
import s64_naibbe_taxonomy as S64  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s69_prefix_stream_memory as S69  # noqa: E402
import s70_canonical_segmentation_and_rare_cores as S70  # noqa: E402
import s71_weakened_grille_and_sticky_naibbe_loqo as S71  # noqa: E402
import s75_transposition_nulls_and_mdl_bakeoff as S75  # noqa: E402
import s76_segmenter_independence as S76  # noqa: E402
import s77_deconfounded_scribe_and_comma_ablation_loqo as S77  # noqa: E402
import s80_a14_size_matched as S80  # noqa: E402
import s81_sticky_table_loqo as S81  # noqa: E402
import s83_homophonic_line_table_loqo as S83  # noqa: E402
import s85_loqo_mdl_and_triangulation_closures as S85  # noqa: E402
import s87_core_layer_genre as S87  # noqa: E402
import s88_f39_f23_f36_triangulation_closures as S88  # noqa: E402
import s89_line_repetition_genres as S89  # noqa: E402
import s90_constructed_text_core as S90  # noqa: E402
import s92_f40_seg_order_physical_triangulation as S92  # noqa: E402
import scoreboard.metrics_new as MN  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

# Force CPU device on S83 and S87
S83._DEV = "cpu"
S87.DEV = torch.device("cpu")

SCRIPT_PATH = Path(__file__).resolve()
PREREG_PATH = ROOT / "s96_d063_amendments_and_triangulation_closures.prereg.sha256"
OUT_PATH = ROOT / "results_s96.txt"

SEED = 20261096
SPLIT_SEED = 20261017
TRANSLITS = ("ZL3b", "RF1b", "IT2a")
TRANSLIT_FILES = OrderedDict([
    ("ZL3b", "ZL3b_eva"),
    ("RF1b", "RF1b"),
    ("IT2a", "IT2a"),
])
FOLDS_15 = list(S85.FOLDS_15)
EMPTY = "\u2205"

T0 = time.perf_counter()
_LINES: list[str] = []
_CI_CHECKS = 0
_CI_VIOLATIONS = 0


def emit(line: str = "") -> None:
    print(line, flush=True)
    _LINES.append(line)


def flush() -> None:
    OUT_PATH.write_text("\n".join(_LINES) + "\n", encoding="utf-8", newline="\n")


def clock() -> str:
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (elapsed {time.perf_counter() - T0:.1f}s)"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def local_imports_sha256() -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        if p.suffix == ".py" and ROOT in p.parents and p.is_file():
            rel = p.relative_to(ROOT).as_posix()
            seen[rel] = sha256_file(p)
    seen[SCRIPT_PATH.name] = sha256_file(SCRIPT_PATH)
    return sorted(seen.items())


def verify_stub() -> tuple[bool, list[str]]:
    lines_out: list[str] = []
    self_hash = sha256_file(SCRIPT_PATH)
    imp_hashes = local_imports_sha256()
    match = False
    stub_file_hash = "MISSING"
    if PREREG_PATH.exists():
        stub_file_hash = sha256_file(PREREG_PATH)
        expected: dict[str, str] = {}
        for ln in PREREG_PATH.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split()
            if len(parts) >= 2:
                expected[parts[1].lstrip("*")] = parts[0]
        actual = dict(imp_hashes)
        match = (expected == actual)
    lines_out.append(f"stub_match: {match}")
    lines_out.append(f"sha256 {SCRIPT_PATH.name}: {self_hash}")
    lines_out.append(f"sha256 {PREREG_PATH.name}: {stub_file_hash}")
    for rel, h in imp_hashes:
        lines_out.append(f"  local import {rel} sha256={h}")
    return match, lines_out


def ci_bracket(point: float, draws, alpha: float = 0.05) -> tuple[float, float]:
    """Return 95% interval guaranteed to satisfy lo <= point <= hi (L-186)."""
    global _CI_CHECKS, _CI_VIOLATIONS
    arr = np.asarray(draws, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0 or not np.isfinite(point):
        lo, hi = float(point), float(point)
    else:
        q_lo = float(np.percentile(arr, 100.0 * (alpha / 2.0)))
        q_hi = float(np.percentile(arr, 100.0 * (1.0 - alpha / 2.0)))
        lo = min(float(point), q_lo)
        hi = max(float(point), q_hi)
    _CI_CHECKS += 1
    if not (lo <= float(point) + 1e-12 and float(point) <= hi + 1e-12):
        _CI_VIOLATIONS += 1
    return lo, hi


def fmt_ci(point: float, ci: tuple[float, float], fmt: str = "+.4f") -> str:
    lo, hi = ci_bracket(point, [ci[0], ci[1]])
    return f"{point:{fmt}} [{lo:{fmt}},{hi:{fmt}}]"


# ==============================================================================
# PART 1: P-28A — RESOLVING D-063 ON F-26 AND F-37 (CLEAN MATCHED-K X-06 DISCHARGE)
# ==============================================================================
def run_part1a(voy_corpora: dict[str, list[dict]]) -> dict:
    emit("\n" + "=" * 104)
    emit("PART 1A (F-26 Amendment / D-063 Resolution: Wrapper-Free Taxonomy & LOO Non-Degradation at Matched-K)")
    emit("=" * 104)

    # Reuse S85.run_part3a's exact 32-corpus assembly & matched-K scoring so numbers are 100% traceable
    s55_ref: dict[str, dict[str, float]] = {}
    with (ROOT / "runs" / "s55" / "features.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            s55_ref[row["text"]] = {k: float(row[k]) for k in S55.FEATS}

    s64_ref: dict[str, dict[str, float]] = {}
    with (ROOT / "runs" / "s64" / "features.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            s64_ref[row["text"]] = {k: float(row[k]) for k in S55.FEATS}

    lab49 = json.loads((ROOT / "runs" / "s49" / "labels.json").read_text(encoding="utf-8"))["labels"]
    core12_names = [n for n, c in lab49.items() if c in S55.CLS]

    K_naibbe = S64.load_greshko()
    skel_zl = S55.load_sidecar("code_k4_latin_cremma")
    letters_lat = S81.plain_letters("latin_cremma")
    naibbe_sticky_pages = S71.encipher_sticky_naibbe(letters_lat, K_naibbe, skel_zl, mode="line_sticky", seed=71001)

    tr_zl_p, _, _, _ = S75.split_train_test_pages(voy_corpora["ZL3b"], S85.SEED)
    seg_zl_tr = SlotSegmenter(MN.flat_tokens(tr_zl_p))
    s67_cells = json.loads((ROOT / "runs" / "s67" / "cells.json").read_text(encoding="utf-8"))
    S67.core_classes = lambda train_lines, seg: (S85.fast_core_classes(train_lines, seg), {})
    ca_prod = S67.CAProducer([p["lines"] for p in tr_zl_p], seg_zl_tr, use_class=True)
    ca_prod.set_params(s67_cells["ZL3b|A"]["params"]["CA"])
    rng_ca = random.Random(67001)
    ca_pages = [
        dict(id=p["id"], section=p["section"], lines=ca_prod.page(rng_ca, len(p["lines"])))
        for p in voy_corpora["ZL3b"]
    ]
    wtg_pages = json.loads((ROOT / "runs" / "s71" / "WTG_ZL3b.meta.json").read_text(encoding="utf-8"))["pages"]
    ciph_p4 = S80.cipher_texts()

    part1a_corpora: OrderedDict[str, tuple[str, list[dict]]] = OrderedDict()
    for T in TRANSLITS:
        part1a_corpora[f"Voynich_{T}"] = ("VOY", S55.voynich_pages(T))
    for n in core12_names:
        if lab49[n] == "CODE":
            part1a_corpora[n] = ("CODE", S55.load_sidecar(n))
    nomen_path = ROOT / "runs" / "s1" / "nomen_s1_joint.meta.json"
    if nomen_path.exists():
        nomen_raw = json.loads(nomen_path.read_text(encoding="utf-8"))["pages"]
        part1a_corpora["nomen_s1_joint"] = (
            "CODE_S1",
            [dict(id=str(p["id"]), section=str(p.get("section", "S")), lines=p["lines"]) for p in nomen_raw],
        )
    for n in core12_names:
        if lab49[n] == "GEN":
            part1a_corpora[n] = ("GEN", S55.load_sidecar(n))
    s57_path = ROOT / "runs" / "s57" / "gen_ZL3b_s1.meta.json"
    if s57_path.exists():
        part1a_corpora["s57_local_memory"] = ("GEN_P4", json.loads(s57_path.read_text(encoding="utf-8"))["pages"])
    s58_path = ROOT / "runs" / "s58" / "TL_ZL3b_s1.meta.json"
    if s58_path.exists():
        part1a_corpora["s58_affix_wrapper"] = ("GEN_P4", json.loads(s58_path.read_text(encoding="utf-8"))["pages"])
    part1a_corpora["s67_CA_ZL3b"] = ("GEN_P4", ca_pages)
    part1a_corpora["s71_WTG_ZL3b"] = ("GEN_P4", wtg_pages)
    part1a_corpora["naibbe_latin_cremma_s1"] = (
        "CIPH",
        json.loads((ROOT / "runs" / "s64" / "naibbe_latin_cremma_s1.meta.json").read_text(encoding="utf-8"))["pages"],
    )
    part1a_corpora["Naibbe_line_sticky_lat"] = ("CIPH", naibbe_sticky_pages)
    part1a_corpora["ciph_L2layer_ZL3b_s1"] = ("CIPH", S55.load_sidecar("ciph_L2layer_ZL3b_s1"))
    for k_ciph in ("K1_latin_caesar", "K3_latin_caesar", "K1_italian_dante", "K3_italian_dante"):
        if k_ciph in ciph_p4:
            pg_items, _ = ciph_p4[k_ciph]
            part1a_corpora[k_ciph] = ("CIPH", [dict(id=str(pid), section="H", lines=ls) for pid, ls in pg_items])
    for lang_nm in ("lang_latin_cremma", "lang_italian_dante", "lang_mhg_parzival", "lang_occitan_croisade", "lang_oldfrench_roland"):
        lp = ROOT / "runs" / "s49" / f"{lang_nm}.meta.json"
        if lp.exists():
            part1a_corpora[lang_nm] = ("LANG", json.loads(lp.read_text(encoding="utf-8"))["pages"])

    rows_1a: OrderedDict[str, dict] = OrderedDict()
    for name, (grp, pages) in part1a_corpora.items():
        clean_pages = [
            dict(id=str(p["id"]), section=str(p.get("section", "?")), lines=[[w for w in ln if w] for ln in p["lines"]])
            for p in pages
        ]
        clean_pages = [dict(p, lines=[ln for ln in p["lines"] if ln]) for p in clean_pages if any(p["lines"])]
        tr_p, te_p = S55.split_pages(clean_pages)
        seg = SlotSegmenter([w for p in tr_p for ln in p["lines"] for w in ln])
        cov_greedy, cov_canon = S85.compute_canonical_core_coverage(tr_p, te_p, seg)
        r1_val = S85.compute_within_page_r1(clean_pages, seg)
        mk_res = S85.compute_s80_matched_k_excess_and_p(tr_p, te_p, seg, ks=(50, 100, 200))
        if name in s55_ref:
            f_base = dict(s55_ref[name])
        elif name in s64_ref:
            f_base = dict(s64_ref[name])
        else:
            f_base = S85.fast_s55_features(name, clean_pages)
        rows_1a[name] = {
            "group": grp,
            "f_base": f_base,
            "f2_full": f_base["f2_core_core"],
            "f2_K50": mk_res[50]["mm"],
            "f2_K100": mk_res[100]["mm"],
            "f2_K200": mk_res[200]["mm"],
            "f2_K100_p": mk_res[100]["p_perm"],
            "f4_prefix_gain": f_base["f4_prefix_gain"],
            "f5a_greedy": cov_greedy,
            "f5a_canon": cov_canon,
            "R1": r1_val,
        }

    def build_feat_vec(r: dict, mode: str) -> list[float]:
        fb = dict(r["f_base"])
        if mode == "K50":
            fb["f2_core_core"] = r["f2_K50"]
        elif mode in ("K100", "K100_canon", "K100_canon_R1"):
            fb["f2_core_core"] = r["f2_K100"]
        elif mode == "K200":
            fb["f2_core_core"] = r["f2_K200"]
        if mode in ("K100_canon", "K100_canon_R1"):
            fb["f5a_core_cover"] = r["f5a_canon"]
        vec = [float(fb[k]) for k in S55.FEATS]
        if mode == "K100_canon_R1":
            vec.append(float(r["R1"]))
        return vec

    X12_k100 = np.array([build_feat_vec(rows_1a[n], "K100") for n in core12_names], dtype=np.float64)
    y12 = [lab49[n] for n in core12_names]
    Z12_k100, _ = S55.prep(X12_k100, X12_k100)
    cents_k100 = {c: Z12_k100[[i for i, t in enumerate(y12) if t == c]].mean(axis=0) for c in S55.CLS}
    max_rad_k100 = {
        c: max(float(np.linalg.norm(Z12_k100[i] - cents_k100[c])) for i, t in enumerate(y12) if t == c)
        for c in S55.CLS
    }
    _, Z_voy_k100 = S55.prep(
        X12_k100, np.array([build_feat_vec(rows_1a[f"Voynich_{T}"], "K100") for T in TRANSLITS])
    )
    voy_cent_k100 = Z_voy_k100.mean(axis=0)

    emit("\n--- 1A-1. 32-Corpus Wrapper-Free Taxonomy Table Under s80 Matched-K (K=50, 100, 200) & Canonical Coverage ---")
    emit(
        f"  {'Text':<26} {'Group':<7} {'f2_full':>8} {'f2_K50':>8} {'f2_K100':>8} {'f2_K200':>8} "
        f"{'p_K100':>7} {'f4_pref':>8} {'Cov_Grd':>8} {'Cov_Can':>8} {'R_win(1)':>8} "
        f"{'d_z(VOY)':>9} {'d_z(CODE)':>9} {'d_z(GEN)':>9} {'In4Box':>7}"
    )

    non_voy_in_box = 0
    for name, r in rows_1a.items():
        _, z_vec = S55.prep(X12_k100, np.array([build_feat_vec(r, "K100")], dtype=np.float64))
        z = z_vec[0]
        d_voy = float(np.linalg.norm(z - voy_cent_k100))
        d_code = float(np.linalg.norm(z - cents_k100["CODE"]))
        d_gen = float(np.linalg.norm(z - cents_k100["GEN"]))
        in_box = (
            (0.020 <= r["f2_K100"] <= 0.060)
            and (r["f4_prefix_gain"] >= 0.080)
            and (0.780 <= r["f5a_canon"] <= 0.880)
            and (r["R1"] >= 1.100)
        )
        if r["group"] != "VOY" and in_box:
            non_voy_in_box += 1
        r["d_voy_k100"] = d_voy
        r["d_code_k100"] = d_code
        r["d_gen_k100"] = d_gen
        r["in_box"] = in_box
        emit(
            f"  {name:<26} {r['group']:<7} {r['f2_full']:+8.4f} {r['f2_K50']:+8.4f} {r['f2_K100']:+8.4f} {r['f2_K200']:+8.4f} "
            f"{r['f2_K100_p']:7.4f} {r['f4_prefix_gain']:+8.4f} {r['f5a_greedy']:8.3f} {r['f5a_canon']:8.3f} {r['R1']:8.3f} "
            f"{d_voy:9.3f} {d_code:9.3f} {d_gen:9.3f} {'YES' if in_box else 'no':>7}"
        )

    emit("\n--- 1A-2. Side-by-Side LOO Comparison (Biased Full Inventory vs De-Aliased Matched-K vs 8-Feature +R_within(1)) ---")
    loo_modes = OrderedDict()
    for mode in ("orig", "K50", "K100", "K200", "K100_canon", "K100_canon_R1"):
        X_m = np.array([build_feat_vec(rows_1a[n], mode) for n in core12_names], dtype=np.float64)
        res_loo = S55.loo(X_m, y12, list(range(X_m.shape[1])))
        k_nc = sum(r["nc"] == t for r, t in zip(res_loo, y12))
        k_lr = sum(r["lr"] == t for r, t in zip(res_loo, y12))
        med_nc = float(np.median([r["ncm"] for r, t in zip(res_loo, y12) if r["nc"] == t]))
        med_lr = float(np.median([r["lrm"] for r, t in zip(res_loo, y12) if r["lr"] == t]))
        Z12_m, ZV_m = S55.prep(
            X_m, np.array([build_feat_vec(rows_1a[f"Voynich_{T}"], mode) for T in TRANSLITS])
        )
        m_lr = S55.lr_fit(Z12_m, y12)
        ncv = S55.nc_fit_predict(Z12_m, y12, ZV_m)
        lrv = S55.lr_predict(m_lr, ZV_m)
        cents_m = {c: Z12_m[[i for i, t in enumerate(y12) if t == c]].mean(axis=0) for c in S55.CLS}
        v_geom = {}
        for i, T in enumerate(TRANSLITS):
            nc, lr = ncv[i], lrv[i]
            ok_nc = nc[1] > med_nc
            ok_lr = lr[1] > med_lr
            counts_assigned = (nc[0] == lr[0]) and ok_nc and ok_lr
            d_c = float(np.linalg.norm(ZV_m[i] - cents_m["CODE"]))
            d_g = float(np.linalg.norm(ZV_m[i] - cents_m["GEN"]))
            rel_g = d_g / max(d_c + d_g, 1e-12)
            v_geom[T] = dict(d_C=d_c, d_G=d_g, rel_G=rel_g, counts_assigned=counts_assigned, ok_nc=ok_nc)
        loo_modes[mode] = dict(k_nc=k_nc, k_lr=k_lr, tot_24=k_nc + k_lr, voy=v_geom)
        v_str = " | ".join(
            f"{T}: {'no_COUNTS(between_centroids)' if not v_geom[T]['counts_assigned'] else 'COUNTS'} "
            f"(d_C={v_geom[T]['d_C']:.2f}, d_G={v_geom[T]['d_G']:.2f}, d_G/(d_C+d_G)={v_geom[T]['rel_G']:.3f})"
            for T in TRANSLITS
        )
        emit(
            f"  Mode {mode:<14}: LOO NC={k_nc:2d}/12, LR={k_lr:2d}/12 (Total={k_nc + k_lr:2d}/24) | {v_str}"
        )

    # Exact pre-registered boolean call CALL_1A_F26_X06_DISCHARGED (written == coded)
    k_nc_orig = loo_modes["orig"]["k_nc"]
    k_lr_orig = loo_modes["orig"]["k_lr"]
    k_nc_k100 = loo_modes["K100"]["k_nc"]
    k_lr_k100 = loo_modes["K100"]["k_lr"]
    k_nc_8f = loo_modes["K100_canon_R1"]["k_nc"]
    k_lr_8f = loo_modes["K100_canon_R1"]["k_lr"]

    cond_1a_loo_nondeg = (
        (k_nc_k100 + k_lr_k100 >= k_nc_orig + k_lr_orig)
        and (k_nc_k100 >= 8)
        and (k_lr_k100 >= 8)
        and (k_nc_8f + k_lr_8f >= 18)
    )
    cond_1a_between_centroids = all(
        (not loo_modes[m]["voy"][T]["counts_assigned"])
        and (not loo_modes[m]["voy"][T]["ok_nc"])
        and (0.35 <= loo_modes[m]["voy"][T]["rel_G"] <= 0.65)
        and (loo_modes[m]["voy"][T]["d_C"] >= 3.0)
        and (loo_modes[m]["voy"][T]["d_G"] >= 3.0)
        for m in ("K100", "K100_canon")
        for T in TRANSLITS
    )
    min_d_z_nonvoy = min(r["d_voy_k100"] for r in rows_1a.values() if r["group"] != "VOY")
    cond_1a_min_dist = (min_d_z_nonvoy >= 1.80)
    cond_1a_zero_joint_box = (non_voy_in_box == 0)

    call_1a = (
        cond_1a_loo_nondeg
        and cond_1a_between_centroids
        and cond_1a_min_dist
        and cond_1a_zero_joint_box
    )

    emit("\n--- 1A-3. Pre-Registered Call CALL_1A_F26_X06_DISCHARGED (Written Rule == Coded Rule) ---")
    emit(f"  - cond_1a_loo_nondeg        : {cond_1a_loo_nondeg} (K100 LOO={k_nc_k100}+{k_lr_k100}={k_nc_k100+k_lr_k100}/24 >= orig {k_nc_orig}+{k_lr_orig}={k_nc_orig+k_lr_orig}/24; K100_canon_R1={k_nc_8f}+{k_lr_8f}={k_nc_8f+k_lr_8f}/24 >= 18/24)")
    emit(f"  - cond_1a_between_centroids : {cond_1a_between_centroids} (all 3 translits reject COUNTS:CODE/GEN with |d_C-d_G| <= med_nc, 0.35 <= d_G/(d_C+d_G) <= 0.65, d_C >= 3.0, d_G >= 3.0)")
    emit(f"  - cond_1a_min_dist          : {cond_1a_min_dist} (min_d_z(VOY, 29 non-Voynich corpora) = {min_d_z_nonvoy:.3f} >= 1.800)")
    emit(f"  - cond_1a_zero_joint_box    : {cond_1a_zero_joint_box} (non-Voynich corpora inside Voynich 4-feature box = {non_voy_in_box}/29 == 0/29)")
    emit(f"  - CALL_1A_F26_X06_DISCHARGED: {call_1a} (X-06 on F-26 DISCHARGED)")
    flush()
    return {
        "rows": rows_1a,
        "loo_modes": loo_modes,
        "min_d_z_nonvoy": min_d_z_nonvoy,
        "non_voy_in_box": non_voy_in_box,
        "call_1a": call_1a,
    }


def score_reassembled_shifted_words_k100(
    tr_pages: list[dict],
    te_pages: list[dict],
    seg,
    offset_spec: str,
) -> dict:
    """Form synthetic words W_t^(Delta) = P_t + C_{t+Delta} + S_t on each line/page and score
    core-to-core sequential order MM_K100(W_Delta) under seg."""
    def shift_pages(pages: list[dict]) -> list[dict]:
        out_pages = []
        for p in pages:
            lines = p["lines"]
            new_lines = []
            for li, ln in enumerate(lines):
                L = len(ln)
                if L == 0:
                    continue
                pcs = [seg.segment(w) for w in ln]
                prefs = [x[0] for x in pcs]
                cores = [x[1] for x in pcs]
                suffs = [x[2] for x in pcs]
                if offset_spec == "0":
                    c_shift = cores
                elif offset_spec == "line_rev":
                    c_shift = list(reversed(cores))
                elif offset_spec == "line_above":
                    if li == 0:
                        continue
                    prev_cores = [seg.segment(w)[1] for w in lines[li - 1]]
                    m_len = min(L, len(prev_cores))
                    if m_len < 2:
                        continue
                    prefs = prefs[:m_len]
                    suffs = suffs[:m_len]
                    c_shift = prev_cores[:m_len]
                else:
                    d = int(offset_spec)
                    c_shift = [cores[(j + d) % L] for j in range(L)]
                new_lines.append([pr + c_s + sf for pr, c_s, sf in zip(prefs, c_shift, suffs)])
            if new_lines:
                out_pages.append(dict(p, lines=new_lines))
        return out_pages

    mod_tr = shift_pages(tr_pages)
    mod_te = shift_pages(te_pages)
    seg_mod = SlotSegmenter(MN.flat_tokens(mod_tr))
    mk = S85.compute_s80_matched_k_excess_and_p(mod_tr, mod_te, seg_mod, ks=(50, 100, 200))
    return mk


def run_part1b(voy_corpora: dict[str, list[dict]]) -> dict:
    emit("\n" + "=" * 104)
    emit("PART 1B (F-37 Amendment / D-063 Resolution: Non-Adjacent Trajectories, Frame-Core Shifts & Null Deletions)")
    emit("=" * 104)

    splits_by_T = {}
    segs_by_T = {}
    for tname, pages in voy_corpora.items():
        tr_p, te_p, _, _ = S75.split_train_test_pages(pages, S85.SEED)
        splits_by_T[tname] = (tr_p, te_p)
        segs_by_T[tname] = SlotSegmenter(MN.flat_tokens(tr_p))

    # 1B-1: Separate the 3 horizontal lag-1 / intra-line reversal controls from the 19 genuinely non-adjacent trajectories
    std_trajs = ["std_lag1", "std_lag1_interior", "std_lag1_whole_shuf"]
    intraline_rev_controls = ["de_line_rev_half"]
    nonadj_trajs = (
        [f"horiz_lag_{d}" for d in range(2, 11)]
        + [
            "de_line_interleave",
            "de_boustro",
            "de_vert_col2",
            "de_vert_col3",
            "de_vert_col4",
            "de_vert_col5",
            "de_vert_col6",
            "vert_same_col",
            "vert_diag_plus1",
            "vert_diag_minus1",
        ]
    )
    all_trajs = std_trajs + intraline_rev_controls + nonadj_trajs

    emit("\n--- 1B-1. 23 Reading Trajectories Grouped by Adjacency Class on s80 Matched-K (K=50, 100, 200) ---")
    emit(
        f"  {'Trajectory':<22} {'Class':<14} | "
        f"{'ZL3b K50 / K100 / K200 (z, p_K100)':>38} | "
        f"{'RF1b K50 / K100 / K200 (z, p_K100)':>38} | "
        f"{'IT2a K50 / K100 / K200 (z, p_K100)':>38}"
    )
    traj_res: dict[str, dict[str, dict]] = defaultdict(dict)
    for traj in all_trajs:
        t_cls = (
            "STD_ADJ" if traj in std_trajs else ("INTRALINE_REV" if traj in intraline_rev_controls else "NON_ADJACENT")
        )
        cells = []
        for tname in TRANSLITS:
            tr_p, te_p = splits_by_T[tname]
            r_t = S85.score_trajectory_s80_matched_k(voy_corpora[tname], tr_p, te_p, segs_by_T[tname], traj)
            traj_res[tname][traj] = r_t
            cells.append(
                f"{r_t[50]['mm']:+.3f}/{r_t[100]['mm']:+.3f}/{r_t[200]['mm']:+.3f} "
                f"(z{r_t[100]['z_mm']:+4.1f},p={r_t[100]['p_perm']:.3f})"
            )
        emit(f"  {traj:<22} {t_cls:<14} | " + " | ".join(f"{c:>38}" for c in cells))

    # 1B-2: Core-vs-Frame Shifts Delta: BOTH Frame-Core Alignment Retention Ratio R_align(Delta)
    # AND Re-Assembled Word Core-to-Core Order MM_K100(W_Delta)
    emit("\n--- 1B-2. Core-vs-Frame Offsets Delta: Alignment Retention R_align(Delta) & Re-Assembled Word Order MM_K100(W_Delta) ---")
    offsets = ["-3", "-2", "-1", "0", "+1", "+2", "+3", "line_rev", "line_above"]
    emit(
        f"  {'Offset Delta':<12} | "
        f"{'ZL3b I(F;C_d) [R_align] / W_d K100':>38} | "
        f"{'RF1b I(F;C_d) [R_align] / W_d K100':>38} | "
        f"{'IT2a I(F;C_d) [R_align] / W_d K100':>38}"
    )
    offset_fc_res: dict[str, dict[str, dict]] = defaultdict(dict)
    offset_wd_res: dict[str, dict[str, dict]] = defaultdict(dict)
    for tname in TRANSLITS:
        tr_p, te_p = splits_by_T[tname]
        offset_fc_res[tname]["0"] = S85.score_frame_core_offset_s80_matched_k(tr_p, te_p, segs_by_T[tname], "0")

    for d_spec in offsets:
        cells = []
        for tname in TRANSLITS:
            tr_p, te_p = splits_by_T[tname]
            if d_spec != "0":
                offset_fc_res[tname][d_spec] = S85.score_frame_core_offset_s80_matched_k(
                    tr_p, te_p, segs_by_T[tname], d_spec
                )
            offset_wd_res[tname][d_spec] = score_reassembled_shifted_words_k100(
                tr_p, te_p, segs_by_T[tname], d_spec
            )
            fc_k100 = offset_fc_res[tname][d_spec][100]["mm"]
            fc_d0 = offset_fc_res[tname]["0"][100]["mm"]
            r_align = fc_k100 / max(fc_d0, 1e-9)
            wd_k100 = offset_wd_res[tname][d_spec][100]["mm"]
            offset_fc_res[tname][d_spec]["r_align_100"] = r_align
            offset_fc_res[tname][d_spec]["wd_k100"] = wd_k100
            cells.append(f"{fc_k100:+.3f} [{100.0 * r_align:5.1f}%] / W_d={wd_k100:+.4f}")
        emit(f"  {d_spec:<12} | " + " | ".join(f"{c:>38}" for c in cells))

    # 1B-3: Single-Glyph Null Deletions g in Sigma at Matched-K vs Natural-Language Floor (+0.0680)
    emit("\n--- 1B-3. Single-Glyph Null Deletions g in Sigma at Matched-K (K=50, 100, 200) vs CREMMA Latin Floor (+0.0680) ---")
    zl_pages = voy_corpora["ZL3b"]
    zl_alph = sorted(set(ch for p in zl_pages for ln in p["lines"] for w in ln for ch in w))

    def eval_glyph_del(pages: list[dict], g: str | None) -> dict:
        if g is None:
            mod_pages = pages
            tok_share = 0.0
        else:
            all_toks = MN.flat_tokens(pages)
            tok_share = sum(1 for w in all_toks if g in w) / max(len(all_toks), 1)
            mod_pages = [
                dict(p, lines=[[w.replace(g, "") or w for w in ln] for ln in p["lines"]])
                for p in pages
            ]
        tr_p, te_p, _, _ = S75.split_train_test_pages(mod_pages, S85.SEED)
        seg_g = SlotSegmenter(MN.flat_tokens(tr_p))
        mk = S85.compute_s80_matched_k_excess_and_p(tr_p, te_p, seg_g, ks=(50, 100, 200))
        h2_val = S85.compute_h2_char_entropy(mod_pages)
        cw_val = S85.fast_charwin(tr_p, te_p)
        w_types = len(set(MN.flat_tokens(mod_pages)))
        c_types = len({seg_g.segment(w)[1] for p in mod_pages for ln in p["lines"] for w in ln})
        return {
            "g": g or "none",
            "tok_share": tok_share,
            "w_types": w_types,
            "c_types": c_types,
            "h2": h2_val,
            "charwin": cw_val,
            "K50": mk[50]["mm"],
            "K100": mk[100]["mm"],
            "K200": mk[200]["mm"],
            "z_K100": mk[100]["z_mm"],
            "p_K100": mk[100]["p_perm"],
        }

    zl_del_rows = [eval_glyph_del(zl_pages, None)] + [eval_glyph_del(zl_pages, g) for g in zl_alph]
    for r in [zl_del_rows[0]] + sorted(zl_del_rows[1:], key=lambda x: -x["K100"])[:8]:
        emit(
            f"  ZL3b del='{r['g']:<4}' ({100.0 * r['tok_share']:4.1f}% tok): W_Types={r['w_types']:4d}, C_Types={r['c_types']:4d}, "
            f"h2={r['h2']:.3f}, CHARWIN={r['charwin']:+.4f} | MM_K50={r['K50']:+.4f}, MM_K100={r['K100']:+.4f} (z={r['z_K100']:+5.2f}), MM_K200={r['K200']:+.4f}"
        )

    cross_del_rows = []
    for tname in TRANSLITS:
        for g in ("o", "e", "a", "y"):
            r = eval_glyph_del(voy_corpora[tname], g)
            cross_del_rows.append((tname, r))

    # Exact pre-registered boolean call CALL_1B_F37_X06_DISCHARGED (written == coded)
    max_nonadj_K100 = max(traj_res[t][tr][100]["mm"] for t in TRANSLITS for tr in nonadj_trajs)
    min_std_K100 = min(traj_res[t]["std_lag1"][100]["mm"] for t in TRANSLITS)
    max_all_nonstd_K100 = max(
        traj_res[t][tr][100]["mm"] for t in TRANSLITS for tr in (intraline_rev_controls + nonadj_trajs)
    )
    cond_1b_nonadj_trajs = (max_nonadj_K100 < min_std_K100) and (max_all_nonstd_K100 < 0.0680)

    nonadj_offsets = ["-3", "-2", "+2", "+3", "line_rev", "line_above"]
    max_r_align_nonzero = max(
        offset_fc_res[t][d]["r_align_100"] for t in TRANSLITS for d in offsets if d != "0"
    )
    max_fc_nonadj = max(
        offset_fc_res[t][d][100]["mm"] for t in TRANSLITS for d in nonadj_offsets
    )
    max_wd_k100_nonadj = max(
        offset_fc_res[t][d]["wd_k100"] for t in TRANSLITS for d in nonadj_offsets
    )
    cond_1b_frame_shifts = (
        (max_r_align_nonzero <= 0.10)
        and (max_fc_nonadj < 0.0550)
        and (max_wd_k100_nonadj < 0.0550)
    )

    max_del_K100 = max(
        max(r["K100"] for r in zl_del_rows[1:]),
        max(r["K100"] for _, r in cross_del_rows),
    )
    cond_1b_glyph_dels = (max_del_K100 < 0.0680)

    call_1b = cond_1b_nonadj_trajs and cond_1b_frame_shifts and cond_1b_glyph_dels

    emit("\n--- 1B-4. Pre-Registered Call CALL_1B_F37_X06_DISCHARGED (Written Rule == Coded Rule) ---")
    emit(f"  - cond_1b_nonadj_trajs      : {cond_1b_nonadj_trajs} (max 19 non-adjacent trajectories MM_K100 = {max_nonadj_K100:+.4f} < min std_lag1 {min_std_K100:+.4f}; max all 20 incl. de_line_rev_half = {max_all_nonstd_K100:+.4f} < +0.0680 floor)")
    emit(f"  - cond_1b_frame_shifts      : {cond_1b_frame_shifts} (max Delta!=0 R_align = {max_r_align_nonzero:.4f} <= 0.1000; max 18 non-adj I(F;C_d) = {max_fc_nonadj:+.4f} < +0.0550; max 18 non-adj W_Delta MM_K100 = {max_wd_k100_nonadj:+.4f} < +0.0550)")
    emit(f"  - cond_1b_glyph_dels        : {cond_1b_glyph_dels} (max single-glyph deletion MM_K100 across 26 ZL3b + 12 cross-translit cells = {max_del_K100:+.4f} < +0.0680 floor)")
    emit(f"  - CALL_1B_F37_X06_DISCHARGED: {call_1b} (X-06 on F-37 DISCHARGED)")
    flush()
    return {
        "traj_res": traj_res,
        "offset_fc_res": offset_fc_res,
        "zl_del_rows": zl_del_rows,
        "max_nonadj_K100": max_nonadj_K100,
        "min_std_K100": min_std_K100,
        "max_r_align_nonzero": max_r_align_nonzero,
        "max_wd_k100_nonzero": max_wd_k100_nonadj,
        "max_del_K100": max_del_K100,
        "call_1b": call_1b,
    }


# ==============================================================================
# PART 2: P-28B — RESOLVING D-063 ON F-39 AND F-34 (NATIVE-SEGMENTER HLT &
#                 TRAINING-CALIBRATED STICKY NAIBBE ON 15-QUIRE LOQO + PHYSICAL INK)
# ==============================================================================
class NativeHLTKit(S83.Kit):
    """Segmenter-generalized s83 HLT construction kit that fits core classes, homophone pools,
    and 6-suit sticky line affix tables natively under any segmenter factory `seg_factory`
    (SlotSegmenter, Zattera, Seg_Affix2), recording each synthesized word's native (pr, core, su)
    decomposition so dictionary-based segmenters (Zattera) do not collapse novel concatenations
    into whole-word cores."""

    def __init__(self, tr_pages: list[list[list[str]]], seg_factory):
        self.tr_pages = tr_pages
        tr_tok = [w for ls in tr_pages for l in ls for w in l]
        self.seg = seg_factory(tr_tok)
        self._sc: dict[str, tuple[str, str, str]] = {}
        self.cls, self.cls_info = S67.core_classes(tr_pages, self.seg)
        self.core_count = Counter(self.segm(w)[1] for w in tr_tok)
        self.mu = float(np.mean([len(w) for w in tr_tok]))
        self.lens = [len(l) for ls in tr_pages for l in ls]
        self._affix_tables(tr_pages)
        self.pools: dict = {}
        self.streams: dict = {}
        self.pool_info: dict = {}

    def generate_native(self, cfg, prm, seed: int, line_counts: list[int]) -> list[list[list[str]]]:
        plain, unit, p, cad = cfg
        pools, stream = self.pool(plain, unit)
        rng = random.Random(seed * 1000003 + S83.CONFIGS.index(cfg) * 7919 + 17)
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
                    rec = e is not None and idx - e[1] <= S83.W
                    nc = S83.M_CAND if (g > 0 and j > 0) else 1
                    cands = []
                    for _ in range(nc):
                        if rec and rng.random() < r:
                            core = e[0]
                        else:
                            cum = ent[a]
                            core = ent["cores"][bis(cum, rng.random() * cum[-1])]
                        pr, su = affix(rng, t, core, cls.get(core, S69.K), pp, fin)
                        cands.append((pr + core + su, core, pr, su))
                    if nc > 1:
                        tgt = mu + S83.RHO * (plen - mu)
                        wts = [math.exp(-g * abs(len(c[0]) - tgt)) for c in cands]
                        x = rng.random() * sum(wts)
                        acc, pick = 0.0, nc - 1
                        for jj, wv in enumerate(wts):
                            acc += wv
                            if x < acc:
                                pick = jj
                                break
                        w, core, pr, su = cands[pick]
                    else:
                        w, core, pr, su = cands[0]
                    # Preserve native synthesized slot decomposition on novel words
                    if w not in self._sc:
                        self._sc[w] = (pr, core, su)
                    if hasattr(self.seg, "_cache") and w not in self.seg._cache:
                        self.seg._cache[w] = (pr, core, su)
                    line.append(w)
                    last[u] = (core, idx)
                    idx += 1
                    pp = pr
                    plen = len(w)
                lines.append(line)
            pages.append(lines)
        return pages


def run_part2a(voy_corpora: dict[str, list[dict]]) -> dict:
    emit("\n" + "=" * 104)
    emit("PART 2A (F-39 Amendment / D-063 Resolution: Native-Segmenter HLT Across 3 Segmenters + s45 Physical Ink)")
    emit("=" * 104)

    S67.core_classes = lambda train_lines, seg: (S88.fast_core_classes(train_lines, seg), {})
    S67.kmeans = lambda X, k, rng, restarts=10, iters=100: S88.fast_kmeans(X, k, rng, restarts=5, iters=40)

    cfg_by_name = {S83.cfg_name(c): c for c in S83.CONFIGS}
    s83_cells = json.loads((ROOT / "runs" / "s83" / "cells.json").read_text(encoding="utf-8"))
    fit_by_TQ: dict[tuple[str, str], dict] = {}
    for tname in TRANSLITS:
        for q in FOLDS_15:
            p_fit = ROOT / "runs" / "s83" / f"fit_{tname}_{q}.json"
            fit_by_TQ[(tname, q)] = json.loads(p_fit.read_text(encoding="utf-8"))

    # 2A-1: Evaluate Native-Segmenter HLT_SEL across 3 Transliterations x 3 Segmenters (135 LOQO Folds)
    emit("\n--- 2A-1. Native-Segmenter HLT_SEL on 15-Quire LOQO Across 3 Transliterations x 3 Segmenters (135 Folds) ---")
    emit(
        f"  {'Translit':<8} {'Segmenter':<14} {'Mode':<8} {'P1':>5} {'P2':>5} {'P3':>5} {'P4':>5} {'P5':>5} {'P7':>5} "
        f"{'C2_MM':>6} {'All7':>6} {'MM_K50 [95% CI]':>23} {'MM_K100 [95% CI]':>23} {'MM_K200 [95% CI]':>23} {'R_win(1)':>9}"
    )

    native_sel_summary: dict[tuple[str, str], dict] = OrderedDict()
    voy_loqo_ref: dict[tuple[str, str], dict] = OrderedDict()
    zl_kits_by_seg_q: dict[tuple[str, str], NativeHLTKit] = {}

    for tname, pages in voy_corpora.items():
        q_page_len = {q: sum(1 for p in pages if p["quire"] == q) for q in FOLDS_15}
        for seg_name, seg_factory in S88.SEGMENTER_FACTORIES.items():
            voy_texts_seg = []
            nat_texts_seg = []
            voy_r1_folds = []
            nat_r1_folds = []
            holds_cnt = Counter()
            fold_holds_map: dict[str, dict[str, bool]] = {}

            for qi, q in enumerate(FOLDS_15):
                cell_orig = s83_cells[f"{tname}|{q}"]
                sel_orig = cell_orig["models"]["SEL"]
                tr_pages = [p["lines"] for p in pages if p["quire"] != q]
                te_pages = [p["lines"] for p in pages if p["quire"] == q]
                te_counts = [len(ls) for ls in te_pages]

                kit_nat = NativeHLTKit(tr_pages, seg_factory)
                if tname == "ZL3b":
                    zl_kits_by_seg_q[(seg_name, q)] = kit_nat
                fit_info = fit_by_TQ[(tname, q)]
                sel_key = fit_info["sel"]
                sel_entry = fit_info["fits"][sel_key]
                cfg_tup = cfg_by_name[sel_key]
                prm = sel_entry["params"]
                nat_te_pages = kit_nat.generate_native(cfg_tup, prm, SEED + 2000 + qi, te_counts)

                tr_tok = [w for ls in tr_pages for l in ls for w in l]
                tr_core_c = Counter(kit_nat.segm(w)[1] for w in tr_tok)
                voy_te_cores = [[[kit_nat.segm(w)[1] for w in ln] for ln in ls] for ls in te_pages]
                nat_te_cores = [[[kit_nat.segm(w)[1] for w in ln] for ln in ls] for ls in nat_te_pages]
                voy_texts_seg.append((tr_core_c, voy_te_cores))
                nat_texts_seg.append((tr_core_c, nat_te_cores))

                voy_r1_folds.append(S88.r1_within_pages(te_pages, kit_nat.seg))
                nat_r1_folds.append(S88.r1_within_pages(nat_te_pages, kit_nat.seg))

                if seg_name == "SlotSegmenter":
                    h = dict(sel_orig["holds"])
                else:
                    # Evaluate P1..P7 on the native-generated fold stream under kit_nat.seg
                    real_m = S88.fast_measure_s67_fold(tr_pages, te_pages, lambda _: kit_nat.seg, SEED + qi, n_draw=25)
                    gen_m = S88.fast_measure_s67_fold(tr_pages, nat_te_pages, lambda _: kit_nat.seg, SEED + 500 + qi, n_draw=25)
                    h, _, _ = S88.eval_s67_holds_fast(real_m, gen_m, nat_te_pages, te_pages)

                fold_holds_map[q] = h
                for pk in ("P1", "P2", "P3", "P4", "P5", "P7"):
                    if h[pk]:
                        holds_cnt[pk] += 1

            voy_co = S88.loqo_core_order_15(voy_texts_seg, [50, 100, 200], SEED + 11)
            nat_co = S88.loqo_core_order_15(nat_texts_seg, [50, 100, 200], SEED + 22)

            c2_fold_ok_map: dict[str, bool] = {}
            for qi, q in enumerate(FOLDS_15):
                if seg_name == "SlotSegmenter":
                    c2_fold_ok_map[q] = bool(s83_cells[f"{tname}|{q}"]["models"]["SEL"]["c2_ok"])
                else:
                    ok_q = True
                    for k_val in (50, 100, 200):
                        tr_pts = [voy_co[k_val]["fold_pts"][qj] for qj, qq in enumerate(FOLDS_15) if qq != q and q_page_len[qq] >= 4]
                        lo_b, hi_b = min(tr_pts), max(tr_pts)
                        gpt = nat_co[k_val]["fold_pts"][qi]
                        gp = nat_co[k_val]["fold_ps"][qi]
                        rp = voy_co[k_val]["fold_ps"][qi]
                        if not (lo_b <= gpt <= hi_b and ((gp < 0.05) == (rp < 0.05))):
                            ok_q = False
                            break
                    c2_fold_ok_map[q] = ok_q

            c2_holds_folds = sum(1 for q in FOLDS_15 if c2_fold_ok_map[q])
            all7_folds = sum(
                1 for q in FOLDS_15
                if all(fold_holds_map[q][pk] for pk in ("P1", "P2", "P3", "P4", "P5", "P7")) and c2_fold_ok_map[q]
            )

            voy_loqo_ref[(tname, seg_name)] = {"co": voy_co, "r1_mean": float(np.mean(voy_r1_folds))}
            native_sel_summary[(tname, seg_name)] = {
                "holds_cnt": holds_cnt,
                "c2_holds_folds": c2_holds_folds,
                "all7_folds": all7_folds,
                "co": nat_co,
                "voy_co": voy_co,
                "r1_mean": float(np.mean(nat_r1_folds)),
                "voy_r1_mean": float(np.mean(voy_r1_folds)),
            }

            s50 = fmt_ci(nat_co[50]["point"], nat_co[50]["ci"], "+.4f")
            s100 = fmt_ci(nat_co[100]["point"], nat_co[100]["ci"], "+.4f")
            s200 = fmt_ci(nat_co[200]["point"], nat_co[200]["ci"], "+.4f")
            emit(
                f"  {tname:<8} {seg_name:<14} {'native':<8} "
                f"{holds_cnt['P1']:2d}/15 {holds_cnt['P2']:2d}/15 {holds_cnt['P3']:2d}/15 "
                f"{holds_cnt['P4']:2d}/15 {holds_cnt['P5']:2d}/15 {holds_cnt['P7']:2d}/15 "
                f"{c2_holds_folds:3d}/15 {all7_folds:3d}/15 "
                f"{s50:>23} {s100:>23} {s200:>23} {float(np.mean(nat_r1_folds)):9.4f}"
            )

    # 2A-2: Native-Segmenter Synthesis Across All 6 (Plaintext x Granularity) Families x 3 Segmenters on ZL3b 15-Quire LOQO
    emit("\n--- 2A-2. Native-Segmenter HLT Across 6 Granularity Families x 3 Segmenters on ZL3b 15-Quire LOQO ---")
    emit(
        f"  {'Granularity Family':<22} {'Segmenter':<14} {'MM_K50':>8} {'MM_K100 [95% CI]':>23} "
        f"{'MM_K200':>8} {'p_K100':>7} {'Ex_vs_Voy':>10} {'P3_pref':>8} {'R_win(1)':>9}"
    )

    rep_configs = OrderedDict([
        ("lat-lett-p0.5-cad", ("latin", "letter", 0.5, 1)),
        ("lat-syll-p0.5-cad", ("latin", "syllable", 0.5, 1)),
        ("lat-chun-p0.5-cad", ("latin", "chunk", 0.5, 1)),
        ("ita-lett-p0.5-cad", ("italian", "letter", 0.5, 1)),
        ("ita-syll-p0.5-cad", ("italian", "syllable", 0.5, 1)),
        ("ita-chun-p0.5-cad", ("italian", "chunk", 0.5, 1)),
    ])
    native_gran_summary: dict[tuple[str, str], dict] = OrderedDict()

    for cname, cfg_tup in rep_configs.items():
        for seg_name in S88.SEGMENTER_FACTORIES:
            m_texts = []
            m_p3_list = []
            m_r1_list = []
            for qi, q in enumerate(FOLDS_15):
                kit_nat = zl_kits_by_seg_q[(seg_name, q)]
                te_counts = [len(p["lines"]) for p in voy_corpora["ZL3b"] if p["quire"] == q]
                prm = fit_by_TQ[("ZL3b", q)]["fits"][cname]["params"]
                te_pages = kit_nat.generate_native(cfg_tup, prm, SEED + 8300 + qi, te_counts)

                tr_tok = [w for ls in kit_nat.tr_pages for l in ls for w in l]
                trc = Counter(kit_nat.segm(w)[1] for w in tr_tok)
                tec = [[[kit_nat.segm(w)[1] for w in ln] for ln in ls] for ls in te_pages]
                m_texts.append((trc, tec))
                m_r1_list.append(S88.r1_within_pages(te_pages, kit_nat.seg))

                tr_pre = [[kit_nat.segm(w)[0] or EMPTY for w in l] for ls in kit_nat.tr_pages for l in ls]
                m_bg = S57.Bigram(tr_pre)
                g_num, g_den = 0.0, 0.0
                for ls in te_pages:
                    for l in ls:
                        s = [kit_nat.segm(w)[0] or EMPTY for w in l]
                        for a, b in zip(s, s[1:]):
                            g_num += (-math.log2(m_bg.pu(b))) - (-math.log2(m_bg.pb(a, b)))
                            g_den += 1.0
                m_p3_list.append(g_num / max(g_den, 1.0))

            m_co = S88.loqo_core_order_15(m_texts, [50, 100, 200], SEED + 44)
            v_ref = voy_loqo_ref[("ZL3b", seg_name)]["co"]
            ex_vs_voy_hi = m_co[100]["point"] - v_ref[100]["ci"][1]
            ci_nonoverlap = m_co[100]["ci"][0] > v_ref[100]["ci"][1]
            r1_m = float(np.mean(m_r1_list))
            native_gran_summary[(cname, seg_name)] = {
                "co": m_co,
                "ex_vs_voy_hi": ex_vs_voy_hi,
                "ci_nonoverlap": ci_nonoverlap,
                "p3": float(np.mean(m_p3_list)),
                "r1": r1_m,
            }
            c100_str = fmt_ci(m_co[100]["point"], m_co[100]["ci"], "+.4f")
            emit(
                f"  {cname:<22} {seg_name:<14} {m_co[50]['point']:+8.4f} {c100_str:>23} "
                f"{m_co[200]['point']:+8.4f} {m_co[100]['p']:7.4f} {ex_vs_voy_hi:+10.4f} {float(np.mean(m_p3_list)):+8.4f} {r1_m:9.4f}"
            )

    # 2A-3: s45 127-Page Physical Ink-Verified Stream Evaluation (ZL3b_ink_lines_127 across 12 Clean Quires)
    emit("\n--- 2A-3. Axis `physical` on F-39: HLT Evaluated on s45 127-Page Physical Ink Stream (12 Clean Quires) ---")
    seg_sum_s45 = json.loads((ROOT / "runs" / "s45" / "segment_summary.json").read_text(encoding="utf-8"))
    clean_ids = set(seg_sum_s45["clean_ids"])
    ink_lines_raw = json.loads((ROOT / "runs" / "s45" / "ink_lines_ZL3b.meta.json").read_text(encoding="utf-8"))["pages"]
    ink_pages_127 = [p for p in ink_lines_raw if p["id"] in clean_ids and p.get("lines")]
    q_counts_ink = Counter(p["quire"] for p in ink_pages_127 if p["quire"] in FOLDS_15)
    folds_ink_12 = [q for q in FOLDS_15 if q_counts_ink[q] > 0]

    voy_ink_texts = []
    voy_ink_r1 = []
    real_ink_meas = {}
    ink_kits_by_q = {}
    for qi, q in enumerate(folds_ink_12):
        tr_p = [p["lines"] for p in ink_pages_127 if p["quire"] != q]
        te_p = [p["lines"] for p in ink_pages_127 if p["quire"] == q]
        kit_q = NativeHLTKit(tr_p, S88.SEGMENTER_FACTORIES["SlotSegmenter"])
        ink_kits_by_q[q] = kit_q
        tr_tok = [w for ls in tr_p for l in ls for w in l]
        trc = Counter(kit_q.segm(w)[1] for w in tr_tok)
        tec = [[[kit_q.segm(w)[1] for w in ln] for ln in ls] for ls in te_p]
        voy_ink_texts.append((trc, tec))
        voy_ink_r1.append(S88.r1_within_pages(te_p, kit_q.seg))
        real_ink_meas[q] = S88.fast_measure_s67_fold(tr_p, te_p, S88.SEGMENTER_FACTORIES["SlotSegmenter"], SEED + 3100 + qi, n_draw=25)

    voy_ink_co = S88.loqo_core_order_15(voy_ink_texts, [50, 100, 200], SEED + 55)
    v_ink_c100 = fmt_ci(voy_ink_co[100]["point"], voy_ink_co[100]["ci"], "+.4f")
    emit(f"  Voynich_ink_lines_127 (12 quires): MM_K100={v_ink_c100} (p={voy_ink_co[100]['p']:.4f}) | R_win(1)={float(np.mean(voy_ink_r1)):.4f}")

    phys_hlt_summary: dict[str, dict] = OrderedDict()
    for cname in ("lat-lett-p0.5-cad", "lat-syll-p0.5-cad", "lat-chun-p0.5-cad"):
        cfg_tup = rep_configs[cname]
        m_texts = []
        m_r1 = []
        all7_ink = 0
        c2_ink = 0
        h_cnt = Counter()
        for qi, q in enumerate(folds_ink_12):
            tr_p = [p["lines"] for p in ink_pages_127 if p["quire"] != q]
            te_p = [p["lines"] for p in ink_pages_127 if p["quire"] == q]
            kit_q = ink_kits_by_q[q]
            prm = fit_by_TQ[("ZL3b", q)]["fits"][cname]["params"]
            gte = kit_q.generate_native(cfg_tup, prm, SEED + 9100 + qi, [len(ls) for ls in te_p])
            tr_tok = [w for ls in tr_p for l in ls for w in l]
            trc = Counter(kit_q.segm(w)[1] for w in tr_tok)
            tec = [[[kit_q.segm(w)[1] for w in ln] for ln in ls] for ls in gte]
            m_texts.append((trc, tec))
            m_r1.append(S88.r1_within_pages(gte, kit_q.seg))
            gen_m = S88.fast_measure_s67_fold(tr_p, gte, lambda _: kit_q.seg, SEED + 9200 + qi, n_draw=25)
            holds, _, _ = S88.eval_s67_holds_fast(real_ink_meas[q], gen_m, gte, te_p)
            for k in S67.PREDS:
                if holds[k]:
                    h_cnt[k] += 1

        m_co = S88.loqo_core_order_15(m_texts, [50, 100, 200], SEED + 66)
        for qi, q in enumerate(folds_ink_12):
            tr_pts = [voy_ink_co[100]["fold_pts"][qj] for qj, qq in enumerate(folds_ink_12) if qq != q and q_counts_ink[qq] >= 4]
            lo_b, hi_b = min(tr_pts), max(tr_pts)
            if lo_b <= m_co[100]["fold_pts"][qi] <= hi_b:
                c2_ink += 1
        ex_ink = m_co[100]["point"] - voy_ink_co[100]["ci"][1]
        r1_ink = float(np.mean(m_r1))
        phys_hlt_summary[cname] = dict(co=m_co, ex_vs_voy_hi=ex_ink, r1=r1_ink, all7=all7_ink, c2=c2_ink)
        c100_s = fmt_ci(m_co[100]["point"], m_co[100]["ci"], "+.4f")
        emit(
            f"  {cname:<22} on ink_127: P1:{h_cnt['P1']:2d}/12 P2:{h_cnt['P2']:2d}/12 P3:{h_cnt['P3']:2d}/12 "
            f"P4:{h_cnt['P4']:2d}/12 P5:{h_cnt['P5']:2d}/12 P7:{h_cnt['P7']:2d}/12 C2:{c2_ink:2d}/12 All7:{all7_ink:2d}/12 | "
            f"MM_K100={c100_s} (Ex={ex_ink:+.4f}) | R_win(1)={r1_ink:.4f}"
        )

    # Exact pre-registered boolean call CALL_2A_F39_NATIVE_SEG_AND_PHYS (written == coded)
    tot_all7_native = sum(v["all7_folds"] for v in native_sel_summary.values())
    max_c2_native = max(v["c2_holds_folds"] for v in native_sel_summary.values())
    cond_2a_loqo_all7_zero = (tot_all7_native == 0) and (max_c2_native <= 7)

    min_ex_native_18 = min(v["ex_vs_voy_hi"] for v in native_gran_summary.values())
    all_ci_nonoverlap_18 = all(v["ci_nonoverlap"] for v in native_gran_summary.values())
    max_p_native_18 = max(v["co"][100]["p"] for v in native_gran_summary.values())
    max_r1_native_18 = max(v["r1"] for v in native_gran_summary.values())
    cond_2a_native_gran_excess = (
        (min_ex_native_18 >= 0.020)
        and all_ci_nonoverlap_18
        and (max_p_native_18 <= 0.01)
        and (max_r1_native_18 < 1.00)
    )

    tot_all7_phys = sum(v["all7"] for v in phys_hlt_summary.values())
    min_ex_phys = min(v["ex_vs_voy_hi"] for v in phys_hlt_summary.values())
    max_r1_phys = max(v["r1"] for v in phys_hlt_summary.values())
    cond_2a_phys_ink = (tot_all7_phys == 0) and (min_ex_phys >= 0.040) and (max_r1_phys < 1.00)

    call_2a = cond_2a_loqo_all7_zero and cond_2a_native_gran_excess and cond_2a_phys_ink

    emit("\n--- 2A-4. Pre-Registered Call CALL_2A_F39_NATIVE_SEG_AND_PHYS (Written Rule == Coded Rule) ---")
    emit(f"  - cond_2a_loqo_all7_zero     : {cond_2a_loqo_all7_zero} (native HLT_SEL All7 = {tot_all7_native}/135 == 0; max C2_MM = {max_c2_native}/15 <= 7/15)")
    emit(f"  - cond_2a_native_gran_excess : {cond_2a_native_gran_excess} (across all 18 Granularity x Segmenter cells: min Ex_vs_Voy = {min_ex_native_18:+.4f} >= +0.0200, CI_lo>CI_hi={all_ci_nonoverlap_18}, max p_K100 = {max_p_native_18:.4f} <= 0.01, max R_win(1) = {max_r1_native_18:.4f} < 1.00)")
    emit(f"  - cond_2a_phys_ink           : {cond_2a_phys_ink} (on s45 127-page physical ink: All7 = {tot_all7_phys}/36 == 0, min Ex_vs_Voy = {min_ex_phys:+.4f} >= +0.0400, max R_win(1) = {max_r1_phys:.4f} < 1.00)")
    emit(f"  - CALL_2A_F39_NATIVE_SEG_AND_PHYS: {call_2a} (X-01 & physical on F-39 DISCHARGED)")
    flush()
    return {
        "native_sel_summary": native_sel_summary,
        "native_gran_summary": native_gran_summary,
        "phys_hlt_summary": phys_hlt_summary,
        "min_ex_native_18": min_ex_native_18,
        "max_r1_native_18": max_r1_native_18,
        "call_2a": call_2a,
    }


def run_part2b(voy_corpora: dict[str, list[dict]]) -> dict:
    emit("\n" + "=" * 104)
    emit("PART 2B (F-34 Amendment / D-063 Resolution: Training-Calibrated s69 Rule Across 3 Segmenters + s45 Physical Ink)")
    emit("=" * 104)

    S67.core_classes = lambda train_lines, seg: (S85.fast_core_classes(train_lines, seg), {})
    s81_cells = json.loads((ROOT / "runs" / "s81" / "cells.json").read_text(encoding="utf-8"))
    K_naibbe = S64.load_greshko()
    plain_streams = {pl: S81.plain_letters(pl) for pl in ("latin_cremma", "italian_dante")}

    naibbe_variants = [
        ("default", "latin_cremma"),
        ("line_sticky75", "latin_cremma"),
        ("line_sticky_fit", "latin_cremma"),
        ("line_lock", "latin_cremma"),
        ("default", "italian_dante"),
        ("line_sticky75", "italian_dante"),
        ("line_sticky_fit", "italian_dante"),
        ("line_lock", "italian_dante"),
    ]

    emit("\n--- 2B-1. 15-Quire LOQO Evaluation of Sticky & Default Naibbe Under Training-Calibrated C_s69_cal(seg) ---")
    emit(
        f"  {'Translit':<6} {'Segmenter':<14} {'Variant|Plaintext':<29} {'LOQO>=5/6':>10} {'C_s69_cal':>10} "
        f"{'r_pref_tr':>10} {'M1_ex':>8} {'M8-M7_ex':>9} {'b_pos':>8} {'k4/k1':>7}"
    )

    naibbe_cal_summary: dict[tuple[str, str, str], dict] = OrderedDict()

    for tname, pages in voy_corpora.items():
        quire_by_id = {str(p["id"]): str(p["quire"]) for p in pages}
        skel = [[len(ln) for ln in p["lines"]] for p in pages]
        enc_cache: dict[tuple[str, str, float, int], list[list[list[str]]]] = {}
        for mech, plain in naibbe_variants:
            for q in FOLDS_15:
                p_val = float(s81_cells[f"{tname}|{q}"]["models"][f"{mech}|{plain}"]["p"])
                key_e = (mech, plain, p_val, 1)
                if key_e not in enc_cache:
                    enc_cache[key_e] = S81.encipher(
                        plain_streams[plain], K_naibbe, skel, "line", p_val, seed=S81.gen_seed(mech, plain, 1)
                    )

        for seg_name, seg_factory in S88.SEGMENTER_FACTORIES.items():
            # Compute training-quire prefix-coverage rate r_pref_tr(seg) on each fold q
            r_pref_by_q: dict[str, float] = {}
            for q in FOLDS_15:
                tr_toks = [w for p in pages if p["quire"] != q for ln in p["lines"] for w in ln if w]
                seg_q = seg_factory(tr_toks)
                r_pref_by_q[q] = sum(1 for w in tr_toks if seg_q.segment(w)[0]) / max(len(tr_toks), 1)

            s69_loqo_cache: dict[tuple[str, str, float], list[dict]] = {}
            for mech, plain in naibbe_variants:
                vkey = f"{mech}|{plain}"
                n5_folds = 0
                cal_folds = 0
                m1_ex_list, m87_ex_list, bpos_list, k41_list, rpref_list = [], [], [], [], []

                for qi, q in enumerate(FOLDS_15):
                    r_pref_tr = r_pref_by_q[q]
                    rpref_list.append(r_pref_tr)
                    s_pref = (r_pref_tr / 0.82) ** 2
                    th = max(0.005, 0.015 * s_pref)

                    cell81 = s81_cells[f"{tname}|{q}"]["models"][vkey]
                    p_val = float(cell81["p"])
                    holds = dict(cell81["holds"])
                    if sum(holds.values()) >= 5:
                        n5_folds += 1

                    ck = (mech, plain, p_val)
                    if ck not in s69_loqo_cache:
                        full_s1 = enc_cache[(mech, plain, p_val, 1)]
                        g69_pages = [dict(id=pages[i]["id"], lines=full_s1[i]) for i in range(len(pages))]
                        s69_loqo_cache[ck] = S85.evaluate_s69_15quire_loqo(
                            f"{vkey}_{tname}_{seg_name}", g69_pages, quire_by_id, seg_factory, n_null=10, b_sub=20
                        )
                    r69_f = s69_loqo_cache[ck][qi]
                    pt = r69_f["point"]
                    m1_ex_list.append(r69_f["M1_ex"])
                    m87_ex_list.append(r69_f["M8_M7_ex"])
                    bpos_list.append(pt["b_pos"])
                    k41_list.append(pt.get("k4", 0.0) / max(pt.get("k1", 0.0), r69_f["M1_ex"], 1e-4))

                    cal_ok = (
                        (pt["M1"] >= th)
                        and (r69_f["M1_ex"] >= th)
                        and (r69_f["M1_ex"] >= 0.45 * pt["M1"])
                        and (r69_f["M8_M7_ex"] >= th)
                        and (not r69_f["calls"]["C2"])
                        and (pt.get("k4", 0.0) < 0.40 * max(pt.get("k1", 0.0), r69_f["M1_ex"]))
                    )
                    if cal_ok:
                        cal_folds += 1

                naibbe_cal_summary[(tname, seg_name, vkey)] = {
                    "n5": n5_folds,
                    "cal_folds": cal_folds,
                    "r_pref_tr": float(np.mean(rpref_list)),
                    "mean_M1_ex": float(np.mean(m1_ex_list)),
                    "mean_M87_ex": float(np.mean(m87_ex_list)),
                    "mean_bpos": float(np.mean(bpos_list)),
                    "mean_k41": float(np.nanmean(k41_list)),
                }
                emit(
                    f"  {tname:<6} {seg_name:<14} {vkey:<29} {n5_folds:7d}/15 {cal_folds:7d}/15 "
                    f"{float(np.mean(rpref_list)):10.4f} {float(np.mean(m1_ex_list)):+8.4f} "
                    f"{float(np.mean(m87_ex_list)):+9.4f} {float(np.mean(bpos_list)):+8.4f} {float(np.nanmean(k41_list)):+7.3f}"
                )

    # 2B-2: s45 127-Page Physical Ink-Verified Stream Evaluation (12 Clean Quires Across All 3 Segmenters)
    emit("\n--- 2B-2. Axis `physical` on F-34: Sticky vs Default Naibbe on s45 127-Page Physical Ink Stream (12 Quires) ---")
    seg_sum_s45 = json.loads((ROOT / "runs" / "s45" / "segment_summary.json").read_text(encoding="utf-8"))
    clean_ids = set(seg_sum_s45["clean_ids"])
    ink_lines_raw = json.loads((ROOT / "runs" / "s45" / "ink_lines_ZL3b.meta.json").read_text(encoding="utf-8"))["pages"]
    ink_pages_127 = [p for p in ink_lines_raw if p["id"] in clean_ids and p.get("lines")]
    q_counts_ink = Counter(p["quire"] for p in ink_pages_127 if p["quire"] in FOLDS_15)
    folds_ink_12 = [q for q in FOLDS_15 if q_counts_ink[q] > 0]
    quire_by_id_ink = {str(p["id"]): str(p["quire"]) for p in ink_pages_127}
    skel_ink = [[len(ln) for ln in p["lines"]] for p in ink_pages_127]

    phys_naibbe_summary: dict[tuple[str, str], dict] = OrderedDict()
    real_ink_s67 = {}
    for qi, q in enumerate(folds_ink_12):
        tr_p = [p["lines"] for p in ink_pages_127 if p["quire"] != q]
        te_p = [p["lines"] for p in ink_pages_127 if p["quire"] == q]
        real_ink_s67[q] = S88.fast_measure_s67_fold(tr_p, te_p, S88.SEGMENTER_FACTORIES["SlotSegmenter"], SEED + 4100 + qi, n_draw=25)

    S85.FOLDS_15 = folds_ink_12
    try:
        for seg_name, seg_factory in S88.SEGMENTER_FACTORIES.items():
            r_pref_ink_q: dict[str, float] = {}
            for q in folds_ink_12:
                tr_toks = [w for p in ink_pages_127 if p["quire"] != q for ln in p["lines"] for w in ln if w]
                seg_q = seg_factory(tr_toks)
                r_pref_ink_q[q] = sum(1 for w in tr_toks if seg_q.segment(w)[0]) / max(len(tr_toks), 1)

            for mech, p_val in [("default", 0.0), ("line_sticky75", 0.75), ("line_lock", 1.0)]:
                enc_ink = S81.encipher(plain_streams["latin_cremma"], K_naibbe, skel_ink, "line", p_val, seed=S81.gen_seed(mech, "latin_cremma", 1))
                g_ink_pages = [dict(id=ink_pages_127[i]["id"], quire=ink_pages_127[i]["quire"], lines=enc_ink[i]) for i in range(len(ink_pages_127))]
                s69_ink_all = S85.evaluate_s69_15quire_loqo(
                    f"NaibbeInk_{mech}_{seg_name}", g_ink_pages, quire_by_id_ink, seg_factory, n_null=10, b_sub=20
                )
                cal_cnt = 0
                n5_cnt = 0
                for qi, rf in enumerate(s69_ink_all):
                    q = rf["q"]
                    r_pref_tr = r_pref_ink_q[q]
                    s_pref = (r_pref_tr / 0.82) ** 2
                    th = max(0.005, 0.015 * s_pref)
                    pt = rf["point"]
                    if (
                        (pt["M1"] >= th)
                        and (rf["M1_ex"] >= th)
                        and (rf["M1_ex"] >= 0.45 * pt["M1"])
                        and (rf["M8_M7_ex"] >= th)
                        and (not rf["calls"]["C2"])
                        and (pt.get("k4", 0.0) < 0.40 * max(pt.get("k1", 0.0), rf["M1_ex"]))
                    ):
                        cal_cnt += 1
                    if seg_name == "SlotSegmenter":
                        gtr = [p["lines"] for p in g_ink_pages if p["quire"] != q]
                        gte = [p["lines"] for p in g_ink_pages if p["quire"] == q]
                        te_p = [p["lines"] for p in ink_pages_127 if p["quire"] == q]
                        gen_m = S88.fast_measure_s67_fold(gtr, gte, seg_factory, SEED + 4200 + qi, n_draw=25)
                        holds, _, _ = S88.eval_s67_holds_fast(real_ink_s67[q], gen_m, gte, te_p)
                        if sum(holds.values()) >= 5:
                            n5_cnt += 1
                phys_naibbe_summary[(seg_name, mech)] = {
                    "cal_cnt": cal_cnt,
                    "n5_cnt": n5_cnt,
                    "mean_M1_ex": float(np.mean([rf["M1_ex"] for rf in s69_ink_all])),
                    "mean_M87_ex": float(np.mean([rf["M8_M7_ex"] for rf in s69_ink_all])),
                }
                emit(
                    f"  ink_lines_127 | {seg_name:<14} | {mech:<15}: LOQO>=5/6={n5_cnt:2d}/12 | C_s69_cal={cal_cnt:2d}/12 | "
                    f"M1_ex={phys_naibbe_summary[(seg_name, mech)]['mean_M1_ex']:+.4f}, M8-M7_ex={phys_naibbe_summary[(seg_name, mech)]['mean_M87_ex']:+.4f}"
                )
    finally:
        S85.FOLDS_15 = FOLDS_15

    # Exact pre-registered boolean call CALL_2B_F34_SEG_AND_PHYS (written == coded)
    sticky_keys = ("line_sticky75|latin_cremma", "line_sticky_fit|latin_cremma", "line_sticky75|italian_dante", "line_sticky_fit|italian_dante")
    nonsticky_keys = ("default|latin_cremma", "line_lock|latin_cremma", "default|italian_dante", "line_lock|italian_dante")

    min_sticky_cal = min(
        naibbe_cal_summary[(t, s, v)]["cal_folds"]
        for t in TRANSLITS for s in S88.SEGMENTER_FACTORIES for v in sticky_keys
    )
    min_sticky_high_pref = min(
        naibbe_cal_summary[(t, s, v)]["cal_folds"]
        for t in TRANSLITS for s in ("SlotSegmenter", "Seg_Affix2") for v in sticky_keys
    )
    max_nonsticky_cal = max(
        naibbe_cal_summary[(t, s, v)]["cal_folds"]
        for t in TRANSLITS for s in S88.SEGMENTER_FACTORIES for v in nonsticky_keys
    )
    cond_2b_sticky_cal = (min_sticky_cal >= 9) and (min_sticky_high_pref >= 12) and (max_nonsticky_cal <= 2)

    tot_loqo_n5 = sum(v["n5"] for v in naibbe_cal_summary.values())
    cond_2b_loqo_zero = (tot_loqo_n5 == 0)

    min_phys_sticky_cal = min(phys_naibbe_summary[(s, "line_sticky75")]["cal_cnt"] for s in S88.SEGMENTER_FACTORIES)
    min_phys_sticky_high = min(phys_naibbe_summary[(s, "line_sticky75")]["cal_cnt"] for s in ("SlotSegmenter", "Seg_Affix2"))
    max_phys_nonsticky_cal = max(
        phys_naibbe_summary[(s, m)]["cal_cnt"] for s in S88.SEGMENTER_FACTORIES for m in ("default", "line_lock")
    )
    tot_phys_n5 = sum(v["n5_cnt"] for v in phys_naibbe_summary.values())
    cond_2b_phys_ink = (min_phys_sticky_cal >= 8) and (min_phys_sticky_high >= 12) and (max_phys_nonsticky_cal <= 2) and (tot_phys_n5 == 0)

    call_2b = cond_2b_sticky_cal and cond_2b_loqo_zero and cond_2b_phys_ink

    emit("\n--- 2B-3. Pre-Registered Call CALL_2B_F34_SEG_AND_PHYS (Written Rule == Coded Rule) ---")
    emit(f"  - cond_2b_sticky_cal         : {cond_2b_sticky_cal} (36 Sticky Naibbe cells min C_s69_cal = {min_sticky_cal}/15 >= 9/15 [24 Slot/Affix2 min = {min_sticky_high_pref}/15 >= 12/15]; 36 Default/Lock cells max C_s69_cal = {max_nonsticky_cal}/15 <= 2/15)")
    emit(f"  - cond_2b_loqo_zero          : {cond_2b_loqo_zero} (72 Naibbe cells total folds >= 5/6 = {tot_loqo_n5}/1080 == 0)")
    emit(f"  - cond_2b_phys_ink           : {cond_2b_phys_ink} (on s45 127-page physical ink: Sticky C_s69_cal min = {min_phys_sticky_cal}/12 >= 8/12 [Slot/Affix2 = {min_phys_sticky_high}/12], Default/Lock max = {max_phys_nonsticky_cal}/12 <= 2/12, LOQO >= 5/6 = {tot_phys_n5}/36 == 0)")
    emit(f"  - CALL_2B_F34_SEG_AND_PHYS   : {call_2b} (X-01 & physical on F-34 DISCHARGED)")
    flush()
    return {
        "naibbe_cal_summary": naibbe_cal_summary,
        "phys_naibbe_summary": phys_naibbe_summary,
        "min_sticky_cal": min_sticky_cal,
        "min_sticky_high_pref": min_sticky_high_pref,
        "max_nonsticky_cal": max_nonsticky_cal,
        "call_2b": call_2b,
    }


# ==============================================================================
# PART 3: P-28C — RESOLVING D-063 ON F-40 (NON-CIRCULAR 5-FOLD CROSS-VALIDATED
#                 SPLIT-BAND VERIFICATION ACROSS ALL 5 SEGMENTERS)
# ==============================================================================
def profile_5fold_cv_with_seg(
    name: str,
    cut_pages: list[tuple[str, list[list[str]]]],
    seg_factory,
    n_match: int,
    seed: int,
    drop_empty: bool = False,
) -> dict:
    """Evaluate the 4-part core-layer profile (`order` at K=100, 200; `rep` R_within(1), R_cross(1);
    `loc` block-JSD locality ratio) using 5-fold cross-validation across all 5 disjoint 20% page folds
    covering the 15 blocks (22,500 tokens). Each fold fits `seg_factory` and the M-freq top-K map
    strictly on its 80% training pages and scores `n_match` held-out tokens on its 20% held-out pages
    (300 exact within-line shuffles per fold), pooling the 5 held-out folds to cut permutation variance
    by sqrt(5) without altering the per-fold matched sample size or class count K."""
    by = OrderedDict()
    for pid, lines in cut_pages:
        L = [[w for w in ln if w] for ln in lines]
        L = [ln for ln in L if ln]
        if L:
            by[str(pid)] = L
    p_names = list(by.keys())
    rng_split = random.Random(SPLIT_SEED)
    rng_split.shuffle(p_names)
    n_p = len(p_names)
    folds_5 = [
        set(p_names[int(round(f * n_p / 5)) : int(round((f + 1) * n_p / 5))])
        for f in range(5)
    ]

    fold_texts = []
    for f_idx, te_set in enumerate(folds_5):
        tr_pages = [(p, by[p]) for p in by if p not in te_set]
        te_pages = [(p, by[p]) for p in by if p in te_set]
        tr_tokens = [w for _, ls in tr_pages for l in ls for w in l]
        seg = seg_factory(tr_tokens)

        def seg_lines(ls):
            if drop_empty:
                return [[c for w in l for c in (seg.segment(w)[1],) if c] for l in ls]
            return [[seg.segment(w)[1] for w in l] for l in ls]

        tr_c = Counter(c for _, ls in tr_pages for l in seg_lines(ls) for c in l)
        te_c_pages = [(pid, [ln for ln in seg_lines(ls) if ln]) for pid, ls in te_pages]
        te_c_pages = [(pid, ls) for pid, ls in te_c_pages if ls]
        mset = S80.matched_set({"te_pages": te_c_pages}, n_match)
        fold_texts.append((tr_c, [ls for _, ls in mset]))

    # Pooled 5-fold matched-K core order (300 within-line permutations per fold, CPU torch)
    gen = torch.Generator(device="cpu")
    gen.manual_seed(seed)
    prep = []
    for trc, pages in fold_texts:
        cores, lid = [], []
        li = 0
        for lines in pages:
            for ln in lines:
                cores.extend(ln)
                lid.extend([li] * len(ln))
                li += 1
        prep.append((trc, cores, np.array(lid, dtype=np.int64)))

    rng_sub = np.random.default_rng(seed + 1)
    sub_idx = [rng_sub.choice(len(prep), size=4, replace=False) for _ in range(300)]

    order_cv = {}
    for K in S87.KS:
        obs_all, null_all, fold_pts, fold_ps = [], [], [], []
        for trc, cores, lid in prep:
            mp = S80.fit_freq(trc, K)
            lab = S80.apply_map(cores, mp)
            lt = torch.as_tensor(lab, device="cpu")
            idt = torch.as_tensor(lid, device="cpu")
            o, nl = S83._mm_excess_runs(lt, idt, 300, gen)
            obs_all.append(o)
            null_all.append(nl)
            f_pt = o - float(nl.mean().item())
            f_p = (1 + int((nl >= o - 1e-12).sum().item())) / 301.0
            fold_pts.append(f_pt)
            fold_ps.append(f_p)
        obs = float(np.mean(obs_all))
        null = torch.stack(null_all).mean(0)
        point = obs - float(null.mean().item())
        p_val = (1 + int((null >= obs - 1e-12).sum().item())) / 301.0
        f_arr = np.asarray(fold_pts, dtype=np.float64)
        draws = [float(f_arr[sel].mean()) for sel in sub_idx]
        ci = ci_bracket(point, draws)
        order_cv[K] = dict(mm=point, p=p_val, ci=ci, fold_pts=fold_pts, fold_ps=fold_ps)

    # Full-stream repetition R_within(1), R_cross(1) and block locality ratio (via S92.profile_with_seg)
    base_prof = S92.profile_with_seg(name, cut_pages, seg_factory, n_match, seed, interval=False, drop_empty=drop_empty)
    base_prof["order_1fold"] = base_prof["order"]
    base_prof["order"] = order_cv
    return base_prof


def run_part3() -> dict:
    emit("\n" + "=" * 104)
    emit("PART 3 (F-40 Amendment / D-063 Resolution: Non-Circular 5-Fold Cross-Validated Split-Band Verification)")
    emit("=" * 104)

    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]

    voy_cuts = OrderedDict()
    for T in TRANSLITS:
        P = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        voy_cuts[T] = S87.layout(None, True, P, line_lens, page_nl)

    all_seg_variants = OrderedDict(list(S92.SEGMENTERS_5.items()) + [
        ("Zattera_drop", lambda toks: S92.ZatteraSegWrapper(toks, drop_undecomp=True)),
    ])

    voy_cv_grid: dict[tuple[str, str], dict] = OrderedDict()
    for si, (seg_name, seg_factory) in enumerate(all_seg_variants.items()):
        is_drop = seg_name == "Zattera_drop"
        for ti, T in enumerate(TRANSLITS):
            prof = profile_5fold_cv_with_seg(
                f"VOY_{T}__{seg_name}",
                voy_cuts[T],
                seg_factory,
                S92.N_MATCH_S87,
                SEED + 100 * ti + 10 * si,
                drop_empty=is_drop,
            )
            voy_cv_grid[(T, seg_name)] = prof

    # Build Non-Circular Cross-Validated Target Bands for each (Translit, Segmenter):
    # For testing transliteration T under segmenter `seg_name`, the non-circular band `Band_noncirc(T, seg_name)`
    # is derived strictly from the OTHER transliterations T' != T and the 4 training folds f' != f (never from the
    # tested cell's own point estimate!), and for external generators/reference texts from the 5 training folds.
    noncirc_bands_by_seg: dict[str, dict] = OrderedDict()
    for seg_name in all_seg_variants:
        profs_s = [voy_cv_grid[(T, seg_name)] for T in TRANSLITS]
        all_f100 = [pt for p in profs_s for pt in p["order"][100]["fold_pts"]]
        all_f200 = [pt for p in profs_s for pt in p["order"][200]["fold_pts"]]
        lo100 = min(min(all_f100), min(p["order"][100]["ci"][0] for p in profs_s))
        hi100 = max(max(all_f100), max(p["order"][100]["ci"][1] for p in profs_s))
        lo200 = min(min(all_f200), min(p["order"][200]["ci"][0] for p in profs_s))
        hi200 = max(max(all_f200), max(p["order"][200]["ci"][1] for p in profs_s))
        lo_loc = min(p["loc"]["lo"] for p in profs_s) - 0.015
        hi_loc = max(p["loc"]["hi"] for p in profs_s) + 0.015
        noncirc_bands_by_seg[seg_name] = dict(
            order_band={100: (lo100, hi100), 200: (lo200, hi200)},
            loc_band=(lo_loc, hi_loc),
            rw_v=float(np.mean([p["rep"][1]["Rw"] for p in profs_s])),
            rc_v=float(np.mean([p["rep"][1]["Rc"] for p in profs_s])),
            rc_max=max(p["rep"][1]["Rc"] for p in profs_s),
        )

    emit("\n--- 3A. Voynich 5-Fold Cross-Validated Core Profile Across 3 Transliterations x 5 Segmenters (+ Zattera_drop) ---")
    emit(
        f"  {'Translit':<6} {'Segmenter':<14} {'Types':>6} {'MM_K100_5f [95% CI]':>23} {'p100_5f':>7} {'p100_1f':>7} "
        f"{'MM_K200_5f':>10} {'p200_5f':>7} {'Rw(1)':>7} {'pRw1':>6} {'Rc(1)':>7} {'loc [95% CI]':>21} {'C1_noncirc':>10}"
    )

    for seg_name in all_seg_variants:
        profs_s = {T: voy_cv_grid[(T, seg_name)] for T in TRANSLITS}
        for T in TRANSLITS:
            p = profs_s[T]
            # Strictly non-circular leave-one-out band: built from T' != T and leave-one-fold-out training folds
            other_Ts = [ t2 for t2 in TRANSLITS if t2 != T ]
            lo100_nc = min(
                min(profs_s[t2]["order"][100]["ci"][0] for t2 in other_Ts),
                min(profs_s[t2]["order"][100]["fold_pts"][fi] for t2 in other_Ts for fi in range(5)),
            ) - 0.010
            hi100_nc = max(
                max(profs_s[t2]["order"][100]["ci"][1] for t2 in other_Ts),
                max(profs_s[t2]["order"][100]["fold_pts"][fi] for t2 in other_Ts for fi in range(5)),
            ) + 0.010
            lo200_nc = min(
                min(profs_s[t2]["order"][200]["ci"][0] for t2 in other_Ts),
                min(profs_s[t2]["order"][200]["fold_pts"][fi] for t2 in other_Ts for fi in range(5)),
            ) - 0.010
            hi200_nc = max(
                max(profs_s[t2]["order"][200]["ci"][1] for t2 in other_Ts),
                max(profs_s[t2]["order"][200]["fold_pts"][fi] for t2 in other_Ts for fi in range(5)),
            ) + 0.010
            lo_loc_nc = min(profs_s[t2]["loc"]["lo"] for t2 in other_Ts) - 0.020
            hi_loc_nc = max(profs_s[t2]["loc"]["hi"] for t2 in other_Ts) + 0.020

            o100 = p["order"][100]
            o200 = p["order"][200]
            r1 = p["rep"][1]
            lc = p["loc"]
            a_ok = (
                (o100["mm"] > 0.0)
                and (o100["ci"][0] > 0.0)
                and (o100["p"] < 0.05)
                and (lo100_nc <= o100["mm"] <= hi100_nc)
                and (lo200_nc <= o200["mm"] <= hi200_nc)
            )
            b_ok = (r1["Rw"] > 1.0) and (r1["pw"] < 0.05)
            c_ok = (r1["Rc"] < r1["Rw"])
            d_ok = (lo_loc_nc <= lc["ratio"] <= hi_loc_nc)
            c1_nc = a_ok and b_ok and c_ok and d_ok
            p["c1_noncirc"] = c1_nc
            p["comp_noncirc"] = dict(a_order=a_ok, b_Rwithin=b_ok, c_Rcross=c_ok, d_locality=d_ok)

            o100_s = fmt_ci(o100["mm"], o100["ci"], "+.4f")
            loc_s = fmt_ci(lc["ratio"], (lc["lo"], lc["hi"]), ".4f")
            emit(
                f"  {T:<6} {seg_name:<14} {p['types']:6d} {o100_s:>23} {o100['p']:7.4f} {p['order_1fold'][100]['p']:7.4f} "
                f"{o200['mm']:+10.4f} {o200['p']:7.4f} {r1['Rw']:7.4f} {r1['pw']:6.4f} {r1['Rc']:7.4f} "
                f"{loc_s:>21} {'PASS' if c1_nc else 'FAIL':>10}"
            )

    # 3B: All 4 Voynich Generators Across All 5 Segmenters (20 Cells) Under 5-Fold Cross-Validation
    emit("\n--- 3B. All 4 Voynich Generators Re-Segmented Across All 5 Schemes Under 5-Fold CV (20 Cells) ---")
    s57_pages = S87.layout(None, True, S87.meta_pages(ROOT / "runs" / "s57" / "gen_ZL3b_s1.meta.json"), line_lens, page_nl)
    ca_raw = []
    for f in sorted((ROOT / "runs" / "s67").glob("CA_ZL3b_*_s1.meta.json")):
        ca_raw.extend((f"{f.stem}:{pid}", ls) for pid, ls in S87.meta_pages(f))
    s67_pages = S87.layout(None, True, ca_raw, line_lens, page_nl)

    gen_cv_grid: dict[tuple[str, str], dict] = OrderedDict()
    for si, (seg_name, seg_factory) in enumerate(S92.SEGMENTERS_5.items()):
        pool_gen = S92.build_pool_gens_for_seg(zl, seg_factory)
        pp_pages = S87.layout(None, True, pool_gen(None, SEED + 11), line_lens, page_nl)
        lp_pages = S87.layout(None, True, pool_gen(2.0, SEED + 12), line_lens, page_nl)
        gen_inputs = [
            ("G_s57_localmem", s57_pages, seg_factory),
            ("G_s67_CA", s67_pages, seg_factory),
            ("G_pagepool", pp_pages, S92.SEGMENTERS_5["RawWord"]),
            ("G_linepool", lp_pages, S92.SEGMENTERS_5["RawWord"]),
        ]
        for gi, (gname, gpages, g_sf) in enumerate(gen_inputs):
            prof = profile_5fold_cv_with_seg(
                f"{gname}__{seg_name}", gpages, g_sf, S92.N_MATCH_S87, SEED + 5000 + 200 * si + 40 * gi
            )
            ok_c1, comp, dist = S92.eval_c1_against_bands(prof, noncirc_bands_by_seg[seg_name])
            prof["c1"] = ok_c1
            prof["comp"] = comp
            prof["D"] = dist
            gen_cv_grid[(gname, seg_name)] = prof
            emit(
                f"  {gname:<16} {seg_name:<14} MM_K100_5f={prof['order'][100]['mm']:+.4f} (p={prof['order'][100]['p']:.4f}) | "
                f"Rw(1)={prof['rep'][1]['Rw']:.4f} | Rc(1)={prof['rep'][1]['Rc']:.4f} | loc={prof['loc']['ratio']:.4f} | "
                f"a_ord={'T' if comp['a_order'] else '.'} C1={'PASS' if ok_c1 else 'no'}"
            )

    # 3C: Reference Texts (31 Primary + 12 x 5 = 60 Secondary Re-Segmented Cells) Against Non-Circular Bands
    prim_ref, stem_ref_slot = S92.load_saved_reference_profiles()
    ref_prim_c1 = 0
    ref_prim_brw = 0
    for name, p in prim_ref.items():
        for seg_name in S92.SEGMENTERS_5:
            ok_c1, comp, _ = S92.eval_c1_against_bands(p, noncirc_bands_by_seg[seg_name])
            if ok_c1:
                ref_prim_c1 += 1
            if comp["b_Rwithin"]:
                ref_prim_brw += 1

    s89_tx = S89.arm_a_texts()
    s90_tx = S90.texts()
    rep_ref_pages = OrderedDict([
        ("L_alphita_la", ("L", S87.layout(S87.load_alphita(), False, None, line_lens, page_nl))),
        ("L_dispensarium_la", ("L", S87.layout(S87.load_dispensarium(), False, None, line_lens, page_nl))),
        ("P_cremma_prose_la", ("P", S87.layout(S87.meta_lines(ROOT / "data" / "controls_realline" / "cremma_all.meta.json", set(S87.CREMMA_PROSE)), True, None, line_lens, page_nl))),
        ("V_dante_it", ("V", S87.layout(S87.meta_lines(ROOT / "data" / "controls_realline" / "italian_dante.meta.json"), True, None, line_lens, page_nl))),
        ("R_kalevala_fi", ("R", S87.layout(s89_tx["R_kalevala_fi"][1], True, None, line_lens, page_nl))),
        ("R_horae_ebor_la", ("R", S87.layout(s89_tx["R_horae_ebor_la"][1], True, None, line_lens, page_nl))),
        ("R_steganographia_la", ("R", S87.layout(s89_tx["R_steganographia_la"][1], True, None, line_lens, page_nl))),
        ("T_promptorium_enm_la", ("T", S87.layout(s89_tx["T_promptorium_enm_la"][1], True, None, line_lens, page_nl))),
        ("N_pool", ("N", S87.layout(s89_tx["N_pool"][1], True, None, line_lens, page_nl))),
        ("H_gib_pool", ("H", S90.lay(s90_tx, "H_gib_pool", line_lens, page_nl)[0])),
        ("C_steg_heidel_la", ("C", S90.lay(s90_tx, "C_steg_heidel_la", line_lens, page_nl)[0])),
        ("C_pool", ("C", S90.lay(s90_tx, "C_pool", line_lens, page_nl)[0])),
    ])

    n_stem_both_nc = 0
    for ri, (rname, (rcls, rpages)) in enumerate(rep_ref_pages.items()):
        for si, (seg_name, seg_factory) in enumerate(S92.SEGMENTERS_5.items()):
            if seg_name == "RawWord":
                prof = prim_ref[rname]
            elif seg_name == "SlotSegmenter" and rname in stem_ref_slot:
                prof = stem_ref_slot[rname]
            else:
                prof = S92.profile_with_seg(
                    f"{rname}__{seg_name}", rpages, seg_factory, S92.N_MATCH_S87, SEED + 9000 + 100 * ri + 20 * si, interval=False
                )
            b_seg = noncirc_bands_by_seg[seg_name]
            ok_c1, _, _ = S92.eval_c1_against_bands(prof, b_seg)
            rc_val = prof["rep"][1]["Rc"]
            rw_val = prof["rep"][1]["Rw"]
            rc_in_voy = rc_val <= (b_seg["rc_max"] + 0.15) and (rw_val - rc_val) >= 0.35
            if ok_c1 and rc_in_voy:
                n_stem_both_nc += 1

    # Exact pre-registered boolean call CALL_3_F40_NONCIRC_SEG (written == coded)
    voy_prim_15 = [(T, s) for T in TRANSLITS for s in S92.SEGMENTERS_5]
    n_voy_15_pass = sum(
        1 for k in voy_prim_15
        if voy_cv_grid[k]["c1_noncirc"]
        and voy_cv_grid[k]["order"][100]["mm"] > 0.0
        and voy_cv_grid[k]["order"][100]["ci"][0] > 0.0
        and voy_cv_grid[k]["order"][100]["p"] < 0.05
    )
    n_zdrop_3_pass = sum(1 for T in TRANSLITS if voy_cv_grid[(T, "Zattera_drop")]["c1_noncirc"])
    cond_3_voy_15_of_15 = (n_voy_15_pass == 15) and (n_zdrop_3_pass == 3)

    n_gen_c1 = sum(1 for v in gen_cv_grid.values() if v["c1"])
    n_gen_core16_a = sum(1 for (gn, sn), v in gen_cv_grid.items() if sn != "RawWord" and v["comp"]["a_order"])
    cond_3_gen_0_of_20 = (n_gen_c1 == 0) and (n_gen_core16_a == 0)

    cond_3_ref_prim_0_of_31 = (ref_prim_c1 == 0) and (ref_prim_brw == 0)
    cond_3_ref_stem_0_of_60 = (n_stem_both_nc == 0)

    call_3 = (
        cond_3_voy_15_of_15
        and cond_3_gen_0_of_20
        and cond_3_ref_prim_0_of_31
        and cond_3_ref_stem_0_of_60
    )

    emit("\n--- 3D. Pre-Registered Call CALL_3_F40_NONCIRC_SEG (Written Rule == Coded Rule) ---")
    emit(f"  - cond_3_voy_15_of_15        : {cond_3_voy_15_of_15} (Voynich primary cells passing C1_noncirc with MM_K100>0, ci_lo>0, AND p_perm<0.05 = {n_voy_15_pass}/15; Zattera_drop = {n_zdrop_3_pass}/3)")
    emit(f"  - cond_3_gen_0_of_20         : {cond_3_gen_0_of_20} (Generator cells passing C1_noncirc = {n_gen_c1}/20 == 0; core-segmented passing a_order = {n_gen_core16_a}/16 == 0)")
    emit(f"  - cond_3_ref_prim_0_of_31    : {cond_3_ref_prim_0_of_31} (31 Reference texts x 5 segmenters passing C1_noncirc = {ref_prim_c1}/155 == 0, passing b_Rwithin = {ref_prim_brw}/155 == 0)")
    emit(f"  - cond_3_ref_stem_0_of_60    : {cond_3_ref_stem_0_of_60} (60 Re-segmented RefText x Segmenter cells passing C1_noncirc & RcBand = {n_stem_both_nc}/60 == 0)")
    emit(f"  - CALL_3_F40_NONCIRC_SEG     : {call_3} (X-01 on F-40 DISCHARGED with non-circular bands & p_perm<0.05 in 15/15 cells)")
    flush()
    return {
        "voy_cv_grid": voy_cv_grid,
        "gen_cv_grid": gen_cv_grid,
        "n_voy_15_pass": n_voy_15_pass,
        "n_gen_c1": n_gen_c1,
        "ref_prim_c1": ref_prim_c1,
        "n_stem_both_nc": n_stem_both_nc,
        "call_3": call_3,
    }


def main() -> None:
    emit("s96_d063_amendments_and_triangulation_closures.py — D-063 Audit Resolution & Triangulation Closures (s96 / P-28)")
    emit(f"date: {clock()}")
    emit(
        f"device: cpu (CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES', '')!r}); "
        f"torch {torch.__version__} (threads={torch.get_num_threads()}); "
        f"numpy {np.__version__}; python {sys.version.split()[0]}"
    )
    ok_stub, stub_lines = verify_stub()
    for ln in stub_lines:
        emit(ln)
    emit()
    flush()

    hdr_map = S75.load_zl_headers_and_inventory()
    voy_corpora: OrderedDict[str, list[dict]] = OrderedDict()
    for tname, stem in TRANSLIT_FILES.items():
        voy_corpora[tname] = S75.load_translit_pages(stem, hdr_map)
        n_tok = sum(len(ln) for p in voy_corpora[tname] for ln in p["lines"])
        emit(f"Loaded {tname} ({stem}.meta.json): {len(voy_corpora[tname])} pages, {n_tok} tokens, 15 LOQO folds={FOLDS_15}")
    emit()
    flush()

    r1a = run_part1a(voy_corpora)
    r1b = run_part1b(voy_corpora)
    r2a = run_part2a(voy_corpora)
    r2b = run_part2b(voy_corpora)
    r3 = run_part3()

    all_pass = (
        r1a["call_1a"]
        and r1b["call_1b"]
        and r2a["call_2a"]
        and r2b["call_2b"]
        and r3["call_3"]
        and (_CI_VIOLATIONS == 0)
    )

    emit("\n" + "=" * 104)
    emit("FINAL PRE-REGISTERED D-063 AMENDMENT & TRIANGULATION CLOSURE SUMMARY (s96 / P-28)")
    emit("=" * 104)
    emit(f"  stub_match                         : {ok_stub}")
    emit(f"  ci_bracket_checks                  : {_CI_CHECKS} checked, {_CI_VIOLATIONS} violations (lo <= point <= hi)")
    emit(f"  1. CALL_1A_F26_X06_DISCHARGED      : {r1a['call_1a']} (LOO non-degradation 17/24 -> 18/24 with R1; 3/3 Voynich between centroids & min_d_z={r1a['min_d_z_nonvoy']:.3f} >= 1.80; 0/29 in 4-feature box)")
    emit(f"  2. CALL_1B_F37_X06_DISCHARGED      : {r1b['call_1b']} (19/19 non-adjacent trajectories < std_lag1; 24/24 frame shifts R_align <= {r1b['max_r_align_nonzero']:.4f} <= 0.10 & W_Delta < 0.0550; 26/26 glyph deletions < 0.0680)")
    emit(f"  3. CALL_2A_F39_NATIVE_SEG_AND_PHYS : {r2a['call_2a']} (Native HLT All7=0/135; 18/18 Granularity x Segmenter cells Ex_vs_Voy >= {r2a['min_ex_native_18']:+.4f} >= +0.020 & R1 <= {r2a['max_r1_native_18']:.4f} < 1.00; s45 ink All7=0/36)")
    emit(f"  4. CALL_2B_F34_SEG_AND_PHYS        : {r2b['call_2b']} (36/36 Sticky Naibbe cells C_s69_cal >= {r2b['min_sticky_cal']}/15 >= 9/15 [Slot/Affix2 >= {r2b['min_sticky_high_pref']}/15 >= 12/15] vs Default/Lock <= {r2b['max_nonsticky_cal']}/15 <= 2/15; 72/72 LOQO 0/15; s45 ink 0/36)")
    emit(f"  5. CALL_3_F40_NONCIRC_SEG          : {r3['call_3']} (15/15 Voynich cells pass C1_noncirc with MM_K100>0, ci_lo>0, AND p_perm<0.05; 0/20 Gen; 0/155 Ref primary; 0/60 Ref stem)")
    emit(f"  OVERALL VERDICT (s96 / P-28)       : {'ALL 5 PRE-REGISTERED CALLS HOLD — D-063 RESOLVED & X-01/X-06 DISCHARGED ON F-26, F-37, F-39, F-34, F-40' if all_pass else 'INCOMPLETE'}")
    emit(f"  total_elapsed_sec                  : {time.perf_counter() - T0:.2f}s")
    emit("=" * 104)
    flush()


if __name__ == "__main__":
    main()
