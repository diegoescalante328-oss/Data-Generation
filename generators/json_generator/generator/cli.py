from __future__ import annotations

import argparse
import json
from pathlib import Path

from shared.cli.common import (
    build_parser,
    command_main,
    ensure_path_exists,
    optional_dependency_error,
    write_validation_report,
)
from shared.constraints.rules import validate_dataset
from shared.schema_dsl.engine import generate_tables
from shared.schema_dsl.parser import describe_schema, load_schema

from .json_writer import write_json

GENERATOR_NAME = "json_generator"


def _resolve_seed(schema_raw: dict, seed: int | None) -> int:
    return seed if seed is not None else int(schema_raw.get("seed", 0))


def _resolve_mode(schema_raw: dict, mode: str | None) -> str:
    return mode or schema_raw.get("output_mode", "ndjson")


def _table_output_path(out_dir: Path, table_name: str, mode: str) -> Path:
    return out_dir / f"{table_name}.{'ndjson' if mode == 'ndjson' else 'json'}"


def _cmd_generate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    tables = generate_tables(schema.raw, seed, args.rows, args.profile)
    table_name = next(iter(tables))
    mode = _resolve_mode(schema.raw, args.output_mode)
    out = write_json(_table_output_path(Path(args.out), table_name, mode), tables[table_name], mode)
    print(f"Generated {GENERATOR_NAME} output at {out}")
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    print(describe_schema(load_schema(args.schema)))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    seed = _resolve_seed(schema.raw, args.seed)
    table_name = next(iter(schema.raw.get("tables", {})))
    mode = _resolve_mode(schema.raw, args.output_mode)
    out_path = _table_output_path(Path(args.out), table_name, mode)
    checks: list[dict] = []
    errors: list[str] = []

    ensure_path_exists(out_path, description="Output file")
    checks.append({"name": "output_exists", "ok": True, "details": {"path": str(out_path)}})

    tables = generate_tables(schema.raw, seed, args.rows, args.profile)
    dataset_errors = validate_dataset(tables, schema.raw)
    checks.append({"name": "schema_constraints", "ok": not dataset_errors, "details": {"errors": dataset_errors}})
    errors.extend(dataset_errors)

    try:
        if mode == "json":
            parsed = json.loads(out_path.read_text(encoding="utf-8"))
            ok = isinstance(parsed, list)
        else:
            with out_path.open(encoding="utf-8") as handle:
                parsed = [json.loads(line) for line in handle if line.strip()]
            ok = True
        checks.append({"name": "output_parseable", "ok": ok, "details": {"mode": mode, "rows": len(parsed)}})
    except json.JSONDecodeError as exc:
        errors.append(f"JSON parse error: {exc}")
        checks.append({"name": "output_parseable", "ok": False, "details": {"mode": mode, "error": str(exc)}})
        parsed = []

    expected_rows = len(tables.get(table_name, []))
    actual_rows = len(parsed)
    row_ok = expected_rows == actual_rows
    checks.append({"name": "row_count_match", "ok": row_ok, "details": {"expected": expected_rows, "actual": actual_rows}})
    if not row_ok:
        errors.append(f"Row count mismatch for {table_name}: expected {expected_rows}, got {actual_rows}")

    report_path = write_validation_report(
        args.out,
        generator=GENERATOR_NAME,
        schema_path=schema.path,
        output_path=out_path,
        seed=seed,
        checks=checks,
        errors=errors,
        stats={"table_counts": {k: len(v) for k, v in tables.items()}},
    )
    print(f"Validation report: {report_path}")
    return 1 if errors else 0


def build_cli_parser() -> argparse.ArgumentParser:
    parser = build_parser(
        "JSON/NDJSON generator",
        {"describe": _cmd_describe, "generate": _cmd_generate, "validate": _cmd_validate},
    )
    for cmd in parser._subparsers._group_actions[0].choices.values():
        cmd.add_argument("--output-mode", choices=["json", "ndjson"], default=None)
    return parser


def main() -> None:
    try:
        import yaml  # noqa: F401
    except ImportError as exc:
        raise optional_dependency_error("pyyaml", "pip install -r generators/json_generator/requirements.txt") from exc
    command_main(build_cli_parser())


if __name__ == "__main__":
    main()
