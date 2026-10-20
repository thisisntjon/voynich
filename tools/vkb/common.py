"""Shared helpers for the VKB build (see tools/vkb/README.md)."""
import os, sqlite3, subprocess

def _plain(p):
    # The \\?\ long-path prefix breaks open()/makedirs() on joined paths here.
    return p[4:] if p.startswith("\\\\?\\") else p


ROOT = _plain(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
DB = os.path.join(ROOT, "data", "vkb", "vkb.sqlite")


def connect(path=None):
    conn = sqlite3.connect(path or DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA temp_store=MEMORY")  # file temp spill fails in some shells
    return conn


def now():
    try:
        return subprocess.check_output(["date", "+%Y-%m-%d %H:%M"]).decode().strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")


def rel(path):
    p = _plain(os.path.abspath(path))
    return os.path.relpath(p, ROOT).replace("\\", "/") if p.startswith(ROOT) else p.replace("\\", "/")


def create(conn, table, cols):
    """cols: list of 'name TYPE' strings; adds src TEXT NOT NULL."""
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.execute(f"CREATE TABLE {table} ({', '.join(cols + ['src TEXT NOT NULL'])})")


def insert(conn, table, rows):
    rows = list(rows)
    if not rows:
        return 0
    keys = list(rows[0].keys())
    assert "src" in keys, f"{table}: rows need src"
    conn.executemany(f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({', '.join('?' * len(keys))})",
                     [tuple(r.get(k) for k in keys) for r in rows])
    return len(rows)
