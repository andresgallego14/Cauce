from datetime import date

import pytest

from dominio.balance import promedio_diario_calendario, promedio_por_dia_con_salida


def test_calendario_sin_salidas_el_promedio_es_cero():
    assert promedio_diario_calendario([]) == 0.0


def test_calendario_un_solo_dia_promedia_lo_de_ese_dia():
    salidas = [(date(2026, 1, 1), 10.0)]

    assert promedio_diario_calendario(salidas) == pytest.approx(10.0)


def test_calendario_varias_salidas_el_mismo_dia_suman_en_un_dia():
    # riego y cruda el mismo dia: 10 + 5 = 15 m3 en 1 dia
    salidas = [(date(2026, 1, 1), 10.0), (date(2026, 1, 1), 5.0)]

    assert promedio_diario_calendario(salidas) == pytest.approx(15.0)


def test_calendario_promedia_dias_consecutivos():
    salidas = [(date(2026, 1, 1), 10.0), (date(2026, 1, 2), 20.0)]

    assert promedio_diario_calendario(salidas) == pytest.approx(15.0)


def test_calendario_los_dias_sin_registros_cuentan_como_dias_sin_salida():
    # del 1 al 10 de enero hay 10 dias: salieron 30 m3 en total, 3 m3 por dia
    salidas = [(date(2026, 1, 1), 10.0), (date(2026, 1, 10), 20.0)]

    assert promedio_diario_calendario(salidas) == pytest.approx(3.0)


def test_calendario_el_orden_de_las_salidas_no_cambia_el_promedio():
    salidas = [(date(2026, 1, 10), 20.0), (date(2026, 1, 1), 10.0)]

    assert promedio_diario_calendario(salidas) == pytest.approx(3.0)


def test_con_salida_sin_salidas_el_promedio_es_cero():
    assert promedio_por_dia_con_salida([]) == 0.0


def test_con_salida_varias_salidas_el_mismo_dia_cuentan_como_un_solo_dia():
    salidas = [(date(2026, 1, 1), 10.0), (date(2026, 1, 1), 5.0)]

    assert promedio_por_dia_con_salida(salidas) == pytest.approx(15.0)


def test_con_salida_los_dias_sin_registros_no_cuentan():
    # del 1 al 10 de enero solo hubo salidas 2 dias: 30 m3 entre 2 dias
    salidas = [(date(2026, 1, 1), 10.0), (date(2026, 1, 10), 20.0)]

    assert promedio_por_dia_con_salida(salidas) == pytest.approx(15.0)
