# Legacy HTML Cleanup Strategy

## Document Control

| Field | Value |
| --- | --- |
| Title | Legacy HTML Cleanup Strategy |
| Status | Accepted |
| Date | 2026-05-20 |
| Scope | Historical `.html` files under `qrthoughts/` |
| Primary Decision | Delete historical article HTML files after recording the migration state; temporarily retain three named legacy exception pages |

## 1. Purpose

The site now uses Markdown as the canonical content source. Legacy HTML files are no longer active article records, but they still exist in the repository and can still be served by GitHub Pages. This document defines how to remove them without losing date provenance or confusing future authoring work.

## 2. Current Inventory

Local audit on 2026-05-20:

| Category | Count |
| --- | ---: |
| Legacy HTML files under `qrthoughts/` | 127 |
| Markdown article files under `qrthoughts/`, excluding README files | 137 |
| HTML files with direct same-path Markdown counterparts | 123 |
| HTML files covered by standard `type/id` Markdown counterparts | 123 |
| HTML files without direct same-path Markdown counterparts | 4 |

The four exceptions are:

| Legacy Path | Classification | Recommended Handling |
| --- | --- | --- |
| `qrthoughts/others/BooksDoneIndex.html` | Legacy non-article index page | Temporarily retain |
| `qrthoughts/others/BooksItem.html` | Legacy non-article index/template page | Temporarily retain |
| `qrthoughts/year2020/month2/why-now.html` | Non-standard legacy article URL | Temporarily retain; content is represented by `Thoughts/0001` Markdown |
| `qrthoughts/year2023/month10/[Books][0199][模板]-------.html` | Legacy template, not public content | Delete |

Current active pages use Markdown-backed data and do not require these old article HTML files for normal navigation.

## 3. Cleanup Options

| Option | Description | Benefits | Costs | Decision |
| --- | --- | --- | --- | --- |
| Keep all legacy HTML in place | Leave files untouched indefinitely | Maximum compatibility; zero short-term risk | Keeps duplicate content and confusing authoring surface | Rejected |
| Delete old article HTML under `qrthoughts/`, retaining named exceptions | Remove old files once Markdown is stable and report is recorded | Clean repository and publish tree with a small transition exception set | Old direct article URLs stop serving content except retained pages | Accepted |
| Move old HTML to an archive folder | Preserve source copies outside their current paths | Keeps historical source visible | Still carries historical baggage inside the repo | Rejected |
| Replace old HTML with redirect stubs | Keep old URLs alive but route readers to Markdown pages | Preserves external links | Keeps 100+ compatibility files and generated URL machinery | Rejected for now |

## 4. Recommended Decision

Delete the historical article HTML files under `qrthoughts/` once the Markdown site is verified and the migration state is recorded.

This decision deliberately accepts that old direct `.html` article URLs may stop working. The project values a clean Markdown-first repository over maintaining broad compatibility files for historical URLs.

The deletion scope is limited to historical content HTML under `qrthoughts/`. It does not include active site shells such as:

1. `index.html`
2. `render.html`
3. `archive.html`
4. `books.html`
5. `thoughts.html`
6. `study.html`
7. `videos.html`

For the 123 directly mirrored article HTML files, Markdown files are the canonical replacements. For the four exceptions, keep three transition pages and delete the template page:

1. Temporarily retain `qrthoughts/others/BooksDoneIndex.html`.
2. Temporarily retain `qrthoughts/others/BooksItem.html`.
3. Temporarily retain `qrthoughts/year2020/month2/why-now.html`.
4. Delete `qrthoughts/year2023/month10/[Books][0199][模板]-------.html`.

## 5. Deletion Contract

Deletion must follow these rules:

1. Delete only `.html` files under `qrthoughts/`, except the three retained exception files.
2. Do not delete Markdown files, images, scripts, CSS, root page shells, or architecture documents.
3. Before deletion, record the inventory count and exception list in the project migration report.
4. Keep date provenance in Markdown front matter; do not depend on old HTML comments after deletion.
5. Run the site build and browser smoke tests after deletion.

## 6. Stability Gate

Do not perform destructive cleanup until all of these are true:

1. `scripts/build_site.py` succeeds and still generates 137 Markdown-backed public items.
2. Homepage, `archive.html`, collection pages, and representative article pages pass browser smoke tests.
3. The project migration report records the pre-deletion inventory.
4. The four exception files have explicit retain/delete decisions.
5. Git history already contains the old HTML bodies, and the deletion is committed as one isolated change.

## 7. Implementation Plan

1. Add or run an audit command that reports:
   - total legacy HTML files
   - direct Markdown counterpart coverage
   - `type/id` coverage
   - exception files
2. Update the project migration report with the pre-deletion state.
3. Delete all `.html` files under `qrthoughts/`, except the three retained exception files.
4. Run `scripts/build_site.py`.
5. Run local HTTP/browser checks for homepage, archive pages, collection pages, and representative Markdown-rendered articles.
6. Commit the deletion as one isolated commit.

## 8. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Old inbound links break | Accept this as a conscious simplification; active navigation no longer depends on old HTML |
| Dates are lost | Keep canonical dates in Markdown front matter; do not rely on HTML comments after cleanup |
| Migration scripts lose original HTML source | Keep git history and record the pre-deletion state in the migration report |
| Duplicate content affects search identity | Delete duplicate HTML article bodies |
| Future authors edit old HTML by mistake | Remove old bodies and document Markdown-only authoring |

## 9. Final Policy

Legacy HTML should move through two states:

1. **Compatibility Copy**: current state; old HTML bodies remain in place.
2. **Mostly Deleted**: accepted next state after the stability gate; article content body lives only in Markdown, with three named legacy pages temporarily retained.

The site should not return to authoring or maintaining article bodies in HTML.
