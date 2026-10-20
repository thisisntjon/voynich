"""r5.py -- second implementation of F-06 (core residual) and F-13 (core repetition). voynich-91, Roach, blind.

Brief: SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R5-BRIEF-20261018T101945Z. The lead's values were withheld.

DATA: ZL3b-n (primary) and IT2a-n (second transliteration), paragraph loci only.
  Cleaning, segmentation and core definition are unchanged from r3/r4 (IVTFF
  rules V1-V14; prefix/suffix longest match from the r3 lists; core = remainder).
  Streams along each line: prefix, core, suffix (the empty affix is a symbol).
QUIRES: the $Q field of each IVTFF page header. Folds = quires with >= 50
  paragraph lines (ZL: 15 of 16; quire J, with 18 lines, always stays in
  training). Leave-one-quire-out: train on all other pages, score the held-out
  quire. Secondary split: the r3 166/41 pages.
R5a  next-word residual per stream
  Model: Witten-Bell bigram (history = previous token in the same line), backed
  off to a Witten-Bell unigram over a uniform base of (training vocab + 1).
  Fitted on training tokens at line position >= 2 (unigram) and on in-line pairs
  (bigram). Gain = mean over held-out in-line pairs of
  [log2 P_bi(b|a) - log2 P_uni(b)] in bits per token. Held-out tokens unseen in
  training share one UNK symbol. Unseen histories back off, so their gain is 0.
  Decision statistic: p = (1 + #{gain_shuffled >= gain_obs}) / 201, over 200
  within-line shuffles of that stream's tokens in the held-out fold (models fixed).
  CALL (ZL): core p < 0.05 on at least ceil(8/15 * n_folds) folds, AND the prefix
  and suffix streams each reach fewer folds than that.
R5b  core repetition
  For d = 1..30, over pairs (i, i+d) in page reading order (lines concatenated
  within a page) where neither core is empty:
    within  = both tokens in the same line;
    cross   = the pair spans at least one line break (same page);
    reading = all such pairs.
  rate = share of pairs with identical cores. Null: 200 within-page shuffles of
  the core tokens (layout kept, the empty-core mask recomputed after each
  shuffle). R(d) = rate_obs / mean(rate_null).
  p for R(1) > 1: (1 + #{rate_null >= rate_obs}) / 201.
  d* = the first d with R_reading(d) <= 1.
  Rare / common: common = the most frequent training cores (r3 166-page
  training) covering 50 % of training non-empty core tokens; rare = all others.
  R_within(1) is reported separately by the left token's group.
  CALL (ZL): R_within(1) > 1 with p < 0.05, AND R_within(1) > the Latin R_within(1).
CONTROLS, built on the ZL layout (same pages, quires, line lengths) unless noted
  LATIN (positive, R(1) < 1 expected): Caesar BG V-VIII (PG18837). One Gutenberg
    line = one line, 30-line pages, 15 contiguous pseudo-quires. Normalisation:
    NFD, marks dropped, lowercased, non-letters become spaces. Cores: r3
    frequency affixes (10 most common initial bigrams, 20 most common final
    strings of length 1-4, both from the first 80 % of pages), core = remainder.
  COPY (positive, R(1) > 1 expected): Zipf(1) vocabulary of 2,000 core
    codewords. With probability 0.15 a token copies the core 1-5 positions back
    in the same line (uniform), otherwise a fresh Zipf draw. Prefix and suffix
    are uniform random.
  BIGRAM (positive for R5a): the same vocabulary in 75 groups. With probability
    0.5 the next core is drawn from group (7*prev+3) mod 75 (Zipf within the
    group), otherwise from the Zipf vocabulary. Affixes iid uniform.
  NEGATIVE: the ZL cores permuted across the whole book (random.Random(6161));
    prefixes and suffixes kept. Expected null for the core stream in R5a and R5b.
DESCRIPTOR (added after the fixture run, before the freeze): Witten-Bell
  halves the back-off mass for rarely seen histories, so the raw gain can be
  negative with no order at all (IID fixture: -0.57 bits). Each cell therefore
  also reports excess = gain_obs - mean(gain_shuffled). The decision statistic
  is still p. Calibration on 12 IID fixtures: 4.4 % of fold p-values fell below
  0.05 (180 folds).
SEEDS: null shuffles 5001 (R5a) and 5002 (R5b); generators 5101 (copy) and 5102 (bigram).
MODES
  python -I r5.py fixture OUTDIR                 synthetic layout: COPY, BIGRAM and IID generators
  python -I r5.py real ZL IT LAT OUT             real run; checks r5.prereg.sha256
"""
import sys, os, re, math, random, hashlib, datetime, unicodedata, collections
import numpy as np

PREFIXES = ['qo', 'q', 'o', 'y', 'd', 's', 'l', 'r', 'ch', 'sh']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eey', 'ey', 'y', 'ol', 'al', 'or', 'ar',
            'am', 'm', 'g', 'l', 'r', 's']
NULL = 200
DMAX = 30


# ------------------------------------------------------------ parsing
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
    """-> pages OrderedDict page -> lines of words; quire dict page -> $Q."""
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


SEG = make_seg(PREFIXES, SUFFIXES)


def split166(pages):
    ids = sorted(pages); random.Random(20261017).shuffle(ids)
    n = int(len(ids) * 166 / 207) if len(ids) != 207 else 166
    return ids[:n], ids[n:]


def codewords():
    mids = ['']
    for L in (1, 2, 3):
        mids += [''.join(x) for x in _prod('eaio', L)]
    return [a + m + b for a in 'ktpf' for m in mids for b in 'ktpf']


def _prod(alpha, L):
    if L == 0:
        yield (); return
    for x in _prod(alpha, L - 1):
        for c in alpha:
            yield x + (c,)


# ------------------------------------------------------------ corpus = pages of lines of (p, c, s)
def segment_pages(pages, seg=SEG):
    return collections.OrderedDict((pg, [[seg(w) for w in l] for l in ls]) for pg, ls in pages.items())


def gen_layout(template, quire, gen_line, seed):
    """template: pages of lines (only lengths used). gen_line(rng, n) -> list of (p,c,s)."""
    rng = random.Random(seed)
    return collections.OrderedDict((pg, [gen_line(rng, len(l)) for l in ls]) for pg, ls in template.items())


def zipf_vocab(V=2000):
    cw = codewords()
    names = [cw[i % len(cw)] + 'e' * (i // len(cw)) + 'k' for i in range(V)]
    w = [1 / (i + 1) for i in range(V)]
    return names, w


def gen_copy():
    names, w = zipf_vocab(); pre = PREFIXES + ['']; suf = SUFFIXES + ['']

    def line(rng, n):
        cores = []
        for i in range(n):
            if cores and rng.random() < 0.15:
                k = rng.randint(1, min(5, len(cores))); c = cores[-k]
            else:
                c = rng.choices(names, weights=w)[0]
            cores.append(c)
        return [(rng.choice(pre), c, rng.choice(suf)) for c in cores]
    return line


def gen_bigram():
    names, w = zipf_vocab(); V = len(names); pre = PREFIXES + ['']; suf = SUFFIXES + ['']
    groups = [list(range(g, V, 75)) for g in range(75)]
    gw = [[w[c] for c in g] for g in groups]

    def line(rng, n):
        out = []; prev = None
        for _ in range(n):
            if prev is not None and rng.random() < 0.5:
                g = (prev * 7 + 3) % 75; c = rng.choices(groups[g], weights=gw[g])[0]
            else:
                c = rng.choices(range(V), weights=w)[0]
            out.append((rng.choice(pre), names[c], rng.choice(suf))); prev = c
        return out
    return line


def gen_iid():
    names, w = zipf_vocab(); pre = PREFIXES + ['']; suf = SUFFIXES + ['']

    def line(rng, n):
        return [(rng.choice(pre), rng.choices(names, weights=w)[0], rng.choice(suf)) for _ in range(n)]
    return line


def shuffle_cores(corp, seed):
    flat = [t[1] for pg in corp for l in corp[pg] for t in l]
    random.Random(seed).shuffle(flat); it = iter(flat)
    return collections.OrderedDict((pg, [[(t[0], next(it), t[2]) for t in l] for l in ls]) for pg, ls in corp.items())


def latin_corpus(path):
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
    pages = collections.OrderedDict(('p%05d' % (i // 30), []) for i in range(0, len(lines), 30))
    for i, l in enumerate(lines):
        pages['p%05d' % (i // 30)].append(l)
    ids = list(pages)
    ntr = int(len(ids) * 0.8)
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
    corp = segment_pages(pages, make_seg(pre, suf))
    q = {pg: 'Q%02d' % (i * 15 // len(ids)) for i, pg in enumerate(ids)}
    return corp, q, pre, suf


# ------------------------------------------------------------ R5a
def r5a_fold(corp, train, held, k, rng):
    """k: 0 prefix, 1 core, 2 suffix. Returns gain, p, n_pairs."""
    uni = collections.Counter(); bi = collections.defaultdict(collections.Counter)
    for pg in train:
        for l in corp[pg]:
            s = [t[k] for t in l]
            for a, b in zip(s, s[1:]):
                uni[b] += 1; bi[a][b] += 1
    V = len(set(t[k] for pg in train for l in corp[pg] for t in l)) + 1
    N = sum(uni.values()); T = len(uni)

    def p_uni(b):
        return (uni.get(b, 0) + T / V) / (N + T)

    seqs = [[t[k] for t in l] for pg in held for l in corp[pg]]
    vocab = sorted(set(x for s in seqs for x in s))
    UNK = '\x00UNK'
    tr_vocab = set(uni) | set(bi)
    ids = {}
    for x in vocab:
        key = x if (x in tr_vocab) else UNK
        if key not in ids:
            ids[key] = len(ids)
    inv = {i: x for x, i in ids.items()}
    M = len(ids)
    G = np.zeros((M, M))
    for ai in range(M):
        a = inv[ai]; ca = bi.get(a)
        for bj in range(M):
            b = inv[bj]
            pu = p_uni(b) if b != UNK else (T / V) / (N + T)
            if not ca:
                G[ai, bj] = 0.0
            else:
                n = sum(ca.values()); t = len(ca)
                pb = (ca.get(b, 0) + t * pu) / (n + t)
                G[ai, bj] = math.log2(pb) - math.log2(pu)
    flat = []; lid = []
    for li, s in enumerate(seqs):
        for x in s:
            flat.append(ids[x if x in tr_vocab else UNK]); lid.append(li)
    flat = np.array(flat); lid = np.array(lid)
    if len(flat) < 2:
        return float('nan'), float('nan'), 0, float('nan')
    L = np.nonzero(lid[:-1] == lid[1:])[0]
    obs = G[flat[L], flat[L + 1]].mean()
    bounds = []; st = 0
    for s in seqs:
        bounds.append((st, st + len(s))); st += len(s)
    ge = 0; tot = 0.0
    for _ in range(NULL):
        perm = flat.copy()
        for a, b in bounds:
            if b - a > 1:
                seg = list(perm[a:b]); rng.shuffle(seg); perm[a:b] = seg
        gs = G[perm[L], perm[L + 1]].mean(); tot += gs
        if gs >= obs:
            ge += 1
    return float(obs), (1 + ge) / (1 + NULL), len(L), float(obs - tot / NULL)


def run_r5a(name, corp, quire, out, min_lines=50):
    P = out.append
    qlines = collections.Counter()
    for pg in corp:
        qlines[quire[pg]] += len(corp[pg])
    folds = sorted(q for q, n in qlines.items() if n >= min_lines)
    need = math.ceil(8 / 15 * len(folds))
    P('R5a %s: %d folds (quires with >= %d lines): %s ; threshold %d folds' % (name, len(folds), min_lines, ' '.join(folds), need))
    P('   %-5s %6s | %-34s | %-34s | %-34s' % ('fold', 'pairs', 'prefix gain / excess (p)', 'core gain / excess (p)', 'suffix gain / excess (p)'))
    rng = random.Random(5001)
    sig = [0, 0, 0]
    for q in folds:
        held = [pg for pg in corp if quire[pg] == q]; train = [pg for pg in corp if quire[pg] != q]
        row = []
        for k in (0, 1, 2):
            g, p, n, ex = r5a_fold(corp, train, held, k, rng)
            row.append((g, p, ex)); sig[k] += p < 0.05
        P('   %-5s %6d | %+.4f / %+.4f (p=%.3f)      | %+.4f / %+.4f (p=%.3f)      | %+.4f / %+.4f (p=%.3f)' % (
            q, n, row[0][0], row[0][2], row[0][1], row[1][0], row[1][2], row[1][1], row[2][0], row[2][2], row[2][1]))
    P('   folds with p<0.05: prefix %d, core %d, suffix %d (threshold %d)' % (sig[0], sig[1], sig[2], need))
    tr, he = split166(corp)
    row = [r5a_fold(corp, tr, he, k, rng) for k in (0, 1, 2)]
    P('   secondary 166/41 split: prefix %+.4f/%+.4f (p=%.3f), core %+.4f/%+.4f (p=%.3f), suffix %+.4f/%+.4f (p=%.3f)' % (
        row[0][0], row[0][3], row[0][1], row[1][0], row[1][3], row[1][1], row[2][0], row[2][3], row[2][1]))
    call = sig[1] >= need and sig[0] < need and sig[2] < need
    P('   R5a call: %s' % ('PASS' if call else 'FAIL'))
    return call, sig, need


# ------------------------------------------------------------ R5b
def run_r5b(name, corp, out):
    P = out.append
    tr, _ = split166(corp)
    cnt = collections.Counter(t[1] for pg in tr for l in corp[pg] for t in l if t[1] != '')
    tot = sum(cnt.values()); acc = 0; common = set()
    for c, n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])):
        if acc >= tot / 2:
            break
        common.add(c); acc += n
    names = {}
    core, page, line, grp = [], [], [], []
    for pi, pg in enumerate(corp):
        for li, l in enumerate(corp[pg]):
            for t in l:
                c = t[1]
                core.append(names.setdefault(c, len(names))); page.append(pi); line.append(li)
    EMPTY = names.get('', -1)
    core = np.array(core); page = np.array(page); line = np.array(line)
    is_common = np.zeros(len(names), dtype=bool)
    for c, i in names.items():
        if c in common:
            is_common[i] = True
    pg_bounds = []
    st = 0
    for pi, pg in enumerate(corp):
        n = sum(len(l) for l in corp[pg]); pg_bounds.append((st, st + n)); st += n

    def rates(arr):
        res = {}
        for d in range(1, DMAX + 1):
            a = arr[:-d]; b = arr[d:]
            same_pg = page[:-d] == page[d:]
            ok = same_pg & (a != EMPTY) & (b != EMPTY)
            win = ok & (line[:-d] == line[d:])
            crs = ok & (line[:-d] != line[d:])
            eq = a == b
            res[d] = [eq[win].sum(), win.sum(), eq[crs].sum(), crs.sum(), eq[ok].sum(), ok.sum()]
            if d == 1:
                cm = win & is_common[a]; rr = win & ~is_common[a]
                res['grp'] = [eq[cm].sum(), cm.sum(), eq[rr].sum(), rr.sum()]
        return res

    obs = rates(core)
    rng = np.random.default_rng(5002)
    nulls = []
    for _ in range(NULL):
        arr = core.copy()
        for a, b in pg_bounds:
            arr[a:b] = rng.permutation(arr[a:b])
        nulls.append(rates(arr))

    def R(i, j, d):
        o = obs[d][i] / max(obs[d][j], 1)
        nv = [n[d][i] / max(n[d][j], 1) for n in nulls]
        mu = sum(nv) / len(nv)
        p = (1 + sum(1 for v in nv if v >= o)) / (1 + len(nv))
        return o / mu if mu > 0 else float('nan'), p, o, mu

    P('R5b %s: common cores = %d types covering >= 50%% of training core tokens' % (name, len(common)))
    P('   %-3s | %-26s | %-26s | %-26s' % ('d', 'R within (rate obs/null)', 'R cross', 'R reading'))
    dstar = None; series = {}
    for d in range(1, DMAX + 1):
        w = R(0, 1, d); c = R(2, 3, d); r = R(4, 5, d)
        series[d] = (w, c, r)
        if dstar is None and r[0] <= 1:
            dstar = d
        if d <= 10 or d % 5 == 0:
            fmt = lambda x: '%.3f (%.4f/%.4f)' % (x[0], x[2], x[3]) if obs[d][1 if x is w else 3 if x is c else 5] else 'n/a'
            P('   %-3d | %-26s | %-26s | %-26s' % (d, fmt(w), fmt(c), fmt(r)))
    w1 = series[1][0]
    g = obs['grp']
    gn_c = [n['grp'][0] / max(n['grp'][1], 1) for n in nulls]; gn_r = [n['grp'][2] / max(n['grp'][3], 1) for n in nulls]
    Rc = (g[0] / max(g[1], 1)) / (sum(gn_c) / len(gn_c)) if sum(gn_c) else float('nan')
    Rr = (g[2] / max(g[3], 1)) / (sum(gn_r) / len(gn_r)) if sum(gn_r) else float('nan')
    P('   R_within(1) = %.3f, permutation p (R>1) = %.4f ; R_cross(1) = %.3f (p=%.4f) ; d* (R_reading first <= 1) = %s' % (
        w1[0], w1[1], series[1][1][0], series[1][1][1], dstar))
    P('   R_within(1) by left-core group: common %.3f (n=%d pairs), rare %.3f (n=%d pairs)' % (Rc, g[1], Rr, g[3]))
    return w1[0], w1[1], dstar


# ------------------------------------------------------------ main
def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r5.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r5.py sha256: %s' % sha(me)]
    P = out.append
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        rng = random.Random(7)
        template = collections.OrderedDict(('f%03d' % i, [[0] * rng.randint(5, 10) for _ in range(20)]) for i in range(207))
        quire = {pg: 'Q%02d' % (i * 15 // 207) for i, pg in enumerate(template)}
        for nm, g in (('FIX_COPY', gen_copy()), ('FIX_BIGRAM', gen_bigram()), ('FIX_IID', gen_iid())):
            corp = gen_layout(template, quire, g, 5101)
            bad = sum(1 for pg in corp for l in corp[pg] for t in l if SEG(t[0] + t[1] + t[2]) != t)
            P('%s: resegmentation mismatches %d' % (nm, bad))
            corp = segment_pages(collections.OrderedDict((pg, [[''.join(t) for t in l] for l in ls]) for pg, ls in corp.items()))
            run_r5a(nm, corp, quire, out); run_r5b(nm, corp, out); P('')
            print('\n'.join(out[-60:]), flush=True)
        res = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, it, lat, res = sys.argv[2:6]
        try:
            reg = open(os.path.join(os.path.dirname(me), 'r5.prereg.sha256'), encoding='ascii').read().split()[0]
        except OSError:
            reg = 'MISSING'
        P('r5.prereg.sha256: %s' % reg); P('stub match: %s' % ('YES' if reg == sha(me) else 'NO'))
        for f in (zl, it, lat):
            P('data %s sha256 %s' % (os.path.basename(f), sha(f)))
        P('')
        zp, zq = parse_ivtff(zl)
        zc = segment_pages(zp)
        res_zl_a = run_r5a('VOYNICH_ZL', zc, zq, out); res_zl_b = run_r5b('VOYNICH_ZL', zc, out); P('')
        ip, iq = parse_ivtff(it)
        run_r5a('VOYNICH_IT', segment_pages(ip), iq, out); run_r5b('VOYNICH_IT', segment_pages(ip), out); P('')
        lc, lq, pre, suf = latin_corpus(lat)
        P('LATIN affixes: %s ; %s' % (pre, suf))
        run_r5a('LATIN', lc, lq, out); lat_b = run_r5b('LATIN', lc, out); P('')
        for nm, g, seed in (('COPY', gen_copy(), 5101), ('BIGRAM', gen_bigram(), 5102)):
            corp = gen_layout(zp, zq, g, seed)
            corp = segment_pages(collections.OrderedDict((pg, [[''.join(t) for t in l] for l in ls]) for pg, ls in corp.items()))
            run_r5a(nm, corp, zq, out); run_r5b(nm, corp, out); P('')
        neg = shuffle_cores(zc, 6161)
        run_r5a('NEGATIVE', neg, zq, out); run_r5b('NEGATIVE', neg, out); P('')
        P('CALLS (ZL)')
        P('R5a: %s (core folds %d, prefix %d, suffix %d, threshold %d)' % ('PASS' if res_zl_a[0] else 'FAIL', res_zl_a[1][1], res_zl_a[1][0], res_zl_a[1][2], res_zl_a[2]))
        r1, p1, _ = res_zl_b
        P('R5b: %s (R_within(1) %.3f, p %.4f; Latin R_within(1) %.3f)' % (
            'PASS' if (r1 > 1 and p1 < 0.05 and r1 > lat_b[0]) else 'FAIL', r1, p1, lat_b[0]))
    open(res, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-25:]))


if __name__ == '__main__':
    main()
