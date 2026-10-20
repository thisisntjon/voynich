#!/usr/bin/env python3
"""s128 real-book profile (calibration only, no Voynich data read).
Where is the depicted plant named and described inside its own chapter, and does the
'page-unique word' signature survive when only word types (as opaque ids) and positions remain?
Books: Egerton 747 Tractatus de herbis (Ventura 2009 TEI, prose, no MS lines),
Macer Floridus (verse lines), Gart der Gesundheit excerpt (German Herbarium, print lines),
Culpeper Complete Herbal (English, illustrated). Deterministic: random.Random(20261019)."""
import re, sys, json, random, unicodedata, statistics as st, hashlib
from collections import Counter, defaultdict
R = random.Random(20261019)
D = sys.argv[1] if len(sys.argv) > 1 else '.'

def norm(w):
    w = unicodedata.normalize('NFKD', w)
    w = ''.join(c for c in w if not unicodedata.combining(c)).lower()
    w = w.replace('τ', 'r').replace('þ', 's').replace('ÿ', 'y').replace('æ', 'ae').replace('œ', 'oe').replace('ſ', 's')
    w = w.replace('v', 'u').replace('j', 'i')
    return re.sub(r'[^a-z]', '', w)

def toks(s):
    return [t for t in (norm(x) for x in re.split(r'[\s\-]+', s)) if t]

STOP_HEAD = set('de das der die capitel cap capitulum the and of or et'.split()) | {
    'i','ii','iii','iiii','iu','u','ui','uii','uiii','ix','x','xi','xii','xiii','xiv','xu','xui','xuii','xuiii','xix','xx'}

# ---------- loaders: list of dict(name_words, lines=[[tok..]..]) ----------
def load_egerton():
    t = open(f'{D}/ventura.xml', encoding='utf-8').read()
    body = t[t.find('<body'):]
    out = []
    for m in re.finditer(r'<div2[^>]*>(.*?)</div2>', body, re.S):
        blk = m.group(1)
        h = re.search(r'<head>(.*?)</head>', blk, re.S)
        if not h: continue
        head = re.sub(r'<[^>]+>', ' ', h.group(1)).strip()
        if head.upper().startswith(('PROLOG','EXPLICIT','COLOPHON')) or not re.match(r'\s*\d+\.', head): continue
        txt = re.sub(r'<head>.*?</head>', ' ', blk, flags=re.S)
        txt = re.sub(r'<[^>]+>', ' ', txt).replace('&lt;', '').replace('&gt;', '')
        nw = [w for w in toks(head) if w not in STOP_HEAD]
        if not nw: continue
        tk = toks(txt)
        if len(tk) < 5: continue
        out.append(dict(head=head, name=nw, lines=[tk[i:i+8] for i in range(0, len(tk), 8)], real_lines=False))
    return out

def load_macer():
    out, cur = [], None
    for ln in open(f'{D}/macer.txt', encoding='utf-8'):
        ln = ln.rstrip('\n')
        m = re.match(r'##\s*[IVXLC]+\.?\s*(.+)', ln)
        if m:
            cur = dict(head=m.group(1).strip(), name=[w for w in toks(m.group(1)) if w not in STOP_HEAD], lines=[], real_lines=True)
            out.append(cur); continue
        if cur is None or ln.strip() in ('', 'recensere'): continue
        tk = toks(ln)
        if tk: cur['lines'].append(tk)
    return [c for c in out if c['name'] and sum(map(len, c['lines'])) >= 5]

def load_german():
    lines = open(f'{D}/german_herbarium.txt', encoding='utf-8').read().split('\n')
    out, cur = [], None
    for ln in lines:
        if re.search(r'\bcapitel\s*\.?\s*$', ln, re.I) and len(ln.split()) <= 6:
            nw = [w for w in toks(ln) if w not in STOP_HEAD and not re.fullmatch(r'(erst|ander|dritt|uiert|fünfft|funfft|sechst|sibend|acht|neunt|zehend)\w*', w)]
            cur = dict(head=ln.strip(), name=nw, lines=[], real_lines=True); out.append(cur); continue
        if cur is not None:
            tk = toks(ln)
            if tk: cur['lines'].append(tk)
    return [c for c in out if c['name'] and sum(map(len, c['lines'])) >= 5]

def load_culpeper():
    lines = open(f'{D}/culpeper.txt', encoding='utf-8').read().split('\n')
    out, cur = [], None
    for ln in lines:
        if re.fullmatch(r'\s{2,}[A-Z][A-Z ,\'’-]{2,}\.\s*', ln) and not re.search(r'CHAP|INDEX|DIRECTIONS|THE END', ln):
            nw = [w for w in toks(ln) if w not in STOP_HEAD]
            cur = dict(head=ln.strip(), name=nw, lines=[], real_lines=True); out.append(cur); continue
        if cur is not None:
            if re.search(r'\*\*\* END', ln): break
            tk = toks(ln)
            if tk: cur['lines'].append(tk)
    k = next(i for i, c in enumerate(out) if c['head'].startswith('AMARA DULCIS'))
    e = next((i for i, c in enumerate(out) if i > k and c['head'].startswith('OF THE ')), len(out))
    return [c for c in out[k:e] if c['name'] and 30 <= sum(map(len, c['lines'])) <= 5000]

# ---------- word classes (by book language) ----------
CLS = {
 'la': dict(root=r'^radi[xc]', virtue=r'^(uirtu|ualet|confer|prodest|cura|sana|medet|iuua)', prep=r'^(decoct|coqu|coct|pulu[ei]|emplast|distemp|misc|bib|fiat|fac)', complexion=r'^(calid|frigid|sicc|humid|grad)'),
 'de': dict(root=r'^(wurcz|wurtz|wurz)', virtue=r'^(krafft|kraft|tugent|hilff|hilft|gůt|gut|gesund)', prep=r'^(gesot|seud|sied|puluer|trinck|trinc|gemusch|gemüsch|pflaster)', complexion=r'^(hicz|hycz|hitz|kalt|trucken|feucht|grad)'),
 'en': dict(root=r'^roots?$', virtue=r'^(virtue|good|helps?|cures?|heals?)$'.replace('v','u'), prep=r'^(decoction|boiled|boil|powder|drunk|drink|poultice|plaister|juice)$', complexion=r'^(hot|cold|dry|moist|degree)$'),
}

def key_name(nw):
    return nw[0] if len(nw[0]) >= 4 else max(nw, key=len)

def stem_of(w): return w[:max(4, len(w) - 2)] if len(w) >= 5 else w

def analyse(book, chs, lang, N=None, window='start'):
    # truncate/subsample to page size N if asked
    C = []
    for c in chs:
        tk = [t for l in c['lines'] for t in l]
        li = [i for i, l in enumerate(c['lines']) for _ in l]
        if N and len(tk) > N:
            s = 0 if window == 'start' else R.randrange(0, len(tk) - N + 1)
            tk, li = tk[s:s+N], [x - li[s] for x in li[s:s+N]]
        C.append(dict(tk=tk, li=li, name=[key_name(c['name'])]))
    n = len(C)
    df = Counter(); tot = Counter()
    for c in C:
        cnt = Counter(c['tk']); c['cnt'] = cnt
        for w, k in cnt.items(): df[w] += 1; tot[w] += k
    res = dict(book=book, n_chapters=n, N=N, window=window)
    L = [len(c['tk']) for c in C]
    res['len_median'] = st.median(L); res['len_iqr'] = [sorted(L)[n//4], sorted(L)[3*n//4]]
    # A/B name position + recurrence
    pos, first_tok, first3, line1, never, own_rate, other_frac, share = [], 0, 0, 0, 0, [], [], []
    for c in C:
        stv = stem_of(c['name'][0])
        hit = [i for i, t in enumerate(c['tk']) if t.startswith(stv)]
        if not hit: never += 1; continue
        pos.append(hit[0] / max(1, len(c['tk'])))
        first_tok += hit[0] == 0; first3 += hit[0] < 3; line1 += c['li'][hit[0]] == 0
        own_rate.append(100 * len(hit) / len(c['tk']))
        oth = sum(1 for d in C if d is not c and any(t.startswith(stv) for t in d['cnt']))
        other_frac.append(oth / (n - 1))
        allk = sum(k for d in C for t, k in d['cnt'].items() if t.startswith(stv))
        share.append(len(hit) / allk)
    m = n - never
    res['name'] = dict(mentioned=round(m / n, 3), first_token=round(first_tok / n, 3), first3=round(first3 / n, 3),
                       line1=round(line1 / n, 3), median_first_pos_frac=round(st.median(pos), 3) if pos else None,
                       own_per100_median=round(st.median(own_rate), 2) if own_rate else None,
                       own_count_ge2=round(sum(1 for c in C if sum(t.startswith(stem_of(c['name'][0])) for t in c['tk']) >= 2) / n, 3),
                       other_chapters_frac_median=round(st.median(other_frac), 4) if other_frac else None,
                       own_share_median=round(st.median(share), 3) if share else None)
    # C word-class positions
    wc = {}
    for k, rx in CLS[lang].items():
        rr = re.compile(rx); fp = []; dec = [0] * 10; has = 0
        for c in C:
            idx = [i for i, t in enumerate(c['tk']) if rr.search(t)]
            if idx:
                has += 1; fp.append(idx[0] / len(c['tk']))
                for i in idx: dec[min(9, int(10 * i / len(c['tk'])))] += 1
        s = sum(dec) or 1
        wc[k] = dict(chapters_with=round(has / n, 3), median_first_pos_frac=round(st.median(fp), 3) if fp else None,
                     decile_share=[round(x / s, 3) for x in dec])
    res['word_classes'] = wc
    # E page-unique signature (type-only)
    def ptypes(c, strict):
        return [w for w, k in c['cnt'].items() if k >= 2 and (k / tot[w] >= (1.0 if strict else 0.9))]
    for strict in (False, True):
        key = 'pu_strict' if strict else 'pu_0.9'
        npt, fpos, name_in, earliest_is_name, earliest_in_line1 = [], [], 0, 0, 0
        for c in C:
            P = set(ptypes(c, strict)); npt.append(len(P))
            stv = stem_of(c['name'][0])
            if any(w.startswith(stv) for w in P): name_in += 1
            firsts = sorted((c['tk'].index(w), w) for w in P)
            if firsts:
                fpos.append(firsts[0][0] / len(c['tk']))
                earliest_is_name += firsts[0][1].startswith(stv)
                earliest_in_line1 += c['li'][firsts[0][0]] == 0
        res[key] = dict(types_per_chapter_median=st.median(npt), chapters_with_any=round(sum(1 for x in npt if x) / n, 3),
                        name_is_ptype=round(name_in / n, 3), earliest_ptype_is_name=round(earliest_is_name / n, 3),
                        earliest_ptype_in_line1=round(earliest_in_line1 / n, 3),
                        earliest_ptype_pos_frac_median=round(st.median(fpos), 3) if fpos else None)
    # Stolfi statistic: first token occurs on no other chapter, vs a random-position token
    def uniq(c, i): return df[c['tk'][i]] == 1
    ft = sum(uniq(c, 0) for c in C) / n
    rnd = st.mean(st.mean(uniq(c, R.randrange(len(c['tk']))) for c in C) for _ in range(50))
    ft_rec = sum(1 for c in C if df[c['tk'][0]] == 1 and c['cnt'][c['tk'][0]] >= 2) / n
    res['stolfi'] = dict(first_token_unique=round(ft, 3), random_token_unique=round(rnd, 3), first_token_unique_and_recurs=round(ft_rec, 3))
    # G detectability from ids + positions only: statistic S = share of chapters whose earliest
    # 0.9-page-unique recurring type lies in line 1 (or first 8 tokens); null = within-chapter token shuffle
    def S_stat(CC):
        hit = 0
        for c in CC:
            P = [w for w, k in c['cnt'].items() if k >= 2 and k / tot[w] >= 0.9]
            if P:
                i = min(c['tk'].index(w) for w in P)
                hit += c['li'][i] == 0
        return hit / len(CC)
    obs = S_stat(C)
    nulls = []
    for _ in range(200):
        CC = []
        for c in C:
            tk = c['tk'][:]; R.shuffle(tk); CC.append(dict(tk=tk, li=c['li'], cnt=c['cnt']))
        nulls.append(S_stat(CC))
    nulls.sort()
    res['detect'] = dict(S_obs=round(obs, 3), null_mean=round(st.mean(nulls), 3), null_q99=round(nulls[197], 3),
                         p=round((1 + sum(x >= obs for x in nulls)) / 201, 4))
    return res

def power(chs, lang, n_pages, N, reps=200):
    """Bootstrap n_pages chapters truncated to N tokens; fraction of reps where S_obs > null q99 (50 shuffles)."""
    ok = 0
    for r in range(reps):
        sub = [chs[R.randrange(len(chs))] for _ in range(n_pages)]
        # need corpus-wide df from the sample only (as for Voynich: pages of the section)
        a = analyse_small(sub, N)
        ok += a
    return round(ok / reps, 3)

def analyse_small(chs, N):
    C = []
    for c in chs:
        tk = [t for l in c['lines'] for t in l][:N]
        li = [i for i, l in enumerate(c['lines']) for _ in l][:N]
        C.append(dict(tk=tk, li=li, cnt=Counter(tk)))
    tot = Counter()
    for c in C: tot.update(c['cnt'])
    def S(CC):
        h = 0
        for c in CC:
            P = [w for w, k in c['cnt'].items() if k >= 2 and k / tot[w] >= 0.9]
            if P: h += c['li'][min(c['tk'].index(w) for w in P)] == 0
        return h / len(CC)
    o = S(C); nl = []
    for _ in range(50):
        CC = []
        for c in C:
            tk = c['tk'][:]; R.shuffle(tk); CC.append(dict(tk=tk, li=c['li'], cnt=c['cnt']))
        nl.append(S(CC))
    nl.sort(); return o > nl[48]

if __name__ == '__main__':
    books = [('egerton747_ventura', load_egerton(), 'la'), ('macer_floridus', load_macer(), 'la'),
             ('gart_german_herbarium', load_german(), 'de'), ('culpeper', load_culpeper(), 'en')]
    out = {}
    for name, chs, lang in books:
        out[name] = {'full': analyse(name, chs, lang)}
        for N in (60, 90, 120):
            out[name][f'start_N{N}'] = analyse(name, chs, lang, N=N, window='start')
        out[name]['random_window_N90'] = analyse(name, chs, lang, N=90, window='random')
        # prefix-collapsed ids (stand-in for a core equivalence): first 4 letters
        chs4 = [dict(c, lines=[[t[:4] for t in l] for l in c['lines']], name=[c['name'][0][:4]]) for c in chs]
        out[name]['prefix4_N90'] = analyse(name, chs4, lang, N=90)
        if len(chs) >= 40:
            out[name]['power'] = {f'pages{p}_N{N}': power(chs, lang, p, N, reps=100) for p in (40, 110) for N in (60, 90)}
        out[name]['heads_sample'] = [c['head'] for c in chs[:6]]
    json.dump(out, open(f'{D}/results_s128_herbal_profile.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))
