# Site Content Form And Publishing Cadence Plan

Date: 2026-07-10
Status: owner-review candidate; persisted plan; not yet a publishing commitment
Scope: `ShepherdQR.github.io` content forms, editorial rhythm, metadata discipline, and control-plane observation boundary

## Executive Summary

The site no longer has a content-scarcity problem. It has a selection and
rhythm problem: 158 published notes already form a substantial corpus, while
recent publication is concentrated in short bursts. The next stage should make
the site read like the public thinking system of a complex intelligent systems
architect, rather than a chronological export of every captured thought.

The recommended operating model is a dual loop:

- capture freely and frequently in `draft` or local workroom form;
- publish selectively at a sustainable public rhythm of roughly 4-7 items per
  month, with one durable anchor note per week, one deep synthesis per month,
  and optional short signals only when they add a distinct claim.

The site should retain its breadth—software, agents, mathematics, governance,
reading, literature, and poetry—but organize that breadth around one identity:

> 复杂智能系统架构者：以约束为骨、工程为证，构造可演化的人机共生秩序。

## Source Register

| Source | Date/version | Used for | Confidence |
| --- | --- | --- | --- |
| `README.md` | 2026-07-10 working tree | Authoring, build, validation, and metadata workflow | High |
| `homepage-data.js` | 2026-07-10 generated | Corpus size, type mix, dates, summaries, content features | High |
| `index.html` | 2026-07-10 working tree | Public identity and homepage information architecture | High |
| `architecture/site-development-plan.md` | 2026-07-03 | Existing site phases and technical priorities | High |
| `qrthoughts/year2026/month7/[Thoughts][0023][最近关切的5个问题].md` | 2026-07-03 | Explicit current-interest inventory | High |
| Recent `Thoughts` 0014-0030 | 2026-06 to 2026-07 | Observed research and writing themes | High |
| `scripts/generate_homepage_data.py` | 2026-07-10 working tree | Metadata and content-feature generation contract | High |
| `scripts/validate_site.py` | 2026-07-10 working tree | Current quality gates and residual warnings | High |

## Current Evidence

### Corpus Shape

| Metric | Current value |
| --- | ---: |
| Published notes | 158 |
| Books | 125 |
| Thoughts | 30 |
| Study | 1 |
| Videos | 2 |
| 2026 publications through July 7 | 27 |
| 2026 May publications | 7 |
| 2026 June publications | 9 |
| 2026 July publications through July 7 | 11 |

Books are about four-fifths of the historical corpus. Recent growth, however,
is driven by `Thoughts`: ASI structure, constraint fields, agent symbiosis,
Topos, tropical symmetry, mechanical-engineering intelligence, AI-for-AI,
governance, civilization, model/tool observations, and visual-generation
experiments.

The recent rhythm is bursty: four items were published on 2026-07-03 and three
on 2026-07-04. This is useful during exploration, but it makes durable pieces
compete with each other for attention and weakens the distinction between
capture and publication.

### Technical Publishing Baseline

The 2026-07-10 implementation slice now provides:

- summaries for all 158 generated items, using explicit front matter first and
  a plain-text excerpt fallback;
- propagation support for `summary`, `tags`, `series`, `math`, `interactive`,
  and `lead_image`;
- article descriptions and Open Graph metadata;
- conditional runtime loading: three math articles load MathJax, one
  interactive article loads D3, and ordinary articles load neither;
- validator-backed local HTML references and Markdown images;
- non-blocking warnings for multiple body H1 headings and file-header/front
  matter time disagreement;
- 28 current warnings and zero blocking validation errors.

## Editorial Identity And Content Pillars

The site should not split the author's interests into unrelated channels. Each
pillar should answer a different part of the same question: how durable
intelligence, knowledge, and action can be structured under real constraints.

| Pillar | Core question | Typical material | Target share of new public work |
| --- | --- | --- | ---: |
| Constraint fields and complex intelligence | What structures make intelligence governable and evolvable? | ASI, agents, symbiotic constraint fields, world models, control planes | 30% |
| Engineering evidence | What survives contact with implementation? | Architecture decisions, release lessons, evals, failures, tool/model comparisons | 25% |
| Mathematical structure | What invariant or geometry explains the system? | Topos, tropical symmetry, derivatives, category-theoretic or geometric compression | 15% |
| Human, governance, and civilization | What should technical power serve and refuse? | Governance, political judgment, civilization inheritance, AI boundaries | 15% |
| Reading, literature, and poetry | What expands the language and interior structure of the system builder? | Reading constellations, author studies, poems, literary essays | 15% |

These percentages are directional, not quotas. They prevent the public surface
from becoming either a pure engineering log or an unstructured reading ledger.

## Recommended Content Forms

| Form | Length/depth | Purpose | Public rhythm |
| --- | --- | --- | --- |
| Signal Note | 200-600 Chinese characters | One observation, distinction, or hard sentence; no attempt at completeness | At most 1 per week |
| Field Note | 800-1,800 characters | One claim developed through a concrete system, text, event, or experiment | About 1 per week |
| Research Dossier | 2,500-6,000+ characters with sources | Durable theory/evidence synthesis; becomes a reference node | 1 per month |
| Engineering Evidence Note | Event-sized; includes decision, evidence, failure boundary, next gate | Convert implementation work into reusable knowledge | 1-2 per month, event-driven |
| Reading Constellation | 3-5 related books or one deep work | Replace fragmented reading records with a thematic map | 1 per month |
| Quarterly Synthesis | Cross-links prior notes and revises the map | State what changed in the author's model of the world | 1 per quarter |

Long posters, diagrams, and generated images remain welcome as the chosen
visual form. They should support the note rather than determine whether the
note is publishable.

## Publishing Cadence

### Public Rhythm

- Weekly anchor: publish one Field Note or Engineering Evidence Note.
- Optional signal: publish at most one genuinely distinct Signal Note in the
  same week.
- Monthly depth: publish one Research Dossier.
- Monthly reading: publish one Reading Constellation; it may replace that
  week's anchor instead of increasing volume.
- Quarterly: publish one synthesis and update curated paths.

This produces a normal range of 4-7 public items per month. A month with one
excellent dossier and three field notes is healthier than a forced daily feed.

### Burst Rule

- Publish no more than two new items in any rolling 72-hour window.
- Keep overflow as `draft`; schedule it after the current item has had time to
  stand alone.
- Exception: a deliberately packaged series release may exceed the limit when
  every item has an explicit sequence and landing page.

### Capture Rhythm

Capture remains unconstrained. Daily fragments, work logs, quotations, failed
attempts, and speculative branches may accumulate locally. Publication is a
promotion decision, not a synonym for saving work.

## Publication Gate

A new public item should satisfy all of the following:

1. It contains one identifiable claim, distinction, result, or experience.
2. It has enough evidence for its form: example, source, experiment, or clearly
   labeled inference.
3. It is likely to remain useful after 90 days.
4. It has `summary`, at least one `tag`, and a `series` when it belongs to a
   continuing line.
5. Its heading hierarchy and local references pass validation.
6. It links backward or forward when another note is conceptually adjacent.
7. It is public because it clarifies the author's system, not merely because it
   was completed today.

## Metadata And Series Plan

Start with recent `Thoughts` and homepage-selected notes rather than
backfilling all 158 items.

Recommended initial series:

- `约束场与复杂智能`
- `Agentic Software Engineering`
- `数学结构札记`
- `工程证据与发版之后`
- `治理、文明与人的尺度`
- `阅读星图`
- `诗与内部结构`

Recommended initial tags:

- `ASI`, `agent`, `constraint-field`, `software-engineering`, `evaluation`
- `Topos`, `tropical-geometry`, `mathematics`
- `governance`, `civilization`, `AI-boundary`
- `reading`, `literature`, `poetry`

## Ninety-Day Rollout

### Month 1: Establish The Contract

- Backfill explicit summaries, tags, and series for Thoughts 0014-0030 and the
  five homepage-selected notes.
- Reduce the 28 validator warnings only when those articles are naturally
  touched; do not bulk-rewrite historical prose.
- Publish under the 4-7 item monthly cap and record which forms were used.

### Month 2: Make Themes Navigable

- Add archive filters for tag and series.
- Create two curated paths: `约束场与复杂智能` and `治理、文明与人的尺度`.
- Convert `Selected Notes` from hard-coded IDs to explicit metadata or a small
  curated data file.

### Month 3: Evaluate The Rhythm

- Add content-form and series counts to `stats.html`.
- Publish the first monthly/quarterly synthesis that links prior work.
- Review whether 4-7 items per month produces stronger pieces and clearer
  discovery than the July burst pattern.

## Success Measures

- 100% of new public notes have explicit `summary` and at least one tag.
- At least 80% of new public notes belong to a declared pillar or series.
- Monthly public output normally stays between 4 and 7 items.
- At least one durable dossier or synthesis appears each month.
- Site validation remains at zero blocking errors.
- Historical warnings trend from 28 toward 10 through natural maintenance,
  not mass cosmetic rewriting.
- The homepage can explain the author's identity, current lines of work, and
  strongest entry points without requiring the reader to scan `All Notes`.

## Control-Plane Boundary

The website may be onboarded to
`symbiotic-constraint-field-control-plane` at L1 advisory level. The control
plane may read declared surfaces, run declared validators, preserve this plan,
and write control-plane-local reports or dashboards. It does not receive
standing authority to publish, commit, push, start a resident agent, deliver a
mailbox message, enable a broker, or modify site content without a new explicit
human release and target-local authorization.

## Next Decision

After owner review, choose one next implementation slice:

1. metadata backfill for recent Thoughts and selected notes; or
2. tag/series archive navigation.

Do not start both until the owner accepts this content rhythm and the homepage
profile statement.
