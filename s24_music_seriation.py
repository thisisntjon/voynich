#!/usr/bin/env python
"""
S24: bounded musical / hybrid-notation check (workflow/PLAN.md Phase 3 "s24 approval";
workflow/research/phase-3.md section 5).

PRE-REGISTRATION (frozen in s24_music_seriation.prereg.sha256 BEFORE the first run).

Approval (Jon, 2026-10-17 20:20 PDT, verbatim in PLAN.md): "Jon approves the bounded musical/hybrid
notation check at s24 after current Phase 1, using fixed predictions and matched randomized/nonmusical
controls with the same ordering search. Confirm its resource cap before execution. Don't interrupt the
current job, create another team or expand compute. This approval does not cover other experiments or
key searches."  Cap: one CPU process, no GPU, no paid calls, no new data, expected under 5 min, HARD
STOP at 15 min wall clock (enforced below: a watchdog writes what it has and exits), existing edge
matrices and slot tables only.  No matrix is stored on disk anywhere in the project (phase-3.md s5),
so "existing matrices" means: every table is built at run time from the existing sidecars with the
existing builders' definitions (f3.ratio_table / g1.fit_table / c3.edge_pairs pair convention:
(last char of word a, first char of word b) for adjacent words inside a line; d1.cross_pairs /
within_pairs; metrics_new.SlotSegmenter for the diagnostic slot strip).  Nothing is generated.

Corpora (all existing sidecars, loaded with scoreboard/run_v2.load_meta imported by path):
  Voynich: data/translit/ZL3b_eva, RF1b, IT2a (EVA characters as glyphs; lines as in the sidecar).
  Real-line language tables (s17/s18 sidecars, native lines, data/controls_realline/):
    mhg_nibelungenlied, italian_dante, cremma_all, gib_realline_pooled
    (gib_realline_pooled is human gibberish on the writers' own lines; it is listed with the
    "real-line" set as the approval and the task text name it, and is labelled as gibberish).
  Generator tables (data/controls_synthetic/): c2_best, timm_schinner, schwartz_reuse,
    flow_gen_layer (the "n2 / flow_gen_layer" file; present).

FIXED PREDICTIONS AND PASS/FAIL RULES (verbatim from the task; the only scoring rules)

P1 Seriation.  For the last-glyph -> next-first-glyph transition matrix (within-line pairs; EVA
  glyphs; ZL3b, RF1b, IT2a), find an ordering minimising a bandwidth statistic (MAD of |i-j| weighted
  by transition mass) via spectral (Fiedler) initialisation + 200 fixed 2-opt sweeps; PASS if the
  Voynich bandwidth is below the 1st percentile of BOTH 200 within-line-shuffle nulls (same search)
  and 200 row/column-permutation nulls (same search), AND below every control table under the same
  search: real-line language tables built from the s17/s18 sidecars (mhg_nibelungenlied,
  italian_dante, cremma_all, gib_realline_pooled) and generator tables from existing
  controls_synthetic sidecars (c2_best, timm_schinner, schwartz_reuse, one n2/flow_gen_layer file
  if present).
  Operational definitions (declared here, fixed):
   - T[i, j] = count of within-line adjacent word pairs (a, b) with a[-1] = symbol i and b[0] =
     symbol j; symbol set = union of last-chars and first-chars of that corpus; EVA characters
     (no glyph merging).
   - MAD(pi) = sum_ij T_ij |pi(i) - pi(j)| / sum_ij T_ij  (pi = one permutation applied to both axes;
     self-transitions contribute 0).  Lower = more band-diagonal.
   - Search: S = T + T^T, L = diag(S 1) - S, pi0 = argsort of the Fiedler vector (eigenvector of the
     second-smallest eigenvalue of L; numpy.linalg.eigh).  Then 200 sweeps; one sweep evaluates every
     pairwise position swap exactly (delta[a,b] = SD[a,b] + SD[b,a] - SD[a,a] - SD[b,b] + 2 S_ab D_ab
     with D = |pos_i - pos_j| and SD = S @ D) and applies the single best swap if it lowers MAD;
     a sweep with no improving swap ends the search (the remaining sweeps are no-ops).  Identical
     search, identical sweep budget, for every table (Voynich, nulls, controls).
   - Null (a): 200 within-line token shuffles of each Voynich transliteration (independent uniform
     permutation inside every line; line marginals and the token multiset per line preserved), T
     rebuilt, searched.  Null (b): 200 draws T'[i, j] = T[sigma(i), tau(j)] with sigma, tau
     independent uniform permutations (row and column margins preserved up to relabelling), searched.
     Seed 20261017 (numpy default_rng; one generator per null family per transliteration).
   - "Below the 1st percentile": Voynich MAD < numpy.percentile(null MADs, 1); Monte-Carlo
     p = (1 + #(null <= obs)) / 201 is printed alongside.
   - "Below every control table": Voynich MAD (each transliteration) < min over the 8 control MADs.
   - Diagnostics printed, NOT scored: MAD / (n - 1) (alphabet-size-normalised; cremma_all has ~80
     symbols against ~22 for Voynich, which inflates raw MAD for it), band mass |pi(i)-pi(j)| <= 2,
     the spread of the three Voynich MADs, and the found ordering.
  Reading: a pitch-like notation should put its transition mass near a diagonal under some symbol
  ordering (scale steps); language and the generators should not do so beyond their nulls.

P2 Line-end reset.  The coupling (edge MI excess) across line ends vs within lines; PASS if the
  across/within ratio for Voynich is below the minimum ratio of the four real-line language sidecars
  (on all three transliterations; FAIL otherwise).
  Operational definitions (declared here, fixed):
   - within pairs = d1.cross_pairs convention: (a[-1], b[0]) for adjacent words a, b inside a line.
   - across pairs = (last char of the last word of line n, first char of the first word of line
     n+1) for consecutive non-empty lines of the same page.
   - MI excess = plug-in MI(bits) of the observed pairs minus the mean plug-in MI of 20 permutation
     nulls (second element shuffled; random.Random(20261017) per pair set).
   - ratio = across excess / within excess.  Printed: both excesses, pair counts, ratio.
  Reading: a line of music resets at the bar/line end, so the last->first dependence across the line
  break should be weaker (relative to the within-line one) than in language, which continues
  across lines.

P3 Residual syllable inventory.  Strip the putative pitch slot (test both the first-glyph slot and
  the last-glyph slot, declared in advance) and PASS if the residual core inventory has <= 100 types
  covering >= 90 % of tokens AND its h2 lies inside the real-line language range of h2 from the
  s17/s18 rows (read results_s17_*.json / results_s18_cremma_all.json "row" h2).
  Operational definitions (declared here, fixed):
   - Variant F: residual = token[1:]; variant L: residual = token[:-1].  One-character tokens leave
     an empty residual and are dropped from the residual stream (count reported).
   - "<= 100 types covering >= 90 %": the 100 most frequent residual types together cover >= 90 %
     of the residual tokens (equivalently the inventory needed for 90 % coverage has <= 100 types;
     the exact number needed is printed).
   - h2 of the residual stream = a1_profile.char_entropies convention used by the s17/s18 rows:
     H(char pair) - H(char) on " ".join(words) + " " over the first 25,000 residual tokens
     (run_v2 DEFAULT_N), space included as a symbol.
   - Language h2 range = [min, max] of "row"["h2"] over the native-line language rows
     results_s17_mhg_nibelungenlied.json, results_s17_italian_dante.json,
     results_s17_oldfrench_roland.json, results_s17_occitan_croisade.json and
     results_s18_cremma_all.json (relined8 twins, _marks twins and the gibberish row excluded:
     they are layout/markup contrasts and not language).
   - P3 PASSes on a transliteration if EITHER declared slot variant (F or L) meets both conditions
     (the hypothesis does not fix which edge carries the pitch; both are tested, and the more
     favourable one counts).  FAIL if neither does.
   - Diagnostic, NOT scored: the SlotSegmenter residual (prefix + suffix after stripping the
     induced core; metrics_new.SlotSegmenter defaults) with the same two conditions printed.
  Reading: if one glyph slot carries pitch, what remains should be a small closed syllable/duration
  inventory whose character statistics look like language.

VERDICT RULE (verbatim): "musical/hybrid notation SUPPORTED" only if P1, P2 and P3 all PASS on all
  three transliterations; "NOT SUPPORTED" if any fails on any transliteration.  Each prediction's
  numbers and the control values are printed so the reader sees the margins.

HARD STOP: a watchdog thread at 900 s wall clock writes the lines collected so far plus a STOPPED
  line to results_s24.txt and terminates the process; the main loop also checks the clock between
  units of work and stops with the same line.

Writes ONLY results_s24.txt.  No register, PLAN, data, scoreboard, sidecar or other results file is
touched.  Run: python -I s24_music_seriation.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import threading
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):  # -I ignores PYTHONIOENCODING; the console may be cp1252
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SELF = ROOT / "s24_music_seriation.py"
STUB = ROOT / "s24_music_seriation.prereg.sha256"
OUT = ROOT / "results_s24.txt"
TRANSLIT = ROOT / "data" / "translit"
REALLINE = ROOT / "data" / "controls_realline"
SYNTH = ROOT / "data" / "controls_synthetic"

SEED = 20261017
N_NULL = 200
N_SWEEPS = 200
N_MI_NULL = 20
H2_N = 25000
P3_MAX_TYPES = 100
P3_COVER = 0.90
CAP_EXPECTED_S = 300
CAP_HARD_S = 900

VOYNICH = [("ZL3b", TRANSLIT / "ZL3b_eva.meta.json"),
           ("RF1b", TRANSLIT / "RF1b.meta.json"),
           ("IT2a", TRANSLIT / "IT2a.meta.json")]
LANG_TABLES = [("mhg_nibelungenlied", REALLINE / "mhg_nibelungenlied.meta.json", "MHG verse, native lines"),
               ("italian_dante", REALLINE / "italian_dante.meta.json", "Italian verse, native lines"),
               ("cremma_all", REALLINE / "cremma_all.meta.json", "CREMMA Latin, all, native lines"),
               ("gib_realline_pooled", REALLINE / "gib_realline_pooled.meta.json",
                "human GIBBERISH, writers' own lines (listed with the real-line set as named)")]
GEN_TABLES = [("c2_best", SYNTH / "c2_best.meta.json", "c2 section generator"),
              ("timm_schinner", SYNTH / "timm_schinner.meta.json", "Timm-Schinner self-citation"),
              ("schwartz_reuse", SYNTH / "schwartz_reuse.meta.json", "Schwartz reuse generator"),
              ("flow_gen_layer", SYNTH / "flow_gen_layer.meta.json", "n2 flow generator layer")]
H2_ROWS = [ROOT / "results_s17_mhg_nibelungenlied.json", ROOT / "results_s17_italian_dante.json",
           ROOT / "results_s17_oldfrench_roland.json", ROOT / "results_s17_occitan_croisade.json",
           ROOT / "results_s18_cremma_all.json"]

T0 = time.monotonic()
LINES: list[str] = []
_LOCK = threading.Lock()


def elapsed() -> float:
    return time.monotonic() - T0


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


def emit(s: str = "") -> None:
    print(s, flush=True)
    with _LOCK:
        LINES.append(s)


def flush() -> None:
    with _LOCK:
        OUT.write_text("\n".join(LINES) + "\n", encoding="utf-8", newline="\n")


def hard_stop(where: str) -> None:
    emit()
    emit(f"STOPPED: hard cap {CAP_HARD_S} s reached at {elapsed():.1f} s during {where}; partial results above.")
    emit(f"run ended {clock()}")
    flush()
    os._exit(3)


def check_cap(where: str) -> None:
    if elapsed() >= CAP_HARD_S:
        hard_stop(where)


# ---------------------------------------------------------------- tables
def corpus_arrays(pages):
    """Per token: last-char index, first-char index, line id (contiguous per line); symbol list."""
    syms = sorted({t[-1] for p in pages for ln in p["lines"] for t in ln if t}
                  | {t[0] for p in pages for ln in p["lines"] for t in ln if t})
    idx = {s: i for i, s in enumerate(syms)}
    last, first, lid, pid = [], [], [], []
    n = 0
    for pi, p in enumerate(pages):
        for ln in p["lines"]:
            toks = [t for t in ln if t]
            if not toks:
                continue
            last.extend(idx[t[-1]] for t in toks)
            first.extend(idx[t[0]] for t in toks)
            lid.extend([n] * len(toks))
            pid.extend([pi] * len(toks))
            n += 1
    return dict(syms=syms, last=np.asarray(last, dtype=np.int64), first=np.asarray(first, dtype=np.int64),
                lid=np.asarray(lid, dtype=np.int64), pid=np.asarray(pid, dtype=np.int64), n_lines=n)


def table_from(last, first, lid, n):
    """T[i, j] = # adjacent within-line pairs with a[-1] = i, b[0] = j (g1.fit_table / c3.edge_pairs)."""
    same = lid[:-1] == lid[1:]
    a = last[:-1][same]
    b = first[1:][same]
    return np.bincount(a * n + b, minlength=n * n).reshape(n, n).astype(np.float64)


# ---------------------------------------------------------------- seriation search
def mad_of(T, pos):
    D = np.abs(pos[:, None] - pos[None, :])
    return float((T * D).sum() / T.sum())


def fiedler_order(T):
    S = T + T.T
    np.fill_diagonal(S, 0.0)
    L = np.diag(S.sum(1)) - S
    w, v = np.linalg.eigh(L)
    k = 1 if len(w) > 1 else 0
    return np.argsort(v[:, k], kind="stable")


def seriate(T, sweeps=N_SWEEPS):
    """Spectral init + best-improvement pairwise-swap sweeps (fixed budget). Returns (MAD, pos, sweeps_used)."""
    n = T.shape[0]
    tot = T.sum()
    if n < 2 or tot == 0:
        return 0.0, np.arange(n), 0
    S = T + T.T
    np.fill_diagonal(S, 0.0)
    order = fiedler_order(T)
    pos = np.empty(n, dtype=np.int64)
    pos[order] = np.arange(n)
    posf = pos.astype(np.float64)
    used = 0
    for sweep in range(sweeps):
        D = np.abs(posf[:, None] - posf[None, :])
        SD = S @ D
        diag = np.diag(SD)
        delta = SD + SD.T - diag[:, None] - diag[None, :] + 2.0 * S * D
        np.fill_diagonal(delta, 0.0)
        k = int(np.argmin(delta))
        a, b = divmod(k, n)
        if delta[a, b] < -1e-9:
            posf[a], posf[b] = posf[b], posf[a]
            used = sweep + 1
        else:
            break
    return mad_of(T, posf), posf.astype(np.int64), used


def band_mass(T, pos, w=2):
    D = np.abs(pos[:, None] - pos[None, :])
    return float(T[D <= w].sum() / T.sum())


def order_string(syms, pos):
    inv = np.argsort(pos)
    return "".join(syms[i] if len(syms[i]) == 1 else f"[{syms[i]}]" for i in inv)


# ---------------------------------------------------------------- MI (d1 convention)
def mi_plugin(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan")
    pj = Counter(pairs)
    pa = Counter(a for a, _ in pairs)
    pb = Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pj.items())


def mi_excess(pairs, seed=SEED, reps=N_MI_NULL):
    obs = mi_plugin(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    rng = random.Random(seed)
    vals = []
    for _ in range(reps):
        y2 = ys[:]
        rng.shuffle(y2)
        vals.append(mi_plugin(list(zip(xs, y2))))
    return obs, float(np.mean(vals)), obs - float(np.mean(vals))


def within_line_pairs(pages):
    return [(a[-1], b[0]) for p in pages for ln in p["lines"] for a, b in zip(ln, ln[1:]) if a and b]


def across_line_pairs(pages):
    out = []
    for p in pages:
        lines = [[t for t in ln if t] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        out += [(a[-1][-1], b[0][0]) for a, b in zip(lines, lines[1:])]
    return out


# ---------------------------------------------------------------- h2 (a1_profile.char_entropies convention)
def h2_of(words, n_tokens=H2_N):
    words = words[:n_tokens]
    s = " ".join(words) + " "
    c1 = Counter(s)
    n = len(s)
    h1 = -sum(v / n * math.log2(v / n) for v in c1.values())
    c2 = Counter(zip(s, s[1:]))
    n2 = sum(c2.values())
    h12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    return h12 - h1


def inventory_stats(residual):
    freq = Counter(residual)
    n = len(residual)
    cum, need = 0, 0
    for _, c in freq.most_common():
        cum += c
        need += 1
        if cum / n >= P3_COVER:
            break
    top100 = sum(c for _, c in freq.most_common(P3_MAX_TYPES)) / n
    return len(freq), need, top100


# ---------------------------------------------------------------- main
def main() -> None:
    watchdog = threading.Timer(CAP_HARD_S, hard_stop, args=("watchdog",))
    watchdog.daemon = True
    watchdog.start()

    emit("S24: bounded musical / hybrid-notation check (PLAN.md Phase 3 s24 approval; phase-3.md s5)")
    emit(f"run started {clock()}")
    emit(f"s24_music_seriation.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"cap: one CPU process, no GPU, no paid calls, no new data; expected < {CAP_EXPECTED_S} s; "
         f"HARD STOP {CAP_HARD_S} s (watchdog + in-loop checks); every matrix built at run time from existing sidecars")
    emit(f"loader: scoreboard/run_v2.py load_meta by path (sha256 {sha256(ROOT / 'scoreboard' / 'run_v2.py')[:16]}...)")
    emit(f"search: Fiedler init + {N_SWEEPS} best-improvement swap sweeps; nulls {N_NULL}+{N_NULL} per transliteration, "
         f"seed {SEED}; MI nulls {N_MI_NULL} reps; h2 on first {H2_N} tokens")
    emit()
    R2 = load_by_path("run_v2_s24", ROOT / "scoreboard" / "run_v2.py")
    MN = load_by_path("metrics_new_s24", ROOT / "scoreboard" / "metrics_new.py")

    voy = {}
    for name, path in VOYNICH:
        _, pages = R2.load_meta(path)
        voy[name] = pages
    ctrl = {}
    for name, path, note in LANG_TABLES + GEN_TABLES:
        if path.exists():
            _, pages = R2.load_meta(path)
            ctrl[name] = (pages, note)
        else:
            emit(f"control sidecar MISSING: {name} {path}")
    check_cap("loading")

    # ================================================================ P1
    emit("=== P1 seriation: within-line last-char -> next-first-char table, MAD bandwidth, same search everywhere ===")
    emit(f"{'table':24s} {'n':>3s} {'pairs':>6s} {'MAD':>8s} {'MAD/(n-1)':>9s} {'band<=2':>8s} {'sweeps':>6s}  ordering")
    p1 = {}
    for name, pages in voy.items():
        arr = corpus_arrays(pages)
        n = len(arr["syms"])
        T = table_from(arr["last"], arr["first"], arr["lid"], n)
        mad, pos, used = seriate(T)
        p1[name] = dict(arr=arr, T=T, mad=mad, pos=pos, n=n, pairs=int(T.sum()), band=band_mass(T, pos))
        emit(f"{name:24s} {n:3d} {int(T.sum()):6d} {mad:8.4f} {mad / (n - 1):9.4f} {band_mass(T, pos):8.4f} {used:6d}  "
             f"{order_string(arr['syms'], pos)}")
    check_cap("P1 Voynich tables")
    ctrl_mad = {}
    for name, (pages, note) in ctrl.items():
        arr = corpus_arrays(pages)
        n = len(arr["syms"])
        T = table_from(arr["last"], arr["first"], arr["lid"], n)
        mad, pos, used = seriate(T)
        ctrl_mad[name] = dict(mad=mad, n=n, pairs=int(T.sum()), band=band_mass(T, pos), note=note)
        emit(f"{name:24s} {n:3d} {int(T.sum()):6d} {mad:8.4f} {mad / (n - 1):9.4f} {band_mass(T, pos):8.4f} {used:6d}  "
             f"{order_string(arr['syms'], pos)[:60]}  [{note}]")
        check_cap(f"P1 control {name}")
    emit()
    emit(f"P1 nulls ({N_NULL} within-line shuffles + {N_NULL} row/column permutations per transliteration, same search):")
    emit(f"{'translit':10s} {'MAD_obs':>8s} {'shuf_p1':>8s} {'shuf_min':>8s} {'shuf_med':>8s} {'p_shuf':>6s} "
         f"{'rc_p1':>8s} {'rc_min':>8s} {'rc_med':>8s} {'p_rc':>6s}  below-1st-pct(shuf,rc)")
    for name, d in p1.items():
        arr, T, n = d["arr"], d["T"], d["n"]
        rng = np.random.default_rng(SEED)
        shuf = np.empty(N_NULL)
        for k in range(N_NULL):
            keys = rng.random(len(arr["lid"]))
            perm = np.lexsort((keys, arr["lid"]))
            Tn = table_from(arr["last"][perm], arr["first"][perm], arr["lid"], n)
            shuf[k] = seriate(Tn)[0]
            if k % 50 == 49:
                check_cap(f"P1 shuffle nulls {name}")
        rng2 = np.random.default_rng(SEED + 1)
        rc = np.empty(N_NULL)
        for k in range(N_NULL):
            sig = rng2.permutation(n)
            tau = rng2.permutation(n)
            rc[k] = seriate(T[sig][:, tau])[0]
            if k % 50 == 49:
                check_cap(f"P1 row/col nulls {name}")
        q_s, q_r = float(np.percentile(shuf, 1)), float(np.percentile(rc, 1))
        p_s = (1 + int(np.sum(shuf <= d["mad"]))) / (N_NULL + 1)
        p_r = (1 + int(np.sum(rc <= d["mad"]))) / (N_NULL + 1)
        d.update(shuf_q1=q_s, rc_q1=q_r, p_shuf=p_s, p_rc=p_r, shuf_min=float(shuf.min()), rc_min=float(rc.min()),
                 shuf_med=float(np.median(shuf)), rc_med=float(np.median(rc)))
        emit(f"{name:10s} {d['mad']:8.4f} {q_s:8.4f} {shuf.min():8.4f} {np.median(shuf):8.4f} {p_s:6.3f} "
             f"{q_r:8.4f} {rc.min():8.4f} {np.median(rc):8.4f} {p_r:6.3f}  "
             f"({d['mad'] < q_s}, {d['mad'] < q_r})")
    emit()
    ctrl_min_name = min(ctrl_mad, key=lambda k: ctrl_mad[k]["mad"])
    ctrl_min = ctrl_mad[ctrl_min_name]["mad"]
    spread = max(d["mad"] for d in p1.values()) - min(d["mad"] for d in p1.values())
    emit(f"P1 control minimum MAD = {ctrl_min:.4f} ({ctrl_min_name}); Voynich MAD spread across translits = {spread:.4f}")
    p1_pass = {}
    for name, d in p1.items():
        ok = d["mad"] < d["shuf_q1"] and d["mad"] < d["rc_q1"] and d["mad"] < ctrl_min
        p1_pass[name] = ok
        emit(f"P1 {name}: MAD {d['mad']:.4f} vs shuffle 1st pct {d['shuf_q1']:.4f} ({'below' if d['mad'] < d['shuf_q1'] else 'NOT below'}), "
             f"row/col 1st pct {d['rc_q1']:.4f} ({'below' if d['mad'] < d['rc_q1'] else 'NOT below'}), "
             f"control min {ctrl_min:.4f} ({'below' if d['mad'] < ctrl_min else 'NOT below'}) -> {'PASS' if ok else 'FAIL'}")
    emit(f"P1 overall: {'PASS' if all(p1_pass.values()) else 'FAIL'} (all three transliterations required)")
    emit()
    flush()
    check_cap("after P1")

    # ================================================================ P2
    emit("=== P2 line-end reset: MI excess (bits, 20 permutation nulls) across line ends vs within lines ===")
    emit(f"{'corpus':24s} {'n_within':>8s} {'MI_w':>7s} {'null_w':>7s} {'exc_w':>7s} {'n_across':>8s} {'MI_a':>7s} "
         f"{'null_a':>7s} {'exc_a':>7s} {'ratio':>7s}")
    p2 = {}

    def p2_row(name, pages, note=""):
        wp = within_line_pairs(pages)
        ap = across_line_pairs(pages)
        mw, nw, ew = mi_excess(wp)
        ma, na, ea = mi_excess(ap)
        ratio = ea / ew if ew else float("nan")
        p2[name] = ratio
        emit(f"{name:24s} {len(wp):8d} {mw:7.4f} {nw:7.4f} {ew:7.4f} {len(ap):8d} {ma:7.4f} {na:7.4f} {ea:7.4f} {ratio:7.4f}  {note}")

    for name, pages in voy.items():
        p2_row(name, pages, "Voynich")
    for name, path, note in LANG_TABLES:
        if name in ctrl:
            p2_row(name, ctrl[name][0], note)
        check_cap(f"P2 {name}")
    for name, path, note in GEN_TABLES:
        if name in ctrl:
            p2_row(name, ctrl[name][0], f"generator (reference only): {note}")
        check_cap(f"P2 {name}")
    lang_ratios = {k: p2[k] for k, _, _ in LANG_TABLES if k in p2}
    lang_min_name = min(lang_ratios, key=lambda k: lang_ratios[k])
    lang_min = lang_ratios[lang_min_name]
    emit(f"P2 minimum real-line ratio = {lang_min:.4f} ({lang_min_name}); all: " +
         ", ".join(f"{k} {v:.4f}" for k, v in lang_ratios.items()))
    p2_pass = {}
    for name, _ in VOYNICH:
        ok = p2[name] < lang_min
        p2_pass[name] = ok
        emit(f"P2 {name}: ratio {p2[name]:.4f} vs real-line min {lang_min:.4f} -> {'PASS' if ok else 'FAIL'}")
    emit(f"P2 overall: {'PASS' if all(p2_pass.values()) else 'FAIL'}")
    emit()
    flush()
    check_cap("after P2")

    # ================================================================ P3
    emit("=== P3 residual inventory after stripping the putative pitch slot (F = first char, L = last char) ===")
    h2_rows = {}
    for p in H2_ROWS:
        if p.exists():
            h2_rows[p.stem] = float(json.loads(p.read_text(encoding="utf-8"))["row"]["h2"])
        else:
            emit(f"h2 row MISSING: {p}")
    h2_lo, h2_hi = min(h2_rows.values()), max(h2_rows.values())
    emit("language h2 rows: " + ", ".join(f"{k.replace('results_', '')}={v:.4f}" for k, v in h2_rows.items()))
    emit(f"language h2 range = [{h2_lo:.4f}, {h2_hi:.4f}]")
    emit(f"{'translit':8s} {'slot':6s} {'tokens':>6s} {'dropped':>7s} {'types':>6s} {'need90':>6s} {'top100%':>8s} "
         f"{'h2':>7s}  inv<=100  h2-in-range  variant")
    p3 = {}
    for name, pages in voy.items():
        toks = [t for p in pages for ln in p["lines"] for t in ln if t]
        full_h2 = h2_of(toks)
        full_types, full_need, full_top = inventory_stats(toks)
        emit(f"{name:8s} {'none':6s} {len(toks):6d} {0:7d} {full_types:6d} {full_need:6d} {100 * full_top:8.2f} {full_h2:7.4f}  "
             f"{'-':8s}  {'-':11s}  unstripped reference")
        variants = {"F": [t[1:] for t in toks], "L": [t[:-1] for t in toks]}
        seg = MN.SlotSegmenter(toks)
        variants["SEG"] = [(lambda s: s[0] + s[2])(seg.segment(t)) for t in toks]
        res = {}
        for var, stream in variants.items():
            dropped = sum(1 for r in stream if not r)
            stream = [r for r in stream if r]
            types, need, top = inventory_stats(stream)
            h2 = h2_of(stream)
            inv_ok = need <= P3_MAX_TYPES
            h2_ok = h2_lo <= h2 <= h2_hi
            res[var] = (inv_ok and h2_ok, types, need, top, h2)
            tag = "diagnostic (not scored): SlotSegmenter core stripped, prefix+suffix kept" if var == "SEG" else \
                ("first-char slot stripped" if var == "F" else "last-char slot stripped")
            emit(f"{name:8s} {var:6s} {len(stream):6d} {dropped:7d} {types:6d} {need:6d} {100 * top:8.2f} {h2:7.4f}  "
                 f"{str(inv_ok):8s}  {str(h2_ok):11s}  {tag}")
        ok = res["F"][0] or res["L"][0]
        p3[name] = ok
        emit(f"P3 {name}: F {'PASS' if res['F'][0] else 'FAIL'} (need {res['F'][2]} types for 90 %, h2 {res['F'][4]:.4f}); "
             f"L {'PASS' if res['L'][0] else 'FAIL'} (need {res['L'][2]} types, h2 {res['L'][4]:.4f}); "
             f"SEG diagnostic {'meets' if res['SEG'][0] else 'misses'} -> {'PASS' if ok else 'FAIL'} (either F or L)")
        check_cap(f"P3 {name}")
    emit(f"P3 overall: {'PASS' if all(p3.values()) else 'FAIL'}")
    emit()

    # ================================================================ verdict
    emit("=== VERDICT (pre-registered rule: SUPPORTED only if P1, P2 and P3 all PASS on all three transliterations) ===")
    for name, _ in VOYNICH:
        emit(f"{name}: P1 {'PASS' if p1_pass[name] else 'FAIL'}  P2 {'PASS' if p2_pass[name] else 'FAIL'}  "
             f"P3 {'PASS' if p3[name] else 'FAIL'}")
    supported = all(p1_pass.values()) and all(p2_pass.values()) and all(p3.values())
    emit(f"VERDICT: musical/hybrid notation {'SUPPORTED' if supported else 'NOT SUPPORTED'}")
    failed = [f"P{i}" for i, pp in ((1, p1_pass), (2, p2_pass), (3, p3)) if not all(pp.values())]
    emit(f"failed predictions: {', '.join(failed) if failed else 'none'}")
    emit()
    emit(f"elapsed {elapsed():.1f} s (expected < {CAP_EXPECTED_S} s; hard cap {CAP_HARD_S} s; within cap: {elapsed() < CAP_HARD_S})")
    emit(f"done-when: results_s24.txt exists with the P1/P2/P3 blocks on all three transliterations, the control values "
         f"and the verdict line -> met")
    emit(f"run ended {clock()}")
    flush()
    watchdog.cancel()


if __name__ == "__main__":
    main()
