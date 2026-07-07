from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SAMPLES_ROOT = REPO_ROOT / "examples" / "realistic_projects"
SAMPLES = {
    "ecommerce_checkout": {"known": 5, "min_events": 10},
    "inventory_cli": {"known": 5, "min_events": 10},
    "support_ticket": {"known": 4, "min_events": 10},
}


def main() -> int:
    sys.path.insert(0, str(SRC_ROOT))

    from flowtrace.interpretation import build_project_coverage, build_run_issues
    from flowtrace.audit import build_project_audit
    from flowtrace.execution_request import build_project_execution_requests
    from flowtrace.integration_plan import build_project_integration_plan
    from flowtrace.readiness import build_project_readiness
    from flowtrace.run_confirmation_store import confirm_run_profile, revoke_run_confirmation
    from flowtrace.run_execution_gate import build_project_run_execution_gate
    from flowtrace.run_final_confirmation_store import confirm_run_final_execution, revoke_run_final_confirmation
    from flowtrace.run_preflight import build_project_run_preflight
    from flowtrace.run_profile import build_project_run_profiles
    from flowtrace.run_profile_store import annotate_run_profiles, remove_run_profile, save_run_profile
    from flowtrace.runner_dry_run import build_project_runner_dry_runs
    from flowtrace.runner_audit_persistence import build_project_runner_audit_persistences
    from flowtrace.runner_audit_persistence_implementation_audit import (
        build_project_runner_audit_persistence_implementation_audits,
    )
    from flowtrace.runner_audit_integrity_replay_verification import (
        build_project_runner_audit_integrity_replay_verifications,
    )
    from flowtrace.runner_audit_integrity_replay_verification_audit import (
        build_project_runner_audit_integrity_replay_verification_audits,
    )
    from flowtrace.runner_verification_discrepancy_report import (
        build_project_runner_verification_discrepancy_reports,
    )
    from flowtrace.runner_authorization_unlock_audit import build_project_runner_authorization_unlock_audits
    from flowtrace.runner_cancel_timeout_contract import build_project_runner_cancel_timeout_contracts
    from flowtrace.runner_cancel_timeout_real_api import build_project_runner_cancel_timeout_real_apis
    from flowtrace.runner_first_real_test import build_project_runner_first_real_tests
    from flowtrace.runner_execution_adapter_contract import build_project_runner_execution_adapter_contracts
    from flowtrace.runner_execution_adapter_implementation_audit import (
        build_project_runner_execution_adapter_implementation_audits,
    )
    from flowtrace.runner_execution_adapter_review import build_project_runner_execution_adapter_reviews
    from flowtrace.runner_event_writer_implementation_audit import (
        build_project_runner_event_writer_implementation_audits,
    )
    from flowtrace.runner_event_writer import build_project_runner_event_writers
    from flowtrace.runner_config_compatibility_report import build_project_runner_config_compatibility_reports
    from flowtrace.runner_config_field_contract_view import build_project_runner_config_field_contract_views
    from flowtrace.runner_config_field_coverage_index import build_project_runner_config_field_coverage_indexes
    from flowtrace.runner_config_remediation_summary import build_project_runner_config_remediation_summaries
    from flowtrace.runner_config_schema_stabilization import build_project_runner_config_schema_stabilizations
    from flowtrace.runner_execution_config import build_project_runner_execution_configs
    from flowtrace.runner_execution_config_check import build_project_runner_execution_config_checks
    from flowtrace.runner_final_block_matrix import build_project_runner_final_block_matrices
    from flowtrace.runner_governance_readiness import build_project_runner_governance_readiness
    from flowtrace.runner_implementation_gap_checklist import build_project_runner_implementation_gap_checklists
    from flowtrace.runner_launch_api_contract import build_project_runner_launch_api_contracts
    from flowtrace.runner_launch_control import build_project_runner_launch_controls
    from flowtrace.runner_log_cleanup_audit_trail import build_project_runner_log_cleanup_audit_trails
    from flowtrace.runner_log_cleanup_confirmation import build_project_runner_log_cleanup_confirmations
    from flowtrace.runner_log_cleanup_execution_plan import build_project_runner_log_cleanup_execution_plans
    from flowtrace.runner_log_cleanup_preview import build_project_runner_log_cleanup_previews
    from flowtrace.runner_log_directory_policy import build_project_runner_log_directory_policies
    from flowtrace.runner_log_retention_policy import build_project_runner_log_retention_policies
    from flowtrace.runner_plan import build_project_runner_plan
    from flowtrace.runner_process_lifecycle_implementation_audit import (
        build_project_runner_process_lifecycle_implementation_audits,
    )
    from flowtrace.runner_real_execution_adapter import launch_low_risk_sample_profile
    from flowtrace.runner_real_execution_store import (
        append_runner_real_execution,
        build_project_runner_real_executions,
        load_runner_real_executions,
    )
    from flowtrace.runner_process_lifecycle import build_project_runner_process_lifecycles
    from flowtrace.runner_stream_capture import build_project_runner_stream_captures
    from flowtrace.runner_runtime_policy import build_project_runner_runtime_policies
    from flowtrace.runner_service_flag_audit import build_project_runner_service_flag_audits
    from flowtrace.runner_session_state_schema import build_project_runner_session_state_schemas
    from flowtrace.runner_real_execution_implementation_plan import build_project_runner_real_execution_implementation_plans
    from flowtrace.runner_real_execution_scope_diff_audit import build_project_runner_real_execution_scope_diff_audits
    from flowtrace.runner_real_execution_stage_boundary_review import (
        build_project_runner_real_execution_stage_boundary_reviews,
    )
    from flowtrace.runner_real_execution_unlock_material_review import (
        build_project_runner_real_execution_unlock_material_reviews,
    )
    from flowtrace.runner_real_test_authorization_package import build_project_runner_real_test_authorization_packages
    from flowtrace.runner_real_test_authorization_checklist import build_project_runner_real_test_authorization_checklists
    from flowtrace.runner_real_test_final_checklist import build_project_runner_real_test_final_checklists
    from flowtrace.runner_real_test_readiness import build_project_runner_real_test_readiness
    from flowtrace.runner_real_test_sandbox_policy import build_project_runner_real_test_sandbox_policies
    from flowtrace.runner_real_test_ui_preview import build_project_runner_real_test_ui_previews
    from flowtrace.runner_stream_capture_implementation_audit import (
        build_project_runner_stream_capture_implementation_audits,
    )
    from flowtrace.runner_verification_discrepancy_report_audit import (
        build_project_runner_verification_discrepancy_report_audits,
    )
    from flowtrace.runner_real_launch_final_gate_audit import build_project_runner_real_launch_final_gate_audits
    from flowtrace.runner_evidence_gap_index import build_project_runner_evidence_gap_indexes
    from flowtrace.runner_development_path_anchor import build_project_runner_development_path_anchors
    from flowtrace.runner_real_execution_touchpoint_inventory import (
        build_project_runner_real_execution_touchpoint_inventories,
    )
    from flowtrace.runner_real_execution_touchpoint_coverage_index import (
        build_project_runner_real_execution_touchpoint_coverage_indexes,
    )
    from flowtrace.runner_real_execution_touchpoint_gap_link import (
        build_project_runner_real_execution_touchpoint_gap_links,
    )
    from flowtrace.runner_real_execution_touchpoint_unlock_matrix import (
        build_project_runner_real_execution_touchpoint_unlock_matrices,
    )
    from flowtrace.runner_real_execution_unlock_phrase_readiness import (
        build_project_runner_real_execution_unlock_phrase_readiness,
    )
    from flowtrace.runner_real_execution_pre_unlock_evidence_packet_index import (
        build_project_runner_real_execution_pre_unlock_evidence_packet_indexes,
    )
    from flowtrace.runner_real_execution_pre_unlock_review_checklist import (
        build_project_runner_real_execution_pre_unlock_review_checklists,
    )
    from flowtrace.runner_real_execution_pre_unlock_reviewer_role_map import (
        build_project_runner_real_execution_pre_unlock_reviewer_role_maps,
    )
    from flowtrace.runner_real_execution_pre_unlock_reviewer_signoff_rubric import (
        build_project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics,
    )
    from flowtrace.runner_real_execution_pre_unlock_signoff_evidence_binding import (
        build_project_runner_real_execution_pre_unlock_signoff_evidence_bindings,
    )
    from flowtrace.runner_real_execution_pre_unlock_implementation_entry_readiness_ledger import (
        build_project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
    )
    from flowtrace.runner_real_execution_pre_unlock_round10_minimal_scope_preview import (
        build_project_runner_real_execution_pre_unlock_round10_minimal_scope_previews,
    )
    from flowtrace.runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt import (
        build_project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
    )
    from flowtrace.runner_real_execution_pre_round10_locked_handoff_summary import (
        build_project_runner_real_execution_pre_round10_locked_handoff_summaries,
    )
    from flowtrace.runner_real_execution_round10_explicit_unlock_checkpoint import (
        build_project_runner_real_execution_round10_explicit_unlock_checkpoints,
    )
    from flowtrace.runner_real_execution_round10_unlock_decision_mirror import (
        build_project_runner_real_execution_round10_unlock_decision_mirrors,
    )
    from flowtrace.runner_launch_snapshot import build_project_runner_launch_snapshots
    from flowtrace.runner_session import build_project_runner_sessions
    from flowtrace.scanner import scan_project
    from flowtrace.storage import list_runs, read_events

    results = []
    failures = []
    for sample_name, expected in SAMPLES.items():
        root = SAMPLES_ROOT / sample_name
        trace_dir = root / ".flowtrace"
        project_model = scan_project(root)
        project_model["context"] = {"schema_version": "project_context.v1", "root": str(root), "trace_dir": str(trace_dir)}
        runs = list_runs(trace_dir)
        events_by_run = [read_events(run["run_id"], trace_dir) for run in runs]
        coverage = build_project_coverage(project_model, events_by_run)
        issues_by_run = [
            {"run_id": run["run_id"], "label": run.get("label"), "issues": build_run_issues(events)}
            for run, events in zip(runs, events_by_run)
        ]
        readiness = build_project_readiness(project_model, coverage, runs, issues_by_run)
        audit = build_project_audit(project_model, readiness, coverage, runs, issues_by_run)
        integration_plan = build_project_integration_plan(project_model, coverage, readiness, audit)
        run_profiles = build_project_run_profiles(project_model, integration_plan)
        run_preflight = build_project_run_preflight(project_model["context"], run_profiles)
        run_execution_gate = build_project_run_execution_gate(project_model["context"], run_profiles, run_preflight)
        runner_plan = build_project_runner_plan(project_model["context"], run_profiles, run_execution_gate)
        execution_requests = build_project_execution_requests(project_model["context"], run_profiles, runner_plan)
        runner_sessions = build_project_runner_sessions(project_model["context"], run_profiles, execution_requests)
        runner_launch_snapshots = build_project_runner_launch_snapshots(
            project_model["context"],
            run_profiles,
            runner_sessions,
        )
        runner_dry_runs = build_project_runner_dry_runs(project_model["context"], run_profiles, runner_launch_snapshots)
        runner_real_executions = build_project_runner_real_executions(
            project_model["context"],
            run_profiles,
            runner_dry_runs,
        )
        runner_cancel_timeout_real_apis = build_project_runner_cancel_timeout_real_apis(
            project_model["context"],
            run_profiles,
            runner_real_executions,
        )
        runner_first_real_tests = build_project_runner_first_real_tests(
            project_model["context"],
            run_profiles,
            runner_real_executions,
        )
        runner_process_lifecycles = build_project_runner_process_lifecycles(
            project_model["context"],
            run_profiles,
            runner_real_executions,
        )
        runner_stream_captures = build_project_runner_stream_captures(
            project_model["context"],
            run_profiles,
            runner_real_executions,
            runner_process_lifecycles,
        )
        runner_event_writers = build_project_runner_event_writers(
            project_model["context"],
            run_profiles,
            runner_real_executions,
            runner_process_lifecycles,
            runner_stream_captures,
        )
        runner_audit_persistences = build_project_runner_audit_persistences(
            project_model["context"],
            run_profiles,
            runner_real_executions,
            runner_process_lifecycles,
            runner_stream_captures,
            runner_event_writers,
        )
        runner_audit_integrity_replay_verifications = build_project_runner_audit_integrity_replay_verifications(
            project_model["context"],
            run_profiles,
            runner_audit_persistences,
            runner_event_writers,
        )
        runner_verification_discrepancy_reports = build_project_runner_verification_discrepancy_reports(
            project_model["context"],
            run_profiles,
            runner_audit_integrity_replay_verifications,
        )
        runner_launch_controls = build_project_runner_launch_controls(project_model["context"], run_profiles, runner_dry_runs)
        runner_runtime_policies = build_project_runner_runtime_policies(
            project_model["context"],
            run_profiles,
            runner_launch_controls,
        )
        runner_execution_configs = build_project_runner_execution_configs(
            project_model["context"],
            run_profiles,
            runner_runtime_policies,
        )
        runner_execution_config_checks = build_project_runner_execution_config_checks(
            project_model["context"],
            run_profiles,
            runner_execution_configs,
        )
        runner_config_schema_stabilizations = build_project_runner_config_schema_stabilizations(
            project_model["context"],
            run_profiles,
            runner_execution_configs,
            runner_execution_config_checks,
        )
        runner_config_field_contract_views = build_project_runner_config_field_contract_views(
            project_model["context"],
            runner_config_schema_stabilizations,
        )
        runner_config_compatibility_reports = build_project_runner_config_compatibility_reports(
            project_model["context"],
            run_profiles,
            runner_config_schema_stabilizations,
            runner_execution_config_checks,
        )
        runner_config_remediation_summaries = build_project_runner_config_remediation_summaries(
            project_model["context"],
            runner_config_compatibility_reports,
        )
        runner_config_field_coverage_indexes = build_project_runner_config_field_coverage_indexes(
            project_model["context"],
            runner_config_field_contract_views,
            runner_config_compatibility_reports,
            runner_config_remediation_summaries,
        )
        runner_service_flag_audits = build_project_runner_service_flag_audits(
            project_model["context"],
            run_profiles,
            runner_execution_config_checks,
        )
        runner_log_directory_policies = build_project_runner_log_directory_policies(
            project_model["context"],
            run_profiles,
            runner_service_flag_audits,
        )
        runner_log_retention_policies = build_project_runner_log_retention_policies(
            project_model["context"],
            run_profiles,
            runner_log_directory_policies,
        )
        runner_log_cleanup_previews = build_project_runner_log_cleanup_previews(
            project_model["context"],
            run_profiles,
            runner_log_retention_policies,
        )
        runner_log_cleanup_confirmations = build_project_runner_log_cleanup_confirmations(
            project_model["context"],
            run_profiles,
            runner_log_cleanup_previews,
        )
        runner_log_cleanup_audit_trails = build_project_runner_log_cleanup_audit_trails(
            project_model["context"],
            run_profiles,
            runner_log_cleanup_confirmations,
        )
        runner_log_cleanup_execution_plans = build_project_runner_log_cleanup_execution_plans(
            project_model["context"],
            run_profiles,
            runner_log_cleanup_audit_trails,
        )
        runner_governance_readiness = build_project_runner_governance_readiness(
            project_model["context"],
            run_profiles,
            _governance_layers(
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
            project_model["context"],
            run_profiles,
            runner_governance_readiness,
        )
        runner_launch_api_contracts = build_project_runner_launch_api_contracts(
            project_model["context"],
            run_profiles,
            runner_execution_adapter_contracts,
        )
        runner_execution_adapter_reviews = build_project_runner_execution_adapter_reviews(
            project_model["context"],
            run_profiles,
            runner_launch_api_contracts,
        )
        runner_final_block_matrices = build_project_runner_final_block_matrices(
            project_model["context"],
            run_profiles,
            runner_execution_adapter_reviews,
        )
        runner_authorization_unlock_audits = build_project_runner_authorization_unlock_audits(
            project_model["context"],
            run_profiles,
            runner_final_block_matrices,
        )
        runner_implementation_gap_checklists = build_project_runner_implementation_gap_checklists(
            project_model["context"],
            run_profiles,
            runner_authorization_unlock_audits,
        )
        runner_cancel_timeout_contracts = build_project_runner_cancel_timeout_contracts(
            project_model["context"],
            run_profiles,
            runner_implementation_gap_checklists,
        )
        runner_session_state_schemas = build_project_runner_session_state_schemas(
            project_model["context"],
            run_profiles,
            runner_cancel_timeout_contracts,
        )
        runner_real_test_readiness = build_project_runner_real_test_readiness(
            project_model["context"],
            run_profiles,
            runner_session_state_schemas,
        )
        runner_real_test_authorization_checklists = build_project_runner_real_test_authorization_checklists(
            project_model["context"],
            run_profiles,
            runner_real_test_readiness,
        )
        runner_real_test_authorization_packages = build_project_runner_real_test_authorization_packages(
            project_model["context"],
            run_profiles,
            runner_real_test_authorization_checklists,
        )
        runner_real_test_sandbox_policies = build_project_runner_real_test_sandbox_policies(
            project_model["context"],
            run_profiles,
            runner_real_test_authorization_packages,
        )
        runner_real_test_final_checklists = build_project_runner_real_test_final_checklists(
            project_model["context"],
            run_profiles,
            runner_real_test_sandbox_policies,
        )
        runner_real_test_ui_previews = build_project_runner_real_test_ui_previews(
            project_model["context"],
            run_profiles,
            runner_real_test_final_checklists,
        )
        runner_real_execution_stage_boundary_reviews = build_project_runner_real_execution_stage_boundary_reviews(
            project_model["context"],
            run_profiles,
            runner_real_test_ui_previews,
        )
        runner_real_execution_unlock_material_reviews = build_project_runner_real_execution_unlock_material_reviews(
            project_model["context"],
            run_profiles,
            runner_real_execution_stage_boundary_reviews,
        )
        runner_real_execution_implementation_plans = build_project_runner_real_execution_implementation_plans(
            project_model["context"],
            run_profiles,
            runner_real_execution_unlock_material_reviews,
        )
        runner_real_execution_scope_diff_audits = build_project_runner_real_execution_scope_diff_audits(
            project_model["context"],
            run_profiles,
            runner_real_execution_implementation_plans,
        )
        runner_execution_adapter_implementation_audits = build_project_runner_execution_adapter_implementation_audits(
            project_model["context"],
            run_profiles,
            runner_real_execution_scope_diff_audits,
        )
        runner_process_lifecycle_implementation_audits = build_project_runner_process_lifecycle_implementation_audits(
            project_model["context"],
            run_profiles,
            runner_execution_adapter_implementation_audits,
            runner_process_lifecycles,
        )
        runner_stream_capture_implementation_audits = build_project_runner_stream_capture_implementation_audits(
            project_model["context"],
            run_profiles,
            runner_process_lifecycle_implementation_audits,
            runner_stream_captures,
        )
        runner_event_writer_implementation_audits = build_project_runner_event_writer_implementation_audits(
            project_model["context"],
            run_profiles,
            runner_stream_capture_implementation_audits,
            runner_event_writers,
        )
        runner_audit_persistence_implementation_audits = build_project_runner_audit_persistence_implementation_audits(
            project_model["context"],
            run_profiles,
            runner_event_writer_implementation_audits,
            runner_audit_persistences,
        )
        runner_audit_integrity_replay_verification_audits = (
            build_project_runner_audit_integrity_replay_verification_audits(
                project_model["context"],
                run_profiles,
                runner_audit_persistence_implementation_audits,
                runner_audit_integrity_replay_verifications,
            )
        )
        runner_verification_discrepancy_report_audits = build_project_runner_verification_discrepancy_report_audits(
            project_model["context"],
            run_profiles,
            runner_audit_integrity_replay_verification_audits,
            runner_verification_discrepancy_reports,
        )
        runner_real_launch_final_gate_audits = build_project_runner_real_launch_final_gate_audits(
            project_model["context"],
            run_profiles,
            runner_verification_discrepancy_report_audits,
        )
        runner_evidence_gap_indexes = build_project_runner_evidence_gap_indexes(
            project_model["context"],
            run_profiles,
            runner_real_launch_final_gate_audits,
        )
        runner_development_path_anchors = build_project_runner_development_path_anchors(
            project_model["context"],
            run_profiles,
            runner_evidence_gap_indexes,
        )
        runner_real_execution_touchpoint_inventories = build_project_runner_real_execution_touchpoint_inventories(
            project_model["context"],
            run_profiles,
            runner_development_path_anchors,
        )
        runner_real_execution_touchpoint_coverage_indexes = (
            build_project_runner_real_execution_touchpoint_coverage_indexes(
                project_model["context"],
                run_profiles,
                runner_real_execution_touchpoint_inventories,
                runner_evidence_gap_indexes,
            )
        )
        runner_real_execution_touchpoint_gap_links = build_project_runner_real_execution_touchpoint_gap_links(
            project_model["context"],
            run_profiles,
            runner_real_execution_touchpoint_coverage_indexes,
            runner_evidence_gap_indexes,
        )
        runner_real_execution_touchpoint_unlock_matrices = (
            build_project_runner_real_execution_touchpoint_unlock_matrices(
                project_model["context"],
                run_profiles,
                runner_real_execution_touchpoint_gap_links,
            )
        )
        runner_real_execution_unlock_phrase_readiness = build_project_runner_real_execution_unlock_phrase_readiness(
            project_model["context"],
            run_profiles,
            runner_real_execution_touchpoint_unlock_matrices,
        )
        runner_real_execution_pre_unlock_evidence_packet_indexes = (
            build_project_runner_real_execution_pre_unlock_evidence_packet_indexes(
                project_model["context"],
                run_profiles,
                runner_real_execution_touchpoint_gap_links,
                runner_real_execution_touchpoint_unlock_matrices,
                runner_real_execution_unlock_phrase_readiness,
            )
        )
        runner_real_execution_pre_unlock_review_checklists = (
            build_project_runner_real_execution_pre_unlock_review_checklists(
                project_model["context"],
                run_profiles,
                runner_real_execution_pre_unlock_evidence_packet_indexes,
            )
        )
        runner_real_execution_pre_unlock_reviewer_role_maps = (
            build_project_runner_real_execution_pre_unlock_reviewer_role_maps(
                project_model["context"],
                run_profiles,
                runner_real_execution_pre_unlock_review_checklists,
            )
        )
        runner_real_execution_pre_unlock_reviewer_signoff_rubrics = (
            build_project_runner_real_execution_pre_unlock_reviewer_signoff_rubrics(
                project_model["context"],
                run_profiles,
                runner_real_execution_pre_unlock_reviewer_role_maps,
            )
        )
        runner_real_execution_pre_unlock_signoff_evidence_bindings = (
            build_project_runner_real_execution_pre_unlock_signoff_evidence_bindings(
                project_model["context"],
                run_profiles,
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics,
                runner_real_execution_pre_unlock_reviewer_role_maps,
                runner_real_execution_pre_unlock_review_checklists,
                runner_real_execution_pre_unlock_evidence_packet_indexes,
            )
        )
        runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers = (
            build_project_runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers(
                project_model["context"],
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
                project_model["context"],
                run_profiles,
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
                runner_execution_adapter_contracts,
                runner_real_execution_implementation_plans,
            )
        )
        runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts = (
            build_project_runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts(
                project_model["context"],
                run_profiles,
                runner_real_execution_unlock_phrase_readiness,
                runner_real_execution_pre_unlock_round10_minimal_scope_previews,
            )
        )
        runner_real_execution_pre_round10_locked_handoff_summaries = (
            build_project_runner_real_execution_pre_round10_locked_handoff_summaries(
                project_model["context"],
                run_profiles,
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers,
                runner_real_execution_pre_unlock_round10_minimal_scope_previews,
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
            )
        )
        runner_real_execution_round10_explicit_unlock_checkpoints = (
            build_project_runner_real_execution_round10_explicit_unlock_checkpoints(
                project_model["context"],
                run_profiles,
                runner_real_execution_pre_round10_locked_handoff_summaries,
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts,
            )
        )
        runner_real_execution_round10_unlock_decision_mirrors = (
            build_project_runner_real_execution_round10_unlock_decision_mirrors(
                project_model["context"],
                run_profiles,
                runner_real_execution_round10_explicit_unlock_checkpoints,
                runner_real_execution_pre_round10_locked_handoff_summaries,
            )
        )
        event_count = sum(len(events) for events in events_by_run)
        result = {
            "sample": sample_name,
            "runs": len(runs),
            "events": event_count,
            "known": coverage["summary"]["known_method_count"],
            "covered": coverage["summary"]["covered_method_count"],
            "runtime_only": coverage["runtime_only_methods"],
            "status": readiness["status"],
            "missing_contracts": readiness["summary"]["missing_contract_count"],
            "errors": readiness["summary"]["error_count"],
            "warnings": readiness["summary"]["warning_count"],
            "audit_status": audit["status"],
            "findings": audit["summary"]["finding_count"],
            "audit_errors": audit["summary"]["error_count"],
            "audit_warnings": audit["summary"]["warning_count"],
            "findings_with_location": sum(1 for item in audit["findings"] if item.get("location")),
            "integration_plan_status": integration_plan["status"],
            "integration_plan_phases": len(integration_plan["phases"]),
            "integration_plan_targets": len(integration_plan["execution_targets"]),
            "integration_plan_gates": len(integration_plan["validation_gates"]),
            "integration_next_action": bool(integration_plan["next_action"]),
            "run_profile_count": run_profiles["summary"]["profile_count"],
            "run_profile_executable_count": run_profiles["summary"]["executable_count"],
            "run_profile_safe": not run_profiles["safety"]["executes_commands"]
            and run_profiles["safety"]["requires_user_confirmation"]
            and not run_profiles["safety"]["writes_user_project"],
            "run_preflight_status": run_preflight["status"],
            "run_preflight_safe": not run_preflight["safety"]["executes_commands"]
            and run_preflight["safety"]["requires_user_confirmation"]
            and not run_preflight["safety"]["allows_shell_string"],
            "run_execution_gate_status": run_execution_gate["status"],
            "run_execution_gate_safe": not run_execution_gate["safety"]["executes_commands"]
            and run_execution_gate["safety"]["requires_preflight_confirmation"]
            and run_execution_gate["safety"]["requires_final_confirmation"]
            and not run_execution_gate["safety"]["writes_user_project"],
            "runner_plan_status": runner_plan["status"],
            "runner_plan_safe": not runner_plan["safety"]["executes_commands"]
            and not runner_plan["safety"]["runner_implemented"]
            and runner_plan["safety"]["requires_final_confirmation"]
            and not runner_plan["safety"]["writes_user_project"],
            "execution_request_status": execution_requests["status"],
            "execution_request_safe": not execution_requests["safety"]["executes_commands"]
            and not execution_requests["safety"]["runner_implemented"]
            and execution_requests["safety"]["request_store_only"]
            and execution_requests["safety"]["requires_second_confirmation"]
            and not execution_requests["safety"]["writes_user_project"],
            "runner_session_status": runner_sessions["status"],
            "runner_session_safe": not runner_sessions["safety"]["executes_commands"]
            and not runner_sessions["safety"]["creates_process"]
            and not runner_sessions["safety"]["runner_implemented"]
            and runner_sessions["safety"]["skeleton_only"]
            and runner_sessions["safety"]["session_store_only"]
            and runner_sessions["safety"]["requires_second_confirmed_request"]
            and not runner_sessions["safety"]["writes_user_project"],
            "runner_launch_snapshot_status": runner_launch_snapshots["status"],
            "runner_launch_snapshot_safe": not runner_launch_snapshots["safety"]["executes_commands"]
            and not runner_launch_snapshots["safety"]["creates_process"]
            and not runner_launch_snapshots["safety"]["runner_implemented"]
            and not runner_launch_snapshots["safety"]["launch_enabled"]
            and runner_launch_snapshots["safety"]["snapshot_store_only"]
            and runner_launch_snapshots["safety"]["requires_runner_session_drafted"]
            and not runner_launch_snapshots["safety"]["writes_user_project"],
            "runner_dry_run_status": runner_dry_runs["status"],
            "runner_dry_run_safe": not runner_dry_runs["safety"]["executes_commands"]
            and not runner_dry_runs["safety"]["creates_process"]
            and not runner_dry_runs["safety"]["runner_implemented"]
            and runner_dry_runs["safety"]["dry_run_only"]
            and not runner_dry_runs["safety"]["launch_enabled"]
            and runner_dry_runs["safety"]["dry_run_store_only"]
            and runner_dry_runs["safety"]["requires_launch_snapshot"]
            and not runner_dry_runs["safety"]["writes_user_project"],
            "runner_launch_control_status": runner_launch_controls["status"],
            "runner_launch_control_safe": not runner_launch_controls["safety"]["executes_commands"]
            and not runner_launch_controls["safety"]["creates_process"]
            and not runner_launch_controls["safety"]["runner_implemented"]
            and not runner_launch_controls["safety"]["launch_enabled"]
            and not runner_launch_controls["safety"]["launch_api_available"]
            and runner_launch_controls["safety"]["requires_future_explicit_enablement"]
            and not runner_launch_controls["safety"]["writes_user_project"],
            "runner_runtime_policy_status": runner_runtime_policies["status"],
            "runner_runtime_policy_safe": not runner_runtime_policies["safety"]["executes_commands"]
            and not runner_runtime_policies["safety"]["creates_process"]
            and not runner_runtime_policies["safety"]["runner_implemented"]
            and not runner_runtime_policies["safety"]["launch_enabled"]
            and not runner_runtime_policies["safety"]["launch_api_available"]
            and runner_runtime_policies["safety"]["runtime_policy_only"]
            and not runner_runtime_policies["safety"]["writes_user_project"],
            "runner_execution_config_status": runner_execution_configs["status"],
            "runner_execution_config_safe": not runner_execution_configs["safety"]["executes_commands"]
            and not runner_execution_configs["safety"]["creates_process"]
            and not runner_execution_configs["safety"]["runner_implemented"]
            and not runner_execution_configs["safety"]["launch_enabled"]
            and not runner_execution_configs["safety"]["launch_api_available"]
            and runner_execution_configs["safety"]["execution_config_only"]
            and not runner_execution_configs["safety"]["writes_user_project"],
            "runner_execution_config_check_status": runner_execution_config_checks["status"],
            "runner_execution_config_check_safe": not runner_execution_config_checks["safety"]["executes_commands"]
            and not runner_execution_config_checks["safety"]["creates_process"]
            and not runner_execution_config_checks["safety"]["runner_implemented"]
            and not runner_execution_config_checks["safety"]["launch_enabled"]
            and not runner_execution_config_checks["safety"]["launch_api_available"]
            and runner_execution_config_checks["safety"]["config_check_only"]
            and not runner_execution_config_checks["safety"]["writes_user_project"]
            and not runner_execution_config_checks["safety"]["creates_config_file"],
            "runner_config_schema_stabilization_status": runner_config_schema_stabilizations["status"],
            "runner_config_schema_stabilization_safe": not runner_config_schema_stabilizations["safety"]["executes_commands"]
            and not runner_config_schema_stabilizations["safety"]["creates_process"]
            and not runner_config_schema_stabilizations["safety"]["runner_implemented"]
            and not runner_config_schema_stabilizations["safety"]["launch_enabled"]
            and not runner_config_schema_stabilizations["safety"]["launch_api_available"]
            and runner_config_schema_stabilizations["safety"]["config_schema_stabilization_only"]
            and not runner_config_schema_stabilizations["safety"]["reads_config_file"]
            and not runner_config_schema_stabilizations["safety"]["creates_config_file"]
            and not runner_config_schema_stabilizations["safety"]["writes_config_file"]
            and not runner_config_schema_stabilizations["safety"]["writes_user_project"]
            and not runner_config_schema_stabilizations["safety"]["registers_launch_api"]
            and not runner_config_schema_stabilizations["safety"]["imports_adapter"]
            and not runner_config_schema_stabilizations["safety"]["calls_execution_adapter"],
            "runner_config_field_contract_view_status": runner_config_field_contract_views["status"],
            "runner_config_field_contract_view_safe": not runner_config_field_contract_views["safety"]["executes_commands"]
            and not runner_config_field_contract_views["safety"]["creates_process"]
            and not runner_config_field_contract_views["safety"]["runner_implemented"]
            and not runner_config_field_contract_views["safety"]["launch_enabled"]
            and not runner_config_field_contract_views["safety"]["launch_api_available"]
            and runner_config_field_contract_views["safety"]["config_field_contract_view_only"]
            and not runner_config_field_contract_views["safety"]["reads_config_file"]
            and runner_config_field_contract_views["safety"]["describes_stable_schema_only"]
            and not runner_config_field_contract_views["safety"]["creates_config_file"]
            and not runner_config_field_contract_views["safety"]["writes_config_file"]
            and not runner_config_field_contract_views["safety"]["writes_user_project"]
            and not runner_config_field_contract_views["safety"]["registers_launch_api"]
            and not runner_config_field_contract_views["safety"]["calls_execution_adapter"],
            "runner_config_compatibility_report_status": runner_config_compatibility_reports["status"],
            "runner_config_compatibility_report_safe": not runner_config_compatibility_reports["safety"]["executes_commands"]
            and not runner_config_compatibility_reports["safety"]["creates_process"]
            and not runner_config_compatibility_reports["safety"]["runner_implemented"]
            and not runner_config_compatibility_reports["safety"]["launch_enabled"]
            and not runner_config_compatibility_reports["safety"]["launch_api_available"]
            and runner_config_compatibility_reports["safety"]["config_compatibility_report_only"]
            and not runner_config_compatibility_reports["safety"]["reads_config_file"]
            and runner_config_compatibility_reports["safety"]["uses_in_memory_config_payload"]
            and not runner_config_compatibility_reports["safety"]["creates_config_file"]
            and not runner_config_compatibility_reports["safety"]["writes_config_file"]
            and not runner_config_compatibility_reports["safety"]["writes_user_project"]
            and not runner_config_compatibility_reports["safety"]["registers_launch_api"]
            and not runner_config_compatibility_reports["safety"]["calls_execution_adapter"],
            "runner_config_remediation_summary_status": runner_config_remediation_summaries["status"],
            "runner_config_remediation_summary_safe": not runner_config_remediation_summaries["safety"]["executes_commands"]
            and not runner_config_remediation_summaries["safety"]["creates_process"]
            and not runner_config_remediation_summaries["safety"]["runner_implemented"]
            and not runner_config_remediation_summaries["safety"]["launch_enabled"]
            and not runner_config_remediation_summaries["safety"]["launch_api_available"]
            and runner_config_remediation_summaries["safety"]["config_remediation_summary_only"]
            and not runner_config_remediation_summaries["safety"]["reads_config_file"]
            and runner_config_remediation_summaries["safety"]["consumes_compatibility_report"]
            and not runner_config_remediation_summaries["safety"]["writes_config_file"]
            and not runner_config_remediation_summaries["safety"]["writes_user_project"]
            and not runner_config_remediation_summaries["safety"]["calls_execution_adapter"],
            "runner_config_field_coverage_index_status": runner_config_field_coverage_indexes["status"],
            "runner_config_field_coverage_index_safe": not runner_config_field_coverage_indexes["safety"]["executes_commands"]
            and not runner_config_field_coverage_indexes["safety"]["creates_process"]
            and not runner_config_field_coverage_indexes["safety"]["runner_implemented"]
            and not runner_config_field_coverage_indexes["safety"]["launch_enabled"]
            and not runner_config_field_coverage_indexes["safety"]["launch_api_available"]
            and runner_config_field_coverage_indexes["safety"]["config_field_coverage_index_only"]
            and not runner_config_field_coverage_indexes["safety"]["reads_config_file"]
            and runner_config_field_coverage_indexes["safety"]["uses_in_memory_config_payload"]
            and not runner_config_field_coverage_indexes["safety"]["writes_config_file"]
            and not runner_config_field_coverage_indexes["safety"]["writes_user_project"]
            and not runner_config_field_coverage_indexes["safety"]["calls_execution_adapter"],
            "runner_service_flag_audit_status": runner_service_flag_audits["status"],
            "runner_service_flag_audit_safe": not runner_service_flag_audits["safety"]["executes_commands"]
            and not runner_service_flag_audits["safety"]["creates_process"]
            and not runner_service_flag_audits["safety"]["runner_implemented"]
            and not runner_service_flag_audits["safety"]["launch_enabled"]
            and not runner_service_flag_audits["safety"]["launch_api_available"]
            and runner_service_flag_audits["safety"]["service_flag_audit_only"]
            and not runner_service_flag_audits["safety"]["reads_environment"]
            and not runner_service_flag_audits["safety"]["parses_process_args"]
            and not runner_service_flag_audits["safety"]["writes_user_project"]
            and not runner_service_flag_audits["safety"]["creates_config_file"],
            "runner_log_directory_policy_status": runner_log_directory_policies["status"],
            "runner_log_directory_policy_safe": not runner_log_directory_policies["safety"]["executes_commands"]
            and not runner_log_directory_policies["safety"]["creates_process"]
            and not runner_log_directory_policies["safety"]["runner_implemented"]
            and not runner_log_directory_policies["safety"]["launch_enabled"]
            and not runner_log_directory_policies["safety"]["launch_api_available"]
            and runner_log_directory_policies["safety"]["log_directory_policy_only"]
            and not runner_log_directory_policies["safety"]["creates_log_directory"]
            and not runner_log_directory_policies["safety"]["opens_log_files"]
            and not runner_log_directory_policies["safety"]["writes_logs"]
            and not runner_log_directory_policies["safety"]["writes_user_project"]
            and not runner_log_directory_policies["safety"]["creates_config_file"],
            "runner_log_retention_policy_status": runner_log_retention_policies["status"],
            "runner_log_retention_policy_safe": not runner_log_retention_policies["safety"]["executes_commands"]
            and not runner_log_retention_policies["safety"]["creates_process"]
            and not runner_log_retention_policies["safety"]["runner_implemented"]
            and not runner_log_retention_policies["safety"]["launch_enabled"]
            and not runner_log_retention_policies["safety"]["launch_api_available"]
            and runner_log_retention_policies["safety"]["log_retention_policy_only"]
            and not runner_log_retention_policies["safety"]["scans_log_directory"]
            and not runner_log_retention_policies["safety"]["deletes_logs"]
            and not runner_log_retention_policies["safety"]["rotates_logs"]
            and not runner_log_retention_policies["safety"]["renames_logs"]
            and not runner_log_retention_policies["safety"]["truncates_logs"]
            and not runner_log_retention_policies["safety"]["writes_logs"]
            and not runner_log_retention_policies["safety"]["writes_user_project"]
            and not runner_log_retention_policies["safety"]["creates_config_file"],
            "runner_log_cleanup_preview_status": runner_log_cleanup_previews["status"],
            "runner_log_cleanup_preview_safe": not runner_log_cleanup_previews["safety"]["executes_commands"]
            and not runner_log_cleanup_previews["safety"]["creates_process"]
            and not runner_log_cleanup_previews["safety"]["runner_implemented"]
            and not runner_log_cleanup_previews["safety"]["launch_enabled"]
            and not runner_log_cleanup_previews["safety"]["launch_api_available"]
            and runner_log_cleanup_previews["safety"]["cleanup_preview_only"]
            and not runner_log_cleanup_previews["safety"]["scans_log_directory"]
            and not runner_log_cleanup_previews["safety"]["reads_log_files"]
            and not runner_log_cleanup_previews["safety"]["deletes_logs"]
            and not runner_log_cleanup_previews["safety"]["rotates_logs"]
            and not runner_log_cleanup_previews["safety"]["renames_logs"]
            and not runner_log_cleanup_previews["safety"]["truncates_logs"]
            and not runner_log_cleanup_previews["safety"]["writes_logs"]
            and not runner_log_cleanup_previews["safety"]["writes_user_project"]
            and not runner_log_cleanup_previews["safety"]["creates_config_file"],
            "runner_log_cleanup_confirmation_status": runner_log_cleanup_confirmations["status"],
            "runner_log_cleanup_confirmation_safe": not runner_log_cleanup_confirmations["safety"]["executes_commands"]
            and not runner_log_cleanup_confirmations["safety"]["creates_process"]
            and not runner_log_cleanup_confirmations["safety"]["runner_implemented"]
            and not runner_log_cleanup_confirmations["safety"]["launch_enabled"]
            and not runner_log_cleanup_confirmations["safety"]["launch_api_available"]
            and runner_log_cleanup_confirmations["safety"]["cleanup_confirmation_only"]
            and not runner_log_cleanup_confirmations["safety"]["stores_confirmation"]
            and not runner_log_cleanup_confirmations["safety"]["scans_log_directory"]
            and not runner_log_cleanup_confirmations["safety"]["reads_log_files"]
            and not runner_log_cleanup_confirmations["safety"]["deletes_logs"]
            and not runner_log_cleanup_confirmations["safety"]["rotates_logs"]
            and not runner_log_cleanup_confirmations["safety"]["renames_logs"]
            and not runner_log_cleanup_confirmations["safety"]["truncates_logs"]
            and not runner_log_cleanup_confirmations["safety"]["writes_logs"]
            and not runner_log_cleanup_confirmations["safety"]["writes_user_project"]
            and not runner_log_cleanup_confirmations["safety"]["creates_config_file"],
            "runner_log_cleanup_audit_trail_status": runner_log_cleanup_audit_trails["status"],
            "runner_log_cleanup_audit_trail_safe": not runner_log_cleanup_audit_trails["safety"]["executes_commands"]
            and not runner_log_cleanup_audit_trails["safety"]["creates_process"]
            and not runner_log_cleanup_audit_trails["safety"]["runner_implemented"]
            and not runner_log_cleanup_audit_trails["safety"]["launch_enabled"]
            and not runner_log_cleanup_audit_trails["safety"]["launch_api_available"]
            and runner_log_cleanup_audit_trails["safety"]["cleanup_audit_trail_only"]
            and not runner_log_cleanup_audit_trails["safety"]["stores_audit_events"]
            and not runner_log_cleanup_audit_trails["safety"]["writes_audit_log"]
            and not runner_log_cleanup_audit_trails["safety"]["reads_audit_log"]
            and not runner_log_cleanup_audit_trails["safety"]["scans_log_directory"]
            and not runner_log_cleanup_audit_trails["safety"]["reads_log_files"]
            and not runner_log_cleanup_audit_trails["safety"]["deletes_logs"]
            and not runner_log_cleanup_audit_trails["safety"]["rotates_logs"]
            and not runner_log_cleanup_audit_trails["safety"]["renames_logs"]
            and not runner_log_cleanup_audit_trails["safety"]["truncates_logs"]
            and not runner_log_cleanup_audit_trails["safety"]["writes_logs"]
            and not runner_log_cleanup_audit_trails["safety"]["writes_user_project"]
            and not runner_log_cleanup_audit_trails["safety"]["creates_config_file"],
            "runner_log_cleanup_execution_plan_status": runner_log_cleanup_execution_plans["status"],
            "runner_log_cleanup_execution_plan_safe": not runner_log_cleanup_execution_plans["safety"]["executes_commands"]
            and not runner_log_cleanup_execution_plans["safety"]["creates_process"]
            and not runner_log_cleanup_execution_plans["safety"]["runner_implemented"]
            and not runner_log_cleanup_execution_plans["safety"]["launch_enabled"]
            and not runner_log_cleanup_execution_plans["safety"]["launch_api_available"]
            and runner_log_cleanup_execution_plans["safety"]["cleanup_execution_plan_only"]
            and not runner_log_cleanup_execution_plans["safety"]["stores_execution_plan"]
            and not runner_log_cleanup_execution_plans["safety"]["executes_cleanup"]
            and not runner_log_cleanup_execution_plans["safety"]["generates_candidate_manifest"]
            and not runner_log_cleanup_execution_plans["safety"]["stores_candidate_manifest"]
            and not runner_log_cleanup_execution_plans["safety"]["reads_candidate_manifest"]
            and not runner_log_cleanup_execution_plans["safety"]["stores_audit_events"]
            and not runner_log_cleanup_execution_plans["safety"]["writes_audit_log"]
            and not runner_log_cleanup_execution_plans["safety"]["reads_audit_log"]
            and not runner_log_cleanup_execution_plans["safety"]["scans_log_directory"]
            and not runner_log_cleanup_execution_plans["safety"]["reads_log_files"]
            and not runner_log_cleanup_execution_plans["safety"]["deletes_logs"]
            and not runner_log_cleanup_execution_plans["safety"]["rotates_logs"]
            and not runner_log_cleanup_execution_plans["safety"]["renames_logs"]
            and not runner_log_cleanup_execution_plans["safety"]["truncates_logs"]
            and not runner_log_cleanup_execution_plans["safety"]["writes_logs"]
            and not runner_log_cleanup_execution_plans["safety"]["writes_user_project"]
            and not runner_log_cleanup_execution_plans["safety"]["creates_config_file"],
            "runner_governance_readiness_status": runner_governance_readiness["status"],
            "runner_governance_readiness_safe": not runner_governance_readiness["safety"]["executes_commands"]
            and not runner_governance_readiness["safety"]["creates_process"]
            and not runner_governance_readiness["safety"]["runner_implemented"]
            and not runner_governance_readiness["safety"]["launch_enabled"]
            and not runner_governance_readiness["safety"]["launch_api_available"]
            and runner_governance_readiness["safety"]["governance_readiness_only"]
            and not runner_governance_readiness["safety"]["writes_user_project"]
            and not runner_governance_readiness["safety"]["creates_config_file"]
            and not runner_governance_readiness["safety"]["reads_log_files"]
            and not runner_governance_readiness["safety"]["writes_logs"]
            and not runner_governance_readiness["safety"]["deletes_logs"],
            "runner_execution_adapter_contract_status": runner_execution_adapter_contracts["status"],
            "runner_execution_adapter_contract_safe": not runner_execution_adapter_contracts["safety"]["executes_commands"]
            and not runner_execution_adapter_contracts["safety"]["creates_process"]
            and not runner_execution_adapter_contracts["safety"]["runner_implemented"]
            and not runner_execution_adapter_contracts["safety"]["launch_enabled"]
            and not runner_execution_adapter_contracts["safety"]["launch_api_available"]
            and runner_execution_adapter_contracts["safety"]["execution_adapter_contract_only"]
            and not runner_execution_adapter_contracts["safety"]["writes_user_project"]
            and not runner_execution_adapter_contracts["safety"]["creates_config_file"]
            and not runner_execution_adapter_contracts["safety"]["reads_log_files"]
            and not runner_execution_adapter_contracts["safety"]["writes_logs"]
            and not runner_execution_adapter_contracts["safety"]["deletes_logs"],
            "runner_launch_api_contract_status": runner_launch_api_contracts["status"],
            "runner_launch_api_contract_safe": not runner_launch_api_contracts["safety"]["executes_commands"]
            and not runner_launch_api_contracts["safety"]["creates_process"]
            and not runner_launch_api_contracts["safety"]["runner_implemented"]
            and not runner_launch_api_contracts["safety"]["launch_enabled"]
            and not runner_launch_api_contracts["safety"]["launch_api_available"]
            and runner_launch_api_contracts["safety"]["launch_api_contract_only"]
            and not runner_launch_api_contracts["safety"]["registers_post_api"]
            and not runner_launch_api_contracts["safety"]["writes_user_project"]
            and not runner_launch_api_contracts["safety"]["creates_config_file"]
            and not runner_launch_api_contracts["safety"]["reads_log_files"]
            and not runner_launch_api_contracts["safety"]["writes_logs"]
            and not runner_launch_api_contracts["safety"]["deletes_logs"],
            "runner_execution_adapter_review_status": runner_execution_adapter_reviews["status"],
            "runner_execution_adapter_review_safe": not runner_execution_adapter_reviews["safety"]["executes_commands"]
            and not runner_execution_adapter_reviews["safety"]["creates_process"]
            and not runner_execution_adapter_reviews["safety"]["runner_implemented"]
            and not runner_execution_adapter_reviews["safety"]["launch_enabled"]
            and not runner_execution_adapter_reviews["safety"]["launch_api_available"]
            and runner_execution_adapter_reviews["safety"]["adapter_review_only"]
            and not runner_execution_adapter_reviews["safety"]["scans_code"]
            and not runner_execution_adapter_reviews["safety"]["imports_adapter"]
            and not runner_execution_adapter_reviews["safety"]["registers_post_api"]
            and not runner_execution_adapter_reviews["safety"]["calls_execution_adapter"]
            and not runner_execution_adapter_reviews["safety"]["writes_user_project"]
            and not runner_execution_adapter_reviews["safety"]["creates_config_file"]
            and not runner_execution_adapter_reviews["safety"]["reads_log_files"]
            and not runner_execution_adapter_reviews["safety"]["writes_logs"]
            and not runner_execution_adapter_reviews["safety"]["deletes_logs"],
            "runner_final_block_matrix_status": runner_final_block_matrices["status"],
            "runner_final_block_matrix_safe": not runner_final_block_matrices["safety"]["executes_commands"]
            and not runner_final_block_matrices["safety"]["creates_process"]
            and not runner_final_block_matrices["safety"]["runner_implemented"]
            and not runner_final_block_matrices["safety"]["launch_enabled"]
            and not runner_final_block_matrices["safety"]["launch_api_available"]
            and runner_final_block_matrices["safety"]["final_block_matrix_only"]
            and not runner_final_block_matrices["safety"]["registers_post_api"]
            and not runner_final_block_matrices["safety"]["imports_adapter"]
            and not runner_final_block_matrices["safety"]["calls_execution_adapter"]
            and not runner_final_block_matrices["safety"]["opens_stdout_stderr"]
            and not runner_final_block_matrices["safety"]["writes_runner_events"]
            and not runner_final_block_matrices["safety"]["stores_launch_state"]
            and not runner_final_block_matrices["safety"]["scans_log_directory"]
            and not runner_final_block_matrices["safety"]["reads_log_files"]
            and not runner_final_block_matrices["safety"]["writes_logs"]
            and not runner_final_block_matrices["safety"]["deletes_logs"]
            and not runner_final_block_matrices["safety"]["rotates_logs"]
            and not runner_final_block_matrices["safety"]["renames_logs"]
            and not runner_final_block_matrices["safety"]["truncates_logs"]
            and not runner_final_block_matrices["safety"]["writes_audit_log"]
            and not runner_final_block_matrices["safety"]["reads_audit_log"]
            and not runner_final_block_matrices["safety"]["writes_user_project"]
            and not runner_final_block_matrices["safety"]["creates_config_file"],
            "runner_authorization_unlock_audit_status": runner_authorization_unlock_audits["status"],
            "runner_authorization_unlock_audit_safe": not runner_authorization_unlock_audits["safety"]["executes_commands"]
            and not runner_authorization_unlock_audits["safety"]["creates_process"]
            and not runner_authorization_unlock_audits["safety"]["runner_implemented"]
            and not runner_authorization_unlock_audits["safety"]["launch_enabled"]
            and not runner_authorization_unlock_audits["safety"]["launch_api_available"]
            and runner_authorization_unlock_audits["safety"]["authorization_unlock_audit_only"]
            and not runner_authorization_unlock_audits["safety"]["registers_post_api"]
            and not runner_authorization_unlock_audits["safety"]["imports_adapter"]
            and not runner_authorization_unlock_audits["safety"]["calls_execution_adapter"]
            and not runner_authorization_unlock_audits["safety"]["grants_permission"]
            and not runner_authorization_unlock_audits["safety"]["collects_human_authorization"]
            and not runner_authorization_unlock_audits["safety"]["stores_authorization"]
            and not runner_authorization_unlock_audits["safety"]["opens_stdout_stderr"]
            and not runner_authorization_unlock_audits["safety"]["writes_runner_events"]
            and not runner_authorization_unlock_audits["safety"]["stores_launch_state"]
            and not runner_authorization_unlock_audits["safety"]["scans_log_directory"]
            and not runner_authorization_unlock_audits["safety"]["reads_log_files"]
            and not runner_authorization_unlock_audits["safety"]["writes_logs"]
            and not runner_authorization_unlock_audits["safety"]["deletes_logs"]
            and not runner_authorization_unlock_audits["safety"]["rotates_logs"]
            and not runner_authorization_unlock_audits["safety"]["renames_logs"]
            and not runner_authorization_unlock_audits["safety"]["truncates_logs"]
            and not runner_authorization_unlock_audits["safety"]["writes_audit_log"]
            and not runner_authorization_unlock_audits["safety"]["reads_audit_log"]
            and not runner_authorization_unlock_audits["safety"]["writes_user_project"]
            and not runner_authorization_unlock_audits["safety"]["creates_config_file"],
            "runner_implementation_gap_checklist_status": runner_implementation_gap_checklists["status"],
            "runner_implementation_gap_checklist_safe": not runner_implementation_gap_checklists["safety"]["executes_commands"]
            and not runner_implementation_gap_checklists["safety"]["creates_process"]
            and not runner_implementation_gap_checklists["safety"]["runner_implemented"]
            and not runner_implementation_gap_checklists["safety"]["launch_enabled"]
            and not runner_implementation_gap_checklists["safety"]["launch_api_available"]
            and runner_implementation_gap_checklists["safety"]["implementation_gap_checklist_only"]
            and not runner_implementation_gap_checklists["safety"]["implements_runner"]
            and not runner_implementation_gap_checklists["safety"]["writes_code"]
            and not runner_implementation_gap_checklists["safety"]["registers_post_api"]
            and not runner_implementation_gap_checklists["safety"]["imports_adapter"]
            and not runner_implementation_gap_checklists["safety"]["calls_execution_adapter"]
            and not runner_implementation_gap_checklists["safety"]["grants_permission"]
            and not runner_implementation_gap_checklists["safety"]["collects_human_authorization"]
            and not runner_implementation_gap_checklists["safety"]["stores_authorization"]
            and not runner_implementation_gap_checklists["safety"]["opens_stdout_stderr"]
            and not runner_implementation_gap_checklists["safety"]["writes_runner_events"]
            and not runner_implementation_gap_checklists["safety"]["stores_launch_state"]
            and not runner_implementation_gap_checklists["safety"]["scans_log_directory"]
            and not runner_implementation_gap_checklists["safety"]["reads_log_files"]
            and not runner_implementation_gap_checklists["safety"]["writes_logs"]
            and not runner_implementation_gap_checklists["safety"]["deletes_logs"]
            and not runner_implementation_gap_checklists["safety"]["rotates_logs"]
            and not runner_implementation_gap_checklists["safety"]["renames_logs"]
            and not runner_implementation_gap_checklists["safety"]["truncates_logs"]
            and not runner_implementation_gap_checklists["safety"]["writes_audit_log"]
            and not runner_implementation_gap_checklists["safety"]["reads_audit_log"]
            and not runner_implementation_gap_checklists["safety"]["writes_user_project"]
            and not runner_implementation_gap_checklists["safety"]["creates_config_file"],
            "runner_cancel_timeout_contract_status": runner_cancel_timeout_contracts["status"],
            "runner_cancel_timeout_contract_safe": not runner_cancel_timeout_contracts["safety"]["executes_commands"]
            and not runner_cancel_timeout_contracts["safety"]["creates_process"]
            and not runner_cancel_timeout_contracts["safety"]["runner_implemented"]
            and not runner_cancel_timeout_contracts["safety"]["launch_enabled"]
            and not runner_cancel_timeout_contracts["safety"]["launch_api_available"]
            and runner_cancel_timeout_contracts["safety"]["cancel_timeout_contract_only"]
            and not runner_cancel_timeout_contracts["safety"]["registers_post_api"]
            and not runner_cancel_timeout_contracts["safety"]["registers_cancel_api"]
            and not runner_cancel_timeout_contracts["safety"]["registers_timeout_api"]
            and not runner_cancel_timeout_contracts["safety"]["implements_runner"]
            and not runner_cancel_timeout_contracts["safety"]["imports_adapter"]
            and not runner_cancel_timeout_contracts["safety"]["calls_execution_adapter"]
            and not runner_cancel_timeout_contracts["safety"]["cancels_process"]
            and not runner_cancel_timeout_contracts["safety"]["sends_process_signal"]
            and not runner_cancel_timeout_contracts["safety"]["kills_process"]
            and not runner_cancel_timeout_contracts["safety"]["schedules_timeout"]
            and not runner_cancel_timeout_contracts["safety"]["opens_stdout_stderr"]
            and not runner_cancel_timeout_contracts["safety"]["writes_runner_events"]
            and not runner_cancel_timeout_contracts["safety"]["stores_launch_state"]
            and not runner_cancel_timeout_contracts["safety"]["scans_log_directory"]
            and not runner_cancel_timeout_contracts["safety"]["reads_log_files"]
            and not runner_cancel_timeout_contracts["safety"]["writes_logs"]
            and not runner_cancel_timeout_contracts["safety"]["deletes_logs"]
            and not runner_cancel_timeout_contracts["safety"]["rotates_logs"]
            and not runner_cancel_timeout_contracts["safety"]["renames_logs"]
            and not runner_cancel_timeout_contracts["safety"]["truncates_logs"]
            and not runner_cancel_timeout_contracts["safety"]["writes_audit_log"]
            and not runner_cancel_timeout_contracts["safety"]["reads_audit_log"]
            and not runner_cancel_timeout_contracts["safety"]["writes_user_project"]
            and not runner_cancel_timeout_contracts["safety"]["creates_config_file"],
            "runner_cancel_timeout_real_api_status": runner_cancel_timeout_real_apis["status"],
            "runner_cancel_timeout_real_api_registered_endpoint_count": (
                runner_cancel_timeout_real_apis["summary"]["registered_endpoint_count"]
            ),
            "runner_cancel_timeout_real_api_active_process_count": (
                runner_cancel_timeout_real_apis["summary"]["active_process_count"]
            ),
            "runner_cancel_timeout_real_api_cancelled_count": (
                runner_cancel_timeout_real_apis["summary"]["cancelled_count"]
            ),
            "runner_cancel_timeout_real_api_timed_out_count": (
                runner_cancel_timeout_real_apis["summary"]["timed_out_count"]
            ),
            "runner_cancel_timeout_real_api_safe": not runner_cancel_timeout_real_apis["safety"]["executes_commands"]
            and not runner_cancel_timeout_real_apis["safety"]["creates_process"]
            and runner_cancel_timeout_real_apis["safety"]["runner_implemented"]
            and runner_cancel_timeout_real_apis["safety"]["launch_enabled"]
            and runner_cancel_timeout_real_apis["safety"]["launch_api_available"]
            and runner_cancel_timeout_real_apis["safety"]["cancel_timeout_real_api"]
            and runner_cancel_timeout_real_apis["safety"]["registers_post_api"]
            and runner_cancel_timeout_real_apis["safety"]["registers_cancel_api"]
            and runner_cancel_timeout_real_apis["safety"]["registers_timeout_api"]
            and runner_cancel_timeout_real_apis["safety"]["controls_process"]
            and runner_cancel_timeout_real_apis["safety"]["cancels_process"]
            and runner_cancel_timeout_real_apis["safety"]["sends_process_signal"]
            and not runner_cancel_timeout_real_apis["safety"]["kills_process"]
            and not runner_cancel_timeout_real_apis["safety"]["schedules_timeout"]
            and not runner_cancel_timeout_real_apis["safety"]["accepts_pid"]
            and not runner_cancel_timeout_real_apis["safety"]["accepts_shell"]
            and not runner_cancel_timeout_real_apis["safety"]["calls_execution_adapter"]
            and not runner_cancel_timeout_real_apis["safety"]["writes_runner_events"]
            and not runner_cancel_timeout_real_apis["safety"]["writes_audit_log"]
            and not runner_cancel_timeout_real_apis["safety"]["reads_audit_log"]
            and not runner_cancel_timeout_real_apis["safety"]["reads_log_files"]
            and not runner_cancel_timeout_real_apis["safety"]["writes_logs"]
            and not runner_cancel_timeout_real_apis["safety"]["stores_authorization"]
            and not runner_cancel_timeout_real_apis["safety"]["writes_user_project"],
            "runner_first_real_test_status": runner_first_real_tests["status"],
            "runner_first_real_test_execution_count": runner_first_real_tests["summary"]["execution_count"],
            "runner_first_real_test_completed_count": (
                runner_first_real_tests["summary"]["first_real_test_completed_count"]
            ),
            "runner_first_real_test_failed_count": (
                runner_first_real_tests["summary"]["first_real_test_failed_count"]
            ),
            "runner_first_real_test_safe": not runner_first_real_tests["safety"]["executes_commands"]
            and not runner_first_real_tests["safety"]["creates_process"]
            and runner_first_real_tests["safety"]["runner_implemented"]
            and runner_first_real_tests["safety"]["launch_enabled"]
            and runner_first_real_tests["safety"]["launch_api_available"]
            and runner_first_real_tests["safety"]["first_real_test_report"]
            and not runner_first_real_tests["safety"]["registers_post_api"]
            and not runner_first_real_tests["safety"]["registers_launch_api"]
            and not runner_first_real_tests["safety"]["registers_cancel_api"]
            and not runner_first_real_tests["safety"]["registers_timeout_api"]
            and not runner_first_real_tests["safety"]["imports_adapter"]
            and not runner_first_real_tests["safety"]["calls_execution_adapter"]
            and not runner_first_real_tests["safety"]["controls_process"]
            and not runner_first_real_tests["safety"]["writes_runner_events"]
            and not runner_first_real_tests["safety"]["reads_log_files"]
            and not runner_first_real_tests["safety"]["writes_logs"]
            and not runner_first_real_tests["safety"]["writes_audit_log"]
            and not runner_first_real_tests["safety"]["writes_user_project"],
            "runner_session_state_schema_status": runner_session_state_schemas["status"],
            "runner_session_state_schema_safe": not runner_session_state_schemas["safety"]["executes_commands"]
            and not runner_session_state_schemas["safety"]["creates_process"]
            and not runner_session_state_schemas["safety"]["runner_implemented"]
            and not runner_session_state_schemas["safety"]["launch_enabled"]
            and not runner_session_state_schemas["safety"]["launch_api_available"]
            and runner_session_state_schemas["safety"]["session_state_schema_only"]
            and not runner_session_state_schemas["safety"]["registers_post_api"]
            and not runner_session_state_schemas["safety"]["registers_launch_api"]
            and not runner_session_state_schemas["safety"]["registers_cancel_api"]
            and not runner_session_state_schemas["safety"]["registers_timeout_api"]
            and not runner_session_state_schemas["safety"]["implements_runner"]
            and not runner_session_state_schemas["safety"]["imports_adapter"]
            and not runner_session_state_schemas["safety"]["calls_execution_adapter"]
            and not runner_session_state_schemas["safety"]["creates_session"]
            and not runner_session_state_schemas["safety"]["stores_session_state"]
            and not runner_session_state_schemas["safety"]["mutates_session_state"]
            and not runner_session_state_schemas["safety"]["reads_session_state_store"]
            and not runner_session_state_schemas["safety"]["writes_session_state_store"]
            and not runner_session_state_schemas["safety"]["cancels_process"]
            and not runner_session_state_schemas["safety"]["sends_process_signal"]
            and not runner_session_state_schemas["safety"]["kills_process"]
            and not runner_session_state_schemas["safety"]["schedules_timeout"]
            and not runner_session_state_schemas["safety"]["opens_stdout_stderr"]
            and not runner_session_state_schemas["safety"]["writes_runner_events"]
            and not runner_session_state_schemas["safety"]["scans_log_directory"]
            and not runner_session_state_schemas["safety"]["reads_log_files"]
            and not runner_session_state_schemas["safety"]["writes_logs"]
            and not runner_session_state_schemas["safety"]["writes_audit_log"]
            and not runner_session_state_schemas["safety"]["reads_audit_log"]
            and not runner_session_state_schemas["safety"]["writes_user_project"]
            and not runner_session_state_schemas["safety"]["creates_config_file"],
            "runner_real_test_readiness_status": runner_real_test_readiness["status"],
            "runner_real_test_readiness_safe": not runner_real_test_readiness["safety"]["executes_commands"]
            and not runner_real_test_readiness["safety"]["creates_process"]
            and not runner_real_test_readiness["safety"]["runner_implemented"]
            and not runner_real_test_readiness["safety"]["launch_enabled"]
            and not runner_real_test_readiness["safety"]["launch_api_available"]
            and runner_real_test_readiness["safety"]["real_test_readiness_only"]
            and not runner_real_test_readiness["safety"]["registers_post_api"]
            and not runner_real_test_readiness["safety"]["registers_launch_api"]
            and not runner_real_test_readiness["safety"]["registers_cancel_api"]
            and not runner_real_test_readiness["safety"]["registers_timeout_api"]
            and not runner_real_test_readiness["safety"]["implements_runner"]
            and not runner_real_test_readiness["safety"]["imports_adapter"]
            and not runner_real_test_readiness["safety"]["calls_execution_adapter"]
            and not runner_real_test_readiness["safety"]["creates_session"]
            and not runner_real_test_readiness["safety"]["stores_session_state"]
            and not runner_real_test_readiness["safety"]["mutates_session_state"]
            and not runner_real_test_readiness["safety"]["reads_session_state_store"]
            and not runner_real_test_readiness["safety"]["writes_session_state_store"]
            and not runner_real_test_readiness["safety"]["cancels_process"]
            and not runner_real_test_readiness["safety"]["sends_process_signal"]
            and not runner_real_test_readiness["safety"]["kills_process"]
            and not runner_real_test_readiness["safety"]["schedules_timeout"]
            and not runner_real_test_readiness["safety"]["opens_stdout_stderr"]
            and not runner_real_test_readiness["safety"]["writes_runner_events"]
            and not runner_real_test_readiness["safety"]["scans_log_directory"]
            and not runner_real_test_readiness["safety"]["reads_log_files"]
            and not runner_real_test_readiness["safety"]["writes_logs"]
            and not runner_real_test_readiness["safety"]["writes_audit_log"]
            and not runner_real_test_readiness["safety"]["reads_audit_log"]
            and not runner_real_test_readiness["safety"]["collects_human_authorization"]
            and not runner_real_test_readiness["safety"]["stores_authorization"]
            and not runner_real_test_readiness["safety"]["grants_permission"]
            and not runner_real_test_readiness["safety"]["writes_user_project"]
            and not runner_real_test_readiness["safety"]["creates_config_file"],
            "runner_real_test_authorization_checklist_status": runner_real_test_authorization_checklists["status"],
            "runner_real_test_authorization_checklist_safe": not runner_real_test_authorization_checklists["safety"]["executes_commands"]
            and not runner_real_test_authorization_checklists["safety"]["creates_process"]
            and not runner_real_test_authorization_checklists["safety"]["runner_implemented"]
            and not runner_real_test_authorization_checklists["safety"]["launch_enabled"]
            and not runner_real_test_authorization_checklists["safety"]["launch_api_available"]
            and runner_real_test_authorization_checklists["safety"]["authorization_checklist_only"]
            and not runner_real_test_authorization_checklists["safety"]["registers_post_api"]
            and not runner_real_test_authorization_checklists["safety"]["registers_launch_api"]
            and not runner_real_test_authorization_checklists["safety"]["registers_cancel_api"]
            and not runner_real_test_authorization_checklists["safety"]["registers_timeout_api"]
            and not runner_real_test_authorization_checklists["safety"]["implements_runner"]
            and not runner_real_test_authorization_checklists["safety"]["imports_adapter"]
            and not runner_real_test_authorization_checklists["safety"]["calls_execution_adapter"]
            and not runner_real_test_authorization_checklists["safety"]["creates_session"]
            and not runner_real_test_authorization_checklists["safety"]["stores_session_state"]
            and not runner_real_test_authorization_checklists["safety"]["mutates_session_state"]
            and not runner_real_test_authorization_checklists["safety"]["reads_session_state_store"]
            and not runner_real_test_authorization_checklists["safety"]["writes_session_state_store"]
            and not runner_real_test_authorization_checklists["safety"]["opens_stdout_stderr"]
            and not runner_real_test_authorization_checklists["safety"]["writes_runner_events"]
            and not runner_real_test_authorization_checklists["safety"]["reads_log_files"]
            and not runner_real_test_authorization_checklists["safety"]["writes_logs"]
            and not runner_real_test_authorization_checklists["safety"]["writes_audit_log"]
            and not runner_real_test_authorization_checklists["safety"]["reads_audit_log"]
            and not runner_real_test_authorization_checklists["safety"]["collects_human_authorization"]
            and not runner_real_test_authorization_checklists["safety"]["stores_authorization"]
            and not runner_real_test_authorization_checklists["safety"]["grants_permission"]
            and not runner_real_test_authorization_checklists["safety"]["writes_user_project"]
            and not runner_real_test_authorization_checklists["safety"]["creates_config_file"],
            "runner_real_test_authorization_package_status": runner_real_test_authorization_packages["status"],
            "runner_real_test_authorization_package_safe": not runner_real_test_authorization_packages["safety"]["executes_commands"]
            and not runner_real_test_authorization_packages["safety"]["creates_process"]
            and not runner_real_test_authorization_packages["safety"]["runner_implemented"]
            and not runner_real_test_authorization_packages["safety"]["launch_enabled"]
            and not runner_real_test_authorization_packages["safety"]["launch_api_available"]
            and runner_real_test_authorization_packages["safety"]["authorization_package_only"]
            and not runner_real_test_authorization_packages["safety"]["registers_post_api"]
            and not runner_real_test_authorization_packages["safety"]["registers_launch_api"]
            and not runner_real_test_authorization_packages["safety"]["registers_cancel_api"]
            and not runner_real_test_authorization_packages["safety"]["registers_timeout_api"]
            and not runner_real_test_authorization_packages["safety"]["implements_runner"]
            and not runner_real_test_authorization_packages["safety"]["imports_adapter"]
            and not runner_real_test_authorization_packages["safety"]["calls_execution_adapter"]
            and not runner_real_test_authorization_packages["safety"]["creates_session"]
            and not runner_real_test_authorization_packages["safety"]["stores_session_state"]
            and not runner_real_test_authorization_packages["safety"]["mutates_session_state"]
            and not runner_real_test_authorization_packages["safety"]["reads_session_state_store"]
            and not runner_real_test_authorization_packages["safety"]["writes_session_state_store"]
            and not runner_real_test_authorization_packages["safety"]["opens_stdout_stderr"]
            and not runner_real_test_authorization_packages["safety"]["writes_runner_events"]
            and not runner_real_test_authorization_packages["safety"]["reads_log_files"]
            and not runner_real_test_authorization_packages["safety"]["writes_logs"]
            and not runner_real_test_authorization_packages["safety"]["writes_audit_log"]
            and not runner_real_test_authorization_packages["safety"]["reads_audit_log"]
            and not runner_real_test_authorization_packages["safety"]["collects_human_authorization"]
            and not runner_real_test_authorization_packages["safety"]["stores_authorization"]
            and not runner_real_test_authorization_packages["safety"]["grants_permission"]
            and not runner_real_test_authorization_packages["safety"]["writes_user_project"]
            and not runner_real_test_authorization_packages["safety"]["creates_config_file"],
            "runner_real_test_sandbox_policy_status": runner_real_test_sandbox_policies["status"],
            "runner_real_test_sandbox_policy_safe": not runner_real_test_sandbox_policies["safety"]["executes_commands"]
            and not runner_real_test_sandbox_policies["safety"]["creates_process"]
            and not runner_real_test_sandbox_policies["safety"]["runner_implemented"]
            and not runner_real_test_sandbox_policies["safety"]["launch_enabled"]
            and not runner_real_test_sandbox_policies["safety"]["launch_api_available"]
            and runner_real_test_sandbox_policies["safety"]["sandbox_policy_only"]
            and not runner_real_test_sandbox_policies["safety"]["applies_sandbox_policy"]
            and not runner_real_test_sandbox_policies["safety"]["writes_environment"]
            and not runner_real_test_sandbox_policies["safety"]["creates_log_directory"]
            and not runner_real_test_sandbox_policies["safety"]["changes_permissions"]
            and not runner_real_test_sandbox_policies["safety"]["grants_process_permission"]
            and not runner_real_test_sandbox_policies["safety"]["registers_post_api"]
            and not runner_real_test_sandbox_policies["safety"]["registers_launch_api"]
            and not runner_real_test_sandbox_policies["safety"]["registers_cancel_api"]
            and not runner_real_test_sandbox_policies["safety"]["registers_timeout_api"]
            and not runner_real_test_sandbox_policies["safety"]["implements_runner"]
            and not runner_real_test_sandbox_policies["safety"]["imports_adapter"]
            and not runner_real_test_sandbox_policies["safety"]["calls_execution_adapter"]
            and not runner_real_test_sandbox_policies["safety"]["opens_stdout_stderr"]
            and not runner_real_test_sandbox_policies["safety"]["writes_runner_events"]
            and not runner_real_test_sandbox_policies["safety"]["reads_log_files"]
            and not runner_real_test_sandbox_policies["safety"]["writes_logs"]
            and not runner_real_test_sandbox_policies["safety"]["writes_audit_log"]
            and not runner_real_test_sandbox_policies["safety"]["reads_audit_log"]
            and not runner_real_test_sandbox_policies["safety"]["collects_human_authorization"]
            and not runner_real_test_sandbox_policies["safety"]["stores_authorization"]
            and not runner_real_test_sandbox_policies["safety"]["grants_permission"]
            and not runner_real_test_sandbox_policies["safety"]["writes_user_project"]
            and not runner_real_test_sandbox_policies["safety"]["creates_config_file"],
            "runner_real_test_final_checklist_status": runner_real_test_final_checklists["status"],
            "runner_real_test_final_checklist_safe": not runner_real_test_final_checklists["safety"]["executes_commands"]
            and not runner_real_test_final_checklists["safety"]["creates_process"]
            and not runner_real_test_final_checklists["safety"]["runner_implemented"]
            and not runner_real_test_final_checklists["safety"]["launch_enabled"]
            and not runner_real_test_final_checklists["safety"]["launch_api_available"]
            and runner_real_test_final_checklists["safety"]["final_checklist_only"]
            and not runner_real_test_final_checklists["safety"]["marks_checklist_complete"]
            and not runner_real_test_final_checklists["safety"]["grants_launch_permission"]
            and not runner_real_test_final_checklists["safety"]["registers_post_api"]
            and not runner_real_test_final_checklists["safety"]["registers_launch_api"]
            and not runner_real_test_final_checklists["safety"]["registers_cancel_api"]
            and not runner_real_test_final_checklists["safety"]["registers_timeout_api"]
            and not runner_real_test_final_checklists["safety"]["implements_runner"]
            and not runner_real_test_final_checklists["safety"]["imports_adapter"]
            and not runner_real_test_final_checklists["safety"]["calls_execution_adapter"]
            and not runner_real_test_final_checklists["safety"]["opens_stdout_stderr"]
            and not runner_real_test_final_checklists["safety"]["writes_runner_events"]
            and not runner_real_test_final_checklists["safety"]["reads_log_files"]
            and not runner_real_test_final_checklists["safety"]["writes_logs"]
            and not runner_real_test_final_checklists["safety"]["writes_audit_log"]
            and not runner_real_test_final_checklists["safety"]["reads_audit_log"]
            and not runner_real_test_final_checklists["safety"]["collects_human_authorization"]
            and not runner_real_test_final_checklists["safety"]["stores_authorization"]
            and not runner_real_test_final_checklists["safety"]["grants_permission"]
            and not runner_real_test_final_checklists["safety"]["writes_user_project"]
            and not runner_real_test_final_checklists["safety"]["creates_config_file"],
            "runner_real_test_ui_preview_status": runner_real_test_ui_previews["status"],
            "runner_real_test_ui_preview_safe": not runner_real_test_ui_previews["safety"]["executes_commands"]
            and not runner_real_test_ui_previews["safety"]["creates_process"]
            and not runner_real_test_ui_previews["safety"]["runner_implemented"]
            and not runner_real_test_ui_previews["safety"]["launch_enabled"]
            and not runner_real_test_ui_previews["safety"]["launch_api_available"]
            and runner_real_test_ui_previews["safety"]["ui_preview_only"]
            and not runner_real_test_ui_previews["safety"]["enables_launch_ui"]
            and not runner_real_test_ui_previews["safety"]["enables_cancel_ui"]
            and not runner_real_test_ui_previews["safety"]["enables_timeout_ui"]
            and not runner_real_test_ui_previews["safety"]["registers_post_api"]
            and not runner_real_test_ui_previews["safety"]["registers_launch_api"]
            and not runner_real_test_ui_previews["safety"]["registers_cancel_api"]
            and not runner_real_test_ui_previews["safety"]["registers_timeout_api"]
            and not runner_real_test_ui_previews["safety"]["implements_runner"]
            and not runner_real_test_ui_previews["safety"]["imports_adapter"]
            and not runner_real_test_ui_previews["safety"]["calls_execution_adapter"]
            and not runner_real_test_ui_previews["safety"]["opens_stdout_stderr"]
            and not runner_real_test_ui_previews["safety"]["writes_runner_events"]
            and not runner_real_test_ui_previews["safety"]["reads_log_files"]
            and not runner_real_test_ui_previews["safety"]["writes_logs"]
            and not runner_real_test_ui_previews["safety"]["writes_audit_log"]
            and not runner_real_test_ui_previews["safety"]["reads_audit_log"]
            and not runner_real_test_ui_previews["safety"]["collects_human_authorization"]
            and not runner_real_test_ui_previews["safety"]["stores_authorization"]
            and not runner_real_test_ui_previews["safety"]["grants_permission"]
            and not runner_real_test_ui_previews["safety"]["writes_user_project"]
            and not runner_real_test_ui_previews["safety"]["creates_config_file"],
            "runner_real_execution_stage_boundary_review_status": runner_real_execution_stage_boundary_reviews["status"],
            "runner_real_execution_stage_boundary_review_safe": not runner_real_execution_stage_boundary_reviews["safety"]["executes_commands"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["creates_process"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["runner_implemented"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["launch_enabled"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["launch_api_available"]
            and runner_real_execution_stage_boundary_reviews["safety"]["stage_boundary_review_only"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["stage_three_unlocked"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["allows_real_execution_implementation"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["writes_code"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["registers_post_api"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["registers_launch_api"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["registers_cancel_api"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["registers_timeout_api"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["imports_adapter"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["calls_execution_adapter"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["creates_session"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["opens_stdout_stderr"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["writes_runner_events"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["reads_log_files"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["writes_logs"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["writes_audit_log"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["reads_audit_log"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["collects_human_authorization"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["stores_authorization"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["grants_permission"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["writes_user_project"]
            and not runner_real_execution_stage_boundary_reviews["safety"]["creates_config_file"],
            "runner_real_execution_unlock_material_review_status": runner_real_execution_unlock_material_reviews["status"],
            "runner_real_execution_unlock_material_review_safe": not runner_real_execution_unlock_material_reviews["safety"]["executes_commands"]
            and not runner_real_execution_unlock_material_reviews["safety"]["creates_process"]
            and not runner_real_execution_unlock_material_reviews["safety"]["runner_implemented"]
            and not runner_real_execution_unlock_material_reviews["safety"]["launch_enabled"]
            and not runner_real_execution_unlock_material_reviews["safety"]["launch_api_available"]
            and runner_real_execution_unlock_material_reviews["safety"]["unlock_material_review_only"]
            and not runner_real_execution_unlock_material_reviews["safety"]["allows_real_execution_implementation"]
            and not runner_real_execution_unlock_material_reviews["safety"]["collects_unlock_materials"]
            and not runner_real_execution_unlock_material_reviews["safety"]["stores_unlock_materials"]
            and not runner_real_execution_unlock_material_reviews["safety"]["accepts_unlock_materials"]
            and not runner_real_execution_unlock_material_reviews["safety"]["writes_code"]
            and not runner_real_execution_unlock_material_reviews["safety"]["registers_launch_api"]
            and not runner_real_execution_unlock_material_reviews["safety"]["calls_execution_adapter"]
            and not runner_real_execution_unlock_material_reviews["safety"]["creates_session"]
            and not runner_real_execution_unlock_material_reviews["safety"]["opens_stdout_stderr"]
            and not runner_real_execution_unlock_material_reviews["safety"]["writes_runner_events"]
            and not runner_real_execution_unlock_material_reviews["safety"]["reads_log_files"]
            and not runner_real_execution_unlock_material_reviews["safety"]["writes_logs"]
            and not runner_real_execution_unlock_material_reviews["safety"]["writes_audit_log"]
            and not runner_real_execution_unlock_material_reviews["safety"]["reads_audit_log"]
            and not runner_real_execution_unlock_material_reviews["safety"]["collects_human_authorization"]
            and not runner_real_execution_unlock_material_reviews["safety"]["stores_authorization"]
            and not runner_real_execution_unlock_material_reviews["safety"]["grants_permission"]
            and not runner_real_execution_unlock_material_reviews["safety"]["writes_user_project"]
            and not runner_real_execution_unlock_material_reviews["safety"]["creates_config_file"],
            "runner_real_execution_implementation_plan_status": runner_real_execution_implementation_plans["status"],
            "runner_real_execution_implementation_plan_safe": not runner_real_execution_implementation_plans["safety"]["executes_commands"]
            and not runner_real_execution_implementation_plans["safety"]["creates_process"]
            and not runner_real_execution_implementation_plans["safety"]["runner_implemented"]
            and not runner_real_execution_implementation_plans["safety"]["launch_enabled"]
            and not runner_real_execution_implementation_plans["safety"]["launch_api_available"]
            and runner_real_execution_implementation_plans["safety"]["implementation_plan_only"]
            and not runner_real_execution_implementation_plans["safety"]["writes_code"]
            and not runner_real_execution_implementation_plans["safety"]["registers_post_api"]
            and not runner_real_execution_implementation_plans["safety"]["registers_launch_api"]
            and not runner_real_execution_implementation_plans["safety"]["registers_cancel_api"]
            and not runner_real_execution_implementation_plans["safety"]["registers_timeout_api"]
            and not runner_real_execution_implementation_plans["safety"]["implements_runner"]
            and not runner_real_execution_implementation_plans["safety"]["imports_adapter"]
            and not runner_real_execution_implementation_plans["safety"]["calls_execution_adapter"]
            and not runner_real_execution_implementation_plans["safety"]["creates_session"]
            and not runner_real_execution_implementation_plans["safety"]["stores_session_state"]
            and not runner_real_execution_implementation_plans["safety"]["mutates_session_state"]
            and not runner_real_execution_implementation_plans["safety"]["reads_session_state_store"]
            and not runner_real_execution_implementation_plans["safety"]["writes_session_state_store"]
            and not runner_real_execution_implementation_plans["safety"]["opens_stdout_stderr"]
            and not runner_real_execution_implementation_plans["safety"]["writes_runner_events"]
            and not runner_real_execution_implementation_plans["safety"]["reads_log_files"]
            and not runner_real_execution_implementation_plans["safety"]["writes_logs"]
            and not runner_real_execution_implementation_plans["safety"]["writes_audit_log"]
            and not runner_real_execution_implementation_plans["safety"]["reads_audit_log"]
            and not runner_real_execution_implementation_plans["safety"]["collects_human_authorization"]
            and not runner_real_execution_implementation_plans["safety"]["stores_authorization"]
            and not runner_real_execution_implementation_plans["safety"]["grants_permission"]
            and not runner_real_execution_implementation_plans["safety"]["writes_user_project"]
            and not runner_real_execution_implementation_plans["safety"]["creates_config_file"],
            "runner_real_execution_scope_diff_audit_status": runner_real_execution_scope_diff_audits["status"],
            "runner_real_execution_scope_diff_audit_safe": not runner_real_execution_scope_diff_audits["safety"]["executes_commands"]
            and not runner_real_execution_scope_diff_audits["safety"]["creates_process"]
            and not runner_real_execution_scope_diff_audits["safety"]["runner_implemented"]
            and not runner_real_execution_scope_diff_audits["safety"]["launch_enabled"]
            and not runner_real_execution_scope_diff_audits["safety"]["launch_api_available"]
            and runner_real_execution_scope_diff_audits["safety"]["scope_diff_audit_only"]
            and runner_real_execution_scope_diff_audits["safety"]["compares_scope_only"]
            and not runner_real_execution_scope_diff_audits["safety"]["allows_real_execution_implementation"]
            and not runner_real_execution_scope_diff_audits["safety"]["writes_code"]
            and not runner_real_execution_scope_diff_audits["safety"]["enables_launch_ui"]
            and not runner_real_execution_scope_diff_audits["safety"]["registers_post_api"]
            and not runner_real_execution_scope_diff_audits["safety"]["registers_launch_api"]
            and not runner_real_execution_scope_diff_audits["safety"]["registers_cancel_api"]
            and not runner_real_execution_scope_diff_audits["safety"]["registers_timeout_api"]
            and not runner_real_execution_scope_diff_audits["safety"]["implements_runner"]
            and not runner_real_execution_scope_diff_audits["safety"]["imports_adapter"]
            and not runner_real_execution_scope_diff_audits["safety"]["calls_execution_adapter"]
            and not runner_real_execution_scope_diff_audits["safety"]["creates_session"]
            and not runner_real_execution_scope_diff_audits["safety"]["opens_stdout_stderr"]
            and not runner_real_execution_scope_diff_audits["safety"]["writes_runner_events"]
            and not runner_real_execution_scope_diff_audits["safety"]["reads_log_files"]
            and not runner_real_execution_scope_diff_audits["safety"]["writes_logs"]
            and not runner_real_execution_scope_diff_audits["safety"]["writes_audit_log"]
            and not runner_real_execution_scope_diff_audits["safety"]["reads_audit_log"]
            and not runner_real_execution_scope_diff_audits["safety"]["collects_human_authorization"]
            and not runner_real_execution_scope_diff_audits["safety"]["stores_authorization"]
            and not runner_real_execution_scope_diff_audits["safety"]["grants_permission"]
            and not runner_real_execution_scope_diff_audits["safety"]["writes_user_project"]
            and not runner_real_execution_scope_diff_audits["safety"]["creates_config_file"],
            "runner_execution_adapter_implementation_audit_status": runner_execution_adapter_implementation_audits["status"],
            "runner_execution_adapter_implementation_audit_safe": not runner_execution_adapter_implementation_audits["safety"]["executes_commands"]
            and not runner_execution_adapter_implementation_audits["safety"]["creates_process"]
            and not runner_execution_adapter_implementation_audits["safety"]["runner_implemented"]
            and not runner_execution_adapter_implementation_audits["safety"]["launch_enabled"]
            and not runner_execution_adapter_implementation_audits["safety"]["launch_api_available"]
            and runner_execution_adapter_implementation_audits["safety"]["adapter_implementation_audit_only"]
            and not runner_execution_adapter_implementation_audits["safety"]["writes_code"]
            and not runner_execution_adapter_implementation_audits["safety"]["registers_post_api"]
            and not runner_execution_adapter_implementation_audits["safety"]["registers_launch_api"]
            and not runner_execution_adapter_implementation_audits["safety"]["registers_cancel_api"]
            and not runner_execution_adapter_implementation_audits["safety"]["registers_timeout_api"]
            and not runner_execution_adapter_implementation_audits["safety"]["implements_runner"]
            and not runner_execution_adapter_implementation_audits["safety"]["implements_adapter"]
            and not runner_execution_adapter_implementation_audits["safety"]["imports_adapter"]
            and not runner_execution_adapter_implementation_audits["safety"]["calls_execution_adapter"]
            and not runner_execution_adapter_implementation_audits["safety"]["creates_session"]
            and not runner_execution_adapter_implementation_audits["safety"]["stores_session_state"]
            and not runner_execution_adapter_implementation_audits["safety"]["mutates_session_state"]
            and not runner_execution_adapter_implementation_audits["safety"]["reads_session_state_store"]
            and not runner_execution_adapter_implementation_audits["safety"]["writes_session_state_store"]
            and not runner_execution_adapter_implementation_audits["safety"]["opens_stdout_stderr"]
            and not runner_execution_adapter_implementation_audits["safety"]["writes_runner_events"]
            and not runner_execution_adapter_implementation_audits["safety"]["reads_log_files"]
            and not runner_execution_adapter_implementation_audits["safety"]["writes_logs"]
            and not runner_execution_adapter_implementation_audits["safety"]["writes_audit_log"]
            and not runner_execution_adapter_implementation_audits["safety"]["reads_audit_log"]
            and not runner_execution_adapter_implementation_audits["safety"]["collects_human_authorization"]
            and not runner_execution_adapter_implementation_audits["safety"]["stores_authorization"]
            and not runner_execution_adapter_implementation_audits["safety"]["grants_permission"]
            and not runner_execution_adapter_implementation_audits["safety"]["writes_user_project"]
            and not runner_execution_adapter_implementation_audits["safety"]["creates_config_file"],
            "runner_process_lifecycle_implementation_audit_status": runner_process_lifecycle_implementation_audits["status"],
            "runner_process_lifecycle_implementation_audit_safe": not runner_process_lifecycle_implementation_audits["safety"]["executes_commands"]
            and not runner_process_lifecycle_implementation_audits["safety"]["creates_process"]
            and runner_process_lifecycle_implementation_audits["safety"]["runner_implemented"]
            and runner_process_lifecycle_implementation_audits["safety"]["launch_enabled"]
            and runner_process_lifecycle_implementation_audits["safety"]["launch_api_available"]
            and runner_process_lifecycle_implementation_audits["safety"]["process_lifecycle_projection"]
            and not runner_process_lifecycle_implementation_audits["safety"]["registers_post_api"]
            and not runner_process_lifecycle_implementation_audits["safety"]["registers_launch_api"]
            and not runner_process_lifecycle_implementation_audits["safety"]["registers_cancel_api"]
            and not runner_process_lifecycle_implementation_audits["safety"]["registers_timeout_api"]
            and not runner_process_lifecycle_implementation_audits["safety"]["implements_adapter"]
            and not runner_process_lifecycle_implementation_audits["safety"]["imports_adapter"]
            and not runner_process_lifecycle_implementation_audits["safety"]["calls_execution_adapter"]
            and not runner_process_lifecycle_implementation_audits["safety"]["creates_session"]
            and not runner_process_lifecycle_implementation_audits["safety"]["stores_session_state"]
            and not runner_process_lifecycle_implementation_audits["safety"]["mutates_session_state"]
            and not runner_process_lifecycle_implementation_audits["safety"]["reads_session_state_store"]
            and not runner_process_lifecycle_implementation_audits["safety"]["writes_session_state_store"]
            and not runner_process_lifecycle_implementation_audits["safety"]["cancels_process"]
            and not runner_process_lifecycle_implementation_audits["safety"]["sends_process_signal"]
            and not runner_process_lifecycle_implementation_audits["safety"]["kills_process"]
            and not runner_process_lifecycle_implementation_audits["safety"]["controls_process"]
            and not runner_process_lifecycle_implementation_audits["safety"]["schedules_timeout"]
            and not runner_process_lifecycle_implementation_audits["safety"]["opens_stdout_stderr"]
            and not runner_process_lifecycle_implementation_audits["safety"]["writes_runner_events"]
            and not runner_process_lifecycle_implementation_audits["safety"]["reads_log_files"]
            and not runner_process_lifecycle_implementation_audits["safety"]["writes_logs"]
            and not runner_process_lifecycle_implementation_audits["safety"]["writes_audit_log"]
            and not runner_process_lifecycle_implementation_audits["safety"]["reads_audit_log"]
            and not runner_process_lifecycle_implementation_audits["safety"]["collects_human_authorization"]
            and not runner_process_lifecycle_implementation_audits["safety"]["stores_authorization"]
            and not runner_process_lifecycle_implementation_audits["safety"]["grants_permission"]
            and not runner_process_lifecycle_implementation_audits["safety"]["writes_user_project"]
            and not runner_process_lifecycle_implementation_audits["safety"]["creates_config_file"],
            "runner_stream_capture_implementation_audit_status": runner_stream_capture_implementation_audits["status"],
            "runner_stream_capture_implementation_audit_safe": not runner_stream_capture_implementation_audits["safety"]["executes_commands"]
            and not runner_stream_capture_implementation_audits["safety"]["creates_process"]
            and runner_stream_capture_implementation_audits["safety"]["runner_implemented"]
            and runner_stream_capture_implementation_audits["safety"]["launch_enabled"]
            and runner_stream_capture_implementation_audits["safety"]["launch_api_available"]
            and runner_stream_capture_implementation_audits["safety"]["stream_capture_projection"]
            and not runner_stream_capture_implementation_audits["safety"]["registers_post_api"]
            and not runner_stream_capture_implementation_audits["safety"]["registers_launch_api"]
            and not runner_stream_capture_implementation_audits["safety"]["registers_cancel_api"]
            and not runner_stream_capture_implementation_audits["safety"]["registers_timeout_api"]
            and not runner_stream_capture_implementation_audits["safety"]["implements_adapter"]
            and not runner_stream_capture_implementation_audits["safety"]["imports_adapter"]
            and not runner_stream_capture_implementation_audits["safety"]["calls_execution_adapter"]
            and not runner_stream_capture_implementation_audits["safety"]["creates_session"]
            and not runner_stream_capture_implementation_audits["safety"]["stores_session_state"]
            and not runner_stream_capture_implementation_audits["safety"]["mutates_session_state"]
            and not runner_stream_capture_implementation_audits["safety"]["cancels_process"]
            and not runner_stream_capture_implementation_audits["safety"]["sends_process_signal"]
            and not runner_stream_capture_implementation_audits["safety"]["kills_process"]
            and not runner_stream_capture_implementation_audits["safety"]["controls_process"]
            and not runner_stream_capture_implementation_audits["safety"]["schedules_timeout"]
            and not runner_stream_capture_implementation_audits["safety"]["opens_stdout_stderr"]
            and not runner_stream_capture_implementation_audits["safety"]["reads_stdout_stderr"]
            and not runner_stream_capture_implementation_audits["safety"]["captures_stdout_stderr"]
            and not runner_stream_capture_implementation_audits["safety"]["writes_runner_events"]
            and not runner_stream_capture_implementation_audits["safety"]["reads_log_files"]
            and not runner_stream_capture_implementation_audits["safety"]["writes_logs"]
            and not runner_stream_capture_implementation_audits["safety"]["writes_audit_log"]
            and not runner_stream_capture_implementation_audits["safety"]["reads_audit_log"]
            and not runner_stream_capture_implementation_audits["safety"]["collects_human_authorization"]
            and not runner_stream_capture_implementation_audits["safety"]["stores_authorization"]
            and not runner_stream_capture_implementation_audits["safety"]["grants_permission"]
            and not runner_stream_capture_implementation_audits["safety"]["writes_user_project"]
            and not runner_stream_capture_implementation_audits["safety"]["creates_config_file"],
            "runner_event_writer_implementation_audit_status": runner_event_writer_implementation_audits["status"],
            "runner_event_writer_implementation_audit_safe": not runner_event_writer_implementation_audits["safety"]["executes_commands"]
            and not runner_event_writer_implementation_audits["safety"]["creates_process"]
            and runner_event_writer_implementation_audits["safety"]["runner_implemented"]
            and runner_event_writer_implementation_audits["safety"]["launch_enabled"]
            and runner_event_writer_implementation_audits["safety"]["launch_api_available"]
            and runner_event_writer_implementation_audits["safety"]["event_writer_projection"]
            and not runner_event_writer_implementation_audits["safety"]["registers_post_api"]
            and not runner_event_writer_implementation_audits["safety"]["registers_launch_api"]
            and not runner_event_writer_implementation_audits["safety"]["registers_cancel_api"]
            and not runner_event_writer_implementation_audits["safety"]["registers_timeout_api"]
            and not runner_event_writer_implementation_audits["safety"]["implements_adapter"]
            and not runner_event_writer_implementation_audits["safety"]["imports_adapter"]
            and not runner_event_writer_implementation_audits["safety"]["calls_execution_adapter"]
            and not runner_event_writer_implementation_audits["safety"]["creates_session"]
            and not runner_event_writer_implementation_audits["safety"]["stores_session_state"]
            and not runner_event_writer_implementation_audits["safety"]["mutates_session_state"]
            and not runner_event_writer_implementation_audits["safety"]["reads_session_state_store"]
            and not runner_event_writer_implementation_audits["safety"]["writes_session_state_store"]
            and not runner_event_writer_implementation_audits["safety"]["cancels_process"]
            and not runner_event_writer_implementation_audits["safety"]["sends_process_signal"]
            and not runner_event_writer_implementation_audits["safety"]["kills_process"]
            and not runner_event_writer_implementation_audits["safety"]["controls_process"]
            and not runner_event_writer_implementation_audits["safety"]["schedules_timeout"]
            and not runner_event_writer_implementation_audits["safety"]["opens_stdout_stderr"]
            and not runner_event_writer_implementation_audits["safety"]["reads_stdout_stderr"]
            and not runner_event_writer_implementation_audits["safety"]["captures_stdout_stderr"]
            and not runner_event_writer_implementation_audits["safety"]["writes_runner_events"]
            and not runner_event_writer_implementation_audits["safety"]["opens_runner_event_log"]
            and not runner_event_writer_implementation_audits["safety"]["writes_event_log"]
            and not runner_event_writer_implementation_audits["safety"]["scans_log_directory"]
            and not runner_event_writer_implementation_audits["safety"]["reads_log_files"]
            and not runner_event_writer_implementation_audits["safety"]["writes_logs"]
            and not runner_event_writer_implementation_audits["safety"]["writes_audit_log"]
            and not runner_event_writer_implementation_audits["safety"]["reads_audit_log"]
            and not runner_event_writer_implementation_audits["safety"]["collects_human_authorization"]
            and not runner_event_writer_implementation_audits["safety"]["stores_authorization"]
            and not runner_event_writer_implementation_audits["safety"]["grants_permission"]
            and not runner_event_writer_implementation_audits["safety"]["writes_user_project"]
            and not runner_event_writer_implementation_audits["safety"]["creates_config_file"],
            "runner_audit_persistence_implementation_audit_status": runner_audit_persistence_implementation_audits["status"],
            "runner_audit_persistence_implementation_audit_safe": not runner_audit_persistence_implementation_audits["safety"]["executes_commands"]
            and not runner_audit_persistence_implementation_audits["safety"]["creates_process"]
            and runner_audit_persistence_implementation_audits["safety"]["runner_implemented"]
            and runner_audit_persistence_implementation_audits["safety"]["launch_enabled"]
            and runner_audit_persistence_implementation_audits["safety"]["launch_api_available"]
            and runner_audit_persistence_implementation_audits["safety"]["audit_persistence_projection"]
            and not runner_audit_persistence_implementation_audits["safety"]["audit_persistence_audit_only"]
            and not runner_audit_persistence_implementation_audits["safety"]["writes_code"]
            and not runner_audit_persistence_implementation_audits["safety"]["registers_post_api"]
            and not runner_audit_persistence_implementation_audits["safety"]["registers_launch_api"]
            and not runner_audit_persistence_implementation_audits["safety"]["registers_cancel_api"]
            and not runner_audit_persistence_implementation_audits["safety"]["registers_timeout_api"]
            and not runner_audit_persistence_implementation_audits["safety"]["implements_runner"]
            and not runner_audit_persistence_implementation_audits["safety"]["implements_adapter"]
            and not runner_audit_persistence_implementation_audits["safety"]["imports_adapter"]
            and not runner_audit_persistence_implementation_audits["safety"]["calls_execution_adapter"]
            and not runner_audit_persistence_implementation_audits["safety"]["creates_session"]
            and not runner_audit_persistence_implementation_audits["safety"]["stores_session_state"]
            and not runner_audit_persistence_implementation_audits["safety"]["mutates_session_state"]
            and not runner_audit_persistence_implementation_audits["safety"]["reads_session_state_store"]
            and not runner_audit_persistence_implementation_audits["safety"]["writes_session_state_store"]
            and not runner_audit_persistence_implementation_audits["safety"]["cancels_process"]
            and not runner_audit_persistence_implementation_audits["safety"]["sends_process_signal"]
            and not runner_audit_persistence_implementation_audits["safety"]["kills_process"]
            and not runner_audit_persistence_implementation_audits["safety"]["controls_process"]
            and not runner_audit_persistence_implementation_audits["safety"]["schedules_timeout"]
            and not runner_audit_persistence_implementation_audits["safety"]["opens_stdout_stderr"]
            and not runner_audit_persistence_implementation_audits["safety"]["reads_stdout_stderr"]
            and not runner_audit_persistence_implementation_audits["safety"]["captures_stdout_stderr"]
            and not runner_audit_persistence_implementation_audits["safety"]["writes_runner_events"]
            and not runner_audit_persistence_implementation_audits["safety"]["opens_runner_event_log"]
            and not runner_audit_persistence_implementation_audits["safety"]["writes_event_log"]
            and not runner_audit_persistence_implementation_audits["safety"]["opens_audit_log"]
            and not runner_audit_persistence_implementation_audits["safety"]["reads_audit_log"]
            and not runner_audit_persistence_implementation_audits["safety"]["writes_audit_log"]
            and not runner_audit_persistence_implementation_audits["safety"]["stores_audit_records"]
            and not runner_audit_persistence_implementation_audits["safety"]["reads_audit_records"]
            and not runner_audit_persistence_implementation_audits["safety"]["scans_log_directory"]
            and not runner_audit_persistence_implementation_audits["safety"]["reads_log_files"]
            and not runner_audit_persistence_implementation_audits["safety"]["writes_logs"]
            and not runner_audit_persistence_implementation_audits["safety"]["collects_human_authorization"]
            and not runner_audit_persistence_implementation_audits["safety"]["stores_authorization"]
            and not runner_audit_persistence_implementation_audits["safety"]["grants_permission"]
            and not runner_audit_persistence_implementation_audits["safety"]["writes_user_project"]
            and not runner_audit_persistence_implementation_audits["safety"]["creates_config_file"],
            "runner_audit_integrity_replay_verification_audit_status": runner_audit_integrity_replay_verification_audits["status"],
            "runner_audit_integrity_replay_verification_audit_safe": not runner_audit_integrity_replay_verification_audits["safety"]["executes_commands"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["creates_process"]
            and runner_audit_integrity_replay_verification_audits["safety"]["runner_implemented"]
            and runner_audit_integrity_replay_verification_audits["safety"]["launch_enabled"]
            and runner_audit_integrity_replay_verification_audits["safety"]["launch_api_available"]
            and runner_audit_integrity_replay_verification_audits["safety"]["integrity_replay_projection"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["integrity_replay_audit_only"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["writes_code"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["registers_post_api"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["registers_launch_api"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["registers_cancel_api"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["registers_timeout_api"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["implements_runner"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["implements_adapter"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["imports_adapter"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["calls_execution_adapter"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["creates_session"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["stores_session_state"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["mutates_session_state"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["reads_session_state_store"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["writes_session_state_store"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["cancels_process"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["sends_process_signal"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["kills_process"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["controls_process"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["schedules_timeout"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["opens_stdout_stderr"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["reads_stdout_stderr"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["captures_stdout_stderr"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["reads_runner_events"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["writes_runner_events"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["opens_runner_event_log"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["writes_event_log"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["opens_audit_log"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["reads_audit_log"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["writes_audit_log"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["stores_audit_records"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["reads_audit_records"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["reads_config_snapshots"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["performs_integrity_checks"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["performs_replay_checks"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["performs_consistency_checks"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["scans_log_directory"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["reads_log_files"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["writes_logs"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["collects_human_authorization"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["stores_authorization"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["grants_permission"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["writes_user_project"]
            and not runner_audit_integrity_replay_verification_audits["safety"]["creates_config_file"],
            "runner_audit_integrity_replay_verification_status": runner_audit_integrity_replay_verifications["status"],
            "runner_audit_integrity_replay_verification_integrity_check_count": (
                runner_audit_integrity_replay_verifications["summary"]["integrity_check_count"]
            ),
            "runner_audit_integrity_replay_verification_replay_check_count": (
                runner_audit_integrity_replay_verifications["summary"]["replay_check_count"]
            ),
            "runner_audit_integrity_replay_verification_consistency_check_count": (
                runner_audit_integrity_replay_verifications["summary"]["consistency_check_count"]
            ),
            "runner_audit_integrity_replay_verification_safe": (
                not runner_audit_integrity_replay_verifications["safety"]["executes_commands"]
                and not runner_audit_integrity_replay_verifications["safety"]["creates_process"]
                and runner_audit_integrity_replay_verifications["safety"]["integrity_replay_projection"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_audit_log"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_audit_records"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_runner_events"]
                and not runner_audit_integrity_replay_verifications["safety"]["opens_runner_event_log"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_config_snapshots"]
                and not runner_audit_integrity_replay_verifications["safety"]["performs_integrity_checks"]
                and not runner_audit_integrity_replay_verifications["safety"]["performs_replay_checks"]
                and not runner_audit_integrity_replay_verifications["safety"]["performs_consistency_checks"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_log_files"]
                and not runner_audit_integrity_replay_verifications["safety"]["writes_logs"]
                and not runner_audit_integrity_replay_verifications["safety"]["stores_authorization"]
                and not runner_audit_integrity_replay_verifications["safety"]["writes_user_project"]
            ),
            "runner_verification_discrepancy_report_audit_status": runner_verification_discrepancy_report_audits["status"],
            "runner_verification_discrepancy_report_audit_safe": not runner_verification_discrepancy_report_audits["safety"]["executes_commands"]
            and not runner_verification_discrepancy_report_audits["safety"]["creates_process"]
            and runner_verification_discrepancy_report_audits["safety"]["runner_implemented"]
            and runner_verification_discrepancy_report_audits["safety"]["launch_enabled"]
            and runner_verification_discrepancy_report_audits["safety"]["launch_api_available"]
            and runner_verification_discrepancy_report_audits["safety"]["discrepancy_report_projection"]
            and not runner_verification_discrepancy_report_audits["safety"]["discrepancy_report_audit_only"]
            and not runner_verification_discrepancy_report_audits["safety"]["writes_code"]
            and not runner_verification_discrepancy_report_audits["safety"]["registers_post_api"]
            and not runner_verification_discrepancy_report_audits["safety"]["registers_launch_api"]
            and not runner_verification_discrepancy_report_audits["safety"]["registers_cancel_api"]
            and not runner_verification_discrepancy_report_audits["safety"]["registers_timeout_api"]
            and not runner_verification_discrepancy_report_audits["safety"]["implements_runner"]
            and not runner_verification_discrepancy_report_audits["safety"]["implements_adapter"]
            and not runner_verification_discrepancy_report_audits["safety"]["imports_adapter"]
            and not runner_verification_discrepancy_report_audits["safety"]["calls_execution_adapter"]
            and not runner_verification_discrepancy_report_audits["safety"]["creates_session"]
            and not runner_verification_discrepancy_report_audits["safety"]["stores_session_state"]
            and not runner_verification_discrepancy_report_audits["safety"]["mutates_session_state"]
            and not runner_verification_discrepancy_report_audits["safety"]["reads_session_state_store"]
            and not runner_verification_discrepancy_report_audits["safety"]["writes_session_state_store"]
            and not runner_verification_discrepancy_report_audits["safety"]["cancels_process"]
            and not runner_verification_discrepancy_report_audits["safety"]["sends_process_signal"]
            and not runner_verification_discrepancy_report_audits["safety"]["kills_process"]
            and not runner_verification_discrepancy_report_audits["safety"]["controls_process"]
            and not runner_verification_discrepancy_report_audits["safety"]["schedules_timeout"]
            and not runner_verification_discrepancy_report_audits["safety"]["opens_stdout_stderr"]
            and not runner_verification_discrepancy_report_audits["safety"]["reads_stdout_stderr"]
            and not runner_verification_discrepancy_report_audits["safety"]["captures_stdout_stderr"]
            and not runner_verification_discrepancy_report_audits["safety"]["reads_runner_events"]
            and not runner_verification_discrepancy_report_audits["safety"]["writes_runner_events"]
            and not runner_verification_discrepancy_report_audits["safety"]["opens_runner_event_log"]
            and not runner_verification_discrepancy_report_audits["safety"]["writes_event_log"]
            and not runner_verification_discrepancy_report_audits["safety"]["opens_audit_log"]
            and not runner_verification_discrepancy_report_audits["safety"]["reads_audit_log"]
            and not runner_verification_discrepancy_report_audits["safety"]["writes_audit_log"]
            and not runner_verification_discrepancy_report_audits["safety"]["stores_audit_records"]
            and not runner_verification_discrepancy_report_audits["safety"]["reads_audit_records"]
            and not runner_verification_discrepancy_report_audits["safety"]["reads_config_snapshots"]
            and not runner_verification_discrepancy_report_audits["safety"]["performs_integrity_checks"]
            and not runner_verification_discrepancy_report_audits["safety"]["performs_replay_checks"]
            and not runner_verification_discrepancy_report_audits["safety"]["performs_consistency_checks"]
            and not runner_verification_discrepancy_report_audits["safety"]["generates_discrepancy_reports"]
            and not runner_verification_discrepancy_report_audits["safety"]["makes_blocking_decisions"]
            and not runner_verification_discrepancy_report_audits["safety"]["generates_operator_messages"]
            and not runner_verification_discrepancy_report_audits["safety"]["scans_log_directory"]
            and not runner_verification_discrepancy_report_audits["safety"]["reads_log_files"]
            and not runner_verification_discrepancy_report_audits["safety"]["writes_logs"]
            and not runner_verification_discrepancy_report_audits["safety"]["collects_human_authorization"]
            and not runner_verification_discrepancy_report_audits["safety"]["stores_authorization"]
            and not runner_verification_discrepancy_report_audits["safety"]["grants_permission"]
            and not runner_verification_discrepancy_report_audits["safety"]["writes_user_project"]
            and not runner_verification_discrepancy_report_audits["safety"]["creates_config_file"],
            "runner_verification_discrepancy_report_status": runner_verification_discrepancy_reports["status"],
            "runner_verification_discrepancy_report_count": (
                runner_verification_discrepancy_reports["summary"]["discrepancy_report_count"]
            ),
            "runner_verification_discrepancy_report_blocking_decision_count": (
                runner_verification_discrepancy_reports["summary"]["blocking_decision_count"]
            ),
            "runner_verification_discrepancy_report_operator_message_count": (
                runner_verification_discrepancy_reports["summary"]["operator_message_count"]
            ),
            "runner_verification_discrepancy_report_safe": (
                not runner_verification_discrepancy_reports["safety"]["executes_commands"]
                and not runner_verification_discrepancy_reports["safety"]["creates_process"]
                and runner_verification_discrepancy_reports["safety"]["discrepancy_report_projection"]
                and not runner_verification_discrepancy_reports["safety"]["reads_audit_log"]
                and not runner_verification_discrepancy_reports["safety"]["reads_audit_records"]
                and not runner_verification_discrepancy_reports["safety"]["reads_runner_events"]
                and not runner_verification_discrepancy_reports["safety"]["opens_runner_event_log"]
                and not runner_verification_discrepancy_reports["safety"]["reads_config_snapshots"]
                and not runner_verification_discrepancy_reports["safety"]["performs_integrity_checks"]
                and not runner_verification_discrepancy_reports["safety"]["performs_replay_checks"]
                and not runner_verification_discrepancy_reports["safety"]["performs_consistency_checks"]
                and not runner_verification_discrepancy_reports["safety"]["generates_discrepancy_reports"]
                and not runner_verification_discrepancy_reports["safety"]["makes_blocking_decisions"]
                and not runner_verification_discrepancy_reports["safety"]["writes_report_files"]
                and not runner_verification_discrepancy_reports["safety"]["reads_log_files"]
                and not runner_verification_discrepancy_reports["safety"]["writes_logs"]
                and not runner_verification_discrepancy_reports["safety"]["stores_authorization"]
                and not runner_verification_discrepancy_reports["safety"]["writes_user_project"]
            ),
            "runner_real_launch_final_gate_audit_status": runner_real_launch_final_gate_audits["status"],
            "runner_real_launch_final_gate_audit_safe": not runner_real_launch_final_gate_audits["safety"]["executes_commands"]
            and not runner_real_launch_final_gate_audits["safety"]["creates_process"]
            and not runner_real_launch_final_gate_audits["safety"]["runner_implemented"]
            and not runner_real_launch_final_gate_audits["safety"]["launch_enabled"]
            and not runner_real_launch_final_gate_audits["safety"]["launch_api_available"]
            and runner_real_launch_final_gate_audits["safety"]["final_launch_gate_audit_only"]
            and not runner_real_launch_final_gate_audits["safety"]["writes_code"]
            and not runner_real_launch_final_gate_audits["safety"]["registers_post_api"]
            and not runner_real_launch_final_gate_audits["safety"]["registers_launch_api"]
            and not runner_real_launch_final_gate_audits["safety"]["registers_cancel_api"]
            and not runner_real_launch_final_gate_audits["safety"]["registers_timeout_api"]
            and not runner_real_launch_final_gate_audits["safety"]["enables_launch_ui"]
            and not runner_real_launch_final_gate_audits["safety"]["implements_runner"]
            and not runner_real_launch_final_gate_audits["safety"]["imports_adapter"]
            and not runner_real_launch_final_gate_audits["safety"]["calls_execution_adapter"]
            and not runner_real_launch_final_gate_audits["safety"]["creates_session"]
            and not runner_real_launch_final_gate_audits["safety"]["mutates_session_state"]
            and not runner_real_launch_final_gate_audits["safety"]["controls_process"]
            and not runner_real_launch_final_gate_audits["safety"]["opens_stdout_stderr"]
            and not runner_real_launch_final_gate_audits["safety"]["reads_stdout_stderr"]
            and not runner_real_launch_final_gate_audits["safety"]["reads_runner_events"]
            and not runner_real_launch_final_gate_audits["safety"]["writes_runner_events"]
            and not runner_real_launch_final_gate_audits["safety"]["opens_audit_log"]
            and not runner_real_launch_final_gate_audits["safety"]["reads_audit_log"]
            and not runner_real_launch_final_gate_audits["safety"]["writes_audit_log"]
            and not runner_real_launch_final_gate_audits["safety"]["reads_audit_records"]
            and not runner_real_launch_final_gate_audits["safety"]["reads_config_snapshots"]
            and not runner_real_launch_final_gate_audits["safety"]["performs_integrity_checks"]
            and not runner_real_launch_final_gate_audits["safety"]["performs_replay_checks"]
            and not runner_real_launch_final_gate_audits["safety"]["generates_discrepancy_reports"]
            and not runner_real_launch_final_gate_audits["safety"]["makes_launch_decisions"]
            and not runner_real_launch_final_gate_audits["safety"]["reads_log_files"]
            and not runner_real_launch_final_gate_audits["safety"]["writes_logs"]
            and not runner_real_launch_final_gate_audits["safety"]["collects_human_authorization"]
            and not runner_real_launch_final_gate_audits["safety"]["stores_authorization"]
            and not runner_real_launch_final_gate_audits["safety"]["grants_permission"]
            and not runner_real_launch_final_gate_audits["safety"]["writes_user_project"]
            and not runner_real_launch_final_gate_audits["safety"]["creates_config_file"],
            "runner_evidence_gap_index_status": runner_evidence_gap_indexes["status"],
            "runner_evidence_gap_index_safe": not runner_evidence_gap_indexes["safety"]["executes_commands"]
            and not runner_evidence_gap_indexes["safety"]["creates_process"]
            and not runner_evidence_gap_indexes["safety"]["runner_implemented"]
            and not runner_evidence_gap_indexes["safety"]["launch_enabled"]
            and not runner_evidence_gap_indexes["safety"]["launch_api_available"]
            and runner_evidence_gap_indexes["safety"]["evidence_gap_index_only"]
            and not runner_evidence_gap_indexes["safety"]["registers_post_api"]
            and not runner_evidence_gap_indexes["safety"]["registers_launch_api"]
            and not runner_evidence_gap_indexes["safety"]["enables_launch_ui"]
            and not runner_evidence_gap_indexes["safety"]["imports_adapter"]
            and not runner_evidence_gap_indexes["safety"]["calls_execution_adapter"]
            and not runner_evidence_gap_indexes["safety"]["creates_session"]
            and not runner_evidence_gap_indexes["safety"]["mutates_session_state"]
            and not runner_evidence_gap_indexes["safety"]["opens_stdout_stderr"]
            and not runner_evidence_gap_indexes["safety"]["reads_runner_events"]
            and not runner_evidence_gap_indexes["safety"]["writes_runner_events"]
            and not runner_evidence_gap_indexes["safety"]["reads_audit_log"]
            and not runner_evidence_gap_indexes["safety"]["writes_audit_log"]
            and not runner_evidence_gap_indexes["safety"]["reads_audit_records"]
            and not runner_evidence_gap_indexes["safety"]["reads_config_snapshots"]
            and not runner_evidence_gap_indexes["safety"]["performs_integrity_checks"]
            and not runner_evidence_gap_indexes["safety"]["performs_replay_checks"]
            and not runner_evidence_gap_indexes["safety"]["generates_discrepancy_reports"]
            and not runner_evidence_gap_indexes["safety"]["makes_launch_decisions"]
            and not runner_evidence_gap_indexes["safety"]["reads_log_files"]
            and not runner_evidence_gap_indexes["safety"]["scans_log_directory"]
            and not runner_evidence_gap_indexes["safety"]["writes_logs"]
            and not runner_evidence_gap_indexes["safety"]["collects_human_authorization"]
            and not runner_evidence_gap_indexes["safety"]["stores_authorization"]
            and not runner_evidence_gap_indexes["safety"]["grants_permission"]
            and not runner_evidence_gap_indexes["safety"]["writes_user_project"]
            and not runner_evidence_gap_indexes["safety"]["creates_config_file"],
            "runner_development_path_anchor_status": runner_development_path_anchors["status"],
            "runner_development_path_anchor_current_phase": (
                runner_development_path_anchors["summary"]["current_phase"]
            ),
            "runner_development_path_anchor_completed_round_count": (
                runner_development_path_anchors["summary"]["completed_round_count"]
            ),
            "runner_development_path_anchor_locked_round_count": (
                runner_development_path_anchors["summary"]["locked_round_count"]
            ),
            "runner_development_path_anchor_launchable_count": (
                runner_development_path_anchors["summary"]["launchable_count"]
            ),
            "runner_development_path_anchor_safe": not runner_development_path_anchors["safety"]["executes_commands"]
            and not runner_development_path_anchors["safety"]["creates_process"]
            and not runner_development_path_anchors["safety"]["runner_implemented"]
            and not runner_development_path_anchors["safety"]["launch_enabled"]
            and not runner_development_path_anchors["safety"]["launch_api_available"]
            and runner_development_path_anchors["safety"]["development_path_anchor_only"]
            and not runner_development_path_anchors["safety"]["registers_post_api"]
            and not runner_development_path_anchors["safety"]["imports_adapter"]
            and not runner_development_path_anchors["safety"]["calls_execution_adapter"]
            and not runner_development_path_anchors["safety"]["writes_runner_events"]
            and not runner_development_path_anchors["safety"]["reads_log_files"]
            and not runner_development_path_anchors["safety"]["writes_logs"]
            and not runner_development_path_anchors["safety"]["writes_audit_log"]
            and not runner_development_path_anchors["safety"]["collects_human_authorization"]
            and not runner_development_path_anchors["safety"]["stores_authorization"]
            and not runner_development_path_anchors["safety"]["grants_permission"]
            and not runner_development_path_anchors["safety"]["writes_user_project"],
            "runner_process_lifecycle_status": runner_process_lifecycles["status"],
            "runner_process_lifecycle_session_state_count": (
                runner_process_lifecycles["summary"]["session_state_count"]
            ),
            "runner_process_lifecycle_pending_count": runner_process_lifecycles["summary"]["pending_count"],
            "runner_process_lifecycle_terminal_count": runner_process_lifecycles["summary"]["terminal_count"],
            "runner_process_lifecycle_safe": (
                not runner_process_lifecycles["safety"]["executes_commands"]
                and not runner_process_lifecycles["safety"]["creates_process"]
                and runner_process_lifecycles["safety"]["process_lifecycle_projection"]
                and not runner_process_lifecycles["safety"]["controls_process"]
                and not runner_process_lifecycles["safety"]["cancels_process"]
                and not runner_process_lifecycles["safety"]["schedules_timeout"]
                and not runner_process_lifecycles["safety"]["registers_cancel_api"]
                and not runner_process_lifecycles["safety"]["registers_timeout_api"]
                and not runner_process_lifecycles["safety"]["writes_user_project"]
            ),
            "runner_stream_capture_status": runner_stream_captures["status"],
            "runner_stream_capture_stream_count": runner_stream_captures["summary"]["stream_count"],
            "runner_stream_capture_captured_count": runner_stream_captures["summary"]["captured_stream_count"],
            "runner_stream_capture_pending_count": runner_stream_captures["summary"]["pending_stream_count"],
            "runner_stream_capture_safe": (
                not runner_stream_captures["safety"]["executes_commands"]
                and not runner_stream_captures["safety"]["creates_process"]
                and runner_stream_captures["safety"]["stream_capture_projection"]
                and not runner_stream_captures["safety"]["opens_stdout_stderr"]
                and not runner_stream_captures["safety"]["reads_stdout_stderr"]
                and not runner_stream_captures["safety"]["captures_stdout_stderr"]
                and not runner_stream_captures["safety"]["reads_log_files"]
                and not runner_stream_captures["safety"]["writes_logs"]
                and not runner_stream_captures["safety"]["writes_user_project"]
            ),
            "runner_event_writer_status": runner_event_writers["status"],
            "runner_event_writer_projected_event_count": runner_event_writers["summary"]["projected_event_count"],
            "runner_event_writer_terminal_event_count": runner_event_writers["summary"]["terminal_event_count"],
            "runner_event_writer_safe": (
                not runner_event_writers["safety"]["executes_commands"]
                and not runner_event_writers["safety"]["creates_process"]
                and runner_event_writers["safety"]["event_writer_projection"]
                and not runner_event_writers["safety"]["writes_runner_events"]
                and not runner_event_writers["safety"]["opens_runner_event_log"]
                and not runner_event_writers["safety"]["writes_event_log"]
                and not runner_event_writers["safety"]["reads_log_files"]
                and not runner_event_writers["safety"]["writes_logs"]
                and not runner_event_writers["safety"]["writes_user_project"]
            ),
            "runner_audit_persistence_status": runner_audit_persistences["status"],
            "runner_audit_persistence_audit_record_count": runner_audit_persistences["summary"]["audit_record_count"],
            "runner_audit_persistence_safe": (
                not runner_audit_persistences["safety"]["executes_commands"]
                and not runner_audit_persistences["safety"]["creates_process"]
                and runner_audit_persistences["safety"]["audit_persistence_projection"]
                and not runner_audit_persistences["safety"]["writes_audit_log"]
                and not runner_audit_persistences["safety"]["reads_audit_log"]
                and not runner_audit_persistences["safety"]["opens_runner_event_log"]
                and not runner_audit_persistences["safety"]["reads_log_files"]
                and not runner_audit_persistences["safety"]["writes_logs"]
                and not runner_audit_persistences["safety"]["stores_authorization"]
                and not runner_audit_persistences["safety"]["writes_user_project"]
            ),
            "runner_audit_integrity_replay_verification_status": runner_audit_integrity_replay_verifications["status"],
            "runner_audit_integrity_replay_verification_integrity_check_count": (
                runner_audit_integrity_replay_verifications["summary"]["integrity_check_count"]
            ),
            "runner_audit_integrity_replay_verification_replay_check_count": (
                runner_audit_integrity_replay_verifications["summary"]["replay_check_count"]
            ),
            "runner_audit_integrity_replay_verification_consistency_check_count": (
                runner_audit_integrity_replay_verifications["summary"]["consistency_check_count"]
            ),
            "runner_audit_integrity_replay_verification_safe": (
                not runner_audit_integrity_replay_verifications["safety"]["executes_commands"]
                and not runner_audit_integrity_replay_verifications["safety"]["creates_process"]
                and runner_audit_integrity_replay_verifications["safety"]["integrity_replay_projection"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_audit_log"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_audit_records"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_runner_events"]
                and not runner_audit_integrity_replay_verifications["safety"]["opens_runner_event_log"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_config_snapshots"]
                and not runner_audit_integrity_replay_verifications["safety"]["performs_integrity_checks"]
                and not runner_audit_integrity_replay_verifications["safety"]["performs_replay_checks"]
                and not runner_audit_integrity_replay_verifications["safety"]["performs_consistency_checks"]
                and not runner_audit_integrity_replay_verifications["safety"]["reads_log_files"]
                and not runner_audit_integrity_replay_verifications["safety"]["writes_logs"]
                and not runner_audit_integrity_replay_verifications["safety"]["stores_authorization"]
                and not runner_audit_integrity_replay_verifications["safety"]["writes_user_project"]
            ),
            "runner_verification_discrepancy_report_status": runner_verification_discrepancy_reports["status"],
            "runner_verification_discrepancy_report_count": (
                runner_verification_discrepancy_reports["summary"]["discrepancy_report_count"]
            ),
            "runner_verification_discrepancy_report_blocking_decision_count": (
                runner_verification_discrepancy_reports["summary"]["blocking_decision_count"]
            ),
            "runner_verification_discrepancy_report_operator_message_count": (
                runner_verification_discrepancy_reports["summary"]["operator_message_count"]
            ),
            "runner_verification_discrepancy_report_safe": (
                not runner_verification_discrepancy_reports["safety"]["executes_commands"]
                and not runner_verification_discrepancy_reports["safety"]["creates_process"]
                and runner_verification_discrepancy_reports["safety"]["discrepancy_report_projection"]
                and not runner_verification_discrepancy_reports["safety"]["reads_audit_log"]
                and not runner_verification_discrepancy_reports["safety"]["reads_audit_records"]
                and not runner_verification_discrepancy_reports["safety"]["reads_runner_events"]
                and not runner_verification_discrepancy_reports["safety"]["opens_runner_event_log"]
                and not runner_verification_discrepancy_reports["safety"]["reads_config_snapshots"]
                and not runner_verification_discrepancy_reports["safety"]["performs_integrity_checks"]
                and not runner_verification_discrepancy_reports["safety"]["performs_replay_checks"]
                and not runner_verification_discrepancy_reports["safety"]["performs_consistency_checks"]
                and not runner_verification_discrepancy_reports["safety"]["generates_discrepancy_reports"]
                and not runner_verification_discrepancy_reports["safety"]["makes_blocking_decisions"]
                and not runner_verification_discrepancy_reports["safety"]["writes_report_files"]
                and not runner_verification_discrepancy_reports["safety"]["reads_log_files"]
                and not runner_verification_discrepancy_reports["safety"]["writes_logs"]
                and not runner_verification_discrepancy_reports["safety"]["stores_authorization"]
                and not runner_verification_discrepancy_reports["safety"]["writes_user_project"]
            ),
            "runner_real_execution_touchpoint_inventory_status": (
                runner_real_execution_touchpoint_inventories["status"]
            ),
            "runner_real_execution_touchpoint_inventory_touchpoint_count": (
                runner_real_execution_touchpoint_inventories["summary"]["touchpoint_count"]
            ),
            "runner_real_execution_touchpoint_inventory_locked_count": (
                runner_real_execution_touchpoint_inventories["summary"]["locked_touchpoint_count"]
            ),
            "runner_real_execution_touchpoint_inventory_launchable_count": (
                runner_real_execution_touchpoint_inventories["summary"]["launchable_count"]
            ),
            "runner_real_execution_touchpoint_inventory_safe": (
                not runner_real_execution_touchpoint_inventories["safety"]["executes_commands"]
                and not runner_real_execution_touchpoint_inventories["safety"]["creates_process"]
                and not runner_real_execution_touchpoint_inventories["safety"]["runner_implemented"]
                and not runner_real_execution_touchpoint_inventories["safety"]["launch_enabled"]
                and not runner_real_execution_touchpoint_inventories["safety"]["launch_api_available"]
                and runner_real_execution_touchpoint_inventories["safety"]["touchpoint_inventory_only"]
                and not runner_real_execution_touchpoint_inventories["safety"]["creates_files"]
                and not runner_real_execution_touchpoint_inventories["safety"]["registers_post_api"]
                and not runner_real_execution_touchpoint_inventories["safety"]["enables_launch_ui"]
                and not runner_real_execution_touchpoint_inventories["safety"]["imports_adapter"]
                and not runner_real_execution_touchpoint_inventories["safety"]["calls_execution_adapter"]
                and not runner_real_execution_touchpoint_inventories["safety"]["creates_session"]
                and not runner_real_execution_touchpoint_inventories["safety"]["mutates_session_state"]
                and not runner_real_execution_touchpoint_inventories["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_touchpoint_inventories["safety"]["writes_runner_events"]
                and not runner_real_execution_touchpoint_inventories["safety"]["reads_log_files"]
                and not runner_real_execution_touchpoint_inventories["safety"]["writes_logs"]
                and not runner_real_execution_touchpoint_inventories["safety"]["writes_audit_log"]
                and not runner_real_execution_touchpoint_inventories["safety"]["collects_human_authorization"]
                and not runner_real_execution_touchpoint_inventories["safety"]["stores_authorization"]
                and not runner_real_execution_touchpoint_inventories["safety"]["grants_permission"]
                and not runner_real_execution_touchpoint_inventories["safety"]["writes_user_project"]
            ),
            "runner_real_execution_touchpoint_coverage_index_status": (
                runner_real_execution_touchpoint_coverage_indexes["status"]
            ),
            "runner_real_execution_touchpoint_coverage_index_entry_count": (
                runner_real_execution_touchpoint_coverage_indexes["summary"]["coverage_entry_count"]
            ),
            "runner_real_execution_touchpoint_coverage_index_locked_count": (
                runner_real_execution_touchpoint_coverage_indexes["summary"]["locked_entry_count"]
            ),
            "runner_real_execution_touchpoint_coverage_index_stage_count": (
                runner_real_execution_touchpoint_coverage_indexes["summary"]["mapped_stage_count"]
            ),
            "runner_real_execution_touchpoint_coverage_index_launchable_count": (
                runner_real_execution_touchpoint_coverage_indexes["summary"]["launchable_count"]
            ),
            "runner_real_execution_touchpoint_coverage_index_safe": (
                not runner_real_execution_touchpoint_coverage_indexes["safety"]["executes_commands"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["creates_process"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["runner_implemented"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["launch_enabled"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["launch_api_available"]
                and runner_real_execution_touchpoint_coverage_indexes["safety"]["touchpoint_coverage_index_only"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["creates_files"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["registers_post_api"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["enables_launch_ui"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["imports_adapter"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["calls_execution_adapter"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["creates_session"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["mutates_session_state"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["writes_runner_events"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["reads_log_files"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["writes_logs"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["writes_audit_log"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["collects_human_authorization"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["stores_authorization"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["grants_permission"]
                and not runner_real_execution_touchpoint_coverage_indexes["safety"]["writes_user_project"]
            ),
            "runner_real_execution_touchpoint_gap_link_status": runner_real_execution_touchpoint_gap_links["status"],
            "runner_real_execution_touchpoint_gap_link_entry_count": (
                runner_real_execution_touchpoint_gap_links["summary"]["link_entry_count"]
            ),
            "runner_real_execution_touchpoint_gap_link_locked_count": (
                runner_real_execution_touchpoint_gap_links["summary"]["locked_link_count"]
            ),
            "runner_real_execution_touchpoint_gap_link_launchable_count": (
                runner_real_execution_touchpoint_gap_links["summary"]["launchable_count"]
            ),
            "runner_real_execution_touchpoint_gap_link_safe": (
                not runner_real_execution_touchpoint_gap_links["safety"]["executes_commands"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["creates_process"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["runner_implemented"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["launch_enabled"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["launch_api_available"]
                and runner_real_execution_touchpoint_gap_links["safety"]["touchpoint_gap_link_only"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["creates_files"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["registers_post_api"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["enables_launch_ui"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["imports_adapter"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["calls_execution_adapter"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["creates_session"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["mutates_session_state"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["writes_runner_events"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["reads_log_files"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["writes_logs"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["writes_audit_log"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["collects_human_authorization"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["stores_authorization"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["grants_permission"]
                and not runner_real_execution_touchpoint_gap_links["safety"]["writes_user_project"]
            ),
            "runner_real_execution_touchpoint_unlock_matrix_status": (
                runner_real_execution_touchpoint_unlock_matrices["status"]
            ),
            "runner_real_execution_touchpoint_unlock_matrix_entry_count": (
                runner_real_execution_touchpoint_unlock_matrices["summary"]["matrix_entry_count"]
            ),
            "runner_real_execution_touchpoint_unlock_matrix_locked_count": (
                runner_real_execution_touchpoint_unlock_matrices["summary"]["locked_matrix_count"]
            ),
            "runner_real_execution_touchpoint_unlock_matrix_implementation_allowed_count": (
                runner_real_execution_touchpoint_unlock_matrices["summary"]["implementation_allowed_count"]
            ),
            "runner_real_execution_touchpoint_unlock_matrix_execution_allowed_count": (
                runner_real_execution_touchpoint_unlock_matrices["summary"]["execution_allowed_count"]
            ),
            "runner_real_execution_touchpoint_unlock_matrix_launchable_count": (
                runner_real_execution_touchpoint_unlock_matrices["summary"]["launchable_count"]
            ),
            "runner_real_execution_touchpoint_unlock_matrix_safe": (
                not runner_real_execution_touchpoint_unlock_matrices["safety"]["executes_commands"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["creates_process"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["runner_implemented"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["launch_enabled"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["launch_api_available"]
                and runner_real_execution_touchpoint_unlock_matrices["safety"]["touchpoint_unlock_matrix_only"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["creates_files"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["registers_post_api"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["enables_launch_ui"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["imports_adapter"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["calls_execution_adapter"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["creates_session"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["mutates_session_state"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["writes_runner_events"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["reads_log_files"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["writes_logs"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["writes_audit_log"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["collects_human_authorization"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["stores_authorization"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["grants_permission"]
                and not runner_real_execution_touchpoint_unlock_matrices["safety"]["writes_user_project"]
            ),
            "runner_real_execution_unlock_phrase_readiness_status": (
                runner_real_execution_unlock_phrase_readiness["status"]
            ),
            "runner_real_execution_unlock_phrase_readiness_required_phrase_count": (
                runner_real_execution_unlock_phrase_readiness["summary"]["required_phrase_count"]
            ),
            "runner_real_execution_unlock_phrase_readiness_observed_phrase_count": (
                runner_real_execution_unlock_phrase_readiness["summary"]["observed_phrase_count"]
            ),
            "runner_real_execution_unlock_phrase_readiness_matching_phrase_count": (
                runner_real_execution_unlock_phrase_readiness["summary"]["matching_phrase_count"]
            ),
            "runner_real_execution_unlock_phrase_readiness_accepted_phrase_count": (
                runner_real_execution_unlock_phrase_readiness["summary"]["accepted_phrase_count"]
            ),
            "runner_real_execution_unlock_phrase_readiness_implementation_allowed_count": (
                runner_real_execution_unlock_phrase_readiness["summary"]["implementation_allowed_count"]
            ),
            "runner_real_execution_unlock_phrase_readiness_execution_allowed_count": (
                runner_real_execution_unlock_phrase_readiness["summary"]["execution_allowed_count"]
            ),
            "runner_real_execution_unlock_phrase_readiness_launchable_count": (
                runner_real_execution_unlock_phrase_readiness["summary"]["launchable_count"]
            ),
            "runner_real_execution_unlock_phrase_readiness_safe": (
                not runner_real_execution_unlock_phrase_readiness["safety"]["executes_commands"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["creates_process"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["runner_implemented"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["launch_enabled"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["launch_api_available"]
                and runner_real_execution_unlock_phrase_readiness["safety"]["unlock_phrase_readiness_only"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["collects_unlock_phrase"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["stores_unlock_phrase"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["allows_real_execution_implementation"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["creates_files"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["registers_post_api"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["enables_launch_ui"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["imports_adapter"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["calls_execution_adapter"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["creates_session"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["mutates_session_state"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["writes_runner_events"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["reads_log_files"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["writes_logs"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["writes_audit_log"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["collects_human_authorization"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["stores_authorization"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["grants_permission"]
                and not runner_real_execution_unlock_phrase_readiness["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_status": (
                runner_real_execution_pre_unlock_evidence_packet_indexes["status"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_section_count": (
                runner_real_execution_pre_unlock_evidence_packet_indexes["summary"]["packet_section_count"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_review_ready_count": (
                runner_real_execution_pre_unlock_evidence_packet_indexes["summary"]["review_packet_ready_count"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_accepted_phrase_count": (
                runner_real_execution_pre_unlock_evidence_packet_indexes["summary"]["accepted_phrase_count"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_implementation_allowed_count": (
                runner_real_execution_pre_unlock_evidence_packet_indexes["summary"]["implementation_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_execution_allowed_count": (
                runner_real_execution_pre_unlock_evidence_packet_indexes["summary"]["execution_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_launchable_count": (
                runner_real_execution_pre_unlock_evidence_packet_indexes["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_evidence_packet_index_safe": (
                not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_evidence_packet_indexes["safety"][
                    "pre_unlock_evidence_packet_index_only"
                ]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["accepts_evidence_packet"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["collects_human_authorization"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_evidence_packet_indexes["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_status": (
                runner_real_execution_pre_unlock_review_checklists["status"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_item_count": (
                runner_real_execution_pre_unlock_review_checklists["summary"]["checklist_item_count"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_pending_count": (
                runner_real_execution_pre_unlock_review_checklists["summary"]["pending_item_count"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_accepted_count": (
                runner_real_execution_pre_unlock_review_checklists["summary"]["accepted_item_count"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_ready_count": (
                runner_real_execution_pre_unlock_review_checklists["summary"]["ready_item_count"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_implementation_allowed_count": (
                runner_real_execution_pre_unlock_review_checklists["summary"]["implementation_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_execution_allowed_count": (
                runner_real_execution_pre_unlock_review_checklists["summary"]["execution_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_launchable_count": (
                runner_real_execution_pre_unlock_review_checklists["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_review_checklist_safe": (
                not runner_real_execution_pre_unlock_review_checklists["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_review_checklists["safety"][
                    "pre_unlock_review_checklist_only"
                ]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["accepts_checklist_answers"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["accepts_evidence_packet"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["collects_human_authorization"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_review_checklists["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_status": (
                runner_real_execution_pre_unlock_reviewer_role_maps["status"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_entry_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["role_entry_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_unique_role_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["unique_role_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_assigned_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["assigned_role_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_accepted_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["accepted_role_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_ready_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["ready_role_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_implementation_allowed_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["implementation_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_execution_allowed_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["execution_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_launchable_count": (
                runner_real_execution_pre_unlock_reviewer_role_maps["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_role_map_safe": (
                not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["pre_unlock_reviewer_role_map_only"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["assigns_reviewer_roles"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["accepts_reviewer_roles"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["accepts_checklist_answers"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["accepts_evidence_packet"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["collects_human_authorization"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_reviewer_role_maps["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_status": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["status"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_entry_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["rubric_entry_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_unique_role_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["unique_role_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_required_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["required_signoff_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_accepted_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["accepted_signoff_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_ready_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["ready_signoff_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_implementation_allowed_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["implementation_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_execution_allowed_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["execution_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_launchable_count": (
                runner_real_execution_pre_unlock_reviewer_signoff_rubrics["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_reviewer_signoff_rubric_safe": (
                not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"][
                    "pre_unlock_reviewer_signoff_rubric_only"
                ]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"][
                    "accepts_reviewer_signoff"
                ]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["accepts_reviewer_roles"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"][
                    "accepts_checklist_answers"
                ]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["accepts_evidence_packet"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_reviewer_signoff_rubrics["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_status": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["status"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_entry_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["binding_entry_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_unique_role_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["unique_role_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_checklist_link_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["checklist_link_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_packet_section_link_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["packet_section_link_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_accepted_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["accepted_binding_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_ready_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["ready_binding_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_implementation_allowed_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["implementation_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_execution_allowed_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["execution_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_launchable_count": (
                runner_real_execution_pre_unlock_signoff_evidence_bindings["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_signoff_evidence_binding_safe": (
                not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"][
                    "pre_unlock_signoff_evidence_binding_only"
                ]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"][
                    "accepts_signoff_evidence_bindings"
                ]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"][
                    "accepts_reviewer_signoff"
                ]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["accepts_reviewer_roles"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"][
                    "accepts_checklist_answers"
                ]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["accepts_evidence_packet"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_signoff_evidence_bindings["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_status": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["status"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_entry_count": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["summary"]["ledger_entry_count"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_locked_count": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["summary"]["locked_entry_count"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_blocking_count": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["summary"]["blocking_entry_count"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_accepted_count": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["summary"]["accepted_entry_count"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_ready_count": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["summary"]["ready_entry_count"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_round_10_allowed_count": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["summary"]["round_10_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_launchable_count": (
                runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_safe": (
                not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"][
                    "pre_unlock_implementation_entry_readiness_ledger_only"
                ]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"][
                    "allows_round_10_entry"
                ]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"][
                    "accepts_unlock_phrase"
                ]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"][
                    "accepts_reviewer_signoff"
                ]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_implementation_entry_readiness_ledgers["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_status": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["status"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_entry_count": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["summary"]["preview_entry_count"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_minimal_touch_count": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["summary"]["minimal_touch_count"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_deferred_count": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["summary"]["explicitly_deferred_count"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_accepted_count": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["summary"]["accepted_preview_count"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_ready_count": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["summary"]["ready_preview_count"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_round_10_allowed_count": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["summary"]["round_10_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_launchable_count": (
                runner_real_execution_pre_unlock_round10_minimal_scope_previews["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_round10_minimal_scope_preview_safe": (
                not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"][
                    "pre_unlock_round10_minimal_scope_preview_only"
                ]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["allows_round_10_entry"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_round10_minimal_scope_previews["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_status": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["status"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_entry_count": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["summary"]["receipt_entry_count"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_required_count": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["summary"]["required_receipt_count"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_observed_count": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["summary"]["observed_receipt_count"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_accepted_count": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["summary"]["accepted_receipt_count"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_ready_count": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["summary"]["ready_receipt_count"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_round_10_allowed_count": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["summary"]["round_10_allowed_count"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_launchable_count": (
                runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_safe": (
                not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["executes_commands"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["creates_process"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["runner_implemented"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["launch_enabled"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["launch_api_available"]
                and runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "pre_unlock_explicit_unlock_handoff_receipt_only"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "collects_unlock_receipt"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "stores_unlock_receipt"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "accepts_unlock_receipt"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "accepts_unlock_phrase"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["allows_round_10_entry"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["creates_files"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["registers_post_api"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["imports_adapter"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "calls_execution_adapter"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["creates_session"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["reads_log_files"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["writes_logs"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["stores_authorization"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["grants_permission"]
                and not runner_real_execution_pre_unlock_explicit_unlock_handoff_receipts["safety"]["writes_user_project"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_status": (
                runner_real_execution_pre_round10_locked_handoff_summaries["status"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_entry_count": (
                runner_real_execution_pre_round10_locked_handoff_summaries["summary"]["handoff_summary_entry_count"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_locked_count": (
                runner_real_execution_pre_round10_locked_handoff_summaries["summary"]["locked_entry_count"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_blocking_count": (
                runner_real_execution_pre_round10_locked_handoff_summaries["summary"]["blocking_entry_count"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_accepted_count": (
                runner_real_execution_pre_round10_locked_handoff_summaries["summary"]["accepted_summary_count"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_ready_count": (
                runner_real_execution_pre_round10_locked_handoff_summaries["summary"]["ready_summary_count"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_round_10_allowed_count": (
                runner_real_execution_pre_round10_locked_handoff_summaries["summary"]["round_10_allowed_count"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_launchable_count": (
                runner_real_execution_pre_round10_locked_handoff_summaries["summary"]["launchable_count"]
            ),
            "runner_real_execution_pre_round10_locked_handoff_summary_safe": (
                not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["executes_commands"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["creates_process"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["runner_implemented"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["launch_enabled"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["launch_api_available"]
                and runner_real_execution_pre_round10_locked_handoff_summaries["safety"][
                    "pre_round10_locked_handoff_summary_only"
                ]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["accepts_handoff_summary"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["accepts_authorization"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["allows_round_10_entry"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["creates_files"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["registers_post_api"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["enables_launch_ui"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["imports_adapter"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["calls_execution_adapter"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["creates_session"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["mutates_session_state"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["writes_runner_events"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["reads_log_files"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["writes_logs"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["writes_audit_log"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["stores_authorization"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["grants_permission"]
                and not runner_real_execution_pre_round10_locked_handoff_summaries["safety"]["writes_user_project"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_status": (
                runner_real_execution_round10_explicit_unlock_checkpoints["status"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_entry_count": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"]["checkpoint_entry_count"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_required_count": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"]["required_checkpoint_count"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_externally_satisfied_count": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"][
                    "externally_satisfied_checkpoint_count"
                ]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_accepted_count": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"]["accepted_checkpoint_count"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_ready_count": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"]["ready_checkpoint_count"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_round_10_allowed_count": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"]["round_10_allowed_count"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_launchable_count": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"]["launchable_count"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_external_satisfied": (
                runner_real_execution_round10_explicit_unlock_checkpoints["summary"]["external_unlock_satisfied"]
            ),
            "runner_real_execution_round10_explicit_unlock_checkpoint_safe": (
                not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["executes_commands"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["creates_process"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["runner_implemented"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["launch_enabled"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["launch_api_available"]
                and runner_real_execution_round10_explicit_unlock_checkpoints["safety"][
                    "round10_explicit_unlock_checkpoint_only"
                ]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["collects_unlock_input"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["stores_unlock_input"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["accepts_unlock_input"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["external_unlock_satisfied"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["accepts_authorization"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["allows_round_10_entry"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["creates_files"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["registers_post_api"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["enables_launch_ui"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["imports_adapter"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["calls_execution_adapter"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["creates_session"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["mutates_session_state"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["writes_runner_events"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["reads_log_files"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["writes_logs"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["writes_audit_log"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["stores_authorization"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["grants_permission"]
                and not runner_real_execution_round10_explicit_unlock_checkpoints["safety"]["writes_user_project"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_status": (
                runner_real_execution_round10_unlock_decision_mirrors["status"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_entry_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["decision_entry_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_locked_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["locked_decision_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_not_allowed_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["not_allowed_decision_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_accepted_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["accepted_decision_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_ready_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["ready_decision_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_external_satisfied_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["external_unlock_satisfied_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_round_10_allowed_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["round_10_allowed_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_launchable_count": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["launchable_count"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_can_enter_round_10": (
                runner_real_execution_round10_unlock_decision_mirrors["summary"]["can_enter_round_10"]
            ),
            "runner_real_execution_round10_unlock_decision_mirror_safe": (
                not runner_real_execution_round10_unlock_decision_mirrors["safety"]["executes_commands"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["creates_process"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["runner_implemented"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["launch_enabled"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["launch_api_available"]
                and runner_real_execution_round10_unlock_decision_mirrors["safety"][
                    "round10_unlock_decision_mirror_only"
                ]
                and runner_real_execution_round10_unlock_decision_mirrors["safety"]["mirrors_decision_only"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["collects_unlock_input"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["stores_unlock_input"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["accepts_unlock_input"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["external_unlock_satisfied"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["accepts_unlock_phrase"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["accepts_authorization"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["grants_permission"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["allows_round_10_entry"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"][
                    "allows_real_execution_implementation"
                ]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["creates_files"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["registers_post_api"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["registers_launch_api"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["registers_cancel_api"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["registers_timeout_api"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["enables_launch_ui"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["implements_adapter"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["imports_adapter"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["calls_execution_adapter"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["creates_session"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["mutates_session_state"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["opens_stdout_stderr"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["writes_runner_events"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["reads_log_files"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["writes_logs"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["writes_audit_log"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"][
                    "collects_human_authorization"
                ]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["stores_authorization"]
                and not runner_real_execution_round10_unlock_decision_mirrors["safety"]["writes_user_project"]
            ),
        }
        results.append(result)
        failures.extend(_sample_failures(result, expected))

    store_result = _verify_run_profile_store()
    failures.extend(store_result["failures"])

    print(json.dumps({"results": results, "run_profile_store": store_result, "failures": failures}, ensure_ascii=False, indent=2))
    return 1 if failures else 0


def _verify_run_profile_store() -> dict[str, object]:
    from flowtrace.integration_plan import build_project_integration_plan
    from flowtrace.interpretation import build_project_coverage, build_run_issues
    from flowtrace.audit import build_project_audit
    from flowtrace.execution_request import build_project_execution_requests
    from flowtrace.execution_request_store import (
        confirm_execution_request,
        load_execution_requests,
        prepare_execution_request,
        remove_execution_request,
        revoke_execution_request_confirmation,
    )
    from flowtrace.readiness import build_project_readiness
    from flowtrace.run_confirmation_store import confirm_run_profile, revoke_run_confirmation
    from flowtrace.run_execution_gate import build_project_run_execution_gate
    from flowtrace.run_final_confirmation_store import confirm_run_final_execution, revoke_run_final_confirmation
    from flowtrace.run_preflight import build_project_run_preflight
    from flowtrace.run_profile import build_project_run_profiles
    from flowtrace.run_profile_store import annotate_run_profiles, remove_run_profile, save_run_profile
    from flowtrace.runner_dry_run import build_project_runner_dry_runs
    from flowtrace.runner_dry_run_store import prepare_runner_dry_run, remove_runner_dry_run
    from flowtrace.runner_audit_persistence_implementation_audit import (
        build_project_runner_audit_persistence_implementation_audits,
    )
    from flowtrace.runner_audit_integrity_replay_verification_audit import (
        build_project_runner_audit_integrity_replay_verification_audits,
    )
    from flowtrace.runner_authorization_unlock_audit import build_project_runner_authorization_unlock_audits
    from flowtrace.runner_cancel_timeout_contract import build_project_runner_cancel_timeout_contracts
    from flowtrace.runner_cancel_timeout_real_api import build_project_runner_cancel_timeout_real_apis
    from flowtrace.runner_first_real_test import build_project_runner_first_real_tests
    from flowtrace.runner_execution_adapter_contract import build_project_runner_execution_adapter_contracts
    from flowtrace.runner_execution_adapter_implementation_audit import (
        build_project_runner_execution_adapter_implementation_audits,
    )
    from flowtrace.runner_execution_adapter_review import build_project_runner_execution_adapter_reviews
    from flowtrace.runner_event_writer_implementation_audit import (
        build_project_runner_event_writer_implementation_audits,
    )
    from flowtrace.runner_config_compatibility_report import build_project_runner_config_compatibility_reports
    from flowtrace.runner_config_field_contract_view import build_project_runner_config_field_contract_views
    from flowtrace.runner_config_field_coverage_index import build_project_runner_config_field_coverage_indexes
    from flowtrace.runner_config_remediation_summary import build_project_runner_config_remediation_summaries
    from flowtrace.runner_config_schema_stabilization import build_project_runner_config_schema_stabilizations
    from flowtrace.runner_execution_config import build_project_runner_execution_configs
    from flowtrace.runner_execution_config_check import build_project_runner_execution_config_checks
    from flowtrace.runner_final_block_matrix import build_project_runner_final_block_matrices
    from flowtrace.runner_governance_readiness import build_project_runner_governance_readiness
    from flowtrace.runner_implementation_gap_checklist import build_project_runner_implementation_gap_checklists
    from flowtrace.runner_launch_api_contract import build_project_runner_launch_api_contracts
    from flowtrace.runner_launch_control import build_project_runner_launch_controls
    from flowtrace.runner_log_cleanup_audit_trail import build_project_runner_log_cleanup_audit_trails
    from flowtrace.runner_log_cleanup_confirmation import build_project_runner_log_cleanup_confirmations
    from flowtrace.runner_log_cleanup_execution_plan import build_project_runner_log_cleanup_execution_plans
    from flowtrace.runner_log_cleanup_preview import build_project_runner_log_cleanup_previews
    from flowtrace.runner_log_directory_policy import build_project_runner_log_directory_policies
    from flowtrace.runner_log_retention_policy import build_project_runner_log_retention_policies
    from flowtrace.runner_plan import build_project_runner_plan
    from flowtrace.runner_process_lifecycle_implementation_audit import (
        build_project_runner_process_lifecycle_implementation_audits,
    )
    from flowtrace.runner_real_execution_adapter import launch_low_risk_sample_profile
    from flowtrace.runner_real_execution_store import (
        append_runner_real_execution,
        build_project_runner_real_executions,
        load_runner_real_executions,
    )
    from flowtrace.runner_runtime_policy import build_project_runner_runtime_policies
    from flowtrace.runner_service_flag_audit import build_project_runner_service_flag_audits
    from flowtrace.runner_session_state_schema import build_project_runner_session_state_schemas
    from flowtrace.runner_real_execution_implementation_plan import build_project_runner_real_execution_implementation_plans
    from flowtrace.runner_real_execution_scope_diff_audit import build_project_runner_real_execution_scope_diff_audits
    from flowtrace.runner_real_execution_stage_boundary_review import (
        build_project_runner_real_execution_stage_boundary_reviews,
    )
    from flowtrace.runner_real_execution_unlock_material_review import (
        build_project_runner_real_execution_unlock_material_reviews,
    )
    from flowtrace.runner_real_test_authorization_package import build_project_runner_real_test_authorization_packages
    from flowtrace.runner_real_test_authorization_checklist import build_project_runner_real_test_authorization_checklists
    from flowtrace.runner_real_test_final_checklist import build_project_runner_real_test_final_checklists
    from flowtrace.runner_real_test_readiness import build_project_runner_real_test_readiness
    from flowtrace.runner_real_test_sandbox_policy import build_project_runner_real_test_sandbox_policies
    from flowtrace.runner_real_test_ui_preview import build_project_runner_real_test_ui_previews
    from flowtrace.runner_stream_capture_implementation_audit import (
        build_project_runner_stream_capture_implementation_audits,
    )
    from flowtrace.runner_verification_discrepancy_report_audit import (
        build_project_runner_verification_discrepancy_report_audits,
    )
    from flowtrace.runner_real_launch_final_gate_audit import build_project_runner_real_launch_final_gate_audits
    from flowtrace.runner_evidence_gap_index import build_project_runner_evidence_gap_indexes
    from flowtrace.runner_launch_snapshot import build_project_runner_launch_snapshots
    from flowtrace.runner_launch_snapshot_store import prepare_runner_launch_snapshot, remove_runner_launch_snapshot
    from flowtrace.runner_session import build_project_runner_sessions
    from flowtrace.runner_session_store import prepare_runner_session, remove_runner_session
    from flowtrace.scanner import scan_project
    from flowtrace.storage import list_runs, read_events

    root = SAMPLES_ROOT / "ecommerce_checkout"
    trace_dir = root / ".flowtrace"
    project_model = scan_project(root)
    project_model["context"] = {"schema_version": "project_context.v1", "root": str(root), "trace_dir": str(trace_dir)}
    runs = list_runs(trace_dir)
    events_by_run = [read_events(run["run_id"], trace_dir) for run in runs]
    coverage = build_project_coverage(project_model, events_by_run)
    issues_by_run = [
        {"run_id": run["run_id"], "label": run.get("label"), "issues": build_run_issues(events)}
        for run, events in zip(runs, events_by_run)
    ]
    readiness = build_project_readiness(project_model, coverage, runs, issues_by_run)
    audit = build_project_audit(project_model, readiness, coverage, runs, issues_by_run)
    integration_plan = build_project_integration_plan(project_model, coverage, readiness, audit)
    run_profiles = build_project_run_profiles(project_model, integration_plan)
    failures = []
    with tempfile.TemporaryDirectory(prefix="flowtrace_run_profile_store_") as directory:
        temporary_trace_dir = Path(directory)
        profile = run_profiles["profiles"][0]
        saved_store = save_run_profile(temporary_trace_dir, profile)
        annotated = annotate_run_profiles(run_profiles, saved_store)
        saved_profile = next((item for item in annotated["profiles"] if item["id"] == profile["id"]), {})
        preflight = build_project_run_preflight(project_model["context"], annotated)
        report = preflight["reports"][0] if preflight["reports"] else {}
        confirmed_store = confirm_run_profile(temporary_trace_dir, saved_profile, report)
        confirmed_preflight = build_project_run_preflight(project_model["context"], annotated, confirmed_store)
        execution_gate = build_project_run_execution_gate(project_model["context"], annotated, confirmed_preflight)
        final_store = confirm_run_final_execution(temporary_trace_dir, saved_profile, confirmed_preflight["reports"][0])
        confirmed_execution_gate = build_project_run_execution_gate(
            project_model["context"],
            annotated,
            confirmed_preflight,
            final_store,
        )
        runner_plan = build_project_runner_plan(project_model["context"], annotated, confirmed_execution_gate)
        empty_execution_requests = build_project_execution_requests(project_model["context"], annotated, runner_plan)
        runner_report = runner_plan["reports"][0]
        prepared_store = prepare_execution_request(temporary_trace_dir, saved_profile, runner_report)
        prepared_execution_requests = build_project_execution_requests(
            project_model["context"],
            annotated,
            runner_plan,
            prepared_store,
        )
        second_confirmed_store = confirm_execution_request(temporary_trace_dir, saved_profile, runner_report)
        second_confirmed_execution_requests = build_project_execution_requests(
            project_model["context"],
            annotated,
            runner_plan,
            second_confirmed_store,
        )
        empty_runner_sessions = build_project_runner_sessions(
            project_model["context"],
            annotated,
            second_confirmed_execution_requests,
        )
        runner_session_store = prepare_runner_session(
            temporary_trace_dir,
            saved_profile,
            second_confirmed_execution_requests["reports"][0],
        )
        drafted_runner_sessions = build_project_runner_sessions(
            project_model["context"],
            annotated,
            second_confirmed_execution_requests,
            runner_session_store,
        )
        empty_launch_snapshots = build_project_runner_launch_snapshots(
            project_model["context"],
            annotated,
            drafted_runner_sessions,
        )
        launch_snapshot_store = prepare_runner_launch_snapshot(
            temporary_trace_dir,
            saved_profile,
            drafted_runner_sessions["reports"][0],
        )
        snapshotted_launch_snapshots = build_project_runner_launch_snapshots(
            project_model["context"],
            annotated,
            drafted_runner_sessions,
            launch_snapshot_store,
        )
        empty_dry_runs = build_project_runner_dry_runs(
            project_model["context"],
            annotated,
            snapshotted_launch_snapshots,
        )
        dry_run_store = prepare_runner_dry_run(
            temporary_trace_dir,
            saved_profile,
            snapshotted_launch_snapshots["reports"][0],
        )
        prepared_dry_runs = build_project_runner_dry_runs(
            project_model["context"],
            annotated,
            snapshotted_launch_snapshots,
            dry_run_store,
        )
        launch_controls = build_project_runner_launch_controls(project_model["context"], annotated, prepared_dry_runs)
        runtime_policies = build_project_runner_runtime_policies(project_model["context"], annotated, launch_controls)
        execution_configs = build_project_runner_execution_configs(project_model["context"], annotated, runtime_policies)
        missing_config_checks = build_project_runner_execution_config_checks(
            project_model["context"],
            annotated,
            execution_configs,
        )
        temporary_project_context = dict(project_model["context"])
        temporary_project_context["trace_dir"] = str(temporary_trace_dir)
        config_file = temporary_trace_dir / "flowtrace.runner.json"
        config_file.write_text("{", encoding="utf-8")
        invalid_json_config_checks = build_project_runner_execution_config_checks(
            temporary_project_context,
            annotated,
            execution_configs,
        )
        config_file.write_text(json.dumps(_bad_runner_config(), ensure_ascii=False), encoding="utf-8")
        bad_config_checks = build_project_runner_execution_config_checks(
            temporary_project_context,
            annotated,
            execution_configs,
        )
        config_file.write_text(json.dumps(_valid_runner_config(), ensure_ascii=False), encoding="utf-8")
        present_config_checks = build_project_runner_execution_config_checks(
            temporary_project_context,
            annotated,
            execution_configs,
        )
        real_executions = build_project_runner_real_executions(
            temporary_project_context,
            annotated,
            prepared_dry_runs,
        )
        cancel_timeout_real_apis = build_project_runner_cancel_timeout_real_apis(
            temporary_project_context,
            annotated,
            real_executions,
        )
        first_real_tests_before_launch = build_project_runner_first_real_tests(
            temporary_project_context,
            annotated,
            real_executions,
        )
        temporary_launch_profile = {**saved_profile, "env": {"FLOWTRACE_DIR": str(temporary_trace_dir)}}
        first_execution = launch_low_risk_sample_profile(
            temporary_project_context,
            temporary_launch_profile,
            prepared_dry_runs["reports"][0],
            "RUN TARGET PROJECT",
        )
        append_runner_real_execution(temporary_trace_dir, first_execution)
        real_executions_after_launch = build_project_runner_real_executions(
            temporary_project_context,
            annotated,
            prepared_dry_runs,
            load_runner_real_executions(temporary_trace_dir),
        )
        first_real_tests_after_launch = build_project_runner_first_real_tests(
            temporary_project_context,
            annotated,
            real_executions_after_launch,
        )
        config_schema_stabilizations = build_project_runner_config_schema_stabilizations(
            temporary_project_context,
            annotated,
            execution_configs,
            present_config_checks,
        )
        config_field_contract_views = build_project_runner_config_field_contract_views(
            temporary_project_context,
            config_schema_stabilizations,
        )
        config_compatibility_reports = build_project_runner_config_compatibility_reports(
            temporary_project_context,
            annotated,
            config_schema_stabilizations,
            present_config_checks,
        )
        bad_config_compatibility_reports = build_project_runner_config_compatibility_reports(
            temporary_project_context,
            annotated,
            config_schema_stabilizations,
            bad_config_checks,
        )
        config_remediation_summaries = build_project_runner_config_remediation_summaries(
            temporary_project_context,
            config_compatibility_reports,
        )
        config_field_coverage_indexes = build_project_runner_config_field_coverage_indexes(
            temporary_project_context,
            config_field_contract_views,
            config_compatibility_reports,
            config_remediation_summaries,
        )
        service_flag_audits = build_project_runner_service_flag_audits(
            temporary_project_context,
            annotated,
            present_config_checks,
        )
        log_directory_policies = build_project_runner_log_directory_policies(
            temporary_project_context,
            annotated,
            service_flag_audits,
        )
        log_retention_policies = build_project_runner_log_retention_policies(
            temporary_project_context,
            annotated,
            log_directory_policies,
        )
        log_cleanup_previews = build_project_runner_log_cleanup_previews(
            temporary_project_context,
            annotated,
            log_retention_policies,
        )
        log_cleanup_confirmations = build_project_runner_log_cleanup_confirmations(
            temporary_project_context,
            annotated,
            log_cleanup_previews,
        )
        log_cleanup_audit_trails = build_project_runner_log_cleanup_audit_trails(
            temporary_project_context,
            annotated,
            log_cleanup_confirmations,
        )
        log_cleanup_execution_plans = build_project_runner_log_cleanup_execution_plans(
            temporary_project_context,
            annotated,
            log_cleanup_audit_trails,
        )
        governance_readiness = build_project_runner_governance_readiness(
            temporary_project_context,
            annotated,
            _governance_layers(
                preflight,
                confirmed_execution_gate,
                runner_plan,
                second_confirmed_execution_requests,
                drafted_runner_sessions,
                snapshotted_launch_snapshots,
                prepared_dry_runs,
                launch_controls,
                runtime_policies,
                execution_configs,
                present_config_checks,
                config_schema_stabilizations,
                config_field_contract_views,
                config_compatibility_reports,
                config_remediation_summaries,
                config_field_coverage_indexes,
                service_flag_audits,
                log_directory_policies,
                log_retention_policies,
                log_cleanup_previews,
                log_cleanup_confirmations,
                log_cleanup_audit_trails,
                log_cleanup_execution_plans,
            ),
        )
        execution_adapter_contracts = build_project_runner_execution_adapter_contracts(
            temporary_project_context,
            annotated,
            governance_readiness,
        )
        launch_api_contracts = build_project_runner_launch_api_contracts(
            temporary_project_context,
            annotated,
            execution_adapter_contracts,
        )
        execution_adapter_reviews = build_project_runner_execution_adapter_reviews(
            temporary_project_context,
            annotated,
            launch_api_contracts,
        )
        final_block_matrices = build_project_runner_final_block_matrices(
            temporary_project_context,
            annotated,
            execution_adapter_reviews,
        )
        authorization_unlock_audits = build_project_runner_authorization_unlock_audits(
            temporary_project_context,
            annotated,
            final_block_matrices,
        )
        implementation_gap_checklists = build_project_runner_implementation_gap_checklists(
            temporary_project_context,
            annotated,
            authorization_unlock_audits,
        )
        cancel_timeout_contracts = build_project_runner_cancel_timeout_contracts(
            temporary_project_context,
            annotated,
            implementation_gap_checklists,
        )
        session_state_schemas = build_project_runner_session_state_schemas(
            temporary_project_context,
            annotated,
            cancel_timeout_contracts,
        )
        real_test_readiness = build_project_runner_real_test_readiness(
            temporary_project_context,
            annotated,
            session_state_schemas,
        )
        real_test_authorization_checklists = build_project_runner_real_test_authorization_checklists(
            temporary_project_context,
            annotated,
            real_test_readiness,
        )
        real_test_authorization_packages = build_project_runner_real_test_authorization_packages(
            temporary_project_context,
            annotated,
            real_test_authorization_checklists,
        )
        real_test_sandbox_policies = build_project_runner_real_test_sandbox_policies(
            temporary_project_context,
            annotated,
            real_test_authorization_packages,
        )
        real_test_final_checklists = build_project_runner_real_test_final_checklists(
            temporary_project_context,
            annotated,
            real_test_sandbox_policies,
        )
        real_test_ui_previews = build_project_runner_real_test_ui_previews(
            temporary_project_context,
            annotated,
            real_test_final_checklists,
        )
        real_execution_stage_boundary_reviews = build_project_runner_real_execution_stage_boundary_reviews(
            temporary_project_context,
            annotated,
            real_test_ui_previews,
        )
        real_execution_unlock_material_reviews = build_project_runner_real_execution_unlock_material_reviews(
            temporary_project_context,
            annotated,
            real_execution_stage_boundary_reviews,
        )
        real_execution_implementation_plans = build_project_runner_real_execution_implementation_plans(
            temporary_project_context,
            annotated,
            real_execution_unlock_material_reviews,
        )
        real_execution_scope_diff_audits = build_project_runner_real_execution_scope_diff_audits(
            temporary_project_context,
            annotated,
            real_execution_implementation_plans,
        )
        execution_adapter_implementation_audits = build_project_runner_execution_adapter_implementation_audits(
            temporary_project_context,
            annotated,
            real_execution_scope_diff_audits,
        )
        process_lifecycle_implementation_audits = build_project_runner_process_lifecycle_implementation_audits(
            temporary_project_context,
            annotated,
            execution_adapter_implementation_audits,
        )
        stream_capture_implementation_audits = build_project_runner_stream_capture_implementation_audits(
            temporary_project_context,
            annotated,
            process_lifecycle_implementation_audits,
        )
        event_writer_implementation_audits = build_project_runner_event_writer_implementation_audits(
            temporary_project_context,
            annotated,
            stream_capture_implementation_audits,
        )
        audit_persistence_implementation_audits = build_project_runner_audit_persistence_implementation_audits(
            temporary_project_context,
            annotated,
            event_writer_implementation_audits,
        )
        integrity_replay_verification_audits = build_project_runner_audit_integrity_replay_verification_audits(
            temporary_project_context,
            annotated,
            audit_persistence_implementation_audits,
        )
        verification_discrepancy_report_audits = build_project_runner_verification_discrepancy_report_audits(
            temporary_project_context,
            annotated,
            integrity_replay_verification_audits,
        )
        real_launch_final_gate_audits = build_project_runner_real_launch_final_gate_audits(
            temporary_project_context,
            annotated,
            verification_discrepancy_report_audits,
        )
        evidence_gap_indexes = build_project_runner_evidence_gap_indexes(
            temporary_project_context,
            annotated,
            real_launch_final_gate_audits,
        )
        revoked_request_store = revoke_execution_request_confirmation(temporary_trace_dir, profile["id"])
        revoked_execution_requests = build_project_execution_requests(
            project_model["context"],
            annotated,
            runner_plan,
            revoked_request_store,
        )
        stale_runner_sessions = build_project_runner_sessions(
            project_model["context"],
            annotated,
            revoked_execution_requests,
            runner_session_store,
        )
        removed_runner_session_store = remove_runner_session(temporary_trace_dir, profile["id"])
        removed_runner_sessions = build_project_runner_sessions(
            project_model["context"],
            annotated,
            second_confirmed_execution_requests,
            removed_runner_session_store,
        )
        stale_launch_snapshots = build_project_runner_launch_snapshots(
            project_model["context"],
            annotated,
            removed_runner_sessions,
            launch_snapshot_store,
        )
        removed_launch_snapshot_store = remove_runner_launch_snapshot(temporary_trace_dir, profile["id"])
        removed_launch_snapshots = build_project_runner_launch_snapshots(
            project_model["context"],
            annotated,
            drafted_runner_sessions,
            removed_launch_snapshot_store,
        )
        stale_dry_runs = build_project_runner_dry_runs(
            project_model["context"],
            annotated,
            removed_launch_snapshots,
            dry_run_store,
        )
        removed_dry_run_store = remove_runner_dry_run(temporary_trace_dir, profile["id"])
        removed_dry_runs = build_project_runner_dry_runs(
            project_model["context"],
            annotated,
            snapshotted_launch_snapshots,
            removed_dry_run_store,
        )
        removed_request_store = remove_execution_request(temporary_trace_dir, profile["id"])
        removed_execution_requests = build_project_execution_requests(
            project_model["context"],
            annotated,
            runner_plan,
            removed_request_store,
        )
        revoked_final_store = revoke_run_final_confirmation(temporary_trace_dir, profile["id"])
        revoked_execution_gate = build_project_run_execution_gate(
            project_model["context"],
            annotated,
            confirmed_preflight,
            revoked_final_store,
        )
        revoked_store = revoke_run_confirmation(temporary_trace_dir, profile["id"])
        revoked_preflight = build_project_run_preflight(project_model["context"], annotated, revoked_store)
        removed_store = remove_run_profile(temporary_trace_dir, profile["id"])
        removed = annotate_run_profiles(run_profiles, removed_store)
        removed_preflight = build_project_run_preflight(project_model["context"], removed)
        if annotated["summary"]["saved_count"] != 1:
            failures.append("run_profile_store: expected saved_count=1 after save")
        if not saved_profile.get("saved"):
            failures.append("run_profile_store: expected profile saved flag")
        if removed["summary"]["saved_count"] != 0:
            failures.append("run_profile_store: expected saved_count=0 after remove")
        if preflight["summary"]["report_count"] != 1:
            failures.append("run_preflight: expected one report after save")
        if preflight["safety"]["executes_commands"]:
            failures.append("run_preflight: expected no command execution")
        if removed_preflight["status"] != "no_saved_profiles":
            failures.append("run_preflight: expected no_saved_profiles after remove")
        if not confirmed_preflight["reports"][0]["confirmation"]["confirmed"]:
            failures.append("run_confirmation: expected confirmed report")
        if confirmed_preflight["safety"]["executes_commands"]:
            failures.append("run_confirmation: expected no command execution")
        if revoked_preflight["reports"][0]["confirmation"]["status"] != "none":
            failures.append("run_confirmation: expected none after revoke")
        if execution_gate["status"] not in {"ready_for_final_confirmation", "final_confirmed"}:
            failures.append("run_execution_gate: expected ready after preflight confirmation")
        if execution_gate["safety"]["executes_commands"]:
            failures.append("run_execution_gate: expected no command execution")
        if confirmed_execution_gate["reports"][0]["final_confirmation"]["status"] != "confirmed":
            failures.append("run_final_confirmation: expected confirmed final gate")
        if confirmed_execution_gate["safety"]["executes_commands"]:
            failures.append("run_final_confirmation: expected no command execution")
        if revoked_execution_gate["reports"][0]["final_confirmation"]["status"] != "none":
            failures.append("run_final_confirmation: expected none after revoke")
        if runner_plan["status"] != "ready_for_runner_implementation":
            failures.append("runner_plan: expected ready after final confirmation")
        if runner_plan["safety"]["executes_commands"]:
            failures.append("runner_plan: expected no command execution")
        if runner_plan["safety"]["runner_implemented"]:
            failures.append("runner_plan: expected runner_implemented=false")
        if not runner_plan["reports"][0]["log_plan"]["event_log"].endswith("runner_events.jsonl"):
            failures.append("runner_plan: expected runner event log plan")
        if empty_execution_requests["reports"][0]["request"]["status"] != "none":
            failures.append("execution_request: expected none before prepare")
        if prepared_execution_requests["reports"][0]["request"]["status"] != "prepared":
            failures.append("execution_request: expected prepared after prepare")
        if second_confirmed_execution_requests["reports"][0]["request"]["status"] != "second_confirmed":
            failures.append("execution_request: expected second_confirmed after confirm")
        if second_confirmed_execution_requests["safety"]["executes_commands"]:
            failures.append("execution_request: expected no command execution")
        if revoked_execution_requests["reports"][0]["request"]["status"] != "prepared":
            failures.append("execution_request: expected prepared after revoke")
        if removed_execution_requests["reports"][0]["request"]["status"] != "none":
            failures.append("execution_request: expected none after remove")
        if empty_runner_sessions["reports"][0]["session"]["status"] != "none":
            failures.append("runner_session: expected none before prepare")
        if drafted_runner_sessions["reports"][0]["session"]["status"] != "drafted":
            failures.append("runner_session: expected drafted after prepare")
        if stale_runner_sessions["reports"][0]["session"]["status"] != "stale":
            failures.append("runner_session: expected stale after execution request revoke")
        if not stale_runner_sessions["reports"][0]["can_remove"]:
            failures.append("runner_session: expected stale session can be removed")
        if drafted_runner_sessions["safety"]["executes_commands"]:
            failures.append("runner_session: expected no command execution")
        if drafted_runner_sessions["safety"]["creates_process"]:
            failures.append("runner_session: expected no process creation")
        if not drafted_runner_sessions["event_schema"]["schema_version"].endswith(".v1"):
            failures.append("runner_session: expected runner event schema")
        if removed_runner_sessions["reports"][0]["session"]["status"] != "none":
            failures.append("runner_session: expected none after remove")
        if empty_launch_snapshots["reports"][0]["snapshot"]["status"] != "none":
            failures.append("runner_launch_snapshot: expected none before prepare")
        if snapshotted_launch_snapshots["reports"][0]["snapshot"]["status"] != "snapshotted":
            failures.append("runner_launch_snapshot: expected snapshotted after prepare")
        if snapshotted_launch_snapshots["safety"]["executes_commands"]:
            failures.append("runner_launch_snapshot: expected no command execution")
        if snapshotted_launch_snapshots["safety"]["creates_process"]:
            failures.append("runner_launch_snapshot: expected no process creation")
        if snapshotted_launch_snapshots["safety"]["launch_enabled"]:
            failures.append("runner_launch_snapshot: expected launch disabled")
        if stale_launch_snapshots["reports"][0]["snapshot"]["status"] != "stale":
            failures.append("runner_launch_snapshot: expected stale after runner session remove")
        if not stale_launch_snapshots["reports"][0]["can_remove"]:
            failures.append("runner_launch_snapshot: expected stale snapshot can be removed")
        if removed_launch_snapshots["reports"][0]["snapshot"]["status"] != "none":
            failures.append("runner_launch_snapshot: expected none after remove")
        if empty_dry_runs["reports"][0]["dry_run"]["status"] != "none":
            failures.append("runner_dry_run: expected none before prepare")
        if prepared_dry_runs["reports"][0]["dry_run"]["status"] != "prepared":
            failures.append("runner_dry_run: expected prepared after prepare")
        if prepared_dry_runs["safety"]["executes_commands"]:
            failures.append("runner_dry_run: expected no command execution")
        if prepared_dry_runs["safety"]["creates_process"]:
            failures.append("runner_dry_run: expected no process creation")
        if prepared_dry_runs["safety"]["launch_enabled"]:
            failures.append("runner_dry_run: expected launch disabled")
        if not prepared_dry_runs["reports"][0]["preview"]["planned_logs"]:
            failures.append("runner_dry_run: expected planned logs")
        if stale_dry_runs["reports"][0]["dry_run"]["status"] != "stale":
            failures.append("runner_dry_run: expected stale after launch snapshot remove")
        if not stale_dry_runs["reports"][0]["can_remove"]:
            failures.append("runner_dry_run: expected stale dry-run can be removed")
        if removed_dry_runs["reports"][0]["dry_run"]["status"] != "none":
            failures.append("runner_dry_run: expected none after remove")
        if launch_controls["status"] != "disabled_by_policy":
            failures.append("runner_launch_control: expected disabled_by_policy after dry-run")
        if launch_controls["summary"]["launchable_count"] != 0:
            failures.append("runner_launch_control: expected launchable_count=0")
        if launch_controls["safety"]["launch_enabled"]:
            failures.append("runner_launch_control: expected launch disabled")
        if launch_controls["safety"]["launch_api_available"]:
            failures.append("runner_launch_control: expected launch API unavailable")
        if runtime_policies["status"] != "ready_but_launch_disabled":
            failures.append("runner_runtime_policy: expected ready_but_launch_disabled after launch control")
        if runtime_policies["summary"]["launchable_count"] != 0:
            failures.append("runner_runtime_policy: expected launchable_count=0")
        if runtime_policies["safety"]["executes_commands"]:
            failures.append("runner_runtime_policy: expected no command execution")
        if runtime_policies["safety"]["creates_process"]:
            failures.append("runner_runtime_policy: expected no process creation")
        if not runtime_policies["reports"][0]["output_policy"]["rules"]:
            failures.append("runner_runtime_policy: expected output policy rules")
        if not runtime_policies["reports"][0]["cancellation_policy"]["rules"]:
            failures.append("runner_runtime_policy: expected cancellation policy rules")
        if not runtime_policies["reports"][0]["completion_policy"]["rules"]:
            failures.append("runner_runtime_policy: expected completion policy rules")
        if execution_configs["status"] != "configuration_required":
            failures.append("runner_execution_config: expected configuration_required after runtime policy")
        if execution_configs["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_config: expected launchable_count=0")
        if execution_configs["safety"]["executes_commands"]:
            failures.append("runner_execution_config: expected no command execution")
        if execution_configs["safety"]["creates_process"]:
            failures.append("runner_execution_config: expected no process creation")
        if execution_configs["safety"]["launch_enabled"]:
            failures.append("runner_execution_config: expected launch disabled")
        if execution_configs["safety"]["launch_api_available"]:
            failures.append("runner_execution_config: expected launch API unavailable")
        if not execution_configs["reports"][0]["required_config"]["real_execution"]["typed_consent"]:
            failures.append("runner_execution_config: expected typed consent requirement")
        if not execution_configs["reports"][0]["required_config"]["process_isolation"]["argv_must_be_tokenized"]:
            failures.append("runner_execution_config: expected argv tokenization requirement")
        if missing_config_checks["status"] != "config_missing":
            failures.append("runner_execution_config_check: expected config_missing without config file")
        if missing_config_checks["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_config_check: expected launchable_count=0 when config missing")
        if missing_config_checks["safety"]["creates_config_file"]:
            failures.append("runner_execution_config_check: expected no config file creation")
        if invalid_json_config_checks["status"] != "blocked":
            failures.append("runner_execution_config_check: expected blocked for invalid json config")
        if invalid_json_config_checks["config_file"]["status"] != "invalid_json":
            failures.append("runner_execution_config_check: expected invalid_json config status")
        if invalid_json_config_checks["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_config_check: expected launchable_count=0 for invalid json")
        if invalid_json_config_checks["safety"]["executes_commands"]:
            failures.append("runner_execution_config_check: expected no command execution for invalid json")
        if bad_config_checks["status"] != "blocked":
            failures.append("runner_execution_config_check: expected blocked for bad config")
        if bad_config_checks["config_file"]["status"] != "present":
            failures.append("runner_execution_config_check: expected present config status for bad config")
        if bad_config_checks["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_config_check: expected launchable_count=0 for bad config")
        if bad_config_checks["safety"]["creates_process"]:
            failures.append("runner_execution_config_check: expected no process creation for bad config")
        if present_config_checks["status"] != "config_present_but_launch_disabled":
            failures.append("runner_execution_config_check: expected config_present_but_launch_disabled with valid config")
        if present_config_checks["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_config_check: expected launchable_count=0 with valid config")
        if present_config_checks["safety"]["executes_commands"]:
            failures.append("runner_execution_config_check: expected no command execution")
        if present_config_checks["safety"]["creates_process"]:
            failures.append("runner_execution_config_check: expected no process creation")
        if present_config_checks["safety"]["launch_enabled"]:
            failures.append("runner_execution_config_check: expected launch disabled")
        if present_config_checks["safety"]["launch_api_available"]:
            failures.append("runner_execution_config_check: expected launch API unavailable")
        if config_schema_stabilizations["status"] != "schema_stabilization_required":
            failures.append("runner_config_schema_stabilization: expected schema_stabilization_required")
        if config_schema_stabilizations["summary"]["launchable_count"] != 0:
            failures.append("runner_config_schema_stabilization: expected launchable_count=0")
        if config_schema_stabilizations["summary"]["field_contract_count"] < 10:
            failures.append("runner_config_schema_stabilization: expected field contracts")
        if config_schema_stabilizations["summary"]["compatibility_rule_count"] < 6:
            failures.append("runner_config_schema_stabilization: expected compatibility rules")
        if config_schema_stabilizations["summary"]["error_code_count"] < 8:
            failures.append("runner_config_schema_stabilization: expected error map")
        if config_schema_stabilizations["config_schema_stabilization_schema"]["config_file_schema_version"] != "flowtrace_runner_config.v1":
            failures.append("runner_config_schema_stabilization: expected stable config schema version")
        if config_schema_stabilizations["safety"]["executes_commands"]:
            failures.append("runner_config_schema_stabilization: expected no command execution")
        if config_schema_stabilizations["safety"]["creates_process"]:
            failures.append("runner_config_schema_stabilization: expected no process creation")
        if config_schema_stabilizations["safety"]["reads_config_file"]:
            failures.append("runner_config_schema_stabilization: expected no direct config read")
        if config_schema_stabilizations["safety"]["writes_config_file"]:
            failures.append("runner_config_schema_stabilization: expected no config writes")
        if config_schema_stabilizations["safety"]["launch_enabled"]:
            failures.append("runner_config_schema_stabilization: expected launch disabled")
        if config_schema_stabilizations["safety"]["launch_api_available"]:
            failures.append("runner_config_schema_stabilization: expected launch API unavailable")
        if config_field_contract_views["status"] != "contract_view_ready":
            failures.append("runner_config_field_contract_view: expected contract_view_ready")
        if config_field_contract_views["summary"]["launchable_count"] != 0:
            failures.append("runner_config_field_contract_view: expected launchable_count=0")
        if config_field_contract_views["summary"]["field_contract_count"] < 10:
            failures.append("runner_config_field_contract_view: expected field contract descriptions")
        if config_field_contract_views["summary"]["default_value_count"] < 10:
            failures.append("runner_config_field_contract_view: expected default values")
        if config_field_contract_views["summary"]["error_code_count"] < 8:
            failures.append("runner_config_field_contract_view: expected error code descriptions")
        if config_field_contract_views["field_contract_view_schema"]["stable_config_schema_version"] != "flowtrace_runner_config.v1":
            failures.append("runner_config_field_contract_view: expected stable config schema version")
        if config_field_contract_views["safety"]["executes_commands"]:
            failures.append("runner_config_field_contract_view: expected no command execution")
        if config_field_contract_views["safety"]["creates_process"]:
            failures.append("runner_config_field_contract_view: expected no process creation")
        if config_field_contract_views["safety"]["reads_config_file"]:
            failures.append("runner_config_field_contract_view: expected no config reads")
        if config_field_contract_views["safety"]["writes_config_file"]:
            failures.append("runner_config_field_contract_view: expected no config writes")
        if config_field_contract_views["safety"]["launch_enabled"]:
            failures.append("runner_config_field_contract_view: expected launch disabled")
        if config_field_contract_views["safety"]["launch_api_available"]:
            failures.append("runner_config_field_contract_view: expected launch API unavailable")
        if config_compatibility_reports["status"] != "compatibility_report_required":
            failures.append("runner_config_compatibility_report: expected compatibility_report_required")
        if config_compatibility_reports["summary"]["launchable_count"] != 0:
            failures.append("runner_config_compatibility_report: expected launchable_count=0")
        if config_compatibility_reports["summary"]["compatibility_issue_count"] < 1:
            failures.append("runner_config_compatibility_report: expected compatibility issues")
        if config_compatibility_reports["summary"]["missing_field_count"] < 1:
            failures.append("runner_config_compatibility_report: expected missing field issues")
        if (
            config_compatibility_reports["summary"].get("issue_navigation_target_count", 0)
            < config_compatibility_reports["summary"]["compatibility_issue_count"]
        ):
            failures.append("runner_config_compatibility_report: expected issue navigation targets")
        if not any(report.get("index_entries") for report in config_compatibility_reports.get("reports", [])):
            failures.append("runner_config_compatibility_report: expected report index entries")
        if config_compatibility_reports["compatibility_report_schema"]["stable_config_schema_version"] != "flowtrace_runner_config.v1":
            failures.append("runner_config_compatibility_report: expected stable config schema version")
        if config_compatibility_reports["safety"]["executes_commands"]:
            failures.append("runner_config_compatibility_report: expected no command execution")
        if config_compatibility_reports["safety"]["creates_process"]:
            failures.append("runner_config_compatibility_report: expected no process creation")
        if config_compatibility_reports["safety"]["reads_config_file"]:
            failures.append("runner_config_compatibility_report: expected no direct config read")
        if not config_compatibility_reports["safety"]["uses_in_memory_config_payload"]:
            failures.append("runner_config_compatibility_report: expected in-memory config payload")
        if config_compatibility_reports["safety"]["writes_config_file"]:
            failures.append("runner_config_compatibility_report: expected no config writes")
        if config_compatibility_reports["safety"]["launch_enabled"]:
            failures.append("runner_config_compatibility_report: expected launch disabled")
        if config_compatibility_reports["safety"]["launch_api_available"]:
            failures.append("runner_config_compatibility_report: expected launch API unavailable")
        if bad_config_compatibility_reports["status"] != "blocked":
            failures.append("runner_config_compatibility_report: expected blocked for bad config")
        if bad_config_compatibility_reports["summary"]["compatibility_issue_count"] < 1:
            failures.append("runner_config_compatibility_report: expected bad config compatibility issues")
        if bad_config_compatibility_reports["summary"]["launchable_count"] != 0:
            failures.append("runner_config_compatibility_report: expected launchable_count=0 for bad config")
        if bad_config_compatibility_reports["safety"]["executes_commands"]:
            failures.append("runner_config_compatibility_report: expected no command execution for bad config")
        if bad_config_compatibility_reports["safety"]["writes_config_file"]:
            failures.append("runner_config_compatibility_report: expected no config writes for bad config")
        if config_remediation_summaries["status"] != "remediation_required":
            failures.append("runner_config_remediation_summary: expected remediation_required")
        if config_remediation_summaries["summary"]["recommendation_count"] < 1:
            failures.append("runner_config_remediation_summary: expected recommendations")
        if not all(
            item.get("navigation", {}).get("item_key")
            for report in config_remediation_summaries.get("reports", [])
            for item in report.get("recommendations", [])
        ):
            failures.append("runner_config_remediation_summary: expected recommendation navigation")
        if config_remediation_summaries["summary"]["launchable_count"] != 0:
            failures.append("runner_config_remediation_summary: expected launchable_count=0")
        if config_remediation_summaries["safety"]["executes_commands"]:
            failures.append("runner_config_remediation_summary: expected no command execution")
        if config_remediation_summaries["safety"]["creates_process"]:
            failures.append("runner_config_remediation_summary: expected no process creation")
        if config_remediation_summaries["safety"]["reads_config_file"]:
            failures.append("runner_config_remediation_summary: expected no config reads")
        if config_remediation_summaries["safety"]["writes_config_file"]:
            failures.append("runner_config_remediation_summary: expected no config writes")
        if not config_remediation_summaries["safety"]["consumes_compatibility_report"]:
            failures.append("runner_config_remediation_summary: expected compatibility report consumption")
        if config_field_coverage_indexes["status"] != "coverage_index_ready":
            failures.append("runner_config_field_coverage_index: expected coverage_index_ready")
        if config_field_coverage_indexes["summary"]["launchable_count"] != 0:
            failures.append("runner_config_field_coverage_index: expected launchable_count=0")
        if config_field_coverage_indexes["summary"]["field_count"] < 10:
            failures.append("runner_config_field_coverage_index: expected indexed fields")
        if config_field_coverage_indexes["summary"]["indexed_issue_count"] < 1:
            failures.append("runner_config_field_coverage_index: expected indexed compatibility issues")
        if config_field_coverage_indexes["summary"]["indexed_recommendation_count"] < 1:
            failures.append("runner_config_field_coverage_index: expected indexed recommendations")
        if config_field_coverage_indexes["summary"]["target_group_count"] != 4:
            failures.append("runner_config_field_coverage_index: expected four target groups")
        if config_field_coverage_indexes["summary"]["filter_group_count"] < 4:
            failures.append("runner_config_field_coverage_index: expected field filter groups")
        if not all(item.get("filter_tags") for item in config_field_coverage_indexes.get("field_indexes", [])):
            failures.append("runner_config_field_coverage_index: expected field filter tags")
        target_group_keys = {item.get("key") for item in config_field_coverage_indexes.get("target_groups", [])}
        if target_group_keys != {
            "config_field_coverage",
            "config_field_contract",
            "config_field_issue",
            "config_field_remediation",
        }:
            failures.append("runner_config_field_coverage_index: expected stable target group keys")
        coverage_index_kinds = {
            item.get("kind")
            for report in config_field_coverage_indexes.get("reports", [])
            for item in report.get("index_entries", [])
            if isinstance(item, dict)
        }
        if "config_field_coverage" not in coverage_index_kinds:
            failures.append("runner_config_field_coverage_index: expected coverage navigation entries")
        if "config_field_contract" not in coverage_index_kinds:
            failures.append("runner_config_field_coverage_index: expected contract navigation entries")
        if "config_field_issue" not in coverage_index_kinds:
            failures.append("runner_config_field_coverage_index: expected issue navigation entries")
        if "config_field_remediation" not in coverage_index_kinds:
            failures.append("runner_config_field_coverage_index: expected remediation navigation entries")
        if config_field_coverage_indexes["safety"]["executes_commands"]:
            failures.append("runner_config_field_coverage_index: expected no command execution")
        if config_field_coverage_indexes["safety"]["creates_process"]:
            failures.append("runner_config_field_coverage_index: expected no process creation")
        if config_field_coverage_indexes["safety"]["reads_config_file"]:
            failures.append("runner_config_field_coverage_index: expected no config reads")
        if config_field_coverage_indexes["safety"]["writes_config_file"]:
            failures.append("runner_config_field_coverage_index: expected no config writes")
        if not config_field_coverage_indexes["safety"]["uses_in_memory_config_payload"]:
            failures.append("runner_config_field_coverage_index: expected in-memory payload consumption")
        if service_flag_audits["status"] != "service_flags_required":
            failures.append("runner_service_flag_audit: expected service_flags_required with valid config check")
        if service_flag_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_service_flag_audit: expected launchable_count=0")
        if service_flag_audits["safety"]["executes_commands"]:
            failures.append("runner_service_flag_audit: expected no command execution")
        if service_flag_audits["safety"]["creates_process"]:
            failures.append("runner_service_flag_audit: expected no process creation")
        if service_flag_audits["safety"]["launch_enabled"]:
            failures.append("runner_service_flag_audit: expected launch disabled")
        if service_flag_audits["safety"]["launch_api_available"]:
            failures.append("runner_service_flag_audit: expected launch API unavailable")
        if service_flag_audits["safety"]["reads_environment"]:
            failures.append("runner_service_flag_audit: expected no environment reads")
        if service_flag_audits["safety"]["parses_process_args"]:
            failures.append("runner_service_flag_audit: expected no process arg parsing")
        if log_directory_policies["status"] != "log_directory_policy_required":
            failures.append("runner_log_directory_policy: expected log_directory_policy_required after service audit")
        if log_directory_policies["summary"]["launchable_count"] != 0:
            failures.append("runner_log_directory_policy: expected launchable_count=0")
        if log_directory_policies["safety"]["executes_commands"]:
            failures.append("runner_log_directory_policy: expected no command execution")
        if log_directory_policies["safety"]["creates_process"]:
            failures.append("runner_log_directory_policy: expected no process creation")
        if log_directory_policies["safety"]["launch_enabled"]:
            failures.append("runner_log_directory_policy: expected launch disabled")
        if log_directory_policies["safety"]["launch_api_available"]:
            failures.append("runner_log_directory_policy: expected launch API unavailable")
        if log_directory_policies["safety"]["creates_log_directory"]:
            failures.append("runner_log_directory_policy: expected no log directory creation")
        if log_directory_policies["safety"]["opens_log_files"]:
            failures.append("runner_log_directory_policy: expected no log file open")
        if log_directory_policies["safety"]["writes_logs"]:
            failures.append("runner_log_directory_policy: expected no log writes")
        if not log_directory_policies["reports"][0]["candidate_directories"]:
            failures.append("runner_log_directory_policy: expected candidate directories")
        if log_retention_policies["status"] != "log_retention_policy_required":
            failures.append("runner_log_retention_policy: expected log_retention_policy_required after directory policy")
        if log_retention_policies["summary"]["launchable_count"] != 0:
            failures.append("runner_log_retention_policy: expected launchable_count=0")
        if log_retention_policies["safety"]["executes_commands"]:
            failures.append("runner_log_retention_policy: expected no command execution")
        if log_retention_policies["safety"]["creates_process"]:
            failures.append("runner_log_retention_policy: expected no process creation")
        if log_retention_policies["safety"]["launch_enabled"]:
            failures.append("runner_log_retention_policy: expected launch disabled")
        if log_retention_policies["safety"]["launch_api_available"]:
            failures.append("runner_log_retention_policy: expected launch API unavailable")
        if log_retention_policies["safety"]["scans_log_directory"]:
            failures.append("runner_log_retention_policy: expected no log directory scanning")
        if log_retention_policies["safety"]["deletes_logs"]:
            failures.append("runner_log_retention_policy: expected no log deletion")
        if log_retention_policies["safety"]["rotates_logs"]:
            failures.append("runner_log_retention_policy: expected no log rotation")
        if log_retention_policies["safety"]["renames_logs"]:
            failures.append("runner_log_retention_policy: expected no log rename")
        if log_retention_policies["safety"]["truncates_logs"]:
            failures.append("runner_log_retention_policy: expected no log truncation")
        if log_retention_policies["safety"]["writes_logs"]:
            failures.append("runner_log_retention_policy: expected no log writes")
        if not log_retention_policies["reports"][0]["cleanup_rules"]:
            failures.append("runner_log_retention_policy: expected cleanup rules")
        if log_cleanup_previews["status"] != "cleanup_preview_required":
            failures.append("runner_log_cleanup_preview: expected cleanup_preview_required after retention policy")
        if log_cleanup_previews["summary"]["launchable_count"] != 0:
            failures.append("runner_log_cleanup_preview: expected launchable_count=0")
        if log_cleanup_previews["summary"]["previewed_deletion_count"] != 0:
            failures.append("runner_log_cleanup_preview: expected previewed_deletion_count=0 without fs scan")
        if log_cleanup_previews["safety"]["executes_commands"]:
            failures.append("runner_log_cleanup_preview: expected no command execution")
        if log_cleanup_previews["safety"]["creates_process"]:
            failures.append("runner_log_cleanup_preview: expected no process creation")
        if log_cleanup_previews["safety"]["launch_enabled"]:
            failures.append("runner_log_cleanup_preview: expected launch disabled")
        if log_cleanup_previews["safety"]["launch_api_available"]:
            failures.append("runner_log_cleanup_preview: expected launch API unavailable")
        if log_cleanup_previews["safety"]["scans_log_directory"]:
            failures.append("runner_log_cleanup_preview: expected no log directory scanning")
        if log_cleanup_previews["safety"]["reads_log_files"]:
            failures.append("runner_log_cleanup_preview: expected no log file reads")
        if log_cleanup_previews["safety"]["deletes_logs"]:
            failures.append("runner_log_cleanup_preview: expected no log deletion")
        if log_cleanup_previews["safety"]["rotates_logs"]:
            failures.append("runner_log_cleanup_preview: expected no log rotation")
        if log_cleanup_previews["safety"]["renames_logs"]:
            failures.append("runner_log_cleanup_preview: expected no log rename")
        if log_cleanup_previews["safety"]["truncates_logs"]:
            failures.append("runner_log_cleanup_preview: expected no log truncation")
        if log_cleanup_previews["safety"]["writes_logs"]:
            failures.append("runner_log_cleanup_preview: expected no log writes")
        if not log_cleanup_previews["reports"][0]["risk_warnings"]:
            failures.append("runner_log_cleanup_preview: expected risk warnings")
        if log_cleanup_confirmations["status"] != "cleanup_confirmation_required":
            failures.append("runner_log_cleanup_confirmation: expected cleanup_confirmation_required after preview")
        if log_cleanup_confirmations["summary"]["launchable_count"] != 0:
            failures.append("runner_log_cleanup_confirmation: expected launchable_count=0")
        if log_cleanup_confirmations["summary"]["confirmed_cleanup_count"] != 0:
            failures.append("runner_log_cleanup_confirmation: expected confirmed_cleanup_count=0")
        if log_cleanup_confirmations["safety"]["executes_commands"]:
            failures.append("runner_log_cleanup_confirmation: expected no command execution")
        if log_cleanup_confirmations["safety"]["creates_process"]:
            failures.append("runner_log_cleanup_confirmation: expected no process creation")
        if log_cleanup_confirmations["safety"]["launch_enabled"]:
            failures.append("runner_log_cleanup_confirmation: expected launch disabled")
        if log_cleanup_confirmations["safety"]["launch_api_available"]:
            failures.append("runner_log_cleanup_confirmation: expected launch API unavailable")
        if log_cleanup_confirmations["safety"]["stores_confirmation"]:
            failures.append("runner_log_cleanup_confirmation: expected no confirmation storage")
        if log_cleanup_confirmations["safety"]["scans_log_directory"]:
            failures.append("runner_log_cleanup_confirmation: expected no log directory scanning")
        if log_cleanup_confirmations["safety"]["reads_log_files"]:
            failures.append("runner_log_cleanup_confirmation: expected no log reads")
        if log_cleanup_confirmations["safety"]["deletes_logs"]:
            failures.append("runner_log_cleanup_confirmation: expected no log deletion")
        if log_cleanup_confirmations["safety"]["rotates_logs"]:
            failures.append("runner_log_cleanup_confirmation: expected no log rotation")
        if log_cleanup_confirmations["safety"]["renames_logs"]:
            failures.append("runner_log_cleanup_confirmation: expected no log rename")
        if log_cleanup_confirmations["safety"]["truncates_logs"]:
            failures.append("runner_log_cleanup_confirmation: expected no log truncation")
        if log_cleanup_confirmations["safety"]["writes_logs"]:
            failures.append("runner_log_cleanup_confirmation: expected no log writes")
        if not log_cleanup_confirmations["reports"][0]["required_future_confirmation"]["typed_consent"]:
            failures.append("runner_log_cleanup_confirmation: expected typed consent")
        if log_cleanup_confirmations["reports"][0]["confirmation_state"]["status"] != "not_collected":
            failures.append("runner_log_cleanup_confirmation: expected not_collected state")
        if log_cleanup_audit_trails["status"] != "cleanup_audit_trail_required":
            failures.append("runner_log_cleanup_audit_trail: expected cleanup_audit_trail_required after confirmation")
        if log_cleanup_audit_trails["summary"]["launchable_count"] != 0:
            failures.append("runner_log_cleanup_audit_trail: expected launchable_count=0")
        if log_cleanup_audit_trails["summary"]["stored_audit_event_count"] != 0:
            failures.append("runner_log_cleanup_audit_trail: expected stored_audit_event_count=0")
        if log_cleanup_audit_trails["safety"]["executes_commands"]:
            failures.append("runner_log_cleanup_audit_trail: expected no command execution")
        if log_cleanup_audit_trails["safety"]["creates_process"]:
            failures.append("runner_log_cleanup_audit_trail: expected no process creation")
        if log_cleanup_audit_trails["safety"]["launch_enabled"]:
            failures.append("runner_log_cleanup_audit_trail: expected launch disabled")
        if log_cleanup_audit_trails["safety"]["launch_api_available"]:
            failures.append("runner_log_cleanup_audit_trail: expected launch API unavailable")
        if log_cleanup_audit_trails["safety"]["stores_audit_events"]:
            failures.append("runner_log_cleanup_audit_trail: expected no audit event storage")
        if log_cleanup_audit_trails["safety"]["writes_audit_log"]:
            failures.append("runner_log_cleanup_audit_trail: expected no audit log writes")
        if log_cleanup_audit_trails["safety"]["reads_audit_log"]:
            failures.append("runner_log_cleanup_audit_trail: expected no audit log reads")
        if log_cleanup_audit_trails["safety"]["scans_log_directory"]:
            failures.append("runner_log_cleanup_audit_trail: expected no log directory scanning")
        if log_cleanup_audit_trails["safety"]["reads_log_files"]:
            failures.append("runner_log_cleanup_audit_trail: expected no log reads")
        if log_cleanup_audit_trails["safety"]["deletes_logs"]:
            failures.append("runner_log_cleanup_audit_trail: expected no log deletion")
        if log_cleanup_audit_trails["safety"]["rotates_logs"]:
            failures.append("runner_log_cleanup_audit_trail: expected no log rotation")
        if log_cleanup_audit_trails["safety"]["renames_logs"]:
            failures.append("runner_log_cleanup_audit_trail: expected no log rename")
        if log_cleanup_audit_trails["safety"]["truncates_logs"]:
            failures.append("runner_log_cleanup_audit_trail: expected no log truncation")
        if log_cleanup_audit_trails["safety"]["writes_logs"]:
            failures.append("runner_log_cleanup_audit_trail: expected no log writes")
        if not log_cleanup_audit_trails["reports"][0]["required_future_events"]:
            failures.append("runner_log_cleanup_audit_trail: expected required future events")
        if log_cleanup_audit_trails["reports"][0]["audit_state"]["status"] != "not_recorded":
            failures.append("runner_log_cleanup_audit_trail: expected not_recorded state")
        if log_cleanup_execution_plans["status"] != "cleanup_execution_plan_required":
            failures.append("runner_log_cleanup_execution_plan: expected cleanup_execution_plan_required after audit trail")
        if log_cleanup_execution_plans["summary"]["launchable_count"] != 0:
            failures.append("runner_log_cleanup_execution_plan: expected launchable_count=0")
        if log_cleanup_execution_plans["summary"]["planned_operation_count"] != 0:
            failures.append("runner_log_cleanup_execution_plan: expected planned_operation_count=0")
        if log_cleanup_execution_plans["summary"]["stored_plan_count"] != 0:
            failures.append("runner_log_cleanup_execution_plan: expected stored_plan_count=0")
        if log_cleanup_execution_plans["safety"]["executes_commands"]:
            failures.append("runner_log_cleanup_execution_plan: expected no command execution")
        if log_cleanup_execution_plans["safety"]["creates_process"]:
            failures.append("runner_log_cleanup_execution_plan: expected no process creation")
        if log_cleanup_execution_plans["safety"]["launch_enabled"]:
            failures.append("runner_log_cleanup_execution_plan: expected launch disabled")
        if log_cleanup_execution_plans["safety"]["launch_api_available"]:
            failures.append("runner_log_cleanup_execution_plan: expected launch API unavailable")
        if log_cleanup_execution_plans["safety"]["stores_execution_plan"]:
            failures.append("runner_log_cleanup_execution_plan: expected no plan storage")
        if log_cleanup_execution_plans["safety"]["executes_cleanup"]:
            failures.append("runner_log_cleanup_execution_plan: expected no cleanup execution")
        if log_cleanup_execution_plans["safety"]["generates_candidate_manifest"]:
            failures.append("runner_log_cleanup_execution_plan: expected no candidate manifest generation")
        if log_cleanup_execution_plans["safety"]["stores_candidate_manifest"]:
            failures.append("runner_log_cleanup_execution_plan: expected no candidate manifest storage")
        if log_cleanup_execution_plans["safety"]["reads_candidate_manifest"]:
            failures.append("runner_log_cleanup_execution_plan: expected no candidate manifest reads")
        if log_cleanup_execution_plans["safety"]["writes_audit_log"]:
            failures.append("runner_log_cleanup_execution_plan: expected no audit log writes")
        if log_cleanup_execution_plans["safety"]["reads_audit_log"]:
            failures.append("runner_log_cleanup_execution_plan: expected no audit log reads")
        if log_cleanup_execution_plans["safety"]["scans_log_directory"]:
            failures.append("runner_log_cleanup_execution_plan: expected no log directory scanning")
        if log_cleanup_execution_plans["safety"]["reads_log_files"]:
            failures.append("runner_log_cleanup_execution_plan: expected no log reads")
        if log_cleanup_execution_plans["safety"]["deletes_logs"]:
            failures.append("runner_log_cleanup_execution_plan: expected no log deletion")
        if log_cleanup_execution_plans["safety"]["rotates_logs"]:
            failures.append("runner_log_cleanup_execution_plan: expected no log rotation")
        if log_cleanup_execution_plans["safety"]["renames_logs"]:
            failures.append("runner_log_cleanup_execution_plan: expected no log rename")
        if log_cleanup_execution_plans["safety"]["truncates_logs"]:
            failures.append("runner_log_cleanup_execution_plan: expected no log truncation")
        if log_cleanup_execution_plans["safety"]["writes_logs"]:
            failures.append("runner_log_cleanup_execution_plan: expected no log writes")
        if log_cleanup_execution_plans["reports"][0]["plan_state"]["status"] != "not_planned":
            failures.append("runner_log_cleanup_execution_plan: expected not_planned state")
        if log_cleanup_execution_plans["reports"][0]["planned_operations"]:
            failures.append("runner_log_cleanup_execution_plan: expected no planned operations")
        if governance_readiness["status"] != "governance_required":
            failures.append("runner_governance_readiness: expected governance_required")
        if governance_readiness["summary"]["launchable_count"] != 0:
            failures.append("runner_governance_readiness: expected launchable_count=0")
        if governance_readiness["summary"]["layer_count"] < 18:
            failures.append("runner_governance_readiness: expected governance layer summary")
        if governance_readiness["safety"]["executes_commands"]:
            failures.append("runner_governance_readiness: expected no command execution")
        if governance_readiness["safety"]["creates_process"]:
            failures.append("runner_governance_readiness: expected no process creation")
        if governance_readiness["safety"]["launch_enabled"]:
            failures.append("runner_governance_readiness: expected launch disabled")
        if governance_readiness["safety"]["launch_api_available"]:
            failures.append("runner_governance_readiness: expected launch API unavailable")
        if governance_readiness["safety"]["reads_log_files"]:
            failures.append("runner_governance_readiness: expected no log reads")
        if governance_readiness["safety"]["writes_logs"]:
            failures.append("runner_governance_readiness: expected no log writes")
        if governance_readiness["safety"]["deletes_logs"]:
            failures.append("runner_governance_readiness: expected no log deletion")
        if execution_adapter_contracts["status"] != "adapter_contract_required":
            failures.append("runner_execution_adapter_contract: expected adapter_contract_required")
        if execution_adapter_contracts["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_adapter_contract: expected launchable_count=0")
        if execution_adapter_contracts["safety"]["executes_commands"]:
            failures.append("runner_execution_adapter_contract: expected no command execution")
        if execution_adapter_contracts["safety"]["creates_process"]:
            failures.append("runner_execution_adapter_contract: expected no process creation")
        if execution_adapter_contracts["safety"]["launch_enabled"]:
            failures.append("runner_execution_adapter_contract: expected launch disabled")
        if execution_adapter_contracts["safety"]["launch_api_available"]:
            failures.append("runner_execution_adapter_contract: expected launch API unavailable")
        if execution_adapter_contracts["safety"]["writes_logs"]:
            failures.append("runner_execution_adapter_contract: expected no log writes")
        if execution_adapter_contracts["safety"]["deletes_logs"]:
            failures.append("runner_execution_adapter_contract: expected no log deletion")
        if not execution_adapter_contracts["safety"]["execution_adapter_contract_only"]:
            failures.append("runner_execution_adapter_contract: expected contract-only safety flag")
        adapter_contract = execution_adapter_contracts["reports"][0]["adapter_contract"]
        if not adapter_contract["interface"]:
            failures.append("runner_execution_adapter_contract: expected adapter interface")
        if not adapter_contract["hooks"]:
            failures.append("runner_execution_adapter_contract: expected lifecycle hooks")
        if adapter_contract["argv_contract"]["shell_string_allowed"]:
            failures.append("runner_execution_adapter_contract: expected shell strings to stay forbidden")
        if launch_api_contracts["status"] != "launch_api_contract_required":
            failures.append("runner_launch_api_contract: expected launch_api_contract_required")
        if launch_api_contracts["summary"]["launchable_count"] != 0:
            failures.append("runner_launch_api_contract: expected launchable_count=0")
        if launch_api_contracts["summary"]["registered_endpoint_count"] != 0:
            failures.append("runner_launch_api_contract: expected registered_endpoint_count=0")
        if launch_api_contracts["safety"]["executes_commands"]:
            failures.append("runner_launch_api_contract: expected no command execution")
        if launch_api_contracts["safety"]["creates_process"]:
            failures.append("runner_launch_api_contract: expected no process creation")
        if launch_api_contracts["safety"]["launch_enabled"]:
            failures.append("runner_launch_api_contract: expected launch disabled")
        if launch_api_contracts["safety"]["launch_api_available"]:
            failures.append("runner_launch_api_contract: expected launch API unavailable")
        if launch_api_contracts["safety"]["registers_post_api"]:
            failures.append("runner_launch_api_contract: expected no POST registration")
        if launch_api_contracts["safety"]["writes_logs"]:
            failures.append("runner_launch_api_contract: expected no log writes")
        if launch_api_contracts["safety"]["deletes_logs"]:
            failures.append("runner_launch_api_contract: expected no log deletion")
        if not launch_api_contracts["safety"]["launch_api_contract_only"]:
            failures.append("runner_launch_api_contract: expected contract-only safety flag")
        launch_contract = launch_api_contracts["reports"][0]["launch_api_contract"]
        if launch_contract["future_endpoint"]["registered_now"]:
            failures.append("runner_launch_api_contract: expected endpoint not registered")
        if "command_string" not in launch_contract["request_contract"]["forbidden_fields"]:
            failures.append("runner_launch_api_contract: expected command string forbidden")
        if "execution_adapter_contract_required" not in launch_contract["required_guards"]:
            failures.append("runner_launch_api_contract: expected adapter contract guard")
        if execution_adapter_reviews["status"] != "adapter_review_required":
            failures.append("runner_execution_adapter_review: expected adapter_review_required")
        if execution_adapter_reviews["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_adapter_review: expected launchable_count=0")
        if execution_adapter_reviews["summary"]["implemented_adapter_count"] != 0:
            failures.append("runner_execution_adapter_review: expected implemented_adapter_count=0")
        if execution_adapter_reviews["summary"]["violation_count"] != 0:
            failures.append("runner_execution_adapter_review: expected violation_count=0")
        if execution_adapter_reviews["safety"]["executes_commands"]:
            failures.append("runner_execution_adapter_review: expected no command execution")
        if execution_adapter_reviews["safety"]["creates_process"]:
            failures.append("runner_execution_adapter_review: expected no process creation")
        if execution_adapter_reviews["safety"]["launch_enabled"]:
            failures.append("runner_execution_adapter_review: expected launch disabled")
        if execution_adapter_reviews["safety"]["launch_api_available"]:
            failures.append("runner_execution_adapter_review: expected launch API unavailable")
        if execution_adapter_reviews["safety"]["scans_code"]:
            failures.append("runner_execution_adapter_review: expected no code scanning")
        if execution_adapter_reviews["safety"]["imports_adapter"]:
            failures.append("runner_execution_adapter_review: expected no adapter imports")
        if execution_adapter_reviews["safety"]["calls_execution_adapter"]:
            failures.append("runner_execution_adapter_review: expected no adapter calls")
        if execution_adapter_reviews["safety"]["registers_post_api"]:
            failures.append("runner_execution_adapter_review: expected no POST registration")
        if execution_adapter_reviews["safety"]["writes_logs"]:
            failures.append("runner_execution_adapter_review: expected no log writes")
        if execution_adapter_reviews["safety"]["deletes_logs"]:
            failures.append("runner_execution_adapter_review: expected no log deletion")
        if not execution_adapter_reviews["safety"]["adapter_review_only"]:
            failures.append("runner_execution_adapter_review: expected review-only safety flag")
        adapter_review = execution_adapter_reviews["reports"][0]["adapter_review"]
        if adapter_review["implementation_state"]["adapter_loaded_now"]:
            failures.append("runner_execution_adapter_review: expected adapter not loaded")
        if adapter_review["implementation_state"]["adapter_invoked_now"]:
            failures.append("runner_execution_adapter_review: expected adapter not invoked")
        if "adapter_must_reject_shell_strings" not in adapter_review["required_review_gates"]:
            failures.append("runner_execution_adapter_review: expected shell rejection review gate")
        if final_block_matrices["status"] != "final_block_required":
            failures.append("runner_final_block_matrix: expected final_block_required")
        if final_block_matrices["summary"]["launchable_count"] != 0:
            failures.append("runner_final_block_matrix: expected launchable_count=0")
        if final_block_matrices["summary"]["blocking_reason_count"] < 1:
            failures.append("runner_final_block_matrix: expected blocking reasons")
        if final_block_matrices["safety"]["executes_commands"]:
            failures.append("runner_final_block_matrix: expected no command execution")
        if final_block_matrices["safety"]["creates_process"]:
            failures.append("runner_final_block_matrix: expected no process creation")
        if final_block_matrices["safety"]["launch_enabled"]:
            failures.append("runner_final_block_matrix: expected launch disabled")
        if final_block_matrices["safety"]["launch_api_available"]:
            failures.append("runner_final_block_matrix: expected launch API unavailable")
        if final_block_matrices["safety"]["registers_post_api"]:
            failures.append("runner_final_block_matrix: expected no POST registration")
        if final_block_matrices["safety"]["imports_adapter"]:
            failures.append("runner_final_block_matrix: expected no adapter import")
        if final_block_matrices["safety"]["calls_execution_adapter"]:
            failures.append("runner_final_block_matrix: expected no adapter call")
        if final_block_matrices["safety"]["opens_stdout_stderr"]:
            failures.append("runner_final_block_matrix: expected no stdout/stderr opening")
        if final_block_matrices["safety"]["writes_runner_events"]:
            failures.append("runner_final_block_matrix: expected no runner event writes")
        if final_block_matrices["safety"]["writes_logs"]:
            failures.append("runner_final_block_matrix: expected no log writes")
        if final_block_matrices["safety"]["deletes_logs"]:
            failures.append("runner_final_block_matrix: expected no log deletion")
        if final_block_matrices["safety"]["writes_audit_log"]:
            failures.append("runner_final_block_matrix: expected no audit log writes")
        if final_block_matrices["safety"]["reads_audit_log"]:
            failures.append("runner_final_block_matrix: expected no audit log reads")
        if final_block_matrices["safety"]["writes_user_project"]:
            failures.append("runner_final_block_matrix: expected no user project writes")
        if not final_block_matrices["safety"]["final_block_matrix_only"]:
            failures.append("runner_final_block_matrix: expected matrix-only safety flag")
        final_matrix_report = final_block_matrices["reports"][0]
        if final_matrix_report["launch_state"]["launchable"]:
            failures.append("runner_final_block_matrix: expected non-launchable report")
        if not final_matrix_report["blocking_reasons"]:
            failures.append("runner_final_block_matrix: expected report blocking reasons")
        if "implemented execution adapter" not in " ".join(final_matrix_report["required_future_unlocks"]):
            failures.append("runner_final_block_matrix: expected implemented adapter future unlock")
        if authorization_unlock_audits["status"] != "authorization_unlock_required":
            failures.append("runner_authorization_unlock_audit: expected authorization_unlock_required")
        if authorization_unlock_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_authorization_unlock_audit: expected launchable_count=0")
        if authorization_unlock_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_authorization_unlock_audit: expected missing evidence")
        if authorization_unlock_audits["safety"]["executes_commands"]:
            failures.append("runner_authorization_unlock_audit: expected no command execution")
        if authorization_unlock_audits["safety"]["creates_process"]:
            failures.append("runner_authorization_unlock_audit: expected no process creation")
        if authorization_unlock_audits["safety"]["launch_enabled"]:
            failures.append("runner_authorization_unlock_audit: expected launch disabled")
        if authorization_unlock_audits["safety"]["launch_api_available"]:
            failures.append("runner_authorization_unlock_audit: expected launch API unavailable")
        if authorization_unlock_audits["safety"]["registers_post_api"]:
            failures.append("runner_authorization_unlock_audit: expected no POST registration")
        if authorization_unlock_audits["safety"]["imports_adapter"]:
            failures.append("runner_authorization_unlock_audit: expected no adapter import")
        if authorization_unlock_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_authorization_unlock_audit: expected no adapter call")
        if authorization_unlock_audits["safety"]["grants_permission"]:
            failures.append("runner_authorization_unlock_audit: expected no permission grant")
        if authorization_unlock_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_authorization_unlock_audit: expected no authorization collection")
        if authorization_unlock_audits["safety"]["stores_authorization"]:
            failures.append("runner_authorization_unlock_audit: expected no authorization storage")
        if authorization_unlock_audits["safety"]["writes_logs"]:
            failures.append("runner_authorization_unlock_audit: expected no log writes")
        if authorization_unlock_audits["safety"]["deletes_logs"]:
            failures.append("runner_authorization_unlock_audit: expected no log deletion")
        if authorization_unlock_audits["safety"]["writes_audit_log"]:
            failures.append("runner_authorization_unlock_audit: expected no audit log writes")
        if authorization_unlock_audits["safety"]["reads_audit_log"]:
            failures.append("runner_authorization_unlock_audit: expected no audit log reads")
        if authorization_unlock_audits["safety"]["writes_user_project"]:
            failures.append("runner_authorization_unlock_audit: expected no user project writes")
        if not authorization_unlock_audits["safety"]["authorization_unlock_audit_only"]:
            failures.append("runner_authorization_unlock_audit: expected audit-only safety flag")
        authorization_report = authorization_unlock_audits["reports"][0]
        if authorization_report["authorization_state"]["permission_granted_now"]:
            failures.append("runner_authorization_unlock_audit: expected permission not granted")
        if authorization_report["authorization_state"]["authorization_collected_now"]:
            failures.append("runner_authorization_unlock_audit: expected authorization not collected")
        if not authorization_report["unlock_items"]:
            failures.append("runner_authorization_unlock_audit: expected unlock items")
        if "human authorization round id" not in authorization_report["required_authorization_records"]:
            failures.append("runner_authorization_unlock_audit: expected human authorization record")
        if implementation_gap_checklists["status"] != "implementation_gap_required":
            failures.append("runner_implementation_gap_checklist: expected implementation_gap_required")
        if implementation_gap_checklists["summary"]["launchable_count"] != 0:
            failures.append("runner_implementation_gap_checklist: expected launchable_count=0")
        if implementation_gap_checklists["summary"]["gap_count"] < 1:
            failures.append("runner_implementation_gap_checklist: expected implementation gaps")
        if implementation_gap_checklists["safety"]["executes_commands"]:
            failures.append("runner_implementation_gap_checklist: expected no command execution")
        if implementation_gap_checklists["safety"]["creates_process"]:
            failures.append("runner_implementation_gap_checklist: expected no process creation")
        if implementation_gap_checklists["safety"]["launch_enabled"]:
            failures.append("runner_implementation_gap_checklist: expected launch disabled")
        if implementation_gap_checklists["safety"]["launch_api_available"]:
            failures.append("runner_implementation_gap_checklist: expected launch API unavailable")
        if implementation_gap_checklists["safety"]["implements_runner"]:
            failures.append("runner_implementation_gap_checklist: expected no runner implementation")
        if implementation_gap_checklists["safety"]["writes_code"]:
            failures.append("runner_implementation_gap_checklist: expected no code writes")
        if implementation_gap_checklists["safety"]["registers_post_api"]:
            failures.append("runner_implementation_gap_checklist: expected no POST registration")
        if implementation_gap_checklists["safety"]["imports_adapter"]:
            failures.append("runner_implementation_gap_checklist: expected no adapter import")
        if implementation_gap_checklists["safety"]["calls_execution_adapter"]:
            failures.append("runner_implementation_gap_checklist: expected no adapter call")
        if implementation_gap_checklists["safety"]["writes_logs"]:
            failures.append("runner_implementation_gap_checklist: expected no log writes")
        if implementation_gap_checklists["safety"]["writes_audit_log"]:
            failures.append("runner_implementation_gap_checklist: expected no audit log writes")
        if implementation_gap_checklists["safety"]["writes_user_project"]:
            failures.append("runner_implementation_gap_checklist: expected no user project writes")
        if not implementation_gap_checklists["safety"]["implementation_gap_checklist_only"]:
            failures.append("runner_implementation_gap_checklist: expected checklist-only safety flag")
        implementation_report = implementation_gap_checklists["reports"][0]
        if implementation_report["implementation_state"]["runner_implemented_now"]:
            failures.append("runner_implementation_gap_checklist: expected runner not implemented")
        if implementation_report["implementation_state"]["launch_api_registered_now"]:
            failures.append("runner_implementation_gap_checklist: expected launch API not registered")
        if implementation_report["implementation_state"]["can_start_real_test_now"]:
            failures.append("runner_implementation_gap_checklist: expected real test not startable")
        component_keys = {item["key"] for item in implementation_report["implementation_components"]}
        if "execution_adapter" not in component_keys:
            failures.append("runner_implementation_gap_checklist: expected execution adapter component")
        if "cancel_timeout_endpoints" not in component_keys:
            failures.append("runner_implementation_gap_checklist: expected cancel/timeout component")
        if cancel_timeout_contracts["status"] != "cancel_timeout_contract_required":
            failures.append("runner_cancel_timeout_contract: expected cancel_timeout_contract_required")
        if cancel_timeout_contracts["summary"]["launchable_count"] != 0:
            failures.append("runner_cancel_timeout_contract: expected launchable_count=0")
        if cancel_timeout_contracts["summary"]["registered_endpoint_count"] != 0:
            failures.append("runner_cancel_timeout_contract: expected registered_endpoint_count=0")
        if cancel_timeout_contracts["summary"]["future_endpoint_count"] < 2:
            failures.append("runner_cancel_timeout_contract: expected future endpoints")
        if cancel_timeout_contracts["safety"]["executes_commands"]:
            failures.append("runner_cancel_timeout_contract: expected no command execution")
        if cancel_timeout_contracts["safety"]["creates_process"]:
            failures.append("runner_cancel_timeout_contract: expected no process creation")
        if cancel_timeout_contracts["safety"]["launch_enabled"]:
            failures.append("runner_cancel_timeout_contract: expected launch disabled")
        if cancel_timeout_contracts["safety"]["launch_api_available"]:
            failures.append("runner_cancel_timeout_contract: expected launch API unavailable")
        if cancel_timeout_contracts["safety"]["registers_post_api"]:
            failures.append("runner_cancel_timeout_contract: expected no POST registration")
        if cancel_timeout_contracts["safety"]["registers_cancel_api"]:
            failures.append("runner_cancel_timeout_contract: expected no cancel API registration")
        if cancel_timeout_contracts["safety"]["registers_timeout_api"]:
            failures.append("runner_cancel_timeout_contract: expected no timeout API registration")
        if cancel_timeout_contracts["safety"]["calls_execution_adapter"]:
            failures.append("runner_cancel_timeout_contract: expected no adapter call")
        if cancel_timeout_contracts["safety"]["cancels_process"]:
            failures.append("runner_cancel_timeout_contract: expected no process cancel")
        if cancel_timeout_contracts["safety"]["sends_process_signal"]:
            failures.append("runner_cancel_timeout_contract: expected no process signal")
        if cancel_timeout_contracts["safety"]["kills_process"]:
            failures.append("runner_cancel_timeout_contract: expected no process kill")
        if cancel_timeout_contracts["safety"]["schedules_timeout"]:
            failures.append("runner_cancel_timeout_contract: expected no timeout scheduling")
        if cancel_timeout_contracts["safety"]["writes_runner_events"]:
            failures.append("runner_cancel_timeout_contract: expected no runner event writes")
        if cancel_timeout_contracts["safety"]["writes_logs"]:
            failures.append("runner_cancel_timeout_contract: expected no log writes")
        if cancel_timeout_contracts["safety"]["writes_audit_log"]:
            failures.append("runner_cancel_timeout_contract: expected no audit log writes")
        if cancel_timeout_contracts["safety"]["writes_user_project"]:
            failures.append("runner_cancel_timeout_contract: expected no user project writes")
        if not cancel_timeout_contracts["safety"]["cancel_timeout_contract_only"]:
            failures.append("runner_cancel_timeout_contract: expected contract-only safety flag")
        cancel_timeout_report = cancel_timeout_contracts["reports"][0]
        endpoint_ids = {item["id"] for item in cancel_timeout_report["future_endpoints"]}
        if "runner_cancel" not in endpoint_ids:
            failures.append("runner_cancel_timeout_contract: expected cancel endpoint contract")
        if "runner_timeout" not in endpoint_ids:
            failures.append("runner_cancel_timeout_contract: expected timeout endpoint contract")
        if cancel_timeout_report["contract_state"]["endpoints_registered_now"]:
            failures.append("runner_cancel_timeout_contract: expected endpoints not registered")
        if "running -> cancelling" not in cancel_timeout_report["allowed_future_state_transitions"]:
            failures.append("runner_cancel_timeout_contract: expected cancel transition")
        if "timeout_finalized" not in cancel_timeout_report["required_future_events"]:
            failures.append("runner_cancel_timeout_contract: expected timeout finalized event")
        if cancel_timeout_real_apis["status"] != "cancel_timeout_api_available":
            failures.append("runner_cancel_timeout_real_api: expected cancel_timeout_api_available")
        if cancel_timeout_real_apis["summary"]["registered_endpoint_count"] != 2:
            failures.append("runner_cancel_timeout_real_api: expected two registered endpoints")
        if cancel_timeout_real_apis["summary"]["active_process_count"] != 0:
            failures.append("runner_cancel_timeout_real_api: expected no active process without launch")
        if cancel_timeout_real_apis["safety"]["executes_commands"]:
            failures.append("runner_cancel_timeout_real_api: expected no command execution")
        if cancel_timeout_real_apis["safety"]["creates_process"]:
            failures.append("runner_cancel_timeout_real_api: expected no process creation")
        if not cancel_timeout_real_apis["safety"]["registers_post_api"]:
            failures.append("runner_cancel_timeout_real_api: expected POST registration")
        if not cancel_timeout_real_apis["safety"]["registers_cancel_api"]:
            failures.append("runner_cancel_timeout_real_api: expected cancel API registration")
        if not cancel_timeout_real_apis["safety"]["registers_timeout_api"]:
            failures.append("runner_cancel_timeout_real_api: expected timeout API registration")
        if not cancel_timeout_real_apis["safety"]["controls_process"]:
            failures.append("runner_cancel_timeout_real_api: expected active-process control")
        if not cancel_timeout_real_apis["safety"]["cancels_process"]:
            failures.append("runner_cancel_timeout_real_api: expected cancel capability")
        if not cancel_timeout_real_apis["safety"]["sends_process_signal"]:
            failures.append("runner_cancel_timeout_real_api: expected terminate signal capability")
        if cancel_timeout_real_apis["safety"]["kills_process"]:
            failures.append("runner_cancel_timeout_real_api: expected no process kill")
        if cancel_timeout_real_apis["safety"]["accepts_pid"]:
            failures.append("runner_cancel_timeout_real_api: expected no pid input")
        if cancel_timeout_real_apis["safety"]["accepts_shell"]:
            failures.append("runner_cancel_timeout_real_api: expected no shell input")
        if cancel_timeout_real_apis["safety"]["calls_execution_adapter"]:
            failures.append("runner_cancel_timeout_real_api: expected no adapter call")
        if cancel_timeout_real_apis["safety"]["writes_runner_events"]:
            failures.append("runner_cancel_timeout_real_api: expected no runner event writes")
        if cancel_timeout_real_apis["safety"]["writes_audit_log"]:
            failures.append("runner_cancel_timeout_real_api: expected no audit log writes")
        if cancel_timeout_real_apis["safety"]["writes_user_project"]:
            failures.append("runner_cancel_timeout_real_api: expected no user project writes")
        if first_real_tests_before_launch["status"] != "first_real_test_not_started":
            failures.append("runner_first_real_test: expected not_started before launch")
        if first_execution["status"] != "completed":
            failures.append("runner_first_real_test: expected completed execution from low-risk sample")
        if first_execution["exit_code"] != 0:
            failures.append("runner_first_real_test: expected exit_code=0")
        if first_real_tests_after_launch["status"] != "first_real_test_completed":
            failures.append("runner_first_real_test: expected completed report after launch")
        if first_real_tests_after_launch["summary"]["execution_count"] != 1:
            failures.append("runner_first_real_test: expected one recorded execution after launch")
        if first_real_tests_after_launch["summary"]["first_real_test_completed_count"] != 1:
            failures.append("runner_first_real_test: expected one completed first real test")
        if first_real_tests_after_launch["safety"]["executes_commands"]:
            failures.append("runner_first_real_test: expected report layer to avoid command execution")
        if first_real_tests_after_launch["safety"]["creates_process"]:
            failures.append("runner_first_real_test: expected report layer to avoid process creation")
        if first_real_tests_after_launch["safety"]["registers_post_api"]:
            failures.append("runner_first_real_test: expected no new POST registration")
        if first_real_tests_after_launch["safety"]["calls_execution_adapter"]:
            failures.append("runner_first_real_test: expected report layer not to call adapter")
        if first_real_tests_after_launch["safety"]["writes_user_project"]:
            failures.append("runner_first_real_test: expected no user project writes")
        if session_state_schemas["status"] != "session_state_schema_required":
            failures.append("runner_session_state_schema: expected session_state_schema_required")
        if session_state_schemas["summary"]["launchable_count"] != 0:
            failures.append("runner_session_state_schema: expected launchable_count=0")
        if session_state_schemas["summary"]["persisted_session_count"] != 0:
            failures.append("runner_session_state_schema: expected no persisted sessions")
        if session_state_schemas["summary"]["active_session_count"] != 0:
            failures.append("runner_session_state_schema: expected no active sessions")
        if session_state_schemas["summary"]["state_count"] < 8:
            failures.append("runner_session_state_schema: expected declared states")
        if session_state_schemas["safety"]["executes_commands"]:
            failures.append("runner_session_state_schema: expected no command execution")
        if session_state_schemas["safety"]["creates_process"]:
            failures.append("runner_session_state_schema: expected no process creation")
        if session_state_schemas["safety"]["launch_enabled"]:
            failures.append("runner_session_state_schema: expected launch disabled")
        if session_state_schemas["safety"]["launch_api_available"]:
            failures.append("runner_session_state_schema: expected launch API unavailable")
        if session_state_schemas["safety"]["registers_post_api"]:
            failures.append("runner_session_state_schema: expected no POST registration")
        if session_state_schemas["safety"]["registers_launch_api"]:
            failures.append("runner_session_state_schema: expected no launch API registration")
        if session_state_schemas["safety"]["registers_cancel_api"]:
            failures.append("runner_session_state_schema: expected no cancel API registration")
        if session_state_schemas["safety"]["registers_timeout_api"]:
            failures.append("runner_session_state_schema: expected no timeout API registration")
        if session_state_schemas["safety"]["creates_session"]:
            failures.append("runner_session_state_schema: expected no session creation")
        if session_state_schemas["safety"]["stores_session_state"]:
            failures.append("runner_session_state_schema: expected no session state storage")
        if session_state_schemas["safety"]["mutates_session_state"]:
            failures.append("runner_session_state_schema: expected no session state mutation")
        if session_state_schemas["safety"]["writes_session_state_store"]:
            failures.append("runner_session_state_schema: expected no session state store writes")
        if session_state_schemas["safety"]["calls_execution_adapter"]:
            failures.append("runner_session_state_schema: expected no adapter call")
        if session_state_schemas["safety"]["cancels_process"]:
            failures.append("runner_session_state_schema: expected no process cancel")
        if session_state_schemas["safety"]["sends_process_signal"]:
            failures.append("runner_session_state_schema: expected no process signal")
        if session_state_schemas["safety"]["kills_process"]:
            failures.append("runner_session_state_schema: expected no process kill")
        if session_state_schemas["safety"]["schedules_timeout"]:
            failures.append("runner_session_state_schema: expected no timeout scheduling")
        if session_state_schemas["safety"]["opens_stdout_stderr"]:
            failures.append("runner_session_state_schema: expected no stdout/stderr opening")
        if session_state_schemas["safety"]["writes_runner_events"]:
            failures.append("runner_session_state_schema: expected no runner event writes")
        if session_state_schemas["safety"]["writes_logs"]:
            failures.append("runner_session_state_schema: expected no log writes")
        if session_state_schemas["safety"]["writes_audit_log"]:
            failures.append("runner_session_state_schema: expected no audit log writes")
        if session_state_schemas["safety"]["writes_user_project"]:
            failures.append("runner_session_state_schema: expected no user project writes")
        if not session_state_schemas["safety"]["session_state_schema_only"]:
            failures.append("runner_session_state_schema: expected schema-only safety flag")
        session_state_report = session_state_schemas["reports"][0]
        if session_state_report["schema_state"]["session_store_available_now"]:
            failures.append("runner_session_state_schema: expected no session store")
        if "running" not in session_state_report["allowed_states"]:
            failures.append("runner_session_state_schema: expected running state")
        if "running -> cancelling" not in session_state_report["allowed_future_transitions"]:
            failures.append("runner_session_state_schema: expected cancel transition")
        if "terminal_state_written_once" not in session_state_report["required_future_guards"]:
            failures.append("runner_session_state_schema: expected terminal state guard")
        if real_test_readiness["status"] != "real_test_blocked":
            failures.append("runner_real_test_readiness: expected real_test_blocked")
        if real_test_readiness["summary"]["launchable_count"] != 0:
            failures.append("runner_real_test_readiness: expected launchable_count=0")
        if real_test_readiness["summary"]["can_start_real_test_count"] != 0:
            failures.append("runner_real_test_readiness: expected no startable real tests")
        if real_test_readiness["summary"]["missing_gate_count"] < 1:
            failures.append("runner_real_test_readiness: expected missing gates")
        if real_test_readiness["safety"]["executes_commands"]:
            failures.append("runner_real_test_readiness: expected no command execution")
        if real_test_readiness["safety"]["creates_process"]:
            failures.append("runner_real_test_readiness: expected no process creation")
        if real_test_readiness["safety"]["launch_enabled"]:
            failures.append("runner_real_test_readiness: expected launch disabled")
        if real_test_readiness["safety"]["launch_api_available"]:
            failures.append("runner_real_test_readiness: expected launch API unavailable")
        if real_test_readiness["safety"]["registers_post_api"]:
            failures.append("runner_real_test_readiness: expected no POST registration")
        if real_test_readiness["safety"]["registers_launch_api"]:
            failures.append("runner_real_test_readiness: expected no launch API registration")
        if real_test_readiness["safety"]["registers_cancel_api"]:
            failures.append("runner_real_test_readiness: expected no cancel API registration")
        if real_test_readiness["safety"]["registers_timeout_api"]:
            failures.append("runner_real_test_readiness: expected no timeout API registration")
        if real_test_readiness["safety"]["implements_runner"]:
            failures.append("runner_real_test_readiness: expected no runner implementation")
        if real_test_readiness["safety"]["imports_adapter"]:
            failures.append("runner_real_test_readiness: expected no adapter import")
        if real_test_readiness["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_test_readiness: expected no adapter call")
        if real_test_readiness["safety"]["creates_session"]:
            failures.append("runner_real_test_readiness: expected no session creation")
        if real_test_readiness["safety"]["stores_session_state"]:
            failures.append("runner_real_test_readiness: expected no session state storage")
        if real_test_readiness["safety"]["mutates_session_state"]:
            failures.append("runner_real_test_readiness: expected no session state mutation")
        if real_test_readiness["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_test_readiness: expected no stdout/stderr opening")
        if real_test_readiness["safety"]["writes_runner_events"]:
            failures.append("runner_real_test_readiness: expected no runner event writes")
        if real_test_readiness["safety"]["reads_log_files"]:
            failures.append("runner_real_test_readiness: expected no log reads")
        if real_test_readiness["safety"]["writes_logs"]:
            failures.append("runner_real_test_readiness: expected no log writes")
        if real_test_readiness["safety"]["writes_audit_log"]:
            failures.append("runner_real_test_readiness: expected no audit log writes")
        if real_test_readiness["safety"]["collects_human_authorization"]:
            failures.append("runner_real_test_readiness: expected no authorization collection")
        if real_test_readiness["safety"]["stores_authorization"]:
            failures.append("runner_real_test_readiness: expected no authorization storage")
        if real_test_readiness["safety"]["grants_permission"]:
            failures.append("runner_real_test_readiness: expected no permission grants")
        if real_test_readiness["safety"]["writes_user_project"]:
            failures.append("runner_real_test_readiness: expected no user project writes")
        if not real_test_readiness["safety"]["real_test_readiness_only"]:
            failures.append("runner_real_test_readiness: expected readiness-only safety flag")
        real_test_report = real_test_readiness["reports"][0]
        if real_test_report["launch_state"]["can_start_real_test_now"]:
            failures.append("runner_real_test_readiness: expected real test not startable")
        gate_keys = {item["key"] for item in real_test_report["readiness_gates"]}
        if "launch_api_registered" not in gate_keys:
            failures.append("runner_real_test_readiness: expected launch API gate")
        if "fresh_human_authorization_recorded" not in gate_keys:
            failures.append("runner_real_test_readiness: expected authorization gate")
        if real_test_authorization_checklists["status"] != "authorization_checklist_required":
            failures.append("runner_real_test_authorization_checklist: expected authorization_checklist_required")
        if real_test_authorization_checklists["summary"]["launchable_count"] != 0:
            failures.append("runner_real_test_authorization_checklist: expected launchable_count=0")
        if real_test_authorization_checklists["summary"]["collected_authorization_count"] != 0:
            failures.append("runner_real_test_authorization_checklist: expected no collected authorization")
        if real_test_authorization_checklists["summary"]["permission_granted_count"] != 0:
            failures.append("runner_real_test_authorization_checklist: expected no permission grants")
        if real_test_authorization_checklists["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_real_test_authorization_checklist: expected missing evidence")
        if real_test_authorization_checklists["safety"]["executes_commands"]:
            failures.append("runner_real_test_authorization_checklist: expected no command execution")
        if real_test_authorization_checklists["safety"]["creates_process"]:
            failures.append("runner_real_test_authorization_checklist: expected no process creation")
        if real_test_authorization_checklists["safety"]["launch_enabled"]:
            failures.append("runner_real_test_authorization_checklist: expected launch disabled")
        if real_test_authorization_checklists["safety"]["launch_api_available"]:
            failures.append("runner_real_test_authorization_checklist: expected launch API unavailable")
        if real_test_authorization_checklists["safety"]["registers_post_api"]:
            failures.append("runner_real_test_authorization_checklist: expected no POST registration")
        if real_test_authorization_checklists["safety"]["registers_launch_api"]:
            failures.append("runner_real_test_authorization_checklist: expected no launch API registration")
        if real_test_authorization_checklists["safety"]["registers_cancel_api"]:
            failures.append("runner_real_test_authorization_checklist: expected no cancel API registration")
        if real_test_authorization_checklists["safety"]["registers_timeout_api"]:
            failures.append("runner_real_test_authorization_checklist: expected no timeout API registration")
        if real_test_authorization_checklists["safety"]["implements_runner"]:
            failures.append("runner_real_test_authorization_checklist: expected no runner implementation")
        if real_test_authorization_checklists["safety"]["imports_adapter"]:
            failures.append("runner_real_test_authorization_checklist: expected no adapter import")
        if real_test_authorization_checklists["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_test_authorization_checklist: expected no adapter call")
        if real_test_authorization_checklists["safety"]["creates_session"]:
            failures.append("runner_real_test_authorization_checklist: expected no session creation")
        if real_test_authorization_checklists["safety"]["stores_session_state"]:
            failures.append("runner_real_test_authorization_checklist: expected no session state storage")
        if real_test_authorization_checklists["safety"]["mutates_session_state"]:
            failures.append("runner_real_test_authorization_checklist: expected no session state mutation")
        if real_test_authorization_checklists["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_test_authorization_checklist: expected no stdout/stderr opening")
        if real_test_authorization_checklists["safety"]["writes_runner_events"]:
            failures.append("runner_real_test_authorization_checklist: expected no runner event writes")
        if real_test_authorization_checklists["safety"]["reads_log_files"]:
            failures.append("runner_real_test_authorization_checklist: expected no log reads")
        if real_test_authorization_checklists["safety"]["writes_logs"]:
            failures.append("runner_real_test_authorization_checklist: expected no log writes")
        if real_test_authorization_checklists["safety"]["writes_audit_log"]:
            failures.append("runner_real_test_authorization_checklist: expected no audit log writes")
        if real_test_authorization_checklists["safety"]["collects_human_authorization"]:
            failures.append("runner_real_test_authorization_checklist: expected no authorization collection")
        if real_test_authorization_checklists["safety"]["stores_authorization"]:
            failures.append("runner_real_test_authorization_checklist: expected no authorization storage")
        if real_test_authorization_checklists["safety"]["grants_permission"]:
            failures.append("runner_real_test_authorization_checklist: expected no permission grants")
        if real_test_authorization_checklists["safety"]["writes_user_project"]:
            failures.append("runner_real_test_authorization_checklist: expected no user project writes")
        if not real_test_authorization_checklists["safety"]["authorization_checklist_only"]:
            failures.append("runner_real_test_authorization_checklist: expected checklist-only safety flag")
        authorization_report = real_test_authorization_checklists["reports"][0]
        if authorization_report["authorization_state"]["authorization_collected_now"]:
            failures.append("runner_real_test_authorization_checklist: expected authorization not collected")
        if authorization_report["authorization_state"]["permission_granted_now"]:
            failures.append("runner_real_test_authorization_checklist: expected permission not granted")
        authorization_keys = {item["key"] for item in authorization_report["authorization_items"]}
        if "launch_api_registered" not in authorization_keys:
            failures.append("runner_real_test_authorization_checklist: expected launch API authorization item")
        if "fresh_human_authorization_recorded" not in authorization_keys:
            failures.append("runner_real_test_authorization_checklist: expected human authorization item")
        if real_test_authorization_packages["status"] != "authorization_package_required":
            failures.append("runner_real_test_authorization_package: expected authorization_package_required")
        if real_test_authorization_packages["summary"]["launchable_count"] != 0:
            failures.append("runner_real_test_authorization_package: expected launchable_count=0")
        if real_test_authorization_packages["summary"]["collected_authorization_count"] != 0:
            failures.append("runner_real_test_authorization_package: expected no collected authorization")
        if real_test_authorization_packages["summary"]["stored_authorization_count"] != 0:
            failures.append("runner_real_test_authorization_package: expected no stored authorization")
        if real_test_authorization_packages["summary"]["permission_granted_count"] != 0:
            failures.append("runner_real_test_authorization_package: expected no permission grants")
        if real_test_authorization_packages["summary"]["risk_acknowledgement_count"] < 5:
            failures.append("runner_real_test_authorization_package: expected risk acknowledgements")
        if real_test_authorization_packages["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_real_test_authorization_package: expected missing evidence")
        if real_test_authorization_packages["safety"]["executes_commands"]:
            failures.append("runner_real_test_authorization_package: expected no command execution")
        if real_test_authorization_packages["safety"]["creates_process"]:
            failures.append("runner_real_test_authorization_package: expected no process creation")
        if real_test_authorization_packages["safety"]["launch_enabled"]:
            failures.append("runner_real_test_authorization_package: expected launch disabled")
        if real_test_authorization_packages["safety"]["launch_api_available"]:
            failures.append("runner_real_test_authorization_package: expected launch API unavailable")
        if real_test_authorization_packages["safety"]["registers_post_api"]:
            failures.append("runner_real_test_authorization_package: expected no POST registration")
        if real_test_authorization_packages["safety"]["registers_launch_api"]:
            failures.append("runner_real_test_authorization_package: expected no launch API registration")
        if real_test_authorization_packages["safety"]["registers_cancel_api"]:
            failures.append("runner_real_test_authorization_package: expected no cancel API registration")
        if real_test_authorization_packages["safety"]["registers_timeout_api"]:
            failures.append("runner_real_test_authorization_package: expected no timeout API registration")
        if real_test_authorization_packages["safety"]["implements_runner"]:
            failures.append("runner_real_test_authorization_package: expected no runner implementation")
        if real_test_authorization_packages["safety"]["imports_adapter"]:
            failures.append("runner_real_test_authorization_package: expected no adapter import")
        if real_test_authorization_packages["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_test_authorization_package: expected no adapter call")
        if real_test_authorization_packages["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_test_authorization_package: expected no stdout/stderr opening")
        if real_test_authorization_packages["safety"]["writes_runner_events"]:
            failures.append("runner_real_test_authorization_package: expected no runner event writes")
        if real_test_authorization_packages["safety"]["reads_log_files"]:
            failures.append("runner_real_test_authorization_package: expected no log reads")
        if real_test_authorization_packages["safety"]["writes_logs"]:
            failures.append("runner_real_test_authorization_package: expected no log writes")
        if real_test_authorization_packages["safety"]["writes_audit_log"]:
            failures.append("runner_real_test_authorization_package: expected no audit log writes")
        if real_test_authorization_packages["safety"]["collects_human_authorization"]:
            failures.append("runner_real_test_authorization_package: expected no authorization collection")
        if real_test_authorization_packages["safety"]["stores_authorization"]:
            failures.append("runner_real_test_authorization_package: expected no authorization storage")
        if real_test_authorization_packages["safety"]["grants_permission"]:
            failures.append("runner_real_test_authorization_package: expected no permission grants")
        if real_test_authorization_packages["safety"]["writes_user_project"]:
            failures.append("runner_real_test_authorization_package: expected no user project writes")
        if not real_test_authorization_packages["safety"]["authorization_package_only"]:
            failures.append("runner_real_test_authorization_package: expected package-only safety flag")
        authorization_package_report = real_test_authorization_packages["reports"][0]
        if authorization_package_report["package_state"]["authorization_collected_now"]:
            failures.append("runner_real_test_authorization_package: expected authorization not collected")
        if authorization_package_report["package_state"]["authorization_stored_now"]:
            failures.append("runner_real_test_authorization_package: expected authorization not stored")
        if authorization_package_report["package_state"]["permission_granted_now"]:
            failures.append("runner_real_test_authorization_package: expected permission not granted")
        package_review_keys = {item["key"] for item in authorization_package_report["review_items"]}
        if "launch_api_registered" not in package_review_keys:
            failures.append("runner_real_test_authorization_package: expected launch API review item")
        if "fresh_human_authorization_recorded" not in package_review_keys:
            failures.append("runner_real_test_authorization_package: expected human authorization review item")
        if real_test_sandbox_policies["status"] != "sandbox_policy_required":
            failures.append("runner_real_test_sandbox_policy: expected sandbox_policy_required")
        if real_test_sandbox_policies["summary"]["launchable_count"] != 0:
            failures.append("runner_real_test_sandbox_policy: expected launchable_count=0")
        if real_test_sandbox_policies["summary"]["workspace_rule_count"] < 3:
            failures.append("runner_real_test_sandbox_policy: expected workspace rules")
        if real_test_sandbox_policies["summary"]["environment_rule_count"] < 3:
            failures.append("runner_real_test_sandbox_policy: expected environment rules")
        if real_test_sandbox_policies["summary"]["timeout_rule_count"] < 3:
            failures.append("runner_real_test_sandbox_policy: expected timeout rules")
        if real_test_sandbox_policies["summary"]["log_rule_count"] < 3:
            failures.append("runner_real_test_sandbox_policy: expected log rules")
        if real_test_sandbox_policies["summary"]["permission_rule_count"] < 3:
            failures.append("runner_real_test_sandbox_policy: expected permission rules")
        if real_test_sandbox_policies["safety"]["executes_commands"]:
            failures.append("runner_real_test_sandbox_policy: expected no command execution")
        if real_test_sandbox_policies["safety"]["creates_process"]:
            failures.append("runner_real_test_sandbox_policy: expected no process creation")
        if real_test_sandbox_policies["safety"]["launch_enabled"]:
            failures.append("runner_real_test_sandbox_policy: expected launch disabled")
        if real_test_sandbox_policies["safety"]["applies_sandbox_policy"]:
            failures.append("runner_real_test_sandbox_policy: expected no applied sandbox policy")
        if real_test_sandbox_policies["safety"]["writes_environment"]:
            failures.append("runner_real_test_sandbox_policy: expected no environment writes")
        if real_test_sandbox_policies["safety"]["creates_log_directory"]:
            failures.append("runner_real_test_sandbox_policy: expected no log directory creation")
        if real_test_sandbox_policies["safety"]["changes_permissions"]:
            failures.append("runner_real_test_sandbox_policy: expected no permission changes")
        if real_test_sandbox_policies["safety"]["grants_process_permission"]:
            failures.append("runner_real_test_sandbox_policy: expected no process permission grants")
        if real_test_sandbox_policies["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_test_sandbox_policy: expected no stdout/stderr opening")
        if real_test_sandbox_policies["safety"]["writes_runner_events"]:
            failures.append("runner_real_test_sandbox_policy: expected no runner event writes")
        if real_test_sandbox_policies["safety"]["reads_log_files"]:
            failures.append("runner_real_test_sandbox_policy: expected no log reads")
        if real_test_sandbox_policies["safety"]["writes_logs"]:
            failures.append("runner_real_test_sandbox_policy: expected no log writes")
        if real_test_sandbox_policies["safety"]["writes_audit_log"]:
            failures.append("runner_real_test_sandbox_policy: expected no audit log writes")
        if real_test_sandbox_policies["safety"]["writes_user_project"]:
            failures.append("runner_real_test_sandbox_policy: expected no user project writes")
        if not real_test_sandbox_policies["safety"]["sandbox_policy_only"]:
            failures.append("runner_real_test_sandbox_policy: expected sandbox-policy-only safety flag")
        sandbox_policy_report = real_test_sandbox_policies["reports"][0]
        if sandbox_policy_report["policy_state"]["policy_applied_now"]:
            failures.append("runner_real_test_sandbox_policy: expected policy not applied")
        if sandbox_policy_report["policy_state"]["can_launch_now"]:
            failures.append("runner_real_test_sandbox_policy: expected launch disabled in policy state")
        if real_test_final_checklists["status"] != "final_checklist_required":
            failures.append("runner_real_test_final_checklist: expected final_checklist_required")
        if real_test_final_checklists["summary"]["launchable_count"] != 0:
            failures.append("runner_real_test_final_checklist: expected launchable_count=0")
        if real_test_final_checklists["summary"]["check_item_count"] < 8:
            failures.append("runner_real_test_final_checklist: expected checklist items")
        if real_test_final_checklists["summary"]["passed_item_count"] != 0:
            failures.append("runner_real_test_final_checklist: expected no passed items")
        if real_test_final_checklists["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_real_test_final_checklist: expected missing evidence")
        if real_test_final_checklists["safety"]["executes_commands"]:
            failures.append("runner_real_test_final_checklist: expected no command execution")
        if real_test_final_checklists["safety"]["creates_process"]:
            failures.append("runner_real_test_final_checklist: expected no process creation")
        if real_test_final_checklists["safety"]["launch_enabled"]:
            failures.append("runner_real_test_final_checklist: expected launch disabled")
        if real_test_final_checklists["safety"]["marks_checklist_complete"]:
            failures.append("runner_real_test_final_checklist: expected checklist not completed")
        if real_test_final_checklists["safety"]["grants_launch_permission"]:
            failures.append("runner_real_test_final_checklist: expected no launch permission")
        if real_test_final_checklists["safety"]["registers_launch_api"]:
            failures.append("runner_real_test_final_checklist: expected no launch API registration")
        if real_test_final_checklists["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_test_final_checklist: expected no adapter call")
        if real_test_final_checklists["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_test_final_checklist: expected no stdout/stderr opening")
        if real_test_final_checklists["safety"]["writes_runner_events"]:
            failures.append("runner_real_test_final_checklist: expected no runner event writes")
        if real_test_final_checklists["safety"]["writes_audit_log"]:
            failures.append("runner_real_test_final_checklist: expected no audit log writes")
        if real_test_final_checklists["safety"]["writes_user_project"]:
            failures.append("runner_real_test_final_checklist: expected no user project writes")
        if not real_test_final_checklists["safety"]["final_checklist_only"]:
            failures.append("runner_real_test_final_checklist: expected checklist-only safety flag")
        final_checklist_report = real_test_final_checklists["reports"][0]
        if final_checklist_report["checklist_state"]["checklist_completed_now"]:
            failures.append("runner_real_test_final_checklist: expected checklist state incomplete")
        if final_checklist_report["checklist_state"]["can_launch_now"]:
            failures.append("runner_real_test_final_checklist: expected launch disabled in checklist state")
        if real_test_ui_previews["status"] != "ui_preview_required":
            failures.append("runner_real_test_ui_preview: expected ui_preview_required")
        if real_test_ui_previews["summary"]["launchable_count"] != 0:
            failures.append("runner_real_test_ui_preview: expected launchable_count=0")
        if real_test_ui_previews["summary"]["preview_item_count"] < 6:
            failures.append("runner_real_test_ui_preview: expected preview items")
        if real_test_ui_previews["summary"]["disabled_control_count"] < 3:
            failures.append("runner_real_test_ui_preview: expected disabled controls")
        if real_test_ui_previews["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_real_test_ui_preview: expected missing evidence")
        if real_test_ui_previews["safety"]["executes_commands"]:
            failures.append("runner_real_test_ui_preview: expected no command execution")
        if real_test_ui_previews["safety"]["creates_process"]:
            failures.append("runner_real_test_ui_preview: expected no process creation")
        if real_test_ui_previews["safety"]["launch_enabled"]:
            failures.append("runner_real_test_ui_preview: expected launch disabled")
        if real_test_ui_previews["safety"]["enables_launch_ui"]:
            failures.append("runner_real_test_ui_preview: expected launch UI disabled")
        if real_test_ui_previews["safety"]["enables_cancel_ui"]:
            failures.append("runner_real_test_ui_preview: expected cancel UI disabled")
        if real_test_ui_previews["safety"]["enables_timeout_ui"]:
            failures.append("runner_real_test_ui_preview: expected timeout UI disabled")
        if real_test_ui_previews["safety"]["registers_launch_api"]:
            failures.append("runner_real_test_ui_preview: expected no launch API registration")
        if real_test_ui_previews["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_test_ui_preview: expected no adapter call")
        if real_test_ui_previews["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_test_ui_preview: expected no stdout/stderr opening")
        if real_test_ui_previews["safety"]["writes_runner_events"]:
            failures.append("runner_real_test_ui_preview: expected no runner event writes")
        if real_test_ui_previews["safety"]["writes_audit_log"]:
            failures.append("runner_real_test_ui_preview: expected no audit log writes")
        if real_test_ui_previews["safety"]["writes_user_project"]:
            failures.append("runner_real_test_ui_preview: expected no user project writes")
        if not real_test_ui_previews["safety"]["ui_preview_only"]:
            failures.append("runner_real_test_ui_preview: expected preview-only safety flag")
        ui_preview_report = real_test_ui_previews["reports"][0]
        if ui_preview_report["preview_state"]["launch_button_enabled_now"]:
            failures.append("runner_real_test_ui_preview: expected launch button disabled")
        if ui_preview_report["preview_state"]["cancel_button_enabled_now"]:
            failures.append("runner_real_test_ui_preview: expected cancel button disabled")
        if ui_preview_report["preview_state"]["timeout_button_enabled_now"]:
            failures.append("runner_real_test_ui_preview: expected timeout button disabled")
        if ui_preview_report["preview_state"]["can_launch_now"]:
            failures.append("runner_real_test_ui_preview: expected launch disabled in preview state")
        if real_execution_stage_boundary_reviews["status"] != "stage_boundary_review_required":
            failures.append("runner_real_execution_stage_boundary_review: expected stage_boundary_review_required")
        if real_execution_stage_boundary_reviews["summary"]["launchable_count"] != 0:
            failures.append("runner_real_execution_stage_boundary_review: expected launchable_count=0")
        if real_execution_stage_boundary_reviews["summary"]["implementation_allowed_count"] != 0:
            failures.append("runner_real_execution_stage_boundary_review: expected no implementation allowed")
        if real_execution_stage_boundary_reviews["summary"]["missing_unlock_count"] < 1:
            failures.append("runner_real_execution_stage_boundary_review: expected missing unlock requirements")
        if real_execution_stage_boundary_reviews["safety"]["executes_commands"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no command execution")
        if real_execution_stage_boundary_reviews["safety"]["creates_process"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no process creation")
        if real_execution_stage_boundary_reviews["safety"]["allows_real_execution_implementation"]:
            failures.append("runner_real_execution_stage_boundary_review: expected implementation locked")
        if real_execution_stage_boundary_reviews["safety"]["writes_code"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no code writes")
        if real_execution_stage_boundary_reviews["safety"]["registers_launch_api"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no launch API registration")
        if real_execution_stage_boundary_reviews["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no adapter call")
        if real_execution_stage_boundary_reviews["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no stdout/stderr opening")
        if real_execution_stage_boundary_reviews["safety"]["writes_runner_events"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no runner event writes")
        if real_execution_stage_boundary_reviews["safety"]["writes_audit_log"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no audit log writes")
        if real_execution_stage_boundary_reviews["safety"]["writes_user_project"]:
            failures.append("runner_real_execution_stage_boundary_review: expected no user project writes")
        if not real_execution_stage_boundary_reviews["safety"]["stage_boundary_review_only"]:
            failures.append("runner_real_execution_stage_boundary_review: expected review-only safety flag")
        boundary_review_report = real_execution_stage_boundary_reviews["reports"][0]
        if boundary_review_report["review_state"]["stage_three_unlocked_now"]:
            failures.append("runner_real_execution_stage_boundary_review: expected stage locked")
        if boundary_review_report["review_state"]["implementation_allowed_now"]:
            failures.append("runner_real_execution_stage_boundary_review: expected implementation disabled")
        if boundary_review_report["review_state"]["launch_allowed_now"]:
            failures.append("runner_real_execution_stage_boundary_review: expected launch disabled")
        if real_execution_unlock_material_reviews["status"] != "unlock_material_review_required":
            failures.append("runner_real_execution_unlock_material_review: expected unlock_material_review_required")
        if real_execution_unlock_material_reviews["summary"]["launchable_count"] != 0:
            failures.append("runner_real_execution_unlock_material_review: expected launchable_count=0")
        if real_execution_unlock_material_reviews["summary"]["implementation_allowed_count"] != 0:
            failures.append("runner_real_execution_unlock_material_review: expected no implementation allowed")
        if real_execution_unlock_material_reviews["summary"]["missing_material_count"] < 1:
            failures.append("runner_real_execution_unlock_material_review: expected missing materials")
        if real_execution_unlock_material_reviews["safety"]["executes_commands"]:
            failures.append("runner_real_execution_unlock_material_review: expected no command execution")
        if real_execution_unlock_material_reviews["safety"]["creates_process"]:
            failures.append("runner_real_execution_unlock_material_review: expected no process creation")
        if real_execution_unlock_material_reviews["safety"]["collects_unlock_materials"]:
            failures.append("runner_real_execution_unlock_material_review: expected no material collection")
        if real_execution_unlock_material_reviews["safety"]["stores_unlock_materials"]:
            failures.append("runner_real_execution_unlock_material_review: expected no material storage")
        if real_execution_unlock_material_reviews["safety"]["accepts_unlock_materials"]:
            failures.append("runner_real_execution_unlock_material_review: expected no material acceptance")
        if real_execution_unlock_material_reviews["safety"]["allows_real_execution_implementation"]:
            failures.append("runner_real_execution_unlock_material_review: expected implementation locked")
        if real_execution_unlock_material_reviews["safety"]["writes_code"]:
            failures.append("runner_real_execution_unlock_material_review: expected no code writes")
        if real_execution_unlock_material_reviews["safety"]["registers_launch_api"]:
            failures.append("runner_real_execution_unlock_material_review: expected no launch API registration")
        if real_execution_unlock_material_reviews["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_execution_unlock_material_review: expected no adapter call")
        if real_execution_unlock_material_reviews["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_execution_unlock_material_review: expected no stdout/stderr opening")
        if real_execution_unlock_material_reviews["safety"]["writes_runner_events"]:
            failures.append("runner_real_execution_unlock_material_review: expected no runner event writes")
        if real_execution_unlock_material_reviews["safety"]["writes_audit_log"]:
            failures.append("runner_real_execution_unlock_material_review: expected no audit log writes")
        if real_execution_unlock_material_reviews["safety"]["writes_user_project"]:
            failures.append("runner_real_execution_unlock_material_review: expected no user project writes")
        if not real_execution_unlock_material_reviews["safety"]["unlock_material_review_only"]:
            failures.append("runner_real_execution_unlock_material_review: expected review-only safety flag")
        unlock_material_report = real_execution_unlock_material_reviews["reports"][0]
        if unlock_material_report["review_state"]["collects_materials_now"]:
            failures.append("runner_real_execution_unlock_material_review: expected materials not collected")
        if unlock_material_report["review_state"]["stores_materials_now"]:
            failures.append("runner_real_execution_unlock_material_review: expected materials not stored")
        if unlock_material_report["review_state"]["materials_accepted_now"]:
            failures.append("runner_real_execution_unlock_material_review: expected materials not accepted")
        if unlock_material_report["review_state"]["implementation_allowed_now"]:
            failures.append("runner_real_execution_unlock_material_review: expected implementation disabled")
        if real_execution_implementation_plans["status"] != "implementation_plan_required":
            failures.append("runner_real_execution_implementation_plan: expected implementation_plan_required")
        if real_execution_implementation_plans["summary"]["launchable_count"] != 0:
            failures.append("runner_real_execution_implementation_plan: expected launchable_count=0")
        if real_execution_implementation_plans["summary"]["planned_module_count"] < 9:
            failures.append("runner_real_execution_implementation_plan: expected implementation modules")
        if real_execution_implementation_plans["summary"]["ready_module_count"] != 0:
            failures.append("runner_real_execution_implementation_plan: expected no ready modules")
        if real_execution_implementation_plans["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_real_execution_implementation_plan: expected missing evidence")
        if real_execution_implementation_plans["safety"]["executes_commands"]:
            failures.append("runner_real_execution_implementation_plan: expected no command execution")
        if real_execution_implementation_plans["safety"]["creates_process"]:
            failures.append("runner_real_execution_implementation_plan: expected no process creation")
        if real_execution_implementation_plans["safety"]["launch_enabled"]:
            failures.append("runner_real_execution_implementation_plan: expected launch disabled")
        if real_execution_implementation_plans["safety"]["launch_api_available"]:
            failures.append("runner_real_execution_implementation_plan: expected launch API unavailable")
        if real_execution_implementation_plans["safety"]["writes_code"]:
            failures.append("runner_real_execution_implementation_plan: expected no code writes")
        if real_execution_implementation_plans["safety"]["registers_post_api"]:
            failures.append("runner_real_execution_implementation_plan: expected no POST registration")
        if real_execution_implementation_plans["safety"]["registers_launch_api"]:
            failures.append("runner_real_execution_implementation_plan: expected no launch API registration")
        if real_execution_implementation_plans["safety"]["registers_cancel_api"]:
            failures.append("runner_real_execution_implementation_plan: expected no cancel API registration")
        if real_execution_implementation_plans["safety"]["registers_timeout_api"]:
            failures.append("runner_real_execution_implementation_plan: expected no timeout API registration")
        if real_execution_implementation_plans["safety"]["implements_runner"]:
            failures.append("runner_real_execution_implementation_plan: expected no runner implementation")
        if real_execution_implementation_plans["safety"]["imports_adapter"]:
            failures.append("runner_real_execution_implementation_plan: expected no adapter import")
        if real_execution_implementation_plans["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_execution_implementation_plan: expected no adapter call")
        if real_execution_implementation_plans["safety"]["creates_session"]:
            failures.append("runner_real_execution_implementation_plan: expected no session creation")
        if real_execution_implementation_plans["safety"]["stores_session_state"]:
            failures.append("runner_real_execution_implementation_plan: expected no session state storage")
        if real_execution_implementation_plans["safety"]["mutates_session_state"]:
            failures.append("runner_real_execution_implementation_plan: expected no session state mutation")
        if real_execution_implementation_plans["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_execution_implementation_plan: expected no stdout/stderr opening")
        if real_execution_implementation_plans["safety"]["writes_runner_events"]:
            failures.append("runner_real_execution_implementation_plan: expected no runner event writes")
        if real_execution_implementation_plans["safety"]["reads_log_files"]:
            failures.append("runner_real_execution_implementation_plan: expected no log reads")
        if real_execution_implementation_plans["safety"]["writes_logs"]:
            failures.append("runner_real_execution_implementation_plan: expected no log writes")
        if real_execution_implementation_plans["safety"]["writes_audit_log"]:
            failures.append("runner_real_execution_implementation_plan: expected no audit log writes")
        if real_execution_implementation_plans["safety"]["reads_audit_log"]:
            failures.append("runner_real_execution_implementation_plan: expected no audit log reads")
        if real_execution_implementation_plans["safety"]["collects_human_authorization"]:
            failures.append("runner_real_execution_implementation_plan: expected no authorization collection")
        if real_execution_implementation_plans["safety"]["stores_authorization"]:
            failures.append("runner_real_execution_implementation_plan: expected no authorization storage")
        if real_execution_implementation_plans["safety"]["grants_permission"]:
            failures.append("runner_real_execution_implementation_plan: expected no permission grants")
        if real_execution_implementation_plans["safety"]["writes_user_project"]:
            failures.append("runner_real_execution_implementation_plan: expected no user project writes")
        if not real_execution_implementation_plans["safety"]["implementation_plan_only"]:
            failures.append("runner_real_execution_implementation_plan: expected plan-only safety flag")
        implementation_report = real_execution_implementation_plans["reports"][0]
        if implementation_report["plan_state"]["implements_now"]:
            failures.append("runner_real_execution_implementation_plan: expected implementation disabled")
        if implementation_report["plan_state"]["can_launch_now"]:
            failures.append("runner_real_execution_implementation_plan: expected launch disabled in plan state")
        module_keys = {item["key"] for item in implementation_report["implementation_modules"]}
        if "execution_adapter" not in module_keys:
            failures.append("runner_real_execution_implementation_plan: expected execution adapter module")
        if "launch_api" not in module_keys:
            failures.append("runner_real_execution_implementation_plan: expected launch API module")
        if real_execution_scope_diff_audits["status"] != "scope_diff_audit_required":
            failures.append("runner_real_execution_scope_diff_audit: expected scope_diff_audit_required")
        if real_execution_scope_diff_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_real_execution_scope_diff_audit: expected launchable_count=0")
        if real_execution_scope_diff_audits["summary"]["implementation_allowed_count"] != 0:
            failures.append("runner_real_execution_scope_diff_audit: expected no implementation allowed")
        if real_execution_scope_diff_audits["summary"]["scope_item_count"] < 9:
            failures.append("runner_real_execution_scope_diff_audit: expected scope diff items")
        if real_execution_scope_diff_audits["summary"]["locked_scope_item_count"] < 9:
            failures.append("runner_real_execution_scope_diff_audit: expected locked scope items")
        if real_execution_scope_diff_audits["summary"]["allowed_scope_item_count"] != 0:
            failures.append("runner_real_execution_scope_diff_audit: expected no allowed scope items")
        if real_execution_scope_diff_audits["safety"]["executes_commands"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no command execution")
        if real_execution_scope_diff_audits["safety"]["creates_process"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no process creation")
        if real_execution_scope_diff_audits["safety"]["allows_real_execution_implementation"]:
            failures.append("runner_real_execution_scope_diff_audit: expected implementation locked")
        if real_execution_scope_diff_audits["safety"]["writes_code"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no code writes")
        if real_execution_scope_diff_audits["safety"]["enables_launch_ui"]:
            failures.append("runner_real_execution_scope_diff_audit: expected launch UI disabled")
        if real_execution_scope_diff_audits["safety"]["registers_launch_api"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no launch API registration")
        if real_execution_scope_diff_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no adapter call")
        if real_execution_scope_diff_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no stdout/stderr opening")
        if real_execution_scope_diff_audits["safety"]["writes_runner_events"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no runner event writes")
        if real_execution_scope_diff_audits["safety"]["writes_audit_log"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no audit log writes")
        if real_execution_scope_diff_audits["safety"]["writes_user_project"]:
            failures.append("runner_real_execution_scope_diff_audit: expected no user project writes")
        if not real_execution_scope_diff_audits["safety"]["scope_diff_audit_only"]:
            failures.append("runner_real_execution_scope_diff_audit: expected audit-only safety flag")
        scope_diff_report = real_execution_scope_diff_audits["reports"][0]
        if scope_diff_report["audit_state"]["implementation_allowed_now"]:
            failures.append("runner_real_execution_scope_diff_audit: expected implementation disabled")
        if scope_diff_report["audit_state"]["launch_allowed_now"]:
            failures.append("runner_real_execution_scope_diff_audit: expected launch disabled")
        if execution_adapter_implementation_audits["status"] != "adapter_implementation_audit_required":
            failures.append("runner_execution_adapter_implementation_audit: expected adapter_implementation_audit_required")
        if execution_adapter_implementation_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_execution_adapter_implementation_audit: expected launchable_count=0")
        if execution_adapter_implementation_audits["summary"]["audit_item_count"] < 9:
            failures.append("runner_execution_adapter_implementation_audit: expected adapter audit items")
        if execution_adapter_implementation_audits["summary"]["ready_item_count"] != 0:
            failures.append("runner_execution_adapter_implementation_audit: expected no ready audit items")
        if execution_adapter_implementation_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_execution_adapter_implementation_audit: expected missing evidence")
        if execution_adapter_implementation_audits["safety"]["executes_commands"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no command execution")
        if execution_adapter_implementation_audits["safety"]["creates_process"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no process creation")
        if execution_adapter_implementation_audits["safety"]["launch_enabled"]:
            failures.append("runner_execution_adapter_implementation_audit: expected launch disabled")
        if execution_adapter_implementation_audits["safety"]["launch_api_available"]:
            failures.append("runner_execution_adapter_implementation_audit: expected launch API unavailable")
        if execution_adapter_implementation_audits["safety"]["writes_code"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no code writes")
        if execution_adapter_implementation_audits["safety"]["registers_post_api"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no POST registration")
        if execution_adapter_implementation_audits["safety"]["registers_launch_api"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no launch API registration")
        if execution_adapter_implementation_audits["safety"]["registers_cancel_api"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no cancel API registration")
        if execution_adapter_implementation_audits["safety"]["registers_timeout_api"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no timeout API registration")
        if execution_adapter_implementation_audits["safety"]["implements_runner"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no runner implementation")
        if execution_adapter_implementation_audits["safety"]["implements_adapter"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no adapter implementation")
        if execution_adapter_implementation_audits["safety"]["imports_adapter"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no adapter import")
        if execution_adapter_implementation_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no adapter call")
        if execution_adapter_implementation_audits["safety"]["creates_session"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no session creation")
        if execution_adapter_implementation_audits["safety"]["stores_session_state"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no session state storage")
        if execution_adapter_implementation_audits["safety"]["mutates_session_state"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no session state mutation")
        if execution_adapter_implementation_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no stdout/stderr opening")
        if execution_adapter_implementation_audits["safety"]["writes_runner_events"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no runner event writes")
        if execution_adapter_implementation_audits["safety"]["reads_log_files"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no log reads")
        if execution_adapter_implementation_audits["safety"]["writes_logs"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no log writes")
        if execution_adapter_implementation_audits["safety"]["writes_audit_log"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no audit log writes")
        if execution_adapter_implementation_audits["safety"]["reads_audit_log"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no audit log reads")
        if execution_adapter_implementation_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no authorization collection")
        if execution_adapter_implementation_audits["safety"]["stores_authorization"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no authorization storage")
        if execution_adapter_implementation_audits["safety"]["grants_permission"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no permission grants")
        if execution_adapter_implementation_audits["safety"]["writes_user_project"]:
            failures.append("runner_execution_adapter_implementation_audit: expected no user project writes")
        if not execution_adapter_implementation_audits["safety"]["adapter_implementation_audit_only"]:
            failures.append("runner_execution_adapter_implementation_audit: expected audit-only safety flag")
        adapter_audit_report = execution_adapter_implementation_audits["reports"][0]
        if adapter_audit_report["audit_state"]["adapter_implemented_now"]:
            failures.append("runner_execution_adapter_implementation_audit: expected adapter not implemented")
        if adapter_audit_report["audit_state"]["adapter_imported_now"]:
            failures.append("runner_execution_adapter_implementation_audit: expected adapter not imported")
        if adapter_audit_report["audit_state"]["adapter_called_now"]:
            failures.append("runner_execution_adapter_implementation_audit: expected adapter not called")
        audit_keys = {item["key"] for item in adapter_audit_report["audit_items"]}
        if "launch_request_contract" not in audit_keys:
            failures.append("runner_execution_adapter_implementation_audit: expected launch request contract")
        if "fixture_matrix" not in audit_keys:
            failures.append("runner_execution_adapter_implementation_audit: expected fixture matrix")
        if process_lifecycle_implementation_audits["status"] != "process_lifecycle_audit_required":
            failures.append("runner_process_lifecycle_implementation_audit: expected process_lifecycle_audit_required")
        if process_lifecycle_implementation_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_process_lifecycle_implementation_audit: expected launchable_count=0")
        if process_lifecycle_implementation_audits["summary"]["audit_item_count"] < 10:
            failures.append("runner_process_lifecycle_implementation_audit: expected process lifecycle audit items")
        if process_lifecycle_implementation_audits["summary"]["ready_item_count"] != 0:
            failures.append("runner_process_lifecycle_implementation_audit: expected no ready audit items")
        if process_lifecycle_implementation_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_process_lifecycle_implementation_audit: expected missing evidence")
        if process_lifecycle_implementation_audits["safety"]["executes_commands"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no command execution")
        if process_lifecycle_implementation_audits["safety"]["creates_process"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no process creation")
        if process_lifecycle_implementation_audits["safety"]["launch_enabled"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected launch disabled")
        if process_lifecycle_implementation_audits["safety"]["launch_api_available"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected launch API unavailable")
        if process_lifecycle_implementation_audits["safety"]["writes_code"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no code writes")
        if process_lifecycle_implementation_audits["safety"]["registers_post_api"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no POST registration")
        if process_lifecycle_implementation_audits["safety"]["registers_launch_api"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no launch API registration")
        if process_lifecycle_implementation_audits["safety"]["registers_cancel_api"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no cancel API registration")
        if process_lifecycle_implementation_audits["safety"]["registers_timeout_api"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no timeout API registration")
        if process_lifecycle_implementation_audits["safety"]["implements_runner"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no runner implementation")
        if process_lifecycle_implementation_audits["safety"]["implements_adapter"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no adapter implementation")
        if process_lifecycle_implementation_audits["safety"]["imports_adapter"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no adapter import")
        if process_lifecycle_implementation_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no adapter call")
        if process_lifecycle_implementation_audits["safety"]["creates_session"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no session creation")
        if process_lifecycle_implementation_audits["safety"]["stores_session_state"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no session state storage")
        if process_lifecycle_implementation_audits["safety"]["mutates_session_state"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no session state mutation")
        if process_lifecycle_implementation_audits["safety"]["cancels_process"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no process cancellation")
        if process_lifecycle_implementation_audits["safety"]["sends_process_signal"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no process signals")
        if process_lifecycle_implementation_audits["safety"]["kills_process"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no process kill")
        if process_lifecycle_implementation_audits["safety"]["controls_process"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no process control")
        if process_lifecycle_implementation_audits["safety"]["schedules_timeout"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no real timeout scheduling")
        if process_lifecycle_implementation_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no stdout/stderr opening")
        if process_lifecycle_implementation_audits["safety"]["writes_runner_events"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no runner event writes")
        if process_lifecycle_implementation_audits["safety"]["reads_log_files"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no log reads")
        if process_lifecycle_implementation_audits["safety"]["writes_logs"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no log writes")
        if process_lifecycle_implementation_audits["safety"]["writes_audit_log"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no audit log writes")
        if process_lifecycle_implementation_audits["safety"]["reads_audit_log"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no audit log reads")
        if process_lifecycle_implementation_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no authorization collection")
        if process_lifecycle_implementation_audits["safety"]["stores_authorization"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no authorization storage")
        if process_lifecycle_implementation_audits["safety"]["grants_permission"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no permission grants")
        if process_lifecycle_implementation_audits["safety"]["writes_user_project"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected no user project writes")
        if not process_lifecycle_implementation_audits["safety"]["process_lifecycle_audit_only"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected audit-only safety flag")
        process_audit_report = process_lifecycle_implementation_audits["reports"][0]
        if process_audit_report["audit_state"]["process_created_now"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected process not created")
        if process_audit_report["audit_state"]["process_control_enabled_now"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected process control disabled")
        if process_audit_report["audit_state"]["timeout_enabled_now"]:
            failures.append("runner_process_lifecycle_implementation_audit: expected timeout disabled")
        process_audit_keys = {item["key"] for item in process_audit_report["audit_items"]}
        if "spawn_contract" not in process_audit_keys:
            failures.append("runner_process_lifecycle_implementation_audit: expected spawn contract")
        if "terminal_state_contract" not in process_audit_keys:
            failures.append("runner_process_lifecycle_implementation_audit: expected terminal state contract")
        if stream_capture_implementation_audits["status"] != "stream_capture_audit_required":
            failures.append("runner_stream_capture_implementation_audit: expected stream_capture_audit_required")
        if stream_capture_implementation_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_stream_capture_implementation_audit: expected launchable_count=0")
        if stream_capture_implementation_audits["summary"]["audit_item_count"] < 10:
            failures.append("runner_stream_capture_implementation_audit: expected stream capture audit items")
        if stream_capture_implementation_audits["summary"]["ready_item_count"] != 0:
            failures.append("runner_stream_capture_implementation_audit: expected no ready audit items")
        if stream_capture_implementation_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_stream_capture_implementation_audit: expected missing evidence")
        if stream_capture_implementation_audits["summary"]["stream_open_count"] != 0:
            failures.append("runner_stream_capture_implementation_audit: expected no opened streams")
        if stream_capture_implementation_audits["summary"]["log_write_count"] != 0:
            failures.append("runner_stream_capture_implementation_audit: expected no log writes")
        if stream_capture_implementation_audits["safety"]["executes_commands"]:
            failures.append("runner_stream_capture_implementation_audit: expected no command execution")
        if stream_capture_implementation_audits["safety"]["creates_process"]:
            failures.append("runner_stream_capture_implementation_audit: expected no process creation")
        if stream_capture_implementation_audits["safety"]["launch_enabled"]:
            failures.append("runner_stream_capture_implementation_audit: expected launch disabled")
        if stream_capture_implementation_audits["safety"]["launch_api_available"]:
            failures.append("runner_stream_capture_implementation_audit: expected launch API unavailable")
        if stream_capture_implementation_audits["safety"]["writes_code"]:
            failures.append("runner_stream_capture_implementation_audit: expected no code writes")
        if stream_capture_implementation_audits["safety"]["registers_post_api"]:
            failures.append("runner_stream_capture_implementation_audit: expected no POST registration")
        if stream_capture_implementation_audits["safety"]["registers_launch_api"]:
            failures.append("runner_stream_capture_implementation_audit: expected no launch API registration")
        if stream_capture_implementation_audits["safety"]["registers_cancel_api"]:
            failures.append("runner_stream_capture_implementation_audit: expected no cancel API registration")
        if stream_capture_implementation_audits["safety"]["registers_timeout_api"]:
            failures.append("runner_stream_capture_implementation_audit: expected no timeout API registration")
        if stream_capture_implementation_audits["safety"]["imports_adapter"]:
            failures.append("runner_stream_capture_implementation_audit: expected no adapter import")
        if stream_capture_implementation_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_stream_capture_implementation_audit: expected no adapter call")
        if stream_capture_implementation_audits["safety"]["creates_session"]:
            failures.append("runner_stream_capture_implementation_audit: expected no session creation")
        if stream_capture_implementation_audits["safety"]["mutates_session_state"]:
            failures.append("runner_stream_capture_implementation_audit: expected no session state mutation")
        if stream_capture_implementation_audits["safety"]["controls_process"]:
            failures.append("runner_stream_capture_implementation_audit: expected no process control")
        if stream_capture_implementation_audits["safety"]["schedules_timeout"]:
            failures.append("runner_stream_capture_implementation_audit: expected no real timeout scheduling")
        if stream_capture_implementation_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_stream_capture_implementation_audit: expected no stdout/stderr opening")
        if stream_capture_implementation_audits["safety"]["reads_stdout_stderr"]:
            failures.append("runner_stream_capture_implementation_audit: expected no stdout/stderr reads")
        if stream_capture_implementation_audits["safety"]["captures_stdout_stderr"]:
            failures.append("runner_stream_capture_implementation_audit: expected no stdout/stderr capture")
        if stream_capture_implementation_audits["safety"]["writes_runner_events"]:
            failures.append("runner_stream_capture_implementation_audit: expected no runner event writes")
        if stream_capture_implementation_audits["safety"]["reads_log_files"]:
            failures.append("runner_stream_capture_implementation_audit: expected no log reads")
        if stream_capture_implementation_audits["safety"]["writes_logs"]:
            failures.append("runner_stream_capture_implementation_audit: expected no log writes")
        if stream_capture_implementation_audits["safety"]["writes_audit_log"]:
            failures.append("runner_stream_capture_implementation_audit: expected no audit log writes")
        if stream_capture_implementation_audits["safety"]["reads_audit_log"]:
            failures.append("runner_stream_capture_implementation_audit: expected no audit log reads")
        if stream_capture_implementation_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_stream_capture_implementation_audit: expected no authorization collection")
        if stream_capture_implementation_audits["safety"]["stores_authorization"]:
            failures.append("runner_stream_capture_implementation_audit: expected no authorization storage")
        if stream_capture_implementation_audits["safety"]["grants_permission"]:
            failures.append("runner_stream_capture_implementation_audit: expected no permission grants")
        if stream_capture_implementation_audits["safety"]["writes_user_project"]:
            failures.append("runner_stream_capture_implementation_audit: expected no user project writes")
        if not stream_capture_implementation_audits["safety"]["stream_capture_audit_only"]:
            failures.append("runner_stream_capture_implementation_audit: expected audit-only safety flag")
        stream_audit_report = stream_capture_implementation_audits["reports"][0]
        if stream_audit_report["audit_state"]["stdout_opened_now"]:
            failures.append("runner_stream_capture_implementation_audit: expected stdout not opened")
        if stream_audit_report["audit_state"]["stderr_opened_now"]:
            failures.append("runner_stream_capture_implementation_audit: expected stderr not opened")
        if stream_audit_report["audit_state"]["log_written_now"]:
            failures.append("runner_stream_capture_implementation_audit: expected log not written")
        stream_audit_keys = {item["key"] for item in stream_audit_report["audit_items"]}
        if "chunking_contract" not in stream_audit_keys:
            failures.append("runner_stream_capture_implementation_audit: expected chunking contract")
        if "terminal_correlation_contract" not in stream_audit_keys:
            failures.append("runner_stream_capture_implementation_audit: expected terminal correlation contract")
        if event_writer_implementation_audits["status"] != "event_writer_audit_required":
            failures.append("runner_event_writer_implementation_audit: expected event_writer_audit_required")
        if event_writer_implementation_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_event_writer_implementation_audit: expected launchable_count=0")
        if event_writer_implementation_audits["summary"]["audit_item_count"] < 10:
            failures.append("runner_event_writer_implementation_audit: expected event writer audit items")
        if event_writer_implementation_audits["summary"]["ready_item_count"] != 0:
            failures.append("runner_event_writer_implementation_audit: expected no ready audit items")
        if event_writer_implementation_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_event_writer_implementation_audit: expected missing evidence")
        if event_writer_implementation_audits["summary"]["event_write_count"] != 0:
            failures.append("runner_event_writer_implementation_audit: expected no event writes")
        if event_writer_implementation_audits["summary"]["log_write_count"] != 0:
            failures.append("runner_event_writer_implementation_audit: expected no log writes")
        if event_writer_implementation_audits["safety"]["executes_commands"]:
            failures.append("runner_event_writer_implementation_audit: expected no command execution")
        if event_writer_implementation_audits["safety"]["creates_process"]:
            failures.append("runner_event_writer_implementation_audit: expected no process creation")
        if event_writer_implementation_audits["safety"]["launch_enabled"]:
            failures.append("runner_event_writer_implementation_audit: expected launch disabled")
        if event_writer_implementation_audits["safety"]["launch_api_available"]:
            failures.append("runner_event_writer_implementation_audit: expected launch API unavailable")
        if event_writer_implementation_audits["safety"]["writes_code"]:
            failures.append("runner_event_writer_implementation_audit: expected no code writes")
        if event_writer_implementation_audits["safety"]["registers_post_api"]:
            failures.append("runner_event_writer_implementation_audit: expected no POST registration")
        if event_writer_implementation_audits["safety"]["registers_launch_api"]:
            failures.append("runner_event_writer_implementation_audit: expected no launch API registration")
        if event_writer_implementation_audits["safety"]["registers_cancel_api"]:
            failures.append("runner_event_writer_implementation_audit: expected no cancel API registration")
        if event_writer_implementation_audits["safety"]["registers_timeout_api"]:
            failures.append("runner_event_writer_implementation_audit: expected no timeout API registration")
        if event_writer_implementation_audits["safety"]["imports_adapter"]:
            failures.append("runner_event_writer_implementation_audit: expected no adapter import")
        if event_writer_implementation_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_event_writer_implementation_audit: expected no adapter call")
        if event_writer_implementation_audits["safety"]["creates_session"]:
            failures.append("runner_event_writer_implementation_audit: expected no session creation")
        if event_writer_implementation_audits["safety"]["mutates_session_state"]:
            failures.append("runner_event_writer_implementation_audit: expected no session state mutation")
        if event_writer_implementation_audits["safety"]["controls_process"]:
            failures.append("runner_event_writer_implementation_audit: expected no process control")
        if event_writer_implementation_audits["safety"]["schedules_timeout"]:
            failures.append("runner_event_writer_implementation_audit: expected no real timeout scheduling")
        if event_writer_implementation_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_event_writer_implementation_audit: expected no stdout/stderr opening")
        if event_writer_implementation_audits["safety"]["reads_stdout_stderr"]:
            failures.append("runner_event_writer_implementation_audit: expected no stdout/stderr reads")
        if event_writer_implementation_audits["safety"]["captures_stdout_stderr"]:
            failures.append("runner_event_writer_implementation_audit: expected no stdout/stderr capture")
        if event_writer_implementation_audits["safety"]["writes_runner_events"]:
            failures.append("runner_event_writer_implementation_audit: expected no runner event writes")
        if event_writer_implementation_audits["safety"]["opens_runner_event_log"]:
            failures.append("runner_event_writer_implementation_audit: expected no event log open")
        if event_writer_implementation_audits["safety"]["writes_event_log"]:
            failures.append("runner_event_writer_implementation_audit: expected no event log writes")
        if event_writer_implementation_audits["safety"]["reads_log_files"]:
            failures.append("runner_event_writer_implementation_audit: expected no log reads")
        if event_writer_implementation_audits["safety"]["writes_logs"]:
            failures.append("runner_event_writer_implementation_audit: expected no log writes")
        if event_writer_implementation_audits["safety"]["writes_audit_log"]:
            failures.append("runner_event_writer_implementation_audit: expected no audit log writes")
        if event_writer_implementation_audits["safety"]["reads_audit_log"]:
            failures.append("runner_event_writer_implementation_audit: expected no audit log reads")
        if event_writer_implementation_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_event_writer_implementation_audit: expected no authorization collection")
        if event_writer_implementation_audits["safety"]["stores_authorization"]:
            failures.append("runner_event_writer_implementation_audit: expected no authorization storage")
        if event_writer_implementation_audits["safety"]["grants_permission"]:
            failures.append("runner_event_writer_implementation_audit: expected no permission grants")
        if event_writer_implementation_audits["safety"]["writes_user_project"]:
            failures.append("runner_event_writer_implementation_audit: expected no user project writes")
        if not event_writer_implementation_audits["safety"]["event_writer_audit_only"]:
            failures.append("runner_event_writer_implementation_audit: expected audit-only safety flag")
        event_audit_report = event_writer_implementation_audits["reports"][0]
        if event_audit_report["audit_state"]["event_written_now"]:
            failures.append("runner_event_writer_implementation_audit: expected event not written")
        if event_audit_report["audit_state"]["event_log_opened_now"]:
            failures.append("runner_event_writer_implementation_audit: expected event log not opened")
        if event_audit_report["audit_state"]["event_persisted_now"]:
            failures.append("runner_event_writer_implementation_audit: expected event not persisted")
        if event_audit_report["audit_state"]["log_written_now"]:
            failures.append("runner_event_writer_implementation_audit: expected log not written")
        event_audit_keys = {item["key"] for item in event_audit_report["audit_items"]}
        if "event_schema_contract" not in event_audit_keys:
            failures.append("runner_event_writer_implementation_audit: expected event schema contract")
        if "terminal_event_contract" not in event_audit_keys:
            failures.append("runner_event_writer_implementation_audit: expected terminal event contract")
        if "write_failure_contract" not in event_audit_keys:
            failures.append("runner_event_writer_implementation_audit: expected write failure contract")
        if audit_persistence_implementation_audits["status"] != "audit_persistence_audit_required":
            failures.append("runner_audit_persistence_implementation_audit: expected audit_persistence_audit_required")
        if audit_persistence_implementation_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_audit_persistence_implementation_audit: expected launchable_count=0")
        if audit_persistence_implementation_audits["summary"]["audit_item_count"] < 10:
            failures.append("runner_audit_persistence_implementation_audit: expected audit persistence items")
        if audit_persistence_implementation_audits["summary"]["ready_item_count"] != 0:
            failures.append("runner_audit_persistence_implementation_audit: expected no ready audit items")
        if audit_persistence_implementation_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_audit_persistence_implementation_audit: expected missing evidence")
        if audit_persistence_implementation_audits["summary"]["audit_record_count"] != 0:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit records")
        if audit_persistence_implementation_audits["summary"]["audit_write_count"] != 0:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit writes")
        if audit_persistence_implementation_audits["summary"]["audit_read_count"] != 0:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit reads")
        if audit_persistence_implementation_audits["safety"]["executes_commands"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no command execution")
        if audit_persistence_implementation_audits["safety"]["creates_process"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no process creation")
        if audit_persistence_implementation_audits["safety"]["launch_enabled"]:
            failures.append("runner_audit_persistence_implementation_audit: expected launch disabled")
        if audit_persistence_implementation_audits["safety"]["launch_api_available"]:
            failures.append("runner_audit_persistence_implementation_audit: expected launch API unavailable")
        if audit_persistence_implementation_audits["safety"]["writes_code"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no code writes")
        if audit_persistence_implementation_audits["safety"]["registers_post_api"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no POST registration")
        if audit_persistence_implementation_audits["safety"]["registers_launch_api"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no launch API registration")
        if audit_persistence_implementation_audits["safety"]["registers_cancel_api"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no cancel API registration")
        if audit_persistence_implementation_audits["safety"]["registers_timeout_api"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no timeout API registration")
        if audit_persistence_implementation_audits["safety"]["imports_adapter"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no adapter import")
        if audit_persistence_implementation_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no adapter call")
        if audit_persistence_implementation_audits["safety"]["creates_session"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no session creation")
        if audit_persistence_implementation_audits["safety"]["mutates_session_state"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no session state mutation")
        if audit_persistence_implementation_audits["safety"]["controls_process"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no process control")
        if audit_persistence_implementation_audits["safety"]["schedules_timeout"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no real timeout scheduling")
        if audit_persistence_implementation_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no stdout/stderr opening")
        if audit_persistence_implementation_audits["safety"]["reads_stdout_stderr"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no stdout/stderr reads")
        if audit_persistence_implementation_audits["safety"]["captures_stdout_stderr"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no stdout/stderr capture")
        if audit_persistence_implementation_audits["safety"]["writes_runner_events"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no runner event writes")
        if audit_persistence_implementation_audits["safety"]["opens_runner_event_log"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no event log open")
        if audit_persistence_implementation_audits["safety"]["writes_event_log"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no event log writes")
        if audit_persistence_implementation_audits["safety"]["opens_audit_log"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit log open")
        if audit_persistence_implementation_audits["safety"]["reads_audit_log"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit log reads")
        if audit_persistence_implementation_audits["safety"]["writes_audit_log"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit log writes")
        if audit_persistence_implementation_audits["safety"]["stores_audit_records"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit record storage")
        if audit_persistence_implementation_audits["safety"]["reads_audit_records"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no audit record reads")
        if audit_persistence_implementation_audits["safety"]["reads_log_files"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no log reads")
        if audit_persistence_implementation_audits["safety"]["writes_logs"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no log writes")
        if audit_persistence_implementation_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no authorization collection")
        if audit_persistence_implementation_audits["safety"]["stores_authorization"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no authorization storage")
        if audit_persistence_implementation_audits["safety"]["grants_permission"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no permission grants")
        if audit_persistence_implementation_audits["safety"]["writes_user_project"]:
            failures.append("runner_audit_persistence_implementation_audit: expected no user project writes")
        if not audit_persistence_implementation_audits["safety"]["audit_persistence_audit_only"]:
            failures.append("runner_audit_persistence_implementation_audit: expected audit-only safety flag")
        audit_persistence_report = audit_persistence_implementation_audits["reports"][0]
        if audit_persistence_report["audit_state"]["audit_record_written_now"]:
            failures.append("runner_audit_persistence_implementation_audit: expected audit record not written")
        if audit_persistence_report["audit_state"]["audit_log_opened_now"]:
            failures.append("runner_audit_persistence_implementation_audit: expected audit log not opened")
        if audit_persistence_report["audit_state"]["audit_record_persisted_now"]:
            failures.append("runner_audit_persistence_implementation_audit: expected audit record not persisted")
        if audit_persistence_report["audit_state"]["audit_record_read_now"]:
            failures.append("runner_audit_persistence_implementation_audit: expected audit record not read")
        audit_persistence_keys = {item["key"] for item in audit_persistence_report["audit_items"]}
        if "authorization_evidence_contract" not in audit_persistence_keys:
            failures.append("runner_audit_persistence_implementation_audit: expected authorization evidence contract")
        if "event_chain_summary_contract" not in audit_persistence_keys:
            failures.append("runner_audit_persistence_implementation_audit: expected event chain summary contract")
        if "audit_record_schema_contract" not in audit_persistence_keys:
            failures.append("runner_audit_persistence_implementation_audit: expected audit record schema contract")
        if integrity_replay_verification_audits["status"] != "integrity_replay_audit_required":
            failures.append("runner_audit_integrity_replay_verification_audit: expected integrity_replay_audit_required")
        if integrity_replay_verification_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_audit_integrity_replay_verification_audit: expected launchable_count=0")
        if integrity_replay_verification_audits["summary"]["audit_item_count"] < 10:
            failures.append("runner_audit_integrity_replay_verification_audit: expected integrity replay audit items")
        if integrity_replay_verification_audits["summary"]["ready_item_count"] != 0:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no ready audit items")
        if integrity_replay_verification_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_audit_integrity_replay_verification_audit: expected missing evidence")
        if integrity_replay_verification_audits["summary"]["integrity_check_count"] != 0:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no integrity checks")
        if integrity_replay_verification_audits["summary"]["replay_check_count"] != 0:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no replay checks")
        if integrity_replay_verification_audits["summary"]["consistency_check_count"] != 0:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no consistency checks")
        if integrity_replay_verification_audits["safety"]["executes_commands"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no command execution")
        if integrity_replay_verification_audits["safety"]["creates_process"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no process creation")
        if integrity_replay_verification_audits["safety"]["launch_enabled"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected launch disabled")
        if integrity_replay_verification_audits["safety"]["launch_api_available"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected launch API unavailable")
        if integrity_replay_verification_audits["safety"]["writes_code"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no code writes")
        if integrity_replay_verification_audits["safety"]["registers_post_api"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no POST registration")
        if integrity_replay_verification_audits["safety"]["registers_launch_api"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no launch API registration")
        if integrity_replay_verification_audits["safety"]["registers_cancel_api"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no cancel API registration")
        if integrity_replay_verification_audits["safety"]["registers_timeout_api"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no timeout API registration")
        if integrity_replay_verification_audits["safety"]["imports_adapter"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no adapter import")
        if integrity_replay_verification_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no adapter call")
        if integrity_replay_verification_audits["safety"]["creates_session"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no session creation")
        if integrity_replay_verification_audits["safety"]["mutates_session_state"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no session state mutation")
        if integrity_replay_verification_audits["safety"]["controls_process"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no process control")
        if integrity_replay_verification_audits["safety"]["schedules_timeout"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no real timeout scheduling")
        if integrity_replay_verification_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no stdout/stderr opening")
        if integrity_replay_verification_audits["safety"]["reads_stdout_stderr"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no stdout/stderr reads")
        if integrity_replay_verification_audits["safety"]["captures_stdout_stderr"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no stdout/stderr capture")
        if integrity_replay_verification_audits["safety"]["reads_runner_events"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no runner event reads")
        if integrity_replay_verification_audits["safety"]["writes_runner_events"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no runner event writes")
        if integrity_replay_verification_audits["safety"]["opens_runner_event_log"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no event log open")
        if integrity_replay_verification_audits["safety"]["writes_event_log"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no event log writes")
        if integrity_replay_verification_audits["safety"]["opens_audit_log"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no audit log open")
        if integrity_replay_verification_audits["safety"]["reads_audit_log"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no audit log reads")
        if integrity_replay_verification_audits["safety"]["writes_audit_log"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no audit log writes")
        if integrity_replay_verification_audits["safety"]["stores_audit_records"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no audit record storage")
        if integrity_replay_verification_audits["safety"]["reads_audit_records"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no audit record reads")
        if integrity_replay_verification_audits["safety"]["reads_config_snapshots"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no config snapshot reads")
        if integrity_replay_verification_audits["safety"]["performs_integrity_checks"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no integrity checks")
        if integrity_replay_verification_audits["safety"]["performs_replay_checks"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no replay checks")
        if integrity_replay_verification_audits["safety"]["performs_consistency_checks"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no consistency checks")
        if integrity_replay_verification_audits["safety"]["reads_log_files"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no log reads")
        if integrity_replay_verification_audits["safety"]["writes_logs"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no log writes")
        if integrity_replay_verification_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no authorization collection")
        if integrity_replay_verification_audits["safety"]["stores_authorization"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no authorization storage")
        if integrity_replay_verification_audits["safety"]["grants_permission"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no permission grants")
        if integrity_replay_verification_audits["safety"]["writes_user_project"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected no user project writes")
        if not integrity_replay_verification_audits["safety"]["integrity_replay_audit_only"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected audit-only safety flag")
        integrity_replay_report = integrity_replay_verification_audits["reports"][0]
        if integrity_replay_report["audit_state"]["audit_log_opened_now"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected audit log not opened")
        if integrity_replay_report["audit_state"]["audit_record_read_now"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected audit record not read")
        if integrity_replay_report["audit_state"]["runner_event_read_now"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected runner event not read")
        if integrity_replay_report["audit_state"]["config_snapshot_read_now"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected config snapshot not read")
        if integrity_replay_report["audit_state"]["integrity_checked_now"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected integrity not checked")
        if integrity_replay_report["audit_state"]["replay_checked_now"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected replay not checked")
        if integrity_replay_report["audit_state"]["consistency_checked_now"]:
            failures.append("runner_audit_integrity_replay_verification_audit: expected consistency not checked")
        integrity_replay_keys = {item["key"] for item in integrity_replay_report["audit_items"]}
        if "audit_record_reference_contract" not in integrity_replay_keys:
            failures.append("runner_audit_integrity_replay_verification_audit: expected audit record reference contract")
        if "event_replay_contract" not in integrity_replay_keys:
            failures.append("runner_audit_integrity_replay_verification_audit: expected event replay contract")
        if "integrity_hash_contract" not in integrity_replay_keys:
            failures.append("runner_audit_integrity_replay_verification_audit: expected integrity hash contract")
        if verification_discrepancy_report_audits["status"] != "discrepancy_report_audit_required":
            failures.append("runner_verification_discrepancy_report_audit: expected discrepancy_report_audit_required")
        if verification_discrepancy_report_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_verification_discrepancy_report_audit: expected launchable_count=0")
        if verification_discrepancy_report_audits["summary"]["audit_item_count"] < 10:
            failures.append("runner_verification_discrepancy_report_audit: expected discrepancy report audit items")
        if verification_discrepancy_report_audits["summary"]["ready_item_count"] != 0:
            failures.append("runner_verification_discrepancy_report_audit: expected no ready audit items")
        if verification_discrepancy_report_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_verification_discrepancy_report_audit: expected missing evidence")
        if verification_discrepancy_report_audits["summary"]["discrepancy_report_count"] != 0:
            failures.append("runner_verification_discrepancy_report_audit: expected no discrepancy reports")
        if verification_discrepancy_report_audits["summary"]["blocking_decision_count"] != 0:
            failures.append("runner_verification_discrepancy_report_audit: expected no blocking decisions")
        if verification_discrepancy_report_audits["summary"]["operator_message_count"] != 0:
            failures.append("runner_verification_discrepancy_report_audit: expected no operator messages")
        if verification_discrepancy_report_audits["safety"]["executes_commands"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no command execution")
        if verification_discrepancy_report_audits["safety"]["creates_process"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no process creation")
        if verification_discrepancy_report_audits["safety"]["launch_enabled"]:
            failures.append("runner_verification_discrepancy_report_audit: expected launch disabled")
        if verification_discrepancy_report_audits["safety"]["launch_api_available"]:
            failures.append("runner_verification_discrepancy_report_audit: expected launch API unavailable")
        if verification_discrepancy_report_audits["safety"]["writes_code"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no code writes")
        if verification_discrepancy_report_audits["safety"]["registers_post_api"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no POST registration")
        if verification_discrepancy_report_audits["safety"]["registers_launch_api"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no launch API registration")
        if verification_discrepancy_report_audits["safety"]["registers_cancel_api"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no cancel API registration")
        if verification_discrepancy_report_audits["safety"]["registers_timeout_api"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no timeout API registration")
        if verification_discrepancy_report_audits["safety"]["imports_adapter"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no adapter import")
        if verification_discrepancy_report_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no adapter call")
        if verification_discrepancy_report_audits["safety"]["creates_session"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no session creation")
        if verification_discrepancy_report_audits["safety"]["mutates_session_state"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no session state mutation")
        if verification_discrepancy_report_audits["safety"]["controls_process"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no process control")
        if verification_discrepancy_report_audits["safety"]["schedules_timeout"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no real timeout scheduling")
        if verification_discrepancy_report_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no stdout/stderr opening")
        if verification_discrepancy_report_audits["safety"]["reads_stdout_stderr"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no stdout/stderr reads")
        if verification_discrepancy_report_audits["safety"]["captures_stdout_stderr"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no stdout/stderr capture")
        if verification_discrepancy_report_audits["safety"]["reads_runner_events"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no runner event reads")
        if verification_discrepancy_report_audits["safety"]["writes_runner_events"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no runner event writes")
        if verification_discrepancy_report_audits["safety"]["opens_runner_event_log"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no event log open")
        if verification_discrepancy_report_audits["safety"]["writes_event_log"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no event log writes")
        if verification_discrepancy_report_audits["safety"]["opens_audit_log"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no audit log open")
        if verification_discrepancy_report_audits["safety"]["reads_audit_log"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no audit log reads")
        if verification_discrepancy_report_audits["safety"]["writes_audit_log"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no audit log writes")
        if verification_discrepancy_report_audits["safety"]["stores_audit_records"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no audit record storage")
        if verification_discrepancy_report_audits["safety"]["reads_audit_records"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no audit record reads")
        if verification_discrepancy_report_audits["safety"]["reads_config_snapshots"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no config snapshot reads")
        if verification_discrepancy_report_audits["safety"]["performs_integrity_checks"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no integrity checks")
        if verification_discrepancy_report_audits["safety"]["performs_replay_checks"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no replay checks")
        if verification_discrepancy_report_audits["safety"]["performs_consistency_checks"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no consistency checks")
        if verification_discrepancy_report_audits["safety"]["generates_discrepancy_reports"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no discrepancy reports")
        if verification_discrepancy_report_audits["safety"]["makes_blocking_decisions"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no blocking decisions")
        if verification_discrepancy_report_audits["safety"]["generates_operator_messages"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no operator messages")
        if verification_discrepancy_report_audits["safety"]["reads_log_files"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no log reads")
        if verification_discrepancy_report_audits["safety"]["writes_logs"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no log writes")
        if verification_discrepancy_report_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no authorization collection")
        if verification_discrepancy_report_audits["safety"]["stores_authorization"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no authorization storage")
        if verification_discrepancy_report_audits["safety"]["grants_permission"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no permission grants")
        if verification_discrepancy_report_audits["safety"]["writes_user_project"]:
            failures.append("runner_verification_discrepancy_report_audit: expected no user project writes")
        if not verification_discrepancy_report_audits["safety"]["discrepancy_report_audit_only"]:
            failures.append("runner_verification_discrepancy_report_audit: expected audit-only safety flag")
        discrepancy_report = verification_discrepancy_report_audits["reports"][0]
        if discrepancy_report["audit_state"]["discrepancy_report_generated_now"]:
            failures.append("runner_verification_discrepancy_report_audit: expected discrepancy report not generated")
        if discrepancy_report["audit_state"]["blocking_decision_made_now"]:
            failures.append("runner_verification_discrepancy_report_audit: expected blocking decision not made")
        if discrepancy_report["audit_state"]["operator_message_generated_now"]:
            failures.append("runner_verification_discrepancy_report_audit: expected operator message not generated")
        if discrepancy_report["audit_state"]["audit_record_read_now"]:
            failures.append("runner_verification_discrepancy_report_audit: expected audit record not read")
        if discrepancy_report["audit_state"]["runner_event_read_now"]:
            failures.append("runner_verification_discrepancy_report_audit: expected runner event not read")
        if discrepancy_report["audit_state"]["verification_executed_now"]:
            failures.append("runner_verification_discrepancy_report_audit: expected verification not executed")
        discrepancy_keys = {item["key"] for item in discrepancy_report["audit_items"]}
        if "discrepancy_taxonomy_contract" not in discrepancy_keys:
            failures.append("runner_verification_discrepancy_report_audit: expected discrepancy taxonomy contract")
        if "blocking_decision_contract" not in discrepancy_keys:
            failures.append("runner_verification_discrepancy_report_audit: expected blocking decision contract")
        if "operator_message_contract" not in discrepancy_keys:
            failures.append("runner_verification_discrepancy_report_audit: expected operator message contract")
        if real_launch_final_gate_audits["status"] != "final_launch_gate_audit_required":
            failures.append("runner_real_launch_final_gate_audit: expected final gate audit required")
        if real_launch_final_gate_audits["summary"]["launchable_count"] != 0:
            failures.append("runner_real_launch_final_gate_audit: expected launchable_count=0")
        if real_launch_final_gate_audits["summary"]["audit_item_count"] < 10:
            failures.append("runner_real_launch_final_gate_audit: expected final gate audit items")
        if real_launch_final_gate_audits["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_real_launch_final_gate_audit: expected missing evidence")
        if real_launch_final_gate_audits["summary"]["pre_launch_blocker_count"] < 1:
            failures.append("runner_real_launch_final_gate_audit: expected pre-launch blockers")
        if real_launch_final_gate_audits["summary"]["final_gate_decision_count"] != 0:
            failures.append("runner_real_launch_final_gate_audit: expected no real final gate decisions")
        if real_launch_final_gate_audits["summary"]["registered_endpoint_count"] != 0:
            failures.append("runner_real_launch_final_gate_audit: expected no registered endpoints")
        if real_launch_final_gate_audits["safety"]["executes_commands"]:
            failures.append("runner_real_launch_final_gate_audit: expected no command execution")
        if real_launch_final_gate_audits["safety"]["creates_process"]:
            failures.append("runner_real_launch_final_gate_audit: expected no process creation")
        if real_launch_final_gate_audits["safety"]["launch_enabled"]:
            failures.append("runner_real_launch_final_gate_audit: expected launch disabled")
        if real_launch_final_gate_audits["safety"]["launch_api_available"]:
            failures.append("runner_real_launch_final_gate_audit: expected launch API unavailable")
        if real_launch_final_gate_audits["safety"]["registers_post_api"]:
            failures.append("runner_real_launch_final_gate_audit: expected no POST registration")
        if real_launch_final_gate_audits["safety"]["registers_launch_api"]:
            failures.append("runner_real_launch_final_gate_audit: expected no launch API registration")
        if real_launch_final_gate_audits["safety"]["enables_launch_ui"]:
            failures.append("runner_real_launch_final_gate_audit: expected launch UI disabled")
        if real_launch_final_gate_audits["safety"]["imports_adapter"]:
            failures.append("runner_real_launch_final_gate_audit: expected no adapter import")
        if real_launch_final_gate_audits["safety"]["calls_execution_adapter"]:
            failures.append("runner_real_launch_final_gate_audit: expected no adapter call")
        if real_launch_final_gate_audits["safety"]["creates_session"]:
            failures.append("runner_real_launch_final_gate_audit: expected no session creation")
        if real_launch_final_gate_audits["safety"]["mutates_session_state"]:
            failures.append("runner_real_launch_final_gate_audit: expected no session mutation")
        if real_launch_final_gate_audits["safety"]["opens_stdout_stderr"]:
            failures.append("runner_real_launch_final_gate_audit: expected no stdout/stderr opening")
        if real_launch_final_gate_audits["safety"]["reads_runner_events"]:
            failures.append("runner_real_launch_final_gate_audit: expected no runner event reads")
        if real_launch_final_gate_audits["safety"]["writes_runner_events"]:
            failures.append("runner_real_launch_final_gate_audit: expected no runner event writes")
        if real_launch_final_gate_audits["safety"]["opens_audit_log"]:
            failures.append("runner_real_launch_final_gate_audit: expected no audit log open")
        if real_launch_final_gate_audits["safety"]["reads_audit_log"]:
            failures.append("runner_real_launch_final_gate_audit: expected no audit log reads")
        if real_launch_final_gate_audits["safety"]["writes_audit_log"]:
            failures.append("runner_real_launch_final_gate_audit: expected no audit log writes")
        if real_launch_final_gate_audits["safety"]["reads_audit_records"]:
            failures.append("runner_real_launch_final_gate_audit: expected no audit record reads")
        if real_launch_final_gate_audits["safety"]["reads_config_snapshots"]:
            failures.append("runner_real_launch_final_gate_audit: expected no config snapshot reads")
        if real_launch_final_gate_audits["safety"]["performs_integrity_checks"]:
            failures.append("runner_real_launch_final_gate_audit: expected no integrity checks")
        if real_launch_final_gate_audits["safety"]["performs_replay_checks"]:
            failures.append("runner_real_launch_final_gate_audit: expected no replay checks")
        if real_launch_final_gate_audits["safety"]["generates_discrepancy_reports"]:
            failures.append("runner_real_launch_final_gate_audit: expected no discrepancy report generation")
        if real_launch_final_gate_audits["safety"]["makes_launch_decisions"]:
            failures.append("runner_real_launch_final_gate_audit: expected no launch decisions")
        if real_launch_final_gate_audits["safety"]["reads_log_files"]:
            failures.append("runner_real_launch_final_gate_audit: expected no log reads")
        if real_launch_final_gate_audits["safety"]["writes_logs"]:
            failures.append("runner_real_launch_final_gate_audit: expected no log writes")
        if real_launch_final_gate_audits["safety"]["collects_human_authorization"]:
            failures.append("runner_real_launch_final_gate_audit: expected no authorization collection")
        if real_launch_final_gate_audits["safety"]["stores_authorization"]:
            failures.append("runner_real_launch_final_gate_audit: expected no authorization storage")
        if real_launch_final_gate_audits["safety"]["grants_permission"]:
            failures.append("runner_real_launch_final_gate_audit: expected no permission grants")
        if real_launch_final_gate_audits["safety"]["writes_user_project"]:
            failures.append("runner_real_launch_final_gate_audit: expected no user project writes")
        if not real_launch_final_gate_audits["safety"]["final_launch_gate_audit_only"]:
            failures.append("runner_real_launch_final_gate_audit: expected audit-only safety flag")
        final_gate_report = real_launch_final_gate_audits["reports"][0]
        if final_gate_report["audit_state"]["real_launch_allowed_now"]:
            failures.append("runner_real_launch_final_gate_audit: expected real launch not allowed")
        if final_gate_report["audit_state"]["real_launch_api_registered_now"]:
            failures.append("runner_real_launch_final_gate_audit: expected launch API not registered")
        if final_gate_report["audit_state"]["adapter_called_now"]:
            failures.append("runner_real_launch_final_gate_audit: expected adapter not called")
        if final_gate_report["audit_state"]["process_created_now"]:
            failures.append("runner_real_launch_final_gate_audit: expected process not created")
        if final_gate_report["audit_state"]["runner_event_read_now"]:
            failures.append("runner_real_launch_final_gate_audit: expected runner event not read")
        if final_gate_report["audit_state"]["audit_log_read_now"]:
            failures.append("runner_real_launch_final_gate_audit: expected audit log not read")
        if final_gate_report["audit_state"]["authorization_collected_now"]:
            failures.append("runner_real_launch_final_gate_audit: expected authorization not collected")
        final_gate_keys = {item["key"] for item in final_gate_report["audit_items"]}
        if "pre_launch_gate_contract" not in final_gate_keys:
            failures.append("runner_real_launch_final_gate_audit: expected pre-launch gate contract")
        if "safety_invariant_matrix" not in final_gate_keys:
            failures.append("runner_real_launch_final_gate_audit: expected safety invariant matrix")
        if "launch_api_absence_contract" not in final_gate_keys:
            failures.append("runner_real_launch_final_gate_audit: expected launch API absence contract")
        if evidence_gap_indexes["status"] != "evidence_index_required":
            failures.append("runner_evidence_gap_index: expected evidence index required")
        if evidence_gap_indexes["summary"]["launchable_count"] != 0:
            failures.append("runner_evidence_gap_index: expected launchable_count=0")
        if evidence_gap_indexes["summary"]["index_entry_count"] < 1:
            failures.append("runner_evidence_gap_index: expected index entries")
        if evidence_gap_indexes["summary"]["navigation_target_count"] < 1:
            failures.append("runner_evidence_gap_index: expected navigation targets")
        if evidence_gap_indexes["summary"]["missing_evidence_count"] < 1:
            failures.append("runner_evidence_gap_index: expected missing evidence entries")
        if evidence_gap_indexes["summary"]["pre_launch_blocker_count"] < 1:
            failures.append("runner_evidence_gap_index: expected pre-launch blocker entries")
        if evidence_gap_indexes["summary"]["registered_endpoint_count"] != 0:
            failures.append("runner_evidence_gap_index: expected no registered endpoints")
        if evidence_gap_indexes["safety"]["executes_commands"]:
            failures.append("runner_evidence_gap_index: expected no command execution")
        if evidence_gap_indexes["safety"]["creates_process"]:
            failures.append("runner_evidence_gap_index: expected no process creation")
        if evidence_gap_indexes["safety"]["launch_enabled"]:
            failures.append("runner_evidence_gap_index: expected launch disabled")
        if evidence_gap_indexes["safety"]["launch_api_available"]:
            failures.append("runner_evidence_gap_index: expected launch API unavailable")
        if evidence_gap_indexes["safety"]["registers_post_api"]:
            failures.append("runner_evidence_gap_index: expected no POST registration")
        if evidence_gap_indexes["safety"]["registers_launch_api"]:
            failures.append("runner_evidence_gap_index: expected no launch API registration")
        if evidence_gap_indexes["safety"]["enables_launch_ui"]:
            failures.append("runner_evidence_gap_index: expected launch UI disabled")
        if evidence_gap_indexes["safety"]["imports_adapter"]:
            failures.append("runner_evidence_gap_index: expected no adapter import")
        if evidence_gap_indexes["safety"]["calls_execution_adapter"]:
            failures.append("runner_evidence_gap_index: expected no adapter call")
        if evidence_gap_indexes["safety"]["creates_session"]:
            failures.append("runner_evidence_gap_index: expected no session creation")
        if evidence_gap_indexes["safety"]["mutates_session_state"]:
            failures.append("runner_evidence_gap_index: expected no session mutation")
        if evidence_gap_indexes["safety"]["opens_stdout_stderr"]:
            failures.append("runner_evidence_gap_index: expected no stdout/stderr opening")
        if evidence_gap_indexes["safety"]["reads_runner_events"]:
            failures.append("runner_evidence_gap_index: expected no runner event reads")
        if evidence_gap_indexes["safety"]["writes_runner_events"]:
            failures.append("runner_evidence_gap_index: expected no runner event writes")
        if evidence_gap_indexes["safety"]["reads_audit_log"]:
            failures.append("runner_evidence_gap_index: expected no audit log reads")
        if evidence_gap_indexes["safety"]["writes_audit_log"]:
            failures.append("runner_evidence_gap_index: expected no audit log writes")
        if evidence_gap_indexes["safety"]["reads_audit_records"]:
            failures.append("runner_evidence_gap_index: expected no audit record reads")
        if evidence_gap_indexes["safety"]["reads_config_snapshots"]:
            failures.append("runner_evidence_gap_index: expected no config snapshot reads")
        if evidence_gap_indexes["safety"]["performs_integrity_checks"]:
            failures.append("runner_evidence_gap_index: expected no integrity checks")
        if evidence_gap_indexes["safety"]["performs_replay_checks"]:
            failures.append("runner_evidence_gap_index: expected no replay checks")
        if evidence_gap_indexes["safety"]["generates_discrepancy_reports"]:
            failures.append("runner_evidence_gap_index: expected no discrepancy reports")
        if evidence_gap_indexes["safety"]["makes_launch_decisions"]:
            failures.append("runner_evidence_gap_index: expected no launch decisions")
        if evidence_gap_indexes["safety"]["scans_log_directory"]:
            failures.append("runner_evidence_gap_index: expected no log directory scans")
        if evidence_gap_indexes["safety"]["reads_log_files"]:
            failures.append("runner_evidence_gap_index: expected no log reads")
        if evidence_gap_indexes["safety"]["writes_logs"]:
            failures.append("runner_evidence_gap_index: expected no log writes")
        if evidence_gap_indexes["safety"]["collects_human_authorization"]:
            failures.append("runner_evidence_gap_index: expected no authorization collection")
        if evidence_gap_indexes["safety"]["stores_authorization"]:
            failures.append("runner_evidence_gap_index: expected no authorization storage")
        if evidence_gap_indexes["safety"]["grants_permission"]:
            failures.append("runner_evidence_gap_index: expected no permission grants")
        if evidence_gap_indexes["safety"]["writes_user_project"]:
            failures.append("runner_evidence_gap_index: expected no user project writes")
        if not evidence_gap_indexes["safety"]["evidence_gap_index_only"]:
            failures.append("runner_evidence_gap_index: expected index-only safety flag")
        evidence_index_report = evidence_gap_indexes["reports"][0]
        if evidence_index_report["index_state"]["log_file_read_now"]:
            failures.append("runner_evidence_gap_index: expected no log file read")
        if evidence_index_report["index_state"]["runner_event_read_now"]:
            failures.append("runner_evidence_gap_index: expected no runner event read")
        if evidence_index_report["index_state"]["audit_log_read_now"]:
            failures.append("runner_evidence_gap_index: expected no audit log read")
        if evidence_index_report["index_state"]["config_snapshot_read_now"]:
            failures.append("runner_evidence_gap_index: expected no config snapshot read")
        if evidence_index_report["index_state"]["launch_api_registered_now"]:
            failures.append("runner_evidence_gap_index: expected no launch API registration")
        if evidence_index_report["index_state"]["process_created_now"]:
            failures.append("runner_evidence_gap_index: expected no process creation state")
        if evidence_index_report["index_state"]["adapter_called_now"]:
            failures.append("runner_evidence_gap_index: expected no adapter call state")
        index_kinds = {item["kind"] for item in evidence_index_report["index_entries"]}
        if "missing_evidence" not in index_kinds:
            failures.append("runner_evidence_gap_index: expected missing evidence entry")
        if "pre_launch_blocker" not in index_kinds:
            failures.append("runner_evidence_gap_index: expected pre-launch blocker entry")
        if "required_layer" not in index_kinds:
            failures.append("runner_evidence_gap_index: expected required layer entry")
        indexed_required_layers = {
            item["key"] for item in evidence_index_report["index_entries"] if item.get("kind") == "required_layer"
        }
        if "real_execution_stage_boundary_review" not in indexed_required_layers:
            failures.append("runner_evidence_gap_index: expected stage boundary review required layer")
        if "real_execution_unlock_material_review" not in indexed_required_layers:
            failures.append("runner_evidence_gap_index: expected unlock material review required layer")
        if "real_execution_scope_diff_audit" not in indexed_required_layers:
            failures.append("runner_evidence_gap_index: expected scope diff audit required layer")
        return {
            "saved_count_after_save": annotated["summary"]["saved_count"],
            "profile_saved_flag": bool(saved_profile.get("saved")),
            "saved_count_after_remove": removed["summary"]["saved_count"],
            "preflight_status_after_save": preflight["status"],
            "preflight_status_after_remove": removed_preflight["status"],
            "confirmation_after_confirm": confirmed_preflight["reports"][0]["confirmation"]["status"],
            "confirmation_after_revoke": revoked_preflight["reports"][0]["confirmation"]["status"],
            "execution_gate_after_preflight_confirm": execution_gate["status"],
            "final_confirmation_after_confirm": confirmed_execution_gate["reports"][0]["final_confirmation"]["status"],
            "final_confirmation_after_revoke": revoked_execution_gate["reports"][0]["final_confirmation"]["status"],
            "runner_plan_after_final_confirm": runner_plan["status"],
            "execution_request_after_prepare": prepared_execution_requests["reports"][0]["request"]["status"],
            "execution_request_after_second_confirm": second_confirmed_execution_requests["reports"][0]["request"]["status"],
            "execution_request_after_revoke": revoked_execution_requests["reports"][0]["request"]["status"],
            "execution_request_after_remove": removed_execution_requests["reports"][0]["request"]["status"],
            "runner_session_after_prepare": drafted_runner_sessions["reports"][0]["session"]["status"],
            "runner_session_after_request_revoke": stale_runner_sessions["reports"][0]["session"]["status"],
            "runner_session_after_remove": removed_runner_sessions["reports"][0]["session"]["status"],
            "runner_launch_snapshot_after_prepare": snapshotted_launch_snapshots["reports"][0]["snapshot"]["status"],
            "runner_launch_snapshot_after_session_remove": stale_launch_snapshots["reports"][0]["snapshot"]["status"],
            "runner_launch_snapshot_after_remove": removed_launch_snapshots["reports"][0]["snapshot"]["status"],
            "runner_dry_run_after_prepare": prepared_dry_runs["reports"][0]["dry_run"]["status"],
            "runner_dry_run_after_snapshot_remove": stale_dry_runs["reports"][0]["dry_run"]["status"],
            "runner_dry_run_after_remove": removed_dry_runs["reports"][0]["dry_run"]["status"],
            "runner_launch_control_status": launch_controls["status"],
            "runner_launch_control_launchable_count": launch_controls["summary"]["launchable_count"],
            "runner_runtime_policy_status": runtime_policies["status"],
            "runner_runtime_policy_launchable_count": runtime_policies["summary"]["launchable_count"],
            "runner_execution_config_status": execution_configs["status"],
            "runner_execution_config_launchable_count": execution_configs["summary"]["launchable_count"],
            "runner_execution_config_check_missing_status": missing_config_checks["status"],
            "runner_execution_config_check_invalid_json_status": invalid_json_config_checks["status"],
            "runner_execution_config_check_bad_config_status": bad_config_checks["status"],
            "runner_execution_config_check_present_status": present_config_checks["status"],
            "runner_execution_config_check_launchable_count": present_config_checks["summary"]["launchable_count"],
            "runner_config_schema_stabilization_status": config_schema_stabilizations["status"],
            "runner_config_schema_stabilization_launchable_count": (
                config_schema_stabilizations["summary"]["launchable_count"]
            ),
            "runner_config_schema_stabilization_field_contract_count": (
                config_schema_stabilizations["summary"]["field_contract_count"]
            ),
            "runner_config_schema_stabilization_error_code_count": (
                config_schema_stabilizations["summary"]["error_code_count"]
            ),
            "runner_config_field_contract_view_status": config_field_contract_views["status"],
            "runner_config_field_contract_view_field_contract_count": (
                config_field_contract_views["summary"]["field_contract_count"]
            ),
            "runner_config_field_contract_view_error_code_count": (
                config_field_contract_views["summary"]["error_code_count"]
            ),
            "runner_config_field_contract_view_launchable_count": (
                config_field_contract_views["summary"]["launchable_count"]
            ),
            "runner_config_compatibility_report_status": config_compatibility_reports["status"],
            "runner_config_compatibility_report_launchable_count": (
                config_compatibility_reports["summary"]["launchable_count"]
            ),
            "runner_config_compatibility_report_issue_count": (
                config_compatibility_reports["summary"]["compatibility_issue_count"]
            ),
            "runner_config_compatibility_report_missing_field_count": (
                config_compatibility_reports["summary"]["missing_field_count"]
            ),
            "runner_config_bad_config_compatibility_status": bad_config_compatibility_reports["status"],
            "runner_config_bad_config_issue_count": (
                bad_config_compatibility_reports["summary"]["compatibility_issue_count"]
            ),
            "runner_config_compatibility_report_issue_navigation_target_count": (
                config_compatibility_reports["summary"].get("issue_navigation_target_count", 0)
            ),
            "runner_config_remediation_summary_status": config_remediation_summaries["status"],
            "runner_config_remediation_summary_recommendation_count": (
                config_remediation_summaries["summary"]["recommendation_count"]
            ),
            "runner_config_remediation_summary_launchable_count": (
                config_remediation_summaries["summary"]["launchable_count"]
            ),
            "runner_config_field_coverage_index_status": config_field_coverage_indexes["status"],
            "runner_config_field_coverage_index_field_count": (
                config_field_coverage_indexes["summary"]["field_count"]
            ),
            "runner_config_field_coverage_index_indexed_issue_count": (
                config_field_coverage_indexes["summary"]["indexed_issue_count"]
            ),
            "runner_config_field_coverage_index_launchable_count": (
                config_field_coverage_indexes["summary"]["launchable_count"]
            ),
            "runner_service_flag_audit_status": service_flag_audits["status"],
            "runner_service_flag_audit_launchable_count": service_flag_audits["summary"]["launchable_count"],
            "runner_log_directory_policy_status": log_directory_policies["status"],
            "runner_log_directory_policy_launchable_count": log_directory_policies["summary"]["launchable_count"],
            "runner_log_retention_policy_status": log_retention_policies["status"],
            "runner_log_retention_policy_launchable_count": log_retention_policies["summary"]["launchable_count"],
            "runner_log_cleanup_preview_status": log_cleanup_previews["status"],
            "runner_log_cleanup_preview_launchable_count": log_cleanup_previews["summary"]["launchable_count"],
            "runner_log_cleanup_confirmation_status": log_cleanup_confirmations["status"],
            "runner_log_cleanup_confirmation_launchable_count": log_cleanup_confirmations["summary"]["launchable_count"],
            "runner_log_cleanup_audit_trail_status": log_cleanup_audit_trails["status"],
            "runner_log_cleanup_audit_trail_launchable_count": log_cleanup_audit_trails["summary"]["launchable_count"],
            "runner_log_cleanup_execution_plan_status": log_cleanup_execution_plans["status"],
            "runner_log_cleanup_execution_plan_launchable_count": log_cleanup_execution_plans["summary"]["launchable_count"],
            "runner_log_cleanup_execution_plan_operation_count": log_cleanup_execution_plans["summary"]["planned_operation_count"],
            "runner_governance_readiness_status": governance_readiness["status"],
            "runner_governance_readiness_launchable_count": governance_readiness["summary"]["launchable_count"],
            "runner_governance_readiness_layer_count": governance_readiness["summary"]["layer_count"],
            "runner_execution_adapter_contract_status": execution_adapter_contracts["status"],
            "runner_execution_adapter_contract_launchable_count": execution_adapter_contracts["summary"]["launchable_count"],
            "runner_launch_api_contract_status": launch_api_contracts["status"],
            "runner_launch_api_contract_launchable_count": launch_api_contracts["summary"]["launchable_count"],
            "runner_launch_api_contract_registered_endpoint_count": launch_api_contracts["summary"]["registered_endpoint_count"],
            "runner_execution_adapter_review_status": execution_adapter_reviews["status"],
            "runner_execution_adapter_review_launchable_count": execution_adapter_reviews["summary"]["launchable_count"],
            "runner_execution_adapter_review_implemented_adapter_count": execution_adapter_reviews["summary"]["implemented_adapter_count"],
            "runner_final_block_matrix_status": final_block_matrices["status"],
            "runner_final_block_matrix_launchable_count": final_block_matrices["summary"]["launchable_count"],
            "runner_final_block_matrix_blocking_reason_count": final_block_matrices["summary"]["blocking_reason_count"],
            "runner_authorization_unlock_audit_status": authorization_unlock_audits["status"],
            "runner_authorization_unlock_audit_launchable_count": authorization_unlock_audits["summary"]["launchable_count"],
            "runner_authorization_unlock_audit_missing_evidence_count": authorization_unlock_audits["summary"]["missing_evidence_count"],
            "runner_implementation_gap_checklist_status": implementation_gap_checklists["status"],
            "runner_implementation_gap_checklist_launchable_count": implementation_gap_checklists["summary"]["launchable_count"],
            "runner_implementation_gap_checklist_gap_count": implementation_gap_checklists["summary"]["gap_count"],
            "runner_cancel_timeout_contract_status": cancel_timeout_contracts["status"],
            "runner_cancel_timeout_contract_launchable_count": cancel_timeout_contracts["summary"]["launchable_count"],
            "runner_cancel_timeout_contract_registered_endpoint_count": cancel_timeout_contracts["summary"]["registered_endpoint_count"],
            "runner_cancel_timeout_real_api_status": cancel_timeout_real_apis["status"],
            "runner_cancel_timeout_real_api_registered_endpoint_count": (
                cancel_timeout_real_apis["summary"]["registered_endpoint_count"]
            ),
            "runner_cancel_timeout_real_api_active_process_count": (
                cancel_timeout_real_apis["summary"]["active_process_count"]
            ),
            "runner_first_real_test_before_status": first_real_tests_before_launch["status"],
            "runner_first_real_test_after_status": first_real_tests_after_launch["status"],
            "runner_first_real_test_after_execution_count": (
                first_real_tests_after_launch["summary"]["execution_count"]
            ),
            "runner_first_real_test_after_completed_count": (
                first_real_tests_after_launch["summary"]["first_real_test_completed_count"]
            ),
            "runner_first_real_test_latest_exit_code": first_execution["exit_code"],
            "runner_session_state_schema_status": session_state_schemas["status"],
            "runner_session_state_schema_launchable_count": session_state_schemas["summary"]["launchable_count"],
            "runner_session_state_schema_persisted_session_count": session_state_schemas["summary"]["persisted_session_count"],
            "runner_session_state_schema_active_session_count": session_state_schemas["summary"]["active_session_count"],
            "runner_real_test_readiness_status": real_test_readiness["status"],
            "runner_real_test_readiness_launchable_count": real_test_readiness["summary"]["launchable_count"],
            "runner_real_test_readiness_startable_count": real_test_readiness["summary"]["can_start_real_test_count"],
            "runner_real_test_readiness_missing_gate_count": real_test_readiness["summary"]["missing_gate_count"],
            "runner_real_test_authorization_checklist_status": real_test_authorization_checklists["status"],
            "runner_real_test_authorization_checklist_launchable_count": real_test_authorization_checklists["summary"]["launchable_count"],
            "runner_real_test_authorization_checklist_authorized_count": real_test_authorization_checklists["summary"]["collected_authorization_count"],
            "runner_real_test_authorization_checklist_permission_granted_count": real_test_authorization_checklists["summary"]["permission_granted_count"],
            "runner_real_test_authorization_checklist_missing_evidence_count": real_test_authorization_checklists["summary"]["missing_evidence_count"],
            "runner_real_test_authorization_package_status": real_test_authorization_packages["status"],
            "runner_real_test_authorization_package_launchable_count": real_test_authorization_packages["summary"]["launchable_count"],
            "runner_real_test_authorization_package_collected_count": real_test_authorization_packages["summary"]["collected_authorization_count"],
            "runner_real_test_authorization_package_stored_count": real_test_authorization_packages["summary"]["stored_authorization_count"],
            "runner_real_test_authorization_package_permission_granted_count": real_test_authorization_packages["summary"]["permission_granted_count"],
            "runner_real_test_authorization_package_risk_acknowledgement_count": real_test_authorization_packages["summary"]["risk_acknowledgement_count"],
            "runner_real_test_authorization_package_missing_evidence_count": real_test_authorization_packages["summary"]["missing_evidence_count"],
            "runner_real_test_sandbox_policy_status": real_test_sandbox_policies["status"],
            "runner_real_test_sandbox_policy_launchable_count": real_test_sandbox_policies["summary"]["launchable_count"],
            "runner_real_test_sandbox_policy_workspace_rule_count": real_test_sandbox_policies["summary"]["workspace_rule_count"],
            "runner_real_test_sandbox_policy_environment_rule_count": real_test_sandbox_policies["summary"]["environment_rule_count"],
            "runner_real_test_sandbox_policy_timeout_rule_count": real_test_sandbox_policies["summary"]["timeout_rule_count"],
            "runner_real_test_sandbox_policy_log_rule_count": real_test_sandbox_policies["summary"]["log_rule_count"],
            "runner_real_test_sandbox_policy_permission_rule_count": real_test_sandbox_policies["summary"]["permission_rule_count"],
            "runner_real_test_final_checklist_status": real_test_final_checklists["status"],
            "runner_real_test_final_checklist_launchable_count": real_test_final_checklists["summary"]["launchable_count"],
            "runner_real_test_final_checklist_item_count": real_test_final_checklists["summary"]["check_item_count"],
            "runner_real_test_final_checklist_missing_evidence_count": real_test_final_checklists["summary"]["missing_evidence_count"],
            "runner_real_test_final_checklist_passed_item_count": real_test_final_checklists["summary"]["passed_item_count"],
            "runner_real_test_ui_preview_status": real_test_ui_previews["status"],
            "runner_real_test_ui_preview_launchable_count": real_test_ui_previews["summary"]["launchable_count"],
            "runner_real_test_ui_preview_item_count": real_test_ui_previews["summary"]["preview_item_count"],
            "runner_real_test_ui_preview_disabled_control_count": real_test_ui_previews["summary"]["disabled_control_count"],
            "runner_real_test_ui_preview_missing_evidence_count": real_test_ui_previews["summary"]["missing_evidence_count"],
            "runner_real_execution_stage_boundary_review_status": real_execution_stage_boundary_reviews["status"],
            "runner_real_execution_stage_boundary_review_launchable_count": real_execution_stage_boundary_reviews["summary"]["launchable_count"],
            "runner_real_execution_stage_boundary_review_allowed_count": real_execution_stage_boundary_reviews["summary"]["implementation_allowed_count"],
            "runner_real_execution_stage_boundary_review_missing_unlock_count": real_execution_stage_boundary_reviews["summary"]["missing_unlock_count"],
            "runner_real_execution_unlock_material_review_status": real_execution_unlock_material_reviews["status"],
            "runner_real_execution_unlock_material_review_launchable_count": real_execution_unlock_material_reviews["summary"]["launchable_count"],
            "runner_real_execution_unlock_material_review_allowed_count": real_execution_unlock_material_reviews["summary"]["implementation_allowed_count"],
            "runner_real_execution_unlock_material_review_missing_material_count": real_execution_unlock_material_reviews["summary"]["missing_material_count"],
            "runner_real_execution_implementation_plan_status": real_execution_implementation_plans["status"],
            "runner_real_execution_implementation_plan_launchable_count": real_execution_implementation_plans["summary"]["launchable_count"],
            "runner_real_execution_implementation_plan_module_count": real_execution_implementation_plans["summary"]["planned_module_count"],
            "runner_real_execution_implementation_plan_missing_evidence_count": real_execution_implementation_plans["summary"]["missing_evidence_count"],
            "runner_real_execution_scope_diff_audit_status": real_execution_scope_diff_audits["status"],
            "runner_real_execution_scope_diff_audit_launchable_count": real_execution_scope_diff_audits["summary"]["launchable_count"],
            "runner_real_execution_scope_diff_audit_item_count": real_execution_scope_diff_audits["summary"]["scope_item_count"],
            "runner_real_execution_scope_diff_audit_locked_item_count": real_execution_scope_diff_audits["summary"]["locked_scope_item_count"],
            "runner_real_execution_scope_diff_audit_allowed_item_count": real_execution_scope_diff_audits["summary"]["allowed_scope_item_count"],
            "runner_execution_adapter_implementation_audit_status": execution_adapter_implementation_audits["status"],
            "runner_execution_adapter_implementation_audit_launchable_count": execution_adapter_implementation_audits["summary"]["launchable_count"],
            "runner_execution_adapter_implementation_audit_item_count": execution_adapter_implementation_audits["summary"]["audit_item_count"],
            "runner_execution_adapter_implementation_audit_missing_evidence_count": execution_adapter_implementation_audits["summary"]["missing_evidence_count"],
            "runner_process_lifecycle_implementation_audit_status": process_lifecycle_implementation_audits["status"],
            "runner_process_lifecycle_implementation_audit_launchable_count": process_lifecycle_implementation_audits["summary"]["launchable_count"],
            "runner_process_lifecycle_implementation_audit_item_count": process_lifecycle_implementation_audits["summary"]["audit_item_count"],
            "runner_process_lifecycle_implementation_audit_missing_evidence_count": process_lifecycle_implementation_audits["summary"]["missing_evidence_count"],
            "runner_stream_capture_implementation_audit_status": stream_capture_implementation_audits["status"],
            "runner_stream_capture_implementation_audit_launchable_count": stream_capture_implementation_audits["summary"]["launchable_count"],
            "runner_stream_capture_implementation_audit_item_count": stream_capture_implementation_audits["summary"]["audit_item_count"],
            "runner_stream_capture_implementation_audit_missing_evidence_count": stream_capture_implementation_audits["summary"]["missing_evidence_count"],
            "runner_event_writer_implementation_audit_status": event_writer_implementation_audits["status"],
            "runner_event_writer_implementation_audit_launchable_count": event_writer_implementation_audits["summary"]["launchable_count"],
            "runner_event_writer_implementation_audit_item_count": event_writer_implementation_audits["summary"]["audit_item_count"],
            "runner_event_writer_implementation_audit_missing_evidence_count": event_writer_implementation_audits["summary"]["missing_evidence_count"],
            "runner_audit_persistence_implementation_audit_status": audit_persistence_implementation_audits["status"],
            "runner_audit_persistence_implementation_audit_launchable_count": audit_persistence_implementation_audits["summary"]["launchable_count"],
            "runner_audit_persistence_implementation_audit_item_count": audit_persistence_implementation_audits["summary"]["audit_item_count"],
            "runner_audit_persistence_implementation_audit_missing_evidence_count": audit_persistence_implementation_audits["summary"]["missing_evidence_count"],
            "runner_audit_integrity_replay_verification_audit_status": integrity_replay_verification_audits["status"],
            "runner_audit_integrity_replay_verification_audit_launchable_count": integrity_replay_verification_audits["summary"]["launchable_count"],
            "runner_audit_integrity_replay_verification_audit_item_count": integrity_replay_verification_audits["summary"]["audit_item_count"],
            "runner_audit_integrity_replay_verification_audit_missing_evidence_count": integrity_replay_verification_audits["summary"]["missing_evidence_count"],
            "runner_verification_discrepancy_report_audit_status": verification_discrepancy_report_audits["status"],
            "runner_verification_discrepancy_report_audit_launchable_count": verification_discrepancy_report_audits["summary"]["launchable_count"],
            "runner_verification_discrepancy_report_audit_item_count": verification_discrepancy_report_audits["summary"]["audit_item_count"],
            "runner_verification_discrepancy_report_audit_missing_evidence_count": verification_discrepancy_report_audits["summary"]["missing_evidence_count"],
            "runner_real_launch_final_gate_audit_status": real_launch_final_gate_audits["status"],
            "runner_real_launch_final_gate_audit_launchable_count": real_launch_final_gate_audits["summary"]["launchable_count"],
            "runner_real_launch_final_gate_audit_item_count": real_launch_final_gate_audits["summary"]["audit_item_count"],
            "runner_real_launch_final_gate_audit_pre_launch_blocker_count": real_launch_final_gate_audits["summary"]["pre_launch_blocker_count"],
            "runner_real_launch_final_gate_audit_missing_evidence_count": real_launch_final_gate_audits["summary"]["missing_evidence_count"],
            "runner_evidence_gap_index_status": evidence_gap_indexes["status"],
            "runner_evidence_gap_index_launchable_count": evidence_gap_indexes["summary"]["launchable_count"],
            "runner_evidence_gap_index_entry_count": evidence_gap_indexes["summary"]["index_entry_count"],
            "runner_evidence_gap_index_required_layer_count": evidence_gap_indexes["summary"]["required_layer_count"],
            "runner_evidence_gap_index_navigation_target_count": evidence_gap_indexes["summary"]["navigation_target_count"],
            "runner_evidence_gap_index_unresolved_gap_count": evidence_gap_indexes["summary"]["unresolved_gap_count"],
            "failures": failures,
        }


def _sample_failures(result: dict[str, object], expected: dict[str, int]) -> list[str]:
    failures = []
    sample = result["sample"]
    if int(result["runs"]) < 1:
        failures.append(f"{sample}: expected at least one run")
    if int(result["events"]) < expected["min_events"]:
        failures.append(f"{sample}: expected at least {expected['min_events']} events")
    if int(result["known"]) != expected["known"]:
        failures.append(f"{sample}: expected {expected['known']} known methods, got {result['known']}")
    if int(result["covered"]) != int(result["known"]):
        failures.append(f"{sample}: expected full coverage, got {result['covered']}/{result['known']}")
    if result["runtime_only"]:
        failures.append(f"{sample}: expected no runtime-only methods")
    if result["status"] not in {"ready", "partial", "risky"}:
        failures.append(f"{sample}: unexpected readiness status {result['status']}")
    if int(result["findings"]) < 1:
        failures.append(f"{sample}: expected audit findings")
    if int(result["findings_with_location"]) != int(result["findings"]):
        failures.append(f"{sample}: expected every audit finding to include location data")
    if result["audit_status"] not in {"pass", "warn", "fail", "blocked"}:
        failures.append(f"{sample}: unexpected audit status {result['audit_status']}")
    if result["integration_plan_status"] not in {"ready", "partial", "risky", "no_runs", "not_connected", "blocked", "unknown"}:
        failures.append(f"{sample}: unexpected integration plan status {result['integration_plan_status']}")
    if int(result["integration_plan_phases"]) < 5:
        failures.append(f"{sample}: expected integration plan phases")
    if int(result["integration_plan_targets"]) < 1:
        failures.append(f"{sample}: expected integration plan execution targets")
    if int(result["integration_plan_gates"]) < 5:
        failures.append(f"{sample}: expected integration plan validation gates")
    if not result["integration_next_action"]:
        failures.append(f"{sample}: expected integration plan next action")
    if int(result["run_profile_count"]) < 1:
        failures.append(f"{sample}: expected run profile drafts")
    if not result["run_profile_safe"]:
        failures.append(f"{sample}: expected inert run profiles requiring confirmation")
    if result["run_preflight_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving run profiles")
    if not result["run_preflight_safe"]:
        failures.append(f"{sample}: expected inert run preflight requiring confirmation")
    if result["run_execution_gate_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving execution gate profiles")
    if not result["run_execution_gate_safe"]:
        failures.append(f"{sample}: expected inert final execution gate")
    if result["runner_plan_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner plan profiles")
    if not result["runner_plan_safe"]:
        failures.append(f"{sample}: expected inert runner plan")
    if result["execution_request_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving execution requests")
    if not result["execution_request_safe"]:
        failures.append(f"{sample}: expected inert execution requests")
    if result["runner_session_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner sessions")
    if not result["runner_session_safe"]:
        failures.append(f"{sample}: expected inert runner sessions")
    if result["runner_launch_snapshot_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner launch snapshots")
    if not result["runner_launch_snapshot_safe"]:
        failures.append(f"{sample}: expected inert runner launch snapshots")
    if result["runner_dry_run_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner dry-runs")
    if not result["runner_dry_run_safe"]:
        failures.append(f"{sample}: expected inert runner dry-runs")
    if result["runner_launch_control_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner launch controls")
    if not result["runner_launch_control_safe"]:
        failures.append(f"{sample}: expected inert runner launch controls")
    if result["runner_runtime_policy_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner runtime policies")
    if not result["runner_runtime_policy_safe"]:
        failures.append(f"{sample}: expected inert runner runtime policies")
    if result["runner_execution_config_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner execution configs")
    if not result["runner_execution_config_safe"]:
        failures.append(f"{sample}: expected inert runner execution configs")
    if result["runner_execution_config_check_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner execution config checks")
    if not result["runner_execution_config_check_safe"]:
        failures.append(f"{sample}: expected inert runner execution config checks")
    if result["runner_config_schema_stabilization_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner config schema stabilizations")
    if not result["runner_config_schema_stabilization_safe"]:
        failures.append(f"{sample}: expected inert runner config schema stabilizations")
    if result["runner_config_field_contract_view_status"] != "contract_view_ready":
        failures.append(f"{sample}: expected ready runner config field contract view")
    if not result["runner_config_field_contract_view_safe"]:
        failures.append(f"{sample}: expected inert runner config field contract view")
    if result["runner_config_compatibility_report_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner config compatibility reports")
    if not result["runner_config_compatibility_report_safe"]:
        failures.append(f"{sample}: expected inert runner config compatibility reports")
    if result["runner_config_remediation_summary_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner config remediation summaries")
    if not result["runner_config_remediation_summary_safe"]:
        failures.append(f"{sample}: expected inert runner config remediation summaries")
    if result["runner_config_field_coverage_index_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner config field coverage indexes")
    if not result["runner_config_field_coverage_index_safe"]:
        failures.append(f"{sample}: expected inert runner config field coverage indexes")
    if result["runner_service_flag_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner service flag audits")
    if not result["runner_service_flag_audit_safe"]:
        failures.append(f"{sample}: expected inert runner service flag audits")
    if result["runner_log_directory_policy_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner log directory policies")
    if not result["runner_log_directory_policy_safe"]:
        failures.append(f"{sample}: expected inert runner log directory policies")
    if result["runner_log_retention_policy_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner log retention policies")
    if not result["runner_log_retention_policy_safe"]:
        failures.append(f"{sample}: expected inert runner log retention policies")
    if result["runner_log_cleanup_preview_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner log cleanup previews")
    if not result["runner_log_cleanup_preview_safe"]:
        failures.append(f"{sample}: expected inert runner log cleanup previews")
    if result["runner_log_cleanup_confirmation_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner log cleanup confirmations")
    if not result["runner_log_cleanup_confirmation_safe"]:
        failures.append(f"{sample}: expected inert runner log cleanup confirmations")
    if result["runner_log_cleanup_audit_trail_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner log cleanup audit trails")
    if not result["runner_log_cleanup_audit_trail_safe"]:
        failures.append(f"{sample}: expected inert runner log cleanup audit trails")
    if result["runner_log_cleanup_execution_plan_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner log cleanup execution plans")
    if not result["runner_log_cleanup_execution_plan_safe"]:
        failures.append(f"{sample}: expected inert runner log cleanup execution plans")
    if result["runner_governance_readiness_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner governance readiness")
    if not result["runner_governance_readiness_safe"]:
        failures.append(f"{sample}: expected inert runner governance readiness")
    if result["runner_execution_adapter_contract_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner execution adapter contracts")
    if not result["runner_execution_adapter_contract_safe"]:
        failures.append(f"{sample}: expected inert runner execution adapter contracts")
    if result["runner_launch_api_contract_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner launch API contracts")
    if not result["runner_launch_api_contract_safe"]:
        failures.append(f"{sample}: expected inert runner launch API contracts")
    if result["runner_execution_adapter_review_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner execution adapter reviews")
    if not result["runner_execution_adapter_review_safe"]:
        failures.append(f"{sample}: expected inert runner execution adapter reviews")
    if result["runner_final_block_matrix_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner final block matrices")
    if not result["runner_final_block_matrix_safe"]:
        failures.append(f"{sample}: expected inert runner final block matrices")
    if result["runner_authorization_unlock_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner authorization unlock audits")
    if not result["runner_authorization_unlock_audit_safe"]:
        failures.append(f"{sample}: expected inert runner authorization unlock audits")
    if result["runner_implementation_gap_checklist_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner implementation gap checklists")
    if not result["runner_implementation_gap_checklist_safe"]:
        failures.append(f"{sample}: expected inert runner implementation gap checklists")
    if result["runner_cancel_timeout_contract_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner cancel timeout contracts")
    if not result["runner_cancel_timeout_contract_safe"]:
        failures.append(f"{sample}: expected inert runner cancel timeout contracts")
    if result["runner_cancel_timeout_real_api_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner cancel timeout real APIs")
    if int(result["runner_cancel_timeout_real_api_registered_endpoint_count"]) != 0:
        failures.append(f"{sample}: expected no registered cancel timeout real API endpoints before saving profiles")
    if int(result["runner_cancel_timeout_real_api_active_process_count"]) != 0:
        failures.append(f"{sample}: expected no active cancel timeout controlled processes before saving profiles")
    if int(result["runner_cancel_timeout_real_api_cancelled_count"]) != 0:
        failures.append(f"{sample}: expected no cancelled executions before saving profiles")
    if int(result["runner_cancel_timeout_real_api_timed_out_count"]) != 0:
        failures.append(f"{sample}: expected no timed-out executions before saving profiles")
    if not result["runner_cancel_timeout_real_api_safe"]:
        failures.append(f"{sample}: expected safe runner cancel timeout real APIs")
    if result["runner_first_real_test_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner first real tests")
    if int(result["runner_first_real_test_execution_count"]) != 0:
        failures.append(f"{sample}: expected no first real test executions before saving profiles")
    if int(result["runner_first_real_test_completed_count"]) != 0:
        failures.append(f"{sample}: expected no completed first real tests before saving profiles")
    if int(result["runner_first_real_test_failed_count"]) != 0:
        failures.append(f"{sample}: expected no failed first real tests before saving profiles")
    if not result["runner_first_real_test_safe"]:
        failures.append(f"{sample}: expected safe runner first real test reports")
    if result["runner_session_state_schema_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner session state schemas")
    if not result["runner_session_state_schema_safe"]:
        failures.append(f"{sample}: expected inert runner session state schemas")
    if result["runner_real_test_readiness_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real-test readiness")
    if not result["runner_real_test_readiness_safe"]:
        failures.append(f"{sample}: expected inert runner real-test readiness")
    if result["runner_real_test_authorization_checklist_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real-test authorization checklists")
    if not result["runner_real_test_authorization_checklist_safe"]:
        failures.append(f"{sample}: expected inert runner real-test authorization checklists")
    if result["runner_real_test_authorization_package_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real-test authorization packages")
    if not result["runner_real_test_authorization_package_safe"]:
        failures.append(f"{sample}: expected inert runner real-test authorization packages")
    if result["runner_real_test_sandbox_policy_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real-test sandbox policies")
    if not result["runner_real_test_sandbox_policy_safe"]:
        failures.append(f"{sample}: expected inert runner real-test sandbox policies")
    if result["runner_real_test_final_checklist_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real-test final checklists")
    if not result["runner_real_test_final_checklist_safe"]:
        failures.append(f"{sample}: expected inert runner real-test final checklists")
    if result["runner_real_test_ui_preview_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real-test UI previews")
    if not result["runner_real_test_ui_preview_safe"]:
        failures.append(f"{sample}: expected inert runner real-test UI previews")
    if result["runner_real_execution_stage_boundary_review_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real execution stage boundary reviews")
    if not result["runner_real_execution_stage_boundary_review_safe"]:
        failures.append(f"{sample}: expected inert runner real execution stage boundary reviews")
    if result["runner_real_execution_unlock_material_review_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real execution unlock material reviews")
    if not result["runner_real_execution_unlock_material_review_safe"]:
        failures.append(f"{sample}: expected inert runner real execution unlock material reviews")
    if result["runner_real_execution_implementation_plan_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real execution implementation plans")
    if not result["runner_real_execution_implementation_plan_safe"]:
        failures.append(f"{sample}: expected inert runner real execution implementation plans")
    if result["runner_real_execution_scope_diff_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real execution scope diff audits")
    if not result["runner_real_execution_scope_diff_audit_safe"]:
        failures.append(f"{sample}: expected inert runner real execution scope diff audits")
    if result["runner_execution_adapter_implementation_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner execution adapter implementation audits")
    if not result["runner_execution_adapter_implementation_audit_safe"]:
        failures.append(f"{sample}: expected inert runner execution adapter implementation audits")
    if result["runner_process_lifecycle_implementation_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner process lifecycle implementation audits")
    if not result["runner_process_lifecycle_implementation_audit_safe"]:
        failures.append(f"{sample}: expected inert runner process lifecycle implementation audits")
    if result["runner_stream_capture_implementation_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner stream capture implementation audits")
    if not result["runner_stream_capture_implementation_audit_safe"]:
        failures.append(f"{sample}: expected inert runner stream capture implementation audits")
    if result["runner_event_writer_implementation_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner event writer implementation audits")
    if not result["runner_event_writer_implementation_audit_safe"]:
        failures.append(f"{sample}: expected inert runner event writer implementation audits")
    if result["runner_audit_persistence_implementation_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner audit persistence implementation audits")
    if not result["runner_audit_persistence_implementation_audit_safe"]:
        failures.append(f"{sample}: expected inert runner audit persistence implementation audits")
    if result["runner_audit_persistence_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner audit persistences")
    if int(result["runner_audit_persistence_audit_record_count"]) != 0:
        failures.append(f"{sample}: expected no projected audit records before saving profiles")
    if not result["runner_audit_persistence_safe"]:
        failures.append(f"{sample}: expected inert runner audit persistence projections")
    if result["runner_audit_integrity_replay_verification_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner audit integrity replay verification audits")
    if not result["runner_audit_integrity_replay_verification_audit_safe"]:
        failures.append(f"{sample}: expected inert runner audit integrity replay verification audits")
    if result["runner_audit_integrity_replay_verification_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner audit integrity replay verifications")
    if int(result["runner_audit_integrity_replay_verification_integrity_check_count"]) != 0:
        failures.append(f"{sample}: expected no projected integrity checks before saving profiles")
    if int(result["runner_audit_integrity_replay_verification_replay_check_count"]) != 0:
        failures.append(f"{sample}: expected no projected replay checks before saving profiles")
    if int(result["runner_audit_integrity_replay_verification_consistency_check_count"]) != 0:
        failures.append(f"{sample}: expected no projected consistency checks before saving profiles")
    if not result["runner_audit_integrity_replay_verification_safe"]:
        failures.append(f"{sample}: expected inert runner audit integrity replay projections")
    if result["runner_verification_discrepancy_report_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner verification discrepancy report audits")
    if not result["runner_verification_discrepancy_report_audit_safe"]:
        failures.append(f"{sample}: expected inert runner verification discrepancy report audits")
    if result["runner_verification_discrepancy_report_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner verification discrepancy reports")
    if int(result["runner_verification_discrepancy_report_count"]) != 0:
        failures.append(f"{sample}: expected no projected discrepancy reports before saving profiles")
    if int(result["runner_verification_discrepancy_report_blocking_decision_count"]) != 0:
        failures.append(f"{sample}: expected no projected blocking decisions before saving profiles")
    if int(result["runner_verification_discrepancy_report_operator_message_count"]) != 0:
        failures.append(f"{sample}: expected no projected operator messages before saving profiles")
    if not result["runner_verification_discrepancy_report_safe"]:
        failures.append(f"{sample}: expected inert runner verification discrepancy report projections")
    if result["runner_real_launch_final_gate_audit_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner real launch final gate audits")
    if not result["runner_real_launch_final_gate_audit_safe"]:
        failures.append(f"{sample}: expected inert runner real launch final gate audits")
    if result["runner_evidence_gap_index_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving runner evidence gap indexes")
    if not result["runner_evidence_gap_index_safe"]:
        failures.append(f"{sample}: expected inert runner evidence gap indexes")
    if result["runner_development_path_anchor_status"] != "path_anchor_round18_first_real_test_ready":
        failures.append(f"{sample}: expected round-18 first-real-test-ready runner development path anchor")
    if result["runner_development_path_anchor_current_phase"] != "real_execution_minimal_implementation":
        failures.append(f"{sample}: expected real-execution minimal implementation phase")
    if int(result["runner_development_path_anchor_completed_round_count"]) != 18:
        failures.append(f"{sample}: expected 18 completed fixed-path rounds")
    if int(result["runner_development_path_anchor_locked_round_count"]) != 0:
        failures.append(f"{sample}: expected 0 locked fixed-path rounds")
    if int(result["runner_development_path_anchor_launchable_count"]) != 0:
        failures.append(f"{sample}: expected development path anchor launchable_count=0")
    if not result["runner_development_path_anchor_safe"]:
        failures.append(f"{sample}: expected inert runner development path anchor")
    if result["runner_process_lifecycle_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving lifecycle profiles")
    if int(result["runner_process_lifecycle_session_state_count"]) != 0:
        failures.append(f"{sample}: expected no lifecycle session state before saving profiles")
    if int(result["runner_process_lifecycle_pending_count"]) != 0:
        failures.append(f"{sample}: expected no pending lifecycle states before saving profiles")
    if int(result["runner_process_lifecycle_terminal_count"]) != 0:
        failures.append(f"{sample}: expected no terminal lifecycle states before saving profiles")
    if not result["runner_process_lifecycle_safe"]:
        failures.append(f"{sample}: expected safe runner process lifecycle projection")
    if result["runner_stream_capture_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving stream capture profiles")
    if int(result["runner_stream_capture_stream_count"]) != 0:
        failures.append(f"{sample}: expected no stream capture states before saving profiles")
    if int(result["runner_stream_capture_captured_count"]) != 0:
        failures.append(f"{sample}: expected no captured streams before saving profiles")
    if int(result["runner_stream_capture_pending_count"]) != 0:
        failures.append(f"{sample}: expected no pending stream captures before saving profiles")
    if not result["runner_stream_capture_safe"]:
        failures.append(f"{sample}: expected safe runner stream capture projection")
    if result["runner_event_writer_status"] != "no_saved_profiles":
        failures.append(f"{sample}: expected no_saved_profiles before saving event writer profiles")
    if int(result["runner_event_writer_projected_event_count"]) != 0:
        failures.append(f"{sample}: expected no projected runner events before saving profiles")
    if int(result["runner_event_writer_terminal_event_count"]) != 0:
        failures.append(f"{sample}: expected no terminal projected runner events before saving profiles")
    if not result["runner_event_writer_safe"]:
        failures.append(f"{sample}: expected safe runner event writer projection")
    if result["runner_real_execution_touchpoint_inventory_status"] != "touchpoint_inventory_locked":
        failures.append(f"{sample}: expected locked runner real execution touchpoint inventory")
    if int(result["runner_real_execution_touchpoint_inventory_touchpoint_count"]) < 18:
        failures.append(f"{sample}: expected real execution touchpoint inventory entries")
    if int(result["runner_real_execution_touchpoint_inventory_locked_count"]) != int(
        result["runner_real_execution_touchpoint_inventory_touchpoint_count"]
    ):
        failures.append(f"{sample}: expected every real execution touchpoint to remain locked")
    if int(result["runner_real_execution_touchpoint_inventory_launchable_count"]) != 0:
        failures.append(f"{sample}: expected touchpoint inventory launchable_count=0")
    if not result["runner_real_execution_touchpoint_inventory_safe"]:
        failures.append(f"{sample}: expected inert runner real execution touchpoint inventory")
    if result["runner_real_execution_touchpoint_coverage_index_status"] != "touchpoint_coverage_index_locked":
        failures.append(f"{sample}: expected locked runner real execution touchpoint coverage index")
    if int(result["runner_real_execution_touchpoint_coverage_index_entry_count"]) < 18:
        failures.append(f"{sample}: expected real execution touchpoint coverage entries")
    if int(result["runner_real_execution_touchpoint_coverage_index_locked_count"]) != int(
        result["runner_real_execution_touchpoint_coverage_index_entry_count"]
    ):
        failures.append(f"{sample}: expected every real execution touchpoint coverage entry to remain locked")
    if int(result["runner_real_execution_touchpoint_coverage_index_stage_count"]) < 6:
        failures.append(f"{sample}: expected touchpoint coverage to map to multiple audit stages")
    if int(result["runner_real_execution_touchpoint_coverage_index_launchable_count"]) != 0:
        failures.append(f"{sample}: expected touchpoint coverage index launchable_count=0")
    if not result["runner_real_execution_touchpoint_coverage_index_safe"]:
        failures.append(f"{sample}: expected inert runner real execution touchpoint coverage index")
    if result["runner_real_execution_touchpoint_gap_link_status"] != "touchpoint_gap_link_locked":
        failures.append(f"{sample}: expected locked runner real execution touchpoint gap links")
    if int(result["runner_real_execution_touchpoint_gap_link_entry_count"]) < 18:
        failures.append(f"{sample}: expected real execution touchpoint gap link entries")
    if int(result["runner_real_execution_touchpoint_gap_link_locked_count"]) != int(
        result["runner_real_execution_touchpoint_gap_link_entry_count"]
    ):
        failures.append(f"{sample}: expected every real execution touchpoint gap link to remain locked")
    if int(result["runner_real_execution_touchpoint_gap_link_launchable_count"]) != 0:
        failures.append(f"{sample}: expected touchpoint gap link launchable_count=0")
    if not result["runner_real_execution_touchpoint_gap_link_safe"]:
        failures.append(f"{sample}: expected inert runner real execution touchpoint gap links")
    if result["runner_real_execution_touchpoint_unlock_matrix_status"] != "touchpoint_unlock_matrix_locked":
        failures.append(f"{sample}: expected locked runner real execution touchpoint unlock matrix")
    if int(result["runner_real_execution_touchpoint_unlock_matrix_entry_count"]) < 18:
        failures.append(f"{sample}: expected real execution touchpoint unlock matrix entries")
    if int(result["runner_real_execution_touchpoint_unlock_matrix_locked_count"]) != int(
        result["runner_real_execution_touchpoint_unlock_matrix_entry_count"]
    ):
        failures.append(f"{sample}: expected every real execution touchpoint unlock matrix item to remain locked")
    if int(result["runner_real_execution_touchpoint_unlock_matrix_implementation_allowed_count"]) != 0:
        failures.append(f"{sample}: expected touchpoint unlock matrix implementation_allowed_count=0")
    if int(result["runner_real_execution_touchpoint_unlock_matrix_execution_allowed_count"]) != 0:
        failures.append(f"{sample}: expected touchpoint unlock matrix execution_allowed_count=0")
    if int(result["runner_real_execution_touchpoint_unlock_matrix_launchable_count"]) != 0:
        failures.append(f"{sample}: expected touchpoint unlock matrix launchable_count=0")
    if not result["runner_real_execution_touchpoint_unlock_matrix_safe"]:
        failures.append(f"{sample}: expected inert runner real execution touchpoint unlock matrix")
    if result["runner_real_execution_unlock_phrase_readiness_status"] != "unlock_phrase_readiness_locked":
        failures.append(f"{sample}: expected locked runner real execution unlock phrase readiness")
    if int(result["runner_real_execution_unlock_phrase_readiness_required_phrase_count"]) != 1:
        failures.append(f"{sample}: expected one required explicit unlock phrase")
    if int(result["runner_real_execution_unlock_phrase_readiness_observed_phrase_count"]) != 0:
        failures.append(f"{sample}: expected no observed unlock phrase")
    if int(result["runner_real_execution_unlock_phrase_readiness_matching_phrase_count"]) != 0:
        failures.append(f"{sample}: expected no matching unlock phrase")
    if int(result["runner_real_execution_unlock_phrase_readiness_accepted_phrase_count"]) != 0:
        failures.append(f"{sample}: expected no accepted unlock phrase")
    if int(result["runner_real_execution_unlock_phrase_readiness_implementation_allowed_count"]) != 0:
        failures.append(f"{sample}: expected unlock phrase readiness implementation_allowed_count=0")
    if int(result["runner_real_execution_unlock_phrase_readiness_execution_allowed_count"]) != 0:
        failures.append(f"{sample}: expected unlock phrase readiness execution_allowed_count=0")
    if int(result["runner_real_execution_unlock_phrase_readiness_launchable_count"]) != 0:
        failures.append(f"{sample}: expected unlock phrase readiness launchable_count=0")
    if not result["runner_real_execution_unlock_phrase_readiness_safe"]:
        failures.append(f"{sample}: expected inert runner real execution unlock phrase readiness")
    if (
        result["runner_real_execution_pre_unlock_evidence_packet_index_status"]
        != "pre_unlock_evidence_packet_index_locked"
    ):
        failures.append(f"{sample}: expected locked runner pre-unlock evidence packet index")
    if int(result["runner_real_execution_pre_unlock_evidence_packet_index_section_count"]) != 3:
        failures.append(f"{sample}: expected three pre-unlock evidence packet sections")
    if int(result["runner_real_execution_pre_unlock_evidence_packet_index_review_ready_count"]) != 0:
        failures.append(f"{sample}: expected no accepted review packet")
    if int(result["runner_real_execution_pre_unlock_evidence_packet_index_accepted_phrase_count"]) != 0:
        failures.append(f"{sample}: expected no accepted phrase in evidence packet")
    if int(result["runner_real_execution_pre_unlock_evidence_packet_index_implementation_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock packet implementation_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_evidence_packet_index_execution_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock packet execution_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_evidence_packet_index_launchable_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock packet launchable_count=0")
    if not result["runner_real_execution_pre_unlock_evidence_packet_index_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock evidence packet index")
    if result["runner_real_execution_pre_unlock_review_checklist_status"] != "pre_unlock_review_checklist_locked":
        failures.append(f"{sample}: expected locked runner pre-unlock review checklist")
    if int(result["runner_real_execution_pre_unlock_review_checklist_item_count"]) != 9:
        failures.append(f"{sample}: expected nine pre-unlock review checklist items")
    if int(result["runner_real_execution_pre_unlock_review_checklist_pending_count"]) != int(
        result["runner_real_execution_pre_unlock_review_checklist_item_count"]
    ):
        failures.append(f"{sample}: expected every pre-unlock review checklist item to remain pending")
    if int(result["runner_real_execution_pre_unlock_review_checklist_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted pre-unlock review checklist answers")
    if int(result["runner_real_execution_pre_unlock_review_checklist_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready pre-unlock review checklist answers")
    if int(result["runner_real_execution_pre_unlock_review_checklist_implementation_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock checklist implementation_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_review_checklist_execution_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock checklist execution_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_review_checklist_launchable_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock checklist launchable_count=0")
    if not result["runner_real_execution_pre_unlock_review_checklist_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock review checklist")
    if result["runner_real_execution_pre_unlock_reviewer_role_map_status"] != "pre_unlock_reviewer_role_map_locked":
        failures.append(f"{sample}: expected locked runner pre-unlock reviewer role map")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_entry_count"]) != 9:
        failures.append(f"{sample}: expected nine pre-unlock reviewer role entries")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_unique_role_count"]) != 3:
        failures.append(f"{sample}: expected three pre-unlock reviewer roles")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_assigned_count"]) != 0:
        failures.append(f"{sample}: expected no assigned pre-unlock reviewer roles")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted pre-unlock reviewer roles")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready pre-unlock reviewer roles")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_implementation_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock reviewer role map implementation_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_execution_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock reviewer role map execution_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_reviewer_role_map_launchable_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock reviewer role map launchable_count=0")
    if not result["runner_real_execution_pre_unlock_reviewer_role_map_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock reviewer role map")
    if (
        result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_status"]
        != "pre_unlock_reviewer_signoff_rubric_locked"
    ):
        failures.append(f"{sample}: expected locked runner pre-unlock reviewer sign-off rubric")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_entry_count"]) != 3:
        failures.append(f"{sample}: expected three pre-unlock reviewer sign-off rubric entries")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_unique_role_count"]) != 3:
        failures.append(f"{sample}: expected three pre-unlock reviewer sign-off roles")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_required_count"]) != 3:
        failures.append(f"{sample}: expected three required pre-unlock reviewer sign-offs")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted pre-unlock reviewer sign-offs")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready pre-unlock reviewer sign-offs")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_implementation_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock sign-off rubric implementation_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_execution_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock sign-off rubric execution_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_launchable_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock sign-off rubric launchable_count=0")
    if not result["runner_real_execution_pre_unlock_reviewer_signoff_rubric_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock reviewer sign-off rubric")
    if (
        result["runner_real_execution_pre_unlock_signoff_evidence_binding_status"]
        != "pre_unlock_signoff_evidence_binding_locked"
    ):
        failures.append(f"{sample}: expected locked runner pre-unlock sign-off evidence binding")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_entry_count"]) != 3:
        failures.append(f"{sample}: expected three pre-unlock sign-off evidence bindings")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_unique_role_count"]) != 3:
        failures.append(f"{sample}: expected three pre-unlock sign-off evidence binding roles")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_checklist_link_count"]) != 9:
        failures.append(f"{sample}: expected nine pre-unlock sign-off checklist links")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_packet_section_link_count"]) != 3:
        failures.append(f"{sample}: expected three pre-unlock sign-off packet section links")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted pre-unlock sign-off evidence bindings")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready pre-unlock sign-off evidence bindings")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_implementation_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock sign-off evidence binding implementation_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_execution_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock sign-off evidence binding execution_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_signoff_evidence_binding_launchable_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock sign-off evidence binding launchable_count=0")
    if not result["runner_real_execution_pre_unlock_signoff_evidence_binding_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock sign-off evidence binding")
    if (
        result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_status"]
        != "pre_unlock_implementation_entry_readiness_ledger_locked"
    ):
        failures.append(f"{sample}: expected locked runner pre-unlock implementation entry readiness ledger")
    if int(result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_entry_count"]) != 5:
        failures.append(f"{sample}: expected five pre-unlock implementation entry ledger entries")
    if int(result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_locked_count"]) != 5:
        failures.append(f"{sample}: expected five locked pre-unlock implementation entry ledger entries")
    if int(result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_blocking_count"]) != 5:
        failures.append(f"{sample}: expected five blocking pre-unlock implementation entry ledger entries")
    if int(result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted pre-unlock implementation entry ledger entries")
    if int(result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready pre-unlock implementation entry ledger entries")
    if int(result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_round_10_allowed_count"]) != 0:
        failures.append(f"{sample}: expected round_10_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_launchable_count"]) != 0:
        failures.append(f"{sample}: expected pre-unlock implementation entry ledger launchable_count=0")
    if not result["runner_real_execution_pre_unlock_implementation_entry_readiness_ledger_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock implementation entry readiness ledger")
    if (
        result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_status"]
        != "pre_unlock_round10_minimal_scope_preview_locked"
    ):
        failures.append(f"{sample}: expected locked runner pre-unlock round-10 minimal scope preview")
    if int(result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_entry_count"]) != 6:
        failures.append(f"{sample}: expected six pre-unlock round-10 minimal scope preview entries")
    if int(result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_minimal_touch_count"]) != 4:
        failures.append(f"{sample}: expected four round-10 minimal touch preview entries")
    if int(result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_deferred_count"]) != 2:
        failures.append(f"{sample}: expected two explicitly deferred preview entries")
    if int(result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted round-10 minimal scope previews")
    if int(result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready round-10 minimal scope previews")
    if int(result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_round_10_allowed_count"]) != 0:
        failures.append(f"{sample}: expected round-10 preview allowed count=0")
    if int(result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_launchable_count"]) != 0:
        failures.append(f"{sample}: expected round-10 preview launchable_count=0")
    if not result["runner_real_execution_pre_unlock_round10_minimal_scope_preview_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock round-10 minimal scope preview")
    if (
        result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_status"]
        != "pre_unlock_explicit_unlock_handoff_receipt_locked"
    ):
        failures.append(f"{sample}: expected locked runner pre-unlock explicit unlock handoff receipt")
    if int(result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_entry_count"]) != 7:
        failures.append(f"{sample}: expected seven explicit unlock handoff receipt entries")
    if int(result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_required_count"]) != 7:
        failures.append(f"{sample}: expected seven required explicit unlock handoff receipt entries")
    if int(result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_observed_count"]) != 0:
        failures.append(f"{sample}: expected no observed explicit unlock handoff receipts")
    if int(result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted explicit unlock handoff receipts")
    if int(result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready explicit unlock handoff receipts")
    if int(result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_round_10_allowed_count"]) != 0:
        failures.append(f"{sample}: expected explicit unlock handoff receipt round_10_allowed_count=0")
    if int(result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_launchable_count"]) != 0:
        failures.append(f"{sample}: expected explicit unlock handoff receipt launchable_count=0")
    if not result["runner_real_execution_pre_unlock_explicit_unlock_handoff_receipt_safe"]:
        failures.append(f"{sample}: expected inert runner pre-unlock explicit unlock handoff receipt")
    if (
        result["runner_real_execution_pre_round10_locked_handoff_summary_status"]
        != "pre_round10_locked_handoff_summary_locked"
    ):
        failures.append(f"{sample}: expected locked runner pre-round-10 handoff summary")
    if int(result["runner_real_execution_pre_round10_locked_handoff_summary_entry_count"]) != 6:
        failures.append(f"{sample}: expected six pre-round-10 handoff summary entries")
    if int(result["runner_real_execution_pre_round10_locked_handoff_summary_locked_count"]) != 6:
        failures.append(f"{sample}: expected six locked pre-round-10 handoff summary entries")
    if int(result["runner_real_execution_pre_round10_locked_handoff_summary_blocking_count"]) != 6:
        failures.append(f"{sample}: expected six blocking pre-round-10 handoff summary entries")
    if int(result["runner_real_execution_pre_round10_locked_handoff_summary_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted pre-round-10 handoff summaries")
    if int(result["runner_real_execution_pre_round10_locked_handoff_summary_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready pre-round-10 handoff summaries")
    if int(result["runner_real_execution_pre_round10_locked_handoff_summary_round_10_allowed_count"]) != 0:
        failures.append(f"{sample}: expected pre-round-10 handoff summary round_10_allowed_count=0")
    if int(result["runner_real_execution_pre_round10_locked_handoff_summary_launchable_count"]) != 0:
        failures.append(f"{sample}: expected pre-round-10 handoff summary launchable_count=0")
    if not result["runner_real_execution_pre_round10_locked_handoff_summary_safe"]:
        failures.append(f"{sample}: expected inert runner pre-round-10 handoff summary")
    if (
        result["runner_real_execution_round10_explicit_unlock_checkpoint_status"]
        != "round10_explicit_unlock_checkpoint_locked"
    ):
        failures.append(f"{sample}: expected locked runner round-10 explicit unlock checkpoint")
    if int(result["runner_real_execution_round10_explicit_unlock_checkpoint_entry_count"]) != 5:
        failures.append(f"{sample}: expected five round-10 explicit unlock checkpoint entries")
    if int(result["runner_real_execution_round10_explicit_unlock_checkpoint_required_count"]) != 5:
        failures.append(f"{sample}: expected five required round-10 explicit unlock checkpoint entries")
    if int(result["runner_real_execution_round10_explicit_unlock_checkpoint_externally_satisfied_count"]) != 0:
        failures.append(f"{sample}: expected no externally satisfied round-10 unlock checkpoints")
    if int(result["runner_real_execution_round10_explicit_unlock_checkpoint_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted round-10 unlock checkpoints")
    if int(result["runner_real_execution_round10_explicit_unlock_checkpoint_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready round-10 unlock checkpoints")
    if int(result["runner_real_execution_round10_explicit_unlock_checkpoint_round_10_allowed_count"]) != 0:
        failures.append(f"{sample}: expected round-10 explicit unlock checkpoint round_10_allowed_count=0")
    if int(result["runner_real_execution_round10_explicit_unlock_checkpoint_launchable_count"]) != 0:
        failures.append(f"{sample}: expected round-10 explicit unlock checkpoint launchable_count=0")
    if result["runner_real_execution_round10_explicit_unlock_checkpoint_external_satisfied"]:
        failures.append(f"{sample}: expected external unlock satisfied flag to remain false")
    if not result["runner_real_execution_round10_explicit_unlock_checkpoint_safe"]:
        failures.append(f"{sample}: expected inert runner round-10 explicit unlock checkpoint")
    if (
        result["runner_real_execution_round10_unlock_decision_mirror_status"]
        != "round10_unlock_decision_mirror_locked"
    ):
        failures.append(f"{sample}: expected locked runner round-10 unlock decision mirror")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_entry_count"]) != 5:
        failures.append(f"{sample}: expected five round-10 unlock decision entries")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_locked_count"]) != 5:
        failures.append(f"{sample}: expected five locked round-10 unlock decision entries")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_not_allowed_count"]) != 5:
        failures.append(f"{sample}: expected five not-allowed round-10 unlock decision entries")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_accepted_count"]) != 0:
        failures.append(f"{sample}: expected no accepted round-10 unlock decisions")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_ready_count"]) != 0:
        failures.append(f"{sample}: expected no ready round-10 unlock decisions")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_external_satisfied_count"]) != 0:
        failures.append(f"{sample}: expected no externally satisfied round-10 unlock decisions")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_round_10_allowed_count"]) != 0:
        failures.append(f"{sample}: expected round-10 unlock decision mirror round_10_allowed_count=0")
    if int(result["runner_real_execution_round10_unlock_decision_mirror_launchable_count"]) != 0:
        failures.append(f"{sample}: expected round-10 unlock decision mirror launchable_count=0")
    if result["runner_real_execution_round10_unlock_decision_mirror_can_enter_round_10"]:
        failures.append(f"{sample}: expected round-10 unlock decision mirror can_enter_round_10=false")
    if not result["runner_real_execution_round10_unlock_decision_mirror_safe"]:
        failures.append(f"{sample}: expected inert runner round-10 unlock decision mirror")
    return failures


def _governance_layers(
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


def _valid_runner_config() -> dict[str, object]:
    return {
        "schema_version": "flowtrace_runner_config.v1",
        "runner": {
            "enable_real_execution": True,
            "typed_consent": "RUN TARGET PROJECT",
        },
        "process": {
            "no_shell_string": True,
            "argv_must_be_tokenized": True,
            "inherit_environment": False,
        },
        "logs": {
            "stdout_chunk_bytes": 4096,
            "stderr_chunk_bytes": 4096,
            "max_stream_bytes": 2 * 1024 * 1024,
        },
        "cancel_timeout": {
            "default_timeout_seconds": 120,
        },
    }


def _bad_runner_config() -> dict[str, object]:
    return {
        "schema_version": "flowtrace_runner_config.v0",
        "runner": {
            "enable_real_execution": "yes",
        },
        "process": {
            "no_shell_string": False,
            "argv_must_be_tokenized": "true",
            "inherit_environment": True,
        },
        "logs": {
            "stdout_chunk_bytes": 1,
            "stderr_chunk_bytes": "4096",
            "max_stream_bytes": 1,
        },
        "cancel_timeout": {
            "default_timeout_seconds": 1,
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
