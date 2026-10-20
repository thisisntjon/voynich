"""VKB checker (D-070): coverage, contradictions, unverified load-bearing facts.
Usage: python tools/vkb/check.py [db]. Prints FAIL/WARN/INFO lines; exit 1 on any FAIL."""
import os, sqlite3, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import DB, ROOT

REQUIRED = ["folios", "quires", "loci", "tokens", "runs", "claims", "measurements", "findings", "finding_lines",
            "hypotheses", "points", "assumptions", "pending", "learnings", "decisions", "open_questions",
            "corpora", "corpus_stats", "sources", "external_items", "folio_features", "finding_links", "panel_images", "page_facts", "team_files"]


def q(conn, sql, *a):
    return conn.execute(sql, a).fetchall()


def main(path=None):
    conn = sqlite3.connect(f"file:{path or DB}?mode=ro", uri=True)
    have = {r[0] for r in q(conn, "SELECT name FROM sqlite_master WHERE type='table'")}
    fails, warns = [], []
    F = fails.append; W = warns.append
    missing = [t for t in REQUIRED if t not in have]
    if missing:
        F(f"tables missing: {missing}")
    for t in sorted(have & set(REQUIRED)):
        n = q(conn, f"SELECT COUNT(*) FROM {t}")[0][0]
        nsrc = q(conn, f"SELECT COUNT(*) FROM {t} WHERE src IS NULL OR src=''")[0][0]
        print(f"INFO {t}: {n} rows")
        if n == 0:
            F(f"{t}: empty")
        if nsrc:
            F(f"{t}: {nsrc} rows without src")
    if "folios" in have:
        for col in ("quire", "section", "hand_davis"):
            n = q(conn, f"SELECT COUNT(*) FROM folios WHERE {col} IS NULL")[0][0]
            if n:
                F(f"folios with NULL {col}: {n}")
        n = q(conn, "SELECT COUNT(*) FROM folios WHERE image_path IS NULL")[0][0]
        if n: W(f"folios without image_path: {n}")
        if "panel_images" in have:
            n = q(conn, "SELECT COUNT(*) FROM folios f WHERE NOT EXISTS (SELECT 1 FROM panel_images p WHERE p.folio=f.folio)")[0][0]
            if n: F(f"folios with no scan at all (panel_images): {n}")
    if "quires" in have:
        n = q(conn, "SELECT COUNT(*) FROM quires WHERE collation IS NULL")[0][0]
        if n: W(f"quires without collation formula: {n} (gap: Phase 7.4)")
    if {"runs", "claims"} <= have:
        n = q(conn, "SELECT COUNT(*) FROM runs WHERE stub_ok = 0")[0][0]
        if n: W(f"runs whose stub does not verify: {n} -> " + ", ".join(r[0] for r in q(conn, "SELECT run_id FROM runs WHERE stub_ok = 0 LIMIT 15")))
        n = q(conn, "SELECT COUNT(*) FROM runs WHERE stub_mtime IS NOT NULL AND results_ctime IS NOT NULL AND stub_mtime > results_ctime")[0][0]
        if n: W(f"runs whose stub is newer than results creation: {n} (check overwrite/refreeze)")
        n = q(conn, "SELECT COUNT(*) FROM runs r WHERE results IS NOT NULL AND NOT EXISTS (SELECT 1 FROM claims c WHERE c.run_id = r.run_id)")[0][0]
        if n: W(f"runs with results but no claim: {n}")
    if {"claims", "measurements"} <= have:
        tot = q(conn, "SELECT COUNT(*) FROM claims WHERE CAST(substr(claim_id,3) AS INTEGER) >= 300")[0][0]
        got = q(conn, "SELECT COUNT(DISTINCT m.claim_id) FROM measurements m JOIN claims c ON c.claim_id=m.claim_id WHERE CAST(substr(c.claim_id,3) AS INTEGER) >= 300")[0][0]
        share = got / tot if tot else 0
        print(f"INFO claims c-300+ with >= 1 parsed measurement: {got}/{tot} ({share:.0%})")
        if share < 0.6: W("measurement parse coverage below 60%")
    if {"findings", "finding_lines", "claims"} <= have:
        rows = q(conn, "SELECT f.fid, COUNT(*) FROM findings f JOIN finding_lines l ON l.fid=f.fid WHERE f.load_bearing IN (1,'1','true','True') AND l.unverified IN (1,'1','true','True') GROUP BY f.fid")
        for fid, n in rows: W(f"load-bearing {fid} has {n} unverified evidence lines")
        rows = q(conn, "SELECT l.fid, l.claim FROM finding_lines l WHERE l.claim IS NOT NULL AND l.claim <> '' AND NOT EXISTS (SELECT 1 FROM claims c WHERE c.claim_id = l.claim)")
        for fid, c in rows: F(f"{fid} cites missing claim {c}")
    if "measurements" in have:
        # contradiction: same statistic, corpus, translit, segmenter, scope reported with different values by different claims
        rows = q(conn, """SELECT statistic, corpus, translit, segmenter, scope, COUNT(DISTINCT ROUND(value,3)), GROUP_CONCAT(DISTINCT claim_id)
                          FROM measurements WHERE value IS NOT NULL AND corpus IS NOT NULL AND scope IS NOT NULL AND scope <> ''
                          GROUP BY statistic, corpus, translit, segmenter, scope HAVING COUNT(DISTINCT ROUND(value,3)) > 1 AND COUNT(DISTINCT claim_id) > 1""")
        for r in rows[:25]: W(f"same measurement, different values: {r[0]} {r[1]} {r[2]} {r[3]} [{r[4]}] -> {r[5]} values in {r[6]}")
        if len(rows) > 25: W(f"... {len(rows) - 25} more value conflicts")
    if "sources" in have:
        for have_v, n in q(conn, "SELECT have, COUNT(*) FROM sources GROUP BY have"):
            print(f"INFO sources {have_v}: {n}")
        n = q(conn, "SELECT COUNT(*) FROM sources WHERE have='FAKE'")[0][0]
        if n: W(f"sources that are fake downloads: {n}")
        # Phase 8.5: a HAVE row whose full local path is gone means the register is stale (bare basenames are skipped)
        for sid, lp in q(conn, "SELECT source_id, local_path FROM sources WHERE have='HAVE' AND local_path IS NOT NULL"):
            for p in lp.split("; "):
                p = p.strip().rstrip("/")
                if "/" in p and "..." not in p and "*" not in p and not any(os.path.exists(os.path.join(ROOT, b, p)) for b in ("", "data", "data/external")):
                    W(f"source {sid} is HAVE but {p} is not on disk")
    if "external_items" in have:
        n = q(conn, "SELECT COUNT(*) FROM external_items WHERE intake_class='unaudited'")[0][0]
        if n: W(f"external items not yet intake-audited: {n}")
    # Phase 8.1: the VKB must not lag the registers it is derived from (a stale VKB gives wrong answers silently)
    import re as _re
    reg = os.path.join(ROOT, ".inventory", "registers")
    for table, col, fname, pat in (("claims", "claim_id", "CLAIMS.md", r"`c-(\d+)`"), ("learnings", "lid", "LEARNINGS.md", r"^\| L-(\d+) \|"),
                                   ("decisions", "did", "DECISIONS.md", r"^\| D-(\d+) \|"), ("open_questions", "oid", "OPEN.md", r"^\| O-(\d+) \|")):
        if table not in have:
            continue
        try:
            txt = open(os.path.join(reg, fname), encoding="utf-8").read()
        except OSError:
            continue
        reg_ids = {int(x) for x in _re.findall(pat, txt, _re.M)}
        db_ids = {int(m.group(1)) for (v,) in q(conn, f"SELECT {col} FROM {table}") for m in [_re.search(r"(\d+)", str(v))] if m}
        missing = sorted(reg_ids - db_ids)
        if missing:
            F(f"VKB lags {fname}: {len(missing)} ids not in table {table} (e.g. {missing[-3:]}); rebuild with python tools/vkb/build.py")
    for w in warns: print("WARN", w)
    for f in fails: print("FAIL", f)
    print("VKB CHECK:", "FAIL" if fails else "PASS", f"({len(fails)} fail, {len(warns)} warn)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
