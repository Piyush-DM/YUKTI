/*
  YUKTI Website — Motion Constants (JS-side)
  Source of truth: yukti-motion-system-v1.md, Section 2.4 (Spring Constant)

  The spring model is physics-driven, not curve-driven, so it cannot live in
  CSS as a token — it is a per-frame computation. This module is the single
  place that constant is defined; canvas/visualization code imports it rather
  than hard-coding 0.06 / 0.04 inline (Section 2.3's "no magic numbers" rule
  applies to JS as much as CSS).
*/

export const SPRING_K_ACTIVE = 0.06; // cluster re-grouping (evidence graph, source map)
export const SPRING_K_IDLE = 0.04;   // idle ambient drift — slower, calmer, "settled" not "searching"

export const COUNT_STEPS = 45;
export const COUNT_STEP_MS = 24; // COUNT_STEPS * COUNT_STEP_MS ≈ --yukti-duration-count (1080ms)

export const REVEAL_IO_THRESHOLD = 0.12;
export const REVEAL_STAGGER_SLOTS = 4;
export const REVEAL_STAGGER_STEP_MS = 60;

export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}
