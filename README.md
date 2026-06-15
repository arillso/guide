# Arillso Guide

> The simple, flexible, robust and powerful toolbox for Ansible.<br />It contains roles for managing Linux and Windows devices.

## Overview

This repository builds the Arillso documentation site published at
<https://guide.arillso.io>. It is a [Sphinx](https://www.sphinx-doc.org/)
project rendered with
[antsibull-docs](https://github.com/ansible-community/antsibull-docs) and the
`sphinx-ansible-theme`. The build collects documentation from the Arillso
Ansible collections and renders it into a static HTML site deployed to GitHub
Pages.

## Quickstart

```bash
# Install build dependencies
pip install -r requirements.txt

# Build the documentation
./build.sh
```

The rendered site lands in `build/html`. A containerised build is also
available via `docker-compose.yml`.

## Configuration

- `conf.py` — Sphinx configuration
- `antsibull-docs.cfg` — antsibull-docs configuration
- `versions.env` — pinned versions consumed by the build
- `_static/` / `_templates/` — theme overrides and custom assets

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, build
instructions, and the pull request process.

## License

MIT — see [LICENSE](LICENSE).
