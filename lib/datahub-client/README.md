# Datahub client for Find MOJ Data

This library is part of the Ministry of Justice "Find MOJ Data" service.

It pushes metadata to (and retrieves metadata from) a Datahub catalogue.

## How to install

To install the package using `pip`, run:

```shell
pip install ministryofjustice-data-platform-catalogue
```

## Getting started

```python
from data_platform_catalogue import (
  DataHubCatalogueClient,
  Table
)

client = DataHubCatalogueClient(jwt_token='datahub-personal-token', api_url='https://your-datahub-instance')

# Search
client.search()

# Ingest a table
client.upsert_table(Table(name="Some table", description="A special table I want to share")
```
