"""Serializes integer cents in the exact form the parser accepts."""


def serialize(cents):
    sign = "-" if cents < 0 else ""
    return f"{sign}{abs(cents) // 100}.{abs(cents) % 100:02d}"
