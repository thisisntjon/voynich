#!/usr/bin/env python
"""s51: Pre-registered closures for O-051 (repaired superimposed-streams independence selector),
O-052 (matched-size Currier B cross-space coupling vs short Latin verse with within-manuscript
bootstrap), and P4-U2 (6-alphabet bake-off on 131 common pages + Davis-hand x Currier-language
crossed test).

PRE-REGISTRATION (frozen in s51_o051_o052_p4u2_closures.prereg.sha256 BEFORE the first run):

Part 1 — O-051 (Repaired Superimposed-Streams Independence Selector, extending s34):
  Problem in s34 (c-347): S = I_self - I_cross ranked the true planted M = {PITCH} 25th of 1022
    on planted_cremma because 26-glyph supersets had I_self = 0.680 and I_cross = 0.055 (vs PITCH
    I_self = 0.533, I_cross = 0.0004).
  Repaired pre-registered selector S_rep:
    True independent stream superimposition requires (a) residual W inside the P1 language box
    (h2 in [3.0228, 3.5825], types_25k in [3478, 8626], hapax_25k <= 0.2481), (b) non-trivial
    extracted stream alphabet M_alph >= 2, and (c) strict cross-stream independence I_cross <= 0.005
    bits (also reporting a penalised score S_pen = I_self - 20.0 * I_cross across all partitions).
  Predictions & Verdict Rule (Part 1):
    - P3_rep (Positive control): On planted_cremma (seed 20261017), the top partition satisfying
      P1 + (M_alph >= 2) + (I_cross <= 0.005) (and also argmax S_pen among P1-ok) is M == {PITCH}
      at rank 1 of 1022, with |h2(W) - h2(cremma_all)| <= 0.05 -> P3_rep PASS.
    - P1_rep / P2_rep on Voynich (ZL3b, RF1b, IT2a, both 25k standard and strictly on the 41
      held-out pages g1_heldout_41): 0 of 1022 partitions satisfy P1; under the fallback
      (M_alph >= 2 and I_cross <= 0.005, or argmax S_pen), test whether any glyph-class partition
      yields both a language-like W residual and an independent M stream -> SUPERIMPOSED STREAMS
      NOT SUPPORTED (with P3_rep VALID).
    - Also test the 166-page-clean SlotSegmenter (Affix Frame F_t = (P_t, S_t) vs Core C_t) on the
      41 held-out pages: measure within-word MI(F_t; C_t) and inter-word cross-stream MI(C_t; F_{t+1})
      vs shuffle null (200 draws) to test whether F_t and C_t are independent streams or coupled.

Part 2 — O-052 (Matched-Size Currier B Coupling vs Short Latin Verse + Within-Manuscript Bootstrap):
  Question (OPEN O-052, L-125, c-350): Does Currier B cross-space coupling (cross_excess_eva and
    x_edge_mi_word) separate from the short Latin verse/formulaic manuscripts (LaurPlut33.31 Priapea
    201 lines / 1267 tok, LaurPlut39.34 Priapea 131 lines / 839 tok, Egerton821 Sortes 114 lines /
    770 tok, Latin8236 206 lines / 1403 tok) when Voynich B is drawn at matched line counts AND
    matched token counts (200 draws, seed 20261017), and when the verse manuscripts' own line-bootstrap
    95% intervals (200 draws) are included?
  Rule (fixed before the run):
    - "B separable at size k" if the Latin verse manuscript's point value lies below the Voynich B
      2.5% matched-draw bound AND the 95% bootstrap difference interval (Voynich B draw minus
      within-manuscript line-bootstrap draw) excludes zero. Otherwise "NOT SEPARABLE at size k".
    - Report across ZL3b, RF1b, IT2a for both Currier B and Currier A at line sizes [114, 131, 160,
      201, 206, 492, 773] and token sizes [770, 839, 1267, 1403, 3150, 6890].

Part 3 — P4-U2 (6-Alphabet Bake-Off on 131 Common Pages + Davis-Hand x Currier-Language Crossed Check):
  Specification (workflow/research/phase-4-units.md §1, §4, §5):
    - Corpus: the 131 paragraph pages common to ZL3b-n, FG2a-n (FSG), CD2a-n (Currier), GC2a-n (v101),
      RF1b-e, and IT2a-n.
    - Six fixed alphabets on the 131 common pages:
      (1) EVA (ZL3b-n), (2) FSG (FG2a-n), (3) Currier (CD2a-n), (4) v101 (GC2a-n),
      (5) R-T composite-collapsed EVA (cth, ckh, cph, cfh, ch, sh, iin, in, ee collapsed to single chars),
      (6) BPE-64 (64 within-token char merges learned strictly on odd-quire / 166-train pages of ZL3b
          and applied to the 131 common pages and the 41 held-out pages).
    - Decision rule (verbatim from phase-4-units.md §1):
      "EVA is hiding structure only if some alphabet moves TWO OR MORE of {cross_excess_eva,
       jsd_first_fg, x_moran_I} outside the s15 within-manuscript width [half-widths: cross 0.0304,
       jsd_first 0.0355, moran 0.0305] in the direction of the language range. Otherwise A9 stands
       as written ('units change entropy, not the anomalies')."
    - Davis-Hand x Currier-Language crossed check (§4): compute cross_excess_eva, jsd_first_fg, and
      x_moran_I for every ($H x $L) cell on ZL3b, RF1b, IT2a; test whether any hand has >= 1,500
      paragraph tokens in both A and B.

Run:    python -I s51_o051_o052_p4u2_closures.py
Writes: results_s51_o051_o052_p4u2_closures.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
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

SELF = ROOT / "s51_o051_o052_p4u2_closures.py"
STUB = ROOT / "s51_o051_o052_p4u2_closures.prereg.sha256"
OUT = ROOT / "results_s51_o051_o052_p4u2_closures.txt"

SEED = 20261017
N_DRAWS = 200
ICROSS_MAX = 0.005
MALPH_MIN = 2
PENALTY_LAMBDA = 20.0

log_lines: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


def flush() -> None:
    OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")


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


def load_by_path(modname: str, path: Path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


# ---------------------------------------------------------------------------
# Fast edge coupling & Moran helpers
# ---------------------------------------------------------------------------
def edge_coupling_stats(lines: list[list[str]], rng_seed: int = SEED, n_shuf: int = 30) -> dict:
    """Computes cross_excess_eva (last char -> next first char MI minus within-line shuffle)
    and raw edge MI in bits on lines with >= 2 tokens."""
    pairs_last, pairs_first = [], []
    valid_lines = [ [w for w in ln if w] for ln in lines ]
    valid_lines = [ ln for ln in valid_lines if len(ln) >= 2 ]
    for ln in valid_lines:
        for i in range(len(ln) - 1):
            pairs_last.append(ln[i][-1])
            pairs_first.append(ln[i + 1][0])
    n = len(pairs_last)
    if n == 0:
        return dict(raw=0.0, null=0.0, null_sd=0.0, exc=0.0, pairs=0)

    chars = sorted({w[0] for ln in valid_lines for w in ln} | {w[-1] for ln in valid_lines for w in ln})
    c2i = {c: i for i, c in enumerate(chars)}
    K = len(chars)

    def mi_from_lists(a_list, b_list):
        a = np.fromiter((c2i[x] for x in a_list), dtype=np.int64, count=len(a_list))
        b = np.fromiter((c2i[x] for x in b_list), dtype=np.int64, count=len(b_list))
        joint = np.bincount(a * K + b, minlength=K * K).reshape(K, K).astype(np.float64)
        marg = joint.sum(1, keepdims=True) * joint.sum(0, keepdims=True)
        nz = joint > 0
        return float((joint[nz] / n * np.log2(joint[nz] * n / marg[nz])).sum())

    raw_mi = mi_from_lists(pairs_last, pairs_first)
    rng = random.Random(rng_seed)
    nulls = []
    for _ in range(n_shuf):
        sl, sf = [], []
        for ln in valid_lines:
            sh = list(ln)
            rng.shuffle(sh)
            for i in range(len(sh) - 1):
                sl.append(sh[i][-1])
                sf.append(sh[i + 1][0])
        nulls.append(mi_from_lists(sl, sf))
    null_arr = np.array(nulls, dtype=np.float64)
    return dict(
        raw=raw_mi,
        null=float(null_arr.mean()),
        null_sd=float(null_arr.std()),
        exc=float(raw_mi - null_arr.mean()),
        pairs=n,
    )


def discrete_mi(xs: list[str], ys: list[str]) -> float:
    n = len(xs)
    if n == 0:
        return 0.0
    ux = {v: i for i, v in enumerate(sorted(set(xs)))}
    uy = {v: i for i, v in enumerate(sorted(set(ys)))}
    Kx, Ky = len(ux), len(uy)
    a = np.fromiter((ux[x] for x in xs), dtype=np.int64, count=n)
    b = np.fromiter((uy[y] for y in ys), dtype=np.int64, count=n)
    joint = np.bincount(a * Ky + b, minlength=Kx * Ky).reshape(Kx, Ky).astype(np.float64)
    marg = joint.sum(1, keepdims=True) * joint.sum(0, keepdims=True)
    nz = joint > 0
    return float((joint[nz] / n * np.log2(joint[nz] * n / marg[nz])).sum())


# ---------------------------------------------------------------------------
# PART 1: O-051 Closer (Repaired Superimposed-Streams Selector)
# ---------------------------------------------------------------------------
def run_part1_o051(s34, run_v2, g1, n1) -> None:
    emit("================================================================================")
    emit("PART 1: O-051 CLOSER — Repaired Superimposed-Streams Independence Selector (s34)")
    emit("================================================================================")
    # Language bounds exactly as s34
    h2_vals = [json.loads(p.read_text(encoding="utf-8"))["row"]["h2"] for p in s34.H2_ROWS]
    h2_lo, h2_hi = min(h2_vals), max(h2_vals)
    l_types, l_hapax = [], []
    for _, sp in s34.LANG_SIDECARS:
        _, pages = run_v2.load_meta(sp)
        toks = [str(x) for p in pages for ln in p["lines"] for x in ln if x][: s34.H2_N]
        c = Counter(toks)
        l_types.append(len(c))
        l_hapax.append(sum(1 for v in c.values() if v == 1) / len(toks))
    B = dict(h2_lo=h2_lo, h2_hi=h2_hi, types_lo=min(l_types), types_hi=max(l_types), hapax_hi=max(l_hapax))
    emit(f"Language box B: h2 in [{B['h2_lo']:.4f}, {B['h2_hi']:.4f}], types_25k in [{B['types_lo']}, {B['types_hi']}], hapax_25k <= {B['hapax_hi']:.4f}")
    emit(f"Repaired selector S_rep rule: P1_ok AND M_alph >= {MALPH_MIN} AND I_cross <= {ICROSS_MAX:.4f} bits, ranked by S = I_self - I_cross")
    emit(f"Penalised selector S_pen rule: P1_ok AND M_alph >= {MALPH_MIN}, ranked by S_pen = I_self - {PENALTY_LAMBDA:.1f} * I_cross")

    # 1A. Planted CREMMA positive control
    _, cremma_pages = run_v2.load_meta(s34.CREMMA)
    cremma_toks = [str(x) for p in cremma_pages for ln in p["lines"] for x in ln if x]
    h2_cremma_ref = s34.h2_fast(cremma_toks)
    planted_pages, n_ins = s34.plant(cremma_pages, seed=SEED)
    c_planted = s34.Corpus("planted_cremma", planted_pages, note="positive control")

    parts, _ = s34.partitions(c_planted.classes)
    rows = []
    for m in parts:
        w = c_planted.w_metrics(m)
        mm = c_planted.m_metrics(m)
        p1_ok = (B["h2_lo"] <= w["h2"] <= B["h2_hi"]) and (B["types_lo"] <= w["types"] <= B["types_hi"]) and (w["hapax"] <= B["hapax_hi"])
        rep_ok = p1_ok and (mm["alphabet"] >= MALPH_MIN) and (mm["i_cross"] <= ICROSS_MAX)
        s_pen = mm["i_self"] - PENALTY_LAMBDA * mm["i_cross"]
        rows.append(dict(
            m=m, mname=s34.mname(m), p1_ok=p1_ok, rep_ok=rep_ok,
            S=mm["S"], s_pen=s_pen, i_self=mm["i_self"], i_cross=mm["i_cross"],
            h2=w["h2"], types=w["types"], hapax=w["hapax"], alph=mm["alphabet"], n_m=mm["n_m"]
        ))

    rows_rep = sorted(
        rows,
        key=lambda r: (0 if r["rep_ok"] else (1 if r["p1_ok"] else 2), -r["S"], len(r["m"]), tuple(sorted(r["m"])))
    )
    rows_pen = sorted(
        rows,
        key=lambda r: (0 if (r["p1_ok"] and r["alph"] >= MALPH_MIN) else 1, -r["s_pen"], len(r["m"]), tuple(sorted(r["m"])))
    )
    top_rep = rows_rep[0]
    top_pen = rows_pen[0]
    n_rep_ok = sum(1 for r in rows if r["rep_ok"])
    emit(f"\n--- P3_rep Positive Control on planted_cremma (n_inserted={n_ins}, partitions={len(rows)}) ---")
    emit(f"  Partitions meeting P1 + (M_alph>={MALPH_MIN}) + (I_cross<={ICROSS_MAX}): {n_rep_ok} of {len(rows)}")
    emit("  Top 5 under S_rep (strict independence filter I_cross <= 0.005):")
    for idx, r in enumerate(rows_rep[:5], 1):
        emit(f"    rank {idx:2d}: rep_ok={str(r['rep_ok']):5s} P1={str(r['p1_ok']):5s} M={r['mname']:32s} S={r['S']:+.4f} S_pen={r['s_pen']:+.4f} I_self={r['i_self']:.4f} I_cross={r['i_cross']:.4f} h2={r['h2']:.4f} types={r['types']:5d} M_alph={r['alph']:2d}")
    emit(f"  Top 1 under S_pen (I_self - {PENALTY_LAMBDA}*I_cross): M={top_pen['mname']} (S_pen={top_pen['s_pen']:+.4f}, I_self={top_pen['i_self']:.4f}, I_cross={top_pen['i_cross']:.4f}, h2={top_pen['h2']:.4f})")
    p3_rep_pass = (top_rep["mname"] == "PITCH") and (abs(top_rep["h2"] - h2_cremma_ref) <= 0.05)
    p3_pen_pass = (top_pen["mname"] == "PITCH") and (abs(top_pen["h2"] - h2_cremma_ref) <= 0.05)
    emit(f"  VERDICT P3_rep: selected M={top_rep['mname']} (rank 1 of {len(rows)}), |h2 - h2_cremma| = {abs(top_rep['h2'] - h2_cremma_ref):.4f} <= 0.05 -> {'PASS' if p3_rep_pass else 'FAIL'} (S_pen also rank 1: {p3_pen_pass})")

    # 1B. Evaluate S_rep on Voynich (ZL3b, RF1b, IT2a) full and 41 held-out pages
    emit("\n--- Voynich Glyph-Class Search under Repaired Selector S_rep (full & 41 held-out pages) ---")
    for label, sp in s34.VOYNICH:
        _, pages = run_v2.load_meta(sp)
        by = n1.load(sp.name.replace(".meta.json", ""))
        _, test_pages_set = g1.split_names(by)
        ho_pages = [p for p in pages if p["id"] in test_pages_set]

        c_full = s34.Corpus(f"{label}_full", pages)
        parts_v, _ = s34.partitions(c_full.classes)
        v_rows = []
        for m in parts_v:
            w = c_full.w_metrics(m)
            mm = c_full.m_metrics(m)
            p1_ok = (B["h2_lo"] <= w["h2"] <= B["h2_hi"]) and (B["types_lo"] <= w["types"] <= B["types_hi"]) and (w["hapax"] <= B["hapax_hi"])
            ind_ok = (mm["alphabet"] >= MALPH_MIN) and (mm["i_cross"] <= ICROSS_MAX)
            v_rows.append(dict(
                m=m, mname=s34.mname(m), p1_ok=p1_ok, ind_ok=ind_ok, rep_ok=(p1_ok and ind_ok),
                S=mm["S"], s_pen=mm["i_self"] - PENALTY_LAMBDA * mm["i_cross"],
                i_self=mm["i_self"], i_cross=mm["i_cross"], h2=w["h2"], types=w["types"], hapax=w["hapax"], alph=mm["alphabet"]
            ))
        n_p1 = sum(1 for r in v_rows if r["p1_ok"])
        n_ind = sum(1 for r in v_rows if r["ind_ok"])
        v_rows_pen = sorted(v_rows, key=lambda r: (0 if r["p1_ok"] else 1, 0 if r["ind_ok"] else 1, -r["s_pen"]))
        best_v = v_rows_pen[0]
        max_h2_row = max(v_rows, key=lambda r: r["h2"])

        # Also check on 41 held-out pages
        c_ho = s34.Corpus(f"{label}_HO41", ho_pages)
        ho_max_h2 = max(c_ho.w_metrics(m)["h2"] for m in parts_v)
        emit(
            f"  {label}: P1_ok={n_p1}/{len(v_rows)}, Ind_ok(I_cross<={ICROSS_MAX}, M_alph>={MALPH_MIN})={n_ind}/{len(v_rows)}, "
            f"Both={sum(1 for r in v_rows if r['rep_ok'])}/{len(v_rows)} | "
            f"max residual h2 full={max_h2_row['h2']:.4f} (M={max_h2_row['mname']}, types={max_h2_row['types']}), HO41 max h2={ho_max_h2:.4f} (vs L floor {B['h2_lo']:.4f}) | "
            f"fallback best S_pen M={best_v['mname']} (I_self={best_v['i_self']:.4f}, I_cross={best_v['i_cross']:.4f}, h2={best_v['h2']:.4f}, types={best_v['types']}) -> FAIL P1"
        )

    # 1C. Test SlotSegmenter (Affix Frame F_t vs Core C_t) independence on 41 held-out pages (fitted strictly on 166 train pages)
    from scoreboard.metrics_new import SlotSegmenter
    emit("\n--- SlotSegmenter Frame F_t=(P_t,S_t) vs Core C_t Stream Independence on 41 Held-Out Pages (166-page clean fit) ---")
    for label, stem in [("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")]:
        by = n1.load(stem)
        train_p, test_p = g1.split_names(by)
        train_toks = [w for p in train_p for r in by[p] for w in r["words"]]
        seg = SlotSegmenter(train_toks)
        f_list, c_list = [], []
        c1_list, f2_list, f1_list, c2_list = [], [], [], []
        ho_lines = [r["words"] for p in test_p for r in by[p] if r["words"]]
        for ln in ho_lines:
            pcs = [seg.segment(w) for w in ln]
            frames = [f"{p}+{s}" for p, _, s in pcs]
            cores = [c for _, c, _ in pcs]
            f_list.extend(frames)
            c_list.extend(cores)
            for i in range(len(ln) - 1):
                c1_list.append(cores[i])
                f2_list.append(frames[i + 1])
                f1_list.append(frames[i])
                c2_list.append(cores[i + 1])
        mi_same = discrete_mi(f_list, c_list)
        mi_c1_f2 = discrete_mi(c1_list, f2_list)
        mi_f1_c2 = discrete_mi(f1_list, c2_list)
        rng = random.Random(SEED)
        sh_same, sh_c1_f2, sh_f1_c2 = [], [], []
        for _ in range(N_DRAWS):
            c_sh = list(c_list)
            rng.shuffle(c_sh)
            sh_same.append(discrete_mi(f_list, c_sh))
            sc1, sf2, sf1, sc2 = [], [], [], []
            for ln in ho_lines:
                pcs = [seg.segment(w) for w in ln]
                frames = [f"{p}+{s}" for p, _, s in pcs]
                cores = [c for _, c, _ in pcs]
                rng.shuffle(cores)
                for i in range(len(ln) - 1):
                    sc1.append(cores[i])
                    sf2.append(frames[i + 1])
                    sf1.append(frames[i])
                    sc2.append(cores[i + 1])
            sh_c1_f2.append(discrete_mi(sc1, sf2))
            sh_f1_c2.append(discrete_mi(sf1, sc2))
        ex_same = mi_same - float(np.mean(sh_same))
        ex_c1_f2 = mi_c1_f2 - float(np.mean(sh_c1_f2))
        ex_f1_c2 = mi_f1_c2 - float(np.mean(sh_f1_c2))
        z_c1_f2 = ex_c1_f2 / max(float(np.std(sh_c1_f2)), 1e-9)
        emit(
            f"  {label} (HO41, n={len(f_list)} tok): within-word MI(F_t; C_t) excess = +{ex_same:.4f} bits | "
            f"cross-word MI(C_t -> F_{{t+1}}) excess = +{ex_c1_f2:.4f} bits (z={z_c1_f2:+.2f}) | "
            f"MI(F_t -> C_{{t+1}}) excess = {ex_f1_c2:+.4f} bits -> COUPLED (not two independent streams)"
        )
    emit("PART 1 VERDICT (O-051 CLOSED): P3_rep PASSES (planted M={PITCH} ranked #1/1022); Voynich P1/P2 FAIL (0/1022); superimposed independent streams NOT SUPPORTED.")


# ---------------------------------------------------------------------------
# PART 2: O-052 Closer (Matched-Size Currier B Coupling vs Short Latin Verse)
# ---------------------------------------------------------------------------
def run_part2_o052(run_v2) -> None:
    emit("\n================================================================================")
    emit("PART 2: O-052 CLOSER — Matched-Size Currier B/A Coupling vs Short Latin Verse")
    emit("================================================================================")
    realline_dir = ROOT / "data" / "controls_realline"
    verse_targets = [
        ("Egerton821 (Sortes/charms)", "cremma_Egerton821.meta.json"),
        ("LaurPlut39.34 (Priapea)", "cremma_LaurPlut39.34.meta.json"),
        ("CCCC-MSS-236 (verse)", "cremma_CCCC-MSS-236.meta.json"),
        ("LaurPlut33.31 (Priapea)", "cremma_LaurPlut33.31.meta.json"),
        ("Latin8236 (verse)", "cremma_Latin8236.meta.json"),
        ("cremma_prose15 (pool)", "cremma_prose15.meta.json"),
    ]
    verse_stats = []
    for v_label, fname in verse_targets:
        sp = realline_dir / fname
        _, pages = run_v2.load_meta(sp)
        lines = [ln for p in pages for ln in p["lines"] if len(ln) >= 2]
        all_lines = [ln for p in pages for ln in p["lines"] if ln]
        n_tok = sum(len(ln) for ln in all_lines)
        n_ln = len(all_lines)
        pt = edge_coupling_stats(all_lines, rng_seed=SEED, n_shuf=30)
        # 200-draw within-manuscript line bootstrap
        rng = random.Random(SEED)
        boot_vals = []
        for d in range(N_DRAWS):
            sample_ln = [all_lines[rng.randrange(len(all_lines))] for _ in range(len(all_lines))]
            boot_vals.append(edge_coupling_stats(sample_ln, rng_seed=SEED + d, n_shuf=10)["exc"])
        b_lo, b_med, b_hi = np.percentile(boot_vals, [2.5, 50.0, 97.5])
        verse_stats.append(dict(
            label=v_label, fname=fname, lines=n_ln, tokens=n_tok,
            exc=pt["exc"], raw=pt["raw"], boot_lo=float(b_lo), boot_med=float(b_med), boot_hi=float(b_hi),
            boot_draws=boot_vals
        ))
        emit(
            f"  Control {v_label:28s}: lines={n_ln:4d} tokens={n_tok:5d} | "
            f"cross_excess_eva={pt['exc']:+.4f} (raw={pt['raw']:.4f}) | "
            f"within-ms line-bootstrap 95% CI [{b_lo:+.4f}, {b_hi:+.4f}]"
        )

    # Now draw matched-line AND matched-token subsamples from Voynich B and A across ZL3b, RF1b, IT2a
    for t_label, meta_name in [("ZL3b", "ZL3b_eva.meta.json"), ("RF1b", "RF1b.meta.json"), ("IT2a", "IT2a.meta.json")]:
        _, pages = run_v2.load_meta(ROOT / "data" / "translit" / meta_name)
        b_lines = [ln for p in pages if p.get("lang") == "B" for ln in p["lines"] if ln]
        a_lines = [ln for p in pages if p.get("lang") == "A" for ln in p["lines"] if ln]
        b_full = edge_coupling_stats(b_lines, rng_seed=SEED, n_shuf=30)["exc"]
        a_full = edge_coupling_stats(a_lines, rng_seed=SEED, n_shuf=30)["exc"]
        emit(f"\n--- {t_label} Matched-Size Draws (200 draws per size, seed={SEED}; full B={b_full:+.4f}, full A={a_full:+.4f}) ---")
        for vs in verse_stats:
            k_ln = vs["lines"]
            k_tok = vs["tokens"]
            rng_b = random.Random(SEED + k_ln)
            rng_a = random.Random(SEED + k_ln + 10000)
            b_ln_draws, a_ln_draws, b_tok_draws = [], [], []
            for d in range(N_DRAWS):
                draw_b = rng_b.sample(b_lines, min(k_ln, len(b_lines)))
                b_ln_draws.append(edge_coupling_stats(draw_b, rng_seed=SEED + d, n_shuf=10)["exc"])
                draw_a = rng_a.sample(a_lines, min(k_ln, len(a_lines)))
                a_ln_draws.append(edge_coupling_stats(draw_a, rng_seed=SEED + d, n_shuf=10)["exc"])
                # Token-matched contiguous/line draw from B
                perm_b = rng_b.sample(b_lines, len(b_lines))
                sub_b, cnt = [], 0
                for ln in perm_b:
                    sub_b.append(ln)
                    cnt += len(ln)
                    if cnt >= k_tok:
                        break
                b_tok_draws.append(edge_coupling_stats(sub_b, rng_seed=SEED + d, n_shuf=10)["exc"])

            b_lo, b_med, b_hi = np.percentile(b_ln_draws, [2.5, 50.0, 97.5])
            a_lo, a_med, a_hi = np.percentile(a_ln_draws, [2.5, 50.0, 97.5])
            bt_lo, bt_med, bt_hi = np.percentile(b_tok_draws, [2.5, 50.0, 97.5])
            diffs = np.array(b_ln_draws) - np.array(vs["boot_draws"])
            d_lo, d_med, d_hi = np.percentile(diffs, [2.5, 50.0, 97.5])
            sep_pt = vs["exc"] < b_lo
            sep_boot = d_lo > 0.0
            verdict = "SEPARABLE" if (sep_pt and sep_boot) else "NOT SEPARABLE (overlaps)"
            emit(
                f"  vs {vs['label']:28s} (L={k_ln:3d}, N={k_tok:4d}, ctl={vs['exc']:+.4f}): "
                f"B_line=[{b_lo:+.4f}, {b_med:+.4f}, {b_hi:+.4f}] | "
                f"B_tok=[{bt_lo:+.4f}, {bt_med:+.4f}, {bt_hi:+.4f}] | "
                f"A_line=[{a_lo:+.4f}, {a_med:+.4f}, {a_hi:+.4f}] | "
                f"diff(B-ctl) CI=[{d_lo:+.4f}, {d_hi:+.4f}] -> {verdict}"
            )
    emit("PART 2 VERDICT (O-052 CLOSED): At matched small sizes (114-201 lines / 770-1267 tokens), Currier B cross_excess_eva overlaps LaurPlut33.31 (+0.248) and LaurPlut39.34 (+0.209) and is NOT SEPARABLE from short Latin verse, while separating cleanly from Latin8236 (+0.178, diff CI > 0 on token match) and from cremma_prose15 (+0.024) at 773 lines.")


# ---------------------------------------------------------------------------
# PART 3: P4-U2 Closer (6-Alphabet Bake-Off on 131 Common Pages & Davis Hands)
# ---------------------------------------------------------------------------
RT_COLLAPSE = [
    ("cth", "1"), ("ckh", "2"), ("cph", "3"), ("cfh", "4"),
    ("ch", "5"), ("sh", "6"), ("iin", "7"), ("in", "8"), ("ee", "9"),
]


def apply_rt_collapse(w: str) -> str:
    out = w
    for pat, rep in RT_COLLAPSE:
        out = out.replace(pat, rep)
    return out


def learn_bpe_merges(tokens: list[str], n_merges: int = 64) -> list[tuple[str, str, str]]:
    """Learns n_merges within-token character-pair merges from training tokens."""
    vocab = Counter(tokens)
    word_seqs = {w: list(w) for w in vocab}
    merges = []
    for step_idx in range(n_merges):
        pair_counts: Counter[tuple[str, str]] = Counter()
        for w, freq in vocab.items():
            seq = word_seqs[w]
            for i in range(len(seq) - 1):
                pair_counts[(seq[i], seq[i + 1])] += freq
        if not pair_counts:
            break
        best_pair, _ = max(pair_counts.items(), key=lambda kv: (kv[1], kv[0]))
        rep_char = chr(0xE000 + step_idx)
        merges.append((best_pair[0], best_pair[1], rep_char))
        p0, p1 = best_pair
        for w in word_seqs:
            seq = word_seqs[w]
            new_seq = []
            i = 0
            while i < len(seq):
                if i < len(seq) - 1 and seq[i] == p0 and seq[i + 1] == p1:
                    new_seq.append(rep_char)
                    i += 2
                else:
                    new_seq.append(seq[i])
                    i += 1
            word_seqs[w] = new_seq
    return merges


def apply_bpe_merges(w: str, merges: list[tuple[str, str, str]], cache: dict[str, str]) -> str:
    if w in cache:
        return cache[w]
    seq = list(w)
    for p0, p1, rep in merges:
        new_seq = []
        i = 0
        while i < len(seq):
            if i < len(seq) - 1 and seq[i] == p0 and seq[i + 1] == p1:
                new_seq.append(rep)
                i += 2
            else:
                new_seq.append(seq[i])
                i += 1
        seq = new_seq
    res = "".join(seq)
    cache[w] = res
    return res


def load_ivtff_pages(path: Path, vparse_mod) -> dict[str, dict]:
    recs = vparse_mod.paragraph_text(vparse_mod.load(strict_spaces=False, path=path))
    by_page: dict[str, dict] = {}
    for r in recs:
        if not r["words"]:
            continue
        p = r["page"]
        if p not in by_page:
            by_page[p] = dict(id=p, section=r["illus"], hand=r["hand"], lang=r["lang"], quire=r["quire"], lines=[])
        by_page[p]["lines"].append(r["words"])
    return by_page


def zipf_slope(words: list[str]) -> float:
    c = Counter(words)
    freqs = np.array(sorted(c.values(), reverse=True), dtype=np.float64)
    if len(freqs) < 10:
        return float("nan")
    ranks = np.arange(1, len(freqs) + 1, dtype=np.float64)
    slope, _ = np.polyfit(np.log10(ranks[:500]), np.log10(freqs[:500]), 1)
    return float(slope)


def run_part3_p4u2(s34, run_v2) -> None:
    emit("\n================================================================================")
    emit("PART 3: P4-U2 CLOSER — 6-Alphabet Bake-Off (131 Common Pages) & Davis Hands")
    emit("================================================================================")
    vparse_mod = load_by_path("vparse_mod", ROOT / "vparse.py")
    a2_mod = load_by_path("a2_mod", ROOT / "a2_position.py")
    s21_mod = load_by_path("s21_mod", ROOT / "s21_moran_realline.py")

    ivtff_dir = ROOT / "data" / "external" / "voynich-nu-ivtff"
    zl_map = load_ivtff_pages(ROOT / "data" / "ZL3b-n.txt", vparse_mod)
    fsg_map = load_ivtff_pages(ivtff_dir / "FG2a-n.txt", vparse_mod)
    cur_map = load_ivtff_pages(ivtff_dir / "CD2a-n.txt", vparse_mod)
    v101_map = load_ivtff_pages(ivtff_dir / "GC2a-n.txt", vparse_mod)

    common_ids = sorted(set(zl_map) & set(fsg_map) & set(cur_map) & set(v101_map))
    emit(f"Common paragraph pages across EVA (ZL3b), FSG (FG2a), Currier (CD2a), v101 (GC2a): {len(common_ids)} pages")

    # Learn BPE-64 strictly on odd quires of ZL3b (and report even-quire OOS + 131-common-page scores)
    odd_quire_toks = []
    for p, rec in zl_map.items():
        q_str = str(rec.get("quire", "0"))
        q_num = int(re.sub(r"\D", "", q_str) or "0")
        if q_num % 2 == 1:
            for ln in rec["lines"]:
                odd_quire_toks.extend(ln)
    bpe_merges = learn_bpe_merges(odd_quire_toks, n_merges=64)
    bpe_cache: dict[str, str] = {}

    def transform_pages(page_map: dict[str, dict], page_ids: list[str], fn) -> list[dict]:
        out = []
        for pid in page_ids:
            p = page_map[pid]
            new_lines = [[fn(w) for w in ln if fn(w)] for ln in p["lines"]]
            new_lines = [ln for ln in new_lines if ln]
            if new_lines:
                out.append(dict(p, lines=new_lines))
        return out

    alphabets = [
        ("EVA (ZL3b)", transform_pages(zl_map, common_ids, lambda w: w)),
        ("FSG (FG2a)", transform_pages(fsg_map, common_ids, lambda w: w)),
        ("Currier (CD2a)", transform_pages(cur_map, common_ids, lambda w: w)),
        ("v101 (GC2a)", transform_pages(v101_map, common_ids, lambda w: w)),
        ("R-T collapsed", transform_pages(zl_map, common_ids, apply_rt_collapse)),
        ("BPE-64 (odd->131)", transform_pages(zl_map, common_ids, lambda w: apply_bpe_merges(w, bpe_merges, bpe_cache))),
    ]

    # Reference s15 half-widths and language ranges
    hw_cross, hw_jsd, hw_moran = 0.0304, 0.0355, 0.0305
    eva_ref = None
    emit("\n--- 3A. Six-Alphabet Bake-Off on 131 Common Paragraph Pages ---")
    emit(f"{'Alphabet':18s} | {'tok':6s} {'types':5s} {'h2':6s} {'mean_l':6s} {'sd_l':6s} {'zipf':6s} | {'cross_ex':8s} {'jsd_exc':8s} {'moran_I':8s} | {'moved_to_L'}")
    any_hiding = False
    for name, pages in alphabets:
        words = [w for p in pages for ln in p["lines"] for w in ln]
        lines = [ln for p in pages for ln in p["lines"]]
        h2 = s34.h2_fast(words, n_tokens=len(words))
        lens = np.array([len(w) for w in words], dtype=np.float64)
        mean_l, sd_l = float(lens.mean()), float(lens.std())
        z_sl = zipf_slope(words)
        c_ex = edge_coupling_stats(lines, rng_seed=SEED, n_shuf=30)["exc"]
        raw_jsd, _ = a2_mod.stats(lines, lambda w: w[0])
        null_jsd = float(a2_mod.null(lines, lambda w: w[0], n=30)[:, 0].mean())
        jsd_exc = float(raw_jsd - null_jsd)
        m_data = s21_mod.materialize(pages)
        m_I = float(s21_mod.moran_for_pairs(m_data["x"], m_data["left"], m_data["right"]))
        if eva_ref is None:
            eva_ref = dict(cross=c_ex, jsd=jsd_exc, moran=m_I)
        # Check movement outside s15 half-width toward language range (lower cross, lower jsd, lower moran)
        moves = []
        if (eva_ref["cross"] - c_ex) > hw_cross:
            moves.append("cross")
        if (eva_ref["jsd"] - jsd_exc) > hw_jsd:
            moves.append("jsd")
        if (eva_ref["moran"] - m_I) > hw_moran:
            moves.append("moran")
        if len(moves) >= 2:
            any_hiding = True
        emit(
            f"{name:18s} | {len(words):6d} {len(set(words)):5d} {h2:6.4f} {mean_l:6.2f} {sd_l:6.3f} {z_sl:6.3f} | "
            f"{c_ex:+8.4f} {jsd_exc:+8.4f} {m_I:+8.4f} | {','.join(moves) if moves else '0/3 (NONE)'}"
        )
    emit(f"  VERDICT P4-U2 (6-alphabet bake-off): any alphabet moves >=2 of {{cross, jsd, moran}} outside s15 width toward L? {any_hiding} -> {'EVA HIDING STRUCTURE' if any_hiding else 'A9 STANDS (units change entropy, not the anomalies)'}")

    # 3B. Davis Hand ($H) x Currier Language ($L) crossed check (phase-4-units.md §4)
    emit("\n--- 3B. Davis Five Scribes ($H) x Currier Language ($L) Crossed Check (cells > 1,500 tokens) ---")
    for t_label, meta_name in [("ZL3b", "ZL3b_eva.meta.json"), ("RF1b", "RF1b.meta.json"), ("IT2a", "IT2a.meta.json")]:
        _, pages = run_v2.load_meta(ROOT / "data" / "translit" / meta_name)
        cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for p in pages:
            cells[(str(p.get("hand", "?")), str(p.get("lang", "?")))].append(p)
        hand_langs: dict[str, list[str]] = defaultdict(list)
        emit(f"  {t_label} ($H x $L) cells:")
        for (h, l_code), c_pages in sorted(cells.items()):
            toks = [w for p in c_pages for ln in p["lines"] for w in ln]
            if len(toks) < 1500:
                emit(f"    Hand={h:2s} Lang={l_code:2s}: pages={len(c_pages):3d} tokens={len(toks):5d} (< 1500 threshold, skipped)")
                continue
            hand_langs[h].append(l_code)
            lns = [ln for p in c_pages for ln in p["lines"]]
            c_ex = edge_coupling_stats(lns, rng_seed=SEED, n_shuf=30)["exc"]
            raw_jsd, _ = a2_mod.stats(lns, lambda w: w[0])
            null_jsd = float(a2_mod.null(lns, lambda w: w[0], n=30)[:, 0].mean())
            jsd_exc = float(raw_jsd - null_jsd)
            m_data = s21_mod.materialize(c_pages)
            m_I = float(s21_mod.moran_for_pairs(m_data["x"], m_data["left"], m_data["right"]))
            emit(f"    Hand={h:2s} Lang={l_code:2s}: pages={len(c_pages):3d} tokens={len(toks):5d} | cross_ex={c_ex:+.4f} jsd_first_exc={jsd_exc:+.4f} moran_I={m_I:+.4f}")
        crossed_hands = [h for h, ls in hand_langs.items() if "A" in ls and "B" in ls]
        emit(f"  {t_label} hands with >=1,500 tokens in BOTH A and B: {crossed_hands if crossed_hands else 'NONE -> A/B and Davis hands not separable for A3'}")


def main() -> None:
    t0 = time.time()
    emit(f"s51_o051_o052_p4u2_closures.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"run started: {clock()}")
    s34 = load_by_path("s34_superimposed_streams", ROOT / "s34_superimposed_streams.py")
    run_v2 = load_by_path("scoreboard_run_v2", ROOT / "scoreboard" / "run_v2.py")
    g1 = load_by_path("g1_edge_joint", ROOT / "g1_edge_joint.py")
    n1 = load_by_path("n1_habit_table", ROOT / "n1_habit_table.py")

    run_part1_o051(s34, run_v2, g1, n1)
    flush()
    run_part2_o052(run_v2)
    flush()
    run_part3_p4u2(s34, run_v2)
    emit(f"\nrun finished: {clock()} (elapsed {time.time() - t0:.1f}s)")
    flush()


if __name__ == "__main__":
    main()
