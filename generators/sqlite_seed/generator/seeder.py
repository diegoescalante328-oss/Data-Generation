from __future__ import annotations

import sqlite3
from pathlib import Path

from shared.schema_dsl.engine import generate_tables


def seed_database(schema: dict, out_file: str, seed: int, rows_override: int | None, profile: str) -> dict[str, int]:
    tables = generate_tables(schema, seed, rows_override, profile)
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(out_file)
    conn.execute("PRAGMA foreign_keys = ON;")
    from .ddl import create_table_sql

    relationships = schema.get("relationships", [])
    for tname, spec in schema.get("tables", {}).items():
        conn.execute(create_table_sql(tname, spec, relationships))
        if spec.get("indexes"):
            for idx in spec["indexes"]:
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{tname}_{idx} ON {tname}({idx});")
    for tname, rows in tables.items():
        if not rows:
            continue
        cols = list(rows[0].keys())
        q = f"INSERT INTO {tname} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
        conn.executemany(q, [tuple(r.get(c) for c in cols) for r in rows])
    conn.commit()
    counts = {k: len(v) for k, v in tables.items()}
    conn.close()
    return counts
