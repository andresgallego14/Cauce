import config
from dominio.enums import Fuente
from infraestructura.models import Registro


def enviar_lectura(cliente, fecha, fuente, lectura):
    return cliente.post(
        "/lectura",
        json={
            "fecha": fecha,
            "fuente": fuente,
            "lectura": lectura,
            "usuario": "Prueba",
        },
    )


def lecturas_guardadas(db, fuente):
    return db.query(Registro).filter(Registro.fuente == fuente).all()


def test_primera_lectura_queda_como_base_con_consumo_cero(cliente, db):
    respuesta = enviar_lectura(cliente, "2026-11-02", "riego", 32218.0)

    assert respuesta.status_code == 200
    assert respuesta.json()["consumo_m3"] == 0.0
    guardado = lecturas_guardadas(db, Fuente.RIEGO)[0]
    assert guardado.valor == 0.0
    assert guardado.lectura_acumulada == 32218.0


def test_segunda_lectura_guarda_la_resta_como_consumo(cliente, db):
    enviar_lectura(cliente, "2026-11-02", "riego", 32218.0)

    respuesta = enviar_lectura(cliente, "2026-11-03", "riego", 32240.5)

    assert respuesta.json()["consumo_m3"] == 22.5
    assert lecturas_guardadas(db, Fuente.RIEGO)[-1].valor == 22.5


def test_lectura_menor_se_rechaza_y_no_se_guarda(cliente, db):
    enviar_lectura(cliente, "2026-11-02", "cruda", 508.0)

    respuesta = enviar_lectura(cliente, "2026-11-03", "cruda", 50.8)

    assert respuesta.status_code == 409
    assert "menor que la anterior" in respuesta.json()["detalle"]
    assert len(lecturas_guardadas(db, Fuente.CRUDA)) == 1


def test_consumo_imposible_se_rechaza(cliente):
    enviar_lectura(cliente, "2026-10-05", "fertirriego", 534.78)

    respuesta = enviar_lectura(cliente, "2026-10-19", "fertirriego", 61794.52)

    assert respuesta.status_code == 409
    assert "supera" in respuesta.json()["detalle"]


def test_fuente_sin_medidor_se_rechaza(cliente):
    respuesta = enviar_lectura(cliente, "2026-11-02", "lluvia", 12.0)

    assert respuesta.status_code == 422
    assert "no tiene medidor" in respuesta.json()["detalle"]


def test_sin_punto_de_partida_no_se_puede_registrar_lectura(cliente, monkeypatch):
    monkeypatch.setattr(config, "FECHA_INICIO_BALANCE", None)

    respuesta = enviar_lectura(cliente, "2026-11-02", "riego", 32218.0)

    assert respuesta.status_code == 409
