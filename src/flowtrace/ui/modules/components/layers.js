// 模块：层级流转组件。负责渲染可移动的项目层级节点和层级内方法小窗。
import { buildEdgeLanes, routeDirectedEdge } from "../graph/edge-router.js";
import { mountZoomableSurface } from "../graph/viewport.js";
import { escapeHtml } from "../utils/html.js";

const NODE_WIDTH = 210;
const NODE_HEIGHT = 64;
const COLUMN_GAP = 270;
const ROW_GAP = 112;
const CANVAS_PADDING_X = 96;
const CANVAS_PADDING_Y = 76;
const EDGE_LANE_GAP = 22;
const INSPECTOR_WIDTH = 380;
const INSPECTOR_GAP = 22;

export function renderLayerFlow(container, layerFlow, savedPositions, onSelectEdge, onSelectMethod, onWatchMethod, onLayoutChange) {
  container.className = "animator-canvas";
  container.innerHTML = "";

  const graph = buildLayout(layerFlow, savedPositions);
  if (!graph.nodes.length) {
    container.className = "animator-canvas empty";
    container.textContent = "暂无层级流转。";
    return;
  }

  const surface = document.createElement("div");
  surface.className = "animator-surface layer-surface";
  surface.style.width = `${graph.width}px`;
  surface.style.height = `${graph.height}px`;

  const edgeLayer = renderEdges(graph.edges, graph.positions, onSelectEdge);
  surface.appendChild(edgeLayer.svg);
  const viewport = mountZoomableSurface(container, surface, {
    width: graph.width,
    height: graph.height,
    storageKey: "flowtrace.zoom.layers.v1",
  });

  for (const node of graph.nodes) {
    const button = renderLayerNode(node, graph.positions.get(node.id));
    installDrag(button, node, graph.positions, savedPositions, edgeLayer.redraw, onLayoutChange, viewport.getScale);
    button.addEventListener("dblclick", () => {
      renderLayerInspector(surface, node, graph.positions.get(node.id), graph.edges, onSelectMethod, onWatchMethod);
    });
    surface.appendChild(button);
  }
}

function buildLayout(layerFlow, savedPositions) {
  const nodes = layerFlow.nodes || [];
  const edges = layerFlow.edges || [];
  const depthById = computeDepth(nodes, edges);
  const rowsByDepth = groupRows(nodes, depthById);
  const positions = new Map();

  let maxDepth = 0;
  let maxRows = 1;
  for (const [depth, depthNodes] of rowsByDepth.entries()) {
    maxDepth = Math.max(maxDepth, depth);
    maxRows = Math.max(maxRows, depthNodes.length);
    depthNodes.forEach((node, row) => {
      const saved = savedPositions[node.id];
      positions.set(node.id, saved || {
        x: CANVAS_PADDING_X + depth * COLUMN_GAP,
        y: CANVAS_PADDING_Y + row * ROW_GAP,
      });
    });
  }

  return {
    nodes,
    edges,
    positions,
    width: CANVAS_PADDING_X * 2 + maxDepth * COLUMN_GAP + NODE_WIDTH + INSPECTOR_WIDTH + 160,
    height: CANVAS_PADDING_Y * 2 + (maxRows - 1) * ROW_GAP + NODE_HEIGHT + 280,
  };
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

  const paths = [];
  const lanes = buildEdgeLanes(edges, EDGE_LANE_GAP);
  for (const edge of edges) {
    const status = edgeClass(edge);
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("class", `flow-edge layer-flow-edge ${status}`);
    path.setAttribute("marker-end", `url(#layerArrowHead-${status})`);

    const hitPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
    hitPath.setAttribute("class", "flow-edge-hit");
    hitPath.setAttribute("tabindex", "0");
    hitPath.setAttribute("role", "button");
    hitPath.setAttribute("aria-label", edgeTitle(edge));
    hitPath.appendChild(svgTitle(edgeTitle(edge)));

    const selectEdge = () => {
      for (const item of paths) {
        item.path.classList.toggle("selected", item.edge === edge);
      }
      onSelectEdge(edge);
    };
    hitPath.addEventListener("click", selectEdge);
    hitPath.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectEdge();
      }
    });

    svg.appendChild(path);
    svg.appendChild(hitPath);
    paths.push({ edge, path, hitPath, laneOffset: lanes.get(edge) || 0 });
  }

  const redraw = () => {
    for (const item of paths) {
      const from = positions.get(item.edge.from);
      const to = positions.get(item.edge.to);
      if (!from || !to) {
        continue;
      }
      const d = routeDirectedEdge(nodeRect(item.edge.from, from), nodeRect(item.edge.to, to), item.laneOffset);
      item.path.setAttribute("d", d);
      item.hitPath.setAttribute("d", d);
    }
  };
  redraw();
  return { svg, redraw };
}

function markerTemplate() {
  return `
    <defs>
      <marker id="layerArrowHead-normal" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
        <path d="M 0 0 L 9 4.5 L 0 9 z" class="arrow-head normal"></path>
      </marker>
      <marker id="layerArrowHead-warn" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
        <path d="M 0 0 L 9 4.5 L 0 9 z" class="arrow-head warn"></path>
      </marker>
      <marker id="layerArrowHead-error" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
        <path d="M 0 0 L 9 4.5 L 0 9 z" class="arrow-head error"></path>
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

function edgeTitle(edge) {
  const source = edge.from_label || edge.from || "未知来源";
  const target = edge.to_label || edge.to || "未知目标";
  const count = edge.transfer_count ? `，${edge.transfer_count} 次传递` : "";
  return `${source} 到 ${target}${count}`;
}

function svgTitle(text) {
  const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
  title.textContent = text;
  return title;
}

function renderLayerNode(node, position) {
  const button = document.createElement("button");
  button.className = `animator-node layer-node ${nodeClass(node)}`;
  button.style.left = `${position.x}px`;
  button.style.top = `${position.y}px`;
  button.innerHTML = `
    <strong>${escapeHtml(node.label)}</strong>
    <span>调用 ${node.called_method_count || 0} / 未调用 ${node.uncalled_method_count || 0}</span>
  `;
  return button;
}

function installDrag(button, node, positions, savedPositions, redrawEdges, onLayoutChange, getScale) {
  let dragging = null;

  button.addEventListener("pointerdown", (event) => {
    dragging = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      origin: { ...positions.get(node.id) },
    };
    button.setPointerCapture(event.pointerId);
  });

  button.addEventListener("pointermove", (event) => {
    if (!dragging || dragging.pointerId !== event.pointerId) {
      return;
    }
    const scale = getScale?.() || 1;
    const next = {
      x: dragging.origin.x + (event.clientX - dragging.startX) / scale,
      y: dragging.origin.y + (event.clientY - dragging.startY) / scale,
    };
    positions.set(node.id, next);
    savedPositions[node.id] = next;
    button.style.left = `${next.x}px`;
    button.style.top = `${next.y}px`;
    moveAnchoredInspector(button.parentElement, node.id, next);
    redrawEdges();
  });

  button.addEventListener("pointerup", () => {
    dragging = null;
    onLayoutChange?.();
  });

  button.addEventListener("pointercancel", () => {
    dragging = null;
    onLayoutChange?.();
  });
}

function renderLayerInspector(surface, node, position, edges, onSelectMethod, onWatchMethod) {
  surface.querySelector(".layer-inspector")?.remove();
  const incoming = incomingMethods(edges);
  const inspector = document.createElement("section");
  inspector.className = "layer-inspector";
  inspector.dataset.anchorId = node.id;
  const placement = inspectorPlacement(surface, position);
  inspector.style.left = `${placement.x}px`;
  inspector.style.top = `${placement.y}px`;
  inspector.dataset.placement = placement.side;
  inspector.innerHTML = `
    <header>
      <div>
        <strong><span class="ide-symbol">class</span> ${escapeHtml(node.label)} 层级</strong>
        <span>与左侧主节点关联展开的方法窗口</span>
      </div>
      <button class="inspector-close" type="button" aria-label="关闭方法窗口">关闭</button>
    </header>
    <div class="method-list">
      ${(node.methods || []).map((method) => methodRow(method, incoming)).join("")}
    </div>
  `;
  inspector.querySelector(".inspector-close")?.addEventListener("click", () => inspector.remove());
  inspector.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      inspector.remove();
    }
  });
  inspector.querySelectorAll("[data-method]").forEach((item) => {
    item.addEventListener("dragstart", (event) => {
      const method = (node.methods || []).find((candidate) => candidate.label === item.getAttribute("data-method"));
      if (!method) {
        return;
      }
      event.dataTransfer.setData("application/json", JSON.stringify(methodToWatchPayload(method)));
      event.dataTransfer.effectAllowed = "copy";
    });
    item.addEventListener("click", () => {
      const method = (node.methods || []).find((candidate) => candidate.label === item.getAttribute("data-method"));
      onSelectMethod(method || {});
    });
  });
  inspector.querySelectorAll("[data-watch-method]").forEach((item) => {
    item.addEventListener("click", (event) => {
      event.stopPropagation();
      const method = (node.methods || []).find((candidate) => candidate.label === item.getAttribute("data-watch-method"));
      if (method) {
        onWatchMethod(method);
      }
    });
  });
  surface.appendChild(inspector);
}

function moveAnchoredInspector(surface, nodeId, position) {
  if (!surface) {
    return;
  }
  const inspector = [...surface.querySelectorAll(".layer-inspector")].find((item) => item.dataset.anchorId === nodeId);
  if (!inspector) {
    return;
  }
  const placement = inspectorPlacement(surface, position);
  inspector.style.left = `${placement.x}px`;
  inspector.style.top = `${placement.y}px`;
  inspector.dataset.placement = placement.side;
}

function inspectorPlacement(surface, position) {
  const surfaceWidth = Number.parseFloat(surface.style.width) || surface.clientWidth || 1200;
  const rightX = position.x + NODE_WIDTH + INSPECTOR_GAP;
  if (rightX + INSPECTOR_WIDTH < surfaceWidth - 24) {
    return { x: rightX, y: Math.max(18, position.y - 8), side: "right" };
  }
  return {
    x: Math.max(18, position.x - INSPECTOR_WIDTH - INSPECTOR_GAP),
    y: Math.max(18, position.y - 8),
    side: "left",
  };
}

function methodRow(method, incoming) {
  const called = Boolean(method.called);
  const hasInputArrow = incoming.has(method.label);
  return `
    <button class="method-row ${called ? "called" : "uncalled"}" draggable="true" data-method="${escapeHtml(method.label)}">
      <span class="method-input-arrow ${hasInputArrow ? "visible" : "hidden"}">-></span>
      <strong><span class="ide-symbol">def</span> ${escapeHtml(method.short_label || method.label)}</strong>
      <span class="method-state ${called ? "called" : "uncalled"}">${called ? "已调用" : "未调用"}</span>
      <span>${hasInputArrow ? "有数据传入" : "无指向箭头传入"}</span>
      <span class="method-status ${statusClass(method)}">${statusText(method)}</span>
      <span class="method-action" data-watch-method="${escapeHtml(method.label)}">监视</span>
    </button>
  `;
}

function methodToWatchPayload(method) {
  return {
    type: "method",
    id: method.label,
    label: method.label,
    layer: method.layer,
  };
}

function incomingMethods(edges) {
  const result = new Set();
  for (const edge of edges) {
    for (const methodEdge of edge.method_edges || []) {
      if (methodEdge.to_label) {
        result.add(methodEdge.to_label);
      }
    }
  }
  return result;
}

function statusText(method) {
  if (!method.called) {
    return "未产生运行数据";
  }
  if (method.error) {
    return "运行异常";
  }
  if (method.input_validation?.status === "fail") {
    return "输入失败";
  }
  if (method.validation?.status === "fail") {
    return "输出失败";
  }
  return "运行通过";
}

function statusClass(method) {
  if (!method.called) {
    return "muted";
  }
  if (method.error || method.input_validation?.status === "fail" || method.validation?.status === "fail") {
    return "error";
  }
  return "pass";
}

function nodeClass(node) {
  if (node.error || node.validation?.status === "fail") {
    return "error";
  }
  if (node.validation?.status === "warn") {
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
