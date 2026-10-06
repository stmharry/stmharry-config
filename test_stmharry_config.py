from __future__ import annotations

import importlib.util
import io
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "cli.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("stmharry_config", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GuardedConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cli = load_cli()

    def run_cli(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            status = self.cli.main(list(args))
        return status, output.getvalue()

    def test_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status, output = self.run_cli("apply", "--home", tmp, "--group", "core")
        self.assertEqual(status, 2)
        self.assertIn("without --yes", output)

    def test_apply_creates_core_configs_in_sandbox_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status, _ = self.run_cli("apply", "--home", tmp, "--group", "core", "--yes")
            self.assertEqual(status, 0)
            self.assertTrue((Path(tmp) / ".gitconfig").is_file())
            self.assertTrue((Path(tmp) / ".gitmessage.txt").is_file())
            self.assertTrue((Path(tmp) / ".zshrc").is_file())
            self.assertTrue((Path(tmp) / ".config" / "tmux" / "tmux.conf").is_file())
            self.assertTrue((Path(tmp) / ".config" / "nvim").is_dir())

            strict_status, strict_output = self.run_cli("check", "--home", tmp, "--group", "core", "--strict", "--configs-only")
            self.assertEqual(strict_status, 0)
            self.assertIn("0 selected required configs not in sync", strict_output)

    def test_apply_backs_up_drifted_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / ".gitconfig"
            target.write_text("[user]\n\tname = Local\n")

            status, output = self.run_cli("apply", "--home", tmp, "--group", "core", "--yes")
            self.assertEqual(status, 0)
            self.assertIn("gitconfig: replaced with backup", output)
            backups = list(Path(tmp).glob(".gitconfig.stmharry-config-backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertIn("Harry Hsu", target.read_text())
            self.assertIn("Local", backups[0].read_text())

    def test_diff_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status, output = self.run_cli("diff", "--home", tmp, "--group", "core")
        self.assertEqual(status, 0)
        self.assertIn("No mutations were performed.", output)

    def test_repeated_apply_preserves_local_overrides_and_excludes_private_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            local = home / ".zshrc.local"
            local.write_text("export EDITOR=local-editor\n")
            git_local = home / ".gitconfig.local"
            git_local.write_text("[commit]\n\tgpgsign = true\n[user]\n\tsigningkey = local-key\n")
            self.assertEqual(self.run_cli("apply", "--home", tmp, "--yes")[0], 0)
            status, output = self.run_cli("apply", "--home", tmp, "--yes")
            self.assertEqual(status, 0)
            self.assertNotIn("created", output)
            self.assertNotIn("replaced", output)
            self.assertEqual(local.read_text(), "export EDITOR=local-editor\n")
            self.assertIn("local-key", git_local.read_text())
            self.assertFalse((home / ".ssh/config").exists())
            self.assertFalse((home / ".gmailctl").exists())
            self.assertFalse((home / "Harry.json").exists())
            self.assertEqual(list(home.rglob("*.stmharry-config-backup-*")), [])
            if shutil.which("git"):
                result = subprocess.run(
                    ["git", "config", "--file", str(home / ".gitconfig"), "--includes", "--get", "commit.gpgsign"],
                    env={**os.environ, "HOME": tmp}, text=True, capture_output=True, check=True,
                )
                self.assertEqual(result.stdout.strip(), "true")

    def test_inspection_never_executes_recipes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = copy.deepcopy(self.cli.load_manifest())
            manifest["tools"] = [{"id": "missing", "command": "missing", "required": True,
                                  "setup": {"Darwin": ["touch dangerous"], "Linux": ["touch dangerous"]}}]
            manifest["prerequisites"] = []
            with patch.object(self.cli, "load_manifest", return_value=manifest), patch.object(self.cli.shutil, "which", return_value=None), patch.object(self.cli.subprocess, "run") as run:
                for command in ("plan", "check", "diff", "capture"):
                    status, _ = self.run_cli(command, "--home", tmp)
                    self.assertEqual(status, 0)
                run.assert_not_called()
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_strict_includes_required_tools_and_prerequisites(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli("apply", "--home", tmp, "--yes")
            manifest = self.cli.load_manifest()
            with patch.object(self.cli, "inspect_tool", return_value=("missing", "not on PATH")):
                self.assertEqual(self.run_cli("check", "--home", tmp, "--strict")[0], 1)
                self.assertEqual(self.run_cli("check", "--home", tmp)[0], 0)
                status, output = self.run_cli("check", "--home", tmp, "--strict", "--configs-only")
                self.assertEqual(status, 0)
                self.assertNotIn("Prerequisites (", output)
            manifest["tools"] = []
            with patch.object(self.cli, "load_manifest", return_value=manifest):
                status, output = self.run_cli("check", "--home", tmp, "--strict")
                self.assertEqual(status, 1)
                self.assertIn("required prerequisites missing", output)

    def test_optional_missing_tools_do_not_fail_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"tools": [{"id": "optional", "command": "optional", "required": False}], "configs": []}
            with patch.object(self.cli, "load_manifest", return_value=manifest), patch.object(self.cli.shutil, "which", return_value=None):
                self.assertEqual(self.run_cli("check", "--home", tmp, "--strict")[0], 0)

    def test_platform_specific_recipes_and_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(self.cli.platform, "system", return_value="Linux"), patch.object(self.cli, "inspect_tool", return_value=("missing", "not on PATH")):
                status, output = self.run_cli("plan", "--home", tmp)
            self.assertEqual(status, 0)
            self.assertIn("sudo apt install git", output)
            self.assertNotIn("brew install", output)
            self.assertNotIn("sudo apt install neovim", output)
            self.assertLess(output.index("python (required"), output.index("pre-commit (required"))
            self.assertLess(output.index("Prerequisites (before-apply"), output.index("Prerequisites (after-apply"))
            self.assertNotIn("system-harry", output)
            with patch.object(self.cli.platform, "system", return_value="Darwin"), patch.object(self.cli, "inspect_tool", return_value=("missing", "not on PATH")), patch.object(self.cli.shutil, "which", return_value=None):
                _, output = self.run_cli("plan", "--home", tmp)
            self.assertIn("brew install neovim", output)
            self.assertIn("Homebrew/install/HEAD/install.sh", output)
            self.assertNotIn("sudo apt", output)

    def test_version_probes(self) -> None:
        tool = {"id": "neovim", "command": "nvim", "min_version": "0.11", "version_args": ["--version"]}
        for output, expected in [("NVIM v0.12.3", "ok"), ("NVIM v0.9.5", "incompatible"), ("unknown", "version-unknown")]:
            with self.subTest(output=output), patch.object(self.cli.shutil, "which", return_value="/bin/nvim"), patch.object(self.cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, output, "")) as run:
                self.assertEqual(self.cli.inspect_tool(tool)[0], expected)
                self.assertEqual(run.call_args.args[0], ["/bin/nvim", "--version"])
        for failure in [OSError("missing"), subprocess.TimeoutExpired("nvim", 10)]:
            with self.subTest(failure=failure), patch.object(self.cli.shutil, "which", return_value="/bin/nvim"), patch.object(self.cli.subprocess, "run", side_effect=failure):
                self.assertEqual(self.cli.inspect_tool(tool)[0], "version-unknown")
        with patch.object(self.cli.shutil, "which", return_value="/bin/nvim"), patch.object(self.cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "0.12.3", "")):
            self.assertEqual(self.cli.inspect_tool(tool)[0], "version-unknown")
        self.assertEqual(self.cli.version_tuple("v24.3.0"), (24, 3, 0))
        self.assertEqual(self.cli.version_tuple("tmux 3.2a"), (3, 2, 0))

    def test_fd_alternative(self) -> None:
        with patch.object(self.cli.shutil, "which", side_effect=lambda command: "/usr/bin/fdfind" if command == "fdfind" else None):
            state, detail = self.cli.inspect_tool({"command": "fd", "alternatives": ["fdfind"]})
            self.assertEqual(state, "ok")
            self.assertEqual(detail, "/usr/bin/fdfind")

    def test_prerequisite_kind_and_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            item = {"id": "file", "path": "~/resource", "group": "core", "phase": "before-apply"}
            self.assertEqual(self.cli.prerequisite_state(item, home), "missing")
            (home / "resource").mkdir()
            self.assertEqual(self.cli.prerequisite_state(item, home), "missing")
            self.assertEqual(self.cli.prerequisite_state({**item, "kind": "directory"}, home), "ok")
            host = self.cli.HostContext("Linux", "x86_64", home, {})
            items = [item, {**item, "id": "private", "group": "ssh"}, {**item, "id": "mac", "platforms": ["Darwin"]}]
            self.assertEqual(list(self.cli.selected_prerequisites({"prerequisites": items}, host, ["core"])), [item])

    def test_manifest_validation(self) -> None:
        self.assertEqual(self.cli.manifest_errors(self.cli.load_manifest()), [])
        cases = [
            {"package_managers": {"brew": {"setup": {"Darwin": "install"}}}},
            {"prerequisites": [{"id": "x", "path": "~/x", "group": "core", "phase": {}, "platforms": [{}]}]},
            {"tools": [{"id": "x", "command": "x", "min_version": "newest"}]},
            {"tools": [{"id": "x", "command": "x", "setup": {"Linux": "install x"}}]},
            {"tools": [{"id": "x", "command": "x", "verify": [7]}]},
            {"tools": [{"id": "x", "command": "x"}, {"id": "x", "command": "x"}]},
            {"tools": [{"id": "x", "command": "x", "required": "true"}]},
            {"prerequisites": [{"id": "x", "path": "~/x", "group": "core", "phase": "invalid"}]},
        ]
        for manifest in cases:
            with self.subTest(manifest=manifest):
                self.assertTrue(self.cli.manifest_errors(manifest))

    @unittest.skipUnless(shutil.which("zsh"), "zsh unavailable")
    def test_zsh_startup_and_noninteractive_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="stm home ") as tmp:
            home = Path(tmp)
            self.run_cli("apply", "--home", tmp, "--yes")
            binary = home / ".local/bin/codex"
            binary.parent.mkdir(parents=True)
            binary.write_text("#!/bin/sh\nexit 0\n")
            binary.chmod(0o755)
            (home / ".zshrc.local").write_text("export EDITOR=local-editor\n")
            env = {**os.environ, "HOME": tmp, "ZDOTDIR": tmp}
            result = subprocess.run(["zsh", "-d", "-c", "command -v codex"], env=env, capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), str(binary))
            result = subprocess.run(["zsh", "-d", "-i", "-c", 'print -r -- "$EDITOR"'], env=env, capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), "local-editor")
            self.assertEqual(result.stderr, "")

    @unittest.skipUnless(shutil.which("nvim"), "Neovim unavailable")
    def test_optional_editor_specs_without_installing_plugins(self) -> None:
        plugins = json.dumps(str(ROOT / "astronvim/nvim/lua/plugins"))
        code = """
local base = PLUGINS
vim.env.STMHARRY_NVIM_COPILOT = nil
local copilot = dofile(base .. "/copilot.lua")
assert(copilot.enabled == false and copilot.build == nil)
for _, plugin in ipairs(dofile(base .. "/copilot-chat.lua")) do assert(plugin.enabled == false) end
vim.env.STMHARRY_NVIM_COPILOT = "1"
assert(dofile(base .. "/copilot.lua").enabled == true)
for _, plugin in ipairs(dofile(base .. "/copilot-chat.lua")) do assert(plugin.enabled == true) end
local preview = dofile(base .. "/markdown-preview.lua")
preview.init()
assert(vim.g.mkdp_auto_start == 0 and vim.g.mkdp_open_to_the_world == 0)
-- Lua treats 0 as truthy: ensure the no-npx branch uses the binary installer.
vim.fn.executable = function() return 0 end
local installed = false
local original_cmd = vim.cmd
vim.fn["mkdp#util#install"] = function() installed = true end
vim.cmd = function(command) assert(command == "Lazy load markdown-preview.nvim") end
preview.build({dir = "/unused"})
assert(installed)
vim.cmd = original_cmd
print("EDITOR_SPEC_CHECK_OK")
""".replace("PLUGINS", plugins)
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["nvim", "--headless", "-u", "NONE", "-i", "NONE", "+lua " + code, "+qa"],
                env={**os.environ, "HOME": tmp}, capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("EDITOR_SPEC_CHECK_OK", result.stderr)
            self.assertNotIn("Error detected", result.stderr)

    @unittest.skipUnless(shutil.which("tmux"), "tmux unavailable")
    def test_tmux_startup_preserves_keybindings_without_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli("apply", "--home", tmp, "--yes")
            socket = str(Path(tmp) / "tmux.sock")
            env = {**os.environ, "HOME": tmp}
            base = ["tmux", "-S", socket]
            try:
                subprocess.run([*base, "-f", str(Path(tmp) / ".config/tmux/tmux.conf"), "new-session", "-d", "-s", "smoke"], env=env, capture_output=True, text=True, check=True)
                result = subprocess.run([*base, "show-options", "-gv", "prefix"], env=env, capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout.strip(), "C-a")
                result = subprocess.run([*base, "list-keys", "-T", "prefix"], env=env, capture_output=True, text=True, check=True)
                self.assertIn('split-window -h -c', result.stdout)
            finally:
                subprocess.run([*base, "kill-server"], env=env, capture_output=True)


if __name__ == "__main__":
    unittest.main()
