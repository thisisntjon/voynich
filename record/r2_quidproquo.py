"""R2 (Top-10 #3/#8): period attestation for many-to-one substitution.
Downloads the School of Salernum text (archive.org djvu.txt, public domain),
extracts Quid pro Quo entries of form 'Pro X, Y vel Z.', and measures:
 substitutes per simple (one-to-many choice) and simples per substitute
 (many-to-one sharing = lossy-collapse attestation relevant to K4).
Corpus + pairs saved under data/external/quid-pro-quo/ with hash.
Run: uv run python r2_quidproquo.py -> results_r2.txt
"""
import hashlib
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
DIR = ROOT / "data" / "external" / "quid-pro-quo"
TXT = DIR / "schoolsalernuma00handgoog_djvu.txt"
URLS = [
    "https://archive.org/download/schoolsalernuma00handgoog/schoolsalernuma00handgoog_djvu.txt",
    "https://ia801304.us.archive.org/33/items/schoolsalernuma00handgoog/schoolsalernuma00handgoog_djvu.txt",
]
OUT = ROOT / "results_r2.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    used = None
    if not TXT.exists():
        errors = []
        for u in URLS:
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "voynich-team-research/1.0"})
                TXT.write_bytes(urllib.request.urlopen(req, timeout=120).read())
                used = u
                break
            except Exception as e:  # noqa: BLE001 - report all mirrors failing
                errors.append(f"{u}: {e}")
        if used is None:
            emit("DOWNLOAD FAILED all mirrors: " + " | ".join(errors))
            OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
            return
    raw = TXT.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    emit(f"source {used or 'cached file'} bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()}")
    # Entries: Pro <simple>, <subs separated by vel/aut>.
    pat = re.compile(r"Pro\s+([a-zA-Z][a-zA-Z\s\-]{1,40}?),\s*([a-zA-Z][a-zA-Z\s\-]{1,80})\.", re.I)
    pairs = []
    for m in pat.finditer(text):
        simple = " ".join(m.group(1).lower().split())
        subs = [" ".join(s.lower().split()) for s in re.split(r"\s+(?:vel|aut)\s+", m.group(2), flags=re.I)]
        subs = [s for s in subs if 2 <= len(s) <= 40]
        if simple and subs:
            pairs.append((simple, subs))
    by_simple = defaultdict(set)
    by_sub = defaultdict(set)
    for s, subs in pairs:
        for x in subs:
            by_simple[s].add(x)
            by_sub[x].add(s)
    emit(f"parsed entries={len(pairs)} simples={len(by_simple)} substitutes={len(by_sub)}")
    spc = Counter(len(v) for v in by_simple.values())
    cps = Counter(len(v) for v in by_sub.values())
    emit(f"substitutes-per-simple distribution: {dict(sorted(spc.items()))}")
    emit(f"simples-per-substitute distribution: {dict(sorted(cps.items()))}")
    shared = {x: ss for x, ss in by_sub.items() if len(ss) > 1}
    emit(f"shared substitutes (many-to-one): {len(shared)}/{len(by_sub)} "
         f"({100*len(shared)/max(len(by_sub),1):.1f}%); max simples per substitute={max((len(v) for v in by_sub.values()), default=0)}")
    for x, ss in sorted(shared.items(), key=lambda kv: -len(kv[1]))[:12]:
        emit(f"  {x} <- {', '.join(sorted(ss))}")
    csv = ["simple,substitute"] + [f"{s},{x}" for s, subs in pairs for x in subs]
    (DIR / "quid_pro_quo_pairs.csv").write_text("\n".join(csv) + "\n", encoding="utf-8")
    emit(f"pairs written: {len(csv)-1} rows -> data/external/quid-pro-quo/quid_pro_quo_pairs.csv")
    emit("Scope: one printed Salernum edition's appendix; genre attestation, "
         "not the 1477 Benedetto item (still unverified, STEAL-VERIFY.md).")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Wrote results_r2.txt")


if __name__ == "__main__":
    main()
