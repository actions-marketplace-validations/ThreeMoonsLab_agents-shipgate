from __future__ import annotations

import hashlib
import json
from collections import Counter

from agents_shipgate.config.schema import AgentsShipgateManifest, SuppressionConfig
from agents_shipgate.core.models import Finding, ReadinessReport, ReportSummary, Severity, Tool, ToolSurfaceSummary
from agents_shipgate.core.risk_hints import is_high_risk_tool, risk_tags


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def assign_finding_ids(findings: list[Finding]) -> list[Finding]:
    seen: dict[str, int] = {}
    for finding in findings:
        base_id = finding_fingerprint(finding)
        finding.fingerprint = base_id
        seen[base_id] = seen.get(base_id, 0) + 1
        finding.id = base_id if seen[base_id] == 1 else f"{base_id}_{seen[base_id]}"
    return findings


def apply_suppressions(
    findings: list[Finding], suppressions: list[SuppressionConfig]
) -> list[Finding]:
    for finding in findings:
        match = _matching_suppression(finding, suppressions)
        if match:
            finding.suppressed = True
            finding.suppression_reason = match.reason
    return findings


def apply_severity_overrides(
    findings: list[Finding], overrides: dict[str, Severity]
) -> list[Finding]:
    for finding in findings:
        override = overrides.get(finding.check_id)
        if override:
            finding.evidence.setdefault("default_severity", finding.severity)
            finding.severity = override
    return findings


def summarize_findings(findings: list[Finding], tools: list[Tool]) -> ReportSummary:
    active = [finding for finding in findings if not finding.suppressed]
    counts = Counter(finding.severity for finding in active)
    suppressed_count = len(findings) - len(active)
    if counts["critical"] > 0:
        status = "release_blockers_detected"
    elif active:
        status = "warnings_detected"
    elif any(tool.extraction_confidence != "high" for tool in tools):
        status = "human_review_recommended"
    else:
        status = "no_release_blockers_detected"
    return ReportSummary(
        status=status,
        critical_count=counts["critical"],
        high_count=counts["high"],
        medium_count=counts["medium"],
        low_count=counts["low"],
        info_count=counts["info"],
        suppressed_count=suppressed_count,
        human_review_recommended=counts["critical"] > 0 or counts["high"] > 0 or status == "human_review_recommended",
        evidence_coverage="mixed" if _has_mixed_evidence(tools) else "static",
    )


def summarize_tool_surface(tools: list[Tool]) -> ToolSurfaceSummary:
    sources = Counter(tool.source_type for tool in tools)
    return ToolSurfaceSummary(
        total_tools=len(tools),
        high_risk_tools=sum(1 for tool in tools if is_high_risk_tool(tool)),
        sources=dict(sorted(sources.items())),
        wildcard_tools=sum(1 for tool in tools if tool.annotations.get("wildcard_tools") is True),
        missing_descriptions=sum(1 for tool in tools if not (tool.description or "").strip()),
    )


def recommended_actions(findings: list[Finding]) -> list[str]:
    active = sorted(
        [finding for finding in findings if not finding.suppressed],
        key=lambda finding: (SEVERITY_ORDER[finding.severity], finding.check_id),
    )
    actions: list[str] = []
    seen: set[str] = set()
    for finding in active:
        if finding.recommendation in seen:
            continue
        actions.append(finding.recommendation)
        seen.add(finding.recommendation)
        if len(actions) >= 8:
            break
    return actions


def tool_inventory(tools: list[Tool]) -> list[dict[str, object]]:
    return [
        {
            "name": tool.name,
            "source_type": tool.source_type,
            "source_ref": tool.source_ref,
            "risk_tags": risk_tags(tool, min_confidence="medium"),
            "risk_tag_confidence": _risk_tag_confidence(tool, min_confidence="medium"),
            "auth_scopes": tool.auth.scopes,
            "owner": tool.owner,
            "confidence": tool.extraction_confidence,
        }
        for tool in sorted(tools, key=lambda item: item.name)
    ]


def build_report(
    *,
    run_id: str,
    manifest: AgentsShipgateManifest,
    agent: dict[str, object],
    environment: dict[str, object],
    tools: list[Tool],
    findings: list[Finding],
    generated_reports: dict[str, str],
    source_warnings: list[str] | None = None,
) -> ReadinessReport:
    return ReadinessReport(
        run_id=run_id,
        project=manifest.project.model_dump(exclude_none=True),
        agent=agent,
        environment=environment,
        summary=summarize_findings(findings, tools),
        tool_surface=summarize_tool_surface(tools),
        findings=findings,
        recommended_actions=recommended_actions(findings),
        generated_reports=generated_reports,
        tool_inventory=tool_inventory(tools),
        source_warnings=source_warnings or [],
    )


def _matching_suppression(
    finding: Finding, suppressions: list[SuppressionConfig]
) -> SuppressionConfig | None:
    for suppression in suppressions:
        if suppression.check_id != finding.check_id:
            continue
        if not suppression.tool:
            return suppression
        possible_tools = {
            finding.tool_name,
            finding.tool_id,
            finding.tool_id.replace("tool:", "") if finding.tool_id else None,
        }
        if suppression.tool in possible_tools:
            return suppression
    return None


def finding_fingerprint(finding: Finding) -> str:
    identity = {
        "check_id": finding.check_id,
        "tool_name": finding.tool_name,
        "evidence": finding.evidence,
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]
    return f"fp_{digest}"


def _risk_tag_confidence(tool: Tool, min_confidence: str) -> dict[str, str]:
    threshold = _confidence_rank(min_confidence)
    by_tag: dict[str, str] = {}
    for hint in tool.risk_hints:
        if _confidence_rank(hint.confidence) < threshold:
            continue
        current = by_tag.get(hint.tag)
        if current is None or _confidence_rank(hint.confidence) > _confidence_rank(current):
            by_tag[hint.tag] = hint.confidence
    return dict(sorted(by_tag.items()))


def _confidence_rank(confidence: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(confidence, 0)


def _has_mixed_evidence(tools: list[Tool]) -> bool:
    return any(
        tool.source_type == "sdk_function" or tool.extraction_confidence != "high"
        for tool in tools
    )
