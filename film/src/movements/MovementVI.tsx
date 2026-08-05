/**
 * MOVEMENT VI — CONTRADICTION
 * "What happens when they do not agree?"
 *
 * Rule F4: this movement's structural job is to reinforce, one last time, the
 * expectation that VII breaks. The machine must be seen resolving a genuinely
 * hard case, completely, with the full cascade evaluating in order — several
 * rules reached, one firing. The viewer must leave certain that this system
 * produces verdicts.
 */

import { useCurrentFrame } from "remotion";
import { CANVAS, COLOR, SPACE, TYPE } from "../system/tokens";
import { FAMILY } from "../system/fonts";
import { frames } from "../system/timing";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Axis, Edge, Node } from "../primitives/Diagram";
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
  SPLIT_STANCE,
  TALLY,
  compactLaneCentreX,
  compactLaneX,
} from "./laneGeometry";

/** The full cascade, evaluated in order. Nothing is omitted. */
export const CONTESTED_RULES: readonly DecisionRule[] = [
  {
    id: "R1",
    name: "insufficient-basis",
    observed: "4 usable of 4",
    outcome: "fell-through",
  },
  {
    id: "R2",
    name: "live-disagreement",
    observed: "2 disagreement(s), margin 1",
    outcome: "fired",
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

const TALLY_TEXT = "support 4, opposition 4, conditional 2";

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;

  const axisAt = at + frames("build");
  const cascadeAt = axisAt + frames("build");

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        {KERNELS.map((kernel, i) => {
          const stanceX =
            COMPACT_AXIS.x + COMPACT_AXIS.width * (SPLIT_STANCE[i] ?? 0.5);
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
              <Artifact
                x={compactLaneX(i) + COMPACT_ARTIFACT.inset}
                y={COMPACT_ARTIFACT.top}
                width={COMPACT_ARTIFACT.width}
                height={COMPACT_ARTIFACT.height}
                frame={frame}
                at={at}
                index={i}
                count={KERNELS.length}
              />
              <Edge
                from={{
                  x: compactLaneCentreX(i),
                  y: LANE_TOP + COMPACT_LANE_HEIGHT,
                }}
                to={{ x: stanceX, y: COMPACT_AXIS.y }}
                progress={frame >= axisAt ? 1 : 0}
                opacity={0.6}
              />
              {/* Support sits above the axis, opposition below — form, not hue. */}
              <circle
                cx={stanceX}
                cy={COMPACT_AXIS.y}
                r={5}
                fill={(SPLIT_STANCE[i] ?? 0.5) > 0.5 ? "none" : COLOR.bone300}
                stroke={COLOR.bone300}
                strokeWidth={1}
                opacity={frame >= axisAt ? 1 : 0}
              />
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
        rules={CONTESTED_RULES}
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
        CONTESTED
      </Verdict>
    </>
  );
};

export const MovementVI: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(6);
  return (
    <Plate
      number={movement.index}
      total={MOVEMENT_COUNT}
      title={movement.name}
      question={movement.question}
      constructionTier="derive"
      durationInFrames={durationInFrames}
    >
      <Content />
    </Plate>
  );
};
