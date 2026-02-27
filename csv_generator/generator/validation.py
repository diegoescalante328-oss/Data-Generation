"""Validation helpers for generated tabular data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Structured validation report."""

    valid: bool
    errors: list[str]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": self.errors, "summary": self.summary}


def _has_type(value: Any, expected: str) -> bool:
    if value is None:
        return True
    type_map = {
        "id": (int, str),
        "integer": (int,),
        "float": (int, float),
        "categorical": (str, int, float, bool),
        "boolean": (bool,),
        "date": (str,),
        "datetime": (str,),
        "string_pattern": (str,),
        "name": (str,),
        "email": (str,),
        "city": (str,),
        "state": (str,),
        "constant": (str, int, float, bool),
    }
    if expected not in type_map:
        return True
    return isinstance(value, type_map[expected])


def validate_tables(schema: dict[str, Any], tables: dict[str, list[dict[str, Any]]]) -> ValidationResult:
    """Validate generated tables for schema constraints and relationships."""

    errors: list[str] = []
    summary: dict[str, Any] = {"table_rows": {name: len(rows) for name, rows in tables.items()}}

    for table_name, table_spec in schema["tables"].items():
        rows = tables.get(table_name, [])
        columns = table_spec.get("columns", [])

        for column in columns:
            name = column["name"]
            constraints = column.get("constraints", {})
            seen: set[Any] = set()

            for idx, row in enumerate(rows):
                value = row.get(name)
                if constraints.get("not_null") and value in (None, ""):
                    errors.append(f"{table_name}.{name}[{idx}] violates not_null")
                if constraints.get("unique") or constraints.get("primary_key"):
                    if value in seen:
                        errors.append(f"{table_name}.{name}[{idx}] violates uniqueness")
                    seen.add(value)
                if "min" in constraints and value is not None and value < constraints["min"]:
                    errors.append(f"{table_name}.{name}[{idx}] below min")
                if "max" in constraints and value is not None and value > constraints["max"]:
                    errors.append(f"{table_name}.{name}[{idx}] above max")
                if "type" in column and not _has_type(value, column["type"]):
                    errors.append(
                        f"{table_name}.{name}[{idx}] has invalid type {type(value).__name__} for {column['type']}"
                    )

    for rel in schema.get("relationships", []):
        parent_rows = tables.get(rel["parent_table"], [])
        child_rows = tables.get(rel["child_table"], [])
        parent_key = rel["parent_key"]
        child_key = rel["child_key"]
        parent_values = {row[parent_key] for row in parent_rows}

        for idx, row in enumerate(child_rows):
            if row.get(child_key) not in parent_values:
                errors.append(
                    f"Relationship violation {rel['child_table']}.{child_key}[{idx}] not found in "
                    f"{rel['parent_table']}.{parent_key}"
                )

    return ValidationResult(valid=not errors, errors=errors, summary=summary)
