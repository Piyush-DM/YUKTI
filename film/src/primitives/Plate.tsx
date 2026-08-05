/**
 * PLATE SYSTEM — visual language §3.1 and §5
 *
 * "One plate = one question = one answer."
 *
 * Every plate follows the same six beats. Motion System §1.6: predictability is
 * a trust feature — "a user who has seen one panel open has effectively seen
 * all of them open". The template is therefore fixed here rather than
 * re-choreographed per plate.
 *
 *   1 Slug          mark        plate number and title appear
 *   2 Question      build       the question this plate answers
 *   3 Construction  build|derive the structure assembles
 *   4 Hold          holdRead    complete stillness
 *   5 Assertion     mark        yellow marks the claim
 *   6 Resolve       mark        assertion clears; structure persists
 */

import { createContext, useContext, type ReactNode } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { CANVAS, LAYER } from "../system/tokens";
import { QUESTION_ORIGIN, SLUG_ORIGIN } from "../system/layout";
import { sequence, totalFrames, type Beat, type TierName } from "../system/timing";
import {
  assertCameraRules,
  cameraTransform,
  type CameraKeyframe,
  type CameraRuleExemption,
  type FrameWindow,
} from "../system/camera";
import { Ground } from "./Ground";
import { Question, Slug } from "./Typography";

// ============================================================
// Beat context
// ============================================================

export interface PlateBeats {
  readonly slug: Beat;
  readonly question: Beat;
  readonly construction: Beat;
  readonly hold: Beat;
  readonly assertion: Beat;
  readonly resolve: Beat;
  readonly total: number;
}

const PlateContext = createContext<PlateBeats | null>(null);

/** Read the current plate's beat schedule. Throws outside a Plate. */
export const usePlateBeats = (): PlateBeats => {
  const ctx = useContext(PlateContext);
  if (!ctx) {
    throw new Error("usePlateBeats must be called inside a <Plate>.");
  }
  return ctx;
};

export const buildPlateBeats = (
  constructionTier: TierName,
  holdTier: "holdRead" | "holdWeight",
  totalDuration?: number,
): PlateBeats => {
  const [slug, question, construction, hold, assertion, resolve] = sequence([
    ["slug", "mark"],
    ["question", "build"],
    ["construction", constructionTier],
    ["hold", holdTier],
    ["assertion", "mark"],
    ["resolve", "mark"],
  ]) as [Beat, Beat, Beat, Beat, Beat, Beat];

  const base = totalFrames([slug, question, construction, hold, assertion, resolve]);

  // A movement's length comes from its approved proportional weight; the
  // six-beat template supplies the ORDER. Where the weight exceeds the
  // template's natural length the surplus is absorbed by the hold, because
  // Rule M2 states holds as a MINIMUM ("at least holdRead") and stillness is
  // the approved place for extra time. Every other beat keeps its tier.
  const surplus = totalDuration === undefined ? 0 : Math.max(0, totalDuration - base);
  if (surplus === 0) {
    return {
      slug,
      question,
      construction,
      hold,
      assertion,
      resolve,
      total: base,
    };
  }

  const heldHold: Beat = {
    ...hold,
    duration: hold.duration + surplus,
    end: hold.end + surplus,
  };
  const shiftedAssertion: Beat = {
    ...assertion,
    start: assertion.start + surplus,
    end: assertion.end + surplus,
  };
  const shiftedResolve: Beat = {
    ...resolve,
    start: resolve.start + surplus,
    end: resolve.end + surplus,
  };

  return {
    slug,
    question,
    construction,
    hold: heldHold,
    assertion: shiftedAssertion,
    resolve: shiftedResolve,
    total: base + surplus,
  };
};

// ============================================================
// Plate
// ============================================================

export interface PlateProps {
  readonly number: number;
  readonly total: number;
  /** Slug title. Uppercased on render. */
  readonly title: string;
  /** Rule S1: printed on screen, must end in "?". */
  readonly question: string;
  /**
   * Beat 3 duration. `build` for a structure assembling, `derive` for a value
   * being derived (visual language §2.2).
   */
  readonly constructionTier?: TierName;
  /**
   * Rule M2: at least `holdRead`. `holdWeight` for the film's key claims.
   */
  readonly holdTier?: "holdRead" | "holdWeight";
  /** Movement length from its approved weight. Surplus is absorbed by the hold. */
  readonly durationInFrames?: number;
  /** Rule C2: at most one move. Rule C3: must end on PLATE. */
  readonly camera?: readonly CameraKeyframe[];
  /** Rule C1: declared so camera moves can be checked against them. */
  readonly buildWindows?: readonly FrameWindow[];
  /** Declared, reasoned exemption. See camera.ts TODO. */
  readonly cameraExemption?: CameraRuleExemption;
  readonly children?: ReactNode;
}

export const Plate: React.FC<PlateProps> = ({
  number,
  total,
  title,
  question,
  constructionTier = "build",
  holdTier = "holdRead",
  durationInFrames,
  camera = [{ at: 0, state: "PLATE" }],
  buildWindows = [],
  cameraExemption,
  children,
}) => {
  const frame = useCurrentFrame();
  const beats = buildPlateBeats(constructionTier, holdTier, durationInFrames);

  // Approved rules are checked at render time so a violation fails in the
  // Studio rather than surviving to review.
  assertCameraRules(camera, buildWindows, `${number} ${title}`, cameraExemption);

  return (
    <PlateContext.Provider value={beats}>
      <AbsoluteFill style={{ width: CANVAS.width, height: CANVAS.height }}>
        {/* Layer 1 — ground. Outside the camera: the drafting surface does not
            zoom, only the drawing on it does. */}
        <Ground />

        {/* Layers 2-4 — structure, data, assertion. Under the camera. */}
        <AbsoluteFill
          style={{
            transform: cameraTransform(camera, frame),
            transformOrigin: "0 0",
            zIndex: LAYER.structure,
          }}
        >
          {children}
        </AbsoluteFill>

        {/* Layer 5 — plate furniture. Outside the camera: the slug and the
            question are the reader's fixed reference points and must not move
            when the drawing is inspected. */}
        <AbsoluteFill style={{ zIndex: LAYER.furniture }}>
          <div
            style={{
              position: "absolute",
              left: QUESTION_ORIGIN.x,
              top: QUESTION_ORIGIN.y,
              maxWidth: QUESTION_ORIGIN.maxWidth,
            }}
          >
            <Question frame={frame} at={beats.question.start}>
              {question}
            </Question>
          </div>

          <div
            style={{
              position: "absolute",
              left: SLUG_ORIGIN.x,
              top: SLUG_ORIGIN.y,
              transform: "translateY(-100%)",
            }}
          >
            <Slug
              plate={number}
              total={total}
              title={title.toUpperCase()}
              frame={frame}
              at={beats.slug.start}
            />
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    </PlateContext.Provider>
  );
};
