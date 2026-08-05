/**
 * TRANSITION PRIMITIVES — visual language §6
 *
 * Three transitions exist. Everything else is forbidden by name:
 * cross-dissolve, wipe, slide, push, zoom-as-transition, whip pan, morph cut,
 * glitch, light leak, "anything with a named effect".
 *
 * FILM_STRUCTURE.md's structural claim is stronger than a transition list:
 *
 *   "The End State of every movement is the Start State of the next, verbatim.
 *    There is no cut between movements, no re-establishment, no scene that
 *    begins somewhere new. The film is one continuous state, advanced nine
 *    times."
 *
 * So PERSIST is not merely the default — it is what the seam between movements
 * IS. This module models the three kinds and enforces Rule TR1.
 */

export type TransitionKind =
  /** Structure stays; annotation and question change. The seam's default. */
  | "PERSIST"
  /** One element survives and seeds the next structure. Teaches causation. */
  | "INHERIT"
  /** Hard cut. Only when the next plate is deliberately unrelated. */
  | "CUT";

export interface TransitionSpec {
  readonly kind: TransitionKind;
  /**
   * For INHERIT: the id of the single element carried across.
   * Object permanence used as pedagogy — the node leaving one plate is
   * visibly the same node entering the next.
   */
  readonly carries?: string;
  /**
   * Rule TR1: "No transition may introduce information. Transitions carry;
   * plates teach." Stating what the transition carries makes an accidental
   * violation visible in review.
   */
  readonly introduces?: never;
}

export class TransitionRuleError extends Error {
  constructor(detail: string) {
    super(`Rule TR1 (visual language §6.3): ${detail}`);
    this.name = "TransitionRuleError";
  }
}

/**
 * INHERIT must name exactly one carried element. Carrying several is a
 * re-establishment, which is the thing the verbatim-seam rule exists to
 * prevent.
 */
export const assertTransition = (
  spec: TransitionSpec,
  seam: string,
): void => {
  if (spec.kind === "INHERIT" && !spec.carries) {
    throw new TransitionRuleError(
      `seam "${seam}" declares INHERIT but names no carried element. An ` +
        `INHERIT that carries nothing is a CUT.`,
    );
  }
  if (spec.kind !== "INHERIT" && spec.carries) {
    throw new TransitionRuleError(
      `seam "${seam}" declares ${spec.kind} but names a carried element. Only ` +
        `INHERIT carries.`,
    );
  }
};

/**
 * A seam is valid only if the outgoing End State text and the incoming Start
 * State text are identical. FILM_STRUCTURE.md holds these as verbatim copies;
 * this checks the invariant mechanically rather than trusting the copy-paste.
 */
export const assertVerbatimSeam = (
  endState: string,
  startState: string,
  seam: string,
): void => {
  const normalise = (s: string) => s.replace(/\s+/g, " ").trim();
  if (normalise(endState) !== normalise(startState)) {
    throw new TransitionRuleError(
      `seam "${seam}" is not verbatim. The End State of a movement must be the ` +
        `Start State of the next, word for word. Divergence here means the film ` +
        `re-establishes instead of continuing.`,
    );
  }
};
