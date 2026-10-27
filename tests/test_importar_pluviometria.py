from datetime import date, datetime
import pytest
from importar.pluviometria import fecha_del_dato

LUNES = datetime(2026, 10, 26, 9, 0)
MARTES = datetime(2026, 10, 27, 8, 30)

def test_el_mismo_dia_de_la_semana_es_la_fecha_del_envio():
    assert fecha_del_dato(MARTES, "Martes") == date(2026, 10, 27)

def test_un_dia_anterior_retrocede_hasta_ese_dia():
    assert fecha_del_dato(MARTES, "Lunes") == date(2026, 10, 26)

def test_un_dia_posterior_retrocede_a_la_semana_anterior():
    assert fecha_del_dato(MARTES, "Sabado") == date(2026, 10, 24)

def test_el_dato_del_domingo_enviado_el_lunes_queda_en_domingo():
    assert fecha_del_dato(LUNES, "Domingo") == date(2026, 10, 25)

def test_el_dato_del_lunes_enviado_el_lunes_queda_en_lunes():
    assert fecha_del_dato(LUNES, "Lunes") == date(2026, 10, 26)

def test_toma_la_ultima_palabra_sin_importar_mayusculas():
    assert fecha_del_dato(MARTES, "dia lunes") == date(2026, 10, 26)

@pytest.mark.parametrize("dia_texto", ["Festivo", " ", None])
def test_devuelve_none_si_no_reconoce_el_dia(dia_texto):
    assert fecha_del_dato(MARTES, dia_texto) is None