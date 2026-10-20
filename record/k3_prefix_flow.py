"""K3: stem codebook + flow-chosen prefix slot.

K2 trade-off: homophones as whole separate codewords buy edge coupling and
line effects only by inflating the type count (14-23k vs 7k) and h2, and
they wash out section NMI and word order. Voynich has 0.18-bit edge
coupling with 7k types. Hypothesis: the meaning sits in a STEM (codebook,
few homophones, K2 x2 which matched NMI and residual) and the edge coupling
sits in a small PREFIX slot chosen to flow from the previous glyph (Voynich
qo-, o-, d-, ch-, sh-, y-... families).

Prefix inventory and its conditional use come from Voynich itself (circular,
like R and Naibbe's tables): every Voynich token is decomposed as prefix +
remainder with the longest prefix from PREFIXES whose remainder is an
attested type; P(prefix | previous token's last glyph) and P(prefix |
line position class) are counted on within-line pairs. Stems: K2 codebook
at scale 2 over the K2 codeword pool restricted to words that do not start
with a prefix. Token = prefix + stem; prefix chosen with weight
P(prefix | prev last) * positional factor of the resulting token (k1.pos_factor),
and only prefixes whose junction bigram is attested in Voynich.
Rows: Voynich, K2 x2 (no prefix slot), K3 with the prefix slot, K3 null
(plaintext shuffled), K3 with prefixes chosen at random (no flow) to
separate the slot from the flow.
Run: python k3_prefix_flow.py  -> results_k3.txt
"""
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import c2_section_generator as c2
import f3_flow_choice as f3
import k1_joint_producer as k1
import k2_nomenclator as k2

OUT = Path(__file__).parent / "results_k3.txt"
PREFIXES = ["qok", "qot", "qo", "q", "ok", "ot", "o", "d", "ch", "sh", "y", "s", "l", "k", "t", "p", "f", "a"]
log = k1.log


def decompose(w, types):
    for p in sorted(PREFIXES, key=len, reverse=True):
        if w.startswith(p) and len(w) > len(p) and w[len(p):] in types:
            return p, w[len(p):]
    return "", w


def prefix_tables(by, g):
    types = set(g.freq)
    cond = defaultdict(Counter)
    for recs in by.values():
        for r in recs:
            ws = r["words"]
            for a, b in zip(["^"] + ws, ws):
                cond[a[-1] if a != "^" else "^"][decompose(b, types)[0]] += 1
    return cond


def encrypt(by, streams, book, cond, big, Qi, Qe, para, seed, flow=True):
    rng = random.Random(seed)
    its = {k: iter(v) for k, v in streams.items()}
    ptypes, pw = list(para), list(para.values())
    allp = Counter()
    for c in cond.values():
        allp.update(c)
    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            n = len(r["words"]); line = []
            for i in range(n):
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pw)[0]); continue
                stems = book[next(its[(r["hand"], r["illus"])])]
                stem = rng.choices([s for s, _ in stems], [c for _, c in stems])[0]
                ctx = line[-1][-1] if line else "^"
                dist = cond[ctx] if flow else allp
                cands = [(p, c) for p, c in dist.items() if p == "" or big[(p[-1], stem[0])]]
                if not cands:
                    cands = [("", 1)]
                ws = [c * k1.pos_factor(p + stem, i, n, Qi, Qe) for p, c in cands]
                p = rng.choices([p for p, _ in cands], ws)[0]
                line.append(p + stem)
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


def main():
    rng = np.random.default_rng(0)
    k1.emit("K3: stem codebook (K2 x2) + flow-chosen prefix slot + M5 layer; columns as K1")
    k1.emit()
    by = k1.layout()
    Qi, Qe, para = k1.line_tables(by)
    R = f3.ratio_table(by)
    g = c2.Gen(by)
    cond = prefix_tables(by, g)
    big = Counter()
    for w, c in g.freq.items():
        for a, b in zip(w, w[1:]):
            big[(a, b)] += c
    types = set(g.freq)
    share = sum(1 for w in g.freq.elements() if decompose(w, types)[0]) / sum(g.freq.values())
    k1.emit(f"Voynich tokens with a decomposable prefix: {share:.1%}; P(prefix|prev last) for y: "
            + ", ".join(f"{p or '-'}:{c / sum(cond['y'].values()):.2f}" for p, c in cond["y"].most_common(6)))
    k1.bench("VOYNICH", by, rng)
    streams = k2.plaintext_streams(by)
    allw = [w for v in streams.values() for w in v]
    pool = k2.codeword_pool(g, 120_000)
    k1.bench("K2 nomenclator x2", k2.encrypt(by, streams, k2.codebook(allw, g, 2.0, pool)[0], R, Qi, Qe, para, 1), rng)
    spool = [w for w in pool if decompose(w, types)[0] == "" and not any(w.startswith(p) for p in ("q", "o", "d", "y"))]
    for scale in (1.0, 2.0):
        book = k2.codebook(allw, g, scale, spool)[0]
        k1.bench(f"K3 stem x{scale} + flow prefix", encrypt(by, streams, book, cond, big, Qi, Qe, para, 1), rng)
    book = k2.codebook(allw, g, 2.0, spool)[0]
    k1.bench("K3 x2, prefix NOT flow", encrypt(by, streams, book, cond, big, Qi, Qe, para, 1, flow=False), rng)
    shuf = k2.plaintext_streams(by, shuffle=True)
    book = k2.codebook([w for v in shuf.values() for w in v], g, 2.0, spool)[0]
    k1.bench("K3 x2 NULL shuffled plain", encrypt(by, shuf, book, cond, big, Qi, Qe, para, 1), rng)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
