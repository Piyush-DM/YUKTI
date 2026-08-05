/**
 * CONSTRUCTION UTILITIES
 *
 * Helpers for beat 3 of the plate template ("the structure assembles").
 *
 * Rule S3: a plate may hold at most one idea in motion at a time. These
 * utilities therefore build GROUPS in a single coordinated pass rather than
 * animating members independently — a staggered group is one idea in motion,
 * twelve independently-timed elements are twelve.
 */

import { interpolate } from "remotion";
import { EASE } from "../system/motion";
import { frames, type TierName } from "../system/timing";
import { BUDGET } from "../system/budgets";

/**
 * Per-member delay for a staggered build.
 *
 * The stagger is bounded so the whole group still completes inside one tier —
 * a build that runs long reads as decoration rather than construction.
 */
export const stagger = (
  index: number,
  count: number,
  tier: TierName = "build",
): number => {
  if (count <= 1) return 0;
  const window = frames(tier) * 0.5;
  return Math.round((index / (count - 1)) * window);
};

/**
 * Draw-on progress for a single member of a staggered group, 0..1.
 * Feed directly to `Edge.progress` or an opacity.
 */
export const buildProgress = ({
  frame,
  at,
  index,
  count,
  tier = "build",
}: {
  frame: number;
  at: number;
  index: number;
  count: number;
  tier?: TierName;
}): number => {
  const start = at + stagger(index, count, tier);
  return interpolate(frame, [start, start + frames(tier)], [0, 1], {
    easing: EASE.standard,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

/** Total frames a staggered group occupies, including its stagger tail. */
export const buildDuration = (count: number, tier: TierName = "build"): number =>
  frames(tier) + stagger(count - 1, count, tier);

/**
 * Rule H2: "Elements appear in reading order and never rearrange after
 * appearing. If the layout must change, it is a new plate."
 *
 * Re-layout destroys the mental model a viewer has just built, and it is the
 * most common failure in technical animation. This sorts a group into reading
 * order once so that build order and reading order cannot diverge.
 */
export const readingOrder = <T extends { x: number; y: number }>(
  items: readonly T[],
  rowTolerance = 24,
): T[] =>
  [...items].sort((a, b) =>
    Math.abs(a.y - b.y) > rowTolerance ? a.y - b.y : a.x - b.x,
  );

/**
 * Rule S3 / §8.3: at most one moving group per beat.
 * Call with the groups a plate animates in a single beat.
 */
export const assertSingleMovingGroup = (
  groupCount: number,
  plate: string,
): void => {
  if (groupCount > BUDGET.movingGroups) {
    throw new Error(
      `Rule S3 (visual language §5.3): plate "${plate}" animates ${groupCount} ` +
        `groups in one beat; the limit is ${BUDGET.movingGroups}. A plate may ` +
        `hold at most one idea in motion at a time.`,
    );
  }
};
