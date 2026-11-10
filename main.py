from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import config
from api.acceso import verificar_acceso
from api.errores import registrar_manejadores_de_errores
from api.routers import balance, bloques, clima, registros

RUTA_FRONTEND = Path(__file__).parent / "frontend"

app = FastAPI(
    docs_url="/docs" if config.MOSTRAR_DOCUMENTACION else None,
    redoc_url=None,
    openapi_url="/openapi.json" if config.MOSTRAR_DOCUMENTACION else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGENES_PERMITIDOS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-type"],
)

registrar_manejadores_de_errores(app)
app.include_router(balance.router)
app.include_router(bloques.router)
app.include_router(registros.router)
app.include_router(clima.router)
app.mount("/", StaticFiles(directory=RUTA_FRONTEND, html=True), name="frontend")


@app.middleware("http")
async def revisar_version_nueva(
    peticion: Request, siguiente: Callable[[Request], Awaitable[Response]]
) -> Response:
    respuesta = await siguiente(peticion)
    respuesta.headers["Cache-Control"] = "no-cache"
    return respuesta


app.middleware("http")(verificar_acceso)
