"""Controlled dirty-data injection."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Any


def apply_corruption(
    rows: list[dict[str, Any]],
    table_spec: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    """Apply reproducible corruption toggles to table rows."""

    result = [deepcopy(r) for r in rows]
    corruption = table_spec.get("corruption", {})

    missing_rate = float(corruption.get("missing_rate", 0.0))
    if missing_rate > 0:
        for row in result:
            for column in table_spec.get("columns", []):
                if column.get("constraints", {}).get("primary_key"):
                    continue
                if rng.random() < missing_rate:
                    row[column["name"]] = ""

    per_column = corruption.get("missing_by_column", {})
    for col_name, rate in per_column.items():
        for row in result:
            if rng.random() < float(rate):
                row[col_name] = ""

    outlier_rate = float(corruption.get("outlier_rate", 0.0))
    if outlier_rate > 0:
        numeric_cols = [
            c["name"]
            for c in table_spec.get("columns", [])
            if c.get("type") in {"integer", "float"}
        ]
        for row in result:
            if rng.random() < outlier_rate and numeric_cols:
                col = rng.choice(numeric_cols)
                value = row.get(col)
                if isinstance(value, (int, float)):
                    row[col] = value * rng.uniform(4.0, 10.0)

    type_noise = corruption.get("type_noise", {})
    for col_name, spec in type_noise.items():
        rate = float(spec.get("rate", 0.0))
        token = spec.get("value", "N/A")
        for row in result:
            if rng.random() < rate:
                row[col_name] = token

    duplicate_rate = float(corruption.get("duplicate_rate", 0.0))
    if duplicate_rate > 0 and result:
        duplicate_count = int(len(result) * duplicate_rate)
        for _ in range(duplicate_count):
            result.append(deepcopy(rng.choice(result)))

    return result
