"""vx01_a1_known_answer.py - A1 known-answer test of segmenters on planted books (script 3).

Plan: PLAN-X01-v5.1 (SHA256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393), section 4 (A1), rules 1-8 of section 3.
All output is UNVERIFIED until the Independent Verifier signs. No thresholds are set in this file other than the ones
in vx01_a1_metrics.py (F1 0.85, exact 0.70, null false structure 0.05, 10 of 15 books in each of 9 cells).

Modes
  default (DEV): dev seeds only (20261111 .. 20261115). Guard: gate seeds are refused. Does ONLY (a) hand tests of the
         metrics, (b) generator sanity counts, (c) the ORACLE ceiling (plan: "A dictionary parse knowing the true
         inventories must reach the thresholds on G1 and G2"), (d) a smoke run of every segmenter on ONE dev book that
         prints no scores (crash and time check only). Output goes to runs/vx01_a1_dev/, never to results_*.txt.
  --gate: GATE seeds from vx01_gate_seeds.json. Needs the stub to match (vx01_common checks). Single shot. Scores 8
         rows on 135 gate books (3 sets x {G1, G2, NULL} x 15) and writes runs/vx01_a1/a1_scores.csv and
         results_vx01_a1.txt (with scores_sha256= and stub_match=). NEVER run by the analyst before the Independent
         Verifier / lead says GO.
  --dev-path-test: DEV seeds only; runs the exact scoring/report code of --gate on 1 dev book per (set, family) and
         writes to runs/vx01_a1_dev/path_test_<stamp>/ . Prints only file names, row counts and hashes, NO scores
         (checks that the gate code path runs; it is not an analysis). Logged in the dev log like any dev run.
Rows (plan section 4 "Rows scored"): Slot; Zattera primary (drops unparsable tokens: a miss); Zattera-hybrid
(Z_S1_whole); Zattera S2 (Z_S2_empty); Seg_Affix2; Canonical (CanonicalSlotSegmenter mode "Canon+Comp", the s70 default);
vx01_seg_mdl; unsegmented words. Every segmenter is fitted on the tokens of the book it scores (unsupervised, the way it is
used on the real text). Existing segmenters are imported unchanged. The secondary report-only small-inventory books are
NOT implemented here: the plan gives them neither seeds nor a suffix count (open question to Eve).
Compute: one process, BelowNormal.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import vx01_common as C

ROOT = Path(__file__).resolve().parent
SEG_ORDER = ("Slot", "Zattera-primary", "Zattera-hybrid", "Zattera-S2", "Seg_Affix2", "Canonical", "vx01_seg_mdl",
             "unsegmented")


def make_segmenters(tokens):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scoreboard.metrics_new import SlotSegmenter
    import s76_segmenter_independence as S76
    from s77_deconfounded_scribe_and_comma_ablation_loqo import SegAffix2
    from s70_canonical_segmentation_and_rare_cores import CanonicalSlotSegmenter
    from vx01_seg_mdl import SegMDL

    def wrap_drop(z):
        def f(w):
            try:
                return z.segment(w)
            except ValueError:
                return None
        return f
    slot = SlotSegmenter(tokens)
    zp = S76.ZatteraSegmenter("drop", "primary", tokens)
    zh = S76.ZatteraSegmenter("whole", "primary", tokens)
    z2 = S76.ZatteraSegmenter("empty", "primary", tokens)
    aff = SegAffix2(tokens)
    can = CanonicalSlotSegmenter(tokens, mode="Canon+Comp")
    mdl = SegMDL(tokens)
    return {"Slot": slot.segment, "Zattera-primary": wrap_drop(zp), "Zattera-hybrid": zh.segment,
            "Zattera-S2": z2.segment, "Seg_Affix2": aff.segment, "Canonical": can.segment,
            "vx01_seg_mdl": mdl.segment, "unsegmented": (lambda w: ("", w, ""))}


def selftest():
    import vx01_a1_metrics as M
    assert M.boundaries("qo", "kee", "y") == frozenset({2, 5})
    seg = {"qokeey": ("qo", "kee", "y"), "keey": ("", "keey", "")}.get
    sc = M.score_book(["qokeey", "keey"], [("qo", "kee", "y"), ("", "kee", "y")], seg)
    assert abs(sc["precision"] - 1.0) < 1e-12 and abs(sc["recall"] - 2 / 3) < 1e-12 and abs(sc["exact"] - 0.5) < 1e-12
    sc2 = M.score_book(["ab"], [("", "ab", "")], lambda w: None)
    assert sc2["dropped_share"] == 1.0 and sc2["f1"] == 0.0
    return "metrics hand tests ok"


def books_for(mode, tset, real, G):
    """Yield (family, index, master, book) in a fixed order."""
    if mode == "dev":
        masters = C.dev_seed_list("A1")
        for i, m in enumerate(masters):
            yield "G1", i, m, G.gen_g1(tset, m, real)
        for i, m in enumerate(masters):
            yield "G2", i, m, G.gen_g2(tset, m, m, m, real)
        for i, m in enumerate(masters):
            yield "NULL", i, m, G.gen_null(tset, m, real)
    else:
        g1, g2 = C.gate_seed_list("A1_G1"), C.gate_seed_list("A1_G2")
        gt, gg = C.gate_seed_list("A1_G2_table"), C.gate_seed_list("A1_G2_grille")
        nl = C.gate_seed_list("A1_NULL")
        for i, m in enumerate(g1):
            yield "G1", i, m, G.gen_g1(tset, m, real)
        for i, m in enumerate(g2):
            yield "G2", i, m, G.gen_g2(tset, m, gt[i], gg[i], real)
        for i, m in enumerate(nl):
            yield "NULL", i, m, G.gen_null(tset, m, real)


def run_dev(ctx, out_dir, stamp):
    import vx01_a1_gen as G
    import vx01_a1_metrics as M
    lines = list(ctx.header())
    lines.append(selftest())
    lines.append("# DEV ONLY: oracle ceiling and generator counts. Segmenter scores are NOT computed or printed in dev.")
    oracle_rows = []
    smoke = None
    for tset in G.SET_ORDER:
        real = G.load_set(tset)
        for fam, i, m, bk in books_for("dev", tset, real, G):
            if fam == "NULL":
                if i == 0:
                    from collections import Counter
                    lines.append("NULL %s: tokens %d, types %d (real types %d), lines %d" % (
                        tset, len(bk["tokens"]), len(set(bk["tokens"])), len(set(real["tokens"])), len(bk["layout"])))
                continue
            sc = M.score_book(bk["tokens"], bk["truth"], M.oracle_fn(bk["truth"]))
            oracle_rows.append(dict(set=tset, family=fam, idx=i, master=m, passed=M.book_passes(fam, sc),
                                    inv=bk["inventory"], types=len(set(bk["tokens"])), **sc))
            if smoke is None and fam == "G1" and tset == "ZL3b" and i == 0:
                smoke = bk
    lines.append("")
    lines.append("ORACLE ceiling (true inventories + true counts), 5 dev books per cell; needs F1>=0.85 AND exact>=0.70:")
    ok_all = True
    for tset in G.SET_ORDER:
        for fam in ("G1", "G2"):
            rs = [r for r in oracle_rows if r["set"] == tset and r["family"] == fam]
            npass = sum(r["passed"] for r in rs)
            ok_all &= npass == len(rs)
            lines.append("  %s %s: %d/%d pass; F1 min %.4f mean %.4f; exact min %.4f mean %.4f; inventory P/C/S %s; types %s" % (
                tset, fam, npass, len(rs), min(r["f1"] for r in rs), sum(r["f1"] for r in rs) / len(rs),
                min(r["exact"] for r in rs), sum(r["exact"] for r in rs) / len(rs),
                "/".join(str(rs[0]["inv"][k]) for k in "PCS"), rs[0]["types"]))
    lines.append("ORACLE verdict: %s" % ("ALL dev books pass; generators OK" if ok_all else
                                         "SOME dev books fail: generator needs a code revision on dev seeds (counts toward max 2)"))
    t0 = time.time()
    segs = make_segmenters(smoke["tokens"])
    for name in SEG_ORDER:
        t1 = time.time()
        n = 0
        for w in sorted(set(smoke["tokens"])):
            segs[name](w)
            n += 1
        lines.append("smoke %-16s ran on %d types in %.1f s (no score printed)" % (name, n, time.time() - t1))
    lines.append("smoke total %.1f s (fit + segment)" % (time.time() - t0))
    out_dir.mkdir(parents=True, exist_ok=True)
    rpt = out_dir / ("dev_report_%s.txt" % stamp)
    if rpt.exists():
        C.refuse("will not overwrite %s" % rpt)
    rpt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return [rpt]


def score_all(ctx, mode, out_dir, resp, limit=None):
    import vx01_a1_gen as G
    import vx01_a1_metrics as M
    out_dir.mkdir(parents=True, exist_ok=True)
    csvp = out_dir / "a1_scores.csv"
    for p in (csvp, resp):
        if p.exists():
            C.refuse("will not overwrite %s" % p)
    rows, flat = [], []
    t_start = time.time()
    for tset in G.SET_ORDER:
        real = G.load_set(tset)
        seen = {}
        for fam, i, m, bk in books_for(mode, tset, real, G):
            if limit is not None and seen.get(fam, 0) >= limit:
                continue
            seen[fam] = seen.get(fam, 0) + 1
            segs = make_segmenters(bk["tokens"])
            for name in SEG_ORDER:
                sc = M.score_book(bk["tokens"], bk["truth"], segs[name])
                passed = M.book_passes(fam, sc)
                rows.append(dict(set=tset, family=fam, segmenter=name, passed=passed))
                flat.append(dict(set=tset, family=fam, book=i, master_seed=m, segmenter=name,
                                 passed=int(passed), **{k: sc[k] for k in (
                                     "n_tokens", "f1", "precision", "recall", "exact", "false_structure", "type_f1",
                                     "dropped_share")}))
            print("done %s %s %d  (%.0f s)" % (tset, fam, i, time.time() - t_start), flush=True)
    cols = ["set", "family", "book", "master_seed", "segmenter", "passed", "n_tokens", "f1", "precision", "recall",
            "exact", "false_structure", "type_f1", "dropped_share"]
    with open(csvp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in flat:
            w.writerow({k: (("%.6f" % v) if isinstance(v, float) else v) for k, v in r.items()})
    roll = M.rollup(rows)
    L = list(ctx.header())
    L.append("scores_file=runs/vx01_a1/a1_scores.csv")
    L.append("scores_sha256=%s" % C.sha256_file(csvp))
    L.append("")
    L.append("A1 known-answer roll-up: books passing out of 15 per cell. G1/G2 pass = F1>=0.85 and exact>=0.70; NULL pass = false structure<=0.05.")
    L.append("Label rule: ADEQUATE ON PLANTED BOOKS (G1 at Slot-sized inventories, G2 Rugg-sized) only if all 9 cells have >=10/15.")
    L.append("%-16s %s  LABEL" % ("segmenter", "  ".join("%s-%s" % (t, f) for t in G.SET_ORDER for f in M.FAMILIES)))
    n_adequate = 0
    for name in SEG_ORDER:
        d = roll[name]
        cells = "  ".join("%9s" % ("%d/%d" % tuple(d["cells"][(t, f)])) for t in G.SET_ORDER for f in M.FAMILIES)
        lab = "ADEQUATE ON PLANTED BOOKS (G1 at Slot-sized inventories, G2 Rugg-sized)" if d["adequate"] else "NOT ADEQUATE"
        n_adequate += d["adequate"]
        L.append("%-16s %s  %s" % (name, cells, lab))
    L.append("")
    if n_adequate == 0:
        L.append("No segmenter, Slot included, is ADEQUATE: X-01 stays at-risk; no finding is upgraded or downgraded; A2/A3 flips are descriptive only (filed as 'no segmenter validated').")
    L.append("Zattera-hybrid (Part B dependency): %s" % ("ADEQUATE in all 9 cells" if roll["Zattera-hybrid"]["adequate"] else "fails in at least one cell"))
    L.append("These labels hold only on synthetic books with independent affix draws (Slot's own assumption). They do not mean adequate for the Voynich text and do not discharge X-01.")
    resp.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    return [csvp, resp], L


def run_gate(ctx):
    outs, L = score_all(ctx, "gate", ROOT / "runs" / "vx01_a1", ROOT / "results_vx01_a1.txt")
    print("\n".join(L))
    return outs


def run_path_test(ctx, stamp):
    d = ROOT / "runs" / "vx01_a1_dev" / ("path_test_%s" % stamp)
    outs, L = score_all(ctx, "dev", d, d / "results_path_test.txt", limit=1)
    print("path test ok: %d files" % len(outs))
    for p in outs:
        print("  %s sha256 %s" % (p, C.sha256_file(p)))
    return outs


def main():
    C.set_below_normal()
    gate = "--gate" in sys.argv
    if gate:
        if (ROOT / "results_vx01_a1.txt").exists() or (ROOT / "runs" / "vx01_a1" / "a1_scores.csv").exists():
            C.refuse("A1 result files already exist; never overwritten")
        seeds = (C.gate_seed_list("A1_G1") + C.gate_seed_list("A1_G2") + C.gate_seed_list("A1_G2_table")
                 + C.gate_seed_list("A1_G2_grille") + C.gate_seed_list("A1_NULL"))
    else:
        seeds = C.dev_seed_list("A1")
    ctx = C.RunContext(__file__, sys.argv[1:], seeds, gate).start()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    if gate:
        outs = run_gate(ctx)
    elif "--dev-path-test" in sys.argv:
        outs = run_path_test(ctx, stamp)
    else:
        outs = run_dev(ctx, ROOT / "runs" / "vx01_a1_dev", stamp)
    print("log line sha256:", ctx.finish(outs))


if __name__ == "__main__":
    main()
