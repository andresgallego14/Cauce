from datetime import date, datetime
from openpyxl import Workbook
from importar.fertirriego import leer_lecturas

COLUMNA_FECHA = 1
COLUMNA_SEMANA = 3
COLUMNA_LECTURA = 4

def escribir_fila(hoja, fila, fecha, semana, lectura):
    hoja.cell(row=fila, column=COLUMNA_FECHA, value=fecha)
    hoja.cell(row=fila, column=COLUMNA_SEMANA, value=semana)
    hoja.cell(row=fila, column=COLUMNA_LECTURA, value=lectura)

def hoja_con(filas, fila_inicial=54):
    hoja = Workbook().active
    for numero, (fecha, semana, lectura) in enumerate(filas):
        escribir_fila(hoja, fila_inicial + numero, fecha, semana, lectura)
    return hoja

def test_lee_fecha_y_lectura_desde_la_fila_54():
    hoja = hoja_con(
        [
            (datetime(2026, 1, 1), "semana 1", 100),
            (datetime(2026, 1, 2), "semana 2", 110),
        ]
    )
    assert leer_lecturas(hoja) == [(date(2026, 1, 1), 100), (date(2026, 1, 2), 110)]

def test_ignora_lo_que_hay_encima_de_la_fila_54():
    hoja = hoja_con([(datetime(2026, 1, 2), "semana 2", 110)])
    escribir_fila(hoja, 53, datetime(2026, 1, 1), "semana 1", 100)
    assert leer_lecturas(hoja) == [(date(2026, 1, 2), 110)]

def test_salta_las_filas_sin_texto_de_semana():
    hoja = hoja_con(
        [
            (datetime(2026, 1, 1), None, 100),
            (datetime(2026, 1, 2), "   ", 105),
            (datetime(2026, 1, 3), "semana 3", 110),
        ]
    )
    assert leer_lecturas(hoja) == [(date(2026, 1, 3), 110)]

def test_salta_las_filas_malas_y_sigue_leyendo():
    hoja = hoja_con(
        [
            (datetime(2026, 1, 1), "semana 1", 100),
            (None, "semana 2", 105),
            (datetime(2026, 1, 3), "semana 3", "sin dato"),
            (datetime(2026, 1, 4), "semana 4", 120),
        ]
    )
    assert leer_lecturas(hoja) == [(date(2026, 1, 1), 100), (date(2026, 1, 4), 120)]