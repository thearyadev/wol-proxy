from typing import Any, AsyncGenerator, Generator, Optional
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import os
from wakeonlan import send_magic_packet

app = FastAPI()

PROXY_TARGET = os.environ.get("PROXY_URL") or "http://192.168.1.11:11434"
WOL_MAC = os.environ.get("WOL_MAC") or "B4:2E:99:4D:5C:B4"
TIMEOUT = os.environ.get("TIMEOUT") or "10"

if not all((PROXY_TARGET, WOL_MAC, )):
    raise Exception("Environ (one of) [PROXY_URL, WOL_MAC, WOL_ADDR, WOL_INT] is not set.")


async def forwardStream(
    request: Request, content: Optional[bytes] = None
) -> AsyncGenerator[bytes, Any]:
    client = httpx.AsyncClient()
    async with client.stream(
        request.method, PROXY_TARGET + request.url.path, content=content, timeout=30
    ) as response:
        async for chunk in response.aiter_bytes():
            yield chunk


@app.get("/{full_path:path}")
async def get(request: Request) -> StreamingResponse:
    send_magic_packet(WOL_MAC,)
    return StreamingResponse(forwardStream(request), media_type="application/json")


@app.post("/{full_path:path}")
async def post(request: Request) -> StreamingResponse:
    send_magic_packet(WOL_MAC, )
    return StreamingResponse(
        forwardStream(request, await request.body()), media_type="application/json"
    )


@app.delete("/{full_path:path}")
async def delete(request: Request) -> StreamingResponse:
    send_magic_packet(WOL_MAC, )
    return StreamingResponse(forwardStream(request), media_type="application/json")


@app.put("/{full_path:path}")
async def put(request: Request) -> StreamingResponse:
    send_magic_packet(WOL_MAC, )
    return StreamingResponse(
        forwardStream(request, await request.body()), media_type="application/json"
    )
