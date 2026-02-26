import hashlib
import json

from shared.schema_dsl.engine import generate_tables
from shared.schema_dsl.parser import load_schema


def _hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def test_shared_reproducibility():
    schema = load_schema("generators/json_generator/schemas/web_events_ndjson.yaml")
    a = generate_tables(schema.raw, seed=123)
    b = generate_tables(schema.raw, seed=123)
    assert _hash(a) == _hash(b)
