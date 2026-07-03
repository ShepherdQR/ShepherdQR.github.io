# Site Improvement Analysis

Date: 2026-07-03
Scope: `ShepherdQR.github.io` static site, local checkout at `E:\Codes\ShepherdQR.github.io`

## Executive Summary

The site has crossed the hardest threshold: it is now a coherent Markdown-first static site rather than a mixed historical collection. The current build and validation chain is healthy: `scripts/validate_site.py` reports 150 homepage items, 150 Markdown items checked, 150 Markdown sources checked, 0 errors, and `result: OK`.

The next useful work is not another migration pass. It is turning the 150-note corpus into a more navigable knowledge system, improving metadata for search and sharing, reducing runtime JavaScript dependencies, and tightening article semantics on mobile.

Highest-value directions:

1. Add real content metadata and knowledge navigation: tags, series, summaries, curated topic paths, and a search/filter layer.
2. Improve generated head metadata: descriptions, canonical URLs on index pages, Open Graph/Twitter cards, and better Atom summaries.
3. Reduce runtime dependencies: every article currently loads D3, MathJax, and remote `marked`, even though only a small minority need images, math, or embedded scripts.
4. Normalize article heading semantics: some article bodies render extra H1 headings after the page title, which is especially loud on mobile.
5. Extend validation beyond publish correctness: local link checks, image checks, heading hierarchy, metadata coverage, and dependency policy.

## Source Register

| Source | Used for | Confidence |
| --- | --- | --- |
| `README.md` | Current authoring/build/validate/publish workflow | High |
| `architecture/site-content-architecture.md` | Target architecture and original homepage/URL decisions | High |
| `architecture/markdown-publishing-workflow.md` | Markdown-first workflow and article renderer contract | High |
| `architecture/archive-and-article-page-design.md` | Archive/article page data contract | High |
| `architecture/project-change-migration-report.md` | Migration state and legacy cleanup history | High |
| `scripts/build_site.py` | Generated article pages, sitemap, Atom feed, dependency loading | High |
| `scripts/generate_homepage_data.py` | `homepage-data.js` fields and stats generation | High |
| `scripts/validate_site.py` | Current validation coverage | High |
| `index.html`, `includes/css/homepage.css` | Homepage IA and visual behavior | High |
| `archive.html`, `stats.html`, `includes/js/archive-page.js`, `includes/js/stats-page.js` | Archive/stats behavior | High |
| `render.html`, `includes/js/article-renderer.js`, `includes/css/pages.css` | Article rendering, dependencies, semantics, mobile behavior | High |
| Browser checks at `http://127.0.0.1:8000/` | Desktop/mobile visual and console behavior | High |

## Current Strengths

### 1. Publishing Pipeline Is Solid

The site is generated from Markdown source under `qrthoughts/`, with stable clean URLs such as `/thoughts/0023/` and `/books/0124/`. Generated outputs include `homepage-data.js`, article alias pages, `sitemap.xml`, and `includes/atom.xml`.

Validation currently passes cleanly:

```text
Site validation summary
  homepage items: 150
  markdown items checked: 150
  markdown sources checked: 150
  errors: 0
  result: OK
```

Local link checks also found no missing generated HTML links across 2,942 local href/src references, and Markdown image checks found no missing images across 8 Markdown image references.

### 2. The Visual Direction Fits The Site

The current homepage and archive pages are text-first, restrained, and readable. The desktop homepage presents identity, navigation, portrait, recent notes, collections, selected notes, years, and the full note list without feeling like a marketing page.

The mobile homepage has no horizontal overflow at a 390px viewport, and the layout gracefully stacks the portrait and content.

### 3. Legacy HTML Is No Longer The Main Burden

The migration ledger says the site moved from legacy HTML toward Markdown-first publishing, and the current checkout retains only three legacy HTML exception files under `qrthoughts/`:

```text
qrthoughts/year2020/month2/why-now.html
qrthoughts/others/BooksItem.html
qrthoughts/others/BooksDoneIndex.html
```

This means new improvement work can focus on reader experience and generated quality rather than historical cleanup.

## Main Improvement Directions

### 1. Turn The Corpus Into A Knowledge Map

Current data shape:

| Metric | Value |
| --- | ---: |
| Published notes | 150 |
| Books | 124 |
| Thoughts | 23 |
| Study | 1 |
| Videos | 2 |
| Years | 2020-2026 |

The site currently exposes chronology and type. That is useful, but it undersells the corpus. The reader cannot yet enter by theme, project, concept, author, reading sequence, or current research concern.

Recommended changes:

- Start using `summary`, `tags`, and `series` in front matter for new notes.
- Propagate `summary`, `tags`, and `series` from Markdown into `homepage-data.js`.
- Add tag/series filtered archive views, either as generated pages or as client-side filters on archive pages.
- Replace or collapse the homepage `All Notes` section once archive/search becomes strong enough; the homepage can then become a more curated map.
- Add curated paths, for example "AI/agent systems", "software engineering", "mathematics", "politics/governance", "literature reading", and "personal essays".
- Make `Selected Notes` data-driven instead of hard-coded in `index.html`.

Why this matters: the site already has enough material that chronology alone becomes a storage system, not a discovery system.

### 2. Add Real Metadata For Search, Sharing, And Feeds

Across root pages plus 150 article pages, the current generated HTML has:

| Metadata | Coverage |
| --- | ---: |
| `meta description` | 0 / 158 |
| Open Graph | 0 / 158 |
| Twitter cards | 0 / 158 |
| JSON-LD | 0 / 158 |
| Canonical links | 150 / 158 |
| Atom feed alternate links | 151 / 158 |

Atom feed summaries currently fall back to generic values such as `Thoughts note 0023` because article summaries are not populated.

Recommended changes:

- Add `summary` to front matter and emit it into `homepage-data.js`.
- Generate `<meta name="description">` for homepage, archive pages, collection pages, and articles.
- Generate `og:title`, `og:description`, `og:type`, `og:url`, and optional `og:image`.
- Use the first article image as `og:image` when present, especially for poster-led recent Thoughts notes.
- Add canonical links to `index.html`, `archive.html`, `stats.html`, and collection pages using `https://zqr.world`.
- Use summaries in `includes/atom.xml` instead of generic type/id fallbacks.
- Consider JSON-LD `BlogPosting` or `Article` for article pages after summaries are available.

This is a high-leverage improvement because it mostly lives in the generator and front matter contract.

### 3. Reduce Runtime Rendering And Unconditional Dependencies

Every one of the 150 generated article pages currently loads:

- local `includes/js/d3.js` at about 600 KB;
- remote MathJax from `cdn.jsdelivr.net`;
- remote `marked` from `cdn.jsdelivr.net`;
- local `includes/js/article-renderer.js`.

But content analysis shows:

| Feature | Notes |
| --- | ---: |
| Notes with images | 6 |
| Notes with script/SVG | 1 |
| Rough notes with math-like syntax | 4 |

Recommended changes:

- Add front matter flags such as `math: true`, `interactive: true`, and perhaps `lead_image`.
- Load MathJax only when `math: true` or when a build-time detector sees math syntax.
- Load D3 only for the known interactive Study note or notes marked `interactive: true`.
- Prefer build-time Markdown rendering so generated article HTML contains content without requiring `marked` at runtime.
- If runtime Markdown rendering remains, vendor `marked` locally or pin it explicitly with integrity/version policy.
- Add a no-JavaScript fallback for generated article pages once build-time HTML is available.

This would improve speed, offline robustness, privacy, and long-term durability.

### 4. Fix Article Heading Semantics

The article shell renders the page title as H1. Most Markdown files also start with a `# title`; the renderer strips that first heading when it matches the front matter title. That works for most notes.

However, 7 notes contain multiple `#` lines. On pages such as `/thoughts/0018/`, body-level `#` headings remain H1 after the article title. On mobile, those body H1 sections render around 36px, which can become visually louder than the article structure should be.

Recommended changes:

- In the renderer or build step, normalize body headings down one level after removing the article title.
- Add CSS for `.article-content h1` so any remaining H1 is styled like section-level content, not a second page title.
- Add a validator warning when a published article body contains multiple top-level `#` headings.

This is not a publishing blocker, but it is a tidy quality improvement for accessibility, document outline, and mobile reading.

### 5. Make Stats A Reader-Facing Insight Page

The current stats page is accurate but basic: totals, collection counts, and year counts. It currently behaves more like a sanity dashboard than a public-facing reading map.

Recommended additions:

- Year-by-type matrix.
- Recent publishing cadence.
- Longest notes and shortest notes.
- Notes with images, math, or interactive content.
- Top tags and series after metadata exists.
- "Current active threads" based on recent tags or curated front matter.

This would make the Stats page a map of the site's intellectual shape, not only a count table.

### 6. Strengthen Validation

`scripts/validate_site.py` is strong for generated URL/data consistency, but there are useful checks still outside it.

Recommended new validations:

- Local HTML link and asset existence.
- Markdown image existence.
- Metadata coverage thresholds: summary/tag/series coverage.
- Generated head metadata presence.
- Article heading hierarchy warnings.
- Conditional dependency policy: D3/MathJax should only appear when needed.
- Homepage archive years should be newest-first.

One concrete bug-like finding: homepage archive years render as `2020 ... 2026`, while archive and stats pages are newest-first. This happens because JavaScript object keys that look like integers are enumerated in numeric order. Sort `Object.keys(data.stats.years || {})` descending in `index.html`.

### 7. Clean Up CSS Generations Gradually

The site now has newer CSS for homepage/archive and older CSS for legacy article styles in `pages.css` and `frontpage.css`. This is not causing immediate breakage, but the article CSS still carries global historical rules such as `H1`, `H2`, `body.mobile`, older `div.outer`, ads, and syntax highlight blocks.

Recommended changes:

- Preserve old classes only where real legacy pages still need them.
- Move article-shell-specific rules into a clearer modern block.
- Add explicit `.article-content h1` handling.
- Remove or quarantine unused Bootstrap/jQuery-era CSS only after checking the retained legacy exception pages.

This should be done cautiously because older migrated notes may depend on some historical styles.

## Suggested Implementation Sequence

### Phase 1: Quick Wins

1. Sort homepage archive years newest-first.
2. Add `.article-content h1` styling or heading normalization.
3. Add local link/image checks into `scripts/validate_site.py`.
4. Add root-page canonical and feed alternate links.
5. Add article `meta description` using fallback excerpt generation.

### Phase 2: Metadata Backbone

1. Extend `generate_homepage_data.py` to preserve `summary`, `tags`, `series`, `math`, `interactive`, and `lead_image`.
2. Update `new_note.py` to encourage summary/tags for new notes.
3. Backfill summaries/tags for the newest and selected notes first, not all 150 at once.
4. Use summaries in homepage lists, archive pages, Atom feed, and meta descriptions.

### Phase 3: Discovery Upgrade

1. Add archive filters for type, year, tag, and series.
2. Add a lightweight generated search index.
3. Convert `Selected Notes` into a curated data file or front matter flag.
4. Build topic path pages for the highest-value clusters.

### Phase 4: Rendering Upgrade

1. Add build-time Markdown-to-HTML rendering.
2. Keep `render.html?md=...` as a diagnostic/compatibility reader.
3. Generate article body HTML into clean article pages.
4. Load MathJax/D3 only when front matter or detection requires it.
5. Add no-JS article fallback as the default generated output.

## Recommended Next Task

The best next concrete task is a small "metadata and validation hardening" pass:

1. Fix homepage year sort.
2. Add `.article-content h1` handling.
3. Propagate optional front matter fields into `homepage-data.js`.
4. Add generated `meta description` and better Atom summaries.
5. Add link/image/head-metadata validation checks.

That task is small enough to ship safely, but it opens the path for the larger knowledge-map work.
