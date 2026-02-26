from __future__ import annotations

import hashlib
from pathlib import Path

from csv_generator.generator.config import load_schema
from csv_generator.generator.core import generate_dataset
from csv_generator.generator.writers import write_tables


def _hash_dir(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(path.glob("*.csv")):
        digest.update(file_path.name.encode("utf-8"))
        digest.update(file_path.read_bytes())
    return digest.hexdigest()


def test_same_seed_same_output(tmp_path: Path) -> None:
    schema = load_schema("csv_generator/schemas/retail_basic.yaml")

    tables1, order1, _ = generate_dataset(schema, rows_override=200, seed_override=123)
    out1 = tmp_path / "run1"
    write_tables(out1, tables1, order1)

    tables2, order2, _ = generate_dataset(schema, rows_override=200, seed_override=123)
    out2 = tmp_path / "run2"
    write_tables(out2, tables2, order2)

    assert _hash_dir(out1) == _hash_dir(out2)
