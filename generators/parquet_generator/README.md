# Parquet Generator

Generate analytics-grade Parquet datasets from the shared YAML DSL.

```bash
python -m generators.parquet_generator.generator.cli generate --schema generators/parquet_generator/schemas/retail_basic_parquet.yaml --out generators/parquet_generator/output
```

Supports `generate`, `describe`, and `validate` with shared options (`--schema --seed --out --rows --profile`).
