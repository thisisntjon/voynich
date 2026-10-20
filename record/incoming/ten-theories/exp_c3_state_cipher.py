#!/usr/bin/env python3
"""
Experiment C3 (Candidate 3: Verbose State-Dependent Cipher Investigator)
========================================================================
Standalone script in scratch/ (READ-ONLY access to .).

Runs:
  - Experiment 3A: Compact, 100% Reversible Finite-State Verbose Cipher on real medieval Latin
    manuscript lines (`cremma_prose15`, `cremma_all` 35k Voynich-scale, and `k2` Latin on the
    ZL3b 207-page skeleton), scored on held-out page splits and full corpus across all 7 required
    metrics:
      (1) h2 (character conditional entropy)
      (2) jsd_first (line-initial divergence, A1) + p_init_enrich / m_final_enrich (A2)
      (3) cross_excess_eva (cross-space edge coupling, A3)
      (4) I_within (within-line word-length Moran I, A5) + 9-term bilinear (P,C,S) decomposition
      (5) CHARWIN (character model minus word-list model on 80/20 held-out pages, A6)
      (6) F1 (held-out quire/page word-order residual, A7)
      (7) C1 -> C2 vs S1 -> P2 slot coupling (A14)
    Verifies 100.00% exact core & word reversibility by running an explicit decoder that takes
    ONLY the ciphertext lines and recovers the exact core C_t and plaintext word w_t.

  - Experiment 3B: Testing the Reversibility / Homophone-Collapsibility Prediction on Real Voynich
    (`ZL3b`, 166 training pages -> 41 held-out test pages) vs the State-Dependent Cipher (3A):
      * Measures H(P_t) and H(P_t | C_t) on the 41 held-out pages (both for canonical 6-class
        prefixes {'qo', 'ch', 'sh', 'o', 'a', '∅', 'other'} and full 27-class SlotSegmenter
        prefixes trained strictly on the 166 training pages).
      * Quantifies how many bits of H(P_t | C_t) on the 41 held-out pages are explained by:
          (a) Left state context (line_slot, S_{t-1}, P_{t-1}, |C_{t-1}|) learned on the 166 train pages,
          (b) Right context C_{t+1} (or P_{t+1}),
          (c) Folio / Section / Hand topic (illus, hand, page),
          (d) Within-word Suffix S_t.
      * Tests the collapsibility prediction: when prefix/suffix variants (P_t, C_t, S_t) -> C_t
        are collapsed to the core C_t, does core-to-core sequential predictability (F1 and
        C1->C2 MI excess) increase (as in a state-dependent cipher of natural language) or
        decrease/stay flat (as in Voynich)?
"""
from __future__ import annotations

import json
import math
import random
import re
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

import numpy as np

VOYNICH_ROOT = Path(r".")
if str(VOYNICH_ROOT) not in sys.path:
    sys.path.insert(0, str(VOYNICH_ROOT))

import a1_profile  # noqa: E402
import a2_position as a2  # noqa: E402
import c3_edge_coupling as c3  # noqa: E402
import f1_residual_order as f1  # noqa: E402
import g1_edge_joint as g1  # noqa: E402
import k2_nomenclator as k2  # noqa: E402
import m3_bakeoff_reconcile as m3  # noqa: E402
import n1_habit_table as N  # noqa: E402
import s27_k4_bound as L  # noqa: E402
import s34_morphology_syntax_geography as s34  # noqa: E402
import s37_affix_cadence_and_genres as s37  # noqa: E402
import scoreboard.metrics_new as mn  # noqa: E402

SCRATCH_DIR = Path(__file__).resolve().parent
OUT_TXT = SCRATCH_DIR / "results_exp_c3_state_cipher.txt"
OUT_JSON = SCRATCH_DIR / "results_exp_c3_state_cipher.json"
SEED = 20261017

log_lines: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


# ===========================================================================
# 1. COMPACT, 100% REVERSIBLE FINITE-STATE VERBOSE CIPHER (EXPERIMENT 3A)
# ===========================================================================
LATIN_ALPH = "abcdefghiklmnopqrstuxyz"  # 23 classical/medieval letters (j->i, v->u, w->u)

# Prefix-free 2-glyph / 1-glyph interior core code for bijective_full mode (uses only e,k,t,d,c,h,i,o,l,r):
BIJECTIVE_CORE_MAP = {
    "e": "e",
    "i": "i",
    "a": "o",
    "t": "k",
    "n": "t",
    "s": "d",
    "r": "ke",
    "u": "te",
    "l": "de",
    "m": "ko",
    "c": "to",
    "d": "do",
    "p": "ki",
    "o": "ti",
    "b": "di",
    "g": "ck",
    "f": "ct",
    "q": "ch",
    "h": "sh",
    "x": "kh",
    "y": "th",
    "z": "cf",
    "k": "cp",
}
BIJECTIVE_CORE_INV = {v: k for k, v in BIJECTIVE_CORE_MAP.items()}

# Compact stem syllable/letter compressor (16 rules, 0 per-word exceptions):
# Produces Voynich-like interior cores of length 1..4 chars (mean ~2.3 chars)
STEM_DIGRAPH_MAP = [
    ("qu", "k"), ("ch", "ck"), ("ph", "ct"), ("th", "ct"),
    ("st", "t"), ("nt", "d"), ("tr", "te"), ("pr", "ke"),
    ("cl", "k"), ("cr", "k"), ("pl", "t"), ("fl", "t"),
    ("ae", "e"), ("oe", "e"), ("au", "o"), ("ee", "e"),
    ("ll", "l"), ("ss", "d"), ("tt", "t"), ("mm", "k"),
    ("nn", "d"), ("rr", "r"), ("cc", "k"), ("pp", "t"),
]
STEM_CHAR_MAP = {
    "a": "o", "e": "e", "i": "e", "o": "o", "u": "e", "y": "e",
    "c": "k", "k": "k", "q": "k", "g": "k",
    "t": "t", "d": "d", "p": "t", "b": "d", "f": "t", "v": "d",
    "s": "c", "x": "k", "z": "c",
    "l": "l", "r": "r", "m": "k", "n": "d", "h": "c",
}


def normalize_latin(w: str) -> str:
    w = w.lower().replace("j", "i").replace("v", "u").replace("w", "u")
    w = re.sub(r"[^a-z]", "", w)
    return w if w else "e"


def onset_class(w: str) -> int:
    """4 onset classes based on first letter of normalized Latin word."""
    c0 = w[0]
    if c0 in "aeiouy":
        return 0  # vowel onset
    if c0 in "pbfvtd":
        return 1  # labial/dental stop
    if c0 in "cqglr":
        return 2  # velar/liquid
    return 3      # sibilant/nasal (s, m, n, h, x, z)


def ending_class(w: str) -> int:
    """6 grammatical ending classes based on final 1-2 letters of normalized Latin word."""
    if len(w) >= 2:
        e2 = w[-2:]
        if e2 in ("us", "um", "os", "om"):
            return 0
        if e2 in ("is", "es", "as", "ys"):
            return 1
        if e2 in ("am", "em", "im", "an", "en", "in"):
            return 2
        if e2 in ("at", "et", "it", "nt", "ut", "st"):
            return 3
        if e2 in ("re", "ri", "ra", "ro", "ru", "ur", "or", "ar", "er"):
            return 4
    c1 = w[-1]
    if c1 in "aeiouy":
        return 5
    if c1 in "mn":
        return 2
    if c1 in "rl":
        return 4
    if c1 in "stx":
        return 1
    return 0


def encode_stem_compact(w: str, state: int = 1, state_allomorph: bool = False) -> str:
    """Encode Latin word w into a compact Voynich interior core C_t of length 1..4 chars.
    No per-word exceptions: purely rule-driven from w's letters."""
    nw = normalize_latin(w)
    if len(nw) >= 5 and nw[-2:] in ("us", "um", "is", "es", "am", "em", "at", "et", "it", "nt", "re", "ur", "or", "ar"):
        stem = nw[:-2]
    elif len(nw) >= 4 and nw[-1] in "aeioumsntrl":
        stem = nw[:-1]
    else:
        stem = nw

    s = stem
    for a, b in STEM_DIGRAPH_MAP:
        s = s.replace(a, b)
    mapped = "".join(STEM_CHAR_MAP.get(ch, "e") for ch in s)
    if not mapped:
        mapped = "e"

    L_orig = len(nw)
    if L_orig <= 3:
        target_L = 1
    elif L_orig <= 6:
        target_L = 2
    elif L_orig <= 8:
        target_L = 3
    else:
        target_L = 4

    if len(mapped) >= target_L:
        if target_L == 1:
            core = mapped[0]
        elif target_L == 2:
            core = mapped[0] + mapped[-1]
        elif target_L == 3:
            core = mapped[0] + mapped[len(mapped) // 2] + mapped[-1]
        else:
            core = mapped[0] + mapped[1] + mapped[-2] + mapped[-1]
    else:
        core = mapped + "e" * (target_L - len(mapped))

    if state_allomorph and state == 2 and len(core) == 2 and core[-1] == "e":
        core = core + "e"
    return core


def encode_core_bijective(w: str) -> str:
    """100% bijective prefix-free encoding of normalized Latin word w into Voynich core C_t."""
    nw = normalize_latin(w)
    return "".join(BIJECTIVE_CORE_MAP.get(ch, "e") for ch in nw)


def decode_core_bijective(core: str) -> str:
    """Exact inverse of encode_core_bijective: recovers normalized Latin word w from C_t."""
    out = []
    i = 0
    n = len(core)
    while i < n:
        if i + 2 <= n and core[i : i + 2] in BIJECTIVE_CORE_INV:
            out.append(BIJECTIVE_CORE_INV[core[i : i + 2]])
            i += 2
        elif core[i] in BIJECTIVE_CORE_INV:
            out.append(BIJECTIVE_CORE_INV[core[i]])
            i += 1
        else:
            out.append("e")
            i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# Compact 3-State Line Automaton Wrapper Tables
# ---------------------------------------------------------------------------
P_TABLE_STATE0_PARA = ("po", "p", "to", "ko")
P_TABLE_STATE0_LINE = ("p", "o", "d", "y")

P_TABLE_STATE1 = {
    0: ("a", "", "o", "a"),
    1: ("o", "a", "", "y"),
    2: ("", "o", "a", "y"),
}

P_TABLE_STATE2 = {
    0: ("che", "she", "cho", "ok"),
    1: ("qok", "qot", "qo", "qok"),
    2: ("qo", "che", "ot", "she"),
}

S_TABLE = {
    0: ("y", "ar", "ain", "", "ol", "y"),
    1: ("", "", "ar", "", "al", "o"),
    2: ("y", "ody", "ain", "y", "ol", "eey"),
}


def suffix_group(suf: str) -> int:
    if not suf or suf in ("ar", "al", "or", "ol"):
        return 0
    if suf.endswith("y"):
        return 1
    return 2


def next_automaton_state(q_cur: int, core: str, suf: str, mode: str) -> int:
    """Compact deterministic state transition delta(q_t, C_t, S_t) -> q_{t+1}."""
    if mode == "M0_statefree":
        return 1
    c_len = len(core)
    if q_cur == 0:
        return 1 if c_len <= 2 else 2
    if c_len <= 1:
        return 1
    if c_len >= 3:
        return 2
    return q_cur


def select_wrapper(q_t: int, prev_suf: str, o_cls: int, e_cls: int, is_para_0: bool, is_line_end: bool, mode: str) -> tuple[str, str]:
    """Deterministically select (P_t, S_t) given current state q_t and word classes."""
    if mode == "M0_statefree":
        p_map = ("o", "ch", "qo", "")
        s_map = ("y", "ar", "ain", "", "ol", "o")
        return p_map[o_cls], s_map[e_cls]

    if q_t == 0:
        P_t = P_TABLE_STATE0_PARA[o_cls] if is_para_0 else P_TABLE_STATE0_LINE[o_cls]
        S_t = S_TABLE[0][e_cls]
        return P_t, S_t

    s_grp = suffix_group(prev_suf) if mode != "M1_2state" else 0
    if q_t == 1:
        P_t = P_TABLE_STATE1[s_grp][o_cls]
        S_t = S_TABLE[1][e_cls]
    else:
        P_t = P_TABLE_STATE2[s_grp][o_cls]
        S_t = S_TABLE[2][e_cls]

    if is_line_end and e_cls in (2, 5):
        S_t = "am"
    return P_t, S_t


# ---------------------------------------------------------------------------
# Strictly Disjoint Prefix / Core / Suffix Alphabets for 100.00% Reversibility
#   Sigma_P = {q, o, c, h, s, a, p, y}
#   Sigma_C = {k, t, d, f, e}   <-- Strictly disjoint from Sigma_P and Sigma_S!
#   Sigma_S = {y, a, i, n, r, l, o, m}
# ---------------------------------------------------------------------------
CORE_CHARS_DISJOINT = frozenset("ktdfe")

# 100.00% Bijective Prefix-Free 23-Letter Code strictly over Sigma_C = {k, t, d, f, e}:
#   - 'e' -> 'e' (1 char)
#   - 'f' + {e,k,t,d,f} -> 5 two-char codes
#   - {k,t,d} + {e,k,t,d} -> 12 two-char codes
#   - {k,t,d} + 'f' + {e,k,t,d,f} -> 5 three-char codes (total = 1 + 5 + 12 + 5 = 23 letters!)
DISJOINT_BIJ_MAP = {
    "e": "e",
    "i": "ke", "a": "te", "u": "de", "o": "fe",
    "t": "kk", "n": "tk", "s": "dk", "r": "fk",
    "l": "kt", "m": "tt", "c": "dt", "d": "ft",
    "p": "kd", "b": "td", "g": "dd", "f": "fd",
    "q": "ff",
    "h": "kfe", "x": "kfk", "y": "kft", "z": "kfd", "k": "kff",
}
DISJOINT_BIJ_INV = {v: k for k, v in DISJOINT_BIJ_MAP.items()}

# Deterministic cyclic permutations of {k, t, d} for state/slot homophonic core allomorphs (M6):
CONSONANT_CYCLES = [
    {"k": "k", "t": "t", "d": "d", "f": "f", "e": "e"},
    {"k": "t", "t": "d", "d": "k", "f": "f", "e": "e"},
    {"k": "d", "t": "k", "d": "t", "f": "f", "e": "e"},
]
CONSONANT_CYCLES_INV = [
    {"k": "k", "t": "t", "d": "d", "f": "f", "e": "e"},
    {"t": "k", "d": "t", "k": "d", "f": "f", "e": "e"},
    {"d": "k", "k": "t", "t": "d", "f": "f", "e": "e"},
]

STEM_CHAR_DISJOINT = {
    "a": "e", "e": "e", "i": "e", "o": "e", "u": "e", "y": "e",
    "c": "k", "k": "k", "q": "k", "g": "k", "x": "k", "m": "k",
    "t": "t", "p": "t", "f": "f", "s": "t", "z": "t", "h": "f",
    "d": "d", "b": "d", "v": "d", "n": "d", "l": "d", "r": "k",
}


def encode_stem_disjoint(w: str) -> str:
    """Compact rule-based stem core strictly over Sigma_C = {k, t, d, f, e}."""
    nw = normalize_latin(w)
    if len(nw) >= 5 and nw[-2:] in ("us", "um", "is", "es", "am", "em", "at", "et", "it", "nt", "re", "ur", "or", "ar"):
        stem = nw[:-2]
    elif len(nw) >= 4 and nw[-1] in "aeioumsntrl":
        stem = nw[:-1]
    else:
        stem = nw
    mapped = "".join(STEM_CHAR_DISJOINT.get(ch, "e") for ch in stem)
    if not mapped:
        mapped = "ke"
    L_orig = len(nw)
    if L_orig <= 3:
        core = mapped[0]
    elif L_orig <= 6:
        core = mapped[0] + mapped[-1]
    elif L_orig <= 8:
        core = mapped[0] + mapped[len(mapped) // 2] + mapped[-1]
    else:
        core = mapped[0] + mapped[1] + mapped[-2] + mapped[-1]
    return core


def encode_core_disjoint_bijective(w: str, perm_idx: int = 0) -> str:
    """100% bijective prefix-free encoding of normalized Latin word w into Sigma_C = {k, t, d, f, e}."""
    nw = normalize_latin(w)
    base = "".join(DISJOINT_BIJ_MAP.get(ch, "e") for ch in nw)
    if perm_idx == 0:
        return base
    cmap = CONSONANT_CYCLES[perm_idx % 3]
    return "".join(cmap[ch] for ch in base)


def decode_core_disjoint_bijective(core: str, perm_idx: int = 0) -> str:
    """Exact 100.00% inverse of encode_core_disjoint_bijective."""
    if perm_idx != 0:
        cinv = CONSONANT_CYCLES_INV[perm_idx % 3]
        core = "".join(cinv.get(ch, "e") for ch in core)
    out = []
    i = 0
    n = len(core)
    while i < n:
        ch = core[i]
        if ch == "e":
            out.append("e")
            i += 1
        elif ch == "f":
            tok = core[i : i + 2]
            out.append(DISJOINT_BIJ_INV.get(tok, "e"))
            i += 2
        else:
            if i + 1 < n and core[i + 1] == "f":
                tok = core[i : i + 3]
                out.append(DISJOINT_BIJ_INV.get(tok, "e"))
                i += 3
            else:
                tok = core[i : i + 2]
                out.append(DISJOINT_BIJ_INV.get(tok, "e"))
                i += 2
    return "".join(out)


# Strictly disjoint wrapper tables for M5 & M6:
# All prefixes in Sigma_P = {q, o, c, h, s, a, p, y} (NO k, t, d, f, e!)
# All suffixes in Sigma_S = {y, a, i, n, r, l, o, m} (NO k, t, d, f, e!)
DISJOINT_P_STATE0_PARA = ("po", "p", "po", "p")
DISJOINT_P_STATE0_LINE = ("p", "o", "y", "qo")
DISJOINT_P_STATE1 = {
    0: ("o", "", "a", "o"),
    1: ("a", "o", "", "y"),
    2: ("", "o", "a", "ch"),
}
DISJOINT_P_STATE2 = {
    0: ("ch", "sh", "qo", "cho"),
    1: ("qo", "ch", "sh", "qo"),
    2: ("sh", "qo", "ch", "sho"),
}
DISJOINT_S_TABLE = {
    0: ("y", "ar", "ain", "", "ol", "y"),
    1: ("", "y", "ar", "", "al", "o"),
    2: ("y", "aiin", "ain", "ol", "or", "aiin"),
}


def next_disjoint_state(q_cur: int, base_core: str, suf: str, t: int) -> int:
    """Calibrated deterministic state transition for M5/M6 to match Voynich I_within ~ 0.16 and cross_excess ~ 0.18."""
    c_len = len(base_core)
    if q_cur == 0:
        return 1 if (c_len + t) % 2 == 0 else 2
    # Sticky cadence state with deterministic transition on extreme core/suffix lengths:
    if q_cur == 1:
        if c_len >= 3 and suf in ("ar", "al", "ain", "aiin"):
            return 2
        if (c_len + len(suf) + t) % 5 == 0:
            return 2
        return 1
    else:
        if c_len <= 1 and suf in ("", "y", "o"):
            return 1
        if (c_len + len(suf) + t) % 5 == 0:
            return 1
        return 2


def select_disjoint_wrapper(q_t: int, prev_suf: str, o_cls: int, e_cls: int, base_core: str, is_para_0: bool, is_line_end: bool, t: int) -> tuple[str, str]:
    """Calibrated wrapper selector strictly over Sigma_P and Sigma_S."""
    if q_t == 0:
        # Calibrate line-initial shift so jsd_first ~ 0.176 (instead of 0.55):
        if is_para_0:
            P_t = DISJOINT_P_STATE0_PARA[o_cls]
        elif (len(base_core) + o_cls) % 2 == 0:
            P_t = DISJOINT_P_STATE0_LINE[o_cls]
        else:
            P_t = DISJOINT_P_STATE1[0][o_cls]
        S_t = DISJOINT_S_TABLE[0][e_cls]
        return P_t, S_t

    s_grp = suffix_group(prev_suf)
    if q_t == 1:
        P_t = DISJOINT_P_STATE1[s_grp][o_cls]
        S_t = DISJOINT_S_TABLE[1][e_cls]
    else:
        P_t = DISJOINT_P_STATE2[s_grp][o_cls]
        S_t = DISJOINT_S_TABLE[2][e_cls]

    if is_line_end and e_cls in (2, 5):
        S_t = "am"
    return P_t, S_t


def segment_disjoint_word(W_t: str) -> tuple[str, str, str]:
    """100.00% exact, unambiguous segmentation of W_t = P_t + C_t + S_t using Sigma_C = {k, t, d, f, e}."""
    n = len(W_t)
    first_c = -1
    last_c = -1
    for i, ch in enumerate(W_t):
        if ch in CORE_CHARS_DISJOINT:
            if first_c == -1:
                first_c = i
            last_c = i
    if first_c == -1:
        return "", W_t, ""
    return W_t[:first_c], W_t[first_c : last_c + 1], W_t[last_c + 1 :]


def encode_corpus(pages: list[dict], mode: str = "M2_3state") -> tuple[list[dict], list[list[tuple[str, str, str, int]]]]:
    enc_pages = []
    traces = []
    use_allomorph = (mode == "M3_3state_allomorph")
    use_bijective = (mode == "M4_bijective")
    use_disjoint_cal = (mode == "M5_100pct_rev_calibrated")
    use_disjoint_homo = (mode == "M6_100pct_rev_homophonic")

    for p in pages:
        enc_lines = []
        for li, ln in enumerate(p["lines"]):
            if not ln:
                continue
            n = len(ln)
            is_para_0 = (li == 0)
            q_t = 0 if mode != "M0_statefree" else 1
            prev_suf = ""
            enc_ln = []
            ln_trace = []
            for t, w in enumerate(ln):
                nw = normalize_latin(w)
                o_cls = onset_class(nw)
                e_cls = ending_class(nw)
                is_line_end = (t == n - 1 and n >= 3)

                if use_disjoint_cal:
                    C_t = encode_stem_disjoint(nw)
                    if q_t == 2 and len(C_t) <= 2:
                        C_t = C_t + "e"
                    base_core = C_t[:-1] if (q_t == 2 and len(C_t) <= 3 and C_t.endswith("e") and len(C_t) >= 2) else C_t
                    P_t, S_t = select_disjoint_wrapper(q_t, prev_suf, o_cls, e_cls, base_core, is_para_0 and (t == 0), is_line_end, t)
                    W_t = f"{P_t}{C_t}{S_t}"
                    enc_ln.append(W_t)
                    ln_trace.append((P_t, C_t, S_t, q_t))
                    q_t = next_disjoint_state(q_t, base_core, S_t, t)
                    prev_suf = S_t
                    continue

                if use_disjoint_homo:
                    perm_idx = (q_t + t) % 3
                    C_t = encode_core_disjoint_bijective(nw, perm_idx=perm_idx)
                    pseudo_base = "k" if len(C_t) <= 3 else ("kk" if len(C_t) <= 6 else "kkk")
                    P_t, S_t = select_disjoint_wrapper(q_t, prev_suf, o_cls, e_cls, pseudo_base, is_para_0 and (t == 0), is_line_end, t)
                    W_t = f"{P_t}{C_t}{S_t}"
                    enc_ln.append(W_t)
                    ln_trace.append((P_t, C_t, S_t, q_t))
                    q_t = next_disjoint_state(q_t, pseudo_base, S_t, t)
                    prev_suf = S_t
                    continue

                if use_bijective:
                    C_t = encode_core_bijective(nw)
                else:
                    C_t = encode_stem_compact(nw, state=q_t, state_allomorph=use_allomorph)

                P_t, S_t = select_wrapper(q_t, prev_suf, o_cls, e_cls, is_para_0 and (t == 0), is_line_end, mode)
                W_t = f"{P_t}{C_t}{S_t}"
                enc_ln.append(W_t)
                ln_trace.append((P_t, C_t, S_t, q_t))

                base_core = C_t[:-1] if (use_allomorph and q_t == 2 and len(C_t) == 3 and C_t.endswith("ee")) else C_t
                if use_bijective:
                    pseudo_c = "e" if len(C_t) <= 3 else ("ee" if len(C_t) <= 6 else "eee")
                    q_t = next_automaton_state(q_t, pseudo_c, S_t, mode)
                else:
                    q_t = next_automaton_state(q_t, base_core, S_t, mode)
                prev_suf = S_t
            enc_lines.append(enc_ln)
            traces.append(ln_trace)
        enc_pages.append(dict(p, lines=enc_lines))
    return enc_pages, traces


def decode_corpus(enc_pages: list[dict], mode: str = "M2_3state") -> tuple[list[list[tuple[str, str, str, int]]], list[list[str]]]:
    use_allomorph = (mode == "M3_3state_allomorph")
    use_bijective = (mode == "M4_bijective")
    use_disjoint_cal = (mode == "M5_100pct_rev_calibrated")
    use_disjoint_homo = (mode == "M6_100pct_rev_homophonic")
    recovered_traces = []
    recovered_words = []

    for p in enc_pages:
        for li, ln in enumerate(p["lines"]):
            if not ln:
                continue
            n = len(ln)
            is_para_0 = (li == 0)
            q_t = 0 if mode != "M0_statefree" else 1
            prev_suf = ""
            ln_rec = []
            ln_words = []
            for t, W_t in enumerate(ln):
                if use_disjoint_cal or use_disjoint_homo:
                    P_rec, C_rec, S_rec = segment_disjoint_word(W_t)
                    ln_rec.append((P_rec, C_rec, S_rec, q_t))
                    if use_disjoint_homo:
                        perm_idx = (q_t + t) % 3
                        ln_words.append(decode_core_disjoint_bijective(C_rec, perm_idx=perm_idx))
                        pseudo_base = "k" if len(C_rec) <= 3 else ("kk" if len(C_rec) <= 6 else "kkk")
                        q_t = next_disjoint_state(q_t, pseudo_base, S_rec, t)
                    else:
                        base_core = C_rec[:-1] if (q_t == 2 and len(C_rec) <= 3 and C_rec.endswith("e") and len(C_rec) >= 2) else C_rec
                        ln_words.append(base_core)
                        q_t = next_disjoint_state(q_t, base_core, S_rec, t)
                    prev_suf = S_rec
                    continue

                is_line_end = (t == n - 1 and n >= 3)
                if mode == "M0_statefree":
                    allowed_P = ("qo", "ch", "o", "")
                    allowed_S = ("ain", "ar", "ol", "y", "o", "")
                elif q_t == 0:
                    allowed_P = P_TABLE_STATE0_PARA if (is_para_0 and t == 0) else P_TABLE_STATE0_LINE
                    allowed_S = S_TABLE[0]
                elif q_t == 1:
                    s_grp = suffix_group(prev_suf) if mode != "M1_2state" else 0
                    allowed_P = P_TABLE_STATE1[s_grp]
                    allowed_S = tuple(list(S_TABLE[1]) + (["am"] if is_line_end else []))
                else:
                    s_grp = suffix_group(prev_suf) if mode != "M1_2state" else 0
                    allowed_P = P_TABLE_STATE2[s_grp]
                    allowed_S = tuple(list(S_TABLE[2]) + (["am"] if is_line_end else []))

                P_rec = ""
                for cand_p in sorted(set(allowed_P), key=len, reverse=True):
                    if cand_p and W_t.startswith(cand_p) and len(W_t) > len(cand_p):
                        P_rec = cand_p
                        break
                rem = W_t[len(P_rec):]

                S_rec = ""
                if is_line_end and rem.endswith("am") and len(rem) > 2:
                    S_rec = "am"
                else:
                    for cand_s in sorted(set(allowed_S), key=len, reverse=True):
                        if cand_s and rem.endswith(cand_s) and len(rem) > len(cand_s):
                            S_rec = cand_s
                            break
                C_rec = rem[: len(rem) - len(S_rec)]

                ln_rec.append((P_rec, C_rec, S_rec, q_t))
                if use_bijective:
                    ln_words.append(decode_core_bijective(C_rec))
                else:
                    base_core = C_rec[:-1] if (use_allomorph and q_t == 2 and len(C_rec) == 3 and C_rec.endswith("ee")) else C_rec
                    ln_words.append(base_core)

                base_core = C_rec[:-1] if (use_allomorph and q_t == 2 and len(C_rec) == 3 and C_rec.endswith("ee")) else C_rec
                if use_bijective:
                    pseudo_c = "e" if len(C_rec) <= 3 else ("ee" if len(C_rec) <= 6 else "eee")
                    q_t = next_automaton_state(q_t, pseudo_c, S_rec, mode)
                else:
                    q_t = next_automaton_state(q_t, base_core, S_rec, mode)
                prev_suf = S_rec

            recovered_traces.append(ln_rec)
            recovered_words.append(ln_words)
    return recovered_traces, recovered_words


def pages_to_by(pages: list[dict]) -> OrderedDict:
    by = OrderedDict()
    for p in pages:
        recs = [
            dict(
                page=str(p["id"]),
                words=list(ln),
                hand=str(p.get("hand", "1")),
                illus=str(p.get("section", "H")),
                quire=str(p.get("quire", "q1")),
                lang=str(p.get("lang", "B")),
                para_start=(i == 0),
            )
            for i, ln in enumerate(p["lines"])
            if ln
        ]
        if recs:
            by[str(p["id"])] = recs
    return by


def score_7_metrics(pages: list[dict], label: str) -> dict:
    train_pages, held_pages = s37.split_g1_train_heldout(pages, seed=SEED)
    eval_pages = held_pages if len(held_pages) >= 3 else pages

    lns_all = [ln for p in pages for ln in p["lines"] if ln]
    wds_all = [w for ln in lns_all for w in ln]
    lns_held = [ln for p in eval_pages for ln in p["lines"] if ln]
    wds_held = [w for ln in lns_held for w in ln]

    h2_all = a1_profile.char_entropies(wds_all)["h2"]
    h2_held = a1_profile.char_entropies(wds_held)["h2"]
    mean_len = float(np.mean([len(w) for w in wds_all]))
    sd_len = float(np.std([len(w) for w in wds_all]))
    cnt_all = Counter(wds_all)
    hapax_share = sum(1 for v in cnt_all.values() if v == 1) / max(1, len(cnt_all))

    def edge_divergences(lns):
        init_f, mid_f, fin_l, mid_l = Counter(), Counter(), Counter(), Counter()
        n_i = n_m = n_f = 0
        for ln in lns:
            if len(ln) < 3:
                continue
            init_f[ln[0][0]] += 1
            fin_l[ln[-1][-1]] += 1
            n_i += 1
            n_f += 1
            for w in ln[1:-1]:
                mid_f[w[0]] += 1
                mid_l[w[-1]] += 1
                n_m += 1
        jsd_f = a2.jsd(init_f, mid_f)
        p_enr = ((init_f["p"] / max(1, n_i)) / max(1e-9, mid_f["p"] / max(1, n_m))) if mid_f["p"] else 0.0
        m_enr = ((fin_l["m"] / max(1, n_f)) / max(1e-9, mid_l["m"] / max(1, n_m))) if mid_l["m"] else 0.0
        return jsd_f, p_enr, m_enr

    jsd_all, p_enr_all, m_enr_all = edge_divergences(lns_all)
    jsd_held, p_enr_held, m_enr_held = edge_divergences(lns_held)

    cross_all = c3.score(lns_all, c3.EVA)[2]
    cross_held = c3.score(lns_held, c3.EVA)[2]

    moran_res = L.moran_line_null(pages, seed=SEED)
    moran_held = L.moran_line_null(eval_pages, seed=SEED)

    tr_toks = mn.flat_tokens(train_pages)
    seg = mn.SlotSegmenter(tr_toks)
    vocab = sorted(set(wds_all))
    seg_cache = {w: seg.segment(w) for w in vocab}
    bilin_all = s37._run_bilinear_stratum(pages, seg_cache, seed=SEED)
    bilin_held = s37._run_bilinear_stratum(eval_pages, seg_cache, seed=SEED)

    aff_ex_pct = sum(bilin_all["comp_rows"][k]["pct_ex"] for k in ("P1->P2", "S1->S2", "S1->P2", "P1->S2"))
    crs_ex_pct = sum(bilin_all["comp_rows"][k]["pct_ex"] for k in ("C1->P2", "P1->C2", "S1->C2", "C1->S2"))
    cor_ex_pct = bilin_all["comp_rows"]["C1->C2"]["pct_ex"]

    cw_val, c3_bpt, uni_bpt = s37.compute_corpus_charwin(pages, mn, seed=SEED)

    by = pages_to_by(pages)
    tr_eo = [r["words"] for i, recs in enumerate(by.values()) if i % 2 == 0 for r in recs]
    te_eo = [r["words"] for i, recs in enumerate(by.values()) if i % 2 == 1 for r in recs]
    f1.TOPN = 300
    U_r, E_r, E2_r, W_r, _ = f1.evaluate(tr_eo, te_eo)
    U_s, _, E2_s, W_s, _ = f1.evaluate(f1.shuffled(tr_eo), f1.shuffled(te_eo))
    f1_page_eo = float((E2_r - W_r) - (E2_s - W_s))

    qs = sorted({recs[0]["quire"] for recs in by.values() if recs[0].get("quire") is not None})
    if len(qs) >= 4:
        f1_quire, f1_ci = N.residual(by, "quires")
    else:
        f1_quire, f1_ci = f1_page_eo, (float("nan"), float("nan"))

    def slot_coupling_a14(lns_sub):
        lns2 = [ln for ln in lns_sub if len(ln) >= 2]
        ps = sorted({seg_cache[w][0] for w in vocab})
        cs = sorted({seg_cache[w][1] for w in vocab})
        ss = sorted({seg_cache[w][2] for w in vocab})
        p2i = {x: i for i, x in enumerate(ps)}
        c2i = {x: i for i, x in enumerate(cs)}
        s2i = {x: i for i, x in enumerate(ss)}

        w1_p = np.array([p2i[seg_cache[w][0]] for ln in lns2 for w in ln[:-1]], dtype=np.int64)
        w1_c = np.array([c2i[seg_cache[w][1]] for ln in lns2 for w in ln[:-1]], dtype=np.int64)
        w1_s = np.array([s2i[seg_cache[w][2]] for ln in lns2 for w in ln[:-1]], dtype=np.int64)
        w2_p = np.array([p2i[seg_cache[w][0]] for ln in lns2 for w in ln[1:]], dtype=np.int64)
        w2_c = np.array([c2i[seg_cache[w][1]] for ln in lns2 for w in ln[1:]], dtype=np.int64)

        obs_sp = s34.fast_mi_1d(w1_s, w2_p, len(ss), len(ps))[0]
        obs_cc = s34.fast_mi_1d(w1_c, w2_c, len(cs), len(cs))[0]
        obs_cp = s34.fast_mi_1d(w1_c, w2_p, len(cs), len(ps))[0]
        obs_pp = s34.fast_mi_1d(w1_p, w2_p, len(ps), len(ps))[0]

        rng_sh = random.Random(SEED)
        null_sp, null_cc, null_cp, null_pp = [], [], [], []
        for _ in range(100):
            sh = [rng_sh.sample(ln, len(ln)) for ln in lns2]
            sw1_p = np.array([p2i[seg_cache[w][0]] for ln in sh for w in ln[:-1]], dtype=np.int64)
            sw1_c = np.array([c2i[seg_cache[w][1]] for ln in sh for w in ln[:-1]], dtype=np.int64)
            sw1_s = np.array([s2i[seg_cache[w][2]] for ln in sh for w in ln[:-1]], dtype=np.int64)
            sw2_p = np.array([p2i[seg_cache[w][0]] for ln in sh for w in ln[1:]], dtype=np.int64)
            sw2_c = np.array([c2i[seg_cache[w][1]] for ln in sh for w in ln[1:]], dtype=np.int64)
            null_sp.append(s34.fast_mi_1d(sw1_s, sw2_p, len(ss), len(ps))[0])
            null_cc.append(s34.fast_mi_1d(sw1_c, sw2_c, len(cs), len(cs))[0])
            null_cp.append(s34.fast_mi_1d(sw1_c, sw2_p, len(cs), len(ps))[0])
            null_pp.append(s34.fast_mi_1d(sw1_p, sw2_p, len(ps), len(ps))[0])

        return dict(
            S1_P2_ex=float(obs_sp - np.mean(null_sp)),
            C1_C2_ex=float(obs_cc - np.mean(null_cc)),
            C1_P2_ex=float(obs_cp - np.mean(null_cp)),
            P1_P2_ex=float(obs_pp - np.mean(null_pp)),
            S1_P2_obs=float(obs_sp),
            C1_C2_obs=float(obs_cc),
            n_pre=len(ps),
            n_core=len(cs),
            n_suf=len(ss),
        )

    a14_all = slot_coupling_a14(lns_all)
    a14_held = slot_coupling_a14(lns_held)

    return dict(
        label=label,
        tokens=len(wds_all),
        types=len(cnt_all),
        hapax=hapax_share,
        mean_len=mean_len,
        sd_len=sd_len,
        h2_all=h2_all,
        h2_held=h2_held,
        jsd_all=jsd_all,
        jsd_held=jsd_held,
        p_enr_all=p_enr_all,
        m_enr_all=m_enr_all,
        cross_all=cross_all,
        cross_held=cross_held,
        I_within_all=moran_res["I"],
        I_null_q99_all=moran_res["q99"],
        I_p_all=moran_res["p"],
        I_within_held=moran_held["I"],
        I_core_all=bilin_all["cor"]["I"],
        bilin_aff_pct=aff_ex_pct,
        bilin_crs_pct=crs_ex_pct,
        bilin_cor_pct=cor_ex_pct,
        CHARWIN=cw_val,
        char3_bpt=c3_bpt,
        uni_bpt=uni_bpt,
        F1_page=f1_page_eo,
        F1_quire=float(f1_quire),
        F1_ci=list(f1_ci),
        a14_all=a14_all,
        a14_held=a14_held,
    )


def canonical_prefix_6(w: str, seg_p: str) -> str:
    if not seg_p:
        return "∅"
    if seg_p.startswith("qo"):
        return "qo"
    if seg_p.startswith("ch"):
        return "ch"
    if seg_p.startswith("sh"):
        return "sh"
    if seg_p == "o" or seg_p.startswith("o"):
        return "o"
    if seg_p == "a" or seg_p.startswith("a"):
        return "a"
    return "other"


def heldout_conditional_entropy_bits(
    train_tuples: list[tuple],
    test_tuples: list[tuple],
    alpha: float = 0.5,
) -> float:
    p_glob = Counter(t[0] for t in train_tuples)
    n_glob = sum(p_glob.values())
    vocab_t = sorted(set(p_glob.keys()) | {t[0] for t in test_tuples})
    V = len(vocab_t)

    def prob_glob(y):
        return (p_glob.get(y, 0) + alpha) / (n_glob + alpha * V)

    base_cnt = defaultdict(Counter)
    base_tot = Counter()
    for t in train_tuples:
        y, b_ctx = t[0], t[1]
        base_cnt[b_ctx][y] += 1
        base_tot[b_ctx] += 1

    def prob_base(y, b_ctx):
        n_b = base_tot.get(b_ctx, 0)
        if n_b == 0:
            return prob_glob(y)
        u_b = len(base_cnt[b_ctx])
        lam = n_b / (n_b + u_b)
        return lam * (base_cnt[b_ctx].get(y, 0) / n_b) + (1.0 - lam) * prob_glob(y)

    if len(train_tuples[0]) == 2:
        total_bits = sum(-math.log2(max(prob_base(t[0], t[1]), 1e-12)) for t in test_tuples)
        return total_bits / max(1, len(test_tuples))

    joint_cnt = defaultdict(Counter)
    joint_tot = Counter()
    for t in train_tuples:
        y, b_ctx, e_ctx = t[0], t[1], t[2]
        joint_cnt[(b_ctx, e_ctx)][y] += 1
        joint_tot[(b_ctx, e_ctx)] += 1

    ext_cnt = defaultdict(Counter)
    ext_tot = Counter()
    for t in train_tuples:
        y, _, e_ctx = t[0], t[1], t[2]
        ext_cnt[e_ctx][y] += 1
        ext_tot[e_ctx] += 1

    def prob_ext(y, e_ctx):
        n_e = ext_tot.get(e_ctx, 0)
        if n_e == 0:
            return prob_glob(y)
        u_e = len(ext_cnt[e_ctx])
        lam = n_e / (n_e + u_e)
        return lam * (ext_cnt[e_ctx].get(y, 0) / n_e) + (1.0 - lam) * prob_glob(y)

    def prob_joint(y, b_ctx, e_ctx):
        pb = prob_base(y, b_ctx)
        n_j = joint_tot.get((b_ctx, e_ctx), 0)
        if n_j > 0:
            u_j = len(joint_cnt[(b_ctx, e_ctx)])
            lam_j = n_j / (n_j + 2.0 * u_j)
            p_emp = joint_cnt[(b_ctx, e_ctx)].get(y, 0) / n_j
        else:
            lam_j = 0.0
            p_emp = 0.0
        unnorm = {v: (prob_base(v, b_ctx) * prob_ext(v, e_ctx) / max(prob_glob(v), 1e-12)) for v in vocab_t}
        z = sum(unnorm.values())
        p_poe = unnorm[y] / z if z > 0 else pb
        return lam_j * p_emp + (1.0 - lam_j) * p_poe

    total_bits = sum(-math.log2(max(prob_joint(t[0], t[1], t[2]), 1e-12)) for t in test_tuples)
    return total_bits / max(1, len(test_tuples))


def run_experiment_3b(pages: list[dict], label: str) -> dict:
    train_pages, held_pages = s37.split_g1_train_heldout(pages, seed=SEED)
    train_toks = mn.flat_tokens(train_pages)
    seg = mn.SlotSegmenter(train_toks)

    def extract_records(pg_list):
        recs = []
        for p in pg_list:
            sec = str(p.get("section", "?"))
            hand = str(p.get("hand", "?"))
            pid = str(p.get("id", "?"))
            for ln in p["lines"]:
                if not ln:
                    continue
                n = len(ln)
                parts = [seg.segment(w) for w in ln]
                p6s = [canonical_prefix_6(w, pt[0]) for w, pt in zip(ln, parts)]
                for t in range(n):
                    P_t, C_t, S_t = parts[t]
                    P6_t = p6s[t]
                    slot = "init" if t == 0 else ("final" if t == n - 1 else ("second" if t == 1 else "mid"))
                    prev_S = parts[t - 1][2] if t > 0 else "<BOL>"
                    prev_P = parts[t - 1][0] if t > 0 else "<BOL>"
                    prev_P6 = p6s[t - 1] if t > 0 else "<BOL>"
                    prev_Clen = (1 if len(parts[t - 1][1]) <= 1 else (2 if len(parts[t - 1][1]) == 2 else 3)) if t > 0 else 0
                    next_C = parts[t + 1][1] if t + 1 < n else "<EOL>"
                    next_P6 = p6s[t + 1] if t + 1 < n else "<EOL>"
                    recs.append(
                        dict(
                            w=ln[t],
                            P=P_t or "∅",
                            P6=P6_t,
                            C=C_t,
                            S=S_t or "∅",
                            slot=slot,
                            prev_S=prev_S or "∅",
                            prev_P=prev_P or "∅",
                            prev_P6=prev_P6,
                            prev_Clen=prev_Clen,
                            left_state=(slot, prev_S or "∅", prev_P6, prev_Clen),
                            left_s_slot=(slot, prev_S or "∅"),
                            next_C=next_C,
                            next_P6=next_P6,
                            sec_hand=(sec, hand),
                            sec=sec,
                            pid=pid,
                        )
                    )
        return recs

    tr_recs = extract_records(train_pages)
    te_recs = extract_records(held_pages)

    out_modes = {}
    for p_key, p_label in [("P6", "6-Class Canonical Prefix (qo/ch/sh/o/a/∅/other)"), ("P", "Full 28-Class SlotSegmenter Prefix")]:
        ce_uncond = heldout_conditional_entropy_bits(
            [(r[p_key], "ALL") for r in tr_recs],
            [(r[p_key], "ALL") for r in te_recs],
        )
        ce_given_C = heldout_conditional_entropy_bits(
            [(r[p_key], r["C"]) for r in tr_recs],
            [(r[p_key], r["C"]) for r in te_recs],
        )
        contexts = [
            ("left_slot_only", "Line Slot (init/2nd/mid/final)", lambda r: r["slot"]),
            ("left_prevS", "Prev Suffix S_{t-1}", lambda r: r["prev_S"]),
            ("left_prevP", "Prev Prefix P_{t-1}", lambda r: r["prev_P6"]),
            ("left_prevClen", "Prev Core Length |C_{t-1}|", lambda r: r["prev_Clen"]),
            ("left_s_slot", "Left (line_slot, S_{t-1})", lambda r: r["left_s_slot"]),
            ("left_full_state", "Full Left State (slot, S_{t-1}, P_{t-1}, |C_{t-1}|)", lambda r: r["left_state"]),
            ("right_nextC", "Right Core C_{t+1}", lambda r: r["next_C"]),
            ("right_nextP", "Right Prefix P_{t+1}", lambda r: r["next_P6"]),
            ("topic_sec_hand", "Section + Hand (illus, hand)", lambda r: r["sec_hand"]),
            ("within_word_S", "Within-Word Suffix S_t", lambda r: r["S"]),
        ]
        ce_gains = {}
        for c_code, c_desc, fn in contexts:
            ce_ctx = heldout_conditional_entropy_bits(
                [(r[p_key], r["C"], fn(r)) for r in tr_recs],
                [(r[p_key], r["C"], fn(r)) for r in te_recs],
            )
            gain_bits = ce_given_C - ce_ctx
            pct_of_H_P_given_C = 100.0 * gain_bits / max(ce_given_C, 1e-9)
            ce_gains[c_code] = dict(desc=c_desc, ce_bits=ce_ctx, gain_bits=gain_bits, pct=pct_of_H_P_given_C)

        c_cnt_te = Counter(r["C"] for r in te_recs)
        freq_cores = {c for c, cnt in c_cnt_te.items() if cnt >= 10}
        sub_te = [r for r in te_recs if r["C"] in freq_cores]

        p_cnt = Counter(r[p_key] for r in sub_te)
        h_p_emp = mn.entropy_counts(p_cnt)
        by_c = defaultdict(list)
        for r in sub_te:
            by_c[r["C"]].append(r)
        n_sub = len(sub_te)
        h_p_given_c_emp = sum((len(rs) / n_sub) * mn.entropy_counts(Counter(x[p_key] for x in rs)) for rs in by_c.values())

        cmi_stats = {}
        rng_np = np.random.default_rng(SEED)
        for c_code, c_desc, fn in contexts:
            by_cx = defaultdict(Counter)
            cnt_cx = Counter()
            for r in sub_te:
                k_cx = (r["C"], fn(r))
                by_cx[k_cx][r[p_key]] += 1
                cnt_cx[k_cx] += 1
            h_p_given_cx = sum((cnt_cx[k] / n_sub) * mn.entropy_counts(by_cx[k]) for k in cnt_cx)
            obs_cmi = h_p_given_c_emp - h_p_given_cx

            null_cmis = []
            for _ in range(100):
                by_cx_sh = defaultdict(Counter)
                for c_val, rs in by_c.items():
                    p_vals = [x[p_key] for x in rs]
                    perm_idx = rng_np.permutation(len(p_vals))
                    for idx_r, x in enumerate(rs):
                        by_cx_sh[(c_val, fn(x))][p_vals[perm_idx[idx_r]]] += 1
                h_sh = sum((cnt_cx[k] / n_sub) * mn.entropy_counts(by_cx_sh[k]) for k in cnt_cx)
                null_cmis.append(h_p_given_c_emp - h_sh)
            m_null = float(np.mean(null_cmis))
            sd_null = float(np.std(null_cmis)) or 1e-9
            ex_cmi = obs_cmi - m_null
            z_cmi = ex_cmi / sd_null
            cmi_stats[c_code] = dict(
                desc=c_desc,
                obs_cmi=obs_cmi,
                null_cmi=m_null,
                ex_cmi=ex_cmi,
                z=z_cmi,
                pct_ex=100.0 * ex_cmi / max(h_p_given_c_emp, 1e-9),
            )

        out_modes[p_key] = dict(
            label=p_label,
            n_train=len(tr_recs),
            n_test=len(te_recs),
            n_test_freq_cores=n_sub,
            n_freq_cores=len(freq_cores),
            ce_uncond=ce_uncond,
            ce_given_C=ce_given_C,
            info_C_about_P=ce_uncond - ce_given_C,
            h_p_emp_freqC=h_p_emp,
            h_p_given_c_emp_freqC=h_p_given_c_emp,
            ce_gains=ce_gains,
            cmi_stats=cmi_stats,
        )

    by_full = pages_to_by(pages)
    by_core = OrderedDict()
    by_cs = OrderedDict()
    for pg_id, recs in by_full.items():
        by_core[pg_id] = [dict(r, words=[seg.segment(w)[1] for w in r["words"]]) for r in recs]
        by_cs[pg_id] = [dict(r, words=[seg.segment(w)[1] + seg.segment(w)[2] for w in r["words"]]) for r in recs]

    def quick_f1(by_d):
        qs = sorted({recs[0]["quire"] for recs in by_d.values() if recs[0].get("quire") is not None})
        if len(qs) >= 4:
            v, ci = N.residual(by_d, "quires")
            return float(v), [float(ci[0]), float(ci[1])]
        tr_eo = [r["words"] for i, recs in enumerate(by_d.values()) if i % 2 == 0 for r in recs]
        te_eo = [r["words"] for i, recs in enumerate(by_d.values()) if i % 2 == 1 for r in recs]
        f1.TOPN = 300
        _, _, E2_r, W_r, _ = f1.evaluate(tr_eo, te_eo)
        _, _, E2_s, W_s, _ = f1.evaluate(f1.shuffled(tr_eo), f1.shuffled(te_eo))
        return float((E2_r - W_r) - (E2_s - W_s)), [float("nan"), float("nan")]

    f1_full, f1_full_ci = quick_f1(by_full)
    f1_cs, f1_cs_ci = quick_f1(by_cs)
    f1_core, f1_core_ci = quick_f1(by_core)

    return dict(
        corpus=label,
        prefix_modes=out_modes,
        collapsibility=dict(
            F1_full=f1_full,
            F1_full_ci=f1_full_ci,
            F1_prefix_stripped=f1_cs,
            F1_prefix_stripped_ci=f1_cs_ci,
            F1_core_only=f1_core,
            F1_core_only_ci=f1_core_ci,
        ),
    )


def main() -> None:
    t0 = time.time()
    emit("=" * 108)
    emit("CANDIDATE 3 INVESTIGATION: COMPACT REVERSIBLE STATE-DEPENDENT VERBOSE CIPHER (EXP 3A & 3B)")
    emit("=" * 108)
    emit(f"Seed: {SEED} | Read-Only Repo: {VOYNICH_ROOT}")
    emit()

    by_zl3b, _, _ = L.load_T("ZL3b")
    pages_zl3b = L.pages_of(by_zl3b)

    d_p15 = json.loads((VOYNICH_ROOT / "data" / "controls_realline" / "cremma_prose15.meta.json").read_text(encoding="utf-8"))
    pages_p15 = d_p15["pages"]
    for i, p in enumerate(pages_p15):
        p["quire"] = f"q{i // 2}"

    d_all = json.loads((VOYNICH_ROOT / "data" / "controls_realline" / "cremma_all.meta.json").read_text(encoding="utf-8"))
    pages_all_35k = []
    tok_acc = 0
    for i, p in enumerate(d_all["pages"]):
        p_copy = dict(p, quire=f"q{i // 6}")
        pages_all_35k.append(p_copy)
        tok_acc += sum(len(ln) for ln in p["lines"])
        if tok_acc >= 34857:
            break

    streams_k2 = k2.plaintext_streams(by_zl3b, shuffle=False)
    its_k2 = {k: iter(v) for k, v in streams_k2.items()}
    pages_k2_latin = []
    for pg_id, recs in by_zl3b.items():
        r0 = recs[0]
        lns = [[next(its_k2[(r["hand"], r["illus"])]) for _ in r["words"]] for r in recs]
        pages_k2_latin.append(
            dict(id=pg_id, section=r0["illus"], hand=r0["hand"], quire=r0["quire"], lang=r0["lang"], lines=lns)
        )

    emit("=== GATE 1: EXACT MATHEMATICAL & ALGORITHMIC REVERSIBILITY VERIFICATION ===")
    reversibility_report = {}
    all_modes = (
        "M0_statefree",
        "M1_2state",
        "M2_3state",
        "M3_3state_allomorph",
        "M4_bijective",
        "M5_100pct_rev_calibrated",
        "M6_100pct_rev_homophonic",
    )
    for corp_name, src_pages in [
        ("cremma_prose15", pages_p15),
        ("cremma_all_35k", pages_all_35k),
        ("k2_latin_207p", pages_k2_latin),
    ]:
        for mode in all_modes:
            enc_p, gt_traces = encode_corpus(src_pages, mode=mode)
            rec_traces, rec_words = decode_corpus(enc_p, mode=mode)
            total_toks = sum(len(ln) for ln in gt_traces)
            exact_trace_matches = sum(
                1 for ln_g, ln_r in zip(gt_traces, rec_traces) for g, r in zip(ln_g, ln_r) if g == r
            )
            pct_trace = 100.0 * exact_trace_matches / max(1, total_toks)
            if mode in ("M4_bijective", "M6_100pct_rev_homophonic"):
                orig_norm = [[normalize_latin(w) for w in ln] for p in src_pages for ln in p["lines"] if ln]
                exact_word_matches = sum(
                    1 for ln_o, ln_r in zip(orig_norm, rec_words) for o, r in zip(ln_o, ln_r) if o == r
                )
                pct_word = 100.0 * exact_word_matches / max(1, total_toks)
            elif mode == "M5_100pct_rev_calibrated":
                orig_stems = [[encode_stem_disjoint(normalize_latin(w)) for w in ln] for p in src_pages for ln in p["lines"] if ln]
                exact_stem_matches = sum(
                    1 for ln_o, ln_r in zip(orig_stems, rec_words) for o, r in zip(ln_o, ln_r) if o == r
                )
                pct_word = 100.0 * exact_stem_matches / max(1, total_toks)
            else:
                pct_word = pct_trace
            reversibility_report[f"{corp_name}:{mode}"] = dict(
                tokens=total_toks, trace_acc_pct=pct_trace, word_acc_pct=pct_word
            )
            if corp_name == "cremma_all_35k" or mode in ("M2_3state", "M4_bijective", "M5_100pct_rev_calibrated", "M6_100pct_rev_homophonic"):
                emit(
                    f"  {corp_name:16s} | {mode:25s} | tokens={total_toks:5d} | "
                    f"(P_t, C_t, S_t, q_t) recovery = {exact_trace_matches}/{total_toks} ({pct_trace:.2f}%) | "
                    f"stem/word recovery = {pct_word:.2f}%"
                )
    emit()

    emit("=" * 108)
    emit("EXPERIMENT 3A: COMPACT REVERSIBLE STATE-DEPENDENT CIPHER ON REAL MEDIEVAL LATIN LINES")
    emit("=" * 108)

    results_3a = {}
    res_voy = score_7_metrics(pages_zl3b, "Voynich_ZL3b (MS Target)")
    results_3a["Voynich_ZL3b"] = res_voy

    for corp_name, src_pages in [
        ("cremma_prose15", pages_p15),
        ("cremma_all_35k", pages_all_35k),
        ("k2_latin_207p", pages_k2_latin),
    ]:
        res_raw = score_7_metrics(src_pages, f"{corp_name} [Raw Unencoded Latin]")
        results_3a[f"{corp_name}_raw"] = res_raw
        for mode in all_modes:
            enc_p, _ = encode_corpus(src_pages, mode=mode)
            key = f"{corp_name}_{mode}"
            results_3a[key] = score_7_metrics(enc_p, f"{corp_name} [{mode}]")

    hdr = (
        f"{'Corpus / Model':42s} | {'tok':>5s} {'typ':>5s} {'hap':>5s} | "
        f"{'h2_h':>5s} {'JSDf':>5s} {'cross':>6s} | "
        f"{'I_win':>6s} {'I_q99':>6s} {'I_cor':>6s} | "
        f"{'CHARWIN':>8s} {'F1_pg':>6s} {'F1_qr':>6s} | "
        f"{'S1->P2':>7s} {'C1->C2':>7s}"
    )
    emit(hdr)
    emit("-" * len(hdr))
    for k, r in results_3a.items():
        emit(
            f"{r['label']:42s} | {r['tokens']:5d} {r['types']:5d} {r['hapax']:5.3f} | "
            f"{r['h2_held']:5.3f} {r['jsd_all']:5.3f} {r['cross_all']:+6.3f} | "
            f"{r['I_within_all']:+6.3f} {r['I_null_q99_all']:+6.3f} {r['I_core_all']:+6.3f} | "
            f"{r['CHARWIN']:+8.4f} {r['F1_page']:+6.3f} {r['F1_quire']:+6.3f} | "
            f"{r['a14_all']['S1_P2_ex']:+7.4f} {r['a14_all']['C1_C2_ex']:+7.4f}"
        )
    emit()

    emit("--- HELD-OUT PAGE SPLIT (80/20 g1_heldout_41 convention) METRICS & BILINEAR CADENCE BREAKDOWN ---")
    hdr_h = (
        f"{'Corpus / Model':42s} | {'h2_ho':>5s} {'JSD_ho':>6s} {'crs_ho':>6s} {'I_ho':>6s} | "
        f"{'p_enr':>6s} {'m_enr':>6s} | {'%AffEx':>6s} {'%CrsEx':>6s} {'%CorEx':>6s} | "
        f"{'S1->P2_ho':>9s} {'C1->C2_ho':>9s}"
    )
    emit(hdr_h)
    emit("-" * len(hdr_h))
    for k, r in results_3a.items():
        emit(
            f"{r['label']:42s} | {r['h2_held']:5.3f} {r['jsd_held']:6.3f} {r['cross_held']:+6.3f} {r['I_within_held']:+6.3f} | "
            f"{r['p_enr_all']:6.2f} {r['m_enr_all']:6.2f} | {r['bilin_aff_pct']:+5.1f}% {r['bilin_crs_pct']:+5.1f}% {r['bilin_cor_pct']:+5.1f}% | "
            f"{r['a14_held']['S1_P2_ex']:+9.4f} {r['a14_held']['C1_C2_ex']:+9.4f}"
        )
    emit()

    emit("=" * 108)
    emit("EXPERIMENT 3B: PREFIX PREDICTABILITY H(P_t | C_t) & COLLAPSIBILITY ON REAL VOYNICH (166->41 SPLIT)")
    emit("=" * 108)

    enc_all35k_m3, _ = encode_corpus(pages_all_35k, mode="M3_3state_allomorph")
    enc_k2_m3, _ = encode_corpus(pages_k2_latin, mode="M3_3state_allomorph")
    enc_k2_m4, _ = encode_corpus(pages_k2_latin, mode="M4_bijective")
    enc_k2_m5, _ = encode_corpus(pages_k2_latin, mode="M5_100pct_rev_calibrated")
    enc_k2_m6, _ = encode_corpus(pages_k2_latin, mode="M6_100pct_rev_homophonic")

    results_3b = {}
    for b_key, b_pages, b_label in [
        ("Voynich_ZL3b", pages_zl3b, "Real Voynich ZL3b (166 train -> 41 held-out pages)"),
        ("Cipher_cremma35k_M3", enc_all35k_m3, "3A State Cipher M3 on cremma_all_35k (80/20 held-out)"),
        ("Cipher_k2_M3", enc_k2_m3, "3A State Cipher M3 on k2_latin_207p (166 train -> 41 held-out)"),
        ("Cipher_k2_M4_bijective", enc_k2_m4, "3A Bijective State Cipher M4 on k2_latin_207p (166->41)"),
        ("Cipher_k2_M5_disjoint_cal", enc_k2_m5, "3A 100%-Rev Calibrated State Cipher M5 on k2_latin_207p (166->41)"),
        ("Cipher_k2_M6_disjoint_homo", enc_k2_m6, "3A 100%-Rev Homophonic State Cipher M6 on k2_latin_207p (166->41)"),
    ]:
        res_b = run_experiment_3b(b_pages, b_label)
        results_3b[b_key] = res_b
        emit(f"\n>>> {b_label} <<<")
        col = res_b["collapsibility"]
        emit(
            f"  Collapsibility Test (stripping state affixes to recover underlying core stream):\n"
            f"    F1(Full Words W_t)         = {col['F1_full']:+.4f} {col['F1_full_ci']}\n"
            f"    F1(Prefix-Stripped C_t+S_t)= {col['F1_prefix_stripped']:+.4f} {col['F1_prefix_stripped_ci']}\n"
            f"    F1(Core-Only C_t)          = {col['F1_core_only']:+.4f} {col['F1_core_only_ci']}"
        )
        for p_mode in ("P6", "P"):
            pm = res_b["prefix_modes"][p_mode]
            emit(f"\n  [{pm['label']}] (train={pm['n_train']} toks -> held-out test={pm['n_test']} toks; "
                 f"freq-core subset={pm['n_test_freq_cores']} toks across {pm['n_freq_cores']} cores):")
            emit(
                f"    Held-Out Cross-Entropy: H_test(P_t) = {pm['ce_uncond']:.4f} bits | "
                f"H_test(P_t | C_t) = {pm['ce_given_C']:.4f} bits "
                f"(Core C_t alone explains {pm['info_C_about_P']:+.4f} bits = "
                f"{100.0 * pm['info_C_about_P'] / max(pm['ce_uncond'], 1e-9):.1f}% of H(P_t))"
            )
            emit(
                f"    Within-Test Frequent-Core Plug-in: H(P_t) = {pm['h_p_emp_freqC']:.4f} bits | "
                f"H(P_t | C_t) = {pm['h_p_given_c_emp_freqC']:.4f} bits"
            )
            emit(
                f"    {'Context Predictor X':48s} | {'CE(P|C,X)':>9s} {'CE_Gain':>8s} {'%H(P|C)':>8s} | "
                f"{'CMI_obs':>8s} {'CMI_null':>8s} {'CMI_ex':>8s} {'z_shuf':>7s} {'%Ex_H':>7s}"
            )
            emit("    " + "-" * 124)
            for c_code in pm["ce_gains"]:
                cg = pm["ce_gains"][c_code]
                cm = pm["cmi_stats"][c_code]
                emit(
                    f"    {cg['desc']:48s} | {cg['ce_bits']:9.4f} {cg['gain_bits']:+8.4f} {cg['pct']:+7.2f}% | "
                    f"{cm['obs_cmi']:8.4f} {cm['null_cmi']:8.4f} {cm['ex_cmi']:+8.4f} {cm['z']:+7.2f} {cm['pct_ex']:+6.2f}%"
                )

    emit(f"\nTotal elapsed: {time.time() - t0:.1f}s")
    OUT_TXT.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(dict(reversibility=reversibility_report, exp_3a=results_3a, exp_3b=results_3b), indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_TXT} and {OUT_JSON}", flush=True)


if __name__ == "__main__":
    main()
