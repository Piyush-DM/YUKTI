# YUKTI Website v1.0 — Build Architecture
### Frozen Blueprint, Prior to Implementation

**Status:** 🟢 **FROZEN — approved via `YUKTI_Website_v1_Final_Governance_Decisions.docx`.** Section 0 below reflects final, binding decisions. Implementation may proceed per the Build Order (Section 6).
**Governs:** the public YUKTI website only. Does not touch `choir/`, `daale/`, `applications/` (reaffirmed as D5, below).
**Depends on:** [`yukti-motion-system-v1.md`](yukti-motion-system-v1.md) (motion tokens/primitives, referenced not restated) and the Canonical Build Constitution supplied in this session (visual identity, homepage philosophy, engineering philosophy).
**Purpose of this document:** satisfy the Constitution's requirement to produce Information Architecture, Component Tree, Design System Mapping, Motion Mapping, Responsive Strategy, and Build Order — and to freeze them, per the OttoLabs Lesson, before a single component is written.

---

## 0. Governance Decisions (FINAL — ratified, not open)

### 0.1 Core Decisions (D1–D4)

| Decision | Final Decision | Rationale |
|---|---|---|
| **D1 — Build Tooling** | Static HTML, CSS, and vanilla JavaScript. Vite used **only** as a dev-server/bundler — no framework runtime ships to production. | The public website is a business card, not the application. Zero framework runtime keeps the site lightweight, deterministic, and easier to animate against the Motion System's native-API mandate. |
| **D2 — Typography** | Display: **Söhne**. Body/UI: **Inter**. Data/provenance: **IBM Plex Mono**. | Creates an engineered-editorial aesthetic while keeping evidence and provenance visually distinct from narrative copy — the monospace register is reserved for literal data, never decoration (Section 2.2). |
| **D3 — Content Source** | Purpose-written copy authored during implementation. No lorem ipsum, no marketing-placeholder filler. | Every sentence must support the information architecture rather than exist to fill space — copy is written to the scene's *job* (Section 1), not fitted around a template. |
| **D4 — Evidence Visualization** | A static, deterministic reasoning graph built from representative data drawn from the actual YUKTI prototype (not invented, not live-API-driven at v1.0). | Demonstrates the real methodology rather than pretending to be a live product — satisfies the Constitution's explicit ban on fake dashboards without requiring a backend integration workstream. |

**Licensing note (D2 follow-up, not yet decided — flagging so it isn't silently dropped):** Söhne (Klim Type Foundry) is a commercial license; Inter and IBM Plex Mono are open-licensed (SIL OFL) and can be self-hosted immediately. Söhne requires a procured license + font files before it can ship — until then, the type system implements with a documented fallback stack (`"Söhne", "Neue Haas Grotesk Display", ui-sans-serif, sans-serif`) so the token layer is correct today and silently upgrades the moment licensed files land. This is a procurement dependency, not an architecture question — do not let it block Build Order Step 1.

### 0.2 Additional Frozen Decisions (D5–D14)

| Decision | Final Decision |
|---|---|
| **D5 — Repository Structure** | Website remains isolated from `choir/`, `daale/`, and `applications/` — lives in its own top-level directory (`website/`, per Section 6's scaffold). |
| **D6 — Hosting** | Static deployment via Cloudflare Pages or Vercel Static. No server runtime. |
| **D7 — Performance Budget** | LCP under 1.8s. JavaScript under 180KB (total, shipped). Images as SVG/WebP only. |
| **D8 — Accessibility** | WCAG AA conformance. Full keyboard navigation. `prefers-reduced-motion` support (already required by the Motion System, now also a governance-level requirement). ARIA labels on all interactive/data-bearing elements. **Yellow focus states** — `--yukti-color-yellow-500` is the system's focus-ring color, in addition to its hover/active/data-state roles (Section 2.1 updated accordingly). |
| **D9 — Browser Support** | Latest two versions of Chrome, Edge, Firefox, and Safari. No legacy-browser fallback path. |
| **D10 — Animation Philosophy** | Every animation must answer one of three questions: **What entered? What changed? What became connected?** An animation that answers none of these is a defect, not a flourish — this is now the literal acceptance test applied to every Motion System citation in Section 4. |
| **D11 — Scroll Philosophy** | The homepage is a **continuous document, not stacked pages.** This ratifies Section 1's "scene exit conditions" requirement as a hard governance rule, not a stylistic preference. |
| **D12 — Graph Philosophy** | The homepage evidence graph is a **living illustration, not a product demo.** It must read as authentic methodology, but it is explicitly not a claim that this *is* the product UI — Section 3/4's `EvidenceGraphCanvas` and `EvidenceTraceVisualization` descriptions are read in this light. |
| **D13 — Homepage Success Criterion** | A visitor should leave understanding: (1) what YUKTI is, (2) why reasoning differs from AI-generated answers, (3) why provenance matters. Every scene in Section 1 is now checked against which of these three it serves — a scene serving none of them is out of scope for v1.0. |
| **D14 — Governing Principle** | The website is not designed to impress. It is designed to establish confidence. Every element should make YUKTI appear more rigorous, deliberate, and trustworthy. **If an element exists only because it is visually impressive, it should be removed.** This is the standing test for every future addition to this document. |

All decisions in this section are now binding. Section 6 (Build Order) may proceed.

---

## 1. Homepage Information Architecture

The Constitution's structure (Hero → Why Reasoning Matters → Approach → Evidence → Applications → Philosophy → Contact) is treated as fixed content order. This section defines, per scene: **its one job**, **what proves that job**, **what must never appear**, and **the exit condition into the next scene** — because the Constitution requires scenes to flow continuously rather than read as stacked sections, so each scene's ending must be designed as the next scene's beginning.

### Scene 1 — Hero
- **Job:** state what YUKTI is, in a register that reads as engineered rather than pitched.
- **Content:** one declarative statement of identity (not a slogan), one supporting line, one living evidence-graph visualization (real structure, not decoration — see D4).
- **Proof:** the visualization itself is the proof — it must be inspectable (hoverable nodes with real labels), not ambient.
- **Never:** a CTA button styled as urgency ("Get Started," countdown, gradient glow). A single quiet link forward is acceptable; nothing performing eagerness.
- **Exit condition:** as the visualization settles, the page's next scene's opening statement should already be partially visible/anchored below the fold — no hard section boundary, no full-viewport-snap.

### Scene 2 — Why Reasoning Matters
- **Job:** name the problem class (systems that produce answers vs. institutions that require reasoning) without naming YUKTI yet.
- **Content:** short paragraph-form argument, not bullet points — this scene is meant to read like the opening of a technical memo.
- **Proof:** none needed — this is a framing scene, not an evidence scene. Resist the urge to add a stat here; stats belong to Scene 4.
- **Never:** comparison logos, "vs. the competition" framing, fear-based language.
- **Exit condition:** the argument's final sentence should pose the question Scene 3 answers, so the transition is logical, not spatial.

### Scene 3 — How YUKTI Approaches Problems
- **Job:** communicate philosophy, explicitly without architecture diagrams or jargon (per Constitution).
- **Content:** a small number (3–4) of short, plainly-stated method principles — closer to axioms than feature bullets.
- **Proof:** none — this is conceptual, per the Constitution's own instruction.
- **Never:** pipeline diagrams, technology names, "how it works" flowcharts.
- **Exit condition:** the last principle should be the one Scene 4 demonstrates concretely ("conclusions stay connected to evidence") — direct semantic handoff.

### Scene 4 — Evidence
- **Job:** demonstrate, not claim, that conclusions remain traceable to evidence.
- **Content:** one restrained interactive visualization showing a real claim → evidence → confidence chain (see D4). Not a dashboard grid, not multiple charts competing for attention — **one** demonstration, done credibly.
- **Proof:** the interaction itself (a visitor can trace a conclusion back to its sources by hovering/clicking) is the proof.
- **Never:** invented statistics, animated counters implying scale that hasn't been earned yet, more than one visualization competing for attention.
- **Exit condition:** the traced evidence naturally terminates at a labeled domain (e.g., "applied in compliance review") that becomes Scene 5's opening example.

### Scene 5 — Institutional Applications
- **Job:** show domains (Investment, Insurance, Compliance, Procurement, Research) without becoming a feature grid.
- **Content:** a restrained list/sequence — each domain gets a short, specific sentence about what reasoning failure looks like there, not a marketing card with an icon.
- **Proof:** specificity of language substitutes for a case-study logo wall the site doesn't have yet.
- **Never:** icon grids, "solutions for X" card layouts, generic industry stock imagery.
- **Exit condition:** domains converge back to one sentence ("in every one of these, the reasoning must survive scrutiny") that becomes Scene 6's first line.

### Scene 6 — Philosophy
- **Job:** state the four commitments plainly: evidence over confidence, transparency over opacity, reasoning over prediction, trust over persuasion.
- **Content:** exactly these four statements, typographically prominent, minimal surrounding copy.
- **Proof:** none needed — this is a declaration, and over-supporting it with evidence here would undercut its role as the section that states values rather than proves them (Scene 4 already did the proving).
- **Never:** restating Scene 4's evidence, adding a fifth "innovation" value that dilutes the four.
- **Exit condition:** the fourth statement ("trust over persuasion") reads directly into Contact's tone — quiet, not persuasive.

### Scene 7 — Contact
- **Job:** simple, professional, quiet conversion point.
- **Content:** a direct contact path (email or short form) and, if applicable, office/location information — no chat widget, no "book a demo" scheduling embed unless already an approved product motion.
- **Proof:** none — this is administrative, not persuasive.
- **Never:** urgency copy, multiple competing CTAs, a large decorative closing illustration.
- **Exit condition:** footer (legal, secondary links) — the one place a hard boundary is acceptable, since it's explicitly a different register (administrative, not narrative).

---

## 2. Design System Mapping

### 2.1 Color Tokens

| Token | Role | Value guidance | Notes |
|---|---|---|---|
| `--yukti-color-graphite-900` | Primary background (deep graphite/off-black) | near-black, warm-neutral undertone (avoid pure `#000`, which reads as "app," not "material") | Foundation surface for the whole site |
| `--yukti-color-graphite-700` | Secondary/raised background (panels, alternating bands) | one to two steps lighter than 900 | Used to create depth without introducing a second hue |
| `--yukti-color-bone-100` | Card surface (resting state) | warm off-white, "editorial paper," not clinical `#fff` | Cards, panels, contrast blocks |
| `--yukti-color-bone-300` | Body text on dark backgrounds | slightly dimmed bone, not pure white | Primary reading color on graphite |
| `--yukti-color-ink-900` | Body text on bone/light surfaces | near-black, matches graphite-900 hue family | Ensures light-surface text isn't a different color language than the dark-surface foundation |
| `--yukti-color-yellow-500` | **Primary accent — construction yellow** | saturated, industrial-machinery yellow (JCB/Caterpillar register) — must be validated against pastel/gold/orange failure modes explicitly named in the Constitution | The system's *only* accent hue. No secondary accent color exists in v1.0. |
| `--yukti-color-yellow-600` | Yellow, pressed/active state | slightly darker/more saturated than 500 | Used for `:active`, not `:hover` — hover uses 500 |
| `--yukti-color-yellow-focus` | **Focus ring (D8)** | `--yukti-color-yellow-500`, 2px solid ring, 2px offset | Every interactive element's `:focus-visible` state — non-negotiable per D8 (WCAG AA). This is a fourth approved use of yellow, added to the Color Rule below. |
| `--yukti-color-line-blueprint` | Background linework | graphite-900 + ~4–8% bone opacity, hairline weight | Never exceeds "barely perceptible" — see Rule below |
| `--yukti-color-border-hairline` | Card/panel borders | low-contrast graphite-on-graphite or bone-on-bone hairline | Enterprise Neo-Brutalism reads through precise hairlines, not shadows |

**Color rule (hard constraint):** yellow is a **state signal**, never a decorative fill. It appears only on: (a) hover/active/focus states — including the mandatory `:focus-visible` ring (D8), (b) elements actively carrying data/evidence-flow meaning (an active node, an in-progress verification step, the scroll-scrub progress fill), and (c) a strictly limited set of primary actions (one link per scene, never a button field). If a design calls for yellow "because it looks good there," that is a violation, not a judgment call — flag it and route to the extension process instead of applying it. Motion System §2.2's `--yukti-ease-emphasis` reservation rule is the direct analogue here: a color used everywhere loses its signaling value.

**Blueprint linework rule:** the background linework is architectural-drafting-grade, not a texture. It must remain legible as "the surface has structure" and must never compete with foreground content for attention at a normal viewing distance — if a user notices the linework before the content, the opacity is too high.

### 2.2 Typography Scale

**Families (D2, final):**
- `--yukti-font-display: "Söhne", "Neue Haas Grotesk Display", ui-sans-serif, sans-serif` — headlines only. Fallback stack active until Söhne license/files are procured (see D2 licensing note in Section 0.1).
- `--yukti-font-body: "Inter", ui-sans-serif, system-ui, sans-serif` — all narrative/UI copy. Self-hostable now (SIL OFL).
- `--yukti-font-data: "IBM Plex Mono", ui-monospace, monospace` — data/provenance only (Section 2.2's data-register rule, unchanged). Self-hostable now (SIL OFL).

| Token | Role | Family | Size (fluid, `clamp()`-based) | Weight | Tracking |
|---|---|---|---|---|---|
| `--yukti-type-display` | Hero/scene headline | `--yukti-font-display` | large, fluid 44–96px | 700–800 (Söhne Kräftig/Halbfett or fallback-equivalent) | tight/negative tracking, per Constitution's "powerful typography" |
| `--yukti-type-heading` | Section/scene subheads | `--yukti-font-display` | 28–44px | 500–700 | tight |
| `--yukti-type-body` | Paragraph copy | `--yukti-font-body` | 16–18px | 400 (Inter Regular) | normal |
| `--yukti-type-label` | UI labels, facet controls, captions | `--yukti-font-body` | 11–13px | 500 (Inter Medium) | wide/uppercase tracking |
| `--yukti-type-data` | Coordinates, figures, evidence citations, timestamps | `--yukti-font-data` | 12–14px | 400 (IBM Plex Mono Regular) | normal, tabular numerals (`font-variant-numeric: tabular-nums`) mandatory |

**Rule:** `--yukti-type-data` is reserved for content that is *literally data* (a citation, a confidence figure, a timestamp) — never used decoratively to "look technical." This mirrors Motion System Rule 11 (typography motion never goes below the word) — here, the analogous rule is that the monospace register never goes below actual data.

### 2.3 Spacing & Grid System

| Token | Value | Use |
|---|---|---|
| `--yukti-space-1` | 4px | Micro-gaps (icon-to-label) |
| `--yukti-space-2` | 8px | Tight internal padding |
| `--yukti-space-3` | 16px | Standard internal padding |
| `--yukti-space-4` | 24px | Component-to-component gaps |
| `--yukti-space-5` | 40px | Sub-scene gaps |
| `--yukti-space-6` | 64px | Scene-to-scene rhythm unit |
| `--yukti-space-7` | 96–128px (fluid) | Major scene padding, top/bottom |

**Grid:** a 12-column layout grid with a fixed outer margin (fluid, `clamp()`-based, matching the blueprint-drafting reference — think a drawing sheet's margin, not a arbitrary container width). All component widths snap to column boundaries; no arbitrary pixel widths (per Constitution's "no arbitrary values, no magic numbers").

**Rule:** every spacing decision in every component must reference one of these seven tokens. A value like `18px` or `50px` appearing anywhere in the codebase is, by definition, a bug against this system.

### 2.4 Surface & Elevation Language

Enterprise Neo-Brutalism reads through **hairline precision and flat state-change**, not soft shadow elevation. Concretely:

- **Cards (bone-white, resting):** flat bone-100 fill, `--yukti-color-border-hairline` 1px border, no drop shadow, sharp or minimally-radiused corners (radius token: `--yukti-radius-sm` ≈ 2–4px — never a soft/pill radius, which reads as consumer-app, not instrument).
- **Cards (activated/hovered):** transition fill toward `--yukti-color-yellow-500` (or a yellow-tinted surface state, not a full opaque fill if legibility of internal content requires restraint), per Motion System `--yukti-duration-quick`/`--yukti-ease-micro`. This is the system's primary "interactive = yellow" signal.
- **No glassmorphism, no blur, no gradient fills** — explicitly banned by the Constitution. Any `backdrop-filter` usage must clear the same bar Motion System §12 sets (small, fixed, infrequent elements only — e.g., a tooltip), never a card or panel surface.
- **Depth is communicated by z-layer and hairline separation**, not shadow softness — reuses Motion System §2.6's z-layer scale directly (canvas/veil/content/nav/panel/modal/toast/consent) without modification.

### 2.5 Iconography & Ornament

- No decorative icon sets, no illustration style. Where a mark is needed (e.g., a facet-control glyph), it should read as **drafting notation** — a small geometric mark (a plus, a bracket, a coordinate crosshair) consistent with technical-publication conventions, not a rounded consumer icon.
- No photography, no stock imagery, no illustrated characters — consistent with Motion System §6's "the data is the visual" principle, now extended to the whole visual system, not just canvases.

---

## 3. Component Tree

Framework-agnostic; reads as a composition tree regardless of D1's outcome.

```
YUKTI Website
├── App Shell
│   ├── PrimaryNav                          [persistent, Motion §4.1]
│   │   ├── Wordmark
│   │   ├── NavLinkGroup
│   │   └── MenuTrigger → PanelTakeover       [Motion §4.2 — reserved emphasis-curve component]
│   ├── PageRegion (Homepage)
│   │   ├── Scene: Hero
│   │   │   ├── EntrySequence                [Motion §8.1 — one-time, unconditional]
│   │   │   ├── HeadlineBlock (display type)
│   │   │   ├── SupportingLine
│   │   │   ├── EvidenceGraphCanvas          [Motion §4.5, viewport-gated after entry]
│   │   │   └── QuietForwardLink
│   │   ├── Scene: WhyReasoningMatters
│   │   │   ├── ArgumentBlock (reveal-on-scroll)
│   │   │   └── TransitionAnchor              [semantic handoff element, no visual chrome]
│   │   ├── Scene: HowYuktiApproaches
│   │   │   ├── PrincipleList (3–4 items, reveal-on-scroll, 4-slot stagger)
│   │   │   └── TransitionAnchor
│   │   ├── Scene: Evidence
│   │   │   ├── EvidenceTraceVisualization    [single instance, Motion §4.5/4.8 hybrid — see 4. Motion Mapping]
│   │   │   ├── TraceDetailPanel (appears on node selection)
│   │   │   └── TransitionAnchor
│   │   ├── Scene: InstitutionalApplications
│   │   │   ├── DomainSequence (5 items: Investment/Insurance/Compliance/Procurement/Research)
│   │   │   │   └── DomainStatement (reveal-on-scroll, not a card component — explicitly not `DomainCard`)
│   │   │   └── TransitionAnchor
│   │   ├── Scene: Philosophy
│   │   │   ├── CommitmentStatement × 4 (fixed order, reveal-on-scroll)
│   │   │   └── TransitionAnchor
│   │   └── Scene: Contact
│   │       ├── ContactStatement
│   │       ├── ContactChannel (mailto or minimal form — per D3/content decisions)
│   │       └── Footer
│   │           ├── LegalLinkGroup
│   │           └── SecondaryLinkGroup
│   └── GlobalOverlays
│       ├── ConsentNotice                     [Motion §2.6 consent layer]
│       └── ReducedMotionRuntimeFlag          [not visual — a runtime check gating all of the above]
│
├── Shared/Design-System Components (reused across scenes)
│   ├── RevealOnScroll (wrapper/primitive, Motion primitive 1:1)
│   ├── FacetControl (single-select, Motion §4.11)
│   ├── DataLabel (typography role `--yukti-type-data`)
│   ├── HairlineCard (bone surface, yellow-activation states)
│   ├── QuietLink (the system's only "action" style — no button-as-CTA component exists in v1.0)
│   └── BlueprintBackground (the architectural linework layer, applied at App Shell level, not per-scene)
```

**Explicit non-components (named so they are never accidentally introduced):**
- No `FeatureCard` / `FeatureGrid` — banned by the Constitution's "avoid feature grids" instruction (Scene 5 uses `DomainStatement`, not a card).
- No `StatCounter` on the homepage v1.0 — the Constitution's evidence scene demonstrates via trace, not via animated numbers (the Motion System's `linear-count` primitive remains valid for a future dashboard/product surface, just not this homepage).
- No `PrimaryButton` — only `QuietLink`. If a future requirement genuinely needs a button, that is a Section-13-style extension request against both this document and the Motion System, not a default component.

---

## 4. Motion Mapping

Per the Constitution ("follow the canonical Motion System, do not invent additional animation languages"), every animated element on the site must cite an existing Motion System §2/§4/§9 entry. No new primitive is introduced in this document.

| Website Element | Motion System Reference | Notes |
|---|---|---|
| `EntrySequence` (hero) | §8.1 Entry Sequence + `spring-cluster` primitive | Evidence-graph nodes coalesce once, unconditionally, before scroll is possible — exact reuse, domain relabeled to "evidence nodes" per prior mapping work |
| `PrimaryNav` scroll state | §4.1 | Binary 40px threshold, background/padding only |
| `MenuTrigger` → panel | §4.2 `panel-takeover` | The **one** component permitted `--yukti-ease-emphasis` on this site |
| `RevealOnScroll` (all scene copy blocks) | §4.9 / `reveal-on-scroll` primitive | IO@0.12, once, 4-slot stagger, `--yukti-duration-reveal` |
| `EvidenceGraphCanvas` (Hero) | §4.5 `spring-cluster` + `viewport-gated-canvas` | Idle drift `k=0.04` once settled; must respect the exclusion-zone rule (Motion Rule 6) around the headline |
| `EvidenceTraceVisualization` (Scene 4) | §4.5 (node interaction/highlight) + §4.8 (`path-draw`, if the trace renders as a connected line/graph edge) | This is the one visualization on the homepage permitted deliberate-register motion beyond entrance — because it is the Constitution's single evidence demonstration, not decoration |
| `TraceDetailPanel` | §4.4 (instant content swap, responsive register) | Selecting a node swaps detail text instantly — no crossfade delay, mirroring the verification-stage-tab rule that direct user selection should not be artificially slowed |
| `DomainSequence` items | §4.9 `reveal-on-scroll` only | Explicitly **no** hover-tilt (§4.7/`cursor-tilt` is not applied here — Scene 5 is prose, not a dashboard stat card, and tilt is disabled by default outside dashboard/landing-hero contexts per Motion Rule 14's spirit) |
| `CommitmentStatement` × 4 | §4.9, plus optional §4.4-style progressive emphasis if the four statements reveal one-at-a-time rather than as a block | Recommend one-at-a-time reveal (each statement its own `reveal-on-scroll` instance) so the four commitments read as sequential weight, not a bullet dump |
| `FacetControl` (if Evidence scene exposes a "trace by: source / date / confidence" switch) | §4.11 | Strict single-select, instant active-state swap, re-clustering handled by the visualization's own `spring-cluster` |
| `ConsentNotice` | Motion System §2.6 `consent` z-layer; motion itself not fully specified in v1.0 of the Motion System — inherit `--yukti-duration-standard` fade-in as the default, pending an explicit Motion System addendum if a bespoke treatment is wanted |

**Hard constraint carried forward:** `prefers-reduced-motion` disables `EntrySequence`, `EvidenceGraphCanvas` drift, `EvidenceTraceVisualization` motion, and all `reveal-on-scroll` transforms **structurally** (Motion Rule 8) — the homepage must be fully legible and fully functional with every animation removed, not merely faster.

---

## 5. Responsive Strategy

| Breakpoint | Range | Behavior |
|---|---|---|
| `--yukti-bp-compact` | < 480px | Single-column flow throughout. `EvidenceGraphCanvas` renders at reduced particle/node density (device-adaptive, per Motion §12). `EntrySequence` still plays but is shortened proportionally — never skipped, since it's the one unconditional brand moment, but never allowed to block interaction past ~1.5s on this tier. |
| `--yukti-bp-narrow` | 480–760px | Single-column. Grid collapses from 12 to 4 columns. Nav collapses to `MenuTrigger` only (no inline link group). |
| `--yukti-bp-standard` | 760–1200px | Grid at 8 columns. Full inline nav returns. Any scroll-scrub-style component (not currently in the homepage per Section 1, but reserved for a future Verification Pipeline sub-page) is disabled below 760px per Motion §4.3's own rule, inherited verbatim. |
| `--yukti-bp-wide` | > 1200px | Full 12-column grid. Full typographic scale ceiling (`clamp()` upper bounds reached). |

**Cross-cutting responsive rules:**
- `EvidenceGraphCanvas` and `EvidenceTraceVisualization` must both define an explicit minimum-viable layout for `--yukti-bp-compact` (e.g., a simplified 2D arrangement rather than the full desktop composition) — never simply scaled-down desktop art, since illegible micro-labels would violate the "inspectable, not decorative" requirement for these two components specifically.
- Blueprint background linework density reduces at `--yukti-bp-compact` — small-viewport devices should show less linework, not the same density compressed, or it will read as visual noise rather than architectural depth.
- Touch devices: `EvidenceGraphCanvas`/`EvidenceTraceVisualization` hover-to-inspect interactions require a tap-to-inspect equivalent (persistent until tapped elsewhere), not a hover-only interaction with no touch fallback.

---

## 6. Build Order

Sequenced specifically to prevent the OttoLabs failure mode: **foundation before composition, and no component is touched twice without a documented reason.**

1. **Design tokens first, in isolation.** Implement Section 2's color/type/space/radius tokens as the literal CSS custom-property (or equivalent) layer. No component exists yet. This is reviewable and approvable on its own before anything renders.
2. **Layout shell.** `App Shell`, grid system, `BlueprintBackground`, `PrimaryNav` (static states only — no scroll behavior yet). Confirms the 12-column grid and spacing rhythm at all four breakpoints with placeholder content blocks only.
3. **Shared/design-system components**, built and reviewed independently of any scene: `RevealOnScroll`, `HairlineCard`, `QuietLink`, `DataLabel`, `FacetControl`. Each ships with its Motion System citation attached in code comments, per Motion §13's conformance rule.
4. **Scene 1 (Hero) — including `EntrySequence` and `EvidenceGraphCanvas`.** Built first among scenes because it's the highest-risk component (Motion §12 flags the entry sequence as the single highest performance-risk moment) and because getting the canvas exclusion-zone/legibility rules right here establishes the pattern Scene 4 reuses.
5. **Scenes 2, 3, 6, 7 (text-driven scenes: Why/Approach/Philosophy/Contact).** Built together since they share the same `reveal-on-scroll`-only motion profile and no bespoke visualization — lowest risk, fastest to freeze.
6. **Scene 4 (Evidence) — `EvidenceTraceVisualization`.** Built after Scene 1's canvas patterns are proven, since it reuses the same interaction/exclusion-zone conventions at higher content stakes (this is the Constitution's single most important credibility moment on the page).
7. **Scene 5 (Institutional Applications).** Built last among scenes deliberately — it is pure `DomainStatement` prose reveal, and building it last ensures it doesn't accidentally regress into a feature-grid pattern "borrowed" from an earlier, more visual scene.
8. **Full-page integration pass.** Verify scene-to-scene transition anchors (Section 1's "exit condition" requirement) read as continuous rather than stacked — this is a review pass, not a rebuild; any fix here should be a targeted refinement per the Constitution's modification rules (Section 7 below), not a redesign.
9. **Responsive pass across all four breakpoints**, in the order defined in Section 5 (compact → narrow → standard → wide), fixing forward only — a fix found at `compact` should never require touching `wide`'s already-approved layout.
10. **Reduced-motion and accessibility audit** (keyboard nav through `PanelTakeover`, `FacetControl`, and both visualizations; screen-reader labeling for `EvidenceGraphCanvas`/`EvidenceTraceVisualization` content, since both carry real information, not decoration).
11. **Performance pass** against Motion System §12's targets, specifically profiling `EntrySequence` and both evidence visualizations on low-end/mobile hardware.

**Explicit rule for this build order:** each numbered step is a checkpoint. A step is not reopened once approved unless a documented change request (Section 7, below) justifies it. If step 6 reveals a problem with a component from step 3, the fix is scoped to step 3's component and re-verified — it does not cascade into re-litigating steps 4–5 "while we're in there."

---

## 7. Change Control (inherited, restated for this document specifically)

This document, the Motion System, and the eventual codebase are three artifacts that must move together. Before any component is modified after its build-order step is marked complete:

1. State which requirement (Constitution, this document, or the Motion System) the current implementation fails to meet.
2. Confirm the proposed change doesn't violate a token, rule, or component boundary defined above — if it does, the *system* is amended first (as a reviewable diff to this document), and the component change follows from that amendment, never the other way around.
3. Prefer refinement (adjusting a token value, a threshold, a spacing step) over replacement (rewriting a component's structure) wherever the requirement can be satisfied that way.
4. Log the change and its justification — this document should always reflect the current, real state of the built system, not the original plan alone.

---

## SECTION 15 — Addendum v1.1 (Layout & Motion Pass, No Reasoning Graph)

Ratified per `YUKTI Website v2 — Layout & Motion Pass` brief. This is a refinement of the approved visual direction, not a redesign — per this document's own change-control rule (Section 7), each change below states why it's necessary and confirms it doesn't violate an existing token/rule.

### 15.1 New Component — `ReasoningCanvas`

**Why:** the hero's reserved right-half visualization area must not contain an invented graph — the real reasoning graph is proprietary and arrives later. `ReasoningCanvas` is architectural space designed to *receive* that component, not a stand-in for it.

**Contract:**
- Responsive, fixed aspect ratio (`aspect-ratio` CSS, not a hardcoded pixel box).
- Empty by default — no nodes, edges, or invented diagram content, ever, per the brief's explicit ban.
- Soft hairline border (`--yukti-color-border-hairline-dark`, `--yukti-radius-sm` — reuses existing tokens, no new ones).
- A denser, local blueprint treatment inside it (coordinate labels, registration crosses, measurement ticks) — distinct from but token-consistent with the page-level `BlueprintBackground`.
- One idle animation only: `reasoning-canvas-idle` (Motion Addendum §15.2) — corner-mark opacity breathing, nothing else.
- **Mount API:** exposes `mountSVG(el)` / `mountCanvas(el)` / `clear()` so the future proprietary graph integrates as a clean drop-in rather than requiring this container to be rewritten. This satisfies "accepts future SVG/canvas rendering" as an actual engineering contract, not just a visual affordance.

**Does not violate:** Section 2's "yellow is a state signal" rule (canvas uses graphite/bone/hairline only, no yellow, since it carries no active data yet); Section 2.5's no-decorative-imagery rule (the frame is drafting notation, not illustration).

### 15.2 Blueprint System Expansion

**Why:** the brief asks the blueprint language to "reward observation rather than demand attention" — CAD/architectural-drawing register, not decoration.

**Additions (all at `--yukti-color-line-blueprint`-equivalent low opacity):**
- Registration crosses at the four viewport corners (fixed, `aria-hidden`).
- Scene index numbers (`01 — Reasoning`, `02 — Approach`, …) function simultaneously as **section identifiers** and as the brief's requested sectional-numbering rhythm device. Numbering starts at the first post-hero scene (Hero remains unnumbered — it's the cold open, not part of the "document" the numbering is counting through).
- A left-edge measurement-tick ruler, wide-viewport only (matches the existing "reduced density on small viewports" responsive rule — it is removed, not shrunk, below `--yukti-bp-standard`).

**Does not violate:** Section 2.1's "never exceeds barely perceptible" rule — all additions ship at the same opacity ceiling as the existing linework.

### 15.3 Scene Rhythm System

**Why:** the brief's diagnosis — "every section feels identical" — is correct against the Step 2 layout-shell baseline, which was deliberately uniform to validate the grid in isolation. This addendum is the intended next refinement, not a correction of an error.

- **Alternating content widths:** each scene's content now spans a deliberately varied column range within the frozen 12-column grid (e.g., narrower/offset for the memo-like "Why Reasoning Matters," wider for the annotation-dense "Evidence," centered/oversized for the declarative "Philosophy") — variation is expressed as different grid-column spans, never as arbitrary pixel widths.
- **Vertical spacing variation:** scene padding varies by a multiple of `--yukti-space-7` (e.g., `× 1.2`), never a raw pixel value — Section 2.3's "no arbitrary values" rule stays intact because every value is still token-derived.
- **One oversized quotation:** applied exactly once, to the Evidence scene's closing line ("The important outcome is not that the recommendation changed…") — chosen because it's the single strongest editorial line in the mock copy. Deliberately singular, per the brief's "occasional," so it doesn't become a repeated decorative device.

### 15.4 Evidence Scene — Annotation Restyle

**Why:** the brief asks the claim/evidence/finding/result labels to "resemble engineering annotations rather than cards."

**Change:** the bordered-box treatment (Step 2 placeholder) is replaced with a continuous left-rule annotation flow — a single hairline connecting claim → evidence → finding → result, each node marked with a small tick rather than enclosed in its own bordered box. Content is unchanged (Section 1's Scene 4 spec, and the mock copy itself, are untouched) — this is presentation only.

### 15.5 Applications Scene — Sequence, Not List

**Why:** the brief asks for independent per-item reveal and a "sequence" feeling, still with no icons/illustrations (reaffirms the existing `DomainStatement`/no-`FeatureCard` rule from Section 3 — unchanged, just now animated).

**Change:** each `DomainStatement` gets its own `reveal-on-scroll` instance (Motion §4.9) rather than revealing as one static block; hover uses `precision-underline`/`border-appear` (Motion Addendum §15.2), never scale or icon-based emphasis.

### 15.6 Build Order Status Update

This pass implements `reveal-on-scroll`'s IntersectionObserver wiring and the `precision-underline`/`border-appear`/`tracking-shift` hover primitives across Nav, `QuietLink`, and the Applications sequence — which is materially the content of **Build Order Step 3** (Section 6). Step 3 is therefore considered **complete as of this addendum**, delivered in this pass rather than as a separate isolated checkpoint, because the brief's motion requirements made the two inseparable in practice. `HairlineCard` and `FacetControl` remain not yet needed (no card or facet-filter UI exists on the homepage yet) and stay pending until a scene requires them.

---

## SECTION 16 — Addendum v1.2 ("Architectural Editorial" pass)

Ratified per `YUKTI v3 — Architectural Editorial Design` proposal. Compact changelog form (the full prose-justification ceremony of v1.1 doesn't scale to a pass this size without becoming overhead of its own) — each line is still a real, deliberate decision, not drift.

- **New type tier — `--yukti-type-mega`**: scene headings scale up dramatically (clamp to ~180px), left-aligned, uppercase, multi-line word-stacked. `.yukti-type-heading` remains for smaller in-context headings where still needed.
- **Hero recomposed**: sparser, single-column, drafting-frame dividers around the `ReasoningCanvas`; supporting copy demoted to an "annotation" register beneath the canvas rather than large body text under the headline. Copy text itself unchanged (D3) — only hierarchy/placement changed.
- **`ReasoningCanvas` frame**: corner marks changed from crosses to L-shaped drafting brackets (closer to a viewfinder/crop-mark than a registration cross); added `GRAPH MODULE` / `REV 0.2` / `READY` labels. Page-level registration crosses (`.yukti-registration`) are unchanged — different concept (page coordinate reference vs. canvas frame).
- **New scene — Pull Quote**, inserted between Evidence and Applications. New copy ("Reasoning survives scrutiny. Confidence doesn't.") authored directly by the user in the v3 brief — treated as authored content per the same logic as the mock-copy docx, not placeholder. This is the oversized-quotation moment (supersedes the v1.1 choice of using Evidence's closing line for that role — that line now serves as Evidence's own smaller "Annotation" caption instead).
- **Evidence recomposed** into a labeled pipeline diagram (Claim → Evidence → Finding → Result, arrow-connected) plus an "Annotation" caption box (bone-surfaced, paper-grain texture — see Materials below). **Deviation from the brief's own mockup**: the mockup's 5-stage version (Claim / Evidence / Finding / Assumption / Decision) doesn't match the 4 real data points in the mock copy — rather than invent an "Assumption" value, the pipeline uses the 4 real fields only. Flagging this rather than silently fabricating content, consistent with the project's standing no-invented-content discipline (D4).
- **Applications recomposed**: stacked huge-name/tiny-explanation blocks with drafting-tick dividers between entries, replacing the horizontal label/statement row. Still no icons, no cards (unchanged rule).
- **Philosophy recomposed**: each of the four commitments becomes its own fullscreen (100vh) statement, native CSS `scroll-snap` (not a JS scroll-jack/pin — consistent with Motion Rule 5). Each commitment's existing "X over Y." grammar is parsed into three stacked lines (word / "over" / word) rather than new copy being written.
- **Living margin** (the brief's own top-priority item): a small per-scene annotation block (`SECTION NN / [name] / DRAWING YK-0NN / REV [x] / SHEET n/7 / UPDATED 29 JUL 2026`) placed in the trailing grid columns beside each scene's content. Wide viewports only (≥1200px) — there's no spare grid column to place it in below that, and cluttering a narrow layout with marginalia would violate the "barely perceptible" rule it's supposed to serve.
- **Drafting-tick rule**: the system's plain hairline divider gets an optional tick-mark variant (a short perpendicular mark partway along the line) for use inside Evidence/Applications/Hero/Footer — a shared primitive, not four bespoke implementations.
- **Materials**: a shared low-opacity SVG-turbulence grain texture, applied (a) globally/very subtly to the body background (the "graphite" feel) and (b) to the new bone-surfaced Evidence annotation box (the "museum paper" feel — the only bone-background surface that currently exists on the homepage; broader application waits for `HairlineCard`, still pending). A "powder-coat" treatment (soft directional gradient, not flat fill) is added as a utility for filled yellow surfaces (tick dots, canvas corner brackets) — most yellow usage remains thin lines/text where a fill texture wouldn't read, per the existing "yellow is a state signal, not decoration" rule.
- **Coordinate readout format**: changed from normalized 0–1 fractions to integer pixel offsets, matching the brief's mockup and reading more like a real instrument.
- **Footer** implemented now (was deferred to "Build Order Step 5" in the original plan) — the brief's blueprint sign-off content is treated as direct authorization to build it, superseding that deferral.

---

## SECTION 17 — Addendum v1.3 (Entry Sequence)

Ratified per `YUKTI Entry Sequence v1` brief. New component, sits in front of (not inside) the homepage's own scene stack.

- **New component — `EntrySequence`**: full-viewport solid-yellow cover, centered "YUKTI" wordmark (charcoal — reuses `--yukti-color-ink-900`, already this value; no new color token), two door-panels that slide fully off-screen on interaction, revealing the homepage underneath. Markup is a single native `<button>` (free keyboard semantics for click/Enter/Space) containing two door `<span>`s and the wordmark `<span>` — no visible hint/instruction text anywhere, per the brief's explicit "nothing else competes for attention" (an `aria-label` on the button carries the accessible name instead, satisfying D8 without adding visible copy).
- **Session gating**: `sessionStorage` (not `localStorage` — explicitly "per browser session"). Gated via a synchronous inline script in `<head>` (before the render-blocking stylesheet paint completes) adding `yukti-entry-pending` to `<html>` — avoids any flash of the homepage on a fresh session or of the cover on a repeat one. Progressive-enhancement fallback: if JS never runs, the cover's default CSS state is `display:none` and the homepage is fully visible/interactive — a failure here degrades to "no entry sequence," never to "homepage permanently hidden."
- **Scroll lock while pending**: `html.yukti-entry-pending { overflow:hidden }` — prevents a wheel/touch trigger gesture from also scrolling the (invisible, `pointer-events:none`) homepage underneath before the cover clears.
- **Reduced motion**: a distinct code path (`runReducedFade`, not a CSS-only branch) — skips the door/logo choreography entirely and cross-fades the cover out / homepage in over the one shared `--yukti-entry-reveal-duration` token. See Motion Addendum §17 for why that one token is deliberately exempt from the global reduced-motion zero-out.
- **Ambient idle motion**: reuses the existing `--yukti-texture-grain` token (materials, Addendum v1.2) for the "microscopic paper grain movement," plus a single soft radial-gradient highlight drifting slowly for "lighting drift" — deliberately singular/restrained, not the "particles" or "floating forms" (plural) the brief's own example list mentions, since multiple moving shapes would read as decoration, not atmosphere.
- **Does not touch** any existing scene, token, or component from v1.0–v1.2 — it's a layer in front of the homepage, gated on by a class removal, not a rewrite of anything underneath.

---

*End of architecture document. Status: **FROZEN, D1–D14 ratified**, Addendum v1.1, v1.2, v1.3 ratified. Build Order Steps 3 and (informally) parts of 5/6 delivered via addenda; the Entry Sequence (v1.3) is a new pre-homepage layer, not a Build Order step.*
