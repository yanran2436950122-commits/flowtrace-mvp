// 模块：视图切换组件。负责在不同运行视图之间切换。
const VIEWS = [
  { id: "project", label: "项目结构" },
  { id: "layers", label: "层级流转" },
  { id: "dataflow", label: "方法数据流" },
  { id: "expanded", label: "全量细节" },
  { id: "issues", label: "问题列表" },
  { id: "compare", label: "运行对比" },
  { id: "events", label: "事件流程" },
];

export function renderViewToggle(container, activeView, onSelectView) {
  container.innerHTML = "";
  for (const view of VIEWS) {
    const button = document.createElement("button");
    button.className = `view-tab ${view.id === activeView ? "active" : ""}`;
    button.textContent = view.label;
    button.addEventListener("click", () => onSelectView(view.id));
    container.appendChild(button);
  }
}
