"""scoreboard.score: every metric of the a1/a2/a4b/a7/b1(T2)/b3(C3,C4)/b4/b5
battery computed from one Corpus (scoreboard/corpus.py), with the SAME
definitions, seeds and sample caps as the original scripts, so the filed
results_*.txt numbers reproduce (tests/test_score.py).

    from scoreboard.corpus import Corpus
    from scoreboard.score import score
    res = score(Corpus.from_voynich())            # ~1-2 min
    res = score(corpus, skip_nmf=True)            # without b5 NMF/NMI

Every metric lives in one function whose docstring names the original
script and results file it reproduces. Per-metric seeds are pinned to the
originals' values (a2 null seeds 0..n-1, a4/a4b seed 0, b3 Random(7), b5
default_rng(0) + NMF random_state=0); `seed` is used where the original
used SEED=20261017 (b1 T2) and is recorded in the output.

The frozen v1 board functions (PREREG v1, hash in PREREG.sha256) are kept
verbatim in scoreboard/score_v1.py and re-exported here so
g0_score_filed.py (score.score_corpus) keeps working.
"""
from __future__ import annotations

import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from a1_profile import char_entropies, zipf_slope          # noqa: E402
from a2_position import jsd, null as a2_null, stats as a2_stats  # noqa: E402
from a4_selfcite import nn as a4_nn                          # noqa: E402
from b1_docx_tests import lev_le1                            # noqa: E402
from b4_selfcite_sim import edit1                            # noqa: E402
from scoreboard.corpus import Corpus, UNKNOWN                # noqa: E402
from scoreboard.score_v1 import (                            # noqa: E402,F401
    N_PROFILE, SEED, TARGETS, edge_metrics, line_metrics, perseveration,
    profile_metrics, score_corpus)
from scoreboard.score_v1 import main as main_v1             # noqa: E402,F401

DEFAULT_N = 25000
DEFAULT_SEED = 20261017
GALLOWS = "ktpf"


def _r(x, nd=4):
    if x is None:
        return None
    x = float(x)
    return None if math.isnan(x) else round(x, nd)


# ---------------------------------------------------------------------------
# a1_profile.py  -> results_a1.txt
# ---------------------------------------------------------------------------
def profile(words, n_tokens=DEFAULT_N):
    """a1_profile.profile() on the first n_tokens tokens (results_a1.txt
    columns tokens, types, hapax, mean_len, sd_len, alpha, h1, h2, h3,
    zipf, redup, top10). h2 = H(char pair) - H(char) on " ".join(words)+" "
    (space is a symbol). sd_len is the population SD (np.std). redup is the
    immediate-repeat share of adjacent pairs, in percent; top10 the token
    share of the ten most frequent types, in percent."""
    words = words[:n_tokens]
    c = Counter(words)
    ce = char_entropies(words)
    lens = [len(w) for w in words]
    redup = sum(a == b for a, b in zip(words, words[1:])) / max(len(words) - 1, 1)
    top10 = sum(v for _, v in c.most_common(10)) / len(words)
    return dict(
        tokens=len(words), types=len(c),
        hapax=_r(sum(v == 1 for v in c.values()) / len(c)),
        mean_len=_r(np.mean(lens)), sd_len=_r(np.std(lens)),
        alpha=ce["alpha"], h1=_r(ce["h1"]), h2=_r(ce["h2"]), h3=_r(ce["h3"]),
        zipf=_r(zipf_slope(words)), redup_pct=_r(100 * redup),
        top10_pct=_r(100 * top10),
    )


def h2_underscore(words):
    """b3_slot_claims.h2(stream(words)) / b4_selfcite_sim.h2(words): the same
    conditional char entropy on "_".join(words) with no trailing separator.
    b3 C4 'orig' column (first 25k tokens); b4 'h2=' (all lines-2+ tokens)."""
    s = "_".join(words)
    c1 = Counter(s); c2 = Counter(zip(s, s[1:]))
    n1, n2 = sum(c1.values()), sum(c2.values())
    H1 = -sum(v / n1 * math.log2(v / n1) for v in c1.values())
    H12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    return H12 - H1


# ---------------------------------------------------------------------------
# a2_position.py / b4_selfcite_sim.py  -> results_a2.txt / results_b4.txt
# ---------------------------------------------------------------------------
def _enrich_table(lines, where, top=10, min_count=20):
    """Rate of each glyph at the line edge vs mid-line (a2_position main,
    'ratio vs mid-line'); b4.enrich() is the same ratio for one glyph."""
    edge, mid = Counter(), Counter()
    for ws in lines:
        if len(ws) < 3:
            continue
        edge[ws[0][0] if where == "first" else ws[-1][-1]] += 1
        for w in ws[1:-1]:
            mid[w[0] if where == "first" else w[-1]] += 1
    ne, nm = sum(edge.values()), max(sum(mid.values()), 1)

    def ratio(g):
        a = edge[g] / ne if ne else 0.0
        b = mid[g] / nm
        return a / b if b else float("inf")

    table = [dict(glyph=g, edge_rate=_r(v / ne, 3), mid_rate=_r(mid[g] / nm, 3),
                  ratio=_r(ratio(g), 2), edge_count=v)
             for g, v in edge.most_common(top)]
    cands = [g for g, v in edge.items() if v >= min_count and mid[g] > 0]
    best = max(cands, key=ratio) if cands else None
    return table, ratio, best


def position(lines, n_null=30, fixed_first="p", fixed_last="m"):
    """a2_position.report()/main() on a set of lines (lines with <3 words
    skipped, as a2.stats). For each feature (first glyph, last glyph,
    length=min(len,9)): JSD(first-word feature, mid-word feature) and
    JSD(last, mid), with the within-line word-shuffle null (seeds 0..n_null-1
    via random.Random(i), as a2.null) as mean/std over n_null draws and as
    the mean over the first 20 draws (b4.report uses n=20: identical draws).
    Enrichment: edge rate / mid rate for the fixed Voynich glyphs p (line
    initial) and m (line final) (a2 'x17.89'/'x16.31', b4 'p-init'/'m-final'),
    the top-10 table a2 prints, and the generalised 'most over-represented
    edge glyph' (max ratio among glyphs with >=20 edge occurrences)."""
    if not lines:
        return None
    out = {}
    feats = {"first_glyph": lambda w: w[0], "last_glyph": lambda w: w[-1],
             "length": lambda w: min(len(w), 9)}
    for fname, feat in feats.items():
        f, l = a2_stats(lines, feat)
        nl = a2_null(lines, feat, n=n_null)
        out[fname] = dict(
            jsd_first=_r(f), jsd_last=_r(l),
            null_first_mean=_r(nl[:, 0].mean()), null_first_std=_r(nl[:, 0].std()),
            null_last_mean=_r(nl[:, 1].mean()), null_last_std=_r(nl[:, 1].std()),
            null20_first_mean=_r(nl[:20, 0].mean()), null20_last_mean=_r(nl[:20, 1].mean()),
        )
    tf, rf, bf = _enrich_table(lines, "first")
    tl, rl, bl = _enrich_table(lines, "last")
    out["enrich"] = dict(
        fixed_first_glyph=fixed_first, fixed_first_ratio=_r(rf(fixed_first), 2),
        fixed_last_glyph=fixed_last, fixed_last_ratio=_r(rl(fixed_last), 2),
        max_first_glyph=bf, max_first_ratio=_r(rf(bf), 2) if bf else None,
        max_last_glyph=bl, max_last_ratio=_r(rl(bl), 2) if bl else None,
        first_table=tf, last_table=tl,
    )
    out["jsd_first_fg"] = out["first_glyph"]["jsd_first"]
    out["jsd_last_lg"] = out["last_glyph"]["jsd_last"]
    out["n_lines_ge3"] = sum(len(ws) >= 3 for ws in lines)
    return out


def samecol_rate(page_lines):
    """b4_selfcite_sim.samecol_rate: over consecutive line pairs of a page,
    share of tokens of the lower line whose same-index token on the line
    above is identical or one edit away (b4 'samecol_edit<=1')."""
    hit = n = 0
    for _, ls in page_lines:
        for a, b in zip(ls, ls[1:]):
            for j, w in enumerate(b):
                if j < len(a):
                    n += 1
                    hit += a[j] == w or edit1(a[j], w)
    return hit / n if n else float("nan")


def position_body(corpus: Corpus):
    """b4_selfcite_sim.report('VOYNICH') row of results_b4.txt: position()
    on lines 2+ of each page (page-first line excluded), null mean over 20
    draws, plus h2 (h2_underscore) over those tokens, immediate-repeat share
    (b4: pairs / tokens, percent), samecol_edit<=1 over all page lines, and
    the token count."""
    lines = corpus.body_lines()
    if not lines:
        return None
    pos = position(lines, n_null=30)
    words = [w for l in lines for w in l]
    rep = sum(a == b for a, b in zip(words, words[1:])) / len(words)
    return dict(
        jsd_first=pos["first_glyph"]["jsd_first"],
        null_first=pos["first_glyph"]["null20_first_mean"],
        jsd_last=pos["last_glyph"]["jsd_last"],
        null_last=pos["last_glyph"]["null20_last_mean"],
        p_init_ratio=pos["enrich"]["fixed_first_ratio"],
        m_final_ratio=pos["enrich"]["fixed_last_ratio"],
        max_first_glyph=pos["enrich"]["max_first_glyph"],
        max_first_ratio=pos["enrich"]["max_first_ratio"],
        max_last_glyph=pos["enrich"]["max_last_glyph"],
        max_last_ratio=pos["enrich"]["max_last_ratio"],
        h2=_r(h2_underscore(words)), repeat_pct=_r(100 * rep),
        samecol_edit_le1=_r(samecol_rate(corpus.page_lines()), 3),
        tokens=len(words),
    )


def page_first_gallows(corpus: Corpus, gallows=GALLOWS):
    """a2_position main, last block: share of page-first lines whose first
    glyph is a gallows (k,t,p,f) vs other lines, and p/f only. The original
    read vparse records with '?'-words kept; this runs on the Corpus
    ('?'-words dropped), see REPRODUCTION.md."""
    starts, other = Counter(), Counter()
    for _, ls in corpus.page_lines():
        for i, ws in enumerate(ls):
            if not ws:
                continue
            (starts if i == 0 else other)[ws[0][0]] += 1
    ns, no = sum(starts.values()), sum(other.values())
    if not ns or not no:
        return None
    return dict(
        gallows_pagefirst_pct=_r(100 * sum(starts[g] for g in gallows) / ns, 2),
        gallows_other_pct=_r(100 * sum(other[g] for g in gallows) / no, 2),
        pf_pagefirst_pct=_r(100 * (starts["p"] + starts["f"]) / ns, 2),
        pf_other_pct=_r(100 * (other["p"] + other["f"]) / no, 2),
        n_pagefirst=ns, n_other=no,
    )


# ---------------------------------------------------------------------------
# a4b_selfcite_matched.py / a4_selfcite.py  -> results_a4b.txt
# ---------------------------------------------------------------------------
def _ratios(loc, far):
    def q(a, b):
        return _r(a / b, 2) if b else None
    return dict(
        exact_loc=_r(loc[0], 3), exact_far=_r(far[0], 3), exact_ratio=q(loc[0], far[0]),
        d1_loc=_r(loc[1], 3), d1_far=_r(far[1], 3), d1_ratio=q(loc[1], far[1]),
        le1_loc=_r(loc[0] + loc[1], 3), le1_far=_r(far[0] + far[1], 3),
        le1_ratio=q(loc[0] + loc[1], far[0] + far[1]),
    )


def near_copy_matched(corpus: Corpus, W, seed=0, min_group=400, min_sep=1500):
    """a4b_selfcite_matched.run(W): for every second token whose (lang,
    section, hand) group has >=400 members, nearest Levenshtein distance
    (a4.nn, capped at 4) to the W preceding tokens ('local') vs to a W-window
    ending at a random same-group position >1500 tokens away ('far';
    random.Random(seed) draws 20 candidates, first admissible used).
    results_a4b.txt 'VMS matched W=10/40' rows: exact, d=1, d<=1 shares and
    local/far ratios. On a corpus without metadata all tokens form one
    group (unmatched, but still with the a4b sampling)."""
    toks = corpus.tokens_meta()
    rng = random.Random(seed)
    words = [t[0] for t in toks]
    groups = defaultdict(list)
    for i, t in enumerate(toks):
        if i >= W and toks[i - W][1] == t[1]:
            groups[t[1]].append(i)
    loc = np.zeros(5); far = np.zeros(5); n = 0
    for g, idx in groups.items():
        if len(idx) < min_group:
            continue
        for i in idx[::2]:
            cands = [j for j in (rng.choice(idx) for _ in range(20)) if abs(j - i) > min_sep]
            if not cands:
                continue
            j = cands[0]
            loc[a4_nn(words[i], words[i - W:i])] += 1
            far[a4_nn(words[i], words[j - W:j])] += 1
            n += 1
    if n == 0:
        return None
    out = _ratios(loc / loc.sum(), far / far.sum())
    out.update(W=W, n=n, groups=sum(len(v) >= min_group for v in groups.values()))
    return out


def near_copy_unmatched(words, W, N=12000, seed=0, min_sep=2000):
    """a4_selfcite.measure(words) with a4.W=W: first N=12000 tokens, local =
    W preceding tokens, far = W-window ending at a random position >=2000
    tokens away (random.Random(seed)). results_a4b.txt control rows
    ('latin_caesar W=10: exact 1.19 d=1 1.08 d<=1 1.12')."""
    rng = random.Random(seed)
    words = words[:N]
    if len(words) <= W + min_sep:
        return None
    loc = np.zeros(5); dist = np.zeros(5)
    for i in range(W, len(words)):
        w = words[i]
        loc[a4_nn(w, words[i - W:i])] += 1
        j = rng.randrange(W, len(words))
        while abs(j - i) < min_sep:
            j = rng.randrange(W, len(words))
        dist[a4_nn(w, words[j - W:j])] += 1
    out = _ratios(loc / loc.sum(), dist / dist.sum())
    out.update(W=W, n=int(loc.sum()))
    return out


# ---------------------------------------------------------------------------
# a7_abbrev.py  -> results_a7.txt
# ---------------------------------------------------------------------------
def abbreviation(words, n_tokens=DEFAULT_N):
    """a7_abbrev.run(): on the first 25k tokens, Spearman rho between type
    frequency and type length over types with freq>=3; mean length of the 50
    most frequent types; mean token length; their ratio (results_a7.txt)."""
    from scipy.stats import spearmanr
    ws = words[:n_tokens]
    c = Counter(ws)
    types = [w for w, v in c.items() if v >= 3]
    lens = [len(w) for w in types]
    if len(types) < 3 or len(set(lens)) < 2 or len({c[w] for w in types}) < 2:
        rho = float("nan")  # undefined (constant input); original would warn
    else:
        rho = spearmanr([c[w] for w in types], lens).correlation
    top = float(np.mean([len(w) for w, _ in c.most_common(50)]))
    allm = float(np.mean([len(w) for w in ws]))
    return dict(rho=_r(rho, 3), top50_len=_r(top, 2), token_mean_len=_r(allm, 2),
                ratio=_r(top / allm, 2), n_types_ge3=len(types))


# ---------------------------------------------------------------------------
# b1_docx_tests.py T2  -> results_b1.txt
# ---------------------------------------------------------------------------
def column_copy(corpus: Corpus, seed=DEFAULT_SEED):
    """b1_docx_tests.t2_same_column(): on lines with >=3 words grouped by
    page, for each token of line i (i>=1) at index j: hit if identical
    (exact) or Levenshtein<=1 (near) to the tokens at j-1..j+1 of line i-1
    (same-column), at j+4..j+6 of line i-1 (off-column), or at j-1..j+1 of
    line i-4 (far line; a random line of the corpus via random.Random(seed)
    when i<4). Percentages and the col/far, col/off edit<=1 ratios."""
    pages = []
    for _, ls in corpus.page_lines():
        ls = [ws for ws in ls if len(ws) >= 3]
        if ls:
            pages.append(ls)
    if not pages:
        return None
    rng = random.Random(seed)
    all_lines = [ws for ls in pages for ws in ls]
    st = Counter()

    def hit(w, cands):
        ex = any(w == c for c in cands)
        near = ex or any(lev_le1(w, c) for c in cands)
        return ex, near

    for ls in pages:
        for i in range(1, len(ls)):
            prev, cur = ls[i - 1], ls[i]
            far_line = ls[i - 4] if i >= 4 else rng.choice(all_lines)
            for j, w in enumerate(cur):
                near_c = [prev[k] for k in (j - 1, j, j + 1) if 0 <= k < len(prev)]
                off_c = [prev[k] for k in (j + 4, j + 5, j + 6) if 0 <= k < len(prev)]
                far_c = [far_line[k] for k in (j - 1, j, j + 1) if 0 <= k < len(far_line)]
                if not near_c:
                    continue
                st["n"] += 1
                e, n_ = hit(w, near_c); st["col_exact"] += e; st["col_near"] += n_
                if off_c:
                    st["n_off"] += 1
                    e, n_ = hit(w, off_c); st["off_exact"] += e; st["off_near"] += n_
                if far_c:
                    st["n_far"] += 1
                    e, n_ = hit(w, far_c); st["far_exact"] += e; st["far_near"] += n_

    def pct(a, b):
        return 100 * st[a] / max(st[b], 1)

    out = dict(
        n_col=st["n"], n_off=st["n_off"], n_far=st["n_far"],
        exact_col_pct=_r(pct("col_exact", "n"), 2),
        exact_off_pct=_r(pct("off_exact", "n_off"), 2),
        exact_far_pct=_r(pct("far_exact", "n_far"), 2),
        near_col_pct=_r(pct("col_near", "n"), 2),
        near_off_pct=_r(pct("off_near", "n_off"), 2),
        near_far_pct=_r(pct("far_near", "n_far"), 2),
    )
    if st["far_near"] and st["off_near"]:
        out["near_col_over_far"] = _r(pct("col_near", "n") / pct("far_near", "n_far"), 2)
        out["near_col_over_off"] = _r(pct("col_near", "n") / pct("off_near", "n_off"), 2)
    return out


# ---------------------------------------------------------------------------
# b3_slot_claims.py C3, C4  -> results_b3.txt
# ---------------------------------------------------------------------------
def final_restriction(words, n_tokens=DEFAULT_N, min_count=200, top=6):
    """b3 C3: on the first 25k tokens, for each glyph with >=200 occurrences
    the share of its occurrences that are word-final; number of glyphs with
    share >=0.9 and the top-6 (glyph, share) list."""
    W = words[:n_tokens]
    tot, fin = Counter(), Counter()
    for w in W:
        for i, ch in enumerate(w):
            tot[ch] += 1; fin[ch] += i == len(w) - 1
    rows = sorted(((fin[c] / tot[c], c) for c in tot if tot[c] >= min_count), reverse=True)
    return dict(n_ge90=sum(1 for r, _ in rows if r >= 0.9),
                top=[[c, _r(r, 2)] for r, c in rows[:top]])


def shuffle_h2(words, n_tokens=DEFAULT_N, seed=7):
    """b3 C4: h2 (h2_underscore) of the first 25k tokens, after a word-order
    shuffle, and after shuffling the characters inside each word
    (random.Random(seed) used for both, in that order; the original shared
    one Random(7) across all corpora in sequence, so only the first corpus
    (voynich_eva) is bit-exact; see REPRODUCTION.md). Returns the deltas."""
    W = words[:n_tokens]
    rng = random.Random(seed)
    o = h2_underscore(W)
    ws = W[:]; rng.shuffle(ws); s1 = h2_underscore(ws)
    cs = ["".join(rng.sample(w, len(w))) for w in W]; s2 = h2_underscore(cs)
    return dict(h2=_r(o, 3), word_shuffled=_r(s1, 3), d_word_shuffle=_r(s1 - o, 3),
                char_shuffled=_r(s2, 3), d_char_shuffle=_r(s2 - o, 3))


# ---------------------------------------------------------------------------
# b5_nmf_topics.py  -> results_b5.txt
# ---------------------------------------------------------------------------
def _nmi_with_nulls(cl, labels, rng, blocks, nperm):
    """b5_nmf_topics.score(): observed NMI; block-permutation null (labels
    reassigned among blocks, nperm draws from rng) mean and 99th pct;
    rotation null (block-label sequence rolled by every offset) mean, max
    and p = share of offsets with NMI >= observed."""
    from sklearn.metrics import normalized_mutual_info_score as nmi
    labels = np.asarray(labels); cl = np.asarray(cl)
    obs = nmi(labels, cl)
    ub = list(dict.fromkeys(blocks))
    blab = {b: Counter(l for l, bb in zip(labels, blocks) if bb == b).most_common(1)[0][0]
            for b in ub}
    vals = np.array([blab[b] for b in ub])
    perm = []
    for _ in range(nperm):
        m = dict(zip(ub, rng.permutation(vals)))
        perm.append(nmi([m[b] for b in blocks], cl))
    rot = []
    for off in range(1, len(ub)):
        m = dict(zip(ub, np.roll(vals, off)))
        rot.append(nmi([m[b] for b in blocks], cl))
    rot = np.array(rot) if rot else np.array([obs])
    return dict(nmi=_r(obs, 3), perm_mean=_r(np.mean(perm), 3),
                perm_p99=_r(np.percentile(perm, 99), 3),
                rot_mean=_r(rot.mean(), 3), rot_max=_r(rot.max(), 3),
                rot_p=_r(np.mean(rot >= obs), 3))


def nmf_topics(corpus: Corpus, k=8, chunk=40, nperm=200, seed=0,
               min_chunks_per_section=30, min_chunks=30):
    """b5_nmf_topics.voynich_block(): sequential 40-token chunks over the
    page-ordered stream (page boundaries ignored), each labelled by the
    majority page attribute; TF-IDF (min_df=2, sublinear) + NMF(k=8,
    nndsvda, random_state=0, max_iter=600), cluster = argmax topic; NMI of
    the clusters against section ('illus'), hand and lang with the b5 nulls
    (np.random.default_rng(seed) shared in that order, then within-hand).
    Within-hand: for each hand label (sorted), chunks of that hand in
    sections with >=30 chunks; if >=2 such sections and >=30 chunks, refit
    NMF with k = n_sections + 2 on those chunks only. For ZL3b this selects
    hand 1 {H,P} and hand 2 {B,H,T}, the sets b5 hard-coded. Label keys with
    fewer than two distinct values are skipped (None). results_b5.txt
    '[VOYNICH ZL3b]' block and the CTRL rows (via Corpus.from_control_sections)."""
    from b5_nmf_topics import topics
    toks = [(w, p) for p in corpus.pages for l in p["lines"] for w in l]
    ch = []
    for i in range(0, len(toks) - chunk + 1, chunk):
        part = toks[i:i + chunk]
        lab = lambda key: Counter(p.get(key, p["page_id"]) for _, p in part).most_common(1)[0][0]
        ch.append(dict(text=" ".join(w for w, _ in part), section=lab("section"),
                       hand=lab("hand"), lang=lab("lang"), block=lab("block")))
    if len(ch) < min_chunks:
        return None
    rng = np.random.default_rng(seed)
    cl = topics([c["text"] for c in ch], k=k, seed=seed)
    out = dict(chunks=len(ch), k=k, chunk=chunk, nperm=nperm)
    for key in ("section", "hand", "lang"):
        labs = [c[key] for c in ch]
        if len(set(labs)) < 2:
            out[key] = None
            continue
        out[key] = _nmi_with_nulls(cl, labs, rng, [c["block"] for c in ch], nperm)
    within = {}
    for hand in sorted({c["hand"] for c in ch} - {UNKNOWN}):
        sub_all = [c for c in ch if c["hand"] == hand]
        cnt = Counter(c["section"] for c in sub_all)
        secs = sorted(s for s, v in cnt.items() if v >= min_chunks_per_section and s != UNKNOWN)
        sub = [c for c in sub_all if c["section"] in secs]
        if len(secs) < 2 or len(sub) < min_chunks:
            continue
        cl2 = topics([c["text"] for c in sub], k=len(secs) + 2, seed=seed)
        r = _nmi_with_nulls(cl2, [c["section"] for c in sub], rng,
                            [c["block"] for c in sub], nperm)
        r.update(sections={s: cnt[s] for s in secs}, k=len(secs) + 2)
        within[hand] = r
    out["within_hand"] = within or None
    return out


# ---------------------------------------------------------------------------
# the one entry point
# ---------------------------------------------------------------------------
def score(corpus: Corpus, n_tokens=DEFAULT_N, seed=DEFAULT_SEED, skip_nmf=False,
          near_copy_windows=(10, 40), verbose=False):
    """Every metric on one Corpus. Returns a nested dict (see README table).
    n_tokens caps the a1/a7/b3 token-stream metrics (the originals' 25000);
    a4 unmatched keeps its own N=12000 cap. seed is used for b1 T2 and
    recorded; the other metrics keep their originals' pinned seeds."""
    import time
    t0 = time.time()
    words = corpus.words()
    res = dict(corpus=corpus.summary(),
               params=dict(n_tokens=n_tokens, seed=seed, skip_nmf=skip_nmf,
                           near_copy_windows=list(near_copy_windows)))

    def step(name, fn):
        t = time.time()
        res[name] = fn()
        if verbose:
            print(f"  {name:18} {time.time() - t:6.1f}s", flush=True)

    step("profile", lambda: profile(words, n_tokens))
    res["h2_all_tokens"] = _r(h2_underscore(words))
    if corpus.has_lines:
        step("position_all", lambda: position(corpus.lines()))
        step("position_body", lambda: position_body(corpus))
        step("page_first_gallows", lambda: page_first_gallows(corpus))
        step("column_copy", lambda: column_copy(corpus, seed))
    else:
        res.update(position_all=None, position_body=None,
                   page_first_gallows=None, column_copy=None)
    nc = {}
    for W in near_copy_windows:
        nc[f"matched_w{W}"] = near_copy_matched(corpus, W)
        nc[f"unmatched_w{W}"] = near_copy_unmatched(words, W)
    res["near_copy"] = nc
    if verbose:
        print(f"  {'near_copy':18} {time.time() - t0:6.1f}s cumulative", flush=True)
    step("abbreviation", lambda: abbreviation(words, n_tokens))
    step("final_restriction", lambda: final_restriction(words, n_tokens))
    step("shuffle_h2", lambda: shuffle_h2(words, n_tokens))
    if skip_nmf or not corpus.has_lines:
        res["nmf"] = None
    else:
        step("nmf", lambda: nmf_topics(corpus))
    res["runtime_s"] = round(time.time() - t0, 1)
    return res


def flatten(res, prefix="", out=None):
    """Dotted-key view of a score() result (lists/tables kept as values)."""
    out = {} if out is None else out
    for k, v in res.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict) and not k.endswith("_table") and k != "sections":
            flatten(v, key + ".", out)
        else:
            out[key] = v
    return out


__all__ = ["score", "flatten", "profile", "h2_underscore", "position",
           "position_body", "page_first_gallows", "samecol_rate",
           "near_copy_matched", "near_copy_unmatched", "abbreviation",
           "column_copy", "final_restriction", "shuffle_h2", "nmf_topics",
           "score_corpus", "profile_metrics", "line_metrics", "edge_metrics",
           "perseveration", "main_v1", "TARGETS", "N_PROFILE", "SEED"]
