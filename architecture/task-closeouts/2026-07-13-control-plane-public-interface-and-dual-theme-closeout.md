# Control-Plane Public Interface And Dual Theme Closeout

Date: 2026-07-13
Workspace: `E:\Codes\ShepherdQR.github.io`
Thread: repository, structure, form, aesthetics, and AGI control-plane alignment

## Objective

Evolve the repository and public site so its information architecture,
engineering form, visual language, and governance semantics match the current
AGI control-plane direction, while preserving the Markdown-first GitHub Pages
workflow, human authority, existing user work, and explicit L1 advisory
boundaries. Add a persistent museum-grade visual profile derived from the ASI
material-object series without reducing it to generic dark mode.

## Completed

- Reframed the site as a human-owned public knowledge data plane with four
  primary surfaces: Field, Atlas, Evidence, and System.
- Added `data/site-plane.json` as the declarative public projection and
  generated `site-data.js` through the existing deterministic build.
- Added `field.html` for the human-gated control loop, dated WP0-WP8 baseline,
  T12 `candidate_not_adopted` boundary, operational denials, and provenance.
- Rebuilt the homepage around five narrative lines, fresh evidence, corpus
  pulse, curated entry paths, and the author's complex-intelligence identity;
  removed the duplicate all-notes wall from the homepage.
- Upgraded Archive and collection pages into a static Atlas with search plus
  type, year, series, and tag filters whose state persists in the URL.
- Upgraded `stats.html` into an Evidence observatory for corpus shape, metadata
  coverage, authority boundaries, dated evolution state, and current evidence.
- Added a shared accessible design system and a device-local profile switch:
  - `Field / 学术约束场`: warm paper and editorial archive;
  - `Museum / 深层博物馆`: governed institutional artifact aesthetics using
    an obsidian field, cold glass, accession labels, and semantic gate colors.
- Bound Museum mode to the control-plane aesthetic canon: canonical nine-grid
  v2, `#030708` field, ivory labels, glacial evidence cyan, verified green,
  human-gate amber, and blocked/refused/revoked red. Articles use a dark museum
  shell with an archival paper folio for sustained readability.
- Added theme support to every generated article, the legacy reader, Series,
  and root pages; added article reading progress, estimated time, taxonomy
  links, heading anchors, and a responsive object index without a dependency.
- Backfilled explicit summary, tags, and series for Thoughts 0014-0029 and
  0031. Thoughts 0028 now explicitly uses the canonical ASI nine-grid v2 lead
  image while preserving V1/V2 history in the article body.
- Preserved and released the pre-existing Thoughts 0031, generated discovery
  artifacts, README example, and prior complete-session closeout.
- Extended the validator and CI to check the public projection, human/L1/T12
  authority invariants, disabled runtime flags, visual profiles, root metadata,
  canonical museum reference, theme scripts, and JavaScript syntax.

## Evidence

- Implementation commit: `470f599` (`Evolve site into control-plane knowledge interface`)
- Primary contract: `architecture/site-control-plane-interface-2026-07-13.md`
- Public projection: `data/site-plane.json`, `site-data.js`
- Interface surfaces: `index.html`, `archive.html`, `stats.html`, `field.html`
- Visual system: `includes/css/system.css`, `includes/js/theme.js`
- Build: `python scripts\build_site.py` -> 159 Markdown-backed items, 159
  article aliases, sitemap, Atom feed, and site projection generated.
- Determinism: aggregate generated-artifact fingerprint remained
  `732981c4a3ec6e6f9c6b6a07798c5e6450c224ee` across consecutive builds.
- Validation: `python -B scripts\validate_site.py --max-warnings 50` -> 159
  items checked, 28 known warnings, 0 errors, result `OK`.
- Static quality: all Python files compiled; all client JavaScript passed
  `node --check`; CSS brace balance and root-page duplicate-id checks passed;
  `git diff --check` passed.
- Theme persistence smoke: stored Museum preference applied before page binding.
- HTTP smoke: homepage, Atlas query, Evidence, System, Series, Thoughts 0028,
  Thoughts 0031, generated data, shared CSS, and theme script all returned 200;
  expected interface markers and generated article theme binding were present.

## Decisions

- Kept the existing framework-free static architecture and introduced no new
  dependency, database, runtime, broker, connector, or hosting surface.
- Used the museum visual canon structurally: object sovereignty, provenance,
  material meaning, label discipline, withheld authority, and semantic color.
  Rejected dashboard/card-wall, decorative glassmorphism, neon/cyberpunk,
  generic AI-brain, infinite motion, and autonomy-overclaim shortcuts.
- Kept Field and Museum as reversible viewing profiles over identical content,
  evidence, URLs, and authority semantics; the switch is not governance state.
- Used the 2026-07-12 WP8 record as the dated current baseline. WP0-WP8 evidence
  completion does not mean AGI completion; T12 remains a non-adopted candidate;
  broker, watcher, resident runtime, target adapter, and autonomous publishing
  remain disabled or unauthorized.
- Treated the active 2026-07-13 owner request as the scoped target write,
  commit, and publication release recorded in `.control-plane.yaml`.

## Remaining

- The 28 historical validator warnings remain: eight multi-H1 article bodies
  and twenty file-header/front-matter timestamp differences. None were created
  by this implementation; clean them through natural content maintenance.
- Article bodies still depend on runtime Markdown rendering and the external
  `marked` script. Build-time HTML and a no-JavaScript article fallback are the
  next durability frontier and may require a separate dependency decision.
- No automated screenshot or browser visual-regression pass was performed.
  A human review of both profiles at desktop/mobile sizes, including normal,
  math, interactive, and poster-led articles, remains the appropriate final
  taste arbitration.

## Final State

- Branch: `master`
- Implementation commit: `470f599`
- The implementation and this closeout are intended for the same
  `origin/master` release.
- No unrelated repository or control-plane working tree was staged by this
  closeout.
