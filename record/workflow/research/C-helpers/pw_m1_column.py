"""Power curve for m1's column-specific excess. Uses m1_coordinates.build_pages/collect/boot
unchanged (real boxes). Base = m1 null 1 (words shuffled within each line, boxes fixed).
Injection: each token on line n whose nearest line n-1 token is within 0.5 W is replaced by
that token's word (exact same-column copy) with probability r. Detection = P(column-specific
excess <= 0) < 0.05 under the page-cluster bootstrap (N_BOOT=300). Also: seed sensitivity
of the filed P on the REAL data (the far line is a random draw).
Run: python -I workflow/research/C-helpers/pw_m1_column.py"""
import sys, time, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import numpy as np
import m1_coordinates as m

t0 = time.time()
pages, _ = m.build_pages()
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 10
print(f"pages {len(pages)} aligned paragraph lines {sum(len(p['lines']) for p in pages.values())}  build {time.time()-t0:.1f}s")
print("[real data] P(column-specific<=0) and P(same-far<=0) over far-line draw seeds (filed: 0.068 with seed 20261017):")
for seed in range(NSEED):
    rng = np.random.default_rng(seed)
    res = m.collect(pages, rng)
    _, dci = m.boot(res, rng, n_boot=300)
    print(f"  seed {seed}: n_same={len(res['same'])} col-spec [{dci['column-specific'][0]:+.2f},{dci['column-specific'][1]:+.2f}] P={dci['column-specific'][2]:.3f}   same-far P={dci['same-far'][2]:.3f}")

def inject(pages, r, rr):
    out = {}
    for folio, pg in pages.items():
        W = pg["W"]
        by_no = {}
        new_lines = []
        for no, toks in pg["lines"]:
            words = [t["word"] for t in toks]
            rr.shuffle(words)                      # null 1: within-line shuffle, boxes fixed
            toks2 = [dict(t, word=w) for t, w in zip(toks, words)]
            prev = by_no.get(no - 1)
            if prev is not None:
                pc = [t for t in prev if m.ok_word(t["word"])]
                for t in toks2:
                    if pc and rr.random() < r:
                        d, c = m.nearest(t, pc)
                        if d <= 0.5 * W:
                            t["word"] = c["word"]
            by_no[no] = toks2
            new_lines.append((no, toks2))
        out[folio] = dict(pg, lines=new_lines)
    return out

R_GRID = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.0, 0.005, 0.01, 0.015, 0.02, 0.03, 0.05]
print(f"\n[injection] r = per-token probability of an exact same-column copy from line n-1 on top of the within-line shuffle; {NSEED} seeds")
for r in R_GRID:
    ps, pf, exc = [], [], []
    for seed in range(NSEED):
        rr = random.Random(1000 + seed)
        pg = inject(pages, r, rr)
        rng = np.random.default_rng(seed)
        res = m.collect(pg, rng)
        rs, ro, rf, rof = (m.rates(res[c])["le1"] for c in ("same", "off", "far", "off_far"))
        exc.append((rs - rf) - (ro - rof))
        _, dci = m.boot(res, rng, n_boot=300)
        ps.append(dci["column-specific"][2]); pf.append(dci["same-far"][2])
    print(f"  r={r:.3f}  col-spec excess mean {np.mean(exc):+.2f} pp  P: {' '.join(f'{p:.3f}' for p in ps)}  detect={np.mean([p<0.05 for p in ps]):.1f}   same-far detect={np.mean([p<0.05 for p in pf]):.1f}  t={time.time()-t0:.0f}s")
