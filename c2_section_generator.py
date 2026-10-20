"""C2: can a meaningless copy-and-mutate generator with a section-specific seed
vocabulary and two simple line rules reach Voynich's within-hand section NMI
(0.275 hand 1, 0.333 hand 2, results_b5.txt) AND its ~x16 line-edge
enrichment (p- line-initial x15.97, -m line-final x16.55, results_b4.txt)?

Generator (keeps every real page's line count and line lengths, b4 style):
  * each "lexicon key" owns a seed lexicon: L word types drawn without
    replacement from the global Voynich vocabulary (weight sqrt(freq)), used
    with weight freq. The key decides what the vocabulary follows:
      section : key = (hand, section)       <- the hypothesis under test
      drift   : key = page position in the manuscript (smooth blend of anchor
                lexicons every DRIFT_PAGES pages; ignores section) - a
                writing-order-drift null used again by c1
      global  : one lexicon for everything  - null
      circular: lexicon = the real tokens of that (hand, section), i.e. the
                vocabulary is copied from the answer (upper bound, Naibbe-like)
  * first line of a page: fresh draws from the lexicon. Later words: with
    p_seed a fresh lexicon draw, else copy a word from the page so far
    (5% same column, as SIMcal in b4); then mutate with p_mut to a
    single-glyph-edit neighbour (b4.build_neighbours).
  * line rules (explicit, position-dependent): line-initial word gets an
    initial p with prob RULE_P; line-final word gets a final m with prob
    RULE_M. Rules apply while generating, so copying can spread p/m words.
Measures: B5 within-hand NMI (same chunking/NMF/nulls as b5), b4.report line
statistics. Controls: Augustine book-label NMI and Dante verse line stats
(already in results_b5/b4; Augustine recomputed here for the NMI side).
Run: python c2_section_generator.py  -> results_c2.txt
"""
import random
from collections import Counter
from pathlib import Path

import numpy as np

import b4_selfcite_sim as b4
import b5_nmf_topics as b5

OUT = Path(__file__).parent / "results_c2.txt"
L = 300
DRIFT_PAGES = 20
RULE_P = 0.088   # chosen so line-initial p ~ 0.093 if mid-line p stays ~0.005
RULE_M = 0.148   # line-final m ~ 0.155
log = b4.log     # share b4.report's log


def emit(s=""):
    b4.emit(s)


_build_neighbours = b4.build_neighbours


def sorted_neighbours(freq):
    """b4.build_neighbours, with candidates in sorted order: b4's come from set
    iteration, so its generators change with PYTHONHASHSEED between runs."""
    out = {}
    for w, (c, wt) in _build_neighbours(freq).items():
        pairs = sorted(zip(c, wt))
        out[w] = ([a for a, _ in pairs], [b for _, b in pairs])
    return out


b4.build_neighbours = sorted_neighbours   # in-process only; b4 file untouched


class Gen:
    def __init__(self, by):
        self.by = by
        words = [w for p in by.values() for r in p for w in r["words"]]
        self.freq = Counter(words)
        self.nb = b4.build_neighbours(self.freq)
        self.types = [w for w, c in self.freq.items() if c >= 2]
        self.tw = [self.freq[w] ** 0.5 for w in self.types]
        self.page_ix = {p: i for i, p in enumerate(by)}
        self.real = {}
        for recs in by.values():
            for r in recs:
                self.real.setdefault((r["hand"], r["illus"]), Counter()).update(r["words"])

    def lexicon(self, rng, size=L):
        chosen = set()
        while len(chosen) < size:
            chosen.update(rng.choices(self.types, self.tw, k=size - len(chosen)))
        ws = sorted(chosen)
        return ws, [self.freq[w] for w in ws]

    def generate(self, mode, seed, p_seed=0.3, p_mut=0.6, rule_p=RULE_P, rule_m=RULE_M,
                 lex_size=L, post=False):
        """post=True applies the line rules to a finished page (a rule of
        layout, not of composition), so copied words never carry them."""
        rng = random.Random(seed)
        lex = {}

        def get(key):
            if key not in lex:
                if mode == "circular":
                    c = self.real[key]; ws = list(c); lex[key] = (ws, [c[w] for w in ws])
                else:
                    lex[key] = self.lexicon(rng, lex_size)
            return lex[key]

        def draw(page, r):
            if mode in ("section", "circular"):
                return rng.choices(*get((r["hand"], r["illus"])))[0]
            if mode == "global":
                return rng.choices(*get(0))[0]
            x = self.page_ix[page] / DRIFT_PAGES          # drift: blend two anchors
            a = int(x)
            return rng.choices(*get(a if rng.random() > x - a else a + 1))[0]

        def mutate(w):
            if rng.random() < p_mut and w in self.nb:
                c, wt = self.nb[w]
                return rng.choices(c, wt)[0]
            return w

        def edge_rules(line):
            if rule_p and rng.random() < rule_p:
                w = line[0]; line[0] = "p" + (w[1:] if w[0] in "ktfq" else w)
            if rule_m and rng.random() < rule_m:
                w = line[-1]; line[-1] = (w[:-1] if w[-1] in "ynlrs" else w) + "m"
            return line

        out = {}
        for page, recs in self.by.items():
            lines = []
            for li, r in enumerate(recs):
                line = []
                for j in range(len(r["words"])):
                    if li == 0 or rng.random() < p_seed:
                        w = draw(page, r)
                    else:
                        same = [l for l in lines if len(l) > j]
                        if same and rng.random() < 0.05:
                            w = rng.choice(same)[j]
                        else:
                            w = rng.choice([x for l in lines for x in l] + line)
                    line.append(mutate(w))
                if not post:
                    edge_rules(line)
                lines.append(line)
            if post:
                lines = [edge_rules(l[:]) for l in lines]
            out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
        return out


WITHIN = (("1", ("H", "P")), ("2", ("B", "H", "T")))


def within_nmi(by, rng):
    """B5 protocol: chunk, refit NMF per hand subset, NMI(cluster, section),
    page-block permutation null and rotation null. Returns dict per hand."""
    ch = b5.chunks_from_pages(by)
    res = {}
    for hand, secs in WITHIN:
        sub = [c for c in ch if c["hand"] == hand and c["illus"] in secs]
        cl = b5.topics([c["text"] for c in sub], k=len(secs) + 2)
        o, m, p99 = b5.score(cl, [c["illus"] for c in sub], rng, [c["block"] for c in sub])
        res[hand] = (o, m, p99, b5.SCORE_ROT[-1][2])
    return res


def nmi_line(name, by, rng):
    r = within_nmi(by, rng)
    emit(f"{name:26} within-hand NMI: hand1 {r['1'][0]:.3f} (perm {r['1'][1]:.3f}, p99 {r['1'][2]:.3f}, rot p={r['1'][3]:.3f})"
         f"   hand2 {r['2'][0]:.3f} (perm {r['2'][1]:.3f}, p99 {r['2'][2]:.3f}, rot p={r['2'][3]:.3f})")
    return r


def main():
    rng = np.random.default_rng(0)
    emit("C2: section-seeded copy-and-mutate generator + line rules vs Voynich targets")
    emit(f"L={L} lexicon types per key; rules: p-initial prob {RULE_P}, m-final prob {RULE_M}; DRIFT_PAGES={DRIFT_PAGES}")
    emit("targets: within-hand NMI 0.275 (hand 1) / 0.333 (hand 2); p-init x15.97, m-final x16.55; h2 2.09; repeat 0.87%; samecol 0.044")
    emit()
    by = b4.pages()
    g = Gen(by)
    R = dict(rule_p=RULE_P, rule_m=RULE_M)
    N = dict(rule_p=0, rule_m=0)
    runs = [("VOYNICH", None),
            ("NULL global, no rules", dict(mode="global", seed=1, p_seed=0.3, **N))]
    runs += [(f"section ps={ps} s{s}", dict(mode="section", seed=s, p_seed=ps, **R))
             for ps in (0.1, 0.3, 0.6, 0.8) for s in (1, 2)]
    runs += [("section ps=0.3 no rules", dict(mode="section", seed=1, p_seed=0.3, **N)),
             ("section ps=0.6 L=150 s1", dict(mode="section", seed=1, p_seed=0.6, lex_size=150, **R)),
             ("section ps=0.6 L=150 s2", dict(mode="section", seed=2, p_seed=0.6, lex_size=150, **R)),
             ("section ps=0.6 rules x2", dict(mode="section", seed=1, p_seed=0.6, rule_p=0.18, rule_m=0.30)),
             ("section ps=0.6 post-rules", dict(mode="section", seed=1, p_seed=0.6, post=True, **R)),
             ("section ps=0.6 L=150 post", dict(mode="section", seed=3, p_seed=0.6, lex_size=150, post=True, **R)),
             *[(f"TUNED L=200 ps=0.6 post s{k}", dict(mode="section", seed=k, p_seed=0.6, lex_size=200,
                                                     post=True, rule_p=0.088, rule_m=0.21)) for k in (4, 5, 6)],
             ("drift ps=0.6", dict(mode="drift", seed=1, p_seed=0.6, **R)),
             ("circular ps=0.3", dict(mode="circular", seed=1, p_seed=0.3, **R)),
             ("circular ps=0.6", dict(mode="circular", seed=1, p_seed=0.6, **R)),
             ("circular ps=0.6 post", dict(mode="circular", seed=1, p_seed=0.6, post=True, **R))]
    emit("--- section NMI (B5 protocol) ---")
    gen = {}
    for name, cfg in runs:
        gen[name] = by if cfg is None else g.generate(**cfg)
        nmi_line(name, gen[name], rng)
    cc = b5.control_chunks("latin_augustine", r"^LIBER ([A-Z ]+?)\.?$")
    o, m, p99 = b5.score(b5.topics([c["text"] for c in cc]), [c["label"] for c in cc], rng, [c["block"] for c in cc])
    emit(f"{'CTRL latin_augustine':26} NMI(cluster, book) {o:.3f} (perm {m:.3f}, p99 {p99:.3f}, rot p={b5.SCORE_ROT[-1][2]:.3f})")
    emit()
    emit("--- line statistics (b4.report, lines 2+ of each page) ---")
    for name, _ in runs:
        b4.report(name, gen[name])
    b4.report("CTRL_dante", lines=b4.verse_lines("italian_dante"))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
