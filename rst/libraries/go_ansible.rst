.. meta::
  :description: go.ansible: Go package that builds and runs ansible-galaxy and ansible-playbook commands; exported API, configuration fields and example

.. _go_ansible:

go.ansible
==========

Go package ``ansible`` that builds and runs ``ansible-galaxy`` and
``ansible-playbook`` commands from a ``Config`` struct. It calls the Ansible
binaries on ``PATH``; Ansible itself is not part of the module. All facts on this
page come from ``go.mod``, ``ansiblePlaybook.go``, ``example_test.go`` and
``CHANGELOG.md`` in https://github.com/arillso/go.ansible.

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
   * - Module path
     - ``github.com/arillso/go.ansible/v2``
   * - Package name
     - ``ansible``
   * - Latest release
     - ``v2.0.0`` (2026-03-13)
   * - Go version (``go.mod``)
     - ``v2.0.0``: ``go 1.26.1``; ``main``: ``go 1.27.4``
   * - Dependencies
     - none outside the standard library
   * - API reference
     - https://pkg.go.dev/github.com/arillso/go.ansible/v2
   * - License
     - MIT

Installation
------------

.. code-block:: bash

   go get github.com/arillso/go.ansible/v2@v2.0.0

.. code-block:: go

   import ansible "github.com/arillso/go.ansible/v2"

Example
-------

Runs Galaxy requirements and a playbook, logs the masked command lines first and
checks the Ansible exit code. Compiles against ``v2.0.0`` and ``main``.

.. code-block:: go

   package main

   import (
       "context"
       "errors"
       "log"
       "os"
       "time"

       ansible "github.com/arillso/go.ansible/v2"
   )

   func main() {
       ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
       defer cancel()

       pb := ansible.NewPlaybook()
       pb.Config.Playbooks = []string{"site.yml"}
       pb.Config.Inventories = []string{"inventory.yml"}
       pb.Config.GalaxyFile = "requirements.yml"
       pb.Config.ExtraVars = []string{"env=staging"}
       pb.Config.Limit = "web"
       pb.Config.VaultPassword = os.Getenv("VAULT_PASSWORD")

       // Preview the command lines; secrets and extra-vars are masked.
       cmds, err := pb.CommandStrings(ctx)
       if err != nil {
           log.Fatal(err)
       }
       for _, c := range cmds {
           log.Println(c)
       }

       if err := pb.Exec(ctx); err != nil {
           var ae *ansible.AnsibleError
           if errors.As(err, &ae) && ae.ExitCode == ansible.ExitCodeUnreachable {
               log.Fatalf("hosts unreachable: %v", ae)
           }
           log.Fatal(err)
       }
   }

More runnable examples are in ``example_test.go`` and on pkg.go.dev.

Exported API
------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Identifier
     - Description
   * - ``func NewPlaybook() *Playbook``
     - Returns a ``Playbook`` with ``Config.Forks = 5`` and
       ``Config.TempDir = os.TempDir()``.
   * - ``func (p *Playbook) Exec(ctx context.Context) error``
     - Resolves playbooks, writes temporary secret files, runs the commands in
       order and removes the temporary files. Cancelling ``ctx`` stops the
       running process.
   * - ``func (p *Playbook) CommandStrings(ctx context.Context) ([]string, error)``
     - Returns the command lines ``Exec`` would run, without running them and
       without writing temporary files. Values of ``--extra-vars``,
       ``--private-key`` and ``--vault-password-file`` are masked as
       ``******``.
   * - ``type Playbook struct``
     - Fields ``Config Config``, ``Debug bool`` (trace output),
       ``TraceOutput``, ``Stdout``, ``Stderr io.Writer`` (default
       ``os.Stdout``/``os.Stderr``). Not safe for concurrent use.
   * - ``type Config struct``
     - All options, see :ref:`go_ansible_config`.
   * - ``type AnsibleError struct``
     - Returned (wrapped) when an Ansible command exits non-zero. Fields
       ``ExitCode``, ``Command``, ``Message``, ``CommandIndex``,
       ``TotalCommands``, ``Err``; methods ``Error()`` and ``Unwrap()``.
   * - ``ExitCode*`` constants
     - ``ExitCodeSuccess`` 0, ``ExitCodeError`` 1, ``ExitCodeHostFailed`` 2,
       ``ExitCodeUnreachable`` 3, ``ExitCodeParserError`` 4,
       ``ExitCodeUserAbort`` 99, ``ExitCodeUnexpected`` 250

Execution Order
---------------

``Exec`` runs up to four commands:

#. ``ansible --version`` if ``ShowVersion`` is set.
#. ``ansible-galaxy role install`` and ``ansible-galaxy collection install`` if
   ``GalaxyFile`` or ``GalaxyRequirementsFile`` is set. The file must exist.
#. ``ansible-playbook`` with all ``Playbooks`` as positional arguments.

Before that, ``Exec`` checks:

* ``Playbooks`` is not empty. Each entry is a file path, a glob pattern or a
  collection playbook (``namespace.collection.name``); paths and globs must
  match existing files.
* Each ``Inventories`` entry is a readable file, or an inline inventory
  containing a comma (``localhost,``). Without inventories, ``ansible-playbook``
  uses its configured inventory.
* ``PrivateKey`` contains PEM ``BEGIN``/``END`` markers.

``PrivateKey`` and ``VaultPassword`` are written to files with mode ``0600`` in
``TempDir`` (``CRLF`` converted to ``LF``, trailing newline added) and removed
after the run. Errors are wrapped with ``%w``, so
``errors.As`` and ``errors.Is`` (including ``context.DeadlineExceeded``) work.

.. _go_ansible_config:

Config Fields
-------------

Each field's doc comment names the flag or environment variable it sets.
``docs/option-mapping.md`` in the repository groups them by mechanism.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Group
     - Fields
   * - General
     - ``Become``, ``BecomeMethod``, ``BecomeUser``, ``User``, ``PrivateKey``,
       ``PrivateKeyFile``, ``AskBecomePass``, ``AskPass``, ``Check``, ``Diff``,
       ``FlushCache``, ``ForceHandlers``, ``SyntaxCheck``, ``ListHosts``,
       ``ListTags``, ``ListTasks``, ``Step``, ``Connection``, ``Timeout``,
       ``Forks``
   * - SSH
     - ``SSHCommonArgs``, ``SSHExtraArgs``, ``SCPExtraArgs``, ``SFTPExtraArgs``,
       ``SSHTransferMethod``
   * - Playbook
     - ``Inventories []string``, ``Playbooks []string``, ``Limit``,
       ``ExtraVars []string``, ``StartAtTask``, ``Tags``, ``SkipTags``,
       ``ModulePath []string``, ``Verbose`` (1-4, rendered as ``-v`` to
       ``-vvvv``),
       ``NoColor``
   * - Vault
     - ``VaultID``, ``VaultPassword``, ``VaultPasswordFile``, ``AskVaultPass``
   * - Facts
     - ``FactPath``, ``FactCaching``, ``FactCachingTimeout``
   * - Galaxy
     - ``GalaxyFile``, ``GalaxyAPIKey`` (exported as ``ANSIBLE_GALAXY_TOKEN``),
       ``GalaxyAPIServerURL``, ``GalaxyCollectionsPath``,
       ``GalaxyDisableGPGVerify``, ``GalaxyForce``, ``GalaxyForceWithDeps``,
       ``GalaxyNoDeps``, ``GalaxyIgnoreCerts``,
       ``GalaxyIgnoreSignatureStatusCodes``, ``GalaxyKeyring``,
       ``GalaxyOffline``, ``GalaxyPre``, ``GalaxyRequiredValidSignatureCount``,
       ``GalaxyRequirementsFile``, ``GalaxyRolesPath``, ``GalaxySignature``,
       ``GalaxyTimeout``, ``GalaxyUpgrade``
   * - Other
     - ``CallbacksEnabled``, ``PollInterval``, ``StrategyPlugin``,
       ``AnyErrorsFatal``, ``ConfigFile`` (must exist), ``OutputCallback``,
       ``ExtraEnv map[string]string`` (applied last, overrides other
       variables), ``ShowVersion``, ``TempDir``
   * - Deprecated
     - ``GatherSubset``, ``GatherTimeout``, ``MaxFailPercentage``: on ``main``
       ``Exec`` and ``CommandStrings`` return an error when set; set them as
       play keywords

.. note::

   ``main`` contains fixes not yet released in ``v2.0.0`` (``CHANGELOG.md``,
   section *Unreleased*). Among them: ``NoColor``, ``StrategyPlugin``,
   ``CallbacksEnabled``, ``PollInterval``, ``AnyErrorsFatal`` and
   ``SSHTransferMethod`` are passed as ``ANSIBLE_*`` environment variables;
   ``v2.0.0`` passes them as CLI flags that ``ansible-playbook`` rejects.

Development
-----------

.. code-block:: bash

   make test

CI calls reusable workflows from ``arillso/.github``: ``ci-go`` and ``ci-lint``
on pull requests, ``security-code`` and Trivy nightly, release and SBOM on tag push
(``tag.yml``).

.. seealso::

   * :ref:`action.playbook <action_playbook>` - GitHub Action built on this library
   * :ref:`docker.ansible <docker_ansible>` - container image with ``ansible-playbook``
