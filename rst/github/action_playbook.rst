.. meta::
  :description: GitHub Action for running Ansible Playbooks with comprehensive configuration options

.. _action_playbook:

action.playbook
===============

GitHub Action for running Ansible Playbooks with advanced configuration support for Galaxy, SSH, Vault, and privilege escalation.

.. contents::
   :local:
   :depth: 2

Overview
--------

``action.playbook`` is a Docker-based GitHub Action that executes Ansible playbooks in CI/CD pipelines with extensive configuration options and automatic credential handling.

**Repository:** https://github.com/arillso/action.playbook

**GitHub Marketplace:** https://github.com/marketplace/actions/play-ansible-playbook

**Latest Version:** v1.2.0+

Features
--------

Ansible Galaxy Support
~~~~~~~~~~~~~~~~~~~~~~

* Automatic role and collection installation
* Custom Galaxy server configuration
* Offline mode support
* GPG signature verification
* Dependency management

SSH Authentication
~~~~~~~~~~~~~~~~~~

* Automatic SSH key normalization (v1.2.0+)
* CRLF → LF conversion
* Trailing newline handling
* Format validation (RSA, OpenSSH, EC, DSA)
* Bastion host support via ProxyCommand

Vault Integration
~~~~~~~~~~~~~~~~~

* Multiple vault identity support
* Secure password handling via GitHub Secrets
* Vault file management

Comprehensive Options
~~~~~~~~~~~~~~~~~~~~~

* All ansible-playbook flags supported
* Privilege escalation (sudo, become)
* Check mode (dry-run)
* Diff mode
* Tag filtering
* Host limiting
* Verbosity control

Quick Start
-----------

Basic Usage
~~~~~~~~~~~

.. code-block:: yaml

   name: Deploy Application
   on: [push]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Run Ansible Playbook
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: deploy.yml
             inventory: inventory.yml
           env:
             ANSIBLE_HOST_KEY_CHECKING: 'false'

With SSH Key
~~~~~~~~~~~~

.. code-block:: yaml

   - name: Deploy with SSH
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: deploy.yml
       inventory: production.yml
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}
     env:
       ANSIBLE_HOST_KEY_CHECKING: 'false'

With Galaxy Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   - name: Deploy with Galaxy Roles
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: site.yml
       inventory: hosts.yml
       galaxy_file: requirements.yml
     env:
       ANSIBLE_HOST_KEY_CHECKING: 'false'

Input Parameters
----------------

Required Inputs
~~~~~~~~~~~~~~~

**playbook** (required)
  List of playbooks to execute.

  .. code-block:: yaml

     playbook: deploy.yml

  Multiple playbooks:

  .. code-block:: yaml

     playbook: |
       prepare.yml
       deploy.yml
       verify.yml

**inventory** (required)
  One or more inventory files or inline inventory.

  .. code-block:: yaml

     inventory: production.yml

  Multiple inventories:

  .. code-block:: yaml

     inventory: |
       group_vars/
       production.yml

  Inline inventory:

  .. code-block:: yaml

     inventory: |
       [webservers]
       web1.example.com
       web2.example.com

Galaxy Options
~~~~~~~~~~~~~~

**galaxy_file**
  Path to Galaxy requirements file (``requirements.yml``).

**galaxy_force**
  Force reinstallation of roles/collections.

  .. code-block:: yaml

     galaxy_force: 'true'

**galaxy_api_key**
  API key for Ansible Galaxy authentication.

  .. code-block:: yaml

     galaxy_api_key: ${{ secrets.GALAXY_API_KEY }}

**galaxy_api_server_url**
  Custom Galaxy server URL.

**galaxy_collections_path**
  Path to collections directory.

**galaxy_disable_gpg_verify**
  Disable GPG signature verification.

**galaxy_ignore_certs**
  Ignore SSL certificate validation.

**galaxy_offline**
  Enable offline mode (no Galaxy requests).

**galaxy_timeout**
  Galaxy operation timeout in seconds.

SSH Authentication
~~~~~~~~~~~~~~~~~~

**private_key**
  SSH private key content (stored in GitHub Secrets).

  .. code-block:: yaml

     private_key: ${{ secrets.SSH_PRIVATE_KEY }}

  .. note::
     Starting with v1.2.0, SSH keys are automatically normalized:

     * Line endings converted (CRLF → LF)
     * Trailing newlines added if missing
     * Format validated

**user**
  SSH connection username.

  .. code-block:: yaml

     user: deploy

**ssh_common_args**
  Common arguments for all SSH connections.

  .. code-block:: yaml

     ssh_common_args: '-o StrictHostKeyChecking=no'

**ssh_extra_args**
  Extra arguments for SSH only.

**scp_extra_args**
  Extra arguments for SCP only.

**sftp_extra_args**
  Extra arguments for SFTP only.

Execution Control
~~~~~~~~~~~~~~~~~

**limit**
  Limit execution to specific hosts.

  .. code-block:: yaml

     limit: 'webservers'

**tags**
  Only run tasks with specific tags.

  .. code-block:: yaml

     tags: 'deploy,configure'

**skip_tags**
  Skip tasks with specific tags.

  .. code-block:: yaml

     skip_tags: 'debug,testing'

**start_at_task**
  Start execution at specific task.

  .. code-block:: yaml

     start_at_task: 'Deploy Application'

**extra_vars**
  Set additional variables (key=value format).

  .. code-block:: yaml

     extra_vars: |
       version=1.2.3
       environment=production

**check**
  Run in check mode (dry-run, no changes).

  .. code-block:: yaml

     check: 'true'

**diff**
  Show differences when changing files.

  .. code-block:: yaml

     diff: 'true'

Vault Options
~~~~~~~~~~~~~

**vault_id**
  Vault identity to use.

  .. code-block:: yaml

     vault_id: 'production@vault'

**vault_password**
  Vault password (stored in GitHub Secrets).

  .. code-block:: yaml

     vault_password: ${{ secrets.VAULT_PASSWORD }}

Privilege Escalation
~~~~~~~~~~~~~~~~~~~~~

**become**
  Enable privilege escalation.

  .. code-block:: yaml

     become: 'true'

**become_method**
  Escalation method (sudo, su, etc.).

  .. code-block:: yaml

     become_method: 'sudo'

**become_user**
  User to escalate to.

  .. code-block:: yaml

     become_user: 'root'

Advanced Options
~~~~~~~~~~~~~~~~

**verbose**
  Verbosity level (0-4).

  .. code-block:: yaml

     verbose: 2

**forks**
  Number of parallel processes.

  .. code-block:: yaml

     forks: 10

**syntax_check**
  Only perform syntax check.

  .. code-block:: yaml

     syntax_check: 'true'

**list_hosts**
  Only list matching hosts.

**list_tasks**
  Only list tasks that would execute.

**list_tags**
  List all available tags.

**flush_cache**
  Clear fact cache.

**force_handlers**
  Run handlers even if tasks fail.

Complete Examples
-----------------

Production Deployment
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Production Deployment

   on:
     push:
       branches: [main]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       environment: production

       steps:
         - uses: actions/checkout@v4

         - name: Deploy to Production
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: site.yml
             inventory: production.yml
             galaxy_file: requirements.yml
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             vault_password: ${{ secrets.VAULT_PASSWORD }}
             extra_vars: |
               version=${{ github.sha }}
               environment=production
             become: 'true'
             diff: 'true'
           env:
             ANSIBLE_HOST_KEY_CHECKING: 'false'

Staging with Check Mode
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Staging Check

   on:
     pull_request:
       branches: [main]

   jobs:
     check:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - name: Check Staging Changes
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: deploy.yml
             inventory: staging.yml
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             check: 'true'
             diff: 'true'
             verbose: 2
           env:
             ANSIBLE_HOST_KEY_CHECKING: 'false'

Multi-Environment Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Multi-Environment Deploy

   on:
     workflow_dispatch:
       inputs:
         environment:
           description: 'Environment to deploy'
           required: true
           type: choice
           options:
             - development
             - staging
             - production

   jobs:
     deploy:
       runs-on: ubuntu-latest
       environment: ${{ github.event.inputs.environment }}

       steps:
         - uses: actions/checkout@v4

         - name: Deploy to ${{ github.event.inputs.environment }}
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: site.yml
             inventory: ${{ github.event.inputs.environment }}.yml
             galaxy_file: requirements.yml
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             extra_vars: |
               environment=${{ github.event.inputs.environment }}
               version=${{ github.sha }}
             become: 'true'
           env:
             ANSIBLE_HOST_KEY_CHECKING: 'false'

Kubernetes Deployment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: Deploy to Kubernetes

   on:
     push:
       tags: ['v*']

   jobs:
     deploy:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - name: Deploy to K8s
           uses: arillso/action.playbook@v1.2.0
           with:
             playbook: k8s-deploy.yml
             inventory: localhost,
             galaxy_file: requirements.yml
             extra_vars: |
               k8s_context=production
               app_version=${{ github.ref_name }}
               namespace=default
           env:
             ANSIBLE_HOST_KEY_CHECKING: 'false'
             K8S_AUTH_KUBECONFIG: ${{ secrets.KUBECONFIG }}

SSH Key Management
------------------

Storing SSH Keys in GitHub Secrets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: ``SSH_PRIVATE_KEY``
4. Value: Paste your complete private key including headers

   .. code-block:: text

      -----BEGIN RSA PRIVATE KEY-----
      MIIEpAIBAAKCAQEA...
      ...
      -----END RSA PRIVATE KEY-----

5. Click **Add secret**

.. warning::
   NEVER commit private SSH keys to your repository!

Automatic Normalization (v1.2.0+)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The action automatically handles:

* **Line Endings:** Windows (CRLF) → Unix (LF)
* **Trailing Newlines:** Added if missing
* **Format Validation:** Verifies PEM format

Supported key formats:

* RSA (``-----BEGIN RSA PRIVATE KEY-----``)
* OpenSSH (``-----BEGIN OPENSSH PRIVATE KEY-----``)
* EC (``-----BEGIN EC PRIVATE KEY-----``)
* DSA (``-----BEGIN DSA PRIVATE KEY-----``)

Bastion Host / ProxyCommand
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For bastion hosts (versions < 1.2.0 or edge cases):

.. code-block:: yaml

   - name: Setup SSH Key
     run: |
       mkdir -p ~/.ssh
       echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
       chmod 600 ~/.ssh/deploy_key

   - name: Deploy via Bastion
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: deploy.yml
       inventory: production.yml
       ssh_common_args: '-o ProxyCommand="ssh -W %h:%p bastion.example.com"'
       extra_vars: ansible_ssh_private_key_file=~/.ssh/deploy_key

Troubleshooting
---------------

SSH Connection Issues
~~~~~~~~~~~~~~~~~~~~~

Enable verbose SSH debugging:

.. code-block:: yaml

   - name: Debug SSH
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: debug.yml
       inventory: hosts.yml
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}
       verbose: 4
       ssh_common_args: '-vvv'

Galaxy Installation Fails
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use force reinstall:

.. code-block:: yaml

   - name: Force Galaxy Install
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: site.yml
       inventory: hosts.yml
       galaxy_file: requirements.yml
       galaxy_force: 'true'

Permission Denied Errors
~~~~~~~~~~~~~~~~~~~~~~~~~

Check SSH key permissions and format:

.. code-block:: yaml

   - name: Verify SSH Key
     run: |
       echo "${{ secrets.SSH_PRIVATE_KEY }}" | head -1
       echo "${{ secrets.SSH_PRIVATE_KEY }}" | tail -1

Expected output:

.. code-block:: text

   -----BEGIN RSA PRIVATE KEY-----
   -----END RSA PRIVATE KEY-----

Environment Variables
---------------------

Common Ansible environment variables:

.. code-block:: yaml

   env:
     # Disable host key checking (use with caution)
     ANSIBLE_HOST_KEY_CHECKING: 'false'

     # Disable deprecation warnings
     ANSIBLE_DEPRECATION_WARNINGS: 'false'

     # Set callback plugin
     ANSIBLE_STDOUT_CALLBACK: 'yaml'

     # Configure retry files
     ANSIBLE_RETRY_FILES_ENABLED: 'false'

     # Set fact gathering
     ANSIBLE_GATHERING: 'smart'

Container Image
---------------

The action uses the ``arillso/ansible`` container image.

**Registry:** ghcr.io/arillso/action.playbook

**Features:**

* Mitogen-optimized Ansible
* Pre-installed Kubernetes tools
* Multi-platform support (amd64, arm64)

See :ref:`docker.ansible <docker_ansible>` for container details.

Best Practices
--------------

Security
~~~~~~~~

1. **Always use GitHub Secrets for credentials**

   .. code-block:: yaml

      # Good
      private_key: ${{ secrets.SSH_PRIVATE_KEY }}

      # Bad - NEVER do this
      private_key: '-----BEGIN RSA PRIVATE KEY-----...'

2. **Use environment-specific secrets**

   .. code-block:: yaml

      environment: production
      steps:
        - uses: arillso/action.playbook@v1.2.0
          with:
            private_key: ${{ secrets.PRODUCTION_SSH_KEY }}

3. **Enable manual approval for production**

   .. code-block:: yaml

      environment:
        name: production
        url: https://example.com

Testing
~~~~~~~

1. **Use check mode in pull requests**

   .. code-block:: yaml

      on: pull_request
      steps:
        - uses: arillso/action.playbook@v1.2.0
          with:
            check: 'true'
            diff: 'true'

2. **Run syntax checks first**

   .. code-block:: yaml

      - name: Syntax Check
        uses: arillso/action.playbook@v1.2.0
        with:
          playbook: site.yml
          inventory: hosts.yml
          syntax_check: 'true'

Performance
~~~~~~~~~~~

1. **Increase forks for large inventories**

   .. code-block:: yaml

      forks: 20

2. **Use fact caching**

   .. code-block:: yaml

      env:
        ANSIBLE_GATHERING: 'smart'
        ANSIBLE_FACT_CACHING: 'jsonfile'

CI/CD Integration
-----------------

The project includes automated workflows:

* **CI** - Linting with golangci-lint
* **Testing** - Comprehensive test playbooks
* **Release** - Automated Docker image publishing
* **Security** - CodeQL and Trivy scanning

License
-------

MIT License - Copyright (c) 2020-2026, arillso

.. seealso::

   * :ref:`docker.ansible <docker_ansible>` - Container image used by this action
   * :ref:`go.ansible <go_ansible>` - Go library with similar functionality
   * GitHub Marketplace: https://github.com/marketplace/actions/play-ansible-playbook
