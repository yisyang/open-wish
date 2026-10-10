"""Human-facing output preserves the need → spec → execution relationship."""

from .model import GATES, direct_specs, estimate_tokens, needs_context
from .storage import WishError, read_json
from .workflow import gate_valid, review_path, scoped_tasks, validate_review


def status_data(project):
    needs = []
    for key, need in project["needs"].items():
        gates = {}
        for gate in GATES:
            record = need["state"]["gates"].get(gate)
            if need["meta"]["implementation"] == "approved":
                gates[gate] = "historical" if record else "missing"
            else:
                try:
                    valid = gate_valid(project, key, gate)
                except (OSError, WishError):
                    valid = False
                gates[gate] = "valid" if valid else ("stale" if record else "missing")
        tasks = scoped_tasks(project, [key])
        specs = [{"id": sid, "title": project["specs"][sid]["meta"]["title"],
                  "implementation": project["specs"][sid]["meta"]["implementation"]}
                 for sid in direct_specs(project, [key])]
        needs.append({**need["meta"], "mode": need["state"]["mode"], "specs": specs, "gates": gates,
                      "done": sum(t["status"] == "done" for t in tasks), "tasks": len(tasks)})
    return {"product": project["config"]["product"], "needs": needs,
            "needs_tokens_estimate": estimate_tokens(needs_context(project))}


def summary(project, keys):
    lines = []
    for key in keys:
        need = project["needs"][key]["meta"]
        lines.extend([f"{key} — {need['title']} [{need['implementation']}]", f"Outcome: {need['outcome']}"])
        for sid in direct_specs(project, [key]):
            spec = project["specs"][sid]["meta"]
            lines.append(f"Spec: {sid} — {spec['title']} [{spec['implementation']}]")
        tasks = scoped_tasks(project, [key])
        lines.append(f"Work: {sum(t['status'] == 'done' for t in tasks)}/{len(tasks)} tasks complete")
        path = review_path(project, key)
        if path.exists():
            review = read_json(path)
            lines.append(f"Result: {review.get('summary', '')}")
            try:
                validate_review(project, key)
                lines.extend(f"Verified: {check}" for check in review["checks"])
            except (OSError, WishError):
                lines.append("Verification needs refresh before acceptance.")
        lines.append("")
    return "\n".join(lines)
