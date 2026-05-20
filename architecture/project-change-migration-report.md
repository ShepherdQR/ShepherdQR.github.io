# Project Change and Migration Report

## Document Control

| Field | Value |
| --- | --- |
| Title | Project Change and Migration Report |
| Status | Active |
| Started | 2026-05-20 |
| Scope | ShepherdQR GitHub Pages content architecture, migration, and cleanup decisions |

## Purpose

This report is the project-level migration ledger. It records major architecture changes, content migrations, cleanup decisions, verification results, and follow-up work. Detailed design documents remain in separate ADR-style files under `architecture/`.

## Current State

As of 2026-05-20:

| Area | State |
| --- | --- |
| Canonical content source | Markdown under `qrthoughts/` |
| Published data model | `homepage-data.js`, generated from Markdown front matter |
| Article renderer | `render.html` |
| Homepage | Markdown-backed homepage with portrait, collections, archive years, selected notes, and all notes |
| Archive pages | `archive.html`, `books.html`, `thoughts.html`, `study.html`, `videos.html` |
| Legacy HTML | 127 historical `.html` files under `qrthoughts/`; accepted decision is deleting 124 and temporarily retaining 3 named exception pages |

## Change Log

| Date | Change | Result | Reference |
| --- | --- | --- | --- |
| 2026-05-20 | Defined Markdown-first content architecture | Markdown selected as canonical article source | `site-content-architecture.md` |
| 2026-05-20 | Designed Markdown publishing workflow | New notes are created as Markdown and site data is generated | `markdown-publishing-workflow.md` |
| 2026-05-20 | Migrated historical public article data | 137 public items are Markdown-backed | `full-markdown-migration-report.md` |
| 2026-05-20 | Added homepage and article rendering upgrades | Homepage, archive pages, and article pages use generated Markdown data | `archive-and-article-page-design.md` |
| 2026-05-20 | Accepted legacy HTML deletion strategy | Delete old article HTML under `qrthoughts/`, retain three transition exceptions, and remove the old template page | `legacy-html-cleanup-strategy.md` |
| 2026-05-20 | Executed legacy HTML cleanup | Deleted 124 historical `.html` files, retained 3 named exceptions, and verified Markdown site output | This report |

## Legacy HTML Cleanup Ledger

Pre-deletion inventory from local audit on 2026-05-20:

| Category | Count |
| --- | ---: |
| Legacy HTML files under `qrthoughts/` | 127 |
| Markdown article files under `qrthoughts/`, excluding README files | 137 |
| HTML files with direct same-path Markdown counterparts | 123 |
| HTML files covered by standard `type/id` Markdown counterparts | 123 |
| HTML files without direct same-path Markdown counterparts | 4 |

Exception file decisions:

| Path | Decision | Reason |
| --- | --- | --- |
| `qrthoughts/others/BooksDoneIndex.html` | Temporarily retain | Legacy non-article index page |
| `qrthoughts/others/BooksItem.html` | Temporarily retain | Legacy non-article index/template page |
| `qrthoughts/year2020/month2/why-now.html` | Temporarily retain | Non-standard legacy URL; represented by `Thoughts/0001` Markdown |
| `qrthoughts/year2023/month10/[Books][0199][模板]-------.html` | Delete | Legacy template, not public content |

## Verification Requirements

Before deleting legacy HTML:

1. `scripts/build_site.py` must generate 137 Markdown-backed items.
2. Homepage must load and show generated Markdown data.
3. `archive.html` and collection pages must load generated Markdown data.
4. Representative article pages must render title, type/id, creation date, and update date.
5. Git status must be understood before deletion.

After deleting legacy HTML:

1. `rg --files -g "*.html" qrthoughts` should return only the three retained exception files.
2. `scripts/build_site.py` should still generate 137 Markdown-backed items.
3. Homepage, archive pages, collection pages, and representative article pages should pass local browser smoke tests.
4. The deletion should be committed as one isolated change.

## Legacy HTML Cleanup Result

Execution completed on 2026-05-20:

| Result | Count |
| --- | ---: |
| Historical `.html` files deleted under `qrthoughts/` | 124 |
| Temporarily retained exception `.html` files | 3 |
| Markdown-backed public items after rebuild | 137 |

Retained files:

| Path | Reason |
| --- | --- |
| `qrthoughts/others/BooksDoneIndex.html` | Legacy non-article index page retained temporarily |
| `qrthoughts/others/BooksItem.html` | Legacy non-article index/template page retained temporarily |
| `qrthoughts/year2020/month2/why-now.html` | Non-standard legacy URL retained temporarily |

Verification completed:

| Check | Result |
| --- | --- |
| `scripts/build_site.py` | Generated 137 Markdown-backed items |
| Remaining `qrthoughts/**/*.html` files | Only the three retained exception files |
| HTTP checks | Homepage, archive, collection pages, and representative article returned 200 |
| Browser checks | Archive 137, Books 122, Thoughts 12, Study 1, Videos 2; representative article rendered dates and neighbor link |

## Open Follow-Ups

| Item | Status |
| --- | --- |
| Delete legacy `.html` files under `qrthoughts/`, except three retained exceptions | Completed |
| Rebuild and smoke-test after deletion | Completed |
| Commit deletion as isolated migration change | Pending |
