# Implementation Notes — CHOIR Explainer Film

Design problems revealed by implementation. **Raised, not solved.**

Per the engineering brief: *"If implementation reveals a design problem: STOP.
Do not solve it. Raise it as an implementation note. Never silently redesign
the film."*

Each note states what the approved spec says, what happened when it was
implemented faithfully, and what was done in the meantime. None of these has
been resolved in code.

---

## Note 1 — Total runtime is unapproved, and the film cannot render without one

**Status:** blocking for final render, not blocking for Phase 3.

**Spec.** Visual language §11.1 lists total runtime as an open item ("roughly
3:00–3:30. Confirm the target."). FILM_STRUCTURE.md deliberately expresses
movement lengths as proportions so they hold at any total.

**What implementation needs.** A composition requires `durationInFrames`. A
proportion cannot be rendered.

**What was done.** `PLACEHOLDER_TOTAL_SECONDS = 210` in `src/system/timing.ts`,
at the top of the stated range, marked as unapproved at the definition site.
`weightToFrames()` derives every movement length from the approved proportions,
so changing the one constant re-times the entire film correctly and requires no
other edit.

**Decision needed.** Confirm the total. Nothing else about the structure moves.

---

## Note 2 — The approved type scale is below projection legibility

**Status:** this is the one I would most want ruled on before Movement I.

**Spec.** Visual language §4.2 assigns the website type tokens to film roles.
Faithfully resolved at 1920×1080 those are:

| Role | Token | Resolved | Share of frame height |
|---|---|---|---|
| Question | `heading` | 44px | 4.07% |
| Explanatory line | `body` | 18px | **1.67%** |
| Structure label | `label` | 12.32px | **1.14%** |
| Data / slug | `data` | 13.44px | **1.24%** |

**What happened.** Render `out/harness-fonts.png` and look at the slug. It is
legible on a monitor at desk distance and marginal on a projected surface at
room distance. Common broadcast and conference guidance puts minimum on-screen
text at roughly 2–3% of frame height; three of the four registers above fall
below that, and the two carrying the most system-specific meaning — labels and
data — fall furthest.

**Why this is a design problem and not a bug.** The scale is not wrong. It was
designed for a browser viewport read at desk distance, where 18px body is
correct and 12.32px labels are conventional. The film is a different surface
with a different viewing distance, and §4.2 inherited the scale without that
being re-examined. This is exactly the class of thing §0's inheritance policy
was meant to catch, and it did not.

**Why I did not fix it.** Any fix is a design decision with knock-on effects:

- Scaling the whole type system up changes the film's density and the 54-character
  measure, which the two-line cap in §8.3 is derived from.
- Scaling only the small registers breaks the proportional relationship between
  tiers, which is what makes the three-register system read as one system.
- Re-resolving the clamps against a notional larger viewport would change the
  numbers without anyone deciding to.

All three are §4 amendments. None is mine to make.

**What was done.** Nothing. The tokens are implemented exactly as specified and
the arithmetic is shown in `src/system/tokens.ts` so the decision can be made
against real numbers.

---

## Note 3 — Söhne is unprocured, so no plate title can render as designed

**Status:** procurement, not design. Already flagged; now concrete.

**Spec.** Architecture D2 sets Söhne as the display face. Visual language §11.4
flags the licence as an open procurement dependency and warns against shipping
to a keynote on a fallback.

**What happened.** Inter and IBM Plex Mono are open-licensed (SIL OFL) and are
loaded in `src/system/fonts.ts`. Söhne is not loaded because the files do not
exist. `FONT.display` resolves through its documented fallback stack, so every
plate title in the film currently renders in a substitute face.

**What was done.** The token stack is correct and will upgrade silently the
moment licensed files land in the project. No workaround was introduced — in
particular I did not substitute a visually-similar free grotesque, because that
would make the gap invisible and it would ship.

**Decision needed.** Procure, or approve a different display face. The longer
this runs the more plates are reviewed and approved against type that will
change.

---

## Note 4 — Narration mode is unapproved and materially affects the text system

**Status:** blocking for Movement III onward; Movements I–II are unaffected.

**Spec.** Visual language §11.2 lists narration as open: voiceover, on-screen
text only, or both. It notes that an on-screen-text-only film "needs a third
text tier".

**What was done.** The foundation implements the two approved registers
(`Question`, `Line`) and the two-line cap from §8.3. It does not invent a third
tier.

**Why it matters soon.** Movements I and II carry almost no explanatory text.
From III onward the film explains structure, and if there is no voiceover, §4.2's
two-line cap becomes the binding constraint on what a plate can say.

---

## Note 5 — Rule C1's guard is only as good as the build windows plates declare

**Status:** implementation discipline for Phase 3. Not a design problem.

`assertNoCameraDuringBuild()` in `src/system/camera.ts` implements Rule C1
correctly, but it checks camera keyframes against build windows a plate
*declares*. `Plate`'s `buildWindows` prop defaults to `[]`, so a plate that
declares none passes trivially.

This is not fixable by making the prop required — most plates have no camera
move, and forcing empty declarations everywhere would be noise. Recorded here
so it is a known convention rather than a discovered gap: **any plate with a
camera move must declare its build windows.** Worth checking at each movement
approval.

---

## Not notes

Things that look like problems and are not:

- **The harness renders a verdict that is not asserted.** Deliberate. Rule F1
  reserves the first yellow-on-a-refusal for Movement VII, and the harness must
  not spend it.
- **`Lane` has no `connectTo` prop.** Deliberate. Movement IV's teaching is an
  absence; inter-lane connection is not something the primitive can express.
- **`Defeated` has no code path that unmounts its child.** Deliberate. Rule K1.
- **30fps rather than 60.** Every approved duration tier resolves to a whole
  number of frames at 30 and the film is slow reveals and long holds. Recorded
  in `README.md`, not a design decision.
