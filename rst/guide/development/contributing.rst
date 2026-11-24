.. meta::
  :description: How to contribute to the arillso collections, container image, GitHub Action and Go library

.. _contributing:

Contributing
============

Rules that apply across the arillso repositories. Each repository has its own
``CONTRIBUTING.md`` with the exact setup; where it differs from this page, the
repository file wins.

.. contents::
   :local:
   :depth: 2

Repositories
------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Repository
     - Content
   * - `arillso/ansible.system <https://github.com/arillso/ansible.system>`_
     - Collection ``arillso.system``
   * - `arillso/ansible.container <https://github.com/arillso/ansible.container>`_
     - Collection ``arillso.container``
   * - `arillso/ansible.agent <https://github.com/arillso/ansible.agent>`_
     - Collection ``arillso.agent``
   * - `arillso/docker.ansible <https://github.com/arillso/docker.ansible>`_
     - Container image ``arillso/ansible``
   * - `arillso/action.playbook <https://github.com/arillso/action.playbook>`_
     - GitHub Action ``arillso/action.playbook``
   * - `arillso/go.ansible <https://github.com/arillso/go.ansible>`_
     - Go module ``github.com/arillso/go.ansible/v2``

The organisation-wide code of conduct, security policy and pull request
template live in `arillso/.github <https://github.com/arillso/.github>`_.

Prerequisites
-------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Repository type
     - Requirements (from the repository's ``CONTRIBUTING.md``)
   * - Ansible collections
     - Ansible >= 2.18, Python >= 3.12 (arillso.system: 3.13, the version
       its CI runs), Git, Docker for tests; arillso.container needs QEMU with
       KVM for Molecule
   * - Go library and action
     - Go version from the ``go`` directive in ``go.mod``, Git; Docker for
       the action
   * - Container image
     - Docker, Make

All repositories use `lefthook <https://github.com/evilmartians/lefthook>`_
for Git hooks. Run ``lefthook install`` once after cloning; see
:ref:`cicd` for what the hooks check.

Workflow
--------

1. Fork the repository and clone it:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/ansible.system.git
      cd ansible.system
      git remote add upstream https://github.com/arillso/ansible.system.git

2. Create a branch named after the change type, for example
   ``feat/your-topic`` or ``fix/your-topic``.
3. Run ``make lint`` and ``make test`` and fix all findings.
4. Add an entry under ``[Unreleased]`` in ``CHANGELOG.md``.
5. Open a pull request against ``main`` and fill in the template.

A maintainer reviews the pull request. All CI checks must pass and at least
one maintainer approval is required before merge. The CI jobs are described
in :ref:`cicd`.

Commit Messages
---------------

`Conventional Commits <https://www.conventionalcommits.org/>`_: a type, an
optional scope (role, plugin or area) and an imperative summary in lower
case.

.. code-block:: text

   fix(firewall): reload nftables after config validation

   Optional body: what changes for users and why.

   Fixes #123

Common types are ``feat``, ``fix``, ``docs``, ``test``, ``ci``, ``chore`` and
``refactor``. A change that requires users to adapt playbooks or variables is
breaking: add ``!`` after the scope (``fix(tuning)!: ...``) and a
``BREAKING CHANGE:`` footer with the migration step.

Ansible Collections
-------------------

Role Layout
~~~~~~~~~~~

.. code-block:: text

   roles/ROLE_NAME/
   ├── defaults/
   │   └── main.yml              # User-configurable variables
   ├── handlers/
   │   └── main.yml              # Service handlers
   ├── meta/
   │   ├── main.yml              # Role metadata, platforms
   │   └── argument_specs.yml    # Variable specifications
   ├── tasks/
   │   ├── main.yml              # Entry point
   │   ├── install.yml
   │   ├── configure.yml
   │   └── service.yml
   ├── templates/
   ├── vars/
   │   ├── Debian.yml
   │   └── RedHat.yml
   └── README.md

Molecule scenarios live in ``extensions/molecule/<role>/`` in arillso.system
and in ``roles/<role>/molecule/`` in arillso.container and arillso.agent. The
design rules behind this layout are in :ref:`ansible-roles`.

Rules
~~~~~

* Tasks are idempotent; a second run must not report changes.
* Modules are called by their fully qualified name
  (``ansible.builtin.template``, not ``template``).
* Variables are prefixed with the role name and documented in
  ``defaults/main.yml``.
* Every role has ``meta/argument_specs.yml``. CI validates it in the
  *Argument Specs Check* job, and the role pages of this guide are generated
  from it.
* Service restarts and reloads go through handlers.
* YAML uses four spaces, starts with ``---`` and stays under 500 characters
  per line (``.yamllint.yml``).
* Python plugins follow PEP 8 with a line length of 100 (black, ruff).

Example task:

.. code-block:: yaml

   - name: Install Grafana Alloy package
     ansible.builtin.package:
         name: "{{ alloy_package_name }}"
         state: "{{ alloy_package_state }}"

Testing
~~~~~~~

.. code-block:: bash

   make lint            # ansible-lint, yamllint, ruff/black
   make test            # pytest unit suite
   make test-molecule   # every Molecule scenario (slow)
   make build           # ansible-galaxy collection build

``make test`` runs ``pytest`` directly. CI runs ``ansible-test units
--docker`` instead, so a green local run does not guarantee a green CI run.

Release
~~~~~~~

Maintainers only.

1. Move the ``[Unreleased]`` entries in ``CHANGELOG.md`` to a new
   ``## [X.Y.Z]`` section.
2. Set ``version`` in ``galaxy.yml`` to the same version.
3. Tag without ``v`` prefix and push the tag:

   .. code-block:: bash

      git tag 2.0.5
      git push origin 2.0.5

``tag.yml`` refuses the release if the tag and ``galaxy.yml`` differ or the
changelog section is missing, then publishes to Ansible Galaxy and creates
the GitHub Release.

Go Library and Action
---------------------

* Format with ``gofmt``/``goimports``; ``golangci-lint`` runs with the
  repository's ``.golangci.yml``.
* go.ansible: use ``context.Context`` for command execution and
  cancellation, wrap errors with the standard library (``fmt.Errorf`` with
  ``%w``).
* Document exported functions and types.
* action.playbook: expose Ansible options as action inputs named after the
  Ansible CLI flags and document every input in ``action.yml``.

.. code-block:: bash

   make lint
   make test

Release tags: ``vX.Y.Z`` for go.ansible, ``X.Y.Z`` without prefix for
action.playbook. Both release from ``tag.yml`` after a ``CHANGELOG.md``
update.

Container Image
---------------

The ``Dockerfile`` of ``arillso/ansible`` is a multi-stage build on Alpine,
runs as ``USER 1000:1000`` and constrains Alpine packages with version ranges
(for example ``python3>=3.14.10-r1``) so security patches still apply.

.. code-block:: bash

   make ansible-build        # build the image
   make test-quick           # basic tests
   make comprehensive-test   # structure, security, performance,
                             # integration, unit and upgrade tests
   make release-check        # comprehensive-test as release gate

There is no manual release: a merge to ``main`` that changes ``Dockerfile``
or ``requirements.txt`` builds and publishes the image (see :ref:`cicd`).

Security
--------

* Report vulnerabilities by email to ``security@arillso.io``, not as public
  issues.
* Do not commit secrets. Gitleaks runs in the pre-commit and pre-push hooks
  and in CI.

.. seealso::

   * :ref:`standards` - Repository Standards
   * :ref:`ansible-roles` - Role and Collection Design
   * :ref:`cicd` - CI/CD & Linting
   * :ref:`compatibility` - Version Compatibility
   * :ref:`list_of_collections` - Ansible Collections
   * :ref:`list_of_containers` - Container Images
   * :ref:`list_of_libraries` - Go Libraries
