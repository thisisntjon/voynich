# s128 prereg v2 -> v3: diff table against IV-REVIEW-S128-PREREG-V2-20261019.md (sha256 4231aece9ee2fc252114b7b63f927152465ccfd195c9453521442e90176cee36)

v2: runs/s128/s128_name_slot_prediction_v2.prereg 8c96091ae42df96e4771a816320452ff40e0e2f7f0b69c1e0e1212d39b432e6f (unchanged)
v3: runs/s128/s128_name_slot_prediction_v3.prereg (hash in the v3 stub and the re-review request)
Full line diff: runs/s128/s128_prereg_v2_to_v3.diff (diff -u v2 v3). Line numbers are v3 unless marked v2.

## Must-fixes A-D

| # | Must-fix | v3 lines | Change |
|---|---|---|---|
| A | Write the N2 ruling (option B decides) | :11-:28 (order), :96-:106 (COUNT LIST), :112-:122 (N60/N90 now report-only), :124-:143 (F0-N2-REAL), :167 (call rule 0) | New step d0: frozen count script runs/s128/s128_layout_counts.py (hash in the stub now; run only on a hand-written synthetic fixture, never on a Voynich file) runs only after HOLD 1 clears, on ZL3b only, and is the only code touching a Voynich file before step d. Per page it writes only page id, $Q, $B, $H, $L, per-line token counts and per-line paragraph-start flags, with the fix-4 page set and token rules. Count-list sha256 goes into the stub before N2 runs. Step d1: F0-N2-REAL decides, seeds 20261046-60. Egerton mapping fixed: random start chapter, edition order with wrap, each chapter at most once per seed, consecutive blocks per stratum in count-list order, each chapter poured into one page's real line lengths with real flags and slots. A chapter shorter than its page is skipped (SHORT_SKIP); more than 10% skipped, or the edition running out, fails the seed. Pass = NAME >= 10/15 and RARITY <= 5/15; a fail stops s128 before any Voynich text is read. At step d the scorer rebuilds the count list byte for byte or stops (COUNT_LIST_MISMATCH). Any after-read repeat is report-only. G1b stays the deciding power gate. |
| B | IVTFF locators | :51-:52, :64-:70 (v2 :40, :53-:55) | Locator '!' lines excluded. No locator changes paragraph structure; '@' is not a paragraph start. If ZL3b has no <%> mark on included herbal lines, the primary stops (STOP_NO_PARA_MARKS; count script exit code 3); no fallback for the primary. RF1b/IT2a only: LAYOUT_PROXY (rules i and iii), report-only, enters no call. Rules (ii)/(iii) now read the text after comment removal; a <$> on a line dropped as empty carries to the next kept line. |
| C | v1:24 rule dropped | :91-:94 | New rule: pages with no $H or no $L value are left out of the N2 strata. Their paragraph-initial tokens are held in place, their line-initial and other tokens are permuted within the page, they stay in S and N1, and their count is printed. The same rule applies in F0-N2-REAL (:129). |
| D | v1 -> v2 changes not listed | see the next table | All six named. |

## D. v1 -> v2 changes not listed in s128_prereg_v1_to_v2_DIFF.md (all kept in v3)

| v2 line | v3 line | Change from v1 |
|---|---|---|
| :23 | :32 | Question wording widened from "the known rarity of paragraph-initial words" to "the rarity and positional habits of paragraph-initial words (L-069, F-02)". |
| :63 | :77-:78 | Pages with no $L form their own reference group '?' (v3 adds a printed page count). |
| :69 | :84 | Nulls: "S recomputed on each draw with the reference counts of the permuted corpus" (stated explicitly; v1 was silent). |
| :79-:81 | :109-:111 | F0 setup details added: 8-token pseudo-lines, one paragraph per chapter, reference corpus = all chapters, 200 N1 draws, one within-chapter shuffle per seed. |
| :127 | :180 | Egerton other-chapter fraction corrected from 0.002-0.004 to 0.0019 (start_N90, calibration file line 9). |
| :134 | :187 | Meaning of MIXED stated: "no claim either way". |

## Other v2 -> v3 changes

- Header (:1-:9) names v2 as replaced and the v2 review; v1, v2 and the DRAFT are unchanged.
- STATUS (:12-:13) says the count script exists and has run only on the synthetic fixture.
- The Verifier's RARITY-arm limit is written next to the N60/N90 arms (:118-:119).
- The section header now reads "before any Voynich TEXT is read" (:108), because F0-N2-REAL uses the count list.
- Stub: the v3 prereg first, then the count script, then the same 18 v2 entries re-hashed (the v2 prereg kept as an unchanged
  reference), the v2-to-v3 diff files, the four fixture files and the two v2 review files. The count list gets its own line later, at step d0.
