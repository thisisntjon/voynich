# Independent support audit: Phase 1 measurement validity

Author: Codex support session, 2026-10-17. Scope: read-only review of the Phase 1
design plus isolated synthetic checks and one cached XML page; not a CREMMA scoring
run, a new decipherment hypothesis, or an amendment to the approved roadmap.

Reviewed `workflow/phases/phase-1.md`, stamped 20:05 PDT, SHA256
`113a7385d05e943b420634affe67e947dccd710b70f5537393bbdc36f58c75e0`.
Evidence: `support_phase1_audit.py` and `support_phase1_audit.json` beside this note.
The JSON records code, helper and source hashes, seed, examples and measured outputs.

## Recommended checks before freezing s18

1. **Do not let a low pooled JSD alone establish that scribal controls lack the
   effect.** Synthetic manuscript A has 100 lines `ax bx bx`; B has 100 lines
   `bx ax ax`. Initial-versus-interior JSD is **1.0 in each manuscript, 0.0 pooled**.
   This is exact cancellation, also reproduced with the project's existing
   `a2_position.stats`, independently of the support helper. It does not demonstrate
   cancellation in CREMMA. Retain the planned per-manuscript rows, but make them
   load-bearing: preregister how heterogeneity, manuscript-weighted within-manuscript
   effects and leave-one-manuscript-out pooling qualify the primary verdict.
   Calibrate small samples before interpreting their raw JSD (item 4).

2. **Resolve internal punctuation before defining the token stream.** The literal
   planned tokenizer leaves `facit.aliud` and `ꝑtinet.aliud` as single tokens.
   On cached `Arras-861/056r.xml`, 12 of 70 MainZone lines have different token
   counts under that tokenizer versus the support punctuation-delimited tokenizer.
   This is a source-format observation, not proof that every punctuation mark is a
   word boundary. Freeze an explicit delimiter policy with reviewed fixtures;
   replace accepted delimiters with boundaries, rather than deleting them and
   joining words. Report token counts and changed-line counts. Do not silently
   reconstruct unmarked word breaks across physical lines.

3. **Treat abbreviation normalization as a sensitivity, not invisible cleanup.**
   The planned removal of combining marks discards unresolved abbreviation
   information. In a synthetic base-plus-mark glyph test, lines `ãx ax ax` have
   JSD 1.0 with marks retained as part of a glyph and 0.0 after stripping.
   This is a possibility proof, not an estimated CREMMA effect. Keep the agreed
   base-letter board row, but preregister a mark-preserving sensitivity with an
   explicit glyph-unit definition. Merely retaining NFD marks while taking `w[0]`
   does not implement this sensitivity; taking `w[-1]` can instead count a detached
   combining mark. Do not compare a changed unit to an old band without qualification.

4. **Calibrate raw JSD for sample size and symbol inventory.** In 200 seeded IID
   simulations per size (24 equiprobable symbols, 7 tokens per line, no positional
   effect), mean initial JSD is 0.126 at 50 lines, 0.056 at 100, 0.0104 at 500,
   and 0.00119 at 4,130. At 50 lines the central 95% range is 0.056–0.204.
   This does NOT predict that the pooled prose15 row crosses 0.10 by chance.
   It shows why small per-manuscript raw rows and a large Voynich row need matched
   sampling and/or within-line permutation calibration. Voynich-only s15 widths
   do not by themselves calibrate Latin finite-sample bias. Report effect magnitude
   and uncertainty, not just a permutation p-value.

5. **Keep block-start distinct from paragraph-start.** The plan already acknowledges
   no paragraph annotations. The inspected XML has two MainZone blocks, 35 lines
   each, at horizontal positions 386 and 2264: a column layout. Label the proxy
   honestly, and mark paragraph-specific comparisons unavailable or proxy-only.
   This does not invalidate ordinary line-edge JSD; it limits paragraph claims.

## Interpretation boundary

A low score would mean the specified controls, transcription policy and estimator
did not reproduce the Voynich effect. A high score would supply a counterexample
to uniqueness of that statistic. Neither alone establishes a universal layout
explanation, content, or a decipherment. Preserve the approved compute stop rule,
but distinguish a resource decision from a causal conclusion. No field-first
claim follows from this audit.

## Checks and handoff

- `.\\.venv\\Scripts\\python.exe -B workflow\\research\\support_phase1_audit.py`:
  exit 0; synthetic assertions passed; JSON recorded.
  Script refuses to overwrite an existing JSON receipt.
- `.\\.venv\\Scripts\\python.exe -B -m unittest tests.test_medieval_line_controls -v`:
  exit 0; all five helper tests passed, including exact edge-null enumeration,
  planted marker, tokenization, XML filtering and Holm correction.
- Separate `python -B -c` check using `a2_position.stats` returned `[1.0, 1.0, 0.0]`
  for the three pooling cases; exit 0. No actual CREMMA edge effects were scored.
- These are author-run checks, not an external scientific replication or adoption
  by the Phase 1 owner. Fable should decide amendments before scoring and freezing.
- No changes to Fable's plan, preregistration, prefixes, registry, shared scoreboard
  or producer files. Earlier MLC1 fetch/scoring work remains parked to avoid overlap;
  its partial cache supplied only the one XML source-format inspection here.

Suggested handoff: **Keep Phase 1; before freezing s18, resolve token boundaries,
add an abbreviation-unit sensitivity, and require calibrated per-manuscript checks
before a pooled-low verdict is interpreted as excluding scribal layout.**
