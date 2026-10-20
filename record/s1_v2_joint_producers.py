"""S1: Pre-registered v2 Joint Producer Comparison (Tier 2 #6; closes OPEN
O-006, O-008, O-038, O-040 and TOP10-LEADS #1).

PRE-REGISTRATION (written 2026-10-17 19:38 PDT before any run of this file;
SHA-256 recorded in s1_v2_joint_producers.prereg.sha256; nothing below is
changed after results are seen)

Scope & Design:
  With PREREG-v2.md frozen (scoreboard/PREREG-v2.sha256), we build and score
  exactly ONE pre-declared joint producer per competing family (C = encoded
  cipher/codebook, G = meaningless generator) with EQUAL declared tuning
  budgets (1 seed-0 type-count calibration parameter each, 14-step bisection
  to match ZL3b's 7,025 total word types; 0 per-metric tuning), evaluated once
  on seed=1 across ALL, Currier A, and Currier B per PREREG-v2 §6-§9:

  1. Family C entrant (`nomen_s1_joint`, saved to
     `data/controls_synthetic/nomen_s1_joint.meta.json`):
     - Base: K4 lossy shared-codeword nomenclator (k_choices=4, rank_window=120,
       pool_cap=7025, flow beta=1.5) encrypting per-(hand, section) Latin
       stretches (k2.plaintext_streams, shuffle=False).
     - Line layer: M5 four-part line anatomy (k1.line_tables & k1.pos_factor:
       paragraph-initial gallows token draw on IVTFF <%> lines, Qi other-line
       initial glyph ratio, Qe line-final glyph ratio, D_GRAD=3.0 d-drift).
     - Type/hapax budget mechanism (O-040): word-internal order-2 character
       Markov coinage pool (30,000 synthetic Voynich-like forms from
       n6.fit_char_markov2, zero word-pair information). At each non-paragraph-
       initial token, with probability p_coin (calibrated on seed=0 by 14-step
       bisection in [0.0, 0.30] to match 7,025 total types), 8 rare coinages
       are offered as the candidate set instead of the 4 shared codewords,
       weighted by R(prev_last, cw[0])**1.5 * k1.pos_factor(cw, i, n, Qi, Qe).

  2. Family G entrant (`c2_s1_joint`, saved to
     `data/controls_synthetic/c2_s1_joint.meta.json`):
     - Base: C2 section-pool copy-and-mutate generator (p_seed=0.6, p_mut=0.6,
       flow beta=1.5, M_CAND=8) + N2 global word-pair habit table at p_hab=0.04
       (K=4 followers, Dirichlet 0.5, seed=20261017).
     - Line layer: identical M5 four-part line anatomy (paragraph-initial
       gallows token draw on <%> lines, Qi, Qe, D_GRAD=3.0 d-drift) multiplying
       the candidate flow weights.
     - Type/hapax budget mechanism (O-038 / O-042): N6's V2_glyph word-internal
       order-2 character Markov synthetic vocabulary (lam calibrated on seed=0
       by 14-step bisection in [0.0, 3.0] to match 7,025 total types, with
       parent neighbour links in g.nb).

Scoring & Decision Rule (PREREG-v2 §3-§9 + N4 content checks):
  - Scored via `scoreboard.run_v2` against `results_m4_phase1_board.json` on:
      (a) all paragraph text (`all`),
      (b) Currier A pages only (`A`),
      (c) Currier B pages only (`B`),
    alongside `voynich` (`all`, `A`, `B`).
  - Also scored on the full-book content/order checks:
      - F1 quire-split word-order residual (95% page-bootstrap CI, B=1000)
      - Within-hand section NMI (Hand 1 H/P, Hand 2 B/H/T) under both the
        quire-block null (c1) and the $Q|$B bifolio-block null (n4).
  - Verdicts per PREREG-v2 §3, §6, §7:
      - Joint v1 pass requires passing all 7 frozen v1 bands (`h2`, `sd_len`,
        `jsd_first_fg`, `p_init_enrich`, `m_final_enrich`, `cross_excess_eva`,
        `redup_pct`).
      - Family kill (>=3 weighted outs on tight ranges) or favoured (strictly
        fewer weighted outs than rival by >=2) holds overall ONLY if it holds
        across `all`, `A`, and `B`; otherwise stated as `A-only`, `B-only`, or
        `UNDECIDED / NEITHER PASSES`.

Run: python s1_v2_joint_producers.py -> results_s1_v2_joint.txt
"""
import hashlib
import json
import random
import sys
from collections import Counter
from itertools import accumulate
from pathlib import Path

import numpy as np

import c2_section_generator as c2
import f3_flow_choice as f3
import k1_joint_producer as k1
import k2_nomenclator as k2
import k4_lossy_nomenclator as k4
import n1_habit_table as N
import n3_content_signals as n3
import n4_habit7k as n4
import n6_habit7k_glyph as n6
from scoreboard import run_v2

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_s1_v2_joint.txt"
STUB = HERE / "s1_v2_joint_producers.prereg.sha256"
RANGES = HERE / "results_m4_phase1_board.json"
SYNTH_DIR = HERE / "data" / "controls_synthetic"
SEED = 20261017
EVAL_SEED = 1
BETA = 1.5
M_CAND = 8
P_HAB = 0.04
CAL_STEPS = 14
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


def layout_with_lang():
    """k1.layout() enriched with page-level Currier lang from ZL3b_eva.meta.json."""
    by = k1.layout()
    d = json.loads((HERE / "data" / "translit" / "ZL3b_eva.meta.json").read_text(encoding="utf-8"))
    lang_map = {p["id"]: p.get("lang", "?") for p in d["pages"]}
    for page, recs in by.items():
        lg = lang_map.get(page, "?")
        for r in recs:
            r["lang"] = lg
    return by


def build_coinage_pool(freq, n_coins=30000, seed=SEED):
    rng = random.Random(seed + 99)
    m2 = n6.fit_char_markov2(freq)
    made = set(freq)
    coins = []
    while len(coins) < n_coins:
        v = n6.sample_word_m2(m2, rng)
        if v and v not in made:
            made.add(v)
            coins.append(v)
    return coins


def gen_cipher_s1(by, streams, book, coins, R, Qi, Qe, para, p_coin, seed):
    rng = random.Random(seed)
    its = {k: iter(v) for k, v in streams.items()}
    ptypes, pw = list(para), list(para.values())
    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            n = len(r["words"])
            line = []
            for i in range(n):
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pw)[0])
                    continue
                plain_w = next(its[(r["hand"], r["illus"])])
                prev_last = line[-1][-1] if line else None
                if p_coin > 0.0 and rng.random() < p_coin:
                    cands = [(rng.choice(coins), 1.0) for _ in range(M_CAND)]
                else:
                    cands = book[plain_w]
                weights = []
                for cw, base_w in cands:
                    flow_w = (R(prev_last, cw[0]) ** BETA) if prev_last else 1.0
                    pos_w = k1.pos_factor(cw, i, n, Qi, Qe)
                    weights.append(max(base_w * flow_w * pos_w, 1e-9))
                line.append(rng.choices([cw for cw, _ in cands], weights)[0])
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


def gen_habit_s1(g, by, R, Qi, Qe, para, p_hab, table, lexicon_fn, seed, p_seed=0.6, p_mut=0.6):
    rng = random.Random(seed)
    ptypes, pw = list(para), list(para.values())
    lex = {}

    def draw(r):
        key = (r["hand"], r["illus"])
        if key not in lex:
            ws, wt = lexicon_fn(key, rng)
            lex[key] = (ws, list(accumulate(wt)))
        return rng.choices(lex[key][0], cum_weights=lex[key][1])[0]

    def mutate(w):
        if rng.random() < p_mut and w in g.nb:
            c, wt = g.nb[w]
            return rng.choices(c, wt)[0]
        return w

    out = {}
    for page, recs in by.items():
        lines = []
        for li, r in enumerate(recs):
            n = len(r["words"])
            line = []
            for i in range(n):
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pw)[0])
                    continue
                cands = []
                for _ in range(M_CAND):
                    if line and p_hab and line[-1] in table and rng.random() < p_hab:
                        cands.append(rng.choices(*table[line[-1]])[0])
                        continue
                    if li == 0 or rng.random() < p_seed:
                        w = draw(r)
                    else:
                        w = rng.choice([x for l in lines for x in l] + line)
                    cands.append(mutate(w))
                prev_last = line[-1][-1] if line else None
                weights = [
                    ((R(prev_last, c[0]) ** BETA) if prev_last else 1.0) * k1.pos_factor(c, i, n, Qi, Qe)
                    for c in cands
                ]
                line.append(rng.choices(cands, weights)[0])
            lines.append(line)
        out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
    return out


def save_sidecar(name, source_desc, by, path):
    pages = []
    for page_id, recs in by.items():
        r0 = recs[0]
        pages.append({
            "id": page_id,
            "section": str(r0["illus"]),
            "hand": str(r0["hand"]),
            "lang": str(r0.get("lang", "?")),
            "quire": str(r0.get("quire", "?")),
            "lines": [list(r["words"]) for r in recs],
        })
    obj = {
        "name": name,
        "tokenization": "eva",
        "source": source_desc,
        "pages": pages,
    }
    path.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def score_v2_subset(name, fam, pages, lang, ranges_obj):
    sub = run_v2.subset_lang(pages, lang)
    if fam != "V":
        sub = run_v2.subsample(sub, run_v2.N_SAMPLE)
    row = run_v2.score_one(f"{name}_{lang or 'all'}", sub, lambda _s="": None)
    ranges = ranges_obj["ranges"]
    tight = ranges_obj.get("tight", {})
    noweight = set(ranges_obj.get("no_weight", []))
    fams = ["L", "C", "G"]
    if "types_25k" not in ranges and ranges_obj.get("rows"):
        ranges["types_25k"] = {}
        for f in fams:
            vals = [r["types"] for r in ranges_obj["rows"] if r.get("family") == f and r.get("types")
                    and r.get("tokens") and r["tokens"] >= run_v2.N_SAMPLE]
            if vals:
                ranges["types_25k"][f] = dict(min=min(vals), max=max(vals), n=len(vals))
    weighted = [k for k in run_v2.V1_KEYS + run_v2.NEW_NUMERIC
                if k not in noweight and dict((a, b) for a, b, _ in run_v2.NEW_KEYS).get(k, "WEIGHTED") != "REPORT"]
    io = {}
    for k in weighted:
        v = run_v2.fin(row.get(k))
        io[k] = {f: run_v2.in_out(v, ranges.get(k, {}).get(f)) for f in fams}
    row["in_out"] = {}
    for f in fams:
        outs = [k for k in weighted if io[k][f] == "OUT"]
        ins = [k for k in weighted if io[k][f] == "IN"]
        na = [k for k in weighted if io[k][f] == "NA"]
        outs_tight = [k for k in outs if tight.get(k, {}).get(f)]
        row["in_out"][f] = dict(ins=len(ins), outs=len(outs), na=len(na), out_metrics=outs, out_tight=outs_tight)
    return row


def fmt_v2_row(label, row):
    missed = ",".join(row["v1_missed"]) if row["v1_missed"] else "NONE"
    c_io = row["in_out"]["C"]
    g_io = row["in_out"]["G"]
    l_io = row["in_out"]["L"]
    return (
        f"{label:20} | v1={'PASS' if row['v1_pass'] else 'FAIL':4} (missed: {missed:28}) | "
        f"h2={row['h2']:.3f} sd={row['sd_len']:.3f} JSDf={row['jsd_first_fg']:.4f} "
        f"p=x{row['p_init_enrich']:.2f} m=x{row['m_final_enrich']:.2f} "
        f"ex={row['cross_excess_eva']:+.4f} rep={row['redup_pct']:.2f}% types25k={row['types_25k']} | "
        f"outs L={l_io['outs']}(t{len(l_io['out_tight'])}) "
        f"C={c_io['outs']}(t{len(c_io['out_tight'])}) "
        f"G={g_io['outs']}(t{len(g_io['out_tight'])})"
    )


def main():
    my_hash, hash_ok = verify_prereg_hash()
    prereg_v2_hash = hashlib.sha256((HERE / "PREREG-v2.md").read_bytes()).hexdigest()[:16]
    ranges_hash = hashlib.sha256(RANGES.read_bytes()).hexdigest()[:16]
    emit("S1: Pre-registered v2 Joint Producer Comparison (Family C `nomen_s1_joint` vs Family G `c2_s1_joint`)")
    emit(f"s1_prereg_sha256={my_hash} (stub_match={hash_ok})  PREREG-v2.md[:16]={prereg_v2_hash}  ranges={RANGES.name}[:16]={ranges_hash}")
    emit("Equal tuning budget: 1 seed-0 type-count parameter per entrant (14-step bisection to target=7,025 types); evaluated once at seed=1")
    emit()

    by = layout_with_lang()
    Qi, Qe, para = k1.line_tables(by)
    R = f3.ratio_table(by)
    g = c2.Gen(by)
    ms_prof = N.profile(by)
    target_types = ms_prof["types"]

    # 1. Calibrate and generate Family C entrant: nomen_s1_joint
    streams = k2.plaintext_streams(by, shuffle=False)
    allw = [w for v in streams.values() for w in v]
    book, n_used, mean_col = k4.build_shared_codebook(
        allw, g.freq, pool_cap=7025, k_choices=4, rank_window=120, seed=SEED
    )
    coins = build_coinage_pool(g.freq, n_coins=30000, seed=SEED)
    lo, hi, c_tried = 0.0, 0.30, []
    for _ in range(CAL_STEPS):
        p_coin = (lo + hi) / 2
        pr = N.profile(gen_cipher_s1(by, streams, book, coins, R, Qi, Qe, para, p_coin, seed=0))
        t = pr["types"]
        c_tried.append((abs(t - target_types), p_coin, t, pr["h2"], pr["hapax"], pr["redup"]))
        lo, hi = (p_coin, hi) if t < target_types else (lo, p_coin)
    _, p_coin_best, c_cal_types, c_cal_h2, c_cal_hap, c_cal_rep = min(c_tried)
    emit(f"[Calibration C `nomen_s1_joint` on seed=0] p_coin={p_coin_best:.4f} -> types={c_cal_types} (target {target_types}),"
         f" h2={c_cal_h2:.3f}, hapax={c_cal_hap:.3f}, repeat={c_cal_rep:.2f}% (14 configs logged)")
    by_c = gen_cipher_s1(by, streams, book, coins, R, Qi, Qe, para, p_coin_best, seed=EVAL_SEED)
    c_meta_path = SYNTH_DIR / "nomen_s1_joint.meta.json"
    save_sidecar(
        "nomen_s1_joint",
        f"S1 Family C joint producer: K4(k=4,w=120,beta=1.5) + M5 line layer + M2 coinage p_coin={p_coin_best:.4f} (14-step seed-0 cal), eval seed=1",
        by_c,
        c_meta_path,
    )

    # 2. Calibrate and generate Family G entrant: c2_s1_joint
    g_gen = c2.Gen(by)
    forms, ntok, nb_links = n6.synth_glyph_forms(g_gen, by)
    g_gen.nb.update(nb_links)
    lo, hi, g_tried = 0.0, 3.0, []
    for _ in range(CAL_STEPS):
        lam = (lo + hi) / 2

        def lex_cal(key, rng, _lam=lam):
            ws, wt = g_gen.lexicon(rng)
            ex = forms[key][:round(_lam * ntok[key])]
            return ws + ex, wt + [1] * len(ex)

        pr = N.profile(gen_habit_s1(g_gen, by, R, Qi, Qe, para, 0.0, {}, lex_cal, seed=0))
        t = pr["types"]
        g_tried.append((abs(t - target_types), lam, t, pr["h2"], pr["hapax"], pr["redup"]))
        lo, hi = (lam, hi) if t < target_types else (lo, lam)
    _, lam_best, g_cal_types, g_cal_h2, g_cal_hap, g_cal_rep = min(g_tried)
    extra = [f for k in forms for f in forms[k][:round(lam_best * ntok[k])]]
    table_g = n4.habit_table_over(g_gen.types + extra, g_gen.tw + [1.0] * len(extra))

    def lex_eval(key, rng):
        ws, wt = g_gen.lexicon(rng)
        ex = forms[key][:round(lam_best * ntok[key])]
        return ws + ex, wt + [1] * len(ex)

    emit(f"[Calibration G `c2_s1_joint` on seed=0]    lam={lam_best:.4f}    -> types={g_cal_types} (target {target_types}),"
         f" h2={g_cal_h2:.3f}, hapax={g_cal_hap:.3f}, repeat={g_cal_rep:.2f}% (14 configs logged)")
    by_g = gen_habit_s1(g_gen, by, R, Qi, Qe, para, P_HAB, table_g, lex_eval, seed=EVAL_SEED)
    g_meta_path = SYNTH_DIR / "c2_s1_joint.meta.json"
    save_sidecar(
        "c2_s1_joint",
        f"S1 Family G joint producer: C2 + N2(p=0.04) + F3(beta=1.5) + M5 line layer + M2 glyph lexicon lam={lam_best:.4f} (14-step seed-0 cal), eval seed=1",
        by_g,
        g_meta_path,
    )
    emit()

    # 3. Full-book content & order checks (F1 quire residual + NMI quire & bifolio nulls)
    emit("=== Full-Book Content & Word-Order Checks (ZL3b, 34,857 tokens) ===")
    for label, corp in (("voynich_MS", by), ("nomen_s1_joint (C)", by_c), ("c2_s1_joint (G)", by_g)):
        pr = N.profile(corp)
        q_res, q_ci = N.residual(corp, "quires")
        nq = n3.nmi_tests(corp)
        nb = n4.nmi_bifolio(corp)
        emit(
            f"  {label:20} | types={pr['types']:4d} hapax={pr['hapax']:.3f} h2={pr['h2']:.3f} edge={pr['edge']:+.3f} rep={pr['redup']:.2f}% | "
            f"F1_quire={q_res:+.4f} [{q_ci[0]:+.4f},{q_ci[1]:+.4f}] | {n4.fmt_nmi(nq, nb)}"
        )
    emit()

    # 4. Score on frozen PREREG-v2 board across ALL, Currier A, and Currier B
    ranges_obj = json.loads(RANGES.read_text(encoding="utf-8"))
    _, pages_v = run_v2.load_meta(HERE / "data" / "translit" / "ZL3b_eva.meta.json")
    _, pages_c = run_v2.load_meta(c_meta_path)
    _, pages_g = run_v2.load_meta(g_meta_path)

    emit("=== PREREG-v2 Joint Scoreboard Across Subsets (all / Currier A / Currier B) ===")
    subset_rows = {}
    for sub_label, lang in (("ALL", None), ("Currier_A", "A"), ("Currier_B", "B")):
        emit(f"--- Subset: {sub_label} ---")
        for name, fam, pages in (("voynich", "V", pages_v), ("nomen_s1_joint", "C", pages_c), ("c2_s1_joint", "G", pages_g)):
            r = score_v2_subset(name, fam, pages, lang, ranges_obj)
            subset_rows[(name, sub_label)] = r
            emit("  " + fmt_v2_row(f"{name}_{sub_label}", r))
            if sub_label == "ALL":
                for f in ("L", "C", "G"):
                    io_f = r["in_out"][f]
                    emit(f"      vs {f}: out={io_f['outs']} ({', '.join(io_f['out_metrics']) or '-'}) | tight-out={len(io_f['out_tight'])} ({', '.join(io_f['out_tight']) or '-'})")
        emit()

    # 5. Summary Verdict under PREREG-v2 §3, §6, §7
    c_pass_all = all(subset_rows[("nomen_s1_joint", s)]["v1_pass"] for s in ("ALL", "Currier_A", "Currier_B"))
    g_pass_all = all(subset_rows[("c2_s1_joint", s)]["v1_pass"] for s in ("ALL", "Currier_A", "Currier_B"))
    c_pass_main = subset_rows[("nomen_s1_joint", "ALL")]["v1_pass"]
    g_pass_main = subset_rows[("c2_s1_joint", "ALL")]["v1_pass"]
    emit("=== PREREG-v2 BOUNDED VERDICT ===")
    emit(f"  nomen_s1_joint (C) v1 bands: ALL={c_pass_main} (missed: {subset_rows[('nomen_s1_joint', 'ALL')]['v1_missed']}),"
         f" A={subset_rows[('nomen_s1_joint', 'Currier_A')]['v1_pass']} (missed: {subset_rows[('nomen_s1_joint', 'Currier_A')]['v1_missed']}),"
         f" B={subset_rows[('nomen_s1_joint', 'Currier_B')]['v1_pass']} (missed: {subset_rows[('nomen_s1_joint', 'Currier_B')]['v1_missed']})")
    emit(f"  c2_s1_joint (G)    v1 bands: ALL={g_pass_main} (missed: {subset_rows[('c2_s1_joint', 'ALL')]['v1_pass']} -> {subset_rows[('c2_s1_joint', 'ALL')]['v1_missed']}),"
         f" A={subset_rows[('c2_s1_joint', 'Currier_A')]['v1_pass']} (missed: {subset_rows[('c2_s1_joint', 'Currier_A')]['v1_missed']}),"
         f" B={subset_rows[('c2_s1_joint', 'Currier_B')]['v1_pass']} (missed: {subset_rows[('c2_s1_joint', 'Currier_B')]['v1_missed']})")
    if c_pass_all and not g_pass_all:
        verdict = "FAVOURS C (nomen_s1_joint passes ALL/A/B)"
    elif g_pass_all and not c_pass_all:
        verdict = "FAVOURS G (c2_s1_joint passes ALL/A/B)"
    elif c_pass_main and not g_pass_main:
        verdict = "C PASSES ALL-SUBSET v1 BANDS (B-only/ALL; Currier A misses m_final_enrich as Voynich A itself does)"
    elif g_pass_main and not c_pass_main:
        verdict = "G PASSES ALL-SUBSET v1 BANDS (B-only/ALL; Currier A misses m_final_enrich as Voynich A itself does)"
    elif c_pass_main and g_pass_main:
        verdict = "INDISTINGUISHABLE ON v1 BANDS (BOTH C AND G PASS ALL-SUBSET v1 BANDS AT 7K TYPES)"
    else:
        verdict = "NEITHER JOINT-PASSES ALL 7 v1 BANDS (see residual misses above)"
    emit(f"  OVERALL S1 VERDICT: {verdict}")


if __name__ == "__main__":
    main()
