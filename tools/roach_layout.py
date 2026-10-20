"""Rebuild the folder layout roach's replication scripts expect, so runs/roach-r*/r*.py can be rerun.

roach (the team's second machine) ran its code-independent replications from one root folder holding r1 ... r15
side by side and the inputs under dl_* folders (dl_ZL/ZL3b-n.txt, r11/dl_PG7000/pg7000.txt, dl_CREMMA/data/...).
Here those runs live in runs/roach-rN/. This script builds that root at roach-root/ (gitignored): it copies each
runs/roach-rN/ to roach-root/rN/, then places every input that a roach stub (*.prereg.sha256) or MANIFEST.sha256
lists, checked against the sha256 recorded there:

  dl_ZL, dl_IT, dl_RF   copied from the files tools/fetch_data.py downloads (run that first);
  dl_PG<n>, dl_DANTE    downloaded from Project Gutenberg (public domain in the USA);
  dl_WLC                downloaded from openscriptures/morphhb (Westminster Leningrad Codex, CC BY 4.0);
  dl_CREMMA             copied from data/external/cremma (run tools/fetch_cremma.py first, see its docstring).

A file whose sha256 differs from the recorded one is kept but reported: the source may have been revised since
2026-10, and a run on it may not reproduce exactly. Then run, for example:
  cd roach-root/r12 && python -I r12.py real .. ../out-r12      (each rN/README.md gives the exact command)

Usage (from the repository root): python tools/roach_layout.py [--offline]
"""
import hashlib
import re
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "roach-root"
LINE = re.compile(r"^([0-9a-f]{64})\s+\*?(\S.*?)\s*$")
FETCHED = {"dl_ZL/ZL3b-n.txt": "data/ZL3b-n.txt",
           "dl_IT/IT2a-n.txt": "data/external/voynich-nu-ivtff/IT2a-n.txt",
           "dl_RF/RF1b-e.txt": "data/external/voynich-nu-ivtff/RF1b-e.txt"}
WLC = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/{name}"
GUTENBERG = "https://www.gutenberg.org/cache/epub/{n}/pg{n}.txt"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def wanted():
    """{path under roach-root: sha256} for every dl_* input a roach stub or manifest lists."""
    out = {}
    for run in sorted((ROOT / "runs").glob("roach-r*")):
        name = run.name.replace("roach-", "")
        for listing in list(run.glob("*.prereg.sha256")) + list(run.glob("MANIFEST.sha256")):
            for line in listing.read_text(encoding="utf-8", errors="ignore").splitlines():
                m = LINE.match(line.strip())
                if not m or line.lstrip().startswith("#") or "dl_" not in m.group(2):
                    continue
                rel = (Path(name) / m.group(2)).as_posix()
                parts = []
                for part in rel.split("/"):  # normalise ../ without touching the file system
                    if part == "..":
                        parts.pop() if parts else None
                    elif part not in ("", "."):
                        parts.append(part)
                out["/".join(parts)] = m.group(1)
    return out


def source_for(rel: str):
    """(kind, local path or URL) for one input."""
    tail = rel.split("/", 1)[1] if not rel.startswith("dl_") else rel
    for k, v in FETCHED.items():
        if tail == k or rel == k:
            return "fetched", ROOT / v
    m = re.search(r"dl_PG(\d+)/pg\1\.txt$", rel) or re.search(r"dl_DANTE/pg(1000)\.txt$", rel)
    if m:
        return "gutenberg", GUTENBERG.format(n=m.group(1))
    m = re.search(r"dl_WLC/(\w+\.xml)$", rel)
    if m:
        return "wlc", WLC.format(name=m.group(1))
    m = re.search(r"dl_CREMMA/(data/.+)$", rel)
    if m:
        return "cremma", ROOT / "data" / "external" / "cremma" / m.group(1)
    return "unknown", None


def main():
    offline = "--offline" in sys.argv
    for run in sorted((ROOT / "runs").glob("roach-r*")):
        dest = OUT / run.name.replace("roach-", "")
        if not dest.exists():
            shutil.copytree(run, dest)
    counts, notes = {"ok": 0, "differs": 0, "missing": 0}, []
    for rel, want in sorted(wanted().items()):
        target = OUT / rel
        if target.exists() and sha(target) == want:
            counts["ok"] += 1
            continue
        kind, src = source_for(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if kind in ("fetched", "cremma"):
                if not src.exists():
                    raise FileNotFoundError(f"{src.relative_to(ROOT)} not found (run "
                                            f"{'tools/fetch_data.py' if kind == 'fetched' else 'tools/fetch_cremma.py'} first)")
                shutil.copyfile(src, target)
            elif kind in ("gutenberg", "wlc") and not offline:
                req = urllib.request.Request(src, headers={"User-Agent": "voynich-research-record/roach_layout"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    target.write_bytes(r.read())
            else:
                raise FileNotFoundError("no automatic source" if kind == "unknown" else "offline")
        except Exception as e:  # noqa: BLE001 - report and continue with the next input
            counts["missing"] += 1
            notes.append(f"missing  {rel}: {e}")
            continue
        if sha(target) == want:
            counts["ok"] += 1
        else:
            counts["differs"] += 1
            notes.append(f"differs  {rel}: sha256 {sha(target)[:12]} (roach used {want[:12]}; the source may have changed)")
    for n in notes:
        print(n)
    print(f"roach-root/: {counts['ok']} inputs match roach's sha256, {counts['differs']} differ, {counts['missing']} missing")
    sys.exit(1 if counts["missing"] or counts["differs"] else 0)


if __name__ == "__main__":
    main()
