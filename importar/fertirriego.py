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
