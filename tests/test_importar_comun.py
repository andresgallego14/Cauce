from datetime import date

from importar.comun import consumos_desde_lecturas

DIA_1 = date(2026, 1, 1)
DIA_2 = date(2026, 1, 2)
DIA_3 = date(2026, 1, 3)


def test_sin_lecturas_no_hay_consumos():
    assert consumos_desde_lecturas([]) == []


def test_una_sola_lectura_solo_sirve_de_base():
    assert consumos_desde_lecturas([(DIA_1, 10.0)]) == []


def test_el_consumo_es_la_lectura_menos_la_anterior():
    lecturas = [(DIA_1, 10.0), (DIA_2, 15.0)]
    assert consumos_desde_lecturas(lecturas) == [(DIA_2, 15.0, 5.0)]


def test_cada_lectura_se_resta_de_la_anterior():
    lecturas = [(DIA_1, 10.0), (DIA_2, 15.0), (DIA_3, 22.0)]
    assert consumos_desde_lecturas(lecturas) == [
        (DIA_2, 15.0, 5.0),
        (DIA_3, 22.0, 7.0),
    ]


def test_una_lectura_igual_a_la_anterior_es_consumo_cero():
    lecturas = [(DIA_1, 10.0), (DIA_2, 10.0)]
    assert consumos_desde_lecturas(lecturas) == [(DIA_2, 10.0, 0.0)]


def test_una_lectura_menor_se_omite_y_pasa_a_ser_la_nueva_base():
    lecturas = [(DIA_1, 100.0), (DIA_2, 5.0), (DIA_3, 12.0)]
    assert consumos_desde_lecturas(lecturas) == [(DIA_3, 12.0, 7.0)]
