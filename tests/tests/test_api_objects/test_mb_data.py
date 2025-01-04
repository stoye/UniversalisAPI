from pathlib import Path
import json

import pytest

from universalisapi.api_objects.mb_data import MBDataResponse, MBDataResponseItem
from universalisapi.client import UniversalisAPIClient
from universalisapi.exceptions import UniversalisError


@pytest.mark.unittest
class TestMBDataResponse:

    def test_data(self, mb_data_data_objs):
        stem, data, resp = mb_data_data_objs
        assert data == resp.data

    def test_data_set(self):
        with pytest.raises(UniversalisError):
            obj = MBDataResponse({}, {})
            obj.data = {}

    def test_items(self, mb_data_data_objs):
        stem, data, resp = mb_data_data_objs
        items = {item_id: MBDataResponseItem(item_data) for item_id, item_data in data['items'].items()}
        for item, item_obj in zip(items.values(), resp.items.values()):
            assert isinstance(item_obj, MBDataResponseItem)
            assert item.item_id == item_obj.item_id

    def test_items_set(self):
        with pytest.raises(UniversalisError):
            obj = MBDataResponse({}, {})
            obj.items = {}

    def test_get_listing_ids(self, mb_data_data_objs):
        stem, data, resp = mb_data_data_objs

        items = data['items'].values()

        listing_ids = []
        for item in items:
            for listing in item['listings']:
                listing_ids.append(listing['listingID'])

        assert resp.get_listing_ids() == listing_ids


class TestMBDataResponseItem:

    def test_data(self, mb_data_data_items):
        stem, data, resp, zlist = mb_data_data_items
        for item_data, item_obj in zlist:
            assert item_data == item_obj.data

    def test_data_setter(self):
        with pytest.raises(UniversalisError):
            obj = MBDataResponseItem({'itemID': 0, 'listings': 0})
            obj.data = {}

    def test_get_listing_ids(self, mb_data_data_items):
        stem, data, resp, zlist = mb_data_data_items
        for item_data, item_obj in zlist:
            listing_ids = [l['listingID'] for l in item_data['listings']]
            assert listing_ids == item_obj.get_listing_ids()