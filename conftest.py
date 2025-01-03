import json

import pytest

from universalisapi.wrapper import UniversalisAPIWrapper


# globals
BASE_URL = UniversalisAPIWrapper.base_url

@pytest.fixture
def base_url():
    return BASE_URL

with open('tests/data-centers.json', 'r', encoding='utf-8') as f:
    DATA_CENTERS_DATA = json.load(f)

@pytest.fixture
def data_centers():
    yield DATA_CENTERS_DATA

with open('tests/worlds.json', 'r', encoding='utf-8') as f:
    WORLD_DATA = json.load(f)

@pytest.fixture
def worlds():
    yield WORLD_DATA

@pytest.fixture
def valid_region_names(data_centers, worlds):
    names = [region for region in UniversalisAPIWrapper.valid_regions]
    for dc in data_centers:
        names.append(dc['name'].lower())
    for world in worlds:
        names.append(world['name'].lower())
    return names