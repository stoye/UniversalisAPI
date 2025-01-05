import logging

import aiohttp

from .._wrapper import UniversalisAPIWrapper
from ..exceptions import UniversalisError


module_logger = logging.getLogger(__name__)


class MBDataResponse(UniversalisAPIWrapper):
    """
    An abstract representation of a Universalis API response for market board data.

    :param items: dict[int, MBDataResponseItem]
    :param unresolved_items: list[int] of item IDs for which data could not be found
    """

    _MBDataResponse_logger = module_logger.getChild(__qualname__)

    def __init__(self, mb_data: dict, params: dict):
        super().__init__()
        self._instance_logger = self._MBDataResponse_logger.getChild(str(id(self)))

        self._data = mb_data
        self._params = params

        if 'items' in self._data:
            items_dict = self._data['items'].items()
            self._items = {item_id: MBDataResponseItem(item_info) for item_id, item_info in items_dict}
        elif 'itemID' in self._data:
            self._items = {self._data['itemID']: MBDataResponseItem(self._data)}
        else:
            self._items = {}

        self.unresolved_items = self._data.get('unresovledItems')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, _):
        raise UniversalisError("Cannot set data of MBDataResponse object")

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, _):
        raise UniversalisError("Cannot set items for MBDataResponse object")

    def get_listing_ids(self):
        listing_ids = []
        for item in self.items.values():
            listing_ids.extend(item.get_listing_ids())
        return listing_ids


class MBDataResponseItem:
    """
    An abstract representation of a Universalis API response for market board data about a specific item
    """

    _MBDataResponseItem_logger = module_logger.getChild(__qualname__)

    def __init__(self, item_data: dict):
        self._instance_logger = self._MBDataResponseItem_logger.getChild(str(id(self)))

        self._data = item_data
        self.item_id = self._data['itemID']
        self.listings = self._data['listings']

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, _):
        raise UniversalisError("Cannot set data for MBDataResponseItem object")

    def get_listing_ids(self):
        listing_ids = []
        for listing in self.listings:
            listing_ids.append(listing['listingID'])
        return listing_ids