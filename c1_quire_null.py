"""C1: is B5's within-scribe section signal just writing-order drift?

B5 found NMI(NMF cluster, section) = 0.275 (hand 1: Herbal vs Pharma) and
0.333 (hand 2: Biological / Herbal-B / Astro), beating a page-permutation null
and (hand 2 only narrowly, p=0.048) a rotation null. Sections are bound in
their own quires, so any drift in vocabulary between quires (time of writing,
batch of exemplar, mood of the scribe) would also produce that NMI.

Tests (same chunks, NMF clusters and section labels as B5):
  A quire-block null: the unit of permutation is a quire-section block (a
    contiguous run of one section inside one quire). Section labels are
    reassigned among blocks in every distinct way (exact enumeration), so the
    null keeps whatever is quire-local. p = share of assignments >= observed.
  B within-quire contrast: quires that hold two sections in one hand
    (hand 1 quire O: Herbal + Pharma; hand 2 quire M: Biological + Astro).
    NMI(cluster, section) restricted to that quire, page-permutation null.
  C cluster-free check: cosine distance between block TF-IDF centroids;
    statistic = mean distance between different-section blocks minus mean
    between same-section blocks; exact block-label enumeration null.
Controls:
  natural language: Augustine Confessiones, "sections" = books I-IX
    (autobiography) vs X-XIII (memory, time, Genesis exegesis); "quires" =
    consecutive 1,200-word blocks.
  nulls: token-shuffled Voynich (no structure); c2 drift generator (vocabulary
    drifts with page order, ignores section) - must NOT pass test A if the test
    controls drift; c2 section generator (vocabulary keyed to section) - should.
Run: python c1_quire_null.py  -> results_c1.txt
"""
from math import comb as math_comb
import random
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import normalized_mutual_info_score as nmi

import b4_selfcite_sim as b4
import b5_nmf_topics as b5
import c2_section_generator as c2

OUT = Path(__file__).parent / "results_c1.txt"
log = []
MAXPERM = 5000


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def assignments(labels, rng):
    """All distinct reassignments of a label multiset; Monte Carlo if > MAXPERM."""
    cnt = Counter(labels)
    n_distinct = 1
    rem = len(labels)
    for v in cnt.values():
        n_distinct *= math_comb(rem, v); rem -= v
    if n_distinct > MAXPERM:
        return [tuple(rng.permutation(labels)) for _ in range(MAXPERM)]
    out = []

    def rec(prefix, left):
        if len(prefix) == len(labels):
            out.append(tuple(prefix)); return
        for k in sorted(left):
            if left[k]:
                left[k] -= 1; rec(prefix + [k], left); left[k] += 1
    rec([], dict(cnt))
    return out


def block_test(units, cl, rng):
    """units: list of dicts with 'sec', 'blk'. Returns observed NMI, null mean, p, n blocks, n assignments,
    plus the centroid-distance statistic and its p."""
    blks = list(dict.fromkeys(u["blk"] for u in units))
    lab = [Counter(u["sec"] for u in units if u["blk"] == b).most_common(1)[0][0] for b in blks]
    secs = [u["sec"] for u in units]
    obs = nmi(secs, cl)
    alls = assignments(lab, rng)
    ix = [blks.index(u["blk"]) for u in units]
    vals = np.array([nmi([a[i] for i in ix], cl) for a in alls])
    # centroid distances
    X = TfidfVectorizer(min_df=2, token_pattern=r"\S+", sublinear_tf=True).fit_transform([u["text"] for u in units])
    C = np.vstack([np.asarray(X[[i for i, u in enumerate(units) if u["blk"] == b]].mean(0)) for b in blks])
    C /= np.linalg.norm(C, axis=1, keepdims=True)
    D = 1 - C @ C.T
    iu = np.triu_indices(len(blks), 1)

    def dstat(a):
        same = np.array([a[i] == a[j] for i, j in zip(*iu)])
        d = D[iu]
        return d[~same].mean() - d[same].mean() if same.any() and (~same).any() else np.nan

    dobs = dstat(lab)
    dnull = np.array([dstat(a) for a in alls])
    return dict(obs=obs, null=vals.mean(), p=float(np.mean(vals >= obs - 1e-12)), nb=len(blks), na=len(alls),
                lab="".join(l[0] for l in lab), dobs=dobs, dp=float(np.nanmean(dnull >= dobs - 1e-12)))


def page_perm(units, cl, rng, n=2000):
    pages = list(dict.fromkeys(u["page"] for u in units))
    lab = {p: Counter(u["sec"] for u in units if u["page"] == p).most_common(1)[0][0] for p in pages}
    obs = nmi([u["sec"] for u in units], cl)
    vals = []
    for _ in range(n):
        m = dict(zip(pages, rng.permutation([lab[p] for p in pages])))
        vals.append(nmi([m[u["page"]] for u in units], cl))
    vals = np.array(vals)
    return obs, vals.mean(), float(np.mean(vals >= obs - 1e-12)), len(pages)


def chunks(by):
    """B5 chunks, also labelled with quire and page."""
    toks = [(w, r) for recs in by.values() for r in recs for w in r["words"]]
    out = []
    for i in range(0, len(toks) - b5.CHUNK + 1, b5.CHUNK):
        part = toks[i:i + b5.CHUNK]
        lab = lambda key: Counter(r[key] for _, r in part).most_common(1)[0][0]
        out.append(dict(text=" ".join(w for w, _ in part), sec=lab("illus"), hand=lab("hand"),
                        quire=lab("quire"), page=lab("page")))
    return out


def voynich_like(name, by, rng):
    emit(f"[{name}]")
    ch = chunks(by)
    for hand, secs in c2.WITHIN:
        sub = [dict(c, blk=c["quire"] + c["sec"]) for c in ch if c["hand"] == hand and c["sec"] in secs]
        cl = b5.topics([c["text"] for c in sub], k=len(secs) + 2)
        r = block_test(sub, cl, rng)
        emit(f"  hand {hand} A quire-block null: NMI={r['obs']:.3f}  null mean {r['null']:.3f}  p={r['p']:.3f}"
             f"  ({r['nb']} blocks {r['lab']}, {r['na']} assignments)")
        emit(f"  hand {hand} C centroid dist diff-minus-same section = {r['dobs']:+.4f}  p={r['dp']:.3f}")
        cl = np.asarray(cl)
        for q in sorted({c["quire"] for c in sub}):
            inq = [i for i, c in enumerate(sub) if c["quire"] == q]
            sc = Counter(sub[i]["sec"] for i in inq)
            if len(sc) < 2 or min(sc.values()) < 3:
                continue
            o, m, p, npg = page_perm([sub[i] for i in inq], cl[inq], rng)
            emit(f"  hand {hand} B within quire {q} {dict(sc)}: NMI={o:.3f}  page-perm null {m:.3f}  p={p:.3f}  ({npg} pages)")


def augustine(rng):
    cc = b5.control_chunks("latin_augustine", r"^LIBER ([A-Z ]+?)\.?$")
    # the Gutenberg file has a table of contents (short label runs) before the
    # text and ~875 chunks of notes/index after it, all labelled; keep the main
    # run: first long 'primus' run through the end of the next 'decimus tertius' run
    start = next(i for i in range(len(cc)) if all(c["label"] == "primus" for c in cc[i:i + 50]))
    end = start + 1
    while end < len(cc) and not (cc[end]["label"] == "primus" and cc[end - 1]["label"] == "decimus tertius"):
        end += 1
    cc = cc[start:end]
    late = {"decimus", "undecimus", "duodecimus", "decimus tertius"}
    units = []
    for i, c in enumerate(cc):
        sec = "X-XIII" if c["label"] in late else "I-IX"
        units.append(dict(text=c["text"], sec=sec, blk=f"{i // 30:03d}", page=f"{i // 5:04d}"))
    # keep the 'quire' unit section-pure: split a quire where the section changes
    units = [dict(u, blk=u["blk"] + u["sec"]) for u in units]
    # balance: 1,200-word quires give ~114 blocks; subsample nothing, use MC null
    cl = b5.topics([u["text"] for u in units], k=4)
    r = block_test(units, cl, rng)
    emit(f"[CTRL latin_augustine main text ({len(cc)} chunks), books I-IX vs X-XIII, quire = 30 chunks]")
    emit(f"  A quire-block null: NMI={r['obs']:.3f}  null mean {r['null']:.3f}  p={r['p']:.4f}  ({r['nb']} blocks, {r['na']} MC assignments)")
    emit(f"  C centroid dist diff-minus-same = {r['dobs']:+.4f}  p={r['dp']:.4f}")
    # matched power: only as many quire blocks as Voynich hand 1 (11), contiguous run around the boundary
    blks = list(dict.fromkeys(u["blk"] for u in units))
    b0 = next(i for i, b in enumerate(blks) if b.endswith("X-XIII"))
    keep = set(blks[b0 - 9:b0 + 2])
    sub = [u for u in units if u["blk"] in keep]
    cl = b5.topics([u["text"] for u in sub], k=4)
    r = block_test(sub, cl, rng)
    emit(f"  matched to hand 1 size (blocks {r['lab']}): A NMI={r['obs']:.3f} null {r['null']:.3f} p={r['p']:.3f} ({r['na']} assignments);"
         f"  C {r['dobs']:+.4f} p={r['dp']:.3f}")


def main():
    rng = np.random.default_rng(0)
    emit("C1: quire-aligned null for the B5 within-scribe section signal")
    emit("A = section labels permuted among quire-section blocks (exact); B = within one quire, page-permutation null;")
    emit("C = TF-IDF centroid cosine distance, different-section minus same-section block pairs, same exact null")
    emit("p-values in A/C cannot go below 1/(number of distinct assignments)")
    emit()
    by = b4.pages()
    voynich_like("VOYNICH ZL3b", by, rng)
    flat = [w for recs in by.values() for r in recs for w in r["words"]]
    random.Random(5).shuffle(flat)
    it = iter(flat)
    voynich_like("NULL token-shuffled", {p: [dict(r, words=[next(it) for _ in r["words"]]) for r in recs]
                                         for p, recs in by.items()}, rng)
    g = c2.Gen(by)
    voynich_like("NULL drift generator (c2 drift ps=0.6)", g.generate("drift", 1, p_seed=0.6), rng)
    voynich_like("GEN section generator (c2 section ps=0.6)", g.generate("section", 2, p_seed=0.6), rng)
    emit()
    augustine(rng)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
