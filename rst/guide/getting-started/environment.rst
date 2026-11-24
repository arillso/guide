.. meta::
  :description: Development environment for working on the arillso Ansible collections
  :keywords: arillso, development, environment, lefthook, molecule, ansible-lint

.. _environment:

Development Environment
=======================

Tools and configuration used in the collection repositories
``arillso/ansible.system``, ``arillso/ansible.container`` and
``arillso/ansible.agent``. Each repository ships these files itself; this
page describes what is there.

.. contents::
   :local:
   :depth: 2

Requirements
------------

* Python in the version pinned in ``.python-version``
* Git
* Docker, for Molecule scenarios
* `Lefthook <https://github.com/evilmartians/lefthook>`_ for the Git hooks
* Node.js (``npx``), used by the ``prettier`` and ``markdownlint`` hooks
* ``gitleaks`` and ``actionlint`` as system binaries for the hooks

Setup
-----

.. code-block:: bash

   git clone https://github.com/arillso/ansible.system.git
   cd ansible.system

   python3 -m venv .venv
   source .venv/bin/activate
   make install-dev      # pip install -r requirements.txt

   lefthook install

``requirements.txt`` installs ``ansible-core>=2.18.0``, ``ansible-lint``,
``yamllint``, ``ruff``, ``black``, ``molecule``,
``molecule-plugins[docker]``, ``molecule-qemu``, ``pytest``,
``pytest-ansible`` and ``pytest-cov``. ``arillso.system`` adds ``tomli-w``
for its TOML filters.

Make targets
------------

``make help`` lists the targets of the current repository. Shared by all
three collections:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Target
     - Action
   * - ``install-dev``
     - ``pip install -r requirements.txt``
   * - ``lint``
     - Runs ``lint-ansible``, ``lint-yaml`` and ``lint-python``
       (``ansible-lint``, ``yamllint .``, ``ruff``/``black`` on
       ``plugins/``). Linters that are not installed are skipped; CI is
       the gate.
   * - ``format``
     - ``black plugins/``
   * - ``build``
     - ``ansible-galaxy collection build --force``
   * - ``clean``
     - Removes build artifacts

Test targets differ: ``ansible.system`` has ``test-unit``, ``coverage``,
``test-integration`` and ``test-molecule``; ``ansible.agent`` has
``test-unit`` and ``test-molecule``; ``ansible.container`` has ``test`` (``pytest tests/unit/``).

Molecule
--------

Scenario locations:

* ``ansible.system``, ``ansible.agent``: ``extensions/molecule/<scenario>/``
* ``ansible.container``: ``roles/<role>/molecule/default/``

``make test-molecule`` runs every scenario and skips those whose driver
is unavailable, for example when Docker is not running.

Git hooks
---------

``lefthook.yml`` defines the hooks:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Hook
     - Command
     - Files
   * - pre-commit
     - ``prettier --check``
     - ``*.{json,yml,yaml,md}``
   * - pre-commit
     - ``yamllint -c .yamllint.yml``
     - ``*.{yml,yaml}``
   * - pre-commit
     - ``markdownlint-cli2``
     - ``*.md``
   * - pre-commit
     - ``ansible-lint --profile=production``
     - ``{roles,plugins,tests,meta}/**/*.{yml,yaml}``
   * - pre-commit
     - ``actionlint``
     - ``.github/workflows/*.{yml,yaml}``
   * - pre-commit
     - ``gitleaks git --staged``
     - staged changes
   * - pre-push
     - ``gitleaks git``
     - full history

``ansible.container`` runs ``ansible-lint`` with ``--offline`` in the hook.
Files under ``.ansible/`` are excluded.

Configuration files
-------------------

.editorconfig
~~~~~~~~~~~~~

As in ``ansible.system`` and ``ansible.container`` (``ansible.agent`` adds
``indent_size = 2`` for JSON):

.. code-block:: ini

   root = true

   [*]
   indent_style = space
   indent_size = 4
   end_of_line = lf
   charset = utf-8
   trim_trailing_whitespace = true
   insert_final_newline = true

   [*.{yml,yaml}]
   indent_size = 4

   [*.{json,json5}]
   indent_size = 4

   [*.md]
   trim_trailing_whitespace = false

   [Makefile]
   indent_style = tab

.yamllint.yml
~~~~~~~~~~~~~

Identical in all three repositories. It extends ``default`` with:

* indentation of 4 spaces, sequences indented
* ``line-length`` 500, as warning
* ``truthy`` allows only ``true`` and ``false``
* ``document-start`` required, ``document-end`` forbidden
* implicit and explicit octal values forbidden
* ignores ``.ansible/``, ``.github/``, ``.venv/``, ``venv/``, ``.tox/``

.ansible-lint
~~~~~~~~~~~~~

All three repositories exclude ``.ansible/``, ``.github/``, ``.venv/`` and
``venv/`` and skip ``galaxy[version-incorrect]``,
``command-instead-of-module``, ``no-handler`` and ``package-latest``.

* ``ansible.system``: warns on ``name[casing]`` and ``yaml[line-length]``
* ``ansible.container``: ``profile: production``, ``strict: true``, warns
  on ``name[casing]`` and ``yaml[line-length]``
* ``ansible.agent``: ``profile: production``, ``strict: true``

The pre-commit hook applies the ``production`` profile in every
repository.

Running in the container image
------------------------------

The :ref:`arillso/ansible <docker_ansible>` image runs as user
``ansible`` (UID 1000) and contains ``ansible-core`` but not
``ansible-lint`` or Molecule. Use it to run playbooks against test hosts:

.. code-block:: bash

   docker run --rm -it \
     -v "$PWD":/workspace -w /workspace \
     arillso/ansible bash

Editor
------

``.editorconfig`` covers indentation and line endings in most editors.
For VS Code, the Red Hat Ansible extension (``redhat.ansible``) runs
``ansible-lint`` and picks up ``.ansible-lint`` from the repository root.

.. seealso::

   * :ref:`quickstart` - Install and use the collections
   * :ref:`standards` - Repository standards
   * :ref:`contributing` - Contribution workflow
   * :ref:`cicd` - CI workflows
