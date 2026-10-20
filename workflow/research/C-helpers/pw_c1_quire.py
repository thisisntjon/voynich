"""Power curve for c1's quire-block null (test A). Injection: start from token-shuffled
Voynich (c1's NULL), then replace each token with probability s by a draw from the REAL
unigram distribution of that record's section (bag-level section vocabulary). s=1 is the
bag-level section signal, s=0 is the null. Uses c1.chunks/block_test and b5.topics unchanged.
Run: python -I workflow/research/C-helpers/pw_c1_quire.py"""
import sys, time, random
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import numpy as np
import b4_selfcite_sim as b4
import b5_nmf_topics as b5
import c1_quire_null as c1
import c2_section_generator as c2

t0 = time.time()
by = b4.pages()
flat = [w for recs in by.values() for r in recs for w in r["words"]]
sec_vocab = {}
for recs in by.values():
    for r in recs:
        sec_vocab.setdefault((r["hand"], r["illus"]), []).extend(r["words"])
S_GRID = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 5
print(f"s = share of tokens replaced by a draw from the real (hand,section) unigram bag; base = token-shuffled Voynich")
print(f"detect = p<0.05 under c1 exact quire-block null (hand1 floor 1/55=0.018, hand2 floor 1/105=0.0095); {NSEED} seeds per s")
for hand, secs in c2.WITHIN:
    print(f"[hand {hand} sections {secs}]")
    for s in S_GRID:
        nmis, ps, nb = [], [], None
        for seed in range(NSEED):
            rr = random.Random(100 + seed)
            fl = flat[:]; rr.shuffle(fl); it = iter(fl)
            byn = {}
            for p, recs in by.items():
                out = []
                for r in recs:
                    ws = [next(it) for _ in r["words"]]
                    pool = sec_vocab[(r["hand"], r["illus"])]
                    ws = [rr.choice(pool) if rr.random() < s else w for w in ws]
                    out.append(dict(r, words=ws))
                byn[p] = out
            ch = c1.chunks(byn)
            sub = [dict(c, blk=c["quire"] + c["sec"]) for c in ch if c["hand"] == hand and c["sec"] in secs]
            cl = b5.topics([c["text"] for c in sub], k=len(secs) + 2)
            r = c1.block_test(sub, cl, np.random.default_rng(seed))
            nmis.append(r["obs"]); ps.append(r["p"]); nb = (r["nb"], r["na"])
        det = sum(p < 0.05 for p in ps) / NSEED
        print(f"  s={s:.2f}  NMI mean {np.mean(nmis):.3f} (min {min(nmis):.3f} max {max(nmis):.3f})  p: {' '.join(f'{p:.3f}' for p in ps)}  detect={det:.1f}  blocks={nb[0]} assignments={nb[1]}  t={time.time()-t0:.0f}s")
