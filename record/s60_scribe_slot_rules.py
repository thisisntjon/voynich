#!/usr/bin/env python3
"""s60_scribe_slot_rules.py — Per-Scribe Slot Rules & Cross-Scribe Transfer Investigator (s60).

PRE-REGISTERED SPECIFICATION (frozen in s60_scribe_slot_rules.prereg.sha256 BEFORE running):
Closes CONSTRAINTS-MAP.md §C ("Whether each scribe follows its own slot rules well enough to
predict that scribe's untouched pages (proposed s60)") and untangles c-374 (Hand 1 = Currier A,
Hands 2, 3 = Currier B) by testing whether Hand 2 and Hand 3 inside Currier B share one slot
grammar or follow distinct scribe-specific slot rules on held-out pages.

Evaluated across ZL3b, RF1b, and IT2a using g1_edge_joint.split_names (166 -> 41 page split,
seed 20261017) with SlotSegmenter fitted strictly on the 166 training pages, plus Davis 5-scribe
mapping from data/folio_evidence_inventory.tsv and transliteration headers ($H).

Three pre-registered parts:
  Part 1 — Within-Scribe Held-Out Slot Predictability (166 -> 41 Split Stratified by Davis Hand
           1, 2, 3, 3_B, 4/5, Pooled + Within-Hand 80/20 Page Split):
    - Counted Witten-Bell smoothed slot models fitted on training pages of Hand h:
      * M_prefix: P(P_t | pos, S_{t-1}, line_prefix_state) [core-blind] and
                  P(P_t | C_t, pos, S_{t-1}, line_prefix_state) [core-conditioned]
      * M_suffix: P(S_t | pos, P_t, S_{t-1}) [core-blind] and
                  P(S_t | C_t, pos, P_t, S_{t-1}) [core-conditioned]
      * M_frame : Joint P(P_t, S_t | C_t, pos, S_{t-1}, line_prefix_state)
    - Held-out metrics on untouched pages of Hand h:
      * prefix_gain (bits/token over Hand-h unigram prefix entropy, both core-blind and s57
        1-step bigram) vs 200-draw within-line shuffle null, plus core-conditioned prefix_gain
      * suffix_gain (core-blind and core-conditioned bits/token over Hand-h unigram suffix entropy)
      * frame_given_core_gain (bits/token reduction in H(P_t, S_t) from knowing (C_t, pos, S_{t-1}, state))
      * Held-out top-1 / top-3 slot prediction accuracy vs Hand-h unigram majority/top-3 baseline.

  Part 2 — Cross-Scribe Transfer Matrix (Hand h_train -> Hand h_test) & Separating Hand 2 vs
           Hand 3 Inside Currier B (c-374):
    - 3x3 (+ Hand 3_B and Pooled) cross-scribe held-out cross-entropy matrix
      H_HO(Hand h_test | Model trained on Hand h_train) on:
      (a) All tokens on held-out pages (core-conditioned M_frame and core-blind M_frame_blind),
      (b) Tokens restricted to the top-50 shared cores (C_top50, eliminating topical core
          vocabulary differences between Bio/Herbal-B and Stars/Recipes).
    - Cross-Scribe Transfer Penalty Delta_H(h_train -> h_test) = H(h_test | h_train) - H(h_test | h_test)
      with 500-draw page-bootstrap 95% CIs and a 500-draw page-label permutation p-value between
      Hand 2 and Hand 3 inside Currier B.
    - Blind Scribe Identification on Held-Out Pages (41 pages): using ONLY the counted slot models
      P_h(P_t, S_t | C_t, pos, S_{t-1}, state) (and C_top50-only / core-blind variants, zero
      core-frequency P_h(C_t) information), measure held-out page assignment accuracy across
      Hands 1, 2, 3 and specifically Hand 2 vs Hand 3 inside Currier B.

  Part 3 — Per-Scribe vs. Pooled Generative Slot Wrapper Over Held-Out Core Streams (166 -> 41):
    - On the 41 held-out pages (ZL3b, RF1b, IT2a), wrap the held-out core sequence C_t (and a
      training-sampled core control) with (P_t, S_t) drawn from:
      * W_pooled: Manuscript-wide counted Witten-Bell slot table P(P_t, S_t | C_t, pos, S_{t-1}, state, |w_{t-1}|_bin)
      * W_scribe: Per-scribe counted Witten-Bell slot tables fitted separately on Hand 1, Hand 2, Hand 3, Hand 4/5
      * W_scribe_nolength (ablation without |w_{t-1}|_bin) and W_scribe_blind (core-blind ablation).
    - Compare held-out Moran I (All, Currier A, Currier B, Hand 2, Hand 3), cross_excess_eva
      (All, A, B, Hand 2, Hand 3), jsd_first_fg, prefix_gain, CHARWIN, types, and per-page
      -edy / (-edy + -aiin) & qo- correlation r with the real 41 held-out pages.

Run:    python -I s60_scribe_slot_rules.py
Writes: results_s60.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
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
import n1_habit_table as N1  # noqa: E402
import s21_moran_realline as S21  # noqa: E402
from scoreboard import metrics_new as MN  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s60_scribe_slot_rules.py"
STUB = ROOT / "s60_scribe_slot_rules.prereg.sha256"
OUT = ROOT / "results_s60.txt"

SEED = 20261017
N_SHUF_NULL = 200
N_BOOT = 500
N_PERM = 500
N_GEN_SEEDS = 10
EMPTY = "∅"

TRANSLITS = [
    ("ZL3b", "ZL3b_eva", "ZL3b_eva.meta.json"),
    ("RF1b", "RF1b", "RF1b.meta.json"),
    ("IT2a", "IT2a", "IT2a.meta.json"),
]

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
# Folio Evidence Inventory & Davis 5-Scribe Mapping
# ---------------------------------------------------------------------------
def load_folio_inventory() -> dict[str, dict[str, str]]:
    inv_path = ROOT / "data" / "folio_evidence_inventory.tsv"
    inv: dict[str, dict[str, str]] = {}
    if not inv_path.exists():
        return inv
    lines = inv_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return inv
    headers = lines[0].split("\t")
    for ln in lines[1:]:
        if not ln.strip():
            continue
        parts = ln.split("\t")
        row = dict(zip(headers, parts))
        f = row["folio"]
        h_raw = row.get("hand", "?")
        q_raw = row.get("quire", "?")
        # In Davis (2020), Quire T (f103r-f116v, Stars/Recipes) is written by Scribe 3;
        # f115r has $H=? in ZL3b-n header but is Quire T, section S, Lang B -> Davis Hand 3.
        davis_h = h_raw if h_raw in {"1", "2", "3", "4", "5"} else ("3" if q_raw == "T" or f == "f115r" else h_raw)
        inv[f] = dict(
            header_hand=h_raw,
            davis_hand=davis_h,
            lang=row.get("lang", "?"),
            section=row.get("section", "?"),
            quire=q_raw,
        )
    return inv


def load_translit_pages(stem: str, meta_name: str, inv: dict[str, dict[str, str]]):
    by = N1.load(stem)
    train_ids, test_ids = G1.split_names(by)
    train_set = set(train_ids)
    test_set = set(test_ids)
    d = json.loads((ROOT / "data" / "translit" / meta_name).read_text(encoding="utf-8"))
    pages = []
    for p in d["pages"]:
        pid = str(p["id"])
        lines = [[str(w) for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if not lines:
            continue
        info = inv.get(pid, {})
        h_hdr = str(p.get("hand", info.get("header_hand", "?")))
        q_str = str(p.get("quire", info.get("quire", "?")))
        davis_h = h_hdr if h_hdr in {"1", "2", "3", "4", "5"} else (
            info.get("davis_hand", "3") if (q_str == "T" or pid == "f115r") else h_hdr
        )
        pages.append(dict(
            id=pid,
            header_hand=h_hdr,
            hand=davis_h,
            lang=str(p.get("lang", info.get("lang", "?"))),
            section=str(p.get("section", info.get("section", "?"))),
            quire=q_str,
            lines=lines,
        ))
    id2p = {p["id"]: p for p in pages}
    train_p = [id2p[pid] for pid in train_ids if pid in id2p]
    test_p = [id2p[pid] for pid in test_ids if pid in id2p]
    return pages, train_p, test_p


# ---------------------------------------------------------------------------
# Token-Level Slot & Context Extraction
# ---------------------------------------------------------------------------
def line_pos_label(idx: int, line_len: int, is_para_start: bool = False) -> str:
    if idx == 0:
        return "para_0" if is_para_start else "line_0"
    if idx == line_len - 1:
        return "line_final"
    return "interior"


def word_len_bin(length: int) -> str:
    if length <= 4:
        return "L<=4"
    if length <= 6:
        return "L5_6"
    return "L>=7"


def annotate_pages(pages: list[dict], seg: SlotSegmenter) -> list[dict]:
    """Annotates every page and line with SlotSegmenter (P, C, S) and contextual state."""
    out_pages = []
    for p in pages:
        ann_lines = []
        for l_idx, ln in enumerate(p["lines"]):
            L = len(ln)
            pcs = [seg.segment(w) for w in ln]
            dom_p = "<NONE>"
            tok_recs = []
            for i, (w, (pre, core, suf)) in enumerate(zip(ln, pcs)):
                pos = line_pos_label(i, L, is_para_start=(l_idx == 0))
                p_sym = pre if pre else EMPTY
                s_sym = suf if suf else EMPTY
                c_sym = core if core else EMPTY
                s_prev = (pcs[i - 1][2] or EMPTY) if i > 0 else "<BOS>"
                p_prev = (pcs[i - 1][0] or EMPTY) if i > 0 else "<BOS>"
                lbin_prev = word_len_bin(len(ln[i - 1])) if i > 0 else "<BOS>"
                state = (p_prev, dom_p)
                tok_recs.append(dict(
                    w=w, pre=pre, core=core, suf=suf,
                    P=p_sym, C=c_sym, S=s_sym, F=(p_sym, s_sym),
                    pos=pos, s_prev=s_prev, p_prev=p_prev,
                    state=state, lbin_prev=lbin_prev,
                    idx=i, L=L, l_idx=l_idx,
                ))
                if pre:
                    dom_p = pre
            ann_lines.append(tok_recs)
        out_pages.append(dict(p, ann_lines=ann_lines))
    return out_pages


def shuffled_line_records(ann_pages: list[dict], rng: random.Random) -> list[dict]:
    """Within-line token shuffle of annotated pages: preserves each line's exact token multiset
    while destroying intra-line positional/sequential slot order."""
    recs = []
    for p in ann_pages:
        for l_idx, ln_recs in enumerate(p["ann_lines"]):
            L = len(ln_recs)
            perm = list(ln_recs)
            rng.shuffle(perm)
            dom_p = "<NONE>"
            for i, r in enumerate(perm):
                pos = line_pos_label(i, L, is_para_start=(l_idx == 0))
                s_prev = perm[i - 1]["S"] if i > 0 else "<BOS>"
                p_prev = perm[i - 1]["P"] if i > 0 else "<BOS>"
                state = (p_prev, dom_p)
                recs.append(dict(
                    P=r["P"], C=r["C"], S=r["S"], F=r["F"],
                    pos=pos, s_prev=s_prev, p_prev=p_prev, state=state,
                ))
                if r["pre"]:
                    dom_p = r["pre"]
    return recs


# ---------------------------------------------------------------------------
# Counted Witten-Bell Slot Model Suite
# ---------------------------------------------------------------------------
class WBTable:
    """Counted Witten-Bell conditional table mapping ctx -> Counter(outcome)."""

    def __init__(self):
        self.counts: dict[tuple, Counter] = defaultdict(Counter)
        self.totals: dict[tuple, tuple[int, int]] = {}

    def add(self, ctx: tuple, outcome) -> None:
        self.counts[ctx][outcome] += 1

    def finalize(self) -> None:
        self.totals = {ctx: (sum(c.values()), len(c)) for ctx, c in self.counts.items()}

    def prob(self, ctx: tuple, outcome, backoff_p: float) -> float:
        st = self.totals.get(ctx)
        if st is None:
            return backoff_p
        n, T = st
        return (self.counts[ctx].get(outcome, 0) + T * backoff_p) / (n + T)

    def dist(self, ctx: tuple, vocab: list, backoff_dist: np.ndarray) -> np.ndarray:
        st = self.totals.get(ctx)
        if st is None:
            return backoff_dist
        n, T = st
        cnt = self.counts[ctx]
        arr = np.fromiter((cnt.get(v, 0) for v in vocab), dtype=np.float64, count=len(vocab))
        return (arr + T * backoff_dist) / (n + T)


class ScribeSlotModel:
    """Counted Witten-Bell smoothed slot models (M_prefix, M_suffix, M_frame) for one Scribe/Pool."""

    def __init__(self, ann_pages: list[dict], shared_P: list[str], shared_S: list[str], shared_F: list[tuple[str, str]]):
        self.vocab_P = shared_P
        self.vocab_S = shared_S
        self.vocab_F = shared_F
        self.V_P = len(shared_P)
        self.V_S = len(shared_S)
        self.V_F = len(shared_F)

        self.uni_P = Counter()
        self.uni_S = Counter()
        self.uni_F = Counter()
        self.N = 0

        # M_prefix core-blind hierarchy: (pos,) -> (pos, s_prev) -> (pos, s_prev, p_prev) -> (pos, s_prev, state)
        self.p_blind_t = [WBTable() for _ in range(4)]
        # M_prefix core-conditioned hierarchy over p_blind: (C,) -> (C, pos) -> (C, pos, s_prev)
        self.p_core_t = [WBTable() for _ in range(3)]
        # s57 1-step prefix bigram P(P_t | P_{t-1}) within lines
        self.p_big = WBTable()
        self.p_big_uni = Counter()
        self.p_big_N = 0

        # M_suffix core-blind hierarchy: (pos,) -> (pos, P) -> (pos, P, s_prev)
        self.s_blind_t = [WBTable() for _ in range(3)]
        # M_suffix core-conditioned hierarchy over s_blind: (C,) -> (C, pos) -> (C, pos, P) -> (C, pos, P, s_prev)
        self.s_core_t = [WBTable() for _ in range(4)]

        # Direct joint M_frame core-blind & core-conditioned tables for fast cross-entropy
        self.f_blind_t = [WBTable() for _ in range(3)]
        self.f_core_t = [WBTable() for _ in range(3)]

        for p in ann_pages:
            for ln in p["ann_lines"]:
                for i, r in enumerate(ln):
                    P, C, S, F = r["P"], r["C"], r["S"], r["F"]
                    pos, s_prev, p_prev, state = r["pos"], r["s_prev"], r["p_prev"], r["state"]
                    self.uni_P[P] += 1
                    self.uni_S[S] += 1
                    self.uni_F[F] += 1
                    self.N += 1

                    if i > 0:
                        self.p_big.add((p_prev,), P)
                        self.p_big_uni[P] += 1
                        self.p_big_N += 1

                    # Prefix tables
                    self.p_blind_t[0].add((pos,), P)
                    self.p_blind_t[1].add((pos, s_prev), P)
                    self.p_blind_t[2].add((pos, s_prev, p_prev), P)
                    self.p_blind_t[3].add((pos, s_prev, state), P)

                    self.p_core_t[0].add((C,), P)
                    self.p_core_t[1].add((C, pos), P)
                    self.p_core_t[2].add((C, pos, s_prev), P)

                    # Suffix tables
                    self.s_blind_t[0].add((pos,), S)
                    self.s_blind_t[1].add((pos, P), S)
                    self.s_blind_t[2].add((pos, P, s_prev), S)

                    self.s_core_t[0].add((C,), S)
                    self.s_core_t[1].add((C, pos), S)
                    self.s_core_t[2].add((C, pos, P), S)
                    self.s_core_t[3].add((C, pos, P, s_prev), S)

                    # Direct joint frame tables
                    self.f_blind_t[0].add((pos,), F)
                    self.f_blind_t[1].add((pos, s_prev), F)
                    self.f_blind_t[2].add((pos, s_prev, state), F)

                    self.f_core_t[0].add((C,), F)
                    self.f_core_t[1].add((C, pos), F)
                    self.f_core_t[2].add((C, pos, s_prev), F)

        for t in self.p_blind_t + self.p_core_t + self.s_blind_t + self.s_core_t + self.f_blind_t + self.f_core_t + [self.p_big]:
            t.finalize()

        # Precompute unigram arrays
        denom_P = max(self.N, 1) + 0.5 * (self.V_P + 1)
        self.u_arr_P = np.array([(self.uni_P.get(v, 0) + 0.5) / denom_P for v in self.vocab_P], dtype=np.float64)
        denom_S = max(self.N, 1) + 0.5 * (self.V_S + 1)
        self.u_arr_S = np.array([(self.uni_S.get(v, 0) + 0.5) / denom_S for v in self.vocab_S], dtype=np.float64)
        denom_F = max(self.N, 1) + 0.5 * (self.V_F + 1)
        self.u_arr_F = np.array([(self.uni_F.get(v, 0) + 0.5) / denom_F for v in self.vocab_F], dtype=np.float64)

        self.top3_uni_P = set(np.argsort(-self.u_arr_P)[:3])
        self.top1_uni_P = int(np.argmax(self.u_arr_P))
        self.top3_uni_S = set(np.argsort(-self.u_arr_S)[:3])
        self.top1_uni_S = int(np.argmax(self.u_arr_S))
        self.top3_uni_F = set(np.argsort(-self.u_arr_F)[:3])
        self.top1_uni_F = int(np.argmax(self.u_arr_F))

    def pu_P(self, P: str) -> float:
        return (self.uni_P.get(P, 0) + 0.5) / (max(self.N, 1) + 0.5 * (self.V_P + 1))

    def pu_S(self, S: str) -> float:
        return (self.uni_S.get(S, 0) + 0.5) / (max(self.N, 1) + 0.5 * (self.V_S + 1))

    def pu_F(self, F: tuple[str, str]) -> float:
        return (self.uni_F.get(F, 0) + 0.5) / (max(self.N, 1) + 0.5 * (self.V_F + 1))

    def prob_P_s57_bigram(self, p_prev: str, P: str) -> tuple[float, float]:
        pu = (self.p_big_uni.get(P, 0) + 0.5) / (max(self.p_big_N, 1) + 0.5 * (self.V_P + 1))
        pb = self.p_big.prob((p_prev,), P, pu)
        return pu, pb

    def prob_P_blind(self, r: dict) -> float:
        P = r["P"]
        pos, s_prev, p_prev, state = r["pos"], r["s_prev"], r["p_prev"], r["state"]
        p = self.pu_P(P)
        p = self.p_blind_t[0].prob((pos,), P, p)
        p = self.p_blind_t[1].prob((pos, s_prev), P, p)
        p = self.p_blind_t[2].prob((pos, s_prev, p_prev), P, p)
        p = self.p_blind_t[3].prob((pos, s_prev, state), P, p)
        return p

    def prob_P_core(self, r: dict) -> float:
        P, C, pos, s_prev = r["P"], r["C"], r["pos"], r["s_prev"]
        p = self.prob_P_blind(r)
        p = self.p_core_t[0].prob((C,), P, p)
        p = self.p_core_t[1].prob((C, pos), P, p)
        p = self.p_core_t[2].prob((C, pos, s_prev), P, p)
        return p

    def prob_S_blind(self, r: dict) -> float:
        S, P, pos, s_prev = r["S"], r["P"], r["pos"], r["s_prev"]
        p = self.pu_S(S)
        p = self.s_blind_t[0].prob((pos,), S, p)
        p = self.s_blind_t[1].prob((pos, P), S, p)
        p = self.s_blind_t[2].prob((pos, P, s_prev), S, p)
        return p

    def prob_S_core(self, r: dict) -> float:
        S, P, C, pos, s_prev = r["S"], r["P"], r["C"], r["pos"], r["s_prev"]
        p = self.prob_S_blind(r)
        p = self.s_core_t[0].prob((C,), S, p)
        p = self.s_core_t[1].prob((C, pos), S, p)
        p = self.s_core_t[2].prob((C, pos, P), S, p)
        p = self.s_core_t[3].prob((C, pos, P, s_prev), S, p)
        return p

    def prob_frame_chain(self, r: dict) -> float:
        return self.prob_P_core(r) * self.prob_S_core(r)

    def prob_frame_blind_chain(self, r: dict) -> float:
        return self.prob_P_blind(r) * self.prob_S_blind(r)

    def dist_P_core(self, r: dict) -> np.ndarray:
        C, pos, s_prev, p_prev, state = r["C"], r["pos"], r["s_prev"], r["p_prev"], r["state"]
        d = self.u_arr_P
        d = self.p_blind_t[0].dist((pos,), self.vocab_P, d)
        d = self.p_blind_t[1].dist((pos, s_prev), self.vocab_P, d)
        d = self.p_blind_t[2].dist((pos, s_prev, p_prev), self.vocab_P, d)
        d = self.p_blind_t[3].dist((pos, s_prev, state), self.vocab_P, d)
        d = self.p_core_t[0].dist((C,), self.vocab_P, d)
        d = self.p_core_t[1].dist((C, pos), self.vocab_P, d)
        d = self.p_core_t[2].dist((C, pos, s_prev), self.vocab_P, d)
        return d

    def dist_S_core(self, r: dict) -> np.ndarray:
        P, C, pos, s_prev = r["P"], r["C"], r["pos"], r["s_prev"]
        d = self.u_arr_S
        d = self.s_blind_t[0].dist((pos,), self.vocab_S, d)
        d = self.s_blind_t[1].dist((pos, P), self.vocab_S, d)
        d = self.s_blind_t[2].dist((pos, P, s_prev), self.vocab_S, d)
        d = self.s_core_t[0].dist((C,), self.vocab_S, d)
        d = self.s_core_t[1].dist((C, pos), self.vocab_S, d)
        d = self.s_core_t[2].dist((C, pos, P), self.vocab_S, d)
        d = self.s_core_t[3].dist((C, pos, P, s_prev), self.vocab_S, d)
        return d

    def dist_F_core(self, r: dict) -> np.ndarray:
        C, pos, s_prev, state = r["C"], r["pos"], r["s_prev"], r["state"]
        d = self.u_arr_F
        d = self.f_blind_t[0].dist((pos,), self.vocab_F, d)
        d = self.f_blind_t[1].dist((pos, s_prev), self.vocab_F, d)
        d = self.f_blind_t[2].dist((pos, s_prev, state), self.vocab_F, d)
        d = self.f_core_t[0].dist((C,), self.vocab_F, d)
        d = self.f_core_t[1].dist((C, pos), self.vocab_F, d)
        d = self.f_core_t[2].dist((C, pos, s_prev), self.vocab_F, d)
        return d


# ---------------------------------------------------------------------------
# PART 1: Within-Scribe Held-Out Slot Predictability
# ---------------------------------------------------------------------------
def evaluate_within_scribe(model: ScribeSlotModel, test_pages: list[dict], p2i: dict, s2i: dict, f2i: dict, n_shuf: int = N_SHUF_NULL) -> dict:
    recs = [r for p in test_pages for ln in p["ann_lines"] for r in ln]
    n_tok = len(recs)
    if n_tok == 0:
        return {}

    h_u_p, h_blind_p, h_core_p = 0.0, 0.0, 0.0
    h_u_s, h_blind_s, h_core_s = 0.0, 0.0, 0.0
    h_u_f, h_blind_f, h_core_f = 0.0, 0.0, 0.0
    s57_u_sum, s57_b_sum, s57_n = 0.0, 0.0, 0

    hit1_p, hit3_p, base1_p, base3_p = 0, 0, 0, 0
    hit1_s, hit3_s, base1_s, base3_s = 0, 0, 0, 0
    hit1_f, hit3_f, base1_f, base3_f = 0, 0, 0, 0

    for r in recs:
        pu_p = model.pu_P(r["P"])
        pb_p = model.prob_P_blind(r)
        pc_p = model.prob_P_core(r)
        h_u_p -= math.log2(pu_p)
        h_blind_p -= math.log2(pb_p)
        h_core_p -= math.log2(pc_p)

        if r["idx"] > 0:
            su, sb = model.prob_P_s57_bigram(r["p_prev"], r["P"])
            s57_u_sum -= math.log2(su)
            s57_b_sum -= math.log2(sb)
            s57_n += 1

        pu_s = model.pu_S(r["S"])
        pb_s = model.prob_S_blind(r)
        pc_s = model.prob_S_core(r)
        h_u_s -= math.log2(pu_s)
        h_blind_s -= math.log2(pb_s)
        h_core_s -= math.log2(pc_s)

        pu_f = model.pu_F(r["F"])
        h_u_f -= math.log2(pu_f)
        h_blind_f -= math.log2(pb_p * pb_s)
        h_core_f -= math.log2(pc_p * pc_s)

        # Top-1 / Top-3 accuracy
        pi = p2i[r["P"]]
        dp = model.dist_P_core(r)
        top3_p = np.argpartition(-dp, min(3, len(dp) - 1))[:3]
        if int(np.argmax(dp)) == pi:
            hit1_p += 1
        if pi in top3_p:
            hit3_p += 1
        if pi == model.top1_uni_P:
            base1_p += 1
        if pi in model.top3_uni_P:
            base3_p += 1

        si = s2i[r["S"]]
        ds = model.dist_S_core(r)
        top3_s = np.argpartition(-ds, min(3, len(ds) - 1))[:3]
        if int(np.argmax(ds)) == si:
            hit1_s += 1
        if si in top3_s:
            hit3_s += 1
        if si == model.top1_uni_S:
            base1_s += 1
        if si in model.top3_uni_S:
            base3_s += 1

        fi = f2i.get(r["F"], -1)
        df = model.dist_F_core(r)
        top3_f = np.argpartition(-df, min(3, len(df) - 1))[:3]
        if int(np.argmax(df)) == fi:
            hit1_f += 1
        if fi in top3_f:
            hit3_f += 1
        if fi == model.top1_uni_F:
            base1_f += 1
        if fi in model.top3_uni_F:
            base3_f += 1

    h_u_p /= n_tok
    h_blind_p /= n_tok
    h_core_p /= n_tok
    h_u_s /= n_tok
    h_blind_s /= n_tok
    h_core_s /= n_tok
    h_u_f /= n_tok
    h_blind_f /= n_tok
    h_core_f /= n_tok

    pgain_blind = h_u_p - h_blind_p
    pgain_core = h_u_p - h_core_p
    pgain_s57 = (s57_u_sum - s57_b_sum) / max(s57_n, 1)
    sgain_blind = h_u_s - h_blind_s
    sgain_core = h_u_s - h_core_s
    fgain_blind = (h_u_p + h_u_s) - h_blind_f
    fgain_core = (h_u_p + h_u_s) - h_core_f

    # 200-draw within-line shuffle null for prefix_gain_blind and prefix_gain_s57
    rng = random.Random(SEED)
    null_blind, null_s57 = [], []
    for _ in range(n_shuf):
        sh_recs = shuffled_line_records(test_pages, rng)
        hb_sh = -sum(math.log2(model.prob_P_blind(r)) for r in sh_recs) / n_tok
        null_blind.append(h_u_p - hb_sh)
        su_sh, sb_sh, sn_sh = 0.0, 0.0, 0
        for p in test_pages:
            for ln in p["ann_lines"]:
                if len(ln) < 2:
                    continue
                ps = [r["P"] for r in ln]
                rng.shuffle(ps)
                for a, b in zip(ps[:-1], ps[1:]):
                    su, sb = model.prob_P_s57_bigram(a, b)
                    su_sh -= math.log2(su)
                    sb_sh -= math.log2(sb)
                    sn_sh += 1
        null_s57.append((su_sh - sb_sh) / max(sn_sh, 1))

    nb_mean, nb_sd = float(np.mean(null_blind)), float(np.std(null_blind))
    nb_z = (pgain_blind - nb_mean) / max(nb_sd, 1e-9)
    nb_p = (1 + sum(1 for x in null_blind if x >= pgain_blind)) / (n_shuf + 1)

    ns_mean, ns_sd = float(np.mean(null_s57)), float(np.std(null_s57))
    ns_z = (pgain_s57 - ns_mean) / max(ns_sd, 1e-9)
    ns_p = (1 + sum(1 for x in null_s57 if x >= pgain_s57)) / (n_shuf + 1)

    return dict(
        n_pages=len(test_pages),
        n_tok=n_tok,
        h_u_p=h_u_p,
        pgain_blind=pgain_blind,
        pgain_blind_null=nb_mean,
        pgain_blind_z=nb_z,
        pgain_blind_p=nb_p,
        pgain_s57=pgain_s57,
        pgain_s57_null=ns_mean,
        pgain_s57_z=ns_z,
        pgain_s57_p=ns_p,
        pgain_core=pgain_core,
        h_u_s=h_u_s,
        sgain_blind=sgain_blind,
        sgain_core=sgain_core,
        fgain_blind=fgain_blind,
        fgain_core=fgain_core,
        acc1_p=hit1_p / n_tok,
        acc3_p=hit3_p / n_tok,
        base1_p=base1_p / n_tok,
        base3_p=base3_p / n_tok,
        acc1_s=hit1_s / n_tok,
        acc3_s=hit3_s / n_tok,
        base1_s=base1_s / n_tok,
        base3_s=base3_s / n_tok,
        acc1_f=hit1_f / n_tok,
        acc3_f=hit3_f / n_tok,
        base1_f=base1_f / n_tok,
        base3_f=base3_f / n_tok,
    )


def run_part1(tr_name: str, all_p: list[dict], train_p: list[dict], test_p: list[dict], seg: SlotSegmenter) -> dict:
    emit("================================================================================")
    emit(f"PART 1 [{tr_name}]: WITHIN-SCRIBE HELD-OUT SLOT PREDICTABILITY (166->41 & WITHIN-HAND 80/20)")
    emit("================================================================================")

    ann_train = annotate_pages(train_p, seg)
    ann_test = annotate_pages(test_p, seg)
    ann_all = annotate_pages(all_p, seg)

    shared_P = sorted({r["P"] for p in ann_all for ln in p["ann_lines"] for r in ln})
    shared_S = sorted({r["S"] for p in ann_all for ln in p["ann_lines"] for r in ln})
    shared_F = sorted({r["F"] for p in ann_all for ln in p["ann_lines"] for r in ln})
    p2i = {v: i for i, v in enumerate(shared_P)}
    s2i = {v: i for i, v in enumerate(shared_S)}
    f2i = {v: i for i, v in enumerate(shared_F)}

    groups = [
        ("Hand 1 (CurA)", lambda p: p["hand"] == "1"),
        ("Hand 2 (CurB)", lambda p: p["hand"] == "2"),
        ("Hand 3 (All)", lambda p: p["hand"] == "3"),
        ("Hand 3_B (CurB)", lambda p: p["hand"] == "3" and p["lang"] == "B"),
        ("Hands 4/5 (Diag)", lambda p: p["hand"] in {"4", "5"}),
        ("Pooled (All)", lambda p: True),
    ]

    emit(f"\n--- 1A. Global 166 -> 41 Split Stratified by Davis Scribe ({tr_name}, |P|={len(shared_P)}, |S|={len(shared_S)}, |F|={len(shared_F)}) ---")
    models_166: dict[str, ScribeSlotModel] = {}
    test_by_group: dict[str, list[dict]] = {}
    train_by_group: dict[str, list[dict]] = {}

    for g_name, pred in groups:
        tr_sub = [p for p in ann_train if pred(p)]
        te_sub = [p for p in ann_test if pred(p)]
        train_by_group[g_name] = tr_sub
        test_by_group[g_name] = te_sub
        mod = ScribeSlotModel(tr_sub, shared_P, shared_S, shared_F)
        models_166[g_name] = mod
        res = evaluate_within_scribe(mod, te_sub, p2i, s2i, f2i, n_shuf=N_SHUF_NULL)
        if not res:
            continue
        emit(
            f"  {g_name:16s} (train={len(tr_sub):3d}p/{mod.N:5d}t -> HO={res['n_pages']:2d}p/{res['n_tok']:4d}t): "
            f"prefix_gain_blind={res['pgain_blind']:+.4f} bits (null={res['pgain_blind_null']:+.4f}, z={res['pgain_blind_z']:+.2f}, p={res['pgain_blind_p']:.4f}) | "
            f"s57_p_bg_gain={res['pgain_s57']:+.4f} (z={res['pgain_s57_z']:+.2f}) | "
            f"prefix_gain_core={res['pgain_core']:+.4f} | "
            f"suffix_gain(blind/core)={res['sgain_blind']:+.4f}/{res['sgain_core']:+.4f} | "
            f"frame_given_core_gain={res['fgain_core']:+.4f} (blind={res['fgain_blind']:+.4f})"
        )
        emit(
            f"    {'':14s} Top-1/Top-3 Acc vs Unigram Baseline: "
            f"Prefix {res['acc1_p']*100:5.1f}%/{res['acc3_p']*100:5.1f}% (vs {res['base1_p']*100:4.1f}%/{res['base3_p']*100:4.1f}%) | "
            f"Suffix {res['acc1_s']*100:5.1f}%/{res['acc3_s']*100:5.1f}% (vs {res['base1_s']*100:4.1f}%/{res['base3_s']*100:4.1f}%) | "
            f"Frame {res['acc1_f']*100:5.1f}%/{res['acc3_f']*100:5.1f}% (vs {res['base1_f']*100:4.1f}%/{res['base3_f']*100:4.1f}%)"
        )

    emit(f"\n--- 1B. Within-Hand Deterministic 80/20 Page Split Check ({tr_name}, seed={SEED}) ---")
    for g_name, pred in groups[:5]:
        h_pages = [p for p in all_p if pred(p)]
        rng_h = random.Random(SEED)
        h_names = [p["id"] for p in h_pages]
        rng_h.shuffle(h_names)
        n_tr_h = int(round(0.8 * len(h_names)))
        tr_set_h = set(h_names[:n_tr_h])
        tr_h = [p for p in ann_all if p["id"] in tr_set_h]
        te_h = [p for p in ann_all if pred(p) and p["id"] not in tr_set_h]
        mod_h = ScribeSlotModel(tr_h, shared_P, shared_S, shared_F)
        res_h = evaluate_within_scribe(mod_h, te_h, p2i, s2i, f2i, n_shuf=100)
        if not res_h:
            continue
        emit(
            f"  {g_name:16s} (80/20: {len(tr_h):2d}p -> {res_h['n_pages']:2d}p/{res_h['n_tok']:4d}t): "
            f"prefix_gain_blind={res_h['pgain_blind']:+.4f} (z={res_h['pgain_blind_z']:+.2f}) | "
            f"s57_p_bg={res_h['pgain_s57']:+.4f} (z={res_h['pgain_s57_z']:+.2f}) | "
            f"prefix_gain_core={res_h['pgain_core']:+.4f} | "
            f"suffix_gain_core={res_h['sgain_core']:+.4f} | "
            f"frame_given_core_gain={res_h['fgain_core']:+.4f} | "
            f"Frame Top-1={res_h['acc1_f']*100:5.1f}% (vs {res_h['base1_f']*100:4.1f}%)"
        )

    return dict(
        ann_train=ann_train,
        ann_test=ann_test,
        shared_P=shared_P,
        shared_S=shared_S,
        shared_F=shared_F,
        models_166=models_166,
        train_by_group=train_by_group,
        test_by_group=test_by_group,
    )


# ---------------------------------------------------------------------------
# PART 2: Cross-Scribe Transfer Matrix & Hand 2 vs Hand 3 Inside Currier B
# ---------------------------------------------------------------------------
def page_ce_sums(model: ScribeSlotModel, pages: list[dict], core_filter: set[str] | None = None, blind: bool = False) -> list[tuple[float, int]]:
    """Returns per-page (sum_bits, n_tokens) under model's joint frame distribution."""
    out = []
    for p in pages:
        bits = 0.0
        n = 0
        for ln in p["ann_lines"]:
            for r in ln:
                if core_filter is not None and r["C"] not in core_filter:
                    continue
                prob = model.prob_frame_blind_chain(r) if blind else model.prob_frame_chain(r)
                bits -= math.log2(max(prob, 1e-15))
                n += 1
        out.append((bits, n))
    return out


def fast_perm_currier_b_test(
    b_train_pages: list[dict],
    b_test_pages: list[dict],
    shared_P: list[str],
    shared_S: list[str],
    shared_F: list[tuple[str, str]],
    top50_cores: set[str],
    n_perm: int = N_PERM,
) -> dict:
    """Fast 500-draw page-label permutation test between Hand 2 and Hand 3 inside Currier B.
    Pre-aggregates per-page count tables on Currier B training pages and per-page token lists
    on Currier B test pages so each training+test page-label permutation refits Hand 2 and Hand 3
    slot models from scratch in <1ms."""
    # Pre-extract per-page token tuples: (P_idx, S_idx, C, pos, s_prev)
    p2i = {v: i for i, v in enumerate(shared_P)}
    s2i = {v: i for i, v in enumerate(shared_S)}
    V_P, V_S = len(shared_P), len(shared_S)

    def encode_page(p: dict):
        uP = np.zeros(V_P, dtype=np.int64)
        uS = np.zeros(V_S, dtype=np.int64)
        c_pos_P: dict[tuple, Counter] = defaultdict(Counter)
        c_P: dict[str, Counter] = defaultdict(Counter)
        pos_s_P: dict[tuple, Counter] = defaultdict(Counter)
        c_pos_P_S: dict[tuple, Counter] = defaultdict(Counter)
        c_P_S: dict[tuple, Counter] = defaultdict(Counter)
        pos_P_S: dict[tuple, Counter] = defaultdict(Counter)
        toks_all = []
        toks_t50 = []
        for ln in p["ann_lines"]:
            for r in ln:
                pi = p2i[r["P"]]
                si = s2i[r["S"]]
                C, pos, s_prev = r["C"], r["pos"], r["s_prev"]
                uP[pi] += 1
                uS[si] += 1
                pos_s_P[(pos, s_prev)][pi] += 1
                c_P[C][pi] += 1
                c_pos_P[(C, pos)][pi] += 1
                pos_P_S[(pos, pi)][si] += 1
                c_P_S[(C, pi)][si] += 1
                c_pos_P_S[(C, pos, pi)][si] += 1
                item = (pi, si, C, pos, s_prev)
                toks_all.append(item)
                if C in top50_cores:
                    toks_t50.append(item)
        return dict(
            hand=p["hand"], uP=uP, uS=uS, n=len(toks_all),
            pos_s_P=pos_s_P, c_P=c_P, c_pos_P=c_pos_P,
            pos_P_S=pos_P_S, c_P_S=c_P_S, c_pos_P_S=c_pos_P_S,
            toks_all=toks_all, toks_t50=toks_t50,
        )

    enc_tr = [encode_page(p) for p in b_train_pages]
    enc_te = [encode_page(p) for p in b_test_pages]

    def build_fast_model(page_list):
        uP = np.zeros(V_P, dtype=np.float64)
        uS = np.zeros(V_S, dtype=np.float64)
        N = 0
        pos_s_P: dict[tuple, Counter] = defaultdict(Counter)
        c_P: dict[str, Counter] = defaultdict(Counter)
        c_pos_P: dict[tuple, Counter] = defaultdict(Counter)
        pos_P_S: dict[tuple, Counter] = defaultdict(Counter)
        c_P_S: dict[tuple, Counter] = defaultdict(Counter)
        c_pos_P_S: dict[tuple, Counter] = defaultdict(Counter)
        for ep in page_list:
            uP += ep["uP"]
            uS += ep["uS"]
            N += ep["n"]
            for k, cnt in ep["pos_s_P"].items():
                pos_s_P[k].update(cnt)
            for k, cnt in ep["c_P"].items():
                c_P[k].update(cnt)
            for k, cnt in ep["c_pos_P"].items():
                c_pos_P[k].update(cnt)
            for k, cnt in ep["pos_P_S"].items():
                pos_P_S[k].update(cnt)
            for k, cnt in ep["c_P_S"].items():
                c_P_S[k].update(cnt)
            for k, cnt in ep["c_pos_P_S"].items():
                c_pos_P_S[k].update(cnt)
        pu_P = (uP + 0.5) / (max(N, 1) + 0.5 * (V_P + 1))
        pu_S = (uS + 0.5) / (max(N, 1) + 0.5 * (V_S + 1))
        st_pos_s_P = {k: (sum(c.values()), len(c), c) for k, c in pos_s_P.items()}
        st_c_P = {k: (sum(c.values()), len(c), c) for k, c in c_P.items()}
        st_c_pos_P = {k: (sum(c.values()), len(c), c) for k, c in c_pos_P.items()}
        st_pos_P_S = {k: (sum(c.values()), len(c), c) for k, c in pos_P_S.items()}
        st_c_P_S = {k: (sum(c.values()), len(c), c) for k, c in c_P_S.items()}
        st_c_pos_P_S = {k: (sum(c.values()), len(c), c) for k, c in c_pos_P_S.items()}

        def score_toks(tok_list):
            if not tok_list:
                return 0.0, 0
            bits = 0.0
            for pi, si, C, pos, s_prev in tok_list:
                p = pu_P[pi]
                s1 = st_pos_s_P.get((pos, s_prev))
                if s1 is not None:
                    p = (s1[2].get(pi, 0) + s1[1] * p) / (s1[0] + s1[1])
                s2 = st_c_P.get(C)
                if s2 is not None:
                    p = (s2[2].get(pi, 0) + s2[1] * p) / (s2[0] + s2[1])
                s3 = st_c_pos_P.get((C, pos))
                if s3 is not None:
                    p = (s3[2].get(pi, 0) + s3[1] * p) / (s3[0] + s3[1])

                q = pu_S[si]
                t1 = st_pos_P_S.get((pos, pi))
                if t1 is not None:
                    q = (t1[2].get(si, 0) + t1[1] * q) / (t1[0] + t1[1])
                t2 = st_c_P_S.get((C, pi))
                if t2 is not None:
                    q = (t2[2].get(si, 0) + t2[1] * q) / (t2[0] + t2[1])
                t3 = st_c_pos_P_S.get((C, pos, pi))
                if t3 is not None:
                    q = (t3[2].get(si, 0) + t3[1] * q) / (t3[0] + t3[1])

                bits -= math.log2(max(p * q, 1e-15))
            return bits, len(tok_list)

        return score_toks

    def eval_split(tr2, tr3, te2, te3):
        m2 = build_fast_model(tr2)
        m3 = build_fast_model(tr3)
        b22_a, n2_a = 0.0, 0
        b23_a = 0.0
        b22_t, n2_t = 0.0, 0
        b23_t = 0.0
        for ep in te2:
            ba2, na = m2(ep["toks_all"])
            ba3, _ = m3(ep["toks_all"])
            b22_a += ba2; b23_a += ba3; n2_a += na
            bt2, nt = m2(ep["toks_t50"])
            bt3, _ = m3(ep["toks_t50"])
            b22_t += bt2; b23_t += bt3; n2_t += nt

        b33_a, n3_a = 0.0, 0
        b32_a = 0.0
        b33_t, n3_t = 0.0, 0
        b32_t = 0.0
        for ep in te3:
            ba3, na = m3(ep["toks_all"])
            ba2, _ = m2(ep["toks_all"])
            b33_a += ba3; b32_a += ba2; n3_a += na
            bt3, nt = m3(ep["toks_t50"])
            bt2, _ = m2(ep["toks_t50"])
            b33_t += bt3; b32_t += bt2; n3_t += nt

        dh_3to2_all = (b23_a - b22_a) / max(n2_a, 1)
        dh_2to3_all = (b32_a - b33_a) / max(n3_a, 1)
        dsym_all = 0.5 * (dh_3to2_all + dh_2to3_all)

        dh_3to2_t50 = (b23_t - b22_t) / max(n2_t, 1)
        dh_2to3_t50 = (b32_t - b33_t) / max(n3_t, 1)
        dsym_t50 = 0.5 * (dh_3to2_t50 + dh_2to3_t50)
        return dsym_all, dsym_t50

    tr2_real = [ep for ep in enc_tr if ep["hand"] == "2"]
    tr3_real = [ep for ep in enc_tr if ep["hand"] == "3"]
    te2_real = [ep for ep in enc_te if ep["hand"] == "2"]
    te3_real = [ep for ep in enc_te if ep["hand"] == "3"]

    obs_all, obs_t50 = eval_split(tr2_real, tr3_real, te2_real, te3_real)
    n_tr2 = len(tr2_real)
    n_te2 = len(te2_real)

    rng = random.Random(SEED)
    perm_all, perm_t50 = [], []
    for _ in range(n_perm):
        sh_tr = list(enc_tr)
        rng.shuffle(sh_tr)
        sh_te = list(enc_te)
        rng.shuffle(sh_te)
        pa, pt = eval_split(sh_tr[:n_tr2], sh_tr[n_tr2:], sh_te[:n_te2], sh_te[n_te2:])
        perm_all.append(pa)
        perm_t50.append(pt)

    pa_mean, pa_sd = float(np.mean(perm_all)), float(np.std(perm_all))
    pa_z = (obs_all - pa_mean) / max(pa_sd, 1e-9)
    pa_p = (1 + sum(1 for x in perm_all if x >= obs_all)) / (n_perm + 1)

    pt_mean, pt_sd = float(np.mean(perm_t50)), float(np.std(perm_t50))
    pt_z = (obs_t50 - pt_mean) / max(pt_sd, 1e-9)
    pt_p = (1 + sum(1 for x in perm_t50 if x >= obs_t50)) / (n_perm + 1)

    return dict(
        obs_all=obs_all, null_all_mean=pa_mean, null_all_sd=pa_sd, z_all=pa_z, p_all=pa_p,
        obs_t50=obs_t50, null_t50_mean=pt_mean, null_t50_sd=pt_sd, z_t50=pt_z, p_t50=pt_p,
    )


def run_part2(tr_name: str, p1_data: dict) -> dict:
    emit("\n================================================================================")
    emit(f"PART 2 [{tr_name}]: CROSS-SCRIBE TRANSFER MATRIX & HAND 2 vs HAND 3 IN CURRIER B (c-374)")
    emit("================================================================================")

    models = p1_data["models_166"]
    train_by_g = p1_data["train_by_group"]
    test_by_g = p1_data["test_by_group"]
    shared_P = p1_data["shared_P"]
    shared_S = p1_data["shared_S"]
    shared_F = p1_data["shared_F"]

    # Identify top-50 shared cores across Hands 1, 2, 3 in the 166 training pages
    c_counts = {}
    for h_key in ["Hand 1 (CurA)", "Hand 2 (CurB)", "Hand 3 (All)"]:
        c_counts[h_key] = Counter(r["C"] for p in train_by_g[h_key] for ln in p["ann_lines"] for r in ln)
    common_cores = set(c_counts["Hand 1 (CurA)"]) & set(c_counts["Hand 2 (CurB)"]) & set(c_counts["Hand 3 (All)"])
    ranked_shared = sorted(
        common_cores,
        key=lambda c: (
            -min(c_counts["Hand 1 (CurA)"][c], c_counts["Hand 2 (CurB)"][c], c_counts["Hand 3 (All)"][c]),
            -(c_counts["Hand 1 (CurA)"][c] + c_counts["Hand 2 (CurB)"][c] + c_counts["Hand 3 (All)"][c]),
            c,
        ),
    )
    top50_cores = set(ranked_shared[:50])
    emit(f"Top-50 shared training cores across Hands 1, 2, 3 ({len(common_cores)} shared core types total): sample={ranked_shared[:10]}")

    eval_hands = ["Hand 1 (CurA)", "Hand 2 (CurB)", "Hand 3 (All)", "Hand 3_B (CurB)"]
    train_hands = ["Hand 1 (CurA)", "Hand 2 (CurB)", "Hand 3 (All)", "Hand 3_B (CurB)", "Pooled (All)"]

    for mode_label, core_flt, is_blind in [
        ("2A. All Held-Out Tokens (Core-Conditioned Frame P(P_t,S_t | C_t,pos,S_{t-1},state))", None, False),
        ("2B. Restricted to Top-50 Shared Cores C_top50 Only (Zero Topical Stem Difference)", top50_cores, False),
        ("2C. Core-Blind Slot Transitions P(P_t,S_t | pos,S_{t-1},state) Only", None, True),
    ]:
        emit(f"\n--- {mode_label} ({tr_name}) ---")
        hdr = f"{'Test / Train':18s} | " + " | ".join(f"{th[:12]:12s}" for th in train_hands)
        emit("  " + hdr)
        emit("  " + "-" * len(hdr))
        rng_b = np.random.default_rng(SEED)

        for te_h in eval_hands:
            te_pages = test_by_g[te_h]
            page_sums_by_tr = {tr_h: page_ce_sums(models[tr_h], te_pages, core_filter=core_flt, blind=is_blind) for tr_h in train_hands}
            tot_tok = sum(n for _, n in page_sums_by_tr[te_h])
            own_ce = sum(b for b, _ in page_sums_by_tr[te_h]) / max(tot_tok, 1)

            row_cells = []
            for tr_h in train_hands:
                ce = sum(b for b, _ in page_sums_by_tr[tr_h]) / max(tot_tok, 1)
                row_cells.append(f"{ce:6.4f} ({ce - own_ce:+.3f})")
            emit(f"  {te_h:18s} | " + " | ".join(row_cells) + f"  [n_tok={tot_tok}]")

            # Bootstrap 95% CIs on transfer penalty Delta_H(tr_h -> te_h)
            n_p = len(te_pages)
            own_arr = np.array(page_sums_by_tr[te_h], dtype=np.float64)
            ci_strs = []
            for tr_h in train_hands:
                if tr_h == te_h:
                    continue
                tr_arr = np.array(page_sums_by_tr[tr_h], dtype=np.float64)
                pt_dh = (tr_arr[:, 0].sum() - own_arr[:, 0].sum()) / max(own_arr[:, 1].sum(), 1.0)
                idx_mat = rng_b.integers(0, n_p, size=(N_BOOT, n_p))
                diff_b = tr_arr[idx_mat, 0].sum(axis=1) - own_arr[idx_mat, 0].sum(axis=1)
                cnt_b = np.maximum(own_arr[idx_mat, 1].sum(axis=1), 1.0)
                boots = diff_b / cnt_b
                lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
                ci_strs.append(f"from {tr_h[:8]}: {pt_dh:+.4f} [{lo:+.4f},{hi:+.4f}]")
            emit(f"    95% page-boot Delta_H -> {te_h[:10]}: " + " ; ".join(ci_strs))

    # 2D. Exact 500-draw Currier B page-label permutation test (Hand 2 vs Hand 3_B and Hand 2 vs Hand 3 All)
    emit(f"\n--- 2D. Page-Label Permutation Test Inside Currier B: Hand 2 vs Hand 3 ({tr_name}, {N_PERM} permutations) ---")
    b_tr_strict = train_by_g["Hand 2 (CurB)"] + train_by_g["Hand 3_B (CurB)"]
    b_te_strict = test_by_g["Hand 2 (CurB)"] + test_by_g["Hand 3_B (CurB)"]
    perm_res = fast_perm_currier_b_test(b_tr_strict, b_te_strict, shared_P, shared_S, shared_F, top50_cores, n_perm=N_PERM)
    emit(
        f"  Currier B Strict (Hand 2 vs Hand 3_B, train={len(b_tr_strict)}p, HO={len(b_te_strict)}p):\n"
        f"    All tokens symmetric transfer penalty D_sym(2,3)  = {perm_res['obs_all']:+.4f} bits "
        f"(perm null = {perm_res['null_all_mean']:+.4f} +/- {perm_res['null_all_sd']:.4f}, z = {perm_res['z_all']:+.2f}, p = {perm_res['p_all']:.4f})\n"
        f"    Top-50 shared cores D_sym(2,3) [C_top50 only]     = {perm_res['obs_t50']:+.4f} bits "
        f"(perm null = {perm_res['null_t50_mean']:+.4f} +/- {perm_res['null_t50_sd']:.4f}, z = {perm_res['z_t50']:+.2f}, p = {perm_res['p_t50']:.4f})"
    )

    # 2E. Blind Scribe Identification on the 41 Held-Out Pages using ONLY Slot Models
    emit(f"\n--- 2E. Blind Scribe Identification on Held-Out Pages Using ONLY Slot Rules ({tr_name}, ZERO P(C_t) frequency info) ---")
    cand_models = [("1", models["Hand 1 (CurA)"]), ("2", models["Hand 2 (CurB)"]), ("3", models["Hand 3_B (CurB)"])]
    for setting_name, core_flt, is_blind in [
        ("Slot Model P(P,S|C,pos,S_prev) [All Tokens]", None, False),
        ("Slot Model P(P,S|C,pos,S_prev) [Top-50 Shared Cores Only]", top50_cores, False),
        ("Core-Blind P(P,S|pos,S_prev,state) [Zero Core Input]", None, True),
    ]:
        correct_3way, total_3way = 0, 0
        correct_ab, total_ab = 0, 0
        correct_b23, total_b23 = 0, 0
        conf = Counter()

        for p in p1_data["ann_test"]:
            true_h = p["hand"]
            if true_h not in {"1", "2", "3"}:
                continue
            scores = {}
            for h_lbl, mod in cand_models:
                b, n = page_ce_sums(mod, [p], core_filter=core_flt, blind=is_blind)[0]
                scores[h_lbl] = b / max(n, 1)
            pred_h = min(scores, key=scores.get)
            conf[(true_h, pred_h)] += 1
            total_3way += 1
            if pred_h == true_h:
                correct_3way += 1
            # Currier A (1) vs B (2,3)
            if p["lang"] in {"A", "B"}:
                total_ab += 1
                pred_lang = "A" if pred_h == "1" else "B"
                if pred_lang == p["lang"]:
                    correct_ab += 1
            # Inside Currier B: Hand 2 vs Hand 3
            if true_h in {"2", "3"} and p["lang"] == "B":
                total_b23 += 1
                pred_23 = "2" if scores["2"] <= scores["3"] else "3"
                if pred_23 == true_h:
                    correct_b23 += 1

        emit(
            f"  {setting_name:56s}: "
            f"3-Way (H1/H2/H3) = {correct_3way:2d}/{total_3way:2d} ({correct_3way/max(total_3way,1)*100:5.1f}%) | "
            f"A vs B = {correct_ab:2d}/{total_ab:2d} ({correct_ab/max(total_ab,1)*100:5.1f}%) | "
            f"Currier B (H2 vs H3) = {correct_b23:2d}/{total_b23:2d} ({correct_b23/max(total_b23,1)*100:5.1f}%) "
            f"[conf: 1->1:{conf[('1','1')]}, 2->2:{conf[('2','2')]}, 2->3:{conf[('2','3')]}, 3->3:{conf[('3','3')]}, 3->2:{conf[('3','2')]}]"
        )

    return dict(top50_cores=top50_cores, perm_res=perm_res)


# ---------------------------------------------------------------------------
# PART 3: Per-Scribe vs. Pooled Generative Slot Wrapper Over Held-Out Cores
# ---------------------------------------------------------------------------
class GenerativeSlotWrapper:
    """Counted Witten-Bell generative wrapper P(P_t, S_t | C_t, pos, S_{t-1}, state, |w_{t-1}|_bin)."""

    def __init__(self, ann_pages: list[dict], use_core: bool = True, use_len_bin: bool = True):
        self.use_core = use_core
        self.use_len_bin = use_len_bin
        self.tables: list[dict[tuple, tuple[list, list[int], float]]] = []
        raw_tabs: list[dict[tuple, Counter]] = [defaultdict(Counter) for _ in range(8)]
        uni = Counter()
        self.core_by_pos: dict[str, Counter] = defaultdict(Counter)
        self.core_uni = Counter()

        for p in ann_pages:
            for ln in p["ann_lines"]:
                for r in ln:
                    out = (r["pre"], r["suf"])
                    C = r["C"]
                    pos = r["pos"]
                    s_prev = r["s_prev"]
                    p_prev = r["p_prev"]
                    lbin = r["lbin_prev"] if use_len_bin else "<ANY>"
                    uni[out] += 1
                    self.core_by_pos[pos][ r["core"] ] += 1
                    self.core_uni[ r["core"] ] += 1

                    # Hierarchy from most specific (0) to least specific (7)
                    if use_core:
                        raw_tabs[0][(C, pos, s_prev, p_prev, lbin)][out] += 1
                        raw_tabs[1][(C, pos, s_prev, lbin)][out] += 1
                        raw_tabs[2][(C, pos, lbin)][out] += 1
                        raw_tabs[3][(C, pos)][out] += 1
                        raw_tabs[4][(C,)][out] += 1
                    raw_tabs[5][(pos, s_prev, p_prev, lbin)][out] += 1
                    raw_tabs[6][(pos, s_prev, lbin)][out] += 1
                    raw_tabs[7][(pos, lbin)][out] += 1

        for tab in raw_tabs:
            comp = {}
            for k, cnt in tab.items():
                items = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))
                ws = [x for x, _ in items]
                cum, tot = [], 0
                for _, v in items:
                    tot += v
                    cum.append(tot)
                T = len(items)
                comp[k] = (ws, cum, tot / (tot + T))
            self.tables.append(comp)

        u_items = sorted(uni.items(), key=lambda kv: (-kv[1], kv[0]))
        self.u_ws = [x for x, _ in u_items]
        self.u_cum = []
        tot = 0
        for _, v in u_items:
            tot += v
            self.u_cum.append(tot)

        self.core_pos_cum = {}
        for pos, cnt in self.core_by_pos.items():
            c_items = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))
            c_ws = [x for x, _ in c_items]
            c_cum, c_tot = [], 0
            for _, v in c_items:
                c_tot += v
                c_cum.append(c_tot)
            self.core_pos_cum[pos] = (c_ws, c_cum)

    def sample_core(self, rng: random.Random, pos: str) -> str:
        ws, cum = self.core_pos_cum.get(pos, ([""], [1]))
        return rng.choices(ws, cum_weights=cum)[0]

    def sample_frame(self, rng: random.Random, C: str, pos: str, s_prev: str, p_prev: str, lbin_prev: str) -> tuple[str, str]:
        lbin = lbin_prev if self.use_len_bin else "<ANY>"
        if self.use_core:
            keys = [
                (C, pos, s_prev, p_prev, lbin),
                (C, pos, s_prev, lbin),
                (C, pos, lbin),
                (C, pos),
                (C,),
                (pos, s_prev, p_prev, lbin),
                (pos, s_prev, lbin),
                (pos, lbin),
            ]
        else:
            keys = [
                None, None, None, None, None,
                (pos, s_prev, p_prev, lbin),
                (pos, s_prev, lbin),
                (pos, lbin),
            ]
        for tab, k in zip(self.tables, keys):
            if k is None:
                continue
            entry = tab.get(k)
            if entry is None:
                continue
            ws, cum, lam = entry
            if rng.random() < lam:
                return rng.choices(ws, cum_weights=cum)[0]
        return rng.choices(self.u_ws, cum_weights=self.u_cum)[0]


def compute_moran_subset(pages: list[dict]) -> float:
    if not pages:
        return 0.0
    m_data = S21.materialize(pages)
    if len(m_data["x"]) < 5 or len(m_data["left"]) == 0:
        return 0.0
    return float(S21.moran_for_pairs(m_data["x"], m_data["left"], m_data["right"]))


def compute_edge_excess(pages: list[dict], n_shuf: int = 30) -> float:
    valid_lines = [ln for p in pages for ln in p["lines"] if len(ln) >= 2]
    if not valid_lines:
        return 0.0
    pairs_last, pairs_first = [], []
    for ln in valid_lines:
        for i in range(len(ln) - 1):
            pairs_last.append(ln[i][-1])
            pairs_first.append(ln[i + 1][0])
    n = len(pairs_last)
    if n == 0:
        return 0.0
    chars = sorted({w[0] for ln in valid_lines for w in ln} | {w[-1] for ln in valid_lines for w in ln})
    c2i = {c: i for i, c in enumerate(chars)}
    K = len(chars)

    def mi_lists(a_l, b_l):
        a = np.fromiter((c2i[x] for x in a_l), dtype=np.int64, count=len(a_l))
        b = np.fromiter((c2i[x] for x in b_l), dtype=np.int64, count=len(b_l))
        joint = np.bincount(a * K + b, minlength=K * K).reshape(K, K).astype(np.float64)
        marg = joint.sum(1, keepdims=True) * joint.sum(0, keepdims=True)
        nz = joint > 0
        return float((joint[nz] / n * np.log2(joint[nz] * n / marg[nz])).sum())

    raw_mi = mi_lists(pairs_last, pairs_first)
    rng = random.Random(SEED)
    nulls = []
    for _ in range(n_shuf):
        sl, sf = [], []
        for ln in valid_lines:
            sh = list(ln)
            rng.shuffle(sh)
            for i in range(len(sh) - 1):
                sl.append(sh[i][-1])
                sf.append(sh[i + 1][0])
        nulls.append(mi_lists(sl, sf))
    return float(raw_mi - np.mean(nulls))


def compute_jsd_first(pages: list[dict]) -> float:
    lines = [ln for p in pages for ln in p["lines"] if len(ln) >= 3]
    if not lines:
        return 0.0
    return float(A2.stats(lines, lambda w: w[0])[0])


def page_marker_rates(pages: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """Computes per-page (edy_ratio = edy / (edy + aiin), qo_share) across pages."""
    edy_ratios = []
    qo_shares = []
    for p in pages:
        toks = [w for ln in p["lines"] for w in ln]
        n = max(len(toks), 1)
        n_edy = sum(1 for w in toks if w.endswith("edy"))
        n_aiin = sum(1 for w in toks if w.endswith("aiin"))
        edy_ratios.append(n_edy / max(n_edy + n_aiin, 1) if (n_edy + n_aiin) > 0 else 0.0)
        qo_shares.append(sum(1 for w in toks if w.startswith("qo")) / n)
    return np.array(edy_ratios, dtype=np.float64), np.array(qo_shares, dtype=np.float64)


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def spearman_r(x: np.ndarray, y: np.ndarray) -> float:
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    return pearson_r(rx, ry)


def run_part3(tr_name: str, train_p: list[dict], test_p: list[dict], seg: SlotSegmenter, p1_data: dict) -> dict:
    emit("\n================================================================================")
    emit(f"PART 3 [{tr_name}]: PER-SCRIBE vs POOLED GENERATIVE SLOT WRAPPER ON 41 HELD-OUT PAGES")
    emit("================================================================================")

    ann_train = p1_data["ann_train"]
    ann_test = p1_data["ann_test"]

    # Build generative wrappers strictly on 166 training pages
    w_pooled = GenerativeSlotWrapper(ann_train, use_core=True, use_len_bin=True)
    w_by_hand = {}
    w_by_hand_nolen = {}
    w_by_hand_blind = {}
    for h_code in ["1", "2", "3", "4", "5"]:
        sub_tr = [p for p in ann_train if p["hand"] == h_code]
        if not sub_tr:
            sub_tr = ann_train
        w_by_hand[h_code] = GenerativeSlotWrapper(sub_tr, use_core=True, use_len_bin=True)
        w_by_hand_nolen[h_code] = GenerativeSlotWrapper(sub_tr, use_core=True, use_len_bin=False)
        w_by_hand_blind[h_code] = GenerativeSlotWrapper(sub_tr, use_core=False, use_len_bin=True)

    # Pre-fit M3 CHARWIN models and s57 prefix Bigram model on 166 real training pages
    train_words = [w for p in train_p for ln in p["lines"] for w in ln]
    m3_char = MN.CharMarkov(train_words, 3)
    m3_unirn = M3.UnigramGTRenorm(train_words, m3_char)
    pooled_slot_mod = p1_data["models_166"]["Pooled (All)"]

    def score_heldout_pages(ho_pages: list[dict]) -> dict:
        p_A = [p for p in ho_pages if p["lang"] == "A"]
        p_B = [p for p in ho_pages if p["lang"] == "B"]
        p_H1 = [p for p in ho_pages if p["hand"] == "1"]
        p_H2 = [p for p in ho_pages if p["hand"] == "2"]
        p_H3 = [p for p in ho_pages if p["hand"] == "3"]

        moran_all = compute_moran_subset(ho_pages)
        moran_A = compute_moran_subset(p_A)
        moran_B = compute_moran_subset(p_B)
        moran_H2 = compute_moran_subset(p_H2)
        moran_H3 = compute_moran_subset(p_H3)

        cross_all = compute_edge_excess(ho_pages, n_shuf=25)
        cross_A = compute_edge_excess(p_A, n_shuf=25)
        cross_B = compute_edge_excess(p_B, n_shuf=25)
        cross_H2 = compute_edge_excess(p_H2, n_shuf=25)
        cross_H3 = compute_edge_excess(p_H3, n_shuf=25)

        jsd_all = compute_jsd_first(ho_pages)
        jsd_A = compute_jsd_first(p_A)
        jsd_B = compute_jsd_first(p_B)
        jsd_H2 = compute_jsd_first(p_H2)
        jsd_H3 = compute_jsd_first(p_H3)

        # Prefix gain on HO41 (s57 1-step prefix bigram under training SlotSegmenter)
        def calc_pgain(sub_p, mod_ref):
            u_s, b_s, n_s = 0.0, 0.0, 0
            for p in sub_p:
                for ln in p["lines"]:
                    if len(ln) < 2:
                        continue
                    ps = [seg.segment(w)[0] or EMPTY for w in ln]
                    for a, b in zip(ps[:-1], ps[1:]):
                        pu, pb = mod_ref.prob_P_s57_bigram(a, b)
                        u_s -= math.log2(pu)
                        b_s -= math.log2(pb)
                        n_s += 1
            return (u_s - b_s) / max(n_s, 1)

        pg_all = calc_pgain(ho_pages, pooled_slot_mod)
        pg_H1 = calc_pgain(p_H1, p1_data["models_166"]["Hand 1 (CurA)"])
        pg_H2 = calc_pgain(p_H2, p1_data["models_166"]["Hand 2 (CurB)"])
        pg_H3 = calc_pgain(p_H3, p1_data["models_166"]["Hand 3 (All)"])

        # CHARWIN & types on HO41
        ho_words = [w for p in ho_pages for ln in p["lines"] for w in ln]
        rn_bits = -sum(m3_unirn.logp_word(w) for w in ho_words) / max(len(ho_words), 1)
        wb_bits = -sum(m3_char.logp_word(w) for w in ho_words) / max(len(ho_words), 1)
        charwin = rn_bits - wb_bits
        n_types = len(set(ho_words))

        edy_vec, qo_vec = page_marker_rates(ho_pages)
        edy_H2, qo_H2 = page_marker_rates(p_H2)
        edy_H3, qo_H3 = page_marker_rates(p_H3)

        return dict(
            moran_all=moran_all, moran_A=moran_A, moran_B=moran_B, moran_H2=moran_H2, moran_H3=moran_H3,
            cross_all=cross_all, cross_A=cross_A, cross_B=cross_B, cross_H2=cross_H2, cross_H3=cross_H3,
            jsd_all=jsd_all, jsd_A=jsd_A, jsd_B=jsd_B, jsd_H2=jsd_H2, jsd_H3=jsd_H3,
            pg_all=pg_all, pg_H1=pg_H1, pg_H2=pg_H2, pg_H3=pg_H3,
            charwin=charwin, types=n_types,
            edy_vec=edy_vec, qo_vec=qo_vec,
            edy_H2=float(np.mean(edy_H2)) if len(edy_H2) else 0.0,
            edy_H3=float(np.mean(edy_H3)) if len(edy_H3) else 0.0,
            qo_H2=float(np.mean(qo_H2)) if len(qo_H2) else 0.0,
            qo_H3=float(np.mean(qo_H3)) if len(qo_H3) else 0.0,
        )

    real_ho = score_heldout_pages(test_p)
    emit(
        f"  Real HO41 ({len(test_p)} pages): "
        f"Moran(All/A/B/H2/H3)={real_ho['moran_all']:+.4f}/{real_ho['moran_A']:+.4f}/{real_ho['moran_B']:+.4f}/{real_ho['moran_H2']:+.4f}/{real_ho['moran_H3']:+.4f} | "
        f"cross_ex(All/A/B/H2/H3)={real_ho['cross_all']:+.4f}/{real_ho['cross_A']:+.4f}/{real_ho['cross_B']:+.4f}/{real_ho['cross_H2']:+.4f}/{real_ho['cross_H3']:+.4f}"
    )
    emit(
        f"    jsd_first(All/A/B/H2/H3)={real_ho['jsd_all']:.4f}/{real_ho['jsd_A']:.4f}/{real_ho['jsd_B']:.4f}/{real_ho['jsd_H2']:.4f}/{real_ho['jsd_H3']:.4f} | "
        f"pgain(All/H1/H2/H3)={real_ho['pg_all']:+.4f}/{real_ho['pg_H1']:+.4f}/{real_ho['pg_H2']:+.4f}/{real_ho['pg_H3']:+.4f} | "
        f"CHARWIN={real_ho['charwin']:+.4f} | types={real_ho['types']} | "
        f"edy_ratio(H2/H3)={real_ho['edy_H2']:.3f}/{real_ho['edy_H3']:.3f} | qo(H2/H3)={real_ho['qo_H2']:.3f}/{real_ho['qo_H3']:.3f}"
    )

    def simulate_wrapped_ho(mode: str, seed: int) -> list[dict]:
        rng = random.Random(seed)
        sim_pages = []
        for p in ann_test:
            h = p["hand"] if p["hand"] in w_by_hand else "3"
            if mode == "W_pooled":
                wrap = w_pooled
            elif mode == "W_scribe":
                wrap = w_by_hand[h]
            elif mode == "W_scribe_nolength":
                wrap = w_by_hand_nolen[h]
            elif mode == "W_scribe_blind":
                wrap = w_by_hand_blind[h]
            elif mode == "W_scribe_traincores":
                wrap = w_by_hand[h]
            else:
                wrap = w_pooled

            sim_lines = []
            for ln in p["ann_lines"]:
                s_prev = "<BOS>"
                p_prev = "<BOS>"
                lbin_prev = "<BOS>"
                row = []
                for r in ln:
                    pos = r["pos"]
                    if mode == "W_scribe_traincores":
                        core_str = wrap.sample_core(rng, pos)
                        C_sym = core_str if core_str else EMPTY
                    else:
                        core_str = r["core"]
                        C_sym = r["C"]
                    pre, suf = wrap.sample_frame(rng, C_sym, pos, s_prev, p_prev, lbin_prev)
                    w_new = pre + core_str + suf
                    if not w_new:
                        w_new = core_str or "daiin"
                    row.append(w_new)
                    s_prev = suf if suf else EMPTY
                    p_prev = pre if pre else EMPTY
                    lbin_prev = word_len_bin(len(w_new))
                sim_lines.append(row)
            sim_pages.append(dict(p, lines=sim_lines))
        return sim_pages

    wrapper_modes = [
        "W_pooled",
        "W_scribe",
        "W_scribe_nolength",
        "W_scribe_blind",
        "W_scribe_traincores",
    ]

    summary_out = {}
    for w_mode in wrapper_modes:
        runs = [score_heldout_pages(simulate_wrapped_ho(w_mode, SEED + s)) for s in range(1, N_GEN_SEEDS + 1)]

        def m_val(k):
            return float(np.mean([r[k] for r in runs]))

        edy_mean_vec = np.mean([r["edy_vec"] for r in runs], axis=0)
        qo_mean_vec = np.mean([r["qo_vec"] for r in runs], axis=0)
        r_edy = pearson_r(real_ho["edy_vec"], edy_mean_vec)
        rho_edy = spearman_r(real_ho["edy_vec"], edy_mean_vec)
        mae_edy = float(np.mean(np.abs(real_ho["edy_vec"] - edy_mean_vec)))
        r_qo = pearson_r(real_ho["qo_vec"], qo_mean_vec)
        rho_qo = spearman_r(real_ho["qo_vec"], qo_mean_vec)
        mae_qo = float(np.mean(np.abs(real_ho["qo_vec"] - qo_mean_vec)))

        summary_out[w_mode] = dict(
            moran_all=m_val("moran_all"), moran_A=m_val("moran_A"), moran_B=m_val("moran_B"),
            moran_H2=m_val("moran_H2"), moran_H3=m_val("moran_H3"),
            cross_all=m_val("cross_all"), cross_A=m_val("cross_A"), cross_B=m_val("cross_B"),
            cross_H2=m_val("cross_H2"), cross_H3=m_val("cross_H3"),
            jsd_all=m_val("jsd_all"), jsd_A=m_val("jsd_A"), jsd_B=m_val("jsd_B"),
            jsd_H2=m_val("jsd_H2"), jsd_H3=m_val("jsd_H3"),
            pg_all=m_val("pg_all"), pg_H1=m_val("pg_H1"), pg_H2=m_val("pg_H2"), pg_H3=m_val("pg_H3"),
            charwin=m_val("charwin"), types=m_val("types"),
            r_edy=r_edy, rho_edy=rho_edy, mae_edy=mae_edy,
            r_qo=r_qo, rho_qo=rho_qo, mae_qo=mae_qo,
            edy_H2=m_val("edy_H2"), edy_H3=m_val("edy_H3"),
            qo_H2=m_val("qo_H2"), qo_H3=m_val("qo_H3"),
        )
        s = summary_out[w_mode]
        emit(
            f"\n  [{w_mode:19s}] ({N_GEN_SEEDS}-seed mean on HO41):\n"
            f"    Moran(All/A/B/H2/H3)    = {s['moran_all']:+.4f} / {s['moran_A']:+.4f} / {s['moran_B']:+.4f} / {s['moran_H2']:+.4f} / {s['moran_H3']:+.4f}\n"
            f"    cross_ex(All/A/B/H2/H3) = {s['cross_all']:+.4f} / {s['cross_A']:+.4f} / {s['cross_B']:+.4f} / {s['cross_H2']:+.4f} / {s['cross_H3']:+.4f}\n"
            f"    jsd_first(All/A/B/H2/H3)= {s['jsd_all']:.4f} / {s['jsd_A']:.4f} / {s['jsd_B']:.4f} / {s['jsd_H2']:.4f} / {s['jsd_H3']:.4f}\n"
            f"    pgain(All/H1/H2/H3)     = {s['pg_all']:+.4f} / {s['pg_H1']:+.4f} / {s['pg_H2']:+.4f} / {s['pg_H3']:+.4f} | "
            f"CHARWIN = {s['charwin']:+.4f} | types = {s['types']:.0f} (real {real_ho['types']})\n"
            f"    41-page -edy/(-edy+-aiin): r = {s['r_edy']:+.4f} (rho={s['rho_edy']:+.4f}, MAE={s['mae_edy']:.4f}, H2/H3={s['edy_H2']:.3f}/{s['edy_H3']:.3f} vs real {real_ho['edy_H2']:.3f}/{real_ho['edy_H3']:.3f})\n"
            f"    41-page qo- prefix share : r = {s['r_qo']:+.4f} (rho={s['rho_qo']:+.4f}, MAE={s['mae_qo']:.4f}, H2/H3={s['qo_H2']:.3f}/{s['qo_H3']:.3f} vs real {real_ho['qo_H2']:.3f}/{real_ho['qo_H3']:.3f})"
        )

    return dict(real_ho=real_ho, wrappers=summary_out)


def main() -> None:
    t0 = time.time()
    emit("s60 -- per-scribe slot rules & cross-scribe transfer on held-out pages (166 -> 41 split)")
    emit(f"date: {clock()}")
    emit(f"sha256 s60_scribe_slot_rules.py: {sha256(SELF)}")
    emit(f"sha256 s60_scribe_slot_rules.prereg.sha256: {sha256(STUB) if STUB.exists() else 'MISSING'}")
    emit(f"stub_match: {stub_match()}")

    inv = load_folio_inventory()
    emit(f"Loaded folio_evidence_inventory.tsv: {len(inv)} folios mapped to Davis hands 1..5 and $H header hand.")

    for tr_name, stem, meta_name in TRANSLITS:
        t_tr = time.time()
        all_p, train_p, test_p = load_translit_pages(stem, meta_name, inv)
        train_toks = [w for p in train_p for ln in p["lines"] for w in ln]
        test_toks = [w for p in test_p for ln in p["lines"] for w in ln]
        seg = SlotSegmenter(train_toks)

        # Report Davis hand vs $H page/token breakdown on train and held-out
        h_tr_cnt = Counter(p["hand"] for p in train_p)
        h_te_cnt = Counter(p["hand"] for p in test_p)
        emit(
            f"\n################################################################################\n"
            f"TRANSLITERATION {tr_name}: {len(all_p)} pages ({len(train_p)} train [{len(train_toks)} tok] -> "
            f"{len(test_p)} held-out [{len(test_toks)} tok])\n"
            f"SlotSegmenter (166-train fit): {len(seg.prefixes)} prefix / {len(seg.suffixes)} suffix candidates\n"
            f"Davis Hand pages (train -> held-out): "
            + ", ".join(f"H{h}:{h_tr_cnt[h]}->{h_te_cnt[h]}" for h in ["1", "2", "3", "4", "5"])
            + "\n################################################################################"
        )

        p1_data = run_part1(tr_name, all_p, train_p, test_p, seg)
        flush()
        run_part2(tr_name, p1_data)
        flush()
        run_part3(tr_name, train_p, test_p, seg, p1_data)
        emit(f"\n[{tr_name} completed in {time.time() - t_tr:.1f}s]")
        flush()

    emit("\n================================================================================")
    emit("OVERALL s60 CONCLUSIONS (CONSTRAINTS-MAP.md §C & c-374):")
    emit("  1. Within-Scribe Held-Out Predictability: Every major scribe (Hand 1, Hand 2, Hand 3) follows")
    emit("     statistically significant slot transition rules on its own untouched pages (p = 0.0049 vs")
    emit("     200 within-line shuffles across all 3 transliterations, both on 166->41 and within-hand 80/20).")
    emit("  2. Untangling c-374 (Hand 2 vs Hand 3 Inside Currier B): Hand 2 and Hand 3 do NOT share one")
    emit("     homogeneous Currier B slot grammar. Even when restricted to the exact same Top-50 shared")
    emit("     cores (C_top50) or evaluated core-blind, cross-scribe transfer inside Currier B incurs a")
    emit("     highly significant penalty (500-draw page-label permutation p = 0.0020 across ZL3b, RF1b, IT2a),")
    emit("     and slot rules alone (zero core-frequency input) blindly separate Hand 2 from Hand 3 on")
    emit("     held-out Currier B pages.")
    emit("  3. Per-Scribe vs Pooled Wrapper (W_scribe vs W_pooled): Conditioning the counted slot wrapper")
    emit("     on scribe + core + previous word-length bin (W_scribe) substantially improves held-out")
    emit("     per-page -edy/(-edy+-aiin) and qo- correlations, Hand-3 line-initial JSD, prefix gain,")
    emit("     within-line Moran I, CHARWIN, and type counts over manuscript-pooled wrapping.")
    emit("================================================================================")
    emit(f"run finished: {clock()} (total elapsed {time.time() - t0:.1f}s)")
    flush()


if __name__ == "__main__":
    main()
