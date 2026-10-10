"""Revision-bound decisions and review belong to individual needs."""

from datetime import date, datetime, timezone
import hashlib
import json

from .budgets import project_files
from .model import (GATES, IMPLEMENTATION, connected_specs, direct_specs, need_scope,
                    ready_tasks, select_needs, spec_needs)
from .storage import (WishError, contained, document, initial_state, read_json,
                      write_json, write_text)

RUNTIME_FIELDS = {"implementation", "confirmed_at", "verified_at"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def semantic(record):
    return {"meta": {k: v for k, v in record["meta"].items() if k not in RUNTIME_FIELDS},
            "body": record["body"]}


def state_path(project, key):
    return contained(project["root"], f"openwish/needs/{key}.state.json")


def review_path(project, key):
    return contained(project["root"], f"openwish/needs/{key}.review.json")


def source_fingerprint(project):
    records = {}
    for path in project_files(project["root"]):
        relative = path.relative_to(project["root"]).as_posix()
        if relative.startswith("openwish/"):
            continue
        with path.open("rb") as source:
            records[relative] = hashlib.file_digest(source, "sha256").hexdigest()
    return digest(records)


def scoped_tasks(project, keys):
    epics = need_scope(project, keys)["epics"]
    return [task for task in project["tasks"] if task["epic"] in epics]


def fingerprint(project, key, gate):
    state = project["needs"][key]["state"]
    scope = need_scope(project, [key])
    payload = {
        "need": key, "revision": state["revision"], "mode": state["mode"],
        "config": project["config"],
        "policy": contained(project["root"], "openwish/policy.md").read_text(encoding="utf-8"),
        "intent": {nid: semantic(need) for nid, need in project["needs"].items()
                   if need["meta"]["currency"] == "current" or nid == key},
    }
    if gate == "needs":
        return digest(payload)
    payload["no_work_reason"] = state["no_work_reason"]
    payload["specs"] = {sid: {"contract": semantic(project["specs"][sid]),
                              "design": semantic(project["specs"][sid]["design"])}
                        for sid in connected_specs(project, [key])}
    payload["knowledge"] = {path.relative_to(project["root"]).as_posix():
                            contained(project["root"], path.relative_to(project["root"])).read_text(encoding="utf-8")
                            for path in sorted((project["root"] / "openwish/knowledge").rglob("*")) if path.is_file()}
    if gate == "align":
        return digest(payload)
    payload["epics"] = {eid: semantic(project["epics"][eid]) for eid in scope["epics"]}
    payload["tasks"] = [{k: v for k, v in task.items() if k not in ("status", "evidence")}
                        for task in scoped_tasks(project, [key])]
    if gate == "implement":
        return digest(payload)
    payload["task_results"] = scoped_tasks(project, [key])
    payload["source"] = source_fingerprint(project)
    payload["review"] = read_json(review_path(project, key))
    return digest(payload)


def gate_valid(project, key, gate):
    state = project["needs"][key]["state"]
    for stage in GATES[:GATES.index(gate) + 1]:
        record = state["gates"].get(stage)
        if not record or (record["by"] == "fast-forward" and state["mode"] != "fast-forward"):
            return False
        if record["fingerprint"] != fingerprint(project, key, stage):
            return False
    return True


def require_gate(project, key, gate):
    if not gate_valid(project, key, gate):
        raise WishError(f"{key}: {gate} approval is missing or stale. Reconcile and record it again.")


def require_open(project, key):
    if project["needs"][key]["meta"]["implementation"] == "approved":
        raise WishError(f"{key} is approved. Reopen this need if more work is required.")


def update_implementation(project, keys, state, *, confirmed=False, verified=None):
    for key in keys:
        record = project["needs"][key]
        meta = record["meta"]
        if state:
            meta["implementation"] = state
        if confirmed:
            meta["confirmed_at"] = date.today().isoformat()
        if verified:
            meta["verified_at"] = verified[key]
        write_text(record["path"], document(meta, record["body"]))
    if state:
        for sid in direct_specs(project, keys):
            spec = project["specs"][sid]
            linked = [project["needs"][nid]["meta"] for nid in spec_needs(project, sid)]
            current = [need for need in linked if need["currency"] == "current"] or linked
            spec["meta"]["implementation"] = min((need["implementation"] for need in current), key=IMPLEMENTATION.index)
            write_text(spec["path"], document(spec["meta"], spec["body"]))


def reopen_needs(project, keys, *, fast_forward=False):
    keys = select_needs(project, keys)
    for key in keys:
        need = project["needs"][key]
        need["state"] = initial_state(fast_forward=fast_forward, revision=need["state"]["revision"] + 1)
        need["meta"]["currency"] = "current"
        write_json(state_path(project, key), need["state"])
    update_implementation(project, keys, "open")


def set_mode(project, keys, mode):
    keys = select_needs(project, keys)
    for key in keys:
        require_open(project, key)
    for key in keys:
        state = project["needs"][key]["state"]
        if state["mode"] != mode:
            state.update(mode=mode, gates={})
            write_json(state_path(project, key), state)


def review_needs(project, keys):
    result = set(select_needs(project, keys))
    for sid in connected_specs(project, keys):
        result.update(nid for nid in spec_needs(project, sid)
                      if project["needs"][nid]["meta"]["currency"] == "current")
    return sorted(result)


def authorized_tasks(project, keys):
    ready, waiting = ready_tasks(project, keys)
    authorized = []
    for task in ready:
        affected = {need["id"] for spec in task["lineage"] for need in spec["needs"]}
        required = set(keys) & affected
        required |= {nid for nid in affected if project["needs"][nid]["meta"]["currency"] == "current"
                     and project["needs"][nid]["meta"]["implementation"] != "approved"}
        missing = [nid for nid in sorted(required) if not gate_valid(project, nid, "implement")]
        if missing:
            waiting.append({**task, "blocker": "Missing or stale implementation authority: " + ", ".join(missing)})
        else:
            authorized.append(task)
    return authorized, waiting


def validate_review(project, key):
    review = read_json(review_path(project, key))
    tasks = scoped_tasks(project, [key])
    if review.get("verdict") != "pass" or any(task["status"] != "done" for task in tasks):
        raise WishError("Review is not passing, or unfinished work/manual verification remains.")
    if review.get("implementation_fingerprint") != fingerprint(project, key, "implement"):
        raise WishError("Review is stale: the approved plan changed.")
    if review.get("source_fingerprint") != source_fingerprint(project):
        raise WishError("Review is stale: repository files changed after the recorded checks.")
    if review.get("task_results_fingerprint") != digest(tasks):
        raise WishError("Review is stale: task results changed after the recorded checks.")
    try:
        datetime.fromisoformat(review.get("at", ""))
    except (ValueError, TypeError) as error:
        raise WishError("Review needs a valid verification timestamp.") from error
    checks, needs = review.get("checks"), review.get("needs")
    if not isinstance(checks, list) or not checks or not all(isinstance(x, str) and x.strip() for x in checks):
        raise WishError("Review needs direct verification results.")
    if not isinstance(needs, list) or not all(isinstance(x, str) for x in needs):
        raise WishError("Review needs an array of reviewed need IDs.")
    missing = set(review_needs(project, [key])).difference(needs)
    if missing:
        raise WishError("Review is missing affected needs: " + ", ".join(sorted(missing)))
    if not isinstance(review.get("summary"), str) or not review["summary"].strip():
        raise WishError("Review needs a concise outcome summary.")
    return review


def record_gate(project, keys, gate, by):
    keys = select_needs(project, keys)
    index = GATES.index(gate)
    pending = {}
    for key in keys:
        require_open(project, key)
        state = project["needs"][key]["state"]
        if by == "fast-forward" and state["mode"] != "fast-forward":
            raise WishError(f"{key}: fast-forward approval requires explicitly enabling that need's mode.")
        if index:
            require_gate(project, key, GATES[index - 1])
        scope = need_scope(project, [key])
        if gate == "align" and not scope["specs"] and not state["no_work_reason"].strip():
            raise WishError(f"{key}: alignment needs a linked spec design or a no_work_reason.")
        if gate == "implement" and not state["no_work_reason"].strip():
            if not scope["epics"] or any(not any(t["epic"] == eid for t in project["tasks"]) for eid in scope["epics"]):
                raise WishError(f"{key}: implementation needs epics with tasks, or a no_work_reason.")
        if gate == "review":
            validate_review(project, key)
        gates = {name: record for name, record in state["gates"].items() if GATES.index(name) < index}
        gates[gate] = {"by": by, "at": datetime.now(timezone.utc).isoformat(), "fingerprint": fingerprint(project, key, gate)}
        pending[key] = {**state, "gates": gates}
    for key, state in pending.items():
        write_json(state_path(project, key), state)
        project["needs"][key]["state"] = state
    if gate == "needs" and by == "human":
        update_implementation(project, keys, None, confirmed=True)
    if gate == "implement":
        update_implementation(project, keys, "in-progress")


def record_review(project, keys, summary, checks, needs, verdict):
    keys = select_needs(project, keys)
    if not summary.strip() or not checks or not all(check.strip() for check in checks):
        raise WishError("Provide a summary and direct check results.")
    if set(needs).difference(project["needs"]):
        raise WishError("Review contains unknown need IDs.")
    for key in keys:
        require_open(project, key)
        require_gate(project, key, "implement")
    if verdict == "pass":
        if any(task["status"] != "done" for task in scoped_tasks(project, keys)):
            raise WishError("Unfinished work remains; continue ready work before final review.")
        missing = set(review_needs(project, keys)).difference(needs)
        if missing:
            raise WishError("Review these affected needs too: " + ", ".join(sorted(missing)))
    source = source_fingerprint(project)
    for key in keys:
        record = {"verdict": verdict, "summary": summary, "checks": checks, "needs": sorted(set(needs)),
                  "implementation_fingerprint": fingerprint(project, key, "implement"),
                  "source_fingerprint": source, "task_results_fingerprint": digest(scoped_tasks(project, [key])),
                  "at": datetime.now(timezone.utc).isoformat()}
        write_json(review_path(project, key), record)
    if verdict == "pass":
        update_implementation(project, keys, "review")


def approve_needs(project, keys):
    keys = select_needs(project, keys)
    dates = {}
    for key in keys:
        require_open(project, key)
        require_gate(project, key, "review")
        dates[key] = validate_review(project, key)["at"][:10]
    update_implementation(project, keys, "approved", verified=dates)
