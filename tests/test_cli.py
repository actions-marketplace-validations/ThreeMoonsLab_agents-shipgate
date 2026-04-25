from typer.testing import CliRunner

from agents_shipgate.cli.main import app


runner = CliRunner()


def test_cli_advisory_exits_zero(tmp_path):
    result = runner.invoke(
        app,
        [
            "scan",
            "--config",
            "samples/support_refund_agent/shipgate.yaml",
            "--out",
            str(tmp_path),
            "--ci-mode",
            "advisory",
        ],
    )

    assert result.exit_code == 0
    assert "Agents Shipgate v0.1" in result.output
    assert "release_blockers_detected" in result.output


def test_cli_strict_exits_one(tmp_path):
    result = runner.invoke(
        app,
        [
            "scan",
            "--config",
            "samples/support_refund_agent/shipgate.yaml",
            "--out",
            str(tmp_path),
            "--ci-mode",
            "strict",
        ],
    )

    assert result.exit_code == 1
    assert "Exit code: 1" in result.output


def test_cli_invalid_config_exits_two(tmp_path):
    bad_config = tmp_path / "shipgate.yaml"
    bad_config.write_text("version: '0.1'\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", "--config", str(bad_config)])

    assert result.exit_code == 2
    assert "Config error:" in result.output


def test_cli_input_parse_error_exits_three(tmp_path):
    config = tmp_path / "shipgate.yaml"
    config.write_text(
        """
version: "0.1"
project:
  name: parse-error
agent:
  name: parse-error-agent
  declared_purpose:
    - test
environment:
  target: local
tool_sources:
  - id: missing
    type: mcp
    path: missing.json
""",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["scan", "--config", str(config)])

    assert result.exit_code == 3
    assert "Input parsing error:" in result.output


def test_cli_list_checks_outputs_catalog():
    result = runner.invoke(app, ["list-checks"])

    assert result.exit_code == 0
    assert "SHIP-POLICY-APPROVAL-MISSING" in result.output


def test_cli_explain_outputs_check_details():
    result = runner.invoke(app, ["explain", "SHIP-POLICY-APPROVAL-MISSING"])

    assert result.exit_code == 0
    assert "Default severity: critical" in result.output
    assert "Rationale:" in result.output


def test_cli_explain_unknown_check_suggests_close_match():
    result = runner.invoke(app, ["explain", "SHIP-POLICY-APPROVAL-MISSNG"])

    assert result.exit_code == 2
    assert "Did you mean SHIP-POLICY-APPROVAL-MISSING?" in result.output


def test_cli_init_prints_manifest_template(tmp_path):
    (tmp_path / "api.openapi.yaml").write_text(
        "openapi: 3.1.0\ninfo:\n  title: T\n  version: '1'\npaths: {}\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["init", "--workspace", str(tmp_path)])

    assert result.exit_code == 0
    assert "tool_sources:" in result.output
    assert "api.openapi.yaml" in result.output


def test_cli_doctor_enumerates_sources():
    result = runner.invoke(
        app,
        [
            "doctor",
            "--config",
            "samples/support_refund_agent/shipgate.yaml",
        ],
    )

    assert result.exit_code == 0
    assert "Total tools:" in result.output
    assert "support_openapi" in result.output


def test_cli_scan_accepts_workspace(tmp_path):
    result = runner.invoke(
        app,
        [
            "scan",
            "--workspace",
            "samples/support_refund_agent",
            "--out",
            str(tmp_path),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert "Project: support-refund-agent" in result.output


def test_cli_verbose_json_logs(tmp_path):
    result = runner.invoke(
        app,
        [
            "scan",
            "--config",
            "samples/support_refund_agent/shipgate.yaml",
            "--out",
            str(tmp_path),
            "--format",
            "json",
            "--verbose",
        ],
        env={"AGENTS_SHIPGATE_LOG_FORMAT": "json"},
    )

    assert result.exit_code == 0
    assert '"message": "loaded sources"' in result.output
    assert '"source_count": 4' in result.output
