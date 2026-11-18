import pytest

import config
from infraestructura.models import Anulacion

CLAVE = "clave-de-prueba"


@pytest.fixture(autouse=True)
def clave_de_administrador(monkeypatch):
    monkeypatch.setattr(config, "CLAVE_ADMIN", CLAVE)


def crear_lluvia(cliente):
    cliente.post(
        "/registro",
        json={
            "fecha": "2026-11-17",
            "fuente": "lluvia",
            "valor": 0.0,
            "usuario": "Prueba",
        },
    )
    return cliente.get("/registros").json()[0]["id"]


def anular(cliente, id_registro, clave=CLAVE, motivo="Dato de prueba"):
    return cliente.post(
        f"/registros/{id_registro}/anular",
        json={"motivo": motivo, "usuario": "Andrés", "clave": clave},
    )


def test_el_historial_trae_el_numero_de_cada_registro(cliente):
    id_registro = crear_lluvia(cliente)

    assert isinstance(id_registro, int)


def test_anular_con_la_clave_correcta_lo_saca_del_historial(cliente, db):
    id_registro = crear_lluvia(cliente)

    respuesta = anular(cliente, id_registro)

    assert respuesta.status_code == 200
    assert cliente.get("/registros").json() == []
    assert db.query(Anulacion).one().usuario == "Andrés"


def test_clave_incorrecta_responde_403_y_no_anula(cliente, db):
    id_registro = crear_lluvia(cliente)

    respuesta = anular(cliente, id_registro, clave="otra")

    assert respuesta.status_code == 403
    assert "clave" in respuesta.json()["detalle"].lower()
    assert db.query(Anulacion).count() == 0


def test_sin_clave_configurada_nadie_puede_anular(cliente, monkeypatch):
    monkeypatch.setattr(config, "CLAVE_ADMIN", None)
    id_registro = crear_lluvia(cliente)

    respuesta = anular(cliente, id_registro, clave="cualquiera")

    assert respuesta.status_code == 403


def test_motivo_vacio_responde_409_con_el_motivo(cliente):
    id_registro = crear_lluvia(cliente)

    respuesta = anular(cliente, id_registro, motivo="   ")

    assert respuesta.status_code == 409
    assert "motivo" in respuesta.json()["detalle"]
