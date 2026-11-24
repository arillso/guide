.. meta::
  :description: How the arillso collections, container image, GitHub Action and Go library fit together
  :keywords: arillso, architecture, dependencies, collections, container image, ci

.. _architecture:

Architecture
============

How the arillso projects depend on each other, how the collection roles
are structured, and how the projects are built and released.

.. contents::
   :local:
   :depth: 2

Projects and dependencies
-------------------------

.. mermaid::

   flowchart LR
       system["arillso.system"]
       container["arillso.container"]
       agent["arillso.agent"]
       image["arillso/ansible image"]
       goansible["go.ansible"]
       action["action.playbook"]

       container -->|galaxy.yml dependency| system
       agent -->|galaxy.yml dependency| system
       action -->|Go module| goansible
       action -->|runtime base image| image

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Project
     - Depends on (source)
   * - ``arillso.system``
     - ``ansible.posix``, ``community.general``, ``community.crypto``
       (``galaxy.yml``); ``ansible-core>=2.18.0`` (``meta/runtime.yml``)
   * - ``arillso.container``
     - ``arillso.system``, ``community.docker`` (``galaxy.yml``);
       ``ansible-core>=2.18.0``
   * - ``arillso.agent``
     - ``arillso.system`` (``galaxy.yml``); ``ansible-core>=2.18.0``
   * - ``arillso/ansible``
     - Alpine Linux base; ``ansible-core``, Mitogen and Python libraries
       from ``requirements.txt``; ``kubectl``, ``helm``, ``kustomize``
       from Alpine packages (``Dockerfile``)
   * - ``action.playbook``
     - ``github.com/arillso/go.ansible/v2`` (``go.mod``); final stage
       ``FROM arillso/ansible`` (``Dockerfile``)
   * - ``go.ansible``
     - Calls the ``ansible-playbook`` and ``ansible-galaxy`` binaries; it
       does not bundle Ansible

The container image does not contain the arillso collections. Playbooks
that use them install the collections at run time, for example through
the ``galaxy_file`` input of the action.

Collections
-----------

Content per collection:

.. list-table::
   :header-rows: 1
   :widths: 22 39 39

   * - Collection
     - Roles
     - Plugins
   * - :ref:`arillso.system <plugins_in_arillso.system>`
     - ``access``, ``ansible``, ``bitwarden_secrets``, ``facts``,
       ``firewall``, ``logging``, ``network``, ``packages``, ``python``,
       ``ready``, ``shell``, ``systemd``, ``thermal``, ``tuning``, ``zram``
     - Modules ``apt_update_info``, ``reboot_info``; filters
       ``from_toml``, ``to_toml``, ``to_nice_toml``,
       ``to_nftables_hierarchy``, ``to_nftables_ports``,
       ``to_nftables_rule``; lookups ``environment_files``,
       ``github_latest_release``
   * - :ref:`arillso.container <plugins_in_arillso.container>`
     - ``docker``, ``docker_compose_v2``, ``docker_login``, ``fleet``,
       ``helm``, ``k3s``, ``tailscale``
     - Filters ``apt_version_pin``, ``fleet_transform_targets``,
       ``to_camel_case``
   * - :ref:`arillso.agent <plugins_in_arillso.agent>`
     - ``alloy``, ``do``, ``tailscale``
     - Filter ``apt_version_pin``

Two roles are named ``tailscale``: ``arillso.agent.tailscale`` installs
the Tailscale client on a host, ``arillso.container.tailscale`` manages
Tailscale resources in a Kubernetes cluster through a kubeconfig.

Role layout
~~~~~~~~~~~

The collection ``CONTRIBUTING.md`` files define this layout:

.. code-block:: text

   roles/<role>/
   ├── defaults/main.yml          # user-configurable variables
   ├── handlers/main.yml
   ├── meta/
   │   ├── main.yml               # platforms, min_ansible_version
   │   └── argument_specs.yml     # variable specification
   ├── tasks/main.yml
   ├── templates/
   └── vars/                      # per-OS variables

* Variables carry the role name as prefix (``packages_list``,
  ``k3s_version``).
* ``meta/argument_specs.yml`` is the source of the role pages in this
  guide; Ansible validates role variables against it at run time.
* ``meta/main.yml`` lists the supported platforms per role: Debian,
  Ubuntu and, for most roles, Enterprise Linux.

Entry points
~~~~~~~~~~~~

Several roles define more than one entry point in
``meta/argument_specs.yml``. Each entry point is a task file that can be
run on its own with ``tasks_from``:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Role
     - Entry points besides ``main``
   * - :ref:`arillso.system.packages <ansible_collections.arillso.system.packages_role>`
     - ``apt_config``, ``cache``, ``clean``, ``hold``, ``install``,
       ``keys``, ``packages``, ``remove``, ``repositories``, ``unhold``,
       ``upgrade``
   * - :ref:`arillso.system.access <ansible_collections.arillso.system.access_role>`
     - ``groups``, ``ssh``, ``ssh_keys``, ``sudoers``, ``users``
   * - :ref:`arillso.system.systemd <ansible_collections.arillso.system.systemd_role>`
     - ``journald``, ``service``, ``unit``
   * - :ref:`arillso.system.network <ansible_collections.arillso.system.network_role>`
     - ``dns``, ``netplan``
   * - :ref:`arillso.system.logging <ansible_collections.arillso.system.logging_role>`
     - ``logrotate``, ``rsyslog``
   * - :ref:`arillso.system.python <ansible_collections.arillso.system.python_role>`
     - ``pip``, ``requirements``
   * - :ref:`arillso.container.k3s <ansible_collections.arillso.container.k3s_role>`
     - ``agent``, ``server_init``, ``server_join``
   * - :ref:`arillso.container.fleet <ansible_collections.arillso.container.fleet_role>`
     - ``auth``, ``bundles``, ``clusters``, ``gitrepos``,
       ``registration_tokens``, ``workspaces``
   * - :ref:`arillso.agent.alloy <ansible_collections.arillso.agent.alloy_role>`
     - ``configure``, ``install``, ``service``

.. code-block:: yaml

   - name: Install packages only
     ansible.builtin.include_role:
       name: arillso.system.packages
       tasks_from: install
     vars:
       packages_list:
         - name: git

Container image
---------------

``arillso/ansible`` (``Dockerfile`` in ``arillso/docker.ansible``):

* Multi-stage build on Alpine Linux. The builder stage creates a Python
  virtual environment under ``/pipx/venvs/ansible``; the production stage
  copies it.
* Runs as ``ansible`` (UID/GID 1000), ``/sbin/tini`` is PID 1,
  ``STOPSIGNAL SIGINT``.
* ``/etc/ansible/ansible.cfg`` sets ``host_key_checking = False``,
  ``pipelining = True`` and registers the Mitogen strategy path without
  making it the default.
* Published to Docker Hub (``arillso/ansible``) and
  ``ghcr.io/arillso/ansible`` for ``linux/amd64`` and ``linux/arm64``.
  Tags: ``latest``, the ``ansible-core`` version, and the version with a
  commit SHA suffix.

Details: :ref:`docker_ansible`.

GitHub Action
-------------

``action.playbook`` is a Docker action. ``action.yml`` points to the
prebuilt image ``ghcr.io/arillso/action.playbook``; that image contains a
Go binary built on ``go.ansible`` and is based on ``arillso/ansible``.
The binary maps the action inputs to ``ansible-galaxy`` and
``ansible-playbook`` arguments. Outputs are ``status`` and
``exit_code``. Details: :ref:`action_playbook`.

Go library
----------

``go.ansible`` (module ``github.com/arillso/go.ansible/v2``) exposes
``NewPlaybook()`` and a ``Config`` struct. ``Playbook.Exec(ctx)``
optionally installs Galaxy requirements and then runs
``ansible-playbook`` with arguments built from ``Config``. SSH keys and
vault passwords are written to temporary files in ``Config.TempDir``
(default ``os.TempDir()``). Details: :ref:`go_ansible`.

Build and release
-----------------

All repositories call reusable workflows from ``arillso/.github``.

.. list-table::
   :header-rows: 1
   :widths: 22 26 52

   * - Repository
     - Trigger
     - Reusable workflows
   * - Collections
     - pull request
     - ``ci-ansible-collection``, ``ci-ansible-molecule`` (one job per
       scenario), ``security-secrets``, ``ai-claude-review``;
       ``ansible.container`` also ``security-deps``
   * - Collections
     - push to ``main``
     - ``ci-ansible-collection``, ``security-secrets``
   * - Collections
     - tag
     - ``release-ansible-collection``: checks the tag against
       ``version`` in ``galaxy.yml``, publishes to Ansible Galaxy and
       creates a GitHub release
   * - Collections
     - schedule
     - Security workflows; the set differs per repository
       (``security-secrets``, ``security-config``, ``security-sbom``,
       ``security-code`` or ``security-codeql``)
   * - ``docker.ansible``
     - push to ``main``
     - Builds and pushes the image to Docker Hub and GHCR
   * - ``docker.ansible``
     - schedule
     - ``security-codeql`` and a Trivy scan of the image
   * - ``action.playbook``
     - tag
     - Builds and pushes ``ghcr.io/arillso/action.playbook``,
       ``security-sbom``
   * - ``go.ansible``
     - pull request
     - ``ci-go``, ``ci-lint``, ``security-secrets``, ``security-deps``,
       ``ai-claude-review``

This guide
----------

This site is built by ``build.sh`` in ``arillso/guide``. It fetches the
collection versions pinned in ``versions.env`` (updated by Renovate),
renders the role and plugin pages with ``antsibull-docs`` from the
collections' ``argument_specs.yml`` and plugin documentation, and runs
Sphinx with ``-W``.

.. seealso::

   * :ref:`quickstart` - Install and use the collections
   * :ref:`environment` - Development setup for the collections
   * :ref:`cicd` - CI/CD workflows
   * :ref:`standards` - Repository standards
