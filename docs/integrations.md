# Integration Recipes

## GitHub Actions

The public Marketplace wrapper is planned for the first tagged release. The
action installs from its tagged source by default; set `shipgate_version` only
after the package is published to PyPI.

```yaml
name: Agents Shipgate

on:
  pull_request:

permissions:
  contents: read

jobs:
  agents-shipgate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
      - id: agents-shipgate
        uses: ThreeMoonsLab/agents-shipgate@v0.1.0
        with:
          config: shipgate.yaml
          ci_mode: advisory
```

To post PR comments, set:

```yaml
permissions:
  contents: read
  pull-requests: write

with:
  pr_comment: "true"
```

Action outputs:

| Output | Meaning |
| --- | --- |
| `status` | Report summary status, such as `release_blockers_detected`. |
| `critical_count` | Unsuppressed critical finding count. |
| `high_count` | Unsuppressed high finding count. |
| `medium_count` | Unsuppressed medium finding count. |
| `report_json` | Path to `report.json`. |
| `report_markdown` | Path to `report.md`. |
| `exit_code` | Agents Shipgate CLI exit code. |

For source-only testing in this repository:

```yaml
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
- uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
  with:
    python-version: "3.12"
- run: python -m pip install -e ".[dev]"
- run: agents-shipgate scan --config shipgate.yaml --ci-mode advisory
```

## Local Diagnostics

```bash
agents-shipgate init --workspace . --write
agents-shipgate doctor --config shipgate.yaml
AGENTS_SHIPGATE_LOG_FORMAT=json agents-shipgate scan --config shipgate.yaml --verbose
```

## GitLab CI

```yaml
agents-shipgate:
  image: python:3.12
  script:
    - python -m pip install -e ".[dev]"  # replace with pip install agents-shipgate after PyPI publication
    - agents-shipgate scan --config shipgate.yaml --ci-mode advisory
  artifacts:
    paths:
      - agents-shipgate-reports/
```

## CircleCI

```yaml
jobs:
  agents-shipgate:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run: python -m pip install -e ".[dev]" # replace with pip install agents-shipgate after PyPI publication
      - run: agents-shipgate scan --config shipgate.yaml --ci-mode advisory
```

## Jenkins

```groovy
stage('Agents Shipgate') {
  steps {
    sh 'python -m pip install -e ".[dev]"' // replace with pip install agents-shipgate after PyPI publication
    sh 'agents-shipgate scan --config shipgate.yaml --ci-mode advisory'
    archiveArtifacts artifacts: 'agents-shipgate-reports/**', allowEmptyArchive: true
  }
}
```
