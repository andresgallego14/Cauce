from dominio.consumo import consumo_por_lectura

def consumos_desde_lecturas(lecturas):
    consumos = []
    lectura_anterior = None
    for fecha, lectura in lecturas:
        if lectura_anterior is not None:
            try:
                consumo = consumo_por_lectura(lectura, lectura_anterior)
                consumos.append((fecha, lectura, consumo))
            except ValueError:
                pass
        lectura_anterior = lectura
    return consumos 