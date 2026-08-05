# CHOIR Explainer Film — Remotion Implementation

Implements [`yukti-choir-film-v1-visual-language.md`](../yukti-choir-film-v1-visual-language.md)
and [`FILM_STRUCTURE.md`](../FILM_STRUCTURE.md). Both are approved. Neither is
reinterpreted here.

**Every line of code implements an already-approved decision.** Where
implementation revealed a design problem it was raised in
[`IMPLEMENTATION_NOTES.md`](IMPLEMENTATION_NOTES.md), not solved.

```bash
npm install --prefix film
npm run studio --prefix film
```

## Status

All nine movements implemented. Master composition renders the complete film.

Phase 3 builds movements one at a time, in order, each after approval. The
`implemented` flag in `src/registry/movements.ts` is the record of how far the
film has been built; `Root.tsx` registers only what that flag turns on.

| | |
|---|---|
| Movements implemented | 9 / 9 |
| Compositions registered | `Master`, `M01`-`M09`, `SystemHarness` |

## Layout

```
src/
├── system/          values and rules — no rendering
│   ├── tokens.ts      transcribed from the website token layer; clamps resolved
│   ├── timing.ts      duration tiers; the 400-500ms gap is unreachable
│   ├── motion.ts      transport vs transformation; Rule M1 enforcement
│   ├── camera.ts      the reading instrument; Rules C1-C3
│   ├── layout.ts      grid, safe area, VERDICT_LOCUS
│   ├── budgets.ts     §8.3 limits as checkable functions
│   └── fonts.ts       Inter + IBM Plex Mono loaded; Söhne unprocured
├── primitives/      rendering
│   ├── Ground.tsx     layer 1; inert by specification
│   ├── Typography.tsx three registers, not interchangeable
│   ├── Diagram.tsx    state in form and value, never hue
│   ├── Verdict.tsx    the fixed locus — the memorable frame depends on it
│   ├── Plate.tsx      the six-beat template
│   ├── Transition.tsx PERSIST / INHERIT / CUT
│   └── Construct.tsx  build utilities
├── registry/
│   └── movements.ts   FILM_STRUCTURE.md as data; seams derived, not stored
├── harness/
│   └── SystemHarness.tsx  verification surface; never appears in the film
└── Root.tsx
```

## Rules that are enforced in code, not just documented

The project's habit is mechanical verification rather than assertion
(`--frozen`, `--audit`, `--replay`). The film follows it where it can.

| Approved rule | Where it is enforced |
|---|---|
| No duration in the 400–500ms band | `frames()` takes a tier name; `framesFromMs()` throws |
| Rule M1 — never transport and transform in one beat | `composeMotion()` throws on the mixed case |
| Rule S1 — every plate prints its question | `Question` throws if the string does not end in `?` |
| Rule C1/C2/C3 — camera discipline | `assertCameraRules()` at plate render |
| Rule K1 — nothing is deleted from the frame | `Defeated` dims; it has no unmount path |
| Rule T1 — mono means real system output | `Datum` requires a `source` |
| §8.3 budgets | `assertStructureBudget`, `assertBodyTextBudget`, `assertAssertionBudget` |
| Verbatim seams between movements | `startStateOf()` derives from the predecessor |
| Weights sum to 1 | Checked at registry module load |
| `--yukti-ease-emphasis` is reserved | Not exported; `emphasisIsReserved()` throws with the reason |

## Frame rate

30fps. Every approved duration tier resolves to a whole number of frames at 30
(200ms → 6, 800ms → 24, 1600ms → 48, 1200ms → 36, 2400ms → 72), and the film is
slow reveals and long holds rather than fast motion. This is a render setting,
not a design decision.

## Verification

```bash
npm run typecheck --prefix film
npx remotion still SystemHarness out/harness.png --frame=120 --config=film/remotion.config.ts
```

The harness is the film's equivalent of the website's `tokens.html` — a surface
that exercises the foundation so it can be checked before anything is built on
it. It renders no narrative content and makes no design decision.
