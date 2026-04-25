# Trust Model

Agents Shipgate v0.1 is designed as a local static scanner.

## Default Invariants

By default Agents Shipgate does not:

- import user project code;
- execute agent code;
- call tools;
- call LLMs;
- connect to MCP servers;
- resolve remote or local filesystem OpenAPI `$ref` values;
- make network calls;
- shell out to subprocesses;
- import third-party check plugins;
- collect telemetry.

## Input Parsing

- YAML is parsed with `yaml.safe_load`.
- OpenAPI `$ref` resolution only follows internal JSON pointers beginning with `#/`.
- `file://`, `http://`, and other external `$ref` values are left as inert schema values.
- OpenAI Agents SDK enrichment uses `ast.parse` only. It does not import or execute Python modules.
- Third-party check plugins are disabled by default. Setting `AGENTS_SHIPGATE_ENABLE_PLUGINS=1` opts into importing and running installed plugin entry points.

## Failure Policy

Declared input sources should fail closed when parsing cannot complete. Required source parse errors return CLI exit code `3`. Optional source parse errors are recorded as source warnings and the scan continues.

## Known Limits

Static analysis does not verify runtime tool routing, actual model behavior, external authorization enforcement, tool execution results, or prompt-injection resistance of returned tool content.

Verbose logs may include tool names, source counts, and risk-hint evidence. Treat `--verbose` output as release-review metadata.

## Diagnostics

Use `agents-shipgate doctor --config shipgate.yaml` to validate the manifest and enumerate declared sources without running checks. Use `agents-shipgate scan --verbose` for per-source and risk-hint debug logs. Set `AGENTS_SHIPGATE_LOG_FORMAT=json` to emit structured JSON logs to stderr.
