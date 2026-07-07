from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .context import utc_now
from .runner_process_control import RunnerProcessRegistry


RUNNER_REAL_EXECUTION_TYPED_CONSENT = "RUN TARGET PROJECT"
LOW_RISK_SAMPLE_SEGMENT = Path("examples") / "realistic_projects"
DEFAULT_TIMEOUT_SECONDS = 120
MAX_CAPTURE_BYTES = 2 * 1024 * 1024


def launch_low_risk_sample_profile(
    project_context: dict[str, Any],
    profile: dict[str, Any],
    dry_run_report: dict[str, Any],
    typed_consent: str,
    process_registry: RunnerProcessRegistry | None = None,
) -> dict[str, object]:
    if typed_consent != RUNNER_REAL_EXECUTION_TYPED_CONSENT:
        raise ValueError("typed_consent must be RUN TARGET PROJECT")
    project_root = Path(str(project_context.get("root") or "")).resolve()
    trace_dir = Path(str(project_context.get("trace_dir") or project_root / ".flowtrace")).resolve()
    _ensure_low_risk_sample_project(project_root)
    _ensure_dry_run_prepared(dry_run_report)
    argv = _safe_argv(project_root, profile)
    run_dir = _run_dir(trace_dir, str(profile.get("id") or "profile"))
    run_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    launch_id = f"runner_real_launch:{started_at.replace(':', '').replace('.', '')}"
    process = subprocess.Popen(
        argv,
        cwd=str(project_root),
        env=_execution_env(project_root, trace_dir, profile),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    if process_registry is not None:
        process_registry.register(launch_id, process, profile)
    terminal_override: str | None = None
    control_reason: str | None = None
    timed_out = False
    try:
        stdout_value, stderr_value = process.communicate(timeout=DEFAULT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.terminate()
        stdout_value, stderr_value = process.communicate()
    finally:
        if process_registry is not None:
            control_record = process_registry.unregister(launch_id)
            if isinstance(control_record, dict):
                requested = control_record.get("requested_terminal_state")
                if requested in {"cancelled", "timed_out"}:
                    terminal_override = str(requested)
                    control_reason = str(control_record.get("control_reason") or requested)
    ended_at = utc_now()
    stdout_text = _bounded_text(stdout_value or "")
    stderr_text = _bounded_text(stderr_value or "")
    (run_dir / "stdout.log").write_text(stdout_text, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr_text, encoding="utf-8")
    if terminal_override:
        status = terminal_override
    elif timed_out:
        status = "timed_out"
        control_reason = "default timeout exceeded"
    else:
        status = "completed" if process.returncode == 0 else "failed"
    execution = {
        "schema_version": "runner_real_execution.v1",
        "launch_id": launch_id,
        "profile_id": profile.get("id"),
        "label": profile.get("label"),
        "status": status,
        "exit_code": process.returncode,
        "started_at": started_at,
        "ended_at": ended_at,
        "control_reason": control_reason,
        "working_directory": str(project_root),
        "argv": argv,
        "uses_shell": False,
        "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
        "run_directory": str(run_dir),
        "stdout_log": str(run_dir / "stdout.log"),
        "stderr_log": str(run_dir / "stderr.log"),
        "stdout_preview": stdout_text[-4096:],
        "stderr_preview": stderr_text[-4096:],
        "writes_user_project": False,
        "writes_trace_dir": True,
    }
    (run_dir / "summary.json").write_text(_json_dumps(execution), encoding="utf-8")
    return execution


def _ensure_low_risk_sample_project(project_root: Path) -> None:
    normalized_parts = tuple(part.lower() for part in project_root.parts)
    expected = tuple(part.lower() for part in LOW_RISK_SAMPLE_SEGMENT.parts)
    if not _contains_subsequence(normalized_parts, expected):
        raise ValueError("real execution is limited to examples/realistic_projects sample projects")
    if not (project_root / "pyproject.toml").is_file():
        raise ValueError("sample project must contain pyproject.toml")


def _ensure_dry_run_prepared(dry_run_report: dict[str, Any]) -> None:
    dry_run = dry_run_report.get("dry_run") if isinstance(dry_run_report.get("dry_run"), dict) else {}
    if dry_run.get("status") != "prepared":
        raise ValueError("runner dry-run must be prepared before launch")


def _safe_argv(project_root: Path, profile: dict[str, Any]) -> list[str]:
    if profile.get("mode") != "command":
        raise ValueError("only command profiles can be launched")
    argv = profile.get("argv") if isinstance(profile.get("argv"), list) else []
    if len(argv) < 2:
        raise ValueError("profile argv must include a python file")
    command = str(argv[0])
    if command.lower() not in {"python", "python.exe"}:
        raise ValueError("minimal runner only supports python command profiles")
    relative_file = str(argv[1]).replace("\\", "/")
    if relative_file.startswith("../") or relative_file.startswith("/") or not relative_file.endswith(".py"):
        raise ValueError("python entry file must be a relative .py file inside the sample project")
    entry_path = (project_root / relative_file).resolve()
    if not str(entry_path).startswith(str(project_root)) or not entry_path.is_file():
        raise ValueError("python entry file must exist inside the sample project")
    return [sys.executable, relative_file, *[str(item) for item in argv[2:]]]


def _execution_env(project_root: Path, trace_dir: Path, profile: dict[str, Any]) -> dict[str, str]:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONIOENCODING": "utf-8",
        "FLOWTRACE_DIR": str(trace_dir),
    }
    profile_env = profile.get("env") if isinstance(profile.get("env"), dict) else {}
    for key, value in profile_env.items():
        if isinstance(key, str) and isinstance(value, str) and key in {"FLOWTRACE_DIR"}:
            env[key] = value
    src_root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = os.pathsep.join([str(src_root), str(project_root)])
    return env


def _run_dir(trace_dir: Path, profile_id: str) -> Path:
    safe_profile = profile_id.replace(":", "_").replace("/", "_").replace("\\", "_")
    return trace_dir / "runner" / f"real_{safe_profile}_{utc_now().replace(':', '').replace('.', '')}"


def _bounded_text(value: str) -> str:
    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= MAX_CAPTURE_BYTES:
        return value
    return encoded[-MAX_CAPTURE_BYTES:].decode("utf-8", errors="replace")


def _contains_subsequence(parts: tuple[str, ...], expected: tuple[str, ...]) -> bool:
    if not expected or len(expected) > len(parts):
        return False
    for index in range(0, len(parts) - len(expected) + 1):
        if parts[index : index + len(expected)] == expected:
            return True
    return False


def _json_dumps(payload: dict[str, object]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
