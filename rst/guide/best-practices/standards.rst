.. meta::
  :description: Repository standards and conventions for arillso projects

.. _standards:

Repository Standards
====================

Files, workflows and conventions shared by the arillso repositories. The shared
pieces (reusable workflows, Renovate presets, issue and pull request templates,
the ruleset template) live in `arillso/.github <https://github.com/arillso/.github>`_.
All repositories are public and MIT-licensed.

.. contents::
   :local:
   :depth: 2

Required Files
--------------

Every Repository
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Purpose
   * - ``README.md``
     - Short description and quick start
   * - ``LICENSE``
     - MIT License
   * - ``.gitignore``, ``.editorconfig``
     - Ignore rules, editor settings
   * - ``.github/CODEOWNERS``
     - Default owner
   * - ``.github/renovate.json``
     - Extends a preset from ``arillso/.github``
   * - ``CHANGELOG.md``
     - Version history, for released projects
   * - ``AGENTS.md``
     - Instructions for coding agents
   * - ``CLAUDE.md``
     - One line: ``@AGENTS.md``
   * - ``REVIEW.md``
     - Rules for the AI review workflow (see :ref:`review-md`)

``CONTRIBUTING.md`` is required for Ansible Collections.

Organisation-Wide Defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~

``arillso/.github`` provides GitHub's default community health files for every
repository that has no own copy: ``SECURITY.md``, ``CONTRIBUTING.md``,
``CODE_OF_CONDUCT.md``, ``SUPPORT.md``, ``GOVERNANCE.md``, the issue templates
(``bug_report.yml``, ``feature_request.yml``, ``documentation.yml``) and
``pull_request_template.md``. A repository adds its own copy only to override
them.

Layout
~~~~~~

.. code-block:: text

   repository/
   ├── .github/
   │   ├── workflows/
   │   │   ├── pull-request.yml
   │   │   ├── merge.yml
   │   │   ├── nightly-security.yml
   │   │   ├── tag.yml              # only where something is released
   │   │   └── cleanup.yml          # only where a container registry is used
   │   ├── CODEOWNERS
   │   └── renovate.json
   ├── AGENTS.md
   ├── CLAUDE.md
   ├── CHANGELOG.md
   ├── CONTRIBUTING.md              # Ansible Collections
   ├── LICENSE
   ├── README.md
   ├── REVIEW.md
   ├── .editorconfig
   ├── .gitignore
   └── [project files]

README.md
---------

Keep the README short: title, one or two sentences, quick start, license.
Collection READMEs additionally list their roles and plugins and may carry CI,
Galaxy and license badges. Detailed usage belongs on guide.arillso.io, agent
instructions in ``AGENTS.md``.

.. code-block:: markdown

   # Project Name

   Short description (1-2 sentences).

   ## Quick Start

   ```bash
   # Installation or usage commands
   ```

   ## License

   MIT License

.. _review-md:

REVIEW.md
---------

``REVIEW.md`` holds the code review rules for a repository. Unlike the other
required files it is written for a machine first: the AI review workflow
``ai-claude-review.yml`` in `arillso/.github
<https://github.com/arillso/.github>`_ reads it on every pull request and is
instructed that it **takes precedence over generic best practices**. Where a
rule in ``REVIEW.md`` conflicts with what the reviewer would otherwise apply,
the file wins.

This is what makes the file worth maintaining: it is the one place where a
repository can narrow, widen, or overrule the review it receives, without
touching the shared workflow.

Precedence and the Base Branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The workflow reads ``REVIEW.md`` from the **base branch**, never from the pull
request's own checkout. It is fetched into a separate ``.review-base/``
directory alongside ``AGENTS.md`` and ``CLAUDE.md``, and the reviewer is told
to ignore any copy at the repository root.

.. important::
   A pull request cannot change the rules of the review it is subject to. A
   change to ``REVIEW.md`` governs the *next* pull request, after it is merged
   — not the one proposing it.

The reason is that the reviewing agent holds approval rights. If a pull request
could rewrite its instructions, it could instruct the reviewer to approve
itself. Reading from the base ref removes that path.

The file is optional in the sense that the workflow tolerates its absence: the
checkout is sparse and exits cleanly when the file is missing, and the reviewer
falls back to generic best practices. A repository without ``REVIEW.md`` is
therefore not broken — it is merely unconfigured, and reviewed by defaults
nobody chose.

Structure
~~~~~~~~~

All repositories use the same five headings, in this order. The headings are
the contract; the content under them is repository-specific.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Heading
     - Content
   * - ``# Code Review Guidelines``
     - Document title. Identical across repositories.
   * - ``## Scope``
     - Two lists, **In scope** and **Out of scope**, naming paths and change
       types. Generated artefacts and dependency-only Renovate pull requests
       belong out of scope.
   * - ``## Required checks``
     - The conditions a change must meet: no committed secrets, the linters
       and test suites that apply, passing security scans.
   * - ``## Severity levels``
     - A table mapping each level to its meaning and merge impact. Defines
       what blocks a merge and what is merely flagged.
   * - ``## Skip``
     - Cases where a review adds nothing and may be skipped entirely.

Severity levels are shared across repositories and should not be renamed —
they are the vocabulary the reviewer uses in its comments:

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - Level
     - Meaning
     - Merge impact
   * - Bug
     - Incorrect behavior or broken contract
     - Blocks merge
   * - Nit
     - Minor issue — suboptimal but not incorrect
     - Non-blocking
   * - Pre-existing
     - Issue present before this pull request; flagged for awareness
     - No action required

Writing Scope and Required Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Scope`` and ``Required checks`` are where repositories genuinely differ, and
where the file earns its keep. Name the actual paths and the actual commands.

.. code-block:: markdown

   ## Scope

   In scope:

   - Role changes (`roles/`)
   - Lookup/module plugin changes (`plugins/`)
   - Collection metadata (`galaxy.yml`, `meta/`)

   Out of scope:

   - `.ansible/` directories — local galaxy/fact caches
   - Renovate dependency-only PRs (patch/minor with automerge enabled)

   ## Required checks

   - No secrets committed — no credentials, tokens, or keys
   - `ansible-lint --profile=production` passes
   - yamllint passes
   - `argument_specs.yml` present and complete for any new or changed role

A documentation repository lists its build and its markdown linter; an Ansible
Collection lists ``ansible-lint``, molecule, and ``argument_specs.yml``. Both
keep the same five headings.

LICENSE Format
--------------

All repositories use **MIT License**:

.. code-block:: text

   MIT License

   Copyright (c) 2025-2026 arillso

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction...

Copyright Year Format
~~~~~~~~~~~~~~~~~~~~~

* **New projects:** Current year only (e.g., ``2026``)
* **Existing projects:** Range from first year to current (e.g., ``2023-2026``)

**Update annually in:**

* LICENSE file
* README.md
* Source files with copyright headers
* Plugin/module headers

GitHub Configuration
--------------------

CODEOWNERS
~~~~~~~~~~

.. code-block:: text

   # Default owner
   * @sbaerlocher

Renovate Configuration
~~~~~~~~~~~~~~~~~~~~~~

**Base configuration** (all repos):

.. code-block:: json

   {
       "$schema": "https://docs.renovatebot.com/renovate-schema.json",
       "extends": ["github>arillso/.github:renovate-base#2026-11-14"]
   }

Pin the preset reference to a date tag. Without the ``#<date-tag>`` suffix
Renovate resolves the preset against the default branch of
``arillso/.github``, so a change there reaches every repository without a pull
request and without review. A ``customManager`` in ``renovate-base`` updates
the tag; these updates are batched on Monday mornings and automerge.

**Available presets:**

* ``renovate-base`` - All repositories
* ``renovate-go`` - Go projects
* ``renovate-actions`` - GitHub Actions
* ``renovate-ansible`` - Ansible collections (includes version variable management)
* ``renovate-alpine`` - Alpine ``apk`` version pins in Dockerfiles

GitHub Rulesets
~~~~~~~~~~~~~~~

Every repository gets the ruleset from ``templates/github-ruleset.json`` in
``arillso/.github``. It contains these rules:

* **Deletion protection** - Prevents deletion of ``main`` branch
* **Non-fast-forward** - Prevents force pushes
* **Required linear history** - Clean git history
* **Pull request required** - No direct pushes
* **Required status checks** - CI must pass

.. code-block:: bash

   # Run in a clone of arillso/.github
   gh api repos/arillso/<repo-name>/rulesets \
     --method POST \
     --input templates/github-ruleset.json

Workflow Standards
------------------

Naming Convention
~~~~~~~~~~~~~~~~~

Workflow files fall into two layers, each with its own naming rule.

**Reusable workflows** live in ``arillso/.github`` and are named
``<category>-<purpose>.yml``:

* ``ci-*.yml`` - Continuous Integration
* ``security-*.yml`` - Security scanning
* ``release-*.yml`` - Release and publishing
* ``cleanup-*.yml`` - Cleanup and maintenance
* ``ai-*.yml`` - AI-assisted workflows (see :ref:`review-md` for the rules
  ``ai-claude-review.yml`` reads)

The category prefix keeps the library navigable and lets a consumer see which
CI it is calling. The ``name:`` field spells the purpose out in full, without
abbreviations (``name: CI - Ansible Collection``, not ``CI Ansible``).

**Caller workflows** live in each project repository and are named after the
event that triggers them, not after the work they do:

* ``pull-request.yml`` - checks on pull requests
* ``merge.yml`` - checks after merge to ``main``
* ``tag.yml`` - release on tag push
* ``nightly-security.yml`` - scheduled security scans
* ``cleanup.yml`` - scheduled maintenance

A caller is thin: it wires an event to one or more reusable workflows and
passes inputs. All names are lowercase with hyphens.

Standard Workflows
~~~~~~~~~~~~~~~~~~

Caller workflows in a project repository:

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Trigger
     - Filename
     - Description
   * - Pull request
     - ``pull-request.yml``
     - Linting and testing on pull requests
   * - Merge
     - ``merge.yml``
     - Linting and testing on ``main`` after merge
   * - Tag
     - ``tag.yml``
     - Publish to registry + GitHub Release
   * - Schedule
     - ``nightly-security.yml``
     - Security scanning, including CodeQL (required for public repos with
       CodeQL-supported code)
   * - Schedule
     - ``cleanup.yml``
     - Registry retention cleanup (only where a registry is used)

Not every repository needs every caller: ``tag.yml`` exists only where there is
something to release, ``cleanup.yml`` only where a container registry is used.

The reusable workflows these callers invoke are listed in
`arillso/.github <https://github.com/arillso/.github>`_.

.. _codeql-exception:

CodeQL Exception
~~~~~~~~~~~~~~~~

CodeQL is required for public repositories **that contain code CodeQL can
analyse**. A repository whose tree holds no file with a CodeQL-supported
extension is exempt: there is nothing for the analysis to read, so the scan
would either fail to configure or report an empty result forever.

The test is the tree, not a maintained list of exempt repositories. It covers
the compiled and interpreted languages ``security-code.yml`` is configured for
via its ``languages`` input:

.. code-block:: bash

   # Exempt if this finds nothing
   git ls-files -- '*.go' '*.py' '*.pyw' '*.js' '*.mjs' '*.cjs' '*.jsx' \
     '*.ts' '*.tsx' '*.java' '*.cs' '*.c' '*.h' '*.cpp' '*.cc' '*.cxx' \
     '*.hpp' '*.hh' '*.rb' '*.swift' '*.kt' '*.kts'

CodeQL also ships an ``actions`` language that analyses
``.github/workflows/*.yml``. It is deliberately **not** part of this test:
``security-code.yml`` does not enable it, so workflow files alone do not make a
repository subject to the criterion. Wiring up Actions analysis is a separate
decision — until it happens, a repository with nothing but workflows and prose
stays exempt.

Pure Ansible Collections and pure documentation repositories are the usual
case. Such a repository still runs ``nightly-security.yml``; its caller invokes
the scans that do apply — at minimum ``security-secrets.yml`` — and omits
``security-code.yml``.

Adding a file in a supported language removes the exemption — the criterion is
re-evaluated per audit, not granted once.

GitHub Actions Security
~~~~~~~~~~~~~~~~~~~~~~~

Actions are pinned to a full commit SHA with the version as a comment, for
example ``actions/checkout@<sha> # v7.0.1``. Renovate updates the SHA and the
comment. See :ref:`cicd`.

Schedules
~~~~~~~~~

``nightly-security.yml`` runs daily at 02:00 UTC (``0 2 * * *``).
``cleanup.yml`` runs monthly (``0 2 1 * *``).

Ansible Collection Standards
----------------------------

Required Files
~~~~~~~~~~~~~~

* ``galaxy.yml`` - metadata; dependencies with lower bounds only
* ``meta/runtime.yml`` - ``requires_ansible`` (``>=2.18.0``), ``action_groups``
  where modules share settings
* ``meta/argument_specs.yml`` for every role (a required check in each
  collection's ``REVIEW.md``)
* ``CHANGELOG.md``, ``CONTRIBUTING.md``
* ``Makefile`` with named targets used by CI and developers (``arillso.system``:
  ``lint``, ``test-unit``, ``test-integration``, ``test-molecule``, ``build``)
* A Molecule scenario per role. ``arillso.system`` keeps them under
  ``extensions/molecule/<role>/``; ``arillso.container`` 2.2.0 under
  ``roles/<role>/molecule/default/``.

See :ref:`contributing` for the contribution workflow and :ref:`ansible-roles`
for role and collection design.

CI
~~

``pull-request.yml`` and ``merge.yml`` call
``ci-ansible-collection.yml``. Its jobs run in parallel; only ``build`` waits
for ``ansible-lint``, ``yaml-lint``, ``python-lint`` and ``sanity-test``.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Job
     - Runs
   * - ``ansible-lint``
     - ``ansible-lint`` (profile ``production`` in ``.ansible-lint``)
   * - ``yaml-lint``
     - ``yamllint``
   * - ``python-lint``
     - ``ruff``, ``black --check``, ``isort --check-only``, ``pylint`` on ``plugins/``
   * - ``markdown-lint``
     - ``markdownlint-cli2``
   * - ``security-scan``
     - Trivy filesystem scan, results uploaded as SARIF
   * - ``sanity-test``
     - ``ansible-test sanity``
   * - ``unit-test``
     - ``ansible-test units --docker`` (input ``enable_unit_tests``)
   * - ``integration-test``
     - ``ansible-test integration --docker`` (input ``enable_integration_tests``)
   * - ``argument-specs``
     - checks ``meta/argument_specs.yml``
   * - ``build``
     - ``ansible-galaxy collection build``

Molecule runs in a separate reusable workflow, ``ci-ansible-molecule.yml``, with
one matrix entry per scenario. ``arillso.system`` calls it three times: once for
the Docker-driver scenarios and once each for ``zram`` and ``tuning`` under QEMU.

Release Process
~~~~~~~~~~~~~~~

1. Add a ``## [x.y.z] - YYYY-MM-DD`` section to ``CHANGELOG.md``
   (`Keep a Changelog <https://keepachangelog.com/>`_).
2. Set ``version: x.y.z`` in ``galaxy.yml``.
3. Tag without a ``v`` prefix and push the tag:

   .. code-block:: bash

      git tag 1.0.1
      git push origin 1.0.1

``tag.yml`` triggers on tags matching ``[0-9]+.[0-9]+.[0-9]+`` and calls
``release-ansible-collection.yml``. That workflow fails if the tag differs from
the ``galaxy.yml`` version or if ``CHANGELOG.md`` has no non-empty
``## [<version>]`` section, then publishes to Galaxy and creates the GitHub
Release from that changelog section.

Keep releasing in that one ``tag.yml`` caller; do not split it across several
callers on the same tag event or trigger on ``release: [published]``.

Documentation
~~~~~~~~~~~~~

* Collection README: overview and list of roles and plugins.
* Role README: short description, features, quick start, link to the role page
  on guide.arillso.io.
* ``meta/argument_specs.yml``: the complete variable documentation. The role
  pages on guide.arillso.io are generated from it.

.. code-block:: markdown

   # Ansible Role: role_name

   Brief description.

   ## Documentation

   https://guide.arillso.io/collections/arillso/<collection>/<role>_role.html

   ## Quick Start

   ```yaml
   - hosts: servers
     roles:
       - role: arillso.<collection>.role_name
   ```

   ## License

   MIT

Version Variables
~~~~~~~~~~~~~~~~~

Pinned upstream versions in ``defaults/main.yml`` carry a Renovate comment on
the line directly above, matched by the regex manager in ``renovate-base``:

.. code-block:: yaml

   # renovate: datasource=github-releases depName=k3s-io/k3s
   k3s_version: "v1.37.1+k3s1"

   # renovate: datasource=github-releases depName=moby/moby
   docker_version: "28.5.2"

Go and Container Projects
-------------------------

See :ref:`contributing` for Go code style and Dockerfile conventions.

AGENTS.md
---------

``CLAUDE.md`` contains only ``@AGENTS.md``. ``AGENTS.md`` has no fixed set of
headings; existing files use sections such as ``Commands``, ``Conventions``,
``Traps`` or ``Gotchas``, and ``Further docs``. It holds what an agent cannot
infer from the code: commands, non-obvious conventions and known traps.

CHANGELOG Format
----------------

Required for released projects, in `Keep a Changelog
<https://keepachangelog.com/>`_ format:

.. code-block:: markdown

   # Changelog

   ## [Unreleased]

   ### Added
   - New feature

   ## [1.0.0] - 2026-01-17

   ### Fixed
   - Bug Y

Sections: Added, Changed, Deprecated, Removed, Fixed, Security.

Issue and Pull Request Templates
--------------------------------

The organisation-wide templates in ``arillso/.github`` apply to every
repository without its own copy:

* Issue templates: ``bug_report.yml``, ``feature_request.yml``,
  ``documentation.yml``.
* ``pull_request_template.md`` sections: Description, Type of Change, Related
  Issue, Affected Component(s), Changes Made, Testing Performed, Documentation,
  Code Quality, Checklist, Screenshots, Additional Notes, Breaking Changes.

.. seealso::

   * :ref:`review-md` - code review rules consumed by the AI review workflow
   * :ref:`ansible-roles` - role and collection design rules
   * :ref:`contributing` - how to contribute
   * :ref:`cicd` - CI/CD workflows and linter configuration
   * :ref:`compatibility` - version requirements and platform support
   * `arillso/.github on GitHub <https://github.com/arillso/.github>`_ - shared standards and reusable workflows
