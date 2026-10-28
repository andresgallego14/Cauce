import pytest

from dominio.prediccion import (
    evaporacion_esperada_m3,
    lluvia_esperada_m3,
    proyectar_niveles,
)


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
    pronostico = [{"fecha": "2026-01-01", "mm_lluvia": 10.0, "probabilidad_lluvia": 50}]

    resultado = lluvia_esperada_m3(pronostico, area_total_m2=1000.0)

    # 10 mm x 50 % = 5 mm; 5 mm sobre 1000 m² son 5000 L, o sea 5 m³
    assert resultado[0]["lluvia_esperada_m3"] == pytest.approx(5.0)


def test_lluvia_esperada_es_cero_si_la_probabilidad_es_cero():
    pronostico = [{"fecha": "2026-01-01", "mm_lluvia": 30.0, "probabilidad_lluvia": 0}]

    resultado = lluvia_esperada_m3(pronostico, area_total_m2=1000.0)

    assert resultado[0]["lluvia_esperada_m3"] == 0.0


def test_lluvia_esperada_conserva_la_fecha_de_cada_dia():
    pronostico = [
        {"fecha": "2026-01-01", "mm_lluvia": 10.0, "probabilidad_lluvia": 50},
        {"fecha": "2026-01-02", "mm_lluvia": 2.0, "probabilidad_lluvia": 100},
    ]

    resultado = lluvia_esperada_m3(pronostico, area_total_m2=500.0)

    assert [dia["fecha"] for dia in resultado] == ["2026-01-01", "2026-01-02"]


def pronostico_de_lluvia(m3_dia_1, m3_dia_2):
    return [
        {"fecha": "2026-01-01", "lluvia_esperada_m3": m3_dia_1},
        {"fecha": "2026-01-02", "lluvia_esperada_m3": m3_dia_2},
    ]


def pronostico_de_evaporacion(m3_dia_1, m3_dia_2):
    return [
        {"fecha": "2026-01-01", "evaporacion_m3": m3_dia_1},
        {"fecha": "2026-01-02", "evaporacion_m3": m3_dia_2},
    ]


def test_peor_caso_resta_consumo_y_evaporacion_sin_sumar_lluvia():
    resultado = proyectar_niveles(
        nivel_actual=100.0,
        consumo_diario_m3=10.0,
        capacidad_m3=200.0,
        lluvia_por_dia=pronostico_de_lluvia(5.0, 5.0),
        evaporacion_por_dia=pronostico_de_evaporacion(2.0, 2.0),
    )

    # Cada dia baja 10 + 2 = 12 m³: 100 -> 88 -> 76
    assert [dia["peor_caso_m3"] for dia in resultado] == [88.0, 76.0]


def test_mejor_caso_suma_la_lluvia_esperada():
    resultado = proyectar_niveles(
        nivel_actual=100.0,
        consumo_diario_m3=10.0,
        capacidad_m3=200.0,
        lluvia_por_dia=pronostico_de_lluvia(5.0, 5.0),
        evaporacion_por_dia=pronostico_de_evaporacion(2.0, 2.0),
    )

    # Cada dia: +5 de lluvia -10 de consumo -2 de evaporacion = -7: 100 -> 93 -> 86
    assert [dia["mejor_caso_m3"] for dia in resultado] == [93.0, 86.0]


def test_el_nivel_nunca_baja_de_cero():
    resultado = proyectar_niveles(
        nivel_actual=5.0,
        consumo_diario_m3=10.0,
        capacidad_m3=200.0,
        lluvia_por_dia=pronostico_de_lluvia(0.0, 0.0),
        evaporacion_por_dia=pronostico_de_evaporacion(0.0, 0.0),
    )

    assert [dia["peor_caso_m3"] for dia in resultado] == [0.0, 0.0]
    assert [dia["mejor_caso_m3"] for dia in resultado] == [0.0, 0.0]


def test_el_nivel_nunca_supera_la_capacidad():
    resultado = proyectar_niveles(
        nivel_actual=95.0,
        consumo_diario_m3=0.0,
        capacidad_m3=100.0,
        lluvia_por_dia=pronostico_de_lluvia(50.0, 50.0),
        evaporacion_por_dia=pronostico_de_evaporacion(0.0, 0.0),
    )

    assert [dia["mejor_caso_m3"] for dia in resultado] == [100.0, 100.0]


def test_la_proyeccion_trae_un_dia_por_cada_dia_del_pronostico():
    resultado = proyectar_niveles(
        nivel_actual=100.0,
        consumo_diario_m3=10.0,
        capacidad_m3=200.0,
        lluvia_por_dia=pronostico_de_lluvia(0.0, 0.0),
        evaporacion_por_dia=pronostico_de_evaporacion(0.0, 0.0),
    )

    assert [dia["fecha"] for dia in resultado] == ["2026-01-01", "2026-01-02"]


def test_los_niveles_se_redondean_a_dos_decimales():
    resultado = proyectar_niveles(
        nivel_actual=100.0,
        consumo_diario_m3=0.3333,
        capacidad_m3=200.0,
        lluvia_por_dia=pronostico_de_lluvia(0.0, 0.0),
        evaporacion_por_dia=pronostico_de_evaporacion(0.0, 0.0),
    )

    # 100 - 0.3333 = 99.6667 -> 99.67; 99.6667 - 0.3333 = 99.3334 -> 99.33
    assert [dia["peor_caso_m3"] for dia in resultado] == [99.67, 99.33]
