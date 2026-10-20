> **Snapshot of 2026-10-19.** The research is paused and this is a handover copy. Status lines, queues, assignments and "next" actions below describe the team at that moment and are historical. Start at the repository's `README.md`.

Inventory: read `INVENTORY.md` first — every tool, research file, finding, report, equation, and plan with status; archive candidates are left in place and marked. Regenerate with `python ~/.claude/skills/curate/curate.py run --project .`.

## Canonical map (Phase 8.3, 2026-10-19 10:10): one home per kind of fact

Edit only the canonical home. Derived views are rebuilt and never hand-edited. If a derived view and its home disagree, the home wins. If a home and a `results_*.txt` disagree, the results file wins.

| Fact kind | Canonical home (hand-edited) | Derived views (never edit) |
|---|---|---|
| Raw measurements | `results_*.txt`, `runs/<id>/results*` (immutable) | VKB `measurements`, `corpus_stats` |
| Cited numbers (claims) | `.inventory/registers/CLAIMS.md` (c-id) | VKB `claims` |
| Learnings | `.inventory/registers/LEARNINGS.md` (L-id) | VKB `learnings` |
| Decisions | `.inventory/registers/DECISIONS.md` (D-id; D-066 is the run log) | VKB `decisions` |
| Open questions, gaps, queue | `.inventory/registers/OPEN.md` (O-id) | VKB `open_questions` |
| Findings, hypotheses, assumptions (X) | `workflow/FINDINGS-GRAPH.yaml` | `workflow/FINDINGS-MAP.md`, VKB findings tables |
| Plan assumptions (U), stage, phase log | `workflow/PLAN.md` | none |
| Runs and run ids | `TEAM-HANDOFF.md` claim lines plus `runs/<id>/` folders (id rule below) | VKB `runs` |
| Published page facts | `data/external/page-facts/<pull>/facts.tsv` | VKB `page_facts` |
| External items and intake classes | `data/external/intake/*.tsv` | VKB `external_items`, `team_files` |
| Team comms | `<team-comms>` (<team-comms>) | `workflow/comms/` is a mirror of lead-sent messages |
| Methods | `.inventory/registers/METHODS.md`, plus `workflow/TRIANGULATION.md` for filing rules | none |
| Tools | script docstrings | `INVENTORY.md`, `.inventory/registers/TOOLS.md` (runtime notes) |
| Inventory | root `INVENTORY.md` (curate) | `workflow/curation/*` |

Per-folio questions: `python tools/vkb/queries/folio_dossier.py <folio>` (one-page dossier), or `python tools/vkb/query.py` over `folios`, `page_facts`, `panel_images`, `loci`, `tokens`. Team work outside the repo: VKB `team_files` and `external_items`.

Findings and how they relate: `workflow/FINDINGS-MAP.md` (generated from `workflow/FINDINGS-GRAPH.yaml`). Every result is filed by `workflow/TRIANGULATION.md`; run `python tools/findings_graph.py render` and `sprawl` before reporting. Do not start new synthesis or status files (D-058).

**Id rule (Phase 8.1, 2026-10-19 09:50):** run ids carry the owner's prefix: lead `s`, Daybreak `db-s`, roach `r`, Grok Bot `gk-`, Voynich Expert `ve-`, Eve/Voynich Analyst `vx`, Argon `ar-`, Muse `mu-`; any other owner registers a prefix in TEAM-HANDOFF first. Claim a run id atomically by creating `runs/<id>/` (mkdir fails if it exists) and then adding the claim line in TEAM-HANDOFF; an id whose folder exists is taken. Register rows (c-, L-, D-, O- in .inventory/registers) and FINDINGS-GRAPH edits are written by the lead session only; other sessions send rows through <team-comms> and the lead files them. `python tools/findings_graph.py sprawl` reports duplicate ids and must show 0.

## Start here (new agent, 5 minutes)

1. `workflow/PLAN.md`: the `Current stage:` line and the latest Phase log entries say what is running and what is next.
2. `workflow/FINDINGS-MAP.md` **section 0** (status at a glance): strongest supported finding with limits and evidence, next approved action, and lists of what is accepted, disputed, rejected, pending review and assigned, plus lanes and reply routes. Then section 1 (scoreboard) and section 2 (grades).
3. `.inventory/registers/DECISIONS.md` rows **D-072** (governing strategy: external bridges before any semantic prediction), **D-075** (post-hoc runs, roach replication queue) and **D-066** (run log: frozen designs, approvals, stopping rules). Rows D-063 to D-065 explain why some results are rejected.
4. `.inventory/registers/LEARNINGS.md`: theme index at the top; method lessons in `workflow/research/learnings-audit-2026-10-18.md` (top 10 bind every new run).
5. `TEAM-HANDOFF.md`: claim a run id before starting ("Free for anyone" marker); the run-id alias map separates lead `sNN` from Daybreak `db-sNN`.

**Speed rule (D-085, Jon 2026-10-19 12:58: 'we are being extremely pedantic ... fix this immediately'). Two tiers.**
- **Explore (the default):** any read-only probe on data we already hold. Run it now and do it in minutes, with no stub, fixture, isolation audit, verifier, approval or comms round-trip. Label it EXPLORATORY, keep the script and output under runs/explore/, and add one line to OPEN or LEARNINGS. It never moves the scoreboard. A null means 'move on'.
- **Confirm (only for scoreboard moves):** when a probe looks real, or a claim would change a grade or be cited, apply the binding rules below, once, to that one result. Blind human or agent reading packets are confirmatory only; prefer published editions and existing transcriptions over new blind reads.
- Anyone may run an explore probe without asking. Astra schedules confirm runs. Opus reviews confirm designs and results only, not probes.

Binding rules: before designing any run, pull what is already published or catalogued for those pages (`data/external/page-facts/`, Zandbergen, Stolfi, Reeds, papers, forums) and use it as a line or skip the run (Jon 2026-10-19, D-066 dd); pre-register (hash stub, LF, frozen before real data, verify with `grep -v "^#" STUB | tr -d '\r' | sha256sum -c -`); synthetic fixture and a positive control first; file the printed call, never the prose; if a stub lists the same file twice (an amendment), the last uncommented line is binding and the earlier one should be marked `# superseded:`; never edit a script named in a stub, even its comments (D-071); never overwrite or delete a results file (a change is a new run id); `impl` means code independent of this tree; no result moves the scoreboard until an independent replication or the lead audit passes (TRIANGULATION.md). Team comms go through <team-comms> (`<team-comms>`); compute: share the CPU (about 4 workers, BelowNormal), prefer the RTX 5080; roach (`\roach`) takes blind replications and offload.
