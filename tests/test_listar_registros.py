from datetime import date

from ayudas import guardar_movimiento
from dominio.enums import Fuente


def test_listar_registros_del_mas_reciente_al_mas_antiguo(db, cliente):
    guardar_movimiento(db, date(2026, 1, 2), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 4), Fuente.FERTIRRIEGO, 20.0)
    guardar_movimiento(db, date(2026, 1, 3), Fuente.RIEGO, 5.0)
    db.commit()

    respuesta = cliente.get("/registros")

    assert respuesta.status_code == 200
    fechas = [registro["fecha"] for registro in respuesta.json()]
    assert fechas == ["2026-01-04", "2026-01-03", "2026-01-02"]


def test_listar_registros_filtra_por_fuente(db, cliente):
    guardar_movimiento(db, date(2026, 1, 2), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 4), Fuente.FERTIRRIEGO, 20.0)
    guardar_movimiento(db, date(2026, 1, 3), Fuente.RIEGO, 5.0)
    db.commit()

    respuesta = cliente.get("/registros", params={"fuente": Fuente.RIEGO.value})

    assert respuesta.status_code == 200
    fuentes = [registro["fuente"] for registro in respuesta.json()]
    assert fuentes == [Fuente.RIEGO.value, Fuente.RIEGO.value]