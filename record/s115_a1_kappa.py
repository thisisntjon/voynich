"""s115-A1 helpers: image index, pilot draw, Cohen's kappa per category, consensus labels.

No text data is read: only the folios table (folio, image_path, quire, section) and the label files.
Usage:
  python s115_a1_kappa.py fixture                      # synthetic kappa checks (must pass first)
  python s115_a1_kappa.py index                        # write data/anchor_A1/images.tsv (never overwrites)
  python s115_a1_kappa.py pilot                        # write data/anchor_A1/pilot_images.txt (seed 115)
  python s115_a1_kappa.py kappa P1 P2 OUT_TXT [CONSENSUS_TSV]
"""
import os, sys, random, subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.join(ROOT, "data", "anchor_A1")
COLS = ["stem", "PT", "P_plants", "P_root", "P_leafshape", "P_leafcount", "P_flower", "P_habit",
        "J_shape", "J_count", "J_fragcount", "J_fragtype", "C_centre", "C_animal", "C_figures",
        "C_rings", "C_diagrams", "C_rays", "B_pools", "B_figures", "B_tubes", "note"]
CATS = COLS[1:-1]
SEED = 115
PILOT = {"H": 5, "P": 2, "B": 3, "CIRC": 3, "S": 1, "T": 1}
FOLD_GROUP = {"120": "CIRC", "121": "CIRC", "122": "CIRC", "123": "CIRC", "125": "CIRC", "126": "CIRC",
              "127": "CIRC", "129": "CIRC", "130": "CIRC", "131": "CIRC", "154": "CIRC", "155": "CIRC",
              "156": "CIRC", "157": "CIRC", "161": "P", "162": "P", "163": "P", "164": "H", "165": "H",
              "169": "H", "170": "H", "171": "H", "177": "P", "178": "P", "179": "P", "180": "P", "181": "P"}


def write_new(path, text):
    if os.path.exists(path):
        sys.exit(f"refusing to overwrite {path}")
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(text)


def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return None, 0, None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    if pe >= 1.0:
        return None, n, po
    return (po - pe) / (1 - pe), n, po


def fixture():
    # textbook example: 50 items, 2x2 table [[20,5],[10,15]] -> po=0.70, pe=0.50, kappa=0.40
    a = ["Y"] * 25 + ["N"] * 25
    b = ["Y"] * 20 + ["N"] * 5 + ["Y"] * 10 + ["N"] * 15
    k, n, po = cohen_kappa(a, b)
    assert abs(k - 0.40) < 1e-9 and abs(po - 0.70) < 1e-9, (k, po)
    k, _, _ = cohen_kappa(list("ABCABC"), list("ABCABC"))
    assert abs(k - 1.0) < 1e-12
    k, _, po = cohen_kappa(list("AAAA"), list("AAAA"))
    assert k is None and po == 1.0
    # chance-level raters: kappa near 0
    rng = random.Random(1)
    a = [rng.choice("ABC") for _ in range(20000)]
    b = [rng.choice("ABC") for _ in range(20000)]
    k, _, _ = cohen_kappa(a, b)
    assert abs(k) < 0.03, k
    # NA handling: applicable-only pairs
    rows1 = {"x": {"C": "NA"}, "y": {"C": "1"}, "z": {"C": "2"}}
    rows2 = {"x": {"C": "1"}, "y": {"C": "1"}, "z": {"C": "2"}}
    pairs = [(rows1[s]["C"], rows2[s]["C"]) for s in rows1 if rows1[s]["C"] != "NA" and rows2[s]["C"] != "NA"]
    assert len(pairs) == 2
    print("FIXTURE PASS: kappa 0.40 textbook, 1.0 identical, undefined single-level, ~0 chance, NA filter")


def folios():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "vkb", "query.py"),
                        "SELECT folio, image_path, quire, section FROM folios"],
                       capture_output=True, text=True, cwd=ROOT, timeout=120)
    rows = []
    for line in r.stdout.splitlines()[1:]:
        c = [x.strip() for x in line.split("|")]
        if len(c) == 4 and c[0]:
            rows.append(c)
    return rows


def index():
    rows = folios()
    by_img = {}
    for fo, ip, q, sec in rows:
        if ip:
            by_img.setdefault(os.path.basename(ip)[:-4], []).append((fo, q, sec))
    out = ["stem\tfolios\tquire\tsection_group\tmapped"]
    for f in sorted(os.listdir(os.path.join(ROOT, "data", "external", "yale_scans", "pages"))):
        if not f.endswith(".jpg"):
            continue
        st = f[:-4]
        if st in by_img:
            fos = by_img[st]
            sec = fos[0][2]
            grp = "CIRC" if sec in ("A", "Z", "C") else sec
            out.append(f"{st}\t{','.join(x[0] for x in fos)}\t{fos[0][1]}\t{grp}\tyes")
        else:
            out.append(f"{st}\tfoldout:{st.split('_', 1)[1]}\t?\t{FOLD_GROUP[st[:3]]}\tno")
    write_new(os.path.join(A1, "images.tsv"), "\n".join(out) + "\n")
    print(len(out) - 1, "images indexed")


def read_index():
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(A1, "images.tsv"), encoding="utf-8")][1:]
    return rows


def pilot():
    rows = read_index()
    rng = random.Random(SEED)
    pick = []
    for g, k in PILOT.items():
        pool = sorted(r[0] for r in rows if r[3] == g)
        pick += rng.sample(pool, k)
    rng.shuffle(pick)
    write_new(os.path.join(A1, "pilot_images.txt"), "\n".join(pick) + "\n")
    print("\n".join(pick))


LEVELS = {
    "PT": "CIRCLE BATH PHARMA PLANT MARGINAL NONE OTHER", "P_plants": "1 2 3+",
    "P_root": "BULB TUBER TAPROOT BRANCHING NONE", "P_leafshape": "DIVIDED ROUND ELLIPTIC LINEAR NONE",
    "P_leafcount": "0 1-4 5-10 11-20 21+", "P_flower": "0 1 2-4 5+", "P_habit": "ROSETTE SINGLE MULTI",
    "J_shape": "CYLINDER VASE OTHER NONE", "J_count": "0 1-2 3-4 5+", "J_fragcount": "0 1-5 6-15 16+",
    "J_fragtype": "ROOTS LEAVES MIXED NONE", "C_centre": "ANIMAL HUMAN FACE GEOMETRIC EMPTY",
    "C_animal": "FISH HORNED HORNLESS CRAWLER BIRD OTHER", "C_figures": "0 1-9 10-19 20+",
    "C_rings": "0-1 2 3 4+", "C_diagrams": "1 2-3 4+", "C_rays": "PRESENT ABSENT",
    "B_pools": "1 2 3+", "B_figures": "1-5 6-10 11+", "B_tubes": "PRESENT ABSENT"}


def validate(*paths):
    bad = 0
    for p in paths:
        for s, r in read_labels(p).items():
            for cat in CATS:
                if r[cat] != "NA" and r[cat] not in LEVELS[cat].split():
                    print(f"OFF-CODEBOOK {os.path.basename(p)} {s} {cat}={r[cat]!r}"); bad += 1
    print(f"validate: {bad} off-codebook values (kept as written, never edited)")


def assemble(out, *parts):
    """Merge part files: per stem, the LAST row with the full 22 fields wins (agents appended
    correction rows instead of editing; malformed or superseded rows are listed, not used)."""
    rows, log = {}, []
    for p in parts:
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            c = line.split("\t")
            if len(c) != len(COLS):
                log.append(f"# skipped malformed ({len(c)} fields): {os.path.basename(p)} line {i} {c[0]}")
                continue
            if c[0] in rows:
                log.append(f"# superseded: {rows[c[0]][1]} by {os.path.basename(p)} line {i} ({c[0]})")
            rows[c[0]] = (c, f"{os.path.basename(p)} line {i}")
    text = "\t".join(COLS) + "\n" + "".join("\t".join(rows[k][0]) + "\n" for k in sorted(rows))
    write_new(out, text)
    print(f"{out}: {len(rows)} stems"); print("\n".join(log) if log else "# no superseded or malformed rows")
    return log


def read_labels(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\r\n")
        if not line.strip() or line.startswith("stem\t"):
            continue
        c = line.split("\t")
        if len(c) < len(COLS) - 1:
            raise SystemExit(f"bad row in {path}: {line[:80]}")
        c = c + ["-"] * (len(COLS) - len(c))
        out[c[0]] = dict(zip(COLS, c))
    return out


def kappa(p1, p2, out_txt, cons=None):
    a, b = read_labels(p1), read_labels(p2)
    stems = sorted(set(a) & set(b))
    lines = [f"s115-A1 kappa: {os.path.basename(p1)} vs {os.path.basename(p2)}; images in both: {len(stems)}"
             f" (only pass1 {len(set(a) - set(b))}, only pass2 {len(set(b) - set(a))})",
             "category\tn_applicable\tpercent_agree\tkappa\tlevels_pass1\tlevels_pass2"]
    for cat in CATS:
        if cat == "PT":
            pr = [(a[s][cat], b[s][cat]) for s in stems]
        else:
            pr = [(a[s][cat], b[s][cat]) for s in stems if a[s][cat] != "NA" and b[s][cat] != "NA"]
        k, n, po = cohen_kappa([x for x, _ in pr], [y for _, y in pr])
        ks = "undefined" if k is None else f"{k:.3f}"
        pos = "-" if po is None else f"{po:.3f}"
        l1 = ",".join(f"{x}:{c}" for x, c in sorted(Counter(x for x, _ in pr).items()))
        l2 = ",".join(f"{x}:{c}" for x, c in sorted(Counter(y for _, y in pr).items()))
        lines.append(f"{cat}\t{n}\t{pos}\t{ks}\t{l1}\t{l2}")
    write_new(out_txt, "\n".join(lines) + "\n")
    print("\n".join(lines))
    if cons:
        idx = {r[0]: r for r in read_index()}
        rows = ["\t".join(["stem", "folios"] + CATS + ["n_disagree"])]
        for s in stems:
            vals, nd = [], 0
            for cat in CATS:
                x, y = a[s][cat], b[s][cat]
                if x == y:
                    vals.append(x)
                else:
                    vals.append(f"DISAGREE:{x}|{y}"); nd += 1
            rows.append("\t".join([s, idx.get(s, [s, "?"])[1]] + vals + [str(nd)]))
        write_new(cons, "\n".join(rows) + "\n")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fixture":
        fixture()
    elif cmd == "index":
        index()
    elif cmd == "pilot":
        pilot()
    elif cmd == "assemble":
        assemble(*sys.argv[2:])
    elif cmd == "validate":
        validate(*sys.argv[2:])
    elif cmd == "kappa":
        kappa(*sys.argv[2:6])
