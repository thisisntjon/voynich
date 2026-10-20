"""r10.py -- what makes cores repeat inside lines? (voynich-91, Roach; blind)

Queue message SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-QUEUE-20261018T202417Z, item r10.
Local import: ../r7/r7.py (frozen r7: loaders, S1, S2 MDL inducer, mi_mm). Own code only.

CORES: S1 (r3 lists) and S2 (r7 MDL inducer fitted on the whole of ZL). Empty
  cores are dropped from each line's sequence. Data: ZL3b-n paragraph loci, LOQO
  over the 15 quires with >= 50 lines.
QUANTITIES per held-out quire (core space):
  t1 = R_w(1), t2 = R_w(2), t3 = mean R_w(3..6): identity rate at in-line
       distance d / the exact within-PAGE expectation (r5-style).
       REVISION 2 (after fixture run 2, before the freeze): the within-line
       baseline was invariant for an exchangeable line pool (R = 1 at every d),
       so line clustering was invisible and a planted pool was matched by copy-recent.
  t4 = R_x'(1): identity of (last core of line n, first core of line n+1), same
       page, / the exact within-page expectation;
  t5 = order: Miller-Madow MI at K=100 (the 99 most frequent training cores +
       pool) minus its within-line-shuffle mean. Real quire: 200 shuffles.
       Generator copies: 20 shuffles each, a declared reduction for run time.
  t6 = quire locality L_q = P(same | quire) / P(same | training book).
GENERATORS, fitted on the training quires' cores (p = training unigram; every
  generated core is drawn from p or copied; there are no unseen types):
  (i)   PER-LINE POOL: a Dirichlet-multinomial urn per line. Word j of a line
        is a fresh draw from p with probability a/(a+j), otherwise a copy of a
        uniform earlier word of the same line. a in closed form from the training
        within-line identity rate r: a = (1 - r)/(r - sum p^2) (1e6 if r <= sum p^2).
  (ii)  DRIFTING POOL: a recency-weighted urn carried across lines and pages
        within a quire. Each word is fresh from p with probability a/(a+W),
        otherwise it copies an earlier token of the quire with weight
        exp(-(line distance)/tau) (same line = distance 0). W = the total cache
        weight; tokens over 30 lines old are dropped. (a, tau) are chosen on the
        grid a in {1,3,10,30,100,300}, tau in {0.5,1,2,4,8} to minimise the
        squared relative error of training (within-line identity, adjacent-line
        share), simulated once on the training layout.
  (iii) COPY-RECENT IN LINE: with probability c a word copies the immediately
        previous word of its line, else it is fresh from p. REVISION 1 (after
        fixture run 1, before the freeze): the window was <= 3 previous words,
        which in 5-10-word lines could not be told apart from a per-line pool
        (the planted pool was matched by copy on 8/15 folds). It is now distance 1. c is chosen
        on the grid {0,.02,.05,.1,.15,.2,.3,.4} to match the training R_w(1).
  200 copies of each held-out quire's core layout.
MATCH: all 6 quantities inside the [0.5, 99.5] percentile envelope of the 200
  copies; NaN counts as inside.
CALL (written before running): a generator "matches" under a segmenter if it
  matches >= 8 of 15 folds. Report which generator(s) match under BOTH S1 and
  S2. If none, report for each generator the quantity most often outside its
  envelope ("which property each misses").
CONTROLS (ZL layout, ZL S1 training p):
  POSITIVE: a planted copy-recent text (c = 0.2): (iii) must match >= 8.
  NEGATIVE: a planted per-line-pool text (a = 2): (iii) must NOT match >= 8.
FIXTURE (synthetic layout, Zipf p over 2,000 types): the same two planted texts,
  same requirements.
PARALLEL: folds in a pool of up to 12 processes at below-normal priority.
MODES: python -I r10.py fixture OUTDIR | python -I r10.py real ZL OUT
"""
import sys, os, math, random, hashlib, datetime, collections, importlib.util
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
R7PATH = os.path.normpath(os.path.join(HERE, '..', 'r7', 'r7.py'))
_spec = importlib.util.spec_from_file_location('r7', R7PATH)
r7 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r7)

K = 100; NCOPY = 200; NSH_REAL = 200; NSH_COPY = 20; ENV = (0.5, 99.5); WORKERS = 12
A_GRID = [1, 3, 10, 30, 100, 300]; TAU_GRID = [0.5, 1, 2, 4, 8]; C_GRID = [0, .02, .05, .1, .15, .2, .3, .4]
TK = ('t1', 't2', 't3', 't4', 't5', 't6')


# ------------------------------------------------------------ quantities
def quantities(held, keep, book_psame, rng, nsh):
    """held: list of (page, [cores]) one quire in order. keep: core->class for K."""
    bypg = collections.OrderedDict()
    for pg, cs in held:
        bypg.setdefault(pg, []).append(cs)
    epg = {}
    for pg, ls in bypg.items():
        allc = collections.Counter(c for cs in ls for c in cs); N = sum(allc.values())
        epg[pg] = sum(v * (v - 1) for v in allc.values()) / (N * (N - 1)) if N > 1 else 0.0
    num = np.zeros(7); den = np.zeros(7)
    for pg, cs in held:
        m = len(cs)
        if m < 2 or epg[pg] == 0:
            continue
        for d in range(1, 7):
            if m > d:
                num[d] += sum(1 for i in range(m - d) if cs[i] == cs[i + d]); den[d] += (m - d) * epg[pg]
    R = [num[d] / den[d] if den[d] > 0 else np.nan for d in range(7)]
    xn = xd = 0.0
    for pg, ls in bypg.items():
        allc = collections.Counter(c for cs in ls for c in cs); N = sum(allc.values())
        if N < 2:
            continue
        e = sum(v * (v - 1) for v in allc.values()) / (N * (N - 1))
        for c1, c2 in zip(ls, ls[1:]):
            if c1 and c2:
                xn += c1[-1] == c2[0]; xd += e
    seqs = [[keep.get(c, K - 1) for c in cs] for _, cs in held]
    flat = np.array([x for s in seqs for x in s], dtype=np.int64)
    lid = np.array([i for i, s in enumerate(seqs) for _ in s])
    t5 = np.nan
    if len(flat) > 2:
        L = np.nonzero(lid[:-1] == lid[1:])[0]
        if len(L):
            obs = r7.mi_mm(flat[L] * K + flat[L + 1], K)
            bounds = []; st = 0
            for s in seqs:
                bounds.append((st, st + len(s))); st += len(s)
            nv = []
            for _ in range(nsh):
                perm = flat.copy()
                for a, b in bounds:
                    if b - a > 1:
                        perm[a:b] = rng.permutation(perm[a:b])
                nv.append(r7.mi_mm(perm[L] * K + perm[L + 1], K))
            t5 = obs - float(np.mean(nv))
    allq = collections.Counter(c for _, cs in held for c in cs); n = sum(allq.values())
    t6 = (sum(v * (v - 1) for v in allq.values()) / (n * (n - 1))) / book_psame if n > 1 else np.nan
    return {'t1': R[1], 't2': R[2], 't3': float(np.nanmean(R[3:7])) if any(not np.isnan(x) for x in R[3:7]) else np.nan,
            't4': xn / xd if xd else np.nan, 't5': t5, 't6': t6}


# ------------------------------------------------------------ generators
class Lex:
    def __init__(self, cnt):
        self.types = [c for c, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]
        w = np.array([cnt[c] for c in self.types], dtype=float); self.p = w / w.sum()
        self.cum = np.cumsum(self.p); self.s2 = float((self.p ** 2).sum())

    def draw(self, rng, n=1):
        idx = np.searchsorted(self.cum, rng.random(n) * self.cum[-1])
        return [self.types[min(i, len(self.types) - 1)] for i in idx]


def gen(kind, lex, layout, rng, par):
    """layout: list of (quire, page, m) in order -> list of (quire, page, [cores])."""
    out = []; cache = []; lastq = None; li = 0
    for q, pg, m in layout:
        if q != lastq:
            cache = []; lastq = q; li = 0
        li += 1
        fresh = lex.draw(rng, m) if m else []
        u = rng.random(m) if m else []
        line = []
        for j in range(m):
            if kind == 'pool':
                a = par['a']
                if j == 0 or u[j] < a / (a + j):
                    c = fresh[j]
                else:
                    c = line[int(rng.integers(j))]
            elif kind == 'drift':
                a, tau = par['a'], par['tau']
                groups = [(l0, toks) for l0, toks in cache] + [(li, line)]
                ws = [len(toks) * math.exp(-(li - l0) / tau) for l0, toks in groups]
                W = sum(ws)
                if W == 0 or u[j] < a / (a + W):
                    c = fresh[j]
                else:
                    x = rng.random() * W; k = 0
                    while k < len(ws) - 1 and x > ws[k]:
                        x -= ws[k]; k += 1
                    toks = groups[k][1]; c = toks[int(rng.integers(len(toks)))]
            else:
                if j > 0 and u[j] < par['c']:
                    c = line[j - 1]
                else:
                    c = fresh[j]
            line.append(c)
        if kind == 'drift':
            cache.append((li, line)); cache = [(l0, t) for l0, t in cache if li - l0 <= 30 and t]
        out.append((q, pg, line))
    return out


def train_stats(lines):
    num = den = 0.0; xn = xd = 0.0; r1n = r1d = 0.0; prev = None
    pgc = collections.defaultdict(collections.Counter)
    for q, pg, cs in lines:
        pgc[(q, pg)].update(cs)
    epg = {}
    for k, c in pgc.items():
        N = sum(c.values()); epg[k] = sum(v * (v - 1) for v in c.values()) / (N * (N - 1)) if N > 1 else 0.0
    for q, pg, cs in lines:
        m = len(cs)
        if m >= 2:
            c = collections.Counter(cs)
            num += sum(v * (v - 1) for v in c.values()); den += m * (m - 1)
            r1n += sum(1 for x, y in zip(cs, cs[1:]) if x == y); r1d += (m - 1) * epg[(q, pg)]
        if prev is not None and prev[0] == q and m and prev[1]:
            c1 = collections.Counter(prev[1]); c2 = collections.Counter(cs)
            xn += sum(c1[k] * c2[k] for k in c1); xd += len(prev[1]) * m
        prev = (q, cs)
    return {'rw': num / den if den else 0.0, 'rx': xn / xd if xd else 0.0, 'R1': r1n / r1d if r1d else 1.0}


def fit_all(train, lex):
    st = train_stats(train)
    a_pool = (1 - st['rw']) / (st['rw'] - lex.s2) if st['rw'] > lex.s2 else 1e6
    lay = [(q, pg, len(cs)) for q, pg, cs in train]
    best = None
    for a in A_GRID:
        for tau in TAU_GRID:
            s2 = train_stats(gen('drift', lex, lay, np.random.default_rng(10001), {'a': a, 'tau': tau}))
            err = ((s2['rw'] - st['rw']) / st['rw']) ** 2 + ((s2['rx'] - st['rx']) / max(st['rx'], 1e-9)) ** 2
            if best is None or err < best[0]:
                best = (err, a, tau)
    bc = None
    for c in C_GRID:
        s3 = train_stats(gen('copy', lex, lay, np.random.default_rng(10002), {'c': c}))
        err = (s3['R1'] - st['R1']) ** 2
        if bc is None or err < bc[0]:
            bc = (err, c)
    return {'pool': {'a': a_pool}, 'drift': {'a': best[1], 'tau': best[2]}, 'copy': {'c': bc[1]}}


def fold_job(args):
    r7.below_normal()
    fi, q, lines = args
    train = [x for x in lines if x[0] != q]; held = [x for x in lines if x[0] == q]
    cnt = collections.Counter(c for _, _, cs in train for c in cs)
    lex = Lex(cnt)
    keep = {c: i for i, c in enumerate(lex.types[:K - 1])}
    Cb = np.array(list(cnt.values()), dtype=float); Nb = Cb.sum(); book = float((Cb * (Cb - 1)).sum() / (Nb * (Nb - 1)))
    rng = np.random.default_rng(10100 + fi)
    real = quantities([(pg, cs) for _, pg, cs in held], keep, book, rng, NSH_REAL)
    pars = fit_all(train, lex)
    lay = [(a, b, len(c)) for a, b, c in held]
    ok = {}; miss = {}
    for gi, kind in enumerate(('pool', 'drift', 'copy')):
        grng = np.random.default_rng(10200 + 10 * fi + gi)
        sims = [quantities([(pg, cs) for _, pg, cs in gen(kind, lex, lay, grng, pars[kind])], keep, book, grng, NSH_COPY) for _ in range(NCOPY)]
        inside = True; miss[kind] = []
        for k in TK:
            v = np.array([s[k] for s in sims], dtype=float); v = v[~np.isnan(v)]; o = real[k]
            if np.isnan(o) or len(v) == 0:
                continue
            lo, hi = np.percentile(v, ENV)
            if not (lo <= o <= hi):
                inside = False; miss[kind].append(k)
        ok[kind] = inside
    return q, ok, miss, real, pars


def fold_test(name, lines, out):
    P = out.append
    qn = collections.Counter(q for q, _, _ in lines)
    folds = sorted(q for q, n in qn.items() if n >= 50)
    need = math.ceil(8 / 15 * len(folds))
    P('  %s: %d folds, threshold %d' % (name, len(folds), need))
    P('   fold | fitted pool a ; drift a/tau ; copy c | match (i) pool (ii) drift (iii) copy | real t1..t6 | misses')
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        res = list(ex.map(fold_job, [(fi, q, lines) for fi, q in enumerate(folds)]))
    wins = collections.Counter(); misscnt = {k: collections.Counter() for k in ('pool', 'drift', 'copy')}
    for q, ok, miss, real, pars in res:
        for k in ok:
            wins[k] += ok[k]
            for t in miss[k]:
                misscnt[k][t] += 1
        P('   %-4s | %.2f ; %g/%g ; %.2f | %-5s %-5s %-5s | %s | pool:%s drift:%s copy:%s' % (
            q, pars['pool']['a'], pars['drift']['a'], pars['drift']['tau'], pars['copy']['c'], ok['pool'], ok['drift'], ok['copy'],
            ' '.join('%.3f' % real[k] for k in TK), ','.join(miss['pool']) or '-', ','.join(miss['drift']) or '-', ','.join(miss['copy']) or '-'))
    matches = {k: wins[k] >= need for k in ('pool', 'drift', 'copy')}
    P('   folds matched: (i) pool %d, (ii) drift %d, (iii) copy %d (threshold %d)' % (wins['pool'], wins['drift'], wins['copy'], need))
    for k in ('pool', 'drift', 'copy'):
        P('   %s most-missed quantities: %s' % (k, ', '.join('%s %d' % kv for kv in misscnt[k].most_common(3)) or 'none'))
    print('\n'.join(out[-5:]), flush=True)
    return matches, wins, misscnt


def planted_cores(layout, lex, kind, seed):
    par = {'copy': {'c': 0.2}, 'pool': {'a': 2.0}}[kind]
    return gen(kind, lex, layout, np.random.default_rng(seed), par)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    r7.below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r10.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r10.py sha256: %s' % sha(me), 'r7.py (local import) sha256: %s' % sha(R7PATH)]
    P = out.append; res = {}
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = [('Q%02d' % (i * 15 // 207), i, r.randint(5, 10)) for i in range(207) for _ in range(20)]
        lex = Lex(collections.Counter({('c%04d' % i): 1.0 / (i + 1) * 1e6 for i in range(2000)}))
        for nm, kind, seed in (('FIX_PLANTED_COPY', 'copy', 10301), ('FIX_PLANTED_POOL', 'pool', 10302)):
            P('== %s' % nm)
            res[nm] = fold_test(nm, planted_cores(layout, lex, kind, seed), out); P('')
        ok = res['FIX_PLANTED_COPY'][0]['copy'] and not res['FIX_PLANTED_POOL'][0]['copy']
        P('FIXTURE CHECK: planted copy -> (iii) matches: %s ; planted pool -> (iii) not matching: %s ; overall %s' % (
            res['FIX_PLANTED_COPY'][0]['copy'], not res['FIX_PLANTED_POOL'][0]['copy'], 'OK' if ok else 'NOT OK'))
        rpath = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, rpath = sys.argv[2:4]
        try:
            reg = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(HERE, 'r10.prereg.sha256'), encoding='ascii').read().splitlines()
                       if l.strip() and not l.startswith('#'))
        except OSError:
            reg = {}
        P('prereg r10.py %s ; stub match: %s ; r7.py entry match: %s' % (
            reg.get('r10.py', 'MISSING'), 'YES' if reg.get('r10.py') == sha(me) else 'NO', 'YES' if reg.get('../r7/r7.py') == sha(R7PATH) else 'NO'))
        P('data %s %s' % (zl, sha(zl)))
        zlines = r7.parse_ivtff(zl)
        P2, S2, dl = r7.mdl_affixes([w for _, _, l in zlines for w in l])
        P('S2 MDL affixes on ZL: %s ; %s' % (P2, S2))
        segs = {'S1': r7.seg_lists(r7.PREFIXES, r7.SUFFIXES), 'S2': r7.seg_lists(P2, S2, need_core=True)}
        for sg in ('S1', 'S2'):
            P('== VOYNICH_ZL %s' % sg)
            res[('ZL', sg)] = fold_test('VOYNICH_ZL ' + sg, r7.build(zlines, segs[sg]), out); P('')
        s1 = r7.build(zlines, segs['S1'])
        lex = Lex(collections.Counter(c for _, _, cs in s1 for c in cs))
        layout = [(q, pg, len(cs)) for q, pg, cs in s1]
        for nm, kind, seed in (('PLANTED_COPY', 'copy', 10401), ('PLANTED_POOL', 'pool', 10402)):
            P('== %s' % nm)
            res[nm] = fold_test(nm, planted_cores(layout, lex, kind, seed), out); P('')
        P('CALLS')
        both = [k for k in ('pool', 'drift', 'copy') if res[('ZL', 'S1')][0][k] and res[('ZL', 'S2')][0][k]]
        for sg in ('S1', 'S2'):
            w = res[('ZL', sg)][1]
            P('ZL %s: folds matched (i) pool %d, (ii) drift %d, (iii) copy %d' % (sg, w['pool'], w['drift'], w['copy']))
        P('Generator(s) matching >= 8/15 under BOTH S1 and S2: %s' % (', '.join(both) if both else 'NONE'))
        if not both:
            for k in ('pool', 'drift', 'copy'):
                P('  %s misses: S1 %s ; S2 %s' % (k, dict(res[('ZL', 'S1')][2][k].most_common(3)), dict(res[('ZL', 'S2')][2][k].most_common(3))))
        pos = res['PLANTED_COPY'][0]['copy']; neg = not res['PLANTED_POOL'][0]['copy']
        P('Controls: positive (planted copy) (iii) matches required: %s ; negative (planted pool) (iii) not matching required: %s' % (pos, neg))
        P('VERDICT: %s%s' % ('matching under both segmenters: ' + ', '.join(both) if both else 'NO generator matches under both segmenters',
                              '' if pos and neg else ' ; CONTROLS MISBEHAVED'))
    open(rpath, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-10:]))


if __name__ == '__main__':
    main()
