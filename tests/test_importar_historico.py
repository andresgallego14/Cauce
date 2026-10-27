from datetime import date, datetime

from openpyxl import Workbook

from dominio.enums import Fuente
from importar.historico import NOTAS, armar_registros, leer_lecturas

COLUMNA_FECHA = 11
COLUMNA_LECTURA = 12

DIA_1 = date(2026, 1, 1)
DIA_2 = date(2026, 1, 2)
DIA_3 = date(2026, 1, 3)
DIA_4 = date(2026, 1, 4)


def hoja_con(filas, fila_inicial=8):
    hoja = Workbook().active
    for numero, (fecha, lectura) in enumerate(filas):
        hoja.cell(row=fila_inicial + numero, column=COLUMNA_FECHA, value=fecha)
        hoja.cell(row=fila_inicial + numero, column=COLUMNA_LECTURA, value=lectura)
    return hoja


def test_lee_fecha_y_lectura_desde_la_fila_8():
    hoja = hoja_con([(datetime(2026, 1, 1), 100), (datetime(2026, 1, 2), 110)])

    assert leer_lecturas(hoja) == [(date(2026, 1, 1), 100), (date(2026, 1, 2), 110)]


def test_ignora_lo_que_hay_encima_de_la_fila_8():
    hoja = hoja_con([(datetime(2026, 1, 1), 100)])
    hoja.cell(row=7, column=COLUMNA_FECHA, value="Fecha")
    hoja.cell(row=7, column=COLUMNA_LECTURA, value="Lectura")

    assert leer_lecturas(hoja) == [(date(2026, 1, 1), 100)]


def test_se_detiene_en_la_primera_fecha_vacia():
    hoja = hoja_con(
        [
            (datetime(2026, 1, 1), 100),
            (None, None),
            (datetime(2026, 1, 3), 120),
        ]
    )

    assert leer_lecturas(hoja) == [(date(2026, 1, 1), 100)]


def test_salta_las_lecturas_que_no_son_numero():
    hoja = hoja_con(
        [
            (datetime(2026, 1, 1), 100),
            (datetime(2026, 1, 2), "sin dato"),
            (datetime(2026, 1, 3), 120),
        ]
    )

    assert leer_lecturas(hoja) == [(date(2026, 1, 1), 100), (date(2026, 1, 3), 120)]


def test_la_primera_lectura_solo_es_punto_de_partida():
    registros = armar_registros([(DIA_1, 100), (DIA_2, 110)], Fuente.RIEGO, "prueba")

    assert len(registros) == 1


def test_el_valor_es_la_diferencia_entre_lecturas():
    registros = armar_registros([(DIA_1, 100), (DIA_2, 110)], Fuente.RIEGO, "prueba")

    assert registros[0].fecha == DIA_2
    assert registros[0].valor == 10.0
    assert registros[0].lectura_acumulada == 110.0


def test_completa_fuente_tipo_usuario_y_notas():
    registros = armar_registros([(DIA_1, 100), (DIA_2, 110)], Fuente.RIEGO, "prueba")

    assert registros[0].fuente == Fuente.RIEGO
    assert registros[0].tipo == Fuente.RIEGO.tipo
    assert registros[0].usuario == "prueba"
    assert registros[0].notas == NOTAS


def test_descarta_las_lecturas_que_bajan():
    lecturas = [(DIA_1, 100), (DIA_2, 110), (DIA_3, 50), (DIA_4, 60)]

    registros = armar_registros(lecturas, Fuente.CRUDA, "prueba")

    assert [registro.fecha for registro in registros] == [DIA_2, DIA_4]
    assert [registro.valor for registro in registros] == [10.0, 10.0]