#!/usr/bin/env python3
"""s128 layout count script (frozen; prereg v3 section COUNT LIST).
Reads ONE IVTFF transliteration and writes, per included herbal page, ONLY:
page id, $Q, $B, $H, $L, the token count of each included line in order, and a paragraph-start flag per line.
It writes no word content, no glyphs and no token strings. It applies the v3 page-set and tokenising rules.
Usage (only after D-072 clears, per prereg v3 step d0):
  python -I runs/s128/s128_layout_counts.py data/ZL3b-n.txt runs/s128/s128_layout_counts_ZL3b.tsv
Exit codes: 0 ok; 3 = no <%> paragraph mark on any included herbal line (primary must stop); 2 = usage/hash error."""
import sys, re, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import vparse  # hashed in the stub; PAGE_RE, LINE_RE, VAR_RE, clean

UNITS = {"P0", "P1", "Pb", "Pc", "Pr"}
FOLDOUT = re.compile(r"^f[0-9]+[rv][0-9]+$")
COMMENT = re.compile(r"<![^>]*>")

def tokens(text):
    # v3 tokenising rules: vparse.clean (comments, <->, tags, [a:b], @nnn;->?, braces, apostrophes, ',' and '.' as breaks),
    # then fillers '!' and '%' removed, then any token with '?' or '*' deleted.
    out = []
    for w in vparse.clean(text, strict_spaces=False):
        w = w.replace("!", "").replace("%", "")
        if not w or "?" in w or "*" in w:
            continue
        out.append(w)
    return out

def main(src, dst):
    raw_bytes = Path(src).read_bytes()
    meta, page, pages, order = {}, None, {}, []
    excluded = []
    pct_marks = 0
    for raw in raw_bytes.decode("ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = vparse.PAGE_RE.match(raw)
        if m:
            page = m.group(1); meta = dict(vparse.VAR_RE.findall(m.group(2))); continue
        m = vparse.LINE_RE.match(raw)
        if not m:
            continue
        pg, _n, loc, unit, text = m.groups()
        hm = meta if pg == page else {}
        if hm.get("I") != "H":
            continue
        if FOLDOUT.match(pg):
            if pg not in excluded: excluded.append(pg)
            continue
        if loc == "!":            # locator '!': text not in the MS (IVTFF 6.4 Table 8) -> excluded
            continue
        if unit not in UNITS:
            continue
        t = COMMENT.sub("", text).strip()
        starts = t.startswith("<%>")
        ends = t.endswith("<$>")
        pct_marks += starts
        n = len(tokens(text))
        if pg not in pages:
            pages[pg] = dict(Q=hm.get("Q", "?"), B=hm.get("B", "?"), H=hm.get("H", "?"), L=hm.get("L", "?"), lines=[], prev_end=False)
            order.append(pg)
        P = pages[pg]
        if n == 0:                 # empty line dropped; a pending <$> still applies to the next kept line
            P["prev_end"] = P["prev_end"] or ends
            continue
        first = not P["lines"]
        flag = 1 if (first or starts or P["prev_end"]) else 0
        P["lines"].append((n, flag)); P["prev_end"] = ends
    rows = ["#s128_layout_counts v3", "#source_sha256\t" + hashlib.sha256(raw_bytes).hexdigest(),
            "#para_start_marks_on_included_herbal_lines\t%d" % pct_marks,
            "#excluded_foldout_pages\t" + ",".join(excluded),
            "page\tQ\tB\tH\tL\tline_token_counts\tpara_start_flags"]
    for pg in order:
        P = pages[pg]
        if not P["lines"]:
            continue
        rows.append("\t".join([pg, P["Q"], P["B"], P["H"], P["L"],
                               ",".join(str(n) for n, _ in P["lines"]), ",".join(str(f) for _, f in P["lines"])]))
    Path(dst).write_bytes(("\n".join(rows) + "\n").encode("ascii"))
    print("pages", len(rows) - 5, "para_marks", pct_marks, "excluded_foldouts", len(excluded))
    print("count_list_sha256", hashlib.sha256(Path(dst).read_bytes()).hexdigest())
    return 3 if pct_marks == 0 else 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
