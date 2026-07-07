// 模块：运行摘要组件。负责把节点、边和问题收敛成顶部状态信息。
import { escapeHtml } from "../utils/html.js";

export function renderSummary(container, summary) {
  const status = summary.status || "unknown";
  container.className = `run-summary ${status}`;
  container.innerHTML = `
    <span class="summary-pill ${status}">${escapeHtml(statusLabel(status))}</span>
    <span>层级 ${summary.layer_count || 0}</span>
    <span>节点 ${summary.node_count || 0}</span>
    <span>数据流边 ${summary.edge_count || 0}</span>
    <span>错误 ${summary.error_count || 0}</span>
    <span>警告 ${summary.warning_count || 0}</span>
    <span>契约失败 ${summary.contract_failure_count || 0}</span>
  `;
}

function statusLabel(status) {
  const labels = {
    healthy: "健康",
    warning: "有警告",
    error: "有错误",
    unknown: "未知",
  };
  return labels[status] || status;
}
