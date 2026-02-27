from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "datagen_onefile.py"
SCHEMA = REPO_ROOT / "generators/sqlite_seed/schemas/retail_basic_sqlite.yaml"


def _can_create_venv() -> bool:
    if shutil.which(sys.executable) is None:
        return False
    probe_dir = REPO_ROOT / ".tmp_venv_probe"
    if probe_dir.exists():
        shutil.rmtree(probe_dir)
    try:
        proc = subprocess.run([sys.executable, "-m", "venv", str(probe_dir)], cwd=REPO_ROOT, capture_output=True)
        return proc.returncode == 0
    finally:
        shutil.rmtree(probe_dir, ignore_errors=True)


pytestmark = pytest.mark.skipif(not _can_create_venv(), reason="Python venv creation unavailable in this environment")


def test_onefile_help() -> None:
    result = subprocess.run([sys.executable, str(RUNNER), "--help"], cwd=REPO_ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Single-file Data-Generation runner" in result.stdout


def test_onefile_generate_and_validate_sqlite(tmp_path: Path) -> None:
    out_db = tmp_path / "retail.db"

    gen = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "generate",
            "--schema",
            str(SCHEMA),
            "--out",
            str(out_db),
            "--format",
            "sqlite",
            "--seed",
            "123",
            "--rows",
            "10",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert gen.returncode == 0, gen.stderr + "\n" + gen.stdout
    assert out_db.exists()

    validate = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "validate",
            "--schema",
            str(SCHEMA),
            "--out",
            str(out_db),
            "--format",
            "sqlite",
            "--seed",
            "123",
            "--rows",
            "10",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, validate.stderr + "\n" + validate.stdout
    assert "Validation passed" in validate.stdout
