from datetime import date

from dominio.informe import resumir_por_dia

DOCE = date(2026, 11, 12)
TRECE = date(2026, 11, 13)


def test_separa_entradas_y_salidas_de_cada_dia() -> None:
    movimientos = [
        (DOCE, 10.0),
        (DOCE, -25.0),
        (DOCE, -5.0),
        (TRECE, 40.0),
    ]

    assert resumir_por_dia(movimientos, DOCE, TRECE) == [
        {
            "fecha": DOCE,
            "entradas_m3": 10.0,
            "salidas_m3": 30.0,
            "neto_m3": -20.0,
            "con_registros": True,
        },
        {
            "fecha": TRECE,
            "entradas_m3": 40.0,
            "salidas_m3": 0.0,
            "neto_m3": 40.0,
            "con_registros": True,
        },
    ]


def test_los_dias_sin_registros_aparecen_en_cero_y_marcados() -> None:
    once = date(2026, 11, 11)

    dias = resumir_por_dia([(DOCE, -8.0)], once, TRECE)

    assert [dia["fecha"] for dia in dias] == [once, DOCE, TRECE]
    assert dias[0]["con_registros"] is False
    assert dias[0]["salidas_m3"] == 0.0
    assert dias[1]["salidas_m3"] == 8.0
    assert dias[2]["con_registros"] is False


def test_ignora_lo_que_esta_fuera_del_rango() -> None:
    movimientos = [
        (date(2026, 11, 10), -99.0),
        (DOCE, -8.0),
        (date(2026, 11, 20), -99.0),
    ]

    dias = resumir_por_dia(movimientos, DOCE, DOCE)

    assert len(dias) == 1
    assert dias[0]["salidas_m3"] == 8.0


def test_un_registro_que_no_mueve_agua_igual_cuenta_como_registro() -> None:
    dias = resumir_por_dia([(DOCE, 0.0)], DOCE, DOCE)

    assert dias[0]["con_registros"] is True
    assert dias[0]["entradas_m3"] == 0.0
    assert dias[0]["salidas_m3"] == 0.0


def test_redondea_a_dos_decimales() -> None:
    dias = resumir_por_dia([(DOCE, -1.234567), (DOCE, 2.345678)], DOCE, DOCE)

    assert dias[0]["salidas_m3"] == 1.23
    assert dias[0]["entradas_m3"] == 2.35
    assert dias[0]["neto_m3"] == 1.11