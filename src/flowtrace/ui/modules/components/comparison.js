// 模块：运行对比组件。负责展示两次运行之间的参数流边差异。
import { escapeHtml } from "../utils/html.js";

export function renderComparison(container, comparison, runLabels, onSelectComparison) {
  container.className = "comparison-list";
  container.innerHTML = "";

  const header = document.createElement("div");
  header.className = "comparison-header";
  header.innerHTML = `
    <strong>目标运行：${escapeHtml(runLabels.target || comparison.target_run_id)}</strong>
    <span>对比基线：${escapeHtml(runLabels.base || comparison.base_run_id)}</span>
  `;
  container.appendChild(header);

  const comparisons = comparison.comparisons || [];
  if (!comparisons.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "暂无可对比的数据流边。";
    container.appendChild(empty);
    return;
  }

  for (const item of comparisons) {
    container.appendChild(createComparisonCard(item, onSelectComparison));
  }
}

function createComparisonCard(item, onSelectComparison) {
  const card = document.createElement("button");
  card.className = `comparison-card ${item.status}`;
  card.innerHTML = `
    <div class="comparison-card-title">
      <strong>${escapeHtml(item.from_label || item.edge_key)}</strong>
      <span>-></span>
      <strong>${escapeHtml(item.to_label || "")}</strong>
    </div>
    <div class="meta">
      <span>${statusLabel(item.status)}</span>
      ${diffBadge("上级输出", item.upstream_output_diff)}
      ${diffBadge("下级输入", item.downstream_input_diff)}
      ${diffBadge("下级输出", item.downstream_output_diff)}
      ${validationBadge(item.validation_change)}
    </div>
  `;
  card.addEventListener("click", () => onSelectComparison(item));
  return card;
}

function diffBadge(label, diff) {
  if (!diff || diff.status !== "compared") {
    return "";
  }
  const count = (diff.added_fields?.length || 0) + (diff.removed_fields?.length || 0) + (diff.changed_fields?.length || 0);
  if (!count) {
    return `<span class="badge pass">${label}无变化</span>`;
  }
  return `<span class="badge warn">${label}${count}处变化</span>`;
}

function validationBadge(change) {
  if (!change) {
    return "";
  }
  const changed =
    change.base_input_status !== change.target_input_status ||
    change.base_output_status !== change.target_output_status;
  if (!changed) {
    return "";
  }
  return `<span class="badge warn">契约状态变化</span>`;
}

function statusLabel(status) {
  const labels = {
    same: "无变化",
    changed: "有变化",
    added: "新增边",
    removed: "移除边",
  };
  return labels[status] || status || "未知";
}
