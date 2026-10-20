> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# External scout — Ninja, voynich.nu, TheVoynich.org, ACL/arXiv

Scouted: 2026-10-17 16:58 (system clock). Method: direct fetch of each site +
coverage counts in `research_notes/` + `reports/` (domain-string matches).
Search-engine summaries were NOT treated as evidence (arXiv mirror spam noted).

## 1. Voynich Ninja — https://www.voynich.ninja/ — COVERED, access-limited

Verified by fetch (guest view, 200): MyBB forum; header tools include Forums,
Blogosphere reader, Folio browser, Image extractor, Portal, Curated threads.
Site states most content is registered-users-only; links/images hidden from
guests ("You are not allowed to view links"). Team coverage: **73 mentions**
in research notes/reports — already a primary citation source (threads on
Timm tests, language-claim master list, Davis criteria).
Gaps/actions: (a) No team account known — registration is free; a human-owned
account unlocks links/images/deeper subforums. Agents should NOT register
autonomously. (b) Folio browser + image extractor are the cheapest route to
bounding-box/coordinate checks if M1's scrape needs independent confirmation.
Named-researcher activity (Davis, Stolfi, Zandbergen, Gheuens, Timm) is
consistent with team notes but was not re-verified person-by-person this scout.

## 2. Voynich.nu (Zandbergen) — https://www.voynich.nu/ — COVERED, canonical

Verified by fetch: author René Zandbergen (© 2004–2026); sections incl.
Description, Illustrations, Origin, History, Solvers, Writing,
Transliteration, Analysis; banner links Voynich MS Conference 2026 (Malta).
Transliteration page (fetched in full) documents FSG→EVA history, FSG/Petersen/
Friedman lineage, and links main transliteration files — the provenance of
the team's `data/ZL3b-n.txt` (ZL = Zandbergen–Landini). Team coverage:
**136 mentions** — the most-cited external source; carbon-dating, Currier,
solvers pages already load-bearing in notes.
Gaps/actions: second transliterations (GC/FSG/CD/Takahashi IVTFF) for
robustness checks are linked here but `data/external/` still does not exist
(PLAN Phase 0 item 3, unowned). Highest-value download target on this list.

## 3. TheVoynich.org — https://thevoynich.org/ — NOT COVERED (gap)

Verified by fetch: "a research record · Beinecke MS 408"; public snapshot
dated 2026-10-07 (UTC), research origin 2025-08-27. Counts: **691 findings
on record**, 651 manuscript records, 221 named figures. Statuses tally:
77 Confirmed, 140 Supported, 138 Candidate, 224 Observed, 70 Falsified,
0 Partially-Falsified, 42 Parked. Pages: Manuscript, Findings, Comparators,
Sources, Coviewer (folio reader with comparator side-by-side). Site explicitly
presents NO decipherment; central hypothesis = structural comparison with
late-medieval medical/divinatory/computational manuscripts (e.g., Cgm 7958
apparatus entries, Supported).
Critical caveat: statuses are "recorded by the researcher" (single-researcher
register + fuller internal workspace), NOT community consensus. Treat as a
well-organised claim index to cross-check, not an authority.
Team coverage: **0 mentions** — the only true blind spot in this scout.
Actions: (a) diff its 70 Falsified against LEADS §B dead ends (cheap
duplicate-work check); (b) diff its 77 Confirmed against LEADS §A constraints;
(c) mine Comparators for period nomenclator/herbal candidates (PLAN Phase 0
controls + §2C book search). Estimated one agent-session; public pages only.

## 4. Academic & computational literature (ACL / arXiv) — COVERED, noisy edges

Verified primaries this scout:
- ACL Anthology Q16-1006 (Hauer & Kondrak, TACL 2016): abstract confirms
  97% language-ID accuracy on 380 languages, 93% anagram-decoding accuracy,
  Hebrew suggestion for Voynich — exactly as team notes cite it.
- arXiv:2608.17096 (Rozanova & Temerev, submitted 17 Aug 2026, cs.CL):
  abstract confirms edge MI 0.2 bits, next-token <1%, h2 2.7 vs ~3.5,
  uncertain-space AUC 0.905, Naibbe/self-citation failing edge coupling —
  the benchmark C3/D1/E1/E2 already chase. Code/data mirrored on GitHub
  (linked from arXiv page; not opened this scout).
Team coverage: aclanthology 3 mentions, arxiv.org 19 mentions; Bowern &
Lindemann, Gaskell & Bowern (CEUR), Greshko Naibbe (Cryptologia/Zenodo,
data already local), Parisel 2026, Schwartz 2026 all in notes with
paywall/403 flags preserved.
Noise warning: web search surfaces fake-mirror arXiv domains, academia.edu
"decipherment" claims, and AI-content farms. Cite only aclanthology.org /
arxiv.org / publisher pages opened directly. r/voynich: 1 team mention —
correctly negligible; casual feed only, no action.

## Bottom line for the team

Three of four sources are already load-bearing (Ninja 73, voynich.nu 136,
ACL/arXiv primaries verified). The single actionable gap is TheVoynich.org:
one session to diff its Falsified/Confirmed registers against LEADS §A/§B
before any new experiment duplicates a tested claim. Second action:
voynich.nu second-transliteration downloads (already planned, still unowned).
Registration on Ninja remains a human decision.
