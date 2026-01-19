.. meta::
  :description: Contributing guidelines and development standards for arillso projects

.. _contributing:

Contributing
=======================

Thank you for your interest in contributing to arillso projects! This guide provides standards, guidelines, and best practices for all arillso repositories.

.. contents::
   :local:
   :depth: 2

General Guidelines
------------------

Code of Conduct
~~~~~~~~~~~~~~~

All arillso projects adhere to a Code of Conduct. By participating, you are expected to uphold this code. Be respectful, constructive, and inclusive in all interactions.

Prerequisites
~~~~~~~~~~~~~

**For Ansible Collections:**

* Ansible >= 2.15
* Python >= 3.9
* Git
* GitHub account

**For Go Projects:**

* Go >= 1.25
* Git
* GitHub account

**For Container Projects:**

* Docker with BuildKit
* Make (optional)

Types of Contributions
~~~~~~~~~~~~~~~~~~~~~~

We welcome various types of contributions:

* **Bug Reports** - Found a bug? Let us know!
* **Feature Requests** - Have an idea for improvement?
* **Documentation** - Improvements to docs are always appreciated
* **Code Contributions** - Bug fixes, new features, or improvements
* **Testing** - Platform testing and validation

Ansible Collection Standards
-----------------------------

File Organization
~~~~~~~~~~~~~~~~~

Each role must follow the standard structure defined in :ref:`standards`.

**Required structure:**

.. code-block:: text

   roles/ROLE_NAME/
   ├── defaults/
   │   └── main.yml          # User-configurable variables
   ├── handlers/
   │   └── main.yml          # Service restart handlers
   ├── meta/
   │   ├── main.yml          # Role metadata
   │   └── argument_specs.yml # REQUIRED: Variable specs
   ├── tasks/
   │   ├── main.yml          # Main entry point
   │   ├── install.yml       # Installation tasks
   │   ├── configure.yml     # Configuration tasks
   │   └── service.yml       # Service management
   ├── templates/
   │   └── ...               # Jinja2 templates
   ├── vars/
   │   ├── main.yml          # Internal variables
   │   ├── Debian.yml        # Debian-specific vars
   │   └── RedHat.yml        # RedHat-specific vars
   └── README.md             # Role documentation

Code Style
~~~~~~~~~~

**Good Example:**

.. code-block:: yaml

   - name: Install Grafana Alloy package
     ansible.builtin.package:
       name: "{{ alloy_package_name }}"
       state: "{{ alloy_package_state }}"
     register: alloy_install_result
     when: alloy_enabled | bool

**Bad Example:**

.. code-block:: yaml

   - name: install pkg
     package: name={{pkg}} state=present
     when: enabled

Best Practices
~~~~~~~~~~~~~~

1. **Use FQCN** (Fully Qualified Collection Names):

   .. code-block:: yaml

      # Good
      - name: Create directory
        ansible.builtin.file:
          path: /etc/app
          state: directory

      # Bad
      - name: Create directory
        file:
          path: /etc/app
          state: directory

2. **Proper YAML Indentation:**

   * Use 4 spaces for indentation (not tabs)
   * Be consistent throughout the file

3. **Meaningful Variable Names:**

   * Prefix with role name: ``alloy_*``, ``docker_*``, ``k3s_*``
   * Use descriptive names: ``alloy_prometheus_enabled`` not ``alloy_prom``
   * Booleans: Use ``*_enabled``, ``*_required``, etc.
   * Lists: Use plural names ``alloy_custom_exporters``
   * Dicts: Use singular names ``alloy_node_exporter_config``

4. **Task Organization:**

   * Separate tasks by function (install, configure, service)
   * Use ``include_tasks`` for modularity
   * Keep main.yml as entry point only

Variable Documentation
~~~~~~~~~~~~~~~~~~~~~~

All variables **MUST** be documented in three places:

**1. defaults/main.yml** - With inline comments:

.. code-block:: yaml

   # Enable Prometheus metrics collection
   alloy_prometheus_enabled: false

   # Prometheus remote write endpoint
   alloy_prometheus_remote_write_url: ""

**2. meta/argument_specs.yml** - With full specifications (REQUIRED):

.. code-block:: yaml

   argument_specs:
     main:
       short_description: Grafana Alloy configuration
       options:
         alloy_prometheus_enabled:
           type: bool
           required: false
           default: false
           description: Enable Prometheus metrics collection

**3. README.md** - With usage examples:

.. code-block:: markdown

   ### Prometheus Configuration

   ```yaml
   alloy_prometheus_enabled: true
   alloy_prometheus_remote_write_url: "https://prometheus.example.com/api/v1/write"
   ```

.. warning::
   Roles without ``argument_specs.yml`` will be rejected!

Testing Requirements
~~~~~~~~~~~~~~~~~~~~

**Before Submitting:**

1. **Lint your code:**

   .. code-block:: bash

      ansible-lint roles/ROLE_NAME/
      yamllint roles/ROLE_NAME/

2. **Test on supported platforms:**

   * Minimum: Test on one major platform
   * Ideal: Test on Ubuntu, Debian, and RHEL

3. **Verify collection builds:**

   .. code-block:: bash

      ansible-galaxy collection build --force
      ansible-galaxy collection install arillso-COLLECTION-*.tar.gz --force

4. **Test with minimal playbook:**

   .. code-block:: yaml

      ---
      - name: Test role
        hosts: localhost
        become: true
        roles:
          - role: arillso.COLLECTION.ROLE_NAME

5. **Verify idempotency:**

   * Running twice should not change anything
   * Check ``changed`` status

Release Process
~~~~~~~~~~~~~~~

.. important::
   **ALWAYS update CHANGELOG.md before releasing!**

**Release Checklist:**

1. **Update CHANGELOG.md** (REQUIRED)

   * Move items from ``[Unreleased]`` to new version section
   * Follow `Keep a Changelog <https://keepachangelog.com/>`_ format (see :ref:`standards`)
   * Categories: Added, Changed, Fixed, Deprecated, Removed, Security

2. **Update galaxy.yml version**

   .. code-block:: yaml

      version: "1.0.1"

3. **Create and push git tag**

   * Use version **without 'v' prefix** per :ref:`standards` (e.g., ``1.0.1`` not ``v1.0.1``)

   .. code-block:: bash

      git tag 1.0.1
      git push origin 1.0.1

4. **Automated workflows trigger**

   * ``publish.yml`` publishes to Ansible Galaxy (see :ref:`cicd` for workflow details)
   * Creates GitHub Release with CHANGELOG notes

Go Project Standards
--------------------

Code Style
~~~~~~~~~~

* Follow standard Go conventions (``gofmt``, ``golangci-lint``)
* Use ``context.Context`` for operations
* Error handling with ``github.com/pkg/errors`` for wrapped errors
* Struct-based configuration with defaults

Testing
~~~~~~~

.. code-block:: bash

   # Run all tests
   go test -v ./...

   # With coverage
   go test -cover ./...

   # Specific test
   go test -run TestPlaybook_Exec ./...

Documentation
~~~~~~~~~~~~~

* All public functions must have doc comments
* Include usage examples in package docs
* Keep README.md up-to-date

Docker/Container Standards
--------------------------

Dockerfile Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Multi-stage builds** for smaller images
2. **Non-root user** for security
3. **Version ranges** for Alpine packages:

   .. code-block:: dockerfile

      # Good - allows security patches
      RUN apk add --no-cache \
          python3>=3.11.0 \
          python3<4.0.0

4. **Multi-platform support** (amd64, arm64)

Testing
~~~~~~~

.. code-block:: bash

   make ansible-build       # Build container
   make test-quick          # Quick validation
   make comprehensive-test  # Full test suite
   make release-check       # Pre-release validation

GitHub Actions Standards
------------------------

Action Development
~~~~~~~~~~~~~~~~~~

1. **Use semantic inputs** - Clear, descriptive parameter names
2. **Provide examples** - Include usage examples in README
3. **Handle errors gracefully** - Validate inputs and provide clear errors
4. **Security first** - Use GitHub Secrets for sensitive data

Action.yml Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: 'Action Name'
   description: 'Clear description'
   inputs:
     input_name:
       description: 'Detailed description'
       required: false
       default: 'value'
   runs:
     using: 'docker'
     image: 'Dockerfile'

Commit Guidelines
-----------------

Commit Message Format
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Add feature description

   - Detailed point 1
   - Detailed point 2
   - Detailed point 3

   Fixes #123

**Format:**

* First line: Brief summary (50 chars or less)
* Blank line
* Detailed description with bullet points
* Reference related issues

**Examples:**

.. code-block:: text

   feat: add Faro configuration to Alloy role

   - Add alloy_enable_faro variable
   - Add Faro receiver template
   - Update README with examples

   Fixes #123

.. code-block:: text

   fix: correct SSH key normalization

   - Handle missing trailing newlines
   - Support all PEM formats
   - Add validation tests

   Closes #456

Pull Request Process
--------------------

1. Prepare Your Changes
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update from upstream
   git fetch upstream
   git rebase upstream/main

   # Run tests
   ansible-lint roles/ROLE_NAME/  # For Ansible
   go test ./...                   # For Go

2. Create Pull Request
~~~~~~~~~~~~~~~~~~~~~~

* Fill out all sections of PR template
* Link related issues
* Mark as draft if work in progress
* Provide test results

3. PR Review Process
~~~~~~~~~~~~~~~~~~~~

* Maintainer review
* Address feedback
* Ensure CI checks pass
* Require maintainer approval
* Maintainer merges when ready

4. After Merge
~~~~~~~~~~~~~~

.. code-block:: bash

   # Delete feature branch
   git branch -d feature/your-feature

   # Update fork
   git checkout main
   git pull upstream main
   git push origin main

Documentation Standards
-----------------------

README Structure
~~~~~~~~~~~~~~~~

Every project README should contain:

1. **Title and badges**
2. **Description** - What it does
3. **Features** - Key capabilities
4. **Installation** - How to install
5. **Quick Start** - Minimal example
6. **Configuration** - Available options
7. **Examples** - Real-world usage
8. **License** - MIT with copyright
9. **Contributing** - Link to guide

Inline Documentation
~~~~~~~~~~~~~~~~~~~~

* **Ansible:** Comment complex logic and non-obvious decisions
* **Go:** Doc comments on all exported functions
* **Docker:** Comment multi-stage builds and custom logic

Version Compatibility
---------------------

See :ref:`compatibility` for complete version requirements, platform support, and upgrade guides.

CI/CD Workflows
---------------

All repositories must have standardized CI/CD workflows.

See :ref:`cicd` for complete workflow implementations, linter configurations, and automation standards.

Security Guidelines
-------------------

Secrets Management
~~~~~~~~~~~~~~~~~~

* **Never commit secrets** to repositories
* Use GitHub Secrets for CI/CD
* Use Vault or secret managers in production
* Rotate credentials regularly

Dependency Management
~~~~~~~~~~~~~~~~~~~~~

* Keep dependencies up-to-date
* Use Renovate for automated updates
* Review security advisories
* Pin major versions, allow patches

Code Security
~~~~~~~~~~~~~

* Validate all inputs
* Sanitize user data
* Use parameterized queries
* Avoid command injection
* Follow OWASP guidelines

Getting Help
------------

If you have questions:

1. Check existing documentation
2. Search closed issues
3. Open a discussion on GitHub
4. Tag maintainers if needed

Community
---------

* **Be respectful** and constructive
* **Provide context** in issues and PRs
* **Be patient** - maintainers are volunteers
* **Celebrate contributions** - recognize others' work

Questions?
----------

Open a discussion on GitHub or check project-specific CONTRIBUTING.md files:

* `arillso.agent CONTRIBUTING.md <https://github.com/arillso/ansible.agent/blob/main/CONTRIBUTING.md>`_
* `arillso.container CONTRIBUTING.md <https://github.com/arillso/ansible.container/blob/main/CONTRIBUTING.md>`_
* `arillso.system CONTRIBUTING.md <https://github.com/arillso/ansible.system/blob/main/CONTRIBUTING.md>`_

.. seealso::

   * :ref:`standards` - Repository standards and conventions
   * :ref:`cicd` - CI/CD workflows and automation
   * :ref:`compatibility` - Version compatibility and requirements
   * :ref:`list_of_collections` - Ansible Collections
   * :ref:`list_of_containers` - Container Images
   * :ref:`list_of_libraries` - Go Libraries

---

**Thank you for contributing to arillso!**

Your contributions help make these projects better for everyone.
