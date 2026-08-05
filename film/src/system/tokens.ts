/**
 * TOKEN SYSTEM
 *
 * Source of truth: `website/src/styles/tokens.design.css` and
 * `website/src/styles/tokens.motion.css`, which are themselves transcriptions
 * of `yukti-motion-system-v1.md` and `yukti-website-v1-architecture.md`.
 *
 * These values are TRANSCRIBED, not reinterpreted. If a value here ever needs
 * to differ from the CSS token layer, the Motion System is amended first (its
 * own Section 13 governance process), then the CSS, then this file.
 *
 * Visual language §0: "Values are referenced, never restated with different
 * numbers."
 *
 * RESOLVED CLAMPS
 * The CSS type scale uses clamp() against viewport width. The film renders at a
 * fixed 1920x1080, so every clamp is resolved here to its value at 1920px and
 * the arithmetic is shown. No clamp survives into the film.
 */

// ============================================================
// Canvas — render target, not a design decision
// ============================================================

export const CANVAS = {
  width: 1920,
  height: 1080,
  fps: 30,
} as const;

// ============================================================
// Colour — tokens.design.css §2.1
// ============================================================

export const COLOR = {
  /** Primary background. Warm-neutral near-black, not pure #000. */
  graphite900: "#14140f",
  /** Secondary/raised background, panels. */
  graphite700: "#1f1f18",

  /** Card surface, resting. Warm off-white, not clinical #fff. */
  bone100: "#f2efe6",
  /** Body text on dark backgrounds. Dimmed bone, not pure white. */
  bone300: "#d8d4c6",

  /** Body text on bone/light surfaces. */
  ink900: "#14140f",

  /**
   * The ONLY accent hue in v1.0 (architecture D14).
   * Visual language §1.4: yellow marks the assertion — the single thing the
   * frame is currently claiming. One assertion per frame.
   */
  yellow500: "#f5c400",
  yellow600: "#d9ac00",

  /** Background drafting linework — barely perceptible. */
  lineBlueprint: "rgba(242, 239, 230, 0.06)",
  /** Hairline border on graphite surfaces. */
  hairlineDark: "rgba(242, 239, 230, 0.14)",
  /** Hairline border on bone surfaces. */
  hairlineLight: "rgba(20, 20, 15, 0.14)",
} as const;

// ============================================================
// Typography — tokens.design.css §2.2
// ============================================================

export const FONT = {
  /**
   * Visual language §4.1: "This is a section of the argument." Plate titles
   * only. Söhne is a commercial licence and is NOT yet procured (architecture
   * D2 licensing note); the fallback stack below is correct and upgrades
   * silently when licensed files land.
   */
  display: '"Söhne", "Neue Haas Grotesk Display", ui-sans-serif, sans-serif',
  /** "A human is explaining." */
  body: '"Inter", ui-sans-serif, system-ui, sans-serif',
  /** "This is a literal value from the system." */
  data: '"IBM Plex Mono", ui-monospace, "SFMono-Regular", monospace',
} as const;

/**
 * Type scale, clamps resolved at 1920px viewport width.
 * 1rem = 16px throughout.
 */
export const TYPE = {
  /** clamp(2.5rem, 1.1rem + 9vw, 11.25rem) -> 17.6 + 172.8 = 190.4, capped 180 */
  mega: {
    size: 180,
    weight: 700,
    tracking: "-0.02em",
    lineHeight: 0.92,
  },
  /** clamp(2.75rem, 2rem + 4.5vw, 6rem) -> 32 + 86.4 = 118.4, capped 96 */
  display: {
    size: 96,
    weight: 700,
    tracking: "-0.02em",
    lineHeight: 1.0,
  },
  /** clamp(1.75rem, 1.4rem + 2vw, 2.75rem) -> 22.4 + 38.4 = 60.8, capped 44 */
  heading: {
    size: 44,
    weight: 600,
    tracking: "-0.01em",
    lineHeight: 1.2,
  },
  /** clamp(1rem, 0.95rem + 0.2vw, 1.125rem) -> 15.2 + 3.84 = 19.04, capped 18 */
  body: {
    size: 18,
    weight: 400,
    tracking: "0em",
    lineHeight: 1.6,
  },
  /** clamp(0.6875rem, 0.65rem + 0.1vw, 0.8125rem) -> 10.4 + 1.92 = 12.32 */
  label: {
    size: 12.32,
    weight: 500,
    tracking: "0.08em",
    lineHeight: 1.4,
  },
  /** clamp(0.75rem, 0.72rem + 0.1vw, 0.875rem) -> 11.52 + 1.92 = 13.44 */
  data: {
    size: 13.44,
    weight: 400,
    tracking: "0em",
    lineHeight: 1.5,
    /** Mandatory — tokens.design.css §2.2 data-register rule. */
    numeric: "tabular-nums" as const,
  },
} as const;

// ============================================================
// Spacing — tokens.design.css §2.3
// ============================================================

export const SPACE = {
  s1: 4,
  s2: 8,
  s3: 16,
  s4: 24,
  s5: 40,
  /** Scene-to-scene rhythm unit. */
  s6: 64,
  /** clamp(6rem, 4rem + 6vw, 8rem) -> 64 + 115.2 = 179.2, capped 128 */
  s7: 128,
} as const;

export const GRID = {
  columns: 12,
  gutter: SPACE.s4,
  /** clamp(1.25rem, 1rem + 2vw, 4rem) -> 16 + 38.4 = 54.4, capped 64 */
  margin: 64,
} as const;

// ============================================================
// Surface — tokens.design.css §2.4
// ============================================================

export const SURFACE = {
  /** Never a soft/pill radius. */
  radiusSm: 3,
  hairline: 1,
} as const;

/**
 * Visual language §1.3: grain is fixed to the frame, not to content.
 * Same SVG turbulence source as the website token layer.
 */
export const TEXTURE_GRAIN =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";

// ============================================================
// Opacity — tokens.motion.css §2.5
// ============================================================

export const OPACITY = {
  hidden: 0,
  /**
   * Visual language Rule K1: defeated / withdrawn material dims to this value
   * and REMAINS on screen. Nothing is ever deleted from the frame.
   */
  muted: 0.35,
  full: 1,
} as const;

// ============================================================
// Z-layers — visual language §8.1, four fixed layers
// ============================================================

export const LAYER = {
  /** 1 — Ground. Graphite, drafting grid, grain. Never changes. */
  ground: 1,
  /** 2 — Structure. Nodes, edges, lanes, containers. Bone hairlines. */
  structure: 2,
  /** 3 — Data. Literal values and identifiers. Mono. */
  data: 3,
  /** 4 — Assertion. The current claim. Yellow. */
  assertion: 4,
  /** Plate furniture (slug, question) sits above all content layers. */
  furniture: 5,
} as const;
