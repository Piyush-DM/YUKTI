# YUKTI Motion System v1.0
### The Official Animation & Interaction Specification for YUKTI

**Status:** Canonical — v1.0
**Scope:** All YUKTI surfaces (investigation workspace, evidence graph, verification pipeline, reports, public site)
**Audience:** Engineers implementing motion, designers extending the system, reviewers auditing conformance
**Governing principle:** *Motion in YUKTI exists to make reasoning legible — never to decorate it.*

---

## 0. How to Read This Document

This is a **design system specification**, not a style guide. Every token has a name, a value, and a rule for when it applies. Every component has a state machine, not just a "hover effect." If an implementation detail isn't listed here, it isn't approved yet — propose it via the extension process in Section 14 before shipping it.

Nothing in this document is aesthetic preference. Every rule traces back to one governing constraint: **YUKTI is institutional reasoning software.** People use it to decide whether a claim is true, whether a source is credible, whether a conclusion holds. Motion that entertains, surprises, or delays that judgment is a defect, not a flourish.

---

## SECTION 1 — Motion Philosophy & Principles

### 1.1 The Governing Constraint

YUKTI's users are evaluating evidence under time pressure and reputational stakes. Every animation decision is filtered through one question: **does this motion help someone trust their own understanding of what they're looking at, faster?** If the answer is no, the motion is cut.

### 1.2 Motion Language

**Deceleration only.** No bounce, no elastic, no overshoot, anywhere in the system, ever. Every custom easing curve resolves monotonically — objects arrive and stop, they do not oscillate past their target and settle back. Overshoot reads as "playful" or "uncertain"; YUKTI's findings are neither.

**Two tempos, not a spectrum.** The system has exactly two motion registers:
- **Responsive** (120–300ms) — for anything the user directly triggered (click, hover, toggle). Must feel instantaneous even though it isn't.
- **Deliberate** (600–1600ms) — for anything that changes the user's understanding of the evidence (a panel opening a new claim, a graph reclustering, a chart drawing itself). Must feel considered, never rushed.

There is no 400–500ms tier. Motion in that gap reads as *hesitant* — neither a reflex nor a decision — and is banned by rule (see Section 10).

**Physical, not decorative.** Where elements represent data (evidence nodes, confidence scores, source clusters), motion should behave like the data has mass and the interface has friction — spring interpolation, not decorative tweening. Where elements are pure UI chrome (menus, buttons, tabs), motion should behave like precision mechanism — clean eased transitions, no physical metaphor implied.

### 1.3 Pacing

Nothing animates unprompted except a single, tightly-scoped entry sequence (Section 8.1). Everything else is triggered by one of exactly three things: **user intent** (click, hover, drag), **visibility** (an element entering the viewport), or **state change** (new evidence arrived, a verification completed). Motion never runs "to fill time" — no ambient looping decoration, no idle micro-animations without informational content behind them, with the single documented exception of confidence-visualization idle-drift (Section 4.5), which exists to signal "this dataset is alive," not to entertain.

### 1.4 Interaction Philosophy

**Demand-driven, not scroll-driven-for-its-own-sake.** Scroll triggers entrance and reveals content; it does not drive a cinematic camera. YUKTI does not simulate a "virtual camera" traveling through a 3D space — that metaphor implies spectacle, and spectacle is the wrong register for a reasoning tool. The one deliberate exception — the scrubbed verification pipeline (Section 8.3) — uses scroll as a literal, 1:1 proxy control, never an eased or cinematic one.

### 1.5 Visual Hierarchy & Perceived Weight

Typography and structured data lead; illustrative/decorative imagery is nearly absent. Where visualization exists, it is *functional* — a confidence bar, an evidence cluster, a citation graph — never purely atmospheric. Perceived weight scales with epistemic weight: the heavier the claim being examined, the more deliberate (not the more dramatic) its motion.

### 1.6 Continuity

Every surface in YUKTI enters via the same small set of primitives (Section 9). Continuity comes from **repetition of a small vocabulary**, not from bespoke per-screen choreography. A user who has seen one panel open has effectively seen all of them open — this predictability is a trust feature, not a limitation.

### 1.7 Whitespace & Exclusion Zones

Any generative or clustering visualization (evidence graphs, source distributions) must compute and respect a **text exclusion zone** around any headline, claim statement, or control panel it shares a canvas with. Data visuals decorate around meaning; they never obscure it. This is a hard rule, not a suggestion — see Section 10, Rule 6.

### 1.8 Transition Philosophy

**Morph the state, don't replace the instance.** A rotating headline word, a swapped verification tab, a re-clustering evidence graph — all reuse one element and change its state, rather than destroying and recreating DOM. This keeps focus, scroll position, and screen-reader context stable across every transition in the system.

---

## SECTION 2 — Motion Token Foundation

All values below are the literal design tokens. Implement as CSS custom properties (or the equivalent in your component framework's token layer) under the `--yukti-` namespace. **No engineer hand-writes a duration or a bezier curve inline** — every animation references one of these tokens by name.

### 2.1 Duration Scale

| Token | Value | Register | Use for |
|---|---|---|---|
| `--yukti-duration-instant` | 120ms | Responsive | Icon color/opacity flips, focus rings |
| `--yukti-duration-quick` | 200ms | Responsive | Hover states, button presses, tab underline |
| `--yukti-duration-standard` | 300ms | Responsive | Toggle switches, checkbox states, tooltip show |
| `--yukti-duration-deliberate` | 600ms | Deliberate | Panel slides, modal takeovers, sidebar collapse |
| `--yukti-duration-reveal` | 800ms | Deliberate | Section/card entrance on scroll |
| `--yukti-duration-cinematic` | 1600ms | Deliberate | Chart/graph line-draw, confidence-timeline reveal |
| `--yukti-duration-count` | 1080ms | Deliberate | Numeric counters (fixed 45-step cadence, 24ms/step) |

**The 400–500ms gap is intentionally empty.** If you find yourself reaching for it, you've picked the wrong register — round down to `quick`/`standard` if the trigger was direct user action, or up to `deliberate` if it changes what the user understands.

### 2.2 Easing Scale

| Token | Curve | Character | Reserved for |
|---|---|---|---|
| `--yukti-ease-standard` | `cubic-bezier(.2,.7,0,1)` | Fast start, long soft settle (deceleration) | The default for almost everything: reveals, bars, chart fills, hover states |
| `--yukti-ease-emphasis` | `cubic-bezier(.76,0,.24,1)` | Symmetric ease-in/ease-out ("snap") | **Reserved exclusively for the single highest-weight takeover in a given surface** — the report/investigation modal, the primary navigation panel. Using this curve elsewhere dilutes its signaling value; see Rule 2 |
| `--yukti-ease-micro` | `cubic-bezier(.2,.8,.2,1)` | Slightly softer decel, quicker settle | Small controls: tab switches, chip toggles, icon-button presses |
| `--yukti-ease-linear` | `linear` | No shaping | Counters, scroll-scrub-driven transforms (the scroll itself is the "ease"), progress bars whose fill must read as literal data, not styled motion |
| `--yukti-ease-spring` | *(not a CSS curve — a per-frame physics model, see 2.4)* | Critically damped | Evidence-node/cluster repositioning |

**No bounce or elastic token exists in this system.** This is not an oversight — it is the single most important rule in the palette. See Rule 1.

### 2.3 Distance & Transform Scale

| Token | Value | Use for |
|---|---|---|
| `--yukti-distance-xs` | 4px | Micro-nudges (accordion chevrons, focus indicators) |
| `--yukti-distance-sm` | 12px | Hover lifts, small card entrances |
| `--yukti-distance-md` | 30px | Standard reveal-on-scroll translateY |
| `--yukti-distance-lg` | 60px | Large section entrances, hero-scale reveals |
| `--yukti-tilt-max` | 6deg | Maximum rotateX/rotateY for any cursor-parallax card (see 10, Rule 12 — capped lower than decorative sites because YUKTI cards often carry dense data-labels that must stay legible) |

### 2.4 Spring Constant (for canvas/data-physics motion)

```
position += (target - position) * k
k = 0.06   // cluster re-grouping (evidence graph, source map)
k = 0.04   // idle ambient drift (slower, calmer — signals "settled," not "searching")
```

Always computed per animation frame inside a `requestAnimationFrame` loop — never expressed as a CSS transition. This is the one motion category in the system that is physics-driven rather than curve-driven, because it represents literal data relationships repositioning, not a UI state change.

### 2.5 Opacity & Layer Scale

| Token | Value | Use |
|---|---|---|
| `--yukti-opacity-hidden` | 0 | Entry/exit states |
| `--yukti-opacity-muted` | 0.35 | De-emphasized/inactive data points |
| `--yukti-opacity-idle-pulse` | 0.35 ↔ 1 | Reserved solely for the "awaiting input" hint pulse (Section 4.1) |
| `--yukti-opacity-full` | 1 | Resting/active state |

### 2.6 Z-Layer Scale

| Layer | z-index | Contents |
|---|---|---|
| `canvas` | 1 | Generative/data visualizations |
| `veil` | 2 | Legibility gradient overlays above canvases |
| `content` | 3 | Text, controls |
| `nav` | 100 | Persistent navigation |
| `panel` | 500 | Slide-in panels (report viewer, filters) |
| `modal` | 900 | Full-takeover modals |
| `toast` | 950 | Live-activity notifications |
| `consent` | 999 | Cookie/consent, system-level overlays |

---

## SECTION 3 — Motion Architecture: Surface Types

YUKTI is composed of five recurring **surface types**, each with its own default motion posture. Every screen in the product is an instance of one of these — new screens should map onto an existing type before a new one is proposed.

### 3.1 Landing / Narrative Surface
Public-facing, scroll-driven, explains what YUKTI is and how the reasoning pipeline works. Motion posture: reveal-heavy, one scrubbed pipeline section, generative evidence-graph hero. (Full spec: Section 8.)

### 3.2 Investigation Workspace
The primary product surface — where a user explores claims, evidence, and confidence scores. Motion posture: near-zero ambient motion; almost everything is state-change-triggered (new evidence arrives, a filter changes, a node is selected). Entrance reveals are used sparingly here — once a user is *working*, motion should defer entirely to their input.

### 3.3 Verification Pipeline View
A staged, sequential view of how a claim moved from ingestion to conclusion. Motion posture: the scrubbed-pipeline pattern (Section 4.3) and the pillar-tab pattern (Section 4.4) both live here.

### 3.4 Evidence & Confidence Dashboard
Aggregate, data-dense views (source distribution, confidence-over-time, agent activity). Motion posture: canvas/SVG visualization primitives (Section 4.5–4.8), all viewport-gated.

### 3.5 Report / Modal Overlay
Full-screen or full-panel takeovers presenting a finished report or a single claim's full evidence trail. Motion posture: the one place `--yukti-ease-emphasis` is used.

---

## SECTION 4 — Component Inventory

Every component below specifies: purpose, state machine, motion per transition, and governing tokens.

### 4.1 Primary Navigation

- **States:** `resting` (transparent, over hero/canvas) → `scrolled` (background applied) → `suppressed` (hidden during the entry sequence, Section 8.1).
- **Transition `resting ↔ scrolled`:** triggered at a fixed scroll offset (40px), not velocity-aware. `transition: background var(--yukti-duration-standard), padding var(--yukti-duration-standard)`. No transform, no scale — background/padding only.
- **Logo:** hover opacity `1 → 0.8`, `--yukti-duration-quick`.
- **Rule:** navigation never hides on scroll-down/reveals on scroll-up. It is always present once the entry sequence completes — a reasoning tool's wayfinding must never play hide-and-seek with the user.

### 4.2 Primary Panel / Modal Takeover (Report Viewer, Full Navigation)

- **Purpose:** the system's single "big moment" — opening a full report, a complete evidence trail, or full site navigation.
- **States:** `closed` (`translateY(-102%)`, `opacity:0`, `visibility:hidden`) → `open` (`translateY(0)`, `opacity:1`, `visibility:visible`).
- **Motion:** `transition: transform var(--yukti-duration-deliberate) var(--yukti-ease-emphasis), opacity var(--yukti-duration-deliberate) var(--yukti-ease-emphasis)`.
- **Side effects:** body scroll lock; `Escape` closes; backdrop click closes; focus trapped inside while open, returned to trigger element on close.
- **Rule:** this is the **only** component permitted to use `--yukti-ease-emphasis`. If a second component in the same surface uses it, one of them is wrong (Rule 2).

### 4.3 Verification Pipeline Scrubber (scroll-linked horizontal track)

- **Purpose:** presents the claim lifecycle — **Ingest → Corroborate → Cross-Check → Weigh → Conclude → Publish** — as a horizontally-traveling sequence driven by vertical scroll.
- **Mechanism:** sticky-height technique, **not** a scroll-jacking fixed-position pin. Section height = `trackScrollWidth − viewportWidth + viewportHeight`. On scroll (rAF-throttled, one calculation per frame via a `ticking` guard):
  ```
  p = clamp((scrollY - sectionTop) / dist, 0, 1)
  track.style.transform = translate3d(-p * dist, 0, 0)
  progressBar.style.width = (p * 100) + '%'
  ```
- **Easing:** `--yukti-ease-linear` — the user's own scroll motion *is* the easing; the system never re-interprets it.
- **Recalculation triggers:** `resize`, `load`, and — critically — after `document.fonts.ready` resolves, since font-swap reflow changes text width and therefore `scrollWidth`. Skipping this reintroduces the exact desync bug this pattern exists to avoid.
- **Responsive fallback:** disabled below 760px; stages render in normal vertical flow instead.
- **Rule:** this pattern must never be implemented via a scroll-jacking pin. See Rule 5 for why.

### 4.4 Verification Stage Tabs (pillar interactive)

- **Purpose:** interactive diagram of the reasoning methodology's stages, letting a user click into any stage's detail without leaving the page (companion/alternate presentation to 4.3, used in dashboard and report contexts).
- **States:** one stage `active` at a time (strict single-select — see Rule 9); clicking swaps the detail panel's text and supporting diagram.
- **Motion:** panel content swap is instant (no crossfade) — the stage-tab click is a **responsive**-register interaction (the user just told the system exactly what they want to see; delaying that with a transition reads as friction, not polish).
- **Statement emphasis ("lit" text):** within any long-form explanatory statement inside this component, key phrases may progressively emphasize (weight/color shift) as they cross a **stricter** intersection threshold (60%, vs. the default 12% for block reveals — see 4.9) — used for word-level emphasis inside a paragraph the reader is actively scrolling through, not for block entrance.

### 4.5 Evidence & Source Cluster Visualization (canvas)

- **Purpose:** the generative, re-clusterable visualization of evidence nodes, sources, or entities — the dashboard-and-landing-page equivalent of a data "living map."
- **States:**
  - `scattered` — initial/idle distribution, gentle independent drift per node (`k = 0.04`, angular offset per node so nothing is ever perfectly static).
  - `clustered[facet]` — nodes spring-interpolate (`k = 0.06`) toward positions grouped by the active facet (By Source / By Confidence / By Date / By Claim Type / By Cross-Reference).
  - `highlighted` — nearest-node-to-cursor detection; hovered/nearby node brightens and shows a label.
- **Exclusion zone:** the visualization computes a rectangle it must avoid — any headline, claim statement, or facet-control panel sharing the canvas — recalculated on resize. This is not optional (Rule 6).
- **Lifecycle:** must be wrapped in `viewport-gated-canvas` (Section 9) — the render loop starts only once the canvas crosses into view and stops the instant it leaves. No canvas in YUKTI runs unconditionally except the single entry-sequence visualization (Section 8.1), which is exempt because it plays before scrolling is possible.
- **Facet switching:** single-select buttons, instant `.active` class swap, triggers the `clustered[facet]` spring re-target — no transition delay on the button itself (**responsive** register), but the *node* motion is **deliberate** (spring settles over roughly 15–20 frames, ≈250–330ms at 60fps, reading as smooth reconfiguration rather than an instant jump-cut of data).

### 4.6 Confidence Bars

- **Purpose:** visualize confidence/coverage/weight-of-evidence by category.
- **Motion:** `width: 0 → target%`, `transition: width var(--yukti-duration-cinematic-short, 1100ms) var(--yukti-ease-standard)`, triggered once via intersection at 30% visibility.
- **Hover:** tooltip with the underlying figure, source count, and named supporting evidence — shown/hidden via class toggle, no animation beyond the tooltip's own `--yukti-duration-quick` fade.

### 4.7 Institutional Stat Counters

- **Purpose:** headline figures (sources verified, cross-checks completed, claims resolved).
- **Motion:** linear count from 0 to target over `--yukti-duration-count` (45 steps × 24ms), triggered once at 50% visibility. **Deliberately unenlaced** — no easing — because a counting number reads as more literal, more auditable, without stylistic shaping.
- **Optional cursor-parallax tilt (desktop, motion-safe only):** `rotateY/rotateX` up to `--yukti-tilt-max` (6deg, lower than a typical marketing-card tilt — see 2.3), plus a smaller inner-layer parallax offset. Fully disabled under `prefers-reduced-motion`, and disabled by default in the Investigation Workspace surface type (3.2) — tilt is a landing/dashboard flourish, not a workspace behavior.

### 4.8 Confidence-Over-Time / Coverage Timeline (SVG)

- **Purpose:** shows how confidence, coverage, or evidence volume accumulated over the life of an investigation.
- **Motion:** path drawn via `stroke-dasharray`/`stroke-dashoffset`, `transition: stroke-dashoffset var(--yukti-duration-cinematic) var(--yukti-ease-standard)`, triggered one frame after the path enters the DOM (required so `getTotalLength()` is measurable before the transition starts).
- **Milestone nodes:** individually fade in (`opacity 0→1`, `--yukti-duration-quick`-ish, ~450ms — a documented, deliberate exception at the slow end of the responsive register because these are discrete, cursor-inspectable data points, not a single continuous reveal); active node renders larger and in the accent color.
- **Rebuild policy:** full teardown/rebuild on resize rather than transform-scaling in place — correctness over animation continuity when the underlying data grid changes shape.

### 4.9 Reveal-on-Scroll (the universal entrance primitive)

- **Purpose:** the default entrance for any block — heading, card, finding, section.
- **States:** `pending` (`opacity:0; transform: translateY(var(--yukti-distance-md))`) → `revealed` (`opacity:1; transform:none`).
- **Motion:** `transition: opacity var(--yukti-duration-reveal) var(--yukti-ease-standard), transform var(--yukti-duration-reveal) var(--yukti-ease-standard)`.
- **Trigger:** `IntersectionObserver({threshold: 0.12})`, fires once, then unobserves — **no re-trigger on scroll-up** (Rule 4).
- **Stagger:** 4-slot repeating delay pattern — `(index % 4) * 60ms` — regardless of group size, so large groups never take multiple seconds to finish revealing.
- **Accessibility:** under `prefers-reduced-motion: reduce`, this component is **structurally** disabled (opacity 1, transform none, transition none) — not merely shortened.

### 4.10 Live Agent / Pipeline Activity Board

- **Purpose:** real-time view of active verification jobs, running agents, or in-flight source pulls — the "the system is working right now" surface.
- **Motion:** split-flap character-reveal per updated cell — `rotateX(86deg) → rotateX(0)`, `opacity 0.3 → 1` — evoking a mechanical, audit-log register rather than a soft crossfade. This is the one place in the system where a slightly more "mechanical" motion signature is intentional: it signals *this data is live and discrete*, not smoothly interpolated.
- **Live values (clocks, counts):** direct text replacement, no animation — motion budget is spent on the flap transition, not on the digits themselves.
- **Activity notifications ("new evidence found," "cross-check completed"):** toast-style, spawn at randomized positions within a pre-defined safe band that never overlaps headline or index labels (same exclusion-zone principle as 4.5), fade in/out over `--yukti-duration-standard`.
- **Row expansion (detail-on-demand):** `opacity 0→1` + `translateY(-4px)→0`, `--yukti-duration-standard`.

### 4.11 Facet / Filter Controls

- **Purpose:** single-lens reclassification of any dataset (evidence, sources, findings) by one facet at a time.
- **States:** strict single-`active` model — clicking a facet button removes `.active` from all siblings and adds it to the clicked one. **No multi-select filter UI exists anywhere in the system** (Rule 9).
- **Motion:** instant `.active` swap on the control itself (**responsive**); downstream effects (re-clustered canvas, re-sorted list) use their own component's motion spec (e.g., 4.5's spring re-target).

### 4.12 Rotating Framing Word / Rotating Locale Text

- **Purpose:** reframes a single word in a fixed headline slot (e.g., what YUKTI *is*: "Reasoning System" / "Evidence Layer" / "Verification Engine" / "Analysis Framework") without restating the whole headline.
- **Motion:** cross-fade cycle — add `.swap` state, wait `--yukti-duration-standard` (300ms), swap text content, remove `.swap` state. Full cycle interval: 2400ms for editorial/headline contexts, 1600ms for lighter contexts (e.g., a rotating locale greeting in a contact surface).
- **Rule:** whole-word swap only. No character-by-character or line-split animation exists anywhere in this system (Rule 11).

---

## SECTION 5 — Typography Motion System

| Element type | Split strategy | Reveal direction | Opacity | Trigger | Duration/Ease |
|---|---|---|---|---|---|
| Section headings, finding statements | Block (whole element) | Up (`--yukti-distance-md`) | 0→1 | IO @ 12% | `--yukti-duration-reveal` / `--yukti-ease-standard` |
| In-paragraph claim/phrase emphasis | Pre-marked phrase-level spans | In place (no translate) | Weight/color state only | IO @ 60% (stricter) | Not eased-in-place — instant class application on threshold cross, since this represents "the reader has now read this," not an entrance |
| Rotating framing word / locale text | Whole word | Cross-fade | swap-state driven | Interval timer | `--yukti-duration-standard` in/out |
| Modal/report headline | Block | Inherits parent panel opacity | 0→1 | Panel open | `--yukti-duration-deliberate` |

**Hard rule: no character-level or line-level split-text animation anywhere in YUKTI**, including the marketing/landing surface. This is not a technical limitation — the system is fully capable of it. It's excluded because per-character cascade reads as decorative performance, which actively undermines an institutional register. Typography motion in this system never goes below the word.

---

## SECTION 6 — Data & Visualization Motion (replaces "image motion")

YUKTI has almost no decorative imagery — its visual language is data, not photography. This section replaces what would otherwise be an "image motion" spec.

- **No parallax photography, no clip-path image reveals, no scroll-linked image scale/rotate exist in the system.** Where a screenshot, diagram, or document excerpt must appear (e.g., inside a report), it enters via the standard `reveal-on-scroll` primitive (4.9) and nothing more — data and document artifacts are presented, not staged.
- **Generative visualization is the system's actual "imagery."** Evidence clusters, confidence graphs, and source maps (Section 4.5, 4.8) occupy the role a hero photograph would occupy on a marketing site — this is a deliberate substitution: *the data is the visual*, not an illustration of the data.
- **Loading state:** no blur-up or shimmer skeleton for visualizations — a visualization either has data and renders, or is in an explicit, labeled "gathering evidence…" state (text, not a decorative spinner animation) until it does.

---

## SECTION 7 — Navigation Grammar

- **Sticky, always-present** once the entry sequence (8.1) completes. Never hide-on-scroll-down.
- **Scroll-awareness is binary**, not velocity-based: a single fixed threshold (40px) toggles the `scrolled` background state.
- **Hover system:** primary nav links use a **padding/indent nudge + color change**, not an underline-draw — text steps toward the reading direction on hover. Secondary controls (icon buttons, tab chips) use the underline/border variant instead, so the two hover grammars stay visually distinct and mean different things (primary wayfinding vs. local control).
- **Active states:** exactly one active item per navigation/facet group at all times — never zero, never multiple (Rule 9).
- **The primary panel takeover (4.2)** is the only navigation-adjacent component permitted to use `--yukti-ease-emphasis`.

---

## SECTION 8 — Landing Surface: Scene Architecture & Transitions

*(Applies specifically to Surface Type 3.1 — the public/narrative surface. Product surfaces, 3.2–3.5, do not use an entry sequence or scroll-scrubbed pipeline.)*

### 8.1 Entry Sequence (single unconditional animation in the entire system)

- On first load of the landing surface only: navigation and headline are suppressed (`opacity:0; pointer-events:none`) while a generative evidence-graph visualization plays a short establishing sequence — nodes coalesce from a scattered field into a structured, headline-avoiding arrangement (mirrors the spring-cluster model of 4.5, run once, unconditionally, before scroll is possible).
- On completion: navigation and headline cross-fade in over `--yukti-duration-deliberate` × ~1.5 (900ms), `--yukti-ease-standard`.
- **This is the one animation in the system allowed to run without a viewport/intent gate**, because it occurs before the user has any surface to scroll or click — there is nothing else competing for the frame budget at that moment.

### 8.2 Scene Sequence (landing surface, top to bottom)

| Scene | Purpose | Entry mechanism | Persistent | Temporary |
|---|---|---|---|---|
| Entry | Establish "this is a living reasoning system" before any copy is read | 8.1 sequence | Evidence-graph canvas (persists into Hero) | Entry overlay |
| Hero | State what YUKTI is; let the visitor probe the live evidence graph | Canvas continues; rotating framing word | Nav, canvas, headline | Facet controls |
| Thesis | Explain the reasoning methodology at a glance | `reveal-on-scroll` (4.9) | Heading | 3 stage summaries |
| Capability Overview | Breadth of what YUKTI analyzes/verifies | `reveal-on-scroll`, static field (no scroll-scrub here) | — | Category term field |
| Selected Investigations | Credibility via concrete past work | `reveal-on-scroll`, hover detail | Cards | Hover states |
| Verification Pipeline | The claim-to-conclusion journey, scrubbed | Scroll-scrub track (4.3) | Progress bar | 6 stage cards |
| Methodology Stages | Interactive deep-dive per stage | `reveal-on-scroll` + click-to-swap (4.4) | Stage nav | Detail panel, supporting diagram |
| Evidence Dashboard | Prove the system with live, real numbers | Independent per-canvas IO gates (4.5–4.8) | Section heading | 4 visualization widgets |
| Trust Signals | Institutional partners/citations | Facet filter (4.11), instant | Filter controls | Logo/citation wall |
| Live Operations | "The system is always working" | Flap-board (4.10), independent timers | Board grid | Activity toasts |
| Contact / Engage | Conversion + human touchpoint | `reveal-on-scroll`, rotating locale text | Contact block | — |
| Footer | Legal, secondary nav | `reveal-on-scroll` | — | — |

### 8.3 Transition Rules Between Scenes

There is no master scroll-scrubbed camera timeline joining scenes together — each scene reveals independently via 4.9 or its own gated mechanism. Continuity across scenes comes from three things only: (1) the persistent navigation, (2) the shared token vocabulary (Section 2), and (3) recurring headline figures (verified sources, cross-checks, resolved claims) reappearing in different visual forms across scenes. This is a deliberate architecture choice — see Rule 5 and Rule 7.

---

## SECTION 9 — Reusable Motion Primitives (implementation library)

Each primitive below is a named, drop-in unit. Reference by name in code comments and design specs so implementations stay traceable to this document.

### `reveal-on-scroll`
Standard block entrance. IO threshold 0.12, once. `opacity 0→1`, `translateY(--yukti-distance-md)→0`. `--yukti-duration-reveal` / `--yukti-ease-standard`. 4-slot stagger (`(i%4)*60ms`). Structurally disabled under reduced motion.

### `word-swap-crossfade`
Fixed-slot word rotation. Interval-driven (2400ms editorial / 1600ms light). `--yukti-duration-standard` fade each direction.

### `spring-cluster`
Physics-driven re-grouping for any node/particle visualization. `pos += (target-pos) * k`; `k=0.06` active reclustering, `k=0.04` idle drift. Must run inside `requestAnimationFrame`, never as a CSS transition.

### `confidence-fill`
Bar/gauge fill from 0 to a data value. IO @ 0.3, once. `--yukti-duration-cinematic-short` (1100ms) / `--yukti-ease-standard`.

### `linear-count`
Numeric counter, 45 steps, 24ms/step (`--yukti-duration-count`), no easing, IO @ 0.5, once.

### `path-draw`
SVG line/path reveal via `stroke-dasharray`/`stroke-dashoffset → 0`. `--yukti-duration-cinematic` (1600ms) / `--yukti-ease-standard`. Must fire one frame after DOM insertion (path-length measurement dependency).

### `panel-takeover`
Full panel/modal slide + fade. `translateY(-102%)→0`, `opacity 0→1`. `--yukti-duration-deliberate` / `--yukti-ease-emphasis`. Body scroll-lock, focus trap, `Escape`-to-close, backdrop-click-to-close. **Reserved for one component per surface.**

### `scroll-scrub-track`
Sticky-height, non-pinning horizontal scroll. `translate3d(-p*dist,0,0)` computed via rAF-throttled scroll handler; recalculated on resize/load/`fonts.ready`. Disabled below 760px viewport width.

### `cursor-tilt`
Cursor-parallax card tilt. `rotateX/Y` capped at `--yukti-tilt-max` (6deg), inner-layer parallax offset scaled larger than outer. Disabled under reduced motion; disabled by default in workspace surfaces (3.2).

### `split-flap-cell`
Mechanical character-reveal for live/ticking data. `rotateX(86deg)→0`, `opacity 0.3→1`, per updated cell.

### `viewport-gated-canvas`
Universal wrapper: any `requestAnimationFrame` visualization loop is started/stopped by an `IntersectionObserver` (threshold tunable 0.05–0.3). No canvas runs unconditionally except the one-time entry sequence (8.1).

---

## SECTION 10 — Interaction Grammar (the rules)

These are enforced, not aspirational. A code review that ships a violation of any of these is a motion-system bug, not a style nitpick.

1. **No bounce, no elastic, no overshoot easing, anywhere, ever.** Every curve in Section 2.2 is monotonic. This is the single most important rule in the system — it is the difference between "confident tool" and "playful app."
2. **`--yukti-ease-emphasis` is reserved for exactly one component per surface** — the highest-weight takeover (report viewer, primary nav panel). If two components on the same screen use it, downgrade one to `--yukti-ease-standard`.
3. **Every visualization loop must self-pause off-screen.** `viewport-gated-canvas` (Section 9) is mandatory for every `requestAnimationFrame`-driven component, with the sole exception of the one-time entry sequence.
4. **Reveal triggers fire once and never re-trigger on scroll-up.** `unobserve` immediately after the first intersection. Motion in YUKTI marks *that you have seen this*, and does not replay it decoratively.
5. **Never scroll-jack with a fixed-position pin.** Scroll-linked sections use the sticky-height + rAF-transform technique (`scroll-scrub-track`) specifically because it degrades gracefully on fast scroll-up and never desyncs. If a library's built-in pinning is used elsewhere in the codebase, it must not be used for anything a user might scroll past quickly.
6. **Generative visualizations must never overlap text.** Any clustering/particle system computes an explicit exclusion rectangle around headlines and controls it shares a canvas with, recalculated on resize.
7. **One calculation per animation frame, never per raw event.** Every scroll/mousemove/resize handler is throttled with a `requestAnimationFrame` guard — direct per-event heavy computation is disallowed.
8. **`prefers-reduced-motion` disables structurally, not just shortens.** Reveal transforms, cursor-tilt, and idle drift are fully removed under the media query — not sped up, removed. An institutional tool has a stronger obligation here than a marketing site does.
9. **Every facet/filter control is single-select.** No multi-select filtering exists anywhere in the system — one active classification lens at a time, so "what am I looking at" is always answerable at a glance.
10. **Data-driven visuals regenerate on resize rather than transform-scaling in place.** Correctness over animation continuity whenever the underlying data grid's shape changes.
11. **Typography motion never goes below the word level.** No character-split or line-cascade animation anywhere, on any surface, ever — this is a permanent constraint, not a current limitation.
12. **Micro-interactions respond to intent, never to scroll position.** Hover tilt, facet clicks, word rotators, and modal open/close are user- or timer-driven. Scroll is reserved for reveal and for the one explicit scrub component (4.3) — it never drives incidental micro-detail.
13. **The 400–500ms duration gap is never used.** Round to `--yukti-duration-standard` (300ms) or `--yukti-duration-deliberate` (600ms) — there is no in-between register.
14. **Cursor-parallax tilt is disabled by default in the Investigation Workspace surface (3.2).** It is a landing/dashboard-appropriate flourish; a working analyst does not need cards tilting under their cursor.

---

## SECTION 11 — Technical Implementation Standard

**Default posture: native browser APIs first.** `IntersectionObserver` for all reveal/visibility gating, `requestAnimationFrame` for all continuous/physics-driven motion, plain CSS `transition`/`@keyframes` referencing the token set in Section 2 for everything else. No animation library is a dependency by default.

**When a heavier library is justified:** only when a specific effect genuinely requires timeline sequencing that native APIs make awkward (e.g., a multi-step choreographed sequence with precise inter-element offsets). If introduced, it must be scoped to the surface that needs it — never loaded globally "just in case," and never used to implement `scroll-scrub-track` (Rule 5 exists specifically because a hand-rolled sticky-height technique is more robust than most libraries' built-in scroll-pin for this exact pattern).

**No smooth-scroll library, no SPA page-transition router, no carousel dependency** are approved defaults — native scroll and native navigation are the baseline; deviations require an explicit justification logged against this document.

**Canvas rendering:** 2D canvas context for all particle/cluster visualizations; `devicePixelRatio` capped at 2. 3D/WebGL is not the default toolset — perspective effects (if needed) are achieved via simple projection math on a 2D canvas, keeping the dependency surface minimal.

**Charts:** native SVG, constructed imperatively (`createElementNS`) or via a minimal charting utility — not a heavyweight charting framework, given the system's charts are simple, bespoke, and token-driven rather than generic.

---

## SECTION 12 — Performance Standard

- **GPU-safe properties only** for anything animated at `--yukti-duration-quick` or faster: `transform` and `opacity`, never `top`/`left`/`padding`/`width` in a hot path. (Exception: `confidence-fill`'s `width` transition — approved because it fires once, on view, never repeatedly, and represents literal data rather than UI chrome.)
- **`translate3d`/`will-change: transform` hints** on any guaranteed-active transform target during its interaction window (scroll-scrub track, panel takeover) — removed once the interaction window closes, to avoid leaving unnecessary compositor layers alive.
- **Canvas particle counts scale adaptively** by viewport size and device pixel ratio — not fixed regardless of device class. Halve default counts on narrow/low-DPR devices.
- **No `backdrop-filter: blur()` on large or frequently-repainted surfaces** — permitted only on small, fixed, infrequent elements (a consent panel, a single tooltip), never on a canvas overlay or a large panel background.
- **`document.fonts.ready` gating is mandatory** for any layout measurement feeding a scroll-scrub or chart-width calculation — skipping this reintroduces a font-swap desync bug class.
- **Reduced-motion is a first-class performance path, not just an accessibility path** — disabling tilt/drift/reveal under the media query also removes real CPU/GPU load, so it should be checked before any expensive visualization initializes, not just before its animation runs.
- **Target: sustained 60fps** on the Verification Pipeline scrubber and all Evidence Dashboard canvases on mid-tier hardware; the one-time entry sequence (8.1) is the single highest-risk moment (unconditional, ungated by visibility) and should be profiled explicitly on low-end/mobile devices before every release.

---

## SECTION 13 — Governance & Versioning

**This document is versioned independently of the product.** Current: **v1.0**.

**To propose a new token, component, or rule:**
1. State which existing token/primitive/rule it's meant to replace or extend — new additions must not duplicate an existing entry under a different name.
2. State which of the 14 interaction-grammar rules (Section 10) it might interact with or need an exception to, and justify the exception explicitly.
3. Land the change as a diff to this document alongside the code — the spec and the implementation update together, never one ahead of the other.

**Deprecation:** a token or primitive is deprecated (not deleted) by marking it `⚠️ deprecated as of vX.X — superseded by <name>` and left in the document for one full version cycle before removal, so existing implementations have a documented migration path.

**Naming convention:** all tokens use the `--yukti-<category>-<name>` pattern (Section 2). All primitives use `kebab-case` names matching their Section 9 heading. Component states use `lowercase` single words (`resting`, `scrolled`, `open`, `closed`, `clustered[facet]`) — never verb phrases, so state names read consistently as nouns across the whole system.

**Conformance:** any PR introducing new motion should be checkable against this document by name — "uses `reveal-on-scroll`," "uses `--yukti-duration-deliberate`" — rather than by re-describing the animation from scratch. If a reviewer cannot map a new animation to an entry in Sections 2, 4, or 9, it is not yet part of the system and should not ship without either conforming to an existing primitive or going through the extension process above.

---

## SECTION 15 — Addendum v1.1 (Website Layout & Motion Pass)

Ratified alongside `YUKTI Website v2 — Layout & Motion Pass` brief. No new duration/easing/distance tokens were required — every primitive below composes existing Section 2 tokens. This addendum documents new **primitives** (new applications of existing tokens) and one **rule amendment**.

### 15.1 Rule Amendment — Navigation Hover Grammar (supersedes part of §7)

§7 originally specified: *"Menu links use a padding-left nudge + color change (not underline-draw)."* The v1.1 brief explicitly requests underline-based hover motion sitewide ("subtle underline movement," "underline grows," "line extends"). This is a deliberate, direct art-direction change, not drift — logged here per Section 13's extension process rather than silently overwritten.

**New rule:** primary nav links, `QuietLink`, and `DomainStatement` hovers all use the `precision-underline` primitive (15.2). The padding-nudge grammar is deprecated for nav specifically; `--yukti-ease-micro` continues to distinguish these from the reserved `--yukti-ease-emphasis` panel-takeover motion — the *curve* discipline is unchanged, only the *transform* changed from a positional nudge to an underline reveal.

### 15.2 New Primitives

**`precision-underline`** — a border or pseudo-element scaled via `transform: scaleX(0 → 1)`, `transform-origin: left`, never via `width` (keeps it GPU-safe/compositor-only, per §12). `--yukti-duration-quick` / `--yukti-ease-micro`. This is the system's default hover grammar wherever "the cursor is inspecting something" needs signaling — nav links, quiet links, sequence items.

**`border-appear`** — an existing hairline border's `opacity` transitions `--yukti-opacity-hidden → --yukti-opacity-full` on hover/focus. `--yukti-duration-instant` or `--yukti-duration-quick`. Used where a full underline would be visually heavier than needed (e.g., domain-sequence side rules).

**`tracking-shift`** — `letter-spacing` nudges up slightly on hover (e.g., `+0.01em`) for label-register text. `--yukti-duration-quick`. Documented exception to the general GPU-safe-properties-only rule (§12): letter-spacing is not compositor-only, but the affected text is always short (labels, not paragraphs), so reflow cost is negligible. Do not apply to body copy.

**`stagger-reveal` (typography)** — clarifies, does not replace, `reveal-on-scroll` (§4.9): when a heading or list has multiple lines/items, each child gets its own `reveal-on-scroll` instance at the existing 4-slot stagger cadence. This is still block/line-level staggering — Rule 11 (never below the word level) is unchanged; nothing here splits a line into words or characters.

**`scroll-parallax` (blueprint layer only)** — the page-level `BlueprintBackground` layer shifts at a fraction of scroll speed (`translateY(scrollY * k)`, `k ≈ 0.04`, rAF-throttled per Rule 7) to read as a "drafting sheet" set slightly back in depth. Reduced-motion disables this listener entirely (not just the transition) — this is JS/rAF-driven, not CSS-transition-driven, so it requires an explicit `prefersReducedMotion()` check rather than relying on token zeroing.

**`reasoning-canvas-idle`** — a second, narrowly-scoped exception to the "no unprompted ambient motion" rule (§1.3), alongside the existing confidence-visualization idle-drift. The empty `ReasoningCanvas` container's corner registration marks breathe opacity very slightly (`--yukti-opacity-muted ↔ --yukti-opacity-full`-adjacent range, long cycle ~3.5–4s, `--yukti-ease-standard`) to signal "this is a live, waiting instrument," not a static placeholder graphic. Disabled under reduced motion. This must remain the *only* motion inside an empty `ReasoningCanvas` — no invented nodes, edges, or graph content (see architecture addendum, Section 15).

### 15.3 Explicit Non-Additions

No bounce/elastic/scale/rotate/glow was added anywhere — the brief's own "avoid: scaling, bouncing, glowing, rotating" instruction restates Rule 1 verbatim; it required no new rule, only reaffirms the existing one.

---

## SECTION 16 — Addendum v1.2 ("Architectural Editorial" pass)

**`scroll-snap-statement`** — new primitive for the Philosophy scene: each commitment becomes a `min-height:100vh` block with native `scroll-snap-align:start` inside a `scroll-snap-type:y mandatory` container. This is explicitly **not** a JS scroll-jack/pin — Rule 5 ("never scroll-jack with a fixed-position pin") is satisfied by using the browser's native snap mechanism instead of a hand-rolled or library pin. No new duration/easing tokens required; the "pause" is the snap itself, not an animated transition.

No other new primitives were required for this pass — the mega-typography, drafting-tick, and materials-grain additions are all static/CSS-only (no motion), and the pull-quote/margin-note/footer scenes reuse `reveal-on-scroll` (§4.9) exactly as-is.

---

## SECTION 17 — Addendum v1.3 (Entry Sequence)

**Supersedes §8.1's original description.** §8.1 described a particle-globe-coalesces entry sequence, inherited conceptually from early reference analysis. It was never built — `ReasoningCanvas` must stay empty by contract (no invented graph). This addendum's cover-page/door-split sequence is the first real entry-sequence implementation and replaces that description outright, not a variant of it.

- **`--yukti-ease-emphasis` reused for a second surface.** Rule 2 reserves this curve to one component per surface. The Entry Sequence is treated as its own surface (a pre-homepage cover, distinct from Surface 3.1 Landing) — so the door-panels using this curve doesn't dilute the homepage's own reserved use (the primary nav panel takeover). Logo movement uses `--yukti-ease-standard` instead (a settling/receding read, not a mechanical slam).
- **New timing tokens** (`tokens.motion.css`): `--yukti-entry-ack-duration` (150ms), `--yukti-entry-split-delay`/`-duration` (400ms/1200ms), `--yukti-entry-logo-delay`/`-duration` (1200ms/700ms), `--yukti-entry-reveal-duration` (600ms). Chosen so the brief's absolute checkpoints (0.2/0.4/1.0/1.2/1.8/2.4s) fall out of the transition math directly rather than being hand-simulated in JS.
- **Deliberate exception to the reduced-motion zero-out rule**: `--yukti-entry-reveal-duration` is intentionally **not** added to tokens.motion.css's `prefers-reduced-motion` zero-out block. The brief explicitly requires reduced-motion users get "a simple fade transition," not an instant cut — zeroing this one token would produce a harsh jump-cut, the opposite of the accessibility intent here. This is a narrow, documented exception (same spirit as the two existing idle-drift exceptions in §1.3/§4.5), not a loophole — the door-split and logo-advance choreography is still fully skipped for reduced motion (a different code path entirely, `runReducedFade()` vs `runFullSequence()`), only the one shared "homepage becomes visible" fade duration survives.
- **`entry-cover-reveal`** (new primitive) — the mechanism suppressing the homepage's own chrome (nav/blueprint/registration/ruler/main/footer, all `opacity:0; pointer-events:none`) while the cover is active, then fading the whole assembly in as one unit via a single class removal. This directly reuses the exact pattern originally sketched in §8.1 (`body.intro-active` hiding nav/hero) — the mechanism survives the visual redesign even though the visual itself was replaced.
- **No ambient-motion exception needed beyond the existing two** — the cover's idle grain-drift/lighting-drift is disabled outright (not narrowed) under reduced motion, since it's decorative, not a "this system is alive" signal like the ReasoningCanvas idle-drift.

---

*End of specification — YUKTI Motion System v1.0, Addendum v1.1, v1.2, v1.3.*
