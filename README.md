# ShepherdQR.github.io

Personal static site for notes, reading records, study logs, and small essays.

Public site:

- <https://zqr.world/>
- GitHub Pages repository: <https://github.com/ShepherdQR/ShepherdQR.github.io>

## Current Shape

The site is Markdown-first:

1. Source notes live under `qrthoughts/yearYYYY/monthM/`.
2. Each note may start with an HTML file-header comment, followed by YAML front matter.
3. `scripts/build_site.py` reads Markdown and regenerates site data.
4. `homepage-data.js` drives the homepage, archive pages, category pages, adjacent article links, and `stats.html`.
5. Stable article URLs are generated as committed static pages, such as `/books/0056/` and `/thoughts/0012/`.
6. `sitemap.xml` and `includes/atom.xml` are generated from the same Markdown metadata.
7. `render.html?md=...` remains as a legacy and diagnostic reader.

Because GitHub Pages serves this repository as static files, generated files such as `homepage-data.js`, `sitemap.xml`, `includes/atom.xml`, and `books/0056/index.html` must be committed after a build.

## Daily Workflow

### 1. Create a New Note

From the repository root:

```powershell
python scripts/new_note.py Thoughts "文章标题"
python scripts/new_note.py Thoughts "导数-渐进的静默"
python scripts/new_note.py Thoughts "导数-博物馆标本式压缩"
python scripts/new_note.py Books "麦肯锡-问题分析与解决技巧"
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
- `sitemap.xml`
- `includes/atom.xml`
- `/books/NNNN/index.html`
- `/thoughts/NNNN/index.html`
- `/study/NNNN/index.html`
- `/videos/NNNN/index.html`

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
- <http://localhost:8000/thoughts/0012/>
- <http://localhost:8000/render.html?md=/qrthoughts/year2026/month5/[Thoughts][0012][对“生存还是毁灭”这一问题的认识].md>

The clean URL is the public canonical URL. The `render.html?md=...` form is mainly kept for compatibility and debugging.

### 5. Validate Before Publishing

Run:

```powershell
python scripts/validate_site.py
```

Expected result:

```text
Site validation summary
  result: OK
```

This checks that Markdown-backed records have valid clean URLs, source paths, legacy URLs, and generated alias pages.

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
tags: ["标签一", "标签二"]
series: "系列名"
summary: "一句短说明"
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

## Statistics

`stats.html` shows global counts, including:

- total published notes
- `Books` count
- `Thoughts` count
- year distribution

These numbers come from generated Markdown metadata in `homepage-data.js`. There is no separate CSV or Excel source.

## Project Files

Important source files:

- `qrthoughts/`: canonical Markdown content
- `scripts/new_note.py`: create a note and optionally build
- `scripts/build_site.py`: regenerate site data and stable URL pages
- `scripts/validate_site.py`: validate generated article URLs
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
