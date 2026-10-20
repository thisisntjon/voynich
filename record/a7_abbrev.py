"""Experiment 7: Zipf's law of abbreviation (frequent words are shorter).
Spearman correlation between word frequency and length over types with freq>=3,
plus mean length of the 50 most frequent types vs all tokens."""
from collections import Counter
import numpy as np
from scipy.stats import spearmanr
import corpora

def run(name, ws):
    ws = ws[:25000]; c = Counter(ws)
    types = [w for w, v in c.items() if v >= 3]
    rho = spearmanr([c[w] for w in types], [len(w) for w in types]).correlation
    top = np.mean([len(w) for w, _ in c.most_common(50)])
    allm = np.mean([len(w) for w in ws])
    print(f"{name:16} rho={rho:+.3f}  top50 len={top:.2f}  token mean len={allm:.2f}  ratio={top/allm:.2f}")

run("VMS eva", corpora.voynich())
run("VMS glyph+", corpora.voynich(tokenization="glyph+"))
for n in corpora.CONTROLS:
    run(n, corpora.control(n))
