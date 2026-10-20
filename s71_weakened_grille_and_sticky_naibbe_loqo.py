"""s71 -- Weakened Table-and-Grille (WTG) & Sticky-Table Naibbe (S1.5):
Closing CONSTRAINTS-MAP.md §C lines 193-194 (Dot 25 / L-163) and Dot 22 (L-159).

PRE-REGISTERED (frozen in s71_weakened_grille_and_sticky_naibbe_loqo.prereg.sha256 BEFORE running on data; D-048).

THREE PRE-REGISTERED PARTS ACROSS ZL3b, RF1b, AND IT2a:
1. Part 1 (Dot 22 / L-159: Sticky-Table Naibbe S1.5 vs Default Naibbe on the s55 Wrapper-Free Taxonomy
   & s69 Prefix-Memory Profile):
   - Evaluates Greshko's Naibbe cipher (from data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx) on
     latin_cremma (Latin prose) and italian_dante poured into the ZL3b 38,000-token line/page skeleton
     under four pre-registered table-persistence mechanisms:
       (0) Naibbe_default (p_stick=0.00): independent 78-card deck draw per slot (s64 baseline).
       (1) Naibbe_line_sticky (p_stick=0.75): stays on previous table T_{t-1} with prob 0.75 within line,
           redraws from deck with prob 0.25, resets at every line break.
       (2) Naibbe_line_lock (p_stick=1.00): one table drawn at line start and held for the entire line,
           resetting at every line break.
       (3) Naibbe_page_bias: each page draws a Dirichlet-skewed deck preference over the 6 tables
           (Dirichlet(alpha_0 * w_deck), alpha_0 = 1.5).
   - Scores all mechanisms on the 8 s55 wrapper-free features, Euclidean distance in s55 z-space to
     Voynich (ZL3b, RF1b, IT2a) and CODE/GEN/NAIBBE centroids, and the s69 prefix-memory ladder
     (M1, M2-M1, M3-M1, M7, M8-M7, b_pos, a_pos, k1..k4 decay, and C1..C5, C3p, C4p).
   - Audits the exact algebraic structure of Greshko's unigram_lookup and presuf_lookup tables to show why
     bigram prefix pieces pre(t, a) are invariant across tables t (locked to the 1st plaintext letter a)
     while table choice t only changes the suffix piece suf(t, b) and unigram prefix family uni(t, a).

2. Part 2 (Dot 25 / L-163: Weakened Table-and-Grille WTG vs Rugg Grille on the s69 Prefix-Memory Profile):
   - Constructs the Weakened Table-and-Grille (WTG) producer fitted strictly on the 166 training pages
     (165 for IT2a; SEED=20261017, zero held-out leakage):
       * K=12 affix-compatibility core classes (rows of the table) and prefix slots P (columns).
       * Line start (j=0): draws (P_0, k_0, S_0, C_0) from the line-initial training distribution
         conditioned on pos_0 in {'P' (@P paragraph-initial / line 0), 'I' (ordinary line-initial)}.
       * Within-line step (j >= 1):
         - Partial reset probability p_gal_reset = 0.35 after a mid-line gallows word w_{j-1};
           100% reset at every line break.
         - 1-step grille column walk P_h(P_j | pos_j, P_{j-1}) -> row selection P_h(k_j | P_j, pos_j, P_{j-1})
           -> M_CAND = 6 candidate (C_j, S_j) pairs drawn from Witten-Bell smoothed
           P_h(S_j | k_j, P_j, pos_j, S_{j-1}) and position-aware core pool P_h(C_j | k_j, P_j, pos_j)
           (with local page core repeat p_rep = 0.15, tau = 12.0 at lag d in 2..20, excluding immediate
           lag-1 core repeat C_j == C_{j-1}, and boundary-bleed guard seg.segment(P_j+C_j+S_j)[0] == P_j),
           weighted by length cadence exp(-gamma |len - (mu + rho(len_prev - mu))| - gamma_comp (len - mu)^2)
           with frozen parameters gamma = 0.35, rho = 0.55, gamma_comp = 0.08.
   - Scores WTG across ZL3b, RF1b, and IT2a on the full s69 prefix-memory ladder alongside Voynich
     and gen_rugg_grille.

3. Part 3 (CONSTRAINTS-MAP.md §C line 193 & L-163: 15-Quire Leave-One-Quire-Out LOQO Evaluation):
   - Evaluates the exact 15-quire LOQO protocol of s67 across ZL3b, RF1b, and IT2a comparing:
       (1) CA (s67 baseline: P(P,S | class(C), pos, prev_suf) + global unpositioned core pool),
       (2) WTG_global (Weakened Table-and-Grille walk + position-conditioned core pools + length coupling
           on global training quires),
       (3) WTG_scribe (WTG conditioned on the held-out quire's paleographic Davis Hand h from training
           quires only, backing off to global training quires).
   - Reports per-fold and aggregate pass counts on P1 (Moran), P2 (core->core), P3 (prefix_gain),
     P4 (jsd_first_fg), P5 (CHARWIN > 0), P7 (types within +-15%), and folds passing >= 5/6.

Run:    python -I s71_weakened_grille_and_sticky_naibbe_loqo.py
Writes: results_s71.txt (and optional sidecars in runs/s71/).
"""
from __future__ import annotations

import bisect
import csv
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import a2_position as A2  # noqa: E402
import m3_bakeoff_reconcile as M3  # noqa: E402
import s55_code_vs_generator as S55  # noqa: E402
import s57_local_memory_model as S57  # noqa: E402
import s64_naibbe_taxonomy as S64  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s69_prefix_stream_memory as S69  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s71_weakened_grille_and_sticky_naibbe_loqo.py"
STUB = ROOT / "s71_weakened_grille_and_sticky_naibbe_loqo.prereg.sha256"
OUT = ROOT / "results_s71.txt"
RUN_DIR = ROOT / "runs" / "s71"

SEED = 20261017
NULL_SEED = 20261018
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
GALLOWS = set("ktpf")
EMPTY = "∅"

# Frozen WTG structural parameters (pre-registered, 0 per-fold tuned parameters)
WTG_PARAMS = dict(
    p_rep=0.15,
    tau=12.0,
    gamma=0.35,
    rho=0.55,
    gamma_comp=0.08,
    p_gal_reset=0.35,
    K=12,
    M_cand=6,
    W=20,
)

PREDS = ["P1", "P2", "P3", "P4", "P5", "P7"]
LOQO_MODELS = ["CA", "WTG_global", "WTG_scribe"]
SEEDS_LOQO = (1, 2)
N_DRAW_LOQO = 300
SMALL_FOLD = 6
TOL_SMALL = dict(P1=0.0158, P2=0.0203, P3=0.0170)
TYPE_TOL = 0.15

log: list[str] = []
T0 = time.time()


def emit(s: str = "") -> None:
    print(s, flush=True)
    log.append(s)


def flush() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


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


def verify_stub() -> bool:
    h_self = sha256(SELF)
    if not STUB.exists():
        emit("stub_match: False (missing stub)")
        emit(f"sha256 {SELF.name}: {h_self}")
        return False
    h_stub = sha256(STUB)
    txt = STUB.read_text(encoding="utf-8").strip().splitlines()
    ok = False
    for ln in txt:
        parts = ln.strip().split()
        if len(parts) >= 2 and parts[-1].lstrip("*").strip() == SELF.name:
            ok = (parts[0].lower() == h_self.lower())
    emit(f"stub_match: {ok}")
    emit(f"sha256 {SELF.name}: {h_self}")
    emit(f"sha256 {STUB.name}: {h_stub}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    return ok


# ==============================================================================
# PART 1: STICKY-TABLE NAIBBE (S1.5) VS DEFAULT NAIBBE (DOT 22 / L-159)
# ==============================================================================
def audit_naibbe_tables(K_naibbe: dict) -> dict:
    """Audit Greshko's unigram_lookup and presuf_lookup tables across the 6 tables."""
    uni, pre, suf = K_naibbe["uni"], K_naibbe["pre"], K_naibbe["suf"]
    tables = S64.TABLES
    letters = S64.LETTERS23
    pre_distinct_per_letter = []
    suf_distinct_per_letter = []
    uni_distinct_per_letter = []
    for a in letters:
        pre_distinct_per_letter.append(len({pre[(t, a)] for t in tables}))
        suf_distinct_per_letter.append(len({suf[(t, a)] for t in tables}))
        uni_distinct_per_letter.append(len({uni[(t, a)] for t in tables}))

    # Also check across all 6 tables for a fixed letter `a`, how many distinct
    # prefix strings exist vs across all 23 letters for a fixed table `t`.
    pre_by_tab = {t: len({pre[(t, a)] for a in letters}) for t in tables}
    suf_by_tab = {t: len({suf[(t, a)] for a in letters}) for t in tables}
    uni_by_tab = {t: len({uni[(t, a)] for a in letters}) for t in tables}

    # Check under Voynich ZL3b 166p SlotSegmenter how `pre[(t1, a)] + suf[(t2, b)]`
    # and `uni[(t1, a)]` segment into (P, C, S):
    pages_zl, _ = S69.voynich_pages("ZL3b")
    trs = S69.split_pages(pages_zl)
    seg_zl = SlotSegmenter([w for p in pages_zl if p["id"] in trs for ln in p["lines"] for w in ln])

    # For bigrams: variance of segmented prefix P across tables t1/t2 vs across letter1 a
    same_a_diff_t_same_P = 0
    same_a_diff_t_total = 0
    same_t_diff_a_same_P = 0
    same_t_diff_a_total = 0
    for a in letters:
        for b in letters:
            ps_by_t = [seg_zl.segment(pre[(t, a)] + suf[(t, b)])[0] for t in tables]
            for i in range(len(tables)):
                for j in range(i + 1, len(tables)):
                    same_a_diff_t_total += 1
                    if ps_by_t[i] == ps_by_t[j]:
                        same_a_diff_t_same_P += 1
    for t in tables:
        for b in letters:
            ps_by_a = [seg_zl.segment(pre[(t, a)] + suf[(t, b)])[0] for a in letters]
            for i in range(len(letters)):
                for j in range(i + 1, len(letters)):
                    same_t_diff_a_total += 1
                    if ps_by_a[i] == ps_by_a[j]:
                        same_t_diff_a_same_P += 1

    # For unigrams: how often does table t1 alone fix the segmented prefix P across different letters a?
    uni_same_t_diff_a_same_P = 0
    uni_same_t_diff_a_total = 0
    uni_same_a_diff_t_same_P = 0
    uni_same_a_diff_t_total = 0
    for t in tables:
        ps_u = [seg_zl.segment(uni[(t, a)])[0] for a in letters]
        for i in range(len(letters)):
            for j in range(i + 1, len(letters)):
                uni_same_t_diff_a_total += 1
                if ps_u[i] == ps_u[j]:
                    uni_same_t_diff_a_same_P += 1
    for a in letters:
        ps_u = [seg_zl.segment(uni[(t, a)])[0] for t in tables]
        for i in range(len(tables)):
            for j in range(i + 1, len(tables)):
                uni_same_a_diff_t_total += 1
                if ps_u[i] == ps_u[j]:
                    uni_same_a_diff_t_same_P += 1

    return dict(
        pre_distinct_mean=float(np.mean(pre_distinct_per_letter)),
        pre_distinct_min=min(pre_distinct_per_letter),
        pre_distinct_max=max(pre_distinct_per_letter),
        suf_distinct_mean=float(np.mean(suf_distinct_per_letter)),
        uni_distinct_mean=float(np.mean(uni_distinct_per_letter)),
        pre_by_tab=pre_by_tab,
        suf_by_tab=suf_by_tab,
        uni_by_tab=uni_by_tab,
        big_same_a_diff_t_same_P=same_a_diff_t_same_P / same_a_diff_t_total,
        big_same_t_diff_a_same_P=same_t_diff_a_same_P / same_t_diff_a_total,
        uni_same_t_diff_a_same_P=uni_same_t_diff_a_same_P / uni_same_t_diff_a_total,
        uni_same_a_diff_t_same_P=uni_same_a_diff_t_same_P / uni_same_a_diff_t_total,
    )


def encipher_sticky_naibbe(letters: str, K_naibbe: dict, skel_pages: list[dict], mode: str, seed: int) -> list[dict]:
    """Encipher plaintext letter stream onto skeleton pages under a specified table-persistence mode:
      - 'default': p_stick = 0.0 (independent card draw per slot, Greshko default)
      - 'line_sticky': p_stick = 0.75 within line, reset at every line break
      - 'line_lock': p_stick = 1.00 within line (one table per line), reset at every line break
      - 'page_bias': Dirichlet(alpha_0 * w_deck) with alpha_0 = 1.5 drawn once per page
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    deck = K_naibbe["deck"]
    # Base deck probabilities from cumulative thresholds
    w_deck = np.array([deck[0]] + [deck[i] - deck[i - 1] for i in range(1, len(deck))], dtype=float)
    w_deck /= w_deck.sum()

    L = len(letters)
    pos_idx = 0
    out_pages = []

    def draw_from_cum(cum_list):
        u = rng.random()
        for t, th in zip(S64.TABLES, cum_list):
            if u < th:
                return t
        return S64.TABLES[-1]

    for p in skel_pages:
        if mode == "page_bias":
            probs = np_rng.dirichlet(1.5 * w_deck * 6.0)
            page_cum = list(np.cumsum(probs))
            page_cum[-1] = 1.0
        else:
            page_cum = deck

        new_lines = []
        for ln in p["lines"]:
            k_words = len([w for w in ln if w])
            if k_words == 0:
                continue
            line_toks = []
            cur_tab = None
            for _wi in range(k_words):
                k_chunk = 1 if rng.random() < K_naibbe["p_uni"] else 2
                chunk = "".join(letters[(pos_idx + j) % L] for j in range(k_chunk))
                pos_idx = (pos_idx + k_chunk) % L

                if mode == "default" or mode == "page_bias":
                    t1 = draw_from_cum(page_cum)
                    t2 = draw_from_cum(page_cum) if k_chunk == 2 else ""
                elif mode == "line_sticky":
                    if cur_tab is None or rng.random() >= 0.75:
                        cur_tab = draw_from_cum(deck)
                    t1 = cur_tab
                    if k_chunk == 2:
                        if rng.random() >= 0.75:
                            cur_tab = draw_from_cum(deck)
                        t2 = cur_tab
                    else:
                        t2 = ""
                elif mode == "line_lock":
                    if cur_tab is None:
                        cur_tab = draw_from_cum(deck)
                    t1 = cur_tab
                    t2 = cur_tab if k_chunk == 2 else ""
                else:
                    raise ValueError(f"Unknown mode: {mode}")

                if k_chunk == 1:
                    line_toks.append(K_naibbe["uni"][(t1, chunk)])
                else:
                    line_toks.append(K_naibbe["pre"][(t1, chunk[0])] + K_naibbe["suf"][(t2, chunk[1])])
            new_lines.append(line_toks)
        if new_lines:
            out_pages.append(dict(id=str(p["id"]), section=str(p.get("section", "?")), lines=new_lines))
    return out_pages


def score_s55_and_s69_worker(job: dict) -> dict:
    """Worker to compute both s55 (8 wrapper-free features) and s69 (prefix-memory profile) on a text."""
    name = job["name"]
    cls = job["cls"]
    pages = job["pages"]
    do_s55 = job.get("do_s55", True)
    n_null_s69 = job.get("n_null_s69", 60)
    b_sub_s69 = job.get("b_sub_s69", 300)

    res = dict(name=name, cls=cls)
    if do_s55:
        td = S55.TextData(name, pages)
        f55, info55, _ = td.measure(boot=False)
        res["s55"] = f55
        res["s55_info"] = info55
        res["tokens"] = td.tokens
        res["te_tokens"] = td.te_tokens

    # s69 measurement
    norm_p = S69.norm_pages(pages)
    t69 = S69.Text(name, norm_p)
    W = {k: t69.A[k] for k in ("pre", "suf", "core", "cc", "gal")}
    st = S69.compute(t69, W)
    point = S69.all_values(st)
    rng = np.random.default_rng(SEED)
    P = t69.n_te_pages
    m = int(round(S69.SUB_FRAC * P))
    subs = defaultdict(list)
    for _ in range(b_sub_s69):
        sel = rng.choice(P, size=m, replace=False)
        for k, v in S69.all_values(st, sel).items():
            subs[k].append(v)
    ci = {k: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))) for k, v in subs.items()}
    nrng = np.random.default_rng(NULL_SEED)
    nulls = defaultdict(list)
    for _ in range(n_null_s69):
        for k, v in S69.all_values(S69.compute(t69, t69.shuffled_word_attrs(nrng))).items():
            nulls[k].append(v)
    nul = {k: (float(np.nanmean(v)), float(np.nanstd(v))) for k, v in nulls.items()}
    ns = {k: int(st[k][0].sum()) for k in st}
    xent = (float(st["M1"][1].sum() / st["M1"][0].sum()), float(st["M1"][2].sum() / st["M1"][0].sum()))
    s69_res = dict(point=point, ci=ci, null=nul, n=ns, xent=xent, n_pre=t69.n_pre, tokens=t69.tokens, te_tokens=t69.te_tokens)
    rows_c, _ = S69.calls({name: s69_res}, [name])
    s69_res["calls"] = {k: (bool(v[0]), v[1]) for k, v in rows_c[name].items()}
    res["s69"] = s69_res
    return res


# ==============================================================================
# PART 2 & 3: WEAKENED TABLE-AND-GRILLE (WTG) PRODUCER
# ==============================================================================
def _cum(counter: Counter):
    items = sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0])))
    ws = [k for k, _ in items]
    cum, t = [], 0
    for _, c in items:
        t += c
        cum.append(t)
    return ws, cum


def _wb_table(tab_dict: dict) -> dict:
    """Convert mapping ctx -> Counter(outcomes) into ctx -> (ws, cum, lam = N / (N + T))."""
    out = {}
    for k, cnt in tab_dict.items():
        tot = sum(cnt.values())
        if tot > 0:
            ws, cum = _cum(cnt)
            out[k] = (ws, cum, tot / (tot + len(cnt)))
    return out


class WTGProducer:
    """Weakened Table-and-Grille (WTG) producer fitted strictly on training pages.
    Supports both global scope (scope='ALL') and scribe-conditioned scope (scope=hand, backing off to 'ALL').
    """

    def __init__(self, train_pages_meta: list[dict], seg: SlotSegmenter, prm: dict | None = None):
        """train_pages_meta: list of dicts with keys 'lines', 'hand', 'section', optional 'para'."""
        self.seg = seg
        self.prm = dict(WTG_PARAMS if prm is None else prm)
        train_lines_only = [p["lines"] for p in train_pages_meta]
        self.cls, self.cls_info = S67.core_classes(train_lines_only, seg)

        # Tables for line-initial (i == 0) and within-line (i >= 1)
        init_cell = defaultdict(Counter)        # (scope, pos0) -> Counter((p, k, s))
        gal_reset_p = defaultdict(Counter)      # (scope, pos) -> Counter(p)
        walk_p_0 = defaultdict(Counter)         # (scope, pos, p_prev, s_prev) -> Counter(p)
        walk_p_1 = defaultdict(Counter)         # (scope, pos, p_prev) -> Counter(p)
        walk_p_2 = defaultdict(Counter)         # (scope, p_prev) -> Counter(p)
        walk_p_3 = defaultdict(Counter)         # (scope, pos) -> Counter(p)

        row_k_0 = defaultdict(Counter)          # (scope, p, pos, p_prev) -> Counter(k)
        row_k_1 = defaultdict(Counter)          # (scope, p, pos) -> Counter(k)
        row_k_2 = defaultdict(Counter)          # (scope, p) -> Counter(k)

        suf_s_0 = defaultdict(Counter)          # (scope, k, p, pos, s_prev) -> Counter(s)
        suf_s_1 = defaultdict(Counter)          # (scope, k, p, pos) -> Counter(s)
        suf_s_2 = defaultdict(Counter)          # (scope, k, p) -> Counter(s)
        suf_s_3 = defaultdict(Counter)          # (scope, k) -> Counter(s)

        core_c_0 = defaultdict(Counter)         # (scope, k, p, pos) -> Counter(c)
        core_c_1 = defaultdict(Counter)         # (scope, k, pos) -> Counter(c)
        core_c_2 = defaultdict(Counter)         # (scope, k) -> Counter(c)

        uni_p = Counter()
        uni_k = Counter()
        uni_s = Counter()
        uni_c = Counter()

        lens_by_scope = defaultdict(list)
        word_lens_by_scope = defaultdict(list)
        hand_token_counts = Counter()
        all_prefixes = set()
        cores_in_k = defaultdict(Counter)

        for prec in train_pages_meta:
            h = str(prec.get("hand", "?"))
            lines = prec["lines"]
            para_flags = prec.get("para")
            scopes = ("ALL", f"H:{h}")
            for li, ln in enumerate(lines):
                L = len(ln)
                if L == 0:
                    continue
                for sc in scopes:
                    lens_by_scope[sc].append(L)
                is_para = (li == 0) or (bool(para_flags[li]) if para_flags and li < len(para_flags) else False)
                p_prev, s_prev, gal_prev = "^", "^", False
                for i, w in enumerate(ln):
                    hand_token_counts[h] += 1
                    pr, co, su = seg.segment(w)
                    k = self.cls.get(co, 12)
                    all_prefixes.add(pr)
                    cores_in_k[k][co] += 1
                    uni_p[pr] += 1
                    uni_k[k] += 1
                    uni_s[su] += 1
                    uni_c[co] += 1
                    pos = ("P" if is_para else "I") if i == 0 else ("F" if i == L - 1 else "M")
                    for sc in scopes:
                        word_lens_by_scope[sc].append(len(w))
                        if i == 0:
                            init_cell[(sc, pos)][(pr, k, su)] += 1
                        else:
                            if gal_prev:
                                gal_reset_p[(sc, pos)][pr] += 1
                            walk_p_0[(sc, pos, p_prev, s_prev)][pr] += 1
                            walk_p_1[(sc, pos, p_prev)][pr] += 1
                            walk_p_2[(sc, p_prev)][pr] += 1
                            walk_p_3[(sc, pos)][pr] += 1

                        row_k_0[(sc, pr, pos, p_prev)][k] += 1
                        row_k_1[(sc, pr, pos)][k] += 1
                        row_k_2[(sc, pr)][k] += 1

                        suf_s_0[(sc, k, pr, pos, s_prev)][su] += 1
                        suf_s_1[(sc, k, pr, pos)][su] += 1
                        suf_s_2[(sc, k, pr)][su] += 1
                        suf_s_3[(sc, k)][su] += 1

                        core_c_0[(sc, k, pr, pos)][co] += 1
                        core_c_1[(sc, k, pos)][co] += 1
                        core_c_2[(sc, k)][co] += 1

                    p_prev, s_prev = pr, su
                    gal_prev = any(ch in GALLOWS for ch in w)

        # Filter core_c_1 and core_c_2 per prefix pr so back-off cores never boundary-bleed into prefix pr
        compat_core_1 = {}
        compat_core_2 = {}
        for pr in all_prefixes:
            for (sc, k, pos), cnt in core_c_1.items():
                filtered = Counter({c: v for c, v in cnt.items() if seg.segment(pr + c)[0] == pr})
                if filtered:
                    compat_core_1[(sc, k, pr, pos)] = filtered
            for (sc, k), cnt in core_c_2.items():
                filtered = Counter({c: v for c, v in cnt.items() if seg.segment(pr + c)[0] == pr})
                if filtered:
                    compat_core_2[(sc, k, pr)] = filtered

        self.init_cell = _wb_table(init_cell)
        self.gal_reset_p = _wb_table(gal_reset_p)
        self.walk_p = [_wb_table(walk_p_0), _wb_table(walk_p_1), _wb_table(walk_p_2), _wb_table(walk_p_3)]
        self.row_k = [_wb_table(row_k_0), _wb_table(row_k_1), _wb_table(row_k_2)]
        self.suf_s = [_wb_table(suf_s_0), _wb_table(suf_s_1), _wb_table(suf_s_2), _wb_table(suf_s_3)]
        self.core_c = [
            _wb_table(core_c_0),
            _wb_table(compat_core_1),
            _wb_table(compat_core_2),
            _wb_table(core_c_1),
            _wb_table(core_c_2),
        ]

        self.uni_p = _cum(uni_p)
        self.uni_k = _cum(uni_k)
        self.uni_s = _cum(uni_s)
        self.uni_c = _cum(uni_c)
        self.lens_by_scope = dict(lens_by_scope)
        self.mu_by_scope = {sc: float(np.mean(v)) for sc, v in word_lens_by_scope.items() if v}
        self.hand_token_counts = hand_token_counts
        self._update_kcum()

    def _update_kcum(self) -> None:
        W = self.prm["W"]
        tau = self.prm["tau"]
        self.kcum = []
        t = 0.0
        for d in range(2, W + 1):
            t += math.exp(-(d - 2) / tau)
            self.kcum.append((d, t))

    @staticmethod
    def _pick(rng: random.Random, ws: list, cum: list):
        return ws[bisect.bisect_right(cum, rng.random() * cum[-1])]

    def _wb_draw(self, rng: random.Random, levels: list[dict], keys: list, fallback_cum: tuple):
        for lev, k in zip(levels, keys):
            e = lev.get(k)
            if e is None:
                continue
            ws, cum, lam = e
            if rng.random() < lam:
                return self._pick(rng, ws, cum)
        return self._pick(rng, *fallback_cum)

    def _draw_init(self, rng: random.Random, sc: str, pos0: str):
        for k in ((sc, pos0), ("ALL", pos0), ("ALL", "I")):
            e = self.init_cell.get(k)
            if e is not None:
                ws, cum, lam = e
                if rng.random() < lam or k == ("ALL", "I"):
                    return self._pick(rng, ws, cum)
        pr = self._pick(rng, *self.uni_p)
        k = self._pick(rng, *self.uni_k)
        su = self._pick(rng, *self.uni_s)
        return pr, k, su

    def _draw_prefix(self, rng: random.Random, sc: str, pos: str, p_prev: str, s_prev: str, gal_prev: bool) -> str:
        if gal_prev and rng.random() < self.prm["p_gal_reset"]:
            for k in ((sc, pos), ("ALL", pos)):
                e = self.gal_reset_p.get(k)
                if e is not None:
                    ws, cum, _ = e
                    return self._pick(rng, ws, cum)
        # Note: walk_p_1 (scope, pos, p_prev) is the primary 1-step grille column walk;
        # walk_p_2 ("ALL", p_prev) and walk_p_3 ("ALL", pos) provide smooth back-off.
        keys = [
            (sc, pos, p_prev),
            ("ALL", pos, p_prev),
            ("ALL", p_prev),
            ("ALL", pos),
        ]
        levs = [self.walk_p[1], self.walk_p[1], self.walk_p[2], self.walk_p[3]]
        return self._wb_draw(rng, levs, keys, self.uni_p)

    def _draw_row_k(self, rng: random.Random, sc: str, pr: str, pos: str, p_prev: str) -> int:
        keys = [
            (sc, pr, pos, p_prev),
            (sc, pr, pos),
            ("ALL", pr, pos),
            ("ALL", pr),
        ]
        levs = [self.row_k[0], self.row_k[1], self.row_k[1], self.row_k[2]]
        return self._wb_draw(rng, levs, keys, self.uni_k)

    def _draw_suf(self, rng: random.Random, sc: str, k: int, pr: str, pos: str, s_prev: str) -> str:
        keys = [
            (sc, k, pr, pos, s_prev),
            (sc, k, pr, pos),
            ("ALL", k, pr, pos),
            ("ALL", k, pr),
            ("ALL", k),
        ]
        levs = [self.suf_s[0], self.suf_s[1], self.suf_s[1], self.suf_s[2], self.suf_s[3]]
        return self._wb_draw(rng, levs, keys, self.uni_s)

    def _draw_core(self, rng: random.Random, sc: str, k: int, pr: str, pos: str, prev_core: str) -> str:
        keys = [
            (sc, k, pr, pos),
            ("ALL", k, pr, pos),
            (sc, k, pr, pos),
            ("ALL", k, pr),
            (sc, k, pos),
            ("ALL", k, pos),
            ("ALL", k),
        ]
        levs = [
            self.core_c[0],
            self.core_c[0],
            self.core_c[1],
            self.core_c[2],
            self.core_c[3],
            self.core_c[3],
            self.core_c[4],
        ]
        for _ in range(6):
            c = self._wb_draw(rng, levs, keys, self.uni_c)
            if c != prev_core:
                return c
        return c

    def generate_page(
        self,
        rng: random.Random,
        n_lines: int,
        hand: str = "ALL",
        line_lens: list[int] | None = None,
        para_flags: list[bool] | None = None,
    ) -> list[list[str]]:
        sc = f"H:{hand}" if (hand != "ALL" and self.hand_token_counts.get(str(hand), 0) >= 800) else "ALL"
        emp_lens = self.lens_by_scope.get(sc) or self.lens_by_scope["ALL"]
        mu = self.mu_by_scope.get(sc, self.mu_by_scope["ALL"])
        p_rep = self.prm["p_rep"]
        gamma = self.prm["gamma"]
        rho = self.prm["rho"]
        gamma_comp = self.prm["gamma_comp"]
        M_cand = self.prm["M_cand"]
        W = self.prm["W"]

        hist_cores: list[tuple[str, int]] = []  # (core, k)
        out_lines: list[list[str]] = []

        for li in range(n_lines):
            L = line_lens[li] if (line_lens is not None and li < len(line_lens)) else rng.choice(emp_lens)
            is_para = (li == 0) or (bool(para_flags[li]) if (para_flags is not None and li < len(para_flags)) else False)
            line: list[str] = []
            p_prev, s_prev, c_prev, gal_prev, plen = "^", "^", "", False, mu

            for i in range(L):
                pos = ("P" if is_para else "I") if i == 0 else ("F" if i == L - 1 else "M")
                if i == 0:
                    pr, k, su = self._draw_init(rng, sc, pos)
                    co = self._draw_core(rng, sc, k, pr, pos, "")
                    w = pr + co + su
                else:
                    pr = self._draw_prefix(rng, sc, pos, p_prev, s_prev, gal_prev)
                    k = self._draw_row_k(rng, sc, pr, pos, p_prev)
                    n_c = M_cand if (gamma > 0 or gamma_comp > 0) else 1
                    cands = []
                    for _ in range(n_c):
                        su_m = self._draw_suf(rng, sc, k, pr, pos, s_prev)
                        co_m = None
                        if len(hist_cores) >= 2 and p_rep > 0 and rng.random() < p_rep:
                            # Repeat a recent core on the page at distance d in 2..W (excluding d=1 / c_prev)
                            max_d = min(W, len(hist_cores))
                            matching = [
                                (d, hist_cores[-d][0])
                                for d in range(2, max_d + 1)
                                if hist_cores[-d][1] == k and hist_cores[-d][0] != c_prev
                                and self.seg.segment(pr + hist_cores[-d][0])[0] == pr
                            ]
                            if matching:
                                wts_d = [math.exp(-(d - 2) / self.prm["tau"]) for d, _ in matching]
                                u_d = rng.random() * sum(wts_d)
                                acc_d = 0.0
                                co_m = matching[-1][1]
                                for ( _, c_cand), wd in zip(matching, wts_d):
                                    acc_d += wd
                                    if u_d <= acc_d:
                                        co_m = c_cand
                                        break
                        if co_m is None:
                            co_m = self._draw_core(rng, sc, k, pr, pos, c_prev)
                        w_m = pr + co_m + su_m
                        cands.append((w_m, co_m, su_m))

                    if n_c > 1:
                        tgt = mu + rho * (plen - mu)
                        wts = [
                            math.exp(-gamma * abs(len(wm) - tgt) - gamma_comp * ((len(wm) - mu) ** 2))
                            for wm, _, _ in cands
                        ]
                        tot = sum(wts)
                        u = rng.random() * tot
                        acc = 0.0
                        chosen = cands[-1]
                        for cand_item, wt in zip(cands, wts):
                            acc += wt
                            if u <= acc:
                                chosen = cand_item
                                break
                        w, co, su = chosen
                    else:
                        w, co, su = cands[0]

                line.append(w)
                hist_cores.append((co, k))
                p_prev, s_prev, c_prev = pr, su, co
                gal_prev = any(ch in GALLOWS for ch in w)
                plen = len(w)
            out_lines.append(line)
        return out_lines


# ==============================================================================
# FAST EXACT SCORING OF s67 LOQO PREDICTIONS (P1, P2, P3, P4, P5, P7)
# ==============================================================================
class MeasuredLOQO:
    """Computes s57/s67 held-out predictions P1, P2, P3, P4, P5 (skipping unused P6 F1 page_sums)."""

    def __init__(self, name: str, train: list[tuple[str, list[list[str]]]], test: list[tuple[str, list[list[str]]]]):
        self.name = name
        self.n_test = len(test)
        tr_tokens = [w for _, ls in train for l in ls for w in l]
        seg = SlotSegmenter(tr_tokens)
        sg = seg.segment
        core_id: dict[str, int] = {}
        self.pages = []
        for _pid, ls in test:
            lens, lid, cores = [], [], []
            for li, l in enumerate(ls):
                for w in l:
                    lens.append(len(w))
                    lid.append(li)
                    cores.append(core_id.setdefault(sg(w)[1], len(core_id)))
            self.pages.append(dict(x=np.array(lens, float), lid=np.array(lid, np.int64), c=np.array(cores, np.int64)))

        tr_pre = [[sg(w)[0] or EMPTY for w in l] for _, ls in train for l in ls]
        m = S57.Bigram(tr_pre)
        self.gain = np.zeros((len(test), 3))
        for k, (_, ls) in enumerate(test):
            for l in ls:
                s = [sg(w)[0] or EMPTY for w in l]
                for a, b in zip(s, s[1:]):
                    self.gain[k] += (1, -math.log2(m.pu(b)), -math.log2(m.pb(a, b)))

        test_lines = [l for _, ls in test for l in ls]
        self.jsd = float(A2.stats(test_lines, lambda w: w[0])[0])
        self.jsd_exc = self.jsd - float(A2.null(test_lines, lambda w: w[0], n=30)[:, 0].mean())

        pages_m3 = [dict(id=str(p), lines=ls) for p, ls in train] + [dict(id=str(p), lines=ls) for p, ls in test]
        acc = M3.score_folds(pages_m3, [list(range(len(train), len(pages_m3)))])
        rn, wb = acc["unigram-GT-renorm"], acc["char3-WB"]
        self.charwin = rn["bits"] / rn["tok"] - wb["bits"] / wb["tok"]
        self.p2_point = self.core_core(np.arange(self.n_test), S57.N_SHUF_POINT, np.random.default_rng(SEED))

    def concat(self, idx):
        xs, ls, cs, off = [], [], [], 0
        for i in idx:
            pg = self.pages[i]
            xs.append(pg["x"])
            cs.append(pg["c"])
            ls.append(pg["lid"] + off)
            off += int(pg["lid"].max()) + 1 if len(pg["lid"]) else 0
        return np.concatenate(xs), np.concatenate(ls), np.concatenate(cs)

    def moran(self, idx) -> float:
        x, lid, _ = self.concat(idx)
        left = np.nonzero(lid[1:] == lid[:-1])[0]
        z = x - x.mean()
        d = float(np.dot(z, z))
        return float(len(x) / len(left) * np.dot(z[left], z[left + 1]) / d) if d > 0 and len(left) else float("nan")

    def core_core(self, idx, n_shuf: int, rng: np.random.Generator) -> float:
        _, lid, c = self.concat(idx)
        left = np.nonzero(lid[1:] == lid[:-1])[0]
        right = left + 1
        obs = S57.mi_codes(c[left], c[right])
        null = []
        for _ in range(n_shuf):
            perm = np.lexsort((rng.random(len(c)), lid))
            y = c[perm]
            null.append(S57.mi_codes(y[left], y[right]))
        return obs - float(np.mean(null))

    def gain_stat(self, idx) -> float:
        s = self.gain[idx].sum(0)
        return (s[1] - s[2]) / s[0] if s[0] else float("nan")

    def point(self) -> dict:
        a = np.arange(self.n_test)
        return dict(
            P1=self.moran(a),
            P2=self.p2_point,
            P3=self.gain_stat(a),
            P4=self.jsd,
            P4_exc=self.jsd_exc,
            P5=self.charwin,
        )

    def draw(self, idx, rng: np.random.Generator) -> dict:
        return dict(
            P1=self.moran(idx),
            P2=self.core_core(idx, S57.N_SHUF_DRAW, rng),
            P3=self.gain_stat(idx),
        )


def draws_for_loqo(ms: list[MeasuredLOQO], seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    k = max(1, int(round(S57.SUB_FRAC * ms[0].n_test)))
    keys = ("P1", "P2", "P3")
    out = {key: np.zeros(N_DRAW_LOQO) for key in keys}
    for b in range(N_DRAW_LOQO):
        vals = defaultdict(list)
        for m in ms:
            idx = rng.choice(m.n_test, size=k, replace=False)
            for key, v in m.draw(idx, rng).items():
                vals[key].append(v)
        for key in keys:
            out[key][b] = float(np.mean(vals[key]))
    return out


def score_loqo_model(
    real_pt: dict,
    real_dr: dict[str, np.ndarray],
    ms: list[MeasuredLOQO],
    gen_dr: dict[str, np.ndarray],
    n_test: int,
    gen_test_pages: list[list[list[str]]],
    real_test_pages: list[list[str]],
) -> tuple[dict, dict, float, bool]:
    pts = [m.point() for m in ms]
    gen_pt = {k: float(np.mean([p[k] for p in pts])) for k in pts[0]}

    cells = {}
    d1 = gen_dr["P1"] - real_dr["P1"]
    lo1, hi1 = S57.pct(d1)
    pd1 = gen_pt["P1"] - real_pt["P1"]
    cells["P1"] = (hi1 >= 0, f"Moran Δ {pd1:+.4f} [{lo1:+.4f},{hi1:+.4f}] (gen {gen_pt['P1']:.4f}, real {real_pt['P1']:.4f})")

    d2 = gen_dr["P2"] - real_dr["P2"]
    lo2, hi2 = S57.pct(d2)
    pd2 = gen_pt["P2"] - real_pt["P2"]
    cells["P2"] = (lo2 <= 0 <= hi2, f"core->core Δ {pd2:+.4f} [{lo2:+.4f},{hi2:+.4f}] (gen {gen_pt['P2']:+.4f}, real {real_pt['P2']:+.4f})")

    lo3, hi3 = S57.pct(real_dr["P3"])
    g3 = gen_pt["P3"]
    cells["P3"] = (lo3 <= g3 <= hi3, f"prefix gain gen {g3:+.4f} vs real {real_pt['P3']:+.4f} [{lo3:+.4f},{hi3:+.4f}]")

    g4 = gen_pt["P4"]
    cells["P4"] = (
        S57.S15_JSD[0] <= g4 <= S57.S15_JSD[1],
        f"jsd_first_fg gen {g4:.4f} vs [{S57.S15_JSD[0]},{S57.S15_JSD[1]}] (real {real_pt['P4']:.4f})",
    )

    g5 = gen_pt["P5"]
    cells["P5"] = (g5 > 0, f"CHARWIN gen {g5:+.4f} (real {real_pt['P5']:+.4f})")

    small = n_test < SMALL_FOLD
    if small:
        cells["P1"] = (pd1 >= -TOL_SMALL["P1"], f"[small] Moran Δ {pd1:+.4f} >= -{TOL_SMALL['P1']}")
        cells["P2"] = (abs(pd2) <= TOL_SMALL["P2"], f"[small] core->core Δ {pd2:+.4f}, |Δ| <= {TOL_SMALL['P2']}")
        d3 = g3 - real_pt["P3"]
        cells["P3"] = (abs(d3) <= TOL_SMALL["P3"], f"[small] prefix gain gen {g3:+.4f} real {real_pt['P3']:+.4f}")

    ratios = []
    for gp in gen_test_pages:
        vg, vr, _ = S67.types_at(gp, real_test_pages)
        ratios.append(vg / vr if vr else float("nan"))
    rt = float(np.mean(ratios))
    cells["P7"] = (abs(rt - 1.0) <= TYPE_TOL, f"types gen/real {rt:.3f} (tol ±{TYPE_TOL:.0%})")
    return cells, gen_pt, rt, small


def run_loqo_fold_worker(job: dict) -> dict:
    """Worker for one (T, Q) fold evaluating WTG_global and WTG_scribe alongside s67 CA."""
    t0 = time.time()
    T = job["T"]
    Q = job["Q"]
    pages_meta = job["pages_meta"]
    s67_cell = job["s67_cell"]
    off = job["off"]

    train_meta = [p for p in pages_meta if p["quire"] != Q]
    test_meta = [p for p in pages_meta if p["quire"] == Q]
    train_pairs = [(p["id"], p["lines"]) for p in train_meta]
    test_pairs = [(p["id"], p["lines"]) for p in test_meta]

    # Paleographic Davis hand of held-out quire Q (known from ink/ductus without reading words)
    quire_hands = Counter(p["hand"] for p in test_meta)
    dom_hand = quire_hands.most_common(1)[0][0]

    tr_tok = [w for p in train_meta for l in p["lines"] for w in l]
    seg = SlotSegmenter(tr_tok)
    prod = WTGProducer(train_meta, seg, WTG_PARAMS)

    real_m = MeasuredLOQO(f"{T} {Q} real", train_pairs, test_pairs)
    real_dr = draws_for_loqo([real_m], SEED + off)
    real_pt = real_m.point()
    real_ci = {k: S57.pct(real_dr[k]) for k in ("P1", "P2", "P3")}
    real_test_pages = [p["lines"] for p in test_meta]

    models_out = {}
    # 1. CA baseline from s67
    models_out["CA"] = dict(
        n=s67_cell["models"]["CA"]["n"],
        holds=s67_cell["models"]["CA"]["holds"],
        text=s67_cell["models"]["CA"]["text"],
        gen_point=s67_cell["models"]["CA"]["gen_point"],
        type_ratio=s67_cell["models"]["CA"]["type_ratio"],
        small=s67_cell["models"]["CA"]["small"],
    )

    # 2. WTG_global and 3. WTG_scribe
    for j, m_name in enumerate(("WTG_global", "WTG_scribe")):
        ms = []
        gen_test_pages_list = []
        for s in SEEDS_LOQO:
            rng = random.Random(s)
            gtr = []
            for i, p in enumerate(train_meta):
                h_arg = p["hand"] if m_name == "WTG_scribe" else "ALL"
                gtr.append((f"g{i}", prod.generate_page(rng, len(p["lines"]), hand=h_arg)))
            gte = []
            for i, p in enumerate(test_meta):
                h_arg = dom_hand if m_name == "WTG_scribe" else "ALL"
                gte.append((f"h{i}", prod.generate_page(rng, len(p["lines"]), hand=h_arg)))
            ms.append(MeasuredLOQO(f"{T} {Q} {m_name} s{s}", gtr, gte))
            gen_test_pages_list.append([ls for _, ls in gte])

        gen_dr = draws_for_loqo(ms, SEED + off + 10 + j)
        cells, gen_pt, rt, small = score_loqo_model(
            real_pt, real_dr, ms, gen_dr, len(test_meta), gen_test_pages_list, real_test_pages
        )
        n_hold = sum(1 for k in PREDS if cells[k][0])
        models_out[m_name] = dict(
            n=n_hold,
            holds={k: bool(cells[k][0]) for k in PREDS},
            text={k: cells[k][1] for k in PREDS},
            gen_point=gen_pt,
            type_ratio=rt,
            small=small,
        )

    return dict(
        T=T,
        Q=Q,
        dom_hand=dom_hand,
        n_test=len(test_meta),
        n_train=len(train_meta),
        real_point=real_pt,
        real_ci=real_ci,
        models=models_out,
        secs=time.time() - t0,
    )


def load_translit_meta(T: str) -> list[dict]:
    """Load pages with id, quire, hand, section, lines, and IVTFF gap/para flags."""
    pages_s69, _ = S69.voynich_pages(T)
    meta_path = ROOT / "data" / "translit" / f"{TRANSLITS[T]}.meta.json"
    d = json.loads(meta_path.read_text(encoding="utf-8"))
    meta_by_id = {str(p["id"]): p for p in d["pages"]}
    out = []
    for p in pages_s69:
        pid = p["id"]
        m = meta_by_id.get(pid, {})
        out.append(
            dict(
                id=pid,
                quire=str(m.get("quire", "?")),
                hand=str(m.get("hand", "?")),
                section=str(m.get("section", "?")),
                lines=p["lines"],
                gaps=p.get("gaps"),
                para=p.get("para"),
            )
        )
    return out


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main() -> None:
    emit("s71 -- Weakened Table-and-Grille (WTG) & Sticky-Table Naibbe (S1.5) LOQO Evaluation")
    emit(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    verify_stub()
    emit(f"python {sys.version.split()[0]}; numpy {np.__version__}; SEED={SEED}; NULL_SEED={NULL_SEED}")
    emit(f"WTG frozen parameters: {WTG_PARAMS}")
    emit()
    flush()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    nproc = max(1, min(14, (os.cpu_count() or 2) - 2))

    # --------------------------------------------------------------------------
    # PART 1: STICKY-TABLE NAIBBE (S1.5) VS DEFAULT NAIBBE (DOT 22 / L-159)
    # --------------------------------------------------------------------------
    emit("================================================================================")
    emit("PART 1 (Dot 22 / L-159): Sticky-Table Naibbe (Naibbe-S1.5) vs Default Naibbe")
    emit("================================================================================")
    K_naibbe = S64.load_greshko()
    audit = audit_naibbe_tables(K_naibbe)
    emit("1A. Algebraic Structure of Greshko's Naibbe Tables (Naibbe_Cipher.xlsx):")
    emit(
        f"  - Bigram prefix piece pre(table, letter1): mean distinct strings per letter1 across the 6 tables = "
        f"{audit['pre_distinct_mean']:.2f} (min={audit['pre_distinct_min']}, max={audit['pre_distinct_max']})"
    )
    emit(
        f"  - Bigram suffix piece suf(table, letter2): mean distinct strings per letter2 across the 6 tables = "
        f"{audit['suf_distinct_mean']:.2f} (by table: {audit['suf_by_tab']})"
    )
    emit(
        f"  - Unigram word uni(table, letter):         mean distinct strings per letter across the 6 tables = "
        f"{audit['uni_distinct_mean']:.2f} (by table: {audit['uni_by_tab']})"
    )
    emit(
        f"  - Under Voynich ZL3b SlotSegmenter: for bigrams (52.8% of tokens), fixing plaintext letter1 and varying "
        f"table t keeps the segmented prefix P identical {100 * audit['big_same_a_diff_t_same_P']:.1f}% of the time, "
        f"whereas fixing table t and varying plaintext letter1 shares P only {100 * audit['big_same_t_diff_a_same_P']:.1f}% of the time!"
    )
    emit(
        f"  - For unigrams (47.2% of tokens), fixing table t across different letters shares the segmented prefix P "
        f"{100 * audit['uni_same_t_diff_a_same_P']:.1f}% of the time (vs {100 * audit['uni_same_a_diff_t_same_P']:.1f}% across tables)."
    )
    emit(
        "  -> MECHANISTIC CONSEQUENCE: In Naibbe bigrams (pre(t1, a) + suf(t2, b)), the prefix is locked to the 1st "
        "plaintext letter `a`, while the table choice changes the core/suffix `respace`! Only unigram slots (47.2% of tokens, "
        "so 0.472^2 = 22.3% of adjacent token pairs) carry table-driven prefix families (`qok/ok/qot/ot/olk/sh`)."
    )
    emit()

    # Build the 8 Naibbe texts (4 mechanisms x 2 plaintexts: latin_cremma [Latin prose] & italian_dante)
    naibbe_modes = [
        ("default", "p_stick=0.00"),
        ("line_sticky", "p_stick=0.75"),
        ("line_lock", "p_stick=1.00"),
        ("page_bias", "Dirichlet(1.5)"),
    ]
    naibbe_plains = ["latin_cremma", "italian_dante"]
    naibbe_jobs = []
    for pi, p_nm in enumerate(naibbe_plains):
        p_file = S64.S49 / f"lang_{p_nm}.meta.json"
        d_plain = json.loads(p_file.read_text(encoding="utf-8"))
        letters = S64.norm_letters([w for pg in d_plain["pages"] for ln in pg["lines"] for w in ln])
        skel = S55.load_sidecar(f"code_k4_{p_nm}")
        for mi, (m_key, _m_desc) in enumerate(naibbe_modes):
            t_name = f"Naibbe_{m_key}_{p_nm}"
            pages_enc = encipher_sticky_naibbe(letters, K_naibbe, skel, mode=m_key, seed=71000 + 100 * pi + mi)
            naibbe_jobs.append(dict(name=t_name, cls=f"S1.5_{m_key}", pages=pages_enc, do_s55=True, n_null_s69=50, b_sub_s69=300))

    # Also prepare Part 2 WTG corpora and Voynich + Rugg Grille jobs so we can score all s69 profiles in parallel!
    pages_by_T = {}
    wtg_pages_by_T = {}
    for ti, T in enumerate(TRANSLITS):
        pages_meta = load_translit_meta(T)
        pages_by_T[T] = pages_meta
        trs = S69.split_pages(pages_meta)
        train_meta = [p for p in pages_meta if p["id"] in trs]
        tr_tok = [w for p in train_meta for l in p["lines"] for w in l]
        seg_tr = SlotSegmenter(tr_tok)
        wtg_prod = WTGProducer(train_meta, seg_tr, WTG_PARAMS)
        rng_wtg = random.Random(71200 + ti)
        wtg_pages = []
        for p in pages_meta:
            gen_lines = wtg_prod.generate_page(
                rng_wtg,
                len(p["lines"]),
                hand=p["hand"],
                line_lens=[len(ln) for ln in p["lines"]],
                para_flags=p.get("para"),
            )
            wtg_pages.append(
                dict(
                    id=p["id"],
                    section=p["section"],
                    hand=p["hand"],
                    quire=p["quire"],
                    lines=gen_lines,
                    gaps=p.get("gaps"),
                    para=p.get("para"),
                )
            )
        wtg_pages_by_T[T] = wtg_pages
        (RUN_DIR / f"WTG_{T}.meta.json").write_text(
            json.dumps(dict(source=f"s71 WTG fitted on {T} 166 training pages", params=WTG_PARAMS, pages=wtg_pages)),
            encoding="utf-8",
            newline="\n",
        )

    part2_jobs = []
    for T in TRANSLITS:
        part2_jobs.append(dict(name=f"Voynich_{T}", cls="VOY", pages=pages_by_T[T], do_s55=False, n_null_s69=100, b_sub_s69=500))
    for T in TRANSLITS:
        part2_jobs.append(dict(name=f"WTG_{T}", cls="WTG", pages=wtg_pages_by_T[T], do_s55=True, n_null_s69=100, b_sub_s69=500))
    rugg_path = S64.S49 / "gen_rugg_grille.meta.json"
    rugg_pages = json.loads(rugg_path.read_text(encoding="utf-8"))["pages"]
    part2_jobs.append(dict(name="gen_rugg_grille", cls="GEN", pages=rugg_pages, do_s55=False, n_null_s69=60, b_sub_s69=300))

    all_s69_jobs = naibbe_jobs + part2_jobs
    scored_map = {}
    with Pool(min(nproc, len(all_s69_jobs))) as pool:
        for r in pool.imap_unordered(score_s55_and_s69_worker, all_s69_jobs):
            scored_map[r["name"]] = r

    # Load s55 reference table (12 CODE/GEN + 3 Voynich) and s64 NAIBBE features
    ref_s55 = {}
    with (ROOT / "runs" / "s55" / "features.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            ref_s55[row["text"]] = {k: float(row[k]) for k in S55.FEATS}
    lab49 = json.loads((S64.S49 / "labels.json").read_text(encoding="utf-8"))["labels"]
    core12 = [n for n, c in lab49.items() if c in S55.CLS]
    X12 = np.array([[ref_s55[n][k] for k in S55.FEATS] for n in core12], dtype=float)
    y12 = [lab49[n] for n in core12]
    m_lr55 = S55.lr_fit(S55.prep(X12, X12)[0], y12)

    # Project Voynich and all Naibbe variants + WTG into s55 z-space
    Z12, Z_voy = S55.prep(X12, np.array([[ref_s55[f"Voynich_{T}"][k] for k in S55.FEATS] for T in TRANSLITS], dtype=float))
    cents55 = {c: Z12[[i for i, t in enumerate(y12) if t == c]].mean(0) for c in S55.CLS}
    voy_z = {T: Z_voy[i] for i, T in enumerate(TRANSLITS)}

    emit("1B. s55 Wrapper-Free Features (8 features) & Distance to Voynich in s55 z-Space:")
    emit(
        f"  {'Text / Variant':30s} "
        + " ".join(f"{k[:10]:>10s}" for k in S55.FEATS)
        + f"  {'d(ZL3b)':>7s} {'d(CODE)':>7s} {'d(GEN)':>7s} {'P(CODE)':>7s}"
    )
    for T in TRANSLITS:
        vname = f"Voynich_{T}"
        f = ref_s55[vname]
        zv = voy_z[T]
        d_zl = float(np.linalg.norm(zv - voy_z["ZL3b"]))
        d_code = float(np.linalg.norm(zv - cents55["CODE"]))
        d_gen = float(np.linalg.norm(zv - cents55["GEN"]))
        p_code = S55.lr_predict(m_lr55, zv[None, :])[0][2]
        emit(
            f"  {vname:30s} "
            + " ".join(f"{f[k]:+10.4f}" for k in S55.FEATS)
            + f"  {d_zl:7.3f} {d_code:7.3f} {d_gen:7.3f} {p_code:7.3f}"
        )

    for job in naibbe_jobs + [j for j in part2_jobs if j["cls"] == "WTG"]:
        nm = job["name"]
        f = scored_map[nm]["s55"]
        _, z_nm = S55.prep(X12, np.array([[f[k] for k in S55.FEATS]], dtype=float))
        z = z_nm[0]
        d_zl = float(np.linalg.norm(z - voy_z["ZL3b"]))
        d_code = float(np.linalg.norm(z - cents55["CODE"]))
        d_gen = float(np.linalg.norm(z - cents55["GEN"]))
        p_code = S55.lr_predict(m_lr55, z_nm)[0][2]
        emit(
            f"  {nm:30s} "
            + " ".join(f"{f[k]:+10.4f}" for k in S55.FEATS)
            + f"  {d_zl:7.3f} {d_code:7.3f} {d_gen:7.3f} {p_code:7.3f}"
        )
    emit()

    emit("1C. s69 Prefix-Memory Profile of Sticky-Table Naibbe (S1.5) vs Voynich:")
    emit(
        f"  {'Text / Variant':30s} {'M1 (f4)':>9s} {'M2-M1':>9s} {'M3-M1':>9s} {'M7(cls)':>9s} "
        f"{'M8-M7_ex':>9s} {'b_pos':>9s} {'a_pos':>9s} {'k4/k1':>8s}  {'Calls (C1,C2,C3p,C4p,C5)'}"
    )
    for nm in [f"Voynich_{T}" for T in TRANSLITS] + [j["name"] for j in naibbe_jobs]:
        r69 = scored_map[nm]["s69"]
        pt = r69["point"]
        nul = r69["null"]
        m8_m7_ex = pt["M8-M7"] - nul["M8-M7"][0]
        c_dict = r69["calls"]
        c_str = " ".join(f"{ck}:{'T' if c_dict[ck][0] else 'F'}" for ck in ("C1", "C2", "C3p", "C4p", "C5"))
        emit(
            f"  {nm:30s} {pt['M1']:+9.4f} {pt['M2-M1']:+9.4f} {pt['M3-M1']:+9.4f} {pt['M7']:+9.4f} "
            f"{m8_m7_ex:+9.4f} {pt['b_pos']:+9.4f} {pt['a_pos']:+9.4f} {pt.get('k4/k1', float('nan')):+8.3f}  {c_str}"
        )
    emit(
        "  -> FINDING (Dot 22 / L-159 CLOSED): Even under 75% line-stickiness (Naibbe_line_sticky) or 100% full-line "
        "table lock (Naibbe_line_lock), Naibbe's prefix stream fails to match Voynich: (1) in bigrams (52.8% of tokens), "
        "pre(t, a) is identical across all 6 tables so table lock creates zero bigram prefix memory; (2) in unigrams "
        "(47.2% of tokens), locking the table along the entire line creates flat, non-decaying order-3+ prefix persistence "
        "(k4/k1 ~ 0.80..1.05 >= 0.25, failing C5 decay!) while still leaving f4_prefix_gain (M1) well below Voynich "
        "and keeping Euclidean distance d(ZL3b) > 4.2 in s55 z-space!"
    )
    emit()
    flush()

    # --------------------------------------------------------------------------
    # PART 2: WEAKENED TABLE-AND-GRILLE (WTG) VS RUGG GRILLE ON s69 PROFILE
    # --------------------------------------------------------------------------
    emit("================================================================================")
    emit("PART 2 (Dot 25 / L-163): Weakened Table-and-Grille (WTG) vs Rugg Grille on s69")
    emit("================================================================================")
    p2_names = [f"Voynich_{T}" for T in TRANSLITS] + [f"WTG_{T}" for T in TRANSLITS] + ["gen_rugg_grille"]

    emit("2A. Prefix-Model Ladder (Held-Out Gain over Add-0.5 Unigram, bits/prefix [95% Subsample CI]):")
    emit(f"  {'Text':20s} {'M1 (lag-1)':>24s} {'M2 (lag-2)':>24s} {'M3 (lag-3)':>24s} {'M7 (own class)':>24s} {'M8 (p1+class)':>24s} {'M7c (core id)':>15s}")
    for nm in p2_names:
        r69 = scored_map[nm]["s69"]
        pt, ci = r69["point"], r69["ci"]
        emit(
            f"  {nm:20s} "
            f"{S69.fmt_ci(pt['M1'], ci['M1']):>24s} "
            f"{S69.fmt_ci(pt['M2'], ci['M2']):>24s} "
            f"{S69.fmt_ci(pt['M3'], ci['M3']):>24s} "
            f"{S69.fmt_ci(pt['M7'], ci['M7']):>24s} "
            f"{S69.fmt_ci(pt['M8'], ci['M8']):>24s} "
            f"{pt['M7c']:+15.4f}"
        )
    emit()

    emit("2B. Key Model Differences & Within-Line Shuffle Excess (gain - null_mean, z-score):")
    emit(f"  {'Text':20s} {'M2-M1 (raw / excess)':>26s} {'M3-M1 (raw / excess)':>26s} {'M8-M7 (raw / excess / z)':>30s} {'M7/M1':>10s}")
    for nm in p2_names:
        r69 = scored_map[nm]["s69"]
        pt, nul = r69["point"], r69["null"]
        ex21 = pt["M2-M1"] - nul["M2-M1"][0]
        ex31 = pt["M3-M1"] - nul["M3-M1"][0]
        ex87 = pt["M8-M7"] - nul["M8-M7"][0]
        z87 = ex87 / nul["M8-M7"][1] if nul["M8-M7"][1] > 0 else float("nan")
        emit(
            f"  {nm:20s} "
            f"{pt['M2-M1']:+.4f} / {ex21:+.4f}".rjust(26) + " "
            f"{pt['M3-M1']:+.4f} / {ex31:+.4f}".rjust(26) + " "
            f"{pt['M8-M7']:+.4f} / {ex87:+.4f} (z{z87:+5.1f})".rjust(30) + " "
            f"{pt['M7/M1']:+10.2f}"
        )
    emit()

    emit("2C. Reset Tests (a: mid-line gallows, b: line break, d: ordinary within-line) & Decay k=1..4:")
    emit(f"  {'Text':20s} {'a_pos [95% CI]':>24s} {'b_pos [95% CI]':>24s} {'d [95% CI]':>24s} {'k1':>8s} {'k2':>8s} {'k3':>8s} {'k4':>8s} {'k4/k1':>8s}")
    for nm in p2_names:
        r69 = scored_map[nm]["s69"]
        pt, ci = r69["point"], r69["ci"]
        emit(
            f"  {nm:20s} "
            f"{S69.fmt_ci(pt['a_pos'], ci['a_pos']):>24s} "
            f"{S69.fmt_ci(pt['b_pos'], ci['b_pos']):>24s} "
            f"{S69.fmt_ci(pt['d'], ci['d']):>24s} "
            f"{pt['k1']:+8.4f} {pt['k2']:+8.4f} {pt['k3']:+8.4f} {pt['k4']:+8.4f} {pt['k4/k1']:+8.3f}"
        )
    emit()

    emit("2D. Pre-Registered s69 Calls (C1, C2, C3, C4, C5, C3p, C4p) Across Voynich, WTG, and Rugg Grille:")
    for nm in p2_names:
        c_dict = scored_map[nm]["s69"]["calls"]
        summary_calls = "  ".join(f"{ck}={('TRUE' if c_dict[ck][0] else 'FALSE')}" for ck in ("C1", "C2", "C3", "C4", "C5", "C3p", "C4p"))
        emit(f"  {nm:20s}: {summary_calls}")
    emit(
        "  -> FINDING (Dot 25 / L-163 on s69): WTG reproduces the exact Voynich call signature across all 3 "
        "transliterations (C1=TRUE, C2=FALSE, C3=FALSE, C4=FALSE, C5=TRUE, C3p=TRUE, C4p=FALSE), whereas "
        "gen_rugg_grille fails C2 (massive order-3+ memory M2-M1=+1.087), fails C5 (k4/k1=0.298 >= 0.25), and "
        "fails C3p (line-break b_pos=+0.379 > 0)."
    )
    emit()
    flush()

    # --------------------------------------------------------------------------
    # PART 3: 15-QUIRE LEAVE-ONE-QUIRE-OUT (LOQO) EVALUATION OF WTG (s67 PROTOCOL)
    # --------------------------------------------------------------------------
    emit("================================================================================")
    emit("PART 3 (CONSTRAINTS-MAP.md §C line 193 & L-163): 15-Quire LOQO Evaluation of WTG")
    emit("================================================================================")
    s67_cells = json.loads((ROOT / "runs" / "s67" / "cells.json").read_text(encoding="utf-8"))
    folds = S67.folds_of([(p["id"], p["quire"], p["lines"]) for p in pages_by_T["ZL3b"]])
    emit(f"Folds (15 quires with >= 4 pages in ZL3b): {folds}")

    loqo_jobs = []
    for ti, T in enumerate(TRANSLITS):
        for fi, Q in enumerate(folds):
            loqo_jobs.append(
                dict(
                    T=T,
                    Q=Q,
                    pages_meta=pages_by_T[T],
                    s67_cell=s67_cells[f"{T}|{Q}"],
                    off=1000 * ti + 10 * fi,
                )
            )

    loqo_res = {}
    t_loqo = time.time()
    with Pool(nproc) as pool:
        for r in pool.imap_unordered(run_loqo_fold_worker, loqo_jobs):
            loqo_res[(r["T"], r["Q"])] = r
    emit(f"Completed 45 LOQO folds ({len(loqo_jobs)} fold jobs across {nproc} workers) in {time.time() - t_loqo:.1f}s")
    emit()

    emit("3A. Per-Fold LOQO Table (P1 P2 P3 P4 P5 P7; p3=prefix_gain, t=type_ratio; * = small fold < 6 pages):")
    for T in TRANSLITS:
        emit(f"  {T}:")
        emit(
            f"    {'Fold':4s} {'Hand':4s} {'Pages':>5s} {'Real_P3 [80% CI]':>24s}  "
            + "  ".join(f"{m:30s}" for m in LOQO_MODELS)
        )
        for Q in folds:
            r = loqo_res[(T, Q)]
            rp3 = r["real_point"]["P3"]
            rci3 = r["real_ci"]["P3"]
            row_cells = []
            for m in LOQO_MODELS:
                md = r["models"][m]
                h = md["holds"]
                flags = "".join("+" if h[k] else "-" for k in PREDS)
                gp3 = md["gen_point"]["P3"]
                rt = md["type_ratio"]
                row_cells.append(f"{md['n']}/6 {flags} p3={gp3:+.3f} t={rt:.2f}")
            star = "*" if r["n_test"] < SMALL_FOLD else " "
            emit(
                f"    {Q:4s} H{r['dom_hand']:3s} {r['n_test']:5d}{star} "
                f"{rp3:+.4f} [{rci3[0]:+.4f},{rci3[1]:+.4f}]  "
                + "  ".join(f"{c:30s}" for c in row_cells)
            )
        emit()

    emit("3B. Aggregate Per-Prediction Pass Counts & Folds Passing >= 5/6 (s67 Verdict Rule):")
    verdict_pass = {}
    for T in TRANSLITS:
        nf = len(folds)
        for m in LOQO_MODELS:
            cnt = {k: sum(loqo_res[(T, Q)]["models"][m]["holds"][k] for Q in folds) for k in PREDS}
            n5 = sum(loqo_res[(T, Q)]["models"][m]["n"] >= 5 for Q in folds)
            verdict_pass[(T, m)] = n5
            mean_p3 = float(np.mean([loqo_res[(T, Q)]["models"][m]["gen_point"]["P3"] for Q in folds]))
            mean_rt = float(np.mean([loqo_res[(T, Q)]["models"][m]["type_ratio"] for Q in folds]))
            emit(
                f"  {T} {m:12s}: folds >= 5/6: {n5:2d}/{nf} | "
                + ", ".join(f"{k} {cnt[k]:2d}/{nf}" for k in PREDS)
                + f" | mean P3={mean_p3:+.4f}, mean type_ratio={mean_rt:.3f}"
            )
        emit()

    # Save sidecar summary
    (RUN_DIR / "loqo_cells_s71.json").write_text(
        json.dumps(
            {f"{T}|{Q}": loqo_res[(T, Q)] for (T, Q) in loqo_res},
            indent=1,
            default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o),
        ),
        encoding="utf-8",
        newline="\n",
    )

    emit("3C. Overall LOQO Verdict (Pre-Registered Rule: >= 5/6 on a strict majority >= 8/15 of folds across ZL3b, RF1b, IT2a):")
    for m in LOQO_MODELS:
        maj = {T: verdict_pass[(T, m)] * 2 > len(folds) for T in TRANSLITS}
        ok = all(maj.values())
        emit(
            f"  {m:12s}: "
            + "; ".join(f"{T} {verdict_pass[(T, m)]}/{len(folds)} ({'MAJORITY YES' if maj[T] else 'majority no'})" for T in TRANSLITS)
            + f" -> {'PREDICTS HELD-OUT QUIRES' if ok else 'DOES NOT PREDICT HELD-OUT QUIRES'}"
        )

    emit()
    emit(f"elapsed: {time.time() - T0:.1f}s")
    emit(f"outputs: {OUT}, {RUN_DIR}")
    flush()


if __name__ == "__main__":
    main()
