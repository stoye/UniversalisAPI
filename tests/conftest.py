import json
from pathlib import Path
import random

import pytest
from aioresponses import aioresponses

from universalisapi.api_objects.mb_data import MBDataResponse, MBDataResponseItem


# globals
AGGREGATE_DATA = {}
agg_data_path = Path('.') / 'tests' / 'aggregate_data'
for file_path in agg_data_path.glob('*.json'):
    with file_path.open('r', encoding='utf-8') as f:
        AGGREGATE_DATA[file_path.stem] = json.load(f)

@pytest.fixture(params=[(stem, data) for stem, data in AGGREGATE_DATA.items()],
                ids=(lambda x: x[0]))
def aggregate_data(request):
    return request.param

LEAST_RECENT_DATA = {}
least_recent_data_path = Path('.') / 'tests' / 'least_recent_data'
for file_path in least_recent_data_path.glob('*.json'):
    with file_path.open('r', encoding='utf-8') as f:
        LEAST_RECENT_DATA[file_path.stem] = json.load(f)

@pytest.fixture(params=[(stem, data) for stem, data in LEAST_RECENT_DATA.items()],
                ids=(lambda x: x[0]))
def least_recent_data(request):
    return request.param

MB_DATA_DATA = {}
MB_DATA_DATA_PATH = Path('.') / 'tests' / 'mb_data_data'
for file_name in MB_DATA_DATA_PATH.glob('*.json'):
    with file_name.open('r', encoding='utf-8') as f:
        MB_DATA_DATA[file_name.stem] = json.load(f)

@pytest.fixture(params=[(stem, data) for stem, data in MB_DATA_DATA.items()],
                ids=(lambda x: x[0]))
def mb_data_data(request):
    return request.param

@pytest.fixture
def mb_data_data_parser(mb_data_data):
    stem, data = mb_data_data
    split_stem = stem.split('_')
    w_d_r = split_stem[0]
    region = split_stem[1]
    items_str = split_stem[2]
    item_ids = list(map(int, items_str.split(',')))
    return w_d_r, region, items_str, item_ids, data

@pytest.fixture
def mb_data_data_objs(mb_data_data):
    stem, data = mb_data_data
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


# aioresponses
@pytest.fixture
def mocked_response():
    with aioresponses() as m:
        yield m

@pytest.fixture
def mocked_data_centers(mocked_response, base_url, data_centers):
    mocked_response.get(f'{base_url}/data-centers',
                        status=200,
                        payload=data_centers)

@pytest.fixture
def mocked_worlds(mocked_response, base_url, worlds):
    mocked_response.get(f'{base_url}/worlds',
                        status=200,
                        payload=worlds)

@pytest.fixture
def mocked_aggregated(mocked_response, base_url):
    def _mocked_aggregated_generator(item_ids, region, data):
        url = f'{base_url}/aggregated/{region}/{item_ids}'
        mocked_response.get(url, status=200, payload=data)
    yield _mocked_aggregated_generator

@pytest.fixture
def mocked_least_recent_items(mocked_response, base_url):
    def _mocked_least_recent_items_generator(k, v, entries, data):
        url = f'{base_url}/extra/stats/least-recently-updated?{k}={v}&entries={entries}'
        mocked_response.get(url, status=200, payload=data)
    yield _mocked_least_recent_items_generator

@pytest.fixture
def mocked_mb_current_data(mocked_response, base_url):
    def _mocked_mb_current_data_generator(region, items_str, params, data):
        url = f'{base_url}/{region}/{items_str}'
        if params:
            url += '?'
            for k, v in params.items():
                if not url.endswith('?'):
                    url += '&'
                url += f'{k}={v}'
        mocked_response.get(url, status=200, payload=data)
    yield _mocked_mb_current_data_generator


# helper functions
@pytest.fixture
def get_random_unicode():
    def _get_random_unicode(length):
        # Update this to include code point ranges to be sampled
        include_ranges = [
            (0x0021, 0x0021),
            (0x0023, 0x0026),
            (0x0028, 0x007E),
            (0x00A1, 0x00AC),
            (0x00AE, 0x00FF),
            (0x0100, 0x017F),
            (0x0180, 0x024F),
            (0x2C60, 0x2C7F),
            (0x16A0, 0x16F0),
            (0x0370, 0x0377),
            (0x037A, 0x037E),
            (0x0384, 0x038A),
            (0x038C, 0x038C),
        ]

        alphabet = [
            chr(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
        ]
        return ''.join(random.choice(alphabet) for i in range(length))
    return _get_random_unicode