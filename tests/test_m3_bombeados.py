from datetime import datetime

import pytest

from dominio.bombeo import BombeoIncongruente, m3_bombeados
from dominio.enums import Bocatoma

INICIO = datetime(2026, 11, 11, 7, 0)


def test_dos_horas_y_media_de_bocatoma_2_son_22_5_m3() -> None:
    fin = datetime(2026, 11, 11, 9, 30)
    assert m3_bombeados(Bocatoma.BOCATOMA_2, INICIO, fin) == pytest.approx(22.5)


def test_una_hora_de_sumergible_son_21_6_m3() -> None:
    fin = datetime(2026, 11, 11, 8, 0)
    assert m3_bombeados(Bocatoma.SUMERGIBLE, INICIO, fin) == pytest.approx(21.6)


def test_bombeo_que_pasa_la_medianoche() -> None:
    inicio = datetime(2026, 11, 11, 22, 0)
    fin = datetime(2026, 11, 12, 1, 0)
    assert m3_bombeados(Bocatoma.BOCATOMA_2, inicio, fin) == pytest.approx(27.0)


def test_exactamente_24_horas_se_acepta() -> None:
    fin = datetime(2026, 11, 12, 7, 0)
    assert m3_bombeados(Bocatoma.BOCATOMA_2, INICIO, fin) == pytest.approx(216.0)


def test_fin_antes_del_inicio_se_rechaza() -> None:
    fin = datetime(2026, 11, 11, 6, 0)
    with pytest.raises(BombeoIncongruente, match="posterior"):
        m3_bombeados(Bocatoma.BOCATOMA_2, INICIO, fin)


def test_fin_igual_al_inicio_se_rechaza() -> None:
    with pytest.raises(BombeoIncongruente, match="posterior"):
        m3_bombeados(Bocatoma.BOCATOMA_2, INICIO, INICIO)


def test_mas_de_24_horas_se_rechaza() -> None:
    fin = datetime(2026, 11, 12, 7, 1)
    with pytest.raises(BombeoIncongruente, match="24 horas"):
        m3_bombeados(Bocatoma.BOCATOMA_2, INICIO, fin)
