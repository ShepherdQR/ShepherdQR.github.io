# Legacy Migration Pilot Report

## Document Control

| Field | Value |
| --- | --- |
| Title | Legacy Migration Pilot Report |
| Date | 2026-05-19 |
| Scope | First audit and Markdown preview run for legacy HTML notes |
| Tool | `scripts/migrate_legacy_html_to_md.py` |

## 1. Summary

The first migration tool pass can audit all legacy HTML files without modifying them. It also generated five representative Markdown preview files under `architecture/migration-pilot/`.

Current full-audit result:

| Metric | Count |
| --- | ---: |
| Legacy HTML files audited | 127 |
| Ready without required review | 121 |
| Needs review or defer | 6 |
| Level 1 plain pages | 39 |
| Level 2 list/script-text pages | 86 |
| Level 3 rich content pages | 1 |
| Level 4 interactive pages | 1 |

## 2. Pilot Preview Set

| Source | Result | Reason |
| --- | --- | --- |
| `qrthoughts/year2021/month11/[Books][0011][算法图解-Aditya Bhargava].html` | Ready | Plain note |
| `qrthoughts/year2021/month12/[Books][0013][[20世纪世界诗歌译丛](第一辑)保罗·策兰诗文选].html` | Ready | Long text and script-text conversion |
| `qrthoughts/year2021/month12/[Books][0021][初等代数_北京市初等数学编写组_1975].html` | Review | Image-rich content |
| `qrthoughts/year2022/month5/[Study][0001][JavaScript-D3.js].html` | Defer/review | D3 interactive page |
| `qrthoughts/others/BooksItem.html` | Review | Special index page without standard type/id filename |

Generated preview files:

| Preview |
| --- |
| `architecture/migration-pilot/qrthoughts/year2021/month11/[Books][0011][算法图解-Aditya Bhargava].md` |
| `architecture/migration-pilot/qrthoughts/year2021/month12/[Books][0013][[20世纪世界诗歌译丛](第一辑)保罗·策兰诗文选].md` |
| `architecture/migration-pilot/qrthoughts/year2021/month12/[Books][0021][初等代数_北京市初等数学编写组_1975].md` |
| `architecture/migration-pilot/qrthoughts/year2022/month5/[Study][0001][JavaScript-D3.js].md` |
| `architecture/migration-pilot/qrthoughts/others/BooksItem.md` |

## 3. Date Preservation Result

The pilot previews preserve:

1. `created` exact timestamp from the legacy HTML comment.
2. `created_date` normalized date.
3. `published` date from `index-data.js` when available.
4. `updated` exact timestamp from the legacy HTML comment.
5. `updated_date` normalized date.
6. `source.legacy_path`.
7. `source.date_source` for created, published, and updated dates.

Example:

```yaml
created: "2021-08-05 15:40:21"
created_date: "2021-08-05"
published: "2021-11-25"
updated: "2022-09-17 00:07:30"
updated_date: "2022-09-17"
source:
  legacy_path: "qrthoughts/year2021/month11/[Books][0011][算法图解-Aditya Bhargava].html"
  date_source:
    created: "html-comment"
    published: "index-data"
    updated: "html-comment"
```

Important observation:

Several older pages share the same `created` timestamp from the legacy template. The migration keeps this value because it exists in the source, but the generated page should also show `published` and `updated` so the visible chronology remains meaningful.

## 4. Conversion Quality Notes

What worked:

1. `writeString` prose was extracted into Markdown.
2. `<br>` and `<hr>` were converted into readable Markdown spacing.
3. Standard filename patterns were parsed into `type`, `id`, and `title`.
4. Images with `src = "..."` spacing were recognized after rule refinement.
5. Chinese-heavy titles now fall back to stable id-based slugs such as `books-0021`.

What still requires review:

1. Special pages under `qrthoughts/others/` do not use standard type/id filenames.
2. D3 and interactive pages should not be flattened into ordinary Markdown without a manual decision.
3. Image-rich pages need visual verification after final static generation.
4. Some legacy `created` timestamps may reflect template creation rather than note creation.

## 5. Recommended Next Step

Proceed with the homepage/data contract upgrade only after keeping the migration script in dry-run mode:

1. Add front matter to existing Markdown notes using the same date contract.
2. Generate homepage data from Markdown metadata.
3. Redesign the homepage around the new metadata.
4. Keep legacy HTML migration as a controlled, reviewable track.

