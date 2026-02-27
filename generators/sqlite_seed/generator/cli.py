from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from shared.cli.common import build_parser, command_main, ensure_path_exists, write_validation_report
from shared.schema_dsl.parser import describe_schema, load_schema

from .seeder import seed_database

GENERATOR_NAME = "sqlite_seed"


def _resolve_seed(schema_raw: dict, seed: int | None) -> int:
    return seed if seed is not None else int(schema_raw.get("seed", 0))


def _cmd_generate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    counts = seed_database(schema.raw, args.out, seed, args.rows, args.profile)
    print(f"Generated SQLite database at {Path(args.out).resolve()} with row counts {counts}")
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    print(describe_schema(load_schema(args.schema)))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    db_path = Path(args.out)
    ensure_path_exists(db_path, description="SQLite database")

    checks: list[dict] = []
    errors: list[str] = []
    counts: dict[str, int] = {}

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    fk_ok = not violations
    checks.append({"name": "foreign_key_integrity", "ok": fk_ok, "details": {"violations": violations}})
    if violations:
        errors.append(f"Foreign key violations: {violations}")

    for table_name, spec in schema.raw.get("tables", {}).items():
        row_count = int(conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])
        counts[table_name] = row_count
        expected = int(args.rows if args.rows is not None else spec.get("rows", 100))
        row_ok = row_count == expected
        checks.append({"name": f"{table_name}_row_count", "ok": row_ok, "details": {"expected": expected, "actual": row_count}})
        if not row_ok:
            errors.append(f"Row count mismatch for {table_name}: expected {expected}, got {row_count}")
    conn.close()

    report = write_validation_report(
        db_path.parent,
        generator=GENERATOR_NAME,
        schema_path=schema.path,
        output_path=db_path,
        seed=seed,
        checks=checks,
        errors=errors,
        stats={"table_counts": counts},
    )
    print(f"Validation report: {report}")
    if not errors:
        print("Validation passed")
    return 1 if errors else 0


def main() -> None:
    command_main(
        build_parser(
            "SQLite seeder",
            {"describe": _cmd_describe, "generate": _cmd_generate, "validate": _cmd_validate},
        )
    )


if __name__ == "__main__":
    main()
