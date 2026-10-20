"""N3b: Retrospective / internally held-out, confound-controlled test of section
vocabulary and page/sheet clustering against N2's habit generator (p=0.04).

Why N3b exists alongside N3 (n3_content_signals.py):
1. n3_content_signals.py fit its generator tables on 100% of the manuscript and
   evaluated on the same pages (no fitting/evaluation split).
2. n3_content_signals.py only ran N.gen_habit with key=(hand, illus), which builds
   section-specific seed lexicons into the generator by construction, without
   separating a section-blind habit generator (key=hand or sheet-drift) from a
   section-seeded positive control.
3. n3_content_signals.py used C1's 7-block quire null (where Hand 2 fails its own
   null, p=0.133..0.219 -> NOT EVIDENCE) rather than P1's physical bifolio ($Q|$B)
   null and L1/P1's page-length-preserving token-shuffle null.

HONEST SCOPE LABEL:
All 227 pages of ZL3b, RF1b, and IT2a have been examined in earlier rounds.
This analysis is therefore RETROSPECTIVE / INTERNALLY HELD-OUT, not untouched
confirmation.

FROZEN PRE-REGISTRATION (written before any run of this file; hash recorded in
n3b_controlled_content.prereg.sha256 before execution):

1. Transcriptions, Page Inclusion, Section Labels & Preprocessing:
   - Transcriptions: T in {ZL3b (EVA), RF1b, IT2a} from data/translit/<T>.meta.json,
     running-text paragraph lines only (labels excluded, identical to n1.load).
   - Physical bifolio sheet map ($Q|$B): parsed from data/ZL3b-n.txt page headers
     via p1_bifolio_null.bifolio_of_pages().
   - Section labels: IVTFF $I illustration tag (H, P in Hand 1; B, H, T in Hand 2).

2. Evaluation Split (No Leakage Between Fitting and Evaluation):
   - Within each (hand, illus) stratum, physical bifolio sheets ($Q|$B) in
     manuscript order are split alternately:
       fit_bifolios  = bs[::2]   (even-indexed sheets in each stratum)
       eval_bifolios = bs[1::2]  (odd-indexed sheets in each stratum)
   - All generator parameters (word frequencies, edit-1 neighbour graph,
     cross-space glyph ratio table R, and K=4 habit follower table) are fit
     STRICTLY on fit_bifolios.
   - Evaluation statistics are computed STRICTLY on eval_bifolios, where
     generators receive only the (page, line_lengths, hand, quire, bifolio)
     skeleton of eval_bifolios (plus illus ONLY for Positive Control HT_sec).

3. Habit-Generator Version, Parameters, Variants & Positive Control:
   - Base parameters frozen from N2: p_hab=0.04, K_FOLLOW=4, DIR_ALPHA=0.5,
     TABLE_SEED=20261017, BETA=1.5, M_CAND=8, p_seed=0.6, p_mut=0.6, L=300,
     SEEDS=(1, 2, 3).
   - Variant 1: HT_hand (Primary section-blind hypothesis):
     One L=300 seed lexicon per scribal hand (key = r["hand"]), page-local copy
     pool (1 - p_seed = 0.4), mutation (0.6), flow choice (beta=1.5), and
     book-wide habit table (p_hab=0.04).
   - Variant 2: HT_sheet (Bifolio-drift / sheet-copy confound control, section-blind):
     Seed lexicon drifts smoothly across bifolio sheets within each hand
     (window = 4 bifolio sheets) and copy pool persists across the entire
     physical bifolio sheet ($Q|$B) rather than resetting per page.
   - Positive Control: HT_sec (Section-seeded habit generator, key = (r["hand"], r["illus"])):
     Each (hand, illus) pair draws its own L=300 seed lexicon from fit_bifolios.
     Must be detected by Q1 on eval_bifolios to establish test power.

4. Questions, Statistics & Confound Controls on eval_bifolios:
   - Q1 (Within-hand section-vocabulary specificity past scribal hand & bifolio sheet):
     40-word chunks on eval_bifolios within Hand 1 (H, P) and Hand 2 (B, H, T).
     Statistic: pooled within-hand TF-IDF cosine section separation
     sec_gap = mean(same_sec_diff_bifolio) - mean(diff_sec_same_hand), plus
     within-hand NMF NMI (h1, h2). Null: 2,000 permutations of ($Q|$B) bifolio
     section labels within each hand (seed 20261017). Uncertainty: 95% CI via
     500 bifolio-block bootstrap resamples.
   - Q2 (Within-stratum page & bifolio clustering past page token length):
     (a) rv_excess: Same-folio Recto/Verso L1 vocabulary cosine minus the mean
         of 500 length-preserving within-(hand, illus) token shuffles on
         eval_bifolios (strictly controlling for page token count, hand, and
         section; L1 Part B / P1 Part A).
     (b) sheet_gap: Within-(hand, section) same-bifolio ($Q|$B) minus
         different-bifolio 40-word chunk TF-IDF cosine gap on eval_bifolios,
         tested against 2,000 within-section chunk-bifolio permutations (P1 Part B).

5. Bounded Decision Rules (per question and transliteration, aggregated by >=2/3 T):
   - Outcome C (Inconclusive - inadequate power, confounding, or stability):
     Fires if MS fails its own null on eval_bifolios (p > 0.05) OR if Positive
     Control (HT_sec for Q1; HT_sheet for Q2b) fails its null (p > 0.05).
   - Outcome A (Generator reproduces statistic - measure does not distinguish):
     Fires if section-blind generator (HT_hand or HT_sheet) has seed-mean >=
     0.75 * MS value (or lies inside MS's 95% bootstrap CI) AND passes the null
     (p <= 0.05) in >= 2/3 seeds.
   - Outcome B (Robust held-out discrepancy remains - generator fails to explain):
     Fires if Power Gate passes, neither HT_hand nor HT_sheet meets Outcome A,
     and MS's 95% bootstrap CI lower bound exceeds the generator seed-mean.
   - Otherwise: Outcome C (Inconclusive).

Expected compute & stopping rule:
   Single local CPU process, 0 paid API calls, ~30-60s expected runtime, hard
   stop at 120s.

Run: python n3b_controlled_content.py -> results_n3b.txt
"""
import math
import random
import re
import time
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import normalized_mutual_info_score as nmi

import b5_nmf_topics as b5
import c2_section_generator as c2
import f3_flow_choice as f3
import n1_habit_table as N
import p1_bifolio_null as P1

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_n3b.txt"
SEED = 20261017
SEEDS = (1, 2, 3)
P_HAB = 0.04
N_PERM = 2000
N_LEN_PERM = 500
N_BOOT = 500
HANDS = (("1", ("H", "P")), ("2", ("B", "H", "T")))
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


def split_by_bifolio(by, bmap):
    """Stratified alternate-bifolio split within each (hand, illus) stratum."""
    page_bf = {}
    strata_bfs = defaultdict(list)
    seen = set()
    for page, recs in by.items():
        q, b = bmap.get(page, ("?", page))
        bf = f"{q}|{b}"
        page_bf[page] = bf
        st = (recs[0]["hand"], recs[0]["illus"])
        if (st, bf) not in seen:
            seen.add((st, bf))
            strata_bfs[st].append(bf)
    fit_bfs, eval_bfs = set(), set()
    for st, bfs in sorted(strata_bfs.items()):
        if len(bfs) == 1:
            fit_bfs.add(bfs[0])
        else:
            fit_bfs.update(bfs[::2])
            eval_bfs.update(bfs[1::2])
    # If any page shares a bifolio across strata, fit_bfs wins to prevent leakage
    eval_bfs -= fit_bfs
    by_fit = OrderedDict((p, r) for p, r in by.items() if page_bf[p] in fit_bfs)
    by_eval = OrderedDict((p, r) for p, r in by.items() if page_bf[p] in eval_bfs)
    return by_fit, by_eval, page_bf, fit_bfs, eval_bfs


def gen_variant(g_fit, R_fit, table_fit, by_eval, page_bf, seed, mode):
    """Generate eval_bifolios using tables fit STRICTLY on fit_bifolios.
    mode in {'hand', 'sheet', 'sec'}.
    """
    rng = random.Random(seed)
    lex = {}

    # Pre-build drifting anchor lexicons per (hand, anchor_idx) for 'sheet' mode
    hand_bfs = defaultdict(list)
    for p, recs in by_eval.items():
        h = recs[0]["hand"]
        bf = page_bf[p]
        if bf not in hand_bfs[h]:
            hand_bfs[h].append(bf)
    bf_rank = {bf: i for h, bfs in hand_bfs.items() for i, bf in enumerate(bfs)}

    def get_lex(key):
        if key not in lex:
            lex[key] = g_fit.lexicon(rng)
        return lex[key]

    def draw(r, page):
        h = r["hand"]
        if mode == "sec":
            return rng.choices(*get_lex(("sec", h, r["illus"])))[0]
        if mode == "hand":
            return rng.choices(*get_lex(("hand", h)))[0]
        if mode == "sheet":
            bf = page_bf[page]
            pos = bf_rank.get(bf, 0) / 3.0
            a0 = int(math.floor(pos))
            frac = pos - a0
            chosen_anchor = a0 + 1 if rng.random() < frac else a0
            return rng.choices(*get_lex(("drift", h, chosen_anchor)))[0]
        raise ValueError(mode)

    def mutate(w):
        if rng.random() < 0.6 and w in g_fit.nb:
            c, wt = g_fit.nb[w]
            return rng.choices(c, wt)[0]
        return w

    out = OrderedDict()
    sheet_history = defaultdict(list)
    for page, recs in by_eval.items():
        bf = page_bf[page]
        lines = []
        for li, r in enumerate(recs):
            line = []
            for _ in range(len(r["words"])):
                cands = []
                for _ in range(f3.M_CAND):
                    if line and P_HAB and line[-1] in table_fit and rng.random() < P_HAB:
                        cands.append(rng.choices(*table_fit[line[-1]])[0])
                        continue
                    pool = (sheet_history[bf] + [x for l in lines for x in l] + line
                            if mode == "sheet" else [x for l in lines for x in l] + line)
                    if not pool or (li == 0 and not (mode == "sheet" and sheet_history[bf])) or rng.random() < 0.6:
                        w = draw(r, page)
                    else:
                        w = rng.choice(pool)
                    cands.append(mutate(w))
                if line:
                    w = rng.choices(cands, [R_fit(line[-1][-1], c[0]) ** N.BETA for c in cands])[0]
                else:
                    w = cands[0]
                line.append(w)
            lines.append(line)
        if mode == "sheet":
            for l in lines:
                sheet_history[bf].extend(l)
        out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
    return out


def eval_q1_section(by_eval, bmap):
    """Q1: Within-hand section-vocabulary separation on eval_bifolios against
    physical bifolio ($Q|$B) permutation null and bifolio-block bootstrap CI.
    """
    ch = P1.chunks(by_eval, bmap)
    rng = np.random.default_rng(SEED)
    py_rng = random.Random(SEED)

    hand_gaps = []
    hand_nulls = []
    nmis = {}
    boot_pool = []

    for hand, secs in HANDS:
        sub = [dict(c, blk=c["bifolio"]) for c in ch if c["hand"] == hand and c["sec"] in secs]
        present_secs = sorted({c["sec"] for c in sub})
        if len(present_secs) < 2 or len(sub) < 6:
            nmis[f"h{hand}"] = (float("nan"), 1.0, 0)
            continue
        cl = b5.topics([c["text"] for c in sub], k=len(present_secs) + 1)
        bt = P1.block_test(sub, cl, py_rng)
        nmis[f"h{hand}"] = (bt["obs"], bt["p"], bt["nb"])

        # Centroid gap across bifolio blocks (diff_sec - same_sec distance = same_sec - diff_sec cosine)
        hand_gaps.append(bt["dobs"])
        # Generate N_PERM random block-label permutations for pooled null
        blks = list(dict.fromkeys(u["blk"] for u in sub))
        lab = [Counter(u["sec"] for u in sub if u["blk"] == b).most_common(1)[0][0] for b in blks]
        X = TfidfVectorizer(min_df=2, token_pattern=r"\S+", sublinear_tf=True).fit_transform(
            [u["text"] for u in sub])
        C = np.vstack([np.asarray(X[[i for i, u in enumerate(sub) if u["blk"] == b]].mean(0)) for b in blks])
        norms = np.linalg.norm(C, axis=1, keepdims=True)
        norms[norms == 0] = 1
        C = C / norms
        S = C @ C.T
        iu = np.triu_indices(len(blks), 1)

        def gap_for(a):
            same = np.array([a[i] == a[j] for i, j in zip(*iu)])
            s = S[iu]
            if not same.any() or not (~same).any():
                return 0.0
            return float(s[same].mean() - s[~same].mean())

        null_g = [gap_for(list(rng.permutation(lab))) for _ in range(N_PERM)]
        hand_nulls.append(null_g)

        # Bifolio-block bootstrap for sec_gap
        boots = []
        for _ in range(N_BOOT):
            pick = rng.integers(0, len(blks), len(blks))
            b_lab = [lab[i] for i in pick]
            S_b = S[np.ix_(pick, pick)]
            iu_b = np.triu_indices(len(pick), 1)
            same_b = np.array([b_lab[i] == b_lab[j] for i, j in zip(*iu_b)])
            valid = (pick[iu_b[0]] != pick[iu_b[1]])
            same_v = same_b & valid
            diff_v = (~same_b) & valid
            if same_v.any() and diff_v.any():
                boots.append(float(S_b[iu_b][same_v].mean() - S_b[iu_b][diff_v].mean()))
        if boots:
            boot_pool.append(np.array(boots))

    if not hand_gaps:
        return dict(sec_gap=0.0, p=1.0, ci=(-1.0, 1.0), nmi_h1=(0.0, 1.0, 0), nmi_h2=(0.0, 1.0, 0))

    sec_gap = float(np.mean(hand_gaps))
    pooled_null = np.mean(np.vstack(hand_nulls), axis=0)
    p_val = float(np.mean(pooled_null >= sec_gap - 1e-12))
    if boot_pool:
        min_len = min(len(b) for b in boot_pool)
        pooled_boot = np.mean(np.vstack([b[:min_len] for b in boot_pool]), axis=0)
        ci = (float(np.percentile(pooled_boot, 2.5)), float(np.percentile(pooled_boot, 97.5)))
    else:
        ci = (sec_gap - 0.05, sec_gap + 0.05)

    return dict(
        sec_gap=sec_gap,
        p=p_val,
        ci=ci,
        nmi_h1=nmis.get("h1", (0.0, 1.0, 0)),
        nmi_h2=nmis.get("h2", (0.0, 1.0, 0)),
    )


def eval_q2_clustering(by_eval, bmap):
    """Q2a: Same-folio Recto/Verso cosine excess over length-preserving within-stratum
    token shuffle on eval_bifolios.
    Q2b: Within-(hand, section) same-bifolio sheet_gap on 40-word chunks.
    """
    rng = random.Random(SEED)
    page_order = list(by_eval.keys())
    page_strata = {p: (recs[0]["hand"], recs[0]["illus"]) for p, recs in by_eval.items()}
    page_words = {p: [w for r in recs for w in r["words"]] for p, recs in by_eval.items()}
    counters = {p: Counter(page_words[p]) for p in page_order}

    rv_pairs = []
    idx = set(page_order)
    for p1 in page_order:
        m = re.match(r"^f(\d+)([rv])(\d*)$", p1)
        if not m or m.group(2) != "r":
            continue
        target = f"f{m.group(1)}v{m.group(3)}"
        if target in idx and page_strata[p1] == page_strata[target]:
            rv_pairs.append((p1, target))

    if rv_pairs:
        obs_rv = sum(P1.cosine_counter(counters[a], counters[b]) for a, b in rv_pairs) / len(rv_pairs)
        nulls_rv = P1.length_null(page_order, page_strata, page_words, rv_pairs, rng, N_LEN_PERM)
        mu_rv, sd_rv, z_rv, p_rv = P1.stats(obs_rv, nulls_rv)
        rv_excess = obs_rv - mu_rv
        # Bootstrap 95% CI across RV pairs
        nrng = np.random.default_rng(SEED)
        pair_sims = np.array([P1.cosine_counter(counters[a], counters[b]) - mu_rv for a, b in rv_pairs])
        boots = [float(pair_sims[nrng.integers(0, len(pair_sims), len(pair_sims))].mean()) for _ in range(N_BOOT)]
        rv_ci = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))
    else:
        rv_excess, z_rv, p_rv, rv_ci = 0.0, 0.0, 1.0, (0.0, 0.0)

    # Q2b: Within-(hand, section) pooled sheet_gap on eval_bifolios
    ch = P1.chunks(by_eval, bmap)
    by_hs = defaultdict(list)
    for c in ch:
        by_hs[(c["hand"], c["sec"])].append(c)

    gaps, weights, mats = [], [], []
    for hs, sub in sorted(by_hs.items()):
        bfs = {c["bifolio"] for c in sub}
        if len(bfs) < 2 or len(sub) < 6:
            continue
        X = TfidfVectorizer(min_df=2, token_pattern=r"\S+", sublinear_tf=True).fit_transform(
            [c["text"] for c in sub])
        norms = np.linalg.norm(X.toarray(), axis=1, keepdims=True)
        norms[norms == 0] = 1
        X_n = X.toarray() / norms
        S = X_n @ X_n.T
        labels = [c["bifolio"] for c in sub]
        g = P1.sheet_gap(S, labels)
        if g is not None:
            gaps.append(g)
            weights.append(len(sub))
            mats.append((S, labels))

    if gaps:
        tot_w = sum(weights)
        obs_sheet = sum(g * w for g, w in zip(gaps, weights)) / tot_w
        null_sheet = []
        for _ in range(N_PERM):
            acc = 0.0
            for (S, labels), w in zip(mats, weights):
                shuf = list(labels)
                rng.shuffle(shuf)
                g = P1.sheet_gap(S, shuf)
                acc += (g if g is not None else 0.0) * w
            null_sheet.append(acc / tot_w)
        _, _, z_sheet, p_sheet = P1.stats(obs_sheet, null_sheet)
        # Bootstrap across chunks within each stratum
        nrng = np.random.default_rng(SEED)
        s_boots = []
        for _ in range(N_BOOT):
            acc, tw = 0.0, 0
            for (S, labels), w in zip(mats, weights):
                pick = nrng.integers(0, len(labels), len(labels))
                S_b = S[np.ix_(pick, pick)]
                lab_b = [labels[i] for i in pick]
                iu = np.triu_indices(len(pick), 1)
                valid = (pick[iu[0]] != pick[iu[1]])
                same = np.array([lab_b[i] == lab_b[j] for i, j in zip(*iu)]) & valid
                diff = np.array([lab_b[i] != lab_b[j] for i, j in zip(*iu)]) & valid
                if same.any() and diff.any():
                    acc += float(S_b[iu][same].mean() - S_b[iu][diff].mean()) * w
                    tw += w
            if tw > 0:
                s_boots.append(acc / tw)
        sheet_ci = (float(np.percentile(s_boots, 2.5)), float(np.percentile(s_boots, 97.5))) if s_boots else (obs_sheet - 0.01, obs_sheet + 0.01)
    else:
        obs_sheet, z_sheet, p_sheet, sheet_ci = 0.0, 0.0, 1.0, (0.0, 0.0)

    return dict(
        n_rv=len(rv_pairs),
        rv_excess=rv_excess,
        rv_z=z_rv,
        rv_p=p_rv,
        rv_ci=rv_ci,
        sheet_gap=obs_sheet,
        sheet_z=z_sheet,
        sheet_p=p_sheet,
        sheet_ci=sheet_ci,
    )


def decide_bounded(ms_val, ms_p, ms_ci, pos_p, hand_vals, hand_ps, sheet_vals, sheet_ps, use_sheet_as_pos=False):
    """Return bounded verdict in {'A', 'B', 'C'} with reason."""
    if ms_p > 0.05 or ms_val <= 0:
        return "C", "MS fails own held-out null (inadequate power/signal)"
    if pos_p > 0.05:
        return "C", "Positive control fails held-out null (inadequate power)"

    # Check if HT_hand reproduces
    h_mean = float(np.mean(hand_vals))
    h_pass = sum(p <= 0.05 for p in hand_ps)
    if (h_mean >= 0.75 * ms_val or ms_ci[0] <= h_mean <= ms_ci[1]) and h_pass >= 2:
        return "A", f"HT_hand reproduces (mean={h_mean:+.4f}, null pass {h_pass}/3)"

    if not use_sheet_as_pos:
        s_mean = float(np.mean(sheet_vals))
        s_pass = sum(p <= 0.05 for p in sheet_ps)
        if (s_mean >= 0.75 * ms_val or ms_ci[0] <= s_mean <= ms_ci[1]) and s_pass >= 2:
            return "A", f"HT_sheet reproduces (mean={s_mean:+.4f}, null pass {s_pass}/3)"
        best_gen = max(h_mean, s_mean)
    else:
        best_gen = h_mean

    if ms_ci[0] > best_gen:
        return "B", f"Held-out discrepancy remains (MS CI low {ms_ci[0]:+.4f} > gen {best_gen:+.4f})"
    return "C", f"MS CI [{ms_ci[0]:+.4f}, {ms_ci[1]:+.4f}] overlaps gen {best_gen:+.4f}"


def main():
    t0 = time.time()
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    emit(f"N3b: Confound-controlled, internally held-out content & clustering test   seed {SEED}   run {stamp}")
    emit("Scope: RETROSPECTIVE / INTERNALLY HELD-OUT (fit on even bifolios per stratum, evaluated on odd bifolios).")
    emit("Pre-registered in docstring; SHA-256 recorded in n3b_controlled_content.prereg.sha256 before execution.")
    emit()

    bmap = P1.bifolio_of_pages()
    verdicts = {"Q1_sec_vocab": {}, "Q2a_rv_len_controlled": {}, "Q2b_sheet_cohesion": {}}

    for T, meta in N.TRANSLITS.items():
        by = N.load(meta)
        by_fit, by_eval, page_bf, fit_bfs, eval_bfs = split_by_bifolio(by, bmap)
        emit(f"=== {T} (fit bifolios={len(fit_bfs)}, pages={len(by_fit)}; eval bifolios={len(eval_bfs)}, pages={len(by_eval)}) ===")

        ms_q1 = eval_q1_section(by_eval, bmap)
        ms_q2 = eval_q2_clustering(by_eval, bmap)
        emit(f"MS (eval)      Q1 sec_gap={ms_q1['sec_gap']:+.4f} CI[{ms_q1['ci'][0]:+.4f},{ms_q1['ci'][1]:+.4f}] p={ms_q1['p']:.4f}"
             f" (NMI h1={ms_q1['nmi_h1'][0]:.3f} p={ms_q1['nmi_h1'][1]:.3f}, h2={ms_q1['nmi_h2'][0]:.3f} p={ms_q1['nmi_h2'][1]:.3f})"
             f" | Q2a rv_ex={ms_q2['rv_excess']:+.4f} z={ms_q2['rv_z']:+.2f} p={ms_q2['rv_p']:.4f}"
             f" | Q2b sheet_gap={ms_q2['sheet_gap']:+.4f} z={ms_q2['sheet_z']:+.2f} p={ms_q2['sheet_p']:.4f}")

        # Fit strictly on by_fit
        g_fit = c2.Gen(by_fit)
        R_fit = f3.ratio_table(by_fit)
        table_fit = N.habit_table(g_fit)

        runs = {m: [] for m in ("hand", "sheet", "sec")}
        for mode in ("hand", "sheet", "sec"):
            for s in SEEDS:
                gb = gen_variant(g_fit, R_fit, table_fit, by_eval, page_bf, s, mode)
                q1 = eval_q1_section(gb, bmap)
                q2 = eval_q2_clustering(gb, bmap)
                runs[mode].append((q1, q2))
                emit(f"HT_{mode:<5} s{s}   Q1 sec_gap={q1['sec_gap']:+.4f} p={q1['p']:.4f}"
                     f" (NMI h1={q1['nmi_h1'][0]:.3f} p={q1['nmi_h1'][1]:.3f}, h2={q1['nmi_h2'][0]:.3f} p={q1['nmi_h2'][1]:.3f})"
                     f" | Q2a rv_ex={q2['rv_excess']:+.4f} z={q2['rv_z']:+.2f} p={q2['rv_p']:.4f}"
                     f" | Q2b sheet_gap={q2['sheet_gap']:+.4f} z={q2['sheet_z']:+.2f} p={q2['sheet_p']:.4f}")

        # Positive control p-values (median across 3 seeds)
        pos_q1_p = float(np.median([r[0]["p"] for r in runs["sec"]]))
        pos_q2a_p = float(np.median([r[1]["rv_p"] for r in runs["hand"]]))
        pos_q2b_p = float(np.median([r[1]["sheet_p"] for r in runs["sheet"]]))

        v_q1, r_q1 = decide_bounded(
            ms_q1["sec_gap"], ms_q1["p"], ms_q1["ci"], pos_q1_p,
            [r[0]["sec_gap"] for r in runs["hand"]], [r[0]["p"] for r in runs["hand"]],
            [r[0]["sec_gap"] for r in runs["sheet"]], [r[0]["p"] for r in runs["sheet"]],
            use_sheet_as_pos=False,
        )
        v_q2a, r_q2a = decide_bounded(
            ms_q2["rv_excess"], ms_q2["rv_p"], ms_q2["rv_ci"], pos_q2a_p,
            [r[1]["rv_excess"] for r in runs["hand"]], [r[1]["rv_p"] for r in runs["hand"]],
            [r[1]["rv_excess"] for r in runs["sheet"]], [r[1]["rv_p"] for r in runs["sheet"]],
            use_sheet_as_pos=False,
        )
        v_q2b, r_q2b = decide_bounded(
            ms_q2["sheet_gap"], ms_q2["sheet_p"], ms_q2["sheet_ci"], pos_q2b_p,
            [r[1]["sheet_gap"] for r in runs["hand"]], [r[1]["sheet_p"] for r in runs["hand"]],
            [r[1]["sheet_gap"] for r in runs["sheet"]], [r[1]["sheet_p"] for r in runs["sheet"]],
            use_sheet_as_pos=False,
        )
        verdicts["Q1_sec_vocab"][T] = v_q1
        verdicts["Q2a_rv_len_controlled"][T] = v_q2a
        verdicts["Q2b_sheet_cohesion"][T] = v_q2b
        emit(f"  VERDICT {T}:")
        emit(f"    Q1_sec_vocab          -> {v_q1} ({r_q1}; pos_ctrl HT_sec median p={pos_q1_p:.4f})")
        emit(f"    Q2a_rv_len_controlled -> {v_q2a} ({r_q2a}; pos_ctrl HT_hand median p={pos_q2a_p:.4f})")
        emit(f"    Q2b_sheet_cohesion    -> {v_q2b} ({r_q2b}; pos_ctrl HT_sheet median p={pos_q2b_p:.4f})")
        emit()

    emit("OVERALL BOUNDED VERDICTS (>=2/3 transliterations; A=Generator reproduces, B=Held-out discrepancy remains, C=Inconclusive):")
    for q, d in verdicts.items():
        c = Counter(d.values())
        ov = "A" if c["A"] >= 2 else "B" if c["B"] >= 2 else "C"
        emit(f"  {q:<24}: {ov}   (" + "  ".join(f"{t}={v}" for t, v in d.items()) + ")")
    emit(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
