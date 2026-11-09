import pytest

from dominio.bombeo import horas_de_bombeo
from dominio.enums import Bocatoma


def test_una_hora_de_bocatoma_1_bombea_4_02_m3():
    assert horas_de_bombeo(4.02, Bocatoma.BOCATOMA_1) == pytest.approx(1.0)


def test_una_hora_de_sumergible_bombea_21_6_m3():
    assert horas_de_bombeo(21.6, Bocatoma.SUMERGIBLE) == pytest.approx(1.0)


def test_consumo_de_un_dia_con_bocatoma_2():
    assert horas_de_bombeo(31.2, Bocatoma.BOCATOMA_2) == pytest.approx(3.467, abs=0.001)


def test_si_no_falta_agua_no_hay_que_bombear():
    assert horas_de_bombeo(0.0, Bocatoma.BOCATOMA_1) == 0.0


def test_si_sobra_agua_tampoco_hay_que_bombear():
    assert horas_de_bombeo(-12.5, Bocatoma.BOCATOMA_2) == 0.0
