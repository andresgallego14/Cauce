from datetime import date

from dominio.enums import Fuente
from dominio.lecturas import Lectura
from infraestructura.models import Registro
from infraestructura.repositorio import obtener_ultima_lectura

DESDE = date(2026, 11, 2)


def guardar_lectura(db, fecha, fuente, lectura):
    db.add(
        Registro(
            fecha=fecha,
            fuente=fuente,
            tipo=fuente.tipo,
            valor=0.0,
            lectura_acumulada=lectura,
            usuario="Prueba",
        )
    )
    db.commit()


def test_sin_lecturas_no_hay_anterior(db):
    assert obtener_ultima_lectura(db, Fuente.RIEGO, DESDE) is None


def test_devuelve_la_lectura_mas_reciente_de_la_fuente(db):
    guardar_lectura(db, date(2026, 11, 2), Fuente.RIEGO, 32218.0)
    guardar_lectura(db, date(2026, 11, 3), Fuente.RIEGO, 32240.5)

    assert obtener_ultima_lectura(db, Fuente.RIEGO, DESDE) == Lectura(
        date(2026, 11, 3), 32240.5
    )


def test_ignora_las_lecturas_de_otras_fuentes(db):
    guardar_lectura(db, date(2026, 11, 3), Fuente.CRUDA, 508.0)

    assert obtener_ultima_lectura(db, Fuente.RIEGO, DESDE) is None


def test_ignora_las_lecturas_anteriores_al_punto_de_partida(db):
    guardar_lectura(db, date(2026, 10, 19), Fuente.FERTIRRIEGO, 61794.52)

    assert obtener_ultima_lectura(db, Fuente.FERTIRRIEGO, DESDE) is None


def test_ignora_los_registros_sin_lectura(db):
    guardar_lectura(db, date(2026, 11, 3), Fuente.RIEGO, None)

    assert obtener_ultima_lectura(db, Fuente.RIEGO, DESDE) is None
