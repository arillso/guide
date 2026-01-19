.. meta::
  :description: Security best practices and hardening guide for arillso
  :keywords: arillso, security, hardening, best practices, compliance

.. _security:

Security & Best Practices
==========================

Security guidelines, hardening strategies, and best practices for arillso-managed infrastructure.

.. contents::
   :local:
   :depth: 2

Security Philosophy
-------------------

arillso follows a **defense-in-depth** approach with multiple security layers:

1. **Code Security** - SHA-pinned dependencies, CodeQL scanning
2. **Container Security** - Minimal images, non-root users, Trivy scanning
3. **Runtime Security** - Secrets management, SSH hardening, firewall
4. **Network Security** - VPN mesh, TLS, network segmentation
5. **Compliance** - Audit logs, monitoring, access control

Secrets Management
------------------

Never commit secrets to version control.

Using Ansible Vault
~~~~~~~~~~~~~~~~~~~

**Create encrypted file:**

.. code-block:: bash

   # Create new vault file
   ansible-vault create vault.yml

   # Edit existing vault
   ansible-vault edit vault.yml

   # Encrypt existing file
   ansible-vault encrypt secrets.yml

**Vault file structure:**

.. code-block:: yaml

   ---
   # vault.yml
   vault_mysql_root_password: "super_secret_password"
   vault_api_key: "sk-1234567890abcdef"
   vault_tailscale_authkey: "tskey-auth-XXXXX"

**Use in playbooks:**

.. code-block:: yaml

   ---
   - name: Deploy with secrets
     hosts: all
     vars_files:
       - vault.yml

     tasks:
       - name: Configure database
         ansible.builtin.template:
           src: db_config.j2
           dest: /etc/db/config.yml
         vars:
           db_password: "{{ vault_mysql_root_password }}"

**Run with vault:**

.. code-block:: bash

   # Prompt for password
   ansible-playbook site.yml --ask-vault-pass

   # Use password file
   ansible-playbook site.yml --vault-password-file ~/.vault_pass

   # Multiple vaults
   ansible-playbook site.yml \
     --vault-id dev@~/.vault_dev \
     --vault-id prod@~/.vault_prod

Using Bitwarden Secrets
~~~~~~~~~~~~~~~~~~~~~~~~

Install Bitwarden Secrets Manager CLI for secrets retrieval:

.. code-block:: yaml

   ---
   - name: Install Bitwarden Secrets Manager CLI
     hosts: all
     become: true

     tasks:
       - name: Install bws CLI
         ansible.builtin.include_role:
           name: arillso.system.bitwarden_secrets
         vars:
           bitwarden_secrets_version: "1.0.0"
           bitwarden_secrets_install_path: "/usr/local/bin"

**Then use bws CLI in your playbooks:**

.. code-block:: yaml

   ---
   - name: Retrieve secrets using bws
     hosts: all
     become: true

     tasks:
       - name: Get secret from Bitwarden
         ansible.builtin.shell:
           cmd: bws secret get SECRET_ID --access-token "{{ lookup('env', 'BWS_ACCESS_TOKEN') }}"
         register: bws_secret
         changed_when: false
         no_log: true

       - name: Use secret
         ansible.builtin.debug:
           msg: "Secret retrieved"

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

For CI/CD environments:

.. code-block:: yaml

   ---
   # Use environment variables
   - name: Deploy
     hosts: all
     vars:
       db_password: "{{ lookup('env', 'DB_PASSWORD') }}"
       api_key: "{{ lookup('env', 'API_KEY') }}"

**GitHub Actions:**

.. code-block:: yaml

   - name: Deploy
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: deploy.yml
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}
       vault_password: ${{ secrets.VAULT_PASSWORD }}
     env:
       DB_PASSWORD: ${{ secrets.DB_PASSWORD }}

SSH Security
------------

SSH Key Management
~~~~~~~~~~~~~~~~~~

**Generate secure SSH keys:**

.. code-block:: bash

   # Ed25519 (recommended)
   ssh-keygen -t ed25519 -C "ansible@example.com"

   # RSA (if Ed25519 not supported)
   ssh-keygen -t rsa -b 4096 -C "ansible@example.com"

**Use arillso.system.access for key management:**

.. code-block:: yaml

   ---
   - name: Manage SSH access
     hosts: all
     become: true

     tasks:
       - name: Configure user access
         ansible.builtin.include_role:
           name: arillso.system.access
         vars:
           access_users:
             - name: admin
               shell: /bin/bash
               groups:
                 - sudo
               ssh_keys:
                 - key: "ssh-ed25519 AAAAC3... admin@example.com"

           access_sudoers:
             - name: admin
               user: admin
               nopasswd: true

           # Security settings
           access_ssh_password_authentication: false
           access_ssh_permit_root_login: "False"
           access_ssh_pubkey_authentication: true

SSH Hardening
~~~~~~~~~~~~~

**Harden SSH daemon with arillso.system.access:**

.. code-block:: yaml

   ---
   - name: Harden SSH configuration
     hosts: all
     become: true

     tasks:
       - name: Configure SSH server
         ansible.builtin.include_role:
           name: arillso.system.access
         vars:
           access_ssh_port: 22
           access_ssh_permit_root_login: "False"
           access_ssh_password_authentication: false
           access_ssh_pubkey_authentication: true
           access_ssh_x11_forwarding: false

Firewall Configuration
----------------------

Use arillso.system.firewall for consistent firewall management.

Basic Firewall Setup
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Configure firewall
     hosts: all
     become: true

     tasks:
       - name: Setup firewall rules
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
                       - ip saddr 10.0.0.0/8 tcp dport 22 accept comment "SSH from management"
                       - tcp dport 80 accept comment "HTTP"
                       - tcp dport 443 accept comment "HTTPS"

Advanced Firewall Rules
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
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

               # SSH rate limiting (prevent brute force)
               - tcp dport 22 ct state new limit rate 5/minute accept comment "SSH rate limit"

               # Allow specific admin IP
               - ip saddr 203.0.113.10 accept comment "Admin access"

               # Block malicious network
               - ip saddr 198.51.100.0/24 drop comment "Blocked network"

               # Allow Docker bridge network
               - ip saddr 172.17.0.0/16 accept comment "Docker network"

               # Log dropped packets
               - log prefix "firewall-drop: " drop

Network Segmentation
~~~~~~~~~~~~~~~~~~~~

.. mermaid::

   flowchart LR
       subgraph DMZ[DMZ - Public Zone]
           Web[Web Servers]
           LB[Load Balancer]
       end

       FW1[Firewall]

       subgraph App[Application Tier]
           AppServ[App Servers]
           Cache[Cache<br/>Redis]
       end

       FW2[Firewall]

       subgraph DB[Database Tier]
           Database[Database Servers]
           Backup[Backup Storage]
       end

       DMZ --> FW1
       FW1 --> App
       App --> FW2
       FW2 --> DB

       style DMZ fill:#FF4757,stroke:#FF4757,color:#fff
       style FW1 fill:#FFB020,stroke:#FFB020,color:#fff
       style App fill:#0066FF,stroke:#0066FF,color:#fff
       style FW2 fill:#FFB020,stroke:#FFB020,color:#fff
       style DB fill:#4EC9B0,stroke:#4EC9B0,color:#fff

System Hardening
----------------

Kernel Hardening
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Harden kernel
     hosts: all
     become: true

     tasks:
       - name: Apply kernel hardening
         ansible.builtin.include_role:
           name: arillso.system.tuning
         vars:
           tuning_sysctl:
             # Network security
             net.ipv4.conf.all.accept_source_route: 0
             net.ipv4.conf.default.accept_source_route: 0
             net.ipv4.conf.all.accept_redirects: 0
             net.ipv4.conf.default.accept_redirects: 0
             net.ipv4.conf.all.secure_redirects: 0
             net.ipv4.conf.default.secure_redirects: 0
             net.ipv4.conf.all.send_redirects: 0
             net.ipv4.conf.default.send_redirects: 0
             net.ipv4.icmp_echo_ignore_broadcasts: 1
             net.ipv4.icmp_ignore_bogus_error_responses: 1
             net.ipv4.tcp_syncookies: 1

             # Kernel security
             kernel.dmesg_restrict: 1
             kernel.kptr_restrict: 2
             kernel.yama.ptrace_scope: 2

             # Filesystem protection
             fs.protected_hardlinks: 1
             fs.protected_symlinks: 1
             fs.suid_dumpable: 0

Package Management
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Secure package management
     hosts: all
     become: true

     tasks:
       - name: Manage packages
         ansible.builtin.include_role:
           name: arillso.system.packages
         vars:
           # Install only what's needed
           packages_list:
             - name: fail2ban
               state: present
             - name: aide
               state: present

             # Remove unnecessary packages
             - name: telnet
               state: absent
             - name: rsh-client
               state: absent
             - name: nis
               state: absent

Container Security
------------------

Docker Security
~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Secure Docker
     hosts: docker_hosts
     become: true

     tasks:
       - name: Install Docker with security settings
         ansible.builtin.include_role:
           name: arillso.container.docker
         vars:
           docker_daemon:
             # Use user namespaces
             userns-remap: "default"

             # Limit logging
             log-driver: "json-file"
             log-opts:
               max-size: "10m"
               max-file: "3"

             # Live restore
             live-restore: true

           # Non-root Docker users
           docker_users:
             - appuser

**Container image security:**

.. code-block:: dockerfile

   # Use minimal base images
   FROM alpine:3.18

   # Don't run as root
   RUN addgroup -g 1000 appuser && \
       adduser -D -u 1000 -G appuser appuser

   USER appuser

   # Copy only what's needed
   COPY --chown=appuser:appuser app /app

   # Run with minimal permissions
   CMD ["/app/start.sh"]

Kubernetes Security
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Secure K3s
     hosts: k8s_all
     become: true

     tasks:
       - name: Deploy K3s with security
         ansible.builtin.include_role:
           name: arillso.container.k3s
         vars:
           k3s_secrets_encryption: true

           k3s_kube_apiserver_args:
             # Authentication
             - "--anonymous-auth=false"
             - "--enable-admission-plugins=NodeRestriction,PodSecurityPolicy"

             # Audit logging
             - "--audit-log-path=/var/log/k8s-audit.log"
             - "--audit-log-maxage=30"
             - "--audit-log-maxbackup=10"

           k3s_kubelet_args:
             # Security
             - "--protect-kernel-defaults=true"
             - "--read-only-port=0"

**Pod Security Policy:**

.. code-block:: yaml

   # psp-restricted.yaml
   apiVersion: policy/v1beta1
   kind: PodSecurityPolicy
   metadata:
     name: restricted
   spec:
     privileged: false
     allowPrivilegeEscalation: false
     requiredDropCapabilities:
       - ALL
     runAsUser:
       rule: MustRunAsNonRoot
     seLinux:
       rule: RunAsAny
     fsGroup:
       rule: RunAsAny
     volumes:
       - 'configMap'
       - 'emptyDir'
       - 'projected'
       - 'secret'
       - 'downwardAPI'
       - 'persistentVolumeClaim'

Monitoring & Auditing
---------------------

Security Monitoring
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Deploy security monitoring
     hosts: all
     become: true

     tasks:
       - name: Install Grafana Alloy for security
         ansible.builtin.include_role:
           name: arillso.agent.alloy
         vars:
           alloy_cluster_name: "security-monitoring"
           alloy_cluster_advertise_address: "{{ ansible_default_ipv4.address }}"
           alloy_cluster_advertise_port: "12345"

Audit Logging
~~~~~~~~~~~~~

**Configure rsyslog for centralized logging:**

.. code-block:: yaml

   ---
   - name: Configure rsyslog
     hosts: all
     become: true

     tasks:
       - name: Setup rsyslog forwarding
         ansible.builtin.include_role:
           name: arillso.system.logging
         vars:
           logging_rsyslog_entries:
             - name: forward-to-siem
               content: |
                 # Forward all logs to SIEM
                 *.* @@siem.example.com:514

**Log rotation for security logs:**

.. code-block:: yaml

   ---
   - name: Configure log rotation
     hosts: all
     become: true

     tasks:
       - name: Setup logrotate
         ansible.builtin.include_role:
           name: arillso.system.logging
         vars:
           logging_logrotate_entries:
             - name: auth-logs
               path: /var/log/auth.log
               options:
                 - daily
                 - rotate 90
                 - compress
                 - delaycompress
                 - notifempty

Compliance
----------

CIS Benchmarks
~~~~~~~~~~~~~~

Apply CIS benchmark recommendations using arillso roles:

.. code-block:: yaml

   ---
   - name: CIS hardening
     hosts: all
     become: true

     tasks:
       # 1. Install security packages
       - name: Install chrony for time sync
         ansible.builtin.include_role:
           name: arillso.system.packages
         vars:
           packages_list:
             - name: chrony
               state: present
             - name: aide
               state: present
             - name: fail2ban
               state: present

       # 2. Disable unused services
       - name: Stop unnecessary services
         ansible.builtin.systemd:
           name: "{{ item }}"
           state: stopped
           enabled: no
         loop:
           - avahi-daemon
           - cups
         ignore_errors: yes

       # 3. Kernel hardening
       - name: Apply CIS kernel parameters
         ansible.builtin.include_role:
           name: arillso.system.tuning
         vars:
           tuning_sysctl:
             net.ipv4.conf.all.accept_source_route: 0
             net.ipv4.conf.all.accept_redirects: 0
             net.ipv4.conf.all.send_redirects: 0
             kernel.dmesg_restrict: 1

Best Practices Checklist
-------------------------

Infrastructure Security
~~~~~~~~~~~~~~~~~~~~~~~

✅ **Access Control:**

* [ ] SSH keys only (no passwords)
* [ ] Sudo access limited to specific users
* [ ] Root login disabled
* [ ] SSH from trusted networks only

✅ **Firewall:**

* [ ] Default deny policy
* [ ] Only required ports open
* [ ] Rate limiting on public services
* [ ] Network segmentation implemented

✅ **System Hardening:**

* [ ] Minimal packages installed
* [ ] Unused services disabled
* [ ] Kernel hardening applied
* [ ] Automatic security updates enabled

✅ **Secrets Management:**

* [ ] Ansible Vault or secrets manager
* [ ] No secrets in version control
* [ ] Secrets rotated regularly
* [ ] Different secrets per environment

Container Security
~~~~~~~~~~~~~~~~~~

✅ **Image Security:**

* [ ] Minimal base images (Alpine)
* [ ] Non-root users
* [ ] No unnecessary packages
* [ ] Images scanned with Trivy

✅ **Runtime Security:**

* [ ] User namespaces enabled
* [ ] Resource limits set
* [ ] Read-only filesystems where possible
* [ ] Capabilities dropped

Monitoring & Compliance
~~~~~~~~~~~~~~~~~~~~~~~

✅ **Monitoring:**

* [ ] Centralized logging (Loki)
* [ ] Metrics collection (Prometheus)
* [ ] Security event alerts
* [ ] Log retention policy

✅ **Compliance:**

* [ ] Audit logging enabled
* [ ] CIS benchmarks applied
* [ ] Regular security scans
* [ ] Documented procedures

Common Security Mistakes
------------------------

❌ **Don't:**

1. **Commit secrets to Git**

   .. code-block:: yaml

      # ❌ WRONG
      db_password: "supersecret123"

   .. code-block:: yaml

      # ✅ CORRECT
      db_password: "{{ vault_db_password }}"

2. **Use weak SSH keys**

   .. code-block:: bash

      # ❌ WRONG
      ssh-keygen -t rsa -b 1024

      # ✅ CORRECT
      ssh-keygen -t ed25519

3. **Run containers as root**

   .. code-block:: dockerfile

      # ❌ WRONG
      FROM ubuntu
      COPY app /app
      CMD ["/app/start"]

      # ✅ CORRECT
      FROM alpine
      RUN adduser -D appuser
      USER appuser
      COPY --chown=appuser app /app
      CMD ["/app/start"]

4. **Disable firewall**

   .. code-block:: yaml

      # ❌ WRONG - No firewall configured

      # ✅ CORRECT
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

5. **Allow root SSH**

   .. code-block:: yaml

      # ❌ WRONG
      access_ssh_permit_root_login: "True"

      # ✅ CORRECT
      access_ssh_permit_root_login: "False"

Security Resources
------------------

Documentation
~~~~~~~~~~~~~

* `CIS Benchmarks <https://www.cisecurity.org/cis-benchmarks/>`_
* `OWASP Top 10 <https://owasp.org/www-project-top-ten/>`_
* `Docker Security <https://docs.docker.com/engine/security/>`_
* `Kubernetes Security <https://kubernetes.io/docs/concepts/security/>`_

Tools
~~~~~

* **Trivy** - Container image scanning
* **ansible-lint** - Playbook security checks
* **Vault** - Secrets management
* **Bitwarden** - Password management
* **Tailscale** - Zero-trust networking

Next Steps
----------

* Implement :ref:`quickstart` securely
* Review :ref:`examples` for secure patterns
* Check :ref:`troubleshooting` for security issues
* Read the compliance documentation for requirements

.. seealso::

   * :ref:`standards` - Repository Standards
   * :ref:`contributing` - Contributing Guidelines
   * :ref:`cicd` - CI/CD Security
