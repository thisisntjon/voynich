"""Check every pre-registration stub (*.prereg, *.prereg.sha256) against the files in this repository.

A stub lists `sha256  path` lines for the files frozen before a run. Each line gets one status:

  OK                 the file is here with that sha256.
  AMENDED            an earlier line for a file the same stub lists again; the last line is binding (AGENTS.md).
  RESTORE-FIRST      an s45 page or sidecar whose text is put back by tools/restore_s45_text.py (after
                     tools/fetch_data.py); run that, then check again.
  WITHHELD           the file is not published (WITHHELD.tsv gives the reason: blind-study material, team
                     communication, third-party text).
  EDITED-AFTER-PIN   the file was edited after this stub pinned it, and the pinned bytes are kept beside it as
                     <name>.orig-<sha prefix><ext> (the tree's own convention), which matches.
  REWRITTEN          the published copy had local paths rewritten; MANIFEST.tsv shows its source sha256 matches.
  OUTSIDE            the stub names a file outside this repository (an absolute path on the team's machines,
                     shown redacted where it was private); it cannot be checked here.
  MISMATCH           none of the above: an unexplained difference.
  MISSING            not here and not listed as withheld.

Usage (from the repository root): python tools/verify_stubs.py [--all]   (--all prints every line, not only problems)
Exit status 1 if any binding line is MISMATCH or MISSING.
"""
import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINE = re.compile(r"^([0-9a-f]{64})\s+\*?(\S+)")
RESTORABLE = re.compile(r"^runs/s45/(pages/[^/]+\.json|ink_ZL3b\.meta\.json|ink_lines_ZL3b\.meta\.json)$")
SKIP = {".git", ".venv", "__pycache__"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def table(name, key, val):
    p = ROOT / name
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return {r[key]: r[val] for r in csv.DictReader(f, delimiter="\t")}


def resolve(stub: Path, name: str) -> str:
    """The repo-relative path a stub line names (beside the stub first, then from the root)."""
    name = name.replace("\\", "/")
    while name.startswith("./"):
        name = name[2:]
    for cand in (stub.parent / name, ROOT / name):
        try:
            rel = cand.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            continue
        if cand.exists() or rel in withheld or rel in source_sha:
            return rel
    return name


def orig_match(rel: str, want: str) -> bool:
    p = ROOT / rel
    for o in p.parent.glob(f"{p.stem}.orig-*{p.suffix}"):
        if want.startswith(o.name[len(p.stem) + 6:].split(".")[0]) and sha(o) == want:
            return True
    return False


def status(rel: str, want: str) -> str:
    if rel.startswith(("/", "<")) or re.match(r"^[A-Za-z]:", rel):
        return "OUTSIDE"
    p = ROOT / rel
    if p.is_file():
        if sha(p) == want:
            return "OK"
        if RESTORABLE.match(rel):
            return "RESTORE-FIRST"
        if orig_match(rel, want):
            return "EDITED-AFTER-PIN"
        if source_sha.get(rel) == want:
            return "REWRITTEN"
        return "MISMATCH"
    if RESTORABLE.match(rel):
        return "RESTORE-FIRST"
    if rel in withheld:
        return "WITHHELD"
    return "MISSING"


withheld = table("WITHHELD.tsv", "path", "reason")
source_sha = table("MANIFEST.tsv", "path", "source_sha256")


def main():
    show_all = "--all" in sys.argv
    counts, bad = Counter(), 0
    stubs = sorted(p for p in list(ROOT.rglob("*.prereg.sha256")) + list(ROOT.rglob("*.prereg"))
                   if not SKIP & set(p.relative_to(ROOT).parts))
    for st in stubs:
        rows = []
        for line in st.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.lstrip().startswith("#"):
                continue
            m = LINE.match(line.strip())
            if m:
                rows.append((m.group(1), resolve(st, m.group(2))))
        last = {rel: i for i, (_, rel) in enumerate(rows)}
        for i, (want, rel) in enumerate(rows):
            s = "AMENDED" if last[rel] != i else status(rel, want)
            counts[s] += 1
            if s in ("MISMATCH", "MISSING"):
                bad += 1
            if show_all or s not in ("OK", "AMENDED"):
                extra = f"  ({withheld[rel]})" if s == "WITHHELD" else ""
                print(f"{s:16} {st.relative_to(ROOT).as_posix()} -> {rel}{extra}")
    print(f"{len(stubs)} stubs, {sum(counts.values())} lines: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"{bad} unexplained (MISMATCH or MISSING)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
