.. meta::
  :description: Complete playbook examples for arillso collections
  :keywords: arillso, examples, playbooks, ansible, complete

.. _examples:

Complete Examples
=================

Ready-to-use playbook examples for common infrastructure tasks.

.. contents::
   :local:
   :depth: 2

Example 1: Docker Server Setup
-------------------------------

Complete setup for a Docker application server with firewall and Tailscale.

**Files:**

.. code-block:: text

   docker-server/
   ├── ansible.cfg
   ├── inventory.ini
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.container
       version: ">=1.0.0"
     - name: arillso.system
       version: ">=1.0.0"
     - name: arillso.agent
       version: ">=1.0.0"

**ansible.cfg**

.. code-block:: ini

   [defaults]
   inventory = inventory.ini
   remote_user = root

**inventory.ini**

.. code-block:: ini

   [docker_servers]
   app1.example.com
   app2.example.com

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Setup Docker servers
     hosts: docker_servers
     become: true

     tasks:
       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker
         vars:
           docker_daemon:
             log-driver: "json-file"
             log-opts:
               max-size: "10m"
               max-file: "3"

       - name: Configure firewall
         ansible.builtin.include_role:
           name: arillso.system.firewall
         vars:
           firewall:
             - table:
                 family: inet
                 name: filter
                 chains:
                   - name: input
                     hook: input
                     policy: drop
                     priority: 0
                     rules:
                       - iifname lo accept
                       - ct state established,related accept
                       - tcp dport 22 accept comment "SSH"
                       - tcp dport 80 accept comment "HTTP"
                       - tcp dport 443 accept comment "HTTPS"

       - name: Install Tailscale
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ lookup('env', 'TAILSCALE_KEY') }}"
           tailscale_accept_dns: "true"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   export TAILSCALE_KEY="tskey-auth-xxxxx"
   ansible-playbook playbook.yml

Example 2: K3s Cluster
----------------------

Deploy a lightweight Kubernetes cluster with K3s.

**Files:**

.. code-block:: text

   k3s-cluster/
   ├── ansible.cfg
   ├── inventory.ini
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.container
       version: ">=1.0.0"
     - name: arillso.system
       version: ">=1.0.0"

**inventory.ini**

.. code-block:: ini

   [k3s_server]
   k3s-master.example.com

   [k3s_agents]
   k3s-worker-1.example.com
   k3s-worker-2.example.com

   [k3s_all:children]
   k3s_server
   k3s_agents

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Prepare K3s nodes
     hosts: k3s_all
     become: true

     tasks:
       - name: Configure kernel parameters
         ansible.builtin.include_role:
           name: arillso.system.tuning
         vars:
           tuning_sysctl:
             net.ipv4.ip_forward: 1
             net.bridge.bridge-nf-call-iptables: 1

       - name: Configure firewall
         ansible.builtin.include_role:
           name: arillso.system.firewall
         vars:
           firewall:
             - table:
                 family: inet
                 name: filter
                 chains:
                   - name: input
                     hook: input
                     policy: accept
                     priority: 0
                     rules:
                       - tcp dport 6443 accept comment "K3s API"
                       - tcp dport 10250 accept comment "Kubelet"

   - name: Install K3s server
     hosts: k3s_server
     become: true

     tasks:
       - name: Deploy K3s server
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_node_name: "{{ inventory_hostname }}"
           k3s_version: "v1.28.5+k3s1"
           k3s_server_url: ""
           k3s_token: "my-secret-token-123"

   - name: Install K3s agents
     hosts: k3s_agents
     become: true

     tasks:
       - name: Deploy K3s agent
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_node_name: "{{ inventory_hostname }}"
           k3s_version: "v1.28.5+k3s1"
           k3s_server_url: "https://{{ hostvars[groups['k3s_server'][0]].ansible_host }}:6443"
           k3s_token: "my-secret-token-123"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   ansible-playbook playbook.yml

Example 3: Developer Workstation
---------------------------------

Set up a local development environment.

**Files:**

.. code-block:: text

   dev-setup/
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: ">=1.0.0"
     - name: arillso.container
       version: ">=1.0.0"

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Setup development workstation
     hosts: localhost
     become: true

     tasks:
       - name: Install Python packages
         ansible.builtin.include_role:
           name: arillso.system.python
         vars:
           python_packages:
             - ansible
             - ansible-lint
             - molecule
             - pytest

       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker

       - name: Install Docker Compose
         ansible.builtin.include_role:
           name: arillso.container.docker_compose_v2

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   ansible-playbook playbook.yml -K

Example 4: Multi-Server Tailscale Mesh
---------------------------------------

Connect multiple servers across different cloud providers.

**Files:**

.. code-block:: text

   tailscale-mesh/
   ├── ansible.cfg
   ├── inventory.ini
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.agent
       version: ">=1.0.0"

**inventory.ini**

.. code-block:: ini

   [aws_servers]
   aws-web-1.example.com
   aws-db-1.example.com

   [azure_servers]
   azure-app-1.example.com

   [do_servers]
   do-cache-1.example.com

   [all_servers:children]
   aws_servers
   azure_servers
   do_servers

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Setup Tailscale mesh network
     hosts: all_servers
     become: true

     tasks:
       - name: Install Tailscale
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ lookup('env', 'TAILSCALE_KEY') }}"
           tailscale_accept_dns: "true"
           tailscale_accept_routes: "true"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   export TAILSCALE_KEY="tskey-auth-xxxxx"
   ansible-playbook playbook.yml

Example 5: Helm Chart Deployment
---------------------------------

Deploy applications to Kubernetes using Helm.

**Files:**

.. code-block:: text

   helm-deploy/
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.container
       version: ">=1.0.0"

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Deploy Helm charts
     hosts: k3s_server[0]
     become: true

     tasks:
       - name: Deploy applications
         ansible.builtin.include_role:
           name: arillso.container.helm
         vars:
           helm_enable_charts: true
           helm_repositories:
             bitnami: "https://charts.bitnami.com/bitnami"
             ingress-nginx: "https://kubernetes.github.io/ingress-nginx"

           helm_charts:
             - name: nginx-ingress
               chart: ingress-nginx/ingress-nginx
               namespace: ingress-nginx
               create_namespace: true
               version: "4.8.0"
               values:
                 controller:
                   replicaCount: 2

             - name: postgresql
               chart: bitnami/postgresql
               namespace: database
               create_namespace: true
               version: "13.2.0"
               values:
                 auth:
                   username: appuser
                   database: appdb
                   password: "changeme"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   ansible-playbook playbook.yml

Example 6: Docker Container Execution
--------------------------------------

Run Ansible playbooks in a container without local installation.

**Files:**

.. code-block:: text

   docker-ansible/
   ├── playbook.yml
   └── inventory.ini

**Run with Docker:**

.. code-block:: bash

   # Pull image
   docker pull arillso/ansible:latest

   # Run playbook
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible ansible-playbook playbook.yml

   # With inventory
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible ansible-playbook -i inventory.ini playbook.yml

   # With extra vars
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible ansible-playbook playbook.yml -e "env=production"

Example 7: Go Application Integration
--------------------------------------

Execute Ansible from Go applications.

**main.go:**

.. code-block:: go

   package main

   import (
       "context"
       "fmt"
       "log"

       "github.com/arillso/go.ansible/pkg/ansible"
   )

   func main() {
       executor := ansible.NewExecutor()

       ctx := context.Background()
       result, err := executor.RunPlaybook(ctx, ansible.PlaybookOptions{
           Playbook:  "deploy.yml",
           Inventory: "production.ini",
           ExtraVars: map[string]string{
               "app_version": "v1.2.3",
               "environment": "production",
           },
       })

       if err != nil {
           log.Fatalf("Failed: %v", err)
       }

       fmt.Printf("Status: %s\n", result.Status)
   }

**Run:**

.. code-block:: bash

   go mod init myapp
   go get github.com/arillso/go.ansible
   go run main.go

Example 8: GitHub Actions Deployment
-------------------------------------

Automated deployment on git push.

**.github/workflows/deploy.yml:**

.. code-block:: yaml

   name: Deploy

   on:
     push:
       branches: [main]

   jobs:
     deploy:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - name: Deploy Infrastructure
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: playbooks/site.yml
             inventory: inventory/production.ini
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             vault_password: ${{ secrets.VAULT_PASSWORD }}
             requirements: requirements.yml
             extra_vars: |
               app_version=${{ github.sha }}
               deployed_by=${{ github.actor }}

**Run:**

Push to main branch to trigger deployment.

Example 9: K3s + Fleet + Monitoring
------------------------------------

Bootstrap a K3s cluster, register GitOps workloads with Fleet and ship
metrics and logs with Grafana Alloy.

**Files:**

.. code-block:: text

   k3s-fleet-monitoring/
   ├── ansible.cfg
   ├── inventory.ini
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.container
       version: ">=1.0.0"
     - name: arillso.agent
       version: ">=1.0.0"

**inventory.ini**

.. code-block:: ini

   [k3s_server]
   k3s-master.example.com

   [k3s_agents]
   k3s-worker-1.example.com

   [k3s_all:children]
   k3s_server
   k3s_agents

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Install K3s control plane
     hosts: k3s_server
     become: true

     tasks:
       - name: Deploy K3s server
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_node_name: "{{ inventory_hostname }}"
           k3s_server_url: ""
           k3s_token: "{{ lookup('env', 'K3S_TOKEN') }}"

   - name: Join K3s agents to the cluster
     hosts: k3s_agents
     become: true

     tasks:
       - name: Deploy K3s agent
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_node_name: "{{ inventory_hostname }}"
           k3s_server_url: "https://{{ hostvars[groups['k3s_server'][0]].ansible_host }}:6443"
           k3s_token: "{{ lookup('env', 'K3S_TOKEN') }}"

   - name: Register GitOps workloads with Fleet
     hosts: k3s_server
     become: true

     tasks:
       - name: Deploy Fleet GitRepos
         ansible.builtin.include_role:
           name: arillso.container.fleet
         vars:
           fleet_enable_gitrepos: true
           fleet_gitrepos:
             - name: "platform-apps"
               namespace: "fleet-default"
               repository: "https://github.com/example/platform-apps.git"
               branch: "main"
               paths:
                 - "manifests/"
               targets:
                 - name: "production"
                   cluster_selector:
                     matchLabels:
                       env: "prod"

   - name: Ship metrics and logs with Alloy
     hosts: k3s_all
     become: true

     tasks:
       - name: Install Grafana Alloy
         ansible.builtin.include_role:
           name: arillso.agent.alloy
         vars:
           alloy_enable_prometheus: true
           alloy_enable_advanced_node_exporter: true
           alloy_enable_loki: true
           alloy_loki_file_sources:
             - name: "syslog"
               targets:
                 - path: "/var/log/syslog"
               write_to: "default"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   export K3S_TOKEN="my-secret-token-123"
   ansible-playbook playbook.yml

Example 10: Multi-Host Firewall
--------------------------------

Apply a consistent nftables baseline across a fleet of hosts and open
extra ports only where a role group needs them.

**Files:**

.. code-block:: text

   firewall-fleet/
   ├── ansible.cfg
   ├── inventory.ini
   ├── group_vars/
   │   ├── all.yml
   │   └── web.yml
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: ">=1.0.0"

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
   # Baseline applied to every host.
   firewall_base_rules:
     - iifname lo accept
     - ct state established,related accept
     - tcp dport 22 accept comment "SSH"

**group_vars/web.yml**

.. code-block:: yaml

   ---
   # Extra ports only for the web group.
   firewall_extra_rules:
     - tcp dport 80 accept comment "HTTP"
     - tcp dport 443 accept comment "HTTPS"

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Apply firewall baseline to all hosts
     hosts: all
     become: true

     tasks:
       - name: Configure nftables firewall
         ansible.builtin.include_role:
           name: arillso.system.firewall
         vars:
           firewall:
             - table:
                 family: inet
                 name: filter
                 chains:
                   - name: input
                     hook: input
                     policy: drop
                     priority: 0
                     rules: "{{ firewall_base_rules + (firewall_extra_rules | default([])) }}"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   ansible-playbook playbook.yml

Example 11: Secret Management
------------------------------

Install the Bitwarden Secrets Manager CLI and combine it with Ansible
Vault instead of hard-coding credentials in playbooks.

**Files:**

.. code-block:: text

   secret-management/
   ├── group_vars/
   │   └── all/
   │       └── vault.yml        # encrypted with ansible-vault
   ├── requirements.yml
   └── playbook.yml

**requirements.yml**

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: ">=1.0.0"
     - name: community.general
       version: ">=8.0.0"

**group_vars/all/vault.yml** (encrypted)

.. code-block:: yaml

   ---
   # ansible-vault encrypt group_vars/all/vault.yml
   vault_db_password: "super-secret-db-password"

**playbook.yml**

.. code-block:: yaml

   ---
   - name: Deploy with managed secrets
     hosts: all
     become: true

     tasks:
       # The role installs the `bws` CLI; secrets are then resolved at
       # runtime via the community.general lookup.
       - name: Install Bitwarden Secrets Manager CLI
         ansible.builtin.include_role:
           name: arillso.system.bitwarden_secrets

       - name: Resolve an API key from Bitwarden Secrets Manager
         ansible.builtin.set_fact:
           api_key: >-
             {{ lookup('community.general.bitwarden_secrets_manager',
                       '00000000-0000-0000-0000-000000000000',
                       bws_access_token=lookup('env', 'BWS_ACCESS_TOKEN')).value }}
         no_log: true

       - name: Use a Vault-encrypted value
         ansible.builtin.debug:
           msg: "DB password length is {{ vault_db_password | length }} characters"

**Run:**

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml
   export BWS_ACCESS_TOKEN="0.your-bitwarden-access-token"
   ansible-playbook playbook.yml --ask-vault-pass

Tips & Best Practices
----------------------

**Secrets Management**

Use environment variables or Ansible Vault for sensitive data:

.. code-block:: bash

   # Environment variable
   export TAILSCALE_KEY="tskey-auth-xxxxx"

   # Or Ansible Vault
   ansible-vault create secrets.yml
   ansible-playbook playbook.yml --vault-password-file .vault-pass

**Testing**

Test playbooks in check mode first:

.. code-block:: bash

   ansible-playbook playbook.yml --check

**Limiting Hosts**

Run on specific hosts:

.. code-block:: bash

   ansible-playbook playbook.yml --limit web1.example.com

**Verbose Output**

Debug with verbose mode:

.. code-block:: bash

   ansible-playbook playbook.yml -vvv

Next Steps
----------

* Review :ref:`use-cases` for more scenarios
* Check :ref:`quickstart` for getting started
* Explore :ref:`architecture` for design patterns

.. seealso::

   * :ref:`use-cases` - Use Cases & Scenarios
   * :ref:`quickstart` - Quick Start Guide
   * :ref:`architecture` - Architecture Guide
