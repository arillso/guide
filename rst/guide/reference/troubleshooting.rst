.. meta::
  :description: Troubleshooting arillso collections: installation, role lookup, firewall, packages, Docker, K3s and Grafana Alloy
  :keywords: arillso, troubleshooting, faq, debugging, errors

.. _troubleshooting:

Troubleshooting & FAQ
=====================

Known failure modes of the arillso collections and how to diagnose them.
Role-specific notes come from the role READMEs and task files of the
documented releases (see :ref:`compatibility`).

.. contents::
   :local:
   :depth: 2

Installation
------------

Collection or Dependency Not Found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ansible-galaxy`` installs the dependencies declared in ``galaxy.yml``
(for example ``ansible.posix`` and ``community.general`` for arillso.system,
``arillso.system`` and ``community.docker`` for arillso.container). Check
what is installed and where:

.. code-block:: bash

   ansible-galaxy collection list
   ansible-galaxy collection install arillso.system:@ARILLSO_SYSTEM_VERSION@ --force

Pin the versions in a ``requirements.yml`` so every environment resolves the
same set:

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: "@ARILLSO_SYSTEM_VERSION@"
     - name: arillso.container
       version: "@ARILLSO_CONTAINER_VERSION@"

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml

Collections Installed to a Custom Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml -p ./collections

Ansible only finds them if the path is configured:

.. code-block:: ini

   # ansible.cfg
   [defaults]
   collections_path = ./collections:~/.ansible/collections

Unsupported Ansible Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All three collections declare ``requires_ansible: ">=2.18.0"``. On older
ansible-core, Ansible warns that the collection does not support the running
version and roles may fail. Upgrade ansible-core to 2.18 or later.

Roles and Variables
-------------------

Role Not Found
~~~~~~~~~~~~~~

Use the fully qualified role name and confirm the role is installed:

.. code-block:: bash

   ansible-galaxy collection list | grep arillso
   ansible-doc -t role arillso.system.packages

.. code-block:: yaml

   - name: Install packages
     ansible.builtin.include_role:
       name: arillso.system.packages

Argument Validation Fails
~~~~~~~~~~~~~~~~~~~~~~~~~

Every role ships ``meta/argument_specs.yml``. Ansible validates the role
variables against it before the first task runs and stops on a wrong type or
a missing required option. The error names the option; the accepted options
and types are listed on the role page, for example
:ref:`arillso.system.packages <ansible_collections.arillso.system.packages_role>`.

Collection Roles
----------------

arillso.system.firewall
~~~~~~~~~~~~~~~~~~~~~~~

The role renders ``/etc/nftables.conf`` (keeping a backup of the previous
file) and enables the ``nftables`` service through
``arillso.system.systemd``. Its default ``firewall_tables`` sets the ``input``
and ``forward`` chains to policy ``drop``; ``input`` accepts loopback,
established/related traffic and new SSH connections on port 22.

* **A service is unreachable after the run:** add an accept rule through
  ``firewall_global``, ``firewall_group`` or ``firewall_host``; they are merged
  on top of ``firewall_tables`` in that order.
* **New SSH connections are dropped under load:** new SSH connections are
  rate-limited (``firewall_ssh_rate_limit``, default ``10/minute``, burst
  ``firewall_ssh_rate_burst``, default ``5``). Raise the limit on CI runners
  and bastions instead of removing the rule.
* **Which packets are dropped:** dropped input packets are logged with the
  prefix ``nft-drop-input:`` (``firewall_log_drop_prefix``).

.. code-block:: bash

   nft list ruleset
   nft -c -f /etc/nftables.conf      # syntax check without loading
   journalctl -k | grep nft-drop-input

See :ref:`arillso.system.firewall <ansible_collections.arillso.system.firewall_role>`.

arillso.system.packages
~~~~~~~~~~~~~~~~~~~~~~~

The role declares only Debian and Ubuntu in ``meta/main.yml``. Packages go
into ``packages_list`` as dictionaries with ``name`` and optional ``state``:

.. code-block:: yaml

   - name: Install packages
     ansible.builtin.include_role:
       name: arillso.system.packages
     vars:
       packages_list:
         - name: nginx
         - name: htop
           state: present

The apt cache is refreshed when it is older than
``packages_cache_valid_time`` (default ``3600`` seconds); set
``packages_force_cache_update: true`` to force a refresh after adding a
repository by hand. See
:ref:`arillso.system.packages <ansible_collections.arillso.system.packages_role>`.

arillso.container.docker
~~~~~~~~~~~~~~~~~~~~~~~~

* **Docker does not start after a config change:** an invalid
  ``docker_daemon`` value produces a malformed ``/etc/docker/daemon.json``.
  Validate it and read the parse error:

  .. code-block:: bash

     dockerd --validate --config-file /etc/docker/daemon.json
     journalctl -u docker -n 50

* **Log rotation is ignored:** the default log driver is ``journald``, which
  ignores ``max-size`` and ``max-file``. For rotation by Docker, switch to
  ``json-file``:

  .. code-block:: yaml

     docker_daemon:
       log-driver: json-file
       log-opts:
         max-size: "10m"
         max-file: "3"

See :ref:`arillso.container.docker <ansible_collections.arillso.container.docker_role>`.

arillso.container.k3s
~~~~~~~~~~~~~~~~~~~~~

* **Node stays NotReady:** check the service (``k3s`` on servers,
  ``k3s-agent`` on agents) and its journal for CNI or kubelet errors.
* **Agents do not join:** the join token on the agents must match the server
  token (``k3s_token``), and the server API must be reachable on port 6443
  (``k3s_https_listen_port``).
* **Upgrade rejected:** the role allows one minor version per step and no
  downgrades. Set ``k3s_version`` to an allowed version.
* **Config change not applied:** if a run aborts after a config file changed
  but before the handler ran, the next run sees no change and does not
  restart k3s. Restart it by hand, or set ``force_handlers: true`` on the
  play.

.. code-block:: bash

   systemctl status k3s
   journalctl -u k3s -n 100

See :ref:`arillso.container.k3s <ansible_collections.arillso.container.k3s_role>`.

arillso.agent.alloy
~~~~~~~~~~~~~~~~~~~

The role waits for ``http://localhost:<alloy_port>/ready`` (default port
``12345``) after starting the ``alloy`` service; set
``alloy_health_check_enabled: false`` to skip the check. Prometheus scraping
is off by default (``alloy_prometheus_enabled: false``), and the default
remote-write target is ``http://localhost:9090/api/v1/write``:

.. code-block:: yaml

   - name: Deploy Grafana Alloy
     ansible.builtin.include_role:
       name: arillso.agent.alloy
     vars:
       alloy_prometheus_enabled: true
       alloy_prometheus_remote_write:
         - name: default
           url: "https://prometheus.example.com/api/v1/write"

.. code-block:: bash

   systemctl status alloy
   journalctl -u alloy -n 100
   curl -s http://localhost:12345/ready

The rendered configuration is ``/etc/alloy/config.alloy``
(``alloy_config_file``). See
:ref:`arillso.agent.alloy <ansible_collections.arillso.agent.alloy_role>`.

Connection and Privileges
-------------------------

.. code-block:: bash

   # Connection and authentication details
   ansible all -i inventory.ini -m ansible.builtin.ping -vvv

   # The roles change system state and need privilege escalation
   ansible-playbook -i inventory.ini site.yml --ask-become-pass

Debugging Techniques
--------------------

.. code-block:: bash

   ansible-playbook site.yml --syntax-check
   ansible-playbook site.yml --check --diff
   ansible-playbook site.yml -vvv
   ansible-playbook site.yml --list-tasks
   ansible-playbook site.yml --start-at-task="Install packages"

FAQ
---

**Which collection covers what?**

* ``arillso.system``: base system roles (access, packages, firewall, logging,
  network, systemd, tuning, zram and others) plus filter, lookup and module
  plugins.
* ``arillso.container``: Docker, Docker Compose v2, registry login, K3s, Helm,
  Fleet and Tailscale.
* ``arillso.agent``: Grafana Alloy, the DigitalOcean agent and Tailscale.

See :ref:`list_of_collections` for the full plugin index.

**Are Windows hosts supported?**

No role declares a Windows platform in ``meta/main.yml``. See
:ref:`compatibility` for the declared Linux platforms.

**How do I report a security issue?**

Send it by email to ``security@arillso.io`` (listed in
``/.well-known/security.txt`` and in the organisation's ``SECURITY.md``), not
as a public issue.

Getting Help
------------

Open an issue in the affected repository and include:

.. code-block:: bash

   ansible --version
   ansible-galaxy collection list | grep arillso
   cat /etc/os-release
   ansible-playbook site.yml -vvv 2>&1 | tee error.log

* `arillso/ansible.system issues <https://github.com/arillso/ansible.system/issues>`_
* `arillso/ansible.container issues <https://github.com/arillso/ansible.container/issues>`_
* `arillso/ansible.agent issues <https://github.com/arillso/ansible.agent/issues>`_

.. seealso::

   * :ref:`quickstart` - Quick Start Guide
   * :ref:`examples` - Examples
   * :ref:`compatibility` - Version Compatibility
   * :ref:`contributing` - Contributing
