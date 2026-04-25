from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from agents_shipgate.core.models import Severity


STRICT_MODEL_CONFIG = ConfigDict(extra="forbid")


class ProjectConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    name: str
    owner: str | None = None
    repo: str | None = None


class AgentSdkConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    type: str | None = None
    language: str | None = None
    entrypoint: str | None = None
    object: str | None = None
    static_extract: bool = True
    deep_import: bool = False


class AgentConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    name: str
    sdk: AgentSdkConfig | None = None
    declared_purpose: list[str] = Field(default_factory=list)
    instructions_preview: str | None = None
    prohibited_actions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_scope_text(self) -> AgentConfig:
        if not self.declared_purpose and not self.instructions_preview:
            raise ValueError(
                "agent.declared_purpose or agent.instructions_preview is required"
            )
        return self


class EnvironmentConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    target: Literal["local", "staging", "production_like", "production"]
    promotion_from: str | None = None
    promotion_to: str | None = None


class ToolSourceConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    id: str
    type: Literal["mcp", "openapi", "openai_agents_sdk"]
    path: str | None = None
    trust: str | None = None
    mode: str | None = None
    optional: bool = False

    @model_validator(mode="after")
    def require_path_when_needed(self) -> ToolSourceConfig:
        if self.type in {"mcp", "openapi"} and not self.path:
            raise ValueError(f"tool source {self.id!r} requires path")
        return self


class PolicyToolEntry(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    tool: str
    reason: str | None = None


def _parse_policy_entries(value: Any) -> list[PolicyToolEntry]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("policy value must be a list")
    entries: list[PolicyToolEntry] = []
    for item in value:
        if isinstance(item, str):
            entries.append(PolicyToolEntry(tool=item))
        elif isinstance(item, dict):
            entries.append(PolicyToolEntry.model_validate(item))
        else:
            raise TypeError("policy entries must be strings or objects")
    return entries


class PoliciesConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    require_approval_for_tools: list[PolicyToolEntry] = Field(default_factory=list)
    require_confirmation_for_tools: list[PolicyToolEntry] = Field(default_factory=list)
    require_idempotency_for_tools: list[PolicyToolEntry] = Field(default_factory=list)

    @field_validator(
        "require_approval_for_tools",
        "require_confirmation_for_tools",
        "require_idempotency_for_tools",
        mode="before",
    )
    @classmethod
    def parse_entries(cls, value: Any) -> list[PolicyToolEntry]:
        return _parse_policy_entries(value)

    def approval_tools(self) -> set[str]:
        return {entry.tool for entry in self.require_approval_for_tools}

    def confirmation_tools(self) -> set[str]:
        return {entry.tool for entry in self.require_confirmation_for_tools}

    def idempotency_tools(self) -> set[str]:
        return {entry.tool for entry in self.require_idempotency_for_tools}


class PermissionsConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    scopes: list[str] = Field(default_factory=list)
    credential_mode: str | None = None
    notes: str | None = None


class ToolRiskOverride(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    tags: list[str] = Field(default_factory=list)
    remove_tags: list[str] = Field(default_factory=list)
    owner: str | None = None
    confidence: str = "manual"
    reason: str


class RiskOverridesConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    tools: dict[str, ToolRiskOverride] = Field(default_factory=dict)


class SuppressionConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    check_id: str
    tool: str | None = None
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_required(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("suppression reason is required")
        return value


class ChecksConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    ignore: list[SuppressionConfig] = Field(default_factory=list)
    severity_overrides: dict[str, Severity] = Field(default_factory=dict)


class CiConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    mode: Literal["advisory", "strict"] = "advisory"
    fail_on: list[Severity] | None = None
    pr_comment: bool = True
    annotations: bool = False
    upload_artifact: bool = True


class OutputConfig(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    directory: str = "agents-shipgate-reports"
    formats: list[Literal["markdown", "json"]] = Field(
        default_factory=lambda: ["markdown", "json"]
    )


class AgentsShipgateManifest(BaseModel):
    model_config = STRICT_MODEL_CONFIG

    version: Literal["0.1"]
    project: ProjectConfig
    agent: AgentConfig
    environment: EnvironmentConfig
    tool_sources: list[ToolSourceConfig]
    policies: PoliciesConfig = Field(default_factory=PoliciesConfig)
    permissions: PermissionsConfig = Field(default_factory=PermissionsConfig)
    risk_overrides: RiskOverridesConfig = Field(default_factory=RiskOverridesConfig)
    checks: ChecksConfig = Field(default_factory=ChecksConfig)
    check_severity_overrides: dict[str, Severity] = Field(default_factory=dict)
    ci: CiConfig = Field(default_factory=CiConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    @field_validator("tool_sources")
    @classmethod
    def require_tool_sources(
        cls, value: list[ToolSourceConfig]
    ) -> list[ToolSourceConfig]:
        if not value:
            raise ValueError("tool_sources must contain at least one source")
        return value

    def severity_overrides(self) -> dict[str, Severity]:
        return {
            **self.checks.severity_overrides,
            **self.check_severity_overrides,
        }
