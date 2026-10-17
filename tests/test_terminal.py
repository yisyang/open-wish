import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

from openwish import __version__
from openwish.integrations import install_skills

from tests.support import ProjectCase


@unittest.skipUnless(os.name == "posix", "Pseudo-terminal checks require POSIX")
class TerminalTests(ProjectCase):
    def start(self, *args, term="xterm"):
        import pty
        import termios

        self.master, self.slave = pty.openpty()
        self.addCleanup(os.close, self.master)
        self.addCleanup(os.close, self.slave)
        self.original_mode = termios.tcgetattr(self.slave)
        environment = {**os.environ, "TERM": term, "COLUMNS": "100", "LINES": "24",
                       "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
        self.process = subprocess.Popen([sys.executable, "-m", "openwish", *args], cwd=self.root,
                                        env=environment, stdin=self.slave, stdout=self.slave, stderr=self.slave)

        def cleanup():
            if self.process.poll() is None:
                self.process.kill()
            self.process.wait(timeout=5)

        self.addCleanup(cleanup)
        self.output = b""

    def read_until(self, text):
        deadline = time.monotonic() + 5
        while text.encode() not in self.output:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.master], [], [], max(remaining, 0))[0]:
                self.fail(f"Did not receive {text!r}: {self.output.decode(errors='replace')}")
            self.output += os.read(self.master, 65536)

    def send(self, text):
        os.write(self.master, text.encode())

    def finish(self, code=0):
        import termios

        self.assertEqual(self.process.wait(timeout=5), code, self.output.decode(errors="replace"))
        self.assertEqual(termios.tcgetattr(self.slave), self.original_mode)

    def test_arrow_space_multiselect_initializes_two_harnesses(self):
        root = self.root / "selected"
        self.start("init", str(root))
        self.read_until("Select one or more harnesses.")
        self.send(" \x1b[B \r")
        self.read_until("35 installed")
        self.finish()
        for directory in (".opencode", ".claude"):
            self.assertTrue((root / directory / "skills/ow-propose/SKILL.md").is_file())
        self.assertFalse((root / ".agents").exists())
        self.assertIn(b"\x1b[?25h", self.output)

    def test_empty_selection_requires_a_choice_and_cancel_restores_terminal(self):
        root = self.root / "cancelled"
        self.start("init", str(root))
        self.read_until("Select one or more harnesses.")
        self.send("\r")
        self.read_until("Choose at least one harness before initializing.")
        self.send("q")
        self.read_until("Cancelled.")
        self.finish(130)
        self.assertFalse(root.exists())
        self.assertIn(b"\x1b[?25h", self.output)

    def test_existing_harnesses_are_preselected_and_enter_is_noop(self):
        path = self.root / ".agents/skills/ow-propose/SKILL.md"
        before = path.read_bytes(), path.stat().st_mtime_ns
        self.start("init")
        self.read_until("[x] Generic Agent Skills")
        self.send("\r")
        self.read_until("12 unchanged")
        self.finish()
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)

    def test_interrupt_restores_terminal_without_initializing(self):
        root = self.root / "interrupted"
        self.start("init", str(root))
        self.read_until("Select one or more harnesses.")
        self.process.send_signal(signal.SIGINT)
        self.read_until("Cancelled.")
        self.finish(130)
        self.assertFalse(root.exists())
        self.assertIn(b"\x1b[?25h", self.output)

    def test_non_ansi_terminal_supports_numbered_multiple_selection(self):
        root = self.root / "numbered"
        self.start("init", str(root), term="dumb")
        self.read_until("Harnesses:")
        self.send("1, 3\n")
        self.read_until("34 installed")
        self.finish()
        self.assertTrue((root / ".opencode/commands/onboard.md").exists())
        self.assertTrue((root / ".agents/skills/ow-propose/SKILL.md").exists())
        self.assertNotIn(b"\x1b[", self.output)

    def test_downgrade_default_keeps_newer_files(self):
        with patch("openwish.integrations.__version__", "9.0.0"):
            install_skills(self.root, "opencode")
        path = self.root / ".opencode/skills/ow-propose/SKILL.md"
        before = path.read_bytes(), path.stat().st_mtime_ns
        self.start("init", "--harness", "opencode")
        self.read_until("Choice [A]:")
        self.send("\n")
        self.read_until("22 kept newer")
        self.finish()
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)

    def test_only_explicit_choice_confirms_a_downgrade(self):
        with patch("openwish.integrations.__version__", "9.0.0"):
            install_skills(self.root, "opencode")
        self.start("init", "--harness", "opencode")
        self.read_until("Choice [A]:")
        self.send("invalid\n")
        self.read_until("Enter A or B.")
        self.assertIn("9.0.0", (self.root / ".opencode/skills/ow-propose/SKILL.md").read_text())
        self.send("B\n")
        self.read_until("22 downgraded")
        self.finish()
        self.assertIn(__version__, (self.root / ".opencode/skills/ow-propose/SKILL.md").read_text())
