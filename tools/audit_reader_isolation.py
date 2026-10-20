"""Audit a blind reader's isolation from its real Claude Code transcript (subagents/agent-<id>.jsonl).

The per-task .output files under the temp tasks folder can be empty, so grepping them proves nothing (L-371).
This parses the reader's own tool_use calls only, not the prompt, which names forbidden paths as prohibitions.
Usage: python tools/audit_reader_isolation.py AGENT_ID ALLOWED_DIR_REGEX OWN_OUTPUT[,OWN_OUTPUT...] [FORBID_REGEX]
Prints each tool call that writes a non-own file, mentions a forbidden pattern, or touches a repo path outside the
allowed folder, then "AUDIT_CLEAN" or "AUDIT_FLAGS n" (flags still need a human read: cd into a parent dir is benign).
"""
import json, re, sys

BASE = "<home>/.claude/projects/<agent-project>/<session>/subagents/"
DEFAULT_FORBID = r"yonichmanuscript|transcription_gt|alphabet|PROTOCOL|known_answer\.py|reading_pilot\.py|fontana|schulte|http"


def main():
    aid, allowed, outs = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    forbid = re.compile(sys.argv[4] if len(sys.argv) > 4 else DEFAULT_FORBID, re.I)
    calls = []
    for line in open(BASE + f"agent-{aid}.jsonl", encoding="utf-8"):
        try:
            m = json.loads(line).get("message", {})
        except ValueError:
            continue
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            calls += [(c["name"], json.dumps(c["input"])) for c in m["content"] if c.get("type") == "tool_use"]
    flags = []
    for tool, inp in calls:
        if tool in ("Write", "Edit"):
            if not any(o in inp for o in outs):
                flags.append(("write-other", tool, inp[:200]))
            continue
        txt = inp
        for o in outs:
            txt = txt.replace(o, "")
        if forbid.search(txt):
            flags.append(("forbidden", tool, inp[:200]))
        for p in re.findall(r"[A-Za-z]:[\/]+[^\"' ]+|/c/[^\"' ]+", inp):
            if "voynich" in p and not re.search(allowed, p) and not any(o in p for o in outs) and "Temp" not in p:
                flags.append(("outside-allowed", tool, p[:200]))
    print(f"{aid}: {len(calls)} tool calls")
    for f in flags:
        print("  ", f)
    print("AUDIT_CLEAN" if not flags else f"AUDIT_FLAGS {len(flags)}")


if __name__ == "__main__":
    main()
