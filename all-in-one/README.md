# All-in-One Bootstrap Workflow (Local-by-Default)

This folder provides the **recommended workflow** for Data-Generation:
`all-in-one/datagen_bootstrap.py` creates/uses `<repo_root>/.venv`, installs only needed dependencies, and routes to the correct generator CLI.

## Primary workflow (recommended)

### 1) See help

```bash
python all-in-one/datagen_bootstrap.py --help
```

### 2) Describe a schema

```bash
python all-in-one/datagen_bootstrap.py describe \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml
```

### 3) Generate data

```bash
python all-in-one/datagen_bootstrap.py generate \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
  --out all-in-one/output/retail.db \
  --rows 10 \
  --seed 123
```

### 4) Validate output

```bash
python all-in-one/datagen_bootstrap.py validate \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
  --out all-in-one/output/retail.db \
  --rows 10 \
  --seed 123
```

## Dependency strategy used by bootstrap

- Uses `<repo_root>/.venv`.
- Installs `requirements-base.txt` **if present**.
- Installs only the selected format's requirements (`generators/*/requirements.txt`, plus legacy CSV requirements where applicable).
- Installs Parquet-specific deps (for example `pyarrow`) only for `--format parquet`.
- Caches install state in `.venv/.datagen_bootstrap.json`; skips reinstall unless fingerprints change or `--reinstall` is passed.

## Advanced/Optional: running modules directly

You can bypass bootstrap, but then **you manage dependencies manually**.

Requirements:
- Activate `.venv` first, **or** invoke `.venv` Python directly.
- Install required packages yourself before running module CLIs.

macOS/Linux example:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r generators/sqlite_seed/requirements.txt
python -m generators.sqlite_seed.generator.cli describe \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml
```

Windows PowerShell example:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r generators/sqlite_seed/requirements.txt
python -m generators.sqlite_seed.generator.cli describe --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml
```

Without activation, call venv Python explicitly:

- macOS/Linux: `.venv/bin/python -m generators.json_generator.generator.cli ...`
- Windows: `.venv\Scripts\python.exe -m generators.json_generator.generator.cli ...`

## Utilities in this folder

- `datagen_bootstrap.py`: primary entrypoint.
- `bootstrap_lib.py`: shared bootstrapping and repo root detection.
- `verify_env.py`: prints venv/python/package/marker status.
- `run_examples.py`: SQLite generate+validate smoke demo.
