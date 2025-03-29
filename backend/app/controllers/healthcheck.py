class HealthCheckController:
    async def __call__(self) -> dict[str, str]:
        return {"status": "OK"}
