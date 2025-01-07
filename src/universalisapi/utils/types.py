"""Type aliases for this library."""

from .enums import World, DataCenter, Region

type APIRegion = World | DataCenter | Region
type APIResponse = dict | list[dict]
