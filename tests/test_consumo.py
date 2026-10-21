import pytest
from dominio.consumo import consumo_por_lectura, consumo_por_tiempo

def test_consumo_por_lectura_es_la_diferecia_con_la_anterior():
    assert consumo_por_lectura(150.0, 100.0) == 50.0

def test_consumo_por_lectura_sin_lectura_anterior_es_cero():
    assert consumo_por_lectura(150.0, None) == 0.0

def test_consumo_por_lectura_rechaza_lectura_menor_a_la_anterior():
    with pytest.raises(ValueError):
        consumo_por_lectura(90.0, 100.0)

def test_consumo_por_tiempo_convierte_litros_a_m3():
    assert consumo_por_tiempo (60.0, 150.0) == pytest.approx(9.0)

def test_consumo_tiempo_rechaza_minutos_negativos():
    with pytest.raises(ValueError):
        consumo_por_tiempo(-5, 150.0)