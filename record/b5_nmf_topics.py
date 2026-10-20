"""B5: does NMF topic structure show meaning, or would self-citation give it too?

Claims (user document, Currier A/B section and "four-layer" synthesis):
  NMF on 40-word chunks, run without page boundaries, gives clusters that align
  with the intersection of scribal hand and subject matter (Sterneck, Polish &
  Bowern 2021), and this argues that morphology "maps deterministically" to
  subject matter.
Questions here:
  Q1 does it replicate on ZL3b? (NMI of NMF cluster vs section / hand / Currier)
  Q2 does section signal survive WITHIN one scribe (hand 1: Herbal vs Pharma;
     hand 2: Biological vs Herbal-B vs Astro) against a label-permutation null?
  Q3 does a meaning-free self-citation text (b4 generator), seeded only with
     each page's real first line, reproduce the same alignment?
Controls: Dante (canticle labels) and Augustine Confessiones (book labels),
same chunking. Null: Voynich tokens shuffled across the whole manuscript.
Run: python b5_nmf_topics.py  -> results_b5.txt
"""
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import normalized_mutual_info_score as nmi

import corpora
import b4_selfcite_sim as b4

OUT = Path(__file__).parent / "results_b5.txt"
CHUNK = 40
K = 8
NPERM = 200
SCORE_ROT = []
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def chunks_from_pages(by):
    """Sequential 40-word chunks over the running text (page order), ignoring
    page boundaries; each chunk labelled by the majority page attributes."""
    toks = [(w, r) for recs in by.values() for r in recs for w in r["words"]]
    out = []
    for i in range(0, len(toks) - CHUNK + 1, CHUNK):
        part = toks[i:i + CHUNK]
        lab = lambda key: Counter(r[key] for _, r in part).most_common(1)[0][0]
        out.append(dict(text=" ".join(w for w, _ in part), illus=lab("illus"),
                        hand=lab("hand"), lang=lab("lang"), block=lab("page")))
    return out


def clean_lines(name):
    t = corpora.strip_gutenberg((corpora.CTRL / f"{name}.txt").read_text(encoding="utf-8", errors="replace"))
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    return t.splitlines()


def control_chunks(name, header_re):
    lab, toks = None, []
    for line in clean_lines(name):
        m = re.match(header_re, line.strip())
        if m:
            lab = m.group(1).lower(); continue
        if lab:
            toks += [(w, lab) for w in re.findall(r"[a-z]+", line.lower())]
    out = []
    for i in range(0, len(toks) - CHUNK + 1, CHUNK):
        part = toks[i:i + CHUNK]
        out.append(dict(text=" ".join(w for w, _ in part),
                        label=Counter(l for _, l in part).most_common(1)[0][0], block=i // (5 * CHUNK)))
    return out


def topics(texts, k=K, seed=0):
    X = TfidfVectorizer(min_df=2, token_pattern=r"\S+", sublinear_tf=True).fit_transform(texts)
    W = NMF(n_components=k, init="nndsvda", random_state=seed, max_iter=600).fit_transform(X)
    return W.argmax(1)


def score(cl, labels, rng, blocks):
    """Observed NMI, plus a BLOCK permutation null: labels are reassigned among
    blocks (Voynich: pages; controls: 200-word stretches), so chunks of one
    page stay together. A chunk-level permutation would be anti-conservative,
    because any page-local process (meaningful or not) makes chunks of the same
    page cluster together."""
    labels = np.asarray(labels); cl = np.asarray(cl)
    obs = nmi(labels, cl)
    ub = list(dict.fromkeys(blocks))
    blab = {b: Counter(l for l, bb in zip(labels, blocks) if bb == b).most_common(1)[0][0] for b in ub}
    vals = np.array([blab[b] for b in ub])
    perm = []
    for _ in range(NPERM):
        m = dict(zip(ub, rng.permutation(vals)))
        perm.append(nmi([m[b] for b in blocks], cl))
    # contiguous fake-section null: rotate the page-label sequence (page order kept),
    # so fake sections stay contiguous - controls for drift in writing order.
    rot = []
    for off in range(1, len(ub)):
        m = dict(zip(ub, np.roll(vals, off)))
        rot.append(nmi([m[b] for b in blocks], cl))
    SCORE_ROT.append((float(np.mean(rot)), float(np.max(rot)), float(np.mean(np.array(rot) >= obs))))
    return obs, float(np.mean(perm)), float(np.percentile(perm, 99))


def voynich_block(name, by, rng):
    ch = chunks_from_pages(by)
    cl = topics([c["text"] for c in ch])
    emit(f"[{name}] chunks={len(ch)} K={K}")
    for key in ("illus", "hand", "lang"):
        o, m, p99 = score(cl, [c[key] for c in ch], rng, [c["block"] for c in ch])
        r = SCORE_ROT[-1]
        emit(f"   NMI(cluster, {key:5}) = {o:.3f}   perm-null mean {m:.3f}, 99th pct {p99:.3f} | rotation-null mean {r[0]:.3f}, max {r[1]:.3f}, p={r[2]:.3f}")
    # within-hand section test: refit NMF on that hand's chunks only
    for hand, secs in (("1", ("H", "P")), ("2", ("B", "H", "T"))):
        sub = [c for c in ch if c["hand"] == hand and c["illus"] in secs]
        if len(sub) < 30:
            continue
        cl2 = topics([c["text"] for c in sub], k=len(secs) + 2)
        o, m, p99 = score(cl2, [c["illus"] for c in sub], rng, [c["block"] for c in sub])
        cnt = Counter(c["illus"] for c in sub)
        r = SCORE_ROT[-1]
        emit(f"   within hand {hand} {dict(cnt)}: NMI(cluster, section) = {o:.3f}  null {m:.3f} / p99 {p99:.3f} | rotation mean {r[0]:.3f}, max {r[1]:.3f}, p={r[2]:.3f}")
    return ch


def main():
    rng = np.random.default_rng(0)
    emit("B5: NMF topic alignment (TF-IDF, 40-word chunks, argmax topic as cluster)")
    emit(f"NMI = normalised mutual information; null = labels permuted among pages/blocks ({NPERM}x), mean and 99th pct")
    emit("rotation null = page-label sequence rotated by every offset (fake sections stay contiguous); p = share of offsets >= observed")
    emit()
    by = b4.pages()
    ch = voynich_block("VOYNICH ZL3b", by, rng)

    # null: all tokens shuffled across the manuscript, page labels kept
    flat = [w for recs in by.values() for r in recs for w in r["words"]]
    random.Random(5).shuffle(flat)
    it = iter(flat)
    shuf = {p: [dict(r, words=[next(it) for _ in r["words"]]) for r in recs] for p, recs in by.items()}
    voynich_block("NULL token-shuffled", shuf, rng)

    for v in ("seeded", "global"):
        voynich_block(f"SIM self-citation ({v} first line)", b4.generate(v, 11, by), rng)
        voynich_block(f"SIMcal self-citation ({v})", b4.generate(v, 12, by, p_samecol=0.05, p_mut=0.97,
                                                              recent_lines=99), rng)

    emit()
    for name, hdr in (("italian_dante", r"^(INFERNO|PURGATORIO|PARADISO)$"),
                      ("latin_augustine", r"^LIBER ([A-Z ]+?)\.?$")):
        cc = control_chunks(name, hdr)
        cl = topics([c["text"] for c in cc])
        o, m, p99 = score(cl, [c["label"] for c in cc], rng, [c["block"] for c in cc])
        emit(f"[CTRL {name}] chunks={len(cc)} labels={dict(Counter(c['label'] for c in cc))}")
        r = SCORE_ROT[-1]
        emit(f"   NMI(cluster, label) = {o:.3f}   null {m:.3f} / p99 {p99:.3f} | rotation mean {r[0]:.3f}, max {r[1]:.3f}, p={r[2]:.3f}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
