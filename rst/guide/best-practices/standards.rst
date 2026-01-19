.. meta::
  :description: Repository standards and conventions for all arillso projects

.. _standards:

Repository Standards
====================

Official standards and conventions for all arillso repositories. All public repositories use **MIT License**.

.. contents::
   :local:
   :depth: 2

Core Principles
---------------

1. **Public by default** - All repositories are public with MIT License
2. **Focus on essentials** - No unnecessary files
3. **Consistency** - Same structure across similar project types
4. **Documentation** - Keep it minimal but complete
5. **Automation** - Use workflows for repetitive tasks

Required Files
--------------

Every Repository Must Have
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **README.md** - Main documentation
2. **LICENSE** - MIT License with copyright
3. **.gitignore** - Project-specific ignore rules
4. **.editorconfig** - Editor consistency
5. **.github/CODEOWNERS** - Code ownership
6. **.github/renovate.json** - Dependency updates
7. **CHANGELOG.md** - Version history (for released projects)
8. **AGENTS.md** - AI agent instructions
9. **CLAUDE.md** - Import reference (``@AGENTS.md``)

Recommended Structure
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   repository/
   ├── .github/
   │   ├── workflows/
   │   │   ├── ci.yml
   │   │   └── publish.yml
   │   ├── ISSUE_TEMPLATE/
   │   ├── pull_request_template.md
   │   ├── CODEOWNERS
   │   └── renovate.json
   ├── AGENTS.md
   ├── CLAUDE.md
   ├── CHANGELOG.md
   ├── CONTRIBUTING.md      # Required for Ansible Collections
   ├── LICENSE
   ├── README.md
   ├── .editorconfig
   ├── .gitignore
   └── [project files]

README.md Structure
-------------------

Minimal Format
~~~~~~~~~~~~~~

.. code-block:: markdown

   # Project Name

   [![badges](shields.io/badges)]  # Only for packages/collections

   Short description (1-2 sentences).

   ## Quick Start

   ```bash
   # Installation or usage commands
   ```

   ## License

   MIT License

   ## Copyright

   (c) YEAR-YEAR, arillso

Guidelines
~~~~~~~~~~

**Include:**

* Project badges (only for Ansible Collections and published packages)
* Brief description
* Quick start example
* Link to comprehensive documentation (if applicable)

**Avoid:**

* Long feature lists (except Ansible Collections)
* Detailed code examples (belongs in AGENTS.md or guide.arillso.io)
* Verbose descriptions

LICENSE Format
--------------

All repositories use **MIT License**:

.. code-block:: text

   MIT License

   Copyright (c) YEAR-YEAR arillso

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
       "extends": ["github>arillso/.github:renovate-base"]
   }

**Available presets:**

* ``renovate-base`` - All repositories
* ``renovate-go`` - Go projects
* ``renovate-actions`` - GitHub Actions
* ``renovate-ansible`` - Ansible collections (includes version variable management)

GitHub Rulesets
~~~~~~~~~~~~~~~

All repositories must have branch protection via GitHub Rulesets:

* **Deletion protection** - Prevents deletion of ``main`` branch
* **Non-fast-forward** - Prevents force pushes
* **Required linear history** - Clean git history
* **Pull request required** - No direct pushes
* **Required status checks** - CI must pass

.. code-block:: bash

   # Create ruleset using GitHub CLI
   gh api repos/arillso/<repo-name>/rulesets \
     --method POST \
     --input .github/templates/github-ruleset.json

Workflow Standards
------------------

Naming Convention
~~~~~~~~~~~~~~~~~

* Lowercase with hyphens
* Short and descriptive
* Standard names: ``ci.yml``, ``publish.yml``, ``codeql.yml``, ``security.yml``

Standard Workflows
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Workflow
     - Filename
     - Description
   * - CI
     - ``ci.yml``
     - Linting, testing, building
   * - Publish
     - ``publish.yml``
     - Publish to registry + GitHub Release
   * - Security
     - ``security.yml``
     - Trivy scanning
   * - CodeQL
     - ``codeql.yml``
     - Code analysis (required for public repos)

GitHub Actions Security
~~~~~~~~~~~~~~~~~~~~~~~

**All GitHub Actions must be pinned to SHA digest.**

See :ref:`cicd` for implementation details and examples.

**Why:**

* Prevents supply chain attacks
* Ensures immutable action versions
* Renovate manages updates automatically

Schedule Frequency
~~~~~~~~~~~~~~~~~~

Scheduled workflows run **weekly on Monday at 06:00 UTC**.

See :ref:`cicd` for workflow implementation examples.

Ansible Collection Standards
-----------------------------

Required Files
~~~~~~~~~~~~~~

All Ansible Collections must include:

* **CONTRIBUTING.md** - Required for all collections
* **meta/argument_specs.yml** - Required for every role
* **CHANGELOG.md** - Version history
* **galaxy.yml** - Collection metadata

See :ref:`contributing` for complete file structure, code style, and development standards.

Testing Philosophy
~~~~~~~~~~~~~~~~~~

**All collections must implement three-level testing:**

1. **Unit Tests** - Python plugins with pytest
2. **Molecule Tests** - Critical roles on multiple distributions
3. **Integration Tests** - ansible-test for end-to-end validation

**All tests consolidated in single** ``ci.yml`` **workflow.**

See :ref:`cicd` for complete CI workflow implementation.

CI Workflow Structure
~~~~~~~~~~~~~~~~~~~~~

**All tests in one file** with dependency chain:

.. mermaid::

   flowchart LR
       subgraph Stage1["Stage 1: Linting (Parallel)"]
           AL[ansible-lint]
           YL[yaml-lint]
           PL[python-lint]
           ML[markdown-lint]
           SS[security-scan]
       end

       subgraph Stage2["Stage 2: Sanity"]
           ST[sanity-test]
       end

       subgraph Stage3["Stage 3: Unit"]
           UT[unit-test]
       end

       subgraph Stage4["Stage 4: Molecule"]
           MOL[molecule-*]
       end

       subgraph Stage5["Stage 5: Integration"]
           INT[integration]
       end

       subgraph Stage6["Stage 6: Build"]
           BUILD[build]
       end

       Stage1 --> Stage2
       Stage2 --> Stage3
       Stage3 --> Stage4
       Stage4 --> Stage5
       Stage5 --> Stage6

       style Stage1 fill:#4285F4,stroke:#4285F4,color:#fff
       style Stage2 fill:#34A853,stroke:#34A853,color:#fff
       style Stage3 fill:#FBBC04,stroke:#FBBC04,color:#fff
       style Stage4 fill:#EA4335,stroke:#EA4335,color:#fff
       style Stage5 fill:#9C27B0,stroke:#9C27B0,color:#fff
       style Stage6 fill:#00BCD4,stroke:#00BCD4,color:#fff

**Runtime:** 15-25 minutes total

Linting Standards
~~~~~~~~~~~~~~~~~

**Use specific linters:**

* ✅ ``ansible-lint`` - Ansible code
* ✅ ``yamllint`` - YAML files
* ✅ ``markdownlint`` - Markdown
* ✅ ``ruff`` or ``black`` - Python
* ❌ **Super-Linter** - DO NOT USE

Release Process
~~~~~~~~~~~~~~~

.. danger::
   **ALWAYS update CHANGELOG.md before releasing!**

**Release checklist:**

1. **Update CHANGELOG.md** (REQUIRED)

   .. code-block:: markdown

      ## [Unreleased]

      ### Added
      - New feature

      ## [1.0.1] - 2026-01-17

      ### Fixed
      - Bug fix

2. **Update galaxy.yml version**

   .. code-block:: yaml

      version: "1.0.1"

3. **Create and push tag** (NO 'v' prefix for Ansible)

   .. code-block:: bash

      git tag 1.0.1
      git push origin 1.0.1

4. **Automated workflow triggers**

   * ``publish.yml`` publishes to Galaxy
   * Creates GitHub Release with CHANGELOG

Publish Workflow
~~~~~~~~~~~~~~~~

**Requirements:**

* Single consolidated ``publish.yml`` workflow
* Tag format without 'v' prefix: ``1.0.0`` (NOT ``v1.0.0``)
* Validate version matches galaxy.yml
* Check CHANGELOG entry exists
* Publish to Galaxy + Create GitHub Release

**Do NOT:**

* ❌ Create separate ``release.yml`` and ``publish.yml``
* ❌ Use ``release: [published]`` event
* ❌ Use 'v' prefix in tags (``1.0.0``, not ``v1.0.0``)

See :ref:`cicd` for complete workflow implementation.

Documentation
~~~~~~~~~~~~~

**Keep documentation DRY:**

1. **Collection README** - Overview + list all roles
2. **Role README** - Features + Quick Start + link to guide
3. **argument_specs.yml** - Complete variable documentation
4. **guide.arillso.io** - Comprehensive documentation

**Role README minimal structure:**

.. code-block:: markdown

   # Ansible Role: role_name

   Brief description.

   ## Features

   - Feature 1
   - Feature 2

   ## Documentation

   https://guide.arillso.io/collections/arillso/collection/role_role.html

   ## Quick Start

   ```yaml
   - hosts: servers
     roles:
       - role: arillso.collection.role_name
   ```

   ## License

   MIT

Version Variables
~~~~~~~~~~~~~~~~~

Use Renovate comments for automatic updates:

.. code-block:: yaml

   # renovate: datasource=github-releases depName=k3s-io/k3s
   k3s_version: "v1.33.3+k3s1"

   # renovate: datasource=github-releases depName=moby/moby
   docker_version: "27.5.1"

Go Project Standards
--------------------

See :ref:`contributing` for complete Go development standards, code style, testing requirements, and best practices.

Docker/Container Standards
--------------------------

See :ref:`contributing` for Dockerfile best practices, multi-stage builds, security requirements, and testing procedures.

AI Agent Documentation
----------------------

CLAUDE.md
~~~~~~~~~

.. code-block:: markdown

   @AGENTS.md

AGENTS.md Structure
~~~~~~~~~~~~~~~~~~~

.. code-block:: markdown

   # Project Name

   ## Context

   [What the project does, for AI]

   ## Conventions

   [Code style, patterns]

   ## Structure

   [Important folders/files]

   ## Do

   [Best practices]

   ## Do Not

   [What AI should avoid]

CHANGELOG Format
----------------

Required for all released projects. Use `Keep a Changelog <https://keepachangelog.com/>`_ format:

.. code-block:: markdown

   # Changelog

   ## [Unreleased]

   ### Added
   - New feature

   ## [1.0.0] - 2026-01-17

   ### Added
   - Feature X

   ### Fixed
   - Bug Y

**Sections:** Added, Changed, Deprecated, Removed, Fixed, Security

Issue Templates
---------------

Required for Ansible Collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**All collections need:**

1. **bug_report.yml** - Structured bug reports
2. **feature_request.yml** - Feature requests
3. **documentation.yml** - Documentation improvements

**Template should include:**

* Role/component dropdown
* Required fields with validation
* Code blocks with syntax highlighting
* Automatic labels
* Title prefixes

Pull Request Template
---------------------

Required for Ansible Collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Template sections:**

1. Description
2. Type of Change (bug fix, feature, breaking change, docs, etc.)
3. Related Issue
4. Which Role(s) Are Affected
5. Changes Made
6. Testing Performed
7. Documentation Updated
8. Code Quality Checklist
9. Breaking Changes (if applicable)

What NOT to Include
-------------------

Files to Avoid
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Reason
   * - ``docs/`` folder
     - README usually enough
   * - ``SECURITY.md``
     - Only for public packages if needed
   * - Multiple YAML configs
     - Keep one ``.yamllint.yml``

.. seealso::

   * :ref:`contributing` - How to contribute (code style, testing, development)
   * :ref:`cicd` - CI/CD workflows and linter configurations
   * :ref:`compatibility` - Version requirements and platform support
   * `STANDARDS.md on GitHub <https://github.com/arillso/.github/blob/main/STANDARDS.md>`_
