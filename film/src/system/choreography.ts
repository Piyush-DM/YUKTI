/**
 * CHOREOGRAPHY
 *
 * The path is the argument.
 *
 * `motion.ts` supplies two verbs — TRANSPORT (a thing moves, unchanged) and
 * TRANSFORMATION (a thing changes state where it stands). This module supplies
 * the film's actual vocabulary, built from transport, because in this film the
 * information lives in the travel and not in the appearance.
 *
 * A fade answers "what entered" and nothing else. Architecture D10 requires
 * every animation to answer one of *what entered, what changed, what became
 * connected*. Each verb below is named for the question it answers.
 *
 * RULE M1 COMPLIANCE
 * Every verb here is pure transport: elements exist at full opacity for the
 * whole beat and change position only. Nothing fades. Where an element must be
 * absent before its beat, it is placed OFF-PLATE and travels in — arrival is a
 * journey, not a materialisation.
 */

import { interpolate } from "remotion";
import { CANVAS } from "./tokens";
import { EASE } from "./motion";
import { frames, type TierName } from "./timing";

export interface Phrase {
  readonly frame: number;
  readonly at: number;
  readonly tier?: TierName;
}

const eased = ({ frame, at, tier = "build" }: Phrase): number =>
  interpolate(frame, [at, at + frames(tier)], [0, 1], {
    easing: EASE.standard,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/** Per-member offset for a group that moves as one idea (Rule S3). */
export const cascadeDelay = (
  index: number,
  count: number,
  tier: TierName = "build",
): number => (count <= 1 ? 0 : Math.round((index / (count - 1)) * frames(tier) * 0.45));

// ============================================================
// ARRIVE — "what entered"
//
// The element travels from off-plate to its resting position. It is never
// faded in: it was always there, it simply had not got here yet.
// ============================================================

export type Edge = "top" | "bottom" | "left" | "right";

const offPlateOffset = (edge: Edge, restY: number, restX: number) => {
  switch (edge) {
    case "top":
      return { dx: 0, dy: -(restY + CANVAS.height * 0.15) };
    case "bottom":
      return { dx: 0, dy: CANVAS.height - restY + CANVAS.height * 0.15 };
    case "left":
      return { dx: -(restX + CANVAS.width * 0.12), dy: 0 };
    case "right":
      return { dx: CANVAS.width - restX + CANVAS.width * 0.12, dy: 0 };
  }
};

export interface ArriveSpec extends Phrase {
  readonly from: Edge;
  readonly restX: number;
  readonly restY: number;
  readonly index?: number;
  readonly count?: number;
}

/** Returns the CURRENT offset from rest. Add to the element's resting x/y. */
export const arrive = (spec: ArriveSpec): { dx: number; dy: number } => {
  const { from, restX, restY, index = 0, count = 1, tier = "build" } = spec;
  const start = spec.at + cascadeDelay(index, count, tier);
  const t = eased({ frame: spec.frame, at: start, tier });
  const off = offPlateOffset(from, restY, restX);
  return {
    dx: interpolate(t, [0, 1], [off.dx, 0]),
    dy: interpolate(t, [0, 1], [off.dy, 0]),
  };
};

// ============================================================
// DESCEND — "what became connected"
//
// One object travels from a source into a destination. Used where the same
// input must be seen ENTERING several sealed destinations: four descents of
// the same object is the independence claim made visible.
// ============================================================

export interface DescendSpec extends Phrase {
  readonly fromY: number;
  readonly toY: number;
  readonly fromX?: number;
  readonly toX?: number;
  readonly index?: number;
  readonly count?: number;
}

export const descend = (
  spec: DescendSpec,
): { x: number; y: number; travelled: number } => {
  const { fromY, toY, fromX = 0, toX = 0, index = 0, count = 1, tier = "build" } = spec;
  const start = spec.at + cascadeDelay(index, count, tier);
  const t = eased({ frame: spec.frame, at: start, tier });
  return {
    x: interpolate(t, [0, 1], [fromX, toX]),
    y: interpolate(t, [0, 1], [fromY, toY]),
    travelled: t,
  };
};

// ============================================================
// TRAVERSE — "what changed"
//
// A read-head runs down a list and HALTS at a row. The distance travelled is
// the information: how far evaluation got before it stopped.
//
// Returns the head's position in rows (fractional while moving) and which rows
// have been reached. Rows beyond the halt are never reached — that is the
// point, and it must be watched happening rather than presented as done.
// ============================================================

export interface TraverseSpec extends Phrase {
  readonly rows: number;
  /** Zero-based row at which evaluation stops. */
  readonly haltAt: number;
  readonly rowHeight: number;
}

export interface TraverseState {
  /** Head offset in pixels from the first row's top. */
  readonly headY: number;
  /** Fractional row index the head currently occupies. */
  readonly headRow: number;
  /** True once the head has arrived at the halting row and stopped. */
  readonly halted: boolean;
  /** Rows the head has reached so far. */
  reached(row: number): boolean;
}

export const traverse = (spec: TraverseSpec): TraverseState => {
  const { rows, haltAt, rowHeight, tier = "derive" } = spec;
  // The head moves at a constant rate per row so that "it stopped early" is
  // legible as a shorter journey, not merely a different end state.
  const perRow = frames(tier) / Math.max(1, rows - 1);
  const travelFrames = perRow * haltAt;
  const t = interpolate(
    spec.frame,
    [spec.at, spec.at + Math.max(1, travelFrames)],
    [0, 1],
    { easing: EASE.linear, extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const headRow = t * haltAt;
  return {
    headY: headRow * rowHeight,
    headRow,
    halted: t >= 1,
    reached: (row: number) => headRow >= row - 0.001,
  };
};

// ============================================================
// DELIVER — "what became connected"
//
// Travel along the film's one established route into the verdict locus. Every
// conclusion takes this path, so the eye learns the route across the film and
// the substitution in Movement VII reads as an arrival that differs, not as a
// different graphic.
// ============================================================

export interface DeliverSpec extends Phrase {
  readonly fromX: number;
  readonly fromY: number;
  readonly toX: number;
  readonly toY: number;
}

export const deliver = (
  spec: DeliverSpec,
): { x: number; y: number; arrived: boolean } => {
  const t = eased({ ...spec, tier: spec.tier ?? "build" });
  return {
    x: interpolate(t, [0, 1], [spec.fromX, spec.toX]),
    y: interpolate(t, [0, 1], [spec.fromY, spec.toY]),
    arrived: t >= 1,
  };
};

// ============================================================
// SETTLE — "what changed"
//
// Values fall and come to rest on a floor set by the LOWEST of them. The
// minimum is the survivor of a descent, not a separately-drawn fact.
// ============================================================

export interface SettleSpec extends Phrase {
  /** Rest heights, one per column. Larger is stronger. */
  readonly heights: readonly number[];
  readonly index: number;
}

export const settle = (spec: SettleSpec): { height: number; isFloor: boolean } => {
  const { heights, index, tier = "derive" } = spec;
  const rest = heights[index] ?? 0;
  const floor = Math.min(...heights);
  const t = eased({ frame: spec.frame, at: spec.at, tier });
  return {
    height: interpolate(t, [0, 1], [0, rest]),
    isFloor: rest === floor,
  };
};

/** The institutional floor, revealed by descent rather than asserted. */
export const settleFloor = (
  heights: readonly number[],
  spec: Phrase,
): number => {
  const t = eased({ ...spec, tier: spec.tier ?? "derive" });
  return interpolate(t, [0, 1], [0, Math.min(...heights)]);
};
