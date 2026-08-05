/**
 * THE WORKED EXAMPLE
 *
 * Visual language §11.5: the film carries one real packet end to end.
 * `orbital-series-b` supplies the contested case (Movement VI); the thinner
 * packet supplies the declined case (Movement VII).
 *
 * Rule T1: every identifier below is a string the system would emit. Nothing
 * here is decorative.
 */

export type IRKind = "entity" | "claim" | "evidence";

export interface IRNode {
  readonly id: string;
  readonly kind: IRKind;
  /** Column index within its tier. */
  readonly slot: number;
  /** Present in the thin packet used by Movement VII. */
  readonly inThinPacket: boolean;
  /** Established in the thin packet, or merely reached. */
  readonly establishedInThinPacket: boolean;
}

export interface IRLink {
  readonly from: string;
  readonly to: string;
}

export const IR_NODES: readonly IRNode[] = [
  { id: "ENT-ORBITAL", kind: "entity", slot: 0, inThinPacket: true, establishedInThinPacket: true },
  { id: "ENT-MARKET", kind: "entity", slot: 1, inThinPacket: true, establishedInThinPacket: false },

  { id: "CLM-RUNWAY", kind: "claim", slot: 0, inThinPacket: true, establishedInThinPacket: false },
  { id: "CLM-REVENUE", kind: "claim", slot: 1, inThinPacket: true, establishedInThinPacket: false },
  { id: "CLM-BURN", kind: "claim", slot: 2, inThinPacket: true, establishedInThinPacket: false },
  { id: "CLM-POSITION", kind: "claim", slot: 3, inThinPacket: false, establishedInThinPacket: false },

  { id: "SRC-DECK", kind: "evidence", slot: 0, inThinPacket: true, establishedInThinPacket: true },
  { id: "SRC-AUDIT", kind: "evidence", slot: 1, inThinPacket: false, establishedInThinPacket: false },
  { id: "DP-ARR", kind: "evidence", slot: 2, inThinPacket: false, establishedInThinPacket: false },
  { id: "DP-BURN", kind: "evidence", slot: 3, inThinPacket: true, establishedInThinPacket: true },
  { id: "SRC-MKT", kind: "evidence", slot: 4, inThinPacket: false, establishedInThinPacket: false },
];

export const IR_LINKS: readonly IRLink[] = [
  { from: "SRC-DECK", to: "CLM-RUNWAY" },
  { from: "SRC-AUDIT", to: "CLM-REVENUE" },
  { from: "DP-ARR", to: "CLM-REVENUE" },
  { from: "DP-BURN", to: "CLM-BURN" },
  { from: "SRC-MKT", to: "CLM-POSITION" },
  { from: "CLM-RUNWAY", to: "ENT-ORBITAL" },
  { from: "CLM-POSITION", to: "ENT-MARKET" },
];

export const KERNELS = [
  "financial_posture",
  "risk_exposure",
  "market_position",
  "governance",
] as const;

/** Confidence step per kernel, full packet. Value steps, never hue. */
export const KERNEL_CONFIDENCE: Readonly<Record<string, 0 | 1 | 2>> = {
  financial_posture: 1,
  risk_exposure: 1,
  market_position: 2,
  governance: 1,
};

export const DERIVATION_LINES = [
  { rule: "rule 0", text: "inputs -- 2 evidence item(s), coverage 5/5 (100%), 0 contradiction(s)" },
  { rule: "rule 1", text: "evidence present -> continue" },
  { rule: "rule 2", text: "coverage 100% >= 50% minimum -> continue" },
  { rule: "rule 3", text: "weakest evidence is SRC-DECK (reported) -> start at moderate" },
  { rule: "rule 4", text: "no contradictions -> no downgrade" },
  { rule: "rule 5", text: "no coverage cap applied" },
] as const;

export const LIMITING_FACTOR = "weakest evidence is reported (SRC-DECK)";

export const RECORD_DIGEST =
  "4771ed0b3591289e75e66214f1fe1f02a63046800aa389d29be2cc66cebb580d";

export const DOMAINS = [
  { name: "investment", holdOut: false },
  { name: "law", holdOut: false },
  { name: "medicine", holdOut: false },
  { name: "engineering", holdOut: true },
] as const;
