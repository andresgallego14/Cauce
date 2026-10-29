from datetime import date

import pytest

import config
from ayudas import guardar_movimiento
from dominio.enums import Fuente
from infraestructura.models import Bloque, Reservorio
from servicios.balance import calcular_balance, consumo_promedio_diario


def test_calcular_balance_suma_entradas_resta_salidas_e_ignora_el_potable(db):
    db.add(Reservorio(capacidad_m3=100.0))
    db.add(Bloque(nombre="Bloque de prueba", area_m2=1000.0))
    guardar_movimiento(db, date(2026, 1, 1), Fuente.FERTIRRIEGO, 60.0)
    guardar_movimiento(db, date(2026, 1, 2), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 3), Fuente.LLUVIA, 10.0)
    guardar_movimiento(db, date(2026, 1, 3), Fuente.AGUA_POTABLE_60, 99.0)
    db.commit()
    bloques = db.query(Bloque).all()

    # 60 - 10 + (10 mm x 1000 m2 / 1000 = 10) = 60; el potable no cuenta
    assert calcular_balance(db, bloques) == pytest.approx(60.0)


def test_calcular_balance_parte_del_nivel_medido_desde_el_inicio(db, monkeypatch):
    monkeypatch.setattr(config, "FECHA_INICIO_BALANCE", date(2026, 1, 3))
    monkeypatch.setattr(config, "NIVEL_INICIAL_M3", 40.0)
    db.add(Reservorio(capacidad_m3=100.0))
    db.add(Bloque(nombre="Bloque de prueba", area_m2=1000.0))
    guardar_movimiento(db, date(2026, 1, 2), Fuente.FERTIRRIEGO, 50.0)
    guardar_movimiento(db, date(2026, 1, 3), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 4), Fuente.FERTIRRIEGO, 5.0)
    db.commit()
    bloques = db.query(Bloque).all()

    # el del 2 de enero es anterior a la medicion y no cuenta: 40 - 10 + 5 = 35
    assert calcular_balance(db, bloques) == pytest.approx(35.0)


def test_consumo_promedio_diario_sin_salidas_es_cero(db):
    assert consumo_promedio_diario(db) == 0.0


def test_consumo_promedio_diario_divide_entre_los_dias_del_calendario(db):
    guardar_movimiento(db, date(2026, 1, 1), Fuente.RIEGO, 10.0)
    guardar_movimiento(db, date(2026, 1, 1), Fuente.CRUDA, 5.0)
    guardar_movimiento(db, date(2026, 1, 4), Fuente.RIEGO, 20.0)
    guardar_movimiento(db, date(2026, 1, 2), Fuente.FERTIRRIEGO, 500.0)
    db.commit()

    # salidas: 10 + 5 + 20 = 35 m3 del 1 al 4 de enero (4 dias): 8.75 por dia
    assert consumo_promedio_diario(db) == pytest.approx(8.75)
