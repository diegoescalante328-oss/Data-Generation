#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from bootstrap_lib import bootstrap, build_env, run_command, venv_python

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = REPO_ROOT / "generators/sqlite_seed/schemas/retail_basic_sqlite.yaml"
EXAMPLE_OUT_DIR = REPO_ROOT / "all-in-one/_example_output"
DB_PATH = EXAMPLE_OUT_DIR / "retail_demo.db"


def main() -> int:
    EXAMPLE_OUT_DIR.mkdir(parents=True, exist_ok=True)
    bootstrap("sqlite", reinstall=False, verbose=True)

    run_command(
        [
            str(venv_python()),
            "all-in-one/datagen_bootstrap.py",
            "generate",
            "--schema",
            str(SCHEMA),
            "--out",
            str(DB_PATH),
            "--format",
            "sqlite",
            "--rows",
            "10",
            "--seed",
            "11",
            "--verbose",
        ],
        env=build_env(),
        verbose=True,
    )

    run_command(
        [
            str(venv_python()),
            "all-in-one/datagen_bootstrap.py",
            "validate",
            "--schema",
            str(SCHEMA),
            "--out",
            str(DB_PATH),
            "--format",
            "sqlite",
            "--rows",
            "10",
            "--seed",
            "11",
            "--verbose",
        ],
        env=build_env(),
        verbose=True,
    )

    report = EXAMPLE_OUT_DIR / "validation_report.json"
    print(f"Example complete. Database: {DB_PATH}")
    print(f"Validation report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
