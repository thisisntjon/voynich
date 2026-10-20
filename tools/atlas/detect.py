#!/usr/bin/env python
"""Atlas step 1: drawn-object detection on every Yale scan (reference tool, no statistics, no calls).

Imports tools/plant_regions.py unchanged (page_trim, chroma_mask, PANELS).  Per scan:
  work scale: trimmed scan resized to WORK_H px high.
  paint  = CIELAB a*b* distance from the median parchment > DAB (plant_regions.chroma_mask), opened OPEN px.
  ink    = L / local background (median blur BG px) < INK_REL, not paint.
  writing mask = kraken blla line polygons (data/atlas/work/lines, tools/atlas/text_lines.py), padded TXT_PAD px;
           ink inside it is removed (paint inside it is kept: paint crossing text belongs to a drawing).
  outline ink = ink connected components outside the writing mask with height >= INK_MIN_H and max side >= INK_MIN
           (glyph-sized marks and stray words are dropped; long pen strokes of drawings survive).
  drawing = paint | outline ink, closed CLOSE px, dilated DIL px, 8-connected components.
  keep components with drawn-pixel area >= MIN_AREA x page area and min side >= MIN_SIDE x page height;
  drop border strips (bbox within EDGE of a border and aspect > 4) and components whose drawn pixels are mostly
  outline ink inside a text-dense band (text_frac > TEXT_FRAC_MAX).
  merge: boxes grown by GAP x page height that overlap are merged (repeat until stable).
Output per scan: data/atlas/work/detect/<stem>.json (boxes in full-scan pixels) + overview PNG.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np
from PIL import Image, ImageDraw
import plant_regions as pr

PAGES = ROOT / "data" / "external" / "yale_scans" / "pages"
WORK = ROOT / "data" / "atlas" / "work"
P = dict(WORK_H=1200, DAB=10.0, V_MIN=0.18, OPEN=3, BG=61, INK_REL=0.87, TXT_PAD=3, INK_MIN_H=22, INK_MIN=34,
         CLOSE=7, DIL=7, MIN_AREA=0.00012, MIN_SIDE=0.011, EDGE=0.015, GAP=0.010, TEXT_FRAC_MAX=0.6, PARCH_RUN=0.45, EDGE_BAND=0.012, SEED_AREA=0.00005, BORDER=0.045, HERB_KEEP=0.05, CIRCLE_SUPPORT=0.6, CIRCLE_CONTRAST=0.25, RING_FRAC=0.5, SPLIT_FRAC=0.12, SPLIT_GAP=0.006, STACK_GAP=0.02, HERB_ABSORB=0.25, BAND_X=0.035, EDGE_ZONE=0.08, EDGE_ZONE_Y=0.025, TEXT_XPAD=0.12)


def merge_boxes(boxes, gap):
    boxes = [list(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        out = []
        while boxes:
            a = boxes.pop()
            i = 0
            while i < len(boxes):
                b = boxes[i]
                if a[0] - gap < b[2] and b[0] - gap < a[2] and a[1] - gap < b[3] and b[1] - gap < a[3]:
                    a = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), a[4] + b[4], a[5] + b[5]]
                    boxes.pop(i); changed = True
                else:
                    i += 1
            out.append(a)
        boxes = out
    return boxes


def stack_merge(boxes, vgap, xov=0.6):
    """Merge vertically stacked boxes (jar bands, stem + root): x-overlap >= xov of the narrower, vertical gap <= vgap."""
    boxes = [list(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                ov = min(a[2], b[2]) - max(a[0], b[0])
                gapy = max(a[1], b[1]) - min(a[3], b[3])
                if ov >= xov * min(a[2] - a[0], b[2] - b[0]) and gapy <= vgap:
                    boxes[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), a[4] + b[4], a[5] + b[5]]
                    boxes.pop(j); changed = True
                    break
            if changed:
                break
    return boxes


def detect(fname, P=P, lines=None, debug=False, gap=None, xr=None, herbal=False, circles=False, ink_rel=None, stack=False):
    import cv2
    im = Image.open(PAGES / fname).convert("RGB")
    full = np.asarray(im)
    xoff = 0
    if xr is not None:
        xoff = int(xr[0] * full.shape[1])
        part = full[:, xoff:int(xr[1] * full.shape[1])]
    else:
        part = full
    tx0, ty0, tx1, ty1 = pr.page_trim(part)
    arr = part[ty0:ty1, tx0:tx1]
    tx0 += xoff; tx1 += xoff
    sc = P["WORK_H"] / arr.shape[0]
    Ws = max(1, int(arr.shape[1] * sc)); Hs = P["WORK_H"]
    sm = cv2.resize(arr, (Ws, Hs), interpolation=cv2.INTER_AREA)
    paint, valid = pr.chroma_mask(sm, P)
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r))
    paint = cv2.morphologyEx(paint.astype(np.uint8), cv2.MORPH_OPEN, k(P["OPEN"])) > 0
    L = cv2.cvtColor(sm, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    bg = cv2.medianBlur(L.astype(np.uint8), P["BG"]).astype(np.float32)
    bg = np.maximum(bg, cv2.dilate(L, k(9)) * 0)  # (no-op guard)
    ink = (L / np.maximum(bg, 1) < (ink_rel or P["INK_REL"])) & valid & ~paint
    # page region: rows/cols where most pixels are parchment-like (excludes neighbouring page edges, tape, binding)
    lab3 = cv2.cvtColor(sm, cv2.COLOR_RGB2LAB).astype(np.float32)
    med = np.median(lab3[valid], axis=0)
    parch = (np.abs(lab3[..., 0] - med[0]) < 28) & (np.hypot(lab3[..., 1] - med[1], lab3[..., 2] - med[2]) < 9)
    def run(prof):
        good = prof > P["PARCH_RUN"]
        best, cur, bs = (0, len(prof)), 0, 0
        bl = -1
        for i, g in enumerate(list(good) + [False]):
            if g:
                if cur == 0: bs = i
                cur += 1
            else:
                if cur > bl: bl, best = cur, (bs, bs + cur)
                cur = 0
        return best
    px0, px1 = run(cv2.blur(parch.mean(0)[None, :].astype(np.float32), (15, 1))[0])
    px0, px1 = 0, Ws  # column-profile page region proved unreliable (cut plants on f19v); border filters below instead
    eb = int(P["EDGE_BAND"] * Hs); py0, py1 = eb, Hs - eb
    region = np.zeros_like(valid); region[py0:py1, px0:px1] = True
    bx_, by_ = int(P["BAND_X"] * Ws), int(P["EDGE_BAND"] * Hs)
    region[:, :bx_] = False; region[:, Ws - bx_:] = False
    paint &= region; ink &= region
    txt = np.zeros((Hs, Ws), np.uint8)
    for ln in (lines or []):
        poly = (np.asarray(ln["poly"], np.float32) - [tx0, ty0]) * sc
        cv2.fillPoly(txt, [poly.astype(np.int32)], 1)
    if P["TXT_PAD"]:
        txt = cv2.dilate(txt, k(2 * P["TXT_PAD"] + 1))
    txt = txt > 0
    kept, good = [], []
    if circles:
        # cosmological / zodiac diagrams: large circles drawn in thin ink (often under text rings) - Hough circles on
        # the grey image, verified by ink along the circumference; the outermost of each concentric family is kept
        g = cv2.GaussianBlur(cv2.cvtColor(sm, cv2.COLOR_RGB2GRAY), (5, 5), 0)
        cs = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, dp=2, minDist=int(0.08 * Hs), param1=60, param2=60,
                              minRadius=int(0.12 * Hs), maxRadius=int(0.5 * Hs))
        inkall = (L / np.maximum(bg, 1) < 0.92) & valid
        inkall = cv2.dilate(inkall.astype(np.uint8), k(5)) > 0
        for cx_, cy_, r_ in (cs[0] if cs is not None else []):
            t = np.linspace(0, 2 * np.pi, 360, endpoint=False)
            xs = (cx_ + r_ * np.cos(t)).astype(int); ys = (cy_ + r_ * np.sin(t)).astype(int)
            ok = (xs >= 0) & (xs < Ws) & (ys >= 0) & (ys < Hs)
            if ok.mean() < 0.9:
                continue
            def ring(rr):
                xx = (cx_ + rr * np.cos(t)).astype(int); yy = (cy_ + rr * np.sin(t)).astype(int)
                o2 = (xx >= 0) & (xx < Ws) & (yy >= 0) & (yy < Hs)
                return inkall[yy[o2], xx[o2]].mean() if o2.any() else 1.0
            sup = ring(r_)
            contrast = sup - max(ring(r_ * 0.94), ring(r_ * 1.06))
            if sup >= P["CIRCLE_SUPPORT"] and contrast >= P["CIRCLE_CONTRAST"]:
                good.append((float(cx_), float(cy_), float(r_), float(sup)))
        good.sort(key=lambda c: -c[2])
        kept = []
        for c in good:
            if any(np.hypot(c[0] - d[0], c[1] - d[1]) < max(c[2], d[2]) for d in kept):
                continue  # concentric / inner circle of an already kept diagram
            kept.append(c)
        ink_u = ink.astype(np.uint8)
        th = max(3, int(0.012 * Hs))
        t = np.linspace(0, 2 * np.pi, 720, endpoint=False)
        for cx_, cy_, r_, sup in kept:
            # concentric rings share the centre (Hough returns one per centre): radial ink profile around the centre,
            # every radius with ink on >= RING_FRAC of the angles is a ring and is erased from the ink
            for rr in range(int(0.03 * Hs), int(r_ * 1.08)):
                xx = (cx_ + rr * np.cos(t)).astype(int); yy = (cy_ + rr * np.sin(t)).astype(int)
                o2 = (xx >= 0) & (xx < Ws) & (yy >= 0) & (yy < Hs)
                if o2.mean() > 0.8 and inkall[yy[o2], xx[o2]].mean() >= P["RING_FRAC"]:
                    cv2.circle(ink_u, (int(cx_), int(cy_)), rr, 0, thickness=th)
        for cx_, cy_, r_, sup in good:  # erase verified rings from the ink so they do not chain figures together
            cv2.circle(ink_u, (int(cx_), int(cy_)), int(r_), 0, thickness=th)
        ink = ink_u > 0
    ink_out = ink & ~txt
    n, lab, st, _ = cv2.connectedComponentsWithStats(ink_out.astype(np.uint8), 8)
    keep = (st[:, 3] >= P["INK_MIN_H"]) & (np.maximum(st[:, 2], st[:, 3]) >= P["INK_MIN"])
    # page edges / gutter shadows: long straight ink strips
    tall = (st[:, 3] > 0.25 * Hs) & (st[:, 2] < 0.08 * st[:, 3])
    wide = (st[:, 2] > 0.25 * Ws) & (st[:, 3] < 0.08 * st[:, 2])
    cx = st[:, 0] + st[:, 2] / 2
    border = (cx < px0 + 0.04 * Ws) | (cx > px1 - 0.04 * Ws)
    keep &= ~tall & ~wide & ~border
    keep[0] = False
    big_ink = keep[lab]
    drawing = (paint | big_ink).astype(np.uint8)
    drawing = cv2.morphologyEx(drawing, cv2.MORPH_CLOSE, k(P["CLOSE"]))
    dil = cv2.dilate(drawing, k(P["DIL"]))
    n, lab, st, _ = cv2.connectedComponentsWithStats(dil, 8)
    page_area = Hs * Ws
    text_x = None
    if lines and len(lines) >= 3:
        lx0 = np.percentile([(ln["x0"] - tx0) * sc for ln in lines], 5); lx1 = np.percentile([(ln["x1"] - tx0) * sc for ln in lines], 95)
        text_x = (lx0 - P["TEXT_XPAD"] * Ws, lx1 + P["TEXT_XPAD"] * Ws)
    cands = []
    raw = drawing > 0
    for i in range(1, n):
        x, y, w, h, _ = st[i]
        sub = lab[y:y + h, x:x + w] == i
        a = int((raw[y:y + h, x:x + w] & sub).sum())
        pa = int((paint[y:y + h, x:x + w] & sub).sum())
        # pre-merge filter: specks, and edge debris (tape, neighbouring leaves, gutter) near the scan border
        if a < P["SEED_AREA"] * Hs * Ws:
            continue
        ccx, ccy = x + w / 2, y + h / 2
        b = P["BORDER"]
        if (ccx < px0 + b * Ws or ccx > px1 - b * Ws or ccy < b * Hs or ccy > (1 - b) * Hs) and a < 0.01 * Hs * Ws:
            continue
        if (x <= px0 + 2 or x + w >= px1 - 2 or y <= py0 + 2 or y + h >= py1 - 2) and max(w, h) > 4 * min(w, h):
            continue
        # edge-zone rule: drop components whose drawn pixels lie mostly in the outer EDGE_ZONE of the scan width
        # or outside the text block's x-extent widened by TEXT_XPAD (stained page edges, neighbouring leaves)
        ez = int(P["EDGE_ZONE"] * Ws)
        colw = (raw[y:y + h, x:x + w] & sub).sum(0)
        cols = np.arange(x, x + w)
        roww = (raw[y:y + h, x:x + w] & sub).sum(1)
        rows_ = np.arange(y, y + h)
        ezy = int(P["EDGE_ZONE_Y"] * Hs)
        inzone = colw[(cols < ez) | (cols >= Ws - ez)].sum() + roww[(rows_ < ezy) | (rows_ >= Hs - ezy)].sum()
        if inzone > 0.5 * max(1, colw.sum()):
            continue
        if text_x is not None and not (text_x[0] <= x + w / 2 <= text_x[1]):
            continue
        cands.append([x, y, x + w, y + h, a, pa])
    gap = (P["GAP"] if gap is None else gap) * Hs
    boxes = merge_boxes(cands, gap)
    if stack:
        boxes = stack_merge(boxes, P["STACK_GAP"] * Hs)
    out = []
    for x0, y0, x1, y1, a, pa in boxes:
        w, h = x1 - x0, y1 - y0
        if a < P["MIN_AREA"] * page_area or min(w, h) < P["MIN_SIDE"] * Hs:
            continue
        e = P["EDGE"]
        near = x0 < e * Ws or y0 < e * Hs or x1 > (1 - e) * Ws or y1 > (1 - e) * Hs
        if near and max(w, h) / max(1, min(w, h)) > 4:
            continue
        nearx = x0 < 0.06 * Ws or x1 > 0.94 * Ws
        if nearx and h > 4 * w:
            continue
        if pa < 0.1 * a and h > 5 * w and w < 0.03 * Ws:
            continue  # thin unpainted vertical strip: page edge / gutter
        if (x0 < 0.08 * Ws or x1 > 0.92 * Ws) and h > 3 * w and h > 0.3 * Hs:
            continue  # tall strip at the scan's left/right edge: page edges, tape
        if w > 0.97 * Ws and h > 0.97 * Hs:
            continue
        tf = float(txt[y0:y1, x0:x1].mean())
        if pa < 0.05 * a and tf > P["TEXT_FRAC_MAX"]:
            continue
        if tf > 0.5 and w > 2.5 * h and h < 0.04 * Hs:
            continue  # a written word / line (red ink counts as paint)
        out.append(dict(bbox=[int(x0 / sc) + tx0, int(y0 / sc) + ty0, int(w / sc), int(h / sc)],
                        draw_px_full=int(a / sc / sc), paint_frac=round(pa / max(a, 1), 3), text_frac=round(tf, 3),
                        bbox_work=[int(x0), int(y0), int(w), int(h)]))
    if not herbal:
        # oversized objects (thin ink and pipes chain whole pages together): split by paint-only components
        drawn = (drawing > 0) if stack else paint  # figure sections: paint | outline ink; others: paint only

        def split_box(x, y, w, h, close, dil, gapf, opn=0):
            pm = drawn[y:y + h, x:x + w].astype(np.uint8)
            if opn:
                pm = cv2.morphologyEx(pm, cv2.MORPH_OPEN, k(opn))
            core = pm > 0
            if close:
                pm = cv2.morphologyEx(pm, cv2.MORPH_CLOSE, k(close))
            if dil:
                pm = cv2.dilate(pm, k(dil))
            n2, lab2, st2, _ = cv2.connectedComponentsWithStats(pm, 8)
            subs = []
            for j in range(1, n2):
                xx, yy, ww, hh, _ = st2[j]
                aa = int((core[yy:yy + hh, xx:xx + ww] & (lab2[yy:yy + hh, xx:xx + ww] == j)).sum())
                if aa < 0.5 * P["MIN_AREA"] * Hs * Ws:
                    continue
                if aa < P["SEED_AREA"] * Hs * Ws:
                    continue
                subs.append([x + xx, y + yy, x + xx + ww, y + yy + hh, aa, aa])
            subs = merge_boxes(subs, gapf * Hs) if gapf else subs
            subs = stack_merge(subs, P["STACK_GAP"] * Hs)
            return [b for b in subs if b[4] >= P["MIN_AREA"] * Hs * Ws and min(b[2] - b[0], b[3] - b[1]) >= P["MIN_SIDE"] * Hs
                    and not (min(b[2] - b[0], b[3] - b[1]) < 0.03 * Ws and max(b[2] - b[0], b[3] - b[1]) > 5 * min(b[2] - b[0], b[3] - b[1]))]

        def mk(X0, Y0, X1, Y1, aa):
            return dict(bbox=[int(X0 / sc) + tx0, int(Y0 / sc) + ty0, int((X1 - X0) / sc), int((Y1 - Y0) / sc)],
                        draw_px_full=int(aa / sc / sc), paint_frac=1.0, text_frac=round(float(txt[Y0:Y1, X0:X1].mean()), 3),
                        bbox_work=[int(X0), int(Y0), int(X1 - X0), int(Y1 - Y0)], split_from_oversized=True)

        big = P["SPLIT_FRAC"] * Ws * Hs
        split_out = []
        for o in out:
            x, y, w, h = o["bbox_work"]
            if w * h <= big:
                split_out.append(o); continue
            subs = split_box(x, y, w, h, 3, 3, P["SPLIT_GAP"])
            if len(subs) < 2:
                subs2 = split_box(x, y, w, h, 11, 3, 0)
                if len(subs2) < 2:
                    split_out.append(o); continue
                subs = subs2
            for X0, Y0, X1, Y1, aa, _ in subs:
                if (X1 - X0) * (Y1 - Y0) > big:  # still oversized: second level, no dilation, opened paint
                    s2 = split_box(X0, Y0, X1 - X0, Y1 - Y0, 11, 3, 0)
                    if len(s2) >= 2:
                        split_out += [mk(*b[:5]) for b in s2]
                        continue
                split_out.append(mk(X0, Y0, X1, Y1, aa))
        out = split_out
    if circles:
        for cx_, cy_, r_, sup in kept:
            X0, Y0 = max(0, int(cx_ - r_)), max(0, int(cy_ - r_)); X1, Y1 = min(Ws, int(cx_ + r_)), min(Hs, int(cy_ + r_))
            out.append(dict(bbox=[int(X0 / sc) + tx0, int(Y0 / sc) + ty0, int((X1 - X0) / sc), int((Y1 - Y0) / sc)],
                            draw_px_full=int(np.pi * r_ * r_ / sc / sc), paint_frac=0.0,
                            text_frac=round(float(txt[Y0:Y1, X0:X1].mean()), 3), bbox_work=[X0, Y0, X1 - X0, Y1 - Y0],
                            circle=[round(cx_ / sc + tx0), round(cy_ / sc + ty0), round(r_ / sc)], circle_support=round(sup, 3)))
    if herbal and out:
        # herbal page: one main plant = union of components with drawn area >= HERB_KEEP x the largest
        # (as tools/plant_regions.herbal_crop); smaller components outside that box stay separate objects
        big = max(o["draw_px_full"] for o in out)
        main = [o for o in out if o["draw_px_full"] >= P["HERB_KEEP"] * big]
        X0 = min(o["bbox_work"][0] for o in main); Y0 = min(o["bbox_work"][1] for o in main)
        X1 = max(o["bbox_work"][0] + o["bbox_work"][2] for o in main); Y1 = max(o["bbox_work"][1] + o["bbox_work"][3] for o in main)
        rest = []
        g = P["HERB_ABSORB"] * Hs
        for o in sorted([o for o in out if o not in main], key=lambda o: -o["draw_px_full"]):
            x, y, w, h = o["bbox_work"]
            if x >= X0 - g and y >= Y0 - g and x + w <= X1 + g and y + h <= Y1 + g:
                # inside or just beyond the plant box (flower heads, root tips on faint stems): part of it
                X0, Y0, X1, Y1 = min(X0, x), min(Y0, y), max(X1, x + w), max(Y1, y + h)
                main.append(o)
                continue
            rest.append(o)
        a = sum(o["draw_px_full"] for o in main)
        pf = sum(o["paint_frac"] * o["draw_px_full"] for o in main) / max(a, 1)
        merged = dict(bbox=[int(X0 / sc) + tx0, int(Y0 / sc) + ty0, int((X1 - X0) / sc), int((Y1 - Y0) / sc)],
                      draw_px_full=a, paint_frac=round(pf, 3), text_frac=round(float(txt[Y0:Y1, X0:X1].mean()), 3),
                      bbox_work=[int(X0), int(Y0), int(X1 - X0), int(Y1 - Y0)], n_parts=len(main))
        out = [merged] + rest
    out.sort(key=lambda o: (o["bbox"][1] // 200, o["bbox"][0]))
    dbg = None
    if debug:
        ov = sm.copy()
        ov[paint] = (ov[paint] * 0.4 + np.array([255, 0, 255]) * 0.6).astype(np.uint8)
        ov[big_ink] = (0, 0, 255); ov[txt & ink] = (255, 160, 0)
        o = Image.fromarray(ov); d = ImageDraw.Draw(o)
        d.rectangle([px0, py0, px1, py1], outline="green", width=2)
        for j, b in enumerate(out):
            x, y, w, h = b["bbox_work"]; d.rectangle([x, y, x + w, y + h], outline="red", width=3); d.text((x + 3, y + 3), str(j), fill="red")
        dbg = o
    region_full = [int(px0 / sc) + tx0, int(py0 / sc) + ty0, int(px1 / sc) + tx0, int(py1 / sc) + ty0]
    return dict(file=fname, size=[full.shape[1], full.shape[0]], trim=[tx0, ty0, tx1, ty1], page_region=region_full, scale=sc, objects=out), dbg
