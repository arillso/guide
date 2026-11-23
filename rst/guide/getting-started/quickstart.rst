.. meta::
  :description: Install the arillso Ansible collections and run a first playbook
  :keywords: arillso, ansible, quickstart, getting started, collections

.. _quickstart:

Quick Start
===========

Install the arillso collections, run a first playbook and find the other
arillso tools.

.. contents::
   :local:
   :depth: 2

What arillso provides
---------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Project
     - Content
   * - :ref:`arillso.system <plugins_in_arillso.system>`
     - Roles for users and SSH (``access``), packages, nftables firewall,
       logging, network, systemd, tuning, zram and more; filters for TOML
       and nftables; modules ``apt_update_info`` and ``reboot_info``.
   * - :ref:`arillso.container <plugins_in_arillso.container>`
     - Roles ``docker``, ``docker_compose_v2``, ``docker_login``, ``k3s``,
       ``helm``, ``fleet`` and ``tailscale`` (Tailscale Kubernetes
       resources).
   * - :ref:`arillso.agent <plugins_in_arillso.agent>`
     - Roles ``alloy`` (Grafana Alloy), ``do`` (DigitalOcean agent) and
       ``tailscale`` (Tailscale client on the host).
   * - :ref:`arillso/ansible <docker_ansible>`
     - Alpine-based container image with ``ansible-core``, Mitogen,
       ``kubectl``, ``helm`` and ``kustomize``.
   * - :ref:`action.playbook <action_playbook>`
     - GitHub Action that runs ``ansible-playbook``.
   * - :ref:`go.ansible <go_ansible>`
     - Go module that builds and runs ``ansible-playbook`` commands.

Prerequisites
-------------

* ``ansible-core`` 2.18 or newer on the control node. All three
  collections declare ``requires_ansible: ">=2.18.0"`` in
  ``meta/runtime.yml``.
* SSH access and privilege escalation on the target hosts.
* Target hosts running Debian, Ubuntu or Enterprise Linux. The supported
  releases differ per role and are listed under ``platforms`` in each
  role's ``meta/main.yml``. The ``packages``, ``ready``, ``thermal`` and
  ``zram`` roles of ``arillso.system`` support Debian and Ubuntu only.

Install the collections
-----------------------

.. code-block:: bash

   ansible-galaxy collection install arillso.system arillso.container arillso.agent

Or pin versions in ``requirements.yml``:

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: ">=2.0.0"
     - name: arillso.container
       version: ">=2.0.0"
     - name: arillso.agent
       version: ">=2.0.0"

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml

``ansible-galaxy`` also installs the dependencies declared in each
``galaxy.yml``:

* ``arillso.system``: ``ansible.posix``, ``community.general``,
  ``community.crypto``
* ``arillso.container``: ``arillso.system``, ``community.docker``
* ``arillso.agent``: ``arillso.system``

Check the installed versions:

.. code-block:: bash

   ansible-galaxy collection list | grep arillso

First playbook
--------------

Install packages with :ref:`arillso.system.packages
<ansible_collections.arillso.system.packages_role>` and join the hosts to
a tailnet with :ref:`arillso.agent.tailscale
<ansible_collections.arillso.agent.tailscale_role>`:

.. code-block:: yaml

   ---
   # site.yml
   - name: Base configuration
     hosts: all
     become: true
     roles:
       - role: arillso.system.packages
         vars:
           packages_list:
             - name: git
             - name: htop
               state: latest

       - role: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
           tailscale_accept_routes: "true"

.. code-block:: ini

   # inventory.ini
   [all]
   web1.example.com
   web2.example.com

Run it in check mode first, then for real:

.. code-block:: bash

   ansible-playbook -i inventory.ini site.yml --check --diff
   ansible-playbook -i inventory.ini site.yml

More role examples
------------------

K3s cluster
~~~~~~~~~~~

:ref:`arillso.container.k3s <ansible_collections.arillso.container.k3s_role>`
requires ``k3s_role`` (``server`` or ``agent``) and ``k3s_version``.

.. code-block:: yaml

   ---
   - name: K3s server
     hosts: k3s_servers
     become: true
     roles:
       - role: arillso.container.k3s
         vars:
           k3s_role: server
           k3s_version: v1.35.2+k3s1
           k3s_server_init: true

   - name: K3s agents
     hosts: k3s_agents
     become: true
     roles:
       - role: arillso.container.k3s
         vars:
           k3s_role: agent
           k3s_version: v1.35.2+k3s1
           k3s_server_url: "https://{{ groups['k3s_servers'][0] }}:6443"
           k3s_token: "{{ vault_k3s_token }}"

Grafana Alloy
~~~~~~~~~~~~~

:ref:`arillso.agent.alloy <ansible_collections.arillso.agent.alloy_role>`
ships metrics via ``alloy_prometheus_remote_write`` and logs via
``alloy_loki_clients``:

.. code-block:: yaml

   ---
   - name: Monitoring agent
     hosts: all
     become: true
     roles:
       - role: arillso.agent.alloy
         vars:
           alloy_prometheus_enabled: true
           alloy_prometheus_remote_write:
             - name: default
               url: https://prometheus.example.com/api/v1/write
           alloy_loki_enabled: true
           alloy_loki_clients:
             - name: default
               url: https://loki.example.com/loki/api/v1/push

Run from the container image
----------------------------

The image ``arillso/ansible`` (also ``ghcr.io/arillso/ansible``) runs as
the non-root user ``ansible`` (UID 1000) with home ``/home/ansible``. It
contains no arillso collections; install them at run time:

.. code-block:: bash

   docker run --rm \
     -v "$PWD":/workspace -w /workspace \
     -v "$HOME/.ssh/id_ed25519":/home/ansible/.ssh/id_ed25519:ro \
     arillso/ansible \
     sh -c 'ansible-galaxy collection install -r requirements.yml && ansible-playbook -i inventory.ini site.yml'

The baked-in ``ansible.cfg`` sets ``host_key_checking = False``; pass
``-e ANSIBLE_HOST_KEY_CHECKING=True`` for persistent hosts. Mitogen is
installed but not the default strategy; enable it with
``-e ANSIBLE_STRATEGY=mitogen_linear``. Details: :ref:`docker_ansible`.

Run from GitHub Actions
-----------------------

.. code-block:: yaml

   # .github/workflows/deploy.yml
   name: Deploy

   on:
     push:
       branches: [main]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Run playbook
           uses: arillso/action.playbook@0.5.0
           with:
             playbook: site.yml
             inventory: inventory.ini
             galaxy_file: requirements.yml
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             vault_password: ${{ secrets.VAULT_PASSWORD }}

``playbook`` and ``inventory`` are the only required inputs. All inputs:
:ref:`action_playbook`.

Run from Go
-----------

.. code-block:: go

   package main

   import (
       "context"
       "log"

       ansible "github.com/arillso/go.ansible/v2"
   )

   func main() {
       pb := ansible.NewPlaybook()
       pb.Config.Playbooks = []string{"site.yml"}
       pb.Config.Inventories = []string{"inventory.ini"}

       if err := pb.Exec(context.Background()); err != nil {
           log.Fatalf("playbook failed: %v", err)
       }
   }

Details: :ref:`go_ansible`.

Troubleshooting
---------------

``couldn't resolve module/action`` or role not found
   The collection is missing or installed in a path Ansible does not
   search. Check with ``ansible-galaxy collection list`` and
   ``ansible-config dump | grep COLLECTIONS_PATHS``.

Version warning on collection load
   The collections need ``ansible-core`` 2.18 or newer. Check with
   ``ansible --version``.

Hosts unreachable
   Test the connection with ``ansible all -i inventory.ini -m ping`` and
   rerun the playbook with ``-vvv``.

More cases: :ref:`troubleshooting`.

Next steps
----------

* Role and plugin reference: :ref:`plugins_in_arillso.system`,
  :ref:`plugins_in_arillso.container`, :ref:`plugins_in_arillso.agent`
* :ref:`environment` for working on the collections themselves
* :ref:`architecture` for how the projects depend on each other
* :ref:`compatibility` for version information
