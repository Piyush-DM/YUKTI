# Elephant Skin — Motion Inventory & Interaction Engineering Specification

**Subject:** https://www.elephant-skin.com/ (homepage, `index.html`)
**Method:** Live DOM/accessibility-tree inspection, network/script audit, and full extraction of the site's own `app.js` (75,796 chars) and inline `<style>` block (56,753 chars). All durations, easing curves, particle counts, and thresholds quoted below are read directly from shipped source, not estimated — except where explicitly marked **[inferred]** for behavior that could not be captured from static source (e.g. exact hover-frame pacing that depends on live mouse input).
**Confidence key:** 🟢 verified in source · 🟡 observed in DOM/CSS, mechanism inferred · 🔴 inferred from convention only

---

## SECTION 1 — Overall Motion Philosophy

**Motion language:** Physical, not decorative. Nothing on this page uses bounce, elastic, or overshoot easing — every custom cubic-bezier resolves to a **deceleration curve** (`cubic-bezier(.2,.7,0,1)`-family: fast start, long soft settle) or a **snap curve** (`cubic-bezier(.76,0,.24,1)`: symmetric ease-in-ease-out, used only for full-panel slides). This reads as engineered precision rather than playful bounce — consistent with the brand's "operating system" positioning (the site literally calls itself infrastructure, not decoration).

**Pacing:** Two speed tiers only. Micro-interactions (hover states, underline sweeps, tab flex) run 200–350ms. Structural transitions (menu panel, reveal-on-scroll, hero intro cross-fade) run 600–900ms. There is no tier in between — nothing lingers at 400–500ms, which keeps the whole system feeling like it has exactly two gears: "instant response" and "deliberate reveal."

**Interaction philosophy:** Nothing animates on load except the hero globe intro and a handful of `.reveal` elements already in the first viewport. Every other animation is **demand-driven**: scroll position, `IntersectionObserver` visibility, or a literal mouse event. This is stated directly in the site's own copy ("Explore. Hover. Scroll. Click.") and enforced in code — canvases call `stop()` via `onView()` the instant they leave the viewport, so idle sections spend zero CPU.

**Visual hierarchy:** Typography leads, data visualization supports, photography/CGI is almost entirely deferred to sub-pages. The homepage is copy- and canvas-driven, not image-driven — a deliberate inversion of typical real-estate-marketing sites, which usually open with a hero photo. Here the hero is a generative particle field standing in for "365 projects."

**Perceived weight:** Everything reads as light/fast except the hamburger menu panel (600ms `cubic-bezier(.76,0,.24,1)`) and the horizontal-scroll pillar section, which is intentionally heavy/slow because it's built to feel like scroll-scrubbed film, not a UI transition.

**Continuity between sections:** The page does not use hard cuts. Every section-level element enters via the same `.reveal` primitive (opacity 0→1 + translateY 30px→0, 0.8s ease), so scroll-driven continuity comes from **repetition of one primitive**, not from bespoke per-section choreography. The exception is the CHEF pillar section and the horizontal-scroll "How developments become brands" band, which are custom scroll-linked pieces.

**Camera behavior:** There is no virtual camera / parallax-scrub scrolling of the whole page (confirmed: `ScrollTrigger` is loaded via CDN but has **zero invocations** in `app.js` — see Section 11). The only "camera" moves are (a) the hero canvas's internal 3D-projected particle globe rotating in place, and (b) the horizontal-scroll section, which translates a `<div id="htrack">` on the X axis in response to vertical scroll — a simulated camera dolly, not a real one.

**Use of whitespace:** Canvases (hero particle field, Living Data cluster visualizations) are explicitly coded to keep a clear rectangle around headline text — `avoidSelector`, `avoidBottomSelector`, and a computed `orbitRegion` in the hero field ensure particles never cross into the text safe-zone. Whitespace is therefore not passive layout — it's an actively enforced exclusion zone recalculated on resize.

**Transition philosophy:** Prefer state-morph over hard replace. The rotating hero word and the multilingual "Say Hi" rotator both cross-fade+scale via a single reusable `.swap` class rather than being swapped instances; the office board flap-clock reuses a single grid and only re-renders text; CHEF's four pillar tabs share one panel rather than four hidden/shown DOM trees.

---

## SECTION 2 — Page Architecture

| Scene | Purpose | Entry State | Exit State | Persistent Elements | Temporary Elements | Scroll Effect | Duration | Narrative Purpose |
|---|---|---|---|---|---|---|---|---|
| **0. Intro / Globe** | First-load spectacle, establishes "365 projects" as living data before any words are read | Full-bleed black canvas, header + hero copy at `opacity:0`, `body.intro-active` | Globe explodes outward, header + copy cross-fade in over 0.9s, `#intro.gone` | Canvas persists (becomes hero field) | `#intro` overlay, "Start the journey" CTA, "click anywhere" hint | None (pre-scroll, click/timeout gated) | ~2–4s (rotation) + 0.9s cross-fade | Signals "this is a system, not a brochure" |
| **1. Hero** | Value proposition + live data toy | Particle field settled in "float" mode, headline visible, rotating pink word | Fades under scroll; canvas keeps running until scrolled out of view | Header nav (sticky), particle canvas, filter buttons | Rotating word (2.4s cycle), demo reel link | Scroll hint only; canvas is independent of scroll position | Continuous (looping) | "This isn't a static company — the data moves" |
| **2. The Elephant Skin Difference** | Thesis statement: Intelligence → Strategy → Performance | Below fold, `.reveal` at rest | Each block reveals independently as it crosses 12% viewport threshold | Section heading | 3 numbered sub-blocks, Business Outcomes list | Standard `.reveal` fade-up | 0.8s per element, staggered 0/60/120/180ms by index%4 | Establishes the CHEF logic before naming it |
| **3. What We Do (word field)** | Breadth-of-service demonstration via dense tag cloud | All tags present, likely at rest opacity or staggered reveal | Persists as static field once revealed | ~100 category words | none | Reveal-on-view only (no horizontal scroll here — see correction below) | 0.8s reveal | Volume as proof of range |
| **4. Selected Work** | Portfolio credibility | Grid of project cards at rest | Cards persist; hover reveals detail | 6 project links | Hover states | Standard reveal | 0.8s | Concrete proof points |
| **5. How Developments Become Brands** | The CHEF pipeline in a scroll-scrubbed horizontal film | Track pinned via CSS `sticky`-style height padding, `htrack` at `translateX(0)` | Track fully translated left; progress bar `#hprog` at 100% width | Section wrapper (`#horizon`), progress bar | 6 pillar cards (Strategy/Brand/Visualization/Film/Sales Experience/Performance) | **Direct 1:1 scroll-to-translateX mapping**, computed every scroll tick via `requestAnimationFrame` | Duration = `track.scrollWidth − innerWidth` px of vertical scroll | Makes the reader physically "travel" the pipeline |
| **6. CHEF® Framework** | Names and diagrams the operating system | 4 pillar cards + interactive detail panel at pillar 1 | Panel content swaps per click; images crossfade | 3 elephant illustration images, tag panel | Article cards (Context/Human/Experience/Funnel), "lit" statement text | `IntersectionObserver` (`threshold:.6`) triggers `.lit` class on statement spans | 0.8s reveal + instant panel swap on click | Turns abstract thesis into a navigable diagram |
| **7. Living Data (ecosystem)** | Proof-by-visualization: real portfolio stats as toys | 4 canvas widgets idle/hidden | Canvases animate only while in viewport; stop on exit | Section heading, CTA card ("Let's talk") | Sales bars, project-cloud canvas, specialist-cloud canvas, city-orbit canvas, growth timeline SVG | Each canvas gated by its own `IntersectionObserver({threshold:.05–.3})`, independent of global scroll % | Continuous while visible; count-up ~1.08s (45 steps × 24ms) | "Not statistics, systems in motion" (site's own copy) |
| **8. Trusted By / Partners** | Social proof at scale (70+ logos) | Filtered logo wall | Filter buttons re-filter in place | Filter controls (Type/Country) | Logo list, "Expand all" toggle | None (filter-driven, not scroll-driven) | Instant/CSS transition | Breadth of trust |
| **9. The Herd Never Sleeps** | Global always-on operations narrative | Static board | Live flap-clock ticks continuously | Office board grid | Feed "pop" notifications spawning at random positions/intervals | Independent `setInterval` ticks, not scroll-bound | Flap animation 350ms (`flapAnim` rotateX), pop spawns randomized | Reinforces 24/7 global operating claim |
| **10. Don't Be Shy / Contact** | Conversion + timezone proof | Office list with live local times | N/A (footer follows) | City/time/status rows | Rotating "Ciao."-style greeting (1.6s cycle, 10 languages) | None | 1s clock tick; 1.6s word rotation | Final human touchpoint before footer |
| **11. Footer** | Legal + secondary nav | Static | N/A | Legal links, social icons | none | None | — | Closure |

**Correction / calibration note:** the accessibility tree suggested the "What We Do" tag cloud might be the horizontal-scroll section; source inspection shows the horizontal-scroll mechanism (`#horizon` / `#htrack` / `#hprog`) is explicitly commented in code as **"How developments become brands"** — i.e., Scene 5, not Scene 3. Scene 3's tag field is a static reveal-only field.

---

## SECTION 3 — Scroll Timeline

Because the homepage has **no global scroll-scrubbed timeline** (no ScrollTrigger master timeline), "percent of page" doesn't drive a single choreography the way it would on a GSAP-pinned site. Instead, scroll drives three independent systems simultaneously:

1. **Global**: `header.nav` toggles `.scrolled` class the instant `scrollY > 40` (background/padding transition, 0.3s).
2. **Per-element**: every `.reveal` node fires once via `IntersectionObserver({threshold:.12})`, independent of absolute scroll %.
3. **Local mechanical**: the horizontal-scroll section computes its own progress `p = (scrollY − section.offsetTop) / dist`, clamped 0–1, entirely self-contained to that section's scroll range.

Approximate timeline (percentages are of total page scroll height, order-of-appearance based on section stacking):

| Scroll % | Event |
|---|---|
| 0% | Globe intro plays (pre-scroll gate); header/hero hidden until intro completes |
| 0% (post-intro) | Header + hero copy cross-fade in (0.9s ease); particle field settles from "explode" into "float" |
| 0–3% | Nav gains `.scrolled` background as soon as `scrollY > 40px` (happens almost immediately) |
| ~6–10% | "The Elephant Skin Difference" heading + 3 pillar blocks reveal, staggered 60ms apart within groups of 4 |
| ~10–14% | Business Outcomes list reveals |
| ~15–20% | "What We Do" tag field reveals (static field, no horizontal motion) |
| ~22–30% | Selected Work project cards reveal, hover-gated detail per card |
| ~32–46% | **Horizontal-scroll pillar section**: page scroll is consumed 1:1 by `#htrack`'s `translateX`; progress bar `#hprog` fills 0→100% across this range; six pillar cards (Strategy → Brand → Visualization → Film → Sales Experience → Performance) pass left to right |
| ~48–55% | CHEF® section: 4 pillar cards reveal; statement text "lights up" word-by-word as each span crosses 60% viewport intersection; clicking a pillar swaps the detail panel + one of 3 elephant illustration images |
| ~56–68% | Living Data section: 4 canvases activate independently as each crosses its own 5–30% visibility threshold — sales bars width-animate (1.1s cubic-bezier), project/specialist/city canvases start their `requestAnimationFrame` loops, growth-timeline SVG draws its line via `stroke-dashoffset` transition (1.6s ease) |
| ~70–76% | Partners/logos section; filter buttons re-filter the wall instantly (no scroll dependency) |
| ~78–86% | "The Herd Never Sleeps" — office flap-board ticks every second; random feed "pop" bubbles spawn on independent timers |
| ~88–95% | Contact/offices section; live per-timezone clocks tick every second; "Ciao."-style greeting rotates every 1.6s |
| 100% | Footer |

---

## SECTION 4 — Component Inventory

### 4.1 Header / Navigation Bar
- **Purpose:** Persistent wayfinding + brand mark + hamburger trigger.
- **States:** Initial (transparent, over hero) → Scrolled (`.scrolled` class adds background + reduces padding, `transition:background .3s,padding .3s`) → Hidden (during intro: `opacity:0;pointer-events:none`).
- **Motion:** opacity/background/padding only — no transform, no scale.
- **Duration/curve:** 0.3s, default ease (no custom bezier specified for this specific rule).
- **Logo hover:** `opacity:1→.8`, 0.2s.
- **Layer order:** z-index above canvas/content; explicitly suppressed (`opacity:0`) while `body.intro-active`.

### 4.2 Hamburger Menu Panel
- **Purpose:** Full navigation overlay.
- **States:** Closed (`translateY(-102%)`, `opacity:0`, `visibility:hidden`) → Open (`.open` class, full translate to 0, opacity 1).
- **Motion:** `transition:transform .6s cubic-bezier(.76,0,.24,1), opacity …` — a symmetric snap curve, not a decelerate curve, giving the panel a mechanical "slam-and-settle" feel distinct from every other transition on the page.
- **Side effects:** `document.body.classList.add('no-scroll')` on open; `Escape` key closes it; click-outside also closes.
- **Menu link hover:** `padding-left` shifts + color change, 0.28s / 0.2s respectively — text nudges right on hover rather than underlining.
- **Menu social icons hover:** background/color invert, 0.2s.

### 4.3 Hero Particle Field (`#heroCanvas`)
- **Purpose:** Generative visualization standing in for the 365-project dataset; doubles as the intro spectacle.
- **Composition:** 1,200 total particles — 495 forming the "globe" shell during intro, 705 additional particles that fill the negative space around the headline once settled ("free flow" / `float` mode).
- **States:**
  - `globe` — particles arranged on a Fibonacci sphere (`GA = π(3−√5)` golden-angle distribution), rotating continuously (`gt` increment), 3D-projected with perspective (`persp = 1.6/(1.6−z)`) and simple Y-axis tilt (0.42 rad).
  - `explode` — on trigger, each particle gets outward velocity `power = 7–18` (random) away from canvas center, plus jitter.
  - `run`/`float` — settled ambient state; particles spring toward per-mode target positions with `pos += (target − pos) * 0.06` (critically-damped spring, not eased tween).
  - Filter-driven cluster modes (`country`, `year`, `service`, `asset` via the "Organize 365 projects by" buttons) — particles re-target into labeled orbit clusters positioned in a computed `orbitRegion` rectangle that is kept clear of the headline (`avoidSelector:'.hero-copy'`) and the filter UI (`avoidBottomSelector:'.hero .filters'`), recomputed on resize.
- **Interactivity:** mouse movement is tracked; nearest particle/cluster highlights and shows a text label at cursor position.
- **Depth/layering:** canvas is `position:absolute;inset:0;z-index:1`; a radial-gradient "veil" (`z-index:2`) sits above it to darken edges and keep text legible; copy sits at `z-index:3`.
- **Performance posture:** single 2D canvas, `devicePixelRatio` capped at 2, full pause via `stop()`/`cancelAnimationFrame` when off-screen (via the same `onView` IO helper used elsewhere).

### 4.4 Rotating Hero Word (`#rotWord`)
- **Purpose:** Reframes the company's category ("Platform," "Discipline," "Infrastructure," "Engine," "Edge," "Intelligence," "Operating System") without a new headline each time.
- **Cycle:** every 2,400ms, add `.swap` class → 300ms later swap `textContent` → remove `.swap`.
- **Motion:** `transition:opacity .3s ease, transform .3s ease` (`.swap` presumably drives opacity/transform to a faded/shifted state, then reverses on removal — a cross-fade, not a slide).

### 4.5 "Say Hi" Multilingual Rotator (`#sayHi`)
- Same `.swap` mechanic, faster cadence: 1,600ms cycle, 200ms swap delay. Cycles through 10 languages/scripts (Hi./Olá./Hola./Ciao./Bonjour./Hallo./你好/안녕/مرحبا/Xin chào.).

### 4.6 Reveal-on-Scroll Primitive (`.reveal`)
- **Purpose:** The single reusable entrance animation used across virtually every section.
- **Initial:** `opacity:0; transform:translateY(30px)`.
- **Final:** `opacity:1; transform:none`.
- **Curve:** plain `ease`, 0.8s, on both properties.
- **Trigger:** `IntersectionObserver({threshold:.12})`, fires once, then `unobserve`s (no re-trigger on scroll-up).
- **Stagger:** `el.style.transitionDelay = (i % 4 * 60) + 'ms'` — a 4-item repeating stagger pattern (0/60/120/180ms) regardless of how many `.reveal` elements exist in a group, not a full sequential stagger.
- **Accessibility:** fully disabled under `prefers-reduced-motion: reduce` (opacity 1, transform none, no transition).

### 4.7 Horizontal-Scroll Pillar Track (`#horizon` / `#htrack` / `#hprog`)
- **Purpose:** "How developments become brands" pipeline (Strategy → Brand → Visualization → Film → Sales Experience → Performance).
- **Mechanism (explicitly commented in source as a deliberate choice):** *"Robust sticky-based horizontal scroll (no GSAP pin → never breaks on scroll-up)."* Section height is padded to `trackScrollWidth − innerWidth + innerHeight` so the track has room to travel while the section behaves like a normal sticky block, avoiding the well-known GSAP `pin` bug where fast scroll-up can desync the pinned element.
- **Motion:** `track.style.transform = translate3d(−p*dist, 0, 0)` recalculated every scroll tick inside `requestAnimationFrame` (throttled with a `ticking` boolean guard — one calculation per frame max, not per scroll event).
- **Progress bar:** `#hprog` width set to `p*100%` in the same tick — a literal 1:1 scrubber, no easing at all (the "easing" is whatever the user's physical scroll motion is).
- **Responsive behavior:** disabled entirely below 760px — mobile gets the cards in normal vertical flow instead (`section.style.height=''; track.style.transform=''`).
- **Recalculation triggers:** on `resize`, on `load`, and again once `document.fonts.ready` resolves (prevents a common bug where font-swap reflow changes `scrollWidth` after layout was first measured).

### 4.8 CHEF® Pillar Tabs
- **Purpose:** Interactive diagram of the four-pillar framework (Context/Strategy, Human/Audience, Experience/Narrative, Funnel/Execution).
- **States:** Initial (Pillar 1 "Context" active) → clicked (swaps `tag/title/sub/desc/produces/cases` text instantly, swaps one of 3 elephant illustration images).
- **Statement "lit" text:** separate mechanism — `[data-lit]` spans inside `.statement` gain `.lit` class via `IntersectionObserver({threshold:.6})`, i.e., text "lights up" (likely a color/weight change) only once 60% of that specific span is in view — a finer-grained trigger than the general `.reveal` (12%), used because this is word-level emphasis, not block entrance.

### 4.9 Living Data — Sales Impact Bars (`#salesBars`)
- **Purpose:** $5B sales-impact breakdown by asset class.
- **Motion:** bar fill `width` transition, `1.1s cubic-bezier(.2,.7,0,1)` (deceleration curve), triggered once via `IntersectionObserver({threshold:.3})` — widths jump from `0` to a `data-w` percentage.
- **Hover:** each bar shows a tooltip (`#salesTip`) with label/value/%/count/example-projects text, toggled via `mouseenter`/`mouseleave` + `.show` class.

### 4.10 Living Data — Big Numbers Count-Up (`.bncard`)
- **Purpose:** Animated stat counters (365 projects, 100+ specialists, etc.).
- **Motion:** `setInterval` step increment, `step = target/45` every 24ms (~1.08s total to reach target) — a linear count, not eased.
- **3D tilt (desktop, motion-safe only):** on `mousemove`, card computes cursor offset from center and applies `rotateY(px*9deg) rotateX(-py*9deg) translateY(-6px)`; an inner layer (`.bn-inner`) parallax-shifts `translate(px*18, py*18) translateZ(40px)`; a glow layer follows with its own offset multiplier (`*55`). Resets to `transform:''` on `mouseleave` (CSS transition, not JS-animated return — relies on whatever `transition` is declared on `.bncard`/`.bn-inner`/`.bn-glow`, likely the `.35s cubic-bezier(.2,.7,…)` found elsewhere for 3D transform surfaces).
- **Reduced motion:** tilt entirely skipped (`if(!reduce)`).

### 4.11 Living Data — Project/Specialist/City Canvases
- **Purpose:** Particle-cluster visualizations of the 365-project and 130-person datasets, re-groupable by filter buttons (Country/Year/Asset/Service for projects; Gender/Discipline/Seniority/Tenure for specialists).
- **Motion:** identical spring-interpolation model to the hero field (`pos += (target−pos)*0.04–0.06`), continuous idle drift via `angle += small increment` and `radius` offset (so particles orbit their cluster center even at rest, never fully static).
- **City canvas:** genuine orbital motion — each city node revolves around a central "ES" hub at an angle rate scaled by its project count (`0.6 + n*0.04`), on concentric rings.
- **Interactivity:** nearest-node hover detection via distance check every frame; hovered node turns white and shows a tooltip.
- **Lifecycle:** every canvas is gated by its own `onView` `IntersectionObserver` (thresholds 0.05–0.3) — `start()`/`stop()` toggle the `requestAnimationFrame` loop, so off-screen canvases consume zero CPU.

### 4.12 Growth Timeline Chart (`#tlChart`)
- **Purpose:** 2017→2026 project-count growth chart (9 milestones).
- **Motion:** SVG path line-draw via `stroke-dasharray`/`stroke-dashoffset` set to path length then animated to 0 — `transition: stroke-dashoffset 1.6s ease`, triggered on next frame after build.
- **Nodes:** each milestone is a `<circle>` + label group with `opacity:0; transition:opacity .45s ease`, `cursor:pointer` — presumably faded in progressively or on hover/click (active node rendered larger, r=6 vs 4.5, filled pink vs dark).
- **Rebuild trigger:** full SVG teardown/rebuild on resize (`chart.innerHTML=''`) rather than a resize-transform — simplest-correct approach for a data-driven chart, at the cost of losing in-flight animation state on resize.

### 4.13 Office Status Board ("The Herd Never Sleeps")
- **Purpose:** Flight-departure-board-style live status grid for 10 global offices.
- **Motion:** `@keyframes flapAnim{from{rotateX(86deg);opacity:.3}to{rotateX(0);opacity:1}}` — a mechanical split-flap character reveal, evoking analog airport boards. Character cells are sized via CSS custom properties (`--cw`, `--ch`, `--cg`) for responsive flap-grid sizing.
- **Row expand:** `.opsb-row.open .opsb-exp` reveals extra detail via `@keyframes opsExp` (opacity 0→1 + translateY(-4px)→0).
- **Swipe hint (mobile):** `@keyframes opsHintNudge` — horizontal nudge (`translateX(0→7px→0)`) to teach the user the board is horizontally scrollable.
- **Live feed pops:** randomly-positioned toast bubbles (`.herd-pop`) spawn within a constrained band (`top: 32–58%`, `left: 8–60%`) so they never overlap the headline or numbered index labels — same "avoid the safe zone" philosophy as the hero canvas, done via inline randomized `style.left/top` instead of a collision engine.

### 4.14 Offices/Contact Live Clocks
- **Purpose:** Real per-timezone local time for each office, ticking every second via `Intl.DateTimeFormat` + `setInterval(tick, 1000)`. No animation on the digits themselves (direct text replacement) — motion budget is spent elsewhere (the flap board), this is plain data.

### 4.15 Demo Reel Modal
- **Purpose:** Lightbox video playback.
- **States:** Closed → Open (`.open` class, `aria-hidden` toggled, `no-scroll` on body). Iframe is only constructed on open (`f.innerHTML = '<iframe …>'`), not pre-loaded — avoids an autoplaying/pre-buffering video sitting in the DOM at all times.
- **Close:** click on modal backdrop (`e.target===m`) or explicit close control.

### 4.16 Cookie Consent Banner (`.es-cc`)
- **Purpose:** Standard consent gate.
- **Position/Style:** fixed bottom-left, `backdrop-filter:blur(12px)`, dark translucent panel, `border-radius:16px`, heavy `box-shadow`.
- **Motion:** not captured in the grabbed CSS snippet — likely a simple slide/fade-in on load given the rest of the system's restraint (no evidence of a bespoke banner animation).

---

## SECTION 5 — Typography Motion

| Element | Split Strategy | Reveal Direction | Scrubbing | Opacity | Mask | Stagger | Duration | Ease | Trigger |
|---|---|---|---|---|---|---|---|---|---|
| Section headings (`.reveal` wrapped) | Block (whole heading as one node) | Up (`translateY(30→0)`) | No — binary on/off, no scroll-scrub | 0→1 | None | 4-slot repeating (0/60/120/180ms) within sibling groups | 0.8s | `ease` (default CSS) | `IntersectionObserver` 12% |
| CHEF statement text (`[data-lit]`) | Word/phrase-level spans, pre-split in markup | In place (no translate implied by class name) | No — binary, but finer-grained per-span | Implied (`.lit` class, exact property not captured — conventionally opacity/color) | None detected | Sequential-by-nature (each span has its own observer entry) | Not captured (likely CSS transition on `.lit`) | Not captured | `IntersectionObserver` 60% (deliberately stricter than the 12% default — used for word-level emphasis, not block entrance) |
| Hero rotating word | Whole-word swap, not character split | Cross-fade (opacity+transform per `.swap` rule) | No | swap-state driven | None | N/A (single element) | 0.3s in, 2.1s hold, 0.3s out (2.4s total cycle) | `ease` | `setInterval`, not scroll |
| "Say Hi" language rotator | Whole-word swap | Cross-fade | No | swap-state driven | None | N/A | 0.2s swap within 1.6s cycle | `ease` | `setInterval`, not scroll |
| Intro headline (`.intro-content h2`) | Block, with `.pink` inline span for accent word | Static reveal via parent opacity | No | Inherits parent `.hero .wrap` opacity transition | None | None | 0.9s | `ease` | Intro sequence completion |
| Growth-timeline node labels | Per-node `<text>` in SVG | Fade | No | 0→1 via `opacity` on group | None | Implicit (nodes render in data order) | 0.45s | `ease` | Likely hover/active-state driven (node opacity starts 0) |

**No character-level or line-level split-text animation exists anywhere on this homepage.** This is a notable, deliberate restraint given how common SplitText/Splitting.js word-cascade reveals are on comparable "premium" sites — Elephant Skin's typography motion budget goes entirely into whole-block reveals, whole-word rotators, and one word-level "lit" emphasis mechanism, never per-character stagger.

---

## SECTION 6 — Image Motion

The homepage is markedly **CGI/photography-light** relative to a typical real-estate site — the only static raster/vector images identified in the DOM are:
- The Elephant Skin wordmark/logo (header, intro, footer) — no motion beyond standard logo hover opacity.
- Three "elephant chef" illustrations inside the CHEF® section (tasting/cooking/plating), used as pillar-state imagery that swaps as the active pillar tab changes — an instant swap (no crossfade transition observed in the grabbed source; if a fade exists it would live in unexamined CSS rules for `.chef-img` or similar, not confirmed).

**No hero photograph, no parallax image layers, no clip-path image reveals, no scroll-linked image scale/rotate** exist on this page — that entire motion category is deferred to the **project sub-pages** (`project.html?id=…`), which is where the CGI/renderings/film content actually lives (linked from Selected Work cards). This homepage's "images" are functionally replaced by the generative canvas visualizations (Section 4.3, 4.11–4.12) — data-as-imagery instead of photography-as-imagery.

**Loading animation:** none observed for images (no blur-up, no skeleton shimmer) — consistent with there being almost no heavy images on this page to begin with.

---

## SECTION 7 — Navigation

- **Sticky logic:** Header is always `position:fixed`-equivalent (persists across all scroll positions per the DOM tree, present once outside all `region`s). It does not hide-on-scroll-down/show-on-scroll-up — it only toggles a background/padding state at the 40px threshold.
- **Scroll awareness:** Single boolean check (`scrollY > 40`), not velocity- or direction-aware. Binary, not proportional.
- **Logo animation:** none beyond the standard hover opacity dip (1→0.8, 0.2s). No logo transform on scroll, no logo swap between light/dark variants detected in the grabbed rules (though the "Legal & Trust Center" / theme references in cookie copy suggest a light/dark theme system might exist independently — not confirmed as logo-linked).
- **Menu animation:** full-panel slide/fade per Section 4.2, gated by a snap-curve (`.76,0,.24,1`) — the single most "designed" easing curve on the page, reserved exclusively for this one interaction, which signals its importance in the hierarchy (full navigation takeover).
- **Hover system:** Menu links use a padding-left nudge + color change (not underline-draw) — text physically steps toward the cursor's reading direction on hover. This is a distinct hover grammar from buttons elsewhere (see Section 10).
- **Active states:** CHEF pillar tabs and Living Data filter buttons use an `.active` class (styling not fully captured, but consistently toggled via `classList.remove('active')` on siblings + `add('active')` on the clicked button — a strict single-active-item pattern, no multi-select anywhere in the filter systems).

---

## SECTION 8 — Section Transitions

Because there is no master scroll timeline, transitions **between** sections are not choreographed as a pair — each section reveals independently via the same `.reveal`/`IntersectionObserver` primitive. The meaningful "transition" analysis is therefore about **what mechanism governs entry**, not about cross-fades between adjacent sections:

| Between | What leaves | What stays | What transforms | Continuity | Discrete or Continuous |
|---|---|---|---|---|---|
| Intro → Hero | `#intro` overlay (`.gone`, opacity 0) | Canvas (globe → float), header, hero copy | Canvas particle state (`explode`→`run`) | High — same canvas element, not a swap | Continuous (state machine on one object) |
| Hero → Difference | Hero canvas keeps animating behind/below | Header (persistent) | New `.reveal` blocks fade up | Low — separate concern, header is the only continuity anchor | Discrete |
| Selected Work → Horizontal Pillar Section | Vertical scroll consumption | Header, progress-bar convention (introduced here for the first time) | Scroll axis effectively re-purposed from vertical-reveal to horizontal-scrub for the section's duration | Medium — page keeps scrolling down, but visually content moves sideways | Discrete but scroll-mechanically continuous (no pin-jump; the "sticky, no-pin" design in 4.7 exists specifically to avoid a jarring discrete jump) |
| Horizontal Pillar → CHEF | Progress bar resets implicitly (new section, new `IntersectionObserver`) | none explicit | Pillar concept re-appears as 4 interactive cards instead of 6 scrubbed cards | Conceptual only (same CHEF framework, different UI pattern) | Discrete |
| CHEF → Living Data | Static illustration/tab UI | none | Shifts from "explain the system" to "prove the system with real numbers" | Conceptual | Discrete |
| Living Data → Partners | Canvas rendering stops (`stop()` on scroll-out) | none | Visualization → static logo grid | Low | Discrete |
| Partners → Herd | Filter UI | none | Static wall → live-ticking flap board | Low | Discrete |
| Herd → Contact | Random pop notifications | Office-city list concept reused | Flap-board format → line-item format with live clocks | Medium (same underlying office dataset, second presentation) | Discrete |

**Overall:** the page is built from **discrete, independently-triggered sections**, unified only by (a) one shared reveal primitive, (b) the persistent header, and (c) recurring data (the 365/37/100+ figures reappear in multiple sections in different visual forms). It is not a single continuous scrollytelling experience in the GSAP-timeline sense — it's closer to "a stack of independently-alive widgets," which is a meaningfully different (and more failure-resistant) architecture than a fully pinned/scrubbed site.

---

## SECTION 9 — Motion Tokens

| Token | Duration | Curve | Distance | Opacity | Scale | Trigger |
|---|---|---|---|---|---|---|
| **Fade Up** (`.reveal`) | 0.8s | `ease` | translateY 30px | 0→1 | none | IO @ 12% |
| **Word Swap** (`.swap`) | 0.3s in/out (hero word), 0.2s (Say Hi) | `ease` | none (opacity/transform per rule, transform not itemized) | cross-fade | implied subtle scale/shift | `setInterval` |
| **Spring Cluster** (particle systems) | continuous, ~0.06 damping/frame (≈ settles in ~15–20 frames) | critically-damped spring (not a CSS ease) | variable (canvas-space) | n/a (canvas alpha ~0.85–0.9 constant) | n/a | mode/filter change |
| **Bar Fill** | 1.1s | `cubic-bezier(.2,.7,0,1)` | width 0→target% | n/a | none | IO @ 30% |
| **Count-Up** | ~1.08s (45×24ms steps) | linear | n/a | n/a | none | IO @ 50% |
| **Line Draw** (timeline SVG) | 1.6s | `ease` | full path length via dashoffset | n/a | none | on build (post-layout) |
| **Flap Reveal** | not explicitly timed (keyframe-based, browser default ~ whatever `animation-duration` is set to elsewhere, not captured in snippet) | n/a (keyframe, linear unless overridden) | rotateX 86°→0° | 0.3→1 | none | data tick / mount |
| **Panel Slide** (menu) | 0.6s | `cubic-bezier(.76,0,.24,1)` | translateY -102%→0 | 0→1 | none | click hamburger |
| **3D Tilt** (big-number cards) | live (mousemove-driven, no fixed duration); return-to-rest presumably ~0.35s | `cubic-bezier(.2,.7,…)` for return (inferred from the `.35s cubic-bezier(.2,.7,` CSS match) | rotateX/Y ±9°, translateY -6px, inner parallax ±18px | n/a | none | `mousemove`/`mouseleave` |
| **Progress Scrub** (horizontal section) | 1:1 with physical scroll, zero independent easing | linear (scroll IS the ease) | full track width minus viewport | n/a | none | scroll (rAF-throttled) |
| **Accordion Expand** (`opsExp`) | not captured (keyframe named, duration external) | n/a | translateY -4px→0 | 0→1 | none | row `.open` toggle |
| **Nudge Hint** (`opsHintNudge`) | not captured (looping keyframe) | n/a | translateX 0→7px→0 | n/a | none | mount (mobile only) |
| **Nav Scroll State** | 0.3s | default | background/padding only | n/a | none | `scrollY>40` |

There is no "Mask Reveal," "Slide Clip," "Image Expand," "Card Stack," or "Heading Compress" token in this build — those categories are simply **not used** on the homepage. The token set is intentionally narrow: one entrance primitive, one swap primitive, one physics primitive (spring), one scrub primitive, one panel-slide primitive.

---

## SECTION 10 — Interaction Grammar

Inferred rules, ranked by how consistently they're enforced in source:

1. **Never use bounce/overshoot easing.** Every custom bezier is monotonic (deceleration or symmetric ease) — confirmed across all 6 extracted `cubic-bezier` instances.
2. **Only one full-panel "snap" curve exists** (`.76,0,.24,1`), reserved exclusively for the hamburger menu — signaling that this is the only "modal-weight" interaction in the system.
3. **Canvases must self-pause off-screen.** Every generative visualization (hero field, 3 Living Data canvases, growth chart) is wrapped in an `IntersectionObserver`-gated `start()`/`stop()` pair. No canvas runs unconditionally.
4. **Reveal triggers fire once, never re-trigger on scroll-up.** `io.unobserve(el)` immediately after adding `.in` — this is a "show once" philosophy, not a "re-animate every time it's in view" philosophy.
5. **Avoid GSAP's `pin` for scroll-driven layout**, even though GSAP + ScrollTrigger are loaded. The horizontal-scroll section explicitly avoids the library's own pinning feature in favor of a hand-rolled sticky-height + rAF-transform approach, with the reasoning commented directly in source ("never breaks on scroll-up"). This is the single most opinionated engineering decision on the page.
6. **Cluster/orbit visuals must never overlap text.** Both the hero particle field and (by convention) the Herd feed-pop notifications compute or hard-code exclusion zones relative to headline/filter-UI bounding boxes.
7. **Motion is throttled to one calculation per animation frame**, never per raw event — every scroll listener uses a `ticking` boolean + `requestAnimationFrame`, never runs handler logic directly in the scroll callback.
8. **`prefers-reduced-motion` is respected structurally, not just cosmetically** — the hero's 3D tilt and `.reveal` are both explicitly disabled (not just shortened) under the media query; particle systems also skip their mousemove-tilt branch entirely (`if(!reduce)`).
9. **Filters are single-select, never multi-select**, across every filter UI (hero project-organizer, Living Data mode-switchers, Partners logo filters) — one active category classification model reused everywhere instead of faceted multi-filtering.
10. **Data-driven UI regenerates its DOM/SVG on resize rather than transforming in place** (timeline chart teardown/rebuild; canvas `resize()`+`calc()`) — correctness over animation continuity when the viewport itself changes.
11. **Micro-interactions respond to intent, not to scroll.** Hover tilt, filter clicks, word rotators, and modal open/close are all discrete user- or timer-driven, never scroll-position-driven — scroll is reserved for reveal/transport (Sections 4.6, 4.7), not for micro-detail animation.
12. **Text motion never goes below the word level.** No character-split animation exists anywhere, even though the framework loaded (GSAP) is fully capable of it — a deliberate scope limitation, not a technical one.

---

## SECTION 11 — Technical Stack Inference

| Technology | Evidence | Confidence |
|---|---|---|
| **Vanilla JS (ES2017+, IIFE-per-feature architecture)** | Entire `app.js` is a sequence of `(function(){...})()` blocks, one per feature, no bundler-artifact signatures (no webpack/vite module wrapper, no React/Vue runtime present) | 🟢 |
| **GSAP core 3.12.5** (loaded from cdnjs) | `<script src=".../gsap/3.12.5/gsap.min.js">` present in document | 🟢 loaded, but... |
| **GSAP ScrollTrigger 3.12.5** | Script tag present, but **zero calls** to `ScrollTrigger.create`, `gsap.timeline`, or any `gsap.*` API found anywhere in `app.js`'s 75KB | 🟢 loaded-but-unused on this page (likely used on inner pages like `approach.html`, `project.html`, or kept as a shared bundle across the site even where unneeded on this route) |
| **Native `IntersectionObserver`** (10 distinct usages) | Powers `.reveal`, CHEF "lit" text, all 4 canvas start/stop gates, big-number count-up | 🟢 |
| **`requestAnimationFrame` loops** | Every canvas visualization; horizontal-scroll scrub | 🟢 |
| **Canvas 2D API** (not WebGL) | `canvas.getContext('2d')` used for hero field, projects/specialists/cities visualizations | 🟢 — no WebGL/THREE despite the "globe" reading as 3D; it's a hand-rolled perspective projection on a 2D canvas |
| **Native SVG (imperative DOM construction)** | Growth timeline built via `document.createElementNS`, not a charting library | 🟢 |
| **CSS `cubic-bezier` custom easing + native transitions** (no Motion/Framer/anime.js) | All easing found in plain CSS `transition:` rules, not JS-driven tweens | 🟢 |
| **No Lenis / smooth-scroll library** | Native browser scroll is used directly (`addEventListener('scroll', …, {passive:true})`); no `data-lenis` attributes or Lenis instantiation found | 🟢 (absence confirmed, not just unchecked) |
| **No Barba.js / page-transition router** | Regular `<a href="...">` links to `.html` pages (`project.html?id=biltmore`, `approach.html`, etc.) — full page loads, no SPA router | 🟢 |
| **No Swiper/Splide carousel library** | Logo wall, project cards use plain flex/grid, not a carousel dependency | 🟡 (inferred from absence in the script list; not exhaustively grepped) |
| **`Intl.DateTimeFormat`** for live office clocks | Directly observed in source | 🟢 |
| **Google Tag Manager** | `googletagmanager.com/gtag/js?id=G-Q1P9HY13J8` | 🟢 |
| **Custom cookie-consent script** (`cookies.js`) and a **guided-tour script** (`tour.js`) | Present as separate site scripts, not analyzed in depth here | 🟡 |

**Headline finding:** this is a **hand-built, dependency-light motion system**. GSAP is present in the stack (likely shared across the whole site's page bundle) but the homepage itself does not lean on it — every scroll/reveal/canvas mechanism here is native browser APIs. That is unusual for a site with this level of visual ambition and is worth calling out explicitly to a rebuild team: **do not assume a GSAP timeline exists to reverse-engineer** — the actual choreography is procedural, frame-by-frame code.

---

## SECTION 12 — Performance

**GPU-accelerated transforms in use:**
- Menu panel `transform: translateY(...)` (compositor-friendly).
- Big-number card `transform: rotateX/rotateY/translateY/translateZ` (3D tilt) — correctly using `transform`, not `top/left`.
- Horizontal-scroll `translate3d(...)` — explicit `3d` hint to force GPU layer promotion, a deliberate performance choice (rather than plain `translateX`).
- Hover nudges (menu links, filter buttons) — `padding-left` is used for the menu-link hover, which is **not** GPU-accelerated (padding is a layout-triggering property). This is the one clear anti-pattern found: a hover interaction on every menu link causes a layout recalculation each time, though the blast radius is tiny (single small element, infrequent trigger) so it's unlikely to visibly matter.

**Paint-heavy effects:**
- `backdrop-filter: blur(12px)` on the cookie consent panel — GPU blur, moderate cost, but it's a single fixed small panel, low risk.
- Canvas `globalAlpha` blending and per-frame `clearRect` + redraw across up to ~1,200 particles (hero) simultaneously with 2 more active canvases if a user scrolls Living Data into view while the hero canvas is still technically in the DOM (though the hero's own `onView`/IO gating should stop it once scrolled far enough away — confirm this threshold is generous enough in a rebuild, since the hero canvas is very tall relative to viewport and could stay "in view" per a loose IO config longer than intended).

**Layout shifts:**
- The horizontal-scroll section explicitly guards against a layout-shift-adjacent bug: it recalculates `dist`/`section.height` again after `document.fonts.ready`, because web-font swap (FOIT/FOUT) changes text width, which changes `track.scrollWidth`, which would otherwise desync the scroll-to-position mapping if measured too early. This is a sophisticated, non-obvious fix worth preserving in a rebuild.
- The growth-timeline SVG's full teardown/rebuild on resize could produce a visible flash/shift on rapid resize (e.g., orientation change on mobile), though this is a minor, infrequent-trigger concern.

**Expensive filters:** none beyond the one `backdrop-filter: blur(12px)` noted above — the page is otherwise filter-light (no heavy `box-shadow` chains beyond a couple of single soft shadows on the office board and cookie panel, no SVG filters, no CSS `filter: blur()` on large elements).

**Optimization opportunities for a rebuild:**
- Convert the menu-link hover from `padding-left` to a `transform: translateX(...)` to make it fully compositor-only.
- Consider `will-change: transform` on the horizontal-scroll `#htrack` and the hero canvas's parent, since both are guaranteed-active transform targets during their respective interaction windows.
- Cap particle count adaptively by viewport/device (e.g., halve the 1,200-particle hero field on narrow/low-DPR devices) — currently the only adaptive control found is `dpr = min(devicePixelRatio, 2)`, not particle count.
- The `.35s cubic-bezier` 3D-tilt return-to-rest on big-number cards should be double-checked for jank on trackpad/high-frequency `mousemove` — computing three separate `transform` strings (`card`, `inner`, `glow`) per mousemove event is fine at 60–120Hz but worth profiling on lower-end hardware.

**Likely FPS:** 🟡 [inferred, not measured] — Given passive scroll listeners, rAF-throttled everything, and IO-gated canvas lifecycles, the architecture is built to sustain 60fps on modern hardware; the highest-risk moment is the intro globe (1,200-particle 3D projection + explode physics) on low-end/mobile devices, since that's the one unconditional, unthrottled-by-visibility animation on the page (it plays before the user has scrolled anywhere, so there's no IO gate protecting it — it's presumably assumed to always be in view at load).

---

## SECTION 13 — Reusable Motion Library

A rebuild-ready, site-agnostic extraction of the tokens in Section 9, written as implementation-ready primitives:

### `fade-up-reveal`
- **Purpose:** Generic scroll-triggered block entrance.
- **Trigger:** element enters viewport (IO threshold 0.12, `once: true`).
- **Duration/Ease:** 800ms, `ease` (or swap for `cubic-bezier(.16,1,.3,1)` if a slightly snappier decel is preferred).
- **Properties:** `opacity 0→1`, `transform: translateY(30px)→none`.
- **Stagger:** cycle a 4-step delay table (`[0,60,120,180]ms` by `index % 4`) rather than a full linear stagger — keeps large groups from taking seconds to fully reveal.
- **Usage:** any card grid, any heading block, any list.

### `word-swap-crossfade`
- **Purpose:** Rotate through a word list in a fixed slot without layout shift.
- **Trigger:** interval timer (parameterize the cycle length: 2400ms for slow/editorial, 1600ms for fast/playful).
- **Duration:** 300ms out, instant text swap, 300ms in (or 200ms/200ms for the faster variant).
- **Properties:** opacity + optional small translateY/scale during the "out" half.
- **Usage:** rotating value-prop word, rotating greeting/language, rotating stat label.

### `spring-cluster`
- **Purpose:** Physically-interpolated grouping/re-grouping of many small elements (particles, dots, avatars) into labeled clusters.
- **Trigger:** filter/mode change.
- **Motion model:** `pos += (target − pos) * k`, `k ≈ 0.04–0.06` per animation frame — not a CSS transition; must run in a `requestAnimationFrame` loop.
- **Idle behavior:** even at rest, apply small independent orbital/angular drift per item so the cluster never looks frozen.
- **Usage:** any "living data" visualization, org charts, tag clouds, geographic distributions.

### `bar-fill-decel`
- **Purpose:** Data bar reveal.
- **Trigger:** IO threshold 0.3, once.
- **Duration/Ease:** 1100ms, `cubic-bezier(.2,.7,0,1)`.
- **Property:** `width: 0 → target%`.

### `linear-count-up`
- **Purpose:** Numeric counter animation.
- **Duration:** ~1080ms via 45 steps at 24ms intervals (or compute steps dynamically: `Math.max(1, target/45)` per tick).
- **Ease:** linear (deliberately — a counting number reads as more "real" without easing).

### `svg-line-draw`
- **Purpose:** Reveal a chart/path progressively.
- **Mechanism:** set `stroke-dasharray = pathLength`, `stroke-dashoffset = pathLength`, then transition `stroke-dashoffset → 0` over 1600ms, `ease`, triggered one frame after the path is added to the DOM (needed so `getTotalLength()` is measurable and the transition isn't skipped by a same-frame style write).

### `panel-slide-snap`
- **Purpose:** Full-viewport modal/menu panel takeover.
- **Duration/Ease:** 600ms, `cubic-bezier(.76,0,.24,1)` (symmetric ease-in-ease-out — reserve this specific curve for nothing else, so it retains "this is the one big moment" signaling value).
- **Properties:** `transform: translateY(-102%)→0`, `opacity 0→1`, `visibility hidden→visible`.
- **Side effects:** lock body scroll, bind `Escape` to close, close on backdrop click.

### `scroll-scrub-track` (sticky-no-pin horizontal scroll)
- **Purpose:** Horizontal storytelling band driven by vertical scroll, without using a scroll-jacking `position:fixed` pin.
- **Mechanism:** pad the section's height to `trackScrollWidth − viewportWidth + viewportHeight`; on scroll (rAF-throttled), compute `p = clamp((scrollY − sectionTop)/dist, 0, 1)`; apply `translate3d(-p*dist, 0, 0)` to the track and `width: p*100%` to any paired progress bar.
- **Responsive fallback:** disable below a breakpoint (e.g. 760px) and let content flow vertically instead.
- **Recalculate on:** resize, load, and `document.fonts.ready` (critical — prevents post-font-swap desync).

### `3d-tilt-parallax`
- **Purpose:** Cursor-reactive depth effect on a card.
- **Mechanism:** on `mousemove`, compute normalized cursor offset from card center (`-0.5…0.5` range); apply `rotateY(px*9deg) rotateX(-py*9deg) translateY(-6px)` to the card, a larger `translate(px*18,py*18) translateZ(40px)` to an inner layer, and an even larger offset to a glow/light layer for parallax depth. Reset via CSS transition on `mouseleave`.
- **Accessibility:** skip entirely under `prefers-reduced-motion: reduce`.

### `split-flap-reveal`
- **Purpose:** Mechanical, analog-board-style character reveal for live/ticking data.
- **Motion:** `@keyframes { from{ rotateX(86deg); opacity:.3 } to{ rotateX(0); opacity:1 } }` per character/cell on data change.
- **Usage:** live counters, status boards, departure-board-style data tables.

### `viewport-gated-canvas`
- **Purpose:** Universal performance wrapper for any canvas/rAF-driven visualization.
- **Mechanism:** wrap `start()`/`stop()` (which toggle the rAF loop) in an `IntersectionObserver` (threshold tunable 0.05–0.3 depending on how eagerly it should start); never run a canvas loop unconditionally.

---

## SECTION 14 — Adaptation for YUKTI

Mapping the interaction *language* (not the branding, not the real-estate domain) onto an institutional/analytical product surface:

| Elephant Skin Interaction | ↓ | Equivalent YUKTI Interaction |
|---|---|---|
| Hero particle globe (1,200 particles → intro spin → explode → settle into headline-avoiding cluster field) | ↓ | **Reasoning-graph reveal**: an intro visualization of nodes representing evidence/claims coalescing from a scattered field into a structured graph around the primary headline/thesis, avoiding text safe-zones the same way |
| Rotating hero category word ("Platform"/"Engine"/"Intelligence"/…) | ↓ | **Rotating framing word** for what YUKTI *is* ("Analysis"/"Evidence Layer"/"Reasoning System"/"Verification Engine"/…), same 2.4s cross-fade cadence |
| Filter-driven particle re-clustering (Country/Year/Asset/Service) | ↓ | **Evidence re-clustering by facet** (by Source / by Confidence / by Date / by Claim-Type) — same spring-interpolation re-grouping mechanic applied to evidence nodes instead of project dots |
| Pinned/scrubbed horizontal pillar section (Strategy→Brand→Visualization→Film→Sales→Performance) | ↓ | **Pinned evidence/reasoning timeline** — a horizontally-scrubbed pipeline of Claim → Evidence Gathered → Cross-Checked → Weighted → Conclusion → Confidence Score, using the identical sticky-no-pin, font-ready-aware scroll math |
| CHEF® four-pillar interactive tabs (Context/Human/Experience/Funnel) | ↓ | **Evidence-panel expansion**: a four (or N)-stage methodology diagram (e.g. Ingest → Verify → Correlate → Report) where clicking a stage swaps the detail panel + a supporting diagram, exactly like the pillar-tab mechanism |
| "Lit" word-by-word statement emphasis (60% IO threshold) | ↓ | **Progressive claim emphasis**: key phrases in a thesis/summary statement light up individually as the reader's scroll centers them — useful for walking a reader through a chain of reasoning sentence-by-sentence |
| Living Data canvases (sales bars, project/specialist clouds, city orbit, growth timeline) | ↓ | **Live evidence/verification dashboard**: bar-fill for confidence-by-category, particle-cloud for source distribution, orbital view for cross-referenced entities, line-draw timeline for how confidence/coverage grew over the investigation | 
| Big-number 3D-tilt cards with count-up | ↓ | **Institutional headline stat cards** (e.g. "N sources verified," "N cross-checks passed") with the same cursor-parallax tilt and linear count-up-on-view |
| Office status board (flap-clock, live per-timezone clocks, random "pop" activity feed) | ↓ | **Live pipeline/activity board**: a flap-style board showing active verification jobs, agents, or data-source pulls in real time, with the same randomized-position "pop" toast pattern for "new evidence found in [source]" notifications |
| Hamburger menu, single reserved snap-curve panel slide | ↓ | Preserve as-is for **primary navigation** — the one "big modal moment" curve should be reserved the same way, for whatever YUKTI's single most-important full-panel takeover is (e.g. a full investigation/report viewer) |
| Reveal-on-scroll primitive (`.reveal`, 0.8s, 4-slot stagger) | ↓ | Reused verbatim as the **default entrance animation** for every section of an institutional report/landing page — headings, findings blocks, methodology sections |
| `prefers-reduced-motion` hard-disables (not just shortens) tilt/reveal | ↓ | Preserve exactly — an institutional/analytical product has an even stronger obligation to degrade gracefully to a fully static, fully legible state |
| Single-select filter model everywhere (no multi-select) | ↓ | Preserve for **evidence/report filtering** — one classification lens active at a time keeps the "what am I looking at" question always answerable in one glance, which matters more for an analytical tool than a marketing site |
| No character/line-split text animation anywhere | ↓ | Same restraint recommended: **YUKTI's typography motion should stay at the word/block level**, never cascade per-letter — per-letter animation reads as decorative, which undercuts an institutional/analytical tone |
| Vanilla-JS-first, GSAP-loaded-but-unused architecture | ↓ | Recommend the same posture for YUKTI: **native `IntersectionObserver` + `requestAnimationFrame` + CSS transitions first**; only reach for a heavier animation library if a specific effect (e.g. true scroll-pinned camera movement) genuinely requires it |

---

*End of specification. All source references (`app.js`, inline `<style>` block, DOM/accessibility tree) were captured live from https://www.elephant-skin.com/ on 2026-07-29.*
