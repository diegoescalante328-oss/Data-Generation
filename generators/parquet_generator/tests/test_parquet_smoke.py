import pytest

pq = pytest.importorskip("pyarrow.parquet")

from generators.parquet_generator.generator.cli import main


def test_parquet_smoke(tmp_path, monkeypatch):
    out = tmp_path / "out"
    monkeypatch.setattr(
        "sys.argv",
        ["prog", "generate", "--schema", "generators/parquet_generator/schemas/retail_basic_parquet.yaml", "--out", str(out)],
    )
    main()
    assert (out / "customers.parquet").exists()
    assert pq.read_table(out / "customers.parquet").num_rows > 0
