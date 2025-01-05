import logging
from typing import cast

import aiohttp

from .exceptions import UniversalisError
from .api_objects.enums import APIRegion, Region, DataCenter, World


# configure module logging
module_logger = logging.getLogger(__name__)


class UniversalisAPIWrapper:
    """
    Wrapper class for UniversalisAPI Objects.

    Generally deals with raw JSON responses rather than more abstracted objects.
    Also handles management of :any:`aiohttp.ClientSession` objects.

    Parameters
    ----------
    session : aiohttp.ClientSession or None, optional
        A `ClientSession` object to use for handling requests.

    Attributes
    ----------
    base_url : str
        The base URL for UniversalisAPI.app
    valid_fields : list[str]
        A list of valid fields to pass to ``UniversalisAPIClient.get_mb_current_data``
    valid_regions : list[str]
        A list of valid regions to request data for
    """

    base_url = "https://universalis.app/api/v2"
    valid_fields = [
        'itemID',
        'lastUploadTime',
        'listings',
        'recentHistory',
        'currentAveragePrice',
        'currentAveragePriceNQ',
        'currentAveragePriceHQ',
        'regularSaleVelocity',
        'nqSaleVelocity',
        'hqSaleVelocity',
        'averagePrice',
        'averagePriceNQ',
        'averagePriceHQ',
        'minPrice',
        'minPriceNQ',
        'minPriceHQ',
        'maxPrice',
        'maxPriceNQ',
        'maxPriceHQ',
        'stackSizeHistogram',
        'stackSizeHistogramNQ',
        'stackSizeHistogramHQ',
        'listingsCount',
        'recentHistoryCount',
        'unitsForSale',
        'unitsSold',
        'hasData'
    ]
    valid_regions = [
        'japan',
        'europe',
        'north-america',
        'oceania',
        'china',
        '中国'
    ]
    _UniversalisAPIWrapper_logger = module_logger.getChild(__qualname__)

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._session = session
        # instance logger
        self._instance_logger = self._UniversalisAPIWrapper_logger.getChild(
            str(id(self)))

    @property
    def session(self) -> aiohttp.ClientSession:
        """
        Retrieve the ``aiohttp.ClientSession`` object for this Wrapper.

        Returns
        -------
        session : aiohttp.ClientSession
        """
        if self._session is None or self._session.closed:
            self._instance_logger.debug("Creating new aiohttp ClientSession object")
            self._session = aiohttp.ClientSession()
        return self._session

    async def _process_response(self, response: aiohttp.ClientResponse) -> None:
        """
        Raise an error if response code is not 200.

        Parameters
        ----------
        response : aiohttp.ClientResponse
            A ``ClientResponse`` to check for error codes.

        Raises
        ------
        UniversalisError
            If a non-200 code is received.
        """
        if response.status == 400:
            self._instance_logger.warning("Error code 400")
            raise UniversalisError(f"Invalid parameters (code 400): {response.url}")
        elif response.status == 404:
            self._instance_logger.warning("Error code 404")
            raise UniversalisError(
                f"World/DC/Region or requested item is invalid (code 404): "
                f"{response.url}")
        elif response.status != 200:
            self._instance_logger.warning("Non-200 response code received",
                                          extra={'response_code': response.status})
            raise UniversalisError(f"{response.status} code received: {response.url}")
        else:
            self._instance_logger.info("200 code received, processing complete")
            return

    async def get_endpoint(self, endpoint: str, *,
                           params: dict | None = None) -> dict | list[dict]:
        """
        Retrieve data from the given Universalis API endpoint as JSON.

        Parameters
        ----------
        endpoint : str
            The endpoint (relative to `base_url`) to get
        params : dict[str, str], optional
            A dictionary of parameters to be passed to the `get` request

        Returns
        -------
        response_data : dict or list
            The JSON from the endpoint (as a dict or list)

        Raises
        ------
        UniversalisError
            If response object could not be read as JSON
        """
        #generate full url
        url = self.base_url + endpoint
        if params is None:
            params = {}
        self._instance_logger.debug("Sending endpoint request",
                                    extra={'url': url, 'params': params})
        async with self.session as session:
            async with session.get(url, params=params) as response:
                self._instance_logger.debug("Response created, processing object")
                await self._process_response(response)
                # try to get the data
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError as e:
                    self._instance_logger.warning(
                        "JSON data expected, but not received",
                        extra={'content-type': response.content_type,
                               'error': e})
                    raise UniversalisError(e)
                else:
                    return data

    def _check_region_name(self, region: str) -> None:
        """
        Check if the given region name is valid.

        Raises
        ------
        UniversalisError
            If region name is not ``APIRegion``.
        """
        region = region.lower()
        if region not in Region and region not in DataCenter and region not in World:
            self._instance_logger.warning("Invalid region", extra={'region': region})
            raise UniversalisError(f"{region} is not a valid region")
        else:
            return

    async def _get_mb_current_data(self,
                                   item_ids: list[int],
                                   region: APIRegion, *,
                                   listings: int | None = None,
                                   entries: int | None = None,
                                   hq: bool | None = None,
                                   stats_within: int | None = None,
                                   entries_within: int | None = None,
                                   fields: list[str] | None = None) -> dict:
        """
        Retrieve the data at /``region``/``item_ids``.

        Parameters
        ----------
        item_ids : list[int]
            A list of item IDs for which to retrieve Market Board data.
            Universalis' API disallows lists longer than 100 items, so this list
            will be auot-sliced at item 100
        region : str
            An APIRegion

        Returns
        -------
        mb_data : dict

        Other Parameters
        ----------------
        listings : int, optional
        entries : int, optional
        hq : bool, optional
        stats_within : int, optional
        entries_within : int, optional
        fields : list[str], optional
        """
        self._instance_logger.debug("Capping item_ids at 100")
        item_ids = item_ids[:100]
        endpoint = f'/{region}/{",".join(map(str, item_ids))}'
        params: dict[str, str | int] = {}
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

        resp = cast(dict, await self.get_endpoint(endpoint, params=params))
        return resp
