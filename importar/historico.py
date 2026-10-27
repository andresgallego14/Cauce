from dominio.enums import Fuente
from importar.comun import consumos_desde_lecturas, reemplazar_registros
from infraestructura.models import Registro

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


def importar_historico(db, libro, usuario):
    total = 0
    for nombre_hoja, fuente in HOJAS.items():
        lecturas = leer_lecturas(libro[nombre_hoja])
        registros = armar_registros(lecturas, fuente, usuario)
        total += reemplazar_registros(db, fuente, NOTAS, registros)
    return total