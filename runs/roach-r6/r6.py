"""r6.py -- line-held affix table test (voynich-91, host Roach; blind, first independent implementation).

Brief: SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R6-BRIEF-20261018T191702Z. The lead's values were withheld.
CLAIM: the affix layer behaves as if each line draws one small affix table, and
the words of the line take their affixes from it.

DATA: ZL3b-n (primary), IT2a-n (second transliteration), paragraph loci. IVTFF
  cleaning, segmenter and affix definition are unchanged from r3-r5: prefix =
  longest match from {qo,q,o,y,d,s,l,r,ch,sh}, else empty (11 symbols); suffix =
  longest match from the r3 list on the remainder, else empty (20 symbols).
  Streams: the prefix stream and the suffix stream along each line.
FOLDS: leave-one-quire-out over the IVTFF $Q quires with >= 50 paragraph lines
  (ZL: 15 folds; quire J always stays in training).

PROFILE (per stream; computed on line positions >= 2, so the line-initial word,
  which is known to be special, is left out of every quantity). Expectations are
  exact closed forms, not simulations:
  R_w(d) = identity rate of pairs (i, i+d) inside a line / its within-line-shuffle
           expectation. For a line with m eligible words and affix counts c,
           P(same) = sum c(c-1) / (m(m-1)) at every d.
  q1 = R_w(1)              within-line order at distance 1
  q2 = R_w(1) - R_w(3)     decay with distance
  q3 = C = sum over lines of sum c(c-1)  /  sum over lines of m(m-1) * e_page,
           with e_page = sum C(C-1) / (N(N-1)) over the page's eligible words:
           within-line clustering against the page
  q4 = X = sum over adjacent lines (same page) of sum c_n c_n+1  /  sum m_n m_n+1 e_page:
           adjacent-line sharing (X near 1 = the table resets at the line break)
DECISION STATISTIC (R6a, whole book): exact permutation p from 200 shuffles.
  q1 and q2 use within-line shuffles of positions >= 2. q3 and q4 are invariant
  under any within-line shuffle by construction, so they use within-page shuffles
  of positions >= 2. p_up = (1 + #{null >= obs}) / 201.
  Two-sided where stated: (1 + #{|null-mean| >= |obs-mean|}) / 201.
LINE-HELD SIGNATURE (used for the Latin negative control): q3 > 1 with p_up < 0.05,
  AND q1 not above shuffle (p_up >= 0.05), AND q4 not above page (p_up >= 0.05).
GENERATORS, fitted on the training quires only, per stream. All three draw the
  line-initial affix from the training line-initial distribution. For positions >= 2:
  (i)   LINE-HELD TABLE: each line draws theta ~ Dirichlet(alpha * p), and its
        words draw iid from theta. p = training unigram over positions >= 2.
        alpha solves (alpha * sum p^2 + 1) / (alpha + 1) = r, with r = the training
        within-line identity rate over positions >= 2. If r <= sum p^2, alpha = 1e6.
        Small alpha = small tables.
  (ii)  PER-WORD TABLE: iid draws from p.
  (iii) FIRST-ORDER MARKOV: P(a_i | a_i-1), add-0.5 smoothing over the alphabet;
        the history includes the line-initial word.
  Each generator produces 200 copies of the held-out quire on its exact layout
  (pages, lines, line lengths).
MATCH (numeric, fixed here): a generator MATCHES a fold if every one of the 8
  quantities (q1-q4 x prefix, suffix) of the real held-out quire lies inside the
  generator's central 99 % envelope, i.e. the [0.5, 99.5] percentiles of its 200
  copies. A NaN quantity (no eligible pairs) counts as inside.
CALL (ZL): (i) matches >= 8 of 15 folds AND (ii) matches < 8 AND (iii) matches < 8
  -> PASS, else FAIL. VERDICT follows the printed call.
CONTROLS
  Positive (fixture and real run): a PLANTED line-held text, Dirichlet(alpha = 3 * p)
    per line for each stream (p = Zipf over the alphabet in the fixture; the
    training unigram in the real run), on the layout. The call must be PASS and
    the fitted alpha should be near 3.
  Fixture chain text: a first-order Markov affix text (each symbol moves to a
    fixed successor with probability 0.5, else uniform). The call must be FAIL,
    with (iii) matching >= 8 folds.
  Negative (real run): Latin prose, Caesar BG V-VIII (PG18837), r3-style frequency
    affixes (10 most common initial bigrams, 20 most common final strings of
    length 1-4, from the first 80 % of pages), 30-line pages, 15 contiguous
    pseudo-quires. It must not show the LINE-HELD SIGNATURE; the full fold call
    is also reported.
SEEDS: generators 6001+; shuffles 6101+; planted 6201; chain 6202.
Runs at below-normal priority, single process.
MODES: python -I r6.py fixture OUTDIR | python -I r6.py real ZL IT LAT OUT
"""
import sys, os, re, math, random, hashlib, datetime, unicodedata, collections
import numpy as np

PREFIXES = ['qo', 'q', 'o', 'y', 'd', 's', 'l', 'r', 'ch', 'sh']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eey', 'ey', 'y', 'ol', 'al', 'or', 'ar',
            'am', 'm', 'g', 'l', 'r', 's']
NCOPY = 200
NSHUF = 200
ENV = (0.5, 99.5)


def below_normal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass(k.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


# ------------------------------------------------------------ parsing (r5)
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
    with open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
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
    return pages, {p: quire.get(p, '?') for p in pages}


def make_seg(prefixes, suffixes):
    P = sorted(prefixes, key=len, reverse=True); S = sorted(suffixes, key=len, reverse=True)

    def seg(w):
        p = next((x for x in P if w.startswith(x)), '')
        rest = w[len(p):]
        s = next((x for x in S if rest.endswith(x) and len(x) <= len(rest)), '')
        return p, rest[:len(rest) - len(s)], s
    return seg


def latin(path):
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
    pages = collections.OrderedDict()
    for i, l in enumerate(lines):
        pages.setdefault('p%05d' % (i // 30), []).append(l)
    ids = list(pages); ntr = int(len(ids) * 0.8)
    ini, fin = collections.Counter(), collections.Counter()
    for pg in ids[:ntr]:
        for l in pages[pg]:
            for w in l:
                if len(w) >= 2:
                    ini[w[:2]] += 1
                for k in range(1, min(4, len(w) - 1) + 1):
                    fin[w[-k:]] += 1
    pre = [x for x, _ in sorted(ini.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]
    suf = [x for x, _ in sorted(fin.items(), key=lambda kv: (-kv[1], kv[0]))[:20]]
    q = {pg: 'Q%02d' % (i * 15 // len(ids)) for i, pg in enumerate(ids)}
    return pages, q, pre, suf


# ------------------------------------------------------------ data model
class Layout:
    """pages -> lines -> affix ids for one stream; arrays for vectorised stats."""

    def __init__(self, page_lines):
        # page_lines: list of (page_index, [ids ...]) per line, in order
        self.lines = page_lines


def to_stream(pages, quire, seg, which, alphabet):
    idx = {a: i for i, a in enumerate(alphabet)}
    out = []  # list of (quire, page_no, [ids])
    for pi, (pg, ls) in enumerate(pages.items()):
        for l in ls:
            out.append((quire[pg], pi, [idx[seg(w)[which]] for w in l]))
    return out


def profile(lines, A):
    """lines: list of (page_no, ids). Returns dict q1..q4 and R_w(1..6)."""
    # counts over positions >= 2
    pg_cnt = collections.defaultdict(lambda: np.zeros(A))
    lc = []
    for pg, ids in lines:
        c = np.bincount(np.asarray(ids[1:], dtype=int), minlength=A) if len(ids) > 1 else np.zeros(A)
        lc.append((pg, c, ids[1:]))
        pg_cnt[pg] = pg_cnt[pg] + c
    epage = {}
    for pg, C in pg_cnt.items():
        N = C.sum()
        epage[pg] = (C * (C - 1)).sum() / (N * (N - 1)) if N > 1 else np.nan
    num_d = np.zeros(7); den_d = np.zeros(7)
    cnum = 0.0; cden = 0.0
    for pg, c, ids in lc:
        m = len(ids)
        if m < 2:
            continue
        e = (c * (c - 1)).sum() / (m * (m - 1))
        cnum += (c * (c - 1)).sum()
        if not np.isnan(epage[pg]):
            cden += m * (m - 1) * epage[pg]
        a = np.asarray(ids)
        for d in range(1, 7):
            if m > d:
                num_d[d] += (a[:-d] == a[d:]).sum()
                den_d[d] += (m - d) * e
    xnum = 0.0; xden = 0.0
    for (pg1, c1, i1), (pg2, c2, i2) in zip(lc, lc[1:]):
        if pg1 == pg2 and len(i1) and len(i2) and not np.isnan(epage[pg1]):
            xnum += (c1 * c2).sum(); xden += len(i1) * len(i2) * epage[pg1]
    R = {d: (num_d[d] / den_d[d] if den_d[d] > 0 else np.nan) for d in range(1, 7)}
    return {'q1': R[1], 'q2': R[1] - R[3], 'q3': cnum / cden if cden > 0 else np.nan,
            'q4': xnum / xden if xden > 0 else np.nan, 'R': R}


QK = ('q1', 'q2', 'q3', 'q4')


def shuffle_lines(lines, rng, mode):
    """mode 'line': shuffle positions >= 2 within each line; 'page': within each page."""
    if mode == 'line':
        out = []
        for pg, ids in lines:
            t = ids[1:]; rng.shuffle(t); out.append((pg, ids[:1] + t))
        return out
    bypg = collections.defaultdict(list)
    for k, (pg, ids) in enumerate(lines):
        bypg[pg].extend(ids[1:])
    for pg in bypg:
        rng.shuffle(bypg[pg])
    pos = collections.defaultdict(int); out = []
    for pg, ids in lines:
        n = len(ids) - 1; s = pos[pg]
        out.append((pg, ids[:1] + bypg[pg][s:s + n])); pos[pg] += n
    return out


def r6a(name, streams, out):
    """streams: {'prefix': (lines, A), 'suffix': ...}. Whole-book profile with permutation p."""
    P = out.append
    P('R6a %s (whole text, positions >= 2)' % name)
    sig = {}
    for st, (lines, A) in streams.items():
        pl = [(pg, ids) for _, pg, ids in lines]
        obs = profile(pl, A)
        rng = random.Random(6101)
        nl = [profile(shuffle_lines(pl, rng, 'line'), A) for _ in range(NSHUF)]
        npg = [profile(shuffle_lines(pl, rng, 'page'), A) for _ in range(NSHUF)]
        res = {}
        for q, nulls in (('q1', nl), ('q2', nl), ('q3', npg), ('q4', npg)):
            v = np.array([n[q] for n in nulls]); o = obs[q]; mu = np.nanmean(v)
            pu = (1 + int((v >= o).sum())) / (1 + len(v))
            pt = (1 + int((np.abs(v - mu) >= abs(o - mu)).sum())) / (1 + len(v))
            res[q] = (o, mu, pu, pt)
        P('   %-6s q1 R_w(1) %.3f (null %.3f, p_up %.3f, p_two %.3f) | q2 decay %+.3f (null %+.3f, p_up %.3f, p_two %.3f)' % (
            st, *res['q1'], *res['q2']))
        P('   %-6s q3 C %.3f (page null %.3f, p_up %.3f) | q4 X %.3f (page null %.3f, p_up %.3f, p_two %.3f)' % (
            st, res['q3'][0], res['q3'][1], res['q3'][2], *res['q4']))
        P('   %-6s R_w(d) d=1..6: %s' % (st, ' '.join('%.3f' % obs['R'][d] for d in range(1, 7))))
        sig[st] = res['q3'][0] > 1 and res['q3'][2] < 0.05 and res['q1'][2] >= 0.05 and res['q4'][2] >= 0.05
        P('   %-6s line-held signature: %s' % (st, 'YES' if sig[st] else 'no'))
    return sig


# ------------------------------------------------------------ generators
def fit(train_lines, A):
    init = np.full(A, 0.5); uni = np.full(A, 0.0); trans = np.full((A, A), 0.5)
    num = 0.0; den = 0.0
    for _, _, ids in train_lines:
        init[ids[0]] += 1
        for a, b in zip(ids, ids[1:]):
            trans[a, b] += 1
        t = ids[1:]
        for x in t:
            uni[x] += 1
        m = len(t)
        if m >= 2:
            c = np.bincount(np.asarray(t), minlength=A)
            num += (c * (c - 1)).sum(); den += m * (m - 1)
    p = (uni + 1e-9) / (uni + 1e-9).sum()
    r = num / den if den else 0.0
    s2 = (p ** 2).sum()
    alpha = (1 - r) / (r - s2) if r > s2 else 1e6
    return {'init': init / init.sum(), 'p': p, 'T': trans / trans.sum(1, keepdims=True), 'alpha': alpha, 'r': r, 's2': s2}


def generate(model, kind, layout_lens, rng):
    """layout_lens: list of (page_no, n). Returns list of (page_no, ids)."""
    A = len(model['p']); out = []
    for pg, n in layout_lens:
        first = int(rng.choice(A, p=model['init']))
        if n == 1:
            out.append((pg, [first])); continue
        if kind == 'line':
            th = rng.dirichlet(np.maximum(model['alpha'] * model['p'], 1e-6))
            rest = list(rng.choice(A, size=n - 1, p=th))
        elif kind == 'word':
            rest = list(rng.choice(A, size=n - 1, p=model['p']))
        else:
            rest = []; prev = first
            for _ in range(n - 1):
                prev = int(rng.choice(A, p=model['T'][prev])); rest.append(prev)
        out.append((pg, [first] + [int(x) for x in rest]))
    return out


def fold_test(name, streams, out, min_lines=50):
    """streams: {'prefix': (lines, A), 'suffix': ...}; lines = (quire, page, ids)."""
    P = out.append
    lines0 = next(iter(streams.values()))[0]
    qn = collections.Counter(q for q, _, _ in lines0)
    folds = sorted(q for q, n in qn.items() if n >= min_lines)
    need = math.ceil(8 / 15 * len(folds))
    P('R6b %s: %d folds: %s ; match threshold %d folds' % (name, len(folds), ' '.join(folds), need))
    P('   fold  lines | alpha(pre) alpha(suf) | match (i) line-held, (ii) per-word, (iii) Markov | real q1..q4 prefix ; suffix')
    wins = {'line': 0, 'word': 0, 'markov': 0}
    for fi, q in enumerate(folds):
        ok = {}; real_all = {}; alphas = {}
        for st, (lines, A) in streams.items():
            tr = [l for l in lines if l[0] != q]; he = [l for l in lines if l[0] == q]
            model = fit(tr, A); alphas[st] = model['alpha']
            real = profile([(pg, ids) for _, pg, ids in he], A); real_all[st] = real
            lay = [(pg, len(ids)) for _, pg, ids in he]
            for gi, kind in enumerate(('line', 'word', 'markov')):
                rng = np.random.default_rng(6001 + 100 * fi + 10 * gi + (0 if st == 'prefix' else 1))
                sims = [profile(generate(model, kind, lay, rng), A) for _ in range(NCOPY)]
                inside = True
                for k in QK:
                    v = np.array([s[k] for s in sims], dtype=float); v = v[~np.isnan(v)]
                    o = real[k]
                    if np.isnan(o) or len(v) == 0:
                        continue
                    lo, hi = np.percentile(v, ENV)
                    if not (lo <= o <= hi):
                        inside = False
                ok[kind] = ok.get(kind, True) and inside
        for k in wins:
            wins[k] += ok[k]
        P('   %-5s %5d | %9.2f %10.2f | %-5s %-5s %-5s | %s ; %s' % (
            q, sum(1 for l in lines0 if l[0] == q), alphas['prefix'], alphas['suffix'],
            'YES' if ok['line'] else 'no', 'YES' if ok['word'] else 'no', 'YES' if ok['markov'] else 'no',
            ' '.join('%.3f' % real_all['prefix'][k] for k in QK), ' '.join('%.3f' % real_all['suffix'][k] for k in QK)))
        print(out[-1], flush=True)
    call = wins['line'] >= need and wins['word'] < need and wins['markov'] < need
    P('   folds matched: (i) line-held %d, (ii) per-word %d, (iii) Markov %d (threshold %d) -> call %s' % (
        wins['line'], wins['word'], wins['markov'], need, 'PASS' if call else 'FAIL'))
    return call, wins, need


# ------------------------------------------------------------ synthetic texts
def planted(layout, A, p, alpha, init, rng):
    return [(q, pg, [int(rng.choice(A, p=init))] + [int(x) for x in rng.choice(A, size=n - 1, p=rng.dirichlet(alpha * p))] if n > 1 else [int(rng.choice(A, p=init))])
            for q, pg, n in layout]


def chain_text(layout, A, rng):
    succ = [(a + 3) % A for a in range(A)]; out = []
    for q, pg, n in layout:
        ids = [int(rng.integers(A))]
        for _ in range(n - 1):
            ids.append(succ[ids[-1]] if rng.random() < 0.5 else int(rng.integers(A)))
        out.append((q, pg, ids))
    return out


def zipf(A):
    w = np.array([1 / (i + 1) for i in range(A)]); return w / w.sum()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r6.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r6.py sha256: %s' % sha(me)]
    P = out.append
    calls = {}
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = []
        for i in range(207):
            for _ in range(20):
                layout.append(('Q%02d' % (i * 15 // 207), i, r.randint(5, 10)))
        for nm, mk in (('FIX_PLANTED_LINE_HELD', 'planted'), ('FIX_CHAIN', 'chain')):
            streams = {}
            for st, A, seed in (('prefix', 11, 0), ('suffix', 20, 1)):
                rng = np.random.default_rng(6201 + seed if mk == 'planted' else 6202 + seed)
                lines = planted(layout, A, zipf(A), 3.0, zipf(A), rng) if mk == 'planted' else chain_text(layout, A, rng)
                streams[st] = (lines, A)
            r6a(nm, streams, out)
            calls[nm] = fold_test(nm, streams, out)
            P('')
        ok1 = calls['FIX_PLANTED_LINE_HELD'][0]
        ok2 = (not calls['FIX_CHAIN'][0]) and calls['FIX_CHAIN'][1]['markov'] >= calls['FIX_CHAIN'][2]
        P('FIXTURE CHECK: planted line-held -> PASS required: %s ; chain -> FAIL with (iii) >= threshold required: %s ; overall %s' % (
            ok1, ok2, 'OK' if ok1 and ok2 else 'NOT OK'))
        res = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, it, lat, res = sys.argv[2:6]
        here = os.path.dirname(me)
        try:
            ent = [l.split() for l in open(os.path.join(here, 'r6.prereg.sha256'), encoding='ascii').read().splitlines()
                   if l.strip() and not l.startswith('#')]
            reg = dict((e[1], e[0]) for e in ent)
        except OSError:
            reg = {}
        P('prereg r6.py: %s ; stub match: %s' % (reg.get('r6.py', 'MISSING'), 'YES' if reg.get('r6.py') == sha(me) else 'NO'))
        for f in (zl, it, lat):
            P('data %s sha256 %s' % (f, sha(f)))
        P('')
        seg = make_seg(PREFIXES, SUFFIXES)
        PA = PREFIXES + ['']; SA = SUFFIXES + ['']
        zp, zq = parse_ivtff(zl)
        zs = {'prefix': (to_stream(zp, zq, seg, 0, PA), len(PA)), 'suffix': (to_stream(zp, zq, seg, 2, SA), len(SA))}
        r6a('VOYNICH_ZL', zs, out)
        calls['ZL'] = fold_test('VOYNICH_ZL', zs, out); P('')
        ip, iq = parse_ivtff(it)
        isd = {'prefix': (to_stream(ip, iq, seg, 0, PA), len(PA)), 'suffix': (to_stream(ip, iq, seg, 2, SA), len(SA))}
        r6a('VOYNICH_IT', isd, out)
        calls['IT'] = fold_test('VOYNICH_IT', isd, out); P('')
        # positive control: planted line-held on the ZL layout with ZL-fitted distributions
        layout = [(q, pg, len(ids)) for q, pg, ids in zs['prefix'][0]]
        ps = {}
        for st, k in (('prefix', 0), ('suffix', 1)):
            lines, A = zs[st]; m = fit(lines, A)
            ps[st] = (planted(layout, A, m['p'], 3.0, m['init'], np.random.default_rng(6201 + k)), A)
        r6a('PLANTED_LINE_HELD (alpha=3)', ps, out)
        calls['PLANTED'] = fold_test('PLANTED_LINE_HELD', ps, out); P('')
        lp, lq, pre, suf = latin(lat)
        P('LATIN affixes: %s ; %s' % (pre, suf))
        lseg = make_seg(pre, suf)
        ls = {'prefix': (to_stream(lp, lq, lseg, 0, pre + ['']), len(pre) + 1), 'suffix': (to_stream(lp, lq, lseg, 2, suf + ['']), len(suf) + 1)}
        lsig = r6a('LATIN', ls, out)
        calls['LATIN'] = fold_test('LATIN', ls, out); P('')
        P('CALLS')
        P('Positive control (planted line-held, alpha=3): call %s (required PASS)' % ('PASS' if calls['PLANTED'][0] else 'FAIL'))
        P('Negative control (Latin): line-held signature prefix=%s suffix=%s (required: no); fold call %s' % (
            lsig['prefix'], lsig['suffix'], 'PASS' if calls['LATIN'][0] else 'FAIL'))
        P('IT (second transliteration): call %s, folds (i) %d (ii) %d (iii) %d' % (
            'PASS' if calls['IT'][0] else 'FAIL', calls['IT'][1]['line'], calls['IT'][1]['word'], calls['IT'][1]['markov']))
        w = calls['ZL'][1]
        P('ZL CALL: (i) line-held matches %d/15, (ii) per-word %d/15, (iii) Markov %d/15, threshold %d -> %s' % (
            w['line'], w['word'], w['markov'], calls['ZL'][2], 'PASS' if calls['ZL'][0] else 'FAIL'))
        controls_ok = calls['PLANTED'][0] and not (lsig['prefix'] or lsig['suffix'])
        P('VERDICT: %s%s' % ('PASS' if calls['ZL'][0] else 'FAIL', '' if controls_ok else ' (controls not as required; see above)'))
    open(res, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-14:]))


if __name__ == '__main__':
    main()
