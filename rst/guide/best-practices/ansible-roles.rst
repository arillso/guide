.. meta::
  :description: Design rules for building maintainable Ansible roles and collections
  :keywords: ansible, roles, collections, argument_specs, molecule, idempotence, semver

.. _ansible-roles:

Ansible Role & Collection Design
================================

How to build an Ansible role and a collection so they stay reusable, testable, and
maintainable over years. These patterns come from production collections, not from theory.

Where this fits: :ref:`standards` defines *which files* a repository must contain,
:ref:`contributing` defines *how to submit* changes. This page defines *how a role is
built internally*.

.. contents::
   :local:
   :depth: 2

Part 1 - The Role
-----------------

The Guiding Principle
~~~~~~~~~~~~~~~~~~~~~

A role is a **function with a contract**, not a section of a script.

Three questions must be answerable without opening ``tasks/main.yml``:

1. **What does it do?** - one responsibility, in one sentence
2. **How do you call it?** - which variables, which types, which are required
3. **What does it depend on?** - collections, other roles, platforms

If any of these can only be answered by reading code, the role is not yet a role.

Directory Structure - The Minimum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   roles/<name>/
   ├── defaults/main.yml          # overridable inputs, all commented
   ├── vars/main.yml              # internal constants (high precedence, not inputs)
   ├── meta/main.yml              # galaxy_info, platforms, dependencies, collections
   ├── meta/argument_specs.yml    # the machine-readable contract
   ├── tasks/main.yml             # dispatcher, not implementation
   ├── tasks/<topic>.yml          # the actual work, split by responsibility
   ├── handlers/main.yml          # prefixed handler names
   ├── templates/                 # path mirrors target filesystem: etc/default/foo.j2
   ├── files/
   └── README.md                  # variable table + example invocation

.. warning::
   ``meta/main.yml`` and ``meta/argument_specs.yml`` are **two different files** with two
   different purposes. ``main.yml`` describes the role for Galaxy and declares
   dependencies. ``argument_specs.yml`` validates inputs at runtime. Both are required.

Roles that support multiple distributions add OS-specific variable files under ``vars/``
(``Debian.yml``, ``RedHat.yml``) loaded via ``include_vars`` keyed on
``ansible_os_family``. These are per-platform constants - package names, paths, service
names - not inputs. The high precedence of ``vars/`` is deliberate here: a caller should
not be able to override them by accident.

Rule 1 - Prefix Everything
~~~~~~~~~~~~~~~~~~~~~~~~~~

Ansible has **one global variable namespace**. There is no per-role scoping. Two roles
that both define ``port`` overwrite each other depending on call order - a bug that only
surfaces in production and takes hours to find.

Therefore: **every variable a role defines or reads starts with the role name.**

.. code-block:: yaml

   # defaults/main.yml of role `zram`
   zram_enabled: true
   zram_percent: 50
   zram_algorithm: zstd

The only exceptions are Ansible's own facts (``ansible_*``), loop variables, and
``inventory_hostname``.

**The most common violation:** a role reads a variable the caller set somewhere in the
playbook without the role declaring it as an input. The role is then no longer callable
on its own - it only works inside that one playbook.

Naming conventions within the prefix:

* Booleans: ``*_enabled``, ``*_required``
* Lists: plural names, ``alloy_custom_exporters``
* Dicts: singular names, ``alloy_node_exporter_config``
* Descriptive over short: ``alloy_prometheus_enabled``, not ``alloy_prom``

Rule 2 - Defaults Explain the Why
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``defaults/main.yml`` is documentation, not just value assignment. A default without a
rationale is a value nobody dares to change later, because nobody knows why it is what
it is.

.. code-block:: yaml

   # zram_percent: percentage of physical RAM used as a zram swap device.
   # Default 50 means: a 16 GB host gets an 8 GB zram device. At typical
   # zstd compression ratios on text workloads (~3x) that yields roughly
   # 24 GB of effectively usable memory.
   zram_percent: 50

Three lines of comment save the archaeology in two years.

Every Variable Lives in Three Places
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **``defaults/main.yml``** - the value, with the rationale comment above
2. **``meta/argument_specs.yml``** - type, ``required``, ``choices``, ``description`` (Rule 3)
3. **``README.md``** - variable table plus a runnable example

The three are not duplication: ``defaults`` answers *which value*, ``argument_specs``
*which shape is valid*, the README *how do I call this*. Without the README a caller has
to read ``argument_specs`` - machine-readable is not the same as human-friendly.

Rule 3 - ``argument_specs`` Is the Contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``meta/argument_specs.yml`` validates inputs **at the role entry point**, before the first
task runs. Without it a typo in a variable name fails somewhere deep in the third task
with an unreadable Jinja error - or worse, does not fail at all and the role silently does
the wrong thing.

.. code-block:: yaml

   ---
   argument_specs:
       main:
           short_description: "Configures compressed RAM swap (zram)"
           description:
               - "Installs zram-tools and the kernel module"
               - "Validates the compression algorithm against kernel capabilities"
           options:
               zram_percent:
                   description:
                       - "Percentage of physical RAM used as a zram swap device"
                       - "50 means: a 16 GB host gets 8 GB of zram"
                   type: "int"
                   required: false
                   default: 50
               zram_algorithm:
                   description: "Kernel compression algorithm"
                   type: "str"
                   required: false
                   default: "zstd"
                   choices:
                       - "zstd"
                       - "lz4"
                       - "lzo"

What this buys:

* **Type checking** - ``type: int`` catches the string ``"50"`` coming from an environment variable
* **``choices``** - constrains to valid values instead of misconfiguring at runtime
* **Self-documentation** - ``ansible-doc`` and documentation generators read it directly
* **``assert`` tasks become unnecessary** - validation belongs at the entry point, not in the task list

.. note::
   Every ``description`` is prose for humans, not a restatement of the variable name.
   ``description: "The zram percentage"`` is worthless. Write down what the value does and
   how to recognise the right one.

.. warning::
   Roles without ``argument_specs.yml`` will be rejected in review.

Rule 4 - ``<role>_enabled`` as Master Switch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every role gets a switch that turns it into a complete no-op:

.. code-block:: yaml

   # defaults/main.yml
   zram_enabled: true

.. code-block:: yaml

   # tasks/main.yml
   - name: Bootstrap zram kernel module
     ansible.builtin.include_tasks: bootstrap.yml
     when: zram_enabled

Why this is more than convenience: it allows a role to be disabled **in the inventory**
per host group without touching the playbook. One playbook listing all roles, plus group
variables switching them on and off per environment - that scales. Playbook variants per
environment do not.

Rule 5 - ``tasks/main.yml`` Is a Dispatcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once a role has more than roughly 50 lines of tasks, ``main.yml`` becomes a distribution
point:

.. code-block:: yaml

   ---
   - name: Bootstrap kernel module
     ansible.builtin.include_tasks: bootstrap.yml
     when: zram_enabled

   - name: Validate configuration against kernel capabilities
     ansible.builtin.include_tasks: validate.yml
     when:
         - zram_enabled
         - not ansible_check_mode

   - name: Deploy configuration
     ansible.builtin.include_tasks: configure.yml
     when: zram_enabled

The split criterion is **responsibility**, not line count. A complex package role
decomposes sensibly into ``keys.yml``, ``repositories.yml``, ``install.yml``,
``remove.yml``, ``hold.yml``, ``cache.yml``, ``upgrade.yml`` - each file one question you
can answer on its own.

**Helper convention:** task files with a ``_`` prefix (``_keys_normalise.yml``,
``_key_apply.yml``) are role-internal subroutines, not meant to be called from outside.

``import_tasks`` vs. ``include_tasks``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 37 38

   * - Aspect
     - ``import_tasks`` (static)
     - ``include_tasks`` (dynamic)
   * - Evaluated
     - parse time
     - runtime
   * - ``when``
     - copied onto **every** imported task individually
     - applies to the include as a whole
   * - Loop over it
     - not possible
     - possible
   * - Filename from a variable
     - not possible
     - possible
   * - ``--list-tasks``
     - visible
     - invisible until execution

Rule of thumb: **``import_tasks`` when the structure is fixed**, ``include_tasks`` when the
decision is only made at runtime or a loop is needed. The ``when`` difference is the most
common source of error - with ``import_tasks`` and an expensive condition, that condition
is evaluated N times.

Rule 6 - Composition, but Only for Real Substance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A role can call another role instead of copying its logic. This is a strong lever - and
at the same time the rule most often overstretched.

.. danger::
   **Repetition is not automatically duplication.** Extracting every line that appears
   more than once into a role trades a little typing for permanent coupling - and produces
   wrapper roles that do nothing but pass parameters through. That is worse than the
   repetition.

The Test: What Is Inside the Called Role?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A separate role is worth it when **non-trivial logic** sits behind the facade, logic you
would otherwise carry everywhere:

* **OS and distribution differences** - ``apt`` vs. ``dnf`` vs. ``zypper``, Debian package
  names vs. Ubuntu, paths and service names per platform
* **Non-obvious pitfalls** - dearmoring GPG keys, replacing deprecated ``apt_key`` with
  keyring files, repository signatures, cache invalidation
* **State logic** - hold/unhold, unattended upgrades, idempotence special cases, retry behaviour
* **A maintained interface** - the role normalises different input shapes into one flow

As a rough scale: a package role covering all of that quickly reaches several hundred
lines across a dozen task files. **That** justifies calling it from ten other roles.

The argument is the error surface, not the saved lines: eight nearly identical task
definitions, one per combination of source type and keyring, mean every change has to be
carried to all eight places and one dearmor regression has to be fixed in four.

How It Looks
^^^^^^^^^^^^

.. code-block:: yaml

   - name: Install zram tools package via packages role
     ansible.builtin.include_role:
         name: arillso.system.packages
         tasks_from: packages
     vars:
         packages_list: >-
             {{ zram_packages
                | map('community.general.dict_kv', 'name')
                | map('combine', {'state': 'present'})
                | list }}

The ``zram`` role installs no packages itself. It **delegates** to the role that knows
package management including all distribution quirks. ``tasks_from`` calls a specific
entry point instead of the whole role - that turns roles into libraries with several
public functions.

When to Leave It Alone
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Situation
     - Do not extract - instead
   * - Four lines of connection parameters in several roles
     - ``module_defaults`` with ``action_groups`` in the playbook (see Part 3)
   * - The same Jinja expression in two places
     - A filter in the collection's ``plugins/filter/``, or simply leave it
   * - Two roles need the same constant
     - ``vars/`` of the collection role or ``group_vars``, no wrapper role
   * - The new role would only forward parameters
     - Call the module directly - an indirection layer without own value costs more than it saves
   * - Two similar blocks that will foreseeably diverge
     - Keep them separate; premature unification breeds parameter sprawl

The Price of Coupling
^^^^^^^^^^^^^^^^^^^^^

Every ``include_role`` onto a foreign role is a **dependency with a contract**:

* If the called role changes its interface, all callers break - it therefore belongs in
  ``meta/main.yml`` under ``dependencies`` or ``collections``, and into the SemVer
  consideration
* The error message originates in foreign code; debugging moves one level deeper
* Molecule has to resolve the called role too - test setup becomes more involved

That is a good trade for several hundred lines of package logic. For four lines it is not.

Rule 7 - Use ``set_fact`` Sparingly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``set_fact`` writes into **host state** and outlives the role. A role that sets and reads
intermediate values via ``set_fact`` across several task files is no longer a module, it
is a procedure with global variables.

Better, in this order:

1. **Default with Jinja** - derived values belong in ``defaults/``, they are evaluated lazily:

   .. code-block:: yaml

      zram_kernel_module_package: >-
          {{ 'linux-modules-extra-' ~ ansible_kernel
             if ansible_distribution == 'Ubuntu' else '' }}

2. **``vars:`` on the task or block** - limited visibility instead of host state
3. **``set_fact`` only** when a value is genuinely needed across play boundaries or after
   a ``register``

As orientation: a healthy collection gets by with a handful of ``set_fact`` across a dozen
roles.

Rule 8 - Namespace Your Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handlers live in the **play-wide** namespace, not the role namespace. Two roles with
``restart service`` collide.

.. code-block:: yaml

   # handlers/main.yml
   - name: "zram: restart zramswap"
     ansible.builtin.systemd_service:
         name: zramswap
         state: restarted

.. code-block:: yaml

   notify: "zram: restart zramswap"

Further handler rules:

* **``notify`` only on real change** - the task must report an honest ``changed``, otherwise
  the handler never fires or always fires
* **``meta: flush_handlers``** set deliberately when a restart must happen *before* the next
  step instead of at the end of the play
* **A dead handler is a bug** - a handler nobody notifies, or a variable nobody reads,
  should be deleted, not kept

Rule 9 - Idempotence Is Not Negotiable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Second run = zero changes. That is Ansible's core promise; without it, it is a shell script
with YAML syntax.

The usual violations:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Pattern
     - Problem
     - Remedy
   * - ``command``/``shell`` without ``changed_when``
     - always reports ``changed``
     - ``changed_when: false`` for pure reads, otherwise tie it to the return value
   * - ``command`` without ``creates``/``removes``
     - runs every time
     - set ``creates:``, or ``stat`` first and use ``when``
   * - ``shell`` where ``command`` suffices
     - unnecessary shell injection surface
     - ``shell`` only for pipe, redirect, glob, ``&&``
   * - ``lineinfile`` for structured files
     - breaks on format change
     - ``template`` with the complete file
   * - Timestamp in a template
     - every run reports ``changed``
     - remove the timestamp or move it to a separate file

**Think about check mode:** tasks that cannot run meaningfully under ``--check`` (because
they read state a previous task would have created) get ``when: not ansible_check_mode`` -
with a comment explaining why.

Rule 10 - ``no_log`` on Secrets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every task handling a password, a token, or a license key gets ``no_log: true``. Without
it the value lands in cleartext in the log, in the CI artifact, and in the callback plugin.

.. code-block:: yaml

   - name: Get secret from Bitwarden
     ansible.builtin.command:
         cmd: bws secret get "{{ app_secret_id }}"
     register: app_secret
     changed_when: false
     no_log: true

This applies to ``argument_specs`` as well: an option carrying a secret gets ``no_log: true``
there too - otherwise the value appears on a validation error.

.. code-block:: yaml

   options:
       app_api_token:
           description: "API token used to authenticate against the upstream service"
           type: "str"
           required: true
           no_log: true

Rule 11 - FQCN Everywhere
~~~~~~~~~~~~~~~~~~~~~~~~~

``ansible.builtin.copy``, not ``copy``. ``ansible.builtin.runas``, not ``runas``. Short
names are resolved through a search order that changes with installed collections - the
same code does different things on two machines.

This applies to ``become_method`` and to filters from collections
(``community.general.dict_kv``) as well.

.. code-block:: yaml

   # Good
   - name: Create configuration directory
     ansible.builtin.file:
         path: /etc/app
         state: directory
         mode: "0755"

   # Bad
   - name: create dir
     file: path=/etc/app state=directory

Part 2 - The Collection
-----------------------

The Collection Is the Standard Unit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. important::
   **The standalone role as a distribution format is legacy.** Anyone building a role today
   that is used beyond its own repository builds a collection - even if it contains exactly
   one role.

The reasons are not taste but the state of the ecosystem:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Aspect
     - Standalone role
     - Role in a collection
   * - Namespace
     - none - ``nginx`` collides with every other ``nginx`` on the role path
     - ``namespace.name.role``, unambiguous
   * - Versioning
     - Git tag without resolution
     - SemVer artifact, resolved by ``ansible-galaxy``
   * - Dependencies
     - only ``requirements.yml`` at repo level, no version resolution
     - ``dependencies`` in ``galaxy.yml`` with ranges
   * - Delivery
     - Git checkout
     - buildable ``.tar.gz``, storable in artifact repositories
   * - Shipping plugins
     - not supported
     - ``plugins/`` - modules, filters, lookups
   * - Tooling
     - limited
     - ``meta/runtime.yml``, ``action_groups``, antsibull docs, ``extensions/molecule/``

On top of that: the ``ansible`` package consists exclusively of collections, and Galaxy
treats standalone roles only as legacy compatibility.

**The cost is low.** A collection around a single role costs three things: ``galaxy.yml``,
``meta/runtime.yml``, and one directory level. In return you get namespace, versioning, and
tooling. And the practical point: **a role rarely stays alone.** Starting with the
collection means nothing has to be rebuilt when the second role arrives.

**The remaining exception:** a role that lives **exclusively in its own playbook repository**
and is never consumed from outside may sit there under ``roles/``. That is project
structure, not a distribution format - the role rules from Part 1 still apply unchanged.
The boundary is clear: **as soon as a second repository needs the role, it becomes a
collection.**

Structure
~~~~~~~~~

.. code-block:: text

   <namespace>.<name>/
   ├── galaxy.yml                 # metadata, dependencies, version
   ├── meta/runtime.yml           # requires_ansible, action_groups, redirects
   ├── roles/
   ├── plugins/
   │   ├── modules/
   │   ├── filter/
   │   ├── lookup/
   │   └── module_utils/
   ├── extensions/molecule/       # one scenario per role
   ├── tests/unit/                # pytest for plugins
   ├── CHANGELOG.md
   ├── README.md
   ├── LICENSE
   └── Makefile                   # lint, test, build as named targets

.. note::
   Molecule scenarios live under ``extensions/molecule/<role>/``. This is the layout
   scaffolded by ``ansible-creator`` and documented by the Molecule collection testing
   guide. The ``extensions/`` directory itself is part of the official collection
   structure; ``molecule/`` inside it is a testing-tool convention rather than part of the
   collection specification.

``galaxy.yml`` - The Dependency Contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   namespace: arillso
   name: system
   version: 1.1.6
   readme: README.md
   authors:
       - Simon Baerlocher (@sbaerlocher) <s.baerlocher@sbaerlocher.ch>
   license:
       - MIT
   dependencies:
       ansible.posix: ">=2.0.0"
       community.general: ">=9.0.0"
       community.crypto: ">=2.0.0"
   repository: https://github.com/arillso/ansible.system
   documentation: https://guide.arillso.io/collections/arillso/system/index.html
   issues: https://github.com/arillso/ansible.system/issues

**Lower bounds, not upper bounds.** ``">=9.0.0"`` states what the collection needs. An
upper bound (``"<10"``) blocks consumers on every major release and is only justified for
a known incompatibility.

``meta/runtime.yml``
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   ---
   requires_ansible: ">=2.18.0"

   action_groups:
       arillso_agent:
           - arillso.agent.alloy
           - arillso.agent.do
           - arillso.agent.tailscale

This file also holds:

* **``action_groups``** - named module groups for ``module_defaults``, so a playbook sets
  credentials once instead of per task
* **``plugin_routing``** - redirects for renames, so old calls keep working; the way to
  rename something without a breaking change

Take SemVer Seriously
~~~~~~~~~~~~~~~~~~~~~

A collection is a public API. Breaking is anything that forces callers to follow:

* Variable renamed or removed
* Default changed such that behaviour changes
* Role renamed or removed
* Required parameter added
* Module return value restructured

That means a **major bump plus migration instructions in the changelog** - not just the
statement that something changed, but the concrete step for the consumer.

Mitigating path: keep the old variable alive for one minor version via ``plugin_routing``
or a compatibility default, with a deprecation notice.

Test Pyramid
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 35 15

   * - Level
     - Tool
     - Checks
     - Cost
   * - Static
     - ``ansible-lint`` (profile ``production``), ``yamllint``
     - idioms, FQCN, idempotence traps
     - seconds
   * - Syntax
     - ``ansible-playbook --syntax-check``
     - parseability, roles resolvable
     - seconds
   * - Unit
     - ``pytest``
     - own modules, filters, lookups
     - seconds
   * - Integration
     - ``molecule`` (container or VM)
     - converge + **idempotence** + verify
     - minutes

.. tip::
   **The single most valuable test is ``idempotence`` in the Molecule sequence.** It runs
   the role twice and fails if the second run changes anything. No static linter finds that.

Molecule Scenario
~~~~~~~~~~~~~~~~~

One scenario per role, under ``extensions/molecule/<role>/``:

.. code-block:: yaml

   scenario:
       test_sequence:
           - dependency
           - cleanup
           - destroy
           - syntax
           - create
           - prepare
           - converge
           - idempotence
           - verify
           - cleanup
           - destroy

**Choose the driver to fit:** containers suffice for roles that manage files and packages.
Roles needing a real kernel (kernel modules, swap, network stack) run under a VM driver -
otherwise you are testing behaviour that does not exist in production.

Where neither is available, a reduced sequence is acceptable **only with a comment stating
why**. A role touching ``/sys/block`` and calling ``swapon`` cannot converge in a container:

.. code-block:: yaml

   ---
   # zram loads the zram kernel module, slurps /sys/block/zram0/comp_algorithm
   # and calls swapon -p. Containers have no own kernel, /sys/block is
   # read-only and swapon fails without privileges. This scenario therefore
   # runs syntax and lint only instead of a real converge.

   scenario:
       test_sequence:
           - dependency
           - destroy
           - syntax

``verify.yml`` checks the **end state on the system**, not the Ansible return value:

.. code-block:: yaml

   - name: Stat the zram block device
     ansible.builtin.stat:
         path: /sys/block/zram0
     register: zram_dev

   - name: Assert the zram kernel module is loaded
     ansible.builtin.assert:
         that:
             - zram_dev.stat.exists
         fail_msg: "/sys/block/zram0 missing - zram module not loaded"

Makefile as Entry Point
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: makefile

   lint: lint-ansible lint-yaml lint-python  ## Run all linters
   test-unit:      ## Run pytest unit suite
   test-molecule:  ## Run every molecule scenario (slow, needs docker)
   build:          ## Build collection

One named target per check. CI calls the same targets the developer calls locally -
otherwise the two drift apart and "works on my machine" becomes permanent.

Part 3 - Architecture Level
---------------------------

Layers
~~~~~~

.. code-block:: text

   Inventory (facts about the world: which hosts, which environment)
      ↓ group_vars / host_vars
   Playbook (orchestration: which role in which order, which gates)
      ↓ role parameters
   Role (capability: how a state is achieved)
      ↓ module parameters
   Module / Plugin (primitive)

**The rule behind it: knowledge flows downward, never upward.** A role must not know which
playbook calls it, which environment it runs in, or which role ran before it. It receives
parameters and establishes a state.

Every violation of this direction makes the role unusable for the next use case.

What Belongs in the Playbook - and What Does Not
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Belongs in the playbook
     - Belongs in the role
   * - Order and dependencies between roles
     - How a single state is established
   * - Host selection (``hosts:``), strategy, ``serial``
     - What happens on a host
   * - Environment gates ("only if the firewall is up")
     - Internal validation of its own inputs
   * - Fetching credentials from a secret store
     - Accepting credentials as parameters

``module_defaults`` Against Parameter Duplication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When several roles address the same API target, the connection parameters belong in the
playbook **once**, not in every role:

.. code-block:: yaml

   - name: Configure infrastructure
     hosts: localhost
     module_defaults:
         group/community.vmware.vmware:
             hostname: "{{ vcenter_hostname }}"
             username: "{{ vcenter_username }}"
             password: "{{ vcenter_password }}"
             validate_certs: true
     roles:
         - role_a
         - role_b

The ``group/...`` syntax comes from the ``action_groups`` in the respective collection's
``meta/runtime.yml``. This is the clean way to solve the "four roles repeat the same four
lines" problem.

Secrets
~~~~~~~

* **Never in the role** - the role accepts a parameter, it fetches nothing
* **Never in the repository** - not even Vault-encrypted, if an external store is available
* **Origin is the playbook's business** - look up against the secret store, then pass through
  as a role parameter
* **``no_log: true``** on every task and every ``argument_specs`` option touching a secret
* **Secret scanner in CI** - gitleaks or secretlint as a pre-commit hook and in the pipeline run

See :ref:`security` for the concrete Vault and Bitwarden patterns.

Error Handling
~~~~~~~~~~~~~~

* **``block``/``rescue``/``always``** for cleanup that must also run on failure
* **``failed_when``** where the return value does not match the definition of success
* **``until``/``retries``/``delay``** for anything crossing a network - but with a finite ceiling
* **No ``ignore_errors: true`` as a habit** - either the error is irrelevant (then
  ``failed_when: false`` with a rationale) or it is not

.. code-block:: yaml

   # Good - states the intent and why the failure is acceptable
   - name: Stop legacy service if present
     ansible.builtin.systemd_service:
         name: avahi-daemon
         state: stopped
         enabled: false
     register: legacy_stop
     # Not every image ships this unit; a missing unit is not an error here.
     failed_when:
         - legacy_stop.failed
         - "'Could not find the requested service' not in (legacy_stop.msg | default(''))"

   # Bad - swallows every error, including the ones that matter
   - name: Stop legacy service
     ansible.builtin.systemd:
         name: avahi-daemon
         state: stopped
     ignore_errors: true

Performance
~~~~~~~~~~~

* **``gather_facts: false``** where no facts are needed; otherwise restrict ``gather_subset``
* **Fact caching** for repeated runs across the same fleet
* **One task with a list beats a loop over N tasks** - package managers accept lists and
  resolve once instead of N times
* **``async``/``poll: 0``** for long, independent operations
* **``serial``** for rolling updates instead of a big bang

.. code-block:: yaml

   # Good - one transaction, one dependency resolution
   - name: Install base packages
     ansible.builtin.package:
         name: "{{ base_packages }}"
         state: present

   # Bad - N transactions
   - name: Install base packages
     ansible.builtin.package:
         name: "{{ item }}"
         state: present
     loop: "{{ base_packages }}"

Pre-Merge Checklist
-------------------

Role
~~~~

* [ ] ``defaults/main.yml`` - all inputs, all prefixed, all commented
* [ ] ``meta/argument_specs.yml`` - type, ``required``, ``default``, real ``description``
* [ ] ``meta/main.yml`` - ``galaxy_info``, ``platforms``, ``min_ansible_version``, ``dependencies``, ``collections``
* [ ] ``README.md`` - variable table plus a runnable example invocation
* [ ] Lists plural, dicts singular, booleans ``_enabled``/``_required``
* [ ] OS differences in ``vars/<Distro>.yml``, not in ``defaults/``
* [ ] ``<role>_enabled`` present and respected on all tasks
* [ ] ``tasks/main.yml`` is a dispatcher, not implementation
* [ ] Handler names prefixed, no dead handler
* [ ] FQCN throughout, including ``become_method``
* [ ] ``no_log: true`` on every secret-handling task and option
* [ ] No ``set_fact`` used as a substitute for a default
* [ ] The role is callable without its originating playbook

Collection
~~~~~~~~~~

* [ ] ``galaxy.yml`` - dependencies with lower bounds, repository and issue links
* [ ] ``meta/runtime.yml`` - ``requires_ansible``, ``action_groups`` where useful
* [ ] ``ansible-lint`` profile ``production`` green, ``yamllint --strict`` green
* [ ] Molecule scenario per role under ``extensions/molecule/<role>/``, ``idempotence`` in the sequence
* [ ] Unit tests for every own plugin
* [ ] ``CHANGELOG.md`` maintained, breaking changes with migration instructions
* [ ] Makefile targets used by CI and developers alike

.. note::
   **The core idea in one sentence:** lint conformance checks idioms, not architecture. A
   role is only finished when someone can call it correctly without knowing its originating
   playbook - and the contract for that is machine-readable in ``argument_specs``.

.. seealso::

   * :ref:`standards` - repository standards, required files, release process
   * :ref:`contributing` - contribution workflow, code style, testing requirements
   * :ref:`security` - secrets management, hardening, security checklists
   * :ref:`cicd` - CI/CD workflows and linter configuration
   * `Collection structure <https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections_structure.html>`_ - official collection layout
   * `Molecule collection testing <https://docs.ansible.com/projects/molecule/getting-started-collections/>`_ - ``extensions/molecule/`` setup
