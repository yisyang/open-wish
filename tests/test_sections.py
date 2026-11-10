from tests.support import ProjectCase

DOC = """# Rules

Intro.

## Opening hours

Open 9 to 5.

### Holidays

Closed.

~~~sh
# not a heading
~~~

## Fees

Ten.

## Fees

Second section with the same title.
"""


class SectionTests(ProjectCase):
    def setUp(self):
        super().setUp()
        (self.root / "docs").mkdir()
        (self.root / "docs/rules.md").write_text(DOC, encoding="utf-8")

    def test_outline_lists_anchors_and_sizes_and_skips_fenced_lines(self):
        output = self.cli("section", "docs/rules.md").stdout
        self.assertIn("docs/rules.md: ~", output)
        self.assertIn("  #opening-hours  ~", output)
        self.assertIn("    #holidays  ~", output)
        self.assertIn("#fees-1", output)
        self.assertNotIn("not-a-heading", output)

    def test_named_section_includes_its_subsections_only(self):
        output = self.cli("section", "docs/rules.md#opening-hours").stdout
        self.assertIn("Open 9 to 5.", output)
        self.assertIn("Closed.", output)
        self.assertNotIn("Ten.", output)
        self.assertIn("Second section", self.cli("section", "docs/rules.md#fees-1").stdout)

    def test_unknown_anchor_missing_file_and_escaping_path_fail(self):
        self.assertIn("ow section docs/rules.md", self.cli("section", "docs/rules.md#nope", success=False).stderr)
        self.cli("section", "docs/absent.md", success=False)
        self.cli("section", "../outside.md", success=False)
