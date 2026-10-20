"""K2: homophonic nomenclator (word-level codebook) with flow choice + M5 layer.

K1 found a letter-level verbose cipher (Naibbe tables) shows NO within-hand
section NMI even when every section encrypts different Latin, while Voynich
has 0.275 / 0.333; meanwhile F1/F3 need cipher-sized word order (residual
~+0.04, prose +0.14..+0.39). A codebook whose PLAINTEXT WORDS each own several
codewords predicts both: topic words survive as code groups (section NMI),
homophony dilutes word-to-word order (residual), and choosing the codeword
that flows from the previous glyph gives the edge table.

Codebook: plaintext word types sorted by frequency; each gets
h = max(1, round(H * (freq / f_max) ** 0.5 * SCALE)) codewords, taken in rank
order from a Voynich-like pool (Voynich types by frequency, then their
single-glyph-edit neighbours), so frequent words get frequent-looking codes.
Every codeword belongs to exactly one plaintext word (decipherable).
Plaintext: as K1 CIPHER-SEC, each (hand, section) key reads its own stretch of
Latin (Caesar / Augustine alternating), word tokens.
Encryption: per token choose among its codewords with base weight = pool
rank weight x R_flow^1.5 x M5 positional factor (k1.pos_factor), paragraph
starts get a K1 null word.
Rows: Voynich; PLAINTEXT in the same skeleton (sanity: section NMI should
appear, residual prose-sized); nomenclator at three homophone levels;
NULL = nomenclator of the plaintext shuffled across the whole book.
Run: python k2_nomenclator.py  -> results_k2.txt
"""
import random
from collections import Counter
from pathlib import Path

import numpy as np

import c2_section_generator as c2
import corpora
import f3_flow_choice as f3
import k1_joint_producer as k1

OUT = Path(__file__).parent / "results_k2.txt"
log = k1.log


def emit(s=""):
    k1.emit(s)


def plaintext_streams(by, shuffle=False):
    texts = {n: corpora.control(n) for n in ("latin_caesar", "latin_augustine")}
    keys = sorted({(r["hand"], r["illus"]) for recs in by.values() for r in recs})
    need = Counter((r["hand"], r["illus"]) for recs in by.values() for r in recs for _ in r["words"])
    words = {}
    for j, k in enumerate(keys):
        t = texts["latin_caesar" if j % 2 == 0 else "latin_augustine"]
        off = (j * 3_100) % max(len(t) - need[k] - 10, 1)
        words[k] = t[off:off + need[k] + 10]
    if shuffle:
        flat = [w for k in keys for w in words[k]]
        random.Random(4).shuffle(flat)
        it = iter(flat)
        words = {k: [next(it) for _ in words[k]] for k in keys}
    return words


def codeword_pool(g, size, seed=0):
    """Voynich types by frequency, then their single-edit neighbours, then new
    Voynich-like strings: one glyph of a Voynich type replaced by a glyph that
    keeps both adjacent bigrams attested in Voynich (word-internal, with ^/$
    as word edges). Deterministic for a seed."""
    pool = [w for w, _ in g.freq.most_common()]
    seen = set(pool)
    for w in list(pool):
        for nb in g.nb.get(w, ([], []))[0]:
            if nb not in seen:
                seen.add(nb); pool.append(nb)
    big = Counter()
    for w, c in g.freq.items():
        x = "^" + w + "$"
        for a, b2 in zip(x, x[1:]):
            big[(a, b2)] += c
    alphabet = sorted({ch for w in g.freq for ch in w})
    rng = random.Random(seed)
    base = [w for w, _ in g.freq.most_common()]
    weights = [g.freq[w] for w in base]
    tries = 0
    while len(pool) < size and tries < size * 50:
        tries += 1
        w = rng.choices(base, weights)[0]
        i = rng.randrange(len(w))
        x = "^" + w + "$"
        ok = [ch for ch in alphabet if ch != w[i] and big[(x[i], ch)] and big[(ch, x[i + 2])]]
        if not ok:
            continue
        nw = w[:i] + rng.choice(ok) + w[i + 1:]
        if nw not in seen:
            seen.add(nw); pool.append(nw)
    return pool


def codebook(plain_words, g, scale, pool):
    freq = Counter(plain_words)
    ranked = [w for w, _ in freq.most_common()]
    fmax = freq[ranked[0]]
    book, pos = {}, 0
    for w in ranked:
        h = max(1, round(12 * (freq[w] / fmax) ** 0.5 * scale))
        codes = pool[pos:pos + h]
        if not codes:
            raise RuntimeError("codeword pool exhausted")
        pos += len(codes)
        book[w] = [(c, g.freq.get(c, 0) + 1) for c in codes]
    return book, pos, len(pool)


def encrypt(by, streams, book, R, Qi, Qe, para, seed):
    rng = random.Random(seed)
    its = {k: iter(v) for k, v in streams.items()}
    ptypes, pw = list(para), list(para.values())
    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            n = len(r["words"]); line = []
            for i in range(n):
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pw)[0]); continue
                cand = book[next(its[(r["hand"], r["illus"])])]
                prev = line[-1] if line else None
                ws = [c * (R(prev[-1], t[0]) ** k1.BETA if prev else 1) * k1.pos_factor(t, i, n, Qi, Qe)
                      for t, c in cand]
                line.append(rng.choices([t for t, _ in cand], ws)[0])
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


def plain_pages(by, streams):
    its = {k: iter(v) for k, v in streams.items()}
    return {p: [dict(r, words=[next(its[(r["hand"], r["illus"])]) for _ in r["words"]]) for r in recs]
            for p, recs in by.items()}


def main():
    rng = np.random.default_rng(0)
    emit("K2: homophonic nomenclator (word codebook) + flow choice + M5 layer; columns as K1")
    emit()
    by = k1.layout()
    R = f3.ratio_table(by)
    Qi, Qe, para = k1.line_tables(by)
    g = c2.Gen(by)
    k1.bench("VOYNICH", by, rng)
    streams = plaintext_streams(by)
    k1.bench("PLAINTEXT Latin (sanity)", plain_pages(by, streams), rng)
    emit()
    allw = [w for v in streams.values() for w in v]
    pool = codeword_pool(g, 120_000)
    emit(f"  codeword pool: {len(pool)} (Voynich types, neighbours, bigram-consistent single-glyph variants)")
    for scale in (1.0, 2.0, 4.0, 8.0, 16.0):
        book, used, npool = codebook(allw, g, scale, pool)
        hs = sorted(len(v) for v in book.values())
        emit(f"  codebook scale {scale}: plaintext types {len(book)}, codewords used {used} of pool {npool}, "
             f"homophones per word median {hs[len(hs) // 2]} max {hs[-1]}")
        k1.bench(f"NOMENCLATOR x{scale}", encrypt(by, streams, book, R, Qi, Qe, para, 1), rng)
    shuf = plaintext_streams(by, shuffle=True)
    book, _, _ = codebook([w for v in shuf.values() for w in v], g, 4.0, pool)
    k1.bench("NULL nomenclator x4, shuffled plain", encrypt(by, shuf, book, R, Qi, Qe, para, 1), rng)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
