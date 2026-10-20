"""s110 diagnostic after fixture run 2 (FAIL), before revision 2. Synthetic planted G2b world only (no Voynich data).
Per fold: fitted-model replicate and oracle replicate (true generator), per-prediction battery holds vs the planted
held-out quire, plus generated vs real point values for P1-P5 and the type ratio."""
import sys
sys.path.insert(0, r".")
import numpy as np
import s110_g2_combinatory_grid as M
S97, S67 = M.S97, M.S67


def main():
    SEED = M.SEED
    layout, qs = M.fx_layout(SEED); ntok = sum(sum(l) for _, _, l in layout)
    rng = np.random.default_rng([SEED, 7])
    pm, pre_s, Tm = M.fx_world_model(SEED)
    pg1, _ = pm.gen_ids(layout, rng.random(ntok), rng)
    tp = [(pid, q, ls) for (pid, q, _), (_, ls) in zip(layout, pg1)]
    jobs = [dict(key=("FX1", fi), train=[x for x in tp if x[1] != Q], seed=SEED + fi) for fi, Q in enumerate(qs)]
    FITS = M.fits_pool(jobs, "diag fits")
    MJ, TX = [], {}
    for fi, Q in enumerate(qs):
        MJ.append(dict(key=("REF", fi), name="r", train=[(p, ls) for p, q, ls in tp if q != Q], test=[(p, ls) for p, q, ls in tp if q == Q], seed=SEED + 30000 + fi))
        for lab, fit in (("FIT", FITS[("FX1", fi)]), ("OR", dict(g2b=pm, g2a=None))):
            tr, te, H = M.loqo_texts("G2b", fit, tp, Q, None, M.FxCodebook(), np.random.default_rng([SEED, 9, fi, len(lab)]))
            TX[(lab, fi)] = te
            MJ.append(dict(key=(lab, fi), name=lab, train=tr, test=te, seed=SEED + 40000 + 100 * len(lab) + fi))
    R = M.battery_pool(MJ, "diag battery")
    cnt = {lab: {k: 0 for k in S67.PREDS} for lab in ("FIT", "OR")}
    for fi, Q in enumerate(qs):
        rm, rdr = R[("REF", fi)]
        f = FITS[("FX1", fi)]["g2b"].fit_info
        for lab in ("FIT", "OR"):
            gm, gdr = R[(lab, fi)]
            cells, gpt, rt, _ = S67.score_model(rm, rm.point(), rdr, [gm], gdr, rm.n_test, [[ls for _, ls in TX[(lab, fi)]]], [ls for p, q, ls in tp if q == Q])
            for k in S67.PREDS:
                cnt[lab][k] += bool(cells[k][0])
            print(f"{Q} {lab:3s} " + "".join("+" if cells[k][0] else "-" for k in S67.PREDS) + " | real " + " ".join(f"{k} {rm.point()[k]:+.4f}" for k in ("P1", "P2", "P3", "P4", "P5"))
                  + " | gen " + " ".join(f"{k} {gpt[k]:+.4f}" for k in ("P1", "P2", "P3", "P4", "P5")) + f" | types {rt:.3f}"
                  + (f" | phi {f['phi']} m {f['m']} n_pre {f['n_pre']} n_suf {f['n_suf']} cores {f['n_cores']}" if lab == "FIT" else ""), flush=True)
    for lab in cnt:
        print(lab, "holds per prediction over 15 folds:", cnt[lab])


if __name__ == "__main__":
    main()
