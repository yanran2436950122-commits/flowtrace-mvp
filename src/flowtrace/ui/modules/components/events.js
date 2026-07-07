// 模块：事件流程组件。负责渲染运行事件、契约状态和字段变化标记。
import { escapeHtml } from "../utils/html.js";

const VISIBLE_EVENT_TYPES = new Set(["user_action", "function_start", "function_end", "run_start", "run_end"]);

const EVENT_TYPE_LABELS = {
  run_start: "运行开始",
  run_end: "运行结束",
  user_action: "用户操作",
  function_start: "函数开始",
  function_end: "函数结束",
};

const VALIDATION_LABELS = {
  pass: "契约通过",
  warn: "契约警告",
  fail: "契约失败",
  no_contract: "无契约",
};

export function renderEvents(container, events, onSelectEvent) {
  container.className = "graph";
  container.innerHTML = "";

  const visible = events.filter((event) => VISIBLE_EVENT_TYPES.has(event.event_type));
  if (!visible.length) {
    container.className = "graph empty";
    container.textContent = "暂无事件。";
    return;
  }

  for (const [index, event] of visible.entries()) {
    container.appendChild(createEventNode(event, onSelectEvent));
    if (index < visible.length - 1) {
      container.appendChild(createArrow());
    }
  }
}

function createEventNode(event, onSelectEvent) {
  const node = document.createElement("button");
  node.className = nodeClass(event);
  node.innerHTML = `
    <h3>${escapeHtml(labelFor(event))}</h3>
    <div class="meta">
      <span>${escapeHtml(eventTypeLabel(event.event_type))}</span>
      ${validationBadge(event)}
      ${diffBadge(event)}
      ${event.duration_ms ? `<span>${event.duration_ms} 毫秒</span>` : ""}
    </div>
  `;
  node.addEventListener("click", () => onSelectEvent(event));
  return node;
}

function createArrow() {
  const arrow = document.createElement("div");
  arrow.className = "arrow";
  arrow.textContent = "->";
  return arrow;
}

function nodeClass(event) {
  const validationStatus = event.validation?.status;
  const classes = ["node"];
  if (event.error || validationStatus === "fail") {
    classes.push("error");
  } else if (validationStatus === "warn") {
    classes.push("warn");
  }
  if (event.event_type === "user_action") {
    classes.push("user");
  }
  return classes.join(" ");
}

function validationBadge(event) {
  const status = event.validation?.status;
  if (!status || status === "no_contract") {
    return "";
  }
  return `<span class="badge ${status}">${escapeHtml(VALIDATION_LABELS[status] || status)}</span>`;
}

function diffBadge(event) {
  const diff = event.diff;
  if (!diff || diff.status !== "compared") {
    return "";
  }
  const count = (diff.added_fields?.length || 0) + (diff.removed_fields?.length || 0) + (diff.changed_fields?.length || 0);
  if (!count) {
    return `<span class="badge pass">字段无变化</span>`;
  }
  return `<span class="badge warn">${count} 处字段变化</span>`;
}

function labelFor(event) {
  if (event.event_type === "function_start") {
    return `开始 - ${event.target_node}`;
  }
  if (event.event_type === "function_end") {
    return `结束 - ${event.source_node}`;
  }
  return event.action || EVENT_TYPE_LABELS[event.event_type] || event.event_id;
}

function eventTypeLabel(eventType) {
  return EVENT_TYPE_LABELS[eventType] || eventType;
}
