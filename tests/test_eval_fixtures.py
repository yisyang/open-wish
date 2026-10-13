import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

FIXTURES = Path(__file__).resolve().parents[1] / "evals/fixtures"
SCENARIOS = {"handoff": "rules.py", "lending": "lending.py"}


class EvalFixtureTests(unittest.TestCase):
    """Evaluator references must satisfy the acceptance checks; every seeded mutant must not."""

    def acceptance(self, fixture, target, stage, mutant):
        reference = FIXTURES / fixture / "reference.py"
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / target).write_text(
                "import importlib.util as _util\n"
                f"_spec = _util.spec_from_file_location('reference', {str(reference)!r})\n"
                "_module = _util.module_from_spec(_spec)\n_spec.loader.exec_module(_module)\n"
                f"globals().update(_module.build({stage}, {mutant!r}))\n", encoding="utf-8")
            environment = {**os.environ, "PROJECT_DIR": directory, "STAGE": str(stage)}
            return subprocess.run([sys.executable, str(FIXTURES / fixture / "acceptance_test.py")],
                                  env=environment, capture_output=True, text=True, timeout=60)

    def test_references_pass_and_mutants_fail_each_stage(self):
        for fixture, target in SCENARIOS.items():
            spec = importlib.util.spec_from_file_location(f"{fixture}_reference", FIXTURES / fixture / "reference.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for stage, mutants in module.MUTANTS.items():
                with self.subTest(fixture=fixture, stage=stage):
                    result = self.acceptance(fixture, target, stage, None)
                    self.assertEqual(result.returncode, 0, result.stderr)
                for mutant in mutants:
                    with self.subTest(fixture=fixture, stage=stage, mutant=mutant):
                        self.assertNotEqual(self.acceptance(fixture, target, stage, mutant).returncode, 0)


if __name__ == "__main__":
    unittest.main()
