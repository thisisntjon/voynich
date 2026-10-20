"""L1: Confirmatory Held-Out G1 Split Diagnostic & Intra-Section Recto/Verso + Bifolio Continuity Test.

Frozen before execution (2026-10-17):
  1. Part A (TEAM-HANDOFF.md Tier-1 #1):
     Score the real Voynich manuscript (ZL3b-n.txt) on G1's exact 80/20 page split
     (Random(20261017): 166 train pages, 41 held-out test pages) and across 200
     random 41-page subsamples (seeds 1000..1199) against the 7 frozen PREREG v1 bands.
     Compare directly against G1 (seed_L200 & circular), H1 (flow cipher + line rules),
     and C (nomenclator) evaluated on the exact same 41 held-out test pages.
     Stopping / Decision Rule:
       - If real Voynich on the 41 test pages (seed=20261017) passes all 7 PREREG v1
         bands (specifically h2 >= 1.98 and jsd_first_fg >= 0.10), G1's held-out misses
         (h2=1.935, jsd_first_fg=0.0994/0.0886) are genuine generator deficits, not
         finite-sample shrinkage at ~8.6k tokens.
       - If real Voynich on the 41 test pages misses h2 or jsd_first_fg (or >20% of
         41-page subsamples of real Voynich fail), the 25k-token PREREG v1 bands exhibit
         finite-sample bias at 41 pages.

  2. Part B (TEAM-HANDOFF.md Tier-1 #4 + TheVoynich.org T2-007 + Voynich.Ninja Thread 6215):
     Test whether within-section recto/verso folio pairs (same leaf, fNNr vs fNNv) and
     sequentially adjacent folios (fNNv -> f(NN+1)r) have higher vocabulary cosine/Jaccard
     similarity than random folio pairs matched on exact (hand, illus) section
     (2,000 section-preserving permutations, seed=20261017).
     Compare real Voynich against G1 (section-level generator, which is exchangeable
     across pages within each (hand, illus) stratum) and H1 (sequential Latin flow cipher).
     Stopping / Decision Rule:
       - Pure section-lexicon generators (C2/G1) draw pages exchangeably within each
         (hand, illus) stratum, predicting z ~ 0 under within-(hand, illus) permutation.
       - If real Voynich shows p < 0.001 (z >= 3.0) within-(hand, illus) recto/verso or
         adjacent-folio excess similarity while G1 has z ~ 0, page-to-page state persists
         within sections, falsifying exchangeable section-table generation.

Compute cap: single local CPU run (<15s), $0 cost.
Output: results_l1.txt
"""
import importlib.util
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "scoreboard_score", ROOT / "scoreboard" / "score.py"
)
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

import corpora
import g1_edge_joint as g1
import h1_flow_lines as h1

OUT = ROOT / "results_l1.txt"
SEED = 20261017
N_RESAMPLES = 200
N_PERM = 2000

log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def score_page_subset(by, page_names, label):
    lines = [r["words"] for p in page_names for r in by[p] if r["words"]]
    words = [w for line in lines for w in line]
    row = score.score_corpus(label, words, lines)
    failed = g1.band_fail(row)
    return row, failed


def format_row(name, row, failed):
    return (
        f"{name:28} tok={row['tokens']:5d} types={row['types']:4d} "
        f"h2={row['h2']:.3f} sd={row['sd_len']:.3f} "
        f"JSDf={row['jsd_first_fg']:.4f} p=x{row['p_init_enrich']:5.2f} "
        f"m=x{row['m_final_enrich']:5.2f} excess={row['cross_excess_eva']:+.4f} "
        f"redup={row['redup_pct']:5.2f}%  "
        f"joint={'PASS' if not failed else 'FAIL'} failed={failed or '-'}"
    )


def folio_num_and_side(page_name):
    m = re.match(r"^f(\d+)([rv])(\d*)$", page_name)
    if not m:
        return None, None, None
    return int(m.group(1)), m.group(2), m.group(3)


def cosine_counter(c1, c2):
    if not c1 or not c2:
        return 0.0
    dot = sum(v * c2.get(k, 0) for k, v in c1.items())
    n1 = math.sqrt(sum(v * v for v in c1.values()))
    n2 = math.sqrt(sum(v * v for v in c2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def page_continuity_test(page_order, page_strata, page_words_map, seed=SEED, n_perm=N_PERM):
    """Compute mean vocabulary cosine similarity for:
      1) Recto/verso pairs on the same folio number within the same (hand, illus) stratum
      2) Consecutive pages in manuscript order within the same (hand, illus) stratum
    Compare against n_perm permutations that shuffle page word-bags within each
    exact (hand, illus) stratum (preserving page lengths / word bags).
    """
    counters = {p: Counter(page_words_map[p]) for p in page_order}

    # Identify within-stratum recto/verso pairs and consecutive pairs by index
    idx_of = {p: i for i, p in enumerate(page_order)}
    rv_pairs = []
    for i, p1 in enumerate(page_order):
        f1, s1, sub1 = folio_num_and_side(p1)
        if f1 is None or s1 != "r":
            continue
        target_v = f"f{f1}v{sub1}"
        if target_v in idx_of and page_strata[p1] == page_strata[target_v]:
            rv_pairs.append((p1, target_v))

    adj_pairs = []
    for p1, p2 in zip(page_order, page_order[1:]):
        if page_strata[p1] == page_strata[p2]:
            adj_pairs.append((p1, p2))

    def mean_sim(pairs, cname_map):
        if not pairs:
            return 0.0
        return sum(cosine_counter(counters[cname_map[a]], counters[cname_map[b]]) for a, b in pairs) / len(pairs)

    identity = {p: p for p in page_order}
    obs_rv = mean_sim(rv_pairs, identity)
    obs_adj = mean_sim(adj_pairs, identity)

    by_stratum = defaultdict(list)
    for p in page_order:
        by_stratum[page_strata[p]].append(p)

    rng = random.Random(seed)
    null_rv = []
    null_adj = []
    for _ in range(n_perm):
        perm_map = {}
        for _, plist in by_stratum.items():
            shuffled = list(plist)
            rng.shuffle(shuffled)
            for orig, shuf in zip(plist, shuffled):
                perm_map[orig] = shuf
        null_rv.append(mean_sim(rv_pairs, perm_map))
        null_adj.append(mean_sim(adj_pairs, perm_map))

    def stats(obs, nulls):
        mu = sum(nulls) / len(nulls)
        sd = math.sqrt(sum((x - mu) ** 2 for x in nulls) / len(nulls))
        z = (obs - mu) / sd if sd > 0 else 0.0
        p = sum(1 for x in nulls if x >= obs) / len(nulls)
        return mu, sd, z, p

    # Also compute length-preserving within-stratum token-shuffle null (200 perms)
    # This removes the page-length variance confound where two high-token pages have higher cosine
    stratum_tokens = defaultdict(list)
    for p in page_order:
        stratum_tokens[page_strata[p]].extend(page_words_map[p])
    tok_null_rv, tok_null_adj = [], []
    for _ in range(200):
        shuf_pools = {}
        for st, pool in stratum_tokens.items():
            cp = list(pool)
            rng.shuffle(cp)
            shuf_pools[st] = iter(cp)
        shuf_counters = {}
        for p in page_order:
            n_tok = len(page_words_map[p])
            it = shuf_pools[page_strata[p]]
            shuf_counters[p] = Counter(next(it) for _ in range(n_tok))
        tok_null_rv.append(
            sum(cosine_counter(shuf_counters[a], shuf_counters[b]) for a, b in rv_pairs) / max(len(rv_pairs), 1)
        )
        tok_null_adj.append(
            sum(cosine_counter(shuf_counters[a], shuf_counters[b]) for a, b in adj_pairs) / max(len(adj_pairs), 1)
        )

    return {
        "n_rv": len(rv_pairs),
        "obs_rv": obs_rv,
        "rv_stats": stats(obs_rv, null_rv),
        "rv_tok_stats": stats(obs_rv, tok_null_rv),
        "n_adj": len(adj_pairs),
        "obs_adj": obs_adj,
        "adj_stats": stats(obs_adj, null_adj),
        "adj_tok_stats": stats(obs_adj, tok_null_adj),
    }


def main():
    emit("L1: Confirmatory Held-Out G1 Split Diagnostic & Intra-Section Continuity Test")
    emit("=============================================================================")
    emit(f"Frozen split seed={SEED}; PREREG v1 bands from scoreboard/score.py")
    emit()

    by = g1.pages()
    train, test = g1.split_names(by)
    emit(f"Part A: Real Voynich & Competing Families on G1's Exact Split (train={len(train)}, test={len(test)})")
    emit("-" * 95)

    # 1. Score real Voynich full, train (166p), and held-out test (41p)
    all_pages = list(by.keys())
    r_full, f_full = score_page_subset(by, all_pages, "voynich_full_207p")
    r_train, f_train = score_page_subset(by, train, "voynich_train_166p")
    r_test, f_test = score_page_subset(by, test, "voynich_held_41p")

    emit(format_row("voynich_full_207p", r_full, f_full))
    emit(format_row("voynich_train_166p", r_train, f_train))
    emit(format_row("voynich_held_41p (TARGET)", r_test, f_test))
    emit()

    # 2. Score G1 (seed_L200 & circular) on the exact same 41 held-out pages
    table, marginal, _, _ = g1.fit_table(by, train)
    for mode, lex_size, seed in [("seed", 200, SEED), ("circular", None, SEED)]:
        rng = random.Random(seed)
        get = g1.lexicon_getter(by, mode, rng, lex_size or 0)
        full_lines, held_lines, _, _ = g1.generate(by, test, table, marginal, get, rng)
        words = [w for line in held_lines for w in line]
        tag = f"g1_{mode}_L{lex_size}_held41p"
        row = score.score_corpus(tag, words, held_lines)
        failed = g1.band_fail(row)
        emit(format_row(tag, row, failed))

    # 3. Score H1 (Latin flow cipher + line rules, ratio table fit on train pages only) on the 41 held-out pages
    import c4_naibbe_lines as c4
    import f3_flow_choice as f3

    v_recs = corpora.voynich_lines()
    by_train = {p: by[p] for p in train}
    seq, tab = f3.naibbe_chunks()
    toks = f3.cipher_stream(seq, tab, f3.ratio_table(by_train), h1.BETA, h1.CIPHER_SEED)
    sk = c4.skeleton(toks, by)
    _, h1_unruled = h1.flatten(sk)
    h1_full_lines = h1.apply_rules(h1_unruled)
    test_set = set(test)
    h1_held_lines = [
        line for r, line in zip(v_recs, h1_full_lines) if r["page"] in test_set and line
    ]
    h1_words = [w for line in h1_held_lines for w in line]
    h1_row = score.score_corpus("h1_flow_cipher_held41p", h1_words, h1_held_lines)
    h1_fail = g1.band_fail(h1_row)
    emit(format_row("h1_flow_cipher_held41p", h1_row, h1_fail))

    # 4. Score C (K2 Nomenclator x2.0 and x5.0 with train-fit line/ratio tables) on the 41 held-out pages
    import c2_section_generator as c2
    import k1_joint_producer as k1
    import k2_nomenclator as k2

    by_k1 = k1.layout()
    by_k1_train = {p: by_k1[p] for p in train if p in by_k1}
    Qi_tr, Qe_tr, para_tr = k1.line_tables(by_k1_train)
    R_tr = f3.ratio_table(by_k1_train)
    g_tr = c2.Gen(by_k1_train)
    streams = k2.plaintext_streams(by_k1)
    allw = [w for v in streams.values() for w in v]
    pool_tr = k2.codeword_pool(g_tr, 25_000)
    k2_x2_pages = {}
    for scale, tag in [(2.0, "c_k2_nomen_x2_held41p"), (5.0, "c_k2_nomen_x5_held41p")]:
        book = k2.codebook(allw, g_tr, scale, pool_tr)[0]
        enc_by = k2.encrypt(by_k1, streams, book, R_tr, Qi_tr, Qe_tr, para_tr, seed=1)
        if scale == 2.0:
            k2_x2_pages = {p: [w for r in recs for w in r["words"]] for p, recs in enc_by.items()}
        nomen_held_lines = [
            r["words"] for p in test if p in enc_by for r in enc_by[p] if r["words"]
        ]
        nomen_held_words = [w for line in nomen_held_lines for w in line]
        nomen_row = score.score_corpus(tag, nomen_held_words, nomen_held_lines)
        nomen_fail = g1.band_fail(nomen_row)
        emit(format_row(tag, nomen_row, nomen_fail))
    emit()

    # 5. Bootstrap / Random 41-page subsamples of Real Voynich (seeds 1000..1199)
    emit(f"Finite-Sample Check: {N_RESAMPLES} Random 41-Page Splits of Real Voynich (seeds 1000..{1000+N_RESAMPLES-1})")
    emit("-" * 95)
    pass_count = 0
    band_miss_counts = Counter()
    h2_vals, jsdf_vals, exc_vals = [], [], []
    for s in range(1000, 1000 + N_RESAMPLES):
        rng = random.Random(s)
        names = list(by.keys())
        rng.shuffle(names)
        sub_test = names[int(round(0.8 * len(names))):]
        row, failed = score_page_subset(by, sub_test, f"sub_{s}")
        if not failed:
            pass_count += 1
        for k in failed:
            band_miss_counts[k] += 1
        h2_vals.append(row["h2"])
        jsdf_vals.append(row["jsd_first_fg"])
        exc_vals.append(row["cross_excess_eva"])

    h2_vals.sort()
    jsdf_vals.sort()
    exc_vals.sort()
    p5 = int(0.05 * N_RESAMPLES)
    p50 = int(0.50 * N_RESAMPLES)
    p95 = int(0.95 * N_RESAMPLES)
    emit(f"Real Voynich 41-page joint PASS rate: {pass_count}/{N_RESAMPLES} ({100*pass_count/N_RESAMPLES:.1f}%)")
    emit(f"Real Voynich 41-page band miss counts: {dict(band_miss_counts) or 'NONE'}")
    emit(f"Real Voynich 41-page quantiles (p05 / p50 / p95):")
    emit(f"  h2              : {h2_vals[p5]:.3f} / {h2_vals[p50]:.3f} / {h2_vals[p95]:.3f}  (PREREG band: [1.980, 2.280])")
    emit(f"  jsd_first_fg    : {jsdf_vals[p5]:.4f} / {jsdf_vals[p50]:.4f} / {jsdf_vals[p95]:.4f}  (PREREG band: >= 0.1000)")
    emit(f"  cross_excess_eva: {exc_vals[p5]:+.4f} / {exc_vals[p50]:+.4f} / {exc_vals[p95]:+.4f}  (PREREG band: >= +0.0900)")
    if not f_test and pass_count / N_RESAMPLES >= 0.80:
        emit("DECISION (Part A): Real Voynich PASSES all 7 bands on the exact 41 held-out pages")
        emit(f"  (h2={r_test['h2']:.3f}, JSDf={r_test['jsd_first_fg']:.4f}) and in {100*pass_count/N_RESAMPLES:.1f}% of random 41-page splits.")
        emit("  Therefore G1's held-out misses (seed h2=1.595, JSDf=0.0801; circular h2=1.935, JSDf=0.0994) are")
        emit("  GENUINE GENERATOR DEFICITS, not finite-sample artifacts.")
    else:
        emit("DECISION (Part A): Finite-sample variance affects 41-page subsets; see miss counts above.")
    emit()

    # Part B: Intra-Section Recto/Verso and Sequential Page Continuity
    emit("Part B: Intra-Section Recto/Verso & Adjacent-Folio Continuity (2,000 Section-Preserving Permutations)")
    emit("-" * 95)
    page_order = list(by.keys())
    page_strata = {}
    real_page_words = {}
    for p, recs in by.items():
        strata_cnt = Counter((r["hand"], r["illus"]) for r in recs)
        page_strata[p] = strata_cnt.most_common(1)[0][0]
        real_page_words[p] = [w for r in recs for w in r["words"] if w]

    rng_g1s = random.Random(SEED)
    get_g1s = g1.lexicon_getter(by, "seed", rng_g1s, 200)
    g1s_full, _, _, _ = g1.generate(by, test, table, marginal, get_g1s, rng_g1s)

    rng_g1c = random.Random(SEED)
    get_g1c = g1.lexicon_getter(by, "circular", rng_g1c, 0)
    g1c_full, _, _, _ = g1.generate(by, test, table, marginal, get_g1c, rng_g1c)

    g1s_page_words = defaultdict(list)
    g1c_page_words = defaultdict(list)
    h1_page_words = defaultdict(list)
    for r, l_s, l_c, l_h in zip(v_recs, g1s_full, g1c_full, h1_full_lines):
        g1s_page_words[r["page"]].extend(l_s)
        g1c_page_words[r["page"]].extend(l_c)
        h1_page_words[r["page"]].extend(l_h)

    for label, pw_map in [
        ("VOYNICH (real)", real_page_words),
        ("G1 seed_L200", g1s_page_words),
        ("G1 circular", g1c_page_words),
        ("H1 flow_cipher", h1_page_words),
        ("C K2_nomen_x2", k2_x2_pages),
    ]:
        res = page_continuity_test(page_order, page_strata, pw_map, seed=SEED, n_perm=N_PERM)
        mu_rv, sd_rv, z_rv, p_rv = res["rv_stats"]
        mu_adj, sd_adj, z_adj, p_adj = res["adj_stats"]
        tmu_rv, tsd_rv, tz_rv, tp_rv = res["rv_tok_stats"]
        tmu_adj, tsd_adj, tz_adj, tp_adj = res["adj_tok_stats"]
        emit(
            f"{label:18} [page-shuf]  | RV (n={res['n_rv']:2d}): obs={res['obs_rv']:.4f} "
            f"null={mu_rv:.4f}+/-{sd_rv:.4f} z={z_rv:+6.2f} p={p_rv:.4f} | "
            f"Adj (n={res['n_adj']:3d}): obs={res['obs_adj']:.4f} "
            f"null={mu_adj:.4f}+/-{sd_adj:.4f} z={z_adj:+6.2f} p={p_adj:.4f}"
        )
        emit(
            f"{label:18} [len-presv]  | RV (n={res['n_rv']:2d}): obs={res['obs_rv']:.4f} "
            f"null={tmu_rv:.4f}+/-{tsd_rv:.4f} z={tz_rv:+6.2f} p={tp_rv:.4f} | "
            f"Adj (n={res['n_adj']:3d}): obs={res['obs_adj']:.4f} "
            f"null={tmu_adj:.4f}+/-{tsd_adj:.4f} z={tz_adj:+6.2f} p={tp_adj:.4f}"
        )

    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
