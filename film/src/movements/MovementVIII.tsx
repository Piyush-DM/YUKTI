/**
 * MOVEMENT VIII — GENERALITY
 * "Does any of this depend on the subject?"
 *
 * The core is drawn ONCE, unduplicated, and every packet's lines enter it.
 * Drawing it four times would assert the opposite of the claim.
 */

import { useCurrentFrame } from "remotion";
import { CANVAS, COLOR, OPACITY, SPACE, SURFACE, TYPE } from "../system/tokens";
import { FAMILY } from "../system/fonts";
import { WORKING_AREA } from "../system/layout";
import { frames } from "../system/timing";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Edge, Node } from "../primitives/Diagram";
import { StructureLabel } from "../primitives/Typography";
import { DOMAINS } from "../content/packet";
import { MOVEMENT_COUNT, movementTiming } from "./shared";

const PACKET_ROW_Y = WORKING_AREA.y + SPACE.s5;
const PACKET_HEIGHT = 130;
const PACKET_GAP = SPACE.s6;
const PACKET_WIDTH =
  (WORKING_AREA.width - PACKET_GAP * (DOMAINS.length - 1)) / DOMAINS.length;

const packetX = (i: number): number =>
  WORKING_AREA.x + i * (PACKET_WIDTH + PACKET_GAP);

/** Packet shapes differ per domain — visibly different, per the end state. */
const PACKET_ROWS: readonly number[] = [4, 2, 5, 3];

const CORE = {
  width: 360,
  height: 96,
  x: WORKING_AREA.x + WORKING_AREA.width / 2 - 180,
  y: PACKET_ROW_Y + PACKET_HEIGHT + SPACE.s7,
} as const;

const Content: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;
  const coreAt = at + frames("build");
  const linkAt = coreAt + frames("mark");

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        {DOMAINS.map((domain, i) => {
          const x = packetX(i);
          const rows = PACKET_ROWS[i] ?? 3;
          return (
            <g key={domain.name}>
              <Node
                x={x}
                y={PACKET_ROW_Y}
                width={PACKET_WIDTH}
                height={PACKET_HEIGHT}
                state={domain.holdOut ? "unevaluated" : "established"}
              />
              {Array.from({ length: rows }, (_, r) => (
                <line
                  key={r}
                  x1={x + SPACE.s3}
                  y1={PACKET_ROW_Y + SPACE.s4 + r * SPACE.s3}
                  x2={x + PACKET_WIDTH - SPACE.s3 - (r % 2) * SPACE.s5}
                  y2={PACKET_ROW_Y + SPACE.s4 + r * SPACE.s3}
                  stroke={COLOR.bone300}
                  strokeWidth={SURFACE.hairline}
                  opacity={OPACITY.muted}
                />
              ))}
              <Edge
                from={{ x: x + PACKET_WIDTH / 2, y: PACKET_ROW_Y + PACKET_HEIGHT }}
                to={{ x: CORE.x + CORE.width / 2, y: CORE.y }}
                progress={frame >= linkAt ? 1 : 0}
                opacity={0.6}
              />
            </g>
          );
        })}

        {/* Drawn once. */}
        <g opacity={frame >= coreAt ? 1 : 0}>
          <Node
            x={CORE.x}
            y={CORE.y}
            width={CORE.width}
            height={CORE.height}
            state="established"
            filled
          />
        </g>
      </svg>

      {DOMAINS.map((domain, i) => (
        <div
          key={domain.name}
          style={{
            position: "absolute",
            left: packetX(i),
            top: PACKET_ROW_Y - 26,
          }}
        >
          <StructureLabel frame={frame} at={at}>
            {domain.holdOut ? `${domain.name} — hold-out` : domain.name}
          </StructureLabel>
        </div>
      ))}

      <div
        style={{
          position: "absolute",
          left: CORE.x,
          top: CORE.y - 26,
        }}
      >
        <StructureLabel frame={frame} at={coreAt}>
          shared core
        </StructureLabel>
      </div>

      <div
        style={{
          position: "absolute",
          left: CORE.x,
          top: CORE.y + CORE.height + SPACE.s4,
          fontFamily: FAMILY.data,
          fontSize: TYPE.data.size,
          fontVariantNumeric: TYPE.data.numeric,
          color:
            frame >= beats.assertion.start ? COLOR.yellow500 : COLOR.bone300,
          opacity: frame >= linkAt ? 1 : 0,
        }}
      >
        core changes required: 0
      </div>
    </>
  );
};

export const MovementVIII: React.FC = () => {
  const { movement, durationInFrames } = movementTiming(8);
  return (
    <Plate
      number={movement.index}
      total={MOVEMENT_COUNT}
      title={movement.name}
      question={movement.question}
      constructionTier="derive"
      durationInFrames={durationInFrames}
      camera={[
        { at: 0, state: "PLATE" },
        {
          at: 0,
          state: "INDEX",
          focus: {
            x: WORKING_AREA.x + WORKING_AREA.width / 2,
            y: (PACKET_ROW_Y + CORE.y + CORE.height) / 2,
          },
        },
      ]}
      cameraExemption={{
        rule: "C3",
        reason:
          "FILM_STRUCTURE.md Movement VIII End State is 'The camera has pulled " +
          "to INDEX', which is also Movement IX's verbatim Start State. Rule C3 " +
          "requires a return to PLATE before a transition. See TODO in camera.ts.",
      }}
    >
      <Content />
    </Plate>
  );
};
