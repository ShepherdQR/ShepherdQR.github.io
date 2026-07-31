# ShepherdQR.github.io

Human-owned public knowledge interface for complex intelligence, engineering
evidence, mathematical structure, governance, civilization, reading, and
literature.

Public site:

- <https://zqr.world/>
- GitHub Pages repository: <https://github.com/ShepherdQR/ShepherdQR.github.io>

## Current Shape

The site is Markdown-first:

1. Source notes live under `qrthoughts/yearYYYY/monthM/`.
2. Each note may start with an HTML file-header comment, followed by YAML front matter.
3. `scripts/build_site.py` reads Markdown and regenerates site data.
4. `homepage-data.js` drives the homepage, searchable Atlas, category pages,
   adjacent article links, and the Evidence observatory.
5. `data/site-plane.json` is the declarative source for the public L1 advisory
   projection; the build emits it as `site-data.js` for the homepage, Evidence,
   and System surfaces.
6. Stable article URLs are generated as committed, build-rendered semantic HTML pages, such as `/books/0056/` and `/thoughts/0012/`; JavaScript progressively adds the object index, reading progress, math, and interactive enhancements.
7. `sitemap.xml` and `includes/atom.xml` are generated from the same Markdown metadata.
8. `render.html?md=...` remains as a legacy and diagnostic reader.

Because GitHub Pages serves this repository as static files, generated files
such as `homepage-data.js`, `site-data.js`, `sitemap.xml`, `includes/atom.xml`,
and `books/0056/index.html` must be committed after a build.

## Public Interface

The site now has four primary surfaces:

- `Field` (`index.html`): Current Exhibition、叙事 registry、fresh evidence 与来源 rail。
- `Atlas` (`archive.html`): 可切换的 Constellation / complete accession Ledger，加全文元数据筛选；Series 是二级策展路径。
- `Evidence` (`stats.html`): 将摘要来源、叙事映射、修订链、dated baseline 与权威边界串成 Evidence Spine。
- `System` (`field.html`): Charter Room、局部所有权 topology、人类门控循环与唯一 negative vitrine。

`Chronicle` (`chronicle.html`) 是独立的 as-known-at 时间脊柱，从 Atlas 与 System 进入，不占用顶级导航。

Every modern surface and generated article supports two persistent visual
profiles:

- `Field / 学术约束场`: warm paper, editorial structure, and calm long-form
  reading.
- `Museum / 深层博物馆`: the control plane's governed-institutional-artifact
  aesthetic—obsidian field, cold glass, archival labels, and role-bearing gate
  colors. Its canonical reference is
  `resources/pics/agi-structure-plan-nine-grid-v2.png`.

The switch stores only a device-local viewing preference. It does not mutate
content or control-plane state. The museum profile is not a generic dark mode:
amber is reserved for human gates, red for blocked/refused/revoked states, and
the long-form reading surface remains an archival paper folio.

Museum has one explicit non-regression invariant: switching to Museum must show
the **局部真理宪章 / Local Truth Charter** as the core exhibit. Field does not
download that Museum-only material on first load; the switch hydrates a responsive
WebP source when Museum is actually requested.

## Daily Workflow

### 1. Create a New Note

From the repository root:

```powershell
python scripts/new_note.py Thoughts "文章标题"
python scripts/new_note.py Thoughts "党建文选学习报告"
python scripts/new_note.py Books "舒婷"
```

Supported content types:

- `Books`
- `Thoughts`
- `Study`
- `Videos`

The command will:

- choose the next four-digit id for that type;
- create a Markdown file under `qrthoughts/yearYYYY/monthM/`;
- write the top file-header comment and standard front matter;
- regenerate `homepage-data.js`;
- regenerate stable article pages such as `/thoughts/0013/`.

Useful options:

```powershell
python scripts/new_note.py Books "鲁迅" --tags "文学,鲁迅" --series "读书"
python scripts/new_note.py Thoughts "短札" --summary "一句短说明"
python scripts/new_note.py Thoughts "数学札记" --math --lead-image "/resources/pics/example.png"
python scripts/new_note.py Thoughts "研究日志" --field-ids "VL-ENGINEERING-EVIDENCE" --revision 1
python scripts/new_note.py Thoughts "修订稿" --supersedes "Thoughts:0012" --revision 2
python scripts/new_note.py Study "交互实验" --interactive
python scripts/new_note.py Study "D3.js" --date 2026-05-20
python scripts/new_note.py Thoughts "草稿标题" --status draft --no-build
python scripts/new_note.py Thoughts "文章标题" --open
```

Use `--id 0013` only when a specific id is intentionally needed.

### 2. Edit an Existing Note

Edit the Markdown file directly, for example:

```text
qrthoughts/year2026/month5/[Thoughts][0012][对“生存还是毁灭”这一问题的认识].md
```

For meaningful edits, update these front matter fields:

```yaml
updated: "2026-05-20 21:30:00"
updated_date: "2026-05-20"
```

Keep these fields stable unless the article identity really changes:

- `type`
- `id`
- `created`
- `created_date`
- `published`

Do not manually edit `homepage-data.js` or generated article pages first. Change Markdown, then rebuild.

### 3. Build the Site

Run:

```powershell
python scripts/build_site.py
```

This regenerates:

- `homepage-data.js`
- `site-data.js`
- `sitemap.xml`
- `includes/atom.xml`
- `/books/NNNN/index.html`
- `/thoughts/NNNN/index.html`
- `/study/NNNN/index.html`
- `/videos/NNNN/index.html`

Generated article pages already contain readable semantic HTML. A CDN or
runtime Markdown failure therefore cannot erase the article body.

Responsive image masters and derivatives are tracked by
`resources/pics/derivatives/manifest.json`. Normal builds validate and reuse the
committed derivatives. To deliberately regenerate them with a locally installed
Chromium-family browser, run:

```powershell
python scripts/build_site.py --images
```

If old Markdown files are missing front matter, the build will stop and list them. For migration cleanup only, run:

```powershell
python scripts/build_site.py --normalize
```

### 4. Preview Locally

Start a local static server:

```powershell
python -m http.server 8000
```

Open:

- <http://localhost:8000/>
- <http://localhost:8000/archive.html>
- <http://localhost:8000/stats.html>
- <http://localhost:8000/field.html>
- <http://localhost:8000/thoughts/0012/>
- <http://localhost:8000/render.html?md=/qrthoughts/year2026/month5/[Thoughts][0012][对“生存还是毁灭”这一问题的认识].md>

The clean URL is the public canonical URL. The `render.html?md=...` form is mainly kept for compatibility and debugging.

### 5. Validate Before Publishing

Run:

```powershell
python -B scripts/test_templates.py
python -B scripts/test_article_durability.py
python -B scripts/image_pipeline.py --check
python -B scripts/validate_site.py --max-warnings 50
python -B scripts/validate_aesthetic_system.py
```

Expected result:

```text
Site validation summary
  result: OK
```

Together these checks cover Markdown truth projection, static article fallback,
heading normalization, responsive image hashes, clean URLs, source paths,
generated aliases, public site-plane freshness, role semantics, the Museum
Charter invariant, transfer budgets, root metadata, theme hydration, and sitemap
coverage.

### 6. Publish

After build and validation:

```powershell
git status --short
git add .
git commit -m "Add new note"
git push origin master
```

GitHub Pages deploys from `master`. After deployment, the public URL should be available at:

```text
https://zqr.world/thoughts/0013/
```

Replace `thoughts/0013` with the generated type and id.

## Markdown Header And Front Matter

Every public note should keep this shape:

```markdown
<!---------------------------------------------------------
 - Author: Qirong ZHANG
 - Date: 2026-05-20 21:30:00
 - Github: https://github.com/ShepherdQR
 - LastEditors: Qirong ZHANG
 - LastEditTime: 2026-05-20 21:30:00
 - Copyright (c) 2026 Qirong ZHANG. All rights reserved.
 - SPDX-License-Identifier: LGPL-3.0-or-later.
 --------------------------------------------------------->
---
type: Thoughts
id: "0013"
title: "文章标题"
created: "2026-05-20 21:30:00"
created_date: "2026-05-20"
published: "2026-05-20"
updated: "2026-05-20 21:30:00"
updated_date: "2026-05-20"
slug: "thoughts-0013"
status: "published"
summary: "一句短说明"
tags: ["标签一", "标签二"]
series: "系列名"
field_ids: ["VL-ENGINEERING-EVIDENCE"]
revision: "1"
revision_status: "current"
supersedes: ""
superseded_by: ""
errata: []
lead_image: ""
math: false
interactive: false
source:
  date_source:
    created: "new-note"
    published: "new-note"
    updated: "new-note"
---
```

Required fields:

- `type`: one of `Books`, `Thoughts`, `Study`, `Videos`
- `id`: four-digit id within the type
- `title`: article title
- `created` and `created_date`: original creation time
- `published`: publication date used for sorting
- `updated` and `updated_date`: latest meaningful update time
- `slug`: stable metadata slug
- `status`: usually `published`

Optional but useful fields:

- `tags`
- `series`
- `summary`
- `field_ids`: stable narrative ids declared in `data/site-plane.json`
- `revision`, `revision_status`, `supersedes`, `superseded_by`, and `errata` for explicit object history
- `math: true` when the article requires MathJax
- `interactive: true` when the article requires D3 or embedded scripts
- `lead_image` for article sharing metadata; source-relative and site-root paths are supported

The build preserves these fields in `homepage-data.js`. It emits
`summarySource: explicit|derived`, `fieldIds`, and `mappingSource` so authored
summaries and transparent taxonomy/default mappings are never reported as the
same kind of evidence. When `summary` is absent, the first prose paragraph is
cleaned into a plain-text excerpt for metadata and Atom feeds.
MathJax and D3 are emitted only for articles that explicitly request them or
whose existing Markdown content requires them.

## Statistics

`stats.html` is the public Evidence observatory. It shows:

- total published notes
- `Books` count
- `Thoughts` count
- year distribution
- authored summary versus derived excerpt coverage
- narrative mapping coverage and mapping source
- revision, supersession, errata, stale projection, and broken provenance counts
- human ownership, L1 advisory mode, denied runtime surfaces, and the dated
  WP0-WP8 / T12-candidate projection

These numbers come from generated Markdown metadata in `homepage-data.js`. There is no separate CSV or Excel source.

Validation also checks generated local links, Markdown image targets, article
feature flags, and generated metadata. Multiple body H1 headings and file-header
timestamps that disagree with front matter are reported as non-blocking warnings
so historical notes can be cleaned up incrementally.

## Project Files

Important source files:

- `qrthoughts/`: canonical Markdown content
- `scripts/new_note.py`: create a note and optionally build
- `scripts/build_site.py`: regenerate site data and stable URL pages
- `scripts/validate_site.py`: validate generated article URLs
- `scripts/test_article_durability.py`: verify static article fallback, heading normalization, form variants, and responsive media
- `scripts/image_pipeline.py`: generate or check responsive image derivatives
- `scripts/validate_aesthetic_system.py`: enforce role tokens, Museum Charter preservation, freshness wiring, and transfer budgets
- `scripts/capture_visual_matrix.ps1`: rebuild the Field/Museum desktop/mobile visual matrix, using segmented viewport samples for the very long Atlas Ledger
- `data/site-plane.json`: canonical public projection and interface contract data
- `site-data.js`: generated browser projection of `data/site-plane.json`
- `field.html`: public System and Evolution Chronicle surface
- `chronicle.html`: dated public knowledge and control-plane temporal spine
- `includes/css/system.css`: shared tokens, primitives, accessibility, and dual themes
- `includes/js/theme.js`: device-local Field/Museum profile switch
- `includes/js/article-renderer.js`: shared Markdown article renderer
- `includes/js/archive-page.js`: archive and category page renderer
- `includes/js/stats-page.js`: global statistics page renderer
- `homepage-data.js`: generated site data
- `sitemap.xml`: generated search-engine discovery file
- `includes/atom.xml`: generated Atom feed
- `render.html`: legacy Markdown reader

Generated public entry points:

- `index.html`
- `archive.html`
- `stats.html`
- `books.html`
- `thoughts.html`
- `study.html`
- `videos.html`
- `books/NNNN/index.html`
- `thoughts/NNNN/index.html`
- `study/NNNN/index.html`
- `videos/NNNN/index.html`

## Troubleshooting

### "加载失败：文件不存在"

Usually check these first:

1. Run `python scripts/build_site.py`.
2. Run `python scripts/validate_site.py`.
3. Confirm `.nojekyll` exists in the repository root.
4. Confirm the Markdown path in `homepage-data.js` matches the actual file path.
5. Prefer the clean URL, such as `/thoughts/0012/`, for public links.

### New Note Does Not Appear

Run:

```powershell
python scripts/build_site.py
python scripts/validate_site.py
```

Then commit both the Markdown source and generated files.

### Stats Look Out of Date

`stats.html` reads `homepage-data.js`, so rebuild first:

```powershell
python scripts/build_site.py
```

Then publish the regenerated files.
