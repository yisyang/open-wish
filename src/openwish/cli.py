"""OpenWish's deterministic CLI, addressed by need IDs."""

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .budgets import check_budgets
from .integrations import HARNESSES, install_skills, installed_harnesses
from .model import GATES, connected_specs, need_scope, needs_context, select_needs
from .scaffold import initialize, new_artifact
from .storage import WishError, load_project, project_root
from .terminal import confirm_downgrade, select_harnesses
from .validation import validate
from .views import status_data, summary
from .workflow import (approve_needs, authorized_tasks, record_gate, record_review,
                       reopen_needs, review_needs, set_mode)


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
    new = commands.add_parser("new", help="Create a need, spec, or epic")
    new.add_argument("kind", choices=("need", "spec", "epic"))
    new.add_argument("id")
    new.add_argument("--title", required=True)
    new.add_argument("--fast-forward", action="store_true", help="Explicitly enable fast-forward for a new need")
    check = commands.add_parser("check", help="Validate links, ordering, artifact bounds, and source size")
    check.add_argument("--json", action="store_true")
    check.add_argument("--artifacts-only", action="store_true")
    status = commands.add_parser("status", help="Summarize needs, linked specs, and implementation progress")
    status.add_argument("--json", action="store_true")
    context = commands.add_parser("context", help="Print all current needs, optionally with relevant work")
    context.add_argument("needs", nargs="*")
    ready = commands.add_parser("ready", help="List authorized ready work and its need/spec context")
    ready.add_argument("needs", nargs="+")
    ready.add_argument("--json", action="store_true")
    report = commands.add_parser("summary", help="Show outcomes, specs, work, and verification for humans")
    report.add_argument("needs", nargs="+")
    reopen = commands.add_parser("reopen", help="Reopen existing need IDs; reset authority to default")
    reopen.add_argument("needs", nargs="+")
    reopen.add_argument("--fast-forward", action="store_true")
    mode = commands.add_parser("mode", help="Set explicit execution authority for selected open needs")
    mode.add_argument("mode", choices=("default", "fast-forward"))
    mode.add_argument("needs", nargs="+")
    gate = commands.add_parser("gate", help="Record a decision on selected need revisions")
    gate.add_argument("stage", choices=GATES)
    gate.add_argument("needs", nargs="+")
    gate.add_argument("--by", choices=("human", "fast-forward"), required=True)
    review = commands.add_parser("record-review", help="Record AI review results against needs")
    review.add_argument("needs", nargs="+")
    review.add_argument("--summary", required=True)
    review.add_argument("--check", action="append", required=True, dest="checks")
    review.add_argument("--covered-need", action="append", default=[], dest="covered")
    review.add_argument("--verdict", choices=("pass", "blocked"), default="pass")
    approve = commands.add_parser("approve", help="Mark reviewed needs approved while preserving currency")
    approve.add_argument("needs", nargs="+")
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
        harnesses = args.harness or select_harnesses(installed_harnesses(root))
        report = initialize(root, harnesses, confirm_downgrade=confirm_downgrade)
        print(f"{'Initialized' if report['initialized'] else 'Checked'} OpenWish in {root}")
        print_installation(report)
        if report["initialized"]:
            print("Start with ow-onboard or ow-propose in your agent.")
        return 0
    root = project_root(args.root)
    if args.command == "skills":
        print_installation(install_skills(root, args.harness, confirm_downgrade=confirm_downgrade))
        return 0
    if args.command == "new":
        print(new_artifact(root, args.kind, args.id, args.title, fast_forward=args.fast_forward))
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
    project = checked_project(root, code=args.command in ("gate", "record-review", "approve"))
    keys = select_needs(project, args.needs) if getattr(args, "needs", None) else []
    if args.command == "status":
        data = status_data(project)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"{data['product']} — {len(data['needs'])} needs; ~{data['needs_tokens_estimate']} context tokens")
            for need in data["needs"]:
                specs = ", ".join(f"{s['id']} ({s['implementation']})" for s in need["specs"]) or "none"
                print(f"{need['id']} [{need['currency']}/{need['implementation']}] {need['title']} — specs: {specs}")
    elif args.command == "context":
        text = needs_context(project)
        if keys:
            manifest = {**need_scope(project, keys), "affected_specs": connected_specs(project, keys),
                        "review_needs": review_needs(project, keys)}
            text += "\n# Retrieve for these needs\n" + json.dumps(manifest, indent=2) + "\n"
        if len(text.splitlines()) >= 500:
            raise WishError("Context output would reach 500 lines. Consolidate the working set first.")
        print(text)
    elif args.command == "ready":
        ready, waiting = authorized_tasks(project, keys)
        if args.json:
            print(json.dumps({"ready": ready, "waiting": waiting}, indent=2))
        else:
            for label, tasks in (("READY", ready), ("WAIT", waiting)):
                for task in tasks:
                    context = "; ".join(f"{spec['id']} ({spec['title']}) → " + ", ".join(
                        f"{need['id']} ({need['title']})" for need in spec["needs"]) for spec in task["lineage"])
                    print(f"{label} {task['id']} [{task['group']}.{task['order']}] {task['title']} — {context}")
                    if task.get("blocker"):
                        print(f"  {task['blocker']}")
            if not ready:
                print("No agent-ready work. Resolve waiting items, or review the needs if all work is done.")
    elif args.command == "summary":
        print(summary(project, keys))
    elif args.command == "reopen":
        reopen_needs(project, keys, fast_forward=args.fast_forward)
        print("Reopened " + ", ".join(keys) + "; retained need identity and reset revision authority.")
    elif args.command == "mode":
        set_mode(project, keys, args.mode)
        print(f"Mode {args.mode}: " + ", ".join(keys))
    elif args.command == "gate":
        record_gate(project, keys, args.stage, args.by)
        print(f"Recorded {args.stage}: {args.by} for " + ", ".join(keys))
    elif args.command == "record-review":
        record_review(project, keys, args.summary, args.checks, args.covered, args.verdict)
        print(f"Recorded {args.verdict} review for " + ", ".join(keys))
    elif args.command == "approve":
        approve_needs(project, keys)
        print("Approved implementations for " + ", ".join(keys) + "; current needs remain binding.")
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
