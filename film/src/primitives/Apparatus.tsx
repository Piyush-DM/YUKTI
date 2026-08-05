/**
 * APPARATUS — composite structures the film reuses across movements.
 *
 * Built exclusively from Diagram and Typography primitives. Nothing here
 * redraws a rectangle, a stroke or a text register that already exists.
 */

import { FAMILY } from "../system/fonts";
import { COLOR, LAYER, OPACITY, SPACE, SURFACE, TYPE } from "../system/tokens";
import { textFade } from "../system/motion";
import { buildProgress } from "./Construct";
import { arrive, settle, traverse } from "../system/choreography";
import { Node, confidenceTint, strokeFor, type MarkState } from "./Diagram";

// ============================================================
// Document field — Movement I
// ============================================================

export interface DocumentFieldProps {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly columns: number;
  readonly rows: number;
  readonly frame: number;
  readonly at: number;
  /** Uniform opacity override, for the collapse in Movement II. */
  readonly opacity?: number;
  /**
   * 0..1 collapse toward `collapseTo`. TRANSPORT only — every cell keeps its
   * size and stroke and changes position alone (Rule M1).
   */
  readonly collapse?: number;
  readonly collapseTo?: { readonly x: number; readonly y: number };
}

const DOC_GAP = SPACE.s1;

/** Tiled hairline rectangles. Quantity is legible; content is not. */
export const DocumentField: React.FC<DocumentFieldProps> = ({
  x,
  y,
  width,
  height,
  columns,
  rows,
  frame,
  at,
  opacity,
  collapse = 0,
  collapseTo,
}) => {
  const cellW = (width - DOC_GAP * (columns - 1)) / columns;
  const cellH = (height - DOC_GAP * (rows - 1)) / rows;
  const count = columns * rows;
  const target = collapseTo ?? { x: x + width / 2, y: y + height / 2 };

  return (
    <g>
      {Array.from({ length: count }, (_, i) => {
        const cx = i % columns;
        const cy = Math.floor(i / columns);
        const restX = x + cx * (cellW + DOC_GAP);
        const restY = y + cy * (cellH + DOC_GAP);
        // Documents ARRIVE: they travel in from below at full stroke. Weight
        // comes from things landing, not from things becoming visible.
        const landing = arrive({
          frame,
          at,
          from: "bottom",
          restX,
          restY,
          index: i,
          count,
          tier: "derive",
        });
        const p = opacity ?? 1;
        return (
          <rect
            key={i}
            x={restX + landing.dx + (target.x - cellW / 2 - restX) * collapse}
            y={restY + landing.dy + (target.y - cellH / 2 - restY) * collapse}
            width={cellW}
            height={cellH}
            fill="none"
            stroke={COLOR.bone300}
            strokeWidth={SURFACE.hairline}
            opacity={p * OPACITY.muted}
          />
        );
      })}
    </g>
  );
};

// ============================================================
// Confidence band — value steps on bone, never hue (§9.2)
// ============================================================

export interface ConfidenceBandProps {
  readonly x: number;
  /** Baseline the column falls TO. Columns descend onto it. */
  readonly baselineY: number;
  readonly width: number;
  readonly step: 0 | 1 | 2;
  /** Rest heights across the whole set, so the floor is discoverable. */
  readonly heights: readonly number[];
  readonly index: number;
  readonly frame: number;
  readonly at: number;
  readonly asserted?: boolean;
}

/**
 * A column that FALLS to its rest height. The lowest column is the floor, and
 * the institutional band is drawn at that floor — so "minimum, not mean" is
 * watched happening rather than stated beside a separate bar.
 */
export const ConfidenceBand: React.FC<ConfidenceBandProps> = ({
  x,
  baselineY,
  width,
  step,
  heights,
  index,
  frame,
  at,
  asserted = false,
}) => {
  const tint = confidenceTint(step);
  const { height } = settle({ frame, at, heights, index });
  return (
    <rect
      x={x}
      y={baselineY - height}
      width={width}
      height={height}
      fill={asserted ? COLOR.yellow500 : tint.fill}
      opacity={tint.opacity}
    />
  );
};

// ============================================================
// Artifact — a lane's structured output
// ============================================================

export interface ArtifactProps {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly state?: MarkState;
  readonly frame: number;
  readonly at: number;
  readonly index?: number;
  readonly count?: number;
}

export const Artifact: React.FC<ArtifactProps> = ({
  x,
  y,
  width,
  height,
  state = "established",
  frame,
  at,
  index = 0,
  count = 1,
}) => {
  const p = buildProgress({ frame, at, index, count });
  return (
    <g opacity={p}>
      <Node x={x} y={y} width={width} height={height} state={state} />
      {[0, 1, 2].map((r) => (
        <line
          key={r}
          x1={x + SPACE.s2}
          y1={y + SPACE.s3 + r * SPACE.s2}
          x2={x + width - SPACE.s2 - r * SPACE.s3}
          y2={y + SPACE.s3 + r * SPACE.s2}
          stroke={strokeFor(state)}
          strokeWidth={SURFACE.hairline}
          opacity={OPACITY.muted}
        />
      ))}
    </g>
  );
};

// ============================================================
// Rule list — the decision cascade, Movements VI and VII
// ============================================================

export type RuleOutcome = "fired" | "fell-through" | "unreached";

export interface DecisionRule {
  readonly id: string;
  readonly name: string;
  readonly observed: string;
  readonly outcome: RuleOutcome;
}

export interface RuleListProps {
  readonly rules: readonly DecisionRule[];
  readonly x: number;
  readonly y: number;
  readonly frame: number;
  readonly at: number;
  /**
   * Movement IX's end state is "There is no yellow anywhere on the frame."
   * The cascade is still shown in full, fired marker included — only the
   * assertion colour is withheld.
   */
  readonly suppressAssertion?: boolean;
}

export const RULE_ROW_HEIGHT = 34;

const markerFor = (outcome: RuleOutcome, reached: boolean): string =>
  !reached ? "[     ]" : outcome === "fired" ? "[FIRED]" : "[  no ]";

/**
 * The rule set is a fixed artifact; EVALUATION IS A PROCESS THAT MOVES THROUGH
 * IT. A read-head runs down the rows and halts. Rows are not faded in — they
 * exist from the first frame, because the rules exist whether or not they are
 * reached. What changes is how far the head got.
 *
 * The distance travelled is the information. Movement VI's head reaches R2;
 * Movement VII's stops at R1, and the four rows below it are visibly never
 * arrived at rather than presented as already-greyed.
 */
export const RuleList: React.FC<RuleListProps> = ({
  rules,
  x,
  y,
  frame,
  at,
  suppressAssertion = false,
}) => {
  const haltAt = Math.max(0, rules.findIndex((r) => r.outcome === "fired"));
  const head = traverse({
    frame,
    at,
    rows: rules.length,
    haltAt,
    rowHeight: RULE_ROW_HEIGHT,
  });

  return (
    <div style={{ position: "absolute", left: x, top: y, zIndex: LAYER.data }}>
      {/* The head. Its travel, and where it stops, is the content. */}
      <div
        style={{
          position: "absolute",
          left: -SPACE.s3,
          top: head.headY,
          width: SPACE.s2,
          height: RULE_ROW_HEIGHT / 2,
          borderLeft: `2px solid ${
            head.halted && !suppressAssertion ? COLOR.yellow500 : COLOR.bone300
          }`,
        }}
      />

      {rules.map((rule, i) => {
        const reached = head.reached(i);
        const fired = reached && rule.outcome === "fired";
        return (
          <div
            key={rule.id}
            style={{
              height: RULE_ROW_HEIGHT,
              fontFamily: FAMILY.data,
              fontSize: TYPE.data.size,
              lineHeight: 1.4,
              fontVariantNumeric: TYPE.data.numeric,
              whiteSpace: "pre",
              color:
                fired && !suppressAssertion ? COLOR.yellow500 : COLOR.bone300,
              opacity: reached ? OPACITY.full : OPACITY.muted * 0.7,
            }}
          >
            <div>{`${markerFor(rule.outcome, reached)} ${rule.id} ${rule.name}`}</div>
            <div style={{ opacity: OPACITY.muted }}>
              {reached ? `         observed: ${rule.observed}` : ""}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ============================================================
// Derivation listing — numbered rules, Movement V
// ============================================================

export interface DerivationLine {
  readonly rule: string;
  readonly text: string;
}

export interface DerivationProps {
  readonly lines: readonly DerivationLine[];
  readonly x: number;
  readonly y: number;
  readonly frame: number;
  readonly at: number;
  /** The limiting factor, marked in yellow. */
  readonly limitingFactor?: string;
  readonly limitAt?: number;
}

const DERIVATION_ROW_HEIGHT = 22;

export const Derivation: React.FC<DerivationProps> = ({
  lines,
  x,
  y,
  frame,
  at,
  limitingFactor,
  limitAt,
}) => (
  <div style={{ position: "absolute", left: x, top: y, zIndex: LAYER.data }}>
    {lines.map((line, i) => (
      <div
        key={line.rule}
        style={{
          height: DERIVATION_ROW_HEIGHT,
          fontFamily: FAMILY.data,
          fontSize: TYPE.data.size,
          fontVariantNumeric: TYPE.data.numeric,
          whiteSpace: "pre",
          color: COLOR.bone300,
          opacity: buildProgress({ frame, at, index: i, count: lines.length }),
        }}
      >
        {`${line.rule}: ${line.text}`}
      </div>
    ))}
    {limitingFactor && limitAt !== undefined ? (
      <div
        style={{
          height: DERIVATION_ROW_HEIGHT,
          marginTop: SPACE.s2,
          fontFamily: FAMILY.data,
          fontSize: TYPE.data.size,
          fontVariantNumeric: TYPE.data.numeric,
          whiteSpace: "pre",
          color: COLOR.yellow500,
          zIndex: LAYER.assertion,
          ...textFade(frame, limitAt),
        }}
      >
        {`limited by: ${limitingFactor}`}
      </div>
    ) : null}
  </div>
);
