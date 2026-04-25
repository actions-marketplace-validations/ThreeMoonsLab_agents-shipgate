from __future__ import annotations

from pathlib import Path


OPENAPI_PATTERNS = (
    "*openapi*.yaml",
    "*openapi*.yml",
    "*openapi*.json",
    "*swagger*.yaml",
    "*swagger*.yml",
    "*swagger*.json",
)
MCP_PATTERNS = (
    "*mcp*.json",
    ".agents-shipgate/*.json",
)


def discover_manifest_paths(workspace: Path) -> list[Path]:
    return sorted(
        path
        for path in workspace.rglob("shipgate.yaml")
        if ".git" not in path.parts and "agents-shipgate-reports" not in path.parts
    )


def discover_tool_sources(workspace: Path) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    seen: set[Path] = set()
    for pattern in OPENAPI_PATTERNS:
        for path in workspace.rglob(pattern):
            if _skip(path) or path in seen:
                continue
            seen.add(path)
            sources.append(
                {
                    "id": _source_id(path, "openapi"),
                    "type": "openapi",
                    "path": _relative(path, workspace),
                }
            )
    for pattern in MCP_PATTERNS:
        for path in workspace.rglob(pattern):
            if _skip(path) or path in seen:
                continue
            seen.add(path)
            sources.append(
                {
                    "id": _source_id(path, "mcp"),
                    "type": "mcp",
                    "path": _relative(path, workspace),
                }
            )
    return sources


def render_manifest_template(workspace: Path) -> str:
    sources = discover_tool_sources(workspace)
    lines = [
        'version: "0.1"',
        "",
        "project:",
        f"  name: {workspace.name}",
        "",
        "agent:",
        "  name: CHANGE_ME",
        "  declared_purpose:",
        "    - CHANGE_ME",
        "  prohibited_actions: []",
        "",
        "environment:",
        "  target: local",
        "",
        "tool_sources:",
    ]
    if sources:
        for source in sources:
            lines.extend(
                [
                    f"  - id: {source['id']}",
                    f"    type: {source['type']}",
                    f"    path: {source['path']}",
                ]
            )
    else:
        lines.extend(
            [
                "  - id: CHANGE_ME",
                "    type: openapi",
                "    path: CHANGE_ME.yaml",
            ]
        )
    lines.extend(
        [
            "",
            "policies:",
            "  require_approval_for_tools: []",
            "  require_confirmation_for_tools: []",
            "  require_idempotency_for_tools: []",
            "",
            "permissions:",
            "  scopes: []",
            "",
            "ci:",
            "  mode: advisory",
            "",
            "output:",
            "  directory: agents-shipgate-reports",
            "  formats:",
            "    - markdown",
            "    - json",
            "",
        ]
    )
    return "\n".join(lines)


def _skip(path: Path) -> bool:
    return any(part in {".git", "agents-shipgate-reports", "__pycache__"} for part in path.parts)


def _relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _source_id(path: Path, source_type: str) -> str:
    stem = path.stem.lower().replace("-", "_").replace(".", "_")
    return f"{source_type}_{stem}"

