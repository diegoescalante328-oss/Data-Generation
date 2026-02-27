#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from bootstrap_lib import (  # type: ignore[import-not-found]
    BootstrapError,
    bootstrap,
    build_env,
    build_generator_command,
    resolve_module,
    run_command,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Option B bootstrap runner for Data-Generation (local .venv + generator routing)."
    )
    parser.add_argument("command", choices=["describe", "generate", "validate"], help="Action to run")
    parser.add_argument("--schema", required=True, help="Path to input schema")
    parser.add_argument("--out", help="Output path (required for generate/validate)")
    parser.add_argument(
        "--format",
        required=True,
        choices=["csv", "json", "ndjson", "sqlite", "parquet", "event_stream"],
        help="Generator format",
    )
    parser.add_argument("--seed", type=int, help="Deterministic seed")
    parser.add_argument("--rows", type=int, help="Row count override")
    parser.add_argument("--profile", choices=["fast", "realistic", "dirty"], default="realistic")
    parser.add_argument("--reinstall", action="store_true", help="Force reinstall dependencies into .venv")
    parser.add_argument("--verbose", action="store_true", help="Verbose bootstrap and downstream CLI logs")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        bootstrap(args.format, reinstall=args.reinstall, verbose=args.verbose)
        module = resolve_module(args.format)
        cmd = build_generator_command(args, module)
        run_command(cmd, env=build_env(), verbose=args.verbose)
    except BootstrapError as exc:
        print(f"Bootstrap error: {exc}")
        return 1
    except KeyboardInterrupt:
        print("Interrupted")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
