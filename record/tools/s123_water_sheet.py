"""s123 (P-68 / H-20, D-066 cc): does the biological-section water colour (green vs blue) follow the sheet?

Modes (run in this order):
  snapshot  copy the needed VKB metadata (quire M folios, image paths, ZL3b folio_features) to runs/s123/inputs_meta.json
  fixture   synthetic quire with the real bifolio structure (gate) + positive control A (text features, F-51 type)
  measure   REAL colour data: per-page water pixels (Yale scans), crops for the hand validation. No statistic.
  test      reads runs/s123/validation.txt (hand check) + measures; prints the statistic and the CALL lines.

Unit: the leaf (10 leaves, 5 bifolios in quire M). Null: all 945 perfect matchings of the 10 leaves (exact).
Statistic T = mean |d| between leaves of different bifolios - mean |d| within bifolios (within similarity - between
similarity, similarity = -|d|), d on the leaf blue share. p = #(matchings with T >= T_obs) / #matchings.
"""
import os, sys, json, time, hashlib, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
RUN = os.path.join(ROOT, "runs", "s123")
META = os.path.join(RUN, "inputs_meta.json")
STUB = os.path.join(ROOT, "s123_water_sheet.prereg.sha256")
DB = os.path.join(ROOT, "data", "vkb", "vkb.sqlite")

SEED = 20261019
QUIRE = "M"
SECTION = "B"
# thresholds chosen on calibration pages f9v (quire B) and f2r (quire A) only (tools/s123_calib.py); never on quire M
TH = dict(L_MIN=35.0, L_MAX=100.0, H_G_LO=105.0, H_SPLIT=200.0, H_B_HI=310.0)
C_MIN_G = 14.0   # green paint chroma floor (removes the f9v show-through ghost and the f2r stain circle)
C_MIN_B = 9.0    # blue paint chroma floor (Yale blue is low-chroma; 14 loses most f9v petals)
CLOSE_PX = 5     # binary closing size (px at 1/2 resolution) before components
MIN_COMP = 2000  # px at 1/2 resolution; smaller blue/green components (speckle, offset dots) are not water
MIN_PX = 5000    # a page is measurable if it has >= MIN_PX water px
ALPHA = 0.05
# colour split rule (per measurable page blue share s): GREEN class s <= 0.2, BLUE class s >= 0.8, MIXED otherwise
SPLIT_LO, SPLIT_HI = 0.2, 0.8
MIXED_MAX = 0.2   # TWO_WAY needs mixed pages <= 20% of measurable pages and >= 2 pages in each class
# validation: 5 crops per colour class; class passes if >= 4/5 crops are painted water of the claimed colour
VAL_N, VAL_PASS = 5, 4
# fixture
NFIX = 10
FIX_PASS = 8
PLANT_LEVELS = (0.15, 0.85)
SHEET_JITTER = 0.10
PAGE_NOISE = 0.05
PARCH = dict(L_MIN=55.0, C_MAX=30.0, H_LO=40.0, H_HI=100.0)  # parchment pixels for positive control B
EXCLUDE_FEAT = {"Rw1_line", "rhythm_excess", "n_stars"}       # as s120


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lower_priority():
    try:
        import psutil
        p = psutil.Process()
        if os.name == "nt":
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            p.nice(10)
        return "priority BelowNormal"
    except Exception as e:  # pragma: no cover
        return f"priority unchanged ({e})"


def verify_stub():
    import subprocess
    if not os.path.exists(STUB):
        raise SystemExit("stub missing: real data may not be read before the freeze")
    lines = [l.strip() for l in open(STUB, encoding="utf-8").read().replace("\r", "").split("\n")
             if l.strip() and not l.startswith("#")]
    bad = []
    for l in lines:
        h, p = l.split(None, 1)
        p = p.lstrip("*")
        if sha(os.path.join(ROOT, p)) != h:
            bad.append(p)
    if bad:
        raise SystemExit(f"stub verify FAILED: {bad}")
    return len(lines)


# ---------------------------------------------------------------- structure and statistic
def matchings(items):
    """All perfect matchings of an even-length list (as lists of pairs)."""
    if not items:
        yield []
        return
    a = items[0]
    for k in range(1, len(items)):
        b = items[k]
        rest = items[1:k] + items[k + 1:]
        for m in matchings(rest):
            yield [(a, b)] + m


class Quire:
    def __init__(self, leaves, bif_of_leaf):
        self.leaves = list(leaves)
        n = len(self.leaves)
        idx = {l: i for i, l in enumerate(self.leaves)}
        obs = {}
        for l in self.leaves:
            obs.setdefault(bif_of_leaf[l], []).append(idx[l])
        self.obs = [tuple(sorted(v)) for v in obs.values()]
        assert all(len(v) == 2 for v in self.obs), "every bifolio must have 2 leaves"
        allm = [sorted(tuple(sorted(p)) for p in m) for m in matchings(list(range(n)))]
        self.M = len(allm)
        # within-pair indicator matrix W[m, pair k] over all leaf pairs
        self.pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        pidx = {p: k for k, p in enumerate(self.pairs)}
        self.W = np.zeros((self.M, len(self.pairs)))
        for m, mm in enumerate(allm):
            for p in mm:
                self.W[m, pidx[p]] = 1.0
        self.obs_row = [m for m, mm in enumerate(allm) if sorted(mm) == sorted(self.obs)]
        assert len(self.obs_row) == 1
        self.obs_row = self.obs_row[0]
        self.nw = n // 2
        self.nb = len(self.pairs) - self.nw

    def stat(self, x):
        """x: n x k leaf profiles. Returns (T_obs, p_exact, T over all matchings)."""
        x = np.asarray(x, float).reshape(len(self.leaves), -1)
        d = np.array([np.sqrt(np.mean((x[i] - x[j]) ** 2)) for i, j in self.pairs])
        within = self.W @ d / self.nw
        between = ((1 - self.W) @ d) / self.nb
        T = between - within
        t0 = T[self.obs_row]
        p = float(np.mean(T >= t0 - 1e-12))
        return float(t0), p, T


def call_sheet(t, p):
    return "SHEET" if (p <= ALPHA and t > 0) else "NOT_SHEET"


# ---------------------------------------------------------------- metadata snapshot
def snapshot():
    import sqlite3
    if os.path.exists(META):
        raise SystemExit(f"refusing to overwrite {META}")
    os.makedirs(RUN, exist_ok=True)
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = list(c.execute("SELECT f.folio, f.quire, f.bifolio, f.conjugate, f.leaf_side, f.section, p.image_path, p.kind "
                          "FROM folios f LEFT JOIN panel_images p ON p.folio = f.folio WHERE f.quire = ? ORDER BY f.rowid",
                          (QUIRE,)))
    cal = list(c.execute("SELECT folio, image_path FROM panel_images WHERE folio IN ('f9v','f2r')"))
    ff = list(c.execute("SELECT folio, feature, value FROM folio_features WHERE translit='ZL3b' AND folio IN (%s)"
                        % ",".join("?" * len(rows)), [r[0] for r in rows]))
    built = c.execute("SELECT MAX(built_at) FROM build_log").fetchone()[0]
    json.dump(dict(vkb_sha256=sha(DB), vkb_built=built, taken=now(),
                   folios=[dict(zip(["folio", "quire", "bifolio", "conjugate", "side", "section", "image", "kind"], r))
                           for r in rows],
                   calibration=[dict(folio=a, image=b) for a, b in cal],
                   features_ZL3b=[list(r) for r in ff]), open(META, "w", encoding="utf-8"), indent=1)
    print(f"wrote {META} ({len(rows)} folios, {len(ff)} feature rows)")


def load_meta():
    m = json.load(open(META, encoding="utf-8"))
    pages = [r for r in m["folios"] if r["section"] == SECTION]
    bif = {}
    for r in m["folios"]:
        bif[r["folio"][:-1]] = r["bifolio"]  # leaf = folio minus side letter (fNNr / fNNv)
    leaves = sorted(bif, key=lambda s: int(s[1:]))
    return m, pages, leaves, bif


# ---------------------------------------------------------------- fixture
def fixture():
    lower_priority()
    m, pages, leaves, bif = load_meta()
    q = Quire(leaves, bif)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(RUN, f"fixture_{ts}.txt")
    L = []

    def P(s=""):
        print(s, flush=True); L.append(s)

    P(f"s123 fixture, started {now()}; leaves {leaves}; bifolios {sorted(set(bif.values()))}; "
      f"matchings {q.M} (exact); min achievable p = {1 / q.M:.5f}")
    P(f"pages in section {SECTION}: {len(pages)} ({', '.join(r['folio'] for r in pages)})")
    page_leaf = [r["folio"][:-1] for r in pages]
    rng = np.random.default_rng(SEED)

    def leaf_profile(page_vals):
        return np.array([np.mean([v for v, l in zip(page_vals, page_leaf) if l == lf]) for lf in leaves])

    def plant_sheet():
        lev = {b: rng.choice(PLANT_LEVELS) + rng.normal(0, SHEET_JITTER) for b in sorted(set(bif.values()))}
        return np.clip([lev[bif[l]] + rng.normal(0, PAGE_NOISE) for l in page_leaf], 0, 1)

    def plant_random():
        lv = {lf: rng.choice(PLANT_LEVELS) + rng.normal(0, SHEET_JITTER) for lf in leaves}  # per leaf, not per sheet
        return np.clip([lv[l] + rng.normal(0, PAGE_NOISE) for l in page_leaf], 0, 1)

    res = {}
    for name, fn in (("sheet", plant_sheet), ("random", plant_random)):
        calls = []
        for k in range(NFIX):
            t, p, _ = q.stat(leaf_profile(fn()))
            calls.append(call_sheet(t, p))
            P(f"  {name}-planted quire {k + 1}: T={t:+.4f} p={p:.4f} -> {calls[-1]}")
        res[name] = calls
    ns = sum(c == "SHEET" for c in res["sheet"])
    nr = sum(c == "NOT_SHEET" for c in res["random"])
    gate = ns >= FIX_PASS and nr >= FIX_PASS
    P(f"GATE sheet-planted SHEET {ns}/{NFIX} (need >= {FIX_PASS}); random-planted NOT_SHEET {nr}/{NFIX} (need >= {FIX_PASS})")
    # descriptive power: pure binary colour classes (no sheet jitter) and a larger sweep
    for jit, nz, lab in ((0.0, PAGE_NOISE, "binary classes, no batch jitter"),
                         (SHEET_JITTER, 0.15, "jitter 0.10, page noise 0.15"),
                         (SHEET_JITTER, PAGE_NOISE, "gate settings")):
        hit = 0
        fp = 0
        for _ in range(500):
            lev = {b: rng.choice(PLANT_LEVELS) + rng.normal(0, jit) for b in sorted(set(bif.values()))}
            v = np.clip([lev[bif[l]] + rng.normal(0, nz) for l in page_leaf], 0, 1)
            hit += call_sheet(*q.stat(leaf_profile(v))[:2]) == "SHEET"
            lv = {lf: rng.choice(PLANT_LEVELS) + rng.normal(0, jit) for lf in leaves}
            v = np.clip([lv[l] + rng.normal(0, nz) for l in page_leaf], 0, 1)
            fp += call_sheet(*q.stat(leaf_profile(v))[:2]) == "SHEET"
        P(f"  descriptive 500 sims ({lab}): power {hit / 500:.3f}, false SHEET rate under random {fp / 500:.3f}")
    # positive control A: F-51-type text features (ZL3b) on quire M, same statistic
    feats = {}
    for f, ft, v in m["features_ZL3b"]:
        if ft in EXCLUDE_FEAT or v is None:
            continue
        feats.setdefault(ft, {})[f] = v
    names = sorted(ft for ft, d in feats.items() if all(r["folio"] in d for r in pages))
    X = np.array([[feats[ft][r["folio"]] for ft in names] for r in pages], float)
    sd = X.std(0, ddof=1)
    keep = sd > 0
    Z = np.clip((X[:, keep] - X[:, keep].mean(0)) / sd[keep], -4, 4)
    LZ = np.array([Z[[i for i, l in enumerate(page_leaf) if l == lf]].mean(0) for lf in leaves])
    t, p, _ = q.stat(LZ)
    P(f"POSITIVE CONTROL A (text, F-51 type; {int(keep.sum())} ZL3b folio features, z within quire M, leaf mean, RMS distance): "
      f"T={t:+.4f} p={p:.4f} -> {call_sheet(t, p)}  (s120 needed 35 sheets; 5 sheets here, so a miss means low power, not a broken test)")
    P(f"CALL_FIXTURE: {'PASS' if gate else 'FAIL'}")
    P(f"finished {now()}")
    if os.path.exists(out):
        raise SystemExit("refusing to overwrite")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", out)


# ---------------------------------------------------------------- real measurement
def water_mask(L, C, h):
    from scipy import ndimage as ndi
    from s123_colour import classify
    g = classify(L, C, h, dict(TH, C_MIN=C_MIN_G)) == 1
    b = classify(L, C, h, dict(TH, C_MIN=C_MIN_B)) == 2
    paint = g | b
    closed = ndi.binary_closing(paint, structure=np.ones((CLOSE_PX, CLOSE_PX), bool))
    lab, n = ndi.label(closed)
    sizes = np.bincount(lab.ravel())
    big = sizes >= MIN_COMP
    big[0] = False
    keep = big[lab] & paint
    return keep & g, keep & b


def measure():
    pr = lower_priority()
    nver = verify_stub()
    from PIL import Image
    from scipy import ndimage as ndi
    from s123_colour import load_rgb, rgb_to_lab, DEV
    m, pages, leaves, bif = load_meta()
    out = os.path.join(RUN, "measures.json")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    cdir = os.path.join(RUN, "crops")
    os.makedirs(cdir, exist_ok=True)
    print(f"s123 measure, started {now()}; {pr}; device {DEV}; stub verified ({nver} files)")
    rec = {}
    for r in m["folios"]:  # all quire M pages (incl. f76r, section T, reported but not in the test)
        rgb = load_rgb(os.path.join(ROOT, r["image"]))
        L, a, bb, C, h = rgb_to_lab(rgb)
        g, b = water_mask(L, C, h)
        w = g | b
        n = int(w.sum())
        parch = (L >= PARCH["L_MIN"]) & (C <= PARCH["C_MAX"]) & (h >= PARCH["H_LO"]) & (h <= PARCH["H_HI"]) & ~w
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
        # page overview: scan | mask
        vis = np.full(rgb.shape, 255, np.uint8)
        vis[g] = (0, 160, 0)
        vis[b] = (0, 0, 220)
        im = Image.fromarray(np.concatenate([rgb, vis], axis=1))
        im.thumbnail((1400, 1000))
        im.save(os.path.join(cdir, f"page_{r['folio']}.png"))
        # densest 400x400 window for each class (for the hand validation)
        for cls, mk in (("green", g), ("blue", b)):
            if mk.sum() < MIN_PX:
                continue
            dens = ndi.uniform_filter(mk.astype(np.float32), 201)
            y, x = np.unravel_index(int(np.argmax(dens)), dens.shape)
            y0, x0 = max(0, y - 200), max(0, x - 200)
            crop = rgb[y0:y0 + 400, x0:x0 + 400]
            ov = crop.copy()
            sub = mk[y0:y0 + 400, x0:x0 + 400]
            ov[sub] = (ov[sub] * 0.3 + np.array([255, 0, 255]) * 0.7).astype(np.uint8)
            Image.fromarray(np.concatenate([crop, ov], axis=1)).save(os.path.join(cdir, f"crop_{cls}_{r['folio']}.png"))
        print(f"  {r['folio']:6s} {r['section']} water {n:7d} blue_share "
              f"{d['blue_share'] if n else float('nan'):.3f} med_hue {d['median_hue'] if n else float('nan'):.1f}", flush=True)
    json.dump(rec, open(out, "w", encoding="utf-8"), indent=1)
    # validation crop list (fixed rule): per class the 5 measurable section-B pages with most pixels of that class,
    # among pages whose share of that class is >= 0.5
    sel = {}
    for cls, key in (("blue", "n_blue"), ("green", "n_green")):
        cand = [d for d in rec.values() if d["section"] == SECTION and d["measurable"]
                and d[f"{cls}_share"] >= 0.5 and d[key] >= MIN_PX]
        cand.sort(key=lambda d: -d[key])
        sel[cls] = [d["folio"] for d in cand[:VAL_N]]
    json.dump(sel, open(os.path.join(RUN, "validation_crops.json"), "w"), indent=1)
    print("validation crops:", sel)
    print(f"finished {now()}; wrote {out}")


# ---------------------------------------------------------------- test
def test():
    pr = lower_priority()
    nver = verify_stub()
    m, pages, leaves, bif = load_meta()
    rec = json.load(open(os.path.join(RUN, "measures.json"), encoding="utf-8"))
    sel = json.load(open(os.path.join(RUN, "validation_crops.json"), encoding="utf-8"))
    vfile = os.path.join(RUN, "validation.txt")
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(ROOT, f"results_s123_{ts}.txt")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    L = []

    def P(s=""):
        print(s, flush=True); L.append(s)

    P(f"s123 water colour vs sheet (P-68 / H-20, D-066 cc) -- REAL RUN. started {now()}; {pr}")
    P(f"script tools/s123_water_sheet.py sha256 {sha(os.path.abspath(__file__))}; stub {os.path.basename(STUB)} "
      f"verified ({nver} files) sha256 {sha(STUB)}; VKB snapshot {os.path.relpath(META, ROOT)} "
      f"(VKB sha256 {m['vkb_sha256'][:16]}.. build {m['vkb_built']})")
    P(f"thresholds (calibrated on f9v, f2r only): {TH}, C_MIN_G {C_MIN_G}, C_MIN_B {C_MIN_B}, closing {CLOSE_PX}, "
      f"min component {MIN_COMP}, min water px {MIN_PX} (1/2-resolution pixels)")
    P("")
    P("Per-page water colour (quire M; f76r is section T, not tested):")
    P(f"{'folio':7s} {'sec':3s} {'water_px':>8s} {'blue_sh':>7s} {'green_sh':>8s} {'med_hue':>7s} {'hue10-90':>11s} "
      f"{'med_C':>5s} {'med_L':>5s} meas")
    for r in m["folios"]:
        d = rec[r["folio"]]
        if d["n_water"]:
            P(f"{d['folio']:7s} {d['section']:3s} {d['n_water']:8d} {d['blue_share']:7.3f} {d['green_share']:8.3f} "
              f"{d['median_hue']:7.1f} {d['hue_p10']:5.0f}-{d['hue_p90']:<5.0f} {d['median_C']:5.1f} {d['median_L']:5.1f} "
              f"{'yes' if d['measurable'] else 'no'}")
        else:
            P(f"{d['folio']:7s} {d['section']:3s} {0:8d}  -- no water px")
    # validation
    P("")
    val_ok = True
    vtxt = open(vfile, encoding="utf-8").read() if os.path.exists(vfile) else ""
    verdict = {}
    for line in vtxt.splitlines():
        if line.strip() and not line.startswith("#"):
            parts = line.split("|")
            verdict[(parts[0].strip(), parts[1].strip())] = parts[2].strip().upper()
    for cls in ("blue", "green"):
        fs = sel[cls]
        npass = sum(verdict.get((cls, f)) == "PASS" for f in fs)
        P(f"VALIDATION {cls}: crops {fs}; hand-check PASS {npass}/{len(fs)} (need >= {VAL_PASS} of {VAL_N})")
        if len(fs) < VAL_N:
            P(f"  note: only {len(fs)} pages qualify as {cls}-class crops")
        # a class with fewer than 5 qualifying pages needs all of them to pass; a class with none is skipped
        if fs and npass < min(VAL_PASS, len(fs)):
            val_ok = False
    if not sel["blue"] and not sel["green"]:
        val_ok = False
    for line in vtxt.splitlines():
        if line.strip() and not line.startswith("#"):
            P(f"  hand: {line.strip()}")
    # colour split
    meas = [rec[r["folio"]] for r in pages if rec[r["folio"]]["measurable"]]
    s = np.array([d["blue_share"] for d in meas])
    ng, nb = int((s <= SPLIT_LO).sum()), int((s >= SPLIT_HI).sum())
    nm = len(s) - ng - nb
    if ng < 2 or nb < 2:
        split = "ONE_COLOUR" if nm / max(len(s), 1) <= MIXED_MAX else "CONTINUUM"
    else:
        split = "TWO_WAY" if nm / len(s) <= MIXED_MAX else "CONTINUUM"
    P("")
    P(f"Colour split over {len(s)} measurable section-B pages: green-class (blue share <= {SPLIT_LO}) {ng}, "
      f"blue-class (>= {SPLIT_HI}) {nb}, mixed {nm}")
    tot = np.sum([np.array(d["hue_hist"]) for d in meas], axis=0)
    P("pooled water hue histogram (5-degree bins from 105 to 310): " + " ".join(str(int(x)) for x in tot))
    # leaf profiles
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
        P(f"NOT_MEASURABLE: bifolios usable {len(use) // 2} (need >= 4); validation ok {val_ok}")
    q = Quire(use, bif)
    P(f"exact null: {q.M} perfect matchings of {len(use)} leaves; minimum achievable p = {1 / q.M:.5f}")
    t, p, T = q.stat([prof[lf][0] for lf in use])
    P(f"PRIMARY (blue share): T = between - within mean |d| = {t:+.4f}; null mean {T.mean():+.4f} sd {T.std():.4f}; "
      f"exact p = {p:.4f} ({int(round(p * q.M))}/{q.M})")
    hz = np.array([prof[lf][1] for lf in use])
    t2, p2, _ = q.stat(hz / 100.0)
    P(f"SECONDARY (median hue / 100): T = {t2:+.4f}; exact p = {p2:.4f}")
    # parchment positive control B (physical: one bifolio = one piece of skin)
    pl = {}
    for r in pages:
        pl.setdefault(r["folio"][:-1], []).append(rec[r["folio"]]["parch_Lab"])
    for r in m["folios"]:
        if r["section"] != SECTION:
            pl.setdefault(r["folio"][:-1], []).append(rec[r["folio"]]["parch_Lab"])
    PX = np.array([np.mean(pl[lf], axis=0) for lf in leaves])
    PZ = (PX - PX.mean(0)) / PX.std(0, ddof=1)
    qa = Quire(leaves, bif)
    t3, p3, _ = qa.stat(PZ)
    P(f"POSITIVE CONTROL B (parchment median L*a*b*, z, all 10 leaves; expected sheet-linked if skin tone dominates "
      f"scan drift): T = {t3:+.4f}; exact p = {p3:.4f} -> {call_sheet(t3, p3)}")
    # descriptive: same leaf r vs v, and facing pages in the current binding (ORDER-DEPENDENT)
    bs = {d["folio"]: d["blue_share"] for d in meas}
    fl = list(bs)
    allp = [(a, b) for i, a in enumerate(fl) for b in fl[i + 1:]]
    dd = {pr_: abs(bs[pr_[0]] - bs[pr_[1]]) for pr_ in allp}
    same_leaf = [pr_ for pr_ in allp if pr_[0][:-1] == pr_[1][:-1]]
    facing = [pr_ for pr_ in allp if pr_[0].endswith("v") and pr_[1].endswith("r")
              and int(pr_[1][1:-1]) == int(pr_[0][1:-1]) + 1]
    rng = np.random.default_rng(SEED)
    for lab, prs in (("same leaf (recto vs verso)", same_leaf), ("FACING pages in current binding [ORDER-DEPENDENT]", facing)):
        if not prs:
            continue
        obs = np.mean([dd[x] for x in prs]) - np.mean([dd[x] for x in allp if x not in prs])
        vals = np.array([bs[f] for f in fl])
        idx = {f: i for i, f in enumerate(fl)}
        cnt = 0
        for _ in range(10000):
            pv = rng.permutation(vals)
            dpp = {x: abs(pv[idx[x[0]]] - pv[idx[x[1]]]) for x in allp}
            nul = np.mean([dpp[x] for x in prs]) - np.mean([dpp[x] for x in allp if x not in prs])
            cnt += nul <= obs
        P(f"DESCRIPTIVE {lab}: {len(prs)} pairs, mean |d| in-pair minus other pairs = {obs:+.4f}; "
          f"MC page-permutation p (more alike) = {(cnt + 1) / 10001:.4f}")
    P("")
    P("Caveats: whether the paint was applied at writing time is unknown, so SHEET means 'painted per sheet', not "
      "'planned per sheet'. n is small (5 bifolios, 10 leaves); the minimum achievable p is printed above. Water = "
      "blue/green paint pixels in components >= MIN_COMP; offset transfer and other green/blue paint are only "
      "controlled by the chroma floors and the hand check. D-066 (v): no real-language control applies (image colour); "
      "the shuffled control is the exact matching null.")
    P(f"CALL: {sheet_call or call_sheet(t, p)}")
    P(f"CALL_COLOUR_SPLIT: {split if val_ok else 'NOT_MEASURABLE'}")
    P(f"finished {now()}")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    {"snapshot": snapshot, "fixture": fixture, "measure": measure, "test": test}.get(
        mode, lambda: SystemExit(__doc__))()
