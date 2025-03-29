import os

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HTTP_HOST", "127.0.0.1"),
        port=int(os.getenv("HTTP_PORT", "8000")),
        reload=True,
    )
