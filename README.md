# Arillso Guide

Source of <https://guide.arillso.io>, the reference documentation for the
arillso Ansible collections, the `arillso/ansible` container image, the
`action.playbook` GitHub Action and the `go.ansible` library.

The site is Sphinx HTML built on top of `antsibull-docs`. Collection
documentation for `arillso.system`, `arillso.agent`, and `arillso.container`
is generated from the released collections and rendered with the site's own
theme (`_theme/arillso/`, styles and scripts in `src/`).

## Source Layout

| Path                             | Purpose                                                                                                                                                             |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/`                           | Frontend sources (CSS tokens/base/layout/components, JS feature modules). PostCSS + esbuild emit the bundles into `_static/`. See [`src/README.md`](src/README.md). |
| `_theme/arillso/`                | Sphinx theme: `theme.toml` and `layout.html`, inheriting only the `basic` templates (search page).                                                                  |
| `scripts/`                       | Python and shell helpers — `collection_cache.py` (collection cache), `normalize_collections.py` (normalisation pass), `build_frontend.sh` (frontend bundle).        |
| `rst/`                           | Hand-written Sphinx sources plus the generated collection trees that `antsibull-docs` writes during the build.                                                      |
| `_static/`                       | Tracked `logo.svg`, `favicon.ico` and `fonts/` (self-hosted, SIL OFL), plus the bundles `custom.css` and `custom.js` that the frontend build regenerates.           |
| `tests/`                         | Pytest suite for the build scripts (collection cache, normaliser).                                                                                                  |
| `versions.env`                   | Pinned collection versions consumed by `build.sh` and `collection_cache.py`.                                                                                        |
| `build.sh`                       | Top-level build entry point — orchestrates the steps below.                                                                                                         |
| `conf.py` / `antsibull-docs.cfg` | Sphinx and antsibull-docs configuration.                                                                                                                            |

## Local Development

Prerequisites: Python 3.15 (see `.python-version`), Node.js 22.22.3+, 24.15+ or 26+ (`cssnano` engine range), and `ansible-galaxy` on `PATH`
(only needed when the collection cache is cold and you are online).

The repository ships a [dde](https://github.com/whatwedo/dde) v2 setup, so
the simplest path is a containerised build that serves the site behind
Traefik on a per-checkout `.test` hostname:

```bash
dde project:up        # build + serve; prints the .test URL
```

For a host-local build without dde:

```bash
# 1. Install Python and Node dependencies
npm ci
pip install -r requirements.txt -r requirements-dev.txt

# 2a. Full build (collections + Sphinx + frontend)
./build.sh

# 2b. Or only rebuild the frontend bundle into _static/
npm run build
```

To work offline against an already-populated collection cache, set
`ARILLSO_OFFLINE=1` before invoking `./build.sh`. The cache root can be
overridden with `ARILLSO_COLLECTIONS_CACHE` (defaults to
`~/.cache/arillso-collections`).

Watch mode while editing the frontend:

```bash
npm run build:watch       # PostCSS + esbuild, rebuild on change
```

## Build Steps

`./build.sh` runs the pipeline in this order:

1. **Frontend build** — `build.sh` runs `npm ci` when `postcss` is not
   installed yet, then `scripts/build_frontend.sh` runs PostCSS
   (autoprefixer + cssnano) over `src/styles/index.css` and esbuild over
   `src/scripts/index.js`, writing `_static/custom.css` and
   `_static/custom.js`.
2. **Collection cache** — `scripts/collection_cache.py ensure` reads
   `versions.env`, populates `~/.cache/arillso-collections/` (offline
   when `ARILLSO_OFFLINE=1`), and exports `ANSIBLE_COLLECTIONS_PATH`.
3. **antsibull-docs** — generates RST for `arillso.system`,
   `arillso.agent`, `arillso.container` into `temp-rst/`, then rsyncs
   into `rst/collections/`.
4. **Normalisation** — `scripts/normalize_collections.py --root rst`
   rewrites collection names to the canonical short form.
5. **Sphinx** — `sphinx-build -M html rst build -c . -W --keep-going`
   renders the site into `build/html/`. Warnings fail the build. While
   reading `conf.py`, Sphinx first renders `_well_known_build/security.txt`
   (see Security below), which `html_extra_path` publishes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, build
instructions, and the pull request process.

## Further Reading

- [`src/README.md`](src/README.md) — design decisions, frontend module map,
  token rules, and frontend build commands.
- [`docs/regression-checklist.md`](docs/regression-checklist.md) — manual
  regression checklist for frontend and theme changes.
- [`AGENTS.md`](AGENTS.md) — conventions and traps when changing this repo.

## Security

Report vulnerabilities to <security@arillso.io>. The full disclosure process
is documented in the [organisation security policy](https://github.com/arillso/guide/security/policy).

The site serves the same contact as an RFC 9116
[`security.txt`](https://guide.arillso.io/.well-known/security.txt). It is
rendered at build time from `_well_known/security.txt.in` by
`scripts/security_txt.py`, which fills the `Expires` field with the build date
plus 364 days — under the one year RFC 9116 §2.5.5 recommends. Every merge to
`main` redeploys the site and so refreshes the date. Keep the `{EXPIRES}`
placeholder — a fixed date expires, and an expired `security.txt` is invalid
under RFC 9116.

## License

MIT — see [LICENSE](LICENSE).
