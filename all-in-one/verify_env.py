#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import json

from bootstrap_lib import MARKER_PATH, REPO_ROOT, VENV_DIR, find_repo_root, run_command_capture, venv_python


def main() -> int:
    detected_root = find_repo_root(Path(__file__))
    py = venv_python()
    if not py.exists():
        print(f"Missing virtual environment interpreter: {py}")
        return 1

    print(f"Repo root: {REPO_ROOT}")
    if detected_root != REPO_ROOT:
        print(f"Warning: runtime root detection mismatch ({detected_root})")
    print(f"Venv python: {py}")

    version = run_command_capture([str(py), "--version"])
    print(version.stdout.strip() or version.stderr.strip())

    pip_list = run_command_capture([str(py), "-m", "pip", "list", "--format=json"])
    packages = json.loads(pip_list.stdout)
    print(f"Installed packages in {VENV_DIR}: {len(packages)}")

    if MARKER_PATH.exists():
        marker = json.loads(MARKER_PATH.read_text(encoding="utf-8"))
        print("Bootstrap marker found:")
        print(json.dumps(marker, indent=2))
    else:
        print("Bootstrap marker not found. Run all-in-one/datagen_bootstrap.py first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
