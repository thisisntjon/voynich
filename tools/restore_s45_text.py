"""Put the transliteration text back into the s45 page files, after tools/fetch_data.py.

The published runs/s45/pages/<page>.json files keep our ink geometry and the line alignment. Their two
text fields, reseg_lines and relined_lines, are the ZL transliteration re-cut at the ink gaps, so they
were removed before publication, as were the two sidecars built from them (runs/s45/ink_ZL3b.meta.json
and runs/s45/ink_lines_ZL3b.meta.json). This script recomputes all of them with the functions
tools/segment_scans.py used, from the fetched data/ZL3b-n.txt. It then checks every rebuilt file
against the sha256 of the file our runs used, so the pre-registration stubs that pin them verify again.

Usage (from the repository root): python tools/restore_s45_text.py [--root <repo>] [--check-only]
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ARGS = sys.argv[1:]
ROOT = Path(ARGS[ARGS.index("--root") + 1]).resolve() if "--root" in ARGS else Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]

# sha256 of the two sidecars our runs read (they are not in MANIFEST.tsv because they are not published).
SIDECARS = {
    "ink_ZL3b": "3f5afe9dc8faa25fbb1373cce89da768b3285bd890fdf30a413f9b7014cc68af",
    "ink_lines_ZL3b": "ecd023ba5a866a9a28706d14ed7b845d8b33eac021c68c22ae4eeb7eb2840703",
}
SIDECAR_SOURCE = "tools/segment_scans.py (kraken blla on Yale IIIF scans + data/ZL3b-n.txt)"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rebuild(page: dict, zpage: dict, ss) -> dict:
    """The page with reseg_lines and relined_lines recomputed, in the order process_page wrote them."""
    loci, det = zpage["loci"], page["lines"]
    reseg, relined = [], []
    for row in page["alignment"]:
        if row["op"] == "miss":
            for j in row["loci"]:
                reseg.append(dict(tokens=list(loci[j]["words"]), src="translit", conf=0.0))
                relined.append(dict(tokens=list(loci[j]["words"]), src="translit"))
            continue
        words_all = [w for j in row["loci"] for w in loci[j]["words"]]
        ink = [t for i in row["det"] for t in det[i]["tokens"]]
        new, _nm, _ns, _nd, conf, _eq = ss.resegment_line(ink, words_all)
        counts = [len(det[i]["tokens"]) for i in row["det"]]
        reseg.extend(ss._distribute(new, counts, src="ink", conf=conf))
        relined.extend(ss._distribute(words_all, counts, src="ink"))
    return dict(page, reseg_lines=reseg, relined_lines=relined)


def main():
    if not (ROOT / "data" / "ZL3b-n.txt").exists():
        sys.exit("data/ZL3b-n.txt is missing: run python tools/fetch_data.py first")
    import segment_scans as ss
    zmap = {z["id"]: z for z in ss.zl_pages()}
    expected = {}
    if (ROOT / "MANIFEST.tsv").exists():
        with open(ROOT / "MANIFEST.tsv", encoding="utf-8") as f:
            expected = {r["path"]: r["source_sha256"] for r in csv.DictReader(f, delimiter="\t")}
    pages_dir = ROOT / "runs" / "s45" / "pages"
    order = [p["id"] for p in json.loads((ROOT / "runs" / "s45" / "segment_summary.json").read_text(encoding="utf-8"))["pages"]]
    bad, reseg, relined = 0, [], []
    for pid in order:
        path = pages_dir / f"{pid}.json"
        page = json.loads(path.read_text(encoding="utf-8"))
        page = {k: v for k, v in page.items() if k not in ("reseg_lines", "relined_lines")}
        full = rebuild(page, zmap[pid], ss)
        data = json.dumps(full).encode("utf-8")
        rel = path.relative_to(ROOT).as_posix()
        if expected.get(rel) and sha(data) != expected[rel]:
            bad += 1
            print(f"MISMATCH {rel}")
        elif "--check-only" not in ARGS:
            path.write_bytes(data)
        z = zmap[pid]
        meta = dict(id=pid, section=z["section"], hand=z["hand"], lang=z["lang"], quire=z["quire"])
        reseg.append(dict(meta, lines=[[t for t in ln["tokens"] if "?" not in t] for ln in full["reseg_lines"]]))
        relined.append(dict(meta, lines=[[t for t in ln["tokens"] if "?" not in t] for ln in full["relined_lines"]]))
    for name, pages in (("ink_ZL3b", reseg), ("ink_lines_ZL3b", relined)):
        side = dict(name=name, source=SIDECAR_SOURCE, pages=[dict(p, lines=[ln for ln in p["lines"] if ln]) for p in pages])
        side["pages"] = [p for p in side["pages"] if p["lines"]]
        data = json.dumps(side, indent=1).replace("\n", "\r\n").encode("utf-8")  # our runs wrote it in Windows text mode
        if sha(data) != SIDECARS[name]:
            bad += 1
            print(f"MISMATCH runs/s45/{name}.meta.json")
        elif "--check-only" not in ARGS:
            (ROOT / "runs" / "s45" / f"{name}.meta.json").write_bytes(data)
    print(f"{len(order)} pages and 2 sidecars rebuilt; {bad} differ from the files our runs used")
    print("These files now hold the transliteration: do not commit them (undo with: git checkout -- runs/s45/pages).")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
