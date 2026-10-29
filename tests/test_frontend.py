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