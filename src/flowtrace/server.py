from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .audit import build_project_audit
from .execution_request import build_project_execution_requests
from .execution_request_store import (
    confirm_execution_request,
    load_execution_requests,
    prepare_execution_request,
    remove_execution_request,
    revoke_execution_request_confirmation,
)
from .integration_plan import build_project_integration_plan
from .interpretation import (
    build_project_coverage,
    build_dataflow,
    build_graph,
    build_layer_flow,
    build_run_comparison,
    build_run_issues,
    build_run_summary,
    collect_method_catalog,
)
from .onboarding import build_project_onboarding
from .project_context import ProjectContext, load_project_context
from .readiness import build_project_readiness
from .run_confirmation_store import confirm_run_profile, load_run_confirmations, revoke_run_confirmation
from .run_execution_gate import build_project_run_execution_gate
from .run_final_confirmation_store import (
    confirm_run_final_execution,
    load_run_final_confirmations,
    revoke_run_final_confirmation,
)
from .run_preflight import build_project_run_preflight
from .run_profile import build_project_run_profiles
from .run_profile_store import annotate_run_profiles, load_saved_run_profiles, remove_run_profile, save_run_profile
from .runner_dry_run import build_project_runner_dry_runs
from .runner_dry_run_store import load_runner_dry_runs, prepare_runner_dry_run, remove_runner_dry_run
from .runner_audit_persistence import build_project_runner_audit_persistences
from .runner_audit_persistence_implementation_audit import build_project_runner_audit_persistence_implementation_audits
from .runner_audit_integrity_replay_verification import (
    build_project_runner_audit_integrity_replay_verifications,
)
from .runner_audit_integrity_replay_verification_audit import (
    build_project_runner_audit_integrity_replay_verification_audits,
)
from .runner_verification_discrepancy_report import build_project_runner_verification_discrepancy_reports
from .runner_execution_adapter_contract import build_project_runner_execution_adapter_contracts
from .runner_execution_adapter_implementation_audit import build_project_runner_execution_adapter_implementation_audits
from .runner_execution_adapter_review import build_project_runner_execution_adapter_reviews
from .runner_event_writer import build_project_runner_event_writers
from .runner_event_writer_implementation_audit import build_project_runner_event_writer_implementation_audits
from .runner_execution_config import build_project_runner_execution_configs
from .runner_execution_config_check import build_project_runner_execution_config_checks
from .runner_config_schema_stabilization import build_project_runner_config_schema_stabilizations
from .runner_config_field_contract_view import build_project_runner_config_field_contract_views
from .runner_config_compatibility_report import build_project_runner_config_compatibility_reports
from .runner_config_remediation_summary import build_project_runner_config_remediation_summaries
from .runner_config_field_coverage_index import build_project_runner_config_field_coverage_indexes
from .runner_authorization_unlock_audit import build_project_runner_authorization_unlock_audits
from .runner_cancel_timeout_contract import build_project_runner_cancel_timeout_contracts
from .runner_cancel_timeout_real_api import build_project_runner_cancel_timeout_real_apis
from .runner_first_real_test import build_project_runner_first_real_tests
from .runner_final_block_matrix import build_project_runner_final_block_matrices
from .runner_governance_readiness import build_project_runner_governance_readiness
from .runner_implementation_gap_checklist import build_project_runner_implementation_gap_checklists
from .runner_launch_api_contract import build_project_runner_launch_api_contracts
from .runner_launch_control import build_project_runner_launch_controls
from .runner_launch_snapshot import build_project_runner_launch_snapshots
from .runner_launch_snapshot_store import (
    load_runner_launch_snapshots,
    prepare_runner_launch_snapshot,
    remove_runner_launch_snapshot,
)
from .runner_log_cleanup_audit_trail import build_project_runner_log_cleanup_audit_trails
from .runner_log_cleanup_confirmation import build_project_runner_log_cleanup_confirmations
from .runner_log_cleanup_execution_plan import build_project_runner_log_cleanup_execution_plans
from .runner_log_cleanup_preview import build_project_runner_log_cleanup_previews
from .runner_log_directory_policy import build_project_runner_log_directory_policies
from .runner_log_retention_policy import build_project_runner_log_retention_policies
from .runner_plan import build_project_runner_plan
from .runner_process_lifecycle import build_project_runner_process_lifecycles
from .runner_process_lifecycle_implementation_audit import build_project_runner_process_lifecycle_implementation_audits
from .runner_runtime_policy import build_project_runner_runtime_policies
from .runner_service_flag_audit import build_project_runner_service_flag_audits
from .runner_real_execution_implementation_plan import build_project_runner_real_execution_implementation_plans
from .runner_real_execution_scope_diff_audit import build_project_runner_real_execution_scope_diff_audits
from .runner_real_execution_stage_boundary_review import build_project_runner_real_execution_stage_boundary_reviews
from .runner_real_execution_unlock_material_review import (
    build_project_runner_real_execution_unlock_material_reviews,
)
from .runner_development_path_anchor import build_project_runner_development_path_anchors
from .runner_real_execution_touchpoint_inventory import build_project_runner_real_execution_touchpoint_inventories
from .runner_real_execution_touchpoint_coverage_index import (
    build_project_runner_real_execution_touchpoint_coverage_indexes,
)
from .runner_real_execution_touchpoint_gap_link import build_project_runner_real_execution_touchpoint_gap_links
from .runner_real_execution_touchpoint_unlock_matrix import (
    build_project_runner_real_execution_touchpoint_unlock_matrices,
)
from .runner_real_execution_unlock_phrase_readiness import (
    build_project_runner_real_execution_unlock_phrase_readiness,
)
from .runner_real_execution_pre_unlock_evidence_packet_index import (
    build_project_runner_real_execution_pre_unlock_evidence_packet_indexes,
)
from .runner_real_execution_pre_unlock_review_checklist import (
    build_project_runner_real_execution_pre_unlock_review_checklists,
)
from .runner_real_execution_pre_unlock_reviewer_role_map import (
    build_project_runner_real_execution_pre_unlock_reviewer_role_maps,
)
from .runner_real_execution_pre_unlock_reviewer_signoff_rubric import (
    build_project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics,
)
from .runner_real_execution_pre_unlock_signoff_evidence_binding import (
    build_project_runner_real_execution_pre_unlock_signoff_evidence_bindings,
)
from .runner_real_execution_pre_unlock_implementation_entry_readiness_ledger import (
    build_project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
)
from .runner_real_execution_pre_unlock_round10_minimal_scope_preview import (
    build_project_runner_real_execution_pre_unlock_round10_minimal_scope_previews,
)
from .runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt import (
    build_project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
)
from .runner_real_execution_pre_round10_locked_handoff_summary import (
    build_project_runner_real_execution_pre_round10_locked_handoff_summaries,
)
from .runner_real_execution_round10_explicit_unlock_checkpoint import (
    build_project_runner_real_execution_round10_explicit_unlock_checkpoints,
)
from .runner_real_execution_round10_unlock_decision_mirror import (
    build_project_runner_real_execution_round10_unlock_decision_mirrors,
)
from .runner_real_execution_adapter import launch_low_risk_sample_profile
from .runner_process_control import RUNNER_CANCEL_TIMEOUT_TYPED_CONSENT, RunnerProcessRegistry
from .runner_real_execution_store import (
    append_runner_real_execution,
    build_project_runner_real_executions,
    load_runner_real_executions,
)
from .runner_real_test_authorization_package import build_project_runner_real_test_authorization_packages
from .runner_real_test_authorization_checklist import build_project_runner_real_test_authorization_checklists
from .runner_real_test_final_checklist import build_project_runner_real_test_final_checklists
from .runner_real_test_readiness import build_project_runner_real_test_readiness
from .runner_real_test_sandbox_policy import build_project_runner_real_test_sandbox_policies
from .runner_real_test_ui_preview import build_project_runner_real_test_ui_previews
from .runner_session_state_schema import build_project_runner_session_state_schemas
from .runner_session import build_project_runner_sessions
from .runner_session_store import load_runner_sessions, prepare_runner_session, remove_runner_session
from .runner_stream_capture import build_project_runner_stream_captures
from .runner_stream_capture_implementation_audit import build_project_runner_stream_capture_implementation_audits
from .runner_real_launch_final_gate_audit import build_project_runner_real_launch_final_gate_audits
from .runner_evidence_gap_index import build_project_runner_evidence_gap_indexes
from .runner_verification_discrepancy_report_audit import build_project_runner_verification_discrepancy_report_audits
from .scanner import collect_declared_methods, scan_project
from .storage import EXTERNAL_RUNTIME_PREFIX, list_runs, read_events


UI_DIR = Path(__file__).parent / "ui"


class FlowTraceServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class: type[BaseHTTPRequestHandler],
        project_context: ProjectContext,
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.project_context = project_context
        self.runner_process_registry = RunnerProcessRegistry()


class FlowTraceHandler(BaseHTTPRequestHandler):
    server_version = "FlowTraceMVP/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/runs":
            self._json(_runs(self.server.project_context))
            return

        if path == "/api/project/context":
            self._json(self.server.project_context.to_payload())
            return

        if path == "/api/project/bootstrap":
            self._json(_project_bootstrap(self.server.project_context))
            return

        if path in {"/api/project", "/api/project/scan"}:
            self._json(_project_model(self.server.project_context))
            return

        if path == "/api/project/coverage":
            self._json(build_project_coverage(_project_model(self.server.project_context), _events_by_run(self.server.project_context)))
            return

        if path == "/api/project/onboarding":
            project_model = _project_model(self.server.project_context)
            coverage = build_project_coverage(project_model, _events_by_run(self.server.project_context))
            self._json(build_project_onboarding(project_model, coverage))
            return

        if path == "/api/project/readiness":
            self._json(_project_readiness(self.server.project_context))
            return

        if path == "/api/project/audit":
            self._json(_project_audit(self.server.project_context))
            return

        if path == "/api/project/integration-plan":
            self._json(_project_integration_plan(self.server.project_context))
            return

        if path == "/api/project/run-profiles":
            self._json(_project_run_profiles(self.server.project_context))
            return

        if path == "/api/project/run-preflight":
            self._json(_project_run_preflight(self.server.project_context))
            return

        if path == "/api/project/run-execution-gate":
            self._json(_project_run_execution_gate(self.server.project_context))
            return

        if path == "/api/project/runner-plan":
            self._json(_project_runner_plan(self.server.project_context))
            return

        if path == "/api/project/execution-requests":
            self._json(_project_execution_requests(self.server.project_context))
            return

        if path == "/api/project/runner-sessions":
            self._json(_project_runner_sessions(self.server.project_context))
            return

        if path == "/api/project/runner-launch-snapshots":
            self._json(_project_runner_launch_snapshots(self.server.project_context))
            return

        if path == "/api/project/runner-dry-runs":
            self._json(_project_runner_dry_runs(self.server.project_context))
            return

        if path == "/api/project/runner-launch-controls":
            self._json(_project_runner_launch_controls(self.server.project_context))
            return

        if path == "/api/project/runner-runtime-policies":
            self._json(_project_runner_runtime_policies(self.server.project_context))
            return

        if path == "/api/project/runner-execution-configs":
            self._json(_project_runner_execution_configs(self.server.project_context))
            return

        if path == "/api/project/runner-execution-config-checks":
            self._json(_project_runner_execution_config_checks(self.server.project_context))
            return

        if path == "/api/project/runner-config-schema-stabilizations":
            self._json(_project_runner_config_schema_stabilizations(self.server.project_context))
            return

        if path == "/api/project/runner-config-field-contract-views":
            self._json(_project_runner_config_field_contract_views(self.server.project_context))
            return

        if path == "/api/project/runner-config-compatibility-reports":
            self._json(_project_runner_config_compatibility_reports(self.server.project_context))
            return

        if path == "/api/project/runner-config-remediation-summaries":
            self._json(_project_runner_config_remediation_summaries(self.server.project_context))
            return

        if path == "/api/project/runner-config-field-coverage-indexes":
            self._json(_project_runner_config_field_coverage_indexes(self.server.project_context))
            return

        if path == "/api/project/runner-service-flag-audits":
            self._json(_project_runner_service_flag_audits(self.server.project_context))
            return

        if path == "/api/project/runner-log-directory-policies":
            self._json(_project_runner_log_directory_policies(self.server.project_context))
            return

        if path == "/api/project/runner-log-retention-policies":
            self._json(_project_runner_log_retention_policies(self.server.project_context))
            return

        if path == "/api/project/runner-log-cleanup-previews":
            self._json(_project_runner_log_cleanup_previews(self.server.project_context))
            return

        if path == "/api/project/runner-log-cleanup-confirmations":
            self._json(_project_runner_log_cleanup_confirmations(self.server.project_context))
            return

        if path == "/api/project/runner-log-cleanup-audit-trails":
            self._json(_project_runner_log_cleanup_audit_trails(self.server.project_context))
            return

        if path == "/api/project/runner-log-cleanup-execution-plans":
            self._json(_project_runner_log_cleanup_execution_plans(self.server.project_context))
            return

        if path == "/api/project/runner-governance-readiness":
            self._json(_project_runner_governance_readiness(self.server.project_context))
            return

        if path == "/api/project/runner-execution-adapter-contracts":
            self._json(_project_runner_execution_adapter_contracts(self.server.project_context))
            return

        if path == "/api/project/runner-launch-api-contracts":
            self._json(_project_runner_launch_api_contracts(self.server.project_context))
            return

        if path == "/api/project/runner-execution-adapter-reviews":
            self._json(_project_runner_execution_adapter_reviews(self.server.project_context))
            return

        if path == "/api/project/runner-final-block-matrices":
            self._json(_project_runner_final_block_matrices(self.server.project_context))
            return

        if path == "/api/project/runner-authorization-unlock-audits":
            self._json(_project_runner_authorization_unlock_audits(self.server.project_context))
            return

        if path == "/api/project/runner-implementation-gap-checklists":
            self._json(_project_runner_implementation_gap_checklists(self.server.project_context))
            return

        if path == "/api/project/runner-cancel-timeout-contracts":
            self._json(_project_runner_cancel_timeout_contracts(self.server.project_context))
            return

        if path == "/api/project/runner-cancel-timeout-real-apis":
            self._json(
                _project_runner_cancel_timeout_real_apis(
                    self.server.project_context,
                    self.server.runner_process_registry.active(),
                )
            )
            return
        if path == "/api/project/runner-first-real-tests":
            self._json(_project_runner_first_real_tests(self.server.project_context))
            return

        if path == "/api/project/runner-session-state-schemas":
            self._json(_project_runner_session_state_schemas(self.server.project_context))
            return

        if path == "/api/project/runner-real-test-readiness":
            self._json(_project_runner_real_test_readiness(self.server.project_context))
            return

        if path == "/api/project/runner-real-test-authorization-checklists":
            self._json(_project_runner_real_test_authorization_checklists(self.server.project_context))
            return

        if path == "/api/project/runner-real-test-authorization-packages":
            self._json(_project_runner_real_test_authorization_packages(self.server.project_context))
            return

        if path == "/api/project/runner-real-test-sandbox-policies":
            self._json(_project_runner_real_test_sandbox_policies(self.server.project_context))
            return

        if path == "/api/project/runner-real-test-final-checklists":
            self._json(_project_runner_real_test_final_checklists(self.server.project_context))
            return

        if path == "/api/project/runner-real-test-ui-previews":
            self._json(_project_runner_real_test_ui_previews(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-stage-boundary-reviews":
            self._json(_project_runner_real_execution_stage_boundary_reviews(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-unlock-material-reviews":
            self._json(_project_runner_real_execution_unlock_material_reviews(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-implementation-plans":
            self._json(_project_runner_real_execution_implementation_plans(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-scope-diff-audits":
            self._json(_project_runner_real_execution_scope_diff_audits(self.server.project_context))
            return

        if path == "/api/project/runner-execution-adapter-implementation-audits":
            self._json(_project_runner_execution_adapter_implementation_audits(self.server.project_context))
            return

        if path == "/api/project/runner-process-lifecycle-implementation-audits":
            self._json(_project_runner_process_lifecycle_implementation_audits(self.server.project_context))
            return

        if path == "/api/project/runner-stream-capture-implementation-audits":
            self._json(_project_runner_stream_capture_implementation_audits(self.server.project_context))
            return

        if path == "/api/project/runner-event-writer-implementation-audits":
            self._json(_project_runner_event_writer_implementation_audits(self.server.project_context))
            return

        if path == "/api/project/runner-audit-persistence-implementation-audits":
            self._json(_project_runner_audit_persistence_implementation_audits(self.server.project_context))
            return

        if path == "/api/project/runner-audit-integrity-replay-verification-audits":
            self._json(_project_runner_audit_integrity_replay_verification_audits(self.server.project_context))
            return

        if path == "/api/project/runner-verification-discrepancy-report-audits":
            self._json(_project_runner_verification_discrepancy_report_audits(self.server.project_context))
            return

        if path == "/api/project/runner-real-launch-final-gate-audits":
            self._json(_project_runner_real_launch_final_gate_audits(self.server.project_context))
            return

        if path == "/api/project/runner-evidence-gap-indexes":
            self._json(_project_runner_evidence_gap_indexes(self.server.project_context))
            return

        if path == "/api/project/runner-development-path-anchors":
            self._json(_project_runner_development_path_anchors(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-touchpoint-inventories":
            self._json(_project_runner_real_execution_touchpoint_inventories(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-touchpoint-coverage-indexes":
            self._json(_project_runner_real_execution_touchpoint_coverage_indexes(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-touchpoint-gap-links":
            self._json(_project_runner_real_execution_touchpoint_gap_links(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-touchpoint-unlock-matrices":
            self._json(_project_runner_real_execution_touchpoint_unlock_matrices(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-unlock-phrase-readiness":
            self._json(_project_runner_real_execution_unlock_phrase_readiness(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-evidence-packet-indexes":
            self._json(_project_runner_real_execution_pre_unlock_evidence_packet_indexes(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-review-checklists":
            self._json(_project_runner_real_execution_pre_unlock_review_checklists(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-reviewer-role-maps":
            self._json(_project_runner_real_execution_pre_unlock_reviewer_role_maps(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-reviewer-signoff-rubrics":
            self._json(_project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-signoff-evidence-bindings":
            self._json(_project_runner_real_execution_pre_unlock_signoff_evidence_bindings(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-implementation-entry-readiness-ledgers":
            self._json(_project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-round10-minimal-scope-previews":
            self._json(_project_runner_real_execution_pre_unlock_round10_minimal_scope_previews(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-unlock-explicit-unlock-handoff-receipts":
            self._json(_project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-pre-round10-locked-handoff-summaries":
            self._json(_project_runner_real_execution_pre_round10_locked_handoff_summaries(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-round10-explicit-unlock-checkpoints":
            self._json(_project_runner_real_execution_round10_explicit_unlock_checkpoints(self.server.project_context))
            return

        if path == "/api/project/runner-real-execution-round10-unlock-decision-mirrors":
            self._json(_project_runner_real_execution_round10_unlock_decision_mirrors(self.server.project_context))
            return

        if path == "/api/project/runner-real-executions":
            self._json(_project_runner_real_executions(self.server.project_context))
            return

        if path == "/api/project/runner-process-lifecycles":
            self._json(_project_runner_process_lifecycles(self.server.project_context))
            return

        if path == "/api/project/runner-stream-captures":
            self._json(_project_runner_stream_captures(self.server.project_context))
            return

        if path == "/api/project/runner-event-writers":
            self._json(_project_runner_event_writers(self.server.project_context))
            return

        if path == "/api/project/runner-audit-persistences":
            self._json(_project_runner_audit_persistences(self.server.project_context))
            return

        if path == "/api/project/runner-audit-integrity-replay-verifications":
            self._json(_project_runner_audit_integrity_replay_verifications(self.server.project_context))
            return

        if path == "/api/project/runner-verification-discrepancy-reports":
            self._json(_project_runner_verification_discrepancy_reports(self.server.project_context))
            return

        if path.startswith("/api/runs/") and path.endswith("/events"):
            run_id = unquote(path.removeprefix("/api/runs/").removesuffix("/events").strip("/"))
            self._json(_events(self.server.project_context, run_id))
            return

        if path.startswith("/api/runs/") and path.endswith("/graph"):
            run_id = unquote(path.removeprefix("/api/runs/").removesuffix("/graph").strip("/"))
            self._json(build_graph(_events(self.server.project_context, run_id)))
            return

        if path.startswith("/api/runs/") and path.endswith("/dataflow"):
            run_id = unquote(path.removeprefix("/api/runs/").removesuffix("/dataflow").strip("/"))
            self._json(build_dataflow(_events(self.server.project_context, run_id)))
            return

        if path.startswith("/api/runs/") and path.endswith("/layers"):
            run_id = unquote(path.removeprefix("/api/runs/").removesuffix("/layers").strip("/"))
            if _is_external_runtime_run(run_id):
                self._json({"nodes": [], "edges": []})
                return
            self._json(build_layer_flow(_events(self.server.project_context, run_id), _method_catalog(self.server.project_context)))
            return

        if path.startswith("/api/runs/") and path.endswith("/compare"):
            run_id = unquote(path.removeprefix("/api/runs/").removesuffix("/compare").strip("/"))
            if _is_external_runtime_run(run_id):
                self._json({"error": "external runtime projections do not support run comparison"}, status=404)
                return
            query = parse_qs(parsed.query)
            base_run_id = query.get("base_run_id", [None])[0] or _previous_run_id(run_id, self.server.project_context)
            if base_run_id is None:
                self._json({"error": "no base run available"}, status=404)
                return
            self._json(
                {
                    "target_run_id": run_id,
                    "base_run_id": base_run_id,
                    **build_run_comparison(
                        _events(self.server.project_context, run_id),
                        _events(self.server.project_context, base_run_id),
                    ),
                }
            )
            return

        if path.startswith("/api/runs/") and path.endswith("/issues"):
            run_id = unquote(path.removeprefix("/api/runs/").removesuffix("/issues").strip("/"))
            self._json(build_run_issues(_events(self.server.project_context, run_id)))
            return

        if path.startswith("/api/runs/") and path.endswith("/summary"):
            run_id = unquote(path.removeprefix("/api/runs/").removesuffix("/summary").strip("/"))
            if _is_external_runtime_run(run_id):
                self._json(_external_runtime_summary(self.server.project_context, run_id))
                return
            self._json(build_run_summary(_events(self.server.project_context, run_id), _method_catalog(self.server.project_context)))
            return

        self._serve_static(path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/project/context":
            self._update_project_context()
            return
        if parsed.path == "/api/fs/dialog":
            self._open_filesystem_dialog()
            return
        if parsed.path == "/api/project/run-profiles/save":
            self._save_run_profile()
            return
        if parsed.path == "/api/project/run-profiles/remove":
            self._remove_run_profile()
            return
        if parsed.path == "/api/project/run-preflight/confirm":
            self._confirm_run_preflight()
            return
        if parsed.path == "/api/project/run-preflight/revoke":
            self._revoke_run_preflight()
            return
        if parsed.path == "/api/project/run-execution-gate/confirm":
            self._confirm_run_execution_gate()
            return
        if parsed.path == "/api/project/run-execution-gate/revoke":
            self._revoke_run_execution_gate()
            return
        if parsed.path == "/api/project/execution-requests/prepare":
            self._prepare_execution_request()
            return
        if parsed.path == "/api/project/execution-requests/confirm":
            self._confirm_execution_request()
            return
        if parsed.path == "/api/project/execution-requests/revoke":
            self._revoke_execution_request()
            return
        if parsed.path == "/api/project/execution-requests/remove":
            self._remove_execution_request()
            return
        if parsed.path == "/api/project/runner-sessions/prepare":
            self._prepare_runner_session()
            return
        if parsed.path == "/api/project/runner-sessions/remove":
            self._remove_runner_session()
            return
        if parsed.path == "/api/project/runner-launch-snapshots/prepare":
            self._prepare_runner_launch_snapshot()
            return
        if parsed.path == "/api/project/runner-launch-snapshots/remove":
            self._remove_runner_launch_snapshot()
            return
        if parsed.path == "/api/project/runner-dry-runs/prepare":
            self._prepare_runner_dry_run()
            return
        if parsed.path == "/api/project/runner-dry-runs/remove":
            self._remove_runner_dry_run()
            return
        if parsed.path == "/api/project/runner/launch":
            self._launch_runner_real_execution()
            return

        if parsed.path == "/api/project/runner/cancel":
            self._control_runner_process("cancelled")
            return

        if parsed.path == "/api/project/runner/timeout":
            self._control_runner_process("timed_out")
            return
        self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _update_project_context(self) -> None:
        try:
            payload = self._read_json_body()
            project_root = _optional_string(payload.get("project_root"))
            trace_dir = _optional_string(payload.get("trace_dir"))
            config_file = _optional_string(payload.get("config_file"))
            if not project_root and not config_file:
                self._json({"error": "project_root or config_file is required"}, status=400)
                return
            next_context = load_project_context(project_root, config_file, trace_dir, cwd=self.server.project_context.root)
            self.server.project_context = ProjectContext(
                root=next_context.root,
                trace_dir=next_context.trace_dir,
                source="runtime",
                config_file=next_context.config_file,
            )
        except ValueError as exc:
            self._json({"error": str(exc)}, status=400)
            return
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)
            return
        self._json(self.server.project_context.to_payload())

    def _open_filesystem_dialog(self) -> None:
        try:
            payload = self._read_json_body()
            kind = _optional_string(payload.get("kind")) or "directory"
            initial_path = _optional_string(payload.get("initial_path"))
            selected_path = _open_native_dialog(kind, initial_path, self.server.project_context.root)
        except ValueError as exc:
            self._json({"error": str(exc)}, status=400)
            return
        self._json(
            {
                "schema_version": "fs_dialog.v1",
                "kind": kind,
                "selected_path": selected_path,
                "cancelled": selected_path is None,
            }
        )

    def _save_run_profile(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            drafts = _draft_project_run_profiles(self.server.project_context)
            profile = _find_run_profile(drafts, profile_id)
            if not profile:
                self._json({"error": f"run profile not found: {profile_id}"}, status=404)
                return
            save_run_profile(self.server.project_context.trace_dir, profile)
            self._json(_project_run_profiles(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _remove_run_profile(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            remove_run_profile(self.server.project_context.trace_dir, profile_id)
            self._json(_project_run_profiles(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _confirm_run_preflight(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            run_profiles = _project_run_profiles(self.server.project_context)
            profile = _find_saved_run_profile(run_profiles, profile_id)
            if not profile:
                self._json({"error": f"saved run profile not found: {profile_id}"}, status=404)
                return
            preflight = _project_run_preflight(self.server.project_context)
            report = _find_preflight_report(preflight, profile_id)
            if not report:
                self._json({"error": f"preflight report not found: {profile_id}"}, status=404)
                return
            if report.get("status") == "blocked":
                self._json({"error": "blocked run profile cannot be confirmed"}, status=400)
                return
            confirm_run_profile(self.server.project_context.trace_dir, profile, report)
            self._json(_project_run_preflight(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _revoke_run_preflight(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            revoke_run_confirmation(self.server.project_context.trace_dir, profile_id)
            self._json(_project_run_preflight(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _confirm_run_execution_gate(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            run_profiles = _project_run_profiles(self.server.project_context)
            profile = _find_saved_run_profile(run_profiles, profile_id)
            if not profile:
                self._json({"error": f"saved run profile not found: {profile_id}"}, status=404)
                return
            preflight = _project_run_preflight(self.server.project_context)
            report = _find_preflight_report(preflight, profile_id)
            if not report:
                self._json({"error": f"preflight report not found: {profile_id}"}, status=404)
                return
            confirmation = report.get("confirmation") if isinstance(report.get("confirmation"), dict) else {}
            if report.get("status") == "blocked" or confirmation.get("status") != "confirmed":
                self._json({"error": "preflight must be confirmed before final execution confirmation"}, status=400)
                return
            confirm_run_final_execution(self.server.project_context.trace_dir, profile, report)
            self._json(_project_run_execution_gate(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _revoke_run_execution_gate(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            revoke_run_final_confirmation(self.server.project_context.trace_dir, profile_id)
            self._json(_project_run_execution_gate(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _prepare_execution_request(self) -> None:
        try:
            profile, runner_report = self._execution_request_inputs()
            if runner_report.get("status") != "ready_for_runner_implementation":
                self._json({"error": "runner plan must be ready before preparing execution request"}, status=400)
                return
            prepare_execution_request(self.server.project_context.trace_dir, profile, runner_report)
            self._json(_project_execution_requests(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _confirm_execution_request(self) -> None:
        try:
            profile, runner_report = self._execution_request_inputs()
            confirm_execution_request(self.server.project_context.trace_dir, profile, runner_report)
            self._json(_project_execution_requests(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _revoke_execution_request(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            revoke_execution_request_confirmation(self.server.project_context.trace_dir, profile_id)
            self._json(_project_execution_requests(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _remove_execution_request(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            remove_execution_request(self.server.project_context.trace_dir, profile_id)
            self._json(_project_execution_requests(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _prepare_runner_session(self) -> None:
        try:
            profile, execution_report = self._runner_session_inputs()
            request = execution_report.get("request") if isinstance(execution_report.get("request"), dict) else {}
            if request.get("status") != "second_confirmed":
                self._json({"error": "execution request must be second-confirmed before preparing runner session"}, status=400)
                return
            prepare_runner_session(self.server.project_context.trace_dir, profile, execution_report)
            self._json(_project_runner_sessions(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _remove_runner_session(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            remove_runner_session(self.server.project_context.trace_dir, profile_id)
            self._json(_project_runner_sessions(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _prepare_runner_launch_snapshot(self) -> None:
        try:
            profile, runner_session_report = self._runner_launch_snapshot_inputs()
            session = runner_session_report.get("session") if isinstance(runner_session_report.get("session"), dict) else {}
            if session.get("status") != "drafted":
                self._json({"error": "runner session must be drafted before preparing launch snapshot"}, status=400)
                return
            prepare_runner_launch_snapshot(self.server.project_context.trace_dir, profile, runner_session_report)
            self._json(_project_runner_launch_snapshots(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _remove_runner_launch_snapshot(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            remove_runner_launch_snapshot(self.server.project_context.trace_dir, profile_id)
            self._json(_project_runner_launch_snapshots(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _prepare_runner_dry_run(self) -> None:
        try:
            profile, launch_snapshot_report = self._runner_dry_run_inputs()
            snapshot = launch_snapshot_report.get("snapshot") if isinstance(launch_snapshot_report.get("snapshot"), dict) else {}
            if snapshot.get("status") != "snapshotted":
                self._json({"error": "launch snapshot must be snapshotted before preparing dry-run runner"}, status=400)
                return
            prepare_runner_dry_run(self.server.project_context.trace_dir, profile, launch_snapshot_report)
            self._json(_project_runner_dry_runs(self.server.project_context))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _remove_runner_dry_run(self) -> None:
        try:
            payload = self._read_json_body()
            profile_id = _optional_string(payload.get("profile_id"))
            if not profile_id:
                self._json({"error": "profile_id is required"}, status=400)
                return
            remove_runner_dry_run(self.server.project_context.trace_dir, profile_id)
            self._json(_project_runner_dry_runs(self.server.project_context))
        except json.JSONDecodeError as exc:
            self._json({"error": f"invalid json: {exc}"}, status=400)

    def _launch_runner_real_execution(self) -> None:
        try:
            profile, dry_run_report, typed_consent = self._runner_real_launch_inputs()
            dry_run = dry_run_report.get("dry_run") if isinstance(dry_run_report.get("dry_run"), dict) else {}
            if dry_run.get("status") != "prepared":
                self._json({"error": "runner dry-run must be prepared before launch"}, status=400)
                return
            execution = launch_low_risk_sample_profile(
                self.server.project_context.to_payload(),
                profile,
                dry_run_report,
                typed_consent,
                self.server.runner_process_registry,
            )
            append_runner_real_execution(self.server.project_context.trace_dir, execution)
            self._json(_project_runner_real_executions(self.server.project_context))
        except subprocess.TimeoutExpired:
            self._json({"error": "runner process timed out"}, status=408)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _control_runner_process(self, action: str) -> None:
        try:
            payload = self._read_json_body()
            launch_id = _optional_string(payload.get("launch_id"))
            typed_consent = _optional_string(payload.get("typed_consent"))
            reason = _optional_string(payload.get("reason"))
            if not launch_id:
                self._json({"error": "launch_id is required"}, status=400)
                return
            if typed_consent != RUNNER_CANCEL_TIMEOUT_TYPED_CONSENT:
                self._json({"error": "typed_consent must be CONTROL TARGET PROJECT"}, status=400)
                return
            result = self.server.runner_process_registry.request_control(launch_id, action, reason)
            self._json(
                {
                    "schema_version": "runner_process_control_response.v1",
                    "action": action,
                    "result": result,
                    "active_processes": self.server.runner_process_registry.active(),
                },
                status=202 if result.get("accepted") else 409,
            )
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, status=400)

    def _execution_request_inputs(self) -> tuple[dict[str, object], dict[str, object]]:
        payload = self._read_json_body()
        profile_id = _optional_string(payload.get("profile_id"))
        if not profile_id:
            raise ValueError("profile_id is required")
        run_profiles = _project_run_profiles(self.server.project_context)
        profile = _find_saved_run_profile(run_profiles, profile_id)
        if not profile:
            raise ValueError(f"saved run profile not found: {profile_id}")
        runner_plan = _project_runner_plan(self.server.project_context)
        runner_report = _find_profile_report(runner_plan, profile_id)
        if not runner_report:
            raise ValueError(f"runner plan report not found: {profile_id}")
        return profile, runner_report

    def _runner_session_inputs(self) -> tuple[dict[str, object], dict[str, object]]:
        payload = self._read_json_body()
        profile_id = _optional_string(payload.get("profile_id"))
        if not profile_id:
            raise ValueError("profile_id is required")
        run_profiles = _project_run_profiles(self.server.project_context)
        profile = _find_saved_run_profile(run_profiles, profile_id)
        if not profile:
            raise ValueError(f"saved run profile not found: {profile_id}")
        execution_requests = _project_execution_requests(self.server.project_context)
        execution_report = _find_profile_report(execution_requests, profile_id)
        if not execution_report:
            raise ValueError(f"execution request report not found: {profile_id}")
        return profile, execution_report

    def _runner_launch_snapshot_inputs(self) -> tuple[dict[str, object], dict[str, object]]:
        payload = self._read_json_body()
        profile_id = _optional_string(payload.get("profile_id"))
        if not profile_id:
            raise ValueError("profile_id is required")
        run_profiles = _project_run_profiles(self.server.project_context)
        profile = _find_saved_run_profile(run_profiles, profile_id)
        if not profile:
            raise ValueError(f"saved run profile not found: {profile_id}")
        runner_sessions = _project_runner_sessions(self.server.project_context)
        runner_session_report = _find_profile_report(runner_sessions, profile_id)
        if not runner_session_report:
            raise ValueError(f"runner session report not found: {profile_id}")
        return profile, runner_session_report

    def _runner_dry_run_inputs(self) -> tuple[dict[str, object], dict[str, object]]:
        payload = self._read_json_body()
        profile_id = _optional_string(payload.get("profile_id"))
        if not profile_id:
            raise ValueError("profile_id is required")
        run_profiles = _project_run_profiles(self.server.project_context)
        profile = _find_saved_run_profile(run_profiles, profile_id)
        if not profile:
            raise ValueError(f"saved run profile not found: {profile_id}")
        launch_snapshots = _project_runner_launch_snapshots(self.server.project_context)
        launch_snapshot_report = _find_profile_report(launch_snapshots, profile_id)
        if not launch_snapshot_report:
            raise ValueError(f"runner launch snapshot report not found: {profile_id}")
        return profile, launch_snapshot_report

    def _runner_real_launch_inputs(self) -> tuple[dict[str, object], dict[str, object], str]:
        payload = self._read_json_body()
        profile_id = _optional_string(payload.get("profile_id"))
        typed_consent = _optional_string(payload.get("typed_consent"))
        if not profile_id:
            raise ValueError("profile_id is required")
        if not typed_consent:
            raise ValueError("typed_consent is required")
        run_profiles = _project_run_profiles(self.server.project_context)
        profile = _find_saved_run_profile(run_profiles, profile_id)
        if not profile:
            raise ValueError(f"saved run profile not found: {profile_id}")
        runner_dry_runs = _project_runner_dry_runs(self.server.project_context)
        dry_run_report = _find_profile_report(runner_dry_runs, profile_id)
        if not dry_run_report:
            raise ValueError(f"runner dry-run report not found: {profile_id}")
        return profile, dry_run_report, typed_consent

    def _read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        payload = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _serve_static(self, path: str) -> None:
        if path == "/":
            path = "/index.html"
        requested = (UI_DIR / path.lstrip("/")).resolve()
        if not str(requested).startswith(str(UI_DIR.resolve())) or not requested.exists() or requested.is_dir():
            self.send_error(404)
            return
        body = requested.read_bytes()
        content_type = mimetypes.guess_type(str(requested))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type = f"{content_type}; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the FlowTrace MVP viewer.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--project", dest="project_root", help="Target project root to scan and correlate.")
    parser.add_argument("--config", dest="config_file", help="Optional FlowTrace config file.")
    parser.add_argument("--trace-dir", dest="trace_dir", help="Optional trace storage directory.")
    args = parser.parse_args()
    project_context = load_project_context(args.project_root, args.config_file, args.trace_dir)
    server = FlowTraceServer((args.host, args.port), FlowTraceHandler, project_context)
    print(f"FlowTrace viewer running at http://{args.host}:{args.port}")
    print(f"FlowTrace target project: {project_context.root} ({project_context.source})")
    print(f"FlowTrace trace directory: {project_context.trace_dir}")
    server.serve_forever()


def _runs(project_context: ProjectContext) -> list[dict[str, object]]:
    return list_runs(project_context.trace_dir)


def _events(project_context: ProjectContext, run_id: str) -> list[dict[str, object]]:
    return read_events(run_id, project_context.trace_dir)


def _is_external_runtime_run(run_id: str) -> bool:
    return run_id.startswith(EXTERNAL_RUNTIME_PREFIX)


def _external_runtime_summary(project_context: ProjectContext, run_id: str) -> dict[str, object]:
    events = _events(project_context, run_id)
    file_event = next((event for event in events if event.get("action") == "external_runtime.file_observed"), {})
    payload = file_event.get("payload") if isinstance(file_event.get("payload"), dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    return {
        "run_id": run_id,
        "event_count": len(events),
        "source": "external_runtime",
        "format": payload.get("format") or "file_projection",
        "path": payload.get("path"),
        "summary": {
            "total": len(events),
            "errors": 0,
            "warnings": 0,
            "projection": "external_runtime_file",
            "file_summary": summary,
        },
        "methods": [],
        "contracts": [],
    }


def _previous_run_id(run_id: str, project_context: ProjectContext) -> str | None:
    runs = _runs(project_context)
    for index, run in enumerate(runs):
        if run["run_id"] == run_id and index + 1 < len(runs):
            return runs[index + 1]["run_id"]
    return None


def _method_catalog(project_context: ProjectContext) -> list[str]:
    runtime_methods = collect_method_catalog(_events(project_context, run["run_id"]) for run in _runs(project_context))
    declared_methods = collect_declared_methods(project_context.root)
    return sorted(set(runtime_methods) | set(declared_methods))


def _project_model(project_context: ProjectContext) -> dict[str, object]:
    project_model = scan_project(project_context.root)
    project_model["context"] = project_context.to_payload()
    return project_model


def _events_by_run(project_context: ProjectContext) -> list[list[dict[str, object]]]:
    return [_events(project_context, run["run_id"]) for run in _runs(project_context)]


def _project_readiness(project_context: ProjectContext) -> dict[str, object]:
    analysis = _project_analysis_context(project_context)
    return build_project_readiness(
        analysis["project_model"],
        analysis["coverage"],
        analysis["runs"],
        analysis["issues_by_run"],
    )


def _project_audit(project_context: ProjectContext) -> dict[str, object]:
    analysis = _project_analysis_context(project_context)
    readiness = build_project_readiness(
        analysis["project_model"],
        analysis["coverage"],
        analysis["runs"],
        analysis["issues_by_run"],
    )
    return build_project_audit(
        analysis["project_model"],
        readiness,
        analysis["coverage"],
        analysis["runs"],
        analysis["issues_by_run"],
    )


def _project_integration_plan(project_context: ProjectContext) -> dict[str, object]:
    analysis = _project_analysis_context(project_context)
    readiness = build_project_readiness(
        analysis["project_model"],
        analysis["coverage"],
        analysis["runs"],
        analysis["issues_by_run"],
    )
    audit = build_project_audit(
        analysis["project_model"],
        readiness,
        analysis["coverage"],
        analysis["runs"],
        analysis["issues_by_run"],
    )
    return build_project_integration_plan(analysis["project_model"], analysis["coverage"], readiness, audit)


def _project_bootstrap(project_context: ProjectContext) -> dict[str, object]:
    analysis = _project_analysis_context(project_context)
    project_model = analysis["project_model"]
    coverage = analysis["coverage"]
    readiness = build_project_readiness(
        project_model,
        coverage,
        analysis["runs"],
        analysis["issues_by_run"],
    )
    audit = build_project_audit(
        project_model,
        readiness,
        coverage,
        analysis["runs"],
        analysis["issues_by_run"],
    )
    integration_plan = build_project_integration_plan(project_model, coverage, readiness, audit)
    run_profile_drafts = build_project_run_profiles(project_model, integration_plan)
    run_profiles = annotate_run_profiles(run_profile_drafts, load_saved_run_profiles(project_context.trace_dir))
    context = project_context.to_payload()
    run_preflight = build_project_run_preflight(
        context,
        run_profiles,
        load_run_confirmations(project_context.trace_dir),
    )
    run_execution_gate = build_project_run_execution_gate(
        context,
        run_profiles,
        run_preflight,
        load_run_final_confirmations(project_context.trace_dir),
    )
    runner_plan = build_project_runner_plan(context, run_profiles, run_execution_gate)
    execution_requests = build_project_execution_requests(
        context,
        run_profiles,
        runner_plan,
        load_execution_requests(project_context.trace_dir),
    )
    runner_sessions = build_project_runner_sessions(
        context,
        run_profiles,
        execution_requests,
        load_runner_sessions(project_context.trace_dir),
    )
    runner_launch_snapshots = build_project_runner_launch_snapshots(
        context,
        run_profiles,
        runner_sessions,
        load_runner_launch_snapshots(project_context.trace_dir),
    )
    runner_dry_runs = build_project_runner_dry_runs(
        context,
        run_profiles,
        runner_launch_snapshots,
        load_runner_dry_runs(project_context.trace_dir),
    )
    runner_real_executions = build_project_runner_real_executions(
        context,
        run_profiles,
        runner_dry_runs,
        load_runner_real_executions(project_context.trace_dir),
    )
    runner_cancel_timeout_real_apis = build_project_runner_cancel_timeout_real_apis(
        context,
        run_profiles,
        runner_real_executions,
    )
    runner_first_real_tests = build_project_runner_first_real_tests(
        context,
        run_profiles,
        runner_real_executions,
    )
    runner_process_lifecycles = build_project_runner_process_lifecycles(
        context,
        run_profiles,
        runner_real_executions,
    )
    runner_stream_captures = build_project_runner_stream_captures(
        context,
        run_profiles,
        runner_real_executions,
        runner_process_lifecycles,
    )
    runner_event_writers = build_project_runner_event_writers(
        context,
        run_profiles,
        runner_real_executions,
        runner_process_lifecycles,
        runner_stream_captures,
    )
    runner_audit_persistences = build_project_runner_audit_persistences(
        context,
        run_profiles,
        runner_real_executions,
        runner_process_lifecycles,
        runner_stream_captures,
        runner_event_writers,
    )
    runner_audit_integrity_replay_verifications = build_project_runner_audit_integrity_replay_verifications(
        context,
        run_profiles,
        runner_audit_persistences,
        runner_event_writers,
    )
    runner_verification_discrepancy_reports = build_project_runner_verification_discrepancy_reports(
        context,
        run_profiles,
        runner_audit_integrity_replay_verifications,
    )
    runner_launch_controls = build_project_runner_launch_controls(context, run_profiles, runner_dry_runs)
    runner_runtime_policies = build_project_runner_runtime_policies(context, run_profiles, runner_launch_controls)
    runner_execution_configs = build_project_runner_execution_configs(context, run_profiles, runner_runtime_policies)
    runner_execution_config_checks = build_project_runner_execution_config_checks(
        context,
        run_profiles,
        runner_execution_configs,
    )
    runner_config_schema_stabilizations = build_project_runner_config_schema_stabilizations(
        context,
        run_profiles,
        runner_execution_configs,
        runner_execution_config_checks,
    )
    runner_config_field_contract_views = build_project_runner_config_field_contract_views(
        context,
        runner_config_schema_stabilizations,
    )
    runner_config_compatibility_reports = build_project_runner_config_compatibility_reports(
        context,
        run_profiles,
        runner_config_schema_stabilizations,
        runner_execution_config_checks,
    )
    runner_config_remediation_summaries = build_project_runner_config_remediation_summaries(
        context,
        runner_config_compatibility_reports,
    )
    runner_config_field_coverage_indexes = build_project_runner_config_field_coverage_indexes(
        context,
        runner_config_field_contract_views,
        runner_config_compatibility_reports,
        runner_config_remediation_summaries,
    )
    runner_service_flag_audits = build_project_runner_service_flag_audits(
        context,
        run_profiles,
        runner_execution_config_checks,
    )
    runner_log_directory_policies = build_project_runner_log_directory_policies(
        context,
        run_profiles,
        runner_service_flag_audits,
    )
    runner_log_retention_policies = build_project_runner_log_retention_policies(
        context,
        run_profiles,
        runner_log_directory_policies,
    )
    runner_log_cleanup_previews = build_project_runner_log_cleanup_previews(
        context,
        run_profiles,
        runner_log_retention_policies,
    )
    runner_log_cleanup_confirmations = build_project_runner_log_cleanup_confirmations(
        context,
        run_profiles,
        runner_log_cleanup_previews,
    )
    runner_log_cleanup_audit_trails = build_project_runner_log_cleanup_audit_trails(
        context,
        run_profiles,
        runner_log_cleanup_confirmations,
    )
    runner_log_cleanup_execution_plans = build_project_runner_log_cleanup_execution_plans(
        context,
        run_profiles,
        runner_log_cleanup_audit_trails,
    )
    runner_governance_readiness = build_project_runner_governance_readiness(
        context,
        run_profiles,
        _runner_governance_layers(
            run_preflight,
            run_execution_gate,
            runner_plan,
            execution_requests,
            runner_sessions,
            runner_launch_snapshots,
            runner_dry_runs,
            runner_launch_controls,
            runner_runtime_policies,
            runner_execution_configs,
            runner_execution_config_checks,
            runner_config_schema_stabilizations,
            runner_config_field_contract_views,
            runner_config_compatibility_reports,
            runner_config_remediation_summaries,
            runner_config_field_coverage_indexes,
            runner_service_flag_audits,
            runner_log_directory_policies,
            runner_log_retention_policies,
            runner_log_cleanup_previews,
            runner_log_cleanup_confirmations,
            runner_log_cleanup_audit_trails,
            runner_log_cleanup_execution_plans,
        ),
    )
    runner_execution_adapter_contracts = build_project_runner_execution_adapter_contracts(
        context,
        run_profiles,
        runner_governance_readiness,
    )
    runner_launch_api_contracts = build_project_runner_launch_api_contracts(
        context,
        run_profiles,
        runner_execution_adapter_contracts,
    )
    runner_execution_adapter_reviews = build_project_runner_execution_adapter_reviews(
        context,
        run_profiles,
        runner_launch_api_contracts,
    )
    runner_final_block_matrices = build_project_runner_final_block_matrices(
        context,
        run_profiles,
        runner_execution_adapter_reviews,
    )
    runner_authorization_unlock_audits = build_project_runner_authorization_unlock_audits(
        context,
        run_profiles,
        runner_final_block_matrices,
    )
    runner_implementation_gap_checklists = build_project_runner_implementation_gap_checklists(
        context,
        run_profiles,
        runner_authorization_unlock_audits,
    )
    runner_cancel_timeout_contracts = build_project_runner_cancel_timeout_contracts(
        context,
        run_profiles,
        runner_implementation_gap_checklists,
    )
    runner_session_state_schemas = build_project_runner_session_state_schemas(
        context,
        run_profiles,
        runner_cancel_timeout_contracts,
    )
    runner_real_test_readiness = build_project_runner_real_test_readiness(
        context,
        run_profiles,
        runner_session_state_schemas,
    )
    runner_real_test_authorization_checklists = build_project_runner_real_test_authorization_checklists(
        context,
        run_profiles,
        runner_real_test_readiness,
    )
    runner_real_test_authorization_packages = build_project_runner_real_test_authorization_packages(
        context,
        run_profiles,
        runner_real_test_authorization_checklists,
    )
    runner_real_test_sandbox_policies = build_project_runner_real_test_sandbox_policies(
        context,
        run_profiles,
        runner_real_test_authorization_packages,
    )
    runner_real_test_final_checklists = build_project_runner_real_test_final_checklists(
        context,
        run_profiles,
        runner_real_test_sandbox_policies,
    )
    runner_real_test_ui_previews = build_project_runner_real_test_ui_previews(
        context,
        run_profiles,
        runner_real_test_final_checklists,
    )
    runner_real_execution_stage_boundary_reviews = build_project_runner_real_execution_stage_boundary_reviews(
        context,
        run_profiles,
        runner_real_test_ui_previews,
    )
    runner_real_execution_unlock_material_reviews = build_project_runner_real_execution_unlock_material_reviews(
        context,
        run_profiles,
        runner_real_execution_stage_boundary_reviews,
    )
    runner_real_execution_implementation_plans = build_project_runner_real_execution_implementation_plans(
        context,
        run_profiles,
        runner_real_execution_unlock_material_reviews,
    )
    runner_real_execution_scope_diff_audits = build_project_runner_real_execution_scope_diff_audits(
        context,
        run_profiles,
        runner_real_execution_implementation_plans,
    )
    runner_execution_adapter_implementation_audits = build_project_runner_execution_adapter_implementation_audits(
        context,
        run_profiles,
        runner_real_execution_scope_diff_audits,
    )
    runner_process_lifecycle_implementation_audits = build_project_runner_process_lifecycle_implementation_audits(
        context,
        run_profiles,
        runner_execution_adapter_implementation_audits,
        runner_process_lifecycles,
    )
    runner_stream_capture_implementation_audits = build_project_runner_stream_capture_implementation_audits(
        context,
        run_profiles,
        runner_process_lifecycle_implementation_audits,
        runner_stream_captures,
    )
    runner_event_writer_implementation_audits = build_project_runner_event_writer_implementation_audits(
        context,
        run_profiles,
        runner_stream_capture_implementation_audits,
        runner_event_writers,
    )
    runner_audit_persistence_implementation_audits = build_project_runner_audit_persistence_implementation_audits(
        context,
        run_profiles,
        runner_event_writer_implementation_audits,
        runner_audit_persistences,
    )
    runner_audit_integrity_replay_verification_audits = (
        build_project_runner_audit_integrity_replay_verification_audits(
            context,
            run_profiles,
            runner_audit_persistence_implementation_audits,
            runner_audit_integrity_replay_verifications,
        )
    )
    runner_verification_discrepancy_report_audits = build_project_runner_verification_discrepancy_report_audits(
        context,
        run_profiles,
        runner_audit_integrity_replay_verification_audits,
        runner_verification_discrepancy_reports,
    )
    runner_real_launch_final_gate_audits = build_project_runner_real_launch_final_gate_audits(
        context,
        run_profiles,
        runner_verification_discrepancy_report_audits,
    )
    runner_evidence_gap_indexes = build_project_runner_evidence_gap_indexes(
        context,
        run_profiles,
        runner_real_launch_final_gate_audits,
    )
    runner_development_path_anchors = build_project_runner_development_path_anchors(
        context,
        run_profiles,
        runner_evidence_gap_indexes,
    )
    runner_real_execution_touchpoint_inventories = build_project_runner_real_execution_touchpoint_inventories(
        context,
        run_profiles,
        runner_development_path_anchors,
    )
    runner_real_execution_touchpoint_coverage_indexes = build_project_runner_real_execution_touchpoint_coverage_indexes(
        context,
        run_profiles,
        runner_real_execution_touchpoint_inventories,
        runner_evidence_gap_indexes,
    )
    runner_real_execution_touchpoint_gap_links = build_project_runner_real_execution_touchpoint_gap_links(
        context,
        run_profiles,
        runner_real_execution_touchpoint_coverage_indexes,
        runner_evidence_gap_indexes,
    )
    runner_real_execution_touchpoint_unlock_matrices = (
        build_project_runner_real_execution_touchpoint_unlock_matrices(
            context,
            run_profiles,
            runner_real_execution_touchpoint_gap_links,
        )
    )
    runner_real_execution_unlock_phrase_readiness = build_project_runner_real_execution_unlock_phrase_readiness(
        context,
        run_profiles,
        runner_real_execution_touchpoint_unlock_matrices,
    )
    runner_real_execution_pre_unlock_evidence_packet_indexes = (
        build_project_runner_real_execution_pre_unlock_evidence_packet_indexes(
            context,
            run_profiles,
            runner_real_execution_touchpoint_gap_links,
            runner_real_execution_touchpoint_unlock_matrices,
            runner_real_execution_unlock_phrase_readiness,
        )
    )
    runner_real_execution_pre_unlock_review_checklists = (
        build_project_runner_real_execution_pre_unlock_review_checklists(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_evidence_packet_indexes,
        )
    )
    runner_real_execution_pre_unlock_reviewer_role_maps = (
        build_project_runner_real_execution_pre_unlock_reviewer_role_maps(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_review_checklists,
        )
    )
    runner_real_execution_pre_unlock_reviewer_signoff_rubrics = (
        build_project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_reviewer_role_maps,
        )
    )
    runner_real_execution_pre_unlock_signoff_evidence_bindings = (
        build_project_runner_real_execution_pre_unlock_signoff_evidence_bindings(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_reviewer_signoff_rubrics,
            runner_real_execution_pre_unlock_reviewer_role_maps,
            runner_real_execution_pre_unlock_review_checklists,
            runner_real_execution_pre_unlock_evidence_packet_indexes,
        )
    )
    runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers = (
        build_project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers(
            context,
            run_profiles,
            runner_development_path_anchors,
            runner_real_execution_pre_unlock_signoff_evidence_bindings,
            runner_real_execution_unlock_phrase_readiness,
            runner_real_execution_implementation_plans,
            runner_real_execution_scope_diff_audits,
        )
    )
    runner_real_execution_pre_unlock_round10_minimal_scope_previews = (
        build_project_runner_real_execution_pre_unlock_round10_minimal_scope_previews(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
            runner_execution_adapter_contracts,
            runner_real_execution_implementation_plans,
        )
    )
    runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts = (
        build_project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts(
            context,
            run_profiles,
            runner_real_execution_unlock_phrase_readiness,
            runner_real_execution_pre_unlock_round10_minimal_scope_previews,
        )
    )
    runner_real_execution_pre_round10_locked_handoff_summaries = (
        build_project_runner_real_execution_pre_round10_locked_handoff_summaries(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
            runner_real_execution_pre_unlock_round10_minimal_scope_previews,
            runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
        )
    )
    runner_real_execution_round10_explicit_unlock_checkpoints = (
        build_project_runner_real_execution_round10_explicit_unlock_checkpoints(
            context,
            run_profiles,
            runner_real_execution_pre_round10_locked_handoff_summaries,
            runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
        )
    )
    runner_real_execution_round10_unlock_decision_mirrors = (
        build_project_runner_real_execution_round10_unlock_decision_mirrors(
            context,
            run_profiles,
            runner_real_execution_round10_explicit_unlock_checkpoints,
            runner_real_execution_pre_round10_locked_handoff_summaries,
        )
    )
    return {
        "schema_version": "project_bootstrap.v1",
        "context": context,
        "project": project_model,
        "coverage": coverage,
        "onboarding": build_project_onboarding(project_model, coverage),
        "readiness": readiness,
        "audit": audit,
        "integration_plan": integration_plan,
        "run_profiles": run_profiles,
        "run_preflight": run_preflight,
        "run_execution_gate": run_execution_gate,
        "runner_plan": runner_plan,
        "execution_requests": execution_requests,
        "runner_sessions": runner_sessions,
        "runner_launch_snapshots": runner_launch_snapshots,
        "runner_dry_runs": runner_dry_runs,
        "runner_real_executions": runner_real_executions,
        "runner_cancel_timeout_real_apis": runner_cancel_timeout_real_apis,
        "runner_first_real_tests": runner_first_real_tests,
        "runner_process_lifecycles": runner_process_lifecycles,
        "runner_stream_captures": runner_stream_captures,
        "runner_event_writers": runner_event_writers,
        "runner_audit_persistences": runner_audit_persistences,
        "runner_audit_integrity_replay_verifications": runner_audit_integrity_replay_verifications,
        "runner_verification_discrepancy_reports": runner_verification_discrepancy_reports,
        "runner_launch_controls": runner_launch_controls,
        "runner_runtime_policies": runner_runtime_policies,
        "runner_execution_configs": runner_execution_configs,
        "runner_execution_config_checks": runner_execution_config_checks,
        "runner_config_schema_stabilizations": runner_config_schema_stabilizations,
        "runner_config_field_contract_views": runner_config_field_contract_views,
        "runner_config_compatibility_reports": runner_config_compatibility_reports,
        "runner_config_remediation_summaries": runner_config_remediation_summaries,
        "runner_config_field_coverage_indexes": runner_config_field_coverage_indexes,
        "runner_service_flag_audits": runner_service_flag_audits,
        "runner_log_directory_policies": runner_log_directory_policies,
        "runner_log_retention_policies": runner_log_retention_policies,
        "runner_log_cleanup_previews": runner_log_cleanup_previews,
        "runner_log_cleanup_confirmations": runner_log_cleanup_confirmations,
        "runner_log_cleanup_audit_trails": runner_log_cleanup_audit_trails,
        "runner_log_cleanup_execution_plans": runner_log_cleanup_execution_plans,
        "runner_governance_readiness": runner_governance_readiness,
        "runner_execution_adapter_contracts": runner_execution_adapter_contracts,
        "runner_launch_api_contracts": runner_launch_api_contracts,
        "runner_execution_adapter_reviews": runner_execution_adapter_reviews,
        "runner_final_block_matrices": runner_final_block_matrices,
        "runner_authorization_unlock_audits": runner_authorization_unlock_audits,
        "runner_implementation_gap_checklists": runner_implementation_gap_checklists,
        "runner_cancel_timeout_contracts": runner_cancel_timeout_contracts,
        "runner_session_state_schemas": runner_session_state_schemas,
        "runner_real_test_readiness": runner_real_test_readiness,
        "runner_real_test_authorization_checklists": runner_real_test_authorization_checklists,
        "runner_real_test_authorization_packages": runner_real_test_authorization_packages,
        "runner_real_test_sandbox_policies": runner_real_test_sandbox_policies,
        "runner_real_test_final_checklists": runner_real_test_final_checklists,
        "runner_real_test_ui_previews": runner_real_test_ui_previews,
        "runner_real_execution_stage_boundary_reviews": runner_real_execution_stage_boundary_reviews,
        "runner_real_execution_unlock_material_reviews": runner_real_execution_unlock_material_reviews,
        "runner_real_execution_implementation_plans": runner_real_execution_implementation_plans,
        "runner_real_execution_scope_diff_audits": runner_real_execution_scope_diff_audits,
        "runner_execution_adapter_implementation_audits": runner_execution_adapter_implementation_audits,
        "runner_process_lifecycle_implementation_audits": runner_process_lifecycle_implementation_audits,
        "runner_stream_capture_implementation_audits": runner_stream_capture_implementation_audits,
        "runner_event_writer_implementation_audits": runner_event_writer_implementation_audits,
        "runner_audit_persistence_implementation_audits": runner_audit_persistence_implementation_audits,
        "runner_audit_integrity_replay_verification_audits": runner_audit_integrity_replay_verification_audits,
        "runner_verification_discrepancy_report_audits": runner_verification_discrepancy_report_audits,
        "runner_real_launch_final_gate_audits": runner_real_launch_final_gate_audits,
        "runner_evidence_gap_indexes": runner_evidence_gap_indexes,
        "runner_development_path_anchors": runner_development_path_anchors,
        "runner_real_execution_touchpoint_inventories": runner_real_execution_touchpoint_inventories,
        "runner_real_execution_touchpoint_coverage_indexes": runner_real_execution_touchpoint_coverage_indexes,
        "runner_real_execution_touchpoint_gap_links": runner_real_execution_touchpoint_gap_links,
        "runner_real_execution_touchpoint_unlock_matrices": runner_real_execution_touchpoint_unlock_matrices,
        "runner_real_execution_unlock_phrase_readiness": runner_real_execution_unlock_phrase_readiness,
        "runner_real_execution_pre_unlock_evidence_packet_indexes": (
            runner_real_execution_pre_unlock_evidence_packet_indexes
        ),
        "runner_real_execution_pre_unlock_review_checklists": runner_real_execution_pre_unlock_review_checklists,
        "runner_real_execution_pre_unlock_reviewer_role_maps": runner_real_execution_pre_unlock_reviewer_role_maps,
        "runner_real_execution_pre_unlock_reviewer_signoff_rubrics": (
            runner_real_execution_pre_unlock_reviewer_signoff_rubrics
        ),
        "runner_real_execution_pre_unlock_signoff_evidence_bindings": (
            runner_real_execution_pre_unlock_signoff_evidence_bindings
        ),
        "runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers": (
            runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers
        ),
        "runner_real_execution_pre_unlock_round10_minimal_scope_previews": (
            runner_real_execution_pre_unlock_round10_minimal_scope_previews
        ),
        "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts": (
            runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts
        ),
        "runner_real_execution_pre_round10_locked_handoff_summaries": (
            runner_real_execution_pre_round10_locked_handoff_summaries
        ),
        "runner_real_execution_round10_explicit_unlock_checkpoints": (
            runner_real_execution_round10_explicit_unlock_checkpoints
        ),
        "runner_real_execution_round10_unlock_decision_mirrors": (
            runner_real_execution_round10_unlock_decision_mirrors
        ),
        "safety": {
            "executes_commands": False,
            "creates_process": False,
            "launch_enabled": False,
            "launch_api_available": False,
            "writes_user_project": False,
        },
    }


def _project_run_profiles(project_context: ProjectContext) -> dict[str, object]:
    drafts = _draft_project_run_profiles(project_context)
    saved_store = load_saved_run_profiles(project_context.trace_dir)
    return annotate_run_profiles(drafts, saved_store)


def _project_runner_governance_chain(project_context: ProjectContext) -> dict[str, dict[str, object]]:
    context = project_context.to_payload()
    run_profiles = _project_run_profiles(project_context)
    run_preflight = build_project_run_preflight(
        context,
        run_profiles,
        load_run_confirmations(project_context.trace_dir),
    )
    run_execution_gate = build_project_run_execution_gate(
        context,
        run_profiles,
        run_preflight,
        load_run_final_confirmations(project_context.trace_dir),
    )
    runner_plan = build_project_runner_plan(context, run_profiles, run_execution_gate)
    execution_requests = build_project_execution_requests(
        context,
        run_profiles,
        runner_plan,
        load_execution_requests(project_context.trace_dir),
    )
    runner_sessions = build_project_runner_sessions(
        context,
        run_profiles,
        execution_requests,
        load_runner_sessions(project_context.trace_dir),
    )
    runner_launch_snapshots = build_project_runner_launch_snapshots(
        context,
        run_profiles,
        runner_sessions,
        load_runner_launch_snapshots(project_context.trace_dir),
    )
    runner_dry_runs = build_project_runner_dry_runs(
        context,
        run_profiles,
        runner_launch_snapshots,
        load_runner_dry_runs(project_context.trace_dir),
    )
    runner_real_executions = build_project_runner_real_executions(
        context,
        run_profiles,
        runner_dry_runs,
        load_runner_real_executions(project_context.trace_dir),
    )
    runner_cancel_timeout_real_apis = build_project_runner_cancel_timeout_real_apis(
        context,
        run_profiles,
        runner_real_executions,
    )
    runner_first_real_tests = build_project_runner_first_real_tests(
        context,
        run_profiles,
        runner_real_executions,
    )
    runner_process_lifecycles = build_project_runner_process_lifecycles(
        context,
        run_profiles,
        runner_real_executions,
    )
    runner_stream_captures = build_project_runner_stream_captures(
        context,
        run_profiles,
        runner_real_executions,
        runner_process_lifecycles,
    )
    runner_event_writers = build_project_runner_event_writers(
        context,
        run_profiles,
        runner_real_executions,
        runner_process_lifecycles,
        runner_stream_captures,
    )
    runner_audit_persistences = build_project_runner_audit_persistences(
        context,
        run_profiles,
        runner_real_executions,
        runner_process_lifecycles,
        runner_stream_captures,
        runner_event_writers,
    )
    runner_audit_integrity_replay_verifications = build_project_runner_audit_integrity_replay_verifications(
        context,
        run_profiles,
        runner_audit_persistences,
        runner_event_writers,
    )
    runner_verification_discrepancy_reports = build_project_runner_verification_discrepancy_reports(
        context,
        run_profiles,
        runner_audit_integrity_replay_verifications,
    )
    runner_launch_controls = build_project_runner_launch_controls(context, run_profiles, runner_dry_runs)
    runner_runtime_policies = build_project_runner_runtime_policies(context, run_profiles, runner_launch_controls)
    runner_execution_configs = build_project_runner_execution_configs(context, run_profiles, runner_runtime_policies)
    runner_execution_config_checks = build_project_runner_execution_config_checks(
        context,
        run_profiles,
        runner_execution_configs,
    )
    runner_config_schema_stabilizations = build_project_runner_config_schema_stabilizations(
        context,
        run_profiles,
        runner_execution_configs,
        runner_execution_config_checks,
    )
    runner_config_field_contract_views = build_project_runner_config_field_contract_views(
        context,
        runner_config_schema_stabilizations,
    )
    runner_config_compatibility_reports = build_project_runner_config_compatibility_reports(
        context,
        run_profiles,
        runner_config_schema_stabilizations,
        runner_execution_config_checks,
    )
    runner_config_remediation_summaries = build_project_runner_config_remediation_summaries(
        context,
        runner_config_compatibility_reports,
    )
    runner_config_field_coverage_indexes = build_project_runner_config_field_coverage_indexes(
        context,
        runner_config_field_contract_views,
        runner_config_compatibility_reports,
        runner_config_remediation_summaries,
    )
    runner_service_flag_audits = build_project_runner_service_flag_audits(
        context,
        run_profiles,
        runner_execution_config_checks,
    )
    runner_log_directory_policies = build_project_runner_log_directory_policies(
        context,
        run_profiles,
        runner_service_flag_audits,
    )
    runner_log_retention_policies = build_project_runner_log_retention_policies(
        context,
        run_profiles,
        runner_log_directory_policies,
    )
    runner_log_cleanup_previews = build_project_runner_log_cleanup_previews(
        context,
        run_profiles,
        runner_log_retention_policies,
    )
    runner_log_cleanup_confirmations = build_project_runner_log_cleanup_confirmations(
        context,
        run_profiles,
        runner_log_cleanup_previews,
    )
    runner_log_cleanup_audit_trails = build_project_runner_log_cleanup_audit_trails(
        context,
        run_profiles,
        runner_log_cleanup_confirmations,
    )
    runner_log_cleanup_execution_plans = build_project_runner_log_cleanup_execution_plans(
        context,
        run_profiles,
        runner_log_cleanup_audit_trails,
    )
    return {
        "run_profiles": run_profiles,
        "run_preflight": run_preflight,
        "run_execution_gate": run_execution_gate,
        "runner_plan": runner_plan,
        "execution_requests": execution_requests,
        "runner_sessions": runner_sessions,
        "runner_launch_snapshots": runner_launch_snapshots,
        "runner_dry_runs": runner_dry_runs,
        "runner_real_executions": runner_real_executions,
        "runner_cancel_timeout_real_apis": runner_cancel_timeout_real_apis,
        "runner_first_real_tests": runner_first_real_tests,
        "runner_process_lifecycles": runner_process_lifecycles,
        "runner_stream_captures": runner_stream_captures,
        "runner_event_writers": runner_event_writers,
        "runner_audit_persistences": runner_audit_persistences,
        "runner_audit_integrity_replay_verifications": runner_audit_integrity_replay_verifications,
        "runner_verification_discrepancy_reports": runner_verification_discrepancy_reports,
        "runner_launch_controls": runner_launch_controls,
        "runner_runtime_policies": runner_runtime_policies,
        "runner_execution_configs": runner_execution_configs,
        "runner_execution_config_checks": runner_execution_config_checks,
        "runner_config_schema_stabilizations": runner_config_schema_stabilizations,
        "runner_config_field_contract_views": runner_config_field_contract_views,
        "runner_config_compatibility_reports": runner_config_compatibility_reports,
        "runner_config_remediation_summaries": runner_config_remediation_summaries,
        "runner_config_field_coverage_indexes": runner_config_field_coverage_indexes,
        "runner_service_flag_audits": runner_service_flag_audits,
        "runner_log_directory_policies": runner_log_directory_policies,
        "runner_log_retention_policies": runner_log_retention_policies,
        "runner_log_cleanup_previews": runner_log_cleanup_previews,
        "runner_log_cleanup_confirmations": runner_log_cleanup_confirmations,
        "runner_log_cleanup_audit_trails": runner_log_cleanup_audit_trails,
        "runner_log_cleanup_execution_plans": runner_log_cleanup_execution_plans,
    }


def _project_run_preflight(project_context: ProjectContext) -> dict[str, object]:
    return build_project_run_preflight(
        project_context.to_payload(),
        _project_run_profiles(project_context),
        load_run_confirmations(project_context.trace_dir),
    )


def _project_run_execution_gate(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    run_preflight = build_project_run_preflight(
        project_context.to_payload(),
        run_profiles,
        load_run_confirmations(project_context.trace_dir),
    )
    return build_project_run_execution_gate(
        project_context.to_payload(),
        run_profiles,
        run_preflight,
        load_run_final_confirmations(project_context.trace_dir),
    )


def _project_runner_plan(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    run_preflight = build_project_run_preflight(
        project_context.to_payload(),
        run_profiles,
        load_run_confirmations(project_context.trace_dir),
    )
    execution_gate = build_project_run_execution_gate(
        project_context.to_payload(),
        run_profiles,
        run_preflight,
        load_run_final_confirmations(project_context.trace_dir),
    )
    return build_project_runner_plan(project_context.to_payload(), run_profiles, execution_gate)


def _project_execution_requests(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    runner_plan = _project_runner_plan(project_context)
    return build_project_execution_requests(
        project_context.to_payload(),
        run_profiles,
        runner_plan,
        load_execution_requests(project_context.trace_dir),
    )


def _project_runner_sessions(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    execution_requests = _project_execution_requests(project_context)
    return build_project_runner_sessions(
        project_context.to_payload(),
        run_profiles,
        execution_requests,
        load_runner_sessions(project_context.trace_dir),
    )


def _project_runner_launch_snapshots(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    runner_sessions = _project_runner_sessions(project_context)
    return build_project_runner_launch_snapshots(
        project_context.to_payload(),
        run_profiles,
        runner_sessions,
        load_runner_launch_snapshots(project_context.trace_dir),
    )


def _project_runner_dry_runs(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    launch_snapshots = _project_runner_launch_snapshots(project_context)
    return build_project_runner_dry_runs(
        project_context.to_payload(),
        run_profiles,
        launch_snapshots,
        load_runner_dry_runs(project_context.trace_dir),
    )


def _project_runner_real_executions(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    dry_runs = _project_runner_dry_runs(project_context)
    return build_project_runner_real_executions(
        project_context.to_payload(),
        run_profiles,
        dry_runs,
        load_runner_real_executions(project_context.trace_dir),
    )


def _project_runner_cancel_timeout_real_apis(
    project_context: ProjectContext,
    active_processes: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    real_executions = _project_runner_real_executions(project_context)
    return build_project_runner_cancel_timeout_real_apis(
        project_context.to_payload(),
        run_profiles,
        real_executions,
        active_processes,
    )


def _project_runner_first_real_tests(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    real_executions = _project_runner_real_executions(project_context)
    return build_project_runner_first_real_tests(
        project_context.to_payload(),
        run_profiles,
        real_executions,
    )


def _project_runner_process_lifecycles(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    real_executions = _project_runner_real_executions(project_context)
    return build_project_runner_process_lifecycles(
        project_context.to_payload(),
        run_profiles,
        real_executions,
    )


def _project_runner_stream_captures(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    real_executions = _project_runner_real_executions(project_context)
    process_lifecycles = _project_runner_process_lifecycles(project_context)
    return build_project_runner_stream_captures(
        project_context.to_payload(),
        run_profiles,
        real_executions,
        process_lifecycles,
    )


def _project_runner_event_writers(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    real_executions = _project_runner_real_executions(project_context)
    process_lifecycles = _project_runner_process_lifecycles(project_context)
    stream_captures = _project_runner_stream_captures(project_context)
    return build_project_runner_event_writers(
        project_context.to_payload(),
        run_profiles,
        real_executions,
        process_lifecycles,
        stream_captures,
    )


def _project_runner_audit_persistences(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    real_executions = _project_runner_real_executions(project_context)
    process_lifecycles = _project_runner_process_lifecycles(project_context)
    stream_captures = _project_runner_stream_captures(project_context)
    event_writers = _project_runner_event_writers(project_context)
    return build_project_runner_audit_persistences(
        project_context.to_payload(),
        run_profiles,
        real_executions,
        process_lifecycles,
        stream_captures,
        event_writers,
    )


def _project_runner_audit_integrity_replay_verifications(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    audit_persistences = _project_runner_audit_persistences(project_context)
    event_writers = _project_runner_event_writers(project_context)
    return build_project_runner_audit_integrity_replay_verifications(
        project_context.to_payload(),
        run_profiles,
        audit_persistences,
        event_writers,
    )


def _project_runner_verification_discrepancy_reports(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    integrity_replay_verifications = _project_runner_audit_integrity_replay_verifications(project_context)
    return build_project_runner_verification_discrepancy_reports(
        project_context.to_payload(),
        run_profiles,
        integrity_replay_verifications,
    )


def _project_runner_launch_controls(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    dry_runs = _project_runner_dry_runs(project_context)
    return build_project_runner_launch_controls(project_context.to_payload(), run_profiles, dry_runs)


def _project_runner_runtime_policies(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    launch_controls = _project_runner_launch_controls(project_context)
    return build_project_runner_runtime_policies(project_context.to_payload(), run_profiles, launch_controls)


def _project_runner_execution_configs(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    runtime_policies = _project_runner_runtime_policies(project_context)
    return build_project_runner_execution_configs(project_context.to_payload(), run_profiles, runtime_policies)


def _project_runner_execution_config_checks(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    execution_configs = _project_runner_execution_configs(project_context)
    return build_project_runner_execution_config_checks(project_context.to_payload(), run_profiles, execution_configs)


def _project_runner_config_schema_stabilizations(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_governance_chain(project_context)["runner_config_schema_stabilizations"]


def _project_runner_config_field_contract_views(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_governance_chain(project_context)["runner_config_field_contract_views"]


def _project_runner_config_compatibility_reports(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_governance_chain(project_context)["runner_config_compatibility_reports"]


def _project_runner_config_remediation_summaries(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_governance_chain(project_context)["runner_config_remediation_summaries"]


def _project_runner_config_field_coverage_indexes(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_governance_chain(project_context)["runner_config_field_coverage_indexes"]


def _project_runner_service_flag_audits(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    config_checks = _project_runner_execution_config_checks(project_context)
    return build_project_runner_service_flag_audits(project_context.to_payload(), run_profiles, config_checks)


def _project_runner_log_directory_policies(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    service_flag_audits = _project_runner_service_flag_audits(project_context)
    return build_project_runner_log_directory_policies(project_context.to_payload(), run_profiles, service_flag_audits)


def _project_runner_log_retention_policies(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    log_directory_policies = _project_runner_log_directory_policies(project_context)
    return build_project_runner_log_retention_policies(project_context.to_payload(), run_profiles, log_directory_policies)


def _project_runner_log_cleanup_previews(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    log_retention_policies = _project_runner_log_retention_policies(project_context)
    return build_project_runner_log_cleanup_previews(project_context.to_payload(), run_profiles, log_retention_policies)


def _project_runner_log_cleanup_confirmations(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    cleanup_previews = _project_runner_log_cleanup_previews(project_context)
    return build_project_runner_log_cleanup_confirmations(project_context.to_payload(), run_profiles, cleanup_previews)


def _project_runner_log_cleanup_audit_trails(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    cleanup_confirmations = _project_runner_log_cleanup_confirmations(project_context)
    return build_project_runner_log_cleanup_audit_trails(project_context.to_payload(), run_profiles, cleanup_confirmations)


def _project_runner_log_cleanup_execution_plans(project_context: ProjectContext) -> dict[str, object]:
    run_profiles = _project_run_profiles(project_context)
    cleanup_audit_trails = _project_runner_log_cleanup_audit_trails(project_context)
    return build_project_runner_log_cleanup_execution_plans(
        project_context.to_payload(),
        run_profiles,
        cleanup_audit_trails,
    )


def _project_runner_governance_readiness(project_context: ProjectContext) -> dict[str, object]:
    chain = _project_runner_governance_chain(project_context)
    return build_project_runner_governance_readiness(
        project_context.to_payload(),
        chain["run_profiles"],
        _runner_governance_layers(
            chain["run_preflight"],
            chain["run_execution_gate"],
            chain["runner_plan"],
            chain["execution_requests"],
            chain["runner_sessions"],
            chain["runner_launch_snapshots"],
            chain["runner_dry_runs"],
            chain["runner_launch_controls"],
            chain["runner_runtime_policies"],
            chain["runner_execution_configs"],
            chain["runner_execution_config_checks"],
            chain["runner_config_schema_stabilizations"],
            chain["runner_config_field_contract_views"],
            chain["runner_config_compatibility_reports"],
            chain["runner_config_remediation_summaries"],
            chain["runner_config_field_coverage_indexes"],
            chain["runner_service_flag_audits"],
            chain["runner_log_directory_policies"],
            chain["runner_log_retention_policies"],
            chain["runner_log_cleanup_previews"],
            chain["runner_log_cleanup_confirmations"],
            chain["runner_log_cleanup_audit_trails"],
            chain["runner_log_cleanup_execution_plans"],
        ),
    )


def _project_runner_real_launch_audit_chain(project_context: ProjectContext) -> dict[str, dict[str, object]]:
    context = project_context.to_payload()
    chain = _project_runner_governance_chain(project_context)
    run_profiles = chain["run_profiles"]
    runner_governance_readiness = build_project_runner_governance_readiness(
        context,
        run_profiles,
        _runner_governance_layers(
            chain["run_preflight"],
            chain["run_execution_gate"],
            chain["runner_plan"],
            chain["execution_requests"],
            chain["runner_sessions"],
            chain["runner_launch_snapshots"],
            chain["runner_dry_runs"],
            chain["runner_launch_controls"],
            chain["runner_runtime_policies"],
            chain["runner_execution_configs"],
            chain["runner_execution_config_checks"],
            chain["runner_config_schema_stabilizations"],
            chain["runner_config_field_contract_views"],
            chain["runner_config_compatibility_reports"],
            chain["runner_config_remediation_summaries"],
            chain["runner_config_field_coverage_indexes"],
            chain["runner_service_flag_audits"],
            chain["runner_log_directory_policies"],
            chain["runner_log_retention_policies"],
            chain["runner_log_cleanup_previews"],
            chain["runner_log_cleanup_confirmations"],
            chain["runner_log_cleanup_audit_trails"],
            chain["runner_log_cleanup_execution_plans"],
        ),
    )
    runner_execution_adapter_contracts = build_project_runner_execution_adapter_contracts(
        context,
        run_profiles,
        runner_governance_readiness,
    )
    runner_launch_api_contracts = build_project_runner_launch_api_contracts(
        context,
        run_profiles,
        runner_execution_adapter_contracts,
    )
    runner_execution_adapter_reviews = build_project_runner_execution_adapter_reviews(
        context,
        run_profiles,
        runner_launch_api_contracts,
    )
    runner_final_block_matrices = build_project_runner_final_block_matrices(
        context,
        run_profiles,
        runner_execution_adapter_reviews,
    )
    runner_authorization_unlock_audits = build_project_runner_authorization_unlock_audits(
        context,
        run_profiles,
        runner_final_block_matrices,
    )
    runner_implementation_gap_checklists = build_project_runner_implementation_gap_checklists(
        context,
        run_profiles,
        runner_authorization_unlock_audits,
    )
    runner_cancel_timeout_contracts = build_project_runner_cancel_timeout_contracts(
        context,
        run_profiles,
        runner_implementation_gap_checklists,
    )
    runner_session_state_schemas = build_project_runner_session_state_schemas(
        context,
        run_profiles,
        runner_cancel_timeout_contracts,
    )
    runner_real_test_readiness = build_project_runner_real_test_readiness(
        context,
        run_profiles,
        runner_session_state_schemas,
    )
    runner_real_test_authorization_checklists = build_project_runner_real_test_authorization_checklists(
        context,
        run_profiles,
        runner_real_test_readiness,
    )
    runner_real_test_authorization_packages = build_project_runner_real_test_authorization_packages(
        context,
        run_profiles,
        runner_real_test_authorization_checklists,
    )
    runner_real_test_sandbox_policies = build_project_runner_real_test_sandbox_policies(
        context,
        run_profiles,
        runner_real_test_authorization_packages,
    )
    runner_real_test_final_checklists = build_project_runner_real_test_final_checklists(
        context,
        run_profiles,
        runner_real_test_sandbox_policies,
    )
    runner_real_test_ui_previews = build_project_runner_real_test_ui_previews(
        context,
        run_profiles,
        runner_real_test_final_checklists,
    )
    runner_real_execution_stage_boundary_reviews = build_project_runner_real_execution_stage_boundary_reviews(
        context,
        run_profiles,
        runner_real_test_ui_previews,
    )
    runner_real_execution_unlock_material_reviews = build_project_runner_real_execution_unlock_material_reviews(
        context,
        run_profiles,
        runner_real_execution_stage_boundary_reviews,
    )
    runner_real_execution_implementation_plans = build_project_runner_real_execution_implementation_plans(
        context,
        run_profiles,
        runner_real_execution_unlock_material_reviews,
    )
    runner_real_execution_scope_diff_audits = build_project_runner_real_execution_scope_diff_audits(
        context,
        run_profiles,
        runner_real_execution_implementation_plans,
    )
    runner_execution_adapter_implementation_audits = build_project_runner_execution_adapter_implementation_audits(
        context,
        run_profiles,
        runner_real_execution_scope_diff_audits,
    )
    runner_process_lifecycle_implementation_audits = build_project_runner_process_lifecycle_implementation_audits(
        context,
        run_profiles,
        runner_execution_adapter_implementation_audits,
        chain["runner_process_lifecycles"],
    )
    runner_stream_capture_implementation_audits = build_project_runner_stream_capture_implementation_audits(
        context,
        run_profiles,
        runner_process_lifecycle_implementation_audits,
        chain["runner_stream_captures"],
    )
    runner_event_writer_implementation_audits = build_project_runner_event_writer_implementation_audits(
        context,
        run_profiles,
        runner_stream_capture_implementation_audits,
        chain["runner_event_writers"],
    )
    runner_audit_persistence_implementation_audits = build_project_runner_audit_persistence_implementation_audits(
        context,
        run_profiles,
        runner_event_writer_implementation_audits,
        chain["runner_audit_persistences"],
    )
    runner_audit_integrity_replay_verification_audits = (
        build_project_runner_audit_integrity_replay_verification_audits(
            context,
            run_profiles,
            runner_audit_persistence_implementation_audits,
            chain["runner_audit_integrity_replay_verifications"],
        )
    )
    runner_verification_discrepancy_report_audits = build_project_runner_verification_discrepancy_report_audits(
        context,
        run_profiles,
        runner_audit_integrity_replay_verification_audits,
        chain["runner_verification_discrepancy_reports"],
    )
    runner_real_launch_final_gate_audits = build_project_runner_real_launch_final_gate_audits(
        context,
        run_profiles,
        runner_verification_discrepancy_report_audits,
    )
    runner_evidence_gap_indexes = build_project_runner_evidence_gap_indexes(
        context,
        run_profiles,
        runner_real_launch_final_gate_audits,
    )
    runner_development_path_anchors = build_project_runner_development_path_anchors(
        context,
        run_profiles,
        runner_evidence_gap_indexes,
    )
    runner_real_execution_touchpoint_inventories = build_project_runner_real_execution_touchpoint_inventories(
        context,
        run_profiles,
        runner_development_path_anchors,
    )
    runner_real_execution_touchpoint_coverage_indexes = build_project_runner_real_execution_touchpoint_coverage_indexes(
        context,
        run_profiles,
        runner_real_execution_touchpoint_inventories,
        runner_evidence_gap_indexes,
    )
    runner_real_execution_touchpoint_gap_links = build_project_runner_real_execution_touchpoint_gap_links(
        context,
        run_profiles,
        runner_real_execution_touchpoint_coverage_indexes,
        runner_evidence_gap_indexes,
    )
    runner_real_execution_touchpoint_unlock_matrices = (
        build_project_runner_real_execution_touchpoint_unlock_matrices(
            context,
            run_profiles,
            runner_real_execution_touchpoint_gap_links,
        )
    )
    runner_real_execution_unlock_phrase_readiness = build_project_runner_real_execution_unlock_phrase_readiness(
        context,
        run_profiles,
        runner_real_execution_touchpoint_unlock_matrices,
    )
    runner_real_execution_pre_unlock_evidence_packet_indexes = (
        build_project_runner_real_execution_pre_unlock_evidence_packet_indexes(
            context,
            run_profiles,
            runner_real_execution_touchpoint_gap_links,
            runner_real_execution_touchpoint_unlock_matrices,
            runner_real_execution_unlock_phrase_readiness,
        )
    )
    runner_real_execution_pre_unlock_review_checklists = (
        build_project_runner_real_execution_pre_unlock_review_checklists(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_evidence_packet_indexes,
        )
    )
    runner_real_execution_pre_unlock_reviewer_role_maps = (
        build_project_runner_real_execution_pre_unlock_reviewer_role_maps(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_review_checklists,
        )
    )
    runner_real_execution_pre_unlock_reviewer_signoff_rubrics = (
        build_project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_reviewer_role_maps,
        )
    )
    runner_real_execution_pre_unlock_signoff_evidence_bindings = (
        build_project_runner_real_execution_pre_unlock_signoff_evidence_bindings(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_reviewer_signoff_rubrics,
            runner_real_execution_pre_unlock_reviewer_role_maps,
            runner_real_execution_pre_unlock_review_checklists,
            runner_real_execution_pre_unlock_evidence_packet_indexes,
        )
    )
    runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers = (
        build_project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers(
            context,
            run_profiles,
            runner_development_path_anchors,
            runner_real_execution_pre_unlock_signoff_evidence_bindings,
            runner_real_execution_unlock_phrase_readiness,
            runner_real_execution_implementation_plans,
            runner_real_execution_scope_diff_audits,
        )
    )
    runner_real_execution_pre_unlock_round10_minimal_scope_previews = (
        build_project_runner_real_execution_pre_unlock_round10_minimal_scope_previews(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
            runner_execution_adapter_contracts,
            runner_real_execution_implementation_plans,
        )
    )
    runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts = (
        build_project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts(
            context,
            run_profiles,
            runner_real_execution_unlock_phrase_readiness,
            runner_real_execution_pre_unlock_round10_minimal_scope_previews,
        )
    )
    runner_real_execution_pre_round10_locked_handoff_summaries = (
        build_project_runner_real_execution_pre_round10_locked_handoff_summaries(
            context,
            run_profiles,
            runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
            runner_real_execution_pre_unlock_round10_minimal_scope_previews,
            runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
        )
    )
    runner_real_execution_round10_explicit_unlock_checkpoints = (
        build_project_runner_real_execution_round10_explicit_unlock_checkpoints(
            context,
            run_profiles,
            runner_real_execution_pre_round10_locked_handoff_summaries,
            runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
        )
    )
    runner_real_execution_round10_unlock_decision_mirrors = (
        build_project_runner_real_execution_round10_unlock_decision_mirrors(
            context,
            run_profiles,
            runner_real_execution_round10_explicit_unlock_checkpoints,
            runner_real_execution_pre_round10_locked_handoff_summaries,
        )
    )
    return {
        **chain,
        "runner_governance_readiness": runner_governance_readiness,
        "runner_execution_adapter_contracts": runner_execution_adapter_contracts,
        "runner_launch_api_contracts": runner_launch_api_contracts,
        "runner_execution_adapter_reviews": runner_execution_adapter_reviews,
        "runner_final_block_matrices": runner_final_block_matrices,
        "runner_authorization_unlock_audits": runner_authorization_unlock_audits,
        "runner_implementation_gap_checklists": runner_implementation_gap_checklists,
        "runner_cancel_timeout_contracts": runner_cancel_timeout_contracts,
        "runner_session_state_schemas": runner_session_state_schemas,
        "runner_real_test_readiness": runner_real_test_readiness,
        "runner_real_test_authorization_checklists": runner_real_test_authorization_checklists,
        "runner_real_test_authorization_packages": runner_real_test_authorization_packages,
        "runner_real_test_sandbox_policies": runner_real_test_sandbox_policies,
        "runner_real_test_final_checklists": runner_real_test_final_checklists,
        "runner_real_test_ui_previews": runner_real_test_ui_previews,
        "runner_real_execution_stage_boundary_reviews": runner_real_execution_stage_boundary_reviews,
        "runner_real_execution_unlock_material_reviews": runner_real_execution_unlock_material_reviews,
        "runner_real_execution_implementation_plans": runner_real_execution_implementation_plans,
        "runner_real_execution_scope_diff_audits": runner_real_execution_scope_diff_audits,
        "runner_execution_adapter_implementation_audits": runner_execution_adapter_implementation_audits,
        "runner_process_lifecycle_implementation_audits": runner_process_lifecycle_implementation_audits,
        "runner_stream_capture_implementation_audits": runner_stream_capture_implementation_audits,
        "runner_event_writer_implementation_audits": runner_event_writer_implementation_audits,
        "runner_audit_persistence_implementation_audits": runner_audit_persistence_implementation_audits,
        "runner_audit_integrity_replay_verification_audits": runner_audit_integrity_replay_verification_audits,
        "runner_verification_discrepancy_report_audits": runner_verification_discrepancy_report_audits,
        "runner_real_launch_final_gate_audits": runner_real_launch_final_gate_audits,
        "runner_evidence_gap_indexes": runner_evidence_gap_indexes,
        "runner_development_path_anchors": runner_development_path_anchors,
        "runner_real_execution_touchpoint_inventories": runner_real_execution_touchpoint_inventories,
        "runner_real_execution_touchpoint_coverage_indexes": runner_real_execution_touchpoint_coverage_indexes,
        "runner_real_execution_touchpoint_gap_links": runner_real_execution_touchpoint_gap_links,
        "runner_real_execution_touchpoint_unlock_matrices": runner_real_execution_touchpoint_unlock_matrices,
        "runner_real_execution_unlock_phrase_readiness": runner_real_execution_unlock_phrase_readiness,
        "runner_real_execution_pre_unlock_evidence_packet_indexes": (
            runner_real_execution_pre_unlock_evidence_packet_indexes
        ),
        "runner_real_execution_pre_unlock_review_checklists": runner_real_execution_pre_unlock_review_checklists,
        "runner_real_execution_pre_unlock_reviewer_role_maps": runner_real_execution_pre_unlock_reviewer_role_maps,
        "runner_real_execution_pre_unlock_reviewer_signoff_rubrics": (
            runner_real_execution_pre_unlock_reviewer_signoff_rubrics
        ),
        "runner_real_execution_pre_unlock_signoff_evidence_bindings": (
            runner_real_execution_pre_unlock_signoff_evidence_bindings
        ),
        "runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers": (
            runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers
        ),
        "runner_real_execution_pre_unlock_round10_minimal_scope_previews": (
            runner_real_execution_pre_unlock_round10_minimal_scope_previews
        ),
        "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts": (
            runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts
        ),
        "runner_real_execution_pre_round10_locked_handoff_summaries": (
            runner_real_execution_pre_round10_locked_handoff_summaries
        ),
        "runner_real_execution_round10_explicit_unlock_checkpoints": (
            runner_real_execution_round10_explicit_unlock_checkpoints
        ),
        "runner_real_execution_round10_unlock_decision_mirrors": (
            runner_real_execution_round10_unlock_decision_mirrors
        ),
    }


def _project_runner_execution_adapter_contracts(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_execution_adapter_contracts"]


def _project_runner_launch_api_contracts(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_launch_api_contracts"]


def _project_runner_execution_adapter_reviews(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_execution_adapter_reviews"]


def _project_runner_final_block_matrices(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_final_block_matrices"]


def _project_runner_authorization_unlock_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_authorization_unlock_audits"]


def _project_runner_implementation_gap_checklists(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_implementation_gap_checklists"]


def _project_runner_cancel_timeout_contracts(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_cancel_timeout_contracts"]


def _project_runner_session_state_schemas(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_session_state_schemas"]


def _project_runner_real_test_readiness(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_test_readiness"]


def _project_runner_real_test_authorization_checklists(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_test_authorization_checklists"]


def _project_runner_real_test_authorization_packages(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_test_authorization_packages"]


def _project_runner_real_test_sandbox_policies(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_test_sandbox_policies"]


def _project_runner_real_test_final_checklists(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_test_final_checklists"]


def _project_runner_real_test_ui_previews(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_test_ui_previews"]


def _project_runner_real_execution_stage_boundary_reviews(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_execution_stage_boundary_reviews"]


def _project_runner_real_execution_unlock_material_reviews(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_execution_unlock_material_reviews"]


def _project_runner_real_execution_implementation_plans(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_execution_implementation_plans"]


def _project_runner_real_execution_scope_diff_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_execution_scope_diff_audits"]


def _project_runner_execution_adapter_implementation_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_execution_adapter_implementation_audits"]


def _project_runner_process_lifecycle_implementation_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_process_lifecycle_implementation_audits"]


def _project_runner_stream_capture_implementation_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_stream_capture_implementation_audits"]


def _project_runner_event_writer_implementation_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_event_writer_implementation_audits"]


def _project_runner_audit_persistence_implementation_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_audit_persistence_implementation_audits"]


def _project_runner_audit_integrity_replay_verification_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_audit_integrity_replay_verification_audits"]


def _project_runner_verification_discrepancy_report_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_verification_discrepancy_report_audits"]


def _project_runner_real_launch_final_gate_audits(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_launch_final_gate_audits"]


def _project_runner_evidence_gap_indexes(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_evidence_gap_indexes"]


def _project_runner_development_path_anchors(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_development_path_anchors"]


def _project_runner_real_execution_touchpoint_inventories(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_execution_touchpoint_inventories"]


def _project_runner_real_execution_touchpoint_coverage_indexes(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_touchpoint_coverage_indexes"
    ]


def _project_runner_real_execution_touchpoint_gap_links(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)["runner_real_execution_touchpoint_gap_links"]


def _project_runner_real_execution_touchpoint_unlock_matrices(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_touchpoint_unlock_matrices"
    ]


def _project_runner_real_execution_unlock_phrase_readiness(project_context: ProjectContext) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_unlock_phrase_readiness"
    ]


def _project_runner_real_execution_pre_unlock_evidence_packet_indexes(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_evidence_packet_indexes"
    ]


def _project_runner_real_execution_pre_unlock_review_checklists(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_review_checklists"
    ]


def _project_runner_real_execution_pre_unlock_reviewer_role_maps(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_reviewer_role_maps"
    ]


def _project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_reviewer_signoff_rubrics"
    ]


def _project_runner_real_execution_pre_unlock_signoff_evidence_bindings(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_signoff_evidence_bindings"
    ]


def _project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers"
    ]


def _project_runner_real_execution_pre_unlock_round10_minimal_scope_previews(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_round10_minimal_scope_previews"
    ]


def _project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts"
    ]


def _project_runner_real_execution_pre_round10_locked_handoff_summaries(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_pre_round10_locked_handoff_summaries"
    ]


def _project_runner_real_execution_round10_explicit_unlock_checkpoints(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_round10_explicit_unlock_checkpoints"
    ]


def _project_runner_real_execution_round10_unlock_decision_mirrors(
    project_context: ProjectContext,
) -> dict[str, object]:
    return _project_runner_real_launch_audit_chain(project_context)[
        "runner_real_execution_round10_unlock_decision_mirrors"
    ]


def _runner_governance_layers(
    run_preflight: dict[str, object],
    run_execution_gate: dict[str, object],
    runner_plan: dict[str, object],
    execution_requests: dict[str, object],
    runner_sessions: dict[str, object],
    runner_launch_snapshots: dict[str, object],
    runner_dry_runs: dict[str, object],
    runner_launch_controls: dict[str, object],
    runner_runtime_policies: dict[str, object],
    runner_execution_configs: dict[str, object],
    runner_execution_config_checks: dict[str, object],
    runner_config_schema_stabilizations: dict[str, object],
    runner_config_field_contract_views: dict[str, object],
    runner_config_compatibility_reports: dict[str, object],
    runner_config_remediation_summaries: dict[str, object],
    runner_config_field_coverage_indexes: dict[str, object],
    runner_service_flag_audits: dict[str, object],
    runner_log_directory_policies: dict[str, object],
    runner_log_retention_policies: dict[str, object],
    runner_log_cleanup_previews: dict[str, object],
    runner_log_cleanup_confirmations: dict[str, object],
    runner_log_cleanup_audit_trails: dict[str, object],
    runner_log_cleanup_execution_plans: dict[str, object],
) -> dict[str, dict[str, object]]:
    return {
        "run_preflight": run_preflight,
        "run_execution_gate": run_execution_gate,
        "runner_plan": runner_plan,
        "execution_requests": execution_requests,
        "runner_sessions": runner_sessions,
        "runner_launch_snapshots": runner_launch_snapshots,
        "runner_dry_runs": runner_dry_runs,
        "runner_launch_controls": runner_launch_controls,
        "runner_runtime_policies": runner_runtime_policies,
        "runner_execution_configs": runner_execution_configs,
        "runner_execution_config_checks": runner_execution_config_checks,
        "runner_config_schema_stabilizations": runner_config_schema_stabilizations,
        "runner_config_field_contract_views": runner_config_field_contract_views,
        "runner_config_compatibility_reports": runner_config_compatibility_reports,
        "runner_config_remediation_summaries": runner_config_remediation_summaries,
        "runner_config_field_coverage_indexes": runner_config_field_coverage_indexes,
        "runner_service_flag_audits": runner_service_flag_audits,
        "runner_log_directory_policies": runner_log_directory_policies,
        "runner_log_retention_policies": runner_log_retention_policies,
        "runner_log_cleanup_previews": runner_log_cleanup_previews,
        "runner_log_cleanup_confirmations": runner_log_cleanup_confirmations,
        "runner_log_cleanup_audit_trails": runner_log_cleanup_audit_trails,
        "runner_log_cleanup_execution_plans": runner_log_cleanup_execution_plans,
    }


def _draft_project_run_profiles(project_context: ProjectContext) -> dict[str, object]:
    analysis = _project_analysis_context(project_context)
    readiness = build_project_readiness(
        analysis["project_model"],
        analysis["coverage"],
        analysis["runs"],
        analysis["issues_by_run"],
    )
    audit = build_project_audit(
        analysis["project_model"],
        readiness,
        analysis["coverage"],
        analysis["runs"],
        analysis["issues_by_run"],
    )
    integration_plan = build_project_integration_plan(analysis["project_model"], analysis["coverage"], readiness, audit)
    return build_project_run_profiles(analysis["project_model"], integration_plan)


def _find_run_profile(collection: dict[str, object], profile_id: str) -> dict[str, object] | None:
    profiles = collection.get("profiles")
    if not isinstance(profiles, list):
        return None
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("id") == profile_id:
            return profile
    return None


def _find_saved_run_profile(collection: dict[str, object], profile_id: str) -> dict[str, object] | None:
    profiles = collection.get("saved_profiles")
    if not isinstance(profiles, list):
        return None
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("id") == profile_id:
            return profile
    return None


def _find_preflight_report(collection: dict[str, object], profile_id: str) -> dict[str, object] | None:
    reports = collection.get("reports")
    if not isinstance(reports, list):
        return None
    for report in reports:
        if isinstance(report, dict) and report.get("profile_id") == profile_id:
            return report
    return None


def _find_profile_report(collection: dict[str, object], profile_id: str) -> dict[str, object] | None:
    reports = collection.get("reports")
    if not isinstance(reports, list):
        return None
    for report in reports:
        if isinstance(report, dict) and report.get("profile_id") == profile_id:
            return report
    return None


def _project_analysis_context(project_context: ProjectContext) -> dict[str, object]:
    project_model = _project_model(project_context)
    runs = _runs(project_context)
    events_by_run = [_events(project_context, run["run_id"]) for run in runs]
    coverage = build_project_coverage(project_model, events_by_run)
    issues_by_run = [
        {
            "run_id": run["run_id"],
            "label": run.get("label"),
            "issues": build_run_issues(events),
        }
        for run, events in zip(runs, events_by_run)
    ]
    return {
        "project_model": project_model,
        "runs": runs,
        "events_by_run": events_by_run,
        "coverage": coverage,
        "issues_by_run": issues_by_run,
    }


def _open_native_dialog(kind: str, initial_path: str | None, fallback_root: Path) -> str | None:
    initial_dir = _dialog_initial_dir(initial_path, fallback_root)
    if kind == "config":
        script = _open_file_dialog_script("选择 FlowTrace 配置文件", initial_dir, "JSON 配置 (*.json)|*.json|所有文件 (*.*)|*.*")
    elif kind in {"project", "trace", "directory"}:
        script = _open_directory_as_file_dialog_script("选择文件夹", initial_dir)
    else:
        raise ValueError(f"Unsupported dialog kind: {kind}")

    result = subprocess.run(
        [
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            "-NoProfile",
            "-STA",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "native file dialog failed").strip()
        raise ValueError(message)
    selected = result.stdout.strip()
    return selected or None


def _dialog_initial_dir(initial_path: str | None, fallback_root: Path) -> str:
    if initial_path:
        path = Path(initial_path).expanduser()
        if path.exists():
            if path.is_file():
                return str(path.parent.resolve())
            return str(path.resolve())
    return str(fallback_root.resolve())


def _open_file_dialog_script(title: str, initial_dir: str, file_filter: str) -> str:
    return rf"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$owner = New-Object System.Windows.Forms.Form
$owner.TopMost = $true
$owner.ShowInTaskbar = $false
$owner.WindowState = [System.Windows.Forms.FormWindowState]::Minimized
$owner.Size = New-Object System.Drawing.Size(1, 1)
$owner.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title = {json.dumps(title, ensure_ascii=False)}
$dialog.InitialDirectory = {json.dumps(initial_dir, ensure_ascii=False)}
$dialog.Filter = {json.dumps(file_filter, ensure_ascii=False)}
$dialog.CheckFileExists = $true
$dialog.CheckPathExists = $true
$result = $dialog.ShowDialog($owner)
$owner.Dispose()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
  Write-Output $dialog.FileName
}}
"""


def _open_directory_as_file_dialog_script(title: str, initial_dir: str) -> str:
    return rf"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$owner = New-Object System.Windows.Forms.Form
$owner.TopMost = $true
$owner.ShowInTaskbar = $false
$owner.WindowState = [System.Windows.Forms.FormWindowState]::Minimized
$owner.Size = New-Object System.Drawing.Size(1, 1)
$owner.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = {json.dumps(title, ensure_ascii=False)}
$dialog.SelectedPath = {json.dumps(initial_dir, ensure_ascii=False)}
$dialog.ShowNewFolderButton = $true
$result = $dialog.ShowDialog($owner)
$owner.Dispose()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
  Write-Output $dialog.SelectedPath
}}
"""


def _optional_string(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


if __name__ == "__main__":
    main()
