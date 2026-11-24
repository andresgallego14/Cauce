import pytest

from dominio.enums import Bocatoma
from dominio.planes import PlanInvalido, evaluar_plan

PEQUENA = Bocatoma.BOCATOMA_1
GRANDE = Bocatoma.BOCATOMA_2


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