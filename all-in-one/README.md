# All-in-One (Option B) Bootstrap Workflow

This folder provides the **recommended Option B experience** for this repository: one command entrypoint that bootstraps a local virtual environment and routes to the right generator CLI.

> This repo intentionally uses **Option B (local `.venv` bootstrap)**. It is **not** a stdlib-only single file, and it does **not** vendor third-party source code.

## Repository layout

- `/shared`  
  Shared schema parsing, CLI helpers, constraints, relationships, and utilities used by all generators.
- `/generators`  
  Format-specific generator packages (`csv_generator`, `json_generator`, `sqlite_seed`, `parquet_generator`, `event_stream_generator`) with module CLIs.
- `/csv_generator` (legacy engine)  
  The original legacy CSV implementation and schemas.
- `/all-in-one`  
  Bootstrap and guided execution scripts:
  - `all-in-one/datagen_bootstrap.py` → primary user entrypoint.
  - `all-in-one/bootstrap_lib.py` → local helper library for venv/dependency/module routing.
  - `all-in-one/verify_env.py` → optional environment verification utility.
  - `all-in-one/run_examples.py` → optional end-to-end demo runner.

## Execution flow (layout-by-layout)

1. **Bootstrap `.venv` and install dependencies** using:  
   `all-in-one/datagen_bootstrap.py`

   ```bash
   python all-in-one/datagen_bootstrap.py describe \
     --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
     --format sqlite
   ```

   What this does:
   - Creates `.venv/` at repo root (if missing).
   - Installs dependencies (prefers `requirements-dev.txt`, plus format requirements).
   - Caches install state in `.venv/.datagen_bootstrap.json`.
   - Invokes only the `.venv` Python for downstream CLI execution.

2. **(Optional) Verify environment** using:  
   `all-in-one/verify_env.py`

   ```bash
   python all-in-one/verify_env.py
   ```

3. **Describe schema** using:  
   `all-in-one/datagen_bootstrap.py`

   ```bash
   python all-in-one/datagen_bootstrap.py describe \
     --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
     --format sqlite
   ```

4. **Generate data** using:  
   `all-in-one/datagen_bootstrap.py`

   ```bash
   python all-in-one/datagen_bootstrap.py generate \
     --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
     --out all-in-one/output/retail.db \
     --format sqlite \
     --rows 10 \
     --seed 123 \
     --profile realistic
   ```

5. **Validate data** using:  
   `all-in-one/datagen_bootstrap.py`

   ```bash
   python all-in-one/datagen_bootstrap.py validate \
     --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
     --out all-in-one/output/retail.db \
     --format sqlite \
     --rows 10 \
     --seed 123
   ```

6. **Outputs and produced files**
   - Generated output goes to `--out` (e.g., `all-in-one/output/retail.db`).
   - Validation writes `validation_report.json` in the output directory context used by generator CLIs.
   - Bootstrap cache marker is `.venv/.datagen_bootstrap.json`.


## Repository root detection

`all-in-one/datagen_bootstrap.py` auto-detects the repository root by walking upward from the script location until it finds a directory that has:

- at least one marker file: `requirements-dev.txt`, `pyproject.toml`, `setup.cfg`, or `setup.py`
- both required directories: `shared/` and `generators/`

This avoids brittle assumptions about exact script placement and keeps `.venv/` and bootstrap cache files anchored to the detected repo root.

Common failure mode: if you copy or move the bootstrap script outside this repository tree, auto-detection will fail with a `BootstrapError` describing the expected markers and directories.

## CLI contract (single entrypoint)

`all-in-one/datagen_bootstrap.py` supports:
- Commands: `describe | generate | validate`
- Flags:
  - `--schema PATH`
  - `--out PATH` (required for `generate` / `validate`)
  - `--format {csv,json,ndjson,sqlite,parquet,event_stream}`
  - `--seed INT`
  - `--profile {fast,realistic,dirty}`
  - `--verbose`
  - `--rows INT`
  - `--reinstall` (force reinstallation of deps)

## Optional guided demo

Run `all-in-one/run_examples.py` to execute a small `generate + validate` SQLite flow with 10 rows.

```bash
python all-in-one/run_examples.py
```

## Troubleshooting

- **Jupyter kernel mismatch**  
  Your notebook may use system Python while bootstrap installed into `.venv`. Select `.venv` as the notebook kernel/interpreter.

- **Windows paths and venv scripts**  
  `.venv\Scripts\python.exe` is used on Windows; macOS/Linux uses `.venv/bin/python`.

- **Proxy/firewall pip issues**  
  Configure `PIP_INDEX_URL` and/or `PIP_EXTRA_INDEX_URL`, then rerun bootstrap.

- **Force reinstall dependencies**  
  Use:
  ```bash
  python all-in-one/datagen_bootstrap.py describe --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml --format sqlite --reinstall
  ```
