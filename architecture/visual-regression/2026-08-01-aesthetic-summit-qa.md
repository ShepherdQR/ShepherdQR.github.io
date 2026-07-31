# 2026-08-01 Aesthetic Summit Visual Regression QA

Date: 2026-08-01

Workspace: `E:\Codes\ShepherdQR.github.io`

Status: accepted

Decision owner: human owner instruction to complete P0-P3 and preserve the Museum-mode【局部真理宪章】exhibit

## Verdict

The aesthetic summit implementation passes release review. Three independent read-only reviews found no P0 or P1 visual issue, no horizontal overflow, no component collision, and no internal clipping. Field and Museum retain the same content, state, provenance, and authority semantics while using different material profiles.

The Museum-mode【局部真理宪章】is a hard non-regression invariant and passed all three parts of its contract:

1. switching from Field to Museum hydrates and displays the responsive Charter exhibit;
2. System / Charter Room retains the same Charter object and local-ownership meaning in both profiles;
3. a first Field load does not request the Museum-only Charter image.

## Rebuildable visual matrix

The ignored, reproducible output lives at `output/playwright/aesthetic-summit-2026-08-01/`. Its manifest records 48 PNG files with byte counts and SHA-256 hashes.

| Dimension | Coverage |
| --- | --- |
| Profiles | Field, Museum |
| Viewports | 1440 × 1100 desktop, 390 × 844 mobile |
| Root instruments | Field, Atlas Constellation, Evidence, System, Chronicle |
| Article forms | exposition, research log, reading, visual essay |
| Long ledger | start, middle, and end viewport samples for both profiles and both viewport sizes |
| Total | 36 full-page images + 12 segmented Ledger images = 48 |

Rebuild command, with an available `playwright-cli` executable:

```powershell
.\scripts\capture_visual_matrix.ps1 -CliPath <path-to-playwright-cli> -IncludeChronicle
```

The screenshot bundle is intentionally excluded from Git. The script, surface definitions, capture logic, and hash manifest contract are committed so the evidence can be regenerated without treating transient pixels as source.

## Acceptance results

### Field and System

- Current Exhibition remains the five-second central object in Field.
- The portrait and Charter keep their intended aspect ratios at both viewport sizes.
- Museum labels, accession metadata, and Charter microcopy remain readable.
- System presents the Charter Room, sparse local-ownership topology, human-gated loop, and one negative vitrine without simulating runtime control.

### Atlas and Evidence

- Constellation and Ledger are visibly distinct instruments.
- The Constellation contains a central `PUBLIC KNOWLEDGE FIELD / 163` hub and non-overlapping narrative nodes.
- Ledger samples prove real, non-repeating start, middle, and end positions; Field and Museum show the same entries and year semantics.
- Evidence Spine exposes summary provenance, mapping provenance, revisions, dated baseline, stale state, and authority ceiling.
- The 2026-07-12 projection correctly reports 20 days of age on 2026-08-01 and is visibly stale.

### Articles and Chronicle

- All 163 canonical public URLs contain build-rendered semantic article bodies.
- Exposition, research log, reading, and visual essay have distinct form-aware compositions.
- V1/V2 provenance, supersession, Charter references, lead media, and folio rails render in Field and Museum at both viewport sizes.
- Chronicle is an independent as-known-at temporal spine and is present in sitemap and Atom discovery.

## Defects found and closed during QA

1. HTML image dimensions were being interpreted as fixed rendered height in shared CSS, stretching the portrait and Charter. Images now preserve intrinsic aspect ratios.
2. Atlas had an unmapped-node collision and lacked a strong center. Positioning was corrected and the public-knowledge hub was added.
3. Article `content-visibility` interacted with full-page capture and produced blank lazy media. The reader now renders media reliably in regression captures.
4. Freshness used timestamp arithmetic that could drift by timezone. It now uses local calendar-day arithmetic.
5. The accessibility skip link leaked into full-page screenshots. Its clipped resting state and focus restoration are now explicit.
6. Chromium repeated the page top when stitching the 20k-36k-pixel Ledger beyond a 16,384px capture boundary. Those invalid four images were removed; the capture contract now uses twelve honest start/middle/end viewport samples.

## Engineering validation

| Check | Result |
| --- | --- |
| `python -B scripts/build_site.py` | 163 Markdown items, 163 stable aliases, sitemap, Atom, and site data generated |
| `python -B scripts/test_templates.py` | 9 passed |
| `python -B scripts/test_article_durability.py` | 6 passed |
| `python -B scripts/image_pipeline.py --check` | 17 masters and 22 responsive derivatives verified |
| `python -B scripts/validate_site.py --max-warnings 50` | 0 errors, 41 non-blocking historical/editorial warnings, result OK |
| `python -B scripts/validate_aesthetic_system.py` | 0 errors, 0 warnings |
| Python compile check | passed |
| `node --check` for `includes/js` | passed |
| `git diff --check` | passed; line-ending notices only |

The aesthetic validator measured 282,495 bytes for the first Field transfer and 341,787 bytes for Museum, both comfortably below the 1.5 MiB and 3 MiB budgets. AVIF generation is not supported by the available local browser and is reported honestly; committed WebP derivatives satisfy the runtime contract.

## Non-blocking observations

- `candidate_not_adopted` can hard-wrap inside one narrow desktop authority cell.
- Five curated entries in a 3 × 2 arrangement intentionally leave one open slot.
- Some Museum monospace metadata is close to the lower readability bound but remains acceptable.
- The mobile Ledger is intentionally long; a future year jump or sticky index could improve navigation without changing truth semantics.
- One research-log SVG contains source-canvas whitespace, and reading-form full-page captures are naturally very tall.
- Ledger middle/end samples include normal entry edges entering or leaving the viewport; this is sampling, not CSS clipping.

None of these observations weakens the accepted composition or the Museum Charter invariant. Any future material change to a root surface must regenerate this matrix and create a superseding dated exhibition record.
