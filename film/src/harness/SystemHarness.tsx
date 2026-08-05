/**
 * SYSTEM HARNESS
 *
 * Equivalent of the website's `tokens.html` Step-1 verification harness: a
 * surface that exercises the foundation so it can be checked before any
 * movement is built on it.
 *
 * This is NOT a movement and never appears in the film. It renders no narrative
 * content and makes no design decision.
 */

import { useCurrentFrame } from "remotion";
import { CANVAS, COLOR, SPACE } from "../system/tokens";
import { VERDICT_LOCUS, WORKING_AREA, col, span } from "../system/layout";
import { Plate, usePlateBeats } from "../primitives/Plate";
import { Datum, Line, StructureLabel } from "../primitives/Typography";
import { Verdict } from "../primitives/Verdict";
import { Axis, Defeated, Edge, Lane, Node, confidenceTint } from "../primitives/Diagram";
import { buildProgress } from "../primitives/Construct";
import { buildPlateBeats } from "../primitives/Plate";

const SPECIMEN_STATES = [
  { label: "established", state: "established" as const },
  { label: "unevaluated", state: "unevaluated" as const },
  { label: "asserted", state: "asserted" as const },
];

const HarnessContent: React.FC = () => {
  const frame = useCurrentFrame();
  const beats = usePlateBeats();
  const at = beats.construction.start;

  const rowY = WORKING_AREA.y + 40;
  const nodeW = 150;
  const nodeH = 56;

  return (
    <>
      <svg
        width={CANVAS.width}
        height={CANVAS.height}
        viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
        style={{ position: "absolute", inset: 0 }}
      >
        {/* Mark states — form and value, never hue (§9.2) */}
        {SPECIMEN_STATES.map((s, i) => (
          <Node
            key={s.label}
            x={col(1) + i * (nodeW + SPACE.s4)}
            y={rowY}
            width={nodeW}
            height={nodeH}
            state={s.state}
            opacity={buildProgress({ frame, at, index: i, count: 4 })}
          />
        ))}

        {/* Defeated — Rule K1: dimmed and struck, never removed */}
        <Defeated
          box={{
            x: col(1) + 3 * (nodeW + SPACE.s4),
            y: rowY,
            width: nodeW,
            height: nodeH,
          }}
        >
          <Node
            x={col(1) + 3 * (nodeW + SPACE.s4)}
            y={rowY}
            width={nodeW}
            height={nodeH}
            state="established"
          />
        </Defeated>

        {/* Confidence as value steps on bone */}
        {([0, 1, 2] as const).map((step) => {
          const tint = confidenceTint(step);
          return (
            <rect
              key={step}
              x={col(1) + step * (90 + SPACE.s3)}
              y={rowY + 120}
              width={90}
              height={18}
              fill={tint.fill}
              opacity={tint.opacity * buildProgress({ frame, at, index: step, count: 3 })}
            />
          );
        })}

        {/* Axis + edge draw-on */}
        <Axis x={col(1)} y={rowY + 220} width={span(6)} />
        <Edge
          from={{ x: col(1), y: rowY + 260 }}
          to={{ x: col(1) + span(4), y: rowY + 260 }}
          progress={buildProgress({ frame, at, index: 0, count: 1 })}
        />

        {/* A sealed lane — no prop exists to connect it to another */}
        <Lane x={col(8)} y={WORKING_AREA.y} width={span(2)} height={340} />

        {/* Verdict locus marker — the fixed coordinates, shown for verification */}
        <line
          x1={VERDICT_LOCUS.x - 24}
          y1={VERDICT_LOCUS.y}
          x2={VERDICT_LOCUS.x - 8}
          y2={VERDICT_LOCUS.y}
          stroke={COLOR.hairlineDark}
          strokeWidth={1}
        />
      </svg>

      <div style={{ position: "absolute", left: col(1), top: rowY - 28 }}>
        <StructureLabel frame={frame} at={at}>
          mark states
        </StructureLabel>
      </div>

      <div style={{ position: "absolute", left: col(1), top: rowY + 92 }}>
        <StructureLabel frame={frame} at={at}>
          confidence — value steps, never hue
        </StructureLabel>
      </div>

      <div style={{ position: "absolute", left: col(8), top: WORKING_AREA.y - 28 }}>
        <StructureLabel frame={frame} at={at}>
          sealed lane
        </StructureLabel>
      </div>

      <div style={{ position: "absolute", left: col(1), top: rowY + 300 }}>
        <Line frame={frame} at={at} plate="harness">
          Inter body register. A human is explaining.
        </Line>
      </div>

      <div style={{ position: "absolute", left: col(1), top: rowY + 340 }}>
        <Datum frame={frame} at={at} source="ir">
          SRC-DECK · coverage 5/5 · moderate
        </Datum>
      </div>

      {/* The verdict locus, exercised. Not asserted: Rule F1 reserves the first
          yellow-on-a-refusal for Movement VII, and the harness must not spend
          it. */}
      <Verdict frame={frame} at={beats.assertion.start} asserted={false}>
        VERDICT_LOCUS
      </Verdict>
    </>
  );
};

export const SystemHarness: React.FC = () => (
  <Plate
    number={0}
    total={9}
    title="System Harness"
    question="Does the foundation render as specified?"
    constructionTier="derive"
  >
    <HarnessContent />
  </Plate>
);

export const HARNESS_DURATION = buildPlateBeats("derive", "holdRead").total;
