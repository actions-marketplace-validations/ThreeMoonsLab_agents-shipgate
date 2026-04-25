from __future__ import annotations

from pathlib import Path

from agents_shipgate.core.models import ReadinessReport


def write_json_report(report: ReadinessReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2, exclude_none=False), encoding="utf-8")
