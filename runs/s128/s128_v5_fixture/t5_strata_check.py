# T5: what the frozen s128_f0n2_real.py does on widening, single-page strata, order and overflow (made-up count list, no Voynich data)
import sys, random; sys.path.insert(0, "runs/s128")
import importlib.util
spec = importlib.util.spec_from_file_location("f", "runs/s128/s128_f0n2_real.py"); f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
def P(pg,Q,B,H,L,lens,flags): return dict(page=pg,Q=Q,B=B,H=H,L=L,lens=lens,flags=flags)
# 8 pages: one 2-page stratum (Q1,B1,1,A) = p0,p1; singles p2 (Q1,B2,1,A), p3 (Q1,B3,1,A), p4 (Q2,B1,2,B); p5 held (H '?'); p6 (Q1,B1,1,A) joins p0/p1; p7 (Q2,B2,2,B)
pages = [P("p0","1","1","1","A",[3,3],[1,0]), P("p1","1","1","1","A",[3,3],[1,1]), P("p2","1","2","1","A",[3],[1]),
         P("p3","1","3","1","A",[3],[1]), P("p4","2","1","2","B",[3,3],[1,1]), P("p5","2","1","?","B",[3],[1]),
         P("p6","1","1","1","A",[3],[1]), P("p7","2","2","2","B",[3],[1])]
groups, held, widened = f.strata(pages)
print("A: 4 single-stratum pages (p2,p3,p4,p7) of 8 = 50% > 25% -> widened", widened)
print("   groups (count-list indices):", groups, "held:", held)
print("   expected: (Q1,B1,1,A)=[0,1,6] stays; widened p2,p3 -> W(1,1,A)=[2,3] (do NOT merge into [0,1,6]); p4,p7 -> W(2,2,B)=[4,7]; p5 held")
pages2 = pages[:2] + [pages[6]] + [P("p8","1","1","1","A",[3],[1]), P("p9","1","1","1","A",[3],[1]), P("p2","1","2","1","A",[3],[1])]
g2, h2, w2 = f.strata(pages2)
print("B: 1 single of 6 = 17% <= 25% -> widened", w2, "groups", g2, "(single page stays a 1-page stratum)")
# single-page stratum under n2: paragraph-initial tokens permuted among that page's own paragraph-initial slots only
lay = [f.slots(p) for p in pages]
toks = [[f"{p['page']}_{j}" for j in range(sum(p['lens']))] for p in pages]
rng = random.Random(1); moved_out = 0; p4_perm = set()
for _ in range(300):
    o = f.n2(toks, lay, groups, rng)
    for i, p in enumerate(pages):
        for j in lay[i][0]:
            if not o[i][j].startswith(p["page"] + "_") and i in (5,): moved_out += 1
    p4_perm.add(tuple(o[4][j] for j in lay[4][0]))
print("C: held page p5 start token ever replaced by another page's token:", moved_out, "(expect 0)")
print("   p4 (2 paragraph starts, widened group with p7) start-slot contents seen:", len(p4_perm), "distinct")
# one-page stratum with 2 paragraph starts: permuted within page only
pagesS = [P("s0","9","9","1","A",[2,2],[1,1]), P("s1","8","8","1","A",[2],[1]), P("s2","7","7","1","A",[2],[1]), P("s3","6","6","1","A",[2],[1]),
          P("x0","5","5","1","A",[2],[1]), P("x1","5","5","1","A",[2],[1]), P("x2","5","5","1","A",[2],[1]), P("x3","5","5","1","A",[2],[1]),
          P("x4","5","5","1","A",[2],[1]), P("x5","5","5","1","A",[2],[1]), P("x6","5","5","1","A",[2],[1]), P("x7","5","5","1","A",[2],[1]),
          P("x8","5","5","1","A",[2],[1]), P("x9","5","5","1","A",[2],[1]), P("y0","5","5","1","A",[2],[1]), P("y1","5","5","1","A",[2],[1]),
          P("y2","5","5","1","A",[2],[1])]
gS, hS, wS = f.strata(pagesS)
print("D: 4 singles of 17 = 23.5% <= 25%: widened", wS, "groups", gS)
layS = [f.slots(p) for p in pagesS]; tS = [[f"{p['page']}_{j}" for j in range(sum(p['lens']))] for p in pagesS]
seen = set()
for _ in range(200):
    o = f.n2(tS, layS, gS, rng); seen.add(tuple(o[0][j] for j in layS[0][0]))
print("   s0 (alone, starts at slots", layS[0][0], ") start contents seen:", sorted(seen), "-> permuted within own page only")
# overflow: run()'s rule tk = tk[:need]
need = sum(pages[0]["lens"]); ch = list(range(20)); print("E: chapter of 20 tokens into a page of", need, "slots keeps", ch[:need], "; tokens", ch[need:], "dropped")
# order of filling: strata in order of first page, then held pages
order = [i for g in groups for i in g] + held
print("F: fill order (count-list indices):", order, "(strata by first page, count-list order inside; held pages last, count-list order)")
