from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agents_shipgate.config.schema import AgentsShipgateManifest
from agents_shipgate.core.models import Agent, OpenAIApiArtifacts, Tool


@dataclass
class ScanContext:
    manifest: AgentsShipgateManifest
    agent: Agent
    tools: list[Tool]
    config_path: Path
    api_artifacts: OpenAIApiArtifacts | None = None
