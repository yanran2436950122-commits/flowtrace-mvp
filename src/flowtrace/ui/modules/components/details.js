// 模块：详情面板组件。负责展示选中事件、方法或数据流边的事实数据。
import { escapeHtml, formatJsonHtml } from "../utils/html.js";

export function renderDetails(container, event) {
  container.innerHTML = `<pre class="code-block">${formatJsonHtml(event)}</pre>`;
}

export function renderAuditFindingDetail(container, finding) {
  container.innerHTML = `
    <section class="finding-detail">
      <div class="finding-detail-header">
        <strong>${escapeHtml(finding.title || "审查问题")}</strong>
        <span>${escapeHtml(finding.severity || "unknown")} · ${escapeHtml(finding.layer || "Analysis")}</span>
      </div>
      <div class="finding-detail-target">
        <span>目标</span>
        <strong>${escapeHtml(finding.target || "未知")}</strong>
      </div>
      <article>
        <h3>问题说明</h3>
        <p>${escapeHtml(finding.detail || "暂无说明。")}</p>
      </article>
      <article>
        <h3>建议动作</h3>
        <p>${escapeHtml(finding.action || "暂无建议。")}</p>
      </article>
      <div class="comparison-grid">
        <article class="comparison-pane">
          <h3>定位信息</h3>
          <pre class="code-block">${formatJsonHtml(finding.location || {})}</pre>
        </article>
        <article class="comparison-pane">
          <h3>证据</h3>
          <pre class="code-block">${formatJsonHtml(finding.evidence || {})}</pre>
        </article>
      </div>
      <article class="comparison-pane full">
        <h3>原始审查项</h3>
        <pre class="code-block">${formatJsonHtml(finding)}</pre>
      </article>
    </section>
  `;
}

export function renderEdgeComparison(container, edge) {
  const methodEdges = edge.method_edges || [];
  const relationType = methodEdges[0]?.relation_type || edge.relation_type;
  const upstreamTitle = relationType === "entry_data_flow" ? "上级层级输入" : "上级方法输出";
  container.innerHTML = `
    <section class="edge-detail">
      <div class="edge-detail-header">
        <strong>${escapeHtml(edge.from_label || edge.from || "未知来源")}</strong>
        <span>-></span>
        <strong>${escapeHtml(edge.to_label || edge.to || "未知目标")}</strong>
      </div>
      ${methodEdges.length ? `<p class="edge-note">该层级边包含 ${methodEdges.length} 条方法级传递。</p>` : ""}
      <div class="comparison-grid">
        <article class="comparison-pane">
          <h3>${upstreamTitle}</h3>
          <pre class="code-block">${formatJsonHtml(edge.upstream_output ?? null)}</pre>
        </article>
        <article class="comparison-pane">
          <h3>下级方法输入</h3>
          <pre class="code-block">${formatJsonHtml(edge.downstream_input ?? null)}</pre>
        </article>
      </div>
      <article class="comparison-pane full">
        <h3>交接差异、输入契约、输出契约与字段变化</h3>
        <pre class="code-block">${formatJsonHtml({
          transfer_count: edge.transfer_count,
          method_edges: methodEdges,
          handoff_diff: edge.handoff_diff,
          downstream_input_validation: edge.downstream_input_validation,
          output_validation: edge.validation,
          diff: edge.diff,
          error: edge.error,
        })}</pre>
      </article>
    </section>
  `;
}
