import pytest

from dominio.balance import lluvia_en_m3, movimiento_en_m3
from dominio.enums import Fuente


def test_lluvia_en_m3_descuenta_la_perdida_inicial_y_convierte_sobre_el_area():
    # 10 mm medidos - 3 mm de perdida = 7 mm utiles; 7 mm x 500 m2 = 3.5 m3
    assert lluvia_en_m3(mm=10.0, area_m2=500.0) == pytest.approx(3.5)


def test_la_lluvia_suma_al_reservorio_segun_el_area():
    movimiento = movimiento_en_m3(Fuente.LLUVIA, valor=10.0, area_total_m2=500.0)
    assert movimiento == pytest.approx(3.5)


def test_cuatro_mm_dejan_solo_un_mm_util():
    # 4 mm medidos - 3 mm de perdida = 1 mm util; 1 mm x 1000 m2 = 1.0 m3
    assert lluvia_en_m3(mm=4.0, area_m2=1000.0) == pytest.approx(1.0)


def test_tres_mm_o_menos_no_llegan_al_reservorio():
    assert lluvia_en_m3(mm=3.0, area_m2=1000.0) == 0.0
    assert lluvia_en_m3(mm=2.0, area_m2=1000.0) == 0.0


def test_sin_lluvia_no_hay_aporte():
    assert lluvia_en_m3(mm=0.0, area_m2=1000.0) == 0.0


def test_el_fertirriego_suma_su_valor_al_reservorio():
    movimiento = movimiento_en_m3(Fuente.FERTIRRIEGO, valor=20.0, area_total_m2=500.0)
    assert movimiento == 20.0


def test_el_riego_y_la_cruda_restan_su_valor_del_reservorio():
    riego = movimiento_en_m3(Fuente.RIEGO, valor=8.0, area_total_m2=500.0)
    cruda = movimiento_en_m3(Fuente.CRUDA, valor=3.0, area_total_m2=500.0)
    assert riego == -8.0
    assert cruda == -3.0


def test_el_agua_potable_no_afecta_al_reservorio():
    potable_60 = movimiento_en_m3(
        Fuente.AGUA_POTABLE_60, valor=15.0, area_total_m2=500.0
    )
    potable_370 = movimiento_en_m3(
        Fuente.AGUA_POTABLE_370, valor=15.0, area_total_m2=500.0
    )
    assert potable_60 == 0.0
    assert potable_370 == 0.0


def test_toda_fuente_tiene_una_regla_de_balance():
    for fuente in Fuente:
        movimiento_en_m3(fuente, valor=1.0, area_total_m2=100.0)
