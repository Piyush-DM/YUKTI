/**
 * TYPOGRAPHY PRIMITIVES — visual language §4
 *
 * §4.1 is the film's core information-hierarchy device:
 *
 *   Söhne  -> "this is a section of the argument"   (plate titles only)
 *   Inter  -> "a human is explaining"               (questions, explanation)
 *   Mono   -> "this is a literal value from the system"
 *
 * The viewer learns the mapping in the first plate and it carries the whole
 * film. Each face therefore gets its own component and they are not
 * interchangeable.
 */

import type { CSSProperties, ReactNode } from "react";
import { FAMILY } from "../system/fonts";
import { COLOR, OPACITY, TYPE, LAYER } from "../system/tokens";
import { assertBodyTextBudget } from "../system/budgets";
import { textFade, textRise } from "../system/motion";

// ============================================================
// Slug — visual language §3.1
// ============================================================

export interface SlugProps {
  readonly plate: number;
  readonly total: number;
  readonly title: string;
  readonly frame: number;
  readonly at?: number;
}

/**
 * "PLATE 04 / 12          INDEPENDENT KERNELS"
 *
 * The viewer's location indicator for the entire film. Never animates beyond a
 * cross-fade on plate change.
 */
export const Slug: React.FC<SlugProps> = ({
  plate,
  total,
  title,
  frame,
  at = 0,
}) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      bottom: 0,
      display: "flex",
      gap: 48,
      // The slug is a single line of furniture, never wrapped. Without this it
      // collapses to the intrinsic width of its flex parent and stacks.
      whiteSpace: "nowrap",
      fontFamily: FAMILY.data,
      fontSize: TYPE.label.size,
      fontWeight: TYPE.label.weight,
      letterSpacing: TYPE.label.tracking,
      color: COLOR.bone300,
      textTransform: "uppercase",
      zIndex: LAYER.furniture,
      // The slug rests at 35% (§3.1) AND fades in. Multiplying keeps both:
      // spreading textFade last would silently discard the resting opacity.
      opacity: OPACITY.muted * textFade(frame, at).opacity,
    }}
  >
    <span style={{ fontVariantNumeric: TYPE.data.numeric }}>
      {`PLATE ${String(plate).padStart(2, "0")} / ${String(total).padStart(2, "0")}`}
    </span>
    <span>{title}</span>
  </div>
);

// ============================================================
// Plate title — Söhne, mega tier
// ============================================================

export interface PlateTitleProps {
  /** Word-stacked: each entry renders on its own line (§4.2). */
  readonly words: readonly string[];
  readonly frame: number;
  readonly at?: number;
  readonly style?: CSSProperties;
}

export const PlateTitle: React.FC<PlateTitleProps> = ({
  words,
  frame,
  at = 0,
  style,
}) => (
  <h1
    style={{
      margin: 0,
      fontFamily: FAMILY.display,
      fontSize: TYPE.mega.size,
      fontWeight: TYPE.mega.weight,
      letterSpacing: TYPE.mega.tracking,
      lineHeight: TYPE.mega.lineHeight,
      textTransform: "uppercase",
      textAlign: "left",
      color: COLOR.bone100,
      zIndex: LAYER.furniture,
      ...textRise(frame, at),
      ...style,
    }}
  >
    {words.map((w) => (
      <div key={w}>{w}</div>
    ))}
  </h1>
);

// ============================================================
// Question — Inter, heading tier
// ============================================================

export interface QuestionProps {
  readonly children: string;
  readonly frame: number;
  readonly at?: number;
  readonly style?: CSSProperties;
}

/**
 * Rule S1: "No plate exists that does not print its question on screen. If the
 * question cannot be written in one line, the plate is doing more than one job
 * and must be split."
 *
 * The trailing "?" is enforced because the question is the plate's contract.
 */
export const Question: React.FC<QuestionProps> = ({
  children,
  frame,
  at = 0,
  style,
}) => {
  if (!children.trimEnd().endsWith("?")) {
    throw new Error(
      `Rule S1 (visual language §5.3): a plate's question must be a question. ` +
        `Received: "${children}"`,
    );
  }
  return (
    <p
      style={{
        margin: 0,
        fontFamily: FAMILY.body,
        fontSize: TYPE.heading.size,
        fontWeight: TYPE.heading.weight,
        letterSpacing: TYPE.heading.tracking,
        lineHeight: TYPE.heading.lineHeight,
        color: COLOR.bone100,
        textAlign: "left",
        zIndex: LAYER.furniture,
        ...textRise(frame, at),
        ...style,
      }}
    >
      {children}
    </p>
  );
};

// ============================================================
// Explanatory line — Inter, body tier
// ============================================================

export interface LineProps {
  readonly children: string;
  readonly frame: number;
  readonly at?: number;
  readonly plate: string;
  readonly style?: CSSProperties;
}

/** Max two lines on screen, ever (§4.2). Enforced against the approved measure. */
export const Line: React.FC<LineProps> = ({
  children,
  frame,
  at = 0,
  plate,
  style,
}) => {
  assertBodyTextBudget(children, plate);
  return (
    <p
      style={{
        margin: 0,
        maxWidth: "54ch",
        fontFamily: FAMILY.body,
        fontSize: TYPE.body.size,
        fontWeight: TYPE.body.weight,
        lineHeight: TYPE.body.lineHeight,
        color: COLOR.bone300,
        textAlign: "left",
        zIndex: LAYER.furniture,
        ...textFade(frame, at),
        ...style,
      }}
    >
      {children}
    </p>
  );
};

// ============================================================
// Datum — IBM Plex Mono
// ============================================================

/**
 * Rule T1: "If a string appears in mono, it must be a string the system would
 * actually emit. Never decorative mono."
 *
 * `source` makes that claim explicit at the call site. It mirrors CHOIR's own
 * commitment X4 — kernels cite only identifiers present in the IR — applied to
 * the film's own typography.
 */
export type DatumSource =
  | "ir"
  | "artifact"
  | "synthesis"
  | "trace"
  | "verdict"
  | "audit"
  | "confidence";

export interface DatumProps {
  readonly children: ReactNode;
  readonly source: DatumSource;
  readonly frame: number;
  readonly at?: number;
  /** Assertion layer — yellow. One per frame (§1.4). */
  readonly asserted?: boolean;
  readonly style?: CSSProperties;
}

export const Datum: React.FC<DatumProps> = ({
  children,
  frame,
  at = 0,
  asserted = false,
  style,
}) => (
  <span
    style={{
      fontFamily: FAMILY.data,
      fontSize: TYPE.data.size,
      fontWeight: TYPE.data.weight,
      lineHeight: TYPE.data.lineHeight,
      fontVariantNumeric: TYPE.data.numeric,
      color: asserted ? COLOR.yellow500 : COLOR.bone300,
      zIndex: asserted ? LAYER.assertion : LAYER.data,
      ...textFade(frame, at),
      ...style,
    }}
  >
    {children}
  </span>
);

// ============================================================
// Structure label — uppercase, tracked
// ============================================================

export interface StructureLabelProps {
  readonly children: string;
  readonly frame: number;
  readonly at?: number;
  readonly style?: CSSProperties;
}

export const StructureLabel: React.FC<StructureLabelProps> = ({
  children,
  frame,
  at = 0,
  style,
}) => (
  <span
    style={{
      fontFamily: FAMILY.body,
      fontSize: TYPE.label.size,
      fontWeight: TYPE.label.weight,
      letterSpacing: TYPE.label.tracking,
      textTransform: "uppercase",
      color: COLOR.bone300,
      zIndex: LAYER.structure,
      ...textFade(frame, at),
      ...style,
    }}
  >
    {children}
  </span>
);
