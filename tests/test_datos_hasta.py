from datetime import date

from api.dependencias import pronostico_actual
from ayudas import guardar_movimiento
from dominio.enums import Fuente
from infraestructura.models import Bloque, Reservorio


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


def test_prediccion_informa_hasta_que_fecha_hay_datos(db, cliente):
    db.add(Reservorio(capacidad_m3=100.0))
    db.add(Bloque(nombre="Bloque de prueba", area_m2=1000.0))
    guardar_movimiento(db, date(2026, 1, 1), Fuente.FERTIRRIEGO, 60.0)
    db.commit()
    pronostico = [
        {
            "fecha": "2026-01-03",
            "mm_lluvia": 0.0,
            "probabilidad_lluvia": 0,
            "temp_max": 25.0,
            "temp_min": 12.0,
            "evaporacion": 0.0,
        }
    ]
    cliente.app.dependency_overrides[pronostico_actual] = lambda: pronostico

    respuesta = cliente.get("/prediccion")

    assert respuesta.json()["datos_hasta"] == "2026-01-01"