# Data-Generation Toolkit

Multi-format, analytics-grade synthetic data toolkit.

## Recommended start (local-by-default)

Use the bootstrap runner first:

```bash
python all-in-one/datagen_bootstrap.py --help
```

Primary workflow docs: [`all-in-one/README.md`](all-in-one/README.md).

The bootstrap runner is the default path for this project: it creates/uses `<repo_root>/.venv`, installs only needed dependencies for the selected format, and runs generator CLIs with that local interpreter.

## Advanced/Optional workflow

Advanced users can run module CLIs directly (for example `python -m generators.<module>.generator.cli ...`) **only after** activating `.venv` or by explicitly using `.venv` Python. If you bypass bootstrap, dependency management is manual.

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

## Test

```bash
pytest
```
