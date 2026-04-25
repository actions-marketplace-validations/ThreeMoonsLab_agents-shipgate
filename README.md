# Agents Shipgate

![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue)

**The pre-flight check your agent release is missing.**

Agents Shipgate is an **Agent Release Gate**: a static, manifest-first scanner that catches risky agent tool configurations at PR time. It reads `shipgate.yaml`, local MCP tool exports, local OpenAPI specs, and optional OpenAI Agents SDK AST metadata, then writes Markdown and JSON reports for release review.

An agent release gate is the static, manifest-based pre-flight check that runs on agent PRs before promotion to staging or production. Today, most agent teams ship without one.

## Findings Gallery

The bundled support-refund fixture demonstrates the kind of release risks Agents Shipgate is designed to surface:

```text
## Agents Shipgate

Status: Release blockers detected
Critical: 2 - High: 13 - Medium: 1
Human review: recommended

Top findings:
1. stripe.create_refund lacks a declared approval policy
2. stripe.create_refund lacks idempotency evidence
3. Manifest declares broad permission scopes
```

- `stripe.create_refund` lacks a declared approval policy, so a financial action could ship without an explicit human review gate.
- `stripe.create_refund.amount` lacks a maximum bound, weakening blast-radius control.
- `stripe.create_refund` lacks idempotency evidence while retry behavior is known, risking duplicate refunds.
- `wildcard_mcp_tools.*` exposes a wildcard tool surface, making review incomplete.
- `gmail.send_customer_email` overlaps a prohibited external-communication action without a matching confirmation policy.

## Why Not Just...

| Alternative | Gap Agents Shipgate Covers |
| --- | --- |
| Unit tests | Tests usually validate code paths, not the released tool surface and declared policies. |
| Code review | Reviewers miss generated specs, MCP exports, broad scopes, and missing approval policies. |
| Runtime traces | Useful later, but they arrive after behavior exists. Agents Shipgate runs before promotion. |
| Nothing | Tool-surface drift becomes a production surprise. |

## Quickstart

PyPI and GitHub Marketplace publication are planned for the first public release. Until then, use a local source checkout:

```bash
python -m pip install -e ".[dev]"
agents-shipgate init --workspace . --write
agents-shipgate doctor --config shipgate.yaml
agents-shipgate scan --config shipgate.yaml
```

Try the bundled fixture:

```bash
agents-shipgate scan --config samples/support_refund_agent/shipgate.yaml
```

## CI Behavior

CI is advisory by default:

```bash
agents-shipgate scan --config shipgate.yaml --ci-mode advisory
```

Strict mode exits with code `1` only when unsuppressed critical findings exist:

```bash
agents-shipgate scan --config shipgate.yaml --ci-mode strict
```

Teams can override severities and CI failure thresholds:

```yaml
checks:
  severity_overrides:
    SHIP-AUTH-MISSING-SCOPE: critical
ci:
  fail_on:
    - critical
    - high
```

## Who It Is For

| Buyer | Pain | Pitch | Next step |
| --- | --- | --- | --- |
| Platform engineer shipping a first production agent | "I don't know what I don't know." | Audits manifest and tool schemas for release risks code review misses. | Run `agents-shipgate init --workspace . --write`. |
| Security or GRC reviewer | "Agents bypass existing controls." | Creates a static tool-surface audit trail for review. | Review the [check catalog](docs/checks.md). |
| AI PM with a shipping deadline | "Security review blocks us late." | Gives teams self-serve pre-review before formal approval. | Scan the [support-refund fixture](samples/support_refund_agent/shipgate.yaml). |

## Trust Model

**Agents Shipgate does not import user code, run agents, call tools, call LLMs, connect to MCP servers, make network calls, or collect telemetry by default.**

See [Trust model](docs/trust-model.md) and [Security policy](SECURITY.md) for the default local-only guarantees and disclosure process.

## GitHub Action

The action installs from the tagged source by default, so it can be used before PyPI publication once the GitHub repository and tag exist:

```yaml
name: Agents Shipgate

on:
  pull_request:

permissions:
  contents: read

jobs:
  agents-shipgate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
      - id: agents-shipgate
        uses: ThreeMoonsLab/agents-shipgate@v0.1.0
        with:
          config: shipgate.yaml
          ci_mode: advisory
          output_dir: agents-shipgate-reports
```

For PR comments, add `pull-requests: write` and set `pr_comment: "true"`. The action exposes `status`, `critical_count`, `high_count`, `medium_count`, `report_json`, `report_markdown`, and `exit_code` outputs for downstream workflow steps.

Set `shipgate_version` only after the package is published to PyPI.

## Pricing And Open Source Stance

Agents Shipgate is and will remain free OSS for individuals and teams running it on their own infrastructure. The core manifest-first scanner, built-in checks, Markdown report, and JSON report are intended to remain open source. We do not collect telemetry and do not require an account.

If hosted dashboards, SSO, org-wide baselines, approval workflows, or trace-based evidence emerge, they should live in a separate optional product rather than moving core OSS functionality behind a paywall.

## Docs

- [Agent Release Gate category](docs/category.md)
- [Manifest v0.1](docs/manifest-v0.1.md)
- [Check catalog](docs/checks.md)
- [Trust model](docs/trust-model.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Integration recipes](docs/integrations.md)
- [Distribution plan](docs/distribution.md)
- [JSON report schema](docs/report-schema.v0.1.json)
