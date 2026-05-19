# Legacy HTML to Markdown Migration

## Document Control

| Field | Value |
| --- | --- |
| Title | Legacy HTML to Markdown Migration |
| Status | Implemented |
| Date | 2026-05-20 |
| Scope | Historical article files under `qrthoughts/` |
| Primary Decision | Convert historical HTML notes into Markdown sources only when original date information can be preserved |

## 1. Purpose

The site should unify content at the data layer before fully upgrading the presentation layer. Historical HTML notes should be converted into Markdown with explicit front matter so the homepage, archives, feeds, and future static article pages can be generated from one canonical content format.

This migration must preserve original date information. A converted note without trustworthy creation and update dates is not considered successfully migrated.

## 2. Migration Principles

1. Markdown becomes the canonical editable content source.
2. Legacy HTML files remain available until generated replacements are verified.
3. Dates are first-class metadata, not incidental comments.
4. Migration is incremental and reviewable.
5. The first implementation should produce previews and reports before writing in place.
6. Pages with complex JavaScript or unusual layout can be deferred.

## 3. Required Date Contract

Every migrated Markdown file must contain:

```yaml
---
created: "2022-10-15 21:41:23"
created_date: "2022-10-15"
published: "2022-10-15"
updated: "2023-03-05 14:08:44"
updated_date: "2023-03-05"
source:
  legacy_path: "qrthoughts/year2022/month10/[Books][0056][论语-孔子].html"
  date_source:
    created: "html-comment"
    published: "index-data"
    updated: "html-comment"
---
```

Rules:

1. Preserve exact timestamps when the source contains them.
2. Preserve date-only fields for grouping and display.
3. Prefer explicit source metadata over filesystem timestamps.
4. If `published` cannot be found in `index-data.js`, use `created_date` and mark the source as `created-date-fallback`.
5. If `created` or `updated` cannot be found in the legacy HTML comment, mark the file for manual review.
6. Do not invent dates.

## 4. Date Source Priority

Creation date priority:

1. HTML header comment `@Date`.
2. HTML header comment `Date`.
3. Existing Markdown front matter if present.
4. Manual review.

Update date priority:

1. HTML header comment `@LastEditTime`.
2. HTML header comment `LastEditTime`.
3. Existing Markdown front matter if present.
4. Manual review.

Publication date priority:

1. Matching `index-data.js` entry.
2. Existing Markdown front matter `published`.
3. `created_date` fallback with explicit source marker.

Filesystem timestamps are allowed only as diagnostic hints. They must not silently become canonical note dates.

## 5. Complexity Levels

| Level | Description | Default Action |
| --- | --- | --- |
| Level 1 | Plain article prose with simple paragraphs | Auto-convert preview |
| Level 2 | Lists, blockquotes, code blocks, or `writeString` prose | Auto-convert preview, then review |
| Level 3 | Images, tables, MathJax, or mixed HTML | Convert preview and require review |
| Level 4 | D3, canvas, iframe, custom interactive scripts | Defer or preserve HTML |

## 6. Pilot Plan

The first migration task should process a representative sample before bulk conversion:

1. One ordinary book note.
2. One long prose or poetry note.
3. One page with many `writeString` blocks.
4. One page with ordered lists.
5. One special or interactive page that should be deferred.

The pilot output should include:

1. Markdown preview files or stdout previews.
2. A migration report.
3. A list of files requiring manual review.
4. A count by complexity level.
5. A count of date extraction success and failure.

## 7. Conversion Rules

HTML to Markdown conversion should:

1. Extract the article title from filename, front matter, `<title>`, or heading.
2. Extract type and id from filename when available.
3. Convert `writeString` template literals into plain Markdown paragraphs.
4. Convert `<br>` into line breaks.
5. Convert `<hr>` into Markdown thematic breaks.
6. Convert `<li>` into Markdown list items.
7. Convert links into Markdown links.
8. Convert images into Markdown image syntax.
9. Strip repeated template boilerplate.
10. Preserve unknown or complex HTML only when conversion would lose meaning.

## 8. Non-Destructive Output Policy

The migration tool must default to dry-run behavior.

Allowed write modes:

1. Preview output directory, preserving relative paths.
2. In-place `.md` creation only when explicitly requested.
3. No overwrite unless explicitly requested.

During the pilot, generated Markdown should be treated as review material, not final content.

## 9. Review Checklist

For each migrated note, verify:

1. Title is correct.
2. Type and id are correct.
3. Creation date is present and matches the legacy source.
4. Update date is present and matches the legacy source.
5. Publication date is present or intentionally falls back to creation date.
6. Body text is not truncated.
7. Lists remain readable.
8. Links and images remain valid.
9. Complex pages are not silently flattened.

## 10. Acceptance Criteria

The migration is successful when:

1. The tool can audit all legacy HTML files without modifying them by default.
2. The tool can produce Markdown previews or in-place Markdown files explicitly.
3. Every generated Markdown file includes date metadata or explicit fallback source markers.
4. Complexity levels are reported.
5. Homepage data can be regenerated from Markdown without relying on the legacy table.
