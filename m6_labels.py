"""m6: Voynich labels as a register -- inventory, entropy profile, o-initial register,
list-order structure, and a replication of Schwartz (2026) label figures.

Units from vparse: P* paragraph, L* label, C* circle, R* radial.
Label tokens = every word in an L* record ("all positions"); "primary" = first word of
each L* locus (Schwartz's term). Words containing '?' (unclear glyphs) are dropped.
Seed 20261017. Writes results_m6_labels.txt. Does not modify any existing file.
"""
import math
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

import corpora
import vparse
from a1_profile import char_entropies

SEED = 20261017
NSHUF = 200
HERE = Path(__file__).parent
OUT = HERE / "results_m6_labels.txt"
rng = random.Random(SEED)

GALLOWS_RE = re.compile(r"^(c[ktpf]h|[ktpf])")

lines_out = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines_out.append(s)


# ----------------------------------------------------------------------------- load
recs = vparse.load()
# paragraph-initial flag: re-read raw file for <%> marker (vparse strips it)
para_init = {}
for raw in vparse.DATA.read_text(encoding="ascii", errors="replace").splitlines():
    m = vparse.LINE_RE.match(raw)
    if m:
        page, n, _, unit, text = m.groups()
        para_init[(page, int(n))] = "<%>" in text

page_order = []
for r in recs:
    if r["page"] not in page_order:
        page_order.append(r["page"])


def ucls(u):
    return u[0]  # P, L, C, R


# tokens with metadata
TOK = []  # dict(word, page, unit, cls, illus, hand, lang, pos, nline, first_of_locus, para_init)
for r in recs:
    ws = [w for w in r["words"] if "?" not in w]
    for i, w in enumerate(ws):
        TOK.append(dict(word=w, page=r["page"], line=r["line"], unit=r["unit"], cls=ucls(r["unit"]),
                        illus=r["illus"], hand=r["hand"], lang=r["lang"], pos=i, nline=len(ws),
                        primary=(i == 0), pinit=(i == 0 and para_init.get((r["page"], r["line"]), False))))

LAB = [t for t in TOK if t["cls"] == "L"]
PAR = [t for t in TOK if t["cls"] == "P"]
CIR = [t for t in TOK if t["cls"] in "CR"]
labw = [t["word"] for t in LAB]
parw = [t["word"] for t in PAR]
cirw = [t["word"] for t in CIR]
ALLW = Counter(t["word"] for t in TOK)
PARW = Counter(parw)
LABW = Counter(labw)
page_words_all = defaultdict(set)
page_words_lab = defaultdict(set)
for t in TOK:
    page_words_all[t["word"]].add(t["page"])
    if t["cls"] == "L":
        page_words_lab[t["word"]].add(t["page"])

say(f"m6_labels.py  run {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} local  seed={SEED}  shuffles={NSHUF}")
say(f"data: {vparse.DATA.name}; words with '?' dropped; label tokens = all words in L* records")
say()


# ----------------------------------------------------------------------------- 1. inventory
def inv(words):
    c = Counter(words)
    n = len(words)
    hap = sum(v == 1 for v in c.values())
    return n, len(c), (hap / len(c) if c else float("nan"))


say("=" * 78)
say("1. INVENTORY  (tokens / types / hapax share of types)")
say("=" * 78)
for key in ["illus", "hand", "lang"]:
    say(f"-- by {key} --")
    say(f"{'':8}{'labels(L*)':>26}{'circle+radial(C*,R*)':>26}{'paragraph(P*)':>26}")
    keys = sorted(set(t[key] for t in TOK))
    for k in keys:
        row = f"{k:8}"
        for grp in (LAB, CIR, PAR):
            n, ty, h = inv([t["word"] for t in grp if t[key] == k])
            row += f"{n:>9}{ty:>8}{h:>9.3f}" if n else f"{'-':>9}{'-':>8}{'-':>9}"
        say(row)
    row = f"{'ALL':8}"
    for grp in (LAB, CIR, PAR):
        n, ty, h = inv([t["word"] for t in grp])
        row += f"{n:>9}{ty:>8}{h:>9.3f}"
    say(row)
    say()
prim = [t for t in LAB if t["primary"]]
say(f"label loci (L* records with >=1 clear word): {len(prim)}; primary (first-word) tokens: {len(prim)}; "
    f"all-position label tokens: {len(LAB)}; label pages: {len(set(t['page'] for t in LAB))}")
say(f"label unit subtypes: {dict(Counter(t['unit'] for t in LAB))}")
say()

# ----------------------------------------------------------------------------- 2. profile
say("=" * 78)
say("2. PROFILE: h2 (a1 char_entropies, space as symbol), h1, length, first/last glyph")
say("=" * 78)


def prof(words, tok="eva"):
    ww = words if tok == "eva" else [corpora.to_glyphs(w, corpora.GLYPHS) for w in words]
    ce = char_entropies(ww)
    L = [len(w) for w in ww]
    return dict(n=len(ww), alpha=ce["alpha"], h1=ce["h1"], h2=ce["h2"], h3=ce["h3"],
                mlen=float(np.mean(L)), sdlen=float(np.std(L)))


def bag_null(pool, n, k=NSHUF, r=rng, tok="eva"):
    vals = defaultdict(list)
    for _ in range(k):
        s = r.sample(pool, n)
        p = prof(s, tok)
        for kk, v in p.items():
            vals[kk].append(v)
    return {kk: (float(np.mean(v)), float(np.std(v))) for kk, v in vals.items()}


def contig_null(pool, n, k=NSHUF, r=rng, tok="eva"):
    vals = defaultdict(list)
    for _ in range(k):
        i = r.randrange(0, len(pool) - n)
        p = prof(pool[i:i + n], tok)
        for kk, v in p.items():
            vals[kk].append(v)
    return {kk: (float(np.mean(v)), float(np.std(v))) for kk, v in vals.items()}


def z(obs, ms):
    m, s = ms
    return (obs - m) / s if s > 0 else float("nan")


PROF_ROWS = {}
for tok in ["eva", "glyph"]:
    say(f"-- tokenization: {tok} --")
    pl = prof(labw, tok)
    pp = prof(parw, tok)
    pc = prof(cirw, tok)
    bag = bag_null(parw, len(labw), tok=tok)
    ctg = contig_null(parw, len(labw), tok=tok)
    PROF_ROWS[tok] = [pl, pp, bag, ctg]
    cols = ["n", "alpha", "h1", "h2", "h3", "mlen", "sdlen"]
    say(f"{'set':34}" + "".join(f"{c:>9}" for c in cols))
    for name, p in [("labels (all tokens)", pl), ("circle+radial", pc), ("paragraph (all)", pp)]:
        say(f"{name:34}" + "".join(f"{p[c]:>9.3f}" if isinstance(p[c], float) else f"{p[c]:>9}" for c in cols))
    say(f"{'bag null: random P words, n=labels':34}" + "".join(f"{bag[c][0]:>9.3f}" for c in cols))
    say(f"{'   (sd)':34}" + "".join(f"{bag[c][1]:>9.3f}" for c in cols))
    say(f"{'contiguous P sample, n=labels':34}" + "".join(f"{ctg[c][0]:>9.3f}" for c in cols))
    say(f"{'   (sd)':34}" + "".join(f"{ctg[c][1]:>9.3f}" for c in cols))
    say(f"labels vs bag null: z(h2)={z(pl['h2'], bag['h2']):+.2f}  z(h1)={z(pl['h1'], bag['h1']):+.2f}  "
        f"z(mlen)={z(pl['mlen'], bag['mlen']):+.2f}  z(sdlen)={z(pl['sdlen'], bag['sdlen']):+.2f}")
    say(f"labels vs contiguous: z(h2)={z(pl['h2'], ctg['h2']):+.2f}")
    # per language / hand h2 of labels vs matched-size bag of same-hand paragraph words
    say("  per hand (labels vs bag of same-hand paragraph words, 100 draws):")
    for h in sorted(set(t["hand"] for t in LAB)):
        lw = [t["word"] for t in LAB if t["hand"] == h]
        pw = [t["word"] for t in PAR if t["hand"] == h]
        if len(lw) < 50 or len(pw) < len(lw):
            say(f"    hand {h}: labels={len(lw)} P words={len(pw)} (skipped: too few)")
            continue
        pl_h = prof(lw, tok)
        bg = bag_null(pw, len(lw), k=100, tok=tok)
        say(f"    hand {h}: labels n={len(lw)} h2={pl_h['h2']:.3f}  bag h2={bg['h2'][0]:.3f}±{bg['h2'][1]:.3f}  "
            f"z={z(pl_h['h2'], bg['h2']):+.2f}  mlen {pl_h['mlen']:.2f} vs {bg['mlen'][0]:.2f}")
    # frequency-matched bag: P tokens sampled to match the labels' corpus-frequency-bin histogram
    def _fbin(f):
        return 0 if f == 1 else 1 if f == 2 else 2 if f <= 5 else 3 if f <= 10 else 4 if f <= 30 else 5
    lab_bin_n = Counter(_fbin(ALLW[w]) for w in labw)
    par_bin_pool = defaultdict(list)
    for w in parw:
        par_bin_pool[_fbin(ALLW[w])].append(w)
    fm = defaultdict(list)
    for _ in range(100):
        s = []
        for b, k in lab_bin_n.items():
            s += rng.sample(par_bin_pool[b], k)
        pr = prof(s, tok)
        for kk, v in pr.items():
            fm[kk].append(v)
    fm = {kk: (float(np.mean(v)), float(np.std(v))) for kk, v in fm.items()}
    PROF_ROWS[tok].append(fm)
    say(f"  frequency-matched bag (P tokens drawn to match label corpus-frequency bins, 100 draws): "
        f"h2={fm['h2'][0]:.3f}±{fm['h2'][1]:.3f}  mlen={fm['mlen'][0]:.2f}  sdlen={fm['sdlen'][0]:.2f}  "
        f"labels z(h2)={z(pl['h2'], fm['h2']):+.2f}")
    say()


# first / last glyph distributions
def first_glyph(w):
    for g in ("cth", "ckh", "cph", "cfh", "ch", "sh", "qo"):
        if w.startswith(g):
            return g
    return w[0]


def last_glyph(w):
    for g in ("iin", "in", "ch", "sh", "dy", "ey", "ol", "al", "ar", "or"):
        if w.endswith(g):
            return g
    return w[-1]


def dist(words, f):
    c = Counter(f(w) for w in words)
    n = sum(c.values())
    return {k: v / n for k, v in c.items()}


def jsd(p, q):
    keys = set(p) | set(q)
    m = {k: (p.get(k, 0) + q.get(k, 0)) / 2 for k in keys}

    def kl(a, b):
        return sum(a[k] * math.log2(a[k] / b[k]) for k in a if a.get(k, 0) > 0)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


for nm, f in [("first glyph", first_glyph), ("last glyph", last_glyph)]:
    dl, dp = dist(labw, f), dist(parw, f)
    keys = sorted(set(dl) | set(dp), key=lambda k: -(dl.get(k, 0) + dp.get(k, 0)))[:12]
    say(f"-- {nm} distribution (share of tokens) --")
    say(f"{'':12}" + "".join(f"{k:>7}" for k in keys))
    say(f"{'labels':12}" + "".join(f"{dl.get(k, 0):>7.3f}" for k in keys))
    say(f"{'paragraph':12}" + "".join(f"{dp.get(k, 0):>7.3f}" for k in keys))
    jd = jsd(dl, dp)
    js_null = []
    for _ in range(NSHUF):
        js_null.append(jsd(dist(rng.sample(parw, len(labw)), f), dp))
    say(f"JSD(labels, paragraph)={jd:.4f}; bag-null JSD={np.mean(js_null):.4f}±{np.std(js_null):.4f} "
        f"(max {max(js_null):.4f}); z={(jd - np.mean(js_null)) / np.std(js_null):+.1f}")
say()

# ----------------------------------------------------------------------------- 3. register
say("=" * 78)
say("3. REGISTER: initial-glyph shares, label-only types, cross-page recurrence")
say("=" * 78)


def share(words, pred):
    return sum(pred(w) for w in words) / len(words) if words else float("nan")


o_init = lambda w: w.startswith("o")
qo_init = lambda w: w.startswith("qo")
gal_init = lambda w: bool(GALLOWS_RE.match(w))


def binom_z(p_obs, n, p0):
    if n == 0 or p0 in (0, 1):
        return float("nan")
    return (p_obs - p0) / math.sqrt(p0 * (1 - p0) / n)


say(f"{'section':8}{'nL':>6}{'nP':>7} | {'o- L':>7}{'o- P':>7}{'z':>6} | {'qo- L':>7}{'qo- P':>7} | "
    f"{'gal L':>7}{'gal P':>7} | {'o- Pline1':>10}")
secs = sorted(set(t["illus"] for t in TOK))
for s in secs + ["ALL"]:
    lw = [t["word"] for t in LAB if s == "ALL" or t["illus"] == s]
    pw = [t["word"] for t in PAR if s == "ALL" or t["illus"] == s]
    p1 = [t["word"] for t in PAR if (s == "ALL" or t["illus"] == s) and t["pos"] == 0]
    if not lw:
        continue
    say(f"{s:8}{len(lw):>6}{len(pw):>7} | {share(lw, o_init):>7.3f}{share(pw, o_init):>7.3f}"
        f"{binom_z(share(lw, o_init), len(lw), share(pw, o_init)):>6.1f} | "
        f"{share(lw, qo_init):>7.3f}{share(pw, qo_init):>7.3f} | "
        f"{share(lw, gal_init):>7.3f}{share(pw, gal_init):>7.3f} | {share(p1, o_init):>10.3f}")
say("(z: label o-share vs binomial at that section's paragraph o-share; Z section has no paragraph text)")
say()
say("-- by hand (o-initial) --")
for h in sorted(set(t["hand"] for t in LAB)):
    lw = [t["word"] for t in LAB if t["hand"] == h]
    pw = [t["word"] for t in PAR if t["hand"] == h]
    p1 = [t["word"] for t in PAR if t["hand"] == h and t["pos"] == 0]
    say(f"  hand {h}: labels n={len(lw)} o-={share(lw, o_init):.3f} | P n={len(pw)} o-={share(pw, o_init):.3f} "
        f"line-initial o-={share(p1, o_init):.3f} | z vs P all={binom_z(share(lw, o_init), len(lw), share(pw, o_init)):+.1f} "
        f"vs P line1={binom_z(share(lw, o_init), len(lw), share(p1, o_init)):+.1f}")
say()

# label types never in paragraph text, with leave-sample-out null
lab_types = set(labw)
never = sum(1 for w in lab_types if w not in PARW)
never_tok = sum(1 for w in labw if w not in PARW)
say(f"label types never in paragraph text: {never}/{len(lab_types)} = {never / len(lab_types):.3f}; "
    f"by tokens {never_tok}/{len(labw)} = {never_tok / len(labw):.3f}")
# null: sample n label-sized set of P tokens; type 'never elsewhere in P' = count in P equals count in sample
nn_t, nn_k = [], []
for _ in range(NSHUF):
    s = rng.sample(parw, len(labw))
    cs = Counter(s)
    nt = sum(1 for w, v in cs.items() if PARW[w] == v)
    nn_t.append(nt / len(cs))
    nn_k.append(sum(v for w, v in cs.items() if PARW[w] == v) / len(s))
say(f"  bag null (random P sample of same size; type absent from the REST of P): "
    f"types {np.mean(nn_t):.3f}±{np.std(nn_t):.3f}, tokens {np.mean(nn_k):.3f}±{np.std(nn_k):.3f}")
# same-size labels vs circle text
never_c = sum(1 for w in set(cirw) if w not in PARW)
say(f"  circle/radial types never in paragraph text: {never_c}/{len(set(cirw))} = {never_c / len(set(cirw)):.3f}")
say()

# cross-page recurrence
say("-- cross-page recurrence --")
lab_pages = defaultdict(Counter)
for t in LAB:
    lab_pages[t["word"]][t["page"]] += 1
rec_tok_lab = sum(1 for t in LAB if len(lab_pages[t["word"]]) > 1) / len(LAB)
rec_tok_any = sum(1 for t in LAB if len(page_words_all[t["word"]]) > 1) / len(LAB)
types_multi = sum(1 for w, c in lab_pages.items() if len(c) > 1)
say(f"label tokens whose type is a LABEL on another page: {rec_tok_lab:.3f}; "
    f"whose type occurs ANYWHERE on another page: {rec_tok_any:.3f}")
say(f"label types on >1 page (as labels): {types_multi} of {len(lab_types)}")

# null A: label-shuffle (permute label words among label slots, keep per-page counts)
slots = [t["page"] for t in LAB]
nullA = []
for _ in range(NSHUF):
    ws = labw[:]
    rng.shuffle(ws)
    d = defaultdict(set)
    for p, w in zip(slots, ws):
        d[w].add(p)
    nullA.append(sum(1 for w, s in d.items() if len(s) > 1))
# null B: running-text null (random P tokens with their pages, same n)
nullB = []
for _ in range(NSHUF):
    s = rng.sample(PAR, len(LAB))
    d = defaultdict(set)
    for t in s:
        d[t["word"]].add(t["page"])
    nullB.append(sum(1 for w, ss in d.items() if len(ss) > 1))
say(f"  label-shuffle null: {np.mean(nullA):.1f}±{np.std(nullA):.1f} (min {min(nullA)}); "
    f"running-text null (random P tokens, same n): {np.mean(nullB):.1f}±{np.std(nullB):.1f} (min {min(nullB)})")
say(f"  observed {types_multi}: z vs label-shuffle {(types_multi - np.mean(nullA)) / np.std(nullA):+.1f}, "
    f"z vs running-text {(types_multi - np.mean(nullB)) / np.std(nullB):+.1f}")

# frequency-matched token recurrence: bins of corpus-wide type frequency
def fbin(f):
    return 0 if f == 1 else 1 if f == 2 else 2 if f <= 5 else 3 if f <= 10 else 4 if f <= 30 else 5


BINS = ["f=1", "f=2", "3-5", "6-10", "11-30", "31+"]
lab_bins = Counter(fbin(ALLW[t["word"]]) for t in LAB)
par_by_bin = defaultdict(list)
for t in PAR:
    par_by_bin[fbin(ALLW[t["word"]])].append(t)
say("  token recurrence (type on another page, any unit), by corpus-wide frequency bin, labels vs P tokens:")
say(f"  {'bin':6}{'nL':>6}{'L rec':>8}{'nP':>7}{'P rec':>8}")
tot_l = tot_p = 0
for b in range(6):
    lt = [t for t in LAB if fbin(ALLW[t["word"]]) == b]
    pt = par_by_bin[b]
    rl = share(lt, lambda t: len(page_words_all[t["word"]]) > 1)
    rp = share(pt, lambda t: len(page_words_all[t["word"]]) > 1)
    say(f"  {BINS[b]:6}{len(lt):>6}{rl:>8.3f}{len(pt):>7}{rp:>8.3f}")
    tot_l += rl * len(lt) if lt else 0
    tot_p += rp * len(lt) if pt else 0
say(f"  frequency-matched: labels {tot_l / len(LAB):.3f} vs P reweighted to label bins {tot_p / len(LAB):.3f}")
say(f"  label frequency bins (share of tokens): " +
    ", ".join(f"{BINS[b]}:{lab_bins[b] / len(LAB):.2f}" for b in range(6)))
pbins = Counter(fbin(ALLW[t["word"]]) for t in PAR)
say(f"  paragraph frequency bins:               " +
    ", ".join(f"{BINS[b]}:{pbins[b] / len(PAR):.2f}" for b in range(6)))
say()

# ----------------------------------------------------------------------------- 4. list structure
say("=" * 78)
say("4. LABELS AS A LIST: adjacent similarity in ZL order vs shuffled order")
say("=" * 78)


def edit(a, b):
    m, n = len(a), len(b)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return prev[n]


def ned(a, b):
    return edit(a, b) / max(len(a), len(b))


def adj_stats(seqs):
    """seqs: list of per-page label lists. Returns mean normalised edit distance, shared-first-glyph
    rate, shared-last-glyph rate, shared-2-prefix rate over adjacent pairs, longest first-glyph run."""
    d = f = l = p2 = 0
    npairs = 0
    longest = 0
    for s in seqs:
        run = 1
        for a, b in zip(s, s[1:]):
            npairs += 1
            d += ned(a, b)
            sf = first_glyph(a) == first_glyph(b)
            f += sf
            l += last_glyph(a) == last_glyph(b)
            p2 += a[:2] == b[:2]
            run = run + 1 if sf else 1
            longest = max(longest, run)
        if len(s) == 1:
            longest = max(longest, 1)
    if npairs == 0:
        return None
    return dict(ned=d / npairs, first=f / npairs, last=l / npairs, pre2=p2 / npairs, run=longest, pairs=npairs)


def list_test(name, seqs):
    seqs = [s for s in seqs if len(s) >= 2]
    obs = adj_stats(seqs)
    if obs is None:
        say(f"{name}: no adjacent pairs")
        return
    null = defaultdict(list)
    for _ in range(NSHUF):
        sh = []
        for s in seqs:
            s2 = s[:]
            rng.shuffle(s2)
            sh.append(s2)
        st = adj_stats(sh)
        for k, v in st.items():
            null[k].append(v)
    say(f"{name}: pages={len(seqs)} labels={sum(len(s) for s in seqs)} adjacent pairs={obs['pairs']}")
    for k, lab, better in [("ned", "adjacent norm. edit distance", "lower"), ("first", "shared first glyph", "higher"),
                           ("last", "shared last glyph", "higher"), ("pre2", "shared 2-char prefix", "higher"),
                           ("run", "longest same-first-glyph run", "higher")]:
        m, s = np.mean(null[k]), np.std(null[k])
        if better == "lower":
            p = (sum(1 for v in null[k] if v <= obs[k]) + 1) / (NSHUF + 1)
        else:
            p = (sum(1 for v in null[k] if v >= obs[k]) + 1) / (NSHUF + 1)
        say(f"   {lab:30} obs={obs[k]:.3f}  shuffled={m:.3f}±{s:.3f}  z={(obs[k] - m) / s if s > 0 else float('nan'):+.2f}  "
            f"p({better})={p:.3f}")


def page_labels(pages, unit_prefix):
    out = []
    for p in pages:
        s = [t["word"] for t in LAB if t["page"] == p and t["unit"].startswith(unit_prefix)]
        if s:
            out.append(s)
    return out


star_pages = ["f68r1", "f68r2", "f68r3"]
zod_pages = [p for p in page_order if p in {"f70v2", "f70v1", "f71r", "f71v", "f72r1", "f72r2", "f72r3",
                                            "f72v3", "f72v2", "f72v1", "f73r", "f73v"}]
pharma_pages = [p for p in page_order if any(t["page"] == p and t["unit"] in ("Lc", "Lf") for t in LAB)]
list_test("STARS f68r1-3 (Ls)", page_labels(star_pages, "Ls"))
list_test("ZODIAC f70v2-f73v (Lz)", page_labels(zod_pages, "Lz"))
list_test("PHARMA jar/container labels (Lc)", page_labels(pharma_pages, "Lc"))
list_test("PHARMA plant-part labels (Lf)", page_labels(pharma_pages, "Lf"))
list_test("ALL label pages, all L* in file order", [[t["word"] for t in LAB if t["page"] == p] for p in page_order])
# control: paragraph lines of same length as label sequences (adjacent words in running text)
say("control: adjacent words WITHIN paragraph lines (same statistics, shuffle within line):")
plines = defaultdict(list)
for t in PAR:
    plines[(t["page"], t["line"])].append(t["word"])
pl = [v for v in plines.values() if len(v) >= 2]
list_test("PARAGRAPH lines (all)", rng.sample(pl, 400))
# longest same-first-glyph run detail
say("longest same-first-glyph runs (observed, per group):")
for name, seqs in [("stars", page_labels(star_pages, "Ls")), ("zodiac", page_labels(zod_pages, "Lz")),
                   ("pharma Lc", page_labels(pharma_pages, "Lc")), ("pharma Lf", page_labels(pharma_pages, "Lf"))]:
    best = (0, None, None)
    for s in seqs:
        run = 1
        for i, (a, b) in enumerate(zip(s, s[1:])):
            run = run + 1 if first_glyph(a) == first_glyph(b) else 1
            if run > best[0]:
                best = (run, first_glyph(b), s[i + 2 - run:i + 2])
    say(f"   {name}: run={best[0]} glyph={best[1]} labels={best[2]}")
say()
say("zodiac label order per page (first glyphs):")
for p in zod_pages:
    s = [t["word"] for t in LAB if t["page"] == p and t["unit"] == "Lz"]
    if s:
        say(f"   {p:6} n={len(s):2} " + "".join(first_glyph(w)[0] for w in s))
say()

# ----------------------------------------------------------------------------- 5. Schwartz replication
say("=" * 78)
say("5. SCHWARTZ 2026 REPLICATION (his numbers quoted from data/external/schwartz-2026-preprint/text.txt)")
say("=" * 78)
primw = [t["word"] for t in prim]
lab_page_set = set(t["page"] for t in LAB)
line1_labpages = [t["word"] for t in PAR if t["pos"] == 0 and t["page"] in lab_page_set]
pinit = [t["word"] for t in PAR if t["pinit"]]
# null matched on hand, section, position: for each label token, the o-share of paragraph words with same
# hand+section; position: labels are single words => compare to line-initial words (pos 0) of same hand+section;
# fall back to hand only when the section has no paragraph text (Z).
P_hs = defaultdict(list)
P_h = defaultdict(list)
P_hs1 = defaultdict(list)
P_h1 = defaultdict(list)
for t in PAR:
    P_hs[(t["hand"], t["illus"])].append(t["word"])
    P_h[t["hand"]].append(t["word"])
    if t["pos"] == 0:
        P_hs1[(t["hand"], t["illus"])].append(t["word"])
        P_h1[t["hand"]].append(t["word"])
exp_all = exp_l1 = 0.0
nmatch = 0
for t in prim:
    k = (t["hand"], t["illus"])
    pool = P_hs.get(k) or P_h.get(t["hand"]) or parw
    pool1 = P_hs1.get(k) or P_h1.get(t["hand"]) or [w for w in parw]
    exp_all += share(pool, o_init)
    exp_l1 += share(pool1, o_init)
    nmatch += 1
exp_all /= nmatch
exp_l1 /= nmatch
o_prim = share(primw, o_init)
say(f"{'quantity':58}{'Schwartz':>14}{'ours':>14}")
say(f"{'label tokens (primary; all positions)':58}{'864; 1,164':>14}{f'{len(prim)}; {len(LAB)}':>14}")
say(f"{'o-initial share: primary labels':58}{'59%':>14}{o_prim * 100:>13.1f}%")
say(f"{'  all-position label tokens':58}{'':>14}{share(labw, o_init) * 100:>13.1f}%")
say(f"{'  line-initial words on label pages':58}{'42%':>14}{share(line1_labpages, o_init) * 100:>13.1f}%")
li_nonP = [t["word"] for t in TOK if t["cls"] != "P" and t["pos"] == 0 and t["page"] in lab_page_set]
li_anyunit = [t["word"] for t in TOK if t["pos"] == 0 and t["page"] in lab_page_set]
li_CR = [t["word"] for t in TOK if t["cls"] in "CR" and t["pos"] == 0 and t["page"] in lab_page_set]
say(f"{'    probe: line-initial of ALL units on label pages (L+C+R+P)':58}{'':>14}{share(li_anyunit, o_init) * 100:>13.1f}%")
say(f"{'    probe: line-initial of circle/radial lines on label pages':58}{'':>14}{share(li_CR, o_init) * 100:>13.1f}%")
say(f"{'  null matched on hand+section (all positions)':58}{'32%':>14}{exp_all * 100:>13.1f}%")
say(f"{'  null matched on hand+section, line-initial':58}{'':>14}{exp_l1 * 100:>13.1f}%")
say(f"{'  paragraph-initial running text (<%> lines, first word)':58}{'18%':>14}{share(pinit, o_init) * 100:>13.1f}%")
say(f"{'  all paragraph words':58}{'':>14}{share(parw, o_init) * 100:>13.1f}%")
say(f"{'o-initial excess over matched null (binomial z)':58}{'11-17 sd':>14}"
    f"{binom_z(o_prim, len(prim), exp_all):>13.1f}")
say(f"{'  vs line-initial matched null':58}{'':>14}{binom_z(o_prim, len(prim), exp_l1):>13.1f}")
say("  per hand (primary labels vs same-hand paragraph words / line-initial):")
for h in sorted(set(t["hand"] for t in prim)):
    lw = [t["word"] for t in prim if t["hand"] == h]
    pw, p1 = P_h.get(h, []), P_h1.get(h, [])
    if not pw:
        say(f"    hand {h}: labels n={len(lw)} o-={share(lw, o_init):.2f}; no paragraph text in this hand")
        continue
    say(f"    hand {h}: labels n={len(lw)} o-={share(lw, o_init):.2f} vs P {share(pw, o_init):.2f} "
        f"(z={binom_z(share(lw, o_init), len(lw), share(pw, o_init)):+.1f}) vs P line1 {share(p1, o_init):.2f} "
        f"(z={binom_z(share(lw, o_init), len(lw), share(p1, o_init)):+.1f})")
prim_types = set(primw)
nev_p = sum(1 for w in prim_types if w not in PARW) / len(prim_types)
nev_pt = sum(1 for w in primw if w not in PARW) / len(primw)
say(f"{'labels never occurring in running text (types; tokens)':58}{'44%':>14}"
    f"{f'{nev_p * 100:.0f}%; {nev_pt * 100:.0f}%':>14}")
# types on >1 page: primary labels only, both nulls
pp_pages = defaultdict(set)
for t in prim:
    pp_pages[t["word"]].add(t["page"])
obs_multi = sum(1 for w, s in pp_pages.items() if len(s) > 1)
nA, nB = [], []
slots_p = [t["page"] for t in prim]
for _ in range(NSHUF):
    ws = primw[:]
    rng.shuffle(ws)
    d = defaultdict(set)
    for p, w in zip(slots_p, ws):
        d[w].add(p)
    nA.append(sum(1 for w, s in d.items() if len(s) > 1))
    s = rng.sample(PAR, len(prim))
    d = defaultdict(set)
    for t in s:
        d[t["word"]].add(t["page"])
    nB.append(sum(1 for w, ss in d.items() if len(ss) > 1))
say(f"{'label types on >1 page: observed; label-shuffle; running-text null':58}{'75; 85; 111':>14}"
    f"{f'{obs_multi}; {np.mean(nA):.0f}; {np.mean(nB):.0f}':>14}")
say(f"  (null sd: label-shuffle {np.std(nA):.1f}, running-text {np.std(nB):.1f}; "
    f"z={(obs_multi - np.mean(nA)) / np.std(nA):+.1f}, {(obs_multi - np.mean(nB)) / np.std(nB):+.1f})")
say("  caveat: label-shuffle null keeps per-page label counts; our running-text null draws random P tokens with "
    "their own pages (P pages are more numerous and longer than label pages, which raises recurrence).")
say()

# ----------------------------------------------------------------------------- verdict helpers
pl, pp, bag, ctg, fm_e = PROF_ROWS["eva"]
fm_g = PROF_ROWS["glyph"][4]
pl_g = PROF_ROWS["glyph"][0]
say("=" * 78)
say("SUMMARY")
say("=" * 78)
say(f"h2 (eva): labels {pl['h2']:.3f} | paragraph all {pp['h2']:.3f} | bag null (random P words, n={len(labw)}) "
    f"{bag['h2'][0]:.3f}±{bag['h2'][1]:.3f} | contiguous P sample {ctg['h2'][0]:.3f}±{ctg['h2'][1]:.3f}")
say(f"   labels z vs bag = {z(pl['h2'], bag['h2']):+.2f}; bag vs full-P difference = {bag['h2'][0] - pp['h2']:+.3f} "
    f"(the 'no neighbours'/sample-size effect alone)")
say(f"   frequency-matched bag (P tokens matched to label rarity bins): eva {fm_e['h2'][0]:.3f}±{fm_e['h2'][1]:.3f} "
    f"(labels {pl['h2']:.3f}, z={z(pl['h2'], fm_e['h2']):+.1f}); glyph {fm_g['h2'][0]:.3f}±{fm_g['h2'][1]:.3f} "
    f"(labels {pl_g['h2']:.3f}, z={z(pl_g['h2'], fm_g['h2']):+.1f}) -> most of the label h2 excess is vocabulary rarity "
    f"(36% corpus-hapax tokens vs 13% in paragraphs), not a distinct glyph grammar")
say(f"o-initial: labels {share(labw, o_init):.3f} vs paragraph {share(parw, o_init):.3f} (line-initial "
    f"{share([t['word'] for t in PAR if t['pos'] == 0], o_init):.3f}); qo-: labels {share(labw, qo_init):.3f} vs "
    f"paragraph {share(parw, qo_init):.3f}; gallows-initial: {share(labw, gal_init):.3f} vs {share(parw, gal_init):.3f}")
say(f"label types never in paragraph text {never / len(lab_types):.3f} vs bag null {np.mean(nn_t):.3f}; "
    f"label types on >1 page {types_multi} vs label-shuffle {np.mean(nullA):.0f} / running-text {np.mean(nullB):.0f}")

OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
print(f"\nwrote {OUT}")
