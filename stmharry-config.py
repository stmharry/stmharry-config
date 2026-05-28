#!/usr/bin/env python3
"""Guarded reconciler for stmharry-config desired state."""

from __future__ import annotations

import argparse
import difflib
import filecmp
import os
import platform
import shutil
import stat
import sys
import tomllib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "project.toml"
BACKUP_FORMAT = "%Y%m%d-%H%M%S"


@dataclass(frozen=True)
class HostContext:
    system: str
    machine: str
    home: Path
    package_managers: dict[str, str | None]


@dataclass(frozen=True)
class ConfigTarget:
    id: str
    kind: str
    source: Path
    target: Path
    required: bool
    private: bool
    group: str
    tool: str
    origin: str
    mode: int | None


def load_manifest() -> dict[str, Any]:
    with MANIFEST.open("rb") as manifest_file:
        return tomllib.load(manifest_file)


def active_for_host(item: dict[str, Any], system: str) -> bool:
    platforms = item.get("platforms")
    return not platforms or system in platforms


def expand_target(value: str, home: Path) -> Path:
    expanded = os.path.expandvars(value)
    if expanded == "~":
        return home
    if expanded.startswith("~/"):
        return home / expanded[2:]
    return Path(expanded).expanduser()


def source_path(value: str) -> Path:
    return (ROOT / value).resolve()


def display_target(path: Path, home: Path) -> str:
    try:
        return "~/" + str(path.relative_to(home))
    except ValueError:
        return str(path)


def bool_label(value: bool) -> str:
    return "required" if value else "optional"


def parse_mode(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 8)
    raise ValueError(f"invalid mode value: {value!r}")


def config_group(raw_config: dict[str, Any]) -> str:
    if "group" in raw_config:
        return str(raw_config["group"])
    if bool(raw_config.get("private", False)):
        return "private"
    if bool(raw_config.get("required", False)):
        return "core"
    return "optional"


def config_private(raw_config: dict[str, Any]) -> bool:
    if "private" in raw_config:
        return bool(raw_config["private"])
    return config_group(raw_config) in {"private", "ssh", "gmailctl", "iterm2"}


def host_context(manifest: dict[str, Any], home: Path) -> HostContext:
    system = platform.system()
    package_managers = {}
    for name, manager in manifest.get("package_managers", {}).items():
        if active_for_host(manager, system):
            command = manager.get("command", name)
            package_managers[name] = shutil.which(command)
    return HostContext(
        system=system,
        machine=platform.machine(),
        home=home,
        package_managers=package_managers,
    )


def manifest_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for index, tool in enumerate(manifest.get("tools", []), start=1):
        for key in ("id", "command"):
            if key not in tool:
                errors.append(f"tools[{index}] missing {key!r}")
    for index, config in enumerate(manifest.get("configs", []), start=1):
        for key in ("id", "source", "target"):
            if key not in config:
                errors.append(f"configs[{index}] missing {key!r}")
        kind = config.get("kind", "file")
        if kind not in {"file", "directory"}:
            errors.append(f"configs[{index}] has unsupported kind {kind!r}")
        try:
            parse_mode(config.get("mode"))
        except ValueError as exc:
            errors.append(f"configs[{index}] {exc}")
    return errors


def package_hint(tool: dict[str, Any], managers: dict[str, str | None]) -> str:
    packages = tool.get("packages", {})
    for manager, path in managers.items():
        if path and manager in packages:
            return f"{manager}: {packages[manager]}"
    if packages:
        options = ", ".join(f"{name}: {package}" for name, package in packages.items())
        return f"available package hints: {options}"
    return "no package hint"


def iter_active_tools(manifest: dict[str, Any], system: str) -> Iterable[dict[str, Any]]:
    for tool in manifest.get("tools", []):
        if active_for_host(tool, system):
            yield tool


def config_target(raw_config: dict[str, Any], home: Path) -> ConfigTarget:
    return ConfigTarget(
        id=str(raw_config["id"]),
        kind=str(raw_config.get("kind", "file")),
        source=source_path(str(raw_config["source"])),
        target=expand_target(str(raw_config["target"]), home),
        required=bool(raw_config.get("required", False)),
        private=config_private(raw_config),
        group=config_group(raw_config),
        tool=str(raw_config.get("tool", raw_config["id"])),
        origin=str(raw_config.get("origin", "custom")),
        mode=parse_mode(raw_config.get("mode")),
    )


def iter_active_configs(manifest: dict[str, Any], host: HostContext) -> Iterable[ConfigTarget]:
    for config in manifest.get("configs", []):
        if active_for_host(config, host.system):
            yield config_target(config, host.home)


def select_configs(configs: Iterable[ConfigTarget], groups: Sequence[str]) -> list[ConfigTarget]:
    selected_groups = set(groups)
    return [config for config in configs if config.group in selected_groups]


def file_state(source: Path, target: Path) -> str:
    if not source.exists():
        return "source-missing"
    if not target.exists():
        return "target-missing"
    if source.is_file() and target.is_file() and filecmp.cmp(source, target, shallow=False):
        return "in-sync"
    if source.is_dir() and target.is_dir():
        changed = list(compare_directory(source, target))
        return "in-sync" if not changed else "drift"
    return "drift"


def compare_directory(source: Path, target: Path) -> Iterable[tuple[str, Path, Path]]:
    source_files = {path.relative_to(source): path for path in source.rglob("*") if path.is_file()}
    target_files = {path.relative_to(target): path for path in target.rglob("*") if path.is_file()}
    for relpath, source_file in sorted(source_files.items()):
        target_file = target / relpath
        if relpath not in target_files:
            yield ("target-missing", source_file, target_file)
        elif not filecmp.cmp(source_file, target_file, shallow=False):
            yield ("drift", source_file, target_file)
    for relpath, target_file in sorted(target_files.items()):
        if relpath not in source_files:
            yield ("target-extra", source / relpath, target_file)


def text_diff(left: Path, right: Path, left_label: str, right_label: str) -> list[str]:
    try:
        left_lines = left.read_text(errors="replace").splitlines(keepends=True)
        right_lines = right.read_text(errors="replace").splitlines(keepends=True)
    except OSError as exc:
        return [f"Unable to read {left} or {right}: {exc}\n"]
    return list(
        difflib.unified_diff(
            left_lines,
            right_lines,
            fromfile=left_label,
            tofile=right_label,
            lineterm="",
        )
    )


def backup_path(target: Path, timestamp: str) -> Path:
    return target.with_name(f"{target.name}.stmharry-config-backup-{timestamp}")


def copy_config(source: Path, target: Path, kind: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if kind == "directory":
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def apply_mode(target: Path, mode: int | None, kind: str) -> None:
    if mode is None:
        return
    if kind == "directory":
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(mode)
    else:
        target.chmod(mode)


def replace_config(config: ConfigTarget, timestamp: str) -> str:
    state = file_state(config.source, config.target)
    if state == "source-missing":
        raise FileNotFoundError(f"{config.id}: source does not exist: {config.source}")
    if state == "in-sync":
        return "in-sync"
    if config.target.exists():
        backup = backup_path(config.target, timestamp)
        if backup.exists():
            raise FileExistsError(f"{config.id}: backup already exists: {backup}")
        shutil.move(str(config.target), str(backup))
        copy_config(config.source, config.target, config.kind)
        apply_mode(config.target, config.mode, config.kind)
        return f"replaced with backup {backup}"
    copy_config(config.source, config.target, config.kind)
    apply_mode(config.target, config.mode, config.kind)
    return "created"


def load_and_validate() -> dict[str, Any]:
    manifest = load_manifest()
    errors = manifest_errors(manifest)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"invalid project.toml:\n{joined}")
    return manifest


def print_host(host: HostContext) -> None:
    print("Host")
    print(f"  system: {host.system}")
    print(f"  machine: {host.machine}")
    print(f"  home: {host.home}")
    print("  package managers:")
    for name, path in host.package_managers.items():
        status = path if path else "missing"
        print(f"    {name}: {status}")


def cmd_plan(args: argparse.Namespace) -> int:
    manifest = load_and_validate()
    host = host_context(manifest, args.home)
    groups = args.group or ["core"]
    print_host(host)
    print()
    print("Tool Plan")
    for tool in iter_active_tools(manifest, host.system):
        command = tool["command"]
        path = shutil.which(command)
        label = bool_label(bool(tool.get("required", False)))
        if path:
            print(f"  OK      {tool['id']} ({label}) -> {path}")
        else:
            hint = package_hint(tool, host.package_managers)
            print(f"  INSTALL {tool['id']} ({label}, {tool.get('channel', 'default')}) -> {hint}")
    print()
    print(f"Config Plan ({', '.join(groups)})")
    for config in select_configs(iter_active_configs(manifest, host), groups):
        state = file_state(config.source, config.target)
        label = bool_label(config.required)
        privacy = ", private" if config.private else ""
        print(f"  {state.upper():14s} {config.id} ({label}, {config.tool}, {config.origin}{privacy})")
        print(f"    source: {config.source.relative_to(ROOT)}")
        print(f"    target: {config.target}")
    print()
    print("No mutations were performed. Use apply --yes for guarded config sync.")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    manifest = load_and_validate()
    host = host_context(manifest, args.home)
    groups = args.group or ["core"]
    missing_required_tools = 0
    drift_required_configs = 0
    print("Tools")
    for tool in iter_active_tools(manifest, host.system):
        path = shutil.which(tool["command"])
        required = bool(tool.get("required", False))
        if path:
            print(f"  OK      {tool['id']} -> {path}")
        else:
            print(f"  MISSING {tool['id']} ({bool_label(required)})")
            missing_required_tools += int(required)
    print()
    print(f"Configs ({', '.join(groups)})")
    for config in select_configs(iter_active_configs(manifest, host), groups):
        state = file_state(config.source, config.target)
        print(f"  {state.upper():14s} {config.id} ({bool_label(config.required)})")
        if config.required and state != "in-sync":
            drift_required_configs += 1
    print()
    print(
        "Summary: "
        f"{missing_required_tools} required tools missing, "
        f"{drift_required_configs} selected required configs not in sync."
    )
    print("No mutations were performed.")
    return 1 if args.strict and drift_required_configs else 0


def print_config_diff(config: ConfigTarget, home: Path, capture: bool = False) -> bool:
    printed = False
    if config.kind == "directory":
        if not config.source.exists() or not config.target.exists():
            print(f"{config.id}: {file_state(config.source, config.target)}")
            return True
        for state, source_file, target_file in compare_directory(config.source, config.target):
            rel_label = source_file.relative_to(config.source) if source_file.exists() else target_file.relative_to(config.target)
            if state == "drift":
                print(f"{config.id}/{rel_label}: drift")
                for line in text_diff(source_file, target_file, str(source_file), str(target_file)):
                    print(line, end="" if line.endswith("\n") else "\n")
            else:
                print(f"{config.id}/{rel_label}: {state}")
            printed = True
        return printed
    state = file_state(config.source, config.target)
    if state == "in-sync":
        return False
    print(f"{config.id}: {state}")
    if state == "drift" and config.source.is_file() and config.target.is_file():
        left, right = (config.target, config.source) if capture else (config.source, config.target)
        left_label, right_label = (
            (f"home/{display_target(config.target, home)}", f"repo/{config.source.relative_to(ROOT)}")
            if capture
            else (f"repo/{config.source.relative_to(ROOT)}", f"home/{display_target(config.target, home)}")
        )
        for line in text_diff(left, right, left_label, right_label):
            print(line, end="" if line.endswith("\n") else "\n")
    return True


def cmd_diff(args: argparse.Namespace) -> int:
    manifest = load_and_validate()
    host = host_context(manifest, args.home)
    groups = args.group or ["core"]
    printed = False
    for config in select_configs(iter_active_configs(manifest, host), groups):
        printed = print_config_diff(config, host.home, capture=False) or printed
    if not printed:
        print("All selected config targets are in sync.")
    print("No mutations were performed.")
    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    manifest = load_and_validate()
    host = host_context(manifest, args.home)
    groups = args.group or ["core"]
    printed = False
    for config in select_configs(iter_active_configs(manifest, host), groups):
        printed = print_config_diff(config, host.home, capture=True) or printed
    if not printed:
        print("No selected local config changes to capture.")
    print("No mutations were performed.")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    manifest = load_and_validate()
    host = host_context(manifest, args.home)
    groups = args.group or ["core"]
    configs = select_configs(iter_active_configs(manifest, host), groups)
    if not configs:
        print(f"No active configs selected for groups: {', '.join(groups)}")
        return 1
    if not args.yes:
        print("Refusing to mutate host without --yes.")
        print(f"Selected groups: {', '.join(groups)}")
        print("Run plan/diff first, then rerun apply with --yes.")
        return 2
    timestamp = datetime.now().strftime(BACKUP_FORMAT)
    for config in configs:
        result = replace_config(config, timestamp)
        print(f"{config.id}: {result}")
    return 0


def add_common_options(parser: argparse.ArgumentParser, *, include_groups: bool = True) -> None:
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="home directory to inspect or mutate; useful for sandbox tests",
    )
    if include_groups:
        parser.add_argument(
            "--group",
            action="append",
            help="config group to select; defaults to core",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect and guardedly apply stmharry-config desired state.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="inspect host state and print proposed actions")
    add_common_options(plan_parser)
    plan_parser.set_defaults(func=cmd_plan)

    check_parser = subparsers.add_parser("check", help="report required tool and config status")
    add_common_options(check_parser)
    check_parser.add_argument("--strict", action="store_true", help="return nonzero when selected required configs drift")
    check_parser.set_defaults(func=cmd_check)

    diff_parser = subparsers.add_parser("diff", help="show repo-to-home config drift")
    add_common_options(diff_parser)
    diff_parser.set_defaults(func=cmd_diff)

    capture_parser = subparsers.add_parser("capture", help="show home-to-repo capture candidates")
    add_common_options(capture_parser)
    capture_parser.set_defaults(func=cmd_capture)

    apply_parser = subparsers.add_parser("apply", help="guardedly copy selected repo configs to the target home")
    add_common_options(apply_parser)
    apply_parser.add_argument("--yes", action="store_true", help="confirm host mutation")
    apply_parser.set_defaults(func=cmd_apply)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
