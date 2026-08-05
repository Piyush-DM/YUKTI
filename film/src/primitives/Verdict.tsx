/**
 * THE VERDICT LOCUS
 *
 * FILM_STRUCTURE.md, "The frame":
 *
 *   "INSUFFICIENT_BASIS, in yellow mono, at the exact coordinates where every
 *    previous verdict has appeared — beneath a fully intact apparatus, with
 *    five decision rules greyed and never reached."
 *
 *   "It is a substitution, not a reveal: its power comes entirely from
 *    something else having occupied that position six times before."
 *
 * This component is the only sanctioned way to render a conclusion. It takes no
 * position props, because the position is not a per-plate decision — it is
 * `VERDICT_LOCUS` in `system/layout.ts`, fixed for the whole film.
 *
 * If a plate seems to need its verdict somewhere else, that is an
 * implementation note, not a local override.
 */

import { FAMILY } from "../system/fonts";
import { COLOR, LAYER, TYPE } from "../system/tokens";
import { VERDICT_LOCUS } from "../system/layout";
import { deliver } from "../system/choreography";

export interface VerdictProps {
  /**
   * The conclusion string exactly as the system emits it.
   * Rule T1: this must be a real system output, never a paraphrase.
   */
  readonly children: string;
  readonly frame: number;
  readonly at?: number;
  /**
   * Whether this verdict is the frame's assertion.
   *
   * Rule F1: no yellow may mark an absence anywhere before Movement VII. A
   * verdict that IS present (Movement II's unattributed answer, VI's CONTESTED)
   * is asserted normally. VII's refusal is the first time yellow lands on a
   * declared non-conclusion, and that first use is the payoff.
   */
  readonly asserted?: boolean;
  /**
   * Where the conclusion travels FROM. Every verdict in the film takes this
   * route into the locus, so the eye learns the path — and Movement VII's
   * refusal reads as the same journey with a different arrival, not as a
   * different graphic. Omit only where nothing is being concluded (Movement IX).
   */
  readonly deliverFrom?: { readonly x: number; readonly y: number };
}

export const Verdict: React.FC<VerdictProps> = ({
  children,
  frame,
  at = 0,
  asserted = true,
  deliverFrom,
}) => {
  const travel = deliverFrom
    ? deliver({
        frame,
        at,
        fromX: deliverFrom.x - VERDICT_LOCUS.x,
        fromY: deliverFrom.y - VERDICT_LOCUS.y,
        toX: 0,
        toY: 0,
      })
    : { x: 0, y: 0, arrived: true };

  return (
  <div
    style={{
      position: "absolute",
      left: VERDICT_LOCUS.x,
      top: VERDICT_LOCUS.y,
      transform: `translate3d(${travel.x}px, ${travel.y}px, 0)`,
      maxWidth: VERDICT_LOCUS.maxWidth,
      fontFamily: FAMILY.data,
      fontSize: TYPE.display.size * 0.34,
      fontWeight: TYPE.data.weight,
      letterSpacing: "0.04em",
      lineHeight: 1.2,
      fontVariantNumeric: TYPE.data.numeric,
      color: asserted ? COLOR.yellow500 : COLOR.bone300,
      zIndex: asserted ? LAYER.assertion : LAYER.data,
      opacity: frame >= at ? 1 : 0,
    }}
  >
    {children}
  </div>
  );
};
