#!/usr/bin/env python
"""Atlas step 0: kraken blla text-line polygons for every Yale scan (writing mask for object detection).

Reference tool (not a statistical run). Imports tools/segment_scans.kraken_lines unchanged.
Output: data/atlas/work/lines/<scan stem>.json  {file, size, lines:[{poly, x0,y0,x1,y1, yb}]}  (skips existing).
Run: <venv_s45>/Scripts/python.exe -I tools/atlas/text_lines.py
"""
import json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np
from PIL import Image
import segment_scans as ss

PAGES = ROOT / "data" / "external" / "yale_scans" / "pages"
OUT = ROOT / "data" / "atlas" / "work" / "lines"


def main():
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)  # BelowNormal
    except Exception:
        pass
    import subprocess
    while True:  # RAM floor: wait while free RAM < 4 GB (shared machine)
        try:
            free = int(subprocess.run(["powershell", "-NoProfile", "-c",
                        "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"], capture_output=True, text=True,
                        timeout=30).stdout.strip()) / 1024 / 1024
        except Exception:
            free = 99
        if free >= 4.0:
            break
        print(f"waiting: free RAM {free:.1f} GB < 4 GB", flush=True)
        time.sleep(30)
    import torch, kraken
    from kraken.lib import vgsl
    OUT.mkdir(parents=True, exist_ok=True)
    dev = "cuda:0" if torch.cuda.is_available() else "cpu"
    model = vgsl.TorchVGSLModel.load_model(os.path.join(os.path.dirname(kraken.__file__), "blla.mlmodel"))
    files = sorted((p.name for p in PAGES.glob("*.jpg")), reverse=os.environ.get("ATLAS_REVERSE") == "1")
    todo = int(os.environ.get("ATLAS_MAX", "0"))  # kraken blla leaks memory: run in short batches
    n_done = 0
    for i, f in enumerate(files):
        o = OUT / (Path(f).stem + ".json")
        if o.exists():
            continue
        if todo and n_done >= todo:
            break
        n_done += 1
        t = time.time()
        im = Image.open(PAGES / f).convert("RGB")
        lines = ss.kraken_lines(im, model, dev)
        for ln in lines:
            ln.pop("baseline", None)
        tmp = o.with_suffix(".tmp")
        tmp.write_text(json.dumps(dict(file=f, size=list(im.size), segmenter="kraken blla default, " + dev, lines=lines)))
        tmp.replace(o)
        print(f"{i+1}/{len(files)} {f} lines={len(lines)} {time.time()-t:.1f}s", flush=True)


if __name__ == "__main__":
    main()
