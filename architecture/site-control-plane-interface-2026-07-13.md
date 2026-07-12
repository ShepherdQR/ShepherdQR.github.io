# Site Control-Plane Interface

Date: 2026-07-13
Status: implementation contract; dual visual system released for repository-local integration
Scope: information architecture, state semantics, visual direction, authority boundary, and acceptance criteria for `ShepherdQR.github.io`

## Decision

The site will evolve as a **human-owned public knowledge interface and
read-only epistemic projection** aligned with the symbiotic constraint-field
control plane.

It is not a live AGI console, a runtime surface, a broker interface, or the
source of truth for target repositories. The site publishes durable knowledge
objects and dated, source-aware descriptions of system evolution. Human
ownership, local validation, and explicit release remain the authority path.

The declarative public source for this interface is:

```text
data/site-plane.json
```

## Source Register

Site-local sources:

- `.control-plane.yaml` — L1 ownership, permissions, human gates, validators,
  freshness policy, and declared surfaces.
- `architecture/site-content-architecture.md` — Markdown-first static
  generation and scholarly knowledge-map direction.
- `architecture/site-content-form-and-publishing-cadence-plan-2026-07-10.md`
  — identity, five content pillars, public rhythm, and publication gate.
- `homepage-data.js` — current corpus projection and selected-entry identities.

Control-plane sources, relative to the companion control-plane repository:

- `control-plane-charter.md` — control/data-plane separation, evidence before
  completion, human gates, and local authority.
- `docs/asi-repo-group/brain-area-map.md` — human interfaces, controlled organs,
  and non-authority relationship rules.
- `docs/asi-repo-group/cross-repo-resident-agent-continuation-plan.md` — current
  resident-exchange, automation, and human-release boundaries.
- `reports/asi-repo-group/resident-agents/2026-07-12-wp8-completion-and-t12-candidate-baseline.md`
  — current WP8-complete baseline and non-adopted T12 candidate.
- `reports/skill-agent-research/2026-07-10-agent-collaboration-control-panel/04-control-panel-aesthetic-brief.md`
  — evidence-vitrine composition, source rail, and role-bearing color.
- `policies/visual-aesthetic-hard-rules.md` — evidence-object, provenance,
  rebuildability, and pairwise-review gates.

## Public Identity

The existing identity remains the organizing statement:

> 复杂智能系统架构者：以约束为骨、工程为证，构造可演化的人机共生秩序。

Recommended first-view copy:

```text
ZQR.WORLD · PUBLIC KNOWLEDGE INTERFACE

Pursuing Immortality

以约束为骨，以证据为脉，
让智能在可审查、可否决、可回滚的秩序中生长。

张启荣的公共知识界面：记录复杂智能、工程证据、数学结构、
治理与文明之间可追溯、可修正、可长期积累的连接。
```

A persistent boundary sentence should accompany any control-plane state view:

> 本站是人类拥有的公共知识发布面，不是运行中 AGI 的控制台；证据、消息、回执与可视化都不会自行产生执行权威。

## Information Architecture

The public hierarchy should prioritize epistemic navigation over content-type
navigation. `Books`, `Thoughts`, `Study`, and `Videos` remain useful filters,
but they are not the highest-level model of the work.

### 1. Field / 当前场

Homepage and first entry point:

- identity and boundary statement;
- current questions and declared narrative lines;
- a dated control-plane frontier snapshot;
- selected durable evidence objects;
- recent publications.

Each current line should show its question, evidence state, lifecycle state,
source date, and next human gate. It must not display activation controls.

### 2. Atlas / 知识图谱

Curated paths across the five public narrative lines:

1. 约束场与复杂智能；
2. 工程证据；
3. 数学结构；
4. 人、治理与文明；
5. 阅读、文学与诗。

The Atlas is a generated navigation projection, not a replacement for the
canonical Markdown sources.

### 3. Chronicle / 演化纪事

A dated, append-only public interpretation of important changes:

- accepted and completed work;
- refused or blocked paths;
- rollback evidence;
- superseded plans;
- candidates awaiting human review.

Historical records remain `as-known-at` snapshots. A later result may
supersede an older plan without rewriting the old record.

### 4. Evidence / 证据库

Durable research and engineering objects:

- Research Dossiers;
- Engineering Evidence Notes;
- source registers;
- validation receipts;
- negative cases and failure boundaries;
- task closeouts and recovery evidence.

Every major object should expose a quiet provenance rail without turning
source metadata into decorative noise.

### 5. System / 系统与器官

A read-only map of roles and boundaries:

- human intent interface;
- knowledge-evidence interface;
- constitutional control plane;
- bounded protocol, governance, research, training, and transfer organs;
- target-domain repositories;
- this public knowledge publishing surface.

The map must communicate that the control plane observes, constrains, routes,
and reviews; target repositories retain local truth, refusal, validation, and
release authority.

### 6. Archive / 全量档案

The complete reverse-chronological corpus with year, type, series, and tag
navigation. Archive density should not dominate the homepage.

## Current Baseline Contract

The public snapshot is dated **2026-07-12**.

### Structural frontier

- T11 has continuous finite engineering validation.
- This is an engineering analogue, not a general mathematical Topos proof or
  a claim that a universal Topos engine exists.

### Evolution frontier

- Evolution Chronicle WP0 through WP8 are complete within their bounded
  contracts.
- WP6 represents 100 deterministic synthetic role traces, not 100 running
  Agents or collective intelligence.
- WP7 represents five read-only, fail-closed organ-repository intakes; all five
  resolved as insufficient evidence and authorized no action.
- WP8 derived the T12 candidate `Federated Intent and Governed Egress`.

The only accurate T12 status is:

```text
candidate_not_adopted
```

Its candidate invariant is:

```text
Origin is federated; effect is governed.
意图源可以联邦化；效果出口必须受治理。
```

T12 has not changed the canonical T0-T11 registry, granted authority, or
self-enacted. WP0-WP8 completion is not AGI completion.

### Operational frontier

- L0 in-thread coordination is available.
- L2 active-local trace-only practice exists without a live watcher.
- L3 has sandboxed simulation-log infrastructure only.
- No broker process, guarded broker, resident-agent runtime, live event
  watcher, or target-local adapter is released by this baseline.

The WP6-WP8 validation records zero performed authority effects. That number
is scoped to those Chronicle records and must not be generalized into a claim
about all historical or external activity.

## Three-Dimensional State Semantics

A single label such as `Active` is forbidden for control-plane material because
it collapses evidence, lifecycle, and authority.

### Axis A: Evidence state

```text
observed | reported | derived | unknown
```

This axis answers how the claim is known and sets its truth ceiling.

### Axis B: Lifecycle state

```text
planned | released | executing | validating | completed
refused | rolled_back | superseded | deferred | blocked
```

This axis answers what happened to a bounded work object. `completed` does not
mean adopted, deployed, or authorized beyond that object's scope.

### Axis C: Authority effect

```text
none | separately_human_released | target_local_authorized | dual_gate
```

Public projections default to `none`. Evidence strength and lifecycle progress
cannot infer a stronger authority value.

T12 should therefore render as:

```text
Evidence: derived
Lifecycle: candidate_not_adopted
Authority effect: none
As known at: 2026-07-12
```

## Control Loop

The site loop is human-gated and event-driven:

```text
human intent
-> capture and authoring
-> source and evidence binding
-> local build and validation
-> human release decision
-> public projection
-> dated observation
-> revise, retire, or continue
```

Publication is a promotion decision, not a synonym for saving a file. The
normal editorial rhythm remains approximately 4-7 public items per month, with
weekly field/evidence work, monthly depth, and quarterly synthesis. A public
state snapshot becomes stale after 14 days unless it is re-observed.

No scheduled publisher, autonomous content promotion, heartbeat, watcher,
broker, or resident runtime is part of this interface contract.

## Visual Metaphor

The governing visual idea is:

> **An evolving evidence vitrine inside a constraint field.**

It combines a scholarly atlas, an archival instrument, and a museum-grade
evidence object. It must not become a glowing central brain, science-fiction
HUD, SaaS dashboard, decorative mood board, or generic card wall.

### Composition

- central object: current constraint field or evidence spine;
- side rail: accession id, status, source, validation date, and claim ceiling;
- lower sequence: Chronicle as conservation and change record;
- next gate: quarantine/review shelf, never an activation control;
- system map: sparse topology that shows boundaries and local ownership.

### Material and color

- quiet graphite, paper, archival labels, restrained glass, and fine rules;
- green only for verified evidence;
- amber for pending human gates;
- red for blocked, refused, or revoked paths;
- blue for simulation;
- neutral tones for dormant or unactivated structures.

The `zqr.world` mark remains quiet, compositionally supported, and outside the
main evidence object. Motion must be optional and respect reduced-motion
preferences. Text contrast and keyboard navigation are hard requirements.

### Dual Visual Profiles

The 2026-07-13 owner release keeps both reviewed directions and makes the
comparison reversible through one device-local switch. Content, state semantics,
URLs, evidence and authority boundaries are identical in both profiles.

| Profile | Primary object | Material logic | Role |
| --- | --- | --- | --- |
| `field` / 学术约束场 | scholarly public knowledge field | warm paper, ink, archival rules, restrained verdigris | long-form reading and calm public orientation |
| `museum` / 深层博物馆 | governed institutional artifact in a vitrine | obsidian field, cold glass, black stone, platinum hairlines, accession labels | evidence-object sovereignty, provenance and withheld authority |

The museum profile is derived from the canonical `AGI结构计划` v2 material
system, not from generic dark-mode or cyberpunk conventions. Its semantic
palette is:

- `#030708`: museum field / constitutional dark ground;
- `#f1ead9`: ivory primary label;
- `#a9f0ff`: glacial evidence and research path;
- `#4f9b91`: verified evidence only;
- `#7fa2c7`: mathematical or structural information;
- `#e9b86d`: human gate, review or withheld authority only;
- `#df6f66`: blocked, refused or revoked only.

Long-form articles use a dark museum shell with an archival folio
(`#f8f0de` / `#efe4cd`, ink `#11120f`) so the visual metaphor never damages
reading. The canonical museum reference is
`resources/pics/agi-structure-plan-nine-grid-v2.png`; `Thoughts 0028` keeps V1
and V2 as history but declares V2 as its lead image.

Forbidden shortcuts in both themes:

- dashboard or SaaS card-wall grammar as the primary composition;
- decorative glassmorphism, neon/cyberpunk, generic AI brain or mystical seal;
- red or amber as unowned decoration;
- infinite scan, pulse, shimmer, particles or parallax;
- any visual implication of runtime autonomy, target-write authority or global
  truth ownership.

The theme controller persists only a local viewing preference. It is not a
content mutation, governance decision or control-plane state change.

## Authority Boundary

The site is L1, human-owned, and advisory.

Allowed standing behavior:

- read declared surfaces;
- expose repository-relative provenance;
- render dated public knowledge projections;
- run declared local validators;
- produce advisory findings and control-plane-local records.

Separately human-gated behavior:

- target content or branch writes;
- direct commits and publication;
- mailbox delivery;
- resident or target-local Agent runtime;
- broker or connector enablement;
- capability grants and dependency changes;
- destructive operations;
- memory, policy, topology, governance-default, or runtime promotion.

Messages, route decisions, dashboards, Chronicle episodes, receipts, and
validated evidence cannot create or amplify authority. The stricter value
between the target manifest, control-plane registry, and action-specific human
release always wins; revocation is deny-wins.

Public JSON must contain only repository-relative references or public URLs.
Drive-letter paths, home directories, worktree paths, and machine-specific
locations are forbidden.

## Acceptance Criteria

The interface contract is acceptable when all of the following hold:

1. `data/site-plane.json` parses as UTF-8 JSON and remains deterministic.
2. The JSON declares `shepherdqr-site`, human ownership, L1 advisory mode, and
   `public_knowledge_publishing_site`.
3. It contains exactly five declared narrative lines whose directional weights
   total 100 without presenting them as publication quotas.
4. It records WP0-WP8 as complete while keeping T12 exactly
   `candidate_not_adopted` with `authority_effect=none`.
5. WP6 is described as synthetic traces with zero runtime Agent instances.
6. WP7 is described as read-only fail-closed intake with zero authorized
   actions.
7. No copy claims that a broker, watcher, runtime, resident Agent, target-local
   adapter, or autonomous publisher is running.
8. Evidence, lifecycle, and authority are displayed as separate dimensions.
9. Every current-state claim shows an `as_of` date and becomes visibly stale
   after the declared threshold.
10. Selected entries use stable `type` plus `id` pairs that exist in the
    generated corpus projection.
11. No public data contains an absolute local filesystem path.
12. Any future page consuming this data remains a read-only projection and
    exposes no write, activate, connect, grant, or publish control.
13. Major visual implementation work compares at least two directions and
    records the chosen evidence object, provenance route, material logic, and
    rejected moves.
14. Repository-local build and validation remain the final technical gate,
    followed by a separate human publication decision.

## Stopping Rule

This document and `data/site-plane.json` establish the public interface
contract. The active 2026-07-13 owner request separately authorizes the scoped
site integration, validation, commit and publication recorded in the target
manifest. Nothing here authorizes control-plane runtime behavior, mailbox or
broker operation, target-local execution, dependency change, or promotion of
memory, policy, topology or governance defaults.
