import json

from pricing import price


def record(items, tax_bps, at, output):
    receipt = {**price(items, tax_bps), "at": at}
    output.write(json.dumps(receipt) + "\n")
    return receipt
