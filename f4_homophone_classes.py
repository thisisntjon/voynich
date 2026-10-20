"""F4: homophone-class recovery (F3 flow cipher as positive control).

Question: do Voynich tokens fall into homophone classes, as they would if a
verbose homophonic cipher's scribe chose each homophone by flow from the
previous glyph (F3 mechanism)?

FROZEN PROCEDURE (fixed 2026-10-17 on the control only, before any Voynich run):
  types       every token type with count >= MINC=10 in the fitting text
  contexts    offsets -1 and +1 inside a line. Neighbours = the text's top
              NB=300 types (pass 0), then the current classes (ITERS=3
              refinement passes).
  edge factor each neighbour count is weighted by R(first|last)^-EDGE, EDGE=1.
              R is the text's OWN within-line edge ratio (f3.ratio_table
              formula), so this removes the flow choice's first|last effect.
  vector      per offset: (counts + ALPHA*marginal)/(row + ALPHA), ALPHA=1;
              sqrt (Hellinger); concatenate; centre; SVD to DIMS=60.
  clusterer   KMeans(K, n_init=4, random_state=seed).
  K rule      K = round(f * n_types) with f chosen from FRACS=(0.1, 0.2, 0.33,
              0.5) by the largest held-out class-over-token gain (fit on even
              pages, scored on odd pages). Truth-blind; the reverse direction
              (odd->even) is the honest held-out number.
  score       control only: type-level ARI / NMI against each type's majority
              unit (token-weighted ARI shown too but is dominated by frequent
              types sitting alone: an exchange clusterer scored 0.32 on both
              control and null that way).
Control iteration log (type ARI, control | shuffled-token null, MINC=5 K=130
unless noted): first SVD+KMeans no edge factor 0.038|0.011, edge factor 0.060|
0.009; Martin-Ney exchange clustering 0.014|0.000 (dropped); edge exponent
1.5/2 and agglomerative ward/average no better; MINC=10 K=65: 0.255|0.066,
MINC=20 K=25: 0.225|0.007. ALPHA 0.2/5, DIMS 30/120, NB 100/800, ITERS 0/8 tried,
none better overall.

Held-out class test (all texts): F1 Witten-Bell chain with TOPN=300, extended
by a class context: P(w | class(prev)) backed off to the edge model E2, and
P(w | prev token) backed off to that class model. Classes are fit on the
training pages only. Reported in bits on held-out pages, each minus the same
quantity for the same text with lines shuffled (F1 calibration):
  class gain  = (E2 - C) - shuffled      what the class of prev adds over edges
  token gain  = (E2 - W) - shuffled      F1 residual (token context)
  class-over-token = (W - CW) - shuffled  W = token ctx -> E2;
                                          CW = token ctx -> class ctx -> E2
Texts: CONTROL = f3.cipher_stream(beta=1.5, seed=2) on naibbe_chunks(), laid
on Voynich pages (c4.skeleton), true unit = chunk letters; CONTROL-NULL = same
tokens shuffled across the book (units attached); VOYNICH = b4.pages();
VOYNICH-NULL = Voynich tokens shuffled across the book; PROSE = latin_caesar
and italian_dante, 50-char lines, 20 lines per page, 33k tokens.
Run: python f4_homophone_classes.py  -> results_f4.txt
"""
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

import b4_selfcite_sim as b4
import c4_naibbe_lines as c4
import corpora
import f1_residual_order as f1
import f2_syllable_control as f2
import f3_flow_choice as f3

HERE = Path(__file__).parent
OUT = HERE / "results_f4.txt"
CACHE = HERE / "f4_control_cache.json"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


# ---------------------------------------------------------------- texts
def control_pages():
    """(by, units_by): F3 flow cipher beta=1.5 seed=2 on Voynich page skeleton."""
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    by = b4.pages()
    R = f3.ratio_table(by)
    seq, tab = f3.naibbe_chunks()
    toks = f3.cipher_stream(seq, tab, R, 1.5, seed=2)
    pairs = list(zip(toks, ["".join(l) for l, _ in seq]))
    sk = c4.skeleton(pairs, by)
    cb = {p: [dict(r, words=[w for w, _ in r["words"]], units=[u for _, u in r["words"]]) for r in recs]
          for p, recs in sk.items()}
    CACHE.write_text(json.dumps(cb), encoding="utf-8")
    return cb


def shuffled_book(by, seed=5):
    """Tokens (and their units, if any) shuffled across the whole book; line lengths kept."""
    items = [(w, (r.get("units") or [None] * len(r["words"]))[i])
             for recs in by.values() for r in recs for i, w in enumerate(r["words"])]
    random.Random(seed).shuffle(items)
    it = iter(items)
    out = {}
    for p, recs in by.items():
        new = []
        for r in recs:
            got = [next(it) for _ in r["words"]]
            d = dict(r, words=[w for w, _ in got])
            if "units" in r:
                d["units"] = [u for _, u in got]
            new.append(d)
        out[p] = new
    return out


def prose_pages(name, n=33000, per_page=20):
    lines = f2.wrap(corpora.control(name, 3 * n)[:n])
    out = {}
    for i in range(0, len(lines), per_page):
        out[f"p{i // per_page:03d}"] = [{"words": l, "quire": f"q{i // (per_page * 8)}"} for l in lines[i:i + per_page]]
    return out


def lines_of(by):
    return [r["words"] for recs in by.values() for r in recs]


# ---------------------------------------------------------------- clustering
P = dict(MINC=10, NB=300, ALPHA=1.0, DIMS=60, ITERS=3, EDGE=1.0, OFFS=(-1, 1), ALGO="kmeans", LINK="ward")


def edge_ratio(lines):
    pairs = [(a[-1], b[0]) for l in lines for a, b in zip(l, l[1:])]
    pj = Counter(pairs); pl = Counter(a for a, _ in pairs); pf = Counter(b for _, b in pairs); n = len(pairs)
    return lambda last, first: (pj.get((last, first), 0) + 0.5) / (pl.get(last, 0) + 0.5) / ((pf.get(first, 0) + 0.5) / n)


def features(lines, types, nbmap, nnb, p):
    """Context matrix: per offset, edge-corrected neighbour counts -> smoothed
    row distributions -> sqrt (Hellinger). nbmap: neighbour token -> column."""
    R = edge_ratio(lines) if p["EDGE"] else None
    ti = {t: i for i, t in enumerate(types)}
    blocks = []
    for off in p["OFFS"]:
        M = np.zeros((len(types), nnb))
        for l in lines:
            for i, w in enumerate(l):
                j = i + off
                if w not in ti or not 0 <= j < len(l):
                    continue
                n = l[j]
                c = nbmap(n)
                if c is None:
                    continue
                wt = 1.0
                if R and off == 1:
                    wt = R(w[-1], n[0]) ** -p["EDGE"]
                elif R and off == -1:
                    wt = R(n[-1], w[0]) ** -p["EDGE"]
                M[ti[w], c] += wt
        marg = M.sum(0) + 1e-9
        marg /= marg.sum()
        M = (M + p["ALPHA"] * marg) / (M.sum(1, keepdims=True) + p["ALPHA"])
        blocks.append(np.sqrt(M))
    X = np.hstack(blocks)
    X -= X.mean(0)
    U, S, _ = np.linalg.svd(X, full_matrices=False)
    d = min(p["DIMS"], X.shape[1] - 1, X.shape[0] - 1)
    return U[:, :d] * S[:d]


def fit(X, k, seed, p):
    if p["ALGO"] == "kmeans":
        return KMeans(k, n_init=4, random_state=seed).fit_predict(X)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12) if p["LINK"] != "ward" else X
    if seed:  # agglomerative is deterministic: seed = bootstrap-free jitter of row order only
        perm = np.random.default_rng(seed).permutation(len(X))
        lab = np.empty(len(X), int)
        lab[perm] = AgglomerativeClustering(k, linkage=p["LINK"], metric="euclidean").fit_predict(Xn[perm])
        return lab
    return AgglomerativeClustering(k, linkage=p["LINK"], metric="euclidean").fit_predict(Xn)


def cluster(lines, k, seed=0, p=P):
    """Returns {type: class} for types with count >= MINC."""
    cnt = Counter(w for l in lines for w in l)
    types = sorted(t for t, c in cnt.items() if c >= p["MINC"])
    top = [t for t, _ in cnt.most_common(p["NB"])]
    tix = {t: i for i, t in enumerate(top)}
    X = features(lines, types, lambda n: tix.get(n), len(top), p)
    lab = fit(X, k, seed, p)
    for _ in range(p["ITERS"]):
        a = dict(zip(types, lab))
        X = features(lines, types, lambda n: a.get(n), k, p)
        lab = fit(X, k, seed, p)
    return dict(zip(types, lab))


def score_truth(by, assign):
    """Type-level ARI / NMI of classes against each type's majority unit
    (homophone recovery = merging distinct types of one unit), plus the
    token-weighted ARI (dominated by the frequent types)."""
    tu = defaultdict(Counter)
    for recs in by.values():
        for r in recs:
            for w, u in zip(r["words"], r["units"]):
                tu[w][u] += 1
    types = sorted(t for t in assign if t in tu)
    y = [tu[t].most_common(1)[0][0] for t in types]
    z = [assign[t] for t in types]
    yt = [u for t in types for u, c in tu[t].items() for _ in range(c)]
    zt = [assign[t] for t in types for u, c in tu[t].items() for _ in range(c)]
    return adjusted_rand_score(y, z), normalized_mutual_info_score(y, z), adjusted_rand_score(yt, zt)


def pair_stability(a, b):
    common = sorted(set(a) & set(b))
    return adjusted_rand_score([a[t] for t in common], [b[t] for t in common]), len(common)


def spelling_baseline(by, k):
    """Truth-blind spelling clustering (first two + last two glyphs) as a reference."""
    cnt = Counter(w for l in lines_of(by) for w in l)
    types = sorted(t for t, c in cnt.items() if c >= P["MINC"])
    keys = sorted({(t[:2], t[-2:]) for t in types})
    ki = {k_: i for i, k_ in enumerate(keys)}
    return {t: ki[(t[:2], t[-2:])] for t in types}


# ---------------------------------------------------------------- held-out class model
class ClassModels(f1.Models):
    def __init__(self, train_lines, f, assign):
        super().__init__(train_lines, f)
        self.a = assign
        self.c = defaultdict(Counter)
        for x, y in f1.pairs_of(train_lines):
            if x in assign:
                self.c[assign[x]][f(y)] += 1

    def pc(self, prev, w, a, k):
        cl = self.a.get(prev)
        back = self.pe2(prev, w, a)
        return self.wb(self.c.get(cl), w, k, back) if cl is not None else back

    def pcw(self, prev, w, a, kc, kw):
        return self.wb(self.w.get(self.f(prev)), w, kw, self.pc(prev, w, a, kc))


def class_eval(train, test, assign):
    f1.TOPN = 300
    f = f1.mapper(train, 300)
    m = ClassModels(train, f, assign)
    tp = [(a, f(b)) for a, b in f1.pairs_of(test)]
    bits = f1.bits
    a = min(f1.GRID_A, key=lambda x: bits(tp, lambda p, w: m.pe2(p, w, x)))
    E2 = bits(tp, lambda p, w: m.pe2(p, w, a))
    W = min(bits(tp, lambda p, w: m.pw(p, w, a, k)) for k in f1.GRID_K)
    C = min(bits(tp, lambda p, w: m.pc(p, w, a, k)) for k in f1.GRID_K)
    CW = min(bits(tp, lambda p, w: m.pcw(p, w, a, kc, kw)) for kc in f1.GRID_K for kw in f1.GRID_K)
    return E2, W, C, CW


FRACS = (0.1, 0.2, 0.33, 0.5)
SEEDS = (0, 1, 2)


def n_types(lines):
    return sum(1 for c in Counter(w for l in lines for w in l).values() if c >= P["MINC"])


def k_for(lines, fr):
    return max(2, round(fr * n_types(lines)))


def page_halves(by):
    ps = list(by)
    return {q: by[q] for q in ps[::2]}, {q: by[q] for q in ps[1::2]}


def heldout(train_by, test_by, fr, seed=0):
    """Fit classes on train pages, score on test pages; shuffle-calibrated as F1."""
    tr, te = lines_of(train_by), lines_of(test_by)
    out = {}
    for tag, (a_tr, a_te) in (("real", (tr, te)), ("shuf", (f1.shuffled(tr), f1.shuffled(te)))):
        assign = cluster(a_tr, k_for(a_tr, fr), seed)
        out[tag] = class_eval(a_tr, a_te, assign)
    (E2, W, C, CW), (sE2, sW, sC, sCW) = out["real"], out["shuf"]
    return dict(cls=(E2 - C) - (sE2 - sC), tok=(E2 - W) - (sE2 - sW), cot=(W - CW) - (sW - sCW))


def analyse(name, by, show=False):
    L = lines_of(by)
    A, B = page_halves(by)
    sel = {fr: heldout(A, B, fr) for fr in FRACS}
    fr = max(FRACS, key=lambda x: sel[x]["cot"])
    rev = heldout(B, A, fr)
    K = k_for(L, fr)
    runs = [cluster(L, K, s) for s in SEEDS]
    seed_st = np.mean([pair_stability(runs[i], runs[j])[0] for i in range(3) for j in range(i + 1, 3)])
    sa, sb = cluster(lines_of(A), k_for(lines_of(A), fr), 0), cluster(lines_of(B), k_for(lines_of(B), fr), 0)
    split_st, ncommon = pair_stability(sa, sb)
    emit(f"{name}")
    emit(f"  tokens={sum(map(len, L))}  types>={P['MINC']}: {n_types(L)}  K-rule picks f={fr} -> K={K}")
    emit("  selection (even->odd) class-over-token by f: " + "  ".join(f"{x}: {sel[x]['cot']:+.4f}" for x in FRACS))
    emit(f"  held-out even->odd: class gain {sel[fr]['cls']:+.4f}  token gain {sel[fr]['tok']:+.4f}  class-over-token {sel[fr]['cot']:+.4f}")
    emit(f"  held-out odd->even: class gain {rev['cls']:+.4f}  token gain {rev['tok']:+.4f}  class-over-token {rev['cot']:+.4f}  (honest)")
    emit(f"  stability: seed ARI (mean of 3 pairs) {seed_st:.3f}   page-split ARI {split_st:.3f} on {ncommon} common types")
    res = dict(name=name, f=fr, K=K, sel=sel[fr], rev=rev, seed=seed_st, split=split_st)
    if any("units" in r for recs in by.values() for r in recs):
        tr = [score_truth(by, a) for a in runs]
        emit("  truth: type ARI " + " / ".join(f"{t[0]:.3f}" for t in tr) + "   type NMI " +
             " / ".join(f"{t[1]:.3f}" for t in tr) + "   token ARI " + " / ".join(f"{t[2]:.3f}" for t in tr) + "  (seeds 0/1/2)")
        res["truth"] = tr
    if show:
        cnt = Counter(w for l in L for w in l)
        groups = defaultdict(list)
        for t, c in runs[0].items():
            groups[c].append(t)
        big = sorted(groups.values(), key=lambda g: -sum(cnt[t] for t in g))
        emit("  largest classes (seed 0, by tokens):")
        for g in big[:12]:
            emit("    " + " ".join(sorted(g, key=lambda t: -cnt[t])[:10]) + (" ..." if len(g) > 10 else "") + f"   [{len(g)} types]")
    emit()
    return res, runs[0]


def control_beta0():
    """Plain Naibbe (beta=0) through the same skeleton: classes without the flow effect."""
    by = b4.pages()
    seq, tab = f3.naibbe_chunks()
    toks = f3.cipher_stream(seq, tab, f3.ratio_table(by), 0, seed=2)
    sk = c4.skeleton(list(zip(toks, ["".join(l) for l, _ in seq])), by)
    return {p: [dict(r, words=[w for w, _ in r["words"]], units=[u for _, u in r["words"]]) for r in recs]
            for p, recs in sk.items()}


def main():
    emit("F4: homophone-class recovery. Procedure frozen in the script docstring before the Voynich rows were run.")
    emit("held-out numbers are bits per token on held-out pages, minus the same text line-shuffled (F1 calibration)")
    emit()
    cb = control_pages()
    texts = [("CONTROL  F3 flow cipher beta=1.5 (truth known)", cb, False),
             ("CONTROL-NULL  same tokens shuffled across book", shuffled_book(cb), False),
             ("CONTROL beta=0  plain Naibbe re-encryption", control_beta0(), False),
             ("VOYNICH  b4.pages() paragraph text", b4.pages(), True),
             ("VOYNICH-NULL  tokens shuffled across book", shuffled_book(b4.pages()), False),
             ("PROSE latin_caesar", prose_pages("latin_caesar"), True),
             ("PROSE italian_dante", prose_pages("italian_dante"), False)]
    rows, keep = [], {}
    for name, by, show in texts:
        r, a = analyse(name, by, show)
        rows.append(r); keep[name.split()[0]] = (by, a)
    emit("SUMMARY  (f, K, held-out odd->even class gain / token gain / class-over-token, seed ARI, split ARI, truth type ARI)")
    for r in rows:
        t = f"  truth tARI {np.mean([x[0] for x in r['truth']]):.3f}" if "truth" in r else ""
        emit(f"  {r['name'][:46]:46} f={r['f']:<4} K={r['K']:<4} cls {r['rev']['cls']:+.4f}  tok {r['rev']['tok']:+.4f}  "
             f"cot {r['rev']['cot']:+.4f}  seed {r['seed']:.3f}  split {r['split']:.3f}{t}")
    emit()
    emit("SEED SPREAD of the honest held-out class-over-token (odd->even, each text's chosen f, KMeans seeds 0/1/2)")
    for r, (name, by, _) in zip(rows, texts):
        A, B = page_halves(by)
        v = [r["rev"]["cot"]] + [heldout(B, A, r["f"], seed=s)["cot"] for s in (1, 2)]
        emit(f"  {name[:46]:46} " + " / ".join(f"{x:+.4f}" for x in v) + f"   mean {np.mean(v):+.4f}")
    emit()
    emit("Step 4 (a6 solver on class sequences) is conditional on stable Voynich classes; see F_RESULTS.md F4.")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    return rows, keep


if __name__ == "__main__":
    main()
