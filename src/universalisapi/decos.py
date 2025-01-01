import logging
from functools import wraps
from time import time

__log__ = logging.getLogger(__name__)

def timed(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        result = await func(*args, **kwargs)
        __log__.info("{} executed in {}s".format(func.__name__, round(time() - start, 2)))
        return result
    return wrapper