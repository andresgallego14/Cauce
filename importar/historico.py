from importar.comun import consumos_desde_lecturas
from infraestructura.models import Registro

FILA_INICIAL = 8
COLUMNA_FECHA = 11
COLUMNA_LECTURA = 12
NOTAS = "importado desde Excel historico"


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


def armar_registros(lecturas, fuente, usuario):
    return [
        Registro(
            fecha=fecha,
            tipo=fuente.tipo,
            fuente=fuente,
            valor=float(consumo),
            lectura_acumulada=float(lectura),
            usuario=usuario,
            notas=NOTAS,
        )
        for fecha, lectura, consumo in consumos_desde_lecturas(lecturas)
    ]