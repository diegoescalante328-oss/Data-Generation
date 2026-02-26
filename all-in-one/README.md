# all-in-one: Ready-to-go CSV generator

If you want one file you can run anywhere (Jupyter, VS Code, terminal), use:

```bash
python all-in-one/csv_generator_ready.py --rows 1000 --seed 42 --out all-in-one/output/generated_data.csv
```

## Jupyter / Notebook usage

```python
import importlib.util

spec = importlib.util.spec_from_file_location("ready_gen", "all-in-one/csv_generator_ready.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

path = mod.generate_csv(rows=500, seed=7, out="my_data.csv")
print(path)
```

## What it generates
A generic analytics-style CSV with columns:
- `event_id`
- `event_time`
- `user_id`
- `session_id`
- `event_type`
- `country`
- `source`
- `device`
- `amount`
- `is_premium_user`

Output folder is created automatically.
