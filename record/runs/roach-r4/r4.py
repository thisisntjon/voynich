"""r4.py -- blind test of "adjacent word cores are not ordered" (voynich-91, host Roach).

Brief: SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R4-BRIEF-20261018T095927Z. The lead's values were withheld.

DATA, SPLIT, SEGMENTATION: unchanged from r3.py (r3 sha256 06e88402...):
  ZL3b-n paragraph loci, IVTFF rules V1-V14, '.' and ',' as word separators;
  pages sorted, random.Random(20261017).shuffle, first 166 pages = training;
  prefix/suffix longest match from the r3 lists, core = remainder (may be '').
UNIT: the sequence of cores along each line. Pairs = adjacent cores in a line.

CLASS MAPS (fitted on training pages only), K in {25, 50, 100, 200, 400, full}
  freq    : the K-1 most frequent training cores (ties by string) keep their own
            class; every other core, seen or unseen, goes to one pooled class.
  cluster : spherical k-means on neighbour profiles. Eligible = training cores
            with count >= 5. Profile = [left-neighbour distribution | right-
            neighbour distribution] over the 50 most frequent training cores
            + OTHER + line boundary (52 + 52 dims). Each half is normalised to
            sum 1, then the vector to unit length. k = min(K-1, n_eligible)
            clusters, k-means++ init (numpy default_rng(4040)), cosine
            assignment, 50 iterations, an empty cluster is reseeded with the
            worst-fit point. Non-eligible and unseen cores go to one pooled class.
  full    : every training core is its own class; unseen cores share one class.
            It is identical under both methods and computed once.
STATISTIC: MI(X;Y) in bits between the classes of adjacent cores, over pairs on
  held-out pages. Plug-in and Miller-Madow:
  MI_MM = MI_plug + [(Kx-1)+(Ky-1)-(Kxy-1)] / (2 N ln 2), with Kx, Ky, Kxy the
  nonzero cells.
  NULL: 200 within-line shuffles of word order (line membership kept), drawn once
  per corpus as position permutations and shared by every class map.
  EXCESS = observed - mean over the 200 shuffles (computed per estimator).
  INTERVAL: 500 draws of round(80 %) of the held-out pages without replacement.
  Each draw has excess = MI_obs(draw) - mean null over shuffles 1-20 (a declared
  reduction from 200, for run time). 2.5 / 97.5 percentiles, plus the r3
  rescaled interval est + sqrt(k/(n-k)) * (q - median) as secondary.
POSITIVE CONTROLS (planted order):
  Plaintexts: Latin, Caesar BG V-VIII (PG18837, about 31k words); Italian,
  Manzoni Promessi sposi (PG45334, first 60,000 words). Normalisation: NFD,
  marks dropped, lowercase, letters a-z only, all other characters dropped, so
  the text becomes one letter stream.
  (a) each plaintext letter -> one core codeword;
  (b) each consecutive 2-letter chunk -> one core codeword.
  Codewords: strings C1 + mid + C2 with C1, C2 in {k,t,p,f} and mid over
  {e,a,i,o} of length 0-3, assigned to symbols by random.Random(5151). Every
  cipher word = random prefix + codeword + random suffix, uniform over the r3
  lists including empty, random.Random(5152). These codewords segment back
  exactly (verified on the fixture).
  Size and layout match the Voynich: the first 35,075 cipher words fill the ZL
  pages, lines and line lengths exactly, under the same page ids, so the split is
  identical.
NEGATIVE CONTROL: the ZL text with cores permuted across the whole book
  (random.Random(6161)); prefixes, suffixes, lines and pages are kept.
PRE-REGISTERED CALLS. Primary = plug-in excess; Miller-Madow reported as secondary.
  (i)   K=100 freq: Voynich excess > 0 with the interval above 0 -> YES / NO.
  (ii)  For K in {50, 100, 200} x {freq, cluster}: Voynich upper bound < the lower
        bound of cipher (a) and of cipher (b). Evaluated separately for the Latin
        and Italian ciphers. YES only if every one of the 6 cells holds for both
        languages; otherwise the failing cells are listed.
  (iii) The negative control's interval includes 0 at every K under both methods;
        otherwise "controls failed".
SECONDARY CHECKS (added after the fixture run, before the freeze)
  On no-order fixtures the brief's interval sometimes excluded 0, even though
  across seeds the excess is centred on 0 (|z| <= 2.3 against the shuffle
  distribution). A page subsample cannot see the realisation noise of the one
  observed sequence. So each cell also reports the null sd and the exact
  permutation p from the 200 shuffles:
    p_up = (1 + #{null >= obs}) / 201;  p_two = (1 + #{|null-mean| >= |obs-mean|}) / 201.
  Secondary calls: (i) p_up < 0.025; (ii) Voynich rescaled upper bound < cipher
  rescaled lower bound; (iii) p_two >= 0.05 in every negative-control cell.
  Primary calls remain exactly as briefed.
MODES
  python -I r4.py fixture OUTDIR             synthetic: planted core chain vs no chain (Voynich-like sparsity)
  python -I r4.py real ZL LAT IT OUT         real run; checks r4.prereg.sha256
"""
import sys, os, re, math, random, hashlib, datetime, unicodedata, collections
import numpy as np

PREFIXES = ['qo', 'q', 'o', 'y', 'd', 's', 'l', 'r', 'ch', 'sh']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eey', 'ey', 'y', 'ol', 'al', 'or', 'ar',
            'am', 'm', 'g', 'l', 'r', 's']
N_TRAIN = 166
KS = [25, 50, 100, 200, 400, 'full']
NULL_REPS = 200
NULL_SUB = 20
DRAWS = 500
LN2 = math.log(2)


# ------------------------------------------------------------ parsing (from r3)
def clean_ivtff_text(t):
    t = re.sub(r'<![^>]*>', '', t)
    t = re.sub(r'<[%$]>', '', t)
    t = re.sub(r'<@[^>]*>', '', t)
    t = re.sub(r'<[-~]>', '.', t)
    t = re.sub(r'<[^>]*>', '', t)
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
    loc = re.compile(r'^<(f[0-9A-Za-z]+)\.(\w+),(.)(\w)[^>]*>\s?(.*)$')
    pages = collections.OrderedDict()
    with open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            s = raw.rstrip('\r\n')
            if not s or s.startswith('#'):
                continue
            m = loc.match(s)
            if not m or m.group(4) != 'P':
                continue
            w = clean_ivtff_text(m.group(5))
            if w:
                pages.setdefault(m.group(1), []).append(w)
    return pages


def split_pages(pages):
    ids = sorted(pages)
    random.Random(20261017).shuffle(ids)
    return ids[:N_TRAIN], ids[N_TRAIN:]


def make_seg():
    P = sorted(PREFIXES, key=len, reverse=True)
    S = sorted(SUFFIXES, key=len, reverse=True)

    def seg(w):
        p = next((x for x in P if w.startswith(x)), '')
        rest = w[len(p):]
        s = next((x for x in S if rest.endswith(x)), '')
        return p, rest[:len(rest) - len(s)], s
    return seg


SEG = make_seg()


def core_pages(word_pages):
    return collections.OrderedDict((pg, [[SEG(w)[1] for w in l] for l in lines]) for pg, lines in word_pages.items())


# ------------------------------------------------------------ controls
def letter_stream(path, max_words=None):
    txt = open(path, encoding='utf-8').read().splitlines()
    i0 = next(i for i, l in enumerate(txt) if l.startswith('*** START'))
    i1 = next(i for i, l in enumerate(txt) if l.startswith('*** END'))
    out, n = [], 0
    for l in txt[i0 + 1:i1]:
        t = unicodedata.normalize('NFD', l)
        t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
        ws = re.findall(r'[a-z]+', t)
        if max_words is not None and n >= max_words:
            break
        n += len(ws)
        out.append(''.join(ws))
    return ''.join(out), n


def codewords():
    mids = ['']
    for L in (1, 2, 3):
        mids += [''.join(x) for x in _product('eaio', L)]
    return [a + m + b for a in 'ktpf' for m in mids for b in 'ktpf']


def _product(alpha, L):
    if L == 0:
        yield ()
        return
    for x in _product(alpha, L - 1):
        for c in alpha:
            yield x + (c,)


def cipher_words(stream, chunk, n_needed):
    syms = [stream[i:i + chunk] for i in range(0, len(stream) - chunk + 1, chunk)]
    alphabet = sorted(set(syms))
    cw = codewords()
    if len(alphabet) > len(cw):
        raise SystemExit('not enough codewords')
    rng = random.Random(5151)
    cw2 = list(cw); rng.shuffle(cw2)
    code = dict(zip(alphabet, cw2))
    r2 = random.Random(5152)
    pre = PREFIXES + ['']; suf = SUFFIXES + ['']
    if len(syms) < n_needed:
        raise SystemExit('plaintext too short for layout: %d < %d' % (len(syms), n_needed))
    return [r2.choice(pre) + code[s] + r2.choice(suf) for s in syms[:n_needed]], len(alphabet)


def layout_like(template_pages, words):
    it = iter(words)
    return collections.OrderedDict((pg, [[next(it) for _ in l] for l in lines]) for pg, lines in template_pages.items())


def shuffle_cores_globally(cpages, seed):
    flat = [c for pg in cpages for l in cpages[pg] for c in l]
    random.Random(seed).shuffle(flat)
    it = iter(flat)
    return collections.OrderedDict((pg, [[next(it) for _ in l] for l in lines]) for pg, lines in cpages.items())


# ------------------------------------------------------------ class maps
def train_counts(cpages, train):
    return collections.Counter(c for pg in train for l in cpages[pg] for c in l)


def freq_map(cnt, K):
    ranked = [c for c, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]
    if K == 'full':
        m = {c: i for i, c in enumerate(ranked)}
        return m, len(ranked), len(ranked) + 1
    keep = ranked[:K - 1]
    return {c: i for i, c in enumerate(keep)}, len(keep), len(keep) + 1


def cluster_map(cpages, train, cnt, K):
    ranked = [c for c, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]
    elig = [c for c in ranked if cnt[c] >= 5]
    ctx = {c: i for i, c in enumerate(ranked[:50])}
    OTHER, BND = 50, 51
    idx = {c: i for i, c in enumerate(elig)}
    L = np.zeros((len(elig), 52)); R = np.zeros((len(elig), 52))
    for pg in train:
        for l in cpages[pg]:
            for j, c in enumerate(l):
                i = idx.get(c)
                if i is None:
                    continue
                L[i, ctx.get(l[j - 1], OTHER) if j > 0 else BND] += 1
                R[i, ctx.get(l[j + 1], OTHER) if j + 1 < len(l) else BND] += 1
    L /= np.maximum(L.sum(1, keepdims=True), 1); R /= np.maximum(R.sum(1, keepdims=True), 1)
    X = np.hstack([L, R]); X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    k = min(K - 1, len(elig))
    if k >= len(elig):
        lab = np.arange(len(elig))
    else:
        rng = np.random.default_rng(4040)
        cent = [X[rng.integers(len(X))]]
        d = 1 - X @ cent[0]
        for _ in range(1, k):
            p = np.maximum(d, 0); p = p / p.sum() if p.sum() > 0 else None
            cent.append(X[rng.choice(len(X), p=p)])
            d = np.minimum(d, 1 - X @ cent[-1])
        C = np.array(cent)
        for _ in range(50):
            sim = X @ C.T
            lab = sim.argmax(1)
            best = sim[np.arange(len(X)), lab]
            newC = np.zeros_like(C)
            for j in range(k):
                mem = X[lab == j]
                if len(mem):
                    v = mem.sum(0); newC[j] = v / max(np.linalg.norm(v), 1e-12)
                else:
                    w = int(best.argmin()); newC[j] = X[w]; best[w] = 2.0
            if np.allclose(newC, C):
                break
            C = newC
        lab = (X @ C.T).argmax(1)
    m = {c: int(lab[i]) for c, i in idx.items()}
    return m, k, k + 1


# ------------------------------------------------------------ statistic
class Corpus:
    def __init__(self, cpages, train, held):
        self.cpages, self.train, self.held = cpages, train, held
        words, page, line = [], [], []
        for pi, pg in enumerate(held):
            for li, l in enumerate(cpages[pg]):
                for c in l:
                    words.append(c); page.append(pi); line.append((pi, li))
        self.words = words
        self.page = np.array(page)
        ln = np.array([hash(x) for x in line])
        self.left = np.nonzero(ln[:-1] == ln[1:])[0]
        self.pair_page = self.page[self.left]
        rng = random.Random(4242)
        bounds = []
        start = 0
        for pg in held:
            for l in cpages[pg]:
                bounds.append((start, start + len(l))); start += len(l)
        self.perms = []
        for _ in range(NULL_REPS):
            perm = np.arange(len(words))
            for a, b in bounds:
                seg = list(range(a, b)); rng.shuffle(seg); perm[a:b] = seg
            self.perms.append(perm)


def mi_codes(codes, M):
    N = len(codes)
    if N == 0:
        return float('nan'), float('nan')
    u, c = np.unique(codes, return_counts=True)
    x = u // M; y = u % M
    cx = np.bincount(codes // M, minlength=M); cy = np.bincount(codes % M, minlength=M)
    mi = float(np.sum(c / N * np.log2(c * N / (cx[x] * cy[y]))))
    kx = int((cx > 0).sum()); ky = int((cy > 0).sum()); kxy = len(u)
    mm = mi + ((kx - 1) + (ky - 1) - (kxy - 1)) / (2 * N * LN2)
    return mi, mm


def pct(xs, q):
    xs = sorted(xs); pos = (len(xs) - 1) * q; lo = int(math.floor(pos)); hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def evaluate(corp, cmap, M):
    unseen = M - 1
    cls = np.array([cmap.get(w, unseen) for w in corp.words], dtype=np.int64)
    L, Rr = corp.left, corp.left + 1
    obs = cls[L] * M + cls[Rr]
    nulls = [cls[p[L]] * M + cls[p[Rr]] for p in corp.perms]
    o = mi_codes(obs, M)
    nv = [mi_codes(n, M) for n in nulls]
    res = {}
    for e in (0, 1):
        res[e] = [o[e], sum(v[e] for v in nv) / len(nv), o[e] - sum(v[e] for v in nv) / len(nv)]
    extra = {}
    for e in (0, 1):
        arr = np.array([v[e] for v in nv]); mu = arr.mean(); sd = arr.std(ddof=1)
        p_up = (1 + int((arr >= o[e]).sum())) / (1 + len(arr))
        p_two = (1 + int((np.abs(arr - mu) >= abs(o[e] - mu)).sum())) / (1 + len(arr))
        extra[e] = [sd, p_up, p_two]
    npg = len(corp.held); k = int(round(0.8 * npg))
    rng = random.Random(4343)
    ex = {0: [], 1: []}
    for _ in range(DRAWS):
        sub = np.array(rng.sample(range(npg), k))
        mask = np.isin(corp.pair_page, sub)
        oo = mi_codes(obs[mask], M)
        ns = [mi_codes(nulls[r][mask], M) for r in range(NULL_SUB)]
        for e in (0, 1):
            ex[e].append(oo[e] - sum(v[e] for v in ns) / NULL_SUB)
    f = math.sqrt(k / (npg - k))
    for e in (0, 1):
        lo, hi, med = pct(ex[e], .025), pct(ex[e], .975), pct(ex[e], .5)
        g = res[e][2]
        res[e] += [lo, hi, g + f * (lo - med), g + f * (hi - med)] + extra[e]
    return res, len(obs)


def run_corpus(name, cpages, out, store):
    train, held = split_pages(cpages)
    corp = Corpus(cpages, train, held)
    cnt = train_counts(cpages, train)
    out.append('== %s: pages %d (train %d, held-out %d), held-out words %d, training core types %d' % (
        name, len(cpages), len(train), len(held), len(corp.words), len(cnt)))
    out.append('   %-8s %-5s %6s %6s | %-72s | %-72s' % ('method', 'K', 'nclass', 'pairs',
               'plug-in excess [95%] (rescaled) null-sd p_up/p_two', 'Miller-Madow excess [95%] (rescaled) null-sd p_up/p_two'))
    for method in ('freq', 'cluster'):
        for K in KS:
            if method == 'cluster' and K == 'full':
                continue
            if method == 'freq':
                cmap, nk, M = freq_map(cnt, K)
            else:
                cmap, nk, M = cluster_map(cpages, train, cnt, K)
            r, npairs = evaluate(corp, cmap, M)
            store[(name, method, K)] = r
            fmt = lambda v: '%+.4f [%+.4f,%+.4f] (%+.4f,%+.4f) sd%.4f p%.3f/%.3f' % (v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9])
            out.append('   %-8s %-5s %6d %6d | %-72s | %-72s' % (method, K, M, npairs, fmt(r[0]), fmt(r[1])))
            print(out[-1], flush=True)


def calls(store, out):
    P = out.append
    for e, tag in ((0, 'PRIMARY plug-in'), (1, 'SECONDARY Miller-Madow')):
        P('--- calls, %s ---' % tag)
        v = store[('VOYNICH', 'freq', 100)][e]
        P('(i)   K=100 freq Voynich excess %+.4f [%+.4f, %+.4f]: %s' % (v[2], v[3], v[4], 'YES' if v[2] > 0 and v[3] > 0 else 'NO'))
        fails = []
        for lang in ('LAT', 'IT'):
            for K in (50, 100, 200):
                for m in ('freq', 'cluster'):
                    vu = store[('VOYNICH', m, K)][e][4]
                    for c in ('A', 'B'):
                        cl = store[('CIPHER_%s_%s' % (c, lang), m, K)][e][3]
                        if not vu < cl:
                            fails.append('%s %s K=%s cipher(%s): Voynich hi %+.4f vs cipher lo %+.4f' % (lang, m, K, c.lower(), vu, cl))
        P('(ii)  Voynich below both planted ciphers with separation, K 50/100/200 x both methods x both languages: %s' % ('YES' if not fails else 'NO'))
        for f in fails:
            P('        fails: ' + f)
        bad = []
        for (n, m, K), r in store.items():
            if n == 'NEGATIVE' and not (r[e][3] <= 0 <= r[e][4]):
                bad.append('%s K=%s [%+.4f, %+.4f]' % (m, K, r[e][3], r[e][4]))
        P('(iii) negative control interval includes 0 at every K: %s' % ('YES' if not bad else 'NO -> controls failed'))
        for b in bad:
            P('        excludes 0: ' + b)
        P('  secondary (%s):' % tag)
        v = store[('VOYNICH', 'freq', 100)][e]
        P('  (i)   permutation p_up = %.4f -> %s' % (v[8], 'YES' if v[8] < 0.025 else 'NO'))
        f2 = []
        for lang in ('LAT', 'IT'):
            for K in (50, 100, 200):
                for m in ('freq', 'cluster'):
                    vu = store[('VOYNICH', m, K)][e][6]
                    for c in ('A', 'B'):
                        cl = store[('CIPHER_%s_%s' % (c, lang), m, K)][e][5]
                        if not vu < cl:
                            f2.append('%s %s K=%s cipher(%s)' % (lang, m, K, c.lower()))
        P('  (ii)  rescaled separation: %s%s' % ('YES' if not f2 else 'NO', '' if not f2 else ' fails: ' + '; '.join(f2)))
        b2 = ['%s K=%s p_two=%.3f' % (m, K, r[e][9]) for (n, m, K), r in store.items() if n == 'NEGATIVE' and r[e][9] < 0.05]
        P('  (iii) negative control p_two >= 0.05 everywhere: %s%s' % ('YES' if not b2 else 'NO -> controls failed', '' if not b2 else ' : ' + '; '.join(b2)))


def fixture_pages(chain, seed):
    rng = random.Random(seed)
    V = 1500
    w = [1 / (i + 1) for i in range(V)]
    groups = [list(range(g, V, 75)) for g in range(75)]
    gw = [[w[c] for c in g] for g in groups]
    cw = codewords()
    names = [cw[i % len(cw)] + 'e' * (i // len(cw)) + 'k' for i in range(V)]
    pages = collections.OrderedDict()
    pid = 0
    for f in range(1, 105):
        for side in 'rv':
            pid += 1
            if pid > 207:
                break
            lines = []
            for _ in range(20):
                prev = None; l = []
                for _ in range(rng.randint(5, 10)):
                    if chain and prev is not None and rng.random() < 0.5:
                        g = (prev * 7 + 3) % 75
                        c = rng.choices(groups[g], weights=gw[g])[0]
                    else:
                        c = rng.choices(range(V), weights=w)[0]
                    l.append(names[c]); prev = c
                lines.append(l)
            pages['f%d%s' % (f, side)] = lines
    return pages


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    mode = sys.argv[1]
    me = os.path.abspath(__file__)
    out = ['r4.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r4.py sha256: %s' % sha(me)]
    store = {}
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        cw = codewords()
        bad = [c for c in cw if SEG('qo' + c + 'aiin')[1] != c or SEG(c)[1] != c or SEG('ch' + c + 'y')[1] != c]
        out.append('codeword segmentation check: %d codewords, %d fail' % (len(cw), len(bad)))
        for chain in (True, False):
            run_corpus('FIXTURE_chain=%s' % chain, fixture_pages(chain, 77), out, store)
        neg = shuffle_cores_globally(fixture_pages(True, 77), 6161)
        run_corpus('FIXTURE_chain_globally_shuffled', neg, out, store)
        res = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, lat, it, res = sys.argv[2:6]
        try:
            reg = open(os.path.join(os.path.dirname(me), 'r4.prereg.sha256'), encoding='ascii').read().split()[0]
        except OSError:
            reg = 'MISSING'
        out += ['r4.prereg.sha256: %s' % reg, 'stub match: %s' % ('YES' if reg == sha(me) else 'NO')]
        for f in (zl, lat, it):
            out.append('data %s sha256 %s' % (os.path.basename(f), sha(f)))
        wp = parse_ivtff(zl)
        cp = core_pages(wp)
        nwords = sum(len(l) for pg in wp for l in wp[pg])
        out.append('ZL pages %d, words %d' % (len(wp), nwords))
        run_corpus('VOYNICH', cp, out, store)
        run_corpus('NEGATIVE', shuffle_cores_globally(cp, 6161), out, store)
        for lang, path, mx in (('LAT', lat, None), ('IT', it, 60000)):
            stream, nw = letter_stream(path, mx)
            out.append('%s plaintext: %d words, %d letters' % (lang, nw, len(stream)))
            for c, chunk in (('A', 1), ('B', 2)):
                words, nsym = cipher_words(stream, chunk, nwords)
                out.append('CIPHER_%s_%s: %d distinct plaintext symbols -> codewords' % (c, lang, nsym))
                run_corpus('CIPHER_%s_%s' % (c, lang), core_pages(layout_like(wp, words)), out, store)
        out.append('')
        calls(store, out)
    open(res, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-30:]))


if __name__ == '__main__':
    main()
