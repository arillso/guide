.. meta::
  :description: Alpine-based Docker container for running Ansible with Mitogen optimization

.. _docker_ansible:

docker.ansible
==============

Alpine-based Docker container for running Ansible with Mitogen optimization, Kubernetes tools, and multi-platform support.

.. contents::
   :local:
   :depth: 2

Overview
--------

``docker.ansible`` is a production-ready Docker container that provides a complete Ansible execution environment with performance optimizations and additional tooling for cloud-native workflows.

**Repository:** https://github.com/arillso/docker.ansible

**Docker Registries:**

* Docker Hub: ``arillso/ansible``
* GitHub Container Registry: ``ghcr.io/arillso/ansible``

Features
--------

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

* **Mitogen enabled by default** - 2-7x faster execution compared to standard Ansible
* Optimized Alpine Linux base for minimal image size
* Multi-platform support (amd64, arm64)

Kubernetes Integration
~~~~~~~~~~~~~~~~~~~~~~

Pre-installed Kubernetes tools:

* ``kubectl`` - Kubernetes command-line tool
* ``helm`` - Kubernetes package manager
* ``kustomize`` - Kubernetes native configuration management

Security
~~~~~~~~

* Non-root user ``ansible`` (UID/GID 1000)
* Minimal attack surface with Alpine Linux
* Regular security scanning with Trivy

Quick Start
-----------

Basic Usage
~~~~~~~~~~~

Check Ansible version:

.. code-block:: bash

   docker run --rm arillso/ansible ansible-playbook --version

Run a playbook:

.. code-block:: bash

   docker run --rm -v $(pwd):/workspace -w /workspace \
     arillso/ansible ansible-playbook playbook.yml

Interactive shell:

.. code-block:: bash

   docker run --rm -it -v $(pwd):/workspace -w /workspace \
     arillso/ansible bash

With Inventory
~~~~~~~~~~~~~~

.. code-block:: bash

   docker run --rm \
     -v $(pwd):/workspace \
     -w /workspace \
     arillso/ansible ansible-playbook \
     -i inventory.yml \
     playbook.yml

Using Mitogen
~~~~~~~~~~~~~

Mitogen is enabled by default through the ``ansible.cfg`` configuration:

.. code-block:: ini

   [defaults]
   strategy_plugins = /usr/lib/python3.11/site-packages/ansible_mitogen/plugins/strategy
   strategy = mitogen_linear

Docker Compose Example
----------------------

.. code-block:: yaml

   version: '3.8'
   services:
     ansible:
       image: arillso/ansible:latest
       volumes:
         - ./:/workspace
       working_dir: /workspace
       command: ansible-playbook -i inventory.yml site.yml

GitHub Actions Example
----------------------

.. code-block:: yaml

   name: Deploy with Ansible
   on: [push]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       container:
         image: arillso/ansible:latest
       steps:
         - uses: actions/checkout@v4
         - name: Run Ansible playbook
           run: ansible-playbook -i inventory.yml playbook.yml

Building from Source
--------------------

Requirements
~~~~~~~~~~~~

* Docker with BuildKit support
* Make (optional, for convenience)

Build Commands
~~~~~~~~~~~~~~

Using Make:

.. code-block:: bash

   make ansible-build       # Build container
   make test-quick          # Quick validation
   make comprehensive-test  # Full test suite
   make release-check       # Pre-release validation

Using Docker directly:

.. code-block:: bash

   docker build -t arillso/ansible:local .

Multi-platform Build
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   docker buildx build \
     --platform linux/amd64,linux/arm64 \
     -t arillso/ansible:latest \
     --push .

Version Management
------------------

The container uses version ranges for Alpine packages to balance stability and security:

.. code-block:: dockerfile

   # Example: Python with version constraint
   RUN apk add --no-cache \
       python3>=3.11.0 \
       python3<4.0.0

This approach:

* Allows security patches within the same minor version
* Prevents breaking changes from major version updates
* Maintains reproducible builds

Testing
-------

The project includes comprehensive testing:

Unit Tests
~~~~~~~~~~

Basic functionality validation:

.. code-block:: bash

   make test-quick

Integration Tests
~~~~~~~~~~~~~~~~~

Real-world playbook execution:

.. code-block:: bash

   make comprehensive-test

Security Scanning
~~~~~~~~~~~~~~~~~

Trivy vulnerability scanning is performed in CI/CD pipeline:

.. code-block:: bash

   trivy image arillso/ansible:latest

Performance Tests
~~~~~~~~~~~~~~~~~

Mitogen performance validation comparing execution times with and without optimization.

CI/CD Pipeline
--------------

Automated workflows in ``.github/workflows/``:

* **Build and Test** - Multi-platform builds with comprehensive testing
* **Security Scanning** - Trivy vulnerability scans
* **Release** - Automated publishing to Docker Hub and GitHub Container Registry

Environment Variables
---------------------

Common Ansible environment variables:

.. code-block:: bash

   docker run --rm \
     -e ANSIBLE_HOST_KEY_CHECKING=False \
     -e ANSIBLE_STDOUT_CALLBACK=yaml \
     -v $(pwd):/workspace \
     -w /workspace \
     arillso/ansible ansible-playbook playbook.yml

Troubleshooting
---------------

Permission Issues
~~~~~~~~~~~~~~~~~

The container runs as user ``ansible`` (UID 1000). If you encounter permission issues:

.. code-block:: bash

   # Run as current user
   docker run --rm --user $(id -u):$(id -g) \
     -v $(pwd):/workspace -w /workspace \
     arillso/ansible ansible-playbook playbook.yml

Mitogen Issues
~~~~~~~~~~~~~~

To disable Mitogen and use standard Ansible:

.. code-block:: bash

   docker run --rm \
     -e ANSIBLE_STRATEGY=linear \
     -v $(pwd):/workspace -w /workspace \
     arillso/ansible ansible-playbook playbook.yml

Python Dependencies
~~~~~~~~~~~~~~~~~~~

Install additional Python packages:

.. code-block:: dockerfile

   FROM arillso/ansible:latest
   RUN pip install --no-cache-dir netaddr jmespath

License
-------

MIT License - Copyright (c) 2024-2026, arillso

.. seealso::

   * :ref:`action.playbook <action_playbook>` - GitHub Action using this container
   * :ref:`go.ansible <go_ansible>` - Go library for Ansible execution
   * :ref:`list_of_collections` - Ansible Collections
