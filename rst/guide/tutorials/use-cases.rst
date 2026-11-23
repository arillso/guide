.. meta::
  :description: Short scenarios that combine arillso roles, the arillso/ansible image, action.playbook and go.ansible
  :keywords: arillso, use cases, scenarios, ansible

.. _use-cases:

Use Cases
=========

Short scenarios that combine roles from ``arillso.system``, ``arillso.container``
and ``arillso.agent``, plus the container image, the GitHub Action and the Go
library. Each scenario lists the goal, a playbook and the facts that matter.
Variable names and defaults come from the role documentation linked in each
section; the documented collection versions are listed on the collection index
pages.

For complete project layouts with inventory and ``requirements.yml`` see
:ref:`examples`.

.. contents::
   :local:
   :depth: 1

.. _usecase-docker-server:

Docker Host with Firewall and Tailscale
---------------------------------------

**Goal:** a Docker host that accepts SSH, HTTP and HTTPS, rotates container logs,
and is reachable over Tailscale.

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
                       - comment: "Loopback"
                         iifname: "lo"
                         action: accept
                       - comment: "Established and related"
                         ct_state: ["established", "related"]
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

**Facts:**

* The ``docker`` role merges ``docker_daemon`` recursively on top of
  ``docker_daemon_base``. The base sets ``log-driver: journald``,
  ``live-restore: true`` and ``no-new-privileges: true``. ``max-size`` and
  ``max-file`` only take effect with ``log-driver: json-file``.
* Setting ``firewall_tables`` replaces the role's default ruleset. That default
  also contains a ``forward`` chain with policy ``drop``; nftables evaluates every
  base chain on a hook, so such a chain also drops traffic Docker forwards to
  containers. The example defines no ``forward`` chain.
* ``tailscale_auth_key`` is the only required variable of
  ``arillso.agent.tailscale`` and is marked ``no_log``.

Role reference: :ref:`docker <ansible_collections.arillso.container.docker_role>`,
:ref:`firewall <ansible_collections.arillso.system.firewall_role>`,
:ref:`tailscale <ansible_collections.arillso.agent.tailscale_role>`.

.. _usecase-k3s-cluster:

K3s Cluster
-----------

**Goal:** one K3s server and two agents.

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

.. code-block:: ini

   [k3s_servers]
   k3s-1.example.com

   [k3s_agents]
   k3s-worker-1.example.com
   k3s-worker-2.example.com

**Facts:**

* ``k3s_version``, ``k3s_role`` (``server`` or ``agent``) and ``k3s_node_name``
  are required. ``k3s_server_init: true`` is set on the first server only.
* If ``k3s_token`` is empty, the role reads the token file from the first
  server. If ``k3s_server_url`` is empty on an agent, it takes the URL from the
  local K3s facts or from the first host of the inventory group
  ``k3s_controllers`` or ``k3s_servers``.
* The role loads ``br_netfilter``, sets ``net.ipv4.ip_forward`` and the
  ``bridge-nf-call`` sysctls in ``/etc/sysctl.d/99-k3s.conf`` and disables swap.
  No separate tuning step is needed for that.
* ``k3s_security_hardening`` defaults to ``true``: secrets encryption,
  ``anonymous-auth=false``, the ``NodeRestriction`` admission plugin and
  ``read-only-port=0``.
* Upgrades are limited to one minor version at a time; downgrades fail.

Role reference: :ref:`k3s <ansible_collections.arillso.container.k3s_role>`.

.. _usecase-dev-workstation:

Developer Workstation
---------------------

**Goal:** the same Ansible tooling, Docker and Docker Compose on every developer
machine.

.. code-block:: yaml

   ---
   - name: Set up a developer workstation
     hosts: localhost
     connection: local
     become: true

     tasks:
       - name: Install Ansible tooling into a virtualenv
         ansible.builtin.include_role:
           name: arillso.system.python
         vars:
           python_packages:
             - name: ansible-core
               virtualenv: /opt/ansible-tools
             - name: ansible-lint
               virtualenv: /opt/ansible-tools
             - name: molecule
               virtualenv: /opt/ansible-tools

       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker

       - name: Install Docker Compose
         ansible.builtin.include_role:
           name: arillso.container.docker_compose_v2

.. code-block:: bash

   ansible-playbook workstation.yml -K

**Facts:**

* ``python_packages`` is a list of dicts; ``name`` is required, ``virtualenv``
  installs into a venv created with ``python_virtualenv_command``
  (default ``python3 -m venv``).
* ``docker_compose_v2`` installs the Compose plugin
  (``docker_compose_v2_version``). It only manages a Compose project when
  ``docker_compose_v2_config`` is not empty.
* Supported platforms for ``docker`` and ``docker_compose_v2``: Debian bullseye
  and bookworm, Ubuntu jammy and noble, EL 9.

Role reference: :ref:`python <ansible_collections.arillso.system.python_role>`,
:ref:`docker_compose_v2 <ansible_collections.arillso.container.docker_compose_v2_role>`.

.. _usecase-do-droplet:

DigitalOcean Droplet
--------------------

**Goal:** install the DigitalOcean metrics agent and reach the droplet only
through Tailscale.

.. code-block:: yaml

   ---
   - name: Configure DigitalOcean droplets
     hosts: do_droplets
     become: true

     tasks:
       - name: Install the DigitalOcean agent
         ansible.builtin.include_role:
           name: arillso.agent.do

       - name: Join the tailnet
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ vault_tailscale_auth_key }}"

       - name: Accept inbound traffic only on tailscale0
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
                       - comment: "Tailscale interface"
                         iifname: "tailscale0"
                         action: accept
                       - comment: "Tailscale WireGuard"
                         udp_dport: 41641
                         action: accept

**Facts:**

* ``arillso.agent.do`` installs the ``do-agent`` package (``do_version``) and
  needs no variables.
* This ruleset drops public SSH. Run it only once the host is reachable over
  Tailscale, or keep an SSH rule until then.

Role reference: :ref:`do <ansible_collections.arillso.agent.do_role>`.

.. _usecase-helm-deployment:

Helm Charts on K3s
------------------

**Goal:** install charts on a K3s cluster from Ansible.

.. code-block:: yaml

   ---
   - name: Deploy Helm charts
     hosts: k3s_servers[0]
     become: true

     tasks:
       - name: Deploy charts through the K3s Helm controller
         ansible.builtin.include_role:
           name: arillso.container.helm
         vars:
           helm_enable_charts: true
           helm_repositories:
             jetstack: "https://charts.jetstack.io"
           helm_charts:
             - name: cert-manager
               chart: cert-manager
               repository: jetstack
               version: "v1.13.2"
               namespace: cert-manager
               create_namespace: true
               values:
                 installCRDs: true

**Facts:**

* The role does not run the ``helm`` binary. It creates ``helm.cattle.io/v1``
  ``HelmChart`` resources in ``kube-system`` and fails if that CRD is missing, so
  it needs the K3s Helm controller (``k3s_disable_helm_controller: false``).
* ``repository`` refers to a key in ``helm_repositories``; ``chart`` is the
  chart name without a repository prefix.
* Nothing is deployed unless ``helm_enable_charts`` is ``true``.

Role reference: :ref:`helm <ansible_collections.arillso.container.helm_role>`.

.. _usecase-grafana-alloy:

Grafana Alloy Cluster
---------------------

**Goal:** Grafana Alloy on every host, clustered, with metrics and journal logs.

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
           alloy_clustering_enabled: true
           alloy_cluster_name: "monitoring"
           alloy_cluster_advertise_address: "{{ ansible_facts['default_ipv4']['address'] }}"
           alloy_cluster_join_peers:
             - "alloy-1.example.com:12345"
             - "alloy-2.example.com:12345"
           alloy_prometheus_enabled: true
           alloy_advanced_node_exporter_enabled: true
           alloy_loki_enabled: true
           alloy_loki_journal_enabled: true

**Facts:**

* The ``alloy_cluster_*`` variables only take effect with
  ``alloy_clustering_enabled: true`` (default ``false``).
* ``alloy_port`` defaults to ``12345``.
* Remote targets default to ``http://localhost:9090/api/v1/write``
  (``alloy_prometheus_remote_write``) and
  ``http://localhost:3100/loki/api/v1/push`` (``alloy_loki_clients``); override
  both for a real backend.

Role reference: :ref:`alloy <ansible_collections.arillso.agent.alloy_role>`.

.. _usecase-system-hardening:

Host Baseline: SSH, Firewall, Sysctl
------------------------------------

**Goal:** key-only SSH, a default-drop firewall with rate-limited SSH, and a set
of hardening sysctls.

.. code-block:: yaml

   ---
   - name: Apply the host baseline
     hosts: servers
     become: true

     tasks:
       - name: Configure users and sshd
         ansible.builtin.include_role:
           name: arillso.system.access
         vars:
           access_users:
             - name: admin
               groups: ["sudo"]
               ssh_keys:
                 - key: "ssh-ed25519 AAAAC3... admin@example.com"
           access_ssh_permit_root_login: "no"
           access_ssh_password_authentication: false

       - name: Configure nftables with the role defaults
         ansible.builtin.include_role:
           name: arillso.system.firewall

       - name: Apply hardening sysctls
         ansible.builtin.include_role:
           name: arillso.system.tuning
         vars:
           tuning_sysctl_config:
             net.ipv4.conf.all.accept_redirects: 0
             net.ipv4.conf.all.send_redirects: 0
             kernel.dmesg_restrict: 1

**Facts:**

* Without overrides, ``arillso.system.firewall`` writes an ``inet filter`` table:
  input and forward policy ``drop``, output ``accept``. Input accepts loopback,
  established/related, and new SSH connections limited by
  ``firewall_ssh_rate_limit`` (``10/minute``, burst ``5``); dropped packets are
  logged with prefix ``nft-drop-input:``.
* ``access_ssh_permit_root_login`` accepts ``yes``, ``no``,
  ``prohibit-password`` (default) and ``forced-commands-only``. Password
  authentication is already ``false`` by default.
* ``tuning_sysctl_config`` replaces the role's default sysctl set. The
  ``tuning`` role also applies its other defaults (GRUB command line, swappiness,
  tuned profile); review them on the role page before use.

Role reference: :ref:`access <ansible_collections.arillso.system.access_role>`,
:ref:`tuning <ansible_collections.arillso.system.tuning_role>`.

.. _usecase-tailscale-mesh:

Tailscale Across Providers
--------------------------

**Goal:** hosts at several providers in one tailnet.

.. code-block:: yaml

   ---
   - name: Join all hosts to the tailnet
     hosts: all_servers
     become: true

     tasks:
       - name: Install Tailscale
         ansible.builtin.include_role:
           name: arillso.agent.tailscale
         vars:
           tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
           tailscale_accept_dns: "true"
           tailscale_accept_routes: "true"

**Facts:**

* The ``tailscale_*`` preference options are strings (``"true"``/``"false"``);
  the default empty string leaves the option unset.
* ``tailscale_version`` pins the package version.
* ``arillso.container.tailscale`` is a different role: it manages the Tailscale
  Kubernetes operator resources, not the host daemon.

.. _usecase-container-execution:

Run Playbooks from the arillso/ansible Image
--------------------------------------------

**Goal:** run ``ansible-playbook`` without a local Ansible installation.

.. code-block:: bash

   docker run --rm \
     -v "$(pwd)":/workspace -w /workspace \
     -v "$HOME/.ssh/id_ed25519":/home/ansible/.ssh/id_ed25519:ro \
     -e ANSIBLE_HOST_KEY_CHECKING=True \
     arillso/ansible ansible-playbook -i inventory.ini site.yml

**Facts:**

* Alpine base, runs as UID ``1000`` (user ``ansible``, home
  ``/home/ansible``); SSH keys go under ``/home/ansible/.ssh``, not ``/root``.
* Ships ``ansible-core``, ``kubectl``, ``helm``, ``kustomize`` and Mitogen.
  Mitogen is opt-in: ``-e ANSIBLE_STRATEGY=mitogen_linear``.
* The baked-in ``ansible.cfg`` sets ``host_key_checking = False``; set
  ``ANSIBLE_HOST_KEY_CHECKING=True`` for persistent hosts.
* Tags: ``latest`` and the ``ansible-core`` version; images for
  ``linux/amd64`` and ``linux/arm64`` on Docker Hub and ``ghcr.io/arillso/ansible``.

Details: :ref:`docker.ansible <docker_ansible>`.

.. _usecase-go-integration:

Run Playbooks from Go
---------------------

**Goal:** start ``ansible-playbook`` from a Go program.

.. code-block:: go

   package main

   import (
       "context"
       "log"

       ansible "github.com/arillso/go.ansible/v2"
   )

   func main() {
       pb := ansible.NewPlaybook()
       pb.Config.Playbooks = []string{"deploy.yml"}
       pb.Config.Inventories = []string{"production.ini"}
       pb.Config.ExtraVars = []string{"app_version=v1.2.3"}

       if err := pb.Exec(context.Background()); err != nil {
           log.Fatalf("playbook failed: %v", err)
       }
   }

**Facts:**

* The library builds and runs command lines; it does not embed Ansible.
  ``Exec`` calls ``ansible --version``, ``ansible-galaxy`` when Galaxy options are
  set, and ``ansible-playbook``, so all three must be on ``PATH``.
* The commands run through ``exec.CommandContext``; cancelling the context stops
  them.
* Each ``ExtraVars`` entry is passed as its own ``--extra-vars`` flag
  (``key=value`` or ``@file``).

Details: :ref:`go.ansible <go_ansible>`.

.. _usecase-github-actions:

Deploy from GitHub Actions
--------------------------

**Goal:** run a playbook on every push to ``main``.

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
           uses: arillso/action.playbook@@ACTION_PLAYBOOK_VERSION@
           with:
             playbook: playbooks/site.yml
             inventory: inventory/production.ini
             galaxy_file: requirements.yml
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             known_hosts: ${{ secrets.SSH_KNOWN_HOSTS }}
             vault_password: ${{ secrets.VAULT_PASSWORD }}
             extra_vars: |
               app_version=${{ github.sha }}

**Facts:**

* ``playbook`` and ``inventory`` are the only required inputs.
* ``private_key`` is loaded into ``ssh-agent``; ``known_hosts`` enables host key
  verification.
* ``dry_run: true`` runs with ``--check --diff``.
* Pin the action to a commit SHA in production workflows; tags are shown here
  for readability.

Details: :ref:`action.playbook <action_playbook>`.

.. seealso::

   * :ref:`examples` - complete project layouts
   * :ref:`quickstart` - first steps
   * :ref:`security` - secrets and hardening
