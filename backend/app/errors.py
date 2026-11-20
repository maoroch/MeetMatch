from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_payload(code: str, message: str, details: object = None) -> dict[str, object]:
    payload: dict[str, object] = {"error": {"code": code, "message": message, "details": details}}
    payload["detail"] = details if details is not None else message
    return payload


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"loc": error.get("loc", []), "msg": error.get("msg", "Invalid value"), "type": error.get("type", "value_error")} for error in exc.errors()]
        return JSONResponse(status_code=422, content=error_payload("validation_error", "Request validation failed", details))

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "http_error"
        message = str(exc.detail)
        return JSONResponse(status_code=exc.status_code, content=error_payload(code, message))
