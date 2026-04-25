# Security Policy

Agents Shipgate is security-adjacent release tooling, so vulnerability reports are welcome.

## Reporting

Please do not open public issues for suspected vulnerabilities. Email `security@threemoonslab.com` with:

- affected version or commit;
- reproduction steps;
- impact;
- whether the issue affects local scanning, report output, GitHub Actions usage, or package distribution.

We will acknowledge reports within 3 business days.

## Supported Versions

Pre-1.0 releases receive best-effort security fixes on the latest minor version.

## Scope

In scope:

- unexpected code execution;
- network or filesystem access that violates the documented trust model;
- unsafe parsing of manifests, OpenAPI files, MCP exports, or SDK source files;
- report output that leaks secrets beyond the provided inputs.

Out of scope:

- findings quality disagreements without a security consequence;
- vulnerabilities in downstream user tools scanned by Agents Shipgate;
- social engineering and denial-of-service against maintainers.

