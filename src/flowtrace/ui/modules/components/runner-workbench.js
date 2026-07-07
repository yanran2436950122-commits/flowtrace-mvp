import { escapeHtml } from "../utils/html.js";

const STAGES = [
  { key: "runner_real_execution_unlock_phrase_readiness", title: "解锁短语", payload: "runnerRealExecutionUnlockPhraseReadiness" },
  { key: "runner_real_execution_pre_unlock_evidence_packet_indexes", title: "证据包", payload: "runnerRealExecutionPreUnlockEvidencePacketIndexes" },
  { key: "runner_real_execution_pre_unlock_review_checklists", title: "审阅清单", payload: "runnerRealExecutionPreUnlockReviewChecklists" },
  { key: "runner_real_execution_pre_unlock_reviewer_role_maps", title: "角色映射", payload: "runnerRealExecutionPreUnlockReviewerRoleMaps" },
  { key: "runner_real_execution_pre_unlock_reviewer_signoff_rubrics", title: "签核标准", payload: "runnerRealExecutionPreUnlockReviewerSignoffRubrics" },
  { key: "runner_real_execution_pre_unlock_signoff_evidence_bindings", title: "Evidence binding", payload: "runnerRealExecutionPreUnlockSignoffEvidenceBindings" },
  { key: "runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers", title: "Entry ledger", payload: "runnerRealExecutionPreUnlockImplementationEntryReadinessLedgers" },
  { key: "runner_real_execution_pre_unlock_round10_minimal_scope_previews", title: "Round 10 preview", payload: "runnerRealExecutionPreUnlockRound10MinimalScopePreviews" },
  { key: "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts", title: "Unlock receipt", payload: "runnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts" },
  { key: "runner_real_execution_pre_round10_locked_handoff_summaries", title: "Locked summary", payload: "runnerRealExecutionPreRound10LockedHandoffSummaries" },
  { key: "runner_real_execution_round10_explicit_unlock_checkpoints", title: "Unlock checkpoint", payload: "runnerRealExecutionRound10ExplicitUnlockCheckpoints" },
  { key: "runner_real_execution_round10_unlock_decision_mirrors", title: "Unlock decision", payload: "runnerRealExecutionRound10UnlockDecisionMirrors" },
  { key: "run_profiles", title: "运行配置", payload: "runProfiles" },
  { key: "run_preflight", title: "安全预检", payload: "runPreflight" },
  { key: "run_execution_gate", title: "最终确认", payload: "runExecutionGate" },
  { key: "runner_plan", title: "Runner 计划", payload: "runnerPlan" },
  { key: "execution_requests", title: "执行请求", payload: "executionRequests" },
  { key: "runner_sessions", title: "会话草案", payload: "runnerSessions" },
  { key: "runner_launch_snapshots", title: "启动快照", payload: "runnerLaunchSnapshots" },
  { key: "runner_dry_runs", title: "Dry-run", payload: "runnerDryRuns" },
  { key: "runner_real_executions", title: "Real execution", payload: "runnerRealExecutions" },
  { key: "runner_cancel_timeout_real_apis", title: "Cancel/timeout API", payload: "runnerCancelTimeoutRealApis" },
  { key: "runner_first_real_tests", title: "First real test", payload: "runnerFirstRealTests" },
  { key: "runner_process_lifecycles", title: "Lifecycle", payload: "runnerProcessLifecycles" },
  { key: "runner_stream_captures", title: "Stream capture", payload: "runnerStreamCaptures" },
  { key: "runner_event_writers", title: "Event writer", payload: "runnerEventWriters" },
  { key: "runner_audit_persistences", title: "Audit persistence", payload: "runnerAuditPersistences" },
  { key: "runner_audit_integrity_replay_verifications", title: "Integrity replay", payload: "runnerAuditIntegrityReplayVerifications" },
  { key: "runner_verification_discrepancy_reports", title: "Discrepancy reports", payload: "runnerVerificationDiscrepancyReports" },
  { key: "runner_launch_controls", title: "启动开关", payload: "runnerLaunchControls" },
  { key: "runner_runtime_policies", title: "运行策略", payload: "runnerRuntimePolicies" },
  { key: "runner_execution_configs", title: "执行配置", payload: "runnerExecutionConfigs" },
  { key: "runner_execution_config_checks", title: "配置检查", payload: "runnerExecutionConfigChecks" },
  { key: "runner_config_schema_stabilizations", title: "配置 Schema", payload: "runnerConfigSchemaStabilizations" },
  { key: "runner_config_field_contract_views", title: "字段契约", payload: "runnerConfigFieldContractViews" },
  { key: "runner_config_compatibility_reports", title: "配置兼容", payload: "runnerConfigCompatibilityReports" },
  { key: "runner_service_flag_audits", title: "服务开关", payload: "runnerServiceFlagAudits" },
  { key: "runner_log_directory_policies", title: "日志目录", payload: "runnerLogDirectoryPolicies" },
  { key: "runner_log_retention_policies", title: "保留策略", payload: "runnerLogRetentionPolicies" },
  { key: "runner_log_cleanup_previews", title: "清理预览", payload: "runnerLogCleanupPreviews" },
  { key: "runner_log_cleanup_confirmations", title: "清理确认", payload: "runnerLogCleanupConfirmations" },
  { key: "runner_log_cleanup_audit_trails", title: "清理审计", payload: "runnerLogCleanupAuditTrails" },
  { key: "runner_log_cleanup_execution_plans", title: "清理计划", payload: "runnerLogCleanupExecutionPlans" },
  { key: "runner_governance_readiness", title: "治理就绪", payload: "runnerGovernanceReadiness" },
  { key: "runner_execution_adapter_contracts", title: "适配器合约", payload: "runnerExecutionAdapterContracts" },
  { key: "runner_launch_api_contracts", title: "启动 API 合约", payload: "runnerLaunchApiContracts" },
  { key: "runner_execution_adapter_reviews", title: "适配器审查", payload: "runnerExecutionAdapterReviews" },
  { key: "runner_final_block_matrices", title: "最终阻断", payload: "runnerFinalBlockMatrices" },
  { key: "runner_authorization_unlock_audits", title: "授权解锁", payload: "runnerAuthorizationUnlockAudits" },
  { key: "runner_implementation_gap_checklists", title: "实现差距", payload: "runnerImplementationGapChecklists" },
  { key: "runner_cancel_timeout_contracts", title: "取消超时", payload: "runnerCancelTimeoutContracts" },
  { key: "runner_session_state_schemas", title: "会话状态", payload: "runnerSessionStateSchemas" },
  { key: "runner_real_test_readiness", title: "真实测试准入", payload: "runnerRealTestReadiness" },
  { key: "runner_real_test_authorization_checklists", title: "授权检查", payload: "runnerRealTestAuthorizationChecklists" },
  { key: "runner_real_test_authorization_packages", title: "授权包", payload: "runnerRealTestAuthorizationPackages" },
  { key: "runner_real_test_sandbox_policies", title: "沙箱策略", payload: "runnerRealTestSandboxPolicies" },
  { key: "runner_real_test_final_checklists", title: "最终清单", payload: "runnerRealTestFinalChecklists" },
  { key: "runner_real_test_ui_previews", title: "UI 预演", payload: "runnerRealTestUiPreviews" },
  { key: "runner_real_execution_stage_boundary_reviews", title: "边界复核", payload: "runnerRealExecutionStageBoundaryReviews" },
  { key: "runner_real_execution_unlock_material_reviews", title: "解锁材料", payload: "runnerRealExecutionUnlockMaterialReviews" },
  { key: "runner_real_execution_implementation_plans", title: "实现计划", payload: "runnerRealExecutionImplementationPlans" },
  { key: "runner_real_execution_scope_diff_audits", title: "范围差异", payload: "runnerRealExecutionScopeDiffAudits" },
  { key: "runner_execution_adapter_implementation_audits", title: "适配器审计", payload: "runnerExecutionAdapterImplementationAudits" },
  { key: "runner_process_lifecycle_implementation_audits", title: "进程审计", payload: "runnerProcessLifecycleImplementationAudits" },
  { key: "runner_stream_capture_implementation_audits", title: "输出审计", payload: "runnerStreamCaptureImplementationAudits" },
  { key: "runner_event_writer_implementation_audits", title: "事件审计", payload: "runnerEventWriterImplementationAudits" },
  { key: "runner_audit_persistence_implementation_audits", title: "审计持久化", payload: "runnerAuditPersistenceImplementationAudits" },
  { key: "runner_audit_integrity_replay_verification_audits", title: "回放校验", payload: "runnerAuditIntegrityReplayVerificationAudits" },
  { key: "runner_verification_discrepancy_report_audits", title: "差异报告", payload: "runnerVerificationDiscrepancyReportAudits" },
  { key: "runner_real_launch_final_gate_audits", title: "最终闸门", payload: "runnerRealLaunchFinalGateAudits" },
  { key: "runner_evidence_gap_indexes", title: "缺口索引", payload: "runnerEvidenceGapIndexes" },
  { key: "runner_development_path_anchors", title: "路径锚点", payload: "runnerDevelopmentPathAnchors" },
  { key: "runner_real_execution_touchpoint_inventories", title: "触点清单", payload: "runnerRealExecutionTouchpointInventories" },
  { key: "runner_real_execution_touchpoint_coverage_indexes", title: "触点索引", payload: "runnerRealExecutionTouchpointCoverageIndexes" },
  { key: "runner_real_execution_touchpoint_gap_links", title: "触点缺口", payload: "runnerRealExecutionTouchpointGapLinks" },
  { key: "runner_real_execution_touchpoint_unlock_matrices", title: "解锁矩阵", payload: "runnerRealExecutionTouchpointUnlockMatrices" },
  { key: "runner_config_remediation_summaries", title: "配置修复", payload: "runnerConfigRemediationSummaries" },
  { key: "runner_config_field_coverage_indexes", title: "Config index", payload: "runnerConfigFieldCoverageIndexes" },
];

const HARD_BOUNDARY_ITEMS = [
  "仅允许 examples/realistic_projects 低风险样例项目",
  "真实启动必须提供 RUN TARGET PROJECT 输入确认",
  "只接受 argv 数组，拒绝 shell 字符串",
  "stdout/stderr 仅写入 FlowTrace trace 目录",
  "cancel/timeout POST API 仅控制当前活动低风险样例 launch_id",
  "不写用户项目源码或配置",
];

const FILTERS = [
  { id: "all", label: "全部" },
  { id: "blocked", label: "阻断" },
  { id: "ready", label: "就绪" },
  { id: "missing", label: "未加载" },
  { id: "governance", label: "治理" },
];

export function renderRunnerWorkbench(container, data = {}) {
  container.className = "runner-workbench";
  const stageItems = STAGES.map((stage) => stageView(stage, data[stage.payload])).filter(Boolean);
  const safety = collectSafety(data);
  const currentStage = selectCurrentStage(stageItems, safety);
  const blockers = collectBlockers(data, currentStage);
  const nextAction = collectNextAction(data, currentStage);
  const selectedStage = currentStage || stageItems[0] || null;
  const criticalPath = buildCriticalPath(stageItems, safety);
  const criticalStageKeys = new Set([
    ...criticalPath.map((step) => step.key),
    ...blockers.map((blocker) => blocker.stageKey),
  ].filter(Boolean));
  const stageSummaryCounts = countStageKinds(stageItems);

  container.innerHTML = `
    <section class="runner-workbench-hero">
      <div class="runner-workbench-title">
        <span>Runner 工作台</span>
        <strong>${escapeHtml(statusTitle(currentStage, safety))}</strong>
        <p>${escapeHtml(nextAction.action)}</p>
      </div>
      <div class="runner-workbench-metrics">
        ${metric("阶段", stageItems.filter((item) => item.available).length, `${stageItems.length}`)}
        ${metric("可启动", safety.launchableCount, "0")}
        ${metric("活跃会话", safety.activeSessionCount, "0")}
        ${metric("已注册端点", safety.registeredEndpointCount, "0")}
      </div>
    </section>

    <section class="runner-workbench-grid">
      <article class="runner-workbench-panel runner-workbench-status">
        <div class="runner-workbench-panel-heading">
          <strong>当前状态</strong>
          <span>${escapeHtml(currentStage?.status || "unknown")}</span>
        </div>
        <div class="runner-workbench-kv">
          ${kv("当前阶段", currentStage?.title || "暂无")}
          ${kv("下一步", nextAction.title)}
          ${kv("保存配置", safety.savedProfileCount)}
          ${kv("报告数量", currentStage?.reportCount ?? 0)}
        </div>
      </article>

      <article class="runner-workbench-panel">
        <div class="runner-workbench-panel-heading">
          <strong>阻断原因</strong>
          <span>${blockers.length} 项</span>
        </div>
        <div class="runner-workbench-list">
          ${blockers.length ? blockers.map((item) => `
            <div class="runner-workbench-list-item ${escapeHtml(item.severity)} ${item.stageKey ? "clickable" : ""}" ${item.stageKey ? `data-runner-blocker data-stage-key="${escapeHtml(item.stageKey)}" data-evidence-title="${escapeHtml(item.evidenceTitle || "")}" tabindex="0" role="button" aria-label="查看${escapeHtml(item.title)}证据"` : ""}>
              <strong>${escapeHtml(item.title)}</strong>
              <span>${escapeHtml(item.detail)}</span>
            </div>
          `).join("") : `<div class="runner-workbench-empty">暂无阻断信息。</div>`}
        </div>
      </article>

      <article class="runner-workbench-panel runner-workbench-boundary">
        <div class="runner-workbench-panel-heading">
          <strong>执行边界</strong>
          <span>受控</span>
        </div>
        <div class="runner-workbench-boundary-list">
          ${HARD_BOUNDARY_ITEMS.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
        </div>
      </article>
    </section>

    <section class="runner-workbench-panel runner-workbench-path-panel">
      <div class="runner-workbench-panel-heading">
        <strong>关键路径</strong>
        <span>优先处理最早阻断点</span>
      </div>
      <div class="runner-workbench-stage-summary" data-runner-stage-summary>
        ${stageChip("阻断", stageSummaryCounts.blocked, "blocked")}
        ${stageChip("警告", stageSummaryCounts.warn, "warn")}
        ${stageChip("就绪", stageSummaryCounts.ready, "ready")}
        ${stageChip("未加载", stageSummaryCounts.missing, "missing")}
      </div>
      <div class="runner-workbench-path" data-runner-critical-path>
        ${criticalPath.map((step, index) => `
          <article class="runner-workbench-path-step ${escapeHtml(step.kind)} ${step.key === selectedStage?.key ? "selected" : ""}" data-runner-path-step data-stage-key="${escapeHtml(step.key || "")}" tabindex="0" role="button" aria-label="查看${escapeHtml(step.title)}阶段详情">
            <small>${index + 1}</small>
            <div>
              <strong>${escapeHtml(step.title)}</strong>
              <span>${escapeHtml(step.detail)}</span>
            </div>
          </article>
        `).join("")}
      </div>
    </section>

    <section class="runner-workbench-panel">
      <div class="runner-workbench-panel-heading">
        <strong>阶段流</strong>
        <span>${stageItems.length} 层</span>
      </div>
      <div class="runner-workbench-toolbar" role="toolbar" aria-label="Runner 阶段筛选">
        ${FILTERS.map((filter) => `
          <button type="button" class="${filter.id === "all" ? "active" : ""}" data-runner-stage-filter="${escapeHtml(filter.id)}">
            ${escapeHtml(filter.label)}
          </button>
        `).join("")}
      </div>
      <div class="runner-workbench-viewbar" role="toolbar" aria-label="Runner 阶段显示">
        <button type="button" class="active" data-runner-stage-density="standard">标准密度</button>
        <button type="button" data-runner-stage-density="dense">紧凑密度</button>
        <button type="button" class="active" data-runner-stage-scope="all">全部阶段</button>
        <button type="button" data-runner-stage-scope="critical">关键阶段</button>
        <label class="runner-stage-search">
          <span>搜索阶段</span>
          <input type="search" data-runner-stage-search placeholder="名称 / 状态 / key" autocomplete="off">
        </label>
        <button type="button" data-runner-stage-search-clear disabled>清空</button>
        <small data-runner-stage-visible-count>${stageItems.length} 项</small>
      </div>
      <div class="runner-stage-detail" data-runner-stage-detail>
        ${renderStageDetail(selectedStage)}
      </div>
      <div class="runner-stage-flow">
        <div class="runner-stage-empty" data-runner-stage-empty hidden>未找到匹配阶段。</div>
        ${stageItems.map((stage) => `
          <article class="runner-stage-card ${escapeHtml(stage.kind)} ${stage.key === selectedStage?.key ? "selected" : ""}" data-runner-stage-card data-stage-key="${escapeHtml(stage.key)}" data-stage-kind="${escapeHtml(stage.kind)}" data-stage-group="${escapeHtml(stage.group)}" data-stage-critical="${criticalStageKeys.has(stage.key) ? "true" : "false"}" data-stage-search="${escapeHtml(stageSearchText(stage))}" tabindex="0">
            <strong>${escapeHtml(stage.title)}</strong>
            <span>${escapeHtml(stage.status)}</span>
            <small>${escapeHtml(stage.summary)}</small>
          </article>
        `).join("")}
      </div>
    </section>
  `;
  installStageFilters(container);
  installStageSelection(container, stageItems);
  installCriticalPathNavigation(container, stageItems);
  installBlockerNavigation(container, stageItems);
  installEvidenceGapNavigation(container, stageItems);
  installAuditSummaryCopy(container, stageItems);
  installDetailModeToggle(container);
  installStageViewControls(container);
  applyStageVisibility(container);
}

function stageView(stage, payload) {
  const status = payload ? (payload.status || "available") : "not_loaded";
  const summary = payload?.summary || {};
  return {
    ...stage,
    available: Boolean(payload),
    status,
    kind: stageKind(status, summary),
    group: stageGroup(stage.key),
    reportCount: numberValue(summary.report_count),
    summary: stageSummary(summary),
    detail: stageDetail(payload),
    nextAction: payload?.next_action || null,
    payload,
  };
}

function selectCurrentStage(stageItems, safety) {
  if (!safety.savedProfileCount) {
    return stageItems.find((stage) => stage.key === "run_profiles") || stageItems[0] || null;
  }
  return stageItems.find((stage) => stage.available && stage.kind === "blocked")
    || [...stageItems].reverse().find((stage) => stage.available)
    || stageItems[0]
    || null;
}

function buildCriticalPath(stageItems, safety) {
  const byKey = new Map(stageItems.map((stage) => [stage.key, stage]));
  const governanceLoaded = stageItems.filter((stage) => stage.available && stage.group === "governance").length;
  const governanceTotal = stageItems.filter((stage) => stage.group === "governance").length;
  return [
    pathStep("运行配置", byKey.get("run_profiles"), safety.savedProfileCount ? "已保存运行配置，可进入预检链路。" : "尚未保存运行配置，先在接入向导保存 profile。", false),
    pathStep("确认链路", byKey.get("run_execution_gate") || byKey.get("run_preflight"), safety.savedProfileCount ? "检查预检确认、最终确认和二次确认状态。" : "等待运行配置后才生成确认链路。", false),
    pathStep("治理链路", byKey.get("runner_governance_readiness"), `已加载 ${governanceLoaded}/${governanceTotal} 个治理阶段。`, false),
    pathStep("真实执行", byKey.get("runner_real_executions") || byKey.get("runner_implementation_gap_checklists"), safety.launchableCount ? "存在可启动项，启动仍需要输入确认。" : "真实启动仍为 0，继续补齐 profile/session/snapshot/dry-run 前置。", false),
  ];
}

function pathStep(title, stage, fallbackDetail, preferStageAction = true) {
  return {
    key: stage?.key || "",
    title,
    kind: stage?.kind || "missing",
    detail: preferStageAction ? (stage?.nextAction?.action || fallbackDetail || stage?.summary) : (fallbackDetail || stage?.summary),
  };
}

function countStageKinds(stageItems) {
  return stageItems.reduce((counts, stage) => {
    counts[stage.kind] = (counts[stage.kind] || 0) + 1;
    return counts;
  }, { blocked: 0, warn: 0, ready: 0, missing: 0 });
}

function stageKind(status, summary) {
  if (!status || status === "not_loaded") {
    return "missing";
  }
  if (numberValue(summary.launchable_count) > 0) {
    return "ready";
  }
  if (status === "no_saved_profiles" || status.includes("disabled") || status.includes("required")) {
    return "blocked";
  }
  if (status.includes("ready") || status.includes("present")) {
    return "warn";
  }
  return "blocked";
}

function stageGroup(key) {
  if (key.includes("log")) {
    return "governance";
  }
  if (key.includes("governance") || key.includes("contract") || key.includes("review") || key.includes("matrix") || key.includes("audit") || key.includes("gap") || key.includes("schema") || key.includes("readiness") || key.includes("authorization") || key.includes("checklist") || key.includes("real_test")) {
    return "governance";
  }
  if (key.includes("execution") || key.includes("session") || key.includes("launch") || key.includes("dry")) {
    return "execution";
  }
  return "setup";
}

function stageDetail(payload) {
  if (!payload) {
    return {
      schema: "not_loaded",
      nextTitle: "未加载",
      nextAction: "当前 bootstrap payload 中没有这个阶段的数据。",
      safety: [],
    };
  }
  const safety = payload.safety || {};
  return {
    schema: payload.schema_version || "unknown",
    nextTitle: localizeRunnerText(payload.next_action?.title || payload.status || "暂无下一步"),
    nextAction: localizeRunnerText(payload.next_action?.action || payload.status || ""),
    evidence: stageEvidence(payload),
    safety: stageSafetyGroups(safety),
  };
}

function localizeRunnerText(value) {
  const text = String(value ?? "");
  const replacements = new Map([
    ["Save a run profile first", "先保存运行配置"],
    ["Save a run profile and generate authorization unlock audits before listing implementation gaps.", "先保存运行配置，并生成授权解锁审计后再查看实现差距。"],
    ["Save a run profile and complete the runner governance chain before aggregating final blockers.", "先保存运行配置，并完成 Runner 治理链路后再汇总最终阻断。"],
    ["Save a run profile and generate final block matrices before auditing authorization unlocks.", "先保存运行配置，并生成最终阻断矩阵后再审计授权解锁。"],
    ["Save a run profile before preparing runner sessions.", "先保存运行配置后再准备 Runner 会话草案。"],
    ["Save a run profile before preparing launch snapshots.", "先保存运行配置后再准备启动快照。"],
    ["Save a run profile before preparing dry-run runner checks.", "先保存运行配置后再准备 dry-run 检查。"],
    ["Continue read-only governance", "继续只读治理"],
    ["Execution adapter implementation", "执行适配器实现"],
    ["Launch POST API implementation", "启动 POST API 实现"],
    ["Runner session state persistence", "Runner 会话状态持久化"],
    ["stdout/stderr stream capture", "stdout/stderr 流捕获"],
    ["Runner event log writer", "Runner 事件日志写入器"],
    ["Cancel and timeout endpoints", "取消与超时端点"],
    ["Audit persistence", "审计持久化"],
    ["Execution console UI", "执行控制台 UI"],
    ["tokenized argv process adapter with shell strings rejected", "使用 argv token 的进程适配器，并拒绝 shell 字符串"],
    ["idempotent launch endpoint guarded by profile, snapshot, and authorization checks", "幂等启动端点，受 profile、快照和授权检查保护"],
    ["pending/running/completed/failed/cancelled/timeout states persisted", "持久化 pending/running/completed/failed/cancelled/timeout 状态"],
    ["bounded stdout/stderr chunk capture and UI-readable stream state", "有边界的 stdout/stderr 分片捕获，并提供 UI 可读流状态"],
    ["structured runner events for launch, chunks, exit, failure, cancel, and timeout", "为启动、分片、退出、失败、取消和超时写入结构化 Runner 事件"],
    ["idempotent cancel and deterministic timeout finalization", "幂等取消与确定性超时收束"],
    ["append-only audit events for authorization, launch, cancel, timeout, and completion", "为授权、启动、取消、超时和完成写入追加式审计事件"],
    ["status, blockers, logs, cancel, timeout, and result summary visible to the user", "向用户展示状态、阻断、日志、取消、超时和结果摘要"],
    ["real launch API", "真实启动 API"],
    ["process execution adapter", "进程执行适配器"],
    ["live stdout/stderr writer", "实时 stdout/stderr 写入器"],
    ["cancel endpoint", "取消端点"],
    ["completion refresh worker", "完成状态刷新 worker"],
    ["audit-log persistence", "审计日志持久化"],
    ["missing", "缺失"],
    ["declared_only", "仅声明"],
    ["future_review_required", "需要未来审查"],
    ["implementing runner adapter in this layer", "在当前只读层实现 Runner 适配器"],
    ["registering POST /api/project/runner/launch", "注册 POST /api/project/runner/launch"],
    ["starting target project process", "启动目标项目进程"],
    ["calling execution adapter", "调用执行适配器"],
    ["opening stdout/stderr files", "打开 stdout/stderr 文件"],
    ["writing runner event logs", "写入 Runner 事件日志"],
    ["writing audit logs", "写入审计日志"],
    ["writing user project files", "写入用户项目文件"],
    ["loading execution adapter", "加载执行适配器"],
    ["creating subprocess", "创建子进程"],
    ["collecting or storing human authorization", "收集或保存人工授权"],
    ["granting launch permission", "授予启动权限"],
    ["registering POST /api/project/runner/launch", "注册 POST /api/project/runner/launch"],
    ["deleting or rotating logs", "删除或轮转日志"],
    ["reading log files", "读取日志文件"],
    ["writing runner events", "写入 Runner 事件"],
    ["launch_api_not_registered", "启动 API 未注册"],
    ["runner_adapter_not_implemented", "Runner 适配器未实现"],
    ["adapter_review_is_preimplementation", "适配器仍处于实现前审查"],
    ["process_creation_disabled", "进程创建被禁用"],
    ["command_execution_disabled", "命令执行被禁用"],
    ["stdout_stderr_writes_disabled", "stdout/stderr 写入被禁用"],
    ["runner_event_writes_disabled", "Runner 事件写入被禁用"],
    ["log_cleanup_execution_disabled", "日志清理执行被禁用"],
    ["audit_log_persistence_disabled", "审计日志持久化被禁用"],
    ["user_project_writes_disabled", "用户项目写入被禁用"],
    ["explicit service flag enablement", "显式启用服务开关"],
    ["valid runner configuration file", "有效 Runner 配置文件"],
    ["fresh launch snapshot", "新鲜启动快照"],
    ["implemented execution adapter", "已实现执行适配器"],
    ["registered launch POST API", "已注册启动 POST API"],
    ["live stdout/stderr sink", "实时 stdout/stderr 接收端"],
    ["runner event log writer", "Runner 事件日志写入器"],
    ["cancel and timeout endpoints", "取消与超时端点"],
    ["audit-log persistence", "审计日志持久化"],
    ["new human authorization round", "新一轮人工授权"],
    ["human authorization round id", "人工授权轮次 ID"],
    ["operator identity", "操作人身份"],
    ["approved profile id", "已批准 profile ID"],
    ["approved launch snapshot id", "已批准启动快照 ID"],
    ["typed consent phrase", "手动输入确认短语"],
    ["approval timestamp", "批准时间戳"],
    ["scope of permission", "授权范围"],
    ["revocation policy", "撤销策略"],
    ["implemented execution adapter review", "执行适配器实现审查"],
    ["registered launch POST API review", "启动 POST API 注册审查"],
    ["service flag enabled review", "服务开关启用审查"],
    ["valid runner config check", "有效 Runner 配置检查"],
    ["stdout/stderr sink review", "stdout/stderr 接收端审查"],
    ["runner event writer review", "Runner 事件写入器审查"],
    ["audit-log persistence review", "审计日志持久化审查"],
    ["cancel and timeout endpoint review", "取消与超时端点审查"],
  ]);
  return replacements.get(text) || text;
}

function renderStageDetail(stage) {
  if (!stage) {
    return `<div class="runner-workbench-empty">暂无阶段详情。</div>`;
  }
  return `
    <div class="runner-stage-detail-heading">
      <strong>${escapeHtml(stage.title)}</strong>
      <div class="runner-stage-detail-actions">
        <span>${escapeHtml(stage.status)}</span>
        <button type="button" data-runner-detail-mode aria-pressed="false">压缩视图</button>
        <button type="button" data-runner-copy-summary data-stage-key="${escapeHtml(stage.key)}">复制摘要</button>
        <small data-runner-copy-status></small>
      </div>
    </div>
    <div class="runner-workbench-kv">
      ${kv("结构版本", stage.detail.schema)}
      ${kv("下一步", stage.detail.nextTitle)}
      ${kv("动作", stage.detail.nextAction)}
      ${kv("摘要", stage.summary)}
    </div>
    ${renderSafetyGroups(stage.detail.safety)}
    ${renderStageEvidence(stage.detail.evidence)}
  `;
}

function stageSafetyGroups(safety) {
  const definitions = [
    {
      title: "执行边界",
      keys: ["executes_commands", "creates_process", "implements_runner", "runner_implemented", "imports_adapter", "calls_execution_adapter"],
    },
    {
      title: "API 边界",
      keys: ["launch_enabled", "launch_api_available", "cancel_timeout_real_api", "registers_post_api", "registers_launch_api", "registers_cancel_api", "registers_timeout_api", "accepts_pid", "accepts_shell"],
    },
    {
      title: "进程控制",
      keys: ["controls_process", "cancels_process", "sends_process_signal", "kills_process", "schedules_timeout"],
    },
    {
      title: "会话边界",
      keys: ["creates_session", "stores_session_state", "mutates_session_state", "reads_session_state_store", "writes_session_state_store", "stores_launch_state"],
    },
    {
      title: "日志与审计",
      keys: ["opens_stdout_stderr", "writes_runner_events", "reads_log_files", "writes_logs", "deletes_logs", "rotates_logs", "renames_logs", "truncates_logs", "scans_log_directory", "writes_audit_log", "reads_audit_log"],
    },
    {
      title: "项目写入",
      keys: ["writes_user_project", "creates_config_file", "writes_code"],
    },
    {
      title: "只读声明",
      keys: Object.keys(safety).filter((key) => key.endsWith("_only")),
    },
  ];
  return definitions.map((definition) => {
    const items = definition.keys
      .filter((key, index, keys) => keys.indexOf(key) === index && Object.prototype.hasOwnProperty.call(safety, key))
      .map((key) => safetyFlag(key, safety[key]));
    return {
      title: definition.title,
      items,
      blockedCount: items.filter((item) => item.state === "blocked").length,
      attentionCount: items.filter((item) => item.state === "attention").length,
    };
  }).filter((group) => group.items.length);
}

function safetyFlag(key, value) {
  const label = safetyFlagLabel(key);
  const expectedFalse = !key.endsWith("_only");
  if (expectedFalse && value === false) {
    return { key, label, value, state: "blocked", text: "已阻断" };
  }
  if (!expectedFalse && value === true) {
    return { key, label, value, state: "readonly", text: "只读声明" };
  }
  return { key, label, value, state: "attention", text: value ? "需要审查" : "未声明" };
}

function safetyFlagLabel(key) {
  const labels = new Map([
    ["executes_commands", "命令执行"],
    ["creates_process", "进程创建"],
    ["implements_runner", "Runner 实现"],
    ["runner_implemented", "Runner 已实现"],
    ["imports_adapter", "导入适配器"],
    ["calls_execution_adapter", "调用适配器"],
    ["launch_enabled", "启动开关"],
    ["launch_api_available", "启动 API"],
    ["cancel_timeout_real_api", "取消/超时 API"],
    ["registers_post_api", "注册 POST API"],
    ["registers_launch_api", "注册启动 API"],
    ["registers_cancel_api", "注册取消 API"],
    ["registers_timeout_api", "注册超时 API"],
    ["accepts_pid", "接受 PID"],
    ["accepts_shell", "接受 shell"],
    ["controls_process", "控制进程"],
    ["cancels_process", "取消进程"],
    ["sends_process_signal", "发送进程信号"],
    ["kills_process", "强杀进程"],
    ["schedules_timeout", "调度超时"],
    ["creates_session", "创建会话"],
    ["stores_session_state", "保存会话状态"],
    ["mutates_session_state", "修改会话状态"],
    ["reads_session_state_store", "读取会话状态库"],
    ["writes_session_state_store", "写入会话状态库"],
    ["stores_launch_state", "保存启动状态"],
    ["opens_stdout_stderr", "打开 stdout/stderr"],
    ["writes_runner_events", "写 Runner 事件"],
    ["reads_log_files", "读日志文件"],
    ["writes_logs", "写日志"],
    ["deletes_logs", "删日志"],
    ["rotates_logs", "轮转日志"],
    ["renames_logs", "重命名日志"],
    ["truncates_logs", "截断日志"],
    ["scans_log_directory", "扫描日志目录"],
    ["writes_audit_log", "写审计日志"],
    ["reads_audit_log", "读审计日志"],
    ["writes_user_project", "写用户项目"],
    ["creates_config_file", "创建配置文件"],
    ["writes_code", "写代码"],
    ["governance_readiness_only", "仅治理就绪检查"],
    ["final_block_matrix_only", "仅最终阻断矩阵"],
    ["authorization_unlock_audit_only", "仅授权解锁审计"],
    ["implementation_gap_checklist_only", "仅实现差距清单"],
    ["cancel_timeout_contract_only", "仅取消超时合约"],
    ["session_state_schema_only", "仅会话状态 schema"],
    ["config_field_coverage_index_only", "Config field coverage index only"],
  ]);
  return labels.get(key) || localizeRunnerText(key);
}

function renderSafetyGroups(groups) {
  if (!groups?.length) {
    return `<div class="runner-stage-safety-empty">暂无安全标记。</div>`;
  }
  return `
    <div class="runner-stage-safety">
      <div class="runner-stage-safety-heading">
        <strong>安全边界</strong>
        <span>${groups.length} 组</span>
      </div>
      <div class="runner-stage-safety-groups">
        ${groups.map((group) => `
          <div class="runner-stage-safety-group">
            <div class="runner-stage-safety-group-heading">
              <strong>${escapeHtml(group.title)}</strong>
              <span>${group.blockedCount} 已阻断${group.attentionCount ? ` / ${group.attentionCount} 待审查` : ""}</span>
            </div>
            <div class="runner-stage-safety-flags">
              ${group.items.map((item) => `
                <span class="${escapeHtml(item.state)}" title="${escapeHtml(item.key)}=${escapeHtml(item.value)}">
                  ${escapeHtml(item.label)}：${escapeHtml(item.text)}
                </span>
              `).join("")}
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function stageEvidence(payload) {
  if (!payload) {
    return { metrics: [], groups: [], gapEntries: [] };
  }
  const schema = firstSchemaObject(payload);
  const metrics = evidenceMetrics(payload.summary || {});
  const gapEntries = evidenceGapEntries(payload);
  const indexEntries = evidenceIndexEntries(payload);
  const groups = [
    evidenceGroup("配置问题定位", indexEntries),
    evidenceGroup("Target groups", payload.target_groups),
    evidenceGroup("Field filters", payload.filter_groups),
    evidenceGroup("Field coverage", payload.field_indexes),
    evidenceGroup("Field contracts", payload.field_contracts),
    evidenceGroup("Error codes", payload.error_codes),
    evidenceGroup("Sections", payload.sections),
    evidenceGroup("Unlock material columns", schema?.required_material_columns),
    evidenceGroup("Safety condition columns", schema?.required_safety_columns),
    evidenceGroup("Unlock matrix", payload.matrix_entries),
    evidenceGroup("Required unlock phrase", payload.required_unlock_phrase ? [payload.required_unlock_phrase] : []),
    evidenceGroup("Pre-unlock evidence packet", payload.packet_sections),
    evidenceGroup("Pre-unlock review checklist", payload.checklist_items),
    evidenceGroup("Pre-unlock reviewer roles", payload.role_entries),
    evidenceGroup("Pre-unlock sign-off rubric", payload.rubric_entries),
    evidenceGroup("Pre-unlock sign-off evidence bindings", payload.binding_entries),
    evidenceGroup("Pre-unlock implementation entry readiness ledger", payload.ledger_entries),
    evidenceGroup("Pre-unlock round-10 minimal scope preview", payload.preview_entries),
    evidenceGroup("Pre-unlock explicit unlock handoff receipt", payload.receipt_entries),
    evidenceGroup("Pre-round-10 locked handoff summary", payload.handoff_summary_entries),
    evidenceGroup("Round-10 explicit unlock checkpoint", payload.checkpoint_entries),
    evidenceGroup("Round-10 unlock decision mirror", payload.decision_entries),
    evidenceGroup("Active runner processes", payload.active_processes),
    evidenceGroup("First real test schema", payload.first_real_test_schema ? [payload.first_real_test_schema] : []),
    evidenceGroup("阻断动作", schema?.blocked_actions),
    evidenceGroup("阻断维度", schema?.blocking_dimensions),
    evidenceGroup("后续解锁项", schema?.required_future_unlocks),
    evidenceGroup("授权记录要求", schema?.required_authorization_records),
    evidenceGroup("证据要求", schema?.required_evidence),
    evidenceGroup("实现组件", schema?.required_components),
    evidenceGroup("治理层", schema?.required_layers),
    evidenceGroup("未来阻断层", schema?.blocked_until_future_layers),
    evidenceGroup("解锁状态", schema?.unlock_item_states),
    evidenceGroup("Real execution history", payload.executions),
    evidenceGroup("Lifecycle session states", (payload.reports || []).map((report) => report.session_state).filter(Boolean)),
    evidenceGroup("Stream capture states", (payload.reports || []).flatMap((report) => report.streams || [])),
    evidenceGroup("Projected runner events", (payload.reports || []).flatMap((report) => report.events || [])),
    evidenceGroup("Audit persistence records", (payload.reports || []).flatMap((report) => report.audit_records || [])),
    evidenceGroup("Integrity projection checks", (payload.reports || []).flatMap((report) => report.integrity_checks || [])),
    evidenceGroup("Replay projection checks", (payload.reports || []).flatMap((report) => report.replay_checks || [])),
    evidenceGroup("Consistency projection checks", (payload.reports || []).flatMap((report) => report.consistency_checks || [])),
    evidenceGroup("Discrepancy projection reports", (payload.reports || []).flatMap((report) => report.discrepancy_reports || [])),
    evidenceGroup("报告证据", payload.reports),
  ].filter((group) => group.items.length);
  return { metrics, groups, gapEntries, fieldFilters: fieldCoverageFilters(payload) };
}

function firstSchemaObject(payload) {
  return Object.entries(payload)
    .find(([key, value]) => key.endsWith("_schema") && value && typeof value === "object" && !Array.isArray(value))?.[1] || null;
}

function evidenceIndexEntries(payload) {
  const reports = Array.isArray(payload?.reports) ? payload.reports : [];
  return reports.flatMap((report) => Array.isArray(report?.index_entries) ? report.index_entries : []);
}

function evidenceMetrics(summary) {
  const labels = new Map([
    ["saved_profile_count", "保存配置"],
    ["saved_count", "保存配置"],
    ["report_count", "报告"],
    ["blocked_count", "阻断"],
    ["launchable_count", "可启动"],
    ["blocking_reason_count", "阻断原因"],
    ["missing_evidence_count", "缺失证据"],
    ["gap_count", "实现差距"],
    ["component_count", "组件"],
    ["layer_count", "治理层"],
    ["stable_schema_count", "稳定 schema"],
    ["supported_version_count", "支持版本"],
    ["field_contract_count", "字段契约"],
    ["field_count", "字段"],
    ["covered_field_count", "已覆盖字段"],
    ["field_with_issue_count", "问题字段"],
    ["field_with_recommendation_count", "修复字段"],
    ["indexed_issue_count", "索引问题"],
    ["indexed_recommendation_count", "索引修复"],
    ["target_group_count", "目标分组"],
    ["compatibility_rule_count", "兼容规则"],
    ["error_code_count", "错误码"],
    ["compatibility_issue_count", "兼容问题"],
    ["missing_field_count", "缺字段"],
    ["type_mismatch_count", "类型错误"],
    ["unsupported_version_count", "版本不兼容"],
    ["default_violation_count", "默认值偏离"],
    ["registered_endpoint_count", "已注册端点"],
    ["persisted_session_count", "持久会话"],
    ["active_session_count", "活跃会话"],
    ["matrix_entry_count", "Matrix entries"],
    ["locked_matrix_count", "Locked matrix"],
    ["implementation_allowed_count", "Implementation allowed"],
    ["execution_allowed_count", "Execution allowed"],
  ]);
  return Object.entries(summary)
    .filter(([key]) => labels.has(key))
    .map(([key, value]) => ({ label: labels.get(key), value }));
}

function evidenceGapEntries(payload) {
  const reports = Array.isArray(payload?.reports) ? payload.reports : [];
  return reports.flatMap((report) => {
    const entries = Array.isArray(report?.index_entries) ? report.index_entries : [];
    return entries
      .map((entry) => normalizeEvidenceGapEntry(entry, report))
      .filter((entry) => entry.stageKey);
  });
}

function normalizeEvidenceGapEntry(entry, report) {
  if (!entry || typeof entry !== "object") {
    return null;
  }
  const navigation = entry.navigation && typeof entry.navigation === "object" ? entry.navigation : {};
  return {
    kind: localizeRunnerText(entry.kind || "evidence_gap"),
    title: localizeRunnerText(entry.title || entry.key || "未命名缺口"),
    detail: localizeRunnerText(entry.detail || entry.reason || ""),
    status: localizeRunnerText(entry.status || ""),
    profileLabel: localizeRunnerText(report?.label || report?.profile_id || ""),
    stageKey: navigation.stage_key || entry.owner_stage_key || "",
    evidenceTitle: navigation.evidence_group || "",
    itemKey: navigation.item_key || entry.key || "",
  };
}

function evidenceGroup(title, value) {
  const items = Array.isArray(value) ? value : [];
  return {
    title,
    items: items.map(evidenceItem).filter(Boolean).slice(0, 8),
    total: items.length,
  };
}

function fieldCoverageFilters(payload) {
  if (!Array.isArray(payload?.filter_groups) || !Array.isArray(payload?.field_indexes)) {
    return [];
  }
  return payload.filter_groups.filter((item) => item && item.count).slice(0, 8);
}

function evidenceItem(item) {
  const text = evidenceItemText(item);
  if (!text) {
    return null;
  }
  const navigation = item && typeof item === "object" && item.navigation && typeof item.navigation === "object"
    ? item.navigation
    : {};
  return {
    text,
    key: navigation.item_key || item?.key || "",
    filterTags: Array.isArray(item?.filter_tags) ? item.filter_tags : [],
  };
}

function evidenceItemText(item) {
  if (typeof item === "string") {
    return localizeRunnerText(item);
  }
  if (!item || typeof item !== "object") {
    return String(item ?? "");
  }
  if (item.title && item.minimum_evidence) {
    return `${localizeRunnerText(item.title)}：${localizeRunnerText(item.minimum_evidence)}`;
  }
  if (item.label && item.id) {
    return `${item.label} (${item.id})`;
  }
  if (item.key && Array.isArray(item.required_unlock_materials)) {
    return `${localizeRunnerText(item.key)}: ${item.required_unlock_materials.length} materials / ${item.required_safety_conditions?.length || 0} safety conditions`;
  }
  if (item.key && item.status) {
    return `${localizeRunnerText(item.key)}：${localizeRunnerText(item.status)}`;
  }
  if (item.title && item.detail) {
    return `${localizeRunnerText(item.title)}: ${localizeRunnerText(item.detail)}`;
  }
  if (item.error_code && item.field) {
    return `${localizeRunnerText(item.error_code)}: ${localizeRunnerText(item.field)}`;
  }
  return localizeRunnerText(Object.entries(item).map(([key, value]) => `${key}=${value}`).join(" | "));
}

function renderFieldCoverageFilters(filters = []) {
  if (!filters.length) {
    return "";
  }
  return `
    <div class="runner-stage-field-filters" aria-label="Field coverage filters">
      ${filters.map((filter, index) => `
        <button type="button" class="${index === 0 ? "active" : ""}" data-field-coverage-filter="${escapeHtml(filter.key)}">
          ${escapeHtml(filter.title)} <span>${escapeHtml(filter.count)}</span>
        </button>
      `).join("")}
    </div>
  `;
}

function renderStageEvidence(evidence) {
  if (!evidence?.metrics.length && !evidence?.groups.length && !evidence?.gapEntries?.length) {
    return "";
  }
  return `
    <div class="runner-stage-evidence">
      <div class="runner-stage-evidence-heading">
        <strong>只读证据</strong>
        <span>${evidence.groups.length} 组</span>
      </div>
      ${evidence.metrics.length ? `
        <div class="runner-stage-evidence-metrics">
          ${evidence.metrics.map((item) => `
            <span><strong>${escapeHtml(item.value ?? 0)}</strong>${escapeHtml(item.label)}</span>
          `).join("")}
        </div>
      ` : ""}
      ${renderEvidenceGapTargets(evidence.gapEntries)}
      ${renderFieldCoverageFilters(evidence.fieldFilters)}
      <div class="runner-stage-evidence-groups">
        ${evidence.groups.map((group, index) => `
          <details ${index === 0 ? "open" : ""}>
            <summary>${escapeHtml(group.title)} <span>${group.items.length}/${group.total}</span></summary>
            <ul>
              ${group.items.map((item) => `<li ${item.key ? `data-evidence-item-key="${escapeHtml(item.key)}"` : ""} ${item.filterTags?.length ? `data-field-filter-tags="${escapeHtml(item.filterTags.join(" "))}"` : ""}>${escapeHtml(item.text)}</li>`).join("")}
            </ul>
          </details>
        `).join("")}
      </div>
    </div>
  `;
}

function renderEvidenceGapTargets(entries = []) {
  if (!entries.length) {
    return "";
  }
  return `
    <div class="runner-stage-gap-targets" aria-label="缺口导航">
      ${entries.slice(0, 10).map((entry) => `
        <button
          type="button"
          class="runner-stage-gap-target"
          data-runner-gap-target
          data-stage-key="${escapeHtml(entry.stageKey)}"
          data-evidence-title="${escapeHtml(entry.evidenceTitle)}"
          data-item-key="${escapeHtml(entry.itemKey)}"
        >
          <span>
            <strong>${escapeHtml(entry.title)}</strong>
            ${entry.detail ? `<small>${escapeHtml(entry.detail)}</small>` : ""}
          </span>
          <span class="runner-stage-gap-target-meta">
            ${entry.status ? `<em>${escapeHtml(entry.status)}</em>` : ""}
            ${entry.profileLabel ? `<em>${escapeHtml(entry.profileLabel)}</em>` : ""}
            <em>${escapeHtml(entry.stageKey)}</em>
          </span>
        </button>
      `).join("")}
    </div>
  `;
}

function installStageFilters(container) {
  const buttons = [...container.querySelectorAll("[data-runner-stage-filter]")];
  for (const button of buttons) {
    button.addEventListener("click", () => {
      applyStageFilter(container, button.dataset.runnerStageFilter || "all");
    });
  }
}

function applyStageFilter(container, filter) {
  container.dataset.runnerStageFilter = filter;
  applyStageVisibility(container);
}

function applyStageScope(container, scope) {
  container.dataset.runnerStageScope = scope;
  applyStageVisibility(container);
}

function applyStageVisibility(container) {
  const filter = container.dataset.runnerStageFilter || "all";
  const scope = container.dataset.runnerStageScope || "all";
  const query = (container.querySelector("[data-runner-stage-search]")?.value || "").trim().toLowerCase();
  const buttons = [...container.querySelectorAll("[data-runner-stage-filter]")];
  const cards = [...container.querySelectorAll("[data-runner-stage-card]")];
  for (const item of buttons) {
    item.classList.toggle("active", (item.dataset.runnerStageFilter || "all") === filter);
  }
  for (const item of container.querySelectorAll("[data-runner-stage-scope]")) {
    item.classList.toggle("active", (item.dataset.runnerStageScope || "all") === scope);
  }
  for (const card of cards) {
    const visibleByFilter = filter === "all"
      || card.dataset.stageKind === filter
      || card.dataset.stageGroup === filter;
    const visibleByScope = scope === "all"
      || card.dataset.stageCritical === "true"
      || card.classList.contains("selected");
    const visibleBySearch = !query || (card.dataset.stageSearch || "").includes(query);
    card.hidden = !(visibleByFilter && visibleByScope && visibleBySearch);
  }
  updateStageVisibleCount(container);
}

function installStageViewControls(container) {
  if (container.__runnerStageViewControlsInstalled) {
    return;
  }
  container.__runnerStageViewControlsInstalled = true;
  container.addEventListener("click", (event) => {
    const densityButton = event.target.closest("[data-runner-stage-density]");
    if (densityButton && container.contains(densityButton)) {
      const density = densityButton.dataset.runnerStageDensity || "standard";
      container.classList.toggle("stage-dense", density === "dense");
      for (const button of container.querySelectorAll("[data-runner-stage-density]")) {
        button.classList.toggle("active", button === densityButton);
      }
      return;
    }
    const scopeButton = event.target.closest("[data-runner-stage-scope]");
    if (scopeButton && container.contains(scopeButton)) {
      applyStageScope(container, scopeButton.dataset.runnerStageScope || "all");
    }
    const clearButton = event.target.closest("[data-runner-stage-search-clear]");
    if (clearButton && container.contains(clearButton)) {
      const search = container.querySelector("[data-runner-stage-search]");
      if (search) {
        search.value = "";
        applyStageVisibility(container);
        search.focus();
      }
    }
  });
  container.addEventListener("input", (event) => {
    if (event.target.matches("[data-runner-stage-search]")) {
      applyStageVisibility(container);
    }
  });
}

function updateStageVisibleCount(container) {
  const count = [...container.querySelectorAll("[data-runner-stage-card]")].filter((card) => !card.hidden).length;
  const total = container.querySelectorAll("[data-runner-stage-card]").length;
  const target = container.querySelector("[data-runner-stage-visible-count]");
  if (target) {
    target.textContent = `${count}/${total} 项`;
  }
  const clearButton = container.querySelector("[data-runner-stage-search-clear]");
  const query = (container.querySelector("[data-runner-stage-search]")?.value || "").trim();
  if (clearButton) {
    clearButton.disabled = !query;
  }
  const empty = container.querySelector("[data-runner-stage-empty]");
  if (empty) {
    empty.hidden = count !== 0;
  }
}

function stageSearchText(stage) {
  return [
    stage.key,
    stage.title,
    stage.status,
    stage.summary,
    stage.group,
    stage.kind,
  ].join(" ").toLowerCase();
}

function installStageSelection(container, stageItems) {
  const detail = container.querySelector("[data-runner-stage-detail]");
  if (!detail) {
    return;
  }
  const byKey = new Map(stageItems.map((stage) => [stage.key, stage]));
  for (const card of container.querySelectorAll("[data-runner-stage-card]")) {
    const select = () => {
      const stage = byKey.get(card.dataset.stageKey || "");
      if (!stage) {
        return;
      }
      selectStage(container, detail, stage, { scroll: false });
    };
    card.addEventListener("click", select);
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
  }
}

function installCriticalPathNavigation(container, stageItems) {
  const detail = container.querySelector("[data-runner-stage-detail]");
  if (!detail) {
    return;
  }
  const byKey = new Map(stageItems.map((stage) => [stage.key, stage]));
  for (const step of container.querySelectorAll("[data-runner-path-step]")) {
    const select = () => {
      const stage = byKey.get(step.dataset.stageKey || "");
      if (!stage) {
        return;
      }
      applyStageFilter(container, "all");
      applyStageScope(container, "all");
      selectStage(container, detail, stage, { scroll: true });
    };
    step.addEventListener("click", select);
    step.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
  }
}

function installBlockerNavigation(container, stageItems) {
  const detail = container.querySelector("[data-runner-stage-detail]");
  if (!detail) {
    return;
  }
  const byKey = new Map(stageItems.map((stage) => [stage.key, stage]));
  for (const blocker of container.querySelectorAll("[data-runner-blocker]")) {
    const select = () => {
      const stage = byKey.get(blocker.dataset.stageKey || "");
      if (!stage) {
        return;
      }
      applyStageFilter(container, "all");
      applyStageScope(container, "all");
      selectStage(container, detail, stage, {
        scroll: true,
        evidenceTitle: blocker.dataset.evidenceTitle || "",
      });
    };
    blocker.addEventListener("click", select);
    blocker.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
  }
}

function installEvidenceGapNavigation(container, stageItems) {
  container.__runnerGapStageByKey = new Map(stageItems.map((stage) => [stage.key, stage]));
  container.__runnerOpenStageTarget = (target) => openRunnerStageTarget(container, target);
  window.flowtraceOpenRunnerStageTarget = container.__runnerOpenStageTarget;
  if (container.__runnerGapNavigationInstalled) {
    return;
  }
  container.__runnerGapNavigationInstalled = true;
  container.addEventListener("click", (event) => {
    const target = event.target.closest("[data-runner-gap-target]");
    if (!target || !container.contains(target)) {
      return;
    }
    openEvidenceGapTarget(container, target);
  });
  container.addEventListener("click", (event) => {
    const target = event.target.closest("[data-field-coverage-filter]");
    if (!target || !container.contains(target)) {
      return;
    }
    applyFieldCoverageFilter(container, target);
  });
}

function openEvidenceGapTarget(container, target) {
  openRunnerStageTarget(container, {
    stageKey: target.dataset.stageKey || "",
    evidenceTitle: target.dataset.evidenceTitle || "",
    itemKey: target.dataset.itemKey || "",
  });
}

function applyFieldCoverageFilter(container, target) {
  const key = target.dataset.fieldCoverageFilter || "all";
  const detail = container.querySelector("[data-runner-stage-detail]");
  if (!detail) {
    return;
  }
  for (const button of detail.querySelectorAll("[data-field-coverage-filter]")) {
    button.classList.toggle("active", button === target);
  }
  for (const item of detail.querySelectorAll("[data-field-filter-tags]")) {
    const tags = (item.dataset.fieldFilterTags || "").split(/\s+/);
    item.hidden = key !== "all" && !tags.includes(key);
  }
}

function openRunnerStageTarget(container, target) {
  const detail = container.querySelector("[data-runner-stage-detail]");
  const stageKey = target.stageKey || target.stage_key || "";
  const stage = container.__runnerGapStageByKey?.get(stageKey);
  if (!detail || !stage) {
    return;
  }
  applyStageFilter(container, "all");
  applyStageScope(container, "all");
  selectStage(container, detail, stage, {
    scroll: true,
    evidenceTitle: target.evidenceTitle || target.evidence_group || "",
    itemKey: target.itemKey || target.item_key || "",
  });
}

function installAuditSummaryCopy(container, stageItems) {
  container.__runnerStageByKey = new Map(stageItems.map((stage) => [stage.key, stage]));
  if (container.__runnerCopyInstalled) {
    return;
  }
  container.__runnerCopyInstalled = true;
  container.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-runner-copy-summary]");
    if (!button || !container.contains(button)) {
      return;
    }
    const stage = container.__runnerStageByKey?.get(button.dataset.stageKey || "");
    if (!stage) {
      return;
    }
    const status = button.parentElement?.querySelector("[data-runner-copy-status]");
    const copied = await copyText(buildAuditSummary(stage));
    if (status) {
      status.textContent = copied ? "已复制" : "复制失败";
    }
  });
}

function installDetailModeToggle(container) {
  if (container.__runnerDetailModeInstalled) {
    return;
  }
  container.__runnerDetailModeInstalled = true;
  container.addEventListener("click", (event) => {
    const button = event.target.closest("[data-runner-detail-mode]");
    if (!button || !container.contains(button)) {
      return;
    }
    const detail = container.querySelector("[data-runner-stage-detail]");
    if (!detail) {
      return;
    }
    detail.classList.toggle("compact");
    updateDetailModeButton(detail);
  });
}

function updateDetailModeButton(detail) {
  const button = detail.querySelector("[data-runner-detail-mode]");
  if (!button) {
    return;
  }
  const compact = detail.classList.contains("compact");
  button.textContent = compact ? "展开视图" : "压缩视图";
  button.setAttribute("aria-pressed", compact ? "true" : "false");
}

async function copyText(text) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // Fall through to the textarea fallback.
  }
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  let copied = false;
  try {
    copied = document.execCommand("copy");
  } catch {
    copied = false;
  }
  textarea.remove();
  return copied;
}

function buildAuditSummary(stage) {
  const lines = [
    "FlowTrace Runner 只读审计摘要",
    `阶段：${stage.title}`,
    `状态：${stage.status}`,
    `结构版本：${stage.detail.schema}`,
    `下一步：${stage.detail.nextTitle}`,
    `动作：${stage.detail.nextAction}`,
    `摘要：${stage.summary}`,
    "",
    "安全边界：",
  ];
  for (const group of stage.detail.safety || []) {
    lines.push(`- ${group.title}：${group.blockedCount} 已阻断${group.attentionCount ? ` / ${group.attentionCount} 待审查` : ""}`);
    for (const item of group.items.slice(0, 6)) {
      lines.push(`  - ${item.label}：${item.text}`);
    }
  }
  if (stage.detail.evidence?.groups?.length) {
    lines.push("", "只读证据：");
    for (const group of stage.detail.evidence.groups.slice(0, 4)) {
      lines.push(`- ${group.title}：${group.items.length}/${group.total}`);
      for (const item of group.items.slice(0, 4)) {
        lines.push(`  - ${item}`);
      }
    }
  }
  lines.push("", "边界：未开放真实启动、未创建进程、未调用执行适配器、未写用户项目。");
  return lines.join("\n");
}

function selectStage(container, detail, stage, options = {}) {
  for (const item of container.querySelectorAll("[data-runner-stage-card]")) {
    item.classList.toggle("selected", item.dataset.stageKey === stage.key);
  }
  for (const item of container.querySelectorAll("[data-runner-path-step]")) {
    item.classList.toggle("selected", item.dataset.stageKey === stage.key);
  }
  applyStageVisibility(container);
  detail.innerHTML = renderStageDetail(stage);
  updateDetailModeButton(detail);
  if (options.evidenceTitle) {
    openEvidenceGroup(detail, options.evidenceTitle, options.itemKey || "");
  }
  if (options.scroll) {
    detail.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
}

function openEvidenceGroup(detail, title, itemKey = "") {
  const groups = [...detail.querySelectorAll(".runner-stage-evidence-groups details")];
  const target = groups.find((group) => group.querySelector("summary")?.textContent.includes(title));
  if (!target) {
    return;
  }
  for (const group of groups) {
    group.open = group === target;
  }
  if (itemKey) {
    for (const item of target.querySelectorAll("[data-evidence-item-key]")) {
      const selected = item.dataset.evidenceItemKey === itemKey;
      item.classList.toggle("selected", selected);
      if (selected) {
        item.scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    }
  }
}

function stageSummary(summary) {
  const parts = [];
  addPart(parts, "报告", summary.report_count);
  addPart(parts, "保存", summary.saved_profile_count ?? summary.saved_count);
  addPart(parts, "可启动", summary.launchable_count);
  addPart(parts, "端点", summary.registered_endpoint_count);
  addPart(parts, "活跃", summary.active_session_count);
  return parts.length ? parts.join(" | ") : "暂无摘要";
}

function addPart(parts, label, value) {
  if (value === undefined || value === null) {
    return;
  }
  parts.push(`${label} ${value}`);
}

function collectSafety(data) {
  const summaries = Object.values(data).map((payload) => payload?.summary || {});
  return {
    launchableCount: maxNumber(summaries, "launchable_count"),
    activeSessionCount: maxNumber(summaries, "active_session_count"),
    registeredEndpointCount: maxNumber(summaries, "registered_endpoint_count"),
    savedProfileCount: maxNumber(summaries, "saved_profile_count", "saved_count"),
  };
}

function collectBlockers(data, latestStage) {
  const blockers = [];
  const safety = collectSafety(data);
  if (!safety.savedProfileCount) {
    blockers.push({
      severity: "warn",
      title: "尚未保存运行配置",
      detail: "需要先保存候选运行配置，后续治理层才会生成针对具体 profile 的报告。",
      stageKey: "run_profiles",
    });
  }
  if (!safety.launchableCount) {
    blockers.push({
      severity: "error",
      title: "尚无可启动 profile",
      detail: "需要保存 command profile，并完成确认、session、snapshot 与 dry-run 后才能真实启动。",
      stageKey: "runner_real_executions",
      evidenceTitle: "报告证据",
    });
  }
  if (safety.registeredEndpointCount && !data.runnerCancelTimeoutRealApis?.summary?.registered_endpoint_count) {
    blockers.push({
      severity: "warn",
      title: "发现注册端点计数",
      detail: "注册端点必须保持在低风险样例和受控 launch_id 范围内。",
      stageKey: "runner_launch_api_contracts",
      evidenceTitle: "阻断动作",
    });
  }
  if (latestStage?.status && latestStage.status !== "no_saved_profiles") {
    blockers.push({
      severity: "info",
      title: latestStage.title,
      detail: latestStage.status,
      stageKey: latestStage.key,
    });
  }
  return blockers;
}

function collectNextAction(data, latestStage) {
  if (latestStage?.nextAction?.title || latestStage?.nextAction?.action) {
    return {
      title: latestStage.nextAction.title || latestStage.title,
      action: latestStage.nextAction.action || latestStage.status,
    };
  }
  const runProfiles = data.runProfiles;
  if (!runProfiles?.summary?.saved_count && !runProfiles?.summary?.saved_profile_count) {
    return {
      title: "先保存运行配置",
      action: "在接入向导保存一个运行配置后，Runner 工作台会显示针对该 profile 的治理报告。",
    };
  }
  return {
    title: "继续只读治理",
    action: "继续补齐只读治理层，或进入工作台交互优化；真实执行需要单独授权实现。",
  };
}

function statusTitle(stage, safety = {}) {
  if (!stage) {
    return "等待项目数据";
  }
  if (!safety.savedProfileCount) {
    return "等待保存运行配置";
  }
  if (stage.status === "no_saved_profiles") {
    return "等待保存运行配置";
  }
  if (stage.kind === "ready") {
    return "存在可启动项";
  }
  return `${stage.title}：${stage.status}`;
}

function metric(label, value, expected = "") {
  return `
    <div class="runner-workbench-metric">
      <strong>${escapeHtml(value ?? 0)}</strong>
      <span>${escapeHtml(label)}${expected ? ` / ${escapeHtml(expected)}` : ""}</span>
    </div>
  `;
}

function stageChip(label, value, kind) {
  return `
    <span class="runner-workbench-stage-chip ${escapeHtml(kind)}">
      <strong>${escapeHtml(value ?? 0)}</strong>
      ${escapeHtml(label)}
    </span>
  `;
}

function kv(label, value) {
  return `
    <div>
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value ?? "暂无")}</strong>
    </div>
  `;
}

function maxNumber(items, ...keys) {
  let max = 0;
  for (const item of items) {
    for (const key of keys) {
      max = Math.max(max, numberValue(item?.[key]));
    }
  }
  return max;
}

function numberValue(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
}








