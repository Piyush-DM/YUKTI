/**
 * IR GRAPH
 *
 * The canonical intermediate representation as drawn structure. Introduced in
 * Movement III and reused wherever the IR appears — the same layout function
 * serves every movement so the viewer sees the same graph, not a redrawing.
 */

import { FAMILY } from "../system/fonts";
import { COLOR, LAYER, OPACITY, SPACE, TYPE } from "../system/tokens";
import { Edge, Node, type MarkState } from "./Diagram";
import { buildProgress } from "./Construct";
import { IR_LINKS, IR_NODES, type IRKind, type IRNode } from "../content/packet";

const KIND_TIER: Record<IRKind, number> = { entity: 0, claim: 1, evidence: 2 };

/** Kinds are distinguished by form, never by hue (§9.2). */
const KIND_SIZE: Record<IRKind, { width: number; height: number }> = {
  entity: { width: 190, height: 52 },
  claim: { width: 150, height: 44 },
  evidence: { width: 120, height: 34 },
};

export interface IRGraphBox {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface PlacedNode extends IRNode {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

const tierCount = (kind: IRKind): number =>
  IR_NODES.filter((n) => n.kind === kind).length;

export const placeIRNodes = (
  box: IRGraphBox,
  scale = 1,
): readonly PlacedNode[] => {
  const tiers = 3;
  const tierGap = box.height / tiers;

  return IR_NODES.map((node) => {
    const base = KIND_SIZE[node.kind];
    const size = { width: base.width * scale, height: base.height * scale };
    const count = tierCount(node.kind);
    const laneWidth = box.width / count;
    return {
      ...node,
      width: size.width,
      height: size.height,
      x: box.x + node.slot * laneWidth + laneWidth / 2 - size.width / 2,
      y: box.y + KIND_TIER[node.kind] * tierGap + tierGap / 2 - size.height / 2,
    };
  });
};

const centreOf = (n: PlacedNode) => ({
  x: n.x + n.width / 2,
  y: n.y + n.height / 2,
});

export interface IRGraphProps {
  readonly box: IRGraphBox;
  readonly frame: number;
  readonly at: number;
  /** Per-node state override. Movement VII dashes what was never established. */
  readonly stateFor?: (node: PlacedNode) => MarkState;
  /** Uniform opacity, for movements that recede the graph. */
  readonly opacity?: number;
  readonly showLabels?: boolean;
  /**
   * Node scale. Required where the graph is drawn inside a narrow container —
   * an unscaled graph overflows its box and, in Movement IV, would visually
   * bridge lanes that must read as sealed.
   */
  readonly scale?: number;
}

export const IRGraph: React.FC<IRGraphProps> = ({
  box,
  frame,
  at,
  stateFor,
  opacity = OPACITY.full,
  showLabels = true,
  scale = 1,
}) => {
  const placed = placeIRNodes(box, scale);
  const byId = new Map(placed.map((n) => [n.id, n]));

  return (
    <g opacity={opacity}>
      {IR_LINKS.map((link, i) => {
        const from = byId.get(link.from);
        const to = byId.get(link.to);
        if (!from || !to) return null;
        const state = stateFor ? stateFor(from) : "established";
        return (
          <Edge
            key={`${link.from}->${link.to}`}
            from={centreOf(from)}
            to={centreOf(to)}
            state={state}
            progress={buildProgress({
              frame,
              at,
              index: i,
              count: IR_LINKS.length,
            })}
          />
        );
      })}

      {placed.map((node, i) => {
        const state = stateFor ? stateFor(node) : "established";
        const p = buildProgress({
          frame,
          at,
          index: i,
          count: placed.length,
        });
        return (
          <g key={node.id} opacity={p}>
            <Node
              x={node.x}
              y={node.y}
              width={node.width}
              height={node.height}
              state={state}
              filled={node.kind === "entity"}
            />
            {showLabels ? (
              <text
                x={node.x + SPACE.s2}
                y={node.y + node.height / 2 + TYPE.data.size / 3}
                fontFamily={FAMILY.data}
                fontSize={TYPE.data.size}
                fill={state === "asserted" ? COLOR.yellow500 : COLOR.bone300}
                opacity={state === "defeated" ? OPACITY.muted : OPACITY.full}
                style={{ zIndex: LAYER.data }}
              >
                {node.id}
              </text>
            ) : null}
          </g>
        );
      })}
    </g>
  );
};
