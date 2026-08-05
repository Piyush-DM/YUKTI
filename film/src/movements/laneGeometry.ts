/**
 * Lane geometry shared by Movements IV–VII.
 *
 * The apparatus must be recognisable as unchanged across these movements —
 * FILM_STRUCTURE.md requires VII to reuse VI's structure with nothing altered,
 * or the refusal reads as breakage. One geometry module guarantees it.
 */

import { SPACE } from "../system/tokens";
import { WORKING_AREA, span } from "../system/layout";
import { KERNELS } from "../content/packet";

export const GRAPH_HEIGHT = 96;
export const LANE_TOP = WORKING_AREA.y + GRAPH_HEIGHT + SPACE.s5;
export const LANE_HEIGHT = 250;
export const LANE_GAP = SPACE.s5;

export const LANE_WIDTH =
  (WORKING_AREA.width - LANE_GAP * (KERNELS.length - 1)) / KERNELS.length;

export const laneX = (i: number): number =>
  WORKING_AREA.x + i * (LANE_WIDTH + LANE_GAP);

export const laneCentreX = (i: number): number => laneX(i) + LANE_WIDTH / 2;

export const ARTIFACT = {
  inset: SPACE.s4,
  top: LANE_TOP + SPACE.s5,
  height: 110,
  width: LANE_WIDTH - SPACE.s4 * 2,
} as const;

export const BAND = {
  top: ARTIFACT.top + ARTIFACT.height + SPACE.s4,
  width: ARTIFACT.width,
} as const;

export const AXIS = {
  x: WORKING_AREA.x,
  y: LANE_TOP + LANE_HEIGHT + SPACE.s6,
  width: span(10),
} as const;

/**
 * Stance on the shared axis, as a fraction of axis width.
 * Lanes 0 and 1 land on the same position without either observing the other.
 */
export const STANCE: readonly number[] = [0.34, 0.34, 0.72, 0.55];

/** Movement VI: the split. Lanes 0 and 2 take opposite sides of the axis. */
export const SPLIT_STANCE: readonly number[] = [0.22, 0.34, 0.82, 0.55];

// ============================================================
// Compact layout — Movements VI and VII
//
// The cascade needs its own column, so the lanes compress to the left half.
// VI and VII share this layout exactly: VII must be recognisable as VI's
// apparatus with nothing altered, or the refusal reads as breakage.
// ============================================================

export const COMPACT_LANE_WIDTH =
  (span(6) - LANE_GAP * (KERNELS.length - 1)) / KERNELS.length;

export const compactLaneX = (i: number): number =>
  WORKING_AREA.x + i * (COMPACT_LANE_WIDTH + LANE_GAP);

export const compactLaneCentreX = (i: number): number =>
  compactLaneX(i) + COMPACT_LANE_WIDTH / 2;

export const COMPACT_LANE_HEIGHT = 170;

export const COMPACT_ARTIFACT = {
  inset: SPACE.s3,
  top: LANE_TOP + SPACE.s5,
  height: 88,
  width: COMPACT_LANE_WIDTH - SPACE.s3 * 2,
} as const;

export const COMPACT_AXIS = {
  x: WORKING_AREA.x,
  y: LANE_TOP + COMPACT_LANE_HEIGHT + SPACE.s6,
  width: span(6),
} as const;

/** Right column: the decision cascade. */
export const CASCADE = {
  x: WORKING_AREA.x + span(7) + LANE_GAP,
  y: LANE_TOP,
} as const;

export const TALLY = {
  x: CASCADE.x,
  y: LANE_TOP - SPACE.s5,
} as const;
