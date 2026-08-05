/**
 * MOVEMENT I — VOLUME
 * "What does an institution decide from?"
 */

import { useCurrentFrame } from "remotion";
import { CANVAS } from "../system/tokens";
import { WORKING_AREA } from "../system/layout";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Datum } from "../primitives/Typography";
import { DocumentField } from "../primitives/Apparatus";
import { COUNT_ANCHOR, MOVEMENT_COUNT, movementTiming } from "./shared";

const FIELD_COLUMNS = 24;
const FIELD_ROWS = 14;
const DOCUMENT_COUNT = FIELD_COLUMNS * FIELD_ROWS;

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();

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
          at={beats.construction.start}
        />
      </svg>

      <div
        style={{
          position: "absolute",
          right: COUNT_ANCHOR.right,
          top: COUNT_ANCHOR.top,
        }}
      >
        <Datum frame={frame} at={beats.assertion.start} source="ir">
          {`${DOCUMENT_COUNT} source documents`}
        </Datum>
      </div>
    </>
  );
};

export const MovementI: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(1);
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
