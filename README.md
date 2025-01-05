# universalisapi

A Python wrapper for interacting with [Universalis.app](https://universalis.app)'s public API.

### Installation

`universalisapi` can be installed with `pip` or an equivalent via:

```console
$ pip install universalisapi
```

### Usage

```python
from universalisapi import UniversalisAPIClient

client = UniversalisAPIClient()
```

### Supported Endpoints

All publicly available endpoints are planned to be supported, but this tool is under active development. A list of the
currently fully-supported endpoints is provided below.

- /data-centers
- /worlds
- /aggregated/{worldDcRegion}/{itemIds}
- /extra/stats/least-recently-updated
- /{worldDcRegion}/{itemIds}

You can find the Universalis API docs [here](https://docs.universalis.app).


#### Generic usage

`client.get_endpoint()` is a method that takes an endpoint stub and appends it to the base API url of
`https://universalis.app/api/v2` to form a request. Any unsupported endpoints may still be accessed easily through the
use of this method. All responses should be a `dict` or `list` of their raw JSON format, but further support for these
endpoints is undocumented for this library.

#### A Note on Game entities

`/extra/content/{contentId}` is listed as "largely untested" by the maintainers of Universalis's API. Until it is
further documented, no official support for this endpoint is planned.

### Documentation

Universalis's public API documentation is available [here](https://docs.universalis.app).

Documentation for `universalisapi` package is in development.
