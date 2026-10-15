"""Evaluation seeds stay valid OW projects, so dry runs see the records their prompts describe."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ow_eval_runner", ROOT / "evals/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class EvalSeedTests(unittest.TestCase):
    def test_every_seed_materializes_a_valid_project_with_fresh_reviews(self):
        seeded = [item for item in runner.load_evals([]) if "seed" in item]
        self.assertTrue(seeded)
        with tempfile.TemporaryDirectory() as directory:
            ow = runner.shim(Path(directory))
            for item in seeded:
                with self.subTest(eval=item["id"]):
                    work = Path(directory) / item["name"]
                    subprocess.run([str(ow), "init", str(work), "--harness", "generic"], check=True,
                                   capture_output=True, text=True, timeout=60)
                    runner.apply_seed(ROOT / item["seed"], work, ow)
                    check = subprocess.run([str(ow), "--root", str(work), "check", "--json"],
                                           capture_output=True, text=True, timeout=60)
                    self.assertEqual(json.loads(check.stdout)["errors"], [], check.stdout)
                    status = json.loads(subprocess.run([str(ow), "--root", str(work), "status", "--json"],
                                                       capture_output=True, text=True, timeout=60).stdout)
                    self.assertTrue(status["needs"])
                    for change in status["changes"]:
                        if change["status"] == "review":
                            self.assertEqual(change["review"], "fresh", change)

    def test_baselines_receive_seed_files_but_no_ow_records(self):
        item = next(item for item in runner.load_evals([]) if item.get("seed", "").endswith("28-direct-delivery"))
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            runner.apply_seed(ROOT / item["seed"], work, None)
            self.assertTrue((work / "app/list_builder.py").exists())
            self.assertFalse((work / "openwish").exists())


if __name__ == "__main__":
    unittest.main()
