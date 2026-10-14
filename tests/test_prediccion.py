import pytest
from prediccion import evaporacion_esperada_m3

def test_evaporacion_aplica_polisombra_y_area_del_reservorio():
    pronostico = [{"fecha": "2026-01-01", "evaporacion": 4}]
    resultado = evaporacion_esperada_m3(pronostico)
    assert resultado[0]["evaporacion_m3"]== pytest.approx(0.19895)
    