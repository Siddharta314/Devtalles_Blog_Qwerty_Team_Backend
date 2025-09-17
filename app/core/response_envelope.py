import json
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


_EXCLUDE_PATH_PREFIXES = ("/docs", "/redoc", "/openapi.json")


def _default_success_message(method: str) -> str:
    m = method.upper()
    if m == "POST":
        return "Operación con éxito"
    if m in ("PUT", "PATCH"):
        return "Actualizado con éxito"
    if m == "DELETE":
        return "Eliminado con éxito"
    return "Operación exitosa"


def _filtered_headers(response) -> dict[str, str]:
    # Remove Content-Length so Starlette recalculates it
    return {k: v for k, v in response.headers.items() if k.lower() != "content-length"}


class SuccessEnvelopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip docs/openapi
        if request.url.path.startswith(_EXCLUDE_PATH_PREFIXES):
            return await call_next(request)

        response = await call_next(request)

        # Only wrap successful JSON responses (or empty 204)
        content_type = response.headers.get("content-type", "")
        if not (
            response.status_code < 400
            and (
                content_type.startswith("application/json")
                or response.status_code == 204
            )
        ):
            return response

        filtered_headers = _filtered_headers(response)
        msg = _default_success_message(request.method)

        # Preserve 204 No Content with envelope and same status
        if response.status_code == 204:
            return JSONResponse(
                status_code=204,
                content={"ok": True, "msg": msg, "data": None},
                headers=filtered_headers,
            )

        # Read response body
        body_bytes = b""
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            body_bytes += chunk

        if not body_bytes:
            # No body to wrap
            return JSONResponse(
                status_code=response.status_code,
                content={"ok": True, "msg": msg, "data": None},
                headers=filtered_headers,
            )

        try:
            payload: Any = json.loads(body_bytes)
        except Exception:
            # Not JSON parseable; return original bytes without clobbering length
            return Response(
                status_code=response.status_code,
                content=body_bytes,
                headers=filtered_headers,
                media_type=content_type,
            )

        # Avoid double wrapping if already has envelope
        if isinstance(payload, dict) and ("ok" in payload or "data" in payload):
            return JSONResponse(
                status_code=response.status_code,
                content=payload,
                headers=filtered_headers,
            )

        # Wrap any JSON (object/array/primitive)
        wrapped = {"ok": True, "msg": msg, "data": payload}
        return JSONResponse(
            status_code=response.status_code,
            content=wrapped,
            headers=filtered_headers,
        )
