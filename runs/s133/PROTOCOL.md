# s133 protocol: Egerton 747 caption gate, fresh blind first read (D-079)

Owner: lead voynich-08 / b3796192. Jon named the lead in charge ("You are lead on this project FYI", 2026-10-19). Sylvie (Egerton owner per O-074) is notified, not asked to approve.

## Why
The Egerton gate (D-072 bridge) stalled because 18 of the 21 primary rows had no first read. Those rows are above row 128, and Ventura held them. Eve is unavailable. The Independent Verifier (IV) has not answered since 03:19. D-079 lifts the Ventura-pending stop: a fresh blind agent supplies the 18 missing first reads from blind-read-1 packet v3.

## Steps (in order; each one stops the run on failure)
1. **Freeze.** `s133.prereg` hashes the scorer, its fixture output, the sealed key, the second read, Grok's first reads and the packet. It is frozen before any reader starts and before any caption text is compared. The lead has read only page/box_index coverage from these files (21 of 21 primary rows map: 3 Grok, 18 packet gate P-ids).
2. **Hint check.** A fresh agent, with no project context, sees only `reader_input/`. It reports whether any file name, image or instruction reveals which rows are gate rows, or reveals expected caption text. Its call is HINT_CLEAN or HINT_FOUND. HINT_FOUND stops the run.
   - Deviation: the frozen protocol assigns the hint check to the IV. The IV is unresponsive, so an agent does it.
3. **Blind read.** A fresh agent with no project context (not Daybreak, Grok, Astra, the IV or the lead) reads all 60 crops per `reader_input/READ_INSTRUCTION.md`. It writes `reader_output/RESPONSE.csv` (the template columns), uses reviewer_id `s133-blind-1`, and gets one attempt.
4. **Audit.** `python tools/audit_reader_isolation.py <agent> <reader_input|reader_output regex> <RESPONSE.csv>` must print AUDIT_CLEAN. Any opening of `sealed/`, `D:/Squire`, the second read, Grok's reads, the web or any other repo path voids the read.
5. **Score.** `python -I s133_egerton_gate_score.py score reader_output/RESPONSE.csv > results_s133_gate.txt`. File the printed CALL. The gate rules are in the script docstring.

## Outcomes
- **BOTH_PASS_POINT_THRESHOLDS:** the caption gate passes on point estimates, with the CP intervals shown. The D-072 Egerton bridge may be used as a reading line, labelled with the interval caveat. No scoreboard move until the lead audit (TRIANGULATION).
- **GATE_NOT_PASSED:** caption reading at this protocol is not reliable enough for the bridge. Record the result and stop. No retry under this run id.
- **INCOMPLETE / HINT_FOUND / AUDIT_FLAGS:** a process failure, recorded as such. It is not a gate result.
