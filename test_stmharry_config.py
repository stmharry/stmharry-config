from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "stmharry-config.py"


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

            strict_status, strict_output = self.run_cli("check", "--home", tmp, "--group", "core", "--strict")
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


if __name__ == "__main__":
    unittest.main()
