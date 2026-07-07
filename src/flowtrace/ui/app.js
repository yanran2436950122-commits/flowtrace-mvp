// 模块：应用入口。负责装配数据加载、视图切换、监视窗口与 UI 组件。
import {
  getProjectAudit,
  getRunComparison,
  getRunDataflow,
  getRunEvents,
  getRunIssues,
  getRunLayers,
  getProject,
  getProjectCoverage,
  getProjectOnboarding,
  getProjectReadiness,
  getProjectIntegrationPlan,
  getProjectRunProfiles,
  getProjectRunPreflight,
  getProjectRunExecutionGate,
  getProjectRunnerPlan,
  getProjectExecutionRequests,
  getProjectRunnerSessions,
  getProjectRunnerLaunchSnapshots,
  getProjectRunnerDryRuns,
  getProjectRunnerRealExecutions,
  getProjectRunnerCancelTimeoutRealApis,
  getProjectRunnerFirstRealTests,
  getProjectRunnerProcessLifecycles,
  getProjectRunnerStreamCaptures,
  getProjectRunnerEventWriters,
  getProjectRunnerAuditPersistences,
  getProjectRunnerAuditIntegrityReplayVerifications,
  getProjectRunnerVerificationDiscrepancyReports,
  getProjectRunnerLaunchControls,
  getProjectRunnerRuntimePolicies,
  getProjectRunnerExecutionConfigs,
  getProjectRunnerExecutionConfigChecks,
  getProjectRunnerConfigSchemaStabilizations,
  getProjectRunnerConfigFieldContractViews,
  getProjectRunnerConfigCompatibilityReports,
  getProjectRunnerConfigRemediationSummaries,
  getProjectRunnerConfigFieldCoverageIndexes,
  getProjectRunnerServiceFlagAudits,
  getProjectRunnerLogDirectoryPolicies,
  getProjectRunnerLogRetentionPolicies,
  getProjectRunnerLogCleanupPreviews,
  getProjectRunnerLogCleanupConfirmations,
  getProjectRunnerLogCleanupAuditTrails,
  getProjectRunnerLogCleanupExecutionPlans,
  getProjectRunnerGovernanceReadiness,
  getProjectRunnerExecutionAdapterContracts,
  getProjectRunnerLaunchApiContracts,
  getProjectRunnerExecutionAdapterReviews,
  getProjectRunnerFinalBlockMatrices,
  getProjectRunnerAuthorizationUnlockAudits,
  getProjectRunnerImplementationGapChecklists,
  getProjectRunnerCancelTimeoutContracts,
  getProjectRunnerSessionStateSchemas,
  getProjectRunnerRealTestReadiness,
  getProjectRunnerRealTestAuthorizationChecklists,
  getProjectRunnerRealTestAuthorizationPackages,
  getProjectRunnerRealTestSandboxPolicies,
  getProjectRunnerRealTestFinalChecklists,
  getProjectRunnerRealTestUiPreviews,
  getProjectRunnerRealExecutionStageBoundaryReviews,
  getProjectRunnerRealExecutionUnlockMaterialReviews,
  getProjectRunnerRealExecutionImplementationPlans,
  getProjectRunnerRealExecutionScopeDiffAudits,
  getProjectRunnerExecutionAdapterImplementationAudits,
  getProjectRunnerProcessLifecycleImplementationAudits,
  getProjectRunnerStreamCaptureImplementationAudits,
  getProjectRunnerEventWriterImplementationAudits,
  getProjectRunnerAuditPersistenceImplementationAudits,
  getProjectRunnerAuditIntegrityReplayVerificationAudits,
  getProjectRunnerVerificationDiscrepancyReportAudits,
  getProjectRunnerRealLaunchFinalGateAudits,
  getProjectRunnerEvidenceGapIndexes,
  getProjectRunnerDevelopmentPathAnchors,
  getProjectRunnerRealExecutionTouchpointInventories,
  getProjectRunnerRealExecutionTouchpointCoverageIndexes,
  getProjectRunnerRealExecutionTouchpointGapLinks,
  getProjectRunnerRealExecutionTouchpointUnlockMatrices,
  getProjectRunnerRealExecutionUnlockPhraseReadiness,
  getProjectRunnerRealExecutionPreUnlockEvidencePacketIndexes,
  getProjectRunnerRealExecutionPreUnlockReviewChecklists,
  getProjectRunnerRealExecutionPreUnlockReviewerRoleMaps,
  getProjectRunnerRealExecutionPreUnlockReviewerSignoffRubrics,
  getProjectRunnerRealExecutionPreUnlockSignoffEvidenceBindings,
  getProjectRunnerRealExecutionPreUnlockImplementationEntryReadinessLedgers,
  getProjectRunnerRealExecutionPreUnlockRound10MinimalScopePreviews,
  getProjectRunnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts,
  getProjectRunnerRealExecutionPreRound10LockedHandoffSummaries,
  getProjectRunnerRealExecutionRound10ExplicitUnlockCheckpoints,
  getProjectRunnerRealExecutionRound10UnlockDecisionMirrors,
  getProjectBootstrap,
  getRuns,
  getRunSummary,
  confirmRunExecutionGate,
  confirmExecutionRequest,
  confirmRunPreflight,
  openPathDialog,
  prepareExecutionRequest,
  prepareRunnerSession,
  prepareRunnerLaunchSnapshot,
  prepareRunnerDryRun,
  removeProjectRunProfile,
  removeExecutionRequest,
  removeRunnerSession,
  removeRunnerLaunchSnapshot,
  removeRunnerDryRun,
  revokeRunExecutionGate,
  revokeExecutionRequest,
  revokeRunPreflight,
  saveProjectRunProfile,
  setProjectContext,
} from "./modules/api.js";
import { renderComparison } from "./modules/components/comparison.js";
import { renderDataflow } from "./modules/components/dataflow.js";
import { renderAuditFindingDetail, renderDetails, renderEdgeComparison } from "./modules/components/details.js";
import { renderEvents } from "./modules/components/events.js";
import { renderExpandedDataflow } from "./modules/components/expanded-dataflow.js";
import { renderIssues } from "./modules/components/issues.js";
import { renderLayerFlow } from "./modules/components/layers.js";
import { renderOnboarding } from "./modules/components/onboarding.js";
import { renderProject } from "./modules/components/project.js";
import { renderRuns } from "./modules/components/runs.js";
import { renderRunnerWorkbench } from "./modules/components/runner-workbench.js";
import { renderSummary } from "./modules/components/summary.js";
import { methodToWatchItem, renderWatchPanel } from "./modules/components/watch.js";
import { installWorkspaceWindows } from "./modules/layout/workspace-windows.js";
import {
  addWatchItem,
  createState,
  getOnboardingSuggestionStatus,
  getWatchItemScroll,
  getWatchItemSnapshot,
  isWatchItemFrozen,
  isWatchItemOpen,
  persistNodePositions,
  removeWatchItem,
  setWatchItemFrozen,
  setWatchItemScroll,
  setWatchItemOpen,
  setOnboardingSuggestionStatus,
} from "./modules/state.js";
import { escapeHtml } from "./modules/utils/html.js";

const WATCH_REFRESH_MS = 3000;
const state = createState();
const mainViews = createMainViewPanels();
let latestOnboarding = null;
let latestReadiness = null;
let latestAudit = null;
let latestIntegrationPlan = null;
let latestRunProfiles = null;
let latestRunPreflight = null;
let latestRunExecutionGate = null;
let latestRunnerPlan = null;
let latestExecutionRequests = null;
let latestRunnerSessions = null;
let latestRunnerLaunchSnapshots = null;
let latestRunnerDryRuns = null;
let latestRunnerRealExecutions = null;
let latestRunnerCancelTimeoutRealApis = null;
let latestRunnerFirstRealTests = null;
let latestRunnerProcessLifecycles = null;
let latestRunnerStreamCaptures = null;
let latestRunnerEventWriters = null;
let latestRunnerAuditPersistences = null;
let latestRunnerAuditIntegrityReplayVerifications = null;
let latestRunnerVerificationDiscrepancyReports = null;
let latestRunnerLaunchControls = null;
let latestRunnerRuntimePolicies = null;
let latestRunnerExecutionConfigs = null;
let latestRunnerExecutionConfigChecks = null;
let latestRunnerConfigSchemaStabilizations = null;
let latestRunnerConfigFieldContractViews = null;
let latestRunnerConfigCompatibilityReports = null;
let latestRunnerConfigRemediationSummaries = null;
let latestRunnerConfigFieldCoverageIndexes = null;
let latestRunnerServiceFlagAudits = null;
let latestRunnerLogDirectoryPolicies = null;
let latestRunnerLogRetentionPolicies = null;
let latestRunnerLogCleanupPreviews = null;
let latestRunnerLogCleanupConfirmations = null;
let latestRunnerLogCleanupAuditTrails = null;
let latestRunnerLogCleanupExecutionPlans = null;
let latestRunnerGovernanceReadiness = null;
let latestRunnerExecutionAdapterContracts = null;
let latestRunnerLaunchApiContracts = null;
let latestRunnerExecutionAdapterReviews = null;
let latestRunnerFinalBlockMatrices = null;
let latestRunnerAuthorizationUnlockAudits = null;
let latestRunnerImplementationGapChecklists = null;
let latestRunnerCancelTimeoutContracts = null;
let latestRunnerSessionStateSchemas = null;
let latestRunnerRealTestReadiness = null;
let latestRunnerRealTestAuthorizationChecklists = null;
let latestRunnerRealTestAuthorizationPackages = null;
let latestRunnerRealTestSandboxPolicies = null;
let latestRunnerRealTestFinalChecklists = null;
let latestRunnerRealTestUiPreviews = null;
let latestRunnerRealExecutionStageBoundaryReviews = null;
let latestRunnerRealExecutionUnlockMaterialReviews = null;
let latestRunnerRealExecutionImplementationPlans = null;
let latestRunnerRealExecutionScopeDiffAudits = null;
let latestRunnerExecutionAdapterImplementationAudits = null;
let latestRunnerProcessLifecycleImplementationAudits = null;
let latestRunnerStreamCaptureImplementationAudits = null;
let latestRunnerEventWriterImplementationAudits = null;
let latestRunnerAuditPersistenceImplementationAudits = null;
let latestRunnerAuditIntegrityReplayVerificationAudits = null;
let latestRunnerVerificationDiscrepancyReportAudits = null;
let latestRunnerRealLaunchFinalGateAudits = null;
let latestRunnerEvidenceGapIndexes = null;
let latestRunnerDevelopmentPathAnchors = null;
let latestRunnerRealExecutionTouchpointInventories = null;
let latestRunnerRealExecutionTouchpointCoverageIndexes = null;
let latestRunnerRealExecutionTouchpointGapLinks = null;
let latestRunnerRealExecutionTouchpointUnlockMatrices = null;
let latestRunnerRealExecutionUnlockPhraseReadiness = null;
let latestRunnerRealExecutionPreUnlockEvidencePacketIndexes = null;
let latestRunnerRealExecutionPreUnlockReviewChecklists = null;
let latestRunnerRealExecutionPreUnlockReviewerRoleMaps = null;
let latestRunnerRealExecutionPreUnlockReviewerSignoffRubrics = null;
let latestRunnerRealExecutionPreUnlockSignoffEvidenceBindings = null;
let latestRunnerRealExecutionPreUnlockImplementationEntryReadinessLedgers = null;
let latestRunnerRealExecutionPreUnlockRound10MinimalScopePreviews = null;
let latestRunnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts = null;
let latestRunnerRealExecutionPreRound10LockedHandoffSummaries = null;
let latestRunnerRealExecutionRound10ExplicitUnlockCheckpoints = null;
let latestRunnerRealExecutionRound10UnlockDecisionMirrors = null;

const elements = {
  content: document.querySelector(".content"),
  runs: document.getElementById("runs"),
  details: document.getElementById("details"),
  runTitle: document.getElementById("runTitle"),
  runMeta: document.getElementById("runMeta"),
  runSummary: document.getElementById("runSummary"),
  watchList: document.getElementById("watchList"),
  watchStatus: document.getElementById("watchStatus"),
  refreshButton: document.getElementById("refreshRuns"),
};

installWorkspaceWindows(elements.content, [
  ...Object.values(mainViews).map((view) => ({ id: view.id, title: view.title, element: view.panel })),
  { id: "watch", title: "监视窗口", element: document.querySelector(".watch-panel") },
  { id: "details", title: "事件详情", element: document.querySelector(".detail-panel") },
]);

elements.refreshButton.addEventListener("click", loadRuns);
document.addEventListener("flowtrace:runner-stage-target", (event) => {
  const runnerTab = document.querySelector('.workspace-pane-tab[data-panel-id="runner"]');
  runnerTab?.click();
  window.requestAnimationFrame(() => {
    window.flowtraceOpenRunnerStageTarget?.(event.detail || {});
  });
});
renderWatch();

function createMainViewPanels() {
  const existingPanel = document.querySelector(".graph-panel");
  const existingGraph = existingPanel.querySelector("#graph");
  existingPanel.classList.add("main-view-panel");
  existingPanel.querySelector(".panel-heading")?.remove();
  existingGraph.id = "graph-layers";
  existingGraph.dataset.viewContainer = "layers";

  const definitions = [
    { id: "project", title: "项目结构" },
    { id: "runner", title: "Runner 工作台" },
    { id: "onboarding", title: "接入向导" },
    { id: "layers", title: "层级流转", panel: existingPanel, container: existingGraph },
    { id: "dataflow", title: "方法数据流" },
    { id: "expanded", title: "全量细节" },
    { id: "issues", title: "问题列表" },
    { id: "compare", title: "运行对比" },
    { id: "events", title: "事件流程" },
  ];

  return Object.fromEntries(definitions.map((definition) => {
    const panel = definition.panel || createGraphPanel(definition.title, definition.id);
    const container = definition.container || panel.querySelector("[data-view-container]");
    return [definition.id, { ...definition, panel, container }];
  }));
}

function createGraphPanel(title, viewId) {
  const panel = document.createElement("div");
  panel.className = "graph-panel main-view-panel";
  panel.innerHTML = `
    <div class="graph empty" data-view-container="${viewId}">暂无数据。</div>
  `;
  return panel;
}

async function loadRuns() {
  if (!elements.runs.children.length) {
    elements.runs.innerHTML = `<div class="empty">正在加载运行记录...</div>`;
  }
  const runs = await getRuns();
  if (!runs.length) {
    elements.runs.innerHTML = `<div class="empty">暂无运行记录。</div>`;
    elements.runSummary.innerHTML = "";
    renderWatch();
    await renderMainViews();
    return;
  }

  renderRuns(elements.runs, runs, state.activeRunId, loadRun);
  if (!state.activeRunId && runs[0]) {
    await loadRun(runs[0]);
  }
}

async function loadRun(run) {
  state.activeRunId = run.run_id;
  state.activeRunRecord = run;
  elements.runTitle.textContent = run.label || run.run_id;
  const projectionLabel = run.source === "external_runtime" ? " - 外部 runtime 投影" : "";
  elements.runMeta.textContent = `${run.event_count} 条事件 - ${run.started_at || "未知开始时间"}${projectionLabel}`;
  renderDetails(elements.details, {});
  renderRuns(elements.runs, await getRuns(), state.activeRunId, loadRun);
  if (run.source === "external_runtime") {
    renderExternalRuntimeSummary(elements.runSummary, run);
    state.latestLayerFlow = { nodes: [], edges: [] };
    renderWatch();
    await renderExternalRuntimeRunViews(run);
    return;
  } else {
    await refreshSummary();
    await refreshWatchData();
  }
  await renderMainViews();
}

async function refreshSummary() {
  if (!state.activeRunId) {
    elements.runSummary.innerHTML = "";
    return;
  }
  const summary = await getRunSummary(state.activeRunId);
  renderSummary(elements.runSummary, summary);
}

async function refreshWatchData() {
  if (!state.activeRunId) {
    renderWatch();
    return;
  }
  state.latestLayerFlow = await getRunLayers(state.activeRunId);
  renderWatch();
}

function renderWatch() {
  renderWatchPanel(
    elements.watchList,
    elements.watchStatus,
    state.watchItems,
    state.latestLayerFlow,
    (item) => {
      removeWatchItem(state, item);
      renderWatch();
    },
    (item) => {
      addWatchItem(state, item);
      renderWatch();
    },
    (item) => renderDetails(elements.details, item),
    (item) => isWatchItemOpen(state, item),
    (item, isOpen) => setWatchItemOpen(state, item, isOpen),
    (item) => getWatchItemScroll(state, item),
    (item, scrollPosition) => setWatchItemScroll(state, item, scrollPosition),
    (item) => isWatchItemFrozen(state, item),
    (item) => getWatchItemSnapshot(state, item),
    (item, isFrozen, snapshot) => {
      setWatchItemFrozen(state, item, isFrozen, snapshot);
      renderWatch();
    },
  );
}

function watchMethod(method) {
  addWatchItem(state, methodToWatchItem(method));
  renderWatch();
}

async function renderMainViews() {
  const bootstrap = await getProjectBootstrap();
  const {
    project,
    coverage,
    onboarding,
    readiness,
    audit,
    integration_plan: integrationPlan,
    run_profiles: runProfiles,
    run_preflight: runPreflight,
    run_execution_gate: runExecutionGate,
    runner_plan: runnerPlan,
    execution_requests: executionRequests,
    runner_sessions: runnerSessions,
    runner_launch_snapshots: runnerLaunchSnapshots,
    runner_dry_runs: runnerDryRuns,
    runner_real_executions: runnerRealExecutions,
    runner_cancel_timeout_real_apis: runnerCancelTimeoutRealApis,
    runner_first_real_tests: runnerFirstRealTests,
    runner_process_lifecycles: runnerProcessLifecycles,
    runner_stream_captures: runnerStreamCaptures,
    runner_event_writers: runnerEventWriters,
    runner_audit_persistences: runnerAuditPersistences,
    runner_audit_integrity_replay_verifications: runnerAuditIntegrityReplayVerifications,
    runner_verification_discrepancy_reports: runnerVerificationDiscrepancyReports,
    runner_launch_controls: runnerLaunchControls,
    runner_runtime_policies: runnerRuntimePolicies,
    runner_execution_configs: runnerExecutionConfigs,
    runner_execution_config_checks: runnerExecutionConfigChecks,
    runner_config_schema_stabilizations: runnerConfigSchemaStabilizations,
    runner_config_field_contract_views: runnerConfigFieldContractViews,
    runner_config_compatibility_reports: runnerConfigCompatibilityReports,
    runner_config_remediation_summaries: runnerConfigRemediationSummaries,
    runner_config_field_coverage_indexes: runnerConfigFieldCoverageIndexes,
    runner_service_flag_audits: runnerServiceFlagAudits,
    runner_log_directory_policies: runnerLogDirectoryPolicies,
    runner_log_retention_policies: runnerLogRetentionPolicies,
    runner_log_cleanup_previews: runnerLogCleanupPreviews,
    runner_log_cleanup_confirmations: runnerLogCleanupConfirmations,
    runner_log_cleanup_audit_trails: runnerLogCleanupAuditTrails,
    runner_log_cleanup_execution_plans: runnerLogCleanupExecutionPlans,
    runner_governance_readiness: runnerGovernanceReadiness,
    runner_execution_adapter_contracts: runnerExecutionAdapterContracts,
    runner_launch_api_contracts: runnerLaunchApiContracts,
    runner_execution_adapter_reviews: runnerExecutionAdapterReviews,
    runner_final_block_matrices: runnerFinalBlockMatrices,
    runner_authorization_unlock_audits: runnerAuthorizationUnlockAudits,
    runner_implementation_gap_checklists: runnerImplementationGapChecklists,
    runner_cancel_timeout_contracts: runnerCancelTimeoutContracts,
    runner_session_state_schemas: runnerSessionStateSchemas,
    runner_real_test_readiness: runnerRealTestReadiness,
    runner_real_test_authorization_checklists: runnerRealTestAuthorizationChecklists,
    runner_real_test_authorization_packages: runnerRealTestAuthorizationPackages,
    runner_real_test_sandbox_policies: runnerRealTestSandboxPolicies,
    runner_real_test_final_checklists: runnerRealTestFinalChecklists,
    runner_real_test_ui_previews: runnerRealTestUiPreviews,
    runner_real_execution_stage_boundary_reviews: runnerRealExecutionStageBoundaryReviews,
    runner_real_execution_unlock_material_reviews: runnerRealExecutionUnlockMaterialReviews,
    runner_real_execution_implementation_plans: runnerRealExecutionImplementationPlans,
    runner_real_execution_scope_diff_audits: runnerRealExecutionScopeDiffAudits,
    runner_execution_adapter_implementation_audits: runnerExecutionAdapterImplementationAudits,
    runner_process_lifecycle_implementation_audits: runnerProcessLifecycleImplementationAudits,
    runner_stream_capture_implementation_audits: runnerStreamCaptureImplementationAudits,
    runner_event_writer_implementation_audits: runnerEventWriterImplementationAudits,
    runner_audit_persistence_implementation_audits: runnerAuditPersistenceImplementationAudits,
    runner_audit_integrity_replay_verification_audits: runnerAuditIntegrityReplayVerificationAudits,
    runner_verification_discrepancy_report_audits: runnerVerificationDiscrepancyReportAudits,
    runner_real_launch_final_gate_audits: runnerRealLaunchFinalGateAudits,
    runner_evidence_gap_indexes: runnerEvidenceGapIndexes,
    runner_development_path_anchors: runnerDevelopmentPathAnchors,
    runner_real_execution_touchpoint_inventories: runnerRealExecutionTouchpointInventories,
    runner_real_execution_touchpoint_coverage_indexes: runnerRealExecutionTouchpointCoverageIndexes,
    runner_real_execution_touchpoint_gap_links: runnerRealExecutionTouchpointGapLinks,
    runner_real_execution_touchpoint_unlock_matrices: runnerRealExecutionTouchpointUnlockMatrices,
    runner_real_execution_unlock_phrase_readiness: runnerRealExecutionUnlockPhraseReadiness,
    runner_real_execution_pre_unlock_evidence_packet_indexes: runnerRealExecutionPreUnlockEvidencePacketIndexes,
    runner_real_execution_pre_unlock_review_checklists: runnerRealExecutionPreUnlockReviewChecklists,
    runner_real_execution_pre_unlock_reviewer_role_maps: runnerRealExecutionPreUnlockReviewerRoleMaps,
    runner_real_execution_pre_unlock_reviewer_signoff_rubrics:
      runnerRealExecutionPreUnlockReviewerSignoffRubrics,
    runner_real_execution_pre_unlock_signoff_evidence_bindings:
      runnerRealExecutionPreUnlockSignoffEvidenceBindings,
    runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers:
      runnerRealExecutionPreUnlockImplementationEntryReadinessLedgers,
    runner_real_execution_pre_unlock_round10_minimal_scope_previews:
      runnerRealExecutionPreUnlockRound10MinimalScopePreviews,
    runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts:
      runnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts,
    runner_real_execution_pre_round10_locked_handoff_summaries:
      runnerRealExecutionPreRound10LockedHandoffSummaries,
    runner_real_execution_round10_explicit_unlock_checkpoints:
      runnerRealExecutionRound10ExplicitUnlockCheckpoints,
    runner_real_execution_round10_unlock_decision_mirrors:
      runnerRealExecutionRound10UnlockDecisionMirrors,
  } = bootstrap;
  latestOnboarding = onboarding;
  latestReadiness = readiness;
  latestAudit = audit;
  latestIntegrationPlan = integrationPlan;
  latestRunProfiles = runProfiles;
  latestRunPreflight = runPreflight;
  latestRunExecutionGate = runExecutionGate;
  latestRunnerPlan = runnerPlan;
  latestExecutionRequests = executionRequests;
  latestRunnerSessions = runnerSessions;
  latestRunnerLaunchSnapshots = runnerLaunchSnapshots;
  latestRunnerDryRuns = runnerDryRuns;
  latestRunnerRealExecutions = runnerRealExecutions;
  latestRunnerCancelTimeoutRealApis = runnerCancelTimeoutRealApis;
  latestRunnerFirstRealTests = runnerFirstRealTests;
  latestRunnerProcessLifecycles = runnerProcessLifecycles;
  latestRunnerStreamCaptures = runnerStreamCaptures;
  latestRunnerEventWriters = runnerEventWriters;
  latestRunnerAuditPersistences = runnerAuditPersistences;
  latestRunnerAuditIntegrityReplayVerifications = runnerAuditIntegrityReplayVerifications;
  latestRunnerVerificationDiscrepancyReports = runnerVerificationDiscrepancyReports;
  latestRunnerLaunchControls = runnerLaunchControls;
  latestRunnerRuntimePolicies = runnerRuntimePolicies;
  latestRunnerExecutionConfigs = runnerExecutionConfigs;
  latestRunnerExecutionConfigChecks = runnerExecutionConfigChecks;
  latestRunnerConfigSchemaStabilizations = runnerConfigSchemaStabilizations;
  latestRunnerConfigFieldContractViews = runnerConfigFieldContractViews;
  latestRunnerConfigCompatibilityReports = runnerConfigCompatibilityReports;
  latestRunnerConfigRemediationSummaries = runnerConfigRemediationSummaries;
  latestRunnerConfigFieldCoverageIndexes = runnerConfigFieldCoverageIndexes;
  latestRunnerServiceFlagAudits = runnerServiceFlagAudits;
  latestRunnerLogDirectoryPolicies = runnerLogDirectoryPolicies;
  latestRunnerLogRetentionPolicies = runnerLogRetentionPolicies;
  latestRunnerLogCleanupPreviews = runnerLogCleanupPreviews;
  latestRunnerLogCleanupConfirmations = runnerLogCleanupConfirmations;
  latestRunnerLogCleanupAuditTrails = runnerLogCleanupAuditTrails;
  latestRunnerLogCleanupExecutionPlans = runnerLogCleanupExecutionPlans;
  latestRunnerGovernanceReadiness = runnerGovernanceReadiness;
  latestRunnerExecutionAdapterContracts = runnerExecutionAdapterContracts;
  latestRunnerLaunchApiContracts = runnerLaunchApiContracts;
  latestRunnerExecutionAdapterReviews = runnerExecutionAdapterReviews;
  latestRunnerFinalBlockMatrices = runnerFinalBlockMatrices;
  latestRunnerAuthorizationUnlockAudits = runnerAuthorizationUnlockAudits;
  latestRunnerImplementationGapChecklists = runnerImplementationGapChecklists;
  latestRunnerCancelTimeoutContracts = runnerCancelTimeoutContracts;
  latestRunnerSessionStateSchemas = runnerSessionStateSchemas;
  latestRunnerRealTestReadiness = runnerRealTestReadiness;
  latestRunnerRealTestAuthorizationChecklists = runnerRealTestAuthorizationChecklists;
  latestRunnerRealTestAuthorizationPackages = runnerRealTestAuthorizationPackages;
  latestRunnerRealTestSandboxPolicies = runnerRealTestSandboxPolicies;
  latestRunnerRealTestFinalChecklists = runnerRealTestFinalChecklists;
  latestRunnerRealTestUiPreviews = runnerRealTestUiPreviews;
  latestRunnerRealExecutionStageBoundaryReviews = runnerRealExecutionStageBoundaryReviews;
  latestRunnerRealExecutionUnlockMaterialReviews = runnerRealExecutionUnlockMaterialReviews;
  latestRunnerRealExecutionImplementationPlans = runnerRealExecutionImplementationPlans;
  latestRunnerRealExecutionScopeDiffAudits = runnerRealExecutionScopeDiffAudits;
  latestRunnerExecutionAdapterImplementationAudits = runnerExecutionAdapterImplementationAudits;
  latestRunnerProcessLifecycleImplementationAudits = runnerProcessLifecycleImplementationAudits;
  latestRunnerStreamCaptureImplementationAudits = runnerStreamCaptureImplementationAudits;
  latestRunnerEventWriterImplementationAudits = runnerEventWriterImplementationAudits;
  latestRunnerAuditPersistenceImplementationAudits = runnerAuditPersistenceImplementationAudits;
  latestRunnerAuditIntegrityReplayVerificationAudits = runnerAuditIntegrityReplayVerificationAudits;
  latestRunnerVerificationDiscrepancyReportAudits = runnerVerificationDiscrepancyReportAudits;
  latestRunnerRealLaunchFinalGateAudits = runnerRealLaunchFinalGateAudits;
  latestRunnerEvidenceGapIndexes = runnerEvidenceGapIndexes;
  latestRunnerDevelopmentPathAnchors = runnerDevelopmentPathAnchors;
  latestRunnerRealExecutionTouchpointInventories = runnerRealExecutionTouchpointInventories;
  latestRunnerRealExecutionTouchpointCoverageIndexes = runnerRealExecutionTouchpointCoverageIndexes;
  latestRunnerRealExecutionTouchpointGapLinks = runnerRealExecutionTouchpointGapLinks;
  latestRunnerRealExecutionTouchpointUnlockMatrices = runnerRealExecutionTouchpointUnlockMatrices;
  latestRunnerRealExecutionUnlockPhraseReadiness = runnerRealExecutionUnlockPhraseReadiness;
  latestRunnerRealExecutionPreUnlockEvidencePacketIndexes = runnerRealExecutionPreUnlockEvidencePacketIndexes;
  latestRunnerRealExecutionPreUnlockReviewChecklists = runnerRealExecutionPreUnlockReviewChecklists;
  latestRunnerRealExecutionPreUnlockReviewerRoleMaps = runnerRealExecutionPreUnlockReviewerRoleMaps;
  latestRunnerRealExecutionPreUnlockReviewerSignoffRubrics = runnerRealExecutionPreUnlockReviewerSignoffRubrics;
  latestRunnerRealExecutionPreUnlockSignoffEvidenceBindings = runnerRealExecutionPreUnlockSignoffEvidenceBindings;
  latestRunnerRealExecutionPreUnlockImplementationEntryReadinessLedgers = (
    runnerRealExecutionPreUnlockImplementationEntryReadinessLedgers
  );
  latestRunnerRealExecutionPreUnlockRound10MinimalScopePreviews = (
    runnerRealExecutionPreUnlockRound10MinimalScopePreviews
  );
  latestRunnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts = (
    runnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts
  );
  latestRunnerRealExecutionPreRound10LockedHandoffSummaries = (
    runnerRealExecutionPreRound10LockedHandoffSummaries
  );
  latestRunnerRealExecutionRound10ExplicitUnlockCheckpoints = (
    runnerRealExecutionRound10ExplicitUnlockCheckpoints
  );
  latestRunnerRealExecutionRound10UnlockDecisionMirrors = (
    runnerRealExecutionRound10UnlockDecisionMirrors
  );
  renderProject(mainViews.project.container, project, coverage, applyProjectContext, pickProjectPath);
  renderOnboardingView();

  if (!state.activeRunId) {
    for (const id of ["layers", "dataflow", "expanded", "issues", "compare", "events"]) {
      renderEmptyMainView(mainViews[id].container, "选择运行记录后显示该视图。");
    }
    return;
  }

  const runs = await getRuns();
  const activeRun = currentRun(runs, state.activeRunId) || state.activeRunRecord;
  const isExternalRuntimeRun = activeRun?.source === "external_runtime";
  const [layerFlow, dataflow, issueReport, events] = isExternalRuntimeRun
    ? await Promise.all([
      Promise.resolve({ nodes: [], edges: [] }),
      getRunDataflow(state.activeRunId),
      getRunIssues(state.activeRunId),
      getRunEvents(state.activeRunId),
    ])
    : await Promise.all([
      getRunLayers(state.activeRunId),
      getRunDataflow(state.activeRunId),
      getRunIssues(state.activeRunId),
      getRunEvents(state.activeRunId),
    ]);
  const viewEvents = events.length ? events : fallbackExternalRuntimeEvents(activeRun);
  const baseRun = previousRun(runs, state.activeRunId);
  const comparison = baseRun && !isExternalRuntimeRun ? await getRunComparison(state.activeRunId, baseRun.run_id) : null;
  state.latestLayerFlow = layerFlow;
  state.latestDataflow = dataflow;
  renderWatch();
  if (isExternalRuntimeRun) {
    renderEmptyMainView(mainViews.layers.container, "外部 runtime 文件级投影暂无调用层级。");
  } else {
    renderLayerFlow(
      mainViews.layers.container,
      layerFlow,
      state.nodePositions.layers,
      (edge) => renderEdgeComparison(elements.details, edge),
      (method) => renderDetails(elements.details, method),
      watchMethod,
      () => persistNodePositions(state),
    );
  }
  renderDataflow(mainViews.dataflow.container, dataflow, (edge) => renderEdgeComparison(elements.details, edge));
  if (isExternalRuntimeProjection(viewEvents) && !(dataflow.edges || []).length) {
    renderExternalRuntimeDetails(mainViews.expanded.container, viewEvents, (event) => renderDetails(elements.details, event));
  } else {
    renderExpandedDataflow(mainViews.expanded.container, dataflow, (edge) => renderEdgeComparison(elements.details, edge));
  }
  renderIssues(mainViews.issues.container, issueReport, (issue) => renderDetails(elements.details, issue));
  if (comparison) {
    renderComparison(
      mainViews.compare.container,
      comparison,
      { target: activeRun?.label, base: baseRun?.label },
      (item) => renderDetails(elements.details, item),
    );
  } else {
    renderEmptyMainView(mainViews.compare.container, "暂无可对比运行。");
  }
  renderEvents(mainViews.events.container, viewEvents, (event) => renderDetails(elements.details, event));
}

function renderEmptyMainView(container, message) {
  container.className = "graph empty";
  container.textContent = message;
}

async function renderExternalRuntimeRunViews(run) {
  if (!state.activeRunId) {
    return;
  }
  const [dataflow, issueReport, events] = await Promise.all([
    getRunDataflow(state.activeRunId),
    getRunIssues(state.activeRunId),
    getRunEvents(state.activeRunId),
  ]);
  const viewEvents = events.length ? events : fallbackExternalRuntimeEvents(run);
  state.latestLayerFlow = { nodes: [], edges: [] };
  state.latestDataflow = dataflow;
  renderWatch();
  renderExternalRuntimeProjectSkeleton(mainViews.project.container, run, viewEvents);
  renderEmptyMainView(mainViews.layers.container, "外部 runtime 文件级投影暂无调用层级。");
  renderDataflow(mainViews.dataflow.container, dataflow, (edge) => renderEdgeComparison(elements.details, edge));
  renderExternalRuntimeDetails(mainViews.expanded.container, viewEvents, (event) => renderDetails(elements.details, event));
  renderIssues(mainViews.issues.container, issueReport, (issue) => renderDetails(elements.details, issue));
  renderEmptyMainView(mainViews.compare.container, "外部 runtime 投影暂不支持运行对比。");
  renderEvents(mainViews.events.container, viewEvents, (event) => renderDetails(elements.details, event));
}

function renderExternalRuntimeProjectSkeleton(container, run, events) {
  const fileEvents = events.filter((event) => event.action === "external_runtime.file_observed");
  const categories = new Set();
  for (const event of fileEvents) {
    const path = event.payload?.path || "";
    const category = String(path).split("/")[0];
    if (category) {
      categories.add(category);
    }
  }
  const metadata = events[0]?.payload?.metadata || {};
  container.className = "project-view";
  container.innerHTML = `
    <section class="project-section">
      <h2>外部 runtime 运行骨架</h2>
      <div class="summary-grid">
        <article>
          <strong>投影类型</strong>
          <span>${escapeHtml(run.runtime_kind || "runtime_group")}</span>
        </article>
        <article>
          <strong>证据文件</strong>
          <span>${escapeHtml(String(fileEvents.length || run.file_count || 0))}</span>
        </article>
        <article>
          <strong>分类</strong>
          <span>${escapeHtml([...categories].join(", ") || (run.categories || []).join(", ") || "未知")}</span>
        </article>
      </div>
      <div class="detail-list">
        ${Object.entries(metadata).map(([key, value]) => `
          <div>
            <strong>${escapeHtml(key)}</strong>
            <span>${escapeHtml(String(value))}</span>
          </div>
        `).join("") || "<p class=\"empty\">暂无结构化元数据。</p>"}
      </div>
    </section>
    <section class="project-section">
      <h2>关联证据</h2>
      <div class="detail-list">
        ${fileEvents.map((event) => `
          <button class="method-row" type="button" data-event-id="${escapeHtml(event.event_id)}">
            <strong>${escapeHtml(event.payload?.path || event.event_id)}</strong>
            <span>${escapeHtml(event.payload?.format || "file")} - ${escapeHtml(String(event.payload?.size_bytes || 0))} bytes</span>
          </button>
        `).join("") || "<p class=\"empty\">暂无证据文件。</p>"}
      </div>
    </section>
  `;
  for (const button of container.querySelectorAll("[data-event-id]")) {
    const event = events.find((item) => item.event_id === button.dataset.eventId);
    button.addEventListener("click", () => renderDetails(elements.details, event || {}));
  }
}

function renderExternalRuntimeSummary(container, run) {
  container.innerHTML = `
    <div class="summary-grid">
      <article>
        <strong>外部 runtime 投影</strong>
        <span>${escapeHtml(run.format || "file_projection")}</span>
      </article>
      <article>
        <strong>事件数</strong>
        <span>${escapeHtml(String(run.event_count || 0))}</span>
      </article>
      <article>
        <strong>来源文件</strong>
        <span>${escapeHtml(run.label || run.run_id)}</span>
      </article>
    </div>
  `;
}

function isExternalRuntimeProjection(events) {
  return events.some((event) => event.source === "external_runtime" || (event.tags || []).includes("external_runtime"));
}

function renderExternalRuntimeDetails(container, events, onSelectEvent) {
  container.className = "expanded-flow";
  container.innerHTML = "";
  if (!events.length) {
    container.className = "expanded-flow empty";
    container.textContent = "暂无外部运行事件。";
    return;
  }

  for (const event of events) {
    const card = document.createElement("article");
    card.className = "expanded-edge normal";
    card.innerHTML = `
      <button class="expanded-edge-title" type="button">
        <strong>${escapeHtml(event.action || event.event_type || event.event_id)}</strong>
        <em>${escapeHtml(event.timestamp || "未知时间")}</em>
      </button>
      <section class="comparison-pane full">
        <h3>外部 runtime 文件级事件</h3>
        <pre class="code-block">${escapeHtml(JSON.stringify(event, null, 2))}</pre>
      </section>
    `;
    card.querySelector("button")?.addEventListener("click", () => onSelectEvent(event));
    container.appendChild(card);
  }
}

function fallbackExternalRuntimeEvents(run) {
  if (!run || run.source !== "external_runtime") {
    return [];
  }
  return [{
    event_id: `${run.run_id}:external_runtime_fallback`,
    run_id: run.run_id,
    trace_id: `${run.run_id}:trace`,
    timestamp: run.started_at || run.ended_at || "",
    actor: "external_runtime",
    action: "external_runtime.file_projection",
    event_type: "user_action",
    payload: {
      label: run.label,
      event_count: run.event_count,
      source: run.source,
      format: run.format,
      note: "Browser-side fallback generated from the run list because the event payload was unavailable in this view.",
    },
    tags: ["external_runtime", "file_projection", "browser_fallback"],
    source: "external_runtime",
    confidence: 0.2,
    run_label: run.label,
  }];
}

function renderOnboardingView() {
  if (!latestOnboarding) {
    return;
  }
  renderOnboarding(
    mainViews.onboarding.container,
    latestOnboarding,
    latestReadiness,
    latestAudit,
    latestIntegrationPlan,
    latestRunProfiles,
    latestRunPreflight,
    latestRunExecutionGate,
    latestRunnerPlan,
    latestExecutionRequests,
    latestRunnerSessions,
    latestRunnerLaunchSnapshots,
    latestRunnerDryRuns,
    latestRunnerLaunchControls,
    latestRunnerRuntimePolicies,
    latestRunnerExecutionConfigs,
    latestRunnerExecutionConfigChecks,
    latestRunnerConfigSchemaStabilizations,
    latestRunnerConfigFieldContractViews,
    latestRunnerConfigCompatibilityReports,
    latestRunnerConfigRemediationSummaries,
    latestRunnerConfigFieldCoverageIndexes,
    latestRunnerServiceFlagAudits,
    latestRunnerLogDirectoryPolicies,
    latestRunnerLogRetentionPolicies,
    latestRunnerLogCleanupPreviews,
    latestRunnerLogCleanupConfirmations,
    latestRunnerLogCleanupAuditTrails,
    latestRunnerLogCleanupExecutionPlans,
    latestRunnerGovernanceReadiness,
    latestRunnerExecutionAdapterContracts,
    latestRunnerLaunchApiContracts,
    latestRunnerExecutionAdapterReviews,
    latestRunnerFinalBlockMatrices,
    latestRunnerAuthorizationUnlockAudits,
    latestRunnerImplementationGapChecklists,
    latestRunnerCancelTimeoutContracts,
    latestRunnerSessionStateSchemas,
    latestRunnerRealTestReadiness,
    latestRunnerRealTestAuthorizationChecklists,
    latestRunnerRealExecutionImplementationPlans,
    latestRunnerExecutionAdapterImplementationAudits,
    latestRunnerProcessLifecycleImplementationAudits,
    latestRunnerStreamCaptureImplementationAudits,
    latestRunnerEventWriterImplementationAudits,
    latestRunnerAuditPersistenceImplementationAudits,
    latestRunnerAuditIntegrityReplayVerificationAudits,
    latestRunnerVerificationDiscrepancyReportAudits,
    latestRunnerRealLaunchFinalGateAudits,
    latestRunnerEvidenceGapIndexes,
    (suggestion) => getOnboardingSuggestionStatus(state, suggestion),
    (suggestion, status) => {
      setOnboardingSuggestionStatus(state, suggestion, status);
      renderOnboardingView();
    },
    (finding) => renderAuditFindingDetail(elements.details, finding),
    saveRunProfile,
    removeRunProfile,
    confirmPreflight,
    revokePreflight,
    confirmExecutionGate,
    revokeExecutionGate,
    prepareExecutionRequestDraft,
    confirmExecutionRequestDraft,
    revokeExecutionRequestDraft,
    removeExecutionRequestDraft,
    prepareRunnerSessionDraft,
    removeRunnerSessionDraft,
    prepareRunnerLaunchSnapshotDraft,
    removeRunnerLaunchSnapshotDraft,
    prepareRunnerDryRunDraft,
    removeRunnerDryRunDraft,
  );
  renderRunnerWorkbenchView();
}

function renderRunnerWorkbenchView() {
  renderRunnerWorkbench(mainViews.runner.container, {
    runProfiles: latestRunProfiles,
    runPreflight: latestRunPreflight,
    runExecutionGate: latestRunExecutionGate,
    runnerPlan: latestRunnerPlan,
    executionRequests: latestExecutionRequests,
    runnerSessions: latestRunnerSessions,
    runnerLaunchSnapshots: latestRunnerLaunchSnapshots,
    runnerDryRuns: latestRunnerDryRuns,
    runnerRealExecutions: latestRunnerRealExecutions,
    runnerCancelTimeoutRealApis: latestRunnerCancelTimeoutRealApis,
    runnerFirstRealTests: latestRunnerFirstRealTests,
    runnerProcessLifecycles: latestRunnerProcessLifecycles,
    runnerStreamCaptures: latestRunnerStreamCaptures,
    runnerEventWriters: latestRunnerEventWriters,
    runnerAuditPersistences: latestRunnerAuditPersistences,
    runnerAuditIntegrityReplayVerifications: latestRunnerAuditIntegrityReplayVerifications,
    runnerVerificationDiscrepancyReports: latestRunnerVerificationDiscrepancyReports,
    runnerLaunchControls: latestRunnerLaunchControls,
    runnerRuntimePolicies: latestRunnerRuntimePolicies,
    runnerExecutionConfigs: latestRunnerExecutionConfigs,
    runnerExecutionConfigChecks: latestRunnerExecutionConfigChecks,
    runnerConfigSchemaStabilizations: latestRunnerConfigSchemaStabilizations,
    runnerConfigFieldContractViews: latestRunnerConfigFieldContractViews,
    runnerConfigCompatibilityReports: latestRunnerConfigCompatibilityReports,
    runnerConfigRemediationSummaries: latestRunnerConfigRemediationSummaries,
    runnerConfigFieldCoverageIndexes: latestRunnerConfigFieldCoverageIndexes,
    runnerServiceFlagAudits: latestRunnerServiceFlagAudits,
    runnerLogDirectoryPolicies: latestRunnerLogDirectoryPolicies,
    runnerLogRetentionPolicies: latestRunnerLogRetentionPolicies,
    runnerLogCleanupPreviews: latestRunnerLogCleanupPreviews,
    runnerLogCleanupConfirmations: latestRunnerLogCleanupConfirmations,
    runnerLogCleanupAuditTrails: latestRunnerLogCleanupAuditTrails,
    runnerLogCleanupExecutionPlans: latestRunnerLogCleanupExecutionPlans,
    runnerGovernanceReadiness: latestRunnerGovernanceReadiness,
    runnerExecutionAdapterContracts: latestRunnerExecutionAdapterContracts,
    runnerLaunchApiContracts: latestRunnerLaunchApiContracts,
    runnerExecutionAdapterReviews: latestRunnerExecutionAdapterReviews,
    runnerFinalBlockMatrices: latestRunnerFinalBlockMatrices,
    runnerAuthorizationUnlockAudits: latestRunnerAuthorizationUnlockAudits,
    runnerImplementationGapChecklists: latestRunnerImplementationGapChecklists,
    runnerCancelTimeoutContracts: latestRunnerCancelTimeoutContracts,
    runnerSessionStateSchemas: latestRunnerSessionStateSchemas,
    runnerRealTestReadiness: latestRunnerRealTestReadiness,
    runnerRealTestAuthorizationChecklists: latestRunnerRealTestAuthorizationChecklists,
    runnerRealTestAuthorizationPackages: latestRunnerRealTestAuthorizationPackages,
    runnerRealTestSandboxPolicies: latestRunnerRealTestSandboxPolicies,
    runnerRealTestFinalChecklists: latestRunnerRealTestFinalChecklists,
    runnerRealTestUiPreviews: latestRunnerRealTestUiPreviews,
    runnerRealExecutionStageBoundaryReviews: latestRunnerRealExecutionStageBoundaryReviews,
    runnerRealExecutionUnlockMaterialReviews: latestRunnerRealExecutionUnlockMaterialReviews,
    runnerRealExecutionImplementationPlans: latestRunnerRealExecutionImplementationPlans,
    runnerRealExecutionScopeDiffAudits: latestRunnerRealExecutionScopeDiffAudits,
    runnerExecutionAdapterImplementationAudits: latestRunnerExecutionAdapterImplementationAudits,
    runnerProcessLifecycleImplementationAudits: latestRunnerProcessLifecycleImplementationAudits,
    runnerStreamCaptureImplementationAudits: latestRunnerStreamCaptureImplementationAudits,
    runnerEventWriterImplementationAudits: latestRunnerEventWriterImplementationAudits,
    runnerAuditPersistenceImplementationAudits: latestRunnerAuditPersistenceImplementationAudits,
    runnerAuditIntegrityReplayVerificationAudits: latestRunnerAuditIntegrityReplayVerificationAudits,
    runnerVerificationDiscrepancyReportAudits: latestRunnerVerificationDiscrepancyReportAudits,
    runnerRealLaunchFinalGateAudits: latestRunnerRealLaunchFinalGateAudits,
    runnerEvidenceGapIndexes: latestRunnerEvidenceGapIndexes,
    runnerDevelopmentPathAnchors: latestRunnerDevelopmentPathAnchors,
    runnerRealExecutionTouchpointInventories: latestRunnerRealExecutionTouchpointInventories,
    runnerRealExecutionTouchpointCoverageIndexes: latestRunnerRealExecutionTouchpointCoverageIndexes,
    runnerRealExecutionTouchpointGapLinks: latestRunnerRealExecutionTouchpointGapLinks,
    runnerRealExecutionTouchpointUnlockMatrices: latestRunnerRealExecutionTouchpointUnlockMatrices,
    runnerRealExecutionUnlockPhraseReadiness: latestRunnerRealExecutionUnlockPhraseReadiness,
    runnerRealExecutionPreUnlockEvidencePacketIndexes: latestRunnerRealExecutionPreUnlockEvidencePacketIndexes,
    runnerRealExecutionPreUnlockReviewChecklists: latestRunnerRealExecutionPreUnlockReviewChecklists,
    runnerRealExecutionPreUnlockReviewerRoleMaps: latestRunnerRealExecutionPreUnlockReviewerRoleMaps,
    runnerRealExecutionPreUnlockReviewerSignoffRubrics: (
      latestRunnerRealExecutionPreUnlockReviewerSignoffRubrics
    ),
    runnerRealExecutionPreUnlockSignoffEvidenceBindings: (
      latestRunnerRealExecutionPreUnlockSignoffEvidenceBindings
    ),
    runnerRealExecutionPreUnlockImplementationEntryReadinessLedgers: (
      latestRunnerRealExecutionPreUnlockImplementationEntryReadinessLedgers
    ),
    runnerRealExecutionPreUnlockRound10MinimalScopePreviews: (
      latestRunnerRealExecutionPreUnlockRound10MinimalScopePreviews
    ),
    runnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts: (
      latestRunnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts
    ),
    runnerRealExecutionPreRound10LockedHandoffSummaries: (
      latestRunnerRealExecutionPreRound10LockedHandoffSummaries
    ),
    runnerRealExecutionRound10ExplicitUnlockCheckpoints: (
      latestRunnerRealExecutionRound10ExplicitUnlockCheckpoints
    ),
    runnerRealExecutionRound10UnlockDecisionMirrors: (
      latestRunnerRealExecutionRound10UnlockDecisionMirrors
    ),
  });
}

async function refreshRunnerGovernanceTail() {
  latestRunnerConfigSchemaStabilizations = await getProjectRunnerConfigSchemaStabilizations();
  latestRunnerConfigFieldContractViews = await getProjectRunnerConfigFieldContractViews();
  latestRunnerConfigCompatibilityReports = await getProjectRunnerConfigCompatibilityReports();
  latestRunnerConfigRemediationSummaries = await getProjectRunnerConfigRemediationSummaries();
  latestRunnerConfigFieldCoverageIndexes = await getProjectRunnerConfigFieldCoverageIndexes();
  latestRunnerLogCleanupExecutionPlans = await getProjectRunnerLogCleanupExecutionPlans();
  latestRunnerGovernanceReadiness = await getProjectRunnerGovernanceReadiness();
  latestRunnerExecutionAdapterContracts = await getProjectRunnerExecutionAdapterContracts();
  latestRunnerLaunchApiContracts = await getProjectRunnerLaunchApiContracts();
  latestRunnerExecutionAdapterReviews = await getProjectRunnerExecutionAdapterReviews();
  latestRunnerFinalBlockMatrices = await getProjectRunnerFinalBlockMatrices();
  latestRunnerAuthorizationUnlockAudits = await getProjectRunnerAuthorizationUnlockAudits();
  latestRunnerImplementationGapChecklists = await getProjectRunnerImplementationGapChecklists();
  latestRunnerCancelTimeoutContracts = await getProjectRunnerCancelTimeoutContracts();
  latestRunnerSessionStateSchemas = await getProjectRunnerSessionStateSchemas();
  latestRunnerRealTestReadiness = await getProjectRunnerRealTestReadiness();
  latestRunnerRealTestAuthorizationChecklists = await getProjectRunnerRealTestAuthorizationChecklists();
  latestRunnerRealTestAuthorizationPackages = await getProjectRunnerRealTestAuthorizationPackages();
  latestRunnerRealTestSandboxPolicies = await getProjectRunnerRealTestSandboxPolicies();
  latestRunnerRealTestFinalChecklists = await getProjectRunnerRealTestFinalChecklists();
  latestRunnerRealTestUiPreviews = await getProjectRunnerRealTestUiPreviews();
  latestRunnerRealExecutionStageBoundaryReviews = await getProjectRunnerRealExecutionStageBoundaryReviews();
  latestRunnerRealExecutionUnlockMaterialReviews = await getProjectRunnerRealExecutionUnlockMaterialReviews();
  latestRunnerRealExecutionImplementationPlans = await getProjectRunnerRealExecutionImplementationPlans();
  latestRunnerRealExecutionScopeDiffAudits = await getProjectRunnerRealExecutionScopeDiffAudits();
  latestRunnerExecutionAdapterImplementationAudits = await getProjectRunnerExecutionAdapterImplementationAudits();
  latestRunnerProcessLifecycleImplementationAudits = await getProjectRunnerProcessLifecycleImplementationAudits();
  latestRunnerStreamCaptureImplementationAudits = await getProjectRunnerStreamCaptureImplementationAudits();
  latestRunnerEventWriterImplementationAudits = await getProjectRunnerEventWriterImplementationAudits();
  latestRunnerAuditPersistenceImplementationAudits = await getProjectRunnerAuditPersistenceImplementationAudits();
  latestRunnerAuditIntegrityReplayVerificationAudits = await getProjectRunnerAuditIntegrityReplayVerificationAudits();
  latestRunnerVerificationDiscrepancyReportAudits = await getProjectRunnerVerificationDiscrepancyReportAudits();
  latestRunnerRealLaunchFinalGateAudits = await getProjectRunnerRealLaunchFinalGateAudits();
  latestRunnerEvidenceGapIndexes = await getProjectRunnerEvidenceGapIndexes();
  latestRunnerDevelopmentPathAnchors = await getProjectRunnerDevelopmentPathAnchors();
  latestRunnerRealExecutionTouchpointInventories = await getProjectRunnerRealExecutionTouchpointInventories();
  latestRunnerRealExecutionTouchpointCoverageIndexes = await getProjectRunnerRealExecutionTouchpointCoverageIndexes();
  latestRunnerRealExecutionTouchpointGapLinks = await getProjectRunnerRealExecutionTouchpointGapLinks();
  latestRunnerRealExecutionTouchpointUnlockMatrices = await getProjectRunnerRealExecutionTouchpointUnlockMatrices();
  latestRunnerRealExecutionUnlockPhraseReadiness = await getProjectRunnerRealExecutionUnlockPhraseReadiness();
  latestRunnerRealExecutionPreUnlockEvidencePacketIndexes = (
    await getProjectRunnerRealExecutionPreUnlockEvidencePacketIndexes()
  );
  latestRunnerRealExecutionPreUnlockReviewChecklists = await getProjectRunnerRealExecutionPreUnlockReviewChecklists();
  latestRunnerRealExecutionPreUnlockReviewerRoleMaps = await getProjectRunnerRealExecutionPreUnlockReviewerRoleMaps();
  latestRunnerRealExecutionPreUnlockReviewerSignoffRubrics = (
    await getProjectRunnerRealExecutionPreUnlockReviewerSignoffRubrics()
  );
  latestRunnerRealExecutionPreUnlockSignoffEvidenceBindings = (
    await getProjectRunnerRealExecutionPreUnlockSignoffEvidenceBindings()
  );
  latestRunnerRealExecutionPreUnlockImplementationEntryReadinessLedgers = (
    await getProjectRunnerRealExecutionPreUnlockImplementationEntryReadinessLedgers()
  );
  latestRunnerRealExecutionPreUnlockRound10MinimalScopePreviews = (
    await getProjectRunnerRealExecutionPreUnlockRound10MinimalScopePreviews()
  );
  latestRunnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts = (
    await getProjectRunnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts()
  );
  latestRunnerRealExecutionPreRound10LockedHandoffSummaries = (
    await getProjectRunnerRealExecutionPreRound10LockedHandoffSummaries()
  );
  latestRunnerRealExecutionRound10ExplicitUnlockCheckpoints = (
    await getProjectRunnerRealExecutionRound10ExplicitUnlockCheckpoints()
  );
  latestRunnerRealExecutionRound10UnlockDecisionMirrors = (
    await getProjectRunnerRealExecutionRound10UnlockDecisionMirrors()
  );
}

async function saveRunProfile(profile) {
  if (!profile?.id) {
    return;
  }
  latestRunProfiles = await saveProjectRunProfile(profile.id);
  latestRunPreflight = await getProjectRunPreflight();
  latestRunExecutionGate = await getProjectRunExecutionGate();
  latestRunnerPlan = await getProjectRunnerPlan();
  latestExecutionRequests = await getProjectExecutionRequests();
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function removeRunProfile(profile) {
  if (!profile?.id) {
    return;
  }
  latestRunProfiles = await removeProjectRunProfile(profile.id);
  latestRunPreflight = await getProjectRunPreflight();
  latestRunExecutionGate = await getProjectRunExecutionGate();
  latestRunnerPlan = await getProjectRunnerPlan();
  latestExecutionRequests = await getProjectExecutionRequests();
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function confirmPreflight(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunPreflight = await confirmRunPreflight(report.profile_id);
  latestRunExecutionGate = await getProjectRunExecutionGate();
  latestRunnerPlan = await getProjectRunnerPlan();
  latestExecutionRequests = await getProjectExecutionRequests();
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function revokePreflight(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunPreflight = await revokeRunPreflight(report.profile_id);
  latestRunExecutionGate = await getProjectRunExecutionGate();
  latestRunnerPlan = await getProjectRunnerPlan();
  latestExecutionRequests = await getProjectExecutionRequests();
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function confirmExecutionGate(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunExecutionGate = await confirmRunExecutionGate(report.profile_id);
  latestRunnerPlan = await getProjectRunnerPlan();
  latestExecutionRequests = await getProjectExecutionRequests();
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function revokeExecutionGate(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunExecutionGate = await revokeRunExecutionGate(report.profile_id);
  latestRunnerPlan = await getProjectRunnerPlan();
  latestExecutionRequests = await getProjectExecutionRequests();
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function prepareExecutionRequestDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestExecutionRequests = await prepareExecutionRequest(report.profile_id);
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function confirmExecutionRequestDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestExecutionRequests = await confirmExecutionRequest(report.profile_id);
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function revokeExecutionRequestDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestExecutionRequests = await revokeExecutionRequest(report.profile_id);
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function removeExecutionRequestDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestExecutionRequests = await removeExecutionRequest(report.profile_id);
  latestRunnerSessions = await getProjectRunnerSessions();
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function prepareRunnerSessionDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunnerSessions = await prepareRunnerSession(report.profile_id);
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function removeRunnerSessionDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunnerSessions = await removeRunnerSession(report.profile_id);
  latestRunnerLaunchSnapshots = await getProjectRunnerLaunchSnapshots();
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function prepareRunnerLaunchSnapshotDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunnerLaunchSnapshots = await prepareRunnerLaunchSnapshot(report.profile_id);
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function removeRunnerLaunchSnapshotDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunnerLaunchSnapshots = await removeRunnerLaunchSnapshot(report.profile_id);
  latestRunnerDryRuns = await getProjectRunnerDryRuns();
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function prepareRunnerDryRunDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunnerDryRuns = await prepareRunnerDryRun(report.profile_id);
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function removeRunnerDryRunDraft(report) {
  if (!report?.profile_id) {
    return;
  }
  latestRunnerDryRuns = await removeRunnerDryRun(report.profile_id);
  latestRunnerRealExecutions = await getProjectRunnerRealExecutions();
  latestRunnerCancelTimeoutRealApis = await getProjectRunnerCancelTimeoutRealApis();
  latestRunnerFirstRealTests = await getProjectRunnerFirstRealTests();
  latestRunnerProcessLifecycles = await getProjectRunnerProcessLifecycles();
  latestRunnerStreamCaptures = await getProjectRunnerStreamCaptures();
  latestRunnerEventWriters = await getProjectRunnerEventWriters();
  latestRunnerAuditPersistences = await getProjectRunnerAuditPersistences();
  latestRunnerAuditIntegrityReplayVerifications = await getProjectRunnerAuditIntegrityReplayVerifications();
  latestRunnerVerificationDiscrepancyReports = await getProjectRunnerVerificationDiscrepancyReports();
  latestRunnerLaunchControls = await getProjectRunnerLaunchControls();
  latestRunnerRuntimePolicies = await getProjectRunnerRuntimePolicies();
  latestRunnerExecutionConfigs = await getProjectRunnerExecutionConfigs();
  latestRunnerExecutionConfigChecks = await getProjectRunnerExecutionConfigChecks();
  latestRunnerServiceFlagAudits = await getProjectRunnerServiceFlagAudits();
  latestRunnerLogDirectoryPolicies = await getProjectRunnerLogDirectoryPolicies();
  latestRunnerLogRetentionPolicies = await getProjectRunnerLogRetentionPolicies();
  latestRunnerLogCleanupPreviews = await getProjectRunnerLogCleanupPreviews();
  latestRunnerLogCleanupConfirmations = await getProjectRunnerLogCleanupConfirmations();
  latestRunnerLogCleanupAuditTrails = await getProjectRunnerLogCleanupAuditTrails();
  await refreshRunnerGovernanceTail();
  renderOnboardingView();
}

async function applyProjectContext(payload) {
  await setProjectContext(payload);
  state.activeRunId = null;
  state.activeRunRecord = null;
  state.latestLayerFlow = null;
  state.latestDataflow = null;
  elements.runTitle.textContent = "尚未选择运行记录";
  elements.runMeta.textContent = "目标项目已切换，请选择运行记录或执行目标流程。";
  elements.runSummary.innerHTML = "";
  renderDetails(elements.details, {});
  renderWatch();
  await loadRuns();
  await renderMainViews();
}

async function pickProjectPath(payload) {
  return openPathDialog(payload);
}

function showMainViewError(error) {
  for (const view of Object.values(mainViews)) {
    renderEmptyMainView(view.container, `加载失败：${error.message}`);
  }
}

setInterval(() => {
  if (!state.activeRunId || !state.watchItems.length) {
    return;
  }
  refreshWatchData().catch(() => {
    elements.watchStatus.textContent = "监视刷新失败";
  });
}, WATCH_REFRESH_MS);

loadRuns().catch((error) => {
  elements.runs.innerHTML = `<div class="empty">加载失败：${escapeHtml(error.message)}</div>`;
});

function currentRun(runs, runId) {
  return runs.find((run) => run.run_id === runId);
}

function previousRun(runs, runId) {
  const index = runs.findIndex((run) => run.run_id === runId);
  if (index < 0 || index + 1 >= runs.length) {
    return null;
  }
  return runs[index + 1];
}















