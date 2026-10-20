"""Parse voynichese.com per-token bounding boxes and align them to ZL3b lines.

Data: data/external/word-coordinates/.../voynichese_boxes/<folio>.js (223 folios,
untrusted downloads). Each file is a JSON literal `[vocab, boxes]`:
  vocab[i] = [word, total_freq, page_count, [pages]]
  boxes[k] = [vocab_index, x, y, w, h]   (page pixels, 3-px grid, ~600 px wide)
Boxes are in reading order (matches ZL line order; verified on f1r/f57v).
The files are parsed with json.loads only - the JS is never executed.

Alignment: a folio's boxes are matched to the folio's ZL3b tokens (all units, file
order) with difflib on collapsed forms (cth/ckh/cph/cfh/ch/sh/iin/in/ee -> single
symbols, as in Rozanova & Temerev's reproduce_headlines.py). Matched boxes take the
ZL word; unmatched boxes are attached to the line of their matched neighbours (same
line on both sides) or to the nearer line by y. A line is ALIGNED when
|n_zl - n_box| <= 1 and at least half of its ZL tokens string-matched (the
transliterations differ in detail, e.g. ZL soiin vs voynichese ooiin, so a stricter
rule throws away lines whose box count is exactly right). When n_box == n_zl the ZL
words are assigned positionally to the boxes; `strict` marks lines where at least
n_zl - 1 tokens string-matched.
"""
import json
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOX_DIR = (ROOT / "data" / "external" / "word-coordinates" / "lrozanova-voynich-units-main"
           / "voynich-units-main" / "data" / "voynich-units" / "morphometry_voynichese"
           / "voynichese_boxes")

SUBSTITUTIONS = [("cth", "T"), ("ckh", "K"), ("cph", "P"), ("cfh", "F"),
                 ("ch", "C"), ("sh", "S"), ("iin", "N"), ("in", "I"), ("ee", "E")]


def collapse(tok):
    for old, new in SUBSTITUTIONS:
        tok = tok.replace(old, new)
    return tok


def load_boxes(folio, box_dir=BOX_DIR):
    """Return list of dict(word, x, y, w, h, cx, cy) in file order, or None."""
    p = Path(box_dir) / f"{folio}.js"
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    if not (isinstance(data, list) and len(data) == 2):
        raise ValueError(f"{p}: unexpected top-level shape")
    vocab = [str(item[0]) for item in data[0]]
    out = []
    for entry in data[1]:
        i, x, y, w, h = (int(v) for v in entry[:5])
        out.append(dict(word=vocab[i], x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2))
    return out


def box_folios(box_dir=BOX_DIR):
    return sorted(p.stem for p in Path(box_dir).glob("*.js"))


def align_page(recs, boxes):
    """recs: vparse records of ONE page in file order. boxes: load_boxes output.

    Returns (lines, stats). lines[i] corresponds to recs[i] and is a dict:
      aligned (bool), tokens: list of dict(word, cx, cy, w, h, matched) in x-reading
      order (box order), n_zl, n_box, n_matched.
    stats: dict(n_box, n_matched, n_lines, n_aligned, n_strict).
    """
    zl = [(ri, j, w) for ri, r in enumerate(recs) for j, w in enumerate(r["words"])]
    sm = SequenceMatcher(a=[collapse(b["word"]) for b in boxes],
                         b=[collapse(w) for _, _, w in zl], autojunk=False)
    box_line = [None] * len(boxes)
    box_zl = [None] * len(boxes)
    for a0, b0, n in sm.get_matching_blocks():
        for k in range(n):
            box_line[a0 + k] = zl[b0 + k][0]
            box_zl[a0 + k] = zl[b0 + k]
    n_matched = sum(v is not None for v in box_line)
    # attach unmatched boxes to a line
    med_y = {}
    for ri in range(len(recs)):
        ys = [boxes[k]["cy"] for k in range(len(boxes)) if box_line[k] == ri]
        if ys:
            ys.sort()
            med_y[ri] = ys[len(ys) // 2]
    for k in range(len(boxes)):
        if box_line[k] is not None:
            continue
        prev = next((box_line[i] for i in range(k - 1, -1, -1) if box_line[i] is not None), None)
        nxt = next((box_line[i] for i in range(k + 1, len(boxes)) if box_line[i] is not None), None)
        if prev is None and nxt is None:
            continue
        if prev is None or nxt is None or prev == nxt:
            box_line[k] = prev if prev is not None else nxt
        else:
            cy = boxes[k]["cy"]
            box_line[k] = min((prev, nxt), key=lambda ri: abs(med_y.get(ri, cy) - cy))
    per_line = defaultdict(list)
    for k, ri in enumerate(box_line):
        if ri is not None:
            per_line[ri].append(k)
    lines = []
    n_aligned = n_strict = 0
    for ri, r in enumerate(recs):
        ks = per_line.get(ri, [])
        toks = []
        nm = 0
        for k in ks:
            b = boxes[k]
            m = box_zl[k] is not None
            nm += m
            toks.append(dict(word=box_zl[k][2] if m else b["word"], cx=b["cx"], cy=b["cy"],
                             w=b["w"], h=b["h"], matched=m))
        n_zl = len(r["words"])
        if n_zl == len(ks) and n_zl > 0:
            for t, w in zip(toks, r["words"]):
                t["word"] = w
        ok = n_zl > 0 and abs(n_zl - len(ks)) <= 1 and nm >= max(1, (n_zl + 1) // 2)
        strict = n_zl > 0 and abs(n_zl - len(ks)) <= 1 and nm >= n_zl - 1
        n_aligned += ok
        n_strict += strict
        lines.append(dict(aligned=ok, strict=strict, tokens=toks, n_zl=n_zl, n_box=len(ks),
                          n_matched=nm))
    stats = dict(n_box=len(boxes), n_matched=n_matched, n_lines=len(recs), n_aligned=n_aligned,
                 n_strict=n_strict)
    return lines, stats


def align_all(recs, box_dir=BOX_DIR):
    """Align every page that has a box file. Returns (pages, per_folio_stats).

    pages[folio] = list of (rec, line) pairs in file order (line as in align_page).
    """
    by_page = defaultdict(list)
    for r in recs:
        by_page[r["page"]].append(r)
    pages, stats = {}, {}
    for folio in box_folios(box_dir):
        if folio not in by_page:
            continue
        boxes = load_boxes(folio, box_dir)
        lines, st = align_page(by_page[folio], boxes)
        pages[folio] = list(zip(by_page[folio], lines))
        stats[folio] = st
    return pages, stats


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT))
    import vparse
    recs = vparse.load()
    pages, stats = align_all(recs)
    tb = sum(s["n_box"] for s in stats.values()); tm = sum(s["n_matched"] for s in stats.values())
    tl = sum(s["n_lines"] for s in stats.values()); ta = sum(s["n_aligned"] for s in stats.values())
    ts = sum(s["n_strict"] for s in stats.values())
    print(f"folios {len(stats)}  boxes {tb}  matched {tm} ({100*tm/tb:.1f}%)  "
          f"lines {tl}  aligned {ta} ({100*ta/tl:.1f}%)  strict {ts} ({100*ts/tl:.1f}%)")
    worst = sorted(stats, key=lambda f: stats[f]["n_matched"] / max(stats[f]["n_box"], 1))[:8]
    for f in worst:
        s = stats[f]
        print(f"  {f}: boxes {s['n_box']} matched {s['n_matched']} lines {s['n_lines']} aligned {s['n_aligned']}")
