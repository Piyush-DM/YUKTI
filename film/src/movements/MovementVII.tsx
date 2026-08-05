/**
 * MOVEMENT VII — RESTRAINT
 * "What happens when there is not enough?"
 *
 * THE FRAME. FILM_STRUCTURE.md:
 *
 *   "INSUFFICIENT_BASIS, in yellow mono, at the exact coordinates where every
 *    previous verdict has appeared — beneath a fully intact apparatus, with
 *    decision rules greyed and never reached."
 *
 * A substitution, not a reveal. The apparatus reuses VI's geometry unchanged
 * (`laneGeometry`), because a machine that looks different reads as broken and
 * the refusal must read as what the system correctly produced.
 *
 * Rule F1: this is the first and only time yellow marks a declared
 * non-conclusion. Rule F3: the longest hold in the film.
 */

import { useCurrentFrame } from "remotion";
import { CANVAS, COLOR, OPACITY, SPACE, TYPE } from "../system/tokens";
import { FAMILY } from "../system/fonts";
import { frames } from "../system/timing";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Axis, Node } from "../primitives/Diagram";
import { Artifact, RuleList, type DecisionRule } from "../primitives/Apparatus";
import { StructureLabel } from "../primitives/Typography";
import { Verdict } from "../primitives/Verdict";
import { KERNELS } from "../content/packet";
import { MOVEMENT_COUNT, movementTiming } from "./shared";
import {
  CASCADE,
  COMPACT_ARTIFACT,
  COMPACT_AXIS,
  COMPACT_LANE_HEIGHT,
  COMPACT_LANE_WIDTH,
  LANE_TOP,
  TALLY,
  compactLaneX,
} from "./laneGeometry";

/**
 * TODO — INCONSISTENCY, NOT RESOLVED HERE.
 *
 * FILM_STRUCTURE.md states the cascade leaves "five decision rules greyed and
 * never reached" after R1 fires, which implies six rules. CHOIR_v0.1_RESEARCH_
 * FREEZE.md §3.2 A6 freezes "the five decision rules and their ordering", and
 * Movement VI is built on those five.
 *
 * Implemented with the frozen five (R1 fires, R2-R5 unreached = four greyed)
 * because the research freeze governs system facts and the film may not invent
 * a sixth rule. Flagged rather than reconciled: whether FILM_STRUCTURE.md's
 * count is corrected, or the frame description is reworded, is not an
 * implementation decision.
 */
const INSUFFICIENT_RULES: readonly DecisionRule[] = [
  {
    id: "R1",
    name: "insufficient-basis",
    observed: "2 usable of 4",
    outcome: "fired",
  },
  {
    id: "R2",
    name: "live-disagreement",
    observed: "not evaluated",
    outcome: "unreached",
  },
  {
    id: "R3",
    name: "proceed-with-conditions",
    observed: "not evaluated",
    outcome: "unreached",
  },
  { id: "R4", name: "proceed", observed: "not evaluated", outcome: "unreached" },
  { id: "R5", name: "decline", observed: "not evaluated", outcome: "unreached" },
];

const TALLY_TEXT = "coverage 2/5 (40%) — below 50% minimum";

/** Lanes 2 and 3 conclude nothing on the thin packet, and say so. */
const CONCLUDED_NOTHING = new Set([2, 3]);

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;
  const cascadeAt = at + frames("build");

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        {KERNELS.map((kernel, i) => {
          const empty = CONCLUDED_NOTHING.has(i);
          return (
            <g key={kernel}>
              <Node
                x={compactLaneX(i)}
                y={LANE_TOP}
                width={COMPACT_LANE_WIDTH}
                height={COMPACT_LANE_HEIGHT}
                state="established"
                opacity={0.45}
              />
              {/* Reached, not established — dashed, and retained (Rule K1). */}
              <Artifact
                x={compactLaneX(i) + COMPACT_ARTIFACT.inset}
                y={COMPACT_ARTIFACT.top}
                width={COMPACT_ARTIFACT.width}
                height={COMPACT_ARTIFACT.height}
                state="unevaluated"
                frame={frame}
                at={at}
                index={i}
                count={KERNELS.length}
              />
              {empty ? null : (
                <circle
                  cx={compactLaneX(i) + COMPACT_LANE_WIDTH / 2}
                  cy={COMPACT_AXIS.y}
                  r={5}
                  fill="none"
                  stroke={COLOR.bone300}
                  strokeWidth={1}
                  strokeDasharray="2 3"
                  opacity={OPACITY.muted}
                />
              )}
            </g>
          );
        })}

        <Axis x={COMPACT_AXIS.x} y={COMPACT_AXIS.y} width={COMPACT_AXIS.width} />
      </svg>

      {KERNELS.map((kernel, i) => (
        <div
          key={kernel}
          style={{
            position: "absolute",
            left: compactLaneX(i) + COMPACT_ARTIFACT.inset,
            top: LANE_TOP + SPACE.s2,
          }}
        >
          <StructureLabel frame={frame} at={at}>
            {kernel.slice(0, 12)}
          </StructureLabel>
        </div>
      ))}

      {KERNELS.map((kernel, i) =>
        CONCLUDED_NOTHING.has(i) ? (
          <div
            key={`nil-${kernel}`}
            style={{
              position: "absolute",
              left: compactLaneX(i) + COMPACT_ARTIFACT.inset,
              top: COMPACT_ARTIFACT.top + COMPACT_ARTIFACT.height + SPACE.s3,
              fontFamily: FAMILY.data,
              fontSize: TYPE.data.size,
              color: COLOR.bone300,
              opacity: OPACITY.muted,
            }}
          >
            no conclusion
          </div>
        ) : null,
      )}

      <div
        style={{
          position: "absolute",
          left: TALLY.x,
          top: TALLY.y,
          fontFamily: FAMILY.data,
          fontSize: TYPE.data.size,
          fontVariantNumeric: TYPE.data.numeric,
          color: COLOR.bone300,
          opacity: frame >= cascadeAt ? 1 : 0,
        }}
      >
        {TALLY_TEXT}
      </div>

      <RuleList
        rules={INSUFFICIENT_RULES}
        x={CASCADE.x}
        y={CASCADE.y}
        frame={frame}
        at={cascadeAt}
      />

      <Verdict
        frame={frame}
        at={beats.assertion.start}
        deliverFrom={{ x: CASCADE.x, y: CASCADE.y }}
      >
        INSUFFICIENT_BASIS
      </Verdict>
    </>
  );
};

export const MovementVII: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(7);
  return (
    <Plate
      number={movement.index}
      total={MOVEMENT_COUNT}
      title={movement.name}
      question={movement.question}
      constructionTier="build"
      holdTier="holdWeight"
      durationInFrames={durationInFrames}
    >
      <Content />
    </Plate>
  );
};
