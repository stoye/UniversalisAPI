"""Python client for interacting with Universalis.app."""

import logging
from typing import cast

import async_property

from .api_objects.mb_data import MBDataResponse
from ._wrapper import UniversalisAPIWrapper
from .exceptions import UniversalisError
from .api_objects.enums import DataCenter, World, APIRegion


module_logger = logging.getLogger(__name__)


class UniversalisAPIClient(UniversalisAPIWrapper):
    """Asynchronous client for accessing Universalis.app's API endpoints."""

    _UniversalisAPIClient_logger = module_logger.getChild(__qualname__)

    def __init__(self, api_key: str = '') -> None:
        super().__init__()
        self._instance_logger = self._UniversalisAPIClient_logger.getChild(
            str(id(self)))
        self.api_key = api_key

        self._worlds: list[dict] = []
        self._dcs: list[dict] = []

    @async_property.async_cached_property
    async def data_centers(self) -> list[dict]:
        """
        Cached list of data center info supported by Universalis API.

        Returns
        -------
        data_centers : list[dict]
        """
        if not self._dcs:
            self._instance_logger.debug("Performing first cache of DCs")
            self._dcs = cast(list[dict], await self.get_endpoint('/data-centers'))
        return self._dcs

    @async_property.async_cached_property
    async def data_center_names(self) -> list[str]:
        """
        Get a list of DC names supported by the API.

        Returns
        -------
        dc_names : :obj:list of :obj:str
            All items in this list should be in
            ``universalisapi.api_objects.enums.DataCenter``.
        """
        resp = await self.data_centers
        dcs = [dc['name'].lower() for dc in resp]
        return dcs

    @async_property.async_cached_property
    async def data_center_worlds(self) -> dict[str, list[int]]:
        """
        Get a dict of DC names mapped to a list of World IDs.

        Returns
        -------
        dict[str, list[int]]
            A mapping from ``universalisapi.api_objects.enums.DataCenter`` to
            ``int``s representing world IDs (can be compared with IDs from
            ``UniversalisClient.worlds``).
        """
        resp = await self.data_centers
        dcs = {}
        for dc in resp:
            dcs[dc['name'].lower()] = dc['worlds']
        return dcs

    @async_property.async_cached_property
    async def worlds(self) -> list[dict]:
        """
        Return a list of World id->name dicts supported by the API.

        Returns
        -------
        list[dict]
        """
        if not self._worlds:
            self._instance_logger.debug("Performing first cache of Worlds")
            self._worlds = cast(list[dict], await self.get_endpoint('/worlds'))
        return self._worlds

    @async_property.async_cached_property
    async def world_names(self) -> list[str]:
        """
        Return a list of World names supported by the API.

        Returns
        -------
        list[str]
            All items in this list should be in
            ``universalisapi.api_objects.enums.World``.
        """
        resp = await self.worlds
        worlds = [world['name'].lower() for world in resp]
        return worlds

    async def current_item_price_data(self, region: APIRegion,
                                      item_ids: list[int]) -> dict:
        """
        Get aggregated market board data for the given items in the given region.

        Returns a list of results for each item searched, as well as a list of items
        that resulted in a failed search.

        Parameters
        ----------
        region : APIRegion
            The region from which to retrieve prices
        item_ids : list[int]
            A list of item IDs for which to retrieve prices

        Returns
        -------
        dict
            The JSON response from Universalis is of the following format:
                'results' -> `list[dict]` of item information for given IDs
                'failedItems' -> `list[int]` of item IDs for which Universalis could not
                    find data
        """
        self._instance_logger.info("Checking region")
        self._check_region_name(region)
        self._instance_logger.debug("Capping item_id list at 100")
        item_ids = item_ids[:100]
        endpoint = f'/aggregated/{region}/{",".join(map(str,item_ids))}'
        data = cast(dict, await self.get_endpoint(endpoint))
        return data

    @staticmethod
    def parse_region_data[I](data: dict[str, I]) -> I:
        """
        Return the most relevant data from a region dataset.

        Prefers to return more specific information. Will return World data,
        then DC data, and finally Region data, depending on what is available.

        Parameters
        ----------
        data : dict[str, Any]
            The data to be parsed

        Returns
        -------
        Any
            The data from the most specific key.

        Raises
        ------
        UniversalisError
            If 'world', 'dc', or 'region' are not keys in the provided `dict`.
        """
        if 'world' in data:
            return data['world']
        elif 'dc' in data:
            return data['dc']
        elif 'region' in data:
            return data['region']
        else:
            raise UniversalisError("region data not found")

    async def current_average_item_price(self,
                                         region: APIRegion,
                                         item_ids: list[int], *,
                                         hq: bool = True) -> dict[int, int]:
        """
        Get the average sale price for the given list of items in the given region.

        Average prices are rounded to the nearest gil.

        Parameters
        ----------
        region : APIRegion
            The region from which to retrieve prices
        item_ids : list[int]
            A list of item IDs for which to retrieve prices
        hq : bool, optional
            Whether to return data for HQ or NQ items. Defaults to True.
            If HQ data is unavailable (for example, for gatherables, which cannot
            be HQ), NQ is used instead.

        Returns
        -------
        dict[int, int]
            A mapping of the provided item IDs to their average prices
        """
        self._instance_logger.info("Getting item price data")
        item_data = await self.current_item_price_data(region, item_ids)
        avg_prices = {}
        failed_items = item_data['failedItems']
        if failed_items:
            self._instance_logger.info("Couldn't find information for all item ids",
                                       extra={'failed_items': failed_items})

        for item in item_data['results']:
            asp_hq_info = item['hq']['averageSalePrice']
            if hq and asp_hq_info:
                avg_price = self.parse_region_data(asp_hq_info)['price']
            else:
                avg_price = self.parse_region_data(item['nq']['averageSalePrice'])
                avg_price = avg_price['price']
            avg_prices[item['itemId']] = round(avg_price)

        return avg_prices

    async def least_recent_items(self, world_or_dc: World | DataCenter,
                                 entries: int | None = None) -> list[dict]:
        """
        Get a list of the least recently updated items in Universalis.

        Parameters
        ----------
        world_or_dc : World or DataCenter
            The world or DC for which to retrieve the least recently updated items.
        entries : int, optional
            How many entries to retrieve. API default is 50, and will not return more
            than 200.

        Returns
        -------
        list[dict]

        Raises
        ------
        UniversalisError
            If world_or_dc is not a `World` or `DataCenter`.
        """
        endpoint = '/extra/stats/least-recently-updated'
        params: dict[str, str | int] = {}
        if entries is not None:
            params['entries'] = entries
        if world_or_dc in World:
            params['world'] = world_or_dc
        elif world_or_dc in DataCenter:
            params['dcName'] = world_or_dc
        else:
            raise UniversalisError("First argument must be World or DataCenter")

        resp = cast(list[dict], await self.get_endpoint(endpoint, params=params))
        return resp

    async def mb_current_data(self,
                              item_ids: list[int],
                              region: APIRegion, *,
                              listings: int | None = None,
                              entries: int | None = None,
                              hq: bool | None = None,
                              stats_within: int | None = None,
                              entries_within: int | None = None,
                              fields: list[str] | None = None) -> MBDataResponse:
        """
        Return an ``MBDataResponse`` object from /``region``/``item_ids``.

        Parameters
        ----------
        item_ids : list[int]
        region : APIRegion

        Returns
        -------
        mb_data : MBDataResponse

        Other Parameters
        ----------------
        listings : int, optional
        entries : int, optional
        hq : bool, optional
        stats_within : int, optional
        entries_within : int, optional
        fields : list[str]
        """
        self._instance_logger.info("Checking region info")
        self._check_region_name(region)
        data = await self._get_mb_current_data(
            item_ids, region,
            listings=listings, entries=entries, hq=hq, stats_within=stats_within,
            entries_within=entries_within, fields=fields)
        params = {'item_ids': item_ids,
                  'region': region,
                  'listings': listings,
                  'entries': entries,
                  'hq': hq,
                  'stats_within': stats_within,
                  'entries_within': entries_within,
                  'fields': fields}
        return MBDataResponse(data, params)
