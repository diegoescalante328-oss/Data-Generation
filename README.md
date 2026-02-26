# Data-Generation Toolkit

Multi-format, analytics-grade synthetic data toolkit.

## Modules
- Legacy + stable CSV engine: [`csv_generator/`](csv_generator/README.md)
- Namespaced CSV wrapper: [`generators/csv_generator/`](generators/csv_generator/README.md)
- Parquet: [`generators/parquet_generator/`](generators/parquet_generator/README.md)
- JSON / NDJSON: [`generators/json_generator/`](generators/json_generator/README.md)
- SQLite seeding: [`generators/sqlite_seed/`](generators/sqlite_seed/README.md)
- Event stream NDJSON: [`generators/event_stream_generator/`](generators/event_stream_generator/README.md)

## Quick Tools
- One-file quick generator: [`all-in-one/`](all-in-one/README.md)

## Docs
- [Quickstart](docs/quickstart.md)
- [Schema DSL guide](docs/schemas_guide.md)
- [Architecture](docs/architecture.md)

## Recommended CLI pattern

```bash
python -m generators.<module>.generator.cli <generate|describe|validate> --schema <path> --out <path> [--seed N] [--rows N] [--profile fast|realistic|dirty]
```

## Test

```bash
pytest
```
