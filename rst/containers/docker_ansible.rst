.. meta::
  :description: arillso/ansible container image: ansible-core on Alpine Linux with Kubernetes CLI tools, published for linux/amd64 and linux/arm64

.. _docker_ansible:

docker.ansible
==============

Container image ``arillso/ansible``: ansible-core in a Python virtualenv on
Alpine Linux, with SSH, Kubernetes and helper CLI tools. All facts on this page
come from ``Dockerfile``, ``requirements.txt`` and ``.github/workflows/`` in
https://github.com/arillso/docker.ansible (branch ``main``).

.. contents::
   :local:
   :depth: 2

Image Facts
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property
     - Value
   * - Base image
     - ``alpine:3.24.4`` (pinned by digest)
   * - ansible-core
     - ``2.22.0`` (``requirements.txt``)
   * - Python
     - Alpine package ``python3`` 3.14; Ansible runs from the virtualenv
       ``/pipx/venvs/ansible``, its binaries are linked into ``/pipx/bin``
       (first on ``PATH``)
   * - User
     - ``ansible``, UID/GID ``1000:1000``, home ``/home/ansible``
   * - Working directory
     - ``/home/ansible``; ``/data`` exists and is owned by ``ansible``
   * - Entrypoint
     - ``/sbin/tini --``
   * - Default command
     - ``ansible-playbook --version``
   * - Stop signal
     - ``SIGINT`` (Ansible finishes the running task and prints the recap)
   * - Platforms
     - ``linux/amd64``, ``linux/arm64`` (``platforms`` in ``merge.yml``)
   * - License
     - MIT

Tags and Registries
-------------------

``merge.yml`` pushes every build to Docker Hub (``arillso/ansible``) and GitHub
Container Registry (``ghcr.io/arillso/ansible``) with the same tags:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Tag
     - Meaning
   * - ``latest``
     - Most recent build from ``main``
   * - ``<ansible-core>`` (e.g. ``2.22.0``)
     - ansible-core version from ``requirements.txt``; moves with every rebuild
       of that version
   * - ``<ansible-core>-<short-sha>``
     - Build of one commit
   * - ``<ansible-core>-<full-sha>``
     - Build of one commit, full SHA

A build runs on every push to ``main`` that changes ``Dockerfile`` or
``requirements.txt``. The matching GitHub release and git tag are named after the
build date (``YYYY-MM-DD``, latest: ``2026-11-21``). The ghcr.io image carries a
build provenance attestation; the build also produces an SBOM.

Contents
--------

System Packages
~~~~~~~~~~~~~~~

Installed with ``apk`` in the production stage of the ``Dockerfile``:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Area
     - Packages
   * - Runtime
     - ``python3``, ``bash``, ``tini``
   * - SSH and transfer
     - ``openssh-client-common``, ``openssh-client-default``, ``openssh-keygen``,
       ``sshpass``, ``rsync``
   * - Kubernetes
     - ``kubectl``, ``helm``, ``kustomize``
   * - Utilities
     - ``git``, ``curl``, ``jq``, ``gnupg``, ``openssl``, ``libexpat``

Python Packages
~~~~~~~~~~~~~~~

Installed from ``requirements.txt`` into ``/pipx/venvs/ansible`` (selection, see
the file for exact pins):

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Area
     - Packages
   * - Ansible
     - ``ansible-core``, ``mitogen``, ``jmespath``, ``netaddr``, ``passlib``,
       ``Jinja2``
   * - Connections
     - ``paramiko``, ``pywinrm[credssp]``, ``requests-credssp``
   * - Cloud
     - ``boto3``/``botocore`` (AWS), ``azure-identity``, ``azure-mgmt-compute``,
       ``azure-mgmt-network``, ``google-cloud-compute``, ``google-auth``,
       ``pyvmomi`` (VMware)
   * - Containers
     - ``docker``, ``kubernetes``, ``openshift``
   * - Databases
     - ``psycopg2-binary``, ``PyMySQL``, ``redis``
   * - Other APIs
     - ``python-gitlab``, ``hvac`` (HashiCorp Vault), ``py-consul``,
       ``crowdstrike-falconpy``, ``dnspython``

Built-in Ansible Configuration
------------------------------

The image writes ``/etc/ansible/ansible.cfg`` and ``/etc/ansible/hosts.yml``:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Setting
     - Value
   * - ``inventory``
     - ``/etc/ansible/hosts.yml`` (only ``localhost`` with
       ``ansible_connection: local``)
   * - ``host_key_checking``
     - ``False``; set ``ANSIBLE_HOST_KEY_CHECKING=True`` for persistent hosts
   * - ``strategy_plugins``
     - Path of the Mitogen strategy plugins; the default strategy stays
       ``linear``
   * - ``stdout_callback``
     - ``default``
   * - ``pipelining``
     - ``True``

``ANSIBLE_FORCE_COLOR=True`` is set as environment variable.

Mitogen is installed but not active. Enable it per run with
``ANSIBLE_STRATEGY=mitogen_linear``.

Usage
-----

.. code-block:: bash

   # Print the Ansible version (default command)
   docker run --rm arillso/ansible

   # Run a playbook from the current directory
   docker run --rm -v "$(pwd)":/workspace -w /workspace \
     arillso/ansible ansible-playbook -i inventory.yml playbook.yml

   # Interactive shell
   docker run --rm -it -v "$(pwd)":/workspace -w /workspace \
     arillso/ansible bash

SSH key and host key checking:

.. code-block:: bash

   docker run --rm \
     -e ANSIBLE_HOST_KEY_CHECKING=True \
     -v "$(pwd)":/workspace -w /workspace \
     -v "$HOME/.ssh/id_ed25519":/home/ansible/.ssh/id_ed25519:ro \
     arillso/ansible ansible-playbook -i inventory.yml playbook.yml

Vault password from a file:

.. code-block:: bash

   docker run --rm \
     -v "$(pwd)":/workspace -w /workspace \
     -v "$(pwd)/.vault_pass":/home/ansible/.vault_pass:ro \
     arillso/ansible ansible-playbook \
       --vault-password-file /home/ansible/.vault_pass playbook.yml

With Mitogen:

.. code-block:: bash

   docker run --rm -e ANSIBLE_STRATEGY=mitogen_linear \
     -v "$(pwd)":/workspace -w /workspace \
     arillso/ansible ansible-playbook -i inventory.yml playbook.yml

Files written to a bind mount belong to UID 1000. To write as the calling user,
add ``--user "$(id -u):$(id -g)"``.

Extending the Image
-------------------

``/pipx`` belongs to ``root``; ``pip`` on ``PATH`` is the virtualenv's pip.
Switch to ``root`` for the install and back to ``1000:1000`` afterwards:

.. code-block:: dockerfile

   FROM arillso/ansible:@ARILLSO_ANSIBLE_IMAGE_VERSION@
   USER root
   RUN pip install --no-cache-dir <package>
   USER 1000:1000

Building from Source
--------------------

.. code-block:: bash

   git clone https://github.com/arillso/docker.ansible
   cd docker.ansible
   make ansible-build        # build the image
   make test-quick           # basic checks
   make comprehensive-test   # all test suites under tests/

``docker build -t arillso/ansible:local .`` works without ``make``. The builder
stage resolves Alpine packages through the ``pkg.arillso.io`` proxy.

CI
--

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Workflow
     - Content
   * - ``pull-request.yml``
     - Lint, hadolint, image build, container structure tests, secret scan,
       dependency review
   * - ``merge.yml``
     - Build and push for ``linux/amd64`` and ``linux/arm64``, GitHub release
   * - ``nightly-security.yml``
     - Daily at 02:00 UTC: CodeQL, Trivy scan (``CRITICAL``, ``HIGH``), secret
       scan

.. seealso::

   * :ref:`action.playbook <action_playbook>` - GitHub Action built on this image
   * :ref:`go.ansible <go_ansible>` - Go library for running ``ansible-playbook``
   * :ref:`list_of_collections` - Ansible Collections
