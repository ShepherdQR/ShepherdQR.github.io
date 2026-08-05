# Hanyi and Nobel Reading Series Publishing Closeout

Date: 2026-08-06
Workspace: `E:\Codes\ShepherdQR.github.io`
Thread: Build and publish the Hanyi academic-classics and Nobel literature reading series

## Objective

Add `汉译世界学术名著丛书` and `诺贝尔文学奖阅读系列` to the existing public series system, provide durable classified reading registers, and ensure each series has a web page with overall progress plus a concise complete catalog.

## Completed

- Added the Hanyi series with a reproducible 1000-title Commercial Press baseline:
  - 20 titles linked to public reading notes
  - 980 titles currently without a public reading note
  - five color/category groups and a 32-title suggested starting path
- Added the Nobel literature series for 1901–2025:
  - 118 awarded prizes and 122 laureates
  - 22 laureates linked to public reading notes
  - 100 laureates currently without a public reading note
  - 2 candidate note matches retained with explicit annotations
- Added durable Markdown registers at:
  - `reading-lists/hanyi-world-academic-classics-unread.md`
  - `reading-lists/nobel-literature-reading-progress.md`
- Added public detail pages at:
  - `/series/hanyi-world-academic-classics/`
  - `/series/nobel-literature/`
- Generalized the series renderer with search, status/category filtering, configurable ordering, optional detail cards, and a default compact-catalog view for the two large series.
- The compact view renders all matching entries in one grouped directory: all 1000 Hanyi titles or all 122 Nobel laureates by default; the detail-card view retains 80-item incremental loading.
- Made sitemap series paths data-driven and extended validation to require progress metrics, directory containers, view controls, valid catalog metadata, source links, and public reading-list targets.

## Evidence

- Implementation commit: `8f032162fb20a10ef908e47d6374778a3cc81ec3` (`Build Hanyi and Nobel reading series`).
- Push: `6ef63a5..8f03216 master -> master`; local `origin/master` resolved to the same full commit after push.
- Reproducibility:
  - `scripts/build_reading_series.py` regenerated the Hanyi 1000/20/980 and Nobel 122/22/100 datasets.
  - SHA-256 checks confirmed `data/series-books.json` and both Markdown registers were deterministic across regeneration.
- Staged-tree isolation:
  - Exported the exact staged index without the unrelated local `Thoughts 0034` files.
  - `python scripts/build_site.py` generated 163 Markdown-backed items and 163 alias pages.
  - Normalized content comparisons reported clean generated output for `homepage-data.js`, `includes/atom.xml`, `sitemap.xml`, and `site-data.js`.
  - `python scripts/validate_site.py --max-warnings 50` reported 0 errors and 41 non-blocking historical content warnings.
- Other automated checks:
  - `node --check includes/js/series-index.js` -> success.
  - `node --check includes/js/series-detail.js` -> success.
  - `python scripts/test_templates.py` -> 9 tests passed.
  - `python scripts/test_article_durability.py` -> 6 tests passed.
  - `python scripts/validate_aesthetic_system.py` -> 0 errors and 0 warnings.
- Local browser checks:
  - Series index rendered all three series and their correct progress totals.
  - Hanyi default view rendered `完整列出 1000 项`; todo rendered `筛选后 980 项`, including the final `HY-LA-050` entry.
  - Nobel default view rendered `完整列出 122 项` from 1901 through 2025; todo rendered `筛选后 100 项`.
  - Mobile visual checks showed readable compact rows, long-name wrapping, group headings, and status labels.
  - Browser console: 0 errors and 0 warnings.
- Live checks after push:
  - `https://zqr.world/series.html` rendered three series cards with the expected totals.
  - `https://zqr.world/series/hanyi-world-academic-classics/` rendered the default compact 1000-title directory through `HY-LA-050`.
  - `https://zqr.world/series/nobel-literature/` rendered all 122 laureates from 1901 through the 2025 laureate.
  - Detail pages and `data/series-books.json` returned HTTP 200; live browser console had no errors or warnings.

## Decisions

- Use a compact full-catalog view as the default for the two large series so “complete catalog” is literal and immediately visible; keep cards as an optional detail view for richer annotations and source links.
- Treat the Commercial Press 2024 official 1000-title list as the complete reproducible baseline, while explicitly noting that the publisher later reported more than 1000 titles in the first 23 installments.
- Treat `done` as “the public site has at least one linked reading note,” not as a claim that every work by a laureate or every volume has been exhaustively read.
- Keep externally refreshed source snapshots out of the normal site build; the committed registry and Markdown reports remain offline-buildable public artifacts.
- Use hunk-scoped staging for `README.md` and `sitemap.xml` so the unrelated local `前无再前` changes were not included in the series commit.

## Remaining

- The 41 staged-tree warnings are historical note-title/timestamp/summary warnings and are non-blocking; none was introduced by the two series.
- A future Hanyi expansion beyond the 1000-title baseline should wait for a new complete official catalog rather than append isolated titles without a reproducible boundary.
- The unrelated local `前无再前` source and generated files remain intentionally uncommitted for separate handling.

## Final State

- Branch: `master`.
- At report-writing time, implementation commit `8f032162fb20a10ef908e47d6374778a3cc81ec3` was present on `origin/master` and verified live.
- This closeout report is the only follow-up artifact to be committed after the implementation push.
- Preserved local changes outside this task: `README.md`, `homepage-data.js`, `includes/atom.xml`, `sitemap.xml`, `qrthoughts/year2026/month8/`, and `thoughts/0034/`.
