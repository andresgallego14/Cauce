from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import config
from api.errores import registrar_manejadores_de_errores
from api.routers import balance, bloques, clima, registros

RUTA_FRONTEND = Path(__file__).parent / "frontend"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGENES_PERMITIDOS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content_type"],
)

registrar_manejadores_de_errores(app)
app.include_router(balance.router)
app.include_router(bloques.router)
app.include_router(registros.router)
app.include_router(clima.router)
app.mount("/", StaticFiles(directory=RUTA_FRONTEND, html=True), name="frontend")
