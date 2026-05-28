#!/usr/bin/env python3
"""Read-only reconciler for stmharry-config desired state."""

from __future__ import annotations

import argparse
import difflib
import filecmp
import os
import platform
import shutil
import sys
import tomllib
from collections.abc import Iterable
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "project.toml"


def load_manifest() -> dict[str, Any]:
    with MANIFEST.open("rb") as manifest_file:
        return tomllib.load(manifest_file)


def active_for_host(item: dict[str, Any], system: str) -> bool:
    platforms = item.get("platforms")
    return not platforms or system in platforms


def expand_target(value: str) -> Path:
    return Path(os.path.expandvars(value)).expanduser()


def source_path(value: str) -> Path:
    return (ROOT / value).resolve()


def display_target(path: Path) -> str:
    try:
        return "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def bool_label(value: bool) -> str:
    return "required" if value else "optional"


def host_context(manifest: dict[str, Any]) -> dict[str, Any]:
    system = platform.system()
    package_managers = {}
    for name, manager in manifest.get("package_managers", {}).items():
        if active_for_host(manager, system):
            command = manager.get("command", name)
            package_managers[name] = shutil.which(command)
    return {
        "system": system,
        "machine": platform.machine(),
        "home": Path.home(),
        "package_managers": package_managers,
    }


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


def iter_active_configs(manifest: dict[str, Any], system: str) -> Iterable[dict[str, Any]]:
    for config in manifest.get("configs", []):
        if active_for_host(config, system):
            yield config


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


def print_host(host: dict[str, Any]) -> None:
    print("Host")
    print(f"  system: {host['system']}")
    print(f"  machine: {host['machine']}")
    print(f"  home: {host['home']}")
    print("  package managers:")
    for name, path in host["package_managers"].items():
        status = path if path else "missing"
        print(f"    {name}: {status}")


def cmd_plan(_: argparse.Namespace) -> int:
    manifest = load_manifest()
    host = host_context(manifest)
    print_host(host)
    print()
    print("Tool Plan")
    for tool in iter_active_tools(manifest, host["system"]):
        command = tool["command"]
        path = shutil.which(command)
        label = bool_label(bool(tool.get("required", False)))
        if path:
            print(f"  OK      {tool['id']} ({label}) -> {path}")
        else:
            hint = package_hint(tool, host["package_managers"])
            print(f"  INSTALL {tool['id']} ({label}, {tool.get('channel', 'default')}) -> {hint}")
    print()
    print("Config Plan")
    for config in iter_active_configs(manifest, host["system"]):
        source = source_path(config["source"])
        target = expand_target(config["target"])
        state = file_state(source, target)
        label = bool_label(bool(config.get("required", False)))
        print(f"  {state.upper():14s} {config['id']} ({label})")
        print(f"    source: {source.relative_to(ROOT)}")
        print(f"    target: {target}")
    print()
    print("No mutations were performed. Use future apply support or legacy Make targets explicitly.")
    return 0


def cmd_check(_: argparse.Namespace) -> int:
    manifest = load_manifest()
    host = host_context(manifest)
    missing_required = 0
    drift_required = 0
    print("Tools")
    for tool in iter_active_tools(manifest, host["system"]):
        path = shutil.which(tool["command"])
        required = bool(tool.get("required", False))
        if path:
            print(f"  OK      {tool['id']} -> {path}")
        else:
            print(f"  MISSING {tool['id']} ({bool_label(required)})")
            missing_required += int(required)
    print()
    print("Configs")
    for config in iter_active_configs(manifest, host["system"]):
        source = source_path(config["source"])
        target = expand_target(config["target"])
        state = file_state(source, target)
        required = bool(config.get("required", False))
        print(f"  {state.upper():14s} {config['id']} ({bool_label(required)})")
        if required and state != "in-sync":
            drift_required += 1
    print()
    print(f"Summary: {missing_required} required tools missing, {drift_required} required configs not in sync.")
    print("No mutations were performed.")
    return 0


def print_config_diff(config: dict[str, Any], capture: bool = False) -> bool:
    source = source_path(config["source"])
    target = expand_target(config["target"])
    kind = config.get("kind", "file")
    printed = False
    if kind == "directory":
        if not source.exists() or not target.exists():
            print(f"{config['id']}: {file_state(source, target)}")
            return True
        for state, source_file, target_file in compare_directory(source, target):
            rel_label = source_file.relative_to(source) if source_file.exists() else target_file.relative_to(target)
            if state == "drift":
                print(f"{config['id']}/{rel_label}: drift")
                for line in text_diff(source_file, target_file, str(source_file), str(target_file)):
                    print(line, end="" if line.endswith("\n") else "\n")
            else:
                print(f"{config['id']}/{rel_label}: {state}")
            printed = True
        return printed
    state = file_state(source, target)
    if state == "in-sync":
        return False
    print(f"{config['id']}: {state}")
    if state == "drift" and source.is_file() and target.is_file():
        left, right = (target, source) if capture else (source, target)
        left_label, right_label = (
            (f"home/{display_target(target)}", f"repo/{source.relative_to(ROOT)}")
            if capture
            else (f"repo/{source.relative_to(ROOT)}", f"home/{display_target(target)}")
        )
        for line in text_diff(left, right, left_label, right_label):
            print(line, end="" if line.endswith("\n") else "\n")
    return True


def cmd_diff(_: argparse.Namespace) -> int:
    manifest = load_manifest()
    host = host_context(manifest)
    printed = False
    for config in iter_active_configs(manifest, host["system"]):
        printed = print_config_diff(config, capture=False) or printed
    if not printed:
        print("All active config targets are in sync.")
    print("No mutations were performed.")
    return 0


def cmd_capture(_: argparse.Namespace) -> int:
    manifest = load_manifest()
    host = host_context(manifest)
    printed = False
    for config in iter_active_configs(manifest, host["system"]):
        printed = print_config_diff(config, capture=True) or printed
    if not printed:
        print("No local config changes to capture.")
    print("No mutations were performed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect stmharry-config desired state without mutating the host.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, handler, help_text in (
        ("plan", cmd_plan, "inspect host state and print proposed actions"),
        ("check", cmd_check, "report required tool and config status"),
        ("diff", cmd_diff, "show repo-to-home config drift"),
        ("capture", cmd_capture, "show home-to-repo capture candidates"),
    ):
        subparser = subparsers.add_parser(name, help=help_text)
        subparser.set_defaults(func=handler)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
