# Full Markdown Migration Report

## Document Control

| Field | Value |
| --- | --- |
| Title | Full Markdown Migration Report |
| Status | Implemented |
| Date | 2026-05-20 |
| Scope | Public article records under `qrthoughts/` |
| Primary Decision | Public article data is now Markdown-backed |

## 1. Summary

The public article list has been migrated from a manually maintained legacy table to Markdown front matter.

| Metric | Count |
| --- | ---: |
| Legacy HTML files audited | 127 |
| Markdown-backed public items | 137 |
| Public legacy index items, excluding old index pages | 137 |
| Missing public Markdown items after migration | 0 |

Current public Markdown type distribution:

| Type | Count |
| --- | ---: |
| Books | 122 |
| Thoughts | 12 |
| Videos | 2 |
| Study | 1 |

## 2. What Changed

1. Markdown files were generated next to legacy HTML article files when a public article id existed.
2. Existing Markdown files were not overwritten.
3. `homepage-data.js` is now generated from Markdown by default.
4. `render.html` is the shared article page template.
5. `index-data.js` is retained as legacy reference data, not as the active publishing table.

## 3. Date Preservation

Each migrated Markdown file preserves:

1. `created` and `created_date`.
2. `published`.
3. `updated` and `updated_date`.
4. `source.legacy_path`.
5. `source.date_source`.

When HTML comments had missing date data, the generated front matter records the fallback explicitly instead of hiding it.

Known fallback:

| Item | Date Handling |
| --- | --- |
| `Books/0029` | Missing HTML comment dates; `created` and `updated` fall back to `index-data` publication date `2022-05-29` with explicit source markers |

## 4. Review Items

The migration tool still reports these historical files as review cases:

| Path | Reason | Result |
| --- | --- | --- |
| `qrthoughts/others/BooksDoneIndex.html` | Non-article index page | Not part of public Markdown article list |
| `qrthoughts/others/BooksItem.html` | Non-article index page | Not part of public Markdown article list |
| `qrthoughts/year2020/month2/why-now.html` | Non-standard legacy filename | Covered by existing `Thoughts/0001` Markdown note |
| `Books/0021` | Rich image/math content | Migrated to Markdown, marked with migration complexity |
| `Books/0029` | Missing HTML comment dates | Migrated with explicit index-date fallback |
| `Study/0001` | D3 interactive content | Migrated with raw SVG/script preserved; `render.html` supports trusted embedded scripts |

## 5. Verification

The migration is accepted when:

1. `scripts/build_site.py` generates `homepage-data.js` from Markdown.
2. Markdown item count equals the public legacy content count: `137`.
3. Browser rendering confirms homepage records and article date headers.
4. Representative migrated articles render through `render.html`.

## 6. Follow-Up

Future cleanup can replace or remove old legacy HTML files once old URL compatibility is no longer required. Until that decision is made, the old HTML files should be treated as compatibility copies only.
