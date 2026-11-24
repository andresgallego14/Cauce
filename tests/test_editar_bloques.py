from datetime import date

import pytest

import config
from dominio.enums import Fuente
from infraestructura.models import Bloque, Registro

CLAVE = "clave-de-prueba"


@pytest.fixture(autouse=True)
def clave_de_administrador(monkeypatch):
    monkeypatch.setattr(config, "CLAVE_ADMIN", CLAVE)


def crear_bloque(db, nombre="PM", area_m2=500.0):
    bloque = Bloque(nombre=nombre, area_m2=area_m2)
    db.add(bloque)
    db.commit()
    return bloque.id


def editar(cliente, id_bloque, nombre="Bloque 3", area_m2=500.0, clave=CLAVE):
    return cliente.post(
        f"/bloques/{id_bloque}/editar",
        json={"nombre": nombre, "area_m2": area_m2, "clave": clave},
    )


def eliminar(cliente, id_bloque, clave=CLAVE):
    return cliente.post(f"/bloques/{id_bloque}/eliminar", json={"clave": clave})


def test_editar_cambia_el_nombre_y_el_area(cliente, db):
    id_bloque = crear_bloque(db)

    respuesta = editar(cliente, id_bloque, nombre="Bloque 3", area_m2=620.5)

    assert respuesta.status_code == 200
    assert cliente.get("/bloques").json() == [
        {"id": id_bloque, "nombre": "Bloque 3", "area_m2": 620.5}
    ]


def test_editar_con_clave_incorrecta_no_cambia_nada(cliente, db):
    id_bloque = crear_bloque(db)

    respuesta = editar(cliente, id_bloque, clave="otra")

    assert respuesta.status_code == 403
    assert cliente.get("/bloques").json()[0]["nombre"] == "PM"


def test_editar_un_bloque_que_no_existe_avisa(cliente):
    respuesta = editar(cliente, 999)

    assert respuesta.status_code == 409
    assert "No existe" in respuesta.json()["detalle"]


def test_el_area_debe_ser_mayor_que_cero(cliente, db):
    id_bloque = crear_bloque(db)

    respuesta = editar(cliente, id_bloque, area_m2=0)

    assert respuesta.status_code == 422


def test_eliminar_quita_el_bloque(cliente, db):
    id_bloque = crear_bloque(db)

    respuesta = eliminar(cliente, id_bloque)

    assert respuesta.status_code == 200
    assert cliente.get("/bloques").json() == []


def test_eliminar_con_clave_incorrecta_no_lo_quita(cliente, db):
    id_bloque = crear_bloque(db)

    respuesta = eliminar(cliente, id_bloque, clave="otra")

    assert respuesta.status_code == 403
    assert len(cliente.get("/bloques").json()) == 1


def test_no_se_puede_eliminar_un_bloque_con_registros(cliente, db):
    id_bloque = crear_bloque(db)
    db.add(
        Registro(
            fecha=date(2026, 11, 20),
            tipo=Fuente.LLUVIA.tipo,
            fuente=Fuente.LLUVIA,
            valor=5.0,
            bloques_id=id_bloque,
            usuario="Prueba",
        )
    )
    db.commit()

    respuesta = eliminar(cliente, id_bloque)

    assert respuesta.status_code == 409
    assert "registros" in respuesta.json()["detalle"]
    assert len(cliente.get("/bloques").json()) == 1
