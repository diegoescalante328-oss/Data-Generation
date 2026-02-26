"""CSV writing utilities."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def write_tables(output_dir: str | Path, tables: dict[str, list[dict[str, Any]]], column_order: dict[str, list[str]]) -> None:
    """Write one CSV file per table with deterministic column order."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for table_name, rows in tables.items():
        path = out / f"{table_name}.csv"
        fields = column_order[table_name]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fields})
