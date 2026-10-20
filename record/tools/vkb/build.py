"""Rebuild data/vkb/vkb.sqlite from the canonical sources (D-070). Usage: python tools/vkb/build.py"""
import importlib, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from common import DB, connect, now, insert, create

MODULES = ["manuscript", "features", "evidence", "world"]


def protect_pinned(db):
    """D-074: a stub that names data/vkb/vkb.sqlite pins the bytes it hashed. Before the live DB is replaced,
    copy it to vkb.orig-<hash6>.sqlite when any stub carries its hash, so that stub still verifies against the copy."""
    import glob, hashlib, shutil
    h = hashlib.sha256(open(db, "rb").read()).hexdigest()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(db))))
    stubs = glob.glob(os.path.join(root, "*.prereg.sha256")) + glob.glob(os.path.join(root, "runs", "**", "*.prereg.sha256"), recursive=True)
    if any(h in open(s, encoding="utf-8", errors="replace").read() for s in stubs):
        dst = os.path.join(os.path.dirname(db), f"vkb.orig-{h[:6]}.sqlite")
        if not os.path.exists(dst):
            shutil.copy2(db, dst)
            print("protected pinned VKB as", os.path.basename(dst))


def main():
    tmp = DB + ".building"
    if os.path.exists(tmp):  # a half-built file from a failed build: set aside, never deleted
        os.replace(tmp, tmp + "." + time.strftime("%Y%m%d-%H%M%S") + ".failed")
    conn = connect(tmp)
    create(conn, "build_log", ["module TEXT", "seconds REAL", "built_at TEXT", "tables TEXT"])
    for name in MODULES:
        t0 = time.time()
        mod = importlib.import_module(name)
        mod.build(conn)
        conn.commit()
        tabs = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        insert(conn, "build_log", [{"module": name, "seconds": round(time.time() - t0, 1), "built_at": now(),
                                    "tables": ",".join(tabs), "src": f"tools/vkb/{name}.py"}])
        conn.commit()
        print(f"{name}: {time.time() - t0:.1f}s")
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.close()
    if os.path.exists(DB):  # keep every earlier build
        protect_pinned(DB)
        os.replace(DB, DB + "." + time.strftime("%Y%m%d-%H%M%S") + ".previous")
    os.replace(tmp, DB)
    print("built", DB)
    import check
    sys.exit(check.main())


if __name__ == "__main__":
    main()
