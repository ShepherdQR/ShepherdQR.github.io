# Homepage Scroll Repair

Date: 2026-07-14  
Workspace: `E:\Codes\ShepherdQR.github.io`

## Objective

Restore normal vertical scrolling on the public homepage, then validate and publish the repair.

## Completed

- Replaced the homepage root's two-axis `overflow: clip` declaration with horizontal-only clipping.
- Preserved the intended suppression of decorative horizontal overflow while restoring document-level vertical scrolling.
- Added a validator regression guard that rejects future homepage rules which set vertical overflow to `hidden` or `clip`.

## Evidence

- Files: `includes/css/homepage.css`, `scripts/validate_site.py`
- Checks: canonical site build, site validation, Python compilation, CSS regression assertion
- Delivery: the repair and this report ship together in one focused commit to `origin/master`.

## Decisions

- The fix is deliberately CSS-only at runtime; no JavaScript scroll handler or browser-specific workaround was introduced.
- Browser automation was not used because the task requested the repair and deployment, not interactive browser QA.

## Remaining

- None known for homepage scrolling.
