.. meta::
  :description: Architecture overview and design principles of arillso platform
  :keywords: arillso, architecture, design, components, ecosystem

.. _architecture:

Architecture Guide
==================

Understanding the arillso ecosystem architecture, design principles, and how components interact.

.. contents::
   :local:
   :depth: 2

Platform Overview
-----------------

arillso is a modular automation platform consisting of four main pillars:

.. mermaid::

   mindmap
     root((arillso Platform))
       Ansible Collections
         arillso.system
         arillso.container
         arillso.agent
       Container Images
         arillso/ansible
         Mitogen optimized
         Multi-platform
       Go Libraries
         go.ansible
         Programmatic API
         Context-aware
       GitHub Actions
         action.playbook
         CI/CD ready
         Vault support

Architecture Principles
-----------------------

1. **Modularity**
   Each component is independent but composable

2. **Production-Ready**
   Battle-tested with comprehensive testing and security scanning

3. **Consistency**
   Unified standards across all projects

4. **Open Source**
   MIT licensed, community-driven development

5. **Security First**
   SHA-pinned dependencies, CodeQL scanning, non-root containers

Component Architecture
----------------------

Ansible Collections Layer
~~~~~~~~~~~~~~~~~~~~~~~~~~

Three specialized collections form the core:

.. mermaid::

   flowchart TD
       System["arillso.system"]
       Container["arillso.container"]
       Agent["arillso.agent"]

       System --> SR["14+ roles"]
       System --> SF["Filters & Lookups"]
       System --> SM["Modules"]

       Container --> CR["7+ roles"]
       Container --> CK["K8s integration"]
       Container --> CG["GitOps support"]

       Agent --> AR["3+ roles"]
       Agent --> AM["Monitors"]
       Agent --> AO["Observability"]

**arillso.system** - System Configuration

* **Purpose:** Base system management and configuration
* **Scope:** OS-level operations, packages, networking, security
* **Use Cases:** Server provisioning, hardening, maintenance

Key roles:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Role
     - Responsibility
   * - ``access``
     - User management, SSH keys, sudo configuration
   * - ``packages``
     - Package installation, updates, repository management
   * - ``firewall``
     - nftables/iptables configuration, security rules
   * - ``network``
     - Network interfaces, routing, DNS configuration
   * - ``logging``
     - System logging, remote log forwarding
   * - ``tuning``
     - Kernel parameters, performance optimization
   * - ``systemd``
     - Service management, timers, unit files

**arillso.container** - Container Orchestration

* **Purpose:** Container runtime and orchestration
* **Scope:** Docker, Kubernetes, GitOps, service mesh
* **Use Cases:** Containerized workloads, K8s clusters, Fleet deployments

Key roles:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Role
     - Responsibility
   * - ``docker``
     - Docker Engine installation and configuration
   * - ``k3s``
     - Lightweight Kubernetes cluster deployment
   * - ``helm``
     - Helm chart deployment and management
   * - ``fleet``
     - Fleet GitOps for multi-cluster management
   * - ``tailscale``
     - Mesh networking and VPN

**arillso.agent** - Monitoring & Agents

* **Purpose:** Observability and monitoring agents
* **Scope:** Metrics, logs, traces, networking
* **Use Cases:** Infrastructure monitoring, observability stack

Key roles:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Role
     - Responsibility
   * - ``alloy``
     - Grafana Alloy - unified observability collector
   * - ``do``
     - DigitalOcean monitoring agent
   * - ``tailscale``
     - Tailscale VPN and mesh networking

Container Images Layer
~~~~~~~~~~~~~~~~~~~~~~

**docker.ansible** - Execution Environment

.. mermaid::

   flowchart TD
       Container["arillso/ansible Container"]
       Container --> Base["Base: Alpine Linux"]
       Container --> Ansible["Ansible 2.15+"]
       Container --> Mitogen["Mitogen<br/>2-7x faster"]
       Container --> K8s["Kubernetes tools<br/>kubectl, helm"]
       Container --> Platform["Multi-platform<br/>amd64, arm64"]
       Container --> Security["Non-root user"]

**Features:**

* Mitogen strategy for performance
* Pre-installed arillso collections
* Kubernetes tooling included
* Security-hardened Alpine base
* Multi-architecture support

Go Libraries Layer
~~~~~~~~~~~~~~~~~~

**go.ansible** - Programmatic Execution

.. mermaid::

   flowchart TD
       Library["go.ansible Library"]
       Library --> API["Playbook execution API"]
       Library --> Galaxy["Galaxy collection management"]
       Library --> Context["Context-aware operations"]
       Library --> Error["Error handling & logging"]

**Use Cases:**

* Embed Ansible in Go applications
* Custom automation tooling
* API-driven infrastructure management
* CI/CD integration

GitHub Actions Layer
~~~~~~~~~~~~~~~~~~~~

**action.playbook** - CI/CD Integration

.. mermaid::

   flowchart TD
       Action["action.playbook Action"]
       Action --> GHA["GitHub Actions integration"]
       Action --> SSH["SSH key normalization"]
       Action --> Vault["Vault password support"]
       Action --> Inventory["Multi-inventory support"]

Integration Patterns
--------------------

Pattern 1: Full Stack Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combining all collections for complete infrastructure:

.. mermaid::

   flowchart LR
       Layer1["Layer 1: Base System<br/>arillso.system<br/>OS hardening, packages, network, firewall"]
       Layer2["Layer 2: Container Runtime<br/>arillso.container<br/>Docker or K3s, Helm, Fleet GitOps"]
       Layer3["Layer 3: Monitoring<br/>arillso.agent<br/>Grafana Alloy, Tailscale VPN"]
       Layer4["Layer 4: Application Workloads<br/>Your applications and services"]

       Layer1 ==> Layer2
       Layer2 ==> Layer3
       Layer3 ==> Layer4

       style Layer1 fill:#0066FF,stroke:#0066FF,color:#fff
       style Layer2 fill:#4EC9B0,stroke:#4EC9B0,color:#fff
       style Layer3 fill:#A05FF7,stroke:#A05FF7,color:#fff
       style Layer4 fill:#FF6B35,stroke:#FF6B35,color:#fff

**Example playbook structure:**

.. code-block:: yaml

   ---
   # Base system configuration
   - import_playbook: playbooks/base-system.yml

   # Container runtime
   - import_playbook: playbooks/containers.yml

   # Monitoring and observability
   - import_playbook: playbooks/monitoring.yml

   # Application deployment
   - import_playbook: playbooks/applications.yml

Pattern 2: Kubernetes Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multi-node K3s cluster with monitoring:

.. mermaid::

   architecture-beta
       group cluster(cloud)[K3s Cluster]

       service master(server)[Master Node K3s server etcd API] in cluster
       service worker1(server)[Worker 1 K3s agent kubelet] in cluster
       service worker2(server)[Worker 2 K3s agent kubelet] in cluster

       service alloy(server)[Grafana Alloy Monitoring]
       service vpn(internet)[Tailscale VPN Secure Network]

       master:B --> T:worker1
       master:B --> T:worker2
       worker1:R --> L:alloy
       worker2:R --> L:alloy
       alloy:R --> L:vpn

Pattern 3: GitOps with Fleet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Continuous deployment with Fleet:

.. mermaid::

   flowchart LR
       subgraph git[Git Repository]
           manifests[manifests/]
       end

       fleet[Fleet Controller<br/>Fleet Manager]
       dev[Cluster Dev]
       staging[Cluster Staging]
       prod[Cluster Prod]

       manifests --> fleet
       fleet --> dev
       fleet --> staging
       fleet --> prod

Data Flow Architecture
----------------------

How data and control flows through the platform:

.. mermaid::

   flowchart TD
       Dev[Developer/Operator]
       Playbooks[Playbooks & Roles]
       Collections[arillso Collections]
       Hosts[Target Hosts<br/>Managed Nodes]
       Config[Configuration Templates]
       State[System State<br/>Desired]

       Dev --> Playbooks
       Playbooks --> Collections
       Collections -->|SSH| Hosts
       Collections --> Config
       Config --> State

       style Dev fill:#0066FF,stroke:#0066FF,color:#fff
       style Collections fill:#A05FF7,stroke:#A05FF7,color:#fff
       style State fill:#00D9A5,stroke:#00D9A5,color:#fff

Security Architecture
---------------------

Multi-layered security approach:

.. mermaid::

   block-beta
       columns 1
       block:layer4["Layer 4: Network Security"]:3
           VPN["Tailscale mesh VPN"]
           Seg["Network segmentation"]
           TLS["TLS/mTLS encryption"]
       end
       space
       block:layer3["Layer 3: Runtime Security"]:3
           Secrets["Secrets management Vault Bitwarden"]
           SSH["SSH key security"]
           FW["Firewall configuration"]
       end
       space
       block:layer2["Layer 2: Container Security"]:3
           Trivy["Trivy scanning"]
           NonRoot["Non-root user"]
           Alpine["Minimal base images Alpine"]
       end
       space
       block:layer1["Layer 1: Code Security"]:3
           SHA["SHA-pinned GitHub Actions"]
           CodeQL["CodeQL analysis"]
           Deps["Dependency scanning Renovate"]
       end

       layer1 --> layer2
       layer2 --> layer3
       layer3 --> layer4

       style layer1 fill:#0066FF,stroke:#0066FF,color:#fff
       style layer2 fill:#4EC9B0,stroke:#4EC9B0,color:#fff
       style layer3 fill:#A05FF7,stroke:#A05FF7,color:#fff
       style layer4 fill:#FF6B35,stroke:#FF6B35,color:#fff

CI/CD Architecture
------------------

Automated testing and deployment pipeline:

.. mermaid::

   flowchart LR
       Push[Code Push]
       Lint[Linting<br/>ansible-lint<br/>yamllint<br/>golangci-lint]
       Test[Testing<br/>Unit, Integration<br/>Molecule]
       Security[Security<br/>CodeQL, Trivy<br/>Dependency scan]
       Build[Build<br/>Collection build<br/>Container build]
       Publish[Publish<br/>Galaxy, Docker Hub<br/>GitHub Release]

       Push --> Lint
       Lint --> Test
       Test --> Security
       Security --> Build
       Build --> Publish

       style Push fill:#0066FF,stroke:#0066FF,color:#fff
       style Lint fill:#FFB020,stroke:#FFB020,color:#fff
       style Test fill:#4EC9B0,stroke:#4EC9B0,color:#fff
       style Security fill:#FF4757,stroke:#FF4757,color:#fff
       style Build fill:#A05FF7,stroke:#A05FF7,color:#fff
       style Publish fill:#00D9A5,stroke:#00D9A5,color:#fff

Scalability Patterns
--------------------

Horizontal Scaling
~~~~~~~~~~~~~~~~~~

Scale by adding more managed nodes:

.. mermaid::

   flowchart TD
       Control[Control Node<br/>Ansible]

       Node1[Node 1]
       Node2[Node 2]
       Node3[Node 3]
       NodeN[Node ...]
       Node98[Node 98]
       Node99[Node 99]

       Control --> Node1
       Control --> Node2
       Control --> Node3
       Control --> NodeN
       Control --> Node98
       Control --> Node99

       style Control fill:#0066FF,stroke:#0066FF,color:#fff

**Key Benefits:**

* Ansible handles parallelism
* Mitogen improves connection efficiency
* Role-based organization for clarity

Vertical Scaling
~~~~~~~~~~~~~~~~

Optimize individual node performance:

* System tuning role for kernel parameters
* Resource limits via systemd
* Performance monitoring with Alloy

Multi-Region Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy across multiple regions:

.. mermaid::

   architecture-beta
       service gitops(disk)[Central GitOps Repository]

       group us(cloud)[Region US]
       group eu(cloud)[Region EU]
       group apac(cloud)[Region APAC]

       service us_k3s(server)[K3s Fleet Monitoring] in us
       service eu_k3s(server)[K3s Fleet Monitoring] in eu
       service apac_k3s(server)[K3s Fleet Monitoring] in apac

       gitops:R --> L:us_k3s
       gitops:R --> L:eu_k3s
       gitops:R --> L:apac_k3s

High Availability
~~~~~~~~~~~~~~~~~

HA K3s cluster configuration:

.. mermaid::

   architecture-beta
       service lb(internet)[Load Balancer HAProxy Nginx]

       group masters(cloud)[Control Plane]
       group workers(cloud)[Worker Nodes]

       service master1(server)[Master 1 etcd] in masters
       service master2(server)[Master 2 etcd] in masters
       service master3(server)[Master 3 etcd] in masters

       service worker1(server)[Worker 1] in workers
       service worker2(server)[Worker 2] in workers
       service worker3(server)[Worker 3] in workers
       service worker4(server)[Worker 4] in workers

       lb:B --> T:master1
       lb:B --> T:master2
       lb:B --> T:master3

       master1:B --> T:worker1
       master2:B --> T:worker2
       master3:B --> T:worker3
       master1:B --> T:worker4

Deployment Strategies
---------------------

Blue-Green Deployment
~~~~~~~~~~~~~~~~~~~~~

Zero-downtime updates with Fleet:

.. code-block:: yaml

   # fleet.yaml
   targetCustomizations:
     - name: blue
       clusterSelector:
         matchLabels:
           env: blue
     - name: green
       clusterSelector:
         matchLabels:
           env: green

Rolling Updates
~~~~~~~~~~~~~~~

Progressive rollout across nodes:

.. code-block:: yaml

   ---
   - name: Rolling update
     hosts: webservers
     serial: "25%"  # Update 25% at a time
     max_fail_percentage: 10
     tasks:
       - name: Update application
         ansible.builtin.include_role:
           name: arillso.container.k3s

Canary Deployment
~~~~~~~~~~~~~~~~~

Test with small subset first:

.. code-block:: yaml

   ---
   # Deploy to canary group (5% of fleet)
   - name: Canary deployment
     hosts: canary
     tasks:
       - name: Deploy new version
         ansible.builtin.include_role:
           name: app_deployment

   # Monitor metrics...

   # If successful, deploy to remaining 95%
   - name: Full deployment
     hosts: production
     tasks:
       - name: Deploy new version
         ansible.builtin.include_role:
           name: app_deployment

Observability Architecture
--------------------------

Grafana Alloy as unified collector:

.. mermaid::

   architecture-beta
       group nodes(cloud)[Application Nodes]
       group backends(cloud)[Storage Backends]

       service alloy(server)[Grafana Alloy Collector] in nodes

       service prometheus(database)[Prometheus Metrics] in backends
       service loki(database)[Loki Logs] in backends
       service tempo(database)[Tempo Traces] in backends

       service grafana(server)[Grafana Dashboards]

       alloy:R --> L:prometheus
       alloy:R --> L:loki
       alloy:R --> L:tempo

       prometheus:R --> L:grafana
       loki:R --> L:grafana
       tempo:R --> L:grafana

Extension Points
----------------

The architecture supports extensions:

Custom Roles
~~~~~~~~~~~~

Add your own roles alongside arillso roles:

.. code-block:: yaml

   collections/
   ├── requirements.yml
   │   ├── arillso.system
   │   ├── arillso.container
   │   └── arillso.agent
   └── my_company/
       └── custom/
           └── roles/
               └── my_custom_role/

Custom Plugins
~~~~~~~~~~~~~~

Extend with custom filters, lookups, modules:

.. code-block:: yaml

   plugins/
   ├── filter/
   │   └── my_custom_filter.py
   ├── lookup/
   │   └── my_custom_lookup.py
   └── modules/
       └── my_custom_module.py

Design Decisions
----------------

Why Ansible?
~~~~~~~~~~~~

* **Agentless:** No agents to install or maintain
* **Declarative:** Describe desired state, not steps
* **Idempotent:** Safe to run multiple times
* **Extensible:** Easy to extend with roles and plugins

Why Alpine Linux?
~~~~~~~~~~~~~~~~~

* **Minimal:** Smaller attack surface
* **Secure:** Security-focused distribution
* **Fast:** Quick container startup
* **Efficient:** Low resource usage

Why Mitogen?
~~~~~~~~~~~~

* **Performance:** 2-7x faster than standard Ansible
* **Efficiency:** Fewer SSH connections
* **Compatibility:** Drop-in replacement for standard strategy

Why K3s over K8s?
~~~~~~~~~~~~~~~~~

* **Lightweight:** Single binary, minimal dependencies
* **Fast:** Quick installation and startup
* **Production-Ready:** CNCF certified Kubernetes
* **Edge-Friendly:** Works on ARM and low-resource environments

Best Practices
--------------

1. **Start Simple**
   Begin with system collection, add containers and monitoring as needed

2. **Use Inventory Groups**
   Organize hosts by role, environment, location

3. **Version Pin Collections**
   Specify versions in requirements.yml for reproducibility

4. **Test in Stages**
   Development → Staging → Production

5. **Monitor Everything**
   Deploy monitoring alongside infrastructure

6. **Automate Secrets**
   Use Bitwarden or Vault, never commit secrets

7. **Document Custom Code**
   Keep AGENTS.md and CLAUDE.md updated

Common Anti-Patterns
--------------------

❌ **Don't:**

* Mix multiple automation tools (choose Ansible or stick with it)
* Hardcode values (use variables and inventory)
* Skip testing (always test before production)
* Ignore monitoring (deploy observability from day one)
* Use root user (configure proper privilege escalation)
* Commit secrets (use vault or secret management)

✅ **Do:**

* Use roles for reusability
* Keep playbooks idempotent
* Version control everything
* Test with --check mode first
* Monitor and log everything
* Follow the standards

Reference Architecture
----------------------

Complete production-ready reference:

.. mermaid::

   architecture-beta
       group control(cloud)[Control Plane Ansible Controller]
       group infra(cloud)[Managed Infrastructure]

       service playbooks(disk)[Playbooks Roles] in control
       service inventory(disk)[Inventory Git managed] in control
       service secrets(disk)[Secrets Vault Bitwarden] in control

       service system(server)[Base System arillso system] in infra
       service container(server)[Containers arillso container] in infra
       service monitoring(server)[Monitoring arillso agent] in infra

       service network(internet)[Network Tailscale VPN] in infra
       service storage(database)[Storage Local S3] in infra
       service security(server)[Security Firewall hardening] in infra
       service mon(server)[Observability Alloy Prometheus Loki Tempo] in infra
       service gitops(server)[GitOps Fleet for K8s] in infra

       playbooks:R --> L:system
       inventory:R --> L:system
       secrets:R --> L:system

       system:B --> T:container
       container:B --> T:monitoring

       network:R --> L:security
       storage:R --> L:system
       monitoring:R --> L:mon
       container:R --> L:gitops

Next Steps
----------

* Explore :ref:`quickstart` for hands-on examples
* Review :ref:`security` for hardening guidance
* Check :ref:`examples` for real-world scenarios
* Read :ref:`troubleshooting` for problem solving

.. seealso::

   * :ref:`standards` - Repository Standards
   * :ref:`cicd` - CI/CD Workflows
   * :ref:`contributing` - Contributing Guidelines
