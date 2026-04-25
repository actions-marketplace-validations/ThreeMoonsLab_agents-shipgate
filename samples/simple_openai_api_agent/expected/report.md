# Agents Shipgate Report

Project: simple-openai-api-agent
Agent: api-refund-assistant
Target: production_like

Result: REVIEW - static findings require human review.
Status: Warnings detected
Critical: 0
High: 15
Medium: 5
Low: 0
Suppressed: 0
Evidence coverage: static
Human review: recommended

## Top Findings

1. create_refund function schema is not strict enough
   Evidence: issues=\['missing_strict_true', 'additional_properties_not_false', 'properties_missing_from_required:amount,reason', 'risky_field_unbounded:amount'\]; risk_tags=\['financial_action', 'write'\]
   Recommendation: Make create_refund a strict function schema: object parameters, additionalProperties=false, complete required list, and bounded risky fields.

2. send_customer_email function schema is not strict enough
   Evidence: issues=\['broad_free_text:message'\]; risk_tags=\['customer_communication', 'external_write', 'write'\]
   Recommendation: Make send_customer_email a strict function schema: object parameters, additionalProperties=false, complete required list, and bounded risky fields.

3. create_refund may be retried without idempotency evidence
   Evidence: retry_policy={'max_attempts': 2}; risk_tags=\['financial_action', 'write'\]
   Recommendation: Add idempotency evidence for create_refund or avoid retrying this side effect.

4. send_customer_email may be retried without idempotency evidence
   Evidence: retry_policy={'max_attempts': 2}; risk_tags=\['customer_communication', 'external_write', 'write'\]
   Recommendation: Add idempotency evidence for send_customer_email or avoid retrying this side effect.

5. Prompt says read-only or advise-only while write/high-risk tools are enabled
   Evidence: tools=\['create_refund', 'send_customer_email'\]
   Recommendation: Align prompt scope with enabled tools or remove write/high-risk tools.

## Recommended Next Actions

- Make create_refund a strict function schema: object parameters, additionalProperties=false, complete required list, and bounded risky fields.
- Make send_customer_email a strict function schema: object parameters, additionalProperties=false, complete required list, and bounded risky fields.
- Add idempotency evidence for create_refund or avoid retrying this side effect.
- Add idempotency evidence for send_customer_email or avoid retrying this side effect.
- Align prompt scope with enabled tools or remove write/high-risk tools.
- Declare auth scopes for create_refund in OpenAPI, MCP metadata, or the manifest before release review.
- Declare auth scopes for send_customer_email in OpenAPI, MCP metadata, or the manifest before release review.
- Declare an owner for each high-risk production tool in risk_overrides.tools.

## Tool Surface Summary

- Total tools: 2
- High-risk tools: 2
- Wildcard tools: 0
- Missing descriptions: 0
- Sources: openai_api=2

## OpenAI API Surface Summary

- Prompt files: 1
- Tool files: 1
- Response formats: 1
- Model config present: True
- Test cases: 1
- Trace samples: 1
- Policy rule files: 1

## Findings By Category

### Api

- HIGH: SHIP-API-FUNCTION-SCHEMA-STRICTNESS [create_refund] - create_refund function schema is not strict enough
- HIGH: SHIP-API-FUNCTION-SCHEMA-STRICTNESS [send_customer_email] - send_customer_email function schema is not strict enough
- HIGH: SHIP-API-OPERATIONAL-READINESS [create_refund] - create_refund may be retried without idempotency evidence
- HIGH: SHIP-API-OPERATIONAL-READINESS [send_customer_email] - send_customer_email may be retried without idempotency evidence
- HIGH: SHIP-API-PROMPT-TOOL-SCOPE-MISMATCH - Prompt says read-only or advise-only while write/high-risk tools are enabled
- MEDIUM: SHIP-API-OPERATIONAL-READINESS - OpenAI API flow lacks timeout metadata
- MEDIUM: SHIP-API-OPERATIONAL-READINESS - Trace sample shows create_refund without approval
- MEDIUM: SHIP-API-OPERATIONAL-READINESS [create_refund] - create_refund lacks success/failure output modeling
- MEDIUM: SHIP-API-PROMPT-TOOL-SCOPE-MISMATCH - Prompt lacks approval/confirmation language for high-risk tools
- MEDIUM: SHIP-API-STRUCTURED-OUTPUT-READINESS - Response format schemas/refund_decision.schema.json is under-specified

### Auth

- HIGH: SHIP-AUTH-MISSING-SCOPE [create_refund] - create_refund lacks declared auth scopes
- HIGH: SHIP-AUTH-MISSING-SCOPE [send_customer_email] - send_customer_email lacks declared auth scopes

### Manifest

- HIGH: SHIP-MANIFEST-HIGH-RISK-OWNER-MISSING [create_refund] - create_refund is high-risk but has no owner
- HIGH: SHIP-MANIFEST-HIGH-RISK-OWNER-MISSING [send_customer_email] - send_customer_email is high-risk but has no owner

### Schema

- HIGH: SHIP-SCHEMA-BROAD-FREE-TEXT [send_customer_email] - send_customer_email accepts broad free-form action input
- HIGH: SHIP-SCHEMA-MISSING-BOUNDS [create_refund] - create_refund.amount has no maximum bound

### Scope

- HIGH: SHIP-SCOPE-PROHIBITED-TOOL-PRESENT [create_refund] - create_refund appears to overlap with a prohibited action
- HIGH: SHIP-SCOPE-PROHIBITED-TOOL-PRESENT [send_customer_email] - send_customer_email appears to overlap with a prohibited action

### Side Effects

- HIGH: SHIP-SIDEFX-IDEMPOTENCY-MISSING [create_refund] - create_refund lacks idempotency evidence
- HIGH: SHIP-SIDEFX-IDEMPOTENCY-MISSING [send_customer_email] - send_customer_email lacks idempotency evidence

## Appendix: Normalized Tool Inventory

| Tool | Source | Risk Tags | Risk Confidence | Auth Scopes | Owner |
| --- | --- | --- | --- | --- | --- |
| create_refund | openai_api | financial_action, write | financial_action=high, write=medium | - | - |
| send_customer_email | openai_api | customer_communication, external_write, write | customer_communication=high, external_write=high, write=medium | - | - |


## Disclaimer

Agents Shipgate is an advisory release-readiness scanner. It does not certify agent safety or compliance. Findings are based on static configuration, declared policies, tool schemas, and optional SDK metadata. Runtime behavior, actual tool routing, and output interpretation are not verified.
