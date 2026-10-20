"""S49 (P4-D3, decision D-052): the identifiability (confusion-matrix) study.

QUESTION: on KNOWN texts at Voynich size, can the project's statistics tell a cipher from a generator from a
language from gibberish?  If they cannot, no cipher-vs-generator verdict read from them means anything.

PRE-REGISTRATION (frozen in s49_identifiability.prereg.sha256 before any generation or scoring run that is
reported; workflow/research/phase-4-decipherability.md section Q2 governs; where Q2 leaves a choice it is fixed
here and marked [CHOICE]; where this design departs from Q2 it is marked [DEVIATION]).  Mechanisms, corpus,
features, classifiers and pass/fail rules below are fixed before the run and scored once.

CORPUS: 30 texts, 5 classes x 6, every text 38,000 tokens [Q2] on real lines or on the Voynich line profile.
  Voynich-profile skeleton [CHOICE]: the transliteration's own pages/lines (s27.load_T: hand, illus, quire,
    para_start), in manuscript order, then repeated from the first page (page ids suffixed ~r1) until 38,000
    tokens; the last line is cut to fit.  All mechanism tables (pools, M2, R_la_syll, c2.Gen, SlotSegmenter,
    habit tables) are built from the untouched transliteration; only the writing runs on the skeleton.
  Real-line texts are truncated to their first 38,000 tokens in source page/line order (last line cut).
  F1 needs quires: Voynich-skeleton texts keep the manuscript quires; every other text gets quire blocks of
    consecutive pages, a new quire when 2,000 tokens have been passed (Q000, Q001, ...) [CHOICE].
  Classes and members (sidecars in the project dialect under runs/s49/, labels in runs/s49/labels.json):
  LANG  natural language on real lines (data/controls_realline + data/controls):
        lang_latin_cremma (cremma_all, Latin), lang_italian_dante (page 'front' dropped), lang_mhg_nibelungenlied,
        lang_occitan_croisade, lang_oldfrench_roland (ONLY 29,524 tokens on disk: used whole, flagged SHORT),
        lang_mhg_parzival ("one more real-line language": data/controls/mhg_parzival.txt verse lines, a2.verse_lines
        rule without the 5000-line cap, 30 lines per page).  [CHOICE] Parzival is MHG like the Nibelungenlied; the
        only other-language real-line text on disk, german_faust, has 29,541 tokens, so a second short text was
        not added.  Q2's C5 "script controls" class is replaced by this class as the brief asks [DEVIATION].
  CIPH  verbose homophonic cipher with nulls (s10 mechanism: s10.gen_s10_cipher loop re-implemented with ONE
        plaintext iterator in reading order, cycled if exhausted; s31 M5 line-edge pools, R_la_syll flow choice
        M_CAND 8 beta 1.5, redup 0.0085, M2 mid-line null words - all as s10) on the ZL3b Voynich-profile
        skeleton.  Plaintexts = the word streams of the first five LANG texts (Latin, Italian, MHG-Nib, Occitan,
        Old French; Roland cycles).  Varied keys, drawn per text from random.Random(SEED + 100 * i) [Q2 frozen
        range]: homophones per vowel U{3..6}, per consonant U{2..4} [CHOICE: s10's consonant floor 2], null rate
        U(0.05, 0.20) (no calibration), piece list (ZL3b unigram glyphs then bigrams by frequency, s10) shuffled
        within consecutive blocks of 8 before the rank assignment.  Generation seed i.
        Sixth member: L_2layer_ZL3b_s1 (s36.TwoLayerModel.generate_L, ZL3b, seed 1), as the brief asks.
  CODE  word code / nomenclator, K4-style: k4.build_shared_codebook at the s27 middle setting (pool_cap 7025,
        k_choices 6, rank_window 180, beta 1.8) over the plaintext's own word types, codebook seed SEED + i;
        k4.encrypt_shared loop re-implemented with ONE plaintext iterator (cycled), Voynich R = f3.ratio_table,
        Qi/Qe/para = k1.line_tables (ZL3b), ZL3b skeleton; plaintexts = all six LANG texts; seed i.
        Q2's C2 Naibbe class is replaced by this class as the brief asks [DEVIATION].
  GEN   procedural generators: gen_s28_ZL3b_s1 (s28 mechanism verbatim, lam re-calibrated by s28's 14-step
        bisection on seed 0 to the type count scaled to 38k, target = round(7025 * (38000 / 34857) ** 0.68)
        [CHOICE, Heaps exponent of s36]); gen_c2_section (c2.Gen.generate with the c2_best kwargs, mode section,
        seed 2, p_seed 0.8, rule_p 0.088, rule_m 0.148, on the skeleton); gen_timm_schinner
        (data/controls_synthetic/timm_schinner_ownlines, its own lines, truncated to 38k); gen_schwartz_reuse
        (ctl_schwartz.HandModel per hand on ctl_common.voynich_pages, betas FROM schwartz_reuse.meta.json 'fit',
        ctl_schwartz.generate on that template extended to 38k, seed 20261017); gen_rugg_grille
        (ctl_generators.rugg_grille + layout, Random(SEED + 10), N_TOKENS set to 38000, own lines);
        gen_G2layer_ZL3b_s1 (s36.TwoLayerModel.generate_G, ZL3b, seed 1), as the brief asks.
  GIB   human gibberish: gib_realline_pooled (38 writers, 10,023 tokens) resampled into six 38k pseudo-texts by
        writer blocks (whole writer pages drawn with replacement, random.Random(SEED + 600 + j), j = 1..6).
        LIMITATION (stated, Q2 flags this class as weak): each pseudo-text repeats every writer ~3.8 times on
        average and the six share one 10k pool, so GIB members are near-copies of each other; GIB accuracy is
        optimistic and says nothing about unseen gibberish writers.  Q2's Markov-of-gibberish members are not
        built (the brief asks for resampling) [DEVIATION].
  Two-layer producers (s36): s36.TwoLayerModel(T, by, ids41) built unchanged on the untouched transliteration,
    then its writing skeleton set to the 38k skeleton, plaintext streams doubled so they cannot run out, and its
    type target scaled by (38k / manuscript tokens) ** 0.68; lam by s36.calibrate_scale (G and L separately),
    p 0.04, as s36.
  TWIN PANEL (Q2 "matched twins ... extendable to 10 pairs"): 10 pairs (G_2layer, L_2layer) from the same model
    and seed: ZL3b seeds 1-4, RF1b seeds 1-3, IT2a seeds 1-3 (each T on its own 38k skeleton).  The ZL3b s1 pair
    is the corpus pair; the other 18 texts are twin-panel only.  The twin question = generator vs message.

FEATURES (26, computed identically on every text and on Voynich; standardised on the training fold only):
  board: the 21 weighted quantities of scoreboard/run_v2.score_one (V1_KEYS + NEW_NUMERIC minus REPORT keys
    x_hapax_10k, info_mi_page, info_bpe_adjacent): h2, sd_len, jsd_first_fg, p_init_enrich, m_final_enrich,
    cross_excess_eva, redup_pct, x_edge_mi_word, types_25k, x_position_entropy, x_ltr_minus_rtl, x_moran_I,
    lex_beta, lex_rate_late_early, lex_edit1_excess, slot_occupancy_pc, slot_table_likeness, slot_core_crowding,
    info_mi_adjacent, info_samecol_minus_othercol, bake_char3_minus_unigram.
  A5 within-line Moran I (s27.moran_stat, s21 estimator); A6 CHARWIN (s27.charwin_stat, m3 page split);
  A7 F1 residual (s27.f1_stat on s27.f1_pages: quire split, TOPN 300, within-line-shuffle corrected; point value);
  A14 core->core excess (p4d1_core_order.core_excess: SlotSegmenter on the text's own tokens, 200 shuffles);
  line-initial excess (s44/s32: a2_position.stats JSD(first glyph, mid) minus the mean of a2.null n = 30).
  cross_excess is the board's cross_excess_eva (counted once).  A feature that errors is NaN and is imputed with
  the training-fold median [CHOICE].  Voynich ZL3b / RF1b / IT2a are scored on their full s27.load_T text
  (34,857 / RF1b / IT2a tokens, NOT 38k: the manuscript is what it is; types_25k is length-fixed) [CHOICE].

CLASSIFIERS (declared, no tuning):
  NC  = nearest centroid, Euclidean in z-space (z from the training fold's mean / sd, sd 0 -> 1), leave-one-text-out.
        Q2 pre-commits this classifier: the gates below are read on NC.
  LDA = sklearn LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto') (Ledoit-Wolf; n < p needs shrinkage),
        same folds and z.  Reported with the same thresholds beside NC; a gate NC passes and LDA fails is
        written "PASS (NC only, not robust to the classifier)".
  Tasks:
   T5  five-class LOO over the 30 texts (confusion matrix, per-class accuracy).
   T2  PRIMARY binary, Q2's C1+C2 vs C3+C4 = (CIPH + CODE) vs (GEN + GIB), 24 texts, LOO on the 24 only.
       NC [CHOICE]: nearest of the four class centroids fitted on the other 23, mapped to its side.
       LDA: two-class LDA on the side labels of the other 23.
   TW  twin task, 10 pairs: train on the 22 non-two-layer texts of the 24 (both corpus two-layer texts always
       held out) [CHOICE]; cipher-likeness s(x) = NC: min distance to {GEN, GIB} centroids minus min distance to
       {CIPH, CODE}; LDA: decision function toward the cipher side.  A pair is correct when s(L_2layer) >
       s(G_2layer).  Reported beside, not gating: the same with the ZL3b s1 two-layer texts kept in training
       (except for the ZL3b s1 pair itself).
  Per-feature univariate AUC for cipher side vs generator side on the 24 (Q2).
  Voynich landing: NC fitted on all 30 (z on the 30): distance to each class centroid, nearest class, margin
    (second-nearest minus nearest); the same on the T2 model (four centroids of the 24 -> side); LDA posteriors;
    bootstrap over features: B = 1000 resamples of the 26 feature columns with replacement
    (np.random.default_rng(20261017)), refit z and centroids, share of resamples per nearest class.

DECISION RULES (Q2, verbatim, frozen):
  - Primary binary task, C1+C2 vs C3+C4 (24 texts): >= 20/24 correct (83 %) for the board to be usable for Tier 2.
    Binomial p vs 0.5 is about 0.0008, and the Clopper-Pearson lower bound is about 0.63. At <= 16/24, the red team
    is confirmed: Tier-2 verdicts from this board are withdrawn, not just weakened.
  - Matched-twin task, which of each pair is the cipher: 2 pairs here, extendable to 10 pairs. It must reach
    >= 9/10 (sign-test p 0.011). Below that, the 7/10-tie problem is structural, and only the non-tied features
    (A5/A6/A7) may be cited.
  - Five-class accuracy, reported but not gating: >= 15/30 (p 0.0002 vs 0.2 chance).
  - A Voynich assignment counts only if the binary classifier passes and Voynich's margin between the two nearest
    centroids exceeds the median margin of correctly classified texts.
  (17-19/24 is between the two binary bars: "not usable for Tier 2; red-team withdrawal bar not reached".)

BLINDING [DEVIATION]: Q2's three-agent blinding (builder / sealed labels / scorer) is not possible in one script.
  Mitigation: everything (mechanisms, features, classifiers, rules) is frozen in this file before the run, the
  classifier has no tuned parameter, and the label file's sha256 is printed before scoring begins.

Smoke run: before the freeze this file was run once with --smoke <scratch dir> (3,000-token texts, all output to
  the scratch dir, not reported) to catch crashes; runs/s49 and results_s49.txt are written only by the real run.
Wall-clock: each phase (generation, scoring) stops with a STOPPED line if it exceeds 90 min.
Constraints: python -I, one CPU process, no GPU, no paid calls, no new data; writes ONLY results_s49.txt and
  runs/s49/; scoreboard/scoreboard.json and data/controls_synthetic/ are never written.
Run: python -I s49_identifiability.py          Writes: results_s49.txt (+ runs/s49/).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
import sys
import time
import unicodedata
from collections import Counter, OrderedDict
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

import a2_position as a2  # noqa: E402
import c2_section_generator as c2  # noqa: E402
import corpora  # noqa: E402
import ctl_common as cc  # noqa: E402
import ctl_generators as cg  # noqa: E402
import ctl_schwartz as csw  # noqa: E402
import f3_flow_choice as f3  # noqa: E402
import k1_joint_producer as k1  # noqa: E402
import k4_lossy_nomenclator as k4  # noqa: E402
import n4_habit7k as n4  # noqa: E402
import n6_habit7k_glyph as n6  # noqa: E402
import p4d1_core_order as P4  # noqa: E402
import s10_cipher_mechanism as s10  # noqa: E402
import s27_k4_bound as L  # noqa: E402  (shared scoring library)
import s28_generator_mechanism as s28  # noqa: E402
import s31_null_glyph_charwin_pilot as s31  # noqa: E402
import s36_two_layer_operator_core as s36  # noqa: E402

SELF = ROOT / "s49_identifiability.py"
STUB = ROOT / "s49_identifiability.prereg.sha256"
SEED = 20261017
N_TOK = 38000
QUIRE_BLOCK = 2000
B_FEAT = 1000
PHASE_LIMIT = 90 * 60
SMOKE = "--smoke" in sys.argv
if SMOKE:
    OUT_DIR = Path(sys.argv[sys.argv.index("--smoke") + 1])
    OUT = OUT_DIR / "results_s49_smoke.txt"
    RUN_DIR = OUT_DIR / "runs_s49"
    N_TOK = 3000
    B_FEAT = 50
else:
    OUT = ROOT / "results_s49.txt"
    RUN_DIR = ROOT / "runs" / "s49"
CLASSES = ["LANG", "CIPH", "CODE", "GEN", "GIB"]
CIPHER_SIDE, GEN_SIDE = ("CIPH", "CODE"), ("GEN", "GIB")
R2 = L.R2
_kinds = dict((a, b) for a, b, _ in R2.NEW_KEYS)
BOARD = [k for k in R2.V1_KEYS + R2.NEW_NUMERIC if _kinds.get(k, "WEIGHTED") != "REPORT"]
EXTRA = ["A5_moran", "A6_charwin", "A7_f1", "A14_core_excess", "line_init_excess"]
FEATS = BOARD + EXTRA
TIED_FREE = ["A5_moran", "A6_charwin", "A7_f1"]
TWIN_SPECS = [("ZL3b", 1), ("ZL3b", 2), ("ZL3b", 3), ("ZL3b", 4), ("RF1b", 1), ("RF1b", 2), ("RF1b", 3),
              ("IT2a", 1), ("IT2a", 2), ("IT2a", 3)]

lines_out: list[str] = []


def emit(s=""):
    print(s, flush=True)
    lines_out.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8", newline="\n")


def guard(t_phase, phase):
    if time.time() - t_phase > PHASE_LIMIT:
        emit(f"STOPPED: phase '{phase}' exceeded {PHASE_LIMIT} s at {L.clock()}; results above are partial")
        flush()
        sys.exit(2)


# ------------------------------------------------------------------ skeletons and text shaping
def extend_by(by, n_tok):
    """Voynich-profile skeleton: pages in order, repeated (ids ~rK) until n_tok tokens; last line cut."""
    out, total, rep = OrderedDict(), 0, 0
    while total < n_tok:
        for page, recs in by.items():
            pid = page if rep == 0 else f"{page}~r{rep}"
            new = []
            for r in recs:
                if total >= n_tok:
                    break
                take = min(len(r["words"]), n_tok - total)
                if take <= 0:
                    continue
                new.append(dict(r, page=pid, words=list(r["words"][:take])))
                total += take
            if new:
                out[pid] = new
            if total >= n_tok:
                break
        rep += 1
    return out


def clean_pages(pages):
    out = []
    for p in pages:
        lines = [[w for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if lines:
            out.append(dict(p, id=str(p.get("id", p.get("page"))), lines=lines))
    return out


def truncate_pages(pages, n_tok):
    out, total = [], 0
    for p in clean_pages(pages):
        lines = []
        for ln in p["lines"]:
            if total >= n_tok:
                break
            take = min(len(ln), n_tok - total)
            lines.append(list(ln[:take]))
            total += take
        if lines:
            out.append(dict(p, lines=lines))
        if total >= n_tok:
            break
    return out


def assign_quires(pages):
    out, cum = [], 0
    for p in pages:
        out.append(dict(p, quire=f"Q{cum // QUIRE_BLOCK:03d}"))
        cum += sum(len(ln) for ln in p["lines"])
    return out


def ntok(pages):
    return sum(len(ln) for p in pages for ln in p["lines"])


def ntypes(pages):
    return len({w for p in pages for ln in p["lines"] for w in ln})


def load_realline(name):
    d = json.loads((ROOT / "data" / "controls_realline" / f"{name}.meta.json").read_text(encoding="utf-8"))
    return [p for p in d["pages"] if p.get("id") != "front"]


def parzival_pages():
    t = corpora.strip_gutenberg((corpora.CTRL / "mhg_parzival.txt").read_text(encoding="utf-8", errors="replace"))
    t = "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")
    lines = [re.findall(r"[a-zß]+", ln) for ln in t.splitlines()]
    lines = [ln for ln in lines if len(ln) >= 3]
    return [dict(id=f"pz{i // 30 + 1:04d}", section="?", hand="?", lang="?", quire=None, lines=lines[i:i + 30])
            for i in range(0, len(lines), 30)]


def plain_words(pages):
    return [w for p in pages for ln in p["lines"] for w in ln]


def cycler(words):
    i = [0]

    def nxt():
        w = words[i[0] % len(words)]
        i[0] += 1
        return w
    nxt.used = i
    return nxt


# ------------------------------------------------------------------ CIPH: s10 mechanism, varied keys, one plaintext iterator
def varied_table(by, plain, krng):
    uni, big = Counter(), Counter()
    for recs in by.values():
        for r in recs:
            for w in r["words"]:
                uni.update(w)
                big.update(w[i:i + 2] for i in range(len(w) - 1))
    pieces = [(p, c) for p, c in uni.most_common()] + [(p, c) for p, c in big.most_common()]
    shuffled = []
    for b in range(0, len(pieces), 8):
        blk = pieces[b:b + 8]
        krng.shuffle(blk)
        shuffled.extend(blk)
    letters = Counter(ch for w in plain for ch in w)
    table, it = {}, iter(shuffled)
    for ch, _ in letters.most_common():
        k = krng.randint(3, 6) if ch in s10.VOWELS else krng.randint(2, 4)
        table[ch] = [next(it) for _ in range(k)]
    return table


def gen_cipher(skel, nextp, table, m2, pools, R_tab, p_null, seed):
    """s10.gen_s10_cipher with nextp() (one plaintext iterator in reading order) in place of the per-key streams."""
    rng = random.Random(seed)
    para_pool, init_pool, fin_pool = pools
    pw = {ch: ([p for p, _ in v], [c for _, c in v]) for ch, v in table.items()}

    def encode(word):
        return "".join(rng.choices(*pw[ch])[0] for ch in word if ch in pw) or "o"

    out = OrderedDict()
    for page, recs in skel.items():
        lines = []
        for r in recs:
            n = len(r["words"])
            line = []
            for i in range(n):
                prev_last = line[-1][-1] if line else None
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(para_pool[0], para_pool[1])[0])
                    continue
                if i == 0 and rng.random() < s10.P_INIT:
                    cands = rng.choices(init_pool[0], init_pool[1], k=s10.M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** s10.BETA) if prev_last else 1.0 for c in cands]
                    line.append(rng.choices(cands, wts)[0])
                    continue
                if i == n - 1 and n >= 3 and rng.random() < s10.P_FIN:
                    cands = rng.choices(fin_pool[0], fin_pool[1], k=s10.M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** s10.BETA) if prev_last else 1.0 for c in cands]
                    line.append(rng.choices(cands, wts)[0])
                    continue
                if line and rng.random() < s10.P_REDUP:
                    line.append(line[-1])
                    continue
                if rng.random() < p_null:
                    w_null = n6.sample_word_m2(m2, rng)
                    line.append(w_null if w_null else "o")
                    continue
                plain_w = nextp()
                cands = [encode(plain_w) for _ in range(s10.M_CAND)]
                wts = [(R_tab(prev_last, c[0]) ** s10.BETA) if prev_last else 1.0 for c in cands]
                line.append(rng.choices(cands, wts)[0])
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


# ------------------------------------------------------------------ CODE: K4 nomenclator, one plaintext iterator
def gen_code(skel, nextp, book, R, Qi, Qe, para, beta, seed):
    """k4.encrypt_shared with nextp() in place of the per-key streams."""
    rng = random.Random(seed)
    ptypes, pwt = list(para), list(para.values())
    out = OrderedDict()
    for page, recs in skel.items():
        lines = []
        for r in recs:
            n = len(r["words"])
            line = []
            for i in range(n):
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pwt)[0])
                    continue
                cands = book[nextp()]
                prev_last = line[-1][-1] if line else None
                weights = []
                for cw, base_w in cands:
                    flow_w = (R(prev_last, cw[0]) ** beta) if prev_last else 1.0
                    pos_w = k1.pos_factor(cw, i, n, Qi, Qe)
                    weights.append(max(base_w * flow_w * pos_w, 1e-9))
                line.append(rng.choices([cw for cw, _ in cands], weights)[0])
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


# ------------------------------------------------------------------ two-layer producers
def two_layer_model(T, by):
    ids41 = L.heldout_ids(by)
    tm = s36.TwoLayerModel(T, by, ids41)
    n_orig = sum(len(r["words"]) for recs in by.values() for r in recs)
    skel = extend_by(by, N_TOK)
    tm.by_full = skel
    tm.streams = {k: list(v) + list(v) + list(v) for k, v in tm.streams.items()}
    tm.target_types = round(tm.target_types * (N_TOK / n_orig) ** 0.68)
    cal = {}
    for mode in ("G", "L"):
        cal[mode] = tm.calibrate_scale(mode)
    return tm, cal


# ------------------------------------------------------------------ features
FEAT1 = (lambda w: w[0])


def features(name, pages):
    pages = clean_pages(pages)
    by = L.pages_to_by(pages)
    f, err = {}, {}
    row = R2.score_one(name, pages, lambda s: None)
    for k in BOARD:
        v = R2.fin(row.get(k))
        f[k] = float("nan") if v is None else float(v)
    for k, e in row.get("errors", {}).items():
        err[f"board:{k}"] = e

    def put(k, fn):
        try:
            f[k] = float(fn())
        except Exception as e:  # noqa: BLE001
            f[k] = float("nan")
            err[k] = f"{type(e).__name__}: {e}"
    put("A5_moran", lambda: L.moran_stat(np.array(list(L.moran_pages(pages).values()))))
    put("A6_charwin", lambda: L.charwin_stat(np.array(list(L.charwin_pages(pages).values()))))
    put("A7_f1", lambda: L.f1_stat(np.array(list(L.f1_pages(by).values()))))
    toks = [w for p in pages for ln in p["lines"] for w in ln]
    lines = [ln for p in pages for ln in p["lines"]]
    put("A14_core_excess", lambda: P4.core_excess(toks, lines)[0])

    def li():
        raw, _ = a2.stats(lines, FEAT1)
        return raw - a2.null(lines, FEAT1, n=30)[:, 0].mean()
    put("line_init_excess", li)
    return f, err


# ------------------------------------------------------------------ classifiers
def prep(Xtr, Xte):
    Xtr = np.array(Xtr, dtype=float); Xte = np.array(Xte, dtype=float)
    if Xte.ndim == 1:
        Xte = Xte[None, :]
    med = np.nanmedian(np.where(np.isfinite(Xtr), Xtr, np.nan), axis=0) if np.isfinite(Xtr).any() else np.zeros(Xtr.shape[1])
    med = np.where(np.isfinite(med), med, 0.0)
    Xtr = np.where(np.isfinite(Xtr), Xtr, med); Xte = np.where(np.isfinite(Xte), Xte, med)
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    return (Xtr - mu) / sd, (Xte - mu) / sd


def centroids(Z, y, classes):
    return {c: Z[[i for i, t in enumerate(y) if t == c]].mean(0) for c in classes}


def dists(z, cents):
    return {c: float(np.linalg.norm(z - m)) for c, m in cents.items()}


def lda_fit(Z, y):
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    m = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    m.fit(Z, y)
    return m


def side(c):
    return "cipher" if c in CIPHER_SIDE else ("generator" if c in GEN_SIDE else "language")


def binom_p_ge(k, n, p=0.5):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def cp_lower(k, n, a=0.05):
    if k == 0:
        return 0.0
    from scipy.stats import beta
    return float(beta.ppf(a / 2, k, n - k + 1))


def auc(pos, neg):
    pos = [x for x in pos if math.isfinite(x)]; neg = [x for x in neg if math.isfinite(x)]
    if not pos or not neg:
        return float("nan")
    s = 0.0
    for a in pos:
        for b in neg:
            s += 1.0 if a > b else (0.5 if a == b else 0.0)
    return s / (len(pos) * len(neg))


def confusion(true, pred, labels):
    M = {t: Counter() for t in labels}
    for t, p in zip(true, pred):
        M[t][p] += 1
    return M


def emit_conf(title, M, labels, cols=None):
    cols = cols or labels
    emit(title)
    hdr = "true / pred"
    emit(f"  {hdr:12s} " +" ".join(f"{c:>9s}" for c in cols) + "   correct")
    for t in labels:
        emit(f"  {t:12s} " + " ".join(f"{M[t][c]:9d}" for c in cols) + f"   {M[t][t] if t in cols else 0}/{sum(M[t].values())}")


def write_conf_csv(path, M, labels, cols=None):
    cols = cols or labels
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["true\\pred"] + cols)
        for t in labels:
            w.writerow([t] + [M[t][c] for c in cols])


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_sidecar(name, pages, tokenization, meta):
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    obj = dict(name=name, tokenization=tokenization, s49=meta, pages=pages)
    (RUN_DIR / f"{name}.meta.json").write_text(json.dumps(obj), encoding="utf-8")


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    L.header(emit, "S49 (P4-D3, D-052): blind identifiability study - can the board tell cipher / code / generator / "
                   "language / gibberish apart on known texts at 38k tokens?" + (" [SMOKE RUN, not reported]" if SMOKE else ""), SELF, STUB)
    emit(f"date: {L.clock()}")
    emit(f"N_TOK {N_TOK}; quire block {QUIRE_BLOCK}; features {len(FEATS)} ({len(BOARD)} board + {len(EXTRA)} extras); B_feat {B_FEAT}; phase limit {PHASE_LIMIT} s")
    emit("deps: " + "; ".join(f"{m}={sha256(ROOT / m)[:16]}" for m in (
        "s10_cipher_mechanism.py", "s28_generator_mechanism.py", "s36_two_layer_operator_core.py", "p4d1_core_order.py",
        "k4_lossy_nomenclator.py", "ctl_schwartz.py", "ctl_generators.py", "c2_section_generator.py", "a2_position.py",
        "scoreboard/metrics_new.py")))
    emit()
    texts = OrderedDict()   # name -> dict(cls, pages, note, tok)

    def add(name, cls, pages, note, tokenization):
        pages = clean_pages(pages)
        texts[name] = dict(cls=cls, pages=pages, note=note)
        write_sidecar(name, pages, tokenization, dict(cls=cls, note=note))
        emit(f"  built {name:32s} class {cls:5s} tokens {ntok(pages):6d} types {ntypes(pages):6d} pages {len(pages):4d}  {note}  [{time.time() - t0:.0f}s]")
        flush()

    # ========================= PHASE 1: generation
    tg = time.time()
    emit("=== PHASE 1: corpus construction (mechanisms fixed in the docstring) ===")
    by_zl, n_ex, n_fb = L.load_T("ZL3b")
    n_zl = sum(len(r["words"]) for recs in by_zl.values() for r in recs)
    skel = extend_by(by_zl, N_TOK)
    emit(f"ZL3b: {len(by_zl)} pages {n_zl} tokens; skeleton {len(skel)} pages {sum(len(r['words']) for recs in skel.values() for r in recs)} tokens")
    # LANG
    lang_src = [("latin_cremma", load_realline("cremma_all")), ("italian_dante", load_realline("italian_dante")),
                ("mhg_nibelungenlied", load_realline("mhg_nibelungenlied")), ("occitan_croisade", load_realline("occitan_croisade")),
                ("oldfrench_roland", load_realline("oldfrench_roland")), ("mhg_parzival", parzival_pages())]
    plains = {}
    for nm, pg in lang_src:
        tp = assign_quires(truncate_pages(pg, N_TOK))
        short = ntok(tp) < N_TOK
        add(f"lang_{nm}", "LANG", tp, f"real lines, first {ntok(tp)} tokens" + (" SHORT (source has fewer than 38k tokens)" if short else ""), "native")
        plains[nm] = plain_words(tp)
    guard(tg, "generation")
    # shared ZL3b construction (s10 / s28)
    R_la = s31.build_latin_syllable_edge_table(by_zl)
    pools = s31.build_m5_edge_pools(by_zl)
    fmid = s10.midline_freq(by_zl)
    m2 = n6.fit_char_markov2(fmid)
    # CIPH
    for i, nm in enumerate(["latin_cremma", "italian_dante", "mhg_nibelungenlied", "occitan_croisade", "oldfrench_roland"], start=1):
        krng = random.Random(SEED + 100 * i)
        table = varied_table(by_zl, plains[nm], krng)
        p_null = krng.uniform(0.05, 0.20)
        nextp = cycler(plains[nm])
        enc = gen_cipher(skel, nextp, table, m2, pools, R_la, p_null, seed=i)
        hk = Counter(len(v) for v in table.values())
        add(f"ciph_s10_{nm}", "CIPH", L.pages_of(enc),
            f"s10 verbose homophonic, p_null {p_null:.3f}, {len(table)} letters, homophone counts {dict(sorted(hk.items()))}, "
            f"plaintext words consumed {nextp.used[0]} of {len(plains[nm])}{' (CYCLED)' if nextp.used[0] > len(plains[nm]) else ''}", "eva")
        guard(tg, "generation")
    # CODE
    Qi, Qe, para = k1.line_tables(by_zl)
    Rf3 = f3.ratio_table(by_zl)
    g_k4 = c2.Gen(by_zl)
    for i, nm in enumerate(["latin_cremma", "italian_dante", "mhg_nibelungenlied", "occitan_croisade", "oldfrench_roland", "mhg_parzival"], start=1):
        book, n_used, mean_col = k4.build_shared_codebook(plains[nm], g_k4.freq, pool_cap=7025, k_choices=6, rank_window=180, seed=SEED + i)
        nextp = cycler(plains[nm])
        enc = gen_code(skel, nextp, book, Rf3, Qi, Qe, para, beta=1.8, seed=i)
        add(f"code_k4_{nm}", "CODE", L.pages_of(enc),
            f"K4 shared-codeword nomenclator (7025/6/180/1.8), codebook seed {SEED + i}, {n_used} codewords used, mean owners {mean_col:.2f}, "
            f"plaintext words consumed {nextp.used[0]} of {len(plains[nm])}{' (CYCLED)' if nextp.used[0] > len(plains[nm]) else ''}", "eva")
        guard(tg, "generation")
    # GEN: s28
    g = c2.Gen(by_zl)
    forms, ntk, nb_links = s28.synth_glyph_forms_mid(g, by_zl, m2)
    g.nb.update(nb_links)

    def lex_fn(key, rng, lam):
        ws, wt = g.lexicon(rng)
        ex = forms[key][: round(lam * ntk[key])]
        return ws + ex, wt + [1] * len(ex)
    target = round(len({w for recs in by_zl.values() for r in recs for w in r["words"]}) * (N_TOK / n_zl) ** 0.68)
    lo, hi, tried = 0.0, s28.LAM_HI, []
    for _ in range(s28.LAM_STEPS):
        lam = (lo + hi) / 2
        by0 = s31.gen_s31_generator_m5_direct(g, skel, lambda k, r, _l=lam: lex_fn(k, r, _l), pools, R_la, {}, p_hab=0.0, seed=0)
        t = len({w for recs in by0.values() for r in recs for w in r["words"]})
        tried.append((abs(t - target), lam, t))
        lo, hi = (lam, hi) if t < target else (lo, lam)
    _, lam_cal, t_cal = min(tried)
    extra = [f for k in forms for f in forms[k][: round(lam_cal * ntk[k])]]
    htab = n4.habit_table_over(g.types + extra, g.tw + [1.0] * len(extra))
    gb = s31.gen_s31_generator_m5_direct(g, skel, lambda k, r: lex_fn(k, r, lam_cal), pools, R_la, htab, p_hab=s28.P_HAB, seed=1)
    add("gen_s28_ZL3b_s1", "GEN", L.pages_of(gb), f"s28 mechanism, lam {lam_cal:.4f} -> {t_cal} types at seed 0 (target {target})", "eva")
    guard(tg, "generation")
    # GEN: c2
    meta_c2 = json.loads((ROOT / "data" / "controls_synthetic" / "c2_best.meta.json").read_text(encoding="utf-8"))
    gc = c2.Gen(by_zl)
    gc.by = skel
    gc.page_ix = {p: i for i, p in enumerate(skel)}
    enc = gc.generate(**meta_c2["kwargs"])
    add("gen_c2_section", "GEN", L.pages_of(enc), f"c2.Gen.generate {meta_c2['kwargs']} on the skeleton", "eva")
    # GEN: Timm-Schinner own lines
    ts = json.loads((ROOT / "data" / "controls_synthetic" / "timm_schinner_ownlines.meta.json").read_text(encoding="utf-8"))["pages"]
    tp = assign_quires(truncate_pages(ts, N_TOK))
    add("gen_timm_schinner", "GEN", tp, "timm_schinner_ownlines (Java generator output, own lines), first 38k tokens", "eva")
    # GEN: Schwartz reuse, regenerated on the extended template with the stored betas
    meta_sw = json.loads((ROOT / "data" / "controls_synthetic" / "schwartz_reuse.meta.json").read_text(encoding="utf-8"))
    template = cc.voynich_pages()
    by_hand = {}
    for p in template:
        by_hand.setdefault(p["hand"], []).append(p)
    models = {h: csw.HandModel(h, ps) for h, ps in by_hand.items()}
    betas = {h: meta_sw["fit"][h]["beta"] for h in models}
    tpl_by = OrderedDict((p["id"], [dict(page=p["id"], words=ln, _p=p) for ln in p["lines"]]) for p in template)
    tpl_ext = extend_by(tpl_by, N_TOK)
    template_ext = [dict(recs[0]["_p"], id=pid, lines=[r["words"] for r in recs]) for pid, recs in tpl_ext.items()]
    sw = csw.generate(models, template_ext, meta_sw["seed"], betas)
    add("gen_schwartz_reuse", "GEN", sw, f"ctl_schwartz.generate, betas from schwartz_reuse.meta.json, seed {meta_sw['seed']}, extended template", "eva")
    # GEN: Rugg grille
    cg.N_TOKENS = N_TOK
    rng_r = random.Random(SEED + 10)
    w_r, _ = cg.rugg_grille(rng_r, corpora.voynich())
    rp = cg.layout(rng_r, w_r[:N_TOK])
    rp = assign_quires([dict(id=f"rg{p['page']:04d}", section=p["section"], hand="?", lang="?", lines=p["lines"]) for p in rp])
    add("gen_rugg_grille", "GEN", rp, "ctl_generators.rugg_grille + layout, Random(SEED+10), N_TOKENS 38000, own lines", "eva")
    guard(tg, "generation")
    # GIB
    gib = load_realline("gib_realline_pooled")
    for j in range(1, 7):
        rng_g = random.Random(SEED + 600 + j)
        pg, tot, k = [], 0, 0
        while tot < N_TOK:
            w = rng_g.choice(gib)
            pg.append(dict(w, id=f"{w['id']}~b{k}"))
            tot += sum(len(ln) for ln in w["lines"]); k += 1
        tp = assign_quires(truncate_pages(pg, N_TOK))
        cnt = Counter(p["id"].split("~")[0] for p in tp)
        add(f"gib_resample_{j}", "GIB", tp, f"gib_realline_pooled writer blocks with replacement: {len(tp)} blocks, {len(cnt)} of {len(gib)} writers, max repeats {max(cnt.values())}", "native")
    guard(tg, "generation")
    # two-layer producers (corpus pair + twin panel)
    twins = []
    models2 = {}
    for T in ("ZL3b", "RF1b", "IT2a"):
        by_T = by_zl if T == "ZL3b" else L.load_T(T)[0]
        tm, cal = two_layer_model(T, by_T)
        models2[T] = (tm, cal)
        emit(f"  two-layer model {T}: target types {tm.target_types} at {N_TOK} tokens; G lam {cal['G'][0]:.4f} -> {cal['G'][1]} types; L lam {cal['L'][0]:.4f} -> {cal['L'][1]} types")
        for TT, s in TWIN_SPECS:
            if TT != T:
                continue
            gbt = tm.generate_G(cal["G"][0], 0.04, seed=s, hab_tab=cal["G"][3])
            lbt = tm.generate_L(cal["L"][0], 0.04, seed=s, hab_tab=cal["L"][3])
            if (T, s) == ("ZL3b", 1):
                add("gen_G2layer_ZL3b_s1", "GEN", L.pages_of(gbt), "s36 G_2layer, ZL3b, seed 1 (corpus member; twin pair 1)", "eva")
                add("ciph_L2layer_ZL3b_s1", "CIPH", L.pages_of(lbt), "s36 L_2layer, ZL3b, seed 1 (corpus member; twin pair 1)", "eva")
                twins.append(("gen_G2layer_ZL3b_s1", "ciph_L2layer_ZL3b_s1"))
            else:
                gn, ln_ = f"twin_G2layer_{T}_s{s}", f"twin_L2layer_{T}_s{s}"
                add(gn, "TWIN_G", L.pages_of(gbt), f"s36 G_2layer, {T}, seed {s} (twin panel only)", "eva")
                add(ln_, "TWIN_L", L.pages_of(lbt), f"s36 L_2layer, {T}, seed {s} (twin panel only)", "eva")
                twins.append((gn, ln_))
            guard(tg, "generation")
    labels = {n: d["cls"] for n, d in texts.items()}
    lab_path = RUN_DIR / "labels.json"
    lab_path.write_text(json.dumps(dict(labels=labels, notes={n: d["note"] for n, d in texts.items()}, twins=twins), indent=1), encoding="utf-8")
    emit(f"labels: {lab_path} sha256={sha256(lab_path)} ({len(labels)} texts: " + ", ".join(f"{c} {sum(1 for v in labels.values() if v == c)}" for c in CLASSES + ['TWIN_G', 'TWIN_L']) + ")")
    emit(f"phase 1 elapsed {time.time() - tg:.0f}s")
    emit()
    flush()

    # ========================= PHASE 2: scoring
    ts_ = time.time()
    emit("=== PHASE 2: features (26 per text) ===")
    F, ERR = OrderedDict(), {}
    voy = OrderedDict()
    for T in ("ZL3b", "RF1b", "IT2a"):
        by_T = by_zl if T == "ZL3b" else L.load_T(T)[0]
        if SMOKE:
            by_T = extend_by(by_T, N_TOK)
        voy[f"Voynich_{T}"] = L.pages_of(by_T)
    for name, pages in list(((n, d["pages"]) for n, d in texts.items())) + list(voy.items()):
        t1 = time.time()
        F[name], ERR[name] = features(name, pages)
        emit(f"  {name:32s} " + " ".join(f"{k[:10]}={F[name][k]:+.4f}" for k in EXTRA) + f"  types_25k={F[name]['types_25k']:.0f}"
             + (f"  ERRORS {ERR[name]}" if ERR[name] else "") + f"  [{time.time() - t1:.0f}s]")
        flush()
        guard(ts_, "scoring")
    with (RUN_DIR / "features.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "class", "tokens"] + FEATS)
        for n, f in F.items():
            pg = texts[n]["pages"] if n in texts else voy[n]
            w.writerow([n, labels.get(n, "VOYNICH"), ntok(pg)] + [f"{f[k]:.6g}" for k in FEATS])
    emit(f"feature table: {RUN_DIR / 'features.csv'}")
    emit(f"checks (not gates): Voynich ZL3b A14 core excess {F['Voynich_ZL3b']['A14_core_excess']:+.4f} (s34 paragraph text -0.0315); "
         f"line-initial excess {F['Voynich_ZL3b']['line_init_excess']:+.4f} (s32/s44 +0.1740); A5 {F['Voynich_ZL3b']['A5_moran']:+.4f} (+0.1572); "
         f"A6 {F['Voynich_ZL3b']['A6_charwin']:+.4f} (+0.0940); A7 {F['Voynich_ZL3b']['A7_f1']:+.4f} (+0.0461)")
    emit()
    emit(f"{'class means (raw)':20s} " + " ".join(f"{c:>10s}" for c in CLASSES) + "   Voynich_ZL3b")
    for k in FEATS:
        emit(f"  {k[:18]:18s} " + " ".join(f"{np.nanmean([F[n][k] for n in texts if labels[n] == c]):+10.4f}" for c in CLASSES) + f"   {F['Voynich_ZL3b'][k]:+.4f}")
    emit()
    flush()

    # ========================= PHASE 3: classification
    emit("=== PHASE 3: classification (NC = nearest centroid gates; LDA declared second) ===")
    corpus = [n for n in texts if labels[n] in CLASSES]
    X = {n: np.array([F[n][k] for k in FEATS]) for n in F}
    # ---- T5
    pred_nc, pred_lda, margins5 = {}, {}, {}
    for n in corpus:
        tr = [m for m in corpus if m != n]
        Ztr, Zte = prep([X[m] for m in tr], X[n])
        ytr = [labels[m] for m in tr]
        cents = centroids(Ztr, ytr, CLASSES)
        d = dists(Zte[0], cents)
        srt = sorted(d.items(), key=lambda kv: kv[1])
        pred_nc[n] = srt[0][0]; margins5[n] = srt[1][1] - srt[0][1]
        pred_lda[n] = str(lda_fit(Ztr, ytr).predict(Zte)[0])
    for tag, pred in (("NC", pred_nc), ("LDA", pred_lda)):
        M = confusion([labels[n] for n in corpus], [pred[n] for n in corpus], CLASSES)
        k5 = sum(pred[n] == labels[n] for n in corpus)
        emit_conf(f"T5 five-class LOO, {tag}: {k5}/30 correct (reported, not gating: bar >= 15/30; binomial p vs 0.2 = {binom_p_ge(k5, 30, 0.2):.2g})", M, CLASSES)
        write_conf_csv(RUN_DIR / f"confusion_T5_{tag}.csv", M, CLASSES)
        emit("  per-class accuracy: " + ", ".join(f"{c} {M[c][c]}/6" for c in CLASSES))
    emit("  T5 per-text NC: " + "; ".join(f"{n}->{pred_nc[n]}" for n in corpus if pred_nc[n] != labels[n]) + " (misclassified only)")
    emit("  T5 per-text LDA: " + "; ".join(f"{n}->{pred_lda[n]}" for n in corpus if pred_lda[n] != labels[n]) + " (misclassified only)")
    emit()
    # ---- T2
    bin24 = [n for n in corpus if labels[n] in CIPHER_SIDE + GEN_SIDE]
    C4 = list(CIPHER_SIDE + GEN_SIDE)
    b_nc, b_lda, margins2 = {}, {}, {}
    for n in bin24:
        tr = [m for m in bin24 if m != n]
        Ztr, Zte = prep([X[m] for m in tr], X[n])
        cents = centroids(Ztr, [labels[m] for m in tr], C4)
        d = dists(Zte[0], cents)
        srt = sorted(d.items(), key=lambda kv: kv[1])
        b_nc[n] = side(srt[0][0]); margins2[n] = srt[1][1] - srt[0][1]
        b_lda[n] = str(lda_fit(Ztr, [side(labels[m]) for m in tr]).predict(Zte)[0])
    res_bin = {}
    for tag, pred in (("NC", b_nc), ("LDA", b_lda)):
        k = sum(pred[n] == side(labels[n]) for n in bin24)
        res_bin[tag] = k
        M = confusion([side(labels[n]) for n in bin24], [pred[n] for n in bin24], ["cipher", "generator"])
        emit_conf(f"T2 PRIMARY binary (CIPH+CODE) vs (GEN+GIB), 24 texts LOO, {tag}: {k}/24 correct; binomial p vs 0.5 = {binom_p_ge(k, 24):.2g}; "
                  f"Clopper-Pearson 95% lower {cp_lower(k, 24):.3f}", M, ["cipher", "generator"])
        write_conf_csv(RUN_DIR / f"confusion_T2_{tag}.csv", M, ["cipher", "generator"])
        emit("  by class: " + ", ".join(f"{c} {sum(1 for n in bin24 if labels[n] == c and pred[n] == side(c))}/6" for c in C4)
             + "; wrong: " + ("; ".join(f"{n}->{pred[n]}" for n in bin24 if pred[n] != side(labels[n])) or "none"))
    emit()
    # ---- TW
    base22 = [n for n in bin24 if n not in ("gen_G2layer_ZL3b_s1", "ciph_L2layer_ZL3b_s1")]

    def twin_scores(train, names):
        Ztr, Zte = prep([X[m] for m in train], [X[n] for n in names])
        cents = centroids(Ztr, [labels[m] for m in train], C4)
        nc = {}
        for n, z in zip(names, Zte):
            d = dists(z, cents)
            nc[n] = min(d[c] for c in GEN_SIDE) - min(d[c] for c in CIPHER_SIDE)
        lda = lda_fit(Ztr, [1 if labels[m] in CIPHER_SIDE else 0 for m in train])
        ld = dict(zip(names, lda.decision_function(Zte)))
        return nc, ld
    tw_res = {}
    for variant in ("primary", "beside"):
        ok_nc = ok_lda = 0
        rows = []
        for gname, lname in twins:
            if variant == "primary" or (gname, lname) == ("gen_G2layer_ZL3b_s1", "ciph_L2layer_ZL3b_s1"):
                train = base22
            else:
                train = bin24
            nc, ld = twin_scores(train, [gname, lname])
            c_nc = nc[lname] > nc[gname]; c_ld = ld[lname] > ld[gname]
            ok_nc += c_nc; ok_lda += c_ld
            rows.append(f"    {gname:24s} vs {lname:24s}  NC s(G)={nc[gname]:+.3f} s(L)={nc[lname]:+.3f} -> {'correct' if c_nc else 'WRONG'};  "
                        f"LDA s(G)={ld[gname]:+.3f} s(L)={ld[lname]:+.3f} -> {'correct' if c_ld else 'WRONG'}")
        tw_res[variant] = (ok_nc, ok_lda)
        emit(f"TW twin task ({variant}{': train = 22 non-two-layer texts of the 24' if variant == 'primary' else ': ZL3b s1 two-layer texts kept in training, reported not gating'}): "
             f"NC {ok_nc}/{len(twins)}, LDA {ok_lda}/{len(twins)}; sign-test p (>=k of {len(twins)}) NC {binom_p_ge(ok_nc, len(twins)):.3g}, LDA {binom_p_ge(ok_lda, len(twins)):.3g}")
        for r in rows:
            emit(r)
    emit()
    # ---- AUC
    emit("Per-feature univariate AUC, cipher side (CIPH+CODE) vs generator side (GEN+GIB), 24 texts (|AUC-0.5| sorted):")
    au = {k: auc([F[n][k] for n in bin24 if labels[n] in CIPHER_SIDE], [F[n][k] for n in bin24 if labels[n] in GEN_SIDE]) for k in FEATS}
    for k, v in sorted(au.items(), key=lambda kv: -abs(kv[1] - 0.5) if math.isfinite(kv[1]) else 0):
        emit(f"  {k:30s} AUC {v:.3f}")
    emit()
    flush()
    # ---- Voynich landing
    emit("=== Voynich landing (models fitted on all 30 / the 24; z on the training texts only) ===")
    Z30, ZV = prep([X[n] for n in corpus], [X[v] for v in voy])
    cents5 = centroids(Z30, [labels[n] for n in corpus], CLASSES)
    Z24, ZV24 = prep([X[n] for n in bin24], [X[v] for v in voy])
    cents4 = centroids(Z24, [labels[n] for n in bin24], C4)
    lda5 = lda_fit(Z30, [labels[n] for n in corpus])
    lda2 = lda_fit(Z24, [side(labels[n]) for n in bin24])
    med5 = float(np.median([margins5[n] for n in corpus if pred_nc[n] == labels[n]])) if any(pred_nc[n] == labels[n] for n in corpus) else float("nan")
    med2 = float(np.median([margins2[n] for n in bin24 if b_nc[n] == side(labels[n])])) if any(b_nc[n] == side(labels[n]) for n in bin24) else float("nan")
    emit(f"median LOO margin (2nd nearest - nearest) of correctly classified texts: T5 {med5:.3f}; T2 {med2:.3f}")
    rngb = np.random.default_rng(SEED)
    boot5 = {v: Counter() for v in voy}; boot2 = {v: Counter() for v in voy}
    Xc = np.array([X[n] for n in corpus]); Xb = np.array([X[n] for n in bin24]); Xv = np.array([X[v] for v in voy])
    y30 = [labels[n] for n in corpus]; y24 = [labels[n] for n in bin24]
    for _ in range(B_FEAT):
        cols = rngb.integers(0, len(FEATS), len(FEATS))
        a, b = prep(Xc[:, cols], Xv[:, cols]); ce = centroids(a, y30, CLASSES)
        a2_, b2 = prep(Xb[:, cols], Xv[:, cols]); ce4 = centroids(a2_, y24, C4)
        for i, v in enumerate(voy):
            d = dists(b[i], ce); boot5[v][min(d, key=d.get)] += 1
            d4 = dists(b2[i], ce4); boot2[v][side(min(d4, key=d4.get))] += 1
    bin_pass = res_bin["NC"] >= 20
    for i, v in enumerate(voy):
        d5 = dists(ZV[i], cents5); s5 = sorted(d5.items(), key=lambda kv: kv[1])
        d4 = dists(ZV24[i], cents4); s4 = sorted(d4.items(), key=lambda kv: kv[1])
        p5 = dict(zip(lda5.classes_, lda5.predict_proba(ZV[i:i + 1])[0]))
        p2 = dict(zip(lda2.classes_, lda2.predict_proba(ZV24[i:i + 1])[0]))
        m5 = s5[1][1] - s5[0][1]; m4 = s4[1][1] - s4[0][1]
        emit(f"{v}: T5 NC nearest {s5[0][0]} (margin {m5:.3f} vs median {med5:.3f}); distances " + ", ".join(f"{c} {d5[c]:.2f}" for c in CLASSES))
        emit(f"    T5 LDA posterior " + ", ".join(f"{c} {p5.get(c, 0):.3f}" for c in CLASSES)
             + f"; feature bootstrap (B={B_FEAT}) nearest class shares " + ", ".join(f"{c} {boot5[v][c] / B_FEAT:.3f}" for c in CLASSES))
        emit(f"    T2 NC nearest {s4[0][0]} -> {side(s4[0][0])} (margin {m4:.3f} vs median {med2:.3f}); distances " + ", ".join(f"{c} {d4[c]:.2f}" for c in C4)
             + f"; LDA posterior cipher {p2.get('cipher', 0):.3f} generator {p2.get('generator', 0):.3f}; bootstrap side shares cipher {boot2[v]['cipher'] / B_FEAT:.3f} generator {boot2[v]['generator'] / B_FEAT:.3f}")
        counts = bin_pass and m4 > med2
        emit(f"    assignment counts (Q2 rule: binary passes AND margin > median margin): {'YES' if counts else 'NO'}"
             f" (binary NC {'passes' if bin_pass else 'does not pass'}; margin {m4:.3f} {'>' if m4 > med2 else '<='} {med2:.3f})")
    emit()
    # ---- verdicts
    emit("=== VERDICTS (Q2 rules, frozen) ===")
    k, kl = res_bin["NC"], res_bin["LDA"]

    def bin_word(x):
        return ("PASS: board usable for Tier 2" if x >= 20 else
                "RED TEAM CONFIRMED: Tier-2 verdicts from this board are withdrawn, not just weakened" if x <= 16 else
                "NOT USABLE for Tier 2 (17-19/24: below the 20/24 bar, above the 16/24 withdrawal bar)")
    emit(f"PRIMARY binary NC {k}/24 -> {bin_word(k)}" + (" (NC only, not robust to the classifier)" if k >= 20 and kl < 20 else ""))
    emit(f"  LDA beside: {kl}/24 -> {bin_word(kl)}")
    tn, tl = tw_res["primary"]
    emit(f"TWIN NC {tn}/{len(twins)} -> " + ("PASS (>= 9/10)" if tn >= 9 else "FAIL: the 7/10-tie problem is structural, and only the non-tied features (A5/A6/A7) may be cited")
         + (" (NC only, not robust to the classifier)" if tn >= 9 and tl < 9 else "") + f"; LDA beside {tl}/{len(twins)}")
    k5 = sum(pred_nc[n] == labels[n] for n in corpus); k5l = sum(pred_lda[n] == labels[n] for n in corpus)
    emit(f"FIVE-CLASS NC {k5}/30 ({'>=' if k5 >= 15 else '<'} 15/30, reported not gating); LDA {k5l}/30")
    emit(f"VERDICT|s49|binary_nc={k}/24|binary_lda={kl}/24|twin_nc={tn}/{len(twins)}|twin_lda={tl}/{len(twins)}|five_nc={k5}/30|five_lda={k5l}/30")
    emit()
    emit(f"phase 2+3 elapsed {time.time() - ts_:.0f}s")
    emit(f"sidecars: {RUN_DIR} ({len(list(RUN_DIR.glob('*.meta.json')))} .meta.json); features.csv, confusion_*.csv, labels.json there")
    emit(f"elapsed {time.time() - t0:.0f}s; run ended {L.clock()}")
    flush()


if __name__ == "__main__":
    main()
