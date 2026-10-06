#!/usr/bin/env python3
"""Guarded reconciler for stmharry-config desired state."""

from __future__ import annotations

import argparse
import difflib
import filecmp
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "config.toml"
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
    managers = manifest.get("package_managers", {})
    if not isinstance(managers, dict) or any(not isinstance(item, dict) for item in managers.values()):
        return ["package_managers must be a table of tables"]
    sections = {section: manifest.get(section, []) for section in ("tools", "prerequisites", "configs")}
    sections["package_managers"] = [{**item, "id": name} for name, item in managers.items()]
    for section, entries in sections.items():
        if not isinstance(entries, list) or any(not isinstance(item, dict) for item in entries):
            errors.append(f"{section} must be an array of tables")
            return errors
        ids = [item.get("id") for item in entries]
        if any(not isinstance(value, str) or not value for value in ids):
            errors.append(f"{section} entries need nonempty string ids")
        valid_ids = [value for value in ids if isinstance(value, str)]
        if len(valid_ids) != len(set(valid_ids)):
            errors.append(f"{section} has duplicate ids")
        for index, item in enumerate(entries, start=1):
            label = f"{section}[{index}]"
            if "required" in item and not isinstance(item["required"], bool):
                errors.append(f"{label} required must be a boolean")
            platforms = item.get("platforms", ["Linux", "Darwin"])
            if not isinstance(platforms, list) or any(
                not isinstance(value, str) or value not in {"Linux", "Darwin"}
                for value in platforms
            ):
                errors.append(f"{label} platforms must contain Linux or Darwin")
            for field in ("alternatives", "version_args", "verify"):
                if field in item and not string_list(item[field]):
                    errors.append(f"{label} {field} must be an array of nonempty strings")
            setup = item.get("setup", {})
            if not isinstance(setup, dict) or any(
                system not in {"Linux", "Darwin"} or not string_list(commands)
                for system, commands in setup.items()
            ):
                errors.append(f"{label} setup must map platforms to command arrays")
            for field in ("docs", "notes"):
                if field in item and not isinstance(item[field], str):
                    errors.append(f"{label} {field} must be a string")
    for index, tool in enumerate(manifest.get("tools", []), start=1):
        for key in ("id", "command"):
            if not isinstance(tool.get(key), str) or not tool[key]:
                errors.append(f"tools[{index}] missing or invalid {key!r}")
        if "min_version" in tool:
            minimum = tool["min_version"]
            if not isinstance(minimum, str) or not re.fullmatch(r"\d+(?:\.\d+){0,2}", minimum):
                errors.append(f"tools[{index}] min_version must be a numeric version string")
            if not tool.get("version_args"):
                errors.append(f"tools[{index}] min_version requires version_args")
    for index, item in enumerate(manifest.get("prerequisites", []), start=1):
        for key in ("path", "group"):
            if not isinstance(item.get(key), str) or not item[key]:
                errors.append(f"prerequisites[{index}] missing or invalid {key!r}")
        kind = item.get("kind", "file")
        if not isinstance(kind, str) or kind not in {"file", "directory"}:
            errors.append(f"prerequisites[{index}] unsupported kind")
        phase = item.get("phase")
        if not isinstance(phase, str) or phase not in {"before-apply", "after-apply"}:
            errors.append(f"prerequisites[{index}] phase must be before-apply or after-apply")
    for index, config in enumerate(manifest.get("configs", []), start=1):
        for key in ("id", "source", "target"):
            if not isinstance(config.get(key), str) or not config[key]:
                errors.append(f"configs[{index}] missing or invalid {key!r}")
        kind = config.get("kind", "file")
        if not isinstance(kind, str) or kind not in {"file", "directory"}:
            errors.append(f"configs[{index}] has unsupported kind {kind!r}")
        try:
            parse_mode(config.get("mode"))
        except ValueError as exc:
            errors.append(f"configs[{index}] {exc}")
    return errors


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and bool(item.strip()) for item in value)


def version_tuple(value: str) -> tuple[int, int, int] | None:
    match = re.search(r"\bv?(\d+)\.(\d+)(?:\.(\d+))?", value)
    if not match:
        return None
    return (int(match[1]), int(match[2]), int(match[3] or 0))


def inspect_tool(tool: dict[str, Any]) -> tuple[str, str]:
    path = next(
        (found for command in [tool["command"], *tool.get("alternatives", [])]
         if (found := shutil.which(command))),
        None,
    )
    if not path:
        return "missing", "not on PATH"
    if "min_version" not in tool:
        return "ok", path
    try:
        result = subprocess.run(
            [path, *tool["version_args"]], capture_output=True, text=True,
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "version-unknown", f"{path}: version probe failed"
    version = version_tuple(result.stdout + "\n" + result.stderr)
    minimum = tuple(int(part) for part in tool["min_version"].split("."))
    minimum += (0,) * (3 - len(minimum))
    if result.returncode or version is None:
        return "version-unknown", f"{path}: cannot verify minimum {tool['min_version']}"
    installed = ".".join(str(part) for part in version)
    state = "ok" if version >= minimum else "incompatible"
    return state, f"{path} ({installed}; minimum {tool['min_version']})"


def selected_prerequisites(manifest: dict[str, Any], host: HostContext, groups: Sequence[str]) -> Iterable[dict[str, Any]]:
    for item in manifest.get("prerequisites", []):
        if active_for_host(item, host.system) and item["group"] in groups:
            yield item


def prerequisite_state(item: dict[str, Any], home: Path) -> str:
    path = expand_target(item["path"], home)
    present = path.is_dir() if item.get("kind", "file") == "directory" else path.is_file()
    return "ok" if present else "missing"


def print_recipe(item: dict[str, Any], system: str) -> None:
    commands = item.get("setup", {}).get(system, [])
    if not commands:
        print("    setup: no automated recipe for this platform; consult upstream docs")
    for command in commands:
        print("    setup:")
        for line in command.splitlines():
            print(f"      {line}")
    for command in item.get("verify", []):
        print(f"    verify: {command}")
    for field in ("docs", "notes"):
        if item.get(field):
            print(f"    {field}: {item[field]}")


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
        raise ValueError(f"invalid config.toml:\n{joined}")
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
    for name, path in host.package_managers.items():
        manager = manifest["package_managers"][name]
        if path is None and manager.get("setup"):
            print(f"  Bootstrap package manager: {name}")
            print_recipe(manager, host.system)
    print()
    print("Tool Plan (ordered recipes; optional tools require separate selection)")
    for tool in iter_active_tools(manifest, host.system):
        state, detail = inspect_tool(tool)
        label = bool_label(bool(tool.get("required", False)))
        print(f"  {state.upper():16s} {tool['id']} ({label}, {tool.get('channel', 'default')}) -> {detail}")
        if state != "ok":
            print_recipe(tool, host.system)
    for phase in ("before-apply", "after-apply"):
        print()
        print(f"Prerequisites ({phase}, {', '.join(groups)})")
        for item in selected_prerequisites(manifest, host, groups):
            if item["phase"] != phase:
                continue
            state = prerequisite_state(item, host.home)
            print(f"  {state.upper():16s} {item['id']} ({bool_label(item.get('required', False))}) -> {item['path']}")
            if state != "ok":
                print_recipe(item, host.system)
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
    print("Order: approved tools, before-apply prerequisites, config apply, after-apply bootstrap, verification.")
    print("No mutations were performed. Recipes are guidance, never executed by this CLI.")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    manifest = load_and_validate()
    host = host_context(manifest, args.home)
    groups = args.group or ["core"]
    failed_required_tools = 0
    missing_required_prerequisites = 0
    drift_required_configs = 0
    if not args.configs_only:
        print("Tools (current process PATH)")
        for tool in iter_active_tools(manifest, host.system):
            state, detail = inspect_tool(tool)
            required = bool(tool.get("required", False))
            print(f"  {state.upper():16s} {tool['id']} ({bool_label(required)}) -> {detail}")
            failed_required_tools += int(required and state != "ok")
        print()
        print(f"Prerequisites ({', '.join(groups)})")
        for item in selected_prerequisites(manifest, host, groups):
            state = prerequisite_state(item, host.home)
            required = bool(item.get("required", False))
            print(f"  {state.upper():16s} {item['id']} ({bool_label(required)}, {item['phase']}) -> {item['path']}")
            missing_required_prerequisites += int(required and state != "ok")
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
        f"{failed_required_tools} required tools missing or incompatible, "
        f"{missing_required_prerequisites} required prerequisites missing, "
        f"{drift_required_configs} selected required configs not in sync."
    )
    print("No mutations were performed.")
    failures = failed_required_tools + missing_required_prerequisites + drift_required_configs
    return 1 if args.strict and failures else 0


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
    check_parser.add_argument("--strict", action="store_true", help="return nonzero for required tool, prerequisite, or config failures")
    check_parser.add_argument("--configs-only", action="store_true", help="skip tool and prerequisite checks; verify isolated config apply")
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
