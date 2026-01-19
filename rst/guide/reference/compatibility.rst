.. meta::
  :description: Version compatibility and upgrade guide for arillso
  :keywords: arillso, compatibility, versions, upgrade, migration

.. _compatibility:

Version Compatibility
=====================

Compatibility matrix, version requirements, and upgrade guides for arillso collections and tools.

.. contents::
   :local:
   :depth: 2

Supported Versions
------------------

Current Release Status
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 20 30

   * - Component
     - Current Version
     - Status
     - End of Life
   * - arillso.system
     - 1.0.x
     - Supported
     - TBD
   * - arillso.container
     - 1.0.x
     - Supported
     - TBD
   * - arillso.agent
     - 1.0.x
     - Supported
     - TBD
   * - arillso/ansible (container)
     - latest
     - Supported
     - Rolling
   * - go.ansible (library)
     - 1.x
     - Supported
     - TBD
   * - action.playbook (GitHub Action)
     - 1.2.x
     - Supported
     - TBD

Version Support Policy
~~~~~~~~~~~~~~~~~~~~~~

* **Major versions** (1.0.0 → 2.0.0): Supported for 12 months after next major release
* **Minor versions** (1.0.0 → 1.1.0): Supported for 6 months after next minor release
* **Patch versions** (1.0.0 → 1.0.1): Always upgrade to latest patch
* **Security fixes**: Backported to all supported versions

Requirements
------------

Ansible Requirements
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - arillso Collection
     - Minimum Ansible
     - Recommended Ansible
   * - arillso.system 1.x
     - 2.15.0
     - 2.16.0+
   * - arillso.container 1.x
     - 2.15.0
     - 2.16.0+
   * - arillso.agent 1.x
     - 2.15.0
     - 2.16.0+

**Check your Ansible version:**

.. code-block:: bash

   ansible --version

**Upgrade Ansible:**

.. code-block:: bash

   # Using pip
   pip install --upgrade ansible

   # Using pipx (recommended)
   pipx upgrade ansible

Python Requirements
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Component
     - Minimum Python
     - Recommended Python
   * - Ansible Control Node
     - 3.9
     - 3.11+
   * - Managed Nodes
     - 3.6
     - 3.9+
   * - go.ansible
     - N/A (Go)
     - N/A (Go)

**Check Python version:**

.. code-block:: bash

   # Control node
   python3 --version

   # Managed nodes
   ansible all -m ansible.builtin.command -a "python3 --version"

Operating System Support
------------------------

Control Node (Where Ansible Runs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - OS
     - Status
     - Notes
   * - Ubuntu 20.04, 22.04, 24.04
     - ✅ Supported
     - Recommended
   * - Debian 11, 12
     - ✅ Supported
     -
   * - RHEL/Rocky/Alma 8, 9
     - ✅ Supported
     -
   * - macOS 12+
     - ✅ Supported
     - With Homebrew
   * - Windows 10/11
     - ⚠️ Limited
     - WSL2 only
   * - Alpine Linux
     - ❌ Not Supported
     - Use container image

Managed Nodes (Target Hosts)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**arillso.system**

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - OS
     - Status
     - Notes
   * - Ubuntu 20.04, 22.04, 24.04
     - ✅ Fully Supported
     - Primary platform
   * - Debian 11, 12
     - ✅ Fully Supported
     -
   * - RHEL/Rocky/Alma 8, 9
     - ✅ Fully Supported
     -
   * - Fedora 38+
     - ⚠️ Best Effort
     - Community supported
   * - Alpine Linux
     - ⚠️ Limited
     - Container roles only
   * - Arch Linux
     - ❌ Not Supported
     -
   * - Windows
     - ❌ Not Supported
     - Use arillso.system on Linux

**arillso.container**

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - OS
     - Status
     - Notes
   * - Ubuntu 20.04, 22.04, 24.04
     - ✅ Fully Supported
     -
   * - Debian 11, 12
     - ✅ Fully Supported
     -
   * - RHEL/Rocky/Alma 8, 9
     - ✅ Fully Supported
     -
   * - Alpine Linux
     - ✅ Supported
     - K3s, Docker
   * - Raspberry Pi OS
     - ✅ Supported
     - ARM64

**arillso.agent**

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - OS
     - Status
     - Notes
   * - Ubuntu 20.04, 22.04, 24.04
     - ✅ Fully Supported
     -
   * - Debian 11, 12
     - ✅ Fully Supported
     -
   * - RHEL/Rocky/Alma 8, 9
     - ✅ Fully Supported
     -

Architecture Support
--------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Architecture
     - Support Status
     - Notes
   * - x86_64 (amd64)
     - ✅ Fully Supported
     - Primary
   * - ARM64 (aarch64)
     - ✅ Fully Supported
     - Tested on Pi, Graviton
   * - ARMv7
     - ⚠️ Limited
     - Basic roles only
   * - x86 (32-bit)
     - ❌ Not Supported
     -

Collection Compatibility
------------------------

Inter-Collection Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Collection
     - arillso.system
     - arillso.container
     - arillso.agent
   * - arillso.system
     - 1.x
     - Any
     - Any
   * - arillso.container
     - Any
     - 1.x
     - Any
   * - arillso.agent
     - Any
     - Any
     - 1.x

**All arillso collections are designed to work together seamlessly.**

Community Collections
~~~~~~~~~~~~~~~~~~~~~

arillso collections depend on these community collections:

.. code-block:: yaml

   # Automatically installed as dependencies
   dependencies:
     - ansible.posix (>= 1.5.0)
     - community.general (>= 8.0.0)

**Verify dependencies:**

.. code-block:: bash

   ansible-galaxy collection list

Third-Party Tool Versions
--------------------------

Container Runtimes
~~~~~~~~~~~~~~~~~~

**Docker**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Docker Version
     - arillso.container
     - Notes
   * - 20.10.x
     - ✅ Supported
     - Minimum
   * - 23.0.x
     - ✅ Supported
     -
   * - 24.0.x
     - ✅ Supported
     -
   * - 25.0.x+
     - ✅ Supported
     - Recommended

**Kubernetes (K3s)**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - K3s Version
     - arillso.container
     - Notes
   * - v1.26.x
     - ✅ Supported
     - Minimum
   * - v1.27.x
     - ✅ Supported
     -
   * - v1.28.x
     - ✅ Supported
     - Recommended
   * - v1.29.x+
     - ✅ Supported
     -

**Customize K3s version:**

.. code-block:: yaml

   # In your vars
   # renovate: datasource=github-releases depName=k3s-io/k3s
   k3s_version: "v1.28.0+k3s1"

Monitoring Tools
~~~~~~~~~~~~~~~~

**Grafana Alloy**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Alloy Version
     - arillso.agent
     - Notes
   * - v1.0.x
     - ✅ Supported
     - Latest stable

**Tailscale**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Tailscale Version
     - arillso.agent
     - Notes
   * - Latest stable
     - ✅ Supported
     - Auto-updated

Upgrade Guides
--------------

Upgrading Collections
~~~~~~~~~~~~~~~~~~~~~

**Minor Version Upgrades (1.0.x → 1.1.x)**

Minor upgrades are backward compatible:

.. code-block:: bash

   # Update to latest minor version
   ansible-galaxy collection install arillso.system --upgrade

   # Test with check mode
   ansible-playbook site.yml --check

   # Deploy
   ansible-playbook site.yml

**Major Version Upgrades (1.x → 2.x)**

Major upgrades may include breaking changes:

1. **Review Changelog:**

   .. code-block:: bash

      # View changelog
      ansible-doc-collection arillso.system

      # Or visit GitHub
      curl https://github.com/arillso/ansible.system/blob/main/CHANGELOG.md

2. **Update in test environment first:**

   .. code-block:: bash

      # Test environment
      ansible-galaxy collection install arillso.system:2.0.0 \
        -p ./test-collections

      # Test playbooks
      ansible-playbook -i test-inventory site.yml

3. **Update variable names if needed:**

   .. code-block:: yaml

      # Example breaking change (hypothetical)
      # v1.x
      firewall:  # Old structure
        - table:
            family: inet

      # v2.x (hypothetical)
      firewall_tables:  # New structure
        inet:
          chains: []

4. **Deploy to production:**

   .. code-block:: bash

      ansible-galaxy collection install arillso.system:2.0.0 --force
      ansible-playbook site.yml

Migration Paths
---------------

From Other Collections
~~~~~~~~~~~~~~~~~~~~~~

**From geerlingguy.* roles**

.. code-block:: yaml

   # Before (geerlingguy)
   - hosts: all
     roles:
       - geerlingguy.docker

   # After (arillso)
   - hosts: all
     tasks:
       - name: Install Docker
         ansible.builtin.include_role:
           name: arillso.container.docker

**From ansible.builtin modules**

.. code-block:: yaml

   # Before
   - name: Install packages
     ansible.builtin.package:
       name:
         - nginx
         - htop

   # After (more features)
   - name: Install packages
     ansible.builtin.include_role:
       name: arillso.system.packages
     vars:
       packages_list:
         - name: nginx
           state: present
         - name: htop
           state: present

From Manual Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Converting shell scripts to playbooks:**

.. code-block:: bash

   # Before (shell script)
   #!/bin/bash
   apt-get update
   apt-get install -y nginx
   systemctl enable nginx
   systemctl start nginx

.. code-block:: yaml

   # After (Ansible)
   ---
   - name: Setup web server
     hosts: webservers
     become: true
     tasks:
       - name: Install nginx
         ansible.builtin.include_role:
           name: arillso.system.packages
         vars:
           packages_list:
             - name: nginx
               state: present

Breaking Changes
----------------

Version 1.x Breaking Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**arillso.system 1.0.0**

* Initial release - no breaking changes

**arillso.container 1.0.0**

* Initial release - no breaking changes

**arillso.agent 1.0.0**

* Initial release - no breaking changes

Planned Deprecations
~~~~~~~~~~~~~~~~~~~~

No deprecations planned for 1.x series.

Version Pinning
---------------

Best Practices
~~~~~~~~~~~~~~

**Use version ranges in requirements.yml:**

.. code-block:: yaml

   ---
   collections:
     # Allow patch updates
     - name: arillso.system
       version: ">=1.0.0,<1.1.0"

     # Allow minor updates
     - name: arillso.container
       version: ">=1.0.0,<2.0.0"

     # Pin exact version (not recommended)
     - name: arillso.agent
       version: "1.0.0"

**Renovate auto-updates:**

.. code-block:: json

   {
     "$schema": "https://docs.renovatebot.com/renovate-schema.json",
     "extends": [
       "github>arillso/.github:renovate-ansible"
     ]
   }

Lock Files
~~~~~~~~~~

Create a lock file for reproducibility:

.. code-block:: bash

   # Generate lock file
   ansible-galaxy collection list --format yaml > collections-lock.yml

   # Install from lock file
   ansible-galaxy collection install -r collections-lock.yml

Compatibility Testing
---------------------

Testing Different Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # molecule/default/requirements.yml
   ---
   collections:
     - name: arillso.system
       version: "1.0.0"  # Test specific version

.. code-block:: bash

   # Test with molecule
   molecule test

Matrix Testing
~~~~~~~~~~~~~~

Test multiple versions in CI/CD:

.. code-block:: yaml

   # .github/workflows/test.yml
   strategy:
     matrix:
       ansible:
         - "2.15"
         - "2.16"
       collection:
         - "1.0.0"
         - "latest"

Known Issues
------------

Current Known Issues
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Issue
     - Description
     - Workaround
   * - None
     - No known issues
     - N/A

Version-Specific Issues
~~~~~~~~~~~~~~~~~~~~~~~

Issues are tracked per version in GitHub Issues.

See: https://github.com/arillso/ansible.*/issues

Compatibility Checklist
-----------------------

Before Upgrading
~~~~~~~~~~~~~~~~

✅ **Pre-upgrade checklist:**

* [ ] Review CHANGELOG for breaking changes
* [ ] Test in non-production environment
* [ ] Backup configuration files
* [ ] Update requirements.yml
* [ ] Run playbooks with ``--check`` mode
* [ ] Update CI/CD pipelines
* [ ] Document any custom changes needed
* [ ] Plan rollback procedure

After Upgrading
~~~~~~~~~~~~~~~

✅ **Post-upgrade verification:**

* [ ] Verify collection versions installed
* [ ] Run full playbook in test environment
* [ ] Check all roles function correctly
* [ ] Verify monitoring still works
* [ ] Review logs for errors
* [ ] Test rollback procedure
* [ ] Update documentation
* [ ] Deploy to production

Getting Help
------------

Version-Related Issues
~~~~~~~~~~~~~~~~~~~~~~

If you encounter compatibility issues:

1. **Check compatibility matrix** (this page)
2. **Review CHANGELOG** for breaking changes
3. **Search GitHub Issues** for known problems
4. **Open new issue** with version details

Include in bug reports:

.. code-block:: bash

   # Ansible version
   ansible --version

   # Collection versions
   ansible-galaxy collection list | grep arillso

   # OS details
   cat /etc/os-release

   # Python version
   python3 --version

Release Calendar
----------------

Release Schedule
~~~~~~~~~~~~~~~~

* **Major releases** (x.0.0): Annually
* **Minor releases** (1.x.0): Quarterly
* **Patch releases** (1.0.x): As needed

**Subscribe to releases:**

* GitHub: Watch → Custom → Releases
* RSS: https://github.com/arillso/ansible.*/releases.atom

Next Steps
----------

* Review :ref:`quickstart` for getting started
* Check :ref:`examples` for version-specific examples
* Read :ref:`troubleshooting` for upgrade issues
* Explore :ref:`contributing` for version requirements

.. seealso::

   * :ref:`quickstart` - Quick Start Guide
   * :ref:`troubleshooting` - Troubleshooting Guide
   * :ref:`contributing` - Contributing Guidelines
   * `GitHub Releases <https://github.com/arillso>`_
