# Data-Generation

This repository contains a professional-grade, schema-driven CSV dataset generator for analytics practice.
It supports reproducible generation with fixed seeds, realistic distributions, table-level constraints,
multi-table referential integrity, computed columns, and optional dirty-data corruption features.
The project is designed for command-line usage and straightforward pandas ingestion.

See full documentation in [`csv_generator/README.md`](csv_generator/README.md).

## Quick examples

```bash
python -m csv_generator.generator.cli generate --schema csv_generator/schemas/retail_basic.yaml --rows 1000 --seed 42 --out csv_generator/output/retail_basic
python -m csv_generator.generator.cli describe --schema csv_generator/schemas/hr_employees.yaml
```
