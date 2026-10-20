"""r12.py -- word-length rhythm, two ways (voynich-91, Roach; blind). Replicates F-04 and a Voynich Ninja claim independently.

Queue message SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-QUEUE-20261018T202417Z, item r12.
Local imports: ../r11/r11.py (frozen r11 loaders) and, through it, ../r7/r7.py. Own code only.

x = word length in characters (EVA glyph characters for Voynich, as r3 cleaning;
  letters for the other texts; consonants for Hebrew). Lines and blocks are as in
  r11: Voynich = its 15 quires with >= 50 lines; others = at most 35,075 words in
  15 equal-line blocks. Paragraphs: Voynich = runs of lines starting at a locus
  whose raw text has '<%>'; Gutenberg texts = blank-line-separated groups; CREMMA
  = one page file; Hebrew = one chapter.
STATISTICS per block, each with 2,000 shuffles (seed 12001+):
  L1 POOLED : Pearson correlation of (x_i, x_i+1) over adjacent in-line pairs,
              against within-line shuffles.
  L1 LINE   : mean over lines with >= 4 words of the per-line lag-1
              autocorrelation (line mean removed), against within-line shuffles.
  PARA      : Pearson lag-1 over adjacent pairs inside a paragraph, including
              pairs across line breaks, against within-paragraph shuffles.
  XLINE     : Pearson of (last word of line n, first word of line n+1), same
              paragraph, against within-line shuffles.
  excess = obs - null mean; p_up = (1 + #{null >= obs}) / 2001;
  p_two = (1 + #{|null - mean| >= |obs - mean|}) / 2001.
  A block is POSITIVE for a statistic if excess > 0 and p_up < 0.05.
CALL (written before running), on L1 POOLED (the primary within-line measure):
  Voynich ZL is positive on >= 8 of 15 blocks, AND no natural text is positive on
  >= 8 of 15 blocks -> "Voynich-specific positive rhythm" HOLDS; otherwise
  NOT HOLDS. L1 LINE, PARA and XLINE are reported the same way. Whole-text
  values (all blocks pooled, 2,000 shuffles) are also reported.
CONTROLS: POSITIVE = a planted text on the ZL layout whose in-line word lengths
  follow an AR(1) (phi = 0.3) around the ZL mean length; it must be positive on
  >= 8 blocks. NEGATIVE = the same text with lengths shuffled within lines; it
  must not be. Planted words are runs of 'x' of the given length (length is all
  that is measured).
TEXTS: Voynich ZL, IT; Caesar (Latin prose); the 11 r11 texts (Apicius, Digby,
  Roget, Culpeper, Kalevala, Ballads, Catholic litanies, Medieval prayers, CREMMA
  abbreviated Latin, Hebrew unvowelled, Dante).
PARALLEL: texts in a pool of up to 12 processes at below-normal priority.
MODES: python -I r12.py fixture OUTDIR | python -I r12.py real ROOT OUT
"""
import sys, os, re, math, random, hashlib, datetime, collections, importlib.util
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
R11PATH = os.path.normpath(os.path.join(HERE, '..', 'r11', 'r11.py'))
_spec = importlib.util.spec_from_file_location('r11', R11PATH)
r11 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r11)
r7 = r11.r7
NSH = 2000; NMAX = 35075; WORKERS = 12


# ------------------------------------------------------------ loaders with paragraphs
def voynich_par(path):
    """-> list of (quire, page, par_id, words) for paragraph loci; a paragraph starts at a '<%>' locus."""
    hdr = re.compile(r'^<(f[0-9A-Za-z]+)>\s*(.*)$')
    loc = re.compile(r'^<(f[0-9A-Za-z]+)\.(\w+),(.)(\w)[^>]*>\s?(.*)$')
    quire = {}; out = []; par = 0
    for raw in open(path, encoding='utf-8', errors='replace'):
        s = raw.rstrip('\r\n')
        if not s or s.startswith('#'):
            continue
        m = loc.match(s)
        if m:
            if m.group(4) == 'P':
                if '<%>' in m.group(5):
                    par += 1
                w = r7.clean_ivtff_text(m.group(5))
                if w:
                    out.append((quire.get(m.group(1), '?'), m.group(1), par, w))
            continue
        m = hdr.match(s)
        if m:
            quire[m.group(1)] = dict(re.findall(r'\$(\w)=(\w+)', m.group(2))).get('Q', '?')
    return out


def gut_par(path, start=None, nth=1):
    body = r7.gut_body(path); i0 = 0
    if start is not None:
        hits = [i for i, l in enumerate(body) if start(l)]
        i0 = hits[nth - 1]
    out = []; par = 0; blank = True
    for l in body[i0:]:
        w = r7.norm_words(l)
        if not l.strip():
            blank = True; continue
        if not w:
            continue
        if blank:
            par += 1; blank = False
        out.append((par, w))
    return out


def dante_par(path):
    body = r7.gut_body(path)
    j = next(i for i, l in enumerate(body) if l.strip() == 'Canto I')
    out = []; par = 0; blank = True
    for l in body[j:]:
        s = l.strip()
        if not s:
            blank = True; continue
        if s.lower() in ('inferno', 'purgatorio', 'paradiso') or re.match(r'^Canto [IVXLC]+\.?$', s):
            blank = True; continue
        w = r7.norm_words(s)
        if w:
            if blank:
                par += 1; blank = False
            out.append((par, w))
    return out


def cremma_par(root):
    out = []; par = 0
    data = os.path.join(root, 'dl_CREMMA', 'data')
    import xml.etree.ElementTree as ET, unicodedata
    for ms in sorted(os.listdir(data)):
        for f in sorted(x for x in os.listdir(os.path.join(data, ms)) if x.endswith('.xml') and not x.endswith('.chocomufin.xml')):
            par += 1
            rt = ET.fromstring(open(os.path.join(data, ms, f), 'rb').read()); ns = rt.tag.split('}')[0] + '}'
            lab = {e.get('ID'): e.get('LABEL') for e in rt.iter(ns + 'OtherTag')}
            for b in rt.iter(ns + 'TextBlock'):
                if 'MainZone' not in [lab.get(x, x) for x in (b.get('TAGREFS') or '').split()]:
                    continue
                for tl in b.iter(ns + 'TextLine'):
                    ll = [lab.get(x, x) for x in (tl.get('TAGREFS') or '').split()]
                    if ll and 'DefaultLine' not in ll:
                        continue
                    t = unicodedata.normalize('NFC', ' '.join(s.get('CONTENT', '') for s in tl.iter(ns + 'String'))).lower()
                    t = ''.join(c if (unicodedata.category(c)[0] in 'LM' or c in r11.KEEP_EXTRA) else ' ' for c in t)
                    w = t.split()
                    if w:
                        out.append((par, w))
    return out


def hebrew_par(paths):
    import xml.etree.ElementTree as ET, unicodedata
    out = []; par = 0; lastch = None
    for p in paths:
        rt = ET.fromstring(open(p, 'rb').read()); ns = rt.tag.split('}')[0] + '}'
        for v in rt.iter(ns + 'verse'):
            ch = '.'.join(v.get('osisID').split('.')[:2])
            if ch != lastch:
                par += 1; lastch = ch
            ws = []
            for w in v.iter(ns + 'w'):
                t = unicodedata.normalize('NFD', (w.text or '').replace('/', ''))
                t = ''.join(c for c in t if 'א' <= c <= 'ת')
                if t:
                    ws.append(t)
            if ws:
                out.append((par, ws))
    return out


def blocks_par(lines):
    out, n = [], 0
    for l in lines:
        if n >= NMAX:
            break
        out.append(l); n += len(l[1])
    L = len(out)
    return [('B%02d' % (i * 15 // L), 'p%05d' % (i // 30), par, w) for i, (par, w) in enumerate(out)]


# ------------------------------------------------------------ statistics (vectorised)
def group_perm(groups, rng):
    """random permutation of positions that keeps each position inside its group id."""
    keys = groups * 4.0 + rng.random(len(groups))
    order = np.argsort(keys, kind='stable')
    perm = np.empty_like(order)
    perm[np.argsort(groups, kind='stable')] = order
    return perm


def pearson(a, b):
    if len(a) < 3:
        return float('nan')
    a = a - a.mean(); b = b - b.mean(); d = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float('nan')


def stats_block(rows, rng):
    """rows: list of (page, par, words). Returns dict stat -> (obs, null mean, excess, p_up, p_two, positive)."""
    x = []; line = []; para = []
    for li, (pg, par, w) in enumerate(rows):
        for t in w:
            x.append(len(t)); line.append(li); para.append(par)
    x = np.array(x, dtype=float); line = np.array(line); para = np.array(para)
    if len(x) < 10:
        return None
    inl = np.nonzero(line[:-1] == line[1:])[0]
    inp = np.nonzero(para[:-1] == para[1:])[0]
    xl = np.nonzero((line[:-1] != line[1:]) & (para[:-1] == para[1:]))[0]
    starts = np.r_[0, np.nonzero(np.diff(line))[0] + 1]; ends = np.r_[starts[1:], len(x)]
    big = [(s, e) for s, e in zip(starts, ends) if e - s >= 4]

    def per_line(v):
        vals = []
        for s, e in big:
            seg = v[s:e] - v[s:e].mean(); den = (seg * seg).sum()
            if den > 0:
                vals.append((seg[:-1] * seg[1:]).sum() / den)
        return float(np.mean(vals)) if vals else float('nan')

    def all4(v, vp=None):
        vp = v if vp is None else vp
        return {'L1_POOLED': pearson(v[inl], v[inl + 1]), 'L1_LINE': per_line(v),
                'XLINE': pearson(v[xl], v[xl + 1]), 'PARA': pearson(vp[inp], vp[inp + 1])}
    obs = all4(x)
    nl = {k: [] for k in obs}; npar = []
    for _ in range(NSH):
        pl = x[group_perm(line, rng)]
        r = all4(pl)
        for k in ('L1_POOLED', 'L1_LINE', 'XLINE'):
            nl[k].append(r[k])
        pp = x[group_perm(para, rng)]
        npar.append(pearson(pp[inp], pp[inp + 1]))
    nl['PARA'] = npar
    out = {}
    for k in obs:
        v = np.array(nl[k], dtype=float); v = v[~np.isnan(v)]; o = obs[k]
        if np.isnan(o) or len(v) == 0:
            out[k] = (o, float('nan'), float('nan'), 1.0, 1.0, False); continue
        mu = float(v.mean()); pu = (1 + int((v >= o).sum())) / (1 + len(v))
        pt = (1 + int((np.abs(v - mu) >= abs(o - mu)).sum())) / (1 + len(v))
        out[k] = (o, mu, o - mu, pu, pt, (o - mu) > 0 and pu < 0.05)
    return out


SK = ('L1_POOLED', 'L1_LINE', 'PARA', 'XLINE')


def text_job(args):
    r7.below_normal()
    name, rows, seed, vfold = args
    rng = np.random.default_rng(seed)
    qn = collections.Counter(q for q, _, _, _ in rows)
    folds = sorted(q for q, n in qn.items() if n >= 50) if vfold else sorted(qn)
    lines_out = []; pos = collections.Counter()
    for q in folds:
        st = stats_block([(pg, par, w) for qq, pg, par, w in rows if qq == q], rng)
        if st is None:
            continue
        for k in SK:
            pos[k] += st[k][5]
        lines_out.append('      %-4s ' % q + ' | '.join('%s %+.4f (p %.4f) %s' % (k, st[k][2], st[k][3], 'POS' if st[k][5] else '-') for k in SK))
    allst = stats_block([(pg, par, w) for qq, pg, par, w in rows if qq in folds], rng)
    return name, len(folds), pos, lines_out, allst


def run(texts, out):
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        res = list(ex.map(text_job, texts))
    table = {}
    for name, nf, pos, lines_out, allst in res:
        need = math.ceil(8 / 15 * nf)
        out.append('  %s: %d blocks ; positive blocks: %s (threshold %d)' % (name, nf, ', '.join('%s %d' % (k, pos[k]) for k in SK), need))
        out.append('    whole text: ' + ' | '.join('%s obs %+.4f null %+.4f excess %+.4f p_up %.4f p_two %.4f' % (k, *allst[k][:5]) for k in SK))
        out.extend(lines_out)
        table[name] = (pos, nf, need, allst)
    return table


def planted_rows(layout, seed, shuffle):
    rng = np.random.default_rng(seed); out = []
    for q, pg, par, n in layout:
        ls = []; z = 0.0
        for _ in range(n):
            z = 0.3 * z + rng.normal(); ls.append(max(1, int(round(5.0 + 1.6 * z))))
        if shuffle:
            rng.shuffle(ls)
        out.append((q, pg, par, ['x' * k for k in ls]))
    return out


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    r7.below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r12.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r12.py sha256: %s' % sha(me), 'r11.py (local import) sha256: %s' % sha(R11PATH), 'r7.py (local import) sha256: %s' % sha(r11.R7PATH)]
    P = out.append
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = []
        for i in range(207):
            for k in range(20):
                layout.append(('Q%02d' % (i * 15 // 207), 'f%03d' % i, i * 3 + k // 7, r.randint(5, 10)))
        t = run([('FIX_PLANTED_AR', planted_rows(layout, 12101, False), 12001, True),
                 ('FIX_SHUFFLED', planted_rows(layout, 12101, True), 12002, True)], out)
        ok = t['FIX_PLANTED_AR'][0]['L1_POOLED'] >= t['FIX_PLANTED_AR'][2] and t['FIX_SHUFFLED'][0]['L1_POOLED'] < t['FIX_SHUFFLED'][2]
        P('FIXTURE CHECK: planted AR positive on >= 8: %s ; shuffled not: %s ; overall %s' % (
            t['FIX_PLANTED_AR'][0]['L1_POOLED'] >= t['FIX_PLANTED_AR'][2], t['FIX_SHUFFLED'][0]['L1_POOLED'] < t['FIX_SHUFFLED'][2], 'OK' if ok else 'NOT OK'))
        rpath = os.path.join(outdir, 'results_fixture.txt')
    else:
        root, rpath = sys.argv[2:4]
        try:
            reg = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(HERE, 'r12.prereg.sha256'), encoding='ascii').read().splitlines()
                       if l.strip() and not l.startswith('#'))
        except OSError:
            reg = {}
        P('prereg r12.py %s ; stub match: %s ; r11 entry %s ; r7 entry %s' % (
            reg.get('r12.py', 'MISSING'), 'YES' if reg.get('r12.py') == sha(me) else 'NO',
            'YES' if reg.get('../r11/r11.py') == sha(R11PATH) else 'NO', 'YES' if reg.get('../r7/r7.py') == sha(r11.R7PATH) else 'NO'))
        J = lambda *a: os.path.join(root, *a)
        zl = voynich_par(J('dl_ZL', 'ZL3b-n.txt'))
        it = voynich_par(J('dl_IT', 'IT2a-n.txt'))
        layout = [(q, pg, par, len(w)) for q, pg, par, w in zl]
        T = [('VOYNICH_ZL', zl, 12001, True), ('VOYNICH_IT', it, 12002, True),
             ('CTRL_POS_PLANTED_AR', planted_rows(layout, 12101, False), 12003, True),
             ('CTRL_NEG_SHUFFLED', planted_rows(layout, 12101, True), 12004, True),
             ('CAESAR_LATIN', blocks_par(gut_par(J('r3', 'dl_PG18837', 'pg18837.txt'))), 12005, False),
             ('APICIUS_LATIN_RECIPES', blocks_par(gut_par(J('r11', 'dl_PG16439', 'pg16439.txt'))), 12006, False),
             ('DIGBY_RECIPES', blocks_par(gut_par(J('r11', 'dl_PG16441', 'pg16441.txt'), lambda l: l.startswith('A RECEIPT TO MAKE METHEGLIN AS IT IS MADE AT LIEGE'))), 12007, False),
             ('ROGET_SYNONYMS', blocks_par(gut_par(J('r11', 'dl_PG10681', 'pg10681.txt'), lambda l: l.startswith('1. Existence'))), 12008, False),
             ('CULPEPER_HERBAL', blocks_par(gut_par(J('r11', 'dl_PG49513', 'pg49513.txt'), lambda l: l.strip() == 'AMARA DULCIS.')), 12009, False),
             ('KALEVALA_VERSE', blocks_par(gut_par(J('r11', 'dl_PG7000', 'pg7000.txt'), lambda l: l.strip() == 'Ensimmäinen runo')), 12010, False),
             ('BALLADS_REFRAINS', blocks_par(gut_par(J('r11', 'dl_PG44969', 'pg44969.txt'), lambda l: l.strip() == 'RIDDLES WISELY EXPOUNDED')), 12011, False),
             ('CATHOLIC_LITANIES', blocks_par(gut_par(J('r11', 'dl_PG62988', 'pg62988.txt'), lambda l: l.strip() == 'Litany Of The Holy Name Of Jesus.')), 12012, False),
             ('MEDIEVAL_PRAYERS', blocks_par(gut_par(J('r11', 'dl_PG48242', 'pg48242.txt'))), 12013, False),
             ('CREMMA_ABBREV_LATIN', blocks_par(cremma_par(root)), 12014, False),
             ('HEBREW_UNVOWELLED', blocks_par(hebrew_par([J('r11', 'dl_WLC', 'Gen.xml'), J('r11', 'dl_WLC', 'Exod.xml')])), 12015, False),
             ('DANTE_VERSE', blocks_par(dante_par(J('dl_DANTE', 'pg1000.txt'))), 12016, False)]
        t = run(T, out)
        P('')
        P('CALLS (positive blocks of 15 per statistic; positive = excess > 0 and p_up < 0.05)')
        for name, _, _, _ in T:
            pos, nf, need, allst = t[name]
            P('%-22s ' % name + ' ; '.join('%s %d/%d%s' % (k, pos[k], nf, '*' if pos[k] >= need else '') for k in SK))
        nat = [n for n, _, _, _ in T if not n.startswith(('VOYNICH', 'CTRL'))]
        vz = t['VOYNICH_ZL'][0]['L1_POOLED'] >= t['VOYNICH_ZL'][2]
        natpos = [n for n in nat if t[n][0]['L1_POOLED'] >= t[n][2]]
        pos_ok = t['CTRL_POS_PLANTED_AR'][0]['L1_POOLED'] >= t['CTRL_POS_PLANTED_AR'][2]
        neg_ok = t['CTRL_NEG_SHUFFLED'][0]['L1_POOLED'] < t['CTRL_NEG_SHUFFLED'][2]
        P('Voynich ZL positive on >= 8 blocks (L1_POOLED): %s ; natural texts positive on >= 8: %s' % (vz, ', '.join(natpos) if natpos else 'none'))
        P('Controls: planted AR positive required: %s ; shuffled not positive required: %s' % (pos_ok, neg_ok))
        P('VERDICT: Voynich-specific positive in-line rhythm %s%s' % ('HOLDS' if vz and not natpos else 'NOT HOLDS', '' if pos_ok and neg_ok else ' ; CONTROLS MISBEHAVED'))
    open(rpath, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-22:]))


if __name__ == '__main__':
    main()
