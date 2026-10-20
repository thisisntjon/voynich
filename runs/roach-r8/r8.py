"""r8.py -- does a homophonic cipher under a per-line affix table leave the wrong core statistics? (voynich-91, Roach; blind)

Task relayed from Skynet (Jon), 2026-10-18; reply thread SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R6-BRIEF-20261018T191702Z.
Local import: ../r7/r7.py (frozen r7; its loaders, segmenters S1/S2 and fold measures are reused unchanged).

CLAIM: if plaintext units are carried in the cores through homophones while a
  per-line affix table supplies prefixes and suffixes, the cipher text has MORE
  core order than the manuscript and LESS same-core recurrence at distance 1.
CIPHER (built here; the plaintext is Latin, Caesar BG V-VIII, PG18837, as one
  stream of letters a-z after NFD, marks dropped, lowercasing, non-letters dropped)
  Core glyph alphabet G = {k,t,p,f,e,o,a,i,d}. It deliberately overlaps
  Voynich-like affix glyphs, so segmentation is not trivial.
  Codewords = all strings over G of the setting's lengths, shuffled with
  random.Random(8101); each unit gets h distinct codewords (its homophone class).
  Each cipher word picks one of its unit's homophones uniformly at random.
  Per-line affix table: each line draws T = 3 (prefix, suffix) pairs uniformly
  from (r3 prefixes + empty) x (r3 suffixes + empty). Every word of the line
  takes a pair uniformly from that table. Word = prefix + codeword + suffix.
  Layout: the ZL pages, quires and line lengths exactly, filled with the first
  35,075 cipher words, so size and folds match.
  SETTINGS (fixed before running):
    A: unit = letter,        h = 3, codeword length 2-3
    B: unit = letter,        h = 6, codeword length 2-3
    C: unit = 2-letter chunk, h = 2, codeword length 3-4
  The generator's boundaries are never used. The cipher text is re-segmented by
  S1 (r3 lists) and by S2 (r7 MDL inducer fitted on the cipher text itself).
  Voynich (ZL) is segmented by the same S1, and by S2 fitted on ZL.
MEASURES per LOQO fold (15 quires with >= 50 lines), from r7.fold_measures:
  (a) core order = Miller-Madow MI excess at K=100 over 200 within-line shuffles;
  (b) R_within(1) against the exact within-line expectation.
CALL (written before running): under a segmenter, a setting "supports" the
  claim if cipher (a) > Voynich (a) AND cipher (b) < Voynich (b) on >= 8 of 15
  folds (same quire). The claim HOLDS under that segmenter if >= 2 of the 3
  settings support it. Reported per segmenter; S1/S2 disagreement is reported
  as a result.
FIXTURE (before any real data): the Voynich slot is filled by stand-ins on a
  synthetic layout, with a synthetic plaintext (first-order random letter chain).
  REVISION 1 (after fixture run 1, before the freeze). Run 1 used the r7 planted
  text as WEAK; its core order (MI excess about +0.3) exceeded ciphers B and C,
  so it was not weak. Run 1 also showed S2 finding no suffixes on the cipher,
  which is a segmenter property the real run is meant to measure. Revised:
  Stand-in WEAK = within-line copy p = 0.15, group chain p = 0.05 (truly weak
    order), otherwise Zipf.
  The fixture pass check uses ORACLE cores (the generator's own boundaries,
  fixture only; never used in the real run): WEAK -> HOLDS, STRONG -> NOT HOLDS.
  S1/S2 fixture outcomes are reported but not required.
  Stand-in STRONG = a text with stronger order and more repetition than any
    cipher setting (copy previous core with p = 0.5, else a deterministic
    successor with p = 0.9): the claim must NOT HOLD.
MODES: python -I r8.py fixture OUTDIR | python -I r8.py real ZL LAT OUT
"""
import sys, os, math, random, hashlib, datetime, collections, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R7PATH = os.path.normpath(os.path.join(HERE, '..', 'r7', 'r7.py'))
_spec = importlib.util.spec_from_file_location('r7', R7PATH)
r7 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r7)

G = ['k', 't', 'p', 'f', 'e', 'o', 'a', 'i', 'd']
SETTINGS = [('A', 1, 3, (2, 3)), ('B', 1, 6, (2, 3)), ('C', 2, 2, (3, 4))]


def strings(lengths):
    out = []
    for L in range(lengths[0], lengths[1] + 1):
        out += [''.join(x) for x in r7._prod(G, L)]
    return out


def cipher_lines(stream, unit, h, lengths, layout, seed, oracle=False):
    units = [stream[i:i + unit] for i in range(0, len(stream) - unit + 1, unit)]
    alphabet = sorted(set(units))
    cw = strings(lengths); random.Random(8101).shuffle(cw)
    if len(alphabet) * h > len(cw):
        raise SystemExit('not enough codewords')
    homo = {u: cw[i * h:(i + 1) * h] for i, u in enumerate(alphabet)}
    rng = random.Random(seed)
    pre = r7.PREFIXES + ['']; suf = r7.SUFFIXES + ['']
    it = iter(units); out = []
    for q, pg, n in layout:
        table = [(rng.choice(pre), rng.choice(suf)) for _ in range(3)]
        l = []
        for _ in range(n):
            u = next(it); p, s = rng.choice(table); c = rng.choice(homo[u])
            l.append(c if oracle else p + c + s)
        out.append((q, pg, l))
    return out, len(alphabet)


def per_fold(lines, seg, seed):
    cl = r7.build(lines, seg)
    qn = collections.Counter(q for q, _, _ in lines)
    folds = sorted(q for q, n in qn.items() if n >= 50)
    rng = np.random.default_rng(seed)
    res = {}
    for q in folds:
        m = r7.fold_measures(cl, q, rng)
        res[q] = (m['a'][0], m['b'][0])
    return res


def compare(name, voy, cip, out):
    folds = sorted(voy)
    need = math.ceil(8 / 15 * len(folds))
    ok = 0
    out.append('   %-14s fold: cipher(a) vs voy(a) | cipher R(1) vs voy R(1) | supports' % name)
    for q in folds:
        ca, cb = cip[q]; va, vb = voy[q]
        s = (ca > va) and (cb < vb)
        ok += s
        out.append('      %-4s %+.4f vs %+.4f | %.3f vs %.3f | %s' % (q, ca, va, cb, vb, s))
    sup = ok >= need
    out.append('   %-14s folds supporting %d of %d (threshold %d) -> %s' % (name, ok, len(folds), need, 'SUPPORTS' if sup else 'does not support'))
    return sup, ok


def synth_stream(n, seed):
    rng = random.Random(seed); letters = 'abcdefghilmnopqrstuvx'
    succ = {c: letters[(i * 5 + 2) % len(letters)] for i, c in enumerate(letters)}
    s = [rng.choice(letters)]
    for _ in range(n - 1):
        s.append(succ[s[-1]] if rng.random() < 0.4 else rng.choice(letters))
    return ''.join(s)


def weak_standin(layout, seed):
    rng = random.Random(seed); V = 2000; cw = r7.codewords()
    names = [cw[i % len(cw)] + 'e' * (i // len(cw)) + 'k' for i in range(V)]
    w = [1 / (i + 1) for i in range(V)]
    groups = [list(range(g, V, 75)) for g in range(75)]; gw = [[w[c] for c in g] for g in groups]
    pre = r7.PREFIXES + ['']; suf = r7.SUFFIXES + ['']
    out = []
    for q, pg, n in layout:
        cores = []
        for _ in range(n):
            if cores and rng.random() < 0.15:
                c = cores[-1]
            elif cores and rng.random() < 0.05:
                g = (cores[-1] * 7 + 3) % 75; c = rng.choices(groups[g], weights=gw[g])[0]
            else:
                c = rng.choices(range(V), weights=w)[0]
            cores.append(c)
        out.append((q, pg, [rng.choice(pre) + names[c] + rng.choice(suf) for c in cores]))
    return out


def strong_standin(layout, seed):
    rng = random.Random(seed); cw = r7.codewords(); V = 400
    names = [cw[i] for i in range(V)]
    pre = r7.PREFIXES + ['']; suf = r7.SUFFIXES + ['']
    out = []
    for q, pg, n in layout:
        cores = []
        for _ in range(n):
            if cores and rng.random() < 0.5:
                c = cores[-1]
            elif cores and rng.random() < 0.9:
                c = (cores[-1] * 13 + 7) % V
            else:
                c = rng.randrange(V)
            cores.append(c)
        out.append((q, pg, [rng.choice(pre) + names[c] + rng.choice(suf) for c in cores]))
    return out


def run_all(voy_lines, stream, layout, out, oracle=False):
    P = out.append
    vwords = [w for _, _, l in voy_lines for w in l]
    P2, S2, dl = r7.mdl_affixes(vwords)
    P('Voynich-slot S2 MDL affixes: %s ; %s' % (P2, S2))
    vseg = {'S1': r7.seg_lists(r7.PREFIXES, r7.SUFFIXES), 'S2': r7.seg_lists(P2, S2, need_core=True)}
    sgs = ('S1', 'S2', 'ORACLE') if oracle else ('S1', 'S2')
    if oracle:
        vseg['ORACLE'] = vseg['S1']  # stand-in cores start k/t/p/f and end k: S1 recovers them exactly
    voy = {sg: per_fold(voy_lines, vseg[sg], 8201) for sg in sgs}
    support = {sg: [] for sg in sgs}
    for name, unit, h, lengths in SETTINGS:
        cl, nunits = cipher_lines(stream, unit, h, lengths, layout, 8301 + ord(name))
        cw = [w for _, _, l in cl for w in l]
        cp, cs, _ = r7.mdl_affixes(cw)
        P('Setting %s: unit=%d h=%d lengths=%s, %d plaintext units; cipher S2 MDL affixes: %s ; %s' % (name, unit, h, lengths, nunits, cp, cs))
        cseg = {'S1': r7.seg_lists(r7.PREFIXES, r7.SUFFIXES), 'S2': r7.seg_lists(cp, cs, need_core=True)}
        if oracle:
            ocl, _ = cipher_lines(stream, unit, h, lengths, layout, 8301 + ord(name), oracle=True)
        for sg in sgs:
            if sg == 'ORACLE':
                cip = per_fold(ocl, lambda w: ('', w, ''), 8202)
            else:
                cip = per_fold(cl, cseg[sg], 8202)
            sup, _ = compare('%s/%s' % (name, sg), voy[sg], cip, out)
            support[sg].append(sup)
            print('\n'.join(out[-1:]), flush=True)
    calls = {}
    for sg in sgs:
        n = sum(support[sg]); calls[sg] = n >= 2
        P('CALL %s: settings supporting %d of 3 -> claim %s' % (sg, n, 'HOLDS' if calls[sg] else 'NOT HOLDS'))
    return calls


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    r7.below_normal()
    mode = sys.argv[1]; me = os.path.abspath(__file__)
    out = ['r8.py mode=%s run at (clock): %s' % (mode, datetime.datetime.now().astimezone().isoformat(timespec='seconds')),
           'r8.py sha256: %s' % sha(me), 'r7.py (local import) sha256: %s' % sha(R7PATH)]
    P = out.append
    if mode == 'fixture':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        r = random.Random(9)
        layout = [('Q%02d' % (i * 15 // 207), 'f%03d' % i, r.randint(5, 10)) for i in range(207) for _ in range(20)]
        stream = synth_stream(200000, 8401)
        P('== FIXTURE stand-in WEAK (revision 1)')
        c1 = run_all(weak_standin(layout, 8403), stream, layout, out, oracle=True)
        P('== FIXTURE stand-in STRONG')
        c2 = run_all(strong_standin(layout, 8402), stream, layout, out, oracle=True)
        ok = c1['ORACLE'] and not c2['ORACLE']
        P('FIXTURE CHECK (ORACLE cores): WEAK -> HOLDS: %s ; STRONG -> NOT HOLDS: %s ; overall %s' % (
            c1['ORACLE'], not c2['ORACLE'], 'OK' if ok else 'NOT OK'))
        P('fixture info (not required): WEAK S1 %s S2 %s ; STRONG S1 %s S2 %s' % (c1['S1'], c1['S2'], c2['S1'], c2['S2']))
        rpath = os.path.join(outdir, 'results_fixture.txt')
    else:
        zl, lat, rpath = sys.argv[2:5]
        try:
            reg = dict((l.split()[1], l.split()[0]) for l in open(os.path.join(HERE, 'r8.prereg.sha256'), encoding='ascii').read().splitlines()
                       if l.strip() and not l.startswith('#'))
        except OSError:
            reg = {}
        P('prereg r8.py %s ; stub match: %s ; r7.py entry match: %s' % (
            reg.get('r8.py', 'MISSING'), 'YES' if reg.get('r8.py') == sha(me) else 'NO', 'YES' if reg.get('../r7/r7.py') == sha(R7PATH) else 'NO'))
        for f in (zl, lat):
            P('data %s %s' % (f, sha(f)))
        zlines = r7.parse_ivtff(zl)
        layout = [(q, pg, len(l)) for q, pg, l in zlines]
        body = r7.gut_body(lat)
        stream = ''.join(''.join(r7.norm_words(l)) for l in body)
        stream = ''.join(c for c in stream if 'a' <= c <= 'z')
        P('Latin letter stream: %d letters' % len(stream))
        calls = run_all(zlines, stream, layout, out)
        P('')
        P('CALLS')
        P('S1: claim %s ; S2: claim %s ; segmenters %s' % ('HOLDS' if calls['S1'] else 'NOT HOLDS', 'HOLDS' if calls['S2'] else 'NOT HOLDS',
                                                         'AGREE' if calls['S1'] == calls['S2'] else 'DISAGREE'))
        P('VERDICT: S1 %s, S2 %s' % ('HOLDS' if calls['S1'] else 'NOT HOLDS', 'HOLDS' if calls['S2'] else 'NOT HOLDS'))
    open(rpath, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('\n'.join(out[-8:]))


if __name__ == '__main__':
    main()
