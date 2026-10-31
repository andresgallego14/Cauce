import config
from config import lista_desde_texto


def test_usuarios_devuelve_la_lista_configurada(cliente, monkeypatch):
    monkeypatch.setattr(config, "USUARIOS", ["Ana Prueba", "Luis Ejemplo"])

    respuesta = cliente.get("/usuarios")

    assert respuesta.status_code == 200
    assert respuesta.json() == ["Ana Prueba", "Luis Ejemplo"]


def test_usuarios_vacia_si_no_hay_configuracion(cliente, monkeypatch):
    monkeypatch.setattr(config, "USUARIOS", [])

    respuesta = cliente.get("/usuarios")

    assert respuesta.json() == []


def test_lista_desde_texto_limpia_espacios_y_comas_sobrantes():
    assert lista_desde_texto(" Ana Prueba , Luis Ejemplo,, ") == [
        "Ana Prueba",
        "Luis Ejemplo",
    ]


def test_lista_desde_texto_sin_texto_da_lista_vacia():
    assert lista_desde_texto(None) == []
