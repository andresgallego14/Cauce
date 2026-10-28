def consumo_por_lectura(lectura_actual: float, lectura_anterior: float | None) -> float:
    if lectura_anterior is None:
        return 0.0
    if lectura_actual < lectura_anterior:
        raise ValueError("La lectura actual no puede ser menor que la anterior")
    return lectura_actual - lectura_anterior


def consumo_por_tiempo(minutos: float, caudal_l_min: float) -> float:
    if minutos < 0:
        raise ValueError("Los minutos no pueden ser negativos")
    return minutos * caudal_l_min / 1000
