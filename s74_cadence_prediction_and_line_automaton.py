#!/usr/bin/env python3
"""s74_cadence_prediction_and_line_automaton.py — Length-Blind Cadence Prediction & Line Automaton Investigator (s74).

PRE-REGISTERED SPECIFICATION (frozen in s74_cadence_prediction_and_line_automaton.prereg.sha256 BEFORE running on real data):
Closes CONSTRAINTS-MAP.md §C line 194 & O-043 ("The line rhythm can be planted but not yet predicted") and
connects Dots 21, 23, 25 (s37, s60, s66, s67, s69) across ZL3b, RF1b, and IT2a.

Three pre-registered parts:
  Part 1 — Exact Decomposition of Within-Line Rhythm (I_within = 0.156 on HO41) into Page/Line Mean Drift
           vs. Strictly Length-Blind Morphological State Transitions (166 -> 41 Split):
    - Evaluates a nested ladder of strictly length-blind, zero-free-parameter counted Markov slot/class
      automata fitted ONLY by maximum-likelihood counts on the 166 training pages (NO word length |w|,
      NO core length |c|, NO affix length |p|, |s|, and NO fitting to Moran I):
        * L0_unigram           : Page/(Hand, Section)-conditioned unigram draw (captures page/hand mean drift).
        * L1_pos_scribe        : L0 + 5-state line position (para_0, line_0, slot_1, mid, line_end) per Davis Hand (s60).
        * L2_s69_affix_chain   : L1 + s69 one-word affix transition P(P_t, S_t | P_{t-1}, S_{t-1}, pos, hand) with
                                 core C_t drawn compositionally via length-blind core class k_t ~ P(K(C_t) | P_t, S_t, pos, hand).
        * L3_core_to_next_affix: L2 + Core-to-next-Prefix/Suffix Handshake P(P_t, S_t | K(C_{t-1}), P_{t-1}, S_{t-1}, pos, hand)
                                 and C_t ~ P(C_t | k_t, hand, sec), where K(C) in {0..19} is a strictly length-blind
                                 core cluster defined ONLY by boundary glyph classes and training (P, S, P_next) co-occurrence
                                 profiles (zero length information).
        * L4_line_mode_register: L3 + Per-Line Counted Affix/Core Mode m_L in {0..5} (6-state length-blind line register
                                 clustered strictly on training line (P, S, K(C)) categorical token counts + empirical
                                 training-line Dirichlet-Multinomial slot/class palette in (hand, section), zero length input).
    - Measures on ZL3b, RF1b, IT2a (3 seeds each on the 41 held-out pages):
      I_within, line-shuffle null_med, intra-line excess I_within - null_med, bilinear covariances
      dCov(w,w), dCov(A,A), dCov(C,A) [split into dCov(C1,P2) + dCov(C1,S2)], dCov(A,C), dCov(C,C),
      within-word Cov(|A_t|, |C_t|), held-out s69 M1 prefix_gain, CHARWIN, jsd_first, cross_excess_eva,
      A14 core->core MI excess, and types.

  Part 2 — Why Does Cov(|C_{t-1}|, |P_t|) Equal +28.0% of Intra-Line Covariance? (Phonotactic / Graphical
           vs. Metric Handshake Test):
    - On the 166 training and 41 held-out pages (ZL3b, RF1b, IT2a), tests Hypothesis H_graphical
      (Length-Blind Glyph/Slot Conditioning) vs. Residual Metric Length Coupling using an exact
      Law-of-Total-Covariance / Within-Cell Permutation Ladder (200 shuffles of |C_{t-1}| within each
      length-blind conditioning cell Z):
        * Z0_hand_pos      : (hand, pos_1)
        * Z1_prev_affix    : (hand, pos_1, P_1, S_1)
        * Z2_graphical_edge: (hand, pos_1, S_1, last_glyph(w_1))
        * Z3_full_graphical: (hand, pos_1, P_1, S_1, last_glyph(w_1), first_glyph(C_1), gallows_bench_class(C_1))
        * Z4_core_class_K20: (hand, pos_1, P_1, S_1, K(C_1))
        * Z5_s69_triplet   : (hand, pos_1, P_1, S_1, P_2)
    - Reports analytical & permutation-based explained covariance, % of raw Cov(|C1|,|P2|) and intra-line
      dCov(|C1|,|P2|) explained without knowing |C_1|, residual within-cell metric covariance Cov(|C1|,|P2| | Z),
      and a concrete morphological core-family table.

  Part 3 — Leave-One-Quire-Out (15 Quires) Test of Zero-Length-Parameter L3_core_to_next_affix and
           L4_line_mode_register vs. s67:
    - Evaluates L3_core_to_next_affix and L4_line_mode_register (both with 0 length parameters, fitting no
      gamma or rho to Moran I, using s66's (Hand, Section) -> Hand -> Lang training pool so Quire M uses Hand 2 priors)
      across all 15 quires (LOQO) on ZL3b, RF1b, IT2a for P1 Moran I, P2 A14 core->core, P3 s69 M1 prefix_gain,
      P4 jsd_first, P5 CHARWIN, and P7 types ratio, compared side-by-side against s67's CA and CA0.

Run:    python -I s74_cadence_prediction_and_line_automaton.py [--fixture] [--list-imports]
Writes: results_s74.txt only.
"""
from __future__ import annotations

import bisect
import functools
import hashlib
import json
import math
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

import a2_position as A2  # noqa: E402
import g1_edge_joint as G1  # noqa: E402
import m3_bakeoff_reconcile as M3  # noqa: E402
import s21_moran_realline as S21  # noqa: E402
import vparse  # noqa: E402
from scoreboard.metrics_new import CharMarkov, SlotSegmenter  # noqa: E402


def make_cached_segmenter(toks: list[str]) -> SlotSegmenter:
    seg = SlotSegmenter(toks)
    seg.segment = functools.lru_cache(maxsize=None)(seg.segment)  # type: ignore[method-assign]
    return seg


SELF = ROOT / "s74_cadence_prediction_and_line_automaton.py"
STUB = ROOT / "s74_cadence_prediction_and_line_automaton.prereg.sha256"
OUT = ROOT / "results_s74.txt"

SEED = 20261017
EMPTY = "∅"
K_CORE = 20
K_STATE = 8
M_LINE = 6
TOP_CORES = 150
ALPHA_SMOOTH = 3.0
N_SEEDS_P1 = 3
N_SHUF_MORAN = 80
N_SHUF_CELL = 80
N_DRAW_LOQO = 25
SMALL_FOLD = 6
S15_JSD = (0.1447, 0.2156)
TOL_SMALL = dict(P1=0.0158, P2=0.0203, P3=0.0170)
TYPE_TOL = 0.15
PREDS = ["P1", "P2", "P3", "P4", "P5", "P7"]

TRANSLITS = OrderedDict([
    ("ZL3b", "ZL3b_eva"),
    ("RF1b", "RF1b"),
    ("IT2a", "IT2a"),
])

log_lines: list[str] = []
T0 = time.time()


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


def flush_output() -> None:
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
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f).lower() != h.lower()]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


# ==============================================================================
# DATA LOADING & DAVIS SCRIBE / SECTION METADATA
# ==============================================================================
def load_folio_inventory() -> dict[str, dict[str, str]]:
    inv: dict[str, dict[str, str]] = {}
    inv_path = ROOT / "data" / "folio_evidence_inventory.tsv"
    if inv_path.exists():
        lines = inv_path.read_text(encoding="utf-8").splitlines()
        if lines:
            headers = lines[0].split("\t")
            for ln in lines[1:]:
                if not ln.strip():
                    continue
                row = dict(zip(headers, ln.split("\t")))
                f = row["folio"]
                h_raw = row.get("hand", "?")
                q_raw = row.get("quire", "?")
                davis_h = h_raw if h_raw in {"1", "2", "3", "4", "5"} else (
                    "3" if q_raw == "T" or f == "f115r" else h_raw
                )
                inv[f] = dict(
                    hand=davis_h,
                    lang=row.get("lang", "?"),
                    section=row.get("section", "?"),
                    quire=q_raw,
                )
    zl_path = ROOT / "data" / "ZL3b-n.txt"
    if zl_path.exists():
        for raw in zl_path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = vparse.PAGE_RE.match(raw)
            if m:
                f = m.group(1)
                d = dict(vparse.VAR_RE.findall(m.group(2)))
                cur = inv.get(f, {})
                q_r = d.get("Q", cur.get("quire", "?"))
                h_r = d.get("H", cur.get("hand", "?"))
                if h_r not in {"1", "2", "3", "4", "5"} and (q_r == "T" or f == "f115r"):
                    h_r = "3"
                inv[f] = dict(
                    hand=h_r if h_r in {"1", "2", "3", "4", "5"} else cur.get("hand", "3"),
                    lang=d.get("L", cur.get("lang", "?")),
                    section=d.get("I", cur.get("section", "?")),
                    quire=q_r,
                )
    return inv


def load_translit_pages(meta_stem: str, inv: dict[str, dict[str, str]]) -> tuple[list[dict], dict[str, list[list[str]]], str]:
    meta_path = ROOT / "data" / "translit" / f"{meta_stem}.meta.json"
    d = json.loads(meta_path.read_text(encoding="utf-8"))
    pages = []
    by_page = OrderedDict()
    for p in d["pages"]:
        pid = str(p["id"])
        lines = [[str(w) for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if not lines:
            continue
        info = inv.get(pid, {})
        q_str = str(p.get("quire") or info.get("quire") or "?")
        h_str = str(p.get("hand") or info.get("hand") or "?")
        if h_str not in {"1", "2", "3", "4", "5"}:
            h_str = info.get("hand", "3" if q_str == "T" or pid == "f115r" else "1")
        sec_str = str(p.get("section") or info.get("section") or "?")
        lang_str = str(p.get("lang") or p.get("currier") or info.get("lang") or ("A" if h_str == "1" else "B"))
        rec = dict(
            id=pid,
            hand=h_str,
            section=sec_str,
            quire=q_str,
            lang=lang_str,
            lines=lines,
        )
        pages.append(rec)
        by_page[pid] = lines
    return pages, by_page, sha256(meta_path)[:16]


def pos_5(l_idx: int, i: int, L: int) -> str:
    if i == 0:
        return "para_0" if l_idx == 0 else "line_0"
    if i == L - 1:
        return "line_end"
    if i == 1:
        return "slot_1"
    return "mid"


# ==============================================================================
# FAST BLAS K-MEANS & STRICTLY LENGTH-BLIND MORPHOLOGICAL AUTOMATON (L0..L4)
# ==============================================================================
def kmeans_pp(X: np.ndarray, k: int, seed: int = SEED, restarts: int = 2, iters: int = 15) -> tuple[np.ndarray, np.ndarray]:
    """Fast BLAS matrix-multiply k-means++ (no 3D broadcasting)."""
    rng = np.random.default_rng(seed)
    n, d = X.shape
    if n <= k:
        C = np.zeros((k, d), dtype=np.float64)
        C[:n] = X
        lab = np.arange(n, dtype=np.int64) % max(1, k)
        return C, lab
    x_norm2 = (X * X).sum(axis=1)
    best_inertia = float("inf")
    best_C = None
    best_lab = None
    for _ in range(restarts):
        c_idx = [int(rng.integers(n))]
        d2 = np.maximum(0.0, x_norm2 + x_norm2[c_idx[0]] - 2.0 * (X @ X[c_idx[0]]))
        for _j in range(1, k):
            s = float(d2.sum())
            pr = d2 / s if s > 1e-12 else np.full(n, 1.0 / n)
            nxt = int(rng.choice(n, p=pr))
            c_idx.append(nxt)
            d2_new = np.maximum(0.0, x_norm2 + x_norm2[nxt] - 2.0 * (X @ X[nxt]))
            d2 = np.minimum(d2, d2_new)
        C = X[c_idx].copy()
        lab = np.zeros(n, dtype=np.int64)
        for _it in range(iters):
            c_norm2 = (C * C).sum(axis=1)
            D = np.maximum(0.0, x_norm2[:, None] + c_norm2[None, :] - 2.0 * (X @ C.T))
            nl = D.argmin(axis=1)
            if _it > 0 and np.array_equal(nl, lab):
                break
            lab = nl
            for j in range(k):
                mask = (lab == j)
                if np.any(mask):
                    C[j] = X[mask].mean(axis=0)
        c_norm2 = (C * C).sum(axis=1)
        D = np.maximum(0.0, x_norm2[:, None] + c_norm2[None, :] - 2.0 * (X @ C.T))
        inertia = float(D[np.arange(n), lab].sum())
        if inertia < best_inertia:
            best_inertia = inertia
            best_C = C.copy()
            best_lab = lab.copy()
    return best_C, best_lab


ATOMIC_EVA = frozenset({"o", "a", "e", "y", "d", "l", "r", "s", "k", "t", "p", "f", "i", "m", "n", "g"})


@functools.lru_cache(maxsize=None)
def core_glyph_features(c: str) -> np.ndarray:
    """Strictly length-blind categorical glyph-identity and morpheme-group feature vector for core c.
    Uses ONLY first glyph identity, last glyph identity, and categorical ligature/geminate/coda group presence.
    NEVER computes or uses len(c)!"""
    first_alph = "oaeyktpfcsdlrqi"
    last_alph = "yrlnsomdktehai"
    v = np.zeros(len(first_alph) + len(last_alph) + 8, dtype=np.float64)
    if not c or c == EMPTY:
        return v
    ch0, ch1 = c[0], c[-1]
    if ch0 in first_alph:
        v[first_alph.index(ch0)] = 0.5
    off = len(first_alph)
    if ch1 in last_alph:
        v[off + last_alph.index(ch1)] = 0.5
    off2 = off + len(last_alph)
    if "cth" in c or "ckh" in c or "cph" in c or "cfh" in c:
        v[off2 + 0] = 1.2
    elif "ch" in c or "sh" in c:
        v[off2 + 1] = 1.0
    if any(g in c for g in "ktpf"):
        v[off2 + 2] = 1.0
    if "ee" in c or "eo" in c or "ea" in c:
        v[off2 + 3] = 1.2
    if "ii" in c or "ai" in c or "oi" in c:
        v[off2 + 4] = 1.2
    if any(sub in c for sub in ("al", "ar", "ol", "or", "el", "er", "in", "an", "am", "om")):
        v[off2 + 5] = 1.0
    if any(sub in c for sub in ("ey", "ay", "oy", "dy", "ky", "ty")):
        v[off2 + 6] = 1.0
    if c in ATOMIC_EVA:
        v[off2 + 7] = 1.4
    return v


def build_length_blind_core_clusters(train_pages: list[dict], seg: SlotSegmenter) -> tuple[dict[str, int], np.ndarray, np.ndarray]:
    """Builds K_CORE = 20 strictly length-blind core clusters K(C) in {0..19} from training pages ONLY.
    Features: smoothed [P(P_t|c), P(S_t|c), P(P_{t+1}|c), P(S_{t+1}|c), 0.65 * core_glyph_features(c)].
    Zero word/core/affix length information."""
    pre_c: dict[str, Counter] = defaultdict(Counter)
    suf_c: dict[str, Counter] = defaultdict(Counter)
    np_c: dict[str, Counter] = defaultdict(Counter)
    ns_c: dict[str, Counter] = defaultdict(Counter)
    gp, gs = Counter(), Counter()
    cc = Counter()

    for p in train_pages:
        for ln in p["lines"]:
            pcs = [seg.segment(w) for w in ln]
            for i, (pr, co, su) in enumerate(pcs):
                P = pr or EMPTY
                C = co or EMPTY
                S = su or EMPTY
                pre_c[C][P] += 1
                suf_c[C][S] += 1
                gp[P] += 1
                gs[S] += 1
                cc[C] += 1
                if i + 1 < len(pcs):
                    P2 = pcs[i + 1][0] or EMPTY
                    S2 = pcs[i + 1][2] or EMPTY
                    np_c[C][P2] += 1
                    ns_c[C][S2] += 1

    pv = sorted(gp.keys())
    sv = sorted(gs.keys())
    gP = np.array([gp[x] for x in pv], dtype=np.float64)
    gP /= max(1.0, float(gP.sum()))
    gS = np.array([gs[x] for x in sv], dtype=np.float64)
    gS /= max(1.0, float(gS.sum()))

    def full_prof(c: str) -> np.ndarray:
        n = cc[c]
        n_nx = sum(np_c[c].values())
        a = (np.array([pre_c[c][x] for x in pv], dtype=np.float64) + ALPHA_SMOOTH * gP) / (n + ALPHA_SMOOTH)
        b = (np.array([suf_c[c][x] for x in sv], dtype=np.float64) + ALPHA_SMOOTH * gS) / (n + ALPHA_SMOOTH)
        c_np = (np.array([np_c[c][x] for x in pv], dtype=np.float64) + ALPHA_SMOOTH * gP) / (n_nx + ALPHA_SMOOTH)
        c_ns = (np.array([ns_c[c][x] for x in sv], dtype=np.float64) + ALPHA_SMOOTH * gS) / (n_nx + ALPHA_SMOOTH)
        gf = 1.10 * core_glyph_features(c)
        return np.concatenate([a, b, c_np, c_ns, gf])

    ranked = sorted(cc.keys(), key=lambda x: (-cc[x], x))
    top = ranked[: min(TOP_CORES, len(ranked))]
    X_top = np.array([full_prof(c) for c in top], dtype=np.float64)
    C_cent, lab_top = kmeans_pp(X_top, K_CORE, seed=SEED)
    cls_map: dict[str, int] = {c: int(l) for c, l in zip(top, lab_top)}

    gf_dim = len(core_glyph_features("daiin"))
    C_gf = C_cent[:, -gf_dim:]
    c_gf_norm2 = (C_gf * C_gf).sum(axis=1)

    rest_cores = ranked[len(top):]
    if rest_cores:
        X_gf_rest = np.array([1.10 * core_glyph_features(c) for c in rest_cores], dtype=np.float64)
        D_gf = (X_gf_rest * X_gf_rest).sum(axis=1)[:, None] + c_gf_norm2[None, :] - 2.0 * (X_gf_rest @ C_gf.T)
        for c, l_i in zip(rest_cores, D_gf.argmin(axis=1)):
            cls_map[c] = int(l_i)

    return cls_map, C_cent, C_gf


def get_core_class(c: str, cls_map: dict[str, int], C_gf: np.ndarray) -> int:
    k = cls_map.get(c)
    if k is not None:
        return k
    gf = 1.10 * core_glyph_features(c)
    return int(((C_gf - gf) ** 2).sum(axis=1).argmin())


def _compile_wb_table(tab: dict[tuple, Counter], discount_scale: float = 1.0) -> dict[tuple, tuple[list, list[int], float]]:
    out = {}
    for k, cnt in tab.items():
        items = sorted(cnt.items(), key=lambda kv: (-kv[1], str(kv[0])))
        ws = [x for x, _ in items]
        cum, tot = [], 0
        for _, v in items:
            tot += v
            cum.append(tot)
        T = len(items)
        lam = tot / (tot + discount_scale * T)
        out[k] = (ws, cum, lam)
    return out


def _sample_cum(rng: random.Random, ws: list, cum: list[int]):
    return ws[bisect.bisect_right(cum, rng.random() * cum[-1])]


class LengthBlindLineAutomaton:
    """Strictly length-blind counted Markov slot/class/line-mode automaton implementing rungs L0..L4.
    Words w_t = P_t + C_t + S_t are assembled compositionally from (P_t, S_t) and C_t coupled strictly
    through the 20-class length-blind core cluster k_t = K(C_t) in {0..19} (plus page-level core repeat
    at distance d in 2..20 with fixed p_rep = 0.08, tau = 10.0 from s56/s67).
    Zero word/core/affix lengths used anywhere in training or generation. Zero fitted continuous parameters."""

    def __init__(self, train_pages: list[dict], seg: SlotSegmenter):
        self.seg = seg
        self.cls_map, self.C_cent, self.C_gf = build_length_blind_core_clusters(train_pages, seg)

        # Pass 1: annotate tokens and count (P, S, K(C)) next-affix profiles
        triple_next_p: dict[tuple, Counter] = defaultdict(Counter)
        triple_next_s: dict[tuple, Counter] = defaultdict(Counter)
        triple_cnt: Counter = Counter()
        gp, gs = Counter(), Counter()
        hs_tok_counts: Counter = Counter()
        h_tok_counts: Counter = Counter()

        ann_pages = []
        for p in train_pages:
            hand = p["hand"]
            sec = p["section"]
            lang = p.get("lang", "A" if hand == "1" else "B")
            hs = (hand, sec)
            ann_lines = []
            for l_idx, ln in enumerate(p["lines"]):
                L = len(ln)
                row = []
                pcs = [seg.segment(w) for w in ln]
                for i, (w, (pr, co, su)) in enumerate(zip(ln, pcs)):
                    P = pr or EMPTY
                    C = co or EMPTY
                    S = su or EMPTY
                    k = get_core_class(C, self.cls_map, self.C_gf)
                    pos = pos_5(l_idx, i, L)
                    end_g = w[-1]
                    gp[P] += 1
                    gs[S] += 1
                    hs_tok_counts[hs] += 1
                    h_tok_counts[hand] += 1
                    tr_key = (P, S, k)
                    triple_cnt[tr_key] += 1
                    if i + 1 < L:
                        P2 = pcs[i + 1][0] or EMPTY
                        S2 = pcs[i + 1][2] or EMPTY
                        triple_next_p[tr_key][P2] += 1
                        triple_next_s[tr_key][S2] += 1
                    row.append(dict(w=w, pre=pr, core=co, suf=su, P=P, C=C, S=S, F=(P, S), k=k, pos=pos, end_g=end_g))
                ann_lines.append(row)
            ann_pages.append(dict(p, hs=hs, lang=lang, ann_lines=ann_lines))

        self.hs_tok_counts = hs_tok_counts
        self.h_tok_counts = h_tok_counts
        self.pv = sorted(gp.keys())
        self.sv = sorted(gs.keys())
        p2i = {x: i for i, x in enumerate(self.pv)}
        s2i = {x: i for i, x in enumerate(self.sv)}
        gP = np.array([gp[x] for x in self.pv], dtype=np.float64)
        gP /= max(1.0, float(gP.sum()))
        gS = np.array([gs[x] for x in self.sv], dtype=np.float64)
        gS /= max(1.0, float(gS.sum()))

        # Cluster top 120 (P, S, K(C)) triples into K_STATE = 8 transition-equivalent states M_tok
        all_triples = sorted(triple_cnt.keys(), key=lambda x: (-triple_cnt[x], str(x)))
        n_top_tr = min(120, len(all_triples))
        X_tr = []
        for tk in all_triples[:n_top_tr]:
            n_nx = sum(triple_next_p[tk].values())
            vp = (np.array([triple_next_p[tk][x] for x in self.pv], dtype=np.float64) + 2.0 * gP) / (n_nx + 2.0)
            vs = (np.array([triple_next_s[tk][x] for x in self.sv], dtype=np.float64) + 2.0 * gS) / (n_nx + 2.0)
            X_tr.append(np.concatenate([vp, vs]))
        X_tr_arr = np.array(X_tr, dtype=np.float64)
        _, lab_top_tr = kmeans_pp(X_tr_arr, K_STATE, seed=SEED)
        self.mtok_map: dict[tuple, int] = {tk: int(l) for tk, l in zip(all_triples[:n_top_tr], lab_top_tr)}
        for tk in all_triples[n_top_tr:]:
            self.mtok_map[tk] = tk[2] % K_STATE

        # Cluster training lines into M_LINE = 6 categorical line-mode registers m_L (strictly length-blind)
        VP, VS = len(self.pv), len(self.sv)
        line_vecs = []
        line_refs = []
        for p_idx, p in enumerate(ann_pages):
            for l_idx, ln in enumerate(p["ann_lines"]):
                L = max(1, len(ln))
                v = np.zeros(VP + VS + K_CORE + K_STATE, dtype=np.float64)
                for r in ln:
                    r["m_tok"] = self.mtok_map.get((r["P"], r["S"], r["k"]), r["k"] % K_STATE)
                    v[p2i[r["P"]]] += 1.0 / L
                    v[VP + s2i[r["S"]]] += 1.0 / L
                    v[VP + VS + r["k"]] += 1.5 / L
                    v[VP + VS + K_CORE + r["m_tok"]] += 1.0 / L
                line_vecs.append(v)
                line_refs.append((p_idx, l_idx))
        X_line = np.array(line_vecs, dtype=np.float64)
        n_sub_l = min(500, len(X_line))
        C_line, _ = kmeans_pp(X_line[:n_sub_l], M_LINE, seed=SEED)
        D_line = ((X_line * X_line).sum(axis=1)[:, None] + (C_line * C_line).sum(axis=1)[None, :] - 2.0 * (X_line @ C_line.T))
        lab_line = D_line.argmin(axis=1)
        for (p_idx, l_idx), m_l in zip(line_refs, lab_line):
            for r in ann_pages[p_idx]["ann_lines"][l_idx]:
                r["m_line"] = int(m_l)

        # Store training line templates and line-mode transitions
        self.line_templates_hs: dict[tuple, list[dict]] = defaultdict(list)
        self.line_templates_h: dict[tuple, list[dict]] = defaultdict(list)
        self.line_templates_lang: dict[tuple, list[dict]] = defaultdict(list)
        self.line_mode_trans_hs: dict[tuple, Counter] = defaultdict(Counter)
        self.line_mode_trans_h: dict[tuple, Counter] = defaultdict(Counter)
        self.line_mode_uni_hs: dict[tuple, Counter] = defaultdict(Counter)
        self.line_mode_uni_h: dict[str, Counter] = defaultdict(Counter)

        # Counted tables for L0..L4:
        f_l0 = [defaultdict(Counter) for _ in range(3)]   # hs -> hand -> global
        f_l1 = [defaultdict(Counter) for _ in range(3)]   # (pos, hs) -> (pos, hand) -> (pos,)
        f_l2 = [defaultdict(Counter) for _ in range(2)]   # (P1, S1, pos, hand) -> (P1, pos)
        f_l3 = [defaultdict(Counter) for _ in range(4)]   # (k1, P1, S1, pos, hand) -> (k1, S1, end1, pos, hand) -> (m1, P1, pos, hand) -> (P1, pos)
        f_l4 = [defaultdict(Counter) for _ in range(3)]   # (mL, k1, P1, S1, pos, hand) -> (mL, m1, P1, pos, hand) -> (mL, pos, hand)

        # Compositional core-class selection P(k_t | ...) and core lexicon P(C_t | ...)
        # Note: c_given_k NEVER conditions on prefix P_t, ensuring P_t + C_t + S_t is always assembled compositionally!
        k_given_f = [defaultdict(Counter) for _ in range(5)]  # (mL, F, k1, pos, hand) -> (F, k1, pos, hand) -> (F, pos, hand) -> (F,) -> (hand,)
        c_given_k = [defaultdict(Counter) for _ in range(5)]  # (k, S, hs) -> (k, hs) -> (k, hand) -> (k, lang) -> (k,)

        for p in ann_pages:
            hand = p["hand"]
            hs = p["hs"]
            lang = p["lang"]
            prev_mL = -1
            for l_idx, ln in enumerate(p["ann_lines"]):
                mL = ln[0]["m_line"]
                self.line_mode_uni_hs[hs][mL] += 1
                self.line_mode_uni_h[hand][mL] += 1
                if l_idx > 0:
                    self.line_mode_trans_hs[(hs, prev_mL)][mL] += 1
                    self.line_mode_trans_h[(hand, prev_mL)][mL] += 1
                prev_mL = mL

                if len(ln) >= 2:
                    tmpl = dict(
                        F_set=frozenset(r["F"] for r in ln),
                        P_set=frozenset(r["P"] for r in ln),
                        S_set=frozenset(r["S"] for r in ln),
                        K_set=frozenset(r["k"] for r in ln),
                    )
                    self.line_templates_hs[(hs, mL)].append(tmpl)
                    self.line_templates_h[(hand, mL)].append(tmpl)
                    self.line_templates_lang[(lang, mL)].append(tmpl)

                for i, r in enumerate(ln):
                    F = r["F"]
                    S = r["S"]
                    C = r["core"]
                    k = r["k"]
                    pos = r["pos"]

                    f_l0[0][hs][F] += 1
                    f_l0[1][hand][F] += 1
                    f_l0[2]["*"][F] += 1

                    f_l1[0][(pos, hs)][F] += 1
                    f_l1[1][(pos, hand)][F] += 1
                    f_l1[2][(pos,)][F] += 1

                    f_l4[2][(mL, pos, hand)][F] += 1

                    k_given_f[2][(F, pos, hand)][k] += 1
                    k_given_f[3][(F,)][k] += 1
                    k_given_f[4][(hand,)][k] += 1

                    c_given_k[0][(k, S, hs)][C] += 1
                    c_given_k[1][(k, hs)][C] += 1
                    c_given_k[2][(k, hand)][C] += 1
                    c_given_k[3][(k, lang)][C] += 1
                    c_given_k[4][(k,)][C] += 1

                    if i > 0:
                        rp = ln[i - 1]
                        P1, S1, k1, m1, end1 = rp["P"], rp["S"], rp["k"], rp["m_tok"], rp["end_g"]

                        f_l2[0][(P1, S1, pos, hand)][F] += 1
                        f_l2[1][(P1, pos)][F] += 1

                        f_l3[0][(k1, P1, S1, pos, hand)][F] += 1
                        f_l3[1][(k1, S1, end1, pos, hand)][F] += 1
                        f_l3[2][(m1, P1, pos, hand)][F] += 1
                        f_l3[3][(P1, pos)][F] += 1

                        f_l4[0][(mL, k1, P1, S1, pos, hand)][F] += 1
                        f_l4[1][(mL, m1, P1, pos, hand)][F] += 1

                        k_given_f[0][(mL, F, k1, pos, hand)][k] += 1
                        k_given_f[1][(F, k1, pos, hand)][k] += 1

        self.t_l0 = [_compile_wb_table(t) for t in f_l0]
        self.t_l1 = [
            _compile_wb_table(f_l1[0], 0.25),
            _compile_wb_table(f_l1[1], 0.0),
            _compile_wb_table(f_l1[2], 0.0),
        ]
        self.t_l2 = [_compile_wb_table(f_l2[0], 1.4), _compile_wb_table(f_l2[1], 1.8)]
        self.t_l3 = [
            _compile_wb_table(f_l3[0], 1.3),
            _compile_wb_table(f_l3[1], 1.5),
            _compile_wb_table(f_l3[2], 1.6),
            _compile_wb_table(f_l3[3], 2.0),
        ]
        self.t_l4 = [
            _compile_wb_table(f_l4[0], 1.6),
            _compile_wb_table(f_l4[1], 1.8),
            _compile_wb_table(f_l4[2], 1.2),
        ]

        self.t_k_f = [_compile_wb_table(t) for t in k_given_f]
        # c_given_k[0] conditions only on (k, S, hs) with discount 4.5 (never seeing P_t), backing off to (k, pool)
        self.t_c_k = [
            _compile_wb_table(c_given_k[0], 4.5),
            _compile_wb_table(c_given_k[1], 1.0),
            _compile_wb_table(c_given_k[2], 1.0),
            _compile_wb_table(c_given_k[3], 1.0),
            _compile_wb_table(c_given_k[4], 1.0),
        ]

        self.lm_trans_hs = _compile_wb_table(self.line_mode_trans_hs)
        self.lm_trans_h = _compile_wb_table(self.line_mode_trans_h)
        self.lm_uni_hs = _compile_wb_table(self.line_mode_uni_hs)
        self.lm_uni_h = _compile_wb_table(self.line_mode_uni_h)

        # Fixed s56/s67 page-level core-recency kernel (d = 2..20, p_rep = 0.08, tau = 10.0)
        self.p_rep = 0.08
        self.kcum = []
        tot_k = 0.0
        for d in range(2, 21):
            tot_k += math.exp(-(d - 1) / 10.0)
            self.kcum.append(tot_k)

    def _sample_from_chain(self, rng: random.Random, chain: list[tuple[dict, tuple]], tmpl: dict | None = None):
        for tab, key in chain:
            e = tab.get(key)
            if e is None:
                continue
            ws, cum, lam = e
            if rng.random() < lam:
                if tmpl is not None and len(ws) > 1:
                    F_set = tmpl["F_set"]
                    P_set = tmpl["P_set"]
                    S_set = tmpl["S_set"]
                    wts = []
                    prev_c = 0
                    for f_val, c_val in zip(ws, cum):
                        cnt = c_val - prev_c
                        prev_c = c_val
                        mult = 1.0
                        if f_val in F_set:
                            mult += 2.0
                        elif f_val[0] in P_set:
                            mult += 0.8
                        if f_val[1] in S_set:
                            mult += 0.4
                        wts.append(cnt * mult)
                    tot_w = sum(wts)
                    u = rng.random() * tot_w
                    acc = 0.0
                    for f_val, w_i in zip(ws, wts):
                        acc += w_i
                        if u <= acc:
                            return f_val
                return _sample_cum(rng, ws, cum)
        ws, cum, _ = self.t_l0[2]["*"]
        return _sample_cum(rng, ws, cum)

    def _sample_core_class_and_core(
        self,
        rng: random.Random,
        rung: str,
        F: tuple[str, str],
        pos: str,
        hs: tuple[str, str],
        hand: str,
        lang: str,
        page_hist: list[tuple[int, str]],
        k_prev: int = -1,
        mL: int = -1,
        tmpl: dict | None = None,
    ) -> tuple[int, str]:
        # Step 1: Sample length-blind core class k_t given (F_t, k_{t-1}, pos, hand)
        if rung == "L4_line_mode_register":
            k_chain = []
            if k_prev >= 0:
                k_chain.append((self.t_k_f[0], (mL, F, k_prev, pos, hand)))
                k_chain.append((self.t_k_f[1], (F, k_prev, pos, hand)))
            k_chain.extend([
                (self.t_k_f[2], (F, pos, hand)),
                (self.t_k_f[3], (F,)),
                (self.t_k_f[4], (hand,)),
            ])
        elif rung == "L3_core_to_next_affix":
            k_chain = []
            if k_prev >= 0:
                k_chain.append((self.t_k_f[1], (F, k_prev, pos, hand)))
            k_chain.extend([
                (self.t_k_f[2], (F, pos, hand)),
                (self.t_k_f[3], (F,)),
                (self.t_k_f[4], (hand,)),
            ])
        elif rung == "L0_unigram":
            k_chain = [
                (self.t_k_f[3], (F,)),
                (self.t_k_f[4], (hand,)),
            ]
        else:
            k_chain = [
                (self.t_k_f[2], (F, pos, hand)),
                (self.t_k_f[3], (F,)),
                (self.t_k_f[4], (hand,)),
            ]

        k_t = None
        for tab, key in k_chain:
            e = tab.get(key)
            if e is None:
                continue
            ws, cum, lam = e
            if rng.random() < lam or tab is self.t_k_f[4]:
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
                    k_t = _sample_cum(rng, ws, cum)
                break
        if k_t is None:
            k_t = 0

        # Step 2: Page-level core recency (d in 2..20, never d=1 adjacent repeat) for class k_t
        prev_core = page_hist[-1][1] if page_hist else None
        if rung != "L0_unigram" and len(page_hist) >= 2 and rng.random() < self.p_rep:
            h_max = min(19, len(page_hist) - 1)
            d_idx = bisect.bisect_right(self.kcum[:h_max], rng.random() * self.kcum[h_max - 1])
            d = d_idx + 2
            cand_k, cand_c = page_hist[-d]
            if cand_k == k_t and cand_c != prev_core:
                return k_t, cand_c

        # Step 3: Draw core C_t compositionally (never conditioning on prefix P_t)
        S_sym = F[1]
        c_chain = []
        if self.hs_tok_counts[hs] >= 2200:
            c_chain.append((self.t_c_k[0], (k_t, S_sym, hs)))
            c_chain.append((self.t_c_k[1], (k_t, hs)))
        if self.h_tok_counts[hand] >= 2200:
            c_chain.append((self.t_c_k[2], (k_t, hand)))
        c_chain.append((self.t_c_k[3], (k_t, lang)))
        c_chain.append((self.t_c_k[4], (k_t,)))

        for _ in range(4):
            chosen = "daiin"
            for tab, key in c_chain:
                e = tab.get(key)
                if e is None:
                    continue
                ws, cum, lam = e
                if rng.random() < lam or tab is self.t_c_k[4]:
                    chosen = _sample_cum(rng, ws, cum)
                    break
            if rung == "L0_unigram" or prev_core is None or chosen != prev_core:
                return k_t, chosen
        return k_t, chosen

    def _sample_line_mode(self, rng: random.Random, hs: tuple[str, str], hand: str, lang: str, prev_mL: int) -> tuple[int, dict | None]:
        mL = None
        if prev_mL >= 0:
            for tab, k in [(self.lm_trans_hs, (hs, prev_mL)), (self.lm_trans_h, (hand, prev_mL))]:
                e = tab.get(k)
                if e is not None and rng.random() < e[2]:
                    mL = _sample_cum(rng, e[0], e[1])
                    break
        if mL is None:
            for tab, k in [(self.lm_uni_hs, hs), (self.lm_uni_h, hand)]:
                e = tab.get(k)
                if e is not None:
                    mL = _sample_cum(rng, e[0], e[1])
                    break
        if mL is None:
            mL = 0
        tmpls = (
            self.line_templates_hs.get((hs, mL))
            or self.line_templates_h.get((hand, mL))
            or self.line_templates_lang.get((lang, mL))
        )
        tmpl = rng.choice(tmpls) if tmpls else None
        return mL, tmpl

    def generate_pages(self, target_pages: list[dict], rung: str, seed: int) -> list[dict]:
        rng = random.Random(seed)
        out_pages = []
        for p in target_pages:
            hand = p["hand"]
            sec = p["section"]
            lang = p.get("lang", "A" if hand == "1" else "B")
            hs = (hand, sec)
            sim_lines = []
            page_hist: list[tuple[int, str]] = []
            prev_mL = -1
            for l_idx, ln in enumerate(p["lines"]):
                L = len(ln)
                mL, tmpl = (-1, None)
                if rung == "L4_line_mode_register":
                    mL, tmpl = self._sample_line_mode(rng, hs, hand, lang, prev_mL)
                    prev_mL = mL
                row = []
                P_prev, S_prev, k_prev, m_prev, end_prev = EMPTY, EMPTY, -1, 0, EMPTY
                for i in range(L):
                    pos = pos_5(l_idx, i, L)
                    l0_chain = [
                        (self.t_l0[0], hs),
                        (self.t_l0[1], hand),
                        (self.t_l0[2], "*"),
                    ]
                    l1_chain = [
                        (self.t_l1[0], (pos, hs)),
                        (self.t_l1[1], (pos, hand)),
                        (self.t_l1[2], (pos,)),
                    ] + l0_chain

                    if rung == "L0_unigram":
                        F = self._sample_from_chain(rng, l0_chain)
                    elif rung == "L1_pos_scribe":
                        F = self._sample_from_chain(rng, l1_chain)
                    elif rung == "L2_s69_affix_chain":
                        if i == 0:
                            F = self._sample_from_chain(rng, l1_chain)
                        else:
                            l2_chain = [
                                (self.t_l2[0], (P_prev, S_prev, pos, hand)),
                                (self.t_l2[1], (P_prev, pos)),
                            ] + l1_chain
                            F = self._sample_from_chain(rng, l2_chain)
                    elif rung == "L3_core_to_next_affix":
                        if i == 0:
                            F = self._sample_from_chain(rng, l1_chain)
                        else:
                            l3_chain = [
                                (self.t_l3[0], (k_prev, P_prev, S_prev, pos, hand)),
                                (self.t_l3[1], (k_prev, S_prev, end_prev, pos, hand)),
                                (self.t_l3[2], (m_prev, P_prev, pos, hand)),
                                (self.t_l3[3], (P_prev, pos)),
                            ] + l1_chain
                            F = self._sample_from_chain(rng, l3_chain)
                    elif rung == "L4_line_mode_register":
                        if i == 0:
                            F = self._sample_from_chain(rng, l1_chain, tmpl=None)
                        else:
                            l4_chain = [
                                (self.t_l4[0], (mL, k_prev, P_prev, S_prev, pos, hand)),
                                (self.t_l3[0], (k_prev, P_prev, S_prev, pos, hand)),
                                (self.t_l3[1], (k_prev, S_prev, end_prev, pos, hand)),
                                (self.t_l4[1], (mL, m_prev, P_prev, pos, hand)),
                                (self.t_l3[3], (P_prev, pos)),
                                (self.t_l4[2], (mL, pos, hand)),
                            ] + l1_chain
                            F = self._sample_from_chain(rng, l4_chain, tmpl=tmpl)
                    else:
                        F = self._sample_from_chain(rng, l1_chain)

                    P_sym, S_sym = F
                    pre_str = "" if P_sym == EMPTY else P_sym
                    suf_str = "" if S_sym == EMPTY else S_sym
                    k_cur, core_str = self._sample_core_class_and_core(
                        rng, rung, F, pos, hs, hand, lang, page_hist, k_prev=k_prev, mL=mL, tmpl=tmpl
                    )
                    w_str = pre_str + core_str + suf_str
                    if not w_str:
                        w_str = core_str or "daiin"
                    row.append(w_str)
                    page_hist.append((k_cur, core_str))

                    m_cur = self.mtok_map.get((P_sym, S_sym, k_cur), k_cur % K_STATE)
                    P_prev, S_prev, k_prev, m_prev, end_prev = P_sym, S_sym, k_cur, m_cur, w_str[-1]
                sim_lines.append(row)
            out_pages.append(dict(p, lines=sim_lines))
        return out_pages


# ==============================================================================
# PART 1 METRICS: MORAN I, BILINEAR COVARIANCE, S69 PREFIX GAIN, CHARWIN, JSD, A14
# ==============================================================================
class PrefixBigramScorer:
    """Exact s55/s57/s69 add-0.5 unigram and Witten-Bell bigram scorer for prefix stream."""

    def __init__(self, train_pages: list[dict], seg: SlotSegmenter):
        self.seg = seg
        self.uni = Counter()
        self.big: dict[str, Counter] = defaultdict(Counter)
        for p in train_pages:
            for ln in p["lines"]:
                ps = [seg.segment(w)[0] or EMPTY for w in ln]
                for x in ps:
                    self.uni[x] += 1
                for a, b in zip(ps[:-1], ps[1:]):
                    self.big[a][b] += 1
        self.N = sum(self.uni.values())
        self.V = len(self.uni)
        self.tot = {a: sum(c.values()) for a, c in self.big.items()}

    def pu(self, b: str) -> float:
        return (self.uni.get(b, 0) + 0.5) / (self.N + 0.5 * (self.V + 1))

    def pb(self, a: str, b: str) -> float:
        c = self.big.get(a)
        if not c:
            return self.pu(b)
        T = len(c)
        return (c.get(b, 0) + T * self.pu(b)) / (self.tot[a] + T)

    def score_pages(self, pages: list[dict]) -> float:
        u_bits, b_bits, n = 0.0, 0.0, 0
        for p in pages:
            for ln in p["lines"]:
                if len(ln) < 2:
                    continue
                ps = [self.seg.segment(w)[0] or EMPTY for w in ln]
                for a, b in zip(ps[:-1], ps[1:]):
                    u_bits -= math.log2(self.pu(b))
                    b_bits -= math.log2(self.pb(a, b))
                    n += 1
        return (u_bits - b_bits) / max(1, n)


def mi_codes(a: np.ndarray, b: np.ndarray) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    kb = int(b.max()) + 1
    j, cj = np.unique(a.astype(np.int64) * kb + b, return_counts=True)
    ca = np.bincount(a)
    cb = np.bincount(b)
    ja, jb = j // kb, j % kb
    p = cj / n
    return float(np.sum(p * np.log2(cj * n / (ca[ja].astype(np.float64) * cb[jb]))))


def evaluate_part1_pages(
    pages: list[dict],
    seg: SlotSegmenter,
    p_scorer: PrefixBigramScorer,
    cm3: CharMarkov,
    ug_rn: M3.UnigramGTRenorm,
    n_shuf: int = N_SHUF_MORAN,
    seed: int = SEED,
) -> dict[str, float]:
    """Computes full Part 1 battery on a 41-page held-out (or simulated held-out) set."""
    rng = np.random.default_rng(seed)
    w_len, p_len, c_len, s_len, a_len = [], [], [], [], []
    lid, pid, cid = [], [], []
    core_map: dict[str, int] = {}
    first_g, last_g = [], []
    g_map: dict[str, int] = {}

    line_counter = 0
    for p_i, p in enumerate(pages):
        for ln in p["lines"]:
            if not ln:
                continue
            for w in ln:
                pr, co, su = seg.segment(w)
                lw, lp, lc, ls = len(w), len(pr), len(co), len(su)
                w_len.append(lw)
                p_len.append(lp)
                c_len.append(lc)
                s_len.append(ls)
                a_len.append(lp + ls)
                lid.append(line_counter)
                pid.append(p_i)
                cid.append(core_map.setdefault(co, len(core_map)))
                first_g.append(g_map.setdefault(w[0], len(g_map)))
                last_g.append(g_map.setdefault(w[-1], len(g_map)))
            line_counter += 1

    xw = np.array(w_len, dtype=np.float64)
    xp = np.array(p_len, dtype=np.float64)
    xc = np.array(c_len, dtype=np.float64)
    xs = np.array(s_len, dtype=np.float64)
    xa = np.array(a_len, dtype=np.float64)
    lid_a = np.array(lid, dtype=np.int64)
    pid_a = np.array(pid, dtype=np.int64)
    cid_a = np.array(cid, dtype=np.int64)
    fg_a = np.array(first_g, dtype=np.int64)
    lg_a = np.array(last_g, dtype=np.int64)

    left = np.nonzero(lid_a[1:] == lid_a[:-1])[0]
    right = left + 1
    N = len(xw)
    M = len(left)

    zw = xw - xw.mean()
    denom = float(np.dot(zw, zw))
    scale = (N / M / denom) if (denom > 0 and M > 0) else 0.0
    I_within = float(scale * np.dot(zw[left], zw[right]))

    zp, zc, zs, za = xp - xp.mean(), xc - xc.mean(), xs - xs.mean(), xa - xa.mean()

    def pair_cov(za_v: np.ndarray, zb_v: np.ndarray, perm: np.ndarray | None = None) -> float:
        if perm is None:
            return float(np.mean(za_v[left] * zb_v[right]))
        return float(np.mean(za_v[perm[left]] * zb_v[perm[right]]))

    obs_ww = pair_cov(zw, zw)
    obs_aa = pair_cov(za, za)
    obs_ca = pair_cov(zc, za)
    obs_ac = pair_cov(za, zc)
    obs_cc = pair_cov(zc, zc)
    obs_cp = pair_cov(zc, zp)
    obs_cs = pair_cov(zc, zs)

    null_I = np.empty(n_shuf, dtype=np.float64)
    null_page_I = np.empty(min(60, n_shuf), dtype=np.float64)
    sh_ww, sh_aa, sh_ca, sh_ac, sh_cc, sh_cp, sh_cs = [], [], [], [], [], [], []
    sh_core_mi = []
    sh_edge_mi = []

    obs_core_mi = mi_codes(cid_a[left], cid_a[right])
    obs_edge_mi = mi_codes(lg_a[left], fg_a[right])

    for b in range(n_shuf):
        perm = np.lexsort((rng.random(N), lid_a))
        null_I[b] = float(scale * np.dot(zw[perm[left]], zw[perm[right]]))
        sh_ww.append(pair_cov(zw, zw, perm))
        sh_aa.append(pair_cov(za, za, perm))
        sh_ca.append(pair_cov(zc, za, perm))
        sh_ac.append(pair_cov(za, zc, perm))
        sh_cc.append(pair_cov(zc, zc, perm))
        sh_cp.append(pair_cov(zc, zp, perm))
        sh_cs.append(pair_cov(zc, zs, perm))
        if b < len(null_page_I):
            p_pg = np.lexsort((rng.random(N), pid_a))
            null_page_I[b] = float(scale * np.dot(zw[p_pg[left]], zw[p_pg[right]]))
            sh_core_mi.append(mi_codes(cid_a[perm[left]], cid_a[perm[right]]))
            sh_edge_mi.append(mi_codes(lg_a[perm[left]], fg_a[perm[right]]))

    null_med = float(np.median(null_I))
    null_mean = float(np.mean(null_I))
    page_shuf_med = float(np.median(null_page_I))
    within_ac = float(np.mean(za * zc))

    pgain_ext = p_scorer.score_pages(pages)
    all_words = [w for p in pages for ln in p["lines"] for w in ln]
    rn_bits = -sum(ug_rn.logp_word(w) for w in all_words) / max(1, len(all_words))
    wb_bits = -sum(cm3.logp_word(w) for w in all_words) / max(1, len(all_words))
    charwin = rn_bits - wb_bits

    lines_ge3 = [ln for p in pages for ln in p["lines"] if len(ln) >= 3]
    jsd_first = float(A2.stats(lines_ge3, lambda w: w[0])[0]) if lines_ge3 else 0.0

    return dict(
        I_within=I_within,
        null_med=null_med,
        null_mean=null_mean,
        page_shuf_med=page_shuf_med,
        I_excess=I_within - null_med,
        d_ww=obs_ww - float(np.mean(sh_ww)),
        d_aa=obs_aa - float(np.mean(sh_aa)),
        d_ca=obs_ca - float(np.mean(sh_ca)),
        d_ac=obs_ac - float(np.mean(sh_ac)),
        d_cc=obs_cc - float(np.mean(sh_cc)),
        d_cp=obs_cp - float(np.mean(sh_cp)),
        d_cs=obs_cs - float(np.mean(sh_cs)),
        within_ac=within_ac,
        pgain=pgain_ext,
        charwin=charwin,
        jsd_first=jsd_first,
        cross_ex=obs_edge_mi - float(np.mean(sh_edge_mi)),
        core_core=obs_core_mi - float(np.mean(sh_core_mi)),
        types=float(len(set(all_words))),
        tokens=float(len(all_words)),
    )


# ==============================================================================
# PART 2: PHONOTACTIC / GRAPHICAL vs. METRIC HANDSHAKE TEST FOR Cov(|C1|, |P2|)
# ==============================================================================
def core_family_label(c: str) -> str:
    if not c or c == EMPTY:
        return "5_empty"
    if "cth" in c or "ckh" in c or "cph" in c or "cfh" in c:
        return "1_bench_gallows(cth/ckh)"
    if "ee" in c or "ai" in c:
        return "2_double_vowel(ee/ai)"
    if any(g in c for g in "ktpf"):
        return "3_single_gallows(k/t/p/f)"
    if "ch" in c or "sh" in c:
        return "4_bench_ch_sh"
    return "5_minim_vowel_short"


def run_part2_handshake_test(
    tr_name: str,
    pages: list[dict],
    split_label: str,
    seg: SlotSegmenter,
    cls_map: dict[str, int],
    C_gf: np.ndarray,
) -> dict:
    """Tests Hypothesis H_graphical vs. Residual Metric Coupling for Cov(|C_{t-1}|, |P_t|)
    on either the 166 training pages or 41 held-out pages."""
    pair_c1_len = []
    pair_p2_len = []
    pair_s1_len = []
    pair_p1_len = []
    cells_by_name: dict[str, list[tuple]] = defaultdict(list)
    fam_stats: dict[str, list[tuple[int, int, int, str, str]]] = defaultdict(list)

    all_c_len, all_p_len, all_s_len, all_lid = [], [], [], []
    lid_cnt = 0

    for p in pages:
        hand = p["hand"]
        for l_idx, ln in enumerate(p["lines"]):
            L = len(ln)
            if L < 2:
                continue
            pcs = [seg.segment(w) for w in ln]
            for i, (w, (pr, co, su)) in enumerate(zip(ln, pcs)):
                P = pr or EMPTY
                C = co or EMPTY
                S = su or EMPTY
                all_c_len.append(len(co))
                all_p_len.append(len(pr))
                all_s_len.append(len(su))
                all_lid.append(lid_cnt)
                if i + 1 < L:
                    pr2, co2, su2 = pcs[i + 1]
                    P2 = pr2 or EMPTY
                    pos1 = pos_5(l_idx, i, L)
                    last_g = w[-1]
                    first_c = C[0] if C != EMPTY else EMPTY
                    fam = core_family_label(C)
                    k_c = get_core_class(C, cls_map, C_gf)

                    c1_l = len(co)
                    p2_l = len(pr2)
                    pair_c1_len.append(c1_l)
                    pair_p2_len.append(p2_l)
                    pair_s1_len.append(len(su))
                    pair_p1_len.append(len(pr))

                    cells_by_name["Z0_hand_pos"].append((hand, pos1))
                    cells_by_name["Z1_prev_affix"].append((hand, pos1, P, S))
                    cells_by_name["Z2_graphical_edge"].append((hand, pos1, S, last_g))
                    cells_by_name["Z3_full_graphical"].append((hand, pos1, P, S, last_g, first_c, fam))
                    cells_by_name["Z4_core_class_K20"].append((hand, pos1, P, S, k_c))
                    cells_by_name["Z5_s69_triplet"].append((hand, pos1, P, S, P2))

                    fam_stats[fam].append((c1_l, len(su), p2_l, S, P2))
            lid_cnt += 1

    c1 = np.array(pair_c1_len, dtype=np.float64)
    p2 = np.array(pair_p2_len, dtype=np.float64)
    s1 = np.array(pair_s1_len, dtype=np.float64)
    p1 = np.array(pair_p1_len, dtype=np.float64)
    M = len(c1)

    zc1 = c1 - c1.mean()
    zp2 = p2 - p2.mean()
    raw_cov = float(np.mean(zc1 * zp2))
    within_c1_s1 = float(np.mean((c1 - c1.mean()) * (s1 - s1.mean())))
    within_c1_p1 = float(np.mean((c1 - c1.mean()) * (p1 - p1.mean())))

    xc_all = np.array(all_c_len, dtype=np.float64)
    xp_all = np.array(all_p_len, dtype=np.float64)
    lid_arr = np.array(all_lid, dtype=np.int64)
    left = np.nonzero(lid_arr[1:] == lid_arr[:-1])[0]
    right = left + 1
    rng = np.random.default_rng(SEED)
    shuf_covs = np.empty(N_SHUF_CELL, dtype=np.float64)
    for b in range(N_SHUF_CELL):
        perm = np.lexsort((rng.random(len(xc_all)), lid_arr))
        ca_s = xc_all[perm[left]]
        pb_s = xp_all[perm[right]]
        shuf_covs[b] = float(np.mean((ca_s - ca_s.mean()) * (pb_s - pb_s.mean())))
    shuf_mean = float(np.mean(shuf_covs))
    shuf_sd = float(np.std(shuf_covs))
    dcov_obs = raw_cov - shuf_mean
    z_obs = dcov_obs / max(1e-12, shuf_sd)

    emit(
        f"  [{tr_name} {split_label} (pairs={M})]: Raw Cov(|C1|,|P2|)={raw_cov:+.5f}, LineShuf={shuf_mean:+.5f} +/- {shuf_sd:.5f}, "
        f"dCov(|C1|,|P2|)={dcov_obs:+.5f} (z={z_obs:+.2f}) | Within-word Cov(|C1|,|P1|)={within_c1_p1:+.4f}, Cov(|C1|,|S1|)={within_c1_s1:+.4f}"
    )
    emit(
        f"    {'Conditioning Cell Z (strictly length-blind)':42} | {'nCells':>6} | {'Cov_Expl':>9} {'%Raw_Ex':>8} | "
        f"{'dCov_Expl':>9} {'%dCov_Ex':>8} | {'Resid_Cov':>9} {'z_res':>6} {'p_res':>6}"
    )

    cell_results = {}
    for z_name in [
        "Z0_hand_pos",
        "Z1_prev_affix",
        "Z2_graphical_edge",
        "Z3_full_graphical",
        "Z4_core_class_K20",
        "Z5_s69_triplet",
    ]:
        keys = cells_by_name[z_name]
        u_map: dict[tuple, int] = {}
        z_idx = np.array([u_map.setdefault(k, len(u_map)) for k in keys], dtype=np.int64)
        n_cells = len(u_map)

        counts = np.bincount(z_idx, minlength=n_cells).astype(np.float64)
        sums_c1 = np.bincount(z_idx, weights=c1, minlength=n_cells)
        mean_c1_z = sums_c1 / np.maximum(1.0, counts)
        e_c1 = mean_c1_z[z_idx]

        cov_expl_ana = float(np.mean((e_c1 - c1.mean()) * zp2))
        resid_cov = raw_cov - cov_expl_ana

        perm_covs = np.empty(N_SHUF_CELL, dtype=np.float64)
        for b in range(N_SHUF_CELL):
            p_in_z = np.lexsort((rng.random(M), z_idx))
            c1_sh = c1[p_in_z]
            perm_covs[b] = float(np.mean((c1_sh - c1.mean()) * zp2))
        perm_mean = float(np.mean(perm_covs))
        perm_sd = float(np.std(perm_covs))
        z_res = (raw_cov - perm_mean) / max(1e-12, perm_sd)
        p_res = (1 + int(np.sum(np.abs(perm_covs - perm_mean) >= abs(raw_cov - perm_mean)))) / (N_SHUF_CELL + 1)

        dcov_expl = cov_expl_ana - shuf_mean
        pct_raw = 100.0 * cov_expl_ana / raw_cov if abs(raw_cov) > 1e-9 else 0.0
        pct_dcov = 100.0 * dcov_expl / dcov_obs if abs(dcov_obs) > 1e-9 else 0.0

        emit(
            f"    {z_name:42} | {n_cells:6d} | {cov_expl_ana:+9.5f} {pct_raw:7.1f}% | "
            f"{dcov_expl:+9.5f} {pct_dcov:7.1f}% | {resid_cov:+9.5f} {z_res:+6.2f} {p_res:6.3f}"
        )
        cell_results[z_name] = dict(
            n_cells=n_cells,
            cov_expl=cov_expl_ana,
            pct_raw=pct_raw,
            dcov_expl=dcov_expl,
            pct_dcov=pct_dcov,
            resid_cov=resid_cov,
            z_res=z_res,
            p_res=p_res,
        )

    if split_label == "Train166":
        emit(f"    --- {tr_name} Core-Family Handshake Anatomy (Train166) ---")
        for fam in sorted(fam_stats.keys()):
            rows = fam_stats[fam]
            if not rows:
                continue
            n_f = len(rows)
            m_c1 = float(np.mean([r[0] for r in rows]))
            m_s1 = float(np.mean([r[1] for r in rows]))
            m_p2 = float(np.mean([r[2] for r in rows]))
            s_empty = 100.0 * sum(1 for r in rows if r[3] == EMPTY) / n_f
            p2_long = 100.0 * sum(1 for r in rows if r[2] >= 2) / n_f
            p2_empty = 100.0 * sum(1 for r in rows if r[4] == EMPTY) / n_f
            emit(
                f"      {fam:26} (n={n_f:5d}, {100*n_f/M:4.1f}%): E[|C1|]={m_c1:.2f}, E[|S1|]={m_s1:.2f} (S1=∅:{s_empty:4.1f}%) "
                f"-> E[|P2|]={m_p2:.2f} (|P2|>=2:{p2_long:4.1f}%, P2=∅:{p2_empty:4.1f}%)"
            )
    return dict(raw_cov=raw_cov, dcov_obs=dcov_obs, cells=cell_results)


# ==============================================================================
# PART 3: FAST 15-QUIRE LEAVE-ONE-QUIRE-OUT (LOQO) SCORER (EXACT S57/S67 RULES)
# ==============================================================================
class FastFoldEvaluator:
    """Scores a held-out quire (real or generated) on s67's exact 6 LOQO predictions (P1, P2, P3, P4, P5, P7)."""

    def __init__(
        self,
        test_pages: list[dict],
        seg: SlotSegmenter,
        p_scorer: PrefixBigramScorer,
        cm3: CharMarkov,
        ug_rn: M3.UnigramGTRenorm,
        seed_offset: int = 0,
    ):
        self.n_test = len(test_pages)
        self.pages_data = []
        self.gain_rows = np.zeros((self.n_test, 3), dtype=np.float64)
        core_id: dict[str, int] = {}

        all_words = []
        all_lines_ge3 = []
        for k, p in enumerate(test_pages):
            lens, lid, cores = [], [], []
            for li, ln in enumerate(p["lines"]):
                if len(ln) >= 3:
                    all_lines_ge3.append(ln)
                ps = [seg.segment(w)[0] or EMPTY for w in ln]
                for a, b in zip(ps[:-1], ps[1:]):
                    self.gain_rows[k] += (1.0, -math.log2(p_scorer.pu(b)), -math.log2(p_scorer.pb(a, b)))
                for w in ln:
                    all_words.append(w)
                    lens.append(len(w))
                    lid.append(li)
                    cores.append(core_id.setdefault(seg.segment(w)[1], len(core_id)))
            self.pages_data.append(dict(
                x=np.array(lens, dtype=np.float64),
                lid=np.array(lid, dtype=np.int64),
                c=np.array(cores, dtype=np.int64),
            ))

        self.all_words = all_words
        self.jsd = float(A2.stats(all_lines_ge3, lambda w: w[0])[0]) if all_lines_ge3 else 0.0
        rn_bits = -sum(ug_rn.logp_word(w) for w in all_words) / max(1, len(all_words))
        wb_bits = -sum(cm3.logp_word(w) for w in all_words) / max(1, len(all_words))
        self.charwin = rn_bits - wb_bits
        self.p2_point = self.core_core(np.arange(self.n_test), 20, np.random.default_rng(SEED + seed_offset))

    def concat(self, idx: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        xs, ls, cs, off = [], [], [], 0
        for i in idx:
            pg = self.pages_data[int(i)]
            xs.append(pg["x"])
            cs.append(pg["c"])
            ls.append(pg["lid"] + off)
            off += int(pg["lid"].max()) + 1 if len(pg["lid"]) else 0
        return np.concatenate(xs), np.concatenate(ls), np.concatenate(cs)

    def moran(self, idx: np.ndarray) -> float:
        x, lid, _ = self.concat(idx)
        left = np.nonzero(lid[1:] == lid[:-1])[0]
        z = x - x.mean()
        d = float(np.dot(z, z))
        return float(len(x) / len(left) * np.dot(z[left], z[left + 1]) / d) if d > 0 and len(left) else 0.0

    def core_core(self, idx: np.ndarray, n_shuf: int, rng: np.random.Generator) -> float:
        _, lid, c = self.concat(idx)
        left = np.nonzero(lid[1:] == lid[:-1])[0]
        if len(left) == 0:
            return 0.0
        right = left + 1
        obs = mi_codes(c[left], c[right])
        nulls = np.empty(n_shuf, dtype=np.float64)
        for b in range(n_shuf):
            perm = np.lexsort((rng.random(len(c)), lid))
            y = c[perm]
            nulls[b] = mi_codes(y[left], y[right])
        return obs - float(np.mean(nulls))

    def gain_stat(self, idx: np.ndarray) -> float:
        s = self.gain_rows[idx].sum(axis=0)
        return float((s[1] - s[2]) / s[0]) if s[0] > 0 else 0.0

    def point(self) -> dict[str, float]:
        a = np.arange(self.n_test)
        return dict(
            P1=self.moran(a),
            P2=self.p2_point,
            P3=self.gain_stat(a),
            P4=self.jsd,
            P5=self.charwin,
        )


def subsample_draws(evals: list[FastFoldEvaluator], seed: int, n_draw: int = N_DRAW_LOQO) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_test = evals[0].n_test
    k = max(1, int(round(0.8 * n_test)))
    out = {key: np.zeros(n_draw, dtype=np.float64) for key in ("P1", "P2", "P3")}
    for b in range(n_draw):
        p1_l, p2_l, p3_l = [], [], []
        for ev in evals:
            idx = rng.choice(n_test, size=k, replace=False)
            p1_l.append(ev.moran(idx))
            p2_l.append(ev.core_core(idx, 2, rng))
            p3_l.append(ev.gain_stat(idx))
        out["P1"][b] = float(np.mean(p1_l))
        out["P2"][b] = float(np.mean(p2_l))
        out["P3"][b] = float(np.mean(p3_l))
    return out


def pct_95(a: np.ndarray) -> tuple[float, float]:
    return float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))


def score_loqo_fold(
    real_pt: dict[str, float],
    real_dr: dict[str, np.ndarray],
    gen_evals: list[FastFoldEvaluator],
    gen_dr: dict[str, np.ndarray],
    real_words: list[str],
    n_test: int,
) -> dict:
    pts = [ev.point() for ev in gen_evals]
    gen_pt = {k: float(np.mean([p[k] for p in pts])) for k in pts[0]}
    small = n_test < SMALL_FOLD

    holds = {}
    if small:
        holds["P1"] = (gen_pt["P1"] - real_pt["P1"]) >= -TOL_SMALL["P1"]
        holds["P2"] = abs(gen_pt["P2"] - real_pt["P2"]) <= TOL_SMALL["P2"]
        holds["P3"] = abs(gen_pt["P3"] - real_pt["P3"]) <= TOL_SMALL["P3"]
    else:
        lo1, hi1 = pct_95(gen_dr["P1"] - real_dr["P1"])
        holds["P1"] = hi1 >= 0.0
        lo2, hi2 = pct_95(gen_dr["P2"] - real_dr["P2"])
        holds["P2"] = (lo2 <= 0.0 <= hi2)
        lo3, hi3 = pct_95(real_dr["P3"])
        holds["P3"] = (lo3 <= gen_pt["P3"] <= hi3)

    holds["P4"] = (S15_JSD[0] <= gen_pt["P4"] <= S15_JSD[1])
    holds["P5"] = (gen_pt["P5"] > 0.0)

    ratios = []
    for ev in gen_evals:
        n_m = min(len(ev.all_words), len(real_words))
        vg = len(set(ev.all_words[:n_m]))
        vr = len(set(real_words[:n_m]))
        ratios.append(vg / max(1, vr))
    rt = float(np.mean(ratios))
    holds["P7"] = (abs(rt - 1.0) <= TYPE_TOL)
    n_holds = sum(1 for k in PREDS if holds[k])
    return dict(n=n_holds, holds=holds, gen_pt=gen_pt, type_ratio=rt, small=small)


# ==============================================================================
# SYNTHETIC FIXTURE (--fixture, pre-freeze verification with no real data read)
# ==============================================================================
def run_fixture() -> bool:
    rng = random.Random(42)
    pres = ["", "qo", "ch", "sh", "o", "a", "d", "y"]
    sufs = ["", "edy", "aiin", "ar", "or", "y", "ol", "s"]
    cores = ["cth", "ckh", "eedy", "keey", "k", "t", "d", "l", "r", "o", "a", "aiin", "ol", "ch"]
    pages = []
    for i in range(24):
        hand = "1" if i < 12 else "2"
        sec = "H" if i < 12 else "B"
        quire = "A" if i < 8 else ("B" if i < 16 else "M")
        lines = []
        for _ in range(6):
            L = rng.randint(5, 9)
            ln = [rng.choice(pres) + rng.choice(cores) + rng.choice(sufs) for _ in range(L)]
            lines.append(ln)
        pages.append(dict(id=f"f{i+1}r", hand=hand, section=sec, quire=quire, lang="A" if hand == "1" else "B", lines=lines))
    train_p, test_p = pages[:18], pages[18:]
    tr_toks = [w for p in train_p for ln in p["lines"] for w in ln]
    seg = make_cached_segmenter(tr_toks)
    auto = LengthBlindLineAutomaton(train_p, seg)
    p_sc = PrefixBigramScorer(train_p, seg)
    cm3 = CharMarkov(tr_toks, 3)
    ug_rn = M3.UnigramGTRenorm(tr_toks, cm3)
    for rung in ["L0_unigram", "L1_pos_scribe", "L2_s69_affix_chain", "L3_core_to_next_affix", "L4_line_mode_register"]:
        sim = auto.generate_pages(test_p, rung, seed=101)
        res = evaluate_part1_pages(sim, seg, p_sc, cm3, ug_rn, n_shuf=20, seed=101)
        assert not math.isnan(res["I_within"])
    ev_r = FastFoldEvaluator(test_p, seg, p_sc, cm3, ug_rn, seed_offset=1)
    dr_r = subsample_draws([ev_r], SEED, n_draw=10)
    sc = score_loqo_fold(ev_r.point(), dr_r, [ev_r], dr_r, [w for p in test_p for ln in p["lines"] for w in ln], len(test_p))
    assert "holds" in sc and len(sc["holds"]) == 6
    print("FIXTURE PASS", flush=True)
    return True


# ==============================================================================
# MAIN EXECUTION (PARTS 1, 2, AND 3 ACROSS ZL3b, RF1b, IT2a)
# ==============================================================================
def main() -> None:
    emit("==========================================================================================================")
    emit("S74: Length-Blind Cadence Prediction & Line Automaton Investigator (Closing CONSTRAINTS-MAP §C & O-043)")
    emit("==========================================================================================================")
    emit(f"date: {clock()}")
    emit(f"sha256 s74_cadence_prediction_and_line_automaton.py: {sha256(SELF)}")
    emit(f"sha256 s74_cadence_prediction_and_line_automaton.prereg.sha256: {sha256(STUB) if STUB.exists() else 'MISSING'}")
    emit(f"stub_match: {stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(
        f"params: SEED={SEED}, K_CORE={K_CORE}, K_STATE={K_STATE}, M_LINE={M_LINE}, "
        f"N_SEEDS_P1={N_SEEDS_P1}, N_SHUF_MORAN={N_SHUF_MORAN}, N_SHUF_CELL={N_SHUF_CELL}, N_DRAW_LOQO={N_DRAW_LOQO}"
    )
    emit("STRICT LENGTH-BLINDNESS GUARANTEE: All rungs L0..L4 fit 0 length parameters and never inspect |w|, |c|, |p|, or |s|.")
    emit("")

    inv = load_folio_inventory()
    translit_data = {}
    for tr_name, stem in TRANSLITS.items():
        pages, by_page, h_meta = load_translit_pages(stem, inv)
        train_ids, test_ids = G1.split_names(by_page)
        id2p = {p["id"]: p for p in pages}
        train_p = [id2p[pid] for pid in train_ids if pid in id2p]
        test_p = [id2p[pid] for pid in test_ids if pid in id2p]
        tr_toks = [w for p in train_p for ln in p["lines"] for w in ln]
        seg = make_cached_segmenter(tr_toks)
        translit_data[tr_name] = dict(
            pages=pages,
            by_page=by_page,
            h_meta=h_meta,
            train_p=train_p,
            test_p=test_p,
            tr_toks=tr_toks,
            seg=seg,
        )
        emit(
            f"Loaded {tr_name} ({stem}.meta.json sha256={h_meta}): total={len(pages)}p, "
            f"train={len(train_p)}p ({len(tr_toks)} tok), held-out={len(test_p)}p "
            f"({sum(len(ln) for p in test_p for ln in p['lines'])} tok), "
            f"SlotSegmenter={len(seg.prefixes)}P/{len(seg.suffixes)}S"
        )
    emit("")

    # ==========================================================================
    # PART 1: EXACT DECOMPOSITION OF I_within ON 41 HELD-OUT PAGES (L0..L4)
    # ==========================================================================
    emit("==========================================================================================================")
    emit("PART 1: STRICTLY LENGTH-BLIND MORPHOLOGICAL AUTOMATON LADDER (L0..L4) ON 41 HELD-OUT PAGES (166 -> 41)")
    emit("==========================================================================================================")
    rungs = [
        "L0_unigram",
        "L1_pos_scribe",
        "L2_s69_affix_chain",
        "L3_core_to_next_affix",
        "L4_line_mode_register",
    ]
    part1_summary = {}

    for tr_name, td in translit_data.items():
        t_p1 = time.time()
        train_p, test_p, seg, tr_toks = td["train_p"], td["test_p"], td["seg"], td["tr_toks"]
        auto = LengthBlindLineAutomaton(train_p, seg)
        td["auto_166"] = auto
        p_scorer = PrefixBigramScorer(train_p, seg)
        cm3 = CharMarkov(tr_toks, 3)
        ug_rn = M3.UnigramGTRenorm(tr_toks, cm3)

        real_res = evaluate_part1_pages(test_p, seg, p_scorer, cm3, ug_rn, n_shuf=N_SHUF_MORAN, seed=SEED)
        between_page_drift = real_res["page_shuf_med"]
        between_line_drift = real_res["null_med"] - real_res["page_shuf_med"]

        emit(f"--- PART 1 [{tr_name}] Held-Out 41 Pages Baseline Decomposition ---")
        emit(
            f"  Real_HO41 Total I_within = {real_res['I_within']:+.4f} = "
            f"Page/Hand Mean Drift ({between_page_drift:+.4f}, {100*between_page_drift/real_res['I_within']:.1f}%) + "
            f"Within-Page Line-Mode Drift ({between_line_drift:+.4f}, {100*between_line_drift/real_res['I_within']:.1f}%) "
            f"[Total Line-Shuf null_med = {real_res['null_med']:+.4f}, {100*real_res['null_med']/real_res['I_within']:.1f}%] + "
            f"Intra-Line Sequential Excess ({real_res['I_excess']:+.4f}, {100*real_res['I_excess']/real_res['I_within']:.1f}%)"
        )
        emit(
            f"  {'Rung / Model (0 len params)':24} | {'I_within':>8} {'null_med':>8} {'I_excess':>8} {'%Real_I':>7} {'%Ex_I':>6} | "
            f"{'dCov(w,w)':>9} {'dCov(A,A)':>9} {'dCov(C,A)':>9} {'[C->P/C->S]':>15} {'dCov(A,C)':>9} {'dCov(C,C)':>9} {'Cov(A,C)':>8} | "
            f"{'M1_pgain':>8} {'CHARWIN':>8} {'jsd_1st':>7} {'cross_ex':>8} {'A14_c->c':>8} {'types':>5}"
        )

        def fmt_row(label: str, r: dict[str, float]) -> None:
            pct_I = 100.0 * r["I_within"] / real_res["I_within"] if real_res["I_within"] else 0.0
            pct_ex = 100.0 * r["I_excess"] / real_res["I_excess"] if real_res["I_excess"] else 0.0
            cp_cs = f"{r['d_cp']:+.3f}/{r['d_cs']:+.3f}"
            emit(
                f"  {label:24} | {r['I_within']:+8.4f} {r['null_med']:+8.4f} {r['I_excess']:+8.4f} {pct_I:6.1f}% {pct_ex:5.1f}% | "
                f"{r['d_ww']:+9.4f} {r['d_aa']:+9.4f} {r['d_ca']:+9.4f} {cp_cs:>15} {r['d_ac']:+9.4f} {r['d_cc']:+9.4f} {r['within_ac']:+8.4f} | "
                f"{r['pgain']:+8.4f} {r['charwin']:+8.4f} {r['jsd_first']:7.4f} {r['cross_ex']:+8.4f} {r['core_core']:+8.4f} {r['types']:5.0f}"
            )

        fmt_row("Real_HO41 (observed)", real_res)
        part1_summary[tr_name] = {"Real_HO41": real_res}

        for rung in rungs:
            seed_runs = []
            for s_i in range(1, N_SEEDS_P1 + 1):
                sim_p = auto.generate_pages(test_p, rung, seed=SEED + 100 * s_i)
                seed_runs.append(evaluate_part1_pages(sim_p, seg, p_scorer, cm3, ug_rn, n_shuf=60, seed=SEED + s_i))
            avg_r = {k: float(np.mean([sr[k] for sr in seed_runs])) for k in seed_runs[0]}
            part1_summary[tr_name][rung] = avg_r
            fmt_row(rung, avg_r)

        emit(f"  [{tr_name} Part 1 completed in {time.time() - t_p1:.1f}s]")
        emit("")
        flush_output()

    # ==========================================================================
    # PART 2: WHY DOES Cov(|C_{t-1}|, |P_t|) EQUAL +28.0% OF INTRA-LINE COVARIANCE?
    # ==========================================================================
    emit("==========================================================================================================")
    emit("PART 2: PHONOTACTIC / GRAPHICAL vs. METRIC HANDSHAKE TEST FOR Cov(|C_{t-1}|, |P_t|) (166 TRAIN & 41 HO)")
    emit("==========================================================================================================")
    part2_summary = {}
    for tr_name, td in translit_data.items():
        auto = td["auto_166"]
        seg = td["seg"]
        r_tr = run_part2_handshake_test(tr_name, td["train_p"], "Train166", seg, auto.cls_map, auto.C_gf)
        r_ho = run_part2_handshake_test(tr_name, td["test_p"], "HeldOut41", seg, auto.cls_map, auto.C_gf)
        part2_summary[tr_name] = dict(train=r_tr, ho=r_ho)
        emit("")
        flush_output()

    # ==========================================================================
    # PART 3: 15-QUIRE LEAVE-ONE-QUIRE-OUT (LOQO) OF L3 & L4 vs. s67 (CA & CA0)
    # ==========================================================================
    emit("==========================================================================================================")
    emit("PART 3: 15-QUIRE LEAVE-ONE-QUIRE-OUT (LOQO) OF ZERO-LENGTH-PARAM L3 & L4 vs. s67 (CA & CA0)")
    emit("==========================================================================================================")

    s67_cells_path = ROOT / "runs" / "s67" / "cells.json"
    s67_ref = json.loads(s67_cells_path.read_text(encoding="utf-8")) if s67_cells_path.exists() else {}

    zl_quire_counts = Counter(p["quire"] for p in translit_data["ZL3b"]["pages"])
    folds = [q for q in sorted(zl_quire_counts.keys()) if zl_quire_counts[q] >= 4 and q != "?"]
    emit(f"LOQO Folds ({len(folds)} quires with >= 4 pages in ZL3b): {folds}")
    emit("Models evaluated on each fold (seeds 1, 2; 0 fitted length parameters):")
    emit("  - L3_core_to_next_affix : (Hand, Section)->Hand->Lang pool + K(C_{t-1})->(P_t,S_t) + s69 P_{t-1}->P_t + 5-slot pos")
    emit("  - L4_line_mode_register : L3 + 6-state length-blind line-mode register m_L & training-line slot palette")
    emit("")

    loqo_models = ["L3_core_to_next_affix", "L4_line_mode_register"]
    loqo_results = {}

    for ti, (tr_name, td) in enumerate(translit_data.items()):
        t_loqo = time.time()
        all_pages = td["pages"]
        all_toks = [w for p in all_pages for ln in p["lines"] for w in ln]
        seg_base = make_cached_segmenter(all_toks)
        emit(f"=== PART 3 LOQO: {tr_name} ===")
        emit(
            f"  {'Fold':4} {'Pg':>3} {'H:S':5} | {'Real_I':>7} {'L3_I':>7} {'L4_I':>7} | "
            f"{'Real_P3':>7} {'L3_P3':>7} {'L4_P3':>7} | {'Real_P4':>7} {'L3_P4':>7} {'L4_P4':>7} | "
            f"{'L3_P5':>7} {'L4_P5':>7} | {'L3_tR':>5} {'L4_tR':>5} | {'L3_Hold':14} {'L4_Hold':14} {'s67_CA_ref':14}"
        )

        for fi, Q in enumerate(folds):
            train_q = [p for p in all_pages if p["quire"] != Q]
            test_q = [p for p in all_pages if p["quire"] == Q]
            tr_tok = [w for p in train_q for ln in p["lines"] for w in ln]
            real_te_words = [w for p in test_q for ln in p["lines"] for w in ln]

            auto_q = LengthBlindLineAutomaton(train_q, seg_base)
            p_sc_q = PrefixBigramScorer(train_q, seg_base)
            cm3_q = CharMarkov(tr_tok, 3)
            ug_rn_q = M3.UnigramGTRenorm(tr_tok, cm3_q)

            off = 1000 * ti + 10 * fi
            real_ev = FastFoldEvaluator(test_q, seg_base, p_sc_q, cm3_q, ug_rn_q, seed_offset=off)
            real_pt = real_ev.point()
            real_dr = subsample_draws([real_ev], SEED + off, n_draw=N_DRAW_LOQO)

            fold_out = {"real_pt": real_pt, "n_test": len(test_q), "models": {}}
            for mi, m_name in enumerate(loqo_models):
                gen_evs = []
                for s_seed in (1, 2):
                    sim_te = auto_q.generate_pages(test_q, m_name, seed=SEED + 500 * s_seed + fi)
                    gen_evs.append(FastFoldEvaluator(sim_te, seg_base, p_sc_q, cm3_q, ug_rn_q, seed_offset=off + s_seed))
                gen_dr = subsample_draws(gen_evs, SEED + off + 1 + mi, n_draw=N_DRAW_LOQO)
                sc = score_loqo_fold(real_pt, real_dr, gen_evs, gen_dr, real_te_words, len(test_q))
                fold_out["models"][m_name] = sc

            loqo_results[(tr_name, Q)] = fold_out

            hs_dom = Counter((p["hand"], p["section"]) for p in test_q).most_common(1)[0][0]
            hs_str = f"H{hs_dom[0]}:{hs_dom[1]}"
            r3 = fold_out["models"]["L3_core_to_next_affix"]
            r4 = fold_out["models"]["L4_line_mode_register"]
            h3_str = f"{r3['n']}/6 " + "".join("+" if r3["holds"][k] else "-" for k in PREDS)
            h4_str = f"{r4['n']}/6 " + "".join("+" if r4["holds"][k] else "-" for k in PREDS)

            s67_cell = s67_ref.get(f"{tr_name}|{Q}", {}).get("models", {}).get("CA")
            if s67_cell:
                s67_str = f"{s67_cell['n']}/6 " + "".join("+" if s67_cell["holds"][k] else "-" for k in PREDS)
            else:
                s67_str = "n/a"

            emit(
                f"  {Q:4} {len(test_q):3d} {hs_str:5} | "
                f"{real_pt['P1']:+7.4f} {r3['gen_pt']['P1']:+7.4f} {r4['gen_pt']['P1']:+7.4f} | "
                f"{real_pt['P3']:+7.4f} {r3['gen_pt']['P3']:+7.4f} {r4['gen_pt']['P3']:+7.4f} | "
                f"{real_pt['P4']:7.4f} {r3['gen_pt']['P4']:7.4f} {r4['gen_pt']['P4']:7.4f} | "
                f"{r3['gen_pt']['P5']:+7.4f} {r4['gen_pt']['P5']:+7.4f} | "
                f"{r3['type_ratio']:5.2f} {r4['type_ratio']:5.2f} | "
                f"{h3_str:14} {h4_str:14} {s67_str:14}"
            )

        emit(f"  [{tr_name} 15-quire LOQO completed in {time.time() - t_loqo:.1f}s]")
        emit("")
        flush_output()

    # Summarize Part 3 across all 15 folds and compare to s67 CA and CA0
    emit("=== PART 3 SUMMARY: PER-PREDICTION FOLD COUNTS & MEAN METRICS ACROSS 15 QUIRES (L3, L4 vs. s67 CA, CA0) ===")
    for tr_name in TRANSLITS:
        nf = len(folds)
        for m_name in loqo_models:
            cnt = {k: sum(1 for Q in folds if loqo_results[(tr_name, Q)]["models"][m_name]["holds"][k]) for k in PREDS}
            n5 = sum(1 for Q in folds if loqo_results[(tr_name, Q)]["models"][m_name]["n"] >= 5)
            n4 = sum(1 for Q in folds if loqo_results[(tr_name, Q)]["models"][m_name]["n"] >= 4)
            mean_I = float(np.mean([loqo_results[(tr_name, Q)]["models"][m_name]["gen_pt"]["P1"] for Q in folds]))
            mean_P2 = float(np.mean([loqo_results[(tr_name, Q)]["models"][m_name]["gen_pt"]["P2"] for Q in folds]))
            mean_P3 = float(np.mean([loqo_results[(tr_name, Q)]["models"][m_name]["gen_pt"]["P3"] for Q in folds]))
            mean_P4 = float(np.mean([loqo_results[(tr_name, Q)]["models"][m_name]["gen_pt"]["P4"] for Q in folds]))
            mean_P5 = float(np.mean([loqo_results[(tr_name, Q)]["models"][m_name]["gen_pt"]["P5"] for Q in folds]))
            mean_tR = float(np.mean([loqo_results[(tr_name, Q)]["models"][m_name]["type_ratio"] for Q in folds]))
            qm_tR = loqo_results[(tr_name, "M")]["models"][m_name]["type_ratio"]
            emit(
                f"  {tr_name} {m_name:22}: >=5/6: {n5:2d}/{nf} (>=4/6: {n4:2d}/{nf}) | " +
                ", ".join(f"{k} {cnt[k]:2d}/{nf}" for k in PREDS) +
                f" | mean(I={mean_I:+.4f}, P2={mean_P2:+.4f}, P3={mean_P3:+.4f}, JSD={mean_P4:.4f}, CW={mean_P5:+.4f}, tR={mean_tR:.3f}, QuireM_tR={qm_tR:.3f})"
            )
        for s67_m in ("CA", "CA0"):
            if f"{tr_name}|A" in s67_ref:
                cnt67 = {k: sum(1 for Q in folds if s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["holds"][k]) for k in PREDS}
                n5_67 = sum(1 for Q in folds if s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["n"] >= 5)
                n4_67 = sum(1 for Q in folds if s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["n"] >= 4)
                m_I67 = float(np.mean([s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["gen_point"]["P1"] for Q in folds]))
                m_P2_67 = float(np.mean([s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["gen_point"]["P2"] for Q in folds]))
                m_P3_67 = float(np.mean([s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["gen_point"]["P3"] for Q in folds]))
                m_P4_67 = float(np.mean([s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["gen_point"]["P4"] for Q in folds]))
                m_P5_67 = float(np.mean([s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["gen_point"]["P5"] for Q in folds]))
                m_tR67 = float(np.mean([s67_ref[f"{tr_name}|{Q}"]["models"][s67_m]["type_ratio"] for Q in folds]))
                qm_tR67 = s67_ref[f"{tr_name}|M"]["models"][s67_m]["type_ratio"]
                emit(
                    f"  {tr_name} s67_{s67_m:18}: >=5/6: {n5_67:2d}/{nf} (>=4/6: {n4_67:2d}/{nf}) | " +
                    ", ".join(f"{k} {cnt67[k]:2d}/{nf}" for k in PREDS) +
                    f" | mean(I={m_I67:+.4f}, P2={m_P2_67:+.4f}, P3={m_P3_67:+.4f}, JSD={m_P4_67:.4f}, CW={m_P5_67:+.4f}, tR={m_tR67:.3f}, QuireM_tR={qm_tR67:.3f})"
                )
        emit("")

    emit(f"elapsed: {time.time() - T0:.1f} s")
    emit(f"date end: {clock()}")
    flush_output()


if __name__ == "__main__":
    if "--list-imports" in sys.argv:
        for m in local_modules():
            print(m)
        sys.exit(0)
    if "--fixture" in sys.argv:
        sys.exit(0 if run_fixture() else 1)
    main()
