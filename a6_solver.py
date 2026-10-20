"""Experiment 6: homophonic-substitution decipherment attempt with controls.

Voynich text is segmented into units (BPE, k merges). The solver searches a
many-to-one map unit -> plaintext letter that maximises a character-trigram
language model (word spaces kept). Score = mean log2 P per character.

Controls:
  POS  - Latin (Caesar, unseen by the LM) enciphered with a random homophonic
         key of the same alphabet size: the solver should recover it.
  NULL - "pseudo-Voynich": text sampled from Voynich's OWN unit-bigram model.
         It has Voynich's surface statistics and no meaning. If real Voynich
         scores no better than NULL, the solver's "best reading" is noise.
"""
import math
import re
import random
import sys
from collections import Counter

import numpy as np

import corpora
from a5_verbose import bpe

ALPH = "_abcdefghijklmnopqrstuvwxyz"
IDX = {c: i for i, c in enumerate(ALPH)}
SAMPLE_WORDS = 2500


ROMAN = re.compile(r"^[ivxlcdm]+$")


def train_lm(words, k=0.1):
    words = [w for w in words if not ROMAN.match(w)]
    t = np.full((27, 27, 27), k)
    s = [0]
    for w in words:
        s += [IDX[c] for c in w if c in IDX] + [0]
    s = np.array(s)
    np.add.at(t, (s[:-2], s[1:-1], s[2:]), 1)
    t /= t.sum(axis=2, keepdims=True)
    uni = np.bincount(s, minlength=27)[1:].astype(float) + 1
    return np.log2(t), uni / uni.sum()


LAMBDA = 1.0


def objective(lm, seqs_abc, m):
    tri, uni = lm
    a, b, c = seqs_abc
    dec = m[b]
    q = np.bincount(dec, minlength=27)[1:].astype(float) + 0.5
    q /= q.sum()
    kl = np.sum(q * np.log2(q / uni))
    return tri[m[a], m[b], m[c]].mean() - LAMBDA * kl


def lm_score(lm, words):
    lm = lm[0]
    s = [0]
    for w in words:
        s += [IDX[c] for c in w if c in IDX] + [0]
    s = np.array(s)
    return lm[s[:-2], s[1:-1], s[2:]].mean()


def solve(units_seq, n_units, lm, iters=40000, restarts=4, seed=0):
    """units_seq: int array with 0 = space, units 1..n_units."""
    rng = np.random.default_rng(seed)
    best_all = (-1e9, None)
    a, b, c = units_seq[:-2], units_seq[1:-1], units_seq[2:]
    for r in range(restarts):
        m = np.concatenate([[0], rng.integers(1, 27, n_units)])
        cur = objective(lm, (a, b, c), m)
        T0 = 0.02
        for it in range(iters):
            u = rng.integers(1, n_units + 1)
            old = m[u]
            m[u] = rng.integers(1, 27)
            sc = objective(lm, (a, b, c), m)
            T = T0 * (1 - it / iters) + 1e-5
            if sc >= cur or rng.random() < math.exp((sc - cur) / T):
                cur = sc
            else:
                m[u] = old
        if cur > best_all[0]:
            best_all = (cur, m.copy())
    return best_all


def encode_units(seqs):
    inv = {}
    out = [0]
    for s in seqs:
        for u in s:
            out.append(inv.setdefault(u, len(inv) + 1))
        out.append(0)
    return np.array(out), inv


def voynich_units(k):
    vw = corpora.voynich()
    _, vocab = bpe(vw, k)
    # map each word to its segmentation
    seg = {}
    for s in vocab:
        seg["".join(s)] = s
    return [seg[w] for w in vw]


def pseudo(seqs, n_words, seed):
    """Sample text from the unit-bigram model of seqs (word boundaries included)."""
    rng = random.Random(seed)
    trans = {}
    for s in seqs:
        q = ["_"] + list(s) + ["_"]
        for x, y in zip(q, q[1:]):
            trans.setdefault(x, []).append(y)
    out = []
    while len(out) < n_words:
        w, x = [], "_"
        while True:
            x = rng.choice(trans[x])
            if x == "_" or len(w) > 12:
                break
            w.append(x)
        if w:
            out.append(tuple(w))
    return out


def homophonic(words, n_sym, seed):
    rng = random.Random(seed)
    letters = [c for c in ALPH[1:]]
    freq = Counter(c for w in words for c in w)
    syms = list(range(n_sym))
    rng.shuffle(syms)
    key = {L: [syms.pop()] for L in letters if syms}
    # spread remaining symbols over frequent letters (homophones)
    for L, _ in freq.most_common():
        if not syms:
            break
        key.setdefault(L, []).append(syms.pop())
    return [tuple(f"s{rng.choice(key[c])}" for c in w if c in key) for w in words], key


def decode(m, inv, seqs, n=12):
    return " ".join("".join(ALPH[m[inv[u]]] for u in s) for s in seqs[:n])


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    lms = {
        "latin": train_lm(corpora.control("latin_augustine")),
        "italian": train_lm(corpora.control("italian_dante")),
        "german": train_lm(corpora.control("german_faust") + corpora.control("german_kafka")),
    }
    vseq = voynich_units(k)[:SAMPLE_WORDS]
    n_units = len({u for s in vseq for u in s})
    print(f"BPE merges={k}: {n_units} distinct units in sample, {np.mean([len(s) for s in vseq]):.2f} units/word")

    caesar = corpora.control("latin_caesar")[:SAMPLE_WORDS]
    ref = lm_score(lms["latin"], caesar)
    print(f"Reference: genuine Caesar under Latin LM = {ref:.3f} bits/char (ceiling)")

    pos, key = homophonic(caesar, n_units, seed=3)
    seq, inv = encode_units(pos)
    sc, m = solve(seq, len(inv), lms["latin"])
    truth = {f"s{s}": L for L, ss in key.items() for s in ss}
    acc = np.mean([ALPH[m[inv[u]]] == truth[u] for s in pos for u in s])
    print(f"POS control (homophonic Latin, {len(inv)} syms): score {sc:.3f}, letter accuracy {acc:.1%}")
    print("   ", decode(m, inv, pos))

    for lang, lm in lms.items():
        seq, inv = encode_units(vseq)
        sc, m = solve(seq, len(inv), lm)
        nulls = []
        for s in range(3):
            ps = pseudo(voynich_units(k), SAMPLE_WORDS, seed=s)
            pseq, pinv = encode_units(ps)
            nulls.append(solve(pseq, len(pinv), lm, seed=s + 10)[0])
        print(f"VMS -> {lang:8}: score {sc:.3f}  vs pseudo-VMS null {np.mean(nulls):.3f}±{np.std(nulls):.3f}")
        print("    ", decode(m, inv, vseq))


if __name__ == "__main__":
    main()
