"""OpenWish's deterministic CLI for needs and disposable execution."""

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .budgets import check_budgets
from .integrations import HARNESSES, install_skills, installed_harnesses
from .model import need_graph, needs_context, ready_tasks, review_needs, select_changes
from .scaffold import initialize, new_artifact
from .storage import WishError, load_project, project_config, project_root
from .terminal import confirm_downgrade, select_harnesses
from .validation import validate
from .views import status_data, summary
from .workflow import clean_changes, close_changes, record_review, set_mode


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
    check = commands.add_parser("check", help="Validate artifacts, references, task dependencies, and budgets")
    check.add_argument("--json", action="store_true")
    check.add_argument("--artifacts-only", action="store_true")
    status = commands.add_parser("status", help="Show durable needs and disposable work")
    status.add_argument("--json", action="store_true")
    context = commands.add_parser("context", help="Print all current needs, optionally with relevant changes")
    context.add_argument("selection", nargs="*", help="Need or change IDs")
    graph = commands.add_parser("graph", help="Derive reasoned need relationships; selections show incident links")
    graph.add_argument("selection", nargs="*", help="Need IDs; default all retained needs")
    graph.add_argument("--json", action="store_true")
    ready = commands.add_parser("ready", help="List ready work and blockers (readiness does not grant authority)")
    ready.add_argument("selection", nargs="*", help="Need or change IDs; default all")
    ready.add_argument("--json", action="store_true")
    report = commands.add_parser("summary", help="Show needs, outcomes, work, and verification")
    report.add_argument("selection", nargs="+", help="Need or change IDs")
    mode = commands.add_parser("mode", help="Set explicitly requested acceptance mode for one active change")
    mode.add_argument("mode", choices=("default", "fast-forward"))
    mode.add_argument("change")
    review = commands.add_parser("record-review", help="Record AI review and direct results for one change")
    review.add_argument("change")
    review.add_argument("--summary", required=True)
    review.add_argument("--check", action="append", required=True, dest="checks")
    review.add_argument("--covered-need", action="append", default=[], dest="covered")
    review.add_argument("--verdict", choices=("pass", "blocked"), default="pass")
    close = commands.add_parser("close", help="Close reviewed changes using actual human or delegated acceptance")
    close.add_argument("changes", nargs="+")
    close.add_argument("--by", choices=("human", "fast-forward"), required=True)
    clean = commands.add_parser("clean", help="Dispose closed changes and tasks after preserving useful knowledge")
    clean.add_argument("changes", nargs="+")
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


def print_installation(report):
    print("Harnesses: " + ", ".join(report["harnesses"]))
    counts = (f"{report[key]} {key.replace('_', ' ')}" for key in
              ("installed", "upgraded", "downgraded", "unchanged", "kept_newer") if report[key])
    print("Integration files: " + ", ".join(counts))


def run(args):
    if args.command == "init":
        root = (args.root or args.path).resolve()
        if (root / "openwish/config.json").exists():
            project_config(root)
        harnesses = args.harness or select_harnesses(installed_harnesses(root))
        report = initialize(root, harnesses, confirm_downgrade=confirm_downgrade)
        print(f"{'Initialized' if report['initialized'] else 'Checked'} OpenWish in {root}")
        print_installation(report)
        if report["initialized"]:
            print("Start with ow-onboard or ow-propose in your agent.")
        return 0
    root = project_root(args.root)
    project_config(root)
    if args.command == "skills":
        print_installation(install_skills(root, args.harness, confirm_downgrade=confirm_downgrade))
        return 0
    if args.command == "new":
        print(new_artifact(root, args.kind, args.id, args.title, needs=args.needs, fast_forward=args.fast_forward))
        return 0
    if args.command == "check":
        project = load_project(root)
        errors, warnings = validate(project), []
        if not errors:
            errors, warnings = check_budgets(project, code=not args.artifacts_only)
        if args.json:
            print(json.dumps({"errors": errors, "warnings": warnings}, indent=2))
        else:
            for level, messages in (("ERROR", errors), ("WARN", warnings)):
                for message in messages:
                    print(f"{level} {message}")
            print(f"{'FAIL' if errors else 'PASS'}: {len(errors)} errors, {len(warnings)} warnings")
        return 1 if errors else 0
    project = checked_project(root, code=args.command in ("record-review", "close"))
    if args.command == "status":
        data = status_data(project)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"{data['product']} — {len(data['needs'])} needs; ~{data['needs_tokens_estimate']} context tokens")
            for need in data["needs"]:
                print(f"{need['id']} [{need['currency']}] {need['title']} — active changes: "
                      + (", ".join(need["changes"]) or "none"))
            for change in data["changes"]:
                print(f"{change['id']} [{change['status']}] {change['title']} — "
                      f"{change['done']}/{change['tasks']} tasks; review: {change['review']}")
            for label, keys in data["retention"].items():
                if keys:
                    print(f"{label.replace('_', ' ').capitalize()}: {', '.join(keys)}")
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
        text = needs_context(project)
        if args.selection:
            selected = select_changes(project, args.selection)
            manifest = [{"id": cid, "needs": project["changes"][cid]["meta"]["needs"],
                         "review_needs": review_needs(project, cid),
                         "path": f"openwish/changes/{cid}/change.md"} for cid in selected]
            text += "\n# Retrieve for this work\n" + json.dumps(manifest, indent=2) + "\n"
        if len(text.splitlines()) >= 500:
            raise WishError("Context output would reach 500 lines. Narrow the work selection or compact needs.")
        print(text)
    elif args.command == "ready":
        ready, waiting = ready_tasks(project, args.selection)
        if args.json:
            print(json.dumps({"ready": ready, "waiting": waiting}, indent=2))
        else:
            for label, tasks in (("READY", ready), ("WAIT", waiting)):
                for task in tasks:
                    context = "; ".join(f"{need['id']} — {need['outcome']}" for need in task["needs"])
                    print(f"{label} {task['id']} {task['title']} — {context}")
                    if task.get("blocker"):
                        print(f"  {task['blocker']}")
            if not ready:
                print("No agent-ready work. Resolve waiting items, or review completed changes.")
    elif args.command == "summary":
        print(summary(project, args.selection))
    elif args.command == "mode":
        set_mode(project, args.change, args.mode)
        print(f"Mode {args.mode}: {args.change}")
    elif args.command == "record-review":
        record_review(project, args.change, args.summary, args.checks, args.covered, args.verdict)
        print(f"Recorded {args.verdict} review for {args.change}")
    elif args.command == "close":
        close_changes(project, args.changes, args.by)
        print("Closed " + ", ".join(args.changes) + "; current needs remain binding.")
    elif args.command == "clean":
        removed = clean_changes(project, args.changes)
        print("Disposed " + ", ".join(removed) + "; needs, code, and tests retained.")
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
