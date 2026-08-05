/**
 * SCENE REGISTRY
 *
 * The approved contents of FILM_STRUCTURE.md, as data.
 *
 * THE VERBATIM SEAM
 * FILM_STRUCTURE.md's structural claim is that the End State of every movement
 * is the Start State of the next, word for word. Storing both would let them
 * drift. Each movement therefore stores only its `endState`, and `startState`
 * is DERIVED from its predecessor — so the invariant holds by construction and
 * cannot be violated by an edit.
 *
 * IMPLEMENTATION STATUS
 * Every movement is registered with `implemented: false`. Phase 3 turns them on
 * one at a time, in order, each after approval. The registry is the record of
 * how far the film has been built.
 */

import type { TransitionKind } from "../primitives/Transition";

export interface Movement {
  readonly numeral: string;
  readonly index: number;
  readonly name: string;
  /** Rule S1: printed on screen. Must end in "?". */
  readonly question: string;
  /** One emotional word. FILM_STRUCTURE.md. */
  readonly word: string;
  /** Proportional weight. Sums to 1 across the film. */
  readonly weight: number;
  /** Transition INTO this movement from its predecessor. */
  readonly transitionIn: TransitionKind;
  /** The frame this movement ends on. Becomes the next movement's start. */
  readonly endState: string;
  /** Flipped to true in Phase 3, one movement at a time, after approval. */
  readonly implemented: boolean;
}

/** Movement I opens on an empty plate; it has no predecessor to inherit from. */
export const INITIAL_STATE =
  "Empty plate. Graphite ground, drafting grid at 6%. No structure, no data, " +
  "no label. Slug only.";

export const MOVEMENTS: readonly Movement[] = [
  {
    numeral: "I",
    index: 1,
    name: "Volume",
    question: "What does an institution decide from?",
    word: "Weight",
    weight: 0.08,
    transitionIn: "CUT",
    endState:
      "The plate is filled edge to edge with source material rendered as " +
      "structure — several hundred hairline rectangles, tiled, each one a " +
      "document. No content is legible. Quantity is legible. The count sits in " +
      "mono at the lower right. Nothing moves.",
    implemented: true,
  },
  {
    numeral: "II",
    index: 2,
    name: "Opacity",
    question: "What happens when one process reads all of it?",
    word: "Doubt",
    weight: 0.08,
    transitionIn: "PERSIST",
    endState:
      "All source material has collapsed into a single solid rectangle at plate " +
      "centre. One line leaves it. At the end of that line, at the coordinates " +
      "this film will use for every verdict from here on, is a conclusion set in " +
      "mono. The conclusion is marked in yellow. Behind it there is nothing — no " +
      "evidence, no citation, no structure. The rectangle has no interior. The " +
      "plate holds.",
    implemented: true,
  },
  {
    numeral: "III",
    index: 3,
    name: "Structure",
    question: "What if the material had a common form?",
    word: "Order",
    weight: 0.13,
    transitionIn: "INHERIT",
    endState:
      "The solid rectangle has opened. In its place is a structured graph: " +
      "entities, claims, evidence items and the relationships between them, each " +
      "kind visually distinct, each carrying a mono identifier. Evidence items " +
      "connect to the claims they support. No conclusion is present anywhere on " +
      "the plate. The structure is complete and still.",
    implemented: true,
  },
  {
    numeral: "IV",
    index: 4,
    name: "Isolation",
    question: "What if no reader could see the others?",
    word: "Separation",
    weight: 0.15,
    transitionIn: "INHERIT",
    endState:
      "Four sealed lanes run the height of the plate. The structured graph has " +
      "entered each lane in full. Each lane has produced a structured artifact " +
      "carrying findings and the evidence identifiers behind them. No line " +
      "connects any lane to any other. Two lanes have independently arrived at " +
      "the same position on a shared axis; that coincidence is marked in yellow. " +
      "The lanes remain sealed.",
    implemented: true,
  },
  {
    numeral: "V",
    index: 5,
    name: "Derivation",
    question: "Where does confidence come from?",
    word: "Honesty",
    weight: 0.13,
    transitionIn: "PERSIST",
    endState:
      "Each artifact now carries a derived confidence band, expressed as a value " +
      "step on bone rather than a hue. Beside one artifact the derivation is " +
      "printed in full — numbered rules, in mono, each showing its input and its " +
      "effect, terminating in a band and a named limiting factor. Below the four " +
      "bands, the institutional band has resolved to the lowest of them, not " +
      "their average. The limiting factor is marked in yellow.",
    implemented: true,
  },
  {
    numeral: "VI",
    index: 6,
    name: "Contradiction",
    question: "What happens when they do not agree?",
    word: "Friction",
    weight: 0.11,
    transitionIn: "PERSIST",
    endState:
      "Findings are grouped by topic. On one topic the four lanes have split: " +
      "positions sit on opposite sides of a stated axis, both well supported, " +
      "neither withdrawn. The tally is printed in mono with its running totals " +
      "visible. The decision rules are listed in order, each showing whether it " +
      "fired and what it observed; the rule that fired is marked in yellow, and " +
      "the rules that did not fire remain on the plate at reduced opacity. The " +
      "verdict reads CONTESTED.",
    implemented: true,
  },
  {
    numeral: "VII",
    index: 7,
    name: "Restraint",
    question: "What happens when there is not enough?",
    word: "Relief",
    weight: 0.13,
    transitionIn: "PERSIST",
    endState:
      "The same four lanes, in the same positions, the apparatus visibly " +
      "unchanged from the previous movement. The packet is thinner. Most claims " +
      "stand in dashed outline — reached, not established. Two lanes have " +
      "concluded nothing and say so. The first decision rule fires immediately; " +
      "the remaining five are never evaluated and stand greyed and unreached. At " +
      "the verdict locus — the coordinates every conclusion in this film has " +
      "occupied — the mono string INSUFFICIENT_BASIS, marked in yellow. The " +
      "unevaluated material stays on the plate, dashed, at reduced opacity. " +
      "Nothing further is produced. The plate holds longer than any other in the " +
      "film.",
    implemented: true,
  },
  {
    numeral: "VIII",
    index: 8,
    name: "Generality",
    question: "Does any of this depend on the subject?",
    word: "Recognition",
    weight: 0.11,
    transitionIn: "PERSIST",
    endState:
      "The camera has pulled to INDEX. Four packets of visibly different shape " +
      "sit side by side, from four unrelated fields. Each has run the same core; " +
      "the core is drawn once, in the centre, unduplicated. The lines from every " +
      "packet enter the same structure. A count of changes made to that core is " +
      "printed in mono, and it reads zero. One of the four packets is labelled as " +
      "the hold-out.",
    implemented: true,
  },
  {
    numeral: "IX",
    index: 9,
    name: "Record",
    question: "What remains?",
    word: "Permanence",
    weight: 0.08,
    transitionIn: "PERSIST",
    endState:
      "A single completed record on one plate: the structure, the evidence, the " +
      "artifacts, the derivation, the fired and unfired rules, the defeated " +
      "positions at reduced opacity, the unevaluated material in dashed outline, " +
      "and the verdict. Nothing has been removed. The record digest is printed " +
      "once, in mono. The plate is still. There is no yellow anywhere on the " +
      "frame.",
    implemented: true,
  },
];

/**
 * The Start State of a movement IS the End State of its predecessor.
 * Derived, never stored — the seam cannot drift.
 */
export const startStateOf = (index: number): string => {
  if (index <= 1) return INITIAL_STATE;
  const previous = MOVEMENTS[index - 2];
  if (!previous) {
    throw new RangeError(`No movement precedes index ${index}.`);
  }
  return previous.endState;
};

export const movementByIndex = (index: number): Movement => {
  const m = MOVEMENTS[index - 1];
  if (!m) throw new RangeError(`No movement at index ${index}.`);
  return m;
};

/** Weights must sum to 1. Checked at module load. */
const weightSum = MOVEMENTS.reduce((acc, m) => acc + m.weight, 0);
if (Math.abs(weightSum - 1) > 1e-9) {
  throw new Error(
    `Movement weights sum to ${weightSum}, not 1. FILM_STRUCTURE.md's ` +
      `proportional allocation is approved; correct the registry, not the film.`,
  );
}

export const implementedMovements = (): readonly Movement[] =>
  MOVEMENTS.filter((m) => m.implemented);
