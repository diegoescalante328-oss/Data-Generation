from __future__ import annotations

from csv_generator.generator.config import load_schema
from csv_generator.generator.core import generate_dataset


def test_primary_keys_are_unique() -> None:
    schema = load_schema("csv_generator/schemas/retail_basic.yaml")
    tables, _, _ = generate_dataset(schema, rows_override=150, seed_override=11)

    customer_ids = [row["customer_id"] for row in tables["customers"]]
    product_ids = [row["product_id"] for row in tables["products"]]
    order_ids = [row["order_id"] for row in tables["orders"]]

    assert len(customer_ids) == len(set(customer_ids))
    assert len(product_ids) == len(set(product_ids))
    assert len(order_ids) == len(set(order_ids))
