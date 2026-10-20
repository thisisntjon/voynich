#!/usr/bin/env python
"""Draw the stratified hand-check sample (30 objects across sections, seed 20261019) and write a contact sheet.
Output: data/atlas/work/handcheck_sample.json, data/atlas/work/handcheck_sheet_{1,2}.jpg"""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B
from PIL import Image, ImageDraw
QUOTA = {"P": 5, "B": 5, "H": 4, "Z": 4, "S": 4, "C": 3, "A": 3, "T": 2}
objs = B.objects_list()
rng = random.Random(20261019)
sample = []
for sec, n in QUOTA.items():
    pool = [o for o in objs if o["section"].split("/")[0] == sec]
    sample += rng.sample(pool, min(n, len(pool)))
(B.WORK / "handcheck_sample.json").write_text(json.dumps([o["object_id"] for o in sample]))
for part, chunk in enumerate((sample[:15], sample[15:]), 1):
    cell = 300
    sheet = Image.new("RGB", (cell * 5, (cell + 20) * 3), "white"); d = ImageDraw.Draw(sheet)
    for i, o in enumerate(chunk):
        im = Image.open(B.ATLAS / "crops" / f"{o['object_id']}.png").convert("RGB"); im.thumbnail((cell - 6, cell - 6))
        x, y = (i % 5) * cell, (i // 5) * (cell + 20)
        sheet.paste(im, (x + 3, y + 20)); d.text((x + 3, y + 3), f"{i + 1 + 15 * (part - 1)} {o['object_id']} {o['section']}", fill="black")
    sheet.save(B.WORK / f"handcheck_sheet_{part}.jpg", quality=88)
print([o["object_id"] for o in sample])
