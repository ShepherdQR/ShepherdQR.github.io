# Site Development Plan

Date: 2026-07-03
Last updated: 2026-07-13
Status: Active
Scope: ShepherdQR.github.io static personal site
Source analysis: [Site Improvement Analysis 2026-07-03](site-improvement-analysis-2026-07-03.md)

## Direction

The site has completed the core Markdown-first migration. The next stage is to turn the 150-note corpus from a chronological archive into a durable, searchable, and shareable knowledge system while keeping the current minimalist personal-site character.

The development direction is:

1. Preserve Markdown as the canonical content source.
2. Keep generated static pages and clean URLs as the public surface.
3. Add richer metadata and discovery paths before doing large visual redesign.
4. Reduce unnecessary runtime JavaScript on article pages.
5. Keep validation strict enough that source/generated drift is caught before publishing.

## Current Baseline

As of 2026-07-13:

| Area | Baseline |
| --- | --- |
| Published Markdown notes | 159 |
| Collections | Books 125, Thoughts 31, Study 1, Videos 2 |
| Validation | `python scripts/validate_site.py` passes with 0 errors |
| Source model | Markdown front matter under `qrthoughts/` |
| Public URLs | Clean generated URLs such as `/thoughts/0023/` |
| Legacy HTML | Only three retained exception files under `qrthoughts/` |
| Optional discovery metadata | `summary`, `tags`, and `series` supported by authoring workflow but not populated in the corpus |

## Phase 1: Quality And Metadata Hardening

Goal: improve generated quality without changing the site's publishing model.

| Task | Status | Notes |
| --- | --- | --- |
| Sort homepage archive years newest-first | Proposed | `index.html` currently enumerates numeric object keys in ascending order. |
| Normalize article body heading hierarchy | In progress | Validator now warns on multiple body H1 headings; historical cleanup remains incremental. |
| Preserve optional front matter in `homepage-data.js` | Implemented | Includes `summary`, `tags`, `series`, `math`, `interactive`, and optional `lead_image`; summary has excerpt fallback. |
| Generate `meta description` fields | Partially implemented | Homepage and all generated article aliases now have descriptions; remaining root collection pages are future work. |
| Improve Atom summaries | Implemented | Explicit summaries or generated excerpts replace generic type/id fallbacks. |
| Add root-page canonical links | Proposed | Add canonical URLs for homepage, archive, stats, and collection pages. |
| Add validation for local links and Markdown images | Implemented | Validator checks generated/local HTML references and Markdown images; first run fixed three legacy path errors. |

Acceptance:

- `python scripts/build_site.py` completes.
- `python scripts/validate_site.py` completes with `result: OK`.
- Homepage, archive, stats, one normal article, and one image article pass browser smoke checks.
- Generated diffs remain deterministic.

## Phase 2: Knowledge Navigation

Goal: make the corpus explorable by theme and reading path, not only by date and type.

| Task | Status | Notes |
| --- | --- | --- |
| Backfill summaries for recent and selected notes | Implemented initial slice | Thoughts 0014-0029 and 0031 now have explicit summary, tags, and series; historical corpus remains incremental. |
| Backfill tags for high-value clusters | Implemented initial slice | Recent Thoughts cover ASI/agents, engineering, mathematics, governance, civilization, reading, literature, and poetry. |
| Add series support to archive rendering | Implemented | Atlas search and rows expose series from generated metadata. |
| Make `Selected Notes` data-driven | Implemented | `data/site-plane.json` curates stable `type` + `id` entries across five narrative lines. |
| Add tag/series filters to archive pages | Implemented | Atlas and collection pages filter by query, type, year, series, and tag with URL persistence. |
| Add curated topic paths | Implemented first public layer | Homepage five-field map links into generated Atlas filters and stable collections. |

Acceptance:

- A reader can enter the site by collection, year, tag, series, selected notes, and recent notes.
- The homepage can become more curated because archive/search handles the long tail.
- Metadata additions do not require manual edits to generated files.

## Phase 3: Search And Stats Upgrade

Goal: turn statistics and archive data into public navigation.

| Task | Status | Notes |
| --- | --- | --- |
| Add a lightweight generated search index | Implemented without a second file | `homepage-data.js` remains the compact static search/read model. |
| Add archive search/filter UI | Implemented | Filters title/summary/id/type/year/tag/series without a backend. |
| Expand `stats.html` | Implemented public evidence slice | Adds metadata coverage, authority boundary, dated control-plane baseline, collections, years, and fresh evidence. |
| Track content feature counts | Proposed | Images, math, interactive notes, posters. |

Acceptance:

- `stats.html` explains the shape of the corpus, not only total counts.
- Search and filters work without a backend.
- The generated data remains small enough for GitHub Pages.

## Phase 4: Article Rendering Durability

Goal: reduce runtime fragility and make article pages useful even when remote scripts fail.

| Task | Status | Notes |
| --- | --- | --- |
| Render Markdown to HTML at build time | Proposed | Keep `render.html?md=...` as a diagnostic reader. |
| Load MathJax only when needed | Implemented | Front matter plus build-time detection currently selects three math articles. |
| Load D3 only for interactive notes | Implemented | Front matter plus build-time detection currently selects one interactive article. |
| Vendor or pin Markdown runtime dependencies | Proposed | If runtime rendering remains, avoid unpinned remote `marked`. |
| Add no-JavaScript article fallback | Proposed | Generated article pages should contain readable body HTML. |

Acceptance:

- Ordinary text articles do not load D3 or MathJax.
- Article pages remain readable without remote CDN availability.
- Interactive migrated notes still work when explicitly marked.

## Phase 5: CSS And Legacy Surface Cleanup

Goal: simplify styling after behavior is protected by validation.

| Task | Status | Notes |
| --- | --- | --- |
| Separate modern article-shell CSS from legacy page CSS | In progress | Shared `system.css` and scoped modern overrides now protect the generated article shell; historical exception rules remain quarantined in `pages.css`. |
| Audit retained legacy exception pages | Proposed | Confirm which Bootstrap/jQuery-era assets still matter. |
| Remove or quarantine unused assets | Proposed | Only after link and browser checks. |
| Improve image/poster handling | Implemented initial slice | Lead images drive article/social metadata; ASI Research explicitly selects canonical nine-grid v2. |

## Phase 6: Public Control-Plane Interface And Visual System

Goal: express the repository as a human-owned public knowledge data plane
without presenting an advisory projection as runtime authority.

| Task | Status | Notes |
| --- | --- | --- |
| Add declarative public projection | Implemented | `data/site-plane.json` -> generated `site-data.js`, validated for L1/human/T12 boundaries. |
| Add System / Chronicle surface | Implemented | `field.html` exposes the human-gated loop, dated WP0-WP8 baseline, T12 candidate, denials, and provenance. |
| Establish shared design tokens | Implemented | `includes/css/system.css` governs typography, spacing, focus, status colors, and responsive primitives. |
| Add reversible dual visual profiles | Implemented | Field and Museum profiles share content/semantics; preference persists device-locally through `theme.js`. |
| Upgrade article reading | Implemented progressive layer | Reading progress, taxonomy links, estimated time, heading anchors, and responsive object index are injected without a new dependency. |
| Preserve authority truthfulness | Implemented validator gate | Validator rejects authority effects, adopted T12 claims, runtime/broker flags, missing theme profiles, and local absolute paths. |

Acceptance:

- Field, Atlas, Evidence, System, Series, and generated articles share the same
  tokens and persistent profile switch.
- Museum mode uses the canonical governed-institutional-artifact semantics
  without implying live runtime or target authority.
- Generated public projection and all 159 article aliases remain deterministic.
- Retained legacy exception pages remain protected by scoped modern selectors.

## Near-Term Task Card

Recommended next implementation slice:

1. Render ordinary Markdown article bodies to HTML at build time.
2. Add a readable no-JavaScript article fallback while retaining
   `render.html?md=...` for diagnostics.
3. Pin or vendor the Markdown runtime only under a separate dependency release.
4. Continue metadata backfill through natural maintenance rather than a blind
   historical rewrite.
5. Perform a human visual review of both Field and Museum profiles across
   desktop/mobile, a normal article, a math article, an interactive article and
   a poster-led article.

This keeps the next risk concentrated in rendering durability instead of
mixing it with another information-architecture change.

## Operating Rules

- Change Markdown source first, then rebuild generated outputs.
- Do not manually edit `homepage-data.js`, article alias pages, `sitemap.xml`, or `includes/atom.xml` as the source of truth.
- After generator or renderer changes, always run:

```powershell
python scripts/build_site.py
python scripts/validate_site.py
```

- Browser smoke checks should include:
  - `index.html`
  - `archive.html`
  - `stats.html`
  - one normal article
  - one poster/image article
  - one mobile viewport check
