import asyncio

import pytest

from universalisapi.client import UniversalisAPIClient


@pytest.mark.integration
class TestUniversalisAPIClientIntegration:

    client = UniversalisAPIClient()

    @pytest.mark.asyncio
    async def test_data_centers(self, data_centers):
        resp_data = await self.client.data_centers
        assert resp_data == data_centers

    @pytest.mark.asyncio
    async def test_worlds(self, worlds):
        loop = asyncio.new_event_loop()
        resp_data = await self.client.worlds
        assert worlds == resp_data