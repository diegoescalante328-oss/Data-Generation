from __future__ import annotations

from typing import Any

from shared.constraints.rules import validate_column_value
from shared.corruption.profiles import apply_profile
from shared.distributions.generators import generate_value
from shared.io.rng import derive_rng
from shared.relationships.fk import apply_foreign_keys, generation_order


def generate_tables(raw_schema: dict[str, Any], seed: int, rows_override: int | None = None, profile: str = "realistic") -> dict[str, list[dict]]:
    tables = raw_schema.get("tables", {})
    relationships = raw_schema.get("relationships", [])
    results: dict[str, list[dict]] = {}
    for table_name in generation_order(tables, relationships):
        spec = tables[table_name]
        rng = derive_rng(seed, table_name)
        row_count = int(rows_override if rows_override is not None else spec.get("rows", 100))
        unique_sets = {c["name"]: set() for c in spec.get("columns", []) if c.get("constraints", {}).get("unique")}
        rows: list[dict] = []
        for idx in range(row_count):
            row = {}
            for col in spec.get("columns", []):
                for _ in range(10):
                    val = generate_value(col, idx, rng)
                    if validate_column_value(val, col, unique_sets.get(col["name"])):
                        if col["name"] in unique_sets:
                            unique_sets[col["name"]].add(val)
                        row[col["name"]] = val
                        break
            rows.append(row)
        for rel in relationships:
            if rel["child_table"] == table_name:
                apply_foreign_keys(rows, rel, results[rel["parent_table"]], rng)
        results[table_name] = apply_profile(rows, profile, rng)
    return results
