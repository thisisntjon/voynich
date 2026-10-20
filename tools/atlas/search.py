#!/usr/bin/env python
"""Free-text picture search over the atlas (SigLIP image-text similarity; a machine ranking, not an identification).

Usage: <venv_s45>/Scripts/python.exe -I tools/atlas/search.py "root with a face" [-k 20] [--html]
--html writes data/atlas/search_<slug>.html (thumbnails, links into index.html) and prints its path.
"""
import argparse, csv, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "data" / "atlas"
MODEL = ROOT / "data" / "external" / "models" / "siglip-base-patch16-224"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query"); ap.add_argument("-k", type=int, default=20); ap.add_argument("--html", action="store_true")
    a = ap.parse_args()
    import numpy as np, torch
    from transformers import AutoModel, AutoProcessor
    ids = json.loads((ATLAS / "emb_ids.json").read_text())
    E = np.load(ATLAS / "emb_siglip.npy")
    rows = {}
    with open(ATLAS / "objects.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            rows[r["object_id"]] = r
    proc = AutoProcessor.from_pretrained(MODEL); model = AutoModel.from_pretrained(MODEL).eval()
    with torch.no_grad():
        inp = proc(text=[f"a drawing of {a.query}"], padding="max_length", return_tensors="pt")
        t = torch.nn.functional.normalize(model.get_text_features(**inp).float(), dim=-1).numpy()[0]
    s = E @ t
    top = np.argsort(-s)[:a.k]
    for j in top:
        r = rows.get(ids[j], {})
        print(f"{ids[j]}\t{s[j]:.4f}\t{r.get('folio') or r.get('panels_covered')}\t{r.get('kind')}\t{r.get('caption')}")
    if a.html:
        slug = re.sub(r"[^a-z0-9]+", "_", a.query.lower()).strip("_")[:40]
        cards = "".join(f'<a href="index.html#o/{ids[j]}"><img src="thumbs/{ids[j]}.jpg" title="{ids[j]} {s[j]:.3f}"></a>' for j in top)
        p = ATLAS / f"search_{slug}.html"
        p.write_text(f"<!doctype html><meta charset=utf-8><title>Atlas search</title><h3>{a.query} (SigLIP ranking)</h3>{cards}",
                     encoding="utf-8")
        print(p)


if __name__ == "__main__":
    main()
