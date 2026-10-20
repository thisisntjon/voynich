import sys, time
sys.path.insert(0, r".")
import numpy as np
import s110_g2_combinatory_grid as M
S97, S67, S87, S91 = M.S97, M.S67, M.S87, M.S91
from scoreboard.metrics_new import SlotSegmenter
def main():
    SEED = M.SEED
    layout, qs = M.fx_layout(SEED); ntok = sum(sum(l) for _,_,l in layout)
    rng = np.random.default_rng([SEED, 7])
    pm, pre_s, Tm = M.fx_world_model(SEED)
    pg1, _ = pm.gen_ids(layout, rng.random(ntok), rng)
    planted = [(pid,q,ls) for (pid,q,_),(_,ls) in zip(layout,pg1)]
    gmap = {s:g for s,g in zip(M.SYM_RANK, M.FX_GROUPS)}
    nl = sum(len(l) for _,_,l in layout); u2 = rng.random(nl)
    pg2, rows2 = M.g2a_gen(gmap, layout, u2)
    planted_a = [(pid,q,ls) for (pid,q,_),(_,ls) in zip(layout,pg2)]
    T = {"FX1": (planted, "G2b"), "FX2": (planted_a, "G2a")}
    fitlike = {"FX1": dict(g2b=pm, g2a=gmap), "FX2": dict(g2b=pm, g2a=gmap)}
    PROF, MJ, TX, PR = {}, [], {}, {}
    for ti,(tn,(tp,constr)) in enumerate(T.items()):
        PROF[tn] = S97.profile_g(f"D/{tn}/t", S91.cut([(p,ls) for p,_,ls in tp]), SlotSegmenter, M.N_MATCH, SEED+500+ti)
        for fi,Q in enumerate(qs):
            frng = np.random.default_rng([SEED, 88, ti, fi])
            tr, te, H = M.loqo_texts(constr, fitlike[tn], tp, Q, None, M.FxCodebook(), frng)
            TX[(tn,fi)] = te
            PR[(tn,fi)] = S97.profile_g(f"D/{tn}/{Q}", H, SlotSegmenter, M.N_MATCH, SEED+700+100*ti+fi)
            MJ.append(dict(key=("REF",tn,fi), name="r", train=[(p,ls) for p,q,ls in tp if q!=Q], test=[(p,ls) for p,q,ls in tp if q==Q], seed=SEED+30000+1000*ti+fi))
            MJ.append(dict(key=("SV",tn,fi), name="g", train=tr, test=te, seed=SEED+40000+1000*ti+fi))
    Mres = M.battery_pool(MJ, "diag battery")
    for ti,(tn,(tp,constr)) in enumerate(T.items()):
        lb = S87.loc_band_from([PROF[tn]]); print(tn, S97.fmt(PROF[tn], lb))
        for fi,Q in enumerate(qs):
            rm, rdr = Mres[("REF",tn,fi)]; gm, gdr = Mres[("SV",tn,fi)]
            real_te = [ls for p,q,ls in tp if q==Q]
            cells,_,_,_ = S67.score_model(rm, rm.point(), rdr, [gm], gdr, rm.n_test, [[ls for _,ls in TX[(tn,fi)]]], real_te)
            p = PR[(tn,fi)]; sig, fl = M.S104.sig_rel(p, [PROF[tn]])
            print(f" {tn} {Q} sig {fl} Rw {p['rep'][1]['Rw']:.3f} Rc {p['rep'][1]['Rc']:.3f} loc {p['loc']['ratio']:.4f} in {lb[0]<=p['loc']['ratio']<=lb[1]} | bat " + "".join("+" if cells[k][0] else "-" for k in S67.PREDS) + f" {sum(bool(cells[k][0]) for k in S67.PREDS)}")
if __name__ == "__main__":
    main()
