from __future__ import annotations

import argparse
from pathlib import Path

from shared.cli.common import build_parser, command_main, ensure_path_exists, optional_dependency_error, write_validation_report
from shared.constraints.rules import validate_dataset
from shared.schema_dsl.engine import generate_tables
from shared.schema_dsl.parser import describe_schema, load_schema

from .parquet_writer import write_parquet_tables

GENERATOR_NAME = "parquet_generator"


def _resolve_seed(schema_raw: dict, seed: int | None) -> int:
    return seed if seed is not None else int(schema_raw.get("seed", 0))


def _cmd_generate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    tables = generate_tables(schema.raw, seed=seed, rows_override=args.rows, profile=args.profile)
    parts = {n: s.get("partition_by", []) for n, s in schema.raw.get("tables", {}).items()}
    write_parquet_tables(args.out, tables, parts)
    print(f"Generated Parquet at {Path(args.out).resolve()}")
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    print(describe_schema(load_schema(args.schema)))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    import pyarrow.parquet as pq

    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    tables = generate_tables(schema.raw, seed=seed, rows_override=args.rows, profile=args.profile)

    checks: list[dict] = []
    errors: list[str] = []
    dataset_errors = validate_dataset(tables, schema.raw)
    checks.append({"name": "schema_constraints", "ok": not dataset_errors, "details": {"errors": dataset_errors}})
    errors.extend(dataset_errors)

    row_stats: dict[str, dict[str, int]] = {}
    for table_name, expected_rows in {k: len(v) for k, v in tables.items()}.items():
        flat_file = Path(args.out) / f"{table_name}.parquet"
        partition_dir = Path(args.out) / table_name
        if flat_file.exists():
            actual_rows = pq.read_table(flat_file).num_rows
            location = flat_file
        elif partition_dir.exists():
            actual_rows = pq.read_table(partition_dir).num_rows
            location = partition_dir
        else:
            ensure_path_exists(flat_file, description=f"Parquet output for {table_name}")
        row_ok = expected_rows == actual_rows
        row_stats[table_name] = {"expected": expected_rows, "actual": actual_rows}
        checks.append({"name": f"{table_name}_parseable", "ok": True, "details": {"path": str(location)}})
        checks.append({"name": f"{table_name}_row_count", "ok": row_ok, "details": row_stats[table_name]})
        if not row_ok:
            errors.append(f"Row count mismatch for {table_name}: expected {expected_rows}, got {actual_rows}")

    report = write_validation_report(
        args.out,
        generator=GENERATOR_NAME,
        schema_path=schema.path,
        output_path=args.out,
        seed=seed,
        checks=checks,
        errors=errors,
        stats={"row_counts": row_stats},
    )
    print(f"Validation report: {report}")
    return 1 if errors else 0


def main() -> None:
    command_main(
        build_parser(
            "Parquet generator",
            {"describe": _cmd_describe, "generate": _cmd_generate, "validate": _cmd_validate},
        )
    )


if __name__ == "__main__":
    try:
        import pyarrow  # noqa: F401
    except ImportError as exc:
        raise optional_dependency_error("pyarrow", "pip install -r generators/parquet_generator/requirements.txt") from exc
    main()
