// 模块：项目结构视图。负责展示静态扫描结果与运行覆盖对齐结果。
import { escapeHtml } from "../utils/html.js";

export function renderProject(container, project, coverage, onApplyContext = async () => {}, onPickPath = async () => ({ cancelled: true })) {
  container.className = "project-view";
  container.innerHTML = "";

  const totals = project.totals || {};
  const summary = coverage.summary || {};
  const context = project.context || {};
  const root = context.root || project.root || "未知";
  const traceDir = context.trace_dir || "未知";
  const source = context.source || "unknown";
  const configFile = context.config_file || "";
  const contextSection = section("项目接入", renderContextForm(root, traceDir, source, configFile));
  container.appendChild(contextSection);
  installContextForm(contextSection, onApplyContext, onPickPath);

  container.appendChild(section("项目概览", `
    <div class="project-metrics">
      ${metric("文件", totals.files)}
      ${metric("模块", totals.modules)}
      ${metric("类", totals.classes)}
      ${metric("函数", totals.functions)}
      ${metric("入口候选", totals.entrypoints)}
      ${metric("声明方法", totals.declared_methods)}
      ${metric("运行覆盖", `${summary.covered_method_count || 0}/${summary.known_method_count || 0}`)}
    </div>
    ${projectRoot(root, traceDir, source)}
    <p class="project-note">静态扫描只产生候选结构；真实调用关系以运行记录为准。</p>
  `));

  container.appendChild(section("项目结构摘要", renderProjectSummary(project)));
  container.appendChild(section("入口候选", renderEntrypoints(project.entrypoints || [])));
  container.appendChild(section("模块列表", renderModules(project.modules || [])));
  container.appendChild(section("方法覆盖", renderCoverage(coverage)));
  container.appendChild(section("扫描错误", renderScanErrors(project.scan_errors || [])));
}

function section(title, bodyHtml) {
  const node = document.createElement("section");
  node.className = "project-section";
  node.innerHTML = `<h3>${escapeHtml(title)}</h3>${bodyHtml}`;
  return node;
}

function metric(label, value) {
  return `
    <div class="project-metric">
      <strong>${escapeHtml(value ?? 0)}</strong>
      <span>${escapeHtml(label)}</span>
    </div>
  `;
}

function projectRoot(root, traceDir, source) {
  return `
    <div class="project-root">
      <span>目标项目</span>
      <strong title="${escapeHtml(root)}">${escapeHtml(root)}</strong>
      <span>运行记录</span>
      <strong title="${escapeHtml(traceDir)}">${escapeHtml(traceDir)}</strong>
      <em>${escapeHtml(source)}</em>
    </div>
  `;
}

function renderContextForm(root, traceDir, source, configFile) {
  return `
    <form class="project-context-form" data-current-root="${escapeHtml(root)}" data-current-trace="${escapeHtml(traceDir)}">
      <div class="project-context-intro">
        <strong>接入真实项目</strong>
        <span>选择一个项目文件夹后，FlowTrace 会切换扫描与治理视图；默认运行记录目录为该项目下的 .flowtrace。</span>
      </div>
      <label>
        <span>项目文件夹</span>
        <div class="project-path-field">
          <input name="project_root" value="${escapeHtml(root)}" placeholder="选择或粘贴完整项目文件夹路径" spellcheck="false" />
          <button type="button" data-path-picker="project">选择文件夹</button>
        </div>
      </label>
      <label>
        <span>运行记录目录</span>
        <div class="project-path-field">
          <input name="trace_dir" value="${escapeHtml(traceDir)}" placeholder="默认使用项目文件夹下的 .flowtrace" spellcheck="false" />
          <button type="button" data-path-picker="trace">选择文件夹</button>
        </div>
      </label>
      <label>
        <span>配置文件</span>
        <div class="project-path-field">
          <input name="config_file" value="${escapeHtml(configFile)}" placeholder="可选" spellcheck="false" />
          <button type="button" data-path-picker="config">选择文件</button>
        </div>
      </label>
      <div class="project-context-actions">
        <span>来源：${escapeHtml(source)}</span>
        <button type="submit">应用项目</button>
      </div>
      <p class="project-note">只切换 FlowTrace 读取上下文，不修改目标项目代码。</p>
      <p class="project-context-status" data-project-context-status></p>
    </form>
  `;
}

function installContextForm(sectionNode, onApplyContext, onPickPath) {
  const form = sectionNode.querySelector(".project-context-form");
  const status = sectionNode.querySelector("[data-project-context-status]");
  if (!form) {
    return;
  }
  for (const button of form.querySelectorAll("[data-path-picker]")) {
    button.addEventListener("click", async () => {
      const kind = button.dataset.pathPicker;
      const input = pathInputForKind(form, kind);
      if (!input) {
        return;
      }
      const originalText = button.textContent;
      button.disabled = true;
      button.textContent = "选择中";
      status.textContent = kind === "config" ? "请在系统窗口中选择配置文件。" : "请在系统窗口中选择文件夹。";
      status.className = "project-context-status";
      try {
        const result = await onPickPath({ kind, initial_path: input.value.trim() });
        if (!result.cancelled && result.selected_path) {
          const previousRoot = form.dataset.currentRoot || "";
          const previousTrace = form.dataset.currentTrace || "";
          const traceInput = form.elements.trace_dir;
          const shouldSyncTrace = kind === "project" && shouldUseDefaultTraceDir(traceInput.value, previousRoot, previousTrace);
          input.value = result.selected_path;
          if (shouldSyncTrace) {
            traceInput.value = defaultTraceDir(result.selected_path);
          }
          status.textContent = kind === "project" ? "项目文件夹已选择，请应用项目。" : "路径已选择，请应用项目。";
          status.classList.add("pass");
        } else {
          status.textContent = "已取消选择。";
        }
      } catch (error) {
        status.textContent = `选择失败：${error.message}`;
        status.classList.add("error");
      } finally {
        button.disabled = false;
        button.textContent = originalText;
      }
    });
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button[type='submit']");
    const payload = {
      project_root: form.elements.project_root.value.trim(),
      trace_dir: form.elements.trace_dir.value.trim(),
      config_file: form.elements.config_file.value.trim(),
    };
    status.textContent = "正在切换项目...";
    status.className = "project-context-status";
    button.disabled = true;
    try {
      await onApplyContext(payload);
      status.textContent = "项目已切换，视图已刷新。";
      status.classList.add("pass");
    } catch (error) {
      status.textContent = `切换失败：${error.message}`;
      status.classList.add("error");
    } finally {
      button.disabled = false;
    }
  });
}

function pathInputForKind(form, kind) {
  if (kind === "project") {
    return form.elements.project_root;
  }
  if (kind === "trace") {
    return form.elements.trace_dir;
  }
  if (kind === "config") {
    return form.elements.config_file;
  }
  return null;
}

function shouldUseDefaultTraceDir(traceValue, currentRoot, currentTrace) {
  const value = String(traceValue || "").trim();
  if (!value) {
    return true;
  }
  if (samePath(value, currentTrace)) {
    return true;
  }
  return samePath(value, defaultTraceDir(currentRoot));
}

function defaultTraceDir(projectRoot) {
  const root = String(projectRoot || "").trim().replace(/[\\/]+$/, "");
  if (!root) {
    return "";
  }
  const separator = root.includes("\\") ? "\\" : "/";
  return `${root}${separator}.flowtrace`;
}

function samePath(left, right) {
  const normalize = (value) => String(value || "").trim().replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
  return Boolean(normalize(left)) && normalize(left) === normalize(right);
}

function renderEntrypoints(entrypoints) {
  if (!entrypoints.length) {
    return `<div class="empty">暂无入口候选。</div>`;
  }
  return `<div class="project-list">${entrypoints.map((item) => `
    <article class="project-row">
      <strong>${escapeHtml(item.label || item.id)}</strong>
      <span>${escapeHtml(item.kind)} · ${escapeHtml(item.file)}:${escapeHtml(item.line)}</span>
    </article>
  `).join("")}</div>`;
}

function renderProjectSummary(project) {
  const identity = project.project_identity || {};
  const summary = project.file_summary || {};
  const packages = identity.package_candidates || [];
  const markers = summary.markers || [];
  const frameworks = summary.framework_hints || [];
  const extensions = summary.by_extension || [];
  const topLevel = summary.top_level || [];
  return `
    <div class="project-summary-grid">
      <article class="project-summary-card">
        <h4>项目身份</h4>
        <div class="project-kv"><span>名称</span><strong>${escapeHtml(identity.name || "未知")}</strong></div>
        <div class="project-kv"><span>Python 文件</span><strong>${escapeHtml(summary.python_files || 0)}</strong></div>
        <div class="project-pills">${packages.length ? packages.map((item) => pill(item)).join("") : `<span class="project-muted">暂无包候选</span>`}</div>
      </article>
      <article class="project-summary-card">
        <h4>项目标记</h4>
        ${markers.length ? `<div class="project-mini-list">${markers.map((item) => `
          <div><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(item.path)} · ${escapeHtml(item.kind)}</span></div>
        `).join("")}</div>` : `<div class="empty">暂无常见项目标记。</div>`}
      </article>
      <article class="project-summary-card">
        <h4>技术线索</h4>
        ${frameworks.length ? `<div class="project-mini-list">${frameworks.map((item) => `
          <div><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml((item.evidence || []).join("，"))}</span></div>
        `).join("")}</div>` : `<div class="empty">暂无框架线索。</div>`}
      </article>
      <article class="project-summary-card">
        <h4>文件类型</h4>
        <div class="project-pills">${extensions.length ? extensions.map((item) => pill(`${item.extension} ${item.count}`)).join("") : `<span class="project-muted">暂无文件统计</span>`}</div>
      </article>
    </div>
    <div class="project-tree-strip">
      ${topLevel.length ? topLevel.map((item) => `
        <div class="project-tree-item">
          <strong>${escapeHtml(item.name)}</strong>
          <span>${escapeHtml(item.total_files)} 文件 · ${escapeHtml(item.python_files)} Python</span>
        </div>
      `).join("") : `<div class="empty">暂无顶层目录。</div>`}
    </div>
  `;
}

function pill(value) {
  return `<span class="project-pill">${escapeHtml(value)}</span>`;
}

function renderModules(modules) {
  if (!modules.length) {
    return `<div class="empty">暂无模块。</div>`;
  }
  return `<div class="project-list">${modules.map((item) => `
    <article class="project-row">
      <strong>${escapeHtml(item.name)}</strong>
      <span>${escapeHtml(item.file)} · 函数 ${escapeHtml(item.function_count)} · 类 ${escapeHtml(item.class_count)} · 声明方法 ${escapeHtml(item.declared_method_count)}</span>
    </article>
  `).join("")}</div>`;
}

function renderCoverage(coverage) {
  const covered = coverage.covered_methods || [];
  const uncovered = coverage.uncovered_methods || [];
  const runtimeOnly = coverage.runtime_only_methods || [];
  return `
    <div class="coverage-grid">
      ${coverageColumn("已覆盖", covered, "pass")}
      ${coverageColumn("未覆盖", uncovered, "warn")}
      ${coverageColumn("仅运行时发现", runtimeOnly, "neutral")}
    </div>
  `;
}

function coverageColumn(title, items, tone) {
  return `
    <div class="coverage-column ${tone}">
      <h4>${escapeHtml(title)} <span>${items.length}</span></h4>
      ${items.length ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : `<div class="empty">暂无</div>`}
    </div>
  `;
}

function renderScanErrors(errors) {
  if (!errors.length) {
    return `<div class="empty">暂无扫描错误。</div>`;
  }
  return `<div class="project-list">${errors.map((item) => `
    <article class="project-row error">
      <strong>${escapeHtml(item.file)}</strong>
      <span>${escapeHtml(item.error)}: ${escapeHtml(item.message)}</span>
    </article>
  `).join("")}</div>`;
}
