"""G control 3: the project's own c2_section_generator.py at its best joint setting.

Selection rule (fixed before running): parse results_c2.txt, and for every generator
setting listed there compute the relative deviation |x - target| / target on the seven
targets printed in that file's header (within-hand NMI hand 1 0.275 / hand 2 0.333,
p-init x15.97, m-final x16.55, h2 2.09, repeat 0.87 %, samecol 0.044); the best setting
is the one with the smallest MAXIMUM deviation (minimax). "circular" settings are excluded
(they copy the real per-section vocabulary, an upper bound, not a generator) and so are the
VOYNICH / NULL / CTRL rows. The chosen setting is regenerated with c2's own Gen class
(same seed, same sorted-neighbour patch, so the output is the text results_c2.txt scored)
and written in the shared page/line sidecar format.

Outputs: data/controls_synthetic/c2_best.txt / .meta.json (sidecar carries the chosen
setting, its kwargs and the deviation table).
Run:  python ctl_c2_best.py
"""
import re

import b4_selfcite_sim as b4
import c2_section_generator as c2
import ctl_common as cc

TARGETS = dict(nmi1=0.275, nmi2=0.333, p_init=15.97, m_final=16.55, h2=2.09, repeat=0.87, samecol=0.044)


def settings():
    """Name -> kwargs, replicating c2_section_generator.main()'s run list."""
    R = dict(rule_p=c2.RULE_P, rule_m=c2.RULE_M)
    N = dict(rule_p=0, rule_m=0)
    runs = [(f"section ps={ps} s{s}", dict(mode="section", seed=s, p_seed=ps, **R))
            for ps in (0.1, 0.3, 0.6, 0.8) for s in (1, 2)]
    runs += [("section ps=0.3 no rules", dict(mode="section", seed=1, p_seed=0.3, **N)),
             ("section ps=0.6 L=150 s1", dict(mode="section", seed=1, p_seed=0.6, lex_size=150, **R)),
             ("section ps=0.6 L=150 s2", dict(mode="section", seed=2, p_seed=0.6, lex_size=150, **R)),
             ("section ps=0.6 rules x2", dict(mode="section", seed=1, p_seed=0.6, rule_p=0.18, rule_m=0.30)),
             ("section ps=0.6 post-rules", dict(mode="section", seed=1, p_seed=0.6, post=True, **R)),
             ("section ps=0.6 L=150 post", dict(mode="section", seed=3, p_seed=0.6, lex_size=150, post=True, **R)),
             *[(f"TUNED L=200 ps=0.6 post s{k}", dict(mode="section", seed=k, p_seed=0.6, lex_size=200,
                                                     post=True, rule_p=0.088, rule_m=0.21)) for k in (4, 5, 6)],
             ("drift ps=0.6", dict(mode="drift", seed=1, p_seed=0.6, **R))]
    return dict(runs)


def parse_results():
    txt = (cc.ROOT / "results_c2.txt").read_text(encoding="utf-8").splitlines()
    nmi, line = {}, {}
    for l in txt:
        m = re.match(r"(.+?)\s+within-hand NMI: hand1 ([\d.]+) .*hand2 ([\d.]+)", l)
        if m:
            nmi[m.group(1).strip()] = (float(m.group(2)), float(m.group(3)))
        m = re.match(r"(.+?)\s+JSDfirst=.*p-init x\s*([\d.]+)\s+m-final x\s*([\d.]+)\s+h2=([\d.]+)\s+repeat=([\d.]+)%\s+samecol_edit<=1=([\d.]+)", l)
        if m:
            line[m.group(1).strip()] = dict(p_init=float(m.group(2)), m_final=float(m.group(3)), h2=float(m.group(4)),
                                            repeat=float(m.group(5)), samecol=float(m.group(6)))
    out = {}
    for k in nmi:
        if k in line:
            out[k] = dict(nmi1=nmi[k][0], nmi2=nmi[k][1], **line[k])
    return out


def main():
    res = parse_results()
    cfgs = settings()
    table = []
    for name, v in res.items():
        if name not in cfgs:
            continue
        dev = {k: abs(v[k] - t) / t for k, t in TARGETS.items()}
        worst = max(dev, key=dev.get)
        table.append((dev[worst], name, worst, dev))
    table.sort()
    print("setting                      max rel. dev  (on)      nmi1  nmi2  p-init m-final h2   repeat samecol")
    for mx, name, worst, dev in table:
        print(f"{name:28} {mx:6.3f}  {worst:8}  " + " ".join(f"{dev[k]:5.2f}" for k in TARGETS))
    best = table[0][1]
    cfg = cfgs[best]
    print(f"\nBEST (minimax): {best}  kwargs={cfg}")
    by = b4.pages()
    gen = c2.Gen(by).generate(**cfg)
    pages = []
    for p in cc.voynich_pages():
        recs = gen[p["id"]]
        pages.append(dict(p, lines=[list(r["words"]) for r in recs]))
    b4.report(f"c2 {best} (regen)", gen)
    print(b4.log[-1])
    cc.write_control("c2_best", pages, source="c2_section_generator.Gen (ctl_c2_best.py)", setting=best, kwargs=cfg,
                     selection="minimax relative deviation over results_c2.txt targets",
                     deviations={name: dict(max=mx, worst=worst, **dev) for mx, name, worst, dev in table})
    print(cc.stats_row("c2_best", cc.ctl_stats(pages)))


if __name__ == "__main__":
    main()
