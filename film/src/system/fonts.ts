/**
 * FONT LOADING
 *
 * Architecture D2 (final): Display Söhne · Body/UI Inter · Data IBM Plex Mono.
 *
 * Inter and IBM Plex Mono are open-licensed (SIL OFL) and are loaded here.
 *
 * SÖHNE IS NOT LOADED. It is a commercial licence from Klim Type Foundry and
 * the files have not been procured (architecture §0.1, D2 licensing note;
 * visual language §11.4). Until they exist, `FONT.display` resolves through its
 * documented fallback stack. This is a PROCUREMENT dependency, not a design
 * question — the token layer is already correct and upgrades silently the
 * moment licensed files land.
 *
 * Consequence for the film: plate titles currently render in a substitute face.
 * See IMPLEMENTATION_NOTES.md, note 3.
 */

import { FONT } from "./tokens";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadPlexMono } from "@remotion/google-fonts/IBMPlexMono";

const inter = loadInter("normal", {
  weights: ["400", "500", "600", "700"],
  subsets: ["latin"],
});

const plexMono = loadPlexMono("normal", {
  weights: ["400", "500"],
  subsets: ["latin"],
});

/**
 * Resolved family names, for use where the token stack must be overridden with
 * the actually-loaded face. The tokens remain the source of truth for the
 * fallback chain; these are prepended to it.
 */
export const LOADED = {
  body: inter.fontFamily,
  data: plexMono.fontFamily,
} as const;

/**
 * The stacks components actually render with: the loaded face first, the
 * approved token stack behind it unchanged.
 *
 * `display` is the token stack alone — there is no loaded Söhne to prepend.
 */
export const FAMILY = {
  display: FONT.display,
  body: `${LOADED.body}, ${FONT.body}`,
  data: `${LOADED.data}, ${FONT.data}`,
} as const;

export const fontsReady = (): Promise<void> =>
  Promise.all([inter.waitUntilDone(), plexMono.waitUntilDone()]).then(
    () => undefined,
  );
