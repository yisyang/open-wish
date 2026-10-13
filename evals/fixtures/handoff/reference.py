"""Evaluator-only reference for the handoff scenario's public contract, with seeded mutants.

`evals/run.py grade` substitutes `build(stage, mutant)` for the product's rules.py and
reruns the product's retained tests: they should pass on the reference and fail on
each mutant. Never copy this file into an evaluated product.
"""

from fractions import Fraction
import math

BONUSES = {
    "organic": {"cash": Fraction(1, 2), "quality": Fraction(1), "freight": Fraction(1, 2)},
    "efficiency": {"cash": Fraction(-1, 5), "quality": Fraction(1, 10), "freight": Fraction(-1, 10)},
}
MUTANTS = {
    1: ["bonus-applied-to-input-basis", "truncate-instead-of-half-up"],
    2: ["multiplicative-stacking", "efficiency-freight-minus-20-percent", "truncate-instead-of-half-up"],
}


def build(stage, mutant=None):
    known = {"organic"} if stage == 1 else {"organic", "efficiency"}
    bonuses = {name: dict(values) for name, values in BONUSES.items() if name in known}
    if mutant == "efficiency-freight-minus-20-percent":
        bonuses["efficiency"]["freight"] = Fraction(-1, 5)

    def rounded(value):
        return math.floor(value) if mutant == "truncate-instead-of-half-up" else math.floor(value + Fraction(1, 2))

    def quote(process_cash, input_basis, quality, freight, skills):
        skills = list(skills)
        if len(skills) > 3 or len(set(skills)) != len(skills) or not set(skills) <= known:
            raise ValueError("Select at most three distinct known skills.")
        bases = {"cash": process_cash, "quality": quality, "freight": freight}
        result = {}
        for component, base in bases.items():
            if mutant == "multiplicative-stacking":
                factor = Fraction(1)
                for skill in skills:
                    factor *= 1 + bonuses[skill][component]
            else:
                factor = 1 + sum((bonuses[skill][component] for skill in skills), Fraction(0))
            if component == "cash" and mutant == "bonus-applied-to-input-basis":
                result[component] = rounded((base + input_basis) * factor)
            else:
                result[component] = rounded(base * factor)
        if mutant != "bonus-applied-to-input-basis":
            result["cash"] += input_basis
        return result

    return {"quote": quote}
