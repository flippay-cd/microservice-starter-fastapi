import os

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HTTP_HOST", "0.0.0.0"),
        port=int(os.getenv("HTTP_PORT", "8000")),
        limit_max_requests=1000,
    )
