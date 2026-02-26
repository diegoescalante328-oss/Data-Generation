"""Distribution helpers used by schema-driven value generation."""

from __future__ import annotations

import math
import random
from datetime import date, datetime, timedelta
from typing import Any, Sequence


def _coerce_date(value: str) -> date:
    return date.fromisoformat(value)


def _coerce_datetime(value: str) -> datetime:
    value = value.replace("Z", "+00:00") if value.endswith("Z") else value
    return datetime.fromisoformat(value)


def numeric_distribution(rng: random.Random, spec: dict[str, Any]) -> float:
    """Generate numeric value from supported distributions."""

    dist = spec.get("distribution", "uniform")
    if dist == "uniform":
        return rng.uniform(float(spec.get("min", 0)), float(spec.get("max", 1)))
    if dist == "normal":
        return rng.gauss(float(spec.get("mean", 0)), float(spec.get("std", 1)))
    if dist == "lognormal":
        return rng.lognormvariate(float(spec.get("mean", 0)), float(spec.get("sigma", 1)))
    if dist == "poisson":
        lam = float(spec.get("lambda", 5))
        l_val = math.exp(-lam)
        k = 0
        p = 1.0
        while p > l_val:
            k += 1
            p *= rng.random()
        return float(k - 1)
    raise ValueError(f"Unsupported distribution: {dist}")


def weighted_choice(rng: random.Random, values: Sequence[Any], weights: Sequence[float]) -> Any:
    """Choose a value from weights using deterministic RNG."""

    if len(values) != len(weights):
        raise ValueError("values and weights must have the same length")
    return rng.choices(list(values), weights=list(weights), k=1)[0]


def random_date(rng: random.Random, start: str, end: str) -> str:
    """Generate random date in ISO format."""

    start_date = _coerce_date(start)
    end_date = _coerce_date(end)
    delta = (end_date - start_date).days
    return (start_date + timedelta(days=rng.randint(0, max(delta, 0)))).isoformat()


def random_datetime(rng: random.Random, start: str, end: str) -> str:
    """Generate random datetime in ISO format."""

    start_dt = _coerce_datetime(start)
    end_dt = _coerce_datetime(end)
    seconds = int((end_dt - start_dt).total_seconds())
    return (start_dt + timedelta(seconds=rng.randint(0, max(seconds, 0)))).isoformat()
