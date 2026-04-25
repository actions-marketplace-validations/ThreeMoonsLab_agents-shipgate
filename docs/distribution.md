# Distribution Plan

These items require release infrastructure, registry credentials, domains, or GitHub repository settings. They are tracked here so the project has a clear path beyond source installs.

## Package Channels

- Publish `agents-shipgate` to PyPI.
- Publish a pinned GitHub Action release tag such as `v0.1.0`.
- Publish a container image such as `ghcr.io/threemoonslab/agents-shipgate:0.1.0`.
- Evaluate Homebrew once CLI usage warrants it.

The GitHub Action can install from its tagged source before PyPI publication. A
`shipgate_version` input is available for release flows that intentionally
install a published PyPI version.

## Supply Chain

- Generate SBOMs for release artifacts.
- Sign release artifacts with Sigstore.
- Keep GitHub Actions pinned by SHA.
- Use Dependabot for Python and GitHub Actions updates.
- Add a lockfile for release and dev dependency builds once packaging workflow is finalized.

## Marketplace And Site

- Submit `ThreeMoonsLab/agents-shipgate` to GitHub Marketplace after the first tagged release.
- Create a small landing page with install instructions, trust model, and findings gallery.
- Consider a local-only playground later; do not accept private customer manifests into a hosted service without a separate privacy review.

## Marketplace Repository Constraint

GitHub Marketplace action repositories must keep a single action metadata file at
the repository root and must not contain workflow files in the action repository.
For that reason this repo does not keep `.github/workflows/*` CI files on the
published branch. Run release validation locally or from a separate/internal CI
repository before tagging a Marketplace release.
