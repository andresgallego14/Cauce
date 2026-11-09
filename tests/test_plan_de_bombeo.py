import pytest

from dominio.bombeo import armar_plan
from dominio.enums import Bocatoma


def test_mantener_es_el_consumo_menos_la_lluvia_esperada():
    plan = armar_plan(
        nivel_actual_m3=100.0,
        capacidad_m3=215.0,
        consumo_diario_m3=31.2,
        lluvia_diaria_m3=4.2,
    )

    assert plan.m3_para_mantener == pytest.approx(27.0)
    assert plan.horas_para_mantener[Bocatoma.BOCATOMA_2] == pytest.approx(3.0)


def test_llenar_es_lo_que_falta_para_la_capacidad():
    plan = armar_plan(
        nivel_actual_m3=100.0,
        capacidad_m3=215.0,
        consumo_diario_m3=31.2,
        lluvia_diaria_m3=0.0,
    )

    assert plan.m3_para_llenar == pytest.approx(115.0)
    assert plan.horas_para_llenar[Bocatoma.SUMERGIBLE] == pytest.approx(
        5.324, abs=0.001
    )


def test_trae_las_horas_de_las_tres_bocatomas():
    plan = armar_plan(
        nivel_actual_m3=100.0,
        capacidad_m3=215.0,
        consumo_diario_m3=31.2,
        lluvia_diaria_m3=0.0,
    )

    assert set(plan.horas_para_mantener) == set(Bocatoma)
    assert set(plan.horas_para_llenar) == set(Bocatoma)


def test_si_llueve_mas_de_lo_que_se_consume_no_hay_que_bombear_para_mantener():
    plan = armar_plan(
        nivel_actual_m3=100.0,
        capacidad_m3=215.0,
        consumo_diario_m3=31.2,
        lluvia_diaria_m3=40.0,
    )

    assert plan.m3_para_mantener == 0.0
    assert all(horas == 0.0 for horas in plan.horas_para_mantener.values())


def test_si_el_reservorio_esta_lleno_no_hay_que_llenar():
    plan = armar_plan(
        nivel_actual_m3=215.0,
        capacidad_m3=215.0,
        consumo_diario_m3=31.2,
        lluvia_diaria_m3=0.0,
    )

    assert plan.m3_para_llenar == 0.0
