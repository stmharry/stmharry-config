# Repository Agent Instructions

These instructions are the machine-oriented contract for agents using or
changing this repository. `README.md` is the public usage entrypoint,
`config.toml` is the source of truth for desired state, and `./cli.py` is the
deterministic interface for inspection and guarded config apply.

## Scope

This repository contains personal system and application configuration. Agents
usually operate in one of two lanes:

- **Host Setup Operator:** use the repository to inspect or configure a machine.
- **Repository Maintainer:** change the repository itself.

Keep changes small, intentional, and limited to the user-requested task. Do not
add placeholder scaffolding, generated outputs, local logs, credentials, private
URLs, copied shell exports, or machine-specific state to Git.

## Host Setup Operator

When using this repository to set up or update a host, treat it as a guarded
declarative system.

1. Read `README.md`, `AGENTS.md`, and `config.toml`.
1. Use `python3 ./cli.py plan`, `check`, and `diff` before proposing host
   mutations.
1. Report missing tools, selected config groups, and drift clearly.
1. Do not install packages, copy files manually, or mutate the host through
   hidden commands.
1. Run `python3 ./cli.py apply --group <group> --yes` only after explicit user
   confirmation.
1. Keep repo-to-home apply separate from home-to-repo capture.

Package installation is currently planned output only. Do not add package
mutation unless a future explicit guarded command, confirmation flow, tests, and
docs exist.

## Repository Maintainer

When changing the repository, preserve existing behavior unless the requested
task intentionally changes it. Prefer narrow, coherent changes that can be
validated and merged quickly.

- `README.md` owns user-facing usage, public quickstarts, and compact
  orientation.
- `AGENTS.md` owns agent policy, maintainer workflow, validation expectations,
  and commit-message format.
- `config.toml` owns the machine-readable tool and configuration inventory.
- `./cli.py` owns deterministic inspection and guarded apply behavior.

Do not duplicate full config inventory in docs. Use prose for durable intent and
interfaces; use `config.toml` and CLI output for exact owned files and targets.

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

- Separate refactor commits from feature or behavior-change commits unless a
  task explicitly requires a coupled change.
- Avoid speculative abstractions, empty scaffolding, and optionality that current
  usage does not need.
- Treat commands that install, update, or copy into user directories as
  side-effectful. Do not run them unless the user explicitly asks.
- Do not add new host mutation to `./cli.py` without an explicit command,
  `--yes` confirmation, backups where applicable, tests, and docs.

## Checks

Before pushing a logical change, run:

```bash
python3 -m unittest
python3 ./cli.py plan
python3 ./cli.py check
python3 ./cli.py diff
python3 ./cli.py capture
```

For guarded apply changes, also run against a temporary home:

```bash
tmp_home="$(mktemp -d)"
python3 ./cli.py apply --group core --home "$tmp_home" --yes
python3 ./cli.py check --group core --home "$tmp_home" --strict
rm -rf "$tmp_home"
```

When available in the development environment, also run:

```bash
uvx pre-commit run --all-files
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
