# System Configs for `stmharry`

## Overview
This repository contains configuration files and setup scripts for various tools and environments used by `stmharry`. The configurations are structured into directories based on their respective applications, and installation is managed using `Makefile`s.

## Directory Structure
```
└── stmharry-config/
    ├── Makefile
    ├── utils.mk
    ├── .pre-commit-config.yaml
    ├── astronvim/
    │   ├── Makefile
    │   └── nvim/
    ├── gmailctl/
    │   ├── Makefile
    │   └── config.jsonnet
    ├── tmux/
    │   ├── Makefile
    │   └── tmux.conf
    └── zsh/
        ├── Harry.json
        ├── Makefile
        ├── stmharry.zsh-theme
        └── .zshrc
```

## Configuration Details
### Zsh
Located in `zsh/`, this directory contains Zsh-related configurations.
- `.zshrc` sets up environment variables, aliases, and plugin configurations.
- `stmharry.zsh-theme` defines the custom prompt appearance.
- `Makefile` provides installation scripts for `oh-my-zsh` and additional tools.

### Tmux
Located in `tmux/`, this directory contains the configuration for `tmux`.
- `tmux.conf` contains the user-defined configuration.
- `Makefile` automates the installation of `tmux` and its plugin manager (`tpm`).

### Astronvim (Neovim Configuration)
Located in `astronvim/nvim/`, this directory contains the configuration for AstroNvim, a highly extensible Neovim distribution.
- Plugins are defined in `lua/plugins/`
- Core settings are managed in `init.lua`, `lazy_setup.lua`, and `polish.lua`.
- Uses Lazy.nvim for plugin management.

### Gmailctl
Located in `gmailctl/`, this directory contains configuration for managing Gmail filters using `gmailctl`.
- The `config.jsonnet` file defines filters and labels.
- `Makefile` automates the setup and configuration updates.


## Installation
To install the configurations, use the provided `Makefile`. Run the following command from the root directory:

```sh
make install
```

To install a specific component, use:
```sh
make install-<component>
```
Where `<component>` can be `zsh`, `tmux`, `astronvim`, or `gmailctl`.

## Updating Configurations
To update the configuration files from the system, use:
```sh
make update-configs
```
For a specific component:
```sh
make update-configs-<component>
```

## License
This repository is maintained by `stmharry`. Usage and modifications are permitted under the terms specified by the repository owner.
