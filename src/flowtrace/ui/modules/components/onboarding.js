// 模块：接入向导视图。负责展示确定性接入建议，不自动修改用户项目代码。
import { escapeHtml } from "../utils/html.js";

const SECTION_COLLAPSE_STORAGE_KEY = "flowtrace.onboardingSectionCollapse.v1";

const PRIORITY_LABELS = {
  high: "高",
  medium: "中",
  low: "低",
};

const KIND_LABELS = {
  scan_error: "扫描错误",
  entrypoint: "入口候选",
  uncovered_method: "未覆盖方法",
  runtime_only_method: "运行时方法",
  core_candidate: "核心候选",
};

const STATUS_LABELS = {
  pending: "待处理",
  done: "已接入",
  ignored: "忽略",
};

const CHECK_LABELS = {
  pass: "通过",
  warn: "注意",
  error: "阻塞",
};

const AUDIT_LABELS = {
  blocked: "阻塞",
  fail: "失败",
  warn: "有风险",
  pass: "通过",
};

const FINDING_LABELS = {
  critical: "严重",
  error: "错误",
  warning: "警告",
  info: "信息",
};

export function renderOnboarding(
  container,
  onboarding,
  readiness = null,
  audit = null,
  integrationPlan = null,
  runProfiles = null,
  runPreflight = null,
  runExecutionGate = null,
  runnerPlan = null,
  executionRequests = null,
  runnerSessions = null,
  runnerLaunchSnapshots = null,
  runnerDryRuns = null,
  runnerLaunchControls = null,
  runnerRuntimePolicies = null,
  runnerExecutionConfigs = null,
  runnerExecutionConfigChecks = null,
  runnerConfigSchemaStabilizations = null,
  runnerConfigFieldContractViews = null,
  runnerConfigCompatibilityReports = null,
  runnerConfigRemediationSummaries = null,
  runnerConfigFieldCoverageIndexes = null,
  runnerServiceFlagAudits = null,
  runnerLogDirectoryPolicies = null,
  runnerLogRetentionPolicies = null,
  runnerLogCleanupPreviews = null,
  runnerLogCleanupConfirmations = null,
  runnerLogCleanupAuditTrails = null,
  runnerLogCleanupExecutionPlans = null,
  runnerGovernanceReadiness = null,
  runnerExecutionAdapterContracts = null,
  runnerLaunchApiContracts = null,
  runnerExecutionAdapterReviews = null,
  runnerFinalBlockMatrices = null,
  runnerAuthorizationUnlockAudits = null,
  runnerImplementationGapChecklists = null,
  runnerCancelTimeoutContracts = null,
  runnerSessionStateSchemas = null,
  runnerRealTestReadiness = null,
  runnerRealTestAuthorizationChecklists = null,
  runnerRealExecutionImplementationPlans = null,
  runnerExecutionAdapterImplementationAudits = null,
  runnerProcessLifecycleImplementationAudits = null,
  runnerStreamCaptureImplementationAudits = null,
  runnerEventWriterImplementationAudits = null,
  runnerAuditPersistenceImplementationAudits = null,
  runnerAuditIntegrityReplayVerificationAudits = null,
  runnerVerificationDiscrepancyReportAudits = null,
  runnerRealLaunchFinalGateAudits = null,
  runnerEvidenceGapIndexes = null,
  getStatus = () => "pending",
  onSetStatus = () => {},
  onSelectFinding = () => {},
  onSaveRunProfile = async () => {},
  onRemoveRunProfile = async () => {},
  onConfirmRunPreflight = async () => {},
  onRevokeRunPreflight = async () => {},
  onConfirmRunExecutionGate = async () => {},
  onRevokeRunExecutionGate = async () => {},
  onPrepareExecutionRequest = async () => {},
  onConfirmExecutionRequest = async () => {},
  onRevokeExecutionRequest = async () => {},
  onRemoveExecutionRequest = async () => {},
  onPrepareRunnerSession = async () => {},
  onRemoveRunnerSession = async () => {},
  onPrepareRunnerLaunchSnapshot = async () => {},
  onRemoveRunnerLaunchSnapshot = async () => {},
  onPrepareRunnerDryRun = async () => {},
  onRemoveRunnerDryRun = async () => {},
) {
  container.className = "onboarding-view";
  container.innerHTML = "";

  const summary = onboarding.summary || {};
  const suggestions = onboarding.suggestions || [];
  const statusSummary = summarizeStatuses(suggestions, getStatus);
  if (readiness) {
    container.appendChild(section("接入状态", renderReadiness(readiness)));
  }
  if (audit) {
    container.appendChild(section("自动审查", renderAudit(audit)));
  }
  if (integrationPlan) {
    container.appendChild(section("接入计划", renderIntegrationPlan(integrationPlan)));
  }
  if (runProfiles) {
    container.appendChild(section("运行配置草案", renderRunProfiles(runProfiles)));
  }
  if (runPreflight) {
    container.appendChild(section("执行前安全预检", renderRunPreflight(runPreflight)));
  }
  if (runExecutionGate) {
    container.appendChild(section("最终执行确认", renderRunExecutionGate(runExecutionGate)));
  }
  if (runnerPlan) {
    container.appendChild(section("Runner 隔离设计", renderRunnerPlan(runnerPlan)));
  }
  if (executionRequests) {
    container.appendChild(section("执行请求草案", renderExecutionRequests(executionRequests)));
  }
  if (runnerSessions) {
    container.appendChild(section("Runner 会话草案", renderRunnerSessions(runnerSessions)));
  }
  if (runnerLaunchSnapshots) {
    container.appendChild(section("启动前快照", renderRunnerLaunchSnapshots(runnerLaunchSnapshots)));
  }
  if (runnerDryRuns) {
    container.appendChild(section("Dry-run Runner", renderRunnerDryRuns(runnerDryRuns)));
  }
  if (runnerLaunchControls) {
    container.appendChild(section("Runner 启动开关", renderRunnerLaunchControls(runnerLaunchControls)));
  }
  if (runnerRuntimePolicies) {
    container.appendChild(section("Runner 运行时策略", renderRunnerRuntimePolicies(runnerRuntimePolicies)));
  }
  if (runnerExecutionConfigs) {
    container.appendChild(section("Runner 执行配置", renderRunnerExecutionConfigs(runnerExecutionConfigs)));
  }
  if (runnerExecutionConfigChecks) {
    container.appendChild(section("Runner 配置检查", renderRunnerExecutionConfigChecks(runnerExecutionConfigChecks)));
  }
  if (runnerConfigSchemaStabilizations) {
    container.appendChild(section("Runner 配置 Schema 稳定化", renderRunnerConfigSchemaStabilizations(runnerConfigSchemaStabilizations)));
  }
  if (runnerConfigFieldContractViews) {
    container.appendChild(section("Runner 配置字段契约说明", renderRunnerConfigFieldContractViews(runnerConfigFieldContractViews)));
  }
  if (runnerConfigCompatibilityReports) {
    container.appendChild(section("Runner 配置兼容性报告", renderRunnerConfigCompatibilityReports(runnerConfigCompatibilityReports)));
  }
  if (runnerConfigRemediationSummaries) {
    container.appendChild(section("Runner 配置修复建议汇总", renderRunnerConfigRemediationSummaries(runnerConfigRemediationSummaries)));
  }
  if (runnerConfigFieldCoverageIndexes) {
    container.appendChild(section("Runner config field coverage index", renderRunnerConfigFieldCoverageIndexes(runnerConfigFieldCoverageIndexes)));
  }
  if (runnerServiceFlagAudits) {
    container.appendChild(section("Runner 服务开关审计", renderRunnerServiceFlagAudits(runnerServiceFlagAudits)));
  }
  if (runnerLogDirectoryPolicies) {
    container.appendChild(section("Runner 日志目录策略", renderRunnerLogDirectoryPolicies(runnerLogDirectoryPolicies)));
  }
  if (runnerLogRetentionPolicies) {
    container.appendChild(section("Runner 日志保留策略", renderRunnerLogRetentionPolicies(runnerLogRetentionPolicies)));
  }
  if (runnerLogCleanupPreviews) {
    container.appendChild(section("Runner 日志清理预览", renderRunnerLogCleanupPreviews(runnerLogCleanupPreviews)));
  }
  if (runnerLogCleanupConfirmations) {
    container.appendChild(section("Runner 日志清理确认", renderRunnerLogCleanupConfirmations(runnerLogCleanupConfirmations)));
  }
  if (runnerLogCleanupAuditTrails) {
    container.appendChild(section("Runner 日志清理审计追踪", renderRunnerLogCleanupAuditTrails(runnerLogCleanupAuditTrails)));
  }
  if (runnerLogCleanupExecutionPlans) {
    container.appendChild(section("Runner 日志清理执行计划", renderRunnerLogCleanupExecutionPlans(runnerLogCleanupExecutionPlans)));
  }
  if (runnerGovernanceReadiness) {
    container.appendChild(section("Runner 治理就绪度", renderRunnerGovernanceReadiness(runnerGovernanceReadiness)));
  }
  if (runnerExecutionAdapterContracts) {
    container.appendChild(section("Runner 执行适配器合约", renderRunnerExecutionAdapterContracts(runnerExecutionAdapterContracts)));
  }
  if (runnerLaunchApiContracts) {
    container.appendChild(section("Runner 启动 API 合约", renderRunnerLaunchApiContracts(runnerLaunchApiContracts)));
  }
  if (runnerExecutionAdapterReviews) {
    container.appendChild(section("Runner 执行适配器审查", renderRunnerExecutionAdapterReviews(runnerExecutionAdapterReviews)));
  }
  if (runnerFinalBlockMatrices) {
    container.appendChild(section("Runner 最终阻断矩阵", renderRunnerFinalBlockMatrices(runnerFinalBlockMatrices)));
  }
  if (runnerAuthorizationUnlockAudits) {
    container.appendChild(section("Runner 授权解锁审计", renderRunnerAuthorizationUnlockAudits(runnerAuthorizationUnlockAudits)));
  }
  if (runnerImplementationGapChecklists) {
    container.appendChild(section("Runner 实现差距清单", renderRunnerImplementationGapChecklists(runnerImplementationGapChecklists)));
  }
  if (runnerCancelTimeoutContracts) {
    container.appendChild(section("Runner 取消超时合约", renderRunnerCancelTimeoutContracts(runnerCancelTimeoutContracts)));
  }
  if (runnerSessionStateSchemas) {
    container.appendChild(section("Runner 会话状态 Schema", renderRunnerSessionStateSchemas(runnerSessionStateSchemas)));
  }
  if (runnerRealTestReadiness) {
    container.appendChild(section("Runner 真实测试准入", renderRunnerRealTestReadiness(runnerRealTestReadiness)));
  }
  if (runnerRealTestAuthorizationChecklists) {
    container.appendChild(section("Runner 真实测试授权检查清单", renderRunnerRealTestAuthorizationChecklists(runnerRealTestAuthorizationChecklists)));
  }
  if (runnerRealExecutionImplementationPlans) {
    container.appendChild(section("Runner 真实执行实现计划", renderRunnerRealExecutionImplementationPlans(runnerRealExecutionImplementationPlans)));
  }
  if (runnerExecutionAdapterImplementationAudits) {
    container.appendChild(section("Runner 执行适配器实现准备审计", renderRunnerExecutionAdapterImplementationAudits(runnerExecutionAdapterImplementationAudits)));
  }
  if (runnerProcessLifecycleImplementationAudits) {
    container.appendChild(section("Runner 进程生命周期实现准备审计", renderRunnerProcessLifecycleImplementationAudits(runnerProcessLifecycleImplementationAudits)));
  }
  if (runnerStreamCaptureImplementationAudits) {
    container.appendChild(section("Runner stdout/stderr 捕获实现准备审计", renderRunnerStreamCaptureImplementationAudits(runnerStreamCaptureImplementationAudits)));
  }
  if (runnerEventWriterImplementationAudits) {
    container.appendChild(section("Runner 事件写入实现准备审计", renderRunnerEventWriterImplementationAudits(runnerEventWriterImplementationAudits)));
  }
  if (runnerAuditPersistenceImplementationAudits) {
    container.appendChild(section("Runner 审计持久化实现准备审计", renderRunnerAuditPersistenceImplementationAudits(runnerAuditPersistenceImplementationAudits)));
  }
  if (runnerAuditIntegrityReplayVerificationAudits) {
    container.appendChild(section("Runner 审计完整性与回放校验准备审计", renderRunnerAuditIntegrityReplayVerificationAudits(runnerAuditIntegrityReplayVerificationAudits)));
  }
  if (runnerVerificationDiscrepancyReportAudits) {
    container.appendChild(section("Runner 校验差异报告实现准备审计", renderRunnerVerificationDiscrepancyReportAudits(runnerVerificationDiscrepancyReportAudits)));
  }
  if (runnerRealLaunchFinalGateAudits) {
    container.appendChild(section("Runner 真实启动最终闸门准备审计", renderRunnerRealLaunchFinalGateAudits(runnerRealLaunchFinalGateAudits)));
  }
  if (runnerEvidenceGapIndexes) {
    container.appendChild(section("Runner 证据索引与缺口导航", renderRunnerEvidenceGapIndexes(runnerEvidenceGapIndexes)));
  }
  container.appendChild(section("接入概览", `
    <div class="onboarding-metrics">
      ${metric("建议", summary.suggestion_count)}
      ${metric("高优先级", summary.high_priority_count)}
      ${metric("已接入", statusSummary.done)}
      ${metric("忽略", statusSummary.ignored)}
      ${metric("入口候选", summary.entrypoint_count)}
      ${metric("未覆盖", summary.uncovered_method_count)}
      ${metric("运行时发现", summary.runtime_only_method_count)}
      ${metric("扫描错误", summary.scan_error_count)}
    </div>
  `));

  container.appendChild(section("推荐步骤", renderSteps(onboarding.steps || [])));
  container.appendChild(section("接入建议", renderSuggestions(suggestions, getStatus)));
  installSuggestionActions(container, suggestions, onSetStatus);
  installAuditActions(container, audit, onSelectFinding);
  installRunProfileActions(container, runProfiles, onSaveRunProfile, onRemoveRunProfile);
  installRunPreflightActions(container, runPreflight, onConfirmRunPreflight, onRevokeRunPreflight);
  installRunExecutionGateActions(container, runExecutionGate, onConfirmRunExecutionGate, onRevokeRunExecutionGate);
  installExecutionRequestActions(
    container,
    executionRequests,
    onPrepareExecutionRequest,
    onConfirmExecutionRequest,
    onRevokeExecutionRequest,
    onRemoveExecutionRequest,
  );
  installRunnerSessionActions(container, runnerSessions, onPrepareRunnerSession, onRemoveRunnerSession);
  installRunnerLaunchSnapshotActions(
    container,
    runnerLaunchSnapshots,
    onPrepareRunnerLaunchSnapshot,
    onRemoveRunnerLaunchSnapshot,
  );
  installRunnerDryRunActions(container, runnerDryRuns, onPrepareRunnerDryRun, onRemoveRunnerDryRun);
  installRunnerConfigCompatibilityNavigation(container);
}

function renderRunnerExecutionAdapterReviews(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const reviewSchema = payload.review_schema || {};
  const implementationState = reviewSchema.implementation_state || {};
  return `
    <div class="runner-execution-adapter-reviews">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("需审查", summary.adapter_review_required_count)}
        ${metric("已实现适配器", summary.implemented_adapter_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 执行适配器审查状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>审查 schema：${escapeHtml(reviewSchema.schema_version || "")}</strong>
        <span>当前为预实现审查：适配器未加载、未调用，真实启动仍禁用。</span>
        <div class="runner-snapshot-evidence">
          <span>预实现：${implementationState.review_is_preimplementation ? "是" : "否"}</span>
          <span>当前加载适配器：${implementationState.adapter_loaded_now ? "是" : "否"}</span>
          <span>当前调用适配器：${implementationState.adapter_invoked_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(reviewSchema.required_review_gates || []).map((item) => `
            <span>门槛<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(reviewSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const review = report.adapter_review || {};
          const state = review.implementation_state || {};
          return `
            <article class="runner-execution-adapter-review-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>启动 API 合约：${escapeHtml(report.launch_api_contract_status || "missing")}</span>
                <span>适配器加载：${state.adapter_loaded_now ? "是" : "否"}</span>
                <span>适配器调用：${state.adapter_invoked_now ? "是" : "否"}</span>
                <span>预实现审查：${state.review_is_preimplementation ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(review.required_evidence || []).map((item) => `
                  <span>证据<small>${escapeHtml(item)}</small></span>
                `).join("")}
                ${(review.required_review_gates || []).map((item) => `
                  <span>审查<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 执行适配器审查报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerFinalBlockMatrices(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const blockSchema = payload.block_matrix_schema || {};
  const matrixState = blockSchema.matrix_state || {};
  return `
    <div class="runner-final-block-matrices">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("阻断矩阵", summary.final_block_required_count)}
        ${metric("阻断原因", summary.blocking_reason_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 最终阻断矩阵状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>阻断矩阵 schema：${escapeHtml(blockSchema.schema_version || "")}</strong>
        <span>当前只聚合真实启动前阻断原因；不注册启动 API、不加载或调用执行适配器、不创建进程、不执行命令、不读写日志、不写审计日志、不修改用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${matrixState.read_only ? "是" : "否"}</span>
          <span>当前可启动：${matrixState.can_launch_now ? "是" : "否"}</span>
          <span>需要新实现轮次：${matrixState.requires_new_implementation_round ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(blockSchema.blocking_dimensions || []).map((item) => `
            <span>阻断维度<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(blockSchema.required_future_unlocks || []).map((item) => `
            <span>未来解锁<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const launchState = report.launch_state || {};
          return `
            <article class="runner-final-block-matrix-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>适配器审查：${escapeHtml(report.execution_adapter_review_status || "missing")}</span>
                <span>可启动：${launchState.launchable ? "是" : "否"}</span>
                <span>启动开关：${launchState.launch_enabled ? "开启" : "关闭"}</span>
                <span>启动 API：${launchState.launch_api_available ? "可用" : "不可用"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.blocking_reasons || []).map((reason) => `
                  <span>${escapeHtml(reason.severity || "blocker")}<small>${escapeHtml(reason.title || reason.key || "")}</small></span>
                `).join("")}
                ${(report.required_future_unlocks || []).map((item) => `
                  <span>解锁<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 最终阻断矩阵报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerAuthorizationUnlockAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.authorization_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-authorization-unlock-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("需授权", summary.authorization_required_count)}
        ${metric("未来解锁", summary.future_unlock_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 授权解锁审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>授权审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来授权与解锁证据；不收集授权、不授予启动权限、不注册启动 API、不调用执行适配器、不创建进程、不执行命令、不读写日志、不写审计日志、不修改用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>已收集授权：${auditState.authorization_collected_now ? "是" : "否"}</span>
          <span>已授予权限：${auditState.permission_granted_now ? "是" : "否"}</span>
          <span>当前可解锁：${auditState.can_unlock_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_authorization_records || []).map((item) => `
            <span>授权记录<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(auditSchema.required_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const authorizationState = report.authorization_state || {};
          return `
            <article class="runner-authorization-unlock-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>最终阻断矩阵：${escapeHtml(report.final_block_matrix_status || "missing")}</span>
                <span>已收集授权：${authorizationState.authorization_collected_now ? "是" : "否"}</span>
                <span>已授予权限：${authorizationState.permission_granted_now ? "是" : "否"}</span>
                <span>当前可解锁：${authorizationState.can_unlock_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.unlock_items || []).map((item) => `
                  <span>${escapeHtml(item.state || "future_review_required")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.required_authorization_records || []).map((item) => `
                  <span>授权<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 授权解锁审计报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerImplementationGapChecklists(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const gapSchema = payload.implementation_gap_schema || {};
  const checklistState = gapSchema.checklist_state || {};
  return `
    <div class="runner-implementation-gap-checklists">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("需实现", summary.implementation_required_count)}
        ${metric("组件", summary.component_count)}
        ${metric("缺口", summary.gap_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 实现差距清单状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>差距清单 schema：${escapeHtml(gapSchema.schema_version || "")}</strong>
        <span>当前只列出真实 Runner 前的实现缺口；不实现 runner、不注册启动 API、不调用执行适配器、不创建进程、不执行命令、不打开 stdout/stderr、不写 runner 事件、不读写日志、不写审计日志、不修改用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${checklistState.read_only ? "是" : "否"}</span>
          <span>当前实现：${checklistState.implements_now ? "是" : "否"}</span>
          <span>当前可启动：${checklistState.can_launch_now ? "是" : "否"}</span>
          <span>需新授权实现轮次：${checklistState.requires_new_authorized_implementation_round ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(gapSchema.required_components || []).map((item) => `
            <span>组件<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(gapSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const implementationState = report.implementation_state || {};
          return `
            <article class="runner-implementation-gap-checklist-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>授权解锁审计：${escapeHtml(report.authorization_unlock_audit_status || "missing")}</span>
                <span>Runner 已实现：${implementationState.runner_implemented_now ? "是" : "否"}</span>
                <span>启动 API 已注册：${implementationState.launch_api_registered_now ? "是" : "否"}</span>
                <span>当前可真实测试：${implementationState.can_start_real_test_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.implementation_components || []).map((item) => `
                  <span>${escapeHtml(item.implementation_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 实现差距清单报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerCancelTimeoutContracts(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const contractSchema = payload.cancel_timeout_contract_schema || {};
  const contractState = contractSchema.contract_state || {};
  return `
    <div class="runner-cancel-timeout-contracts">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("需合约", summary.contract_required_count)}
        ${metric("未来端点", summary.future_endpoint_count)}
        ${metric("已注册", summary.registered_endpoint_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 取消超时合约状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>取消超时合约 schema：${escapeHtml(contractSchema.schema_version || "")}</strong>
        <span>当前只声明未来取消和超时端点合约；不注册端点、不发送进程信号、不 kill 进程、不调用 adapter hook、不调度 timeout worker、不写 runner event、不读写日志、不写审计日志、不修改用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${contractState.read_only ? "是" : "否"}</span>
          <span>端点已注册：${contractState.endpoints_registered_now ? "是" : "否"}</span>
          <span>当前可取消：${contractState.can_cancel_now ? "是" : "否"}</span>
          <span>当前可超时：${contractState.can_timeout_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(contractSchema.future_endpoints || []).map((endpoint) => `
            <span>未来端点<small>${escapeHtml(endpoint.method || "POST")} ${escapeHtml(endpoint.path || "")}</small></span>
          `).join("")}
          ${(contractSchema.allowed_future_state_transitions || []).map((item) => `
            <span>状态流转<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(contractSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const contractState = report.contract_state || {};
          return `
            <article class="runner-cancel-timeout-contract-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>实现差距清单：${escapeHtml(report.implementation_gap_checklist_status || "missing")}</span>
                <span>端点已注册：${contractState.endpoints_registered_now ? "是" : "否"}</span>
                <span>当前可取消：${contractState.can_cancel_now ? "是" : "否"}</span>
                <span>当前可超时：${contractState.can_timeout_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.future_endpoints || []).map((endpoint) => `
                  <span>${escapeHtml(endpoint.id || "endpoint")}<small>${escapeHtml(endpoint.method || "POST")} ${escapeHtml(endpoint.path || "")}</small></span>
                `).join("")}
                ${(report.required_future_guards || []).map((item) => `
                  <span>门槛<small>${escapeHtml(item)}</small></span>
                `).join("")}
                ${(report.required_future_events || []).map((item) => `
                  <span>事件<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 取消超时合约报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerSessionStateSchemas(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const stateSchema = payload.session_state_schema || {};
  const schemaState = stateSchema.schema_state || {};
  return `
    <div class="runner-session-state-schemas">
      <div class="integration-summary">
        ${metric("Saved profiles", summary.saved_profile_count)}
        ${metric("Reports", summary.report_count)}
        ${metric("Need schema", summary.state_schema_required_count)}
        ${metric("States", summary.state_count)}
        ${metric("Persisted", summary.persisted_session_count)}
        ${metric("Active", summary.active_session_count)}
        ${metric("Launchable", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner session state schema status")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>Session state schema: ${escapeHtml(stateSchema.schema_version || "")}</strong>
        <span>Contract-only read layer. It declares future session identity fields, state fields, transitions, guards, and events. It does not create sessions, persist state, mutate state, register launch/cancel/timeout APIs, create processes, call adapters, open streams, write runner events, read/write logs, write audit logs, or modify the user project.</span>
        <div class="runner-snapshot-evidence">
          <span>Read only: ${schemaState.read_only ? "yes" : "no"}</span>
          <span>Store now: ${schemaState.session_store_available_now ? "yes" : "no"}</span>
          <span>Created now: ${schemaState.session_created_now ? "yes" : "no"}</span>
          <span>Mutated now: ${schemaState.session_mutated_now ? "yes" : "no"}</span>
          <span>Active now: ${schemaState.active_session_now ? "yes" : "no"}</span>
        </div>
        <div class="runner-session-events">
          ${(stateSchema.identity_fields || []).map((item) => `
            <span>identity<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(stateSchema.allowed_states || []).map((item) => `
            <span>state<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(stateSchema.allowed_future_transitions || []).map((item) => `
            <span>transition<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(stateSchema.blocked_actions || []).map((item) => `
            <span>blocked<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const schemaState = report.schema_state || {};
          return `
            <article class="runner-session-state-schema-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "Run profile")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>Cancel/timeout: ${escapeHtml(report.cancel_timeout_contract_status || "missing")}</span>
                <span>Store now: ${schemaState.session_store_available_now ? "yes" : "no"}</span>
                <span>Created now: ${schemaState.session_created_now ? "yes" : "no"}</span>
                <span>Mutated now: ${schemaState.session_mutated_now ? "yes" : "no"}</span>
                <span>Active now: ${schemaState.active_session_now ? "yes" : "no"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.required_future_fields || []).map((item) => `
                  <span>field<small>${escapeHtml(item)}</small></span>
                `).join("")}
                ${(report.required_future_guards || []).map((item) => `
                  <span>guard<small>${escapeHtml(item)}</small></span>
                `).join("")}
                ${(report.required_future_events || []).map((item) => `
                  <span>event<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">No Runner session state schema reports.</div>`}
      </div>
    </div>
  `;
}

function renderRunnerRealTestReadiness(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const gateSchema = payload.real_test_gate_schema || {};
  const readinessState = gateSchema.readiness_state || {};
  return `
    <div class="runner-real-test-readiness">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("准入门槛", summary.gate_count)}
        ${metric("缺失门槛", summary.missing_gate_count)}
        ${metric("可真实测试", summary.can_start_real_test_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 真实测试准入状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>真实测试准入 schema：${escapeHtml(gateSchema.schema_version || "")}</strong>
        <span>当前只聚合真实测试前的准入门槛；不注册 launch/cancel/timeout API、不实现或导入执行适配器、不创建进程、不打开 stdout/stderr、不写 Runner 事件、不读写日志、不写审计日志、不收集授权、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${readinessState.read_only ? "是" : "否"}</span>
          <span>当前可真实测试：${readinessState.can_start_real_test_now ? "是" : "否"}</span>
          <span>已收集授权：${readinessState.approval_collected_now ? "是" : "否"}</span>
          <span>需要新授权实现轮次：${readinessState.requires_new_authorized_implementation_round ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(gateSchema.required_gates || []).map((item) => `
            <span>门槛<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(gateSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const launchState = report.launch_state || {};
          return `
            <article class="runner-real-test-readiness-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>会话状态 Schema：${escapeHtml(report.session_state_schema_status || "missing")}</span>
                <span>当前可真实测试：${launchState.can_start_real_test_now ? "是" : "否"}</span>
                <span>启动开关：${launchState.launch_enabled ? "开启" : "关闭"}</span>
                <span>启动 API：${launchState.launch_api_available ? "可用" : "不可用"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.readiness_gates || []).map((item) => `
                  <span>${escapeHtml(item.status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 真实测试准入报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerRealTestAuthorizationChecklists(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const checklistSchema = payload.authorization_checklist_schema || {};
  const authorizationState = checklistSchema.authorization_state || {};
  return `
    <div class="runner-real-test-authorization-checklists">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("授权项", summary.check_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已授权", summary.collected_authorization_count)}
        ${metric("已授予", summary.permission_granted_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 真实测试授权检查状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>授权检查 schema：${escapeHtml(checklistSchema.schema_version || "")}</strong>
        <span>当前只列出未来真实测试授权前需要核对的证据；不收集授权、不保存授权、不授予权限、不注册 launch/cancel/timeout API、不创建进程、不调用适配器、不打开 stdout/stderr、不写 Runner 事件、不读写日志、不写审计日志、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${authorizationState.read_only ? "是" : "否"}</span>
          <span>已收集授权：${authorizationState.authorization_collected_now ? "是" : "否"}</span>
          <span>已保存授权：${authorizationState.authorization_stored_now ? "是" : "否"}</span>
          <span>已授予权限：${authorizationState.permission_granted_now ? "是" : "否"}</span>
          <span>当前可启动：${authorizationState.can_launch_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(checklistSchema.required_authorization_records || []).map((item) => `
            <span>授权记录<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(checklistSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.authorization_state || {};
          return `
            <article class="runner-real-test-authorization-checklist-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>真实测试准入：${escapeHtml(report.real_test_readiness_status || "missing")}</span>
                <span>已收集授权：${state.authorization_collected_now ? "是" : "否"}</span>
                <span>已保存授权：${state.authorization_stored_now ? "是" : "否"}</span>
                <span>已授予权限：${state.permission_granted_now ? "是" : "否"}</span>
                <span>当前可启动：${state.can_launch_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.authorization_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.required_authorization_records || []).map((item) => `
                  <span>记录<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 真实测试授权检查清单。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerRealExecutionImplementationPlans(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const planSchema = payload.implementation_plan_schema || {};
  const planState = planSchema.plan_state || {};
  return `
    <div class="runner-real-execution-implementation-plans">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("实现模块", summary.planned_module_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪模块", summary.ready_module_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 真实执行实现计划状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>实现计划 schema：${escapeHtml(planSchema.schema_version || "")}</strong>
        <span>当前只拆解未来真实执行实现范围；不写 Runner 实现、不注册 launch/cancel/timeout API、不导入或调用适配器、不创建进程、不打开 stdout/stderr、不写 Runner 事件、不读写日志、不写审计日志、不收集授权、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${planState.read_only ? "是" : "否"}</span>
          <span>当前实现：${planState.implements_now ? "是" : "否"}</span>
          <span>当前可启动：${planState.can_launch_now ? "是" : "否"}</span>
          <span>需要新授权实现轮次：${planState.requires_new_authorized_implementation_round ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(planSchema.implementation_modules || []).map((item) => `
            <span>模块<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(planSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.plan_state || {};
          return `
            <article class="runner-real-execution-implementation-plan-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>授权检查：${escapeHtml(report.authorization_checklist_status || "missing")}</span>
                <span>当前实现：${state.implements_now ? "是" : "否"}</span>
                <span>当前可启动：${state.can_launch_now ? "是" : "否"}</span>
                <span>只读：${state.read_only ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.implementation_modules || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 真实执行实现计划。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerExecutionAdapterImplementationAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.adapter_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-execution-adapter-implementation-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪", summary.ready_item_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 执行适配器实现准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>适配器审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来执行适配器实现前必须锁定的输入、输出、错误、事件和审计证据；不写适配器、不导入或调用适配器、不注册 launch/cancel/timeout API、不创建进程、不打开 stdout/stderr、不写 Runner 事件、不读写日志、不写审计日志、不收集授权、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>已实现适配器：${auditState.adapter_implemented_now ? "是" : "否"}</span>
          <span>已导入适配器：${auditState.adapter_imported_now ? "是" : "否"}</span>
          <span>已调用适配器：${auditState.adapter_called_now ? "是" : "否"}</span>
          <span>当前可启动：${auditState.can_launch_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_adapter_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-execution-adapter-implementation-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>实现计划：${escapeHtml(report.implementation_plan_status || "missing")}</span>
                <span>已实现适配器：${state.adapter_implemented_now ? "是" : "否"}</span>
                <span>已导入适配器：${state.adapter_imported_now ? "是" : "否"}</span>
                <span>已调用适配器：${state.adapter_called_now ? "是" : "否"}</span>
                <span>当前可启动：${state.can_launch_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 执行适配器实现准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerProcessLifecycleImplementationAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.process_lifecycle_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-process-lifecycle-implementation-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪", summary.ready_item_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 进程生命周期实现准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>进程生命周期审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来进程生命周期实现前必须锁定的进程创建、PID 归属、终止态、取消、超时和清理边界；不创建进程、不控制进程、不发送信号、不注册 launch/cancel/timeout API、不导入或调用适配器、不打开 stdout/stderr、不写 Runner 事件、不读写日志、不写审计日志、不收集授权、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>已创建进程：${auditState.process_created_now ? "是" : "否"}</span>
          <span>已记录 PID：${auditState.pid_recorded_now ? "是" : "否"}</span>
          <span>进程控制开启：${auditState.process_control_enabled_now ? "是" : "否"}</span>
          <span>取消开启：${auditState.cancellation_enabled_now ? "是" : "否"}</span>
          <span>超时开启：${auditState.timeout_enabled_now ? "是" : "否"}</span>
          <span>当前可启动：${auditState.can_launch_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_process_lifecycle_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-process-lifecycle-implementation-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>适配器审计：${escapeHtml(report.adapter_audit_status || "missing")}</span>
                <span>已创建进程：${state.process_created_now ? "是" : "否"}</span>
                <span>已记录 PID：${state.pid_recorded_now ? "是" : "否"}</span>
                <span>进程控制开启：${state.process_control_enabled_now ? "是" : "否"}</span>
                <span>当前可启动：${state.can_launch_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 进程生命周期实现准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerStreamCaptureImplementationAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.stream_capture_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-stream-capture-implementation-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪", summary.ready_item_count)}
        ${metric("已开流", summary.stream_open_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner stdout/stderr 捕获实现准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>输出流捕获审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来 stdout/stderr 捕获实现前必须锁定的分块、脱敏、背压、保留策略和终止态关联；不打开 stdout/stderr、不读取输出流、不写日志、不写 Runner 事件、不创建进程、不注册 launch/cancel/timeout API、不导入或调用适配器、不写审计日志、不收集授权、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>stdout 已打开：${auditState.stdout_opened_now ? "是" : "否"}</span>
          <span>stderr 已打开：${auditState.stderr_opened_now ? "是" : "否"}</span>
          <span>捕获开启：${auditState.stream_capture_enabled_now ? "是" : "否"}</span>
          <span>已持久化：${auditState.stream_persisted_now ? "是" : "否"}</span>
          <span>已写日志：${auditState.log_written_now ? "是" : "否"}</span>
          <span>当前可启动：${auditState.can_launch_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_stream_capture_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-stream-capture-implementation-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>进程审计：${escapeHtml(report.process_lifecycle_audit_status || "missing")}</span>
                <span>stdout 已打开：${state.stdout_opened_now ? "是" : "否"}</span>
                <span>stderr 已打开：${state.stderr_opened_now ? "是" : "否"}</span>
                <span>捕获开启：${state.stream_capture_enabled_now ? "是" : "否"}</span>
                <span>已写日志：${state.log_written_now ? "是" : "否"}</span>
                <span>当前可启动：${state.can_launch_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner stdout/stderr 捕获实现准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerEventWriterImplementationAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.event_writer_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-event-writer-implementation-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪", summary.ready_item_count)}
        ${metric("已写事件", summary.event_write_count)}
        ${metric("已写日志", summary.log_write_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 事件写入实现准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>事件写入审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来 Runner event 写入前必须锁定的 schema、顺序、终止态、失败处理和脱敏规则；不写 Runner event、不打开 event log、不写日志、不创建进程、不打开 stdout/stderr、不注册 launch/cancel/timeout API、不调用适配器、不写审计日志、不收集授权、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>写入器已实现：${auditState.event_writer_implemented_now ? "是" : "否"}</span>
          <span>事件已写入：${auditState.event_written_now ? "是" : "否"}</span>
          <span>event log 已打开：${auditState.event_log_opened_now ? "是" : "否"}</span>
          <span>事件已持久化：${auditState.event_persisted_now ? "是" : "否"}</span>
          <span>日志已写入：${auditState.log_written_now ? "是" : "否"}</span>
          <span>当前可启动：${auditState.can_launch_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_event_writer_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-event-writer-implementation-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>输出审计：${escapeHtml(report.stream_capture_audit_status || "missing")}</span>
                <span>事件已写入：${state.event_written_now ? "是" : "否"}</span>
                <span>event log 已打开：${state.event_log_opened_now ? "是" : "否"}</span>
                <span>事件已持久化：${state.event_persisted_now ? "是" : "否"}</span>
                <span>日志已写入：${state.log_written_now ? "是" : "否"}</span>
                <span>当前可启动：${state.can_launch_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 事件写入实现准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerAuditPersistenceImplementationAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.audit_persistence_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-audit-persistence-implementation-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪", summary.ready_item_count)}
        ${metric("审计记录", summary.audit_record_count)}
        ${metric("已写审计", summary.audit_write_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 审计持久化实现准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>审计持久化审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来人工授权证据、启动决策、事件链摘要、失败原因和不可抵赖审计记录之间的关联规则；不写审计记录、不打开或读取 audit log、不写 Runner event、不写日志、不创建进程、不打开 stdout/stderr、不注册 launch/cancel/timeout API、不调用适配器、不收集授权、不写用户项目。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>持久化已实现：${auditState.audit_persistence_implemented_now ? "是" : "否"}</span>
          <span>审计记录已写入：${auditState.audit_record_written_now ? "是" : "否"}</span>
          <span>audit log 已打开：${auditState.audit_log_opened_now ? "是" : "否"}</span>
          <span>审计记录已持久化：${auditState.audit_record_persisted_now ? "是" : "否"}</span>
          <span>审计记录已读取：${auditState.audit_record_read_now ? "是" : "否"}</span>
          <span>当前可启动：${auditState.can_launch_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_audit_persistence_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-audit-persistence-implementation-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>事件审计：${escapeHtml(report.event_writer_audit_status || "missing")}</span>
                <span>审计记录已写入：${state.audit_record_written_now ? "是" : "否"}</span>
                <span>audit log 已打开：${state.audit_log_opened_now ? "是" : "否"}</span>
                <span>审计记录已持久化：${state.audit_record_persisted_now ? "是" : "否"}</span>
                <span>审计记录已读取：${state.audit_record_read_now ? "是" : "否"}</span>
                <span>当前可启动：${state.can_launch_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 审计持久化实现准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerAuditIntegrityReplayVerificationAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.integrity_replay_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-audit-integrity-replay-verification-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪", summary.ready_item_count)}
        ${metric("完整性校验", summary.integrity_check_count)}
        ${metric("回放校验", summary.replay_check_count)}
        ${metric("一致性校验", summary.consistency_check_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 审计完整性与回放校验准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>完整性回放审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来审计记录、Runner event、启动配置、失败原因之间如何做一致性校验和回放核验；不读取 audit log、不读取审计记录、不读取 Runner event、不读取配置快照、不执行完整性校验、不执行回放、不写事件、不写日志、不创建进程。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>完整性校验已实现：${auditState.integrity_verification_implemented_now ? "是" : "否"}</span>
          <span>回放校验已实现：${auditState.replay_verification_implemented_now ? "是" : "否"}</span>
          <span>audit log 已打开：${auditState.audit_log_opened_now ? "是" : "否"}</span>
          <span>审计记录已读取：${auditState.audit_record_read_now ? "是" : "否"}</span>
          <span>Runner event 已读取：${auditState.runner_event_read_now ? "是" : "否"}</span>
          <span>配置快照已读取：${auditState.config_snapshot_read_now ? "是" : "否"}</span>
          <span>当前可启动：${auditState.can_launch_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_integrity_replay_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-audit-integrity-replay-verification-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>审计持久化：${escapeHtml(report.audit_persistence_audit_status || "missing")}</span>
                <span>审计记录已读取：${state.audit_record_read_now ? "是" : "否"}</span>
                <span>Runner event 已读取：${state.runner_event_read_now ? "是" : "否"}</span>
                <span>配置快照已读取：${state.config_snapshot_read_now ? "是" : "否"}</span>
                <span>完整性已校验：${state.integrity_checked_now ? "是" : "否"}</span>
                <span>回放已校验：${state.replay_checked_now ? "是" : "否"}</span>
                <span>一致性已校验：${state.consistency_checked_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 审计完整性与回放校验准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerEvidenceGapIndexes(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const indexSchema = payload.evidence_gap_index_schema || {};
  const indexState = indexSchema.index_state || {};
  return `
    <div class="runner-evidence-gap-indexes">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("索引项", summary.index_entry_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("预启动阻断", summary.pre_launch_blocker_count)}
        ${metric("必备层", summary.required_layer_count)}
        ${metric("导航目标", summary.navigation_target_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 证据索引与缺口导航状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>证据缺口索引 schema：${escapeHtml(indexSchema.schema_version || "")}</strong>
        <span>当前只把最终闸门的内存报告整理为 UI 导航索引；不读日志、不读 Runner event、不读审计记录、不读配置快照、不执行校验、不创建进程、不开放真实启动 API。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${indexState.read_only ? "是" : "否"}</span>
          <span>来自内存 payload：${indexState.index_generated_from_in_memory_payload ? "是" : "否"}</span>
          <span>日志已读取：${indexState.log_file_read_now ? "是" : "否"}</span>
          <span>Runner event 已读取：${indexState.runner_event_read_now ? "是" : "否"}</span>
          <span>audit log 已读取：${indexState.audit_log_read_now ? "是" : "否"}</span>
          <span>启动 API 已注册：${indexState.launch_api_registered_now ? "是" : "否"}</span>
          <span>进程已创建：${indexState.process_created_now ? "是" : "否"}</span>
          <span>适配器已调用：${indexState.adapter_called_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(indexSchema.entry_kinds || []).map((item) => `
            <span>类型<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(indexSchema.required_navigation_contract || []).map((item) => `
            <span>导航合约<small>${escapeHtml(item.key || "")}</small></span>
          `).join("")}
          ${(indexSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-evidence-gap-index-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>最终闸门：${escapeHtml(report.final_gate_audit_status || "missing")}</span>
              <span>索引项：${(report.index_entries || []).length}</span>
            </div>
            <div class="runner-session-events">
              ${(report.index_entries || []).map((item) => `
                <span>${escapeHtml(item.kind || "gap")}<small>${escapeHtml(item.title || item.key || "")} -> ${escapeHtml(item.navigation?.stage_key || "")}</small></span>
              `).join("")}
              ${(report.blocked_actions || []).map((item) => `
                <span>禁止<small>${escapeHtml(item)}</small></span>
              `).join("")}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 证据索引与缺口导航。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerRealLaunchFinalGateAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.final_gate_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-real-launch-final-gate-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("必备层", summary.required_layer_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("预启动阻断", summary.pre_launch_blocker_count)}
        ${metric("真实决策", summary.final_gate_decision_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 真实启动最终闸门准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>最终闸门审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只汇总前置只读审计层，说明真实启动仍被哪些证据和硬边界阻断；不注册启动接口、不启用启动按钮、不授权、不调用适配器、不创建进程、不读写事件/日志/审计记录/配置快照。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>最终门禁已实现：${auditState.final_gate_implemented_now ? "是" : "否"}</span>
          <span>真实决策已做出：${auditState.final_gate_decision_made_now ? "是" : "否"}</span>
          <span>真实启动允许：${auditState.real_launch_allowed_now ? "是" : "否"}</span>
          <span>启动 API 已注册：${auditState.real_launch_api_registered_now ? "是" : "否"}</span>
          <span>适配器已调用：${auditState.adapter_called_now ? "是" : "否"}</span>
          <span>进程已创建：${auditState.process_created_now ? "是" : "否"}</span>
          <span>授权已采集：${auditState.authorization_collected_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_layers || []).map((item) => `
            <span>必备层<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(auditSchema.required_final_gate_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-real-launch-final-gate-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>差异报告审计：${escapeHtml(report.verification_discrepancy_report_audit_status || "missing")}</span>
                <span>真实启动允许：${state.real_launch_allowed_now ? "是" : "否"}</span>
                <span>启动 API 已注册：${state.real_launch_api_registered_now ? "是" : "否"}</span>
                <span>启动按钮已启用：${state.launch_button_enabled_now ? "是" : "否"}</span>
                <span>适配器已调用：${state.adapter_called_now ? "是" : "否"}</span>
                <span>进程已创建：${state.process_created_now ? "是" : "否"}</span>
                <span>Runner event 已读取：${state.runner_event_read_now ? "是" : "否"}</span>
                <span>audit log 已读取：${state.audit_log_read_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.pre_launch_blockers || []).map((item) => `
                  <span>${escapeHtml(item.status || "blocked")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 真实启动最终闸门准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerVerificationDiscrepancyReportAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.discrepancy_report_audit_schema || {};
  const auditState = auditSchema.audit_state || {};
  return `
    <div class="runner-verification-discrepancy-report-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("审计项", summary.audit_item_count)}
        ${metric("缺证据", summary.missing_evidence_count)}
        ${metric("已就绪", summary.ready_item_count)}
        ${metric("差异报告", summary.discrepancy_report_count)}
        ${metric("阻断决策", summary.blocking_decision_count)}
        ${metric("操作者消息", summary.operator_message_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 校验差异报告实现准备审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>差异报告审计 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只审计未来完整性/回放校验发现差异后如何分类、分级、展示、关联证据和阻断真实启动；不读取 audit log、不读取 Runner event、不执行回放、不生成真实差异报告、不做启动阻断决策、不写事件、不写日志、不创建进程。</span>
        <div class="runner-snapshot-evidence">
          <span>只读：${auditState.read_only ? "是" : "否"}</span>
          <span>差异报告已实现：${auditState.discrepancy_report_implemented_now ? "是" : "否"}</span>
          <span>真实报告已生成：${auditState.discrepancy_report_generated_now ? "是" : "否"}</span>
          <span>阻断决策已做出：${auditState.blocking_decision_made_now ? "是" : "否"}</span>
          <span>操作者消息已生成：${auditState.operator_message_generated_now ? "是" : "否"}</span>
          <span>audit log 已打开：${auditState.audit_log_opened_now ? "是" : "否"}</span>
          <span>Runner event 已读取：${auditState.runner_event_read_now ? "是" : "否"}</span>
          <span>校验已执行：${auditState.verification_executed_now ? "是" : "否"}</span>
        </div>
        <div class="runner-session-events">
          ${(auditSchema.required_discrepancy_report_evidence || []).map((item) => `
            <span>证据<small>${escapeHtml(item.title || item.key || "")}</small></span>
          `).join("")}
          ${(auditSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.audit_state || {};
          return `
            <article class="runner-verification-discrepancy-report-audit-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>回放校验：${escapeHtml(report.integrity_replay_audit_status || "missing")}</span>
                <span>真实报告已生成：${state.discrepancy_report_generated_now ? "是" : "否"}</span>
                <span>阻断决策已做出：${state.blocking_decision_made_now ? "是" : "否"}</span>
                <span>操作者消息已生成：${state.operator_message_generated_now ? "是" : "否"}</span>
                <span>审计记录已读取：${state.audit_record_read_now ? "是" : "否"}</span>
                <span>Runner event 已读取：${state.runner_event_read_now ? "是" : "否"}</span>
                <span>校验已执行：${state.verification_executed_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.audit_items || []).map((item) => `
                  <span>${escapeHtml(item.evidence_status || "missing")}<small>${escapeHtml(item.title || item.key || "")}</small></span>
                `).join("")}
                ${(report.blocked_actions || []).map((item) => `
                  <span>禁止<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 校验差异报告实现准备审计。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLaunchApiContracts(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const contractSchema = payload.contract_schema || {};
  const futureEndpoint = contractSchema.future_endpoint || {};
  return `
    <div class="runner-launch-api-contracts">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("需合约", summary.launch_api_contract_required_count)}
        ${metric("已注册端点", summary.registered_endpoint_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 启动 API 合约状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>合约 schema：${escapeHtml(contractSchema.schema_version || "")}</strong>
        <span>未来端点：${escapeHtml(futureEndpoint.method || "POST")} ${escapeHtml(futureEndpoint.path || "")}；当前未注册，真实启动仍禁用。</span>
        <div class="runner-session-events">
          ${(contractSchema.required_guards || []).map((item) => `
            <span>门槛<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(contractSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const contract = report.launch_api_contract || {};
          const endpoint = contract.future_endpoint || {};
          const request = contract.request_contract || {};
          const idempotency = contract.idempotency_contract || {};
          return `
            <article class="runner-launch-api-contract-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>适配器合约：${escapeHtml(report.execution_adapter_contract_status || "missing")}</span>
                <span>未来端点：${escapeHtml(endpoint.method || "POST")} ${escapeHtml(endpoint.path || "")}</span>
                <span>当前注册：${endpoint.registered_now ? "是" : "否"}</span>
                <span>幂等键：${endpoint.requires_idempotency_key ? "必需" : "未声明"}</span>
              </div>
              <div class="runner-session-events">
                ${(request.required_fields || []).map((item) => `
                  <span>必填<small>${escapeHtml(item)}</small></span>
                `).join("")}
                ${(request.forbidden_fields || []).map((item) => `
                  <span>禁止字段<small>${escapeHtml(item)}</small></span>
                `).join("")}
                <span>幂等范围<small>${escapeHtml(idempotency.scope || "")}</small></span>
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 启动 API 合约报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerExecutionAdapterContracts(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const contractSchema = payload.contract_schema || {};
  return `
    <div class="runner-execution-adapter-contracts">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("需合约", summary.adapter_contract_required_count)}
        ${metric("阻塞", summary.blocked_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 执行适配器合约状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>合约 schema：${escapeHtml(contractSchema.schema_version || "")}</strong>
        <span>当前只声明未来执行适配器接口；真实启动 API、进程创建、stdout/stderr 文件打开和 runner 日志写入仍禁用。</span>
        <div class="runner-session-events">
          ${(contractSchema.adapter_interface || []).map((item) => `
            <span>接口<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(contractSchema.hooks || []).map((item) => `
            <span>钩子<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(contractSchema.blocked_actions || []).map((item) => `
            <span>禁止<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const contract = report.adapter_contract || {};
          const argvContract = contract.argv_contract || {};
          return `
            <article class="runner-execution-adapter-contract-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>治理状态：${escapeHtml(report.governance_status || "missing")}</span>
                <span>argv token：${argvContract.argv_must_be_tokenized ? "是" : "否"}</span>
                <span>shell 字符串：${argvContract.shell_string_allowed ? "允许" : "禁止"}</span>
                <span>继承环境变量：${argvContract.inherit_environment ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(contract.required_inputs || []).map((item) => `
                  <span>输入<small>${escapeHtml(item)}</small></span>
                `).join("")}
                ${(contract.required_outputs || []).map((item) => `
                  <span>未来输出<small>${escapeHtml(item)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 执行适配器合约报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerGovernanceReadiness(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const governanceSchema = payload.governance_schema || {};
  return `
    <div class="runner-governance-readiness">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("治理层", summary.layer_count)}
        ${metric("阻塞", summary.blocked_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 治理就绪度状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>治理 schema：${escapeHtml(governanceSchema.schema_version || "")}</strong>
        <span>当前只汇总只读治理层；真实启动 API、进程执行、日志写入和清理仍禁用。</span>
        <div class="runner-session-events">
          ${(governanceSchema.blocked_until_future_layers || []).map((item) => `
            <span>未实现<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-governance-readiness-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>可启动：${report.launch_state?.launchable ? "是" : "否"}</span>
              <span>启动 API：${report.launch_state?.launch_api_available ? "可用" : "不可用"}</span>
              <span>真实执行：${report.launch_state?.launch_enabled ? "启用" : "禁用"}</span>
              <span>层数：${escapeHtml(String((report.layer_states || []).length))}</span>
            </div>
            <div class="runner-session-events">
              ${(report.layer_states || []).map((layer) => `
                <span>${escapeHtml(layer.label || layer.key || "")}<small>${escapeHtml(layer.report_status || "")}</small></span>
              `).join("")}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 治理就绪度报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLogCleanupPreviews(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const cleanupPreviewSchema = payload.cleanup_preview_schema || {};
  const requiredConfirmation = cleanupPreviewSchema.required_future_confirmation || {};
  return `
    <div class="runner-log-cleanup-previews">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待预览", summary.preview_required_count)}
        ${metric("计划删除", summary.previewed_deletion_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 日志清理预览状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>清理预览 schema：${escapeHtml(cleanupPreviewSchema.schema_version || "")}</strong>
        <span>当前只消费日志保留策略报告；不扫描真实目录，不读取日志文件，不删除、轮转、重命名、截断或写入日志。</span>
        <div class="runner-snapshot-evidence">
          <span>确认短语：${escapeHtml(requiredConfirmation.typed_consent || "")}</span>
          <span>范围确认：${escapeHtml(requiredConfirmation.scope_acknowledgement || "")}</span>
          <span>真实清理：禁用</span>
          <span>目录扫描：否</span>
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const previewCounts = report.preview_counts || {};
          return `
            <article class="runner-log-cleanup-preview-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>保留策略：${escapeHtml(report.log_retention_policy_status || "missing")}</span>
                <span>候选目录：${escapeHtml(previewCounts.candidate_directory_count ?? 0)}</span>
                <span>计划删除：${escapeHtml(previewCounts.planned_delete_count ?? 0)}</span>
                <span>计划轮转：${escapeHtml(previewCounts.planned_rotate_count ?? 0)}</span>
              </div>
              <div class="runner-session-events">
                ${(report.candidate_directories || []).map((directory) => `
                  <span>候选：<small>${escapeHtml(directory)}</small></span>
                `).join("")}
                ${(report.risk_warnings || []).map((warning) => `
                  <span>风险：<small>${escapeHtml(warning.message || warning.id || "")}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 日志清理预览报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLogCleanupConfirmations(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const confirmationSchema = payload.cleanup_confirmation_schema || {};
  const requiredConfirmation = confirmationSchema.required_future_confirmation || {};
  return `
    <div class="runner-log-cleanup-confirmations">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待确认", summary.confirmation_required_count)}
        ${metric("已确认", summary.confirmed_cleanup_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 日志清理确认状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>清理确认 schema：${escapeHtml(confirmationSchema.schema_version || "")}</strong>
        <span>当前只声明未来确认门槛；不收集确认、不写确认记录、不扫描目录、不读取日志、不删除、轮转、重命名、截断或写入日志。</span>
        <div class="runner-snapshot-evidence">
          <span>确认短语：${escapeHtml(requiredConfirmation.typed_consent || "")}</span>
          <span>范围确认：${escapeHtml(requiredConfirmation.scope_acknowledgement || "")}</span>
          <span>候选清单：${escapeHtml(requiredConfirmation.candidate_manifest_acknowledgement || "")}</span>
          <span>不可逆动作：${escapeHtml(requiredConfirmation.irreversible_action_acknowledgement || "")}</span>
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const previewCounts = report.preview_counts || {};
          const confirmationState = report.confirmation_state || {};
          return `
            <article class="runner-log-cleanup-confirmation-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>清理预览：${escapeHtml(report.cleanup_preview_status || "missing")}</span>
                <span>确认状态：${escapeHtml(confirmationState.status || "not_collected")}</span>
                <span>已确认：${confirmationState.confirmed ? "是" : "否"}</span>
                <span>当前可确认：${confirmationState.can_confirm_now ? "是" : "否"}</span>
                <span>候选目录：${escapeHtml(previewCounts.candidate_directory_count ?? 0)}</span>
              </div>
              <div class="runner-session-events">
                ${(report.confirmation_gates || []).map((gate) => `
                  <span>确认门槛：<small>${escapeHtml(gate)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 日志清理确认报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLogCleanupAuditTrails(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const auditSchema = payload.cleanup_audit_trail_schema || {};
  const auditSink = auditSchema.audit_sink || {};
  return `
    <div class="runner-log-cleanup-audit-trails">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待追踪", summary.audit_trail_required_count)}
        ${metric("已记录事件", summary.stored_audit_event_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 日志清理审计追踪状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>审计追踪 schema：${escapeHtml(auditSchema.schema_version || "")}</strong>
        <span>当前只声明未来审计事件；不写审计日志、不读审计日志、不扫描目录、不读取日志、不删除、轮转、重命名、截断或写入日志。</span>
        <div class="runner-snapshot-evidence">
          <span>计划审计文件：${escapeHtml(auditSink.planned_file || "")}</span>
          <span>当前写入：${auditSink.write_now ? "是" : "否"}</span>
          <span>当前读取：${auditSink.read_now ? "是" : "否"}</span>
          <span>事件字段：${escapeHtml((auditSchema.required_event_fields || []).length)}</span>
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const auditState = report.audit_state || {};
          return `
            <article class="runner-log-cleanup-audit-trail-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>清理确认：${escapeHtml(report.cleanup_confirmation_status || "missing")}</span>
                <span>审计状态：${escapeHtml(auditState.status || "not_recorded")}</span>
                <span>已保存：${auditState.stored ? "是" : "否"}</span>
                <span>事件数：${escapeHtml(auditState.event_count ?? 0)}</span>
                <span>当前可写：${auditState.can_write_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.required_future_events || []).map((eventName) => `
                  <span>未来事件：<small>${escapeHtml(eventName)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 日志清理审计追踪报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLogCleanupExecutionPlans(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const planSchema = payload.cleanup_execution_plan_schema || {};
  const manifest = planSchema.candidate_manifest || {};
  const planState = planSchema.plan_state || {};
  return `
    <div class="runner-log-cleanup-execution-plans">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待计划", summary.execution_plan_required_count)}
        ${metric("计划操作", summary.planned_operation_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 日志清理执行计划状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>执行计划 schema：${escapeHtml(planSchema.schema_version || "")}</strong>
        <span>当前只声明未来清理执行计划；不生成候选清单、不保存计划、不扫描目录、不读取日志、不删除、轮转、重命名、截断或写入日志，也不读写审计日志。</span>
        <div class="runner-snapshot-evidence">
          <span>当前写计划：${planState.write_now ? "是" : "否"}</span>
          <span>当前读计划：${planState.read_now ? "是" : "否"}</span>
          <span>当前执行：${planState.execute_now ? "是" : "否"}</span>
          <span>候选清单 hash：${manifest.requires_hash ? escapeHtml(manifest.hash_algorithm || "required") : "未声明"}</span>
        </div>
        <div class="runner-session-events">
          ${(planSchema.allowed_future_operation_types || []).map((item) => `
            <span>允许未来操作<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(planSchema.forbidden_future_operation_types || []).map((item) => `
            <span>禁止未来操作<small>${escapeHtml(item)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const state = report.plan_state || {};
          return `
            <article class="runner-log-cleanup-execution-plan-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>审计追踪：${escapeHtml(report.cleanup_audit_trail_status || "missing")}</span>
                <span>计划状态：${escapeHtml(state.status || "not_planned")}</span>
                <span>已保存：${state.stored ? "是" : "否"}</span>
                <span>操作数：${escapeHtml(state.operation_count ?? 0)}</span>
                <span>当前可执行：${state.can_execute_now ? "是" : "否"}</span>
              </div>
              <div class="runner-session-events">
                ${(report.required_future_plan_fields || []).map((field) => `
                  <span>字段<small>${escapeHtml(field)}</small></span>
                `).join("")}
                ${(report.required_future_gates || []).map((gate) => `
                  <span>门槛<small>${escapeHtml(gate)}</small></span>
                `).join("")}
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 日志清理执行计划报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLogRetentionPolicies(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const logRetentionSchema = payload.log_retention_schema || {};
  const retentionLimits = logRetentionSchema.retention_limits || {};
  const rotationLimits = logRetentionSchema.rotation_limits || {};
  return `
    <div class="runner-log-retention-policies">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待策略", summary.policy_required_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 日志保留策略状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>日志保留 schema：${escapeHtml(logRetentionSchema.schema_version || "")}</strong>
        <span>当前只声明保留和轮转约束；不扫描目录，不删除日志，不重命名日志，不截断文件，不写入日志。</span>
        <div class="runner-snapshot-evidence">
          <span>保留运行数：${escapeHtml(retentionLimits.max_retained_runs_per_profile ?? "")}</span>
          <span>保留天数：${escapeHtml(retentionLimits.retain_days ?? "")}</span>
          <span>单次上限：${escapeHtml(retentionLimits.max_single_run_log_bytes ?? "")}</span>
          <span>总量上限：${escapeHtml(retentionLimits.max_total_profile_log_bytes ?? "")}</span>
        </div>
        <div class="runner-snapshot-evidence">
          <span>stdout 轮转：${escapeHtml(rotationLimits.stdout_rotate_bytes ?? "")}</span>
          <span>stderr 轮转：${escapeHtml(rotationLimits.stderr_rotate_bytes ?? "")}</span>
          <span>events 轮转：${escapeHtml(rotationLimits.runner_events_rotate_bytes ?? "")}</span>
          <span>轮转文件数：${escapeHtml(rotationLimits.max_rotated_files_per_stream ?? "")}</span>
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-log-retention-policy-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>日志目录策略：${escapeHtml(report.log_directory_policy_status || "missing")}</span>
              <span>扫描目录：否</span>
              <span>删除日志：否</span>
              <span>轮转日志：否</span>
            </div>
            <div class="runner-session-events">
              ${(report.candidate_directories || []).map((directory) => `
                <span>候选：<small>${escapeHtml(directory)}</small></span>
              `).join("")}
              ${(report.cleanup_rules || []).map((rule) => `
                <span>规则：<small>${escapeHtml(rule)}</small></span>
              `).join("")}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 日志保留策略报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLogDirectoryPolicies(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const logDirectorySchema = payload.log_directory_schema || {};
  return `
    <div class="runner-log-directory-policies">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待策略", summary.policy_required_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 日志目录策略状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>日志目录 schema：${escapeHtml(logDirectorySchema.schema_version || "")}</strong>
        <span>当前只声明候选目录和未来文件名；不创建目录，不打开日志文件，不写 stdout/stderr/events/summary。</span>
        <div class="runner-session-events">
          <span>候选根目录：<small>${escapeHtml(logDirectorySchema.candidate_root || "")}</small></span>
          <span>目录模板：<small>${escapeHtml(logDirectorySchema.directory_template || "")}</small></span>
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-log-directory-policy-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>服务开关审计：${escapeHtml(report.service_flag_audit_status || "missing")}</span>
              <span>创建目录：否</span>
              <span>写入日志：否</span>
              <span>真实执行：禁用</span>
            </div>
            <div class="runner-session-events">
              ${(report.candidate_directories || []).map((directory) => `
                <span>候选：<small>${escapeHtml(directory)}</small></span>
              `).join("")}
              ${(report.required_future_files || []).map((fileName) => `
                <span>未来文件：<small>${escapeHtml(fileName)}</small></span>
              `).join("")}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 日志目录策略报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerServiceFlagAudits(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const serviceFlagSchema = payload.service_flag_schema || {};
  const requiredFlags = serviceFlagSchema.required_future_flags || {};
  return `
    <div class="runner-service-flag-audits">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待开关", summary.service_flags_required_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 服务开关审计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>服务开关 schema：${escapeHtml(serviceFlagSchema.schema_version || "")}</strong>
        <span>当前只消费配置检查报告；不读取环境变量，不解析当前进程参数，不创建真实启动 API。</span>
        <div class="runner-snapshot-evidence">
          <span>服务参数：${escapeHtml(requiredFlags.server_flag || "")}</span>
          <span>环境开关：${escapeHtml(requiredFlags.environment_flag || "")}</span>
          <span>配置开关：${escapeHtml(requiredFlags.config_flag || "")}</span>
          <span>确认短语：${escapeHtml(requiredFlags.typed_consent || "")}</span>
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-service-flag-audit-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>配置检查：${escapeHtml(report.config_check_status || "missing")}</span>
              <span>启动 API：不可用</span>
              <span>真实执行：禁用</span>
              <span>读取环境：否</span>
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 服务开关审计报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerExecutionConfigChecks(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const checkSchema = payload.config_check_schema || {};
  const configFile = payload.config_file || {};
  return `
    <div class="runner-execution-config-checks">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("已读取", summary.config_present_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 配置检查状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>检查 schema：${escapeHtml(checkSchema.schema_version || "")}</strong>
        <span>配置状态：${escapeHtml(configFile.status || "missing")}；当前阶段只读取，不创建或修改配置文件。</span>
        <div class="runner-session-events">
          ${(checkSchema.candidate_paths || []).map((path) => `
            <span>候选<small>${escapeHtml(path)}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-execution-config-check-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>配置文件：${escapeHtml(report.config_file?.status || "missing")}</span>
              <span>路径：${escapeHtml(report.config_file?.path || "未发现")}</span>
              <span>启动 API：不可用</span>
              <span>真实执行：禁用</span>
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 配置检查报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerConfigSchemaStabilizations(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const schema = payload.config_schema_stabilization_schema || {};
  const defaultPolicy = schema.default_policy || {};
  return `
    <div class="runner-config-schema-stabilizations">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("字段契约", summary.field_contract_count)}
        ${metric("兼容规则", summary.compatibility_rule_count)}
        ${metric("错误码", summary.error_code_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 配置 Schema 稳定化状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>配置文件 schema：${escapeHtml(schema.config_file_schema_version || "")}</strong>
        <span>配置文件：${escapeHtml(schema.config_file_name || "")}；当前只稳定字段、兼容性和错误码，不创建配置、不开放启动 API。</span>
        <div class="runner-snapshot-evidence">
          <span>支持版本：${escapeHtml((schema.supported_versions || []).join(", "))}</span>
          <span>默认真实执行：${defaultPolicy["runner.enable_real_execution"] ? "启用" : "禁用"}</span>
          <span>启动 API：不可用</span>
          <span>真实执行：禁用</span>
        </div>
        <div class="runner-session-events">
          ${(schema.field_contracts || []).slice(0, 10).map((item) => `
            <span>${escapeHtml(item.path || "")}<small>${escapeHtml(item.error_code || item.type || "")}</small></span>
          `).join("")}
          ${(schema.compatibility_rules || []).slice(0, 8).map((item) => `
            <span>兼容<small>${escapeHtml(item.key || "")}</small></span>
          `).join("")}
          ${(schema.error_map || []).slice(0, 8).map((item) => `
            <span>错误码<small>${escapeHtml(item.code || "")}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-config-schema-stabilization-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>稳定版本：${escapeHtml(report.stable_config_schema_version || "")}</span>
              <span>执行配置：${escapeHtml(report.execution_config_status || "missing")}</span>
              <span>配置检查：${escapeHtml(report.config_check_status || "missing")}</span>
              <span>支持版本：${escapeHtml((report.supported_versions || []).join(", "))}</span>
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 配置 Schema 稳定化报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerConfigFieldContractViews(payload) {
  const summary = payload.summary || {};
  const nextAction = payload.next_action || {};
  const schema = payload.field_contract_view_schema || {};
  const sections = payload.sections || [];
  const fieldContracts = payload.field_contracts || [];
  const errorCodes = payload.error_codes || [];
  const reports = payload.reports || [];
  return `
    <div class="runner-config-field-contract-views">
      <div class="integration-summary">
        ${metric("字段契约", summary.field_contract_count)}
        ${metric("必填字段", summary.required_field_count)}
        ${metric("默认值", summary.default_value_count)}
        ${metric("错误码", summary.error_code_count)}
        ${metric("分组", summary.section_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 配置字段契约说明")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>字段契约视图 schema：${escapeHtml(schema.schema_version || "")}</strong>
        <span>稳定配置版本：${escapeHtml(schema.stable_config_schema_version || "")}；当前只展示字段类型、默认值和错误码，辅助用户手动修复配置；不写配置、不执行命令。</span>
        <div class="runner-snapshot-evidence">
          <span>配置文件：${escapeHtml(schema.config_file_name || "")}</span>
          <span>支持版本：${escapeHtml((schema.supported_versions || []).join(", "))}</span>
          <span>字段契约：${escapeHtml(String(fieldContracts.length))}</span>
          <span>错误码：${escapeHtml(String(errorCodes.length))}</span>
        </div>
        <div class="runner-session-events">
          ${sections.map((item) => `
            <span>${escapeHtml(item.title || item.key || "")}<small>${escapeHtml(String(item.field_count || 0))} fields</small></span>
          `).join("")}
        </div>
      </div>
      <div class="runner-session-schema">
        <strong>字段类型与默认值</strong>
        <div class="runner-session-events">
          ${fieldContracts.map((item) => `
            <button
              type="button"
              data-runner-config-issue-target
              data-stage-key="${escapeHtml(item.navigation?.stage_key || "runner_config_field_contract_views")}"
              data-evidence-title="${escapeHtml(item.navigation?.evidence_group || "Field contracts")}"
              data-item-key="${escapeHtml(item.navigation?.item_key || "")}"
            >
              ${escapeHtml(item.path || "")}
              <small>${escapeHtml(`${item.type || ""} | default=${item.default_display ?? ""} | ${item.error_code || ""}`)}</small>
            </button>
          `).join("") || `<span>字段契约<small>暂无字段契约。</small></span>`}
        </div>
      </div>
      <div class="runner-session-schema">
        <strong>错误码说明</strong>
        <div class="runner-session-events">
          ${errorCodes.map((item) => `
            <button
              type="button"
              data-runner-config-issue-target
              data-stage-key="${escapeHtml(item.navigation?.stage_key || "runner_config_field_contract_views")}"
              data-evidence-title="${escapeHtml(item.navigation?.evidence_group || "Error codes")}"
              data-item-key="${escapeHtml(item.navigation?.item_key || "")}"
            >
              ${escapeHtml(item.code || "")}
              <small>${escapeHtml(`${item.field || ""}: ${item.message || ""}`)}</small>
            </button>
          `).join("") || `<span>错误码<small>暂无错误码。</small></span>`}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-config-field-contract-view ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.status_label || report.status || "Runner 配置字段契约说明")}</strong>
            <span>${escapeHtml(report.stable_config_schema_version || "")}</span>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>字段契约：${escapeHtml(report.field_contract_count ?? 0)}</span>
              <span>错误码：${escapeHtml(report.error_code_count ?? 0)}</span>
              <span>分组：${escapeHtml(report.section_count ?? 0)}</span>
              <span>真实执行：禁用</span>
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 配置字段契约说明。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerConfigCompatibilityReports(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const schema = payload.compatibility_report_schema || {};
  return `
    <div class="runner-config-compatibility-reports">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("候选配置", summary.config_present_count)}
        ${metric("兼容问题", summary.compatibility_issue_count)}
        ${metric("缺字段", summary.missing_field_count)}
        ${metric("类型错误", summary.type_mismatch_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 配置兼容性报告状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>兼容性报告 schema：${escapeHtml(schema.schema_version || "")}</strong>
        <span>稳定配置版本：${escapeHtml(schema.stable_config_schema_version || "")}；当前只消费上游配置检查的内存 payload，不直接读取或写入配置。</span>
        <div class="runner-snapshot-evidence">
          <span>支持版本：${escapeHtml((schema.supported_versions || []).join(", "))}</span>
          <span>字段契约：${escapeHtml(String((schema.field_contracts || []).length))}</span>
          <span>兼容规则：${escapeHtml(String((schema.compatibility_rules || []).length))}</span>
          <span>错误码：${escapeHtml(String((schema.error_map || []).length))}</span>
        </div>
        <div class="runner-session-events">
          ${(schema.issue_kinds || []).map((item) => `
            <span>问题类型<small>${escapeHtml(item)}</small></span>
          `).join("")}
          ${(schema.error_map || []).slice(0, 8).map((item) => `
            <span>错误码<small>${escapeHtml(item.code || "")}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-config-compatibility-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>配置文件：${escapeHtml(report.config_file_status || "missing")}</span>
              <span>稳定版本：${escapeHtml(report.stable_config_schema_version || "")}</span>
              <span>schema 稳定化：${escapeHtml(report.schema_stabilization_status || "missing")}</span>
              <span>配置检查：${escapeHtml(report.config_check_status || "missing")}</span>
            </div>
            <div class="runner-session-events">
              ${(report.compatibility_issues || []).slice(0, 10).map((issue) => `
                <span>${escapeHtml(issue.error_code || issue.kind || "")}<small>${escapeHtml(`${issue.field || ""}：${issue.message || ""}`)}</small></span>
              `).join("") || `<span>兼容性<small>暂无候选配置问题。</small></span>`}
            </div>
            <div class="runner-session-events runner-config-issue-targets">
              ${(report.index_entries || []).slice(0, 10).map(renderRunnerConfigCompatibilityIndexEntry).join("")}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 配置兼容性报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerConfigCompatibilityIndexEntry(entry) {
  const navigation = entry.navigation || {};
  return `
    <button
      type="button"
      data-runner-config-issue-target
      data-stage-key="${escapeHtml(navigation.stage_key || "runner_config_compatibility_reports")}"
      data-evidence-title="${escapeHtml(navigation.evidence_group || "配置问题定位")}"
      data-item-key="${escapeHtml(navigation.item_key || entry.key || "")}"
    >
      ${escapeHtml(entry.error_code || entry.title || entry.kind || "")}
      <small>${escapeHtml(entry.detail || entry.field || "")}</small>
    </button>
  `;
}

function installRunnerConfigCompatibilityNavigation(container) {
  for (const button of container.querySelectorAll("[data-runner-config-issue-target]")) {
    button.addEventListener("click", () => {
      container.dispatchEvent(new CustomEvent("flowtrace:runner-stage-target", {
        bubbles: true,
        detail: {
          stageKey: button.dataset.stageKey || "runner_config_compatibility_reports",
          evidenceTitle: button.dataset.evidenceTitle || "配置问题定位",
          itemKey: button.dataset.itemKey || "",
        },
      }));
    });
  }
}

function renderRunnerConfigRemediationSummaries(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  return `
    <div class="runner-config-remediation-summaries">
      <div class="integration-summary">
        ${metric("报告", summary.report_count)}
        ${metric("建议", summary.recommendation_count)}
        ${metric("字段", summary.field_count)}
        ${metric("错误码", summary.error_code_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 配置修复建议")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-config-remediation-summary ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-session-events">
              ${(report.recommendations || []).slice(0, 10).map(renderRunnerConfigRemediationTarget).join("") || `<span>修复建议<small>暂无建议。</small></span>`}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 Runner 配置修复建议。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerConfigRemediationTarget(item) {
  const navigation = item.navigation || {};
  return `
    <button
      type="button"
      data-runner-config-issue-target
      data-stage-key="${escapeHtml(navigation.stage_key || "runner_config_compatibility_reports")}"
      data-evidence-title="${escapeHtml(navigation.evidence_group || "配置问题定位")}"
      data-item-key="${escapeHtml(navigation.item_key || "")}"
    >
      ${escapeHtml(item.error_code || item.issue_kind || "")}
      <small>${escapeHtml(`${item.field || ""}: ${item.action || ""}`)}</small>
    </button>
  `;
}

function renderRunnerConfigFieldCoverageIndexes(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  return `
    <div class="runner-config-field-coverage-indexes">
      <div class="integration-summary">
        ${metric("fields", summary.field_count)}
        ${metric("with issues", summary.field_with_issue_count)}
        ${metric("with fixes", summary.field_with_recommendation_count)}
        ${metric("launchable", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner config field coverage index")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-config-field-coverage-index ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.status_label || report.status || "")}</strong>
            <span>${escapeHtml(`fields=${report.field_count || 0} issues=${report.indexed_issue_count || 0} recommendations=${report.indexed_recommendation_count || 0}`)}</span>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-session-events runner-config-issue-targets">
              ${(report.index_entries || []).slice(0, 10).map(renderRunnerConfigCompatibilityIndexEntry).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">No Runner config field coverage index.</div>`}
      </div>
    </div>
  `;
}

function renderRunnerExecutionConfigs(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const configSchema = payload.execution_config_schema || {};
  return `
    <div class="runner-execution-configs">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("待配置", summary.configuration_required_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 执行配置状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>配置 schema：${escapeHtml(configSchema.schema_version || "")}</strong>
        <span>配置文件：${escapeHtml(configSchema.config_file_name || "")}；当前阶段不自动创建、不写入、不启用真实执行。</span>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => {
          const requirements = report.required_config || {};
          const realExecution = requirements.real_execution || {};
          const isolation = requirements.process_isolation || {};
          const logLimits = requirements.log_limits || {};
          return `
            <article class="runner-execution-config-report ${escapeHtml(report.status || "")}">
              <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
              <span>${escapeHtml(report.status_label || report.status || "")}</span>
              <code>${escapeHtml(report.display_command || "")}</code>
              <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
              <div class="runner-snapshot-evidence">
                <span>配置开关：${escapeHtml(realExecution.config_flag || "")}</span>
                <span>服务开关：${escapeHtml(realExecution.server_flag || "")}</span>
                <span>环境开关：${escapeHtml(realExecution.environment_flag || "")}</span>
                <span>确认短语：${escapeHtml(realExecution.typed_consent || "")}</span>
              </div>
              <div class="runner-snapshot-evidence">
                <span>argv 分离：${isolation.argv_must_be_tokenized ? "是" : "否"}</span>
                <span>禁用 shell 字符串：${isolation.no_shell_string ? "是" : "否"}</span>
                <span>stdout：${escapeHtml(String(logLimits.stdout_chunk_bytes || 0))}B</span>
                <span>stderr：${escapeHtml(String(logLimits.stderr_chunk_bytes || 0))}B</span>
              </div>
              <div class="preflight-checks">
                ${(report.checks || []).map((check) => `
                  <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
                `).join("")}
              </div>
            </article>
          `;
        }).join("") || `<div class="empty">暂无 Runner 执行配置报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerRuntimePolicies(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const runtimeSchema = payload.runtime_schema || {};
  return `
    <div class="runner-runtime-policies">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("策略就绪", summary.ready_policy_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 运行时策略状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>运行时 schema：${escapeHtml(runtimeSchema.schema_version || "")}</strong>
        <span>只定义未来真实 runner 的输出、取消、超时和完成刷新策略。</span>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-runtime-policy-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>stdout 分片：${escapeHtml(String(report.output_policy?.stdout_chunk_bytes || 0))}B</span>
              <span>stderr 分片：${escapeHtml(String(report.output_policy?.stderr_chunk_bytes || 0))}B</span>
              <span>尾部摘要：${escapeHtml(String(report.output_policy?.tail_preview_bytes || 0))}B</span>
              <span>超时：${escapeHtml(String(report.cancellation_policy?.default_timeout_seconds || 0))}s</span>
            </div>
            <div class="runner-session-events">
              ${(report.output_policy?.rules || []).map((item) => `
                <span>${escapeHtml(item.id || "")}<small>${escapeHtml(item.label || "")}</small></span>
              `).join("")}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 runner 运行时策略。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerLaunchControls(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const controlSchema = payload.control_schema || {};
  return `
    <div class="runner-launch-controls">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("策略禁用", summary.disabled_count)}
        ${metric("可启动", summary.launchable_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 启动开关状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>开关 schema：${escapeHtml(controlSchema.schema_version || "")}</strong>
        <span>当前没有真实启动 API；下面是未来允许真实执行前必须满足的条件。</span>
        <div class="runner-session-events">
          ${(controlSchema.future_enablement || []).map((item) => `
            <span>${escapeHtml(item.id || "")}<small>${escapeHtml(item.label || "")}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-launch-control-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>dry-run：${escapeHtml(report.dry_run_id || "未绑定")}</span>
              <span>开关：${escapeHtml(report.switch?.state || "disabled")}</span>
              <span>启动 API：${report.switch?.launch_api_available ? "可用" : "不可用"}</span>
            </div>
            <div class="execution-request-state blocked">
              <span>${escapeHtml(report.switch?.reason || "真实执行被策略禁用")}</span>
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 runner 启动开关报告。</div>`}
      </div>
    </div>
  `;
}

function renderRunnerDryRuns(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const dryRunSchema = payload.dry_run_schema || {};
  return `
    <div class="runner-dry-runs">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("可生成", summary.ready_count)}
        ${metric("已生成", summary.prepared_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Dry-run Runner 状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>dry-run schema：${escapeHtml(dryRunSchema.schema_version || "")}</strong>
        <span>只验证 runner 边界与日志策略，当前不启动进程。</span>
        <div class="runner-session-events">
          ${(dryRunSchema.lifecycle_policy || []).map((item) => `
            <span>${escapeHtml(item.state || "")}<small>${escapeHtml(item.meaning || "")}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-dry-run-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>快照：${escapeHtml(report.preview?.snapshot_id || "未绑定")}</span>
              <span>argv：${escapeHtml(String(report.preview?.argv_count ?? 0))}</span>
              <span>日志：${escapeHtml(report.preview?.planned_logs?.run_directory || "未规划")}</span>
            </div>
            <div class="execution-request-state ${escapeHtml(report.dry_run?.status || "none")}">
              <span>${escapeHtml(runnerDryRunLabel(report.dry_run))}</span>
              ${runnerDryRunButtons(report)}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 dry-run runner 记录。</div>`}
      </div>
    </div>
  `;
}

function runnerDryRunLabel(dryRun = {}) {
  if (dryRun.status === "prepared") {
    return `dry-run 已生成 ${dryRun.created_at || ""}`;
  }
  if (dryRun.status === "stale") {
    return "dry-run 已失效，需要重新生成";
  }
  if (dryRun.status === "blocked") {
    return dryRun.reason || "前置条件未满足";
  }
  return "尚未生成";
}

function runnerDryRunButtons(report) {
  const buttons = [];
  if (report.can_prepare) {
    buttons.push(`<button type="button" data-runner-dry-run-prepare="${escapeHtml(report.profile_id || "")}">生成 dry-run</button>`);
  }
  if (report.can_remove) {
    buttons.push(`<button type="button" data-runner-dry-run-remove="${escapeHtml(report.profile_id || "")}">移除 dry-run</button>`);
  }
  return buttons.join("");
}

function renderRunnerLaunchSnapshots(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const snapshotSchema = payload.snapshot_schema || {};
  return `
    <div class="runner-launch-snapshots">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("可快照", summary.ready_count)}
        ${metric("已快照", summary.snapshotted_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "启动前快照状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>快照 schema：${escapeHtml(snapshotSchema.schema_version || "")}</strong>
        <span>当前只保存启动前证据，不启动 runner。</span>
        <div class="runner-session-events">
          ${(snapshotSchema.rules || []).map((item) => `
            <span>${escapeHtml(item.id || "")}<small>${escapeHtml(item.label || "")}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-launch-snapshot-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-snapshot-evidence">
              <span>会话：${escapeHtml(report.evidence?.runner_session?.session_id || "未绑定")}</span>
              <span>请求：${escapeHtml(report.evidence?.runner_session?.request_id || "未绑定")}</span>
              <span>argv：${escapeHtml(String(report.evidence?.profile?.argv_count ?? 0))}</span>
            </div>
            <div class="execution-request-state ${escapeHtml(report.snapshot?.status || "none")}">
              <span>${escapeHtml(runnerLaunchSnapshotLabel(report.snapshot))}</span>
              ${runnerLaunchSnapshotButtons(report)}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无启动前快照。</div>`}
      </div>
    </div>
  `;
}

function runnerLaunchSnapshotLabel(snapshot = {}) {
  if (snapshot.status === "snapshotted") {
    return `快照已生成 ${snapshot.created_at || ""}`;
  }
  if (snapshot.status === "stale") {
    return "快照已失效，需要重新生成";
  }
  if (snapshot.status === "blocked") {
    return snapshot.reason || "前置条件未满足";
  }
  return "尚未生成";
}

function runnerLaunchSnapshotButtons(report) {
  const buttons = [];
  if (report.can_prepare) {
    buttons.push(`<button type="button" data-runner-launch-snapshot-prepare="${escapeHtml(report.profile_id || "")}">生成快照</button>`);
  }
  if (report.can_remove) {
    buttons.push(`<button type="button" data-runner-launch-snapshot-remove="${escapeHtml(report.profile_id || "")}">移除快照</button>`);
  }
  return buttons.join("");
}

function renderRunnerSessions(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  const eventSchema = payload.event_schema || {};
  return `
    <div class="runner-sessions">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("可生成", summary.ready_count)}
        ${metric("已生成", summary.drafted_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 会话状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="runner-session-schema">
        <strong>事件 schema：${escapeHtml(eventSchema.schema_version || "")}</strong>
        <span>格式：${escapeHtml(eventSchema.format || "jsonl")}；当前只预览结构，不写入运行事件。</span>
        <div class="runner-session-events">
          ${(eventSchema.event_types || []).map((item) => `
            <span>${escapeHtml(item.event_type || "")}<small>${escapeHtml(item.phase || "")}</small></span>
          `).join("")}
        </div>
      </div>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-session-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="execution-request-state ${escapeHtml(report.session?.status || "none")}">
              <span>${escapeHtml(runnerSessionLabel(report.session))}</span>
              ${runnerSessionButtons(report)}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 runner 会话草案。</div>`}
      </div>
    </div>
  `;
}

function runnerSessionLabel(session = {}) {
  if (session.status === "drafted") {
    return `草案已生成 ${session.created_at || ""}`;
  }
  if (session.status === "stale") {
    return "草案已失效，需要重新生成";
  }
  if (session.status === "blocked") {
    return session.reason || "前置条件未满足";
  }
  return "尚未生成";
}

function runnerSessionButtons(report) {
  const buttons = [];
  if (report.can_prepare) {
    buttons.push(`<button type="button" data-runner-session-prepare="${escapeHtml(report.profile_id || "")}">生成草案</button>`);
  }
  if (report.can_remove) {
    buttons.push(`<button type="button" data-runner-session-remove="${escapeHtml(report.profile_id || "")}">移除草案</button>`);
  }
  return buttons.join("");
}

function renderExecutionRequests(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  return `
    <div class="execution-requests">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("已准备", summary.prepared_count)}
        ${metric("二次确认", summary.second_confirmed_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "执行请求状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="execution-request-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="execution-request-state ${escapeHtml(report.request?.status || "none")}">
              <span>${escapeHtml(executionRequestLabel(report.request))}</span>
              ${executionRequestButtons(report)}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无执行请求草案。</div>`}
      </div>
    </div>
  `;
}

function executionRequestLabel(request = {}) {
  if (request.status === "second_confirmed") {
    return `已二次确认 ${request.second_confirmed_at || ""}`;
  }
  if (request.status === "prepared") {
    return `草案已准备 ${request.created_at || ""}`;
  }
  if (request.status === "stale") {
    return "草案已失效，需要重新准备";
  }
  if (request.status === "blocked") {
    return "前置条件未满足";
  }
  return "尚未准备";
}

function executionRequestButtons(report) {
  const buttons = [];
  if (report.can_prepare) {
    buttons.push(`<button type="button" data-execution-request-prepare="${escapeHtml(report.profile_id || "")}">准备草案</button>`);
  }
  if (report.can_confirm) {
    buttons.push(`<button type="button" data-execution-request-confirm="${escapeHtml(report.profile_id || "")}">二次确认</button>`);
  }
  if (report.can_revoke) {
    buttons.push(`<button type="button" data-execution-request-revoke="${escapeHtml(report.profile_id || "")}">撤销二次确认</button>`);
  }
  if (report.can_remove) {
    buttons.push(`<button type="button" data-execution-request-remove="${escapeHtml(report.profile_id || "")}">移除草案</button>`);
  }
  return buttons.join("");
}

function renderRunnerPlan(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  return `
    <div class="runner-plan">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("可设计", summary.ready_count)}
        ${metric("阻断", summary.blocked_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "Runner 设计状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="runner-plan-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="runner-plan-grid">
              ${runnerPlanGroup("隔离策略", report.isolation || [], "label")}
              ${runnerPlanGroup("生命周期", report.lifecycle || [], "state", "meaning")}
              ${runnerLogPlan(report.log_plan || {})}
              ${runnerPlanGroup("失败回收", report.failure_recovery || [], "label")}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无 runner 设计报告。</div>`}
      </div>
    </div>
  `;
}

function runnerPlanGroup(title, items, labelKey, detailKey = null) {
  return `
    <div class="runner-plan-group">
      <strong>${escapeHtml(title)}</strong>
      ${(items || []).slice(0, 7).map((item) => `
        <span>${escapeHtml(item?.[labelKey] || item?.id || "")}${detailKey ? `：${escapeHtml(item?.[detailKey] || "")}` : ""}</span>
      `).join("") || "<span>暂无</span>"}
    </div>
  `;
}

function runnerLogPlan(logPlan) {
  const entries = [
    ["运行目录", logPlan.run_directory],
    ["事件日志", logPlan.event_log],
    ["标准输出", logPlan.stdout_log],
    ["标准错误", logPlan.stderr_log],
    ["摘要文件", logPlan.summary_file],
  ];
  return `
    <div class="runner-plan-group">
      <strong>日志计划</strong>
      ${entries.map(([label, value]) => `<span>${escapeHtml(label)}：${escapeHtml(value || "")}</span>`).join("")}
    </div>
  `;
}

function renderRunExecutionGate(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  return `
    <div class="run-execution-gate">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("可确认", summary.ready_count)}
        ${metric("已最终确认", summary.confirmed_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "最终确认状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="execution-gate-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="execution-boundary">${escapeHtml(report.execution_boundary || "")}</div>
            <div class="preflight-confirmation ${escapeHtml(report.final_confirmation?.status || "none")}">
              <span>${escapeHtml(finalConfirmationLabel(report.final_confirmation))}</span>
              ${executionGateButton(report)}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无可最终确认的运行配置。</div>`}
      </div>
    </div>
  `;
}

function finalConfirmationLabel(confirmation = {}) {
  if (confirmation.status === "confirmed") {
    return `已最终确认 ${confirmation.confirmed_at || ""}`;
  }
  if (confirmation.status === "stale") {
    return "最终确认已失效，需要重新确认";
  }
  if (confirmation.status === "blocked") {
    return "前置条件未满足";
  }
  return "未最终确认";
}

function executionGateButton(report) {
  if (report.final_confirmation?.status === "confirmed") {
    return `<button type="button" data-run-execution-revoke="${escapeHtml(report.profile_id || "")}">撤销最终确认</button>`;
  }
  if (report.status !== "ready_for_final_confirmation") {
    return "";
  }
  return `<button type="button" data-run-execution-confirm="${escapeHtml(report.profile_id || "")}">确认最终意图</button>`;
}

function renderRunPreflight(payload) {
  const summary = payload.summary || {};
  const reports = payload.reports || [];
  const nextAction = payload.next_action || {};
  return `
    <div class="run-preflight">
      <div class="integration-summary">
        ${metric("保存配置", summary.saved_profile_count)}
        ${metric("报告", summary.report_count)}
        ${metric("阻断", summary.error_count)}
        ${metric("警告", summary.warning_count)}
      </div>
      <article class="integration-next">
        <strong>${escapeHtml(nextAction.title || payload.status || "预检状态")}</strong>
        <span>${escapeHtml(nextAction.action || "")}</span>
      </article>
      <div class="integration-targets">
        ${reports.map((report) => `
          <article class="preflight-report ${escapeHtml(report.status || "")}">
            <strong>${escapeHtml(report.label || report.profile_id || "运行配置")}</strong>
            <span>${escapeHtml(report.status_label || report.status || "")}</span>
            <code>${escapeHtml(report.display_command || "")}</code>
            <div class="preflight-confirmation ${escapeHtml(report.confirmation?.status || "none")}">
              <span>${escapeHtml(preflightConfirmationLabel(report.confirmation))}</span>
              ${report.status === "blocked" ? "" : preflightConfirmationButton(report)}
            </div>
            <div class="preflight-checks">
              ${(report.checks || []).map((check) => `
                <span class="${escapeHtml(check.status || "warn")}">${escapeHtml(check.title || check.key || "")}</span>
              `).join("")}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无已保存运行配置，保存草案后生成预检。</div>`}
      </div>
    </div>
  `;
}

function preflightConfirmationLabel(confirmation = {}) {
  if (confirmation.status === "confirmed") {
    return `已确认 ${confirmation.confirmed_at || ""}`;
  }
  if (confirmation.status === "stale") {
    return "确认已失效，需要重新确认";
  }
  return "未确认";
}

function preflightConfirmationButton(report) {
  if (report.confirmation?.status === "confirmed") {
    return `<button type="button" data-run-preflight-revoke="${escapeHtml(report.profile_id || "")}">撤销确认</button>`;
  }
  return `<button type="button" data-run-preflight-confirm="${escapeHtml(report.profile_id || "")}">确认预检</button>`;
}

function renderRunProfiles(payload) {
  const summary = payload.summary || {};
  const safety = payload.safety || {};
  const profiles = payload.profiles || [];
  return `
    <div class="run-profiles">
      <div class="integration-summary">
        ${metric("草案", summary.profile_count)}
        ${metric("可执行命令", summary.executable_count)}
        ${metric("手动触发", summary.manual_count)}
        ${metric("需确认", summary.requires_confirmation_count)}
      </div>
      <article class="integration-next">
        <strong>安全边界</strong>
        <span>${escapeHtml(runProfileSafetyText(safety))}</span>
      </article>
      <div class="integration-targets">
        ${profiles.slice(0, 8).map((profile) => `
          <article>
            <strong>${escapeHtml(profile.label || profile.id || "运行配置")}</strong>
            <span>${escapeHtml(profile.working_directory || "")}</span>
            <code>${escapeHtml(profile.display_command || "")}</code>
            <span>${escapeHtml((profile.notes || []).join(" "))}</span>
            <div class="onboarding-actions">
              <span class="run-profile-state ${profile.saved ? "saved" : ""}">${profile.saved ? "已保存" : "未保存"}</span>
              ${profile.saved
                ? `<button type="button" data-run-profile-remove="${escapeHtml(profile.id || "")}">取消保存</button>`
                : `<button type="button" data-run-profile-save="${escapeHtml(profile.id || "")}">保存草案</button>`}
            </div>
          </article>
        `).join("") || `<div class="empty">暂无运行配置草案。</div>`}
      </div>
    </div>
  `;
}

function runProfileSafetyText(safety) {
  if (!safety.executes_commands && safety.requires_user_confirmation && !safety.writes_user_project) {
    return "当前只生成命令草案，不执行命令，不写入用户项目；后续执行前必须由用户确认。";
  }
  return "运行配置安全状态需要复核。";
}

function renderIntegrationPlan(plan) {
  const summary = plan.summary || {};
  const targets = plan.execution_targets || [];
  const phases = plan.phases || [];
  const gates = plan.validation_gates || [];
  const nextAction = plan.next_action || {};
  return `
    <div class="integration-plan">
      <div class="integration-summary">
        ${metric("执行入口", summary.execution_target_count)}
        ${metric("计划阶段", summary.phase_count)}
        ${metric("阻断项", summary.blocker_count)}
        ${metric("覆盖率", `${Math.round(Number(summary.coverage_ratio || 0) * 100)}%`)}
      </div>
      ${nextAction.title ? `
        <article class="integration-next">
          <strong>${escapeHtml(nextAction.title)}</strong>
          <span>${escapeHtml(nextAction.action || "")}</span>
        </article>
      ` : ""}
      <div class="integration-gates">
        ${gates.map((gate) => `
          <span class="${gate.passed ? "pass" : "todo"}">${escapeHtml(gate.label || gate.id || "")}</span>
        `).join("")}
      </div>
      <div class="integration-phases">
        ${phases.map((phase) => `
          <article class="${escapeHtml(phase.status || "todo")}">
            <div>
              <strong>${escapeHtml(phase.title || phase.id || "")}</strong>
              <span>${escapeHtml(phase.goal || "")}</span>
            </div>
            <ol>
              ${(phase.actions || []).slice(0, 4).map((action) => `<li>${escapeHtml(action)}</li>`).join("")}
            </ol>
          </article>
        `).join("")}
      </div>
      ${targets.length ? `
        <div class="integration-targets">
          ${targets.slice(0, 8).map((target) => `
            <article>
              <strong>${escapeHtml(target.label || target.id || "")}</strong>
              <span>${escapeHtml([target.file, target.line].filter(Boolean).join(":"))}</span>
              <code>${escapeHtml(target.run_hint || "")}</code>
            </article>
          `).join("")}
        </div>
      ` : ""}
    </div>
  `;
}

function section(title, bodyHtml) {
  const node = document.createElement("section");
  node.className = "onboarding-section";
  const key = sectionKey(title);
  const stored = readSectionCollapseState()[key];
  const isCollapsed = typeof stored === "boolean" ? stored : sectionCollapsedByDefault(title);
  node.dataset.sectionKey = key;
  node.classList.toggle("collapsed", isCollapsed);
  node.innerHTML = `
    <button type="button" class="onboarding-section-toggle" aria-expanded="${isCollapsed ? "false" : "true"}">
      <span>${escapeHtml(title)}</span>
      <small>${isCollapsed ? "Open" : "Close"}</small>
    </button>
    <div class="onboarding-section-body" ${isCollapsed ? "hidden" : ""}>${bodyHtml}</div>
  `;
  const toggle = node.querySelector(".onboarding-section-toggle");
  const body = node.querySelector(".onboarding-section-body");
  toggle?.addEventListener("click", () => {
    const nextCollapsed = !node.classList.contains("collapsed");
    node.classList.toggle("collapsed", nextCollapsed);
    if (body) {
      body.hidden = nextCollapsed;
    }
    toggle.setAttribute("aria-expanded", nextCollapsed ? "false" : "true");
    const label = toggle.querySelector("small");
    if (label) {
      label.textContent = nextCollapsed ? "Open" : "Close";
    }
    writeSectionCollapseState(key, nextCollapsed);
  });
  return node;
}

function sectionCollapsedByDefault(title) {
  return title.startsWith("Runner") || title.includes("执行请求") || title.includes("启动前") || title.includes("Dry-run") || title.includes("接入建议");
}

function sectionKey(title) {
  return title.toLowerCase().replace(/\s+/g, "-");
}

function readSectionCollapseState() {
  try {
    return JSON.parse(localStorage.getItem(SECTION_COLLAPSE_STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function writeSectionCollapseState(key, value) {
  try {
    const state = readSectionCollapseState();
    state[key] = value;
    localStorage.setItem(SECTION_COLLAPSE_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Collapse state is only a local UI preference.
  }
}

function metric(label, value) {
  return `
    <div class="onboarding-metric">
      <strong>${escapeHtml(value ?? 0)}</strong>
      <span>${escapeHtml(label)}</span>
    </div>
  `;
}

function renderReadiness(readiness) {
  const summary = readiness.summary || {};
  const checks = readiness.checks || [];
  const actions = readiness.next_actions || [];
  const risks = readiness.risk_edges || [];
  const status = readiness.status || "unknown";
  return `
    <div class="readiness-hero ${escapeHtml(status)}">
      <div>
        <strong>${escapeHtml(readiness.status_label || status)}</strong>
        <span>当前项目接入判断</span>
      </div>
      <div class="readiness-score">
        <strong>${escapeHtml(summary.covered_method_count || 0)}/${escapeHtml(summary.known_method_count || 0)}</strong>
        <span>方法覆盖</span>
      </div>
      <div class="readiness-score">
        <strong>${escapeHtml(summary.missing_contract_count || 0)}</strong>
        <span>缺契约</span>
      </div>
      <div class="readiness-score">
        <strong>${escapeHtml(summary.error_count || 0)}/${escapeHtml(summary.warning_count || 0)}</strong>
        <span>错误/警告</span>
      </div>
    </div>
    <div class="readiness-checks">
      ${checks.map(renderCheck).join("")}
    </div>
    ${actions.length ? `
      <div class="readiness-actions">
        ${actions.slice(0, 5).map((item) => `
          <article>
            <strong>${escapeHtml(item.title)}</strong>
            <span>${escapeHtml(item.action)}</span>
          </article>
        `).join("")}
      </div>
    ` : ""}
    ${risks.length ? `
      <div class="readiness-risks">
        ${risks.slice(0, 6).map((item) => `
          <article class="${escapeHtml(item.severity || "warn")}">
            <strong>${escapeHtml(item.title || item.kind || "风险")}</strong>
            <span>${escapeHtml([item.node, item.edge, item.message].filter(Boolean).join(" · "))}</span>
          </article>
        `).join("")}
      </div>
    ` : ""}
  `;
}

function renderCheck(check) {
  const status = check.status || "warn";
  return `
    <article class="readiness-check ${escapeHtml(status)}">
      <strong>${escapeHtml(check.title || check.key || "检查项")}</strong>
      <span>${escapeHtml(CHECK_LABELS[status] || status)} · ${escapeHtml(check.detail || "")}</span>
    </article>
  `;
}

function renderAudit(audit) {
  const summary = audit.summary || {};
  const findings = audit.findings || [];
  const actions = audit.next_actions || [];
  return `
    <div class="audit-summary ${escapeHtml(audit.status || "warn")}">
      <strong>${escapeHtml(AUDIT_LABELS[audit.status] || audit.status || "未知")}</strong>
      <span>问题 ${escapeHtml(summary.finding_count || 0)} · 严重 ${escapeHtml(summary.critical_count || 0)} · 错误 ${escapeHtml(summary.error_count || 0)} · 警告 ${escapeHtml(summary.warning_count || 0)}</span>
    </div>
    ${findings.length ? `
      <div class="audit-list">
        ${findings.slice(0, 12).map(renderFinding).join("")}
      </div>
    ` : `<div class="empty">自动审查未发现问题。</div>`}
    ${actions.length ? `
      <div class="audit-actions">
        ${actions.slice(0, 5).map((item) => `
          <article>
            <strong>${escapeHtml(item.title)}</strong>
            <span>${escapeHtml(item.target)} · ${escapeHtml(item.action)}</span>
          </article>
        `).join("")}
      </div>
    ` : ""}
  `;
}

function renderFinding(item) {
  return `
    <button type="button" class="audit-finding ${escapeHtml(item.severity || "warning")}" data-audit-finding="${escapeHtml(item.id || "")}">
      <div class="audit-finding-head">
        <strong>${escapeHtml(item.title || "审查问题")}</strong>
        <span>${escapeHtml(FINDING_LABELS[item.severity] || item.severity || "未知")} · ${escapeHtml(item.layer || "Analysis")}</span>
      </div>
      <div class="audit-target">${escapeHtml(item.target || "")}</div>
      <p>${escapeHtml(item.detail || "")}</p>
      <p>${escapeHtml(item.action || "")}</p>
    </button>
  `;
}

function renderSteps(steps) {
  if (!steps.length) {
    return `<div class="empty">暂无推荐步骤。</div>`;
  }
  return `<ol class="onboarding-steps">${steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>`;
}

function renderSuggestions(suggestions, getStatus) {
  if (!suggestions.length) {
    return `<div class="empty">当前项目暂无接入建议。</div>`;
  }
  return `<div class="onboarding-list">${suggestions.map((item) => renderSuggestion(item, getStatus(item))).join("")}</div>`;
}

function renderSuggestion(item, status) {
  const fileLine = [item.file, item.line].filter(Boolean).join(":");
  const suggestionId = item.id || `${item.kind || "unknown"}:${item.target || "unknown"}`;
  return `
    <article class="onboarding-card ${escapeHtml(item.priority || "medium")} ${escapeHtml(status)}">
      <div class="onboarding-card-title">
        <strong>${escapeHtml(item.title || "接入建议")}</strong>
        <span>${escapeHtml(PRIORITY_LABELS[item.priority] || item.priority || "未知")} · ${escapeHtml(STATUS_LABELS[status] || status)}</span>
      </div>
      <div class="onboarding-meta">
        <span>${escapeHtml(KIND_LABELS[item.kind] || item.kind || "未知类型")}</span>
        <span>${escapeHtml(item.target || "未知目标")}</span>
        ${fileLine ? `<span>${escapeHtml(fileLine)}</span>` : ""}
      </div>
      <p>${escapeHtml(item.reason || "")}</p>
      <p>${escapeHtml(item.action || "")}</p>
      <div class="onboarding-actions">
        ${statusButton(suggestionId, "pending", status)}
        ${statusButton(suggestionId, "done", status)}
        ${statusButton(suggestionId, "ignored", status)}
        ${item.code ? `<button type="button" data-onboarding-copy="${escapeHtml(suggestionId)}">复制片段</button>` : ""}
      </div>
      ${item.code ? `<pre class="code-block onboarding-code">${escapeHtml(item.code)}</pre>` : ""}
    </article>
  `;
}

function statusButton(suggestionId, status, activeStatus) {
  return `
    <button
      type="button"
      data-onboarding-status="${escapeHtml(status)}"
      data-suggestion-id="${escapeHtml(suggestionId)}"
      class="${status === activeStatus ? "active" : ""}"
    >${escapeHtml(STATUS_LABELS[status])}</button>
  `;
}

function installSuggestionActions(container, suggestions, onSetStatus) {
  const suggestionById = new Map(suggestions.map((item) => [item.id || `${item.kind || "unknown"}:${item.target || "unknown"}`, item]));
  for (const button of container.querySelectorAll("[data-onboarding-status]")) {
    button.addEventListener("click", () => {
      const suggestion = suggestionById.get(button.dataset.suggestionId);
      if (suggestion) {
        onSetStatus(suggestion, button.dataset.onboardingStatus || "pending");
      }
    });
  }
  for (const button of container.querySelectorAll("[data-onboarding-copy]")) {
    button.addEventListener("click", async () => {
      const suggestion = suggestionById.get(button.dataset.onboardingCopy);
      if (!suggestion?.code) {
        return;
      }
      try {
        await copyText(suggestion.code);
        button.textContent = "已复制";
      } catch {
        button.textContent = "复制失败";
      }
      window.setTimeout(() => {
        button.textContent = "复制片段";
      }, 1200);
    });
  }
}

function installAuditActions(container, audit, onSelectFinding) {
  const findings = audit?.findings || [];
  const findingById = new Map(findings.map((item) => [item.id, item]));
  for (const button of container.querySelectorAll("[data-audit-finding]")) {
    button.addEventListener("click", () => {
      const finding = findingById.get(button.dataset.auditFinding);
      if (finding) {
        onSelectFinding(finding);
      }
    });
  }
}

function installRunProfileActions(container, runProfiles, onSaveRunProfile, onRemoveRunProfile) {
  const profiles = runProfiles?.profiles || [];
  const profileById = new Map(profiles.map((item) => [item.id, item]));
  for (const button of container.querySelectorAll("[data-run-profile-save]")) {
    button.addEventListener("click", async () => {
      const profile = profileById.get(button.dataset.runProfileSave);
      if (!profile) {
        return;
      }
      button.disabled = true;
      button.textContent = "保存中";
      try {
        await onSaveRunProfile(profile);
      } catch {
        button.disabled = false;
        button.textContent = "保存失败";
      }
    });
  }
  for (const button of container.querySelectorAll("[data-run-profile-remove]")) {
    button.addEventListener("click", async () => {
      const profile = profileById.get(button.dataset.runProfileRemove);
      if (!profile) {
        return;
      }
      button.disabled = true;
      button.textContent = "移除中";
      try {
        await onRemoveRunProfile(profile);
      } catch {
        button.disabled = false;
        button.textContent = "移除失败";
      }
    });
  }
}

function installRunPreflightActions(container, runPreflight, onConfirmRunPreflight, onRevokeRunPreflight) {
  const reports = runPreflight?.reports || [];
  const reportByProfileId = new Map(reports.map((item) => [item.profile_id, item]));
  for (const button of container.querySelectorAll("[data-run-preflight-confirm]")) {
    button.addEventListener("click", async () => {
      const report = reportByProfileId.get(button.dataset.runPreflightConfirm);
      if (!report) {
        return;
      }
      button.disabled = true;
      button.textContent = "确认中";
      try {
        await onConfirmRunPreflight(report);
      } catch {
        button.disabled = false;
        button.textContent = "确认失败";
      }
    });
  }
  for (const button of container.querySelectorAll("[data-run-preflight-revoke]")) {
    button.addEventListener("click", async () => {
      const report = reportByProfileId.get(button.dataset.runPreflightRevoke);
      if (!report) {
        return;
      }
      button.disabled = true;
      button.textContent = "撤销中";
      try {
        await onRevokeRunPreflight(report);
      } catch {
        button.disabled = false;
        button.textContent = "撤销失败";
      }
    });
  }
}

function installRunExecutionGateActions(container, runExecutionGate, onConfirmRunExecutionGate, onRevokeRunExecutionGate) {
  const reports = runExecutionGate?.reports || [];
  const reportByProfileId = new Map(reports.map((item) => [item.profile_id, item]));
  for (const button of container.querySelectorAll("[data-run-execution-confirm]")) {
    button.addEventListener("click", async () => {
      const report = reportByProfileId.get(button.dataset.runExecutionConfirm);
      if (!report) {
        return;
      }
      button.disabled = true;
      button.textContent = "确认中";
      try {
        await onConfirmRunExecutionGate(report);
      } catch {
        button.disabled = false;
        button.textContent = "确认失败";
      }
    });
  }
  for (const button of container.querySelectorAll("[data-run-execution-revoke]")) {
    button.addEventListener("click", async () => {
      const report = reportByProfileId.get(button.dataset.runExecutionRevoke);
      if (!report) {
        return;
      }
      button.disabled = true;
      button.textContent = "撤销中";
      try {
        await onRevokeRunExecutionGate(report);
      } catch {
        button.disabled = false;
        button.textContent = "撤销失败";
      }
    });
  }
}

function installExecutionRequestActions(
  container,
  executionRequests,
  onPrepareExecutionRequest,
  onConfirmExecutionRequest,
  onRevokeExecutionRequest,
  onRemoveExecutionRequest,
) {
  const reports = executionRequests?.reports || [];
  const reportByProfileId = new Map(reports.map((item) => [item.profile_id, item]));
  const actions = [
    ["[data-execution-request-prepare]", "executionRequestPrepare", "准备中", "准备失败", onPrepareExecutionRequest],
    ["[data-execution-request-confirm]", "executionRequestConfirm", "确认中", "确认失败", onConfirmExecutionRequest],
    ["[data-execution-request-revoke]", "executionRequestRevoke", "撤销中", "撤销失败", onRevokeExecutionRequest],
    ["[data-execution-request-remove]", "executionRequestRemove", "移除中", "移除失败", onRemoveExecutionRequest],
  ];
  for (const [selector, datasetKey, pendingText, failedText, handler] of actions) {
    for (const button of container.querySelectorAll(selector)) {
      button.addEventListener("click", async () => {
        const report = reportByProfileId.get(button.dataset[datasetKey]);
        if (!report) {
          return;
        }
        button.disabled = true;
        button.textContent = pendingText;
        try {
          await handler(report);
        } catch {
          button.disabled = false;
          button.textContent = failedText;
        }
      });
    }
  }
}

function installRunnerSessionActions(container, runnerSessions, onPrepareRunnerSession, onRemoveRunnerSession) {
  const reports = runnerSessions?.reports || [];
  const reportByProfileId = new Map(reports.map((item) => [item.profile_id, item]));
  const actions = [
    ["[data-runner-session-prepare]", "runnerSessionPrepare", "生成中", "生成失败", onPrepareRunnerSession],
    ["[data-runner-session-remove]", "runnerSessionRemove", "移除中", "移除失败", onRemoveRunnerSession],
  ];
  for (const [selector, datasetKey, pendingText, failedText, handler] of actions) {
    for (const button of container.querySelectorAll(selector)) {
      button.addEventListener("click", async () => {
        const report = reportByProfileId.get(button.dataset[datasetKey]);
        if (!report) {
          return;
        }
        button.disabled = true;
        button.textContent = pendingText;
        try {
          await handler(report);
        } catch {
          button.disabled = false;
          button.textContent = failedText;
        }
      });
    }
  }
}

function installRunnerLaunchSnapshotActions(
  container,
  runnerLaunchSnapshots,
  onPrepareRunnerLaunchSnapshot,
  onRemoveRunnerLaunchSnapshot,
) {
  const reports = runnerLaunchSnapshots?.reports || [];
  const reportByProfileId = new Map(reports.map((item) => [item.profile_id, item]));
  const actions = [
    [
      "[data-runner-launch-snapshot-prepare]",
      "runnerLaunchSnapshotPrepare",
      "生成中",
      "生成失败",
      onPrepareRunnerLaunchSnapshot,
    ],
    [
      "[data-runner-launch-snapshot-remove]",
      "runnerLaunchSnapshotRemove",
      "移除中",
      "移除失败",
      onRemoveRunnerLaunchSnapshot,
    ],
  ];
  for (const [selector, datasetKey, pendingText, failedText, handler] of actions) {
    for (const button of container.querySelectorAll(selector)) {
      button.addEventListener("click", async () => {
        const report = reportByProfileId.get(button.dataset[datasetKey]);
        if (!report) {
          return;
        }
        button.disabled = true;
        button.textContent = pendingText;
        try {
          await handler(report);
        } catch {
          button.disabled = false;
          button.textContent = failedText;
        }
      });
    }
  }
}

function installRunnerDryRunActions(container, runnerDryRuns, onPrepareRunnerDryRun, onRemoveRunnerDryRun) {
  const reports = runnerDryRuns?.reports || [];
  const reportByProfileId = new Map(reports.map((item) => [item.profile_id, item]));
  const actions = [
    ["[data-runner-dry-run-prepare]", "runnerDryRunPrepare", "生成中", "生成失败", onPrepareRunnerDryRun],
    ["[data-runner-dry-run-remove]", "runnerDryRunRemove", "移除中", "移除失败", onRemoveRunnerDryRun],
  ];
  for (const [selector, datasetKey, pendingText, failedText, handler] of actions) {
    for (const button of container.querySelectorAll(selector)) {
      button.addEventListener("click", async () => {
        const report = reportByProfileId.get(button.dataset[datasetKey]);
        if (!report) {
          return;
        }
        button.disabled = true;
        button.textContent = pendingText;
        try {
          await handler(report);
        } catch {
          button.disabled = false;
          button.textContent = failedText;
        }
      });
    }
  }
}

function summarizeStatuses(suggestions, getStatus) {
  return suggestions.reduce(
    (summary, suggestion) => {
      const status = getStatus(suggestion);
      summary[status] = (summary[status] || 0) + 1;
      return summary;
    },
    { pending: 0, done: 0, ignored: 0 },
  );
}

async function copyText(value) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}
