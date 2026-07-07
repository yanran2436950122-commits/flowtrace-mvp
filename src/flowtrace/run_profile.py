from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


RUN_PROFILE_COLLECTION_VERSION = "project_run_profiles.v1"


def build_project_run_profiles(
    project_model: dict[str, Any],
    integration_plan: dict[str, Any],
) -> dict[str, object]:
    """Create deterministic command drafts from integration targets.

    Profiles are deliberately inert: they describe how a user may run the
    target project, but FlowTrace does not execute them without a later,
    explicit confirmation layer.
    """
    context = project_model.get("context") if isinstance(project_model.get("context"), dict) else {}
    root = Path(str(context.get("root") or project_model.get("root") or "."))
    trace_dir = Path(str(context.get("trace_dir") or (root / ".flowtrace")))
    targets = integration_plan.get("execution_targets", [])
    profiles = [_profile_from_target(target, root, trace_dir) for target in targets if isinstance(target, dict)]
    profiles = [profile for profile in profiles if profile]

    return {
        "schema_version": RUN_PROFILE_COLLECTION_VERSION,
        "context": project_model.get("context"),
        "summary": {
            "profile_count": len(profiles),
            "executable_count": sum(1 for item in profiles if item["mode"] == "command"),
            "manual_count": sum(1 for item in profiles if item["mode"] == "manual"),
            "requires_confirmation_count": sum(1 for item in profiles if item["requires_confirmation"]),
        },
        "profiles": profiles,
        "safety": {
            "executes_commands": False,
            "requires_user_confirmation": True,
            "writes_user_project": False,
        },
    }


def _profile_from_target(target: dict[str, Any], root: Path, trace_dir: Path) -> dict[str, object] | None:
    label = str(target.get("label") or target.get("id") or "run")
    file = _relative_file(target.get("file"))
    run_hint = str(target.get("run_hint") or "")
    profile_id = _profile_id(label, file, str(target.get("line") or ""))

    if file and _looks_python_file(file):
        argv = ["python", file]
        return {
            "id": profile_id,
            "label": label,
            "mode": "command",
            "command": "python",
            "args": [file],
            "argv": argv,
            "display_command": _display_command(argv),
            "working_directory": str(root),
            "env": _default_env(root, trace_dir),
            "source_target": target,
            "confidence": target.get("confidence") or "medium",
            "requires_confirmation": True,
            "preflight": _preflight(root, file),
            "notes": ["命令草案来自入口候选；执行前需要用户确认工作目录、环境变量和输入数据。"],
        }

    if target.get("source") == "route_decorator" or "Web" in run_hint or "HTTP" in run_hint:
        return {
            "id": profile_id,
            "label": label,
            "mode": "manual",
            "command": None,
            "args": [],
            "argv": [],
            "display_command": "启动目标 Web 服务后，用浏览器或 HTTP 请求触发该入口。",
            "working_directory": str(root),
            "env": _default_env(root, trace_dir),
            "source_target": target,
            "confidence": target.get("confidence") or "medium",
            "requires_confirmation": True,
            "preflight": _preflight(root, file),
            "notes": ["该入口需要真实用户操作或 Web 请求；后续应接入浏览器录制。"],
        }

    if target.get("kind") == "workflow":
        return {
            "id": profile_id,
            "label": label,
            "mode": "manual",
            "command": None,
            "args": [],
            "argv": [],
            "display_command": "按目标项目原有入口运行，确保该 workflow 被真实流程调用。",
            "working_directory": str(root),
            "env": _default_env(root, trace_dir),
            "source_target": target,
            "confidence": target.get("confidence") or "medium",
            "requires_confirmation": True,
            "preflight": _preflight(root, file),
            "notes": ["workflow 方法通常不是直接命令入口；优先通过真实入口触发。"],
        }

    return None


def _relative_file(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("\\", "/")
    if normalized.startswith("../") or normalized.startswith("/"):
        return None
    return normalized


def _looks_python_file(value: str) -> bool:
    return value.endswith(".py")


def _default_env(root: Path, trace_dir: Path) -> dict[str, str]:
    return {
        "PYTHONPATH": str(root),
        "FLOWTRACE_DIR": str(trace_dir),
    }


def _preflight(root: Path, file: str | None) -> list[dict[str, object]]:
    checks = [
        {
            "id": "working_directory_exists",
            "label": "工作目录存在",
            "passed": root.exists() and root.is_dir(),
            "detail": str(root),
        },
        {
            "id": "trace_dir_declared",
            "label": "运行记录目录已声明",
            "passed": True,
            "detail": str(root / ".flowtrace"),
        },
    ]
    if file:
        target_file = root / file
        checks.append(
            {
                "id": "entry_file_exists",
                "label": "入口文件存在",
                "passed": target_file.exists() and target_file.is_file(),
                "detail": str(target_file),
            }
        )
    return checks


def _display_command(argv: list[str]) -> str:
    return " ".join(_quote_arg(item) for item in argv)


def _quote_arg(value: str) -> str:
    if not value or any(char.isspace() for char in value):
        return f'"{value}"'
    return value


def _profile_id(label: str, file: str | None, line: str) -> str:
    raw = "|".join([label, file or "", line])
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    safe_label = "".join(char if char.isalnum() else "-" for char in label.lower()).strip("-") or "run"
    return f"profile:{safe_label}:{digest}"
