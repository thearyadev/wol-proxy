from typing import Any, AsyncGenerator, Optional
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import os
import subprocess

app = FastAPI()

PROXY_TARGET = os.environ.get("PROXY_URL") or ""
WOL_MAC = os.environ.get("WOL_MAC") or ""
WOL_INT = os.environ.get("WOL_INT") or ""
TIMEOUT = int(os.environ.get("TIMEOUT") or "30")


if not all((PROXY_TARGET, WOL_MAC, WOL_INT, TIMEOUT)):
    raise Exception("Environ (one of) [PROXY_URL, WOL_MAC, WOL_INT] is not set.")


def run_etherwake():
    subprocess.run(["etherwake", "-i", WOL_INT, WOL_MAC])


async def forwardStream(
    request: Request, content: Optional[bytes] = None
) -> AsyncGenerator[bytes, Any]:
    client = httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=3))
    async with client.stream(
        request.method,
        PROXY_TARGET + request.url.path,
        content=content,
        timeout=TIMEOUT,
    ) as response:
        async for chunk in response.aiter_bytes():
            yield chunk


@app.get("/{full_path:path}")
async def get(request: Request) -> StreamingResponse:
    run_etherwake()
    return StreamingResponse(forwardStream(request), media_type="application/json")


@app.post("/{full_path:path}")
async def post(request: Request) -> StreamingResponse:
    run_etherwake()
    return StreamingResponse(
        forwardStream(request, await request.body()), media_type="application/json"
    )


@app.delete("/{full_path:path}")
async def delete(request: Request) -> StreamingResponse:
    run_etherwake()
    return StreamingResponse(forwardStream(request), media_type="application/json")


@app.put("/{full_path:path}")
async def put(request: Request) -> StreamingResponse:
    run_etherwake()
    return StreamingResponse(
        forwardStream(request, await request.body()), media_type="application/json"
    )
