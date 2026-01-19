.. meta::
  :description: Quick start guide for getting started with arillso
  :keywords: arillso, ansible, quickstart, getting started, tutorial

.. _quickstart:

Quick Start Guide
=================

Get up and running with arillso in minutes. This guide walks you through your first steps with arillso collections.

.. contents::
   :local:
   :depth: 2

What is arillso?
----------------

arillso is a comprehensive automation platform that provides:

* **Production-ready Ansible Collections** for system, container, and agent management
* **Container images** optimized for Ansible automation
* **Go libraries** for programmatic Ansible execution
* **GitHub Actions** for CI/CD integration

Choose Your Path
----------------

.. raw:: html

   <div class="quickstart-paths">
     <div class="path">
       <h3>🖥️ System Configuration</h3>
       <p>Manage system configuration, packages, firewall, networking, security hardening, and service orchestration</p>
       <a href="#path-system-admin">Start Here →</a>
     </div>
     <div class="path">
       <h3>🐳 Container & Orchestration</h3>
       <p>Docker, Docker Compose, Kubernetes (K3s), Helm, Fleet, Tailscale with security hardening and GitOps support</p>
       <a href="#path-containers">Start Here →</a>
     </div>
     <div class="path">
       <h3>📊 Monitoring & Networking Agents</h3>
       <p>Grafana Alloy (observability), DigitalOcean Agent (Droplet monitoring), Tailscale (VPN mesh networking)</p>
       <a href="#path-monitoring">Start Here →</a>
     </div>
   </div>

Prerequisites
-------------

Before starting, ensure you have:

**Required:**

* Ansible >= 2.15
* Python >= 3.9
* SSH access to target hosts

**Optional:**

* Docker (for container images)
* Go >= 1.25 (for Go library)
* GitHub account (for Actions)

Installation
------------

Install Ansible Collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install all arillso collections
   ansible-galaxy collection install arillso.system
   ansible-galaxy collection install arillso.container
   ansible-galaxy collection install arillso.agent

   # Or install from requirements file
   cat > requirements.yml <<EOF
   ---
   collections:
     - name: arillso.system
       version: ">=1.0.0"
     - name: arillso.container
       version: ">=1.0.0"
     - name: arillso.agent
       version: ">=1.0.0"
   EOF

   ansible-galaxy collection install -r requirements.yml

Verify Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List installed collections
   ansible-galaxy collection list | grep arillso

   # Expected output:
   # arillso.agent        1.0.0
   # arillso.container    1.0.0
   # arillso.system       1.0.0

.. _path-system-admin:

Path 1: System Administration
------------------------------

Manage system configuration, packages, firewall, and services.

Your First Playbook
~~~~~~~~~~~~~~~~~~~

Create a playbook to configure a basic server:

.. code-block:: yaml

   ---
   # site.yml
   - name: Configure web server
     hosts: webservers
     become: true

     tasks:
       - name: Install and configure packages
         ansible.builtin.include_role:
           name: arillso.system.packages
         vars:
           packages_install:
             - nginx
             - htop
             - vim

       - name: Configure firewall
         ansible.builtin.include_role:
           name: arillso.system.firewall
         vars:
           firewall_enabled: true
           firewall_rules:
             - name: "Allow HTTP"
               port: 80
               protocol: tcp
               action: accept
             - name: "Allow HTTPS"
               port: 443
               protocol: tcp
               action: accept

       - name: Configure logging
         ansible.builtin.include_role:
           name: arillso.system.logging
         vars:
           logging_remote_enabled: true
           logging_remote_host: "logs.example.com"

Create your inventory:

.. code-block:: ini

   # inventory.ini
   [webservers]
   web1.example.com ansible_user=ubuntu
   web2.example.com ansible_user=ubuntu

Run the playbook:

.. code-block:: bash

   ansible-playbook -i inventory.ini site.yml

Next Steps
~~~~~~~~~~

* Explore :ref:`arillso.system roles <plugins_in_arillso.system>`
* Learn about :ref:`network configuration <ansible_collections.arillso.system.network_role>`
* Set up :ref:`system tuning <ansible_collections.arillso.system.tuning_role>`

.. _path-containers:

Path 2: Container Orchestration
--------------------------------

Deploy and manage Docker, Kubernetes, and container workloads.

K3s Cluster Setup
~~~~~~~~~~~~~~~~~

Deploy a lightweight Kubernetes cluster:

.. code-block:: yaml

   ---
   # k3s-cluster.yml
   - name: Deploy K3s cluster
     hosts: k3s_servers
     become: true

     tasks:
       - name: Install K3s server
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_server: true
           k3s_cluster_init: true
           k3s_disable:
             - traefik  # We'll use our own ingress

   - name: Join K3s agents
     hosts: k3s_agents
     become: true

     tasks:
       - name: Install K3s agent
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_server: false
           k3s_url: "https://{{ hostvars[groups['k3s_servers'][0]]['ansible_default_ipv4']['address'] }}:6443"
           k3s_token: "{{ k3s_cluster_token }}"

Docker with Fleet GitOps
~~~~~~~~~~~~~~~~~~~~~~~~~

Set up Docker with Fleet for GitOps deployments:

.. code-block:: yaml

   ---
   # docker-fleet.yml
   - name: Configure Docker and Fleet
     hosts: docker_hosts
     become: true

     tasks:
       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker
         vars:
           docker_edition: "ce"
           docker_users:
             - "{{ ansible_user }}"

       - name: Deploy Fleet
         ansible.builtin.include_role:
           name: arillso.container.fleet
         vars:
           fleet_repo_url: "https://github.com/myorg/fleet-configs"
           fleet_targets:
             - name: production
               cluster_group: prod

Inventory:

.. code-block:: ini

   # inventory.ini
   [k3s_servers]
   k3s-master.example.com

   [k3s_agents]
   k3s-worker1.example.com
   k3s-worker2.example.com

   [docker_hosts]
   docker1.example.com
   docker2.example.com

Run the deployment:

.. code-block:: bash

   ansible-playbook -i inventory.ini k3s-cluster.yml
   ansible-playbook -i inventory.ini docker-fleet.yml

Next Steps
~~~~~~~~~~

* Configure :ref:`Helm <ansible_collections.arillso.container.helm_role>`
* Set up :ref:`Tailscale networking <ansible_collections.arillso.container.tailscale_role>`
* Learn :ref:`Docker Compose v2 <ansible_collections.arillso.container.docker_compose_v2_role>`

.. _path-monitoring:

Path 3: Monitoring & Observability
-----------------------------------

Deploy Grafana Alloy for metrics, logs, and traces collection.

Grafana Alloy Setup
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   # monitoring.yml
   - name: Deploy Grafana Alloy
     hosts: monitoring
     become: true

     tasks:
       - name: Install Grafana Alloy
         ansible.builtin.include_role:
           name: arillso.agent.alloy
         vars:
           alloy_prometheus_enabled: true
           alloy_prometheus_remote_write_url: "https://prometheus.example.com/api/v1/write"

           alloy_loki_enabled: true
           alloy_loki_url: "https://loki.example.com/loki/api/v1/push"

           alloy_tempo_enabled: true
           alloy_tempo_endpoint: "tempo.example.com:4317"

           # Node exporter metrics
           alloy_node_exporter_enabled: true

           # Custom scrape configs
           alloy_custom_scrape_configs:
             - job_name: "custom_app"
               static_configs:
                 - targets:
                     - "app1.example.com:9090"
                     - "app2.example.com:9090"

DigitalOcean Monitoring
~~~~~~~~~~~~~~~~~~~~~~~

For DigitalOcean droplets:

.. code-block:: yaml

   ---
   # do-monitoring.yml
   - name: Install DO Agent
     hosts: digitalocean
     become: true

     tasks:
       - name: Install DigitalOcean Agent
         ansible.builtin.include_role:
           name: arillso.agent.do

Tailscale VPN
~~~~~~~~~~~~~

Secure your infrastructure with Tailscale:

.. code-block:: yaml

   ---
   # tailscale.yml
   - name: Configure Tailscale
     hosts: all
     become: true

     tasks:
       - name: Install Tailscale
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_authkey: "{{ vault_tailscale_authkey }}"
           tailscale_args: "--accept-routes --advertise-exit-node"

Run the setup:

.. code-block:: bash

   ansible-playbook -i inventory.ini monitoring.yml

Next Steps
~~~~~~~~~~

* Configure :ref:`advanced Alloy features <ansible_collections.arillso.agent.alloy_role>`
* Learn about :ref:`Tailscale mesh networking <ansible_collections.arillso.agent.tailscale_role>`

Complete Example: Full Stack Deployment
----------------------------------------

Combine all components for a complete infrastructure:

.. code-block:: yaml

   ---
   # full-stack.yml
   - name: Base system configuration
     hosts: all
     become: true
     roles:
       - role: arillso.system.packages
         vars:
           packages_install:
             - htop
             - vim
             - curl

       - role: arillso.system.firewall
         vars:
           firewall_enabled: true

       - role: arillso.agent.tailscale
         vars:
           tailscale_authkey: "{{ vault_tailscale_authkey }}"

   - name: Deploy K3s cluster
     hosts: k3s_servers
     become: true
     roles:
       - role: arillso.container.k3s
         vars:
           k3s_server: true
           k3s_cluster_init: true

   - name: Deploy monitoring
     hosts: all
     become: true
     roles:
       - role: arillso.agent.alloy
         vars:
           alloy_prometheus_enabled: true
           alloy_loki_enabled: true
           alloy_node_exporter_enabled: true

Full inventory:

.. code-block:: ini

   # inventory.ini
   [all:vars]
   ansible_user=ubuntu

   [k3s_servers]
   k3s-master.example.com

   [k3s_agents]
   k3s-worker1.example.com
   k3s-worker2.example.com

   [docker_hosts]
   docker1.example.com

   [monitoring]
   monitor.example.com

Run complete deployment:

.. code-block:: bash

   # Dry run first
   ansible-playbook -i inventory.ini full-stack.yml --check

   # Execute
   ansible-playbook -i inventory.ini full-stack.yml

Using Container Images
----------------------

arillso provides optimized Ansible container images:

.. code-block:: bash

   # Pull the image
   docker pull arillso/ansible:latest

   # Run a playbook
   docker run --rm \
     -v $(pwd):/ansible \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible \
     ansible-playbook -i inventory.ini site.yml

   # Run with Mitogen (2-7x faster)
   docker run --rm \
     -v $(pwd):/ansible \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible \
     ansible-playbook -i inventory.ini site.yml \
     --strategy mitogen_linear

Using Go Library
----------------

Programmatic Ansible execution:

.. code-block:: go

   package main

   import (
       "context"
       "github.com/arillso/go.ansible"
   )

   func main() {
       ctx := context.Background()

       playbook := ansible.NewPlaybook(
           ansible.WithPlaybookPath("site.yml"),
           ansible.WithInventory("inventory.ini"),
       )

       err := playbook.Exec(ctx)
       if err != nil {
           panic(err)
       }
   }

Using GitHub Actions
--------------------

Automate with CI/CD:

.. code-block:: yaml

   # .github/workflows/deploy.yml
   name: Deploy Infrastructure

   on:
     push:
       branches: [main]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Deploy with Ansible
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: site.yml
             inventory: inventory.ini
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             vault_password: ${{ secrets.VAULT_PASSWORD }}

Common Patterns
---------------

Secrets Management
~~~~~~~~~~~~~~~~~~

Use Bitwarden for secrets:

.. code-block:: yaml

   - name: Retrieve secrets from Bitwarden
     ansible.builtin.include_role:
       name: arillso.system.bitwarden_secrets
     vars:
       bitwarden_secrets:
         - id: "database-password"
           field: "password"
           register_as: db_password

Idempotent Operations
~~~~~~~~~~~~~~~~~~~~~

All arillso roles are idempotent:

.. code-block:: bash

   # Run multiple times - only changes what's needed
   ansible-playbook site.yml
   ansible-playbook site.yml  # No changes
   ansible-playbook site.yml  # Still no changes

Check Mode (Dry Run)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # See what would change without making changes
   ansible-playbook site.yml --check --diff

Troubleshooting
---------------

Installation Issues
~~~~~~~~~~~~~~~~~~~

**Collection not found:**

.. code-block:: bash

   # Update Galaxy API
   ansible-galaxy collection install arillso.system --force

**Version conflicts:**

.. code-block:: bash

   # Show installed versions
   ansible-galaxy collection list

   # Upgrade to latest
   ansible-galaxy collection install arillso.system --upgrade

Connection Issues
~~~~~~~~~~~~~~~~~

**SSH connection failed:**

.. code-block:: bash

   # Test connectivity
   ansible all -i inventory.ini -m ping

   # Verbose output
   ansible-playbook site.yml -vvv

**Permission denied:**

.. code-block:: bash

   # Ensure SSH key is correct
   ssh -i ~/.ssh/id_rsa user@host

   # Check become password
   ansible-playbook site.yml --ask-become-pass

Next Steps
----------

Now that you've completed the quick start:

1. **Explore Collections**

   * :ref:`arillso.system <plugins_in_arillso.system>` - System management
   * :ref:`arillso.container <plugins_in_arillso.container>` - Containers
   * :ref:`arillso.agent <plugins_in_arillso.agent>` - Monitoring

2. **Learn Best Practices**

   * :ref:`security` - Security guidelines
   * :ref:`standards` - Repository standards
   * :ref:`contributing` - Contribute to arillso

3. **Advanced Topics**

   * :ref:`examples` - Real-world examples
   * :ref:`architecture` - Architecture guide
   * :ref:`troubleshooting` - Problem solving

4. **Get Help**

   * Check the troubleshooting guide
   * Open an issue on `GitHub <https://github.com/arillso>`_
   * Review :ref:`compatibility` for version info

.. seealso::

   * :ref:`standards` - Repository Standards
   * :ref:`contributing` - Contributing Guidelines
   * :ref:`cicd` - CI/CD Setup
