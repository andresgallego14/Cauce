from infraestructura.models import Bloque


def preparar_bloques(db):
    db.add(Bloque(nombre="Bloque A", area_m2=600.0))
    db.add(Bloque(nombre="Bloque B", area_m2=400.0))
    db.commit()


def test_convierte_mm_a_m3_descontando_la_perdida(cliente, db):
    preparar_bloques(db)

    respuesta = cliente.get("/lluvia-en-m3", params={"mm": 4})

    assert respuesta.status_code == 200
    # 4 mm - 3 mm de perdida = 1 mm util x 1000 m2 de techo = 1 m3
    assert respuesta.json() == {
        "mm_medidos": 4.0,
        "perdida_mm": 3.0,
        "mm_utiles": 1.0,
        "m3": 1.0,
    }


def test_una_lluvia_menor_a_la_perdida_no_aporta(cliente, db):
    preparar_bloques(db)

    respuesta = cliente.get("/lluvia-en-m3", params={"mm": 2})

    assert respuesta.json()["mm_utiles"] == 0.0
    assert respuesta.json()["m3"] == 0.0


def test_milimetros_negativos_se_rechazan(cliente):
    respuesta = cliente.get("/lluvia-en-m3", params={"mm": -1})

    assert respuesta.status_code == 422
