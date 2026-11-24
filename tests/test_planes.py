import pytest

from dominio.enums import Bocatoma
from dominio.planes import (
    PlanInvalido,
    dias_minimos_para_llenar,
    evaluar_plan,
    horas_para_llenar_en,
    repartir_horas,
)

PEQUENA = Bocatoma.BOCATOMA_1
GRANDE = Bocatoma.BOCATOMA_2
SUMERGIBLE = Bocatoma.SUMERGIBLE
SIN_SUMERGIBLE = (PEQUENA, GRANDE)
TODAS = (PEQUENA, GRANDE, SUMERGIBLE)


def minutos(horas: dict[Bocatoma, float]) -> dict[Bocatoma, int]:
    return {bocatoma: round(h * 60) for bocatoma, h in horas.items()}


def test_calcula_los_m3_de_cada_bocatoma_y_del_dia() -> None:
    resultado = evaluar_plan({PEQUENA: 9, GRANDE: 4}, 148.9, 17.8)

    assert resultado.m3_por_bocatoma == pytest.approx({PEQUENA: 36.18, GRANDE: 36.0})
    assert resultado.m3_por_dia == pytest.approx(72.18)


def test_cuenta_los_dias_para_llenar_redondeando_hacia_arriba() -> None:
    resultado = evaluar_plan({PEQUENA: 9, GRANDE: 4}, 148.9, 17.8)

    # 72.18 que entran - 17.8 que se gastan = 54.38 netos al dia
    # 148.9 / 54.38 = 2.74 -> 3 dias
    assert resultado.neto_por_dia == pytest.approx(54.38)
    assert resultado.dias_para_llenar == 3


def test_si_no_alcanza_el_consumo_no_hay_dias_para_llenar() -> None:
    resultado = evaluar_plan({PEQUENA: 2}, 148.9, 17.8)

    assert resultado.neto_por_dia == pytest.approx(-9.76)
    assert resultado.dias_para_llenar is None


def test_si_ya_esta_lleno_faltan_cero_dias() -> None:
    resultado = evaluar_plan({PEQUENA: 3}, 0.0, 17.8)

    assert resultado.dias_para_llenar == 0


@pytest.mark.parametrize("horas", [-1, 9.5])
def test_las_horas_deben_caber_en_la_jornada(horas: float) -> None:
    with pytest.raises(PlanInvalido, match="9"):
        evaluar_plan({GRANDE: horas}, 148.9, 17.8)


def test_mantener_usa_solo_la_pequena_con_las_horas_justas() -> None:
    # 17.8 / 4.02 = 4.428 h = 265.7 min -> 266 min (4 h 26 min)
    assert minutos(repartir_horas(17.8, SIN_SUMERGIBLE)) == {PEQUENA: 266}


def test_si_la_pequena_no_alcanza_suma_la_grande() -> None:
    # pequena 9 h = 36.18; faltan 56.07 / 9 = 6.23 h = 373.8 min -> 374 min
    assert minutos(repartir_horas(92.25, SIN_SUMERGIBLE)) == {
        PEQUENA: 540,
        GRANDE: 374,
    }


def test_la_sumergible_solo_entra_cuando_esta_permitida_y_hace_falta() -> None:
    # pequena y grande 9 h = 117.18; faltan 21.6 = 1 h de Sumergible
    assert minutos(repartir_horas(138.78, TODAS)) == {
        PEQUENA: 540,
        GRANDE: 540,
        SUMERGIBLE: 60,
    }


def test_sin_agua_que_meter_no_prende_nada() -> None:
    assert repartir_horas(0.0, SIN_SUMERGIBLE) == {}


def test_si_ni_con_toda_la_jornada_alcanza_lo_dice() -> None:
    with pytest.raises(PlanInvalido, match="Sumergible"):
        repartir_horas(150.0, SIN_SUMERGIBLE)


def test_dias_minimos_para_llenar_sin_sumergible() -> None:
    # maximo 117.18 - 17.8 que se gastan = 99.38 netos; 148.9 / 99.38 = 1.5 -> 2
    assert dias_minimos_para_llenar(148.9, 17.8, SIN_SUMERGIBLE) == 2


def test_si_el_consumo_supera_el_maximo_nunca_llena() -> None:
    assert dias_minimos_para_llenar(148.9, 120.0, SIN_SUMERGIBLE) is None


def test_lleno_no_necesita_dias() -> None:
    assert dias_minimos_para_llenar(0.0, 17.8, SIN_SUMERGIBLE) == 0


def test_llenar_en_dos_dias_reparte_en_partes_iguales() -> None:
    # 17.8 + 148.9 / 2 = 92.25 m3 por dia
    assert minutos(horas_para_llenar_en(2, 148.9, 17.8, SIN_SUMERGIBLE)) == {
        PEQUENA: 540,
        GRANDE: 374,
    }


def test_llenar_en_una_semana_usa_menos_horas() -> None:
    # 17.8 + 148.9 / 7 = 39.07; pequena 9 h y grande 2.89 / 9 = 19.3 min -> 20
    assert minutos(horas_para_llenar_en(7, 148.9, 17.8, SIN_SUMERGIBLE)) == {
        PEQUENA: 540,
        GRANDE: 20,
    }