import config

LLAVE = "llave-de-prueba"


def test_sin_llave_configurada_se_entra_libre(cliente, monkeypatch):
    monkeypatch.setattr(config, "LLAVE_ACCESO", None)

    assert cliente.get("/bloques").status_code == 200


def test_sin_acceso_se_bloquea_la_pagina(cliente, monkeypatch):
    monkeypatch.setattr(config, "LLAVE_ACCESO", LLAVE)

    respuesta = cliente.get("/")

    assert respuesta.status_code == 403
    assert "portal de la empresa" in respuesta.text


def test_sin_acceso_se_bloquea_la_api(cliente, monkeypatch):
    monkeypatch.setattr(config, "LLAVE_ACCESO", LLAVE)

    assert cliente.get("/bloques").status_code == 403


def test_llave_incorrecta_no_deja_entrar(cliente, monkeypatch):
    monkeypatch.setattr(config, "LLAVE_ACCESO", LLAVE)

    assert cliente.get("/?acceso=otra-llave").status_code == 403


def test_llave_correcta_deja_entrar_y_recuerda_el_celular(cliente, monkeypatch):
    monkeypatch.setattr(config, "LLAVE_ACCESO", LLAVE)

    respuesta = cliente.get(f"/?acceso={LLAVE}", follow_redirects=False)

    assert respuesta.status_code == 303
    assert respuesta.headers["location"] == "/"
    assert "httponly" in respuesta.headers["set-cookie"].lower()
    assert cliente.get("/bloques").status_code == 200
