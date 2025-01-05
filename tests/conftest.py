import json
from pathlib import Path

import pytest

from universalisapi._wrapper import UniversalisAPIWrapper
from universalisapi.api_objects.mb_data import MBDataResponse


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

AGGREGATE_DATA = {}
agg_data_path = Path('.') / 'tests' / 'aggregate_data'
for file_path in agg_data_path.glob('*.json'):
    with file_path.open('r', encoding='utf-8') as f:
        AGGREGATE_DATA[file_path.stem] = json.load(f)

@pytest.fixture
def valid_unviersalis_item_ids():
    item_ids = []
    for stem in AGGREGATE_DATA.keys():
        item_ids_str = stem.split('_')[1]
        item_ids_strs = item_ids_str.split(',')
        item_ids.extend(list(map(int, item_ids_strs)))
    return item_ids

@pytest.fixture
def aggregate_data():
    return AGGREGATE_DATA

@pytest.fixture(params=[(stem, data) for stem, data in AGGREGATE_DATA.items()],
                ids=(lambda x: x[0]))
def aggregate_data_parametrized(request):
    return request.param

LEAST_RECENT_DATA = {}
least_recent_data_path = Path('.') / 'tests' / 'least_recent_data'
for file_path in least_recent_data_path.glob('*.json'):
    with file_path.open('r', encoding='utf-8') as f:
        LEAST_RECENT_DATA[file_path.stem] = json.load(f)

@pytest.fixture
def least_recent_data():
    return LEAST_RECENT_DATA

@pytest.fixture(params=[(stem, data) for stem, data in LEAST_RECENT_DATA.items()],
                ids=(lambda x: x[0]))
def least_recent_data_parametrized(request):
    return request.param

MB_DATA_DATA = {}
mb_data_data_path = Path('.') / 'tests' / 'mb_data_data'
for file_name in mb_data_data_path.glob('*.json'):
    with file_name.open('r', encoding='utf-8') as f:
        MB_DATA_DATA[file_name.stem] = json.load(f)

@pytest.fixture
def mb_data_data():
    return MB_DATA_DATA

@pytest.fixture(params=[(stem, data) for stem, data in MB_DATA_DATA.items()],
                ids=(lambda x: x[0]))
def mb_data_data_parametrized(request):
    return request.param

@pytest.fixture
def mb_data_data_parser(mb_data_data_parametrized):
    stem, data = mb_data_data_parametrized
    split_stem = stem.split('_')
    w_d_r = split_stem[0]
    region = split_stem[1]
    items_str = split_stem[2]
    item_ids = list(map(int, items_str.split(',')))
    return w_d_r, region, items_str, item_ids, data

@pytest.fixture
def mb_data_data_objs(mb_data_data_parametrized):
    stem, data = mb_data_data_parametrized
    if 'items' not in data:
        stem_data = stem.split('_')
        w_d = stem_data[0]
        w_d_name = stem_data[1]
        data = {
            'itemIDs': [data['itemID']],
            'items': {str(data['itemID']): data},
            w_d: w_d_name,
            'unresolvedItems': []
        }
    return stem, data, MBDataResponse(data, {})

@pytest.fixture
def mb_data_data_items(mb_data_data_objs):
    stem, data, resp = mb_data_data_objs
    return stem, data, resp, zip(data['items'].values(), resp.items.values())