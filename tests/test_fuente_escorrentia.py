from dominio.balance import movimiento_en_m3
from dominio.enums import Fuente, TipoMovimiento


def enviar_lectura(cliente, fecha, lectura):
    return cliente.post(
        "/lectura",
        json={
            "fecha": fecha,
            "fuente": "escorrentia",
            "lectura": lectura,
            "usuario": "Prueba",
        },
    )


def test_escorrentia_es_una_entrada():
    assert Fuente.ESCORRENTIA.tipo == TipoMovimiento.ENTRADA


def test_escorrentia_suma_sus_m3_al_reservorio():
    assert movimiento_en_m3(Fuente.ESCORRENTIA, 12.5, 1000.0) == 12.5


def test_escorrentia_se_registra_por_lectura_de_medidor(cliente):
    primera = enviar_lectura(cliente, "2026-11-23", 1649.0)
    segunda = enviar_lectura(cliente, "2026-11-24", 1661.5)

    assert primera.json()["consumo_m3"] == 0.0
    assert segunda.json()["consumo_m3"] == 12.5


def test_una_lectura_imposible_de_escorrentia_se_rechaza(cliente):
    enviar_lectura(cliente, "2026-11-23", 1649.0)

    # Q3 = 63 m3/h: en 1 dia marca como maximo 63 x 24 = 1512 m3
    respuesta = enviar_lectura(cliente, "2026-11-24", 3649.0)

    assert respuesta.status_code == 409
    assert "supera" in respuesta.json()["detalle"]
