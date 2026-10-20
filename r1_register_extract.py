"""R1: extract TheVoynich.org register for LEADS diff. Read-only on team files.
Input: data/external/thevoynich-register/research-snapshot.json (CC BY-NC 4.0)
Output: register_extract.txt (status lists + keyword buckets, UTF-8).
Run: uv run python r1_register_extract.py
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "data" / "external" / "thevoynich-register" / "research-snapshot.json"
OUT = ROOT / "register_extract.txt"
BUCKETS = {
    "cipher/substitution": r"cipher|substitution|homophon|nomenclator|verbose|anagram",
    "entropy/statistics": r"entropy|zipf|statistic|entropy|h2|bigram|frequency",
    "scribe/hand/quire": r"scribe|hand|quire|bifol|singulion|binding|folio order",
    "currier/language": r"currier|language a|language b|dialect",
    "labels/plants": r"label|plant|herbal|botan",
    "hartlieb/secreta": r"hartlieb|secreta|women|gynec|medical secret",
    "f57v/ring": r"f57v|period|ring|circular",
    "dating/provenance": r"radiocarbon|carbon|dating|rudolf|kircher|provenance|vellum|ink",
}


def main():
    raw = SRC.read_bytes()
    d = json.loads(raw.decode("utf-8"))
    f = d["findings"]
    lines = [
        f"snapshot_at_utc={d.get('snapshot_at_utc')} date={d.get('snapshot_date')} "
        f"schema={d.get('schema_version')} bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()}",
        f"counts={d.get('counts')} status_counts={d.get('status_counts')}",
        f"finding keys sample: {sorted(f[0])}",
        f"withheld findings fields: {len([w for w in d.get('field_withholdings', []) if w['table']=='findings'])}",
    ]
    def status(x):
        return x.get("status") or x.get("confidence") or "?"
    lines.append(f"status tally (parsed): {dict(Counter(status(x) for x in f))}")
    for want in ("Falsified", "Confirmed"):
        rows = [x for x in f if status(x) == want]
        lines.append(f"\n=== {want} ({len(rows)}) ===")
        for x in rows:
            lines.append(f"- [{x.get('code') or x.get('id')}] {x.get('title') or '(title withheld)'}")
    titled = [x for x in f if x.get("title")]
    lines.append(f"\n=== Keyword buckets over {len(titled)} titled findings ===")
    for name, pat in BUCKETS.items():
        rx = re.compile(pat, re.I)
        hits = [x for x in titled if rx.search(x["title"])]
        lines.append(f"\n-- {name}: {len(hits)} --")
        for x in hits[:40]:
            lines.append(f"  [{status(x)}] [{x.get('code') or x.get('id')}] {x['title']}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
