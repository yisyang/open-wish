"""Decides whether a plant is due for watering today (pure; dates and species data are passed in)."""

from datetime import date
import json
from pathlib import Path

SPECIES = json.loads((Path(__file__).with_name("species.json")).read_text(encoding="utf-8"))


def due_today(species: str, last_watered: date, today: date) -> bool:
    if species not in SPECIES:
        raise ValueError(f"Unknown species: {species!r}")
    return (today - last_watered).days >= SPECIES[species]["interval_days"]
