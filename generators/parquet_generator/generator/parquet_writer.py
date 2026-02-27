from __future__ import annotations

from pathlib import Path


def write_parquet_tables(out_dir: str | Path, tables: dict[str, list[dict]], partition_by: dict[str, list[str]] | None = None) -> None:
    try:
        import pyarrow as pa
        import pyarrow.dataset as ds
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError(
            "Optional dependency 'pyarrow' is required. Install with: "
            "pip install -r generators/parquet_generator/requirements.txt"
        ) from exc

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    partition_by = partition_by or {}
    for table_name, rows in tables.items():
        table = pa.Table.from_pylist(rows)
        target = out / table_name
        parts = partition_by.get(table_name)
        if parts:
            ds.write_dataset(table, base_dir=str(target), format="parquet", partitioning=parts, existing_data_behavior="overwrite_or_ignore")
        else:
            pq.write_table(table, target.with_suffix(".parquet"))
