#!/usr/bin/env python
"""
Subagent 2 Experiment: Candidate 1 (Procedural text generation with local memory)
vs Candidate 2 (Meaningful text beneath a positional wrapper).

Central question:
"Can a fixed rule explain the word-edge behavior and predict something we didn't
use to design it? That would help us choose among these candidates."

STRICT READ-ONLY POLICY:
- Imports / reads data from . without modifying
  or creating any file in that directory.
- Writes output ONLY to the brain scratch directories.
"""
from __future__ import annotations

import importlib.util
import json
import math
import random
import shutil
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

import numpy as np

VOY_ROOT = Path(r".")
PARENT_SCRATCH = Path(r"<home>/.gemini/antigravity/brain/<session>/scratch")
OWN_SCRATCH = Path(r"<home>/.gemini/antigravity/brain/<session>/scratch")
OUT_FILE_PARENT = PARENT_SCRATCH / "results_exp_c1_vs_c2.txt"
OUT_FILE_OWN = OWN_SCRATCH / "results_exp_c1_vs_c2.txt"

if str(VOY_ROOT) not in sys.path:
    sys.path.insert(0, str(VOY_ROOT))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SEED = 20261017
EMPTY = "∅"
BOS = "<BOS>"

log_lines: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


def flush_out() -> None:
    text = "\n".join(log_lines) + "\n"
    for d, f in [(OWN_SCRATCH, OUT_FILE_OWN), (PARENT_SCRATCH, OUT_FILE_PARENT)]:
        try:
            d.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8", newline="\n")
        except Exception:
            pass


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Load read-only modules from voynich directory
N1 = load_mod("n1_habit_table", VOY_ROOT / "n1_habit_table.py")
G1 = load_mod("g1_edge_joint", VOY_ROOT / "g1_edge_joint.py")
M_NEW = load_mod("metrics_new", VOY_ROOT / "scoreboard" / "metrics_new.py")
R_V2 = load_mod("run_v2", VOY_ROOT / "scoreboard" / "run_v2.py")
C3 = load_mod("c3_edge_coupling", VOY_ROOT / "c3_edge_coupling.py")
F1 = load_mod("f1_residual_order", VOY_ROOT / "f1_residual_order.py")
M1 = load_mod("m1_coordinates", VOY_ROOT / "m1_coordinates.py")
S37 = load_mod("s37_affix_cadence", VOY_ROOT / "s37_affix_cadence_and_genres.py")
A2 = load_mod("a2_position", VOY_ROOT / "a2_position.py")


def load_zl3b_with_para():
    """Load ZL3b_eva with exact paragraph-start flags (matching s27/s28/s31/s33)."""
    d = json.loads((VOY_ROOT / "data" / "translit" / "ZL3b_eva.meta.json").read_text(encoding="utf-8"))
    by = OrderedDict()
    for p in d["pages"]:
        ps = p.get("para_starts")
        ps_set = set(ps) if ps is not None else {0}
        recs = []
        for idx, ln in enumerate(p["lines"]):
            if ln:
                recs.append(
                    dict(
                        page=p["id"],
                        words=list(ln),
                        hand=str(p.get("hand", "?")),
                        illus=str(p.get("section", "?")),
                        quire=p.get("quire", "?"),
                        lang=str(p.get("lang", "?")),
                        para_start=(idx in ps_set),
                    )
                )
        if recs:
            by[p["id"]] = recs
    return by


def by_to_pages(by: dict) -> list[dict]:
    return [
        dict(
            id=p,
            section=recs[0]["illus"],
            hand=recs[0]["hand"],
            quire=recs[0]["quire"],
            lang=recs[0]["lang"],
            lines=[list(r["words"]) for r in recs if r["words"]],
        )
        for p, recs in by.items()
        if any(r["words"] for r in recs)
    ]


def subset_by(by: dict, page_ids: list[str] | set[str]) -> OrderedDict:
    pset = set(page_ids)
    return OrderedDict((p, recs) for p, recs in by.items() if p in pset)


def slot_label(idx: int, line_len: int, para_start: bool) -> str:
    if idx == 0:
        return "para_0" if para_start else "line_0"
    if idx == line_len - 1:
        return "final"
    if idx == 1:
        return "slot_1"
    if idx == line_len - 2 and line_len >= 4:
        return "penult"
    return "mid"


def core_len_bin(c: str) -> str:
    L = len(c)
    if L <= 1:
        return "1"
    if L == 2:
        return "2"
    if L == 3:
        return "3"
    return "4+"


# ==============================================================================
# Factored Conditional Wrapper Rule (Trained Strictly on 166 Train Pages)
# ==============================================================================
class FactoredWrapperRule:
    """Product-of-experts / Naive-Bayes factored conditional model fitted strictly on
    the 166 training pages (zero test-set parameters):
      P(target | base_ctx, f_1, ..., f_k) \\propto P_base(target | base_ctx) * \\prod_j (P(target | f_j) / P(target))^{w_j}
    Each 1D conditional table P(target | f_j) is smoothed toward P(target) with Dirichlet
    pseudocount m_smooth (default 10.0) so rare contexts smoothly shrink to the marginal
    instead of overfitting on singletons.
    """

    def __init__(self, vocab: list[str], base_fn, factor_fns: list[tuple[callable, float]], m_smooth: float = 10.0):
        self.vocab = sorted(set(vocab))
        self.V = len(self.vocab)
        self.base_fn = base_fn
        self.factor_fns = factor_fns
        self.m_smooth = m_smooth
        self.uni = Counter()
        self.N = 0
        self.base_counts: list[dict[tuple, Counter]] = []
        self.base_totals: list[dict[tuple, int]] = []
        self.fac_counts: list[dict[tuple, Counter]] = [defaultdict(Counter) for _ in factor_fns]
        self.fac_totals: list[dict[tuple, int]] = [defaultdict(int) for _ in factor_fns]
        self._cache: dict[tuple, dict[str, float]] = {}

    def fit(self, items: list[tuple[dict, str]]) -> "FactoredWrapperRule":
        for ctx_dict, target in items:
            self.uni[target] += 1
            self.N += 1
            b_ctxs = self.base_fn(ctx_dict)
            while len(self.base_counts) < len(b_ctxs):
                self.base_counts.append(defaultdict(Counter))
                self.base_totals.append(defaultdict(int))
            for lvl, bk in enumerate(b_ctxs):
                self.base_counts[lvl][bk][target] += 1
                self.base_totals[lvl][bk] += 1
            for fi, (ffn, _) in enumerate(self.factor_fns):
                fk = ffn(ctx_dict)
                if fk is not None:
                    self.fac_counts[fi][fk][target] += 1
                    self.fac_totals[fi][fk] += 1
        return self

    def dist(self, ctx_dict: dict) -> dict[str, float]:
        b_ctxs = tuple(self.base_fn(ctx_dict))
        f_keys = tuple(ffn(ctx_dict) for ffn, _ in self.factor_fns)
        cache_key = (b_ctxs, f_keys)
        if cache_key in self._cache:
            return self._cache[cache_key]

        denom_u = self.N + 0.5 * self.V
        p_u = {v: (self.uni.get(v, 0) + 0.5) / denom_u for v in self.vocab}
        p_cur = dict(p_u)

        # Base positional + section hierarchy with gentle pseudocount M=8.0
        for lvl in range(len(b_ctxs) - 1, -1, -1):
            if lvl >= len(self.base_counts):
                continue
            bk = b_ctxs[lvl]
            cnts = self.base_counts[lvl].get(bk)
            if not cnts:
                continue
            tot = self.base_totals[lvl][bk]
            M = 8.0
            denom = tot + M
            for v in self.vocab:
                p_cur[v] = (cnts.get(v, 0) + M * p_cur[v]) / denom

        # Multiply by smoothed likelihood-ratio lifts from sequential edge/wrapper factors
        for fi, (_, w_exp) in enumerate(self.factor_fns):
            fk = f_keys[fi]
            if fk is None:
                continue
            cnts = self.fac_counts[fi].get(fk)
            if not cnts:
                continue
            tot = self.fac_totals[fi][fk]
            M = self.m_smooth
            denom = tot + M
            for v in self.vocab:
                p_cond = (cnts.get(v, 0) + M * p_u[v]) / denom
                lift = (p_cond / p_u[v]) ** w_exp
                p_cur[v] *= lift

        norm = sum(p_cur.values())
        for v in self.vocab:
            p_cur[v] /= norm
        self._cache[cache_key] = p_cur
        return p_cur


def extract_wrapper_items(by: dict, seg) -> list[dict]:
    """Extract per-token context dicts and target P_t, S_t, C_t."""
    out = []
    for page, recs in by.items():
        for li, r in enumerate(recs):
            ws = r["words"]
            L = len(ws)
            if L == 0:
                continue
            segs = [seg.segment(w) for w in ws]
            for i, (w, (p_raw, c_raw, s_raw)) in enumerate(zip(ws, segs)):
                P_t = p_raw if p_raw else EMPTY
                S_t = s_raw if s_raw else EMPTY
                C_t = c_raw
                s_lbl = slot_label(i, L, r.get("para_start", False))
                if i == 0:
                    P_prev = BOS
                    S_prev = BOS
                    C_prev = BOS
                    cbin_prev = BOS
                    clast_prev = BOS
                else:
                    p_pr, c_pr, s_pr = segs[i - 1]
                    P_prev = p_pr if p_pr else EMPTY
                    S_prev = s_pr if s_pr else EMPTY
                    C_prev = c_pr
                    cbin_prev = core_len_bin(c_pr)
                    clast_prev = c_pr[-1] if c_pr else EMPTY
                ctx = dict(
                    page=page,
                    line_idx=li,
                    tok_idx=i,
                    line_len=L,
                    line_len_bin="short" if L <= 6 else ("med" if L <= 10 else "long"),
                    slot=s_lbl,
                    sec=r["illus"],
                    hand=r["hand"],
                    lang=r["lang"],
                    P_prev=P_prev,
                    S_prev=S_prev,
                    C_prev=C_prev,
                    cbin_prev=cbin_prev,
                    clast_prev=clast_prev,
                    P_t=P_t,
                    C_t=C_t,
                    S_t=S_t,
                    word=w,
                )
                out.append(ctx)
    return out


# ==============================================================================
# EXPERIMENT 2A: Out-of-Sample Wrapper Rule Prediction & Untargeted Moran I
# ==============================================================================
def run_experiment_2a(by_all: dict, train_ids: list[str], held_ids: list[str], seg) -> dict:
    emit("=" * 104)
    emit("EXPERIMENT 2A: FIXED POSITIONAL + EDGE-COUPLED WRAPPER RULE (166 Train Pages -> 41 Held-Out Pages)")
    emit("=" * 104)

    by_train = subset_by(by_all, train_ids)
    by_held = subset_by(by_all, held_ids)

    tr_items = extract_wrapper_items(by_train, seg)
    te_items = extract_wrapper_items(by_held, seg)

    p_vocab = sorted({x["P_t"] for x in tr_items} | {x["P_t"] for x in te_items} | {EMPTY})
    s_vocab = sorted({x["S_t"] for x in tr_items} | {x["S_t"] for x in te_items} | {EMPTY})

    p_len_map = {p: (0 if p == EMPTY else len(p)) for p in p_vocab}
    s_len_map = {s: (0 if s == EMPTY else len(s)) for s in s_vocab}

    base_pos_sec = lambda d: [(d["slot"], d["sec"]), (d["slot"],)]
    fac_sprev = (lambda d: None if d["S_prev"] == BOS else (d["S_prev"], d["lang"]), 0.65)
    fac_cbin = (lambda d: None if d["cbin_prev"] == BOS else d["cbin_prev"], 0.30)
    fac_pprev = (lambda d: None if d["P_prev"] == BOS else d["P_prev"], 0.30)
    fac_cprev = (lambda d: None if d["C_prev"] == BOS else d["C_prev"], 0.25)
    fac_clast = (lambda d: None if d["clast_prev"] == BOS else d["clast_prev"], 0.25)

    model_specs = [
        ("W0_Unigram", lambda d: [], [], "Marginal P(P_t) on 166 train pages"),
        ("W1_PosSlot_Sec", base_pos_sec, [], "Positional slot + section only"),
        (
            "W2_Pos_Sprev_Sec",
            base_pos_sec,
            [fac_sprev],
            "Positional + S_{t-1}->P_t sandhi + section",
        ),
        (
            "W3_Pos_Sprev_Cbin_Sec",
            base_pos_sec,
            [fac_sprev, fac_cbin],
            "Prompt baseline: (line_slot, S_{t-1}, len_bin(C_{t-1}), section)",
        ),
        (
            "W4_Add_Pprev_Persist",
            base_pos_sec,
            [fac_sprev, fac_cbin, fac_pprev],
            "W3 + P_{t-1}->P_t prefix-run persistence (s34/s37)",
        ),
        (
            "W5_Full_S37_Cprev_Pprev",
            base_pos_sec,
            [fac_sprev, fac_cbin, fac_pprev, fac_clast, fac_cprev],
            "W4 + C_{t-1}->P_t exact/edge core-to-prefix coupling (s34/s37)",
        ),
    ]

    emit("\n--- 2A-i: Out-of-Sample Prediction of Prefix Class P_t & Prefix Length |P_t| on 41 Held-Out Pages ---")
    emit(
        f"  Train: 166 pages ({len(tr_items)} tokens); Held-Out Test: 41 pages ({len(te_items)} tokens, "
        f"{sum(1 for x in te_items if x['tok_idx'] > 0)} non-initial adjacent transitions)."
    )
    hdr = (
        f"  {'Model':24s} | {'All_H(b)':>8s} {'PPL':>6s} {'Gain':>7s} {'Top1%':>6s} {'Top3%':>6s} {'Top5%':>6s} | "
        f"{'Adj_H':>7s} {'AdjGain':>7s} {'r(|P|)':>7s} {'MAE|P|':>6s} | Description"
    )
    emit(hdr)
    emit("  " + "-" * (len(hdr) - 2))

    p_models = {}
    s_models = {}
    eval_summary = {}

    base_all_h = None
    base_adj_h = None

    for m_name, b_fn, f_list, desc in model_specs:
        pm = FactoredWrapperRule(p_vocab, b_fn, f_list, m_smooth=25.0).fit([(x, x["P_t"]) for x in tr_items])
        p_models[m_name] = pm

        s_base_fn = (lambda d: []) if m_name == "W0_Unigram" else (lambda d: [(d["slot"], d["P_t"], d["sec"]), (d["slot"], d["P_t"]), (d["slot"],)])
        s_facs = [] if m_name in ("W0_Unigram", "W1_PosSlot_Sec") else [
            (lambda d: None if d["S_prev"] == BOS else (d["S_prev"], d["lang"]), 0.45),
            (lambda d: None if d["cbin_prev"] == BOS else d["cbin_prev"], 0.30),
        ]
        sm = FactoredWrapperRule(s_vocab, s_base_fn, s_facs, m_smooth=25.0).fit([(x, x["S_t"]) for x in tr_items])
        s_models[m_name] = sm

        bits_all, bits_adj, n_adj = 0.0, 0.0, 0
        top1, top3, top5 = 0, 0, 0
        pred_plen, true_plen = [], []

        for x in te_items:
            dist = pm.dist(x)
            p_true = dist[x["P_t"]]
            b = -math.log2(max(p_true, 1e-15))
            bits_all += b
            ranked = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)
            r_keys = [k for k, _ in ranked]
            if r_keys[0] == x["P_t"]:
                top1 += 1
            if x["P_t"] in r_keys[:3]:
                top3 += 1
            if x["P_t"] in r_keys[:5]:
                top5 += 1

            exp_len = sum(prob * p_len_map[k] for k, prob in dist.items())
            actual_len = p_len_map[x["P_t"]]
            pred_plen.append(exp_len)
            true_plen.append(actual_len)

            if x["tok_idx"] > 0:
                bits_adj += b
                n_adj += 1

        h_all = bits_all / len(te_items)
        h_adj = bits_adj / max(1, n_adj)
        if base_all_h is None:
            base_all_h = h_all
            base_adj_h = h_adj

        gain_all = base_all_h - h_all
        gain_adj = base_adj_h - h_adj
        ppl = 2.0 ** h_all
        t1_pct = 100.0 * top1 / len(te_items)
        t3_pct = 100.0 * top3 / len(te_items)
        t5_pct = 100.0 * top5 / len(te_items)

        pa = np.array(pred_plen, dtype=float)
        ta = np.array(true_plen, dtype=float)
        r_len = float(np.corrcoef(pa, ta)[0, 1]) if np.std(pa) > 1e-9 else 0.0
        mae_len = float(np.mean(np.abs(pa - ta)))

        eval_summary[m_name] = dict(
            h_all=h_all,
            ppl=ppl,
            gain_all=gain_all,
            t1=t1_pct,
            t3=t3_pct,
            t5=t5_pct,
            h_adj=h_adj,
            gain_adj=gain_adj,
            r_len=r_len,
            mae_len=mae_len,
        )
        emit(
            f"  {m_name:24s} | {h_all:8.4f} {ppl:6.2f} {gain_all:+7.4f} {t1_pct:5.2f}% {t3_pct:5.2f}% {t5_pct:5.2f}% | "
            f"{h_adj:7.4f} {gain_adj:+7.4f} {r_len:+7.4f} {mae_len:6.3f} | {desc}"
        )

    emit("\n--- 2A-i (Slot Breakdown): Held-Out P_t Prediction by Line Position Slot (W0 vs W3 vs W5) ---")
    emit(
        f"  {'Slot':10s} | {'N_tok':>6s} {'Mean|P|':>7s} {'EmptyP%':>7s} | "
        f"{'W0_H':>7s} {'W3_H':>7s} {'W3_Gain':>8s} {'W3_Top1':>7s} {'W3_Top3':>7s} | "
        f"{'W5_H':>7s} {'W5_Gain':>8s} {'W5_Top1':>7s} {'W5_Top3':>7s}"
    )
    emit("  " + "-" * 108)
    for s_lbl in ["para_0", "line_0", "slot_1", "mid", "penult", "final"]:
        sub = [x for x in te_items if x["slot"] == s_lbl]
        if not sub:
            continue
        mean_pl = np.mean([p_len_map[x["P_t"]] for x in sub])
        emp_pct = 100.0 * sum(1 for x in sub if x["P_t"] == EMPTY) / len(sub)
        vals = {}
        for mn in ["W0_Unigram", "W3_Pos_Sprev_Cbin_Sec", "W5_Full_S37_Cprev_Pprev"]:
            pm = p_models[mn]
            b_sum, t1, t3 = 0.0, 0, 0
            for x in sub:
                d = pm.dist(x)
                b_sum += -math.log2(max(d[x["P_t"]], 1e-15))
                rk = [k for k, _ in sorted(d.items(), key=lambda kv: kv[1], reverse=True)]
                if rk[0] == x["P_t"]:
                    t1 += 1
                if x["P_t"] in rk[:3]:
                    t3 += 1
            vals[mn] = (b_sum / len(sub), 100.0 * t1 / len(sub), 100.0 * t3 / len(sub))
        w0_h = vals["W0_Unigram"][0]
        w3_h, w3_t1, w3_t3 = vals["W3_Pos_Sprev_Cbin_Sec"]
        w5_h, w5_t1, w5_t3 = vals["W5_Full_S37_Cprev_Pprev"]
        emit(
            f"  {s_lbl:10s} | {len(sub):6d} {mean_pl:7.3f} {emp_pct:6.2f}% | "
            f"{w0_h:7.4f} {w3_h:7.4f} {w0_h - w3_h:+8.4f} {w3_t1:6.2f}% {w3_t3:6.2f}% | "
            f"{w5_h:7.4f} {w0_h - w5_h:+8.4f} {w5_t1:6.2f}% {w5_t3:6.2f}%"
        )

    emit("\n--- 2A-i (Joint Wrapper): Held-Out Joint (P_t, S_t) Entropy & Gain on 41 Held-Out Pages ---")
    emit(f"  {'Model':24s} | {'H(P_t)':>8s} {'H(S_t|P_t)':>10s} {'H(P_t,S_t)':>10s} {'JointGain':>10s} | {'E[|P+S|] r':>10s}")
    emit("  " + "-" * 76)
    base_joint_h = None
    for m_name, _, _, _ in model_specs:
        pm = p_models[m_name]
        sm = s_models[m_name]
        bp, bs = 0.0, 0.0
        pred_alen, true_alen = [], []
        for x in te_items:
            dp = pm.dist(x)
            ds = sm.dist(x)
            bp += -math.log2(max(dp[x["P_t"]], 1e-15))
            bs += -math.log2(max(ds[x["S_t"]], 1e-15))
            exp_p = sum(prob * p_len_map[k] for k, prob in dp.items())
            exp_s = sum(prob * s_len_map[k] for k, prob in ds.items())
            pred_alen.append(exp_p + exp_s)
            true_alen.append(p_len_map[x["P_t"]] + s_len_map[x["S_t"]])
        hp = bp / len(te_items)
        hs = bs / len(te_items)
        hj = hp + hs
        if base_joint_h is None:
            base_joint_h = hj
        ra = float(np.corrcoef(pred_alen, true_alen)[0, 1]) if np.std(pred_alen) > 1e-9 else 0.0
        emit(f"  {m_name:24s} | {hp:8.4f} {hs:10.4f} {hj:10.4f} {base_joint_h - hj:+10.4f} | {ra:+10.4f}")

    # ==========================================================================
    # Part 2A-ii: Why s28 only reached I_within = 0.057 vs MS 0.157, and whether
    # driving an uncoupled core pool with the fixed wrapper rule predicts I_within!
    # ==========================================================================
    emit("\n" + "=" * 104)
    emit("EXPERIMENT 2A-ii: WHY S28 ONLY REACHED I_within = 0.057 VS MS 0.157, AND UNTARGETED")
    emit("                  OUT-OF-SAMPLE PREDICTION OF I_within ON THE 41 HELD-OUT PAGES")
    emit("=" * 104)

    all_toks_zl = [w for recs in by_all.values() for r in recs for w in r["words"]]
    seg_cache_zl = {w: seg.segment(w) for w in set(all_toks_zl)}
    pages_zl_full = by_to_pages(by_all)
    pages_zl_g41 = by_to_pages(by_held)

    bil_zl_full = S37._run_bilinear_stratum(pages_zl_full, seg_cache_zl, seed=SEED)
    bil_zl_g41 = S37._run_bilinear_stratum(pages_zl_g41, seg_cache_zl, seed=SEED)

    s28_bils_full = []
    s28_bils_g41 = []
    for s_idx in (1, 2, 3):
        s28_path = VOY_ROOT / "runs" / "s28" / f"s28_gen_ZL3b_s{s_idx}.meta.json"
        if s28_path.exists():
            d_s28 = json.loads(s28_path.read_text(encoding="utf-8"))
            pg_s28 = d_s28["pages"]
            toks_s28 = [w for p in pg_s28 for ln in p["lines"] for w in ln]
            seg_cache_s28 = {w: seg.segment(w) for w in set(toks_s28)}
            s28_bils_full.append((f"s28_ZL3b_s{s_idx}_full", S37._run_bilinear_stratum(pg_s28, seg_cache_s28, seed=SEED)))
            pg_s28_g41 = [p for p in pg_s28 if p["id"] in set(held_ids)]
            s28_bils_g41.append((f"s28_ZL3b_s{s_idx}_g41", S37._run_bilinear_stratum(pg_s28_g41, seg_cache_s28, seed=SEED)))

    emit("\n--- 2A-ii (Part 1): Exact 9-Component Bilinear Decomposition of Voynich vs S28 Generator ---")
    emit(
        f"  {'Dataset':22s} | {'I_within':>8s} {'I_shuf':>8s} {'I_excess':>8s} | "
        f"{'P1->P2':>8s} {'S1->S2':>8s} {'S1->P2':>8s} {'C1->P2':>8s} {'C1->S2':>8s} {'S1->C2':>8s} {'P1->C2':>8s} {'C1->C2':>8s}"
    )
    emit("  " + "-" * 116)

    def _emit_bil_row(label: str, br: dict, use_excess: bool = True):
        cr = br["comp_rows"]
        k = "ex_mean" if use_excess else "i_obs"
        tot_i = br["tot"]["I"]
        shuf_i = br["tot"]["null_mean"]
        ex_i = tot_i - shuf_i
        emit(
            f"  {label:22s} | {tot_i:+8.4f} {shuf_i:+8.4f} {ex_i:+8.4f} | "
            f"{cr['P1->P2'][k]:+8.4f} {cr['S1->S2'][k]:+8.4f} {cr['S1->P2'][k]:+8.4f} "
            f"{cr['C1->P2'][k]:+8.4f} {cr['C1->S2'][k]:+8.4f} {cr['S1->C2'][k]:+8.4f} "
            f"{cr['P1->C2'][k]:+8.4f} {cr['C1->C2'][k]:+8.4f}"
        )

    _emit_bil_row("Voynich_ZL3b_full", bil_zl_full, True)
    for lbl, br in s28_bils_full:
        _emit_bil_row(lbl, br, True)
    emit("  " + "." * 116)
    _emit_bil_row("Voynich_ZL3b_g41", bil_zl_g41, True)
    for lbl, br in s28_bils_g41:
        _emit_bil_row(lbl, br, True)

    c_to_ps_train = defaultdict(Counter)
    ps_sec_to_c_train = defaultdict(Counter)
    ps_to_c_train = defaultdict(Counter)
    sec_to_c_train = defaultdict(Counter)
    c_len_to_ps_train = defaultdict(Counter)

    for x in tr_items:
        ps_key = (x["P_t"], x["S_t"])
        c_to_ps_train[x["C_t"]][ps_key] += 1
        c_len_to_ps_train[core_len_bin(x["C_t"])][ps_key] += 1
        ps_sec_to_c_train[(x["P_t"], x["S_t"], x["sec"])][x["C_t"]] += 1
        ps_to_c_train[(x["P_t"], x["S_t"])][x["C_t"]] += 1
        sec_to_c_train[x["sec"]][x["C_t"]] += 1

    def simulate_heldout_protocol_a(m_name: str, use_within_word_bind: bool, seed_sim: int = SEED) -> tuple[list[dict], dict]:
        rng = random.Random(seed_sim)
        pm = p_models[m_name]
        sm = s_models[m_name]
        sim_pages = []
        seg_override = {}

        for page, recs in by_held.items():
            sim_lines = []
            for li, r in enumerate(recs):
                ws = r["words"]
                L = len(ws)
                if L == 0:
                    continue
                true_cores = [seg.segment(w)[1] for w in ws]
                shuf_cores = true_cores[:]
                rng.shuffle(shuf_cores)

                line_words = []
                P_prev, S_prev, C_prev = BOS, BOS, BOS
                for i, C_t in enumerate(shuf_cores):
                    s_lbl = slot_label(i, L, r.get("para_start", False))
                    ctx = dict(
                        slot=s_lbl,
                        sec=r["illus"],
                        hand=r["hand"],
                        lang=r["lang"],
                        P_prev=P_prev,
                        S_prev=S_prev,
                        C_prev=C_prev,
                        cbin_prev=BOS if i == 0 else core_len_bin(C_prev),
                        clast_prev=BOS if i == 0 else (C_prev[-1] if C_prev else EMPTY),
                    )
                    dp = pm.dist(ctx)
                    if use_within_word_bind:
                        ps_cnts = c_to_ps_train.get(C_t)
                        if not ps_cnts or sum(ps_cnts.values()) < 3:
                            ps_cnts = c_len_to_ps_train[core_len_bin(C_t)]
                        p_marginal_c = Counter()
                        for (pk, sk), cnt in ps_cnts.items():
                            p_marginal_c[pk] += cnt
                        tot_c = sum(p_marginal_c.values())
                        wts_p = [dp[pk] * ((p_marginal_c.get(pk, 0) + 0.2) / (tot_c + 0.2 * len(p_vocab))) for pk in p_vocab]
                        P_t = rng.choices(p_vocab, weights=wts_p, k=1)[0]
                        ctx["P_t"] = P_t
                        ds = sm.dist(ctx)
                        s_given_cp = {sk: ps_cnts.get((P_t, sk), 0) for sk in s_vocab}
                        tot_scp = sum(s_given_cp.values())
                        wts_s = [ds[sk] * ((s_given_cp.get(sk, 0) + 0.2) / (tot_scp + 0.2 * len(s_vocab))) for sk in s_vocab]
                        S_t = rng.choices(s_vocab, weights=wts_s, k=1)[0]
                    else:
                        P_t = rng.choices(p_vocab, weights=[dp[pk] for pk in p_vocab], k=1)[0]
                        ctx["P_t"] = P_t
                        ds = sm.dist(ctx)
                        S_t = rng.choices(s_vocab, weights=[ds[sk] for sk in s_vocab], k=1)[0]

                    p_str = "" if P_t == EMPTY else P_t
                    s_str = "" if S_t == EMPTY else S_t
                    w_syn = f"{p_str}{C_t}{s_str}"
                    seg_override[w_syn] = seg.segment(w_syn)
                    line_words.append(w_syn)
                    P_prev, S_prev, C_prev = P_t, S_t, C_t
                sim_lines.append(line_words)
            sim_pages.append(
                dict(
                    id=page,
                    section=recs[0]["illus"],
                    hand=recs[0]["hand"],
                    quire=recs[0]["quire"],
                    lang=recs[0]["lang"],
                    lines=sim_lines,
                )
            )
        return sim_pages, seg_override

    def simulate_heldout_protocol_b(m_name: str, line_reg: bool = True, seed_sim: int = SEED) -> tuple[list[dict], dict]:
        rng = random.Random(seed_sim)
        pm = p_models[m_name]
        sm = s_models[m_name]
        sim_pages = []
        seg_override = {}

        line_means_by_key = defaultdict(list)
        for p, recs in by_train.items():
            for r in recs:
                if len(r["words"]) >= 2:
                    line_means_by_key[(r["hand"], r["illus"])].append(float(np.mean([len(w) for w in r["words"]])))
        all_line_means = [m for ms in line_means_by_key.values() for m in ms]

        for page, recs in by_held.items():
            sim_lines = []
            for li, r in enumerate(recs):
                ws = r["words"]
                L = len(ws)
                if L == 0:
                    continue
                key = (r["hand"], r["illus"])
                l_pool = line_means_by_key.get(key, all_line_means)
                target_l = rng.choice(l_pool) if line_reg else 5.0

                line_words = []
                P_prev, S_prev, C_prev = BOS, BOS, BOS
                for i in range(L):
                    s_lbl = slot_label(i, L, r.get("para_start", False))
                    ctx = dict(
                        slot=s_lbl,
                        sec=r["illus"],
                        hand=r["hand"],
                        lang=r["lang"],
                        P_prev=P_prev,
                        S_prev=S_prev,
                        C_prev=C_prev,
                        cbin_prev=BOS if i == 0 else core_len_bin(C_prev),
                        clast_prev=BOS if i == 0 else (C_prev[-1] if C_prev else EMPTY),
                    )
                    dp = pm.dist(ctx)
                    if line_reg:
                        wts_p = [dp[pk] * math.exp(-0.35 * abs((p_len_map[pk] + 3.1) - target_l)) for pk in p_vocab]
                    else:
                        wts_p = [dp[pk] for pk in p_vocab]
                    P_t = rng.choices(p_vocab, weights=wts_p, k=1)[0]
                    ctx["P_t"] = P_t
                    ds = sm.dist(ctx)
                    if line_reg:
                        wts_s = [
                            ds[sk] * math.exp(-0.35 * abs((p_len_map[P_t] + s_len_map[sk] + 2.3) - target_l))
                            for sk in s_vocab
                        ]
                    else:
                        wts_s = [ds[sk] for sk in s_vocab]
                    S_t = rng.choices(s_vocab, weights=wts_s, k=1)[0]

                    c_cnts = ps_sec_to_c_train.get((P_t, S_t, r["illus"]))
                    if not c_cnts or sum(c_cnts.values()) < 3:
                        c_cnts = ps_to_c_train.get((P_t, S_t))
                    if not c_cnts:
                        c_cnts = sec_to_c_train.get(r["illus"])
                    c_cands = list(c_cnts.keys())
                    if line_reg:
                        p_l = p_len_map[P_t] + s_len_map[S_t]
                        c_wts = [c_cnts[c] * math.exp(-0.45 * abs((p_l + len(c)) - target_l)) for c in c_cands]
                    else:
                        c_wts = [c_cnts[c] for c in c_cands]
                    C_t = rng.choices(c_cands, weights=c_wts, k=1)[0]

                    p_str = "" if P_t == EMPTY else P_t
                    s_str = "" if S_t == EMPTY else S_t
                    w_syn = f"{p_str}{C_t}{s_str}"
                    seg_override[w_syn] = seg.segment(w_syn)
                    line_words.append(w_syn)
                    P_prev, S_prev, C_prev = P_t, S_t, C_t
                sim_lines.append(line_words)
            sim_pages.append(
                dict(
                    id=page,
                    section=recs[0]["illus"],
                    hand=recs[0]["hand"],
                    quire=recs[0]["quire"],
                    lang=recs[0]["lang"],
                    lines=sim_lines,
                )
            )
        return sim_pages, seg_override

    emit("\n--- 2A-ii (Part 2): Untargeted Prediction of Held-Out Within-Line Moran I (41 Held-Out Pages) ---")
    emit("  Protocol A: Held-out line cores C_t are SHUFFLED within each line (destroying all C_{t-1}->C_t order),")
    emit("              and wrappers (P_t, S_t) are generated by the fixed rule fitted strictly on 166 train pages.")
    emit("  Protocol B: Pure 166-page-trained wrapper + uncoupled core pool (zero held-out cores used).")
    emit(
        f"  {'Configuration':34s} | {'I_within':>8s} {'I_shuf':>8s} {'I_q99':>8s} {'I_excess':>8s} {'p':>6s} | "
        f"{'PureAff_Ex':>10s} {'AffCore_Ex':>10s} {'Core_Ex':>8s}"
    )
    emit("  " + "-" * 114)

    def _emit_sim_row(label: str, br: dict):
        tot = br["tot"]
        cr = br["comp_rows"]
        ex_tot = tot["I"] - tot["null_mean"]
        aff_ex = sum(cr[k]["ex_mean"] for k in ["P1->P2", "S1->S2", "S1->P2", "P1->S2"])
        crs_ex = sum(cr[k]["ex_mean"] for k in ["C1->P2", "P1->C2", "S1->C2", "C1->S2"])
        cor_ex = cr["C1->C2"]["ex_mean"]
        emit(
            f"  {label:34s} | {tot['I']:+8.4f} {tot['null_med']:+8.4f} {tot['null_q99']:+8.4f} {ex_tot:+8.4f} {tot['p']:6.3f} | "
            f"{aff_ex:+10.4f} {crs_ex:+10.4f} {cor_ex:+8.4f}"
        )

    _emit_sim_row("Voynich_ZL3b_g41 (Observed Target)", bil_zl_g41)
    if s28_bils_g41:
        _emit_sim_row("s28_gen_ZL3b_s1_g41 (Flat M2 Gen)", s28_bils_g41[0][1])

    for m_name in [
        "W0_Unigram",
        "W1_PosSlot_Sec",
        "W2_Pos_Sprev_Sec",
        "W3_Pos_Sprev_Cbin_Sec",
        "W4_Add_Pprev_Persist",
        "W5_Full_S37_Cprev_Pprev",
    ]:
        sp_a, sc_a = simulate_heldout_protocol_a(m_name, use_within_word_bind=True, seed_sim=SEED)
        br_a = S37._run_bilinear_stratum(sp_a, sc_a, seed=SEED)
        _emit_sim_row(f"ProtA (ShufC + {m_name[:18]})", br_a)

    emit("  " + "." * 114)
    for m_name, line_reg, tag in [
        ("W1_PosSlot_Sec", False, "ProtB_NoLineReg (W1_PosSlot)"),
        ("W3_Pos_Sprev_Cbin_Sec", False, "ProtB_NoLineReg (W3_PromptRule)"),
        ("W5_Full_S37_Cprev_Pprev", False, "ProtB_NoLineReg (W5_FullS37)"),
        ("W3_Pos_Sprev_Cbin_Sec", True, "ProtB_WithLineReg (W3_PromptRule)"),
        ("W4_Add_Pprev_Persist", True, "ProtB_WithLineReg (W4_AddPprev)"),
        ("W5_Full_S37_Cprev_Pprev", True, "ProtB_WithLineReg (W5_FullS37)"),
    ]:
        sp_b, sc_b = simulate_heldout_protocol_b(m_name, line_reg=line_reg, seed_sim=SEED)
        br_b = S37._run_bilinear_stratum(sp_b, sc_b, seed=SEED)
        _emit_sim_row(tag, br_b)

    flush_out()
    return dict(p_models=p_models, s_models=s_models, tr_items=tr_items, te_items=te_items)


# ==============================================================================
# EXPERIMENT 2B: Candidate 2 Stripping Test — Fixed Wrapper Stripping on Untouched Pages
# ==============================================================================
def build_stripped_by(
    by_src: dict,
    seg,
    rule_name: str,
    p_model=None,
    s_model=None,
) -> OrderedDict:
    out = OrderedDict()
    init_markers = ("p", "f", "y", "d", "t", "s", "o")
    fin_markers = ("m", "g")
    oyds_markers = ("o", "y", "d", "s")

    for page, recs in by_src.items():
        new_recs = []
        for r in recs:
            ws = r["words"]
            L = len(ws)
            if L == 0:
                continue
            segs = [seg.segment(w) for w in ws]
            new_ws = []
            P_prev, S_prev, C_prev = BOS, BOS, BOS

            for i, (w, (p_raw, c_raw, s_raw)) in enumerate(zip(ws, segs)):
                P_t = p_raw if p_raw else EMPTY
                S_t = s_raw if s_raw else EMPTY
                C_t = c_raw
                s_lbl = slot_label(i, L, r.get("para_start", False))

                if rule_name == "S0_Raw_Full":
                    w_new = w
                elif rule_name == "S1a_LineEdge_Only":
                    w_new = w
                    if i == 0 and len(w_new) >= 3 and w_new[0] in init_markers:
                        w_new = w_new[1:]
                    if i == L - 1 and len(w_new) >= 3 and w_new[-1] in fin_markers:
                        w_new = w_new[:-1]
                elif rule_name == "S1b_LineEdge_Plus_oyds":
                    w_new = w
                    if i == 0 and len(w_new) >= 3 and w_new[0] in init_markers:
                        w_new = w_new[1:]
                    elif len(w_new) >= 3 and w_new[0] in oyds_markers:
                        w_new = w_new[1:]
                    if i == L - 1 and len(w_new) >= 3 and w_new[-1] in fin_markers:
                        w_new = w_new[:-1]
                elif rule_name == "S2a_Strip_Prefix_Only":
                    w_new = c_raw + s_raw
                elif rule_name == "S2b_Strip_Suffix_Only":
                    w_new = p_raw + c_raw
                elif rule_name == "S2_Strip_Full_SlotSeg_Core":
                    w_new = c_raw
                elif rule_name in ("S3a_CondStrip_Top1", "S3b_CondStrip_Top3"):
                    k_top = 1 if rule_name == "S3a_CondStrip_Top1" else 3
                    ctx = dict(
                        slot=s_lbl,
                        sec=r["illus"],
                        hand=r["hand"],
                        lang=r["lang"],
                        P_prev=P_prev,
                        S_prev=S_prev,
                        C_prev=C_prev,
                        cbin_prev=BOS if i == 0 else core_len_bin(C_prev),
                        clast_prev=BOS if i == 0 else (C_prev[-1] if C_prev else EMPTY),
                    )
                    dp = p_model.dist(ctx)
                    rk_p = [k for k, _ in sorted(dp.items(), key=lambda kv: kv[1], reverse=True)]
                    keep_p = "" if (P_t in rk_p[:k_top]) else p_raw
                    ctx["P_t"] = P_t
                    ds = s_model.dist(ctx)
                    rk_s = [k for k, _ in sorted(ds.items(), key=lambda kv: kv[1], reverse=True)]
                    keep_s = "" if (S_t in rk_s[:k_top]) else s_raw
                    w_new = f"{keep_p}{c_raw}{keep_s}"
                else:
                    raise ValueError(f"Unknown rule {rule_name}")

                if not w_new:
                    w_new = c_raw if c_raw else w
                new_ws.append(w_new)
                P_prev, S_prev, C_prev = P_t, S_t, C_t

            new_recs.append(dict(r, words=new_ws))
        if new_recs:
            out[page] = new_recs
    return out


def compute_f1_decomposed(train_lines: list[list[str]], test_pl: list[tuple[str, list[str]]], topn: int | None = 300) -> dict:
    F1.TOPN = topn

    def _eval_pages(tr_l, te_pl):
        f = F1.mapper(tr_l, topn)
        m = F1.Models(tr_l, f)
        te_l = [l for _, l in te_pl]
        tp = [(a, f(b)) for a, b in F1.pairs_of(te_l)]
        a_best = min(F1.GRID_A, key=lambda x: F1.bits(tp, lambda a, b: m.pe2(a, b, x)))
        k_best = min(F1.GRID_K, key=lambda k: F1.bits(tp, lambda a, b: m.pw(a, b, a_best, k)))
        sums = defaultdict(lambda: np.zeros(4, dtype=np.float64))
        for p, l in te_pl:
            for a, b in zip(l, l[1:]):
                bm = f(b)
                sums[p] += (
                    1.0,
                    -math.log2(m.pu(bm)),
                    -math.log2(m.pe2(a, bm, a_best)),
                    -math.log2(m.pw(a, bm, a_best, k_best)),
                )
        return sums

    real = _eval_pages(train_lines, test_pl)
    rng = random.Random(3)
    sh_tr = [rng.sample(l, len(l)) for l in train_lines]
    sh_te = [(p, rng.sample(l, len(l))) for p, l in test_pl]
    shuf = _eval_pages(sh_tr, sh_te)

    pages = sorted(real)
    R = np.array([real[p] for p in pages], dtype=np.float64)
    S = np.array([shuf[p] for p in pages], dtype=np.float64)

    r_sum = R.sum(0)
    s_sum = S.sum(0)
    u_real, e2_real, w_real = r_sum[1] / r_sum[0], r_sum[2] / r_sum[0], r_sum[3] / r_sum[0]
    u_shuf, e2_shuf, w_shuf = s_sum[1] / s_sum[0], s_sum[2] / s_sum[0], s_sum[3] / s_sum[0]

    edge_gain_ex = (u_real - e2_real) - (u_shuf - e2_shuf)
    resid_f1 = (e2_real - w_real) - (e2_shuf - w_shuf)
    tot_gain_ex = (u_real - w_real) - (u_shuf - w_shuf)

    brng = np.random.default_rng(SEED)
    ix = brng.integers(0, len(pages), size=(1000, len(pages)))
    r_b = R[ix].sum(1)
    s_b = S[ix].sum(1)
    f1_boots = (r_b[:, 2] - r_b[:, 3]) / r_b[:, 0] - (s_b[:, 2] - s_b[:, 3]) / s_b[:, 0]
    tot_boots = (r_b[:, 1] - r_b[:, 3]) / r_b[:, 0] - (s_b[:, 1] - s_b[:, 3]) / s_b[:, 0]

    return dict(
        u_real=float(u_real),
        e2_real=float(e2_real),
        w_real=float(w_real),
        raw_edge=float(u_real - e2_real),
        raw_resid=float(e2_real - w_real),
        raw_tot=float(u_real - w_real),
        edge_ex=float(edge_gain_ex),
        f1=float(resid_f1),
        f1_ci=(float(np.quantile(f1_boots, 0.025)), float(np.quantile(f1_boots, 0.975))),
        tot_ex=float(tot_gain_ex),
        tot_ci=(float(np.quantile(tot_boots, 0.025)), float(np.quantile(tot_boots, 0.975))),
    )


class S40_Bigram:
    """Exact s40 Witten-Bell bigram model."""

    def __init__(self, lines: list[list[str]]):
        self.uni = Counter(s for ln in lines for s in ln)
        self.N = sum(self.uni.values())
        self.V = len(self.uni)
        self.big = defaultdict(Counter)
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

    def eval_lines(self, test_lines: list[list[str]]) -> tuple[float, float, float]:
        bu = bb = 0.0
        n = 0
        for ln in test_lines:
            for a, b in zip(ln, ln[1:]):
                bu -= math.log2(self.pu(b))
                bb -= math.log2(self.pb(a, b))
                n += 1
        return (bu / n, bb / n, (bu - bb) / n) if n else (float("nan"),) * 3


def compute_charwin_from_words(train_words: list[str], test_words: list[str]) -> float:
    m3 = M_NEW.CharMarkov(train_words, 3)
    c_tr = Counter(train_words)
    N_tr = len(train_words)
    n1 = sum(1 for v in c_tr.values() if v == 1)
    p0 = max(n1, 1) / N_tr

    seen_mass = sum(2.0 ** m3.logp_word(w) for w in c_tr)
    rem_mass = max(1.0 - seen_mass, 1e-12)
    log_renorm = -math.log2(rem_mass)
    log_1_p0_N = math.log2((1.0 - p0) / N_tr)
    log_p0_renorm = math.log2(p0) + log_renorm

    c_te = Counter(test_words)
    N_te = len(test_words)
    bits_c3 = 0.0
    bits_uni = 0.0
    for w, cnt in c_te.items():
        lp_c3 = m3.logp_word(w)
        tr_cnt = c_tr.get(w, 0)
        if tr_cnt > 0:
            lp_uni = log_1_p0_N + math.log2(tr_cnt)
        else:
            lp_uni = log_p0_renorm + lp_c3
        bits_c3 += (-lp_c3) * cnt
        bits_uni += (-lp_uni) * cnt
    return float((bits_uni - bits_c3) / N_te)


def evaluate_stripped_stream(by_stream: dict, train_ids: list[str], held_ids: list[str]) -> dict:
    by_tr = subset_by(by_stream, train_ids)
    by_te = subset_by(by_stream, held_ids)

    lines_tr = [r["words"] for recs in by_tr.values() for r in recs if r["words"]]
    lines_te = [r["words"] for recs in by_te.values() for r in recs if r["words"]]
    test_pl_41 = [(p, r["words"]) for p, recs in by_te.items() for r in recs if r["words"]]

    m_bg = S40_Bigram(lines_tr)
    bu, bb, g_41 = m_bg.eval_lines(lines_te)
    rng_s40 = random.Random(SEED)
    null_g = []
    for _ in range(30):
        sh_tr = [rng_s40.sample(ln, len(ln)) for ln in lines_tr]
        sh_te = [rng_s40.sample(ln, len(ln)) for ln in lines_te]
        null_g.append(S40_Bigram(sh_tr).eval_lines(sh_te)[2])
    g_null_mu = float(np.mean(null_g))
    g_null_sd = float(np.std(null_g))
    g_exc = g_41 - g_null_mu
    g_z = g_exc / (g_null_sd if g_null_sd > 1e-12 else 1e-12)

    f1_g41 = compute_f1_decomposed(lines_tr, test_pl_41, topn=300)
    tr_q, te_q = N1.split(by_stream, "quires")
    f1_quires = compute_f1_decomposed(tr_q, te_q, topn=300)

    pages_te = by_to_pages(by_te)
    mat_te = S37.materialize_lines(pages_te)
    wlen_te = np.array([len(w) for w in mat_te["tokens"]], dtype=np.float64)
    moran_te = S37.moran_1d_with_null(wlen_te, mat_te["line_id"], mat_te["left"], mat_te["right"], seed=SEED, n_draws=500)

    pages_all = by_to_pages(by_stream)
    mat_all = S37.materialize_lines(pages_all)
    wlen_all = np.array([len(w) for w in mat_all["tokens"]], dtype=np.float64)
    moran_all = S37.moran_1d_with_null(wlen_all, mat_all["line_id"], mat_all["left"], mat_all["right"], seed=SEED, n_draws=500)

    edge_te_ex = C3.score(lines_te, C3.EVA)[2]
    lines_all = [r["words"] for recs in by_stream.values() for r in recs if r["words"]]
    edge_all_ex = C3.score(lines_all, C3.EVA)[2]

    train_words = [w for ln in lines_tr for w in ln]
    test_words = [w for ln in lines_te for w in ln]
    cw_41 = compute_charwin_from_words(train_words, test_words)
    cw_all, _, _ = S37.compute_corpus_charwin(pages_all, M_NEW, seed=SEED)

    top300_tr = {w for w, _ in Counter(train_words).most_common(300)}
    map300 = lambda w: w if w in top300_tr else "<RARE>"
    a_te = [mat_te["tokens"][i] for i in mat_te["left"]]
    b_te = [mat_te["tokens"][i] for i in mat_te["right"]]
    mi_te_raw = S37.mi_shuffle_corrected_pairs(a_te, b_te, seed=SEED, n_null=100)
    mi_te_300 = S37.mi_shuffle_corrected_pairs([map300(w) for w in a_te], [map300(w) for w in b_te], seed=SEED, n_null=100)

    a_all = [mat_all["tokens"][i] for i in mat_all["left"]]
    b_all = [mat_all["tokens"][i] for i in mat_all["right"]]
    mi_all_300 = S37.mi_shuffle_corrected_pairs([map300(w) for w in a_all], [map300(w) for w in b_all], seed=SEED, n_null=100)

    return dict(
        ntok_te=len(test_words),
        ntyp_te=len(set(test_words)),
        ntyp_all=len(set(mat_all["tokens"])),
        mean_len_te=float(wlen_te.mean()),
        s40_uni=bu,
        s40_bi=bb,
        s40_gain=g_41,
        s40_exc=g_exc,
        s40_z=g_z,
        f1_g41=f1_g41,
        f1_quires=f1_quires,
        moran_te=moran_te,
        moran_all=moran_all,
        edge_te_ex=edge_te_ex,
        edge_all_ex=edge_all_ex,
        cw_41=cw_41,
        cw_all=cw_all,
        mi_te_raw=mi_te_raw,
        mi_te_300=mi_te_300,
        mi_all_300=mi_all_300,
    )


def run_experiment_2b(by_all: dict, train_ids: list[str], held_ids: list[str], seg, res_2a: dict) -> dict:
    emit("\n" + "=" * 104)
    emit("EXPERIMENT 2B: CANDIDATE 2 STRIPPING TEST — FIXED WRAPPER STRIPPING ON UNTOUCHED MATERIAL (41 HELD-OUT PAGES)")
    emit("=" * 104)

    pm_w3 = res_2a["p_models"]["W3_Pos_Sprev_Cbin_Sec"]
    sm_w3 = res_2a["s_models"]["W3_Pos_Sprev_Cbin_Sec"]

    rules = [
        ("S0_Raw_Full", "Unstripped full surface words w_t"),
        ("S1a_LineEdge_Only", "Strip slot-0 init (p/f/y/d/t/s/o) & final (-m/-g)"),
        ("S1b_LineEdge_Plus_oyds", "Strip slot-0 init, final (-m/-g), and all-slot initial (o/y/d/s)"),
        ("S2a_Strip_Prefix_Only", "Strip full SlotSegmenter Prefix P_t (leave C_t + S_t)"),
        ("S2b_Strip_Suffix_Only", "Strip full SlotSegmenter Suffix S_t (leave P_t + C_t)"),
        ("S2_Strip_Full_SlotSeg_Core", "Strip full SlotSegmenter P_t and S_t (leave Core C_t)"),
        ("S3a_CondStrip_Top1", "Context-conditional: strip P_t/S_t ONLY if Top-1 predicted by W3"),
        ("S3b_CondStrip_Top3", "Context-conditional: strip P_t/S_t ONLY if Top-3 predicted by W3"),
    ]

    res_2b = {}
    for r_name, r_desc in rules:
        by_str = build_stripped_by(by_all, seg, r_name, p_model=pm_w3, s_model=sm_w3)
        res_2b[r_name] = evaluate_stripped_stream(by_str, train_ids, held_ids)

    emit("\n--- 2B-1: Out-of-Sample Metrics on the 41 Held-Out Pages (Models & Segmenter Fitted Strictly on 166 Train Pages) ---")
    hdr1 = (
        f"  {'Rule':26s} | {'Typ41':>5s} {'MeanL':>5s} | "
        f"{'s40_Gain':>8s} {'s40_Ex':>8s} {'s40_z':>6s} | "
        f"{'F1_g41':>8s} {'F1_g41_CI':>19s} | "
        f"{'I_with41':>8s} {'I_ex41':>7s} {'I_p':>5s} | "
        f"{'edge41':>7s} {'CW_41':>7s} {'MI300_ex':>8s}"
    )
    emit(hdr1)
    emit("  " + "-" * (len(hdr1) - 2))
    for r_name, _ in rules:
        r = res_2b[r_name]
        f1g = r["f1_g41"]
        mo = r["moran_te"]
        emit(
            f"  {r_name:26s} | {r['ntyp_te']:5d} {r['mean_len_te']:5.2f} | "
            f"{r['s40_gain']:+8.4f} {r['s40_exc']:+8.4f} {r['s40_z']:+6.1f} | "
            f"{f1g['f1']:+8.4f} [{f1g['f1_ci'][0]:+7.4f}, {f1g['f1_ci'][1]:+7.4f}] | "
            f"{mo['I']:+8.4f} {mo['excess']:+7.4f} {mo['p']:5.3f} | "
            f"{r['edge_te_ex']:+7.4f} {r['cw_41']:+7.4f} {r['mi_te_300']['excess']:+8.4f}"
        )

    emit("\n--- 2B-2: Full-Corpus Reference Metrics & F1 Decomposition (U->E2 Edge Gain vs E2->W Residual vs U->W Total Gain) ---")
    hdr2 = (
        f"  {'Rule':26s} | {'TypAll':>6s} | "
        f"{'Edge(U-E2)_ex':>13s} {'F1(E2-W)_quire':>14s} {'F1_quire_CI':>19s} {'Tot(U-W)_ex':>11s} | "
        f"{'I_all':>7s} {'I_ex':>7s} {'edgeAll':>7s} {'CW_all':>7s} {'MI300_all':>9s}"
    )
    emit(hdr2)
    emit("  " + "-" * (len(hdr2) - 2))
    for r_name, _ in rules:
        r = res_2b[r_name]
        fq = r["f1_quires"]
        mo = r["moran_all"]
        emit(
            f"  {r_name:26s} | {r['ntyp_all']:6d} | "
            f"{fq['edge_ex']:+13.4f} {fq['f1']:+14.4f} [{fq['f1_ci'][0]:+7.4f}, {fq['f1_ci'][1]:+7.4f}] {fq['tot_ex']:+11.4f} | "
            f"{mo['I']:+7.4f} {mo['excess']:+7.4f} {r['edge_all_ex']:+7.4f} {r['cw_all']:+7.4f} {r['mi_all_300']['excess']:+9.4f}"
        )

    emit("\n--- 2B-3: Control Benchmark — What S0 (Full) vs S2 (Core-Only) Does to Latin (cremma_all) & S28 Generator ---")
    emit(
        f"  {'Control_Stream':30s} | {'TypTe':>5s} | {'s40_Gain':>8s} {'s40_Ex':>8s} {'s40_z':>6s} | "
        f"{'Edge(U-E2)_ex':>13s} {'F1(E2-W)_ex':>12s} {'Tot(U-W)_ex':>11s} | {'I_with':>7s} {'edge_ex':>7s} {'CW':>7s}"
    )
    emit("  " + "-" * 124)

    _, lat_pages_raw = R_V2.load_meta(VOY_ROOT / "data" / "controls_realline" / "cremma_all.meta.json")
    lat_pages = R_V2.subsample(lat_pages_raw, 25000)
    by_lat = OrderedDict()
    for i, p in enumerate(lat_pages):
        by_lat[p["id"]] = [
            dict(page=p["id"], words=list(ln), hand="1", illus="L", quire=str(i // 4), lang="L", para_start=(j == 0))
            for j, ln in enumerate(p["lines"])
            if ln
        ]
    lat_tr_ids, lat_te_ids = G1.split_names(by_lat)
    seg_lat = M_NEW.SlotSegmenter([w for pid in lat_tr_ids for r in by_lat[pid] for w in r["words"]])
    for r_code in ["S0_Raw_Full", "S2_Strip_Full_SlotSeg_Core"]:
        bs_lat = build_stripped_by(by_lat, seg_lat, r_code)
        ev_lat = evaluate_stripped_stream(bs_lat, lat_tr_ids, lat_te_ids)
        fg = ev_lat["f1_g41"]
        emit(
            f"  {'Latin_cremma_' + r_code[:6]:30s} | {ev_lat['ntyp_te']:5d} | "
            f"{ev_lat['s40_gain']:+8.4f} {ev_lat['s40_exc']:+8.4f} {ev_lat['s40_z']:+6.1f} | "
            f"{fg['edge_ex']:+13.4f} {fg['f1']:+12.4f} {fg['tot_ex']:+11.4f} | "
            f"{ev_lat['moran_all']['I']:+7.4f} {ev_lat['edge_all_ex']:+7.4f} {ev_lat['cw_all']:+7.4f}"
        )

    s28_p1 = VOY_ROOT / "runs" / "s28" / "s28_gen_ZL3b_s1.meta.json"
    if s28_p1.exists():
        d_s28 = json.loads(s28_p1.read_text(encoding="utf-8"))
        by_s28 = OrderedDict()
        for p in d_s28["pages"]:
            by_s28[p["id"]] = [
                dict(
                    page=p["id"],
                    words=list(ln),
                    hand=str(p.get("hand", "1")),
                    illus=str(p.get("section", "H")),
                    quire=p.get("quire", "Q1"),
                    lang=str(p.get("lang", "B")),
                    para_start=(j == 0),
                )
                for j, ln in enumerate(p["lines"])
                if ln
            ]
        for r_code in ["S0_Raw_Full", "S2_Strip_Full_SlotSeg_Core"]:
            bs_28 = build_stripped_by(by_s28, seg, r_code)
            ev_28 = evaluate_stripped_stream(bs_28, train_ids, held_ids)
            fg = ev_28["f1_g41"]
            emit(
                f"  {'s28_gen_s1_' + r_code[:6]:30s} | {ev_28['ntyp_te']:5d} | "
                f"{ev_28['s40_gain']:+8.4f} {ev_28['s40_exc']:+8.4f} {ev_28['s40_z']:+6.1f} | "
                f"{fg['edge_ex']:+13.4f} {fg['f1']:+12.4f} {fg['tot_ex']:+11.4f} | "
                f"{ev_28['moran_all']['I']:+7.4f} {ev_28['edge_all_ex']:+7.4f} {ev_28['cw_all']:+7.4f}"
            )

    flush_out()
    return res_2b


# ==============================================================================
# EXPERIMENT 2C: Direct C1 vs C2 Discriminator (Vertical Line n-1 vs Horizontal w_{t-1})
# ==============================================================================
def run_experiment_2c(by_all: dict, train_ids: list[str], held_ids: list[str], seg) -> None:
    emit("\n" + "=" * 104)
    emit("EXPERIMENT 2C: DIRECT C1 (PROCEDURAL LOCAL MEMORY) VS C2 (MEANINGFUL CORE STREAM) DISCRIMINATOR")
    emit("=" * 104)

    emit("\n--- 2C-i: Resolving the S39 vs S40 Paradox — F1 Decomposition on Full, Prefix-Only, Core-Only, Suffix-Only ---")
    emit("  Note: F1 (n1_habit_table.residual) measures ONLY E2 - W (bits bought by full prev token beyond its last 2 chars).")
    emit("        Because 27/27 prefix candidates have length 1..3, prev[-2:] ALREADY identifies the prefix!")
    emit(
        f"  {'Layer_Stream':24s} | {'Types':>5s} | {'Edge(U-E2)_raw':>14s} {'Edge(U-E2)_ex':>13s} | "
        f"{'F1(E2-W)_raw':>12s} {'F1(E2-W)_ex':>12s} {'F1_CI':>19s} | {'Tot(U-W)_ex':>11s}"
    )
    emit("  " + "-" * 122)

    for s_name, slot_idx in [
        ("full (w_t)", None),
        ("prefix-only (keep ∅)", 0),
        ("core-only (C_t)", 1),
        ("suffix-only (keep ∅)", 2),
    ]:
        bs = OrderedDict()
        for p, recs in by_all.items():
            nr = []
            for r in recs:
                if slot_idx is None:
                    ws = list(r["words"])
                else:
                    ws = [(seg.segment(w)[slot_idx] or EMPTY) for w in r["words"]]
                nr.append(dict(r, words=ws))
            bs[p] = nr
        tr_q, te_q = N1.split(bs, "quires")
        fd = compute_f1_decomposed(tr_q, te_q, topn=300)
        ntyp = len({w for recs in bs.values() for r in recs for w in r["words"]})
        emit(
            f"  {s_name:24s} | {ntyp:5d} | {fd['raw_edge']:+14.4f} {fd['edge_ex']:+13.4f} | "
            f"{fd['raw_resid']:+12.4f} {fd['f1']:+12.4f} [{fd['f1_ci'][0]:+7.4f}, {fd['f1_ci'][1]:+7.4f}] | {fd['tot_ex']:+11.4f}"
        )

    emit("\n--- 2C-ii: Extended Vertical Line n-1 Same-x Recency Analysis (204 Aligned Pages, 200 Line-Perm Draws) ---")
    emit("  Tests what s42's lev(w,c)<=1 filter missed: (1) What are the 319 'other' lev<=1 hits?")
    emit("  (2) Does vertical same-x recency copy the CORE when the wrapper changes by >=2 chars (lev(w,c)>=2)?")
    emit("  (3) Does vertical same-x recency copy the WRAPPER (P,S) when the core changes by >=2 chars (lev(C_w,C_c)>=2)?")

    pages_m1, _ = M1.build_pages()
    all_m1_words = [t["word"] for pg in pages_m1.values() for _, toks in pg["lines"] for t in toks if M1.ok_word(t["word"])]
    seg_m1_full = M_NEW.SlotSegmenter(M_NEW.flat_tokens(M_NEW.voynich_pages("eva")))
    seg_cache_m1 = {w: seg_m1_full.segment(w) for w in set(all_m1_words)}

    EXT_CATS = [
        "1_lev0_exact_word",
        "2_lev1_same_core_chg_aff",
        "3_lev1_same_aff_chg_core",
        "4_lev1_other_seg_shift",
        "5_lev2p_EXACT_CORE_chg_aff",
        "6_lev2p_EXACT_AFF_chg_core",
        "7_any_EXACT_CORE_diff_word",
        "8_any_EXACT_PREFIX_nonempty",
        "9_any_EXACT_SUFFIX_nonempty",
        "10_lev1_CORE_regardless_aff",
    ]

    def classify_pair_ext(w: str, c: str) -> list[str]:
        pw, kw, sw = seg_cache_m1[w]
        pc, kc, sc = seg_cache_m1[c]
        ex, e1 = M1.score(w, c)
        tags = []
        if ex:
            tags.append("1_lev0_exact_word")
        elif e1:
            if kw == kc and (pw, sw) != (pc, sc):
                tags.append("2_lev1_same_core_chg_aff")
            elif (pw, sw) == (pc, sc) and kw != kc:
                tags.append("3_lev1_same_aff_chg_core")
            else:
                tags.append("4_lev1_other_seg_shift")
        else:
            if kw == kc and (pw, sw) != (pc, sc):
                tags.append("5_lev2p_EXACT_CORE_chg_aff")
            if (pw, sw) == (pc, sc) and (pw or sw) and kw != kc:
                tags.append("6_lev2p_EXACT_AFF_chg_core")

        if w != c and kw == kc:
            tags.append("7_any_EXACT_CORE_diff_word")
        if pw and pw == pc:
            tags.append("8_any_EXACT_PREFIX_nonempty")
        if sw and sw == sc:
            tags.append("9_any_EXACT_SUFFIX_nonempty")
        if kw != kc and M1.lev_le1(kw, kc):
            tags.append("10_lev1_CORE_regardless_aff")
        return tags

    def count_vertical(prev_of_fn):
        probes = 0
        hits = Counter()
        examples_other = []
        for f, pg in pages_m1.items():
            W = pg["W"]
            by_no = {no: toks for no, toks in pg["lines"]}
            nos = sorted(by_no)
            for no in nos:
                cur = [t for t in by_no[no] if M1.ok_word(t["word"])]
                if not cur:
                    continue
                cline = prev_of_fn(by_no, nos, no)
                if not cline:
                    continue
                cands = [t for t in cline if M1.ok_word(t["word"])]
                if not cands:
                    continue
                for tok in cur:
                    w = tok["word"]
                    d, c = M1.nearest(tok, cands)
                    if d <= 0.5 * W:
                        probes += 1
                        tgs = classify_pair_ext(w, c["word"])
                        for tg in tgs:
                            hits[tg] += 1
                        if "4_lev1_other_seg_shift" in tgs and len(examples_other) < 12:
                            examples_other.append((w, seg_cache_m1[w], c["word"], seg_cache_m1[c["word"]]))
        return probes, hits, examples_other

    probes_obs, hits_obs, ex_other = count_vertical(lambda by_no, nos, no: by_no.get(no - 1))
    rng_v = random.Random(SEED)
    null_hits = {k: [] for k in EXT_CATS}
    null_probes = []
    for _ in range(200):
        def _rand_prev(by_no, nos, no, _r=rng_v):
            others = [m for m in nos if m != no]
            return by_no[_r.choice(others)] if others else None

        p_n, h_n, _ = count_vertical(_rand_prev)
        null_probes.append(p_n)
        for k in EXT_CATS:
            null_hits[k].append(h_n[k])

    emit(f"  Aligned same-x probes (d <= 0.5W): obs = {probes_obs}, null mean = {np.mean(null_probes):.1f}")
    emit(f"  {'Category':30s} | {'Obs':>6s} | {'Null_Mean':>9s} {'Null_SD':>7s} | {'Excess':>8s} {'z':>7s} {'p':>7s} | {'Obs%':>6s} {'Null%':>6s}")
    emit("  " + "-" * 100)
    mean_np = float(np.mean(null_probes))
    for k in EXT_CATS:
        arr = np.array(null_hits[k], dtype=float)
        mu, sd = float(arr.mean()), float(arr.std())
        obs_v = hits_obs[k]
        exc_raw = obs_v - mu
        z_raw = exc_raw / sd if sd > 0 else 0.0
        p_raw = (1 + int((arr >= obs_v).sum())) / 201.0
        obs_pct = 100.0 * obs_v / probes_obs
        nul_pct = 100.0 * mu / mean_np
        emit(
            f"  {k:30s} | {obs_v:6d} | {mu:9.1f} {sd:7.1f} | {exc_raw:+8.1f} {z_raw:+7.2f} {p_raw:7.3f} | {obs_pct:5.2f}% {nul_pct:5.2f}%"
        )

    emit("\n  Concrete examples of Category 4 ('other' lev<=1 hits in s42 — showing segmentation boundary shifts):")
    for w, sw_t, c, sc_t in ex_other[:8]:
        emit(f"    line_n='{w}' {sw_t}  <-->  line_n-1='{c}' {sc_t}")

    emit("\n--- 2C-iii: Horizontal Core-to-Core (C_{t-1} -> C_t) Predictability Under Progressive Copy-Mutate Ablations ---")
    emit("  Evaluates held-out Witten-Bell core bigram EXCESS over within-line shuffle (166 train -> 41 held-out pages)")
    emit("  as local procedural copy-mutate pairs are progressively masked out from evaluation:")
    emit(
        f"  {'Ablation_Filter_on_Test_Pairs':38s} | "
        f"{'Voy_Pairs':>9s} {'Voy_Ex(b)':>10s} {'Voy_z':>7s} | "
        f"{'Lat_Pairs':>9s} {'Lat_Ex(b)':>10s} {'Lat_z':>7s} | "
        f"{'s28_Pairs':>9s} {'s28_Ex(b)':>10s} {'s28_z':>7s}"
    )
    emit("  " + "-" * 124)

    def eval_core_ablation_suite(by_corpus: dict, tr_ids: list[str], te_ids: list[str], seg_c):
        by_tr = subset_by(by_corpus, tr_ids)
        by_te = subset_by(by_corpus, te_ids)

        def _extract_line_tuples(by_sub):
            lines_out = []
            for p, recs in by_sub.items():
                prev_line_words = []
                for r in recs:
                    ws = r["words"]
                    if not ws:
                        continue
                    tups = []
                    for idx, w in enumerate(ws):
                        pr, cr, sr = seg_c.segment(w)
                        vert_hit = False
                        if prev_line_words:
                            j_est = int(round(idx * (len(prev_line_words) - 1) / max(1, len(ws) - 1)))
                            for j in range(max(0, j_est - 1), min(len(prev_line_words), j_est + 2)):
                                pw_cand = prev_line_words[j]
                                if w == pw_cand or M1.lev_le1(w, pw_cand) or seg_c.segment(pw_cand)[1] == cr:
                                    vert_hit = True
                                    break
                        tups.append((w, pr, cr, sr, vert_hit))
                    lines_out.append(tups)
                    prev_line_words = ws
            return lines_out

        tr_tups = _extract_line_tuples(by_tr)
        te_tups = _extract_line_tuples(by_te)

        filters = [
            ("F0_All_Adjacent_Core_Pairs", lambda a, b: True),
            ("F1_Drop_Exact_Core_Repeat (C1!=C2)", lambda a, b: a[2] != b[2]),
            (
                "F2_Drop_Lev1_Word_or_Core_Mutate",
                lambda a, b: (a[2] != b[2]) and (not M1.lev_le1(a[0], b[0])) and (not M1.lev_le1(a[2], b[2])),
            ),
            (
                "F3_Drop_Edge_Char_Match (C1[-1]!=C2[0])",
                lambda a, b: (a[2] != b[2])
                and (not M1.lev_le1(a[0], b[0]))
                and (not M1.lev_le1(a[2], b[2]))
                and (a[2][-1:] != b[2][:1]),
            ),
            (
                "F4_Drop_Vertical_Line_n-1_Echoes",
                lambda a, b: (a[2] != b[2])
                and (not M1.lev_le1(a[0], b[0]))
                and (not M1.lev_le1(a[2], b[2]))
                and (a[2][-1:] != b[2][:1])
                and (not b[4]),
            ),
            (
                "F5_Strictly_Disjoint_Cores (no char2)",
                lambda a, b: (a[2] != b[2])
                and (not M1.lev_le1(a[0], b[0]))
                and (not M1.lev_le1(a[2], b[2]))
                and (a[2][-1:] != b[2][:1])
                and (not b[4])
                and (len({a[2][k : k + 2] for k in range(len(a[2]) - 1)} & {b[2][k : k + 2] for k in range(len(b[2]) - 1)}) == 0),
            ),
        ]

        tr_core_lines = [[t[2] for t in ln] for ln in tr_tups]
        m_real = S40_Bigram(tr_core_lines)

        rng_ab = random.Random(SEED)
        shuf_models_and_lines = []
        for _ in range(30):
            sh_tr = [[t[2] for t in rng_ab.sample(ln, len(ln))] for ln in tr_tups]
            sh_te = [rng_ab.sample(ln, len(ln)) for ln in te_tups]
            shuf_models_and_lines.append((S40_Bigram(sh_tr), sh_te))

        out_f = {}
        for f_name, pred in filters:
            bu = bb = 0.0
            n_p = 0
            for ln in te_tups:
                for a, b in zip(ln, ln[1:]):
                    if pred(a, b):
                        bu -= math.log2(m_real.pu(b[2]))
                        bb -= math.log2(m_real.pb(a[2], b[2]))
                        n_p += 1
            gain_real = (bu - bb) / max(1, n_p)

            null_gains = []
            for m_sh, sh_te in shuf_models_and_lines:
                s_bu = s_bb = 0.0
                s_n = 0
                for ln in sh_te:
                    for a, b in zip(ln, ln[1:]):
                        if pred(a, b):
                            s_bu -= math.log2(m_sh.pu(b[2]))
                            s_bb -= math.log2(m_sh.pb(a[2], b[2]))
                            s_n += 1
                null_gains.append((s_bu - s_bb) / max(1, s_n))
            mu_n = float(np.mean(null_gains))
            sd_n = float(np.std(null_gains))
            exc = gain_real - mu_n
            z = exc / (sd_n if sd_n > 1e-12 else 1e-12)
            out_f[f_name] = dict(n=n_p, gain=gain_real, null_mu=mu_n, exc=exc, z=z)
        return out_f

    _, lat_pages_raw = R_V2.load_meta(VOY_ROOT / "data" / "controls_realline" / "cremma_all.meta.json")
    lat_pages = R_V2.subsample(lat_pages_raw, 25000)
    by_lat = OrderedDict(
        (
            p["id"],
            [
                dict(page=p["id"], words=list(ln), hand="1", illus="L", quire=str(i // 4), lang="L", para_start=(j == 0))
                for j, ln in enumerate(p["lines"])
                if ln
            ],
        )
        for i, p in enumerate(lat_pages)
    )
    lat_tr_ids, lat_te_ids = G1.split_names(by_lat)
    seg_lat = M_NEW.SlotSegmenter([w for pid in lat_tr_ids for r in by_lat[pid] for w in r["words"]])

    d_s28 = json.loads((VOY_ROOT / "runs" / "s28" / "s28_gen_ZL3b_s1.meta.json").read_text(encoding="utf-8"))
    by_s28 = OrderedDict(
        (
            p["id"],
            [
                dict(
                    page=p["id"],
                    words=list(ln),
                    hand=str(p.get("hand", "1")),
                    illus=str(p.get("section", "H")),
                    quire=p.get("quire", "Q1"),
                    lang=str(p.get("lang", "B")),
                    para_start=(j == 0),
                )
                for j, ln in enumerate(p["lines"])
                if ln
            ],
        )
        for p in d_s28["pages"]
    )

    ab_voy = eval_core_ablation_suite(by_all, train_ids, held_ids, seg)
    ab_lat = eval_core_ablation_suite(by_lat, lat_tr_ids, lat_te_ids, seg_lat)
    ab_s28 = eval_core_ablation_suite(by_s28, train_ids, held_ids, seg)

    for f_name in ab_voy:
        v = ab_voy[f_name]
        l = ab_lat[f_name]
        s = ab_s28[f_name]
        emit(
            f"  {f_name:38s} | "
            f"{v['n']:9d} {v['exc']:+10.4f} {v['z']:+7.2f} | "
            f"{l['n']:9d} {l['exc']:+10.4f} {l['z']:+7.2f} | "
            f"{s['n']:9d} {s['exc']:+10.4f} {s['z']:+7.2f}"
        )

    emit("\n--- 2C-iv: Concrete Cross-Sample Core Transitions (C_{t-1} -> C_t) Shared Between 166 Train & 41 Held-Out Pages ---")
    by_tr = subset_by(by_all, train_ids)
    by_te = subset_by(by_all, held_ids)

    tr_c_pairs = Counter()
    tr_c_uni = Counter()
    for recs in by_tr.values():
        for r in recs:
            cs = [seg.segment(w)[1] for w in r["words"]]
            tr_c_uni.update(cs)
            for a, b in zip(cs, cs[1:]):
                tr_c_pairs[(a, b)] += 1

    te_c_pairs = Counter()
    te_c_uni = Counter()
    for recs in by_te.values():
        for r in recs:
            cs = [seg.segment(w)[1] for w in r["words"]]
            te_c_uni.update(cs)
            for a, b in zip(cs, cs[1:]):
                te_c_pairs[(a, b)] += 1

    N_tr_p = sum(tr_c_pairs.values())
    N_te_p = sum(te_c_pairs.values())
    N_tr_u = sum(tr_c_uni.values())
    N_te_u = sum(te_c_uni.values())

    shared_c_pairs = []
    for (a, b), c_te in te_c_pairs.items():
        c_tr = tr_c_pairs.get((a, b), 0)
        if c_tr >= 5 and c_te >= 3 and a != b:
            pmi_tr = math.log2((c_tr / N_tr_p) / ((tr_c_uni[a] / N_tr_u) * (tr_c_uni[b] / N_tr_u)))
            pmi_te = math.log2((c_te / N_te_p) / ((te_c_uni[a] / N_te_u) * (te_c_uni[b] / N_te_u)))
            if pmi_tr > 0.3 and pmi_te > 0.3:
                shared_c_pairs.append((c_te * pmi_te, a, b, c_tr, c_te, pmi_tr, pmi_te, M1.lev_le1(a, b), a[-1:] == b[:1]))

    shared_c_pairs.sort(reverse=True)
    emit(
        f"  {'C_{t-1} -> C_t':22s} | {'Tr_Cnt':>6s} {'Te_Cnt':>6s} | {'PMI_Train':>9s} {'PMI_Test':>8s} | "
        f"{'Lev<=1':>6s} {'EdgeEq':>6s} | Mechanism Diagnosis"
    )
    emit("  " + "-" * 98)
    for _, a, b, c_tr, c_te, p_tr, p_te, is_l1, is_eq in shared_c_pairs[:15]:
        diag = []
        if is_l1:
            diag.append("1-edit core mutation")
        if is_eq:
            diag.append(f"shared boundary char '{a[-1]}'")
        if b.startswith("k") or b.startswith("t") or b.startswith("p") or b.startswith("f"):
            diag.append("unsegmented initial gallows in C2")
        if a.endswith("y") or a.endswith("r") or a.endswith("l") or a.endswith("n"):
            diag.append(f"unsegmented final '{a[-1]}' in C1")
        if not diag:
            diag.append("disjoint lexical/core collocation")
        emit(
            f"  {a + ' -> ' + b:22s} | {c_tr:6d} {c_te:6d} | {p_tr:+9.3f} {p_te:+8.3f} | "
            f"{str(is_l1):>6s} {str(is_eq):>6s} | {', '.join(diag)}"
        )

    flush_out()


def main() -> int:
    t0 = time.time()
    # Mirror script to parent scratch dir as requested
    try:
        PARENT_SCRATCH.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(__file__), PARENT_SCRATCH / "exp_c1_vs_c2_edge_rule.py")
    except Exception:
        pass

    emit("=" * 104)
    emit("SUBAGENT 2 REPORT: CANDIDATE 1 (PROCEDURAL LOCAL MEMORY) VS CANDIDATE 2 (MEANINGFUL TEXT + WRAPPER)")
    emit("Out-of-Sample Fixed Wrapper Rule Prediction, Stripping Test, and Horizontal vs Vertical Memory")
    emit("=" * 104)

    by_all = load_zl3b_with_para()
    train_ids, held_ids = G1.split_names(by_all)
    toks_tr = [w for p in train_ids for r in by_all[p] for w in r["words"]]
    toks_te = [w for p in held_ids for r in by_all[p] for w in r["words"]]
    seg = M_NEW.SlotSegmenter(toks_tr)

    emit(
        f"Dataset: ZL3b_eva | Total pages={len(by_all)} ({len(toks_tr) + len(toks_te)} tokens) | "
        f"Train={len(train_ids)} pages ({len(toks_tr)} tokens) | Held-out={len(held_ids)} pages ({len(toks_te)} tokens)"
    )
    emit(
        f"Train-166 SlotSegmenter: {len(seg.prefixes)} prefixes {sorted(seg.prefixes)}, "
        f"{len(seg.suffixes)} suffixes {sorted(seg.suffixes)}"
    )

    res_2a = run_experiment_2a(by_all, train_ids, held_ids, seg)
    run_experiment_2b(by_all, train_ids, held_ids, seg, res_2a)
    run_experiment_2c(by_all, train_ids, held_ids, seg)

    emit("\n" + "=" * 104)
    emit(f"COMPLETED ALL EXPERIMENTS (2A, 2B, 2C) IN {time.time() - t0:.1f}s.")
    emit(f"Output saved to {OUT_FILE_PARENT} and {OUT_FILE_OWN}")
    emit("=" * 104)
    flush_out()
    return 0


if __name__ == "__main__":
    sys.exit(main())
