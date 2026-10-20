"""r3.py -- independent re-implementation of three lead claims (R3a, R3b, R3c).

voynich-91 (host Roach), brief SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-ACK-20261018T092528Z.
The lead's values were withheld from this session, so the analysis is blind.

DATA
  ZL3b-n.txt (voynich.nu), the same file as r1/r2. Paragraph loci only (locus type P).
  IVTFF cleaning as in r1/r2 prep.py (rules V1-V14):
    comments dropped; <!..> <%> <$> <@..> removed; <-> and <~> become word breaks;
    [a:b] -> a; braces and ' removed; @NNN; -> one private character per code;
    '?' kept; '.' and ',' are both word separators.
  A line is one IVTFF locus line; a page is the IVTFF page id.
SPLIT
  pages = sorted(page ids with P text) (plain Python string sort), then
  random.Random(20261017).shuffle(pages). The first 166 pages are training, the
  rest are held-out. The total is reported; the brief expects 207.
SEGMENTATION (fixed rule, the brief's suggestion adopted unchanged)
  prefix = longest match at the word start from {qo,q,o,y,d,s,l,r,ch,sh}, else '' (empty);
  suffix = longest match at the end of the REMAINDER after the prefix is removed, from
           {aiin,ain,iin,in,dy,edy,eey,ey,y,ol,al,or,ar,am,m,g,l,r,s}, else '';
  core   = whatever remains, possibly ''.
  The empty prefix and the empty suffix are ordinary symbols.
R3a  prefix-stream order
  Tokens scored: the prefixes of words at line position >= 2 (each has a previous
  word in the same line). Unigram model: Witten-Bell interpolation of the training
  counts of those tokens with a uniform distribution over the prefix alphabet
  (10 prefixes + empty = 11). Bigram model: Witten-Bell, history = previous word's
  prefix, backed off to that unigram. Both are fitted on training pages only.
  Gain = mean over held-out tokens of [bits_unigram - bits_bigram].
  Interval: 500 draws, each a random 80 % (round) of the held-out pages without
  replacement, with the gain recomputed (models fixed); 2.5 / 97.5 percentiles.
  PASS if gain >= 0.05 bits and lower bound > 0.
R3b  affixes depend on the core
  Every word. Unconditional model: Witten-Bell over (prefix, suffix) pairs, with a
  uniform base over 11 x 20 = 220 pairs. Conditional model: Witten-Bell with history
  = the word's own core, backed off to the unconditional model. Fitted on training.
  Gain = mean over held-out words of [bits_uncond - bits_cond]. Interval as in R3a.
  PASS if gain > 0.5 bits and lower bound > 0.
R3c  word length within a line versus across a line break
  x = word length in transcribed characters (each @-code and '?' counts 1).
  Within pairs: adjacent words in a line. Cross pairs: (last word of line n, first
  word of line n+1) for consecutive P lines of the same page in file order.
  Moran I over a pair set E: [sum_E (xa-m)(xb-m) / |E|] / [sum_W (x-m)^2 / |W|], with
  m and W = all words of the pages in the sample.
  Null: 200 within-line shuffles of word order (line membership kept), applied once;
  for each sample, null I = mean over the 200 shuffles on the same pages.
  Excess = I_obs - null mean. Primary sample: all pages. Interval: 500 draws of
  80 % of pages without replacement. Secondary: held-out pages only.
  Call "within-line only" if within lower bound > 0 AND the cross interval includes
  0 or lies below 0. Any other pattern is reported as it is.
REFERENCES (context only, no pass/fail)
  Latin prose: Caesar, De Bello Gallico V-VIII (Project Gutenberg #18837).
  Italian prose: Manzoni, I promessi sposi (PG #45334), first 60,000 words.
  Text between the *** START / *** END markers, one Gutenberg line = one line.
  Normalisation: NFD, combining marks dropped, lowercased, every non-letter becomes
  a space; empty lines dropped. Pages = consecutive blocks of 30 lines, ids
  zero-padded; the same sort, shuffle and seed; training = first int(N*166/207).
  Affixes are frequency-defined on the training words:
    prefixes = the 10 most common initial bigrams (words of length >= 2);
    suffixes = the 20 most common final strings of length 1-4 that leave at least
               one character (each word contributes each of its final strings once).
  Segmentation, R3a, R3b and R3c are then exactly as for the Voynich text
  (alphabet sizes 11 and 21).
SECONDARY (added after the fixture run showed the issue, before the freeze)
  An 80 % subsample without replacement shares most of its pages with every other
  draw, so its spread understates the full-sample uncertainty by about
  sqrt(0.2/0.8) = 0.5. In the fixture this produced a false "within-line" excess on
  the no-chain control. Each interval is therefore also reported rescaled:
  est + sqrt(k/(n-k)) * (q - median of draws), with k = pages per draw.
  R3c also reports the null sd and a one-sided permutation p over the 200 shuffles,
  p = (1 + #{null >= obs}) / 201 (cross: two-sided on |excess|).
  Primary calls follow the brief (unscaled). Secondary calls use the rescaled interval.
SEEDS  split 20261017; R3a/R3b intervals 3101; R3c null 3102; R3c intervals 3103.

MODES
  python -I r3.py fixture OUTDIR       synthetic check: a planted first-order prefix chain
                                       (with core-dependent suffixes) and a no-chain control
  python -I r3.py real ZL LAT IT OUT   the real run; prints the self-hash and the
                                       r3.prereg.sha256 match at the top of OUT
"""
import sys, os, re, math, random, hashlib, datetime, unicodedata, collections

PREFIXES = ['qo', 'q', 'o', 'y', 'd', 's', 'l', 'r', 'ch', 'sh']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eey', 'ey', 'y', 'ol', 'al', 'or', 'ar',
            'am', 'm', 'g', 'l', 'r', 's']
N_TRAIN = 166
DRAWS = 500
NULL_REPS = 200


# ---------------------------------------------------------------- parsing
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
    """-> OrderedDict page -> list of lines (each a list of words), paragraph loci only."""
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


def norm_ref_words(text):
    t = unicodedata.normalize('NFD', text)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
    t = ''.join(c if unicodedata.category(c).startswith('L') else ' ' for c in t)
    return t.split()


def parse_gutenberg(path, max_words=None, block=30):
    txt = open(path, encoding='utf-8').read().splitlines()
    i0 = next(i for i, l in enumerate(txt) if l.startswith('*** START'))
    i1 = next(i for i, l in enumerate(txt) if l.startswith('*** END'))
    lines, n = [], 0
    for l in txt[i0 + 1:i1]:
        w = norm_ref_words(l)
        if not w:
            continue
        if max_words is not None and n >= max_words:
            break
        lines.append(w); n += len(w)
    pages = collections.OrderedDict()
    for i in range(0, len(lines), block):
        pages['p%05d' % (i // block)] = lines[i:i + block]
    return pages


def split_pages(pages, n_train=None):
    ids = sorted(pages)
    random.Random(20261017).shuffle(ids)
    if n_train is None:
        n_train = N_TRAIN
    return ids[:n_train], ids[n_train:]


# ---------------------------------------------------------------- segmentation
def make_seg(prefixes, suffixes):
    P = sorted(prefixes, key=len, reverse=True)
    S = sorted(suffixes, key=len, reverse=True)

    def seg(w):
        p = next((x for x in P if w.startswith(x)), '')
        rest = w[len(p):]
        s = next((x for x in S if rest.endswith(x) and len(x) <= len(rest)), '')
        core = rest[:len(rest) - len(s)]
        return p, core, s
    return seg


def freq_affixes(pages, train):
    ini, fin = collections.Counter(), collections.Counter()
    for pg in train:
        for l in pages[pg]:
            for w in l:
                if len(w) >= 2:
                    ini[w[:2]] += 1
                for k in range(1, min(4, len(w) - 1) + 1):
                    fin[w[-k:]] += 1
    pre = [x for x, _ in sorted(ini.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]
    suf = [x for x, _ in sorted(fin.items(), key=lambda kv: (-kv[1], kv[0]))[:20]]
    return pre, suf


# ---------------------------------------------------------------- models
class WB:
    """Witten-Bell: P(w|h) = (c(h,w) + T(h) * lower(w)) / (c(h) + T(h)); unseen h -> lower."""

    def __init__(self, lower):
        self.lower = lower
        self.c = collections.defaultdict(collections.Counter)

    def add(self, h, w):
        self.c[h][w] += 1

    def prob(self, h, w):
        ch = self.c.get(h)
        if not ch:
            return self.lower(w)
        n = sum(ch.values()); T = len(ch)
        return (ch.get(w, 0) + T * self.lower(w)) / (n + T)


def wb_unigram(counter, vsize):
    n = sum(counter.values()); T = len(counter)
    return lambda w: (counter.get(w, 0) + T / vsize) / (n + T)


def pct(xs, q):
    xs = sorted(xs); pos = (len(xs) - 1) * q; lo = int(math.floor(pos)); hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def interval(per_page, held, seed):
    """per_page: page -> (sum_diff, n). Gain on all held-out pages + 80 % page-subsample interval."""
    tot = sum(per_page[p][0] for p in held); n = sum(per_page[p][1] for p in held)
    k = int(round(0.8 * len(held)))
    rng = random.Random(seed)
    gs = []
    for _ in range(DRAWS):
        sub = rng.sample(held, k)
        a = sum(per_page[p][0] for p in sub); b = sum(per_page[p][1] for p in sub)
        gs.append(a / b if b else 0.0)
    g = tot / n; f = math.sqrt(k / (len(held) - k)); med = pct(gs, 0.5)
    return g, pct(gs, 0.025), pct(gs, 0.975), n, g + f * (pct(gs, 0.025) - med), g + f * (pct(gs, 0.975) - med)


def r3a(pages, train, held, seg, n_pre):
    ctr = collections.Counter()
    pairs_tr = []
    for pg in train:
        for l in pages[pg]:
            ps = [seg(w)[0] for w in l]
            for a, b in zip(ps, ps[1:]):
                ctr[b] += 1; pairs_tr.append((a, b))
    uni = wb_unigram(ctr, n_pre)
    bi = WB(uni)
    for a, b in pairs_tr:
        bi.add(a, b)
    per = {}
    for pg in held:
        d = 0.0; n = 0
        for l in pages[pg]:
            ps = [seg(w)[0] for w in l]
            for a, b in zip(ps, ps[1:]):
                d += -math.log2(uni(b)) + math.log2(bi.prob(a, b)); n += 1
        per[pg] = (d, n)
    return interval(per, held, 3101)


def r3b(pages, train, held, seg, vsize):
    ctr = collections.Counter(); obs = []
    for pg in train:
        for l in pages[pg]:
            for w in l:
                p, c, s = seg(w); ctr[(p, s)] += 1; obs.append((c, (p, s)))
    unc = wb_unigram(ctr, vsize)
    cond = WB(unc)
    for c, ps in obs:
        cond.add(c, ps)
    per = {}
    for pg in held:
        d = 0.0; n = 0
        for l in pages[pg]:
            for w in l:
                p, c, s = seg(w)
                d += -math.log2(unc((p, s))) + math.log2(cond.prob(c, (p, s))); n += 1
        per[pg] = (d, n)
    return interval(per, held, 3101)


def page_stats(lines):
    """word sums and within/cross pair sums of one page (lines in order)."""
    L = [[len(w) for w in l] for l in lines]
    sx = sum(sum(l) for l in L); sxx = sum(x * x for l in L for x in l); nw = sum(len(l) for l in L)
    wi = [0.0, 0.0, 0]  # sum xa*xb, sum(xa+xb), count
    for l in L:
        for a, b in zip(l, l[1:]):
            wi[0] += a * b; wi[1] += a + b; wi[2] += 1
    cr = [0.0, 0.0, 0]
    for l1, l2 in zip(L, L[1:]):
        a, b = l1[-1], l2[0]
        cr[0] += a * b; cr[1] += a + b; cr[2] += 1
    return (sx, sxx, nw), wi, cr


def moran(wsum, psum):
    sx, sxx, nw = wsum
    if nw == 0 or psum[2] == 0:
        return float('nan')
    m = sx / nw
    var = sxx / nw - m * m
    cov = (psum[0] - m * psum[1] + m * m * psum[2]) / psum[2]
    return cov / var


def r3c(pages, ids):
    rng = random.Random(3102)
    obs = {pg: page_stats(pages[pg]) for pg in ids}
    nulls = {pg: [] for pg in ids}
    for _ in range(NULL_REPS):
        for pg in ids:
            sh = []
            for l in pages[pg]:
                l2 = list(l); rng.shuffle(l2); sh.append(l2)
            _, wi, cr = page_stats(sh)
            nulls[pg].append((wi, cr))

    def agg(sample):
        ws = [sum(obs[p][0][i] for p in sample) for i in range(3)]
        out = {}
        for j, key in ((1, 'within'), (2, 'cross')):
            ps = [sum(obs[p][j][i] for p in sample) for i in range(3)]
            io = moran(ws, ps)
            nl = []
            for r in range(NULL_REPS):
                pr = [sum(nulls[p][r][j - 1][i] for p in sample) for i in range(3)]
                nl.append(moran(ws, pr))
            mu = sum(nl) / len(nl)
            sd = (sum((x - mu) ** 2 for x in nl) / (len(nl) - 1)) ** 0.5
            if key == 'within':
                pv = (1 + sum(1 for x in nl if x >= io)) / (1 + len(nl))
            else:
                pv = (1 + sum(1 for x in nl if abs(x - mu) >= abs(io - mu))) / (1 + len(nl))
            out[key] = (io, mu, io - mu, sd, pv)
        return out

    full = agg(ids)
    k = int(round(0.8 * len(ids)))
    drng = random.Random(3103)
    ex = {'within': [], 'cross': []}
    for _ in range(DRAWS):
        a = agg(drng.sample(ids, k))
        for key in ex:
            ex[key].append(a[key][2])
    res = {}
    f = math.sqrt(k / (len(ids) - k))
    for key in ('within', 'cross'):
        io, mu, exs, sd, pv = full[key]
        lo, hi, med = pct(ex[key], 0.025), pct(ex[key], 0.975), pct(ex[key], 0.5)
        res[key] = (io, mu, exs, lo, hi, exs + f * (lo - med), exs + f * (hi - med), sd, pv)
    return res


# ---------------------------------------------------------------- reporting
def analyse(name, pages, train, held, seg, n_pre, n_suf, out, ids_c=None, c_label='all pages'):
    P = out.append
    nw = sum(len(l) for pg in pages for l in pages[pg])
    P('== %s : pages %d (train %d, held-out %d), lines %d, words %d' % (
        name, len(pages), len(train), len(held), sum(len(pages[p]) for p in pages), nw))
    g, lo, hi, n, rlo, rhi = r3a(pages, train, held, seg, n_pre)
    a_pass = g >= 0.05 and lo > 0
    P('R3a prefix-stream gain  %+.4f bits/prefix  95%% [%+.4f, %+.4f]  rescaled [%+.4f, %+.4f]  n=%d  -> %s (rescaled: %s)' % (
        g, lo, hi, rlo, rhi, n, 'PASS' if a_pass else 'FAIL', 'PASS' if g >= 0.05 and rlo > 0 else 'FAIL'))
    g, lo, hi, n, rlo, rhi = r3b(pages, train, held, seg, n_pre * n_suf)
    b_pass = g > 0.5 and lo > 0
    P('R3b affix|core gain     %+.4f bits/word    95%% [%+.4f, %+.4f]  rescaled [%+.4f, %+.4f]  n=%d  -> %s (rescaled: %s)' % (
        g, lo, hi, rlo, rhi, n, 'PASS' if b_pass else 'FAIL', 'PASS' if g > 0.5 and rlo > 0 else 'FAIL'))
    res = {}
    for label, ids in ((c_label, ids_c if ids_c is not None else list(pages)), ('held-out pages', held)):
        c = r3c(pages, ids)
        res[label] = c
        for key in ('within', 'cross'):
            io, mu, exs, lo, hi, rlo, rhi, sd, pv = c[key]
            P('R3c [%s] %-6s Moran I obs %+.4f null %+.4f (sd %.4f) excess %+.4f  95%% [%+.4f, %+.4f]  rescaled [%+.4f, %+.4f]  perm p=%.4f' % (
                label, key, io, mu, sd, exs, lo, hi, rlo, rhi, pv))
        for tag, i, j in (('call', 3, 4), ('rescaled call', 5, 6)):
            w_lo = c['within'][i]; c_lo, c_hi = c['cross'][i], c['cross'][j]
            if w_lo > 0 and (c_lo <= 0 <= c_hi or c_hi < 0):
                call = 'within-line only'
            elif w_lo > 0 and c_lo > 0:
                call = 'both within-line and cross-line excess above 0'
            elif w_lo <= 0 and c_lo > 0:
                call = 'cross-line only'
            else:
                call = 'no within-line excess (interval includes or lies below 0)'
            P('R3c [%s] %s: %s' % (label, tag, call))
    return a_pass, b_pass, res


def write_fixture(path, chain, seed):
    rng = random.Random(seed)
    cores = ['k', 't', 'p', 'f', 'ckh', 'cth', 'kt', 'tp']
    pre = PREFIXES + ['']
    suf = SUFFIXES + ['']
    succ = {p: pre[(i + 3) % len(pre)] for i, p in enumerate(pre)}
    favs = {c: suf[(i * 3) % len(suf)] for i, c in enumerate(cores)}
    lines = ['#=IVTFF Eva- 2.0 M 5', '# synthetic fixture chain=%s' % chain]
    pid = 0
    for f in range(1, 105):
        for side in 'rv':
            pid += 1
            if pid > 207:
                break
            pg = 'f%d%s' % (f, side)
            lines.append('<%s>      <! $Q=A $L=%s $H=1>' % (pg, 'A' if pid % 2 else 'B'))
            for ln in range(1, 21):
                ws = []; prev = None
                for _ in range(rng.randint(5, 10)):
                    if chain and prev is not None and rng.random() < 0.6:
                        p = succ[prev]
                    else:
                        p = rng.choice(pre)
                    c = rng.choice(cores)
                    s = favs[c] if (chain and rng.random() < 0.7) else rng.choice(suf)
                    ws.append(p + c + s); prev = p
                lines.append('<%s.%d,%sP0>      %s' % (pg, ln, '@' if ln == 1 else '+', '.'.join(ws)))
    open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    mode = sys.argv[1]
    me = os.path.abspath(__file__)
    out = []
    P = out.append
    P('r3.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')))
    myhash = sha(me)
    P('r3.py sha256: %s' % myhash)
    seg = make_seg(PREFIXES, SUFFIXES)
    if mode == 'fixture':
        outdir = sys.argv[2]
        os.makedirs(outdir, exist_ok=True)
        for chain in (True, False):
            fp = os.path.join(outdir, 'fixture_%s.txt' % ('chain' if chain else 'nochain'))
            write_fixture(fp, chain, 42)
            pages = parse_ivtff(fp)
            tr, he = split_pages(pages)
            P('fixture %s sha256 %s' % (os.path.basename(fp), sha(fp)))
            analyse('FIXTURE chain=%s' % chain, pages, tr, he, seg, 11, 20, out)
        res = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, lat, it, res = sys.argv[2:6]
        regp = os.path.join(os.path.dirname(me), 'r3.prereg.sha256')
        try:
            reg = open(regp, encoding='ascii').read().split()[0]
        except OSError:
            reg = 'MISSING'
        P('r3.prereg.sha256: %s' % reg)
        P('stub match: %s' % ('YES' if reg == myhash else 'NO'))
        for f in (zl, lat, it):
            P('data %s sha256 %s' % (os.path.basename(f), sha(f)))
        P('')
        pages = parse_ivtff(zl)
        P('ZL pages with paragraph text: %d (brief expects 207)%s' % (len(pages), '' if len(pages) == 207 else '  <-- DIFFERS'))
        tr, he = split_pages(pages)
        P('held-out pages: %s' % ' '.join(sorted(he)))
        a, b, c = analyse('VOYNICH ZL3b paragraph text', pages, tr, he, seg, 11, 20, out)
        P('')
        P('CALLS (Voynich): R3a %s ; R3b %s ; R3c (all pages) %s' % (
            'PASS' if a else 'FAIL', 'PASS' if b else 'FAIL',
            [l for l in out if l.startswith('R3c [all pages] call')][-1].split('call: ')[1]))
        P('')
        P('REFERENCES (context only)')
        for name, path, mx in (('LATIN Caesar BG V-VIII (PG18837)', lat, None), ('ITALIAN Manzoni Promessi sposi (PG45334, first 60000 words)', it, 60000)):
            rp = parse_gutenberg(path, mx)
            ntr = int(len(rp) * N_TRAIN / 207)
            rtr, rhe = split_pages(rp, ntr)
            pre, suf = freq_affixes(rp, rtr)
            P('%s affixes: prefixes %s ; suffixes %s' % (name.split()[0], pre, suf))
            analyse(name, rp, rtr, rhe, make_seg(pre, suf), len(pre) + 1, len(suf) + 1, out)
    open(res, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
