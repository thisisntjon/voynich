"""r11.py -- a bigger reference class for in-line reuse (b) and the cross-line drop (c). voynich-91, Roach; blind.

Queue message SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-QUEUE-20261018T202417Z, item r11.
Local import: ../r7/r7.py (frozen: loaders, S1, S2 MDL inducer, build). Own code only.

TESTS (as r7 (b) and (c)), now with 2,000 shuffles:
  (b) R_within(1) = adjacent in-line identity / its exact within-line expectation.
      PASS if R > 1 and p_up < 0.05 (2,000 within-line shuffles).
  (c) D = Rw' - Rx' (both against the exact within-page expectation; Rx' = last
      core of line n against the first core of line n+1, same page).
      PASS if D > 0 and p_up < 0.05 (2,000 within-page shuffles).
  p_up = (1 + #{null >= obs}) / 2001.
UNITS: definitions S0 (whole word) and S2 (r7 MDL inducer fitted per text).
  Voynich also gets S1 (r3 lists). Empty cores are dropped.
BLOCKS: each text is cut to at most 35,075 words (the ZL size) and split into 15
  contiguous blocks of equal line count (Voynich: its 15 quires with >= 50
  lines). Pages are 30-line pseudo-pages (Voynich: real pages).
CALL (written before running): a text "shows (b) and (c) together" under a
  definition if both pass on >= 8 of 15 blocks. Reported per text and
  definition. Headline: does any non-Voynich text show it?
CONTROLS: POSITIVE = the r7 planted text (ZL layout). Its cores are exact
  under S1, so it must show (b)&(c) under S1 (it is also reported under S0
  and S2). NEGATIVE = Caesar BG V-VIII (the r7 negative); it must not show it
  under any definition.
TEXTS (one source line = one line unless stated; start markers fixed here):
  1  Apicius, De re coquinaria (Latin recipes, critical edition, apparatus kept), PG16439, whole body
  2  Digby, The Closet ... Opened (recipes, 1669), PG16441, from "A RECEIPT TO MAKE METHEGLIN AS IT IS MADE AT LIEGE"
  3  Roget's Thesaurus (synonym list), PG10681, from the line starting "1. Existence"
  4  Culpeper, Complete Herbal (herbal entries), PG49513, from the line "AMARA DULCIS."
  5  Kalevala (Finnish verse; parallelism and refrains), PG7000, from "Ensimmäinen runo"
  6  English and Scottish Popular Ballads vol. 1 (verse with refrains), PG44969, from the line "RIDDLES WISELY EXPOUNDED"
     (REVISION 1, before the freeze: a loader-only dry run showed that only one line matches exactly; the TOC entry is formatted differently)
  7  Complete Manual of Catholic Piety (litanies), PG62988, from "Litany Of The Holy Name Of Jesus."
  8  Prayers of the Middle Ages (prayers and litanies), PG48242, whole body (about 15k words)
  9  CREMMA Medii Aevi (ABBREVIATED medieval Latin; real manuscript lines): all
     21 MSS, the raw *.xml (not chocomufin), MainZone/DefaultLine lines. Words:
     NFC, lowercase, keep letters + combining marks + abbreviation signs; other
     characters become spaces.
  10 Hebrew Bible, Genesis + Exodus, UNVOWELLED: WLC (openscriptures/morphhb
     Gen.xml, Exod.xml); <w> text with '/' removed and all combining marks
     (points, accents) dropped; one verse = one line.
  11 Dante, Commedia (Italian verse), PG1000, the r1 line rules.
  Text normalisation for 1-8 and 11: NFD, marks dropped, lowercase, non-letters become spaces.
PARALLEL: (text, definition) jobs in a pool of up to 12 processes at below-normal priority.
MODES: python -I r11.py fixture OUTDIR | python -I r11.py real ROOT OUT   (ROOT = C:/Users/thisi/voynich-replication)
"""
import sys, os, re, math, random, hashlib, datetime, unicodedata, collections, importlib.util
import xml.etree.ElementTree as ET
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
R7PATH = os.path.normpath(os.path.join(HERE, '..', 'r7', 'r7.py'))
_spec = importlib.util.spec_from_file_location('r7', R7PATH)
r7 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r7)
NSH = 2000; NMAX = 35075; WORKERS = 12
KEEP_EXTRA = set('\u204a\ua76f\ua770\ua751\ua753\ua757\ua759\ua75b\u1e9c\u0142\u0127')


# ------------------------------------------------------------ loaders
def gut_lines(path, start=None, nth=1):
    body = r7.gut_body(path)
    i0 = 0
    if start is not None:
        hits = [i for i, l in enumerate(body) if (start(l))]
        if len(hits) < nth:
            raise SystemExit('start marker not found in %s' % path)
        i0 = hits[nth - 1]
    return [w for w in (r7.norm_words(l) for l in body[i0:]) if w]


def cremma_lines(root):
    lines = []
    data = os.path.join(root, 'dl_CREMMA', 'data')
    for ms in sorted(os.listdir(data)):
        for f in sorted(x for x in os.listdir(os.path.join(data, ms)) if x.endswith('.xml') and not x.endswith('.chocomufin.xml')):
            raw = open(os.path.join(data, ms, f), 'rb').read()
            if b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:
                raise SystemExit('DTD in ' + f)
            rt = ET.fromstring(raw); ns = rt.tag.split('}')[0] + '}'
            lab = {e.get('ID'): e.get('LABEL') for e in rt.iter(ns + 'OtherTag')}
            for b in rt.iter(ns + 'TextBlock'):
                if 'MainZone' not in [lab.get(x, x) for x in (b.get('TAGREFS') or '').split()]:
                    continue
                for tl in b.iter(ns + 'TextLine'):
                    ll = [lab.get(x, x) for x in (tl.get('TAGREFS') or '').split()]
                    if ll and 'DefaultLine' not in ll:
                        continue
                    t = unicodedata.normalize('NFC', ' '.join(s.get('CONTENT', '') for s in tl.iter(ns + 'String'))).lower()
                    t = ''.join(c if (unicodedata.category(c)[0] in 'LM' or c in KEEP_EXTRA) else ' ' for c in t)
                    w = t.split()
                    if w:
                        lines.append(w)
    return lines


def hebrew_lines(paths):
    lines = []
    for p in paths:
        raw = open(p, 'rb').read()
        if b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:
            raise SystemExit('DTD in ' + p)
        rt = ET.fromstring(raw); ns = rt.tag.split('}')[0] + '}'
        for v in rt.iter(ns + 'verse'):
            ws = []
            for w in v.iter(ns + 'w'):
                t = unicodedata.normalize('NFD', (w.text or '').replace('/', ''))
                t = ''.join(c for c in t if '\u05d0' <= c <= '\u05ea')
                if t:
                    ws.append(t)
            if ws:
                lines.append(ws)
    return lines


def dante_lines(path):
    body = r7.gut_body(path)
    j = next(i for i, l in enumerate(body) if l.strip() == 'Canto I')
    out = []
    for l in body[j:]:
        s = l.strip()
        if not s or s.lower() in ('inferno', 'purgatorio', 'paradiso') or re.match(r'^Canto [IVXLC]+\.?$', s):
            continue
        w = r7.norm_words(s)
        if w:
            out.append(w)
    return out


def blocks(lines):
    """truncate to NMAX words, 30-line pages, 15 equal-line blocks -> (block, page, words)."""
    out, n = [], 0
    for l in lines:
        if n >= NMAX:
            break
        out.append(l); n += len(l)
    L = len(out)
    return [('B%02d' % (i * 15 // L), 'p%05d' % (i // 30), l) for i, l in enumerate(out)]


# ------------------------------------------------------------ tests
def test_bc(cl, q, seed):
    held = [x for x in cl if x[0] == q]
    rng = random.Random(seed)
    hl = [cs for _, _, cs in held]

    def nb(lines_):
        return sum(1 for cs in lines_ for x, y in zip(cs, cs[1:]) if x == y)
    den = 0.0
    for cs in hl:
        m = len(cs)
        if m >= 2:
            c = collections.Counter(cs); den += (m - 1) * sum(v * (v - 1) for v in c.values()) / (m * (m - 1))
    ob = nb(hl); Rb = ob / den if den else float('nan')
    ge = 0
    for _ in range(NSH):
        sh = []
        for cs in hl:
            t = list(cs); rng.shuffle(t); sh.append(t)
        ge += nb(sh) >= ob
    pb = (1 + ge) / (1 + NSH)
    bypg = collections.OrderedDict()
    for _, pg, cs in held:
        bypg.setdefault(pg, []).append(cs)

    def stat(pages):
        wn = wd = xn = xd = 0.0
        for ls in pages.values():
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
    D, rw, rx = stat(bypg)
    ge = 0
    for _ in range(NSH):
        sp = collections.OrderedDict()
        for pg, ls in bypg.items():
            fl = [c for cs in ls for c in cs]; rng.shuffle(fl); it = iter(fl)
            sp[pg] = [[next(it) for _ in cs] for cs in ls]
        ge += stat(sp)[0] >= D
    pc = (1 + ge) / (1 + NSH)
    return (Rb, pb, Rb > 1 and pb < 0.05), (D, rw, rx, pc, D > 0 and pc < 0.05)


def job(args):
    r7.below_normal()
    name, dn, lines, segspec = args
    if segspec[0] == 'S0':
        seg = lambda w: ('', w, '')
    elif segspec[0] == 'S1':
        seg = r7.seg_lists(r7.PREFIXES, r7.SUFFIXES)
    else:
        seg = r7.seg_lists(segspec[1], segspec[2], need_core=True)
    cl = r7.build(lines, seg)
    qn = collections.Counter(q for q, _, _ in lines)
    folds = sorted(q for q, n in qn.items() if n >= 50) if name.startswith('VOYNICH') else sorted(qn)
    rows = []; nb = nc = nbc = 0
    for fi, q in enumerate(folds):
        b, c = test_bc(cl, q, 11001 + fi)
        nb += b[2]; nc += c[4]; nbc += b[2] and c[4]
        rows.append('      %-4s (b) R %.3f p %.4f %-5s | (c) D %+.3f (Rw\' %.3f / Rx\' %.3f) p %.4f %-5s' % (q, b[0], b[1], b[2], c[0], c[1], c[2], c[3], c[4]))
    need = math.ceil(8 / 15 * len(folds))
    return name, dn, rows, nb, nc, nbc, len(folds), need


def run_all(texts, out):
    jobs = []
    for name, lines, defs in texts:
        words = [w for _, _, l in lines for w in l]
        if 'S2' in defs:
            P2, S2, dl = r7.mdl_affixes(words)
            out.append('%s: %d lines, %d words, %d blocks ; S2 MDL affixes %s ; %s' % (
                name, len(lines), len(words), len(set(q for q, _, _ in lines)), P2, S2))
        for dn in defs:
            jobs.append((name, dn, lines, (dn,) if dn != 'S2' else ('S2', P2, S2)))
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        res = list(ex.map(job, jobs))
    table = {}
    for name, dn, rows, nb, nc, nbc, nf, need in res:
        out.append('  %s %s: (b) %d, (c) %d, (b)&(c) %d of %d blocks (threshold %d) -> %s' % (
            name, dn, nb, nc, nbc, nf, need, 'SHOWS (b)&(c)' if nbc >= need else 'does not show'))
        out.extend(rows)
        table[(name, dn)] = (nbc >= need, nb, nc, nbc, nf)
    return table


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    r7.below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r11.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r11.py sha256: %s' % sha(me), 'r7.py (local import) sha256: %s' % sha(R7PATH)]
    P = out.append
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = [('Q%02d' % (i * 15 // 207), 'f%03d' % i, r.randint(5, 10)) for i in range(207) for _ in range(20)]
        pl = r7.planted(layout, 7101)
        src = r7.planted(layout, 7999)
        wm = r7.word_markov(src, layout, 7102)
        t = run_all([('FIX_PLANTED', [(('B%02d' % int(q[1:])), pg, l) for q, pg, l in pl], ['S1', 'S0']),
                     ('FIX_WORD_MARKOV', [(('B%02d' % int(q[1:])), pg, l) for q, pg, l in wm], ['S1', 'S0'])], out)
        ok = t[('FIX_PLANTED', 'S1')][0] and not t[('FIX_WORD_MARKOV', 'S1')][0] and not t[('FIX_WORD_MARKOV', 'S0')][0]
        P('FIXTURE CHECK: planted shows (b)&(c) under S1: %s ; word-Markov does not (S0,S1): %s ; overall %s' % (
            t[('FIX_PLANTED', 'S1')][0], not (t[('FIX_WORD_MARKOV', 'S1')][0] or t[('FIX_WORD_MARKOV', 'S0')][0]), 'OK' if ok else 'NOT OK'))
        rpath = os.path.join(outdir, 'results_fixture.txt')
    else:
        root, rpath = sys.argv[2:4]
        try:
            reg = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(HERE, 'r11.prereg.sha256'), encoding='ascii').read().splitlines()
                       if l.strip() and not l.startswith('#'))
        except OSError:
            reg = {}
        P('prereg r11.py %s ; stub match: %s ; r7.py entry match: %s' % (
            reg.get('r11.py', 'MISSING'), 'YES' if reg.get('r11.py') == sha(me) else 'NO', 'YES' if reg.get('../r7/r7.py') == sha(R7PATH) else 'NO'))
        J = lambda *a: os.path.join(root, *a)
        zl = r7.parse_ivtff(J('dl_ZL', 'ZL3b-n.txt'))
        layout = [(q, pg, len(l)) for q, pg, l in zl]
        T = [
            ('VOYNICH_ZL', zl, ['S0', 'S1', 'S2']),
            ('CTRL_POS_PLANTED', r7.planted(layout, 7101), ['S1', 'S0', 'S2']),
            ('CTRL_NEG_CAESAR', blocks(gut_lines(J('r3', 'dl_PG18837', 'pg18837.txt'))), ['S0', 'S2']),
            ('APICIUS_LATIN_RECIPES', blocks(gut_lines(J('r11', 'dl_PG16439', 'pg16439.txt'))), ['S0', 'S2']),
            ('DIGBY_RECIPES', blocks(gut_lines(J('r11', 'dl_PG16441', 'pg16441.txt'), lambda l: l.startswith('A RECEIPT TO MAKE METHEGLIN AS IT IS MADE AT LIEGE'))), ['S0', 'S2']),
            ('ROGET_SYNONYMS', blocks(gut_lines(J('r11', 'dl_PG10681', 'pg10681.txt'), lambda l: l.startswith('1. Existence'))), ['S0', 'S2']),
            ('CULPEPER_HERBAL', blocks(gut_lines(J('r11', 'dl_PG49513', 'pg49513.txt'), lambda l: l.strip() == 'AMARA DULCIS.')), ['S0', 'S2']),
            ('KALEVALA_VERSE', blocks(gut_lines(J('r11', 'dl_PG7000', 'pg7000.txt'), lambda l: l.strip() == 'Ensimmäinen runo')), ['S0', 'S2']),
            ('BALLADS_REFRAINS', blocks(gut_lines(J('r11', 'dl_PG44969', 'pg44969.txt'), lambda l: l.strip() == 'RIDDLES WISELY EXPOUNDED', nth=1)), ['S0', 'S2']),
            ('CATHOLIC_LITANIES', blocks(gut_lines(J('r11', 'dl_PG62988', 'pg62988.txt'), lambda l: l.strip() == 'Litany Of The Holy Name Of Jesus.')), ['S0', 'S2']),
            ('MEDIEVAL_PRAYERS', blocks(gut_lines(J('r11', 'dl_PG48242', 'pg48242.txt'))), ['S0', 'S2']),
            ('CREMMA_ABBREV_LATIN', blocks(cremma_lines(root)), ['S0', 'S2']),
            ('HEBREW_UNVOWELLED', blocks(hebrew_lines([J('r11', 'dl_WLC', 'Gen.xml'), J('r11', 'dl_WLC', 'Exod.xml')])), ['S0', 'S2']),
            ('DANTE_VERSE', blocks(dante_lines(J('dl_DANTE', 'pg1000.txt'))), ['S0', 'S2']),
        ]
        t = run_all(T, out)
        P('')
        P('CALLS')
        for name, _, defs in T:
            P('%-22s ' % name + ' ; '.join('%s %s (%d/%d)' % (d, 'SHOWS' if t[(name, d)][0] else 'no', t[(name, d)][3], t[(name, d)][4]) for d in defs))
        refs = [n for n, _, _ in T if not n.startswith(('VOYNICH', 'CTRL'))]
        shows = [n for n in refs if any(t[(n, d)][0] for d in ('S0', 'S2'))]
        pos = t[('CTRL_POS_PLANTED', 'S1')][0]; neg = not any(t[('CTRL_NEG_CAESAR', d)][0] for d in ('S0', 'S2'))
        P('Controls: positive (planted, S1) shows required: %s ; negative (Caesar) does not show required: %s' % (pos, neg))
        P('VERDICT: reference texts showing (b)&(c) on >= 8/15 blocks: %s%s' % (', '.join(shows) if shows else 'NONE', '' if pos and neg else ' ; CONTROLS MISBEHAVED'))
    open(rpath, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-22:]))


if __name__ == '__main__':
    main()
