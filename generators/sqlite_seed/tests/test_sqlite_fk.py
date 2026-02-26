import sqlite3

from generators.sqlite_seed.generator.cli import main


def test_sqlite_fk(tmp_path, monkeypatch):
    out = tmp_path / "retail.db"
    monkeypatch.setattr("sys.argv", ["prog", "generate", "--schema", "generators/sqlite_seed/schemas/retail_basic_sqlite.yaml", "--out", str(out)])
    main()
    conn = sqlite3.connect(out)
    conn.execute("PRAGMA foreign_keys = ON;")
    assert conn.execute("PRAGMA foreign_key_check;").fetchall() == []
    assert conn.execute("select count(*) from orders").fetchone()[0] > 0
    conn.close()
