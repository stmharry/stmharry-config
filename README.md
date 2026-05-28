# stmharry-config

## Overview
This repository contains personal system and application configurations for **stmharry**. It organizes dotfiles and setup metadata for shell, editor, version control, terminal multiplexer, Gmail filter management, and system-level dependencies. `project.toml` is the desired-state contract, and `./stmharry-config.py` is the guarded vanilla-Python reconciliation tool.

## Repository Structure
```
stmharry-config/
├── AGENTS.md           # agent workflow and repository policy
├── project.toml        # declarative desired-state contract
├── stmharry-config.py  # guarded reconciliation CLI
├── astronvim/          # AstroNvim (Neovim) configuration
│   └── nvim/
├── git/                # Git configuration (.gitconfig, .gitmessage.txt)
│   ├── .gitconfig
│   └── .gitmessage.txt
├── gmailctl/           # Gmail filter management with gmailctl
│   └── config.jsonnet
├── ssh/                # SSH client configuration
│   └── config
├── system/             # System-level setup (brew/apt packages, dotfiles)
│   └── Harry.json
├── tmux/               # tmux configuration and TPM
│   └── tmux.conf
└── zsh/                # Zsh configuration and custom theme
    ├── stmharry.zsh-theme
    ├── .zprofile
    └── .zshrc
```

## Components
Below is a summary of each configuration component:

### system
- Path: `system/`
- Stores exported platform-specific application configuration such as `Harry.json`.

### git
- Path: `git/`
- Manages Git configuration:
  - `.gitconfig`
  - `.gitmessage.txt`

### zsh
- Path: `zsh/`
- Manages Zsh shell configuration:
  - `.zprofile` (login shell settings)
  - `.zshrc` (interactive shell settings)
  - `stmharry.zsh-theme` (Oh My Zsh custom prompt theme)

### tmux
- Path: `tmux/`
- Manages tmux configuration:
  - `tmux.conf` (copied to `~/.config/tmux/tmux.conf`)

### astronvim
- Path: `astronvim/`
- Provides AstroNvim (Neovim) setup:
  - Stores `nvim/` config directory
  - Uses Lazy.nvim for plugin management

### gmailctl
- Path: `gmailctl/`
- Configures Gmail filters via [gmailctl](https://github.com/mbrt/gmailctl):
  - `config.jsonnet`

### ssh
- Path: `ssh/`
- Stores SSH client configuration:
  - `config`

## Reconciliation

### Prerequisites
- Git
- Python 3.11 or newer

`project.toml` is the machine-readable desired-state contract for tools and
configuration targets. `./stmharry-config.py` reads that contract, reports
drift, and guardedly applies selected configuration groups.

```sh
python3 ./stmharry-config.py plan
python3 ./stmharry-config.py check
python3 ./stmharry-config.py diff
python3 ./stmharry-config.py capture
```

The default group is `core`, which covers required Git, zsh, tmux, and curated
AstroNvim configuration. Applying configs requires an explicit confirmation
flag:

```sh
python3 ./stmharry-config.py apply --group core --yes
```

When a target already exists and differs, the CLI creates a timestamped backup
beside the target before replacing it.

Optional private groups are never applied by default. Apply them explicitly:

```sh
python3 ./stmharry-config.py apply --group ssh --yes
python3 ./stmharry-config.py apply --group gmailctl --yes
python3 ./stmharry-config.py apply --group iterm2 --yes
```

For sandbox testing, point the target home at a temporary directory:

```sh
python3 ./stmharry-config.py apply --group core --home /tmp/stm-home --yes
```

## Commands

- `plan` summarizes host state, missing tools, and config drift.
- `check` reports required tool and config status.
- `diff` shows repo-to-home configuration differences.
- `capture` shows home-to-repo changes that could be captured manually.
- `apply` copies selected repo configs to the target home after `--yes`.

## License
This repository is maintained by **stmharry**. Usage and modifications are permitted under the terms specified by the repository owner.
