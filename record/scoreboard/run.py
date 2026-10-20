"""CLI: score a corpus and file it in scoreboard/scoreboard.json (key "v2",
one entry per corpus name; the v1 "entrants" list is left untouched).

    python -m scoreboard.run --corpus voynich
    python -m scoreboard.run --corpus voynich:glyph --corpus voynich:glyph+
    python -m scoreboard.run --control latin_caesar            # flat
    python -m scoreboard.run --control italian_dante:verse     # own line breaks
    python -m scoreboard.run --control latin_caesar:lines9     # pseudo-lines of 9
    python -m scoreboard.run --sections latin_augustine        # b5 CTRL layout
    python -m scoreboard.run --meta data/synth/foo.meta.json   # sidecar corpus
    python -m scoreboard.run --control latin_caesar --skip-nmf --print

Each entry records metrics, params, seed, a clock timestamp and git-free
provenance (sha256 of score.py / corpus.py / score_v1.py, library versions).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scoreboard.corpus import Corpus          # noqa: E402
from scoreboard.score_v2 import flatten, score   # noqa: E402

BOARD = HERE / "scoreboard.json"
SECTION_HEADERS = {
    "italian_dante": r"^(INFERNO|PURGATORIO|PARADISO)$",
    "latin_augustine": r"^LIBER ([A-Z ]+?)\.?$",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance():
    import numpy, scipy, sklearn  # noqa: E401
    return dict(
        score_v2_py=sha256(HERE / "score_v2.py"), corpus_py=sha256(HERE / "corpus.py"),
        score_v1_py=sha256(HERE / "score_v1.py"),
        data_zl3b=sha256(ROOT / "data" / "ZL3b-n.txt"),
        python=platform.python_version(), numpy=numpy.__version__,
        scipy=scipy.__version__, sklearn=sklearn.__version__,
    )


def build(args):
    """Yield Corpus objects for every target on the command line."""
    for spec in args.corpus or []:
        tok = spec.split(":", 1)[1] if ":" in spec else "eva"
        yield Corpus.from_voynich(tokenization=tok)
    for spec in args.control or []:
        name, _, mode = spec.partition(":")
        if mode == "verse":
            yield Corpus.from_control(name, lines="verse")
        elif mode.startswith("lines"):
            yield Corpus.from_control(name, lines=int(mode[5:]))
        elif mode == "":
            yield Corpus.from_control(name)
        else:
            raise SystemExit(f"unknown control mode {mode!r} in {spec!r}")
    for name in args.sections or []:
        if name not in SECTION_HEADERS:
            raise SystemExit(f"no section header regex for {name!r}; "
                             f"known: {sorted(SECTION_HEADERS)}")
        yield Corpus.from_control_sections(name, SECTION_HEADERS[name])
    for path in args.meta or []:
        yield Corpus.from_meta_json(path)


def load_board(path):
    if path.exists():
        board = json.loads(path.read_text(encoding="utf-8"))
    else:
        board = {}
    board.setdefault("v2", {})
    return board


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", action="append", help="voynich | voynich:glyph | voynich:glyph+")
    ap.add_argument("--control", action="append",
                    help="control name, optionally :verse or :linesN")
    ap.add_argument("--sections", action="append",
                    help="control laid out as b5 section chunks (italian_dante, latin_augustine)")
    ap.add_argument("--meta", action="append", help="path to a .meta.json sidecar (or its .txt)")
    ap.add_argument("--name", help="override the entry name (single target only)")
    ap.add_argument("--n-tokens", type=int, default=25000)
    ap.add_argument("--seed", type=int, default=20261017)
    ap.add_argument("--skip-nmf", action="store_true", help="skip the b5 NMF/NMI block")
    ap.add_argument("--out", type=Path, default=BOARD)
    ap.add_argument("--print", action="store_true", help="print the flat metric table")
    ap.add_argument("--dry-run", action="store_true", help="score but do not write")
    args = ap.parse_args(argv)
    targets = list(build(args))
    if not targets:
        ap.error("give at least one of --corpus / --control / --sections / --meta")
    if args.name and len(targets) != 1:
        ap.error("--name needs exactly one target")
    board = load_board(args.out)
    prov = provenance()
    for corpus in targets:
        name = args.name or corpus.name
        print(f"scoring {name} ({corpus.n_tokens()} tokens, {len(corpus.pages)} pages)", flush=True)
        res = score(corpus, n_tokens=args.n_tokens, seed=args.seed,
                    skip_nmf=args.skip_nmf, verbose=True)
        entry = dict(name=name, timestamp=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                     seed=args.seed, params=res["params"], corpus=res["corpus"],
                     source=corpus.source, provenance=prov,
                     runtime_s=res["runtime_s"],
                     metrics={k: v for k, v in res.items()
                              if k not in ("params", "corpus", "runtime_s")})
        if args.print:
            for k, v in flatten(entry["metrics"]).items():
                if not k.endswith("_table"):
                    print(f"  {k:45} {v}")
        if args.dry_run:
            continue
        board["v2"][name] = entry
        args.out.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"filed {name} -> {args.out} (v2 entries: {len(board['v2'])})", flush=True)


if __name__ == "__main__":
    main()
