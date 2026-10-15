"""Builds today's watering list for a garden; the only module that reads the garden file."""

from datetime import date
import json

from watering import due_today


def todays_list(garden_path: str, today: date) -> list[str]:
    with open(garden_path, encoding="utf-8") as handle:
        plants = json.load(handle)
    return sorted(plant["name"] for plant in plants
                  if due_today(plant["species"], date.fromisoformat(plant["last_watered"]), today))
