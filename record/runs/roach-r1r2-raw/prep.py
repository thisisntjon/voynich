"""prep.py -- build line-preserved corpora for the R1/R2 replication.

Independent replication session, written 2026-10-17 (clock-stamped at run time).
Reads only the downloaded text files given on the command line; never executes
anything from them. Writes corpora.json: {corpus_name: {"meta":..., "lines":[[w,...],...]}}
plus per-line page metadata for Voynich.

FIXED RULES (recorded before running)

Voynich (IVTFF 2.0, EVA), applied identically to ZL3b-n, IT2a-n, RF1b-e:
 V1  Lines starting with '#' are comments: dropped.
 V2  Page header lines '<fNNx>  <! $K=V ...>' set the current page; fields $L
     (Currier language) and $H (hand) are kept. Missing field -> '?'.
 V3  Locus lines '<page.n,Xt..>' : X = position code, t = locus type
     (P paragraph, L label, C circular, R radial). PRIMARY corpus keeps type P
     only (running text lines). A secondary corpus "ALLLOCI" keeps all types.
 V4  Inline comments '<!...>' removed (this also removes '<!@254;>' etc).
 V5  '<%>' (paragraph start), '<$>' (paragraph end), '<@...>' (inline header
     change, e.g. <@H=3>) removed.
 V6  '<->' (drawing interrupts line) and '<~>' -> word break.
 V7  Any other '<...>' tag removed (counted).
 V8  Alternative / uncertain readings '[a:b(:c)]' -> first alternative 'a'.
 V9  Ligature braces '{...}' -> braces removed, content kept. Apostrophe "'"
     (used inside braces for special forms) removed.
 V10 '@NNN;' extended-character codes -> one private symbol per distinct code
     (mapped into Unicode private-use block U+E000+NNN), i.e. a single
     character whose identity is the code. Not merged with '?'.
 V11 '?' (unreadable character) kept as a character.
 V12 Word separators: '.' always. ',' (uncertain space) treated as a word
     separator in the PRIMARY corpus; a secondary corpus "NOCOMMA" (ZL only)
     treats ',' as no space (deleted, glyphs joined).
 V13 After V4-V12, any character not in [a-z?] or the private-use block is
     deleted (counted and reported). Case: kept (one 'I' in ZL).
 V14 Empty words dropped. One transliteration line = one manuscript line.

CREMMA Medii Aevi (CREMMA-Medieval-LAT) v0.1.2, files fetched from GitHub
tag commit 9439fe33a07eeb2814fa4b94b65c280f20aa6ec1 (the commit the Zenodo
record 8407213 cites as isSupplementTo):
 L1  Fifteenth-century selection from data-registry.csv: notBefore >= 1400
     AND notAfter <= 1499.  (Expected: LaurentianusPluteus39.34, PalLat373,
     LaurentianusPluteus53.08, LaurentianusPluteus53.09, SBB_PK_Hdschr25,
     BGO-511, Latin8236.)
 L2  Genre classes fixed in advance from the registry 'Type'/'Content':
       prose      : PalLat373 (Plaoul, De Fide, scholastic),
                    LaurentianusPluteus53.08, LaurentianusPluteus53.09
                    (Donatus commentary on Terence)
       formulaic  : SBB_PK_Hdschr25 (Book of Hours), BGO-511 (penitential psalms)
       verse      : LaurentianusPluteus39.34 (Priapea), Latin8236 (Prudentius/Tibullus)
     Pools: LAT15_PROSE = the three prose MSS; LAT15_ALL = all seven.
 L3  Files used: the '*.chocomufin.xml' ALTO files (the release's own
     normalised transcription). Non-chocomufin '*.xml' are not used.
     Files containing '<!DOCTYPE' or '<!ENTITY' are refused.
 L4  Lines kept: TextLine inside a TextBlock whose TAGREFS label is
     'MainZone', and whose own TAGREFS label is 'DefaultLine' or absent.
     (Excluded: HeadingLine, InterlinearLine, DropCapitalLine, margin and
     numbering zones.) Line order: document order within page; pages in
     sorted filename order.
 L5  Line text = the CONTENT attributes of the line's String elements joined
     with a space.
 L6  Normalisation (Latin and Dante): Unicode NFD, delete combining marks
     (category Mn), lowercase, then keep characters of category L* plus
     the word signs U+204A TIRONIAN ET, U+00F7, U+223B, '&'; every other
     character (punctuation, digits, symbols) is DELETED (not replaced by a
     space). Split on whitespace; drop empty words.

Dante (Project Gutenberg #1000, 'La Divina Commedia di Dante', Italian):
 D1  Text between the '*** START' and '*** END' markers, beginning at the
     first line that is exactly 'Canto I' (start of Inferno I).
 D2  Drop blank lines, lines that are exactly a cantica name
     (Inferno/Purgatorio/Paradiso, any case) and lines matching
     '^Canto [IVXLC]+\\.?$'. Every remaining line = one verse line.
 D3  Normalisation as L6.

Usage: python -I prep.py OUT.json ZL.txt IT.txt RF.txt CREMMA_ROOT DANTE.txt
"""
import sys, re, os, json, csv, unicodedata, hashlib, collections
import xml.etree.ElementTree as ET

KEEP_EXTRA = {'⁊', '÷', '∻', '&'}


def parse_ivtff(path, keep_types=('P',), comma_is_space=True):
    stats = collections.Counter()
    deleted = collections.Counter()
    lines = []
    page = None; lang = '?'; hand = '?'
    hdr = re.compile(r'^<(f[0-9A-Za-z]+)>\s*(.*)$')
    loc = re.compile(r'^<(f[0-9A-Za-z]+)\.(\w+),(.)(\w)[^>]*>\s?(.*)$')
    with open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            s = raw.rstrip('\r\n')
            if not s or s.startswith('#'):
                continue
            m = loc.match(s)
            if m:
                pg, ln, pos, typ, txt = m.groups()
                stats['locus_lines'] += 1
                if typ not in keep_types:
                    stats['locus_dropped_type_' + typ] += 1
                    continue
                words = clean_ivtff_text(txt, comma_is_space, stats, deleted)
                if not words:
                    stats['empty_after_clean'] += 1
                    continue
                L = lang if pg == page else '?'
                H = hand if pg == page else '?'
                lines.append({'page': pg, 'line': ln, 'lang': L, 'hand': H, 'w': words})
                continue
            m = hdr.match(s)
            if m:
                page = m.group(1)
                f = dict(re.findall(r'\$(\w)=(\w+)', m.group(2)))
                lang = f.get('L', '?'); hand = f.get('H', '?')
                stats['pages'] += 1
                continue
            stats['unparsed_noncomment_lines'] += 1
    return lines, stats, deleted


def clean_ivtff_text(t, comma_is_space, stats, deleted):
    t = re.sub(r'<![^>]*>', '', t)                       # V4
    t = re.sub(r'<[%$]>', '', t)                          # V5
    t = re.sub(r'<@[^>]*>', '', t)                        # V5
    t = re.sub(r'<[-~]>', '.', t)                         # V6
    n_other = len(re.findall(r'<[^>]*>', t))
    stats['other_tags_removed'] += n_other
    t = re.sub(r'<[^>]*>', '', t)                         # V7
    t = re.sub(r'\[([^:\]]*)(?::[^\]]*)?\]', r'\1', t)    # V8
    t = t.replace('{', '').replace('}', '').replace("'", '')  # V9
    t = re.sub(r'@(\d+);', lambda m: chr(0xE000 + int(m.group(1))), t)  # V10
    t = t.replace(',', '.' if comma_is_space else '')     # V12
    out = []
    for w in t.split('.'):
        keep = []
        for ch in w:
            if ('a' <= ch <= 'z') or ch == '?' or ch == 'I' or 0xE000 <= ord(ch) <= 0xE3FF:
                keep.append(ch)
            else:
                deleted[ch] += 1                          # V13
        w2 = ''.join(keep)
        if w2:
            out.append(w2)                                # V14
    return out


def norm_words(text):
    t = unicodedata.normalize('NFD', text)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = t.lower()
    t = ''.join(c for c in t if c.isspace() or unicodedata.category(c).startswith('L') or c in KEEP_EXTRA)
    return t.split()


def alto_lines(path, stats):
    data = open(path, 'rb').read()
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:
        raise SystemExit('refusing file with DTD/entity: ' + path)
    root = ET.fromstring(data)
    ns = root.tag.split('}')[0] + '}' if root.tag.startswith('{') else ''
    labels = {}
    for el in root.iter(ns + 'OtherTag'):
        labels[el.get('ID')] = el.get('LABEL')
    out = []
    for blk in root.iter(ns + 'TextBlock'):
        bl = [labels.get(x, x) for x in (blk.get('TAGREFS') or '').split()]
        if 'MainZone' not in bl:
            stats['lines_in_nonmain_blocks'] += sum(1 for _ in blk.iter(ns + 'TextLine'))
            continue
        for tl in blk.iter(ns + 'TextLine'):
            ll = [labels.get(x, x) for x in (tl.get('TAGREFS') or '').split()]
            if ll and 'DefaultLine' not in ll:
                stats['lines_dropped_' + '+'.join(ll)] += 1
                continue
            txt = ' '.join(s.get('CONTENT', '') for s in tl.iter(ns + 'String'))
            w = norm_words(txt)
            if w:
                out.append(w)
            else:
                stats['lines_empty'] += 1
    return out


GENRE = {
    'PalLat373': 'prose', 'LaurentianusPluteus53.08': 'prose', 'LaurentianusPluteus53.09': 'prose',
    'SBB_PK_Hdschr25': 'formulaic', 'BGO-511': 'formulaic',
    'LaurentianusPluteus39.34': 'verse', 'Latin8236': 'verse',
}


def cremma(root):
    reg = list(csv.DictReader(open(os.path.join(root, 'data-registry.csv'), encoding='utf-8')))
    sel = []
    for r in reg:
        try:
            nb, na = int(r['notBefore']), int(r['notAfter'])
        except ValueError:
            continue
        if nb >= 1400 and na <= 1499:
            sel.append((r['Folder'].split('/')[-1], nb, na, r['Type'], r['Script'], r['Content']))
    corp = {}
    for folder, nb, na, typ, script, content in sel:
        if folder not in GENRE:
            raise SystemExit('selected MS without pre-registered genre: ' + folder)
        d = os.path.join(root, 'data', folder)
        files = sorted(f for f in os.listdir(d) if f.endswith('.chocomufin.xml'))
        st = collections.Counter()
        lines = []
        for f in files:
            lines.extend(alto_lines(os.path.join(d, f), st))
        corp['LAT15_' + folder] = {'meta': {'source': 'CREMMA-Medieval-LAT v0.1.2', 'folder': folder,
                                            'notBefore': nb, 'notAfter': na, 'type': typ, 'script': script,
                                            'content': content, 'genre': GENRE[folder], 'files': files,
                                            'filter_stats': dict(st)},
                                   'lines': lines}
    return corp


def dante(path):
    txt = open(path, encoding='utf-8').read().splitlines()
    i0 = next(i for i, l in enumerate(txt) if l.startswith('*** START'))
    i1 = next(i for i, l in enumerate(txt) if l.startswith('*** END'))
    body = txt[i0 + 1:i1]
    j = next(i for i, l in enumerate(body) if l.strip() == 'Canto I')
    lines = []
    for l in body[j:]:
        s = l.strip()
        if not s or s.lower() in ('inferno', 'purgatorio', 'paradiso') or re.match(r'^Canto [IVXLC]+\.?$', s):
            continue
        w = norm_words(s)
        if w:
            lines.append(w)
    return lines


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    out, zl, it, rf, croot, dpath = sys.argv[1:7]
    corpora = {}
    report = {}
    for name, p in (('ZL', zl), ('IT', it), ('RF', rf)):
        for variant, kt, cs in (('', ('P',), True), ('_ALLLOCI', ('P', 'L', 'C', 'R'), True), ('_NOCOMMA', ('P',), False)):
            if variant == '_NOCOMMA' and name != 'ZL':
                continue
            lines, st, dele = parse_ivtff(p, kt, cs)
            corpora['VOY_' + name + variant] = {'meta': {'file': os.path.basename(p), 'sha256': sha(p),
                                                          'locus_types': kt, 'comma_is_space': cs,
                                                          'stats': dict(st),
                                                          'deleted_chars': {repr(k): v for k, v in dele.items()}},
                                                 'lines': [l['w'] for l in lines],
                                                 'lang': [l['lang'] for l in lines],
                                                 'hand': [l['hand'] for l in lines],
                                                 'page': [l['page'] for l in lines]}
    corpora.update(cremma(croot))
    corpora['DANTE'] = {'meta': {'file': os.path.basename(dpath), 'sha256': sha(dpath)}, 'lines': dante(dpath)}
    json.dump(corpora, open(out, 'w', encoding='utf-8'), ensure_ascii=True)
    for k, v in corpora.items():
        n3 = sum(1 for l in v['lines'] if len(l) >= 3)
        nw = sum(len(l) for l in v['lines'])
        extra = ''
        if 'lang' in v:
            c = collections.Counter(v['lang'])
            extra = ' lang=' + ','.join('%s:%d' % kv for kv in sorted(c.items()))
        print('%-32s lines=%5d lines>=3w=%5d words=%6d%s' % (k, len(v['lines']), n3, nw, extra))
        if 'stats' in v['meta']:
            print('    stats', v['meta']['stats'])
            print('    deleted', v['meta']['deleted_chars'])
        if 'filter_stats' in v['meta']:
            print('    %s %d-%d %s files=%d filter=%s' % (v['meta']['genre'], v['meta']['notBefore'], v['meta']['notAfter'],
                                                     v['meta']['type'], len(v['meta']['files']), v['meta']['filter_stats']))


if __name__ == '__main__':
    main()
