from pathlib import Path
import json
import random

import pytest

from universalisapi.api_objects.mb_data import MBDataResponse, MBDataResponseItem
from universalisapi.client import UniversalisAPIClient
from universalisapi.exceptions import UniversalisError


@pytest.mark.unittest
class TestMBDataResponseItem:

    def test_data_property(self, mb_data_data_items):
        data, item_objs = mb_data_data_items
        for item_data, item_obj in zip(data, item_objs):
            assert item_data == item_obj.data

    def test_data_property_set(self, mb_data_data_items):
        with pytest.raises(UniversalisError):
            data, item_objs = mb_data_data_items
            obj = item_objs[0]
            obj.data = {}

    def test_prices_property(self, mb_data_data_items):
        data, item_objs = mb_data_data_items
        for item_data, item_obj in zip(data, item_objs):
            price_dict = {
                'current': {
                    'default': item_data['currentAveragePrice'],
                    'nq': item_data['currentAveragePriceNQ'],
                    'hq': item_data['currentAveragePriceHQ']
                },
                'average': {
                    'default': item_data['averagePrice'],
                    'nq': item_data['averagePriceNQ'],
                    'hq': item_data['averagePriceHQ']
                },
                'min': {
                    'default': item_data['minPrice'],
                    'nq': item_data['minPriceNQ'],
                    'hq': item_data['minPriceHQ']
                },
                'max': {
                    'default': item_data['maxPrice'],
                    'nq': item_data['maxPriceNQ'],
                    'hq': item_data['maxPriceHQ']
                }
            }
            assert price_dict == item_obj.prices

    def test_best_price(self, mb_data_data_items):
        data, item_objs = mb_data_data_items
        for item_data, item_obj in zip(data, item_objs):
            best_price = item_data['minPrice']
            assert best_price == item_obj.best_price

    def test_listing_ids_property(self, mb_data_data_items):
        data, item_objs = mb_data_data_items
        for item_data, item_obj in zip(data, item_objs):
            listing_ids = [l['listingID'] for l in item_data['listings']]
            assert listing_ids == item_obj.listing_ids

    @pytest.mark.parametrize("n", [random.randint(1,500000)])
    def test_get_better_listings(self, mb_data_data_items, n):
        data, item_objs = mb_data_data_items
        for item_data, item_obj in zip(data, item_objs):
            better_listings = item_obj.get_better_listings(n)
            for listing in item_data['listings']:
                if listing['pricePerUnit'] < n:
                    assert listing in better_listings


@pytest.mark.unittest
class TestMBDataResponse:

    def test_data_property(self, mb_data_data_objs):
        data, resp = mb_data_data_objs
        assert data == resp.data

    def test_data_property_set(self):
        with pytest.raises(UniversalisError):
            obj = MBDataResponse({}, {})
            obj.data = {}

    def test_items_property(self, mb_data_data_objs):
        data, resp = mb_data_data_objs
        data_items = data.get('items')
        if data_items is not None:
            items = {item_id: MBDataResponseItem(item_data) for item_id, item_data in data['items'].items()}
        else:
            item_id = data['itemID']
            items = {item_id: MBDataResponseItem(data)}
        for item, item_obj in zip(items.values(), resp.items.values()):
            assert isinstance(item_obj, MBDataResponseItem)
            assert item.item_id == item_obj.item_id

    def test_items_property_set(self):
        with pytest.raises(UniversalisError):
            obj = MBDataResponse({}, {})
            obj.items = {}

    def test_best_prices_property(self, mb_data_data_objs):
        data, resp = mb_data_data_objs
        data_items = data.get('items')
        if data_items is not None:
            items = data_items.values()
        else:
            items = [data]

        best_prices = {item['itemID']: item['minPrice'] for item in items}
        assert best_prices == resp.best_prices

    def test_listing_ids_property(self, mb_data_data_objs):
        data, resp = mb_data_data_objs

        data_items = data.get('items')
        if data_items is not None:
            items = data_items.values()
        else:
            items = [data]

        listing_ids = []
        for item in items:
            for listing in item['listings']:
                listing_ids.append(listing['listingID'])

        assert resp.listing_ids == listing_ids
