from datetime import date, timedelta

UN_DIA = timedelta(days=1)


def resumir_por_dia(
    movimientos: list[tuple[date, float]], desde: date, hasta: date
) -> list[dict]:
    por_fecha: dict[date, list[float]] = {}
    for fecha, cantidad in movimientos:
        por_fecha.setdefault(fecha, []).append(cantidad)

    dias = []
    fecha = desde
    while fecha <= hasta:
        del_dia = por_fecha.get(fecha, [])
        entradas = sum(cantidad for cantidad in del_dia if cantidad > 0)
        salidas = -sum(cantidad for cantidad in del_dia if cantidad < 0)
        dias.append(
            {
                "fecha": fecha,
                "entradas_m3": round(entradas, 2),
                "salidas_m3": round(salidas, 2),
                "neto_m3": round(entradas - salidas, 2),
                "con_registros": bool(del_dia),
            }
        )
        fecha += UN_DIA
    return dias
