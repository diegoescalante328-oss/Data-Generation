"""Relationship helpers for foreign keys and cardinality."""

from __future__ import annotations

import random
from typing import Any


def get_generation_order(tables: dict[str, Any], relationships: list[dict[str, Any]]) -> list[str]:
    """Topologically order tables so parents generate before children."""

    deps: dict[str, set[str]] = {name: set() for name in tables}
    for rel in relationships:
        deps[rel["child_table"]].add(rel["parent_table"])

    ordered: list[str] = []
    ready = [table for table, parents in deps.items() if not parents]
    while ready:
        table = ready.pop(0)
        ordered.append(table)
        for other, parents in deps.items():
            if table in parents:
                parents.remove(table)
                if not parents and other not in ordered and other not in ready:
                    ready.append(other)

    if len(ordered) != len(tables):
        raise ValueError("Relationship graph contains a cycle")
    return ordered


def assign_foreign_keys(
    child_rows: list[dict[str, Any]],
    relationship: dict[str, Any],
    parent_rows: list[dict[str, Any]],
    rng: random.Random,
) -> None:
    """Assign FK and optional lookup columns to child rows."""

    parent_key = relationship["parent_key"]
    child_key = relationship["child_key"]
    min_children = int(relationship.get("min_children", 0))
    max_children = int(relationship.get("max_children", max(1, len(child_rows))))

    key_pool: list[Any] = []
    for parent in parent_rows:
        repeats = rng.randint(min_children, max_children)
        key_pool.extend([parent[parent_key]] * repeats)

    if not key_pool:
        key_pool = [parent[parent_key] for parent in parent_rows]

    while len(key_pool) < len(child_rows):
        key_pool.append(rng.choice(key_pool))
    rng.shuffle(key_pool)

    parent_index = {row[parent_key]: row for row in parent_rows}
    lookup_cols: dict[str, str] = relationship.get("lookup_columns", {})

    for idx, row in enumerate(child_rows):
        fk_value = key_pool[idx]
        row[child_key] = fk_value
        parent_row = parent_index[fk_value]
        for parent_col, child_col in lookup_cols.items():
            row[child_col] = parent_row[parent_col]
