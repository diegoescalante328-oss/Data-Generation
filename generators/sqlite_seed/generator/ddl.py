from __future__ import annotations


def create_table_sql(name: str, spec: dict, relationships: list[dict]) -> str:
    cols = []
    for col in spec.get("columns", []):
        ctype = col.get("sqlite_type", "INTEGER" if col.get("type") in {"id", "integer", "boolean"} else "TEXT")
        constraints = []
        if col.get("constraints", {}).get("primary_key"):
            constraints.append("PRIMARY KEY")
        if col.get("constraints", {}).get("not_null"):
            constraints.append("NOT NULL")
        cols.append(f"{col['name']} {ctype} {' '.join(constraints)}".strip())
    for rel in relationships:
        if rel["child_table"] == name:
            cols.append(f"FOREIGN KEY ({rel['child_key']}) REFERENCES {rel['parent_table']}({rel['parent_key']})")
    return f"CREATE TABLE IF NOT EXISTS {name} ({', '.join(cols)});"
