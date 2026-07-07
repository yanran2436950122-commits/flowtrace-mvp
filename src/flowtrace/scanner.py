from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path


IGNORED_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".venv", "__pycache__", "node_modules"}
PROJECT_MODEL_VERSION = "project_model.v1"
PROJECT_MARKER_FILES = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    "package.json",
    "README.md",
    "readme.md",
    "manage.py",
}
FRAMEWORK_IMPORT_HINTS = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "click": "Click",
    "typer": "Typer",
    "pytest": "pytest",
    "pydantic": "Pydantic",
    "sqlalchemy": "SQLAlchemy",
}


def collect_declared_methods(project_root: Path) -> list[str]:
    return sorted(scan_project(project_root)["declared_methods"])


def scan_project(project_root: Path) -> dict[str, object]:
    root = project_root.resolve()
    modules: list[dict[str, object]] = []
    classes: list[dict[str, object]] = []
    functions: list[dict[str, object]] = []
    imports: list[dict[str, object]] = []
    entrypoints: list[dict[str, object]] = []
    declared_methods: set[str] = set()
    traced_method_names: set[str] = set()
    contract_method_names: set[str] = set()
    scan_errors: list[dict[str, object]] = []
    file_summary = _file_summary(root)

    for path in _python_files(root):
        relative_path = _relative_path(path, root)
        module_name = _module_name(path, root)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            scan_errors.append({"file": relative_path, "error": type(exc).__name__, "message": str(exc)})
            continue

        module_functions = _module_functions(tree, module_name, relative_path)
        module_classes = _module_classes(tree, module_name, relative_path)
        module_imports = _imports(tree, module_name, relative_path)
        module_contracts = _contract_names(tree)
        module_entrypoints = _entrypoints(tree, module_name, relative_path, module_functions)
        traced_methods = {item["traced_label"] for item in module_functions if item.get("traced_label")}

        modules.append(
            {
                "id": module_name,
                "name": module_name,
                "file": relative_path,
                "function_count": len(module_functions),
                "class_count": len(module_classes),
                "import_count": len(module_imports),
                "declared_method_count": len(traced_methods | module_contracts),
                "entrypoint_count": len(module_entrypoints),
            }
        )
        classes.extend(module_classes)
        functions.extend(module_functions)
        imports.extend(module_imports)
        entrypoints.extend(module_entrypoints)
        declared_methods.update(traced_methods)
        declared_methods.update(module_contracts)
        traced_method_names.update(traced_methods)
        contract_method_names.update(module_contracts)

    return {
        "schema_version": PROJECT_MODEL_VERSION,
        "root": str(root),
        "project_identity": _project_identity(root),
        "totals": {
            "files": file_summary["total_files"],
            "modules": len(modules),
            "classes": len(classes),
            "functions": len(functions),
            "entrypoints": len(entrypoints),
            "imports": len(imports),
            "declared_methods": len(declared_methods),
            "scan_errors": len(scan_errors),
        },
        "modules": sorted(modules, key=lambda item: str(item["name"])),
        "classes": sorted(classes, key=lambda item: str(item["id"])),
        "functions": sorted(functions, key=lambda item: str(item["id"])),
        "entrypoints": sorted(entrypoints, key=lambda item: (str(item["kind"]), str(item["id"]))),
        "imports": sorted(imports, key=lambda item: (str(item["module"]), str(item["name"]))),
        "declared_methods": sorted(declared_methods),
        "traced_methods": sorted(traced_method_names),
        "contract_methods": sorted(contract_method_names),
        "scan_errors": scan_errors,
        "file_summary": {
            **file_summary,
            "framework_hints": _framework_hints(imports, file_summary["markers"]),
        },
    }


def _python_files(project_root: Path) -> list[Path]:
    result = []
    for path in project_root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.relative_to(project_root).parts):
            continue
        result.append(path)
    return result


def _project_identity(project_root: Path) -> dict[str, object]:
    package_candidates = []
    for path in sorted(project_root.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_dir() or path.name in IGNORED_DIRS:
            continue
        if (path / "__init__.py").exists():
            package_candidates.append(path.name)
    return {
        "name": project_root.name,
        "root": str(project_root),
        "package_candidates": package_candidates[:12],
    }


def _file_summary(project_root: Path) -> dict[str, object]:
    total_files = 0
    python_files = 0
    extension_counts: Counter[str] = Counter()
    top_level: list[dict[str, object]] = []
    markers: list[dict[str, object]] = []

    for child in sorted(project_root.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
        if child.name in IGNORED_DIRS:
            continue
        if child.is_dir():
            counts = _count_files(child, project_root)
            if counts["total_files"]:
                top_level.append(
                    {
                        "name": child.name,
                        "path": _relative_path(child, project_root),
                        "kind": "directory",
                        "total_files": counts["total_files"],
                        "python_files": counts["python_files"],
                    }
                )
                total_files += int(counts["total_files"])
                python_files += int(counts["python_files"])
                extension_counts.update(counts["extensions"])
            continue

        total_files += 1
        if child.suffix == ".py":
            python_files += 1
        extension_counts[_extension_label(child)] += 1
        if child.name in PROJECT_MARKER_FILES:
            markers.append(_marker_info(child, project_root))

    markers.extend(_nested_marker_files(project_root))
    by_extension = [
        {"extension": extension, "count": count}
        for extension, count in sorted(extension_counts.items(), key=lambda item: (-item[1], item[0]))[:16]
    ]
    return {
        "total_files": total_files,
        "python_files": python_files,
        "ignored_dirs": sorted(IGNORED_DIRS),
        "by_extension": by_extension,
        "top_level": top_level[:32],
        "markers": _dedupe_markers(markers),
    }


def _count_files(directory: Path, project_root: Path) -> dict[str, object]:
    total_files = 0
    python_files = 0
    extensions: Counter[str] = Counter()
    for path in directory.rglob("*"):
        relative_parts = path.relative_to(project_root).parts
        if any(part in IGNORED_DIRS for part in relative_parts):
            continue
        if not path.is_file():
            continue
        total_files += 1
        if path.suffix == ".py":
            python_files += 1
        extensions[_extension_label(path)] += 1
    return {"total_files": total_files, "python_files": python_files, "extensions": extensions}


def _nested_marker_files(project_root: Path) -> list[dict[str, object]]:
    result = []
    for marker_name in ("requirements.txt", "pyproject.toml", "package.json"):
        for path in project_root.glob(f"*/{marker_name}"):
            if any(part in IGNORED_DIRS for part in path.relative_to(project_root).parts):
                continue
            result.append(_marker_info(path, project_root))
    return result


def _marker_info(path: Path, project_root: Path) -> dict[str, object]:
    return {
        "name": path.name,
        "path": _relative_path(path, project_root),
        "kind": _marker_kind(path.name),
    }


def _marker_kind(name: str) -> str:
    if name in {"pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile", "poetry.lock", "uv.lock"}:
        return "python_config"
    if name == "package.json":
        return "node_config"
    if name.lower() == "readme.md":
        return "docs"
    if name == "manage.py":
        return "entrypoint"
    return "marker"


def _dedupe_markers(markers: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    seen = set()
    for marker in markers:
        key = marker.get("path")
        if key in seen:
            continue
        seen.add(key)
        result.append(marker)
    return sorted(result, key=lambda item: str(item["path"]))[:24]


def _framework_hints(imports: list[dict[str, object]], markers: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: dict[str, set[str]] = {}
    marker_names = {str(marker.get("name")) for marker in markers}
    if "manage.py" in marker_names:
        seen.setdefault("Django", set()).add("manage.py")
    for item in imports:
        imported = str(item.get("name") or "").split(".")[0]
        label = FRAMEWORK_IMPORT_HINTS.get(imported)
        if label:
            seen.setdefault(label, set()).add(str(item.get("file") or "import"))
    return [
        {"name": name, "evidence": sorted(evidence)[:5]}
        for name, evidence in sorted(seen.items(), key=lambda item: item[0].lower())
    ]


def _extension_label(path: Path) -> str:
    return path.suffix.lower() or "[无扩展名]"


def _module_functions(tree: ast.AST, module_name: str, relative_path: str) -> list[dict[str, object]]:
    result = []
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.append(_function_info(node, module_name, relative_path, "function", node.name))
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result.append(_function_info(item, module_name, relative_path, "method", f"{node.name}.{item.name}", node.name))
    return result


def _function_info(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_name: str,
    relative_path: str,
    kind: str,
    qualname: str,
    class_name: str | None = None,
) -> dict[str, object]:
    decorators = [_decorator_name(item) for item in node.decorator_list]
    traced_label = _trace_label_from_decorators(node.decorator_list)
    info: dict[str, object] = {
        "id": f"{module_name}.{qualname}",
        "module": module_name,
        "name": node.name,
        "qualname": qualname,
        "kind": kind,
        "file": relative_path,
        "line": node.lineno,
        "async": isinstance(node, ast.AsyncFunctionDef),
        "decorators": [item for item in decorators if item],
    }
    if class_name:
        info["class"] = class_name
    if traced_label:
        info["traced_label"] = traced_label
    return info


def _module_classes(tree: ast.AST, module_name: str, relative_path: str) -> list[dict[str, object]]:
    result = []
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if not isinstance(node, ast.ClassDef):
            continue
        methods = [item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
        result.append(
            {
                "id": f"{module_name}.{node.name}",
                "module": module_name,
                "name": node.name,
                "file": relative_path,
                "line": node.lineno,
                "method_count": len(methods),
                "methods": methods,
                "decorators": [item for item in (_decorator_name(decorator) for decorator in node.decorator_list) if item],
            }
        )
    return result


def _imports(tree: ast.AST, module_name: str, relative_path: str) -> list[dict[str, object]]:
    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.append(
                    {
                        "module": module_name,
                        "file": relative_path,
                        "line": node.lineno,
                        "name": alias.name,
                        "asname": alias.asname,
                        "kind": "import",
                    }
                )
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                result.append(
                    {
                        "module": module_name,
                        "file": relative_path,
                        "line": node.lineno,
                        "name": f"{'.' * node.level}{node.module or ''}.{alias.name}".strip("."),
                        "asname": alias.asname,
                        "kind": "from_import",
                    }
                )
    return result


def _entrypoints(
    tree: ast.AST,
    module_name: str,
    relative_path: str,
    functions: list[dict[str, object]],
) -> list[dict[str, object]]:
    result = []
    for function in functions:
        if function["kind"] == "function" and function["name"] in {"main", "app", "application"}:
            result.append(
                {
                    "id": function["id"],
                    "module": module_name,
                    "file": relative_path,
                    "line": function["line"],
                    "kind": "function_name",
                    "label": function["name"],
                }
            )
        route_decorators = [item for item in function.get("decorators", []) if _looks_like_route(str(item))]
        for decorator in route_decorators:
            result.append(
                {
                    "id": f"{function['id']}:{decorator}",
                    "module": module_name,
                    "file": relative_path,
                    "line": function["line"],
                    "kind": "route_decorator",
                    "label": decorator,
                }
            )

    if _has_main_guard(tree):
        result.append(
            {
                "id": f"{module_name}:__main__",
                "module": module_name,
                "file": relative_path,
                "line": 1,
                "kind": "main_guard",
                "label": "if __name__ == '__main__'",
            }
        )
    return result


def _method_names(tree: ast.AST) -> set[str]:
    result = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not _call_named(node.func, {"trace_node", "contract"}):
            continue
        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            result.add(node.args[0].value)
    return result


def _contract_names(tree: ast.AST) -> set[str]:
    result = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _call_named(node.func, {"contract"}):
            continue
        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            result.add(node.args[0].value)
    return result


def _trace_label_from_decorators(decorators: list[ast.expr]) -> str | None:
    for decorator in decorators:
        if isinstance(decorator, ast.Call) and _call_named(decorator.func, {"trace_node"}):
            return _literal_first_arg(decorator)
    return None


def _literal_first_arg(node: ast.Call) -> str | None:
    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        return node.args[0].value
    return None


def _decorator_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Call):
        return _call_name(node.func)
    return _call_name(node)


def _looks_like_route(name: str) -> bool:
    return name in {"route", "get", "post", "put", "patch", "delete"} or name.endswith(
        (".route", ".get", ".post", ".put", ".patch", ".delete")
    )


def _has_main_guard(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Compare) or not isinstance(test.left, ast.Name) or test.left.id != "__name__":
            continue
        for comparator in test.comparators:
            if isinstance(comparator, ast.Constant) and comparator.value == "__main__":
                return True
    return False


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _call_named(node: ast.AST, names: set[str]) -> bool:
    call_name = _call_name(node)
    return bool(call_name and call_name.split(".")[-1] in names)


def _module_name(path: Path, project_root: Path) -> str:
    relative = path.relative_to(project_root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else path.stem


def _relative_path(path: Path, project_root: Path) -> str:
    return str(path.relative_to(project_root)).replace("\\", "/")
