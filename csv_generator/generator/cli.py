"""Command line interface for CSV dataset generation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .config import SchemaError, load_schema
from .core import generate_dataset
from .validation import validate_tables
from .writers import write_tables


def _resolve_path(value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else (Path.cwd() / path).resolve()


def _cmd_generate(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    if args.out is None:
        raise ValueError("--out is required for generate")
    out_dir = _resolve_path(args.out)
    assert out_dir is not None

    tables, order, seed = generate_dataset(schema, rows_override=args.rows, seed_override=args.seed)
    write_tables(out_dir, tables, order)
    print(f"Generated dataset '{schema.raw['dataset']}' with seed={seed} at {out_dir}")
    for table_name, rows in tables.items():
        print(f"  - {table_name}: {len(rows)} rows")


def _cmd_describe(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    raw = schema.raw
    print(f"Dataset: {raw['dataset']}")
    print(f"Schema: {schema.path}")
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
            print(f"- {rel['child_table']}.{rel['child_key']} -> {rel['parent_table']}.{rel['parent_key']}")


def _cmd_validate(args: argparse.Namespace) -> None:
    schema = load_schema(args.schema)
    tables, _, _ = generate_dataset(schema, rows_override=args.rows, seed_override=args.seed)
    result = validate_tables(schema.raw, tables)

    report_text = json.dumps(result.to_dict(), indent=2)
    out_path = _resolve_path(args.out) if args.out else (schema.path.parent / f"{schema.raw['dataset']}_validation_report.json")
    assert out_path is not None

    if out_path.suffix:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report_text + "\n", encoding="utf-8")
    else:
        out_path.mkdir(parents=True, exist_ok=True)
        (out_path / "validation_report.json").write_text(report_text + "\n", encoding="utf-8")

    print(report_text)
    if not result.valid:
        raise ValueError(f"Validation failed with {len(result.errors)} issue(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Schema-driven CSV data generator")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--schema", required=True, help="Path to schema file (YAML or JSON)")
    common.add_argument("--out", default=None, help="Output path")
    common.add_argument("--seed", type=int, default=None, help="Override schema seed")
    common.add_argument("--verbose", action="store_true", help="Show full traceback on errors")

    gen = sub.add_parser("generate", help="Generate CSV datasets", parents=[common])
    gen.add_argument("--rows", type=int, default=None, help="Override rows for all tables")
    gen.set_defaults(func=_cmd_generate)

    describe = sub.add_parser("describe", help="Describe schema contents", parents=[common])
    describe.set_defaults(func=_cmd_describe)

    validate = sub.add_parser("validate", help="Validate generated dataset against schema", parents=[common])
    validate.add_argument("--rows", type=int, default=None, help="Override rows for generated validation sample")
    validate.set_defaults(func=_cmd_validate)

    return parser


def _format_error(exc: Exception) -> str:
    return f"Error: {exc}"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    verbose_mode = bool(getattr(args, "verbose", False) or os.getenv("DEBUG"))

    try:
        args.func(args)
    except (SchemaError, ValueError, OSError) as exc:
        if verbose_mode:
            raise
        print(_format_error(exc))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
