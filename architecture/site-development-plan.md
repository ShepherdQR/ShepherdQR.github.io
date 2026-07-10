# Site Development Plan

Date: 2026-07-03
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

As of 2026-07-03:

| Area | Baseline |
| --- | --- |
| Published Markdown notes | 150 |
| Collections | Books 124, Thoughts 23, Study 1, Videos 2 |
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
| Backfill summaries for recent and selected notes | Proposed | Start with current Thoughts notes and homepage selected notes. |
| Backfill tags for high-value clusters | Proposed | Suggested clusters: AI/agent systems, software engineering, mathematics, governance, literature, personal essays. |
| Add series support to archive rendering | Proposed | Use existing front matter field rather than inventing a new source. |
| Make `Selected Notes` data-driven | Proposed | Prefer front matter or a small curated data file over hard-coded IDs in `index.html`. |
| Add tag/series filters to archive pages | Proposed | Can be client-side first using generated data. |
| Add curated topic paths | Proposed | Small static pages for stable reader journeys. |

Acceptance:

- A reader can enter the site by collection, year, tag, series, selected notes, and recent notes.
- The homepage can become more curated because archive/search handles the long tail.
- Metadata additions do not require manual edits to generated files.

## Phase 3: Search And Stats Upgrade

Goal: turn statistics and archive data into public navigation.

| Task | Status | Notes |
| --- | --- | --- |
| Add a lightweight generated search index | Proposed | Keep it static and framework-free. |
| Add archive search/filter UI | Proposed | Filter by title, type, year, tag, and series. |
| Expand `stats.html` | Proposed | Add year-by-type matrix, longest notes, content features, and top tags. |
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
| Separate modern article-shell CSS from legacy page CSS | Proposed | `includes/css/pages.css` carries both current and historical rules. |
| Audit retained legacy exception pages | Proposed | Confirm which Bootstrap/jQuery-era assets still matter. |
| Remove or quarantine unused assets | Proposed | Only after link and browser checks. |
| Improve image/poster handling | Proposed | Add optional lead-image styling and social preview support. |

Acceptance:

- Current homepage, archive, stats, and article pages retain their visual identity.
- Retained legacy exception pages remain intentionally supported or explicitly retired.
- CSS cleanup does not create layout regressions on desktop or mobile.

## Near-Term Task Card

Recommended first implementation slice:

1. Fix homepage year ordering.
2. Normalize article body H1 rendering.
3. Add optional metadata propagation to `homepage-data.js`.
4. Generate article/root meta descriptions and better Atom summaries.
5. Add local link/image validation to `scripts/validate_site.py`.

This slice is small enough to ship safely and creates the foundation for the larger knowledge-map work.

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
