# Check Catalog

Agents Shipgate v0.1 checks are deterministic static checks. They do not certify safety, run agents, call tools, call LLMs, or verify runtime routing.

## Severity Contract

- `critical`: strict CI exits `1` unless the finding is explicitly suppressed with a reason.
- `high`: requires human review but does not fail CI by default.
- `medium`: review during release hardening.
- `low` and `info`: informational.

Only unsuppressed `critical` findings block strict mode. Suppressed findings remain in JSON with `suppressed: true` and are excluded from active severity counts.

## Evidence Coverage

- `static`: all enumerated tools came from high-confidence static sources.
- `mixed`: at least one enumerated tool came from lower-confidence enrichment, such as SDK AST extraction.

Suppressions do not change evidence coverage.

## v0.1 Checks

| Check ID | Severity | Meaning |
| --- | --- | --- |
| `SHIP-INVENTORY-NOT-ENUMERABLE` | high | No tool surface could be enumerated from the manifest inputs. |
| `SHIP-INVENTORY-WILDCARD-TOOLS` | high | A source exposes wildcard/all tools instead of an explicit allowlist. |
| `SHIP-INVENTORY-TOOL-SURFACE-TOO-LARGE` | medium | The normalized tool count exceeds the MVP review threshold. |
| `SHIP-DOC-MISSING-DESCRIPTION` | medium | A tool has no description or a description too short for reliable review. |
| `SHIP-DOC-INJECTION-RISK` | high | A tool description contains instruction-override style language. |
| `SHIP-DOC-SECRET-IN-DESCRIPTION` | high | A tool description contains a secret-like token or credential value. |
| `SHIP-SCHEMA-BROAD-FREE-TEXT` | high | A write/action-like tool accepts broad `action`, `body`, `command`, `updates`, or similar free-form input. |
| `SHIP-SCHEMA-MISSING-BOUNDS` | high | A risky numeric parameter such as `amount`, `count`, or `quantity` lacks a maximum. |
| `SHIP-SCHEMA-FREEFORM-OUTPUT` | medium | A tool returns free-form string output that may later be placed in model context. |
| `SHIP-AUTH-MISSING-SCOPE` | high | A write-like tool has no declared auth scope metadata. |
| `SHIP-AUTH-MANIFEST-BROAD-SCOPE` | high | The manifest declares broad scopes such as `*`, `admin`, or `service:*`. |
| `SHIP-AUTH-TOOL-BROAD-SCOPE` | high | A tool declares broad scopes such as `*`, `admin`, or `service:*`. |
| `SHIP-AUTH-SCOPE-COVERAGE-MISSING` | high | A tool requires scopes that are not covered by `permissions.scopes`. |
| `SHIP-SCOPE-TOOL-OUTSIDE-PURPOSE` | high | A write-capable tool contradicts a read-only declared purpose. |
| `SHIP-SCOPE-PROHIBITED-TOOL-PRESENT` | high | A tool appears to overlap with a manifest `prohibited_actions` entry. |
| `SHIP-POLICY-APPROVAL-MISSING` | critical | A high-risk tool lacks a manifest approval policy. |
| `SHIP-POLICY-CONFIRMATION-MISSING` | high | A destructive, external-write, or customer-communication tool lacks a confirmation policy. |
| `SHIP-SIDEFX-IDEMPOTENCY-MISSING` | critical/high | A risky write tool lacks idempotency evidence. Critical only when retry behavior is known. |

## Check Details

### SHIP-INVENTORY-NOT-ENUMERABLE

The scanner could not enumerate any tools from required manifest inputs. Add a local MCP JSON or OpenAPI source before relying on the report.

### SHIP-INVENTORY-WILDCARD-TOOLS

A source exposes wildcard or all-tools access. Replace it with an explicit allowlist so review can reason about the actual release surface.

### SHIP-INVENTORY-TOOL-SURFACE-TOO-LARGE

The normalized tool count exceeds the MVP review threshold. Split or reduce the surface when the report becomes too broad to review.

### SHIP-INVENTORY-LOW-CONFIDENCE-PRODUCTION-SURFACE

A production target depends on lower-confidence extraction, such as SDK AST enrichment. Declare the tools through manifest, MCP, or OpenAPI inputs.

### SHIP-DOC-MISSING-DESCRIPTION

A tool has no description or a description too short for reliable review. Add a concise capability description.

### SHIP-DOC-INJECTION-RISK

A tool description contains instruction-override-like language. Rewrite it as neutral metadata.

### SHIP-DOC-SECRET-IN-DESCRIPTION

A tool description contains a secret-like token or credential value. Remove it and rotate the exposed secret.

### SHIP-SCHEMA-BROAD-FREE-TEXT

A write/action-like tool accepts broad free-form input. Constrain the field with structured schema or enums.

### SHIP-SCHEMA-MISSING-BOUNDS

A risky numeric parameter lacks a maximum. Add a maximum or equivalent policy limit.

### SHIP-SCHEMA-FREEFORM-OUTPUT

A tool returns free-form string output that may later be placed in model context. Prefer structured output for model-consumed tool results.

### SHIP-AUTH-MISSING-SCOPE

A write or sensitive-data tool has no auth scope metadata. Declare scopes in OpenAPI, MCP, or manifest metadata.

### SHIP-AUTH-MANIFEST-BROAD-SCOPE

The manifest declares broad permission scopes such as wildcard or admin scopes. Replace them with operation-specific scopes.

### SHIP-AUTH-TOOL-BROAD-SCOPE

A tool declares broad auth scopes. Use narrower tool scopes where possible.

### SHIP-AUTH-SCOPE-COVERAGE-MISSING

A tool requires scopes that are not covered by `permissions.scopes`. Reconcile the manifest with the tool requirements.

### SHIP-SCOPE-TOOL-OUTSIDE-PURPOSE

A write-capable tool contradicts a read-only declared purpose. Remove the tool or update the declared release scope.

### SHIP-SCOPE-PROHIBITED-TOOL-PRESENT

A tool appears to overlap with a manifest `prohibited_actions` entry. Remove or narrow the tool, or revise policy/scope text.

### SHIP-POLICY-APPROVAL-MISSING

A high-risk tool lacks a declared approval policy. Add an approval policy or remove the tool from the release.

### SHIP-POLICY-CONFIRMATION-MISSING

A destructive, external-write, or customer-communication tool lacks a confirmation policy. Add confirmation policy or remove the tool.

### SHIP-SIDEFX-IDEMPOTENCY-MISSING

A risky write tool lacks idempotency evidence. Add an idempotency key, idempotent annotation, or declared idempotency policy.

## Risk Tags

Risk tags are hints, not findings by themselves. Checks consume tags with confidence thresholds.

Common tags:

- `read_only`
- `write`
- `destructive`
- `external_write`
- `financial_action`
- `customer_communication`
- `sensitive_data_access`
- `infrastructure_change`
- `code_execution`

Manual `risk_overrides` in `shipgate.yaml` are treated as high-confidence evidence. Use `remove_tags` to subtract heuristic tags that are known to be wrong for a specific tool.

## Listing Checks

Use the CLI to inspect the built-in catalog:

```bash
agents-shipgate list-checks
agents-shipgate list-checks --json
agents-shipgate explain SHIP-POLICY-APPROVAL-MISSING
```

Third-party packages can register checks through the `agents_shipgate.checks` Python entry-point group. Plugins are disabled by default because loading them imports third-party Python modules. Set `AGENTS_SHIPGATE_ENABLE_PLUGINS=1` to opt in. A plugin check should expose a callable with the same `ScanContext -> list[Finding]` shape as built-ins and may attach `AGENTS_SHIPGATE_METADATA` as either a `CheckMetadata` instance or a compatible dictionary.

## OpenAI Agents SDK Static Extraction

SDK extraction is optional enrichment. v0.1 detects Python functions decorated directly with `@function_tool`, `@function_tool(...)`, `@agents.function_tool`, or `@openai_agents.function_tool`, such as:

```python
@function_tool
def search_customer(customer_id: str) -> str:
    ...
```

The static extractor does not execute user code and intentionally does not detect dynamic wrappers, factory-created tools, `Tool.from_fn()` style objects, runtime imports, or dynamic tool lists. Declare those tools through MCP/OpenAPI inputs or manifest metadata.
