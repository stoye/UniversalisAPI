import logging
from datetime import datetime
from functools import cached_property
from typing import cast

import aiohttp
from .._wrapper import UniversalisAPIWrapper
from ..exceptions import UniversalisError


module_logger = logging.getLogger(__name__)


class MBDataResponseItem(UniversalisAPIWrapper):
    """
    A representation of a specifc item from a Universalis API response.

    Parameters
    ----------
    item_data : dict
        The data representing a Universalis MB Data response for a specific item. This
        is expected to conform to the schema provided by the public Universalis API.

    Attributes
    ----------
    item_id : int
        ID for the item this data represents
    last_upload_time : datetime
        The last upload time for this item on Universalis, as a datetime
        (for raw response in MS, see `last_upload_time_ms`)
    listings : list[dict]
        A list of listings representing entries for this item on the MB in the region.
    listings_count : int
    recent_history : list[dict]
        The currently shown sales of this item.
    recent_history_count : int
    units_for_sale : int
        The number of ITEMS (not listings) up for sale.
    units_sold : int
        The number of ITEMS (not sale events) sold over `recent_history`.
    world_upload_times : dict[int, datetime]
        If the request that generated this object was for a specific world, this will be
        an empty dict. Otherwise, this is a mapping from worldIDs to datetimes.
    """

    _MBDataResponseItem_logger = module_logger.getChild(__qualname__)

    def __init__(self, item_data: dict, *,
                 session: aiohttp.ClientSession | None = None) -> None:
        super().__init__(session=session)
        self._instance_logger = self._MBDataResponseItem_logger.getChild(str(id(self)))

        self._data: dict = item_data
        self.item_id: int = self._data['itemID']
        self._last_upload_time_ms: int = cast(int, self._data.get('lastUploadTime'))
        self.last_upload_time: datetime = datetime.fromtimestamp(
            round(self._last_upload_time_ms / 1000, 4))
        self.listings: list[dict] = self._data['listings']
        self.listings_count: int = self._data['listingsCount']
        self.recent_history: list[dict] = self._data['recentHistory']
        self.recent_history_count: int = self._data['recentHistoryCount']
        self.units_for_sale: int = self._data['unitsForSale']
        self.units_sold: int = self._data['unitsSold']

        # get world_upload_times if it exists
        self._world_upload_times = self._data.get('worldUploadTimes')
        self.world_upload_times: dict[int, datetime]
        if self._world_upload_times is not None:
            self.world_upload_times = dict(
                zip(self._world_upload_times.keys(),
                    map(lambda x: datetime.fromtimestamp(round(x/1000)),
                        self._world_upload_times.values()))
            )
        else:
            self.world_upload_times = {}

        self.histograms = {
            'default': self._data['stackSizeHistogram'],
            'nq': self._data['stackSizeHistogramNQ'],
            'hq': self._data['stackSizeHistogramHQ']
        }

        self.region_info: str | None
        # get region info
        if 'worldName' in self._data:
            self.region_info = self._data['worldName']
        elif 'dcName' in self._data:
            self.region_info = self._data['dcName']
        elif 'regionName' in self._data:
            self.region_info = self._data['regionName']
        else:
            # warn if we can't get the region info
            self._instance_logger.warning(
                "Could not determine region information for item",
                extra={'data': self._data})
            self.region_info = None

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, _) -> None:
        raise UniversalisError("Cannot set data for MBDataResponseItem object")

    @property
    def prices(self) -> dict[str, dict[str, int | float]]:
        """
        Generate a dict of the price data for this MB Item.

        Returns
        -------
        dict[str, dict[str, int | float]]
            A dictionary with mappings for hq and nq values for all price information.
            Entries in `'current'` and `'average'` will be floats if not 0.

        Examples
        --------
        >>> item = MBDataResponseItem({...})
        >>> item.prices['current']
        {'default': 151210.5, 'nq': 151210.5, 'hq': 0}
        """
        price_dict = {
            'current': {
                'default': self._data['currentAveragePrice'],
                'nq': self._data['currentAveragePriceNQ'],
                'hq': self._data['currentAveragePriceHQ']
            },
            'average': {
                'default': self._data['averagePrice'],
                'nq': self._data['averagePriceNQ'],
                'hq': self._data['averagePriceHQ']
            },
            'min': {
                'default': self._data['minPrice'],
                'nq': self._data['minPriceNQ'],
                'hq': self._data['minPriceHQ']
            },
            'max': {
                'default': self._data['maxPrice'],
                'nq': self._data['maxPriceNQ'],
                'hq': self._data['maxPriceHQ']
            }
        }
        return price_dict

    @property
    def best_price(self) -> int:
        """
        Get the best total price for this item.

        Returns
        -------
        price : int
        """
        return cast(int, self.prices['min']['default'])

    @property
    def listing_ids(self) -> list[str]:
        """
        Return a list of listingIDs for this item.

        Returns
        -------
        listing_ids : list[str]
        """
        listing_ids = []
        for listing in self.listings:
            listing_ids.append(listing['listingID'])
        return listing_ids

    def get_better_listings(self, price: int) -> list[dict]:
        """Return list of listing info whose prices are better than the given price."""
        better_listings = []
        for listing in self.listings:
            if listing['pricePerUnit'] < price:
                better_listings.append(listing)

        return better_listings


class MBDataResponse(UniversalisAPIWrapper):
    """
    An abstract representation of a Universalis API response for market board data.

    Parameters
    ----------
    mb_data : dict
        The data representing a Universalis MB Data response. This is expected to
        conform to the schema provided by the public Universalis API.
    params : dict
        The params that were passed along with the request that generated `mb_data`.
    """

    _MBDataResponse_logger = module_logger.getChild(__qualname__)

    def __init__(self, mb_data: dict, params: dict, *,
                 session: aiohttp.ClientSession | None = None) -> None:
        super().__init__(session=session)
        self._instance_logger = self._MBDataResponse_logger.getChild(str(id(self)))

        # store the raw data privately
        self._data = mb_data
        self._params = params

        # initialize the private vars
        self._items: dict[int, MBDataResponseItem]
        self.unresolved_items: list[int] | None
        self._reset()

    def _reset(self) -> None:
        """Reset this object using its new data."""
        # response comes in two forms, so handle both
        if 'items' in self._data:
            # it's a list of items, create a dict of ID -> MBDataResponseItem
            items_list = self._data['items'].values()
            self._items = {item_info['itemID']: MBDataResponseItem(item_info)
                           for item_info in items_list}
        elif 'itemID' in self._data:
            # otherwise, create a dict with the existing data as an MBDataResponseItem
            self._items = {self._data['itemID']: MBDataResponseItem(self._data)}
        else:
            # finally, if no valid items are found for some reason, iniate empty dict
            self._items = {}

        # store a list of the unresolved item IDs if there were any
        self.unresolved_items = self._data.get('unresovledItems')

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, _) -> None:
        raise UniversalisError("Cannot set data of MBDataResponse object")

    @property
    def items(self) -> dict[int, MBDataResponseItem]:
        return self._items

    @items.setter
    def items(self, _) -> None:
        raise UniversalisError("Cannot set items for MBDataResponse object")

    @property
    def best_prices(self) -> dict[int, int]:
        """
        Get the best price for each item in this response.

        Returns
        -------
        dict[int, int]
            Mapping of item_ids to prices.
        """
        prices = {item_id: item.best_price for item_id, item in self._items.items()}
        return prices

    @property
    def listing_ids(self) -> list[str]:
        """
        Return a list of listingIDs for all the items in this request.

        Returns
        -------
        listing_ids : list[str]
        """
        listing_ids = []
        for item in self.items.values():
            listing_ids.extend(item.listing_ids)
        return listing_ids

    async def get_price_changes(self) -> dict[int, dict]:
        """
        Rerun this response's initial search and check for changes.

        This function changes the data stored in this object. Any existing items will
        become inaccessible.

        Returns
        -------
        price_changes : dict[int, dict]
            A dictionary of all items whose best prices have changed, where keys are
            item_ids, and where the values are a dict of the following format:
                'item_id': `int`, the ID of the item
                'old_price': `int`, the previous best price
                'new_price': `int`, the current best price
                'listings': `list[dict]`, the listings that are prices than the
                old price
        """
        # fetch new data
        self._instance_logger.info("Passing params to wrapper call")
        new_data = await self._get_mb_current_data(
            self._params['item_ids'],
            self._params['region'],
            listings=self._params['listings'],
            entries=self._params['entries'],
            hq=self._params['hq'],
            stats_within=self._params['stats_within'],
            entries_within=self._params['entries_within'],
            fields=self._params['fields']
        )

        # setup a dummy MBDataResponse
        # TODO find a better way of doing this?
        self._instance_logger.info("Creating new response object for comparison")
        new_resp_obj = MBDataResponse(new_data, self._params.copy())

        price_changes: dict[int, dict] = {}
        item_comp_dict: dict[int, tuple[MBDataResponseItem, MBDataResponseItem]] = {
            item_id: item_comp_info
            for item_id, item_comp_info in
            zip(self.items.keys(),
                zip(self.items.values(),
                    new_resp_obj.items.values()
                    )
                )
        }

        for item_id, (old_item, new_item) in item_comp_dict.items():
            price_changes[item_id] = {
                'item_id': item_id,
                'old_price': old_item.best_price,
                'new_price': new_item.best_price,
                'listings': new_item.get_better_listings(old_item.best_price)
            }

        return price_changes
