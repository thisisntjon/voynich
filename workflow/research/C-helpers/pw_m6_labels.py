"""Power curve for m6's list-order test (shared 2-char prefix rate of adjacent labels vs
within-page shuffle). m6_labels.py is module-level code (cannot be imported), so adj_stats and
list_test are re-implemented minimally (same definitions: first/last glyph via m6 rules, 200 shuffles,
p = (#null>=obs + 1)/(201)). Injection: for each adjacent pair in ZL order, with probability r the
second label takes the first label's 2-char prefix. Groups and sizes as in results_m6 §4.
Run: python -I workflow/research/C-helpers/pw_m6_labels.py"""
import sys, re, random, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import numpy as np
import vparse

recs = vparse.load()
page_order = list(dict.fromkeys(r["page"] for r in recs))
LAB = [dict(page=r["page"], unit=r["unit"], word=w) for r in recs if r["unit"].startswith("L") for w in r["words"] if "?" not in w]
NSHUF = 200

def pre2_rate(seqs):
    n = h = 0
    for s in seqs:
        for a, b in zip(s, s[1:]):
            n += 1; h += a[:2] == b[:2]
    return h / n, n

def ptest(seqs, rng):
    obs, n = pre2_rate(seqs)
    null = []
    for _ in range(NSHUF):
        sh = []
        for s in seqs:
            s2 = s[:]; rng.shuffle(s2); sh.append(s2)
        null.append(pre2_rate(sh)[0])
    p = (sum(v >= obs for v in null) + 1) / (NSHUF + 1)
    return obs, float(np.mean(null)), float(np.std(null)), p, n

def inject(seqs, r, rr):
    out = []
    for s in seqs:
        s2 = s[:]
        for i in range(1, len(s2)):
            if rr.random() < r and len(s2[i]) >= 2:
                s2[i] = s2[i - 1][:2] + s2[i][2:]
        out.append(s2)
    return out

def page_labels(pages, prefix):
    out = []
    for p in pages:
        s = [t["word"] for t in LAB if t["page"] == p and t["unit"].startswith(prefix)]
        if len(s) >= 2: out.append(s)
    return out

star = ["f68r1", "f68r2", "f68r3"]
zod = [p for p in page_order if p in {"f70v2","f70v1","f71r","f71v","f72r1","f72r2","f72r3","f72v3","f72v2","f72v1","f73r","f73v"}]
pharma = [p for p in page_order if any(t["page"] == p and t["unit"] in ("Lc", "Lf") for t in LAB)]
groups = [("STARS Ls", page_labels(star, "Ls")), ("ZODIAC Lz", page_labels(zod, "Lz")),
          ("PHARMA Lc", page_labels(pharma, "Lc")), ("PHARMA Lf", page_labels(pharma, "Lf")),
          ("ALL L*", [[t["word"] for t in LAB if t["page"] == p] for p in page_order if sum(t["page"] == p for t in LAB) >= 2])]
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 10
R_GRID = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
t0 = time.time()
for name, seqs in groups:
    obs, m, sd, p, n = ptest(seqs, random.Random(20261017))
    print(f"[{name}] pages={len(seqs)} pairs={n} observed pre2 {obs:.3f} null {m:.3f}+-{sd:.3f} p={p:.3f}  (m6 filed obs listed in results_m6 §4)")
    for r in R_GRID:
        ps = []; obsv = []
        for seed in range(NSEED):
            rr = random.Random(500 + seed)
            # base = within-page shuffled order (no list structure), then inject
            base = [random.Random(900 + seed).sample(s, len(s)) for s in seqs]
            inj = inject(base, r, rr)
            o, m_, sd_, p_, _ = ptest(inj, random.Random(seed))
            ps.append(p_); obsv.append(o - m_)
        print(f"   r={r:.2f}  excess pre2 {np.mean(obsv):+.3f}  p: {' '.join(f'{x:.3f}' for x in ps)}  detect={np.mean([x<0.05 for x in ps]):.1f}  t={time.time()-t0:.0f}s")
