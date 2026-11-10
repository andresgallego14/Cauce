import hashlib
import secrets
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

import config

NOMBRE_COOKIE = "acceso"
UN_ANIO_EN_SEGUNDOS = 365 * 24 * 60 * 60
PAGINA_SIN_ACCESO = (
    "<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Acceso no autorizado</title></head>"
    "<body style='font-family:sans-serif;padding:40px;text-align:center'>"
    "<h1>Acceso no autorizado</h1>"
    "<p>Abre la aplicación desde el portal de la empresa.</p>"
    "</body></html>"
)


def huella(llave: str) -> str:
    return hashlib.sha256(llave.encode()).hexdigest()


def son_iguales(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode(), b.encode())


async def verificar_acceso(
    peticion: Request, siguiente: Callable[[Request], Awaitable[Response]]
) -> Response:
    llave = config.LLAVE_ACCESO
    if llave is None:
        return await siguiente(peticion)

    if son_iguales(peticion.cookies.get(NOMBRE_COOKIE, ""), huella(llave)):
        return await siguiente(peticion)

    if son_iguales(peticion.query_params.get("acceso", ""), llave):
        respuesta = RedirectResponse(peticion.url.path, status_code=303)
        respuesta.set_cookie(
            NOMBRE_COOKIE,
            huella(llave),
            max_age=UN_ANIO_EN_SEGUNDOS,
            httponly=True,
            samesite="lax",
        )
        return respuesta

    return HTMLResponse(PAGINA_SIN_ACCESO, status_code=403)
