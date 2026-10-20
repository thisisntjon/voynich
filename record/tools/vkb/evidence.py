"""VKB module: runs, claims, measurements, findings, finding_lines, hypotheses, points, assumptions,
pending, learnings, decisions, open_questions (schema and row rules: tools/vkb/README.md).

Sources (all read-only):
  * results_*.txt in the root, runs/*/ (runs/roach-r*/results_rN.txt, runs/roach-r1r2-raw), the
    pre-registration stubs (*.prereg.sha256) and scripts beside them.
  * .inventory/registers/CLAIMS.md, LEARNINGS.md, DECISIONS.md, OPEN.md (markdown tables).
  * workflow/FINDINGS-GRAPH.yaml (yaml.safe_load, as tools/findings_graph.py reads it; line numbers from
    yaml.compose; grade from tools/findings_graph.grade).
  * TEAM-HANDOFF.md run-id lists (the "taken" line, the "Claimed ..." paragraph, the run-id alias map).

Run ids (README): lead sNN (and the lettered rounds a1, n6, m4 ...), Daybreak db-sNN, roach rN.
  Two local conventions, forced by collisions in the tree:
  * lead r-round ids (r1_register_extract.py, r2_quidproquo.py / results_r2.txt) are `lead-r1`, `lead-r2`
    so they do not collide with roach r1/r2.
  * where two scripts share a prefix and both write results (TEAM-HANDOFF: "cite by filename"), the run
    that writes results_<stem>.txt keeps the full stem (s34_morphology_syntax_geography, n6_ab_split ...);
    the run writing results_sNN.txt keeps sNN.
  s111 is running (TEAM-HANDOFF): no s111_* or runs/s111 file is opened, hashed or stat'ed.

stub_ok runs, from the stub's directory, the binding check
  grep -v "^#" STUB | tr -d '\\r' | sha256sum -c -
as a process pipeline (Git for Windows grep/tr/sha256sum). stub_ok 1 = exit 0, 0 = any failure.

Measurements: regex handlers map numbers in each claim's quoted text and Value cell to canonical
statistic names (README list); CALL_ / VERDICT lines are read from every results file with their line.
Ranges ("a-b", "a..b", "a to b") go to ci_lo/ci_hi with value NULL and scope starting "range:";
an unattached "[a, b]" goes the same way with scope "interval:". Numbers no handler consumed are listed
in the claim's note ("unparsed: ...") so nothing is lost. No number is computed or inferred.
Coverage pass (2026-10-18 17:20 PDT): z owns only the number(s) right after it (it no longer donates its value to
the statistic before it, and does not block a Value cell's default statistic); dAIC, R(d>1), MATTR added; an a/b
chain followed by a non-fold unit ("24/24 points", "9/9 cells", "0/3353 CI violations", "1/6 held-out
predictions"), a p floor "1/55", a hand id ("hand 1", "hands 2/3"), a parenthesised index "(10)" and the level
of "95% CI" are no longer read as folds or values; a clause with no canonical statistic keeps its printed p as
statistic p_value; lower-case "verdict: x" in the claim text becomes a verdict row.
"""
import datetime, glob, hashlib, os, re, shutil, subprocess, sys

import yaml

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, rel, create, insert  # noqa: E402

REG = os.path.join(ROOT, ".inventory", "registers")
CLAIMS_MD = os.path.join(REG, "CLAIMS.md")
DECISIONS_MD = os.path.join(REG, "DECISIONS.md")
LEARNINGS_MD = os.path.join(REG, "LEARNINGS.md")
OPEN_MD = os.path.join(REG, "OPEN.md")
GRAPH = os.path.join(ROOT, "workflow", "FINDINGS-GRAPH.yaml")
HANDOFF = os.path.join(ROOT, "TEAM-HANDOFF.md")
SKIP = "s111"  # running: never touch s111_* or runs/s111

REJECTED = {"s93": "D-064", "s96": "D-065"}


# ----------------------------------------------------------------------------- small helpers
def rd(p):
    with open(p, "rb") as f:
        b = f.read()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16", errors="replace")
    return b.decode("utf-8-sig", errors="replace")


def ts(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def skipped(path):
    b = os.path.basename(path.rstrip("/\\"))
    return b.startswith(SKIP + "_") or b == SKIP or b.startswith("results_" + SKIP) or \
        ("runs/" + SKIP) in path.replace("\\", "/")


PREFIX_RE = re.compile(r"^([a-z]+\d+(?:[a-z]+\d*)?)(?=_|\.|-|$)")


def prefix(stem):
    m = PREFIX_RE.match(stem)
    return m.group(1) if m else stem


def run_sort_key(r):
    m = re.match(r"^(db-|lead-)?([a-z]+)(\d+)(.*)$", r)
    return (m.group(1) or "", m.group(2), int(m.group(3)), m.group(4)) if m else ("~", r, 0, "")


# ----------------------------------------------------------------------------- markdown tables
PH = "\x00"


def split_cells(line):
    """Split a markdown table row on unescaped pipes outside code spans; edge cells dropped."""
    s = line.replace("\\|", PH)
    s = re.sub(r"`[^`\n]*`", lambda m: m.group(0).replace("|", PH), s)
    cells = s.strip().split("|")
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.replace(PH, "\\|").strip() for c in cells]


def join(cells):
    return " | ".join(cells) if cells else None


def unesc(s):
    return s.replace("\\|", "|") if s is not None else None


DATE_CELL = re.compile(r"^\d{4}-\d{2}-\d{2}\b")


def table_rows(path, id_re):
    """(line_no, cells) for rows whose first cell matches id_re."""
    out = []
    for i, line in enumerate(rd(path).split("\n"), 1):
        if not line.startswith("|"):
            continue
        cells = split_cells(line)
        if cells and re.match(id_re, cells[0].strip("` ")):
            out.append((i, cells))
    return out


# ----------------------------------------------------------------------------- registers
def parse_claims():
    rows = []
    for ln, c in table_rows(CLAIMS_MD, r"^c-\d+$"):
        cid = c[0].strip("` ")
        # anchor on the Verified date cell: id | claim | value | source | method | date | status | used in
        jd = None
        for j in range(len(c) - 1, 0, -1):
            if DATE_CELL.match(c[j]) and j >= 5:
                jd = j
                break
        if jd is None:
            jd = 5 if len(c) >= 8 else len(c) - 3
        status = c[jd + 1] if jd + 1 < len(c) else None
        used = join(c[jd + 2:]) if jd + 2 < len(c) else None
        method = c[jd - 1]
        source = c[jd - 2]
        mid = c[1:jd - 2]  # claim (+ value); extra pipes land here
        k = None
        for j in range(len(mid) - 1, -1, -1):
            if mid[j].rstrip().endswith(('"', "”")) and j < len(mid) - 1:
                k = j
                break
        if k is None:
            k = 0 if len(mid) > 1 else len(mid) - 1
        claim = "|".join(mid[:k + 1])
        value = "|".join(mid[k + 1:]) or None
        rows.append(dict(ln=ln, cid=cid, claim=unesc(claim), value=unesc(value), source=unesc(source),
                         method=unesc(method), date=c[jd], status=unesc(status), used=unesc(used)))
    return rows


def parse_decisions():
    out = []
    for ln, c in table_rows(DECISIONS_MD, r"^D-\d+$"):
        did, date, dec = c[0], c[1] if len(c) > 1 else None, c[2] if len(c) > 2 else ""
        body2 = refs = state = None
        if len(c) == 4:
            refs = c[3]
        elif len(c) == 5:
            body2, refs = c[3], c[4]
        elif len(c) >= 6:
            body2, refs, state = c[3], c[4], join(c[5:])
        m = re.match(r"\*\*(.+?)\*\*", dec)
        if m:
            title = m.group(1).strip(" .:")
        else:
            title = re.split(r"(?<=[.;:])\s", dec, 1)[0] if len(dec) > 200 else dec
        body = dec + (("\n\nWho / account: " + body2) if body2 else "")
        out.append(dict(did=did, date=date, title=unesc(title), body=unesc(body), refs=unesc(refs),
                        state=unesc(state), src=f"{rel(DECISIONS_MD)}:{ln}"))
    return out


def parse_learnings():
    out = []
    for ln, c in table_rows(LEARNINGS_MD, r"^L-\d+[a-z]?$"):
        date = c[-1] if DATE_CELL.match(c[-1]) else None
        body = c[1:-1] if date else c[1:]
        if len(body) >= 4:
            belief, result, evidence, change = body[0], body[1], body[2], "|".join(body[3:])
        elif len(body) == 3:
            belief, result, evidence, change = body[0], None, body[1], body[2]
        else:
            belief, result, evidence, change = (body + [None] * 4)[:4]
        out.append(dict(lid=c[0], belief=unesc(belief), result=unesc(result), evidence=unesc(evidence),
                        change=unesc(change), date=date, src=f"{rel(LEARNINGS_MD)}:{ln}"))
    return out


STATE_WORD = re.compile(r"^(open|parked|closed|active|answered|blocked|done|superseded)\b", re.I)
MARKER = re.compile(r"\*\*\[(CLOSED|ANSWERED|SCOPE|REPAIRED|MECHANISM IDENTIFIED|REOPENED)[^\]]*\]\*\*|"
                    r"^\*\*(CLOSED)\b|^(CLOSED)\b", re.I)


def parse_open():
    out = []
    for ln, c in table_rows(OPEN_MD, r"^O-\d+$"):
        oid, q = c[0], c[1] if len(c) > 1 else ""
        rest = c[2:]
        state = None
        if len(rest) == 2:  # question | state | note  or  question | note | state
            si = 0 if STATE_WORD.match(rest[0]) else (1 if STATE_WORD.match(rest[1]) else None)
            if si is not None:
                state = rest[si]
                source = rest[1 - si]
            else:
                source = join(rest)
        else:
            names = ["why parked", "what would close it", "cost", "evidence"]
            source = "; ".join(f"{names[i] if i < len(names) else 'more'}: {x}" for i, x in enumerate(rest))
        if state is None:
            m = MARKER.search(q)
            state = (next(g for g in m.groups() if g)).lower() if m else "open"
        out.append(dict(oid=oid, question=unesc(q), source=unesc(source), state=state,
                        src=f"{rel(OPEN_MD)}:{ln}"))
    return out


# ----------------------------------------------------------------------------- graph
def graph_lines(text):
    """{(section, key): line, (section, key, list, idx): line} from yaml.compose marks."""
    node = yaml.compose(text, Loader=yaml.SafeLoader)
    marks = {}
    for k, v in node.value:
        sec = k.value
        if not isinstance(v, yaml.MappingNode):
            continue
        for k2, v2 in v.value:
            marks[(sec, k2.value)] = k2.start_mark.line + 1
            if isinstance(v2, yaml.MappingNode):
                for k3, v3 in v2.value:
                    if isinstance(v3, yaml.SequenceNode):
                        for i, item in enumerate(v3.value):
                            marks[(sec, k2.value, k3.value, i)] = item.start_mark.line + 1
    return marks


def load_graph():
    text = rd(GRAPH)
    g = yaml.safe_load(text)
    for k in ("axes", "hypotheses", "assumptions", "findings", "pending"):
        g[k] = g.get(k) or {}
    return g, graph_lines(text)


def grade_fn():
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import findings_graph
        return findings_graph.grade
    except Exception:  # same rule as tools/findings_graph.grade, kept in step by hand
        indep = {"impl", "physical", "external"}

        def grade(f):
            lines = [l for l in f.get("lines", []) if not l.get("unverified")]
            agree = {l["axis"] for l in lines if l.get("agrees", True) and "axis" in l}
            if [l for l in lines if not l.get("agrees", True) and not l.get("resolved")]:
                return "CONTESTED", agree
            if len(agree) >= 3 and agree & indep:
                return "TRIANGULATED", agree
            return ("CORROBORATED" if len(agree) >= 2 else "SINGLE"), agree
        return grade


def b01(x):
    return None if x is None else (1 if x else 0)


def build_graph_tables(conn):
    g, marks = load_graph()
    gsrc = rel(GRAPH)
    grade = grade_fn()
    F, FL, P = [], [], []
    for fid, f in g["findings"].items():
        ln = marks.get(("findings", fid))
        try:
            gr = grade(f)[0]
        except Exception:
            gr = None
        F.append(dict(fid=fid, title=f.get("title"), status=f.get("status"), load_bearing=b01(f.get("load_bearing", False)),
                      absence=b01(f.get("absence", False)), grade=gr, src=f"{gsrc}:{ln}"))
        for key in ("lines", "controls"):
            for i, l in enumerate(f.get(key) or []):
                if not isinstance(l, dict):
                    continue
                known = {"axis", "by", "ref", "claim", "agrees", "unverified", "resolved", "note", "what"}
                extra = "; ".join(f"{k}={v}" for k, v in l.items() if k not in known)
                note = "; ".join(x for x in [str(l["note"]) if l.get("note") else "", extra,
                                             "control" if key == "controls" else ""] if x) or None
                FL.append(dict(fid=fid, axis=l.get("axis") or ("control" if "what" in l else None),
                               by=l.get("by") or l.get("what"), ref=l.get("ref"), claim=l.get("claim"),
                               agrees=b01(l.get("agrees", True)) if "agrees" in l or "axis" in l else None,
                               unverified=b01(l.get("unverified", False)),
                               resolved=str(l["resolved"]) if l.get("resolved") is not None else None,
                               note=note, src=f"{gsrc}:{marks.get(('findings', fid, key, i), ln)}"))
        for i, p in enumerate(f.get("points") or []):
            P.append(dict(fid=fid, hid=p.get("h"), rel=p.get("rel"), strength=p.get("strength"), why=p.get("why"),
                          src=f"{gsrc}:{marks.get(('findings', fid, 'points', i), ln)}"))
    H = [dict(hid=h, short=v.get("short"), name=v.get("name"), status=str(v.get("status")),
              src=f"{gsrc}:{marks.get(('hypotheses', h))}") for h, v in g["hypotheses"].items()]
    X = [dict(xid=x, statement=v.get("statement") + (f" (basis: {v['basis']})" if v.get("basis") else ""),
              status=v.get("status"), src=f"{gsrc}:{marks.get(('assumptions', x))}") for x, v in g["assumptions"].items()]
    PE = []
    for pid, v in g["pending"].items():
        dec = v.get("decides")
        PE.append(dict(pid=pid, run=str(v.get("run")) if v.get("run") is not None else None, owner=v.get("owner"),
                       state=v.get("state"), result=v.get("result"),
                       decides=", ".join(map(str, dec)) if isinstance(dec, list) else dec,
                       question=v.get("question"), src=f"{gsrc}:{marks.get(('pending', pid))}"))
    create(conn, "findings", ["fid TEXT PRIMARY KEY", "title TEXT", "status TEXT", "load_bearing INTEGER",
                              "absence INTEGER", "grade TEXT"])
    create(conn, "finding_lines", ["fid TEXT", "axis TEXT", "by TEXT", "ref TEXT", "claim TEXT", "agrees INTEGER",
                                   "unverified INTEGER", "resolved TEXT", "note TEXT"])
    create(conn, "hypotheses", ["hid TEXT PRIMARY KEY", "short TEXT", "name TEXT", "status TEXT"])
    create(conn, "points", ["fid TEXT", "hid TEXT", "rel TEXT", "strength TEXT", "why TEXT"])
    create(conn, "assumptions", ["xid TEXT PRIMARY KEY", "statement TEXT", "status TEXT"])
    create(conn, "pending", ["pid TEXT PRIMARY KEY", "run TEXT", "owner TEXT", "state TEXT", "result TEXT",
                             "decides TEXT", "question TEXT"])
    for t, rows in (("findings", F), ("finding_lines", FL), ("hypotheses", H), ("points", P),
                    ("assumptions", X), ("pending", PE)):
        insert(conn, t, rows)
    return g, marks, PE


# ----------------------------------------------------------------------------- run discovery
def scripts_index():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "*.py")):
        stem = os.path.splitext(os.path.basename(p))[0]
        if not skipped(stem):
            out[stem] = p
    return out


def collision_runs(scripts, root_results):
    """Script stems that write results_<stem>.txt while results_<prefix>.txt also exists."""
    stems = {os.path.basename(p)[8:-4] for p in root_results}
    out = set()
    for st in scripts:
        pf = prefix(st)
        if st != pf and st in stems and pf in stems:
            out.add(st)
    return out


def run_of_results_name(stem, coll, in_root=True):
    """stem = results file name without 'results_' and '.txt'."""
    for c in sorted(coll, key=len, reverse=True):
        if stem == c or stem.startswith(c + "_") or stem.startswith(c + "."):
            return c
    pf = prefix(stem)
    if pf == "n6" and stem != "n6" and "n6_ab_split" in coll:  # n6_ab_split writes results_n6_{tag}.txt
        return "n6_ab_split"
    if in_root and re.fullmatch(r"r\d+", pf):
        return "lead-" + pf
    return pf


def run_of_path(path, coll):
    p = path.replace("\\", "/")
    m = re.search(r"runs/roach-r(\d+)[^/]*/results_r(\d+)", p)
    if m:
        return "r" + m.group(2)
    m = re.search(r"runs/roach-r1r2-raw/results_(r\d)", p)
    if m:
        return m.group(1)
    if "codex_lab" in p or "yonichmanuscript" in p:
        m = re.search(r"results_(s\d+)", p)
        return ("db-" + m.group(1)) if m else None
    m = re.search(r"(?:^|/)results_([\w.\-]+?)\.txt", p)
    if m:
        in_root = "/" not in p.split("results_")[0].strip("/") if not p.startswith("runs/") else False
        return run_of_results_name(m.group(1), coll, in_root=in_root)
    return None


def norm_token(tok, coll):
    """A run-id-like token from prose -> run id or None."""
    t = tok.strip("`'\" ,.;:()")
    t = re.sub(r"\.(py|txt|json)$", "", t)
    if t.startswith("results_"):
        return run_of_results_name(t[8:], coll)
    if re.fullmatch(r"db-s\d+", t):
        return t
    if t in coll:
        return t
    pf = prefix(t)
    if re.fullmatch(r"[a-z]{1,2}\d+(?:[a-z]+\d*)?", pf) and not re.fullmatch(r"(sha|x|c|f|h|o|d|l|p|k|q)\d{3,}", pf):
        return pf
    return None


def handoff_runs(coll):
    """{run_id: {'src': ..., 'owner': ..., 'results': ...}} from the TEAM-HANDOFF run-id lists."""
    out = {}
    lines = rd(HANDOFF).split("\n")
    in_alias = False

    def add(rid, ln, **kw):
        if not rid:
            return
        d = out.setdefault(rid, {"src": f"{rel(HANDOFF)}:{ln}"})
        for k, v in kw.items():
            if v and not d.get(k):
                d[k] = v

    for ln, line in enumerate(lines, 1):
        if line.startswith("### Run-id alias map"):
            in_alias = True
            continue
        if in_alias and line.startswith("#"):
            in_alias = False
        if in_alias and line.startswith("| s"):
            c = split_cells(line)
            rid = c[0].strip()
            owner = re.split(r"[,(]", c[1])[0].strip() if len(c) > 1 else None
            add(rid, ln, owner=owner)
            if len(c) > 2:
                m = re.search(r"db-s\d+", c[2]) or (re.match(r"\s*db-", c[2]) and None)
                did = m.group(0) if m else "db-" + rid
                pm = re.search(r"([A-Za-z]:/[^\s()]+?results_[^\s()]+?\.txt)", c[2])
                add(did, ln, owner="Daybreak", results=pm.group(1) if pm else None)
            continue
        is_list = ("are taken" in line) or line.startswith("Claimed ") or ("db-s" in line and "Daybreak" in line)
        if not is_list:
            continue
        taken = "are taken" in line
        # ranges `x`–`y`
        for a, b in re.findall(r"`([a-z]+\d+)`\s*[–-]\s*`([a-z]+\d+)`", line):
            ma, mb = re.match(r"([a-z]+)(\d+)", a), re.match(r"([a-z]+)(\d+)", b)
            if ma.group(1) == mb.group(1):
                for n in range(int(ma.group(2)), int(mb.group(2)) + 1):
                    add(ma.group(1) + str(n), ln)
        for a, b in re.findall(r"db-s(\d+)\s+to\s+db-s(\d+)", line):
            for n in range(int(a), int(b) + 1):
                add(f"db-s{n}", ln, owner="Daybreak")
        for tok in re.findall(r"`([^`]+)`", line):
            if taken and re.fullmatch(r"r\d+", tok):
                add("lead-" + tok, ln)
                continue
            if " " in tok or "=" in tok or "/" in tok:
                continue
            add(norm_token(tok, coll), ln)
        for tok in re.findall(r"\bdb-s\d+\b", line):
            add(tok, ln, owner="Daybreak")
    return out


def find_tool(name):
    p = shutil.which(name)
    if p and "system32" not in p.lower():
        return p
    for d in (r"C:\Program Files\Git\usr\bin", r"C:\Program Files (x86)\Git\usr\bin"):
        q = os.path.join(d, name + ".exe")
        if os.path.exists(q):
            return q
    return p


TOOLS = {}


_RELOC = {}


def _relocated(base, h):
    """A stub path written on another machine (e.g. roach's ../r7/r7.py, ../dl_ZL/ZL3b-n.txt) counts when a file with the
    same name under data/, runs/ or the repo root has the same hash. Returns its repo-relative path or None."""
    if not _RELOC:
        for top in ("data", "runs", "."):
            base_dir = os.path.join(ROOT, top)
            for dp, dn, fn in os.walk(base_dir):
                if top == "." and dp != base_dir:
                    continue
                dn[:] = [x for x in dn if x not in ("__pycache__", "vkb", "facsimile")]
                for f in fn:
                    _RELOC.setdefault(f, []).append(os.path.join(dp, f))
        _RELOC["__built__"] = []
    for fp in _RELOC.get(base, []):
        try:
            if os.path.getsize(fp) < 200_000_000 and hashlib.sha256(open(fp, "rb").read()).hexdigest() == h:
                return rel(fp)
        except OSError:
            pass
    return None



def stub_check(stub):
    """Run grep -v "^#" STUB | tr -d '\\r' | sha256sum -c - in the stub's directory. Returns (ok, detail)."""
    if not TOOLS:
        TOOLS.update({k: find_tool(k) for k in ("grep", "tr", "sha256sum")})
    if not all(TOOLS.values()):
        return None, "tools missing"
    d, b = os.path.dirname(stub), os.path.basename(stub)
    try:
        p1 = subprocess.Popen([TOOLS["grep"], "-v", "^#", b], cwd=d, stdout=subprocess.PIPE)
        # tr's own "\r" escape, as in tr -d '\r' (a literal CR argument is dropped by the Windows command line)
        p2 = subprocess.Popen([TOOLS["tr"], "-d", "\\r"], cwd=d, stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        p3 = subprocess.Popen([TOOLS["sha256sum"], "-c", "-"], cwd=d, stdin=p2.stdout,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p2.stdout.close()
        out = p3.communicate(timeout=900)[0].decode("utf-8", "replace")
        p1.wait()
        p2.wait()
        bad = [l for l in out.splitlines() if not l.rstrip().endswith(": OK")]
        if p3.returncode != 0 and bad:
            # Judge each stub line on its own. A file edited after the freeze counts as verified when its hashed
            # original is preserved beside it as <stem>.orig-<first 6 hex>.<ext> and matches (audit-1217-rewrite.md).
            # When a stub names a file twice, the last uncommented line is binding (AGENTS.md).
            restored, left, entries = [], [], {}
            for ln in open(stub, encoding="utf-8", errors="replace"):
                if ln.startswith("#") or not ln.strip():
                    continue
                parts = ln.strip().split(None, 1)
                if len(parts) != 2:
                    continue
                entries[parts[1].lstrip("*").strip()] = parts[0].lower()
            checked = [l for l in out.splitlines() if l.rstrip().endswith(": OK") or ": FAILED" in l]  # file lines only, not the WARNING summary
            superseded = len(checked) - len(entries)
            for name, h in entries.items():
                fp = os.path.join(d, name)
                cur = hashlib.sha256(open(fp, "rb").read()).hexdigest() if os.path.isfile(fp) else None
                if cur == h:
                    continue
                stem, ext = os.path.splitext(fp)
                cand = f"{stem}.orig-{h[:6]}{ext}"
                if os.path.isfile(cand) and hashlib.sha256(open(cand, "rb").read()).hexdigest() == h:
                    restored.append(f"{name} -> {os.path.basename(cand)}")
                elif cur is None and _relocated(os.path.basename(name), h):
                    restored.append(f"{name} -> relocated copy {_relocated(os.path.basename(name), h)}")
                else:
                    left.append(f"{name}: {'MISSING' if cur is None else 'FAILED'} ({h[:12]})")
            if not left:
                note = f"; {superseded} earlier duplicate line(s) superseded" if superseded > 0 else ""
                return 1, ("restored originals verify: " + "; ".join(restored) if restored else "last binding lines verify")[:450] + note
            return 0, "; ".join(left + [f"restored {r}" for r in restored])[:500]
        return (1 if p3.returncode == 0 else 0), "; ".join(bad)[:500]
    except Exception as e:  # noqa: BLE001
        return 0, f"error: {e}"


# ----------------------------------------------------------------------------- measurement extraction
STATS = [
    ("Rw1", r"R_?w(?:in|ithin)?\s*\(\s*1\s*\)|\bRw1\b|\bR_within_1\b"),
    ("Rc1", r"R_?c(?:ross)?\s*\(\s*1\s*\)|\bRc1\b|R_x'?\s*\(\s*1\s*\)|\bR_cross\b"),
    ("core_order_K100", r"\bMM[_-]?(?:MI[_ ])?K\s*=?\s*100\b|\bK\s*=\s*100\b|\bK100\b"),
    ("core_order_K200", r"\bMM[_-]?(?:MI[_ ])?K\s*=?\s*200\b|\bK\s*=\s*200\b|\bK200\b"),
    ("quire_locality", r"quire[ -]locality|\bL_q\b"),
    ("h2", r"\bh2\b"),
    ("rhythm_excess", r"lag-1 word-length (?:correlation|excess|covariance)|length rhythm|in-line rhythm|\brhythm\b"),
    ("lag2_prefix_residue", r"lag-2 prefix"),
    ("battery_folds", r"\bbattery\b"),
    ("planted_recovery_folds", r"\bplanted\b"),
    ("kappa", r"\bkappa\b|κ"),
    ("mde", r"\bMDE\b"),
    ("auc", r"\bAUC\b"),
    ("odds_ratio", r"\bodds ratio\b|\bOR\b"),
    ("jsd_first", r"\bjsd_?first(?:_fg|_exc)?\b|\bJSDf\b|first-glyph JSD|line-initial (?:JSD )?excess|line-initial JSD|JSD\(first"),
    ("jsd_last", r"\bjsd_?last(?:_lg|_exc)?\b|JSD\(last|line-final (?:JSD )?excess"),
    ("sd_len", r"\bsd_len\b|length SD|word-length SD"),
    ("redup_pct", r"\bredup(?:_pct)?\b|immediate repeats"),
    ("hapax", r"\bhapax(?: rate)?\b"),
    ("cross_excess", r"\bcross_excess(?:_eva)?\b|cross-space MI excess|coupling excess|\bcrossMI\b|"
                     r"(?:edge|cross-space|B|A) coupling\b|\bcoupling(?: interval)?\b"),
    ("x_edge_mi_word", r"\bx_edge_mi_word\b"),
    ("x_moran_I", r"\bx_moran_I\b|Moran(?:'s)? I\b|\bMoran\b|\bwithin-line I\b|\bI_core\b|\bmean I\b"),
    ("charwin", r"\bCHARWIN\b|char-win"),
    ("nmi", r"\bNMI\b"),
    ("p_init_enrich", r"\bp_init(?:_enrich)?\b|p-initial"),
    ("m_final_enrich", r"\bm_final(?:_enrich)?\b|m-final"),
    ("mrr", r"\bMRR\b"),
    ("ari", r"\bARI\b"),
    ("zipf_slope", r"\bZipf(?: slope)?\b"),
    ("chi2", r"\bchi2\b|χ2|χ²"),
    ("f1_residual", r"word-order residual|\bresidual\b"),
    ("mantel_r", r"\bMantel(?: r)?\b"),
    ("core_repeat_R1", r"(?<![\w_])R\(\s*1\s*\)"),
    ("prefix_order_gain", r"(?:held-out )?(?:bigram|order) gain|prefix(?:-stream)? gain|\bf4_prefix_gain\b"),
    ("edit1_parent_ratio", r"edit-1 parents?(?: excess)?|parent excess"),
    ("core_core_excess", r"core\s*(?:→|->)\s*(?:next-)?core(?: ordering)?(?: excess| statistic)?"),
    # added 2026-10-18 (parse coverage pass): z-scores, delta-AIC, R(d) at distance d > 1 (d kept in scope)
    ("z", r"(?<![\w.\-/])z(?:-score)?(?=\s*(?:=\s*)?[+\-−]?\.?\d)"),
    ("dAIC", r"\bdAIC\b|ΔAIC|\bdelta[ -]AIC\b"),
    ("mattr", r"\bMATTR\b"),
    ("core_repeat_Rd", r"(?<![\w_])R(?:_?w(?:ithin)?)?\s*\(\s*(?:d|[2-9]|[1-9]\d|\d\s*\.\.\s*\d+)\s*\)"),
]
STAT_RE = [(n, re.compile(r)) for n, r in STATS]
FOLD_STATS = {"battery_folds", "planted_recovery_folds"}

TRANSLIT = [(re.compile(r"\bZL3b\b|\bZL\b"), "ZL3b"), (re.compile(r"\bRF1b(?:-er?)?\b|\bRF\b"), "RF1b"),
            (re.compile(r"\bIT2a(?:-n)?\b|\bIT\b"), "IT2a"), (re.compile(r"\bGC2a(?:-n)?\b"), "GC2a")]
SEGMENTER = [(re.compile(r"\bS0\b"), "S0"), (re.compile(r"\bS1\b"), "S1"), (re.compile(r"\bS2\b"), "S2"),
             (re.compile(r"SlotSegmenter|\bslot\b"), "slot"), (re.compile(r"\bZattera\b"), "zattera"),
             (re.compile(r"Seg_Affix2|\baffix2\b"), "affix2"), (re.compile(r"\bidentity\b"), "identity"),
             (re.compile(r"\bwhole words\b"), "words")]
CORPUS = [(re.compile(r"\bVoynich\b|\bMS\b|\bmanuscript\b"), "voynich"),
          (re.compile(r"\bLatin\b"), "latin"), (re.compile(r"\bDante\b"), "dante"),
          (re.compile(r"\bKalevala\b"), "kalevala"), (re.compile(r"\bNibelungenlied\b|\bnib\b"), "nibelungenlied"),
          (re.compile(r"\bRoland\b"), "roland"), (re.compile(r"\bOccitan\b"), "occitan"),
          (re.compile(r"\bCaesar\b"), "caesar"), (re.compile(r"\bApicius\b"), "apicius"),
          (re.compile(r"\bDigby\b"), "digby"), (re.compile(r"\bRoget\b"), "roget"),
          (re.compile(r"\bCulpeper\b"), "culpeper"), (re.compile(r"\bCREMMA\b|\bcremma\b"), "cremma"),
          (re.compile(r"\bgibberish\b|\bgib\b"), "gibberish"), (re.compile(r"\bHebrew\b"), "hebrew"),
          (re.compile(r"\bTacuinum\b"), "tacuinum"), (re.compile(r"\bConstantinus\b"), "constantinus"),
          (re.compile(r"\bLlull\b"), "llull"), (re.compile(r"\bPriapea\b"), "priapea"),
          (re.compile(r"\bNaibbe\b"), "naibbe"), (re.compile(r"\bFaust\b"), "faust"),
          (re.compile(r"\bAugustine\b"), "augustine"), (re.compile(r"\bSteganographia\b"), "steganographia"),
          (re.compile(r"\bManzoni\b"), "manzoni"), (re.compile(r"\bForme of Cury\b"), "forme_of_cury")]
LABELS = [(r, v, "translit") for r, v in TRANSLIT] + [(r, v, "segmenter") for r, v in SEGMENTER] + \
         [(r, v, "corpus") for r, v in CORPUS]

UNIT = re.compile(r"\s*(?:(?:held-out|unseen|training|test|box-aligned|real|scored|paragraph)\s+)?(?:lines?|tokens?|tok|pages?|pairs?|draws?|shuffles?|types?|words?|entries|rows?|loci|folios?|"
                  r"images?|canvases|plants?|crops?|writers?|texts?|cells?|seeds?|quires?|blocks?|nulls?|copies|"
                  r"variants?|instances?|letters?|chars?|glyphs?|labels?|sheets?|bifolios?|illustrations?|"
                  r"trajectories|settings?|predictions?|jobs?|stars?|markers?|detections?|manuscripts?|"
                  r"permutations?|grid points?|sections?|transliterations?|hands?|generators?|subsets?|keys?|"
                  r"families|controls?|samples?|metrics?|members?|cores?|MSS|PDT|workers?|CPU|GB|s\b|min\b)\b")
NUM = re.compile(r"[+\-−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|[+\-−]?\.\d+")
PVAL = re.compile(r"(?<![\w\-])(?:p\s*(?:=|<=|>=|<|>|≤|≥)?|P\s*(?:=|<=|<|≤)|P\s+(?=0?\.\d))\s*([+\-]?\d*\.?\d+(?:\s*/\s*\d*\.?\d+)*)(?![\w])")
CI_BR = re.compile(r"\[\s*([+\-−]?\d*\.?\d+)\s*[,;]\s*([+\-−]?\d*\.?\d+)\s*\]")
CI_TXT = re.compile(r"\(\s*95\s*%\s*CI\s*([+\-−]?\d*\.?\d+)\s*(?:[-–,]|to)\s*([+\-−]?\d*\.?\d+)\s*\)")
CI_PAR = re.compile(r"\(\s*([+\-−]?\d*\.\d+)\s*[-–]\s*([+\-−]?\d*\.\d+)\s*\)")  # "OR 0.807 (0.554-1.174)"
N_EQ = re.compile(r"(?<![\w])[nN]\s*=\s*(\d[\d,]*)")
THRESH_BEFORE = re.compile(r"(?:\bbar|\bthreshold|\bband|\bcut|>=|<=|≥|≤|<|>|\bwindow|\bT_\w+)\s*$")
NULL_BEFORE = re.compile(r"(?:\bnull|\bshuffle|\bpermuted|\bbaseline|\bcontrols?)(?:\s+[\w%]+){0,3}\s*$", re.I)
VAR_EQ = re.compile(r"(?<![\w])([A-Za-zα-ωβτ][\w]{0,9})\s*=\s*\[?\s*$")
GAP_OK = {"and", "vs", "the", "with", "for", "all", "both", "mean", "median", "per", "each", "across", "under",
          "against", "excess", "folds", "fold", "raw", "native", "full", "matched", "size", "whole", "text", "real",
          "bits", "words", "cores", "core", "prefix", "suffix", "seed", "seeds", "only", "pooled", "range", "band",
          "null", "shuffle", "within", "line", "lines", "cross", "held-out", "transliterations", "transliteration"}
PRE_SKIP = re.compile(r"(?:\bParts?|\blines?|\brows?|§|\bblocks?|\bTest|\bAmendment|\bPhase|\bstage|\brung|"
                      r"\bTable|\bcolumn|\bitem|\bround|\bseeds?|\bfolios?|\bK\s?=?|\bd\s?=)\s*$")
HAND_ID = re.compile(r"\b[Hh]ands?\s*$")  # "hand 1 +8.2", "hands 2/3": a hand id (1-5), not a value
AUX_STATS = {"z"}  # printed beside another statistic: never blocks the Value cell's default statistic
Z_VAL = re.compile(r"\s*(?:=\s*)?[+\-−]?\d*\.?\d+(?:\s*/\s*[+\-−]?\d*\.?\d+)*(?:\s*(?:\.\.|–|to)\s*[+\-−]?\d*\.?\d+)?")
FOLD_UNIT = {"fold", "folds", "quire", "quires", "block", "blocks", "loqo"}
# an a/b chain followed by one of these counts something else ("24/24 points", "9/9 seeds", "35/37 held-out pages")
CHAIN_PREFIX = re.compile(r"[`'\"”)\]]*\s*(?:\([^)]{0,30}\)\s*)?(?:,\s*\d+\s*/\s*\d+[`'\"]?\s*(?:\([^)]{0,30}\)\s*)?)*")
NONFOLD_WORDS = {"points", "point", "seeds", "splits", "cells", "cell", "encodings", "languages", "ciphers", "controls",
                 "settings", "cases", "items", "hits", "events", "combos", "configurations", "models", "features",
                 "runs", "trials", "tests", "classes", "conditions", "arms", "families", "readings", "sidecars",
                 "ci", "interval", "intervals", "violations", "texts", "re-segmentations"}
FOLD_CTX = re.compile(r"\bfolds?\b|\bLOQO\b|\bquires?\b|\bblocks?\b|\bheld-out\b", re.I)


def fnum(s):
    s = s.replace("−", "-").replace(",", "").replace("+", "")
    try:
        return float(s)
    except ValueError:
        return None


def tokenize(seg, base, consumed):
    """Numeric items in seg: dicts kind single|chain|range|fold|foldchain, vals, start, end (abs)."""
    toks = []
    last_skip = -9
    for m in NUM.finditer(seg):
        a, b = m.start(), m.end()
        if any(lo <= base + a < hi for lo, hi in consumed):
            continue
        s = m.group(0)
        pre = seg[a - 1] if a > 0 else " "
        nxt = seg[b] if b < len(seg) else " "
        rng_join = False
        if s[0] in "-−" and pre.isdigit():  # "0.378-4.410": the dash is a range separator
            rng_join = True
            s = s[1:]
            a += 1
            pre = seg[a - 1]
        if a - last_skip <= 1 and pre in "–-−/":  # "results_s92.txt:285–287", "lines 15–52", "hands 2/3": second end too
            last_skip = b
            continue
        if pre == "(" and nxt == ")" and re.fullmatch(r"\d+", s):  # "1.09 (10)": an index or a count in parentheses
            continue
        if re.match(r"\s*%[\s-]*CI\b", seg[b:b + 8]):  # "95% CI": the interval's level, not a value
            continue
        if PRE_SKIP.search(seg[max(0, a - 12):a]) or \
                (re.fullmatch(r"[1-5]", s) and HAND_ID.search(seg[max(0, a - 8):a]) and seg[b:b + 1] != "."):
            last_skip = b
            continue
        if pre == "." and seg[max(0, a - 2):a] == ".." and a >= 3 and seg[a - 3].isdigit():
            pre = " "  # "+0.074..+0.655": second end of a range
        if not rng_join and (pre.isalnum() or pre in "_.:'’#$@"):
            last_skip = b
            continue
        if s[0] in "+-−" and a >= 2 and seg[a - 1].isalnum():
            continue
        if nxt.isalpha() and nxt not in "×x" or nxt == ":" and b + 1 < len(seg) and seg[b + 1].isdigit():
            if not (nxt.isalpha() and seg[b:b + 2] in ("e-",)):
                continue
        if nxt == "-" and b + 1 < len(seg) and seg[b + 1].isalpha():  # 15-quire, 4-letter
            continue
        if re.fullmatch(r"\d{4}", s) and 1000 <= int(s) <= 2100:  # years, folio counts of years
            continue
        if re.match(r"-\d{2}-\d{2}", seg[b:b + 6]):  # dates
            continue
        if VAR_EQ.search(seg[max(0, a - 12):a]):
            v = VAR_EQ.search(seg[max(0, a - 12):a]).group(1)
            if v.lower() not in ("h2", "or", "kappa", "auc", "mde", "nmi", "ari", "mrr", "z", "daic", "i"):
                continue
        toks.append(dict(s=s, v=fnum(s), a=a, b=b, rj=rng_join))
    items, i = [], 0
    while i < len(toks):
        t = toks[i]
        j = i
        chain = [t]
        while j + 1 < len(toks) and re.fullmatch(r"\s*/\s*", seg[toks[j]["b"]:toks[j + 1]["a"]]):
            chain.append(toks[j + 1])
            j += 1
        if len(chain) > 1:
            ints = all(re.fullmatch(r"\d+", c["s"]) for c in chain)
            items.append(dict(kind="intchain" if ints else "chain", vals=[c["v"] for c in chain],
                              a=base + chain[0]["a"], b=base + chain[-1]["b"]))
            i = j + 1
            continue
        if i + 1 < len(toks):
            gap = seg[t["b"]:toks[i + 1]["a"]]
            if toks[i + 1]["rj"] and gap in ("", "-", "−") or re.fullmatch(r"\s*(?:–|\.\.|to)\s*", gap):
                items.append(dict(kind="range", vals=[t["v"], toks[i + 1]["v"]], a=base + t["a"], b=base + toks[i + 1]["b"]))
                i += 2
                continue
        tail = seg[t["b"]:t["b"] + 40]
        um = UNIT.match(tail)
        items.append(dict(kind="count" if (um and not tail.lstrip().startswith("bits")) else "single",
                          vals=[t["v"]], a=base + t["a"], b=base + t["b"],
                          int=bool(re.fullmatch(r"\d+", t["s"]))))
        i += 1
    return items


def nearest_label(text, upto, kind, lo=0):
    best, pos = None, -1
    for r, v, k in LABELS:
        if k != kind:
            continue
        for m in r.finditer(text, lo, upto):
            if m.start() > pos:
                best, pos = v, m.start()
    return best


def following_list(text, at):
    """'(ZL3b/RF1b/IT2a)' or ' on ZL3b/RF1b/IT2a' right after a chain -> list of (kind, value)."""
    m = re.match(r"\s*(?:\(|on |under |for )\s*([A-Za-z0-9_\-]+(?:\s*(?:/|,)\s*[A-Za-z0-9_\-]+)+)\)?", text[at:at + 60])
    if not m:
        return None
    out = []
    for part in re.split(r"\s*(?:/|,)\s*", m.group(1)):
        lab = None
        for r, v, k in LABELS:
            if r.fullmatch(part):
                lab = (k, v)
                break
        out.append(lab or ("scope", part))
    return out


def chain_counts_folds(text, it):
    """False when an a/b chain counts something other than folds: the first three words after it (and after any
    "(label), c/d (label)" run, up to the next , ; : ( = +) name a unit that is not a fold, quire or block
    ("24/24 points", "9/9 transliteration x segmenter cells", "0/3353 CI violations"), or a chain without a
    common denominator holds counts above 50 ("2360 / 2491 / 2420")."""
    vals = it["vals"]
    if len(vals) > 2 and len(set(vals[1::2])) > 1 and max(vals) > 50:
        return False
    m = CHAIN_PREFIX.match(text, it["b"])
    tail = re.split(r"[,;:(=+]|\s\d", text[m.end():m.end() + 60], 1)[0]
    for w in re.findall(r"[A-Za-z][\w\-]*", tail)[:3]:
        w = w.lower()
        if w in FOLD_UNIT:
            return True
        if w in NONFOLD_WORDS or UNIT.fullmatch(" " + w):
            return False
    return True


def extract_numeric(text, base_src, ln, claim_id, run_id, consumed_all, default_stat=None):
    """Rows for canonical statistics found in text. default_stat: used for a text with no statistic keyword
    at all (a claim's Value cell when the claim names exactly one canonical statistic)."""
    rows = []
    if not text:
        return rows
    has_any = any(r.search(text) for n, r in STAT_RE if n not in AUX_STATS)
    clause_starts = [0] + [m.end() for m in re.finditer(r";|\.\s(?=[A-Z])", text)] + [len(text)]
    for ci in range(len(clause_starts) - 1):
        c0, c1 = clause_starts[ci], clause_starts[ci + 1]
        clause = text[c0:c1]
        kws = []
        for name, r in STAT_RE:
            for m in r.finditer(clause):
                kws.append((m.start(), m.end(), name))
        kws.sort(key=lambda x: (x[0], -(x[1] - x[0])))
        clean, last_end = [], -1
        for k in kws:
            if k[0] >= last_end:
                clean.append(k)
                last_end = k[1]
        # segments
        segs = []
        first = clean[0][0] if clean else len(clause)
        segs.append((0, first, None if has_any else default_stat))
        idx = 0
        while idx < len(clean):
            s, e, name = clean[idx]
            nxt = clean[idx + 1][0] if idx + 1 < len(clean) else len(clause)
            # "MDE AUC 0.749": a keyword with no number before the next keyword keeps the next segment
            if name in AUX_STATS:  # "z +4.5": z owns only the number(s) right after it; the rest goes back
                zm = Z_VAL.match(clause, e)
                zend = zm.end() if zm else e
                segs.append((e, zend, name))
                prev = next((k[2] for k in reversed(clean[:idx]) if k[2] not in AUX_STATS),
                            None if has_any else default_stat)
                if zend < nxt:
                    arrow = clause.find("->", zend, nxt)
                    segs.append((zend, min(nxt, zend + 160, arrow if arrow >= 0 else len(clause)), prev))
                idx += 1
                continue
            if idx + 1 < len(clean) and not NUM.search(clause[e:nxt]) and nxt - e <= 6 and \
                    clean[idx + 1][2] not in AUX_STATS:
                nxt2 = clean[idx + 2][0] if idx + 2 < len(clean) else len(clause)
                segs.append((clean[idx + 1][1], min(nxt2, clean[idx + 1][1] + 160), name))
                idx += 2
                continue
            arrow = clause.find("->", e, nxt)  # an outcome arrow ends the statistic's segment
            segs.append((e, min(nxt, e + 160, arrow if arrow >= 0 else len(clause)), name))
            idx += 1
        has_fold_ctx = bool(FOLD_CTX.search(clause))
        rows_before = len(rows)
        for s0, s1, name in segs:
            seg = clause[s0:s1]
            if not seg.strip():
                continue
            a0 = c0 + s0  # absolute offset
            consumed = []
            ps = []
            for m in PVAL.finditer(seg):
                ps.append((a0 + m.start(), [fnum(x) for x in re.split(r"\s*/\s*", m.group(1))], s0 + m.start(), a0 + m.end()))
                consumed.append((a0 + m.start(), a0 + m.end()))
            cis = []
            for r in (CI_BR, CI_TXT, CI_PAR):
                for m in r.finditer(seg):
                    cis.append((a0 + m.start(), a0 + m.end(), fnum(m.group(1)), fnum(m.group(2))))
                    consumed.append((a0 + m.start(), a0 + m.end()))
            nm = N_EQ.search(seg)
            n_val = int(nm.group(1).replace(",", "")) if nm else None
            if nm:
                consumed.append((a0 + nm.start(), a0 + nm.end()))
            items = tokenize(seg, a0, consumed)
            if n_val is None:
                for it in items:
                    if it["kind"] == "count":
                        n_val = int(it["vals"][0]) if it["vals"][0] is not None and it["vals"][0] == int(it["vals"][0]) else None
                        break
            tr_clause = {v for r, v in TRANSLIT if r.search(clause)}
            emitted_any = False
            prev_end = a0
            cut = None
            for it in items:
                if it["kind"] == "count":
                    continue
                gap = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", text[prev_end:it["a"]])
                words = [w for w in re.findall(r"[A-Za-z][A-Za-z\-']{2,}", gap)
                         if w.lower() not in GAP_OK and not any(r.fullmatch(w) for r, _, _ in LABELS)]
                if name and name not in FOLD_STATS and len(words) >= (7 if prev_end == a0 else 2):  # the statistic's run of numbers ended
                    cut = it["a"]
                    break
                prev_end = it["b"]
                rel_a = it["a"] - c0
                pre = clause[max(0, rel_a - 14):rel_a]
                scope_tag = None
                if THRESH_BEFORE.search(pre):
                    continue  # a threshold or band edge, not a measurement
                if NULL_BEFORE.search(pre):
                    scope_tag = "null"
                stat = name
                vals = it["vals"]
                fold = None
                if it["kind"] == "intchain":
                    if not chain_counts_folds(text, it) or \
                            re.search(r"\bfloor\W{0,3}$", text[max(0, it["a"] - 12):it["a"]]):
                        continue  # a count of something else, or a p floor "1/55": left in the unparsed note
                    total = None
                    m_of = re.match(r"\s*of\s+(\d+)", clause[it["b"] - c0:it["b"] - c0 + 10])
                    if len(vals) == 2 and vals[1] >= vals[0]:
                        fold = [(vals[0], vals[1])]
                    elif len(vals) % 2 == 0 and len(set(vals[1::2])) == 1 and max(vals[0::2]) <= vals[1]:
                        fold = list(zip(vals[0::2], vals[1::2]))  # "8/15 / 7/15 / 5/15"
                    else:
                        if m_of:
                            total = float(m_of.group(1))
                        else:
                            mt = re.search(r"(\d+)[- ]quire|(\d+) (?:blocks|folds)|/(\d+) folds|of (\d+) folds", clause)
                            if mt:
                                total = float(next(x for x in mt.groups() if x))
                        fold = [(v, total) for v in vals]
                    if stat is None or stat in FOLD_STATS:
                        if stat is None:
                            if not has_fold_ctx:
                                continue
                            near = clause[max(0, rel_a - 50):rel_a]
                            stat = "planted_recovery_folds" if "planted" in near else (
                                "battery_folds" if "battery" in clause else "loqo_folds")
                    labels = following_list(clause, it["b"] - c0) if len(vals) > 2 or fold is None else None
                    for k, (fp, ft) in enumerate(fold):
                        rows.append(mrow(claim_id, run_id, stat, None, None, None, None, fp, ft, clause, rel_a,
                                         labels[k] if labels and len(labels) == len(fold) else None, tr_clause,
                                         seg, scope_tag, base_src, ln, n_val, ps, k, len(fold)))
                    emitted_any = True
                    consumed_all.append((it["a"], it["b"]))
                    continue
                if stat is None or stat in FOLD_STATS:
                    continue
                if it["kind"] == "range":
                    rows.append(mrow(claim_id, run_id, stat, None, vals[0], vals[1], None, None, None, clause, rel_a,
                                     None, tr_clause, seg, "range" + (":null" if scope_tag else ""), base_src, ln,
                                     n_val, ps, 0, 1))
                elif it["kind"] == "chain":
                    labels = following_list(clause, it["b"] - c0)
                    for k, v in enumerate(vals):
                        rows.append(mrow(claim_id, run_id, stat, v, None, None, None, None, None, clause, rel_a,
                                         labels[k] if labels and len(labels) == len(vals) else None, tr_clause,
                                         seg, scope_tag, base_src, ln, n_val, ps, k, len(vals)))
                elif it.get("int") and has_fold_ctx and vals[0] is not None and vals[0] <= 50:
                    # a bare small integer in a fold/block context is a count of folds, not the statistic
                    mt = re.search(r"\bof (\d+)\b|(\d+)[- ]quire|(\d+) (?:blocks|folds)|/(\d+) folds", clause)
                    ft = float(next(x for x in mt.groups() if x)) if mt else None
                    rows.append(mrow(claim_id, run_id, stat, None, None, None, None, vals[0], ft, clause, rel_a, None,
                                     tr_clause, seg, scope_tag, base_src, ln, n_val, ps, 0, 1))
                else:
                    lo = hi = None
                    for (ca, cb, x, y) in cis:
                        if 0 <= ca - it["b"] <= 3:
                            lo, hi = x, y
                            consumed_all.append((ca, cb))
                            prev_end = max(prev_end, cb)
                    rows.append(mrow(claim_id, run_id, stat, vals[0], lo, hi, None, None, None, clause, rel_a, None,
                                     tr_clause, seg, scope_tag, base_src, ln, n_val, ps, 0, 1))
                consumed_all.append((it["a"], it["b"]))
                emitted_any = True
            if emitted_any or name:
                for pa, _, _, pe in ps:
                    consumed_all.append((pa, pe))
            # unattached intervals in a stat segment
            if name and name not in FOLD_STATS:
                for (ca, cb, x, y) in cis:
                    if cut is not None and ca >= cut:
                        continue
                    if VAR_EQ.search(text[max(0, ca - 12):ca + 1]):  # "A14=[...]" belongs to another quantity
                        continue
                    if not any(lo <= ca < hi for lo, hi in consumed_all):
                        rows.append(mrow(claim_id, run_id, name, None, x, y, None, None, None, clause, ca - c0, None,
                                         tr_clause, seg, "interval", base_src, ln, n_val, ps, 0, 1))
                        consumed_all.append((ca, cb))
        if len(rows) == rows_before:  # a printed p with no canonical statistic in its clause: statistic p_value
            tr_clause = {v for r, v in TRANSLIT if r.search(clause)}
            for m in PVAL.finditer(clause):
                a, b = c0 + m.start(), c0 + m.end()
                if any(lo <= a < hi for lo, hi in consumed_all):
                    continue
                if re.match(r"p\s*(?:<|<=|≤)\s*0?\.05\b", m.group(0)):  # a decision rule, not a result
                    continue
                vals = [fnum(x) for x in re.split(r"\s*/\s*", m.group(1))]
                for k, v in enumerate(vals):
                    if v is None or not 0 <= v <= 1:
                        continue
                    rows.append(mrow(claim_id, run_id, "p_value", None, None, None, v, None, None, clause,
                                     m.start(), None, tr_clause, clause, None, base_src, ln, None, [], k, len(vals)))
                consumed_all.append((a, b))
    return rows


def mrow(claim_id, run_id, stat, value, lo, hi, p, fp, ft, clause, at, label, tr_clause, seg, scope_tag,
         base_src, ln, n_val, ps, k, kn):
    translit = segmenter = corpus = None
    extra_scope = None
    if label:
        kind, v = label
        if kind == "translit":
            translit = v
        elif kind == "segmenter":
            segmenter = v
        elif kind == "corpus":
            corpus = v
        else:
            extra_scope = v
    # a label right after the number ("0/15 folds ZL") beats the nearest one before it
    m_after = re.match(r"[^;,()]{0,14}?\b(ZL3b|ZL|RF1b|IT2a|IT|GC2a)\b", clause[at:at + 30])
    m_after = m_after if (m_after and kn == 1 and re.match(r"[\d/+\-−. ]*(?:folds?)?\s*$",
                                                            clause[at:at + m_after.start(1)])) else None
    if translit is None:
        if m_after:
            translit = next(v for r, v in TRANSLIT if r.fullmatch(m_after.group(1)))
        else:
            translit = nearest_label(clause, at, "translit", max(0, at - 80))
        if translit is None and len(tr_clause) == 1:
            translit = next(iter(tr_clause))
    if segmenter is None:
        segmenter = nearest_label(clause, at, "segmenter", max(0, at - 80))
    if corpus is None:
        corpus = nearest_label(clause, at, "corpus", 0)
        if corpus is None and translit is not None:
            corpus = "voynich"
    # p: the p chain aligned with values, else the first single p printed after the value (within 60 chars)
    pv = None
    if ps:
        chains = [x for x in ps if len(x[1]) == kn and kn > 1]
        if chains:
            pv = chains[0][1][k]
        else:
            after = [x for x in ps if len(x[1]) == 1 and 0 < x[2] - at <= 60]
            if after:
                pv = after[0][1][0]
    sc = seg.strip()
    scope = "; ".join(x for x in [scope_tag, extra_scope and f"label={extra_scope}", sc[:200]] if x)
    return dict(claim_id=claim_id, run_id=run_id, statistic=stat, value=value, ci_lo=lo, ci_hi=hi,
                p=p if p is not None else pv, n=n_val, folds_pass=fp, folds_total=ft, call_name=None,
                call_value=None, translit=translit, segmenter=segmenter, corpus=corpus, scope=scope, line=ln,
                src=base_src)


CALL_PATTERNS = [
    re.compile(r"\b(CALL_[A-Za-z0-9_]+)\s*(?:\([^)]{0,80}\)\s*)?(?:=|:)?\s*"
               r"(True|False|TRUE|FALSE|NOT ASSESSABLE|[A-Z][A-Z_]{2,}|\d+(?:\.\d+)?)"),
    re.compile(r"\bCall\s+([A-Z0-9][A-Za-z0-9_]+)\s*=\s*(\w+)"),
    re.compile(r"\bCALL\s+([a-z]\w*)\s*=?\s*(True|False)\b"),
]
CALL_COLON = re.compile(r"\bCALLS?\s*[:=]\s*(.{1,200}?)(?=;|\"|$|\s->|\.\s)")
PAIR = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\s*(?:\([^)]{0,60}\)\s*)?=\s*([A-Za-z]+|\d+(?:\.\d+)?)")
VERDICT_LC = re.compile(r"\bverdict\s*[:=]\s*([a-z][\w\- ']{2,60}?)(?=[;,\"()]|$)")
VERDICT_RE = re.compile(r"\bVERDICT\b\s*[:=]?\s*(.{1,160}?)(?=;|\"|$|\s\(|\s->)")
OUTCOME_RE = re.compile(r"\b(NOT HOLDS|HOLDS|FAVOURED|FAVOURS [A-Z]+(?: [A-Z]+)?|PASS(?:ES)?|FAIL(?:S)?|INCONCLUSIVE|"
                        r"UNDERPOWERED|UNINFORMATIVE|POWERED|NOT ASSESSABLE|SURVIVES|FALLS|NO MATCH|MATCH|SAME|SPLIT|"
                        r"REOPENED|NOT SUPPORTED|SUPPORTED|EXCLUDED|INVALID|NEGATIVE|POSITIVE|NOT EVIDENCE|"
                        r"SIZE-DEPENDENT|BOTH RELIABLE|RELIABLE|HOLD|TIE)\b")
ARROW_RE = re.compile(r"->\s*(?!VERDICT)([A-Za-z0-9_ ']{2,60}?)(?=[;,\"()]|$)")


def extract_calls(text, base_src, ln, claim_id, run_id, consumed_all):
    rows = []
    if not text:
        return rows

    def add(stat, name, val, a, b):
        rows.append(dict(claim_id=claim_id, run_id=run_id, statistic=stat, value=None, ci_lo=None, ci_hi=None,
                         p=None, n=None, folds_pass=None, folds_total=None, call_name=name, call_value=val.strip(),
                         translit=None, segmenter=None, corpus=None, scope=text[max(0, a - 60):b + 60].strip()[:240],
                         line=ln, src=base_src))
        consumed_all.append((a, b))

    seen = set()
    for r in CALL_PATTERNS:
        for m in r.finditer(text):
            if (m.group(1), m.start()) in seen:
                continue
            seen.add((m.group(1), m.start()))
            add("call", m.group(1), m.group(2), m.start(), m.end())
    for m in CALL_COLON.finditer(text):
        body = m.group(1)
        pairs = list(PAIR.finditer(body))
        if pairs:
            for pm in pairs:
                if pm.group(1).startswith("CALL_"):
                    continue
                add("call", pm.group(1), pm.group(2), m.start(1) + pm.start(), m.start(1) + pm.end())
        else:
            add("call", "CALL", body, m.start(), m.end())
    for m in VERDICT_RE.finditer(text):
        v = m.group(1).strip(" :,")
        if not v or re.match(r"^(block|line|lines|R\d|,)", v):
            continue
        add("verdict", "VERDICT", v, m.start(), m.end())
    for m in VERDICT_LC.finditer(text):
        add("verdict", "verdict", m.group(1), m.start(), m.end())
    for m in OUTCOME_RE.finditer(text):  # printed outcome words (upper case) in the quoted claim
        if any(lo <= m.start() < hi for lo, hi in consumed_all):
            continue
        add("verdict", "outcome", m.group(1), m.start(), m.end())
    for m in ARROW_RE.finditer(text):
        v = m.group(1).strip()
        if re.search(r"\b(FAIL|PASS|HOLDS?|NOT|MATCH|none|NONE|SUPPORTED|INVALID|EXCLUDED|FAVOURS?)\b", v):
            add("verdict", "->", v, m.start(), m.end())
    return rows


def extract_outcomes(text, base_src, ln, claim_id, run_id, consumed_all):
    """Upper-case outcome words only (for the Value cell)."""
    rows = []
    for m in OUTCOME_RE.finditer(text or ""):
        if any(lo <= m.start() < hi for lo, hi in consumed_all):
            continue
        rows.append(dict(claim_id=claim_id, run_id=run_id, statistic="verdict", value=None, ci_lo=None, ci_hi=None,
                         p=None, n=None, folds_pass=None, folds_total=None, call_name="outcome",
                         call_value=m.group(1), translit=None, segmenter=None, corpus=None,
                         scope=text[max(0, m.start() - 60):m.end() + 60].strip()[:240], line=ln, src=base_src))
        consumed_all.append((m.start(), m.end()))
    return rows


RES_CALL = re.compile(r"\b(CALL(?:_[A-Za-z0-9_]+)?)(?:\s+([a-z]\w*))?\s*(?:\(([^)]{0,120})\))?\s*[:=]\s*(\S.*)")
RES_VERDICT = re.compile(r"\b((?:[A-Za-z0-9\-]+\s+){0,3}VERDICT(?:_\w+)?)\b\s*(?:\([^)]*\))?\s*[:=|]?\s*(.*)")


def results_call_rows(path, run_id):
    rows = []
    try:
        lines = rd(path).split("\n")
    except OSError:
        return rows
    src = rel(path)
    for i, line in enumerate(lines, 1):
        if "CALL" not in line and "VERDICT" not in line:
            continue
        s = line.strip()
        got = False
        for m in re.finditer(r"\b(CALL_[A-Za-z0-9_]+)\s*(?:\([^)]{0,120}\)\s*)?[:=]\s*([^\s,;()]+)", s):
            v = m.group(2)
            if v.startswith("---"):
                continue
            rows.append(dict(claim_id=None, run_id=run_id, statistic="call", value=None, ci_lo=None, ci_hi=None, p=None,
                             n=None, folds_pass=None, folds_total=None, call_name=m.group(1), call_value=v,
                             translit=None, segmenter=None, corpus=None, scope=s[:300], line=i, src=f"{src}:{i}"))
            got = True
        if not got:
            m = re.search(r"\bCALL(?:\s+([a-z]\w*))?\s*[:=]\s*(\S.*)", s)
            if m and not m.group(2).startswith("---"):
                rows.append(dict(claim_id=None, run_id=run_id, statistic="call", value=None, ci_lo=None, ci_hi=None,
                                 p=None, n=None, folds_pass=None, folds_total=None,
                                 call_name="CALL" + ("_" + m.group(1) if m.group(1) else ""),
                                 call_value=m.group(2)[:200], translit=None, segmenter=None, corpus=None,
                                 scope=s[:300], line=i, src=f"{src}:{i}"))
        if "VERDICT" in s and "CALL_SHOWS" not in s[:0]:
            m = RES_VERDICT.search(s)
            if m:
                val = m.group(2).strip(" =:")
                if not val or set(val) <= set("=-# "):
                    for nxt in lines[i:i + 4]:
                        if nxt.strip() and not set(nxt.strip()) <= set("=-# "):
                            val = nxt.strip()
                            break
                if val:
                    rows.append(dict(claim_id=None, run_id=run_id, statistic="verdict", value=None, ci_lo=None,
                                     ci_hi=None, p=None, n=None, folds_pass=None, folds_total=None,
                                     call_name=m.group(1).strip()[-60:], call_value=val[:300], translit=None,
                                     segmenter=None, corpus=None, scope=s[:300], line=i, src=f"{src}:{i}"))
    return rows


def unparsed_numbers(text, consumed):
    out = []
    for m in NUM.finditer(text or ""):
        a, b = m.start(), m.end()
        pre = text[a - 1] if a else " "
        if pre.isalnum() or pre in "_-:.'`$#@" and not m.group(0)[0] in "+-−":
            continue
        if b < len(text) and (text[b].isalpha() or text[b] in "-:" and b + 1 < len(text) and text[b + 1].isalnum()):
            continue
        if re.fullmatch(r"\d{4}", m.group(0)):
            continue
        if any(lo <= a < hi for lo, hi in consumed):
            continue
        out.append(text[max(0, a - 25):b + 3].replace("\n", " "))
    return out


# ----------------------------------------------------------------------------- main build
def build(conn):
    g, marks, pending_rows = build_graph_tables(conn)

    claims = parse_claims()
    decisions = parse_decisions()
    learnings = parse_learnings()
    opens = parse_open()

    scripts = scripts_index()
    root_results = sorted(p for p in glob.glob(os.path.join(ROOT, "results_*.txt")) if not skipped(p))
    coll = collision_runs(scripts, root_results)

    runs = {}

    def R(rid, src):
        if not rid:
            return None
        if rid not in runs:
            runs[rid] = dict(run_id=rid, owner=None, script=None, script_sha=None, stub=None, stub_ok=None,
                             stub_mtime=None, results=None, results_ctime=None, admissibility=None,
                             impl_independent=None, decision=None, src=src, _results=[], _claims=[], _notes=[])
        return runs[rid]

    # 1. root results files
    for p in root_results:
        stem = os.path.basename(p)[8:-4]
        rid = run_of_results_name(stem, coll)
        R(rid, rel(p))["_results"].append(p)
    # 2. runs/*/
    for d in sorted(glob.glob(os.path.join(ROOT, "runs", "*"))):
        if not os.path.isdir(d) or skipped(d):
            if os.path.basename(d) == SKIP:
                R(SKIP, "runs/" + SKIP)
            continue
        b = os.path.basename(d)
        m = re.fullmatch(r"roach-r(\d+)", b)
        if m:
            rid = "r" + m.group(1)
            r = R(rid, rel(d))
            r["owner"] = "roach"
            main = os.path.join(d, f"results_{rid}.txt")
            if os.path.exists(main):
                r["_results"].append(main)
            sc = os.path.join(d, f"{rid}.py")
            if os.path.exists(sc):
                r["script"] = sc
            st = os.path.join(d, f"{rid}.prereg.sha256")
            if os.path.exists(st):
                r["stub"] = st
        elif b == "roach-r1r2-raw":
            for rid in ("r1", "r2"):
                r = R(rid, rel(d))
                r["owner"] = "roach"
                main = os.path.join(d, f"results_{rid}.txt")
                if os.path.exists(main):
                    r["_results"].append(main)
                if os.path.exists(os.path.join(d, "prep.py")):
                    r["script"] = os.path.join(d, "prep.py")
                r["_notes"].append("no prereg stub in runs/roach-r1r2-raw (PREREG_LOG.txt only)")
        elif re.fullmatch(r"[a-z]+\d+\w*", b):
            R(b if b in coll else prefix(b), rel(d))
    # 3. CLAIMS rows -> run ids
    for c in claims:
        rids = []
        head = re.split(r"[\"“]", c["claim"] or "", 1)[0]
        dbs = re.findall(r"\bdb-s\d+\b", head)
        roach = bool(re.search(r"\broach\b", head, re.I))
        if dbs:  # Daybreak claims cite codex_lab files as `.../results_sNN_*.txt`
            rids = list(dict.fromkeys(dbs))
        for pth in re.findall(r"[A-Za-z]:/[^\s`;,]+?\.txt|(?:\.\.\./|runs/[\w\-]+/)?results_[\w.\-]+?\.txt",
                              c["source"] or ""):
            if dbs:
                break
            if pth.startswith(".../"):
                m = re.search(r"results_(?:db_)?s(\d+)", pth)
                rid = ("db-s" + m.group(1)) if m else None
            elif roach and re.fullmatch(r"results_r\d+\.txt", pth):
                rid = pth[8:-4]
            else:
                rid = run_of_path(pth, coll)
            if rid and rid not in rids:
                rids.append(rid)
        if not rids:
            m = re.match(r"\s*(?:[Rr]oach\s+r(\d+))", head) or (
                re.search(r"\b(?:roach|Replication)\b", head) and re.match(r"\s*R(\d+)\b", (c["claim"] or "")[len(head) + 1:]))
            if m:
                rids.append("r" + m.group(1))
            else:
                m = re.search(r"\bdb-s\d+\b", head)
                if m:
                    rids.append(m.group(0))
                else:
                    m = re.match(r"\s*([A-Z]\d+[a-z]?)\b", head)
                    if m and int(c["cid"][2:]) not in range(200, 300):
                        t = m.group(1).lower()
                        rids.append(("lead-" + t) if re.fullmatch(r"r\d+", t) else t)
        c["run_id"] = rids[0] if rids else None
        c["runs"] = rids
        for rid in rids:
            R(rid, f"{rel(CLAIMS_MD)}:{c['ln']}")["_claims"].append(c)
    # 4. graph pending rows
    for prow in pending_rows:
        rtxt = prow["run"] or ""
        m = re.search(r"\bdb-s\d+\b", rtxt) or None
        rid = m.group(0) if m else None
        if not rid:
            m = re.search(r"roach\s+r(\d+)", rtxt)
            rid = ("r" + m.group(1)) if m else None
        if not rid:
            m = re.match(r"\s*([a-z]+\d+\w*)", rtxt)
            rid = norm_token(m.group(1), coll) if m else None
        if not rid:
            continue
        r = R(rid, prow["src"])
        r["_pending"] = prow
    # 5. TEAM-HANDOFF run-id lists
    for rid, d in handoff_runs(coll).items():
        r = R(rid, d["src"])
        r["_handoff"] = d
        if d.get("results") and os.path.exists(d["results"]) and not r["_results"]:
            r["_results"].append(d["results"])

    # owners, scripts, stubs, admissibility
    decision_refs = {}
    for d in decisions:
        txt = " ".join(x or "" for x in (d["title"], d["body"], d["refs"]))
        toks = set(re.findall(r"\bdb-s\d+\b", txt))
        toks |= {"s" + x for x in re.findall(r"(?<![\w-])s(\d+)\b", txt)}
        toks |= {"r" + x for x in re.findall(r"(?<![\w-])r(\d+)\b", txt)}
        for t in toks:
            decision_refs.setdefault(t, []).append(d["did"])

    stub_index = {os.path.basename(p)[:-len(".prereg.sha256")]: p
                  for p in glob.glob(os.path.join(ROOT, "*.prereg.sha256")) if not skipped(p)}
    for rid, r in runs.items():
        if rid == SKIP:
            r["_notes"].append("running (TEAM-HANDOFF); files not opened by rule")
            r["owner"] = r["owner"] or "lead"
            continue
        pend = r.get("_pending") or {}
        ho = r.get("_handoff") or {}
        if rid.startswith("db-"):
            r["owner"] = "Daybreak"
        elif r["owner"] is None:
            o = pend.get("owner") or ho.get("owner")
            if not o:
                for c in r["_claims"]:
                    head = re.split(r"[\"“]", c["claim"] or "", 1)[0]
                    if "Argon" in head:
                        o = "Argon"
                        break
            if o and o.startswith("Argon") and o != "Argon":
                r["_notes"].append("owner as recorded: " + o)
            if not o and rid in coll:
                r["_notes"].append("owner not recorded (prefix shared with another run); default lead")
            o = "Argon" if o and o.startswith("Argon") else ("roach" if o and o.startswith("roach") else o)
            r["owner"] = "lead" if (not o or o in ("voynich-08", "lead")) else o
        # script and stub for lead-tree runs
        if not rid.startswith(("db-",)) and r["owner"] != "roach":
            base = rid[5:] if rid.startswith("lead-") else rid
            if base in scripts:
                cands = [base]
            else:
                cands = sorted(s for s in scripts if prefix(s) == base and s not in coll)
            if cands:
                with_stub = [s for s in cands if s in stub_index]
                outs = [os.path.basename(x) for x in r["_results"]]
                writes = [s for s in cands if any(o in rd(scripts[s]) for o in outs)] if outs else []
                pick = (with_stub and with_stub[0]) or (writes and writes[0]) or cands[0]
                r["script"] = scripts[pick]
                if len(cands) > 1:
                    r["_notes"].append("other scripts with this prefix: " + ", ".join(s for s in cands if s != pick))
                if pick in stub_index:
                    r["stub"] = stub_index[pick]
            if not r["stub"]:
                st = [k for k in stub_index if prefix(k) == base and (base in coll or k not in coll)]
                if len(st) == 1:
                    r["stub"] = stub_index[st[0]]
        if r["script"] and os.path.exists(r["script"]):
            r["script_sha"] = sha256(r["script"])
        if r["stub"]:
            r["stub_mtime"] = ts(os.path.getmtime(r["stub"]))
            ok, detail = stub_check(r["stub"])
            r["stub_ok"] = ok
            if detail:
                r["_notes"].append("stub check: " + detail)
        if r["_results"]:
            prim = os.path.join(ROOT, f"results_{rid}.txt")
            if prim not in r["_results"]:
                prim = min(r["_results"], key=lambda x: (len(os.path.basename(x)), x))
            r["results"] = prim
            r["results_ctime"] = ts(os.stat(prim).st_ctime)
        # admissibility
        texts = [((c["status"] or "") + " " + (c["used"] or "")) for c in r["_claims"]]
        claim_txt = " ".join((c["claim"] or "") for c in r["_claims"])
        alltxt = " ".join(texts)
        adm = None
        decs = list(decision_refs.get(rid, []))
        if rid in REJECTED:
            adm = "rejected"
            decs.append(REJECTED[rid])
        elif pend.get("state") == "rejected":
            adm = "rejected"
        elif r["owner"] and r["owner"].startswith("Argon"):
            passed = re.search(r"lead (?:integrity )?audit (?:PASS|passe)|VERIFIED by lead audit|admissible by lead audit",
                               alltxt, re.I)
            adm = "admissible" if passed else "quarantined"
            if passed and re.search(r"\bscope\b", alltxt, re.I):
                adm = "admissible-with-scope"
            decs.append("D-065")
        elif re.search(r"NOT ASSESSABLE", claim_txt) and not re.search(r"\bVERIFIED\b.*\bOK\b(?!.*NOT)", ""):
            adm = "not-assessable" if re.search(r"VERDICT: CALL_\w+ = NOT ASSESSABLE|CALL_SHOWS_F40_CORE = NOT ASSESSABLE",
                                                claim_txt) else None
        if adm is None and r["_claims"]:
            if re.search(r"no stub frozen", alltxt) and re.search(r"\bHOLD\b", claim_txt):
                adm = "hold"
            elif any(re.search(r"\bVERIFIED\b", c["status"] or "") for c in r["_claims"]):
                adm = "admissible-with-scope" if re.search(r"\bscope\b", alltxt, re.I) else "admissible"
            elif any(re.search(r"\brejected\b", t, re.I) for t in texts):
                adm = "rejected"
        r["admissibility"] = adm
        r["decision"] = ", ".join(sorted(set(decs), key=lambda x: int(x[2:]))) or None
        if r["owner"] == "roach" or rid == "db-s114":
            r["impl_independent"] = 1
        elif rid.startswith("db-"):
            r["impl_independent"] = None
        else:
            r["impl_independent"] = 0

    # ---- measurements
    meas = []
    claim_rows = []
    for c in claims:
        src = f"{rel(CLAIMS_MD)}:{c['ln']}"
        cons_claim, cons_val = [], []
        m1 = extract_calls(c["claim"], src, c["ln"], c["cid"], c["run_id"], cons_claim)
        m2 = extract_numeric(c["claim"], src, c["ln"], c["cid"], c["run_id"], cons_claim)
        named = {n for n, r in STAT_RE if r.search(c["claim"] or "")} - FOLD_STATS - AUX_STATS
        m3 = extract_numeric(c["value"], src, c["ln"], c["cid"], c["run_id"], cons_val,
                             default_stat=next(iter(named)) if len(named) == 1 else None)
        m3 += extract_outcomes(c["value"], src, c["ln"], c["cid"], c["run_id"], cons_val)
        meas += m1 + m2 + m3
        un = unparsed_numbers(c["claim"], cons_claim) + unparsed_numbers(c["value"], cons_val)
        note = "; ".join(x for x in [
            f"value: {c['value']}" if c["value"] else "",
            f"used in: {c['used']}" if c["used"] else "",
            f"other runs: {', '.join(c['runs'][1:])}" if len(c["runs"]) > 1 else "",
            ("unparsed: " + " | ".join(un)) if un else ""] if x) or None
        claim_rows.append(dict(claim_id=c["cid"], run_id=c["run_id"], text=c["claim"], results=c["source"],
                               lines=c["method"], verified=c["status"], date=c["date"], note=note, src=src))
    for rid, r in runs.items():
        for p in r["_results"]:
            if os.path.exists(p) and not skipped(p):
                meas += results_call_rows(p, rid)
    for i, m in enumerate(meas, 1):
        m["id"] = i

    # ---- write
    create(conn, "runs", ["run_id TEXT PRIMARY KEY", "owner TEXT", "script TEXT", "script_sha TEXT", "stub TEXT",
                          "stub_ok INTEGER", "stub_mtime TEXT", "results TEXT", "results_ctime TEXT",
                          "admissibility TEXT", "impl_independent INTEGER", "decision TEXT", "note TEXT"])
    rows = []
    for rid in sorted(runs, key=run_sort_key):
        r = runs[rid]
        rows.append(dict(run_id=rid, owner=r["owner"], script=rel(r["script"]) if r["script"] else None,
                         script_sha=r["script_sha"], stub=rel(r["stub"]) if r["stub"] else None, stub_ok=r["stub_ok"],
                         stub_mtime=r["stub_mtime"], results=rel(r["results"]) if r["results"] else None,
                         results_ctime=r["results_ctime"], admissibility=r["admissibility"],
                         impl_independent=r["impl_independent"], decision=r["decision"],
                         note="; ".join(r["_notes"]) or None, src=r["src"]))
    insert(conn, "runs", rows)
    create(conn, "claims", ["claim_id TEXT PRIMARY KEY", "run_id TEXT", "text TEXT", "results TEXT", "lines TEXT",
                            "verified TEXT", "date TEXT", "note TEXT"])
    insert(conn, "claims", claim_rows)
    create(conn, "measurements", ["id INTEGER PRIMARY KEY", "claim_id TEXT", "run_id TEXT", "statistic TEXT",
                                  "value REAL", "ci_lo REAL", "ci_hi REAL", "p REAL", "n INTEGER", "folds_pass REAL",
                                  "folds_total REAL", "call_name TEXT", "call_value TEXT", "translit TEXT",
                                  "segmenter TEXT", "corpus TEXT", "scope TEXT", "line INTEGER"])
    insert(conn, "measurements", meas)
    create(conn, "learnings", ["lid TEXT PRIMARY KEY", "belief TEXT", "result TEXT", "evidence TEXT", "change TEXT",
                               "date TEXT"])
    insert(conn, "learnings", learnings)
    create(conn, "decisions", ["did TEXT PRIMARY KEY", "date TEXT", "title TEXT", "body TEXT", "refs TEXT",
                               "state TEXT"])
    insert(conn, "decisions", decisions)
    create(conn, "open_questions", ["oid TEXT PRIMARY KEY", "question TEXT", "source TEXT", "state TEXT"])
    insert(conn, "open_questions", opens)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_meas_stat ON measurements(statistic)")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_meas_run ON measurements(run_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_meas_claim ON measurements(claim_id)")
    conn.commit()


# ----------------------------------------------------------------------------- self-test
def _report(conn):
    q = lambda s: conn.execute(s).fetchall()  # noqa: E731
    for t in ("runs", "claims", "measurements", "findings", "finding_lines", "hypotheses", "points", "assumptions",
              "pending", "learnings", "decisions", "open_questions"):
        print(f"{t:15s} {q(f'SELECT COUNT(*) FROM {t}')[0][0]}")
    tot, hit = q("""SELECT COUNT(*), SUM(EXISTS(SELECT 1 FROM measurements m WHERE m.claim_id=c.claim_id))
                    FROM claims c WHERE CAST(substr(claim_id,3) AS INTEGER) >= 300""")[0]
    num = q("""SELECT SUM(EXISTS(SELECT 1 FROM measurements m WHERE m.claim_id=c.claim_id
                    AND m.statistic NOT IN ('call','verdict')))
               FROM claims c WHERE CAST(substr(claim_id,3) AS INTEGER) >= 300""")[0][0]
    print(f"claims c-300+: {hit}/{tot} = {hit / tot:.1%} with >=1 measurement ({num} with a numeric statistic)")
    print("by statistic:", q("SELECT statistic, COUNT(*) FROM measurements GROUP BY 1 ORDER BY 2 DESC"))
    print("stub failures:")
    for r in q("SELECT run_id, stub, note FROM runs WHERE stub_ok = 0 ORDER BY run_id"):
        print("  ", r[0], r[1], (r[2] or "")[:160])
    print("runs with a stub, ok:", q("SELECT COUNT(*) FROM runs WHERE stub_ok=1")[0][0],
          "of", q("SELECT COUNT(*) FROM runs WHERE stub IS NOT NULL")[0][0])
    nc = q("""SELECT run_id FROM runs r WHERE results IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM claims c WHERE c.run_id = r.run_id
                               OR (' ' || c.note) LIKE '%other runs:%' || r.run_id || '%') ORDER BY run_id""")
    print(f"runs with results but no claim ({len(nc)}):", " ".join(x[0] for x in nc))
    print("admissibility:", q("SELECT admissibility, COUNT(*) FROM runs GROUP BY 1"))
    fl = q("SELECT run_id FROM runs WHERE stub_mtime > results_ctime ORDER BY run_id")
    print(f"flag, stub last written after the results file was created ({len(fl)}; re-freezes and fixture "
          "runs also do this):", " ".join(x[0] for x in fl))


if __name__ == "__main__":
    import sqlite3
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "vkb", "test_evidence.sqlite")
    assert os.path.basename(out) != "vkb.sqlite", "self-test never writes vkb.sqlite"
    conn = sqlite3.connect(out)  # every table is dropped and re-created by build()
    build(conn)
    _report(conn)
    conn.close()
