# s128 prereg v1 -> v2: diff summary against IV-REVIEW-S128-PREREG-V1-20261019.md (sha256 dab20d8b471e855b48f941005535819409e4c49bdefd278a26e1305c96b4a6a2)

v1: runs/s128/s128_name_slot_prediction_v1.prereg c03290385f5cd6e6133a39c8ba007834b424d48279dbff57d472a9a34917e385 (unchanged)
v2: runs/s128/s128_name_slot_prediction_v2.prereg 8c96091ae42df96e4771a816320452ff40e0e2f7f0b69c1e0e1212d39b432e6f (139 lines, LF)
v2 stub: runs/s128/s128_name_slot_prediction_v2.prereg.sha256 25774525952fb785441e873f90f8b2954878c84dd5b46c8bc4de7bf2105ae298 (18 entries)

| # | Must-fix | Where in v2 | What changed |
|---|---|---|---|
| 1 | CALL rules overlap | :113-:121 | Ordered rules, first match wins: G1b fail -> NOT_POWERED; S <= N1 q99 -> ABSENT; S <= N2 q99 -> RARITY_ONLY; S > max(N1,N2 q99) with floor and LOQO_MET -> NAME_SLOT_PRESENT; anything else above both nulls -> MIXED with reasons. Every outcome maps to one call. q99 index defined at :69-:70. |
| 2 | N2 never tried on a known answer | :82-:92 (F0-N2), :94-:97 (G1b) | F0-N2 runs on Egerton before any Voynich read: 112 pages in pseudo-strata of 4, name in the paragraph-initial slot, N60/N90. NAME arm must pass N2 in >= 10/15 seeds; RARITY arm (name removed, a non-recurring fresh type at token 0) must pass in <= 5/15. Frozen expected outcome already observed (runs/s128/results_s128_f0n2_calibration.txt): NAME 15/15 at both N, RARITY 1/15 and 0/15. G1b, now the decisive power gate, plants at the paragraph-initial slot at real Voynich page sizes, 10/15 bar. The old non-initial plant becomes G1a (reported). |
| 3 | Voynich data not frozen | :25-:35 + stub | Paths and sha256 for data/ZL3b-n.txt, RF1b-er.txt, IT2a-n.txt (hashed as bytes only, content not read), vparse.py, p1_bifolio_null.py, metrics_new.py (SlotSegmenter), s76_segmenter_independence.py (Zattera). Sheet rule written out (:34-:35). Foldout rule plus frozen list runs/s128/s128_excluded_foldouts.txt (f90r1/r2/v1/v2, f95r1/r2/v1/v2, from the published catalogue). |
| 4 | IVTFF reading rules not fixed | :37-:58 | Headers, text-line regex, included unit codes (P0 P1 Pb Pc Pr; Pt/L/C/R/S out), line 1, comments, <->, <%>/<$>, other tags, [a:b], { }, fillers, '.' and ',' breaks, uncertain glyphs (? * @nnn;) delete the token, empty lines dropped, paragraph-start rules with a printed fallback, slot classes. |
| 5 | Numbers do not match calibration | :95 (0.535), :101 (0.364), :118-:121 (floor) | Recurrence probability 0.535 (Egerton start_N90 'recurs>=2', calibration line 9); Macer arm 0.364 (line 18). Floor set to 0.117 = Macer start_N90 S (line 18), stated as AT Macer so a Macer-strength signal passes. 'identical' changed to 'adapted' (:62). |
| 6 | Seeds open | :71 (N2 20261019), :76 (N1 20261020), :79 (F0 20261021-30), :82 (F0-N2 20261031-45), :94 (G1b 20261101-15), :98 (G1a 20261201-15), :102 (Macer arms 20261301-15, 20261401-15), :108 (LOQO 20261501) | Every random draw has a fixed seed. |
| 7 | LOQO < 3 quires; one-token line 1 | :106-:111, :99-:100, :103-:104 | Fewer than 3 qualifying quires -> LOQO_NOT_ASSESSABLE -> MIXED. Pass bar ceil(2/3 x n). One-token line 1: G1b still plants in that token; G1a skips the page (counted; G1a_REDUCED if > 10%); pages with nothing outside line 1 get no recurrence copies (counted). |

Small notes also taken: 'adapted' wording (:62); secondary segmenters hashed. Not taken: none.
Open tension, for the Verifier: F0-N2 runs before any Voynich read, so it uses Egerton pages at N60/N90 and 112 pages, not real
Voynich page sizes. The real-size version is G1b, which needs the Voynich read and so runs after it (and before the real score).
