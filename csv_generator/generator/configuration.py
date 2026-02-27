"""Backward-compatible imports for schema configuration utilities."""

from .config import SchemaConfig, SchemaError, load_schema

__all__ = ["SchemaConfig", "SchemaError", "load_schema"]
