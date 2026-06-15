# Code Review Guidelines

## Scope

In scope:

- Sphinx configuration (`conf.py`, `antsibull-docs.cfg`)
- Build tooling (`build.sh`, `requirements.txt`, `versions.env`, `Dockerfile`, `docker-compose.yml`)
- Theme and layout (`_static/`, `_templates/`, `package.json`, `postcss.config.js`)
- CI/CD workflow changes
- Renovate configuration updates

Out of scope:

- Generated artefacts (`build/`, `temp-rst/`, `rst/collections/`)
- Renovate dependency-only PRs (patch/minor with automerge enabled)

## Required checks

- No secrets committed — no credentials, tokens, or keys
- The documentation build succeeds (`./build.sh`)
- yamllint passes
- markdownlint passes
- Security scans pass (gitleaks, secretlint, trivy)

## Severity levels

| Level        | Meaning                                             | Merge impact       |
| ------------ | --------------------------------------------------- | ------------------ |
| Bug          | Incorrect behavior or broken build                  | Blocks merge       |
| Nit          | Minor issue — suboptimal but not incorrect          | Non-blocking       |
| Pre-existing | Issue present before this PR; flagged for awareness | No action required |

## Skip

- Renovate PRs with `automerge: true` (patch/minor) after CI passes
- Documentation-content-only changes with no functional impact
