# Clickhouse Client
Example of use:

```python
from dependency_injector.wiring import Provide, inject
from core.container import Container
from infra.clickhouse_client import ClickHouseClient


@inject
async def clickhouse_test(client: ClickHouseClient = Provide[Container.clickhouse_client]):
    await client.connect()

    # SELECT
    query = "SELECT * FROM events ORDER BY dt LIMIT 10"
    result = await client.select(query)

    # INSERT
    query = "INSERT INTO events(user_id, event_name) VALUES"
    data = {"user_id": 42546, "event_name": "template_test"}
    await client.insert(query, data)

    await client.disconnect()
```
