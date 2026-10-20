"""N1: does a meaningless generator with a fixed word-pair habit table produce
the manuscript's transferable word order?

Background. F1/F3 measure the "residual": held-out bits per token that the
previous WORD buys beyond the previous word's last one or two glyphs (the
cross-space edge table), minus the same quantity on within-line-shuffled text.
The manuscript scores about +0.04. Every meaningless generator tested so far
scores at most +0.017, and letter ciphers of real text score +0.03 to +0.06. That gap is
the main result favouring encoded text. The obvious rebuttal, never tested:
a scribe producing meaningless text with fixed word-pair HABITS shared across
the whole book would also leave transferable word order, without meaning.

PRE-REGISTRATION (written 2026-10-17 18:17 PDT before any run of this file;
nothing below is changed after results are seen)

Texts, per transliteration T in {ZL3b (EVA), RF1b, IT2a}, all loaded from
data/translit/<T>.meta.json, running-text units only:
  MS        the manuscript itself.
  HT(p, s)  habit-table generator: f3.gen_flow (the c2 section generator,
            flow choice beta=1.5 over M_CAND=8 candidates, p_seed=0.6,
            p_mut=0.6; all inherited, not re-tuned), except that each
            candidate after the first word of a line is, with probability p,
            a HABIT follower of the previous word instead of a normal draw.
            Habit followers are not mutated.
            Habit table: built once per T with seed 20261017 and never from
            manuscript word PAIRS. Every type with count >= 2 gets K=4
            followers sampled from the same type list with sqrt-frequency
            weights; follower weights ~ Dirichlet(0.5).
            Grid p in {0, 0.1, 0.25, 0.5}; seeds s in {1, 2, 3}. p=0 is the
            plain meaningless baseline.

Metric. Residual excess with f1's models (Witten-Bell, TOPN=300 target
vocabulary, smoothing chosen on the test half exactly as f1.evaluate).
Primary split: alternate quires (train A,C,E,..; test B,D,..). Secondary:
pages even->odd. 95% CI by page bootstrap: test pages resampled with
replacement, B=1000, models fixed and per-page log-prob sums reused. Also
reported, from the whole text: cross-space edge MI excess (c3.score, EVA),
h2, types, hapax share, immediate repeat %.

Decision rule (primary split; ZL3b, RF1b and IT2a each judged separately):
  The manuscript CI must exclude the p=0 baseline (seed mean), or the
  discriminator has NO POWER on T.
  HT "matches" at p > 0 if ALL of these hold:
     seed-mean residual >= manuscript CI lower bound
     seed-mean edge MI excess >= 0.75 x the manuscript's
     |h2 - h2(p=0)| <= 0.05 (habits did not change the character statistics)
     repeat % <= 2 x the manuscript's
  T verdict: DIES if some p matches. SURVIVES if no p reaches the residual
  bound. COSTLY if the residual bound is reached only at settings that fail
  another check (habits can fake word order, but only by breaking that check).
  Overall: DIES if DIES on >= 2 of 3 transliterations; SURVIVES if no T DIES;
  otherwise MIXED.
Interpretation fixed in advance: DIES means transferable word order no
longer separates encoded text from meaningless generation. SURVIVES/COSTLY
keep it as evidence for the encoded-text families (or a genuine grammar).

Run: python n1_habit_table.py  -> results_n1.txt
"""
import json
import math
import random
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

import numpy as np

import a1_profile
import c2_section_generator as c2
import c3_edge_coupling as c3
import f1_residual_order as f1
import f3_flow_choice as f3

HERE = Path(__file__).parent
OUT = HERE / "results_n1.txt"
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
GRID_P = (0, 0.1, 0.25, 0.5)
SEEDS = (1, 2, 3)
K_FOLLOW, DIR_ALPHA, TABLE_SEED = 4, 0.5, 20261017
BETA, B_BOOT = 1.5, 1000
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- data
def load(name):
    d = json.loads((HERE / "data" / "translit" / f"{name}.meta.json").read_text(encoding="utf-8"))
    by = OrderedDict()
    for p in d["pages"]:
        recs = [dict(page=p["id"], words=l, hand=p["hand"], illus=p["section"], quire=p["quire"], lang=p["lang"])
                for l in p["lines"] if l]
        if recs:
            by[p["id"]] = recs
    return by


# ---------------------------------------------------------------- generator
def habit_table(g):
    rng = random.Random(TABLE_SEED)
    nrng = np.random.default_rng(TABLE_SEED)
    table = {}
    for w in g.types:
        fol = rng.choices(g.types, g.tw, k=K_FOLLOW)
        table[w] = (fol, list(nrng.dirichlet([DIR_ALPHA] * K_FOLLOW)))
    return table


def gen_habit(g, R, seed, p_hab, table, p_seed=0.6, p_mut=0.6):
    """f3.gen_flow with habit candidates (see docstring)."""
    rng = random.Random(seed)
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
            line = []
            for _ in range(len(r["words"])):
                cands = []
                for _ in range(f3.M_CAND):
                    if line and p_hab and line[-1] in table and rng.random() < p_hab:
                        cands.append(rng.choices(*table[line[-1]])[0])
                        continue
                    if li == 0 or rng.random() < p_seed:
                        w = draw(r)
                    else:
                        w = rng.choice([x for l in lines for x in l] + line)
                    cands.append(mutate(w))
                if line:
                    w = rng.choices(cands, [R(line[-1][-1], c[0]) ** BETA for c in cands])[0]
                else:
                    w = cands[0]
                line.append(w)
            lines.append(line)
        out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
    return out


# ---------------------------------------------------------------- residual with page bootstrap
def split(by, kind):
    pages = list(by.items())
    if kind == "quires":
        qs = sorted({recs[0]["quire"] for _, recs in pages})
        qtrain = set(qs[::2])
        sel = lambda i, recs: recs[0]["quire"] in qtrain
    else:
        sel = lambda i, recs: i % 2 == 0
    tr = [r["words"] for i, (_, recs) in enumerate(pages) if sel(i, recs) for r in recs]
    te = [(p, r["words"]) for i, (p, recs) in enumerate(pages) if not sel(i, recs) for r in recs]
    return tr, te


def page_sums(train, test_pl):
    """Per test page: (n pairs, sum bits E2, sum bits W) with f1.evaluate's parameter choice."""
    f1.TOPN = 300
    f = f1.mapper(train, 300)
    m = f1.Models(train, f)
    test = [l for _, l in test_pl]
    tp = [(a, f(b)) for a, b in f1.pairs_of(test)]
    a_best = min(f1.GRID_A, key=lambda x: f1.bits(tp, lambda a, b: m.pe2(a, b, x)))
    k_best = min(f1.GRID_K, key=lambda k: f1.bits(tp, lambda a, b: m.pw(a, b, a_best, k)))
    sums = defaultdict(lambda: np.zeros(3))
    for p, l in test_pl:
        for a, b in zip(l, l[1:]):
            b = f(b)
            sums[p] += (1, -math.log2(m.pe2(a, b, a_best)), -math.log2(m.pw(a, b, a_best, k_best)))
    return sums


def residual(by, kind, boot=True):
    tr, te = split(by, kind)
    real = page_sums(tr, te)
    rng = random.Random(3)
    sh_tr = [rng.sample(l, len(l)) for l in tr]
    sh_te = [(p, rng.sample(l, len(l))) for p, l in te]
    shuf = page_sums(sh_tr, sh_te)
    pages = sorted(real)
    R = np.array([real[p] for p in pages]); S = np.array([shuf[p] for p in pages])

    def stat(ix):
        r = R[ix].sum(0); s = S[ix].sum(0)
        return (r[1] - r[2]) / r[0] - (s[1] - s[2]) / s[0]

    full = stat(np.arange(len(pages)))
    if not boot:
        return full, None
    brng = np.random.default_rng(7)
    bs = [stat(brng.integers(0, len(pages), len(pages))) for _ in range(B_BOOT)]
    return full, tuple(np.percentile(bs, [2.5, 97.5]))


def profile(by):
    lines = [r["words"] for recs in by.values() for r in recs]
    words = [w for l in lines for w in l]
    c = Counter(words)
    return dict(edge=c3.score(lines, c3.EVA)[2], h2=a1_profile.char_entropies(words)["h2"], types=len(c),
                hapax=sum(v == 1 for v in c.values()) / len(c),
                redup=100 * sum(a == b for l in lines for a, b in zip(l, l[1:])) / max(1, sum(len(l) - 1 for l in lines)))


# ---------------------------------------------------------------- main
def main():
    emit("N1: habit-table generator vs the manuscript's transferable word order (pre-registered in the docstring)")
    emit("residual = held-out bits the previous word buys beyond the edge table, minus within-line shuffle (TOPN=300)")
    emit()
    verdicts = {}
    for T, meta in TRANSLITS.items():
        by = load(meta)
        ms_prof = profile(by)
        ms_q, ms_ci = residual(by, "quires")
        ms_p, ms_pci = residual(by, "pages")
        emit(f"=== {T}: {sum(len(r['words']) for recs in by.values() for r in recs)} tokens, {len(by)} pages ===")
        emit(f"MS            residual quires {ms_q:+.4f} [{ms_ci[0]:+.4f}, {ms_ci[1]:+.4f}]   pages {ms_p:+.4f} "
             f"[{ms_pci[0]:+.4f}, {ms_pci[1]:+.4f}]   edge {ms_prof['edge']:+.3f}  h2 {ms_prof['h2']:.3f}  "
             f"types {ms_prof['types']}  hapax {ms_prof['hapax']:.2f}  repeat {ms_prof['redup']:.2f}%")
        g = c2.Gen(by)
        R = f3.ratio_table(by)
        table = habit_table(g)
        rows = {}
        for p in GRID_P:
            res = []
            for s in SEEDS:
                gb = gen_habit(g, R, s, p, table)
                q, qci = residual(gb, "quires")
                pg, _ = residual(gb, "pages", boot=False)
                pr = profile(gb)
                res.append(dict(q=q, qci=qci, pg=pg, **pr))
                emit(f"HT p={p:<4} s{s}   residual quires {q:+.4f} [{qci[0]:+.4f}, {qci[1]:+.4f}]   pages {pg:+.4f}   "
                     f"edge {pr['edge']:+.3f}  h2 {pr['h2']:.3f}  types {pr['types']}  hapax {pr['hapax']:.2f}  repeat {pr['redup']:.2f}%")
            rows[p] = {k: float(np.mean([r[k] for r in res])) for k in ("q", "pg", "edge", "h2", "types", "hapax", "redup")}
            rows[p]["qci_hi"] = float(np.mean([r["qci"][1] for r in res]))
        base = rows[0]
        power = ms_ci[0] > base["q"]
        emit(f"power: manuscript CI lower {ms_ci[0]:+.4f} vs p=0 baseline seed mean {base['q']:+.4f} -> {'OK' if power else 'NO POWER'}")
        reached, matched = [], []
        for p in GRID_P[1:]:
            r = rows[p]
            checks = dict(resid=r["q"] >= ms_ci[0], edge=r["edge"] >= 0.75 * ms_prof["edge"],
                          h2=abs(r["h2"] - base["h2"]) <= 0.05, repeat=r["redup"] <= 2 * ms_prof["redup"])
            emit(f"  p={p:<4} seed mean residual {r['q']:+.4f}  edge {r['edge']:+.3f}  h2 {r['h2']:.3f}  repeat {r['redup']:.2f}%  "
                 + "  ".join(f"{k}={'ok' if v else 'FAIL'}" for k, v in checks.items()))
            if checks["resid"]:
                reached.append(p)
                if all(checks.values()):
                    matched.append(p)
        v = "NO POWER" if not power else "DIES" if matched else "COSTLY" if reached else "SURVIVES"
        verdicts[T] = v
        emit(f"VERDICT {T}: {v}" + (f" (matches at p={matched})" if matched else f" (bound reached at p={reached})" if reached else ""))
        emit()
    n_dies = sum(v == "DIES" for v in verdicts.values())
    overall = "DIES" if n_dies >= 2 else "SURVIVES" if n_dies == 0 else "MIXED"
    emit(f"OVERALL: {overall}   " + "  ".join(f"{k}={v}" for k, v in verdicts.items()))


if __name__ == "__main__":
    main()
