from dominio.enums import Fuente
from importar.comun import armar_registros, reemplazar_registros

FILA_INICIAL = 8
COLUMNA_FECHA = 11
COLUMNA_LECTURA = 12
NOTAS = "importado desde Excel historico"
HOJAS = {
    "Fertilizada 2026 ": Fuente.RIEGO,
    "Cruda 2026": Fuente.CRUDA,
}


def leer_lecturas(hoja):
    lecturas = []
    for fila in range(FILA_INICIAL, hoja.max_row + 1):
        fecha = hoja.cell(row=fila, column=COLUMNA_FECHA).value
        lectura = hoja.cell(row=fila, column=COLUMNA_LECTURA).value
        if fecha is None:
            break
        if not isinstance(lectura, (int, float)):
            continue
        lecturas.append((fecha.date(), lectura))
    return lecturas


def importar_historico(db, libro, usuario):
    total = 0
    for nombre_hoja, fuente in HOJAS.items():
        lecturas = leer_lecturas(libro[nombre_hoja])
        registros = armar_registros(lecturas, fuente, usuario, NOTAS)
        total += reemplazar_registros(db, fuente, NOTAS, registros)
    return total