# Library gaps (P5, lib01, 2026-10-19)

What the library does not yet hold or index, and why. Each item names the blocker that was observed. None of this is
work for a person; each item is a retry or a source for a later agent run.

## Sources not harvested (catalogue completeness)
| gap | observed blocker | next attempt |
|---|---|---|
| Google Scholar | no API; scraping is against its terms | rely on OpenAlex + Semantic Scholar (both harvested) |
| Google Books | API quota 0 from the box | retry from Skynet with a quota, or skip (Open Library and IA were harvested) |
| DBLP | bot wall (HTML challenge) on the JSON API | retry later; coverage is mostly in OpenAlex |
| JSTOR | no open metadata API | JSTOR items appear through Crossref / OpenAlex DOIs |
| voynich.ninja curated link lists and master lists | login required | only public thread index harvested (`indexes/forum_threads_voynich_ninja.tsv`) |
| Blogs other than the four indexed | WordPress API 404/403 (e.g. Mod_Security) | per-site sitemap or Wayback |
| Popular books (ISBN level) | no single open source | Open Library harvested; coverage partial |

## Full text not held (P2)
| gap | blocker |
|---|---|
| Paywalled journal articles (Cryptologia, Speculum, etc.) | licence; metadata + abstract + link only, as required |
| Items listed in `fulltext/NOT-FETCHED.tsv` | landing page without a machine-readable PDF link, 403/404, or not open |
| Mention-level rows (`relevance=mention`, ~600 with OA URLs) | out of scope for this run; not downloaded |
| Internet Archive lending-only books | access-restricted; only open `_djvu.txt` files fetched |
| Newbold 1928, Manly 1931 full texts, Brumbaugh 1978, Kennedy & Churchill 2004 | copyright / not open |
| Greshko 2025 article full text | Cryptologia paywall (supplementary Zenodo files are open and fetched where PDF) |

## Primary sources not held (P3)
| gap | blocker |
|---|---|
| NSA declassified Friedman / Tiltman / Currier PDFs | HTTP 403 from both box and Skynet; D'Imperio 1978 is held in the project already; IA copy DTIC_ADA070618 exists |
| Kircher correspondence scans (carteggio) | links on voynich.nu dead since 2025 (per `letters.html`) |
| philipneal.net live site | unreachable 2026-10-19; Wayback copies used (`web/philipneal/`), possibly older than the last live version |
| Arizona radiocarbon internal report | not published (per Zandbergen `extra/carbon.html`); Hodgins 2009 letter is held |
| Yale 2014 forensic report details | reported only via Clemens (ed.) 2016 (book, not open) |
| Stolfi `text16e6.evt` original URL | 404; copy held via Bowern-Lindemann repo; IVTFF LSI is the maintained form |
| Yale Orbis / catalog JSON | HTTP 202 with empty body |

## Known quality limits
- `topic_tags` are keyword-regex tags, not judgments.
- `claim_summary` is the first sentence of the source's own abstract; empty when there is no abstract.
- Crosswalk `author_year_only` matches are unverified.
- Zenodo 2026 deposits are numerous and mostly unreviewed; `relevance=core` means on-topic, not credible.
- `inventory/build_held_files.ps1` is a superseded failed script (its deletion was blocked by Auto-review); use `build_held_files.py`.
