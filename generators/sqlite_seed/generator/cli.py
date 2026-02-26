from __future__ import annotations

import argparse
import sqlite3

from shared.schema_dsl.parser import describe_schema, load_schema
from .seeder import seed_database


def _cmd_generate(args):
    schema = load_schema(args.schema)
    seed = args.seed if args.seed is not None else schema.raw.get("seed", 0)
    counts = seed_database(schema.raw, args.out, seed, args.rows, args.profile)
    print(counts)


def _cmd_describe(args):
    print(describe_schema(load_schema(args.schema)))


def _cmd_validate(args):
    conn = sqlite3.connect(args.out)
    conn.execute("PRAGMA foreign_keys = ON;")
    violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    conn.close()
    if violations:
        print(violations)
        raise SystemExit(1)
    print("Validation passed")


def main():
    parser = argparse.ArgumentParser(description="SQLite seeder")
    sub = parser.add_subparsers(dest="command", required=True)
    for n, fn in (("generate", _cmd_generate), ("describe", _cmd_describe), ("validate", _cmd_validate)):
        p = sub.add_parser(n)
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
