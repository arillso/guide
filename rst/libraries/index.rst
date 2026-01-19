:orphan:

.. meta::
  :antsibull-docs: 2.5.0.post0

.. _list_of_libraries:

Libraries Index
===============

Programming libraries for integrating Ansible automation into applications.

.. contents::
   :local:
   :depth: 1

Go Libraries
------------

:ref:`go.ansible <go_ansible>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go module for programmatically executing Ansible playbooks with Galaxy integration and secure credential management.

**Key Features:**

* Execute Ansible playbooks from Go applications
* Automatic Galaxy role/collection installation
* Secure SSH key and Vault password handling
* Context-based execution with cancellation support
* Comprehensive error handling with wrapped errors

**Installation:**

.. code-block:: bash

   go get github.com/arillso/go.ansible

**Quick Start:**

.. code-block:: go

   pb := ansible.NewPlaybook()
   pb.Config.Playbooks = []string{"site.yml"}
   pb.Config.Inventories = []string{"inventory.yml"}
   err := pb.Exec(context.Background())

**Documentation:** https://pkg.go.dev/github.com/arillso/go.ansible

**Repository:** https://github.com/arillso/go.ansible

.. toctree::
   :maxdepth: 1
   :hidden:

   go_ansible

.. seealso::

   * :ref:`list_of_collections` - Ansible Collections
   * :ref:`list_of_containers` - Container Images
   * :ref:`list_of_github` - GitHub Actions
