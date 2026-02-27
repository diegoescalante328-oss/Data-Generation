import hashlib
import json
import sqlite3

from generators.sqlite_seed.generator.cli import main


def _dump_table_hash(db_path, table):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
    conn.close()
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


def test_sqlite_smoke_generate_and_validate(tmp_path, monkeypatch):
    out = tmp_path / "retail.db"
    schema = "generators/sqlite_seed/schemas/retail_basic_sqlite.yaml"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "9"])
    main()

    conn = sqlite3.connect(out)
    conn.execute("PRAGMA foreign_keys = ON;")
    assert conn.execute("PRAGMA foreign_key_check;").fetchall() == []
    assert conn.execute("select count(*) from orders").fetchone()[0] == 10
    conn.close()

    monkeypatch.setattr("sys.argv", ["prog", "validate", "--schema", schema, "--out", str(out), "--rows", "10", "--seed", "9"])
    main()
    report = json.loads((tmp_path / "validation_report.json").read_text())
    assert report["ok"] is True


def test_sqlite_deterministic_seed(tmp_path, monkeypatch):
    schema = "generators/sqlite_seed/schemas/retail_basic_sqlite.yaml"
    db1 = tmp_path / "a.db"
    db2 = tmp_path / "b.db"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(db1), "--rows", "10", "--seed", "19"])
    main()
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", schema, "--out", str(db2), "--rows", "10", "--seed", "19"])
    main()
    assert _dump_table_hash(db1, "customers") == _dump_table_hash(db2, "customers")
    assert _dump_table_hash(db1, "orders") == _dump_table_hash(db2, "orders")
