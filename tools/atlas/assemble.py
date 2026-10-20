#!/usr/bin/env python
"""Atlas assemble stage: objects.tsv, browser data (data/atlas/atlas_data.js + .json), neighbours, links.

Reference tool. No statistics, no calls.  Kinds and captions are machine-generated (qwen2.5vl) and are never an
identification.  Pharma fragment candidates are geometric (row / left-to-right rank), not an identification either.
"""
import csv, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "atlas"))
import numpy as np
import build as B

ATLAS = B.ATLAS
WORK = B.WORK
SKIP_ATTR = {"bifolio", "quire", "loci-count", "panels", "rz-language", "currier-language", "section-subset",
             "hand", "page-type"}
QUERIES = ["root with a face", "jar with lid", "jar with a spout", "tall decorated jar", "plant with blue flowers",
           "plant with red flowers", "large single leaf", "bulbous root", "root like an animal", "tangled roots",
           "woman bathing in a pool", "group of women", "woman holding a ring", "woman with a crown",
           "figure in a tub", "pipe or tube", "pool of blue water", "green pool", "star with rays", "eight pointed star",
           "sun with a face", "moon crescent", "rosette", "circle diagram with text", "zodiac animal", "fish", "ram",
           "bull", "crab", "scorpion", "lion", "archer", "dragon or lizard", "bird", "castle or tower",
           "clouds", "barrel", "cup", "spiral", "tree", "seed pod", "leaves on a stem", "page edge or stain", "handwriting"]


def facts_by_folio():
    con = B.vkb()
    out = {}
    for folio, attr, val, src in con.execute("SELECT folio, attribute, value, source FROM page_facts"):
        if attr in SKIP_ATTR:
            continue
        out.setdefault(folio, []).append(dict(a=attr, v=val, s=src))
    return out


def captions():
    c = {}
    p = WORK / "captions.jsonl"
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            try:
                j = json.loads(ln)
            except Exception:
                continue
            if j.get("kind") or j["object_id"] not in c:
                c[j["object_id"]] = j
    return c


def box_dist(o, x, y):
    dx = max(o["x"] - x, 0, x - (o["x"] + o["w"]))
    dy = max(o["y"] - y, 0, y - (o["y"] + o["h"]))
    return float(np.hypot(dx, dy))


def pharma_rows(objs, facts):
    """Geometric candidates: per pharma folio, objects (not jars by caption) are grouped into the number of rows the
    source lists, by y-centre (largest gaps); within a row ranked left to right; fragment with the same row and rank."""
    res = {}
    by_f = {}
    for o in objs:
        if o["folio"] and any(f["a"] == "pharma-fragment" for f in facts.get(o["folio"], [])):
            by_f.setdefault(o["folio"], []).append(o)
    for folio, os_ in by_f.items():
        frs = []
        for f in facts[folio]:
            if f["a"] != "pharma-fragment":
                continue
            v = f["v"]
            try:
                n = int(v.split("fragment")[1].split(",")[0]); r = int(v.split("row")[1].strip().split()[0])
            except Exception:
                continue
            frs.append((r, n, v))
        if not frs:
            continue
        nrows = max(r for r, _, _ in frs)
        parts = [o for o in os_ if o.get("kind") not in ("jar",) and o.get("is_drawing") is not False]
        if len(parts) < nrows:
            continue
        ys = sorted(parts, key=lambda o: o["y"] + o["h"] / 2)
        cy = [o["y"] + o["h"] / 2 for o in ys]
        gaps = sorted(range(1, len(cy)), key=lambda i: -(cy[i] - cy[i - 1]))[:nrows - 1]
        cuts = sorted(gaps)
        rows, start = [], 0
        for c in cuts + [len(ys)]:
            rows.append(ys[start:c]); start = c
        for ri, row in enumerate(rows, 1):
            rf = sorted([(n, v) for r, n, v in frs if r == ri])
            row = sorted(row, key=lambda o: o["x"])
            for k, o in enumerate(row):
                cand = rf[k][1] if k < len(rf) else ""
                res[o["object_id"]] = dict(row=ri, rank=k + 1, n_in_row=len(row), n_frag_in_row=len(rf),
                                           candidate=cand, count_match=len(row) == len(rf))
    return res


def main():
    objs = B.objects_list()
    fm = B.folio_meta()
    facts = facts_by_folio()
    cap = captions()
    for o in objs:
        c = cap.get(o["object_id"], {})
        o["kind"] = c.get("kind", ""); o["caption"] = c.get("caption", ""); o["is_drawing"] = c.get("is_drawing")
        o["kind_source"] = o["caption_source"] = "qwen2.5vl" if c else ""
        m = fm.get(o["folio"], {})
        o["quire"] = m.get("quire", ""); o["bifolio"] = m.get("bifolio", ""); o["hand_davis"] = m.get("hand_davis", "")
    # neighbours
    ids_p = ATLAS / "emb_ids.json"
    nn = {}
    if ids_p.exists():
        ids = json.loads(ids_p.read_text())
        E = np.load(ATLAS / "emb_dinov2.npy")
        idx = {i: k for k, i in enumerate(ids)}
        S = E @ E.T
        np.fill_diagonal(S, -9)
        for i, oid in enumerate(ids):
            top = np.argsort(-S[i])[:10]
            nn[oid] = [(ids[j], round(float(S[i, j]), 3)) for j in top]
    for o in objs:
        o["nn_dinov2"] = nn.get(o["object_id"], [])
    # labels
    lp = WORK / "label_points.json"
    reg = {}
    if (WORK / "registration.tsv").exists():
        with open(WORK / "registration.tsv", encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                reg[r["page"]] = r
    by_scan = {}
    for o in objs:
        o["labels"] = []
        by_scan.setdefault(o["scan"], []).append(o)
    n_lab_linked = 0
    if lp.exists():
        for L in json.loads(lp.read_text()):
            cands = [o for o in by_scan.get(L["scan"], []) if o.get("is_drawing") is not False
                     and (not o["folio"] or o["folio"] == L["page"] or L["page"] in o["panels_covered"].split(";"))]
            if not cands:
                continue
            size = json.loads((WORK / "detect" / (Path(L["scan"]).stem + ".json")).read_text())["size"]
            d = [(box_dist(o, L["x"], L["y"]), o) for o in cands]
            dmin, best = min(d, key=lambda t: t[0])
            if dmin <= 0.06 * size[1]:
                best["labels"].append(dict(uid=L["uid"], text=L["text"], dist_px=round(dmin)))
                n_lab_linked += 1
    # pharma
    ph = pharma_rows(objs, facts)
    for o in objs:
        o["pharma_row_candidate"] = ph.get(o["object_id"], {})
        o["jon_observation"] = ""
    # siglip canned queries
    canned = {}
    if ids_p.exists() and (ATLAS / "emb_siglip.npy").exists():
        canned = siglip_queries(json.loads(ids_p.read_text()), np.load(ATLAS / "emb_siglip.npy"))
    # TSV
    cols = ["object_id", "folio", "panels_covered", "folio_assignment", "section", "quire", "bifolio", "hand_davis",
            "scan", "x", "y", "w", "h", "area_px", "drawn_px", "paint_frac", "text_frac", "is_drawing", "kind",
            "kind_source", "caption", "caption_source", "labels", "label_uids", "pharma_row_candidate",
            "page_fact_count", "nn_dinov2", "crop", "thumb", "jon_observation"]
    with open(ATLAS / "objects.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(cols)
        for o in objs:
            pfc = sum(len(facts.get(f, [])) for f in o["panels_covered"].split(";"))
            pr = o["pharma_row_candidate"]
            prs = (f"row {pr['row']} rank {pr['rank']}/{pr['n_in_row']} -> {pr['candidate']}"
                   f"{'' if pr['count_match'] else ' (count mismatch)'}") if pr else ""
            w.writerow([o["object_id"], o["folio"], o["panels_covered"], o["folio_assignment"], o["section"], o["quire"],
                        o["bifolio"], o["hand_davis"], o["scan"], o["x"], o["y"], o["w"], o["h"], o["area_px"],
                        o["drawn_px"], o["paint_frac"], o["text_frac"], o["is_drawing"], o["kind"], o["kind_source"],
                        o["caption"], o["caption_source"], " | ".join(l["text"] for l in o["labels"]),
                        ";".join(l["uid"] for l in o["labels"]), prs, pfc,
                        ";".join(f"{i}:{s}" for i, s in o["nn_dinov2"]),
                        f"crops/{o['object_id']}.png", f"thumbs/{o['object_id']}.jpg", ""])
    # browser data
    scans = B.scan_table()
    pages = []
    for fn, s in sorted(scans.items()):
        dp = WORK / "detect" / (Path(fn).stem + ".json")
        size = json.loads(dp.read_text())["size"] if dp.exists() else None
        secs = sorted({fm[f]["section"] for f in s["folios"] if f in fm})
        pages.append(dict(scan=fn, preview=f"scans/{Path(fn).stem}.jpg", size=size, folios=s["folios"], kinds=s["kinds"],
                          sections=secs, registration={f: dict(passA=reg[f]["passA"], passB=reg[f]["passB"],
                                                                frac=reg[f]["frac_box_centres_in_text"],
                                                                linked=reg[f]["linked"]) for f in s["folios"] if f in reg},
                          objects=[o["object_id"] for o in by_scan.get(fn, [])]))
    keep = ["object_id", "folio", "panels_covered", "folio_assignment", "section", "quire", "hand_davis", "scan", "x",
            "y", "w", "h", "area_px", "is_drawing", "kind", "caption", "labels", "pharma_row_candidate", "nn_dinov2"]
    data = dict(objects=[{k: o[k] for k in keep} for o in objs], pages=pages,
                facts={f: v for f, v in facts.items() if any(f in p["folios"] for p in pages)},
                canned=canned, kinds=B.KINDS)
    js = json.dumps(data, ensure_ascii=False)
    (ATLAS / "atlas_data.json").write_text(js, encoding="utf-8")
    (ATLAS / "atlas_data.js").write_text("window.ATLAS = " + js + ";\n", encoding="utf-8")
    print("objects", len(objs), "labels linked", n_lab_linked, "pharma candidates", len(ph), "canned", len(canned))


def siglip_queries(ids, E):
    import torch
    from transformers import AutoModel, AutoProcessor
    path = B.MODELS / "siglip-base-patch16-224"
    proc = AutoProcessor.from_pretrained(path); model = AutoModel.from_pretrained(path).eval()
    with torch.no_grad():
        inp = proc(text=[f"a drawing of {q}" for q in QUERIES], padding="max_length", return_tensors="pt")
        T = torch.nn.functional.normalize(model.get_text_features(**inp).float(), dim=-1).numpy()
    S = T @ E.T
    return {q: [(ids[j], round(float(S[k, j]), 4)) for j in np.argsort(-S[k])[:40]] for k, q in enumerate(QUERIES)}


if __name__ == "__main__":
    main()
