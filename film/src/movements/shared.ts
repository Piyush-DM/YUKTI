/**
 * Shared movement wiring. Every movement reads its approved metadata from the
 * registry and its length from its approved proportional weight — never from a
 * literal in the movement file.
 */

import { CANVAS } from "../system/tokens";
import { SAFE } from "../system/layout";
import { weightToFrames } from "../system/timing";
import { buildPlateBeats } from "../primitives/Plate";
import { movementByIndex, type Movement } from "../registry/movements";
import type { TierName } from "../system/timing";

export const MOVEMENT_COUNT = 9;

export interface MovementTiming {
  readonly movement: Movement;
  readonly durationInFrames: number;
}

export const movementTiming = (
  index: number,
  totalSeconds?: number,
): MovementTiming => {
  const movement = movementByIndex(index);
  return {
    movement,
    durationInFrames: weightToFrames(movement.weight, totalSeconds),
  };
};

/** Beat schedule for a movement, honouring its weight-derived length. */
export const movementBeats = (
  index: number,
  constructionTier: TierName = "build",
  holdTier: "holdRead" | "holdWeight" = "holdRead",
  totalSeconds?: number,
) =>
  buildPlateBeats(
    constructionTier,
    holdTier,
    movementTiming(index, totalSeconds).durationInFrames,
  );

/** Lower-right datum anchor, shared by movements that print a count. */
export const COUNT_ANCHOR = {
  right: SAFE.right,
  bottom: SAFE.bottom + 40,
  top: CANVAS.height - SAFE.bottom - 40,
} as const;
