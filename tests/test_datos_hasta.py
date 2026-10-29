from datetime import date

from ayudas import guardar_movimiento
from dominio.enums import Fuente
from infraestructura.models import Reservorio


def test_balance_informa_hasta_que_fecha_hay_datos(db, cliente):
    db.add(Reservorio(capacidad_m3=100.0))
    guardar_movimiento(db, date(2026, 1, 5), Fuente.FERTIRRIEGO, 20.0)
    db.commit()

    respuesta = cliente.get("/balance")

    assert respuesta.json()["datos_hasta"] == "2026-01-05"


def test_balance_sin_registros_informa_datos_hasta_nulo(db, cliente):
    db.add(Reservorio(capacidad_m3=100.0))
    db.commit()

    respuesta = cliente.get("/balance")

    assert respuesta.json()["datos_hasta"] is None