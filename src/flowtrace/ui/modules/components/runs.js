// 模块：运行列表组件。负责渲染可选择的工作流运行记录。
import { escapeHtml } from "../utils/html.js";

export function renderRuns(container, runs, activeRunId, onSelectRun) {
  container.innerHTML = "";
  for (const run of runs) {
    const button = document.createElement("button");
    button.className = `run-item ${run.run_id === activeRunId ? "active" : ""}`;
    const sourceLabel = run.source === "external_runtime" ? `<span>外部 runtime 投影</span>` : "";
    button.innerHTML = `
      <strong>${escapeHtml(run.label || run.run_id)}</strong>
      <span>${run.event_count} 条事件</span>
      <span>${escapeHtml(run.started_at || "未知开始时间")}</span>
      ${sourceLabel}
    `;
    button.addEventListener("click", () => onSelectRun(run));
    container.appendChild(button);
  }
}
