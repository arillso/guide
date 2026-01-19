:orphan:

.. meta::
  :antsibull-docs: 2.5.0.post0

.. _list_of_containers:

Container Index
================

Production-ready container images for Ansible automation.

.. contents::
   :local:
   :depth: 1

Docker Images
-------------

:ref:`docker.ansible <docker_ansible>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alpine-based Docker container for running Ansible with Mitogen optimization, Kubernetes tools, and multi-platform support.

**Key Features:**

* Mitogen-optimized Ansible (2-7x faster execution)
* Pre-installed Kubernetes tools (kubectl, helm, kustomize)
* Multi-platform support (amd64, arm64)
* Non-root user for enhanced security
* Minimal Alpine Linux base

**Registry:**

* Docker Hub: ``arillso/ansible``
* GitHub Container Registry: ``ghcr.io/arillso/ansible``

**Quick Start:**

.. code-block:: bash

   docker run --rm arillso/ansible ansible-playbook --version

**Repository:** https://github.com/arillso/docker.ansible

.. toctree::
   :maxdepth: 1
   :hidden:

   docker_ansible

.. seealso::

   * :ref:`list_of_collections` - Ansible Collections
   * :ref:`list_of_libraries` - Go Libraries
   * :ref:`list_of_github` - GitHub Actions
