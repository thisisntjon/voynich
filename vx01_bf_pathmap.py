"""vx01_bf_pathmap.py -- load roach r13 (and through it r10, r7) without editing any file.

Plan: PLAN-X01-B-FALLBACK-v3, section 8a (base PLAN-X01-v5.1 af4fee6b...). NOT FROZEN until IV accepts.

Why: runs/roach-r13/r13.py:66 spec-loads HERE/../r10/r10.py and runs/roach-r10/r10.py:61 spec-loads
HERE/../r7/r7.py. Those paths (runs/r10, runs/r7) do not exist; the files live in runs/roach-r10 and
runs/roach-r7. Both loads go through importlib.util.spec_from_file_location, so for the duration of ONE
import of r13 this module wraps that one function and remaps exactly the two paths in REMAP.

Rules (plan 8a):
- Remap only if the source path does not exist AND the target exists; otherwise stop (RuntimeError).
- Every remap is logged through the caller's log function, one record per remap, in every run.
- If the caller passes expected target hashes (from its stub), a mismatch stops the run.
- The original function is restored afterwards, even on error.
- Single process only: nothing here is picklable to workers, and no worker is ever started.
- This module opens files only to hash them; it writes nothing itself (the caller's log does).

Use:  r13 = vx01_bf_pathmap.load_r13(log)   where log(record_dict) appends to the caller's chained log.
Smoke test:  python -B vx01_bf_pathmap.py --smoke   (imports r13 only; calls no r13 function; logs to
vx01_bf_pathmap_dev_runs.log through vx01_common.append_chained).
"""
import hashlib
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
R13 = os.path.join(ROOT, "runs", "roach-r13", "r13.py")
REMAP = {  # source (what r13/r10 ask for) -> target (where the file is); normalised absolute paths
    os.path.normpath(os.path.join(ROOT, "runs", "r10", "r10.py")):
        os.path.normpath(os.path.join(ROOT, "runs", "roach-r10", "r10.py")),
    os.path.normpath(os.path.join(ROOT, "runs", "r7", "r7.py")):
        os.path.normpath(os.path.join(ROOT, "runs", "roach-r7", "r7.py")),
}


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def load_r13(log, expected=None):
    """Import r13.py by spec with the two remaps active; return the module object.
    log: callable taking one dict. expected: optional {relative target path: sha256}."""
    orig = importlib.util.spec_from_file_location
    done = []

    def remapped(name, location=None, *args, **kwargs):
        if location is not None:
            src = os.path.normpath(os.path.abspath(os.fspath(location)))
            if src in REMAP:
                dst = REMAP[src]
                if os.path.exists(src) or not os.path.exists(dst):
                    raise RuntimeError("pathmap: refuse %s -> %s (source exists or target missing)" % (rel(src), rel(dst)))
                h = sha256_file(dst)
                if expected is not None and expected.get(rel(dst)) != h:
                    raise RuntimeError("pathmap: %s sha256 %s not as expected" % (rel(dst), h))
                log(dict(event="PATHMAP", module=name, src=rel(src), dst=rel(dst), dst_sha256=h))
                done.append(rel(dst))
                location = dst
        return orig(name, location, *args, **kwargs)

    importlib.util.spec_from_file_location = remapped
    try:
        spec = orig("r13", R13)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        importlib.util.spec_from_file_location = orig
    if sorted(done) != sorted(rel(d) for d in REMAP.values()):
        raise RuntimeError("pathmap: expected 2 remaps, got %s" % done)
    return mod


def _smoke():
    sys.path.insert(0, ROOT)
    import vx01_common as C
    me = os.path.abspath(__file__)
    logp = C.dev_log_path(me)
    C.append_chained(logp, dict(event="SMOKE-START", script=rel(me), script_sha256=sha256_file(me),
                                r13_sha256=sha256_file(R13), utc=C.utc_now(), argv=sys.argv[1:]))
    r13 = load_r13(lambda rec: C.append_chained(logp, dict(rec, utc=C.utc_now())))
    info = dict(QGRID=r13.QGRID, EGRID=r13.EGRID, RGRID=r13.RGRID, r10_file=rel(r13.r10.__file__),
                r7_file=rel(r13.r7.__file__), restored=importlib.util.spec_from_file_location.__name__)
    head = C.append_chained(logp, dict(event="SMOKE-END", utc=C.utc_now(), info=info))
    print("smoke OK", info, "log head", head)


if __name__ == "__main__":
    if sys.argv[1:] == ["--smoke"]:
        _smoke()
    else:
        print("usage: python -B vx01_bf_pathmap.py --smoke  (import is the normal use)")
