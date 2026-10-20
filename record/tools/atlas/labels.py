#!/usr/bin/env python
"""Atlas step: label points in scan pixels, only on pages whose word-box registration passes (reference tool).

Registration (box canvas -> Yale scan): tools/s116_label_object.register_page (imported unchanged; results cached in
runs/s116/pages.tsv are reused, missing pages are registered fresh).  Its label-free check: the page's word boxes are
split at median y; each half is registered independently; PASS-A when both half transforms put the four corners of the
box extent within 120 scan px of the full transform, and the scale is not at the search edge.
Atlas adds an independent second check, PASS-B (or PASS-C where kraken misses ring text): >= 60 % of the transformed word-box centres fall inside the kraken
text-line polygons (data/atlas/work/lines, padded 0.5 line height) of that scan.
PASS-C: >= 85 % of the transformed word boxes contain ink (>= 3 % local-dark pixels) and that rate exceeds the rate
for the same boxes shifted +-8 % of the page height in x or y (mean of 4 shifts) by >= 0.15.
A page's labels are linked only when PASS-A holds and PASS-B or PASS-C holds.  Label point = mean centre of the label's
string-matched boxes (s116_label_object.label_loci, imported unchanged), transformed to scan px.
Output: data/atlas/work/label_points.json, data/atlas/work/registration.tsv
"""
import csv, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np
import boxes as bm
import s116_label_object as s116

WORK = ROOT / "data" / "atlas" / "work"


def in_text_frac(scan, pts):
    import cv2
    lp = WORK / "lines" / (Path(scan).stem + ".json")
    if not lp.exists():
        return None
    d = json.loads(lp.read_text())
    W, H = d["size"]; f = 4
    m = np.zeros((H // f + 1, W // f + 1), np.uint8)
    for ln in d["lines"]:
        poly = (np.asarray(ln["poly"], np.float32) / f).astype(np.int32)
        cv2.fillPoly(m, [poly], 1)
        hh = max(2, int(0.5 * (ln["y1"] - ln["y0"]) / f))
        cv2.polylines(m, [poly], True, 1, thickness=hh)
    pts = np.asarray(pts) / f
    ok = [(0 <= x < m.shape[1] and 0 <= y < m.shape[0] and m[int(y), int(x)] > 0) for x, y in pts]
    return float(np.mean(ok)) if ok else None


def ink_hit(scan, bx, sx, sy, ox, oy):
    """Fraction of transformed word-box rectangles that contain ink (local-dark pixels >= 3 % of the box), versus the
    same rectangles shifted by +-8 % of the page in x and y (mean of 4 shifts).  Returns (hit, control)."""
    import cv2
    from PIL import Image
    im = Image.open(ROOT / "data" / "external" / "yale_scans" / "pages" / scan).convert("L")
    f = 4
    g = np.asarray(im.resize((im.size[0] // f, im.size[1] // f)), np.float32)
    bg = cv2.medianBlur(g.astype(np.uint8), 31).astype(np.float32)
    ink = (g / np.maximum(bg, 1)) < 0.8
    H, W = ink.shape

    def rate(dx, dy):
        hits = []
        for b in bx:
            x0 = int((sx * b["x"] + ox) / f + dx); y0 = int((sy * b["y"] + oy) / f + dy)
            x1 = int((sx * (b["x"] + b["w"]) + ox) / f + dx); y1 = int((sy * (b["y"] + b["h"]) + oy) / f + dy)
            if x1 <= x0 or y1 <= y0 or x0 < 0 or y0 < 0 or x1 > W or y1 > H:
                continue
            hits.append(ink[y0:y1, x0:x1].mean() >= 0.03)
        return float(np.mean(hits)) if hits else 0.0
    d = 0.08 * H
    return rate(0, 0), float(np.mean([rate(d, 0), rate(-d, 0), rate(0, d), rate(0, -d)]))


def main():
    cached = {}
    with open(ROOT / "runs" / "s116" / "pages.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            cached[r["page"]] = r
    labels = s116.label_loci()
    rows, points = [], []
    for page in sorted(labels):
        R = cached.get(page)
        if R is None:
            R = {k: str(v) for k, v in s116.register_page(page).items()}
        okA = R["ok"] == "True"
        sx, sy, ox, oy = (float(R[k]) for k in ("sx", "sy", "ox", "oy"))
        bx = bm.load_boxes(page) or []
        pts = [(sx * b["cx"] + ox, sy * b["cy"] + oy) for b in bx]
        fB = in_text_frac(R["scan"], pts) if R["scan"] else None
        okB = fB is not None and fB >= 0.60
        hit, ctl = ink_hit(R["scan"], bx, sx, sy, ox, oy) if (R["scan"] and okA and not okB) else (None, None)
        okC = hit is not None and hit >= 0.85 and hit - ctl >= 0.15
        ok = okA and (okB or okC)
        rows.append(dict(page=page, scan=R["scan"], passA=okA, passA_why=R["why"], passB=okB,
                         frac_box_centres_in_text=None if fB is None else round(fB, 3),
                         passC=okC, ink_hit=None if hit is None else round(hit, 3), ink_hit_shifted=None if ctl is None else round(ctl, 3), linked=ok,
                         n_labels=len(labels[page]), sx=sx, sy=sy, ox=ox, oy=oy, source="cached s116" if page in cached else "fresh"))
        if ok:
            for L in labels[page]:
                px = float(np.mean([p[0] for p in L["pts"]])); py = float(np.mean([p[1] for p in L["pts"]]))
                points.append(dict(uid=L["uid"], page=page, scan=R["scan"], text=".".join(L["toks"]),
                                   x=round(sx * px + ox, 1), y=round(sy * py + oy, 1)))
        print(page, R["scan"], "A", okA, "B", fB, "C", hit, ctl, "->", ok, flush=True)
    with open(WORK / "registration.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t"); w.writeheader(); w.writerows(rows)
    (WORK / "label_points.json").write_text(json.dumps(points, indent=0))
    print("pages", len(rows), "linked", sum(r["linked"] for r in rows), "label points", len(points))


if __name__ == "__main__":
    main()
