#!/usr/bin/env python3
"""All-in-one CSV generator.

A single-file, dependency-free generator that creates realistic mixed-domain data.
Works out of the box in terminal, VS Code, and Jupyter.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

FIRST_NAMES = [
    "Olivia", "Noah", "Emma", "Liam", "Ava", "Sophia", "Mia", "Ethan", "Mason", "Lucas",
    "Amelia", "Harper", "Evelyn", "James", "Benjamin", "Henry", "Ella", "Aria", "Avery", "Scarlett",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Seattle", "Boston", "Denver", "Austin", "Atlanta",
]

COUNTRIES = ["USA", "Canada", "UK", "Germany", "France", "India", "Japan", "Australia", "Brazil", "Mexico"]

STATUSES = ["new", "active", "inactive", "paused", "cancelled"]

PRODUCTS = [
    "Laptop", "Headphones", "Keyboard", "Monitor", "Mouse", "Backpack", "Phone", "Camera", "Desk", "Chair",
]



def random_date(start_days_ago: int = 730, end_days_ago: int = 0) -> str:
    now = datetime.now()
    start = now - timedelta(days=start_days_ago)
    end = now - timedelta(days=end_days_ago)
    delta_seconds = int((end - start).total_seconds())
    timestamp = start + timedelta(seconds=random.randint(0, max(1, delta_seconds)))
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")



def generate_row(row_num: int) -> dict[str, str | int | float]:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    quantity = random.randint(1, 5)
    unit_price = round(random.uniform(8.5, 1200.0), 2)
    total = round(quantity * unit_price, 2)

    return {
        "record_id": row_num,
        "customer_id": f"CUST-{random.randint(10000, 99999)}",
        "first_name": first,
        "last_name": last,
        "email": f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@example.com",
        "city": random.choice(CITIES),
        "country": random.choice(COUNTRIES),
        "status": random.choice(STATUSES),
        "signup_ts": random_date(1800, 30),
        "last_seen_ts": random_date(30, 0),
        "product": random.choice(PRODUCTS),
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": total,
        "is_priority": random.choice([True, False]),
        "score": round(random.uniform(0, 100), 2),
    }



def generate_csv(output_path: Path, rows: int, seed: int | None = None) -> None:
    if seed is not None:
        random.seed(seed)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(generate_row(1).keys())
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for idx in range(1, rows + 1):
            writer.writerow(generate_row(idx))



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a general-purpose CSV dataset.")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows to generate (default: 1000)")
    parser.add_argument("--output", type=Path, default=Path("generated_data.csv"), help="Output CSV path")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for reproducible output")
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    if args.rows <= 0:
        raise ValueError("--rows must be > 0")

    generate_csv(output_path=args.output, rows=args.rows, seed=args.seed)
    print(f"Generated {args.rows} rows at: {args.output.resolve()}")


if __name__ == "__main__":
    main()
