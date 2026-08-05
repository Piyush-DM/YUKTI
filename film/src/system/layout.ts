/**
 * LAYOUT — grid, safe area, and the fixed loci the film depends on.
 *
 * Visual language §3.4 (composition) and §8 (information hierarchy).
 */

import { CANVAS, GRID, SPACE } from "./tokens";

// ============================================================
// Safe area — visual language §3.4
//
// "Keynote projection is unforgiving; nothing important within 8% of any edge."
// SPACE.s7 (128px) exceeds 8% of height (86px) and is close to 8% of width
// (154px), so the larger of the two is used per axis.
// ============================================================

const EIGHT_PERCENT_X = Math.round(CANVAS.width * 0.08);
const EIGHT_PERCENT_Y = Math.round(CANVAS.height * 0.08);

export const SAFE = {
  left: Math.max(SPACE.s7, EIGHT_PERCENT_X),
  right: Math.max(SPACE.s7, EIGHT_PERCENT_X),
  top: Math.max(SPACE.s7, EIGHT_PERCENT_Y),
  bottom: Math.max(SPACE.s7, EIGHT_PERCENT_Y),
} as const;

export const SAFE_BOX = {
  x: SAFE.left,
  y: SAFE.top,
  width: CANVAS.width - SAFE.left - SAFE.right,
  height: CANVAS.height - SAFE.top - SAFE.bottom,
} as const;

// ============================================================
// 12-column grid — inherited from GRID.columns
// ============================================================

const COLUMN_WIDTH =
  (SAFE_BOX.width - GRID.gutter * (GRID.columns - 1)) / GRID.columns;

/** Left edge of column `n` (1-indexed), in absolute canvas pixels. */
export const col = (n: number): number => {
  if (n < 1 || n > GRID.columns) {
    throw new RangeError(`Column ${n} is outside the ${GRID.columns}-column grid.`);
  }
  return SAFE_BOX.x + (n - 1) * (COLUMN_WIDTH + GRID.gutter);
};

/** Width spanning `n` columns including the gutters between them. */
export const span = (n: number): number => {
  if (n < 1 || n > GRID.columns) {
    throw new RangeError(`Span ${n} is outside the ${GRID.columns}-column grid.`);
  }
  return n * COLUMN_WIDTH + (n - 1) * GRID.gutter;
};

// ============================================================
// THE VERDICT LOCUS
//
// FILM_STRUCTURE.md, "The frame":
//
//   "A fixed verdict locus, identical coordinates every time — installed in
//    Movement II, held by every plate after. Consequence if missed: the
//    substitution is invisible; the frame is just a word."
//
// Every conclusion the film renders — the unattributed answer in Movement II,
// CONTESTED in VI, INSUFFICIENT_BASIS in VII — is placed HERE and nowhere
// else. The memorable frame is a substitution at these coordinates, and it
// only reads if the position never moves.
//
// This constant is load-bearing. Do not parameterise it, do not offset it
// per-movement, and do not centre a verdict "because it looks better on this
// plate". If a plate cannot place its verdict here, that is an implementation
// note, not a local fix.
// ============================================================

export const VERDICT_LOCUS = {
  /** Left-aligned to column 1, consistent with §3.4's left-aligned default. */
  x: col(1),
  /**
   * Vertically at 72% of frame height: below the working area where structure
   * is built, above the slug line. Fixed for the entire film.
   */
  y: Math.round(CANVAS.height * 0.72),
  /** Verdicts are mono strings; this bounds the longest (INSUFFICIENT_BASIS). */
  maxWidth: span(6),
} as const;

// ============================================================
// Plate furniture
// ============================================================

/** Slug: lower-left corner. Visual language §3.1. */
export const SLUG_ORIGIN = {
  x: SAFE.left,
  y: CANVAS.height - SAFE.bottom,
} as const;

/** The question: upper-left, above the working area. Visual language §5.2. */
export const QUESTION_ORIGIN = {
  x: col(1),
  y: SAFE.top,
  maxWidth: span(8),
} as const;

/** The working area: where structure is constructed. Between question and verdict. */
export const WORKING_AREA = {
  x: SAFE_BOX.x,
  y: SAFE.top + 140,
  width: SAFE_BOX.width,
  height: VERDICT_LOCUS.y - (SAFE.top + 140) - SPACE.s5,
} as const;
