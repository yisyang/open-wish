"""Builds the merged shopping list for a week's meal plan (pure)."""


def build(meals):
    merged = {}
    for meal in meals:
        for item in meal["ingredients"]:
            key = (item["name"], item["unit"])
            merged[key] = merged.get(key, 0) + item["quantity"]
    return [{"name": n, "unit": u, "quantity": q} for (n, u), q in sorted(merged.items())]
