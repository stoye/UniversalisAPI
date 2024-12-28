import logging
import asyncio
from collections.abc import Iterable
from typing import Any

import aiohttp
import async_property

from .decos import timed
from .wrapper import UniversalisAPIWrapper
from .exceptions import UniversalisError


class UniversalisAPIClient(UniversalisAPIWrapper):
    """
    Asynchronous client for accessing Universalis.app's API endpoints.
    Parameters
    ------------
    api_key: str
        The API key used with Universalis.app's API
    session: aiohttp.ClientSession
        This client's aiohttp session (will be created if not provided
    """

    def __init__(self, api_key: str = '', session: aiohttp.ClientSession | None = None) -> None:
        super().__init__(session)
        self.api_key = api_key

        self._worlds = {}
        self._dcs = {}

    @async_property.async_cached_property
    async def data_centers(self) -> list[dict]:
        """
        Cached list of data center info supported by Universalis API
        :return:
        """
        if not self._dcs:
            self._dcs = await self.get_endpoint('/data-centers')
        return self._dcs

    @timed
    async def data_center_names(self) -> list[str]:
        """
        Get a list of DC names supported by the API
        :return: list[str] of DC names
        """
        resp = await self.data_centers
        dcs = [dc['name'] for dc in resp]
        return dcs

    @timed
    async def data_center_worlds(self) -> dict[str, list[int]]:
        """
        Get a dict of DC names mapped to a list of World IDs
        :return: dict[str, list[int]] of DC name->World IDs
        """
        resp = await self.data_centers
        dcs = {}
        for dc in resp:
            dcs[dc['name']] = dc['worlds']
        return dcs

    @async_property.async_cached_property
    async def worlds(self) -> list[dict]:
        """
        Return a list of World id->name dicts supported by the API

        List of Dictionaries of Worlds containing:
        'id' -> int World ID
        'name' -> str World name
        :return: list[dict] of Worlds
        """
        if not self._worlds:
            self._worlds = await self.get_endpoint('/worlds')
        return self._worlds

    @timed
    async def world_names(self) -> list[str]:
        """
        Return a list of World names supported by the API
        :return: a list of World names
        """
        resp = await self.worlds
        worlds = [world['name'] for world in resp]
        return worlds

    @timed
    async def current_item_price_data(self, region: str, item_ids: list[int]) -> dict:
        """
        Get aggregated market board data for the given items in the given region

        Returns a list of results for each item searched, as well as a list of items that resulted in a failed search.
        Return response:
        'results' -> List[Dict] of item information for given IDs
        'failedItems' -> List[int] of item IDs not supported by Universalis
        :param region: str The world, DC, or Region to retrieve data for
        :param item_ids: Iterable[int] a list of item IDs to retrieve data for
        :return: Dict of the full response from Universalis (for more functionality see other methods)
        """
        endpoint = f'/aggregated/{region}/{",".join(map(str,item_ids))}'
        return await self.get_endpoint(endpoint)

    @staticmethod
    def parse_region_data(data: dict[str, Any]) -> Any:
        """
        Return the most relevant data from a region dataset (world, then dc, then region)
        :param data: dict of data to be parsed
        :return:
        :raises: UniversaliseError if no region data is found
        """
        if 'world' in data:
            return data['world']
        elif 'dc' in data:
            return data['dc']
        elif 'region' in data:
            return data['region']
        else:
            raise UniversalisError("region data not found")

    @timed
    async def current_item_price(self, region: str, item_ids: list[int], hq: bool = True) -> dict[int, int]:
        """
        Get the average sale price for the given list of items in the given region

        Average prices are rounded to the nearest gil.
        :param region: the world, DC, or region to retrieve data for
        :param item_ids: the item IDs to retrieve average prices for
        :param hq: Whether to return the HQ or NQ item prices. Defaults to True for HQ. Will provide NQ data if HQ unavailable
        :return: a dict of itemID->itemPrice
        """
        item_data = await self.current_item_price_data(region, item_ids)
        avg_prices = {}

        for item in item_data['results']:
            asp_hq_info = item['hq']['averageSalePrice']
            if hq and asp_hq_info:
                avg_price = self.parse_region_data(asp_hq_info)['price']
            else:
                avg_price = self.parse_region_data(item['nq']['averageSalePrice'])['price']
            avg_prices[item['itemId']] = round(avg_price)

        return avg_prices

    @timed
    async def least_recent_items(self, world: str = None, dc: str = None, entries: int = None) -> list[dict]:
        """
        Get a list of the least recently updated items in Universalis. Must supply a world or DC
        :param world: the world to get a list for
        :param dc: the dc to get a list for
        :param entries: the number of entries to return (API default if None, max 200)
        :return: list of item responses
        """
        endpoint = '/extra/stats/least-recently-updated'
        params = {}
        if entries is not None and 0 < entries <= 200:
            params['entries'] = entries
        if world:
            params['world'] = world
        elif dc:
            params['dcName'] = dc
        else:
            raise UniversalisError("Must supply world or dc name for least recent items request")

        return await self.get_endpoint(endpoint, params=params)

    @timed
    async def mb_current_data(self,
                              item_ids: list[int],
                              region: str,
                              listings: int = None,
                              entries: int = None,
                              hq: bool = None,
                              stats_within: int = None,
                              entries_within: int = None,
                              fields: list[str] = None) -> dict:
        """
        Return the current market board data for the given list of items in the given region.
        :param item_ids: list of items to return data for
        :param region: region to gather data
        :param listings: number of active listings to return, if none provided will return all listings
        :param entries: number of recent history entries to return per item, if non provided the default max is 5
        :param hq: whether to return hq or nq entries and listings. returns both if none, hq if True, nq if False
        :param stats_within: the amount of time before now in ms to calculate stats over. API default is 7 days
        :param entries_within: the amount of time before now to take entries within, in seconds
        :param fields: list of API fields that should be included with the response, if None returns all fields
        :return: the full API response
        """
        endpoint = f'/{region}/{",".join(map(str, item_ids))}'
        params = {}
        if listings is not None:
            params['listings'] = listings
        if entries is not None:
            params['entries'] = entries
        if hq is not None:
            params['hq'] = str(hq).lower()
        if stats_within is not None:
            params['statsWithin'] = stats_within
        if entries_within is not None:
            params['entriesWithin'] = entries_within
        if fields is not None:
            params['fields'] = ','.join(fields)

        return await self.get_endpoint(endpoint, params=params)