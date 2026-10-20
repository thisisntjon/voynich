# Continuing this work on your own

*For an AI agent (or a person) picking the research up from this repository alone. Snapshot 2026-10-19.*

The project ran as a team: a lead session, an execution lead, replication agents and a message bus between them. [`record/AGENTS.md`](record/AGENTS.md) is that team's rulebook and is kept as evidence of how results were produced. Some of its rules cannot apply to you; this page says which, and what to do instead.

## Your first hour

1. Read [`README.md`](README.md), then [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md): the live explanations, the unsecured assumptions, and the briefed tests nobody ran.
2. Before testing anything, check [`DEAD-ENDS.md`](DEAD-ENDS.md) and search [`record/.inventory/registers/LEARNINGS.md`](record/.inventory/registers/LEARNINGS.md) for the idea (theme index at the top).
3. Fetch and rebuild the data ([`README.md`](README.md), "Reproduce a result"), then rerun one finding's results file to confirm your setup.

## Where to start: the newest open leads

From [`record/.inventory/registers/OPEN.md`](record/.inventory/registers/OPEN.md), newest first; each names its evidence so far. Most can be probed with data the README's commands fetch.

- **O-086**: Method gap: are F-40's and F-41's cross-line-avoidance numbers line-edge vocabulary? Astra exploratory (runs/explore/drawing_gap_repetition_20261019.*, exact words, no cores): true line-return repeats 4/6/8 (ZL3b/RF1b/IT2a). … Evidence so far: runs/explore/drawing_gap_repetition_20261019.* (yonichmanuscript); s87_core_layer_genre.py:57-58 (filing time not recorded; the row's own stamp is below)
- **O-083**: EXPLORATORY (D-085, Astra): do single labels recur as joined 2-3-word sequences in the body text? Label-compound concordance over ZL single labels: 736 label instances; 86 match some body join somewhere; 3 match on the same page. No enrichment claim is made. Opus checked the two anchors in VKB. … Evidence so far: lab/runs/explore/label_compound_concordance_20261019.*; 2026-10-19 13:11
- **O-081**: EXPLORATORY (D-085, Astra, ZL3b, not confirmatory): does adjacent-line word recurrence drop across marked paragraph breaks? At adjacent lines in section S: yes, within .008052 vs across .005421 (circular-shift p .002, 25 pages), and with the top-20 words excluded .005850 vs .003087 (p .014). … Evidence so far: lab/runs/explore/paragraph_recurrence_20261019.*, paragraph_interior_20261019.*; 2026-10-19 13:04
- **O-079**: EXPLORATORY (D-085): do zodiac nymph labels line up by position across signs at ANY ring start or direction? No. The best-alignment match sum is at the null in ZL3b, RF1b and IT2a, both exact and edit<=1 (p 0.13-0.66); 27 of 250 distinct ZL3b labels occur on more than one page. … Evidence so far: runs/explore/zodiac_label_alignment_probe_20261019.txt; 2026-10-19 12:58
- **O-078**: Two dependencies for any Egerton transfer design (D-082 d). (1) The 390-box manifest yonichmanuscript/codex_lab/acquisition/egerton747_crop_manifest_draft.json is marked DRAFT_MANUAL_ANNOTATION_NOT_QC_PASSED; … Evidence so far: evidence pointers sent to Astra 19:50:12Z; 2026-10-19 12:50
- **O-077**: tools/audit_reader_isolation.py can miss isolation breaches. (1) An output counts as the reader's own if its name appears anywhere in the tool input, so a Write to another file passes when its text mentions RESPONSE.csv. … Evidence so far: ASTRA-INDEPENDENT-ISOLATION-REVIEW-S133-FINAL-20261019.md; D-082(f); 2026-10-19 12:41

## Rules from AGENTS.md that still apply

- Never edit or overwrite a `results_*.txt` file or a script a stub pins; a change is a new run.
- Pre-register a confirmatory test: hash the script and design into a `*.prereg.sha256` before it reads real data; run a planted-answer fixture (positive control) first.
- Report the printed call of a test, not a paraphrase of it.
- Check what is already published for the pages and question first ([`record/data/page-facts/`](record/data/page-facts/), [`record/data/SOURCES.tsv`](record/data/SOURCES.tsv), the library catalogue).
- Two tiers: quick read-only probes (label them EXPLORATORY, keep them under [`record/runs/explore/`](record/runs/explore/), never cite them as findings) and confirm runs (the full rules, once, for a result that would change a grade).

## Rules that applied only inside the team

- Messages through the team's message bus (shown redacted as `<team-comms>`): there is no message bus here. Write your notes into your run folder.
- "Register rows are written by the lead session only": you are the custodian of your own copy. Add rows to the registers and the graph yourself, and say in the row that you are a new contributor.
- Run-id prefixes (`s`, `db-s`, `r`, `gk-` …) belong to the original team. Pick a new prefix of your own (for example `x-`) and create `runs/<prefix><n>/` before you start.
- [`record/AGENTS.md`](record/AGENTS.md) says to regenerate [`record/INVENTORY.md`](record/INVENTORY.md) with a curation tool that is not in this repository; treat [`record/INVENTORY.md`](record/INVENTORY.md) as a snapshot.
- roach's replication scripts expect roach's own folder layout: run `python tools/roach_layout.py` to rebuild it under `roach-root/`.
- "Astra schedules", "Opus reviews", roach replications, the RTX 5080 and CPU sharing: team roles and machines. Replicate your own important results with independently written code, and say so.

## Filing a result

1. Results file in `runs/<id>/`; cite every number you use as a new claim row in [`record/.inventory/registers/CLAIMS.md`](record/.inventory/registers/CLAIMS.md) (next free `c-` id).
2. Add the evidence line to the finding in [`record/workflow/FINDINGS-GRAPH.yaml`](record/workflow/FINDINGS-GRAPH.yaml) (axis, by, ref, claim, agrees), then `python tools/findings_graph.py render --allow-missing` and `python tools/findings_graph.py sprawl` (0 duplicates).
3. Record what you learned, including a null, as an `L-` row; record a choice as a `D-` row.

Scale of what is here: 51 findings, 582 claims, 308 learnings, 88 decisions, 86 open rows, 619 results files.
