from __future__ import annotations

import argparse
import json

from shared.constraints.rules import validate_dataset
from shared.io.reporting import write_validation_report
from shared.schema_dsl.engine import generate_tables
from shared.schema_dsl.parser import describe_schema, load_schema
from .json_writer import write_json


def _cmd_generate(args):
    schema = load_schema(args.schema)
    seed = args.seed if args.seed is not None else schema.raw.get("seed", 0)
    tables = generate_tables(schema.raw, seed, args.rows, args.profile)
    tname = next(iter(tables.keys()))
    mode = args.output_mode or schema.raw.get("output_mode", "ndjson")
    suffix = "ndjson" if mode == "ndjson" else "json"
    out = write_json(f"{args.out}/{tname}.{suffix}", tables[tname], mode)
    print(out)


def _cmd_describe(args):
    print(describe_schema(load_schema(args.schema)))


def _cmd_validate(args):
    schema = load_schema(args.schema)
    seed = args.seed if args.seed is not None else schema.raw.get("seed", 0)
    tables = generate_tables(schema.raw, seed, args.rows, args.profile)
    errors = validate_dataset(tables, schema.raw)
    tname = next(iter(tables.keys()))
    mode = args.output_mode or schema.raw.get("output_mode", "ndjson")
    path = f"{args.out}/{tname}.{'ndjson' if mode == 'ndjson' else 'json'}"
    text = open(path, encoding="utf-8").read() if mode == "json" else "[" + ",".join(open(path, encoding='utf-8').read().strip().splitlines()) + "]"
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(str(exc))
    report = write_validation_report(args.out, errors, {k: len(v) for k, v in tables.items()})
    print(report)
    if errors:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="JSON/NDJSON generator")
    sub = parser.add_subparsers(dest="command", required=True)
    for n, fn in (("generate", _cmd_generate), ("describe", _cmd_describe), ("validate", _cmd_validate)):
        p = sub.add_parser(n)
        p.add_argument("--schema", required=True)
        p.add_argument("--seed", type=int, default=None)
        p.add_argument("--out", required=True)
        p.add_argument("--rows", type=int, default=None)
        p.add_argument("--profile", choices=["fast", "realistic", "dirty"], default="realistic")
        p.add_argument("--output-mode", choices=["json", "ndjson"], default=None)
        p.set_defaults(func=fn)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
