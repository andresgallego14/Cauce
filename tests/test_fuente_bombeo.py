from dominio.balance import movimiento_en_m3
from dominio.enums import Fuente, TipoMovimiento


def test_bombeo_es_una_entrada() -> None:
    assert Fuente.BOMBEO.tipo == TipoMovimiento.ENTRADA


def test_bombeo_suma_sus_m3_al_reservorio() -> None:
    assert movimiento_en_m3(Fuente.BOMBEO, 22.5, 1000.0) == 22.5
