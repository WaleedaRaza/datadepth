import pytest
from datadepth.validators import validate_schema


def test_valid_schema_passes():
    schema = {
        "columns": [
            {"name": "age", "type": "int"},
            {"name": "name", "type": "str"},
        ]
    }
    validate_schema(schema)


def test_missing_columns_key():
    with pytest.raises(ValueError):
        validate_schema({})


def test_invalid_column_entry():
    schema = {"columns": [{"name": "x"}]}  # Missing type
    with pytest.raises(ValueError):
        validate_schema(schema)
