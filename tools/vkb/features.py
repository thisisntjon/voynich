"""VKB module: folio_features (per-folio text statistics) and finding_links (graph related / decisions /
rests_on links). Schema, every feature and its formula: tools/vkb/README.md ("folio_features").

Inputs (read-only): the `tokens`, `loci` and `folios` tables written by manuscript.py earlier in the same
build, workflow/FINDINGS-GRAPH.yaml (through evidence.load_graph, the same yaml reader evidence.py uses).
Glyphs: corpora.to_glyphs(word, corpora.GLYPHS), the rule manuscript.py uses for tokens.n_glyphs.
All statistics are written fresh here (D-071: no run script is imported). Text features use paragraph (P)
loci only; label features use all loci. Seeds are fixed per (translit, folio, feature), so a rebuild gives the
same numbers. Nothing here is a filed measurement: these are descriptive inputs for exploratory queries.
"""
import math, os, sys, zlib
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, rel, create, insert  # noqa: E402

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

N_SUB = 50        # size-matched statistics: tokens per subsample (folios with fewer P tokens get NULL)
R_SUB = 50        # subsamples per size-matched statistic
R_SHUF = 200      # within-line shuffles for rhythm_excess
TOP_AFFIX = 10    # slot prefixes / suffixes ranked on all ZL3b P tokens
TOP_EDGE = 6      # line-initial first glyphs / line-final last glyphs ranked on ZL3b P lines
SRC = "tools/vkb/features.py"


def seed(*parts):
    return zlib.crc32("|".join(map(str, parts)).encode())


def entropy(counter):
    n = sum(counter.values())
    return -sum(c / n * math.log2(c / n) for c in counter.values() if c) if n else None


def h1_h2(words):
    """h1: plug-in entropy of glyph unigrams (bits). h2: conditional entropy H(next | previous) of glyph bigrams
    inside words padded with a boundary symbol on both ends (order-free across words)."""
    uni, big, left = Counter(), Counter(), Counter()
    for w in words:
        uni.update(w)
        s = "_" + w + "_"
        for a, b in zip(s, s[1:]):
            big[(a, b)] += 1
            left[a] += 1
    if not uni:
        return None, None
    nb = sum(big.values())
    h2 = -sum(c / nb * math.log2(c / left[a]) for (a, _), c in big.items())
    return entropy(uni), h2


def rw1(lines):
    """lines: lists of cores. Returns (Rw1 vs within-folio permutation, Rw1 vs within-line shuffle, n pairs).
    Both nulls are exact expectations (no Monte Carlo): pairs with an empty core are excluded."""
    obs = pairs = 0
    exp_line = 0.0
    folio = Counter()
    for ln in lines:
        cs = [c for c in ln if c]
        folio.update(cs)
        for a, b in zip(ln, ln[1:]):
            if a and b:
                pairs += 1
                obs += a == b
        L = len(cs)
        if L >= 2:  # within-line shuffle: P(two given slots share a core) = sum m(m-1) / L(L-1)
            m = Counter(cs)
            exp_line += (len([1 for a, b in zip(ln, ln[1:]) if a and b])) * \
                sum(v * (v - 1) for v in m.values()) / (L * (L - 1))
    M = sum(folio.values())
    if pairs == 0 or M < 2:
        return None, None, pairs
    p_folio = sum(v * (v - 1) for v in folio.values()) / (M * (M - 1))
    r_f = (obs / pairs) / p_folio if p_folio > 0 else None
    r_l = obs / exp_line if exp_line > 0 else None
    return r_f, r_l, pairs


def lag1(lines):
    """Pooled Pearson r of (len_i, len_i+1) over adjacent pairs in the same line, lengths centred on the folio mean."""
    allv = [x for ln in lines for x in ln]
    if len(allv) < 3:
        return None, 0
    mu = sum(allv) / len(allv)
    var = sum((x - mu) ** 2 for x in allv) / len(allv)
    a = [x - mu for ln in lines for x in ln[:-1]]
    b = [x - mu for ln in lines for x in ln[1:]]
    if not a or var == 0:
        return None, len(a)
    return sum(x * y for x, y in zip(a, b)) / len(a) / var, len(a)


def rhythm(lines, rng):
    """(lag-1 r, r minus the mean r over R_SHUF within-line shuffles, n pairs)."""
    r_obs, n = lag1(lines)
    if r_obs is None or n < 10:
        return r_obs, None, n
    allv = np.array([x for ln in lines for x in ln], dtype=float)
    mu, var = allv.mean(), allv.var()
    arrs = [np.array(ln, dtype=float) - mu for ln in lines if len(ln) >= 2]
    tot = 0.0
    for _ in range(R_SHUF):
        s = 0.0
        for v in arrs:
            p = rng.permutation(v)
            s += float(np.dot(p[:-1], p[1:]))
        tot += s / n / var
    return r_obs, r_obs - tot / R_SHUF, n


def build_folio_features(conn):
    import corpora
    inv = {v: k for k, v in corpora.SYMS.items()}
    gname = lambda ch: inv.get(ch, ch)  # noqa: E731
    P = defaultdict(lambda: defaultdict(list))  # translit -> folio -> lines (token tuples), P loci only
    q = conn.execute("""SELECT t.translit, t.folio, t.line_id, t.pos, t.word, t.n_glyphs, t.slot_prefix, t.slot_core,
                               t.slot_suffix FROM tokens t JOIN loci l ON l.translit=t.translit AND l.line_id=t.line_id
                        WHERE l.locus_type='P' ORDER BY t.translit, t.folio, t.rowid""")
    cur = {}
    for tr, f, lid, pos, w, ng, sp, sc, ss in q:
        key = (tr, f)
        if cur.get(key) != lid:
            P[tr][f].append([])
            cur[key] = lid
        P[tr][f][-1].append((w, ng, sp or "", sc or "", ss or "", corpora.to_glyphs(w, corpora.GLYPHS)))

    # rankings on ZL3b P tokens
    zl = [t for lines in P["ZL3b"].values() for ln in lines for t in ln]
    top_p = [p for p, _ in Counter(t[2] for t in zl if t[2]).most_common(TOP_AFFIX)]
    top_s = [s for s, _ in Counter(t[4] for t in zl if t[4]).most_common(TOP_AFFIX)]
    top_i = [g for g, _ in Counter(ln[0][5][0] for lines in P["ZL3b"].values() for ln in lines
                                   if ln and ln[0][5]).most_common(TOP_EDGE)]
    top_f = [g for g, _ in Counter(ln[-1][5][-1] for lines in P["ZL3b"].values() for ln in lines
                                   if ln and ln[-1][5]).most_common(TOP_EDGE)]

    loci_ct = defaultdict(Counter)
    for tr, f, lt, n in conn.execute("SELECT translit, folio, locus_type, COUNT(*) FROM loci GROUP BY 1, 2, 3"):
        loci_ct[(tr, f)][lt] = n
    stars = dict(conn.execute("SELECT folio, n_stars FROM folios WHERE n_stars IS NOT NULL"))
    tsrc = {tr: s for tr, s in conn.execute("SELECT translit, MIN(src) FROM loci GROUP BY 1")}

    rows = []
    for tr in sorted({k[0] for k in loci_ct}):
        base = f"tokens/loci {tr} ({tsrc.get(tr, '').split(':')[0]}, via tools/vkb/manuscript.py); {SRC}"
        folios = sorted({k[1] for k in loci_ct if k[0] == tr})
        for f in folios:
            lines = [ln for ln in P[tr].get(f, []) if ln]
            toks = [t for ln in lines for t in ln]
            n = len(toks)

            def add(feat, val, cnt, note=""):
                rows.append(dict(folio=f, translit=tr, feature=feat,
                                 value=None if val is None or (isinstance(val, float) and math.isnan(val)) else float(val),
                                 n=cnt, src=base + (f" {feat}" + (f" ({note})" if note else ""))))
            add("n_tokens", n, n)
            add("n_lines", len(lines), len(lines))
            add("mean_wlen", (sum(t[1] for t in toks) / n) if n else None, n)
            rng = np.random.default_rng(seed(tr, f, "sub"))
            if n >= N_SUB:
                ttrs, h1s, h2s = [], [], []
                for _ in range(R_SUB):
                    idx = rng.choice(n, N_SUB, replace=False)
                    sub = [toks[i] for i in idx]
                    ttrs.append(len({t[0] for t in sub}) / N_SUB)
                    a, b = h1_h2([t[5] for t in sub])
                    h1s.append(a); h2s.append(b)
                add("ttr_50", sum(ttrs) / R_SUB, n, f"{R_SUB} subsamples of {N_SUB}")
                add("h1_50", sum(h1s) / R_SUB, n, f"{R_SUB} subsamples of {N_SUB}")
                add("h2_50", sum(h2s) / R_SUB, n, f"{R_SUB} subsamples of {N_SUB}")
            else:
                for k in ("ttr_50", "h1_50", "h2_50"):
                    add(k, None, n, f"fewer than {N_SUB} P tokens")
            a, b = h1_h2([t[5] for t in toks])
            add("h1", a, n)
            add("h2", b, n)
            for p in top_p:
                add(f"pfx:{p}", (sum(t[2] == p for t in toks) / n) if n else None, n)
            for s in top_s:
                add(f"sfx:{s}", (sum(t[4] == s for t in toks) / n) if n else None, n)
            r_f, r_l, npair = rw1([[t[3] for t in ln] for ln in lines])
            add("Rw1", r_f, npair, "null: within-folio permutation, exact")
            add("Rw1_line", r_l, npair, "null: within-line shuffle, exact")
            r_obs, r_exc, npair = rhythm([[t[1] for t in ln] for ln in lines],
                                         np.random.default_rng(seed(tr, f, "rhythm")))
            add("lag1_wlen", r_obs, npair)
            add("rhythm_excess", r_exc, npair, f"{R_SHUF} within-line shuffles")
            ini = [ln[0][5][0] for ln in lines if ln[0][5]]
            fin = [ln[-1][5][-1] for ln in lines if ln[-1][5]]
            for g in top_i:
                add(f"init:{gname(g)}", (sum(x == g for x in ini) / len(ini)) if ini else None, len(ini))
            for g in top_f:
                add(f"final:{gname(g)}", (sum(x == g for x in fin) / len(fin)) if fin else None, len(fin))
            lc = loci_ct[(tr, f)]
            nl = sum(lc.values())
            add("label_share", (lc["L"] + lc["R"]) / nl if nl else None, nl, "loci of type L or R / all loci")
            add("n_stars", stars.get(f) if f in stars else None, None,
                "runs/s100/star_classes.tsv via folios.n_stars; scope quire T only")
    create(conn, "folio_features", ["folio TEXT", "translit TEXT", "feature TEXT", "value REAL", "n INTEGER"])
    insert(conn, "folio_features", rows)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_ff ON folio_features(translit, feature, folio)")


def build_finding_links(conn):
    import evidence
    g, marks = evidence.load_graph()
    gsrc = rel(evidence.GRAPH)
    rows = []
    for fid, f in g["findings"].items():
        ln = marks.get(("findings", fid))
        for i, r in enumerate(f.get("related") or []):
            if isinstance(r, dict):
                rows.append(dict(fid=fid, rel=r.get("rel"), target=r.get("f"), note=r.get("note"),
                                 src=f"{gsrc}:{marks.get(('findings', fid, 'related', i), ln)}"))
        for key, relname in (("decisions", "decision"), ("rests_on", "rests-on")):
            for i, d in enumerate(f.get(key) or []):
                rows.append(dict(fid=fid, rel=relname, target=str(d), note=None,
                                 src=f"{gsrc}:{marks.get(('findings', fid, key, i), ln)}"))
    create(conn, "finding_links", ["fid TEXT", "rel TEXT", "target TEXT", "note TEXT"])
    insert(conn, "finding_links", rows)


def build(conn):
    build_folio_features(conn)
    build_finding_links(conn)
    conn.commit()


if __name__ == "__main__":
    import sqlite3, shutil
    from common import DB
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "vkb", "test_features.sqlite")
    assert os.path.basename(out) != "vkb.sqlite", "self-test never writes vkb.sqlite"
    shutil.copyfile(DB, out)  # needs tokens/loci/folios from the last build
    conn = sqlite3.connect(out)
    build(conn)
    for r in conn.execute("SELECT translit, COUNT(DISTINCT folio), COUNT(DISTINCT feature), COUNT(*), SUM(value IS NULL) "
                          "FROM folio_features GROUP BY 1"):
        print(r)
    print(conn.execute("SELECT rel, COUNT(*) FROM finding_links GROUP BY 1").fetchall())
    conn.close()
