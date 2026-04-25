# Agents Shipgate v0.1 Decisions

## Locked MVP Defaults

- Runtime: Python 3.12.
- Package layout: `src/agents_shipgate`.
- CLI framework: Typer.
- Config: mandatory `shipgate.yaml`.
- Input sources: local MCP tools JSON and local OpenAPI 3.x specs.
- SDK support: optional static AST enrichment only.
- Execution model: local-only, no network, no user-code import by default.
- Check engine: deterministic registry.
- Severity model: no score; strict CI fails only on unsuppressed critical findings.
- Reports: Markdown and JSON.
- Telemetry: none.
- Manifest version: `version: "0.1"`.

## Deferred

- Deep import execution.
- Remote MCP `tools/list`.
- Trace ingestion.
- LLM-assisted classification.
- HTML, SARIF, baseline diff, hosted dashboard, policy packs, runtime gateway.
