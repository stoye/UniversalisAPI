import logging
import asyncio

import aiohttp
import async_property
from pythonjsonlogger.json import JsonFormatter

from .exceptions import UniversalisError

# configure module logging
module_logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_formatter = JsonFormatter()
log_handler.setFormatter(log_formatter)
module_logger.addHandler(log_handler)


class UniversalisAPIWrapper:
    """
    Wrapper class for UniversalisAPI Objects. Handles interacting with aiohttp ClientSession objects

    :param session: class:`aiohttp.ClientSession`
    :param base_url: the base url of the Universalis API
    """

    base_url = "https://universalis.app/api/v2"
    _UniversalisAPIWrapper_logger = module_logger.getChild(__qualname__)

    def __init__(self, session: aiohttp.ClientSession | None = None):
        self._session = session
        # instance logger
        self._instance_logger = self._UniversalisAPIWrapper_logger.getChild(str(id(self)))

    @property
    def session(self) -> aiohttp.ClientSession:
        """
        Returns this object's aiohttp.ClientSession, or creates a new one if it's closed/doesn't exist yet
        :return:
        """
        if self._session is None or self._session.closed:
            self._instance_logger.debug("Creating new aiohttp ClientSession object")
            self._session = aiohttp.ClientSession()
        return self._session

    async def _process_response(self, response: aiohttp.ClientResponse) -> None:
        """
        Check response for error codes, and if none are found, pass along the response object.
        :param response: aiohttp.ClientResponse response from self.session.get()
        :return: ClientResponse
        :raise: UniversalisError if non-200 status code, or if response could not be processed into JSON
        """
        if response.status == 400:
            self._instance_logger.warning("Error code 400")
            raise UniversalisError(f"400 code received: {response.url} + {response.real_url}")
        elif response.status == 404:
            self._instance_logger.warning("Error code 404")
            raise UniversalisError(f"404 code received: {response.url} + {response.real_url}")
        elif response.status != 200:
            self._instance_logger.warning("Non-200 response code received", extra={'response_code': response.status})
            raise UniversalisError(f"{response.status} code received: {response.url} + {response.real_url}")
        else:
            self._instance_logger.info("200 code received, processing complete")
            return

    async def get_endpoint(self, endpoint: str, params: dict[str, str] = None, json: bool = True) -> dict | list | bytes:
        """
        Retrieve data from the given Universalis API endpoint as JSON unless specified
        :param endpoint: the specific endpoint to request from
        :param params: optional parameters (added as ?key=value)
        :param json: bool representing type of data to retrieve
        :return: aiohttp.ClientResponse
        :raise: UniversalisError if response cannot be read
        """
        #generate full url
        url = self.base_url + endpoint
        if params is None:
            params = {}
        self._instance_logger.debug("Sending endpoint request", extra={'url': url, 'params': params})
        async with self.session.get(url, params=params) as response:
            self._instance_logger.debug("Response created, processing object")
            await self._process_response(response)
            # try to get the data
            try:
                if json:
                    data = await response.json()
                else:
                    data = await response.read()
            except aiohttp.ContentTypeError as e:
                self._instance_logger.warning("JSON data expected, but not received",
                                              extra={'content-type': response.content_type,
                                                     'error': e})
                raise UniversalisError(e)
            except aiohttp.ClientResponseError as e:
                self._instance_logger.warning("Bytestream could not be read",
                                              extra={'content-type': response.content_type,
                                                     'error': e})
                raise UniversalisError(e)
            else:
                return data