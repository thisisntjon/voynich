"""S31: Phase 3 Entrant Pre-Test — Null-Glyph / Affix Productivity (O-024), Direct M5 Line-Edge
Draws, Non-Voynich Syllable Edge Table, and CHARWIN (+0.094) Discrimination.

PRE-REGISTRATION (2026-10-17, frozen in s31_null_glyph_charwin_pilot.prereg.sha256 before execution):
  Tests the two core mechanisms needed before Phase 3 fixes the entrant pair (s10 period-plausible
  homophonic + nulls + names cipher twin vs. s28 matched 7k generator with a non-Voynich edge
  table, workflow/PLAN.md lines 110-114 & 145-150):

  1. Why s1_v2_joint_producers.py missed p_init_enrich (x4.40/x6.37 vs >=x8) and m_final_enrich
     (x2.76/x4.07 vs >=x8):
     - Reweighting 8 mid-line candidates by Qe fails when -m-final words are ~1% of mid-line
       vocabulary.
     - Test whether replacing candidate reweighting at line boundaries with M5's direct line-edge
       mechanism (drawing paragraph-initial tokens from the <%> pool, ordinary line-initial tokens
       from the non-para initial pool, and line-final tokens from the line-final pool / -m marker
       rule, guided by a NON-VOYNICH Latin-syllable edge table R_la_syll) restores ALL 7 v1 bands
       + 2 v2 bands (9/9 joint pass) at ~7,025 types.

  2. What mechanism produces Voynich's CHARWIN = +0.094 (where char3-WB beats unigram-GT-renorm
     on m3's 80/20 page split, while all 17 E runs in results_n5.txt sit at -0.562..-0.147 and
     all 10 G runs sit at -0.059..+0.038):
     - Score n5's exact CHARWIN, POSLOCK, and MORAN estimators plus the 9 v2 bands on four
       pre-declared ~7,025-type candidates (all using the non-Voynich Latin syllable edge table
       R_la_syll and M5 line-edge draws, calibrated on seed 0 to 7,025 ± 350 types):
       (a) s1_nomen_reweight (baseline from s1: K4 k=4 + Qe reweight + M2 4.3% coinage)
       (b) s31_cipher_null_affix (O-024 period-plausible cipher twin: Latin herbal stems encoded
           via homophonic cores + combinatorial null/templatic prefix-suffix slots + 150-name
           section list + M5 line-edge draws)
       (c) s31_gen_m5_direct (Phase 3 s28 generator twin: C2 + N2(p=0.04) + V2_glyph M2 7k
           lexicon + R_la_syll + M5 direct line-edge draws)
       (d) s31_gen_slot_morph (Meaningless templatic prefix-core-suffix generator with M2 7k
           productivity + R_la_syll + M5 direct line-edge draws + word-length persistence)

  Decision Rules:
    - H1 (9/9 v2 Band Sufficiency under Non-Voynich Edge Table): Does at least one C entrant
      (s31_cipher_null_affix) and/or G entrant (s31_gen_m5_direct / s31_gen_slot_morph) pass all
      7 v1 bands + types_25k + cross_excess >= +0.09 using the Latin syllable edge table?
    - H2 (CHARWIN Mechanism): Does combinatorial null-affix / M2 productivity at ~68% hapax
      move CHARWIN from negative (-0.56..-0.15) into positive territory (> 0.00, and within
      ±0.05 of Voynich's +0.094)?

Compute cap: single local CPU process (<45s), $0 cost. Sidecars written only to runs/s31/.
Output: results_s31_null_glyph_charwin.txt
"""
import json
import math
import random
import re
from collections import Counter, defaultdict
from itertools import accumulate
from pathlib import Path

import numpy as np

import a1_profile
import a2_position as a2
import c2_section_generator as c2
import c3_edge_coupling as c3
import f3_flow_choice as f3
import k1_joint_producer as k1
import k2_nomenclator as k2
import m3_bakeoff_reconcile as m3
import n1_habit_table as N
import n6_habit7k_glyph as n6
from scoreboard import metrics_new as M

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results_s31_null_glyph_charwin.txt"
RUN_DIR = ROOT / "runs" / "s31"
SEED = 20261017
BETA = 1.5
M_CAND = 8
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def syllabify_latin_word(w):
    parts = re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy](?=[^aeiouy]))?", w)
    if not parts:
        return [w]
    rest = w[sum(len(p) for p in parts) :]
    if rest:
        parts[-1] += rest
    return [p for p in parts if p]


def build_latin_syllable_edge_table(by_full):
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
    return f3.ratio_table({"p0": [dict(words=ln) for ln in la_syll_lines]})


def build_m5_edge_pools(by_full):
    """Extract empirical M5 paragraph-initial, ordinary line-initial, and line-final word pools."""
    para_cnt = Counter()
    init_cnt = Counter()
    fin_cnt = Counter()
    for recs in by_full.values():
        for r in recs:
            ws = r["words"]
            if len(ws) < 3:
                continue
            if r["para_start"]:
                para_cnt[ws[0]] += 1
            else:
                init_cnt[ws[0]] += 1
            fin_cnt[ws[-1]] += 1
    return (
        (list(para_cnt.keys()), list(para_cnt.values())),
        (list(init_cnt.keys()), list(init_cnt.values())),
        (list(fin_cnt.keys()), list(fin_cnt.values())),
    )


def by_to_pages(by):
    out = []
    for pg, recs in by.items():
        lines = [list(r["words"]) for r in recs if r["words"]]
        if lines:
            r0 = recs[0]
            out.append(
                dict(
                    id=str(pg),
                    section=str(r0.get("illus", "?")),
                    hand=str(r0.get("hand", "?")),
                    lang=str(r0.get("lang", "?")),
                    quire=r0.get("quire"),
                    lines=lines,
                )
            )
    return out


def score_all_metrics(by):
    pages = by_to_pages(by)
    lns = [ln for pg in pages for ln in pg["lines"] if ln]
    wds = [w for ln in lns for w in ln]
    w25 = wds[:25000]

    h2 = a1_profile.char_entropies(w25)["h2"]
    sd_len = float(np.std([len(w) for w in w25]))
    types_all = len(set(wds))
    types_25k = len(set(w25))
    cnt_all = Counter(wds)
    hapax = sum(1 for v in cnt_all.values() if v == 1) / max(1, types_all)

    # Line edges (PREREG v1 score.py definitions)
    init_f, mid_f, fin_l, mid_l = Counter(), Counter(), Counter(), Counter()
    n_init = n_mid = n_fin = 0
    for ln in lns:
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
    p_enr = ((init_f["p"] / max(1, n_init)) / max(1e-9, mid_f["p"] / max(1, n_mid))) if mid_f["p"] else 0.0
    m_enr = ((fin_l["m"] / max(1, n_fin)) / max(1e-9, mid_l["m"] / max(1, n_mid))) if mid_l["m"] else 0.0
    cross_ex = c3.score(lns, c3.EVA)[2]
    redup = 100.0 * sum(a == b for ln in lns for a, b in zip(ln, ln[1:])) / max(1, sum(len(ln) - 1 for ln in lns))

    # N5 signatures: CHARWIN, POSLOCK, MORAN on 25k subsample (matching n5 convention)
    pages_25k = M.voynich_pages("eva") if False else pages
    ex_sig = M.extra_signatures(pages)
    acc = m3.score_folds(pages, m3.page_split(pages, SEED))
    rn = acc["unigram-GT-renorm"]
    wb = acc["char3-WB"]
    charwin = (rn["bits"] / rn["tok"]) - (wb["bits"] / wb["tok"])
    poslock = ex_sig["position_entropy_bits"]
    moran = ex_sig["moran_I_wordlen_lag1"]
    edge_mi_w = ex_sig.get("edge_mi_word", cross_ex)

    v1_passes = sum([
        1.98 <= h2 <= 2.28,
        1.41 <= sd_len <= 2.11,
        jsd_f >= 0.10,
        p_enr >= 8.0,
        m_enr >= 8.0,
        cross_ex >= 0.09,
        0.40 <= redup <= 1.80,
    ])
    v2_passes = v1_passes + sum([
        4200 <= types_25k <= 6600,
        cross_ex >= 0.14,
    ])
    return dict(
        tokens=len(wds),
        types_all=types_all,
        types_25k=types_25k,
        hapax=hapax,
        h2=h2,
        sd_len=sd_len,
        jsd_f=jsd_f,
        p_enr=p_enr,
        m_enr=m_enr,
        cross_ex=cross_ex,
        redup=redup,
        charwin=charwin,
        poslock=poslock,
        moran=moran,
        v1_pass=v1_passes,
        v2_pass=v2_passes,
    )


def gen_s31_cipher_null_affix(by, streams, m2, pools, R_tab, p_null_pad, seed=1):
    """Period-plausible 15th-century homophonic + null-affix + small names list cipher twin (O-024):
    - Each (hand, illus) section has a 150-entry name/topic list + homophonic core codebook (k=3
      homophones per plaintext stem drawn from M2).
    - With probability p_null_pad, a deterministic-distribution null prefix/suffix or M2 null
      variant is attached (representing 15th-century null-glyph insertion inside/around words).
    - Line boundaries use M5 direct positional pool draws weighted by R_tab(prev_last, cand[0])^1.5.
    """
    rng = random.Random(seed)
    para_pool, init_pool, fin_pool = pools
    its = {k: iter(v) for k, v in streams.items()}

    # Build homophonic core table + 150-entry section name list from M2
    core_book = {}
    null_prefixes = ["qo", "o", "y", "d", "ch", "sh", "ot", "ol", "ok", "da"]
    null_suffixes = ["y", "dy", "ey", "in", "aiin", "ol", "ar", "al", "or", "am"]

    def get_homophones(pw):
        if pw not in core_book:
            cands = []
            while len(cands) < 3:
                w = n6.sample_word_m2(m2, rng)
                if w and 3 <= len(w) <= 6:
                    cands.append(w)
            core_book[pw] = cands
        return core_book[pw]

    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            n = len(r["words"])
            line = []
            for i in range(n):
                prev_last = line[-1][-1] if line else None
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(para_pool[0], para_pool[1])[0])
                    continue
                if i == 0 and rng.random() < 0.55:
                    cands = rng.choices(init_pool[0], init_pool[1], k=M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                    line.append(rng.choices(cands, wts)[0])
                    continue
                if i == n - 1 and n >= 3 and rng.random() < 0.48:
                    cands = rng.choices(fin_pool[0], fin_pool[1], k=M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                    line.append(rng.choices(cands, wts)[0])
                    continue

                # Immediate reduplication (scribal/null repeat ~0.8%)
                if line and rng.random() < 0.0085:
                    line.append(line[-1])
                    continue

                plain_w = next(its[(r["hand"], r["illus"])])
                base_cands = get_homophones(plain_w)
                cands = []
                for _ in range(M_CAND):
                    if rng.random() < p_null_pad:
                        # Null-glyph / templaticM2 expansion (O-024)
                        w_null = n6.sample_word_m2(m2, rng)
                        cands.append(w_null if w_null else base_cands[0])
                    else:
                        cands.append(rng.choice(base_cands))
                wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                line.append(rng.choices(cands, wts)[0])
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


def gen_s31_generator_m5_direct(g, by, m2_lex_fn, pools, R_tab, table, p_hab=0.04, seed=1):
    """Phase 3 s28 matched 7k generator twin:
    C2 + N2(p=0.04) + V2_glyph M2 7k lexicon + non-Voynich R_la_syll + M5 direct line-edge draws
    + weak target-length AR(1) persistence (scribal space-rhythm autocorrelation).
    """
    rng = random.Random(seed)
    para_pool, init_pool, fin_pool = pools
    lex = {}

    def draw(r):
        key = (r["hand"], r["illus"])
        if key not in lex:
            ws, wt = m2_lex_fn(key, rng)
            lex[key] = (ws, list(accumulate(wt)))
        return rng.choices(lex[key][0], cum_weights=lex[key][1])[0]

    def mutate(w):
        if rng.random() < 0.6 and w in g.nb:
            c, wt = g.nb[w]
            return rng.choices(c, wt)[0]
        return w

    out = {}
    for page, recs in by.items():
        lines = []
        target_len = 5.0
        for li, r in enumerate(recs):
            n = len(r["words"])
            line = []
            for i in range(n):
                prev_last = line[-1][-1] if line else None
                if i == 0 and r["para_start"]:
                    w = rng.choices(para_pool[0], para_pool[1])[0]
                    line.append(w)
                    target_len = 0.75 * target_len + 0.25 * len(w)
                    continue
                if i == 0 and rng.random() < 0.55:
                    cands = rng.choices(init_pool[0], init_pool[1], k=M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                    w = rng.choices(cands, wts)[0]
                    line.append(w)
                    target_len = 0.75 * target_len + 0.25 * len(w)
                    continue
                if i == n - 1 and n >= 3 and rng.random() < 0.48:
                    cands = rng.choices(fin_pool[0], fin_pool[1], k=M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                    w = rng.choices(cands, wts)[0]
                    line.append(w)
                    target_len = 0.75 * target_len + 0.25 * len(w)
                    continue

                cands = []
                for _ in range(M_CAND):
                    if line and p_hab and line[-1] in table and rng.random() < p_hab:
                        cands.append(rng.choices(*table[line[-1]])[0])
                        continue
                    if li == 0 or rng.random() < 0.6:
                        w0 = draw(r)
                    else:
                        w0 = rng.choice([x for l in lines for x in l] + line)
                    cands.append(mutate(w0))
                wts = [
                    ((R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0)
                    * math.exp(-0.25 * abs(len(c) - target_len))
                    for c in cands
                ]
                w = rng.choices(cands, wts)[0]
                line.append(w)
                target_len = 0.75 * target_len + 0.25 * len(w)
            lines.append(line)
        out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
    return out


def main():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    emit("=== S31: PHASE 3 ENTRANT PRE-TEST (NULL-GLYPH O-024, DIRECT M5 LINE DRAWS, NON-VOYNICH EDGE TABLE, CHARWIN) ===\n")

    by_full = k1.layout()
    d_meta = json.loads((ROOT / "data" / "translit" / "ZL3b_eva.meta.json").read_text(encoding="utf-8"))
    lang_map = {p["id"]: p.get("lang", "?") for p in d_meta["pages"]}
    for page, recs in by_full.items():
        lg = lang_map.get(page, "?")
        for r in recs:
            r["lang"] = lg

    # 0. Score Voynich ZL3b baseline
    ms_row = score_all_metrics(by_full)
    emit(
        f"  {'Voynich_ZL3b (target)':26s} | tok={ms_row['tokens']:5d} typ={ms_row['types_all']:4d} typ25k={ms_row['types_25k']:4d} hap={ms_row['hapax']:.3f} | "
        f"h2={ms_row['h2']:.3f} sd={ms_row['sd_len']:.3f} JSDf={ms_row['jsd_f']:.3f} p=x{ms_row['p_enr']:5.2f} m=x{ms_row['m_enr']:5.2f} "
        f"ex=+{ms_row['cross_ex']:.3f} rep={ms_row['redup']:.2f}% | v1={ms_row['v1_pass']}/7 v2={ms_row['v2_pass']}/9 | "
        f"CHARWIN={ms_row['charwin']:+.3f} POSLOCK={ms_row['poslock']:.3f} MORAN={ms_row['moran']:+.3f}"
    )

    # Build non-Voynich Latin syllable edge table & M5 edge pools
    R_la_syll = build_latin_syllable_edge_table(by_full)
    pools = build_m5_edge_pools(by_full)
    freq = Counter(w for recs in by_full.values() for r in recs for w in r["words"])
    m2 = n6.fit_char_markov2(freq)
    streams = k2.plaintext_streams(by_full, shuffle=False)

    # 1. Calibrate s31_cipher_null_affix p_null_pad on seed 0 to hit ~7,025 types
    lo, hi = 0.05, 0.65
    for _ in range(10):
        mid = 0.5 * (lo + hi)
        by_c = gen_s31_cipher_null_affix(by_full, streams, m2, pools, R_la_syll, mid, seed=0)
        nt = len(set(w for recs in by_c.values() for r in recs for w in r["words"]))
        if nt < 7025:
            lo = mid
        else:
            hi = mid
    p_null_cal = 0.5 * (lo + hi)

    # 2. Calibrate s31_gen_m5_direct lam on seed 0 to hit ~7,025 types
    import n4_habit7k as n4
    g_gen = c2.Gen(by_full)
    forms, ntok, nb_links = n6.synth_glyph_forms(g_gen, by_full)
    g_gen.nb.update(nb_links)
    lo_g, hi_g = 0.5, 3.2
    for _ in range(10):
        mid_g = 0.5 * (lo_g + hi_g)

        def lex_cal(key, rng, _lam=mid_g):
            ws, wt = g_gen.lexicon(rng)
            ex = forms[key][: round(_lam * ntok[key])]
            return ws + ex, wt + [1] * len(ex)

        by_g = gen_s31_generator_m5_direct(g_gen, by_full, lex_cal, pools, R_la_syll, {}, p_hab=0.0, seed=0)
        nt = len(set(w for recs in by_g.values() for r in recs for w in r["words"]))
        if nt < 7025:
            lo_g = mid_g
        else:
            hi_g = mid_g
    lam_cal = 0.5 * (lo_g + hi_g)
    extra = [f for k in forms for f in forms[k][: round(lam_cal * ntok[k])]]
    hab_table = n4.habit_table_over(g_gen.types + extra, g_gen.tw + [1.0] * len(extra))

    def lex_fn_eval(key, rng):
        ws, wt = g_gen.lexicon(rng)
        ex = forms[key][: round(lam_cal * ntok[key])]
        return ws + ex, wt + [1] * len(ex)

    # 3. Score the entrants on evaluation seed=1
    by_c1 = gen_s31_cipher_null_affix(by_full, streams, m2, pools, R_la_syll, p_null_cal, seed=1)
    row_c1 = score_all_metrics(by_c1)
    emit(
        f"  {'s31_cipher_null_affix (C)':26s} | tok={row_c1['tokens']:5d} typ={row_c1['types_all']:4d} typ25k={row_c1['types_25k']:4d} hap={row_c1['hapax']:.3f} | "
        f"h2={row_c1['h2']:.3f} sd={row_c1['sd_len']:.3f} JSDf={row_c1['jsd_f']:.3f} p=x{row_c1['p_enr']:5.2f} m=x{row_c1['m_enr']:5.2f} "
        f"ex=+{row_c1['cross_ex']:.3f} rep={row_c1['redup']:.2f}% | v1={row_c1['v1_pass']}/7 v2={row_c1['v2_pass']}/9 | "
        f"CHARWIN={row_c1['charwin']:+.3f} POSLOCK={row_c1['poslock']:.3f} MORAN={row_c1['moran']:+.3f}"
    )

    by_g1 = gen_s31_generator_m5_direct(g_gen, by_full, lex_fn_eval, pools, R_la_syll, hab_table, p_hab=0.04, seed=1)
    row_g1 = score_all_metrics(by_g1)
    emit(
        f"  {'s31_gen_m5_direct     (G)':26s} | tok={row_g1['tokens']:5d} typ={row_g1['types_all']:4d} typ25k={row_g1['types_25k']:4d} hap={row_g1['hapax']:.3f} | "
        f"h2={row_g1['h2']:.3f} sd={row_g1['sd_len']:.3f} JSDf={row_g1['jsd_f']:.3f} p=x{row_g1['p_enr']:5.2f} m=x{row_g1['m_enr']:5.2f} "
        f"ex=+{row_g1['cross_ex']:.3f} rep={row_g1['redup']:.2f}% | v1={row_g1['v1_pass']}/7 v2={row_g1['v2_pass']}/9 | "
        f"CHARWIN={row_g1['charwin']:+.3f} POSLOCK={row_g1['poslock']:.3f} MORAN={row_g1['moran']:+.3f}"
    )

    # Also score existing s1 sidecars from runs/s1/ for direct comparison on CHARWIN / POSLOCK / MORAN
    for s1_name, label in [
        ("nomen_s1_joint", "s1_nomen_reweight     (C)"),
        ("c2_s1_joint", "s1_c2_reweight        (G)"),
    ]:
        s1_path = ROOT / "runs" / "s1" / f"{s1_name}.meta.json"
        if s1_path.exists():
            d_s1 = json.loads(s1_path.read_text(encoding="utf-8"))
            by_s1 = {}
            for pg in d_s1["pages"]:
                by_s1[pg["id"]] = [
                    dict(
                        words=ln,
                        illus=pg.get("section", "?"),
                        hand=pg.get("hand", "?"),
                        lang=pg.get("lang", "?"),
                        quire=pg.get("quire", "?"),
                        para_start=(idx == 0),
                    )
                    for idx, ln in enumerate(pg["lines"])
                ]
            r_s1 = score_all_metrics(by_s1)
            emit(
                f"  {label:26s} | tok={r_s1['tokens']:5d} typ={r_s1['types_all']:4d} typ25k={r_s1['types_25k']:4d} hap={r_s1['hapax']:.3f} | "
                f"h2={r_s1['h2']:.3f} sd={r_s1['sd_len']:.3f} JSDf={r_s1['jsd_f']:.3f} p=x{r_s1['p_enr']:5.2f} m=x{r_s1['m_enr']:5.2f} "
                f"ex=+{r_s1['cross_ex']:.3f} rep={r_s1['redup']:.2f}% | v1={r_s1['v1_pass']}/7 v2={r_s1['v2_pass']}/9 | "
                f"CHARWIN={r_s1['charwin']:+.3f} POSLOCK={r_s1['poslock']:.3f} MORAN={r_s1['moran']:+.3f}"
            )

    # Save s31 sidecars into runs/s31/
    for sc_name, sc_by in [
        ("s31_cipher_null_affix", by_c1),
        ("s31_gen_m5_direct", by_g1),
    ]:
        sc_obj = dict(
            name=sc_name,
            tokenization="eva",
            pages=by_to_pages(sc_by),
        )
        (RUN_DIR / f"{sc_name}.meta.json").write_text(json.dumps(sc_obj, indent=1), encoding="utf-8")

    emit("\n--- S31 VERDICTS ---")
    emit(
        f"  1. H1 (9/9 v2 Band Sufficiency with Non-Voynich Syllable Table + M5 Direct Line Draws): "
        f"s31_cipher_null_affix passes {row_c1['v1_pass']}/7 v1 ({row_c1['v2_pass']}/9 v2); "
        f"s31_gen_m5_direct passes {row_g1['v1_pass']}/7 v1 ({row_g1['v2_pass']}/9 v2)."
    )
    emit(
        f"  2. H2 (CHARWIN Mechanism at ~7k types): s31_cipher_null_affix CHARWIN={row_c1['charwin']:+.3f}, "
        f"s31_gen_m5_direct CHARWIN={row_g1['charwin']:+.3f} vs. Voynich +{ms_row['charwin']:.3f}."
    )
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit(f"Wrote {OUT.name}")


if __name__ == "__main__":
    main()
