from typing import Any, Dict, List, Sequence

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.core.config import settings


# --- Translation helpers (EN -> ES) ---
_VALIDATION_CODE_TO_ES: Dict[str, str] = {
    # Pydantic v2 common codes
    "value_error.missing": "Campo requerido",
    "missing": "Campo requerido",
    "type_error.email": "El correo no es válido",
    "value_error.email": "El correo no es válido",
    "string_too_short": "La cadena es demasiado corta",
    "string_too_long": "La cadena es demasiado larga",
    "value_error.any_str.min_length": "La cadena es demasiado corta",
    "value_error.any_str.max_length": "La cadena es demasiado larga",
    "value_error.number.not_gt": "El valor debe ser mayor",
    "value_error.number.not_ge": "El valor debe ser mayor o igual",
    "value_error.number.not_lt": "El valor debe ser menor",
    "value_error.number.not_le": "El valor debe ser menor o igual",
    "value_error.bool": "Debe ser verdadero o falso",
    "value_error.integer": "Debe ser un número entero",
    "type_error.integer": "Debe ser un número entero",
    "type_error.boolean": "Debe ser verdadero o falso",
}

_HTTP_MSG_EN_TO_ES: Dict[str, str] = {
    # Generic
    "Not Found": "No encontrado",
    "Unauthorized": "No autorizado",
    "Forbidden": "Prohibido",
    "Bad Request": "Solicitud inválida",
    "Conflict": "Conflicto",
    "Internal server error": "Error interno del servidor",
    # Auth
    "Email already registered": "El correo ya está registrado",
    "Invalid credentials": "Credenciales inválidas",
    "Invalid token": "Token inválido",
    "User not found": "Usuario no encontrado",
    "Admin access required": "Se requiere acceso de administrador",
    # Discord
    "Authorization code is required": "Se requiere el código de autorización",
    "Discord authentication failed": "Falló la autenticación con Discord",
    "Authentication process failed": "Falló el proceso de autenticación",
    # Domain specifics
    "Post not found": "Publicación no encontrada",
    "Failed to delete post": "No se pudo eliminar la publicación",
    "Not authorized to update this post": "No estás autorizado para actualizar esta publicación",
    "Not authorized to delete this post": "No estás autorizado para eliminar esta publicación",
    "Tag not found": "Etiqueta no encontrada",
    "Category not found": "Categoría no encontrada",
    "Like not found": "Like no encontrado",
    "Comment not found": "Comentario no encontrado",
}


def _translate_http_msg(msg: str) -> str:
    return _HTTP_MSG_EN_TO_ES.get(msg, msg)


def _translate_validation(code: str | None, default_msg: str) -> str:
    if code and code in _VALIDATION_CODE_TO_ES:
        return _VALIDATION_CODE_TO_ES[code]
    return default_msg


def _json_detail(detail: Any) -> str:
    """Extract a human message from various `detail` shapes and translate to ES."""
    base: str
    if isinstance(detail, str):
        base = detail
    elif isinstance(detail, dict):
        base = detail.get("msg") or detail.get("detail") or str(detail)
    elif isinstance(detail, list):
        base = "; ".join(str(item) for item in detail)
    else:
        base = str(detail)
    return _translate_http_msg(base)


def _format_loc(loc: Sequence[Any]) -> str:
    """Convert tuple/list location to dotted path: ('body','item','name',0) -> 'body.item.name.0'."""
    return ".".join(str(p) for p in loc) if loc else ""


def _format_validation_errors(exc: RequestValidationError) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for err in exc.errors():
        code = err.get("type")
        original_msg = err.get("msg", "Invalid input")
        translated_msg = _translate_validation(code, original_msg)
        item: Dict[str, Any] = {
            "field": _format_loc(err.get("loc", [])),
            "msg": translated_msg,
            "code": code,
        }
        if settings.DEBUG:
            item["value"] = err.get("input", None)
            item["ctx"] = err.get("ctx")
        out.append(item)
    return out


def setup_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for a unified error envelope.

    Successful responses stay as defined by response_model. Errors are wrapped as:
    { "ok": false, "msg": string, "errors": [...]? }
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = _format_validation_errors(exc)
        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "msg": "Error de validación",
                "errors": errors,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        headers = getattr(exc, "headers", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "ok": False,
                "msg": _json_detail(exc.detail)
                if exc.detail is not None
                else "Error HTTP",
            },
            headers=headers,
        )

    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        msg = "Error de integridad"
        try:
            raw = str(getattr(exc, "orig", exc))
            low = raw.lower()
            # PostgreSQL common phrases
            if (
                "duplicate key value violates unique constraint" in low
                or "unique violation" in low
            ):
                msg = "Valor duplicado: viola una restricción única"
            elif (
                "violates foreign key constraint" in low
                or "foreign key violation" in low
            ):
                msg = "Restricción de clave foránea violada"
            elif "null value in column" in low or "not null violation" in low:
                msg = "NULL viola una restricción NOT NULL"
            elif "check constraint" in low:
                msg = "Restricción CHECK violada"
            else:
                msg = raw
        except Exception:
            pass
        return JSONResponse(status_code=409, content={"ok": False, "msg": msg})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Avoid leaking internals; keep concise message.
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "msg": "Error interno del servidor",
            },
        )
