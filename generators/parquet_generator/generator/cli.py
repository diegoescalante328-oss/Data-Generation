from __future__ import annotations

import argparse
from pathlib import Path

from shared.constraints.rules import validate_dataset
from shared.io.reporting import write_validation_report
from shared.schema_dsl.engine import generate_tables
from shared.schema_dsl.parser import describe_schema, load_schema
from .parquet_writer import write_parquet_tables


def _cmd_generate(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    seed = args.seed if args.seed is not None else schema.raw.get("seed", 0)
    tables = generate_tables(schema.raw, seed=seed, rows_override=args.rows, profile=args.profile)
    parts = {n: s.get("partition_by", []) for n, s in schema.raw.get("tables", {}).items()}
    write_parquet_tables(args.out, tables, parts)
    print(f"Generated Parquet to {Path(args.out).resolve()}")


def _cmd_describe(args: argparse.Namespace) -> None:
    print(describe_schema(load_schema(args.schema)))


def _cmd_validate(args: argparse.Namespace) -> None:
    import pyarrow.parquet as pq

    schema = load_schema(args.schema)
    seed = args.seed if args.seed is not None else schema.raw.get("seed", 0)
    tables = generate_tables(schema.raw, seed=seed, rows_override=args.rows, profile=args.profile)
    errors = validate_dataset(tables, schema.raw)
    for table_name in schema.raw.get("tables", {}):
        p = Path(args.out) / f"{table_name}.parquet"
        if p.exists() and pq.read_table(p).num_rows < 1:
            errors.append(f"{table_name} has no rows")
    report = write_validation_report(args.out, errors, {t: len(r) for t, r in tables.items()})
    print(f"Validation report: {report}")
    if errors:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parquet generator")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("generate", _cmd_generate), ("describe", _cmd_describe), ("validate", _cmd_validate)):
        p = sub.add_parser(name)
        p.add_argument("--schema", required=True)
        p.add_argument("--seed", type=int, default=None)
        p.add_argument("--out", required=True)
        p.add_argument("--rows", type=int, default=None)
        p.add_argument("--profile", choices=["fast", "realistic", "dirty"], default="realistic")
        p.set_defaults(func=fn)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
