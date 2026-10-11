import os
from pathlib import Path
import time

from receipts import record


def checkout(items):
    with Path("receipts.jsonl").open("a") as output:
        return record(items, int(os.environ.get("TAX_BPS", "1000")), time.time(), output)


def process(baskets):
    tax_bps = int(os.environ.get("TAX_BPS", "1000"))
    with Path("receipts.jsonl").open("a") as output:
        return [record(items, tax_bps, time.time(), output)["total"] for items in baskets]
