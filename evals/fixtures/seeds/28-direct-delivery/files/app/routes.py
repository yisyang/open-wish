"""HTTP routes; handlers load data and render templates, rules stay in list_builder."""

from app.list_builder import build


def shopping_list(request, plan_store):
    return {"template": "list.html", "items": build(plan_store.week(request.household))}
