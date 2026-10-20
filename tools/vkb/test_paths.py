"""Regression: ROOT/DB must be openable plain Windows paths (no \\\\?\\ prefix).

Run: .venv/Scripts/python.exe -I tools/vkb/test_paths.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, DB, connect

assert not ROOT.startswith("\\\\?\\"), f"ROOT keeps long-path prefix: {ROOT!r}"
zl = os.path.join(ROOT, "data/translit/ZL3b_eva.meta.json")
with open(zl, encoding="utf-8") as f:
    assert f.read(1), "ZL meta empty"
assert os.path.isdir(os.path.dirname(DB)), f"DB dir missing: {DB}"
assert connect().execute("PRAGMA temp_store").fetchone()[0] == 2, "temp_store must be MEMORY"
print("OK test_paths ROOT=", ROOT)
