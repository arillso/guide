.. meta::
  :description: Secrets handling and host hardening with the arillso roles
  :keywords: arillso, security, hardening, secrets, ssh, nftables, k3s

.. _security:

Security
========

Secrets handling and host hardening with the arillso roles. Every role variable
named here is documented on the role page linked in its section; defaults refer to
the collection versions this guide documents.

.. contents::
   :local:
   :depth: 2

Secrets
-------

Keep secrets out of version control in plaintext. Pass them to roles as
variables; the roles do not fetch secrets themselves.

Ansible Vault
~~~~~~~~~~~~~

.. code-block:: bash

   ansible-vault create group_vars/all/vault.yml
   ansible-vault edit group_vars/all/vault.yml

   ansible-playbook site.yml --ask-vault-pass
   ansible-playbook site.yml --vault-password-file ~/.vault_pass
   ansible-playbook site.yml --vault-id dev@~/.vault_dev --vault-id prod@~/.vault_prod

.. code-block:: yaml

   # group_vars/all/vault.yml (encrypted)
   vault_tailscale_auth_key: "tskey-auth-..."

.. code-block:: yaml

   - name: Join the tailnet
     ansible.builtin.include_role:
       name: arillso.agent.tailscale
     vars:
       tailscale_auth_key: "{{ vault_tailscale_auth_key }}"

Bitwarden Secrets Manager
~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`arillso.system.bitwarden_secrets <ansible_collections.arillso.system.bitwarden_secrets_role>`
installs the ``bws`` CLI (``bitwarden_secrets_version``, default ``1.0.0``) to
``bitwarden_secrets_install_path`` (default ``/usr/local/bin``). Secrets are then
read with the ``community.general.bitwarden_secrets_manager`` lookup, which runs on
the control node, so install ``bws`` there. A complete project is in
:ref:`examples`.

Secrets in CI
~~~~~~~~~~~~~

With :ref:`action.playbook <action_playbook>`, pass secrets as inputs or as
environment variables of the step:

.. code-block:: yaml

   - name: Run playbook
     uses: arillso/action.playbook@0.5.0
     with:
       playbook: deploy.yml
       inventory: inventory/production.ini
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}
       known_hosts: ${{ secrets.SSH_KNOWN_HOSTS }}
       vault_password: ${{ secrets.VAULT_PASSWORD }}
     env:
       DB_PASSWORD: ${{ secrets.DB_PASSWORD }}

``vault_password`` and ``vault_password_file`` are alternatives, as are
``private_key`` and ``private_key_file``.

``no_log``
~~~~~~~~~~

Secret-carrying role options are declared ``no_log`` in ``argument_specs``, for
example ``tailscale_auth_key`` and ``k3s_token``. Some roles also have a switch
that controls ``no_log`` on their secret-handling tasks, such as
``tailscale_no_log_auth_key``,
``do_no_log_api_token``, ``alloy_no_log_config`` and ``alloy_no_log_env_file``
(all default ``true``). Set ``no_log: true`` on your own tasks that handle
secrets; see :ref:`ansible-roles`.

SSH Access
----------

:ref:`arillso.system.access <ansible_collections.arillso.system.access_role>`
manages users, groups, sudoers, ``authorized_keys`` and ``sshd_config``.

.. code-block:: yaml

   - name: Configure users and sshd
     ansible.builtin.include_role:
       name: arillso.system.access
     vars:
       access_users:
         - name: admin
           groups: ["sudo"]
           ssh_keys:
             - key: "ssh-ed25519 AAAAC3... admin@example.com"
       access_sudoers:
         - name: admin
           user: admin
           nopasswd: true
       access_ssh_permit_root_login: "no"
       access_ssh_allow_groups: ["sudo"]

Relevant defaults:

.. list-table::
   :header-rows: 1
   :widths: 45 25 30

   * - Variable
     - Default
     - Note
   * - ``access_ssh_permit_root_login``
     - ``prohibit-password``
     - ``yes``, ``no``, ``prohibit-password``, ``forced-commands-only``
   * - ``access_ssh_password_authentication``
     - ``false``
     -
   * - ``access_ssh_pubkey_authentication``
     - ``true``
     -
   * - ``access_ssh_max_auth_tries``
     - ``3``
     -
   * - ``access_ssh_x11_forwarding``
     - ``false``
     -
   * - ``access_ssh_agent_forwarding``
     - ``false``
     -
   * - ``access_ssh_tcp_forwarding``
     - ``true``
     -
   * - ``access_validate_ssh_config``
     - ``true``
     - runs ``sshd -t`` on the rendered config before it is written
   * - ``access_validate_sudoers``
     - ``true``
     - runs ``visudo -c`` on sudoers files before they are written

Firewall
--------

:ref:`arillso.system.firewall <ansible_collections.arillso.system.firewall_role>`
renders ``/etc/nftables.conf`` from YAML.

Default Ruleset
~~~~~~~~~~~~~~~

Without overrides the role writes one ``inet filter`` table:

* ``input``, policy ``drop``: accept loopback, accept established/related, accept
  new SSH connections on port 22 limited by ``firewall_ssh_rate_limit``
  (``10/minute``) and ``firewall_ssh_rate_burst`` (``5``), then log with
  ``firewall_log_drop_prefix`` (``nft-drop-input:``) at
  ``firewall_log_drop_rate_limit`` (``5/minute``) and drop.
* ``forward``, policy ``drop``: accept established/related.
* ``output``, policy ``accept``.

Raise ``firewall_ssh_rate_limit`` on hosts that open many short-lived SSH
connections (CI runners, bastions) instead of removing the rule.

Custom Rules
~~~~~~~~~~~~

Rules are dicts, not nftables strings. Keys include ``iifname``, ``oifname``,
``ip_saddr``, ``ip_daddr``, ``tcp_dport``, ``udp_dport``, ``ct_state``,
``limit``, ``burst``, ``log_prefix``, ``log_level``, ``comment`` and ``action``
(default ``accept``).

.. code-block:: yaml

   firewall_host:
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
               - comment: "SSH from the management network"
                 ip_saddr: "10.0.0.0/8"
                 tcp_dport: 22
                 action: accept
               - comment: "Blocked network"
                 ip_saddr: "198.51.100.0/24"
                 action: drop
               - comment: "HTTP and HTTPS"
                 tcp_dport: [80, 443]
                 action: accept

.. important::
   ``firewall_tables``, ``firewall_global``, ``firewall_group`` and
   ``firewall_host`` are not merged rule by rule. The last non-empty level in
   that order becomes the complete ruleset. A host that sets ``firewall_host``
   loses the default ruleset and everything from the lower levels.

On Docker hosts, define no ``forward`` chain with policy ``drop`` in the
``inet filter`` table: nftables evaluates every base chain on a hook, so it would
also drop traffic Docker forwards to containers.

Kernel Parameters
-----------------

:ref:`arillso.system.tuning <ansible_collections.arillso.system.tuning_role>`
writes sysctls from ``tuning_sysctl_config`` to
``/etc/sysctl.d/99-tuning.conf``.

.. code-block:: yaml

   - name: Apply hardening sysctls
     ansible.builtin.include_role:
       name: arillso.system.tuning
     vars:
       tuning_sysctl_config:
         net.ipv4.conf.all.accept_source_route: 0
         net.ipv4.conf.all.accept_redirects: 0
         net.ipv4.conf.all.send_redirects: 0
         net.ipv4.tcp_syncookies: 1
         kernel.dmesg_restrict: 1
         kernel.kptr_restrict: 2
         fs.protected_hardlinks: 1
         fs.protected_symlinks: 1

``tuning_sysctl_config`` replaces the role's default sysctl set, which contains
performance values (``vm.*``, ``net.core.*``, TCP buffers). The role also
manages the GRUB command line, swap, I/O scheduler, CPU governor, transparent
huge pages and the tuned profile; check those defaults before running it for
sysctls alone.

Packages
--------

:ref:`arillso.system.packages <ansible_collections.arillso.system.packages_role>`
installs and removes packages and can configure unattended upgrades. The role
supports Debian and Ubuntu only.

.. code-block:: yaml

   - name: Manage packages
     ansible.builtin.include_role:
       name: arillso.system.packages
     vars:
       packages_list:
         - name: fail2ban
           state: present
         - name: telnet
           state: absent
       packages_unattended_upgrades_enabled: true

With ``packages_unattended_upgrades_enabled: true`` the role installs and
configures ``unattended-upgrades``. The default origins include the
distribution's ``-security`` pocket; ``packages_unattended_upgrades_auto_reboot``
is ``false`` by default.

Docker
------

:ref:`arillso.container.docker <ansible_collections.arillso.container.docker_role>`
renders ``/etc/docker/daemon.json`` from ``docker_daemon_base`` merged recursively
with ``docker_daemon``.

* The base sets ``no-new-privileges: true``, ``live-restore: true`` and
  ``log-driver: journald``.
* ``no-new-privileges`` breaks images that rely on setuid binaries; opt out with
  ``docker_daemon: {no-new-privileges: false}``.
* ``userns-remap`` is not set by default. Enabling it changes bind-mount UIDs and
  disables ``--privileged`` containers:

.. code-block:: yaml

   docker_daemon:
     userns-remap: "default"

K3s
---

:ref:`arillso.container.k3s <ansible_collections.arillso.container.k3s_role>`
applies a hardening set while ``k3s_security_hardening`` is ``true`` (default):

.. list-table::
   :header-rows: 1
   :widths: 45 20 35

   * - Variable
     - Default
     - Effect
   * - ``k3s_secrets_encryption``
     - ``true``
     - Secrets encrypted at rest
   * - ``k3s_anonymous_auth``
     - ``false``
     - ``anonymous-auth=false``
   * - ``k3s_node_restriction``
     - ``true``
     - ``NodeRestriction`` admission plugin
   * - ``k3s_kubelet_read_only_port_disabled``
     - ``true``
     - ``read-only-port=0``
   * - ``k3s_audit_log_enabled``
     - ``true``
     - API audit log, ``k3s_audit_log_maxage`` ``30``, level ``Metadata``
   * - ``k3s_protect_kernel_defaults``
     - ``false``
     - ``protect-kernel-defaults``
   * - ``k3s_pod_security_admission_profile``
     - ``""``
     - ``privileged``, ``baseline`` or ``restricted`` as cluster default

Enabling the set on an existing cluster changes behaviour: anonymous health
probes and scrapers of kubelet port ``10255`` stop working.

Logging
-------

:ref:`arillso.system.logging <ansible_collections.arillso.system.logging_role>`
configures rsyslog and logrotate.

.. code-block:: yaml

   - name: Forward logs and rotate auth.log
     ansible.builtin.include_role:
       name: arillso.system.logging
     vars:
       logging_rsyslog_remote_servers:
         - host: siem.example.com
           port: 514
           protocol: tcp
       logging_logrotate_entries:
         - name: auth-logs
           path: /var/log/auth.log
           options:
             - daily
             - rotate 90
             - compress
             - delaycompress
             - notifempty

For journal and metrics shipping, use
:ref:`arillso.agent.alloy <ansible_collections.arillso.agent.alloy_role>` with
``alloy_loki_enabled`` and ``alloy_loki_journal_enabled``.

Checklist
---------

* Secrets only in Vault or a secrets manager, passed in as variables.
* ``no_log: true`` on tasks that handle secrets.
* SSH: keys only, ``access_ssh_permit_root_login`` not ``yes``.
* Firewall: default ``drop`` on input, only required ports open, SSH rate limit
  kept.
* Package upgrades: ``packages_unattended_upgrades_enabled`` or a scheduled run.
* Docker: ``no-new-privileges`` left on unless an image needs setuid.
* K3s: ``k3s_security_hardening`` left on; set a Pod Security Admission profile.

.. seealso::

   * :ref:`ansible-roles` - role design, ``no_log`` and secret-handling rules
   * :ref:`standards` - repository standards
   * :ref:`cicd` - CI/CD security
   * `Docker security <https://docs.docker.com/engine/security/>`_
   * `Kubernetes security <https://kubernetes.io/docs/concepts/security/>`_
