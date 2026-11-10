def iniciar(cliente, bocatoma, inicio):
    return cliente.post(
        "/bombeo/inicio",
        json={"bocatoma": bocatoma, "inicio": inicio, "usuario": "Ana"},
    )


def terminar(cliente, bocatoma, fin):
    return cliente.post(
        "/bombeo/fin",
        json={"bocatoma": bocatoma, "fin": fin, "usuario": "Luis"},
    )


def test_iniciar_deja_el_bombeo_visible_para_todos(cliente):
    respuesta = iniciar(cliente, "Bocatoma 2", "2026-01-15T07:00")

    assert respuesta.status_code == 200
    assert cliente.get("/bombeos-en-curso").json() == [
        {"bocatoma": "Bocatoma 2", "inicio": "2026-01-15T07:00:00", "usuario": "Ana"}
    ]


def test_terminar_devuelve_los_m3_y_ya_no_aparece_prendida(cliente):
    iniciar(cliente, "Bocatoma 2", "2026-01-15T07:00")

    respuesta = terminar(cliente, "Bocatoma 2", "2026-01-15T09:30")

    assert respuesta.status_code == 200
    assert respuesta.json()["m3"] == 22.5
    assert cliente.get("/bombeos-en-curso").json() == []


def test_prender_dos_veces_responde_409_con_el_motivo(cliente):
    iniciar(cliente, "Bocatoma Sumergible", "2026-01-15T07:00")

    respuesta = iniciar(cliente, "Bocatoma Sumergible", "2026-01-15T08:00")

    assert respuesta.status_code == 409
    assert "ya está prendida" in respuesta.json()["detalle"]


def test_hora_futura_responde_409(cliente):
    respuesta = iniciar(cliente, "Bocatoma 2", "2099-01-01T07:00")

    assert respuesta.status_code == 409
    assert "futuro" in respuesta.json()["detalle"]


def test_hora_con_zona_horaria_se_rechaza(cliente):
    respuesta = iniciar(cliente, "Bocatoma 2", "2026-01-15T07:00:00Z")

    assert respuesta.status_code == 422
