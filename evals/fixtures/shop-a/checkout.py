import json
import os
from pathlib import Path
import time


def checkout(items):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = (subtotal * int(os.environ.get("TAX_BPS", "1000")) + 5000) // 10000
    receipt = {"subtotal": subtotal, "tax": tax, "total": subtotal + tax,
               "at": time.time()}
    with Path("receipts.jsonl").open("a") as output:
        output.write(json.dumps(receipt) + "\n")
    return receipt
