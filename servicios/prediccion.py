import config
from dominio.prediccion import (
    evaporacion_esperada_m3,
    lluvia_esperada_m3,
    proyectar_niveles,
)
from infraestructura.repositorio import obtener_reservorio
from servicios.balance import calcular_balance, consumo_promedio_diario


def proyectar_balance(db, bloques, pronostico):
    area_total_m2 = sum(bloque.area_m2 for bloque in bloques)
    lluvia_por_dia = lluvia_esperada_m3(pronostico, area_total_m2)
    evaporacion_por_dia = evaporacion_esperada_m3(
        pronostico, config.SUPERFICIE_RESERVORIO_M2, config.REDUCCION_POLISOMBRA
    )

    return proyectar_niveles(
        nivel_actual=calcular_balance(db, bloques),
        consumo_diario_m3=consumo_promedio_diario(db),
        capacidad_m3=obtener_reservorio(db).capacidad_m3,
        lluvia_por_dia=lluvia_por_dia,
        evaporacion_por_dia=evaporacion_por_dia,
    )
