"""N2: N1 rerun with a fine habit grid and an h2 check measured against the manuscript.

Why. In N1 (results_n1.txt) the weakest habit setting, p=0.1, already tripled the
manuscript's residual. The only check that failed was h2 against the p=0
baseline, and h2 had moved TOWARD the manuscript. N1's SURVIVES verdict was
therefore a property of its grid and that check. N2 asks the same question
with those two things fixed. N1 itself is not re-cut.

PRE-REGISTRATION (written 2026-10-17 18:24 PDT before any run of this file;
nothing below is changed after results are seen)

Identical to N1 (n1_habit_table.py, imported unchanged) except:
  Grid  p in {0, 0.01, 0.02, 0.03, 0.04, 0.05}; seeds {1, 2, 3}.
  h2 check  habits must not move h2 AWAY from the manuscript by more than
            0.05 bits:
              |h2(p) - h2(MS)| <= |h2(p=0) - h2(MS)| + 0.05
            (seed means; the plain generator's own h2 gap is not charged to the habits).
Same texts (ZL3b, RF1b, IT2a), the same habit table (seed 20261017, K=4,
Dirichlet 0.5), the same generator, residual (TOPN=300, quire split primary,
pages secondary, page bootstrap B=1000), and the same other checks:
  residual   seed-mean residual >= manuscript CI lower bound
  edge       seed-mean edge MI excess >= 0.75 x the manuscript's
  repeat     repeat % <= 2 x the manuscript's
Same verdicts: per T, DIES if some p > 0 passes all four checks, COSTLY if
the residual bound is reached only with another check failing, SURVIVES if the
bound is never reached, NO POWER if the manuscript CI does not exclude the
p=0 baseline. Overall: DIES if >= 2 of 3 DIE, SURVIVES if none, else MIXED.
Also reported, without effect on the verdict: the smallest p whose seed-mean
residual lies inside the manuscript's 95% CI.
Interpretation fixed in advance: DIES means a weak book-wide word-pair habit
reproduces the manuscript's transferable word order, so F1 no longer
separates encoded text from meaningless generation. SURVIVES/COSTLY keep F1.

Run: python n2_habit_fine.py  -> results_n2.txt
"""
from pathlib import Path

import numpy as np

import c2_section_generator as c2
import f3_flow_choice as f3
import n1_habit_table as N

OUT = Path(__file__).parent / "results_n2.txt"
GRID_P = (0, 0.01, 0.02, 0.03, 0.04, 0.05)
SEEDS = (1, 2, 3)
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


def main():
    emit("N2: fine habit grid, h2 checked against the manuscript (pre-registered in the docstring; N1 code imported unchanged)")
    emit()
    verdicts = {}
    for T, meta in N.TRANSLITS.items():
        by = N.load(meta)
        ms = N.profile(by)
        ms_q, ms_ci = N.residual(by, "quires")
        ms_p, ms_pci = N.residual(by, "pages")
        emit(f"=== {T} ===")
        emit(f"MS          residual quires {ms_q:+.4f} [{ms_ci[0]:+.4f}, {ms_ci[1]:+.4f}]   pages {ms_p:+.4f} [{ms_pci[0]:+.4f}, {ms_pci[1]:+.4f}]"
             f"   edge {ms['edge']:+.3f}  h2 {ms['h2']:.3f}  repeat {ms['redup']:.2f}%")
        g = c2.Gen(by)
        R = f3.ratio_table(by)
        table = N.habit_table(g)
        rows = {}
        for p in GRID_P:
            res = []
            for s in SEEDS:
                gb = N.gen_habit(g, R, s, p, table)
                q, qci = N.residual(gb, "quires")
                pg, _ = N.residual(gb, "pages", boot=False)
                pr = N.profile(gb)
                res.append(dict(q=q, pg=pg, **pr))
                emit(f"HT p={p:<5} s{s}  residual quires {q:+.4f} [{qci[0]:+.4f}, {qci[1]:+.4f}]   pages {pg:+.4f}"
                     f"   edge {pr['edge']:+.3f}  h2 {pr['h2']:.3f}  types {pr['types']}  repeat {pr['redup']:.2f}%")
            rows[p] = {k: float(np.mean([r[k] for r in res])) for k in ("q", "pg", "edge", "h2", "redup")}
        base = rows[0]
        power = ms_ci[0] > base["q"]
        emit(f"power: manuscript CI lower {ms_ci[0]:+.4f} vs p=0 seed mean {base['q']:+.4f} -> {'OK' if power else 'NO POWER'}")
        reached, matched, inside = [], [], []
        gap0 = abs(base["h2"] - ms["h2"])
        for p in GRID_P[1:]:
            r = rows[p]
            checks = dict(resid=r["q"] >= ms_ci[0], edge=r["edge"] >= 0.75 * ms["edge"],
                          h2=abs(r["h2"] - ms["h2"]) <= gap0 + 0.05, repeat=r["redup"] <= 2 * ms["redup"])
            if ms_ci[0] <= r["q"] <= ms_ci[1]:
                inside.append(p)
            emit(f"  p={p:<5} seed mean residual {r['q']:+.4f}  edge {r['edge']:+.3f}  h2 {r['h2']:.3f} (gap {abs(r['h2'] - ms['h2']):.3f} vs p=0 {gap0:.3f})"
                 f"  repeat {r['redup']:.2f}%  " + "  ".join(f"{k}={'ok' if v else 'FAIL'}" for k, v in checks.items()))
            if checks["resid"]:
                reached.append(p)
                if all(checks.values()):
                    matched.append(p)
        v = "NO POWER" if not power else "DIES" if matched else "COSTLY" if reached else "SURVIVES"
        verdicts[T] = v
        emit(f"VERDICT {T}: {v}" + (f" (all checks pass at p={matched})" if matched else f" (bound reached at p={reached})" if reached else "")
             + f"   residual inside manuscript CI at p={inside or 'none'}")
        emit()
    n_dies = sum(v == "DIES" for v in verdicts.values())
    overall = "DIES" if n_dies >= 2 else "SURVIVES" if n_dies == 0 else "MIXED"
    emit(f"OVERALL: {overall}   " + "  ".join(f"{k}={v}" for k, v in verdicts.items()))


if __name__ == "__main__":
    main()
