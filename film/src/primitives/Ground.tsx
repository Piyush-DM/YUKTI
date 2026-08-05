/**
 * GROUND — layer 1 of the information hierarchy (visual language §8.1).
 *
 * "Graphite, drafting grid, grain. Never changes for the entire film."
 *
 * This component renders once, behind everything, and is deliberately inert.
 * It has no props that vary over time because §8.1 says it never changes — the
 * absence of animation here is the specification, not an omission.
 *
 * §1.3: the grid is static and never parallaxes; grain is fixed to the frame,
 * not to content.
 */

import { AbsoluteFill } from "remotion";
import { CANVAS, COLOR, LAYER, TEXTURE_GRAIN } from "../system/tokens";

/** Drafting grid pitch. One 12-column gutter unit, squared. */
const GRID_PITCH = 40;

export const Ground: React.FC = () => (
  <AbsoluteFill style={{ zIndex: LAYER.ground }}>
    {/* Flat graphite. Never a gradient, never a vignette (§1.3). */}
    <AbsoluteFill style={{ backgroundColor: COLOR.graphite900 }} />

    {/* Drafting linework at 6% bone — barely perceptible, static. */}
    <svg
      width={CANVAS.width}
      height={CANVAS.height}
      viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`}
      style={{ position: "absolute", inset: 0 }}
    >
      <defs>
        <pattern
          id="drafting-grid"
          width={GRID_PITCH}
          height={GRID_PITCH}
          patternUnits="userSpaceOnUse"
        >
          <path
            d={`M ${GRID_PITCH} 0 L 0 0 0 ${GRID_PITCH}`}
            fill="none"
            stroke={COLOR.lineBlueprint}
            strokeWidth={1}
          />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#drafting-grid)" />
    </svg>

    {/* Grain, fixed to the frame. */}
    <AbsoluteFill
      style={{
        backgroundImage: TEXTURE_GRAIN,
        opacity: 0.035,
        mixBlendMode: "overlay",
      }}
    />
  </AbsoluteFill>
);
