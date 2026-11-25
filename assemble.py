#!/usr/bin/env python3
"""Assemble the Atlas from a source checkout and verify every byte."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent
NAME = "Voynich-Reconstruction-Atlas-1.0.zip"
EXPECTED = "debec9a2be89fa9ae8c21cb23490778996888309619ce94d59e68c296dcb3ab5"

def assemble(destination):
    destination.mkdir(parents=True, exist_ok=True)
    final = destination / NAME
    with tempfile.NamedTemporaryFile(dir=destination, delete=False) as out:
        temporary = Path(out.name)
    try:
        digest = hashlib.sha256()
        with temporary.open("wb") as stream:
            for index in range(1, 13):
                part = ROOT / "distribution" / f"part-{index:03}"
                with part.open("rb") as source:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        stream.write(block)
                        digest.update(block)
        if digest.hexdigest() != EXPECTED:
            raise ValueError("The assembled Atlas does not match the published SHA-256.")
        with ZipFile(temporary) as archive:
            manifest = json.loads(archive.read("MANIFEST.sha256.json"))
            if set(archive.namelist()) != set(manifest) | {"MANIFEST.sha256.json"}:
                raise ValueError("The archive file list does not match the edition manifest.")
            for name, checksum in manifest.items():
                if hashlib.sha256(archive.read(name)).hexdigest() != checksum:
                    raise ValueError(f"Checksum mismatch for {name}")
        os.replace(temporary, final)
        print(f"{final} ({len(manifest)} files verified)")
    finally:
        temporary.unlink(missing_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path.cwd())
    assemble(parser.parse_args().output)
