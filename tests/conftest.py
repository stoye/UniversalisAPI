import json
import random
from pathlib import Path

import pytest

from universalisapi._wrapper import UniversalisAPIWrapper
from universalisapi.api_objects.mb_data import MBDataResponse, MBDataResponseItem


# globals
BASE_URL = UniversalisAPIWrapper.base_url

@pytest.fixture
def base_url() -> str:
    """The base Universalis URL."""
    return BASE_URL

with open('tests/data-centers.json', encoding='utf-8') as f:
    DATA_CENTERS_DATA = json.load(f)

@pytest.fixture
def data_centers() -> list[dict]:
    """A response from /data-centers."""
    yield DATA_CENTERS_DATA

with open('tests/worlds.json', encoding='utf-8') as f:
    WORLD_DATA = json.load(f)

@pytest.fixture
def worlds() -> list[dict]:
    """A response from /worlds."""
    yield WORLD_DATA

@pytest.fixture
def valid_region_names(data_centers, worlds) -> list[str]:
    """List of valid regions to pass to methods."""
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
"""Responses from /aggregate/{region}/{item_ids}, keyed on {region}_{item_ids}"""

@pytest.fixture
def valid_unviersalis_item_ids() -> list[int]:
    """Generate a list of item_ids we know Universalis has data for."""
    item_ids = []
    for stem in AGGREGATE_DATA.keys():
        item_ids_str = stem.split('_')[1]
        item_ids_strs = item_ids_str.split(',')
        item_ids.extend(list(map(int, item_ids_strs)))
    return item_ids

@pytest.fixture
def aggregate_data() -> dict[str, dict]:
    """Fixture for AGG_DATA Global above."""
    return AGGREGATE_DATA

@pytest.fixture(params=[(stem, data) for stem, data in AGGREGATE_DATA.items()],
                ids=(lambda x: x[0]))
def aggregate_data_parametrized(request) -> tuple[str, dict[str, dict]]:
    """Parametrized fixture for running the tests on each instance of agg_data."""
    return request.param

LEAST_RECENT_DATA: dict[str, list[dict]] = {}
least_recent_data_path = Path('.') / 'tests' / 'least_recent_data'
for file_path in least_recent_data_path.glob('*.json'):
    with file_path.open('r', encoding='utf-8') as f:
        LEAST_RECENT_DATA[file_path.stem] = json.load(f)
"""Responses from /extra/stats/least-recently-updated?{region}={region},
keyed on {region_type}_{region}_{entries}"""

@pytest.fixture
def least_recent_data() -> dict[str, list[dict]]:
    """Fixture for the above global."""
    return LEAST_RECENT_DATA

@pytest.fixture(params=[(stem, data) for stem, data in LEAST_RECENT_DATA.items()],
                ids=(lambda x: x[0]))
def least_recent_data_parametrized(request) -> tuple[str, list[dict]]:
    """Parametrized fixture for running the tests on each instance of LR Data."""
    return request.param

MB_DATA_DATA = {}
mb_data_data_path = Path('.') / 'tests' / 'mb_data_data'
for file_name in mb_data_data_path.glob('*.json'):
    with file_name.open('r', encoding='utf-8') as f:
        MB_DATA_DATA[file_name.stem] = json.load(f)
"""Responses from /{region}/{item_ids}, keyed on {region_type}_{region}_{item_ids}"""

@pytest.fixture
def mb_data_data() -> dict[str, dict]:
    """Fixture for above global."""
    return MB_DATA_DATA

@pytest.fixture(params=[(stem, data) for stem, data in MB_DATA_DATA.items()],
                ids=(lambda x: x[0]))
def mb_data_data_parametrized(request) -> tuple[str, dict]:
    """Parametrized fixture for running the tests on each instance of MB Data."""
    return request.param

@pytest.fixture
def mb_data_data_parser(mb_data_data_parametrized) -> tuple[str, str, str, list[id], dict]:
    """Break up stems for testing.

    Returns
    -------
    w_d_r : str
        'worldName' | 'dcName'
    region : str
        World | DataCenter
    items_str : str
        concat list of item_ids
    item_ids : list[int]
        list of item ids
    data : dict
        dict that belongs to each stem
    """
    stem, data = mb_data_data_parametrized
    split_stem = stem.split('_')
    w_d_r = split_stem[0]
    region = split_stem[1]
    items_str = split_stem[2]
    item_ids = list(map(int, items_str.split(',')))
    return w_d_r, region, items_str, item_ids, data

@pytest.fixture
def mb_data_data_objs(mb_data_data_parser) -> tuple[dict, MBDataResponse]:
    """
    Create test MBDataResponse objects.

    Returns
    -------
    stem : str
        dict key from MB_DATA_DATA
    data : dict
        dict value from MB_DATA_DATA
    MBDataResponse
        object with the given data and appropriate params
    """
    w_d_r, region, items_str, item_ids, data = mb_data_data_parser
    params = {
        'item_ids': item_ids,
        'region': region,
        'listings': None,
        'entries': None,
        'hq': None,
        'stats_within': None,
        'entries_within': None,
        'fields': None
    }
    return data, MBDataResponse(data, params)

@pytest.fixture
def mb_data_data_items(mb_data_data_parser):
    """
    Create test MBDataResponseItem objects.

    Returns
    -------

    """
    w_d_r, region, items_str, item_ids, data = mb_data_data_parser

    if 'items' in data:
        item_objs = [MBDataResponseItem(item_data) for item_data in data['items'].values()]
        item_data = data['items'].values()
    else:
        item_objs = [MBDataResponseItem(data)]
        item_data = [data]
    return item_data, item_objs

MB_DATA_DATA_CHANGES = {}
mb_data_data_changes_path = Path('.') / 'tests' / 'mb_data_data_changes'
for file_name in mb_data_data_changes_path.glob('*.json'):
    with file_name.open('r', encoding='utf-8') as f:
        MB_DATA_DATA_CHANGES[file_name.stem] = json.load(f)
"""Responses from /{region}/{item_ids}, keyed on {region_type}_{region}_{item_ids}"""

@pytest.fixture
def mb_data_data_changes():
    return MB_DATA_DATA_CHANGES

@pytest.fixture
def mb_data_data_old_and_changes(mb_data_data_changes,
                                 mb_data_data_parser,
                                 mb_data_data_objs):
    w_d_r, region, items_str, item_ids, old_data = mb_data_data_parser
    key = f'{w_d_r}_{region}_{items_str}'
    new_data = mb_data_data_changes[key]
    old_resp_obj = mb_data_data_objs[1]

    return old_data, old_resp_obj, new_data
