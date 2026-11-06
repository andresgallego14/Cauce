def test_sin_lecturas_la_anterior_es_nula(cliente):
    respuesta = cliente.get("/lectura-anterior", params={"fuente": "riego"})

    assert respuesta.status_code == 200
    assert respuesta.json() is None


def test_devuelve_la_ultima_lectura_registrada(cliente):
    cliente.post(
        "/lectura",
        json={
            "fecha": "2026-11-03",
            "fuente": "riego",
            "lectura": 32240.5,
            "usuario": "prueba",
        },
    )

    respuesta = cliente.get("/lectura-anterior", params={"fuente": "riego"})

    assert respuesta.json() == {"fecha": "2026-11-03", "lectura": 32240.5}


def test_fuente_sin_medidor_no_tiene_lectura_anterior(cliente):
    respuesta = cliente.get("/lectura-anterior", params={"fuente": "lluvia"})

    assert respuesta.status_code == 422
