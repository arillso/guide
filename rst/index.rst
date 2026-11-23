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

- **3** collections
- |total_roles| roles
- |total_plugins| modules and plugins
- **4** ways to run a playbook

.. container:: hook

   .. container:: hook-play

      .. code-block:: yaml
         :caption: site.yml — one playbook, three collections

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
           arillso/ansible \
           ansible-playbook -i inventory.ini site.yml

      .. code-block:: yaml
         :caption: GitHub Actions

         - uses: arillso/action.playbook@0.5.0
           with:
             playbook: site.yml
             inventory: inventory.ini

The collection pages on this site are generated with antsibull-docs from the
released versions listed below. Go: :doc:`go.ansible <libraries/go_ansible>`.

Collections
-----------

.. list-table::
   :header-rows: 1
   :widths: 22 10 8 8 8 8 36
   :class: index-table

   * - Collection
     - Version
     - Roles
     - Modules
     - Filters
     - Lookups
     - Scope
   * - :doc:`arillso.system <collections/arillso/system/index>`
     - |system_version|
     - |system_roles|
     - |system_modules|
     - |system_filters|
     - |system_lookups|
     - Base system: packages, users and SSH access, nftables firewall,
       network, logging, systemd units, kernel tuning, zram, Python,
       Bitwarden Secrets
   * - :doc:`arillso.container <collections/arillso/container/index>`
     - |container_version|
     - |container_roles|
     - |container_modules|
     - |container_filters|
     - |container_lookups|
     - Docker Engine, Docker Compose v2, registry login, K3s, Helm, Fleet,
       Tailscale
   * - :doc:`arillso.agent <collections/arillso/agent/index>`
     - |agent_version|
     - |agent_roles|
     - |agent_modules|
     - |agent_filters|
     - |agent_lookups|
     - Host agents: Grafana Alloy, DigitalOcean monitoring agent, Tailscale

Install a collection from Ansible Galaxy:

.. code-block:: bash

   ansible-galaxy collection install arillso.system arillso.container arillso.agent

Indexes across all three collections: :doc:`roles <collections/index_role>`,
:doc:`modules <collections/index_module>`,
:doc:`filters <collections/index_filter>`,
:doc:`lookups <collections/index_lookup>`,
:doc:`environment variables <collections/environment_variables>`.

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
   * - Reference
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
   :caption: Reference

   guide/reference/compatibility
   guide/reference/troubleshooting
   guide/best-practices/standards
   guide/development/cicd
   guide/development/contributing

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Ansible collections

   collections/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Container image

   containers/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Go library

   libraries/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: GitHub Action

   github/index

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
