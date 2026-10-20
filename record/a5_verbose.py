"""Experiment 5: can a verbose-cipher reading reach natural-language statistics?

Greedy BPE merges glyph pairs into units. After each merge we record the
unit-alphabet size, conditional entropy h2 (unit | previous unit, word
boundary included) and units per word. A plaintext alphabet (Latin ~23-26
letters) with h2 ~3.1-3.3 and ~5-6 letters/word is the target.
"""
import math
from collections import Counter

import corpora


def h2(seqs):
    s = []
    for q in seqs:
        s += list(q) + ["_"]
    c1 = Counter(s); c2 = Counter(zip(s, s[1:]))
    n1, n2 = len(s), len(s) - 1
    H1 = -sum(v / n1 * math.log2(v / n1) for v in c1.values())
    H12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    return len(c1) - 1, H1, H12 - H1


def bpe(words, steps):
    vocab = Counter(tuple(w) for w in words)
    hist = []
    for k in range(steps + 1):
        seqs = [s for s, c in vocab.items() for _ in range(c)]
        a, H1, H2 = h2(seqs)
        upw = sum(len(s) * c for s, c in vocab.items()) / sum(vocab.values())
        hist.append((k, a, H1, H2, upw))
        pairs = Counter()
        for s, c in vocab.items():
            for p in zip(s, s[1:]):
                pairs[p] += c
        if not pairs:
            break
        (x, y), _ = pairs.most_common(1)[0]
        new = Counter()
        for s, c in vocab.items():
            out, i = [], 0
            while i < len(s):
                if i + 1 < len(s) and s[i] == x and s[i + 1] == y:
                    out.append(x + y); i += 2
                else:
                    out.append(s[i]); i += 1
            new[tuple(out)] += c
        vocab = new
    return hist, vocab


def main():
    vw = corpora.voynich()
    hist, vocab = bpe(vw, 40)
    print("merge alpha   H1    h2   units/word")
    for k, a, H1, H2, u in hist[::4]:
        print(f"{k:5} {a:5} {H1:5.2f} {H2:5.2f} {u:6.2f}")
    best = max(hist, key=lambda t: t[3])
    print("max h2 reached:", best)
    for n in corpora.CONTROLS:
        a, H1, H2 = h2(corpora.control(n, 25000))
        print(f"{n:16} alpha {a:3} H1 {H1:.2f} h2 {H2:.2f}")

    # What happens to the controls under a verbose cipher? (each letter -> 2 glyphs
    # from a small inventory, chosen deterministically) -- shows h2 halving is natural.
    import random
    rng = random.Random(1)
    lat = corpora.control("latin_caesar", 25000)
    letters = sorted(set("".join(lat)))
    glyphs = "abcdefgh"
    code = {}
    pool = [x + y for x in glyphs for y in glyphs]
    rng.shuffle(pool)
    for L, c in zip(letters, pool):
        code[L] = c
    enc = ["".join(code[ch] for ch in w) for w in lat]
    a, H1, H2 = h2(enc)
    print(f"Latin under 1->2 verbose code: alpha {a} H1 {H1:.2f} h2 {H2:.2f} len {sum(map(len,enc))/len(enc):.1f}")
    print("Top merged units:", Counter(u for s, c in vocab.items() for u in s for _ in range(c)).most_common(30))


if __name__ == "__main__":
    main()
