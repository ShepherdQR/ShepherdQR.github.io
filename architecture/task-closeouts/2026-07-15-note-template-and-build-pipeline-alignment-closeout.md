# Note Template and Build Pipeline Alignment

Date: 2026-07-15
Workspace: `E:\Codes\ShepherdQR.github.io`

## Objective

Align the new-note authoring template with the current knowledge-interface article template and confirm that the site build pipeline includes the latest generated surfaces.

## Completed

- Updated `scripts/new_note.py` so every new note emits a stable metadata shape containing `summary`, `tags`, `series`, `lead_image`, `math`, and `interactive` fields.
- Added `--lead-image`, `--math`, and `--interactive` authoring options while preserving automatic id allocation, file-header comments, front matter, and optional site rebuilding.
- Versioned the generated article shell as `knowledge-note-v2` and aligned its navigation with Field, Atlas, Evidence, System, and Series.
- Added the Field/Museum default binding, skip link, main-content target, and current `ZQR.WORLD` identity to every generated article page.
- Extended `scripts/validate_site.py` to reject stale article shells or mismatched template configuration.
- Added `scripts/test_templates.py` and wired it into the site-hardening workflow.
- Updated the README authoring examples and metadata specimen without replacing the user's in-progress example edit.

## Evidence

- `python -B scripts/test_templates.py` -> 3 tests passed.
- `python -B -m py_compile scripts/new_note.py scripts/build_site.py scripts/validate_site.py scripts/test_templates.py` -> passed.
- `python scripts/build_site.py` -> 160 Markdown-backed items, 160 article aliases, sitemap, Atom feed, and `site-data.js` generated.
- A consecutive second build reproduced all 164 generated files with zero hash drift.
- `python -B scripts/validate_site.py --max-warnings 50` -> 160 items, 30 historical/content warnings, 0 errors, result OK.
- `git diff --check` -> passed.

## Decisions

- Empty optional metadata fields remain explicit in new notes so the authoring contract is stable without inventing summaries, tags, series, or imagery.
- Article HTML remains generated rather than manually maintained; the build script is the canonical source of the public article shell.
- Existing user changes to Thoughts 0031, the new Thoughts 0032 source, and their generated discovery data were preserved.
- Browser automation was not used because interactive browser QA was not requested.

## Remaining

- The implementation is local and uncommitted because this request did not explicitly authorize a commit or push.
- The current working tree also contains the user's in-progress 0031/0032 content and generated publication changes; those should be reviewed and released together only when the user requests it.
