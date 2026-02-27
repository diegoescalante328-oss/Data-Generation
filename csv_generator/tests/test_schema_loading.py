from __future__ import annotations

from pathlib import Path

import pytest

from csv_generator.generator.config import SchemaError, load_schema


def test_load_schema_missing_file() -> None:
    with pytest.raises(SchemaError, match="Schema file not found"):
        load_schema("csv_generator/schemas/does_not_exist.yaml")


def test_load_schema_requires_mapping(tmp_path: Path) -> None:
    schema_file = tmp_path / "schema.json"
    schema_file.write_text("[1,2,3]", encoding="utf-8")

    with pytest.raises(SchemaError, match="must be a mapping"):
        load_schema(schema_file)


def test_load_schema_defaults_relationships(tmp_path: Path) -> None:
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"dataset": "d", "tables": {"t": {"columns": []}}}', encoding="utf-8")

    schema = load_schema(schema_file)

    assert schema.raw["relationships"] == []
