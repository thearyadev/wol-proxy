from typing import Any, AsyncGenerator, Optional
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
import httpx
import os
import subprocess
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger("uvicorn.error")
PROXY_TARGET = os.environ.get("PROXY_URL") or ""
WOL_MAC = os.environ.get("WOL_MAC") or ""
WOL_INT = os.environ.get("WOL_INT") or ""
TIMEOUT = int(os.environ.get("TIMEOUT") or "30")
GET_CACHE = bool(os.environ.get("GET_CACHE") or False)
GET_CACHE_INVALIDATE_SECONDS = int(os.environ.get("GET_CACHE_INVALIDATE") or "1800")


cache: dict[str, tuple[bytes, datetime]] = {}

app = FastAPI()

if not all(
    (PROXY_TARGET, WOL_MAC, WOL_INT, TIMEOUT, GET_CACHE, GET_CACHE_INVALIDATE_SECONDS)
):
    raise Exception(
        "Environ (one of) [PROXY_URL, WOL_MAC, WOL_INT, GET_CACHE, GET_CACHE_INVALIDATE_SECONDS] is not set."
    )


def run_etherwake() -> None:
    subprocess.run(["etherwake", "-i", WOL_INT, WOL_MAC])
    time.sleep(2)
    logger.info(f"[PROXY] Sent magic packet to {WOL_MAC} on {WOL_INT}")


async def forwardStream(
    request: Request, content: Optional[bytes] = None
) -> AsyncGenerator[bytes, Any]:
    """Fowards a request to another webserver. Response is streamed."""
    client = httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=3))
    async with client.stream(
        request.method,
        PROXY_TARGET + request.url.path,
        content=content,
        timeout=TIMEOUT,
    ) as response:
        async for chunk in response.aiter_bytes():
            yield chunk


async def forwardGet(request: Request) -> httpx.Response:
    """Forwards a request to another webserver. Response is not streamed. GET only."""
    client = httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=3))
    response = await client.get(PROXY_TARGET + request.url.path, timeout=TIMEOUT)
    return response


@app.get("/{full_path:path}")
async def get(request: Request) -> Response:
    if GET_CACHE and (cached_response_content := cache.get(request.url.path)):
        if cached_response_content[1] < datetime.now():
            logger.info(f"[PROXY] {request.url.path} was cached, and is now invalid.")
        else:
            logger.info(
                f"[PROXY] {request.url.path} is cached until {cached_response_content[1].strftime("%Y-%m-%dT%H:%M:%S")}"
            )
            return Response(
                content=cached_response_content[0], media_type="application/json"
            )

    logger.info(f"[PROXY] {request.url.path} is not cached (or caching is disabled)")
    run_etherwake()
    response = await forwardGet(request)
    if response.status_code == 200:
        cache[request.url.path] = (
            response.content,
            datetime.now() + timedelta(seconds=GET_CACHE_INVALIDATE_SECONDS),
        )
    return Response(response.content, media_type="application/json")


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
