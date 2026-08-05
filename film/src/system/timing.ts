/**
 * TIMING UTILITIES
 *
 * Motion System §2: "No engineer hand-writes a duration or a bezier curve
 * inline — every animation references one of these tokens by name."
 *
 * This module makes that rule structural rather than advisory. `frames()`
 * accepts a tier NAME, not a number, so the forbidden 400-500ms gap is
 * unreachable through the normal path. `framesFromMs()` exists for the rare
 * measured case and asserts against the gap at runtime.
 */

import { CANVAS } from "./tokens";

// ============================================================
// Film duration tiers — visual language §2.2
//
// Every tier is a multiple of a published motion token. None is invented.
// At 30fps every tier resolves to a whole number of frames; this is why 30 was
// chosen over 60 (see README, "Frame rate").
// ============================================================

export const TIER = {
  /** 200ms = --yukti-duration-quick. A single element appearing. */
  mark: 200,
  /** 800ms = --yukti-duration-reveal. A structure assembling. */
  build: 800,
  /** 1600ms = --yukti-duration-cinematic. A value being derived. */
  derive: 1600,
  /** 1200ms. Stillness after a structure completes. */
  holdRead: 1200,
  /** 2400ms = 2 x holdRead. Stillness after the film's key claims. */
  holdWeight: 2400,
  /** 800ms = --yukti-duration-reveal. Any camera state change. */
  camera: 800,
} as const;

export type TierName = keyof typeof TIER;

/**
 * Motion System §2.1 / architecture D10: the 400-500ms band is intentionally
 * empty. "Motion in that gap reads as hesitant — neither a reflex nor a
 * decision — and is banned by rule."
 */
const FORBIDDEN_GAP_MIN = 400;
const FORBIDDEN_GAP_MAX = 500;

export class ForbiddenDurationError extends Error {
  constructor(ms: number) {
    super(
      `Duration ${ms}ms falls in the forbidden 400-500ms band ` +
        `(Motion System §2.1, architecture D10). Round down to 'mark' if the ` +
        `trigger was direct, or up to 'build' if it changes what the viewer ` +
        `understands. Do not add a tier here.`,
    );
    this.name = "ForbiddenDurationError";
  }
}

/** Convert milliseconds to whole frames at the film's frame rate. */
const msToFrames = (ms: number): number => Math.round((ms / 1000) * CANVAS.fps);

/**
 * The normal path. Takes a tier name; cannot express a forbidden duration.
 *
 *   frames("build")  // 24
 */
export const frames = (tier: TierName): number => msToFrames(TIER[tier]);

/**
 * Escape hatch for measured, non-tier durations (e.g. a hold tuned to
 * narration). Asserts against the forbidden gap.
 */
export const framesFromMs = (ms: number): number => {
  if (ms >= FORBIDDEN_GAP_MIN && ms <= FORBIDDEN_GAP_MAX) {
    throw new ForbiddenDurationError(ms);
  }
  return msToFrames(ms);
};

/** Seconds to frames. For movement-length arithmetic only. */
export const seconds = (s: number): number => Math.round(s * CANVAS.fps);

// ============================================================
// Beat sequencing
// ============================================================

export interface Beat {
  readonly name: string;
  readonly start: number;
  readonly duration: number;
  readonly end: number;
}

/**
 * Lay beats end to end from frame 0 and return absolute frame ranges.
 * Used by the Plate system to schedule the approved six-beat template.
 */
export const sequence = (
  spec: ReadonlyArray<readonly [name: string, tier: TierName]>,
): Beat[] => {
  const out: Beat[] = [];
  let cursor = 0;
  for (const [name, tier] of spec) {
    const duration = frames(tier);
    out.push({ name, start: cursor, duration, end: cursor + duration });
    cursor += duration;
  }
  return out;
};

export const totalFrames = (beats: readonly Beat[]): number =>
  beats.length === 0 ? 0 : Math.max(...beats.map((b) => b.end));

// ============================================================
// Runtime allocation
// ============================================================

/**
 * UNAPPROVED VALUE — see IMPLEMENTATION_NOTES.md, note 1.
 *
 * Visual language §11.1 lists total runtime as an open item ("roughly
 * 3:00-3:30, confirm the target"). FILM_STRUCTURE.md deliberately expresses
 * movement lengths as PROPORTIONS so they hold at any total.
 *
 * 210s (3:30) is a placeholder at the top of the stated range. Changing it
 * re-times the whole film correctly and requires no other edit.
 */
export const PLACEHOLDER_TOTAL_SECONDS = 210;

/**
 * Convert an approved proportional weight into frames.
 * Weights are defined in the scene registry and sum to 1.
 */
export const weightToFrames = (
  weight: number,
  totalSeconds: number = PLACEHOLDER_TOTAL_SECONDS,
): number => Math.round(weight * totalSeconds * CANVAS.fps);
