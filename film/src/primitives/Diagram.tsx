/**
 * DIAGRAM PRIMITIVES — visual language §9.2
 *
 * The approved constraint that shapes this entire module: D14 permits exactly
 * one accent hue, so CHOIR's states — support/opposition, established/
 * unevaluated, live/defeated — CANNOT be encoded in colour. Red/green is the
 * dashboard register the film exists to avoid, and it fails colour-vision
 * accessibility besides.
 *
 * State is therefore encoded in FORM and VALUE:
 *
 *   present / absent      solid stroke / hairline dashed stroke
 *   support / opposition  filled / hollow
 *   confidence            value steps on bone, never hue
 *   assertion             yellow, and only yellow
 *   defeated / withdrawn  35% opacity + 1px strike rule, RETAINED on screen
 *
 * Rule K1 is implemented literally here: `Defeated` dims its child, it never
 * unmounts it. Nothing is ever deleted from the frame.
 */

import type { ReactNode } from "react";
import { COLOR, LAYER, OPACITY, SURFACE } from "../system/tokens";

// ============================================================
// Mark state
// ============================================================

export type MarkState =
  /** Established: evidence supports it. Solid stroke. */
  | "established"
  /** Reached but not established. Hairline dashed — visibly not a false thing. */
  | "unevaluated"
  /** Defeated or withdrawn. Dimmed and struck, never removed (Rule K1). */
  | "defeated"
  /** The single thing this frame is claiming. Yellow. */
  | "asserted";

/** Dash pattern for unevaluated material. One pattern, used everywhere. */
export const DASH_UNEVALUATED = "6 5";

export const strokeFor = (state: MarkState): string =>
  state === "asserted" ? COLOR.yellow500 : COLOR.bone300;

export const opacityFor = (state: MarkState): number =>
  state === "defeated" ? OPACITY.muted : OPACITY.full;

export const dashFor = (state: MarkState): string | undefined =>
  state === "unevaluated" ? DASH_UNEVALUATED : undefined;

export const layerFor = (state: MarkState): number =>
  state === "asserted" ? LAYER.assertion : LAYER.structure;

/**
 * Confidence as a value step on bone. Never a hue (§9.2).
 * Step 0 is the strongest reading, step 2 the weakest.
 */
export const confidenceTint = (step: 0 | 1 | 2): { fill: string; opacity: number } =>
  [
    { fill: COLOR.bone100, opacity: OPACITY.full },
    { fill: COLOR.bone300, opacity: OPACITY.full },
    { fill: COLOR.bone300, opacity: OPACITY.muted },
  ][step]!;

// ============================================================
// Node
// ============================================================

export interface NodeProps {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly state?: MarkState;
  /** Support is filled; opposition is hollow (§9.2). */
  readonly filled?: boolean;
  readonly opacity?: number;
}

export const Node: React.FC<NodeProps> = ({
  x,
  y,
  width,
  height,
  state = "established",
  filled = false,
  opacity,
}) => (
  <rect
    x={x}
    y={y}
    width={width}
    height={height}
    rx={SURFACE.radiusSm}
    fill={filled ? strokeFor(state) : "none"}
    fillOpacity={filled ? 0.12 : 0}
    stroke={strokeFor(state)}
    strokeWidth={SURFACE.hairline}
    strokeDasharray={dashFor(state)}
    opacity={opacity ?? opacityFor(state)}
  />
);

// ============================================================
// Edge
// ============================================================

export interface EdgeProps {
  readonly from: { readonly x: number; readonly y: number };
  readonly to: { readonly x: number; readonly y: number };
  readonly state?: MarkState;
  /**
   * 0..1 draw-on progress. A construction utility, not decoration: an edge
   * drawing itself is TRANSPORT (§2.1) and teaches that something connected.
   */
  readonly progress?: number;
  readonly opacity?: number;
}

export const Edge: React.FC<EdgeProps> = ({
  from,
  to,
  state = "established",
  progress = 1,
  opacity,
}) => {
  const length = Math.hypot(to.x - from.x, to.y - from.y);
  const drawn = length * Math.max(0, Math.min(1, progress));
  return (
    <line
      x1={from.x}
      y1={from.y}
      x2={to.x}
      y2={to.y}
      stroke={strokeFor(state)}
      strokeWidth={SURFACE.hairline}
      strokeDasharray={state === "unevaluated" ? DASH_UNEVALUATED : `${drawn} ${length}`}
      opacity={opacity ?? opacityFor(state)}
    />
  );
};

// ============================================================
// Lane — a sealed vertical channel
// ============================================================

export interface LaneProps {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly opacity?: number;
  readonly children?: ReactNode;
}

/**
 * Movement IV's central teaching is an ABSENCE — no line connects any lane to
 * any other, and the viewer must be able to confirm it by looking.
 *
 * A `Lane` therefore renders its own bounded channel and nothing that crosses
 * it. There is deliberately no `connectTo` prop on this component: inter-lane
 * connection is not a thing the primitive can express.
 */
export const Lane: React.FC<LaneProps> = ({
  x,
  y,
  width,
  height,
  opacity = OPACITY.full,
  children,
}) => (
  <g opacity={opacity}>
    <rect
      x={x}
      y={y}
      width={width}
      height={height}
      fill="none"
      stroke={COLOR.hairlineDark}
      strokeWidth={SURFACE.hairline}
    />
    {children}
  </g>
);

// ============================================================
// Defeated — Rule K1
// ============================================================

export interface DefeatedProps {
  readonly children: ReactNode;
  /** Bounding box for the strike rule. */
  readonly box: {
    readonly x: number;
    readonly y: number;
    readonly width: number;
    readonly height: number;
  };
}

/**
 * Rule K1: "Nothing is ever deleted from the frame. Defeated evidence,
 * withdrawn claims and rejected alternatives dim to 35% and REMAIN on screen
 * for the rest of the plate."
 *
 * This wrapper dims and strikes. It has no code path that removes its child —
 * that is the point. It is commitment E12 rendered as a visual law.
 */
export const Defeated: React.FC<DefeatedProps> = ({ children, box }) => (
  <g opacity={OPACITY.muted}>
    {children}
    <line
      x1={box.x}
      y1={box.y + box.height / 2}
      x2={box.x + box.width}
      y2={box.y + box.height / 2}
      stroke={COLOR.bone300}
      strokeWidth={SURFACE.hairline}
    />
  </g>
);

// ============================================================
// Axis — for support/opposition positioning
// ============================================================

export interface AxisProps {
  readonly x: number;
  readonly y: number;
  readonly width: number;
}

/** A stated axis. Positions above it read as support, below as opposition. */
export const Axis: React.FC<AxisProps> = ({ x, y, width }) => (
  <line
    x1={x}
    y1={y}
    x2={x + width}
    y2={y}
    stroke={COLOR.hairlineDark}
    strokeWidth={SURFACE.hairline}
  />
);
