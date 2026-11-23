:orphan:

.. meta::
  :antsibull-docs: 2.5.0.post0

.. _list_of_github:

GitHub Actions Index
====================

GitHub Actions maintained by arillso.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Action
     - Release
     - Purpose
   * - :ref:`action.playbook <action_playbook>`
     - ``@ACTION_PLAYBOOK_VERSION@``
     - Runs ``ansible-playbook`` in a Docker container action; installs Galaxy
       requirements, loads SSH keys into ``ssh-agent``, passes Vault passwords
       through a temporary file

.. code-block:: yaml

   - uses: arillso/action.playbook@@ACTION_PLAYBOOK_VERSION@
     with:
       playbook: site.yml
       inventory: inventory.yml
       private_key: ${{ secrets.SSH_PRIVATE_KEY }}

Source: https://github.com/arillso/action.playbook

.. toctree::
   :maxdepth: 1
   :hidden:

   action_playbook

.. seealso::

   * :ref:`list_of_collections` - Ansible Collections
   * :ref:`list_of_containers` - Container Images
   * :ref:`list_of_libraries` - Go Libraries
