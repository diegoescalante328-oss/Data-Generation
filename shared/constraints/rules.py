from __future__ import annotations

import re
from typing import Any


def validate_column_value(value: Any, column: dict, seen: set[Any] | None = None) -> bool:
    cons = column.get("constraints", {})
    if cons.get("not_null") and value is None:
        return False
    if "allowed" in cons and value not in cons["allowed"]:
        return False
    if "min" in cons and value < cons["min"]:
        return False
    if "max" in cons and value > cons["max"]:
        return False
    if cons.get("pattern") and not re.match(cons["pattern"], str(value)):
        return False
    if seen is not None and value in seen:
        return False
    return True


def validate_dataset(tables: dict[str, list[dict]], schema: dict) -> list[str]:
    errors: list[str] = []
    for tname, spec in schema.get("tables", {}).items():
        rows = tables.get(tname, [])
        required = [c["name"] for c in spec.get("columns", [])]
        for i, row in enumerate(rows):
            missing = [c for c in required if c not in row]
            if missing:
                errors.append(f"{tname}[{i}] missing {missing}")
    for rel in schema.get("relationships", []):
        parent_keys = {r[rel['parent_key']] for r in tables.get(rel["parent_table"], [])}
        for row in tables.get(rel["child_table"], []):
            if row.get(rel["child_key"]) not in parent_keys:
                errors.append(f"FK violation {rel['child_table']}.{rel['child_key']}")
                break
    return errors
