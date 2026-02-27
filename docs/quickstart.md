# Quickstart (Local-by-Default)

This quickstart uses the bootstrap runner (`all-in-one/datagen_bootstrap.py`) as the default workflow.

## 1) Verify Python

```bash
python --version
```

## 2) Show bootstrap help

```bash
python all-in-one/datagen_bootstrap.py --help
```

## 3) Describe a schema

```bash
python all-in-one/datagen_bootstrap.py describe \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml
```

## 4) Generate data (SQLite example)

```bash
python all-in-one/datagen_bootstrap.py generate \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
  --out generators/sqlite_seed/output/retail_basic.db \
  --rows 10 \
  --seed 9
```

## 5) Validate output

```bash
python all-in-one/datagen_bootstrap.py validate \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
  --out generators/sqlite_seed/output/retail_basic.db \
  --rows 10 \
  --seed 9
```

`validate` writes `validation_report.json` in the format's output context.

## Advanced/Optional: run modules directly

This is supported, but manual:

- Activate `.venv` (or call `.venv` Python directly).
- Install required dependencies yourself.

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r generators/json_generator/requirements.txt
python -m generators.json_generator.generator.cli generate \
  --schema generators/json_generator/schemas/web_events_ndjson.yaml \
  --out generators/json_generator/output \
  --output-mode ndjson
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r generators/json_generator/requirements.txt
python -m generators.json_generator.generator.cli generate --schema generators/json_generator/schemas/web_events_ndjson.yaml --out generators/json_generator/output --output-mode ndjson
```

If you skip bootstrap, you are responsible for dependency installation and environment consistency.
