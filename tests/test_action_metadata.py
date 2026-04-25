from pathlib import Path


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
