# Repository Agent Instructions

These instructions are the machine-oriented contributor contract for this
repository. They apply to all agent and contributor work in this repository.

## Scope

This repository contains personal system and application configuration. Treat
`README.md` as the human-facing overview, repository hierarchy, installation
guide, and component reference. Treat this file as the repository workflow and
policy source for agents.

- Keep changes small, intentional, and limited to the user-requested task.
- Preserve existing behavior unless a logical change intentionally updates it.
- Create files and directories only when a current task needs them.
- Do not add placeholder scaffolding, generated outputs, or local machine state
  to Git.
- Do not duplicate project structure or component usage details from
  `README.md`.

## Documentation Contract

Every logical change must leave repository state, contributor instructions, and
user-facing docs in agreement. Update the owning doc once instead of duplicating
status, command blocks, or interpretation.

- `README.md` owns the human-facing overview, repository hierarchy,
  installation instructions, and component descriptions.
- `AGENTS.md` owns contributor workflow, repository policy, validation
  expectations, and commit message format.
- Workflow or process changes must update `AGENTS.md`.
- User-facing usage changes must update `README.md`.

## Trunk-Based Worktree Workflow

`main` is the shared trunk, and `origin/main` may move while an agent is
working. Keep changes small, use short-lived branches or ephemeral worktrees for
logical components, and land validated commits back into `main` quickly.

Before implementation after the initial repository bootstrap:

1. Fetch and inspect the remote trunk with `git fetch origin main`.
1. Compare local `main` with `origin/main`.
1. Reconcile differences before branching, creating worktrees, or implementing.
1. Create a new short-lived branch or ephemeral git worktree from reconciled
   `main`.
1. Implement only inside that branch or worktree.
1. Commit each logical component whenever possible.
1. Before integration, fetch and inspect `origin/main` again.
1. Reconcile local `main` and `origin/main` before merging the work branch.
1. Fast-forward when possible. If `main` moved, rebase the work branch onto
   reconciled `main`, rerun required checks, then fast-forward. If rebase is not
   safe, merge explicitly.
1. Never overwrite, discard, or silently replace user or other-agent changes.
1. Push `main` after successful validation and integration when network access
   and remote credentials are available.
1. Remove ephemeral worktrees after successful integration and push.

If divergence, conflicts, or remote changes cannot be safely interpreted, stop
and surface the exact state instead of guessing.

## Change Style And Safety

Changes should make the repository easier to maintain without changing behavior
unless the behavior change is intentional, validated, and documented.

- Prefer small, coherent, behavior-preserving changes that can merge cleanly.
- Separate refactor commits from feature or behavior-change commits unless a
  task explicitly requires a coupled change.
- Avoid speculative abstractions, empty scaffolding, and optionality that current
  usage does not need.
- Treat commands that install, update, or copy into user directories as
  side-effectful. Do not run them unless the user explicitly asks.
- Keep credentials, private URLs, copied shell exports, developer-specific
  absolute paths, local logs, generated state, and machine-specific outputs out
  of Git.

## Declarative State Workflow

`project.toml` is the desired-state contract for tools and configuration
targets. `./stmharry-config.py` is the read-only inspection CLI for that
contract.

- Use `project.toml` before changing setup, update, or synchronization behavior.
- Run `python3 ./stmharry-config.py plan`, `check`, and `diff` before proposing
  host mutations.
- Treat Makefiles as legacy deterministic helpers until replacement behavior is
  implemented and documented.
- Keep repo-to-home apply behavior separate from home-to-repo capture behavior.
- Do not add host mutation to `./stmharry-config.py` without an explicit
  `apply`-style command and documented approval boundary.

## Checks

Before pushing a logical change, run:

```bash
pre-commit run --all-files
```

For Makefile changes, prefer dry-run validation before any live install or
update command:

```bash
make -n install
make -n -C <component> install
```

For declarative state or CLI changes, run:

```bash
python3 ./stmharry-config.py plan
python3 ./stmharry-config.py check
python3 ./stmharry-config.py diff
python3 ./stmharry-config.py capture
```

Final handoff must state which checks were run. If a check could not be run,
state the exact reason.

## Commit Message Format

Commit messages must follow:

```text
<gitmoji> (scope): <subject>
```

Use these categories:

```text
✨ feat       Introduce new features
🐛 fix        Fix a bug
📝 docs       Documentation only changes
💄 style      Code style changes
♻️ refactor   Refactoring without behavior change
⚡️ perf       Improve performance
✅ test       Add or update tests
🔧 build      Build system or dependency changes
👷 ci         CI configuration and scripts
🔒 chore      Other changes not affecting src or tests
⏪️ revert     Revert a previous commit
```

Examples:

```text
📝 docs(project): add repository agent instructions
🔧 build(git): update commit message template
♻️ refactor(zsh): simplify shell startup config
```

Commit bodies are optional. When present, explain what and why, not how, and
wrap body text at 72 characters.
