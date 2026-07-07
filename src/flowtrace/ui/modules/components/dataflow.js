// 模块：方法数据流组件。负责渲染可点击的方法级参数传递图。
import { buildEdgeLanes, routeDirectedEdge } from "../graph/edge-router.js";
import { mountZoomableSurface } from "../graph/viewport.js";
import { escapeHtml } from "../utils/html.js";

const NODE_WIDTH = 190;
const NODE_HEIGHT = 34;
const COLUMN_GAP = 255;
const ROW_GAP = 92;
const CANVAS_PADDING_X = 96;
const CANVAS_PADDING_Y = 72;
const EDGE_LANE_GAP = 18;

export function renderDataflow(container, dataflow, onSelectEdge) {
  container.className = "animator-canvas";
  container.innerHTML = "";

  const graph = buildLayout(dataflow);
  if (!graph.nodes.length) {
    container.className = "animator-canvas empty";
    container.textContent = "暂无数据流边。";
    return;
  }

  const surface = document.createElement("div");
  surface.className = "animator-surface";
  surface.style.width = `${graph.width}px`;
  surface.style.height = `${graph.height}px`;
  surface.appendChild(renderEdges(graph.edges, graph.positions, onSelectEdge));

  for (const node of graph.nodes) {
    surface.appendChild(renderNode(node, graph.positions.get(node.id)));
  }

  mountZoomableSurface(container, surface, {
    width: graph.width,
    height: graph.height,
    storageKey: "flowtrace.zoom.dataflow.v1",
  });
}

function buildLayout(dataflow) {
  const nodes = withUserNodes(dataflow.nodes || [], dataflow.edges || []);
  const edges = dataflow.edges || [];
  const depthById = computeDepth(nodes, edges);
  const rowsByDepth = groupRows(nodes, depthById);
  const positions = new Map();

  let maxDepth = 0;
  let maxRows = 1;
  for (const [depth, depthNodes] of rowsByDepth.entries()) {
    maxDepth = Math.max(maxDepth, depth);
    maxRows = Math.max(maxRows, depthNodes.length);
    depthNodes.forEach((node, row) => {
      positions.set(node.id, {
        x: CANVAS_PADDING_X + depth * COLUMN_GAP,
        y: CANVAS_PADDING_Y + row * ROW_GAP,
      });
    });
  }

  return {
    nodes,
    edges,
    positions,
    width: CANVAS_PADDING_X * 2 + maxDepth * COLUMN_GAP + NODE_WIDTH,
    height: CANVAS_PADDING_Y * 2 + (maxRows - 1) * ROW_GAP + NODE_HEIGHT,
  };
}

function withUserNodes(nodes, edges) {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  for (const edge of edges) {
    if (!byId.has(edge.from)) {
      byId.set(edge.from, {
        id: edge.from,
        label: edge.from_label || "用户输入",
        kind: "user_action",
      });
    }
    if (!byId.has(edge.to)) {
      byId.set(edge.to, {
        id: edge.to,
        label: edge.to_label || "未知节点",
        kind: "unknown",
      });
    }
  }
  return [...byId.values()];
}

function computeDepth(nodes, edges) {
  const incoming = new Map(nodes.map((node) => [node.id, []]));
  for (const edge of edges) {
    incoming.get(edge.to)?.push(edge.from);
  }

  const depthById = new Map();
  const visit = (nodeId, seen = new Set()) => {
    if (depthById.has(nodeId)) {
      return depthById.get(nodeId);
    }
    if (seen.has(nodeId)) {
      return 0;
    }
    seen.add(nodeId);
    const parents = incoming.get(nodeId) || [];
    const depth = parents.length ? Math.max(...parents.map((parentId) => visit(parentId, new Set(seen)))) + 1 : 0;
    depthById.set(nodeId, depth);
    return depth;
  };

  for (const node of nodes) {
    visit(node.id);
  }
  return depthById;
}

function groupRows(nodes, depthById) {
  const rows = new Map();
  for (const node of nodes) {
    const depth = depthById.get(node.id) || 0;
    rows.set(depth, [...(rows.get(depth) || []), node]);
  }
  for (const depthNodes of rows.values()) {
    depthNodes.sort((a, b) => String(a.label).localeCompare(String(b.label)));
  }
  return rows;
}

function renderEdges(edges, positions, onSelectEdge) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.classList.add("edge-layer");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", "100%");
  svg.innerHTML = markerTemplate();

  const lanes = buildEdgeLanes(edges, EDGE_LANE_GAP);
  for (const edge of edges) {
    const from = positions.get(edge.from);
    const to = positions.get(edge.to);
    if (!from || !to) {
      continue;
    }
    const pathData = routeDirectedEdge(nodeRect(edge.from, from), nodeRect(edge.to, to), lanes.get(edge) || 0);
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathData);
    path.setAttribute("class", `flow-edge ${edgeClass(edge)}`);
    path.setAttribute("marker-end", "url(#arrowHead)");

    const hitPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
    hitPath.setAttribute("d", pathData);
    hitPath.setAttribute("class", "flow-edge-hit");
    hitPath.setAttribute("aria-label", `${edge.from_label || edge.from} 到 ${edge.to_label || edge.to}`);
    hitPath.addEventListener("click", () => onSelectEdge(edge));

    svg.appendChild(path);
    svg.appendChild(hitPath);
  }

  return svg;
}

function markerTemplate() {
  return `
    <defs>
      <marker id="arrowHead" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
        <path d="M 0 0 L 8 4 L 0 8 z" class="arrow-head"></path>
      </marker>
    </defs>
  `;
}

function nodeRect(id, position) {
  return {
    id,
    x: position.x,
    y: position.y,
    width: NODE_WIDTH,
    height: NODE_HEIGHT,
  };
}

function renderNode(node, position) {
  const button = document.createElement("button");
  button.className = `animator-node ${nodeClass(node)}`;
  button.style.left = `${position.x}px`;
  button.style.top = `${position.y}px`;
  button.innerHTML = `<span>${escapeHtml(node.label || node.id)}</span>`;
  return button;
}

function nodeClass(node) {
  if (node.kind === "user_action") {
    return "entry";
  }
  if ((node.input_validation || {}).status === "fail" || (node.validation || {}).status === "fail" || node.error) {
    return "error";
  }
  if ((node.input_validation || {}).status === "warn" || (node.validation || {}).status === "warn") {
    return "warn";
  }
  return "normal";
}

function edgeClass(edge) {
  const inputStatus = edge.downstream_input_validation?.status;
  const outputStatus = edge.validation?.status;
  if (edge.error || inputStatus === "fail" || outputStatus === "fail") {
    return "error";
  }
  if (inputStatus === "warn" || outputStatus === "warn") {
    return "warn";
  }
  return "normal";
}
