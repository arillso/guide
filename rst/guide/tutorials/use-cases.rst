.. meta::
  :description: Real-world use cases and scenarios for arillso collections
  :keywords: arillso, use cases, scenarios, examples, ansible

.. _use-cases:

Use Cases & Scenarios
=====================

Practical scenarios demonstrating how to use arillso collections for common infrastructure tasks.

.. contents::
   :local:
   :depth: 2

Overview
--------

This guide presents realistic use cases from daily operations. Each includes:

* **Problem** - What you need to accomplish
* **Solution** - Complete working playbook with correct parameters
* **Key Points** - Important implementation details

.. _usecase-docker-server:

Docker Application Server
--------------------------

**Problem:** You need to deploy a production-ready Docker host that can run containerized applications securely. The server should have a hardened firewall that only allows necessary traffic (SSH, HTTP, HTTPS), implement Docker log rotation to prevent disk space issues, and provide secure remote access via Tailscale VPN without exposing additional ports to the internet.

**Solution:**

.. code-block:: yaml

   ---
   - name: Configure Docker server
     hosts: docker_servers
     become: true

     tasks:
       # Install Docker
       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker
         vars:
           docker_daemon:
             log-driver: "json-file"
             log-opts:
               max-size: "10m"
               max-file: "3"

       # Configure firewall
       - name: Setup firewall
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

       # Tailscale for remote access
       - name: Setup Tailscale
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ vault_tailscale_key }}"
           tailscale_accept_dns: "true"

**Key Points:**

* Docker log rotation prevents disk space issues
* Firewall uses nftables with default-drop policy
* Tailscale provides secure remote access without exposing ports

.. _usecase-k3s-cluster:

K3s Cluster Setup
-----------------

**Problem:** You want to run Kubernetes workloads but find standard K8s too resource-intensive. You need a lightweight, production-ready Kubernetes distribution that can run on edge devices, development environments, or resource-constrained servers. The cluster requires proper kernel tuning for container networking, firewall rules for K3s components, and a reliable way to join worker nodes to the control plane.

**Solution:**

.. code-block:: yaml

   ---
   - name: Prepare all K3s nodes
     hosts: k3s_all
     become: true

     tasks:
       # System tuning
       - name: Configure kernel parameters
         ansible.builtin.include_role:
           name: arillso.system.tuning
         vars:
           tuning_sysctl:
             net.ipv4.ip_forward: 1
             net.bridge.bridge-nf-call-iptables: 1

       # Firewall for K3s
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
           k3s_server_url: ""  # Empty for first server
           k3s_token: "{{ k3s_cluster_token }}"

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
           k3s_token: "{{ k3s_cluster_token }}"

**Inventory:**

.. code-block:: ini

   [k3s_server]
   k3s-1.example.com

   [k3s_agents]
   k3s-worker-1.example.com
   k3s-worker-2.example.com

   [k3s_all:children]
   k3s_server
   k3s_agents

**Key Points:**

* Kernel parameters configured for Kubernetes networking
* K3s server deployed first, then agents join
* All nodes require same version and cluster token

.. _usecase-dev-workstation:

Developer Workstation
---------------------

**Problem:** Your development team needs consistent, reproducible workstation setups. Each developer should have the same Python toolchain (Ansible, ansible-lint, molecule for testing), Docker for local container development, and Docker Compose for multi-container applications. Manual installation leads to version mismatches and "works on my machine" problems.

**Solution:**

.. code-block:: yaml

   ---
   - name: Setup developer workstation
     hosts: localhost
     become: true

     tasks:
       # Install Python packages
       - name: Setup Python environment
         ansible.builtin.include_role:
           name: arillso.system.python
         vars:
           python_packages:
             - ansible
             - ansible-lint
             - molecule

       # Install Docker
       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker

       # Docker Compose
       - name: Install Docker Compose
         ansible.builtin.include_role:
           name: arillso.container.docker_compose_v2

**Run locally:**

.. code-block:: bash

   ansible-playbook workstation.yml -K

**Key Points:**

* Python packages installed for Ansible development
* Docker and Docker Compose for local testing
* Run with ``-K`` to prompt for sudo password

.. _usecase-do-droplet:

DigitalOcean Droplet with Monitoring
-------------------------------------

**Problem:** You're running infrastructure on DigitalOcean and need visibility into server metrics without installing complex monitoring stacks. DigitalOcean provides a free monitoring agent, but you want to automate its installation across all droplets. Additionally, you need secure access without exposing SSH to the public internet, using Tailscale to create a private mesh network between all your servers.

**Solution:**

.. code-block:: yaml

   ---
   - name: Configure DigitalOcean droplet
     hosts: do_droplets
     become: true

     tasks:
       # Install DO monitoring agent
       - name: Install DigitalOcean agent
         ansible.builtin.include_role:
           name: arillso.agent.do

       # Tailscale for access
       - name: Setup Tailscale
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ vault_tailscale_key }}"
           tailscale_accept_dns: "true"

       # Firewall (allow only Tailscale)
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
                       - iifname tailscale0 accept
                       - ct state established,related accept
                       - udp dport 41641 accept comment "Tailscale"

**Key Points:**

* DigitalOcean monitoring agent for metrics
* Tailscale mesh network for secure access
* Firewall allows only Tailscale connections

.. _usecase-helm-deployment:

Helm Chart Deployment
----------------------

**Problem:** You have a K3s or Kubernetes cluster and need to deploy production applications like NGINX Ingress Controller and PostgreSQL. Managing raw Kubernetes YAML manifests is error-prone and doesn't provide good version control. Helm charts offer packaged, versioned application deployments with customizable values, but you want to automate the entire process: adding Helm repositories, deploying multiple charts with custom configurations, and creating namespaces automatically.

**Solution:**

.. code-block:: yaml

   ---
   - name: Deploy Helm charts
     hosts: k3s_server[0]
     become: true

     tasks:
       - name: Deploy applications via Helm
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

**Key Points:**

* Helm repositories added before deploying charts
* Each chart can have custom values
* Namespaces created automatically if needed

.. _usecase-grafana-alloy:

Grafana Alloy Monitoring
-------------------------

**Problem:** You're using Grafana Cloud or self-hosted Grafana and need to collect metrics, logs, and traces from distributed servers. Grafana Alloy is the next-generation telemetry collector that replaces Grafana Agent. You need to deploy Alloy agents across your infrastructure in a clustered configuration for high availability, where agents can discover each other and share workload, ensuring no data loss if a single agent fails.

**Solution:**

.. code-block:: yaml

   ---
   - name: Deploy Grafana Alloy
     hosts: monitored_servers
     become: true

     tasks:
       - name: Install Grafana Alloy
         ansible.builtin.include_role:
           name: arillso.agent.alloy
         vars:
           alloy_cluster_name: "production-monitoring"
           alloy_cluster_advertise_address: "{{ ansible_default_ipv4.address }}"
           alloy_cluster_advertise_port: "12345"
           alloy_cluster_join_peers:
             - "alloy-1.example.com:12345"
             - "alloy-2.example.com:12345"

**Key Points:**

* Alloy agents form a cluster for high availability
* Advertise address set to primary network interface
* Join existing cluster via peer addresses

.. _usecase-system-hardening:

System Hardening
----------------

**Problem:** You're deploying production servers that will be exposed to the internet and need to implement security best practices. The server requires a restrictive firewall with default-drop policy that only allows essential services, SSH rate limiting to prevent brute-force attacks, and kernel parameter hardening to disable unnecessary network features that could be exploited. This follows CIS benchmark recommendations and security hardening guidelines.

**Solution:**

.. code-block:: yaml

   ---
   - name: Harden server
     hosts: production_servers
     become: true

     tasks:
       # Restrictive firewall
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
                       - tcp dport 22 ct state new limit rate 5/minute accept comment "SSH rate limit"

       # Security tuning
       - name: Configure sysctl
         ansible.builtin.include_role:
           name: arillso.system.tuning
         vars:
           tuning_sysctl:
             net.ipv4.conf.all.accept_redirects: 0
             net.ipv4.conf.all.send_redirects: 0
             kernel.dmesg_restrict: 1

**Key Points:**

* Default-drop firewall policy
* SSH rate limiting prevents brute force
* Kernel hardening parameters applied

.. _usecase-tailscale-mesh:

Multi-Region Tailscale Mesh
----------------------------

**Problem:** Your infrastructure spans multiple cloud providers (AWS, Azure, DigitalOcean) and regions. Setting up VPN tunnels between each provider is complex, expensive, and doesn't scale. You need a zero-config mesh VPN that allows all servers to communicate securely via private IPs, supports DNS resolution between servers, and doesn't require managing VPN gateways or firewall rules for inter-server communication. Tailscale provides this with WireGuard-based encryption.

**Solution:**

.. code-block:: yaml

   ---
   - name: Setup Tailscale mesh
     hosts: all_servers
     become: true

     tasks:
       - name: Install Tailscale
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ vault_tailscale_key }}"
           tailscale_accept_dns: "true"
           tailscale_accept_routes: "true"

**Inventory:**

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

**Key Points:**

* Single Tailscale mesh across all cloud providers
* DNS resolution between all servers
* No exposed public ports needed

.. _usecase-container-execution:

Run Playbooks in Docker Container
----------------------------------

**Problem:** You want to run Ansible playbooks without installing Ansible and its dependencies on your local machine. This is especially useful for CI/CD pipelines, developer onboarding, or ensuring consistent Ansible versions across a team. The arillso/ansible container image provides a complete Ansible environment with Mitogen (2-7x performance boost), kubectl, helm, and other essential tools in an Alpine-based, multi-platform image.

**Solution:**

.. code-block:: bash

   # Pull the arillso/ansible image
   docker pull arillso/ansible:latest

   # Run playbook from current directory
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible ansible-playbook site.yml

   # Run with inventory
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     arillso/ansible ansible-playbook -i inventory.ini playbook.yml

   # Run with extra vars
   docker run --rm \
     -v $(pwd):/workspace \
     -v ~/.ssh:/root/.ssh:ro \
     -e ANSIBLE_HOST_KEY_CHECKING=False \
     arillso/ansible ansible-playbook playbook.yml -e "env=production"

**Key Points:**

* Container includes Ansible, Mitogen, kubectl, helm
* Mount your playbooks and SSH keys as volumes
* Alpine-based, multi-platform (amd64, arm64)
* Mitogen enabled for 2-7x faster execution

.. _usecase-go-integration:

Programmatic Ansible with Go
-----------------------------

**Problem:** You're building a custom automation platform, self-service portal, or infrastructure management tool in Go and need to execute Ansible playbooks programmatically. Instead of shelling out to ansible-playbook commands and parsing stdout, you want a native Go library that provides type-safe playbook execution with proper context handling, structured output, and error management. The go.ansible library provides this integration.

**Solution:**

.. code-block:: go

   package main

   import (
       "context"
       "fmt"
       "log"

       "github.com/arillso/go.ansible/pkg/ansible"
   )

   func main() {
       // Create Ansible executor
       executor := ansible.NewExecutor()

       // Run playbook
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
           log.Fatalf("Playbook failed: %v", err)
       }

       fmt.Printf("Playbook completed: %s\n", result.Status)
   }

**Key Points:**

* Embed Ansible execution in Go applications
* Context-aware for timeout and cancellation
* Structured output for programmatic use
* Ideal for custom automation tools and APIs

.. _usecase-github-actions:

GitHub Actions CI/CD
--------------------

**Problem:** You want to implement GitOps practices where infrastructure changes are automatically deployed when code is pushed to your repository. GitHub Actions provides CI/CD capabilities, but setting up Ansible execution requires installing dependencies, managing SSH keys, handling vault passwords, and installing Galaxy collections. The arillso/action.playbook GitHub Action handles all of this automatically, providing a one-step solution for Ansible deployments in CI/CD pipelines.

**Solution:**

.. code-block:: yaml

   # .github/workflows/deploy.yml
   name: Deploy Infrastructure

   on:
     push:
       branches:
         - main

   jobs:
     deploy:
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v4

         - name: Deploy with Ansible
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: playbooks/site.yml
             inventory: inventory/production.ini
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             vault_password: ${{ secrets.VAULT_PASSWORD }}
             requirements: requirements.yml

**With extra variables:**

.. code-block:: yaml

   - name: Deploy with extra vars
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: deploy.yml
       inventory: production.ini
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}
       extra_vars: |
         app_version=${{ github.sha }}
         environment=production

**Key Points:**

* Automatic SSH key normalization
* Vault password support
* Requirements auto-installation
* Full Ansible output in CI logs

Next Steps
----------

* Review :ref:`quickstart` for getting started
* Explore :ref:`examples` for complete playbooks
* Check :ref:`architecture` for design patterns

.. seealso::

   * :ref:`quickstart` - Quick Start Guide
   * :ref:`examples` - Complete Examples
   * :ref:`architecture` - Architecture Guide
