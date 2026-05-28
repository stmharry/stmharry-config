# stmharry-config

## Overview

This is a public, guarded personal configuration repository for **stmharry**.
`config.toml` declares the desired tools and owned configuration targets, and
`./cli.py` is the vanilla-Python interface for inspecting drift and applying
selected config groups with explicit confirmation.

## Agent Setup Quickstart

If an agent is given this repository to set up a machine, it should treat the
repository as a deterministic contract rather than improvise host changes.
After installing or opening the agent, paste this repository root and ask it to
follow the guarded workflow here.

1. Read `README.md`, `AGENTS.md`, and `config.toml`.
1. Inspect the host with the read-only commands:

   ```sh
   python3 ./cli.py plan
   python3 ./cli.py check
   python3 ./cli.py diff
   ```

1. Report missing tools, config drift, and the exact group to apply.
1. Do not install packages or copy files by hand.
1. Apply configuration only after explicit user confirmation:

   ```sh
   python3 ./cli.py apply --group core --yes
   ```

`apply` backs up drifted targets beside the target before replacement. Optional
private groups are never part of the default apply path.

## Human Quickstart

Prerequisites:

- Git
- Python 3.11 or newer

Inspect planned work and current drift:

```sh
python3 ./cli.py plan
python3 ./cli.py check
python3 ./cli.py diff
python3 ./cli.py capture
```

Apply the default required configuration group:

```sh
python3 ./cli.py apply --group core --yes
```

Apply optional private groups only when needed:

```sh
python3 ./cli.py apply --group ssh --yes
python3 ./cli.py apply --group gmailctl --yes
python3 ./cli.py apply --group iterm2 --yes
```

For sandbox testing, point the target home at a temporary directory:

```sh
python3 ./cli.py apply --group core --home /tmp/stm-home --yes
```

## Configuration Groups

`config.toml` is the authoritative inventory. Use `python3 ./cli.py plan` for
the current host-specific view.

| Group | Default | Private | Purpose |
| --- | --- | --- | --- |
| `core` | Yes | No | Required Git, shell, tmux, and editor configuration. |
| `ssh` | No | Yes | SSH client configuration. |
| `gmailctl` | No | Yes | Gmail filter configuration for gmailctl. |
| `iterm2` | No | Yes | Platform-specific terminal profile export. |

## Repository Maintenance

Agents changing this repository must follow `AGENTS.md`. In short: keep changes
small, update `README.md` for user-facing usage changes, update `AGENTS.md` for
workflow or policy changes, validate with the documented checks, and use the
repository commit-message format.

## License

This repository is maintained by **stmharry**. Usage and modifications are
permitted under the terms specified by the repository owner.
