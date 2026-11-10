def test_la_raiz_sirve_la_pagina_de_inicio(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]
    assert "Cauce" in respuesta.text


def test_los_archivos_del_frontend_se_sirven(cliente):
    respuesta = cliente.get("/style.css")

    assert respuesta.status_code == 200
    assert "text/css" in respuesta.headers["content-type"]


def test_servir_el_frontend_no_tapa_las_rutas_de_la_api(cliente):
    respuesta = cliente.get("/bloques")

    assert respuesta.status_code == 200
    assert "application/json" in respuesta.headers["content-type"]


def test_el_navegador_debe_revisar_si_hay_version_nueva(cliente):
    respuesta = cliente.get("/js/api.js")

    assert respuesta.headers["cache-control"] == "no-cache"


def test_la_documentacion_de_la_api_no_se_publica(cliente):
    assert cliente.get("/docs").status_code == 404
    assert cliente.get("/openapi.json").status_code == 404
