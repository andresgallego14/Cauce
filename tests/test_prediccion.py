import pytest
from prediccion import evaporacion_esperada_m3, lluvia_esperada_m3

def test_evaporacion_aplica_polisombra_y_covierte_a_m3():
    pronostico = [{"fecha": "2026-01-01", "evaporacion": 4.0}]

    resultado = evaporacion_esperada_m3(
        pronostico, superficie_m2=200.0, reduccion_polisombra=0.75
    )
    # 4mm x (1-0.75) = 1mm; 1mm sobre 200m2 son 200L, o sea 0.2m3
    assert resultado[0]["evaporacion_m3"] == pytest.approx(0.2)

def test_evaporacion_sin_polisombra_es_la_evaporacion_completa():
    pronostico = [{"fecha": "2026-01-01", "evaporacion": 4.0}]

    resultado = evaporacion_esperada_m3(
        pronostico, superficie_m2=100.0, reduccion_polisombra=0.0
    )

    # 4 mm sobre 100 m² son 400 L, o sea 0.4 m³
    assert resultado[0]["evaporacion_m3"] == pytest.approx(0.4)

def test_evaporacion_conserva_la_fecha_de_cada_dia():
    pronostico = [
        {"fecha": "2026-01-01", "evaporacion": 4.0},
        {"fecha": "2026-01-02", "evaporacion": 3.0},
    ]
    resultado = evaporacion_esperada_m3(
        pronostico, superficie_m2=100, reduccion_polisombra=0.5 
)
    assert [dia["fecha"] for dia in resultado] == ["2026-01-01", "2026-01-02"]

def test_lluvia_esperada_es_mm_por_probabilidad_por_area_en_m3():
    pronostico = [
        {"fecha": "2026-01-01", "mm_lluvia": 10.0, "probabilidad_lluvia": 50}
    ]

    resultado = lluvia_esperada_m3(pronostico, area_total_m2=1000.0)

    # 10 mm x 50 % = 5 mm; 5 mm sobre 1000 m² son 5000 L, o sea 5 m³
    assert resultado[0]["lluvia_esperada_m3"] == pytest.approx(5.0)


def test_lluvia_esperada_es_cero_si_la_probabilidad_es_cero():
    pronostico = [
        {"fecha": "2026-01-01", "mm_lluvia": 30.0, "probabilidad_lluvia": 0}
    ]

    resultado = lluvia_esperada_m3(pronostico, area_total_m2=1000.0)

    assert resultado[0]["lluvia_esperada_m3"] == 0.0


def test_lluvia_esperada_conserva_la_fecha_de_cada_dia():
    pronostico = [
        {"fecha": "2026-01-01", "mm_lluvia": 10.0, "probabilidad_lluvia": 50},
        {"fecha": "2026-01-02", "mm_lluvia": 2.0, "probabilidad_lluvia": 100},
    ]

    resultado = lluvia_esperada_m3(pronostico, area_total_m2=500.0)

    assert [dia["fecha"] for dia in resultado] == ["2026-01-01", "2026-01-02"]