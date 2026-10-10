from pathlib import Path
import tempfile
import unittest

from openwish.scaffold import initialize, new_artifact
from openwish.storage import document, load_project, read_document, write_json
from openwish.workflow import record_review


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        initialize(self.root)

    def add_need(self, key="N-002"):
        new_artifact(self.root, "need", key, "Private reconciliation")
        self.edit_document(f"needs/{key}.md", actor="Operations staff", outcome="Keep records local",
                           acceptance=["No raw records leave the device"])

    def add_change(self, key="C-002", needs=("N-001",), **kwargs):
        new_artifact(self.root, "change", key, "Improve reconciliation", needs=needs, **kwargs)

    def fixture(self, *, mode="default"):
        new_artifact(self.root, "need", "N-001", "Reconcile records")
        self.edit_document("needs/N-001.md", actor="Operations staff",
                           outcome="Reconcile without retyping", acceptance=["No manual row copying"])
        self.add_change("C-001", fast_forward=mode == "fast-forward")
        self.write_tasks([self.task()])
        (self.root / "app.py").write_text("def export():\n    return []\n", encoding="utf-8")
        return self.project()

    def task(self, key="C-001/T-001", **kwargs):
        return {"id": key, "title": "Export records", "depends_on": [], "kind": "agent",
                "status": "open", "files": ["app.py"],
                "acceptance": "Exactly the requested records are exported", "evidence": "", **kwargs}

    def project(self):
        return load_project(self.root)

    def edit_document(self, relative, **kwargs):
        path = self.root / "openwish" / relative
        meta, body = read_document(path)
        path.write_text(document({**meta, **kwargs}, body), encoding="utf-8")

    def write_tasks(self, tasks, key="C-001"):
        write_json(self.root / f"openwish/changes/{key}/tasks.json", {"tasks": tasks})

    def finish_tasks(self, key="C-001"):
        self.write_tasks([self.task(f"{key}/T-001", status="done", evidence="Representative export check passed")], key)

    def review(self, key="C-001", needs=None):
        record_review(self.project(), key, "Reconciliation works",
                      ["Representative reconciliation: passed"], needs or ["N-001"], "pass")
