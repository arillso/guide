.. meta::
  :description: Troubleshooting guide and FAQ for arillso
  :keywords: arillso, troubleshooting, faq, debugging, errors

.. _troubleshooting:

Troubleshooting & FAQ
=====================

Common issues, solutions, and frequently asked questions for arillso collections.

.. contents::
   :local:
   :depth: 2

Installation Issues
-------------------

Collection Not Found
~~~~~~~~~~~~~~~~~~~~

**Problem:** ``ansible-galaxy collection install arillso.system`` fails with "not found"

**Solution:**

.. code-block:: bash

   # Update Galaxy API cache
   ansible-galaxy collection install arillso.system --force

   # Verify Galaxy is accessible
   curl https://galaxy.ansible.com/api/

   # Check your internet connection
   ping galaxy.ansible.com

   # Use specific version
   ansible-galaxy collection install arillso.system:1.0.0

Version Conflicts
~~~~~~~~~~~~~~~~~

**Problem:** Dependency conflicts between collections

**Solution:**

.. code-block:: bash

   # Check installed versions
   ansible-galaxy collection list

   # Remove conflicting collection
   ansible-galaxy collection remove arillso.system

   # Reinstall with specific version
   ansible-galaxy collection install arillso.system:1.0.0

   # Use requirements file for consistency
   cat > requirements.yml <<EOF
   ---
   collections:
     - name: arillso.system
       version: "1.0.0"
     - name: arillso.container
       version: "1.0.0"
   EOF

   ansible-galaxy collection install -r requirements.yml --force

Permission Denied During Install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Permission errors installing collections

**Solution:**

.. code-block:: bash

   # Install to user directory (recommended)
   ansible-galaxy collection install arillso.system --force

   # Collections install to ~/.ansible/collections by default

   # Or specify custom path
   ansible-galaxy collection install arillso.system \
     -p ./collections

   # Then configure ansible.cfg
   cat >> ansible.cfg <<EOF
   [defaults]
   collections_paths = ./collections:~/.ansible/collections
   EOF

.. _ssh-issues:

Connection Issues
-----------------

SSH Connection Failed
~~~~~~~~~~~~~~~~~~~~~

**Problem:** Cannot connect to target hosts

**Diagnosis:**

.. code-block:: bash

   # Test connectivity with ping
   ansible all -i inventory.ini -m ping -vvv

   # Test SSH manually
   ssh -i ~/.ssh/id_rsa user@host -vvv

   # Check SSH config
   ansible all -i inventory.ini -m setup -a "filter=ansible_ssh_*"

**Solutions:**

1. **Verify SSH key:**

   .. code-block:: bash

      # Ensure key is added to ssh-agent
      ssh-add ~/.ssh/id_rsa

      # Test key
      ssh -i ~/.ssh/id_rsa user@host

2. **Check inventory:**

   .. code-block:: ini

      [webservers]
      web1.example.com ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa

3. **Verify host is reachable:**

   .. code-block:: bash

      ping host.example.com
      telnet host.example.com 22

Permission Denied (Publickey)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** SSH authentication fails

**Solution:**

.. code-block:: bash

   # Verify SSH key on remote host
   ssh user@host "cat ~/.ssh/authorized_keys"

   # Copy SSH key to host
   ssh-copy-id -i ~/.ssh/id_rsa.pub user@host

   # Or manually add key
   cat ~/.ssh/id_rsa.pub | ssh user@host \
     "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

   # Check permissions on remote host
   ssh user@host "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"

Sudo Password Required
~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Playbook fails with "sudo: a password is required"

**Solution:**

.. code-block:: bash

   # Method 1: Prompt for password
   ansible-playbook site.yml --ask-become-pass

   # Method 2: Configure passwordless sudo
   ssh user@host "echo '$USER ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/$USER"

   # Method 3: Use ansible_become_password
   ansible-playbook site.yml -e "ansible_become_password=mypassword"

Role & Collection Issues
-------------------------

Role Not Found
~~~~~~~~~~~~~~

**Problem:** ``ERROR! the role 'arillso.system.packages' was not found``

**Diagnosis:**

.. code-block:: bash

   # Check collection is installed
   ansible-galaxy collection list | grep arillso

   # Verify role exists
   ansible-doc -t role arillso.system.packages

**Solutions:**

1. **Install missing collection:**

   .. code-block:: bash

      ansible-galaxy collection install arillso.system

2. **Use FQCN (Fully Qualified Collection Name):**

   .. code-block:: yaml

      # ✅ Correct
      - name: Install packages
        ansible.builtin.include_role:
          name: arillso.system.packages

      # ❌ Wrong
      - name: Install packages
        include_role:
          name: packages

3. **Check ansible.cfg:**

   .. code-block:: ini

      [defaults]
      collections_paths = ~/.ansible/collections:/usr/share/ansible/collections

Module Not Found
~~~~~~~~~~~~~~~~

**Problem:** ``ERROR! couldn't resolve module/action``

**Solution:**

.. code-block:: bash

   # Use FQCN for modules
   # ✅ Correct
   - name: Update apt cache
     ansible.builtin.apt:
       update_cache: yes

   # ❌ Wrong
   - name: Update apt cache
     apt:
       update_cache: yes

Variable Not Defined
~~~~~~~~~~~~~~~~~~~~

**Problem:** ``The task includes an option with an undefined variable``

**Diagnosis:**

.. code-block:: bash

   # Run with extra verbosity
   ansible-playbook site.yml -vvv

   # Check variable precedence
   ansible-playbook site.yml -e "debug=yes" --tags debug

**Solutions:**

1. **Define in defaults:**

   .. code-block:: yaml

      # roles/myrole/defaults/main.yml
      my_variable: "default_value"

2. **Check variable spelling:**

   .. code-block:: yaml

      # Typo in variable name
      # ❌ Wrong
      packages_instal:  # Missing 'l'

      # ✅ Correct
      packages_install:

3. **Use default filter:**

   .. code-block:: yaml

      vars:
        my_value: "{{ undefined_var | default('fallback') }}"

.. _performance-issues:

Performance Issues
------------------

Playbook Runs Slowly
~~~~~~~~~~~~~~~~~~~~

**Problem:** Playbook takes too long to execute

**Solutions:**

1. **Use Mitogen strategy:**

   .. code-block:: ini

      # ansible.cfg
      [defaults]
      strategy = mitogen_linear

      [ssh_connection]
      pipelining = True

2. **Enable pipelining:**

   .. code-block:: ini

      [ssh_connection]
      pipelining = True
      control_path = ~/.ssh/cm-%r@%h:%p

3. **Increase forks:**

   .. code-block:: ini

      [defaults]
      forks = 20

4. **Use fact caching:**

   .. code-block:: ini

      [defaults]
      gathering = smart
      fact_caching = jsonfile
      fact_caching_connection = /tmp/ansible_facts
      fact_caching_timeout = 86400

5. **Disable fact gathering when not needed:**

   .. code-block:: yaml

      ---
      - name: Quick playbook
        hosts: all
        gather_facts: no
        tasks:
          - name: Simple task
            ansible.builtin.command: echo "hello"

High Memory Usage
~~~~~~~~~~~~~~~~~

**Problem:** Ansible uses too much memory

**Solutions:**

.. code-block:: ini

   # ansible.cfg
   [defaults]
   # Reduce number of forks
   forks = 5

   # Disable fact caching if not needed
   gathering = explicit

   # Limit callback output
   stdout_callback = yaml
   bin_ansible_callbacks = False

Collection-Specific Issues
---------------------------

arillso.system Issues
~~~~~~~~~~~~~~~~~~~~~

**Firewall Rules Not Applied**

**Problem:** Firewall rules defined but not active

**Diagnosis:**

.. code-block:: bash

   # Check firewall status
   ansible all -m ansible.builtin.command -a "nft list ruleset"

   # Verify role executed
   ansible-playbook site.yml -vvv --tags firewall

**Solution:**

.. code-block:: yaml

   ---
   - name: Configure firewall
     ansible.builtin.include_role:
       name: arillso.system.firewall
     vars:
       firewall_enabled: true  # Must be explicitly enabled
       firewall_rules:
         - name: "HTTP"
           port: 80
           protocol: tcp
           action: accept

**Packages Not Installing**

**Problem:** Packages fail to install

**Diagnosis:**

.. code-block:: bash

   # Check package manager
   ansible all -m ansible.builtin.shell -a "which apt || which yum || which apk"

   # Update cache first
   ansible all -m ansible.builtin.apt -a "update_cache=yes"

**Solution:**

.. code-block:: yaml

   ---
   - name: Install packages
     ansible.builtin.include_role:
       name: arillso.system.packages
     vars:
       packages_update_cache: true  # Update first
       packages_install:
         - package-name

arillso.container Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**K3s Installation Fails**

**Problem:** K3s fails to install or start

**Diagnosis:**

.. code-block:: bash

   # Check K3s status
   ansible k8s_all -m ansible.builtin.systemd -a "name=k3s state=started"

   # View K3s logs
   ansible k8s_all -m ansible.builtin.shell -a "journalctl -u k3s -n 50"

   # Check system requirements
   ansible k8s_all -m ansible.builtin.shell -a "cat /proc/sys/net/ipv4/ip_forward"

**Solution:**

1. **Enable IP forwarding:**

   .. code-block:: yaml

      - name: Prepare for K3s
        ansible.builtin.include_role:
          name: arillso.system.tuning
        vars:
          tuning_kernel_parameters:
            net.ipv4.ip_forward: 1
            net.bridge.bridge-nf-call-iptables: 1

2. **Check firewall allows K3s:**

   .. code-block:: yaml

      firewall_rules:
        - name: "K3s API"
          port: 6443
          protocol: tcp
          action: accept

**Docker Containers Not Starting**

**Problem:** Docker service fails or containers don't start

**Diagnosis:**

.. code-block:: bash

   # Check Docker service
   ansible docker_hosts -m ansible.builtin.systemd \
     -a "name=docker state=started"

   # View Docker logs
   ansible docker_hosts -m ansible.builtin.shell \
     -a "journalctl -u docker -n 50"

   # Check Docker daemon
   ansible docker_hosts -m ansible.builtin.command \
     -a "docker info"

**Solution:**

.. code-block:: yaml

   ---
   - name: Install Docker
     ansible.builtin.include_role:
       name: arillso.container.docker
     vars:
       docker_edition: "ce"
       docker_daemon_config:
         log-driver: "json-file"
         log-opts:
           max-size: "10m"

arillso.agent Issues
~~~~~~~~~~~~~~~~~~~~

**Grafana Alloy Not Sending Metrics**

**Problem:** Alloy installed but metrics not appearing in Prometheus

**Diagnosis:**

.. code-block:: bash

   # Check Alloy service
   ansible monitoring -m ansible.builtin.systemd \
     -a "name=alloy state=started"

   # View Alloy logs
   ansible monitoring -m ansible.builtin.shell \
     -a "journalctl -u alloy -n 100"

   # Test Prometheus endpoint
   ansible monitoring -m ansible.builtin.uri \
     -a "url=http://localhost:12345/metrics"

**Solution:**

.. code-block:: yaml

   ---
   - name: Deploy Alloy
     ansible.builtin.include_role:
       name: arillso.agent.alloy
     vars:
       alloy_prometheus_enabled: true
       alloy_prometheus_remote_write_url: "http://prometheus.example.com:9090/api/v1/write"

       # Verify endpoint is correct
       alloy_node_exporter_enabled: true

       # Check firewall allows outbound
       # No firewall blocking port 9090

Debugging Techniques
--------------------

Verbose Output
~~~~~~~~~~~~~~

Increase verbosity for debugging:

.. code-block:: bash

   # Level 1: Moderate verbosity
   ansible-playbook site.yml -v

   # Level 2: More detail
   ansible-playbook site.yml -vv

   # Level 3: Debug level (connection info)
   ansible-playbook site.yml -vvv

   # Level 4: SSH debugging
   ansible-playbook site.yml -vvvv

Check Mode (Dry Run)
~~~~~~~~~~~~~~~~~~~~

Test without making changes:

.. code-block:: bash

   # See what would change
   ansible-playbook site.yml --check

   # With diff output
   ansible-playbook site.yml --check --diff

   # Limit to specific hosts
   ansible-playbook site.yml --check --limit web1.example.com

Debug Module
~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Debug variables
     hosts: all
     tasks:
       - name: Show all variables
         ansible.builtin.debug:
           var: hostvars[inventory_hostname]

       - name: Show specific variable
         ansible.builtin.debug:
           var: ansible_distribution

       - name: Conditional debug
         ansible.builtin.debug:
           msg: "This is Ubuntu"
         when: ansible_distribution == "Ubuntu"

Tags for Selective Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   - name: Tagged playbook
     hosts: all
     tasks:
       - name: Install packages
         ansible.builtin.include_role:
           name: arillso.system.packages
         tags:
           - packages
           - install

       - name: Configure firewall
         ansible.builtin.include_role:
           name: arillso.system.firewall
         tags:
           - firewall
           - security

.. code-block:: bash

   # Run only tagged tasks
   ansible-playbook site.yml --tags packages

   # Skip tagged tasks
   ansible-playbook site.yml --skip-tags firewall

   # List available tags
   ansible-playbook site.yml --list-tags

Step-by-Step Execution
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Confirm each task
   ansible-playbook site.yml --step

   # Start at specific task
   ansible-playbook site.yml --start-at-task="Install packages"

Syntax Checking
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check syntax
   ansible-playbook site.yml --syntax-check

   # Lint playbook
   ansible-lint site.yml

   # YAML validation
   yamllint site.yml

Frequently Asked Questions
--------------------------

General Questions
~~~~~~~~~~~~~~~~~

**Q: Which collection should I use for my use case?**

A:

* **System administration** (packages, firewall, users) → ``arillso.system``
* **Containers & Kubernetes** (Docker, K3s, Helm) → ``arillso.container``
* **Monitoring & Observability** (Grafana Alloy, agents) → ``arillso.agent``

**Q: Can I use multiple arillso collections together?**

A: Yes! Collections are designed to work together. See :ref:`examples` for combined usage.

**Q: How do I update to the latest version?**

A:

.. code-block:: bash

   # Update single collection
   ansible-galaxy collection install arillso.system --upgrade

   # Update all via requirements
   ansible-galaxy collection install -r requirements.yml --force

**Q: Are arillso collections production-ready?**

A: Yes. All collections are:

* Battle-tested in production
* Comprehensive CI/CD testing
* Security scanned (CodeQL, Trivy)
* Regularly updated

Installation & Setup
~~~~~~~~~~~~~~~~~~~~

**Q: Where are collections installed?**

A: By default: ``~/.ansible/collections/ansible_collections/``

.. code-block:: bash

   # View installation path
   ansible-galaxy collection list

**Q: Can I install to a custom location?**

A: Yes:

.. code-block:: bash

   ansible-galaxy collection install arillso.system -p ./my_collections

   # Configure in ansible.cfg
   [defaults]
   collections_paths = ./my_collections:~/.ansible/collections

**Q: Do I need to install Ansible separately?**

A: Yes. arillso collections require Ansible >= 2.15:

.. code-block:: bash

   pip install ansible>=2.15

Configuration
~~~~~~~~~~~~~

**Q: How do I override default variables?**

A: Variable precedence (highest to lowest):

1. ``-e`` command line
2. Task vars
3. ``vars_files``
4. Playbook ``vars``
5. Inventory ``host_vars``
6. Inventory ``group_vars``
7. Role ``defaults``

.. code-block:: bash

   # Command line (highest priority)
   ansible-playbook site.yml -e "packages_install=['nginx']"

**Q: Can I use arillso with AWX/Tower?**

A: Yes. Install collections in AWX:

1. Add to ``requirements.yml`` in your project
2. AWX will install automatically
3. Use in playbooks as normal

Performance
~~~~~~~~~~~

**Q: How can I speed up playbook execution?**

A:

1. Use Mitogen strategy
2. Enable SSH pipelining
3. Increase forks
4. Use fact caching
5. Disable fact gathering when not needed

See :ref:`Performance Issues <performance-issues>` above.

**Q: Does arillso work with large inventories?**

A: Yes. Tested with 1000+ hosts. Use:

* Batching with ``serial``
* Dynamic inventory
* Fact caching
* Mitogen for speed

Security
~~~~~~~~

**Q: How do I manage secrets?**

A: Three options:

1. Ansible Vault (encrypted files)
2. Bitwarden (arillso.system.bitwarden_secrets)
3. HashiCorp Vault (with lookup plugin)

See :ref:`security` for details.

**Q: Are container images secure?**

A: Yes:

* Based on Alpine Linux (minimal)
* Non-root user
* Trivy scanned
* SHA-pinned dependencies

**Q: How do I report security issues?**

A: Email security@arillso.io or open a private security advisory on GitHub.

Compatibility
~~~~~~~~~~~~~

**Q: Which Linux distributions are supported?**

A:

* Ubuntu 20.04, 22.04, 24.04
* Debian 11, 12
* RHEL/Rocky/Alma 8, 9
* Alpine Linux (specific roles)

**Q: Does arillso work on ARM?**

A: Yes. Tested on:

* Raspberry Pi (arm64)
* AWS Graviton (arm64)
* Apple Silicon (arm64)

**Q: Can I use with Windows targets?**

A: arillso.system and arillso.agent are Linux-only. Consider:

* WSL2 for Windows hosts
* Linux targets only
* Windows-specific collections

Getting Help
------------

When asking for help, provide:

1. **Ansible version:**

   .. code-block:: bash

      ansible --version

2. **Collection version:**

   .. code-block:: bash

      ansible-galaxy collection list | grep arillso

3. **Error message:**

   .. code-block:: bash

      ansible-playbook site.yml -vvv 2>&1 | tee error.log

4. **Minimal reproduction:**

   Simplify to smallest failing playbook

5. **Environment details:**

   * OS and version
   * Python version
   * Inventory structure

Where to Get Help
~~~~~~~~~~~~~~~~~

* **Documentation:** https://guide.arillso.io
* **GitHub Issues:** https://github.com/arillso/<collection>/issues
* **Discussions:** https://github.com/orgs/arillso/discussions

Error Reference
---------------

Common Error Messages
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Error
     - Solution
   * - ``ERROR! Unexpected Exception``
     - Run with ``-vvv`` for details
   * - ``Permission denied (publickey)``
     - Check SSH keys, see :ref:`SSH Issues <ssh-issues>`
   * - ``sudo: a password is required``
     - Use ``--ask-become-pass`` or configure NOPASSWD
   * - ``Unable to find any of apt, yum, dnf``
     - System not supported or wrong package manager
   * - ``The field 'hosts' is required``
     - Missing ``hosts:`` in playbook
   * - ``Could not match supplied host pattern``
     - Check inventory file and host names

Next Steps
----------

* Review :ref:`quickstart` for getting started
* Check :ref:`examples` for working code
* Read :ref:`security` for hardening
* Explore :ref:`architecture` for design

----

.. raw:: html

   <div class="help-cta">
     <h3>Still Stuck?</h3>
     <p>If you couldn't find a solution above, we're here to help:</p>
     <div class="help-options">
       <a href="https://github.com/orgs/arillso/discussions" target="_blank" class="help-btn">
         <span class="help-icon">💬</span>
         <span class="help-text">
           <strong>Ask the Community</strong>
           <small>Get help from other arillso users</small>
         </span>
       </a>
       <a href="https://github.com/arillso" target="_blank" class="help-btn">
         <span class="help-icon">🐛</span>
         <span class="help-text">
           <strong>Report a Bug</strong>
           <small>Found an issue? Let us know</small>
         </span>
       </a>
       <a href="mailto:hello@arillso.io" class="help-btn">
         <span class="help-icon">✉️</span>
         <span class="help-text">
           <strong>Email Us</strong>
           <small>hello@arillso.io</small>
         </span>
       </a>
     </div>
   </div>

.. seealso::

   * :ref:`quickstart` - Quick Start Guide
   * :ref:`examples` - Complete Examples
   * :ref:`security` - Security Best Practices
   * :ref:`contributing` - Contributing Guidelines
