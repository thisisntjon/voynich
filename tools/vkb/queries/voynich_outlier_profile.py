"""Where is Voynich unusual? For each (statistic, pipeline, segmenter) with >= 5 natural corpora in corpus_stats,
print Voynich's mean z-score against the natural texts and how many naturals are as extreme.
Usage: python -I tools/vkb/queries/voynich_outlier_profile.py"""
import os, sqlite3, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import DB

c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
g = defaultdict(lambda: {"nat": [], "voy": []})
for stat, pipe, seg, kind, v in c.execute("""SELECT s.statistic, COALESCE(s.pipeline,''), COALESCE(s.segmenter,''), k.kind, s.value
        FROM corpus_stats s JOIN corpora k ON k.corpus_id = s.corpus_id WHERE s.value IS NOT NULL"""):
    if kind == "natural": g[(stat, pipe, seg)]["nat"].append(v)
    elif kind == "voynich": g[(stat, pipe, seg)]["voy"].append(v)
out = []
for k, d in g.items():
    if len(d["nat"]) >= 5 and d["voy"]:
        m = st.mean(d["nat"]); s = st.pstdev(d["nat"]) or 1e-9; vv = st.mean(d["voy"]); z = (vv - m) / s
        out.append((abs(z), k, len(d["nat"]), m, vv, z, sum(1 for x in d["nat"] if (x >= vv if z > 0 else x <= vv))))
for _, k, n, m, vv, z, b in sorted(out, reverse=True):
    print(f"{k[0]:18s} {k[1][:12]:12s} {k[2][:14]:14s} naturals={n:3d} mean={m:8.3f} voynich={vv:8.3f} z={z:6.1f} as_extreme={b}")
