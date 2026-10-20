"""Per-folio dossier from the VKB: structure, scans, published facts (with agreement/conflict
flags), transliteration loci, and register rows that mention the folio. Read-only.
Usage: python tools/vkb/queries/folio_dossier.py f68r3 [--facts-only] [--max-quote 120]
Flags on page_facts: AGREE = same attribute and value from 2+ sources; DIFFER = one attribute,
2+ distinct values from different sources (often complementary detail, not always a conflict)."""
import os, re, sqlite3, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common import DB


def norm(v):
    return re.sub(r"\s+", " ", (v or "").strip().lower())


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 1
    f = argv[1]
    mq = int(argv[argv.index("--max-quote") + 1]) if "--max-quote" in argv else 120
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cols = [r[1] for r in c.execute("pragma table_info(folios)")]
    row = c.execute("select * from folios where folio=?", (f,)).fetchone()
    if not row:
        print(f"no folio {f!r}; try e.g. f1r, f68r3"); return 1
    if "--facts-only" not in argv:
        print(f"== {f} structure")
        for k, v in zip(cols, row):
            if v not in (None, "") and k != "src":
                print(f"  {k}: {v}")
        print("== scans (panel_images)")
        for p, kind, lab in c.execute("select image_path,kind,canvas_label from panel_images where folio=?", (f,)):
            print(f"  {kind}: {p}" + (f"  [{lab}]" if lab else ""))
        print("== transliteration loci")
        for t, n, tok in c.execute("select translit,count(*),sum(n_tokens) from loci where folio=? group by translit", (f,)):
            print(f"  {t}: {n} loci, {tok} tokens")
    print("== published page facts (page_facts)")
    by = defaultdict(list)
    for a, v, s, q in c.execute("select attribute,value,source,quote from page_facts where folio=?", (f,)):
        by[a].append((v, s, q))
    for a in sorted(by):
        rows = by[a]
        vals = defaultdict(set)
        for v, s, _ in rows:
            vals[norm(v)].add(s)
        srcs = {s for _, s, _ in rows}
        flag = ""
        if any(len(ss) > 1 for ss in vals.values()):
            flag = " AGREE"
        if len(vals) > 1 and len(srcs) > 1:
            flag += " DIFFER"
        print(f"  [{a}]{flag}")
        for v, s, q in rows:
            qs = f'  "{q[:mq]}"' if q and q != v else ""
            print(f"    {v}  <{s}>{qs}")
    if "--facts-only" not in argv:
        pat = re.compile(rf"\b{re.escape(f)}\b", re.I)
        print("== findings and hypotheses mentioning it (workflow/FINDINGS-GRAPH.yaml text)")
        try:
            import yaml
            g = yaml.safe_load(open(os.path.join(os.path.dirname(DB), "..", "..", "workflow", "FINDINGS-GRAPH.yaml"), encoding="utf-8"))
            cids = {i for i, t in c.execute("select claim_id, text from claims") if t and pat.search(t)}
            for sec in ("findings", "hypotheses", "assumptions", "pending"):
                for k, v in (g.get(sec) or {}).items():
                    dump = yaml.safe_dump(v)
                    via = sorted(x for x in cids if re.search(r"\b" + re.escape(x) + r"\b", dump))
                    if pat.search(dump) or via:
                        t = (v.get("title") or v.get("short") or v.get("question") or v.get("statement", "")) if isinstance(v, dict) else ""
                        print(f"  {k}: {str(t)[:110]}" + (f"  [via {', '.join(via)}]" if via else "  [named in graph]"))
        except Exception as e:  # graph unreadable: say so rather than omit silently
            print(f"  (graph not read: {e})")
        print("== register rows mentioning it")
        for tbl, idc, txt in [("claims", "claim_id", "text"), ("learnings", "lid", "belief || ' ' || result"),
                              ("open_questions", "oid", "question")]:
            for i, t in c.execute(f"select {idc}, {txt} from {tbl}"):
                if t and pat.search(t):
                    print(f"  {i}: {t[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
