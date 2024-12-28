import pytest

from aioresponses import aioresponses


@pytest.fixture
def mocked_response():
    with aioresponses() as m:
        yield m