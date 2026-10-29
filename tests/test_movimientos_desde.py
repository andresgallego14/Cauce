from datetime import date

from dominio.balance import movimientos_desde

INICIO = date(2026, 11, 3)


def test_descarta_los_movimientos_anteriores_al_inicio():
    movimientos = [(date(2026, 11, 2), 10.0), (INICIO, 5.0)]
    assert movimientos_desde(movimientos, INICIO) == [(INICIO, 5.0)]


def test_cuenta_los_movimientos_del_mismo_dia_del_inicio():
    movimientos = [(INICIO, -4.0)]
    assert movimientos_desde(movimientos, INICIO) == [(INICIO, -4.0)]


def test_conserva_los_posteriores_sin_cambiar_su_orden():
    movimientos = [(date(2026, 11, 5), 1.0), (date(2026, 11, 4), 2.0)]
    assert movimientos_desde(movimientos, INICIO) == movimientos


def test_sin_movimientos_devuelve_una_lista_vacia():
    assert movimientos_desde([], INICIO) == []
