import json
from pathlib import Path

import pytest
from jsonschema.validators import validator_for


base_schema_path = Path('.') / 'tests' / 'schemas'

agg_data_schema_path = base_schema_path / 'agg_data.json'
with agg_data_schema_path.open('r', encoding='utf-8') as f:
    AGGREGATE_DATA_SCHEMA = json.load(f)

lr_data_scheme_path = base_schema_path / 'least_recent.json'
with lr_data_scheme_path.open('r', encoding='utf-8') as f:
    LR_DATA_SCHEMA = json.load(f)

@pytest.fixture
def agg_data_schema_validator():
    return validator_for(AGGREGATE_DATA_SCHEMA)(AGGREGATE_DATA_SCHEMA)

@pytest.fixture
def least_recent_schema_validator():
    return validator_for(LR_DATA_SCHEMA)(LR_DATA_SCHEMA)