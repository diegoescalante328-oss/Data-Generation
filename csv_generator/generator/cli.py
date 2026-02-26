"""Command line interface for CSV dataset generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_schema
from .core import generate_dataset
from .writers import write_tables


def _cmd_generate(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    tables, order, seed = generate_dataset(schema, rows_override=args.rows, seed_override=args.seed)
    write_tables(args.out, tables, order)
    print(f"Generated dataset '{schema.raw['dataset']}' with seed={seed} at {Path(args.out).resolve()}")
    for table_name, rows in tables.items():
        print(f"  - {table_name}: {len(rows)} rows")


def _cmd_describe(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    raw = schema.raw
    print(f"Dataset: {raw['dataset']}")
    print("Tables:")
    for table_name, spec in raw["tables"].items():
        print(f"- {table_name} (rows={spec.get('rows', 'schema/override')})")
        for col in spec.get("columns", []):
            flags = []
            if col.get("constraints", {}).get("primary_key"):
                flags.append("PK")
            if col.get("constraints", {}).get("unique"):
                flags.append("UNIQUE")
            flag_str = f" [{' '.join(flags)}]" if flags else ""
            print(f"    * {col['name']}: {col.get('type', 'computed')}{flag_str}")
    if raw.get("relationships"):
        print("Relationships:")
        for rel in raw["relationships"]:
            print(
                f"- {rel['child_table']}.{rel['child_key']} -> "
                f"{rel['parent_table']}.{rel['parent_key']}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Schema-driven CSV data generator")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate CSV datasets")
    gen.add_argument("--schema", required=True, help="Path to YAML schema")
    gen.add_argument("--rows", type=int, default=None, help="Override rows for all tables")
    gen.add_argument("--seed", type=int, default=None, help="Override schema seed")
    gen.add_argument("--out", required=True, help="Output directory for CSV files")
    gen.set_defaults(func=_cmd_generate)

    describe = sub.add_parser("describe", help="Describe schema contents")
    describe.add_argument("--schema", required=True, help="Path to YAML schema")
    describe.set_defaults(func=_cmd_describe)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
