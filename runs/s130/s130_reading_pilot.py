"""s130: Fontana reading-feasibility pilot (Jon brief 11:17; follows s129 STEP_A_GATE=FAIL, c-621, L-369).

Two reading aids, each piloted on lines L14 and L17 (random.Random(130).sample(range(1,21),2)) by two blind readers:
  R1 exemplar inventory: reader R1a builds an ID inventory with example boxes; this script cuts those boxes into an
     image sheet; reader R1b reads from the image sheet only (no text shape descriptions).
  R2 enhanced crops: two readers use the s129 text inventory (inventory_A.md) with autocontrast + unsharp + 3x Lanczos
     crops split into 4 abutting segments.
A route passes only if per-line token agreement is >= 0.95 on BOTH pilot lines; otherwise it is recorded failed and stops.

Modes:
  fixture                     agreement scorer controls (identical -> 1.0 PASS; 10% perturbed -> FAIL)
  sheet BOXES.tsv IMGDIR OUT  cut example boxes (ID, line, x0, x1 in full-line-crop pixels) into a labelled sheet
  agree A.tsv B.tsv ROUTE     per-line agreement on L14 and L17; prints ROUTE_<name>=PASS/FAIL
"""
import random, re, sys

LINES = ("L14", "L17")
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


def line_agreement(a, b):
    return 1 - lev(a, b) / max(len(a), len(b), 1)


def valid_tokens(lines):
    return all(re.fullmatch(r"G\d+|/|\?", t) for v in lines.values() for t in v)


def agree(pa, pb, route):
    A, B = parse(pa), parse(pb)
    ok = valid_tokens(A) and valid_tokens(B)
    print(f"token check: {'OK' if ok else 'INVALID TOKENS'}")
    for k in LINES:
        a, b = A.get(k, []), B.get(k, [])
        s = line_agreement(a, b)
        print(f"{k}: tokens A {len(a)} B {len(b)} edits {lev(a, b)} agreement {s:.4f}")
        ok &= s >= GATE and len(a) > 0 and len(b) > 0
    print(f"ROUTE_{route}={'PASS' if ok else 'FAIL'}")


def sheet(boxes, imgdir, out):
    from PIL import Image, ImageDraw
    rows = [r.rstrip("\n").split("\t") for r in open(boxes, encoding="utf-8") if r.strip() and not r.startswith("#")]
    rows = [r for r in rows if re.fullmatch(r"G\d+", r[0])]
    ids = sorted({r[0] for r in rows}, key=lambda g: int(g[1:]))
    cells = {g: [] for g in ids}
    for g, line, x0, x1 in (r[:4] for r in rows):
        im = Image.open(f"{imgdir}/line_{int(line[1:]):02d}.png")
        x0, x1 = max(0, int(x0) - 6), min(im.width, int(x1) + 6)
        c = im.crop((x0, 0, x1, im.height))
        cells[g].append(c.resize((c.width * 2, c.height * 2)))
    H = 240 + 10
    W = 160 + max(sum(c.width + 20 for c in v) for v in cells.values())
    S = Image.new("RGB", (W, H * len(ids)), "white")
    d = ImageDraw.Draw(S)
    for i, g in enumerate(ids):
        d.text((10, i * H + 100), g, fill="black")
        x = 160
        for c in cells[g]:
            S.paste(c, (x, i * H))
            x += c.width + 20
    S.save(out)
    print(f"sheet: {len(ids)} IDs, {len(rows)} examples -> {out}")


def fixture():
    rng = random.Random(130)
    ids = [f"G{i:02d}" for i in range(1, 21)]
    base = {k: [rng.choice(ids + ["/"]) for _ in range(50)] for k in LINES}
    open("fixture_a.tsv", "w", encoding="utf-8", newline="\n").write("".join(f"{k}\t{' '.join(v)}\n" for k, v in base.items()))
    open("fixture_b.tsv", "w", encoding="utf-8", newline="\n").write("".join(f"{k}\t{' '.join(v)}\n" for k, v in base.items()))
    pert = {k: [rng.choice(ids) if rng.random() < 0.10 else t for t in v] for k, v in base.items()}
    open("fixture_c.tsv", "w", encoding="utf-8", newline="\n").write("".join(f"{k}\t{' '.join(v)}\n" for k, v in pert.items()))
    print("-- identical (expect PASS)")
    agree("fixture_a.tsv", "fixture_b.tsv", "FIXTURE_IDENTICAL")
    print("-- 10% perturbed (expect FAIL)")
    agree("fixture_a.tsv", "fixture_c.tsv", "FIXTURE_PERTURBED")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "fixture":
        fixture()
    elif m == "sheet":
        sheet(sys.argv[2], sys.argv[3], sys.argv[4])
    elif m == "agree":
        agree(sys.argv[2], sys.argv[3], sys.argv[4])
