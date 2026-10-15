"""Pure matching of statement rows against ledger rows by date and exact cents."""


def unmatched(statement, ledger):
    remaining = list(ledger)
    missing = []
    for row in statement:
        key = (row["date"], row["amount_cents"])
        hit = next((entry for entry in remaining if (entry["date"], entry["amount_cents"]) == key), None)
        if hit is None:
            missing.append({**row, "source": "statement"})
        else:
            remaining.remove(hit)
    return missing + [{**entry, "source": "ledger"} for entry in remaining]
