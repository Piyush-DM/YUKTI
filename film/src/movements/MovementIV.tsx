/**
 * MOVEMENT IV — ISOLATION
 * "What if no reader could see the others?"
 *
 * The teaching is an ABSENCE: no line connects any lane to any other, and the
 * viewer must be able to confirm it by looking. `Lane` has no prop that could
 * express an inter-lane connection.
 */

import { useCurrentFrame } from "remotion";
import { CANVAS, COLOR, SPACE, SURFACE } from "../system/tokens";
import { WORKING_AREA } from "../system/layout";
import { frames } from "../system/timing";
import { assertStructureBudget } from "../system/budgets";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Axis, Edge, Node } from "../primitives/Diagram";
import { IRGraph } from "../primitives/IRGraph";
import { Artifact } from "../primitives/Apparatus";
import { StructureLabel } from "../primitives/Typography";
import { KERNELS } from "../content/packet";
import { descend } from "../system/choreography";
import { MOVEMENT_COUNT, movementTiming } from "./shared";
import {
  ARTIFACT,
  AXIS,
  GRAPH_HEIGHT,
  LANE_HEIGHT,
  LANE_TOP,
  LANE_WIDTH,
  STANCE,
  laneCentreX,
  laneX,
} from "./laneGeometry";

const PLATE_LABEL = "IV Isolation";


const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;

  assertStructureBudget(KERNELS.length * 2, PLATE_LABEL);

  const laneAt = at + frames("build");
  const artifactAt = laneAt + frames("build");
  const axisAt = artifactAt + frames("build");

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        <IRGraph
          box={{
            x: WORKING_AREA.x,
            y: WORKING_AREA.y,
            width: WORKING_AREA.width,
            height: GRAPH_HEIGHT,
          }}
          frame={frame}
          at={at}
          showLabels={false}
          opacity={0.5}
        />

        {KERNELS.map((kernel, i) => {
          const x = laneX(i);
          const stanceX = AXIS.x + AXIS.width * (STANCE[i] ?? 0.5);
          const agreed = STANCE[i] === STANCE[0] && i <= 1;
          return (
            <g key={kernel}>
              {/* The same graph DESCENDS into each sealed lane. Four descents
                  of one object is the independence claim made visible: the
                  viewer watches identical input arrive in four places that
                  cannot see one another. */}
              <g
                transform={`translate(0, ${
                  descend({
                    frame,
                    at: laneAt,
                    fromY: -(LANE_TOP - WORKING_AREA.y),
                    toY: 0,
                    index: i,
                    count: KERNELS.length,
                  }).y
                })`}
              >
                <IRGraph
                  box={{
                    x: laneX(i) + ARTIFACT.inset,
                    y: LANE_TOP + SPACE.s4,
                    width: LANE_WIDTH - ARTIFACT.inset * 2,
                    height: 84,
                  }}
                  frame={frame}
                  at={laneAt}
                  showLabels={false}
                  opacity={0.55}
                  scale={0.34}
                />
              </g>

              <Node
                x={x}
                y={LANE_TOP}
                width={LANE_WIDTH}
                height={LANE_HEIGHT}
                state="established"
                opacity={0.45}
              />

              <Artifact
                x={x + ARTIFACT.inset}
                y={ARTIFACT.top + 48}
                width={ARTIFACT.width}
                height={ARTIFACT.height}
                frame={frame}
                at={artifactAt}
                index={i}
                count={KERNELS.length}
              />

              {/* Each lane drops its stance onto the shared axis. Lanes never
                  connect to one another — only downward, to the axis. */}
              <Edge
                from={{ x: laneCentreX(i), y: LANE_TOP + LANE_HEIGHT }}
                to={{ x: stanceX, y: AXIS.y }}
                progress={frame >= axisAt ? 1 : 0}
                opacity={0.6}
              />
              <circle
                cx={stanceX}
                cy={AXIS.y}
                r={5}
                fill={
                  agreed && frame >= beats.assertion.start
                    ? COLOR.yellow500
                    : COLOR.bone300
                }
                opacity={frame >= axisAt ? 1 : 0}
              />
            </g>
          );
        })}

        <Axis x={AXIS.x} y={AXIS.y} width={AXIS.width} />

        {/* The absence made explicit: the gaps between lanes carry nothing. */}
        {KERNELS.slice(0, -1).map((kernel, i) => (
          <line
            key={`gap-${kernel}`}
            x1={laneX(i) + LANE_WIDTH}
            y1={LANE_TOP + LANE_HEIGHT / 2}
            x2={laneX(i + 1)}
            y2={LANE_TOP + LANE_HEIGHT / 2}
            stroke={COLOR.hairlineDark}
            strokeWidth={SURFACE.hairline}
            strokeDasharray="1 7"
            opacity={0.4}
          />
        ))}
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
          <StructureLabel frame={frame} at={laneAt}>
            {kernel}
          </StructureLabel>
        </div>
      ))}
    </>
  );
};

export const MovementIV: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(4);
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
