# stmharry-config

## Overview
This repository contains personal system and application configurations for **stmharry**. It organizes dotfiles and setup scripts for shell, editor, version control, terminal multiplexer, Gmail filter management, and system-level dependencies. Each component is managed via a dedicated `Makefile` for easy installation and updates.

## Repository Structure
```
stmharry-config/
├── Makefile            # top-level installer for core components
├── utils.mk            # shared Makefile utilities
├── astronvim/          # AstroNvim (Neovim) configuration
│   ├── Makefile
│   └── nvim/
├── git/                # Git configuration (.gitconfig, .gitmessage.txt)
│   ├── Makefile
│   ├── .gitconfig
│   └── .gitmessage.txt
├── gmailctl/           # Gmail filter management with gmailctl
│   ├── Makefile
│   └── config.jsonnet
├── system/             # System-level setup (brew/apt packages, dotfiles)
│   ├── Makefile
│   └── Harry.json
├── tmux/               # tmux configuration and TPM
│   ├── Makefile
│   └── tmux.conf
└── zsh/                # Zsh configuration and custom theme
    ├── Makefile
    ├── stmharry.zsh-theme
    ├── .zprofile
    └── .zshrc
```

## Components
Below is a summary of each configuration component:

### system
- Path: `system/`
- Installs system dependencies (Homebrew or apt) and copies `Harry.json` to `~`.

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
  - Installs Oh My Zsh and custom theme

### tmux
- Path: `tmux/`
- Manages tmux configuration:
  - `tmux.conf` (copied to `~/.config/tmux/tmux.conf`)
  - Installs TPM (tmux plugin manager) and plugins

### astronvim
- Path: `astronvim/`
- Provides AstroNvim (Neovim) setup:
  - Stores `nvim/` config directory
  - Uses Lazy.nvim for plugin management

### gmailctl
- Path: `gmailctl/`
- Configures Gmail filters via [gmailctl](https://github.com/mbrt/gmailctl):
  - `config.jsonnet`
  - Installs `gmailctl` CLI and initializes configuration

## Installation

### Prerequisites
- Git
- GNU Make
- curl (for script installs)

### Full Installation
Install core components (system, git, zsh, tmux, astronvim) from the root:

```sh
make install
```

### Per-Component Installation
From the root directory, you can install individual components:

```sh
make install-system
make install-git
make install-zsh
make install-tmux
make install-astronvim
```

To install Gmailctl and its configuration:

```sh
make -C gmailctl install
```

### Overwriting Existing Configs
By default, existing configuration files are not overwritten. To force overwrite, set:

```sh
make install FORCE=true
# or for a specific component:
make install-zsh FORCE=true
```

## Updating Configurations
Each component provides an `update-configs` target to pull the latest from this repo into your home directory. For example:

```sh
make -C system update-configs
make -C git    update-configs
make -C zsh    update-configs
make -C tmux   update-configs
make -C astronvim update-configs
make -C gmailctl update-configs
```

Alternatively, to update a single file:

```sh
make -C git update-config-.gitconfig
```

## License
This repository is maintained by **stmharry**. Usage and modifications are permitted under the terms specified by the repository owner.
