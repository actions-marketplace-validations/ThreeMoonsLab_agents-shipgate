from pathlib import Path

import yaml


def test_github_script_reads_output_dir_from_env():
    text = Path("action.yml").read_text(encoding="utf-8")

    assert "OUTPUT_DIR: ${{ inputs.output_dir }}" in text
    assert "process.env.OUTPUT_DIR" in text
    assert 'path.join("${{ inputs.output_dir }}", "report.json")' not in text


def test_action_installs_from_source_when_no_pypi_version_is_set():
    text = Path("action.yml").read_text(encoding="utf-8")

    assert 'default: ""' in text
    assert 'python -m pip install "${GITHUB_ACTION_PATH}"' in text
    assert 'agents-shipgate==${SHIPGATE_VERSION}' in text


def test_action_has_marketplace_metadata_and_outputs():
    data = yaml.safe_load(Path("action.yml").read_text(encoding="utf-8"))

    assert data["name"] == "Agents Shipgate"
    assert data["author"] == "ThreeMoonsLab"
    assert data["branding"] == {"icon": "shield", "color": "blue"}
    assert {"status", "critical_count", "high_count", "report_json", "exit_code"} <= set(
        data["outputs"]
    )


def test_action_preserves_reports_before_applying_exit_code():
    text = Path("action.yml").read_text(encoding="utf-8")

    assert "id: scan" in text
    assert "exit 0" in text
    assert "Apply Agents Shipgate exit code" in text
    assert "steps.scan.outputs.exit_code" in text
    assert "FAIL_ON: ${{ inputs.fail_on }}" in text


def test_marketplace_action_repo_has_no_workflow_files():
    workflow_dir = Path(".github/workflows")

    assert not workflow_dir.exists() or list(workflow_dir.glob("*")) == []
