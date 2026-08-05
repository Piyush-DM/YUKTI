import type { ComponentType } from "react";
import { MovementI } from "./MovementI";
import { MovementII } from "./MovementII";
import { MovementIII } from "./MovementIII";
import { MovementIV } from "./MovementIV";
import { MovementV } from "./MovementV";
import { MovementVI } from "./MovementVI";
import { MovementVII } from "./MovementVII";
import { MovementVIII } from "./MovementVIII";
import { MovementIX } from "./MovementIX";

export interface RegisteredMovement {
  readonly index: number;
  readonly component: ComponentType;
}

/**
 * Movements built so far. Phase 3 appends one at a time; `Root` and the master
 * composition both read from here so neither can drift from the other.
 */
export const BUILT_MOVEMENTS: readonly RegisteredMovement[] = [
  { index: 1, component: MovementI },
  { index: 2, component: MovementII },
  { index: 3, component: MovementIII },
  { index: 4, component: MovementIV },
  { index: 5, component: MovementV },
  { index: 6, component: MovementVI },
  { index: 7, component: MovementVII },
  { index: 8, component: MovementVIII },
  { index: 9, component: MovementIX },
];
