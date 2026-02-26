"""Core orchestration for CSV dataset generation."""

from __future__ import annotations

import random
import uuid
from datetime import date, timedelta
from typing import Any

from .config import SchemaConfig
from .constraints import validate_monotonic, validate_value
from .corruption import apply_corruption
from .distributions import numeric_distribution, random_date, random_datetime, weighted_choice
from .relationships import assign_foreign_keys, get_generation_order


class FallbackFaker:
    """Simple fallback for fake-like values when faker isn't installed."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def name(self) -> str:
        return f"User_{self.rng.randint(1000, 9999)}"

    def email(self) -> str:
        return f"user{self.rng.randint(1000, 9999)}@example.com"

    def city(self) -> str:
        return self.rng.choice(["Austin", "Seattle", "Miami", "Denver", "Boston"])

    def state(self) -> str:
        return self.rng.choice(["CA", "TX", "NY", "FL", "WA", "IL"])


def _make_faker(seed: int) -> Any:
    try:
        from faker import Faker

        fake = Faker()
        Faker.seed(seed)
        fake.seed_instance(seed)
        return fake
    except ImportError:
        return FallbackFaker(random.Random(seed))


def _evaluate_expression(expression: str, row: dict[str, Any], rng: random.Random) -> Any:
    def normal(mean: float, std: float) -> float:
        return rng.gauss(mean, std)

    def rand_days_after(start_iso: str, min_days: int, max_days: int) -> str:
        base = date.fromisoformat(str(start_iso))
        return (base + timedelta(days=rng.randint(min_days, max_days))).isoformat()

    safe_globals = {"__builtins__": {"round": round, "min": min, "max": max, "float": float, "int": int}}
    safe_locals = dict(row)
    safe_locals.update({"normal": normal, "rand_days_after": rand_days_after})
    return eval(expression, safe_globals, safe_locals)


def _generate_value(
    column: dict[str, Any],
    row_idx: int,
    rng: random.Random,
    fake: Any,
) -> Any:
    col_type = column.get("type")

    if col_type == "id":
        mode = column.get("id_mode", "int")
        start = int(column.get("start", 1))
        return start + row_idx if mode == "int" else str(uuid.UUID(int=rng.getrandbits(128)))
    if col_type == "integer":
        value = int(round(numeric_distribution(rng, column)))
        return max(int(column.get("min", value)), min(int(column.get("max", value)), value))
    if col_type == "float":
        value = float(numeric_distribution(rng, column))
        value = max(float(column.get("min", value)), min(float(column.get("max", value)), value))
        return round(value, int(column.get("round", 2)))
    if col_type == "categorical":
        categories = column.get("categories", [])
        weights = column.get("weights", [1] * len(categories))
        return weighted_choice(rng, categories, weights)
    if col_type == "boolean":
        return rng.random() < float(column.get("true_probability", 0.5))
    if col_type == "date":
        return random_date(rng, column["start"], column["end"])
    if col_type == "datetime":
        return random_datetime(rng, column["start"], column["end"])
    if col_type == "string_pattern":
        prefix = column.get("prefix", "item")
        width = int(column.get("width", 5))
        return f"{prefix}{row_idx + 1:0{width}d}"
    if col_type == "name":
        return fake.name()
    if col_type == "email":
        return fake.email()
    if col_type == "city":
        return fake.city()
    if col_type == "state":
        return fake.state()
    if col_type == "constant":
        return column.get("value")
    return ""


def _generate_table(
    table_name: str,
    table_spec: dict[str, Any],
    row_count: int,
    seed: int,
    context: dict[str, list[dict[str, Any]]],
    relationships: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    fake = _make_faker(seed)
    rows: list[dict[str, Any]] = []
    unique_trackers: dict[str, set[Any]] = {
        col["name"]: set()
        for col in table_spec.get("columns", [])
        if col.get("constraints", {}).get("unique") or col.get("constraints", {}).get("primary_key")
    }

    for row_idx in range(row_count):
        row: dict[str, Any] = {}
        for column in table_spec.get("columns", []):
            if column.get("computed"):
                continue
            name = column["name"]
            if name in row:
                continue

            for _ in range(20):
                value = _generate_value(column, row_idx, rng, fake)
                seen = unique_trackers.get(name)
                if validate_value(value, column, seen):
                    if seen is not None:
                        seen.add(value)
                    row[name] = value
                    break
            else:
                raise ValueError(f"Could not satisfy constraints for {table_name}.{name}")

        rows.append(row)

    for relationship in relationships:
        if relationship["child_table"] == table_name:
            assign_foreign_keys(rows, relationship, context[relationship["parent_table"]], rng)

    for row in rows:
        for column in table_spec.get("columns", []):
            if column.get("computed"):
                row[column["name"]] = _evaluate_expression(column["computed"], row, rng)

    monotonic_cols = [
        col["name"] for col in table_spec.get("columns", []) if col.get("constraints", {}).get("monotonic_increasing")
    ]
    for col in monotonic_cols:
        if not validate_monotonic([row[col] for row in rows]):
            raise ValueError(f"Column {table_name}.{col} is not monotonic increasing")

    return apply_corruption(rows, table_spec, rng)


def generate_dataset(
    schema: SchemaConfig,
    rows_override: int | None = None,
    seed_override: int | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[str]], int]:
    """Generate all tables according to schema."""

    raw = schema.raw
    seed = int(seed_override if seed_override is not None else raw.get("seed", 0))

    tables: dict[str, Any] = raw["tables"]
    relationships = raw.get("relationships", [])
    order = get_generation_order(tables, relationships)

    generated: dict[str, list[dict[str, Any]]] = {}
    column_order: dict[str, list[str]] = {}

    for idx, table_name in enumerate(order):
        spec = tables[table_name]
        count = int(rows_override if rows_override is not None else spec.get("rows", 100))
        table_seed = seed + idx * 10_000
        generated[table_name] = _generate_table(table_name, spec, count, table_seed, generated, relationships)
        column_order[table_name] = [col["name"] for col in spec.get("columns", [])]

    return generated, column_order, seed
