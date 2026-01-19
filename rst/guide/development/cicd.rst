.. meta::
  :description: CI/CD workflows and linter configurations for arillso projects

.. _cicd:

CI/CD & Linting
===============

Standard GitHub Actions workflows and linter configurations used across all arillso projects.

.. contents::
   :local:
   :depth: 2

Workflow Standards
------------------

General Principles
~~~~~~~~~~~~~~~~~~

**All workflows must:**

1. **Pin actions to SHA digest** for security
2. **Use concurrency control** to cancel outdated runs
3. **Set minimal permissions** (``contents: read`` by default)
4. **Include path ignores** for documentation changes
5. **Support manual triggering** with ``workflow_dispatch``

Workflow Template Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   name: Workflow Name

   on:
     push:
       branches: [main]
       paths-ignore:
         - "**.md"
         - ".github/CODEOWNERS"
     pull_request:
       branches: [main]
     workflow_dispatch:

   concurrency:
     group: ${{ github.ref }}-${{ github.workflow }}
     cancel-in-progress: true

   permissions:
     contents: read

   jobs:
     job-name:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@<SHA> # v4

CI Workflow (ci.yml)
--------------------

Standard Linting Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

**For Go Projects:**

.. code-block:: yaml

   ---
   name: Continuous Integration

   on:
     push:
       branches: [main, "feature/**"]
       paths-ignore:
         - "**.md"
         - ".github/CODEOWNERS"
     pull_request:
       branches: [main]
     workflow_dispatch:

   concurrency:
     group: ${{ github.ref }}-${{ github.workflow }}
     cancel-in-progress: true

   jobs:
     golangci-lint:
       name: Go Lint
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Setup Go
           uses: actions/setup-go@d35c59abb061a4a6fb18e82ac0862c26744d6ab5 # v5
           with:
             go-version-file: go.mod
             cache: true

         - name: Run golangci-lint
           uses: golangci/golangci-lint-action@4afd733a84b1f43292c63897423277bb7f4313a9 # v8
           with:
             version: latest

     actionlint:
       name: Action Lint
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Run actionlint
           uses: reviewdog/action-actionlint@a5524e1c19e62881d79c1f1b9b6f09f16356e281 # v1
           with:
             reporter: github-pr-review
             fail_level: error

     shellcheck:
       name: Shell Lint
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Run ShellCheck
           uses: reviewdog/action-shellcheck@4c07458293ac342d477251099501a718ae5ef86e # v1.32.0
           with:
             reporter: github-pr-review
             fail_level: warning

     yamllint:
       name: YAML Lint
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Run yamllint
           uses: ibiqlik/action-yamllint@2576378a8e339169678f9939646ee3ee325e845c # v3
           with:
             config_file: .yamllint.yml
             strict: false

**For Ansible Collections:**

Complete workflow implementing the :ref:`standards` CI architecture.

.. code-block:: yaml

   ---
   name: Continuous Integration

   on:
     push:
       branches: [main]
       paths-ignore:
         - "**.md"
         - ".github/CODEOWNERS"
     pull_request:
       branches: [main]
     workflow_dispatch:

   concurrency:
     group: ${{ github.ref }}-${{ github.workflow }}
     cancel-in-progress: true

   jobs:
     # Stage 1: Linting (Parallel)
     ansible-lint:
       name: Ansible Lint
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Run ansible-lint
           uses: ansible/ansible-lint-action@c37fb7b4bda2c8cb18f4942716bae9f11b0dc9bc # v4

     yaml-lint:
       name: YAML Lint
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Run yamllint
           uses: ibiqlik/action-yamllint@2576378a8e339169678f9939646ee3ee325e845c # v3
           with:
             config_file: .yamllint.yml

     # Stage 2: Sanity Tests (depends on Stage 1)
     sanity-test:
       name: Sanity Tests
       runs-on: ubuntu-latest
       needs: [ansible-lint, yaml-lint]
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Setup Python
           uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b # v5
           with:
             python-version: "3.11"

         - name: Install ansible-core
           run: pip install ansible-core

         - name: Run sanity tests
           run: ansible-test sanity --docker

     # Stage 3: Unit Tests
     unit-test:
       name: Unit Tests
       runs-on: ubuntu-latest
       needs: [sanity-test]
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Setup Python
           uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b # v5
           with:
             python-version: "3.11"

         - name: Install dependencies
           run: pip install pytest pytest-cov

         - name: Run pytest
           run: pytest --cov --cov-report=xml

     # Stage 4: Molecule Tests
     molecule-test:
       name: Molecule Test
       runs-on: ubuntu-latest
       needs: [unit-test]
       strategy:
         matrix:
           distro: [ubuntu2204, debian12, rockylinux9]
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Run Molecule
           uses: gofrolist/molecule-action@a56fd09663ec28fbd1143f92db5a3711e9c26dc8 # v2
           with:
             molecule_command: test
             molecule_args: --scenario-name ${{ matrix.distro }}

     # Stage 5: Integration Tests
     integration-test:
       name: Integration Tests
       runs-on: ubuntu-latest
       needs: [molecule-test]
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Setup Python
           uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b # v5
           with:
             python-version: "3.11"

         - name: Install ansible-core
           run: pip install ansible-core

         - name: Run integration tests
           run: ansible-test integration --docker

     # Stage 6: Build
     build:
       name: Build Collection
       runs-on: ubuntu-latest
       needs: [integration-test]
       steps:
         - name: Checkout Code
           uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

         - name: Build collection
           run: ansible-galaxy collection build

         - name: Upload artifact
           uses: actions/upload-artifact@b4b15b8c7c6ac21ea08fcf65892d2ee8f75cf882 # v4
           with:
             name: collection
             path: "*.tar.gz"

**Architecture:** See :ref:`standards` for CI workflow structure diagram.

CodeQL Workflow (codeql.yml)
-----------------------------

Security Scanning
~~~~~~~~~~~~~~~~~

**Required for all public repositories** (see :ref:`standards`).

.. code-block:: yaml

   ---
   name: CodeQL Analysis

   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]
     schedule:
       - cron: "0 6 * * 1"  # Weekly Monday 06:00 UTC

   permissions:
     security-events: write
     contents: read

   jobs:
     analyze:
       name: Analyze Code
       runs-on: ubuntu-latest
       strategy:
         matrix:
           language: [go, python, javascript]
       steps:
         - name: Checkout Code
           uses: actions/checkout@<SHA> # v4

         - name: Initialize CodeQL
           uses: github/codeql-action/init@<SHA> # v3
           with:
             languages: ${{ matrix.language }}

         - name: Autobuild
           uses: github/codeql-action/autobuild@<SHA> # v3

         - name: Perform CodeQL Analysis
           uses: github/codeql-action/analyze@<SHA> # v3

**Features:**

* Weekly scheduled scans (Monday 06:00 UTC)
* Multi-language support (Go, Python, JavaScript)
* Automatic SARIF upload to GitHub Security

Deploy/Publish Workflow
-----------------------

For Docker/Actions (deploy.yml)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   name: Deploy

   on:
     push:
       tags:
         - "v*"  # v1.0.0, v2.1.3, etc.

   permissions:
     contents: write
     packages: write

   jobs:
     build-and-publish:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@<SHA> # v4

         - name: Docker meta
           id: meta
           uses: docker/metadata-action@<SHA> # v5
           with:
             images: ghcr.io/${{ github.repository }}
             tags: |
               type=semver,pattern={{version}}
               type=semver,pattern={{major}}.{{minor}}
               type=semver,pattern={{major}}

         - name: Login to GHCR
           uses: docker/login-action@<SHA> # v3
           with:
             registry: ghcr.io
             username: ${{ github.actor }}
             password: ${{ secrets.GITHUB_TOKEN }}

         - name: Build and push
           uses: docker/build-push-action@<SHA> # v6
           with:
             context: .
             push: true
             tags: ${{ steps.meta.outputs.tags }}
             platforms: linux/amd64,linux/arm64

         - name: Create GitHub Release
           uses: softprops/action-gh-release@<SHA> # v2
           with:
             generate_release_notes: true

**Features:**

* Triggered by version tags (``v1.0.0``)
* Multi-platform builds (amd64, arm64)
* Publishes to GitHub Container Registry
* Creates GitHub Release with auto-generated notes

For Ansible Collections (publish.yml)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Implementation of** :ref:`standards` **publish requirements.**

.. code-block:: yaml

   ---
   name: Publish Collection

   on:
     push:
       tags:
         - "[0-9]+.[0-9]+.[0-9]+"  # 1.0.0 (NO 'v' prefix per standards)

   permissions:
     contents: write

   jobs:
     publish:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@<SHA> # v4

         - name: Get version from tag
           id: get_version
           run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

         - name: Verify galaxy.yml version
           run: |
             VERSION="${{ steps.get_version.outputs.VERSION }}"
             GALAXY_VERSION=$(grep '^version:' galaxy.yml | awk '{print $2}')
             if [ "$VERSION" != "$GALAXY_VERSION" ]; then
               echo "Error: Version mismatch!"
               exit 1
             fi

         - name: Check CHANGELOG entry
           run: |
             VERSION="${{ steps.get_version.outputs.VERSION }}"
             if ! grep -q "## \[$VERSION\]" CHANGELOG.md; then
               echo "Error: No CHANGELOG entry"
               exit 1
             fi

         - name: Extract changelog
           id: changelog
           run: |
             VERSION="${{ steps.get_version.outputs.VERSION }}"
             sed -n "/## \[$VERSION\]/,/## \[/p" CHANGELOG.md | sed '$d' > /tmp/changelog.txt

         - name: Build and Publish
           uses: artis3n/ansible_galaxy_collection@<SHA> # v2
           with:
             api_key: ${{ secrets.GALAXY_API_KEY }}

         - name: Create GitHub Release
           uses: softprops/action-gh-release@<SHA> # v2
           with:
             body_path: /tmp/changelog.txt

**Features:**

* Tag format without 'v' prefix (``1.0.0``)
* Version validation (tag = galaxy.yml)
* CHANGELOG validation
* Automatic changelog extraction
* Publishes to Ansible Galaxy
* Creates GitHub Release

Linter Configurations
---------------------

YAML Lint (.yamllint.yml)
~~~~~~~~~~~~~~~~~~~~~~~~~

**Standard configuration for all projects:**

.. code-block:: yaml

   ---
   extends: default
   rules:
     braces:
       max-spaces-inside: 1
     new-lines:
       level: warning
       type: unix
     line-length:
       max: 500
     comments:
       min-spaces-from-content: 1
     truthy:
       allowed-values: ["true", "false", "on"]

**Key settings:**

* Line length: 500 characters (for long URLs)
* Unix line endings
* Truthy values: ``true``, ``false``, ``on`` only

Go Lint (.golangci.yml)
~~~~~~~~~~~~~~~~~~~~~~~

**Standard configuration for Go projects:**

.. code-block:: yaml

   ---
   version: "2"
   linters:
     default: standard
     enable:
       - gocritic
   formatters:
     enable:
       - gofmt
       - goimports

**Features:**

* Standard linter set
* ``gocritic`` for advanced checks
* Auto-formatting with ``gofmt`` and ``goimports``

Ansible Lint (.ansible-lint)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For Ansible Collections:**

.. code-block:: yaml

   ---
   profile: production
   strict: true
   offline: false

   skip_list:
     - yaml[line-length]  # Already covered by yamllint
     - name[casing]       # Allow flexible task naming

   warn_list:
     - experimental       # Warn on experimental features

   exclude_paths:
     - .github/
     - .ansible/
     - molecule/
     - tests/

**Profile levels:**

* ``min`` - Minimal checks
* ``basic`` - Basic checks
* ``moderate`` - More comprehensive
* ``safety`` - Safety-focused
* ``production`` - Strictest (recommended)

EditorConfig (.editorconfig)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Universal editor settings:**

.. code-block:: ini

   root = true

   [*]
   charset = utf-8
   end_of_line = lf
   insert_final_newline = true
   trim_trailing_whitespace = true
   indent_style = space
   indent_size = 4

   [*.{yml,yaml}]
   indent_size = 2

   [*.md]
   trim_trailing_whitespace = false

   [Makefile]
   indent_style = tab

Common Linter Commands
----------------------

Local Testing
~~~~~~~~~~~~~

**Before committing, run:**

.. code-block:: bash

   # YAML linting
   yamllint .

   # Go linting
   golangci-lint run

   # Ansible linting
   ansible-lint

   # Shell script linting
   shellcheck scripts/*.sh

   # Action linting
   actionlint .github/workflows/*.yml

Install Linters
~~~~~~~~~~~~~~~

.. code-block:: bash

   # YAML
   pip install yamllint

   # Go
   go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

   # Ansible
   pip install ansible-lint

   # Shell
   brew install shellcheck  # macOS
   apt install shellcheck   # Ubuntu/Debian

   # GitHub Actions
   brew install actionlint  # macOS
   go install github.com/rhysd/actionlint/cmd/actionlint@latest

Pre-commit Hooks
----------------

Optional but Recommended
~~~~~~~~~~~~~~~~~~~~~~~~

**Create** ``.pre-commit-config.yaml``:

.. code-block:: yaml

   ---
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v5.0.0
       hooks:
         - id: trailing-whitespace
         - id: end-of-file-fixer
         - id: check-yaml
         - id: check-merge-conflict

     - repo: https://github.com/adrienverge/yamllint
       rev: v1.35.1
       hooks:
         - id: yamllint

     - repo: https://github.com/ansible/ansible-lint
       rev: v24.12.2
       hooks:
         - id: ansible-lint
           files: \.(yaml|yml)$

**Install:**

.. code-block:: bash

   pip install pre-commit
   pre-commit install

**Run manually:**

.. code-block:: bash

   pre-commit run --all-files

GitHub Actions Best Practices
------------------------------

SHA Pinning
~~~~~~~~~~~

**Implementation of arillso security standards** (see :ref:`standards`): All actions must be SHA-pinned.

.. code-block:: yaml

   # ✅ Correct - Pinned to SHA with version comment
   - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

   # ❌ Wrong - Mutable reference
   - uses: actions/checkout@v4
   - uses: actions/checkout@main

**Why:**

* Prevents supply chain attacks
* Ensures immutable versions
* Renovate manages updates automatically

**How to get SHA:**

.. code-block:: bash

   # Get latest SHA for a specific version
   gh api repos/actions/checkout/commits/v4 --jq '.sha'

   # Get latest SHA from main branch
   gh api repos/actions/checkout/commits/main --jq '.sha'

**Renovate handles updates automatically** when configured with ``renovate-actions`` preset.

Caching
~~~~~~~

**Speed up workflows with caching:**

.. code-block:: yaml

   - name: Setup Go
     uses: actions/setup-go@<SHA> # v5
     with:
       go-version-file: go.mod
       cache: true  # Automatic Go module caching

   - name: Setup Python
     uses: actions/setup-python@<SHA> # v5
     with:
       python-version: "3.11"
       cache: "pip"  # Automatic pip caching

Matrix Testing
~~~~~~~~~~~~~~

**Test across multiple versions:**

.. code-block:: yaml

   jobs:
     test:
       strategy:
         matrix:
           go-version: [1.21, 1.22, 1.23]
           os: [ubuntu-latest, macos-latest]
       runs-on: ${{ matrix.os }}
       steps:
         - uses: actions/setup-go@<SHA>
           with:
             go-version: ${{ matrix.go-version }}

Concurrency Control
~~~~~~~~~~~~~~~~~~~

**Prevent wasted CI time:**

.. code-block:: yaml

   concurrency:
     group: ${{ github.ref }}-${{ github.workflow }}
     cancel-in-progress: true

**Effect:**

* Cancels outdated workflow runs
* Saves CI minutes
* Faster feedback on latest push

Conditional Steps
~~~~~~~~~~~~~~~~~

**Run steps conditionally:**

.. code-block:: yaml

   - name: Upload coverage
     if: matrix.go-version == '1.23'
     uses: codecov/codecov-action@<SHA>

   - name: Run on main only
     if: github.ref == 'refs/heads/main'
     run: ./deploy.sh

Path Filters
~~~~~~~~~~~~

**Skip workflows for doc changes:**

.. code-block:: yaml

   on:
     push:
       paths-ignore:
         - "**.md"
         - "docs/**"
         - ".github/CODEOWNERS"

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**1. SHA mismatch errors:**

Solution: Update action SHA to latest version

.. code-block:: bash

   # Get latest SHA
   gh api repos/actions/checkout/commits/main --jq '.sha'

**2. Linter conflicts:**

Solution: Configure linters to avoid overlap

.. code-block:: yaml

   # .ansible-lint
   skip_list:
     - yaml[line-length]  # Already in yamllint

**3. Permission errors:**

Solution: Add required permissions

.. code-block:: yaml

   permissions:
     contents: write
     packages: write
     security-events: write

**4. Cache not working:**

Solution: Verify cache key and paths

.. code-block:: yaml

   - uses: actions/cache@<SHA>
     with:
       path: ~/.cache/go-build
       key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}

Debugging Workflows
~~~~~~~~~~~~~~~~~~~

**Enable debug logging:**

.. code-block:: bash

   # In repository settings, add secrets:
   ACTIONS_RUNNER_DEBUG=true
   ACTIONS_STEP_DEBUG=true

**Add debug steps:**

.. code-block:: yaml

   - name: Debug info
     run: |
       echo "Event: ${{ github.event_name }}"
       echo "Ref: ${{ github.ref }}"
       echo "SHA: ${{ github.sha }}"
       env

.. seealso::

   * :ref:`standards` - Repository Standards
   * :ref:`contributing` - Contributing Guidelines
   * `GitHub Actions Templates <https://github.com/arillso/.github/tree/main/templates/workflows>`_
