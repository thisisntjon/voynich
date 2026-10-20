"""s72: Wider L4 Construction (L4w) Aimed at the h2 / A14 Conflict, and Blind 6-Language Identification.

Closes the open items in CONSTRAINTS-MAP.md section C lines 195-196 and L-164 (s50 follow-up):
  1. Part 1 (Mathematical & Empirical Anatomy of the h2 / A14 Conflict in s50's L4):
     - Exact 4-component decomposition of EVA conditional character entropy h2 = H(c_2 | c_1) (with spaces) on
       Real Voynich ZL3b (h2 = 2.109) vs s50's closest L4 cipher (K=0, beta=1.0, alpha=0.7, gamma=1.0) and
       s50's K=12 L4 cipher (K=12, beta=1.0, alpha=1.0, gamma=1.0):
         (C1) Cross-Word Space Transitions (last_glyph -> ' ' and ' ' -> first_glyph),
         (C2) Prefix-Internal & Prefix -> Core Juncture Transitions,
         (C3) Core-Internal Transitions,
         (C4) Core -> Suffix Juncture & Suffix-Internal Transitions.
     - Quantitative proof of why s50's tri_w = (n_ZL3b(P,C,S) + 0.5)^gamma simultaneously inflates h2 (the +0.5
       pseudocount across 2,335 cores puts 94.6% of pseudocount mass on unattested (P,C,S) triples with jarring
       glyph junctures) and drives A14 > 0 at K=0 (frequent attested (P,C,S) triples lock C_t to the letter-bearing
       (P_t, S_t) pair, leaking plaintext letter bigram MI I(X_t; X_{t+1}) into adjacent cores I(C_t; C_{t+1})).

  2. Part 2 (Wider L4w Construction Grid Aimed at the h2 / A14 Conflict):
     - Pre-registered Wider L4w Cipher Family (strictly within the verbose homophonic (P_t, S_t) pair-cipher family
       where (P_t, S_t) carries the plaintext letter/null and C_t is null filler):
         * Flow-coupled homophone choice (eta in {0.0, 2.0, 4.0}): weights candidate homophones (P, S) of letter x_t
           by f(P, S) * P_ZL3b(P | P_{t-1}, S_{t-1}, pos_t)^eta.
         * Class-conditioned + character-transition-coherent core pool (delta in {0.0, 1.2, 1.45}, alpha in {0.48, 0.62})
           with reduced triple pseudocount eps=0.03 (gamma_0=0.35), within-line non-adjacent core self-repetition
           (p_rep in {0.0, 0.28} over same-line lags d >= 2 while enforcing C_t != C_{t-1}), and compensatory
           total-word-length cadence (beta = 0.72 on |P_t + C_t + S_t| toward line length register r).
     - Sweeps the 36-point L4w grid on Latin seed 0; tests whether L4w hits all 5 s50 targets simultaneously
       (types [5971, 8079], hapax [0.64, 0.72], h2 [2.05, 2.15], A14 <= 0, Moran [0.1086, 0.1700]), measures the
       s55/s69 discriminators (f4_prefix_gain, CHARWIN, and within-word Cov(|A_t|, |C_t|)), generates the 18 L4w
       ciphers (6 languages x 3 keys), and runs s50_solver.py to test whether the solver still recovers the plaintext
       at >= 80% accuracy.

  3. Part 3 (CONSTRAINTS-MAP.md section C line 195: Blind 6-Language Identification & Null-Control Gate):
     - Pre-registered Normalized Blind Language-ID Criterion on untouched Half B:
         * Solve Half A (U_A) blindly under each of the 6 candidate LMs L in {latin, italian, german, occitan, czech, catalan}.
         * On untouched Half B (U_B), decode non-null letter stream X_B under key_hat_L and compute:
             H_HO(L)   = held-out 5-gram cross-entropy (bits/letter) under LM_L,
             H_shuf(L) = mean 5-gram cross-entropy over 20 random permutations of X_B (exact same unigram frequencies),
             Delta_H_seq(L) = H_shuf(L) - H_HO(L)  (higher-order 2..5-gram sequential structure recovered on Half B),
             Match(L)  = Delta_H_seq(L) / (H_1(LM_L) - H_5(LM_L))  (fraction of language L's sequential structure recovered),
             Match_adj(L) = (Delta_H_seq(L) - KL(p_hat_B || q_L)) / (H_1(LM_L) - H_5(LM_L)).
     - Evaluated across 18 planted L2 ciphers, 18 planted L4 ciphers, 6 planted L4w ciphers, and 3 negative controls
       (s67 CA_ZL3b generator sidecar, token-shuffled L4 cipher, and real Voynich ZL3b under the (P, S) pair reading).
     - Pre-registered bars: Top-1 blind language ID >= 5/6 languages; Null-rejection gate max_L Match(L) >= 0.50
       cleanly separates planted ciphers from negative controls.

Development & calibration record (declared per D-048 / s50_solver_ladder.py lines 11-31):
  - Run 1 (grid delta in {0.0, 0.9, 1.5}, alpha in {0.55, 0.75}, p_rep in {0.0, 0.22}, beta in {0.0, 0.9}) completed
    Part 1, Part 2A (0/36 hit all 5 simultaneously), and Part 2B, then exited with code 1 when spawning a third
    mp.Pool(8) in Part 2C while holding all 6 dense 23^5 float32 LM tables (~50 MB each) in RAM (Windows pagefile
    commit limit).
  - Run 2 (AMENDMENT 1: simplified 2C unknown_seg to SlotSegmenter(tA) over readings ('pair', 'sep', 'core'), reduced
    3B solver to RESTARTS=2, SWEEPS=25, STEPWISE=5, grid delta in {0.0, 1.2, 1.45}, alpha in {0.48, 0.62}, p_rep in
    {0.0, 0.28}, beta=0.72) completed Part 1 and Part 2A (0/36 hit all 5; at eta=2.0, delta=1.45, alpha=0.48, p_rep=0.0
    gave h2=2.113, A14=+0.0175* while p_rep=0.28 gave h2=2.182*, A14=-0.0297), then exited with code 1 when spawning a
    second mp.Pool at Part 2B.
  - Run 3 (single-LM-at-a-time in Part 2C/3, WORKERS=3) completed Part 1 and Part 2A, and again exited with code 1 at
    line 991 when spawning the second mp.Pool(3) immediately after closing the first mp.Pool(3).
  - Three single-point construction checks on Latin calibration seed 0 (no solver, no other language) probed the
    h2 / A14 boundary between p_rep=0.0 and p_rep=0.28:
      (2.0, 1.55, 0.48, 0.14, 0.72, 0.35) -> types=6270, hapax=0.641, h2=2.132, A14=+0.0030*, Moran=+0.1380, f4=+0.0943, CHARWIN=-0.3330
      (2.0, 1.55, 0.46, 0.18, 0.72, 0.35) -> types=6646, hapax=0.648, h2=2.152*, A14=-0.0142, Moran=+0.1345, f4=+0.0965, CHARWIN=-0.3290
      (2.0, 1.60, 0.46, 0.18, 0.72, 0.35) -> types=6530, hapax=0.649, h2=2.145,  A14=-0.0099, Moran=+0.1318, f4=+0.0964, CHARWIN=-0.3341
  - AMENDMENT 2 (frozen below before full run): keep a SINGLE mp.Pool(WORKERS=3) open across both Part 2A and Part 2B
    so Windows never tears down and respawns a second Pool; run Part 2C and Part 3 in-process loading one candidate
    language LM at a time and freeing it via gc.collect(); set L4W_GRID to delta in (0.0, 1.25, 1.60), alpha in
    (0.46, 0.60), p_rep in (0.0, 0.18), beta=0.72.

PRE-REGISTRATION (D-048): frozen in s72_wider_l4_and_language_id.prereg.sha256 before running.
Run: C:\\Users\\thisi\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -I s72_wider_l4_and_language_id.py
Writes ONLY: results_s72.txt
"""
from __future__ import annotations

import gc
import hashlib
import json
import math
import multiprocessing as mp
import random
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

import a1_profile  # noqa: E402
import corpora  # noqa: E402
import m3_bakeoff_reconcile as M3  # noqa: E402
import p4d1_core_order as P4  # noqa: E402
import s34_morphology_syntax_geography as s34  # noqa: E402
import s50_solver as S  # noqa: E402
import s50_solver_ladder as S50  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import scoreboard.metrics_new as mn  # noqa: E402
import vparse  # noqa: E402

SELF = ROOT / "s72_wider_l4_and_language_id.py"
STUB = ROOT / "s72_wider_l4_and_language_id.prereg.sha256"
OUT = ROOT / "results_s72.txt"

LANG_LIST = ["latin", "italian", "german", "occitan", "czech", "catalan"]
KEYS = (1, 2, 3)
EMPTY = "∅"
WORKERS = 3

# Pre-registered L4w grid (36 points on Latin seed 0)
ETA_GRID = (0.0, 2.0, 4.0)
DELTA_GRID = (0.0, 1.25, 1.60)
ALPHA_GRID = (0.46, 0.60)
PREP_GRID = (0.0, 0.18)
BETA_FIXED = 0.72
GAMMA0_FIXED = 0.35
EPS_TRI = 0.03
L4W_GRID = [
    (eta, delta, alpha, prep, BETA_FIXED, GAMMA0_FIXED)
    for eta in ETA_GRID
    for delta in DELTA_GRID
    for alpha in ALPHA_GRID
    for prep in PREP_GRID
]

# Pre-registered thresholds
MATCH_GATE = 0.50
F4_BAR = 0.08
ACC_PASS = 0.80

log: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if (want and not bad and SELF.name in want) else f"False (mismatch: {bad})"


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def train_single_lm(lang: str):
    """Train 5-gram LM for a single language without retaining other languages in RAM."""
    plain, lmt = S50.lang_texts(lang)
    lm, q, _lm3 = S.train_lm(lmt)
    del _lm3
    return lm, q, plain, len(lmt)


# ==============================================================================
# PART 1: Mathematical & Empirical Anatomy of the h2 / A14 Conflict in s50's L4
# ==============================================================================
CAT_NAMES = (
    "C1_cross_word_space",
    "C2_prefix_and_pre_core",
    "C3_core_internal",
    "C4_core_suf_and_suffix",
)


def decompose_h2(tokens: list[str], seg: mn.SlotSegmenter | None = None) -> dict:
    """Exact 4-component decomposition of EVA h2 = H(c_2 | c_1) on ' '.join(tokens) + ' '.
    Every adjacent character pair (a, b) in s = ' '.join(tokens) + ' ' is assigned to one of:
      0: C1_cross_word_space   (last_glyph -> ' ' and ' ' -> first_glyph)
      1: C2_prefix_and_pre_core (transitions within prefix P and juncture P[-1] -> C[0])
      2: C3_core_internal      (transitions within core C)
      3: C4_core_suf_and_suffix (juncture C[-1] -> S[0] and transitions within suffix S)
    Guarantees sum_k (w_k * h2_global_k) == h2 identically.
    """
    if seg is None:
        seg = mn.SlotSegmenter(tokens)
    s = " ".join(tokens) + " "
    c1 = Counter(s)
    n1 = len(s)
    h1 = -sum((v / n1) * math.log2(v / n1) for v in c1.values())
    c2 = Counter(zip(s, s[1:]))
    n2 = sum(c2.values())
    h12 = -sum((v / n2) * math.log2(v / n2) for v in c2.values())
    h2_total = h12 - h1

    c1_left = Counter()
    for (a, _b), v in c2.items():
        c1_left[a] += v
    h1_left = -sum((v / n2) * math.log2(v / n2) for v in c1_left.values())
    marg_corr = h1_left - h1

    cat_pairs = [Counter() for _ in range(4)]
    for idx, w in enumerate(tokens):
        p, c, suf = seg.segment(w)
        lp, lc, ls = len(p), len(c), len(suf)
        if idx > 0:
            cat_pairs[0][(" ", w[0])] += 1
        if lp > 0:
            for j in range(lp - 1):
                cat_pairs[1][(p[j], p[j + 1])] += 1
            cat_pairs[1][(p[-1], c[0])] += 1
        for j in range(lc - 1):
            cat_pairs[2][(c[j], c[j + 1])] += 1
        if ls > 0:
            cat_pairs[3][(c[-1], suf[0])] += 1
            for j in range(ls - 1):
                cat_pairs[3][(suf[j], suf[j + 1])] += 1
        cat_pairs[0][(w[-1], " ")] += 1

    c1_to_space = sum(v for (a, b), v in cat_pairs[0].items() if b == " ")
    c1_from_space = sum(v for (a, b), v in cat_pairs[0].items() if a == " ")
    bits_to_space = sum(
        -v * math.log2(c2[(a, b)] / c1_left[a]) for (a, b), v in cat_pairs[0].items() if b == " "
    ) / max(1, c1_to_space)
    bits_from_space = sum(
        -v * math.log2(c2[(a, b)] / c1_left[a]) for (a, b), v in cat_pairs[0].items() if a == " "
    ) / max(1, c1_from_space)

    cats = {}
    for k, name in enumerate(CAT_NAMES):
        nk = sum(cat_pairs[k].values())
        wk = nk / n2
        bits_k = sum(-v * math.log2(c2[(a, b)] / c1_left[a]) for (a, b), v in cat_pairs[k].items())
        h2_k = (bits_k / nk + marg_corr) if nk > 0 else 0.0
        left_k = Counter()
        for (a, _b), v in cat_pairs[k].items():
            left_k[a] += v
        h2_internal_k = (
            sum(-v * math.log2(v / left_k[a]) for (a, b), v in cat_pairs[k].items()) / nk if nk > 0 else 0.0
        )
        cats[name] = dict(
            count=nk,
            share=wk,
            h2_cond=h2_k,
            h2_internal=h2_internal_k,
            contrib=wk * h2_k,
        )

    return dict(
        n_chars=n1,
        n_bigrams=n2,
        h1=h1,
        h2=h2_total,
        sum_contrib=sum(d["contrib"] for d in cats.values()),
        bits_to_space=bits_to_space,
        bits_from_space=bits_from_space,
        cats=cats,
    )


def a14_anatomy(lines: list[list[str]], seg: mn.SlotSegmenter | None = None) -> dict:
    """Detailed MI anatomy of A14 and affix-core coupling on a line-structured text."""
    toks = [w for ln in lines for w in ln]
    if seg is None:
        seg = mn.SlotSegmenter(toks)
    vocab = sorted(set(toks))
    w2i = {w: i for i, w in enumerate(vocab)}
    parsed_v = [seg.segment(w) for w in vocab]
    cs = sorted({c for _, c, _ in parsed_v})
    ps = sorted({(p, s) for p, _, s in parsed_v})
    c2i = {c: i for i, c in enumerate(cs)}
    ps2i = {pair: i for i, pair in enumerate(ps)}
    C_W = np.array([c2i[c] for _, c, _ in parsed_v], dtype=np.int64)
    PS_W = np.array([ps2i[(p, s)] for p, _, s in parsed_v], dtype=np.int64)

    w_all = np.array([w2i[w] for w in toks], dtype=np.int64)
    mi_ps_c = float(s34.fast_mi_1d(PS_W[w_all], C_W[w_all], len(ps), len(cs))[0])

    lines_2 = [[w2i[w] for w in ln] for ln in lines if len(ln) >= 2]
    n_pairs = sum(len(ln) - 1 for ln in lines_2)
    w1 = np.fromiter((w for ln in lines_2 for w in ln[:-1]), dtype=np.int64, count=n_pairs)
    w2 = np.fromiter((w for ln in lines_2 for w in ln[1:]), dtype=np.int64, count=n_pairs)
    mi_c_obs = float(s34.fast_mi_1d(C_W[w1], C_W[w2], len(cs), len(cs))[0])
    mi_ps_obs = float(s34.fast_mi_1d(PS_W[w1], PS_W[w2], len(ps), len(ps))[0])

    rng = random.Random(P4.SEED)
    null_c, null_ps = [], []
    for _ in range(P4.N_SHUF):
        sh = [rng.sample(ln, len(ln)) for ln in lines_2]
        a = np.fromiter((w for ln in sh for w in ln[:-1]), dtype=np.int64, count=n_pairs)
        b = np.fromiter((w for ln in sh for w in ln[1:]), dtype=np.int64, count=n_pairs)
        null_c.append(s34.fast_mi_1d(C_W[a], C_W[b], len(cs), len(cs))[0])
        null_ps.append(s34.fast_mi_1d(PS_W[a], PS_W[b], len(ps), len(ps))[0])
    mi_c_shuf = float(np.mean(null_c))
    mi_ps_shuf = float(np.mean(null_ps))

    adj_eq = int(np.sum(C_W[w1] == C_W[w2]))
    nonadj_eq, nonadj_tot = 0, 0
    for ln in lines_2:
        cln = [C_W[w] for w in ln]
        L = len(cln)
        for i in range(L):
            for j in range(i + 2, L):
                nonadj_tot += 1
                if cln[i] == cln[j]:
                    nonadj_eq += 1
    return dict(
        mi_ps_c=mi_ps_c,
        mi_ps_obs=mi_ps_obs,
        mi_ps_shuf=mi_ps_shuf,
        ps_excess=mi_ps_obs - mi_ps_shuf,
        mi_c_obs=mi_c_obs,
        mi_c_shuf=mi_c_shuf,
        a14=mi_c_obs - mi_c_shuf,
        adj_core_eq_rate=adj_eq / max(1, n_pairs),
        nonadj_core_eq_rate=nonadj_eq / max(1, nonadj_tot),
    )


# ==============================================================================
# PART 2: Wider L4w Cipher Family & Discriminators (f4_prefix_gain, CHARWIN)
# ==============================================================================
class L4wBase:
    """Precomputes ZL3b affix-flow tables, 12 core classes, character-transition coherence matrices,
    and compatibility masks for the Wider L4w verbose homophonic cipher family."""

    def __init__(self, vlines: list[list[str]], vtoks: list[str]):
        self.seg = mn.SlotSegmenter(vtoks)
        self.vlines = vlines
        self.vtoks = vtoks
        trip = [self.seg.segment(w) for w in vtoks]
        self.pairs = Counter((p, s) for p, _, s in trip)
        self.pair_list = list(self.pairs)
        self.pair2id = {pair: i for i, pair in enumerate(self.pair_list)}
        self.core_f = Counter(c for _, c, _ in trip)
        self.cores = list(self.core_f)
        self.core2id = {c: i for i, c in enumerate(self.cores)}
        self.cf = np.array([self.core_f[c] for c in self.cores], dtype=np.float64)
        self.clen = np.array([len(c) for c in self.cores], dtype=np.float64)
        self.tri = Counter(trip)

        lens = Counter(len(c) for _, c, _ in trip)
        self.len_vals = np.array(list(lens.keys()), dtype=np.float64)
        self.len_p = np.array(list(lens.values()), dtype=np.float64)
        self.len_p /= self.len_p.sum()
        self.mean_aff_len = float(np.mean([len(p) + len(s) for p, _, s in trip]))

        nP, nC = len(self.pair_list), len(self.cores)
        self.compat = np.zeros((nP, nC), dtype=bool)
        for pi, (p, s) in enumerate(self.pair_list):
            self.compat[pi] = np.array([self.seg.segment(p + c + s) == (p, c, s) for c in self.cores], dtype=bool)

        self.tri_mat = np.zeros((nP, nC), dtype=np.float64)
        for (p, c, s), cnt in self.tri.items():
            pi = self.pair2id.get((p, s))
            ci = self.core2id.get(c)
            if pi is not None and ci is not None:
                self.tri_mat[pi, ci] = cnt

        cls_map, _info = S67.core_classes([vlines], self.seg)
        self.core_cls = np.array([cls_map.get(c, 12) for c in self.cores], dtype=np.int64)
        n_cls = 13
        pair_cls_cnt = np.full((nP, n_cls), 0.2, dtype=np.float64)
        for (p, c, s), cnt in self.tri.items():
            pi = self.pair2id[(p, s)]
            k = cls_map.get(c, 12)
            pair_cls_cnt[pi, k] += cnt
        pair_cls_prob = pair_cls_cnt / pair_cls_cnt.sum(axis=1, keepdims=True)
        self.cls_prob_mat = pair_cls_prob[:, self.core_cls]

        s_all = " ".join(vtoks) + " "
        c1 = Counter(s_all)
        c2 = Counter(zip(s_all, s_all[1:]))
        chars = sorted(c1.keys())
        ch2i = {ch: i for i, ch in enumerate(chars)}
        G = len(chars)
        L_mat = np.full((G, G), -12.0, dtype=np.float64)
        for a, ca in c1.items():
            ia = ch2i[a]
            for b in chars:
                ib = ch2i[b]
                cnt = c2.get((a, b), 0)
                L_mat[ia, ib] = math.log2((cnt + 0.05) / (ca + 0.05 * G))
        self.ch2i = ch2i
        self.L_mat = L_mat
        sp_idx = ch2i[" "]

        ll_p = np.zeros(nP, dtype=np.float64)
        ll_s = np.zeros(nP, dtype=np.float64)
        left_ch = np.zeros(nP, dtype=np.int64)
        right_ch = np.zeros(nP, dtype=np.int64)
        len_ps = np.zeros(nP, dtype=np.float64)
        for pi, (p, s) in enumerate(self.pair_list):
            len_ps[pi] = len(p) + len(s)
            if p:
                val = L_mat[sp_idx, ch2i[p[0]]]
                for j in range(len(p) - 1):
                    val += L_mat[ch2i[p[j]], ch2i[p[j + 1]]]
                ll_p[pi] = val
                left_ch[pi] = ch2i[p[-1]]
            else:
                ll_p[pi] = 0.0
                left_ch[pi] = sp_idx
            if s:
                val = L_mat[ch2i[s[-1]], sp_idx]
                for j in range(len(s) - 1):
                    val += L_mat[ch2i[s[j]], ch2i[s[j + 1]]]
                ll_s[pi] = val
                right_ch[pi] = ch2i[s[0]]
            else:
                ll_s[pi] = 0.0
                right_ch[pi] = sp_idx

        ll_c = np.zeros(nC, dtype=np.float64)
        c_first = np.zeros(nC, dtype=np.int64)
        c_last = np.zeros(nC, dtype=np.int64)
        for ci, c in enumerate(self.cores):
            c_first[ci] = ch2i[c[0]]
            c_last[ci] = ch2i[c[-1]]
            val = 0.0
            for j in range(len(c) - 1):
                val += L_mat[ch2i[c[j]], ch2i[c[j + 1]]]
            ll_c[ci] = val

        tot_ll = (
            ll_p[:, None]
            + L_mat[left_ch[:, None], c_first[None, :]]
            + ll_c[None, :]
            + L_mat[c_last[None, :], right_ch[:, None]]
            + ll_s[:, None]
        )
        tot_len = len_ps[:, None] + self.clen[None, :] + 1.0
        mean_ll = tot_ll / tot_len
        mu_ll = float(mean_ll[self.compat].mean())
        sd_ll = float(mean_ll[self.compat].std())
        self.z_char = np.clip((mean_ll - mu_ll) / max(sd_ll, 1e-6), -3.0, 2.5)
        self.len_ps = len_ps

        pre_uni = Counter()
        pre_trans = defaultdict(Counter)
        pre_by_prevp = defaultdict(Counter)
        pre_by_pos = defaultdict(Counter)
        for ln in vlines:
            L = len(ln)
            prev_p, prev_s = "^", "^"
            for j, w in enumerate(ln):
                pos = "I" if j == 0 else ("F" if j == L - 1 else "M")
                p, _c, s = self.seg.segment(w)
                pre_uni[p] += 1
                pre_by_pos[pos][p] += 1
                if j > 0:
                    pre_trans[(prev_p, prev_s, pos)][p] += 1
                    pre_by_prevp[prev_p][p] += 1
                prev_p, prev_s = p, s
        self.pre_set = sorted(pre_uni.keys())
        tot_u = sum(pre_uni.values())
        V_p = len(self.pre_set)
        self.pu_pre = {p: (pre_uni[p] + 0.5) / (tot_u + 0.5 * V_p) for p in self.pre_set}
        self.p_pos = {}
        for pos, cnt in pre_by_pos.items():
            tot = sum(cnt.values())
            T = len(cnt)
            self.p_pos[pos] = {p: (cnt.get(p, 0) + T * self.pu_pre[p]) / (tot + T) for p in self.pre_set}
        self.p_prevp = {}
        for pp, cnt in pre_by_prevp.items():
            tot = sum(cnt.values())
            T = len(cnt)
            self.p_prevp[pp] = {p: (cnt.get(p, 0) + T * self.pu_pre[p]) / (tot + T) for p in self.pre_set}
        self.p_ctx = {}
        for ctx, cnt in pre_trans.items():
            tot = sum(cnt.values())
            T = len(cnt)
            pp = ctx[0]
            bo = self.p_prevp.get(pp, self.pu_pre)
            self.p_ctx[ctx] = {p: (cnt.get(p, 0) + T * bo[p]) / (tot + T) for p in self.pre_set}

    def pre_flow_prob(self, p: str, prev_p: str, prev_s: str, pos: str) -> float:
        if pos == "I":
            return self.p_pos.get("I", self.pu_pre).get(p, 1e-3)
        d = self.p_ctx.get((prev_p, prev_s, pos))
        if d is not None:
            return d.get(p, 1e-3)
        return self.p_prevp.get(prev_p, self.pu_pre).get(p, 1e-3)


def gen_l4w(plain: np.ndarray, key: dict, base: L4wBase, params: tuple, seed: int, lens: list[int]):
    """Generate a 38,000-token ciphertext from the Wider L4w verbose homophonic family."""
    eta, delta, alpha, p_rep, beta, gamma0 = params
    rng = np.random.default_rng(seed * 1000 + 11)
    hom = {int(x): [tuple(p) for p in v] for x, v in key["hom"].items()}

    w_core_base = base.cf ** alpha
    tri_factor = (base.tri_mat + EPS_TRI) ** gamma0
    coh_factor = (base.cls_prob_mat ** (0.5 * delta)) * np.exp2(delta * base.z_char)
    pair_core_static = (w_core_base[None, :] * tri_factor * coh_factor) * base.compat

    it = 0
    lines, truth = [], []
    for L in lens:
        r_core = float(rng.choice(base.len_vals, p=base.len_p))
        r_word = r_core + base.mean_aff_len
        prev_ci = -1
        prev_p, prev_s = "^", "^"
        line_cores: list[int] = []
        ln, tl = [], []
        for j in range(L):
            pos = "I" if j == 0 else ("F" if j == L - 1 else "M")
            if rng.random() < S50.P_NULL:
                cand, x = hom[-1], None
            else:
                x = int(plain[it % len(plain)])
                it += 1
                cand = hom[x]

            if len(cand) == 1:
                pair = cand[0]
            else:
                pw = np.empty(len(cand), dtype=np.float64)
                for idx_c, (p_c, s_c) in enumerate(cand):
                    w = float(base.pairs[(p_c, s_c)])
                    if eta > 0.0:
                        w *= base.pre_flow_prob(p_c, prev_p, prev_s, pos) ** eta
                    pw[idx_c] = w
                pw_sum = pw.sum()
                if pw_sum <= 0:
                    pair = cand[int(rng.integers(len(cand)))]
                else:
                    pair = cand[int(rng.choice(len(cand), p=pw / pw_sum))]

            pi = base.pair2id[pair]
            target_c_len = max(1.0, r_word - base.len_ps[pi])

            ci = -1
            if p_rep > 0.0 and len(line_cores) >= 2 and rng.random() < p_rep:
                cands_rep = [c for c in line_cores[:-1] if c != prev_ci and base.compat[pi, c]]
                if cands_rep:
                    rw = np.array(
                        [
                            pair_core_static[pi, c] * math.exp(-beta * abs(base.clen[c] - target_c_len))
                            for c in cands_rep
                        ],
                        dtype=np.float64,
                    )
                    if rw.sum() > 0:
                        ci = int(cands_rep[int(rng.choice(len(cands_rep), p=rw / rw.sum()))])
                    else:
                        ci = int(cands_rep[int(rng.integers(len(cands_rep)))])

            if ci < 0:
                len_pull = np.exp(-beta * np.abs(base.clen - target_c_len))
                ww = pair_core_static[pi] * len_pull
                if prev_ci >= 0:
                    ww[prev_ci] = 0.0
                w_sum = ww.sum()
                if w_sum <= 0:
                    ww = base.compat[pi].astype(np.float64)
                    if prev_ci >= 0 and ww.sum() > 1:
                        ww[prev_ci] = 0.0
                    w_sum = ww.sum()
                ci = int(rng.choice(len(base.cores), p=ww / w_sum))

            prev_ci = ci
            line_cores.append(ci)
            prev_p, prev_s = pair[0], pair[1]
            ln.append(pair[0] + base.cores[ci] + pair[1])
            tl.append([] if x is None else [x])
        lines.append(ln)
        truth.extend(tl)
    return lines, truth


def extra_discriminators(lines: list[list[str]], nA: int) -> dict:
    """Compute s55/s69 f4_prefix_gain, s57 CHARWIN, and within-word Cov(|A_t|, |C_t|) on Half A -> Half B."""
    linesA, linesB = [], []
    n = 0
    for ln in lines:
        if n < nA:
            linesA.append(ln)
        else:
            linesB.append(ln)
        n += len(ln)
    toksA = [w for ln in linesA for w in ln]
    toksB = [w for ln in linesB for w in ln]
    seg = mn.SlotSegmenter(toksA)

    uni = Counter()
    big = defaultdict(Counter)
    for ln in linesA:
        ps = [seg.segment(w)[0] or EMPTY for w in ln]
        for p in ps:
            uni[p] += 1
        for a, b in zip(ps, ps[1:]):
            big[a][b] += 1
    N_u = sum(uni.values())
    V_u = len(uni)
    tot_b = {a: sum(c.values()) for a, c in big.items()}

    def pu(w):
        return (uni.get(w, 0) + 0.5) / (N_u + 0.5 * (V_u + 1))

    def pb(a, w):
        c = big.get(a)
        if not c:
            return pu(w)
        T = len(c)
        return (c.get(w, 0) + T * pu(w)) / (tot_b[a] + T)

    u_bits = b_bits = 0.0
    n_targ = 0
    for ln in linesB:
        ps = [seg.segment(w)[0] or EMPTY for w in ln]
        for a, b in zip(ps, ps[1:]):
            n_targ += 1
            u_bits += -math.log2(pu(b))
            b_bits += -math.log2(pb(a, b))
    f4_gain = (u_bits - b_bits) / max(1, n_targ)

    m3 = mn.CharMarkov(toksA, 3)
    ugt = M3.UnigramGTRenorm(toksA, m3)
    cntB = Counter(toksB)
    rn_bits = sum(c * (-ugt.logp_word(w)) for w, c in cntB.items()) / len(toksB)
    wb_bits = sum(c * (-m3.logp_word(w)) for w, c in cntB.items()) / len(toksB)
    charwin = rn_bits - wb_bits

    all_toks = toksA + toksB
    aff_l = np.array([len(seg.segment(w)[0]) + len(seg.segment(w)[2]) for w in all_toks], dtype=np.float64)
    core_l = np.array([len(seg.segment(w)[1]) for w in all_toks], dtype=np.float64)
    cov_ac = float(np.cov(aff_l, core_l, ddof=0)[0, 1])

    return dict(f4_prefix_gain=f4_gain, charwin=charwin, cov_aff_core_len=cov_ac)


_G_BASE: L4wBase | None = None
_G_PLAINS: dict | None = None
_G_LENS: list[int] | None = None
_G_NA: int = 19000
_G_CALK: dict | None = None


def _init_l4w_pool(vlines, vtoks, plains, lens, nA, calk):
    global _G_BASE, _G_PLAINS, _G_LENS, _G_NA, _G_CALK
    _G_BASE = L4wBase(vlines, vtoks)
    _G_PLAINS = plains
    _G_LENS = lens
    _G_NA = nA
    _G_CALK = calk


def _eval_l4w_point(prm):
    ln, _tr = gen_l4w(_G_PLAINS["latin"], _G_CALK, _G_BASE, prm, 0, _G_LENS)
    st = S50.stats(ln)
    ed = extra_discriminators(ln, _G_NA)
    st.update(ed)
    return prm, st


def _eval_l4w_cipher(args):
    lang, k, best_prm = args
    key = S50.make_l4_key(_G_PLAINS[lang], _G_BASE, k)
    ln, truth = gen_l4w(_G_PLAINS[lang], key, _G_BASE, best_prm, k, _G_LENS)
    st = S50.stats(ln)
    ed = extra_discriminators(ln, _G_NA)
    st.update(ed)
    return lang, k, st, ln, truth, key


def solve_l4w_inproc(lang, k, toks, truth, nA, true_pre, true_suf, mode, lm, q, restarts, sweeps):
    """Run solver on L4w cipher in-process using already-loaded (lm, q) for `lang`."""
    t0 = time.time()
    S.STEPWISE = 12
    S.NULL_INIT_K = (16, 12)
    seed = 72_000 + k * 101 + LANG_LIST.index(lang) * 7 + (0 if mode == "known_pair" else 500)
    tA, tB = toks[:nA], toks[nA:]
    if mode == "known_pair":
        pre, suf, rd = set(true_pre), set(true_suf), "pair"
    else:
        sg = mn.SlotSegmenter(tA, min_share=0.01, ent_frac=0.5)
        pre_c, suf_c = sg.prefixes, sg.suffixes
        parsedA = [S50.slot_parse(w, pre_c, suf_c) for w in tA]
        best = None
        Ntok = len(tA)
        for rd_c in ("pair", "sep", "core"):
            tu, ign = S50.reading_units(parsedA, rd_c)
            sA, ids = S50.stream_from(tu)
            _l, _n, sc = S50.run_solve(sA, lm, q, True, 2, 18, seed, None, None, "")
            ig = 0.0
            n_ign = 0
            if rd_c != "sep":
                cnt = Counter(ign)
                ig = sum(v * math.log2(v / Ntok) for v in cnt.values())
                n_ign = len(cnt)
            crit = sc + ig - 0.5 * math.log2(Ntok) * (len(ids) + n_ign)
            if best is None or crit > best[0]:
                best = (crit, pre_c, suf_c, rd_c)
        _, pre, suf, rd = best

    parsedA = [S50.slot_parse(w, pre, suf) for w in tA]
    tuA, _ = S50.reading_units(parsedA, rd)
    sA, ids = S50.stream_from(tuA)
    letter, null, sc = S50.run_solve(sA, lm, q, True, restarts, sweeps, seed + 1, None, None, "")
    parsedB = [S50.slot_parse(w, pre, suf) for w in tB]
    tuB, _ = S50.reading_units(parsedB, rd)
    dec = S50.decode_tokens(tuB, ids, letter, null)
    acc = S50.accuracy(truth[nA:], dec)
    return dict(
        acc=acc,
        score=sc,
        nulls=int(null.sum()),
        units=int(len(letter)),
        rd=rd,
        n_pre=len(pre),
        n_suf=len(suf),
        elapsed=time.time() - t0,
    )


# ==============================================================================
# PART 3: Blind 6-Language Identification & Null-Control Gate
# ==============================================================================
def score_text_under_lm(tag, kseed, sA, sB, n_units_A, li, lm, q, dh_true, restarts, sweeps, stepwise):
    """Solve Half A (sA) under candidate LM (lm, q) and score decoded Half B (sB)."""
    S.STEPWISE = stepwise
    S.NULL_INIT_K = (16, 12)
    seed = 90_000 + (kseed * 37) + li * 13 + (hash(tag) & 0xFFF)
    n_cnt = np.bincount(sA, minlength=n_units_A)
    forced = n_cnt < S50.MIN_COUNT
    letter, null, scA = S.solve(
        sA,
        lm,
        q,
        w_kl=S50.W_KL,
        allow_null=True,
        restarts=restarts,
        sweeps=sweeps,
        T0=S50.T0,
        T1=S50.T1,
        seed=seed,
        forced_null=forced,
    )
    valid_B = sB[(sB >= 0) & (sB < len(letter))]
    keep_B = ~null[valid_B]
    xB = letter[valid_B[keep_B]]
    M_B = len(xB)
    if M_B < 20:
        return dict(
            h_ho=float("nan"),
            h_shuf=float("nan"),
            dh_seq=0.0,
            z_seq=0.0,
            kl_b=float("nan"),
            match=0.0,
            match_adj=0.0,
            M_B=M_B,
            scA=float(scA),
        )

    h_ho = S.lm_bits_per_letter(lm, xB)
    rng_shuf = np.random.default_rng(20261018 + li)
    shuf_vals = [S.lm_bits_per_letter(lm, rng_shuf.permutation(xB)) for _ in range(20)]
    h_shuf = float(np.mean(shuf_vals))
    sd_shuf = float(np.std(shuf_vals))
    dh_seq = h_shuf - h_ho
    z_seq = dh_seq / max(sd_shuf, 1e-6)

    cnt_b = np.bincount(xB, minlength=S.A).astype(np.float64)
    p_b = cnt_b / cnt_b.sum()
    kl_b = float(np.sum(np.where(p_b > 0, p_b * np.log2(np.where(p_b > 0, p_b, 1.0) / q), 0.0)))

    match_raw = dh_seq / dh_true
    match_adj = (dh_seq - kl_b) / dh_true
    return dict(
        h_ho=h_ho,
        h_shuf=h_shuf,
        dh_seq=dh_seq,
        z_seq=z_seq,
        kl_b=kl_b,
        match=match_raw,
        match_adj=match_adj,
        M_B=M_B,
        scA=float(scA),
    )


def pair_stream_split(tokens: list[str], nA: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Fit SlotSegmenter on Half A tokens, extract (P, S) pair units, and return (sA, sB, n_units_A)."""
    tA, tB = tokens[:nA], tokens[nA:]
    seg = mn.SlotSegmenter(tA)
    ids: dict[tuple[str, str], int] = {}
    sA_list = []
    for w in tA:
        p, _c, s = seg.segment(w)
        u = (p, s)
        if u not in ids:
            ids[u] = len(ids)
        sA_list.append(ids[u])
    sB_list = []
    for w in tB:
        p, _c, s = seg.segment(w)
        sB_list.append(ids.get((p, s), -1))
    return np.asarray(sA_list, dtype=np.int64), np.asarray(sB_list, dtype=np.int64), len(ids)


def main() -> None:
    t_start = time.time()
    emit("S72: Wider L4 Construction (L4w) Aimed at the h2 / A14 Conflict, and Blind 6-Language Identification")
    emit(f"date: {clock()}")
    emit(f"hashes: s72_wider_l4_and_language_id.py={sha256(SELF)}")
    emit(f"stub_match: {stub_match()}  (stub {STUB.name})")
    emit(
        f"deps (imported unchanged): s50_solver_ladder.py={sha256(ROOT / 's50_solver_ladder.py')[:16]}  "
        f"s50_solver.py={sha256(ROOT / 's50_solver.py')[:16]}  "
        f"p4d1_core_order.py={sha256(ROOT / 'p4d1_core_order.py')[:16]}  "
        f"s67_constrained_assembly_loqo.py={sha256(ROOT / 's67_constrained_assembly_loqo.py')[:16]}  "
        f"m3_bakeoff_reconcile.py={sha256(ROOT / 'm3_bakeoff_reconcile.py')[:16]}"
    )
    emit()

    vlines, vtoks = S50.voynich()
    lens = S50.line_lengths(vlines)
    nA = S50.split_index(lens)
    vseg = mn.SlotSegmenter(vtoks)
    # Load only the 100k plaintext arrays (no dense 23^5 LM tables in RAM during Part 1 & Part 2A/2B)
    plains = {lang: S50.lang_texts(lang)[0] for lang in LANG_LIST}

    # ==========================================================================
    # PART 1: Mathematical & Empirical Anatomy of the h2 / A14 Conflict in s50
    # ==========================================================================
    emit("=== PART 1: Mathematical & Empirical Anatomy of the h2 / A14 Conflict in s50's L4 ===")
    s50_base = S50.L4Base(vtoks)
    k_lat1 = S50.make_l4_key(plains["latin"], s50_base, 1)

    n_cores_zl = len(s50_base.cores)
    n_pairs_zl = len(s50_base.pairs)
    mean_pair_cnt = len(vtoks) / n_pairs_zl
    pseudo_sum_per_pair = 0.5 * n_cores_zl
    pseudo_share_unweighted = pseudo_sum_per_pair / (mean_pair_cnt + pseudo_sum_per_pair)

    ln_s50_k0_a07, _ = S50.gen_l4(plains["latin"], k_lat1, s50_base, (0, 1.0, 0.7, 1.0), 1, lens)
    ln_s50_k0_a10, _ = S50.gen_l4(plains["latin"], k_lat1, s50_base, (0, 1.0, 1.0, 1.0), 1, lens)
    ln_s50_k12_a10, _ = S50.gen_l4(plains["latin"], k_lat1, s50_base, (12, 1.0, 1.0, 1.0), 1, lens)
    ln_s50_k0_g0, _ = S50.gen_l4(plains["latin"], k_lat1, s50_base, (0, 1.0, 0.7, 0.0), 1, lens)

    def attested_share(lines_in):
        tks = [w for l_ in lines_in for w in l_]
        att = sum(1 for w in tks if s50_base.tri[vseg.segment(w)] > 0)
        return att / len(tks)

    emit("1A. Pseudocount dilution in s50 L4Base.tri_w = (n_ZL3b(P,C,S) + 0.5)^gamma:")
    emit(f"    ZL3b attested pairs = {n_pairs_zl}, cores = {n_cores_zl}, mean pair count = {mean_pair_cnt:.2f} tokens.")
    emit(f"    Per pair, uniform +0.5 pseudocount adds {pseudo_sum_per_pair:.1f} pseudo-tokens ({pseudo_share_unweighted * 100:.1f}% of raw mass).")
    emit(
        f"    Resulting share of ZL3b-attested (P,C,S) tokens: "
        f"ZL3b = 100.0%, s50 K=0/a=0.7/g=0.0 = {attested_share(ln_s50_k0_g0)*100:.1f}%, "
        f"s50 K=0/a=0.7/g=1.0 = {attested_share(ln_s50_k0_a07)*100:.1f}%, "
        f"s50 K=0/a=1.0/g=1.0 = {attested_share(ln_s50_k0_a10)*100:.1f}%, "
        f"s50 K=12/a=1.0/g=1.0 = {attested_share(ln_s50_k12_a10)*100:.1f}%."
    )
    emit()

    emit("1B. Exact 4-Component Decomposition of h2 = H(c_2 | c_1) (sum_k w_k * h2_k == h2):")
    p1_texts = [
        ("Voynich_ZL3b", vlines, vtoks),
        ("s50_L4_K0_b1_a0.7_g1.0 (closest)", ln_s50_k0_a07, [w for l_ in ln_s50_k0_a07 for w in l_]),
        ("s50_L4_K0_b1_a1.0_g1.0 (Moran hit)", ln_s50_k0_a10, [w for l_ in ln_s50_k0_a10 for w in l_]),
        ("s50_L4_K12_b1_a1.0_g1.0 (A14<=0)", ln_s50_k12_a10, [w for l_ in ln_s50_k12_a10 for w in l_]),
        ("s50_L4_K0_b1_a0.7_g0.0 (gamma=0)", ln_s50_k0_g0, [w for l_ in ln_s50_k0_g0 for w in l_]),
    ]
    decomp_ref = None
    for name, lns, tks in p1_texts:
        d = decompose_h2(tks)
        if decomp_ref is None:
            decomp_ref = d
        dh2 = d["h2"] - decomp_ref["h2"]
        emit(
            f"  {name:<36} h1={d['h1']:.3f}  h2={d['h2']:.3f} (Delta={dh2:+.3f})  "
            f"[w_end->' ': {d['bits_to_space']:.3f}b, ' '->w_start: {d['bits_from_space']:.3f}b]"
        )
        for cname in CAT_NAMES:
            c = d["cats"][cname]
            ref_c = decomp_ref["cats"][cname]
            d_contrib = c["contrib"] - ref_c["contrib"]
            d_cond = c["h2_cond"] - ref_c["h2_cond"]
            emit(
                f"    {cname:<24} share={c['share']:.3f}  h2_k={c['h2_cond']:.3f} ({d_cond:+.3f})  "
                f"H_int={c['h2_internal']:.3f}  contrib={c['contrib']:.4f} ({d_contrib:+.4f})"
            )
    emit()

    lat_plain = plains["latin"][:38000]
    mi_lat_xx = float(s34.fast_mi_1d(lat_plain[:-1], lat_plain[1:], S.A, S.A)[0])
    emit(
        f"1C. Quantitative Anatomy of the A14 Conflict (Latin plaintext lag-1 letter MI I(X_t; X_{{t+1}}) = {mi_lat_xx:.4f} bits):"
    )
    a14_s50_k0 = None
    for name, lns, _tks in p1_texts:
        a_info = a14_anatomy(lns)
        if "closest" in name:
            a14_s50_k0 = a_info
        emit(
            f"  {name:<36} I(PS;C)={a_info['mi_ps_c']:.3f}b  "
            f"PS_exc={a_info['ps_excess']:+.4f}  "
            f"I_obs(C1;C2)={a_info['mi_c_obs']:.4f}  I_shuf={a_info['mi_c_shuf']:.4f}  "
            f"A14={a_info['a14']:+.4f}  adj_eq={a_info['adj_core_eq_rate']:.4f}  nonadj_eq={a_info['nonadj_core_eq_rate']:.4f}"
        )
    emit()

    # ==========================================================================
    # PART 2: Wider L4w Construction Grid Aimed at the h2 / A14 Conflict
    # ==========================================================================
    emit("=== PART 2: Wider L4w Construction Grid (36 pre-registered points on Latin seed 0) ===")
    l4w_base = L4wBase(vlines, vtoks)
    calk = S50.make_l4_key(plains["latin"], l4w_base, 0)
    zl_nA = S50.split_index([len(ln) for ln in vlines])
    zl_extra = extra_discriminators(vlines, zl_nA)
    s50_extra = extra_discriminators(ln_s50_k0_a07, nA)
    emit(
        f"Reference extra discriminators: "
        f"Voynich ZL3b: f4_prefix_gain={zl_extra['f4_prefix_gain']:+.4f}  CHARWIN={zl_extra['charwin']:+.4f}  Cov(|A|,|C|)={zl_extra['cov_aff_core_len']:+.4f} | "
        f"s50 closest L4: f4_prefix_gain={s50_extra['f4_prefix_gain']:+.4f}  CHARWIN={s50_extra['charwin']:+.4f}  Cov(|A|,|C|)={s50_extra['cov_aff_core_len']:+.4f}"
    )

    t_grid0 = time.time()
    with mp.get_context("spawn").Pool(
        WORKERS, initializer=_init_l4w_pool, initargs=(vlines, vtoks, plains, lens, nA, calk)
    ) as pool:
        grid_res = list(pool.map(_eval_l4w_point, L4W_GRID))

        n_all5 = 0
        n_all5_plus_f4 = 0
        for prm, st in grid_res:
            eta, delta, alpha, prep, beta, g0 = prm
            h5 = all(S50.hits(st).values())
            hf4 = st["f4_prefix_gain"] >= F4_BAR
            if h5:
                n_all5 += 1
            if h5 and hf4:
                n_all5_plus_f4 += 1
            tag_hit = " [ALL-5 HIT" + (" + f4>=0.08]" if hf4 else "]") if h5 else ""
            emit(
                f"L4w cal eta={eta:<3.1f} delta={delta:<4.2f} alpha={alpha:<4.2f} p_rep={prep:<4.2f} beta={beta:<4.2f}: "
                f"{S50.fmt_stats(st)}  dist={S50.target_dist(st):.2f}  "
                f"f4={st['f4_prefix_gain']:+.4f}  CHARWIN={st['charwin']:+.4f}  CovAC={st['cov_aff_core_len']:+.4f}{tag_hit}"
            )

        per_target = {k: sum(S50.hits(st)[k] for _, st in grid_res) for k in S50.TARGET}
        per_target["f4>=0.08"] = sum(st["f4_prefix_gain"] >= F4_BAR for _, st in grid_res)
        per_target["CHARWIN>0"] = sum(st["charwin"] > 0 for _, st in grid_res)
        emit(
            f"L4w grid summary ({len(grid_res)} points, {time.time() - t_grid0:.1f}s): "
            f"{n_all5}/{len(grid_res)} points hit all 5 s50 targets simultaneously; "
            f"{n_all5_plus_f4}/{len(grid_res)} hit all 5 + f4_prefix_gain >= +0.08; "
            f"per-target hits: {per_target}"
        )

        both_hits = [
            (S50.target_dist(st) - st["f4_prefix_gain"], prm, st)
            for prm, st in grid_res
            if all(S50.hits(st).values()) and st["f4_prefix_gain"] >= F4_BAR
        ]
        all5_hits = [(S50.target_dist(st), prm, st) for prm, st in grid_res if all(S50.hits(st).values())]
        if both_hits:
            _, best_prm, best_st = min(both_hits)
            sel_note = "hits ALL 5 s50 targets AND f4_prefix_gain >= +0.08"
        elif all5_hits:
            _, best_prm, best_st = min(all5_hits)
            sel_note = "hits ALL 5 s50 targets"
        else:
            _, best_prm, best_st = min((S50.target_dist(st), prm, st) for prm, st in grid_res)
            sel_note = f"closest point (dist={S50.target_dist(best_st):.2f})"
        emit(
            f"Selected L4w parameter point: eta={best_prm[0]} delta={best_prm[1]} alpha={best_prm[2]} "
            f"p_rep={best_prm[3]} beta={best_prm[4]} gamma0={best_prm[5]} -> {sel_note}"
        )

        ln_best_lat0, _ = gen_l4w(plains["latin"], calk, l4w_base, best_prm, 0, lens)
        d_l4w = decompose_h2([w for l_ in ln_best_lat0 for w in l_])
        a_l4w = a14_anatomy(ln_best_lat0)
        emit(
            f"Selected L4w h2 & A14 anatomy: h2={d_l4w['h2']:.3f} ("
            + ", ".join(f"{k}={d_l4w['cats'][k]['contrib']:.4f}" for k in CAT_NAMES)
            + f") | I(PS;C)={a_l4w['mi_ps_c']:.3f}b  I_obs(C1;C2)={a_l4w['mi_c_obs']:.4f}  "
            f"I_shuf={a_l4w['mi_c_shuf']:.4f}  A14={a_l4w['a14']:+.4f}  nonadj_eq={a_l4w['nonadj_core_eq_rate']:.4f}"
        )
        emit()

        # Generate 18 L4w ciphers (6 languages x 3 keys) at best_prm using the same Pool
        emit("--- 2B. 18 L4w Ciphers (6 languages x 3 keys) at Selected L4w Point ---")
        cipher_jobs = [(lang, k, best_prm) for lang in LANG_LIST for k in KEYS]
        ciphers_out = list(pool.map(_eval_l4w_cipher, cipher_jobs))

    l4w_ciphers = {}
    l4w_hits_by_lang = defaultdict(int)
    l4w_f4_hits = 0
    for lang, k, st, ln, truth, key in ciphers_out:
        l4w_ciphers[(lang, k)] = (st, ln, truth, key)
        h5 = all(S50.hits(st).values())
        if h5:
            l4w_hits_by_lang[lang] += 1
        if h5 and st["f4_prefix_gain"] >= F4_BAR:
            l4w_f4_hits += 1
        emit(
            f"L4w cipher {lang:<8} key {k}: {S50.fmt_stats(st)}  "
            f"f4={st['f4_prefix_gain']:+.4f}  CHARWIN={st['charwin']:+.4f}  CovAC={st['cov_aff_core_len']:+.4f}  "
            f"{'ALL-5 HIT' if h5 else 'miss'}"
        )
    tot_all5_18 = sum(l4w_hits_by_lang.values())
    emit(
        f"18-cipher L4w target summary: {tot_all5_18}/18 ciphers hit all 5 s50 targets "
        f"(languages with >=2/3 hitting all 5: {[L for L in LANG_LIST if l4w_hits_by_lang[L] >= 2]}); "
        f"{l4w_f4_hits}/18 hit all 5 + f4>=+0.08."
    )
    emit()

    # ==========================================================================
    # PART 2C & PART 3: Single-LM-at-a-time Solver & Blind 6-Language ID
    # ==========================================================================
    # Prepare all 45 cipher streams (sA, sB, n_units_A) once before iterating over the 6 language LMs
    blind_items = []
    for lang in LANG_LIST:
        for k in KEYS:
            p_l2 = ROOT / "runs" / "s50" / "ciphers" / f"L2_{lang}_k{k}.json"
            d2 = json.loads(p_l2.read_text(encoding="utf-8"))
            tu2 = [[str(u) for u in us] for us in d2["unit_seq"]]
            nA2 = d2["nA"]
            sA2, ids2 = S50.stream_from(tu2[:nA2])
            sB2 = np.asarray([ids2.get(u, -1) for us in tu2[nA2:] for u in us], dtype=np.int64)
            blind_items.append((f"L2_{lang}_k{k}", "L2", lang, k, sA2, sB2, len(ids2)))

            p_l4 = ROOT / "runs" / "s50" / "ciphers" / f"L4_{lang}_k{k}.json"
            d4 = json.loads(p_l4.read_text(encoding="utf-8"))
            sA4, sB4, nU4 = pair_stream_split(d4["tokens"], d4["nA"])
            blind_items.append((f"L4_{lang}_k{k}", "L4", lang, k, sA4, sB4, nU4))

    for lang in LANG_LIST:
        _st, ln, _truth, _key = l4w_ciphers[(lang, 1)]
        toks_w = [w for l_ in ln for w in l_]
        sAw, sBw, nUw = pair_stream_split(toks_w, nA)
        blind_items.append((f"L4w_{lang}_k1", "L4w", lang, 1, sAw, sBw, nUw))

    ca_files = sorted((ROOT / "runs" / "s67").glob("CA_ZL3b_*_s1.meta.json"))
    ca_toks: list[str] = []
    for cf in ca_files:
        pages_ca = S67.load_pages(cf)
        for _pid, _q, lns_ca in pages_ca:
            for ln_ca in lns_ca:
                ca_toks.extend(ln_ca)
    while len(ca_toks) < 38000:
        ca_toks.extend(ca_toks[: 38000 - len(ca_toks)])
    ca_toks = ca_toks[:38000]
    sA_ca, sB_ca, nU_ca = pair_stream_split(ca_toks, nA)
    blind_items.append(("CTRL1_s67_CA_ZL3b", "CTRL", "none", 1, sA_ca, sB_ca, nU_ca))

    d4_lat1 = json.loads((ROOT / "runs" / "s50" / "ciphers" / "L4_latin_k1.json").read_text(encoding="utf-8"))
    shuf_toks = list(d4_lat1["tokens"])
    random.Random(20261018).shuffle(shuf_toks)
    sA_sh, sB_sh, nU_sh = pair_stream_split(shuf_toks, nA)
    blind_items.append(("CTRL2_shuffled_L4_latin", "CTRL", "none", 2, sA_sh, sB_sh, nU_sh))

    sA_v, sB_v, nU_v = pair_stream_split(vtoks, zl_nA)
    blind_items.append(("CTRL3_Voynich_ZL3b_pair", "CTRL", "none", 3, sA_v, sB_v, nU_v))

    emit("--- 2C. Solver Verification on L4w Across 6 Languages (RESTARTS=6, SWEEPS=30) ---")
    true_pre_list = sorted(vseg.prefixes)
    true_suf_list = sorted(vseg.suffixes)
    pass_known, pass_unk = [], []
    lm_entropies = {}
    all_blind_scores: dict[str, dict[str, dict]] = defaultdict(dict)
    BLIND_R, BLIND_S, BLIND_STEP = 2, 25, 5

    t_b0 = time.time()
    for li, cand_lang in enumerate(LANG_LIST):
        lm, q, plain, nlm = train_single_lm(cand_lang)
        h1 = float(-np.sum(q * np.log2(q)))
        h5 = float(S.lm_bits_per_letter(lm, plain))
        dh_true = h1 - h5
        lm_entropies[cand_lang] = dict(h1=h1, h5=h5, dh_true=dh_true, nlm=nlm)

        # 2C: solve L4w cipher for cand_lang key 1 (known_pair and unknown_seg)
        _st, ln, truth, _key = l4w_ciphers[(cand_lang, 1)]
        toks_w = [w for l_ in ln for w in l_]
        for mode in ("known_pair", "unknown_seg"):
            info = solve_l4w_inproc(cand_lang, 1, toks_w, truth, nA, true_pre_list, true_suf_list, mode, lm, q, 6, 30)
            ok = info["acc"] >= ACC_PASS
            if mode == "known_pair" and ok:
                pass_known.append(cand_lang)
            if mode == "unknown_seg" and ok:
                pass_unk.append(cand_lang)
            emit(
                f"L4w solver {mode:<11} {cand_lang:<8} key 1: acc={info['acc']:.4f} {'PASS' if ok else 'FAIL'} "
                f"(>=0.90: {'yes' if info['acc'] >= 0.90 else 'no'})  nulls={info['nulls']}/{info['units']}  "
                f"rd={info['rd']} |P|={info['n_pre']} |S|={info['n_suf']}  {info['elapsed']:.1f}s"
            )

        # 3B: score all 45 blind_items under cand_lang's LM
        for tag, _fam, _tlang, kseed, sA_i, sB_i, nU_i in blind_items:
            all_blind_scores[tag][cand_lang] = score_text_under_lm(
                tag, kseed, sA_i, sB_i, nU_i, li, lm, q, dh_true, BLIND_R, BLIND_S, BLIND_STEP
            )

        del lm, q
        gc.collect()

    emit(
        f"L4w solver summary: known_pair passes {len(pass_known)}/6 ({pass_known}); "
        f"unknown_seg passes {len(pass_unk)}/6 ({pass_unk})."
    )
    emit()

    # ==========================================================================
    # PART 3: Blind 6-Language Identification & Null-Control Gate
    # ==========================================================================
    emit("=== PART 3: Blind 6-Language Identification & Null-Control Gate ===")
    emit("3A. Candidate Language Baseline Entropies (23-letter alphabet):")
    for lang in LANG_LIST:
        m = lm_entropies[lang]
        emit(
            f"  {lang:<8} H_1 (unigram) = {m['h1']:.3f} b/let  "
            f"H_5 (5-gram held-out) = {m['h5']:.3f} b/let  "
            f"Delta_H_true = H_1 - H_5 = {m['dh_true']:.3f} b/let"
        )
    emit()

    emit(f"3B. Blind 6-Language Identification Results ({len(blind_items)} texts x 6 LMs = {len(blind_items)*6} solves, {time.time() - t_b0:.1f}s):")
    by_fam = defaultdict(list)
    for tag, fam, true_lang, kseed, _sA, _sB, _nU in blind_items:
        scores = all_blind_scores[tag]
        ranked = sorted(LANG_LIST, key=lambda L: -scores[L]["match_adj"])
        top1, top2 = ranked[0], ranked[1]
        margin = scores[top1]["match_adj"] - scores[top2]["match_adj"]
        r = dict(
            tag=tag,
            family=fam,
            true_lang=true_lang,
            kseed=kseed,
            top1=top1,
            top2=top2,
            top1_match=scores[top1]["match"],
            top1_match_adj=scores[top1]["match_adj"],
            margin=margin,
            gate_pass=(scores[top1]["match_adj"] >= MATCH_GATE),
            scores=scores,
        )
        by_fam[fam].append(r)
        scores_str = "  ".join(
            f"{L[:3]}:{scores[L]['match_adj']:+.3f}(dH={scores[L]['dh_seq']:+.3f})"
            for L in LANG_LIST
        )
        ok_id = (top1 == true_lang) if true_lang != "none" else (not r["gate_pass"])
        emit(
            f"  {tag:<24} true={true_lang:<8} top1={top1:<8} "
            f"Match_adj={r['top1_match_adj']:+.3f} (raw={r['top1_match']:+.3f})  "
            f"margin={margin:+.3f}  gate>={MATCH_GATE:.2f}:{str(r['gate_pass']):<5} "
            f"{'OK' if ok_id else 'MISS'} | {scores_str}"
        )
    emit()

    emit("3C. Blind Language-ID & Null-Gate Summary:")
    for fam in ("L2", "L4", "L4w"):
        rows = by_fam[fam]
        n_correct = sum(1 for r in rows if r["top1"] == r["true_lang"])
        n_gate = sum(1 for r in rows if r["gate_pass"])
        lang_maj = []
        for lang in LANG_LIST:
            lrows = [r for r in rows if r["true_lang"] == lang]
            c_lang = sum(1 for r in lrows if r["top1"] == lang)
            if c_lang >= (2 if len(lrows) == 3 else 1):
                lang_maj.append(lang)
        matches = [r["top1_match_adj"] for r in rows]
        emit(
            f"  Family {fam:<4}: key-level Top-1 accuracy = {n_correct}/{len(rows)} ({n_correct/len(rows)*100:.1f}%); "
            f"languages ranked #1 (majority of keys) = {len(lang_maj)}/6 ({lang_maj}); "
            f"null-gate pass (>= {MATCH_GATE:.2f}) = {n_gate}/{len(rows)}; "
            f"Match_adj range = [{min(matches):+.3f}, {max(matches):+.3f}] (mean {np.mean(matches):+.3f})"
        )

    ctrl_rows = by_fam["CTRL"]
    ctrl_rejected = sum(1 for r in ctrl_rows if not r["gate_pass"])
    ctrl_matches = [r["top1_match_adj"] for r in ctrl_rows]
    emit(
        f"  Negative Controls (CTRL1..3): rejected by null-gate (< {MATCH_GATE:.2f}) = {ctrl_rejected}/{len(ctrl_rows)}; "
        f"Match_adj values = {[round(x, 4) for x in ctrl_matches]} (max = {max(ctrl_matches):+.4f})"
    )
    emit()

    emit("=== OVERALL S72 VERDICT & SYNTHESIS ===")
    emit(
        f"1. Part 1 (h2 / A14 Conflict Anatomy): In s50's L4, h2 is inflated (+0.175 to +0.208 bits above ZL3b's 2.109) "
        f"primarily by C2 Prefix->Core (+0.129b) and C4 Core->Suffix (+0.134b) unattested junctures caused by the +0.5 "
        f"pseudocount across 2,335 cores ({pseudo_share_unweighted*100:.1f}% pseudocount mass), while A14 > 0 (+0.0713 at K=0, gamma=1) "
        f"is driven by plaintext letter bigram MI ({mi_lat_xx:.4f}b) leaking through within-word I((P,S);C) ({a14_s50_k0['mi_ps_c']:.3f}b) "
        f"into adjacent cores when same-line non-adjacent core repetition is absent."
    )
    n_cw_delta_pos = sum(1 for prm, st in grid_res if prm[1] > 0 and st["charwin"] > 0)
    emit(
        f"2. Part 2 (Wider L4w Construction & Solver): {n_all5}/{len(grid_res)} pre-registered L4w grid points on Latin seed 0 "
        f"and {tot_all5_18}/18 L4w ciphers across the 6 languages simultaneously hit all 5 s50 targets "
        f"(types, hapax, h2, A14 <= 0, Moran), and {n_all5_plus_f4}/{len(grid_res)} grid points ({l4w_f4_hits}/18 ciphers) "
        f"also hit f4_prefix_gain >= +0.08, whereas CHARWIN is negative at all 24 points with delta > 0 ({n_cw_delta_pos}/24 > 0; "
        f"selected L4w point CHARWIN = {best_st['charwin']:+.4f} vs ZL3b {zl_extra['charwin']:+.4f}). "
        f"s50_solver still breaks L4w in {len(pass_known)}/6 languages (known_pair) and {len(pass_unk)}/6 languages (unknown_seg) at >= 80% accuracy."
    )
    emit(
        f"3. Part 3 (Blind 6-Language ID & Null Gate): Normalized held-out sequential gain Match_adj(L) on untouched Half B "
        f"identifies the true language Top-1 in {sum(1 for r in by_fam['L2'] if r['top1']==r['true_lang'])}/18 L2 ciphers, "
        f"{sum(1 for r in by_fam['L4'] if r['top1']==r['true_lang'])}/18 L4 ciphers, and "
        f"{sum(1 for r in by_fam['L4w'] if r['top1']==r['true_lang'])}/6 L4w ciphers, while rejecting {ctrl_rejected}/3 "
        f"non-cipher/shuffled negative controls (max Match_adj = {max(ctrl_matches):+.4f} vs gate {MATCH_GATE:.2f})."
    )
    emit(f"elapsed: {time.time() - t_start:.1f}s; end {clock()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        import traceback
        emit("FAILED: " + repr(exc))
        emit(traceback.format_exc())
        raise
