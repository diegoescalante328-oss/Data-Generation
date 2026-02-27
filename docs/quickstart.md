# Quickstart

This quickstart uses the **Option B bootstrap runner** (`all-in-one/datagen_bootstrap.py`). It is the recommended workflow because it:

- detects and runs from the repository root,
- creates and reuses `./.venv`,
- installs needed dependencies into that local `.venv`,
- routes commands to the correct generator CLI with consistent arguments.

## Prerequisites

### 1) Verify Python

```bash
python3 --version
```

Use Python 3.10+ if possible.

### 2) Show bootstrap help

```bash
python3 all-in-one/datagen_bootstrap.py --help
```

You should see the unified command model:

- `describe`
- `generate`
- `validate`

with common flags such as `--schema`, `--out`, `--seed`, `--rows`, `--profile`, and `--format`.

## Run a schema end-to-end

### 3) Describe a schema

```bash
python3 all-in-one/datagen_bootstrap.py describe \
  --format csv \
  --schema csv_generator/schemas/retail_basic_tiny.yaml
```

This prints dataset/table/column metadata so you can sanity-check schema intent before generating files.

### 4) Generate outputs in two formats (SQLite + NDJSON)

#### A) Generate SQLite database

```bash
python3 all-in-one/datagen_bootstrap.py generate \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
  --out generators/sqlite_seed/output/retail_basic.db \
  --seed 9
```

Produces:

- `generators/sqlite_seed/output/retail_basic.db`

#### B) Generate NDJSON file

```bash
python3 all-in-one/datagen_bootstrap.py generate \
  --format ndjson \
  --schema generators/json_generator/schemas/web_events_ndjson.yaml \
  --out generators/json_generator/output \
  --seed 101
```

Produces (single-table schema):

- `generators/json_generator/output/web_events.ndjson`

### 5) Validate outputs

#### Validate SQLite output

```bash
python3 all-in-one/datagen_bootstrap.py validate \
  --format sqlite \
  --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml \
  --out generators/sqlite_seed/output/retail_basic.db \
  --seed 9
```

Validation report location:

- `generators/sqlite_seed/output/validation_report.json`

#### Validate NDJSON output

```bash
python3 all-in-one/datagen_bootstrap.py validate \
  --format ndjson \
  --schema generators/json_generator/schemas/web_events_ndjson.yaml \
  --out generators/json_generator/output \
  --seed 101
```

Validation report location:

- `generators/json_generator/output/validation_report.json`

## Where output files go

The path passed to `--out` is format-specific:

- `csv`, `json`, `ndjson`, `parquet`, `event_stream`: `--out` is an **output directory**.
- `sqlite`: `--out` is a **SQLite database file path** (for example `.../retail_basic.db`).

`validate` always writes `validation_report.json` into the relevant output directory.

## Manual install (alternative)

> Secondary path (use only if you do not want bootstrap automation).

1. Create and activate a venv yourself.
2. Install dependencies manually.
3. Call generator modules directly.

Example:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -r generators/json_generator/requirements.txt

python -m generators.json_generator.generator.cli generate \
  --schema generators/json_generator/schemas/web_events_ndjson.yaml \
  --out generators/json_generator/output \
  --output-mode ndjson
```

For regular usage, prefer the bootstrap runner.
