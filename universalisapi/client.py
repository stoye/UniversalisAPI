import logging
import asyncio
from collections.abc import Iterable

import aiohttp

from .decos import timed
from .exceptions import UniversalisError

class UniversalisAPIClient:
    """
    Asynchronous client for accessing Universalis.app's API endpoints.
    Parameters
    ------------
    api_key: str
        The API key used with Universalis.app's API
    session: aiohttp.ClientSession
        This client's aiohttp session (will be created if not provided
    """

    base_url = "https://universalis.app/api/v2"

    def __init__(self, api_key: str = '', session: aiohttp.ClientSession | None = None) -> None:
        self.api_key = api_key
        self._session = session

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _process_response(self, response: aiohttp.ClientResponse) -> dict[str, str] | list:
        """
        Check response for errors, and if none are found, pass along response json.

        :param response: aiohttp.ClientResponse object result from self.session.get() call
        :return: Dict or List of the json from the response object
        :raise: UniversalisError if non-200 status code
        """
        if response.status != 200:
            raise UniversalisError(f"{response.status} code received")
        else:
            return await response.json()

    async def get_url_endpoint(self, endpoint: str, params: dict[str, str] = None) -> dict[str, str] | list:
        """
        Create and process a request to the Universalis API at the given endpoint with the given parameters if specified
        :param endpoint: the specific endpoint to request
        :param params: optional parameters (added as ?key=value)
        :return: The JSON response from Universalis as a Dictionary or List
        """
        # generate the full url to request
        url = self.base_url + endpoint
        if params is None:
            params = {}
        # send request
        async with self.session.get(url, params=params) as response:
            return await self._process_response(response)

    @timed
    async def data_centers(self) -> list[dict]:
        """
        Return a list of Data Centers supported by the API

        List of Dictionaries of DCs containing:
        'name' -> str DC name
        'region' -> str Global region
        'worlds' -> list[int] of World IDs
        :return: list[dict] of DCs
        """
        # endpoint
        endpoint = '/data-centers'
        # get response
        return await self.get_url_endpoint(endpoint)

    @timed
    async def data_center_names(self) -> list[str]:
        """
        Get a list of DC names supported by the API
        :return: list[str] of DC names
        """
        resp = await self.data_centers()
        dcs = []
        for dc in resp:
            dcs.append(dc['name'])
        return dcs

    @timed
    async def data_center_worlds(self) -> dict[str, list[int]]:
        """
        Get a dict of DC names mapped to a list of World IDs
        :return: dict[str, list[int]] of DC name->World IDs
        """
        resp = await self.data_centers()
        dcs = {}
        for dc in resp:
            dcs[dc['name']] = dc['worlds']
        return dcs

    @timed
    async def worlds(self) -> list[dict]:
        """
        Return a list of World id->name dicts supported by the API

        List of Dictionaries of Worlds containing:
        'id' -> int World ID
        'name' -> str World name
        :return: list[dict] of Worlds
        """
        #endpoint
        endpoint = '/worlds'
        # get response
        return await self.get_url_endpoint(endpoint)

    @timed
    async def world_names(self) -> list[str]:
        """
        Return a list of World names supported by the API
        :return: a list of World names
        """
        worlds = []
        resp = await self.worlds()
        for world in resp:
            worlds.append(world['name'])
        return worlds

    @timed
    async def current_item_price_data(self, region: str, item_ids: Iterable[int]) -> dict:
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
        return await self.get_url_endpoint(endpoint)

    def _parse_region_data(self, data: dict):
        """
        Return the most relevant data from a region dataset
        :param data:
        :return:
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
    async def current_item_price(self, region: str, item_ids: Iterable[int], hq: bool = True) -> dict[int, int]:
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
            avg_price = 0
            if hq and asp_hq_info:
                avg_price = self._parse_region_data(asp_hq_info)['price']
            else:
                avg_price = self._parse_region_data(item['nq']['averageSalePrice'])['price']
            avg_prices[item['itemId']] = round(avg_price)

        return avg_prices

    @timed
    async def least_recent_items(self, world: str = '', dc: str = '', entries: int = None) -> list[dict]:
        """
        Get a list of the least recently updated items in Universalis. Must supply a world or DC
        :param world: the world to get a list for
        :param dc: the dc to get a list for
        :param entries: the number of entries to return (API default if None, max 200)
        :return: list of item responses
        """
        endpoint = '/extra/stats/least-recently-updated'
        params = {}
        if entries and 0 < entries <= 200:
            params['entries'] = entries
        if not world and not dc:
            raise UniversalisError("must supply world or dc for least recent items request")
        if world:
            params['world'] = world
        else:
            params['dcName'] = dc

        return await self.get_url_endpoint(endpoint, params=params)

    @timed
    async def mb_current_data(self, item_ids: Iterable[int], region: str, listings: int = None, entries: int = None, hq: bool = None, stats_within: int = None, entries_within: int = None, fields: Iterable[str] = None) -> dict:
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

        return await self.get_url_endpoint(endpoint, params=params)