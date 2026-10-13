"""Evaluator-only reference for the lending scenario's public contract, with seeded mutants.

`evals/run.py grade` substitutes `build(stage, mutant)` for the product's lending.py and
reruns the product's retained tests. Never copy this file into an evaluated product.
"""

from datetime import date

MUTANTS = {
    1: ["charge-only-days-beyond-grace", "due-date-counts-as-late", "ignore-cap"],
    2: ["charge-only-days-beyond-grace", "ignore-cap", "reference-renewable-once", "renew-despite-hold"],
    3: ["charge-only-days-beyond-grace", "book-cap-stays-1000", "reference-renewable-once"],
    4: ["charge-only-days-beyond-grace", "book-cap-stays-1000", "dvd-without-grace", "dvd-renewable-twice"],
}


def build(stage, mutant=None):
    kinds = {
        "book": {"rate": 25, "grace": 2, "cap": 1500 if stage >= 3 else 1000, "renewals": 2},
        "reference": {"rate": 100, "grace": 0, "cap": 5000, "renewals": 0},
    }
    if stage >= 4:
        kinds["dvd"] = {"rate": 50, "grace": 1, "cap": 2000, "renewals": 1}
    if mutant == "book-cap-stays-1000":
        kinds["book"]["cap"] = 1000
    if mutant == "dvd-without-grace":
        kinds["dvd"]["grace"] = 0
    if mutant == "dvd-renewable-twice":
        kinds["dvd"]["renewals"] = 2
    if mutant == "reference-renewable-once":
        kinds["reference"]["renewals"] = 1

    def policy(kind):
        if kind not in kinds:
            raise ValueError(f"Unknown item kind: {kind!r}")
        return kinds[kind]

    def late_fee(due, returned, kind):
        rules = policy(kind)
        late = (date.fromisoformat(returned) - date.fromisoformat(due)).days
        if mutant == "due-date-counts-as-late":
            late += 1
        if late <= rules["grace"]:
            return 0
        days = late - rules["grace"] if mutant == "charge-only-days-beyond-grace" else late
        fee = days * rules["rate"]
        return fee if mutant == "ignore-cap" else min(fee, rules["cap"])

    functions = {"late_fee": late_fee}
    if stage >= 2:
        def can_renew(kind, renewals, holds):
            rules = policy(kind)
            if renewals < 0 or holds < 0:
                raise ValueError("Renewals and holds are nonnegative counts.")
            if holds and mutant != "renew-despite-hold":
                return False
            return renewals < rules["renewals"]

        functions["can_renew"] = can_renew
    return functions
