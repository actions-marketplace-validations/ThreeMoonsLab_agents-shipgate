# Agents Shipgate Report

Project: support-refund-agent
Agent: refund-assistant
Target: production_like

Result: BLOCKED - release blockers detected.
Status: Release blockers detected
Critical: 2
High: 13
Medium: 1
Low: 0
Suppressed: 0
Evidence coverage: mixed
Human review: recommended

## Top Findings

1. stripe.create_refund lacks a declared approval policy
   Evidence: risk_tags=\['external_write', 'financial_action', 'write'\]; policy_match=None
   Recommendation: Declare an approval policy for stripe.create_refund or remove this tool from the release.

2. stripe.create_refund lacks idempotency evidence
   Evidence: risk_tags=\['external_write', 'financial_action', 'write'\]; retry_policy_known=True
   Recommendation: Add an idempotency key, idempotent annotation, or declared idempotency policy for stripe.create_refund.

3. Manifest declares broad permission scopes
   Evidence: scopes=\['stripe:*'\]
   Recommendation: Replace broad manifest permission scopes with the narrowest scopes needed for this release.

4. shopify.cancel_order requires scopes not declared in the manifest
   Evidence: tool_scopes=\['shopify:orders:write'\]; manifest_scopes=\['zendesk:tickets:read', 'zendesk:tickets:write', 'stripe:*'\]; missing_scopes=\['shopify:orders:write'\]
   Recommendation: Add the required scopes for shopify.cancel_order to permissions.scopes or narrow the tool's declared auth requirements.

5. support.search_kb requires scopes not declared in the manifest
   Evidence: tool_scopes=\['support:kb:read'\]; manifest_scopes=\['zendesk:tickets:read', 'zendesk:tickets:write', 'stripe:*'\]; missing_scopes=\['support:kb:read'\]
   Recommendation: Add the required scopes for support.search_kb to permissions.scopes or narrow the tool's declared auth requirements.

## Recommended Next Actions

- Declare an approval policy for stripe.create_refund or remove this tool from the release.
- Add an idempotency key, idempotent annotation, or declared idempotency policy for stripe.create_refund.
- Replace broad manifest permission scopes with the narrowest scopes needed for this release.
- Add the required scopes for shopify.cancel_order to permissions.scopes or narrow the tool's declared auth requirements.
- Add the required scopes for support.search_kb to permissions.scopes or narrow the tool's declared auth requirements.
- Add the required scopes for gmail.send_customer_email to permissions.scopes or narrow the tool's declared auth requirements.
- Replace wildcard tool exposure with an explicit tool allowlist before release review.
- Declare a user confirmation policy for stripe.create_refund or remove this action from the release.

## Source Warnings

- MCP source declares wildcard tool exposure

## Tool Surface Summary

- Total tools: 8
- High-risk tools: 3
- Wildcard tools: 1
- Missing descriptions: 0
- Sources: mcp=3, openapi=4, sdk_function=1

## Findings By Category

### Auth

- HIGH: SHIP-AUTH-MANIFEST-BROAD-SCOPE - Manifest declares broad permission scopes
- HIGH: SHIP-AUTH-SCOPE-COVERAGE-MISSING [gmail.send_customer_email] - gmail.send_customer_email requires scopes not declared in the manifest
- HIGH: SHIP-AUTH-SCOPE-COVERAGE-MISSING [shopify.cancel_order] - shopify.cancel_order requires scopes not declared in the manifest
- HIGH: SHIP-AUTH-SCOPE-COVERAGE-MISSING [support.search_kb] - support.search_kb requires scopes not declared in the manifest

### Inventory

- HIGH: SHIP-INVENTORY-WILDCARD-TOOLS [wildcard_mcp_tools.*] - Wildcard tool exposure declared

### Policy

- CRITICAL: SHIP-POLICY-APPROVAL-MISSING [stripe.create_refund] - stripe.create_refund lacks a declared approval policy
- HIGH: SHIP-POLICY-CONFIRMATION-MISSING [gmail.send_customer_email] - gmail.send_customer_email lacks a declared confirmation policy
- HIGH: SHIP-POLICY-CONFIRMATION-MISSING [stripe.create_refund] - stripe.create_refund lacks a declared confirmation policy

### Schema

- HIGH: SHIP-SCHEMA-BROAD-FREE-TEXT [gmail.send_customer_email] - gmail.send_customer_email accepts broad free-form action input
- HIGH: SHIP-SCHEMA-BROAD-FREE-TEXT [zendesk.update_ticket] - zendesk.update_ticket accepts broad free-form action input
- HIGH: SHIP-SCHEMA-MISSING-BOUNDS [stripe.create_refund] - stripe.create_refund.amount has no maximum bound
- MEDIUM: SHIP-SCHEMA-FREEFORM-OUTPUT [send_email_preview] - send_email_preview returns free-form text output

### Scope

- HIGH: SHIP-SCOPE-PROHIBITED-TOOL-PRESENT [gmail.send_customer_email] - gmail.send_customer_email appears to overlap with a prohibited action
- HIGH: SHIP-SCOPE-PROHIBITED-TOOL-PRESENT [stripe.create_refund] - stripe.create_refund appears to overlap with a prohibited action

### Side Effects

- CRITICAL: SHIP-SIDEFX-IDEMPOTENCY-MISSING [stripe.create_refund] - stripe.create_refund lacks idempotency evidence
- HIGH: SHIP-SIDEFX-IDEMPOTENCY-MISSING [gmail.send_customer_email] - gmail.send_customer_email lacks idempotency evidence

## Appendix: Normalized Tool Inventory

| Tool | Source | Risk Tags | Risk Confidence | Auth Scopes | Owner |
| --- | --- | --- | --- | --- | --- |
| gmail.send_customer_email | mcp | customer_communication, external_write | customer_communication=medium, external_write=medium | gmail:send | support-platform |
| refund_status_lookup | openapi | read_only | read_only=high | - | - |
| send_email_preview | sdk_function | read_only | read_only=high | - | - |
| shopify.cancel_order | openapi | destructive, write | destructive=high, write=high | shopify:orders:write | - |
| stripe.create_refund | openapi | external_write, financial_action, write | external_write=high, financial_action=high, write=high | stripe:refunds:write | payments-platform |
| support.search_kb | mcp | read_only | read_only=high | support:kb:read | support-platform |
| wildcard_mcp_tools.* | mcp | - | - | - | - |
| zendesk.update_ticket | openapi | write | write=high | zendesk:tickets:write | - |


## Disclaimer

Agents Shipgate is an advisory release-readiness scanner. It does not certify agent safety or compliance. Findings are based on static configuration, declared policies, tool schemas, and optional SDK metadata. Runtime behavior, actual tool routing, and output interpretation are not verified in v0.1.
