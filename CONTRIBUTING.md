# Contributing

Yes, please contribute.

## Local Setup

```bash
python -m pip install -e ".[dev]"
pytest
```

## Useful Commands

```bash
agents-shipgate init --workspace samples/support_refund_agent
agents-shipgate doctor --config samples/support_refund_agent/shipgate.yaml
agents-shipgate scan --config samples/support_refund_agent/shipgate.yaml
agents-shipgate list-checks
```

## Contribution Areas

- new deterministic checks;
- loader hardening and OpenAPI edge cases;
- docs and integration recipes;
- false-positive reduction tests;
- report/schema compatibility tests.

## Check Contributions

Checks should be deterministic, explainable, and covered by tests. Avoid LLM calls, network calls, user-code import, or runtime tool execution.

Each new check should include catalog metadata, a test fixture, and documentation in `docs/checks.md`.

## Adding A Check End To End

1. Create or update a module under `src/agents_shipgate/checks/`.
2. Implement a pure function with the shape `run(context: ScanContext) -> list[Finding]`.
3. Use `tool_finding(...)` or `agent_finding(...)` from `src/agents_shipgate/checks/base.py` so evidence, recommendations, and source references stay consistent.
4. Register the function and metadata in `src/agents_shipgate/checks/registry.py`.
5. Add a unit test that proves the check fires and a false-positive test that proves it does not fire on a nearby safe case.
6. Add the check ID, severity, and plain-language meaning to `docs/checks.md`.
7. Run:

```bash
pytest
agents-shipgate list-checks
agents-shipgate explain YOUR-CHECK-ID
```

Good checks are narrow, evidence-backed, and easy to suppress with a reason when a team has intentionally accepted the risk.
