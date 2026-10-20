"""K1: one producer, the whole benchmark - flow cipher vs flow generator,
both with the M5 line anatomy as a line layer.

Producers (no per-metric tuning beyond the fixed constants below):
  CIPHER      F3 flow-choice Naibbe re-encryption of Greshko's sampler (beta 1.5)
  CIPHER-SEC  same cipher tables (rebuilt from the workbook, f3.naibbe_chunks),
              but the plaintext changes by section: each (hand, section) key
              gets its own stretch of Latin (Caesar / Augustine, alternating,
              different offsets), so the section signal can only come from
              MEANING (what is written about), not from the cipher
  GEN         F3 flow-choice c2 section generator (beta 1.5, 8 candidates)
Line layer (M5, results_m5_line_anatomy.txt), identical for all producers;
every rate/ratio is measured on Voynich (circular in the same way as the edge
table R and Naibbe's own tables):
  (a) paragraph-first line (IVTFF <%>): word 1 is a NULL drawn from the
      Voynich paragraph-initial type list (with counts); the producer's
      stream continues at word 2 (cipher text is not lost)
  (b) other line starts: free choice reweighted by Q_init(first glyph) =
      P(first | other line-initial) / P(first | mid-line)
  (c) line end: free choice reweighted by Q_end(last glyph) =
      P(last | line-final) / P(last | mid-line)
  (d) d-gradient: at word i of n (i >= 2) weight x (1 + D*(i-1)/(n-1)) if the
      candidate starts with d, D = 3 (d share 4% at word 2 -> 16.5% at end)
  Choice weights multiply: base x R_flow^1.5 x positional factor ^ GAMMA.
Benchmark (each row): within-hand NMI (B5 protocol), JSD first glyph
(paragraph-initial / other line-initial vs mid), JSD last glyph, p-init
(paragraph lines) and m-final multipliers, d share word 2 vs last word,
C3 cross MI excess, F1 residual excess (page split), h2, types, hapax,
immediate repeats. Voynich and the plain (no-layer) producers as references.
Run: python k1_joint_producer.py  -> results_k1.txt
"""
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import a2_position as a2
import b4_selfcite_sim as b4
import c2_section_generator as c2
import c3_edge_coupling as c3
import corpora
import f1_residual_order as f1
import f3_flow_choice as f3
import m5_line_anatomy as m5

OUT = Path(__file__).parent / "results_k1.txt"
BETA = 1.5
GAMMA = 1.0
D_GRAD = 3.0
M_CAND = 8
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


# ---------------------------------------------------------------- layout
def layout():
    """b4.pages() records (hand/illus/quire) + M5 paragraph-start flags."""
    by = b4.pages()
    ps = {(r["page"], r["line"], r["unit"]): r["para_start"] for r in m5.load_lines()}
    for recs in by.values():
        for r in recs:
            r["para_start"] = ps.get((r["page"], r["line"], r["unit"]), False)
    return by


def line_tables(by):
    first_mid, last_mid, first_init, last_fin, para = Counter(), Counter(), Counter(), Counter(), Counter()
    for recs in by.values():
        for r in recs:
            ws = r["words"]
            if len(ws) < 3:
                continue
            (para if r["para_start"] else first_init)[ws[0] if r["para_start"] else ws[0][0]] += 1
            last_fin[ws[-1][-1]] += 1
            for w in ws[1:-1]:
                first_mid[w[0]] += 1; last_mid[w[-1]] += 1

    def ratio(num, den):
        n, d = sum(num.values()), sum(den.values())
        return lambda g: ((num.get(g, 0) + 0.5) / n) / ((den.get(g, 0) + 0.5) / d)
    return ratio(first_init, first_mid), ratio(last_fin, last_mid), para


def pos_factor(t, i, n, Qi, Qe):
    f = 1.0
    if i == 0:
        f *= Qi(t[0])
    if i == n - 1:
        f *= Qe(t[-1])
    if i >= 1 and t[0] == "d" and n > 2:
        f *= 1 + D_GRAD * (i - 1) / (n - 2) if n > 2 else 1
    return f ** GAMMA


# ---------------------------------------------------------------- cipher
def encrypt_chunks(text, tab, rng):
    """Naibbe-style chunking of a letter string (unigram 47.2% / bigram 52.8%),
    letters missing from the tables are dropped."""
    letters = [c for c in text if c in tab["u"] and c in tab["p"] and c in tab["s"]]
    out, i = [], 0
    while i < len(letters):
        if i + 1 < len(letters) and rng.random() < 0.528:
            out.append((letters[i], letters[i + 1])); i += 2
        else:
            out.append((letters[i],)); i += 1
    return out


def candidates(chunk, tab):
    if len(chunk) == 1:
        return list(tab["u"][chunk[0]].items())
    return [(a + b, ca * cb) for a, ca in tab["p"][chunk[0]].items() for b, cb in tab["s"][chunk[1]].items()]


def cipher_pages(by, chunk_source, tab, R, Qi, Qe, para, layer, seed):
    """chunk_source(record) -> next plaintext chunk (iterator per key)."""
    rng = random.Random(seed)
    ptypes, pw = list(para), list(para.values())
    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            n = len(r["words"]); line = []
            for i in range(n):
                if layer and i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pw)[0]); continue
                ch = chunk_source(r)
                if ch is None:
                    break
                cand = candidates(ch, tab)
                prev = line[-1] if line else None
                ws = [c * (R(prev[-1], t[0]) ** BETA if prev else 1) * (pos_factor(t, i, n, Qi, Qe) if layer else 1)
                      for t, c in cand]
                line.append(rng.choices([t for t, _ in cand], ws)[0])
            if len(line) < n:
                return out
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


# ---------------------------------------------------------------- generator
def gen_pages(g, R, Qi, Qe, para, layer, seed, p_seed=0.6, p_mut=0.6):
    rng = random.Random(seed)
    ptypes, pw = list(para), list(para.values())
    lex = {}

    def draw(r):
        key = (r["hand"], r["illus"])
        if key not in lex:
            lex[key] = g.lexicon(rng)
        return rng.choices(*lex[key])[0]

    def mutate(w):
        if rng.random() < p_mut and w in g.nb:
            c, wt = g.nb[w]
            return rng.choices(c, wt)[0]
        return w

    out = {}
    for page, recs in g.by.items():
        lines = []
        for li, r in enumerate(recs):
            n = len(r["words"]); line = []
            for i in range(n):
                if layer and i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pw)[0]); continue
                cands = []
                for _ in range(M_CAND):
                    if li == 0 or rng.random() < p_seed:
                        w = draw(r)
                    else:
                        w = rng.choice([x for l in lines for x in l["words"]] + line)
                    cands.append(mutate(w))
                prev = line[-1] if line else None
                ws = [(R(prev[-1], t[0]) ** BETA if prev else 1) * (pos_factor(t, i, n, Qi, Qe) if layer else 1)
                      for t in cands]
                line.append(rng.choices(cands, ws)[0])
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


# ---------------------------------------------------------------- benchmark
def jsd_counts(a, b):
    return a2.jsd(a, b)


def bench(name, by, rng):
    lines = [r for recs in by.values() for r in recs]
    words = [w for r in lines for w in r["words"]]
    mid_f, mid_l, para_f, oth_f, fin_l = Counter(), Counter(), Counter(), Counter(), Counter()
    pinit = pmid = minit = mmid = 0
    d2 = dl = n2 = 0
    for r in lines:
        ws = r["words"]
        if len(ws) < 3:
            continue
        (para_f if r.get("para_start") else oth_f)[ws[0][0]] += 1
        fin_l[ws[-1][-1]] += 1
        for w in ws[1:-1]:
            mid_f[w[0]] += 1; mid_l[w[-1]] += 1
        if len(ws) >= 8:
            n2 += 1; d2 += ws[1][0] == "d"; dl += ws[-1][0] == "d"
    nm = sum(mid_f.values())
    pm = mid_f["p"] / nm
    p_para = para_f["p"] / max(sum(para_f.values()), 1)
    m_fin = fin_l["m"] / sum(fin_l.values()); m_mid = mid_l["m"] / nm
    try:
        nmi = c2.within_nmi(by, rng)
        nmi_s = f"{nmi['1'][0]:.3f}/{nmi['2'][0]:.3f}"
    except Exception as e:           # too few chunks for a hand subset
        nmi_s = "  n/a  "
    cross = c3.score([r["words"] for r in lines], c3.EVA)
    f1.TOPN = 300
    tr, te = f1.split_pages(by)
    U, E, E2, W, _ = f1.evaluate(tr, te)
    sU, _, sE2, sW, _ = f1.evaluate(f1.shuffled(tr), f1.shuffled(te))
    resid = (E2 - W) - (sE2 - sW)
    cnt = Counter(words)
    hapax = sum(1 for c in cnt.values() if c == 1) / len(cnt)
    rep = sum(a == b for a, b in zip(words, words[1:])) / len(words)
    emit(f"{name:24} NMI h1/h2={nmi_s}  JSDf para={jsd_counts(para_f, mid_f):.3f} other={jsd_counts(oth_f, mid_f):.3f}"
         f"  JSDl={jsd_counts(fin_l, mid_l):.3f}  p(para) x{p_para / pm if pm else float('inf'):6.1f}"
         f"  m-fin x{m_fin / m_mid if m_mid else float('inf'):5.1f}  d w2/last {d2 / max(n2, 1):.3f}/{dl / max(n2, 1):.3f}"
         f"  crossMI+{cross[2]:.3f}  resid {resid:+.3f}  h2={b4.h2(words):.2f}  types={len(cnt)} hapax={hapax:.2f}"
         f"  rep={100 * rep:.2f}%  tok={len(words)}")


def main():
    rng = np.random.default_rng(0)
    emit("K1: joint producers with the M5 line layer; one row per producer, whole benchmark")
    emit(f"BETA={BETA} GAMMA={GAMMA} D_GRAD={D_GRAD}; NMI = B5 within-hand (h1 H/P, h2 B/H/T); JSDf para/other = first glyph of"
         " paragraph-first / other line-initial words vs mid-line; p(para) = p-initial share on paragraph-first lines vs mid-line")
    emit()
    by = layout()
    R = f3.ratio_table(by)
    Qi, Qe, para = line_tables(by)
    bench("VOYNICH", by, rng)
    emit()
    seq, tab = f3.naibbe_chunks()
    for layer in (False, True):
        it = iter([c for c, _ in seq])
        src = lambda r, it=it: next(it, None)
        bench(f"CIPHER {'+layer' if layer else 'plain'}", cipher_pages(by, src, tab, R, Qi, Qe, para, layer, 1), rng)
    # section-aware plaintext: each (hand, section) key reads its own stretch of Latin
    texts = {n: "".join(corpora.control(n)) for n in ("latin_caesar", "latin_augustine")}
    keys = sorted({(r["hand"], r["illus"]) for recs in by.values() for r in recs})
    crng = random.Random(9)
    streams = {}
    for j, k in enumerate(keys):
        t = texts["latin_caesar" if j % 2 == 0 else "latin_augustine"]
        off = (j * 37_000) % max(len(t) - 200_000, 1)
        streams[k] = iter(encrypt_chunks(t[off:off + 200_000], tab, crng))
    src = lambda r: next(streams[(r["hand"], r["illus"])], None)
    bench("CIPHER-SEC +layer", cipher_pages(by, src, tab, R, Qi, Qe, para, True, 2), rng)
    emit()
    g = c2.Gen(by)
    for layer in (False, True):
        for seed in (1, 2):
            bench(f"GEN {'+layer' if layer else 'plain'} s{seed}", gen_pages(g, R, Qi, Qe, para, layer, seed), rng)
    emit()
    emit("NL control reference (other scripts): Augustine book NMI 0.155 (c2); Dante verse JSDf 0.034 JSDl 0.167, m-fin x0.0 (b4);"
         " prose crossMI +0.04..+0.15 (c3); prose residual +0.14..+0.39 (f1)")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
