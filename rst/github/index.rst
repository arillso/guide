:orphan:

.. meta::
  :antsibull-docs: 2.5.0.post0

.. _list_of_github:

GitHub Actions Index
====================

GitHub Actions for Ansible automation in CI/CD pipelines.

.. contents::
   :local:
   :depth: 1

Actions
-------

:ref:`action.playbook <action_playbook>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GitHub Action for running Ansible Playbooks in CI/CD pipelines with comprehensive configuration options.

**Key Features:**

* Automatic SSH key normalization (v1.2.0+)
* Ansible Galaxy integration
* Vault password management via GitHub Secrets
* Privilege escalation support
* Check mode and diff support for safe deployments

**Quick Start:**

.. code-block:: yaml

   - name: Run Ansible Playbook
     uses: arillso/action.playbook@v1.2.0
     with:
       playbook: deploy.yml
       inventory: production.yml
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}

**Marketplace:** https://github.com/marketplace/actions/play-ansible-playbook

**Repository:** https://github.com/arillso/action.playbook

.. toctree::
   :maxdepth: 1
   :hidden:

   action_playbook

.. seealso::

   * :ref:`list_of_collections` - Ansible Collections
   * :ref:`list_of_containers` - Container Images
   * :ref:`list_of_libraries` - Go Libraries
