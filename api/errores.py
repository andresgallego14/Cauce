import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from infraestructura.clima import ClimaNoDisponible
from servicios.balance import BalanceSinPuntoDeInicio

MENSAJE_CLIMA_NO_DISPONIBLE = "El servicio de clima no está disponible por ahora"
MENSAJE_BALANCE_SIN_PUNTO_DE_PARTIDA = (
    "Falta el punto de partida del balance: "
    "el administrador debe configurar la fecha y el nivel inicial"
)

logger = logging.getLogger(__name__)


def clima_no_disponible(peticion: Request, error: ClimaNoDisponible) -> JSONResponse:
    logger.error("Clima no disponible: %s", error)
    return JSONResponse(
        status_code=503,
        content={"detalle": MENSAJE_CLIMA_NO_DISPONIBLE},
    )


def balance_sin_punto_de_partida(
    peticion: Request, error: BalanceSinPuntoDeInicio
) -> JSONResponse:
    logger.warning("Balance sin punto de partida: %s", error)
    return JSONResponse(
        status_code=409,
        content={"detalle": MENSAJE_BALANCE_SIN_PUNTO_DE_PARTIDA},
    )


def registrar_manejadores_de_errores(app: FastAPI) -> None:
    app.add_exception_handler(ClimaNoDisponible, clima_no_disponible)
    app.add_exception_handler(BalanceSinPuntoDeInicio, balance_sin_punto_de_partida)
