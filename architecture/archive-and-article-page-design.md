# Archive and Article Page Design

Status: accepted
Date: 2026-05-20

## Goal

Use Markdown front matter as the single content source, then render every note through one article template and expose the collection through generated index pages. Adding a note should only require adding one Markdown file and rebuilding `homepage-data.js`.

## Scope

- Clean article URLs are canonical, for example `/thoughts/0012/` and `/books/0056/`.
- `render.html?md=...` remains a compatibility reader for old links and diagnostics.
- `archive.html` is the chronological index for all published Markdown notes.
- `books.html`, `thoughts.html`, `study.html`, and `videos.html` are filtered collection indexes.
- `homepage-data.js` remains the generated read model for homepage, archive pages, and article adjacency.

## Data Contract

Every published Markdown note must keep these front matter fields:

- `type`
- `id`
- `title`
- `created_date`
- `published`
- `updated_date`
- `status: published`

The build script turns those fields into `homepage-data.js` items with:

- `href`: canonical clean article URL.
- `canonicalHref`: canonical clean article URL, duplicated explicitly for callers that distinguish display links from canonical identity.
- `legacyHref`: compatibility `render.html?md=/...` URL.
- `sourcePath`: canonical Markdown source path.
- `createdDate`: date displayed as the creation date.
- `published`: date used for sorting and archive grouping.
- `updatedDate`: date displayed as the latest modification date.

## Article Template

Generated clean URL pages and `render.html` share `includes/js/article-renderer.js`. Clean pages provide an embedded `article-config` block with the Markdown source path and canonical URL. `render.html` reads the `md` query parameter for old links. The shared renderer fetches Markdown, parses front matter, renders Markdown content, and shows title metadata directly under the title. The article footer reads `homepage-data.js` to find the current item and show adjacent notes:

- `较新`: previous item in reverse chronological order.
- `较早`: next item in reverse chronological order.

If the current note is not present in `homepage-data.js`, the article still renders but hides adjacent-note navigation.

## Archive Pages

All archive pages load the same script, `includes/js/archive-page.js`.

The page decides its mode from `body[data-collection]`:

- Empty value: show all notes.
- `Books`, `Thoughts`, `Study`, or `Videos`: show only that collection.

Each entry must display:

- publication date
- title
- content type
- creation date
- latest update date

## Maintenance Workflow

1. Add a Markdown note under `qrthoughts/yearYYYY/monthM/`.
2. Keep the filename format `[Type][0000][Title].md`.
3. Fill required front matter, especially date fields.
4. Run `python scripts/build_site.py`.
5. Verify homepage, clean article URL, legacy `render.html?md=...` URL, archive page, and relevant collection page locally.
