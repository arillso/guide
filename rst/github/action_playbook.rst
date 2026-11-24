.. meta::
  :description: arillso/action.playbook: Docker-based GitHub Action that runs ansible-playbook; inputs, outputs and behaviour from action.yml and main.go

.. _action_playbook:

action.playbook
===============

Docker-based GitHub Action that runs ``ansible-playbook``. It is a Go program
(``main.go``) on top of :ref:`go.ansible <go_ansible>`, packaged in an image
derived from :ref:`arillso/ansible <docker_ansible>`. All facts on this page come
from ``action.yml``, ``main.go``, ``Dockerfile`` and ``CHANGELOG.md`` in
https://github.com/arillso/action.playbook.

.. contents::
   :local:
   :depth: 2

Facts
-----

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property
     - Value
   * - Action name
     - ``Play Ansible Playbook``
   * - Latest release
     - ``@ACTION_PLAYBOOK_VERSION@``; tags have no ``v`` prefix
   * - Runner
     - ``docker``, image ``ghcr.io/arillso/action.playbook:@ACTION_PLAYBOOK_VERSION@``
   * - Image base
     - ``arillso/ansible`` (``0.5.0``: ``2.20.3``; ``main``: ``2.22.0``); the
       ``ansible`` user is moved to UID/GID ``1001``
   * - Image platforms
     - ``linux/amd64``, ``linux/arm64`` (``tag.yml``)
   * - Go library
     - ``github.com/arillso/go.ansible/v2`` ``v2.0.0``
   * - License
     - MIT

Usage
-----

.. code-block:: yaml

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4

         - name: Run playbook
           id: ansible
           uses: arillso/action.playbook@@ACTION_PLAYBOOK_VERSION@
           with:
             playbook: site.yml
             inventory: inventory.yml
             private_key: ${{ secrets.SSH_PRIVATE_KEY }}
             known_hosts: ${{ secrets.SSH_KNOWN_HOSTS }}
             vault_password: ${{ secrets.VAULT_PASSWORD }}

         - run: echo "status=${{ steps.ansible.outputs.status }} exit=${{ steps.ansible.outputs.exit_code }}"

Check mode for pull requests:

.. code-block:: yaml

   - uses: arillso/action.playbook@@ACTION_PLAYBOOK_VERSION@
     with:
       playbook: site.yml
       inventory: inventory.yml
       dry_run: 'true'          # --check --diff
       output_file: ansible.log # keep stdout and stderr for a PR comment

Inputs
------

Exactly as declared in ``action.yml`` on ``main``. Inputs marked *Unreleased*
were added after ``0.5.0`` and are not available with ``@0.5.0``.

.. list-table::
   :header-rows: 1
   :widths: 24 8 8 60

   * - Name
     - Required
     - Default
     - Description
   * - ``execution_timeout``
     - no
     - ``30``
     - Timeout in minutes for the playbook execution (1-1440, default: 30).
   * - ``retries``
     - no
     - ``0``
     - Number of times to retry on failure (0-100, 0 = no retries, default: 0).
   * - ``retry_delay``
     - no
     - ``30``
     - Delay in seconds between retries (0-3600, default: 30).
   * - ``galaxy_file``
     - no
     -
     - Name of the galaxy file in your workspace.
   * - ``galaxy_force``
     - no
     -
     - Forces the reinstallation of roles or collections from the Galaxy file.
   * - ``galaxy_api_key``
     - no
     -
     - Sets the API key used for authenticating to Ansible Galaxy.
   * - ``galaxy_api_server_url``
     - no
     -
     - Defines the URL of the Ansible Galaxy API server to interact with.
   * - ``galaxy_collections_path``
     - no
     -
     - Sets the path to the directory where Galaxy collections are stored.
   * - ``galaxy_disable_gpg_verify``
     - no
     -
     - Disables GPG signature verification for Ansible Galaxy operations.
   * - ``galaxy_force_with_deps``
     - no
     -
     - Forces the installation of collections with their dependencies from Galaxy.
   * - ``galaxy_ignore_certs``
     - no
     -
     - Ignores SSL certificate validation for Ansible Galaxy requests.
   * - ``galaxy_ignore_signature_status_codes``
     - no
     -
     - Lists HTTP status codes to ignore during Galaxy signature validation.
   * - ``galaxy_keyring``
     - no
     -
     - Specifies the path to the GPG keyring used with Ansible Galaxy.
   * - ``galaxy_offline``
     - no
     -
     - Enables offline mode, preventing any requests to Ansible Galaxy.
   * - ``galaxy_pre``
     - no
     -
     - Allows the installation of pre-release versions from Ansible Galaxy.
   * - ``galaxy_required_valid_signature_count``
     - no
     -
     - Sets the required number of valid GPG signatures for Galaxy content.
   * - ``galaxy_requirements_file``
     - no
     -
     - Defines the path to the Ansible Galaxy requirements file.
   * - ``galaxy_signature``
     - no
     -
     - Specifies a specific GPG signature to verify for Galaxy content.
   * - ``galaxy_timeout``
     - no
     -
     - Sets the timeout in seconds for Ansible Galaxy operations.
   * - ``galaxy_upgrade``
     - no
     -
     - Enables automatic upgrading of Galaxy collections to the latest version.
   * - ``galaxy_no_deps``
     - no
     -
     - Disables automatic resolution of dependencies in Ansible Galaxy.
   * - ``inventory``
     - yes
     -
     - One or more inventory host files. Supports comma-separated ('inv1.yml,inv2.yml') or multiline YAML syntax.
   * - ``playbook``
     - yes
     -
     - One or more playbooks to apply. Supports comma-separated ('play1.yml,play2.yml') or multiline YAML syntax.
   * - ``limit``
     - no
     -
     - Limits the playbook execution to a specific group of hosts.
   * - ``skip_tags``
     - no
     -
     - Only run plays and tasks whose tags do not match these values.
   * - ``start_at_task``
     - no
     -
     - Start the playbook at the task matching this name.
   * - ``tags``
     - no
     -
     - Executes only tasks and plays with specified tags.
   * - ``extra_vars``
     - no
     -
     - Additional variables in key=value format. Supports comma-separated or multiline YAML syntax for multiple values.
   * - ``module_path``
     - no
     -
     - Prepend directories to the module library path. Supports comma-separated or multiline YAML syntax for multiple paths.
   * - ``lint``
     - no
     - ``false``
     - Run ansible-lint on playbooks before execution.
   * - ``output_file``
     - no
     -
     - Save Ansible stdout to a file (useful for capturing diff output for PR comments).
   * - ``check``
     - no
     -
     - Executes a dry run, showing what changes would be made without making them.
   * - ``diff``
     - no
     -
     - Shows the differences in files and templates when changing them.
   * - ``dry_run``
     - no
     - ``false``
     - Enables both check and diff mode for a dry run without making changes.
   * - ``flush_cache``
     - no
     -
     - Clears the fact cache for every host in the inventory.
   * - ``force_handlers``
     - no
     -
     - Runs all handlers even if a task fails.
   * - ``list_hosts``
     - no
     -
     - Outputs a list of matching hosts.
   * - ``list_tags``
     - no
     -
     - List all available tags.
   * - ``list_tasks``
     - no
     -
     - List all tasks that would be executed.
   * - ``syntax_check``
     - no
     -
     - Performs a syntax check on the playbook, without executing it.
   * - ``forks``
     - no
     -
     - Defines the number of parallel processes to use during playbook execution (1-1000, default: 5).
   * - ``vault_id``
     - no
     -
     - Specifies the identity to use when accessing an Ansible Vault.
   * - ``vault_password``
     - no
     -
     - Sets the password to use for decrypting an Ansible Vault.
   * - ``verbose``
     - no
     -
     - Sets the verbosity level, ranging from 0 (minimal output) to 4 (maximum verbosity).
   * - ``private_key``
     - no
     -
     - Specifies the SSH private key content for connections. The key is loaded into ssh-agent, making it available to ProxyCommand and bastion host connections. Should be stored in a GitHub Secret.
   * - ``private_key_passphrase``
     - no
     -
     - Passphrase for the SSH private key. If provided, the passphrase is used to unlock the key when adding it to ssh-agent. Should be stored in a GitHub Secret.
   * - ``additional_private_keys``
     - no
     -
     - Additional SSH private keys to load into ssh-agent. Supports multiline YAML syntax for multiple keys. Requires private_key to be set.
   * - ``user``
     - no
     -
     - Defines the username for making connections.
   * - ``connection``
     - no
     -
     - Sets the type of connection to use (e.g., SSH).
   * - ``timeout``
     - no
     -
     - Overrides the default connection timeout in seconds.
   * - ``ssh_common_args``
     - no
     -
     - Specifies common arguments to pass to all SSH-based connection methods (SSH, SCP, SFTP).
   * - ``sftp_extra_args``
     - no
     -
     - Provides extra arguments to pass only to SFTP.
   * - ``scp_extra_args``
     - no
     -
     - Provides extra arguments to pass only to SCP.
   * - ``ssh_extra_args``
     - no
     -
     - Provides extra arguments to pass only to SSH.
   * - ``known_hosts``
     - no
     -
     - SSH known hosts entries for host key verification. Supports multiline YAML syntax.
   * - ``become``
     - no
     -
     - Enables privilege escalation, allowing operations to run as another user.
   * - ``become_method``
     - no
     -
     - Specifies the method to use for privilege escalation (e.g., sudo).
   * - ``become_user``
     - no
     -
     - Sets the user to impersonate when using privilege escalation.
   * - ``config_file``
     - no
     -
     - Path to an ansible.cfg configuration file to use (sets ANSIBLE_CONFIG). *Unreleased (not in 0.5.0).*
   * - ``no_color``
     - no
     -
     - Disables colorized output. *Unreleased (not in 0.5.0).*
   * - ``output_callback``
     - no
     -
     - Sets the stdout callback plugin for Ansible output (e.g. 'yaml', 'json', 'minimal'). *Unreleased (not in 0.5.0).*
   * - ``callbacks_enabled``
     - no
     -
     - Comma-separated list of enabled callback plugins (e.g. 'profile_tasks,timer'). *Unreleased (not in 0.5.0).*
   * - ``strategy_plugin``
     - no
     -
     - Specifies the strategy plugin to use (e.g. 'linear', 'free', 'mitogen_linear'). *Unreleased (not in 0.5.0).*
   * - ``gather_subset``
     - no
     -
     - Limits the scope of gathered facts (e.g. '!all,!min,network'). *Unreleased (not in 0.5.0).*
   * - ``gather_timeout``
     - no
     -
     - Timeout in seconds for gathering facts (0-3600, 0 = ansible default). *Unreleased (not in 0.5.0).*
   * - ``fact_path``
     - no
     -
     - Path to local fact files loaded as host facts. *Unreleased (not in 0.5.0).*
   * - ``fact_caching``
     - no
     -
     - Caching method to use for facts (e.g. 'jsonfile', 'redis', 'memory'). *Unreleased (not in 0.5.0).*
   * - ``fact_caching_timeout``
     - no
     -
     - Timeout in seconds for the fact cache (0 = no expiry). *Unreleased (not in 0.5.0).*
   * - ``poll_interval``
     - no
     -
     - Interval in seconds for polling async tasks (0-3600, 0 = ansible default). *Unreleased (not in 0.5.0).*
   * - ``max_fail_percentage``
     - no
     -
     - Maximum percentage of hosts that can fail before the playbook aborts (0-100). *Unreleased (not in 0.5.0).*
   * - ``any_errors_fatal``
     - no
     -
     - Treats any task error as fatal, aborting the whole play. *Unreleased (not in 0.5.0).*
   * - ``ssh_transfer_method``
     - no
     -
     - Method for file transfer over SSH (e.g. 'scp' or 'sftp'). *Unreleased (not in 0.5.0).*
   * - ``vault_password_file``
     - no
     -
     - Path to a file containing the vault password (alternative to vault_password). *Unreleased (not in 0.5.0).*
   * - ``private_key_file``
     - no
     -
     - Path to a file containing the SSH private key (alternative to private_key). *Unreleased (not in 0.5.0).*
   * - ``temp_dir``
     - no
     -
     - Directory for Ansible temporary files. *Unreleased (not in 0.5.0).*

.. note::

   ``main.go`` reads ``galaxy_file`` and ``galaxy_force`` from the action input.
   All other ``galaxy_*`` inputs are read only from environment variables named
   ``ANSIBLE_GALAXY_<NAME>`` (for example ``ANSIBLE_GALAXY_API_KEY``); a value
   given under ``with:`` does not reach them. Set them under ``env:`` instead.
   This applies to ``0.5.0`` and ``main``.

Outputs
-------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Name
     - Description
   * - ``status``
     - ``success`` or ``failed``
   * - ``exit_code``
     - Exit code of the failed Ansible command, taken from
       ``ansible.AnsibleError``; ``1`` for errors outside Ansible (for example
       a missing playbook file); ``0`` on success

The exit code values follow the ``ExitCode*`` constants of
:ref:`go.ansible <go_ansible>`: ``2`` host failed, ``3`` unreachable, ``4``
parser error, ``99`` user abort, ``250`` unexpected error.

Behaviour
---------

Taken from ``run()`` in ``main.go``:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Topic
     - Behaviour
   * - Lists
     - ``playbook``, ``inventory``, ``extra_vars`` and ``module_path`` accept
       comma-separated or multiline values.
   * - File checks
     - Every ``inventory`` and ``playbook`` entry and the Galaxy file must exist
       in the workspace; inline inventories such as ``localhost,`` are rejected.
   * - Galaxy file
     - Without ``galaxy_file``, ``requirements.yml`` or ``requirements.yaml`` in
       the workspace root is used if present. Roles and collections are then
       installed before the playbook runs.
   * - SSH key
     - ``private_key`` gets ``CRLF`` converted to ``LF`` and a trailing newline,
       then is loaded into a new ``ssh-agent`` (unlocked with
       ``private_key_passphrase`` if set). ``SSH_AUTH_SOCK`` is passed to
       Ansible, so ``ProxyCommand`` and bastion hops can use the key.
       ``additional_private_keys`` go into the same agent and are ignored
       without ``private_key``.
   * - Known hosts
     - ``known_hosts`` is appended to ``~/.ssh/known_hosts``.
   * - Vault
     - ``vault_password`` is written to a temporary file with mode ``0600`` and
       passed as ``--vault-password-file``; the file is removed afterwards.
   * - Dry run
     - ``dry_run: 'true'`` sets both ``check`` and ``diff``.
   * - Timeout and retries
     - The whole run is cancelled after ``execution_timeout`` minutes. On
       failure it is repeated ``retries`` times, ``retry_delay`` seconds apart.
   * - Lint
     - ``lint: 'true'`` runs ``ansible-lint`` on the playbooks first. The action
       image does not install ``ansible-lint``, so the step fails with
       ``ansible-lint is not installed``.
   * - Numeric inputs
     - Out-of-range values abort the run, e.g. ``forks`` 1-1000, ``verbose``
       0-4, ``timeout`` 0-3600.
   * - Environment
     - Every input can also be set as ``ANSIBLE_<INPUT_NAME>`` under ``env:``.
   * - Step summary
     - Playbooks, status and duration are written to
       ``$GITHUB_STEP_SUMMARY``.

Release Process
---------------

Pushing a tag runs ``tag.yml``: it checks that the image tag in ``action.yml``
matches the release version, builds and pushes
``ghcr.io/arillso/action.playbook`` for ``linux/amd64`` and ``linux/arm64``, and
creates the GitHub release.

.. seealso::

   * :ref:`docker.ansible <docker_ansible>` - base image of the action image
   * :ref:`go.ansible <go_ansible>` - library that builds and runs the Ansible commands
