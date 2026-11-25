import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.acceso import ClaveIncorrecta
from dominio.bombeo import BombeoIncongruente
from dominio.lecturas import FuenteSinMedidor, LecturaIncongruente
from dominio.planes import PlanInvalido
from infraestructura.clima import ClimaNoDisponible
from servicios.anulaciones import AnulacionInvalida
from servicios.balance import BalanceSinPuntoDeInicio
from servicios.bloques import BloqueInvalido

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


def lectura_incongruente(peticion: Request, error: LecturaIncongruente) -> JSONResponse:
    logger.warning("Lectura rechazada: %s", error)
    return JSONResponse(status_code=409, content={"detalle": str(error)})


def fuente_sin_medidor(peticion: Request, error: FuenteSinMedidor) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detalle": str(error)})


def bombeo_incongruente(peticion: Request, error: BombeoIncongruente) -> JSONResponse:
    logger.warning("Bombeo rechazado: %s", error)
    return JSONResponse(status_code=409, content={"detalle": str(error)})


def clave_incorrecta(peticion: Request, error: ClaveIncorrecta) -> JSONResponse:
    logger.warning("Intento de anulacion con clave incorrecta")
    return JSONResponse(status_code=403, content={"detalle": str(error)})


def anulacion_invalida(peticion: Request, error: AnulacionInvalida) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detalle": str(error)})


def bloque_invalido(peticion: Request, error: BloqueInvalido) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detalle": str(error)})


def plan_invalido(peticion: Request, error: PlanInvalido) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detalle": str(error)})


def registrar_manejadores_de_errores(app: FastAPI) -> None:
    app.add_exception_handler(ClimaNoDisponible, clima_no_disponible)
    app.add_exception_handler(BalanceSinPuntoDeInicio, balance_sin_punto_de_partida)
    app.add_exception_handler(LecturaIncongruente, lectura_incongruente)
    app.add_exception_handler(FuenteSinMedidor, fuente_sin_medidor)
    app.add_exception_handler(BombeoIncongruente, bombeo_incongruente)
    app.add_exception_handler(ClaveIncorrecta, clave_incorrecta)
    app.add_exception_handler(AnulacionInvalida, anulacion_invalida)
    app.add_exception_handler(BloqueInvalido, bloque_invalido)
    app.add_exception_handler(PlanInvalido, plan_invalido)
