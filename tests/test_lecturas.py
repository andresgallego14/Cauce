from datetime import date

import pytest

from dominio.lecturas import Lectura, LecturaIncongruente, calcular_consumo

CAUDAL_FERTIRRIEGO = 4.0


def test_primera_lectura_es_la_base_y_no_consume():
    nueva = Lectura(date(2026, 11, 2), 685.72)

    assert calcular_consumo(nueva, None, CAUDAL_FERTIRRIEGO) == 0.0


def test_consumo_es_la_resta_contra_la_lectura_anterior():
    anterior = Lectura(date(2026, 10, 19), 617.95)
    nueva = Lectura(date(2026, 10, 30), 685.72)

    assert calcular_consumo(nueva, anterior, CAUDAL_FERTIRRIEGO) == pytest.approx(67.77)


def test_lectura_igual_a_la_anterior_no_consume():
    anterior = Lectura(date(2026, 10, 29), 685.72)
    nueva = Lectura(date(2026, 10, 30), 685.72)

    assert calcular_consumo(nueva, anterior, CAUDAL_FERTIRRIEGO) == 0.0


def test_lectura_menor_que_la_anterior_es_incongruente():
    anterior = Lectura(date(2026, 9, 28), 50473.66)
    nueva = Lectura(date(2026, 10, 13), 31794.83)

    with pytest.raises(LecturaIncongruente, match="menor que la anterior"):
        calcular_consumo(nueva, anterior, CAUDAL_FERTIRRIEGO)


def test_consumo_imposible_para_el_medidor_es_incongruente():
    anterior = Lectura(date(2026, 10, 5), 534.78)
    nueva = Lectura(date(2026, 10, 19), 61794.52)

    with pytest.raises(LecturaIncongruente, match="supera"):
        calcular_consumo(nueva, anterior, CAUDAL_FERTIRRIEGO)


def test_dos_lecturas_el_mismo_dia_usan_el_tope_de_un_dia():
    anterior = Lectura(date(2026, 11, 2), 685.72)
    nueva = Lectura(date(2026, 11, 2), 700.0)

    assert calcular_consumo(nueva, anterior, CAUDAL_FERTIRRIEGO) == pytest.approx(14.28)
