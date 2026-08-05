/**
 * CAMERA PRIMITIVES — THE READING INSTRUMENT
 *
 * Visual language §0 (declared extension) and §7.
 *
 * The Motion System bans a virtual camera outright (§1.4) because the website's
 * viewport is controlled by scroll. A film has no user, so something must do
 * scroll's job. The approved extension is narrow and its constraints are the
 * whole point:
 *
 *   "The camera is a reading instrument, not a spectacle device. It does only
 *    what a reader's eye and hand do at a drafting table. It has NO PERSPECTIVE,
 *    NO VANISHING POINT, NO DEPTH. Everything is orthographic, always."
 *
 * This module therefore exposes scale and axis-locked translation and NOTHING
 * ELSE. Rotation, perspective, dolly, roll, focus and motion blur are not
 * missing features — they are absent so that spectacle is unrepresentable.
 */

import { interpolate } from "remotion";
import { CANVAS } from "./tokens";
import { EASE } from "./motion";
import { frames } from "./timing";

// ============================================================
// The three states — visual language §7.1
// ============================================================

export type CameraState = "PLATE" | "DETAIL" | "INDEX";

export const CAMERA_SCALE: Record<CameraState, number> = {
  /** The whole structure in frame. Default. The film sits here most of the time. */
  PLATE: 1.0,
  /** Pushed to one region under discussion. Ceiling, not a target. */
  DETAIL: 2.5,
  /** Pulled out to show relation between plates. At most twice in the film. */
  INDEX: 0.6,
};

export interface CameraKeyframe {
  /** Absolute frame at which this state is reached. */
  readonly at: number;
  readonly state: CameraState;
  /**
   * Point of interest in canvas coordinates. Ignored for PLATE, which always
   * centres the canvas.
   */
  readonly focus?: { readonly x: number; readonly y: number };
}

const CANVAS_CENTRE = { x: CANVAS.width / 2, y: CANVAS.height / 2 } as const;

const focusOf = (kf: CameraKeyframe): { x: number; y: number } =>
  kf.state === "PLATE" ? CANVAS_CENTRE : (kf.focus ?? CANVAS_CENTRE);

/**
 * Resolve the camera transform for a frame.
 *
 * Returns a CSS transform composed only of translate and scale. The returned
 * string is orthographic by construction: there is no `perspective()`, no
 * `rotate*()`, and no `translateZ`.
 */
export const cameraTransform = (
  keyframes: readonly CameraKeyframe[],
  frame: number,
): string => {
  if (keyframes.length === 0) {
    return "translate3d(0px, 0px, 0) scale(1)";
  }

  const move = frames("camera");

  // Find the segment this frame sits in.
  let from = keyframes[0]!;
  let to = keyframes[0]!;
  for (let i = 0; i < keyframes.length; i++) {
    const kf = keyframes[i]!;
    if (frame >= kf.at) {
      from = kf;
      to = keyframes[i + 1] ?? kf;
    }
  }

  const t =
    to === from
      ? 1
      : interpolate(frame, [from.at, from.at + move], [0, 1], {
          easing: EASE.standard,
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  const fromFocus = focusOf(from);
  const toFocus = focusOf(to);

  const scale = interpolate(
    t,
    [0, 1],
    [CAMERA_SCALE[from.state], CAMERA_SCALE[to.state]],
  );
  const cx = interpolate(t, [0, 1], [fromFocus.x, toFocus.x]);
  const cy = interpolate(t, [0, 1], [fromFocus.y, toFocus.y]);

  // Orthographic: place the focus point at canvas centre, scaled about itself.
  const tx = CANVAS.width / 2 - cx * scale;
  const ty = CANVAS.height / 2 - cy * scale;

  return `translate3d(${tx}px, ${ty}px, 0) scale(${scale})`;
};

// ============================================================
// Rule enforcement — visual language §7.3
// ============================================================

export interface FrameWindow {
  readonly start: number;
  readonly end: number;
  readonly label: string;
}

export class CameraRuleError extends Error {
  constructor(rule: string, detail: string) {
    super(`${rule} (visual language §7.3): ${detail}`);
    this.name = "CameraRuleError";
  }
}

/**
 * Rule C1 — "The camera never moves while a structure is building. Build, then
 * move, or move, then build. Never simultaneously."
 *
 * Simultaneous camera and content motion is the most reliable way to lose a
 * viewer, and the rule is marked non-negotiable. Plates declare their build
 * windows; this checks the camera against them.
 */
export const assertNoCameraDuringBuild = (
  keyframes: readonly CameraKeyframe[],
  buildWindows: readonly FrameWindow[],
): void => {
  const move = frames("camera");
  for (const kf of keyframes) {
    const moveStart = kf.at;
    const moveEnd = kf.at + move;
    for (const w of buildWindows) {
      if (moveStart < w.end && w.start < moveEnd) {
        throw new CameraRuleError(
          "Rule C1",
          `camera move at frame ${moveStart}-${moveEnd} overlaps build ` +
            `"${w.label}" (${w.start}-${w.end}). Sequence them.`,
        );
      }
    }
  }
};

/** Rule C2 — one camera move per plate, maximum. Many plates have none. */
export const assertOneMovePerPlate = (
  keyframes: readonly CameraKeyframe[],
  plateLabel: string,
): void => {
  // The opening keyframe establishes state; moves are the transitions after it.
  const moves = Math.max(0, keyframes.length - 1);
  if (moves > 1) {
    throw new CameraRuleError(
      "Rule C2",
      `plate "${plateLabel}" declares ${moves} camera moves; the maximum is 1.`,
    );
  }
};

/** Rule C3 — the camera returns to PLATE before any transition. */
export const assertReturnsToPlate = (
  keyframes: readonly CameraKeyframe[],
  plateLabel: string,
): void => {
  const last = keyframes[keyframes.length - 1];
  if (last && last.state !== "PLATE") {
    throw new CameraRuleError(
      "Rule C3",
      `plate "${plateLabel}" ends in ${last.state}; the camera must return to ` +
        `PLATE before a transition.`,
    );
  }
};

/**
 * TODO — INCONSISTENCY, NOT RESOLVED HERE.
 *
 * Visual language Rule C3 requires the camera to return to PLATE before any
 * transition. FILM_STRUCTURE.md's Movement VIII End State is "The camera has
 * pulled to INDEX", which is that movement's terminal frame and is also the
 * verbatim Start State of Movement IX.
 *
 * The two cannot both hold. Rather than silently drop the check or refuse the
 * approved end state, an exemption must be declared with a reason and is
 * recorded at the call site. Exactly one movement uses it.
 */
export interface CameraRuleExemption {
  readonly rule: "C3";
  readonly reason: string;
}

export const assertCameraRules = (
  keyframes: readonly CameraKeyframe[],
  buildWindows: readonly FrameWindow[],
  plateLabel: string,
  exemption?: CameraRuleExemption,
): void => {
  assertOneMovePerPlate(keyframes, plateLabel);
  if (exemption?.rule !== "C3") {
    assertReturnsToPlate(keyframes, plateLabel);
  }
  assertNoCameraDuringBuild(keyframes, buildWindows);
};
