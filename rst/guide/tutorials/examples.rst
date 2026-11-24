.. meta::
  :description: Complete playbook projects that use the arillso collections
  :keywords: arillso, examples, playbooks, ansible

.. _examples:

Examples
========

Complete playbook projects: directory layout, ``requirements.yml``, inventory and
playbook. Variable names follow the role documentation of the collection
versions this guide documents (``arillso.system`` @ARILLSO_SYSTEM_VERSION@, ``arillso.container``
@ARILLSO_CONTAINER_VERSION@, ``arillso.agent`` @ARILLSO_AGENT_VERSION@). Shorter single-purpose snippets, including the
container image, the GitHub Action and the Go library, are in :ref:`use-cases`.

.. contents::
   :local:
   :depth: 1

Docker Hosts
------------

Docker with ``json-file`` log rotation, an nftables input filter and Tailscale.

.. code-block:: text

   docker-hosts/
   ├── ansible.cfg
   ├── inventory.ini
   ├── requirements.yml
   ├── group_vars/
   │   └── all/
   │       └── vault.yml        # ansible-vault encrypted
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.container
       version: ">=@ARILLSO_CONTAINER_VERSION@"
     - name: arillso.system
       version: ">=@ARILLSO_SYSTEM_VERSION@"
     - name: arillso.agent
       version: ">=@ARILLSO_AGENT_VERSION@"

**ansible.cfg**

.. code-block:: ini

   [defaults]
   inventory = inventory.ini

**inventory.ini**

.. code-block:: ini

   [docker_servers]
   app1.example.com
   app2.example.com

**group_vars/all/vault.yml** (encrypted)

.. code-block:: yaml

   ---
   vault_tailscale_auth_key: "tskey-auth-..."

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Configure Docker hosts
     hosts: docker_servers
     become: true

     tasks:
       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker
         vars:
           docker_daemon:
             log-driver: json-file
             log-opts:
               max-size: "10m"
               max-file: "3"

       - name: Configure nftables
         ansible.builtin.include_role:
           name: arillso.system.firewall
         vars:
           firewall_tables:
             - table:
                 name: filter
                 family: inet
                 chains:
                   - name: input
                     type: filter
                     hook: input
                     priority: 0
                     policy: drop
                     rules:
                       - iifname: "lo"
                         action: accept
                       - ct_state: ["established", "related"]
                         action: accept
                       - comment: "New SSH connections, rate-limited"
                         tcp_dport: 22
                         ct_state: ["new"]
                         limit: "10/minute"
                         burst: 5
                         action: accept
                       - comment: "HTTP and HTTPS"
                         tcp_dport: [80, 443]
                         action: accept

       - name: Join the tailnet
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
           tailscale_accept_dns: "true"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   ansible-playbook playbook.yml --ask-vault-pass

The ruleset defines no ``forward`` chain on purpose: the firewall role's default
ruleset has a ``forward`` chain with policy ``drop``, which would also drop
traffic that Docker forwards to containers. See :ref:`usecase-docker-server`.

K3s Cluster with Fleet and Alloy
--------------------------------

One K3s server, one agent, Fleet GitRepos registered on the server, and Grafana
Alloy on all nodes.

.. code-block:: text

   k3s-cluster/
   ├── ansible.cfg
   ├── inventory.ini
   ├── requirements.yml
   ├── group_vars/
   │   └── all/
   │       └── vault.yml        # vault_k3s_token
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.container
       version: ">=@ARILLSO_CONTAINER_VERSION@"
     - name: arillso.agent
       version: ">=@ARILLSO_AGENT_VERSION@"

**inventory.ini**

.. code-block:: ini

   [k3s_servers]
   k3s-1.example.com

   [k3s_agents]
   k3s-worker-1.example.com

   [k3s_all:children]
   k3s_servers
   k3s_agents

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Install the K3s server
     hosts: k3s_servers
     become: true

     tasks:
       - name: Deploy K3s server
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_role: server
           k3s_server_init: true
           k3s_node_name: "{{ inventory_hostname }}"
           k3s_version: "v1.35.2+k3s1"
           k3s_token: "{{ vault_k3s_token }}"

   - name: Join the K3s agents
     hosts: k3s_agents
     become: true

     tasks:
       - name: Deploy K3s agent
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_role: agent
           k3s_node_name: "{{ inventory_hostname }}"
           k3s_version: "v1.35.2+k3s1"
           k3s_server_url: "https://{{ groups['k3s_servers'][0] }}:6443"
           k3s_token: "{{ vault_k3s_token }}"

   - name: Register GitOps workloads with Fleet
     hosts: k3s_servers
     become: true

     tasks:
       - name: Create Fleet GitRepos
         ansible.builtin.include_role:
           name: arillso.container.fleet
         vars:
           fleet_enable_gitrepos: true
           fleet_gitrepos:
             - name: platform-apps
               namespace: fleet-default
               repository: "https://github.com/example/platform-apps.git"
               branch: main
               paths:
                 - manifests/
               targets:
                 - name: production
                   cluster_selector:
                     matchLabels:
                       env: prod

   - name: Ship metrics and logs with Alloy
     hosts: k3s_all
     become: true

     tasks:
       - name: Install Grafana Alloy
         ansible.builtin.include_role:
           name: arillso.agent.alloy
         vars:
           alloy_prometheus_enabled: true
           alloy_advanced_node_exporter_enabled: true
           alloy_loki_enabled: true
           alloy_loki_file_sources:
             - name: syslog
               targets:
                 - path: /var/log/syslog
               write_to: default

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   ansible-playbook playbook.yml --ask-vault-pass

**Notes:**

* ``arillso.container.fleet`` creates Fleet resources (GitRepos, Bundles,
  Clusters, Workspaces, registration tokens) through ``kubernetes.core.k8s``. It
  does not install the Fleet controller; that must already run in the cluster.
  The kubeconfig defaults to ``/etc/rancher/k3s/k3s.yaml``.
* ``alloy_loki_file_sources`` entries take ``name``, ``targets`` (each with
  ``path`` and optional ``labels``) and ``write_to``, which names an entry of
  ``alloy_loki_clients``.

Multi-Host Firewall
-------------------

A baseline for every host and extra ports for one group, using the firewall
role's levels ``firewall_tables``, ``firewall_global``, ``firewall_group`` and
``firewall_host``.

.. code-block:: text

   firewall/
   ├── inventory.ini
   ├── requirements.yml
   ├── group_vars/
   │   ├── all.yml
   │   └── web.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: ">=@ARILLSO_SYSTEM_VERSION@"

**inventory.ini**

.. code-block:: ini

   [web]
   web-1.example.com
   web-2.example.com

   [db]
   db-1.example.com

**group_vars/all.yml**

.. code-block:: yaml

   ---
   fw_base_rules:
     - iifname: "lo"
       action: accept
     - ct_state: ["established", "related"]
       action: accept
     - comment: "New SSH connections, rate-limited"
       tcp_dport: 22
       ct_state: ["new"]
       limit: "10/minute"
       burst: 5
       action: accept

   fw_extra_rules: []

   firewall_global:
     - table:
         name: filter
         family: inet
         chains:
           - name: input
             type: filter
             hook: input
             priority: 0
             policy: drop
             rules: "{{ fw_base_rules + fw_extra_rules }}"

**group_vars/web.yml**

.. code-block:: yaml

   ---
   fw_extra_rules:
     - comment: "HTTP and HTTPS"
       tcp_dport: [80, 443]
       action: accept

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Apply the firewall
     hosts: all
     become: true

     roles:
       - role: arillso.system.firewall

**Notes:**

* The levels do not merge rule by rule. The role's
  ``to_nftables_hierarchy`` filter takes the last non-empty level in the order
  ``firewall_tables`` → ``firewall_global`` → ``firewall_group`` →
  ``firewall_host`` and uses it as the complete ruleset. A non-empty
  ``firewall_host`` therefore replaces everything set at the lower levels.
* This example keeps one table definition in ``firewall_global`` and varies only
  the rule list per group, so the baseline is written once.

Secrets from Bitwarden Secrets Manager
--------------------------------------

Install the ``bws`` CLI on the control node and resolve secrets with the
``community.general.bitwarden_secrets_manager`` lookup.

.. code-block:: text

   secrets/
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: ">=@ARILLSO_SYSTEM_VERSION@"
     - name: community.general

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Install the bws CLI on the control node
     hosts: localhost
     connection: local
     become: true

     tasks:
       - name: Install Bitwarden Secrets Manager CLI
         ansible.builtin.include_role:
           name: arillso.system.bitwarden_secrets

   - name: Use a secret on the managed hosts
     hosts: all
     become: true

     tasks:
       - name: Resolve the API key
         ansible.builtin.set_fact:
           app_api_key: >-
             {{ lookup('community.general.bitwarden_secrets_manager',
                       '00000000-0000-0000-0000-000000000000',
                       bws_access_token=lookup('env', 'BWS_ACCESS_TOKEN')).value }}
         no_log: true

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   export BWS_ACCESS_TOKEN="..."
   ansible-playbook playbook.yml -K

**Notes:**

* Lookups run on the control node, so ``bws`` has to be installed there, not on
  the managed hosts.
* ``arillso.system.bitwarden_secrets`` installs ``bws`` (default version
  ``bitwarden_secrets_version: 1.0.0``) to ``/usr/local/bin``.

Useful Flags
------------

.. code-block:: bash

   # Dry run with diff
   ansible-playbook playbook.yml --check --diff

   # Limit to one host
   ansible-playbook playbook.yml --limit web-1.example.com

   # Verbose output
   ansible-playbook playbook.yml -vvv

.. seealso::

   * :ref:`use-cases` - shorter scenarios, container image, GitHub Action, Go
   * :ref:`quickstart` - first steps
   * :ref:`security` - secrets and hardening
