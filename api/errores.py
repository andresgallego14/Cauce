from fastapi import FastAPI
from fastapi.responses import JSONResponse

from infraestructura.clima import ClimaNoDisponible

MENSAJE_CLIMA_NO_DISPONIBLE = "El servicio de clima no está disponible por ahora"


def clima_no_disponible(peticion, error):
    return JSONResponse(
        status_code=503,
        content={"detalle": MENSAJE_CLIMA_NO_DISPONIBLE},
    )


def registrar_manejadores_de_errores(app: FastAPI) -> None:
    app.add_exception_handler(ClimaNoDisponible, clima_no_disponible)