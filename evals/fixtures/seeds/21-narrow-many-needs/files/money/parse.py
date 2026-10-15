"""Parses money strings into exact integer cents; the single parser for every feature."""


def parse(text):
    sign = -1 if text.strip().startswith("-") else 1
    digits = text.strip().lstrip("-").replace(",", "")
    whole, _, fraction = digits.partition(".")
    return sign * (int(whole or 0) * 100 + int((fraction + "00")[:2]))
