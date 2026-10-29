import config


def test_balance_sin_punto_de_partida_responde_409(cliente, monkeypatch):
    monkeypatch.setattr(config, "NIVEL_INICIAL_M3", None)

    respuesta = cliente.get("/balance")

    assert respuesta.status_code == 409
    assert "punto de partida" in respuesta.json()["detalle"]
