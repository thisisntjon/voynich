# Cleanup Phase 1 execution plan — federated safety skeleton

**Date:** 2026-10-19  
**Authority:** approved cleanup roadmap and Jon's standing approval  
**Constraint:** no evidence relocation, deletion, upstream edit, or <team-comms> edit

## Step 1 — Freeze contracts and pre-intervention state

Create `workflow/cleanup/phase1/` and record:

- Phase 1 schema/version metadata;
- SHA-256, size, and timestamp of each banner target before modification;
- reference/dependency matches for each target;
- scanner path, version, and SHA-256;
- repository-split authority evidence.

Implement `tools/cleanup_phase1.py` with subcommands for registry validation, receipt validation, question/key validation, freeze verification, and coverage-state checks. Add isolated fixtures in `tests/test_cleanup_phase1.py` that prove invalid acceptance promotion, duplicate receipt IDs, missing evidence anchors, undeclared coverage states, path escape, and changed frozen files fail loudly.

Before any fresh scan, pin and review the predecessor organization evidence rather than silently replacing it: upstream `workflow/curation/inventory.jsonl`, upstream `.inventory/registers/TOMBSTONES.md`, and this workspace's historical `MANIFEST.sha256`. Record what each predecessor can and cannot establish. Obtain an Opus receipt confirming Daybreak's exact writable paths and non-overlap boundary. Log every applied change with old path, new path, reason, recovery method, and verification in the Phase 1 change ledger.

## Step 2 — Freeze the 24-question bank and answer key

Write the public scorer packet:

- `workflow/cleanup/phase1/cold-start/questions.jsonl`;
- `workflow/cleanup/phase1/cold-start/SCORING.md`;
- `workflow/cleanup/phase1/cold-start/FREEZE.sha256`.

Build `answer-key.jsonl` first in a task-specific temporary directory outside the workspace and record its SHA-256 in the sealed freeze record without exposing its path to scorers. Every answer element cites the canonical authority at one cutoff with source hash and locator. The frozen bank records hard cases, invariants, weights, source-open limits, and accepted variants. Copy the byte-identical key into `workflow/cleanup/phase1/cold-start/` only after both blind responses are final; the recorded pre-baseline hash must match.

## Step 3 — Measure the blind pre-banner baseline

Give two clean agents, spawned without conversation history, only the workspace start path, scorer instructions, and questions. Disable web use, forbid the task-specific temporary key location, and require read-only local evidence. Preserve their raw responses and source-open logs under `workflow/cleanup/phase1/cold-start/baseline/<scorer-id>/` only after each scorer finishes, so one scorer cannot see the other's work.

Grade independently against the frozen key, preserve disagreements, and produce a baseline scorecard. This baseline is descriptive; it cannot be retroactively changed when upstream state changes.

## Step 4 — Build and validate the federated root registry and receipt primitives

Write the versioned registry at `workflow/inventory/root-registry/v1/` with one evidenced row for every known body and exactly one coverage state: `MANIFESTED`, `POINTER_ONLY`, `INACCESSIBLE`, `MISSING`, or `EXCLUDED`. Generate a human view from the JSONL.

Write the noncanonical receipt schema and examples under `workflow/cleanup/receipts/daybreak/`. Receipt IDs use exclusive-created `db-ir-<UUIDv7>` identities. The validator must reject upstream dispositions without an upstream entity ID, authority path/hash, observed time, and owner assertion.

## Step 5 — Apply local authority redirects after dependency preflight

Create a compact local `AGENTS.md`. Prepend a compact historical-workspace banner to `README.md`, `TEAM-HANDOFF.md`, root `PLAN.md`, and `LEADS-AND-FINDINGS.md`, preserving their prior contents below. Record `MANIFEST.sha256` as a historical cutoff through adjacent metadata without editing it.

The banner identifies upstream `AGENTS.md` and upstream `workflow/FINDINGS-MAP.md` section 0 as the current project entry points, local `workflow/PLAN.md` as cleanup state, and the prepared/delivered/executed/audited versus filed/accepted distinction. Re-run target hashes and dependency checks and preserve the before/after map.

## Step 6 — Create the final metadata cutoff

Use the pinned research-inventory scanner for two fresh metadata-only scans into `workflow/inventory/workspace-cutoff/`, excluding only the scanner output, default environment/cache names, `.uv-cache`, `.uv-python`, `kraken_deps`, and `kraken_site`. Do not exclude mixed evidence trees.

Validate both generations, compare A to B, and label the accepted result:

- `stable_cutoff` only if the comparison reports zero new, missing, and changed entries;
- otherwise `live_capture`, with every delta preserved and no completeness upgrade.

Record enumeration coverage, hash coverage (zero by metadata-first design), exclusions, errors, and top-level reconciliation separately.

## Step 7 — Verify and close

Run:

1. `pytest tests/test_cleanup_phase1.py`;
2. all `cleanup_phase1.py` validators;
3. research-inventory `verify` on both scans and `compare` across them;
4. freeze verification for the question bank and pre-banner records;
5. a scope check proving no upstream, <team-comms>, or evidence-path mutation was performed.

Produce `workflow/cleanup/phase1/PHASE1-RESULT.md` with artifacts, checks, coverage limits, assumption outcomes, and inherited work. Update `workflow/PLAN.md` immediately if a load-bearing assumption changes.

## Done when

- All Phase 1 `Produces:` artifacts exist and their integrity pins validate.
- Every known root/body has a validated coverage row and explicit unknowns.
- Two baseline scorers completed the frozen bank without seeing the key.
- All five local entry points route correctly and historical bytes remain recoverable from recorded pre-banner hashes/copies.
- The two-scan result is honestly labelled stable or live.
- No evidence file moved or disappeared, and no upstream/<team-comms> file changed by this phase.
- Phase 1 tests and validators pass from a clean invocation.
- The predecessor Forge/curation inventory, tombstone/archive record, and historical workspace manifest are pinned and their limits stated before any fresh scan.
- Opus has acknowledged the exact Daybreak path boundary, and every applied change is recoverable through the cleanup change ledger.

## Roadmap delta

The phase sequence remains unchanged. Phase 1 now uses 24 questions rather than 20 and adds receipt primitives because the investigation showed that accepted-versus-delivered confusion and run-ID collisions are current failure modes. Phase 2 still owns semantic intake reconciliation; Phase 3 still owns post-change retrieval scoring.

## Bounded handoff on 2026-10-19

Jon narrowed Daybreak to file/artifact organization and instructed handoff then stop. Applied local routing and the requested lab index are documented in `workflow/cleanup/phase1/BOUNDED-RESULT.md`. README routing is deferred because it is a control-data input. The broader phase completion criteria above remain unmet; no whole-project completeness or space-reclamation claim is made. Opus owns canonical status and intake acceptance.
