"""Convert CREMMA Medii Aevi ALTO v4 transcriptions (plain `.xml` variant, fetched by
tools/fetch_cremma.py into data/external/cremma/) into scoreboard sidecars with real lines.

Usage (project root, isolated interpreter, script outside the data folder):
    python -I tools/cremma_to_meta.py data/external/cremma data/controls_realline

Selection:
  - one ALTO file = one page; page id = <ms short id>_<page name> (page name = file stem; for
    stems containing " - " the part after the last " - ", spaces -> "_");
  - TextBlocks whose SegmOnto zone label (OtherTag LABEL resolved through TextBlock TAGREFS;
    ids differ per file so labels are matched, never ids) is exactly "MainZone"; every other
    zone (MarginTextZone, RunningTitleZone, DropCapitalZone, NumberingZone, QuireMarksZone,
    StampZone) is dropped;
  - lines are emitted in TextBlock document order, then TextLine document order. Each
    MainZone TextBlock is a BLOCK-INITIAL (column proxy) boundary, not a paragraph: the
    0-based index of the first emitted line of every block is recorded in the page's
    "block_first" list (extra key; run_v2.load_meta ignores it). MainZone blocks are often
    columns (Arras-861/056r has two 35-line MainZones at x=386 and x=2264), so any
    paragraph-specific claim built on block_first is proxy-only;
  - a line whose tokens are all empty after cleaning is skipped and never starts a block;
    a page left with no line is skipped (printed), so page counts equal run_v2.load_meta's;
  - "n_mainzone_blocks" per page is also recorded.

Token rule (audit amendment 2026-10-17, support-phase1-audit.md item 2): the line's single
String CONTENT is split on whitespace AND on the punctuation delimiters ". : , ;" (each
delimiter is a word boundary, so `facit.aliud` -> `facit`, `aliud`); empty pieces are
dropped. Unmarked line-end word breaks are left as the scribe left them (a line-final
fragment is a token; nothing is joined across physical lines). Nothing else is altered
(abbreviation letters, PUA signs, digits, "¶" stay).
Two sidecar families are written from the same split:
  (a) base-letter (no suffix): each piece -> NFD -> remove combining marks (category Mn)
      -> lowercase;
  (b) mark-preserving sensitivity (suffix `_marks`): each piece -> NFD -> lowercase, marks
      kept in place. The GLYPH UNIT of a `_marks` token is one non-Mn code point followed by
      all Mn code points attached to it (regex `[^\\p{Mn}]\\p{Mn}*`; see glyph_units()); the
      first glyph of a word is therefore base[0] plus its marks, never a detached mark. A
      piece that begins with a combining mark but has a base later is kept and counted
      ("leading_mark_tokens"); a piece made only of combining marks (a detached abbreviation
      sign between spaces) is empty in family (a) and is dropped from BOTH families so they
      stay token-aligned; the count is reported ("marks_only_pieces").
      Scorers must segment `_marks` tokens with glyph_units(), not by code point.
For reporting, the earlier delete-and-join rule (whitespace split, strip trailing ".:,;")
is also computed per line and the number of lines whose token count differs is printed per
manuscript ("changed_lines").

Outputs (in <out_dir>), per family: cremma_<ms>[.meta.json | _marks.meta.json] per manuscript;
cremma_all (all 21), cremma_c15 (the seven 15th-century manuscripts), cremma_prose15
(PalLat373, LaurPlut53.08, LaurPlut53.09); and <name>_relined8 twins of the three pooled
sidecars (same tokens in the same order, re-cut into 8-token lines within each page,
block_first = [0]).
Sidecar keys: name, tokenization, source, family, pages[{id, section, hand, lang, quire,
lines, block_first, n_mainzone_blocks}]; "lang" = "la", "section" = registry Type (text
type), "hand" = manuscript short id, "quire" = None.
Prints one line per sidecar with pages/lines/tokens and a JSON summary to stdout.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "{http://www.loc.gov/standards/alto/ns-v4#}"
DELIM = ".:,;"
SPLIT_RE = re.compile(r"[\s.:,;]+")

SHORT = {"LaurentianusPluteus33.31": "LaurPlut33.31", "LaurentianusPluteus39.34": "LaurPlut39.34",
         "LaurentianusPluteus53.08": "LaurPlut53.08", "LaurentianusPluteus53.09": "LaurPlut53.09"}
C15 = ["LaurPlut39.34", "PalLat373", "LaurPlut53.08", "LaurPlut53.09", "SBB_PK_Hdschr25",
       "BGO-511", "Latin8236"]
PROSE15 = ["PalLat373", "LaurPlut53.08", "LaurPlut53.09"]
RELINE = 8
FAMILIES = ("base", "marks")


def is_mark(c: str) -> bool:
    return unicodedata.category(c) == "Mn"


def glyph_units(token: str) -> list[str]:
    """Segment a `_marks` token into glyph units: one non-Mn code point plus the Mn code
    points that follow it. A leading run of marks (no base) forms a unit of its own."""
    units: list[str] = []
    for c in token:
        if is_mark(c) and units:
            units[-1] += c
        elif is_mark(c):
            units.append(c)
        else:
            units.append(c)
    return units


def clean_base(piece: str) -> str:
    s = unicodedata.normalize("NFD", piece)
    return "".join(c for c in s if not is_mark(c)).lower()


def clean_marks(piece: str) -> str:
    return unicodedata.normalize("NFD", piece).lower()


def split_line(content: str) -> list[str]:
    return [p for p in SPLIT_RE.split(content) if p]


def line_tokens(content: str) -> tuple[list[str], list[str], int]:
    """Returns (base tokens, marks tokens, number of marks-only pieces dropped). A piece
    whose base-letter form is empty (it consists only of combining marks, e.g. a detached
    superscript-letter abbreviation sign written between spaces) is dropped from BOTH
    families so that they stay token-aligned."""
    base, marks, dropped = [], [], 0
    for p in split_line(content):
        b = clean_base(p)
        if not b:
            dropped += 1
            continue
        base.append(b)
        marks.append(clean_marks(p))
    return base, marks, dropped


def old_rule_count(content: str) -> int:
    """Delete-and-join rule (whitespace split, strip trailing delimiters) for the report."""
    return sum(1 for p in content.split() if clean_base(p).rstrip(DELIM))


def page_name(stem: str) -> str:
    if " - " in stem:
        stem = stem.rsplit(" - ", 1)[1]
    return stem.replace(" ", "_")


def parse_page(path: Path, ms: str, section: str) -> tuple[dict, dict, dict]:
    root = ET.parse(path).getroot()
    if not root.tag.startswith(NS):
        raise SystemExit(f"{path}: not ALTO v4 ({root.tag})")
    labels = {o.get("ID"): o.get("LABEL") for o in root.iter(NS + "OtherTag")}
    lines_b: list[list[str]] = []
    lines_m: list[list[str]] = []
    block_first: list[int] = []
    n_main = 0
    stats = dict(changed_lines=0, old_tokens=0, leading_mark_tokens=0, marks_only_pieces=0,
                 lines_seen=0)
    for tb in root.iter(NS + "TextBlock"):
        if labels.get(tb.get("TAGREFS")) != "MainZone":
            continue
        n_main += 1
        start = len(lines_b)
        for tl in tb.iter(NS + "TextLine"):
            strings = list(tl.iter(NS + "String"))
            if len(strings) != 1:
                raise SystemExit(f"{path}: TextLine {tl.get('ID')} has {len(strings)} String elements")
            content = strings[0].get("CONTENT") or ""
            base, marks, dropped = line_tokens(content)
            stats["marks_only_pieces"] += dropped
            stats["lines_seen"] += 1 if content.strip() else 0
            old = old_rule_count(content)
            stats["old_tokens"] += old
            if old != len(base):
                stats["changed_lines"] += 1
            stats["leading_mark_tokens"] += sum(1 for t in marks if is_mark(t[0]))
            if base:
                lines_b.append(base)
                lines_m.append(marks)
        if len(lines_b) > start:
            block_first.append(start)
    common = dict(section=section, hand=ms, lang="la", quire=None, block_first=block_first,
                  n_mainzone_blocks=n_main)
    pid = f"{ms}_{page_name(path.stem)}"
    return (dict(id=pid, **common, lines=lines_b), dict(id=pid, **common, lines=lines_m), stats)


def read_registry(cremma: Path) -> dict[str, dict]:
    reg = {}
    with (cremma / "data-registry.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            reg[row["Folder"].split("/")[-1]] = row
    return reg


def fname(name: str, fam: str) -> str:
    return name if fam == "base" else name + "_marks"


def doc(name: str, fam: str, pages: list[dict], source: str) -> dict:
    fam_note = ("base-letter: NFD, combining marks removed, lowercase" if fam == "base" else
                "mark-preserving: NFD, lowercase, marks kept; glyph unit = non-Mn code point + "
                "following Mn code points (tools/cremma_to_meta.py glyph_units)")
    return dict(name=fname(name, fam), tokenization="latin", family=fam,
                source=source + "; " + fam_note, pages=pages)


def relined(d: dict) -> dict:
    pages = []
    for p in d["pages"]:
        toks = [t for ln in p["lines"] for t in ln]
        lines = [toks[i:i + RELINE] for i in range(0, len(toks), RELINE)]
        pages.append(dict(p, lines=lines, block_first=[0] if lines else []))
    return dict(d, name=d["name"].replace("_marks", "") + "_relined8" + ("_marks" if d["family"] == "marks" else ""),
                source=d["source"] + f"; re-lined {RELINE} tokens/line within each page (relined8 twin)",
                pages=pages)


def write(out: Path, d: dict) -> tuple[int, int, int]:
    (out / f"{d['name']}.meta.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    np_ = len(d["pages"])
    nl = sum(len(p["lines"]) for p in d["pages"])
    nt = sum(len(ln) for p in d["pages"] for ln in p["lines"])
    print(f"{d['name']:34} pages={np_:4} lines={nl:5} tokens={nt:6}")
    return np_, nl, nt


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    cremma, out = Path(argv[1]), Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    reg = read_registry(cremma)
    base_src = ("CREMMA Medii Aevi (HTR-United/CREMMA-Medieval-LAT v0.1.2, tree 9439fe33), plain ALTO "
                "variant, MainZone TextBlocks only, real lines; tools/cremma_to_meta.py: split on "
                "whitespace and on the delimiters . : , ; (word boundaries), block_first = block-initial "
                "line indices (column proxy)")
    per: dict[str, dict[str, dict]] = {f: {} for f in FAMILIES}
    summary = {}
    for folder in sorted(p for p in (cremma / "data").iterdir() if p.is_dir()):
        ms = SHORT.get(folder.name, folder.name)
        row = reg.get(folder.name)
        if row is None:
            raise SystemExit(f"{folder.name} not in data-registry.csv")
        section = row["Type"].strip().rstrip(".")
        files = sorted(f for f in folder.glob("*.xml") if not f.name.endswith(".chocomufin.xml"))
        pages = {f: [] for f in FAMILIES}
        st = dict(changed_lines=0, old_tokens=0, leading_mark_tokens=0, marks_only_pieces=0,
                  lines_seen=0)
        for f in files:
            pb, pm, s = parse_page(f, ms, section)
            for k in s:
                st[k] += s[k]
            if pb["lines"]:
                pages["base"].append(pb)
                pages["marks"].append(pm)
            else:
                print(f"skip page with no transcribed MainZone line: {pb['id']} ({f.name})")
        rec = dict(folder=folder.name, notBefore=row["notBefore"], notAfter=row["notAfter"],
                   script=row["Script"], type=section, content=row["Content"],
                   blocks_per_page=[p["n_mainzone_blocks"] for p in pages["base"]],
                   c15=ms in C15, prose15=ms in PROSE15, **st)
        for fam in FAMILIES:
            d = doc(f"cremma_{ms}", fam, pages[fam], base_src + f"; manuscript {folder.name}")
            per[fam][ms] = d
            np_, nl, nt = write(out, d)
            rec[fam] = dict(pages=np_, lines=nl, tokens=nt)
        summary[ms] = rec
    pooled = {"cremma_all": list(per["base"]), "cremma_c15": C15, "cremma_prose15": PROSE15}
    for name, members in pooled.items():
        missing = [m for m in members if m not in per["base"]]
        if missing:
            raise SystemExit(f"{name}: missing manuscripts {missing}")
        rec = dict(members=members)
        for fam in FAMILIES:
            pages = [p for m in members for p in per[fam][m]["pages"]]
            d = doc(name, fam, pages, base_src + f"; pooled {', '.join(members)} (hand = manuscript id)")
            np_, nl, nt = write(out, d)
            rec[fam] = dict(pages=np_, lines=nl, tokens=nt)
            r = relined(d)
            np_, nl, nt = write(out, r)
            rec[fam + "_relined8"] = dict(name=r["name"], pages=np_, lines=nl, tokens=nt)
        summary[name] = rec
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
