import hashlib
import json

import pytest

pq = pytest.importorskip("pyarrow.parquet")

from generators.parquet_generator.generator.cli import main


def _hash_table(path):
    data = pq.read_table(path).to_pylist()
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def test_parquet_smoke_generate_and_validate(tmp_path, monkeypatch):
    out = tmp_path / "out"
    schema = "generators/parquet_generator/schemas/retail_basic_parquet.yaml"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "22"])
    main()
    assert (out / "customers.parquet").exists()
    assert pq.read_table(out / "customers.parquet").num_rows == 10

    monkeypatch.setattr("sys.argv", ["prog", "validate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "22"])
    main()
    assert json.loads((out / "validation_report.json").read_text())["ok"] is True


def test_parquet_deterministic_seed(tmp_path, monkeypatch):
    schema = "generators/parquet_generator/schemas/retail_basic_parquet.yaml"
    out1 = tmp_path / "a"
    out2 = tmp_path / "b"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out1), "--rows", "10", "--seed", "44"])
    main()
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out2), "--rows", "10", "--seed", "44"])
    main()
    assert _hash_table(out1 / "customers.parquet") == _hash_table(out2 / "customers.parquet")
