from datetime import date
import pytest
from ayudas import guardar_movimiento 
from dominio.enums import Fuente
from infraestructura.models import Reservorio
from infraestructura.repositorio import (
    obtener_registros,
    obtener_reservorio,
    obtener_salidas,
)

def test_obtener_registros_sin_datos_devuelve_lista_vacia(db):
    assert obtener_registros(db) == []

def test_obtener_registros_devuelve_todos_los_registros(db):
    guardar_movimiento(db, date(2026, 1, 1), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 1), Fuente.LLUVIA, 5.0)
    guardar_movimiento(db, date(2026, 1, 2), Fuente.AGUA_POTABLE_60, 7.0)
    db.commit()
    assert len(obtener_registros(db)) == 3

def test_obtener_salidas_solo_incluye_riego_y_cruda(db):
    guardar_movimiento(db, date(2026, 1, 1), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 1), Fuente.CRUDA, 3.0)
    guardar_movimiento(db, date(2026, 1, 1), Fuente.FERTIRRIEGO, 20.0)
    guardar_movimiento(db, date(2026, 1, 1), Fuente.LLUVIA, 5.0)
    guardar_movimiento(db, date(2026, 1, 1), Fuente.AGUA_POTABLE_60, 7.0)
    db.commit()
    salidas = obtener_salidas(db)
    assert sorted(salidas) == [(date(2026, 1, 1), 3.0), (date(2026, 1, 1), 10.0)]

def test_obtener_reservorio_devuelve_el_reservorio_de_la_finca(db):
    db.add(Reservorio(capacidad_m3=215.0))
    db.commit()
    assert obtener_reservorio(db).capacidad_m3 == 215.0

def test_obtener_reservorio_sin_reservorio_falla_con_mensaje_claro(db):
    with pytest.raises(ValueError, match="reservorio"):
        obtener_reservorio(db)