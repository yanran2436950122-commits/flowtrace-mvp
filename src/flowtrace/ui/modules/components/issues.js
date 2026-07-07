// 模块：问题列表组件。负责展示后端归纳出的运行问题。
import { escapeHtml } from "../utils/html.js";

const SEVERITY_LABELS = {
  error: "错误",
  warn: "警告",
};

const KIND_LABELS = {
  runtime_error: "运行异常",
  input_contract_failure: "输入契约失败",
  output_contract_failure: "输出契约失败",
  handoff_diff: "交接差异",
};

export function renderIssues(container, issueReport, onSelectIssue) {
  container.className = "issue-list";
  container.innerHTML = "";

  const summary = issueReport.summary || {};
  const header = document.createElement("div");
  header.className = "issue-summary";
  header.innerHTML = `
    <strong>问题总数：<span class="ide-number">${summary.total || 0}</span></strong>
    <span>错误：<span class="ide-error">${summary.errors || 0}</span></span>
    <span>警告：<span class="ide-warn">${summary.warnings || 0}</span></span>
  `;
  container.appendChild(header);

  const issues = issueReport.issues || [];
  if (!issues.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "当前运行暂无问题。";
    container.appendChild(empty);
    return;
  }

  for (const issue of issues) {
    container.appendChild(createIssueCard(issue, onSelectIssue));
  }
}

function createIssueCard(issue, onSelectIssue) {
  const card = document.createElement("button");
  const kindLabel = KIND_LABELS[issue.kind] || issue.kind || "issue";
  const title = issue.title || "未知问题";
  const showKind = kindLabel !== title;
  card.className = `issue-card ${issue.severity || "warn"}`;
  card.innerHTML = `
    <div class="issue-title">
      <strong>${showKind ? `<span class="issue-kind">${escapeHtml(kindLabel)}</span> ` : ""}${escapeHtml(title)}</strong>
      <span class="severity ${issue.severity || "warn"}">${escapeHtml(SEVERITY_LABELS[issue.severity] || issue.severity || "未知级别")}</span>
    </div>
    <div class="issue-meta">
      <span class="ide-path">${escapeHtml(issue.node || "未知节点")}</span>
      ${issue.edge ? `<span class="ide-path">${escapeHtml(issue.edge)}</span>` : ""}
    </div>
    <p>${escapeHtml(issue.message || "")}</p>
  `;
  card.addEventListener("click", () => onSelectIssue(issue));
  return card;
}
