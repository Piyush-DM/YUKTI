# YUKTI — CHOIR Explainer Film v1.0

### Visual Language Specification, Prior to Implementation

**Status:** 🟡 **DRAFT — for approval.** No Remotion code is written until this is ratified.
**Subject:** A linear film introducing CHOIR as a computational primitive to an
engineering audience with no prior context.
**Objective:** comprehension. Not persuasion, not conversion, not brand.
**Governs:** the film surface only. Touches no research, no `choir/`, no
`choir_prototype/`, no `daale/`.
**Inherits from:** [`yukti-motion-system-v1.md`](yukti-motion-system-v1.md) (motion philosophy,
tokens, primitives) and [`website/src/styles/tokens.design.css`](website/src/styles/tokens.design.css)
(color, type, space). Values are referenced, never restated with different numbers.
**Content source:** [`CHOIR_v0.1_RESEARCH_FREEZE.md`](CHOIR_v0.1_RESEARCH_FREEZE.md). The theory is
immutable. This document specifies how it is shown, never what it is.

---

## 0. Inheritance and the One Declared Extension

The Motion System already answers most of what a film needs. Carried forward
without modification:

- **Deceleration only.** No bounce, elastic, or overshoot, anywhere, ever (§1.2).
- **Two tempos, not a spectrum.** The 400–500ms gap stays empty (§1.2, §2.1).
- **No character-level or line-level split-text animation** (§5, hard rule).
- **Motion never runs to fill time** (§1.3).
- **Morph the state, don't replace the instance** (§1.8).
- **The data is the visual**, not an illustration of the data (§6).
- **Text exclusion zones are enforced, not suggested** (§1.7).
- **Perceived weight scales with epistemic weight** (§1.5).
- **Continuity from repetition of a small vocabulary** (§1.6).
- **Reduced motion is structural, not merely faster** (§2, D8).

### The extension

Motion System §1.4 states: *"YUKTI does not simulate a 'virtual camera'
traveling through a 3D space — that metaphor implies spectacle, and spectacle is
the wrong register."*

That rule governs the **website**, where the user controls the viewport by
scrolling. A film has no user. Something must do the work that scroll would have
done, or the viewer cannot be directed to the region that matters.

This specification therefore declares a camera — and constrains it so that the
reason for §1.4 is honored rather than evaded:

> **The camera is a reading instrument, not a spectacle device.** It does only
> what a reader's eye and hand do at a drafting table: move to the region under
> discussion, hold still while it is read, and pull back to re-establish
> context. It has **no perspective, no vanishing point, no depth**. Everything is
> orthographic, always.

A camera that cannot rotate, dolly through, rack focus, or imply a third
dimension cannot produce spectacle. §7 makes this enforceable.

This is the only extension. Everything else inherits.

---

## 1. Visual Identity

### 1.1 The governing metaphor

**A drafting table under even light. Not a screen, not a world, not a space.**

The viewer is looking *down at a document*, never *into an environment*. Marks
are drawn, not rendered. Lines have weight, and weight means something. The film
should look like an engineering plate that happens to move — closer to a patent
drawing or a structural detail sheet than to any software product.

### 1.2 The category rule

> **Every mark on screen is exactly one of: a datum, a structure, or a label.
> There is no fourth category.**

This is the enforcement mechanism for "nothing exists because it looks cool." A
mark that is not carrying a value, not describing a relationship, and not naming
something has no category and is therefore a defect. Atmosphere is not a
category. Depth is not a category.

### 1.3 Surface

| Element | Treatment |
|---|---|
| Ground | `--yukti-color-graphite-900` flat. Never a gradient, never a vignette. |
| Drafting grid | `--yukti-color-line-blueprint` (6% bone). Static. Never animates, never parallaxes. |
| Grain | `--yukti-texture-grain` at low opacity, fixed to the frame, not to content. |
| Structure linework | `--yukti-color-border-hairline-dark`, 1px, at 1× scale. |
| Paper surfaces | `--yukti-color-bone-100`, `--yukti-radius-sm` (3px), 1px hairline border, **no blur shadow**. |
| Accent | `--yukti-color-yellow-500` only. |

### 1.4 Yellow discipline

Yellow is not a highlight color. It has one meaning and never another:

> **Yellow marks the assertion — the single thing the frame is currently
> claiming.** One assertion per frame. When the point is an absence, the absence
> is what turns yellow.

Yellow never appears as fill on large areas, never as a gradient, never as a
brand flourish, and never on two unrelated things simultaneously. §8.3 caps its
frame area.

### 1.5 Prohibited, absolutely

Glow. Bloom. Lens flare. Depth of field. Volumetric light. Drop shadows with
blur radius above zero. Gradients used decoratively. Particles of any kind.
Floating geometry. Rounded/pill radii. Perspective. Reflections. Any hue outside
the token palette. Anything that implies the viewer is inside a space rather
than above a document.

Also prohibited because they are the specific failure mode this film exists to
avoid: neural-network node-and-edge clouds, brains, robots, circuit-board
motifs, "scanning" sweeps, HUD framing, and any blue.

---

## 2. Motion Language

### 2.1 The two kinds of motion

Every animation in the film is one of exactly two things, and never both at once:

| | **Transport** | **Transformation** |
|---|---|---|
| What it does | A thing moves from A to B, unchanged | A thing changes state where it stands |
| What it teaches | **flow** — data moved | **derivation** — data became |
| Example | A claim entering a kernel lane | Confidence resolving from rules |
| Motion | Position only | Value, weight, opacity, or form only |

> **Rule M1.** A single element may never transport and transform in the same
> beat. If it must do both, that is two beats.

This is the film's most load-bearing motion rule. It is what lets a viewer
always know whether they are watching something *move* or something *become*.

### 2.2 Duration

Film tiers derive from the existing scale — they are multiples of published
tokens, not new inventions:

| Film tier | Value | Derivation | Use |
|---|---|---|---|
| `film-mark` | 200ms | `--yukti-duration-quick` | A single element appearing |
| `film-build` | 800ms | `--yukti-duration-reveal` | A structure assembling |
| `film-derive` | 1600ms | `--yukti-duration-cinematic` | A value being derived, a graph drawing |
| `film-hold-read` | 1200ms | — | Stillness after a structure completes |
| `film-hold-weight` | 2400ms | 2 × read | Stillness after the film's three key claims |
| `film-camera` | 800ms | `--yukti-duration-reveal` | Any camera state change |

**The 400–500ms gap remains empty.** Inherited, non-negotiable.

### 2.3 Duration carries meaning

Per Motion System §1.5, weight scales with epistemic weight. In the film this is
literal: **a conclusion resting on nine evidence items takes longer to resolve
than one resting on two.** Not for drama — so that the cost of establishing
something is felt rather than asserted.

### 2.4 Stillness

> **Rule M2.** Every completed structure holds still for at least
> `film-hold-read` before anything else happens.

Stillness is the primary anti-spectacle device and the primary comprehension
device. A viewer cannot parse a diagram that is still moving. Budget roughly
**one third of total runtime as stillness.** If the film feels too slow in
review, cut a scene — never shorten a hold.

### 2.5 Text motion

Type is read, not performed. Text has exactly two permitted entrances:

1. Opacity 0→1 over `film-mark`.
2. Opacity 0→1 with a rise of `--yukti-distance-md` (30px) over `film-build`.

No character split. No line split. No word cascade. No typewriter. No scale. No
tracking animation. Inherited from Motion System §5 and extended: in the film,
**typography motion never goes below the whole text block.**

### 2.6 Reduced-motion cut

A second render target, not a degraded one. Same runtime, same holds, same
narration timing. Transport is replaced by cross-fade in place; transformation
is replaced by a two-state cut. Camera is locked to `PLATE` throughout. This is a
real deliverable, per D8 and Motion System §2.

---

## 3. Cinematography Language

### 3.1 The plate

The frame is a **plate** — a numbered sheet in an engineering drawing set.

Every scene carries a persistent slug in the lower-left corner,
`--yukti-font-data`, `--yukti-type-label-size`, bone-300 at 35% opacity:

```
PLATE 04 / 12          INDEPENDENT KERNELS
```

The slug is the viewer's location indicator for the entire film. It never
animates beyond a cross-fade on plate change. It is the cheapest comprehension
device available and it reads as pure engineering register.

### 3.2 Orthography

**No vanishing point exists in this film.** All views are straight-on or
top-down. Elements do not shrink with distance, because there is no distance.
Scale changes are camera zoom, never perspective.

This single constraint is what makes the aesthetic unmistakably engineering
rather than product-marketing, and it makes the prohibited "AI look" structurally
impossible to produce.

### 3.3 Light

Even, sourceless, shadowless. There is no key light, no rim, no ambient
occlusion. The plate is lit like a document on a table under a drafting lamp —
which is to say, not lit at all, merely legible.

### 3.4 Composition

- 12-column grid inherited from `--yukti-grid-columns`.
- Content respects a safe margin of `--yukti-space-7` on all sides. Keynote
  projection is unforgiving; nothing important within 8% of any edge.
- **Left-aligned by default.** Centered composition is permitted only for the
  film's three key claims (§10) and the final plate.
- Text exclusion zones are computed and enforced, per Motion System §1.7. A
  structure that would collide with a label re-routes; it does not overlap.

---

## 4. Typography System

### 4.1 Register assignment — the rule that teaches

The three faces are not stylistic variety. Each one means something, the viewer
learns the mapping in the first plate, and it carries the whole film:

| Face | Token | Means | Used for |
|---|---|---|---|
| **Söhne** | `--yukti-font-display` | *This is a section of the argument* | Plate titles only. ~8 appearances total. |
| **Inter** | `--yukti-font-body` | *A human is explaining* | The question each plate answers; explanatory lines. |
| **IBM Plex Mono** | `--yukti-font-data` | **This is a literal value from the system** | Every identifier, value, band, rule name, verdict. |

> **Rule T1.** If a string appears in mono, it must be a string the system would
> actually emit. `SRC-DECK`, `coverage 5/5`, `moderate`, `R3`,
> `INSUFFICIENT_BASIS`, `support 7, opposition 1`. Never decorative mono.

This is the film's core information-hierarchy device disguised as typography. It
means the viewer can distinguish *what the system says* from *what we say about
it* at a glance, permanently, without being told.

### 4.2 Scale

| Role | Token | Notes |
|---|---|---|
| Plate title | `--yukti-type-mega-*` | Uppercase, left-aligned, word-stacked, line-height 0.92 |
| The question | `--yukti-type-heading-*` | Sentence case, one line, ends in `?` |
| Explanatory line | `--yukti-type-body-*` | **Max two lines on screen. Ever.** ~54 character measure |
| Structure label | `--yukti-type-label-*` | Uppercase, tracking 0.08em |
| Data | `--yukti-type-data-*` | `tabular-nums` **mandatory** |

### 4.3 Prohibited

Italics. Centered body copy. Text over structure without an exclusion zone.
Justified text. Any face outside the three. Numerals without `tabular-nums` —
non-tabular figures shift width as they count and read as decoration.

---

## 5. Scene Grammar

### 5.1 The unit

> **One plate = one question = one answer.**

### 5.2 The six-beat template

Every plate follows the same six beats. Predictability is a trust feature, per
Motion System §1.6 — a viewer who has understood one plate has understood how
all plates work.

| Beat | Name | Duration | What happens |
|---|---|---|---|
| 1 | **Slug** | `film-mark` | Plate number and title appear in the corner |
| 2 | **Question** | `film-build` | The question this plate answers, in Inter, printed on screen |
| 3 | **Construction** | `film-build`–`film-derive` | The structure assembles |
| 4 | **Hold** | `film-hold-read` | Complete stillness |
| 5 | **Assertion** | `film-mark` | Yellow marks the claim; the answer resolves |
| 6 | **Resolve** | `film-mark` | Assertion clears; structure persists or hands off |

### 5.3 Enforcement rules

> **Rule S1.** No plate exists that does not print its question on screen. If
> the question cannot be written in one line, the plate is doing more than one
> job and must be split.

This is the literal implementation of *every animation must answer a question*.
It is checkable in review: read the plate list, read only the questions, and see
whether they form a coherent argument. If they do, the film works.

> **Rule S2.** A plate may introduce **exactly one** new visual primitive. Two
> new primitives means two plates.

> **Rule S3.** A plate may hold at most **one** idea in motion at a time.

---

## 6. Transition Grammar

### 6.1 The three permitted transitions

| Name | What it does | When |
|---|---|---|
| **PERSIST** | Structure stays; annotation and question change | Default. Use for most plate changes. |
| **INHERIT** | One element of the outgoing plate survives and becomes the seed of the next structure | When the next idea is caused by the previous one |
| **CUT** | Hard cut, no bridge | Only when the next plate is deliberately unrelated — e.g. switching domain |

### 6.2 INHERIT is the workhorse

It is the transition that teaches. When the claim node leaving Plate 3 is
visibly *the same node* entering Plate 4, the viewer understands that data
**flows through** the system rather than being redrawn at each step. This is
object permanence used as pedagogy, and it is the direct film expression of
Motion System §1.8 — morph the state, don't replace the instance.

### 6.3 Prohibited transitions

Cross-dissolve between plates. Wipes. Slides. Pushes. Zoom-as-transition.
Whip pans. Morph cuts. Glitch. Light leaks. Anything with a named "effect."

> **Rule TR1.** No transition may introduce information. Transitions carry;
> plates teach. If something must be learned during a transition, it belongs in
> a plate.

---

## 7. Camera Grammar

### 7.1 Three states, not moves

The camera has states, not choreography:

| State | Scale | Purpose |
|---|---|---|
| **PLATE** | 1.0× | The whole structure in frame. Default. The film sits here most of the time. |
| **DETAIL** | ≤ 2.5× | Pushed to one region under discussion |
| **INDEX** | ≤ 0.6× | Pulled out to show relation *between* plates. Used at most twice in the film. |

### 7.2 Permitted transitions between states

Orthographic scale and axis-locked translation only, over `film-camera`, using
`--yukti-ease-standard`. Never `--yukti-ease-emphasis` — that curve is reserved,
per Motion System §7.

### 7.3 Hard rules

> **Rule C1.** The camera never moves while a structure is building. Build, then
> move — or move, then build. Never simultaneously.

Simultaneous camera and content motion is the single most reliable way to lose a
viewer. This rule is non-negotiable.

> **Rule C2.** One camera move per plate, maximum. Many plates have none.

> **Rule C3.** The camera returns to `PLATE` before any transition.

### 7.4 Forbidden

Rotation on any axis. Perspective. Dolly-through. Roll. Handheld or simulated
imperfection. Arcs. Parallax layers. Focus pulls. Motion blur. Easing that is
not `--yukti-ease-standard`.

---

## 8. Information Hierarchy

### 8.1 Four layers, fixed z-order

| Layer | Content | Treatment |
|---|---|---|
| 1 — **Ground** | Graphite, drafting grid, grain | Never changes for the entire film |
| 2 — **Structure** | Nodes, edges, lanes, containers | Bone hairlines |
| 3 — **Data** | Literal values and identifiers | Mono, sitting on structure |
| 4 — **Assertion** | The current claim | Yellow |

> **Rule H1.** Only one layer is in motion at any moment.

### 8.2 Reading order

There is no scroll, so the film must control reading order directly:

> **Rule H2.** Elements appear in reading order and **never rearrange after
> appearing.** If the layout must change, it is a new plate.

Re-layout destroys the mental model a viewer has just built. It is the most
common failure in technical animation and it is banned outright.

### 8.3 Budgets

| Budget | Limit | Why |
|---|---|---|
| Structure elements on screen | ≤ 12 | Beyond this a viewer parses shape, not content |
| Assertion (yellow) frame area | ≤ 5% | Scarcity is what preserves its meaning |
| Body text on screen | ≤ 2 lines | A viewer reading cannot watch |
| Simultaneous moving elements | ≤ 1 group | Rule S3 |

---

## 9. Color Philosophy

### 9.1 One hue, and no exceptions

D14 establishes yellow as the only accent hue in v1.0. The film honors this
literally, which creates a genuine design problem worth naming: CHOIR expresses
states that beg for red and green — agreement and disagreement, proceed and
decline, support and opposition.

**No second hue is introduced.** Red/green is the exact dashboard-SaaS register
this film exists to avoid, and it fails color-vision accessibility besides.

### 9.2 State is encoded in form and value, never hue

| State | Encoding |
|---|---|
| Present / absent | Solid stroke / hairline dashed stroke |
| Support / opposition | Filled / hollow, or above / below a stated axis |
| Confidence band | Value steps on bone: `bone-100` → `bone-300` → 35% opacity. Never hue. |
| Agreement between kernels | Two structures aligning to the same axis position |
| The current assertion | `--yukti-color-yellow-500` |
| Defeated / withdrawn | Retained at `--yukti-opacity-muted` (0.35) with a 1px strike rule |

### 9.3 The rule that encodes the theory

> **Rule K1. Nothing is ever deleted from the frame.** Defeated evidence,
> withdrawn claims, and rejected alternatives dim to `--yukti-opacity-muted` and
> **remain on screen for the rest of the plate.**

This is frozen commitment E12 — *nothing is deleted; defeated objects are marked
and retained* — rendered as a visual law rather than described in narration. The
viewer learns the property by watching it hold, repeatedly, without being told.

The same approach applies to E13: **what was not evaluated is drawn, in dashed
outline, rather than omitted.** An unevaluated thing is visibly not a false
thing.

Where the visual language can *be* the theory rather than illustrate it, it
should be.

---

## 10. Emotional Progression

The objective is comprehension, so the progression is a sequence of epistemic
states, not feelings. The register named for each movement is what should
accompany understanding — never replace it.

| # | Movement | Register | Viewer's state |
|---|---|---|---|
| 1 | **Recognition** | Sober | "I know this problem." Volume of documentation, shown as scale, not menace. |
| 2 | **Dissatisfaction** | Withheld | A single process: in, out. Clean and deliberately unsatisfying. The viewer should want to see inside the box. |
| 3 | **Structure** | Clarifying | Decomposition. The IR. The sealed lanes. The longest movement. |
| 4 | **Tension** | Alert, not alarmed | The kernels disagree, and the disagreement is legible. |
| 5 | **Restraint** | Composed | **The system declines to conclude.** |
| 6 | **Generality** | Expanding | One core; four domains; nothing in the core changed. |
| 7 | **Settle** | Still | The record. Nothing deleted. Rest on the plate. |

### 10.1 The peak is restraint, not capability

> Movement 5 is the emotional summit of the film.

This is the most important decision in this document. A product video peaks at
what the system *can do*. This film peaks at what it **refuses to do** — the
moment `INSUFFICIENT_BASIS` resolves and the pipeline stops rather than
producing an answer.

Played correctly, that beat lands as **relief**, not failure. It is the moment
an engineer in the audience understands that this is not another system that
always has an answer — and it is the single beat most likely to produce the
intended reaction:

> *"I have never seen institutional reasoning explained like this before."*

Movements 6 and 7 are the settle after that peak, not a second climax. The film
must not end on a capability claim.

### 10.2 Prohibited emotional moves

No triumph. No urgency. No countdown. No music swell at a capability reveal. No
"the future of" framing. No problem/solution melodrama in Movement 1 — the
volume of documents is a *fact*, not a threat.

---

## 11. Open Items for Approval

Deliberately unresolved. These are direction decisions, not design decisions.

1. **Runtime.** Structure above supports roughly 3:00–3:30. Confirm the target.
2. **Narration.** Voiceover, on-screen text only, or both. This changes §4.2's
   two-line cap materially — an on-screen-text-only film needs a third text tier.
3. **Sound.** Whether the film has any. A silent film with printed questions is
   defensible and unusual; if there is sound, it should be mechanical and
   diegetic to the drafting metaphor, never scored.
4. **Söhne licensing.** Unresolved procurement dependency, per architecture D2.
   The fallback stack is specified and correct; the film should not ship to a
   keynote on a fallback face. Flagging early so it is not discovered late.
5. **Worked example.** The film should carry one real packet end to end. The
   prototype's `orbital-series-b` (kernels genuinely disagree, resolves to
   `PROCEED_WITH_CONDITIONS`) and `northwind-seed` (resolves to
   `INSUFFICIENT_BASIS`) together supply both the tension of Movement 4 and the
   restraint of Movement 5. Confirm before the plate list is written.

---

## 12. The Standing Test

Every element added to this film must pass:

> **Does this improve understanding?**

If the answer is no, it is removed. Not reduced, not made subtler — removed.

Per architecture D10, every animation must answer one of: **What entered? What
changed? What became connected?** An animation answering none of the three is a
defect, not a flourish.
