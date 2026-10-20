#!/usr/bin/env python3
"""s128 layout count script v2 (frozen; prereg v4 section COUNT LIST). Replaces runs/s128/s128_layout_counts.py (kept unchanged).
Reads ONE IVTFF transliteration and writes, per herbal page with at least one kept line, ONLY:
page id, $Q, $B, $H, $L, the token count of each kept line in order, and a paragraph-start flag per kept line.
It writes no word content, no glyphs and no token strings.
Before opening the data file for parsing it checks, against the stub, the sha256 of (1) this script, (2) vparse.py, (3) the data file;
any missing entry or mismatch -> exit 2, nothing written, vparse not imported.
Usage (only after D-072 clears, prereg v4 step d0), from the project root:
  python -I runs/s128/s128_layout_counts_v2.py runs/s128/s128_name_slot_prediction_v4.prereg.sha256 data/ZL3b-n.txt runs/s128/s128_layout_counts_ZL3b.tsv
Exit codes: 0 ok; 2 usage or hash error; 3 no <%> paragraph mark on any included herbal line (primary must stop)."""
import sys, re, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = "runs/s128/s128_layout_counts_v2.py"
UNITS = {"P0", "P1", "Pb", "Pc", "Pr"}
FOLDOUT = re.compile(r"^f[0-9]+[rv][0-9]+$")
COMMENT = re.compile(r"<![^>]*>")

def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()

def read_stub(stub):
    d = {}
    for ln in (ROOT / stub).read_text(encoding="utf-8").replace("\r", "").split("\n"):
        if ln and not ln.startswith("#") and "  " in ln:
            h, p = ln.split("  ", 1); d[p] = h
    return d

def check(stub, data):
    d = read_stub(stub); bad = []
    for p in (SELF, "vparse.py", data):
        if p not in d: bad.append(p + " NOT_IN_STUB")
        elif sha(p) != d[p]: bad.append(p + " HASH_MISMATCH")
    return bad

def main(stub, data, dst):
    bad = check(stub, data)
    if bad:
        for b in bad: print("HASH_CHECK_FAIL", b)
        return 2
    print("HASH_CHECK_OK", SELF, "vparse.py", data)
    sys.path.insert(0, str(ROOT))
    import vparse  # imported only after its hash passed

    def tokens(text):
        out = []
        for w in vparse.clean(text, strict_spaces=False):
            w = w.replace("!", "").replace("%", "")
            if not w or "?" in w or "*" in w: continue
            out.append(w)
        return out

    raw_bytes = (ROOT / data).read_bytes()
    meta, page, pages, order, excluded, herbal_seen = {}, None, {}, [], [], []
    pct_marks = 0
    for raw in raw_bytes.decode("ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip(): continue
        m = vparse.PAGE_RE.match(raw)
        if m:
            page = m.group(1); meta = dict(vparse.VAR_RE.findall(m.group(2)))
            if meta.get("I") == "H":
                if FOLDOUT.match(page):
                    if page not in excluded: excluded.append(page)
                elif page not in herbal_seen: herbal_seen.append(page)
            continue
        m = vparse.LINE_RE.match(raw)
        if not m: continue
        pg, _n, loc, unit, text = m.groups()
        hm = meta if pg == page else {}
        if hm.get("I") != "H": continue
        if FOLDOUT.match(pg):
            if pg not in excluded: excluded.append(pg)
            continue
        if pg not in herbal_seen: herbal_seen.append(pg)
        if loc == "!": continue            # IVTFF 6.4 Table 8: text not in the MS
        if unit not in UNITS: continue
        t = COMMENT.sub("", text).strip()
        starts, ends = t.startswith("<%>"), t.endswith("<$>")
        pct_marks += starts
        n = len(tokens(text))
        if pg not in pages:
            pages[pg] = dict(Q=hm.get("Q", "?"), B=hm.get("B", "?"), H=hm.get("H", "?"), L=hm.get("L", "?"),
                             lines=[], pend_end=False, pend_start=False)
            order.append(pg)
        P = pages[pg]
        if n == 0:                         # empty line dropped; a pending <%> or <$> carries to the next kept line
            P["pend_end"] = P["pend_end"] or ends
            P["pend_start"] = P["pend_start"] or starts
            continue
        flag = 1 if (not P["lines"] or starts or P["pend_start"] or P["pend_end"]) else 0
        P["lines"].append((n, flag)); P["pend_end"] = ends; P["pend_start"] = False
    kept = [pg for pg in order if pages[pg]["lines"]]
    nokept = [pg for pg in herbal_seen if pg not in kept]
    rows = ["#s128_layout_counts v2 (prereg v4)", "#source_path\t" + data,
            "#source_sha256\t" + hashlib.sha256(raw_bytes).hexdigest(),
            "#para_start_marks_on_included_herbal_lines\t%d" % pct_marks,
            "#excluded_foldout_pages\t%d\t%s" % (len(excluded), ",".join(excluded)),
            "#herbal_pages_no_kept_line\t%d\t%s" % (len(nokept), ",".join(nokept)),
            "page\tQ\tB\tH\tL\tline_token_counts\tpara_start_flags"]
    for pg in kept:
        P = pages[pg]
        rows.append("\t".join([pg, P["Q"], P["B"], P["H"], P["L"],
                               ",".join(str(n) for n, _ in P["lines"]), ",".join(str(f) for _, f in P["lines"])]))
    out = ROOT / dst
    out.write_bytes(("\n".join(rows) + "\n").encode("ascii"))
    print("pages_kept", len(kept), "pages_no_kept_line", len(nokept), "para_marks", pct_marks, "excluded_foldouts", len(excluded))
    print("count_list_sha256", hashlib.sha256(out.read_bytes()).hexdigest())
    return 3 if pct_marks == 0 else 0

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
