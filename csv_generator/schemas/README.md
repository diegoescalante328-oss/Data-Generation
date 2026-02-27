# CSV Schema Library

This folder contains production-like schemas and CI-sized minimal schemas for the CSV generator.
All files use a consistent top-level structure:

- `dataset`
- `seed`
- `tables`
- `relationships` (optional but included as `[]` for CI schemas)

## Schema Catalog

| Schema | Size | What it tests | Recommended use |
|---|---|---|---|
| `hr_employees_tiny.yaml` | tiny | Multi-table HR joins, computed salary, normal review/performance distributions | CI, quick local smoke tests |
| `hr_employees_small.yaml` | small | Same logic as tiny with higher cardinality and realistic review fanout | Demo runs |
| `hr_employees_medium.yaml` | medium | Scale behavior for large multi-table joins | Performance benchmarking |
| `hr_employees_large.yaml` | large | High-volume HR workloads with relationship fanout | Stress testing |
| `retail_basic_tiny.yaml` | tiny | customer→orders→order_items bridge, product popularity skew, poisson quantities | CI, relationship validation |
| `retail_basic_small.yaml` | small | Retail realism with skewed demand and discount distributions | Demo and integration testing |
| `retail_basic_medium.yaml` | medium | Throughput at six-figure customer and high item counts | Performance benchmarking |
| `retail_basic_large.yaml` | large | Million-scale customers and multi-million order items | Stress testing |
| `web_events_tiny.yaml` | tiny | Rare events, skewed event types, noisy durations | CI and validation checks |
| `web_events_small.yaml` | small | Session/event distributions with realistic interaction mix | Demo and analytics sandboxing |
| `web_events_medium.yaml` | medium | Event stream scale with drift-like time spread | Performance benchmarking |
| `web_events_large.yaml` | large | Very high event volume for throughput + storage tests | Stress testing |
| `single_table_10_rows.yaml` | tiny | Single-table deterministic generation | Unit tests |
| `two_tables_fk_minimal.yaml` | tiny | Basic FK relationships + lookup column propagation | Unit tests |
| `constraints_minimal.yaml` | tiny | Uniqueness, not-null, monotonic constraints | Unit tests |
| `corruption_minimal.yaml` | tiny | Missingness, duplicates, outlier corruption knobs | Unit tests |
| `computed_minimal.yaml` | tiny | Computed column expression evaluation | Unit tests |

> Compatibility aliases: `hr_employees.yaml`, `retail_basic.yaml`, and `web_events.yaml` are maintained and currently mirror the `*_small.yaml` variants.

## Option B Bootstrap Runner Workflow

Use the repository bootstrap flow with a local virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r csv_generator/requirements.txt
```

Generate tiny data:

```bash
python -m csv_generator.generator.cli generate \
  --schema csv_generator/schemas/retail_basic_tiny.yaml \
  --out csv_generator/output/retail_tiny
```

Generate large data:

```bash
python -m csv_generator.generator.cli generate \
  --schema csv_generator/schemas/web_events_large.yaml \
  --out csv_generator/output/web_events_large
```

Override row counts at runtime (applies one row count to every table in the selected schema):

```bash
python -m csv_generator.generator.cli generate \
  --schema csv_generator/schemas/hr_employees_small.yaml \
  --rows 10000 \
  --seed 77 \
  --out csv_generator/output/hr_override
```

## Scaling Notes

- These schemas are designed for both tiny CI workloads and very large performance workloads.
- You can manually scale row counts by editing `rows` in schema files or using `--rows` in the CLI.
- Distribution skew, relationship cardinality, and optional corruption settings are tuned to demonstrate high variability while remaining readable and maintainable.
- Large variants are intentionally realistic defaults for modern hardware; increase further only when infrastructure capacity is known.
