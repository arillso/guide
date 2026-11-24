# Arillso Guide

Sphinx + antsibull-docs toolchain that renders <https://guide.arillso.io>.
It holds no Ansible roles or plugins; collection docs are pulled from the
upstream `arillso.*` collections at build time.

## Sources and generated output

| Edit here                                    | Generated, git-ignored                                     |
| -------------------------------------------- | ---------------------------------------------------------- |
| `rst/` (hand-written pages)                  | `rst/collections/`, `temp-rst/` (antsibull-docs)           |
| `src/styles/`, `src/scripts/` (theme CSS/JS) | `_static/custom.css`, `_static/custom.js` (frontend build) |
| `_theme/arillso/` (theme templates)          | —                                                          |
| `_well_known/security.txt.in`                | `_well_known_build/` (`scripts/security_txt.py`)           |
| upstream collection repo                     | collection pages under `rst/collections/`                  |

`_static/favicon.ico`, `_static/logo.svg` and `_static/fonts/` are tracked
sources; the two `custom.*` bundles are overwritten on every build. The theme
is the repo's own (`_theme/arillso/`, `html_theme = "arillso"`), inheriting
only Sphinx's `basic` templates; there is no third-party Sphinx theme.

## Traps

- Sphinx runs with `-W --keep-going`: every warning (broken `:ref:`, bad
  toctree, nitpicky reference) fails the build. Run `./build.sh` before
  pushing a change under `rst/` or `conf.py`.
- `security.txt` gets its `Expires` date from the build date via the
  `{EXPIRES}` placeholder. Keep the placeholder; a fixed date expires, and
  the date stays valid only because every merge to `main` redeploys.
- Renovate updates `versions.env` (collection versions),
  `mermaid_version` in `conf.py` and the impeccable marketplace `ref` in
  `.claude/settings.json` through custom regex managers in
  `.github/renovate.json`. Keep the `# renovate:` comment line directly
  above each `versions.env` entry, or the manager stops matching.
- `.claude/settings.json` enables the impeccable design plugin but does not
  install it. Run `claude plugin install impeccable@impeccable --scope project`
  once per clone, and `claude plugin update impeccable@impeccable` after a
  Renovate bump of its `ref` (auto-update is off for third-party
  marketplaces; turn it on in `/plugin` → Marketplaces if wanted).
- Release versions of the collections, `action.playbook` and `go.ansible`
  live only in `versions.env` (Renovate bumps them). In `rst/`, usage
  examples write `@ACTION_PLAYBOOK_VERSION@`, `@ARILLSO_SYSTEM_VERSION@` etc.;
  `conf.py` replaces the tokens on `source-read`, code blocks included, and
  an unknown `@…_VERSION@` token fails the build. Sentences about one
  specific release ("not in 0.5.0") keep the literal number on purpose.
- `conf.py` reads `versions.env` and counts the generated
  `rst/collections/arillso/<c>/*_<kind>.rst` files into `rst_epilog`
  substitutions (`|system_version|`, `|system_roles|`, …) for the start
  page. Rename a variable in `versions.env` and the start page breaks.
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

- Before changing `src/` or `_theme/`: read `src/README.md` (design rules,
  banned patterns, token contract).
- After larger frontend or theme changes: walk `docs/regression-checklist.md`.
- Code review scope and severity levels: `REVIEW.md`.
- Setup and lint hooks (`lefthook install`): `CONTRIBUTING.md`. Local
  tests: `pip install -r requirements-dev.txt`, then `pytest`.
