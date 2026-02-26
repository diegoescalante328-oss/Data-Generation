from __future__ import annotations

import argparse
from pathlib import Path

from csv_generator.generator.config import load_schema
from csv_generator.generator.core import generate_dataset
from csv_generator.generator.writers import write_tables
from shared.constraints.rules import validate_dataset


def _cmd_generate(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    tables, order, seed = generate_dataset(schema, rows_override=args.rows, seed_override=args.seed)
    write_tables(args.out, tables, order)
    print(f"Generated dataset '{schema.raw['dataset']}' with seed={seed} at {Path(args.out).resolve()}")


def _cmd_describe(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    print(f"Dataset: {schema.raw['dataset']}")
    for table, spec in schema.raw["tables"].items():
        print(f"- {table}: rows={spec.get('rows', 'override')}")


def _cmd_validate(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    tables, _, _ = generate_dataset(schema, rows_override=args.rows, seed_override=args.seed)
    errors = validate_dataset(tables, schema.raw)
    if errors:
        print("Validation failed")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)
    print("Validation passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CSV generator wrapper")
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd, fn in (("generate", _cmd_generate), ("describe", _cmd_describe), ("validate", _cmd_validate)):
        p = sub.add_parser(cmd)
        p.add_argument("--schema", required=True)
        p.add_argument("--seed", type=int, default=None)
        p.add_argument("--rows", type=int, default=None)
        p.add_argument("--out", default="csv_generator/output")
        p.add_argument("--profile", default="realistic")
        p.set_defaults(func=fn)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
