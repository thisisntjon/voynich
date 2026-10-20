"""B3: test the document's specific slot-grammar and entropy claims.

Claims (user document, "Three-Slot Morphological Grammar" section):
  C1 q is almost always followed by o ("as q requires u in Latin").
  C2 prefixes qo-/o-/y- are normally followed by a gallows (t k p f);
     ch-/sh-/d- normally are not.  Is this more than a bigram fact?
  C3 m n g v are restricted almost exclusively to word-final position.
  C4 "shuffling the order of words leaves the low character entropy intact,
     proving the anomaly is internal word construction" - is that specific to
     Voynich, or true of every text?
  C5 "nearly every word belongs to a dense neighbourhood of lookalike words
     differing by a single glyph" (the argument against Bax's cribs).
Controls: six natural-language texts (25k tokens). Null: Voynich-bigram
pseudo-text (a6_solver.pseudo over EVA chars) - reproduces every 1-step
character dependency and nothing else.
Run: python b3_slot_claims.py  -> results_b3.txt
"""
import math
import random
from collections import Counter
from pathlib import Path

import corpora
from a6_solver import pseudo

OUT = Path(__file__).parent / "results_b3.txt"
N = 25000
GALLOWS = set("tkpf")
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def h2(seq):
    c1 = Counter(seq); c2 = Counter(zip(seq, seq[1:]))
    n1 = sum(c1.values()); n2 = sum(c2.values())
    H1 = -sum(v / n1 * math.log2(v / n1) for v in c1.values())
    H12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    return H12 - H1


def stream(words):
    return list("_".join(words))


def after(words, pre, k=1):
    """Distribution of the next char after word-initial prefix `pre`."""
    c = Counter(w[len(pre)] for w in words if w.startswith(pre) and len(w) > len(pre))
    return c


def gallows_rate(words, pre, mid_only=False):
    c = after(words, pre)
    n = sum(c.values())
    return (sum(v for k, v in c.items() if k in GALLOWS) / n if n else float("nan")), n


def mid_gallows_rate(words, ch):
    """P(next is gallows | char ch occurs NOT word-initially) - baseline for C2."""
    n = g = 0
    for w in words:
        for i in range(1, len(w) - 1):
            if w[i] == ch:
                n += 1; g += w[i + 1] in GALLOWS
    return g / n if n else float("nan"), n


def neighbour_density(words, top=2000):
    freq = Counter(words)
    vocab = set(freq)
    alph = sorted(set("".join(vocab)))
    types = [w for w, _ in freq.most_common(top)]

    def has_nb(w):
        for i in range(len(w) + 1):
            for a in alph:                       # insertion
                if w[:i] + a + w[i:] in vocab:
                    return True
            if i < len(w):
                if w[:i] + w[i + 1:] in vocab:   # deletion
                    return True
                for a in alph:                   # substitution
                    if a != w[i] and w[:i] + a + w[i + 1:] in vocab:
                        return True
        return False
    hits = [has_nb(w) for w in types]
    tok = sum(freq[w] for w, h in zip(types, hits) if h) / sum(freq[w] for w in types)
    return sum(hits) / len(types), tok


def main():
    V = corpora.voynich()[:N]
    rng = random.Random(7)
    ps = ["".join(t) for t in pseudo([tuple(w) for w in V], N, 7)]
    sets = [("voynich_eva", V), ("NULL_bigram_pseudo", ps)] + \
           [(n, corpora.control(n, N)) for n in corpora.CONTROLS]

    emit("=== C1: q -> o binding ===")
    for name, W in sets[:2]:
        c = Counter()
        for w in W:
            for i, ch in enumerate(w[:-1]):
                if ch == "q":
                    c[w[i + 1]] += 1
        n = sum(c.values())
        qi = sum(w.startswith("q") for w in W) / sum("q" in w for w in W)
        emit(f"{name:20} P(o|q)={c['o']/n:.3f} (n={n})  q word-initial share={qi:.3f}")
    for name, W in sets[2:]:
        c = Counter(w[i + 1] for w in W for i, ch in enumerate(w[:-1]) if ch == "q")
        n = sum(c.values())
        if n:
            emit(f"{name:20} P(u|q)={c['u']/n:.3f} (n={n})")
    emit()

    emit("=== C2: does the prefix class predict a following gallows? ===")
    emit("P(next char is t/k/p/f | word starts with prefix); baseline = same char word-internally")
    for name, W in sets[:2]:
        emit(f"[{name}]")
        for pre in ("qo", "o", "y", "ch", "sh", "d"):
            r, n = gallows_rate(W, pre)
            last = pre[-1] if pre not in ("ch", "sh") else "h"
            b, nb = mid_gallows_rate(W, last)
            emit(f"   {pre+'-':4} -> gallows {r:6.3f} (n={n:5})   internal '{last}' -> gallows {b:.3f} (n={nb})")
        # qo- vs bare o-: second-order effect beyond bigram
        rq, _ = gallows_rate(W, "qo"); ro, _ = gallows_rate([w for w in W if w.startswith("o")], "o")
        emit(f"   second-order check: P(gallows|qo-)={rq:.3f} vs P(gallows|o-)={ro:.3f}")
    emit()

    emit("=== C3: word-final restriction ===")
    emit("share of each glyph's occurrences that are word-final (glyphs with >=200 tokens)")
    for name, W in sets:
        tot, fin = Counter(), Counter()
        for w in W:
            for i, ch in enumerate(w):
                tot[ch] += 1; fin[ch] += i == len(w) - 1
        rows = sorted(((fin[c] / tot[c], c) for c in tot if tot[c] >= 200), reverse=True)
        frac90 = sum(1 for r, _ in rows if r >= 0.9)
        emit(f"{name:20} glyphs>=90% final: {frac90:2}  top: " + " ".join(f"{c}:{r:.2f}" for r, c in rows[:6]))
    emit()

    emit("=== C4: h2 (spaces as a symbol) under word-order and within-word shuffles ===")
    emit(f"{'corpus':20} {'orig':>6} {'word-shuf':>9} {'d':>6} {'char-shuf-in-word':>17} {'d':>6}")
    for name, W in sets:
        o = h2(stream(W))
        ws = W[:]; rng.shuffle(ws); s1 = h2(stream(ws))
        cs = ["".join(rng.sample(w, len(w))) for w in W]; s2 = h2(stream(cs))
        emit(f"{name:20} {o:6.3f} {s1:9.3f} {s1-o:+6.3f} {s2:17.3f} {s2-o:+6.3f}")
    emit()

    emit("=== C5: single-edit neighbourhoods (top 2000 types; vocabulary from same 25k tokens) ===")
    emit(f"{'corpus':20} {'types w/ nb':>11} {'token-weighted':>14}")
    for name, W in sets:
        t, k = neighbour_density(W)
        emit(f"{name:20} {t:11.3f} {k:14.3f}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
