.. meta::
   :description: arillso is a set of open source projects for running Ansible: the collections arillso.system, arillso.container and arillso.agent, the arillso/ansible container image, the action.playbook GitHub Action and the go.ansible library.

.. _docsite_root_index:

arillso
=======

.. rst-class:: lede

Ansible roles for what a Linux host needs: packages, firewall, Docker, K3s,
monitoring agents. And the tools to run them from a shell, a container, a
GitHub workflow or Go. Open source, MIT licensed.

.. rst-class:: figures

- **3** :doc:`collections <collections/index>`
- |total_roles| :doc:`roles <collections/index_role>`
- |total_plugins| :doc:`modules, filters and lookups <collections/index>`
- **4** :ref:`ways to run a playbook <run_a_playbook>`

Collections
-----------

.. list-table::
   :header-rows: 1
   :widths: 20 9 21 50
   :class: index-table collections-table

   * - Collection
     - Version
     - Contents
     - Roles
   * - :doc:`arillso.system <collections/arillso/system/index>`
     - |system_version|
     - | |system_roles| roles · |system_modules| modules
       | |system_filters| filters · |system_lookups| lookups
     - :doc:`access <collections/arillso/system/access_role>` (users, SSH),
       :doc:`ansible <collections/arillso/system/ansible_role>` (ansible-pull via systemd timer),
       :doc:`bitwarden_secrets <collections/arillso/system/bitwarden_secrets_role>` (Bitwarden Secrets CLI),
       :doc:`facts <collections/arillso/system/facts_role>` (system facts),
       :doc:`firewall <collections/arillso/system/firewall_role>` (nftables),
       :doc:`logging <collections/arillso/system/logging_role>`,
       :doc:`network <collections/arillso/system/network_role>`,
       :doc:`packages <collections/arillso/system/packages_role>`,
       :doc:`python <collections/arillso/system/python_role>` (pip packages),
       :doc:`ready <collections/arillso/system/ready_role>` (wait for readiness),
       :doc:`shell <collections/arillso/system/shell_role>` (shell, MOTD),
       :doc:`systemd <collections/arillso/system/systemd_role>` (systemd units),
       :doc:`thermal <collections/arillso/system/thermal_role>` (sensors),
       :doc:`tuning <collections/arillso/system/tuning_role>` (kernel tuning),
       :doc:`zram <collections/arillso/system/zram_role>` (compressed swap)
   * - :doc:`arillso.container <collections/arillso/container/index>`
     - |container_version|
     - | |container_roles| roles · |container_modules| modules
       | |container_filters| filters · |container_lookups| lookups
     - :doc:`docker <collections/arillso/container/docker_role>` (Docker Engine),
       :doc:`docker_compose_v2 <collections/arillso/container/docker_compose_v2_role>` (Compose v2),
       :doc:`docker_login <collections/arillso/container/docker_login_role>` (registry login),
       :doc:`k3s <collections/arillso/container/k3s_role>` (K3s),
       :doc:`helm <collections/arillso/container/helm_role>` (Helm charts),
       :doc:`fleet <collections/arillso/container/fleet_role>` (Rancher Fleet),
       :doc:`tailscale <collections/arillso/container/tailscale_role>` (Tailscale in Kubernetes)
   * - :doc:`arillso.agent <collections/arillso/agent/index>`
     - |agent_version|
     - | |agent_roles| roles · |agent_modules| modules
       | |agent_filters| filters · |agent_lookups| lookups
     - :doc:`alloy <collections/arillso/agent/alloy_role>` (Grafana Alloy),
       :doc:`do <collections/arillso/agent/do_role>` (DigitalOcean monitoring agent),
       :doc:`tailscale <collections/arillso/agent/tailscale_role>` (Tailscale VPN client on the host)

Install from Ansible Galaxy:

.. code-block:: bash

   ansible-galaxy collection install arillso.system arillso.container arillso.agent

Indexes across all three collections: :doc:`roles <collections/index_role>`,
:doc:`modules <collections/index_module>`,
:doc:`filters <collections/index_filter>`,
:doc:`lookups <collections/index_lookup>`,
:doc:`environment variables <collections/environment_variables>`.
The collection pages are generated with antsibull-docs from the versions
listed above.

.. _run_a_playbook:

Run a playbook
--------------

.. container:: hook

   .. container:: hook-play

      .. code-block:: yaml
         :caption: site.yml: one playbook, three collections

         - hosts: all
           become: true
           roles:
             - role: arillso.system.packages
               vars:
                 packages_list:
                   - name: git

             - role: arillso.container.docker

             - role: arillso.agent.alloy
               vars:
                 alloy_prometheus_enabled: true
                 alloy_prometheus_remote_write:
                   - name: default
                     url: https://prom.example.com/api/v1/write

   .. container:: hook-run

      .. code-block:: bash
         :caption: Shell

         ansible-playbook -i inventory.ini site.yml

      .. code-block:: bash
         :caption: Container image

         docker run --rm -v "$PWD":/work -w /work \
           arillso/ansible:@ARILLSO_ANSIBLE_IMAGE_VERSION@ \
           ansible-playbook -i inventory.ini site.yml

      .. code-block:: yaml
         :caption: GitHub Actions

         - uses: arillso/action.playbook@@ACTION_PLAYBOOK_VERSION@
           with:
             playbook: site.yml
             inventory: inventory.ini

      .. code-block:: go
         :caption: Go

         pb := ansible.NewPlaybook()
         pb.Config.Playbooks = []string{"site.yml"}
         pb.Config.Inventories = []string{"inventory.ini"}
         err := pb.Exec(ctx)

Tools
-----

.. list-table::
   :header-rows: 1
   :widths: 24 30 46
   :class: index-table

   * - Project
     - Kind
     - Reference
   * - :doc:`arillso/ansible <containers/docker_ansible>`
     - Container image
     - Ansible in an Alpine image, for CI jobs and local runs.
       Source: `arillso/docker.ansible <https://github.com/arillso/docker.ansible>`__
   * - :doc:`action.playbook <github/action_playbook>`
     - GitHub Action
     - Runs ``ansible-playbook`` in a workflow step.
       Source: `arillso/action.playbook <https://github.com/arillso/action.playbook>`__
   * - :doc:`go.ansible <libraries/go_ansible>`
     - Go module
     - Builds and runs ``ansible-playbook`` and ``ansible-galaxy`` calls from Go.
       Source: `arillso/go.ansible <https://github.com/arillso/go.ansible>`__

Guide
-----

.. list-table::
   :header-rows: 1
   :widths: 24 76
   :class: index-table

   * - Part
     - Pages
   * - Getting started
     - :doc:`guide/getting-started/quickstart`,
       :doc:`guide/getting-started/environment`,
       :doc:`guide/getting-started/architecture`
   * - Working with arillso
     - :doc:`guide/tutorials/use-cases`,
       :doc:`guide/tutorials/examples`,
       :doc:`guide/best-practices/security`,
       :doc:`guide/best-practices/ansible-roles`
   * - Project
     - :doc:`guide/reference/compatibility`,
       :doc:`guide/reference/troubleshooting`,
       :doc:`guide/best-practices/standards`,
       :doc:`guide/development/cicd`,
       :doc:`guide/development/contributing`

Source code, issues and discussions: `github.com/arillso <https://github.com/arillso>`__.
All arillso projects are released under the MIT License.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Ansible collections

   collections/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Tools

   containers/index
   github/index
   libraries/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Getting started

   guide/getting-started/quickstart
   guide/getting-started/environment
   guide/getting-started/architecture

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Working with arillso

   guide/tutorials/use-cases
   guide/tutorials/examples
   guide/best-practices/security
   guide/best-practices/ansible-roles

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Project

   guide/reference/compatibility
   guide/reference/troubleshooting
   guide/best-practices/standards
   guide/development/cicd
   guide/development/contributing

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Plugin indexes
   :glob:

   collections/index_*

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Additional resources

   collections/environment_variables
