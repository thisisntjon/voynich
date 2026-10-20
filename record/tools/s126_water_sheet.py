"""s126 = s123 rerun with the blue segmentation recalibrated outside quire M (D-066 cc-s126, approved by Jon 00:33).

Same statistic, exact null (945 leaf matchings), fixture and positive controls as s123: imported from
tools/s123_water_sheet.py unchanged (its RUN/META globals are pointed at runs/s126). Segmentation: tools/s126_colour.py.
Changes vs s123: blue L >= 25, C >= 4, components >= 200 px (green unchanged); the gate validation is the calibration
hand check (runs/s126/validation.txt, >= 4/5 PASS per class); CALL_COLOUR_SPLIT prints NOT_MEASURABLE whenever CALL does;
after measure, 5 quire-M blue crops are hand-checked (runs/s126/validation_M.txt) and reported descriptively.

Modes: snapshot | fixture | measure | test
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s123_water_sheet as s123  # noqa: E402

ROOT = os.path.dirname(HERE)
RUN = os.path.join(ROOT, "runs", "s126")
META = os.path.join(RUN, "inputs_meta.json")
STUB = os.path.join(ROOT, "s126_water_sheet.prereg.sha256")
s123.RUN, s123.META, s123.STUB = RUN, META, STUB  # reuse s123 snapshot/fixture/verify_stub with s126 paths

MIN_PX = s123.MIN_PX          # 5000 water px for a measurable page (unchanged)
VAL_N, VAL_PASS = 5, 4
VAL_M_N = 5
SECTION = s123.SECTION


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def measure():
    pr = s123.lower_priority()
    nver = s123.verify_stub()
    from PIL import Image
    from s126_colour import load_rgb, rgb_to_lab, water_mask, densest_crops, DEV, GREEN, BLUE
    m, pages, leaves, bif = s123.load_meta()
    out = os.path.join(RUN, "measures.json")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    cdir = os.path.join(RUN, "crops")
    os.makedirs(cdir, exist_ok=True)
    print(f"s126 measure, started {now()}; {pr}; device {DEV}; stub verified ({nver} files); green {GREEN}; blue {BLUE}")
    P = s123.PARCH
    rec = {}
    for r in m["folios"]:
        rgb = load_rgb(os.path.join(ROOT, r["image"]))
        L, a, bb, C, h = rgb_to_lab(rgb)
        g, b = water_mask(L, C, h)
        b = b & ~g
        w = g | b
        n = int(w.sum())
        parch = (L >= P["L_MIN"]) & (C <= P["C_MAX"]) & (h >= P["H_LO"]) & (h <= P["H_HI"]) & ~w
        d = dict(folio=r["folio"], section=r["section"], n_px=int(L.size), n_water=n, n_green=int(g.sum()),
                 n_blue=int(b.sum()),
                 blue_share=(float(b.sum()) / n) if n else None,
                 green_share=(float(g.sum()) / n) if n else None,
                 median_hue=float(np.median(h[w])) if n else None,
                 hue_p10=float(np.percentile(h[w], 10)) if n else None,
                 hue_p90=float(np.percentile(h[w], 90)) if n else None,
                 median_C=float(np.median(C[w])) if n else None,
                 median_L=float(np.median(L[w])) if n else None,
                 hue_hist=np.histogram(h[w], bins=41, range=(105, 310))[0].tolist() if n else None,
                 parch_Lab=[float(np.median(L[parch])), float(np.median(a[parch])), float(np.median(bb[parch]))],
                 measurable=n >= MIN_PX)
        rec[r["folio"]] = d
        vis = np.full(rgb.shape, 255, np.uint8)
        vis[g] = (0, 160, 0)
        vis[b] = (0, 0, 220)
        im = Image.fromarray(np.concatenate([rgb, vis], axis=1))
        im.thumbnail((1400, 1000))
        im.save(os.path.join(cdir, f"page_{r['folio']}.png"))
        for cls, mk in (("green", g), ("blue", b)):
            if mk.sum() < 500:
                continue
            for i, (_, arr) in enumerate(densest_crops(rgb, mk, k=1)):
                Image.fromarray(arr).save(os.path.join(cdir, f"crop_{cls}_{r['folio']}.png"))
        print(f"  {r['folio']:6s} {r['section']} water {n:7d} green {d['n_green']:7d} blue {d['n_blue']:7d} blue_share "
              f"{d['blue_share'] if n else float('nan'):.3f} med_hue {d['median_hue'] if n else float('nan'):.1f}", flush=True)
    json.dump(rec, open(out, "w", encoding="utf-8"), indent=1)
    # quire-M blue crops for the descriptive hand check: 5 section-B pages with most blue px (>= 500)
    cand = sorted([d for d in rec.values() if d["section"] == SECTION and d["n_blue"] >= 500], key=lambda d: -d["n_blue"])
    sel = [d["folio"] for d in cand[:VAL_M_N]]
    json.dump(sel, open(os.path.join(RUN, "validation_M_crops.json"), "w"), indent=1)
    print("quire-M blue crops for the hand check:", sel)
    print(f"finished {now()}; wrote {out}")


def read_val(path):
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8").read().splitlines():
            if line.strip() and not line.startswith("#"):
                rows.append([x.strip() for x in line.split("|")])
    return rows


def test():
    pr = s123.lower_priority()
    nver = s123.verify_stub()
    m, pages, leaves, bif = s123.load_meta()
    rec = json.load(open(os.path.join(RUN, "measures.json"), encoding="utf-8"))
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(ROOT, f"results_s126_{ts}.txt")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    from s126_colour import GREEN, BLUE
    L = []

    def P(s=""):
        print(s, flush=True); L.append(s)

    P(f"s126 water colour vs sheet (s123 rerun, blue recalibrated; D-066 cc-s126) -- REAL RUN. started {now()}; {pr}")
    P(f"script tools/s126_water_sheet.py sha256 {s123.sha(os.path.abspath(__file__))}; stub {os.path.basename(STUB)} "
      f"verified ({nver} files) sha256 {s123.sha(STUB)}; VKB snapshot runs/s126/inputs_meta.json "
      f"(VKB sha256 {m['vkb_sha256'][:16]}.. build {m['vkb_built']})")
    P(f"segmentation: green {GREEN}; blue {BLUE} (blue calibrated on f85v/86r Rosettes, f69r, f67r, f9v; negatives f1r, f66r, "
      f"f116v); min water px {MIN_PX} (1/2-resolution pixels)")
    P("")
    P("Per-page water colour (quire M; f76r is section T, not tested):")
    P(f"{'folio':7s} {'sec':3s} {'water_px':>8s} {'green':>7s} {'blue':>7s} {'blue_sh':>7s} {'med_hue':>7s} {'hue10-90':>11s} "
      f"{'med_C':>5s} {'med_L':>5s} meas")
    for r in m["folios"]:
        d = rec[r["folio"]]
        if d["n_water"]:
            P(f"{d['folio']:7s} {d['section']:3s} {d['n_water']:8d} {d['n_green']:7d} {d['n_blue']:7d} {d['blue_share']:7.3f} "
              f"{d['median_hue']:7.1f} {d['hue_p10']:5.0f}-{d['hue_p90']:<5.0f} {d['median_C']:5.1f} {d['median_L']:5.1f} "
              f"{'yes' if d['measurable'] else 'no'}")
        else:
            P(f"{d['folio']:7s} {d['section']:3s} {0:8d}  -- no water px")
    # gate validation: calibration crops (outside quire M)
    P("")
    val_ok = True
    vrows = read_val(os.path.join(RUN, "validation.txt"))
    for cls in ("blue", "green"):
        rr = [x for x in vrows if x[0] == cls]
        npass = sum(x[2].upper() == "PASS" for x in rr)
        ok = len(rr) >= VAL_N and npass >= VAL_PASS * len(rr) / VAL_N
        val_ok &= ok
        P(f"VALIDATION (calibration pages, gate) {cls}: {npass}/{len(rr)} PASS (need >= {VAL_PASS} of {VAL_N}) -> "
          f"{'ok' if ok else 'FAIL'}")
    # descriptive: quire M blue crops
    sel = json.load(open(os.path.join(RUN, "validation_M_crops.json"), encoding="utf-8"))
    mrows = read_val(os.path.join(RUN, "validation_M.txt"))
    P(f"DESCRIPTIVE quire-M blue crop check (not a gate): crops {sel}; PASS "
      f"{sum(x[2].upper() == 'PASS' for x in mrows)}/{len(mrows)}")
    for x in mrows:
        P("  hand: " + " | ".join(x))
    # colour split
    meas = [rec[r["folio"]] for r in pages if rec[r["folio"]]["measurable"]]
    s = np.array([d["blue_share"] for d in meas])
    ng, nb = int((s <= s123.SPLIT_LO).sum()), int((s >= s123.SPLIT_HI).sum())
    nm = len(s) - ng - nb
    if ng < 2 or nb < 2:
        split = "ONE_COLOUR" if nm / max(len(s), 1) <= s123.MIXED_MAX else "CONTINUUM"
    else:
        split = "TWO_WAY" if nm / len(s) <= s123.MIXED_MAX else "CONTINUUM"
    P("")
    P(f"Colour split over {len(s)} measurable section-B pages: green-class (blue share <= {s123.SPLIT_LO}) {ng}, "
      f"blue-class (>= {s123.SPLIT_HI}) {nb}, mixed {nm}")
    if meas:
        tot = np.sum([np.array(d["hue_hist"]) for d in meas], axis=0)
        P("pooled water hue histogram (5-degree bins from 105 to 310): " + " ".join(str(int(x)) for x in tot))
    page_leaf = {d["folio"]: d["folio"][:-1] for d in meas}
    prof = {}
    for lf in leaves:
        v = [d["blue_share"] for d in meas if page_leaf[d["folio"]] == lf]
        hv = [d["median_hue"] for d in meas if page_leaf[d["folio"]] == lf]
        if v:
            prof[lf] = (float(np.mean(v)), float(np.mean(hv)))
    drop = sorted({bif[lf] for lf in leaves if lf not in prof})
    use = [lf for lf in leaves if bif[lf] not in drop]
    P("")
    P("Leaf profiles (mean over measurable pages): " + ", ".join(
        f"{lf}[{bif[lf]}] blue {prof[lf][0]:.3f} hue {prof[lf][1]:.0f}" for lf in leaves if lf in prof))
    if drop:
        P(f"dropped bifolios (a leaf without measurable water): {drop}")
    sheet_call = None
    if len(use) // 2 < 4 or not val_ok:
        sheet_call = "NOT_MEASURABLE"
        P(f"NOT_MEASURABLE: bifolios usable {len(use) // 2} (need >= 4); calibration validation ok {val_ok}")
    t = p = None
    if len(use) >= 4:
        q = s123.Quire(use, bif)
        P(f"exact null: {q.M} perfect matchings of {len(use)} leaves; minimum achievable p = {1 / q.M:.5f}")
        t, p, T = q.stat([prof[lf][0] for lf in use])
        P(f"PRIMARY (blue share): T = between - within mean |d| = {t:+.4f}; null mean {T.mean():+.4f} sd {T.std():.4f}; "
          f"exact p = {p:.4f} ({int(round(p * q.M))}/{q.M})")
        t2, p2, _ = q.stat(np.array([prof[lf][1] for lf in use]) / 100.0)
        P(f"SECONDARY (median hue / 100): T = {t2:+.4f}; exact p = {p2:.4f}")
    # positive control B (parchment), unchanged from s123
    pl = {}
    for r in m["folios"]:
        pl.setdefault(r["folio"][:-1], []).append(rec[r["folio"]]["parch_Lab"])
    PX = np.array([np.mean(pl[lf], axis=0) for lf in leaves])
    PZ = (PX - PX.mean(0)) / PX.std(0, ddof=1)
    t3, p3, _ = s123.Quire(leaves, bif).stat(PZ)
    P(f"POSITIVE CONTROL B (parchment median L*a*b*, z, all 10 leaves): T = {t3:+.4f}; exact p = {p3:.4f} -> "
      f"{s123.call_sheet(t3, p3)}")
    # descriptive: same leaf and facing pages (ORDER-DEPENDENT)
    bs = {d["folio"]: d["blue_share"] for d in meas}
    fl = list(bs)
    allp = [(a, b) for i, a in enumerate(fl) for b in fl[i + 1:]]
    same_leaf = [x for x in allp if x[0][:-1] == x[1][:-1]]
    facing = [x for x in allp if x[0].endswith("v") and x[1].endswith("r") and int(x[1][1:-1]) == int(x[0][1:-1]) + 1]
    rng = np.random.default_rng(s123.SEED)
    vals = np.array([bs[f] for f in fl])
    idx = {f: i for i, f in enumerate(fl)}
    for lab, prs in (("same leaf (recto vs verso)", same_leaf), ("FACING pages in current binding [ORDER-DEPENDENT]", facing)):
        if not prs or len(prs) == len(allp):
            continue
        inp = set(prs)

        def gap(v):
            dd = {x: abs(v[idx[x[0]]] - v[idx[x[1]]]) for x in allp}
            return np.mean([dd[x] for x in prs]) - np.mean([dd[x] for x in allp if x not in inp])
        obs = gap(vals)
        cnt = sum(gap(rng.permutation(vals)) <= obs for _ in range(10000))
        P(f"DESCRIPTIVE {lab}: {len(prs)} pairs, mean |d| in-pair minus other pairs = {obs:+.4f}; "
          f"MC page-permutation p (more alike) = {(cnt + 1) / 10001:.4f}")
    P("")
    P("Caveats: whether the paint was applied at writing time is unknown, so SHEET means 'painted per sheet', not "
      "'planned per sheet'. n is small (5 bifolios, 10 leaves; minimum p 1/945 = 0.00106 with all 10 leaves). Blue is "
      "detected by absolute hue (>= 200); parchment-hued grey-teal washes (as the f69r smudges) are not detectable. The "
      "s126 calibrator had seen quire-M overviews in s123. D-066 (v): no real-language control applies (image colour); "
      "the shuffled control is the exact matching null.")
    final = sheet_call or s123.call_sheet(t, p)
    P(f"CALL: {final}")
    P(f"CALL_COLOUR_SPLIT: {'NOT_MEASURABLE' if final == 'NOT_MEASURABLE' else split}")
    P(f"finished {now()}")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    {"snapshot": s123.snapshot, "fixture": s123.fixture, "measure": measure, "test": test}.get(
        mode, lambda: print(__doc__))()
