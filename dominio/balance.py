def limitar_al_reservorio(nivel, capacidad_m3):
    return min(max(nivel, 0), capacidad_m3)


def simular_balance(movimientos, capacidad):
    movimientos_ordenados = sorted(movimientos, key=lambda movimiento: movimiento[0])
    nivel = 0
    for _, cantidad in movimientos_ordenados:
        nivel = limitar_al_reservorio(nivel + cantidad, capacidad)
    return nivel