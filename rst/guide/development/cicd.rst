.. meta::
  :description: GitHub Actions workflows and linter configuration of the arillso repositories

.. _cicd:

CI/CD & Linting
===============

How the arillso repositories build, test, scan and release. The jobs
themselves live as reusable workflows in
`arillso/.github <https://github.com/arillso/.github/tree/main/.github/workflows>`_;
each repository has thin caller workflows that pass a few inputs.

.. contents::
   :local:
   :depth: 2

Workflow Layout
---------------

Every repository uses the same caller files under ``.github/workflows/``:

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - File
     - Trigger
     - Purpose
   * - ``pull-request.yml``
     - Pull request against ``main``
     - Lint, tests, secret scan, Claude review
   * - ``merge.yml``
     - Push to ``main``
     - Re-run CI and the secret scan; the container image repository also
       builds and publishes here
   * - ``tag.yml``
     - Version tag
     - Release (Ansible Galaxy, GitHub Release, image)
   * - ``nightly-security.yml``
     - Daily cron ``0 2 * * *`` (02:00 UTC)
     - Secret, code and configuration scans, SBOM
   * - ``cleanup.yml``
     - Monthly cron (``docker.ansible``, ``action.playbook``)
     - Prune old images from the registries

Reusable workflows are referenced by date tag, for example
``arillso/.github/.github/workflows/ci-ansible-collection.yml@2026-11-20``.
``arillso/.github`` moves the tag of the current UTC day to the latest commit
on every push to ``main``. Renovate (``renovate-base`` preset) bumps the tag in
the consumer repositories in a weekly Monday window and automerges the update.

Ansible Collections
-------------------

Pull Request
~~~~~~~~~~~~

Excerpt from ``arillso/ansible.system`` (scenario list shortened):

.. code-block:: yaml

   jobs:
     ci:
       uses: arillso/.github/.github/workflows/ci-ansible-collection.yml@2026-11-20
       with:
         collection_namespace: arillso
         collection_name: system
         python_version: "3.13"
         enable_unit_tests: true
         enable_integration_tests: true

     molecule:
       uses: arillso/.github/.github/workflows/ci-ansible-molecule.yml@2026-11-20
       with:
         collection_namespace: arillso
         collection_name: system
         python_version: "3.13"
         scenarios: '["access", "firewall", "packages"]'
         concurrency-suffix: molecule

     molecule-zram:
       uses: arillso/.github/.github/workflows/ci-ansible-molecule.yml@2026-11-20
       with:
         collection_namespace: arillso
         collection_name: system
         driver: qemu
         python_version: "3.13"
         scenarios: '["zram"]'
         concurrency-suffix: molecule-zram

``ci-ansible-collection.yml`` runs these jobs:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Job
     - What it runs
   * - Ansible Lint
     - ``ansible-lint``
   * - YAML Lint
     - ``yamllint .``
   * - Python Lint
     - ``ruff check``, ``black --check``, ``isort --check-only`` and
       ``pylint`` on ``plugins/``
   * - Markdown Lint
     - ``markdownlint-cli2`` on ``**/*.md`` (does not fail the run)
   * - Security Scan
     - Trivy filesystem scan, SARIF upload to code scanning
   * - Sanity Tests
     - ``ansible-test sanity --docker`` for each entry of
       ``ansible_versions`` (default ``stable-2.18``, ``stable-2.19``,
       ``stable-2.20``)
   * - Unit Tests
     - ``ansible-test units --docker``, only with ``enable_unit_tests: true``
   * - Integration Tests
     - ``ansible-test integration --docker``, only with
       ``enable_integration_tests: true``
   * - Argument Specs Check
     - Validates ``meta/argument_specs.yml`` of every role (on by default)
   * - Build Collection
     - ``ansible-galaxy collection build`` after the lint and sanity jobs;
       uploads the tarball as artifact

``ci-ansible-molecule.yml`` runs one Molecule job per scenario:

* ``scenarios_root`` defaults to ``extensions/molecule``; arillso.container
  and arillso.agent point it at ``roles/<role>/molecule`` instead.
* ``driver`` is ``docker`` by default. Scenarios that need a real kernel
  (Docker daemon, K3s, zram, tuning, a stable systemd service for Alloy) use
  ``driver: qemu`` and run in a KVM guest.
* ``concurrency-suffix`` keeps the nested call out of the caller's
  concurrency group; without it GitHub cancels the Molecule run.

Release
~~~~~~~

``tag.yml`` triggers on tags matching ``[0-9]+.[0-9]+.[0-9]+`` (no ``v``
prefix) and calls ``release-ansible-collection.yml``:

.. code-block:: yaml

   on:
     push:
       tags:
         - "[0-9]+.[0-9]+.[0-9]+"

   jobs:
     release:
       uses: arillso/.github/.github/workflows/release-ansible-collection.yml@2026-11-20
       with:
         collection_namespace: arillso
         collection_name: system
       secrets:
         galaxy_api_key: ${{ secrets.GALAXY_API_KEY }}

The reusable workflow:

1. fails if the tag differs from ``version`` in ``galaxy.yml``,
2. fails if ``CHANGELOG.md`` has no non-empty ``## [X.Y.Z]`` section for the
   tag,
3. builds and publishes the collection to Ansible Galaxy
   (``artis3n/ansible_galaxy_collection``),
4. creates a GitHub Release whose body is that changelog section.

Nightly Security
~~~~~~~~~~~~~~~~

``nightly-security.yml`` in the collections calls:

* ``security-secrets.yml``: Gitleaks, TruffleHog and pattern detection.
* ``security-code.yml``: CodeQL, languages as JSON array (for example
  ``'["python"]'``).
* ``security-config.yml``: Trivy configuration scan; with
  ``scan-ansible: true`` also ``ansible-lint`` and ``yamllint`` on
  ``ansible-path``.
* ``security-sbom.yml``: SBOM of the repository
  (``artifact-type: filesystem``).

Jobs that upload SARIF results need ``security-events: write`` in the
caller.

Go Repositories
---------------

``go.ansible`` and ``action.playbook`` call ``ci-go.yml`` on pull request and
merge. It runs ``go mod download`` and ``go mod verify``, ``go vet ./...``, a
``gofmt`` check, ``staticcheck``,
``go test -v -race -coverprofile=coverage.out ./...`` (coverage report as
artifact) and ``golangci-lint``. The Go version comes from ``go.mod``.

``ci-lint.yml`` adds ``actionlint``, ``shellcheck`` (with
``enable_shellcheck: true``) and ``yamllint``. ``security-deps.yml`` runs
GitHub dependency review and a Go dependency audit.

Release tags differ between the two:

* ``go.ansible``: ``v[0-9]+.[0-9]+.[0-9]+`` and pre-releases
  ``vX.Y.Z-<suffix>``. ``tag.yml`` builds and tests the module, creates the
  GitHub Release from the matching ``CHANGELOG.md`` section and attaches an
  SBOM.
* ``action.playbook``: ``[0-9]+.[0-9]+.[0-9]+`` without prefix.
  ``tag.yml`` builds the action image, pushes it to
  ``ghcr.io/arillso/action.playbook`` and creates a GitHub Release.

Container Image
---------------

``docker.ansible`` (image ``arillso/ansible``) runs its own pipeline in
``pull-request.yml``, on pull requests and weekly (Wednesday 01:00 UTC). Code
jobs are skipped when only Markdown or ``LICENSE`` changed.

* Lint: ``ci-lint.yml`` and ``hadolint`` on the ``Dockerfile``.
* Build the image once, then run against it: container-structure-test,
  hardening checks and Trivy (fails on fixable ``CRITICAL``/``HIGH``
  findings not listed in ``.trivyignore``), performance, integration,
  unit (pytest) and upgrade tests.

``merge.yml`` runs on pushes to ``main`` that touch ``Dockerfile`` or
``requirements.txt``. It re-runs the pull request and security workflows, then
builds ``linux/amd64`` and ``linux/arm64`` images, pushes them to Docker Hub
and ``ghcr.io`` with provenance and SBOM, generates a build-provenance
attestation and creates a GitHub Release tagged with the build date.

Action Pinning
--------------

The reusable workflows pin third-party actions to a full commit SHA with the
version as comment:

.. code-block:: yaml

   - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1

Renovate updates SHA and comment together. The ``renovate-base`` preset also
updates such ``uses:`` lines inside ``.rst`` files, so examples in this guide
follow the same scheme.

Linter Configuration
--------------------

The files below are taken from ``arillso/ansible.system``; the other
collections use the same set.

.yamllint.yml
~~~~~~~~~~~~~

Excerpt:

.. code-block:: yaml

   ---
   extends: default

   rules:
       line-length:
           max: 500
           level: warning

       indentation:
           spaces: 4
           indent-sequences: true
           check-multi-line-strings: false

       truthy:
           allowed-values: ["true", "false"]
           check-keys: false

       document-start:
           present: true

       octal-values:
           forbid-implicit-octal: true
           forbid-explicit-octal: true

.ansible-lint
~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   exclude_paths:
       - .ansible/
       - .github/
       - .venv/
       - venv/

   skip_list:
       - galaxy[version-incorrect]
       - command-instead-of-module
       - no-handler
       - package-latest

   warn_list:
       - name[casing]
       - yaml[line-length]

   use_default_rules: true

The lefthook pre-commit hook runs ``ansible-lint --profile=production`` on
staged role, plugin, test and meta files.

.editorconfig
~~~~~~~~~~~~~

Four spaces, LF line endings, UTF-8, final newline and trimmed trailing
whitespace for all files; trailing whitespace is kept in Markdown, and
``Makefile`` uses tabs.

.golangci.yml
~~~~~~~~~~~~~

From ``arillso/go.ansible``, without the per-linter settings:

.. code-block:: yaml

   ---
   version: "2"

   linters:
       enable:
           - errcheck
           - govet
           - staticcheck
           - gosec
           - ineffassign
           - unused
           - misspell
           - gocritic

   formatters:
       enable:
           - gofmt
           - goimports

Local Checks
------------

Each repository ships a ``Makefile`` and a ``lefthook.yml``. Run
``lefthook install`` once after cloning. The pre-commit hook runs yamllint,
markdownlint, actionlint and Gitleaks on staged files, plus the stack's own
checks (``ansible-lint`` in the collections, ``hadolint`` for the image,
``gofmt``/``go vet`` or ``golangci-lint`` in the Go repositories). The
pre-push hook runs a full Gitleaks scan, and ``go test`` in the Go
repositories.

.. code-block:: bash

   make lint          # collections: ansible-lint, yamllint, ruff/black
   make test          # collections: pytest; Go: go test
   make test-molecule # collections: every Molecule scenario
   make build         # collections: ansible-galaxy collection build

``make test`` in a collection runs ``pytest`` directly; CI runs
``ansible-test units --docker``. A green local run does not guarantee a green
CI run.

.. seealso::

   * :ref:`standards` - Repository Standards
   * :ref:`contributing` - Contributing
   * :ref:`compatibility` - Version Compatibility
