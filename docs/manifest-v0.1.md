# `shipgate.yaml` v0.1

`shipgate.yaml` is mandatory and is the source of truth for v0.1.

## Minimal Manifest

```yaml
version: "0.1"

project:
  name: support-refund-agent

agent:
  name: refund-assistant
  declared_purpose:
    - answer refund policy questions

environment:
  target: production_like

tool_sources:
  - id: support_openapi
    type: openapi
    path: specs/support-tools.openapi.yaml
```

## Supported Tool Sources

- `openapi`: local OpenAPI 3.0/3.1 YAML or JSON.
- `mcp`: local exported MCP tools JSON.
- `openai_agents_sdk`: optional static Python AST extraction.

When two sources declare the same tool name, Agents Shipgate keeps the higher-fidelity source and emits a source warning. Current precedence is OpenAPI, then MCP JSON, then SDK static extraction.

## MCP Tools JSON Contract

Preferred shape:

```json
{
  "tools": [
    {
      "name": "support.search_kb",
      "description": "Search support knowledge base articles.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": { "type": "string" }
        },
        "required": ["query"]
      },
      "outputSchema": {},
      "annotations": {
        "readOnlyHint": true,
        "idempotentHint": true
      },
      "auth": {
        "scopes": ["support:kb:read"]
      },
      "owner": "support-platform"
    }
  ]
}
```

The root may also be a JSON array of tool objects.

Wildcard exposure can be represented as:

```json
{ "tools": "*", "wildcard": true }
```

If `wildcard: true` is combined with a non-empty `tools` array, wildcard precedence is used, explicit tools are ignored, and the loader emits a source warning.

## Suppressions

Suppressions require a reason and match by `check_id` plus optional `tool` name.

```yaml
checks:
  ignore:
    - check_id: SHIP-SCHEMA-BROAD-FREE-TEXT
      tool: support.search_kb
      reason: "Search query intentionally accepts free text."
```

Suppressed findings remain in the JSON report with `suppressed: true`.

## Severity Overrides

Teams can re-rank built-in checks without forking the scanner:

```yaml
checks:
  severity_overrides:
    SHIP-DOC-INJECTION-RISK: low
    SHIP-AUTH-MISSING-SCOPE: critical
```

For compatibility with early design-partner manifests, top-level `check_severity_overrides` is also accepted and is applied after `checks.severity_overrides`.

## Risk Overrides

Use `risk_overrides` to add high-confidence manual tags, set owners, or remove known-wrong heuristic tags.

```yaml
risk_overrides:
  tools:
    refund_status_lookup:
      tags: ["read_only"]
      remove_tags: ["financial_action"]
      reason: "This endpoint only reads refund status."
```

## CI Failure Policy

`ci.mode: advisory` exits `0` by default. `ci.mode: strict` fails on unsuppressed `critical` findings by default.

Override the failing severities with `ci.fail_on`:

```yaml
ci:
  mode: strict
  fail_on:
    - critical
    - high
```

The CLI equivalent is:

```bash
agents-shipgate scan --config shipgate.yaml --fail-on critical,high
```

## Finding Fingerprints

Each finding includes a stable `fingerprint` computed from:

- `check_id`
- `tool_name`
- sorted `evidence`

This is the baseline/diff key for future workflows. The human-readable `id` is derived from the same fingerprint and may receive a numeric suffix only if identical findings collide in one report.

## Strict Field Validation

Manifest schema models reject unknown keys. This is intentional: a typo such as `declared_purpoze` should fail fast instead of silently weakening the release review.
