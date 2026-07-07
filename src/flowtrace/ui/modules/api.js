// 模块：API 客户端。统一负责读取本地 FlowTrace 服务数据。
export async function getRuns() {
  return getJson("/api/runs");
}

export async function getRunEvents(runId) {
  return getJson(`/api/runs/${encodeURIComponent(runId)}/events`);
}

export async function getRunDataflow(runId) {
  return getJson(`/api/runs/${encodeURIComponent(runId)}/dataflow`);
}

export async function getRunLayers(runId) {
  return getJson(`/api/runs/${encodeURIComponent(runId)}/layers`);
}

export async function getRunComparison(runId, baseRunId) {
  const query = baseRunId ? `?base_run_id=${encodeURIComponent(baseRunId)}` : "";
  return getJson(`/api/runs/${encodeURIComponent(runId)}/compare${query}`);
}

export async function getRunIssues(runId) {
  return getJson(`/api/runs/${encodeURIComponent(runId)}/issues`);
}

export async function getRunSummary(runId) {
  return getJson(`/api/runs/${encodeURIComponent(runId)}/summary`);
}

export async function getProject() {
  return getJson("/api/project");
}

export async function getProjectBootstrap() {
  return getJson("/api/project/bootstrap");
}

export async function getProjectCoverage() {
  return getJson("/api/project/coverage");
}

export async function getProjectOnboarding() {
  return getJson("/api/project/onboarding");
}

export async function getProjectReadiness() {
  return getJson("/api/project/readiness");
}

export async function getProjectAudit() {
  return getJson("/api/project/audit");
}

export async function getProjectIntegrationPlan() {
  return getJson("/api/project/integration-plan");
}

export async function getProjectRunProfiles() {
  return getJson("/api/project/run-profiles");
}

export async function getProjectRunPreflight() {
  return getJson("/api/project/run-preflight");
}

export async function getProjectRunExecutionGate() {
  return getJson("/api/project/run-execution-gate");
}

export async function getProjectRunnerPlan() {
  return getJson("/api/project/runner-plan");
}

export async function getProjectExecutionRequests() {
  return getJson("/api/project/execution-requests");
}

export async function getProjectRunnerSessions() {
  return getJson("/api/project/runner-sessions");
}

export async function getProjectRunnerLaunchSnapshots() {
  return getJson("/api/project/runner-launch-snapshots");
}

export async function getProjectRunnerDryRuns() {
  return getJson("/api/project/runner-dry-runs");
}

export async function getProjectRunnerRealExecutions() {
  return getJson("/api/project/runner-real-executions");
}

export async function getProjectRunnerCancelTimeoutRealApis() {
  return getJson("/api/project/runner-cancel-timeout-real-apis");
}

export async function getProjectRunnerFirstRealTests() {
  return getJson("/api/project/runner-first-real-tests");
}

export async function getProjectRunnerProcessLifecycles() {
  return getJson("/api/project/runner-process-lifecycles");
}

export async function getProjectRunnerStreamCaptures() {
  return getJson("/api/project/runner-stream-captures");
}

export async function getProjectRunnerEventWriters() {
  return getJson("/api/project/runner-event-writers");
}

export async function getProjectRunnerAuditPersistences() {
  return getJson("/api/project/runner-audit-persistences");
}

export async function getProjectRunnerAuditIntegrityReplayVerifications() {
  return getJson("/api/project/runner-audit-integrity-replay-verifications");
}

export async function getProjectRunnerVerificationDiscrepancyReports() {
  return getJson("/api/project/runner-verification-discrepancy-reports");
}

export async function launchProjectRunner(profileId, typedConsent) {
  return postJson("/api/project/runner/launch", { profile_id: profileId, typed_consent: typedConsent });
}

export async function cancelProjectRunner(launchId, typedConsent, reason = "") {
  return postJson("/api/project/runner/cancel", { launch_id: launchId, typed_consent: typedConsent, reason });
}

export async function timeoutProjectRunner(launchId, typedConsent, reason = "") {
  return postJson("/api/project/runner/timeout", { launch_id: launchId, typed_consent: typedConsent, reason });
}

export async function getProjectRunnerLaunchControls() {
  return getJson("/api/project/runner-launch-controls");
}

export async function getProjectRunnerRuntimePolicies() {
  return getJson("/api/project/runner-runtime-policies");
}

export async function getProjectRunnerExecutionConfigs() {
  return getJson("/api/project/runner-execution-configs");
}

export async function getProjectRunnerExecutionConfigChecks() {
  return getJson("/api/project/runner-execution-config-checks");
}

export async function getProjectRunnerConfigSchemaStabilizations() {
  return getJson("/api/project/runner-config-schema-stabilizations");
}

export async function getProjectRunnerConfigFieldContractViews() {
  return getJson("/api/project/runner-config-field-contract-views");
}

export async function getProjectRunnerConfigCompatibilityReports() {
  return getJson("/api/project/runner-config-compatibility-reports");
}

export async function getProjectRunnerConfigRemediationSummaries() {
  return getJson("/api/project/runner-config-remediation-summaries");
}

export async function getProjectRunnerConfigFieldCoverageIndexes() {
  return getJson("/api/project/runner-config-field-coverage-indexes");
}

export async function getProjectRunnerServiceFlagAudits() {
  return getJson("/api/project/runner-service-flag-audits");
}

export async function getProjectRunnerLogDirectoryPolicies() {
  return getJson("/api/project/runner-log-directory-policies");
}

export async function getProjectRunnerLogRetentionPolicies() {
  return getJson("/api/project/runner-log-retention-policies");
}

export async function getProjectRunnerLogCleanupPreviews() {
  return getJson("/api/project/runner-log-cleanup-previews");
}

export async function getProjectRunnerLogCleanupConfirmations() {
  return getJson("/api/project/runner-log-cleanup-confirmations");
}

export async function getProjectRunnerLogCleanupAuditTrails() {
  return getJson("/api/project/runner-log-cleanup-audit-trails");
}

export async function getProjectRunnerLogCleanupExecutionPlans() {
  return getJson("/api/project/runner-log-cleanup-execution-plans");
}

export async function getProjectRunnerGovernanceReadiness() {
  return getJson("/api/project/runner-governance-readiness");
}

export async function getProjectRunnerExecutionAdapterContracts() {
  return getJson("/api/project/runner-execution-adapter-contracts");
}

export async function getProjectRunnerLaunchApiContracts() {
  return getJson("/api/project/runner-launch-api-contracts");
}

export async function getProjectRunnerExecutionAdapterReviews() {
  return getJson("/api/project/runner-execution-adapter-reviews");
}

export async function getProjectRunnerFinalBlockMatrices() {
  return getJson("/api/project/runner-final-block-matrices");
}

export async function getProjectRunnerAuthorizationUnlockAudits() {
  return getJson("/api/project/runner-authorization-unlock-audits");
}

export async function getProjectRunnerImplementationGapChecklists() {
  return getJson("/api/project/runner-implementation-gap-checklists");
}

export async function getProjectRunnerCancelTimeoutContracts() {
  return getJson("/api/project/runner-cancel-timeout-contracts");
}

export async function getProjectRunnerSessionStateSchemas() {
  return getJson("/api/project/runner-session-state-schemas");
}

export async function getProjectRunnerRealTestReadiness() {
  return getJson("/api/project/runner-real-test-readiness");
}

export async function getProjectRunnerRealTestAuthorizationChecklists() {
  return getJson("/api/project/runner-real-test-authorization-checklists");
}

export async function getProjectRunnerRealTestAuthorizationPackages() {
  return getJson("/api/project/runner-real-test-authorization-packages");
}

export async function getProjectRunnerRealTestSandboxPolicies() {
  return getJson("/api/project/runner-real-test-sandbox-policies");
}

export async function getProjectRunnerRealTestFinalChecklists() {
  return getJson("/api/project/runner-real-test-final-checklists");
}

export async function getProjectRunnerRealTestUiPreviews() {
  return getJson("/api/project/runner-real-test-ui-previews");
}

export async function getProjectRunnerRealExecutionStageBoundaryReviews() {
  return getJson("/api/project/runner-real-execution-stage-boundary-reviews");
}

export async function getProjectRunnerRealExecutionUnlockMaterialReviews() {
  return getJson("/api/project/runner-real-execution-unlock-material-reviews");
}

export async function getProjectRunnerRealExecutionImplementationPlans() {
  return getJson("/api/project/runner-real-execution-implementation-plans");
}

export async function getProjectRunnerRealExecutionScopeDiffAudits() {
  return getJson("/api/project/runner-real-execution-scope-diff-audits");
}

export async function getProjectRunnerExecutionAdapterImplementationAudits() {
  return getJson("/api/project/runner-execution-adapter-implementation-audits");
}

export async function getProjectRunnerProcessLifecycleImplementationAudits() {
  return getJson("/api/project/runner-process-lifecycle-implementation-audits");
}

export async function getProjectRunnerStreamCaptureImplementationAudits() {
  return getJson("/api/project/runner-stream-capture-implementation-audits");
}

export async function getProjectRunnerEventWriterImplementationAudits() {
  return getJson("/api/project/runner-event-writer-implementation-audits");
}

export async function getProjectRunnerAuditPersistenceImplementationAudits() {
  return getJson("/api/project/runner-audit-persistence-implementation-audits");
}

export async function getProjectRunnerAuditIntegrityReplayVerificationAudits() {
  return getJson("/api/project/runner-audit-integrity-replay-verification-audits");
}

export async function getProjectRunnerVerificationDiscrepancyReportAudits() {
  return getJson("/api/project/runner-verification-discrepancy-report-audits");
}

export async function getProjectRunnerRealLaunchFinalGateAudits() {
  return getJson("/api/project/runner-real-launch-final-gate-audits");
}

export async function getProjectRunnerEvidenceGapIndexes() {
  return getJson("/api/project/runner-evidence-gap-indexes");
}

export async function getProjectRunnerDevelopmentPathAnchors() {
  return getJson("/api/project/runner-development-path-anchors");
}

export async function getProjectRunnerRealExecutionTouchpointInventories() {
  return getJson("/api/project/runner-real-execution-touchpoint-inventories");
}

export async function getProjectRunnerRealExecutionTouchpointCoverageIndexes() {
  return getJson("/api/project/runner-real-execution-touchpoint-coverage-indexes");
}

export async function getProjectRunnerRealExecutionTouchpointGapLinks() {
  return getJson("/api/project/runner-real-execution-touchpoint-gap-links");
}

export async function getProjectRunnerRealExecutionTouchpointUnlockMatrices() {
  return getJson("/api/project/runner-real-execution-touchpoint-unlock-matrices");
}

export async function getProjectRunnerRealExecutionUnlockPhraseReadiness() {
  return getJson("/api/project/runner-real-execution-unlock-phrase-readiness");
}

export async function getProjectRunnerRealExecutionPreUnlockEvidencePacketIndexes() {
  return getJson("/api/project/runner-real-execution-pre-unlock-evidence-packet-indexes");
}

export async function getProjectRunnerRealExecutionPreUnlockReviewChecklists() {
  return getJson("/api/project/runner-real-execution-pre-unlock-review-checklists");
}

export async function getProjectRunnerRealExecutionPreUnlockReviewerRoleMaps() {
  return getJson("/api/project/runner-real-execution-pre-unlock-reviewer-role-maps");
}

export async function getProjectRunnerRealExecutionPreUnlockReviewerSignoffRubrics() {
  return getJson("/api/project/runner-real-execution-pre-unlock-reviewer-signoff-rubrics");
}

export async function getProjectRunnerRealExecutionPreUnlockSignoffEvidenceBindings() {
  return getJson("/api/project/runner-real-execution-pre-unlock-signoff-evidence-bindings");
}

export async function getProjectRunnerRealExecutionPreUnlockImplementationEntryReadinessLedgers() {
  return getJson("/api/project/runner-real-execution-pre-unlock-implementation-entry-readiness-ledgers");
}

export async function getProjectRunnerRealExecutionPreUnlockRound10MinimalScopePreviews() {
  return getJson("/api/project/runner-real-execution-pre-unlock-round10-minimal-scope-previews");
}

export async function getProjectRunnerRealExecutionPreUnlockExplicitUnlockHandoffReceipts() {
  return getJson("/api/project/runner-real-execution-pre-unlock-explicit-unlock-handoff-receipts");
}

export async function getProjectRunnerRealExecutionPreRound10LockedHandoffSummaries() {
  return getJson("/api/project/runner-real-execution-pre-round10-locked-handoff-summaries");
}

export async function getProjectRunnerRealExecutionRound10ExplicitUnlockCheckpoints() {
  return getJson("/api/project/runner-real-execution-round10-explicit-unlock-checkpoints");
}

export async function getProjectRunnerRealExecutionRound10UnlockDecisionMirrors() {
  return getJson("/api/project/runner-real-execution-round10-unlock-decision-mirrors");
}

export async function saveProjectRunProfile(profileId) {
  return postJson("/api/project/run-profiles/save", { profile_id: profileId });
}

export async function removeProjectRunProfile(profileId) {
  return postJson("/api/project/run-profiles/remove", { profile_id: profileId });
}

export async function confirmRunPreflight(profileId) {
  return postJson("/api/project/run-preflight/confirm", { profile_id: profileId });
}

export async function revokeRunPreflight(profileId) {
  return postJson("/api/project/run-preflight/revoke", { profile_id: profileId });
}

export async function confirmRunExecutionGate(profileId) {
  return postJson("/api/project/run-execution-gate/confirm", { profile_id: profileId });
}

export async function revokeRunExecutionGate(profileId) {
  return postJson("/api/project/run-execution-gate/revoke", { profile_id: profileId });
}

export async function prepareExecutionRequest(profileId) {
  return postJson("/api/project/execution-requests/prepare", { profile_id: profileId });
}

export async function confirmExecutionRequest(profileId) {
  return postJson("/api/project/execution-requests/confirm", { profile_id: profileId });
}

export async function revokeExecutionRequest(profileId) {
  return postJson("/api/project/execution-requests/revoke", { profile_id: profileId });
}

export async function removeExecutionRequest(profileId) {
  return postJson("/api/project/execution-requests/remove", { profile_id: profileId });
}

export async function prepareRunnerSession(profileId) {
  return postJson("/api/project/runner-sessions/prepare", { profile_id: profileId });
}

export async function removeRunnerSession(profileId) {
  return postJson("/api/project/runner-sessions/remove", { profile_id: profileId });
}

export async function prepareRunnerLaunchSnapshot(profileId) {
  return postJson("/api/project/runner-launch-snapshots/prepare", { profile_id: profileId });
}

export async function removeRunnerLaunchSnapshot(profileId) {
  return postJson("/api/project/runner-launch-snapshots/remove", { profile_id: profileId });
}

export async function prepareRunnerDryRun(profileId) {
  return postJson("/api/project/runner-dry-runs/prepare", { profile_id: profileId });
}

export async function removeRunnerDryRun(profileId) {
  return postJson("/api/project/runner-dry-runs/remove", { profile_id: profileId });
}

export async function setProjectContext(payload) {
  return postJson("/api/project/context", payload);
}

export async function openPathDialog(payload) {
  return postJson("/api/fs/dialog", payload);
}

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || `${response.status} ${response.statusText}`);
  }
  return body;
}
