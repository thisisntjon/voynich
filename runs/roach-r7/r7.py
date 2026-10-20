"""r7.py -- the line-scoped core signature under two independently designed segmenters (voynich-91, Roach; blind).

Task relayed from Skynet (Jon), 2026-10-18; reply thread SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R6-BRIEF-20261018T191702Z.
Own code only (r3-r6 lineage). No Skynet code.

CORE DEFINITIONS
  S0  the whole word (no segmentation), as a reference.
  S1  my existing segmenter. Voynich-type text: the r3 lists (prefix = longest
      match from {qo,q,o,y,d,s,l,r,ch,sh}; suffix = longest match from the r3
      list of 19, taken on the remainder; core = the rest). Natural-language
      references: the r3 frequency affixes (10 most common initial bigrams and
      20 most common final strings of length 1-4, fitted on the whole text).
  S2  NEW, a different principle: a minimum-description-length affix inducer.
      Candidates are the 25 most frequent word-initial strings (length 1-3) and
      the 25 most frequent word-final strings (length 1-4). Each must be shorter
      than the word. Starting from empty sets, candidates are added greedily
      while the total description length falls:
        DL = sum over components (prefix, core, suffix) of token entropy cost
             sum_x n_x log2(N / n_x)
           + lexicon cost sum over distinct cores and affixes of
             (len + 1) * log2(|alphabet| + 1).
      Under the current sets each word is parsed longest-prefix then
      longest-suffix, with a non-empty core required. At most 15 additions per
      side. Fitted on the whole text, unsupervised.
  Empty cores (possible under S1) are dropped from the core sequence of a line.
DATA / FOLDS
  ZL3b-n (primary), IT2a-n (second transliteration), paragraph loci, r3 cleaning.
  Leave-one-quire-out over IVTFF $Q quires with >= 50 lines (15 folds).
  References are laid out as one source line = one line, 30-line pages and 15
  contiguous pseudo-quires, truncated to the ZL word count (35,075) when longer.
MEASUREMENTS per fold, on the held-out quire's core sequences:
  (a) ORDER: cores mapped to K=100 classes (the 99 most frequent training cores
      + one pooled class; training = the other quires). Miller-Madow MI between
      adjacent in-line classes. Excess over 200 within-line shuffles.
      PASS if excess > 0 and p_up < 0.05.
  (b) R_within(1) = identity rate of adjacent in-line cores / its exact
      within-line-shuffle expectation (per line: sum c(c-1) / (m(m-1))).
      p_up from 200 within-line shuffles. PASS if R > 1 and p_up < 0.05.
  (c) D = Rw' - Rx', where both are taken against the exact within-page-shuffle
      expectation: Rw' = adjacent in-line identity rate, Rx' = identity rate of
      the pair (last core of line n, first core of line n+1) on the same page.
      p_up from 200 within-page shuffles. PASS if D > 0 and p_up < 0.05.
  (d) QUIRE LOCALITY L_q = P(same core | two tokens of quire q) /
      P(same core | two tokens of the whole book). Shuffle band = [2.5, 97.5]
      percentiles over 200 shuffles of all tokens across the book (quire sizes
      kept), reported. PASS ("about the book level") if 0.8 <= L_q <= 1.25.
  A FOLD PASSES if (a)-(d) all pass.
CALL (written before running): the signature HOLDS for a core definition if
  >= 8 of 15 folds pass. Reported per corpus and definition.
  Separately: a reference text "shows (b) and (c) together" if (b) and (c) both
  pass on >= 8 of 15 folds.
CONTROLS
  POSITIVE: a planted Voynich-layout text built with all four properties.
    Zipf(1) vocabulary of 2,000 codeword cores in 75 groups. Each line starts
    fresh (no carry across lines, so (c) holds). Each later core copies the
    previous core with probability 0.15 ((b) holds); otherwise, with
    probability 0.35, it comes from group (7*prev+3) mod 75 ((a) holds); else a
    Zipf draw. One global distribution, so (d) holds. Affixes uniform random
    from the S1 lists. It must be called HOLDS under S1.
  NEGATIVE 1: Latin prose (Caesar BG V-VIII). Must be called NOT HOLDS under every definition.
  NEGATIVE 2: a word-level Markov text, a first-order word bigram fitted on all
    of ZL (add-0.01), generated on the ZL layout with the chain continuing
    across lines. Must be called NOT HOLDS under every definition.
REFERENCES (matched size): Forme of Cury (c. 1390, recipes; PG8102): lines from
  "FOR TO MAKE GRONDEN BENES" to before "INDEX AND GLOSSARY", dropping
  footnotes, footnote continuations, all-caps headings and bracketed markers.
  Book of Common Prayer (PG29622, litany and psalter; heavy repetition): from
  "THE LITANY" on. Manzoni, I promessi sposi (PG45334).
SEEDS: 7001+ shuffles; 7101 planted; 7102 word-Markov.
MODES: python -I r7.py fixture OUTDIR | python -I r7.py real ZL IT LAT COOK BCP MANZ OUT
"""
import sys, os, re, math, random, hashlib, datetime, unicodedata, collections
import numpy as np

PREFIXES = ['qo', 'q', 'o', 'y', 'd', 's', 'l', 'r', 'ch', 'sh']
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eey', 'ey', 'y', 'ol', 'al', 'or', 'ar',
            'am', 'm', 'g', 'l', 'r', 's']
NSH = 200
K = 100
NWORDS_MATCH = 35075


def below_normal():
    try:
        import ctypes
        k = ctypes.windll.kernel32; k.SetPriorityClass(k.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


# ------------------------------------------------------------ loading
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
    return [(quire.get(pg, '?'), pg, l) for pg, ls in pages.items() for l in ls]


def norm_words(line):
    t = unicodedata.normalize('NFD', line)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
    return ''.join(c if unicodedata.category(c).startswith('L') else ' ' for c in t).split()


def gut_body(path):
    txt = open(path, encoding='utf-8').read().splitlines()
    i0 = next(i for i, l in enumerate(txt) if l.startswith('*** START'))
    i1 = next(i for i, l in enumerate(txt) if l.startswith('*** END'))
    return txt[i0 + 1:i1]


def ref_lines(kind, path):
    body = gut_body(path)
    if kind == 'cook':
        a = next(i for i, l in enumerate(body) if l.startswith('FOR TO MAKE GRONDEN BENES'))
        b = next(i for i, l in enumerate(body) if l.startswith('INDEX AND GLOSSARY'))
        out = []; in_note = False
        for l in body[a:b]:
            if re.match(r'^\[\d+\]', l):
                in_note = True; continue
            if in_note and (l.startswith('    ') or not l.strip()):
                if not l.strip():
                    in_note = False
                continue
            in_note = False
            if not l.strip() or (l.upper() == l and re.search(r'[A-Z]', l)) or '[Sidenote' in l:
                continue
            out.append(re.sub(r'\[\d+\]', ' ', l))
        body = out
    elif kind == 'bcp':
        a = next(i for i, l in enumerate(body) if l.strip() == 'THE LITANY')
        body = body[a:]
    lines = []; n = 0
    for l in body:
        w = norm_words(l)
        if not w:
            continue
        if n >= NWORDS_MATCH:
            break
        lines.append(w); n += len(w)
    pages = [lines[i:i + 30] for i in range(0, len(lines), 30)]
    out = []
    for pi, pl in enumerate(pages):
        q = 'Q%02d' % (pi * 15 // len(pages))
        for l in pl:
            out.append((q, 'p%05d' % pi, l))
    return out


# ------------------------------------------------------------ segmenters
def seg_lists(prefixes, suffixes, need_core=False):
    P = sorted(prefixes, key=len, reverse=True); S = sorted(suffixes, key=len, reverse=True)

    def seg(w):
        p = next((x for x in P if w.startswith(x) and (len(x) < len(w) or not need_core)), '')
        rest = w[len(p):]
        s = next((x for x in S if rest.endswith(x) and (len(x) < len(rest) if need_core else len(x) <= len(rest))), '')
        return p, rest[:len(rest) - len(s)], s
    return seg


def freq_affixes(words):
    ini, fin = collections.Counter(), collections.Counter()
    for w in words:
        if len(w) >= 2:
            ini[w[:2]] += 1
        for k in range(1, min(4, len(w) - 1) + 1):
            fin[w[-k:]] += 1
    return ([x for x, _ in sorted(ini.items(), key=lambda kv: (-kv[1], kv[0]))[:10]],
            [x for x, _ in sorted(fin.items(), key=lambda kv: (-kv[1], kv[0]))[:20]])


def ent_cost(cnt):
    N = sum(cnt.values())
    return sum(n * math.log2(N / n) for n in cnt.values() if n)


def mdl_affixes(words):
    types = collections.Counter(words)
    alpha = len(set(''.join(types)))
    lc = math.log2(alpha + 1)
    ini, fin = collections.Counter(), collections.Counter()
    for w, n in types.items():
        for k in range(1, min(3, len(w) - 1) + 1):
            ini[w[:k]] += n
        for k in range(1, min(4, len(w) - 1) + 1):
            fin[w[-k:]] += n
    cp = [x for x, _ in sorted(ini.items(), key=lambda kv: (-kv[1], kv[0]))[:25]]
    cs = [x for x, _ in sorted(fin.items(), key=lambda kv: (-kv[1], kv[0]))[:25]]

    def dl(P, S):
        seg = seg_lists(P, S, need_core=True)
        cpf, ccr, csf = collections.Counter(), collections.Counter(), collections.Counter()
        for w, n in types.items():
            p, c, s = seg(w)
            cpf[p] += n; ccr[c] += n; csf[s] += n
        lex = sum((len(c) + 1) * lc for c in ccr) + sum((len(a) + 1) * lc for a in P + S)
        return ent_cost(cpf) + ent_cost(ccr) + ent_cost(csf) + lex

    P, S = [], []
    cur = dl(P, S)
    for _ in range(30):
        best = None
        for side, cands in (('P', cp), ('S', cs)):
            if (side == 'P' and len(P) >= 15) or (side == 'S' and len(S) >= 15):
                continue
            for c in cands:
                if c in (P if side == 'P' else S):
                    continue
                v = dl(P + [c], S) if side == 'P' else dl(P, S + [c])
                if v < cur and (best is None or v < best[0]):
                    best = (v, side, c)
        if best is None:
            break
        cur = best[0]
        (P if best[1] == 'P' else S).append(best[2])
    return P, S, cur


# ------------------------------------------------------------ measurements
def build(lines, seg):
    """-> list of (quire, page, [cores]) with empty cores dropped."""
    return [(q, pg, [c for c in (seg(w)[1] for w in l) if c != '']) for q, pg, l in lines]


def mi_mm(codes, M):
    N = len(codes)
    if N == 0:
        return float('nan')
    u, c = np.unique(codes, return_counts=True)
    cx = np.bincount(codes // M, minlength=M); cy = np.bincount(codes % M, minlength=M)
    mi = float(np.sum(c / N * np.log2(c * N / (cx[u // M] * cy[u % M]))))
    return mi + ((int((cx > 0).sum()) - 1) + (int((cy > 0).sum()) - 1) - (len(u) - 1)) / (2 * N * math.log(2))


def fold_measures(cl, q, rng):
    train = [x for x in cl if x[0] != q]; held = [x for x in cl if x[0] == q]
    # (a)
    cnt = collections.Counter(c for _, _, cs in train for c in cs)
    keep = {c: i for i, (c, _) in enumerate(sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:K - 1])}
    seqs = [[keep.get(c, K - 1) for c in cs] for _, _, cs in held]
    flat = np.array([x for s in seqs for x in s], dtype=np.int64)
    lid = np.array([i for i, s in enumerate(seqs) for _ in s])
    L = np.nonzero(lid[:-1] == lid[1:])[0] if len(flat) > 1 else np.array([], dtype=int)
    obs_a = mi_mm(flat[L] * K + flat[L + 1], K)
    bounds = []; st = 0
    for s in seqs:
        bounds.append((st, st + len(s))); st += len(s)
    na = []
    for _ in range(NSH):
        perm = flat.copy()
        for a, b in bounds:
            if b - a > 1:
                perm[a:b] = rng.permutation(perm[a:b])
        na.append(mi_mm(perm[L] * K + perm[L + 1], K))
    na = np.array(na); ex_a = obs_a - na.mean(); p_a = (1 + int((na >= obs_a).sum())) / (1 + NSH)

    # (b) within-line identity at d=1 vs exact within-line expectation
    def rate_b(lines_):
        num = 0; den = 0.0
        for cs in lines_:
            m = len(cs)
            if m < 2:
                continue
            c = collections.Counter(cs)
            e = sum(v * (v - 1) for v in c.values()) / (m * (m - 1))
            num += sum(1 for x, y in zip(cs, cs[1:]) if x == y); den += (m - 1) * e
        return num, den
    hl = [cs for _, _, cs in held]
    nb, db = rate_b(hl)
    Rb = nb / db if db > 0 else float('nan')
    pr = random.Random(int(rng.integers(1 << 30)))
    nulls_b = []
    for _ in range(NSH):
        sh = []
        for cs in hl:
            t = list(cs); pr.shuffle(t); sh.append(t)
        nulls_b.append(rate_b(sh)[0])
    p_b = (1 + sum(1 for v in nulls_b if v >= nb)) / (1 + NSH)

    # (c) Rw' - Rx' against page expectation; within-page shuffles
    bypg = collections.OrderedDict()
    for _, pg, cs in held:
        bypg.setdefault(pg, []).append(cs)

    def stat_c(pages_):
        wn = wd = xn = xd = 0.0
        for pg, ls in pages_.items():
            allc = collections.Counter(c for cs in ls for c in cs); N = sum(allc.values())
            if N < 2:
                continue
            e = sum(v * (v - 1) for v in allc.values()) / (N * (N - 1))
            for cs in ls:
                wn += sum(1 for x, y in zip(cs, cs[1:]) if x == y); wd += max(len(cs) - 1, 0) * e
            for c1, c2 in zip(ls, ls[1:]):
                if c1 and c2:
                    xn += c1[-1] == c2[0]; xd += e
        rw = wn / wd if wd else float('nan'); rx = xn / xd if xd else float('nan')
        return rw - rx, rw, rx
    Dobs, rw, rx = stat_c(bypg)
    nd = []
    for _ in range(NSH):
        sp = collections.OrderedDict()
        for pg, ls in bypg.items():
            flatp = [c for cs in ls for c in cs]; pr.shuffle(flatp); it = iter(flatp)
            sp[pg] = [[next(it) for _ in cs] for cs in ls]
        nd.append(stat_c(sp)[0])
    nd = np.array(nd, dtype=float)
    p_c = (1 + int((nd >= Dobs).sum())) / (1 + NSH)
    return {'a': (ex_a, p_a, ex_a > 0 and p_a < 0.05), 'b': (Rb, p_b, Rb > 1 and p_b < 0.05),
            'c': (Dobs, rw, rx, p_c, Dobs > 0 and p_c < 0.05)}


def quire_locality(cl, folds, seed):
    toks = [(q, c) for q, _, cs in cl for c in cs]
    qs = np.array([t[0] for t in toks]); ids = {}
    cs = np.array([ids.setdefault(t[1], len(ids)) for t in toks])

    def L(cvec):
        C = np.bincount(cvec); N = C.sum(); book = (C * (C - 1)).sum() / (N * (N - 1))
        out = {}
        for q in folds:
            c = np.bincount(cvec[qs == q]); n = c.sum()
            out[q] = ((c * (c - 1)).sum() / (n * (n - 1))) / book if n > 1 else float('nan')
        return out
    obs = L(cs)
    rng = np.random.default_rng(seed)
    nulls = [L(rng.permutation(cs)) for _ in range(NSH)]
    return {q: (obs[q], np.percentile([n[q] for n in nulls], 2.5), np.percentile([n[q] for n in nulls], 97.5),
                0.8 <= obs[q] <= 1.25) for q in folds}


def run(name, lines, seg, out, seed):
    P = out.append
    cl = build(lines, seg)
    qn = collections.Counter(q for q, _, _ in lines)
    folds = sorted(q for q, n in qn.items() if n >= 50)
    need = math.ceil(8 / 15 * len(folds))
    rng = np.random.default_rng(seed)
    loc = quire_locality(cl, folds, seed + 1)
    P('  %s: %d folds, threshold %d' % (name, len(folds), need))
    P('   fold | (a) excess p pass | (b) R_within p pass | (c) D (Rw\'/Rx\') p pass | (d) L_q [band] pass | FOLD')
    npass = 0; cnt = collections.Counter()
    for q in folds:
        m = fold_measures(cl, q, rng); d = loc[q]
        a, b, c = m['a'], m['b'], m['c']
        ok = a[2] and b[2] and c[4] and d[3]
        npass += ok; cnt['a'] += a[2]; cnt['b'] += b[2]; cnt['c'] += c[4]; cnt['d'] += d[3]; cnt['bc'] += b[2] and c[4]
        P('   %-4s | %+.4f %.3f %-5s | %.3f %.3f %-5s | %+.3f (%.3f/%.3f) %.3f %-5s | %.3f [%.3f,%.3f] %-5s | %s' % (
            q, a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2], c[3], c[4], d[0], d[1], d[2], d[3], 'PASS' if ok else 'fail'))
    holds = npass >= need
    P('   folds passing: (a) %d (b) %d (c) %d (d) %d ; (b)&(c) %d ; ALL FOUR %d of %d -> signature %s' % (
        cnt['a'], cnt['b'], cnt['c'], cnt['d'], cnt['bc'], npass, len(folds), 'HOLDS' if holds else 'NOT HOLDS'))
    print('\n'.join(out[-3:]), flush=True)
    return holds, npass, cnt, need


# ------------------------------------------------------------ synthetic texts
def codewords():
    mids = ['']
    for Lm in (1, 2, 3):
        mids += [''.join(x) for x in _prod('eaio', Lm)]
    return [a + m + b for a in 'ktpf' for m in mids for b in 'ktpf']


def _prod(alpha, Lm):
    if Lm == 0:
        yield (); return
    for x in _prod(alpha, Lm - 1):
        for c in alpha:
            yield x + (c,)


def planted(layout, seed):
    rng = random.Random(seed)
    V = 2000; cw = codewords()
    names = [cw[i % len(cw)] + 'e' * (i // len(cw)) + 'k' for i in range(V)]
    w = [1 / (i + 1) for i in range(V)]
    groups = [list(range(g, V, 75)) for g in range(75)]; gw = [[w[c] for c in g] for g in groups]
    pre = PREFIXES + ['']; suf = SUFFIXES + ['']
    out = []
    for q, pg, n in layout:
        cores = []
        for i in range(n):
            if cores and rng.random() < 0.15:
                c = cores[-1]
            elif cores and rng.random() < 0.35:
                g = (cores[-1] * 7 + 3) % 75; c = rng.choices(groups[g], weights=gw[g])[0]
            else:
                c = rng.choices(range(V), weights=w)[0]
            cores.append(c)
        out.append((q, pg, [rng.choice(pre) + names[c] + rng.choice(suf) for c in cores]))
    return out


def word_markov(source_lines, layout, seed):
    rng = random.Random(seed)
    big = collections.defaultdict(collections.Counter); uni = collections.Counter()
    prev = None
    for _, _, l in source_lines:
        for wd in l:
            uni[wd] += 1
            if prev is not None:
                big[prev][wd] += 1
            prev = wd
    vocab = list(uni); uw = [uni[v] for v in vocab]
    out = []; prev = rng.choices(vocab, weights=uw)[0]
    for q, pg, n in layout:
        l = []
        for _ in range(n):
            nx = big.get(prev)
            if nx and rng.random() < sum(nx.values()) / (sum(nx.values()) + 0.01 * len(vocab)):
                prev = rng.choices(list(nx), weights=list(nx.values()))[0]
            else:
                prev = rng.choices(vocab, weights=uw)[0]
            l.append(prev)
        out.append((q, pg, l))
    return out


def defs_for(lines, voynich_type, out, tag):
    words = [w for _, _, l in lines for w in l]
    if voynich_type:
        s1 = seg_lists(PREFIXES, SUFFIXES)
    else:
        p1, s1l = freq_affixes(words); s1 = seg_lists(p1, s1l)
        out.append('  %s S1 frequency affixes: %s ; %s' % (tag, p1, s1l))
    P2, S2, dl = mdl_affixes(words)
    out.append('  %s S2 MDL affixes (DL %.0f bits): prefixes %s ; suffixes %s' % (tag, dl, P2, S2))
    return {'S0': lambda w: ('', w, ''), 'S1': s1, 'S2': seg_lists(P2, S2, need_core=True)}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r7.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r7.py sha256: %s' % sha(me)]
    P = out.append
    res = {}
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = [('Q%02d' % (i * 15 // 207), 'f%03d' % i, r.randint(5, 10)) for i in range(207) for _ in range(20)]
        pl = planted(layout, 7101)
        src = planted(layout, 7999)
        wm = word_markov(src, layout, 7102)
        for nm, lines in (('FIX_PLANTED', pl), ('FIX_WORD_MARKOV', wm)):
            P('== %s' % nm)
            defs = defs_for(lines, True, out, nm)
            for dn in ('S1', 'S2', 'S0'):
                res[(nm, dn)] = run('%s %s' % (nm, dn), lines, defs[dn], out, 7001)
            P('')
        ok1 = res[('FIX_PLANTED', 'S1')][0]
        ok2 = not any(res[('FIX_WORD_MARKOV', d)][0] for d in ('S0', 'S1', 'S2'))
        P('FIXTURE CHECK: planted HOLDS under S1: %s ; word-Markov NOT HOLDS under all: %s ; overall %s' % (ok1, ok2, 'OK' if ok1 and ok2 else 'NOT OK'))
        rpath = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, it, lat, cook, bcp, manz, rpath = sys.argv[2:9]
        here = os.path.dirname(me)
        try:
            reg = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(here, 'r7.prereg.sha256'), encoding='ascii').read().splitlines()
                       if l.strip() and not l.startswith('#'))
        except OSError:
            reg = {}
        P('prereg r7.py %s ; stub match: %s' % (reg.get('r7.py', 'MISSING'), 'YES' if reg.get('r7.py') == sha(me) else 'NO'))
        for f in (zl, it, lat, cook, bcp, manz):
            P('data %s %s' % (f, sha(f)))
        zlines = parse_ivtff(zl); ilines = parse_ivtff(it)
        layout = [(q, pg, len(l)) for q, pg, l in zlines]
        corpora = [('VOYNICH_ZL', zlines, True), ('VOYNICH_IT', ilines, True),
                   ('PLANTED', planted(layout, 7101), True), ('WORD_MARKOV', word_markov(zlines, layout, 7102), True),
                   ('LATIN', ref_lines('plain', lat), False), ('REF_FORME_OF_CURY', ref_lines('cook', cook), False),
                   ('REF_BCP_LITANY', ref_lines('bcp', bcp), False), ('REF_MANZONI', ref_lines('plain', manz), False)]
        for nm, lines, vt in corpora:
            P('== %s: %d lines, %d words' % (nm, len(lines), sum(len(l) for _, _, l in lines)))
            defs = defs_for(lines, vt, out, nm)
            for dn in ('S0', 'S1', 'S2'):
                res[(nm, dn)] = run('%s %s' % (nm, dn), lines, defs[dn], out, 7001)
            P('')
        P('CALLS')
        for nm, _, _ in corpora:
            P('%-18s ' % nm + ' ; '.join('%s %s (%d/15)' % (d, 'HOLDS' if res[(nm, d)][0] else 'NOT HOLDS', res[(nm, d)][1]) for d in ('S0', 'S1', 'S2')))
        for nm in ('REF_FORME_OF_CURY', 'REF_BCP_LITANY', 'REF_MANZONI', 'LATIN'):
            P('%-18s (b)&(c) together: ' % nm + ' ; '.join('%s %s (%d/15)' % (d, 'YES' if res[(nm, d)][2]['bc'] >= res[(nm, d)][3] else 'no', res[(nm, d)][2]['bc']) for d in ('S0', 'S1', 'S2')))
        pos_ok = res[('PLANTED', 'S1')][0]
        neg_ok = not any(res[(n, d)][0] for n in ('LATIN', 'WORD_MARKOV') for d in ('S0', 'S1', 'S2'))
        P('Controls: positive (planted, S1) HOLDS required: %s ; negatives (Latin, word-Markov) NOT HOLDS under all required: %s' % (pos_ok, neg_ok))
        v = {d: res[('VOYNICH_ZL', d)][0] for d in ('S1', 'S2', 'S0')}
        P('VERDICT: ZL signature S1 %s, S2 %s (S0 reference %s)%s' % (
            'HOLDS' if v['S1'] else 'NOT HOLDS', 'HOLDS' if v['S2'] else 'NOT HOLDS', 'HOLDS' if v['S0'] else 'NOT HOLDS',
            '' if pos_ok and neg_ok else ' ; CONTROLS MISBEHAVED (see above)'))
    open(rpath, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-14:]))


if __name__ == '__main__':
    main()
