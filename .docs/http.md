# HTTP Client
Asynchronous http client has been added to the template to interact with external api
Example of use:

```python
from dependency_injector.wiring import Provide, inject
from core.container import Container
from infra.http_client import AsyncHttpClient
from schemas.article import ArticleDTO

@inject
async def get_articles_from_experience(
experience_client: AsyncHttpClient = Provide[Container.experience_client]
) -> list[ArticleDTO]:
articles = await experience_client.get("/api/web/v1/articles/", params={"page": 1})
articles = articles.json()["results"]
return articles
```
