from __future__ import annotations

from pathlib import Path

from csv_generator.generator.config import load_schema
from csv_generator.generator.core import generate_dataset
from csv_generator.generator.writers import write_tables


def test_smoke_generate_tiny_schema(tmp_path: Path) -> None:
    schema_file = tmp_path / "tiny.json"
    schema_file.write_text(
        """
{
  "dataset": "tiny",
  "seed": 7,
  "tables": {
    "users": {
      "rows": 3,
      "columns": [
        {"name": "id", "type": "id", "constraints": {"primary_key": true, "unique": true}},
        {"name": "age", "type": "integer", "min": 18, "max": 65, "constraints": {"not_null": true}}
      ]
    }
  }
}
""".strip(),
        encoding="utf-8",
    )

    schema = load_schema(schema_file)
    tables, order, _ = generate_dataset(schema)
    out_dir = tmp_path / "out"
    write_tables(out_dir, tables, order)

    assert (out_dir / "users.csv").exists()
    assert len(tables["users"]) == 3
