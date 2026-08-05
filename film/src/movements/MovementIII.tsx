/**
 * MOVEMENT III — STRUCTURE
 * "What if the material had a common form?"
 *
 * INHERIT: the box from Movement II opens and becomes the graph.
 * No conclusion is present anywhere on this plate.
 */

import { interpolate, useCurrentFrame } from "remotion";
import { CANVAS } from "../system/tokens";
import { WORKING_AREA } from "../system/layout";
import { EASE } from "../system/motion";
import { frames } from "../system/timing";
import { assertStructureBudget } from "../system/budgets";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Node } from "../primitives/Diagram";
import { IRGraph } from "../primitives/IRGraph";
import { StructureLabel } from "../primitives/Typography";
import { IR_NODES } from "../content/packet";
import { MOVEMENT_COUNT, movementTiming } from "./shared";

const PLATE_LABEL = "III Structure";

const BOX_WIDTH = 260;
const BOX_HEIGHT = 180;

const BOX = {
  x: WORKING_AREA.x + WORKING_AREA.width / 2 - BOX_WIDTH / 2,
  y: WORKING_AREA.y + WORKING_AREA.height / 2 - BOX_HEIGHT / 2,
} as const;

const TIER_LABELS = [
  { text: "entities", tier: 0 },
  { text: "claims", tier: 1 },
  { text: "evidence", tier: 2 },
];

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;

  assertStructureBudget(IR_NODES.length, PLATE_LABEL);

  // The box opens (transformation), then the graph builds. Sequential.
  const openAt = at;
  const boxOpacity = interpolate(
    frame,
    [openAt, openAt + frames("mark")],
    [1, 0],
    { easing: EASE.standard, extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const graphAt = openAt + frames("mark");
  const tierGap = WORKING_AREA.height / 3;

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        <g opacity={boxOpacity}>
          <Node
            x={BOX.x}
            y={BOX.y}
            width={BOX_WIDTH}
            height={BOX_HEIGHT}
            state="established"
            filled
          />
        </g>

        <IRGraph box={WORKING_AREA} frame={frame} at={graphAt} />
      </svg>

      {TIER_LABELS.map(({ text, tier }) => (
        <div
          key={text}
          style={{
            position: "absolute",
            left: WORKING_AREA.x,
            top: WORKING_AREA.y + tier * tierGap + tierGap / 2 - 46,
          }}
        >
          <StructureLabel frame={frame} at={beats.assertion.start}>
            {text}
          </StructureLabel>
        </div>
      ))}
    </>
  );
};

export const MovementIII: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(3);
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
