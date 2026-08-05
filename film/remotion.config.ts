import { Config } from "@remotion/cli/config";

/**
 * Remotion configuration — YUKTI CHOIR explainer film.
 *
 * Values here are render-pipeline settings only. Nothing in this file makes a
 * design decision; all approved design values live in `src/system/tokens.ts`.
 */

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// The film is flat colour, hairline linework and type. There is no photographic
// content, no gradient and no glow anywhere in the approved visual language
// (§1.5), so a high CRF would only cost bytes without adding fidelity — but
// hairlines and small mono type are exactly what aggressive compression
// destroys first. 18 is chosen to protect 1px strokes at 1920x1080.
Config.setCrf(18);

Config.setChromiumOpenGlRenderer("angle");
