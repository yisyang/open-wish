"""OpenWish's deterministic CLI for needs and disposable execution."""

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .budgets import check_budgets
from .context import context_data
from .integrations import HARNESSES, install_skills, installed_harnesses, require_current_cli
from .model import TASK_STATES, need_graph, ready_tasks, unplanned_changes
from .repository import project_files
from .scaffold import initialize, new_artifact
from .storage import SCHEMA_VERSION, WishError, load_project, project_config, project_root, read_json
from .terminal import confirm_downgrade, select_harnesses
from .trace import mentions, reference_warnings, trace_data
from .validation import knowledge_warnings, validate
from .views import status_data, summary
from .workflow import clean_changes, close_changes, record_review, set_mode, set_task


def parser():
    cli = argparse.ArgumentParser(prog="ow", description="OpenWish — Need-Driven Development")
    cli.add_argument("--version", action="version", version=f"OpenWish {__version__}")
    cli.add_argument("--root", type=Path, help="Project directory (also discovered from parents)")
    commands = cli.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Select harnesses and initialize or update their OW skills")
    init.add_argument("path", nargs="?", type=Path, default=Path.cwd())
    init.add_argument("--harness", choices=HARNESSES, nargs="+", action="extend",
                      help="One or more harnesses; omit for the terminal multi-select")
    skills = commands.add_parser("skills", help="Install or update skills using version-aware replacement")
    skills.add_argument("--harness", choices=HARNESSES, nargs="+", action="extend", required=True)
    new = commands.add_parser("new", help="Create a durable need or disposable change")
    new.add_argument("kind", choices=("need", "change"))
    new.add_argument("id")
    new.add_argument("--title", required=True)
    new.add_argument("--need", action="append", default=[], dest="needs", help="Need addressed by a change; repeatable")
    new.add_argument("--fast-forward", action="store_true", help="Explicitly delegate final acceptance for this change")
    new.add_argument("--after", action="append", default=[], help="Change whose result this one builds on; repeatable")
    check = commands.add_parser("check", help="Validate artifacts, references, task dependencies, and budgets")
    check.add_argument("--json", action="store_true")
    check.add_argument("--artifacts-only", action="store_true")
    status = commands.add_parser("status", help="Show durable needs and disposable work")
    status.add_argument("--json", action="store_true")
    context = commands.add_parser("context", help="Print all current needs, work state, and a retrieval manifest")
    context.add_argument("selection", nargs="*", help="Need or change IDs")
    context.add_argument("--json", action="store_true", help="Complete needs, work state and sized retrieval manifest")
    graph = commands.add_parser("graph", help="Derive reasoned need relationships; selections show incident links")
    graph.add_argument("selection", nargs="*", help="Need IDs; default all retained needs")
    graph.add_argument("--json", action="store_true")
    ready = commands.add_parser("ready", help="List ready work and blockers (readiness does not grant authority)")
    ready.add_argument("selection", nargs="*", help="Need or change IDs; default all")
    ready.add_argument("--json", action="store_true")
    task = commands.add_parser("task", help="Set one task's status and evidence")
    task.add_argument("task", help="Qualified task ID, such as C-001/T-001")
    task.add_argument("status", choices=TASK_STATES)
    task.add_argument("--evidence", help="Concise direct evidence; required to mark work done")
    trace = commands.add_parser("trace", help="Derive need → check links from IDs mentioned in code, tests and docs")
    trace.add_argument("selection", nargs="*", help="Need IDs; default all")
    trace.add_argument("--json", action="store_true")
    report = commands.add_parser("summary", help="Show needs, outcomes, work, and verification")
    report.add_argument("selection", nargs="+", help="Need or change IDs")
    mode = commands.add_parser("mode", help="Set explicitly requested acceptance mode for one active change")
    mode.add_argument("mode", choices=("default", "fast-forward"))
    mode.add_argument("change")
    review = commands.add_parser("record-review", help="Record AI review and direct results for one change")
    review.add_argument("change")
    review.add_argument("--summary", required=True)
    review.add_argument("--check", action="append", required=True, dest="checks")
    review.add_argument("--affected", nargs="+", action="extend", default=[], metavar="NEED",
                        help="Needs whose behavior this change touches besides its linked needs; "
                             "other current needs are recorded as assessed and unaffected")
    review.add_argument("--verdict", choices=("pass", "blocked"), default="pass")
    review.add_argument("--handoff", help="JSON file (or - for stdin) with a handoff array; required for passing review")
    close = commands.add_parser("close", help="Close reviewed changes using actual human or delegated acceptance")
    close.add_argument("changes", nargs="+")
    close.add_argument("--by", choices=("human", "fast-forward"), required=True)
    clean = commands.add_parser("clean", help="Dispose closed changes and tasks after preserving useful knowledge")
    clean.add_argument("changes", nargs="+")
    clean.add_argument("--dry-run", action="store_true", help="Validate disposal and preview retained destinations")
    clean.add_argument("--json", action="store_true")
    return cli


def checked_project(root, *, code=False):
    project = load_project(root)
    errors = validate(project)
    if not errors:
        budget_errors, _ = check_budgets(project, code=code)
        errors.extend(budget_errors)
    if errors:
        raise WishError("Project needs attention:\n- " + "\n- ".join(errors))
    return project


def change_line(change):
    after = f"; after {', '.join(change['after'])}" if change.get("after") else ""
    return (f"{change['id']} [{change['status']}] {change['title']} — "
            f"{change['done']}/{change['tasks']} tasks; review: {change['review']}{after}")


def readiness_lines(ready, waiting, unplanned):
    lines = []
    for default, tasks in (("READY", ready), ("WAIT", waiting)):
        for task in tasks:
            label = "ASK" if task.get("ask") else default
            needs = "; ".join(f"{need['id']} — {need['outcome']}" for need in task.get("needs", []))
            kind = " [investigate]" if task.get("kind") == "investigate" else ""
            lines.append(f"{label} {task['id']}{kind} {task['title']}" + (f" — {needs}" if needs else ""))
            if task.get("blocker"):
                lines.append(f"  {task['blocker']}")
    plannable = [change for change in unplanned if not change["waiting_on"]]
    for change in plannable:
        lines.append(f"PLAN {change['id']} {change['title']} — {', '.join(change['needs'])}")
    if plannable:
        lines.append("  Unplanned: verify prerequisites in the repository, then plan (ow-plan); "
                     "review a verification-only change directly.")
    later = [change for change in unplanned if change["waiting_on"]]
    if later:
        lines.append(f"LATER {len(later)} unplanned changes wait for predecessors: "
                     + ", ".join(change["id"] for change in later))
    asks = sum(bool(task.get("ask")) for task in waiting)
    flight = asks + sum(task.get("kind") == "investigate" and task.get("status") == "in-progress" for task in ready)
    if flight:
        lines.append(f"Investigations in flight: {flight}, {asks} awaiting a human. Keep two or three; "
                     "send ASK questions as one batch (ow-plan).")
    return lines


def print_installation(report):
    print("Harnesses: " + ", ".join(report["harnesses"]))
    counts = (f"{report[key]} {key.replace('_', ' ')}" for key in
              ("installed", "upgraded", "downgraded", "unchanged", "kept_newer") if report[key])
    print("Integration files: " + ", ".join(counts))


def handoff_input(source):
    if source is None:
        return None
    if source == "-":
        try:
            value = json.load(sys.stdin)
        except json.JSONDecodeError as error:
            raise WishError(f"Cannot read handoff JSON from stdin: {error}") from error
        if not isinstance(value, dict):
            raise WishError("Expected a JSON object with a handoff array on stdin")
    else:
        value = read_json(Path(source))
    return value.get("handoff")


def run(args):
    if args.command == "init":
        root = (args.root or args.path).resolve()
        if (root / "openwish/config.json").exists():
            project_config(root, migratable=True)
        harnesses = args.harness or select_harnesses(installed_harnesses(root))
        report = initialize(root, harnesses, confirm_downgrade=confirm_downgrade)
        print(f"{'Initialized' if report['initialized'] else 'Checked'} OpenWish in {root}")
        print_installation(report)
        if report["migration"]:
            print(f"Migrated OW schema {report['migration']['from']} to {SCHEMA_VERSION}.")
            for note in report["migration"]["notes"]:
                print(f"- {note}")
        if report["initialized"]:
            print("Start with ow-onboard or ow-propose in your agent.")
        return 0
    root = project_root(args.root)
    if args.command != "skills":  # installing handles newer files through its downgrade prompt
        require_current_cli(root)
    project_config(root)
    if args.command == "skills":
        print_installation(install_skills(root, args.harness, confirm_downgrade=confirm_downgrade))
        return 0
    if args.command == "new":
        print(new_artifact(root, args.kind, args.id, args.title, needs=args.needs,
                           fast_forward=args.fast_forward, after=args.after))
        return 0
    if args.command == "check":
        project = load_project(root)
        errors, warnings = validate(project), []
        if not errors:
            errors, warnings = check_budgets(project, code=not args.artifacts_only)
            if not args.artifacts_only and not errors:
                files = project_files(root)
                warnings.extend(reference_warnings(project, mentions(project, files)))
                warnings.extend(knowledge_warnings(project, files))
        if args.json:
            print(json.dumps({"errors": errors, "warnings": warnings}, indent=2))
        else:
            for level, messages in (("ERROR", errors), ("WARN", warnings)):
                for message in messages:
                    print(f"{level} {message}")
            print(f"{'FAIL' if errors else 'PASS'} (structure and budgets): "
                  f"{len(errors)} errors, {len(warnings)} warnings")
        return 1 if errors else 0
    project = checked_project(root, code=args.command == "close" or
                              (args.command == "record-review" and args.verdict == "pass"))
    if args.command == "status":
        data = status_data(project)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"{data['product']} — {len(data['needs'])} needs; ~{data['needs_tokens_estimate']} context tokens")
            for need in data["needs"]:
                unresolved = f"; {len(need['open'])} open" if need.get("open") else ""
                print(f"{need['id']} [{need['currency']}] {need['title']} — active changes: "
                      + (", ".join(need["changes"]) or "none") + unresolved)
            for change in data["changes"]:
                print(change_line(change))
            for label, keys in data["retention"].items():
                if keys:
                    print(f"{label.replace('_', ' ').capitalize()}: {', '.join(keys)}")
            for warning in data["repository_warnings"]:
                print("WARN " + warning)
    elif args.command == "graph":
        graph = need_graph(project, args.selection)
        if args.json:
            print(json.dumps(graph, indent=2, ensure_ascii=False))
        else:
            for need in graph["needs"]:
                print(f"{need['id']} [{need['currency']}] {need['title']}")
            for edge in graph["relations"]:
                print(f"{edge['source']} {edge['kind']} {edge['target']}: {edge['reason']}")
            print("Recorded intent links guide investigation; all current needs remain binding.")
    elif args.command == "context":
        data = context_data(project, args.selection)
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(data.pop("needs"))
            work = data.pop("work")
            lines = [change_line(change) for change in work["changes"]]
            lines += readiness_lines(work["ready"], work["waiting"], work["unplanned"])
            lines += ["WARN " + warning for warning in work["warnings"]]
            print("\n# Work (readiness is not permission)\n" + ("\n".join(lines) or "No changes."))
            print("\n# Retrieval manifest and estimated size\n" + json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == "ready":
        ready, waiting = ready_tasks(project, args.selection)
        unplanned = unplanned_changes(project, args.selection)
        if args.json:
            print(json.dumps({"ready": ready, "waiting": waiting, "unplanned": unplanned}, indent=2))
        else:
            for line in readiness_lines(ready, waiting, unplanned):
                print(line)
            if not ready:
                print("No agent-ready tasks. Inspect change scope and evidence before planning work or reviewing results.")
    elif args.command == "task":
        set_task(project, args.task, args.status, args.evidence)
        print(f"{args.task}: {args.status}")
    elif args.command == "trace":
        data = trace_data(project, project_files(root), args.selection)
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            for need in data["needs"]:
                print(f"{need['id']} [{need['currency']}] {need['title']}")
                print("  checks: " + (", ".join(need["checks"]) or "none traced"))
                if need["files"]:
                    print("  other: " + ", ".join(need["files"]))
            for warning in data["warnings"]:
                print("WARN " + warning)
            print(data["note"])
    elif args.command == "summary":
        print(summary(project, args.selection))
    elif args.command == "mode":
        set_mode(project, args.change, args.mode)
        print(f"Mode {args.mode}: {args.change}")
    elif args.command == "record-review":
        record = record_review(project, args.change, args.summary, args.checks, args.affected, args.verdict,
                               handoff=handoff_input(args.handoff))
        print(f"Recorded {args.verdict} review for {args.change}. Affected: {', '.join(record['affected'])}; "
              f"assessed unaffected: {', '.join(record['unaffected']) or 'none'}")
    elif args.command == "close":
        close_changes(project, args.changes, args.by)
        print("Closed " + ", ".join(args.changes) + "; current needs remain binding.")
    elif args.command == "clean":
        report = clean_changes(project, args.changes, dry_run=args.dry_run)
        if args.json or args.dry_run:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            for warning in report["warnings"]:
                print("WARN " + warning)
            for key, removed in report["successors"].items():
                print(f"{key}: no longer waits for {', '.join(removed)}")
            print("Disposed " + ", ".join(report["changes"]) + "; needs, code, and tests retained.")
    return 0


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return run(args)
    except (KeyboardInterrupt, EOFError):
        print("\now: Cancelled.", file=sys.stderr)
        return 130
    except (WishError, OSError) as error:
        if args.command == "check" and args.json:
            print(json.dumps({"errors": [str(error)], "warnings": []}, indent=2))
        else:
            print(f"ow: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
