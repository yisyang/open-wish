"""Renders unmatched rows for the operator; the only output channel is the local screen or file."""


def render(rows):
    return "\n".join(f"{row['source']}\t{row['date']}\t{row['amount_cents']}" for row in rows)
