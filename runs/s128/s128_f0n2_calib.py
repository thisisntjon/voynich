import random, statistics as st
from collections import Counter
import s128_herbal_profile as s  # runs/s128/s128_herbal_profile.py
E = s.load_egerton()
def page(c, N, mode):
    tk = [t for l in c['lines'] for t in l][:N]
    stv = s.stem_of(s.key_name(c['name']))
    if mode == 'rarity':   # name removed; first token = fresh non-recurring type
        tk = ['et' if t.startswith(stv) else t for t in tk]
        tk[0] = 'RARE_' + str(id(c))
    return tk
def S(P, tot):
    h = 0
    for tk in P:
        cnt = Counter(tk); Q = [w for w, k in cnt.items() if k >= 2 and k / tot[w] >= 0.9]
        if Q: h += min(tk.index(w) for w in Q) < 8
    return h / len(P)
def n2(P, strata, rng):
    out = [tk[:] for tk in P]
    for grp in strata:
        firsts = [out[i][0] for i in grp]; rng.shuffle(firsts)
        for i, f in zip(grp, firsts): out[i][0] = f
    for tk in out:
        li = [j for j in range(8, len(tk), 8)]; vals = [tk[j] for j in li]; rng.shuffle(vals)
        for j, v in zip(li, vals): tk[j] = v
        oth = [j for j in range(1, len(tk)) if j % 8]; vals = [tk[j] for j in oth]; rng.shuffle(vals)
        for j, v in zip(oth, vals): tk[j] = v
    return out
def n1(P, rng):
    out = []
    for tk in P: t = tk[:]; rng.shuffle(t); out.append(t)
    return out
for mode in ('name', 'rarity'):
    for N in (60, 90):
        passes2 = passes1 = 0; vals = []
        for i in range(15):
            rng = random.Random(20261031 + i)
            starts = rng.sample(range(0, len(E) - 4, 4), 28)
            P = [page(E[b + k], N, mode) for b in starts for k in range(4)]
            strata = [list(range(4 * g, 4 * g + 4)) for g in range(28)]
            tot = Counter(); [tot.update(tk) for tk in P]
            o = S(P, tot)
            q2 = sorted(S(n2(P, strata, rng), tot) for _ in range(200))[197]
            q1 = sorted(S(n1(P, rng), tot) for _ in range(200))[197]
            passes2 += o > q2; passes1 += o > q1; vals.append((round(o,3), round(q1,3), round(q2,3)))
        print(mode, N, 'N2 pass', passes2, '/15  N1 pass', passes1, '/15', 'median S', st.median(v[0] for v in vals), 'median q1', st.median(v[1] for v in vals), 'median q2', st.median(v[2] for v in vals))
