# Data-Generation Toolkit

Multi-format, analytics-grade synthetic data toolkit.

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


## One-file bootstrap runner

Use the root script when you want a true single-command workflow on a fresh machine.
It creates `.venv/`, installs dependencies, then routes to the matching generator CLI.

```bash
python datagen_onefile.py generate --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml --out out/retail.db --format sqlite --seed 123
python datagen_onefile.py validate --schema generators/sqlite_seed/schemas/retail_basic_sqlite.yaml --out out/retail.db --format sqlite
```

### Troubleshooting
- Corporate proxy / offline hosts: set `PIP_INDEX_URL` / `PIP_EXTRA_INDEX_URL` before running.
- Permission errors creating `.venv/`: run from a writable directory checkout.
- Force refresh dependencies: add `--reinstall`.

## Test

```bash
pytest
```
