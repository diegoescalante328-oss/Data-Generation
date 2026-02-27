# Data-Generation Toolkit

Multi-format, analytics-grade synthetic data toolkit.

## Recommended start (Option B)

Use the all-in-one bootstrap workflow: [`all-in-one/README.md`](all-in-one/README.md).

This is the recommended model for this project: one bootstrap entrypoint that creates/uses `.venv/`, installs dependencies locally, and runs generator CLIs via the venv Python.

## Modules
- Legacy + stable CSV engine: [`csv_generator/`](csv_generator/README.md)
- Namespaced CSV wrapper: [`generators/csv_generator/`](generators/csv_generator/README.md)
- Parquet: [`generators/parquet_generator/`](generators/parquet_generator/README.md)
- JSON / NDJSON: [`generators/json_generator/`](generators/json_generator/README.md)
- SQLite seeding: [`generators/sqlite_seed/`](generators/sqlite_seed/README.md)
- Event stream NDJSON: [`generators/event_stream_generator/`](generators/event_stream_generator/README.md)

## Docs
- [Quickstart](docs/quickstart.md)
- [Schema DSL guide](docs/schemas_guide.md)
- [Architecture](docs/architecture.md)

## Recommended CLI pattern

```bash
python -m generators.<module>.generator.cli <generate|describe|validate> --schema <path> --out <path> [--seed N] [--rows N] [--profile fast|realistic|dirty]
```


## Option B bootstrap runner

Primary runner: `python all-in-one/datagen_bootstrap.py ...`

See full step-by-step instructions in [`all-in-one/README.md`](all-in-one/README.md).

## Test

```bash
pytest
```
