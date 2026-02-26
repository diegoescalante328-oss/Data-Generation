"""Constraint validation for generated rows."""

from __future__ import annotations

import re
from typing import Any


def validate_value(value: Any, column: dict[str, Any], seen_values: set[Any] | None = None) -> bool:
    """Validate single value against constraints."""

    constraints = column.get("constraints", {})
    if constraints.get("not_null", False) and value in (None, ""):
        return False
    if "allowed_values" in constraints and value not in constraints["allowed_values"]:
        return False
    if isinstance(value, (int, float)):
        if "min" in constraints and value < constraints["min"]:
            return False
        if "max" in constraints and value > constraints["max"]:
            return False
    if "pattern" in constraints and not re.fullmatch(constraints["pattern"], str(value)):
        return False
    if constraints.get("unique", False) and seen_values is not None and value in seen_values:
        return False
    return True


def validate_monotonic(values: list[Any]) -> bool:
    """Check if values are monotonically increasing."""

    return all(values[idx] <= values[idx + 1] for idx in range(len(values) - 1))
