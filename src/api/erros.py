"""
src/api/erros.py
----------------
Formato único de erro (documento 01 §6): `{"erro": "<codigo>", "detalhe": "..."}`.
"""

import logging
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("api")


class ErroApi(Exception):
    def __init__(self, status: int, erro: str, detalhe: Optional[str] = None):
        self.status, self.erro, self.detalhe = status, erro, detalhe


def _corpo(erro: str, detalhe: Optional[str]) -> dict:
    return {"erro": erro, "detalhe": detalhe} if detalhe else {"erro": erro}


def registrar(app: FastAPI) -> None:
    @app.exception_handler(ErroApi)
    async def _erro_api(_: Request, exc: ErroApi):
        return JSONResponse(_corpo(exc.erro, exc.detalhe), status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, exc: RequestValidationError):
        detalhe = "; ".join(f"{'.'.join(str(p) for p in e['loc'][1:])}: {e['msg']}" for e in exc.errors())
        return JSONResponse(_corpo("parametro_invalido", detalhe), status_code=400)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        codigo = {404: "nao_encontrado", 405: "metodo_nao_permitido"}.get(exc.status_code, "erro")
        return JSONResponse(_corpo(codigo, None), status_code=exc.status_code)

    @app.exception_handler(Exception)
    async def _interno(request: Request, exc: Exception):
        # Nunca vaza stack trace: o detalhe fica só no log do servidor.
        logger.exception("Erro interno em %s", request.url.path)
        return JSONResponse({"erro": "erro_interno"}, status_code=500)
