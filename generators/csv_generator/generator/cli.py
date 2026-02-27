from __future__ import annotations

import argparse
import csv
from pathlib import Path

from csv_generator.generator.config import load_schema
from csv_generator.generator.core import generate_dataset
from csv_generator.generator.writers import write_tables
from shared.cli.common import build_parser, command_main, ensure_path_exists, write_validation_report
from shared.constraints.rules import validate_dataset

GENERATOR_NAME = "csv_generator_wrapper"


def _cmd_generate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    tables, order, seed = generate_dataset(schema, rows_override=args.rows, seed_override=args.seed)
    write_tables(args.out, tables, order)
    print(f"Generated dataset '{schema.raw['dataset']}' with seed={seed} at {Path(args.out).resolve()}")
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    print(f"Dataset: {schema.raw['dataset']}")
    for table, spec in schema.raw["tables"].items():
        print(f"- {table}: rows={spec.get('rows', 'override')}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    tables, _, seed = generate_dataset(schema, rows_override=args.rows, seed_override=args.seed)
    errors: list[str] = []
    checks: list[dict] = []

    dataset_errors = validate_dataset(tables, schema.raw)
    checks.append({"name": "schema_constraints", "ok": not dataset_errors, "details": {"errors": dataset_errors}})
    errors.extend(dataset_errors)

    table_counts: dict[str, int] = {}
    for table_name, expected_rows in {k: len(v) for k, v in tables.items()}.items():
        table_path = Path(args.out) / f"{table_name}.csv"
        ensure_path_exists(table_path, description=f"CSV output for {table_name}")
        with table_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        table_counts[table_name] = len(rows)
        row_ok = len(rows) == expected_rows
        checks.append({"name": f"{table_name}_row_count", "ok": row_ok, "details": {"expected": expected_rows, "actual": len(rows)}})
        if not row_ok:
            errors.append(f"Row count mismatch for {table_name}: expected {expected_rows}, got {len(rows)}")

    report = write_validation_report(
        args.out,
        generator=GENERATOR_NAME,
        schema_path=schema.path,
        output_path=args.out,
        seed=seed,
        checks=checks,
        errors=errors,
        stats={"table_counts": table_counts},
    )
    print(f"Validation report: {report}")
    return 1 if errors else 0


def main() -> None:
    command_main(
        build_parser(
            "CSV generator wrapper",
            {"describe": _cmd_describe, "generate": _cmd_generate, "validate": _cmd_validate},
        )
    )


if __name__ == "__main__":
    main()
