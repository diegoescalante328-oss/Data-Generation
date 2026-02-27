# All-in-One CSV Generator

A ready-to-run, single-file CSV generator for quick synthetic data creation.

## Quick start

From this folder:

```bash
python csv_generator.py
```

This creates `generated_data.csv` with 1000 rows.

## Common usage

Generate a custom number of rows:

```bash
python csv_generator.py --rows 5000
```

Choose output path:

```bash
python csv_generator.py --rows 2000 --output output/my_data.csv
```

Reproducible output with a seed:

```bash
python csv_generator.py --rows 500 --seed 42 --output output/reproducible.csv
```

## Jupyter / VS Code notebook use

```python
from pathlib import Path
from csv_generator import generate_csv

generate_csv(output_path=Path("notebook_data.csv"), rows=250, seed=7)
```

## Included fields

- record and customer IDs
- names and email
- city and country
- account status and timestamps
- product and purchase values
- boolean and numeric score columns

No external dependencies are required.
