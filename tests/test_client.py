import pytest
import json

from aioresponses import aioresponses

from universalisapi.client import UniversalisAPIClient
from universalisapi.exceptions import UniversalisError

class TestUniversalisAPIClient:
    client = UniversalisAPIClient()
    with open('data-centers.json', 'r', encoding='utf-8') as f:
        data_centers = json.load(f)
    with open('worlds.json', 'r', encoding='utf-8') as f:
        worlds = json.load(f)
    with open('current-item-price-data.json', 'r', encoding='utf-8') as f:
        current_item_price_data = json.load(f)
    with open('least-recently-updated_100_crystal.json', 'r', encoding='utf-8') as f:
        least_recently_updated_100_crystal = json.load(f)
    with open('least-recently-updated_20_coeurl.json', 'r', encoding='utf-8') as f:
        least_recently_updated_20_coeurl = json.load(f)

    @pytest.fixture
    def mocked_data_centers(self, mocked_response):
        mocked_response.get(f'{self.client.base_url}/data-centers',
                            status=200,
                            payload=self.data_centers)

    @pytest.mark.asyncio
    async def test_data_centers(self, mocked_data_centers):
        dcs = await self.client.data_centers
        assert dcs == self.data_centers

    @pytest.mark.asyncio
    async def test_data_center_names(self, mocked_data_centers):
        dc_names = await self.client.data_center_names()
        data_center_names = [dc['name'] for dc in self.data_centers]
        assert dc_names == data_center_names

    @pytest.mark.asyncio
    async def test_data_center_worlds(self, mocked_data_centers):
        dc_worlds = await self.client.data_center_worlds()
        data_center_worlds = {}
        for dc in self.data_centers:
            data_center_worlds[dc['name']] = dc['worlds']
        assert dc_worlds == data_center_worlds

    @pytest.fixture
    def mocked_worlds(self, mocked_response):
        mocked_response.get(f'{self.client.base_url}/worlds',
                            status=200,
                            payload=self.worlds)

    @pytest.mark.asyncio
    async def test_worlds(self, mocked_worlds):
        worlds = await self.client.worlds
        assert worlds == self.worlds

    @pytest.mark.asyncio
    async def test_world_names(self, mocked_worlds):
        world_names = await self.client.world_names()
        wns = [world['name'] for world in self.worlds]
        assert wns == world_names

    @pytest.fixture
    def mocked_aggregated(self, mocked_response):
        mocked_response.get(f'{self.client.base_url}/aggregated/coeurl/42884,20',
                            status=200,
                            payload=self.current_item_price_data)

    @pytest.mark.asyncio
    async def test_current_item_price_data(self, mocked_aggregated):
        data = await self.client.current_item_price_data('coeurl', [42884, 20])
        assert data == self.current_item_price_data

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
        with pytest.raises(UniversalisError) as e:
            data = self.client.parse_region_data({})

    @pytest.mark.asyncio
    @pytest.mark.parametrize("hq", [True, False])
    async def test_current_item_price(self, mocked_aggregated, hq):
        data = await self.client.current_item_price('coeurl', [42884, 20], hq)
        if hq:
            assert data == {42884: 123040}
        else:
            assert data == {42884: 30000}

    @pytest.mark.asyncio
    async def test_least_recent_items_failure(self):
        with pytest.raises(UniversalisError) as e:
            data = await self.client.least_recent_items()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('world_dc_data,entries,data',
                             [(['dcName', 'crystal'], 100, least_recently_updated_100_crystal),
                              (['world', 'coeurl'], 20, least_recently_updated_20_coeurl)])
    async def test_least_recent_items(self, mocked_response, world_dc_data, entries, data):
        base_url = (f'{self.client.base_url}/extra/stats/least-recently-updated?'
                    f'{world_dc_data[0]}={world_dc_data[1]}&entries={entries}')
        mocked_response.get(base_url, status=200, payload=data)
        if 'world' in world_dc_data:
            resp_data = await self.client.least_recent_items(world=world_dc_data[1], entries=entries)
        else:
            resp_data = await self.client.least_recent_items(dc=world_dc_data[1], entries=entries)
        assert data == resp_data