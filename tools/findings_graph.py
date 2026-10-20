"""Findings graph: the canonical map of what we found, what each finding rests on, and what it points to.

Source of truth: workflow/FINDINGS-GRAPH.yaml (hand-edited, one entry per finding).
Generated view:  workflow/FINDINGS-MAP.md (never edit by hand).
Process:         workflow/TRIANGULATION.md.

    python tools/findings_graph.py check    # integrity + triangulation rules; exit 1 on any error
    python tools/findings_graph.py render   # check, then write workflow/FINDINGS-MAP.md (--allow-missing: absent cited files warn)
    python tools/findings_graph.py gaps     # cheapest missing triangulation axis per load-bearing finding
    python tools/findings_graph.py sprawl   # orphans: unmapped claims, unreferenced results, stray root docs
"""
import os, re, subprocess, sys
from collections import Counter, defaultdict
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "workflow", "FINDINGS-GRAPH.yaml")
OUT = os.path.join(ROOT, "workflow", "FINDINGS-MAP.md")
CLAIMS = os.path.join(ROOT, ".inventory", "registers", "CLAIMS.md")
CMAP = os.path.join(ROOT, "workflow", "CONSTRAINTS-MAP.md")
DECS = os.path.join(ROOT, ".inventory", "registers", "DECISIONS.md")

INDEPENDENT = {"impl", "physical", "external"}   # axes that leave our own pipeline
WEIGHT = {"strong": 3, "moderate": 2, "weak": 1}
NET = {"strong": 3, "moderate": 2, "weak": 0}   # weak = compatible, not discriminating: listed, not weighed
GRADE_W = {"TRIANGULATED": 1.0, "CORROBORATED": 0.67, "SINGLE": 0.34, "CONTESTED": 0.0}


# --allow-missing: a cited file that is absent is a warning, not an error (copies without third-party texts).
ALLOW_MISSING = "--allow-missing" in sys.argv


def rd(p):
    return open(p, encoding="utf-8").read()


class UniqueKeyLoader(yaml.SafeLoader):
    """safe_load that refuses a mapping with the same key twice (yaml would keep the last one silently)."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for k, _ in node.value:
            key = self.construct_object(k, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", k.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)


def load():
    g = yaml.load(rd(GRAPH), Loader=UniqueKeyLoader)
    for k in ("axes", "hypotheses", "assumptions", "findings", "pending"):
        g[k] = g.get(k) or {}
    return g


def grade(f):
    """Triangulation grade of one finding from its evidence lines."""
    lines = [l for l in f.get("lines", []) if not l.get("unverified")]
    agree = {l["axis"] for l in lines if l.get("agrees", True)}
    open_dis = [l for l in lines if not l.get("agrees", True) and not l.get("resolved")]
    if open_dis:
        return "CONTESTED", agree
    if len(agree) >= 3 and agree & INDEPENDENT:
        return "TRIANGULATED", agree
    if len(agree) >= 2:
        return "CORROBORATED", agree
    return "SINGLE", agree


def discharged(f):
    """Assumptions a finding no longer rests on because an agreeing, verified line tested it directly."""
    return {x for l in f.get("lines", []) if l.get("agrees", True) and not l.get("unverified") for x in l.get("discharges", [])}


def risky_of(f, g):
    d = discharged(f)
    return [x for x in f.get("rests_on", []) if x not in d and g["assumptions"].get(x, {}).get("status") in ("at-risk", "flipped")]


def check(g):
    err, warn = [], []
    claims = set(re.findall(r"^\| `(c-\d+)` \|", rd(CLAIMS), re.M))
    cmap = rd(CMAP)
    arows = set(re.findall(r"^\| (A\d+) \|", cmap, re.M))
    dots = set(re.findall(r"^(\d+)\. \*\*", cmap, re.M))
    decs = set(re.findall(r"^\| (D-\d+) \|", rd(DECS), re.M))
    H, X, F, P = g["hypotheses"], g["assumptions"], g["findings"], g["pending"]
    axes = set(g["axes"])
    covered = set()

    def ref_ok(where, path):
        p = path.split("#")[0].split(" ")[0]
        if p and not os.path.exists(os.path.join(ROOT, p)):
            (warn if ALLOW_MISSING else err).append(f"{where}: file not found: {p}")

    for fid, f in F.items():
        w = fid
        for k in ("title", "statement", "status"):
            if not f.get(k):
                err.append(f"{w}: missing {k}")
        for c in f.get("claims", []):
            if c not in claims:
                err.append(f"{w}: claim {c} not in CLAIMS.md")
        for m in f.get("map", []):
            if m.startswith("A"):
                if m in arows:
                    covered.add(m)
                else:
                    err.append(f"{w}: map row {m} not in CONSTRAINTS-MAP")
            elif m.startswith("dot") and m[3:] not in dots:
                err.append(f"{w}: {m} not in CONSTRAINTS-MAP")
        for x in f.get("rests_on", []):
            if x not in X:
                err.append(f"{w}: rests_on unknown assumption {x}")
        if f.get("load_bearing") and "rests_on" not in f:
            err.append(f"{w}: load-bearing finding must state rests_on (use [] if none)")
        for l in f.get("lines", []) + f.get("controls", []):
            if "axis" in l and l["axis"] not in axes:
                err.append(f"{w}: unknown axis {l['axis']}")
            if l.get("ref"):
                ref_ok(w, l["ref"])
            if l.get("claim") and l["claim"] not in claims:
                err.append(f"{w}: line claim {l['claim']} not in CLAIMS.md")
        if f.get("kind") == "absence" and f.get("status") != "withdrawn":
            if not [c for c in f.get("controls", []) if c.get("matched")]:
                msg = f"{w}: absence finding lacks a powered positive control at matched conditions"
                (warn if f.get("status") == "at-risk" else err).append(msg)
        for p in f.get("points", []):
            if p.get("h") not in H:
                err.append(f"{w}: points to unknown hypothesis {p.get('h')}")
            if p.get("rel") not in ("for", "against", "excludes"):
                err.append(f"{w}: bad rel {p.get('rel')}")
            if p.get("strength") not in WEIGHT:
                err.append(f"{w}: bad strength {p.get('strength')}")
        for r in f.get("related", []):
            if r.get("f") not in F:
                err.append(f"{w}: related to unknown finding {r.get('f')}")
        for d in f.get("decisions", []):
            if d not in decs:
                err.append(f"{w}: decision {d} not in DECISIONS.md")
        if f.get("status") not in ("standing", "at-risk", "superseded", "withdrawn"):
            err.append(f"{w}: bad status {f.get('status')}")
        gr, _ = grade(f)
        risky = risky_of(f, g)
        if risky and f.get("status") == "standing":
            warn.append(f"{w}: rests on at-risk {risky} but status is 'standing'")
        if gr == "CONTESTED" and f.get("status") == "standing":
            err.append(f"{w}: CONTESTED by an unresolved disagreeing line but status is 'standing'")
    for a in sorted(arows - covered, key=lambda s: int(s[1:])):
        err.append(f"CONSTRAINTS-MAP row {a} is not represented by any finding")
    for pid, p in P.items():
        for t in p.get("decides", []):
            if t not in F and t not in X and t not in H:
                err.append(f"{pid}: decides unknown node {t}")
        if p.get("state") == "filed" and not os.path.exists(os.path.join(ROOT, p.get("result", ""))):
            err.append(f"{pid}: filed but result file missing")
    for xid, x in X.items():
        if x.get("status") not in ("verified", "unverified", "at-risk", "flipped"):
            err.append(f"{xid}: bad status {x.get('status')}")
    for hid, h in H.items():
        if not any(p.get("h") == hid for f in F.values() for p in f.get("points", [])):
            warn.append(f"{hid}: no finding points to this hypothesis")
    return err, warn


def scoreboard(g):
    rows = defaultdict(lambda: {"for": [], "against": [], "w_for": 0.0, "w_against": 0.0})
    for fid, f in g["findings"].items():
        if f.get("status") in ("superseded", "withdrawn"):
            continue
        gr, _ = grade(f)
        risky = risky_of(f, g)
        gw = GRADE_W[gr] * (0.5 if risky else 1.0)
        for p in f.get("points", []):
            r = rows[p["h"]]
            tag = f"{fid}({p['strength'][0]}{'*' if risky else ''})"
            side = "for" if p["rel"] == "for" else "against"
            r[side].append(tag + ("!" if p["rel"] == "excludes" else ""))
            r["w_" + side] += NET[p["strength"]] * gw
    return rows


ORDER = ["impl", "physical", "seg", "split", "order", "method", "data", "external"]


def gaps(g):
    out = []
    for fid, f in g["findings"].items():
        if not f.get("load_bearing") or f.get("status") in ("superseded", "withdrawn"):
            continue
        gr, have = grade(f)
        if gr == "TRIANGULATED" and not risky_of(f, g):
            continue
        missing = [a for a in ORDER if a not in have]
        need = missing if have & INDEPENDENT else [a for a in missing if a in INDEPENDENT] + [a for a in missing if a not in INDEPENDENT]
        pend = [pid for pid, p in g["pending"].items() if fid in p.get("decides", []) and p.get("state") != "filed"]
        out.append((fid, gr, sorted(have), need[:3], pend))
    return out


def stamp():
    try:
        return subprocess.check_output(["date", "+%Y-%m-%d %H:%M %Z"]).decode().strip()
    except Exception:
        return "unstamped"


def cell(s):
    return str(s).replace("|", "/").replace("\n", " ")


def status_section(g):
    """Section 0: one entry point. Judgement fields come from status_board (lead-edited); the lists are computed."""
    F, P, sb = g["findings"], g["pending"], g.get("status_board") or {}
    L = ["## 0. Status at a glance (start here)", ""]
    if sb:
        L += [f"Board updated {sb.get('updated', '?')}. {sb.get('headline', '')}", ""]
        st = sb.get("strongest") or {}
        if st:
            fid = st.get("finding")
            L += [f"**Strongest supported finding: {fid}, {cell(F.get(fid, {}).get('title', ''))}** ({grade(F[fid])[0] if fid in F else '?'}).",
                  f"- Why: {st.get('why', '')}", f"- Limits: {st.get('limits', '')}", f"- Evidence: {st.get('evidence', '')}", ""]
        na = sb.get("next_action") or {}
        if na:
            L += [f"**Next approved action ({na.get('decision', '')}):** {na.get('what', '')}", f"- Approval: {na.get('approved', '')}", ""]
    acc, dis, rev = [], [], []
    for k, f in F.items():
        gr = grade(f)[0]
        risk = risky_of(f, g)
        unv = sum(1 for l in f.get("lines", []) if l.get("unverified"))
        cl = ", ".join(f.get("claims", [])[:4]) or "—"
        if f.get("status") in ("superseded", "withdrawn"):
            continue
        if gr == "CONTESTED" or f.get("status") == "at-risk" or risk:
            why = "; ".join(x for x in [gr if gr == "CONTESTED" else "", f"status {f.get('status')}" if f.get("status") == "at-risk" else "",
                                         f"rests on at-risk {', '.join(risk)}" if risk else ""] if x)
            dis.append(f"| {k} | {cell(f['title'])} | {gr} | {why} | {cl} |")
        elif gr in ("TRIANGULATED", "CORROBORATED"):
            acc.append(f"| {k} | {cell(f['title'])} | {gr} | {'yes' if f.get('load_bearing') else ''} | {cl} |")
        else:
            dis.append(f"| {k} | {cell(f['title'])} | {gr} | one axis only | {cl} |")
        if unv:
            rev.append(f"| {k} | {unv} | " + ", ".join(sorted({pk for pk, p in P.items() if k in (p.get('decides') or []) and p.get('state') in ('briefed', 'claimed', 'running')})) + " |")
    wd = [f"| {k} | {cell(f['title'])} | {f.get('status')} |" for k, f in F.items() if f.get("status") in ("superseded", "withdrawn")]
    wd += [f"| {k} (test {p.get('run')}) | {cell(p.get('question', ''))[:140]} | rejected: {cell(p.get('note', ''))[:120]} |" for k, p in P.items() if p.get("state") == "rejected"]
    asg = [f"| {k} | {p.get('run')} | {cell(p.get('owner', ''))} | {p.get('state')} | {', '.join(p.get('decides') or [])} |"
           for k, p in P.items() if p.get("state") in ("briefed", "claimed", "running")]
    L += ["Accepted = standing, CORROBORATED or TRIANGULATED, no at-risk assumption (accepted inside this project's gate; no external acceptance implied).",
          "Disputed = CONTESTED, at-risk, resting on an at-risk assumption, or single-axis. Grades: section 2; evidence lines: section 7.", "",
          f"**Accepted ({len(acc)})**", "", "| F | Finding | grade | load-bearing | claims |", "|---|---|---|---|---|"] + acc
    L += ["", f"**Disputed or not yet supported ({len(dis)})**", "", "| F | Finding | grade | why | claims |", "|---|---|---|---|---|"] + dis
    L += ["", f"**Withdrawn or rejected ({len(wd)})**", "", "| id | what | state |", "|---|---|---|"] + (wd or ["| — | none | |"])
    L += ["", f"**Pending review: findings with lines that stopped counting ({len(rev)})** (POST-HOC or unverified; they count again only after the named replication)", "",
          "| F | lines not counting | replication assigned |", "|---|---|---|"] + rev
    L += ["", f"**Currently assigned ({len(asg)})**", "", "| P | run | owner | state | decides |", "|---|---|---|---|---|"] + (asg or ["| — | none | | | |"])
    if sb.get("lanes"):
        L += ["", "**Lanes and reply routes**", "", "| lane | owner | writes | reply |", "|---|---|---|---|"]
        L += [f"| {cell(x.get('lane', ''))} | {cell(x.get('owner', ''))} | {cell(x.get('writes', ''))} | {cell(x.get('reply', ''))} |" for x in sb["lanes"]]
    if sb.get("reviews"):
        L += ["", "**Reviews of other lanes' work (reported complete is not accepted; accepted is not used)**", "", "| who | what | lead disposition | why |", "|---|---|---|---|"]
        L += [f"| {cell(x.get('who', ''))} | {cell(x.get('what', ''))} | {cell(x.get('lead', ''))} | {cell(x.get('why', ''))} |" for x in sb["reviews"]]
    return L + [""]


def render(g):
    H, X, F, P = g["hypotheses"], g["assumptions"], g["findings"], g["pending"]
    L = [f"# Findings map (generated {stamp()}; do not edit)", "",
         "Source: `workflow/FINDINGS-GRAPH.yaml`. Regenerate: `python tools/findings_graph.py render`. Process: `workflow/TRIANGULATION.md`.",
         "Numbers live in `.inventory/registers/CLAIMS.md`; narrative in `workflow/CONSTRAINTS-MAP.md`. This page is the",
         "relationship layer: each finding's independent evidence lines, the assumptions it rests on, and where it points.", ""]
    L += status_section(g)
    L += ["## 1. Where the findings point", "",
          "Weight = strength (strong 3, moderate 2; weak links are compatibility only, listed but weighed 0) × triangulation (TRIANGULATED 1.0, CORROBORATED 0.67, SINGLE 0.34,",
          "CONTESTED 0), halved (`*`) when the finding rests on an at-risk assumption; `!` = the finding excludes the hypothesis as built.",
          "This ranks weight of evidence, not probability. Sorted by net weight.", "",
          "| H | Hypothesis | status | weight for / against | findings for | findings against |", "|---|---|---|---|---|---|"]
    sb = scoreboard(g)
    for hid in sorted(H, key=lambda h: -(sb[h]["w_for"] - sb[h]["w_against"])):
        h, r = H[hid], sb[hid]
        L.append(f"| {hid} | {cell(h['name'])} | {h['status']} | {r['w_for']:.1f} / {r['w_against']:.1f} | "
                 f"{', '.join(r['for']) or '—'} | {', '.join(r['against']) or '—'} |")
    L += ["", "## 2. Findings by triangulation grade", "",
          "TRIANGULATED = agreeing evidence lines on ≥3 axes, at least one leaving our pipeline (impl, physical, external).",
          "CORROBORATED = ≥2 axes. SINGLE = 1 axis. CONTESTED = a disagreeing line not yet resolved. ◆ = load-bearing.", "",
          "| F | Finding | grade | axes | rests on (**at risk**, ~~discharged by a direct test~~) | map | status |", "|---|---|---|---|---|---|---|"]
    rank = {"TRIANGULATED": 0, "CORROBORATED": 1, "SINGLE": 2, "CONTESTED": 3}
    for fid in sorted(F, key=lambda k: (rank[grade(F[k])[0]], int(k[2:]))):
        f = F[fid]; gr, ax = grade(f)
        rk, dc = risky_of(f, g), discharged(f)
        ro = ", ".join(f"**{x}**" if x in rk else (f"~~{x}~~" if x in dc else x) for x in f.get("rests_on", [])) or "—"
        lb = " ◆" if f.get("load_bearing") else ""
        L.append(f"| {fid}{lb} | {cell(f['title'])} | {gr} | {', '.join(sorted(ax))} | {ro} | {', '.join(f.get('map', [])) or '—'} | {f['status']} |")
    L += ["", "## 3. Assumptions and what falls with them", "",
          "| X | Assumption | status | findings resting on it | decided by |", "|---|---|---|---|---|"]
    for xid, x in X.items():
        dep = [fid for fid, f in F.items() if xid in f.get("rests_on", [])]
        by = [pid for pid, p in P.items() if xid in p.get("decides", []) and p.get("state") != "filed"]
        L.append(f"| {xid} | {cell(x['statement'])} | {x['status']} | {', '.join(dep) or '—'} | {', '.join(by) or cell(x.get('basis', '—'))} |")
    L += ["", "## 4. Relationships between findings", ""]
    for fid, f in F.items():
        for r in f.get("related", []):
            L.append(f"- {fid} **{r['rel']}** {r['f']}" + (f": {r['note']}" if r.get("note") else ""))
    L += ["", "## 5. Triangulation gaps (load-bearing findings not yet triangulated, or resting on an at-risk assumption)", "",
          "| F | grade | axes it has | cheapest missing axes | pending tests |", "|---|---|---|---|---|"]
    for fid, gr, have, need, pend in gaps(g):
        L.append(f"| {fid} | {gr} | {', '.join(have) or '—'} | {', '.join(need) or '—'} | {', '.join(pend) or '**none: design one**'} |")
    L += ["", "## 6. Pending tests and what they decide", "",
          "| P | run | owner | state | decides | question |", "|---|---|---|---|---|---|"]
    for pid, p in P.items():
        L.append(f"| {pid} | {p['run']} | {p['owner']} | {p.get('state', 'running')} | {', '.join(p.get('decides', []))} | {cell(p['question'])} |")
    L += ["", "## 7. Finding detail", ""]
    for fid, f in F.items():
        gr, _ = grade(f)
        L.append(f"### {fid}: {f['title']} ({gr}, {f['status']})")
        L.append("")
        L.append(f"{f['statement'].strip()}")
        L.append("")
        if f.get("claims"):
            L.append(f"- Claims: {', '.join(f['claims'])}")
        for l in f.get("lines", []):
            mark = "agrees" if l.get("agrees", True) else ("disagrees, resolved: " + l["resolved"] if l.get("resolved") else "**disagrees (unresolved)**")
            uv = " (unverified, not counted)" if l.get("unverified") else ""
            L.append(f"- Line [{l['axis']}] {l['by']}: {mark}{uv}" + (f" ({l['ref']})" if l.get("ref") else ""))
        for c in f.get("controls", []):
            L.append(f"- Control: {c['what']} ({'matched' if c.get('matched') else 'NOT matched'})" + (f" ({c['ref']})" if c.get("ref") else ""))
        for p in f.get("points", []):
            L.append(f"- Points {p['rel']} {p['h']} ({p['strength']})" + (f": {p['why']}" if p.get("why") else ""))
        L.append("")
    L += ["## 8. Diagram (moderate and strong links; dashed = rests on an at-risk assumption)", "", "```mermaid", "graph LR"]
    for hid, h in H.items():
        L.append(f'  {hid.replace("-", "")}(["{hid} {h["short"]}"])')
    for fid, f in F.items():
        if f.get("status") in ("superseded", "withdrawn"):
            continue
        risky = risky_of(f, g)
        for p in f.get("points", []):
            if WEIGHT[p["strength"]] < 2:
                continue
            arrow = "-.->" if risky else "-->"
            L.append(f'  {fid.replace("-", "")}["{fid}"] {arrow}|{p["rel"]}| {p["h"].replace("-", "")}')
    L += ["```", ""]
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")


def sprawl(g):
    claims_txt = rd(CLAIMS)
    claims = re.findall(r"^\| `(c-\d+)` \|", claims_txt, re.M)
    linked = set()
    for f in g["findings"].values():
        linked |= set(f.get("claims", []))
        linked |= {l["claim"] for l in f.get("lines", []) if l.get("claim")}
    sup = set(re.findall(r"^\| `(c-\d+)` \|[^\n]*supersed", claims_txt, re.M | re.I))
    linked |= set((g.get("docs") or {}).get("standalone_claims", {}) or {})
    recent = [c for c in claims if int(c[2:]) >= 300 and c not in linked and c not in sup]
    graph_txt = rd(GRAPH)
    results = sorted(f for f in os.listdir(ROOT) if re.match(r"results_.*\.txt$", f))
    corpus = claims_txt + graph_txt + rd(os.path.join(ROOT, "TEAM-HANDOFF.md"))

    def run_of(r):  # results_s18_cremma_X.txt -> s18 ; results_p4d1_core_order.txt -> p4d1
        return r[len("results_"):-4].split("_")[0].split(".")[0]
    runs = defaultdict(list)
    for r in results:
        runs[run_of(r)].append(r)
    ok_orphans = set(((g.get("docs") or {}).get("orphan_results_ok") or {}).keys())
    unref = []
    for run, files in sorted(runs.items()):
        if not any(f in corpus for f in files) and f"results_{run}" not in corpus:
            unref += [f for f in files if f not in ok_orphans]
    docs = g.get("docs") or {}
    declared = set(docs.get("canonical", [])) | set((docs.get("superseded") or {}).keys()) | set(docs.get("historical", []))
    stray = sorted(f for f in os.listdir(ROOT) if f.endswith(".md") and f not in declared)
    print(f"claims c-300+ not linked to any finding: {len(recent)}")
    print("  " + " ".join(recent))
    print(f"results_*.txt whose run is referenced by none of CLAIMS, graph, TEAM-HANDOFF: {len(unref)} of {len(results)}")
    for r in unref:
        print("  " + r)
    print(f"root *.md not declared canonical/superseded/historical in the graph: {len(stray)}")
    for m in stray:
        print("  " + m)
    # duplicate ids (D-074/Phase 8.1 id rule): every register row id and every pending run id must be unique
    reg = os.path.join(ROOT, ".inventory", "registers")
    dups = []
    for name, pat in (("CLAIMS.md", r"^\| `(c-\d+)` \|"), ("LEARNINGS.md", r"^\| (L-\d+) \|"),
                      ("DECISIONS.md", r"^\| (D-\d+) \|"), ("OPEN.md", r"^\| (O-\d+) \|")):
        ids = re.findall(pat, rd(os.path.join(reg, name)), re.M)
        dups += [f"{name}:{i}" for i, n in Counter(ids).items() if n > 1]
    run_ids = [p.get("run") for p in (g.get("pending") or {}).values() if p.get("run")]
    dups += [f"pending run {i}" for i, n in Counter(run_ids).items() if n > 1]
    print(f"duplicate ids in registers or pending runs: {len(dups)}")
    for d in dups:
        print("  " + d)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    g = load()
    if cmd == "sprawl":
        sprawl(g)
        return
    err, warn = check(g)
    for w in warn:
        print("WARN ", w)
    for e in err:
        print("ERROR", e)
    if cmd == "gaps":
        for row in gaps(g):
            print(*row)
    if err:
        print(f"{len(err)} error(s)")
        sys.exit(1)
    if cmd == "render":
        render(g)
        print("wrote", os.path.relpath(OUT, ROOT))
    print(f"ok: {len(g['findings'])} findings, {len(g['hypotheses'])} hypotheses, {len(g['assumptions'])} assumptions, {len(g['pending'])} pending")


if __name__ == "__main__":
    main()
