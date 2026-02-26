from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any


def _choice(rng: random.Random, values: list[Any], weights: list[float] | None = None) -> Any:
    if not weights:
        return rng.choice(values)
    return rng.choices(values, weights=weights, k=1)[0]


def generate_value(column: dict[str, Any], idx: int, rng: random.Random) -> Any:
    ctype = column.get("type", "string")
    if ctype == "id":
        return idx + int(column.get("start", 1))
    if ctype == "integer":
        return rng.randint(int(column.get("min", 0)), int(column.get("max", 100)))
    if ctype == "float":
        low, high = float(column.get("min", 0)), float(column.get("max", 1))
        return round(rng.uniform(low, high), int(column.get("round", 2)))
    if ctype == "categorical":
        return _choice(rng, column.get("categories", ["unknown"]), column.get("weights"))
    if ctype == "boolean":
        return rng.random() < float(column.get("true_probability", 0.5))
    if ctype == "datetime":
        start = datetime.fromisoformat(column["start"])
        end = datetime.fromisoformat(column["end"])
        delta = int((end - start).total_seconds())
        return (start + timedelta(seconds=rng.randint(0, max(delta, 0)))).isoformat()
    if ctype == "date":
        start = datetime.fromisoformat(column["start"]).date()
        end = datetime.fromisoformat(column["end"]).date()
        days = (end - start).days
        return (start + timedelta(days=rng.randint(0, max(days, 0)))).isoformat()
    if ctype == "string":
        return f"{column.get('prefix', 'value')}_{idx}"
    if ctype == "object":
        obj = {}
        for field in column.get("fields", []):
            include_prob = float(field.get("probability", 1.0))
            if rng.random() <= include_prob:
                obj[field["name"]] = generate_value(field, idx, rng)
        return obj
    return column.get("value", "")
