"""Shipped guidance stays within a word budget: every sentence costs context in every user's project."""

from pathlib import Path
import unittest

SKILLS = Path(__file__).resolve().parents[1] / "src/openwish/assets/skills"
TOTAL_WORDS = 12_800
LARGEST_FILE_WORDS = 2_400


class GuidanceBudgetTests(unittest.TestCase):
    def test_skills_stay_within_their_word_budget(self):
        counts = {path.relative_to(SKILLS).as_posix(): len(path.read_text(encoding="utf-8").split())
                  for path in sorted(SKILLS.rglob("*.md"))}
        self.assertEqual(len(counts), 12, "eleven skills plus the artifact reference")
        total = sum(counts.values())
        self.assertLessEqual(total, TOTAL_WORDS,
                             f"Skills hold {total} words; cut or merge guidance before adding more (CONTRIBUTING.md).")
        for name, words in counts.items():
            self.assertLessEqual(words, LARGEST_FILE_WORDS, f"{name} holds {words} words; split or trim it.")


if __name__ == "__main__":
    unittest.main()
