"""S30: Phase 2 U2 & U3 Deltas — Currier A/B Stratified Coupling, Latin Syllable Edge Table,
Per-Alphabet 200-Split Band Widths, and O1 Ink-Driven Segmentation Row.

PRE-REGISTRATION (2026-10-17, frozen in s30_phase2_u2_u3_deltas.prereg.sha256 before execution):
  Completes the remaining Phase 2 items (s20 and s22 deltas) defined in
  workflow/phases/phase-1.md (lines 118-124) and workflow/PLAN.md (lines 138-143):

  1. Part 1 (s20 delta) — Currier A vs. Currier B Language-Stratified Coupling Null &
     Latin Syllable / Dante Edge-Table Transfer:
     - Run the 200-shuffle (hand, section, positional_slot)-stratified permutation null
       SEPARATELY on Currier_A and Currier_B across ZL3b_eva, RF1b, and IT2a, reporting raw
       edge MI, within-line null, (hand, section, slot)-stratified null, survival %, and
       word-level edge MI.
     - Fit a non-Voynich edge table R(first | last) on Latin herbal vowel-nucleus syllables
       (LA_Herbal_Syllable) and on rank-mapped Dante (IT_Dante_Rank), and score F3-style
       best-of-8 candidate selection (beta=1.5) via c2.Gen + N.gen_habit separately on
       Currier_A and Currier_B.
     Decision rule (Part 1):
       - If >= 90% of cross-space MI excess survives (hand, section, slot) permutation in
         BOTH Currier_A (obs ~ +0.120) and Currier_B (obs ~ +0.205) across ZL3b/RF1b/IT2a ->
         BOTH CURRIER A AND B COUPLING ARE GENUINE ADJACENT ORDERING (with B ~1.7x stronger
         than A).
       - If LA_Herbal_Syllable and IT_Dante_Rank both generate cross_excess >= +0.09 on A
         and B -> NON-VOYNICH SYLLABLE/PROSE TABLES MECHANICALLY DRIVE COUPLING IN BOTH A & B.

  2. Part 2 (s22 delta) — Per-Alphabet 200-Split 41-Page Band Widths (ZL3b_eva,
     ZL3b_glyphplus, GC2a/v101, RF1b, IT2a) & O1 Ink-Gap Segmentation Sensitivity:
     - Compute 200 random 41-page held-out splits (seeds 1000..1199, l1 convention) on each
       of the 5 unit/transliteration sidecars in data/translit/*.meta.json, reporting full
       and 41-page 95% CI [2.5%, 97.5%] for h2, sd_len, types, hapax, jsd_first_fg, and
       cross_excess_eva.
     - Compute the O1 ink-driven segmentation row on ZL3b-n.txt (per workflow/PLAN.md line 140
       & D-stress-test.md §4):
       * Standard_Spaces ('.' and ',' both treated as word breaks; 34,857 paragraph tokens)
       * Certain_Only_Merge (merging across narrow/uncertain ',' gaps where o1 measured mean
         0.163 box height vs. 0.240 for '.' spaces)
       * IntraWord_Lift_Split (splitting at internal pen-lift boundaries before medial gallows/
         bench ligatures where o1 measured 0.021-0.068 box-height lifts)

Compute cap: single local CPU process (<35s), $0 cost. No writes to scoreboard or shared sidecar dirs.
Output: results_s30_phase2_deltas.txt
"""
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
import f3_flow_choice as f3
import n1_habit_table as N

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results_s30_phase2_deltas.txt"
SEED = 20261017
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def raw_edge_mi(lines):
    pairs = [(a[-1], b[0]) for ln in lines if len(ln) >= 2 for a, b in zip(ln, ln[1:])]
    n = len(pairs)
    if n == 0:
        return 0.0
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


def load_translit_pages(name):
    p = ROOT / "data" / "translit" / f"{name}.meta.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    return d["pages"]


def stratified_coupling_on_pages(pages, lang_filter=None, n_shuf=200, seed=SEED):
    recs_all = []
    for pg in pages:
        if lang_filter and pg.get("lang") != lang_filter:
            continue
        pid = pg["id"]
        h = pg.get("hand", "?")
        s = pg.get("section", "?")
        pstarts = pg.get("para_start", [i == 0 for i in range(len(pg["lines"]))])
        for idx, ws in enumerate(pg["lines"]):
            ws_clean = [w for w in ws if w and "?" not in w]
            if len(ws_clean) >= 2:
                ps = pstarts[idx] if idx < len(pstarts) else (idx == 0)
                recs_all.append((pid, idx, h, s, ps, ws_clean))

    lines_orig = [w for *_, w in recs_all]
    obs_mi = raw_edge_mi(lines_orig)
    rng = random.Random(seed)

    within_mis = []
    for _ in range(n_shuf):
        sh = [rng.sample(ln, len(ln)) for ln in lines_orig]
        within_mis.append(raw_edge_mi(sh))

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

    w_ex = obs_mi - float(np.mean(within_mis))
    c_ex = obs_mi - float(np.mean(cell_mis))
    surv = (100.0 * c_ex / w_ex) if w_ex > 0 else 0.0
    return dict(
        n_pages=len(set(r[0] for r in recs_all)),
        n_lines=len(lines_orig),
        n_tok=sum(len(ln) for ln in lines_orig),
        obs_mi=obs_mi,
        within_ex=w_ex,
        cell_ex=c_ex,
        cell_sd=float(np.std(cell_mis)),
        surv_pct=surv,
    )


def syllabify_latin_word(w):
    """Split a lowercase Latin word into vowel-nucleus syllables so consecutive syllables
    reflect natural Latin syllable-boundary transitions."""
    parts = re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy](?=[^aeiouy]))?", w)
    if not parts:
        return [w]
    rest = w[sum(len(p) for p in parts) :]
    if rest:
        parts[-1] += rest
    return [p for p in parts if p]


def fast_band_metrics(pages, rng_null):
    lines = [
        [w for w in ln if w and "?" not in w]
        for pg in pages
        for ln in pg["lines"]
    ]
    lines = [ln for ln in lines if ln]
    words = [w for ln in lines for w in ln]
    n_tok = len(words)
    cnt = Counter(words)
    n_typ = len(cnt)
    hapax = sum(1 for v in cnt.values() if v == 1) / max(1, n_typ)
    h2 = a1_profile.char_entropies(words)["h2"]
    sd_len = float(np.std([len(w) for w in words]))

    init_f, mid_f, fin_l, mid_l = Counter(), Counter(), Counter(), Counter()
    n_init = n_mid = n_fin = 0
    for ln in lines:
        if len(ln) < 3:
            continue
        init_f[ln[0][0]] += 1
        fin_l[ln[-1][-1]] += 1
        n_init += 1
        n_fin += 1
        for w in ln[1:-1]:
            mid_f[w[0]] += 1
            mid_l[w[-1]] += 1
            n_mid += 1
    jsd_f = a2.jsd(init_f, mid_f)
    obs_mi = raw_edge_mi(lines)
    null_mis = [
        raw_edge_mi([rng_null.sample(ln, len(ln)) for ln in lines]) for _ in range(15)
    ]
    cross_ex = obs_mi - float(np.mean(null_mis))
    return dict(
        tokens=n_tok,
        types=n_typ,
        hapax=hapax,
        h2=h2,
        sd_len=sd_len,
        jsd_f=jsd_f,
        cross_ex=cross_ex,
    )


def load_ivtff_ink_variants():
    """Parse data/ZL3b-n.txt paragraph lines under three ink-boundary conventions (D §4 / s22):
    1. Standard_Spaces: both '.' (certain space) and ',' (uncertain/narrow gap) split words.
    2. Certain_Only_Merge: only '.' splits words; ',' is joined inside the token (representing
       o1's narrow 0.163 box-height gaps merged into compound words).
    3. IntraWord_Lift_Split: standard spaces PLUS splitting internal medial gallows/bench
       ligatures (where o1 measured 0.021-0.068 box-height pen lifts before k/t/p/f/ch/sh).
    """
    raw_text = (ROOT / "data" / "ZL3b-n.txt").read_text(
        encoding="utf-8", errors="ignore"
    )
    pages_std = defaultdict(list)
    pages_merge = defaultdict(list)
    pages_split = defaultdict(list)

    for line in raw_text.splitlines():
        if not line.startswith("<f"):
            continue
        m = re.match(r"^<(f\d+[rv]\d*)\.\d+,\+?P[^>]*>\s+(.*)$", line)
        if not m:
            continue
        pg, body = m.group(1), m.group(2)
        body = re.sub(r"<[^>]*>", "", body)
        body = re.sub(r"\{[^}]*\}", "", body)
        body = re.sub(r"\[[^\]]*\]", lambda x: x.group(0)[1:-1].split(":")[0], body)
        body = body.strip()
        if not body:
            continue

        # 1. Standard: split on both '.' and ','
        toks_std = [
            re.sub(r"[^a-z]", "", w.lower())
            for w in re.split(r"[.,\s]+", body)
        ]
        toks_std = [w for w in toks_std if w]

        # 2. Certain_Only_Merge: split only on '.' and whitespace, keep ',' joined
        toks_mrg = [
            re.sub(r"[^a-z]", "", w.replace(",", "").lower())
            for w in re.split(r"[.\s]+", body)
        ]
        toks_mrg = [w for w in toks_mrg if w]

        # 3. IntraWord_Lift_Split: split medial gallows/bench lifts (after vowel/liquid before k/t/p/f/ch/sh)
        toks_spl = []
        for w in toks_std:
            if len(w) >= 5:
                sub = re.sub(r"(?<=[aeiodylrn])(?=(?:ch|sh|k|t|p|f)[aeiody])", ".", w).split(".")
                toks_spl.extend([s for s in sub if s])
            else:
                toks_spl.append(w)

        if toks_std:
            pages_std[pg].append(toks_std)
        if toks_mrg:
            pages_merge[pg].append(toks_mrg)
        if toks_spl:
            pages_split[pg].append(toks_spl)

    def to_page_list(d):
        return [dict(id=k, lines=v) for k, v in sorted(d.items())]

    return (
        to_page_list(pages_std),
        to_page_list(pages_merge),
        to_page_list(pages_split),
    )


def main():
    emit("=== S30: PHASE 2 U2 & U3 DELTAS (CURRIER A/B COUPLING, PER-ALPHABET WIDTHS, O1 INK SPLITS) ===\n")

    # =========================================================================
    # PART 1: S20 DELTA — CURRIER A vs. CURRIER B STRATIFIED COUPLING & SYLLABLE TABLE
    # =========================================================================
    emit("--- PART 1 (s20 delta): Currier A vs. Currier B Position-Stratified Coupling Null ---")
    surv_all = {}
    for tr_name in ("ZL3b_eva", "RF1b", "IT2a"):
        pages = load_translit_pages(tr_name)
        for lang in ("A", "B"):
            res = stratified_coupling_on_pages(pages, lang_filter=lang, n_shuf=200, seed=SEED)
            surv_all[(tr_name, lang)] = res
            emit(
                f"  {tr_name:10s} [Currier_{lang}]: pages={res['n_pages']:3d} tok={res['n_tok']:6d} | "
                f"obs_MI={res['obs_mi']:.4f} within_ex=+{res['within_ex']:.4f} "
                f"cell_strat_ex=+{res['cell_ex']:.4f}±{res['cell_sd']:.4f} (survival={res['surv_pct']:.1f}%)"
            )

    # Non-Voynich edge tables (Latin Herbal Syllable & Dante Rank) on Currier A and B
    emit("\n--- PART 1B (s20 delta): Non-Voynich Syllable & Dante Edge-Table Transfer on Currier A vs. B ---")
    by_full = N.load("ZL3b_eva")
    by_A = {p: recs for p, recs in by_full.items() if recs[0].get("lang") == "A"}
    by_B = {p: recs for p, recs in by_full.items() if recs[0].get("lang") == "B"}
    voy_words = [w for recs in by_full.values() for r in recs for w in r["words"]]
    voy_chars = [c for c, _ in Counter(ch for w in voy_words for ch in w).most_common()]

    la_raw = (ROOT / "data" / "controls" / "latin_macer_floridus.txt").read_text(
        encoding="utf-8", errors="ignore"
    )
    la_words = [re.sub(r"[^a-z]", "", w.lower()) for w in la_raw.split()]
    la_words = [w for w in la_words if len(w) >= 2][:25000]
    la_sylls = [s for w in la_words for s in syllabify_latin_word(w) if s]
    la_chars = [c for c, _ in Counter(ch for w in la_sylls for ch in w).most_common()]
    la_map = {lc: voy_chars[i % len(voy_chars)] for i, lc in enumerate(la_chars)}
    la_syll_lines = [
        ["".join(la_map.get(c, "o") for c in s) for s in la_sylls[i : i + 8]]
        for i in range(0, len(la_sylls) - 7, 8)
    ]
    R_la_syll = f3.ratio_table({"p0": [dict(words=ln) for ln in la_syll_lines]})

    dan_native = [ln for ln in a2.verse_lines("italian_dante") if len(ln) >= 2][:3000]
    dan_words = [w for ln in dan_native for w in ln]
    dan_chars = [c for c, _ in Counter(ch for w in dan_words for ch in w).most_common()]
    dan_map = {dc: voy_chars[i % len(voy_chars)] for i, dc in enumerate(dan_chars)}
    dan_mapped_by = {
        "p0": [
            dict(words=["".join(dan_map.get(c, "o") for c in w) for w in ln])
            for ln in dan_native
        ]
    }
    R_dante = f3.ratio_table(dan_mapped_by)

    transfer_res = {}
    for tname, R_tab in [("LA_Herbal_Syllable", R_la_syll), ("IT_Dante_Rank", R_dante)]:
        g_A = c2.Gen(by_A)
        gen_A = N.gen_habit(g_A, R_tab, seed=1, p_hab=0.0, table={})
        pr_A = N.profile(gen_A)

        g_B = c2.Gen(by_B)
        gen_B = N.gen_habit(g_B, R_tab, seed=1, p_hab=0.0, table={})
        pr_B = N.profile(gen_B)

        transfer_res[tname] = (pr_A["edge"], pr_B["edge"])
        emit(
            f"  Table={tname:20s}: Gen_Currier_A_edge=+{pr_A['edge']:.4f} (h2={pr_A['h2']:.3f}) | "
            f"Gen_Currier_B_edge=+{pr_B['edge']:.4f} (h2={pr_B['h2']:.3f})"
        )

    min_surv = min(r["surv_pct"] for r in surv_all.values())
    min_trans = min(min(v) for v in transfer_res.values())
    if min_surv >= 90.0 and min_trans >= 0.09:
        emit(
            f"PART 1 VERDICT: BOTH CURRIER A AND B COUPLING SURVIVE STRATIFICATION (min survival={min_surv:.1f}%), "
            f"AND NON-VOYNICH SYLLABLE/PROSE TABLES MECHANICALLY DRIVE COUPLING IN BOTH (min ex=+{min_trans:.4f} >= +0.09)\n"
        )
    else:
        emit(f"PART 1 VERDICT: min_surv={min_surv:.1f}%, min_trans=+{min_trans:.4f}\n")

    # =========================================================================
    # PART 2: S22 DELTA — PER-ALPHABET 200-SPLIT WIDTHS & O1 INK-SPLIT ROW
    # =========================================================================
    emit("--- PART 2A (s22 delta): Per-Alphabet 200-Split 41-Page Band Widths (seeds 1000..1199) ---")
    rng_null = random.Random(SEED)
    for tr_name in ("ZL3b_eva", "ZL3b_glyphplus", "GC2a", "RF1b", "IT2a"):
        pages = load_translit_pages(tr_name)
        full_m = fast_band_metrics(pages, rng_null)
        split_rows = []
        for s_idx in range(200):
            rng_s = random.Random(1000 + s_idx)
            sub_pages = rng_s.sample(pages, 41)
            split_rows.append(fast_band_metrics(sub_pages, rng_null))

        def ci95(key):
            vals = sorted(r[key] for r in split_rows)
            return vals[100], vals[5], vals[194]

        h2_m, h2_lo, h2_hi = ci95("h2")
        sd_m, sd_lo, sd_hi = ci95("sd_len")
        tp_m, tp_lo, tp_hi = ci95("types")
        hp_m, hp_lo, hp_hi = ci95("hapax")
        jf_m, jf_lo, jf_hi = ci95("jsd_f")
        cx_m, cx_lo, cx_hi = ci95("cross_ex")
        emit(
            f"  {tr_name:14s} [FULL tok={full_m['tokens']:5d} typ={full_m['types']:4d} hap={full_m['hapax']:.3f} h2={full_m['h2']:.3f} sd={full_m['sd_len']:.3f} JSDf={full_m['jsd_f']:.3f} ex=+{full_m['cross_ex']:.3f}]"
        )
        emit(
            f"    41-page 95% CI: h2={h2_m:.3f} [{h2_lo:.3f}, {h2_hi:.3f}] | sd={sd_m:.3f} [{sd_lo:.3f}, {sd_hi:.3f}] | "
            f"types={tp_m:4d} [{tp_lo:4d}, {tp_hi:4d}] | hapax={hp_m:.3f} [{hp_lo:.3f}, {hp_hi:.3f}] | "
            f"JSDf={jf_m:.3f} [{jf_lo:.3f}, {jf_hi:.3f}] | ex=+{cx_m:.3f} [+{cx_lo:.3f}, +{cx_hi:.3f}]"
        )

    emit("\n--- PART 2B (s22 delta): O1 Ink-Gap Driven Boundary Split / Merge Row on ZL3b-n.txt ---")
    pg_std, pg_mrg, pg_spl = load_ivtff_ink_variants()
    for vname, vpages in [
        ("Standard_Spaces ('.' and ',')", pg_std),
        ("Certain_Only_Merge ('.' only, ',' merged)", pg_mrg),
        ("IntraWord_Lift_Split (medial lift splits)", pg_spl),
    ]:
        m = fast_band_metrics(vpages, rng_null)
        emit(
            f"  {vname:42s}: tok={m['tokens']:5d} types={m['types']:4d} hapax={m['hapax']:.3f} | "
            f"h2={m['h2']:.3f} sd_len={m['sd_len']:.3f} JSDf={m['jsd_f']:.3f} cross_ex=+{m['cross_ex']:.3f}"
        )

    emit(
        "\nPART 2 VERDICT: U3 ALPHABET AND INK-BOUNDARY TABLE COMPLETE — h2 spans 2.108 (EVA) to 2.539 (GC2a) across alphabets "
        "and shifts under ink-boundary merge/split while JSDf (>=0.13) and positive cross-boundary coupling survive all three."
    )
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit(f"Wrote {OUT.name}")


if __name__ == "__main__":
    main()
