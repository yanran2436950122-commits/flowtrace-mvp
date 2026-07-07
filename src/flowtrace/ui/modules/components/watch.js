// 模块：监视窗口组件。负责固定监视方法并按当前运行数据实时刷新。
import { escapeHtml, formatJsonHtml } from "../utils/html.js";

export function renderWatchPanel(
  container,
  statusElement,
  watchItems,
  layerFlow,
  onRemoveWatch,
  onDropWatch,
  onSelectWatch,
  isWatchOpen,
  onWatchOpenChange,
  getWatchScroll,
  onWatchScrollChange,
  isWatchFrozen,
  getWatchSnapshot,
  onWatchFreezeChange,
) {
  installDropTarget(container, onDropWatch);
  statusElement.textContent = watchItems.length ? `监视 ${watchItems.length} 项` : "拖入方法以固定监视";
  container.innerHTML = "";

  if (!watchItems.length) {
    container.innerHTML = `
      <div class="watch-empty">
        <strong>暂无监视项</strong>
        <span>从层级小窗拖入方法，或点击方法行的“监视”。</span>
      </div>
    `;
    return;
  }

  for (const item of watchItems) {
    const method = resolveMethod(layerFlow, item);
    const card = document.createElement("article");
    card.className = `watch-card ${methodStatusClass(method)}`;
    const detailsOpen = isWatchOpen(item) ? "open" : "";
    const liveSnapshot = buildWatchSnapshot(method);
    const frozen = isWatchFrozen(item);
    const snapshotData = frozen ? getWatchSnapshot(item) || liveSnapshot : liveSnapshot;
    card.innerHTML = `
      <header>
        <div>
          <strong><span class="ide-symbol">watch</span> ${escapeHtml(item.label || item.id)}</strong>
          <span>${escapeHtml(method?.layer || item.layer || "未知层级")}</span>
        </div>
        <div class="watch-actions">
          <button type="button" data-freeze>${frozen ? "跟随" : "锁定"}</button>
          <button type="button" data-remove>移除</button>
        </div>
      </header>
      <div class="watch-meta">
        <span class="method-status ${methodStatusClass(method)}">${escapeHtml(methodStatusText(method))}</span>
        <span>${method?.duration_ms ? `${method.duration_ms} 毫秒` : "无耗时"}</span>
        <span>${inputText(method)}</span>
        <span class="watch-lock-state ${frozen ? "locked" : ""}">${frozen ? "快照已锁定" : "跟随最新"}</span>
      </div>
      <details ${detailsOpen}>
        <summary>输入 / 输出快照</summary>
        <pre class="code-block" data-watch-snapshot>${formatJsonHtml(snapshotData)}</pre>
      </details>
    `;
    card.addEventListener("click", (event) => {
      if (event.target.closest("button")) {
        return;
      }
      onSelectWatch(method || item);
    });
    card.querySelector("details")?.addEventListener("toggle", (event) => {
      onWatchOpenChange(item, event.currentTarget.open);
    });
    const snapshotNode = card.querySelector("[data-watch-snapshot]");
    card.querySelector("[data-freeze]")?.addEventListener("click", () => {
      onWatchFreezeChange(item, !frozen, liveSnapshot);
    });
    card.querySelector("[data-remove]")?.addEventListener("click", () => onRemoveWatch(item));
    container.appendChild(card);
    restoreSnapshotScroll(snapshotNode, item, getWatchScroll, onWatchScrollChange);
  }
}

export function methodToWatchItem(method) {
  return {
    type: "method",
    id: method.label,
    label: method.label,
    layer: method.layer,
  };
}

function installDropTarget(container, onDropWatch) {
  container.addEventListener("dragover", (event) => {
    event.preventDefault();
    container.classList.add("drop-active");
  });
  container.addEventListener("dragleave", () => {
    container.classList.remove("drop-active");
  });
  container.addEventListener("drop", (event) => {
    event.preventDefault();
    container.classList.remove("drop-active");
    const raw = event.dataTransfer.getData("application/json");
    if (!raw) {
      return;
    }
    try {
      onDropWatch(JSON.parse(raw));
    } catch {
      return;
    }
  });
}

function resolveMethod(layerFlow, item) {
  for (const node of layerFlow?.nodes || []) {
    for (const method of node.methods || []) {
      if (method.label === item.id) {
        return method;
      }
    }
  }
  return null;
}

function methodStatusText(method) {
  if (!method) {
    return "当前运行未发现";
  }
  if (!method.called) {
    return "未调用";
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

function methodStatusClass(method) {
  if (!method || !method.called) {
    return "muted";
  }
  if (method.error || method.input_validation?.status === "fail" || method.validation?.status === "fail") {
    return "error";
  }
  return "pass";
}

function inputText(method) {
  if (!method) {
    return "无数据";
  }
  if (!method.called) {
    return "无指向箭头传入";
  }
  return method.input ? "有输入快照" : "无输入快照";
}

function buildWatchSnapshot(method) {
  return {
    input: method?.input ?? null,
    output: method?.output ?? null,
    input_validation: method?.input_validation ?? null,
    output_validation: method?.validation ?? null,
    error: method?.error ?? null,
  };
}

function restoreSnapshotScroll(snapshot, item, getWatchScroll, onWatchScrollChange) {
  if (!snapshot) {
    return;
  }
  const scrollPosition = getWatchScroll(item);
  snapshot.scrollLeft = scrollPosition.left;
  snapshot.scrollTop = scrollPosition.top;
  snapshot.addEventListener("scroll", () => {
    onWatchScrollChange(item, {
      left: snapshot.scrollLeft,
      top: snapshot.scrollTop,
    });
  });
}
