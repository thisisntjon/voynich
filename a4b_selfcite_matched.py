"""Experiment 4b: self-citation with distant windows matched on (language, section, hand)."""
import random
from collections import defaultdict
import numpy as np
import corpora
from a4_selfcite import nn

def tokens():
    out = []
    for r in corpora.voynich_lines():
        for w in r["words"]:
            out.append((w, (r["lang"], r["illus"], r["hand"]), r["page"]))
    return out

def run(W, seed=0):
    rng = random.Random(seed)
    toks = tokens()
    words = [t[0] for t in toks]
    groups = defaultdict(list)
    for i, t in enumerate(toks):
        if i >= W and toks[i - W][1] == t[1]:
            groups[t[1]].append(i)
    loc = np.zeros(5); far = np.zeros(5); n = 0
    for g, idx in groups.items():
        if len(idx) < 400:
            continue
        for i in idx[::2]:
            cands = [j for j in (rng.choice(idx) for _ in range(20)) if abs(j - i) > 1500]
            if not cands:
                continue
            j = cands[0]
            loc[nn(words[i], words[i - W:i])] += 1
            far[nn(words[i], words[j - W:j])] += 1
    loc /= loc.sum(); far /= far.sum()
    return loc, far

if __name__ == "__main__":
    for W in [10, 40]:
        l, f = run(W)
        print(f"VMS matched W={W}: exact {l[0]:.3f}/{f[0]:.3f}={l[0]/f[0]:.2f}  d=1 {l[1]:.3f}/{f[1]:.3f}={l[1]/f[1]:.2f}  d<=1 {l[0]+l[1]:.3f}/{f[0]+f[1]:.3f}={(l[0]+l[1])/(f[0]+f[1]):.2f}")
    import a4_selfcite as a4
    for W in [10]:
        a4.W = W
        for n in corpora.CONTROLS:
            l, f = a4.measure(corpora.control(n))
            print(f"{n:16} W={W}: exact {l[0]/f[0]:.2f}  d=1 {l[1]/f[1]:.2f}  d<=1 {(l[0]+l[1])/(f[0]+f[1]):.2f}")
