#!/usr/bin/env python
"""Voynich picture atlas builder (reference tool: no pre-registration, no statistics, no CALL lines).

Stages (each resumable; run in order):
  detect   objects per scan / per known panel (tools/atlas/detect.py)       -> data/atlas/work/detect/*.json
  crops    crop PNG + thumbnail per object, scan previews                    -> data/atlas/crops, thumbs, scans
  caption  qwen2.5vl:7b (local ollama) kind + one-line caption per object   -> data/atlas/work/captions.jsonl
  embed    DINOv2-base CLS and SigLIP-base image embeddings (GPU)           -> data/atlas/emb_*.npy
  assemble objects.tsv, data/*.js for the browser, nearest neighbours, links (tools/atlas/assemble.py)

Run: <venv_s45>/Scripts/python.exe -I tools/atlas/build.py --stage detect|crops|caption|embed|assemble|all
"""
import argparse, json, sqlite3, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "atlas"))
sys.path.insert(0, str(ROOT / "tools" / "vkb"))
import numpy as np
from PIL import Image

PAGES = ROOT / "data" / "external" / "yale_scans" / "pages"
ATLAS = ROOT / "data" / "atlas"
WORK = ATLAS / "work"
MODELS = ROOT / "data" / "external" / "models"
GAP_H, GAP_OTHER = 0.05, 0.008
INK_REL_FIG = 0.92
CROP_MAX, THUMB_MAX, SCAN_PREVIEW_H, MARGIN = 900, 180, 1400, 0.04


def free_ram_gb():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-c",
                              "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return int(out) / 1024 / 1024
    except Exception:
        return 99.0


def ram_guard(max_wait_s=2400):
    """Shared machine: keep >= 4 GB RAM free. Wait (up to max_wait_s) while it is lower, then stop."""
    t0 = time.time()
    while True:
        g = free_ram_gb()
        if g >= 4.0:
            return
        if time.time() - t0 > max_wait_s:
            print(f"STOP: free RAM {g:.1f} GB < 4 GB for {max_wait_s} s", flush=True)
            sys.exit(3)
        print(f"waiting: free RAM {g:.1f} GB < 4 GB", flush=True)
        time.sleep(30)


def low_priority():
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def vkb():
    from common import DB
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def scan_table():
    """scan file -> dict(folios=[...], kinds=[...], sections=[...], panels=[(folio,x0,x1)] or None)"""
    import plant_regions as pr
    con = vkb()
    rows = con.execute("SELECT p.folio, p.image_path, p.kind, f.section FROM panel_images p "
                       "LEFT JOIN folios f ON f.folio = p.folio").fetchall()
    scans = {}
    for folio, ip, kind, sec in rows:
        fn = Path(ip).name
        d = scans.setdefault(fn, dict(file=fn, folios=[], kinds=[], sections=[], panels=None))
        if folio not in d["folios"]:
            d["folios"].append(folio); d["kinds"].append(kind); d["sections"].append(sec or "")
    for fn, pl in pr.PANELS.items():
        if fn in scans and len(pl) > 1:
            scans[fn]["panels"] = [(p[0], p[1], p[2]) for p in pl]
    for fn in sorted(p.name for p in PAGES.glob("*.jpg")):
        scans.setdefault(fn, dict(file=fn, folios=[], kinds=[], sections=[], panels=None))
    return scans


def folio_meta():
    con = vkb()
    cols = ["folio", "section", "quire", "bifolio", "hand_davis", "illus_type", "currier_lang"]
    return {r[0]: dict(zip(cols, r)) for r in con.execute(f"SELECT {', '.join(cols)} FROM folios")}


# ------------------------------------------------------------------------------------------------ detect
def stage_detect(args):
    import detect as D
    out = WORK / "detect"; out.mkdir(parents=True, exist_ok=True)
    ov = WORK / "overview"; ov.mkdir(parents=True, exist_ok=True)
    scans = scan_table(); fm = folio_meta()
    only = set(args.only.split(",")) if args.only else None
    for i, (fn, s) in enumerate(sorted(scans.items())):
        if only and fn not in only:
            continue
        o = out / (Path(fn).stem + ".json")
        if o.exists() and not args.force:
            continue
        if i % 10 == 0:
            ram_guard()
        lp = WORK / "lines" / (Path(fn).stem + ".json")
        if not lp.exists():
            print("no lines yet", fn); continue
        lines = json.loads(lp.read_text())["lines"]
        units = [(None, None)] if not s["panels"] else [((p[1], p[2]), p[0]) for p in s["panels"]]
        res = dict(file=fn, units=[])
        for xr, pfolio in units:
            secs = [fm.get(pfolio, {}).get("section")] if pfolio else s["sections"]
            herbal = bool(secs) and all(x == "H" for x in secs)
            gap = GAP_H if herbal else GAP_OTHER
            circ = any(x in ('C', 'Z', 'A') for x in secs)
            figs = any(x in ("B", "Z", "C", "A") for x in secs)  # faint pen figures: looser ink threshold, stacked merge
            r, dbg = D.detect(fn, lines=lines, debug=True, gap=gap, xr=xr, herbal=herbal, circles=circ,
                              ink_rel=INK_REL_FIG if figs else None, stack=figs)
            r["panel_folio"] = pfolio; r["xr"] = xr; r["gap"] = gap
            res["units"].append(r)
            dbg.thumbnail((900, 900)); dbg.convert("RGB").save(ov / f"{Path(fn).stem}{'_' + pfolio if pfolio else ''}.jpg", quality=80)
        res["size"] = res["units"][0]["size"]
        o.write_text(json.dumps(res))
        print(i, fn, [len(u["objects"]) for u in res["units"]], flush=True)


# ------------------------------------------------------------------------------------------------ objects list
def objects_list():
    scans = scan_table(); fm = folio_meta()
    objs = []
    for fn in sorted(scans):
        p = WORK / "detect" / (Path(fn).stem + ".json")
        if not p.exists():
            continue
        d = json.loads(p.read_text()); s = scans[fn]
        k = 0
        for u in d["units"]:
            for ob in u["objects"]:
                x, y, w, h = ob["bbox"]
                if u["panel_folio"]:
                    folio, covers, how = u["panel_folio"], u["panel_folio"], "panel x-range (tools/plant_regions.PANELS)"
                elif len(s["folios"]) == 1:
                    folio, covers, how = s["folios"][0], s["folios"][0], s["kinds"][0]
                else:
                    folio, covers, how = "", ";".join(s["folios"]), "scan covers several panels; not split"
                secs = sorted({fm[f]["section"] for f in covers.split(";") if f in fm})
                oid = f"s{Path(fn).stem.split('_')[0]}-{k:02d}"
                k += 1
                objs.append(dict(object_id=oid, scan=fn, folio=folio, panels_covered=covers, folio_assignment=how,
                                 section="/".join(secs), x=x, y=y, w=w, h=h, area_px=w * h,
                                 drawn_px=ob["draw_px_full"], paint_frac=ob["paint_frac"], text_frac=ob["text_frac"]))
    return objs


# ------------------------------------------------------------------------------------------------ crops
def stage_crops(args):
    for d in ("crops", "thumbs", "scans"):
        (ATLAS / d).mkdir(parents=True, exist_ok=True)
    objs = objects_list()
    by_scan = {}
    for o in objs:
        by_scan.setdefault(o["scan"], []).append(o)
    for fn in sorted({p.name for p in PAGES.glob("*.jpg")}):
        prev = ATLAS / "scans" / (Path(fn).stem + ".jpg")
        need = [o for o in by_scan.get(fn, []) if args.force or not (ATLAS / "crops" / f"{o['object_id']}.png").exists()]
        if prev.exists() and not need:
            continue
        im = Image.open(PAGES / fn).convert("RGB")
        W, H = im.size
        if not prev.exists():
            pv = im.copy(); pv.thumbnail((10000, SCAN_PREVIEW_H)); pv.save(prev, quality=82)
        for o in need:
            m = int(MARGIN * max(o["w"], o["h"]))
            box = (max(0, o["x"] - m), max(0, o["y"] - m), min(W, o["x"] + o["w"] + m), min(H, o["y"] + o["h"] + m))
            c = im.crop(box); c.thumbnail((CROP_MAX, CROP_MAX)); c.save(ATLAS / "crops" / f"{o['object_id']}.png")
            c.thumbnail((THUMB_MAX, THUMB_MAX)); c.save(ATLAS / "thumbs" / f"{o['object_id']}.jpg", quality=85)
        print(fn, len(need), flush=True)


# ------------------------------------------------------------------------------------------------ caption
KINDS = ["plant", "root", "leaf group", "flower", "jar", "human figure", "pool/tub", "pipe/tube", "star", "sun/moon",
         "rosette", "animal", "cosmological circle", "other"]
PROMPT = ("This is a cropped region from a page of a 15th-century illustrated manuscript. "
          "Describe only what is drawn. Answer in JSON with keys: "
          "\"is_drawing\" (false if the crop shows mainly handwriting, a stain, blank parchment or the page edge; true otherwise), "
          "\"kind\" (exactly one of: " + ", ".join(KINDS) + "), "
          "\"caption\" (one plain visual description of the drawing, at most 20 words; do not guess names or identities).")


SECTION_HINT = {"H": "herbal (plant drawings)", "P": "pharmaceutical (jars and plant parts)",
                "B": "biological (bathing women, pools and tubes)", "S": "stars (text with small stars in the margin)",
                "C": "cosmological (circular diagrams)", "Z": "zodiac (circles of small human figures)",
                "A": "astronomical (sun, moon and star diagrams)", "T": "text-only"}


def stage_caption(args):
    import io, ollama
    outp = WORK / "captions.jsonl"
    done = set()
    if outp.exists() and not args.force:
        for ln in outp.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(ln)["object_id"])
            except Exception:
                pass
    objs = [o for o in objects_list() if o["object_id"] not in done]
    if args.only:
        keep = set(args.only.split(","))
        objs = [o for o in objs if o["object_id"] in keep]
    if args.limit:
        objs = objs[:args.limit]
    print("to caption", len(objs), flush=True)
    t0 = time.time()
    with open(outp, "a", encoding="utf-8") as fh:
        for i, o in enumerate(objs):
            if i % 50 == 0:
                ram_guard()
            c = Image.open(ATLAS / "crops" / f"{o['object_id']}.png").convert("RGB")
            c.thumbnail((640, 640))
            if min(c.size) < 336:  # tiny crops (stars, small figures): upscale so the model sees strokes
                f = 336 / min(c.size)
                c = c.resize((min(1000, int(c.size[0] * f)), min(1000, int(c.size[1] * f))), Image.LANCZOS)
            b = io.BytesIO(); c.save(b, "JPEG", quality=90)
            ctx = SECTION_HINT.get((o["section"] or "").split("/")[0], "")
            prompt = PROMPT + (f" Context: the page belongs to the manuscript's {ctx} section." if ctx else "")
            rec = dict(object_id=o["object_id"], source="qwen2.5vl:7b (ollama, temperature 0)")
            try:
                r = ollama.chat(model="qwen2.5vl:7b", format="json", options={"temperature": 0, "num_predict": 160},
                                messages=[{"role": "user", "content": prompt, "images": [b.getvalue()]}])
                txt = r["message"]["content"]
                j = json.loads(txt)
                kind = str(j.get("kind", "other")).strip().lower()
                if kind not in KINDS:
                    kind = next((k for k in KINDS if k in kind or kind in k), "other")
                isd = j.get("is_drawing", True)
                if isinstance(isd, str):
                    isd = isd.strip().lower() not in ("false", "no", "0")
                rec.update(kind=kind, is_drawing=bool(isd),
                           caption=str(j.get("caption", "")).replace("\t", " ").replace("\n", " ")[:300], raw=txt[:500])
            except Exception as e:
                rec.update(kind="", is_drawing=None, caption="", error=repr(e)[:200])
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            if i % 25 == 0:
                print(i, o["object_id"], rec.get("kind"), rec.get("caption", "")[:80], f"{time.time() - t0:.0f}s", flush=True)


# ------------------------------------------------------------------------------------------------ embed
def square(img, size):
    arr = np.asarray(img)
    edge = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]])
    bg = tuple(int(v) for v in np.median(edge, 0))
    s = max(img.size)
    c = Image.new("RGB", (s, s), bg); c.paste(img, ((s - img.size[0]) // 2, (s - img.size[1]) // 2))
    return c.resize((size, size), Image.BICUBIC)


def stage_embed(args):
    import torch
    from transformers import AutoImageProcessor, AutoModel, AutoProcessor
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    objs = objects_list()
    ids = [o["object_id"] for o in objs]
    imgs = [square(Image.open(ATLAS / "crops" / f"{i}.png").convert("RGB"), 224) for i in ids]
    for name, path in (("dinov2", MODELS / "dinov2-base"), ("siglip", MODELS / "siglip-base-patch16-224")):
        if name == "dinov2":
            proc = AutoImageProcessor.from_pretrained(path)
        else:
            proc = AutoImageProcessor.from_pretrained(path)
        model = AutoModel.from_pretrained(path).to(dev).eval()
        vecs = []
        for b in range(0, len(imgs), 32):
            batch = imgs[b:b + 32]
            views = []
            for flip in (False, True):
                bb = [im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im for im in batch]
                with torch.no_grad():
                    if name == "dinov2":
                        inp = proc(images=bb, return_tensors="pt", do_center_crop=False,
                                   size={"height": 224, "width": 224}).to(dev)
                        v = model(**inp).last_hidden_state[:, 0]
                    else:
                        inp = proc(images=bb, return_tensors="pt").to(dev)
                        v = model.get_image_features(**inp)
                views.append(torch.nn.functional.normalize(v.float(), dim=-1))
            v = torch.nn.functional.normalize(sum(views), dim=-1)
            vecs.append(v.cpu().numpy())
        arr = np.concatenate(vecs).astype(np.float32)
        np.save(ATLAS / f"emb_{name}.npy", arr)
        print(name, arr.shape, dev, flush=True)
        del model
        if dev == "cuda":
            torch.cuda.empty_cache()
    (ATLAS / "emb_ids.json").write_text(json.dumps(ids))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    low_priority()
    ram_guard()
    stages = ["detect", "crops", "caption", "embed", "assemble"] if a.stage == "all" else a.stage.split(",")
    for st in stages:
        if st == "assemble":
            import assemble
            assemble.main()
        else:
            globals()["stage_" + st](a)
