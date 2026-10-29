from datetime import date

from ayudas import guardar_movimiento
from dominio.enums import Fuente
from servicios.balance import fecha_ultimo_registro


def test_fecha_ultimo_registro_devuelve_la_mas_reciente(db):
    guardar_movimiento(db, date(2026, 1, 3), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 5), Fuente.FERTIRRIEGO, 20.0)
    guardar_movimiento(db, date(2026, 1, 4), Fuente.RIEGO, 5.0)
    db.commit()

    assert fecha_ultimo_registro(db) == date(2026, 1, 5)


def test_fecha_ultimo_registro_sin_registros_devuelve_none(db):
    assert fecha_ultimo_registro(db) is None
