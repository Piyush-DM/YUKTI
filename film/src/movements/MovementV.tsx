/**
 * MOVEMENT V — DERIVATION
 * "Where does confidence come from?"
 *
 * PERSIST from IV: the same lanes, in the same positions. The bands are new;
 * the apparatus is not.
 *
 * Two properties must be legible without narration: the band takes the WEAKEST
 * evidence item, and the institutional band takes the MINIMUM across lanes.
 */

import { useCurrentFrame } from "remotion";
import { CANVAS, COLOR, SPACE, TYPE } from "../system/tokens";
import { FAMILY } from "../system/fonts";
import { WORKING_AREA } from "../system/layout";
import { frames } from "../system/timing";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Node } from "../primitives/Diagram";
import { Artifact, ConfidenceBand, Derivation } from "../primitives/Apparatus";
import { settleFloor } from "../system/choreography";
import { StructureLabel } from "../primitives/Typography";
import {
  DERIVATION_LINES,
  KERNELS,
  KERNEL_CONFIDENCE,
  LIMITING_FACTOR,
} from "../content/packet";
import { MOVEMENT_COUNT, movementTiming } from "./shared";
import {
  ARTIFACT,
  LANE_HEIGHT,
  LANE_TOP,
  LANE_WIDTH,
  laneX,
} from "./laneGeometry";

const BASELINE_Y = LANE_TOP + LANE_HEIGHT - SPACE.s4;
const DERIVATION_TOP = LANE_TOP + LANE_HEIGHT + SPACE.s6;
const COLUMN_WIDTH = 46;

const stepFor = (kernel: string): 0 | 1 | 2 => KERNEL_CONFIDENCE[kernel] ?? 1;

/**
 * Rest heights. A stronger band stands taller; the institutional band is the
 * FLOOR the tallest cannot lift. Nothing here asserts "minimum" — the columns
 * fall and the lowest one is simply where the floor ends up.
 */
const COLUMN_HEIGHTS = KERNELS.map((k) => 96 - stepFor(k) * 30);

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;

  const bandAt = at + frames("build");
  const institutionalAt = bandAt + frames("derive");

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        {KERNELS.map((kernel, i) => (
          <g key={kernel}>
            <Node
              x={laneX(i)}
              y={LANE_TOP}
              width={LANE_WIDTH}
              height={LANE_HEIGHT}
              state="established"
              opacity={0.45}
            />
            <Artifact
              x={laneX(i) + ARTIFACT.inset}
              y={ARTIFACT.top}
              width={ARTIFACT.width}
              height={ARTIFACT.height}
              frame={frame}
              at={at}
              index={i}
              count={KERNELS.length}
            />
            <ConfidenceBand
              x={laneX(i) + ARTIFACT.inset}
              baselineY={BASELINE_Y}
              width={COLUMN_WIDTH}
              step={stepFor(kernel)}
              heights={COLUMN_HEIGHTS}
              index={i}
              frame={frame}
              at={bandAt}
            />
          </g>
        ))}

        {/* The floor, drawn where the columns came to rest. It is discovered,
            not declared: its height is min(COLUMN_HEIGHTS) by construction. */}
        <line
          x1={WORKING_AREA.x}
          y1={BASELINE_Y - settleFloor(COLUMN_HEIGHTS, { frame, at: institutionalAt })}
          x2={WORKING_AREA.x + LANE_WIDTH * 4}
          y2={BASELINE_Y - settleFloor(COLUMN_HEIGHTS, { frame, at: institutionalAt })}
          stroke={COLOR.bone300}
          strokeWidth={1}
          strokeDasharray="4 4"
          opacity={0.6}
        />
        <line
          x1={WORKING_AREA.x}
          y1={BASELINE_Y}
          x2={WORKING_AREA.x + LANE_WIDTH * 4}
          y2={BASELINE_Y}
          stroke={COLOR.hairlineDark}
          strokeWidth={1}
        />
      </svg>

      {KERNELS.map((kernel, i) => (
        <div
          key={kernel}
          style={{
            position: "absolute",
            left: laneX(i) + ARTIFACT.inset,
            top: LANE_TOP + SPACE.s3,
          }}
        >
          <StructureLabel frame={frame} at={at}>
            {kernel}
          </StructureLabel>
        </div>
      ))}

      <div
        style={{
          position: "absolute",
          left: WORKING_AREA.x + LANE_WIDTH * 4 + SPACE.s3,
          top: BASELINE_Y - settleFloor(COLUMN_HEIGHTS, { frame, at: institutionalAt }) - 8,
        }}
      >
        <StructureLabel frame={frame} at={institutionalAt}>
          institutional floor
        </StructureLabel>
      </div>

      <Derivation
        lines={DERIVATION_LINES}
        x={laneX(1)}
        y={DERIVATION_TOP}
        frame={frame}
        at={bandAt}
        limitingFactor={LIMITING_FACTOR}
        limitAt={beats.assertion.start}
      />

      <div
        style={{
          position: "absolute",
          left: laneX(1),
          top: DERIVATION_TOP - 24,
          fontFamily: FAMILY.data,
          fontSize: TYPE.data.size,
          color: COLOR.bone300,
          opacity: 0.5,
        }}
      >
        CONFIDENCE DERIVATION
      </div>
    </>
  );
};

export const MovementV: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(5);
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
