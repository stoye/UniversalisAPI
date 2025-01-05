import random
import string

import pytest

from universalisapi.client import UniversalisAPIClient
from universalisapi.exceptions import UniversalisError


@pytest.mark.unittest
class TestUniversalisAPIClient:
    client = UniversalisAPIClient()

    @pytest.mark.asyncio
    async def test_data_centers(self, mocked_data_centers, data_centers):
        dcs = await self.client.data_centers
        assert dcs == data_centers

    @pytest.mark.asyncio
    async def test_data_center_names(self, mocked_data_centers, data_centers):
        dc_names = await self.client.data_center_names
        data_center_names = [dc['name'].lower() for dc in data_centers]
        assert dc_names == data_center_names

    @pytest.mark.asyncio
    async def test_data_center_worlds(self, mocked_data_centers, data_centers):
        dc_worlds = await self.client.data_center_worlds
        data_center_worlds = {}
        for dc in data_centers:
            data_center_worlds[dc['name'].lower()] = dc['worlds']
        assert dc_worlds == data_center_worlds

    @pytest.mark.asyncio
    async def test_worlds(self, mocked_worlds, worlds):
        w = await self.client.worlds
        assert w == worlds

    @pytest.mark.asyncio
    async def test_world_names(self, mocked_worlds, worlds):
        world_names = await self.client.world_names
        wns = [world['name'].lower() for world in worlds]
        assert wns == world_names

    @pytest.mark.asyncio
    async def test_current_item_price_data(self, mocked_aggregated, aggregate_data_parametrized):
        stem, data = aggregate_data_parametrized
        region, item_ids = stem.split('_')
        mocked_aggregated(item_ids, region, data)
        item_ids = list(map(int, item_ids.split(',')))
        resp_data = await self.client.current_item_price_data(region, item_ids)
        assert resp_data == data

    @pytest.mark.parametrize("test,expected",
                             [({'world': 1, 'dc': 2, 'region': 3}, 1),
                              ({'dc': 2, 'region': 3}, 2),
                              ({'world': 1, 'region': 3}, 1),
                              ({'world': 1, 'dc': 2}, 1),
                              ({'world': 1}, 1),
                              ({'dc': 2}, 2),
                              ({'region': 3}, 3)])
    def test_parse_region_data(self, test, expected):
        data = self.client.parse_region_data(test)
        assert data == expected

    def test_parse_region_data_fail(self):
        with pytest.raises(UniversalisError):
            data = self.client.parse_region_data({})

    @pytest.mark.asyncio
    @pytest.mark.parametrize("hq", [True, False])
    @pytest.mark.skip
    async def test_current_item_price(self, mocked_aggregated, hq, aggregate_data_parametrized):
        stem, data = aggregate_data_parametrized
        region, item_ids = stem.split('_')
        mocked_aggregated(item_ids, region, data)
        item_ids = list(map(int, item_ids.split(',')))
        resp_data = await self.client.current_average_item_price(region, item_ids, hq=hq)
        if hq:
            assert resp_data == {42884: 116110}
        else:
            assert resp_data == {42884: 120000}

    @pytest.mark.asyncio
    async def test_least_recent_items_failure(self):
        with pytest.raises(UniversalisError):
            await self.client.least_recent_items('blah')

    @pytest.mark.asyncio
    async def test_least_recent_items(self, mocked_least_recent_items, least_recent_data_parametrized):
        stem, data = least_recent_data_parametrized
        world_dc, world_dc_name, entries = stem.split('_')
        entries = int(entries)
        mocked_least_recent_items(world_dc, world_dc_name, entries, data)
        resp_data = await self.client.least_recent_items(world_dc_name, entries=entries)
        assert data == resp_data

    @pytest.mark.asyncio
    async def test_mb_current_data(self, mb_data_data_parser, mocked_mb_current_data):
        w_d_r, region, items_str, item_ids, data = mb_data_data_parser
        mocked_mb_current_data(region, items_str, {}, data)
        resp = await self.client.mb_current_data(item_ids, region)
        assert resp.data == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("l,e,hq,s_w,e_w,f",
                             [
                                 (
                                     random.randint(0, 100),
                                     random.randint(0, 100),
                                     random.choice([True, False]),
                                     random.randint(0, 10000),
                                     random.randint(0, 10000),
                                     random.choices(UniversalisAPIClient.valid_fields, k=random.randint(1,3))
                                 )
                                 for _ in range(20)
                             ])
    async def test_mb_current_data_params(self, l, e, hq, s_w, e_w, f,
                                          mb_data_data_parser,
                                          mocked_mb_current_data):
        w_d_r, region, items_str, item_ids, data = mb_data_data_parser
        params = {
            'listings': l,
            'entries': e,
            'hq': str(hq).lower(),
            'statsWithin': s_w,
            'entriesWithin': e_w,
            'fields': ','.join(f)
        }
        mocked_mb_current_data(region, items_str, params, data)
        resp = await self.client.mb_current_data(item_ids, region,
                                                 listings=l, entries=e, hq=hq,
                                                 stats_within=s_w, entries_within=e_w,
                                                 fields=f)
        assert data == resp.data