"""C3: score generators on cross-space edge coupling (Rozanova & Temerev 2026).

Their reported target (abstract-level, arXiv 2608.17096; definition not
checked against the full paper): glyphs at token edges share ~0.2 bits of
mutual information across the space, more than any prose control; keyless
generators give ~0.001-0.009 bits (Schwartz 2026, via our research notes).
Our reimplementation:
  MI(last glyph of token i ; first glyph of token i+1), adjacent tokens in the
  same line, plug-in estimate in bits. Null: tokens shuffled within each line
  (keeps every marginal, breaks adjacency), 20 reps; we report raw MI, null
  mean, and excess = raw - null. Both EVA characters and the glyph+ units of
  corpora.GLYPHS_PLUS (ch, sh, iin, ...) are scored.
Texts: Voynich (all running text; Currier A; Currier B), Voynich token-shuffled
across the manuscript (null), b4 self-citation generators, c2 section
generators (with/without line rules, drift, circular), and the six prose
controls cut into 9-word pseudo-lines (Voynich mean line length ~ 9 tokens),
first 33,000 tokens each.
Run: python c3_edge_coupling.py  -> results_c3.txt
"""
import math
import random
from collections import Counter
from pathlib import Path

import corpora
import b4_selfcite_sim as b4
import c2_section_generator as c2

OUT = Path(__file__).parent / "results_c3.txt"
NREP = 20
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def mi(pairs):
    n = len(pairs)
    pj = Counter(pairs); pa = Counter(a for a, _ in pairs); pb = Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pj.items())


def edge_pairs(lines, unit):
    out = []
    for ws in lines:
        g = [unit(w) for w in ws]
        out += [(a[-1], b[0]) for a, b in zip(g, g[1:]) if a and b]
    return out


def score(lines, unit):
    obs = mi(edge_pairs(lines, unit))
    rng = random.Random(0)
    nul = []
    for _ in range(NREP):
        sh = []
        for ws in lines:
            ws = ws[:]; rng.shuffle(ws); sh.append(ws)
        nul.append(mi(edge_pairs(sh, unit)))
    m = sum(nul) / NREP
    sd = (sum((x - m) ** 2 for x in nul) / NREP) ** 0.5
    return obs, m, obs - m, (obs - m) / sd if sd else float("inf")


EVA = lambda w: w
GLY = lambda w: corpora.to_glyphs(w, corpora.GLYPHS_PLUS)


def row(name, lines):
    a = score(lines, EVA)
    b = score(lines, GLY)
    emit(f"{name:30} EVA: MI={a[0]:.4f} null={a[1]:.4f} excess={a[2]:+.4f} (z {a[3]:6.1f})"
         f"   glyph+: MI={b[0]:.4f} null={b[1]:.4f} excess={b[2]:+.4f} (z {b[3]:6.1f})"
         f"   pairs={len(edge_pairs(lines, EVA))}")
    return a, b


def pages_lines(by):
    return [r["words"] for recs in by.values() for r in recs]


def prose_lines(name, n=33000, width=9):
    ws = corpora.control(name, n)
    return [ws[i:i + width] for i in range(0, len(ws), width)]


def main():
    emit("C3: cross-space edge coupling, MI(last glyph of token i ; first glyph of token i+1), bits")
    emit(f"null = tokens shuffled within each line ({NREP} reps); excess = MI - null mean; z = excess / null sd")
    emit("published target (abstract-level): ~0.2 bits real, > all prose controls; keyless generators ~0.001-0.009")
    emit()
    by = b4.pages()
    row("VOYNICH all", pages_lines(by))
    row("VOYNICH Currier A", [r["words"] for recs in by.values() for r in recs if r["lang"] == "A"])
    row("VOYNICH Currier B", [r["words"] for recs in by.values() for r in recs if r["lang"] == "B"])
    import vparse
    strict = [[w for w in r["words"] if "?" not in w] for r in vparse.paragraph_text(vparse.load(strict_spaces=True))]
    row("VOYNICH uncertain spaces joined", [l for l in strict if l])
    flat = [w for recs in by.values() for r in recs for w in r["words"]]
    random.Random(5).shuffle(flat)
    it = iter(flat)
    row("NULL token-shuffled", [[next(it) for _ in r["words"]] for recs in by.values() for r in recs])
    emit()
    for name, args in (("b4 SIM_global", ("global", 1, {})), ("b4 SIM_seeded", ("seeded", 1, {})),
                       ("b4 SIMcal_global", ("global", 3, dict(p_samecol=0.05, p_mut=0.97, recent_lines=99))),
                       ("b4 SIMcal_seeded", ("seeded", 3, dict(p_samecol=0.05, p_mut=0.97, recent_lines=99)))):
        row(name, pages_lines(b4.generate(args[0], args[1], by, **args[2])))
    g = c2.Gen(by)
    for name, cfg in (("c2 global, no rules", dict(mode="global", seed=1, p_seed=0.3, rule_p=0, rule_m=0)),
                      ("c2 section ps=0.6", dict(mode="section", seed=2, p_seed=0.6)),
                      ("c2 TUNED L=200 post s5", dict(mode="section", seed=5, p_seed=0.6, lex_size=200, post=True,
                                                      rule_p=0.088, rule_m=0.21)),
                      ("c2 drift ps=0.6", dict(mode="drift", seed=1, p_seed=0.6)),
                      ("c2 circular ps=0.6", dict(mode="circular", seed=1, p_seed=0.6))):
        row(name, pages_lines(g.generate(**cfg)))
    emit()
    for name in corpora.CONTROLS:
        row(f"CTRL {name}", prose_lines(name))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
