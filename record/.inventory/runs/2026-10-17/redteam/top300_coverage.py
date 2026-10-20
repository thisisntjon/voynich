"""Red-team helper: what share of Voynich tokens do the top-300 types cover (F1/N1/N2 TOPN=300 target)?"""
import sys; sys.path.insert(0, r".")
from collections import Counter
import corpora
toks = corpora.voynich()
c = Counter(toks); n = len(toks)
for k in (100, 300):
    print(f"Voynich tokens={n} types={len(c)} top-{k} coverage={sum(v for _, v in c.most_common(k))/n:.3f}")
for name in ("latin_caesar", "italian_dante"):
    t = corpora.control(name, 25000); cc = Counter(t)
    print(f"{name} top-300 coverage={sum(v for _, v in cc.most_common(300))/len(t):.3f} types={len(cc)}")
