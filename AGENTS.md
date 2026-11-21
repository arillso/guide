# Arillso Guide

Sphinx + antsibull-docs toolchain that renders <https://guide.arillso.io>.
It holds no Ansible roles or plugins; collection docs are pulled from the
upstream `arillso.*` collections at build time.

## Sources and generated output

| Edit here                                    | Generated, git-ignored                                     |
| -------------------------------------------- | ---------------------------------------------------------- |
| `rst/` (hand-written pages)                  | `rst/collections/`, `temp-rst/` (antsibull-docs)           |
| `src/styles/`, `src/scripts/` (theme CSS/JS) | `_static/custom.css`, `_static/custom.js` (frontend build) |
| `_well_known/security.txt.in`                | `_well_known_build/` (`scripts/security_txt.py`)           |
| upstream collection repo                     | collection pages under `rst/collections/`                  |

`_static/favicon.ico` and `_static/logo.svg` are tracked sources; the two
`custom.*` bundles are overwritten on every build.

## Traps

- Sphinx runs with `-W --keep-going`: every warning (broken `:ref:`, bad
  toctree, nitpicky reference) fails the build. Run `./build.sh` before
  pushing a change under `rst/` or `conf.py`.
- `security.txt` gets its `Expires` date from the build date via the
  `{EXPIRES}` placeholder. Keep the placeholder; a fixed date expires, and
  the date stays valid only because every merge to `main` redeploys.
- Renovate updates `versions.env` (collection versions) and
  `mermaid_version` in `conf.py` through custom regex managers in
  `.github/renovate.json`. Keep the `# renovate:` comment line directly
  above each `versions.env` entry, or the manager stops matching.
- `build.sh` runs `npm ci` itself when neither `node_modules/.bin/postcss`
  nor `/usr/src/node_modules/.bin/postcss` exists; the Docker image ships
  the latter.

## CI

Workflows call reusables from `arillso/.github`:

- `pull-request.yml`: `pytest`, `./build.sh`, Sphinx linkcheck, Docker image
  build + smoke test (target `docs`), secret scan, dependency review,
  Claude review.
- `merge.yml`: build and deploy to GitHub Pages on push to `main`, secret scan.
- `nightly-security.yml`: scheduled CodeQL (Python, JavaScript), secret
  scan, SBOM.

A change to `Dockerfile` or `docker-compose.yml` must keep the smoke test in
`pull-request.yml` passing; it runs the image as a non-root user with
`HOME=/tmp`.

## Further docs

- Before changing `src/` or `_templates/`: read `src/README.md`.
- After larger frontend or theme changes: walk `docs/regression-checklist.md`.
- Code review scope and severity levels: `REVIEW.md`.
- Setup and lint hooks (`lefthook install`): `CONTRIBUTING.md`. Local
  tests: `pip install -r requirements-dev.txt`, then `pytest`.
