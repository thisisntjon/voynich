"""F3: the "flow-choice" scribe - meaning-bearing cipher vs meaningless generator.

F1/F2 constraint: Voynich has prose-sized cross-space edge coupling (MI excess
+0.18) but only cipher-sized word order beyond the edges (residual +0.04,
Naibbe +0.04, prose +0.10-0.42, copy generators 0.00). Syllable-spaced
language overshoots both (F2).
Mechanism tested: whenever the producer has a free choice between equivalent
tokens, it prefers the one whose first glyph "flows" from the previous
token's last glyph. Weight of a candidate t after token p:
    w(t) = base(t) * R(first(t) | last(p)) ** BETA,
    R = P_vms(first | last) / P_vms(first)   (Voynich E2 table, within lines)
R is taken from Voynich itself: this tests whether the mechanism CAN carry
the observed table without destroying anything else, not where the table
comes from (as Naibbe's own tables are filled with Voynich words).
Two producers:
  CIPHER  Naibbe re-encryption of the same plaintext chunk sequence (from the
          workbook's 'encrypter' sheet: chunk letters, then the six-table
          homophone pieces per letter and role, rebuilt from all 22k rows).
          Candidates = every prefix x suffix (bigram) or unigram homophone of
          the chunk, base = observed piece frequencies.
  GEN     c2 section generator (ps=0.6), with each word chosen among 8
          candidates drawn by the normal copy/lexicon/mutate step.
BETA = 0 reproduces the plain producer (sanity: matches c4 / c2).
Battery (as F2): c3 cross MI excess, F1 edge/residual excess (top-300),
h2, length, types, hapax; plus line JSD and p/m enrichment (b4.report).
Run: python f3_flow_choice.py  -> results_f3.txt
"""
import random
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

import b4_selfcite_sim as b4
import c2_section_generator as c2
import c4_naibbe_lines as c4
import f1_residual_order as f1
import f2_syllable_control as f2

OUT = Path(__file__).parent / "results_f3.txt"
M_CAND = 8
log = f2.log


def emit(s=""):
    f2.emit(s)


def ratio_table(by):
    pairs = [(a[-1], b[0]) for recs in by.values() for r in recs for a, b in zip(r["words"], r["words"][1:])]
    pj = Counter(pairs); pl = Counter(a for a, _ in pairs); pf = Counter(b for _, b in pairs); n = len(pairs)
    return lambda last, first: (pj.get((last, first), 0) + 0.5) / (pl.get(last, 0) + 0.5) / ((pf.get(first, 0) + 0.5) / n)


def naibbe_chunks():
    """Returns the chunk sequence [(letters...)] and piece tables
    role -> letter -> Counter(piece). Roles: 'u' unigram, 'p' bigram prefix, 's' bigram suffix."""
    wb = openpyxl.load_workbook(c4.XLSX, read_only=True, data_only=True)
    seq, tab = [], defaultdict(lambda: defaultdict(Counter))
    for r in wb["encrypter"].iter_rows(min_row=15, max_col=19, values_only=True):
        if r[2] not in (1, 2) or not r[4] or not r[18] or r[18] == "XXXXX":
            continue
        letters = [x for x in r[5:5 + r[2]] if x]
        pieces = [x for x in r[14:14 + r[2]] if x]
        if len(letters) != r[2] or len(pieces) != r[2]:
            continue
        seq.append((tuple(letters), r[18]))
        if r[2] == 1:
            tab["u"][letters[0]][pieces[0]] += 1
        else:
            tab["p"][letters[0]][pieces[0]] += 1; tab["s"][letters[1]][pieces[1]] += 1
    return seq, tab


def cipher_stream(seq, tab, R, beta, seed):
    rng = random.Random(seed)
    out, prev = [], None
    for letters, orig in seq:
        if len(letters) == 1:
            cand = list(tab["u"][letters[0]].items())
        else:
            P = tab["p"][letters[0]].items(); S = tab["s"][letters[1]].items()
            cand = [(a + b, ca * cb) for a, ca in P for b, cb in S]
        if not cand:
            tok = orig
        else:
            ws = [c * (R(prev[-1], t[0]) ** beta if prev and beta else 1) for t, c in cand]
            tok = rng.choices([t for t, _ in cand], ws)[0]
        out.append(tok); prev = tok
    return out


def gen_flow(g, R, beta, seed, p_seed=0.6, p_mut=0.6, p_pair=0.0):
    """c2 section generator, choosing each word among M_CAND normal draws.
    p_pair: run-copying - copy the word that followed an earlier occurrence
    of the previous word on this page (the rebuttal: fake word order)."""
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
            for j in range(len(r["words"])):
                cands = []
                for _ in range(M_CAND if beta else 1):
                    succ = None
                    if p_pair and line and rng.random() < p_pair:
                        flat = [x for l in lines for x in l] + line
                        nxt = [flat[i + 1] for i in range(len(flat) - 1) if flat[i] == line[-1]]
                        succ = rng.choice(nxt) if nxt else None
                    if succ:
                        w = succ
                    elif li == 0 or rng.random() < p_seed:
                        w = draw(r)
                    else:
                        pool = [x for l in lines for x in l] + line
                        w = rng.choice(pool)
                    cands.append(mutate(w))
                if line and beta:
                    w = rng.choices(cands, [R(line[-1][-1], c[0]) ** beta for c in cands])[0]
                else:
                    w = cands[0]
                line.append(w)
            lines.append(line)
        out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
    return out


def resid_excess(tr, te):
    f1.TOPN = 300
    U, E, E2, W, _ = f1.evaluate(tr, te)
    sU, _, sE2, sW, _ = f1.evaluate(f1.shuffled(tr), f1.shuffled(te))
    return (E2 - W) - (sE2 - sW)


def splits(by):
    """page even/odd, page odd/even, alternate quires (train on A,C,E..; test on B,D,..)"""
    pages = list(by.values())
    qs = sorted({recs[0]["quire"] for recs in pages})
    qtrain = set(qs[::2])
    out = {}
    for name, sel in (("pages even->odd", lambda i, recs: i % 2 == 0),
                      ("pages odd->even", lambda i, recs: i % 2 == 1),
                      ("quires alt", lambda i, recs: recs[0]["quire"] in qtrain)):
        tr = [r["words"] for i, recs in enumerate(pages) if sel(i, recs) for r in recs]
        te = [r["words"] for i, recs in enumerate(pages) if not sel(i, recs) for r in recs]
        out[name] = (tr, te)
    return out


def main():
    emit("F3: flow-choice producers (homophone / candidate chosen by R(first | previous last)^BETA)")
    emit("battery as F2; line rows = b4.report on lines 2+")
    emit()
    by = b4.pages()
    R = ratio_table(by)
    f2.battery("VOYNICH", [r["words"] for recs in by.values() for r in recs], f1.split_pages(by))
    seq, tab = naibbe_chunks()
    emit(f"Naibbe chunks rebuilt: {len(seq)}; unigram letters {len(tab['u'])}, prefix {len(tab['p'])}, suffix {len(tab['s'])};"
         f" homophones per unigram letter (median) {sorted(len(v) for v in tab['u'].values())[len(tab['u']) // 2]}")
    emit()
    streams = {}
    for beta in (0, 1, 2, 3):
        toks = cipher_stream(seq, tab, R, beta, seed=1)
        sk = c4.skeleton(toks, by)
        streams[f"CIPHER flow beta={beta}"] = sk
        f2.battery(f"CIPHER flow beta={beta}", [r["words"] for recs in sk.values() for r in recs], f1.split_pages(sk))
    emit()
    g = c2.Gen(by)
    for beta in (0, 1, 2, 3):
        for seed in (1, 2):
            gb = gen_flow(g, R, beta, seed)
            streams[f"GEN flow beta={beta} s{seed}"] = gb
            f2.battery(f"GEN flow beta={beta} s{seed}", [r["words"] for recs in gb.values() for r in recs], f1.split_pages(gb))
    emit()
    toks = cipher_stream(seq, tab, R, 1.5, seed=2)
    sk = c4.skeleton(toks, by)
    f2.battery("CIPHER flow beta=1.5", [r["words"] for recs in sk.values() for r in recs], f1.split_pages(sk))
    for pp in (0.1, 0.3, 0.5):
        for seed in (1, 2):
            gb = gen_flow(g, R, 1.5, seed, p_pair=pp)
            f2.battery(f"GEN flow1.5 run-copy {pp} s{seed}", [r["words"] for recs in gb.values() for r in recs], f1.split_pages(gb))
    emit()
    emit("--- residual excess under stricter splits (quire split removes neighbouring-page leakage) ---")
    cands = {"VOYNICH": by, "CIPHER flow beta=1.5": sk,
             "GEN flow1.5 s1": gen_flow(g, R, 1.5, 1), "GEN flow1.5 run-copy 0.3 s1": gen_flow(g, R, 1.5, 1, p_pair=0.3)}
    for name, b in cands.items():
        vals = {k: resid_excess(*v) for k, v in splits(b).items()}
        emit(f"{name:28} " + "  ".join(f"{k}: {v:+.3f}" for k, v in vals.items()))
    emit()
    emit("--- line statistics (no line rules in any producer) ---")
    b4.log.clear()
    b4.report("VOYNICH", by)
    for k in ("CIPHER flow beta=0", "CIPHER flow beta=2", "GEN flow beta=0 s1", "GEN flow beta=2 s1"):
        b4.report(k, streams[k])
    log.extend(b4.log)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
