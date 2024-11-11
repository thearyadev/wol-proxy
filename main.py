from typing import Any, AsyncGenerator, Generator, Optional
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import os

app = FastAPI()

PROXY_TARGET = os.environ.get("PROXY_URL") or ""

if not PROXY_TARGET:
    raise Exception("Environ [PROXY_URL] is not set.")


async def forwardStream(
    request: Request, content: Optional[bytes] = None
) -> AsyncGenerator[bytes, Any]:
    client = httpx.AsyncClient()
    async with client.stream(
        request.method, PROXY_TARGET + request.url.path, content=content
    ) as response:
        async for chunk in response.aiter_bytes():
            yield chunk


@app.get("/{full_path:path}")
async def get(request: Request) -> StreamingResponse:
    return StreamingResponse(forwardStream(request), media_type="application/json")


@app.post("/{full_path:path}")
async def post(request: Request) -> StreamingResponse:
    return StreamingResponse(
        forwardStream(request, await request.body()), media_type="application/json"
    )


@app.delete("/{full_path:path}")
async def delete(request: Request) -> StreamingResponse:
    return StreamingResponse(forwardStream(request), media_type="application/json")


@app.put("/{full_path:path}")
async def put(request: Request) -> StreamingResponse:
    return StreamingResponse(
        forwardStream(request, await request.body()), media_type="application/json"
    )
