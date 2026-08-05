/**
 * MOTION PRIMITIVES
 *
 * Motion System §1.2: "Deceleration only. No bounce, no elastic, no overshoot,
 * anywhere in the system, ever."
 *
 * Visual language §2.1, Rule M1: every animation is either TRANSPORT (a thing
 * moves, unchanged) or TRANSFORMATION (a thing changes state where it stands),
 * and never both in the same beat. The two are modelled here as separate
 * functions returning DISJOINT style properties, so combining them is visible
 * at the call site and caught by `composeMotion`.
 */

import { Easing, interpolate } from "remotion";
import { frames, type TierName } from "./timing";

// ============================================================
// Easing — tokens.motion.css §2.2
//
// Every curve below resolves monotonically. No bounce/elastic token exists in
// this system and none may be added (Motion System Rule 1).
// ============================================================

export const EASE = {
  /** Default: reveals, structure builds, camera. cubic-bezier(0.2, 0.7, 0, 1) */
  standard: Easing.bezier(0.2, 0.7, 0, 1),
  /** Small controls only. cubic-bezier(0.2, 0.8, 0.2, 1) */
  micro: Easing.bezier(0.2, 0.8, 0.2, 1),
  /** Counters, literal-data progress fills. */
  linear: Easing.linear,
} as const;

/**
 * `--yukti-ease-emphasis` is RESERVED to one component per surface (Motion
 * System §7) and visual language §7.2 forbids it for camera outright. It is
 * deliberately NOT exported as a usable curve. This function exists only so
 * that an attempt to reach for it fails loudly with the reason.
 */
export const emphasisIsReserved = (): never => {
  throw new Error(
    "--yukti-ease-emphasis is reserved (Motion System §7). The film's camera " +
      "and all structure motion use EASE.standard (visual language §7.2). If a " +
      "beat genuinely needs emphasis easing, raise an implementation note.",
  );
};

// ============================================================
// Shared timing shape
// ============================================================

export interface MotionSpec {
  /** Absolute frame within the enclosing Sequence. */
  readonly frame: number;
  /** Frame at which this motion starts. */
  readonly at: number;
  /** Duration tier. Named, never a raw number (Motion System §2). */
  readonly tier: TierName;
}

const progress = ({ frame, at, tier }: MotionSpec): number =>
  interpolate(frame, [at, at + frames(tier)], [0, 1], {
    easing: EASE.standard,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

// ============================================================
// TRANSPORT — position only. Teaches FLOW: data moved.
// ============================================================

export interface TransportSpec extends MotionSpec {
  readonly from: { readonly x?: number; readonly y?: number };
  readonly to: { readonly x?: number; readonly y?: number };
}

export interface TransportStyle {
  readonly __kind: "transport";
  readonly transform: string;
}

/**
 * Moves an element from one position to another WITHOUT changing it.
 * Returns only `transform`. Never returns opacity, scale, colour or weight —
 * those are transformation, and Rule M1 forbids mixing them into one beat.
 */
export const transport = (spec: TransportSpec): TransportStyle => {
  const t = progress(spec);
  const x = interpolate(t, [0, 1], [spec.from.x ?? 0, spec.to.x ?? 0]);
  const y = interpolate(t, [0, 1], [spec.from.y ?? 0, spec.to.y ?? 0]);
  return {
    __kind: "transport",
    transform: `translate3d(${x}px, ${y}px, 0)`,
  };
};

// ============================================================
// TRANSFORMATION — state in place. Teaches DERIVATION: data became.
// ============================================================

export interface TransformationSpec extends MotionSpec {
  readonly from: number;
  readonly to: number;
  /** Which single property changes. One per beat. */
  readonly property: "opacity" | "strokeOpacity" | "fillOpacity" | "strokeWidth";
}

export interface TransformationStyle {
  readonly __kind: "transformation";
  readonly property: TransformationSpec["property"];
  readonly value: number;
}

/**
 * Changes one property of an element where it stands. Returns no transform.
 */
export const transformation = (
  spec: TransformationSpec,
): TransformationStyle => ({
  __kind: "transformation",
  property: spec.property,
  value: interpolate(progress(spec), [0, 1], [spec.from, spec.to]),
});

// ============================================================
// Rule M1 enforcement
// ============================================================

export class MixedMotionError extends Error {
  constructor() {
    super(
      "Rule M1 (visual language §2.1): a single element may never transport " +
        "and transform in the same beat. If it must do both, that is two beats. " +
        "Sequence them; do not compose them.",
    );
    this.name = "MixedMotionError";
  }
}

/**
 * Combine motion results into a style object, refusing the one combination the
 * approved language forbids.
 */
export const composeMotion = (
  ...parts: ReadonlyArray<TransportStyle | TransformationStyle>
): Record<string, string | number> => {
  const hasTransport = parts.some((p) => p.__kind === "transport");
  const hasTransformation = parts.some((p) => p.__kind === "transformation");
  if (hasTransport && hasTransformation) {
    throw new MixedMotionError();
  }

  const style: Record<string, string | number> = {};
  for (const part of parts) {
    if (part.__kind === "transport") {
      style["transform"] = part.transform;
    } else {
      style[part.property] = part.value;
    }
  }
  return style;
};

// ============================================================
// Text motion — visual language §2.5
//
// "Type is read, not performed." Exactly two permitted entrances, and nothing
// below the whole text block ever animates (Motion System §5, hard rule).
// ============================================================

export const TEXT_RISE_DISTANCE = 30; // --yukti-distance-md

/** Entrance 1: opacity 0 -> 1 over `mark`. */
export const textFade = (frame: number, at: number): { opacity: number } => ({
  opacity: progress({ frame, at, tier: "mark" }),
});

/**
 * Entrance 2: opacity 0 -> 1 with a 30px rise over `build`.
 *
 * This is the single approved exception to Rule M1's separation: the rise and
 * the fade are one indivisible entrance defined as such by the Motion System,
 * not two motions being composed. It is expressed here as one primitive so it
 * cannot be reassembled incorrectly.
 */
export const textRise = (
  frame: number,
  at: number,
): { opacity: number; transform: string } => {
  const t = progress({ frame, at, tier: "build" });
  return {
    opacity: t,
    transform: `translate3d(0, ${interpolate(t, [0, 1], [TEXT_RISE_DISTANCE, 0])}px, 0)`,
  };
};
