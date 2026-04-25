from __future__ import annotations

import re

from agents_shipgate.checks.base import tool_finding
from agents_shipgate.core.context import ScanContext


SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9_]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]
LABELED_SECRET_PATTERN = re.compile(
    r"(?i)\b(password|secret|token|api[_-]?key)\s*[:=]\s*([A-Za-z0-9_./+=-]{20,})"
)

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore (all )?(previous|prior) instructions"),
    re.compile(r"(?i)(ignore|override|replace).{0,40}(system prompt|developer message|instructions)"),
    re.compile(r"(?i)(system prompt|developer message).{0,40}(ignore|override|replace)"),
    re.compile(r"(?i)you are now"),
]


def run(context: ScanContext):
    findings = []
    for tool in context.tools:
        description = tool.description or ""
        if not description.strip() or len(description.strip()) < 20:
            findings.append(
                tool_finding(
                    tool=tool,
                    check_id="SHIP-DOC-MISSING-DESCRIPTION",
                    title=f"{tool.name} has a missing or too-short description",
                    severity="medium",
                    category="documentation",
                    evidence={"description_length": len(description.strip())},
                    confidence="high",
                    recommendation=f"Add a clear tool description for {tool.name} so the agent and reviewers can understand intended use.",
                    context=context,
                )
            )
        if _contains_secret_like_text(description):
            findings.append(
                tool_finding(
                    tool=tool,
                    check_id="SHIP-DOC-SECRET-IN-DESCRIPTION",
                    title=f"{tool.name} description appears to contain a secret",
                    severity="high",
                    category="security",
                    evidence={"matched": "secret-like pattern"},
                    confidence="high",
                    recommendation=f"Remove secret-like values from the {tool.name} description and rotate any exposed credentials.",
                    context=context,
                )
            )
        if _contains_injection_like_text(description):
            findings.append(
                tool_finding(
                    tool=tool,
                    check_id="SHIP-DOC-INJECTION-RISK",
                    title=f"{tool.name} description contains instruction-like text",
                    severity="high",
                    category="security",
                    evidence={"matched": "prompt-injection-like pattern"},
                    confidence="medium",
                    recommendation=f"Rewrite the {tool.name} description as capability metadata, not instructions to the model.",
                    context=context,
                )
            )
    return findings


def _contains_secret_like_text(description: str) -> bool:
    if any(pattern.search(description) for pattern in SECRET_PATTERNS):
        return True
    match = LABELED_SECRET_PATTERN.search(description)
    if not match:
        return False
    value = match.group(2)
    return _looks_like_secret_value(value)


def _looks_like_secret_value(value: str) -> bool:
    if len(value) < 20:
        return False
    has_alpha = any(char.isalpha() for char in value)
    has_digit = any(char.isdigit() for char in value)
    has_secret_alphabet = all(char.isalnum() or char in "_./+=-" for char in value)
    return has_alpha and has_digit and has_secret_alphabet


def _contains_injection_like_text(description: str) -> bool:
    return any(pattern.search(description) for pattern in INJECTION_PATTERNS)
