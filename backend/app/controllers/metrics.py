from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


class MetricsController:
    async def __call__(self) -> Response:
        resp = Response(content=generate_latest())
        resp.headers["Content-Type"] = CONTENT_TYPE_LATEST
        return resp
