"""r13.py -- blind power audit of two exclusions (F-23 copy-and-vary, F-30 table-and-grille). voynich-91, Roach.

Brief: SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R13-20261018T224411Z. Built from published descriptions only.
Local imports: ../r10/r10.py (frozen: quantities t1-t6) and, through it, ../r7/r7.py. Own code only.

UNIT: whole words (EVA, r3 cleaning) of ZL3b paragraph loci, in reading order;
  real pages, lines and quires. LOQO over the 15 quires with >= 50 lines.
PRODUCERS (fitted on training quires; generation restarts at each quire):
  (A) COPY-AND-VARY: each word, with probability q, copies a uniform word among
      the previous W = 10 words of the quire (reading order). With probability e
      the copy then gets one edit (substitution, insertion or deletion, uniform
      op and position; glyph from the training glyph distribution). Otherwise
      the word is a fresh draw from the training word unigram.
      (q, e) chosen on the grid q {0,.1,.2,.3,.45,.6} x e {0,.33,.67,1}
      minimising squared error of training (rep, near):
        rep  = share of tokens identical to one of the previous 10 words;
        near = share of tokens at edit distance exactly 1 from one of them (and not identical).
  (B) TABLE-AND-GRILLE (Rugg-style): a table of R rows x 3 columns, cells drawn
      from the training S1 prefix / core / suffix distributions (seed per fit).
      A grille with column row-offsets (0, d2, d3), d2 and d3 uniform in 1..R-1,
      is placed at a random row at each line start. Each word reads
      T[r][0] + T[r+d2][1] + T[r+d3][2] (mod R); the grille then advances 1-3
      rows (uniform). R chosen on the grid {8,16,32,64,128,256} minimising squared
      relative error of the training (type/token ratio per quire, rep).
QUANTITIES per held-out quire (8): r10 t1 R_w(1), t2 R_w(2), t3 R_w(3..6) (vs
  page expectation), t4 cross-line, t5 order at K=100 (real 200 / copies 20
  shuffles), t6 quire locality; plus t7 type/token ratio of the quire and t8 mean word length.
MATCH: all 8 inside the [0.5, 99.5] percentile envelope of 200 copies of the
  producer refitted on the training quires of the text under test.
TESTS per producer X in {A, B}:
  PLANTED: fit X on ALL of ZL, generate one planted manuscript on the ZL layout
    (seed 13101 / 13102), then run the LOQO match test of X on it. This is the
    POSITIVE control and the power measurement.
  REAL: the LOQO match test of X on the real ZL text.
  CROSS (negative control): X's match test on the OTHER producer's planted
    manuscript. It should be <= 4/15; otherwise "envelope not discriminating" is reported.
CALL (from the brief, written before running), per producer:
  POWERED if planted >= 10/15; WEAK 5-9; UNINFORMATIVE <= 4.
  The real result is reported separately. A real 0/15 counts as an EXCLUSION
  only when planted is POWERED.
ORACLE self-test (REVISION 1, after fixture run 1, before the freeze): copies are
  generated with the TRUE planted parameters (A: the true q, e AND the true
  generating lexicon and glyph distribution; B: the true R and the very same
  table and grille offsets). REVISION 2: the A oracle at first drew from a
  lexicon refitted on the planted text, which is not an oracle; it now uses the
  true Fit object. (The first rev-2 run crashed before any result because the
  Fit object cannot be pickled to the workers. The same design is implemented by
  passing the generating lines and rebuilding Fit in each worker; this is
  disclosed as part of revision 2.) This is reported next to the refitted
  planted test. Fixture run 1 showed that a refitted table-and-grille cannot
  recover the latent table alignment or the offsets (planted B 0/15, all folds
  missing t5 order), which is the question under test. So the fixture now checks
  the machinery with ORACLE copies, and the refitted planted test stays the
  measurement the call uses.
FIXTURE: a synthetic layout and Zipf lexicon of codeword words, with producers
  run at hand-set parameters (A: q 0.3, e 0.5; B: R 32) to make the planted
  texts. Fixture check: both ORACLE self-tests >= 10/15; refitted self-tests reported.
PARALLEL: folds in a pool of up to 12 processes at below-normal priority.
MODES: python -I r13.py fixture OUTDIR | python -I r13.py real ZL OUT
"""
import sys, os, math, random, hashlib, datetime, collections, importlib.util
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
R10PATH = os.path.normpath(os.path.join(HERE, '..', 'r10', 'r10.py'))
_spec = importlib.util.spec_from_file_location('r10', R10PATH)
r10 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r10)
r7 = r10.r7
K = 100; NCOPY = 200; ENV = (0.5, 99.5); WORKERS = 12; W = 10
QGRID = [0, .1, .2, .3, .45, .6]; EGRID = [0, .33, .67, 1.0]; RGRID = [8, 16, 32, 64, 128, 256]
TK = ('t1', 't2', 't3', 't4', 't5', 't6', 't7', 't8')
SEG1 = r7.seg_lists(r7.PREFIXES, r7.SUFFIXES)


def ed1(a, b):
    """True if edit distance(a, b) == 1."""
    la, lb = len(a), len(b)
    if abs(la - lb) > 1 or a == b:
        return False
    if la == lb:
        return sum(1 for x, y in zip(a, b) if x != y) == 1
    if la > lb:
        a, b = b, a; la, lb = lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def stats_train(lines):
    rep = near = n = 0; tt = []
    lastq = None; buf = []
    perq = collections.defaultdict(list)
    for q, pg, ws in lines:
        if q != lastq:
            buf = []; lastq = q
        for w in ws:
            perq[q].append(w)
            if buf:
                if w in buf:
                    rep += 1
                elif any(ed1(w, b) for b in buf):
                    near += 1
            n += 1; buf.append(w); buf = buf[-W:]
    ttr = float(np.mean([len(set(v)) / len(v) for v in perq.values() if v]))
    return {'rep': rep / n if n else 0, 'near': near / n if n else 0, 'ttr': ttr}


class Fit:
    def __init__(self, lines):
        cnt = collections.Counter(w for _, _, ws in lines for w in ws)
        self.lex = r10.Lex(cnt)
        g = collections.Counter(c for w, n in cnt.items() for c in w for _ in range(n))
        self.glyphs = list(g); gw = np.array([g[c] for c in self.glyphs], float); self.gcum = np.cumsum(gw / gw.sum())
        self.parts = [collections.Counter(), collections.Counter(), collections.Counter()]
        for w, n in cnt.items():
            p = SEG1(w)
            for i in range(3):
                self.parts[i][p[i]] += n
        self.pl = []
        for c in self.parts:
            ks = list(c); ww = np.array([c[k] for k in ks], float); self.pl.append((ks, np.cumsum(ww / ww.sum())))

    def glyph(self, rng):
        return self.glyphs[min(int(np.searchsorted(self.gcum, rng.random())), len(self.glyphs) - 1)]

    def part(self, i, rng):
        ks, cum = self.pl[i]; return ks[min(int(np.searchsorted(cum, rng.random())), len(ks) - 1)]


def gen_A(fit, layout, rng, q, e):
    out = []; lastq = None; buf = []
    for qq, pg, n in layout:
        if qq != lastq:
            buf = []; lastq = qq
        fresh = fit.lex.draw(rng, n) if n else []
        line = []
        for j in range(n):
            if buf and rng.random() < q:
                w = buf[int(rng.integers(len(buf)))]
                if rng.random() < e:
                    op = int(rng.integers(3)); L = len(w)
                    if op == 0 and L:
                        i = int(rng.integers(L)); w = w[:i] + fit.glyph(rng) + w[i + 1:]
                    elif op == 1:
                        i = int(rng.integers(L + 1)); w = w[:i] + fit.glyph(rng) + w[i:]
                    elif L > 1:
                        i = int(rng.integers(L)); w = w[:i] + w[i + 1:]
            else:
                w = fresh[j]
            line.append(w); buf.append(w); buf = buf[-W:]
        out.append((qq, pg, line))
    return out


def make_table(fit, R, rng):
    return [[fit.part(i, rng) for i in range(3)] for _ in range(R)]


def gen_B(fit, layout, rng, R, table=None, offs=None):
    if table is None:
        table = make_table(fit, R, rng)
    if offs is None:
        offs = (int(rng.integers(1, R)), int(rng.integers(1, R)))
    out = []
    for qq, pg, n in layout:
        r = int(rng.integers(R)); line = []
        for _ in range(n):
            w = table[r][0] + table[(r + offs[0]) % R][1] + table[(r + offs[1]) % R][2]
            line.append(w if w else 'o')
            r = (r + int(rng.integers(1, 4))) % R
        out.append((qq, pg, line))
    return out


def fit_params(kind, fit, train):
    st = stats_train(train); lay = [(q, pg, len(ws)) for q, pg, ws in train]
    best = None
    if kind == 'A':
        for q in QGRID:
            for e in EGRID:
                s = stats_train(gen_A(fit, lay, np.random.default_rng(13001), q, e))
                err = (s['rep'] - st['rep']) ** 2 + (s['near'] - st['near']) ** 2
                if best is None or err < best[0]:
                    best = (err, {'q': q, 'e': e})
    else:
        for R in RGRID:
            s = stats_train(gen_B(fit, lay, np.random.default_rng(13002), R))
            err = ((s['ttr'] - st['ttr']) / st['ttr']) ** 2 + ((s['rep'] - st['rep']) / max(st['rep'], 1e-6)) ** 2
            if best is None or err < best[0]:
                best = (err, {'R': R})
    return best[1]


def generate(kind, fit, layout, rng, par):
    if kind == 'A':
        return gen_A(fit, layout, rng, par['q'], par['e'])
    return gen_B(fit, layout, rng, par['R'], par.get('table'), par.get('offs'))


def quants(held, keep, book, rng, nsh):
    d = r10.quantities([(pg, ws) for _, pg, ws in held], keep, book, rng, nsh)
    toks = [w for _, _, ws in held for w in ws]
    d['t7'] = len(set(toks)) / len(toks) if toks else np.nan
    d['t8'] = float(np.mean([len(w) for w in toks])) if toks else np.nan
    return d


def fold_job(args):
    r7.below_normal()
    fi, q, lines, kind, seed, oracle = args
    train = [x for x in lines if x[0] != q]; held = [x for x in lines if x[0] == q]
    fit = Fit(train); par = oracle if oracle is not None else fit_params(kind, fit, train)
    gfit = Fit(oracle['fit_lines']) if (oracle is not None and 'fit_lines' in oracle) else fit
    cnt = collections.Counter(w for _, _, ws in train for w in ws)
    keep = {w: i for i, w in enumerate(fit.lex.types[:K - 1])}
    Cb = np.array(list(cnt.values()), float); Nb = Cb.sum(); book = float((Cb * (Cb - 1)).sum() / (Nb * (Nb - 1)))
    rng = np.random.default_rng(seed + fi)
    real = quants(held, keep, book, rng, 200)
    lay = [(a, b, len(c)) for a, b, c in held]
    sims = [quants(generate(kind, gfit, lay, rng, par), keep, book, rng, 20) for _ in range(NCOPY)]
    miss = []
    for k in TK:
        v = np.array([s[k] for s in sims], float); v = v[~np.isnan(v)]; o = real[k]
        if np.isnan(o) or len(v) == 0:
            continue
        lo, hi = np.percentile(v, ENV)
        if not (lo <= o <= hi):
            miss.append(k)
    return q, not miss, miss, par, real


def match_test(name, lines, kind, seed, out, oracle=None):
    qn = collections.Counter(q for q, _, _ in lines)
    folds = sorted(q for q, n in qn.items() if n >= 50)
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        res = list(ex.map(fold_job, [(fi, q, lines, kind, seed, oracle) for fi, q in enumerate(folds)]))
    n = sum(r[1] for r in res); mc = collections.Counter(m for r in res for m in r[2])
    out.append('  %s (producer %s): folds matched %d of %d ; most-missed %s' % (name, kind, n, len(folds), dict(mc.most_common(4))))
    for q, ok, miss, par, real in res:
        pshow = {k: v for k, v in par.items() if k not in ('table', 'fit_lines')}
        out.append('     %-4s %-5s params %s misses %s | %s' % (q, ok, pshow, ','.join(miss) or '-', ' '.join('%.3f' % real[k] for k in TK)))
    print(out[-len(res) - 1], flush=True)
    return n, len(folds)


def band(n):
    return 'POWERED' if n >= 10 else ('WEAK' if n >= 5 else 'UNINFORMATIVE')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    r7.below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r13.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r13.py sha256: %s' % sha(me), 'r10.py sha256: %s' % sha(R10PATH), 'r7.py sha256: %s' % sha(r10.R7PATH)]
    P = out.append
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = [('Q%02d' % (i * 15 // 207), 'f%03d' % i, r.randint(5, 10)) for i in range(207) for _ in range(20)]
        cw = r7.codewords()
        pre = r7.PREFIXES + ['']; suf = r7.SUFFIXES + ['']
        rr = random.Random(5)
        vocab = [rr.choice(pre) + cw[i % len(cw)] + rr.choice(suf) for i in range(3000)]
        base = [(q, pg, [vocab[min(int(rr.paretovariate(1.0)) - 1, 2999)] for _ in range(n)]) for q, pg, n in layout]
        fit = Fit(base)
        pa = gen_A(fit, layout, np.random.default_rng(13101), 0.3, 0.5)
        rngb = np.random.default_rng(13102); tb = make_table(fit, 32, rngb); ob = (int(rngb.integers(1, 32)), int(rngb.integers(1, 32)))
        pb = gen_B(fit, layout, rngb, 32, tb, ob)
        a = match_test('FIX_PLANTED_A refit', pa, 'A', 13201, out)[0]
        b = match_test('FIX_PLANTED_B refit', pb, 'B', 13202, out)[0]
        ao = match_test('FIX_PLANTED_A ORACLE', pa, 'A', 13203, out, {'q': 0.3, 'e': 0.5, 'fit_lines': base})[0]
        bo = match_test('FIX_PLANTED_B ORACLE', pb, 'B', 13204, out, {'R': 32, 'table': tb, 'offs': ob})[0]
        P('FIXTURE CHECK (ORACLE): A %d, B %d (>=10 required) -> %s ; refitted (info): A %d, B %d' % (ao, bo, 'OK' if ao >= 10 and bo >= 10 else 'NOT OK', a, b))
        rpath = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, rpath = sys.argv[2:4]
        try:
            reg = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(HERE, 'r13.prereg.sha256'), encoding='ascii').read().splitlines()
                       if l.strip() and not l.startswith('#'))
        except OSError:
            reg = {}
        P('prereg r13.py %s ; stub match: %s ; r10 entry %s ; r7 entry %s' % (reg.get('r13.py', 'MISSING'), 'YES' if reg.get('r13.py') == sha(me) else 'NO',
                                                                            'YES' if reg.get('../r10/r10.py') == sha(R10PATH) else 'NO', 'YES' if reg.get('../r7/r7.py') == sha(r10.R7PATH) else 'NO'))
        P('data %s %s' % (zl, sha(zl)))
        lines = r7.parse_ivtff(zl)
        layout = [(q, pg, len(ws)) for q, pg, ws in lines]
        fitall = Fit(lines)
        parA = fit_params('A', fitall, lines); parB = fit_params('B', fitall, lines)
        P('Producer parameters fitted on all of ZL: A %s ; B %s' % (parA, parB))
        plA = gen_A(fitall, layout, np.random.default_rng(13101), parA['q'], parA['e'])
        rngb = np.random.default_rng(13102); tB = make_table(fitall, parB['R'], rngb); oB = (int(rngb.integers(1, parB['R'])), int(rngb.integers(1, parB['R'])))
        plB = gen_B(fitall, layout, rngb, parB['R'], tB, oB)
        res = {}
        res['A_planted'] = match_test('PLANTED_A', plA, 'A', 13201, out)
        res['A_real'] = match_test('REAL_ZL', lines, 'A', 13211, out)
        res['A_cross'] = match_test('CROSS_A_on_plantedB', plB, 'A', 13221, out)
        res['B_planted'] = match_test('PLANTED_B', plB, 'B', 13202, out)
        res['B_real'] = match_test('REAL_ZL', lines, 'B', 13212, out)
        res['B_cross'] = match_test('CROSS_B_on_plantedA', plA, 'B', 13222, out)
        res['A_oracle'] = match_test('PLANTED_A ORACLE', plA, 'A', 13203, out, dict(parA, fit_lines=lines))
        res['B_oracle'] = match_test('PLANTED_B ORACLE', plB, 'B', 13204, out, {'R': parB['R'], 'table': tB, 'offs': oB})
        P('')
        P('CALLS')
        for X, nm in (('A', 'copy-and-vary'), ('B', 'table-and-grille')):
            pn = res[X + '_planted'][0]; rn = res[X + '_real'][0]; cn = res[X + '_cross'][0]
            P('Producer %s (%s): planted (refitted) %d/15 -> %s ; planted ORACLE %d/15 ; real %d/15%s ; cross (negative control) %d/15%s' % (
                X, nm, pn, band(pn), res[X + '_oracle'][0], rn, ' -> EXCLUSION' if (rn == 0 and pn >= 10) else (' (0/15 but not an exclusion: test not POWERED)' if rn == 0 else ''),
                cn, '' if cn <= 4 else ' -> envelope not discriminating'))
        P('VERDICT: A %s, B %s' % (band(res['A_planted'][0]), band(res['B_planted'][0])))
    open(rpath, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-8:]))


if __name__ == '__main__':
    main()
