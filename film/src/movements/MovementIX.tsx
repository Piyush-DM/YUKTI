/**
 * MOVEMENT IX — RECORD
 * "What remains?"
 *
 * The film's last teaching: nothing was deleted. Every defeated claim,
 * withdrawn position, unfired rule and unevaluated item is still here.
 *
 * NO YELLOW ANYWHERE. For eight movements yellow meant "this is what is being
 * claimed right now"; its absence is the closing statement. `Verdict` is
 * rendered with `asserted={false}` for that reason and no other.
 *
 * This plate deliberately carries more discrete elements than §8.3's parse
 * budget of 12. That budget protects a plate the viewer must READ; this plate
 * exists to be surveyed, and the density IS the content. Not asserted here on
 * purpose — flagged rather than silently bypassed.
 */

import { useCurrentFrame } from "remotion";
import { CANVAS, COLOR, OPACITY, SPACE, TYPE } from "../system/tokens";
import { FAMILY } from "../system/fonts";
import { WORKING_AREA, span } from "../system/layout";
import { frames } from "../system/timing";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Defeated, Node } from "../primitives/Diagram";
import { IRGraph } from "../primitives/IRGraph";
import { Artifact, Derivation, RuleList } from "../primitives/Apparatus";
import { StructureLabel } from "../primitives/Typography";
import { Verdict } from "../primitives/Verdict";
import { DERIVATION_LINES, KERNELS, RECORD_DIGEST } from "../content/packet";
import { CONTESTED_RULES } from "./MovementVI";
import { MOVEMENT_COUNT, movementTiming } from "./shared";

const GRAPH_BOX = {
  x: WORKING_AREA.x,
  y: WORKING_AREA.y,
  width: span(5),
  height: 210,
} as const;

const ARTIFACT_ROW_Y = GRAPH_BOX.y + GRAPH_BOX.height + SPACE.s5;
const ARTIFACT_W = 110;
const ARTIFACT_H = 66;

const DEFEATED_BOX = {
  x: WORKING_AREA.x + (ARTIFACT_W + SPACE.s3) * KERNELS.length,
  y: ARTIFACT_ROW_Y,
  width: ARTIFACT_W,
  height: ARTIFACT_H,
} as const;

const CASCADE_X = WORKING_AREA.x + span(6) + SPACE.s5;
const DERIVATION_X = WORKING_AREA.x;
const DERIVATION_Y = ARTIFACT_ROW_Y + ARTIFACT_H + SPACE.s5;

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;
  const laterAt = at + frames("mark");

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        <IRGraph
          box={GRAPH_BOX}
          frame={frame}
          at={at}
          showLabels={false}
          opacity={0.7}
        />

        {KERNELS.map((kernel, i) => (
          <Artifact
            key={kernel}
            x={WORKING_AREA.x + i * (ARTIFACT_W + SPACE.s3)}
            y={ARTIFACT_ROW_Y}
            width={ARTIFACT_W}
            height={ARTIFACT_H}
            frame={frame}
            at={laterAt}
            index={i}
            count={KERNELS.length}
          />
        ))}

        {/* Retained, not removed. */}
        <Defeated box={DEFEATED_BOX}>
          <Node
            x={DEFEATED_BOX.x}
            y={DEFEATED_BOX.y}
            width={DEFEATED_BOX.width}
            height={DEFEATED_BOX.height}
            state="established"
          />
        </Defeated>

        {/* Never evaluated, drawn rather than omitted. */}
        <Node
          x={DEFEATED_BOX.x + ARTIFACT_W + SPACE.s3}
          y={ARTIFACT_ROW_Y}
          width={ARTIFACT_W}
          height={ARTIFACT_H}
          state="unevaluated"
        />
      </svg>

      <div
        style={{ position: "absolute", left: WORKING_AREA.x, top: GRAPH_BOX.y - 26 }}
      >
        <StructureLabel frame={frame} at={at}>
          intermediate representation
        </StructureLabel>
      </div>

      <div
        style={{
          position: "absolute",
          left: WORKING_AREA.x,
          top: ARTIFACT_ROW_Y - 26,
        }}
      >
        <StructureLabel frame={frame} at={laterAt}>
          artifacts · defeated · unevaluated
        </StructureLabel>
      </div>

      <Derivation
        lines={DERIVATION_LINES}
        x={DERIVATION_X}
        y={DERIVATION_Y}
        frame={frame}
        at={laterAt}
      />

      <RuleList
        rules={CONTESTED_RULES}
        x={CASCADE_X}
        y={GRAPH_BOX.y}
        frame={frame}
        at={laterAt}
        suppressAssertion
      />

      {/* No yellow. */}
      <Verdict frame={frame} at={laterAt} asserted={false}>
        CONTESTED
      </Verdict>

      <div
        style={{
          position: "absolute",
          left: WORKING_AREA.x,
          top: CANVAS.height - 190,
          fontFamily: FAMILY.data,
          fontSize: TYPE.data.size,
          fontVariantNumeric: TYPE.data.numeric,
          color: COLOR.bone300,
          opacity: OPACITY.muted,
          whiteSpace: "nowrap",
        }}
      >
        {`record digest  ${RECORD_DIGEST}`}
      </div>
    </>
  );
};

export const MovementIX: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(9);
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
