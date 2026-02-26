from __future__ import annotations

from csv_generator.generator.config import load_schema
from csv_generator.generator.core import generate_dataset


def test_foreign_keys_reference_existing_parents() -> None:
    schema = load_schema("csv_generator/schemas/retail_basic.yaml")
    tables, _, _ = generate_dataset(schema, rows_override=200, seed_override=99)

    customer_ids = {row["customer_id"] for row in tables["customers"]}
    product_ids = {row["product_id"] for row in tables["products"]}

    for row in tables["orders"]:
        assert row["customer_id"] in customer_ids
        assert row["product_id"] in product_ids
