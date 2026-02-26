from __future__ import annotations

import random


def generation_order(tables: dict, relationships: list[dict]) -> list[str]:
    ordered = list(tables.keys())
    for rel in relationships:
        parent, child = rel["parent_table"], rel["child_table"]
        if ordered.index(parent) > ordered.index(child):
            ordered.remove(parent)
            ordered.insert(0, parent)
    return ordered


def apply_foreign_keys(rows: list[dict], rel: dict, parent_rows: list[dict], rng: random.Random) -> None:
    keys = [r[rel["parent_key"]] for r in parent_rows]
    for row in rows:
        row[rel["child_key"]] = rng.choice(keys)
