# stmharry-config

A personal developer environment for Ubuntu 24.04 and macOS: zsh/Oh My Zsh,
tmux/Catppuccin, AstroNvim, and terminal coding agents. `config.toml` owns the
exact tool, prerequisite, and configuration inventory. `cli.py` inspects that
contract and applies selected config files with confirmation and backups.

Installation is agent-guided. The CLI prints recipes and verification commands;
it never runs package installers, plugin installers, or authentication flows.

## Agent Setup Quickstart

Start with Git and Python 3.11+ and clone this repository. Bootstrap instructions
for those tools are in `config.toml`; macOS also needs Homebrew for system package
recipes. Linux recipes target Ubuntu 24.04, not every Linux distribution.
`plan` prints Homebrew's bootstrap recipe when it is missing.

Give an agent this repository root and this prompt:

> Read README.md, AGENTS.md, and config.toml. Inspect this host with plan, check,
> diff, and capture. Report missing or incompatible required tools, prerequisites,
> configuration drift, and proposed local overrides. Show the exact installation,
> bootstrap, and apply commands for review before changing the host. Preserve
> existing credentials and machine-specific settings.

The setup sequence is:

1. Inspect using the commands below. Tools are checked on the current process
   PATH; `--home` redirects configuration and prerequisite paths, not tool probes.
1. Review drift in both directions. Separate portable improvements worth bringing
   into the repository from host-specific settings to preserve locally.
1. Approve the exact required tool recipes and `before-apply` prerequisites from
   `plan`. Execute selected recipes in order, in bash or zsh. Optional tools
   require explicit selection. Do not reinstall a working, compatible tool merely
   because it uses a different installation method.
1. Preserve local settings as described below, review the selected config diff,
   and approve `apply --group core --yes`.
1. Execute the selected `after-apply` bootstrap steps. Restore the editor lockfile,
   install tmux plugins in an isolated server, and check runtime health.
1. Start a fresh login shell and run `check --strict`. Complete authentication
   separately, with the account owner present.

For Codex, explicitly instruct it to read `AGENTS.md` and confirm the repository
root and Host Setup Operator workflow before host actions. Claude Code 2.1.277+
can load `AGENTS.md` directly when there is no overriding `CLAUDE.md` in the
working directory or its ancestors. Check `/context` to verify loaded guidance;
if an existing `CLAUDE.md` overrides it, import `@AGENTS.md` there rather than
copying the policy. See [Claude instruction loading](https://code.claude.com/docs/en/memory#agents-md).

## Inspection and Apply

```sh
python3 ./cli.py plan
python3 ./cli.py check
python3 ./cli.py diff
python3 ./cli.py capture
```

`plan` prints ordered platform-specific recipes for missing/incompatible tools
and missing prerequisites, split into before/after apply phases. `verify` and
`docs` entries provide the follow-up checks and upstream references. A file-based
prerequisite check confirms bootstrap files exist; it does not replace editor,
plugin, or authentication health checks.

`check` reports all required tools and selected configuration/prerequisites.
Normal inspection returns zero even with drift; `--strict` returns nonzero for
missing/incompatible required tools, failed version probes, missing required
prerequisites, or selected required configuration drift. Optional missing tools
do not fail strict checks. Version minimums establish compatibility, not whether
an installed tool is the newest release.

After reviewing the diff and approving the selected group:

```sh
python3 ./cli.py apply --group core --yes
```

`apply` requires `--yes`, backs up changed files beside each target as
`*.stmharry-config-backup-YYYYMMDD-HHMMSS`, and leaves identical targets alone.
It owns only the declared files, leaving local overrides and other files alone.
The home-to-repo `capture` command only displays candidates; it never imports
host settings into Git. Apply is not a transaction: if a copy fails, inspect
reported changes and backups before retrying. Restore a backup only after
reviewing changes made since apply.

For isolated configuration-copy tests:

```sh
tmp_home="$(mktemp -d)"
python3 ./cli.py apply --group core --home "$tmp_home" --yes
python3 ./cli.py check --group core --home "$tmp_home" --strict --configs-only
rm -rf "$tmp_home"
```

`--configs-only` skips tools and prerequisites; it does not establish that a
machine is fully set up. Installation recipes always target the current user's
home; `--home` does not rewrite printed shell instructions into sandbox commands.

## Local Settings and Migration

Before replacing an existing shell or Git config, review its drift and retain
host-specific changes in untracked home files:

- `~/.zshrc.local` loads last in interactive shells. Put private connection
  helpers, environment hooks, CUDA/project choices, and optional integration
  settings here. Keep secrets out of the repository; the legacy
  `~/.zsh_secrets` hook remains supported.
- `~/.gitconfig.local` is included after shared Git defaults. Preserve local
  identity, signing keys and signing requirements, credential helpers, custom
  includes, and machine-specific filter configuration here. Extract these
  settings from the existing config before apply; a backup alone does not keep
  them active. Shared defaults do not force signed commits.

Neither override is created or replaced by apply. Do not copy an entire host
configuration into the public repository. Existing SSH, Gmail, and iTerm2 groups
remain private and opt-in; inspect them before selecting them.

```sh
python3 ./cli.py plan --group ssh
python3 ./cli.py diff --group ssh
# Only after approving that group:
python3 ./cli.py apply --group ssh --yes
```

The new `.zshenv` exposes user-local tools to noninteractive SSH shells without
loading plugins or emitting output. Login shells initialize Homebrew and nvm;
interactive shells load optional integrations only when present. Source nvm
explicitly when an agent needs Node in a non-login shell.

## Plugin Bootstrap

Restore the committed AstroNvim v6 plugin versions:

```sh
nvim --headless '+Lazy! restore' +qa
```

Then inspect `:checkhealth` and Mason's required language servers, formatters,
debugger, and Tree-sitter CLI listed in the manifest. Network/compiler failures
must be resolved before declaring the editor ready. Install a Nerd Font on the
terminal client; an SSH-only server does not need the font. Configure clipboard
support for the actual desktop or SSH workflow rather than installing GUI tools
on every server.

For migrations from AstroNvim v4, review local plugin specs for v6 API changes.
Keep backups of editor configuration and data; do not delete caches or local
plugins automatically. Routine setup uses `Lazy restore`; maintainers regenerate
locks in an isolated home with `Lazy sync`, including optional Copilot plugins.
See [AstroNvim v6 migration](https://docs.astronvim.com/configuration/v6_migration/).

Copilot and Copilot Chat are opt-in. Set `STMHARRY_NVIM_COPILOT=1` in your local
shell override, restart Neovim, restore plugins, and authenticate with
`:Copilot auth` yourself. Authentication is never a build hook. Without the
flag, editor setup requires no Copilot credentials. Markdown preview starts
only through `:MarkdownPreview`, listens on localhost, and prints its URL;
forward its reported port over SSH when needed.

Catppuccin is installed manually at the manifest's tagged version; TPM manages
the other tmux plugins. Bootstrap in a temporary server instead of reloading
existing user sessions:

```sh
tmux_setup_dir="$(mktemp -d)"
tmux -S "$tmux_setup_dir/socket" -f "$HOME/.config/tmux/tmux.conf" new-session -d -s setup
TMUX="$tmux_setup_dir/socket,0,0" "$HOME/.tmux/plugins/tpm/bin/install_plugins"
tmux -S "$tmux_setup_dir/socket" kill-server
rm -rf "$tmux_setup_dir"
```

Confirm the manifest's plugin files exist, then check theme and CPU status in a
new session. Do not update or reload existing sessions without approval.

## Coding Agent Authentication

Codex and Claude use official native installers and require neither Bun nor
Node to run. The full developer baseline still includes those runtimes for
other development and editor features. Existing working installations are kept.

Verify installation using the manifest commands. Then run
`codex login --device-auth` for a headless Codex login, or launch `claude` and
follow its account login flow. Keep these interactive steps separate from setup
completion. Preserve `~/.codex`, `~/.claude`, and `~/.claude.json`; never copy
credentials or account state into this repository. This repository does not
manage agent model, approval, permission, or global account settings.

## Repository Maintenance

Follow `AGENTS.md` for branch integration, required validation, and commit
format. Change recipes and exact inventory in `config.toml`, user-facing
workflow here, and agent policy in `AGENTS.md`.

## License

This repository is maintained by **stmharry**. Usage and modifications are
permitted under the terms specified by the repository owner.
