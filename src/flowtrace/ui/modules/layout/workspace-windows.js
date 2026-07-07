// 模块：工作区窗口布局。负责页面标签合并、停靠和布局持久化，不接管具体业务组件样式。
const STORAGE_KEY = "flowtrace.workspaceWindows.v1";
const EDGE_RATIO = 0.22;
const SIDE_MIDDLE_START = 0.2;
const SIDE_MIDDLE_END = 0.8;
const BOTTOM_VISIBLE_EDGE_PX = 76;
const MAIN_PANEL_IDS = ["project", "runner", "onboarding", "layers", "dataflow", "expanded", "issues", "compare", "events"];

export function installWorkspaceWindows(contentElement, panels) {
  const registry = normalizePanels(panels);
  if (!contentElement || !registry.size) {
    return;
  }
  if (shouldResetLayout()) {
    clearLayout();
  }

  const layout = {
    root: loadLayout(registry) || defaultLayout(registry),
    draggingId: "",
    host: document.createElement("section"),
  };
  layout.host.className = "workspace-window-root";
  layout.host._flowtraceWindowLayout = layout;
  contentElement.classList.add("window-workspace");
  contentElement.replaceChildren(layout.host);

  const render = () => {
    layout.root = ensureRegisteredPanels(normalizeLayout(layout.root, registry) || defaultLayout(registry), registry);
    layout.host.replaceChildren(renderNode(layout.root, registry, layout, render));
    saveLayout(layout.root);
  };
  window.flowtraceResetWorkspaceLayout = () => {
    clearLayout();
    layout.root = defaultLayout(registry);
    render();
  };

  render();
}

function normalizePanels(panels) {
  return new Map(
    panels
      .filter((panel) => panel.id && panel.title && panel.element)
      .map((panel) => [panel.id, panel]),
  );
}

function defaultLayout(registry) {
  const mainPanelIds = MAIN_PANEL_IDS.filter((id) => registry.has(id));
  const hasWatch = registry.has("watch");
  const hasDetails = registry.has("details");
  const side = hasWatch && hasDetails
    ? {
        type: "split",
        direction: "vertical",
        ratio: 0.42,
        first: pane("watch-pane", ["watch"]),
        second: pane("details-pane", ["details"]),
      }
    : pane("side-pane", [...["watch", "details"].filter((id) => registry.has(id))]);

  if (!mainPanelIds.length || !side) {
    return pane("main-pane", [...registry.keys()]);
  }

  return {
    type: "split",
    direction: "horizontal",
    ratio: 0.72,
    first: pane("main-pane", mainPanelIds, registry.has("layers") ? "layers" : mainPanelIds[0]),
    second: side,
  };
}

function pane(id, panelIds, active = panelIds[0] || "") {
  return {
    type: "pane",
    id,
    active,
    panels: panelIds,
  };
}

function renderNode(node, registry, layout, render) {
  if (node.type === "split") {
    const shell = document.createElement("section");
    shell.className = `workspace-split ${node.direction}`;

    const first = document.createElement("div");
    const second = document.createElement("div");
    const divider = document.createElement("div");
    first.className = "workspace-split-child";
    second.className = "workspace-split-child";
    divider.className = "workspace-split-divider";
    divider.dataset.splitDirection = node.direction;
    first.style.flex = `${node.ratio} 1 0`;
    second.style.flex = `${1 - node.ratio} 1 0`;
    installSplitResize(divider, node, first, second, layout);
    first.appendChild(renderNode(node.first, registry, layout, render));
    second.appendChild(renderNode(node.second, registry, layout, render));
    shell.append(first, divider, second);
    return shell;
  }

  return renderPane(node, registry, layout, render);
}

function installSplitResize(divider, splitNode, firstElement, secondElement, layout) {
  let resize = null;

  divider.addEventListener("pointerdown", (event) => {
    const firstRect = firstElement.getBoundingClientRect();
    const secondRect = secondElement.getBoundingClientRect();
    resize = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      firstSize: splitNode.direction === "horizontal" ? firstRect.width : firstRect.height,
      totalSize: splitNode.direction === "horizontal"
        ? firstRect.width + secondRect.width
        : firstRect.height + secondRect.height,
    };
    divider.setPointerCapture(event.pointerId);
    event.preventDefault();
  });

  divider.addEventListener("pointermove", (event) => {
    if (!resize || resize.pointerId !== event.pointerId) {
      return;
    }
    const delta = splitNode.direction === "horizontal"
      ? event.clientX - resize.startX
      : event.clientY - resize.startY;
    const ratio = clamp((resize.firstSize + delta) / resize.totalSize, 0.18, 0.82);
    splitNode.ratio = ratio;
    firstElement.style.flex = `${ratio} 1 0`;
    secondElement.style.flex = `${1 - ratio} 1 0`;
  });

  const stopResize = (event) => {
    if (!resize || resize.pointerId !== event.pointerId) {
      return;
    }
    resize = null;
    saveLayout(layout.root);
  };
  divider.addEventListener("pointerup", stopResize);
  divider.addEventListener("pointercancel", stopResize);
}

function renderPane(node, registry, layout, render) {
  const shell = document.createElement("section");
  shell.className = "workspace-pane";
  shell.dataset.paneId = node.id;

  const tabs = document.createElement("nav");
  tabs.className = "workspace-pane-tabs";
  tabs.dataset.paneTabs = node.id;

  for (const panelId of node.panels) {
    const panel = registry.get(panelId);
    if (!panel) {
      continue;
    }
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = `workspace-pane-tab${panelId === node.active ? " active" : ""}`;
    tab.draggable = true;
    tab.dataset.panelId = panelId;
    tab.textContent = panel.title;
    tab.addEventListener("click", () => {
      node.active = panelId;
      render();
    });
    tabs.appendChild(tab);
  }

  const body = document.createElement("div");
  body.className = "workspace-pane-body";
  const activePanel = registry.get(node.active) || registry.get(node.panels[0]);
  if (activePanel) {
    node.active = activePanel.id;
    body.appendChild(activePanel.element);
  }

  installPaneDrop(shell, tabs, node, layout, render);
  shell.append(tabs, body);
  return shell;
}

function installPaneDrop(shell, tabs, node, layout, render) {
  shell.addEventListener("dragover", (event) => {
    if (!layout.draggingId) {
      return;
    }
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  });

  shell.addEventListener("drop", (event) => {
    if (!layout.draggingId) {
      return;
    }
    event.preventDefault();
    const area = dropArea(shell, event);
    const insertIndex = event.target.closest?.(".workspace-pane-tabs") ? tabInsertIndex(tabs, event, layout.draggingId) : null;
    layout.root = movePanel(layout.root, layout.draggingId, node.id, area, insertIndex);
    layout.draggingId = "";
    render();
  });
}

document.addEventListener("dragstart", (event) => {
  const tab = event.target.closest?.(".workspace-pane-tab");
  if (!tab) {
    return;
  }
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", tab.dataset.panelId);
  const root = tab.closest(".workspace-window-root");
  root?.setAttribute("data-dragging-panel", tab.dataset.panelId);
  const appLayout = root?._flowtraceWindowLayout;
  if (appLayout) {
    appLayout.draggingId = tab.dataset.panelId;
  }
});

document.addEventListener("dragend", (event) => {
  const root = event.target.closest?.(".workspace-window-root") || document.querySelector(".workspace-window-root");
  if (root?._flowtraceWindowLayout) {
    root._flowtraceWindowLayout.draggingId = "";
  }
  root?.removeAttribute("data-dragging-panel");
});

function dropArea(paneElement, event) {
  if (event.target.closest?.(".workspace-pane-tabs")) {
    return "center";
  }
  const rect = paneElement.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width;
  const y = (event.clientY - rect.top) / rect.height;
  if (y >= SIDE_MIDDLE_START && y <= SIDE_MIDDLE_END && x <= EDGE_RATIO) {
    return "left";
  }
  if (y >= SIDE_MIDDLE_START && y <= SIDE_MIDDLE_END && x >= 1 - EDGE_RATIO) {
    return "right";
  }
  if (y <= EDGE_RATIO) {
    return "top";
  }
  if (isVisibleBottomDock(rect, event)) {
    return "bottom";
  }
  return "center";
}

function tabInsertIndex(tabsElement, event, draggingId) {
  const tabs = [...tabsElement.querySelectorAll(".workspace-pane-tab")];
  if (!tabs.length) {
    return 0;
  }
  for (const [index, tab] of tabs.entries()) {
    if (tab.dataset.panelId === draggingId) {
      continue;
    }
    const rect = tab.getBoundingClientRect();
    if (event.clientX < rect.left + rect.width / 2) {
      return index;
    }
    if (event.clientX <= rect.right) {
      return index + 1;
    }
  }
  return tabs.length;
}

function isVisibleBottomDock(rect, event) {
  const visibleBottom = Math.min(rect.bottom, window.innerHeight);
  return event.clientY >= visibleBottom - BOTTOM_VISIBLE_EDGE_PX && event.clientY <= visibleBottom;
}

function movePanel(root, panelId, targetPaneId, area, insertIndex = null) {
  const targetBeforeRemove = findPane(root, targetPaneId);
  if (!targetBeforeRemove) {
    return root;
  }
  if (area === "center" && targetBeforeRemove.panels.includes(panelId)) {
    if (insertIndex !== null) {
      reorderPanel(targetBeforeRemove, panelId, insertIndex);
    }
    targetBeforeRemove.active = panelId;
    return root;
  }
  if (targetBeforeRemove.panels.includes(panelId) && targetBeforeRemove.panels.length === 1) {
    return root;
  }

  let nextRoot = removePanel(root, panelId);
  if (area === "center") {
    const target = findPane(nextRoot, targetPaneId);
    if (target && !target.panels.includes(panelId)) {
      insertPanel(target, panelId, insertIndex);
      target.active = panelId;
    }
    return normalizeLayout(nextRoot);
  }

  const newPane = pane(`pane-${panelId}-${Date.now()}`, [panelId]);
  nextRoot = replacePane(nextRoot, targetPaneId, (target) => splitWithPanel(target, newPane, area));
  return normalizeLayout(nextRoot);
}

function reorderPanel(target, panelId, insertIndex) {
  const oldIndex = target.panels.indexOf(panelId);
  if (oldIndex < 0) {
    return;
  }
  target.panels.splice(oldIndex, 1);
  const adjustedIndex = oldIndex < insertIndex ? insertIndex - 1 : insertIndex;
  target.panels.splice(clampIndex(adjustedIndex, target.panels.length), 0, panelId);
}

function insertPanel(target, panelId, insertIndex) {
  target.panels.splice(clampIndex(insertIndex, target.panels.length), 0, panelId);
}

function clampIndex(value, length) {
  if (!Number.isFinite(value)) {
    return length;
  }
  return Math.min(length, Math.max(0, Math.round(value)));
}

function splitWithPanel(target, newPane, area) {
  const direction = area === "left" || area === "right" ? "horizontal" : "vertical";
  const newFirst = area === "left" || area === "top";
  return {
    type: "split",
    direction,
    ratio: 0.5,
    first: newFirst ? newPane : target,
    second: newFirst ? target : newPane,
  };
}

function removePanel(node, panelId) {
  if (!node) {
    return null;
  }
  if (node.type === "pane") {
    node.panels = node.panels.filter((id) => id !== panelId);
    if (node.active === panelId) {
      node.active = node.panels[0] || "";
    }
    return normalizeLayout(node);
  }
  node.first = removePanel(node.first, panelId);
  node.second = removePanel(node.second, panelId);
  return normalizeLayout(node);
}

function replacePane(node, paneId, replacementFactory) {
  if (!node) {
    return null;
  }
  if (node.type === "pane" && node.id === paneId) {
    return replacementFactory(node);
  }
  if (node.type === "split") {
    node.first = replacePane(node.first, paneId, replacementFactory);
    node.second = replacePane(node.second, paneId, replacementFactory);
  }
  return node;
}

function findPane(node, paneId) {
  if (!node) {
    return null;
  }
  if (node.type === "pane" && node.id === paneId) {
    return node;
  }
  if (node.type === "split") {
    return findPane(node.first, paneId) || findPane(node.second, paneId);
  }
  return null;
}

function normalizeLayout(node, registry = null) {
  if (!node) {
    return null;
  }
  if (node.type === "pane") {
    if (registry) {
      node.panels = node.panels.filter((id, index) => registry.has(id) && node.panels.indexOf(id) === index);
    }
    if (!node.panels.length) {
      return null;
    }
    if (!node.panels.includes(node.active)) {
      node.active = node.panels[0];
    }
    return node;
  }
  node.first = normalizeLayout(node.first, registry);
  node.second = normalizeLayout(node.second, registry);
  if (!node.first) {
    return node.second;
  }
  if (!node.second) {
    return node.first;
  }
  return node;
}

function ensureRegisteredPanels(root, registry) {
  const present = collectPanelIds(root);
  const hasMainPanel = MAIN_PANEL_IDS.some((id) => present.has(id));
  if (!hasMainPanel && MAIN_PANEL_IDS.some((id) => registry.has(id))) {
    return defaultLayout(registry);
  }
  const missing = [...registry.keys()].filter((id) => !present.has(id));
  if (!missing.length) {
    return root;
  }
  const target = firstPane(root);
  if (!target) {
    return defaultLayout(registry);
  }
  target.panels.push(...missing);
  if (!target.active || !target.panels.includes(target.active)) {
    target.active = target.panels[0];
  }
  return root;
}

function collectPanelIds(node, result = new Set()) {
  if (!node) {
    return result;
  }
  if (node.type === "pane") {
    for (const panelId of node.panels) {
      result.add(panelId);
    }
    return result;
  }
  collectPanelIds(node.first, result);
  collectPanelIds(node.second, result);
  return result;
}

function firstPane(node) {
  if (!node) {
    return null;
  }
  if (node.type === "pane") {
    return node;
  }
  return firstPane(node.first) || firstPane(node.second);
}

function loadLayout(registry) {
  try {
    const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "null");
    return normalizeLayout(saved, registry);
  } catch {
    return null;
  }
}

function shouldResetLayout() {
  return new URLSearchParams(window.location.search).has("resetWindows");
}

function clearLayout() {
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // localStorage 不可用时无需额外处理。
  }
}

function saveLayout(root) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(root));
  } catch {
    // localStorage 不可用时，布局仍在当前会话生效。
  }
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}
