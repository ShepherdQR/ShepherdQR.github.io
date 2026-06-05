# Site Publishing Architecture Closeout

Date: 2026-06-06
Workspace: `E:\Codes\ShepherdQR.github.io`
Thread: ShepherdQR static site Markdown publishing and homepage redesign

## Objective

Unify the personal static site around Markdown source files, reduce manual table maintenance, preserve original note dates, improve the homepage and article reading experience, migrate historical article data, and leave a durable record of the architecture decisions and follow-up workflow.

This closeout was requested with the `codex-task-closeout` skill and records the recoverable state of the session.

## Completed

- Created architecture records under `architecture/`, including content architecture, Markdown publishing workflow, archive/article design, migration reports, cleanup strategy, and project change ledger.
- Redesigned the homepage into a warm, text-first scholar-style page using `resources/pics/QirongZHANG.png`, removing the older `Classic` and `Architecture` tabs.
- Standardized article metadata around Markdown front matter with `created`, `created_date`, `published`, `updated`, and `updated_date` treated as first-class fields.
- Migrated the public article corpus to Markdown-backed records and preserved original date information wherever available.
- Added generated clean article URL support such as `/books/0056/` and `/thoughts/0012/`, while retaining `render.html?md=...` as a legacy/debug reader.
- Added archive/category pages and shared archive rendering for `archive.html`, `books.html`, `thoughts.html`, `study.html`, and `videos.html`.
- Added build, note creation, migration, normalization, and validation scripts under `scripts/`.
- Added sitemap and Atom feed generation from the same Markdown metadata used by the homepage.
- Added GitHub Actions site hardening workflow through `.github/workflows/site-hardening.yml`.
- Documented the daily workflow in `README.md`, including creating a note, building, validating, previewing, and publishing.

## Evidence

Key architecture files:

- `architecture/site-content-architecture.md`
- `architecture/markdown-publishing-workflow.md`
- `architecture/full-markdown-migration-report.md`
- `architecture/archive-and-article-page-design.md`
- `architecture/legacy-html-cleanup-strategy.md`
- `architecture/project-change-migration-report.md`

Key implementation files:

- `index.html`
- `render.html`
- `homepage-data.js`
- `includes/css/homepage.css`
- `includes/css/pages.css`
- `includes/js/archive-page.js`
- `scripts/build_site.py`
- `scripts/new_note.py`
- `scripts/migrate_legacy_html_to_md.py`
- `scripts/normalize_markdown_front_matter.py`
- `scripts/generate_homepage_data.py`
- `scripts/validate_site.py`
- `sitemap.xml`
- `includes/atom.xml`

Observed project commits for the session sequence:

- `a39152e Add site content architecture design`
- `42960ad Upgrade homepage content architecture`
- `286d22e Unify articles on Markdown publishing workflow`
- `17504f6 Add archive pages and polish article layout`
- `d750842 Document publishing workflow`
- `1f8849e Add site hardening workflow`
- `533099e Harden site validation checks`
- `2425daa Generate sitemap and Atom feed`
- `2d28dd5 Support top markdown comments`
- `151cf50 Update [Thoughts][0013][关于token和工具的观察与思考].md`

Checks and commands used during the work included:

- `python scripts/build_site.py`
- `python scripts/validate_site.py`
- `python -m py_compile ...`
- Local HTTP checks against `http://localhost:8000/`
- Browser smoke checks for homepage, archive pages, clean article URLs, legacy `render.html?md=...` URLs, and representative migrated articles.

## Decisions

- Markdown front matter is the canonical data source. `index-data.js` is legacy reference input and should not be manually maintained for new notes.
- Generated files must be committed because GitHub Pages serves the repository statically.
- Original note dates are not cosmetic metadata; they define the chronology of the site and must be preserved near article titles.
- Clean generated URLs are public canonical URLs. The query-string Markdown reader remains useful for compatibility and debugging.
- Legacy HTML compatibility copies can be removed only after generated Markdown-backed pages and clean URLs are verified.
- New notes should be created through `scripts/new_note.py` and published through `scripts/build_site.py` plus `scripts/validate_site.py`.

## Current Dirty State

At final closeout verification, the only working-tree changes were this closeout report and the `architecture/README.md` index entry that points to it.

Earlier status output showed generated/content paths such as `homepage-data.js`, `includes/atom.xml`, `sitemap.xml`, `qrthoughts/year2026/month6/`, and `thoughts/0014/`; a full untracked and diff check before commit showed those paths were already tracked/clean and did not need to be included in this report commit.

## Lessons

- For static sites on GitHub Pages, "automatic" should mean a deterministic local build script, not runtime directory discovery.
- A single Markdown source plus generated read models is easier to verify than parallel tables, copied HTML templates, and script-embedded prose.
- Dates need explicit source markers during migration; silent fallbacks would create future historical ambiguity.
- Legacy pages with `var string = ...; writeString(string);` are highly migratable when handled as a structured legacy pattern instead of as arbitrary HTML.
- Browser checks are important after visual or generated URL changes; command-line HTTP checks alone do not execute the client rendering path.
- Generated files need strong validation because stale generated artifacts are easy to commit accidentally.

## Skill Or Agent Extraction Review

Recommended skill candidate:

- `github-pages-markdown-publisher`
- Purpose: operate Markdown-first GitHub Pages sites with front matter, generated clean URLs, sitemap/feed generation, local preview, validation, and commit hygiene.
- Trigger examples: "add a new note", "rebuild the site", "migrate this note", "validate generated pages", "publish the static site".
- Why useful: this workflow is repeatable, stateful, and easy to get subtly wrong if build, validation, and generated files are not handled together.

Recommended skill candidate:

- `legacy-html-note-migrator`
- Purpose: convert historical HTML notes, especially `var string`/`writeString` pages, into Markdown while preserving dates and source provenance.
- Trigger examples: "convert old HTML notes to Markdown", "audit migration complexity", "preserve note dates".
- Why useful: the migration rules are specialized enough to preserve as reusable operational knowledge.

Possible repo-local agent:

- `site-publisher`
- Role: run `scripts/build_site.py`, `scripts/validate_site.py`, inspect generated diff, smoke test representative pages, and prepare a focused publishing commit.
- Recommendation: useful later if publishing becomes frequent. Do not create it until the team wants automated publishing behavior, because it would need strict rules around generated files and unrelated dirty worktree changes.

No new skill or agent was installed during this closeout. The above are extraction recommendations only.

## Remaining

- Decide whether to create the proposed Codex skills or keep the knowledge in this repository's architecture docs.
- Continue treating generated site artifacts as build outputs that must be validated before publishing.
- Continue using `scripts/validate_site.py` before any publish commit.

## Final State

- Branch at report creation: `master`.
- Closeout report path: `architecture/task-closeouts/2026-06-06-site-publishing-closeout.md`.
- The report is intended to be committed and pushed separately from pre-existing content/generated-file changes.
