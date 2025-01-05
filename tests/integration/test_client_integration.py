import asyncio
import random

import jsonschema
import pytest

from universalisapi.client import UniversalisAPIClient
from universalisapi.exceptions import UniversalisError
from universalisapi.api_objects.enums import World, DataCenter


@pytest.mark.integration
class TestUniversalisAPIClientIntegration:

    client = UniversalisAPIClient()

    @pytest.mark.asyncio
    async def test_data_centers(self, data_centers):
        resp_data = await self.client.data_centers
        assert resp_data == data_centers

    @pytest.mark.asyncio
    async def test_worlds(self, worlds):
        resp_data = await self.client.worlds
        assert worlds == resp_data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("n",list(range(10)))
    async def test_current_item_price_data_schema(self, n,
                                                  valid_unviersalis_item_ids,
                                                  valid_region_names,
                                                  agg_data_schema_validator):
        region = random.choice(valid_region_names)
        item_ids = random.choices(valid_unviersalis_item_ids, k=20)
        resp = await self.client.current_item_price_data(region, item_ids)
        try:
            agg_data_schema_validator.validate(resp)
        except jsonschema.ValidationError:
            assert False
        else:
            assert True

    @pytest.mark.asyncio
    async def test_current_item_price_data_bad_schema(self,
                                                      valid_unviersalis_item_ids,
                                                      valid_region_names,
                                                      least_recent_schema_validator):
        region = random.choice(valid_region_names)
        item_ids = random.choices(valid_unviersalis_item_ids, k=20)
        resp = await self.client.mb_current_data(item_ids, region)
        with pytest.raises(jsonschema.ValidationError):
            least_recent_schema_validator.validate(resp)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("n",list(range(10)))
    async def test_least_recent_items_schema(self, n, least_recent_schema_validator):
        wds = list(World)
        wds.extend(list(DataCenter))
        w_d = random.choice(wds)
        try:
            resp = await self.client.least_recent_items(w_d)
            assert least_recent_schema_validator.is_valid(resp)
        except UniversalisError:
            pass

    @pytest.mark.asyncio
    async def test_least_recent_items_bad_schema(self, agg_data_schema_validator):
        with pytest.raises(jsonschema.ValidationError):
            resp = await self.client.least_recent_items('crystal')
            agg_data_schema_validator.validate(resp)
