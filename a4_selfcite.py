"""Experiment 4: local self-similarity (Timm & Schinner self-citation test).

For each token, distance to its nearest neighbour (Levenshtein) among the W
preceding tokens ("local") vs among W tokens taken from a random far-away
position in the same text ("distant"). Natural language has topical
burstiness too, so the key number is the local/distant contrast relative to
the controls, especially for NEAR-MISSES (distance exactly 1), which
copying-with-mutation predicts and meaningful text does not.
"""
import random
from functools import lru_cache

import numpy as np

import corpora

W = 40
N = 12000


@lru_cache(maxsize=None)
def lev(a, b):
    if a == b:
        return 0
    if abs(len(a) - len(b)) > 3:
        return 4
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return min(prev[-1], 4)


def nn(word, window):
    best = 4
    for v in set(window):
        d = lev(word, v)
        if d < best:
            best = d
            if d == 0:
                break
    return best


def measure(words, seed=0):
    rng = random.Random(seed)
    words = words[:N]
    loc = np.zeros(5); dist = np.zeros(5)
    for i in range(W, len(words)):
        w = words[i]
        loc[nn(w, words[i - W:i])] += 1
        j = rng.randrange(W, len(words))
        while abs(j - i) < 2000:
            j = rng.randrange(W, len(words))
        dist[nn(w, words[j - W:j])] += 1
    return loc / loc.sum(), dist / dist.sum()


def main():
    texts = [("VMS eva", corpora.voynich()),
             ("VMS lang B", corpora.voynich(lambda r: r["lang"] == "B")),
             ("VMS lang A", corpora.voynich(lambda r: r["lang"] == "A"))]
    texts += [(n, corpora.control(n)) for n in corpora.CONTROLS]
    print(f"{'text':16} {'exact loc':>9} {'exact far':>9} {'ratio':>6} | {'d=1 loc':>8} {'d=1 far':>8} {'ratio':>6} | {'<=1 loc':>8}")
    for name, ws in texts:
        l, d = measure(ws)
        print(f"{name:16} {l[0]:9.3f} {d[0]:9.3f} {l[0]/d[0]:6.2f} | {l[1]:8.3f} {d[1]:8.3f} {l[1]/d[1]:6.2f} | {l[0]+l[1]:8.3f}")


if __name__ == "__main__":
    main()
