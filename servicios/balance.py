from dominio.balance import (
    movimiento_en_m3,
    promedio_diario_calendario,
    simular_balance,
)
from infraestructura.repositorio import (
    obtener_registros,
    obtener_reservorio,
    obtener_salidas,
)


def calcular_balance(db, bloques):
    area_total_m2 = sum(bloque.area_m2 for bloque in bloques)
    movimientos = [
        (
            registro.fecha,
            movimiento_en_m3(registro.fuente, registro.valor, area_total_m2),
        )
        for registro in obtener_registros(db)
    ]
    reservorio = obtener_reservorio(db)
    return simular_balance(movimientos, reservorio.capacidad_m3)


def consumo_promedio_diario(db):
    return promedio_diario_calendario(obtener_salidas(db))
