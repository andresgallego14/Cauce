from dominio.enums import Fuente

def lluvia_en_m3(mm: float, area_m2: float) -> float:
    return mm * area_m2 / 1000

def movimiento_en_m3(fuente: Fuente, valor: float, area_total_m2: float) -> float:
    if fuente == Fuente.LLUVIA:
        return lluvia_en_m3(valor, area_total_m2)
    if fuente == Fuente.FERTIRRIEGO:
        return valor
    if fuente in (Fuente.RIEGO, Fuente.CRUDA):
        return -valor
    if fuente in (Fuente.AGUA_POTABLE_60, Fuente.AGUA_POTABLE_370):
        return 0.0
    raise ValueError(f"la fuente {fuente} no tiene regla de balance")

def limitar_al_reservorio(nivel, capacidad_m3):
    return min(max(nivel, 0), capacidad_m3)

def simular_balance(movimientos, capacidad):
    movimientos_ordenados = sorted(movimientos, key=lambda movimiento: movimiento[0])
    nivel = 0
    for _, cantidad in movimientos_ordenados:
        nivel = limitar_al_reservorio(nivel + cantidad, capacidad)
    return nivel