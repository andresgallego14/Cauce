from datetime import date, datetime, timedelta

from dominio.enums import Fuente
from infraestructura.models import Anulacion, Bloque, Registro


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


def agregar_lluvia(db, dias_atras, mm):
    registro = Registro(
        fecha=date.today() - timedelta(days=dias_atras),
        tipo=Fuente.LLUVIA.tipo,
        fuente=Fuente.LLUVIA,
        valor=mm,
        usuario="Ana",
    )
    db.add(registro)
    db.commit()
    return registro


def hace(dias):
    return (date.today() - timedelta(days=dias)).isoformat()


def test_dias_sin_lluvia_cuenta_desde_la_ultima_de_mas_de_3_mm(cliente, db):
    agregar_lluvia(db, 6, 12.0)
    agregar_lluvia(db, 3, 0.0)
    agregar_lluvia(db, 2, 1.5)
    agregar_lluvia(db, 1, 2.0)

    respuesta = cliente.get("/dias-sin-lluvia")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "dias": 6,
        "ultima_lluvia": hace(6),
        "mm_ultima_lluvia": 12.0,
        "recientes": [
            {"fecha": hace(1), "mm": 2.0},
            {"fecha": hace(2), "mm": 1.5},
            {"fecha": hace(3), "mm": 0.0},
        ],
    }


def test_una_lluvia_anulada_no_cuenta(cliente, db):
    agregar_lluvia(db, 8, 10.0)
    anulada = agregar_lluvia(db, 2, 25.0)
    db.add(
        Anulacion(
            registro_id=anulada.id,
            motivo="Dato de prueba",
            usuario="Ana",
            momento=datetime.now(),
        )
    )
    db.commit()

    assert cliente.get("/dias-sin-lluvia").json()["dias"] == 8


def test_sin_lluvias_registradas_no_hay_dato(cliente):
    respuesta = cliente.get("/dias-sin-lluvia")

    assert respuesta.json() == {
        "dias": None,
        "ultima_lluvia": None,
        "mm_ultima_lluvia": None,
        "recientes": [],
    }
