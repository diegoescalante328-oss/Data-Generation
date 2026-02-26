"""All-in-one, ready-to-run CSV generator.

Designed for copy/paste usage in notebooks, VS Code, or plain Python scripts.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


EVENT_TYPES = ["view", "click", "signup", "purchase", "refund"]
COUNTRIES = ["US", "CA", "UK", "DE", "IN", "BR", "AU", "JP"]
SOURCES = ["organic", "ads", "email", "social", "partner"]
DEVICES = ["mobile", "desktop", "tablet"]



def _random_timestamp(rng: random.Random, start: datetime, end: datetime) -> str:
    delta_seconds = int((end - start).total_seconds())
    point = start + timedelta(seconds=rng.randint(0, max(delta_seconds, 0)))
    return point.isoformat(timespec="seconds")


def generate_rows(rows: int = 1000, seed: int = 42) -> list[dict[str, Any]]:
    """Generate generic analytics-style rows for quick experimentation."""

    rng = random.Random(seed)
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31, 23, 59, 59)

    data: list[dict[str, Any]] = []
    for idx in range(rows):
        user_id = rng.randint(1, max(10, rows // 8))
        session_id = f"s_{user_id}_{rng.randint(1, max(2, rows // 20))}"
        event_type = rng.choices(EVENT_TYPES, weights=[45, 30, 10, 12, 3], k=1)[0]
        amount = 0.0
        if event_type in {"purchase", "refund"}:
            amount = round(rng.uniform(5.0, 500.0), 2)
            if event_type == "refund":
                amount *= -1

        row = {
            "event_id": idx + 1,
            "event_time": _random_timestamp(rng, start, end),
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "country": rng.choice(COUNTRIES),
            "source": rng.choice(SOURCES),
            "device": rng.choice(DEVICES),
            "amount": amount,
            "is_premium_user": rng.random() < 0.2,
        }
        data.append(row)

    data.sort(key=lambda r: r["event_time"])
    return data


def write_csv(rows: list[dict[str, Any]], out_path: str) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return out


def generate_csv(rows: int = 1000, seed: int = 42, out: str = "all-in-one/output/generated_data.csv") -> Path:
    generated = generate_rows(rows=rows, seed=seed)
    return write_csv(generated, out)


def main() -> None:
    parser = argparse.ArgumentParser(description="All-in-one ready CSV generator")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--out", default="all-in-one/output/generated_data.csv", help="Output CSV path")
    args = parser.parse_args()

    path = generate_csv(rows=args.rows, seed=args.seed, out=args.out)
    print(f"Generated CSV: {path}")


if __name__ == "__main__":
    main()
