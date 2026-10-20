"""Run read-only SQL on the VKB. Usage: python tools/vkb/query.py "SELECT ..." [--csv]"""
import csv, os, sqlite3, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import DB


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = conn.execute(sys.argv[1])
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    if "--csv" in sys.argv:
        w = csv.writer(sys.stdout); w.writerow(cols); w.writerows(rows)
    else:
        print(" | ".join(cols))
        for r in rows:
            print(" | ".join("" if v is None else str(v) for v in r))
        print(f"({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
