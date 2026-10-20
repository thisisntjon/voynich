"""r9.py -- regional affix drift (voynich-91, Roach; blind). Tests my own r6 reading.

Queue message SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-QUEUE-20261018T202417Z, item r9.
Own code only (r6 lineage: loaders, S1 segmenter, profile). No Skynet code.

DATA: ZL3b-n (primary), IT2a-n (second), paragraph loci, r3 cleaning. S1 affixes
  (r3 lists + empty). Streams: prefix, suffix. LOQO over the 15 quires with
  >= 50 lines. Reading order = file order; lines carry their page id.
PROFILE per stream, computed on line positions >= 2 (14 quantities in all):
  r6 quantities q1 R_w(1), q2 R_w(1)-R_w(3), q3 C (within-line vs page),
    q4 X (adjacent-line sharing vs page), exactly as in r6.
  DECAY: for lines A, B: share(A,B) = sum_a cA(a) cB(a) / (mA mB).
    S(D)   = pooled share over same-page line pairs D lines apart / quire P(same),
             where quire P(same) = sum C(C-1) / (N(N-1)) over the quire.
    q5 = S(1);  q6 = mean of S(2), S(3), S(4);
    q7 = SX(1) = the same, for the pair (last line of a page, first line of the
         next page) within the quire.
DECISION STATISTIC (whole text): exact permutation p from 200 shuffles. q1,q2:
  within-line. q3,q4: within-page. q5-q7: within-quire shuffles of positions >= 2
  across lines (layout kept). p_up = (1 + #{null >= obs}) / 201.
GENERATORS, fitted on training quires per stream. Line-initial affix from the
  training line-initial distribution; positions >= 2:
  (i)   DRIFT: theta_0 ~ Dir(beta p); theta_n = (1-lam) theta_n-1 + lam g_n,
        g_n ~ Dir(beta p). Carried across lines and pages through the quire;
        words iid from theta_n. (lam, beta) chosen on a grid
        lam in {0.05,0.1,0.2,0.3,0.5,0.7,1.0}, beta in {1,2,5,10,20,50,200}
        to minimise the squared relative error of training (r_w, r_x, r_x3):
        r_w = within-line identity rate, r_x = adjacent-line share,
        r_x3 = share between lines 3 apart (same quire), all / sum p^2.
        REVISION 1 (after fixture run 1, before the freeze): r_x3 was added
        because (r_w, r_x) alone gave a fitted scale of 10 on a planted scale of 5.
        each simulated once on the training layout (seed 9001).
        DRIFT SCALE = 1/lam lines.
  (ii)  LINE-HELD: Dirichlet(alpha p) per line, alpha in closed form as in r6.
  (iii) PER-WORD: iid from p.
  (iv)  FIRST-ORDER CHAIN: P(a_i | a_i-1), add-0.5, restarting each line from the initial distribution (r6).
  200 copies of each held-out quire on its exact layout.
MATCH: all 14 quantities (q1-q7 x prefix, suffix) inside the [0.5, 99.5]
  percentile envelope of the 200 copies; NaN counts as inside.
CALL (ZL): PASS iff (i) matches >= 8 of 15 folds AND (i)'s match count is
  strictly greater than each of (ii), (iii) and (iv). Report the median fitted
  drift scale over folds. VERDICT follows the call.
CONTROLS (real run, ZL layout, ZL-fitted p and initial distribution):
  POSITIVE: planted DRIFT text (lam = 0.2, beta = 10, i.e. scale 5 lines) must give PASS;
    the median fitted scale is reported (planted 5).
  NEGATIVE: planted LINE-HELD text (alpha = 3) must NOT give PASS.
  Latin prose (Caesar, r3 frequency affixes, 30-line pages, 15 pseudo-quires) is reported as a reference.
FIXTURE (synthetic layout and Zipf p): planted drift -> PASS; planted line-held -> not PASS.
PARALLEL: folds run in a pool of up to 12 processes at below-normal priority.
MODES: python -I r9.py fixture OUTDIR | python -I r9.py real ZL IT LAT OUT
"""
import sys, os, re, math, random, hashlib, datetime, unicodedata, collections
import numpy as np
from concurrent.futures import ProcessPoolExecutor

PREFIXES = ['qo', 'q', 'o', 'y', 'd', 's', 'l', 'r', 'ch', 'sh']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eey', 'ey', 'y', 'ol', 'al', 'or', 'ar',
            'am', 'm', 'g', 'l', 'r', 's']
NCOPY = 200; NSHUF = 200; ENV = (0.5, 99.5); WORKERS = 12
LAMS = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]; BETAS = [1, 2, 5, 10, 20, 50, 200]
QK = ('q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7')


def below_normal():
    try:
        import ctypes
        k = ctypes.windll.kernel32; k.SetPriorityClass(k.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def clean_ivtff_text(t):
    t = re.sub(r'<![^>]*>', '', t); t = re.sub(r'<[%$]>', '', t); t = re.sub(r'<@[^>]*>', '', t)
    t = re.sub(r'<[-~]>', '.', t); t = re.sub(r'<[^>]*>', '', t)
    t = re.sub(r'\[([^:\]]*)(?::[^\]]*)?\]', r'\1', t)
    t = t.replace('{', '').replace('}', '').replace("'", '')
    t = re.sub(r'@(\d+);', lambda m: chr(0xE000 + int(m.group(1))), t)
    t = t.replace(',', '.')
    out = []
    for w in t.split('.'):
        w2 = ''.join(ch for ch in w if ('a' <= ch <= 'z') or ch in '?I' or 0xE000 <= ord(ch) <= 0xE3FF)
        if w2:
            out.append(w2)
    return out


def parse_ivtff(path):
    hdr = re.compile(r'^<(f[0-9A-Za-z]+)>\s*(.*)$')
    loc = re.compile(r'^<(f[0-9A-Za-z]+)\.(\w+),(.)(\w)[^>]*>\s?(.*)$')
    pages = collections.OrderedDict(); quire = {}
    for raw in open(path, encoding='utf-8', errors='replace'):
        s = raw.rstrip('\r\n')
        if not s or s.startswith('#'):
            continue
        m = loc.match(s)
        if m:
            if m.group(4) == 'P':
                w = clean_ivtff_text(m.group(5))
                if w:
                    pages.setdefault(m.group(1), []).append(w)
            continue
        m = hdr.match(s)
        if m:
            quire[m.group(1)] = dict(re.findall(r'\$(\w)=(\w+)', m.group(2))).get('Q', '?')
    return [(quire.get(pg, '?'), pi, l) for pi, (pg, ls) in enumerate(pages.items()) for l in ls]


def make_seg(prefixes, suffixes):
    P = sorted(prefixes, key=len, reverse=True); S = sorted(suffixes, key=len, reverse=True)

    def seg(w):
        p = next((x for x in P if w.startswith(x)), '')
        rest = w[len(p):]
        s = next((x for x in S if rest.endswith(x) and len(x) <= len(rest)), '')
        return p, rest[:len(rest) - len(s)], s
    return seg


def latin_lines(path):
    txt = open(path, encoding='utf-8').read().splitlines()
    i0 = next(i for i, l in enumerate(txt) if l.startswith('*** START'))
    i1 = next(i for i, l in enumerate(txt) if l.startswith('*** END'))
    lines = []
    for l in txt[i0 + 1:i1]:
        t = unicodedata.normalize('NFD', l)
        t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
        w = ''.join(c if unicodedata.category(c).startswith('L') else ' ' for c in t).split()
        if w:
            lines.append(w)
    npg = (len(lines) + 29) // 30
    return [('Q%02d' % ((i // 30) * 15 // npg), i // 30, l) for i, l in enumerate(lines)]


def freq_affixes(words):
    ini, fin = collections.Counter(), collections.Counter()
    for w in words:
        if len(w) >= 2:
            ini[w[:2]] += 1
        for k in range(1, min(4, len(w) - 1) + 1):
            fin[w[-k:]] += 1
    return ([x for x, _ in sorted(ini.items(), key=lambda kv: (-kv[1], kv[0]))[:10]],
            [x for x, _ in sorted(fin.items(), key=lambda kv: (-kv[1], kv[0]))[:20]])


def streams_of(lines, seg, PA, SA):
    pi = {a: i for i, a in enumerate(PA)}; si = {a: i for i, a in enumerate(SA)}
    pre = [(q, pg, [pi[seg(w)[0]] for w in l]) for q, pg, l in lines]
    suf = [(q, pg, [si[seg(w)[2]] for w in l]) for q, pg, l in lines]
    return {'prefix': (pre, len(PA)), 'suffix': (suf, len(SA))}


# ------------------------------------------------------------ profile
def profile(lines, A):
    """lines: list of (page, ids) in reading order (one quire or whole text)."""
    lc = []
    pg_cnt = collections.defaultdict(lambda: np.zeros(A)); tot = np.zeros(A)
    for pg, ids in lines:
        c = np.bincount(np.asarray(ids[1:], dtype=int), minlength=A) if len(ids) > 1 else np.zeros(A)
        lc.append((pg, c, ids[1:])); pg_cnt[pg] = pg_cnt[pg] + c; tot += c
    epage = {}
    for pg, C in pg_cnt.items():
        N = C.sum(); epage[pg] = (C * (C - 1)).sum() / (N * (N - 1)) if N > 1 else np.nan
    N = tot.sum(); equire = (tot * (tot - 1)).sum() / (N * (N - 1)) if N > 1 else np.nan
    num_d = np.zeros(4); den_d = np.zeros(4); cnum = cden = 0.0
    for pg, c, ids in lc:
        m = len(ids)
        if m < 2:
            continue
        e = (c * (c - 1)).sum() / (m * (m - 1))
        cnum += (c * (c - 1)).sum()
        if not np.isnan(epage[pg]):
            cden += m * (m - 1) * epage[pg]
        a = np.asarray(ids)
        for d in (1, 3):
            if m > d:
                num_d[d] += (a[:-d] == a[d:]).sum(); den_d[d] += (m - d) * e
    xnum = xden = 0.0
    sn = np.zeros(5); sd = np.zeros(5); xn2 = xd2 = 0.0
    for i in range(len(lc)):
        pg1, c1, i1 = lc[i]
        if not len(i1):
            continue
        for D in range(1, 5):
            if i + D >= len(lc):
                break
            pg2, c2, i2 = lc[i + D]
            if not len(i2):
                continue
            if pg2 == pg1:
                sn[D] += (c1 * c2).sum(); sd[D] += len(i1) * len(i2)
                if D == 1 and not np.isnan(epage[pg1]):
                    xnum += (c1 * c2).sum(); xden += len(i1) * len(i2) * epage[pg1]
            elif D == 1:
                xn2 += (c1 * c2).sum(); xd2 += len(i1) * len(i2)
    R1 = num_d[1] / den_d[1] if den_d[1] else np.nan; R3 = num_d[3] / den_d[3] if den_d[3] else np.nan
    S = [sn[D] / sd[D] / equire if sd[D] and equire else np.nan for D in range(5)]
    return {'q1': R1, 'q2': R1 - R3, 'q3': cnum / cden if cden else np.nan, 'q4': xnum / xden if xden else np.nan,
            'q5': S[1], 'q6': np.nanmean(S[2:5]) if any(not np.isnan(x) for x in S[2:5]) else np.nan,
            'q7': xn2 / xd2 / equire if xd2 and equire else np.nan, 'S': S}


def shuffle(lines, rng, mode):
    if mode == 'line':
        out = []
        for pg, ids in lines:
            t = ids[1:]; rng.shuffle(t); out.append((pg, ids[:1] + t))
        return out
    key = (lambda pg: pg) if mode == 'page' else (lambda pg: 0)
    pool = collections.defaultdict(list)
    for pg, ids in lines:
        pool[key(pg)].extend(ids[1:])
    for k in pool:
        rng.shuffle(pool[k])
    pos = collections.defaultdict(int); out = []
    for pg, ids in lines:
        n = len(ids) - 1; k = key(pg); s = pos[k]
        out.append((pg, ids[:1] + pool[k][s:s + n])); pos[k] += n
    return out


# ------------------------------------------------------------ generators
def fit_basic(train, A):
    init = np.full(A, 0.5); uni = np.zeros(A); trans = np.full((A, A), 0.5)
    num = den = 0.0; xn = xd = 0.0; x3n = x3d = 0.0
    prev = None; hist = []
    for q, pg, ids in train:
        init[ids[0]] += 1
        for a, b in zip(ids, ids[1:]):
            trans[a, b] += 1
        t = ids[1:]
        for x in t:
            uni[x] += 1
        m = len(t)
        if m >= 2:
            c = np.bincount(np.asarray(t), minlength=A); num += (c * (c - 1)).sum(); den += m * (m - 1)
        if prev is not None and prev[0] == q and m and len(prev[1]):
            c1 = np.bincount(np.asarray(prev[1]), minlength=A); c2 = np.bincount(np.asarray(t), minlength=A)
            xn += (c1 * c2).sum(); xd += len(prev[1]) * m
        if len(hist) >= 3 and hist[-3][0] == q and m and len(hist[-3][1]):
            c1 = np.bincount(np.asarray(hist[-3][1]), minlength=A); c2 = np.bincount(np.asarray(t), minlength=A)
            x3n += (c1 * c2).sum(); x3d += len(hist[-3][1]) * m
        prev = (q, t); hist.append((q, t))
    p = (uni + 1e-9) / (uni + 1e-9).sum(); s2 = (p ** 2).sum()
    r = num / den if den else 0.0
    alpha = (1 - r) / (r - s2) if r > s2 else 1e6
    return {'init': init / init.sum(), 'p': p, 'T': trans / trans.sum(1, keepdims=True), 'alpha': alpha,
            'rw': r / s2, 'rx': (xn / xd) / s2 if xd else 1.0, 'rx3': (x3n / x3d) / s2 if x3d else 1.0}


def gen(model, kind, layout, rng, lam=None, beta=None):
    """layout: list of (quire, page, n) in reading order. Returns list of (quire, page, ids)."""
    A = len(model['p']); out = []; theta = None; lastq = None
    for q, pg, n in layout:
        first = int(rng.choice(A, p=model['init']))
        if kind == 'drift':
            if theta is None or q != lastq:
                theta = rng.dirichlet(beta * model['p'] + 1e-9)
            else:
                theta = (1 - lam) * theta + lam * rng.dirichlet(beta * model['p'] + 1e-9)
            lastq = q
        if n <= 1:
            out.append((q, pg, [first])); continue
        if kind == 'drift':
            rest = rng.choice(A, size=n - 1, p=theta / theta.sum())
        elif kind == 'line':
            rest = rng.choice(A, size=n - 1, p=rng.dirichlet(np.maximum(model['alpha'] * model['p'], 1e-6)))
        elif kind == 'word':
            rest = rng.choice(A, size=n - 1, p=model['p'])
        else:
            rest = []; pv = first
            for _ in range(n - 1):
                pv = int(rng.choice(A, p=model['T'][pv])); rest.append(pv)
        out.append((q, pg, [first] + [int(x) for x in rest]))
    return out


def fit_drift(model, train_layout):
    best = None
    for lam in LAMS:
        for beta in BETAS:
            rng = np.random.default_rng(9001)
            sim = gen(model, 'drift', train_layout, rng, lam, beta)
            m2 = fit_basic(sim, len(model['p']))
            err = (((m2['rw'] - model['rw']) / model['rw']) ** 2 + ((m2['rx'] - model['rx']) / model['rx']) ** 2
                   + ((m2['rx3'] - model['rx3']) / model['rx3']) ** 2)
            if best is None or err < best[0]:
                best = (err, lam, beta)
    return best[1], best[2]


def fold_job(args):
    below_normal()
    fi, q, streams = args
    ok = {}; real_all = {}; fitted = {}
    for st, (lines, A) in streams.items():
        tr = [l for l in lines if l[0] != q]; he = [l for l in lines if l[0] == q]
        model = fit_basic(tr, A)
        lam, beta = fit_drift(model, [(a, b, len(c)) for a, b, c in tr])
        fitted[st] = (lam, beta, model['alpha'])
        real = profile([(pg, ids) for _, pg, ids in he], A); real_all[st] = real
        lay = [(a, b, len(c)) for a, b, c in he]
        for gi, kind in enumerate(('drift', 'line', 'word', 'markov')):
            rng = np.random.default_rng(9100 + 100 * fi + 10 * gi + (0 if st == 'prefix' else 1))
            sims = [profile([(pg, ids) for _, pg, ids in gen(model, kind, lay, rng, lam, beta)], A) for _ in range(NCOPY)]
            inside = True
            for k in QK:
                v = np.array([s[k] for s in sims], dtype=float); v = v[~np.isnan(v)]; o = real[k]
                if np.isnan(o) or len(v) == 0:
                    continue
                lo, hi = np.percentile(v, ENV)
                if not (lo <= o <= hi):
                    inside = False
            ok[kind] = ok.get(kind, True) and inside
    return q, ok, real_all, fitted


def fold_test(name, streams, out):
    P = out.append
    lines0 = streams['prefix'][0]
    qn = collections.Counter(q for q, _, _ in lines0)
    folds = sorted(q for q, n in qn.items() if n >= 50)
    need = math.ceil(8 / 15 * len(folds))
    P('R9b %s: %d folds, threshold %d' % (name, len(folds), need))
    P('   fold | drift lam/beta (scale) pre ; suf | match (i) drift (ii) line (iii) word (iv) chain | real q1..q7 prefix ; suffix')
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        res = list(ex.map(fold_job, [(fi, q, streams) for fi, q in enumerate(folds)]))
    wins = collections.Counter(); scales = []
    for q, ok, real, fitted in res:
        for k in ('drift', 'line', 'word', 'markov'):
            wins[k] += ok[k]
        scales += [1 / fitted['prefix'][0], 1 / fitted['suffix'][0]]
        P('   %-4s | %.2f/%g (%.1f) ; %.2f/%g (%.1f) | %-5s %-5s %-5s %-5s | %s ; %s' % (
            q, fitted['prefix'][0], fitted['prefix'][1], 1 / fitted['prefix'][0], fitted['suffix'][0], fitted['suffix'][1], 1 / fitted['suffix'][0],
            ok['drift'], ok['line'], ok['word'], ok['markov'],
            ' '.join('%.3f' % real['prefix'][k] for k in QK), ' '.join('%.3f' % real['suffix'][k] for k in QK)))
    call = wins['drift'] >= need and all(wins['drift'] > wins[k] for k in ('line', 'word', 'markov'))
    med = float(np.median(scales))
    P('   matches: (i) drift %d, (ii) line-held %d, (iii) per-word %d, (iv) chain %d (threshold %d); median fitted drift scale %.1f lines -> call %s' % (
        wins['drift'], wins['line'], wins['word'], wins['markov'], need, med, 'PASS' if call else 'FAIL'))
    print(out[-1], flush=True)
    return call, wins, med


def whole_profile(name, streams, out):
    P = out.append
    P('R9a %s (whole text, positions >= 2; decay S(D) and cross-page SX(1))' % name)
    for st, (lines, A) in streams.items():
        bq = collections.defaultdict(list)
        for q, pg, ids in lines:
            bq[q].append((pg, ids))
        # per-quire profiles pooled by averaging S and q5-q7 weighted equally over quires with data
        obs = {q: profile(v, A) for q, v in bq.items()}
        rng = random.Random(9201)
        nulls = []
        for _ in range(NSHUF):
            nulls.append({q: profile(shuffle(v, rng, 'quire'), A) for q, v in bq.items()})

        def avg(d, k):
            vals = [x[k] for x in d.values() if not np.isnan(x[k])]
            return float(np.mean(vals)) if vals else float('nan')
        for k, lab in (('q5', 'S(1)'), ('q6', 'S(2-4)'), ('q7', 'SX(1)')):
            o = avg(obs, k); v = np.array([avg(n, k) for n in nulls])
            P('   %-6s %-7s %.3f (quire-shuffle null %.3f, p_up %.3f)' % (st, lab, o, np.nanmean(v), (1 + int((v >= o).sum())) / (1 + NSHUF)))
        P('   %-6s S(D) D=1..4 (mean over quires): %s' % (st, ' '.join('%.3f' % float(np.nanmean([obs[q]['S'][D] for q in obs])) for D in range(1, 5))))


def planted(layout_q, A, model, kind, rng, lam=0.2, beta=10.0, alpha=3.0):
    m = dict(model); m['alpha'] = alpha
    return gen(m, 'drift' if kind == 'drift' else 'line', layout_q, rng, lam, beta)


def zipf(A):
    w = np.array([1 / (i + 1) for i in range(A)]); return w / w.sum()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r9.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r9.py sha256: %s' % sha(me)]
    P = out.append; calls = {}
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = [('Q%02d' % (i * 15 // 207), i, r.randint(5, 10)) for i in range(207) for _ in range(20)]
        for nm, kind in (('FIX_PLANTED_DRIFT', 'drift'), ('FIX_PLANTED_LINEHELD', 'line')):
            streams = {}
            for st, A, k in (('prefix', 11, 0), ('suffix', 20, 1)):
                base = {'init': zipf(A), 'p': zipf(A), 'T': np.full((A, A), 1 / A), 'alpha': 3.0}
                streams[st] = (planted(layout, A, base, kind, np.random.default_rng(9301 + k)), A)
            whole_profile(nm, streams, out)
            calls[nm] = fold_test(nm, streams, out); P('')
        ok = calls['FIX_PLANTED_DRIFT'][0] and not calls['FIX_PLANTED_LINEHELD'][0]
        P('FIXTURE CHECK: planted drift PASS: %s (median scale %.1f, planted 5) ; planted line-held not PASS: %s ; overall %s' % (
            calls['FIX_PLANTED_DRIFT'][0], calls['FIX_PLANTED_DRIFT'][2], not calls['FIX_PLANTED_LINEHELD'][0], 'OK' if ok else 'NOT OK'))
        rpath = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, it, lat, rpath = sys.argv[2:6]
        here = os.path.dirname(me)
        try:
            reg = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(here, 'r9.prereg.sha256'), encoding='ascii').read().splitlines()
                       if l.strip() and not l.startswith('#'))
        except OSError:
            reg = {}
        P('prereg r9.py %s ; stub match: %s' % (reg.get('r9.py', 'MISSING'), 'YES' if reg.get('r9.py') == sha(me) else 'NO'))
        for f in (zl, it, lat):
            P('data %s %s' % (f, sha(f)))
        seg = make_seg(PREFIXES, SUFFIXES); PA = PREFIXES + ['']; SA = SUFFIXES + ['']
        zl_l = parse_ivtff(zl)
        zs = streams_of(zl_l, seg, PA, SA)
        whole_profile('VOYNICH_ZL', zs, out); calls['ZL'] = fold_test('VOYNICH_ZL', zs, out); P('')
        its = streams_of(parse_ivtff(it), seg, PA, SA)
        whole_profile('VOYNICH_IT', its, out); calls['IT'] = fold_test('VOYNICH_IT', its, out); P('')
        layout = [(q, pg, len(l)) for q, pg, l in zl_l]
        for nm, kind, seedb in (('PLANTED_DRIFT', 'drift', 9401), ('PLANTED_LINEHELD', 'line', 9411)):
            streams = {}
            for st, k in (('prefix', 0), ('suffix', 1)):
                lines, A = zs[st]; base = fit_basic(lines, A)
                streams[st] = (planted(layout, A, base, kind, np.random.default_rng(seedb + k)), A)
            whole_profile(nm, streams, out); calls[nm] = fold_test(nm, streams, out); P('')
        ll = latin_lines(lat)
        pre, suf = freq_affixes([w for _, _, l in ll for w in l])
        P('LATIN affixes: %s ; %s' % (pre, suf))
        ls = streams_of(ll, make_seg(pre, suf), pre + [''], suf + [''])
        whole_profile('LATIN', ls, out); calls['LATIN'] = fold_test('LATIN', ls, out); P('')
        P('CALLS')
        for k in ('ZL', 'IT', 'PLANTED_DRIFT', 'PLANTED_LINEHELD', 'LATIN'):
            c, w, med = calls[k]
            P('%-17s call %s ; matches (i) %d (ii) %d (iii) %d (iv) %d ; median drift scale %.1f lines' % (
                k, 'PASS' if c else 'FAIL', w['drift'], w['line'], w['word'], w['markov'], med))
        ctrl = calls['PLANTED_DRIFT'][0] and not calls['PLANTED_LINEHELD'][0]
        P('Controls: positive (planted drift) PASS required: %s ; negative (planted line-held) not PASS required: %s' % (
            calls['PLANTED_DRIFT'][0], not calls['PLANTED_LINEHELD'][0]))
        P('VERDICT: %s%s' % ('PASS' if calls['ZL'][0] else 'FAIL', '' if ctrl else ' ; CONTROLS MISBEHAVED'))
    open(rpath, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-12:]))


if __name__ == '__main__':
    main()
