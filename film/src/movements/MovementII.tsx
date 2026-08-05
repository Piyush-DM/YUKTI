/**
 * MOVEMENT II — OPACITY
 * "What happens when one process reads all of it?"
 *
 * Installs the verdict locus. Every conclusion from here on is placed at the
 * same coordinates; the memorable frame in VII is a substitution at this
 * position.
 */

import { interpolate, useCurrentFrame } from "remotion";
import { CANVAS, SPACE } from "../system/tokens";
import { VERDICT_LOCUS, WORKING_AREA } from "../system/layout";
import { EASE } from "../system/motion";
import { frames } from "../system/timing";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Edge, Node } from "../primitives/Diagram";
import { DocumentField } from "../primitives/Apparatus";
import { Verdict } from "../primitives/Verdict";
import { MOVEMENT_COUNT, movementTiming } from "./shared";

const FIELD_COLUMNS = 24;
const FIELD_ROWS = 14;

const BOX_WIDTH = 260;
const BOX_HEIGHT = 180;

const BOX = {
  x: WORKING_AREA.x + WORKING_AREA.width / 2 - BOX_WIDTH / 2,
  y: WORKING_AREA.y + WORKING_AREA.height / 2 - BOX_HEIGHT / 2,
  width: BOX_WIDTH,
  height: BOX_HEIGHT,
} as const;

const BOX_CENTRE = {
  x: BOX.x + BOX.width / 2,
  y: BOX.y + BOX.height / 2,
} as const;

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;

  // Beat 3 runs two sequential motions, never simultaneous (Rule M1):
  // the field collapses (transport), then the box and its line appear.
  const collapse = interpolate(
    frame,
    [at, at + frames("derive")],
    [0, 1],
    { easing: EASE.standard, extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const boxAt = at + frames("derive");
  const boxOpacity = interpolate(
    frame,
    [boxAt, boxAt + frames("mark")],
    [0, 1],
    { easing: EASE.standard, extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const lineAt = boxAt + frames("mark");
  const lineProgress = interpolate(
    frame,
    [lineAt, lineAt + frames("build")],
    [0, 1],
    { easing: EASE.standard, extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        <DocumentField
          x={WORKING_AREA.x}
          y={WORKING_AREA.y}
          width={WORKING_AREA.width}
          height={WORKING_AREA.height}
          columns={FIELD_COLUMNS}
          rows={FIELD_ROWS}
          frame={frame}
          at={at}
          opacity={1 - collapse}
          collapse={collapse}
          collapseTo={BOX_CENTRE}
        />

        <g opacity={boxOpacity}>
          <Node
            x={BOX.x}
            y={BOX.y}
            width={BOX.width}
            height={BOX.height}
            state="established"
            filled
          />
        </g>

        <Edge
          from={{ x: BOX.x + BOX.width / 2, y: BOX.y + BOX.height }}
          to={{ x: VERDICT_LOCUS.x + SPACE.s2, y: VERDICT_LOCUS.y }}
          progress={lineProgress}
        />
      </svg>

      <Verdict
        frame={frame}
        at={beats.assertion.start}
        deliverFrom={{ x: BOX_CENTRE.x, y: BOX.y + BOX.height }}
      >
        PROCEED
      </Verdict>
    </>
  );
};

export const MovementII: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(2);
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
