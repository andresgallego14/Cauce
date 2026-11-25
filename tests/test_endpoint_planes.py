import pytest

import config
from api.dependencias import pronostico_actual
from infraestructura.models import Reservorio

CLAVE = "clave-de-prueba"


@pytest.fixture(autouse=True)
def clave_de_administrador(monkeypatch):
    monkeypatch.setattr(config, "CLAVE_ADMIN", CLAVE)


@pytest.fixture
def cliente_con_reservorio(cliente, db):
    db.add(Reservorio(capacidad_m3=215.0))
    db.commit()
    cliente.app.dependency_overrides[pronostico_actual] = lambda: []
    return cliente


def plan_fin_de_semana(**cambios):
    datos = {
        "nombre": "Fin de semana",
        "meta": "Llenar antes del sábado",
        "modo": "horas",
        "horas": {"Bocatoma pequeña": 7, "Bocatoma grande": 2},
        "dias": None,
        "permite_sumergible": False,
        "usuario": "Brayan",
    }
    datos.update(cambios)
    return datos


def test_lista_los_planes_con_la_recomendacion_de_hoy(cliente_con_reservorio):
    respuesta = cliente_con_reservorio.get("/planes")

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["recomendado"] == "Salir de crítico"
    assert datos["nivel_m3"] == 0.0
    assert datos["capacidad_m3"] == 215.0

    salir = datos["planes"][0]
    assert salir["nombre"] == "Salir de crítico"
    assert salir["recomendado"] is True
    # faltan 107.5; pequena y grande 8 h = 104.16; 3.34 / 21.6 = 9.3 min -> 10
    assert salir["minutos"] == {
        "Bocatoma pequeña": 480,
        "Bocatoma grande": 480,
        "Bocatoma Sumergible": 10,
    }
    assert salir["horario"]["Bocatoma Sumergible"] == [["6:00", "6:10"]]


def test_crea_un_plan_y_aparece_al_final_de_la_lista(cliente_con_reservorio):
    respuesta = cliente_con_reservorio.post("/planes", json=plan_fin_de_semana())

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Fin de semana"
    planes = cliente_con_reservorio.get("/planes").json()["planes"]
    assert planes[-1]["nombre"] == "Fin de semana"
    assert planes[-1]["origen"] == "propio"
    assert planes[-1]["usuario"] == "Brayan"


def test_un_plan_mal_escrito_responde_409_con_el_motivo(cliente_con_reservorio):
    respuesta = cliente_con_reservorio.post(
        "/planes", json=plan_fin_de_semana(nombre="Mantener")
    )

    assert respuesta.status_code == 409
    assert "Ya existe" in respuesta.json()["detalle"]


def test_una_bocatoma_que_no_existe_se_rechaza(cliente_con_reservorio):
    respuesta = cliente_con_reservorio.post(
        "/planes", json=plan_fin_de_semana(horas={"Bocatoma 7": 3})
    )

    assert respuesta.status_code == 422


def crear(cliente, **cambios):
    return cliente.post("/planes", json=plan_fin_de_semana(**cambios)).json()["id"]


def nombres(cliente):
    return [p["nombre"] for p in cliente.get("/planes").json()["planes"]]


def test_eliminar_con_la_clave_borra_el_plan(cliente_con_reservorio):
    id_plan = crear(cliente_con_reservorio)

    respuesta = cliente_con_reservorio.post(
        f"/planes/{id_plan}/eliminar", json={"clave": CLAVE}
    )

    assert respuesta.status_code == 200
    assert "Fin de semana" not in nombres(cliente_con_reservorio)


def test_eliminar_con_clave_incorrecta_no_borra_nada(cliente_con_reservorio):
    id_plan = crear(cliente_con_reservorio)

    respuesta = cliente_con_reservorio.post(
        f"/planes/{id_plan}/eliminar", json={"clave": "otra"}
    )

    assert respuesta.status_code == 403
    assert "Fin de semana" in nombres(cliente_con_reservorio)


def test_eliminar_un_plan_que_no_existe_avisa(cliente_con_reservorio):
    respuesta = cliente_con_reservorio.post(
        "/planes/99/eliminar", json={"clave": CLAVE}
    )

    assert respuesta.status_code == 409
    assert "No existe" in respuesta.json()["detalle"]


def test_editar_con_la_clave_cambia_el_plan(cliente_con_reservorio):
    id_plan = crear(cliente_con_reservorio)
    cambios = plan_fin_de_semana(
        nombre="Fin de semana largo", modo="dias", horas={}, dias=3, usuario="Ana"
    )

    respuesta = cliente_con_reservorio.post(
        f"/planes/{id_plan}/editar", json={**cambios, "clave": CLAVE}
    )

    assert respuesta.status_code == 200
    plan = cliente_con_reservorio.get("/planes").json()["planes"][-1]
    assert plan["nombre"] == "Fin de semana largo"
    assert plan["modo"] == "dias"
    assert plan["dias"] == 3
    assert plan["usuario"] == "Brayan"


def test_editar_puede_dejar_el_mismo_nombre(cliente_con_reservorio):
    id_plan = crear(cliente_con_reservorio)
    cambios = plan_fin_de_semana(meta="Llenar antes del domingo")

    respuesta = cliente_con_reservorio.post(
        f"/planes/{id_plan}/editar", json={**cambios, "clave": CLAVE}
    )

    assert respuesta.status_code == 200


def test_editar_no_deja_copiar_el_nombre_de_otro_plan(cliente_con_reservorio):
    crear(cliente_con_reservorio, nombre="Otro plan")
    id_plan = crear(cliente_con_reservorio)
    cambios = plan_fin_de_semana(nombre="Otro plan")

    respuesta = cliente_con_reservorio.post(
        f"/planes/{id_plan}/editar", json={**cambios, "clave": CLAVE}
    )

    assert respuesta.status_code == 409


def test_editar_con_clave_incorrecta_no_cambia_nada(cliente_con_reservorio):
    id_plan = crear(cliente_con_reservorio)
    cambios = plan_fin_de_semana(nombre="Cambiado")

    respuesta = cliente_con_reservorio.post(
        f"/planes/{id_plan}/editar", json={**cambios, "clave": "otra"}
    )

    assert respuesta.status_code == 403
    assert "Fin de semana" in nombres(cliente_con_reservorio)
