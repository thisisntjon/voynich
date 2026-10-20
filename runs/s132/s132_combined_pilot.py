"""s132: Fontana combined reading pilot (Jon approved 2026-10-19 ~11:31 after s130: R1 picture sheet 0.936/0.915,
R2 enhanced crops 0.80/0.797; c-622, c-624, L-372).

Combines what helped: a picture-sheet inventory (example crops, no text shape descriptions) with >= 2 examples per ID,
cut from contrast-enhanced 3x line images; readers read enhanced 3x crops; written conventions for joins and gaps
(CONVENTIONS.md). Pilot lines L05 and L15 (random.Random(132).sample(lines 1-20 minus 14 and 17, 2)).
Gate: per-line token agreement >= 0.95 on BOTH lines (1 - Levenshtein / max length; '.' = word gap), valid tokens.
One attempt. A pass only earns a proposal to Jon for a full s129-style rerun.

Modes:
  fixture                       scorer controls (identical PASS; 10% perturbed FAIL) and sheet rule control
  sheet BOXES.tsv IMGDIR OUT    rows: ID, Lnn, x0, x1 [, single]; x in enhanced 3x pixels (line width 7410);
                                every ID needs >= 2 boxes unless every row of it is marked 'single' (one instance
                                on the whole page); prints SHEET_OK or SHEET_INVALID (an invalid sheet stops the run)
  agree A.tsv B.tsv ROUTE       per-line agreement on L05 and L15
"""
import random, re, sys

LINES = ("L05", "L15")
GATE = 0.95


def parse(path):
    out = {}
    for row in open(path, encoding="utf-8"):
        row = row.rstrip("\n")
        if not row.strip() or row.startswith("#"):
            continue
        k, _, t = row.partition("\t")
        out[k.strip()] = [x for x in t.replace(".", " / ").split() if x]
    return out


def lev(a, b):
    D = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, D[0] = D[0], i
        for j in range(1, len(b) + 1):
            cur = min(D[j] + 1, D[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev, D[j] = D[j], cur
    return D[len(b)]


def agree(pa, pb, route):
    A, B = parse(pa), parse(pb)
    ok = all(re.fullmatch(r"G\d+|/|\?", t) for d in (A, B) for v in d.values() for t in v)
    print(f"token check: {'OK' if ok else 'INVALID TOKENS'}")
    for k in LINES:
        a, b = A.get(k, []), B.get(k, [])
        s = 1 - lev(a, b) / max(len(a), len(b), 1)
        print(f"{k}: tokens A {len(a)} B {len(b)} edits {lev(a, b)} agreement {s:.4f}")
        ok &= s >= GATE and len(a) > 0 and len(b) > 0
    print(f"ROUTE_{route}={'PASS' if ok else 'FAIL'}")


def check_boxes(rows):
    ids = {}
    for r in rows:
        ids.setdefault(r[0], []).append(r)
    bad = [g for g, rs in ids.items() if len(rs) < 2 and not all(len(r) > 4 and r[4].strip() == "single" for r in rs)]
    return ids, bad


def sheet(boxes, imgdir, out):
    from PIL import Image, ImageDraw
    rows = [r.rstrip("\n").split("\t") for r in open(boxes, encoding="utf-8") if r.strip() and not r.startswith("#")]
    rows = [r for r in rows if re.fullmatch(r"G\d+", r[0])]
    ids, bad = check_boxes(rows)
    if bad:
        print(f"SHEET_INVALID: IDs with < 2 examples and not marked single: {sorted(bad)}")
        return
    order = sorted(ids, key=lambda g: int(g[1:]))
    cells = {g: [] for g in order}
    for g in order:
        for r in ids[g]:
            im = Image.open(f"{imgdir}/line_{int(r[1][1:]):02d}_enh.png")
            x0, x1 = max(0, int(r[2]) - 15), min(im.width, int(r[3]) + 15)
            cells[g].append(im.crop((x0, 0, x1, im.height)))
    H = max(c.height for v in cells.values() for c in v) + 20
    W = 200 + max(sum(c.width + 30 for c in v) for v in cells.values())
    S = Image.new("RGB", (W, H * len(order)), "white")
    d = ImageDraw.Draw(S)
    for i, g in enumerate(order):
        d.text((20, i * H + H // 2), g, fill="black")
        x = 200
        for c in cells[g]:
            S.paste(c, (x, i * H))
            x += c.width + 30
    S.save(out)
    print(f"SHEET_OK: {len(order)} IDs, {len(rows)} examples -> {out}")


def fixture():
    rng = random.Random(132)
    ids = [f"G{i:02d}" for i in range(1, 21)]
    base = {k: [rng.choice(ids + ["/"]) for _ in range(50)] for k in LINES}
    pert = {k: [rng.choice(ids) if rng.random() < 0.10 else t for t in v] for k, v in base.items()}
    for name, d in (("fixture_a.tsv", base), ("fixture_b.tsv", base), ("fixture_c.tsv", pert)):
        open(name, "w", encoding="utf-8", newline="\n").write("".join(f"{k}\t{' '.join(v)}\n" for k, v in d.items()))
    print("-- identical (expect PASS)")
    agree("fixture_a.tsv", "fixture_b.tsv", "FIXTURE_IDENTICAL")
    print("-- 10% perturbed (expect FAIL)")
    agree("fixture_a.tsv", "fixture_c.tsv", "FIXTURE_PERTURBED")
    _, bad = check_boxes([["G01", "L01", "1", "2"], ["G02", "L01", "3", "4"], ["G02", "L02", "5", "6"], ["G03", "L03", "7", "8", "single"]])
    print(f"-- sheet rule (expect only G01 rejected): rejected {bad}")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "fixture":
        fixture()
    elif m == "sheet":
        sheet(sys.argv[2], sys.argv[3], sys.argv[4])
    elif m == "agree":
        agree(sys.argv[2], sys.argv[3], sys.argv[4])
