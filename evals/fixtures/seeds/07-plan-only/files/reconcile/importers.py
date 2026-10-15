"""Statement importers: turn a supported file into ledger-comparable rows (CSV today)."""

import csv


def import_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return [{"date": row["date"], "amount_cents": int(row["amount_cents"]), "memo": row["memo"]}
                for row in csv.DictReader(handle)]
