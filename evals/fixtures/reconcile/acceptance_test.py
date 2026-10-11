"""Independent final-outcome checks. Run with PROJECT_DIR pointing at the output."""

import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ReconciliationTests(unittest.TestCase):
    def run_cli(self, *options):
        root = Path(os.environ["PROJECT_DIR"]).resolve()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "records.csv"
            source.write_text("date,category,cents\n2026-01-03,food,120\n"
                              "2026-01-07,food,-20\n2026-01-10,travel,300\n"
                              "2026-02-01,food,999\n", encoding="utf-8")
            return subprocess.run([sys.executable, str(root / "reconcile.py"), str(source), *options],
                                  text=True, capture_output=True, timeout=10, cwd=directory)

    def test_json_totals(self):
        result = self.run_cli("--month", "2026-01")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"food": 100, "travel": 300})

    def test_csv_totals(self):
        result = self.run_cli("--month", "2026-01", "--format", "csv")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = list(csv.DictReader(io.StringIO(result.stdout)))
        self.assertEqual({row["category"]: int(row["cents"]) for row in rows}, {"food": 100, "travel": 300})

    def test_empty_month_json(self):
        result = self.run_cli("--month", "2026-03")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})

    def test_invalid_month(self):
        result = self.run_cli("--month", "2026-99")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
