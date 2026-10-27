FILA_INICIAL = 8
COLUMNA_FECHA = 11
COLUMNA_LECTURA = 12

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