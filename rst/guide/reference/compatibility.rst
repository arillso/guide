.. meta::
  :description: Ansible, Python and platform requirements of the arillso collections, container image, GitHub Action and Go library
  :keywords: arillso, compatibility, versions, requires_ansible, platforms

.. _compatibility:

Version Compatibility
=====================

Requirements and supported platforms of the arillso components. Every value
on this page is taken from the upstream repository: ``meta/runtime.yml``,
``galaxy.yml`` and ``roles/*/meta/main.yml`` for the collections, the
``Dockerfile`` and workflows for the image, ``action.yml`` for the action and
``go.mod`` for the library.

.. contents::
   :local:
   :depth: 2

Documented Collection Versions
------------------------------

The collection reference in this guide is generated from these releases
(``versions.env`` in the guide repository). Newer releases may exist on
Ansible Galaxy; their requirements can differ.

.. list-table::
   :header-rows: 1
   :widths: 25 15 20 40

   * - Collection
     - Version
     - ``requires_ansible``
     - Collection dependencies (``galaxy.yml``)
   * - :ref:`arillso.system <plugins_in_arillso.system>`
     - 2.0.4
     - ``>=2.18.0``
     - ``ansible.posix >=2.0.0``, ``community.general >=9.0.0``,
       ``community.crypto >=2.0.0``
   * - :ref:`arillso.container <plugins_in_arillso.container>`
     - 2.2.0
     - ``>=2.18.0``
     - ``arillso.system >=1.0.0``, ``community.docker >=3.4.11``
   * - :ref:`arillso.agent <plugins_in_arillso.agent>`
     - 2.1.0
     - ``>=2.18.0``
     - ``arillso.system >=0.0.36``

``ansible-galaxy collection install`` resolves these dependencies
automatically.

Ansible and Python
------------------

* **ansible-core:** all three collections declare ``requires_ansible:
  ">=2.18.0"`` in ``meta/runtime.yml``, and every role sets
  ``min_ansible_version: "2.18"``.
* **CI coverage:** the shared ``ci-ansible-collection.yml`` workflow from
  ``arillso/.github`` runs ``ansible-test sanity`` against ``stable-2.18``,
  ``stable-2.19`` and ``stable-2.20`` (default of its ``ansible_versions``
  input; none of the collections overrides it).
* **Python on the control node:** the collection READMEs state
  ``Python >= 3.12`` for arillso.system and ``Python >= 3.9`` for
  arillso.container. The arillso.agent README states no Python version; it
  requires systemd on the target hosts.

Check the installed versions:

.. code-block:: bash

   ansible --version
   ansible-galaxy collection list | grep -E 'arillso|ansible.posix|community'

Managed Node Platforms
----------------------

Platforms as declared in ``meta/main.yml`` of each role in the documented
release. ``EL`` covers RHEL and its rebuilds. A platform that is not listed
is not declared, not necessarily broken.

arillso.system 2.0.4
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 34 22 22 22

   * - Roles
     - Debian
     - Ubuntu
     - EL
   * - access, bitwarden_secrets, facts, firewall, logging, network, python,
       shell, systemd
     - bullseye, bookworm
     - focal, jammy, noble
     - 8, 9
   * - ansible
     - bullseye, bookworm
     - jammy, noble
     - --
   * - packages
     - buster, bullseye, bookworm
     - bionic, focal, jammy, noble
     - --
   * - ready, thermal
     - bullseye, bookworm
     - focal, jammy, noble
     - --
   * - tuning
     - buster, bullseye
     - focal, jammy
     - all
   * - zram
     - bookworm, trixie
     - jammy, noble
     - --

arillso.container 2.2.0
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 34 22 22 22

   * - Roles
     - Debian
     - Ubuntu
     - EL
   * - docker, docker_compose_v2, docker_login, fleet, helm, k3s, tailscale
     - bullseye, bookworm
     - jammy, noble
     - 9

arillso.agent 2.1.0
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 34 22 22 22

   * - Roles
     - Debian
     - Ubuntu
     - EL
   * - alloy, do
     - bullseye, bookworm
     - focal, jammy, noble
     - 8, 9
   * - tailscale
     - bullseye, bookworm
     - jammy, noble
     - 8, 9

Other Components
----------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Component
     - Versioning
     - Requirements and contents
   * - :ref:`arillso/ansible <docker_ansible>` (container image)
     - Rolling. A push to ``main`` that changes ``Dockerfile`` or
       ``requirements.txt`` publishes ``latest``, ``<ansible-core version>``
       and ``<ansible-core version>-<git sha>`` tags and a GitHub release
       named after the build date.
     - Images for ``linux/amd64`` and ``linux/arm64`` on Docker Hub and
       ``ghcr.io``. Alpine base, runs as UID/GID ``1000:1000``. The
       ansible-core version is pinned in ``requirements.txt``.
   * - :ref:`action.playbook <action_playbook>` (GitHub Action)
     - Semantic version tags without ``v`` prefix (for example ``0.5.0``).
     - Docker action; each release pins its own image
       ``ghcr.io/arillso/action.playbook:<version>``, which is built on a
       pinned ``arillso/ansible`` image.
   * - :ref:`go.ansible <go_ansible>` (Go library)
     - Semantic version tags with ``v`` prefix (for example ``v2.0.0``).
     - Go version from the ``go`` directive in ``go.mod``.

Upgrading
---------

Collections follow semantic versioning; tags carry no ``v`` prefix. Breaking
changes are listed in each collection's ``CHANGELOG.md``:

* `arillso/ansible.system CHANGELOG <https://github.com/arillso/ansible.system/blob/main/CHANGELOG.md>`_
* `arillso/ansible.container CHANGELOG <https://github.com/arillso/ansible.container/blob/main/CHANGELOG.md>`_
* `arillso/ansible.agent CHANGELOG <https://github.com/arillso/ansible.agent/blob/main/CHANGELOG.md>`_

Pin versions in ``requirements.yml`` and raise them deliberately:

.. code-block:: yaml

   ---
   collections:
     - name: arillso.system
       version: "@ARILLSO_SYSTEM_VERSION@"
     - name: arillso.container
       version: "@ARILLSO_CONTAINER_VERSION@"

.. code-block:: bash

   ansible-galaxy collection install -r requirements.yml --upgrade
   ansible-playbook site.yml --check --diff

To let Renovate raise the pins, extend the shared preset from
``arillso/.github``:

.. code-block:: json

   {
     "$schema": "https://docs.renovatebot.com/renovate-schema.json",
     "extends": [
       "github>arillso/.github:renovate-ansible#2026-11-20"
     ]
   }

The ``#<date-tag>`` suffix pins the preset to a fixed revision. Without it
Renovate resolves the preset against the default branch of
``arillso/.github``, so a change there takes effect without a pull request.
A custom manager in the shared ``renovate-base`` preset keeps the tag current
and automerges the bump.

Reporting a Compatibility Problem
---------------------------------

Open an issue in the collection's repository
(`ansible.system <https://github.com/arillso/ansible.system/issues>`_,
`ansible.container <https://github.com/arillso/ansible.container/issues>`_,
`ansible.agent <https://github.com/arillso/ansible.agent/issues>`_) and
include:

.. code-block:: bash

   ansible --version
   ansible-galaxy collection list | grep arillso
   cat /etc/os-release
   python3 --version

.. seealso::

   * :ref:`quickstart` - Quick Start Guide
   * :ref:`troubleshooting` - Troubleshooting
   * :ref:`contributing` - Contributing
