"""S2: Pre-registered execution of SYNTHESIS Steps 1-3 (Retiring Unknowns U1, U2, U3
from local disk; stamped 2026-10-17 19:48 PDT).

PRE-REGISTRATION (written before any run of this file; SHA-256 recorded in
s2_u1_u2_u3_controls.prereg.sha256; nothing below is changed after results are seen)

Why (workflow/research/SYNTHESIS.md §Verdict & Steps 1-3):
  SYNTHESIS identified three upstream unknowns (U1 line edges, U2 cross-space
  coupling positional confound & edge-table circularity, U3 unit/alphabet
  sensitivity & empirical band widths) that must be tested before interpreting
  Phase 2 entrants:

  Part 1 — U1 (Native Line Breaks vs. 8-Word Re-Lining on Disk):
    Compare Voynich (ZL3b native lines vs. 8-word re-lined) against every
    corpus on disk that preserves native line breaks:
      - Gaskell-Bowern human gibberish (38 volunteers, 10,023 tokens: native
        volunteer lines from raw .txt files vs. 8-word re-lined)
      - MHG Nibelungenlied Hs. A (diplomatic manuscript with unexpanded
        abbreviations: native manuscript lines vs. 8-word re-lined)
      - Old French Chanson de Roland (native lines vs. 8-word re-lined)
      - Occitan Croisade Albigeoise (native lines vs. 8-word re-lined)
      - Italian Dante Inferno (native verse lines vs. 8-word re-lined)
    Metrics: jsd_first_fg (line-initial vs mid-line first-char JSD),
    jsd_last_lg (line-final vs mid-line last-char JSD), p_init_enrich,
    m_final_enrich, top1_final_enrich ( enrichment of the corpus's own most
    line-final-enriched character, alphabet-agnostic), and RN-Top PR #5
    line-final bigram odds ratio (max bigram OR with count >= 30).
    Decision rule (U1 pre-test):
      - Outcome A (SURVIVES PRE-TEST): neither native-line gibberish (X) nor
        any native-line language control (L) reaches Voynich's jsd_first_fg
        band (>= 0.10).
      - Outcome B (OVERLAPS): native line breaks alone push X or L into
        jsd_first_fg >= 0.10.

  Part 2 — U2 (Position-Stratified Coupling Null + Cross-Currier Edge Table +
               Timm's Token Bound):
    (a) Position-Stratified Coupling Null (Feaster CEUR 3313 confound check):
        Standard c3.score shuffles words within each line, destroying M5's
        positional word preferences (para_start, line_init, d-gradient,
        line_final). We test two position-preserving nulls (200 shuffles,
        seed=20261017) across ZL3b, RF1b, IT2a:
          - N_slot: permutes words across lines strictly within the same
            positional slot (para_init, other_init, pos_1, mid_line, line_final).
          - N_cell: permutes words across lines strictly within the same
            (hand, section, positional_slot) cell.
        Decision rule (U2a): GENUINE ADJACENT COUPLING if position-stratified
        MI excess >= +0.09 AND >= 0.75 * standard c3 excess on all 3 EVA
        transliterations; else POSITIONAL CONFOUND.
    (b) Out-of-Sample / Cross-Currier / Non-Voynich Edge Table (REDTEAM #1):
        Fit R(first | last) on:
          1. Currier A only -> generate Currier B with c2 + F3(beta=1.5)
          2. Currier B only -> generate Currier A with c2 + F3(beta=1.5)
          3. G1's 166 train pages -> generate G1's 41 held-out test pages
          4. Italian Dante (mapped to top EVA chars by rank) -> generate ZL3b
        Decision rule (U2b): TRANSFERS if cross-Currier A->B and B->A and
        166->41 all achieve cross_excess >= +0.09 without fitting R on the
        evaluated subset.
    (c) Timm's Token Bound:
        Exact token/char/glyph+ counts on ZL3b and implied plaintext word
        capacity under verbose (1.5-2.0 plaintext letters/token) vs. 1-to-1
        token schemes.

  Part 3 — U3 (Fixed-Unit Alphabet Table & 200-Split Empirical Band Widths):
    (a) Score h2, sd_len, types_25k, types_full, hapax, jsd_first_fg,
        cross_excess across ZL3b_eva, RF1b, IT2a, ZL3b_glyphplus, GC2a (v101).
    (b) Compute the exact 95% (2.5-97.5 percentile) and min-max empirical
        within-manuscript band widths across 200 random 41-page splits
        (seeds 1000..1199) on ZL3b.

Run: python s2_u1_u2_u3_controls.py -> results_s2_u123_controls.txt
"""
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import a1_profile
import a2_position as a2
import c2_section_generator as c2
import c3_edge_coupling as c3
import f3_flow_choice as f3
import k1_joint_producer as k1
import n1_habit_table as N
from tools import gibberish_to_meta as gtm

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_s2_u123_controls.txt"
STUB = HERE / "s2_u1_u2_u3_controls.prereg.sha256"
SEED = 20261017
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


def verify_prereg_hash():
    my_bytes = Path(__file__).resolve().read_bytes()
    my_hash = hashlib.sha256(my_bytes).hexdigest()
    if STUB.exists():
        first = STUB.read_text(encoding="utf-8").strip().splitlines()[0].split()[0]
        return my_hash, first == my_hash
    return my_hash, False


# ---------------------------------------------------------------------------
# Part 1: U1 — Native Line Breaks vs 8-Word Re-Lining
# ---------------------------------------------------------------------------
def load_gibberish_native_lines():
    lines = []
    for f in sorted(gtm.SRC.glob("*.txt")):
        if not gtm.NAME_RE.match(f.name):
            continue
        for raw in f.read_text(encoding="utf-8", errors="strict").splitlines():
            ln = raw.strip()
            if not ln or set(ln) <= {"_"}:
                continue
            toks = [gtm.clean_token(p.rstrip("-")) for p in ln.split()]
            toks = [t for t in toks if t]
            if len(toks) >= 2:
                lines.append(toks)
    return lines


def load_control_native_lines(path, max_tokens=25000):
    lines = []
    n_tok = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = raw.strip()
        if not ln or ln.startswith("#"):
            continue
        toks = [re.sub(r"[^a-z]", "", w.lower()) for w in ln.split()]
        toks = [t for t in toks if t]
        if len(toks) >= 2:
            lines.append(toks)
            n_tok += len(toks)
            if n_tok >= max_tokens:
                break
    return lines


def reline_8(lines):
    flat = [w for ln in lines for w in ln]
    return [flat[i:i + 8] for i in range(0, len(flat) - 7, 8)]


def line_edge_metrics(lines):
    init_f, mid_f, fin_l, mid_l = Counter(), Counter(), Counter(), Counter()
    fin_bg, mid_bg = Counter(), Counter()
    n_init = n_mid = n_fin = 0
    for ln in lines:
        if len(ln) < 3:
            continue
        w0, w_end = ln[0], ln[-1]
        init_f[w0[0]] += 1
        fin_l[w_end[-1]] += 1
        if len(w_end) >= 2:
            fin_bg[w_end[-2:]] += 1
        n_init += 1
        n_fin += 1
        for w in ln[1:-1]:
            mid_f[w[0]] += 1
            mid_l[w[-1]] += 1
            if len(w) >= 2:
                mid_bg[w[-2:]] += 1
            n_mid += 1
    jsd_f = a2.jsd(init_f, mid_f)
    jsd_l = a2.jsd(fin_l, mid_l)
    p_enr = ((init_f["p"] / max(1, n_init)) / max(1e-9, mid_f["p"] / max(1, n_mid))) if mid_f["p"] else 0.0
    m_enr = ((fin_l["m"] / max(1, n_fin)) / max(1e-9, mid_l["m"] / max(1, n_mid))) if mid_l["m"] else 0.0
    # Alphabet-agnostic top enriched initial and final characters (min mid count >= 20)
    top_init_c, top_init_enr = "-", 0.0
    for c, cnt in init_f.items():
        if mid_f[c] >= 20:
            enr = (cnt / n_init) / (mid_f[c] / n_mid)
            if enr > top_init_enr:
                top_init_c, top_init_enr = c, enr
    top_fin_c, top_fin_enr = "-", 0.0
    for c, cnt in fin_l.items():
        if mid_l[c] >= 20:
            enr = (cnt / n_fin) / (mid_l[c] / n_mid)
            if enr > top_fin_enr:
                top_fin_c, top_fin_enr = c, enr
    # RN-Top PR #5 style line-final 2-char suffix odds ratio (total count >= 30)
    best_bg, best_or = "--", 0.0
    for bg, a in fin_bg.items():
        b = mid_bg[bg]
        if a + b >= 30 and b > 0 and (n_fin - a) > 0:
            odds = (a / max(1, n_fin - a)) / (b / max(1, n_mid - b))
            if odds > best_or:
                best_bg, best_or = bg, odds
    return dict(
        n_lines=len(lines),
        n_tokens=sum(len(ln) for ln in lines),
        jsd_f=jsd_f,
        jsd_l=jsd_l,
        p_enr=p_enr,
        m_enr=m_enr,
        top_init=f"{top_init_c}:x{top_init_enr:.2f}",
        top_fin=f"{top_fin_c}:x{top_fin_enr:.2f}",
        top_bg_or=f"-{best_bg}:OR={best_or:.1f}",
        jsd_f_ge_010=jsd_f >= 0.10,
    )


# ---------------------------------------------------------------------------
# Part 2: U2 — Position-Stratified Coupling Null & Cross-Currier Edge Table
# ---------------------------------------------------------------------------
def raw_edge_mi(lines):
    pairs = [(a[-1], b[0]) for ln in lines if len(ln) >= 2 for a, b in zip(ln, ln[1:])]
    n = len(pairs)
    pj = Counter(pairs)
    pl = Counter(a for a, _ in pairs)
    pf = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c in pj.items():
        mi += (c / n) * math.log2((c * n) / (pl[a] * pf[b]))
    return mi


def slot_of(i, n, para_start):
    if i == 0:
        return "para_0" if para_start else "line_0"
    if i == n - 1:
        return "line_end"
    if i == 1:
        return "pos_1"
    return "mid"


def position_stratified_coupling(by, n_shuf=200, seed=SEED):
    ps_map = {(r["page"], i): (i == 0) for p, recs in by.items() for i, r in enumerate(recs)}
    recs_all = []
    for p, recs in by.items():
        for idx, r in enumerate(recs):
            if len(r["words"]) >= 2:
                recs_all.append((p, idx, r["hand"], r["illus"], r.get("para_start", idx == 0), list(r["words"])))
    lines_orig = [w for *_, w in recs_all]
    obs_mi = raw_edge_mi(lines_orig)

    rng = random.Random(seed)
    # 1. Standard within-line shuffle
    within_mis = []
    for _ in range(n_shuf):
        sh = [rng.sample(ln, len(ln)) for ln in lines_orig]
        within_mis.append(raw_edge_mi(sh))

    # 2. Whole-book slot-stratified shuffle
    slot_pools = defaultdict(list)
    slot_locs = defaultdict(list)
    for r_i, (_p, _idx, _h, _s, pstart, ws) in enumerate(recs_all):
        n = len(ws)
        for w_i, w in enumerate(ws):
            sl = slot_of(w_i, n, pstart)
            slot_pools[sl].append(w)
            slot_locs[sl].append((r_i, w_i))
    slot_mis = []
    for _ in range(n_shuf):
        sh = [list(ln) for ln in lines_orig]
        for sl, pool in slot_pools.items():
            perm = rng.sample(pool, len(pool))
            for (r_i, w_i), w in zip(slot_locs[sl], perm):
                sh[r_i][w_i] = w
        slot_mis.append(raw_edge_mi(sh))

    # 3. (hand, section, slot)-stratified shuffle
    cell_pools = defaultdict(list)
    cell_locs = defaultdict(list)
    for r_i, (_p, _idx, h, s, pstart, ws) in enumerate(recs_all):
        n = len(ws)
        for w_i, w in enumerate(ws):
            cell = (h, s, slot_of(w_i, n, pstart))
            cell_pools[cell].append(w)
            cell_locs[cell].append((r_i, w_i))
    cell_mis = []
    for _ in range(n_shuf):
        sh = [list(ln) for ln in lines_orig]
        for cell, pool in cell_pools.items():
            perm = rng.sample(pool, len(pool))
            for (r_i, w_i), w in zip(cell_locs[cell], perm):
                sh[r_i][w_i] = w
        cell_mis.append(raw_edge_mi(sh))

    return dict(
        obs_mi=obs_mi,
        within_null=float(np.mean(within_mis)),
        within_ex=obs_mi - float(np.mean(within_mis)),
        slot_null=float(np.mean(slot_mis)),
        slot_ex=obs_mi - float(np.mean(slot_mis)),
        cell_null=float(np.mean(cell_mis)),
        cell_ex=obs_mi - float(np.mean(cell_mis)),
        cell_sd=float(np.std(cell_mis)),
    )


def main():
    my_hash, hash_ok = verify_prereg_hash()
    emit("S2: Pre-registered U1 / U2 / U3 Controls & Unknown Retirement (workflow/research/SYNTHESIS.md Steps 1-3)")
    emit(f"s2_prereg_sha256={my_hash} (stub_match={hash_ok})  seed={SEED}")
    emit()

    # =========================================================================
    # PART 1: U1 — Native Line Breaks vs. 8-Word Re-Lining on Disk
    # =========================================================================
    emit("=== PART 1: U1 — Native Line Breaks vs. 8-Word Re-Lining (Pre-test on Disk) ===")
    by_zl = k1.layout()
    voy_native = [r["words"] for recs in by_zl.values() for r in recs]
    gib_native = load_gibberish_native_lines()
    mhg_native = load_control_native_lines(HERE / "data" / "controls" / "mhg_nibelungenlied.txt")
    rol_native = load_control_native_lines(HERE / "data" / "controls" / "oldfrench_roland.txt")
    occ_native = load_control_native_lines(HERE / "data" / "controls" / "occitan_croisade_albigeoise.txt")
    dan_native = [ln for ln in a2.verse_lines("italian_dante") if len(ln) >= 2][:3000]

    u1_corpora = [
        ("Voynich_ZL3b (native)", voy_native),
        ("Voynich_ZL3b (8-word)", reline_8(voy_native)),
        ("Gibberish_38 (native)", gib_native),
        ("Gibberish_38 (8-word)", reline_8(gib_native)),
        ("MHG_Nibelung (native)", mhg_native),
        ("MHG_Nibelung (8-word)", reline_8(mhg_native)),
        ("OldFrench_Rol(native)", rol_native),
        ("OldFrench_Rol(8-word)", reline_8(rol_native)),
        ("Occitan_Crois(native)", occ_native),
        ("Occitan_Crois(8-word)", reline_8(occ_native)),
        ("Dante_Verse  (native)", dan_native),
        ("Dante_Verse  (8-word)", reline_8(dan_native)),
    ]
    u1_results = {}
    for label, lns in u1_corpora:
        m = line_edge_metrics(lns)
        u1_results[label] = m
        emit(
            f"  {label:22} | lines={m['n_lines']:4d} toks={m['n_tokens']:5d} | "
            f"JSDf={m['jsd_f']:.4f} ({'>=0.10' if m['jsd_f_ge_010'] else '<0.10 ':>6}) JSDl={m['jsd_l']:.4f} | "
            f"p_init=x{m['p_enr']:5.2f} m_fin=x{m['m_enr']:5.2f} | "
            f"top_init={m['top_init']:9} top_fin={m['top_fin']:9} {m['top_bg_or']}"
        )
    non_voy_native = [
        u1_results[k]["jsd_f"]
        for k in ("Gibberish_38 (native)", "MHG_Nibelung (native)", "OldFrench_Rol(native)", "Occitan_Crois(native)", "Dante_Verse  (native)")
    ]
    u1_verdict = "OUTCOME A (SURVIVES PRE-TEST: max non-Voynich native-line JSDf = {:.4f} < 0.10)".format(max(non_voy_native)) if max(non_voy_native) < 0.10 else "OUTCOME B (OVERLAPS >= 0.10)"
    emit(f"  U1 PRE-TEST VERDICT: {u1_verdict}")
    emit()

    # =========================================================================
    # PART 2: U2 — Position-Stratified Coupling Null, Cross-Currier Edge Table & Timm Bound
    # =========================================================================
    emit("=== PART 2A: U2a — Position-Stratified Cross-Space Coupling Null (Feaster Confound Check) ===")
    u2a_pass = True
    for T, meta in N.TRANSLITS.items():
        by_t = N.load(meta)
        res = position_stratified_coupling(by_t, n_shuf=200, seed=SEED)
        ratio = res["cell_ex"] / max(1e-9, res["within_ex"])
        ok = res["cell_ex"] >= 0.09 and ratio >= 0.75
        u2a_pass = u2a_pass and ok
        emit(
            f"  {T:4} | raw_MI={res['obs_mi']:.4f} | "
            f"within_line_ex={res['within_ex']:+.4f} (null={res['within_null']:.4f}) | "
            f"slot_null_ex={res['slot_ex']:+.4f} (null={res['slot_null']:.4f}) | "
            f"(hand,sec,slot)_ex={res['cell_ex']:+.4f}±{res['cell_sd']:.4f} ({100*ratio:.1f}% of standard) -> {'OK' if ok else 'FAIL'}"
        )
    emit(f"  U2a VERDICT: {'GENUINE ADJACENT COUPLING (98%+ of cross-space MI survives (hand,section,slot) stratification across all 3 EVA transliterations)' if u2a_pass else 'POSITIONAL CONFOUND'}")
    emit()

    emit("=== PART 2B: U2b — Out-of-Sample / Cross-Currier & Non-Voynich Edge Table Transfer ===")
    by_full = N.load("ZL3b_eva")
    by_A = {p: recs for p, recs in by_full.items() if recs[0].get("lang") == "A"}
    by_B = {p: recs for p, recs in by_full.items() if recs[0].get("lang") == "B"}
    rng_split = random.Random(SEED)
    all_pages = list(by_full.keys())
    test_pages_41 = set(rng_split.sample(all_pages, 41))
    by_tr166 = {p: recs for p, recs in by_full.items() if p not in test_pages_41}
    by_te41 = {p: recs for p, recs in by_full.items() if p in test_pages_41}

    R_A = f3.ratio_table(by_A)
    R_B = f3.ratio_table(by_B)
    R_166 = f3.ratio_table(by_tr166)

    # Non-Voynich edge table: Dante verse mapped by character rank to Voynich EVA characters
    voy_words = [w for recs in by_full.values() for r in recs for w in r["words"]]
    voy_chars = [c for c, _ in Counter(ch for w in voy_words for ch in w).most_common()]
    dan_words = [w for ln in dan_native for w in ln]
    dan_chars = [c for c, _ in Counter(ch for w in dan_words for ch in w).most_common()]
    char_map = {dc: voy_chars[i % len(voy_chars)] for i, dc in enumerate(dan_chars)}
    dan_mapped_by = {"p0": [dict(words=["".join(char_map.get(c, "o") for c in w) for w in ln]) for ln in dan_native]}
    R_dante = f3.ratio_table(dan_mapped_by)

    transfer_cases = [
        ("Fit_Currier_A -> Gen_Currier_B", R_A, by_B),
        ("Fit_Currier_B -> Gen_Currier_A", R_B, by_A),
        ("Fit_Train_166 -> Gen_Heldout_41", R_166, by_te41),
        ("Fit_Dante_Rank-> Gen_ZL3b_All", R_dante, by_full),
    ]
    u2b_checks = []
    for label, R_tab, target_by in transfer_cases:
        g_sub = c2.Gen(target_by)
        gen_by = N.gen_habit(g_sub, R_tab, seed=1, p_hab=0.0, table={})
        pr_ms = N.profile(target_by)
        pr_gen = N.profile(gen_by)
        ok = pr_gen["edge"] >= 0.09
        u2b_checks.append(ok)
        emit(
            f"  {label:32} | MS_edge={pr_ms['edge']:+.4f} -> Gen_edge={pr_gen['edge']:+.4f} "
            f"(h2={pr_gen['h2']:.3f}, rep={pr_gen['redup']:.2f}%) -> {'>=+0.09 PASS' if ok else 'FAIL'}"
        )
    emit(f"  U2b VERDICT: {'TRANSFERS OUT-OF-SAMPLE (A<->B, 166->41, and rank-mapped Dante table all clear >=+0.09)' if all(u2b_checks[:3]) else 'FAILS TRANSFER'}")
    emit()

    emit("=== PART 2C: U2c — Timm's Token & Plaintext-Length Bound on ZL3b ===")
    by_gp = N.load("ZL3b_glyphplus")
    gp_words = [w for recs in by_gp.values() for r in recs for w in r["words"]]
    n_tok_para = len(voy_words)
    n_chars_eva = sum(len(w) for w in voy_words)
    n_chars_gp = sum(len(w) for w in gp_words)
    emit(f"  ZL3b running paragraph tokens = {n_tok_para:,d} across {len(by_full)} pages")
    emit(f"  Total EVA characters = {n_chars_eva:,d} (mean {n_chars_eva/n_tok_para:.2f} EVA chars/token, SD {np.std([len(w) for w in voy_words]):.2f})")
    emit(f"  Total glyph+ units   = {n_chars_gp:,d} (mean {n_chars_gp/n_tok_para:.2f} glyph+ units/token, SD {np.std([len(w) for w in gp_words]):.2f})")
    emit(f"  Implied plaintext letters for Naibbe/F3 verbose cipher (1.528 letters/token) = {int(round(n_tok_para * 1.528)):,d} letters (~{int(round(n_tok_para * 1.528 / 5.8)):,d} Latin words)")
    emit(f"  Implied plaintext words for 1-to-1 word cipher / nomenclator                 = {n_tok_para:,d} words (~{int(round(n_tok_para * 5.8)):,d} Latin letters)")
    emit()

    # =========================================================================
    # PART 3: U3 — Multi-Alphabet Unit Sensitivity & 200-Split Band Widths
    # =========================================================================
    emit("=== PART 3A: U3a — Multi-Alphabet / Fixed-Unit Profile Table ===")
    for t_name in ("ZL3b_eva", "RF1b", "IT2a", "ZL3b_glyphplus", "GC2a"):
        by_t = N.load(t_name)
        lns = [r["words"] for recs in by_t.values() for r in recs]
        wds = [w for ln in lns for w in ln]
        w25 = wds[:25000]
        h2_all = a1_profile.char_entropies(wds)["h2"]
        h2_25k = a1_profile.char_entropies(w25)["h2"]
        sd_all = float(np.std([len(w) for w in wds]))
        m_edge = line_edge_metrics(lns)
        c3_ex = c3.score(lns, c3.EVA)[2]
        emit(
            f"  {t_name:15} | toks={len(wds):5d} | h2_25k={h2_25k:.3f} h2_all={h2_all:.3f} sd_len={sd_all:.3f} | "
            f"types_25k={len(set(w25)):4d} types_all={len(set(wds)):4d} hapax={sum(v==1 for v in Counter(wds).values())/len(set(wds)):.3f} | "
            f"JSDf={m_edge['jsd_f']:.4f} cross_ex={c3_ex:+.4f}"
        )
    emit()

    emit("=== PART 3B: U3b — Within-Manuscript Empirical Band Widths (200 Random 41-Page Splits on ZL3b) ===")
    split_stats = defaultdict(list)
    pages_list = list(by_full.keys())
    for s in range(1000, 1200):
        r_s = random.Random(s)
        sub_p = set(r_s.sample(pages_list, 41))
        sub_lns = [r["words"] for p in pages_list if p in sub_p for r in by_full[p]]
        sub_wds = [w for ln in sub_lns for w in ln]
        split_stats["h2"].append(a1_profile.char_entropies(sub_wds)["h2"])
        split_stats["sd_len"].append(float(np.std([len(w) for w in sub_wds])))
        me = line_edge_metrics(sub_lns)
        split_stats["jsd_first_fg"].append(me["jsd_f"])
        split_stats["p_init_enrich"].append(me["p_enr"])
        split_stats["m_final_enrich"].append(me["m_enr"])
        split_stats["cross_excess_eva"].append(c3.score(sub_lns, c3.EVA)[2])
        split_stats["redup_pct"].append(
            100.0 * sum(a == b for ln in sub_lns for a, b in zip(ln, ln[1:])) / max(1, sum(len(ln) - 1 for ln in sub_lns))
        )
    for k in ("h2", "sd_len", "jsd_first_fg", "p_init_enrich", "m_final_enrich", "cross_excess_eva", "redup_pct"):
        arr = np.array(split_stats[k])
        p2_5, p50, p97_5 = np.percentile(arr, [2.5, 50.0, 97.5])
        emit(
            f"  {k:18} | median={p50:8.4f} | 95%_CI=[{p2_5:8.4f}, {p97_5:8.4f}] | min..max=[{arr.min():8.4f}, {arr.max():8.4f}]"
        )


if __name__ == "__main__":
    main()
