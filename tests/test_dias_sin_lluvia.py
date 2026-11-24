from datetime import date, timedelta

from dominio.dias_sin_lluvia import dias_sin_lluvia

HOY = date(2026, 11, 24)


def hace(dias: int) -> date:
    return HOY - timedelta(days=dias)


def test_cuenta_los_dias_desde_la_ultima_lluvia() -> None:
    assert dias_sin_lluvia([(hace(5), 10.0)], HOY) == 5


def test_si_llovio_hoy_lleva_cero_dias() -> None:
    assert dias_sin_lluvia([(HOY, 8.0)], HOY) == 0


def test_toma_la_lluvia_mas_reciente() -> None:
    lluvias = [(hace(9), 12.0), (hace(2), 6.0), (hace(6), 20.0)]
    assert dias_sin_lluvia(lluvias, HOY) == 2


def test_tres_mm_o_menos_no_cuentan_como_lluvia() -> None:
    lluvias = [(hace(7), 15.0), (hace(3), 3.0), (hace(1), 1.5)]
    assert dias_sin_lluvia(lluvias, HOY) == 7


def test_sin_lluvias_registradas_no_hay_dato() -> None:
    assert dias_sin_lluvia([], HOY) is None