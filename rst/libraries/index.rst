:orphan:

.. meta::
  :antsibull-docs: 2.5.0.post0

.. _list_of_libraries:

Go library
==========

Libraries maintained by arillso.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Library
     - Release
     - Purpose
   * - :ref:`go.ansible <go_ansible>`
     - ``@GO_ANSIBLE_VERSION@``
     - Go package that builds and runs ``ansible-galaxy`` and
       ``ansible-playbook`` commands from a ``Config`` struct

.. code-block:: bash

   go get github.com/arillso/go.ansible/v2@@GO_ANSIBLE_VERSION@

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.Playbooks = []string{"site.yml"}
   pb.Config.Inventories = []string{"inventory.yml"}
   err := pb.Exec(context.Background())

Source: https://github.com/arillso/go.ansible ·
API reference: https://pkg.go.dev/github.com/arillso/go.ansible/v2

.. toctree::
   :maxdepth: 1
   :hidden:

   go_ansible

.. seealso::

   * :ref:`list_of_collections` - Ansible Collections
   * :ref:`list_of_containers` - Container Images
   * :ref:`list_of_github` - GitHub Actions
