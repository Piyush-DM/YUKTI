/**
 * MASTER COMPOSITION
 *
 * Concatenates every built movement in registry order.
 *
 * The seam between movements is PERSIST by default (visual language §6.1): the
 * End State of one movement is the Start State of the next, so movements abut
 * with no bridging effect. `Series` places them end to end and introduces
 * nothing between them — Rule TR1.
 */

import { Series } from "remotion";
import { BUILT_MOVEMENTS } from "./movements";
import { movementTiming } from "./movements/shared";
import { movementByIndex } from "./registry/movements";

export const MASTER_DURATION = BUILT_MOVEMENTS.reduce(
  (acc, m) => acc + movementTiming(m.index).durationInFrames,
  0,
);

export const Master: React.FC = () => (
  <Series>
    {BUILT_MOVEMENTS.map(({ index, component: Movement }) => (
      <Series.Sequence
        key={movementByIndex(index).numeral}
        durationInFrames={movementTiming(index).durationInFrames}
      >
        <Movement />
      </Series.Sequence>
    ))}
  </Series>
);
