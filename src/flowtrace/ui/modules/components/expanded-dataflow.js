// 模块：全量数据细节组件。负责默认展开每条数据流边的处理细节。
import { escapeHtml, formatJsonHtml } from "../utils/html.js";

export function renderExpandedDataflow(container, dataflow, onSelectEdge) {
  container.className = "expanded-flow";
  container.innerHTML = "";

  const edges = dataflow.edges || [];
  if (!edges.length) {
    container.className = "expanded-flow empty";
    container.textContent = "暂无可展开的数据流边。";
    return;
  }

  for (const edge of edges) {
    const upstreamTitle = edge.relation_type === "entry_data_flow" ? "上级层级输入" : "上级方法输出";
    const card = document.createElement("article");
    card.className = `expanded-edge ${edgeClass(edge)}`;
    card.innerHTML = `
      <button class="expanded-edge-title" type="button">
        <strong>${escapeHtml(edge.from_label || edge.from)}</strong>
        <span>-></span>
        <strong>${escapeHtml(edge.to_label || edge.to)}</strong>
        <em>${escapeHtml(statusText(edge))}</em>
      </button>
      <div class="comparison-grid">
        <section class="comparison-pane">
          <h3>${upstreamTitle}</h3>
          <pre class="code-block">${formatJsonHtml(edge.upstream_output ?? null)}</pre>
        </section>
        <section class="comparison-pane">
          <h3>下级方法输入</h3>
          <pre class="code-block">${formatJsonHtml(edge.downstream_input ?? null)}</pre>
        </section>
      </div>
      <section class="comparison-pane full">
        <h3>处理后数据、交接差异、输入契约、输出契约与字段变化</h3>
        <pre class="code-block">${formatJsonHtml({
          downstream_output: edge.downstream_output,
          handoff_diff: edge.handoff_diff,
          downstream_input_validation: edge.downstream_input_validation,
          output_validation: edge.validation,
          diff: edge.diff,
          error: edge.error,
        })}</pre>
      </section>
    `;
    card.querySelector("button")?.addEventListener("click", () => onSelectEdge(edge));
    container.appendChild(card);
  }
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

function statusText(edge) {
  if (edge.error) {
    return "运行异常";
  }
  if (edge.downstream_input_validation?.status === "fail") {
    return "输入契约失败";
  }
  if (edge.validation?.status === "fail") {
    return "输出契约失败";
  }
  return "已展开";
}
