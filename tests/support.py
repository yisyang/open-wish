from pathlib import Path
import tempfile
import unittest

from openwish.scaffold import initialize, new_artifact
from openwish.storage import document, load_project, read_document, read_json, write_json
from openwish.workflow import record_gate, record_review


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        initialize(self.root)

    def fixture(self, *, mode="default"):
        for kind, key, title in (("need", "N-001", "Reconcile records"),
                                 ("spec", "S-001", "Export records"),
                                 ("epic", "E-001", "Add export")):
            new_artifact(self.root, kind, key, title, fast_forward=kind == "need" and mode == "fast-forward")
        self.edit_document("needs/N-001.md", actor="Operations staff",
                           outcome="Reconcile without retyping", acceptance=["No manual row copying"])
        self.edit_document("specs/S-001/design.md", needs=["N-001"])
        self.edit_document("epics/E-001/design.md", specs=["S-001"])
        self.write_tasks([self.task()])
        (self.root / "app.py").write_text("def export():\n    return []\n", encoding="utf-8")
        return self.project()

    def task(self, key="E-001/T-001", **kwargs):
        return {"id": key, "title": "Export records", "group": 1, "order": 1,
                "depends_on": [], "kind": "agent", "status": "open", "files": ["app.py"],
                "acceptance": "Exactly the requested records are exported", "evidence": "", **kwargs}

    def project(self):
        return load_project(self.root)

    def edit_document(self, relative, **kwargs):
        path = self.root / "openwish" / relative
        meta, body = read_document(path)
        path.write_text(document({**meta, **kwargs}, body), encoding="utf-8")

    def edit_state(self, key="N-001", **kwargs):
        path = self.root / f"openwish/needs/{key}.state.json"
        value = read_json(path)
        write_json(path, {**value, **kwargs})

    def write_tasks(self, tasks):
        write_json(self.root / "openwish/epics/E-001/tasks.json", {"tasks": tasks})

    def approve(self, through="implement", by="human"):
        for gate in ("needs", "align", "implement", "review"):
            record_gate(self.project(), ["N-001"], gate, by)
            if gate == through:
                break

    def finish_tasks(self):
        self.write_tasks([self.task(status="done", evidence="Representative export check passed")])

    def review(self):
        record_review(self.project(), ["N-001"], "Reconciliation works",
                      ["Representative reconciliation: passed"], ["N-001"], "pass")
