from datetime import date

from dominio.lluvia_del_mes import resumir_lluvia_del_mes

LLUVIAS = [
    (date(2026, 11, 2), 12.0),
    (date(2026, 11, 10), 2.0),
    (date(2026, 11, 20), 5.5),
    (date(2026, 10, 15), 30.0),
    (date(2025, 11, 5), 50.0),
]


def test_suma_la_lluvia_total_y_la_util_del_mes() -> None:
    # utiles: 12 - 3 = 9; 2 mm no llega; 5.5 - 3 = 2.5 -> 11.5
    assert resumir_lluvia_del_mes(LLUVIAS, 2026, 11) == {
        "anio": 2026,
        "mes": 11,
        "total_mm": 19.5,
        "util_mm": 11.5,
        "dias_con_lluvia": 3,
        "dias_con_lluvia_util": 2,
    }


def test_la_perdida_se_descuenta_en_cada_lluvia_y_no_al_total() -> None:
    lluvias = [(date(2026, 11, dia), 2.0) for dia in (1, 2, 3)]

    resumen = resumir_lluvia_del_mes(lluvias, 2026, 11)

    assert resumen["total_mm"] == 6.0
    assert resumen["util_mm"] == 0.0


def test_no_mezcla_el_mismo_mes_de_otro_anio() -> None:
    resumen = resumir_lluvia_del_mes(LLUVIAS, 2025, 11)

    assert resumen["total_mm"] == 50.0
    assert resumen["dias_con_lluvia"] == 1


def test_los_dias_en_cero_no_cuentan_como_dias_con_lluvia() -> None:
    lluvias = [
        (date(2026, 11, 1), 0.0),
        (date(2026, 11, 2), 0.0),
        (date(2026, 11, 3), 1.0),
    ]

    assert resumir_lluvia_del_mes(lluvias, 2026, 11)["dias_con_lluvia"] == 1


def test_un_mes_sin_registros_da_cero() -> None:
    assert resumir_lluvia_del_mes(LLUVIAS, 2026, 9) == {
        "anio": 2026,
        "mes": 9,
        "total_mm": 0.0,
        "util_mm": 0.0,
        "dias_con_lluvia": 0,
        "dias_con_lluvia_util": 0,
    }