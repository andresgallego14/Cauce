import logging

from api.dependencias import pronostico_actual
from infraestructura.clima import ClimaNoDisponible

DETALLE_INTERNO = "detalle interno que no debe verse"


def clima_caido():
    raise ClimaNoDisponible(DETALLE_INTERNO)


def test_si_el_clima_cae_el_detalle_queda_en_el_log_y_no_en_la_respuesta(
    cliente, caplog
):
    cliente.app.dependency_overrides[pronostico_actual] = clima_caido

    with caplog.at_level(logging.ERROR):
        respuesta = cliente.get("/pronostico")

    assert respuesta.status_code == 503
    assert DETALLE_INTERNO not in respuesta.text
    assert DETALLE_INTERNO in caplog.text
