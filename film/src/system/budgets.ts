/**
 * BUDGETS — visual language §8.3
 *
 * "Beyond this a viewer parses shape, not content." These are the approved
 * limits, expressed as checkable functions rather than prose so a plate that
 * exceeds one fails during development instead of during review.
 */

import { CANVAS } from "./tokens";

export const BUDGET = {
  /** Structure elements simultaneously on screen. */
  structureElements: 12,
  /** Assertion (yellow) share of frame area. Scarcity preserves its meaning. */
  assertionAreaFraction: 0.05,
  /** Body text lines on screen. "A viewer reading cannot watch." */
  bodyTextLines: 2,
  /** Simultaneous moving groups (Rule S3: one idea in motion per beat). */
  movingGroups: 1,
} as const;

/**
 * Approved measure for body copy, visual language §4.2. Used to derive the
 * two-line cap, since rendered line count is not available at author time.
 */
export const BODY_MEASURE_CHARS = 54;
export const BODY_MAX_CHARS = BODY_MEASURE_CHARS * BUDGET.bodyTextLines;

export class BudgetError extends Error {
  constructor(budget: string, detail: string) {
    super(`Budget exceeded — ${budget} (visual language §8.3): ${detail}`);
    this.name = "BudgetError";
  }
}

export const assertStructureBudget = (count: number, plate: string): void => {
  if (count > BUDGET.structureElements) {
    throw new BudgetError(
      "structure elements",
      `plate "${plate}" renders ${count} structure elements; the limit is ` +
        `${BUDGET.structureElements}. Beyond this a viewer parses shape, not ` +
        `content. Split the plate.`,
    );
  }
};

export const assertBodyTextBudget = (text: string, plate: string): void => {
  if (text.length > BODY_MAX_CHARS) {
    throw new BudgetError(
      "body text",
      `plate "${plate}" body copy is ${text.length} characters; the cap is ` +
        `${BODY_MAX_CHARS} (${BUDGET.bodyTextLines} lines at a ` +
        `${BODY_MEASURE_CHARS}-character measure).`,
    );
  }
};

/**
 * Assertion area. Yellow is capped at 5% of the frame because its meaning —
 * "the single thing being claimed right now" — survives only while it is rare.
 */
export const assertAssertionBudget = (
  areaPx: number,
  plate: string,
): void => {
  const frameArea = CANVAS.width * CANVAS.height;
  const fraction = areaPx / frameArea;
  if (fraction > BUDGET.assertionAreaFraction) {
    throw new BudgetError(
      "assertion area",
      `plate "${plate}" marks ${(fraction * 100).toFixed(1)}% of the frame in ` +
        `yellow; the cap is ${BUDGET.assertionAreaFraction * 100}%.`,
    );
  }
};
