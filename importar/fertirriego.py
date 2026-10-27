from dominio.enums import Fuente
from importar.comun import armar_registros, reemplazar_registros

HOJA = "Respuestas de formulario 1"
FUENTE = Fuente.FERTIRRIEGO
NOTAS = "importado desde forms"
FILA_INICIAL = 54
COLUMNA_FECHA = 1
COLUMNA_SEMANA = 3
COLUMNA_LECTURA = 4


def leer_lecturas(hoja):
    lecturas = []
    for fila in range(FILA_INICIAL, hoja.max_row + 1):
        fecha = hoja.cell(row=fila, column=COLUMNA_FECHA).value
        semana = hoja.cell(row=fila, column=COLUMNA_SEMANA).value
        lectura = hoja.cell(row=fila, column=COLUMNA_LECTURA).value
        if fecha is None or not isinstance(lectura, (int, float)):
            continue
        if not isinstance(semana, str) or not semana.strip():
            continue
        lecturas.append((fecha.date(), lectura))
    return lecturas


def importar_fertirriego(db, libro, usuario):
    lecturas = leer_lecturas(libro[HOJA])
    registros = armar_registros(lecturas, FUENTE, usuario, NOTAS)
    return reemplazar_registros(db, FUENTE, NOTAS, registros)